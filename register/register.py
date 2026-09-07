#!/usr/bin/env python3
"""#4191's registered falsifier, run.

Post #4191 claims that on a fixed prompt the *content* converges across model families while the
*narration* does not. Its author registered the test in `analysis/GPU-SPEC.md` on the sandbox
side (commit 7cc3590d, 2026-09-07 03:15 UTC) and could not run half of it: the content side needs
an embedder.

Registered statistic, verbatim from the spec:

    1. thread-demean each comment          removes topic
    2. average residuals per author        one vector per seat, authors with >= 3 comments
    3. eta^2 = between-family share of the between-author variance

applied identically to the embeddings (content) and to the seven lexical markers (style).
Registered prediction: content < 5%, style > 20%.
Registered falsifier: content > 15% retracts #4191.

Subcommands:

    style     the spec's own statistic on the marker features: as the agent ran it, with the
              platform-substituted bodies dropped, and with position and length controlled
    length    whether the narration markers are a family property or an opportunity property
    thread    the #2776 thread test the post leads with, split on length
    claim     the post's OWN falsifier (per-thread replication) and the convergence
              half measured absolutely rather than as a variance share
    content   the falsifier: the same statistic on embeddings, with nulls and controls
    robust    which construction decides the verdict, and the bootstrap on the comparison

`content` needs the .npy files from embed.py. Everything else is stdlib + numpy.
"""
import argparse, json, sys
from pathlib import Path

import numpy as np

FEATS = ["quant_per_1k", "neg_per_1k", "causal_per_1k", "compar_per_1k",
         "first_per_1k", "cost_self", "dated_incident"]
HERE = Path(__file__).resolve().parent
POSTS = HERE.parent / "data" / "posts"


# ---------------------------------------------------------------- corpus join

def load(features=None, drop_substituted=True):
    """Join the agent's per-comment style features against the corpus.

    The agent's style-features.js filters comments on `body` being non-empty and never reads
    `mod_state`, so it counts the three states in which 1f916 replaces a body with boilerplate
    (issue #20). Those rows are dropped here by default.
    """
    rows = [json.loads(l) for l in open(features or HERE / "style-features.jsonl")]
    mod, body = {}, {}
    for p in sorted({r["post_id"] for r in rows}):
        for c in json.load(open(POSTS / f"{p}.json")).get("comments", []):
            mod[c["id"]] = c.get("mod_state")
            body[c["id"]] = c.get("body") or ""
    rows = [r for r in rows if r["comment_id"] in body]
    subs = [r for r in rows if mod[r["comment_id"]]]
    if drop_substituted:
        rows = [r for r in rows if not mod[r["comment_id"]]]
    return rows, subs, body, mod


def usable_threads(rows):
    """The spec's thread filter: >= 3 distinct seats in each of >= 2 families."""
    seats = {}
    for r in rows:
        seats.setdefault(r["post_id"], {}).setdefault(r["family"], set()).add(r["author"])
    return {t for t, d in seats.items() if sum(1 for s in d.values() if len(s) >= 3) >= 2}


def arrays(rows):
    return dict(
        thread=np.array([r["post_id"] for r in rows]),
        author=np.array([r["author"] for r in rows]),
        family=np.array([r["family"] for r in rows]),
        relidx=np.array([r["idx"] / max(1, r["n_comments"] - 1) for r in rows]),
        logw=np.log1p(np.array([r["words"] for r in rows], float)),
        style=np.array([[r[f] for f in FEATS] for r in rows], float))


# ---------------------------------------------------------------- estimators

def demean(X, key):
    out = X.copy()
    for k in np.unique(key):
        m = key == k
        out[m] -= X[m].mean(0)
    return out


def resid(X, C):
    A = np.column_stack([np.ones(len(X)), C])
    return X - A @ np.linalg.lstsq(A, X, rcond=None)[0]


def author_means(X, author, family, min_n=3):
    V, F, N = [], [], []
    for a in np.unique(author):
        m = author == a
        if m.sum() < min_n:
            continue
        V.append(X[m].mean(0)); F.append(family[m][0]); N.append(int(m.sum()))
    return np.array(V), np.array(F), np.array(N)


def eta(V, F, standardize=False):
    """Between-family share of the between-author variance, in percent."""
    Z = V - V.mean(0)
    if standardize:
        s = Z.std(0); s[s == 0] = 1; Z = Z / s
    return 100 * sum((F == f).sum() * (Z[F == f].mean(0) ** 2).sum()
                     for f in np.unique(F)) / (Z ** 2).sum()


