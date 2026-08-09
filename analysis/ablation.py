#!/usr/bin/env python3
"""Ablation clout: how much does each POST improve the LM's prediction of the
items that follow it?

For post X and the next H items Y1..YH (chronological), score each Y twice
under the frozen LM:
  base : Y conditioned on [X, Y1..Y(k-1)]   (X present)
  abl  : Y conditioned on    [Y1..Y(k-1)]   (X removed)
delta_k = bits_abl(Yk) - bits_base(Yk)  > 0  when X made Yk more predictable.
clout(X) = sum of delta_k over the horizon. Recorded per distance k so the
delta(k) curve reveals whether influence falls off a cliff at k=30 (the front
page shows 30 items).

Each (base, abl) pair is one forward over the [prefix + horizon block], scored
with a chunked lm_head to keep vocab-logit memory bounded. SDPA attention fits
the ~24K-token H=60 block in 24 GB. Posts swept tail->head.

Outputs (results/ablation/): clout.jsonl (per post, joined to karma/votes),
distance_curve.csv (pooled delta by k), run.json.
"""
import argparse, csv, json, math, sys, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO = Path(__file__).resolve().parent.parent
LN2 = math.log(2.0)


def load_items_and_votes(data_dir: Path):
    items, votes = [], {}
    for f in sorted(data_dir.glob("*.json"), key=lambda p: int(p.stem)):
        th = json.loads(f.read_text()); p = th["post"]
        items.append({"kind": "post", "id": p["id"], "created_at": p["created_at"],
                      "author": p["author"], "author_model": p.get("author_model"),
                      "text": ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()})
        votes[("post", p["id"])] = p.get("votes", 0)
        for c in th["comments"]:
            items.append({"kind": "comment", "id": c["id"], "created_at": c["created_at"],
                          "author": c["author"], "author_model": c.get("author_model"),
                          "text": (c.get("body") or "").strip()})
            votes[("comment", c["id"])] = c.get("votes", 0)
    items.sort(key=lambda x: (x["created_at"], 0 if x["kind"] == "post" else 1, x["id"]))
    return items, votes


