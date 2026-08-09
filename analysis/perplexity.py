#!/usr/bin/env python3
"""LM token-loss (perplexity) pass over the 1f916.ai corpus.

For every item (chronological), score its own tokens under a frozen local
language model, twice:
  self  — the item alone (BOS + item): intrinsic predictability
  cond  — trailing window of prior items' text, then the item: predictability
          given forum history (the endogeneity signal)

The self→cond drop is the LM analogue of the zstd novelty ratio, but it also
catches PARAPHRASED convention (not just verbatim ritual, which is all zstd
sees). Per-token conditioned loss additionally localizes ritual spans and
seeds the ablation/clout pass.

Outputs (results/perplexity/):
  metrics.jsonl / .csv  per-item: bits/token & bits/char (self, cond),
                        novelty_ratio, low-information span fraction
  tokens.npz            per-token conditioned bits (float16, concatenated)
                        + per-item offsets, for ritual-span analysis
  run.json              params, model, versions, sanity checks

Run via analysis/run_perplexity.sh (activates the `memetic` conda env).
"""

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO = Path(__file__).resolve().parent.parent
LN2 = math.log(2.0)


def relparam(v):
    """Record paths repo-relative in run.json so it's portable across clones."""
    if isinstance(v, Path):
        try:
            return str(v.resolve().relative_to(REPO))
        except ValueError:
            return str(v)
    return v


def load_items(data_dir: Path):
    items = []
    for f in sorted(data_dir.glob("*.json"), key=lambda p: int(p.stem)):
        th = json.loads(f.read_text())
        p = th["post"]
        text = ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()
        items.append({"kind": "post", "id": p["id"], "post_id": p["id"],
                      "created_at": p["created_at"], "author": p["author"],
                      "author_model": p.get("author_model"), "text": text})
        for c in th["comments"]:
            items.append({"kind": "comment", "id": c["id"], "post_id": p["id"],
                          "created_at": c["created_at"], "author": c["author"],
                          "author_model": c.get("author_model"),
                          "text": (c.get("body") or "").strip()})
    items.sort(key=lambda x: (x["created_at"], 0 if x["kind"] == "post" else 1, x["id"]))
    return items


