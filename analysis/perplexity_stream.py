#!/usr/bin/env python3
"""Long-horizon endogeneity: streaming LM perplexity over the 1f916.ai corpus.

The first perplexity pass conditioned each item on only ~8 preceding items
(a 3K-token window) — at this forum's burstiness that often spans minutes and
is dominated by concurrent thread-siblings, not accumulated culture. This pass
conditions each item on a much longer rolling history (~60-70 items / ~24-30K
tokens) to test whether novelty falls when the model can see the community's
accumulated back-catalogue (endogenous drift) or stays flat (no global
self-recycling).

Streaming with a KV cache keeps this cheap: each step forwards only the new
item (~400 tokens) attending to the cached history, so there is no quadratic
attention blow-up (flash-attention buys nothing here; SDPA suffices). The
corpus (~1.16M tokens) exceeds the model's 32K trained context, so instead of
RoPE-rebasing a sliding cache we use CHUNKED RESTART: grow the cache; when it
nears `cap`, rebuild it from the trailing `window_tokens` (positions reset to
0). Every item thus conditions on >= window_tokens of recent history.

self  = item alone (bos + item), no history.
cond  = item conditioned on the rolling long history.
Correctness of the KV-cache path is asserted against a plain re-encode in
--validate before the full run.

Outputs (results/perplexity_long/): metrics.jsonl/.csv, run.json.
Run: analysis/run_perplexity.sh -> point at this script, or
     .venv-less: /home/dan/miniforge3/envs/memetic/bin/python analysis/perplexity_stream.py
"""
import argparse, csv, json, math, sys, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO = Path(__file__).resolve().parent.parent
LN2 = math.log(2.0)


def load_items(data_dir):
    items = []
    for f in sorted(data_dir.glob("*.json"), key=lambda p: int(p.stem)):
        th = json.loads(f.read_text()); p = th["post"]
        items.append({"kind": "post", "id": p["id"], "post_id": p["id"],
                      "created_at": p["created_at"], "author": p["author"],
                      "author_model": p.get("author_model"),
                      "text": ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()})
        for c in th["comments"]:
            items.append({"kind": "comment", "id": c["id"], "post_id": p["id"],
                          "created_at": c["created_at"], "author": c["author"],
                          "author_model": c.get("author_model"),
                          "text": (c.get("body") or "").strip()})
    items.sort(key=lambda x: (x["created_at"], 0 if x["kind"] == "post" else 1, x["id"]))
    return items


@torch.no_grad()
def self_bits(model, bos, ids):
    """Mean bits/token for `ids` scored alone (bos-prefixed), suffix trick."""
    seq = torch.tensor([bos] + ids, device=model.device)
    logits = model(seq.unsqueeze(0), num_logits_to_keep=len(ids) + 1).logits[0]
    pred = logits[:-1].float()
    tgt = seq[-len(ids):]
    nats = -torch.log_softmax(pred, -1).gather(1, tgt.unsqueeze(1)).squeeze(1)
    return (nats / LN2).cpu().numpy()


