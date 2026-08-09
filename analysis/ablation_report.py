#!/usr/bin/env python3
"""Figure for the ablation-clout pass: influence decay-vs-distance (the cliff
question) and clout-vs-karma (the decoupling test). Reads results/ablation/*,
writes figure.{png,svg}. Uses .venv (matplotlib)."""
import csv, json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "results" / "ablation"
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_VIOLET="#4a3aa7"

rows=[json.loads(l) for l in (OUT/"clout.jsonl").open()]
dist=list(csv.DictReader((OUT/"distance_curve.csv").open()))
run=json.loads((OUT/"run.json").read_text())
k=[int(r["distance_items"]) for r in dist]; dv=[float(r["mean_delta_bits"]) for r in dist]

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.6),dpi=200)
fig.set_facecolor(SURFACE)
for ax in (ax1,ax2):
    ax.set_facecolor(SURFACE); ax.grid(True,color=GRID,linewidth=.75)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("bottom","left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED,labelsize=9)

# Panel 1: decay curve, log-y
ax1.plot(k,dv,color=S_VIOLET,lw=2,marker="o",markersize=3)
ax1.set_yscale("log")
ax1.axvline(30,color=BASE,lw=1,linestyle=(0,(3,3)))
floor=np.median(dv[34:])
ax1.axhline(floor,color=MUTED,lw=1,linestyle=(0,(1,2)))
ax1.annotate("front page = 30 items\n(no cliff here)",(30,dv[3]),xytext=(4,0),
             textcoords="offset points",color=MUTED,fontsize=8,va="center")
ax1.annotate("noise floor",(52,floor),xytext=(0,4),textcoords="offset points",color=MUTED,fontsize=8)
ax1.set_title("Influence decays smoothly, at floor before distance 30",loc="left",color=INK,fontsize=10.5)
ax1.set_xlabel("distance downstream (items)",color=MUTED,fontsize=9)
ax1.set_ylabel("mean PC Δ (bits/tok, log)",color=MUTED,fontsize=9)

# Panel 2: clout vs votes scatter
v=np.array([r["votes"] for r in rows],float); c=np.array([r["clout_sum_60"] for r in rows])
ax2.scatter(v,c,s=14,color=S_BLUE,alpha=.5,edgecolors="none")
# highlight divergent quadrants
cr=np.argsort(np.argsort(c)); vr=np.argsort(np.argsort(v)); n=len(rows)
hcl=(cr>n*.8)&(vr<n*.5); hvl=(vr>n*.8)&(cr<n*.5)
ax2.scatter(v[hcl],c[hcl],s=20,color=S_ORANGE,edgecolors="none",label="high PC, low votes")
ax2.scatter(v[hvl],c[hvl],s=20,color=MUTED,edgecolors="none",label="high votes, low PC")
sp=run["spearman_votes_clout60"]
ax2.set_title(f"Karma vs. predictive contribution (Spearman {sp:.2f})",loc="left",color=INK,fontsize=10.5)
ax2.set_xlabel("votes (karma)",color=MUTED,fontsize=9); ax2.set_ylabel("PC @60 (Σ bits)",color=MUTED,fontsize=9)
leg=ax2.legend(frameon=False,fontsize=8,loc="upper right",labelcolor=INK)
for h_ in leg.legend_handles: h_.set_sizes([20])

fig.suptitle("1f916.ai - post predictive contribution by ablation (Qwen2.5-7B, 425 posts, horizon 60)",
             x=.01,ha="left",color=INK,fontsize=12,fontweight="bold")
fig.tight_layout(rect=(0,0,1,.95))
fig.savefig(OUT/"figure.png",facecolor=SURFACE); fig.savefig(OUT/"figure.svg",facecolor=SURFACE)
print("wrote figure; floor≈",round(float(floor),4),"delta@1",dv[0])
