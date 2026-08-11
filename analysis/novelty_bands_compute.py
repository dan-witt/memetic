# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""RELEASE-version semantic bands: catskill retired; pools = agent, hn, lisp, sci (all releasable).
Both normalizers (qwen = Qwen2.5-7B, gemma = Gemma-3-12B) x 3 embedders. Matched m = 0.8*min(N) ~ 2268.
Point Vendi at full m (one eig) + 100 subsample ratio draws (item-sampling bands only; the honest
uncertainty is the cross-embedder + cross-normalizer spread). Plus rolling claim-Vendi/W (120/40, bge)
for both normalizers. Output: band_final.json."""
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
POOLS = ["agent", "hn", "lisp", "sci"]
DIRS = {"qwen": "baseline_claims", "gemma": "baseline_claims_gemma"}
claims = {n: {k: [c for c in json.load(open(S / d / f"{k}_all.json")) if len(c.strip()) >= 5] for k in POOLS}
          for n, d in DIRS.items()}

def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

mm = int(0.8 * min(len(claims["qwen"][k]) for k in POOLS))
rng = np.random.default_rng(0)
W, STRIDE, DRAWS = 120, 40, 100
print(f"pools sans catskill; matched m={mm}", flush=True)

out = {"m": mm, "pools": POOLS, "vendi_point": {}, "ratios_agent_over_X": {}, "rolling": {}}
for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    tag = MODEL.split("/")[-1]
    emb = SentenceTransformer(MODEL, device="cuda")
    for norm in DIRS:
        E = {k: emb.encode(v, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
             for k, v in claims[norm].items()}
        pv = {k: round(vendi(E[k][rng.choice(len(E[k]), mm, replace=False)]), 2) for k in POOLS}
        out["vendi_point"].setdefault(tag, {})[norm] = pv
        rat = {}
        for k in ("hn", "lisp", "sci"):
            rs = [vendi(E["agent"][rng.choice(len(E["agent"]), mm, replace=False)]) /
                  vendi(E[k][rng.choice(len(E[k]), mm, replace=False)]) for _ in range(DRAWS)]
            rat[k] = [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]
        out["ratios_agent_over_X"].setdefault(tag, {})[norm] = rat
        print(f"{tag} [{norm}] point " + ", ".join(f"{k}={pv[k]}" for k in POOLS), flush=True)
        print(f"{tag} [{norm}] agent/X " + ", ".join(f"{k}={rat[k][0]}[{rat[k][1]},{rat[k][2]}]" for k in rat), flush=True)
        if tag == "bge-large-en-v1.5":
            roll = {}
            for k in POOLS:
                e = E[k]
                ws = [vendi(e[i:i+W]) / W for i in range(0, len(e) - W + 1, STRIDE)]
                roll[k] = round(float(np.mean(ws)), 4)
            out["rolling"][norm] = roll
            print(f"rolling/W bge [{norm}]: " + ", ".join(f"{k}={roll[k]}" for k in POOLS), flush=True)
        del E
    del emb

json.dump(out, open(S / "band_final.json", "w"), indent=1)
print("saved band_final.json")
