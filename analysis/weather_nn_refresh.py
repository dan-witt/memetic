#!/usr/bin/env python3
"""Matched-pool newcomer-refresh cell with an in-geometry permutation null.

Answers: do the claims of authors who arrived in this issue's window sit farther from the
incumbent claim cloud than incumbents sit from each other? (> null = genuine refresh.)

CONSTRUCTION. Each draw partitions the window's INCUMBENT items into three disjoint sets:
a reference pool R, a probe, and a pseudo-newcomer set, with |probe| = |pseudo| = |newcomers|.
  observed delta = median NN-distance(newcomers -> R) - median NN-distance(probe -> R)
  null delta     = median NN-distance(pseudo    -> R) - median NN-distance(probe -> R)
Every query set searches the SAME pool at the SAME size, so pool-size bias cancels; the null
is a label permutation in this corpus's own embedding geometry and centres on 0 by construction.

This SUPERSEDES the asymmetric construction carried by weather_gpu.py before issue #4 (newcomers
queried against ALL incumbents, incumbents against only HALF). A larger candidate pool
mechanically yields a closer nearest neighbour, so that version biased the newcomer side DOWN,
toward "indistinguishable" — by roughly -0.015 to -0.020 on real windows, enough to flip the
sign. Issue #3 omitted the cell rather than publish it; issue #4 publishes this instead.
weather_nn_validate.py is the synthetic null/power check for the construction.

40 draws pins the two-sided permutation p at a floor of 2/40 = 0.05; this uses 500.

USAGE
  weather_nn_refresh.py <label>:<cutoff>:<prev_corpus_dir> [more...]
where <cutoff> is YYYY-MM-DD (that date's midnight UTC, exclusive) and <prev_corpus_dir> holds
the PREVIOUS issue's data/posts, defining the window start as its last raw item. Prior corpus
states come out of git, e.g.
  git archive <issue-N commit> data/posts | tar -x -C /tmp/prevN
Reads the claim cache from $MEMETIC_WORKDIR; writes nn_matched_500draws.json there.
"""
import json, os, sys, datetime as dt
from pathlib import Path
import numpy as np

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
DRAWS = int(os.environ.get("WEATHER_NN_DRAWS", "500"))
CORPUS = "/home/dan/personal/memetic/data/posts"


def load_items(d, cutoff):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]


def matched_nn(En, Ei, draws=DRAWS, seed=0):
    """En = newcomer embeddings, Ei = incumbent embeddings (both L2-normalised)."""
    rng = np.random.default_rng(seed)
    q = min(len(En), len(Ei) // 3)
    P = len(Ei) - 2 * q
    dn, di, dobs, dnull = [], [], [], []
    for _ in range(draws):
        perm = rng.permutation(len(Ei))
        R, probe, pseudo = Ei[perm[:P]], Ei[perm[P:P + q]], Ei[perm[P + q:P + 2 * q]]
        qn = En[rng.choice(len(En), q, replace=False)]
        b = float(np.median(1 - (probe @ R.T).max(1)))
        dn.append(float(np.median(1 - (qn @ R.T).max(1)))); di.append(b)
        dobs.append(dn[-1] - b)
        dnull.append(float(np.median(1 - (pseudo @ R.T).max(1))) - b)
    band = lambda v: [round(float(np.percentile(v, p)), 4) for p in (50, 5, 95)]
    nl, ob = np.array(dnull), float(np.median(dobs))
    return {"reference_pool": P, "queries_per_side": q, "draws": draws,
            "newcomer_to_pool": band(dn), "incumbent_to_pool": band(di),
            "delta_observed": band(dobs), "delta_permutation_null": band(dnull),
            "p_two_sided_vs_null": round(float(2 * min((nl >= ob).mean(), (nl <= ob).mean())), 4),
            "frac_null_ge_observed": round(float((nl >= ob).mean()), 4)}


def legacy_asymmetric(En, Ei, draws=DRAWS, seed=0):
    """The superseded construction, retained only to size its bias on real data.

    As originally written it took ONE random half-split of the incumbents for its baseline, so
    its delta carried no band and moved by ~0.005 between runs — a second defect on top of the
    unequal pool sizes. Here the half-split is repeated `draws` times so the bias estimate is
    stable and comparable to the matched cell. The newcomer arm is deterministic (all newcomers
    against all incumbents), which is exactly the asymmetry at issue.
    """
    rng = np.random.default_rng(seed)
    nn_new = float(np.median(1 - (En @ Ei.T).max(1)))
    base = []
    for _ in range(draws):
        half = rng.permutation(len(Ei)); h1, h2 = half[:len(half)//2], half[len(half)//2:]
        base.append(float(np.median(1 - (Ei[h1] @ Ei[h2].T).max(1))))
    band = lambda v: [round(float(np.percentile(v, p)), 4) for p in (50, 5, 95)]
    return {"newcomer_to_incumbent_median": round(nn_new, 4),
            "incumbent_to_incumbent_median": band(base),
            "delta": band([nn_new - b for b in base]),
            "note": "SUPERSEDED; queries newcomers against ALL incumbents but incumbents against "
                    "HALF. Published only to size the bias; not a reading."}


def main(specs):
    cache = {(k0, int(k1)): c for (k0, k1), c in
             ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
    from sentence_transformers import SentenceTransformer
    M = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
    res = {}
    for spec in specs:
        label, cutoff, prevdir = spec.split(":", 2)
        cut = dt.datetime(*map(int, cutoff.split("-")), tzinfo=dt.timezone.utc).timestamp()
        NEW = load_items(CORPUS, cut)
        prev_last = max(t for t, _, _, _ in load_items(prevdir, cut))
        claims = [cache[k] for _, k, _, _ in NEW]
        claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim"
                  for c in claims]
        win = [i for i, (t, k, x, a) in enumerate(NEW) if t > prev_last]
        first = {}
        for t, k, x, a in NEW:
            if a not in first: first[a] = t
        idx_newc = [i for i in win if first[NEW[i][3]] > prev_last]
        idx_inc = [i for i in win if first[NEW[i][3]] <= prev_last]
        Ea = M.encode(claims, normalize_embeddings=True, batch_size=64,
                      show_progress_bar=False).astype(np.float32)
        En, Ei = Ea[np.array(idx_newc)], Ea[np.array(idx_inc)]
        res[label] = {"cutoff_utc": cutoff + "T00:00:00Z",
                      "window_start_utc": dt.datetime.fromtimestamp(prev_last, dt.timezone.utc)
                                            .strftime("%Y-%m-%d %H:%M:%S"),
                      "corpus_items": len(NEW), "window_items": len(win),
                      "newcomer_items": len(idx_newc), "incumbent_items": len(idx_inc),
                      "matched": matched_nn(En, Ei), "legacy_asymmetric": legacy_asymmetric(En, Ei)}
        print(label, json.dumps(res[label], indent=1), flush=True)
    json.dump(res, open(S / "nn_matched_500draws.json", "w"), indent=1)
    print(f"saved {S / 'nn_matched_500draws.json'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
