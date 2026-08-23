#!/usr/bin/env python3
"""Embed the identity pass's two views.

  lexical : the 12,725 item texts as written (voice = words on the page)
  idea    : the 9,217 claim-normalized sentences, BOTH normalizer families already on disk
            (qwen = Qwen2.5-7B, gemma = Gemma-3-12B) -- no GPU spent on normalization

Two embedders (bge-large, gte-large) because the human-baselines addendum showed semantic
readings here are embedder-dependent; the cross-embedder spread is the honest uncertainty.

Item texts run past bge/gte's 512-token window (34% exceed ~2k chars), so long items are split
into <=1800-char chunks and mean-pooled, then renormalized -- otherwise every long item would be
represented by its opening paragraph alone, which is itself an author-correlated artifact.

Writes identity_emb_{view}_{tag}.npy into MEMETIC_WORKDIR.
"""
import json, os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
EMBEDDERS = [("bge", "BAAI/bge-large-en-v1.5"), ("gte", "thenlper/gte-large")]
CHUNK = 1800

def chunks(t):
    """Split on paragraph boundaries, packing into <=CHUNK-char pieces; never mid-word."""
    out, cur = [], ""
    for para in t.split("\n\n"):
        while len(para) > CHUNK:                      # a single huge paragraph: break on spaces
            cut = para.rfind(" ", 0, CHUNK)
            cut = cut if cut > CHUNK // 2 else CHUNK
            if cur: out.append(cur); cur = ""
            out.append(para[:cut]); para = para[cut:].lstrip()
        if len(cur) + len(para) + 2 > CHUNK and cur:
            out.append(cur); cur = ""
        cur = (cur + "\n\n" + para).strip() if cur else para
    if cur: out.append(cur)
    return out or [t[:CHUNK]]

def encode_pooled(model, texts):
    flat, owner = [], []
    for i, t in enumerate(texts):
        for c in chunks(t):
            flat.append(c); owner.append(i)
    E = model.encode(flat, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    owner = np.asarray(owner)
    out = np.zeros((len(texts), E.shape[1]), dtype=np.float32)
    np.add.at(out, owner, E)
    out /= np.linalg.norm(out, axis=1, keepdims=True)
    print(f"    pooled {len(flat)} chunks -> {len(texts)} items", flush=True)
    return out

def main():
    items = json.load(open(S / "identity_items.json"))
    views = {"lexical": [it["text"] for it in items],
             "claim_qwen": json.load(open(S / "baseline_claims" / "agentcur_all.json")),
             "claim_gemma": json.load(open(S / "baseline_claims_gemma" / "agentcur_all.json"))}
    for tag, name in EMBEDDERS:
        m = SentenceTransformer(name, device="cuda")
        for view, texts in views.items():
            f = S / f"identity_emb_{view}_{tag}.npy"
            if f.exists():
                print(f"  {view}/{tag}: cached", flush=True); continue
            print(f"  {view}/{tag}: {len(texts)} texts", flush=True)
            E = (encode_pooled(m, texts) if view == "lexical" else
                 m.encode(texts, normalize_embeddings=True, batch_size=128,
                          show_progress_bar=False).astype(np.float32))
            np.save(f, E)
            print(f"    saved {f.name} {E.shape}", flush=True)
        del m

if __name__ == "__main__":
    main()
