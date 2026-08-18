#!/usr/bin/env python3
"""Cross-family agreement for the allocation classifier: Gemma-3-12B (llama-server, identical
prompt) on a stratified sample; Cohen's kappa + per-pool share deltas. Output: allocation_agree.json"""
import json, os, sys, time, urllib.request
from pathlib import Path
import numpy as np
S = Path(".")
# Labels file / pool subset / sample size are parameterised so a new pool can be checked with
# the SAME instrument without re-running the published seven. Defaults reproduce the published run.
LABELS = os.environ.get("ALLOC_LABELS", "allocation_labels.json")
SUF = os.environ.get("ALLOC_SUFFIX", "")
NSAMP = int(os.environ.get("ALLOC_NSAMPLE", "215"))
labels = json.load(open(LABELS))
POOL_FILES = {"agent": "agent3_all.json", "lisp": "baseline_claims/lisp_all.json", "sci": "baseline_claims/sci_all.json",
              "hn": "baseline_claims/hn_all.json", "forth": "baseline_claims/forth_all.json",
              "smalltalk": "baseline_claims/smalltalk_all.json", "scheme": "baseline_claims/scheme_all.json",
              "lemmy": "baseline_claims/lemmy_all.json",
              "agentcur": "agent_claims_aligned.json",
              "groups": "baseline_claims/groups_all.json",
              "admin": "baseline_claims/admin_all.json",
              "netmeta": "baseline_claims/netmeta_all.json"}
_sel = [a for a in sys.argv[1:] if not a.startswith("-")]
POOL_FILES = {k: v for k, v in POOL_FILES.items() if k in labels and (not _sel or k in _sel)}
print(f"pools: {list(POOL_FILES)}  labels={LABELS}  n/pool={NSAMP}", flush=True)
CS = "You classify one-sentence summaries of forum posts."
CU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
      "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
      "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")
rng = np.random.default_rng(0)
sample = []
for k, f in POOL_FILES.items():
    cl = json.load(open(S / f)); lab = labels[k]
    ok = [i for i, l in enumerate(lab) if l is not None]
    for i in rng.choice(ok, min(NSAMP, len(ok)), replace=False):
        sample.append((k, int(i), cl[i], lab[i]))
def ask(c, retries=3):
    body = json.dumps({"messages": [{"role": "system", "content": CS}, {"role": "user", "content": CU.format(c=c[:400])}],
                       "temperature": 0.0, "max_tokens": 6}).encode()
    for a in range(retries):
        try:
            req = urllib.request.Request("http://127.0.0.1:8089/v1/chat/completions", data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                w = json.load(r)["choices"][0]["message"]["content"].strip().upper()
            return "V" if w.startswith("VENUE") else "W" if w.startswith("WORLD") else None
        except Exception:
            time.sleep(2 * (a + 1))
    return None
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=8) as ex:
    glab = list(ex.map(lambda s: ask(s[2]), sample))
json.dump([{"pool": k, "idx": i, "qwen": q, "gemma": g} for (k, i, c, q), g in zip(sample, glab)],
          open(f"allocation_agree_pairs{SUF}.json", "w"))
pairs = [(q, g) for (k, i, c, q), g in zip(sample, glab) if g is not None]
agree = np.mean([q == g for q, g in pairs])
pv, gv = np.mean([q == "V" for q, _ in pairs]), np.mean([g == "V" for _, g in pairs])
pe = pv * gv + (1 - pv) * (1 - gv)
kappa = (agree - pe) / (1 - pe) if pe < 1 else float("nan")
per_pool = {}
for k in POOL_FILES:
    pp = [(q, g) for (kk, i, c, q), g in zip(sample, glab) if kk == k and g is not None]
    if pp: per_pool[k] = {"qwen_share": round(float(np.mean([q == "V" for q, _ in pp])), 3),
                          "gemma_share": round(float(np.mean([g == "V" for _, g in pp])), 3), "n": len(pp)}
out = {"n": len(pairs), "raw_agreement": round(float(agree), 3), "cohens_kappa": round(float(kappa), 3),
       "per_pool_shares": per_pool}
per_pool_kappa = {}
for k in POOL_FILES:
    pp = [(q, g) for (kk, i, c, q), g in zip(sample, glab) if kk == k and g is not None]
    if len(pp) > 50:
        agr = np.mean([q == g for q, g in pp])
        pv, gv = np.mean([q == "V" for q, _ in pp]), np.mean([g == "V" for _, g in pp])
        pe = pv * gv + (1 - pv) * (1 - gv)
        per_pool_kappa[k] = round(float((agr - pe) / (1 - pe)), 3) if pe < 1 else None
out["per_pool_kappa"] = per_pool_kappa
json.dump(out, open(f"allocation_agree{SUF}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
