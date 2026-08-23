#!/usr/bin/env python3
"""Fetch 1f916.ai into the observation store, letting the DATABASE decide what to refresh.

THE OLD FETCHER re-read every thread every run -- ~1,800 requests whether or not anything moved.
The site's front door names that as the wrong method:

    "Catch up via /api/changes with If-None-Match, not by re-reading pages; that path never
     comes near the limit."
    "Rate limit: 120 requests per minute per IP on /api/*, enforced at the edge as 20 per 10
     seconds; over it you get 429 for 10 seconds. Set 2026-08-23 after two anonymous pollers
     made 67% of all traffic."

WHAT DRIVES THE REFRESH. Two sources, in priority order:

  1. THE CHANGES FEED, from the cursor stored in the last run. Authoritative for what moved.
  2. THE DATABASE, for what the feed cannot tell us -- a silent edit to an old comment. Threads
     are scored by staleness RELATIVE TO ACTIVITY (corpus_store.stale_threads): a thread active an
     hour ago and unfetched for two outranks one dormant for a week. Attention decays as a thread
     goes quiet, instead of every thread costing the same request every run.

WHY THAT SECOND SOURCE MATTERS. The weather series' content-mutation audit certifies "N items
edited since the last issue". Under pure feed-driven fetching that number is only as good as the
feed's willingness to report edits, and a silent zero is indistinguishable from a clean one. The
staleness sweep plus the coverage figure in every run record turn that into a stated property:
this run verified X% of items within the last 24h, so the audit covers X% and no more. Coverage
replaces an assumption with a number.

BUDGET. --budget caps requests per run so a pass is bounded and predictable; at the default 400
and 0.5 s pacing a run takes ~3.5 minutes and sits at a third of the published limit. Partial runs
are recorded as partial rather than reported as success -- the failure mode that left a
mixed-vintage corpus on 2026-08-23 with nothing in the data to show it.

Usage:
  python3 analysis/corpus_fetch.py                     # catch up + staleness sweep, budget 400
  python3 analysis/corpus_fetch.py --budget 2000       # a bigger sweep
  python3 analysis/corpus_fetch.py --full              # rebuild: every thread, ignores the cursor
  python3 analysis/corpus_fetch.py --dry-run           # show what it WOULD fetch, no requests
"""
import argparse, json, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

BASE = "https://1f916.ai"
UA = {"User-Agent": "1f916-archiver/1.0 (read-only corpus pull)"}
SLEEP = 0.5          # the published sustained limit: 120/min
RETRY_429 = 11.0     # the edge blocks for 10 s; wait it out rather than dropping the thread
STATE = CS.DATA / "fetch_state.json"


