#!/usr/bin/env python3
"""Stratified views of the zstd novelty metrics: author tenure, post tenure,
per-day composition, arrival-ritual incidence, and provenance-brief strata
(joined from data/labels/authors.csv).

Requires results/zstd_curve/metrics.jsonl (run zstd_curve.py first).
Prints tables and writes results/zstd_curve/strata.json.

  .venv/bin/python analysis/stratify.py
"""

import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "zstd_curve"

rows = [json.loads(l) for l in (OUT / "metrics.jsonl").open()]
rows.sort(key=lambda r: r["seq"])
run = json.loads((OUT / "run.json").read_text())
WFULL = run["window_full_ms"]
EVENT = run["event_marker_ms"]

# tenure annotations
item_n, post_n = Counter(), Counter()
for r in rows:
    item_n[r["author"]] += 1
    r["item_tenure"] = item_n[r["author"]]
    if r["kind"] == "post":
        post_n[r["author"]] += 1
        r["post_tenure"] = post_n[r["author"]]

labels = {}
labels_path = REPO / "data" / "labels" / "authors.csv"
if labels_path.exists():
    for lr in csv.DictReader(labels_path.open()):
        if lr.get("provenance_flag"):
            labels[lr["author"]] = (lr["provenance_flag"], lr.get("label_confidence", ""))

ss = [r for r in rows if r["created_at"] >= WFULL]
day_of = lambda r: time.strftime("%m-%d", time.gmtime(r["created_at"] / 1000))


def nov(rs):
    s = sum(r["self_bits"] for r in rs)
    return round(sum(r["cond_win_bits"] for r in rs) / s, 4) if s else None


result = {"steady_state_items": len(ss), "window_full_ms": WFULL}

print(f"steady-state items: {len(ss)}\n")

print("== novelty by author item-tenure ==")
result["item_tenure"] = {}
for lo, hi in [(1, 1), (2, 2), (3, 5), (6, 10), (11, 20), (21, 10**9)]:
    seg = [r for r in ss if lo <= r["item_tenure"] <= hi]
    label = f"{lo}" if lo == hi else f"{lo}-{hi if hi < 10**9 else '+'}"
    result["item_tenure"][label] = {"n": len(seg), "novelty": nov(seg)}
    print(f"  item {label:>5}: n={len(seg):4d}  novelty {nov(seg)}")

print("\n== novelty by post-tenure (posts only) ==")
result["post_tenure"] = {}
for lo, hi, label in [(1, 1, "1st"), (2, 2, "2nd"), (3, 10**9, "3rd+")]:
    seg = [r for r in ss if r["kind"] == "post" and lo <= r.get("post_tenure", 0) <= hi]
    result["post_tenure"][label] = {"n": len(seg), "novelty": nov(seg)}
    print(f"  {label} post: n={len(seg):4d}  novelty {nov(seg)}")

print("\n== per-UTC-day novelty within tenure strata ==")
strata = {"first_item": lambda r: r["item_tenure"] == 1,
          "items_2_5": lambda r: 2 <= r["item_tenure"] <= 5,
          "items_6plus": lambda r: r["item_tenure"] >= 6}
result["per_day"] = {}
for d in sorted({day_of(r) for r in ss}):
    drows = [r for r in ss if day_of(r) == d]
    entry = {name: {"n": len([r for r in drows if pred(r)]),
                    "novelty": nov([r for r in drows if pred(r)])}
             for name, pred in strata.items()}
    entry["share_6plus"] = round(sum(1 for r in drows if r["item_tenure"] >= 6) / len(drows), 3)
    result["per_day"][d] = entry
    print(f"  {d}: " + "  ".join(f"{k} {v['novelty']}({v['n']})" if isinstance(v, dict) else f"6+share {v}"
                                 for k, v in entry.items()))

print("\n== posts: author's nth post by UTC day (composition) ==")
seen = Counter()
result["nth_post_by_day"] = defaultdict(dict)
day_nth = defaultdict(Counter)
for r in rows:
    if r["kind"] != "post":
        continue
    seen[r["author"]] += 1
    day_nth[day_of(r)][min(seen[r["author"]], 3)] += 1
for d in sorted(day_nth):
    c = day_nth[d]
    tot = sum(c.values())
    result["nth_post_by_day"][d] = {"n": tot, "first": round(c[1] / tot, 3),
                                    "second": round(c[2] / tot, 3), "third_plus": round(c[3] / tot, 3)}
    print(f"  {d}: n={tot:3d}  1st={c[1]/tot:.0%} 2nd={c[2]/tot:.0%} 3rd+={c[3]/tot:.0%}")

print("\n== 'my human' incidence per 6h bucket (arrival-ritual proxy) ==")
# needs item text: pull from corpus
text_of = {}
for f in (REPO / "data" / "posts").glob("*.json"):
    th = json.loads(f.read_text())
    p = th["post"]
    text_of[("post", p["id"])] = ((p.get("title") or "") + "\n" + (p.get("body") or "")).lower()
    for c in th["comments"]:
        text_of[("comment", c["id"])] = (c.get("body") or "").lower()
t0 = rows[0]["created_at"]
byb = defaultdict(lambda: [0, 0])
for r in rows:
    b = int((r["created_at"] - t0) / 3.6e6 // 6)
    byb[b][0] += 1
    if "my human" in text_of[(r["kind"], r["id"])]:
        byb[b][1] += 1
result["my_human_by_6h"] = {f"h{6*b}-{6*b+6}": {"n": n, "k": k, "rate": round(k / n, 4)}
                            for b, (n, k) in sorted(byb.items())}
for b, (n, k) in sorted(byb.items()):
    print(f"  h{6*b:3d}-{6*b+6:3d}: {k:3d}/{n:4d} ({k/n:5.1%})")

if labels:
    print("\n== novelty by provenance flag ==")
    result["provenance"] = {"n_authors": dict(Counter(l for l, _ in labels.values()))}
    cuts = {"all_items": lambda r: True,
            "first_items": lambda r: r["item_tenure"] == 1,
            "posts": lambda r: r["kind"] == "post",
            "veteran_6plus": lambda r: r["item_tenure"] >= 6}
    for cname, pred in cuts.items():
        result["provenance"][cname] = {}
        line = f"  {cname:>13}: "
        for flag in ("directed", "open", "autonomous", "unstated"):
            seg = [r for r in ss if labels.get(r["author"], ("?",))[0] == flag and pred(r)]
            result["provenance"][cname][flag] = {"n": len(seg), "novelty": nov(seg)}
            line += f"{flag} {nov(seg)}({len(seg)})  "
        print(line)

print("\n== length-quartile robustness (novelty is ~length-invariant) ==")
srt = sorted(rows, key=lambda r: r["chars"])
q = len(srt) // 4
result["length_quartiles"] = {}
for i, name in enumerate(["Q1_shortest", "Q2", "Q3", "Q4_longest"]):
    seg = srt[i * q:(i + 1) * q if i < 3 else len(srt)]
    ch = sum(r["chars"] for r in seg)
    result["length_quartiles"][name] = {
        "chars_min": seg[0]["chars"], "chars_max": seg[-1]["chars"],
        "self_bpc": round(sum(r["self_bits"] for r in seg) / ch, 3),
        "cond_bpc": round(sum(r["cond_win_bits"] for r in seg) / ch, 3),
        "novelty": nov(seg)}
    v = result["length_quartiles"][name]
    print(f"  {name}: self {v['self_bpc']} cond {v['cond_bpc']} novelty {v['novelty']}")

(OUT / "strata.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"\nwrote {OUT / 'strata.json'}")
