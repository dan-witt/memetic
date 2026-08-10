#!/usr/bin/env python3
"""Vendi Score: semantic-diversity control across corpora. The token-level passes
(zstd, perplexity, shingles) catch verbatim/near-verbatim recycling; Vendi catches
PARAPHRASED recycling -- same idea, different words. Vendi = exp(Shannon entropy of
the eigenvalues of the N x N cosine-similarity matrix of item embeddings) = the
"effective number of distinct items." Reference-free (Friedman & Dieng 2022,
arXiv:2210.02410).

Reports (a) matched-N Vendi (subsample all corpora to the smallest, avg over draws)
so the number is comparable, and (b) rolling-window Vendi/W over normalized time --
a near-direct mode-collapse curve. Embeddings: BAAI/bge-large-en-v1.5. GPU."""
import json, sys
from pathlib import Path
import numpy as np

# Usage: vendi.py <out-dir> "<label>=<data-dir>" ["<label>=<data-dir>" ...]  (2-4 corpora)
if len(sys.argv) < 3:
    sys.exit('usage: vendi.py <out-dir> "label=data_dir" ["label=data_dir" ...]')
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
CORPORA = [tuple(a.split("=", 1)) for a in sys.argv[2:]]
MODEL = "BAAI/bge-large-en-v1.5"
WIN, STRIDE, DRAWS, SEED = 120, 40, 6, 0
SURFACE="#fcfcfb"; INK="#0b0b0b"; MUTED="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
S_BLUE="#2a78d6"; S_ORANGE="#eb6834"; S_VIOLET="#4a3aa7"
COLORS = [S_VIOLET, S_BLUE, S_ORANGE]


def load_items(data_dir):
    items = []
    for f in Path(data_dir).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        items.append((p["created_at"], ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()))
        for c in th.get("comments", []):
            items.append((c["created_at"], (c.get("body") or "").strip()))
    items.sort(key=lambda x: x[0])
    return [t for _, t in items if t]


def vendi(emb, q=1):
    """emb: N x D, L2-normalized rows. exp(H(eigenvalues of K/N)), K = emb emb^T."""
    n = len(emb)
    lam = np.linalg.eigvalsh((emb @ emb.T) / n)
    lam = lam[lam > 1e-12]; lam = lam / lam.sum()
    if q == 1:
        return float(np.exp(-(lam * np.log(lam)).sum()))
    return float((lam ** q).sum() ** (1.0 / (1.0 - q)))


def main():
    from sentence_transformers import SentenceTransformer
    print(f"loading {MODEL} ...", file=sys.stderr)
    model = SentenceTransformer(MODEL, device="cuda")
    rng = np.random.default_rng(SEED)

    corpora = []
    for label, d in CORPORA:
        if not Path(d).exists():
            print(f"skip (missing): {label}", file=sys.stderr); continue
        texts = load_items(d)
        emb = model.encode(texts, normalize_embeddings=True, batch_size=64,
                           show_progress_bar=False).astype(np.float32)
        corpora.append({"label": label, "emb": emb, "n": len(emb)})
        print(f"embedded {label}: {len(emb)} items", file=sys.stderr)

    nmatch = min(c["n"] for c in corpora)
    result = {"model": MODEL, "n_match": nmatch, "window": WIN, "corpora": {}}
    for c in corpora:
        # matched-N Vendi: average over DRAWS random subsamples of size nmatch
        vs = [vendi(c["emb"][rng.choice(c["n"], nmatch, replace=False)]) for _ in range(DRAWS)]
        # rolling-window Vendi/W over the chronological sequence
        roll = []
        for s in range(0, c["n"] - WIN + 1, STRIDE):
            roll.append(vendi(c["emb"][s:s + WIN]) / WIN)
        result["corpora"][c["label"]] = {
            "n": c["n"],
            "vendi_matchedN": round(float(np.mean(vs)), 2),
            "vendi_matchedN_frac": round(float(np.mean(vs)) / nmatch, 4),
            "vendi_matchedN_sd": round(float(np.std(vs)), 2),
            "rolling_vendi_over_W_mean": round(float(np.mean(roll)), 4),
            "rolling_curve": [round(x, 4) for x in roll]}
    (OUT / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({c: {k: result["corpora"][c][k] for k in
          ("n", "vendi_matchedN", "vendi_matchedN_frac", "rolling_vendi_over_W_mean")}
          for c in result["corpora"]}, indent=2))

    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=200); fig.set_facecolor(SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE); ax.grid(True, color=GRID, linewidth=.7)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        for sp in ("bottom", "left"): ax.spines[sp].set_color(BASE)
        ax.tick_params(colors=MUTED, labelsize=9)
    labs = list(result["corpora"])
    fr = [result["corpora"][l]["vendi_matchedN_frac"] for l in labs]
    ax1.barh(range(len(labs)), fr, color=COLORS[:len(labs)], height=.6)
    for i, v in enumerate(fr): ax1.annotate(f"{v:.3f}", (v, i), xytext=(4, 0),
                                            textcoords="offset points", va="center", color=INK, fontsize=9)
    ax1.set_yticks(range(len(labs))); ax1.set_yticklabels(labs, fontsize=9, color=INK)
    ax1.set_xlabel(f"effective-distinct fraction (Vendi / N, matched N={nmatch})", color=MUTED, fontsize=9)
    ax1.set_title("Semantic diversity: effective distinct items", loc="left", color=INK, fontsize=10.5)
    for l, col in zip(labs, COLORS):
        r = result["corpora"][l]["rolling_curve"]; xs = np.linspace(0, 1, len(r))
        ax2.plot(xs, r, color=col, lw=1.8, label=l.split(" (")[0])
    ax2.set_xlabel("position through corpus (0=first, 1=last)", color=MUTED, fontsize=9)
    ax2.set_ylabel(f"rolling Vendi / W  (W={WIN})", color=MUTED, fontsize=9)
    ax2.set_title("Semantic diversity over time (mode-collapse curve)", loc="left", color=INK, fontsize=10.5)
    ax2.legend(frameon=False, fontsize=8, labelcolor=INK)
    fig.suptitle("Semantic-diversity control (Vendi Score, bge-large embeddings)",
                 x=.01, ha="left", color=INK, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(OUT / "figure.png", facecolor=SURFACE); fig.savefig(OUT / "figure.svg", facecolor=SURFACE)
    print("wrote comparison.json + figure", file=sys.stderr)


if __name__ == "__main__":
    main()
