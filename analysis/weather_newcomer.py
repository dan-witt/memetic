#!/usr/bin/env python3
"""Newcomer refresh cells — the per-issue window construction, and a POOLED-WINDOW fallback.

The published cells ask whether the claims of authors who arrived during the issue window sit
anywhere the incumbent cloud does not already cover. They need enough newcomer text to be
measurable: m >= 100 newcomer items for the Vendi-based parity/union cells (a spectrum needs
items), m >= 50 newcomer / >= 150 incumbent for the nearest-incumbent-distance cell (a median
against a permutation null that widens as m shrinks, so it stays interpretable lower).

WHY A POOLED FALLBACK EXISTS. Recruitment fell from 224 new authors on the founding day to single
digits. At ~6-8 new authors a day, a one-day issue window no longer carries enough newcomer text
to run the instrument at all: issue #6 measured 42 newcomer items and skipped every cell, issue #7
measured 9. Issue #6 pre-registered the replacement rather than reporting a second skip — pool the
window over the last K issues so the cell is measurable again, at the cost of resolution.

The pooled window is the CONTIGUOUS interval [start of the (K-1)-th previous issue's window,
cutoff), not the union of K disjoint issue windows. Two reasons. HISTORICALLY (issues #1-#8) each
window started at the previous issue's PULL, so the union left holes -- the items between an
issue's cutoff and its pull entered no issue's window ever (issue #6 measured 228 such items on
08-18) -- and those holes sat at a fixed time of day, which would have made the pooled sample
diurnally non-random on top of being gappy. Issue #9 moved the window start to the previous
issue's CUTOFF, which closes that gap prospectively; the pooled window's own start is still
inherited from a published pull-based start, so the pooled series straddles the change. The second
reason is unaffected: a contiguous interval is the honest description of what is being measured --
the last several days, not K stitched samples.

NEWCOMER is defined against the pooled start, not the issue window: an author whose first item in
the whole corpus falls at or after the pooled start. So the pooled cell answers "do the authors who
arrived over the last N days bring claims the incumbents were not already making?" -- a coarser
question than the per-issue cell, over a longer arrival window, and it is NOT comparable to the
per-issue cells published in issues #1-#5. It starts its own series.

Usage: MEMETIC_WORKDIR=... WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_newcomer.py [K]
"""
import json, os, sys, datetime as dt
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_nn_refresh as NNR   # matched-pool NN construction, single source of truth
import weather_issue_boundary as IB   # issue/window boundaries, single source of truth

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
W = Path("/home/dan/personal/memetic/results/weather")
VENDI_FLOOR, NN_FLOOR = 100, 50   # identical to the per-issue floors in weather_gpu.py
NN_CTRL_DRAWS = int(os.environ.get("WEATHER_NN_CTRL_DRAWS", "100"))


def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))


def split(NEW, start_ts):
    """-> (newcomer item indices, incumbent item indices) for items at or after start_ts.

    NEW is the cutoff-filtered item stream [(t, key, text, author)]; first-appearance is taken
    over the WHOLE stream, so an author who posted before start_ts is an incumbent even if their
    only in-window item is their second ever.

    Boundary is INCLUSIVE (>=) to match weather_gpu.py's win_idx, because from issue #9 the window
    starts at the previous issue's cutoff -- an exact midnight timestamp, which a strict > would
    drop. Cutoffs are exclusive upper bounds and window starts are inclusive lower bounds, so an
    item is in exactly one issue's window.
    """
    first = {}
    for t, k, x, a in NEW:
        if a not in first: first[a] = t
    idx = [i for i, (t, k, x, a) in enumerate(NEW) if t >= start_ts]
    return ([i for i in idx if first[NEW[i][3]] >= start_ts],
            [i for i in idx if first[NEW[i][3]] < start_ts])


