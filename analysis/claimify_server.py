# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""Second-normalizer claim pass (non-Qwen): drive a llama-server (OpenAI-compatible) with the
byte-identical CS/CU claim prompt used by the Qwen2.5-7B pipeline. Greedy, same 3000-char input
truncation, same 48-token budget, same item sequences as claimify_baselines.py (alignment-critical:
loaders copied verbatim). Pools in headline-first order; each saves incrementally.
Usage: claimify_v2.py <port> <outdir> [pool ...]"""
import json, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8089
OUT = S / (sys.argv[2] if len(sys.argv) > 2 else "baseline_claims_gemma"); OUT.mkdir(exist_ok=True)
ONLY = sys.argv[3:] or ["lisp", "agent", "sci", "catskill", "hn"]

def forum_items(d):
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
    for r in C:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append(((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"]))
    return out

LOADERS = {"lisp": lambda: usenet_items("lisp"), "sci": lambda: usenet_items("sci"),
           "agent": lambda: forum_items("/home/dan/personal/memetic/data/posts"),
           "catskill": lambda: forum_items(S / "catskill/posts"),
           "hn": lambda: forum_items(S / "hn/posts")}

CS = "You extract the single core claim or topic of a forum post."
CU = "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."

import os
NOTHINK = os.environ.get("CLAIMIFY_NOTHINK") == "1"   # Qwen3.x: force direct answers, no thinking block

def claim_one(text, retries=4):
    payload = {"messages": [{"role": "system", "content": CS},
                            {"role": "user", "content": CU.format(t=text[:3000])}],
               "temperature": 0.0, "max_tokens": 48}
    if NOTHINK: payload["chat_template_kwargs"] = {"enable_thinking": False}
    body = json.dumps(payload).encode()
    for a in range(retries):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions", data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if a == retries - 1: return f"[NORMALIZER-ERROR: {type(e).__name__}]"
            time.sleep(2 * (a + 1))

for pool in ONLY:
    dst = OUT / f"{pool}_all.json"
    if dst.exists():
        print(f"{pool}: exists, skip", flush=True); continue
    texts = LOADERS[pool]()
    print(f"{pool}: {len(texts)} items", flush=True)
    t0 = time.time()
    claims = [None] * len(texts)
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, c in enumerate(ex.map(claim_one, texts)):
            claims[i] = c
            if (i + 1) % 250 == 0:
                r = (i + 1) / (time.time() - t0)
                print(f"  {i+1}/{len(texts)}  {r:.1f} it/s  eta {int((len(texts)-i-1)/r/60)} min", flush=True)
                json.dump([c for c in claims if c is not None], open(OUT / f"{pool}_partial.json", "w"))
    json.dump(claims, open(dst, "w"))
    errs = sum(1 for c in claims if c.startswith("[NORMALIZER-ERROR"))
    print(f"{pool}: saved {len(claims)} claims ({errs} errors) in {int(time.time()-t0)}s", flush=True)
print("done")
