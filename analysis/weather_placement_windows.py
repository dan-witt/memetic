#!/usr/bin/env python3
"""Placement vs the frozen anchors on MATCHED one-day windows.

weather_gpu.py's window_only cell uses the issue window, whose WIDTH is whatever the gap between
consecutive issues happened to be. Issue #14's window was two calendar days because no issue was
produced for 08-26; issues #9-#13 used one. A wider window draws from more of the pool and reads
closer to the full-pool cell for mechanical reasons, so the published window series mixes widths
and cannot be read as a trend. Issue #14's watch item #5 asked for the last three windows at
matched width and on one basis before issue #3's decline arm is allowed to complete.

This recomputes the cell for arbitrary single calendar days, from the CURRENT claim set, so every
day is one basis (the placeholder-free currency) and one width. Construction is weather_gpu.py's:
Vendi(agent draw) / Vendi(anchor draw), m = min(1500, 0.8*min(pool, anchor)), 40 draws, median
with a 5/95 band. Each cell seeds its own generator, so a cell does not depend on how many cells
ran before it -- weather_gpu draws from one shared stream and is order-dependent by construction,
which is why the two agree to within sampling rather than exactly.

Usage: WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_placement_windows.py [MM-DD ...]
       Days default to the five calendar days ending the day before the cutoff.
"""
import datetime as dt, json, os, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import corpus_store as CS

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]
CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
ANCH = {"lisp": "lisp_all.json", "sci": "sci_all.json", "hn": "hn_all.json"}
MODEL = "BAAI/bge-large-en-v1.5"


def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))


def cell(Ea, pool, Ex, seed=0, draws=40):
    m = min(1500, int(0.8 * min(len(pool), len(Ex))))
    rng = np.random.default_rng(seed)
    rs = [vendi(Ea[pool][rng.choice(len(pool), m, replace=False)]) /
          vendi(Ex[rng.choice(len(Ex), m, replace=False)]) for _ in range(draws)]
    return {"m": m, "n_pool": len(pool),
            "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}


def main(days):
    con = CS.build_index()
    new = CS.weather_items(con, cutoff=CUTOFF)
    claims = json.load(open(S / "agent_claims_current.json"))
    if len(claims) != len(new):
        sys.exit(f"claim/item misalignment: {len(claims)} claims vs {len(new)} items; "
                 "re-run weather_gpu.py at this cutoff first")
    # weather_gpu.py sanitises the same way before embedding; keep the two identical.
    claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim"
              for c in claims]
    dayof = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
    idx = {}
    for i, (t, k, x, a) in enumerate(new):
        idx.setdefault(dayof(t), []).append(i)

    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(MODEL, device="cuda")
    Ea = m.encode(claims, normalize_embeddings=True, batch_size=64,
                  show_progress_bar=False).astype(np.float32)
    out = {"model": MODEL.split("/")[-1], "cutoff": _c, "draws": 40,
           "basis": "excluded" if CS.exclude_placeholders_default() else "with_placeholders",
           "construction": "one calendar day per window; weather_gpu.py's ratio, per-cell seeding",
           "windows": {}}
    for k, f in ANCH.items():
        cl = [c for c in json.load(open(S / "baseline_claims" / f)) if len(c.strip()) >= 5]
        Ex = m.encode(cl, normalize_embeddings=True, batch_size=64,
                      show_progress_bar=False).astype(np.float32)
        for d in days:
            if d not in idx:
                continue
            out["windows"].setdefault(d, {})[k] = cell(Ea, np.array(idx[d]), Ex)
    for d in days:
        if d in out["windows"]:
            print(d, {k: v["band"][0] for k, v in out["windows"][d].items()},
                  "n =", out["windows"][d]["lisp"]["n_pool"], flush=True)
    json.dump(out, open(S / "weather_placement_windows_out.json", "w"), indent=1)
    print("saved", S / "weather_placement_windows_out.json")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        last = dt.datetime.fromtimestamp(CUTOFF, dt.timezone.utc) - dt.timedelta(days=1)
        args = [(last - dt.timedelta(days=i)).strftime("%m-%d") for i in range(4, -1, -1)]
    main(args)
