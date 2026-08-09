#!/usr/bin/env python3
"""Diagnostic: why does peppercorn's provenance-interrogation sweep (comments
1300-1303) score high predictive contribution (PC) in the all-items ablation,
when its real influence -- a paraphrase-spread disclosure norm -- is exactly the
kind of long-horizon, non-verbatim effect PC cannot see?

The four interrogations were posted consecutively in one minute, so a comment's
next 1-3 items are its own near-identical siblings. This scores each of the four
with a per-distance PC profile and marks which downstream items are peppercorn
siblings, to show the high PC is self-similarity (peppercorn predicting
peppercorn), not downstream cascade. The one comment with no sibling after it
(1303) is the clean control.

Reuses analysis/ablation.py scoring. Writes results/ablation_all/{sweep_probe.json,
sweep_figure.png/svg}. GPU (Qwen2.5-7B); ~1 min."""
import json, sys
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ablation import load_items_and_votes, item_bits, REPO  # noqa: E402

OUT = REPO / "results" / "ablation_all"
SWEEP = [1300, 1301, 1302, 1303]
HZN = 12
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2.5-7B", torch_dtype=torch.float16, device_map="cuda",
        attn_implementation="sdpa").eval()
    bos = tok.bos_token_id or tok("\n", add_special_tokens=False)["input_ids"][0]
    sep = tok("\n\n", add_special_tokens=False)["input_ids"]
    items, _ = load_items_and_votes(REPO / "data" / "posts")
    idc = [tok(it["text"], add_special_tokens=False)["input_ids"][:512] for it in items]
    pos = {(it["kind"], it["id"]): i for i, it in enumerate(items)}

    probe = {}
    for cid in SWEEP:
        X = pos[("comment", cid)]
        fut = [j for j in range(X + 1, min(X + 1 + HZN, len(items))) if len(idc[j])]
        blocks = [idc[j] for j in fut]
        base = item_bits(model, [bos] + sep + idc[X], blocks, sep)
        abl = item_bits(model, [bos], blocks, sep)
        deltas = [round(a - b, 4) for a, b in zip(abl, base)]
        sib = [items[j]["author"] == "peppercorn" for j in fut]
        tot = sum(deltas)
        probe[cid] = {"total_PC": round(tot, 3), "deltas": deltas, "sibling": sib,
                      "siblings_after": sum(sib[:3]),
                      "frac_in_d1_3": round(sum(deltas[:3]) / tot, 3) if tot else None,
                      "downstream_ids": [items[j]["id"] for j in fut]}
    (OUT / "sweep_probe.json").write_text(json.dumps(probe, indent=2) + "\n")
    print(json.dumps({c: {k: probe[c][k] for k in ("total_PC", "siblings_after", "frac_in_d1_3")}
                      for c in SWEEP}, indent=2))

    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), dpi=200, sharey=True)
    fig.set_facecolor(SURFACE)
    for ax, cid in zip(axes, SWEEP):
        ax.set_facecolor(SURFACE); ax.grid(True, axis="y", color=GRID, linewidth=.7)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        for s in ("bottom", "left"): ax.spines[s].set_color(BASE)
        ax.tick_params(colors=MUTED, labelsize=8)
        d = probe[cid]["deltas"]; sib = probe[cid]["sibling"]
        xs = list(range(1, len(d) + 1))
        cols = [S_ORANGE if s else S_BLUE for s in sib]
        ax.bar(xs, d, color=cols, width=.72)
        ax.axhline(0, color=BASE, lw=.8)
        sc = probe[cid]["siblings_after"]
        ax.set_title(f"c{cid}  PC={probe[cid]['total_PC']}\n{sc} sibling(s) after",
                     color=INK, fontsize=9.5, loc="left")
        ax.set_xlabel("distance", color=MUTED, fontsize=8.5)
    axes[0].set_ylabel("PC Δ (bits/token)", color=MUTED, fontsize=9)
    fig.suptitle("1f916.ai - peppercorn's interrogation sweep: high PC is sibling self-prediction "
                 "(orange = a peppercorn sibling), not cascade",
                 x=.01, ha="left", color=INK, fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .9))
    fig.savefig(OUT / "sweep_figure.png", facecolor=SURFACE)
    fig.savefig(OUT / "sweep_figure.svg", facecolor=SURFACE)
    print("wrote sweep_probe.json + sweep_figure.{png,svg}")


if __name__ == "__main__":
    main()
