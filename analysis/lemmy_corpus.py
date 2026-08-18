#!/usr/bin/env python3
"""Build the lemmy.world founding-window corpus into the canonical anchor record shape, so
every existing instrument consumes it unmodified.

Source: analysis/lemmy_crawl.py output (posts.jsonl + comments.jsonl) — the 57 local
communities that existed before the reddit exodus arrived on 2023-06-09, all content
published 2023-06-01 .. 2023-06-30.

Records match usenet_corpus_langs.py exactly: group / author / ts / msgid / root / subject /
text / crosspost, with `root == msgid` marking a thread root (claimify prepends the subject
for roots only). Extra fields (kind, community, featured, local, tier) are additive and
ignored by the existing scripts, but let us subset labels per-tier after a single GPU pass
instead of running the pipeline twice.

Quote stripping uses markdown-it (a real CommonMark parser) to locate blockquote blocks by
source line range and drop them — the markdown analogue of strip_body() on the Usenet side.

Output: baseline_corpora_lemmy.json  {"lemmy": [...]} + baseline_corpora_lemmy_summary.json
"""
import json, os, datetime as dt
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from markdown_it import MarkdownIt

S = Path(os.environ.get("MEMETIC_WORKDIR", "."))
LW = S / "lemmy"
T0 = dt.datetime(2023, 6, 1, 7, 1, 46, tzinfo=dt.timezone.utc)

# Communities whose remit IS the venue: announcing/discussing the platform and its
# communities. These cannot sit in the anchor -- a high venue share there prices remit,
# not founding. Kept in the corpus and tagged so they can serve as the upper bracket.
META = {"newcommunities", "lemmyworld", "fediverse", "mastodon", "lemmy_support",
        "lemmyworldsupport", "meta"}

md = MarkdownIt("commonmark")


def strip_quotes(text):
    """Drop blockquote blocks, located by the parser's source-line map."""
    if not text:
        return ""
    lines = text.split("\n")
    drop = set()
    for t in md.parse(text):
        if t.type == "blockquote_open" and t.map:
            drop.update(range(t.map[0], t.map[1]))
    return "\n".join(l for i, l in enumerate(lines) if i not in drop).strip()


def epoch(s):
    s = s.replace("Z", "+00:00")
    if "+" not in s[10:] and "-" not in s[10:]:
        s += "+00:00"
    return int(dt.datetime.fromisoformat(s).timestamp())


def load(name):
    p = LW / name
    return [json.loads(l) for l in p.open()] if p.exists() else []


posts, comments = load("posts.jsonl"), load("comments.jsonl")
post_ap = {p["id"]: (p.get("ap_id") or f"lwpost:{p['id']}") for p in posts}
post_title = {p["id"]: (p.get("title") or "") for p in posts}
print(f"raw: {len(posts)} posts, {len(comments)} comments")

recs = []
for p in posts:
    mid = p.get("ap_id") or f"lwpost:{p['id']}"
    recs.append(dict(group=p["community"], author=p["author_hash"], ts=epoch(p["published"]),
                     msgid=mid, root=mid, subject=(p.get("title") or ""),
                     text=strip_quotes(p.get("body") or ""), crosspost=False,
                     kind="post", community=p["community"],
                     featured=bool(p.get("featured")), local=bool(p.get("local")),
                     tier="meta" if p["community"] in META else "topic"))
for c in comments:
    mid = c.get("ap_id") or f"lwcomment:{c['id']}"
    root = post_ap.get(c.get("post_id"), f"lwpost:{c.get('post_id')}")
    recs.append(dict(group=c["community"], author=c["author_hash"], ts=epoch(c["published"]),
                     msgid=mid, root=root, subject="",
                     text=strip_quotes(c.get("content") or ""), crosspost=False,
                     kind="comment", community=c["community"],
                     featured=False, local=bool(c.get("local")),
                     tier="meta" if c["community"] in META else "topic"))
recs.sort(key=lambda r: r["ts"])