@torch.no_grad()
def item_bits(model, prefix_ids, blocks, sep_ids, chunk=512):
    """One forward over [prefix + sep-joined blocks]; return mean bits/token for
    each block. blocks = list of token-id lists (the horizon items)."""
    seq, spans = list(prefix_ids), []
    for b in blocks:
        seq += sep_ids
        spans.append((len(seq), len(seq) + len(b)))   # [start, end) of this item
        seq += b
    ids = torch.tensor(seq, device=model.device)
    hidden = model.model(ids.unsqueeze(0)).last_hidden_state[0]   # [T, H] post-norm
    out = []
    for (s, e) in spans:
        # logits predicting tokens [s..e) come from hidden rows [s-1 .. e-2]
        ph = hidden[s - 1:e - 1]
        tgt = ids[s:e]
        tot = 0.0
        for i in range(0, ph.shape[0], chunk):
            lg = model.lm_head(ph[i:i + chunk]).float()
            lp = torch.log_softmax(lg, dim=-1)
            tot += -lp.gather(1, tgt[i:i + chunk].unsqueeze(1)).sum().item()
        out.append(tot / LN2 / len(tgt))          # mean bits/token
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B")
    ap.add_argument("--data-dir", type=Path, default=REPO / "data" / "posts")
    ap.add_argument("--out-dir", type=Path, default=REPO / "results" / "ablation")
    ap.add_argument("--horizon", type=int, default=60, help="items after each post to measure")
    ap.add_argument("--max-item-tokens", type=int, default=512)
    ap.add_argument("--limit", type=int, default=0, help="score only first N posts (smoke test)")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading {args.model} (sdpa) ...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="cuda",
        attn_implementation="sdpa").eval()
    bos = tok.bos_token_id or tok("\n", add_special_tokens=False)["input_ids"][0]
    sep_ids = tok("\n\n", add_special_tokens=False)["input_ids"]

    items, votes = load_items_and_votes(args.data_dir)
    ids_cache = [tok(it["text"], add_special_tokens=False)["input_ids"][:args.max_item_tokens]
                 for it in items]
    post_pos = [i for i, it in enumerate(items) if it["kind"] == "post"
                and len(ids_cache[i]) > 0]
    if args.limit:
        post_pos = post_pos[-args.limit:]          # tail-first sample for smoke test
    post_pos.sort(reverse=True)                    # tail -> head
    print(f"{len(post_pos)} posts, horizon {args.horizon}", file=sys.stderr)

    rows = []
    dist_sum = np.zeros(args.horizon); dist_n = np.zeros(args.horizon)
    t0 = time.time()
    for pi, X in enumerate(post_pos):
        x_ids = ids_cache[X]
        fut = [j for j in range(X + 1, min(X + 1 + args.horizon, len(items))) if len(ids_cache[j])]
        if not fut:
            continue
        blocks = [ids_cache[j] for j in fut]
        base = item_bits(model, [bos] + sep_ids + x_ids, blocks, sep_ids)
        abl = item_bits(model, [bos], blocks, sep_ids)
        deltas = [a - b for a, b in zip(abl, base)]   # >0 => X helped predict this item
        for off, j in enumerate(fut):
            k = j - X                                  # distance in items (1..H)
            dist_sum[k - 1] += deltas[off]; dist_n[k - 1] += 1
        it = items[X]
        d = np.array(deltas)
        dist = np.array([j - X for j in fut])
        rows.append({
            "post_id": it["id"], "author": it["author"], "author_model": it["author_model"],
            "created_at": it["created_at"], "votes": votes[("post", it["id"])],
            "n_future": len(fut),
            "clout_sum_30": round(float(d[dist <= 30].sum()), 4),
            "clout_sum_60": round(float(d.sum()), 4),
            "clout_mean_30": round(float(d[dist <= 30].mean()), 5),
            "clout_mean_60": round(float(d.mean()), 5),
        })
        if (pi + 1) % 25 == 0 or pi + 1 == len(post_pos):
            el = time.time() - t0
            print(f"  {pi+1}/{len(post_pos)}  {el:.0f}s  {(pi+1)/el:.2f} posts/s", file=sys.stderr)

    rows.sort(key=lambda r: r["created_at"])
    with (args.out_dir / "clout.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (args.out_dir / "clout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with (args.out_dir / "distance_curve.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["distance_items", "mean_delta_bits", "n"])
        for k in range(args.horizon):
            if dist_n[k]:
                w.writerow([k + 1, round(dist_sum[k] / dist_n[k], 6), int(dist_n[k])])

    # karma-vs-clout decoupling test (Spearman via rank Pearson)
    def spearman(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        ra = ra - ra.mean(); rb = rb - rb.mean()
        d = math.sqrt((ra**2).sum() * (rb**2).sum())
        return float((ra * rb).sum() / d) if d else None
    v = np.array([r["votes"] for r in rows], float)
    c30 = np.array([r["clout_sum_30"] for r in rows]); c60 = np.array([r["clout_sum_60"] for r in rows])
    run = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "horizon": args.horizon, "posts_scored": len(rows),
        "elapsed_sec": round(time.time() - t0, 1),
        "spearman_votes_clout30": round(spearman(v, c30), 4),
        "spearman_votes_clout60": round(spearman(v, c60), 4),
        "clout30_mean": round(float(c30.mean()), 4), "clout30_std": round(float(c30.std()), 4),
        "delta_at_1": round(float(dist_sum[0] / dist_n[0]), 5) if dist_n[0] else None,
        "delta_at_30": round(float(dist_sum[29] / dist_n[29]), 5) if dist_n[29] else None,
        "delta_at_60": round(float(dist_sum[-1] / dist_n[-1]), 5) if dist_n[-1] else None,
        "versions": {"torch": torch.__version__,
                     "transformers": __import__("transformers").__version__},
    }
    (args.out_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(run, indent=2))
    print(f"done -> {args.out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
