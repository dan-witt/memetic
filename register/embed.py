#!/usr/bin/env python3
"""Content side of #4191's GPU-SPEC: embed the thread comments, raw and style-ablated.

Two variants per embedder:
  raw      text as written, with the same handle/URL/code stripping style-features.js applied
  ablated  the same text with the seven style markers deleted (the spec's decider for
           whether a family effect on embeddings is content or register leaking through)

Writes reg4191_{variant}_{tag}.npy + reg4191_rows.json into MEMETIC_WORKDIR.
"""
import json, os, re, sys
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
D = Path("/home/dan/personal/memetic/data/posts")
EMBEDDERS = [("bge", "BAAI/bge-large-en-v1.5"), ("gte", "thenlper/gte-large")]
CHUNK = 1800

# Verbatim from the sandbox's analysis/style-features.js, so the content side ablates exactly
# the markers the style side counts. Not our marker design; replicating theirs.
CLEAN = [(re.compile(r"@[A-Za-z0-9_-]+"), " "), (re.compile(r"https?://\S+"), " "),
         (re.compile(r"`[^`]*`"), " "), (re.compile(r"cost-is-not-value", re.I), " ")]
MARKERS = [re.compile(p, re.I) for p in [
    r"\b(never|every|nothing|always|none|zero|all|any)\b",
    r"\b(isn't|wasn't|didn't|doesn't|cannot|can't|won't|not)\b",
    r"\b(because|therefore|since|so that|which is why|hence)\b",
    r"\b(same|than|rather|instead|unlike|whereas|versus)\b",
    r"(?:^|[^A-Za-z])(I|I'm|I've|my|me|myself|mine)(?:[^A-Za-z]|$)"]]

def clean(b):
    for rx, sub in CLEAN: b = rx.sub(sub, b)
    return b
def ablate(b):
    for rx in MARKERS: b = rx.sub(" ", b)
    return re.sub(r"\s+", " ", b).strip()

def chunks(t):
    out, cur = [], ""
    for para in t.split("\n\n"):
        while len(para) > CHUNK:
            cut = para.rfind(" ", 0, CHUNK); cut = cut if cut > CHUNK // 2 else CHUNK
            if cur: out.append(cur); cur = ""
            out.append(para[:cut]); para = para[cut:].lstrip()
        if len(cur) + len(para) + 2 > CHUNK and cur: out.append(cur); cur = ""
        cur = (cur + "\n\n" + para).strip() if cur else para
    if cur: out.append(cur)
    return out or [t[:CHUNK] or " "]

def encode_pooled(model, texts):
    flat, owner = [], []
    for i, t in enumerate(texts):
        for c in chunks(t): flat.append(c); owner.append(i)
    E = model.encode(flat, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    owner = np.asarray(owner)
    out = np.zeros((len(texts), E.shape[1]), dtype=np.float32)
    np.add.at(out, owner, E)
    out /= np.linalg.norm(out, axis=1, keepdims=True)
    print(f"    pooled {len(flat)} chunks -> {len(texts)} items", flush=True)
    return out

def main():
    feats = [json.loads(l) for l in open(sys.argv[1])]
    bodies, modstate = {}, {}
    for p in sorted({r["post_id"] for r in feats}):
        for c in json.load(open(D / f"{p}.json")).get("comments", []):
            bodies[c["id"]] = c.get("body") or ""; modstate[c["id"]] = c.get("mod_state")
    rows = [r for r in feats
            if r["comment_id"] in bodies and not modstate[r["comment_id"]]
            and clean(bodies[r["comment_id"]]).strip()]
    print(f"{len(feats)} feature rows -> {len(rows)} embeddable "
          f"({len(feats)-len(rows)} dropped: unjoined or platform-substituted)", flush=True)
    raw = [clean(bodies[r["comment_id"]]) for r in rows]
    abl = [ablate(t) for t in raw]
    print(f"ablation removes {100*(1-sum(map(len,abl))/sum(map(len,raw))):.1f}% of characters", flush=True)
    json.dump(rows, open(S / "reg4191_rows.json", "w"))
    for tag, name in EMBEDDERS:
        m = SentenceTransformer(name, device="cuda")
        for variant, texts in (("raw", raw), ("ablated", abl)):
            f = S / f"reg4191_{variant}_{tag}.npy"
            if f.exists(): print(f"  {f.name} exists, skipping", flush=True); continue
            print(f"  {tag}/{variant}", flush=True)
            np.save(f, encode_pooled(m, texts))
        del m
    print("done", flush=True)

main()
