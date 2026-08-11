#!/usr/bin/env python3
"""Figure for results/novelty_bands: (A) idea-level diversity ratio agent/comparator across
3 embedders x 2 normalizers with the parity line; (B) zstd novelty positions per corpus,
raw vs claim-normalized (both normalizers). Reads results/novelty_bands/results.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parent.parent / "results/novelty_bands"
d = json.load(open(R / "results.json"))

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; MUTED = "#898781"; GRID = "#e1e0d9"; BASE = "#c3c2b7"
C_QWEN = "#2a78d6"; C_GEMMA = "#eb6834"; C_RAW = "#898781"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=200,
                               gridspec_kw={"width_ratios": [1.25, 1]})
fig.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7, axis="x")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"): ax.spines[sp].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)

# --- Panel A: agent / comparator claim-Vendi ratios ---
COMPS = [("lisp", "single-topic (lisp)"), ("sci", "broad science (sci)"), ("hn", "broad modern (HN)")]
EMB = [("bge-large-en-v1.5", "bge"), ("all-mpnet-base-v2", "mpnet"), ("gte-large", "gte")]
rows, ylabels = [], []
y = 0
for comp, clab in COMPS:
    for etag, esh in EMB:
        rows.append((y, comp, etag)); ylabels.append((y, esh)); y += 1
    y += 0.9  # group gap
group_mid = {}
for i, (comp, clab) in enumerate(COMPS):
    ys = [r[0] for r in rows if r[1] == comp]
    group_mid[comp] = (min(ys) + max(ys)) / 2

rat = d["vendi_claim_ratios_agent_over_X"]
for yy, comp, etag in rows:
    for norm, col, off in (("qwen", C_QWEN, -0.16), ("gemma", C_GEMMA, 0.16)):
        med, lo, hi = rat[etag][norm][comp]
        ax1.plot([lo, hi], [yy + off] * 2, color=col, lw=1.6, alpha=.55, solid_capstyle="round")
        ax1.plot(med, yy + off, "o", color=col, ms=5.5, zorder=3)
ax1.axvline(1.0, color=INK, lw=1.0, ls=(0, (4, 3)))
ax1.annotate("parity", xy=(1.005, 0.02), xycoords=("data", "axes fraction"),
             color=INK, fontsize=8.5, ha="left")
ax1.set_yticks([yy for yy, _ in ylabels]); ax1.set_yticklabels([e for _, e in ylabels], fontsize=8.5, color=MUTED)
for comp, clab in COMPS:
    ys = [r[0] for r in rows if r[1] == comp]
    ax1.text(0.44, min(ys) - 0.78, clab, color=INK, fontsize=9.5, ha="left", va="center", fontweight="bold")
ax1.invert_yaxis()
ax1.set_xlim(0.42, 1.45)
ax1.set_xlabel("idea-level diversity ratio: agent / comparator  (claim-normalized Vendi, matched m=2,268)",
               color=MUTED, fontsize=9)
ax1.set_title("A · The agent square vs each human anchor — above single-topic, below broad",
              loc="left", color=INK, fontsize=10.5)

# --- Panel B: zstd novelty positions ---
POOLS = [("lisp", "lisp"), ("agent", "agent"), ("sci", "sci"), ("hn", "HN")]
z = d["zstd_matched2836"]
for i, (k, lab) in enumerate(POOLS):
    ax2.plot(z["raw"][k], i, "s", color=C_RAW, ms=6, zorder=3)
    ax2.plot(z["claims_qwen"][k], i, "o", color=C_QWEN, ms=6, zorder=3)
    ax2.plot(z["claims_gemma"][k], i, "o", color=C_GEMMA, ms=6, zorder=3)
    ax2.plot([min(z["claims_qwen"][k], z["claims_gemma"][k]), z["raw"][k]], [i] * 2,
             color=BASE, lw=1.0, zorder=1)
ax2.set_yticks(range(len(POOLS))); ax2.set_yticklabels([lab for _, lab in POOLS], fontsize=9.5, color=INK)
ax2.invert_yaxis()
ax2.set_xlabel("zstd conditional novelty (matched N=2,836; lower = more recycling)", color=MUTED, fontsize=9)
ax2.set_title("B · Verbatim vs idea recycling", loc="left", color=INK, fontsize=10.5)

handles = [plt.Line2D([], [], marker="o", ls="", color=C_QWEN, label="claims · Qwen2.5-7B"),
           plt.Line2D([], [], marker="o", ls="", color=C_GEMMA, label="claims · Gemma-3-12B"),
           plt.Line2D([], [], marker="s", ls="", color=C_RAW, label="raw text (B only)")]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=9,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Novelty bands: the agent square inside the human specialization range",
             x=0.01, ha="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0.045, 1, 0.94))
for ext in ("png", "svg"):
    fig.savefig(R / f"figure.{ext}", facecolor=SURFACE, bbox_inches="tight")
print("saved", R / "figure.png")
