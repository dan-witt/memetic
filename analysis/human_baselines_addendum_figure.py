#!/usr/bin/env python3
"""Addendum figure (core-to-core). Register-controlled idea-diversity of the agent CORE relative to three
human cores, as the ratio agent_core / comparator across three embedders (the bar spans the embedder
range; parity = 1.0). Against a topic-matched insular human SELF-GOVERNANCE core the agent core straddles
parity; the larger gaps vs a hobby core and a broad forum are topic breadth. Reads addendum_results.json."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "results" / "human_baselines"
SURFACE = "#fcfcfb"; INK = "#0b0b0b"; MUTED = "#8a887f"; GRID = "#e4e3db"; BASE = "#c3c2b7"
PAR = "#2e7d5b"; GAP = "#c65a2e"                          # parity green, topic-gap orange
d = json.loads((OUT / "addendum_results.json").read_text())["core_to_core"]["agent_core_over"]
rows = [  # (label, tag, values, is_parity)
    ("vs. matched insular\nself-governance core", "≈ parity", d["usenet_gov_core_bge_mpnet_gte"], True),
    ("vs. insular hobby core", "topic breadth", d["insular_hobby_core_bge_mpnet_gte"], False),
    ("vs. broad forum", "topic breadth", d["hn_diverse_bge_mpnet_gte"], False),
]

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9.6, 3.5), dpi=200); fig.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE); ax.grid(True, axis="x", color=GRID, linewidth=.7, zorder=0)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(BASE); ax.tick_params(colors=MUTED, labelsize=9)

ys = [2, 1, 0]
for y, (label, tag, vals, par) in zip(ys, rows):
    lo, hi, mid = min(vals), max(vals), sorted(vals)[1]; col = PAR if par else GAP
    ax.plot([lo, hi], [y, y], color=col, lw=11, solid_capstyle="round", zorder=2, alpha=.85)
    ax.scatter([mid], [y], s=90, color=col, zorder=4, edgecolor=SURFACE, linewidth=1.4)
    ax.annotate(f"{lo:.2f}–{hi:.2f}", (hi, y), xytext=(9, 0), textcoords="offset points",
                ha="left", va="center", color=col, fontsize=9, fontweight="bold")
    ax.annotate(tag, ((lo+hi)/2, y), xytext=(0, 13), textcoords="offset points", ha="center", color=MUTED, fontsize=8)
ax.axvline(1.0, color=BASE, lw=1.3, linestyle=(0, (3, 3)), zorder=1)
ax.annotate("human parity", (1.0, 2.62), ha="center", color=MUTED, fontsize=8)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=9.5, color=INK)
ax.set_xlim(0.5, 1.2); ax.set_ylim(-0.55, 2.95)
ax.set_xlabel("agent-core idea-diversity as a fraction of the human core's (register-controlled, 3 embedders)", color=MUTED, fontsize=9)
ax.set_title("Core-to-core: agent idea-diversity ≈ a matched human self-governance core",
             loc="left", color=INK, fontsize=11, fontweight="bold", pad=22)
fig.tight_layout()
fig.savefig(OUT / "addendum_figure.png", facecolor=SURFACE); fig.savefig(OUT / "addendum_figure.svg", facecolor=SURFACE)
print("wrote addendum_figure.png")
