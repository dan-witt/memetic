#!/usr/bin/env python3
"""Weather issue #2 (2026-08-12) — CPU half. Hard cutoff: items with t >= 2026-08-13T00:00:00Z
are excluded everywhere. Issue window = (last item of issue-1 corpus, cutoff). Same instruments
as issue #1 + NEW: activity-clock churn signatures (7 equal item-count windows, core = active in
>=3 windows) for agent AND anchors — the commensurable young-phase comparison issue #1 promised.
Outputs weather2_cpu.json."""
import json, sys, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import zstd_curve as Z

CUTOFF = dt.datetime(2026, 8, 13, 0, 0, tzinfo=dt.timezone.utc).timestamp()

def load_items(d, cutoff=CUTOFF):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]

PREV = load_items(S / "old_corpus2/data/posts")          # issue-1 corpus state (git HEAD)
NEW = load_items("/home/dan/personal/memetic/data/posts")
prev_last = max(t for t, _, _, _ in PREV)
print(f"issue-1 items {len(PREV)} (last {dt.datetime.utcfromtimestamp(prev_last):%m-%d %H:%M}), "
      f"issue-2 items {len(NEW)} (cutoff 08-13 00:00)", flush=True)

day = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
days = sorted({day(t) for t, _, _, _ in NEW})
out = {"cutoff_utc": "2026-08-13T00:00:00Z", "issue_window_start_utc":
       dt.datetime.utcfromtimestamp(prev_last).strftime("%Y-%m-%d %H:%M"),
       "corpus": {"items": len(NEW), "posts": sum(1 for _, k, _, _ in NEW if k[0] == "post"),
                  "authors": len({a for _, _, _, a in NEW}), "days": days,
                  "issue_window_items": sum(1 for t, _, _, _ in NEW if t > prev_last)}}

first_seen, per_day_new, per_day_items, newcomer_items = {}, Counter(), Counter(), Counter()
per_day_active = defaultdict(set)
for t, k, x, a in NEW:
    d = day(t)
    per_day_items[d] += 1; per_day_active[d].add(a)
    if a not in first_seen: first_seen[a] = d; per_day_new[d] += 1
    if first_seen[a] == d: newcomer_items[d] += 1
out["inflows"] = {d: {"new_authors": per_day_new[d], "active_authors": len(per_day_active[d]),
                      "items": per_day_items[d],
                      "newcomer_item_share": round(newcomer_items[d] / per_day_items[d], 3)} for d in days}

by_author_days = defaultdict(set)
for t, k, x, a in NEW: by_author_days[a].add(day(t))
coh = {}
for d in days:
    members = [a for a, fd in first_seen.items() if fd == d]
    if not members: continue
    coh[d] = {"n": len(members),
              "survival": {dd: round(sum(1 for a in members if dd in by_author_days[a]) / len(members), 3)
                           for dd in days if dd > d},
              "median_active_days": float(np.median([len(by_author_days[a]) for a in members]))}
out["cohort_survival"] = coh

def signature_windows(win_of_item):
    """generic churn signature over arbitrary window labels per item-author stream"""
    info = defaultdict(set)
    counts = Counter()
    for w, a in win_of_item:
        info[a].add(w); counts[a] += 1
    wins = sorted({w for ws in info.values() for w in ws})
    core = {a for a, ws in info.items() if len(ws) >= 3}
    dom = 100 * sum(counts[a] for a in core) / sum(counts.values())
    def act(pop, w): return {a for a in pop if w in info[a]}
    def jac(pop):
        js = [len(act(pop, w1) & act(pop, w2)) / max(len(act(pop, w1) | act(pop, w2)), 1)
              for w1, w2 in zip(wins[:-1], wins[1:])]
        return float(np.mean(js)) if js else 0.0
    jc, jp = jac(core), jac(set(info))
    byc = defaultdict(list)
    firstw = {a: min(ws) for a, ws in info.items()}
    for a in info: byc[firstw[a]].append(a in core)
    cut = wins[-3] if len(wins) >= 3 else wins[-1]
    conv = [np.mean(byc[w]) for w in sorted(byc) if w <= cut and len(byc[w]) >= 10]
    return {"core_n": len(core), "core_dominance_pct": round(dom, 1),
            "stability_ratio": round(jc / jp, 2) if jp else None,
            "permeability_pct": round(100 * float(np.mean(conv)), 1) if conv else None}

# calendar-day signature (series continuity with issue #1)
out["churn_signature_day_K3"] = signature_windows([(day(t), a) for t, k, x, a in NEW])
out["churn_signature_day_K3"]["note"] = "calendar-day windows; series-internal comparison only"

# NEW: activity-clock signatures — 7 equal item-count windows over each corpus's FIRST n_agent items
def anchor_events(fam, src):
    C = json.load(open(S / src))[fam]
    return sorted((r["ts"], r["author"]) for r in C if len(r["text"]) >= 20)
n_agent = len(NEW)
act_sigs = {"agent": signature_windows([(min(6, i * 7 // n_agent), a) for i, (t, k, x, a) in enumerate(NEW)])}
for fam, src in [("lisp", "baseline_corpora.json"), ("sci", "baseline_corpora.json"),
                 ("forth", "baseline_corpora2.json"), ("smalltalk", "baseline_corpora2.json"),
                 ("scheme", "baseline_corpora2.json")]:
    ev = anchor_events(fam, src)[:n_agent]
    n = len(ev)
    act_sigs[fam] = signature_windows([(min(6, i * 7 // n), a) for i, (t, a) in enumerate(ev)]) | \
                    {"n_items": n, "span_days": round((ev[-1][0] - ev[0][0]) / 86400, 0)}
out["activity_clock_signatures"] = {"design": "each corpus's first min(N, n_agent) items split into 7 equal item-count windows; core = active in >=3 windows; clock-free, commensurable by construction",
                                    "signatures": act_sigs}

# register trend
class Args: level = 19; window_bytes = 524288; bucket = 25; seed = 42
mk = [{"kind": k[0], "id": k[1], "post_id": 0, "created_at": t, "author": a, "author_model": "", "text": x}
      for t, k, x, a in NEW]
rows = Z.compute_metrics(mk, Args())
agg = lambda rs: sum(r["cond_win_bits"] for r in rs) / sum(r["self_bits"] for r in rs)
per_day_z = {d: round(agg([r for r in rows if day(r["created_at"]) == d]), 4)
             for d in days if sum(1 for r in rows if day(r["created_at"]) == d) >= 50}
out["zstd_raw"] = {"whole": round(agg(rows), 4), "per_day": per_day_z, "band_floor": 0.704}
json.dump(out, open(S / "weather2_cpu.json", "w"), indent=1)
print("day churn:", out["churn_signature_day_K3"], flush=True)
print("activity-clock:", {k: {kk: v[kk] for kk in ("core_dominance_pct", "stability_ratio", "permeability_pct")}
                          for k, v in act_sigs.items()}, flush=True)
print("inflows:", {d: v["new_authors"] for d, v in out["inflows"].items()}, flush=True)
print("zstd:", per_day_z, flush=True)
print("saved weather2_cpu.json")
