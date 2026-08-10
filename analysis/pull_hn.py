#!/usr/bin/env python3
"""Build a HUMAN-forum control corpus (Hacker News) matched in item count to the
1f916.ai corpus, shaped into the same thread-JSON schema so zstd_curve.py /
perplexity.py / perplexity_stream.py run on it unchanged (--data-dir).

Each HN story -> a "post"; its comment subtree (flattened, time-sorted) -> comments.
HTML is stripped with a real parser (stdlib html.parser), not a regex. author_model
is set to 'human'. Fetches concurrently from the public Firebase API (no auth)."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.request import urlopen

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "hn"); (OUT / "posts").mkdir(parents=True, exist_ok=True)
TARGET = int(sys.argv[2]) if len(sys.argv) > 2 else 2890
PER_STORY_CAP = 30          # cap comments per story so no mega-thread dominates
API = "https://hacker-news.firebaseio.com/v0"


class Strip(HTMLParser):
    def __init__(self): super().__init__(); self.buf = []
    def handle_data(self, d): self.buf.append(d)
    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br"): self.buf.append("\n\n")
    def text(self): return "".join(self.buf).strip()


def strip_html(h):
    if not h: return ""
    s = Strip(); s.feed(unescape(h)); return s.text()


def get(item_id):
    for _ in range(3):
        try:
            with urlopen(f"{API}/item/{item_id}.json", timeout=20) as r:
                return json.load(r)
        except Exception:
            time.sleep(0.5)
    return None


def main():
    story_ids, seen = [], set()
    for feed in ("topstories", "beststories", "newstories"):
        with urlopen(f"{API}/{feed}.json", timeout=20) as r:
            for s in json.load(r):
                if s not in seen:
                    seen.add(s); story_ids.append(s)
    print(f"{len(story_ids)} candidate stories; target {TARGET} items", file=sys.stderr)
    items_total = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        for sid in story_ids:
            if items_total >= TARGET:
                break
            story = get(sid)
            if not story or story.get("type") != "story" or not story.get("kids"):
                continue
            # BFS the comment tree, capped
            comments, frontier = [], list(story["kids"])
            while frontier and len(comments) < PER_STORY_CAP:
                batch = frontier[:PER_STORY_CAP - len(comments)]; frontier = frontier[len(batch):]
                for c in ex.map(get, batch):
                    if not c or c.get("type") != "comment" or c.get("dead") or c.get("deleted"):
                        continue
                    body = strip_html(c.get("text"))
                    if not body:
                        continue
                    comments.append({"id": c["id"], "parent_id": c.get("parent"),
                                     "body": body, "created_at": c.get("time", 0) * 1000,
                                     "author": c.get("by", "unknown"), "author_model": "human",
                                     "votes": 0})
                    frontier += c.get("kids", []) or []
            if not comments:
                continue
            comments.sort(key=lambda x: x["created_at"])
            thread = {"post": {"id": story["id"], "title": story.get("title") or "",
                               "body": strip_html(story.get("text")) or (story.get("url") or ""),
                               "created_at": story.get("time", 0) * 1000,
                               "author": story.get("by", "unknown"), "author_model": "human",
                               "votes": story.get("score", 0)},
                      "comments": comments}
            (OUT / "posts" / f"{story['id']}.json").write_text(json.dumps(thread))
            items_total += 1 + len(comments)
            if items_total % 200 < (1 + len(comments)):
                print(f"  {items_total} items ...", file=sys.stderr)
    (OUT / "manifest.json").write_text(json.dumps({
        "source": "Hacker News Firebase API /v0", "pulled_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items_total": items_total, "note": "human-forum control, size-matched to 1f916.ai"}, indent=2))
    print(f"done: {items_total} items across {len(list((OUT/'posts').glob('*.json')))} stories", file=sys.stderr)


if __name__ == "__main__":
    main()
