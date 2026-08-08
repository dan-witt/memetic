#!/usr/bin/env python3
"""Figure + stats for the LM token-loss pass: endogeneity curve over time,
LM-vs-zstd agreement, ritual mass, and tenure/provenance cuts.
Reads results/perplexity/metrics.jsonl (+ zstd metrics + labels); writes
results/perplexity/figure.{png,svg} and strata.json. Uses .venv (matplotlib)."""
import csv, json, math, time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "perplexity"
T0 = 1785955279570
WFULL = 1786013100000
EVENT = 1786061073591

SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_AQUA="#1baf7a"; S_VIOLET="#4a3aa7"

ppl=[json.loads(l) for l in (OUT/"metrics.jsonl").open()]
ppl.sort(key=lambda r:r["seq"])
z={(r["kind"],r["id"]):r for r in (json.loads(l) for l in (REPO/"results/zstd_curve/metrics.jsonl").open())}
labels={}
lp=REPO/"data/labels/authors.csv"
if lp.exists():
    for r in csv.DictReader(lp.open()):
        if r.get("provenance_flag"): labels[r["author"]]=r["provenance_flag"]
tenure=Counter()
for r in ppl:
    tenure[r["author"]]+=1; r["item_tenure"]=tenure[r["author"]]
h=lambda ms:(ms-T0)/3.6e6

def roll(rows,key,w=100):
    out=[]
    for i in range(w-1,len(rows)):
        seg=rows[i-w+1:i+1]
        out.append((rows[i]["created_at"], sum(x[key] for x in seg)/len(seg)))
    return out
def roll_ratio(rows,num,den,w=100):
    out=[]
    for i in range(w-1,len(rows)):
        seg=rows[i-w+1:i+1]
        out.append((rows[i]["created_at"], sum(x[num] for x in seg)/sum(x[den] for x in seg)))
    return out

# align zstd novelty onto ppl order
for r in ppl:
    zr=z.get((r["kind"],r["id"])); r["zstd_novelty"]=zr["novelty_ratio"] if zr else None
ss=[r for r in ppl if r["created_at"]>=WFULL]
def agg_nov(rows): return sum(r["cond_bits_per_tok"]*r["tokens"] for r in rows)/sum(r["self_bits_per_tok"]*r["tokens"] for r in rows)

result={"model":json.loads((OUT/"run.json").read_text())["model"],
        "steady_state_items":len(ss),
        "lm_novelty_ss":round(agg_nov(ss),4),
        "lm_ritual_mass_ss":round(sum(r["low_info_frac"] for r in ss)/len(ss),4)}
# tenure
result["lm_novelty_by_tenure"]={}
for lo,hi,lab in [(1,1,"1"),(2,2,"2"),(3,5,"3-5"),(6,10,"6-10"),(11,10**9,"11+")]:
    seg=[r for r in ss if lo<=r["item_tenure"]<=hi]
    if seg: result["lm_novelty_by_tenure"][lab]={"n":len(seg),"novelty":round(agg_nov(seg),4)}
# provenance
result["lm_novelty_by_provenance"]={}
for fl in ("directed","open","autonomous","unstated"):
    seg=[r for r in ss if labels.get(r["author"])==fl]
    if seg: result["lm_novelty_by_provenance"][fl]={"n":len(seg),"novelty":round(agg_nov(seg),4)}
# posts vs comments
for kind in ("post","comment"):
    seg=[r for r in ss if r["kind"]==kind]
    result[f"lm_novelty_{kind}s"]=round(agg_nov(seg),4)
(OUT/"strata.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,7.2),sharex=True,dpi=200)
fig.set_facecolor(SURFACE)
for ax in (ax1,ax2):
    ax.set_facecolor(SURFACE); ax.grid(True,axis="y",color=GRID,linewidth=.75)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("bottom","left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED,labelsize=9)
hrs=lambda pts:[h(t) for t,_ in pts]; val=lambda pts:[v for _,v in pts]
p=roll(ppl,"self_bits_per_char"); ax1.plot(hrs(p),val(p),color=S_BLUE,lw=2,label="LM standalone")
p=roll(ppl,"cond_bits_per_char"); ax1.plot(hrs(p),val(p),color=S_ORANGE,lw=2,label="LM conditioned")
ax1.set_title("LM per-character information: standalone vs. conditioned on forum history",loc="left",color=INK,fontsize=11)
ax1.set_ylabel("bits / char (rolling 100)",color=MUTED,fontsize=9)
ax1.legend(frameon=False,fontsize=8.5,loc="upper right",labelcolor=INK)
p=roll_ratio(ppl,"cond_bits_per_tok","self_bits_per_tok"); ax2.plot(hrs(p),val(p),color=S_VIOLET,lw=2,label="LM novelty (paraphrase-sensitive)")
zpts=[(r["created_at"],r["zstd_novelty"]) for r in ppl if r["zstd_novelty"] is not None]
zr=[]
for i in range(99,len(zpts)):
    seg=zpts[i-99:i+1]; zr.append((seg[-1][0],sum(v for _,v in seg)/len(seg)))
ax2.plot(hrs(zr),val(zr),color=MUTED,lw=1.5,linestyle=(0,(4,3)),label="zstd novelty (verbatim-only)")
ax2.set_title("Novelty ratio: LM vs. zstd — both flat-to-rising (not collapsing)",loc="left",color=INK,fontsize=11)
ax2.set_ylabel("cond / self",color=MUTED,fontsize=9); ax2.set_xlabel("hours since first post",color=MUTED,fontsize=9)
ax2.legend(frameon=False,fontsize=8.5,loc="upper right",labelcolor=INK)
fillh=h(WFULL)
for ax in (ax1,ax2):
    ax.axvspan(ax.get_xlim()[0],fillh,color=GRID,alpha=.45,zorder=0)
    ax.axvline(h(EVENT),color=BASE,lw=1,linestyle=(0,(3,3)))
fig.suptitle("1f916.ai - endogeneity under a language model (Qwen2.5-7B)",x=.01,ha="left",color=INK,fontsize=13,fontweight="bold")
fig.tight_layout(rect=(0,0,1,.96))
fig.savefig(OUT/"figure.png",facecolor=SURFACE); fig.savefig(OUT/"figure.svg",facecolor=SURFACE)
print("wrote figure")
