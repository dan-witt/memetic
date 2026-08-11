# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""Build the two new Usenet novelty-baseline corpora from the UTZOO tapes:
  single-topic: net.lang.lisp -> comp.lang.lisp   (main group only; .x/.franz subgroups excluded)
  broad:        net.sci -> sci.misc               (general-science discussion)
Path = the group's own directory (the reader's view of the venue), confirmed against the article's
Newsgroups: header; dedup by Message-ID (tapes 104-141 double-store groups under stripped paths).
Bodies are quote/sig-stripped identically to the governance core corpus. Authors hashed.
Then a structural characterization (no novelty instruments run here): volume/year, leaky-bucket
stats, churn/core signature (window=calendar year, K=3), thread + length stats.
Output: baseline_corpora2.json (records with cleaned text, local only -- raw corpora stay out of the repo)."""
import tarfile, email.utils, hashlib, json, re, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

TAPES = Path("/home/dan/media/utzoo/tapes")
S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")

FAMS = {
    "pascal":   {"path_groups": {"net.lang.pascal", "comp.lang.pascal", "lang.pascal"},
                 "header_groups": {"net.lang.pascal", "comp.lang.pascal"}},
    "forth":    {"path_groups": {"net.lang.forth", "comp.lang.forth", "lang.forth"},
                 "header_groups": {"net.lang.forth", "comp.lang.forth"}},
    "ada":      {"path_groups": {"net.lang.ada", "comp.lang.ada", "lang.ada"},
                 "header_groups": {"net.lang.ada", "comp.lang.ada"}},
    "fortran":  {"path_groups": {"net.lang.f77", "comp.lang.fortran", "lang.fortran"},
                 "header_groups": {"net.lang.f77", "comp.lang.fortran"}},
    "prolog":   {"path_groups": {"net.lang.prolog", "comp.lang.prolog", "lang.prolog"},
                 "header_groups": {"net.lang.prolog", "comp.lang.prolog"}},
    "modula2":  {"path_groups": {"net.lang.mod2", "comp.lang.modula2", "lang.modula2"},
                 "header_groups": {"net.lang.mod2", "comp.lang.modula2"}},
    "smalltalk":{"path_groups": {"net.lang.st80", "comp.lang.smalltalk", "lang.smalltalk"},
                 "header_groups": {"net.lang.st80", "comp.lang.smalltalk"}},
    "scheme":   {"path_groups": {"comp.lang.scheme", "lang.scheme"},
                 "header_groups": {"comp.lang.scheme"}},
    "perl":     {"path_groups": {"comp.lang.perl", "lang.perl"},
                 "header_groups": {"comp.lang.perl"}},
}

def hz(s): return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:12]

def parse(raw):
    t = raw.decode("latin-1", "replace")
    head, _, body = t.partition("\n\n")
    h = {}
    for ln in head.split("\n"):
        if ln[:1] in (" ", "\t") or ":" not in ln: continue
        k, v = ln.split(":", 1); h[k.strip().lower()] = v.strip()
    return h, body

def epoch(datestr):
    tt = email.utils.parsedate_tz(datestr or "")
    if not tt: return None
    try:
        e = email.utils.mktime_tz(tt)
        return e if 3e8 < e < 7.2e8 else None      # sane 1979..1992
    except Exception: return None

def strip_body(body):
    out = []
    for l in body.split("\n"):
        s = l.strip()
        if s in ("--", "-- "): break
        if s.startswith(">") or s.startswith("|") or re.match(r"^\s*In article|^\s*\w+.* writes:$|^\s*>", l): continue
        out.append(l)
    return "\n".join(out).strip()

recs = {f: {} for f in FAMS}          # family -> msgid_key -> record
raw_seen = Counter()
tapes = sorted(TAPES.glob("news*.tgz"))
print(f"parsing {len(tapes)} tapes ...", flush=True)
for ti, tp in enumerate(tapes):
    try:
        tf = tarfile.open(tp, "r:gz")
    except Exception as e:
        print(f"  skip {tp.name}: {e}"); continue
    try:
        for mem in tf:
            if not mem.isfile(): continue
            parts = mem.name.split("/")
            if len(parts) < 4 or not parts[-1].isdigit(): continue
            pg = ".".join(parts[2:-1])
            fam = next((f for f, c in FAMS.items() if pg in c["path_groups"]), None)
            if fam is None: continue
            try:
                raw = tf.extractfile(mem).read()
            except Exception: continue
            h, body = parse(raw)
            ng = [g.strip() for g in h.get("newsgroups", "").split(",")]
            hits = [g for g in ng if g in FAMS[fam]["header_groups"]]
            if not hits or "from" not in h: continue
            ts = epoch(h.get("date"))
            if ts is None: continue
            raw_seen[fam] += 1
            _, addr = email.utils.parseaddr(h["from"])
            author = hz((addr or h["from"]).lower())
            mid = h.get("message-id", "").strip()
            key = mid if mid else hz(f"{author}|{ts}|{h.get('subject','')}")
            if key in recs[fam]: continue                      # stripped-path double-store / refile dedup
            refs = h.get("references", "").split()
            root = refs[0] if refs else (mid or key)
            recs[fam][key] = dict(group=hits[0], author=author, ts=int(ts), msgid=mid, root=root,
                                  subject=h.get("subject", ""), text=strip_body(body),
                                  crosspost=len(ng) > 1)
    except Exception as e:
        print(f"  truncated {tp.name}: {type(e).__name__} (kept partial)")
    finally:
        tf.close()
    if (ti + 1) % 25 == 0:
        print(f"  {ti+1}/{len(tapes)}: " + ", ".join(f"{f}={len(recs[f])}" for f in FAMS), flush=True)

# ---------- characterization ----------
def gini(x):
    x = np.sort(np.array(x, float)); n = len(x)
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)

def yr(ts): return dt.datetime.utcfromtimestamp(ts).year

def signature(ev, K=3):
    info = {a: (len(t), set(map(yr, t))) for a, t in ev.items()}
    N_item = sum(n for n, _ in info.values())
    years = sorted({y for _, ys in info.values() for y in ys})
    core = {a for a, (n, ys) in info.items() if len(ys) >= K}
    core_items = sum(n for a, (n, ys) in info.items() if a in core)
    def active(pop, y): return {a for a in pop if y in info[a][1]}
    def jac(pop):
        js = [len(active(pop, y) & active(pop, y+1)) / max(len(active(pop, y) | active(pop, y+1)), 1) for y in years[:-1]]
        return np.mean(js) if js else 0.0
    jc, jp = jac(core), jac(set(ev))
    byc = defaultdict(list)
    for a, (n, ys) in info.items(): byc[min(ys)].append(a in core)
    cutoff = years[-1] - (K - 1)
    conv = [np.mean(byc[y]) for y in sorted(byc) if y <= cutoff and len(byc[y]) >= 10]
    core_yrs = [len(ys) for a, (n, ys) in info.items() if a in core]
    return dict(core_n=len(core), core_dominance=100*core_items/N_item,
                stability_ratio=(jc/jp if jp else float('nan')), core_jac=jc, pop_jac=jp,
                permeability=100*np.mean(conv) if conv else float('nan'),
                med_core_years=float(np.median(core_yrs)) if core_yrs else 0)

summary = {}
for fam, rr in recs.items():
    arts = sorted(rr.values(), key=lambda r: r["ts"])
    ev = defaultdict(list)
    for r in arts: ev[r["author"]].append(r["ts"])
    counts = [len(v) for v in ev.values()]; tot = len(arts)
    ten = [(max(v) - min(v)) / 86400 for v in ev.values()]
    peryear = Counter(yr(r["ts"]) for r in arts)
    pergroup = Counter(r["group"] for r in arts)
    th = Counter(r["root"] for r in arts)
    blens = [len(r["text"]) for r in arts]
    sig = signature(ev)
    lo, hi = arts[0]["ts"], arts[-1]["ts"]
    print(f"\n=== {fam}: {tot} articles (raw {raw_seen[fam]}, dedup removed {raw_seen[fam]-tot}), "
          f"{len(ev)} authors, {dt.datetime.utcfromtimestamp(lo):%Y-%m}..{dt.datetime.utcfromtimestamp(hi):%Y-%m} ===")
    print("  per group: " + ", ".join(f"{g}={n}" for g, n in pergroup.most_common()))
    print("  per year:  " + "  ".join(f"{y}:{peryear[y]}" for y in sorted(peryear)))
    print(f"  crossposted: {100*np.mean([r['crosspost'] for r in arts]):.0f}%")
    print(f"  body chars: median {int(np.median(blens))}, mean {int(np.mean(blens))}; empty(<20ch): {sum(b<20 for b in blens)}")
    print(f"  threads: {len(th)}; median len {int(np.median(list(th.values())))}; % items in threads>=2: "
          f"{100*sum(n for n in th.values() if n>1)/tot:.0f}%")
    print(f"  Gini {gini(counts):.2f}; top-5 authors {100*sum(sorted(counts,reverse=True)[:5])/tot:.0f}%; "
          f"drive-by(<7d) {100*np.mean([t<7 for t in ten]):.0f}%; "
          f"deep(>1yr) {100*np.mean([t>365 for t in ten]):.0f}% of authors -> "
          f"{100*sum(len(v) for v in ev.values() if (max(v)-min(v))/86400>365)/tot:.0f}% of items")
    print(f"  churn/core (K=3): core {sig['core_n']} auth, dominance {sig['core_dominance']:.0f}%, "
          f"stability {sig['stability_ratio']:.1f}x ({sig['core_jac']:.2f}/{sig['pop_jac']:.2f}), "
          f"permeability {sig['permeability']:.0f}%, med core yrs {sig['med_core_years']:.0f}")
    summary[fam] = dict(n=tot, n_authors=len(ev), span=[int(lo), int(hi)],
                        per_year={str(y): peryear[y] for y in sorted(peryear)},
                        per_group=dict(pergroup), churn=sig)

json.dump({f: list(sorted(rr.values(), key=lambda r: r["ts"])) for f, rr in recs.items()},
          open(S / "baseline_corpora2.json", "w"))
json.dump(summary, open(S / "baseline_corpora2_summary.json", "w"), indent=1)
print(f"\nsaved baseline_corpora2.json + baseline_corpora2_summary.json")
