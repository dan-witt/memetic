#!/usr/bin/env python3
"""S5 third-normalizer cells: agent/lisp claim-Vendi on Qwen3.6-27B claims, 3 embedders.
Claims produced by claimify_server.py against a llama-server running the 27B gguf (identical
prompt, thinking disabled). Reads baseline_claims_qwen27/{agent,lisp}_all.json in MEMETIC_WORKDIR."""
import json, os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
cl = {k: [c for c in json.load(open(S / "baseline_claims_qwen27" / f"{k}_all.json")) if len(c.strip()) >= 5]
      for k in ("agent", "lisp")}

def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

rng = np.random.default_rng(0); M = 1500
for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    m = SentenceTransformer(MODEL, device="cuda")
    E = {k: m.encode(v, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
         for k, v in cl.items()}
    rs = [vendi(E["agent"][rng.choice(len(E["agent"]), M, replace=False)]) /
          vendi(E["lisp"][rng.choice(len(E["lisp"]), M, replace=False)]) for _ in range(100)]
    print(MODEL.split("/")[-1], "agent/lisp:", [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)])
    del m, E
