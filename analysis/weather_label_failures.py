#!/usr/bin/env python3
"""What the allocation classifier actually says when it fails to answer VENUE or WORLD.

The allocation cell caches a label only when the answer STARTS WITH "VENUE" or "WORLD"
(weather_gpu.py). Anything else caches nothing and is retried next issue, which is the
retro-movement channel issue #6 found. Issue #6's watch item #5 set the trigger: if the
uncovered count grows rather than converges, the prompt -- not the cache -- is the problem.

It grew (72 -> 83 at issue #7) and, more tellingly, ZERO of the 72 published-day failures
resolved on retry. That is what decoding predicts: generation is greedy (do_sample=False), so
the same item under the same prompt gives the same answer every issue. The only reason a retry
can EVER resolve is that batch composition changes the padding, which perturbs the logits at the
margin -- which is exactly the one resolution issue #6 saw out of 66. Retrying is not a repair
mechanism, it is a lottery with a ~1% hit rate.

This re-runs the FROZEN prompt over the currently-unlabelled items, prints the raw answers, and
sizes what a relaxed parse would recover -- WITHOUT changing the published series. Adopting a
different parse changes the denominator on every day at once, which is a series break and has to
be decided and disclosed, not slipped in. The counterfactual per-day shares printed here are what
that decision costs.

Usage: MEMETIC_WORKDIR=... WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_label_failures.py
"""
import json, os, sys, datetime as dt
from collections import Counter
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_nn_refresh as NNR
import weather_alloc_parse as AP   # strict/relaxed/corrected parse + observed WORLD phrasings

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]
CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")

# the frozen prompt, character-identical to weather_gpu.py's
ACS = "You classify one-sentence summaries of forum posts."
ACU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
       "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
       "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")

strict, relaxed, corrected = AP.strict, AP.relaxed, AP.corrected

def lvalid(c):
    return len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"

NEW = NNR.load_items("/home/dan/personal/memetic/data/posts", CUTOFF)
cache = {(k0, int(k1)): c for (k0, k1), c in
         ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
claims = [cache[k] for _, k, _, _ in NEW]
lcache = json.load(open(S / "allocation_label_cache_agent.json"))
todo = [(i, claims[i]) for i, (t, k, x, a) in enumerate(NEW)
        if f"{k[0]}:{k[1]}" not in lcache and lvalid(claims[i])]
print(f"currently unlabelled, valid-claim items: {len(todo)}")
if not todo: sys.exit(0)

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16,
                                           device_map="cuda").eval()
msgs = [[{"role": "system", "content": ACS}, {"role": "user", "content": ACU.format(c=c[:400])}] for _, c in todo]
pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
raw = []
for i in range(0, len(pr), 32):
    enc = tok(pr[i:i+32], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
    with torch.no_grad():
        o = gen.generate(**enc, max_new_tokens=6, do_sample=False, pad_token_id=tok.pad_token_id)
    raw += [tok.decode(g, skip_special_tokens=True).strip().upper() for g in o[:, enc.input_ids.shape[1]:]]

cnt = Counter(raw)
print("\nraw answers (verbatim, truncated at 6 new tokens), by frequency:")
for w, n in cnt.most_common(30):
    print(f"  {n:4d}  {w!r}")
rec_s = sum(1 for w in raw if strict(w))
rec_r = sum(1 for w in raw if relaxed(w))
print(f"\nstrict parse recovers {rec_s}/{len(raw)}   (a nonzero count here is batch-composition"
      f" nondeterminism, not new information)")
print(f"relaxed parse recovers {rec_r}/{len(raw)}   ({len(raw) - rec_r} answers name neither word)")

# counterfactual: what the published series would read if the relaxed parse were adopted.
lc2 = dict(lcache)
for (i, _), w in zip(todo, raw):
    l = relaxed(w)
    if l: lc2[f"{NEW[i][1][0]}:{NEW[i][1][1]}"] = l
def daily(lc):
    ds = {}
    for i, (t, k, x, a) in enumerate(NEW):
        if not lvalid(claims[i]): continue
        l = lc.get(f"{k[0]}:{k[1]}")
        if l: ds.setdefault(DAY(t), []).append(l == "V")
    return {d: (round(float(np.mean(v)), 4), len(v)) for d, v in sorted(ds.items()) if len(v) >= 50}
a, b = daily(lcache), daily(lc2)
print(f"\nper-day venue share, published strict parse -> relaxed-parse counterfactual:")
worst = 0.0
for d in a:
    dv = b[d][0] - a[d][0]; worst = max(worst, abs(dv))
    print(f"  {d}  {a[d][0]:.4f} (n={a[d][1]})  ->  {b[d][0]:.4f} (n={b[d][1]})   {dv:+.4f}")
print(f"\nlargest absolute day move under the relaxed parse: {worst:.4f}")

# --- coverage correction -------------------------------------------------------------------
# If the failures are ONE-SIDED -- every unparseable answer semantically picking the same class --
# then dropping them is not noise, it is bias with a known direction, and the corrected series is
# computable without re-classifying anything: v stays, the denominator gains the uncovered items.
# WORLD_ANSWERS lists the verbatim strings this pass observed that unambiguously choose the
# second branch of the frozen question ("...or about its SUBJECT MATTER or the outside world?").
# It is a list of OBSERVED strings, deliberately not a pattern: a new failure string must be seen
# and added here, never matched speculatively.
WORLD_ANSWERS = AP.WORLD_ANSWERS
unresolved = [w for w in raw if not relaxed(w)]
onesided = all(w in WORLD_ANSWERS for w in unresolved) and bool(unresolved)
print(f"\nall {len(unresolved)} unresolved answers are known WORLD phrasings: {onesided}")
corrected = {}
if onesided:
    unc = {}
    for (i, _), w in zip(todo, raw):
        if not relaxed(w): unc[DAY(NEW[i][0])] = unc.get(DAY(NEW[i][0]), 0) + 1
    print("coverage-corrected series (every uncovered item counted WORLD; v unchanged, n grows):")
    for d, (sh, n) in a.items():
        v = round(sh * n); n2 = n + unc.get(d, 0)
        corrected[d] = round(v / n2, 4)
        print(f"  {d}  published {sh:.4f} (v={v}/n={n})  ->  corrected {corrected[d]:.4f} "
              f"(v={v}/n={n2})   {corrected[d] - sh:+.4f}")
    mv = max(abs(corrected[d] - a[d][0]) for d in a)
    print(f"  largest absolute day move: {mv:.4f}; every move is <= 0 by construction, so the "
          f"published series is an UPPER bound on venue share.")

out = S / "weather_label_failures_out.json"
out.write_text(json.dumps({"cutoff": _c, "unlabelled": len(todo),
    "raw_answer_counts": dict(cnt), "strict_recovered": rec_s, "relaxed_recovered": rec_r,
    "per_day_strict": {d: v[0] for d, v in a.items()},
    "per_day_relaxed_counterfactual": {d: v[0] for d, v in b.items()},
    "largest_day_move": round(worst, 4),
    "unresolved_all_world_phrasings": bool(onesided),
    "per_day_coverage_corrected": corrected}, indent=1))
print(f"saved {out}")