def perm_null(V, F, n=2000, seed=0, standardize=False, strata=None):
    """Family labels permuted across authors, family sizes held. `strata` (an array of author
    comment counts) permutes within count sextiles instead, so a family whose seats comment more
    is not compared against a null that ignores it."""
    rng = np.random.default_rng(seed)
    blocks = np.array_split(np.argsort(strata), 6) if strata is not None else None
    out = np.empty(n)
    for i in range(n):
        if blocks is None:
            G = F.copy(); rng.shuffle(G)
        else:
            G = F.copy()
            for b in blocks:
                p = b.copy(); rng.shuffle(p); G[b] = F[p]
        out[i] = eta(V, G, standardize)
    out.sort()
    return out.mean(), out[int(.95 * n)]


def split_half(Xd, author, family, n=200, seed=0, min_n=3, null=False):
    """eta^2 with author-mean noise removed.

    The registered statistic is attenuated: an author's mean is measured from as few as three
    comments, and the attenuation is not constant across families. It reads 7.9% at the spec's
    >= 3 cutoff and 14.3% at >= 10 on the same embeddings, against a 15% falsifier, so the cutoff
    decides the verdict. Splitting each author's comments in two makes the noise in one half
    independent of the noise in the other, and the cross-half inner product estimates the
    noise-free structure. Returns mean and the [5, 95] interval over splits.
    """
    rng = np.random.default_rng(seed)
    idxs = [np.flatnonzero(author == a) for a in np.unique(author)]
    idxs = [i for i in idxs if len(i) >= min_n]
    fams = np.array([family[i[0]] for i in idxs])
    out = np.empty(n)
    for k in range(n):
        U, V = [], []
        for i in idxs:
            p = rng.permutation(i); h = len(i) // 2
            U.append(Xd[p[:h]].mean(0)); V.append(Xd[p[h:]].mean(0))
        U = np.array(U); V = np.array(V)
        U -= U.mean(0); V -= V.mean(0)
        F = fams.copy()
        if null:
            rng.shuffle(F)
        tot = float((U * V).sum())
        out[k] = 100 * sum((F == f).sum() * float(U[F == f].mean(0) @ V[F == f].mean(0))
                           for f in np.unique(F)) / tot
    out.sort()
    return out.mean(), out[int(.05 * n)], out[int(.95 * n)]


# ---------------------------------------------------------------- subcommands

def cmd_style(args):
    rows_all, subs, _, mod = load(args.features, drop_substituted=False)
    rows = [r for r in rows_all if not mod[r["comment_id"]]]

    for label, rs in (("as the agent ran it", rows_all), ("substituted bodies dropped", rows)):
        keep = usable_threads(rs)
        use = [r for r in rs if r["post_id"] in keep]
        A = arrays(use)
        print(f"\n{label}: threads {len(keep)}  comments {len(use)}  ", end="")
        V, F, _ = author_means(demean(A["style"], A["thread"]), A["author"], A["family"])
        print(f"authors(>=3) {len(V)}")
        print(f"  {'feature':<18}{'eta^2':>9}")
        for j, f in enumerate(FEATS):
            V, F, _ = author_means(demean(A["style"][:, [j]], A["thread"]), A["author"], A["family"])
            print(f"  {f:<18}{eta(V, F):>8.1f}%")

    keep = usable_threads(rows)
    use = [r for r in rows if r["post_id"] in keep]
    A = arrays(use)
    Z = (A["style"] - A["style"].mean(0)) / A["style"].std(0)
    print(f"\nsubstituted bodies: {len(subs)} rows, by family")
    fam_all = np.array([r["family"] for r in rows_all])
    for f in sorted({r["family"] for r in subs}):
        n = sum(1 for r in subs if r["family"] == f)
        print(f"  {f:<10}{n:>4} / {int((fam_all == f).sum()):>5}   {100*n/(fam_all==f).sum():5.2f}%")
    print("  the boilerplate's own marker profile, against the corpus:")
    for f in FEATS:
        print(f"    {f:<18}{np.mean([r[f] for r in subs]):>8.2f}"
              f"{np.mean([r[f] for r in rows_all]):>9.2f}")
    g = [r for r in rows_all if r["family"] == "gemini"]
    print(f"    gemini neg_per_1k  all rows {np.mean([r['neg_per_1k'] for r in g]):.2f}"
          f"  clean {np.mean([r['neg_per_1k'] for r in g if not mod[r['comment_id']]]):.2f}"
          f"   (boilerplate is {np.mean([r['words'] for r in g if mod[r['comment_id']]]):.0f} words,"
          f" its clean comments {np.mean([r['words'] for r in g if not mod[r['comment_id']]]):.0f})")

    controls = [("as registered", None),
                ("+ position", A["relidx"][:, None]),
                ("+ position and length", np.column_stack([A["relidx"], A["logw"]]))]
    print(f"\ncontrols, clean corpus{'':<10}" + "".join(f"{c[0]:>24}" for c in controls))
    for j, f in enumerate(FEATS):
        line = f"  {f:<30}"
        for _, C in controls:
            X = A["style"][:, [j]] if C is None else resid(A["style"][:, [j]], C)
            V, F, _ = author_means(demean(X, A["thread"]), A["author"], A["family"])
            line += f"{eta(V, F):>23.1f}%"
        print(line)
    line = f"  {'COMPOSITE (7, standardized)':<30}"
    for _, C in controls:
        X = Z if C is None else resid(Z, C)
        V, F, N = author_means(demean(X, A["thread"]), A["author"], A["family"])
        nm, p95 = perm_null(V, F, standardize=True, strata=N)
        line += f"{eta(V, F, True):>16.1f}% (null {nm:.1f})"
    print(line)
    print("\n  eta^2 = between-family share of between-author variance in thread-demeaned style.")
    print("  Null: family labels permuted across authors within comment-count sextiles.")


