#!/usr/bin/env python3
"""Weather report — GPU half. Cutoff from $WEATHER_CUTOFF (that date's midnight UTC, exclusive)
everywhere. Delta-claimify new items (cache keyed by kind:id) and evict cache entries for items
EDITED since the previous corpus. Compute: rolling claim-Vendi series; placement vs frozen
anchors (full pool AND issue-window-only cells, 3 embedders); allocation venue share/day;
newcomer cells (within-pool parity + cross-pool refresh: union-vs-incumbent Vendi and
matched-pool nearest-incumbent claim distance). Outputs weather_gpu_out.json +
agent_claims_current.json."""
import json, gc, sys, hashlib, datetime as dt
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_nn_refresh as NNR   # matched-pool NN construction, single source of truth
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import os
S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]  # e.g. "2026-08-14" = midnight UTC upper bound (exclusive)
CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()

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
PREV = load_items(S / "prev_corpus/data/posts")
prev_last = max(t for t, _, _, _ in PREV)
# items EDITED after publication: same id, different text. The id-keyed caches cannot see this,
# so evict them here and let the delta pass re-claimify / re-label them (issue-3 watch item #4).
_h = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
_ph = {k: _h(x) for _, k, x, _ in PREV}
EDITED = [k for _, k, x, _ in NEW if k in _ph and _h(x) != _ph[k]]
print(f"edited items (cache eviction): {len(EDITED)}", flush=True)
cache = {(k0, int(k1)): c for (k0, k1), c in
         ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
for k in EDITED: cache.pop(k, None)
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

claims = [cache[k] for _, k, _, _ in NEW]
json.dump(claims, open(S / "agent_claims_current.json", "w"))
# --- allocation trend: delta-classify (frozen prompt), id-keyed label cache ---
lcache = json.load(open(S / "allocation_label_cache_agent.json"))
for k in EDITED: lcache.pop(f"{k[0]}:{k[1]}", None)   # edited text -> new claim -> re-label
def lvalid(c): return len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"
todo_l = [(i, claims[i]) for i, (t, k, x, a) in enumerate(NEW)
          if f"{k[0]}:{k[1]}" not in lcache and lvalid(claims[i])]
print(f"allocation delta-classify: {len(todo_l)}", flush=True)
if todo_l:
    try: tok
    except NameError:
        tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
        if tok.pad_token is None: tok.pad_token = tok.eos_token
        gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
    ACS = "You classify one-sentence summaries of forum posts."
    ACU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
           "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
           "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")
    amsgs = [[{"role": "system", "content": ACS}, {"role": "user", "content": ACU.format(c=c[:400])}] for _, c in todo_l]
    apr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in amsgs]
    alab = []
    for i in range(0, len(apr), 32):
        enc = tok(apr[i:i+32], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=6, do_sample=False, pad_token_id=tok.pad_token_id)
        for g in o[:, enc.input_ids.shape[1]:]:
            w = tok.decode(g, skip_special_tokens=True).strip().upper()
            alab.append("V" if w.startswith("VENUE") else "W" if w.startswith("WORLD") else None)
    for (i, _), l in zip(todo_l, alab):
        if l: lcache[f"{NEW[i][1][0]}:{NEW[i][1][1]}"] = l
    json.dump(lcache, open(S / "allocation_label_cache_agent.json", "w"))
    del gen, tok; gc.collect(); torch.cuda.empty_cache()
import datetime as _dt
_day = lambda t: _dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
_ds = {}
for t, k, x, a in NEW:
    l = lcache.get(f"{k[0]}:{k[1]}")
    if l: _ds.setdefault(_day(t), []).append(l == "V")
alloc_daily = {d: round(float(np.mean(v)), 4) for d, v in sorted(_ds.items()) if len(v) >= 50}
print("allocation venue-share/day:", alloc_daily, flush=True)
claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim" for c in claims]

from sentence_transformers import SentenceTransformer
def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

ANCH = {"lisp": "lisp_all.json", "sci": "sci_all.json", "hn": "hn_all.json"}
CL = {k: [c for c in json.load(open(S / "baseline_claims" / f)) if len(c.strip()) >= 5] for k, f in ANCH.items()}
rng = np.random.default_rng(0)
win_idx = [i for i, (t, k, x, a) in enumerate(NEW) if t > prev_last]
out = {"n_items": len(claims), "issue_window_items": len(win_idx), "allocation_daily_venue_share": alloc_daily}
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
        # Two floors, deliberately different. The Vendi-based parity/union cells need enough items
        # for a stable spectrum -> m >= 100. The NN cell is a median of distances against a
        # permutation null that widens automatically as m shrinks, so it stays interpretable lower
        # -> m >= 50, and any run below VENDI_FLOOR is flagged below_standing_vendi_floor.
        VENDI_FLOOR, NN_FLOOR = 100, 50
        if len(idx_newc) >= VENDI_FLOOR and len(idx_inc) >= VENDI_FLOOR:
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
        else:
            out["newcomer_vendi_cells_skipped"] = (
                f"newcomer_items={len(idx_newc)} below the standing m>={VENDI_FLOOR} floor for the "
                f"Vendi-based parity/union cells; not computed")
        # cross-pool refresh 2: nearest-incumbent distance, MATCHED candidate pools. Construction,
        # rationale and the superseded version live in weather_nn_refresh.py — imported rather
        # than duplicated so the pipeline and the standalone run cannot drift apart.
        # weather_nn_validate.py is its synthetic null/power check.
        if len(idx_newc) >= NN_FLOOR and len(idx_inc) >= 3 * NN_FLOOR:
            En, Ei = Ea[np.array(idx_newc)], Ea[np.array(idx_inc)]
            out["refresh_nn_distance_matched"] = dict(
                NNR.matched_nn(En, Ei),
                below_standing_vendi_floor=len(idx_newc) < VENDI_FLOOR,
                read="same reference pool R, same size, disjoint from every query set; delta > null"
                     " = newcomer claims sit farther from the incumbent cloud than incumbents do"
                     " from each other. Null centres on 0 by construction; see"
                     " weather_nn_validate.py for the synthetic null/power check.")
            out["refresh_nn_distance_legacy_asymmetric"] = NNR.legacy_asymmetric(En, Ei)
            print("newcomer NN cell:", out["refresh_nn_distance_matched"], flush=True)
    del m, Ea

json.dump(out, open(S / "weather_gpu_out.json", "w"), indent=1)
print("saved weather_gpu_out.json")
