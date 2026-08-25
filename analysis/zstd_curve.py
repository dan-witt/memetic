#!/usr/bin/env python3
"""zstd ritual-accumulation curve for the 1f916.ai corpus.

Measures per-character information of every post and comment, standalone vs.
conditioned on forum history, using zstd raw-content dictionaries as the
conditional compressor. A growing gap between standalone and conditioned
description length — i.e. a falling novelty ratio — is the signature of
ritual accumulation (near-verbatim formulae recurring across authors).

Conditioning variants per item:
  self       standalone zstd (intrinsic redundancy of the item alone)
  cond_win   dictionary = trailing window of prior items (fixed byte budget,
             so conditioning capacity is constant over playback — headline)
  cond_full  dictionary = entire prior history (capacity grows; confounded)
  cond_shuf  dictionary = seeded random sample of OTHER items regardless of
             time (controls for "generic agent-forum text" predictability)

Outputs (results/zstd_curve/): metrics.jsonl, metrics.csv, curve.csv,
curve.png, curve.svg, glossary.md, run.json.

Run via analysis/run.sh (bootstraps the venv) or:
  .venv/bin/python analysis/zstd_curve.py
"""

import argparse
import csv
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import zstandard as zstd

REPO = Path(__file__).resolve().parent.parent
SEP = b"\n\n"


def relparam(v):
    """Record paths repo-relative in run.json so it's portable across clones."""
    if isinstance(v, Path):
        try:
            return str(v.resolve().relative_to(REPO))
        except ValueError:
            return str(v)
    return v

# --- palette (dataviz reference instance, light mode, validated order) ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
S_BLUE = "#2a78d6"    # self bpc (all items)
S_ORANGE = "#eb6834"  # conditioned bpc, posts
S_AQUA = "#1baf7a"    # conditioned bpc, comments
S_VIOLET = "#4a3aa7"  # novelty ratio


def load_items(data_dir: Path):
    """Every post and comment as {kind, id, post_id, created_at, author,
    author_model, text}, chronologically sorted."""
    items = []
    for f in sorted(data_dir.glob("*.json"), key=lambda p: int(p.stem)):
        thread = json.loads(f.read_text())
        p = thread["post"]
        text = (p.get("title") or "") + "\n\n" + (p.get("body") or "")
        items.append({
            "kind": "post", "id": p["id"], "post_id": p["id"],
            "created_at": p["created_at"], "author": p["author"],
            "author_model": p.get("author_model"), "text": text.strip(),
        })
        for c in thread["comments"]:
            items.append({
                "kind": "comment", "id": c["id"], "post_id": p["id"],
                "created_at": c["created_at"], "author": c["author"],
                "author_model": c.get("author_model"),
                "text": (c.get("body") or "").strip(),
            })
    items.sort(key=lambda x: (x["created_at"], 0 if x["kind"] == "post" else 1, x["id"]))
    return items


class Conditioner:
    """Compressed size of a payload, optionally conditioned on a raw-content
    zstd dictionary. Frame overhead (empty-payload size) is subtracted so
    short texts aren't dominated by header bytes."""

    def __init__(self, level: int, history: bytes | None = None):
        if history:
            d = zstd.ZstdCompressionDict(history, dict_type=zstd.DICT_TYPE_RAWCONTENT)
            self.cctx = zstd.ZstdCompressor(level=level, dict_data=d)
        else:
            self.cctx = zstd.ZstdCompressor(level=level)
        self.overhead = len(self.cctx.compress(b""))

    def bits(self, payload: bytes) -> int:
        return max(0, len(self.cctx.compress(payload)) - self.overhead) * 8


def tail_bytes(chunks: list[bytes], budget: int) -> bytes:
    """Concatenate the most recent chunks up to ~budget bytes."""
    out, total = [], 0
    for ch in reversed(chunks):
        out.append(ch)
        total += len(ch) + len(SEP)
        if total >= budget:
            break
    return SEP.join(reversed(out))


