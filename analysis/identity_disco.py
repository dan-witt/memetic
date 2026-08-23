#!/usr/bin/env python3
"""Is a citizen's voice explained by its reported model, by model+harness, or is there an author
effect beyond both? -- and does the answer survive claim-normalization (idea level vs lexical)?

Method: DISCO (Szekely & Rizzo 2010) -- energy-distance ANOVA. With Euclidean distance the total
dispersion decomposes exactly and hierarchically:

    T = S_model  +  S_author|model  +  W_within_author
    T   = (N/2) * mean pairwise distance, pooled
    W_g = sum_g (n_g/2) * mean pairwise distance inside group g

Two things make this a test rather than a description:

  1. Every reported component is compared to a PERMUTATION NULL, never to zero. At n~12k the raw
     between-author energy distance is significantly nonzero even when authors are exchangeable,
     because finite-sample energy distance is positive by construction. The null shuffles item ->
     author labels WITHIN model family, which is exact under "identity is fully explained by
     model". The model component's null shuffles model labels at the AUTHOR level, since model is
     a between-author factor for all but 21 citizens.
  2. The design is BALANCED -- every author contributes exactly CAP items, resampled over DRAWS
     seeds. Equal group sizes make the finite-sample bias identical across groups and identical
     under permutation, and stop the 36 authors with >=100 items from setting the answer on their
     own.

Confound controls, each rerun of the headline:
  thread   -- restricted to (thread x model) cells holding >=2 authors, permuted within cell.
              Authors have beats; an uncontrolled author effect is partly a topic effect.
  length   -- embeddings residualized on [1, log chars, log^2 chars]. The human-baselines
              addendum found the semantic gap here was mostly register; register is length-led.
  nodup    -- drops items with cosine >= 0.95 to an earlier item by the same author. all-items
              ablation was inflated ~2x by same-author bursts; the same artifact would tighten
              within-author dispersion here.

Plus two things DISCO cannot say on its own:
  switchers -- the 21 citizens who posted under >1 model. Within-subject, so between-author
               confounds cannot reach it: is author-a-on-model-1 nearer author-a-on-model-2, or
               nearer other-authors-on-model-1?
  identify  -- held-out identification trained on each author's chronologically FIRST half and
               tested on its SECOND. Burst-immune, and legible: can you name the author?

Reads identity_items.json + identity_emb_*.npy from MEMETIC_WORKDIR; writes identity_stats.json.
"""
import json, os, collections, sys
from pathlib import Path
import numpy as np

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
REPO = Path(__file__).resolve().parent.parent
MIN_ITEMS, CAP, DRAWS, PERMS = 20, 20, 10, 200
MIN_SW = 15                     # per-model floor for a switcher's two arms
SEED = 0

# ------------------------------------------------------------------ energy / DISCO
def dmat(E):
    G = E @ E.T
    D = np.sqrt(np.maximum(2.0 - 2.0 * G, 0.0))
    np.fill_diagonal(D, 0.0)
    return D.astype(np.float64)

def _within(D, groups):
    return sum(0.5 * len(ix) * D[np.ix_(ix, ix)].mean() for ix in groups if len(ix))

def groups_of(labels):
    g = collections.defaultdict(list)
    for i, l in enumerate(labels): g[l].append(i)
    return {k: np.asarray(v) for k, v in g.items()}

def disco_nested(D, model_lab, author_lab):
    """T = S_model + S_author|model + W_within_author, returned as fractions of T."""
    N = D.shape[0]
    T = 0.5 * N * D.mean()
    Wm = _within(D, list(groups_of(model_lab).values()))
    # the finest group is (model, author), not author: 21 citizens post under >1 model, so a
    # bare author label is NOT nested inside model and the decomposition would not telescope.
    Wa = _within(D, list(groups_of(list(zip(model_lab, author_lab))).values()))
    return dict(eta2_model=(T - Wm) / T, eta2_author=(Wm - Wa) / T, eta2_within=Wa / T, T=T)

