# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""Second-normalizer claim pass (non-Qwen): drive a llama-server (OpenAI-compatible) with the
byte-identical CS/CU claim prompt used by the Qwen2.5-7B pipeline. Greedy, same 3000-char input
truncation, same 48-token budget, same item sequences as claimify_baselines.py (alignment-critical:
loaders copied verbatim). Pools in headline-first order; each saves incrementally.
An interrupted pool resumes from its checkpoint: see RESUME below.
Usage: claimify_v2.py <port> <outdir> [pool ...]"""
import hashlib, json, os, sys, tempfile, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
# argv is read in __main__ so LOADERS/sig_of can be imported (by claimify_resume_verify.py) without
# parsing another script's arguments or creating an outdir as an import side effect.
PORT = 8089

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

def usenet_items(fam, src="baseline_corpora.json"):
    C = json.load(open(S / src))[fam]
    out = []
    for r in C:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append(((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"]))
    return out

LOADERS = {"lisp": lambda: usenet_items("lisp"), "sci": lambda: usenet_items("sci"),
           "agent": lambda: forum_items("/home/dan/personal/memetic/data/posts"),
           "catskill": lambda: forum_items(S / "catskill/posts"),
           "hn": lambda: forum_items(S / "hn/posts"),
           "lemmy": lambda: usenet_items("lemmy", "baseline_corpora_lemmy.json"),
           # current-pull agent, truncated to the incremental claim cache so both normalizers
           # cover the SAME items. baseline_claims_gemma/agent_all.json is pull-1 (2,874) and
           # does not match the live corpus -- see lemmy_baseline report, instrument vintages.
           "agentcur": lambda: forum_items("/home/dan/personal/memetic/data/posts")[
               :len(json.load(open(S / "agent_claims_aligned.json")))],
           "groups": lambda: usenet_items("groups", "baseline_corpora_meta.json"),
           "admin": lambda: usenet_items("admin", "baseline_corpora_meta.json"),
           "netmeta": lambda: usenet_items("netmeta", "baseline_corpora_meta.json")}

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

# A power cut mid-pool used to cost the whole pool: json.dump straight onto the target can also
# leave a torn file. Write to a sibling temp and rename, so a checkpoint is either the previous
# one or the new one, never half of either.
def save_json(obj, path):
    fd, tmp = tempfile.mkstemp(dir=str(Path(path).parent), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)

# RESUME. {pool}_partial.json is an ordered prefix of the pool -- ex.map yields in submission
# order, so the filled entries are always claims[:k] -- and sampling is greedy, so finishing the
# tail later is identical to never stopping. What makes that UNSAFE is a partial left over from a
# DIFFERENT corpus: chain scripts rm the pool's _all.json before a rebuild but not its _partial,
# and a stale 34,280-item prefix would slot into a 55,223-item run without tripping any length
# check, silently pairing old claims with new items. So each checkpoint also writes a sidecar
# holding a hash of the exact item sequence, and a partial is only adopted when that hash still
# matches what the loader just produced. No sidecar (or no match) = start clean.
# analysis/claimify_resume_verify.py adopts a pre-sidecar partial after checking alignment.
def sig_of(texts):
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode()); h.update(b"\x00")
    return h.hexdigest()

def resume_at(pool, texts, sig, part, meta_p):
    """-> the claims prefix to keep ([] = start clean)."""
    if not (part.exists() and meta_p.exists()): return []
    try:
        prev, meta = json.load(part.open()), json.load(meta_p.open())
    except Exception as e:
        print(f"{pool}: unreadable checkpoint ({type(e).__name__}), starting clean", flush=True); return []
    if meta.get("sig") != sig or meta.get("n_items") != len(texts):
        print(f"{pool}: checkpoint is from a different item sequence "
              f"({meta.get('n_items')} items), starting clean", flush=True); return []
    if not (isinstance(prev, list) and prev and len(prev) <= len(texts)
            and all(isinstance(c, str) for c in prev)):
        print(f"{pool}: malformed partial, starting clean", flush=True); return []
    return prev

def run_pool(pool, out):
    dst = out / f"{pool}_all.json"
    if dst.exists():
        print(f"{pool}: exists, skip", flush=True); return
    texts = LOADERS[pool]()
    part, meta_p = out / f"{pool}_partial.json", out / f"{pool}_partial.meta.json"
    claims = [None] * len(texts)
    sig = sig_of(texts)                      # once per pool: the checkpoints reuse it
    prev = resume_at(pool, texts, sig, part, meta_p)
    done = len(prev)
    claims[:done] = prev
    if done:
        print(f"{pool}: {len(texts)} items, resuming at {done} "
              f"({100*done/len(texts):.1f}% done, {len(texts)-done} to go)", flush=True)
    else:
        print(f"{pool}: {len(texts)} items", flush=True)
    t0 = time.time()
    # Must match the server's --parallel slot count or the GPU starves: at 8 slots the 4090
    # measured 17% utilisation on the classifier pass. Same model/quant/sampler either way.
    with ThreadPoolExecutor(max_workers=int(os.environ.get("CLAIMIFY_WORKERS", "8"))) as ex:
        for j, c in enumerate(ex.map(claim_one, texts[done:])):
            i = done + j
            claims[i] = c
            if (j + 1) % 250 == 0:
                r = (j + 1) / (time.time() - t0)
                print(f"  {i+1}/{len(texts)}  {r:.1f} it/s  eta {int((len(texts)-i-1)/r/60)} min", flush=True)
                save_json([c for c in claims if c is not None], part)
                save_json({"pool": pool, "n_items": len(texts), "done": i + 1, "sig": sig}, meta_p)
    save_json(claims, dst)
    errs = sum(1 for c in claims if c.startswith("[NORMALIZER-ERROR"))
    print(f"{pool}: saved {len(claims)} claims ({errs} errors) in {int(time.time()-t0)}s", flush=True)

if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    OUT = S / (sys.argv[2] if len(sys.argv) > 2 else "baseline_claims_gemma"); OUT.mkdir(exist_ok=True)
    for pool in (sys.argv[3:] or ["lisp", "agent", "sci", "catskill", "hn"]):
        run_pool(pool, OUT)
    print("done")