def get(url, etag=None, retries=3):
    """-> (status, body, headers). 304 when If-None-Match matches: the cheapest poll available."""
    for attempt in range(retries):
        try:
            h = dict(UA)
            if etag:
                h["If-None-Match"] = etag
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return 304, b"", dict(e.headers)
            if e.code == 429 and attempt < retries - 1:
                time.sleep(RETRY_429)
                continue
            return e.code, e.read(), dict(e.headers)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def changed_since(cursor, etags, budget, log=print):
    """Walk /api/changes from the cursor with If-None-Match. -> (post_ids, cursor, etags, spent)."""
    ids, spent, pages = set(), 0, 0
    since = cursor
    while spent < budget:
        et = etags.get(str(since))
        status, body, hdr = get(f"{BASE}/api/changes?since={since}", etag=et)
        spent += 1
        if status == 304:
            log(f"  changes since={since}: 304 not modified")
            break
        if status != 200:
            log(f"  changes since={since}: HTTP {status} -- stopping the walk")
            break
        if hdr.get("ETag"):
            etags[str(since)] = hdr["ETag"]
        page = json.loads(body)
        pages += 1
        for p in page.get("posts", []):
            ids.add(p["id"])
        for c in page.get("comments", []):
            if c.get("post_id"):
                ids.add(c["post_id"])
        nxt = page.get("next_since", since)
        if not page.get("has_more"):
            since = nxt
            break
        since = nxt
        time.sleep(SLEEP)
    log(f"  changes feed: {pages} page(s), {len(ids)} threads moved, cursor -> {since}")
    return ids, since, {k: v for k, v in etags.items() if k == str(since)}, spent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=400, help="max requests this run")
    ap.add_argument("--full", action="store_true", help="rebuild: fetch every known thread")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fresh-hours", type=float, default=24.0)
    args = ap.parse_args()

    started = time.time()
    run_id = f"fetch:{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))}"
    state = load_state()
    con = CS.build_index()
    spent = 0

    if args.full:
        cursor, etags = 0, {}
        targets, cursor, etags, used = changed_since(0, {}, args.budget) if not args.dry_run else \
            (set(int(p.stem) for p in CS.POSTS.glob("*.json")), 0, {}, 0)
        spent += used
        targets = set(int(p.stem) for p in CS.POSTS.glob("*.json")) | targets
        print(f"full rebuild: {len(targets)} threads")
    else:
        cursor = state.get("cursor", 0)
        etags = dict(state.get("etags") or {})
        if not cursor:
            sys.exit("no cursor yet: run once with --full, or seed data/fetch_state.json")
        print(f"catch-up from cursor {cursor}")
        targets, cursor, etags, used = changed_since(cursor, etags, args.budget) \
            if not args.dry_run else (set(), cursor, etags, 0)
        spent += used
        room = max(0, args.budget - spent - len(targets))
        sweep = CS.stale_threads(con, limit=room)
        print(f"  staleness sweep: {len(sweep)} thread(s) within budget"
              + (f", top score {sweep[0]['score']} (stale {sweep[0]['stale_hours']}h / "
                 f"idle {sweep[0]['idle_hours']}h)" if sweep else ""))
        targets = list(targets) + [s["post_id"] for s in sweep if s["post_id"] not in targets]

    targets = sorted(set(targets))
    if args.dry_run:
        print(f"[dry run] would fetch {len(targets)} threads, ~{spent + len(targets)} requests, "
              f"~{(spent + len(targets)) * SLEEP / 60:.1f} min")
        print("coverage now:", CS.coverage(con, fresh_hours=args.fresh_hours))
        sys.exit(0)

    ok = e404 = e429 = 0
    fetched_at = {}
    for i, pid in enumerate(targets, 1):
        if spent >= args.budget:
            print(f"  budget reached at {i-1}/{len(targets)} threads"); break
        status, body, _ = get(f"{BASE}/api/post/{pid}")
        spent += 1
        if status == 200:
            (CS.POSTS / f"{pid}.json").write_bytes(body); ok += 1
            fetched_at[pid] = time.time()
        elif status == 404:
            e404 += 1
        elif status == 429:
            e429 += 1
        if i % 50 == 0:
            print(f"  {i}/{len(targets)} threads ({ok} ok, {e404} 404, {e429} 429)")
        time.sleep(SLEEP)

    items, _ = CS.scan_tree()
    known = {r["item_key"]: r["content_sha"] for r in CS.load_log()}
    new, edits = CS.append_snapshot(items, time.time(), run_id, known=known)
    complete = (e429 == 0 and spent < args.budget)
    CS.append_run({"run_id": run_id, "started_at": started, "ended_at": time.time(),
                   "mode": "full" if args.full else "catchup",
                   "cursor_before": state.get("cursor", 0), "cursor_after": cursor,
                   "threads_attempted": len(targets), "threads_ok": ok,
                   "threads_404": e404, "threads_429": e429, "complete": int(complete),
                   "note": f"{new} new item-versions, {edits} edits, {spent} requests"})
    STATE.write_text(json.dumps({"cursor": cursor, "etags": etags,
                                 "threads_on_disk": len(list(CS.POSTS.glob("*.json"))),
                                 "last_run": run_id}, indent=1) + "\n")
    con = CS.build_index()
    print(f"\n{ok} threads fetched, {new} new item-versions, {edits} edits, {spent} requests"
          f"{'' if complete else '  [PARTIAL -- recorded as incomplete]'}")
    print("coverage:", CS.coverage(con, fresh_hours=args.fresh_hours))