def eta2_author_given(D, author_lab, block_lab, rng=None):
    """Between-author dispersion inside each block, as a fraction of T. rng shuffles author
    labels within block (the exchangeability null)."""
    N = D.shape[0]
    T = 0.5 * N * D.mean()
    a = np.asarray(author_lab, dtype=object)
    if rng is not None:
        a = a.copy()
        for ix in groups_of(block_lab).values():
            a[ix] = rng.permutation(a[ix])
    Wb = _within(D, list(groups_of(block_lab).values()))
    Wa = _within(D, list(groups_of(list(zip(block_lab, a))).values()))   # nested, see disco_nested
    return (Wb - Wa) / T

def energy(D, ia, ib):
    """Two-sample energy distance, >= 0, zero iff distributions coincide."""
    return float(2 * D[np.ix_(ia, ib)].mean() - D[np.ix_(ia, ia)].mean() - D[np.ix_(ib, ib)].mean())

# ------------------------------------------------------------------ view assembly
def residualize(E, nchars):
    x = np.log(np.asarray(nchars, dtype=np.float64))
    X = np.column_stack([np.ones_like(x), x, x * x])
    B, *_ = np.linalg.lstsq(X, E, rcond=None)
    R = E - X @ B
    return (R / np.linalg.norm(R, axis=1, keepdims=True)).astype(np.float32)

def drop_bursts(E, rows, thresh=0.95):
    """Drop an item whose cosine to an EARLIER item by the same author is >= thresh."""
    keep, by = np.ones(len(rows), bool), collections.defaultdict(list)
    for i, r in enumerate(rows):                       # rows are chronological
        prev = by[r["author"]]
        if prev and float((E[prev] @ E[i]).max()) >= thresh:
            keep[i] = False
        else:
            by[r["author"]].append(i)
    return keep

def balanced(rows, rng, cap=CAP, min_items=MIN_ITEMS):
    by = collections.defaultdict(list)
    for i, r in enumerate(rows): by[r["author"]].append(i)
    pick = []
    for a, ix in by.items():
        if len(ix) >= min_items:
            pick.extend(rng.choice(ix, cap, replace=False))
    return np.sort(np.asarray(pick))