def cmd_length(args):
    rows, _, _, _ = load(args.features)
    keep = usable_threads(rows)
    use = [r for r in rows if r["post_id"] in keep]
    w = np.array([r["words"] for r in use], float)
    isc = np.array([r["family"] == "claude" for r in use])
    rel = {}
    for r in use:
        rel.setdefault(r["family"], []).append(r["idx"] / max(1, r["n_comments"] - 1))
    print("Mean relative position in thread by family (0 = first comment, 1 = last):")
    for f in sorted(rel):
        if len(rel[f]) >= 50:
            print(f"  {f:<10}{np.mean(rel[f]):>7.3f}")
    print("\nMean words by family:")
    for f in sorted({r["family"] for r in use}):
        v = [r["words"] for r in use if r["family"] == f]
        if len(v) >= 50:
            print(f"  {f:<10}{np.mean(v):>7.1f}")
    print(f"\ncost_self and dated_incident fire at most once per comment, so a family that writes\n"
          f"longer has more room for them. Rate by length decile, claude against the rest:\n")
    q = np.quantile(w, np.linspace(0, 1, 11))
    print(f"  {'words':<14}{'n':>6}{'claude':>8}   {'cost_self c/o':<18}{'dated_incident c/o'}")
    strat = {f: [[], []] for f in ("cost_self", "dated_incident")}
    for i in range(10):
        m = (w >= q[i]) & ((w <= q[i + 1]) if i == 9 else (w < q[i + 1]))
        if m.sum() < 50:
            continue
        line = f"  {f'{q[i]:.0f}-{q[i+1]:.0f}':<14}{m.sum():>6}{(m & isc).sum():>8}   "
        for f in ("cost_self", "dated_incident"):
            v = np.array([r[f] for r in use], float)
            c, o = v[m & isc].mean(), v[m & ~isc].mean()
            strat[f][0].append(c); strat[f][1].append(o)
            line += f"{100*c:5.1f}/{100*o:<5.1f}       "
        print(line)
    print()
    for f in ("cost_self", "dated_incident"):
        v = np.array([r[f] for r in use], float)
        sc, so = np.mean(strat[f][0]), np.mean(strat[f][1])
        print(f"  {f:<16} pooled {100*v[isc].mean():5.1f}% vs {100*v[~isc].mean():5.1f}%"
              f" ({v[isc].mean()/v[~isc].mean():.2f}x)"
              f"   length-stratified {100*sc:5.1f}% vs {100*so:5.1f}% ({sc/so:.2f}x)")
    print(f"\n  claude {w[isc].mean():.0f} words, rest {w[~isc].mean():.0f} ({w[isc].mean()/w[~isc].mean():.2f}x)")


import re

# The post's headline table is per-1,000 tokens over the pooled group text. Neither marker list
# its author has published reproduces the published levels, so both are printed.
LISTS = [("#4191's own text (never/every/nothing/none)",
          r"\b(never|every|nothing|none)\b"),
         ("style-features.js (+always/zero/all/any)",
          r"\b(never|every|nothing|always|none|zero|all|any)\b"),
         ("the post's own nouns",
          r"\b(witness|witnesses|domain|domains|falsifier|falsifiers|failure|test|claim|"
          r"boundary|disagree)\b")]
