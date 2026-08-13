#!/usr/bin/env python3
"""Allocation figure: (A) venue-directed share per pool — Qwen full-pool bars with
identity-blocked bands, Gemma sample medians overlaid as dots (the classifier-dependence is the
point); (B) the agent square's daily venue share vs the anchors' range."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parent.parent / "results/allocation"
d = json.load(open(R / "results.json"))

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; MUTED = "#898781"; GRID = "#e1e0d9"; BASE = "#c3c2b7"
C_AGENT = "#2a78d6"; C_ANCH = "#c3c2b7"; C_GEMMA = "#eb6834"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.3), dpi=200, gridspec_kw={"width_ratios": [1.3, 1]})
fig.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7, axis="y")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"): ax.spines[sp].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)

pools = sorted(d["venue_share_qwen_full"], key=lambda k: -d["venue_share_qwen_full"][k]["venue_share"])
xs = range(len(pools))
for i, k in enumerate(pools):
    v = d["venue_share_qwen_full"][k]
    col = C_AGENT if k == "agent" else C_ANCH
    ax1.bar(i, v["venue_share"], color=col, width=.62, zorder=2)
    lo, hi = v["identity_block_band"][1], v["identity_block_band"][2]
    ax1.plot([i, i], [lo, hi], color=INK, lw=1.2, zorder=3)
    g = d["gemma_agreement_sample"]["per_pool_shares"].get(k)
    if g: ax1.plot(i, g["gemma_share"], "o", color=C_GEMMA, ms=6, zorder=4)
ax1.set_xticks(list(xs)); ax1.set_xticklabels(pools, fontsize=9.5)
ax1.set_ylabel("venue-directed share of claims", color=MUTED, fontsize=9)
ax1.set_title("A · How much of each community's discourse is about itself", loc="left", color=INK, fontsize=10.5)
handles = [plt.Rectangle((0, 0), 1, 1, color=C_AGENT), plt.Rectangle((0, 0), 1, 1, color=C_ANCH),
           plt.Line2D([], [], marker="o", ls="", color=C_GEMMA)]
ax1.legend(handles, ["agent square (Qwen, identity-blocked band)", "human anchors (Qwen)",
                     "Gemma on the agreement sample (stricter)"], frameon=False, fontsize=8, loc="upper right")

dd = d["agent_daily_venue_share_qwen"]
days = list(dd)
ax2.plot(range(len(days)), [dd[k] for k in days], color=C_AGENT, lw=1.8, marker="o", ms=4)
anchors = [v["venue_share"] for k, v in d["venue_share_qwen_full"].items() if k != "agent"]
ax2.axhspan(min(anchors), max(anchors), color=BASE, alpha=.35, lw=0)
ax2.text(0, max(anchors) + 0.012, "anchor range (full histories)", color=MUTED, fontsize=8, va="bottom")
ymax = max(v for yr in d["usenet_yearly_venue_share_qwen"].values() for v in yr.values())
ax2.axhline(ymax, color=MUTED, lw=1.0, ls=(0, (3, 3)))
ax2.text(len(d["agent_daily_venue_share_qwen"]) - 1, ymax + 0.012, "highest anchor-YEAR (forth 1991)",
         color=MUTED, fontsize=8, ha="right", va="bottom")
ax2.set_xticks(range(len(days))); ax2.set_xticklabels(days, fontsize=8.5, rotation=45)
ax2.set_ylabel("agent venue share / day (Qwen)", color=MUTED, fontsize=9)
ax2.set_ylim(0, 0.6)
ax2.set_title("B · The square's self-focus by day", loc="left", color=INK, fontsize=10.5)

fig.suptitle("Allocation: what fraction of the discourse is about the venue itself",
             x=0.01, ha="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.93))
for ext in ("png", "svg"):
    fig.savefig(R / f"figure.{ext}", facecolor=SURFACE, bbox_inches="tight")
print("saved", R / "figure.png")
