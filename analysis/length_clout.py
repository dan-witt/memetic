#!/usr/bin/env python3
"""The length mechanism behind the karma-decoupling result: are votes a length
proxy while computational clout is not? Reads results/ablation/clout.jsonl (votes
+ clout per post) and the raw corpus (words per post); writes results/ablation/
{length.json, length_figure.png/svg}. CPU-only, no deps beyond matplotlib.

Prompted by 1f916.ai comment 2389 (weights-and-measures, opus-5), which
independently found rho(words, votes)=0.510 on a separate walk and used it to
retract a published "Anthropic models hold 63.8% of karma" claim (stratified
permutation put it on the null, p=0.83 -- the effect was author count x median
length). This pass adds the missing column: rho(words, clout)."""
import json, math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "ablation"
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_VIOLET="#4a3aa7"


def _ranks(v):
    n = len(v); order = sorted(range(n), key=lambda i: v[i]); r = [0.0] * n; i = 0
    while i < n:  # average ties
        j = i
        while j + 1 < n and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def _pearson(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return cov / (sa * sb) if sa and sb else float("nan")


def spearman(x, y):
    return _pearson(_ranks(x), _ranks(y))


def partial_spearman(x, y, z):
    """Spearman(x, y | z): correlation of rank-residuals after removing rank-z."""
    rx, ry, rz = _ranks(x), _ranks(y), _ranks(z); n = len(x); mz = sum(rz) / n
    dz = sum((zi - mz) ** 2 for zi in rz)

    def resid(r):
        mr = sum(r) / n
        beta = sum((ri - mr) * (zi - mz) for ri, zi in zip(r, rz)) / dz
        a0 = mr - beta * mz
        return [ri - (a0 + beta * zi) for ri, zi in zip(r, rz)]

    return _pearson(resid(rx), resid(ry))


def main():
    words = {}
    for f in (REPO / "data" / "posts").glob("*.json"):
        p = json.load(f.open())["post"]
        words[p["id"]] = len(((p.get("title") or "") + " " + (p.get("body") or "")).split())

    rows = [json.loads(l) for l in (OUT / "clout.jsonl").open()]
    rows = [r for r in rows if r["post_id"] in words]
    W = [words[r["post_id"]] for r in rows]
    V = [r["votes"] for r in rows]
    C60 = [r["clout_sum_60"] for r in rows]
    C30 = [r["clout_sum_30"] for r in rows]

    res = {
        "n_posts": len(rows),
        "rho_words_votes": round(spearman(W, V), 3),
        "rho_words_clout60": round(spearman(W, C60), 3),
        "rho_words_clout30": round(spearman(W, C30), 3),
        "rho_votes_clout60": round(spearman(V, C60), 3),
        "rho_votes_clout60_given_words": round(partial_spearman(V, C60, W), 3),
        "length_loading_ratio_votes_over_clout": round(spearman(W, V) / spearman(W, C60), 2),
        "external_replication_comment_2389": {
            "author": "weights-and-measures (claude-opus-5)", "thread": 365,
            "rho_words_votes": 0.510, "n_posts": 375,
            "retracted_claim": "Anthropic-family models hold 63.8% of karma",
            "stratified_permutation": {"anthropic_percentile": 0.496, "p": 0.83,
                                       "note": "on the null; effect = author count x median length"},
        },
    }
    (OUT / "length.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))

    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    labels = ["words ↔ votes", "words ↔ clout", "votes ↔ clout",
              "votes ↔ clout\n(length removed)"]
    vals = [res["rho_words_votes"], res["rho_words_clout60"],
            res["rho_votes_clout60"], res["rho_votes_clout60_given_words"]]
    cols = [S_ORANGE, S_VIOLET, S_BLUE, BASE]
    fig, ax = plt.subplots(figsize=(7.6, 4.0), dpi=200); fig.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE); ax.grid(True, axis="x", color=GRID, linewidth=.75)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("bottom", "left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)
    y = list(range(len(labels)))[::-1]
    ax.barh(y, vals, color=cols, height=.66)
    for yi, v in zip(y, vals):
        ax.annotate(f"{v:+.3f}", (v, yi), xytext=(4, 0), textcoords="offset points",
                    va="center", color=INK, fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9, color=INK)
    ax.set_xlim(0, 0.62); ax.set_xlabel("Spearman rho", color=MUTED, fontsize=9)
    ax.set_title(f"Votes track length {res['length_loading_ratio_votes_over_clout']}× harder than "
                 f"influence does  (n={res['n_posts']} posts)", loc="left", color=INK, fontsize=10.5)
    fig.suptitle("1f916.ai - the length mechanism behind karma-decoupling",
                 x=.01, ha="left", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig(OUT / "length_figure.png", facecolor=SURFACE)
    fig.savefig(OUT / "length_figure.svg", facecolor=SURFACE)
    print("wrote length.json + length_figure.{png,svg}")


if __name__ == "__main__":
    main()
