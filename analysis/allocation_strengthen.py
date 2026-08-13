#!/usr/bin/env python3
"""Allocation strengtheners (all Qwen-classifier side):
 A. Normalizer-stage check: venue share on GEMMA-normalized claims (agent pull-1, lisp full)
    vs the same items' Qwen-normalized labels — does the allocation contrast survive a
    different claim author?
 B. Raw-item direct classification (800 agent + 800 lisp, no normalizer at all).
 C. Three-way decomposition on the full agent pool: VENUE / GENERAL-AI / WORLD — sizes the
    contested boundary mass explicitly.
 D. Negative keyword control (CPU): technical-keyword claims should skew WORLD.
Outputs allocation_strengthen.json."""
import json, re, gc, datetime as dt
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path(".")
CUTOFF = dt.datetime(2026, 8, 13, 0, 0, tzinfo=dt.timezone.utc).timestamp()
labels = json.load(open("allocation_labels.json"))
agent3 = json.load(open("agent3_all.json"))
g_agent = json.load(open("baseline_claims_gemma/agent_all.json"))     # pull-1, 2874
g_lisp = json.load(open("baseline_claims_gemma/lisp_all.json"))       # full, 5721
q_lisp = json.load(open("baseline_claims/lisp_all.json"))

def agent_raw():
    out = []
    for f in Path("/home/dan/personal/memetic/data/posts").glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        out.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            out.append((tc, (c.get("body") or "").strip()))
    out.sort(key=lambda x: x[0])
    return [x for t, x in out if len(x) >= 20 and t < CUTOFF]
def lisp_raw():
    C = json.load(open("baseline_corpora.json"))["lisp"]
    return [((r["subject"] + "\n\n" + r["text"]).strip() if (r["root"] == r["msgid"] or not r["msgid"]) else r["text"])
            for r in C if len(r["text"]) >= 20]

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
CS = "You classify one-sentence summaries of forum posts."
CU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
      "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
      "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")
CS_RAW = "You classify forum posts."
CU_RAW = ("Post:\n{c}\n\nIs this post about the forum or community ITSELF (its rules, governance, "
          "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
          "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")
CU3 = ("Claim: {c}\n\nClassify this claim into exactly one category:\n"
       "VENUE — about this forum/community itself (its rules, governance, moderation, funds, members, norms, or its quality)\n"
       "GENERAL — about AI agents, models, or LLMs in general (as a phenomenon or class, not this specific community)\n"
       "WORLD — about any other subject matter or the outside world\n"
       "Answer with exactly one word: VENUE or GENERAL or WORLD.")

def run(sys_p, user_t, texts, cut, words, mx=6, bs=32, maxlen=900):
    msgs = [[{"role": "system", "content": sys_p}, {"role": "user", "content": user_t.format(c=x[:cut])}] for x in texts]
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
    out = []
    for i in range(0, len(pr), bs):
        enc = tok(pr[i:i+bs], return_tensors="pt", padding=True, truncation=True, max_length=maxlen).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=mx, do_sample=False, pad_token_id=tok.pad_token_id)
        for g in o[:, enc.input_ids.shape[1]:]:
            w = tok.decode(g, skip_special_tokens=True).strip().upper()
            out.append(next((lbl for lbl in words if w.startswith(lbl)), None))
        if (i // bs) % 40 == 0: print(f"    {min(i+bs, len(pr))}/{len(pr)}", flush=True)
    return out

def valid(c): return len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"
def share(lab): 
    ok = [l for l in lab if l is not None]
    return round(float(np.mean([l == "VENUE" for l in ok])), 4), len(ok)

out = {}
# A: gemma-normalized claims through the same classifier
for name, cl in [("agent_pull1_gemma_norm", g_agent), ("lisp_gemma_norm", g_lisp)]:
    idx = [i for i, c in enumerate(cl) if valid(c)]
    lab = run(CS, CU, [cl[i] for i in idx], 400, ("VENUE", "WORLD"))
    out[name] = dict(zip(("venue_share", "n"), share(lab)))
    print(name, out[name], flush=True)
q1 = labels["agent"][:2874]
out["agent_pull1_qwen_norm_reference"] = {"venue_share": round(float(np.mean([l == "V" for l in q1 if l])), 4),
                                          "n": sum(1 for l in q1 if l)}
out["lisp_qwen_norm_reference"] = {"venue_share": 0.103, "n": 5506}
# B: raw items, no normalizer
rng = np.random.default_rng(1)
ar, lr = agent_raw(), lisp_raw()
for name, pool in [("agent_raw_direct", ar), ("lisp_raw_direct", lr)]:
    samp = [pool[i] for i in rng.choice(len(pool), 800, replace=False)]
    lab = run(CS_RAW, CU_RAW, samp, 1500, ("VENUE", "WORLD"), maxlen=900)
    out[name] = dict(zip(("venue_share", "n"), share(lab)))
    print(name, out[name], flush=True)
# C: three-way on full agent pool
idx = [i for i, c in enumerate(agent3) if valid(c)]
lab3 = run(CS, CU3, [agent3[i] for i in idx], 400, ("VENUE", "GENERAL", "WORLD"))
ok = [l for l in lab3 if l is not None]
out["agent_three_way"] = {"venue": round(float(np.mean([l == "VENUE" for l in ok])), 4),
                          "general_ai": round(float(np.mean([l == "GENERAL" for l in ok])), 4),
                          "world": round(float(np.mean([l == "WORLD" for l in ok])), 4), "n": len(ok)}
print("three-way:", out["agent_three_way"], flush=True)
# D: negative keyword control (CPU)
TECH = re.compile(r"compiler|garbage collect|recursion|syntax|floating.point|wavelength|protein|stack|pointer|benchmark", re.I)
for k, f in [("lisp", "baseline_claims/lisp_all.json"), ("forth", "baseline_claims/forth_all.json"), ("agent", "agent3_all.json")]:
    cl = json.load(open(f)); lab = labels[k]
    hits = [i for i, c in enumerate(cl) if valid(c) and lab[i] is not None and TECH.search(c)]
    if hits:
        out.setdefault("negative_control", {})[k] = {"n_tech_keyword": len(hits),
            "world_share": round(float(np.mean([lab[i] == "W" for i in hits])), 3)}
print("negative control:", out.get("negative_control"), flush=True)
json.dump(out, open("allocation_strengthen.json", "w"), indent=1)
print("saved allocation_strengthen.json")
