#!/usr/bin/env python3
# NOTE: paths to the working directory (raw corpora, claim caches) come from MEMETIC_WORKDIR.
"""Adopt a claim checkpoint that carries no sidecar signature -- e.g. the partial left by the
2026-08-17 power cut, which stopped the Gemma lemmy pass at 38,250/55,223 -- so
claimify_server.py will resume from it instead of redoing the pool.

The whole point of the sidecar is that a partial from a DIFFERENT corpus must never be adopted
(chain scripts rm a pool's _all.json before a rebuild but leave its _partial behind, and a short
stale prefix fits inside a longer new run without tripping any length check). So stamping one by
hand has to earn it: every sampled claim is scored for word overlap against ITS item and against
an unrelated item, and the checkpoint is stamped only if aligned overlap dominates. A prefix
belonging to another corpus scores like the control and is refused.

Usage: claimify_resume_verify.py <outdir> <pool> [--write] [--against <claims.json>]
  --against  second claim list over the same item sequence (e.g. the Qwen pass): an independent
             alignment signal that does not depend on summaries reusing item wording.
"""
import json, random, sys
from pathlib import Path
import claimify_server as C

# Thresholds are CALIBRATED against a real negative control, not guessed: the 2026-08-17 repair
# left a stale 34,280-claim pre-repair list next to the rebuilt 55,223-item corpus, i.e. exactly
# the prefix this must refuse. Measured (n=600/test):
#                                        aligned  control  ratio   sign
#   TRUE  gemma partial x new items       0.2414   0.0165  14.64  0.981
#   TRUE  prerepair qwen x old items      0.2620   0.0142  18.47  0.986
#   TRUE  gemma partial x qwen, same corp 0.3051   0.0391   7.81  0.963
#   STALE prerepair qwen x new items      0.0634   0.0140   4.52  0.821
#   STALE prerepair qwen x qwen new corp  0.0970   0.0352   2.75  0.728
#   STALE prerepair qwen x gemma partial  0.3243   0.1281   2.53  0.722
# Two lessons are baked in. A ratio gate of 2.0 would have PASSED the stale prefix -- the old
# corpus is a subset of the new one, so coincidental and same-community topical overlap keeps the
# ratio well above 1. And an absolute-recall gate is worthless alone (a stale pairing reached
# 0.3243, higher than a true one) because these claims are abstractive: Gemma paraphrases, so only
# ~25% of a claim's content words appear literally in its item. The scale-free sign test separates
# both test types cleanly (true >=0.963, stale <=0.821), so it carries the gate.
NSAMPLE     = 600   # sampled positions; the test is a population claim, not a spot check
MIN_ALIGNED = 0.15  # sanity floor on mean share of a claim's content words found in its own item
MIN_RATIO   = 6.0   # ... over the same measure against unrelated items (true >=7.81, stale <=4.52)
MIN_SIGN    = 0.92  # ... and among non-tied pairs, aligned should almost always win

STOP = set("""about after also been before being both cannot could does doing during each from
have here into just like made make many more most much must only over said same should since
some such than that their them then there these they this those through very were what when
where which while with would your""".split())

def toks(s):
    # No regex: fold anything non-alphanumeric to space, keep content-ish words.
    flat = "".join(ch if ch.isalnum() else " " for ch in s.lower()).split()
    return {w for w in flat if len(w) >= 4 and w not in STOP}

def recall(claim, item):
    """Share of the claim's content words present in the item (None if unscorable)."""
    c = toks(claim)
    return len(c & toks(item)) / len(c) if c else None

