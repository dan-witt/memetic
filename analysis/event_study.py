#!/usr/bin/env python3
"""Disclosure-norm event study over the 1f916.ai corpus.

Uses the per-item LLM classification in data/labels/items.csv
(is_exogenous + four self-disclosure fields) to measure whether
peppercorn's provenance-interrogation sweep (comments 1300-1303,
2026-08-07 06:39-06:40 UTC) changed disclosure behavior — especially
P(disclosure | exogenous item).

Outputs to results/disclosure_event_study/: rates.csv (6h-bucket series),
event_study.json (summary stats), figure.png/.svg.

  .venv/bin/python analysis/event_study.py
"""

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "disclosure_event_study"
OUT.mkdir(parents=True, exist_ok=True)

# --- palette (dataviz reference instance, light mode, validated order) ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
S_BLUE = "#2a78d6"
S_ORANGE = "#eb6834"
S_AQUA = "#1baf7a"

rows = list(csv.DictReader((REPO / "data" / "labels" / "items.csv").open()))
for r in rows:
    r["created_at"] = int(r["created_at"])
    r["exo"] = r["is_exogenous"] == "yes"
    r["disclosed"] = (r["topic_selector"] != "unstated"
                      or r["human_reviewed"] != "unstated"
                      or r["invocation"] != "unstated"
                      or r["autonomy_claim"] == "explicit")
rows.sort(key=lambda r: r["created_at"])
t0 = rows[0]["created_at"]
h = lambda ms: (ms - t0) / 3.6e6

# event anchors
sweep_ms = min(r["created_at"] for r in rows
               if r["kind"] == "comment" and r["id"] in ("1300", "1301", "1302", "1303"))
midnight2_ms = 1786060800000  # 2026-08-07 00:00 UTC (quota reset, posts 210/211 follow)
midnight3_ms = 1786147200000  # 2026-08-08 00:00 UTC
print(f"sweep anchor: {time.strftime('%m-%d %H:%M UTC', time.gmtime(sweep_ms/1000))} "
      f"(h{h(sweep_ms):.1f})")

first_seen = set()
for r in rows:  # author's first item (arrival disclosures live here)
    r["is_first"] = r["author"] not in first_seen
    first_seen.add(r["author"])


def rate(rs):
    return round(sum(r["disclosed"] for r in rs) / len(rs), 4) if rs else None


def richness(rs):
    """Mean number of stated disclosure fields among disclosing items."""
    vals = []
    for r in rs:
        if r["disclosed"]:
            vals.append((r["topic_selector"] != "unstated")
                        + (r["human_reviewed"] != "unstated")
                        + (r["invocation"] != "unstated")
                        + (r["autonomy_claim"] == "explicit"))
    return round(sum(vals) / len(vals), 3) if vals else None


# --- 6h bucket series ---
buckets = defaultdict(list)
for r in rows:
    buckets[int(h(r["created_at"]) // 6)].append(r)
series = []
for b in sorted(buckets):
    rs = buckets[b]
    exo = [r for r in rs if r["exo"]]
    endo = [r for r in rs if not r["exo"]]
    series.append({
        "bucket_start_h": 6 * b, "n": len(rs),
        "exo_share": round(len(exo) / len(rs), 4),
        "disclosure_rate_exo": rate(exo), "n_exo": len(exo),
        "disclosure_rate_endo": rate(endo), "n_endo": len(endo),
        "disclosure_rate_all": rate(rs),
        "disclosure_richness": richness(rs),
    })
with (OUT / "rates.csv").open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(series[0].keys()))
    w.writeheader()
    w.writerows(series)

# --- before/after contrasts at each anchor ---
def contrast(anchor_ms, name):
    pre = [r for r in rows if r["created_at"] < anchor_ms]
    post = [r for r in rows if r["created_at"] >= anchor_ms]
    seg = {}
    for tag, pred in [("exo", lambda r: r["exo"]),
                      ("endo", lambda r: not r["exo"]),
                      ("first_item", lambda r: r["is_first"]),
                      ("non_first", lambda r: not r["is_first"]),
                      ("posts_exo", lambda r: r["exo"] and r["kind"] == "post")]:
        p0, p1 = [r for r in pre if pred(r)], [r for r in post if pred(r)]
        seg[tag] = {"pre_rate": rate(p0), "post_rate": rate(p1),
                    "pre_n": len(p0), "post_n": len(p1)}
    seg["richness_exo"] = {
        "pre": richness([r for r in pre if r["exo"]]),
        "post": richness([r for r in post if r["exo"]])}
    return {"anchor": name, "anchor_ms": anchor_ms, "anchor_h": round(h(anchor_ms), 2),
            "segments": seg}

contrasts = [contrast(sweep_ms, "peppercorn_sweep"),
             contrast(midnight2_ms, "midnight_aug7_placebo"),
             contrast(midnight3_ms, "midnight_aug8_placebo")]

summary = {
    "n_items": len(rows),
    "n_exogenous": sum(1 for r in rows if r["exo"]),
    "n_disclosing": sum(1 for r in rows if r["disclosed"]),
    "sweep_ms": sweep_ms,
    "contrasts": contrasts,
}
(OUT / "event_study.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

# --- figure ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

xs = [s["bucket_start_h"] + 3 for s in series]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.2), sharex=True, dpi=200)
fig.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE)
    ax.grid(True, axis="y", color=GRID, linewidth=0.75)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)

ax1.plot(xs, [s["exo_share"] for s in series], color=S_BLUE, linewidth=2,
         marker="o", markersize=4, label="share of items that are exogenous")
ax1.set_title("Exogenous content share (6h buckets)", loc="left", color=INK, fontsize=11)
ax1.set_ylabel("share of items", color=MUTED, fontsize=9)
ax1.legend(frameon=False, fontsize=8.5, loc="upper left", labelcolor=INK)

ax2.plot(xs, [s["disclosure_rate_exo"] for s in series], color=S_ORANGE, linewidth=2,
         marker="o", markersize=4, label="P(disclosure | exogenous)")
ax2.plot(xs, [s["disclosure_rate_endo"] for s in series], color=S_AQUA, linewidth=2,
         marker="o", markersize=4, label="P(disclosure | endogenous)")
ax2.set_title("Self-disclosure rate by content type (6h buckets)",
              loc="left", color=INK, fontsize=11)
ax2.set_ylabel("disclosure rate", color=MUTED, fontsize=9)
ax2.set_xlabel("hours since first post", color=MUTED, fontsize=9)
ax2.legend(frameon=False, fontsize=8.5, loc="upper left", labelcolor=INK)

for ax in (ax1, ax2):
    ax.axvline(h(sweep_ms), color=BASELINE, linewidth=1.2, linestyle=(0, (3, 3)))
    for m in (midnight2_ms, midnight3_ms):
        ax.axvline(h(m), color=GRID, linewidth=1, linestyle=(0, (1, 2)))
ax1.annotate("peppercorn sweep\n(1300-1303)", (h(sweep_ms), ax1.get_ylim()[1]),
             xytext=(5, -4), textcoords="offset points", color=MUTED, fontsize=8, va="top")
ax1.annotate("UTC midnights", (h(midnight2_ms), ax1.get_ylim()[0]),
             xytext=(5, 6), textcoords="offset points", color=MUTED, fontsize=7.5)

fig.suptitle("1f916.ai - the provenance-disclosure norm", x=0.01, ha="left",
             color=INK, fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(OUT / "figure.png", facecolor=SURFACE)
fig.savefig(OUT / "figure.svg", facecolor=SURFACE)
print(f"wrote figure -> {OUT}")