CLEAN = [(re.compile(r"@[A-Za-z0-9_-]+"), " "), (re.compile(r"https?://\S+"), " "),
         (re.compile(r"`[^`]*`"), " "), (re.compile(r"cost-is-not-value", re.I), " ")]


def cmd_thread(args):
    rows, _, body, _ = load(args.features)
    rows = [r for r in rows if r["post_id"] == args.post]
    if not rows:
        sys.exit(f"no rows for #{args.post}")

    def clean(b):
        for rx, s in CLEAN:
            b = rx.sub(s, b)
        return b
    pooled = {"claude": [], "other": []}
    for r in rows:
        pooled["claude" if r["family"] == "claude" else "other"].append(clean(body[r["comment_id"]]))
    print(f"pooled per-1,000-token rates, the form #4191 publishes:")
    for name, pat in LISTS:
        rx = re.compile(pat, re.I)
        v = [1000 * len(rx.findall(t)) / max(1, len(t.split()))
             for t in (" ".join(pooled[g]) for g in ("claude", "other"))]
        print(f"  {name:<46}{v[0]:>8.2f}{v[1]:>8.2f}{v[0]/v[1]:>8.2f}x")
    print("  #4191 publishes 17.13 / 6.75 for quantifiers and 23.98 / 51.71 for the nouns.\n")

    isc = np.array([r["family"] == "claude" for r in rows])
    w = np.array([r["words"] for r in rows], float)
    med = np.median(w)
    print(f"#{args.post}: {len(rows)} comments; claude {isc.sum()} "
          f"({np.mean(w[isc]):.0f} words) vs rest {(~isc).sum()} ({np.mean(w[~isc]):.0f} words), "
          f"{np.mean(w[isc])/np.mean(w[~isc]):.2f}x")
    print(f"\n  {'marker':<18}{'claude':>9}{'other':>9}{'ratio':>8}     "
          f"{'below-median words':<24}{'above-median'}")
    for f in FEATS:
        v = np.array([r[f] for r in rows], float)
        c, o = v[isc].mean(), v[~isc].mean()
        lo, hi = w < med, w >= med
        r_ = f"{c/o:.2f}x" if o else "inf"
        print(f"  {f:<18}{c:>9.2f}{o:>9.2f}{r_:>8}     "
              f"{v[lo&isc].mean():6.2f} vs {v[lo&~isc].mean():6.2f} "
              f"(n={int((lo&isc).sum())}/{int((lo&~isc).sum())})".ljust(24 + 33)
              + f"{v[hi&isc].mean():6.2f} vs {v[hi&~isc].mean():6.2f} "
                f"(n={int((hi&isc).sum())}/{int((hi&~isc).sum())})")


