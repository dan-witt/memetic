#!/usr/bin/env python3
"""Moderation placeholders in the corpus, and what they do to the published cells.

When 1f916 collapses a comment -- flagged by the community or hidden by the maintainer -- it does
not delete it. It replaces the body with a fixed boilerplate:

    [collapsed - flagged by the community or hidden by the maintainer; not deleted.
     Reason in GET /api/events?kind=moderation]

That string is 122 characters, so it clears the >= 20-char inclusion rule and enters every weather
cell as though it were an item the community wrote. It is not. It is platform chrome, identical
across every occurrence, and it has been in the corpus since 08-06.

Found at issue #13, from the rolling idea series: the two lowest windows in the whole 618-window
history (0.0758 and 0.0761, against a next-lowest of 0.1088) each contained 38 copies of the same
normalised claim. The cause was not a claimify failure -- every claim in those windows was valid --
but 38 identical bodies.

Four cells are affected, in the same direction each time:

  allocation   the placeholder is ABOUT the venue's own governance, so the classifier reads it
               VENUE (137 of 145). It therefore inflates venue share, most on the days with the
               most moderation.
  idea series  identical bodies produce identical claims, which collapse the Vendi of any window
               holding several of them.
  register     no consistent direction, and not cleanly attributable: dropping items also
               re-partitions the 25-item buckets, so the per-day deltas (11 up, 9 down,
               |max| 0.0050) are re-bucketing as much as placeholder.
  corpus       they are counted as items and their authors as active.

This script measures all four with and without them. It does NOT change any published series; the
exclusion decision and its schedule belong to the issue that adopts it.

The three stages need three interpreters, so each MERGES into the shared output rather than
overwriting it:

  python3 analysis/weather_collapsed_items.py              detection + allocation (any python)
  .venv/bin/python  ... --register                          zstd needs 3.10+ syntax
  <conda>/bin/python ... --gpu                              bge, warm claim cache, ~2 min
"""
import datetime as dt, json, os, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")

# The detector moved into corpus_store at issue #14, when the exclusion became the published
# currency and the text-free loaders needed the same rule.
from corpus_store import is_placeholder, PLACEHOLDER_MARKER as MARKER


def find(NEW):
    return [i for i, (t, k, x, a) in enumerate(NEW) if is_placeholder(x)]


def venue_share(NEW, labels, drop=frozenset()):
    ds = defaultdict(list)
    for i, (t, k, x, a) in enumerate(NEW):
        if i in drop: continue
        l = labels.get(f"{k[0]}:{k[1]}")
        if l: ds[DAY(t)].append(l == "V")

    return {d: round(sum(v) / len(v), 4) for d, v in sorted(ds.items()) if len(v) >= 50}