# ------------------------------------------------------------------ headline
def headline(E, rows, tag, log):
    """Balanced nested DISCO with both permutation nulls, averaged over DRAWS resamples."""
    obs_m, obs_a, obs_w, null_a, null_m, ns = [], [], [], [], [], []
    for d in range(DRAWS):
        rng = np.random.default_rng(SEED + d)
        ix = balanced(rows, rng)
        if len(ix) < 200: return None
        D = dmat(E[ix])
        mod = [rows[i]["model_family"] for i in ix]
        aut = [rows[i]["author"] for i in ix]
        r = disco_nested(D, mod, aut)
        obs_m.append(r["eta2_model"]); obs_a.append(r["eta2_author"]); obs_w.append(r["eta2_within"])
        ns.append(len(ix))
        for _ in range(PERMS // DRAWS * 2):
            null_a.append(eta2_author_given(D, aut, mod, rng))
        # model null: permute the model label at AUTHOR level (authors exchangeable across models)
        a2m = {}
        for i in ix: a2m.setdefault(rows[i]["author"], rows[i]["model_family"])
        auths = list(a2m); fams = [a2m[a] for a in auths]
        for _ in range(PERMS // DRAWS * 2):
            perm = dict(zip(auths, rng.permutation(fams)))
            mp = [perm[rows[i]["author"]] for i in ix]
            N = D.shape[0]; T = 0.5 * N * D.mean()
            null_m.append((T - _within(D, list(groups_of(mp).values()))) / T)
    o_a, o_m = float(np.mean(obs_a)), float(np.mean(obs_m))
    na, nm = np.asarray(null_a), np.asarray(null_m)
    out = dict(n_items=int(np.mean(ns)), n_authors=int(np.mean(ns)) // CAP,
               eta2_model=round(o_m, 4), eta2_author=round(o_a, 4),
               eta2_within=round(float(np.mean(obs_w)), 4),
               author_null_mean=round(float(na.mean()), 4),
               author_excess=round(o_a - float(na.mean()), 4),
               author_z=round((o_a - na.mean()) / na.std(), 1),
               author_p=round(float(((na >= o_a).sum() + 1) / (len(na) + 1)), 4),
               model_null_mean=round(float(nm.mean()), 4),
               model_excess=round(o_m - float(nm.mean()), 4),
               model_z=round((o_m - nm.mean()) / nm.std(), 1),
               model_p=round(float(((nm >= o_m).sum() + 1) / (len(nm) + 1)), 4))
    log(f"  [{tag}] n={out['n_items']} ({out['n_authors']} authors x {CAP})  "
        f"model eta2={out['eta2_model']} (null {out['model_null_mean']}, z={out['model_z']})  "
        f"author|model eta2={out['eta2_author']} (null {out['author_null_mean']}, z={out['author_z']})  "
        f"within={out['eta2_within']}")
    return out

# ------------------------------------------------------------------ thread control
def block_control(E, rows, keyfn, name, log, min_cell=4):
    """Author effect inside cells that hold the confound fixed. Two blockings:
      (thread, model)  same conversation, same weights -- removes topic, and narrows the time
                       window ~6x (median thread spans 35 h against a 202 h median tenure)
      (day, model)     same day, same weights -- removes the residual tenure/cohort drift that a
                       thread block leaves behind
    Cells with <2 authors carry no author information and are dropped."""
    cells = collections.defaultdict(list)
    for i, r in enumerate(rows): cells[keyfn(r)].append(i)
    use = [v for v in cells.values()
           if len(v) >= min_cell and len({rows[i]["author"] for i in v}) >= 2]
    ix = np.sort(np.concatenate([np.asarray(v) for v in use])) if use else np.array([], int)
    if len(ix) < 100: return None
    D = dmat(E[ix])
    cell = [str(keyfn(rows[i])) for i in ix]
    aut = [rows[i]["author"] for i in ix]
    obs = eta2_author_given(D, aut, cell)
    rng = np.random.default_rng(SEED)
    null = np.array([eta2_author_given(D, aut, cell, rng) for _ in range(PERMS)])
    out = dict(n_cells=len(use), n_items=int(len(ix)),
               n_authors=len({rows[i]["author"] for i in ix}),
               eta2_author_in_cell=round(float(obs), 4),
               null_mean=round(float(null.mean()), 4),
               excess=round(float(obs - null.mean()), 4),
               z=round(float((obs - null.mean()) / null.std()), 1),
               p=round(float(((null >= obs).sum() + 1) / (PERMS + 1)), 4))
    log(f"  [{name} cells] {out['n_cells']} cells, n={out['n_items']}: "
        f"eta2={out['eta2_author_in_cell']} vs null {out['null_mean']} (z={out['z']}, p={out['p']})")
    return out

# ------------------------------------------------------------------ switchers
def switchers(E, rows, log):
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, r in enumerate(rows): by[r["author"]][r["model_family"]].append(i)
    per_model = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, r in enumerate(rows): per_model[r["model_family"]][r["author"]].append(i)
    out, wins = [], 0
    for a, mm in by.items():
        arms = {m: v for m, v in mm.items() if len(v) >= MIN_SW}
        if len(arms) < 2: continue
        ms = sorted(arms, key=lambda m: -len(arms[m]))[:2]
        ia, ib = np.asarray(arms[ms[0]]), np.asarray(arms[ms[1]])
        peers = [np.asarray(v) for b, v in per_model[ms[0]].items() if b != a and len(v) >= MIN_SW]
        if not peers: continue
        allix = np.concatenate([ia, ib] + peers)
        order = {v: k for k, v in enumerate(allix)}
        D = dmat(E[allix])
        rm = lambda arr: np.asarray([order[x] for x in arr])
        d_self = energy(D, rm(ia), rm(ib))
        d_peer = [energy(D, rm(ia), rm(p)) for p in peers]
        rec = dict(author=a, model_a=ms[0], n_a=len(ia), model_b=ms[1], n_b=len(ib),
                   n_peers=len(peers), d_self_across_model=round(d_self, 4),
                   d_peer_same_model_median=round(float(np.median(d_peer)), 4),
                   ratio=round(float(np.median(d_peer)) / d_self, 2) if d_self > 0 else None)
        wins += rec["ratio"] is not None and rec["ratio"] > 1
        out.append(rec)
    out.sort(key=lambda r: -(r["n_a"] + r["n_b"]))
    n = len(out)
    from math import comb
    p = sum(comb(n, k) for k in range(wins, n + 1)) / 2 ** n if n else None
    log(f"  [switchers] {n} citizens with two >={MIN_SW}-item arms; "
        f"self-across-model closer than peers-same-model in {wins}/{n} (sign p={p:.4g})")
    for r in out[:6]:
        log(f"     {r['author']:>22}  {r['model_a']}({r['n_a']}) vs {r['model_b']}({r['n_b']}): "
            f"self={r['d_self_across_model']} peer={r['d_peer_same_model_median']} ratio={r['ratio']}")
    return dict(n=n, wins=wins, sign_p=p, rows=out)

# ------------------------------------------------------------------ identification
def identify(E, rows, log, min_items=2 * MIN_ITEMS):
    """Train on each author's chronologically first half, test on its second."""
    by = collections.defaultdict(list)
    for i, r in enumerate(rows): by[r["author"]].append(i)      # rows are chronological
    tr, te = {}, {}
    for a, ix in by.items():
        if len(ix) < min_items: continue
        h = len(ix) // 2
        tr[a] = np.asarray(ix[:h]); te[a] = np.asarray(ix[h:])
    if len(tr) < 5: return None
    auths = sorted(tr)
    C = np.stack([E[tr[a]].mean(0) for a in auths]); C /= np.linalg.norm(C, axis=1, keepdims=True)
    a2m = {a: rows[tr[a][0]]["model_family"] for a in auths}
    fams = sorted({a2m[a] for a in auths})
    FC = np.stack([E[np.concatenate([tr[a] for a in auths if a2m[a] == f])].mean(0) for f in fams])
    FC /= np.linalg.norm(FC, axis=1, keepdims=True)
    X = np.concatenate([te[a] for a in auths]); y = sum(([a] * len(te[a]) for a in auths), [])
    Sa, Sf = E[X] @ C.T, E[X] @ FC.T
    pa = [auths[j] for j in Sa.argmax(1)]
    pf = [fams[j] for j in Sf.argmax(1)]
    acc_a = float(np.mean([p == t for p, t in zip(pa, y)]))
    acc_f = float(np.mean([p == a2m[t] for p, t in zip(pf, y)]))
    ch_a, ch_f = 1 / len(auths), max(collections.Counter(a2m[a] for a in y).values()) / len(y)
    # author identification with the true model GIVEN -- the direct "beyond model" readout
    ok, tot, chance = 0, 0, []
    for f in fams:
        cand = [a for a in auths if a2m[a] == f]
        if len(cand) < 2: continue
        cix = [auths.index(a) for a in cand]
        m = np.array([a2m[t] == f for t in y])
        if not m.any(): continue
        pick = Sa[np.ix_(m, cix)].argmax(1)
        ok += int(sum(cand[j] == t for j, t in zip(pick, [t for t, k in zip(y, m) if k])))
        tot += int(m.sum()); chance.append((int(m.sum()), 1 / len(cand)))
    ch_wm = sum(n * c for n, c in chance) / tot if tot else None
    adj = lambda a, c: round((a - c) / (1 - c), 3)
    out = dict(n_authors=len(auths), n_test=len(y),
               author_acc=round(acc_a, 3), author_chance=round(ch_a, 4),
               author_acc_adj=adj(acc_a, ch_a),
               model_acc=round(acc_f, 3), model_chance=round(ch_f, 3),
               model_acc_adj=adj(acc_f, ch_f), n_families=len(fams),
               author_within_model_acc=round(ok / tot, 3) if tot else None,
               author_within_model_chance=round(ch_wm, 4) if tot else None,
               author_within_model_adj=adj(ok / tot, ch_wm) if tot else None,
               n_test_within_model=tot)
    log(f"  [identify] {out['n_authors']} authors, {out['n_test']} held-out second-half items: "
        f"author {out['author_acc']} (chance {out['author_chance']}, adj {out['author_acc_adj']}) | "
        f"model {out['model_acc']} (chance {out['model_chance']}, adj {out['model_acc_adj']}) | "
        f"author|model-known {out['author_within_model_acc']} "
        f"(chance {out['author_within_model_chance']}, adj {out['author_within_model_adj']})")
    return out

# ------------------------------------------------------------------ harness
def harness(E, rows, log, min_authors=6):
    """Does "model + harness = a few clusters per model" hold? Three readings per family:
      item-level  -- DISCO share of the DISCLOSED harness label over items, with the null
                     permuting harness at the AUTHOR level (harness is an author attribute, so an
                     item-level shuffle would be an invalid null).
      centroid    -- the same on author centroids, one point per citizen.
      modality    -- is the centroid cloud multimodal at all, disclosed label or not? A family
                     whose citizens split into modes that the harness string does not name is the
                     interesting case: structure exists, the stated scaffold is not what it is.
    """
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, r in enumerate(rows): by[r["model_family"]][r["author"]].append(i)
    out = []
    for fam, au in by.items():
        keep = {a: np.asarray(v) for a, v in au.items() if len(v) >= MIN_ITEMS}
        if len(keep) < min_authors: continue
        auths = sorted(keep)
        ahar = {a: collections.Counter(rows[i]["harness"] for i in keep[a]).most_common(1)[0][0]
                for a in auths}
        rec = dict(family=fam, n_authors=len(auths),
                   n_items=int(sum(len(v) for v in keep.values())),
                   harness_levels={k: v for k, v in collections.Counter(ahar.values()).most_common()})
        rng = np.random.default_rng(SEED)
        if len(set(ahar.values())) > 1:
            ix = np.concatenate([keep[a] for a in auths])
            Di = dmat(E[ix])
            owner = sum(([a] * len(keep[a]) for a in auths), [])
            N = len(ix); T = 0.5 * N * Di.mean()
            hl = [ahar[a] for a in owner]
            obs = (T - _within(Di, list(groups_of(hl).values()))) / T
            null = []
            for _ in range(PERMS):
                perm = dict(zip(auths, rng.permutation([ahar[a] for a in auths])))
                hp = [perm[a] for a in owner]
                null.append((T - _within(Di, list(groups_of(hp).values()))) / T)
            null = np.asarray(null)
            rec.update(eta2_harness_items=round(float(obs), 4),
                       harness_null=round(float(null.mean()), 4),
                       harness_excess=round(float(obs - null.mean()), 4),
                       harness_p=round(float(((null >= obs).sum() + 1) / (PERMS + 1)), 4))
        C = np.stack([E[keep[a]].mean(0) for a in auths]); C /= np.linalg.norm(C, axis=1, keepdims=True)
        sil, snull, sp, lab = _two_means_sil(C, rng)
        rec.update(sil_k2=round(sil, 3), sil_k2_null=round(snull, 3), sil_p=round(sp, 4))
        if lab is not None:
            modes = []
            for j in (0, 1):
                mem = [a for a, l in zip(auths, lab) if l == j]
                ch = [rows[i]["n_chars"] for a in mem for i in keep[a]]
                modes.append(dict(n_authors=len(mem), median_chars=int(np.median(ch)),
                                  harness={k: v for k, v in
                                           collections.Counter(ahar[a] for a in mem).most_common()},
                                  examples=sorted(mem, key=lambda a: -len(keep[a]))[:4]))
            rec["modes"] = modes
        out.append(rec)
    out.sort(key=lambda r: -r["n_authors"])
    for r in out:
        log(f"  [{r['family']}] {r['n_authors']} authors / {r['n_items']} items: "
            + (f"harness eta2={r['eta2_harness_items']} vs null {r['harness_null']} "
               f"(excess {r['harness_excess']}, p={r['harness_p']}) "
               if "eta2_harness_items" in r else "one disclosed harness level ")
            + f"| centroid 2-means silhouette {r['sil_k2']} vs unimodal null {r['sil_k2_null']} "
              f"(p={r['sil_p']})")
        for j, m in enumerate(r.get("modes", [])):
            log(f"       mode {j}: {m['n_authors']} authors, median {m['median_chars']} chars, "
                f"harness {m['harness']}, e.g. {', '.join(m['examples'])}")
    return out

def _two_means_sil(C, rng, iters=25):
    """Is the author-centroid cloud of one model family multimodal -- 'a few clusters per model'?
    Silhouette of the best 2-means split against a Gaussian null matched to the cloud's covariance
    (unimodal by construction). Run in the top principal subspace: with ~100 centroids in 1024
    dims every cloud looks like a simplex and the test has no power in the ambient space."""
    k = max(2, min(len(C) // 5, 20))
    X0 = C - C.mean(0)
    U, sv, _ = np.linalg.svd(X0, full_matrices=False)
    P = U[:, :k] * sv[:k]                                   # centroids in the top-k PC space
    floor = max(3, int(0.15 * len(C)))    # a lone outlier is not a mode; both obs and null
    def sil2(X, want_lab=False):          # are held to the same minimum cluster size
        D = dmat_euclid(X)
        best, blab = -1.0, None
        for _ in range(iters):
            c = X[rng.choice(len(X), 2, replace=False)]
            lab = None
            for _ in range(30):
                nl = ((X[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
                if len(set(nl.tolist())) < 2: break
                if lab is not None and (nl == lab).all(): lab = nl; break
                lab = nl
                c = np.stack([X[lab == j].mean(0) for j in (0, 1)])
            if lab is None or min(np.bincount(lab, minlength=2)) < floor: continue
            a = np.array([D[i, lab == lab[i]].sum() / max((lab == lab[i]).sum() - 1, 1)
                          for i in range(len(X))])
            b = np.array([D[i, lab != lab[i]].mean() for i in range(len(X))])
            sc = float(np.mean((b - a) / np.maximum(a, b)))
            if sc > best: best, blab = sc, lab
        return (best, blab) if want_lab else best
    obs, lab = sil2(P, want_lab=True)
    cov = (P.T @ P) / len(P)
    L = np.linalg.cholesky(cov + 1e-9 * np.eye(k))
    null = np.array([sil2(rng.standard_normal((len(P), k)) @ L.T) for _ in range(20)])
    return obs, float(null.mean()), float(((null >= obs).sum() + 1) / (len(null) + 1)), lab

def dmat_euclid(X):
    d = np.sqrt(np.maximum(((X[:, None, :] - X[None]) ** 2).sum(-1), 0.0))
    np.fill_diagonal(d, 0.0)
    return d

# ------------------------------------------------------------------ idea-level positive control
def venue_world_control(E, rows, log):
    """claimify compresses every item to one Qwen/Gemma-voiced sentence; it will DEFLATE author
    signal by construction, so a null at claim level is uninterpretable without proof that a
    known-real distinction still survives the same normalization. VENUE- vs WORLD-directed
    allocation labels are that proof -- they are already computed for these exact 9,217 claims."""
    lab = json.load(open(S / "allocation_labels_agentcur.json"))["agentcur"]
    ix = np.array([i for i, r in enumerate(rows) if lab[r["claim_idx"]] in ("V", "W")])
    rng = np.random.default_rng(SEED)
    ix = rng.choice(ix, min(3000, len(ix)), replace=False)
    y = [lab[rows[i]["claim_idx"]] for i in ix]
    D = dmat(E[ix])
    N = len(ix); T = 0.5 * N * D.mean()
    obs = (T - _within(D, list(groups_of(y).values()))) / T
    null = np.array([(T - _within(D, list(groups_of(rng.permutation(y)).values()))) / T
                     for _ in range(PERMS)])
    # a legible companion to eta2: nearest-centroid V/W accuracy, 2-fold, so the control reads
    # as "the normalization preserved a distinction we know is there", not as a magnitude.
    half = len(ix) // 2
    acc = []
    for tr, te in ((slice(None, half), slice(half, None)), (slice(half, None), slice(None, half))):
        yt = np.asarray(y)
        C = np.stack([E[ix[tr]][yt[tr] == c].mean(0) for c in ("V", "W")])
        C /= np.linalg.norm(C, axis=1, keepdims=True)
        pred = np.array(["V", "W"])[(E[ix[te]] @ C.T).argmax(1)]
        acc.append(float((pred == yt[te]).mean()))
    maj = max((np.asarray(y) == c).mean() for c in ("V", "W"))
    out = dict(n=int(N), eta2_venue_world=round(float(obs), 4),
               vw_acc=round(float(np.mean(acc)), 3), vw_majority=round(float(maj), 3),
               null_mean=round(float(null.mean()), 4),
               excess=round(float(obs - null.mean()), 4),
               z=round(float((obs - null.mean()) / null.std()), 1))
    log(f"  [positive control] VENUE vs WORLD on the same claims: eta2={out['eta2_venue_world']} "
        f"vs null {out['null_mean']} (excess {out['excess']}, z={out['z']}); "
        f"nearest-centroid accuracy {out['vw_acc']} vs majority {out['vw_majority']}")
    return out

# ------------------------------------------------------------------ driver
def main():
    items = json.load(open(S / "identity_items.json"))
    lines = []
    def log(s):
        print(s, flush=True); lines.append(s)
    res = {"params": dict(min_items=MIN_ITEMS, cap=CAP, draws=DRAWS, perms=PERMS,
                          min_switcher_arm=MIN_SW, seed=SEED), "views": {}}
    claim_rows = [r for r in items if "claim_idx" in r]
    # lexical_matched runs the AS-WRITTEN embeddings over exactly the rows the claim cache covers
    # (Aug 5-14, 9,217 items, 115 qualifying authors). Without it the lexical-vs-idea contrast
    # would confound normalization with a different corpus window and a different author set.
    VIEWS = [("lexical", "lexical", items, "idx"),
             ("lexical_matched", "lexical", claim_rows, "idx"),
             ("claim_qwen", "claim_qwen", claim_rows, "claim_idx"),
             ("claim_gemma", "claim_gemma", claim_rows, "claim_idx")]
    for tag, _ in [("bge", 0), ("gte", 0)]:
        for view, embview, rows, ikey in VIEWS:
            f = S / f"identity_emb_{embview}_{tag}.npy"
            if not f.exists():
                log(f"MISSING {f.name}, skipped"); continue
            E = np.load(f)[[r[ikey] for r in rows]]
            key = f"{view}/{tag}"
            log(f"== {key}  ({len(rows)} rows)")
            R = {"headline": headline(E, rows, "raw", log)}
            R["thread"] = block_control(E, rows, lambda r: (r["thread"], r["model_family"]),
                                        "thread x model", log)
            R["day"] = block_control(E, rows, lambda r: (int(r["ts"] // 86400), r["model_family"]),
                                     "day x model", log)
            R["identify"] = identify(E, rows, log)
            R["switchers"] = switchers(E, rows, log)
            Er = residualize(E, [r["n_chars"] for r in rows])
            R["headline_lenresid"] = headline(Er, rows, "length-residualized", log)
            R["identify_lenresid"] = identify(Er, rows, log)
            keep = drop_bursts(E, rows)
            log(f"  [nodup] dropped {int((~keep).sum())} near-duplicate items "
                f"({100*(~keep).mean():.1f}%)")
            kr = [r for r, k in zip(rows, keep) if k]
            R["nodup_dropped"] = int((~keep).sum())
            R["headline_nodup"] = headline(E[keep], kr, "burst-filtered", log)
            if tag == "bge":
                R["harness"] = harness(E, rows, log)
            if view.startswith("claim"):
                R["positive_control"] = venue_world_control(E, rows, log)
            res["views"][key] = R
    res["log"] = lines
    json.dump(res, open(S / "identity_stats.json", "w"), indent=1)
    (REPO / "results" / "identity").mkdir(parents=True, exist_ok=True)
    json.dump(res, open(REPO / "results" / "identity" / "results.json", "w"), indent=1)
    print(f"saved identity_stats.json")

if __name__ == "__main__":
    main()