# ---------- characterization (identical statistics to usenet_corpus_langs.py) ----------
def gini(x):
    x = np.sort(np.array(x, float)); n = len(x)
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def day(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d")


def describe(name, arts):
    if not arts:
        print(f"\n=== {name}: empty ==="); return {}
    ev = defaultdict(list)
    for r in arts:
        ev[r["author"]].append(r["ts"])
    counts = [len(v) for v in ev.values()]
    ten = [(max(v) - min(v)) / 86400 for v in ev.values()]
    blens = [len(r["text"]) for r in arts]
    th = Counter(r["root"] for r in arts)
    tot = len(arts)
    lo, hi = arts[0]["ts"], arts[-1]["ts"]
    keep = sum(b >= 20 for b in blens)
    print(f"\n=== {name}: {tot} items, {len(ev)} authors, "
          f"{day(lo)}..{day(hi)} ===")
    print(f"  posts {sum(1 for r in arts if r['kind']=='post')}, "
          f"comments {sum(1 for r in arts if r['kind']=='comment')}; "
          f"communities {len({r['group'] for r in arts})}")
    print(f"  body chars: median {int(np.median(blens))}, mean {int(np.mean(blens))}; "
          f">=20ch: {keep}/{tot} ({100*keep/tot:.0f}%)")
    print(f"  threads: {len(th)}; median len {int(np.median(list(th.values())))}; "
          f"% items in threads>=2: {100*sum(n for n in th.values() if n>1)/tot:.0f}%")
    print(f"  Gini {gini(counts):.2f}; top-5 authors {100*sum(sorted(counts,reverse=True)[:5])/tot:.0f}%; "
          f"drive-by(<1d) {100*np.mean([t<1 for t in ten]):.0f}%; "
          f"deep(>14d) {100*np.mean([t>14 for t in ten]):.0f}% of authors")
    print(f"  local-authored: {100*np.mean([r['local'] for r in arts]):.0f}%")
    return dict(n=tot, n_authors=len(ev), span=[int(lo), int(hi)],
                n_posts=sum(1 for r in arts if r["kind"] == "post"),
                n_comments=sum(1 for r in arts if r["kind"] == "comment"),
                communities=len({r["group"] for r in arts}),
                median_chars=int(np.median(blens)), keep_ge20=int(keep),
                gini=round(gini(counts), 3),
                threads=len(th),
                pct_local=round(100 * float(np.mean([r["local"] for r in arts])), 1))


summary = {}
summary["all"] = describe("lemmy ALL", recs)
summary["topic"] = describe("lemmy TOPIC tier (anchor candidate)",
                            [r for r in recs if r["tier"] == "topic"])
summary["meta"] = describe("lemmy META tier (remit-is-venue bracket)",
                           [r for r in recs if r["tier"] == "meta"])

A0 = dt.datetime(2023, 6, 9, 0, 0, tzinfo=dt.timezone.utc).timestamp()
A1 = A0 + 8.2 * 86400
summary["arrival_window"] = describe("lemmy ARRIVAL WINDOW 06-09 +8.2d (square-matched)",
                                     [r for r in recs if A0 <= r["ts"] < A1])
summary["arrival_window_topic"] = describe("lemmy ARRIVAL WINDOW, topic tier only",
                                           [r for r in recs
                                            if A0 <= r["ts"] < A1 and r["tier"] == "topic"])

percom = Counter(r["group"] for r in recs)
summary["per_community"] = dict(percom)
print("\n top 15 communities by items: " +
      ", ".join(f"{c}={n}" for c, n in percom.most_common(15)))
perday = Counter(day(r["ts"]) for r in recs)
print("\n items/day: " + " ".join(f"{k[5:]}:{v}" for k, v in sorted(perday.items())))
summary["per_day"] = dict(sorted(perday.items()))

json.dump({"lemmy": recs}, open(S / "baseline_corpora_lemmy.json", "w"))
json.dump(summary, open(S / "baseline_corpora_lemmy_summary.json", "w"), indent=1)
print(f"\nsaved baseline_corpora_lemmy.json ({len(recs)} records) + summary")
