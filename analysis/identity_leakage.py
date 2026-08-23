#!/usr/bin/env python3
"""Does the identity pass's author effect ride on the author's HANDLE appearing in its own text?

The pass embeds item text as written. Nothing strips names, so a citizen that signs its posts, or
that talks about itself by handle, hands the embedder a literal copy of its own label. That would
inflate every lexical author cell -- the DISCO author excess, the 0.211/0.368 identification
numbers, and especially the switcher ratios, where the same handle sits on both arms of a model
switch and directly deflates d(self, across models).

Length residualization cannot rule this out: a handle is length-invariant, so "the author effect
is not register (-2%)" says nothing about it.

This script measures the exposure and then removes it:

  1. MEASURE  what fraction of items contain their own author's handle.
  2. MASK     every known handle everywhere in the corpus (not just self-mentions -- masking only
              the author's own handle would leave a citizen's handle in OTHER citizens' text and
              create a new asymmetry) and re-embed with bge.
  3. COMPARE  headline DISCO and identification, as-written vs masked, on identical rows.

The masked run is a LOWER bound on the author effect: handles are replaced with a constant token,
which also destroys legitimate addressee information (who is replying to whom), so masking removes
some real conversational structure along with the leak.

Usage: MEMETIC_WORKDIR=... python3 analysis/identity_leakage.py   (GPU, ~2 min for one embedder)
       IDENTITY_LEAK_MEASURE_ONLY=1 to skip the GPU half and print only step 1.
"""
import collections, json, os, re, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import identity_disco as ID

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
MASK = " someone "          # a constant, low-information token; spaces keep word boundaries


def self_mention(items, min_items=ID.MIN_ITEMS):
    """-> exposure stats over the analysis set (authors with >= min_items)."""
    by = collections.defaultdict(list)
    for r in items:
        by[r["author"]].append(r)
    aset = {a: v for a, v in by.items() if len(v) >= min_items}
    per = {a: sum(1 for r in v if a.lower() in r["text"].lower()) / len(v) for a, v in aset.items()}
    n_items = sum(len(v) for v in aset.values())
    n_hit = sum(round(p * len(aset[a])) for a, p in per.items())
    rates = sorted(per.values(), reverse=True)
    return {
        "analysis_authors": len(aset), "analysis_items": n_items,
        "items_containing_own_handle": n_hit,
        "pct_items": round(100 * n_hit / n_items, 1),
        "authors_with_any": sum(1 for p in per.values() if p > 0),
        "per_author_rate_median": round(rates[len(rates) // 2], 3),
        "per_author_rate_p90": round(rates[int(0.1 * len(rates))], 3),
        "per_author_rate_max": round(max(rates), 3),
    }


def mask_handles(items):
    """-> texts with EVERY known handle replaced by MASK, longest-first so substrings can't win."""
    handles = sorted({r["author"] for r in items if len(r["author"]) >= 4}, key=len, reverse=True)
    pat = re.compile("|".join(re.escape(h) for h in handles), re.IGNORECASE)
    return [pat.sub(MASK, r["text"]) for r in items]


if __name__ == "__main__":
    items = json.load(open(S / "identity_items.json"))
    exposure = self_mention(items)
    print("EXPOSURE (analysis set, >=%d items):" % ID.MIN_ITEMS)
    for k, v in exposure.items():
        print(f"  {k:32s} {v}")
    out = {"exposure": exposure, "mask_token": MASK}

    if not os.environ.get("IDENTITY_LEAK_MEASURE_ONLY"):
        from sentence_transformers import SentenceTransformer
        import identity_embed as IE
        texts = mask_handles(items)
        print(f"\nmasking {len({r['author'] for r in items if len(r['author']) >= 4})} handles; "
              f"re-embedding {len(texts)} items with bge ...", flush=True)
        model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
        Em = IE.encode_pooled(model, texts).astype(np.float32)
        np.save(S / "identity_emb_lexical_masked_bge.npy", Em)

        E0 = np.load(S / "identity_emb_lexical_bge.npy")
        log = lambda s: print(s, flush=True)
        claim_rows = [r for r in items if "claim_idx" in r]
        for name, rows in (("lexical", items), ("lexical_matched", claim_rows)):
            ix = [r["idx"] for r in rows]
            for label, E in (("as-written", E0[ix]), ("masked", Em[ix])):
                print(f"\n--- {name} / {label} ---")
                out[f"{name}/{label}"] = {
                    "headline": ID.headline(E, rows, f"{name}-{label}", log),
                    "identify": ID.identify(E, rows, log),
                }
        (S / "identity_leakage_out.json").write_text(json.dumps(out, indent=1))
        print(f"\nsaved {S / 'identity_leakage_out.json'}")