def main():
    S = Path(os.environ.get("MEMETIC_WORKDIR", Path.home() / "personal/memetic-workdir"))
    cutoff_s = os.environ["WEATHER_CUTOFF"]
    cutoff = dt.datetime(*map(int, cutoff_s.split("-")), tzinfo=dt.timezone.utc).timestamp()
    observed = float(os.environ["WEATHER_OBSERVED_AT"]) if os.environ.get("WEATHER_OBSERVED_AT") else None

    con = CS.build_index()
    # This script MEASURES the placeholders, so it always loads them regardless of the
    # process default that issue #14 set for the published pipeline.
    NEW = CS.weather_items(con, cutoff=cutoff, observed_at=observed,
                           exclude_placeholders=False)
    idx = find(NEW)
    drop = set(idx)
    by_day = dict(sorted(Counter(DAY(NEW[i][0]) for i in idx).items()))
    labels = json.load(open(S / "allocation_label_cache_agent.json"))

    OUTP = S / "weather_collapsed_items_out.json"
    emit = json.load(open(OUTP)) if OUTP.exists() else {}
    emit |= {"cutoff": cutoff_s, "n_items": len(NEW), "n_placeholders": len(idx),
            "pct_of_corpus": round(100 * len(idx) / len(NEW), 2),
            "by_day": by_day,
            "distinct_bodies": len({NEW[i][2].strip() for i in idx}),
            "distinct_authors": len({NEW[i][3] for i in idx}),
            "kinds": dict(Counter(NEW[i][1][0] for i in idx)),
            "allocation_labels": dict(Counter(labels.get(f"{NEW[i][1][0]}:{NEW[i][1][1]}", "(unlabelled)")
                                              for i in idx))}

    print(f"collapse placeholders: {len(idx)} of {len(NEW)} items ({emit['pct_of_corpus']}%), "
          f"{emit['distinct_bodies']} distinct bodies, {emit['distinct_authors']} authors, "
          f"kinds {emit['kinds']}")
    print(f"by day: {by_day}")
    print(f"allocation labels: {emit['allocation_labels']}")

    a, b = venue_share(NEW, labels), venue_share(NEW, labels, drop)
    del labels
    emit["venue_share_with"], emit["venue_share_without"] = a, b
    emit["venue_share_delta"] = {d: round(b[d] - a[d], 4) for d in a if d in b}
    print(f"\n{'day':6s} {'placeholders':>13s} {'venue share':>12s} {'excluding':>10s} {'delta':>8s}")
    for d in a:
        print(f"{d:6s} {by_day.get(d, 0):13d} {a[d]:12.4f} {b[d]:10.4f} {b[d] - a[d]:+8.4f}")

    # register: the zstd cell over the same day partition, with and without
    if "--register" in sys.argv:
      import zstd_curve as Z

      class Args: level = 19; window_bytes = 524288; bucket = 25; seed = 42  # identical to weather_cpu

      reg = {}
      for tag, dropset in (("with", frozenset()), ("without", drop)):
        mk = [{"kind": k[0], "id": k[1], "post_id": 0, "created_at": t, "author": a_,
               "author_model": "", "text": x}
              for i, (t, k, x, a_) in enumerate(NEW) if i not in dropset]
        rows = Z.compute_metrics(mk, Args(), columns=("self", "cond_win"))
        agg = lambda rs: sum(r["cond_win_bits"] for r in rs) / sum(r["self_bits"] for r in rs)
        reg[tag] = {d: round(agg([r for r in rows if DAY(r["created_at"]) == d]), 4)
                    for d in sorted({DAY(r["created_at"]) for r in rows})
                    if sum(1 for r in rows if DAY(r["created_at"]) == d) >= 50}
      emit["register_with"], emit["register_without"] = reg["with"], reg["without"]
      emit["register_delta"] = {d: round(reg["without"][d] - reg["with"][d], 4)
                                for d in reg["with"] if d in reg["without"]}
      print(f"\n{'day':6s} {'register':>9s} {'excluding':>10s} {'delta':>8s}")
      for d in reg["with"]:
        print(f"{d:6s} {reg['with'][d]:9.4f} {reg['without'][d]:10.4f} "
              f"{reg['without'][d] - reg['with'][d]:+8.4f}")

    if "--gpu" in sys.argv:
        import numpy as np
        cache = json.load(open(S / "claim_cache_agent.json"))
        claims = [cache.get(f"{k[0]}:{k[1]}", "empty claim") for _, k, _, _ in NEW]
        claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR"))
                  else "empty claim" for c in claims]
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
        E = m.encode(claims, normalize_embeddings=True, batch_size=64,
                     show_progress_bar=False).astype(np.float32)

        def vendi(X):
            n = len(X); lam = np.linalg.eigvalsh((X @ X.T) / n); lam = lam[lam > 1e-12]
            lam /= lam.sum(); return float(np.exp(-(lam * np.log(lam)).sum()))

        W, ST, FORTH = 120, 40, 0.1269
        # The per-issue rate is the cell the report reads, so it is compared on a MATCHED basis:
        # a window belongs to this issue if its centre item falls in the issue window. Counting
        # "the last N" instead would compare different spans, since dropping items shortens the
        # series.
        import weather_issue_boundary as IB
        prev_at = IB.previous_issue_observed_at(cutoff_s)
        prev_last = con.execute("SELECT MAX(created_at) FROM observations WHERE first_seen_at <= ?"
                                " AND n_chars >= ?", (prev_at, CS.MIN_CHARS)).fetchone()[0]
        win_start, _ = IB.issue_window_start(cutoff_s, prev_last)
        out = {}
        for tag, keep in (("with", list(range(len(NEW)))),
                          ("without", [i for i in range(len(NEW)) if i not in drop])):
            Ek = E[np.array(keep)]
            starts = list(range(0, len(Ek) - W + 1, ST))
            ws = [round(vendi(Ek[i:i + W]) / W, 4) for i in starts]
            centre_t = [NEW[keep[i + W // 2]][0] for i in starts]
            issue = [v for v, t in zip(ws, centre_t) if t >= win_start]
            out[tag] = {"windows": len(ws), "below_forth": sum(1 for v in ws if v < FORTH),
                        "below_forth_pct": round(100 * sum(1 for v in ws if v < FORTH) / len(ws), 1),
                        "min": min(ws),
                        "issue_windows": len(issue),
                        "issue_below_forth": sum(1 for v in issue if v < FORTH),
                        "issue_below_forth_pct": round(100 * sum(1 for v in issue if v < FORTH) / len(issue), 1)
                                                 if issue else None,
                        "series": ws}
            print(f"\nrolling series {tag}: {len(ws)} windows, min {min(ws)}, "
                  f"{out[tag]['below_forth']} below forth ({out[tag]['below_forth_pct']}% pooled); "
                  f"this issue's windows {out[tag]['issue_below_forth']}/{out[tag]['issue_windows']}"
                  f" = {out[tag]['issue_below_forth_pct']}%")
        emit["rolling_with"] = {k: v for k, v in out["with"].items() if k != "series"}
        emit["rolling_without"] = {k: v for k, v in out["without"].items() if k != "series"}
        # Both series are emitted: whichever parse is NOT the published currency is the figure's
        # overlay, and that flipped at issue #14.
        emit["rolling_series_without"] = out["without"]["series"]
        emit["rolling_series_with"] = out["with"]["series"]

    json.dump(emit, open(OUTP, "w"), indent=1)
    print(f"\nsaved {OUTP}")


if __name__ == "__main__":
    main()
