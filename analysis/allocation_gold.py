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
    R = {n: {"dan": human.get(n), "fable": fable.get(n), "gemma": gemma.get(n),
             "qwen": {"V": "V", "W": "W"}.get(key[n]["qwen"]),
             "stratum": key[n]["stratum"], "pool": key[n]["pool"]} for n in key}
    raters = ["dan", "fable", "qwen", "gemma"]  # rater key matches the executed artifact
    for i, a in enumerate(raters):
        for b in raters[i+1:]:
            pp = [(R[n][a], R[n][b]) for n in R if R[n][a] in "VW" and R[n][b] in "VW"]
            agr = np.mean([x == y for x, y in pp])
            pv, gv = np.mean([x == "V" for x, _ in pp]), np.mean([y == "V" for _, y in pp])
            pe = pv * gv + (1 - pv) * (1 - gv)
            print(f"{a} vs {b}: agree {agr:.3f} kappa {(agr - pe)/(1 - pe):.3f} n={len(pp)}")
    json.dump(R, open(S / "gold_matrix.json", "w"), indent=1)
    print("saved gold_matrix.json")

def build_lemmy():
    """Round-2 gold sample: lemmy.world vs the agent square on ONE blind sheet, so rater drift
    cannot be mistaken for a corpus difference. Strata are chosen to probe the failure mode the
    published human_calibration found -- Qwen over-calls VENUE ~3x on HUMAN anchors (0.18 vs
    0.06) while Gemma matches them. Lemmy is a human corpus carrying a human-vs-agent headline,
    so the boundary stratum is topic-community claims that USE venue vocabulary: the cases where
    a false-VENUE bias would do the most damage to the contrast.
    Key seals qwen AND gemma labels; both are full-pool here, not samples."""
    rng = np.random.default_rng(2)
    VENUEISH = re.compile(r"\b(communit|forum|subreddit|instance|moderat|rule|admin|post(ing|ed)?|"
                          r"user|member|server|lemmy|reddit)\w*\b", re.I)
    C = [r for r in json.load(open(S / "baseline_corpora_lemmy.json"))["lemmy"] if len(r["text"]) >= 20]
    lcl = json.load(open(S / "baseline_claims/lemmy_all.json"))
    llab = json.load(open(S / "allocation_labels_lemmy.json"))["lemmy"]
    lgem = {p["idx"]: p["gemma"] for p in json.load(open(S / "allocation_agree_pairs_lemmy_full.json"))}
    acl = json.load(open(S / "agent_claims_aligned.json"))
    alab = json.load(open(S / "allocation_labels_agentcur.json"))["agentcur"]
    agem = {p["idx"]: p["gemma"] for p in json.load(open(S / "allocation_agree_pairs_agentcur.json"))}

    def take(pool, cl, lab, gem, idxs, stratum, n):
        idxs = [i for i in idxs if lab[i] is not None and gem.get(i) is not None]
        pick = rng.choice(idxs, min(n, len(idxs)), replace=False)
        return [{"pool": pool, "idx": int(i), "stratum": stratum, "claim": cl[int(i)],
                 "qwen": lab[int(i)], "gemma": gem[int(i)]} for i in pick]

    topic = [i for i, r in enumerate(C) if r["tier"] == "topic"]
    meta = [i for i, r in enumerate(C) if r["tier"] == "meta"]
    rows = (take("lemmy", lcl, llab, lgem, topic, "lemmy_topic_random", 30)
            + take("lemmy", lcl, llab, lgem,
                   [i for i in topic if VENUEISH.search(lcl[i] or "")], "lemmy_topic_boundary", 25)
            + take("lemmy", lcl, llab, lgem, meta, "lemmy_meta_random", 15)
            + take("agentcur", acl, alab, agem, range(len(acl)), "agent_random", 30))
    order = rng.permutation(len(rows))
    key, lines = {}, []
    for n, j in enumerate(order):
        r = rows[j]
        lines.append(f"{n+1:3d}. [ ] {r['claim']}")
        key[str(n + 1)] = {k: r[k] for k in ("pool", "idx", "stratum", "qwen", "gemma")}
    (S / "gold2_sample_blind.txt").write_text("\n".join(lines) + "\n")
    json.dump(key, open(S / "gold2_sample_key.json", "w"), indent=1)
    from collections import Counter
    print(f"built {len(rows)} claims -> gold2_sample_blind.txt + sealed gold2_sample_key.json")
    print("  strata:", dict(Counter(r["stratum"] for r in rows)))
    print("  machine labels sealed in key (qwen + gemma), both full-pool")


