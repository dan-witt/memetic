#!/usr/bin/env python3
"""Weather report #1 — CPU-side metrics (no GPU): corpus delta, inflows, cohort survival,
churn signature (window=UTC day, core=active>=3 days, pre-registered), raw-zstd register trend.
Also builds the claim cache keyed by (kind,id) from the pull-1 corpus + existing claims, and
counts the delta items needing GPU claimify. Outputs weather1_cpu.json."""
import json, sys, datetime as dt
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import zstd_curve as Z

def load_items(d):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20]

OLD = load_items(S / "old_corpus/data/posts")
NEW = load_items("/home/dan/personal/memetic/data/posts")
old_claims = json.load(open(S / "baseline_claims/agent_all.json"))
assert len(OLD) == len(old_claims), f"cache misalign: {len(OLD)} vs {len(old_claims)}"
cache = {k: c for (_, k, _, _), c in zip(OLD, old_claims)}
json.dump({f"{k[0]}:{k[1]}": c for k, c in cache.items()}, open(S / "claim_cache_agent.json", "w"))
delta = [(t, k, x, a) for t, k, x, a in NEW if k not in cache]
print(f"pull1 items {len(OLD)}, pull2 items {len(NEW)}, DELTA needing claimify: {len(delta)}")

day = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
days = sorted({day(t) for t, _, _, _ in NEW})
out = {"corpus": {"items": len(NEW), "posts": sum(1 for _, k, _, _ in NEW if k[0] == "post"),
                  "authors": len({a for _, _, _, a in NEW}), "days": days,
                  "delta_items_for_claimify": len(delta)}}

# --- inflows: new authors per day, newcomer share of items ---
first_seen, per_day_new, per_day_items, per_day_active = {}, Counter(), Counter(), defaultdict(set)
newcomer_items = Counter()
for t, k, x, a in NEW:
    d = day(t)
    per_day_items[d] += 1; per_day_active[d].add(a)
    if a not in first_seen:
        first_seen[a] = d; per_day_new[d] += 1
    if first_seen[a] == d: newcomer_items[d] += 1
out["inflows"] = {d: {"new_authors": per_day_new[d], "active_authors": len(per_day_active[d]),
                      "items": per_day_items[d],
                      "newcomer_item_share": round(newcomer_items[d] / per_day_items[d], 3)} for d in days}

# --- cohort survival: join-day cohorts, % active on each later day ---
by_author_days = defaultdict(set)
for t, k, x, a in NEW: by_author_days[a].add(day(t))
coh = {}
for d in days:
    members = [a for a, fd in first_seen.items() if fd == d]
    if not members: continue
    later = [dd for dd in days if dd > d]
    coh[d] = {"n": len(members),
              "survival": {dd: round(sum(1 for a in members if dd in by_author_days[a]) / len(members), 3)
                           for dd in later},
              "median_active_days": float(np.median([len(by_author_days[a]) for a in members]))}
out["cohort_survival"] = coh

# --- churn signature (pre-registered: window=UTC day, core=active>=3 days) ---
info = {a: ds for a, ds in by_author_days.items()}
core = {a for a, ds in info.items() if len(ds) >= 3}
n_items_core = sum(1 for t, k, x, a in NEW if a in core)
def active(pop, d): return {a for a in pop if d in info[a]}
def jac(pop):
    js = []
    for d1, d2 in zip(days[:-1], days[1:]):
        u = active(pop, d1) | active(pop, d2)
        if u: js.append(len(active(pop, d1) & active(pop, d2)) / len(u))
    return float(np.mean(js)) if js else 0.0
jc, jp = jac(core), jac(set(info))
byc = defaultdict(list)
for a, ds in info.items(): byc[first_seen[a]].append(a in core)
cut = days[-3] if len(days) >= 3 else days[-1]
conv = [np.mean(byc[d]) for d in sorted(byc) if d <= cut and len(byc[d]) >= 10]
out["churn_signature_day_K3"] = {
    "core_n": len(core), "core_dominance_pct": round(100 * n_items_core / len(NEW), 1),
    "stability_ratio": round(jc / jp, 2) if jp else None, "core_jac": round(jc, 3), "pop_jac": round(jp, 3),
    "newcomer_permeability_pct": round(100 * float(np.mean(conv)), 1) if conv else None,
    "median_core_days": float(np.median([len(info[a]) for a in core])) if core else 0}

# --- register trend: raw zstd novelty, whole timeline + per-day aggregate ---
class Args: level = 19; window_bytes = 524288; bucket = 25; seed = 42
mk = [{"kind": k[0], "id": k[1], "post_id": 0, "created_at": t, "author": a, "author_model": "", "text": x}
      for t, k, x, a in NEW]
rows = Z.compute_metrics(mk, Args())
agg = lambda rs: sum(r["cond_win_bits"] for r in rs) / sum(r["self_bits"] for r in rs)
per_day_z = {}
for d in days:
    rs = [r for r in rows if day(r["created_at"]) == d]
    if len(rs) >= 50: per_day_z[d] = round(agg(rs), 4)
out["zstd_raw"] = {"whole": round(agg(rows), 4), "per_day": per_day_z,
                   "pull1_whole": 0.644, "band_floor": 0.704}
json.dump(out, open(S / "weather1_cpu.json", "w"), indent=1)
print(json.dumps(out["churn_signature_day_K3"]))
print("inflow days:", {d: v["new_authors"] for d, v in out["inflows"].items()})
print("zstd per day:", per_day_z)
print("saved weather1_cpu.json")
