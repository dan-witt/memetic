#!/usr/bin/env python3
"""Gold-sample protocol for the allocation study: `build` makes the stratified blind sample,
`score` computes the four-rater matrix. Paths via MEMETIC_WORKDIR. Blind frontier-rater protocol:
a fresh zero-context agent, hard-fenced to the claims file alone, given only the construct
definition and the tiebreaker ("would this sentence make sense posted in a different
community?"); human rater marks [V/W/U] in the blind txt. Executed-run artifacts:
results/allocation/gold_matrix.json."""
import json, os, re, sys
from pathlib import Path
import numpy as np

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
FILES = {"agent": "agent3_all.json", "lisp": "baseline_claims/lisp_all.json", "sci": "baseline_claims/sci_all.json",
         "hn": "baseline_claims/hn_all.json", "forth": "baseline_claims/forth_all.json",
         "smalltalk": "baseline_claims/smalltalk_all.json", "scheme": "baseline_claims/scheme_all.json"}

def build():
    labels = json.load(open(S / "allocation_labels.json"))
    rng = np.random.default_rng(42)
    BOUND = re.compile(r"\b(ai|agent|agents|model|llm|bot)s?\b", re.I)
    PLAT = re.compile(r"square|treasury|this forum|this community|moderat", re.I)
    rows = []
    for k, f in FILES.items():
        cl = json.load(open(S / f)); lab = labels[k]
        ok = [i for i, l in enumerate(lab) if l is not None]
        if k == "agent":
            bd = [i for i in ok if BOUND.search(cl[i]) and not PLAT.search(cl[i])]
            pick = list(rng.choice(ok, 30, replace=False)) + list(rng.choice(bd, 30, replace=False))
            strata = ["agent_random"] * 30 + ["agent_boundary"] * 30
        else:
            pick = list(rng.choice(ok, 20, replace=False)); strata = [f"{k}_random"] * 20
        rows += [{"pool": k, "idx": int(i), "stratum": s, "claim": cl[int(i)], "qwen": lab[int(i)]}
                 for i, s in zip(pick, strata)]
    order = rng.permutation(len(rows))
    key, lines = {}, []
    for n, j in enumerate(order):
        r = rows[j]
        lines.append(f"{n+1:3d}. [ ] {r['claim']}")
        key[str(n + 1)] = {k: r[k] for k in ("pool", "idx", "stratum", "qwen")}
    (S / "gold_sample_blind.txt").write_text("\n".join(lines))
    json.dump(key, open(S / "gold_sample_key.json", "w"), indent=1)
    print(f"built {len(rows)} claims -> gold_sample_blind.txt + sealed key")

def score(human_txt, fable_json, gemma_json):
    key = json.load(open(S / "gold_sample_key.json"))
    fable, gemma = json.load(open(fable_json)), json.load(open(gemma_json))
    human = {}
    for l in open(human_txt):
        m = re.match(r"\s*(\d+)\. \[([VWUvwu])\]", l)
        if m: human[m.group(1)] = m.group(2).upper()
    R = {n: {"human": human.get(n), "fable": fable.get(n), "gemma": gemma.get(n),
             "qwen": {"V": "V", "W": "W"}.get(key[n]["qwen"]),
             "stratum": key[n]["stratum"], "pool": key[n]["pool"]} for n in key}
    raters = ["human", "fable", "qwen", "gemma"]
    for i, a in enumerate(raters):
        for b in raters[i+1:]:
            pp = [(R[n][a], R[n][b]) for n in R if R[n][a] in "VW" and R[n][b] in "VW"]
            agr = np.mean([x == y for x, y in pp])
            pv, gv = np.mean([x == "V" for x, _ in pp]), np.mean([y == "V" for _, y in pp])
            pe = pv * gv + (1 - pv) * (1 - gv)
            print(f"{a} vs {b}: agree {agr:.3f} kappa {(agr - pe)/(1 - pe):.3f} n={len(pp)}")
    json.dump(R, open(S / "gold_matrix.json", "w"), indent=1)
    print("saved gold_matrix.json")

if __name__ == "__main__":
    if sys.argv[1] == "build": build()
    else: score(*sys.argv[2:5])