def cells(Ea, idx_newc, idx_inc, rng=None):
    """The refresh cells over an arbitrary newcomer/incumbent split of bge embeddings Ea.

    Shared by the per-issue window cell (weather_gpu.py) and the pooled fallback so the two
    constructions cannot drift apart. Returns the skip strings rather than raising when a floor
    is not met -- a skip is a reading about recruitment, not a pipeline gap.
    """
    rng = rng if rng is not None else np.random.default_rng(0)
    out = {"counts": {"newcomer_items": len(idx_newc), "incumbent_items": len(idx_inc)}}
    out.update(vendi_cells(Ea, idx_newc, idx_inc, rng))
    if len(idx_newc) >= NN_FLOOR and len(idx_inc) >= 3 * NN_FLOOR:
        En, Ei = Ea[np.array(idx_newc)], Ea[np.array(idx_inc)]
        out["nn_distance_matched"] = dict(
            NNR.matched_nn(En, Ei), below_standing_vendi_floor=len(idx_newc) < VENDI_FLOOR,
            read="same reference pool R, same size, disjoint from every query set; delta > null"
                 " = newcomer claims sit farther from the incumbent cloud than incumbents do from"
                 " each other. Null centres on 0 by construction; see weather_nn_validate.py.")
        out["nn_distance_legacy_asymmetric"] = NNR.legacy_asymmetric(En, Ei)
    else:
        out["nn_cell_skipped"] = (f"newcomer_items={len(idx_newc)} / incumbent_items={len(idx_inc)} "
                                  f"against the standing floors m>={NN_FLOOR} newcomer and "
                                  f">={3 * NN_FLOOR} incumbent; not computed")
    return out


