#!/usr/bin/env python3
"""Emit results/lemmy_baseline/results.json — every load-bearing statistic in the lemmy_baseline
report, recomputed from the label and corpus files.

WHY THIS EXISTS
A cold review could not reproduce the founding-premium table and correctly observed that no
committed code computed it: the shares came from allocation_run.py but the ratios, premiums,
residuals, retention intervals, gold intervals and perplexity interval were session code. This
script is the arbiter. Every number in the report should be traceable to a key it emits.

CONVENTIONS
  * Intervals are AUTHOR-CLUSTERED bootstrap unless noted: authors are resampled with replacement
    within each cell, all of that author's items travel together. Sampling-only intervals are
    marked `item_bootstrap`.
  * Ratios take null = 1; differences take null = 0. `spans_null` is emitted per statistic.
  * The cross-classifier ENVELOPE (union of the Qwen and Gemma intervals) is the honest interval
    for any agent-vs-lemmy comparison — the within-classifier intervals are conditional on the
    classifier, and classifier choice is the dominant uncertainty (kappa 0.428 on the agent pool).
  * Seeds are fixed; reruns are deterministic.

Usage:  MEMETIC_WORKDIR=... python3 analysis/lemmy_baseline_stats.py [--draws 3000]
"""
import argparse, datetime as dt, json, os, re
from collections import defaultdict
from pathlib import Path
import numpy as np

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
REPO = Path("/home/dan/personal/memetic")
OUT = REPO / "results/lemmy_baseline/results.json"

A0 = dt.datetime(2023, 6, 9, tzinfo=dt.timezone.utc).timestamp()          # exodus arrival clock
T0 = dt.datetime(2023, 6, 1, 7, 1, 46, tzinfo=dt.timezone.utc).timestamp()  # instance creation
L0 = dt.datetime(2023, 6, 22, 12, tzinfo=dt.timezone.utc).timestamp()     # settled window start
W82 = 8.2 * 86400


def jload(p):
    return json.load(open(p))


# ---------------------------------------------------------------- data
def load():
    d = {}
    d["C"] = [r for r in jload(S / "baseline_corpora_lemmy.json")["lemmy"] if len(r["text"]) >= 20]
    d["lm"] = jload(S / "allocation_agree_pairs_lemmy_full.json")
    d["ag"] = jload(S / "allocation_agree_pairs_agentcur.json")
    d["AR"] = jload(S / "agent_rows_aligned.json")
    items = []
    for f in (REPO / "data/posts").glob("*.json"):
        th = jload(f); p = th["post"]
        t = p.get("created_at", 0); t = t / 1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc / 1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip()))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    d["AL"] = [len(x) for _, _, x in items if len(x) >= 20][:len(d["AR"])]
    return d


# ---------------------------------------------------------------- bootstrap
def cell(pairs, key, authorfn, sel):
    """-> (indicator array, author array) over items where BOTH classifiers produced a label."""
    lab = {p["idx"]: p[key] for p in pairs if p["gemma"] is not None}
    idx = [i for i in lab if sel(i)]
    return np.array([lab[i] == "V" for i in idx]), np.array([authorfn(i) for i in idx])


def boot(cells, fn, draws, seed):
    rng = np.random.default_rng(seed)
    pre = []
    for y, a in cells:
        uq, inv = np.unique(a, return_inverse=True)
        pre.append((y, [np.where(inv == k)[0] for k in range(len(uq))]))
    out = np.empty(draws)
    for j in range(draws):
        ms = [float(y[np.concatenate([by[i] for i in rng.integers(0, len(by), len(by))])].mean())
              for y, by in pre]
        out[j] = fn(ms)
    return out


def stat(point, bs, null):
    lo, hi = (float(x) for x in np.percentile(bs, [2.5, 97.5]))
    return {"point": round(float(point), 4), "ci95": [round(lo, 4), round(hi, 4)],
            "null": null, "spans_null": bool(lo <= null <= hi)}


def envelope(a, b):
    lo = min(a["ci95"][0], b["ci95"][0]); hi = max(a["ci95"][1], b["ci95"][1])
    return {"ci95": [round(lo, 4), round(hi, 4)], "null": a["null"],
            "spans_null": bool(lo <= a["null"] <= hi)}


