#!/usr/bin/env python3
"""Figure for results/human_baselines/report.md: relative diversity of an AI-agent
forum vs two human baselines across five instruments. Each instrument is normalized
to the diverse human forum (=1.0), so all five share one axis; a value below 1.0
means less diverse than diverse humans, i.e. more self-referential. Reads
results/human_baselines/results.json; writes figure.{png,svg}. Generic labels only.
CPU-only (matplotlib)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "results" / "human_baselines"
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
AGENT="#4a3aa7"; INSULAR="#2a78d6"; DIVERSE="#eb6834"

d = json.loads((OUT / "results.json").read_text())
grid = d["grid"]
rows = ["zstd_novelty", "lm_perplexity_short", "lm_perplexity_long", "vendi_semantic", "rolling_vendi"]
labels = {"zstd_novelty": "verbatim\n(zstd novelty)", "lm_perplexity_short": "token, local\n(LM 3k window)",
          "lm_perplexity_long": "token, long\n(LM 15k window)", "vendi_semantic": "semantic\n(Vendi)",
          "rolling_vendi": "semantic, over time\n(rolling Vendi)"}

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=200); fig.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE); ax.grid(True, axis="x", color=GRID, linewidth=.7)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(BASE); ax.tick_params(colors=MUTED, labelsize=9)

ys = list(range(len(rows)))[::-1]
ax.axvline(1.0, color=BASE, lw=1.2, linestyle=(0, (3, 3)), zorder=1)
for y, key in zip(ys, rows):
    g = grid[key]; div = g["diverse"]
    a, i, v = g["agent"] / div, g["insular"] / div, 1.0
    ax.plot([min(a, i, v), max(a, i, v)], [y, y], color=GRID, lw=2.5, zorder=1)
    dissent = "caveat" in g
    ax.scatter([a], [y], s=115, color=AGENT, edgecolors=SURFACE, linewidths=1.4, zorder=3)
    ax.scatter([i], [y], s=95, color=INSULAR, edgecolors=SURFACE, linewidths=1.4, zorder=3)
    ax.scatter([v], [y], s=95, color=DIVERSE, edgecolors=SURFACE, linewidths=1.4, zorder=3)
    ax.annotate(f"{a:.2f}", (a, y), xytext=(0, 9), textcoords="offset points",
                ha="center", color=AGENT, fontsize=8, fontweight="bold")
    if dissent:
        ax.annotate("⚠ window-confounded; least reliable here", (i, y), xytext=(0, -14),
                    textcoords="offset points", ha="center", va="top", color=MUTED,
                    fontsize=7.5, style="italic")

ax.set_yticks(ys); ax.set_yticklabels([labels[k] for k in rows], fontsize=9, color=INK)
ax.set_xlim(0.30, 1.12)
ax.set_xlabel("relative diversity  (diverse human forum = 1.0;  ← more self-referential)",
              color=MUTED, fontsize=9.5)
ax.set_title("An AI-agent forum is more self-referential than human forums —\nand the gap is largest at the level of meaning",
             loc="left", color=INK, fontsize=12, fontweight="bold", pad=14)
# legend
from matplotlib.lines import Line2D
leg = [Line2D([0], [0], marker="o", color="none", markerfacecolor=c, markersize=9, label=l)
       for c, l in [(AGENT, "AI-agent forum"), (INSULAR, "insular human forum"), (DIVERSE, "diverse human forum")]]
ax.legend(handles=leg, frameon=False, fontsize=8.5, loc="lower left", labelcolor=INK, ncol=3,
          bbox_to_anchor=(0, -0.16))
fig.tight_layout()
fig.savefig(OUT / "figure.png", facecolor=SURFACE); fig.savefig(OUT / "figure.svg", facecolor=SURFACE)

# --- second figure: rolling semantic diversity over time (the maturity control) ---
curves = d["rolling_vendi_curves"]
fig2, ax2 = plt.subplots(figsize=(9.2, 4.4), dpi=200); fig2.set_facecolor(SURFACE)
ax2.set_facecolor(SURFACE); ax2.grid(True, color=GRID, linewidth=.7)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
for s in ("bottom", "left"): ax2.spines[s].set_color(BASE)
ax2.tick_params(colors=MUTED, labelsize=9)
for key, col, lab in [("agent", AGENT, "AI-agent forum (≈ 3 days)"),
                      ("insular", INSULAR, "insular human forum (multi-year)"),
                      ("diverse", DIVERSE, "diverse human forum")]:
    c = curves[key]; xs = [i / (len(c) - 1) for i in range(len(c))]
    ax2.plot(xs, c, color=col, lw=1.9, marker="o", markersize=2.5, label=lab)
ax2.set_ylim(0, 0.16); ax2.set_xlim(0, 1)
ax2.set_xlabel("position through each corpus's own timeline  (0 = first item → 1 = last)",
               color=MUTED, fontsize=9)
ax2.set_ylabel("local semantic diversity\n(rolling Vendi / W, W = 120 items)", color=MUTED, fontsize=9)
ax2.set_title("Local diversity is flat over time — the agent gap is not a maturity artifact\n"
              "(fixed-count windows credit the multi-year forum nothing for age; agents stay at ~half throughout)",
              loc="left", color=INK, fontsize=10.5, pad=10)
ax2.legend(frameon=False, fontsize=8.5, loc="center right", labelcolor=INK)
fig2.tight_layout()
fig2.savefig(OUT / "figure_timeseries.png", facecolor=SURFACE)
fig2.savefig(OUT / "figure_timeseries.svg", facecolor=SURFACE)
print("wrote figure.png + figure_timeseries.png")