class Stream:
    """Rolling KV cache with chunked restart. Scores each item conditioned on
    the accumulated history, carrying the boundary logit that predicts each
    item's first token."""
    def __init__(self, model, sep_ids, window_tokens, cap):
        self.m = model; self.sep = sep_ids
        self.window = window_tokens; self.cap = cap
        self.reset()

    def reset(self):
        self.cache = None; self.len = 0; self.boundary = None
        self.items = []   # (seq_idx, created_at, ntok) currently in cache

    @torch.no_grad()
    def _prefill(self, token_lists, chunk=512):
        """Fresh cache from [item, sep, item, sep, ...], fed in small chunks so
        the rebuild never runs one huge forward (keeps activation memory low);
        boundary = last-position logit of the final chunk."""
        seq = []
        for t in token_lists:
            seq += t + self.sep
        cache, boundary = None, None
        for i in range(0, len(seq), chunk):
            piece = torch.tensor(seq[i:i + chunk], device=self.m.device)
            # only the last-position logit is needed (the boundary); keeping all
            # chunk logits over a 150k vocab is a multi-GB transient that OOMs
            out = self.m(piece.unsqueeze(0), past_key_values=cache,
                         use_cache=True, num_logits_to_keep=1)
            cache = out.past_key_values
            boundary = out.logits[0, -1].float()
        self.cache = cache
        self.len = len(seq)
        self.boundary = boundary

    @torch.no_grad()
    def score(self, item, ids, all_ids):
        """Return (mean bits/token, effective context tokens, history seconds).
        all_ids: dict seq_idx -> token list, for rebuilds."""
        need = len(ids) + len(self.sep)
        # chunked restart: rebuild cache from trailing `window` tokens
        if self.items and (self.cache is None or self.len + need > self.cap):
            keep, tot = [], 0
            for it in reversed(self.items):
                if tot + it[2] > self.window and keep:
                    break
                keep.append(it); tot += it[2]
            keep.reverse()
            self._prefill([all_ids[s] for s, _, _ in keep])
            self.items = list(keep)

        ctx_tokens = self.len
        hist_sec = (item["created_at"] - self.items[0][1]) / 1000 if self.items else 0.0

        if self.boundary is None:      # empty history (very first item)
            sb = self_score(self.m, ids)          # cond == self
            bits = sb
        else:
            seq = torch.tensor(ids + self.sep, device=self.m.device)
            out = self.m(seq.unsqueeze(0), past_key_values=self.cache, use_cache=True)
            lg = out.logits[0]                     # [len(ids)+len(sep), V]
            # item token 0 from carried boundary; tokens 1.. from lg[0..len(ids)-2]
            rows = torch.cat([self.boundary.unsqueeze(0), lg[:len(ids) - 1].float()], 0)
            tgt = torch.tensor(ids, device=self.m.device)
            nats = -torch.log_softmax(rows, -1).gather(1, tgt.unsqueeze(1)).squeeze(1)
            bits = float((nats / LN2).mean())
            self.cache = out.past_key_values
            self.boundary = lg[-1].float()         # predicts next item's token 0
            self.len += len(ids) + len(self.sep)

        self.items.append((item["seq"], item["created_at"], len(ids) + len(self.sep)))
        return bits, ctx_tokens, hist_sec


def self_score(model, ids):
    return float(self_bits(model, model.config.bos_token_id or 0, ids).mean())


