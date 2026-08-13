#!/usr/bin/env python3
"""Pull every post + comments from 1f916.ai into a data directory.

1. Walk /api/changes?since=0 following next_since while has_more to
   enumerate every post id ever created (the site says this is the only
   complete read of the archive).
2. Fetch /api/post/:id for each and save the raw JSON response
   (post + all comments: ids, titles, bodies, timestamps) to
   data/posts/<id>.json.
3. Write data/manifest.json recording what was fetched and anything missing.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://1f916.ai"
DATA = Path("/home/dan/personal/memetic/data")
POSTS = DATA / "posts"
POSTS.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "1f916-archiver/1.0 (read-only corpus pull)"}


def get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


# --- 1. enumerate post ids via the changes feed ---
post_ids = set()
comment_count = 0
since = 0
pages = 0
while True:
    status, body = get(f"{BASE}/api/changes?since={since}")
    if status != 200:
        raise SystemExit(f"changes feed returned {status} at since={since}")
    page = json.loads(body)
    pages += 1
    for p in page.get("posts", []):
        post_ids.add(p["id"])
    comment_count += len(page.get("comments", []))
    if not page.get("has_more"):
        break
    since = page["next_since"]
    time.sleep(0.15)

print(f"changes feed: {pages} pages, {len(post_ids)} posts, "
      f"{comment_count} comments referenced")

# --- 2. fetch each thread ---
fetched, missing, errors = [], [], []
for i, pid in enumerate(sorted(post_ids), 1):
    status, body = get(f"{BASE}/api/post/{pid}")
    if status == 200:
        (POSTS / f"{pid}.json").write_bytes(body)
        fetched.append(pid)
    elif status == 404:
        missing.append(pid)
    else:
        errors.append({"id": pid, "status": status})
    if i % 50 == 0:
        print(f"  {i}/{len(post_ids)} threads fetched")
    time.sleep(0.15)

# --- 3. probe for any ids the changes feed skipped (deleted posts etc.) ---
max_id = max(post_ids)
gaps = sorted(set(range(1, max_id + 1)) - post_ids)
gap_found = []
for pid in gaps:
    status, body = get(f"{BASE}/api/post/{pid}")
    if status == 200:
        (POSTS / f"{pid}.json").write_bytes(body)
        gap_found.append(pid)
        fetched.append(pid)
    time.sleep(0.15)

manifest = {
    "source": BASE,
    "pulled_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "endpoint": "/api/post/:id (raw responses in posts/<id>.json)",
    "post_ids_from_changes_feed": len(post_ids),
    "threads_saved": len(fetched),
    "max_post_id": max_id,
    "ids_in_feed_but_404": missing,
    "ids_absent_from_feed": gaps,
    "ids_absent_from_feed_but_fetchable": gap_found,
    "errors": errors,
}
(DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v for k, v in manifest.items() if k != "errors"}, indent=2))
print(f"errors: {errors}")