def shuffle_sample(encoded: list[bytes], exclude: range, budget: int, rng: random.Random) -> bytes:
    """Seeded random sample of items outside `exclude`, up to ~budget bytes."""
    pool = [i for i in range(len(encoded)) if i not in exclude]
    rng.shuffle(pool)
    out, total = [], 0
    for i in pool:
        out.append(encoded[i])
        total += len(encoded[i]) + len(SEP)
        if total >= budget:
            break
    return SEP.join(out)


ALL_COLUMNS = ("self", "cond_win", "cond_full", "cond_shuf")


def compute_metrics(items, args, columns=ALL_COLUMNS, reuse=None):
    """-> one row per non-empty item.

    COST. Three of the four conditioners are cheap and one is not. `win` builds a dictionary from a
    fixed `window_bytes` tail and `shuf` from a fixed-size sample, so both cost the same per bucket
    however long the corpus is. `full` builds one from the ENTIRE prior history, once per bucket,
    so its cost grows with the corpus and the pass is quadratic overall: at 19,334 items that was
    ~773 dictionary builds over an average ~12 MB, and it dominated everything else.

    `columns` selects which of those to pay for. A caller that reads only self_bits and
    cond_win_bits -- the weather report's register cell does -- passes ("self", "cond_win") and the
    quadratic term disappears entirely. The default computes all four, so the standalone zstd pass
    is unchanged.

    `reuse` makes the remainder incremental: {item_key: row} from a previous run. self_bits depends
    only on the item, and cond_win_bits on the item plus the trailing window of history BEFORE its
    bucket, so both are PREFIX-STABLE -- appending later items cannot change an earlier item's
    value. Rows are reused for the longest leading run whose key and content hash match, and
    everything from the first divergence is recomputed. Three things break the prefix and are
    detected rather than assumed: an edited item (hash mismatch), an item inserted mid-stream by
    backfill (key mismatch, and it shifts every later bucket boundary because buckets are indexed
    from 0), and a change to level/bucket/window_bytes (the caller must not reuse across those).
    cond_full IS prefix-stable in the same sense (its dictionary is the history before the bucket),
    so it is reusable; it is simply not worth computing for a caller that does not read it. Only
    cond_shuf is NOT prefix-stable -- it samples items regardless of time, including ones after the
    item being scored -- so requesting it alongside `reuse` is refused.
    """
    columns = tuple(columns)
    if reuse is not None and "cond_shuf" in columns:
        raise ValueError("cond_shuf samples items regardless of time, including items AFTER the "
                         "one being scored, so it is not prefix-stable and cannot be reused; "
                         "drop it from `columns` or drop `reuse`")
    want_full = "cond_full" in columns
    want_shuf = "cond_shuf" in columns
    encoded = [it["text"].encode("utf-8") for it in items]
    n = len(items)

    # Where the cached prefix stops being valid.
    resume = 0
    shas = None
    if reuse is not None:
        shas = [hashlib.sha256(b).hexdigest()[:16] for b in encoded]
        for i in range(n):
            key = f"{items[i]['kind']}:{items[i]['id']}"
            prev = reuse.get(key)
            # Key, content AND POSITION. The cache is keyed by item, so an insertion is caught by
            # the key lookup and an edit by the hash -- but a DELETION would shift every later item
            # down while leaving all keys and hashes intact, and those items' cond_win was computed
            # against a history that still contained the removed item. Requiring the cached seq to
            # equal the current index makes the prefix check exact instead of nearly exact.
            if prev is None or prev.get("sha") != shas[i] or prev.get("seq") != i:
                break
            resume = i + 1
        print(f"  zstd cache: {resume}/{n} rows reusable, recomputing from {resume}",
              file=sys.stderr)

    history: list[bytes] = []
    rows = []
    plain = Conditioner(args.level)
    for start in range(0, n, args.bucket):
        bucket = range(start, min(start + args.bucket, n))
        if bucket.stop <= resume:
            # Entirely inside the valid prefix: reuse the rows and only carry the history forward.
            for i in bucket:
                if len(items[i]["text"]) == 0:
                    history.append(encoded[i]); continue
                rows.append(reuse[f"{items[i]['kind']}:{items[i]['id']}"])
                history.append(encoded[i])
            continue
        if history:
            win = Conditioner(args.level, tail_bytes(history, args.window_bytes))
            full = Conditioner(args.level, SEP.join(history)) if want_full else None
        else:
            win = plain
            full = plain if want_full else None
        if want_shuf:
            rng = random.Random(f"{args.seed}:{start}")
            shuf_hist = shuffle_sample(encoded, bucket, args.window_bytes, rng)
            shuf = Conditioner(args.level, shuf_hist) if shuf_hist else plain

        for i in bucket:
            it, data = items[i], encoded[i]
            chars = len(it["text"])
            if chars == 0:
                history.append(data)
                continue
            if i < resume:
                rows.append(reuse[f"{it['kind']}:{it['id']}"])
                history.append(data)
                continue
            self_bits = plain.bits(data)
            row = {
                "seq": i, "kind": it["kind"], "id": it["id"], "post_id": it["post_id"],
                "created_at": it["created_at"], "author": it["author"],
                "author_model": it["author_model"], "chars": chars, "bytes": len(data),
                "self_bits": self_bits,
                "cond_win_bits": win.bits(data),
            }
            if want_full:
                row["cond_full_bits"] = full.bits(data)
            if want_shuf:
                row["cond_shuf_bits"] = shuf.bits(data)
            for k in columns:
                row[f"{k}_bpc"] = round(row[f"{k}_bits"] / chars, 4)
            row["novelty_ratio"] = round(row["cond_win_bits"] / self_bits, 4) if self_bits else None
            if shas is not None:
                row["sha"] = shas[i]
            rows.append(row)
            history.append(data)
        done = bucket.stop
        if done % 500 < args.bucket or done == n:
            print(f"  {done}/{n} items conditioned", file=sys.stderr)
    return rows


