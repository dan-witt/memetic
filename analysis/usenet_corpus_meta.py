#!/usr/bin/env python3
"""Build the Usenet PLATFORM-GOVERNANCE corpora from the UTZOO tapes.

WHY THIS EXISTS
The lemmy_baseline report argues that the earlier ~5x contrast (agent square vs comp.lang.lisp)
compared an undifferentiated platform against a single-topic group whose platform-level governance
traffic "lived elsewhere on the network". A cold review correctly flagged that as asserted, never
measured -- no such cell exists in any report.

This builds the missing cell. Usenet's venue-directed discourse -- newsgroup creation, charters,
moderation policy, propagation and site administration -- happened in dedicated groups, exactly as
lemmy.world's happens in c/newcommunities and c/lemmyworld rather than in c/cat. If those groups
exist in the archive and carry a high VENUE share, then the lisp comparison omitted Usenet's
equivalent of lemmy's meta tier, and the platform-vs-platform argument is measured rather than
argued.

Group families follow the same lineage-merge rule as usenet_corpus_langs.py: path = the group's own
directory (the reader's view of the venue), confirmed against the article's Newsgroups: header,
deduped by Message-ID. Pre-1983 A-news articles carry `Posted:`/`Title:`/`Article-I.D.:` instead of
RFC822 headers; both spellings are accepted here (the language-corpus builders accept only the
RFC822 form, which is why every net.* lineage there appears to begin in 1983).

Output: baseline_corpora_meta.json + baseline_corpora_meta_summary.json
"""
import tarfile, email.utils, hashlib, json, os, re, datetime as dt
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

TAPES = Path("/home/dan/media/utzoo/tapes")
S = Path(os.environ.get("MEMETIC_WORKDIR", "."))

FAMS = {
    # newsgroup creation / charters / naming -- the direct analogue of c/newcommunities
    "groups": {"path_groups": {"net.news.group", "news.groups", "net.news.newsite",
                               "news.announce.newgroups"},
               "header_groups": {"net.news.group", "news.groups", "net.news.newsite",
                                 "news.announce.newgroups"}},
    # site administration, propagation, policy -- the analogue of c/lemmyworld
    "admin":  {"path_groups": {"net.news.adm", "news.admin", "net.news.config", "news.config",
                               "net.news.sa", "news.sysadmin"},
               "header_groups": {"net.news.adm", "news.admin", "net.news.config", "news.config",
                                 "net.news.sa", "news.sysadmin"}},
    # general meta-discussion about the net itself -- the analogue of c/fediverse
    "netmeta": {"path_groups": {"net.news", "news.misc", "net.news.b", "news.software.b",
                                "net.announce", "news.announce.important"},
                "header_groups": {"net.news", "news.misc", "net.news.b", "news.software.b",
                                  "net.announce", "news.announce.important"}},
}


def hz(s):
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:12]


def parse(raw):
    t = raw.decode("latin-1", "replace")
    head, _, body = t.partition("\n\n")
    h = {}
    for ln in head.split("\n"):
        if ln[:1] in (" ", "\t") or ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        h[k.strip().lower()] = v.strip()
    return h, body


def epoch(h):
    """RFC822 Date:, else A-news Posted:. Both spellings, sane 1979..1992 window."""
    for key in ("date", "posted"):
        s = h.get(key)
        if not s:
            continue
        tt = email.utils.parsedate_tz(s)
        if not tt:
            continue
        try:
            e = email.utils.mktime_tz(tt)
            if 3e8 < e < 7.2e8:
                return e
        except Exception:
            continue
    return None


def strip_body(body):
    out = []
    for l in body.split("\n"):
        s = l.strip()
        if s in ("--", "-- "):
            break
        if s.startswith(">") or s.startswith("|") or re.match(r"^\s*In article|^\s*\w+.* writes:$", l):
            continue
        out.append(l)
    return "\n".join(out).strip()