@torch.no_grad()
def token_bits(model, input_ids, n_score):
    """Per-token bits (-log2 p) for the final `n_score` tokens of input_ids,
    each conditioned on all preceding tokens. One forward pass.

    The scored tokens are always a suffix, so ask the model for logits over
    only the last n_score+1 positions (`num_logits_to_keep`) instead of a full
    [T, vocab] tensor, which OOMs at ~150k vocab on long sequences."""
    ids = input_ids.to(model.device)
    logits = model(ids.unsqueeze(0), num_logits_to_keep=n_score + 1).logits[0]
    # rows are positions [T-n_score-1 .. T-1]; predictions for the n_score
    # scored tokens come from rows [0 .. n_score-1].
    pred = logits[:-1].float()                          # [n_score, V]
    tgt = ids[-n_score:]                                # [n_score]
    logp = torch.log_softmax(pred, dim=-1)
    tok_nats = -logp.gather(1, tgt.unsqueeze(1)).squeeze(1)
    return (tok_nats / LN2).cpu().numpy().astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B")
    ap.add_argument("--data-dir", type=Path, default=REPO / "data" / "posts")
    ap.add_argument("--out-dir", type=Path, default=REPO / "results" / "perplexity")
    ap.add_argument("--window-tokens", type=int, default=3072,
                    help="max trailing history tokens for the conditioned score")
    ap.add_argument("--max-item-tokens", type=int, default=2048,
                    help="truncate very long items to bound memory")
    ap.add_argument("--low-info-bits", type=float, default=1.0,
                    help="per-token bits threshold defining a low-information (ritual) token")
    ap.add_argument("--limit", type=int, default=0, help="score only first N items (smoke test)")
    ap.add_argument("--dtype", default="float16")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading model {args.model} ...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=getattr(torch, args.dtype), device_map="cuda")
    model.eval()
    bos = tok.bos_token_id
    if bos is None:  # Qwen has no BOS; use a newline as a neutral 1-token prefix
        bos = tok("\n", add_special_tokens=False)["input_ids"][0]
    sep_ids = tok("\n\n", add_special_tokens=False)["input_ids"]

    items = load_items(args.data_dir)
    if args.limit:
        items = items[:args.limit]
    print(f"{len(items)} items", file=sys.stderr)

    history_ids: list[int] = []          # all prior item tokens, chronological
    rows, tok_bits_all, offsets = [], [], []
    cursor = 0
    t0 = time.time()

    for i, it in enumerate(items):
        ids = tok(it["text"], add_special_tokens=False)["input_ids"][:args.max_item_tokens]
        n = len(ids)
        if n == 0:
            history_ids.extend(sep_ids)
            continue

        # self: [bos] + item  (score the n item tokens, a suffix)
        self_seq = torch.tensor([bos] + ids)
        self_bits = token_bits(model, self_seq, n_score=n)

        # cond: [trailing window of history] + sep + item
        win = history_ids[-args.window_tokens:]
        cond_seq = torch.tensor(win + sep_ids + ids) if win else self_seq
        cond_bits = token_bits(model, cond_seq, n_score=n)

        chars = len(it["text"])
        row = {
            "seq": i, "kind": it["kind"], "id": it["id"], "post_id": it["post_id"],
            "created_at": it["created_at"], "author": it["author"],
            "author_model": it["author_model"], "chars": chars, "tokens": n,
            "self_bits_per_tok": round(float(self_bits.mean()), 4),
            "cond_bits_per_tok": round(float(cond_bits.mean()), 4),
            "self_bits_per_char": round(float(self_bits.sum() / chars), 4),
            "cond_bits_per_char": round(float(cond_bits.sum() / chars), 4),
            "novelty_ratio": round(float(cond_bits.sum() / self_bits.sum()), 4),
            "low_info_frac": round(float((cond_bits < args.low_info_bits).mean()), 4),
            "cond_window_tokens": len(win),
        }
        rows.append(row)
        tok_bits_all.append(cond_bits.astype(np.float16))
        offsets.append((row["seq"], row["kind"], row["id"], cursor, cursor + n))
        cursor += n

        history_ids.extend(ids)
        history_ids.extend(sep_ids)

        if (i + 1) % 100 == 0 or i + 1 == len(items):
            el = time.time() - t0
            print(f"  {i+1}/{len(items)}  {el:.0f}s  {(i+1)/el:.1f} items/s", file=sys.stderr)

    with (args.out_dir / "metrics.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (args.out_dir / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    np.savez_compressed(
        args.out_dir / "tokens.npz",
        cond_bits=np.concatenate(tok_bits_all),
        index=np.array([(o[0], o[3], o[4]) for o in offsets], dtype=np.int64),
        keys=np.array([f"{o[1]}:{o[2]}" for o in offsets]))

    tc = sum(r["chars"] for r in rows)
    agg = lambda k: round(sum(r[k] * r["chars"] for r in rows) / tc, 4)
    checks = {
        "items_scored": len(rows),
        "cond_le_self_frac": round(
            sum(r["cond_bits_per_tok"] <= r["self_bits_per_tok"] + 0.05 for r in rows) / len(rows), 4),
        "corpus_self_bpc": agg("self_bits_per_char"),
        "corpus_cond_bpc": agg("cond_bits_per_char"),
        "corpus_novelty": round(sum(r["cond_bits_per_tok"] * r["tokens"] for r in rows)
                                / sum(r["self_bits_per_tok"] * r["tokens"] for r in rows), 4),
    }
    run = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "params": {k: relparam(v) for k, v in vars(args).items()},
        "versions": {"torch": torch.__version__,
                     "transformers": __import__("transformers").__version__},
        "elapsed_sec": round(time.time() - t0, 1),
        "sanity": checks,
    }
    (args.out_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    print(f"done -> {args.out_dir} in {run['elapsed_sec']}s", file=sys.stderr)


if __name__ == "__main__":
    main()
