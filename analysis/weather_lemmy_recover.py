#!/usr/bin/env python3
"""Recover the raw classifier answers the lemmy comparator's published run DISCARDED.

Issue #7 bounded the comparator's own coverage bias without touching the frozen corpus
(`weather_lemmy_ref.coverage_bound`): 55,223 founding-month items, 55,152 classified, so at most
71 were dropped, and counting every one of them WORLD moves the platform figure 0.4665 -> 0.4659.
That is a worst case, and issue #7 said so — part of the difference is invalid claims rather than
unparsed answers.

Issue #8 adopts the corrected parse on the square's side, and correcting one side of a comparison
only would be rigged. So the comparator needs the same treatment, which needs its raw answers.
This recovers them, and it is NOT a re-measurement of the frozen corpus:

  - the 55,153 published V/W labels are read, never recomputed and never written;
  - only the items the published run left unlabelled are put back through the frozen prompt;
  - of those, only the ones with a VALID claim are eligible, by the same `lvalid` test the
    square's pipeline uses — an invalid claim is excluded from the denominator on both sides, so
    it is not an unparsed answer and must not be recovered as one.

Output: allocation_unparsed_raw_lemmy.json in the workdir, {"idx": [...], "raw": [...]}, consumed
by weather_lemmy_ref.corrected_platform(). Run once; it is deterministic (greedy decoding) and
the corpus is frozen, so re-running it is a no-op that costs a minute of GPU.

Usage: MEMETIC_WORKDIR=... python3 analysis/weather_lemmy_recover.py
"""
import json, os, sys
from collections import Counter
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_alloc_parse as AP

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))

# the frozen prompt, character-identical to weather_gpu.py's
ACS = "You classify one-sentence summaries of forum posts."
ACU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
       "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
       "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")

def lvalid(c):
    return c is not None and len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"

lab = json.load(open(S / "allocation_labels_lemmy.json"))["lemmy"]
claims = json.load(open(S / "baseline_claims/lemmy_all.json"))
assert len(lab) == len(claims), f"label/claim misalignment: {len(lab)} vs {len(claims)}"

unlabelled = [i for i, x in enumerate(lab) if x is None]
todo = [i for i in unlabelled if lvalid(claims[i])]
print(f"published labels: {sum(1 for x in lab if x in ('V','W'))} of {len(lab)}")
print(f"unlabelled: {len(unlabelled)}; of those, valid-claim (= unparsed answers): {len(todo)}; "
      f"invalid-claim (excluded from the denominator on both sides): {len(unlabelled) - len(todo)}")
if not todo:
    sys.exit(0)

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16,
                                           device_map="cuda").eval()
msgs = [[{"role": "system", "content": ACS}, {"role": "user", "content": ACU.format(c=claims[i][:400])}]
        for i in todo]
pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
raw = []
for i in range(0, len(pr), 32):
    enc = tok(pr[i:i+32], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
    with torch.no_grad():
        o = gen.generate(**enc, max_new_tokens=6, do_sample=False, pad_token_id=tok.pad_token_id)
    raw += [tok.decode(g, skip_special_tokens=True).strip().upper() for g in o[:, enc.input_ids.shape[1]:]]

print("\nraw answers, by frequency:")
for w, n in Counter(raw).most_common(30):
    print(f"  {n:4d}  {w!r}")
rs = sum(1 for w in raw if AP.strict(w))
rr = sum(1 for w in raw if AP.relaxed(w))
rc = sum(1 for w in raw if AP.corrected(w))
print(f"\nstrict recovers {rs}/{len(raw)} (nonzero = batch-composition nondeterminism vs the "
      f"published run, not new information)")
print(f"relaxed recovers {rr}/{len(raw)}")
print(f"corrected recovers {rc}/{len(raw)}  ({len(raw) - rc} still unparseable)")
cw = sum(1 for w in raw if AP.corrected(w) == "W")
print(f"of the corrected recoveries, {cw} are WORLD and {rc - cw} are VENUE — one-sided iff "
      f"{rc - cw} == 0")

out = S / "allocation_unparsed_raw_lemmy.json"
out.write_text(json.dumps({
    "note": "raw answers for the founding-month items the PUBLISHED lemmy run left unlabelled; "
            "the frozen corpus's 55,153 published labels are untouched",
    "n_unlabelled": len(unlabelled), "n_valid_claim": len(todo),
    "n_invalid_claim": len(unlabelled) - len(todo),
    "idx": todo, "raw": raw}, indent=1))
print(f"saved {out}")
