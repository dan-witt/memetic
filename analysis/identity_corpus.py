#!/usr/bin/env python3
"""Build the item table for the identity pass: is a citizen's voice explained by its reported
model, by model+harness, or does the author carry signal beyond both?

Emits identity_items.json into MEMETIC_WORKDIR with one row per item:
  idx, kind, thread, ts, author, model_raw, model_family, harness, n_chars, text
plus `claim_idx` -- the index into agent_claims_aligned.json (9,217) for items inside the
claim-cache window, so the idea-level pass costs no GPU.

The model_family / harness maps below are EXHAUSTIVE and hand-written for every raw string with
>=4 items (98% of the corpus); rarer strings fall through to their own singleton family and are
dropped by the >=2-authors filter downstream. author_model is SELF-REPORTED: this map normalizes
spelling, it cannot detect a citizen misreporting its weights.

CORPUS VINTAGE -- read this before re-running. This script has no cutoff: it reads whatever
data/posts happens to contain, so a re-run against a newer corpus silently produces a DIFFERENT
study rather than reproducing the published one. results/identity was computed against data/posts
at commit ce2784c (weather issue #6's pull; last item 2026-08-19 02:49:56 UTC) = 12,725 items /
524 authors, and the hand-written family map is exhaustive AT THAT VINTAGE. Against the corpus as
of 2026-08-22 the same map leaves 89 raw strings (3.5% of items) unmapped, because the square has
since taken two large author influxes -- "100% mapped" is a property of a snapshot, not of the map.

To reproduce the published pass, point IDENTITY_POSTS at that tree:
    git archive ce2784c data/posts | tar -x -C /tmp/identity-vintage
    IDENTITY_POSTS=/tmp/identity-vintage/data/posts python3 analysis/identity_corpus.py
The script prints its item count against the published reference and warns when they differ.
"""
import json, os, collections
from pathlib import Path

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
POSTS = Path(os.environ.get("IDENTITY_POSTS",
                            Path(__file__).resolve().parent.parent / "data" / "posts"))
PUBLISHED_N_ITEMS, PUBLISHED_N_AUTHORS = 12725, 524   # results/identity, corpus at commit ce2784c

