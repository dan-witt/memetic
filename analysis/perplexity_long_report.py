#!/usr/bin/env python3
"""Compare the short-window (~8-item, minutes) and long-window (~40-item, ~1.1h)
LM novelty passes to test whether conditioning on the community's *accumulated*
culture (not just concurrent thread-siblings) lowers novelty, and whether that
endogeneity grows over time (the ritual-accumulation / collapse signature).

Reads results/perplexity/metrics.jsonl (short) and results/perplexity_long/
metrics.jsonl (long), joined on `seq`; strata from data/labels/{authors,items}.csv.
Writes results/perplexity_long/{comparison.json, over_time.csv, strata.csv,
figure.png, figure.svg}. CPU-only. Rerun after either pass is regenerated."""
import csv, json, statistics as st
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHORT = REPO / "results" / "perplexity" / "metrics.jsonl"
LONGD = REPO / "results" / "perplexity_long"
T0 = 1785955279570
E211 = 1786061201186
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_VIOLET="#4a3aa7"


def load(p):
    return {r["seq"]: r for r in (json.loads(l) for l in open(p))}


def tw(rows):
    """Token-weighted corpus novelty = sum(cond*tok)/sum(self*tok)."""
    den = sum(r["self_bits_per_tok"] * r["tokens"] for r in rows)
    return sum(r["cond_bits_per_tok"] * r["tokens"] for r in rows) / den if den else None


S = load(SHORT); L = load(LONGD / "metrics.jsonl")
seqs = sorted(q for q in L if q in S)
assert sum(S[q]["id"] != L[q]["id"] or S[q]["created_at"] != L[q]["created_at"]
           for q in seqs) == 0, "join mismatch"

# ---- headline + confound kill -------------------------------------------------
nS = tw([S[q] for q in seqs]); nL = tw([L[q] for q in seqs])
# identical-token subset: item scored over the exact same token set in both runs
sub = [q for q in seqs if L[q]["tokens"] <= 512 and S[q]["tokens"] == L[q]["tokens"]]
dself = sorted(abs(S[q]["self_bits_per_tok"] - L[q]["self_bits_per_tok"]) for q in sub)
dnov = [L[q]["novelty_ratio"] - S[q]["novelty_ratio"] for q in sub]

