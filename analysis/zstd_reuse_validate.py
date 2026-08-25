#!/usr/bin/env python3
"""Acceptance test for zstd_curve.compute_metrics(reuse=...) — the incremental register path.

The weather report's register cell reads self_bits and cond_win_bits, both of which depend only on
an item and the items BEFORE it. That makes them reusable across issues, which is what took the CPU
stage from ~55 min to 11 s at issue #12. It also makes them silently wrong if the prefix is not
what the cache thinks it is, and a stale register series would be invisible: the numbers stay
plausible to four decimals.

So the cache's invalidation logic gets a test rather than an argument. For each way a prefix can
break, this runs the SAME item list twice -- once from scratch, once against a cache built from the
un-mutated list -- and requires bit-identical rows:

  deletion   the case a key-and-hash cache misses. Every remaining key still matches its cached
             hash, but items after the removal shifted down and their cond_win was computed against
             a history that still contained the removed item. Caught by requiring the cached seq to
             equal the current index.
  insertion  a backfilled item with an earlier created_at lands mid-stream and shifts every later
             bucket boundary. Caught by the key lookup. This is not hypothetical: issue #12's
             backfill inserted 3 items into an already-published day and rewound 502 rows.
  edit       a post-publication text change. Caught by the content hash.
  append     the ordinary case; must reuse everything and recompute only the tail.
  unchanged  must reuse everything and recompute nothing.

Usage: .venv/bin/python analysis/zstd_reuse_validate.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zstd_curve as Z

COLUMNS = ("self", "cond_win")


class Args:
    # Small window and bucket so the test exercises many buckets cheaply; the invariant under test
    # is independent of the values, and weather_cpu.py's real parameters are asserted separately by
    # the neutrality check against a published issue.
    level = 19
    window_bytes = 8192
    bucket = 5
    seed = 42


def _items(n, seed=7):
    rng = random.Random(seed)
    return [{"kind": "comment", "id": i, "post_id": 0, "created_at": i, "author": "a",
             "author_model": "", "text": "".join(rng.choice("abcdefg ") for _ in range(300))}
            for i in range(n)]


def _rows(items, reuse=None):
    return Z.compute_metrics(items, Args(), columns=COLUMNS, reuse=reuse)


def check(label, base_cache, mutated):
    """Recompute `mutated` from scratch and from the cache; require identical rows."""
    truth = _rows(mutated)
    cached = _rows(mutated, reuse=dict(base_cache))
    if len(truth) != len(cached):
        return label, f"row count {len(cached)} != {len(truth)}"
    bad = [t["id"] for t, c in zip(truth, cached)
           if (t["self_bits"], t["cond_win_bits"]) != (c["self_bits"], c["cond_win_bits"])]
    return label, (f"{len(bad)} stale row(s), first ids {bad[:5]}" if bad else None)


def main():
    items = _items(60)
    cache = {f"{r['kind']}:{r['id']}": r for r in _rows(items)}
    extra = dict(items[0], id=999, text="qqq " * 80)
    cases = [
        ("deletion mid-stream", items[:20] + items[21:]),
        ("insertion mid-stream", items[:20] + [extra] + items[20:]),
        ("edit mid-stream", items[:30] + [dict(items[30], text="EDITED " * 50)] + items[31:]),
        ("append", items + [dict(items[0], id=100 + j, text="zzz " * 80) for j in range(10)]),
        ("unchanged", list(items)),
    ]
    results = [check(label, cache, mutated) for label, mutated in cases]
    print()
    ok = True
    for label, err in results:
        print(f"  [{'ok  ' if err is None else 'FAIL'}] {label:22s} {err or 'bit-identical'}")
        ok &= err is None

    # cond_shuf is built from a sample drawn over the WHOLE corpus, including items after the one
    # being scored, so reusing it would be wrong rather than merely stale. cond_full is prefix-stable
    # (its dictionary is the history before the bucket) and is merely expensive, so it must be
    # ACCEPTED. Both halves are part of the contract and both are asserted.
    try:
        Z.compute_metrics(items, Args(), columns=("self", "cond_shuf"), reuse=dict(cache))
        print("  [FAIL] refuses cond_shuf with reuse        accepted it")
        ok = False
    except ValueError:
        print("  [ok  ] refuses cond_shuf with reuse        raises")
    try:
        Z.compute_metrics(items, Args(), columns=("self", "cond_full"), reuse=dict(cache))
        print("  [ok  ] accepts cond_full with reuse        prefix-stable, dropped for cost only")
    except ValueError:
        print("  [FAIL] accepts cond_full with reuse        refused a prefix-stable column")
        ok = False

    print(f"\n{'PASS' if ok else 'FAIL'}: incremental register path")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
