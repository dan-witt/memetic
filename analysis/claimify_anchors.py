#!/usr/bin/env python3
"""Qwen2.5-7B claim pass for any built Usenet anchor family — byte-identical pipeline to
claimify_qwen.py. Usage: claimify_anchors.py <corpora_json> <family> [family ...]
(corpora_json is the output of usenet_corpus_langs.py / usenet_corpus.py in MEMETIC_WORKDIR).
Outputs baseline_claims/<fam>_all.json in the workdir."""
import json, gc
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import os, sys
S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
OUT = S / "baseline_claims"
FAMS = sys.argv[2:]
C = json.load(open(S / sys.argv[1]))

def usenet_items(fam):
    out = []
    for r in C[fam]:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append(((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"]))
    return out

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()

def run(msgs, mx):
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]; out = []
    for i in range(0, len(pr), 16):
        enc = tok(pr[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=1500).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=mx, do_sample=False, pad_token_id=tok.pad_token_id)
        out += [tok.decode(g, skip_special_tokens=True).strip() for g in o[:, enc.input_ids.shape[1]:]]
    return out

CS, CU = "You extract the single core claim or topic of a forum post.", "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."
claimify = lambda texts: run([[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(t=t[:3000])}] for t in texts], 48)

for fam in FAMS:
    dst = OUT / f"{fam}_all.json"
    if dst.exists():
        print(f"{fam}: exists, skip", flush=True); continue
    texts = usenet_items(fam)
    print(f"{fam}: {len(texts)} items", flush=True)
    cl = claimify(texts)
    json.dump(cl, open(dst, "w"))
    print(f"{fam}: saved {len(cl)}", flush=True)
    gc.collect(); torch.cuda.empty_cache()
print("langs done")