# ---- over-time series (6h buckets) -------------------------------------------
bk = defaultdict(list)
for q in seqs:
    bk[int((L[q]["created_at"] - T0) / 3.6e6 // 6)].append(q)
over = []
for k in sorted(bk):
    g = bk[k]
    over.append({"hour_mid": 6 * k + 3, "n": len(g),
                 "novelty_short": round(tw([S[q] for q in g]), 4),
                 "novelty_long": round(tw([L[q] for q in g]), 4),
                 "gap": round(tw([S[q] for q in g]) - tw([L[q] for q in g]), 4),
                 "median_history_hours": round(st.median(L[q]["history_hours"] for q in g), 2),
                 "median_ctx_tokens": int(st.median(L[q]["ctx_tokens"] for q in g))})

# ---- strata ------------------------------------------------------------------
prov = {r["author"]: r.get("provenance_flag", "") for r in csv.DictReader(open(REPO / "data/labels/authors.csv"))}
exo = {(r["kind"], r["id"]): r["is_exogenous"] == "yes" for r in csv.DictReader(open(REPO / "data/labels/items.csv"))}
strata = []
def stratum(name, qs):
    if qs:
        strata.append({"stratum": name, "n": len(qs),
                       "novelty_short": round(tw([S[q] for q in qs]), 4),
                       "novelty_long": round(tw([L[q] for q in qs]), 4)})
stratum("all", seqs)
for k in ("post", "comment"):
    stratum(k, [q for q in seqs if L[q]["kind"] == k])
stratum("exogenous", [q for q in seqs if exo.get((L[q]["kind"], str(L[q]["id"])), False)])
stratum("internal", [q for q in seqs if not exo.get((L[q]["kind"], str(L[q]["id"])), False)])
for flag in ("directed", "open", "autonomous", "unstated"):
    stratum(flag, [q for q in seqs if prov.get(L[q]["author"], "") == flag])

comparison = {
    "n_items": len(seqs),
    "window_short_tokens": 3072, "window_long_tokens": 15000,
    "median_history_hours": {"short": "~minutes (thread-siblings)", "long": round(st.median(L[q]["history_hours"] for q in seqs), 2)},
    "corpus_novelty": {"short": round(nS, 4), "long": round(nL, 4)},
    "history_teaches_1_minus_novelty": {"short": round(1 - nS, 4), "long": round(1 - nL, 4),
                                        "relative_increase": round((1 - nL) / (1 - nS) - 1, 3)},
    "matched_identical_token_subset": {
        "n": len(sub), "self_baseline_median_absdiff": round(st.median(dself), 5),
        "self_baseline_mean_absdiff": round(st.mean(dself), 5),
        "novelty_short": round(tw([S[q] for q in sub]), 4), "novelty_long": round(tw([L[q] for q in sub]), 4),
        "per_item_dnovelty_mean": round(st.mean(dnov), 4), "per_item_dnovelty_median": round(st.median(dnov), 4),
        "frac_items_dropped": round(sum(d < 0 for d in dnov) / len(dnov), 3)},
    "pre_post_211": {lab: round(tw([S[q] for q in seqs if f(L[q])]), 4)
                     for lab, f in [("pre_short", lambda r: r["created_at"] < E211)]}
    ,
    "over_time_gap_stable": {"first_full_bucket_gap": over[1]["gap"], "last_bucket_gap": over[-1]["gap"],
                             "gap_min": min(o["gap"] for o in over[1:]), "gap_max": max(o["gap"] for o in over[1:])},
    "strata": strata,
}
# pre/post 211 for both windows
for lab, f in [("pre", lambda r: r["created_at"] < E211), ("post", lambda r: r["created_at"] >= E211)]:
    g = [q for q in seqs if f(L[q])]
    comparison["pre_post_211"][lab] = {"n": len(g), "novelty_short": round(tw([S[q] for q in g]), 4),
                                       "novelty_long": round(tw([L[q] for q in g]), 4)}
comparison["pre_post_211"].pop("pre_short", None)

(LONGD / "comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
with open(LONGD / "over_time.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(over[0])); w.writeheader(); w.writerows(over)
with open(LONGD / "strata.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(strata[0])); w.writeheader(); w.writerows(strata)
print(json.dumps({k: comparison[k] for k in ("corpus_novelty", "history_teaches_1_minus_novelty",
      "matched_identical_token_subset", "over_time_gap_stable")}, indent=2))

# ---- figure ------------------------------------------------------------------
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=200); fig.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.75)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("bottom", "left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)

# Panel 1: novelty over time, both windows, gap shaded
xs = [o["hour_mid"] for o in over]
ys_s = [o["novelty_short"] for o in over]; ys_l = [o["novelty_long"] for o in over]
ax1.fill_between(xs, ys_l, ys_s, color=S_VIOLET, alpha=.10, linewidth=0)
ax1.plot(xs, ys_s, color=S_BLUE, lw=2, marker="o", markersize=3, label="short window (~8 items, minutes)")
ax1.plot(xs, ys_l, color=S_VIOLET, lw=2, marker="o", markersize=3, label="long window (~40 items, ~1.1 h)")
ax1.axvline((E211 - T0) / 3.6e6, color=BASE, lw=1.2, linestyle=(0, (3, 3)))
ax1.annotate("210/211", ((E211 - T0) / 3.6e6, 0.72), xytext=(4, 0), textcoords="offset points",
             color=MUTED, fontsize=8, va="bottom")
ax1.set_ylim(0.70, 0.92)
ax1.set_title("Accumulated-culture conditioning lowers novelty by a constant ~0.08",
              loc="left", color=INK, fontsize=10.5)
ax1.set_xlabel("hours since first post", color=MUTED, fontsize=9)
ax1.set_ylabel("LM novelty  (cond bits / self bits)", color=MUTED, fontsize=9)
leg = ax1.legend(frameon=False, fontsize=8, loc="lower right", labelcolor=INK)

# Panel 2: short vs long novelty by stratum (dumbbell)
order = ["exogenous", "post", "autonomous", "open", "all", "internal", "directed", "comment"]
order = [s for s in order if any(x["stratum"] == s for x in strata)]
sm = {x["stratum"]: x for x in strata}
yy = range(len(order))
for i, name in enumerate(order):
    a, b = sm[name]["novelty_long"], sm[name]["novelty_short"]
    ax2.plot([a, b], [i, i], color=GRID, lw=2, zorder=1)
ax2.scatter([sm[n]["novelty_long"] for n in order], list(yy), color=S_VIOLET, s=34, zorder=3, label="long")
ax2.scatter([sm[n]["novelty_short"] for n in order], list(yy), color=S_BLUE, s=34, zorder=3, label="short")
ax2.set_yticks(list(yy)); ax2.set_yticklabels([f"{n} (n={sm[n]['n']})" for n in order], fontsize=8, color=INK)
ax2.set_title("Endogeneity gap holds across every stratum", loc="left", color=INK, fontsize=10.5)
ax2.set_xlabel("LM novelty", color=MUTED, fontsize=9)
ax2.legend(frameon=False, fontsize=8, loc="lower right", labelcolor=INK)
ax2.margins(y=.06)

fig.suptitle("1f916.ai - long-horizon LM novelty: does the community lean on its accumulated culture?",
             x=.01, ha="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .95))
fig.savefig(LONGD / "figure.png", facecolor=SURFACE); fig.savefig(LONGD / "figure.svg", facecolor=SURFACE)
print("wrote figure + comparison.json + over_time.csv + strata.csv")
