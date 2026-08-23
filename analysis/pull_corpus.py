#!/usr/bin/env python3
"""Pull posts + comments from 1f916.ai into a data directory.

TWO MODES.

--full (default for now): walk /api/changes?since=0 to enumerate every post id ever created, then
fetch /api/post/:id for ALL of them. This re-reads ~1,800 threads whether or not they changed.

--incremental: the method the site's front door prescribes --

    "Catch up via /api/changes with If-None-Match, not by re-reading pages; that path never
     comes near the limit."
    "KEEP THE ETag AND SEND IT BACK as If-None-Match: an unchanged page answers 304 with no
     body, which is the cheapest poll available here. Cache-Control is no-store, so no HTTP
     cache will revalidate on your behalf; hold the tag in your own client."

Resume from the stored cursor, revalidate with If-None-Match, and fetch only the threads the feed
says moved. A day's delta is a few hundred requests instead of ~1,800.

WHY THIS MATTERS BEYOND POLITENESS: on 2026-08-23 the site set a cap -- "120 requests per minute
per IP on /api/*, enforced at the edge as 20 per 10 seconds ... after two anonymous pollers made
67% of all traffic" -- and a full pull at the old 0.15 s pacing ran ~400/min, 3.3x over it. That
pull came back with 674 of 1,801 threads, silently leaving the corpus mixed-vintage, because a 429
was treated as a permanent per-thread failure.

BEFORE MAKING --incremental THE DEFAULT, validate it against a full pull: the weather series'
feed_lag block detects backfilled items and post-publication EDITS by diffing the previous corpus
against the current one, and that audit is only sound if the changes feed reports comment edits.
Verify that, do not assume it.

Writes data/manifest.json recording what was fetched, what is missing, and the changes cursor.
"""
import argparse
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


# 1f916 publishes its limit on the front page: "120 requests per minute per IP on /api/*,
# enforced at the edge as 20 per 10 seconds; over it you get 429 for 10 seconds." That is one
# request per 0.5 s sustained. This script used to sleep 0.15 s (~400/min, 3.3x over) and treated
# a 429 as a permanent failure, silently skipping the thread -- which is how a pull on 2026-08-23
# came back with 674 of 1801 threads and left the corpus mixed-vintage. Both are fixed here.
SLEEP = 0.5          # seconds between requests; the published sustained limit
RETRY_429 = 11.0     # the edge blocks for 10 s; wait it out rather than dropping the thread


def get(url, retries=3, etag=None):
    """-> (status, body, headers). Send If-None-Match when an etag is held; 304 means unchanged."""
    for attempt in range(retries):
        try:
            hdrs = dict(UA)
            if etag:
                hdrs["If-None-Match"] = etag
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return 304, b"", dict(e.headers)
            if e.code == 429 and attempt < retries - 1:
                time.sleep(RETRY_429)
                continue
            return e.code, e.read(), dict(e.headers)
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--incremental", action="store_true",
                help="resume from the stored changes cursor with If-None-Match and fetch only "
                     "threads the feed reports as moved (the method the site prescribes)")
ap.add_argument("--full", action="store_true",
                help="walk from since=0 and re-fetch every thread (rebuild; the default for now)")
args = ap.parse_args()
INCREMENTAL = args.incremental and not args.full

prior = {}
if (DATA / "manifest.json").exists():
    prior = json.loads((DATA / "manifest.json").read_text())
etags = dict(prior.get("changes_etags") or {})

# --- 1. enumerate post ids via the changes feed ---
post_ids = set()
comment_count = 0
since = prior.get("changes_cursor", 0) if INCREMENTAL else 0
start_since = since
pages = 0
not_modified = False
if INCREMENTAL and not prior.get("changes_cursor"):
    raise SystemExit("--incremental needs a changes_cursor in data/manifest.json; run --full once")
while True:
    et = etags.get(str(since))
    status, body, hdr = get(f"{BASE}/api/changes?since={since}", etag=et)
    if status == 304:                       # the cheapest poll available: nothing moved
        not_modified = True
        break
    if status != 200:
        raise SystemExit(f"changes feed returned {status} at since={since}")
    if hdr.get("ETag"):
        etags[str(since)] = hdr["ETag"]
    page = json.loads(body)
    pages += 1
    for p in page.get("posts", []):
        post_ids.add(p["id"])
    comment_count += len(page.get("comments", []))
    if not page.get("has_more"):
        since = page.get("next_since", since)
        break
    since = page["next_since"]
    time.sleep(SLEEP)
# keep the map small: only cursors we might revalidate against
etags = {k: v for k, v in etags.items() if k in (str(start_since), str(since))}
cursor = since

print(f"changes feed ({'incremental from ' + str(start_since) if INCREMENTAL else 'full from 0'}): "
      f"{pages} pages, {len(post_ids)} posts, {comment_count} comments referenced"
      + (" [304 not modified]" if not_modified else ""))

# --- 2. fetch each thread ---
fetched, missing, errors = [], [], []
for i, pid in enumerate(sorted(post_ids), 1):
    status, body, _hdr = get(f"{BASE}/api/post/{pid}")
    if status == 200:
        (POSTS / f"{pid}.json").write_bytes(body)
        fetched.append(pid)
    elif status == 404:
        missing.append(pid)
    else:
        errors.append({"id": pid, "status": status})
    if i % 50 == 0:
        print(f"  {i}/{len(post_ids)} threads fetched")
    time.sleep(SLEEP)

# --- 3. probe for any ids the changes feed skipped (deleted posts etc.) ---
# Full mode only: this walks every id below max_id, which is exactly the re-reading the cap
# was set against. An incremental run inherits the previous full run's answer.
max_id = max(post_ids) if post_ids else prior.get("max_post_id", 0)
gaps = sorted(set(range(1, max_id + 1)) - post_ids) if not INCREMENTAL else []
gap_found = []
for pid in gaps:
    status, body, _hdr = get(f"{BASE}/api/post/{pid}")
    if status == 200:
        (POSTS / f"{pid}.json").write_bytes(body)
        gap_found.append(pid)
        fetched.append(pid)
    time.sleep(SLEEP)

manifest = {
    "source": BASE,
    "pulled_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "endpoint": "/api/post/:id (raw responses in posts/<id>.json)",
    "mode": "incremental" if INCREMENTAL else "full",
    "post_ids_from_changes_feed": len(post_ids),
    "threads_fetched_this_run": len(fetched),
    # threads_saved used to be the only count here, and on a partial run it read as though the
    # corpus itself were that size. Record what is actually on disk so the manifest cannot
    # misrepresent the corpus again.
    "threads_on_disk": len(list(POSTS.glob("*.json"))),
    "complete": not errors,
    "max_post_id": max_id,
    "changes_cursor": cursor,
    "changes_etags": etags,
    "changes_not_modified": not_modified,
    "ids_in_feed_but_404": missing,
    "ids_absent_from_feed": gaps if not INCREMENTAL else prior.get("ids_absent_from_feed", []),
    "ids_absent_from_feed_but_fetchable": (gap_found if not INCREMENTAL
                                           else prior.get("ids_absent_from_feed_but_fetchable", [])),
    "errors": errors,
}
(DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({k: v for k, v in manifest.items() if k != "errors"}, indent=2))
print(f"errors: {errors}")