def main(draws):
    d = load(); C, lm, ag, AR, AL = d["C"], d["lm"], d["ag"], d["AR"], d["AL"]
    la = lambda i: C[i]["author"]; aa = lambda i: AR[i][1]
    res = {"note": "Emitted by analysis/lemmy_baseline_stats.py. Author-clustered bootstrap; "
                   "ratios null=1, differences null=0; envelope = union of Qwen and Gemma intervals.",
           "draws": draws, "generated_at": None}

    # ---- corpus ----
    res["corpus"] = {
        "items": len(jload(S / "baseline_corpora_lemmy.json")["lemmy"]),
        "ge20char": len(C),
        "authors": len({r["author"] for r in C}),
        "communities_present": len({r["group"] for r in C}),
        "median_chars_ge20": int(np.median([len(r["text"]) for r in C])),
        "median_chars_topic": int(np.median([len(r["text"]) for r in C if r["tier"] == "topic"])),
        "median_chars_agent": int(np.median(AL)),
        "pct_local": round(100 * float(np.mean([r["local"] for r in C])), 1),
    }
    st = jload(S / "lemmy/state.json")
    res["corpus"]["pagination_caps"] = st.get("truncated", [])
    last = defaultdict(str)
    for r in C:
        k = r["group"]
        last[k] = max(last[k], dt.datetime.fromtimestamp(r["ts"], dt.timezone.utc).isoformat())
    res["corpus"]["communities_ending_early"] = sorted(k for k, v in last.items() if v < "2023-06-29")

    # ---- shares, ratios, premiums ----
    res["allocation"] = {}
    for cut, ctag in ((0, "all_items"), (400, "ge400ch")):
        blk = {}
        for norm in ("qwen", "gemma"):
            A = cell(ag, norm, aa, lambda i, c=cut: AL[i] >= c)
            LA = cell(lm, norm, la, lambda i, c=cut: len(C[i]["text"]) >= c)
            TT = cell(lm, norm, la, lambda i, c=cut: C[i]["tier"] == "topic" and len(C[i]["text"]) >= c)
            MT = cell(lm, norm, la, lambda i, c=cut: C[i]["tier"] == "meta" and len(C[i]["text"]) >= c)
            F = cell(lm, norm, la, lambda i, c=cut: C[i]["tier"] == "topic" and len(C[i]["text"]) >= c
                     and A0 <= C[i]["ts"] < A0 + W82)
            SV = cell(lm, norm, la, lambda i, c=cut: C[i]["tier"] == "topic" and len(C[i]["text"]) >= c
                      and L0 <= C[i]["ts"] < L0 + W82)
            FA = cell(lm, norm, la, lambda i, c=cut: len(C[i]["text"]) >= c and A0 <= C[i]["ts"] < A0 + W82)
            SA = cell(lm, norm, la, lambda i, c=cut: len(C[i]["text"]) >= c and L0 <= C[i]["ts"] < L0 + W82)
            pa, pl, pt, pm, pf, ps, pfa, psa = [float(x[0].mean()) for x in (A, LA, TT, MT, F, SV, FA, SA)]
            e = {
                "n": {"agent": len(A[0]), "lemmy_all": len(LA[0]), "topic": len(TT[0]),
                      "meta": len(MT[0]), "founding_topic": len(F[0]), "settled_topic": len(SV[0]),
                      "founding_all": len(FA[0]), "settled_all": len(SA[0])},
                "share_agent": stat(pa, boot([A], lambda m: m[0], draws, 1), -1),
                "share_lemmy_all": stat(pl, boot([LA], lambda m: m[0], draws, 2), -1),
                "share_lemmy_topic": stat(pt, boot([TT], lambda m: m[0], draws, 3), -1),
                "share_lemmy_meta": stat(pm, boot([MT], lambda m: m[0], draws, 4), -1),
                "ratio_agent_over_lemmy_all": stat(pa / pl, boot([A, LA], lambda m: m[0] / m[1], draws, 5), 1.0),
                "ratio_agent_over_topic": stat(pa / pt, boot([A, TT], lambda m: m[0] / m[1], draws, 6), 1.0),
                "founding_premium_topic": stat(pf - ps, boot([F, SV], lambda m: m[0] - m[1], draws, 7), 0.0),
                "founding_ratio_topic": stat(pf / ps, boot([F, SV], lambda m: m[0] / m[1], draws, 8), 1.0),
                "founding_premium_all": stat(pfa - psa, boot([FA, SA], lambda m: m[0] - m[1], draws, 9), 0.0),
                "needed_agent_over_settled_topic": stat(pa / ps, boot([A, SV], lambda m: m[0] / m[1], draws, 10), 1.0),
                "residual_topic": stat((pa / ps) / (pf / ps), boot([A, F], lambda m: m[0] / m[1], draws, 11), 1.0),
            }
            blk[norm] = e
        for k in ("ratio_agent_over_lemmy_all", "ratio_agent_over_topic", "residual_topic",
                  "founding_premium_topic", "founding_ratio_topic", "founding_premium_all"):
            blk.setdefault("envelope", {})[k] = envelope(blk["qwen"][k], blk["gemma"][k])
        res["allocation"][ctag] = blk

    # ---- window-matched whole-platform, both clocks ----
    span = max(t for t, _ in AR) - min(t for t, _ in AR)
    res["window_matched"] = {"agent_span_days": round(span / 86400, 2)}
    # Both cuts are emitted per clock. The length cut previously existed only across the full 30
    # days, so a "06-09 clock, >=400ch" cell had no emitter and could not be refreshed with the
    # corpus -- and pairing it with an all-items windowed number compares two different frames.
    # Cutting inside the window keeps the frame fixed while length varies.
    for clock, cname in ((T0, "clock_06_01_instance_creation"), (A0, "clock_06_09_arrival")):
        blk = {}
        for cut, ctag, sd in ((0, None, 12), (400, "ge400ch", 14)):
            sub = {}
            for norm in ("qwen", "gemma"):
                A = cell(ag, norm, aa, lambda i, c=cut: AL[i] >= c)
                L = cell(lm, norm, la, lambda i, k=clock, c=cut:
                         k <= C[i]["ts"] < k + span and len(C[i]["text"]) >= c)
                if len(L[0]) < 200:
                    continue
                pa, pl = float(A[0].mean()), float(L[0].mean())
                sub[norm] = {"n_lemmy": len(L[0]), "n_agent": len(A[0]),
                             "share_lemmy": stat(pl, boot([L], lambda m: m[0], draws, sd), -1),
                             "ratio_agent_over_lemmy": stat(pa / pl, boot([A, L], lambda m: m[0] / m[1],
                                                                          draws, sd + 1), 1.0)}
            if "qwen" in sub and "gemma" in sub:
                sub["envelope"] = {"ratio_agent_over_lemmy":
                                   envelope(sub["qwen"]["ratio_agent_over_lemmy"],
                                            sub["gemma"]["ratio_agent_over_lemmy"])}
            if ctag is None:
                blk.update(sub)          # all-items keys stay at the top level (schema unchanged)
            elif sub:
                blk[ctag] = sub
        res["window_matched"][cname] = blk

    # ---- per-community shares: the tier-separation evidence, previously computed by hand ----
    # Point estimates only; the tier-level aggregates above carry the intervals. Emitted so the
    # report's c/newcommunities-vs-c/cat cells refresh with the corpus instead of being retyped.
    PC_MIN_N = 100
    labs = {n: {p["idx"]: p[n] for p in lm if p["gemma"] is not None} for n in ("qwen", "gemma")}
    bycom = defaultdict(list)
    for i in labs["qwen"]:
        bycom[C[i]["group"]].append(i)
    pc = {}
    for g, idxs in bycom.items():
        if len(idxs) < PC_MIN_N:
            continue
        pc[g] = {"n": len(idxs), "tier": C[idxs[0]]["tier"],
                 "qwen_share": round(float(np.mean([labs["qwen"][i] == "V" for i in idxs])), 4),
                 "gemma_share": round(float(np.mean([labs["gemma"][i] == "V" for i in idxs])), 4)}
    res["per_community"] = {
        "note": f"point estimates, communities with >={PC_MIN_N} doubly-labelled items; "
                "intervals are reported at tier level, not per community",
        "min_n": PC_MIN_N,
        "communities": dict(sorted(pc.items(), key=lambda kv: -kv[1]["qwen_share"]))}

    # ---- venue share by length band, whole platform and per tier ----
    # The register caveat rests on these: the whole-platform series is non-monotone while the
    # topic tier declines and the meta tier rises. Previously computed by hand.
    BANDS = ((20, 50), (50, 100), (100, 200), (200, 400), (400, 800), (800, 10 ** 6))
    res["length_bands"] = {"note": "venue share by item length; point estimates"}
    for norm in ("qwen", "gemma"):
        blk = {}
        for lo, hi in BANDS:
            row = {}
            for tag, tier in (("all", None), ("topic", "topic"), ("meta", "meta")):
                y, _ = cell(lm, norm, la, lambda i, l=lo, h=hi, t=tier:
                            l <= len(C[i]["text"]) < h and (t is None or C[i]["tier"] == t))
                row[tag] = {"share": round(float(y.mean()), 4), "n": int(len(y))} if len(y) else None
            blk[f"{lo}-{hi if hi < 10 ** 6 else '+'}"] = row
        res["length_bands"][norm] = blk

    # ---- cross-family agreement + context starvation ----
    def kappa(pp):
        a = np.mean([x == y for x, y in pp])
        pv = np.mean([x == "V" for x, _ in pp]); gv = np.mean([y == "V" for _, y in pp])
        pe = pv * gv + (1 - pv) * (1 - gv)
        return (a - pe) / (1 - pe) if pe < 1 else float("nan"), float(a)
    res["cross_family"] = {}
    for nm, pairs in (("lemmy", lm), ("agent", ag)):
        pp = [(p["qwen"], p["gemma"]) for p in pairs if p["gemma"] is not None and p["qwen"] in "VW"]
        k, a = kappa(pp)
        res["cross_family"][nm] = {"kappa": round(k, 4), "raw_agreement": round(a, 4), "n": len(pp)}
    ctx = {}
    labp = {p["idx"]: (p["qwen"], p["gemma"]) for p in lm if p["gemma"] is not None}
    for lo, hi in ((20, 50), (50, 100), (100, 200), (200, 400), (400, 800), (800, 10 ** 6)):
        row = {}
        for kind in ("post", "comment"):
            pp = [labp[i] for i in labp if C[i]["kind"] == kind and lo <= len(C[i]["text"]) < hi]
            if len(pp) >= 40:
                k, _ = kappa(pp)
                row["root" if kind == "post" else "reply"] = {"kappa": round(k, 4), "n": len(pp)}
        ctx[f"{lo}-{hi if hi < 10**6 else '+'}"] = row
    res["context_starvation_kappa"] = ctx

    # ---- gold sample ----
    gp = S / "gold2_matrix.json"
    if gp.exists():
        R = jload(gp); rng = np.random.default_rng(0)
        cons = [n for n in R if R[n]["dan"] in "VW" and R[n]["fable"] in "VW" and R[n]["dan"] == R[n]["fable"]
                and R[n]["qwen"] in "VW" and R[n]["gemma"] in "VW"]
        dq = np.array([R[n]["qwen"] == R[n]["dan"] for n in cons])
        dg = np.array([R[n]["gemma"] == R[n]["dan"] for n in cons])
        idx = [rng.integers(0, len(cons), len(cons)) for _ in range(draws)]
        res["gold"] = {"n_items": len(R), "consensus_n": len(cons),
                       "qwen_accuracy": stat(dq.mean(), np.array([dq[i].mean() for i in idx]), -1),
                       "gemma_accuracy": stat(dg.mean(), np.array([dg[i].mean() for i in idx]), -1),
                       "accuracy_difference": stat(dq.mean() - dg.mean(),
                                                   np.array([dq[i].mean() - dg[i].mean() for i in idx]), 0.0)}
        for a, b in (("dan", "qwen"), ("dan", "gemma"), ("dan", "fable")):
            pp = [(R[n][a], R[n][b]) for n in R if R[n][a] in "VW" and R[n][b] in "VW"]
            k, _ = kappa(pp)
            bs = np.array([kappa([pp[i] for i in rng.integers(0, len(pp), len(pp))])[0] for _ in range(1000)])
            res["gold"][f"kappa_{a}_{b}"] = stat(k, bs[~np.isnan(bs)], 0.0)

    # ---- retention ----
    H = 3600_000
    def at_corpus(f, fam):
        t = defaultdict(list)
        for r in jload(S / f)[fam]:
            t[r["author"]].append(int(r["ts"]) * 1000)
        return {a: sorted(v) for a, v in t.items()}
    def at_forum(dirp, cutoff_ms=None):
        """cutoff_ms pins the agent pool to a vintage. data/posts is a LIVE directory that grows
        with every pull, so without a cutoff this cell silently re-computes on a newer corpus than
        the one allocation is aligned to (agent_rows_aligned.json) and drifts between runs."""
        t = defaultdict(list)
        for f in Path(dirp).glob("*.json"):
            th = jload(f); p = th["post"]
            for a_, ts_ in [(p["author"], p["created_at"])] + \
                           [(c["author"], c["created_at"]) for c in th.get("comments", [])]:
                if cutoff_ms is None or ts_ <= cutoff_ms:
                    t[a_].append(ts_)
        return {a: sorted(v) for a, v in t.items() if v}
    def flags(atd, Wh=48):
        Wm = Wh * H; end = max(x for v in atd.values() for x in v); o = []
        for a, ts in atd.items():
            if ts[0] > end - Wm:
                continue
            first = ts[0]; win = [x for x in ts if first <= x < first + Wm]
            o.append(len({int((x - first) // (6 * H)) for x in win}) >= 2)
        return np.array(o)
    agent_cutoff_ms = int(max(t for t, _ in AR) * 1000)   # last item of the aligned pull
    pools = {"agent": at_forum(REPO / "data/posts", agent_cutoff_ms),
             "lemmy": at_corpus("baseline_corpora_lemmy.json", "lemmy"),
             "lisp": at_corpus("baseline_corpora.json", "lisp"),
             "forth": at_corpus("baseline_corpora2.json", "forth")}
    fl = {k: flags(v) for k, v in pools.items()}
    rng = np.random.default_rng(0)
    res["retention_48h"] = {"note": "item-level author bootstrap (one row per author). "
                                    "lisp/forth are CAPTURE-BOUNDED: UTZOO is a partial feed and "
                                    "retention.py flags them incomplete. agent 'churn' is operator "
                                    "scheduling, not engagement (see retention.py docstring). "
                                    "The agent pool is pinned to the aligned pull's last timestamp "
                                    "so this cell does not drift as data/posts grows."}
    for k, v in fl.items():
        res["retention_48h"][k] = stat(v.mean(), np.array([v[rng.integers(0, len(v), len(v))].mean()
                                                           for _ in range(draws)]), -1)
        res["retention_48h"][k]["n_qualifying"] = int(len(v))
    for k in ("lemmy", "lisp", "forth"):
        a, b = fl["agent"], fl[k]
        bs = np.array([a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean()
                       for _ in range(draws)])
        res["retention_48h"][f"agent_minus_{k}"] = stat(fl["agent"].mean() - fl[k].mean(), bs, 0.0)

    # ---- perplexity ----
    import csv
    def ppl(path, limit=None):
        rows = []
        with open(path) as f:
            for r in csv.DictReader(f):
                try:
                    rows.append((r["author"], float(r["cond_bits_per_tok"]),
                                 float(r["self_bits_per_tok"]), int(r["tokens"])))
                except Exception:
                    continue
        return rows[:limit] if limit else rows
    def pratio(rows):
        return sum(c * t for _, c, _, t in rows) / sum(s * t for _, _, s, t in rows)
    def pboot(rows, seed):
        rng = np.random.default_rng(seed); by = defaultdict(list)
        for r in rows:
            by[r[0]].append(r)
        keys = list(by)
        return np.array([pratio([x for i in rng.integers(0, len(keys), len(keys)) for x in by[keys[i]]])
                         for _ in range(min(draws, 2000))])
    pa_ = REPO / "results/perplexity/metrics.csv"; pl_ = S / "lemmy/perplexity/metrics.csv"
    if pa_.exists() and pl_.exists():
        A_ = ppl(pa_); L_ = ppl(pl_, len(A_)); Lall = ppl(pl_)
        res["perplexity"] = {
            "note": "corpus novelty = sum(cond_bits)/sum(self_bits). The 3072-token conditioning "
                    "window SATURATES at item ~62, so corpus depth cannot affect it; the "
                    "full-corpus/prefix difference is composition, not a depth artifact.",
            "agent": stat(pratio(A_), pboot(A_, 1), -1),
            "lemmy_founding_matched": stat(pratio(L_), pboot(L_, 2), -1),
            "lemmy_all": stat(pratio(Lall), pboot(Lall, 3), -1),
            "difference_agent_minus_lemmy_matched":
                stat(pratio(A_) - pratio(L_), pboot(A_, 4) - pboot(L_, 5), 0.0)}

    # ---- long-window perplexity (15,000-token conditioning) ----
    # The short window above conditions on ~8 items -- minutes of concurrent thread-siblings at
    # these velocities. This is the window that separates the corpora, so it needs an emitter of
    # its own rather than living in session code. Both pools are truncated to the shorter of the
    # two so the comparison is matched; the agent run scores 2,890 items and lemmy 2,776.
    pal = REPO / "results/perplexity_long/metrics.csv"; pll = S / "lemmy/perplexity_long/metrics.csv"
    if pal.exists() and pll.exists():
        Afull, Lfull = ppl(pal), ppl(pll)
        n_ = min(len(Afull), len(Lfull))
        A2, L2 = Afull[:n_], Lfull[:n_]
        res["perplexity_long"] = {
            "note": "15,000-token rolling history via analysis/perplexity_stream.py (agent run: "
                    "results/perplexity_long, 15000/18000). Matched on TOKEN BUDGET, not time or "
                    "item count: at 15k tokens lemmy's median history is ~8.5h against the agent "
                    "pool's ~1.1h, and more history lowers novelty, so the asymmetry favours lemmy "
                    "and the difference below is a lower bound on the gap.",
            "n_matched": n_, "n_agent_scored": len(Afull), "n_lemmy_scored": len(Lfull),
            "agent": stat(pratio(A2), pboot(A2, 6), -1),
            "lemmy_founding": stat(pratio(L2), pboot(L2, 7), -1),
            "difference_agent_minus_lemmy":
                stat(pratio(A2) - pratio(L2), pboot(A2, 8) - pboot(L2, 9), 0.0)}

    # ---- venue share by federation origin ----
    # 42% of the corpus is federated in from other instances, and the square has no analogue for
    # that. If locally-authored items carry a different venue share, the comparison inherits it.
    res["local_split"] = {"note": "lemmy venue share split by the record's `local` flag; the agent "
                                  "pool has no federation analogue, so this is a lemmy-side control"}
    for norm in ("qwen", "gemma"):
        blk = {}
        for tag, want in (("local", True), ("federated", False)):
            y, a_ = cell(lm, norm, la, lambda i, w=want: bool(C[i]["local"]) is w)
            blk[tag] = stat(float(y.mean()), boot([(y, a_)], lambda m: m[0], draws, 16), -1)
            blk[tag]["n"] = int(len(y))
        yl, al_ = cell(lm, norm, la, lambda i: bool(C[i]["local"]))
        yf, af_ = cell(lm, norm, la, lambda i: not bool(C[i]["local"]))
        blk["difference_local_minus_federated"] = stat(
            float(yl.mean()) - float(yf.mean()),
            boot([(yl, al_), (yf, af_)], lambda m: m[0] - m[1], draws, 17), 0.0)
        res["local_split"][norm] = blk

    # ---- optional: Usenet platform-governance pools ----
    mp = S / "allocation_results_meta.json"; ma = S / "allocation_agree_meta.json"
    if mp.exists():
        res["usenet_platform_governance"] = {"qwen": jload(mp).get("shares", {})}
        if ma.exists():
            g = jload(ma)
            res["usenet_platform_governance"]["cross_family"] = {
                "pooled_n": g["n"], "raw_agreement": g["raw_agreement"], "kappa": g["cohens_kappa"],
                "per_pool": g["per_pool_shares"], "per_pool_kappa": g.get("per_pool_kappa", {})}

    res["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")
    spans = []
    def walk(o, path=""):
        if isinstance(o, dict):
            if o.get("spans_null"):
                spans.append(path)
            for k, v in o.items():
                walk(v, f"{path}.{k}" if path else k)
    walk(res)
    print(f"\n{len(spans)} statistics span their null:")
    for s_ in spans:
        print("   " + s_)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=3000)
    main(ap.parse_args().draws)
