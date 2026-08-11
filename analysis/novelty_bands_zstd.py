# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""Uniform zstd-novelty pass over all five corpora (agent, catskill, hn, lisp, sci), raw text AND
claim-normalized, using the repo's zstd_curve.compute_metrics verbatim (level 19, 512KB window,
bucket 25, seed 42). Three aggregations reported consistently for every corpus:
  whole      = sum(cond_win_bits)/sum(self_bits) over the full chronological sequence
  lastN      = same over the final N items (N = smallest corpus)
  matchedN   = same over a seeded random chronological subsequence of N items, re-run through the
               pipeline (thinner history -- the honest size control), median of 5 seeds
The base report's HN cell (0.745) is NOT exactly reproducible from the stored control metrics
(whole=0.714/last1149=0.693; control runs stored no run.json) -- flagged, superseded by this uniform pass."""
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import zstd_curve as Z

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")

class Args: level = 19; window_bytes = 524288; bucket = 25; seed = 42
args = Args()

def forum_texts(d):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), "post"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, (c.get("body") or "").strip(), "comment"))
    items.sort(key=lambda x: x[0])
    return [(t, x, k) for t, x, k in items if len(x) >= 20]

def usenet_texts(fam):
    C = json.load(open(S / "baseline_corpora.json"))[fam]
    out = []
    for r in C:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append((r["ts"], (r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"],
                    "post" if is_root else "comment"))
    return out

OUTNAME = sys.argv[1] if len(sys.argv) > 1 else "band_zstd.json"
CLAIMS_DIR = sys.argv[2] if len(sys.argv) > 2 else "baseline_claims"
POOLS = sys.argv[3:] or ["agent", "catskill", "hn", "lisp", "sci"]
LOADERS = {
    "agent": lambda: forum_texts("/home/dan/personal/memetic/data/posts"),
    "catskill": lambda: forum_texts(S / "catskill/posts"),
    "hn": lambda: forum_texts(S / "hn/posts"),
    "lisp": lambda: usenet_texts("lisp"),
    "sci": lambda: usenet_texts("sci"),
}
CORPORA = {k: LOADERS[k]() for k in POOLS}
CLAIMS = {k: json.load(open(S / CLAIMS_DIR / f"{k}_all.json")) for k in POOLS}
for k in CORPORA:
    assert len(CORPORA[k]) == len(CLAIMS[k]), f"{k}: {len(CORPORA[k])} texts vs {len(CLAIMS[k])} claims"

def mk_items(seq):
    return [{"kind": kind, "id": i, "post_id": i, "created_at": t, "author": "", "author_model": "",
             "text": x} for i, (t, x, kind) in enumerate(seq)]

def agg(rows): return sum(r["cond_win_bits"] for r in rows) / sum(r["self_bits"] for r in rows)

N = min(len(v) for v in CORPORA.values())
print(f"corpora: " + ", ".join(f"{k}={len(v)}" for k, v in CORPORA.items()) + f"; matched N={N}", flush=True)

out = {"N_matched": N, "params": dict(level=19, window_bytes=524288, bucket=25, seed=42), "raw": {}, "claims": {}}
for variant in ["raw", "claims"]:
    for k, seq in CORPORA.items():
        if variant == "claims":
            seq = [(t, c, kind) for (t, _, kind), c in zip(seq, CLAIMS[k]) if len(c.strip()) >= 5]
        items = mk_items(seq)
        rows = Z.compute_metrics(items, args)
        whole, lastn = agg(rows), agg(rows[-N:])
        med = []
        for s in range(5):
            rng = np.random.default_rng(s)
            idx = np.sort(rng.choice(len(items), min(N, len(items)), replace=False))
            med.append(agg(Z.compute_metrics([items[i] for i in idx], args)))
        out[variant][k] = dict(n=len(items), whole=round(whole, 4), lastN=round(lastn, 4),
                               matchedN=round(float(np.median(med)), 4),
                               matchedN_spread=[round(min(med), 4), round(max(med), 4)])
        print(f"{variant:6s} {k:9s} n={len(items):5d}  whole {whole:.3f}  last{N} {lastn:.3f}  "
              f"matched{N} {np.median(med):.3f} [{min(med):.3f},{max(med):.3f}]", flush=True)

json.dump(out, open(S / OUTNAME, "w"), indent=1)
print(f"saved {OUTNAME}")
