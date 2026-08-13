#!/usr/bin/env python3
"""Weather issue #2 — GPU half. Cutoff 2026-08-13T00:00Z everywhere. Delta-claimify new items
(cache keyed by kind:id). Compute: rolling claim-Vendi series; placement vs frozen anchors (full
pool AND issue-window-only cells, 3 embedders); newcomer cells (within-pool parity + NEW
cross-pool refresh: union-vs-incumbent Vendi and nearest-incumbent claim distance). Outputs
weather2_gpu.json + agent3_all.json."""
import json, gc, datetime as dt
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
CUTOFF = dt.datetime(2026, 8, 13, 0, 0, tzinfo=dt.timezone.utc).timestamp()

def load_items(d, cutoff=CUTOFF):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]

NEW = load_items("/home/dan/personal/memetic/data/posts")
prev_last = max(t for t, _, _, _ in load_items(S / "old_corpus2/data/posts"))
cache = {(k0, int(k1)): c for (k0, k1), c in
         ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
todo = [(i, x) for i, (t, k, x, a) in enumerate(NEW) if k not in cache]
print(f"delta to claimify: {len(todo)}", flush=True)

if todo:
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
    CS, CU = "You extract the single core claim or topic of a forum post.", "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."
    msgs = [[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(t=x[:3000])}] for _, x in todo]
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
    outs = []
    for i in range(0, len(pr), 16):
        enc = tok(pr[i:i+16], return_tensors="pt", padding=True, truncation=True, max_length=1500).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=48, do_sample=False, pad_token_id=tok.pad_token_id)
        outs += [tok.decode(g, skip_special_tokens=True).strip() for g in o[:, enc.input_ids.shape[1]:]]
        if (i // 16) % 25 == 0: print(f"  {min(i+16, len(pr))}/{len(pr)}", flush=True)
    for (i, _), c in zip(todo, outs): cache[NEW[i][1]] = c
    json.dump({f"{k[0]}:{k[1]}": c for k, c in cache.items()}, open(S / "claim_cache_agent.json", "w"))
    del gen, tok; gc.collect(); torch.cuda.empty_cache()

claims = [cache[k] for _, k, _, _ in NEW]
json.dump(claims, open(S / "agent3_all.json", "w"))
claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim" for c in claims]

from sentence_transformers import SentenceTransformer
def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

ANCH = {"lisp": "lisp_all.json", "sci": "sci_all.json", "hn": "hn_all.json"}
CL = {k: [c for c in json.load(open(S / "baseline_claims" / f)) if len(c.strip()) >= 5] for k, f in ANCH.items()}
rng = np.random.default_rng(0)
win_idx = [i for i, (t, k, x, a) in enumerate(NEW) if t > prev_last]
out = {"n_items": len(claims), "issue_window_items": len(win_idx)}
W, ST = 120, 40
for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    tag = MODEL.split("/")[-1]
    m = SentenceTransformer(MODEL, device="cuda")
    Ea = m.encode(claims, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
    for k in ANCH:
        Ex = m.encode(CL[k], normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
        cells = {}
        for label, pool in [("full", np.arange(len(Ea))), ("window_only", np.array(win_idx))]:
            md = min(1500, int(0.8 * min(len(pool), len(Ex))))
            rs = [vendi(Ea[pool][rng.choice(len(pool), md, replace=False)]) /
                  vendi(Ex[rng.choice(len(Ex), md, replace=False)]) for _ in range(40)]
            cells[label] = {"m": md, "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        out.setdefault("placement", {}).setdefault(tag, {})[k] = cells
    print(f"{tag}: " + ", ".join(f"{k} full={out['placement'][tag][k]['full']['band'][0]} win={out['placement'][tag][k]['window_only']['band'][0]}" for k in ANCH), flush=True)
    if tag == "bge-large-en-v1.5":
        ws = [(i + W // 2, vendi(Ea[i:i+W]) / W) for i in range(0, len(Ea) - W + 1, ST)]
        out["rolling_series_bge"] = {"t_utc": [dt.datetime.utcfromtimestamp(NEW[i][0]).strftime("%m-%d %H:%M") for i, _ in ws],
                                     "vendi_over_W": [round(v, 4) for _, v in ws]}
        halves = [v for _, v in ws]
        out["rolling_halves_bge"] = {"first_half": round(float(np.mean(halves[:len(halves)//2])), 4),
                                     "second_half": round(float(np.mean(halves[len(halves)//2:])), 4)}
        # newcomer cells within the issue window
        first = {}
        for t, k, x, a in NEW:
            if a not in first: first[a] = t
        idx_newc = [i for i in win_idx if first[NEW[i][3]] > prev_last]
        idx_inc = [i for i in win_idx if first[NEW[i][3]] <= prev_last]
        out["newcomer_counts"] = {"newcomer_items": len(idx_newc), "incumbent_items": len(idx_inc)}
        if len(idx_newc) >= 100 and len(idx_inc) >= 100:
            mm = int(0.8 * min(len(idx_newc), len(idx_inc)))
            rs = [vendi(Ea[np.array(idx_newc)][rng.choice(len(idx_newc), mm, replace=False)]) /
                  vendi(Ea[np.array(idx_inc)][rng.choice(len(idx_inc), mm, replace=False)]) for _ in range(40)]
            out["newcomer_within_pool_parity"] = {"m": mm, "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
            # cross-pool refresh 1: union vs incumbent at fixed size
            mm2 = min(len(idx_newc), len(idx_inc))
            rs_u, rs_i = [], []
            for _ in range(40):
                inc = np.array(idx_inc)[rng.choice(len(idx_inc), mm2, replace=False)]
                nwc = np.array(idx_newc)[rng.choice(len(idx_newc), mm2 // 2, replace=False)]
                union = np.concatenate([inc[:mm2 - len(nwc)], nwc])
                rs_u.append(vendi(Ea[union])); rs_i.append(vendi(Ea[inc]))
            ratio = [round(float(np.percentile(np.array(rs_u) / np.array(rs_i), p)), 3) for p in (50, 5, 95)]
            out["refresh_union_over_incumbent"] = {"m": mm2, "band": ratio,
                "read": ">1 = newcomer claims add effective distinct content beyond incumbents'"}
            # cross-pool refresh 2: nearest-incumbent distance
            En, Ei = Ea[np.array(idx_newc)], Ea[np.array(idx_inc)]
            nn_new = 1 - (En @ Ei.T).max(1)
            half = rng.permutation(len(Ei)); h1, h2 = half[:len(half)//2], half[len(half)//2:]
            nn_base = 1 - (Ei[h1] @ Ei[h2].T).max(1)
            out["refresh_nn_distance"] = {"newcomer_to_incumbent_median": round(float(np.median(nn_new)), 4),
                                          "incumbent_to_incumbent_median": round(float(np.median(nn_base)), 4),
                                          "read": "newcomer >> baseline = newcomers far from the incumbent claim cloud"}
            print("newcomer cells:", out["newcomer_within_pool_parity"], out["refresh_union_over_incumbent"],
                  out["refresh_nn_distance"], flush=True)
    del m, Ea

json.dump(out, open(S / "weather2_gpu.json", "w"), indent=1)
print("saved weather2_gpu.json")