def score(claims, items, label, rng):
    """Aligned vs shuffled-control overlap over a sample of positions."""
    n = min(NSAMPLE, len(claims))
    idx = rng.sample(range(len(claims)), n)
    pairs = []
    for i in idx:
        j = rng.randrange(len(items))          # control partner: an unrelated item
        while j == i: j = rng.randrange(len(items))
        a, b = recall(claims[i], items[i]), recall(claims[i], items[j])
        if a is not None and b is not None: pairs.append((a, b))
    if not pairs:
        return {"label": label, "n": 0, "pass": False, "note": "nothing scorable"}
    al = sum(a for a, _ in pairs) / len(pairs)
    ct = sum(b for _, b in pairs) / len(pairs)
    # Sign test over pairs that actually differ: ties (both claim and control share no words with
    # their item) carry no alignment information and would just dilute the statistic.
    nontied = sum(1 for a, b in pairs if a != b)
    sign = sum(1 for a, b in pairs if a > b) / nontied if nontied else 0.0
    ratio = al / ct if ct else float("inf")
    ok = al >= MIN_ALIGNED and ratio >= MIN_RATIO and sign >= MIN_SIGN
    return {"label": label, "n": len(pairs), "aligned": round(al, 4), "control": round(ct, 4),
            "ratio": round(ratio, 2), "sign": round(sign, 3),
            "tie_frac": round(1 - nontied / len(pairs), 2), "pass": bool(ok)}

def main():
    argv = [a for a in sys.argv[1:]]
    write = "--write" in argv; argv = [a for a in argv if a != "--write"]
    against = None
    if "--against" in argv:
        k = argv.index("--against"); against = argv[k + 1]; del argv[k:k + 2]
    outdir, pool = argv[0], argv[1]

    OUT = C.S / outdir
    part, meta_p = OUT / f"{pool}_partial.json", OUT / f"{pool}_partial.meta.json"
    if not part.exists(): sys.exit(f"no partial: {part}")
    prev = json.load(part.open())
    items = C.LOADERS[pool]()
    print(f"pool={pool}  partial={len(prev):,} claims  loader={len(items):,} items")

    fatal = []
    if not (isinstance(prev, list) and prev and all(isinstance(c, str) for c in prev)):
        fatal.append("partial is not a non-empty list of strings")
    if len(prev) > len(items):
        fatal.append(f"partial ({len(prev):,}) is longer than the item sequence ({len(items):,})")
    if meta_p.exists():
        m = json.load(meta_p.open())
        if m.get("sig") == C.sig_of(items):
            print("sidecar already valid for this item sequence -- nothing to do"); return 0
        fatal.append(f"a sidecar exists and does NOT match this corpus (n_items={m.get('n_items')})")
    errs = sum(1 for c in prev if isinstance(c, str) and c.startswith("[NORMALIZER-ERROR"))
    empt = sum(1 for c in prev if isinstance(c, str) and not c.strip())
    print(f"content: {errs} normalizer errors, {empt} empty")
    if fatal:
        for f in fatal: print(f"  FATAL: {f}")
        sys.exit(1)

    rng = random.Random(0)
    checks = [score(prev, items[:len(prev)], "claim vs its own item", rng)]
    if against:
        other = json.load(open(C.S / against))
        if len(other) < len(prev):
            print(f"  --against list is shorter ({len(other):,}) than the partial; skipping")
        else:
            checks.append(score(prev, other[:len(prev)], f"claim vs {Path(against).name}", rng))

    print()
    for c in checks:
        print(f"  {c['label']:<44} aligned={c.get('aligned')} control={c.get('control')} "
              f"ratio={c.get('ratio')} sign={c.get('sign')} ties={c.get('tie_frac')} n={c['n']}  "
              f"{'PASS' if c['pass'] else 'FAIL'}")
    print(f"  thresholds: aligned>={MIN_ALIGNED} ratio>={MIN_RATIO} sign>={MIN_SIGN}")

    if not all(c["pass"] for c in checks):
        print("\nREFUSED: the partial does not demonstrably line up with these items.")
        sys.exit(1)
    print(f"\nALIGNED: partial is a valid prefix of {len(items):,} items.")
    if not write:
        print("(dry run -- pass --write to stamp the sidecar)"); return 0
    C.save_json({"pool": pool, "n_items": len(items), "done": len(prev), "sig": C.sig_of(items),
                 "adopted_by": "claimify_resume_verify.py", "checks": checks}, meta_p)
    print(f"stamped {meta_p.name}: claimify_server.py will resume at {len(prev):,}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