def rolling(rows, bits_key, roll, pred=None):
    """Aggregate rolling bpc: sum(bits)/sum(chars) over the trailing `roll`
    items matching pred. Returns (created_at, value, n) tuples."""
    sel = [r for r in rows if pred is None or pred(r)]
    out = []
    for i in range(roll - 1, len(sel)):
        w = sel[i - roll + 1: i + 1]
        out.append((sel[i]["created_at"],
                    sum(r[bits_key] for r in w) / sum(r["chars"] for r in w),
                    roll))
    return out


def rolling_ratio(rows, num_key, den_key, roll, pred=None):
    sel = [r for r in rows if pred is None or pred(r)]
    out = []
    for i in range(roll - 1, len(sel)):
        w = sel[i - roll + 1: i + 1]
        out.append((sel[i]["created_at"],
                    sum(r[num_key] for r in w) / sum(r[den_key] for r in w),
                    roll))
    return out


def build_curves(rows, args):
    is_post = lambda r: r["kind"] == "post"
    is_comment = lambda r: r["kind"] == "comment"
    return {
        "self_bpc_all": rolling(rows, "self_bits", args.roll),
        "cond_win_bpc_all": rolling(rows, "cond_win_bits", args.roll),
        "cond_win_bpc_posts": rolling(rows, "cond_win_bits", args.roll_posts, is_post),
        "cond_win_bpc_comments": rolling(rows, "cond_win_bits", args.roll, is_comment),
        "cond_full_bpc_all": rolling(rows, "cond_full_bits", args.roll),
        "novelty_ratio_all": rolling_ratio(rows, "cond_win_bits", "self_bits", args.roll),
        "novelty_ratio_shuffled": rolling_ratio(rows, "cond_shuf_bits", "self_bits", args.roll),
    }


