# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""Claim-normalize the FULL corpora for the novelty-band comparison, with the byte-identical
pipeline used throughout the addendum work (Qwen2.5-7B-Instruct fp16, greedy, batch 16, CS/CU
prompt, 3000-char input truncation, 48 new tokens). Pools, in priority order:
  lisp_all, sci_all       (new Usenet baselines; roots get subject+body like posts, replies body-only)
  agent_all               (425 posts title+body + 2,465 comments body)
  catskill_all, hn_all    (whole human forums, posts+comments)
Each pool saves to baseline_claims/<pool>.json as it finishes (incremental, resumable)."""
import json, gc, os
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
OUT = S / "baseline_claims"; OUT.mkdir(exist_ok=True)

def forum_items(d):
    """posts as title+body, comments as body; chronological; returns list of texts."""
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open())
        p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, (c.get("body") or "").strip()))
    items.sort(key=lambda x: x[0])
    return [t for _, t in items if len(t) >= 20]

def usenet_items(fam):
    C = json.load(open(S / "baseline_corpora.json"))[fam]
    out = []
    for r in C:                                        # already chronological
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append(((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"]))
    return out

POOLS = [
    ("lisp_all", lambda: usenet_items("lisp")),
    ("sci_all", lambda: usenet_items("sci")),
    ("agent_all", lambda: forum_items("/home/dan/personal/memetic/data/posts")),
    ("catskill_all", lambda: forum_items(S / "catskill/posts")),
    ("hn_all", lambda: forum_items(S / "hn/posts")),
]

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
        if (i // 16) % 20 == 0: print(f"    {i+len(out)-len(out)+min(i+16,len(pr))}/{len(pr)}", flush=True)
    return out

CS, CU = "You extract the single core claim or topic of a forum post.", "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."
claimify = lambda texts: run([[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(t=t[:3000])}] for t in texts], 48)

for name, loader in POOLS:
    dst = OUT / f"{name}.json"
    if dst.exists():
        print(f"{name}: exists, skip"); continue
    texts = loader()
    print(f"{name}: {len(texts)} items", flush=True)
    cl = claimify(texts)
    json.dump(cl, open(dst, "w"))
    print(f"{name}: saved {len(cl)} claims", flush=True)
    gc.collect(); torch.cuda.empty_cache()
print("all pools done")