@torch.no_grad()
def reencode_cond(model, sep_ids, hist_ids, ids):
    """Ground-truth cond: re-encode [history + sep + item], score item suffix."""
    seq = hist_ids + sep_ids + ids
    t = torch.tensor(seq, device=model.device)
    logits = model(t.unsqueeze(0), num_logits_to_keep=len(ids) + 1).logits[0]
    pred = logits[:-1].float(); tgt = t[-len(ids):]
    nats = -torch.log_softmax(pred, -1).gather(1, tgt.unsqueeze(1)).squeeze(1)
    return float((nats / LN2).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B")
    ap.add_argument("--data-dir", type=Path, default=REPO / "data" / "posts")
    ap.add_argument("--out-dir", type=Path, default=REPO / "results" / "perplexity_long")
    ap.add_argument("--window-tokens", type=int, default=24000, help="min rolling history per item")
    ap.add_argument("--cap", type=int, default=30000, help="rebuild cache before exceeding this")
    ap.add_argument("--max-item-tokens", type=int, default=512)
    ap.add_argument("--low-info-bits", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--validate", action="store_true", help="assert KV path == re-encode, then exit")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading {args.model} (sdpa) ...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="cuda", attn_implementation="sdpa").eval()
    # force memory-efficient / flash SDPA kernels; the math backend materializes
    # the full [q, kv] score matrix over the long cache and OOMs.
    torch.backends.cuda.enable_math_sdp(False)
    torch.backends.cuda.enable_mem_efficient_sdp(True)
    torch.backends.cuda.enable_flash_sdp(True)
    if model.config.bos_token_id is None:
        model.config.bos_token_id = tok("\n", add_special_tokens=False)["input_ids"][0]
    sep_ids = tok("\n\n", add_special_tokens=False)["input_ids"]

    items = load_items(args.data_dir)
    if args.limit:
        items = items[:args.limit]
    for i, it in enumerate(items):
        it["seq"] = i
    all_ids = {i: tok(it["text"], add_special_tokens=False)["input_ids"][:args.max_item_tokens]
               for i, it in enumerate(items)}

    if args.validate:
        # score items via streaming with a SMALL window, and independently
        # re-encode the exact same conditioning tokens; assert agreement.
        st = Stream(model, sep_ids, window_tokens=1500, cap=2500)  # small -> exercises rebuilds
        worst = 0.0; checked = 0
        for i, it in enumerate(items[:60]):
            ids = all_ids[i]
            if not ids:
                continue
            b, ctx, _ = st.score(it, ids, all_ids)
            # streaming conditioned on st.items MINUS the just-appended current item
            cond_items = st.items[:-1]
            if cond_items and st.boundary is not None:
                hist = []
                for s, _, _ in cond_items:
                    hist += all_ids[s] + sep_ids
                hist = hist[:-len(sep_ids)]
                ref = reencode_cond(model, sep_ids, hist, ids)
                worst = max(worst, abs(b - ref)); checked += 1
        print(f"validation: max |streaming - reencode| over {checked} items = {worst:.4f} bits/token")
        print("PASS" if worst < 0.02 else "FAIL — KV path diverges from re-encode")
        return

    st = Stream(model, sep_ids, args.window_tokens, args.cap)
    rows = []; t0 = time.time()
    for i, it in enumerate(items):
        ids = all_ids[i]
        if not ids:
            continue
        chars = len(it["text"])
        cond, ctx_tokens, hist_sec = st.score(it, ids, all_ids)
        sb = self_bits(model, model.config.bos_token_id, ids)
        row = {"seq": i, "kind": it["kind"], "id": it["id"], "post_id": it["post_id"],
               "created_at": it["created_at"], "author": it["author"],
               "author_model": it["author_model"], "chars": chars, "tokens": len(ids),
               "self_bits_per_tok": round(float(sb.mean()), 4),
               "cond_bits_per_tok": round(cond, 4),
               "novelty_ratio": round(cond / float(sb.mean()), 4) if sb.mean() else None,
               "ctx_tokens": ctx_tokens, "history_hours": round(hist_sec / 3600, 2)}
        rows.append(row)
        if (i + 1) % 200 == 0 or i + 1 == len(items):
            el = time.time() - t0
            print(f"  {i+1}/{len(items)}  {el:.0f}s  {(i+1)/el:.1f} it/s  "
                  f"ctx~{ctx_tokens}tok/{row['history_hours']}h", file=sys.stderr)

    with (args.out_dir / "metrics.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (args.out_dir / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    tc = sum(r["tokens"] for r in rows)
    nov = sum(r["cond_bits_per_tok"] * r["tokens"] for r in rows) / sum(r["self_bits_per_tok"] * r["tokens"] for r in rows)
    checks = {"items": len(rows),
              "median_ctx_tokens": sorted(r["ctx_tokens"] for r in rows)[len(rows) // 2],
              "median_history_hours": sorted(r["history_hours"] for r in rows)[len(rows) // 2],
              "corpus_novelty_long": round(nov, 4),
              "cond_le_self_frac": round(sum(r["cond_bits_per_tok"] <= r["self_bits_per_tok"] + 0.05 for r in rows) / len(rows), 4)}
    run = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "model": args.model, "window_tokens": args.window_tokens, "cap": args.cap,
           "elapsed_sec": round(time.time() - t0, 1), "sanity": checks,
           "versions": {"torch": torch.__version__, "transformers": __import__("transformers").__version__}}
    (args.out_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    print(f"done -> {args.out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
