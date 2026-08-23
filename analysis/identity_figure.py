#!/usr/bin/env python3
"""Figure for results/identity: (A) how much dispersion the reported model explains vs the author
beyond it, as EXCESS over the exchangeability permutation null, per view x embedder; (B) the 21
model-switchers -- is a citizen nearer itself on other weights than its model-mates?; (C) held-out
identification of author vs model on each citizen's chronologically second half.
Reads results/identity/results.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = Path(__file__).resolve().parent.parent / "results/identity"
d = json.load(open(R / "results.json"))["views"]

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; MUTED = "#898781"; GRID = "#e1e0d9"; BASE = "#c3c2b7"
C_AUTH = "#2a78d6"; C_MODEL = "#eb6834"; C_IDEA = "#7a9e3a"

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 5.4), dpi=200,
                                    gridspec_kw={"width_ratios": [1.25, 1.05, 1]})
fig.set_facecolor(SURFACE)
for ax in (ax1, ax2, ax3):
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7, axis="x")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("bottom", "left"): ax.spines[sp].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)

# ---- Panel A: excess dispersion explained, model vs author|model -------------------------
VIEWS = [("lexical", "as written · all"), ("lexical_matched", "as written · matched"),
         ("claim_qwen", "claims · Qwen"), ("claim_gemma", "claims · Gemma")]
EMB = [("bge", "bge"), ("gte", "gte")]
rows, ylab, y = [], [], 0
for v, vlab in VIEWS:
    for e, elab in EMB:
        k = f"{v}/{e}"
        if k in d: rows.append((y, k, v)); ylab.append((y, f"{vlab} · {elab}")); y += 1
    y += 0.5
for yy, k, v in rows:
    for key, col, off, ls in (("headline", C_MODEL, -0.17, "eta2_model"),
                              ("headline", C_AUTH, 0.17, "eta2_author")):
        h = d[k][key]
        obs, null = h[ls], h[ls.replace("eta2_", "") + "_null_mean"]
        ax1.plot([0, obs - null], [yy + off] * 2, color=col, lw=3.2, alpha=.85,
                 solid_capstyle="butt", zorder=2)
        ax1.plot(obs - null, yy + off, "o", color=col, ms=6, zorder=3)
    # length-residualized model effect, as a hollow marker
    h2 = d[k].get("headline_lenresid")
    if h2:
        ax1.plot(h2["eta2_model"] - h2["model_null_mean"], yy - 0.17, "o", mfc=SURFACE,
                 mec=C_MODEL, ms=6, mew=1.4, zorder=4)
        ax1.plot(h2["eta2_author"] - h2["author_null_mean"], yy + 0.17, "o", mfc=SURFACE,
                 mec=C_AUTH, ms=6, mew=1.4, zorder=4)
ax1.axvline(0, color=INK, lw=1.0)
ax1.set_yticks([yy for yy, _ in ylab])
ax1.set_yticklabels([e for _, e in ylab], fontsize=8.5, color=INK)
ax1.invert_yaxis()
ax1.set_xlabel("excess dispersion explained over the permutation null  (DISCO $\\eta^2$)",
               color=MUTED, fontsize=9)
ax1.set_title("A · Who explains the voice — reported model, or the author beyond it",
              loc="left", color=INK, fontsize=10.5)
h = [plt.Line2D([], [], marker="o", ls="", color=C_MODEL, label="reported model"),
     plt.Line2D([], [], marker="o", ls="", color=C_AUTH, label="author, within model"),
     plt.Line2D([], [], marker="o", ls="", mfc=SURFACE, mec=INK, mew=1.4, label="length-residualized")]
ax1.legend(handles=h, loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK)

# ---- Panel B: switchers ------------------------------------------------------------------
sw = d["lexical/bge"]["switchers"]["rows"]
swc = {r["author"]: r for r in d.get("claim_qwen/bge", {}).get("switchers", {}).get("rows", [])}
swm = {r["author"]: r for r in d.get("lexical_matched/bge", {}).get("switchers", {}).get("rows", [])}
sw = sorted(sw, key=lambda r: r["ratio"] or 0)
yy = np.arange(len(sw))
for i, r in enumerate(sw):
    ax2.plot([1, r["ratio"]], [i, i], color=BASE, lw=1.2, zorder=1)
    ax2.plot(r["ratio"], i, "o", color=C_AUTH, ms=7, zorder=3)
    m = swm.get(r["author"])
    if m and m["ratio"]: ax2.plot(m["ratio"], i, "o", mfc=SURFACE, mec=C_AUTH, mew=1.5, ms=6, zorder=3)
    c = swc.get(r["author"])
    if c and c["ratio"]: ax2.plot(c["ratio"], i, "D", color=C_IDEA, ms=5, zorder=3)
ax2.axvline(1.0, color=INK, lw=1.0, ls=(0, (4, 3)))
ax2.annotate("parity", xy=(0.99, 0.985), xycoords=("data", "axes fraction"), color=INK,
             fontsize=8.5, ha="right", va="top")
ax2.set_yticks(yy)
ax2.set_yticklabels([f"{r['author']}\n{r['model_a']} ↔ {r['model_b']}" for r in sw],
                    fontsize=7.5, color=INK)
ax2.set_xlim(0.55, max(r["ratio"] for r in sw) * 1.12)
ax2.set_xlabel("energy distance to a model-mate ÷ distance to itself on other weights",
               color=MUTED, fontsize=9)
ax2.set_title("B · Citizens who changed model — the within-subject test",
              loc="left", color=INK, fontsize=10.5)
h = [plt.Line2D([], [], marker="o", ls="", color=C_AUTH, label="as written · all items"),
     plt.Line2D([], [], marker="o", ls="", mfc=SURFACE, mec=C_AUTH, mew=1.5,
                label="as written · claim window"),
     plt.Line2D([], [], marker="D", ls="", color=C_IDEA, label="claim-normalized")]
ax2.legend(handles=h, loc="center right", frameon=False, fontsize=8.5, labelcolor=INK)

# ---- Panel C: identification -------------------------------------------------------------
# The two tasks do NOT share a chance convention -- author rows are adjusted against UNIFORM
# chance, the model row against the MAJORITY class -- so the bar lengths are not comparable across
# colours. Issue-#10's cold review caught the report making exactly that comparison; the labels
# now carry the baseline so the panel cannot be read that way.
BARS = [("author_acc_adj", "name the author\n(of all citizens)\nvs uniform 1/63", C_AUTH),
        ("author_within_model_adj", "name the author\n(model given)\nvs uniform within family", C_AUTH),
        ("model_acc_adj", "name the reported model\nvs MAJORITY class 0.23\n(vs uniform 1/20: 0.34)", C_MODEL)]
sets = [("lexical_matched/bge", "as written", 0), ("claim_qwen/bge", "claim-normalized", 1)]
w = 0.36
for j, (k, lab, off) in enumerate(sets):
    v = d.get(k, {}).get("identify")
    if not v: continue
    vals = [v[b] for b, _, _ in BARS]
    ax3.barh(np.arange(len(BARS)) + (off - 0.5) * w, vals, height=w * 0.92,
             color=[c for _, _, c in BARS], alpha=1.0 if off == 0 else 0.42,
             edgecolor="none", zorder=2)
    for i, val in enumerate(vals):
        ax3.text(val + (0.007 if val >= 0 else -0.007), i + (off - 0.5) * w, f"{val:.2f}",
                 va="center", ha="left" if val >= 0 else "right", fontsize=7.8,
                 color=INK if off == 0 else MUTED)
ax3.axvline(0, color=INK, lw=1.0)
ax3.set_yticks(range(len(BARS))); ax3.set_yticklabels([l for _, l, _ in BARS], fontsize=8.5, color=INK)
ax3.invert_yaxis()
ax3.set_xlabel("chance-adjusted accuracy, held-out second halves\n"
               "baselines differ by row — compare each row to itself",
               color=MUTED, fontsize=8.5, linespacing=1.5)
ax3.set_title("C · Identification, same 9,217 items — solid as written, faded claim-normalized",
              loc="left", color=INK, fontsize=10.5)

fig.suptitle("Is identity real? Model, harness, and author in an agent society",
             x=0.005, ha="left", color=INK, fontsize=12.5, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
for ext in ("png", "svg"):
    fig.savefig(R / f"figure.{ext}", facecolor=SURFACE, bbox_inches="tight")
print(f"saved {R}/figure.png|svg")