recs = {f: {} for f in FAMS}
raw_seen = Counter()
tapes = sorted(TAPES.glob("news*.tgz"))
print(f"parsing {len(tapes)} tapes for platform-governance groups ...", flush=True)
for ti, tp in enumerate(tapes):
    try:
        tf = tarfile.open(tp, "r:gz")
    except Exception as e:
        print(f"  skip {tp.name}: {e}"); continue
    try:
        for mem in tf:
            if not mem.isfile():
                continue
            parts = mem.name.split("/")
            if len(parts) < 4 or not parts[-1].isdigit():
                continue
            pg = ".".join(parts[2:-1])
            fam = next((f for f, c in FAMS.items() if pg in c["path_groups"]), None)
            if fam is None:
                continue
            try:
                raw = tf.extractfile(mem).read()
            except Exception:
                continue
            h, body = parse(raw)
            ng = [g.strip() for g in h.get("newsgroups", "").split(",")]
            hits = [g for g in ng if g in FAMS[fam]["header_groups"]]
            if not hits or not (h.get("from") or h.get("article-i.d.")):
                continue
            ts = epoch(h)
            if ts is None:
                continue
            raw_seen[fam] += 1
            frm = h.get("from", "")
            _, addr = email.utils.parseaddr(frm)
            author = hz((addr or frm or h.get("article-i.d.", "?")).lower())
            mid = (h.get("message-id") or h.get("article-i.d.") or "").strip()
            subj = h.get("subject") or h.get("title") or ""
            key = mid if mid else hz(f"{author}|{ts}|{subj}")
            if key in recs[fam]:
                continue
            refs = h.get("references", "").split()
            root = refs[0] if refs else (mid or key)
            recs[fam][key] = dict(group=hits[0], author=author, ts=int(ts), msgid=mid, root=root,
                                  subject=subj, text=strip_body(body), crosspost=len(ng) > 1)
    except Exception as e:
        print(f"  truncated {tp.name}: {type(e).__name__} (kept partial)")
    finally:
        tf.close()
    if (ti + 1) % 25 == 0:
        print(f"  {ti+1}/{len(tapes)}: " + ", ".join(f"{f}={len(recs[f])}" for f in FAMS), flush=True)

summary = {}
for fam, rr in recs.items():
    arts = sorted(rr.values(), key=lambda r: r["ts"])
    if not arts:
        print(f"\n=== {fam}: EMPTY ==="); summary[fam] = {"n": 0}; continue
    ev = defaultdict(list)
    for r in arts:
        ev[r["author"]].append(r["ts"])
    blens = [len(r["text"]) for r in arts]
    peryear = Counter(dt.datetime.utcfromtimestamp(r["ts"]).year for r in arts)
    pergroup = Counter(r["group"] for r in arts)
    lo, hi = arts[0]["ts"], arts[-1]["ts"]
    print(f"\n=== {fam}: {len(arts)} articles (raw {raw_seen[fam]}), {len(ev)} authors, "
          f"{dt.datetime.utcfromtimestamp(lo):%Y-%m}..{dt.datetime.utcfromtimestamp(hi):%Y-%m} ===")
    print("  per group: " + ", ".join(f"{g}={n}" for g, n in pergroup.most_common()))
    print("  per year:  " + "  ".join(f"{y}:{peryear[y]}" for y in sorted(peryear)))
    print(f"  body chars: median {int(np.median(blens))}; >=20ch: {sum(b>=20 for b in blens)}/{len(arts)}")
    summary[fam] = dict(n=len(arts), n_authors=len(ev), span=[int(lo), int(hi)],
                        per_year={str(y): peryear[y] for y in sorted(peryear)},
                        per_group=dict(pergroup),
                        median_chars=int(np.median(blens)),
                        keep_ge20=int(sum(b >= 20 for b in blens)))

json.dump({f: sorted(rr.values(), key=lambda r: r["ts"]) for f, rr in recs.items()},
          open(S / "baseline_corpora_meta.json", "w"))
json.dump(summary, open(S / "baseline_corpora_meta_summary.json", "w"), indent=1)
print("\nsaved baseline_corpora_meta.json + summary")