def build_glossary(items, min_authors=3, top=25):
    """Recurring near-verbatim material: duplicated lines (>=30 chars) and
    8-word shingles appearing across >= min_authors distinct authors."""
    def collect(extract):
        seen = {}
        for it in items:
            for s in set(extract(it["text"])):
                e = seen.setdefault(s, {"authors": set(), "items": 0,
                                        "first_seen": it["created_at"], "kinds": set()})
                e["authors"].add(it["author"])
                e["items"] += 1
                e["first_seen"] = min(e["first_seen"], it["created_at"])
                e["kinds"].add(it["kind"])
        return seen

    lines = collect(lambda t: [ln.strip() for ln in t.splitlines() if len(ln.strip()) >= 30])
    words_of = lambda t: t.split()
    def shingles(t):
        w = words_of(t)
        return [" ".join(w[i:i + 8]) for i in range(len(w) - 7)]
    shingle_map = collect(shingles)

    def rank(seen):
        cand = [(s, e) for s, e in seen.items() if len(e["authors"]) >= min_authors]
        cand.sort(key=lambda kv: len(kv[0]) * len(kv[1]["authors"]), reverse=True)
        return cand

    kept_lines = rank(lines)[:top]
    kept_line_texts = [s for s, _ in kept_lines]
    # collapse shifted variants of one phrase: shingles shifted by <= 3 words
    # share a 5-gram, so keep a candidate only if none of its 5-grams is
    # covered by an already-kept shingle
    covered = set()
    kept_shingles = []
    for s, e in rank(shingle_map):
        if any(s in ln for ln in kept_line_texts):
            continue
        w = s.split()
        grams = [tuple(w[i:i + 5]) for i in range(len(w) - 4)]
        if any(g in covered for g in grams):
            continue
        covered.update(grams)
        kept_shingles.append((s, e))
        if len(kept_shingles) >= top:
            break
    return kept_lines, kept_shingles


def fmt_ts(ms):
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(ms / 1000))


def write_glossary(kept_lines, kept_shingles, out_dir):
    def table(rows_):
        out = ["| snippet | authors | items | kinds | first seen |",
               "|---|---|---|---|---|"]
        for s, e in rows_:
            snip = s if len(s) <= 110 else s[:107] + "..."
            snip = snip.replace("|", "\\|")
            out.append(f"| {snip} | {len(e['authors'])} | {e['items']} | "
                       f"{'+'.join(sorted(e['kinds']))} | {fmt_ts(e['first_seen'])} |")
        return "\n".join(out)

    md = ["# Ritual glossary (auto-extracted)", "",
          "Near-verbatim material recurring across >= 3 distinct authors,",
          "ranked by length x author count. Generated by `analysis/zstd_curve.py`.",
          "", "## Duplicated lines (>= 30 chars)", "", table(kept_lines), "",
          "## Duplicated 8-word shingles (not contained in a line above)", "",
          table(kept_shingles), ""]
    (out_dir / "glossary.md").write_text("\n".join(md))


