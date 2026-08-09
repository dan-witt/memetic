#!/usr/bin/env python3
"""The exogenous-content influx after posts 210/211: is the shift toward
importing outside material adopted across the community, and across model
families? Reads data/labels/items.csv (is_exogenous from the disclosure pass);
writes results/exogenous_influx/{figure.png,svg,stats.json}. CPU-only."""
import csv, json, time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "exogenous_influx"; OUT.mkdir(parents=True, exist_ok=True)
T0=1785955279570; E211=1786061201186
MIDS={"Aug6":1785974400000,"Aug7 (210/211)":1786060800000,"Aug8":1786147200000}
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"
h=lambda ms:(ms-T0)/3.6e6

def modfam(m):
    m=(m or "unknown").lower()
    for s in ("claude-opus","claude-fable","claude-sonnet","claude-haiku","claude-mythos",
              "deepseek","grok","gemini","kimi","mimo","qwen","gpt","llama","mistral","glm",
              "minimax","codex","cursor"):
        if s in m: return s.replace("claude-","")
    return m.split("/")[-1][:12]

rows=list(csv.DictReader((REPO/"data/labels/items.csv").open()))
for r in rows: r["ts"]=int(r["created_at"]); r["exo"]=r["is_exogenous"]=="yes"
rows.sort(key=lambda r:r["ts"])
post=[r for r in rows if r["ts"]>=E211 and r["exo"]]
fam=Counter(modfam(r["author_model"]) for r in post)
famauth=defaultdict(set)
for r in post: famauth[modfam(r["author_model"])].add(r["author"])

def share(lo,hi):
    seg=[r for r in rows if lo<=r["ts"]<hi]; e=sum(r["exo"] for r in seg)
    return (e,len(seg),e/len(seg) if seg else 0)
W=12*3.6e6
stats={
    "post211_exo_items":len(post),"post211_exo_authors":len({r['author'] for r in post}),
    "model_families":len(fam),
    "intervening_agent_share":round(sum(r['author'] in ('peppercorn','small-archive') for r in post)/len(post),3),
    "exo_share_before_211":round(share(E211-1e18,E211)[2],4),
    "exo_share_after_211":round(share(E211,E211+1e18)[2],4),
    "midnight_jumps_12h":{name:{"before":round(share(m-W,m)[2],3),"after":round(share(m,m+W)[2],3),
                                "jump":round(share(m,m+W)[2]-share(m-W,m)[2],3)} for name,m in MIDS.items()},
    "by_model_family":{k:{"items":v,"authors":len(famauth[k])} for k,v in fam.most_common()},
}
(OUT/"stats.json").write_text(json.dumps(stats,indent=2)+"\n")
print(json.dumps({k:stats[k] for k in ("post211_exo_items","post211_exo_authors","model_families",
      "intervening_agent_share","midnight_jumps_12h")},indent=2))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
b=defaultdict(lambda:[0,0])
for r in rows: k=int(h(r["ts"])//6); b[k][0]+=1; b[k][1]+=r["exo"]
xs=[6*k+3 for k in sorted(b)]; ys=[b[k][1]/b[k][0] for k in sorted(b)]
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.4),dpi=200); fig.set_facecolor(SURFACE)
for ax in (ax1,ax2):
    ax.set_facecolor(SURFACE); ax.grid(True,axis="both",color=GRID,linewidth=.7)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("bottom","left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED,labelsize=9)
ax1.plot(xs,ys,color=S_BLUE,lw=2,marker="o",markersize=3)
for name,m in MIDS.items():
    lit = "210/211" in name
    ax1.axvline(h(m),color=(BASE if lit else GRID),lw=(1.4 if lit else 1),
                linestyle=(0,(3,3)) if lit else (0,(1,2)))
ax1.annotate("210/211\n(go outward)",(h(E211),max(ys)*.9),xytext=(4,0),
             textcoords="offset points",color=MUTED,fontsize=8,va="top")
ax1.set_title("Exogenous-content share doubles after 210/211",loc="left",color=INK,fontsize=10.5)
ax1.set_xlabel("hours since first post",color=MUTED,fontsize=9); ax1.set_ylabel("share of items importing outside material",color=MUTED,fontsize=9)
items=list(fam.most_common()); labs=[k for k,_ in items][::-1]; vals=[v for _,v in items][::-1]
ax2.barh(range(len(labs)),vals,color=S_ORANGE,height=.72)
ax2.set_yticks(range(len(labs))); ax2.set_yticklabels(labs,fontsize=8,color=INK)
ax2.set_title(f"Adopted across {len(fam)} model families ({stats['post211_exo_authors']} authors)",loc="left",color=INK,fontsize=10.5)
ax2.set_xlabel("post-211 exogenous items",color=MUTED,fontsize=9)
fig.suptitle("1f916.ai - the outward turn: cross-population adoption of importing outside material",
             x=.01,ha="left",color=INK,fontsize=12,fontweight="bold")
fig.tight_layout(rect=(0,0,1,.95))
fig.savefig(OUT/"figure.png",facecolor=SURFACE); fig.savefig(OUT/"figure.svg",facecolor=SURFACE)
print("wrote figure")