def score_lemmy(human_txt, fable_json):
    """Round-2 scoring. The gold2 key already seals BOTH machine labels (qwen + gemma,
    full-pool), so only the two blind human/frontier rater sheets are supplied here.
    Reports pairwise agreement/kappa over all four raters, plus per-stratum accuracy of each
    machine against the human+fable consensus -- which is the cell that actually bounds the
    allocation contrast."""
    key = json.load(open(S / "gold2_sample_key.json"))
    fable = json.load(open(fable_json))
    human = {}
    for l in open(human_txt):
        m = re.match(r"\s*(\d+)\. \[([VWUvwu])\]", l)
        if m: human[m.group(1)] = m.group(2).upper()
    R = {n: {"dan": human.get(n), "fable": fable.get(n),
             "qwen": key[n]["qwen"], "gemma": key[n]["gemma"],
             "stratum": key[n]["stratum"], "pool": key[n]["pool"]} for n in key}
    raters = ["dan", "fable", "qwen", "gemma"]
    print("=== pairwise agreement ===")
    for i, a in enumerate(raters):
        for b in raters[i+1:]:
            pp = [(R[n][a], R[n][b]) for n in R if R[n][a] in "VW" and R[n][b] in "VW"]
            agr = np.mean([x == y for x, y in pp])
            pv, gv = np.mean([x == "V" for x, _ in pp]), np.mean([y == "V" for _, y in pp])
            pe = pv * gv + (1 - pv) * (1 - gv)
            k = (agr - pe) / (1 - pe) if pe < 1 else float("nan")
            print(f"  {a:<6} vs {b:<6} agree {agr:.3f}  kappa {k:.3f}  n={len(pp)}")
    print("\n=== venue share by rater, per stratum ===")
    strata = sorted({R[n]["stratum"] for n in R})
    print(f"  {'stratum':<24} " + "  ".join(f"{r:>6}" for r in raters) + "     n")
    for st in strata:
        ns = [n for n in R if R[n]["stratum"] == st]
        cells = []
        for r in raters:
            v = [R[n][r] for n in ns if R[n][r] in "VW"]
            cells.append(f"{np.mean([x=='V' for x in v]):6.3f}" if v else "     -")
        print(f"  {st:<24} " + "  ".join(cells) + f"  {len(ns):>5}")
    print("\n=== machine vs human+fable CONSENSUS (both agree, V/W only) ===")
    for st in strata + ["ALL"]:
        ns = [n for n in R if (st == "ALL" or R[n]["stratum"] == st)
              and R[n]["dan"] in "VW" and R[n]["fable"] in "VW" and R[n]["dan"] == R[n]["fable"]]
        if len(ns) < 5: continue
        row = f"  {st:<24} n={len(ns):>3}"
        for m in ("qwen", "gemma"):
            mm = [n for n in ns if R[n][m] in "VW"]
            acc = np.mean([R[n][m] == R[n]["dan"] for n in mm])
            fv = np.mean([R[n][m] == "V" and R[n]["dan"] == "W" for n in mm])
            row += f" | {m} acc {acc:.3f} falseV {fv:.3f}"
        print(row)
    json.dump(R, open(S / "gold2_matrix.json", "w"), indent=1)
    print("\nsaved gold2_matrix.json")


if __name__ == "__main__":
    if sys.argv[1] == "build": build()
    elif sys.argv[1] == "build_lemmy": build_lemmy()
    elif sys.argv[1] == "score_lemmy": score_lemmy(*sys.argv[2:4])
    else: score(*sys.argv[2:5])
