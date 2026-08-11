#!/usr/bin/env python3
"""Weather report #1 — GPU half. (1) Delta-claimify the 3,019 new items (byte-identical Qwen
pipeline), merge with the (kind,id)-keyed cache -> full pull-2 claim sequence. (2) Compute:
rolling claim-Vendi/W time series (120/40, bge) vs frozen anchor levels; placement cells
agent2/{lisp,sci,hn} (point at full m + 40 draws at m<=1500, 3 embedders); newcomer-vs-incumbent
idea cell (bge). Outputs weather1_gpu.json + agent2_all.json."""
import json, gc, datetime as dt
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")

def load_items(d):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20]

NEW = load_items("/home/dan/personal/memetic/data/posts")
cache = {tuple(k.split(":", 1)): c for k, c in json.load(open(S / "claim_cache_agent.json")).items()}
cache = {(k0, int(k1)): c for (k0, k1), c in cache.items()}
todo = [(i, x) for i, (t, k, x, a) in enumerate(NEW) if k not in cache]
print(f"delta to claimify: {len(todo)}", flush=True)

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
CS, CU = "You extract the single core claim or topic of a forum post.", "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."
def run(msgs, mx):
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]; out = []
    for i in range(0, len(pr), 16):
        enc = tok(pr[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=1500).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=mx, do_sample=False, pad_token_id=tok.pad_token_id)
        out += [tok.decode(g, skip_special_tokens=True).strip() for g in o[:, enc.input_ids.shape[1]:]]
        if (i // 16) % 25 == 0: print(f"  {min(i+16, len(pr))}/{len(pr)}", flush=True)
    return out

new_claims = run([[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(t=x[:3000])}]
                  for _, x in todo], 48)
for (i, _), c in zip(todo, new_claims):
    cache[NEW[i][1]] = c
claims2 = [cache[k] for _, k, _, _ in NEW]
json.dump(claims2, open(S / "agent2_all.json", "w"))
json.dump({f"{k[0]}:{k[1]}": c for k, c in cache.items()}, open(S / "claim_cache_agent.json", "w"))
print(f"pull-2 claim sequence: {len(claims2)}", flush=True)
del gen, tok; gc.collect(); torch.cuda.empty_cache()

# ---------- compute ----------
from sentence_transformers import SentenceTransformer
def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

claims2 = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim" for c in claims2]
ANCH = {"lisp": "lisp_all.json", "sci": "sci_all.json", "hn": "hn_all.json"}
CL = {k: [c for c in json.load(open(S / "baseline_claims" / f)) if len(c.strip()) >= 5] for k, f in ANCH.items()}
rng = np.random.default_rng(0)
out = {"n_items": len(claims2)}
W, ST = 120, 40
for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    tag = MODEL.split("/")[-1]
    m = SentenceTransformer(MODEL, device="cuda")
    Ea = m.encode(claims2, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
    rat = {}
    for k in ANCH:
        Ex = m.encode(CL[k], normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
        mfull = int(0.8 * min(len(Ea), len(Ex)))
        point = vendi(Ea[rng.choice(len(Ea), mfull, replace=False)]) / vendi(Ex[rng.choice(len(Ex), mfull, replace=False)])
        rs = [vendi(Ea[rng.choice(len(Ea), 1500, replace=False)]) / vendi(Ex[rng.choice(len(Ex), 1500, replace=False)])
              for _ in range(40)]
        rat[k] = {"point_mfull": round(point, 3), "m_full": mfull,
                  "band_m1500": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        del Ex
    out.setdefault("placement", {})[tag] = rat
    print(f"{tag}: " + ", ".join(f"{k}={rat[k]['band_m1500'][0]}" for k in ANCH), flush=True)
    if tag == "bge-large-en-v1.5":
        ws = [(i + W // 2, vendi(Ea[i:i+W]) / W) for i in range(0, len(Ea) - W + 1, ST)]
        ts = [NEW[i][0] for i, _ in ws]
        out["rolling_series_bge"] = {"t_utc": [dt.datetime.utcfromtimestamp(t).strftime("%m-%d %H:%M") for t in ts],
                                     "vendi_over_W": [round(v, 4) for _, v in ws],
                                     "anchor_levels": {"lisp": 0.1077, "smalltalk": 0.1088, "scheme": 0.1115,
                                                       "forth": 0.1269, "sci": 0.1622, "hn": 0.1914},
                                     "pull1_mean": 0.1348}
        halves = [v for _, v in ws]
        out["rolling_halves_bge"] = {"first_half": round(float(np.mean(halves[:len(halves)//2])), 4),
                                     "second_half": round(float(np.mean(halves[len(halves)//2:])), 4)}
        print("rolling halves:", out["rolling_halves_bge"], flush=True)
        # newcomer vs incumbent idea cell: newcomers = authors first seen after pull-1 latest ts
        t_pull1_end = max(t for t, k, x, a in load_items(S / "old_corpus/data/posts"))
        first = {}
        for t, k, x, a in NEW:
            if a not in first: first[a] = t
        idx_new = [i for i, (t, k, x, a) in enumerate(NEW) if first[a] > t_pull1_end]
        idx_inc = [i for i, (t, k, x, a) in enumerate(NEW) if first[a] <= t_pull1_end and t > t_pull1_end]
        mm = int(0.8 * min(len(idx_new), len(idx_inc)))
        rs = [vendi(Ea[np.array(idx_new)][rng.choice(len(idx_new), mm, replace=False)]) /
              vendi(Ea[np.array(idx_inc)][rng.choice(len(idx_inc), mm, replace=False)]) for _ in range(40)]
        out["newcomer_over_incumbent_bge"] = {"n_newcomer_items": len(idx_new), "n_incumbent_items_post_pull1": len(idx_inc),
                                              "m": mm, "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        print("newcomer/incumbent:", out["newcomer_over_incumbent_bge"], flush=True)
    del m, Ea

json.dump(out, open(S / "weather1_gpu.json", "w"), indent=1)
print("saved weather1_gpu.json")