def make_figure(curves, t0, event_ms, window_full_ms, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    hours = lambda pts: [(t - t0) / 3.6e6 for t, _, _ in pts]
    vals = lambda pts: [v for _, v, _ in pts]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.2), sharex=True, dpi=200)
    fig.set_facecolor(SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis="y", color=GRID, linewidth=0.75)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("bottom", "left"):
            ax.spines[side].set_color(BASELINE)
        ax.tick_params(colors=MUTED, labelsize=9)

    series1 = [
        ("self_bpc_all", S_BLUE, "standalone (all items)"),
        ("cond_win_bpc_posts", S_ORANGE, "conditioned - posts"),
        ("cond_win_bpc_comments", S_AQUA, "conditioned - comments"),
    ]
    for key, color, label in series1:
        pts = curves[key]
        ax1.plot(hours(pts), vals(pts), color=color, linewidth=2, label=label)
        ax1.annotate(label, (hours(pts)[-1], vals(pts)[-1]),
                     xytext=(6, 0), textcoords="offset points",
                     color=INK, fontsize=8.5, va="center")
    ax1.set_title("Per-character information: standalone vs. conditioned on forum history",
                  loc="left", color=INK, fontsize=11)
    ax1.set_ylabel("bits / char (rolling)", color=MUTED, fontsize=9)

    pts = curves["novelty_ratio_all"]
    ax2.plot(hours(pts), vals(pts), color=S_VIOLET, linewidth=2,
             label="novelty ratio (window-conditioned)")
    ax2.annotate("novelty ratio", (hours(pts)[-1], vals(pts)[-1]),
                 xytext=(6, 0), textcoords="offset points",
                 color=INK, fontsize=8.5, va="center")
    pts = curves["novelty_ratio_shuffled"]
    ax2.plot(hours(pts), vals(pts), color=MUTED, linewidth=1.5,
             linestyle=(0, (4, 3)), label="shuffled-history control")
    ax2.annotate("shuffled control", (hours(pts)[-1], vals(pts)[-1]),
                 xytext=(6, 0), textcoords="offset points",
                 color=MUTED, fontsize=8.5, va="center")
    ax2.set_title("Novelty ratio: conditioned / standalone bits (1.0 = history teaches nothing)",
                  loc="left", color=INK, fontsize=11)
    ax2.set_ylabel("ratio (rolling)", color=MUTED, fontsize=9)
    ax2.set_xlabel("hours since first post", color=MUTED, fontsize=9)

    ev_h = (event_ms - t0) / 3.6e6
    fill_h = (window_full_ms - t0) / 3.6e6
    span_left = ax1.get_xlim()[0]
    for ax in (ax1, ax2):
        ax.axvline(ev_h, color=BASELINE, linewidth=1, linestyle=(0, (3, 3)))
        ax.axvspan(span_left, fill_h, color=GRID, alpha=0.45, zorder=0)
    ax1.annotate("posts 210-211", (ev_h, ax1.get_ylim()[1]),
                 xytext=(4, -4), textcoords="offset points",
                 color=MUTED, fontsize=8, va="top")
    ax2.annotate("window\nfilling", (fill_h, ax2.get_ylim()[1]),
                 xytext=(-4, -4), textcoords="offset points",
                 color=MUTED, fontsize=8, va="top", ha="right")

    leg = ax1.legend(frameon=False, fontsize=8.5, loc="center right", labelcolor=INK)
    for h in leg.legend_handles:
        h.set_linewidth(2)
    leg = ax2.legend(frameon=False, fontsize=8.5, loc="upper right", labelcolor=INK)
    for h in leg.legend_handles:
        h.set_linewidth(2)
    # direct labels sit past the right edge; leave room
    x_last = max(hours(curves["self_bpc_all"])[-1], hours(curves["novelty_ratio_all"])[-1])
    ax1.set_xlim(right=x_last * 1.18)

    fig.suptitle("1f916.ai - ritual accumulation as compressibility", x=0.01,
                 ha="left", color=INK, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_dir / "curve.png", facecolor=SURFACE)
    fig.savefig(out_dir / "curve.svg", facecolor=SURFACE)
    plt.close(fig)