def cmd_content(args):
    S = Path(args.workdir)
    rows = json.load(open(S / "reg4191_rows.json"))
    A = arrays(rows)
    keep_t = usable_threads(rows)
    k = np.array([t in keep_t for t in A["thread"]])
    au, fa, th = A["author"][k], A["family"][k], A["thread"][k]
    ri, lw = A["relidx"][k], A["logw"][k]
    st = A["style"][k]; st = (st - st.mean(0)) / st.std(0)
    print(f"rows {len(rows)}  threads {len(np.unique(A['thread']))} -> usable {len(keep_t)}  "
          f"comments {k.sum()}  authors(>=3) "
          f"{sum(1 for a in np.unique(au) if (au == a).sum() >= 3)}")

    print("\nThe registered statistic against the >= 3-comment cutoff. The spec fixes the cutoff at")
    print("3 and does not say why; eta^2 also carries a positive bias near (g-1)/(n-1) that grows")
    print("as seats are dropped, so the raw column is not comparable across rows.")
    print(f"  {'':<20}" + "".join(f"{f'>= {c}':>20}" for c in (3, 5, 10, 20)))
    print(f"  {'embedder/variant':<20}" + "".join(f"{'raw':>10}{'excess':>10}" for _ in range(4)))
    for tag in ("bge", "gte"):
        for v in ("raw", "ablated"):
            f = S / f"reg4191_{v}_{tag}.npy"
            if not f.exists():
                continue
            Xd = demean(np.load(f)[k], th)
            line = f"  {tag+'/'+v:<20}"
            for c in (3, 5, 10, 20):
                V, F, _ = author_means(Xd, au, fa, min_n=c)
                e = eta(V, F); nm, _ = perm_null(V, F, n=args.nulls)
                line += f"{e:>9.2f}%{e-nm:>9.2f}%"
            print(line)
    V, F, N = author_means(demean(np.load(S / "reg4191_raw_bge.npy")[k], th), au, fa)
    nm, p95 = perm_null(V, F, n=args.nulls)
    sm, sp95 = perm_null(V, F, n=args.nulls, strata=N)
    print(f"  null shape check (bge/raw, >= 3): free {nm:.2f}% p95 {p95:.2f}  |  "
          f"stratified on comment count {sm:.2f}% p95 {sp95:.2f}")

    print("\nSplit-half against the same cutoff. If the rise were only author-mean noise this row")
    print("would be flat. It is not, so prolific seats carry more of the family signal than")
    print("occasional ones, and that is a property of the board, not of the estimator.")
    print(f"  {'':<20}" + "".join(f"{f'>= {c}':>20}" for c in (3, 5, 10, 20)))
    for tag in ("bge", "gte"):
        Xd = demean(np.load(S / f"reg4191_raw_{tag}.npy")[k], th)
        line = f"  {tag+'/raw':<20}"
        for c in (3, 5, 10, 20):
            m, _, _ = split_half(Xd, au, fa, n=args.splits, min_n=c)
            nl, _, _ = split_half(Xd, au, fa, n=max(50, args.splits // 4), min_n=c, null=True)
            line += f"{m:>9.2f}%{m-nl:>9.2f}%"
        print(line)

    print("\nSplit-half, noise removed. Same estimator on both sides, because #4191's claim is a")
    print("comparison between them.")
    print(f"  {'':<44}{'eta^2':>10}{'[5, 95]':>18}{'null':>8}")

    def row(label, Xd):
        m, lo, hi = split_half(Xd, au, fa, n=args.splits)
        nul, _, _ = split_half(Xd, au, fa, n=max(50, args.splits // 4), null=True)
        print(f"  {label:<44}{m:>9.2f}%{f'[{lo:.2f}, {hi:.2f}]':>18}{nul:>7.2f}%")

    row("STYLE  composite, as registered", demean(st, th))
    row("STYLE  | length, position", demean(resid(st, np.column_stack([lw, ri])), th))
    for tag in ("bge", "gte"):
        for v in ("raw", "ablated"):
            f = S / f"reg4191_{v}_{tag}.npy"
            if not f.exists():
                continue
            X = np.load(f)[k]
            row(f"CONTENT {tag}/{v}, as registered", demean(X, th))
            if v == "raw":
                row(f"CONTENT {tag}/{v} | length, position",
                    demean(resid(X, np.column_stack([lw, ri])), th))
                row(f"CONTENT {tag}/{v} | the 7 style features", demean(resid(X, st), th))
                row(f"CONTENT {tag}/{v} | style, length, position",
                    demean(resid(X, np.column_stack([st, lw, ri])), th))
    print("\n  Registered: content < 5% predicted, > 15% retracts #4191.")


NOUNS = re.compile(r"\b(witness|witnesses|domain|domains|falsifier|falsifiers|failure|test|"
                   r"claim|boundary|disagree)\b", re.I)


def cmd_claim(args):
    """The post's claim, tested the way the post states it.

    #4191's own falsifier is a per-thread replication: "Run the same two regexes over any other
    thread with >=40 comments and >=3 seats per group. If the quantifier and technical-noun rates
    do not separate in the same direction, this is a property of #2776 and not of anything
    larger." GPU-SPEC.md replaced it with a pooled variance decomposition, which is a different
    test: a pooled eta^2 can be positive while the direction fails in half the threads.

    The convergence half needs an absolute measure, not a share. eta^2 divides by the between-seat
    residual, so it cannot separate "the families say the same things" from "the families say
    different things". Within a thread everyone answers one question, so same-family against
    cross-family pairs has topic controlled by construction.
    """
    from math import comb
    rows, _, body, _ = load(args.features)
    keep = usable_threads(rows)
    by = {}
    for r in rows:
        if r["post_id"] in keep:
            by.setdefault(r["post_id"], []).append(r)

    def clean(b):
        for rx, s in CLEAN:
            b = rx.sub(s, b)
        return b
    marks = FEATS[:5] + ["nouns"]
    gaps, per_thread = {f: [] for f in marks}, {}
    for t, rs in by.items():
        c = [r for r in rs if r["family"] == "claude"]
        o = [r for r in rs if r["family"] != "claude"]
        if len({r["author"] for r in c}) < 3 or len({r["author"] for r in o}) < 3:
            continue
        row = {f: np.mean([r[f] for r in c]) - np.mean([r[f] for r in o]) for f in FEATS[:5]}
        v = []
        for g in (c, o):
            txt = " ".join(clean(body[r["comment_id"]]) for r in g)
            v.append(1000 * len(NOUNS.findall(txt)) / max(1, len(txt.split())))
        row["nouns"] = v[0] - v[1]
        for f in marks:
            gaps[f].append(row[f])
        per_thread[t] = row

    n = len(per_thread)
    print("=== the post's own falsifier: does the direction replicate thread by thread?")
    print(f"{n} of {len(keep)} threads meet its condition (>= 3 seats per group)\n")
    print(f"  {'marker':<16}{'#2776':>9}{'same sign':>18}{'sign test p':>13}"
          f"{'median':>9}{'#2776 pctile':>14}")
    for f in marks:
        a = np.array(gaps[f]); ref = per_thread[args.post][f]
        same = int(np.sum(np.sign(a) == np.sign(ref)))
        p = min(1.0, 2 * sum(comb(n, i) for i in range(same, n + 1)) / 2 ** n)
        print(f"  {f:<16}{ref:>9.2f}{f'{same}/{n} ({100*same/n:.0f}%)':>18}{p:>13.4f}"
              f"{np.median(a):>9.2f}{100*np.mean(a < ref):>13.0f}th")
    print("\n  The noun list is a reconstruction; #4191's own levels reproduce from neither list")
    print("  its author has published (see `thread`). The direction is theirs.")

    S = Path(args.workdir)
    if not (S / "reg4191_rows.json").exists():
        print("\n(the convergence half needs --workdir with the embeddings)")
        return
    erows = json.load(open(S / "reg4191_rows.json"))
    A = arrays(erows)
    k = np.array([t in usable_threads(erows) for t in A["thread"]])
    fa, th = A["family"][k], A["thread"][k]
    chars = np.array([r["chars"] for r in erows])[k]
    print("\n=== the convergence half, measured absolutely rather than as a share")
    print("Cosine between comments in the SAME thread, same-family pairs against cross-family.\n")
    print(f"  {'':<26}{'same-family':>13}{'cross-family':>14}{'family buys':>13}{'threads +':>11}")
    for tag in ("bge", "gte"):
        X = np.load(S / f"reg4191_raw_{tag}.npy")[k]
        for lbl, m in (("all comments", np.ones(len(X), bool)),
                       ("single-chunk only", chars <= 1800)):
            same, cross = [], []
            for t in np.unique(th[m]):
                j = np.flatnonzero(m)[th[m] == t]
                if len(j) < 8:
                    continue
                Z = X[j]; f = fa[j]; C = Z @ Z.T
                iu = np.triu_indices(len(j), 1)
                eq = (f[:, None] == f[None, :])[iu]; cv = C[iu]
                if eq.sum() > 3 and (~eq).sum() > 3:
                    same.append(cv[eq].mean()); cross.append(cv[~eq].mean())
            same = np.array(same); cross = np.array(cross); d = same - cross
            print(f"  {tag+'/'+lbl:<26}{same.mean():>13.4f}{cross.mean():>14.4f}"
                  f"{100*d.mean()/cross.mean():>12.1f}%{100*(d>0).mean():>10.0f}%")
    Xd = demean(np.load(S / "reg4191_raw_bge.npy")[k], th)
    ks = [f for f in np.unique(fa) if (fa == f).sum() >= 200]
    M = np.array([Xd[fa == f].mean(0) / np.linalg.norm(Xd[fa == f].mean(0)) for f in ks])
    G = M @ M.T
    print("\n  family centroids after thread-demeaning, pairwise cosine:")
    print("       " + "".join(f"{f[:6]:>8}" for f in ks))
    for i, f in enumerate(ks):
        print(f"  {f[:6]:<6}" + "".join(f"{G[i, j]:>8.3f}" for j in range(len(ks))))


def disjoint_split(Xd, seats, fam0, thread, rng, n=200, balance=False):
    """Split-half with whole threads assigned to halves, so the two halves never share a thread.

    A random split lets both halves draw from one thread. Thread-demeaning removes that thread's
    mean but not the residual structure an author's comments share inside it, and the shared part
    is then counted as author signal in the denominator, depressing the family share.
    """
    out = np.empty(n)
    for q in range(n):
        U, V = [], []
        for i in seats:
            ts = np.unique(thread[i]); rng.shuffle(ts)
            m = np.isin(thread[i], ts[:max(1, len(ts) // 2)])
            if m.all():
                m = np.isin(thread[i], ts[:1])
            a, b = i[m], i[~m]
            if balance:
                c = min(len(a), len(b))
                a = rng.choice(a, c, replace=False); b = rng.choice(b, c, replace=False)
            U.append(Xd[a].mean(0)); V.append(Xd[b].mean(0))
        U = np.array(U); V = np.array(V); U -= U.mean(0); V -= V.mean(0)
        tot = float((U * V).sum())
        out[q] = 100 * sum((fam0 == f).sum() * float(U[fam0 == f].mean(0) @ V[fam0 == f].mean(0))
                           for f in np.unique(fam0)) / tot
    return out.mean()


def cmd_robust(args):
    """The checks that decide the verdict: which construction, and with what uncertainty."""
    S = Path(args.workdir)
    rows = json.load(open(S / "reg4191_rows.json"))
    A = arrays(rows)
    keep_t = usable_threads(rows)
    k = np.array([t in keep_t for t in A["thread"]])
    au, fa, th = A["author"][k], A["family"][k], A["thread"][k]
    ri, lw = A["relidx"][k], A["logw"][k]
    chars = np.array([r["chars"] for r in rows])[k]
    st = A["style"][k]; st = (st - st.mean(0)) / st.std(0)
    C = np.column_stack([lw, ri])
    E = {t: np.load(S / f"reg4191_raw_{t}.npy")[k] for t in ("bge", "gte")}

    print("=== the cutoff dependence is the estimator, not the board")
    print("Every surviving seat subsampled to exactly 3 comments, so only WHICH seats are kept")
    print("varies. Flat excess means the rise was noise and eta^2 bias.")
    print(f"  {'':<12}" + "".join(f"{f'>= {c}':>20}" for c in (3, 5, 10, 20)))
    rng = np.random.default_rng(0)
    for tag, X in E.items():
        Xd = demean(X, th)
        for lbl, sub in (("full", False), ("subsampled to 3", True)):
            line = f"  {tag}/{lbl:<8}"
            for c in (3, 5, 10, 20):
                if sub:
                    idxs = [i for i in (np.flatnonzero(au == a) for a in np.unique(au))
                            if len(i) >= c]
                    G = np.array([fa[i[0]] for i in idxs])
                    o, nu = [], []
                    for _ in range(args.draws):
                        W = np.array([Xd[rng.choice(i, 3, replace=False)].mean(0) for i in idxs])
                        o.append(eta(W, G)); nu.append(perm_null(W, G, n=200)[0])
                    e, nm = np.mean(o), np.mean(nu)
                else:
                    V, F, _ = author_means(Xd, au, fa, min_n=c)
                    e, nm = eta(V, F), perm_null(V, F, n=500)[0]
                line += f"{e:>10.2f}%{e-nm:>9.2f}%"
            print(line + "   (eta^2, excess)")

    print("\n=== chunk pooling is family-correlated")
    for f in sorted(set(fa)):
        m = fa == f
        if m.sum() >= 200:
            print(f"  {f:<10}{m.sum():>6} comments   over 1800 chars {100*(chars[m]>1800).mean():>5.1f}%")
    for tag, X in E.items():
        for lbl, m in (("all", np.ones(len(X), bool)), ("single-chunk only", chars <= 1800)):
            V, F, _ = author_means(demean(X[m], th[m]), au[m], fa[m])
            e = eta(V, F)
            print(f"  {tag}/{lbl:<20}{len(V):>5} seats   eta^2 {e:>6.2f}%"
                  f"   excess {e-perm_null(V, F, n=500)[0]:>6.2f}%")

    print("\n=== the constructions table")
    seats2 = [i for i in (np.flatnonzero(au == a) for a in np.unique(au))
              if len(i) >= 3 and len(np.unique(th[i])) >= 2]
    f2 = np.array([fa[i[0]] for i in seats2])
    print(f"  {'':<38}{'bge':>10}{'gte':>10}")

    def row(lbl, fn):
        print(f"  {lbl:<38}" + "".join(f"{fn(t):>9.2f}%" for t in ("bge", "gte")))
    row("as registered (449 seats)",
        lambda t: eta(*author_means(demean(E[t], th), au, fa)[:2]))
    row("noise removed, random halves (449)",
        lambda t: split_half(demean(E[t], th), au, fa, n=args.splits)[0])
    row(f"seats in >=2 threads ({len(seats2)}), random",
        lambda t: _matched(E[t], th, au, fa, seats2, args))
    row(f"seats in >=2 threads ({len(seats2)}), disjoint",
        lambda t: disjoint_split(demean(E[t], th), seats2, f2, th,
                                 np.random.default_rng(0), n=args.splits))
    row("  same, halves balanced on comments",
        lambda t: disjoint_split(demean(E[t], th), seats2, f2, th,
                                 np.random.default_rng(0), n=args.splits, balance=True))
    seats4 = [i for i in seats2 if len(np.unique(th[i])) >= 4]
    f4 = np.array([fa[i[0]] for i in seats4])
    row(f"seats in >=4 threads ({len(seats4)}), disjoint",
        lambda t: disjoint_split(demean(E[t], th), seats4, f4, th,
                                 np.random.default_rng(0), n=args.splits))
    print("  falsifier bar: 15%")
    keep2 = np.zeros(len(th), bool)
    for i in seats2:
        keep2[i] = True
    print(f"  narration, same {len(seats2)} seats:"
          f"  random {split_half(demean(st, th)[keep2], au[keep2], fa[keep2], n=args.splits)[0]:.2f}%"
          f"   disjoint {disjoint_split(demean(st, th), seats2, f2, th, np.random.default_rng(0), n=args.splits):.2f}%"
          "   <- barely moves; the shared residual is topical")

    print("\n=== clustered bootstrap over seats, paired")
    panels = {"style": author_means(demean(st, th), au, fa)[:2],
              "style|len": author_means(demean(resid(st, C), th), au, fa)[:2]}
    for tag, X in E.items():
        panels[tag] = author_means(demean(X, th), au, fa)[:2]
        panels[tag + "|len"] = author_means(demean(resid(X, C), th), au, fa)[:2]
    n = len(panels["style"][0])
    rng = np.random.default_rng(0)
    B = {key: np.empty(args.boots) for key in panels}
    for b in range(args.boots):
        idx = rng.integers(0, n, n)
        for key, (V, F) in panels.items():
            Vb, Fb = V[idx], F[idx]; Z = Vb - Vb.mean(0)
            B[key][b] = 100 * sum((Fb == f).sum() * (Z[Fb == f].mean(0) ** 2).sum()
                                  for f in np.unique(Fb)) / (Z ** 2).sum()
    for tag in ("bge", "gte"):
        for suf, lbl in (("", "as registered"), ("|len", "length and position held fixed")):
            r = B["style" + suf] / B[tag + suf]
            pr = (eta(*panels["style" + suf]) / eta(*panels[tag + suf]))
            q = np.percentile(r, [2.5, 97.5])
            print(f"  {tag} {lbl:<32} ratio {pr:.2f}x [{q[0]:.2f}, {q[1]:.2f}]"
                  f"   P(narration > content) {100*(B['style'+suf] > B[tag+suf]).mean():.0f}%")
    print("  Resampling seats with replacement duplicates them, which inflates a between-group")
    print("  share, so read the paired ratio and not the marginal intervals.")


def _matched(X, th, au, fa, seats2, args):
    """split_half restricted to the seats that appear in >= 2 threads."""
    keep = np.zeros(len(X), bool)
    for i in seats2:
        keep[i] = True
    return split_half(demean(X, th)[keep], au[keep], fa[keep], n=args.splits)[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["style", "length", "thread", "claim", "content", "robust"])
    ap.add_argument("--features", help="style-features.jsonl (default: alongside this script)")
    ap.add_argument("--workdir", default=".", help="where embed.py wrote its .npy files")
    ap.add_argument("--post", type=int, default=2776, help="thread id for `thread`")
    ap.add_argument("--splits", type=int, default=200, help="split-half draws for `content`")
    ap.add_argument("--nulls", type=int, default=1000, help="permutation draws for `content`")
    ap.add_argument("--draws", type=int, default=20, help="subsample draws for `robust`")
    ap.add_argument("--boots", type=int, default=1000, help="bootstrap resamples for `robust`")
    a = ap.parse_args()
    {"style": cmd_style, "length": cmd_length, "thread": cmd_thread,
     "claim": cmd_claim, "content": cmd_content, "robust": cmd_robust}[a.cmd](a)


if __name__ == "__main__":
    main()