# ---------------------------------------------------------------- model families
# family -> every raw author_model string that denotes those weights. Version boundaries are
# KEPT (opus-5 != opus-4-8): different weights, different expected voice. Serving tier and
# quantization are NOT family boundaries (deepseek-v4-flash-free is the same model on a free
# tier; Q4_K_M and Q8 are the same weights) -- those ride on `harness`.
FAMILIES = {
 "claude-opus-5": ["claude-opus-5", "claude-opus-5[1m]", "human+claude-opus-5"],
 "claude-fable-5": ["claude-fable-5", "anthropic-claude-fable-5", "claude-fable-5 (human-relayed)",
                    "Fable 5"],
 "claude-sonnet-5": ["claude-sonnet-5"],
 "claude-opus-4-8": ["claude-opus-4-8"],
 "claude-opus-4-6": ["claude-opus-4-6", "claude-opus-4.6"],
 "claude-sonnet-4-6": ["claude-sonnet-4-6"],
 "claude-sonnet-4-5": ["claude-sonnet-4-5", "Sonnet 4.5", "claude-3-5-sonnet"],
 "claude-opus-4": ["claude-opus-4", "claude-opus-4.5", "claude-opus-4-5", "claude-opus-4-7"],
 "claude-unspec": ["claude-opus", "claude-code", "claude-fable", "anthropic/claude",
                   "anthropic/claude-opencode", "claude-epos-5", "claude-fable-6",
                   "anthropic/claude-sonnet-4", "claude (nullregistry architect) + scheduled cowork runner"],
 "claude-haiku-4-5": ["claude-haiku-4-5", "claude-haiku-4-5-20251001"],
 "deepseek-v4-flash": ["deepseek-v4-flash", "deepseek-v4-flash-free", "ollama/deepseek-v4-flash:cloud",
                       "ollama-cloud/deepseek-v4-flash:0731", "opencode/deepseek-v4-flash-free",
                       "openrouter/~deepseek/deepseek-v4-flash-latest", "deepseek-v4-flash-0731",
                       "deepseek/deepseek-v4-flash-0731", "deepseek-flash"],
 "deepseek-v4-pro": ["deepseek-v4-pro", "opencode/deepseek-v4-pro",
                     "deepseek-v4-pro (Hermes Agent by Nous Research)"],
 "grok-4.5": ["grok-4.5", "cursor-grok-4.5"],
 "grok-4": ["grok-4"],
 "grok-4.6": ["objectpermanence/grok-4.6"],
 "gpt-5.6-sol": ["gpt-5.6-sol", "openai/gpt-5.6-sol", "GPT-5.6 Sol", "openai-codex/gpt-5.6-sol",
                 "GPT-5.6 Sol — human-relayed"],
 "gpt-5.6-luna": ["gpt-5.6-luna", "openai/gpt-5.6-luna", "5.6 luna"],
 "gpt-5.6-unspec": ["GPT-5.6", "GPT-5.6 Thinking via ChatGPT", "GPT-5.6 Thinking",
                    "openai-codex/gpt-5.6-terra", "objectpermanence/gpt-5.6-terra",
                    "gpt-5.6-pro", "gpt-5.6-opus"],
 "gpt-5": ["gpt-5", "gpt-5-codex", "openai-codex", "openai-codex-gpt-5", "openai/codex-gpt-5",
           "OpenAI Codex (GPT-5)", "openai-gpt-5", "openai-codex-gpt-5-human-relayed",
           "gpt-5-codex-openclaw", "openai-codex/gpt-5.5 via OpenClaw", "GPT-5"],
 "gpt-5.4-mini": ["gpt-5.4-mini"],
 "gpt-6-high": ["gpt-6-high"],
 "glm-5.2": ["glm-5.2", "z-ai/glm-5.2", "glm-5.2:cloud", "vllm/glm-5.2", "glm-5.2-vision-background"],
 "glm-5.3": ["glm-5.3"],
 "glm-5-turbo": ["glm-5-turbo"],
 "qwen3.6-35b": ["qwen3.6:35b", "Qwen3.6-35B-A3B-GGUF:Q4_K_M", "Qwen3.6-35B-A3B-UD-Q8_K_XL",
                 "llama-server/Qwen-3.6-35B-MTP"],
 "qwen3.6-27b": ["qwen3.6-27b", "Prometheus/Qwen3.6-27B"],
 "qwen3.8-27b": ["qwen3.8:27b", "Qwen3.8-27B-GGUF", "qwen3.8-27b", "llama.cpp/Qwen-3.8-27B-Q8"],
 "qwen3-8b": ["qwen3-8b-q4km", "qwen3:8b", "qwen3"],
 "mimo-v2.5": ["mimo-v2.5-free", "xiaomi/mimo-v2.5"],
 "muse-glimmer-30b": ["muse-glimmer:30b", "ollama/muse-glimmer:30b"],
 "gemini-3.6-flash": ["gemini-3.6-flash"],
 "gemini-3.1-pro": ["gemini-3.1-pro", "gemini-3.1-pro-high", "Gemini 3.1 Pro"],
 "gemini-unspec": ["gemini", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash"],
 "gemma4": ["ollama/gemma4:31b", "gemma4:26b", "Gemma-4-E4B"],
 "kimi": ["kimi-k3", "kimi-k2p6", "kimi (moonshot); exact version unknown to citizen",
          "ollama-cloud/kimi-k2.7-code"],
 "minimax-m3": ["minimax-m3; same keeper as ike; works below", "minimax-m3; same keeper as ike; reset often",
                "MiniMax-M3 (Hermes Agent)"],
 "mistral": ["mistral-small-2603", "mistral-large-2407"],
 "hermes3": ["nousresearch/hermes3-0827", "hermes-agent", "hermes/agent-on-vps", "Hermes Agent"],
 "swe-1.7-max": ["SWE-1.7-Max"],
 "laguna-s-2.1": ["poolside/laguna-s-2.1:free"],
 "nemekai-v4": ["Nemekai-V4", "nemekai-v4"],
 "reasonix": ["reasonix", "reasonix-v1.20"],
 "bankr": ["bankr-v1", "bankr-agent"],
 # non-model / refused / unresolvable self-reports. Kept as a labelled bucket, never silently
 # dropped -- 223 items say "undisclosed" and that is itself a stance.
 "undisclosed": ["undisclosed", "unknown", "human", "Human", "n.a", "your-model-id", "保卫",
                 "many; the record is the constant", "agent", "agent-index", "echo", "pi",
                 "mixed-local-fleet", "arena-multi", "auto/coding:free",
                 "Big-Johns-Shiny-Box-of-Wires", "object-permanence", "MathModel", "vivi-1",
                 "Manus AI", "lmstudio-bionic", "qoder-agent", "Atinamos-Agent", "mr-money-ai",
                 "perplexity-computer", "glee-envoy/buffy", "muse-spark-1.2", "qwen-haiku",
                 "qwen3.8-max-preview", "qwen3.5-122b", "Qwen3.8", "GLM4", "grok",
                 "cursor/composer", "hermes-bridge-burner/tencent-hy3",
                 "Tencent Hunyuan Hy3 + DeepSeek-V4 Pro",
                 "deepseek-v4-flash + gpt-5.6 luna mixed"],
}
RAW2FAM = {r: f for f, rs in FAMILIES.items() for r in rs}

# ---------------------------------------------------------------- harness
# The scaffold the weights run inside, where the citizen disclosed it in the model string.
# This is what makes the "model + harness = a few clusters per model" hypothesis testable:
# cursor-grok-4.5 (845 items) vs bare grok-4.5 (287) is the same weights, two scaffolds.
HARNESS = {
 "cursor": ["cursor-grok-4.5", "cursor/composer"],
 "codex": ["gpt-5-codex", "openai-codex", "openai-codex-gpt-5", "openai/codex-gpt-5",
           "OpenAI Codex (GPT-5)", "openai-codex/gpt-5.6-sol", "openai-codex/gpt-5.6-terra",
           "openai-codex-gpt-5-human-relayed", "gpt-5-codex-openclaw",
           "openai-codex/gpt-5.5 via OpenClaw"],
 "ollama": ["ollama/deepseek-v4-flash:cloud", "ollama-cloud/deepseek-v4-flash:0731",
            "ollama/muse-glimmer:30b", "ollama/gemma4:31b", "ollama-cloud/kimi-k2.7-code"],
 "opencode": ["opencode/deepseek-v4-pro", "opencode/deepseek-v4-flash-free",
              "anthropic/claude-opencode"],
 "openrouter": ["openrouter/~deepseek/deepseek-v4-flash-latest"],
 "local-gguf": ["Qwen3.6-35B-A3B-GGUF:Q4_K_M", "Qwen3.6-35B-A3B-UD-Q8_K_XL", "Qwen3.8-27B-GGUF",
                "llama.cpp/Qwen-3.8-27B-Q8", "llama-server/Qwen-3.6-35B-MTP", "qwen3-8b-q4km",
                "lmstudio-bionic", "vllm/glm-5.2"],
 "claude-code": ["claude-code"],
 "hermes": ["nousresearch/hermes3-0827", "hermes-agent", "hermes/agent-on-vps", "Hermes Agent",
            "deepseek-v4-pro (Hermes Agent by Nous Research)", "MiniMax-M3 (Hermes Agent)",
            "hermes-bridge-burner/tencent-hy3"],
 "human-relayed": ["GPT-5.6 Sol — human-relayed", "claude-fable-5 (human-relayed)",
                   "openai-codex-gpt-5-human-relayed", "GPT-5.6 Thinking via ChatGPT",
                   "human+claude-opus-5"],
 "free-tier": ["deepseek-v4-flash-free", "mimo-v2.5-free", "poolside/laguna-s-2.1:free",
               "auto/coding:free"],
}
RAW2HARNESS = {r: h for h, rs in HARNESS.items() for r in rs}
# A raw string can name both a harness and a tier. This comprehension is LAST-wins (a later key
# overwrites an earlier one), not first-wins as this comment claimed until issue-#10's review:
# 'openai-codex-gpt-5-human-relayed' appears under both `codex` and `human-relayed` and resolves to
# `human-relayed`. The collisions are listed explicitly below rather than left to dict order.

def forum_items(d):
    """EXACTLY the ordering of analysis/claimify_server.py:forum_items -- posts as title+body,
    comments as body, chronological, >=20 chars. The claim caches are index-aligned to this."""
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open())
        p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append(dict(kind="post", id=p["id"], thread=p["id"], ts=t, author=p["author"],
                          model_raw=p.get("author_model"),
                          text=((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append(dict(kind="comment", id=c["id"], thread=p["id"], ts=tc, author=c["author"],
                              model_raw=c.get("author_model"), text=(c.get("body") or "").strip()))
    items.sort(key=lambda x: x["ts"])
    return [x for x in items if len(x["text"]) >= 20]

def main():
    items = forum_items(POSTS)
    for i, it in enumerate(items):
        raw = it["model_raw"]
        it["idx"] = i
        it["model_family"] = RAW2FAM.get(raw, "other:" + str(raw))
        it["harness"] = RAW2HARNESS.get(raw, "bare")
        it["n_chars"] = len(it["text"])

    # ---- claim alignment. agent_rows_aligned.json is [ts, author] for the 9,217 claim-cache
    # items; verify index-for-index rather than trusting the length assert alone.
    rows = json.load(open(S / "agent_rows_aligned.json"))
    n = len(rows)
    bad = [i for i in range(n) if abs(items[i]["ts"] - rows[i][0]) > 1e-6 or items[i]["author"] != rows[i][1]]
    if bad:
        raise SystemExit(f"claim alignment broken at {len(bad)} indices, first={bad[:5]}")
    for i in range(n):
        items[i]["claim_idx"] = i

    # ---- audit
    unmapped = collections.Counter(it["model_raw"] for it in items if it["model_family"].startswith("other:"))
    fam = collections.Counter(it["model_family"] for it in items)
    _na = len({i["author"] for i in items})
    print(f"items={len(items)}  claim-aligned={n}  authors={_na}")
    if (len(items), _na) != (PUBLISHED_N_ITEMS, PUBLISHED_N_AUTHORS):
        print(f"  !! OFF-VINTAGE: results/identity published {PUBLISHED_N_ITEMS} items / "
              f"{PUBLISHED_N_AUTHORS} authors (data/posts at commit ce2784c). This run is a "
              f"DIFFERENT study, not a reproduction -- see the module docstring for IDENTITY_POSTS.")
    print(f"families={len(fam)}  unmapped raw strings={len(unmapped)} covering {sum(unmapped.values())} items "
          f"({100*sum(unmapped.values())/len(items):.1f}%)")
    for r, c in unmapped.most_common(10):
        print(f"   unmapped {c:4d}  {r!r}")
    print("top families:", ", ".join(f"{k}={v}" for k, v in fam.most_common(8)))
    hz = collections.Counter(it["harness"] for it in items)
    print("harness:", ", ".join(f"{k}={v}" for k, v in hz.most_common()))
    # RAW2FAM's values are family keys by construction, so the old check here
    # (`RAW2FAM[r].startswith("other:")`) could never fire. Audit the real hazard instead: raw
    # strings claimed by more than one family or harness list, where the comprehension silently
    # keeps the last one.
    for name, table in (("FAMILIES", FAMILIES), ("HARNESS", HARNESS)):
        seen, clash = {}, []
        for key, raws in table.items():
            for r in raws:
                if r in seen and seen[r] != key:
                    clash.append((r, seen[r], key))
                seen[r] = key
        if clash:
            print(f"  note: {len(clash)} raw string(s) claimed by two {name} keys; "
                  f"last listed wins: " + ", ".join(f"{r!r} {a}->{b}" for r, a, b in clash))
    json.dump(items, open(S / "identity_items.json", "w"))
    print(f"saved {S/'identity_items.json'}")

if __name__ == "__main__":
    main()
