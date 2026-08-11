# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR;
# raw corpora are not committed to the repo (public sources + parse rules reproduce them).
#!/usr/bin/env python3
"""The missing addendum-grade validation: is the Qwen claim-normalizer faithful IN-REGIME on the
new Usenet corpora (1980s prose, code-heavy lisp posts)? Three checks per corpus, all five pools:
  1. per-item content preservation: cosine(emb(claim_i), emb(text_i)) aligned, vs a shuffled floor
     (the content_preservation.py pattern; misalignment lesson: both arrays built from the same
     index list, floor = mean over a derangement of the same pairs)
  2. degenerate-claim audit: exact-dup claim rate, top repeated claims, near-dup rate at cosine>0.95
  3. unequal-work ratio: input chars : claim chars (the 15.8:1 vs 1.6:1 stat, extended to new pools)
If lisp shows depressed preservation or elevated claim-duplication vs the other pools, the
agents-more-diverse-than-lisp headline is suspect (normalizer collapse, not real concentration)."""
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

import sys
S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
CLAIMS_DIR = sys.argv[1] if len(sys.argv) > 1 else "baseline_claims"
OUTNAME = sys.argv[2] if len(sys.argv) > 2 else "band_claims_validation.json"
POOLS = sys.argv[3:] or ["agent", "catskill", "hn", "lisp", "sci"]

def forum_texts(d):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, (c.get("body") or "").strip()))
    items.sort(key=lambda x: x[0])
    return [x for _, x in items if len(x) >= 20]

def usenet_texts(fam):
    C = json.load(open(S / "baseline_corpora.json"))[fam]
    out = []
    for r in C:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"])
    return out

TEXTS = {"agent": forum_texts("/home/dan/personal/memetic/data/posts"),
         "catskill": forum_texts(S / "catskill/posts"), "hn": forum_texts(S / "hn/posts"),
         "lisp": usenet_texts("lisp"), "sci": usenet_texts("sci")}
CLAIMS = {k: json.load(open(S / CLAIMS_DIR / f"{k}_all.json")) for k in POOLS}
for k in POOLS:
    assert len(TEXTS[k]) == len(CLAIMS[k]), f"{k} misaligned: {len(TEXTS[k])} vs {len(CLAIMS[k])}"

m = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
rng = np.random.default_rng(0)
out = {}
for k in POOLS:
    n = len(TEXTS[k])
    idx = np.sort(rng.choice(n, min(800, n), replace=False))       # same indices for both arrays
    tx = [TEXTS[k][i][:3000] for i in idx]                          # same truncation the normalizer saw
    cl = [CLAIMS[k][i] for i in idx]
    Et = m.encode(tx, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    Ec = m.encode(cl, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    aligned = (Et * Ec).sum(1)
    perm = np.roll(np.arange(len(idx)), 1)                          # derangement floor
    floor = (Et * Ec[perm]).sum(1)
    # degenerate claims: exact dups over the FULL pool + near-dups within the sample
    allc = [c.strip().lower() for c in CLAIMS[k]]
    exact_dup = 1 - len(set(allc)) / len(allc)
    sim = Ec @ Ec.T; np.fill_diagonal(sim, 0)
    near_dup = float((sim.max(1) > 0.95).mean())
    from collections import Counter
    top = Counter(allc).most_common(3)
    work = np.mean([len(TEXTS[k][i]) for i in range(n)]) / np.mean([max(len(CLAIMS[k][i]), 1) for i in range(n)])
    out[k] = dict(preserve_med=round(float(np.median(aligned)), 3),
                  preserve_p10=round(float(np.percentile(aligned, 10)), 3),
                  floor_med=round(float(np.median(floor)), 3),
                  frac_below_floor_med=round(float((aligned < np.median(floor)).mean()), 3),
                  exact_dup_rate=round(exact_dup, 4), near_dup_rate=round(near_dup, 3),
                  work_ratio=round(float(work), 1),
                  top_repeated=[(c[:70], nn) for c, nn in top if nn > 2])
    print(f"{k:9s} preserve med {out[k]['preserve_med']} (p10 {out[k]['preserve_p10']}) vs floor {out[k]['floor_med']} "
          f"| <floor: {out[k]['frac_below_floor_med']:.1%} | dup exact {exact_dup:.2%} near {near_dup:.1%} "
          f"| work {out[k]['work_ratio']}:1", flush=True)
    if out[k]["top_repeated"]: print(f"          top repeats: {out[k]['top_repeated']}", flush=True)

json.dump(out, open(S / OUTNAME, "w"), indent=1)
print("saved band_claims_validation.json")