def sanity_checks(rows, items, args, data_dir):
    checks = {}
    manifest = json.loads((data_dir.parent / "manifest.json").read_text())
    n_posts = sum(1 for r in rows if r["kind"] == "post")
    n_comments = sum(1 for r in rows if r["kind"] == "comment")
    checks["counts"] = {
        "posts_measured": n_posts, "comments_measured": n_comments,
        "threads_in_manifest": manifest["threads_saved"],
        "posts_match_manifest": n_posts == manifest["threads_saved"],
    }
    tol_bits = 32 * 8
    worse = sum(1 for r in rows if r["cond_win_bits"] > r["self_bits"] + tol_bits)
    checks["conditioning_never_hurts"] = {
        "items_where_cond_exceeds_self_plus_tol": worse,
        "fraction": round(worse / len(rows), 5),
    }
    # known ritual: the "Provenance:" disclaimer line family (cf. post 426)
    text_of = {(it["kind"], it["id"]): it["text"] for it in items}
    prov = [r["cond_win_bpc"] for r in rows
            if "Provenance:" in text_of[(r["kind"], r["id"])]]
    med_all = sorted(r["cond_win_bpc"] for r in rows)[len(rows) // 2]
    checks["provenance_ritual"] = {
        "n_items_containing_Provenance": len(prov),
        "their_median_cond_win_bpc": round(sorted(prov)[len(prov) // 2], 3) if prov else None,
        "corpus_median_cond_win_bpc": round(med_all, 3),
    }
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", type=Path, default=REPO / "data" / "posts")
    ap.add_argument("--out-dir", type=Path, default=REPO / "results" / "zstd_curve")
    ap.add_argument("--level", type=int, default=19)
    ap.add_argument("--window-bytes", type=int, default=512 * 1024)
    ap.add_argument("--bucket", type=int, default=25,
                    help="rebuild conditioning dictionaries every N items")
    ap.add_argument("--exact", action="store_true", help="shorthand for --bucket 1")
    ap.add_argument("--roll", type=int, default=100, help="rolling window, all-item series")
    ap.add_argument("--roll-posts", type=int, default=50, help="rolling window, posts-only series")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if args.exact:
        args.bucket = 1
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print("loading corpus...", file=sys.stderr)
    items = load_items(args.data_dir)
    t0 = items[0]["created_at"]
    event_ms = 1786061073591  # post 210 (peppercorn), post 211 follows ~2 min later
    print(f"{len(items)} items, span {(items[-1]['created_at'] - t0) / 3.6e6:.1f} h",
          file=sys.stderr)

    print(f"conditioning (level={args.level}, window={args.window_bytes}, "
          f"bucket={args.bucket})...", file=sys.stderr)
    rows = compute_metrics(items, args)

    with (args.out_dir / "metrics.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with (args.out_dir / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    curves = build_curves(rows, args)
    with (args.out_dir / "curve.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["series", "created_at_ms", "hours_since_start", "value", "roll_n"])
        for name, pts in curves.items():
            for t, v, n in pts:
                w.writerow([name, t, round((t - t0) / 3.6e6, 4), round(v, 5), n])

    print("extracting glossary...", file=sys.stderr)
    kept_lines, kept_shingles = build_glossary(items)
    write_glossary(kept_lines, kept_shingles, args.out_dir)

    # first timestamp at which cumulative history reaches the window budget —
    # conditioning capacity is constant only after this point
    cum, window_full_ms = 0, items[-1]["created_at"]
    for it in items:
        cum += len(it["text"].encode("utf-8")) + len(SEP)
        if cum >= args.window_bytes:
            window_full_ms = it["created_at"]
            break

    print("rendering figure...", file=sys.stderr)
    make_figure(curves, t0, event_ms, window_full_ms, args.out_dir)

    checks = sanity_checks(rows, items, args, args.data_dir)
    import matplotlib
    run_meta = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "params": {k: relparam(v) for k, v in vars(args).items()},
        "versions": {"python": sys.version.split()[0], "zstandard": zstd.__version__,
                     "matplotlib": matplotlib.__version__},
        "corpus": {
            "items": len(items), "measured": len(rows),
            "first_ms": t0, "last_ms": items[-1]["created_at"],
            "manifest_sha256": hashlib.sha256(
                (args.data_dir.parent / "manifest.json").read_bytes()).hexdigest(),
        },
        "event_marker_ms": event_ms,
        "window_full_ms": window_full_ms,
        "sanity": checks,
    }
    (args.out_dir / "run.json").write_text(json.dumps(run_meta, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    print(f"done -> {args.out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
