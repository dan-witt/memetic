#!/usr/bin/env python3
"""Build a forum corpus from a phpBB board, shaped into the same thread-JSON schema
so the existing novelty/perplexity pipelines run on it unchanged (--data-dir).
Intended as a human-forum reference corpus for the diversity measurement. Text is
taken AS POSTED (inline quotes included, matching how the agent corpus is stored).
Polite by design: 1 req/sec, a descriptive User-Agent (set SCRAPER_UA), public
content, read-only."""
import calendar, json, os, sys, time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

# Usage: pull_phpbb.py <phpbb-base-url> <out-dir> <target-items> <board-ids,csv>
#   e.g. pull_phpbb.py https://host/path/phpBB3/ out 3000 5,29,13
# Be polite: set SCRAPER_UA to a User-Agent naming your project and a contact address.
if len(sys.argv) < 5:
    sys.exit("usage: pull_phpbb.py <base-url> <out-dir> <target-items> <board-ids,csv>")
BASE = sys.argv[1].rstrip("/") + "/"
UA = os.environ.get("SCRAPER_UA", "phpbb-diversity-sampler (set SCRAPER_UA with your contact)")
FORUMS = [int(x) for x in sys.argv[4].split(",")]   # board f= ids to sample
OUT = Path(sys.argv[2]); (OUT / "posts").mkdir(parents=True, exist_ok=True)
TARGET = int(sys.argv[3])


def fetch(url):
    for _ in range(3):
        try:
            time.sleep(1.0)                       # be polite to a small hobbyist server
            with urlopen(Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print("  retry", e, file=sys.stderr); time.sleep(3)
    return ""


def tid(href):
    for part in href.split("&"):
        for kv in part.split("?"):
            if kv.startswith("t="): return kv[2:]
    return href.split("t=")[1].split("&")[0] if "t=" in href else None


def topics_in(f):
    # step by phpBB's viewforum page size (25); sticky rows repeat per page and would
    # drift a len()-based step, so use a fixed step + break after 2 dry pages.
    ids, start, dry = [], 0, 0
    while dry < 2 and start <= 2000:
        s = BeautifulSoup(fetch(f"{BASE}viewforum.php?f={f}&start={start}"), "html.parser")
        hrefs = [a["href"] for a in s.select("a.topictitle")]
        before = len(ids)
        for h in hrefs:
            t = tid(h)
            if t and t not in ids: ids.append(t)
        dry = dry + 1 if len(ids) == before else 0
        if not hrefs: break
        start += 25
    return ids


def parse_posts(soup):
    out = []
    for pd in soup.select("div.post"):
        auth = pd.select_one("p.author")
        content = pd.select_one("div.content")
        if not auth or not content: continue
        line = auth.get_text(" ", strip=True)          # "Unread post by USER » Sat Sep 07, 2024 11:18 pm"
        if " by " not in line or "»" not in line: continue
        who = line.split(" by ", 1)[1].split("»")[0].strip()
        when = line.split("»", 1)[1].strip()
        # keep quotes: measure text AS POSTED, matching how 1f916 items are stored
        # (their inline quoting is included too). Fair, apples-to-apples comparison.
        body = content.get_text("\n", strip=True)
        if not body: continue
        try:
            dt = datetime.strptime(when.replace(" pm", " PM").replace(" am", " AM"), "%a %b %d, %Y %I:%M %p")
            ts = calendar.timegm(dt.timetuple()) * 1000
        except ValueError:
            ts = 0
        out.append({"author": who, "created_at": ts, "body": body})
    return out


def topic(t):
    posts, seen, start, title = [], set(), 0, ""
    while True:
        s = BeautifulSoup(fetch(f"{BASE}viewtopic.php?t={t}&start={start}"), "html.parser")
        if not title and s.select_one("h2"): title = s.select_one("h2").get_text(strip=True)
        page = parse_posts(s)
        new = 0
        for p in page:
            sig = (p["author"], p["created_at"], p["body"][:60])
            if sig not in seen:
                seen.add(sig); posts.append(p); new += 1
        if not page or new == 0: break            # clamped/last page repeats -> done
        start += len(page)
        if start > 400: break
    return title, posts


def main():
    total = 0
    for f in FORUMS:
        if total >= TARGET: break
        tids = topics_in(f)
        print(f"forum {f}: {len(tids)} topics", file=sys.stderr)
        for t in tids:
            if total >= TARGET: break
            title, posts = topic(t)
            if not posts: continue
            posts.sort(key=lambda p: p["created_at"])
            head = posts[0]
            thread = {"post": {"id": int(t), "title": title, "body": head["body"],
                               "created_at": head["created_at"], "author": head["author"],
                               "author_model": "human", "votes": 0},
                      "comments": [{"id": int(t) * 1000 + k, "parent_id": None, "body": p["body"],
                                    "created_at": p["created_at"], "author": p["author"],
                                    "author_model": "human", "votes": 0}
                                   for k, p in enumerate(posts[1:], 1)]}
            (OUT / "posts" / f"{t}.json").write_text(json.dumps(thread))
            total += len(posts)
            if total % 200 < len(posts): print(f"  {total} items ...", file=sys.stderr)
    (OUT / "manifest.json").write_text(json.dumps({
        "source": BASE, "pulled_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items_total": total, "note": "phpBB forum corpus (human-forum diversity reference)"}, indent=2))
    print(f"done: {total} items", file=sys.stderr)


if __name__ == "__main__":
    main()
