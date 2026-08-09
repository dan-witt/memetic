#!/usr/bin/env python3
"""The second channel behind karma-decoupling: quotability vs agenda-setting.

Finding 2 (ablation) plus its length addendum leave a residue length can't
explain -- short, high-vote, low-clout posts (p32, p88). Comment 2389/peppercorn's
proposal: those are *quotable* -- their phrases get repeated verbatim downstream
even though they don't lower downstream loss (low clout). This pass measures that
directly, with no GPU and no new classifier, reusing the glossary's shingle
machinery from zstd_curve.py.

Per-post quotability = how many *later, different* authors reuse an 8-word phrase
that this post ORIGINATED (first corpus occurrence is this post). Originated-only
so that reciting a shared governance ritual doesn't read as being quoted. We then
ask whether the vote-residual-after-length (popularity length doesn't explain) is
carried by quotability (echo) or by influence (clout).

Reads data/posts/*.json + results/ablation/clout.jsonl; writes results/ablation/
{quotability.json, quotability_figure.png/svg}. CPU-only."""
import json
from pathlib import Path
from collections import defaultdict

from length_clout import spearman, partial_spearman, _ranks  # reuse rank stats

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "results" / "ablation"
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_VIOLET="#4a3aa7"


def shingles(text):
    w = text.split()
    return {" ".join(w[i:i + 8]) for i in range(len(w) - 7)}  # 8-word, matches glossary


def vote_residual(votes, words):
    """rank(votes) minus its linear fit on rank(words): popularity length can't explain."""
    rv, rw = _ranks(votes), _ranks(words); n = len(votes)
    mw = sum(rw) / n; dv = sum((w - mw) ** 2 for w in rw)
    mv = sum(rv) / n
    beta = sum((v - mv) * (w - mw) for v, w in zip(rv, rw)) / dv
    a0 = mv - beta * mw
    return [v - (a0 + beta * w) for v, w in zip(rv, rw)]


def main():
    # 1. all items in chronological order (posts + comments), with text
    items = []
    for f in (REPO / "data" / "posts").glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        items.append({"kind": "post", "id": p["id"], "created_at": p["created_at"],
                      "author": p["author"],
                      "text": (p.get("title") or "") + "\n\n" + (p.get("body") or "")})
        for c in th.get("comments", []):
            items.append({"kind": "comment", "id": c["id"], "created_at": c["created_at"],
                          "author": c["author"], "text": c.get("body") or ""})
    items.sort(key=lambda x: (x["created_at"], 0 if x["kind"] == "post" else 1, x["id"]))
    for seq, it in enumerate(items):
        it["seq"] = seq; it["sh"] = shingles(it["text"])

    # 2. occurrences per shingle: seq -> list of (seq, author)
    occ = defaultdict(list)
    for it in items:
        for s in it["sh"]:
            occ[s].append((it["seq"], it["author"]))

    # 3. per-post quotability: distinct later authors reusing a phrase THIS post originated
    quote = {}
    for it in items:
        if it["kind"] != "post":
            continue
        originated = [s for s in it["sh"] if min(o[0] for o in occ[s]) == it["seq"]]
        downstream_authors, reuses = set(), 0
        for s in originated:
            for sq, au in occ[s]:
                if sq > it["seq"] and au != it["author"]:
                    downstream_authors.add(au); reuses += 1
        quote[it["id"]] = {"echo_authors": len(downstream_authors), "echo_reuses": reuses,
                           "n_originated": len(originated), "words": len(it["text"].split())}

    # 4. join clout + votes
    rows = []
    for r in (json.loads(l) for l in (OUT / "clout.jsonl").open()):
        q = quote.get(r["post_id"])
        if q:
            rows.append({**r, **q})
    echo = [r["echo_authors"] for r in rows]
    clout = [r["clout_sum_60"] for r in rows]
    votes = [r["votes"] for r in rows]
    words = [r["words"] for r in rows]
    vres = vote_residual(votes, words)

    res = {
        "n_posts": len(rows),
        "rho_echo_voteResidualAfterLength": round(spearman(echo, vres), 3),
        "rho_clout_voteResidualAfterLength": round(spearman(clout, vres), 3),
        "rho_echo_clout": round(spearman(echo, clout), 3),
        "rho_echo_words": round(spearman(echo, words), 3),
        "rho_echo_voteResidual_given_words": round(partial_spearman(echo, vres, words), 3),
        "rho_echo_votes": round(spearman(echo, votes), 3),
    }
    # locate exemplars
    def pct(vals, target_id, key):
        v = {r["post_id"]: r[key] for r in rows}[target_id]
        return round(sum(x <= v for x in vals) / len(vals), 2), v
    ex = {}
    for pid in (32, 88, 100, 104, 116):
        if any(r["post_id"] == pid for r in rows):
            ep, ev = pct(echo, pid, "echo_authors"); cp, cv = pct(clout, pid, "clout_sum_60")
            vp, vv = pct(votes, pid, "votes")
            ex[f"p{pid}"] = {"echo_authors": ev, "echo_pctile": ep, "clout": round(cv, 2),
                             "clout_pctile": cp, "votes": vv, "votes_pctile": vp}
    res["exemplars"] = ex
    # top quotable and top clout
    res["top_quotable_posts"] = [{"post_id": r["post_id"], "author": r["author"],
                                  "echo_authors": r["echo_authors"], "clout": round(r["clout_sum_60"], 2),
                                  "votes": r["votes"]}
                                 for r in sorted(rows, key=lambda r: -r["echo_authors"])[:8]]
    (OUT / "quotability.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k.startswith("rho") or k == "n_posts"}, indent=2))
    print("exemplars:", json.dumps(ex, indent=2))

    # 5. figure: two influence axes -- clout (build-on) vs echo (quotation)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.8, 5.2), dpi=200); fig.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("bottom", "left"): ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=9)
    import numpy as np
    vr = np.array(vres); sizes = 18 + 120 * (vr - vr.min()) / (vr.max() - vr.min() + 1e-9)
    ax.scatter(clout, echo, s=sizes, color=S_BLUE, alpha=.45, edgecolors="none")
    idc = {r["post_id"]: (r["clout_sum_60"], r["echo_authors"]) for r in rows}
    for pid, tag, col in [(32, "p32", S_ORANGE), (88, "p88", S_ORANGE),
                          (100, "p100", S_VIOLET), (104, "p104", S_VIOLET), (116, "p116", S_VIOLET)]:
        if pid in idc:
            x, y = idc[pid]
            ax.scatter([x], [y], s=70, color=col, edgecolors=SURFACE, linewidths=1.2, zorder=5)
            ax.annotate(tag, (x, y), xytext=(5, 3), textcoords="offset points", color=INK, fontsize=8.5)
    ax.set_xlabel("predictive contribution @60  (downstream loss reduction — 'built on')", color=MUTED, fontsize=9)
    ax.set_ylabel("quotability  (later authors repeating a phrase it coined)", color=MUTED, fontsize=9)
    ax.set_title(f"Two separable influence channels; point size = vote-residual after length\n"
                 f"orange = quotable one-liners, violet = investigative agenda-setters",
                 loc="left", color=INK, fontsize=10)
    fig.suptitle("1f916.ai - quotability vs agenda-setting (n=%d posts)" % len(rows),
                 x=.01, ha="left", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(OUT / "quotability_figure.png", facecolor=SURFACE)
    fig.savefig(OUT / "quotability_figure.svg", facecolor=SURFACE)
    print("wrote quotability.json + quotability_figure.{png,svg}")


if __name__ == "__main__":
    main()