def vendi_cells(Ea, idx_newc, idx_inc, rng=None):
    """Just the two Vendi-ratio cells. Split out of cells() so the m-matched control can repeat
    them over outer subsamples without also re-running the 500-draw NN cell each time."""
    rng = rng if rng is not None else np.random.default_rng(0)
    out = {}
    if len(idx_newc) >= VENDI_FLOOR and len(idx_inc) >= VENDI_FLOOR:
        mm = int(0.8 * min(len(idx_newc), len(idx_inc)))
        rs = [vendi(Ea[np.array(idx_newc)][rng.choice(len(idx_newc), mm, replace=False)]) /
              vendi(Ea[np.array(idx_inc)][rng.choice(len(idx_inc), mm, replace=False)]) for _ in range(40)]
        out["within_pool_parity"] = {"m": mm, "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        mm2 = min(len(idx_newc), len(idx_inc))
        rs_u, rs_i = [], []
        for _ in range(40):
            inc = np.array(idx_inc)[rng.choice(len(idx_inc), mm2, replace=False)]
            nwc = np.array(idx_newc)[rng.choice(len(idx_newc), mm2 // 2, replace=False)]
            union = np.concatenate([inc[:mm2 - len(nwc)], nwc])
            rs_u.append(vendi(Ea[union])); rs_i.append(vendi(Ea[inc]))
        out["union_over_incumbent"] = {"m": mm2,
            "band": [round(float(np.percentile(np.array(rs_u) / np.array(rs_i), p)), 3) for p in (50, 5, 95)],
            "read": ">1 = newcomer claims add effective distinct content beyond incumbents'"}
    else:
        out["vendi_cells_skipped"] = (f"newcomer_items={len(idx_newc)} below the standing "
                                      f"m>={VENDI_FLOOR} floor for the Vendi-based parity/union cells; not computed")
    return out


published_issues_before = IB.published_issues_before   # moved to weather_issue_boundary


def pooled_start(cutoff_str, K=3):
    """-> (start epoch, provenance dict) for a window spanning the last K issue windows.

    The current issue is not published yet, so its own window start is the newest published
    issue's PULL; pooling K windows therefore means starting at the window start of the
    (K-1)-th most recent published issue. Read out of that issue's own results.json rather than
    retyped, so the boundary cannot drift from what was published.
    """
    dirs = published_issues_before(cutoff_str)
    if len(dirs) < K - 1: return None, None
    src = dirs[K - 2]
    d = json.load(open(src / "results.json"))
    ws = d.get("issue_window_start")
    if not ws: return None, None
    t = dt.datetime.strptime(ws, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return t.timestamp(), {"K": K, "start_utc": ws, "start_from_issue": d.get("issue"),
                           "start_source": str(src / "results.json"),
                           "pooled_issues": [q.name for q in dirs[:K - 1]] + ["(this issue)"]}


def pooled_overlap(NEW, start, cutoff, prev_issue_dir, con=None):
    """How much of THIS pooled window is the PREVIOUS issue's pooled window over again.

    Issue #7 opened the pooled series and pre-registered the discipline (its watch item #4):
    consecutive pooled points share most of their items by construction, so they are strongly
    dependent and must never be read as a two-point trend. Quantifying it is what makes that
    caveat checkable instead of rhetorical.

    Overlap is measured on ITEMS, not on elapsed time: the windows have different lengths and
    daily volume is not constant, so a time fraction would misstate how much data is shared.
    Note the newcomer/incumbent SPLIT is not shared even where items are — an author is a
    newcomer relative to each window's own start, so a later pooled start reclassifies earlier
    arrivals as incumbents.
    """
    if not (prev_issue_dir / "results.json").exists(): return None
    d = json.load(open(prev_issue_dir / "results.json"))
    pw = d.get("newcomer_cells_pooled_window") or {}
    ws, pc = pw.get("start_utc"), d.get("cutoff")
    if not (ws and pc): return None
    pstart = dt.datetime.strptime(ws, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp()
    pcut = dt.datetime.strptime(pc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
    mine = [t for t, k, x, a in NEW if start <= t < cutoff]
    both = [t for t in mine if pstart <= t < pcut]
    out = {"prev_issue": d.get("issue"), "prev_pooled_start_utc": ws,
           "prev_pooled_end_utc": pc, "this_pooled_items": len(mine),
           "shared_items": len(both),
           "shared_fraction_of_this": round(len(both) / len(mine), 3) if mine else None,
           "read": "consecutive pooled points are strongly dependent; not a two-point trend."}
    # ...and the item fraction is the WEAKER statement, because the cells measure the SPLIT. An
    # author is a newcomer relative to each window's own start, so a later start reclassifies the
    # previous window's earliest arrivals as incumbents. Issue #18 read a pooled disagreement
    # against an item overlap of 68% while only 37% of the previous newcomer SET was still a
    # newcomer; without this row the dependence caveat points the wrong way.
    try:
        import corpus_store as CS
        _c = con or CS.build_index()
        prev_stream = CS.weather_items(_c, cutoff=pcut)
        pn_i, pi_i = split(prev_stream, pstart)
        key_p = lambda i: f"{prev_stream[i][1][0]}:{prev_stream[i][1][1]}"
        key_t = lambda i: f"{NEW[i][1][0]}:{NEW[i][1][1]}"
        cn_i, ci_i = split(NEW, start)
        pn = {key_p(i) for i in pn_i}
        cn = {key_t(i) for i in cn_i}
        ci = {key_t(i) for i in ci_i}
        out["newcomer_set_overlap"] = {
            "prev_newcomer_items": len(pn), "this_newcomer_items": len(cn),
            "retained_as_newcomer": len(pn & cn),
            "retained_fraction_of_prev": round(len(pn & cn) / len(pn), 3) if pn else None,
            "reclassified_as_incumbent": len(pn & ci),
            "fell_out_of_the_window": len(pn - cn - ci),
            "newly_newcomer": len(cn - pn),
            "read": "the cells measure the newcomer/incumbent SPLIT, so this is the overlap that "
                    "governs how dependent two pooled points are. A low retained fraction with a "
                    "high item overlap means the two windows measure different populations and "
                    "disagreement between them is expected without any change in behaviour."}
    except Exception as e:                       # a control, never a reason to lose the cell
        out["newcomer_set_overlap"] = {"error": repr(e)}
    return out


if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    _c = os.environ["WEATHER_CUTOFF"]
    CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
    import corpus_store as CS
    _con = CS.build_index()
    _obs = float(os.environ["WEATHER_OBSERVED_AT"]) if os.environ.get("WEATHER_OBSERVED_AT") else None
    _prev_at = float(os.environ["WEATHER_PREV_OBSERVED_AT"]) \
        if os.environ.get("WEATHER_PREV_OBSERVED_AT") else IB.previous_issue_observed_at(_c)
    NEW = CS.weather_items(_con, cutoff=CUTOFF, observed_at=_obs)
    # prev_last is a query against recorded observations; there is no prev_corpus tree any more.
    prev_last = _con.execute("SELECT MAX(created_at) FROM observations WHERE first_seen_at <= ? "
                             "AND n_chars >= ?", (_prev_at, CS.MIN_CHARS)).fetchone()[0]
    cache = {(k0, int(k1)): c for (k0, k1), c in
             ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
    missing = [k for _, k, _, _ in NEW if k not in cache]
    assert not missing, f"{len(missing)} items have no cached claim - run weather_gpu.py first"
    claims = [cache[k] for _, k, _, _ in NEW]

    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
    Ea = m.encode(claims, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)

    EMIT = {"cutoff": _c, "n_items": len(NEW)}

    # (1) the per-issue window cell, recomputed here as a REPRODUCTION CHECK on weather_gpu.py.
    # Same split, same floors, same seed -> the two must agree before the pooled cell is trusted.
    WIN_START, _ = IB.issue_window_start(_c, prev_last)
    ni, ii = split(NEW, WIN_START)
    EMIT["per_issue_window"] = dict(cells(Ea, ni, ii, np.random.default_rng(0)),
                                    window_start_utc=dt.datetime.fromtimestamp(WIN_START, dt.timezone.utc)
                                    .strftime("%Y-%m-%d %H:%M"))
    print(f"per-issue window (from {EMIT['per_issue_window']['window_start_utc']}): "
          f"{len(ni)} newcomer / {len(ii)} incumbent items")
    gp = S / "weather_gpu_out.json"
    if gp.exists():
        g = json.load(open(gp))
        agree = (g.get("newcomer_counts") == EMIT["per_issue_window"]["counts"])
        EMIT["per_issue_window"]["reproduces_weather_gpu"] = "AGREES" if agree else "DISAGREES"
        print(f"   reproduction vs weather_gpu.py newcomer_counts: "
              f"{'AGREES' if agree else 'DISAGREES ' + str(g.get('newcomer_counts'))}")

    # (2) the pooled fallback.
    st, prov = pooled_start(_c, K)
    if st is None:
        print(f"pooled window unavailable: fewer than {K - 1} published issues before {_c}")
    else:
        pn, pi = split(NEW, st)
        EMIT["pooled_window"] = dict(cells(Ea, pn, pi, np.random.default_rng(0)), **prov,
            span_days=round((CUTOFF - st) / 86400, 2),
            comparability="NOT comparable to the per-issue newcomer cells of issues #1-#5: longer"
                          " arrival window, contiguous interval, its own series from here.")
        print(f"pooled window K={K} (from {prov['start_utc']}, {EMIT['pooled_window']['span_days']}d): "
              f"{len(pn)} newcomer / {len(pi)} incumbent items")
        for k in ("within_pool_parity", "union_over_incumbent", "nn_distance_matched",
                  "vendi_cells_skipped", "nn_cell_skipped"):
            if k in EMIT["pooled_window"]: print(f"   {k}: {EMIT['pooled_window'][k]}")
        _prevdirs = published_issues_before(_c)
        ov = pooled_overlap(NEW, st, CUTOFF, _prevdirs[0]) if _prevdirs else None
        if ov:
            EMIT["pooled_window"]["overlap_with_prev_issue"] = ov
            print(f"   overlap_with_prev_issue: {ov['shared_items']}/{ov['this_pooled_items']} "
                  f"items = {100 * ov['shared_fraction_of_this']:.1f}% shared with "
                  f"{ov['prev_issue']}'s pooled window")

    # (3) the m-matched control, pre-registered by issue #18's watch item #5.
    #
    # within_pool_parity and union_over_incumbent are Vendi ratios drawn at m set by the newcomer
    # pool size, and that pool shrank with recruitment: 529 -> 346 -> 196 items over issues
    # #17-#19. Vendi grows sublinearly with m at a rate set by each pool's own geometry, so a
    # parity move across those windows confounds the effect with the cell's own sample size.
    #
    # Construction: every published pooled window is rebuilt against its OWN start and cutoff, so
    # each keeps its real newcomer population, and the newcomer set is then subsampled to a common
    # target m. Claims and embeddings are this issue's throughout -- one basis, like the one-basis
    # median column -- so an earlier window is its own population measured with today's instrument.
    #
    # TWO targets, because they answer different questions. Issue #18 registered ONE: subsample the
    # larger pool to the previous window's size, which asks whether the parity move between those
    # two windows survives. The smallest pool across all windows is also run, which is the only m
    # every window can reach and so the only one that puts the whole series on one footing. Both
    # are reported; the registered one is marked.
    #
    # The OUTER subsample is repeated (WEATHER_MCTRL_DRAWS, default 20) rather than drawn once,
    # because a single draw would put the whole comparison on one arbitrary subset. The band below
    # is over outer draws of the per-draw medians; the inner 40-draw band of any one subsample is
    # narrower and is not what should be read.
    if "--no-m-control" not in sys.argv and EMIT.get("pooled_window"):
        D = int(os.environ.get("WEATHER_MCTRL_DRAWS", "20"))
        wins = []
        for q in published_issues_before(_c)[:K - 1]:
            _pd = json.load(open(q / "results.json"))
            _pw = _pd.get("newcomer_cells_pooled_window") or {}
            if not _pw.get("start_utc"):
                continue
            wins.append((_pd["issue"],
                         dt.datetime.strptime(_pw["start_utc"], "%Y-%m-%d %H:%M")
                         .replace(tzinfo=dt.timezone.utc).timestamp(),
                         dt.datetime.strptime(_pd["cutoff"], "%Y-%m-%dT%H:%M:%SZ")
                         .replace(tzinfo=dt.timezone.utc).timestamp()))
        wins.reverse()
        wins.append((f"(this issue, cutoff {_c})", st, CUTOFF))
        rows = []
        for tag, ws, wc in wins:
            keep = [i for i, (t, k, x, a) in enumerate(NEW) if t < wc]
            sub = [NEW[i] for i in keep]
            n_j, i_j = split(sub, ws)
            rows.append({"window": tag, "n": [keep[j] for j in n_j], "i": [keep[j] for j in i_j]})
        # The pre-registered target is the PREVIOUS issue's pooled newcomer count -- that is what
        # "subsample the larger newcomer pool to 346" named. Read it from the previous issue's
        # published block rather than picking a sort position, which happened to equal 346 only
        # because these three counts are distinct.
        counts = sorted({len(r["n"]) for r in rows})
        registered = None
        _pdirs = published_issues_before(_c)
        if _pdirs:
            registered = (((json.load(open(_pdirs[0] / "results.json"))
                            .get("newcomer_cells_pooled_window") or {}).get("counts") or {})
                          .get("newcomer_items"))
        targets = sorted({counts[0]} | ({registered} if registered else set()))
        EMIT["m_matched_control"] = {"K": K, "outer_draws": D,
            "construction": "each published pooled window rebuilt against its own start and "
                            "cutoff; newcomer set subsampled to a common target and the subsample "
                            "repeated D times. Bands are over OUTER draws, not the inner band of "
                            "one subsample. A row whose pool EQUALS the target is not subsampled, "
                            "so its band carries no outer variation and is marked "
                            "no_outer_variation. Claims and embeddings are this issue's throughout.",
            "targets": {}}
        for m_t in targets:
            elig = [r for r in rows if len(r["n"]) >= m_t]
            ctrl = []
            for r in elig:
                rg = np.random.default_rng(0)
                par, uni, nnd, nnp = [], [], [], []
                # A window whose pool EQUALS the target is not subsampled at all, so its "outer
                # draws" are 20 copies of one set and its band carries no outer variation. That is
                # a different quantity from a genuinely subsampled row's band and is flagged.
                degenerate = len(r["n"]) == m_t
                for _ in range(D):
                    draw = [r["n"][j] for j in rg.choice(len(r["n"]), m_t, replace=False)]
                    c = vendi_cells(Ea, draw, r["i"], np.random.default_rng(0))
                    if c.get("within_pool_parity"): par.append(c["within_pool_parity"]["band"][0])
                    if c.get("union_over_incumbent"): uni.append(c["union_over_incumbent"]["band"][0])
                    # NN over the SAME outer draws, at reduced inner draws so the repetition is
                    # affordable. p resolution is 2/NN_CTRL_DRAWS, ample for telling an exclusion
                    # from a null here; the published cell keeps its 500.
                    if len(draw) >= NN_FLOOR and len(r["i"]) >= 3 * NN_FLOOR:
                        _n = NNR.matched_nn(Ea[np.array(draw)], Ea[np.array(r["i"])],
                                            draws=NN_CTRL_DRAWS)
                        nnd.append(_n["delta_observed"][0]); nnp.append(_n["p_two_sided_vs_null"])
                band = lambda v, k=3: [round(float(np.percentile(v, q)), k) for q in (50, 5, 95)] if v else None
                ctrl.append({"window": r["window"], "newcomer_items_full": len(r["n"]),
                             "incumbent_items": len(r["i"]), "newcomer_items_drawn": m_t,
                             "no_outer_variation": degenerate,
                             "parity_over_outer_draws": band(par),
                             "union_over_outer_draws": band(uni),
                             "nn_delta_over_outer_draws": band(nnd, 4),
                             "nn_p_over_outer_draws": band(nnp, 3),
                             "nn_inner_draws": NN_CTRL_DRAWS})
            EMIT["m_matched_control"]["targets"][str(m_t)] = {
                "m_newcomer_items": m_t,
                "vendi_draw_m": int(0.8 * m_t),
                "windows_eligible": len(elig),
                "pre_registered": m_t == registered,
                "windows": ctrl}
            print(f"m-matched control at m={m_t} ({D} outer draws"
                  f"{', PRE-REGISTERED' if m_t == registered else ''}):")
            for c in ctrl:
                print(f"   {c['window']:34s} full={c['newcomer_items_full']:4d}"
                      f"{' [no outer variation]' if c['no_outer_variation'] else '':22s} "
                      f"parity={c['parity_over_outer_draws']} union={c['union_over_outer_draws']} "
                      f"nn_p={c['nn_p_over_outer_draws']}")

    out = S / "weather_newcomer_pooled_out.json"
    out.write_text(json.dumps(EMIT, indent=1))
    print(f"saved {out}")
