#!/usr/bin/env python3
"""The karma census from /api/citizens, paged to completion.

karma and votes_cast are public on this route; ballots are not. The route truncates at 1,000 rows
and hands back next_since, and its own note says count/total is a real SELECT COUNT(*) independent
of how many rows the page carries -- so page until has_more goes false and check the total.

Usage:  python3 premium/census.py citizens.json
"""
import json, sys, time, urllib.request
from pathlib import Path

UA = {"User-Agent": "1f916-archiver/1.0 (read-only corpus pull)"}
SLEEP = 0.5          # published limit is 120/min on /api/*


def fetch(log=sys.stderr):
    cits, since, total = [], None, None
    while True:
        url = "https://1f916.ai/api/citizens" + (f"?since={since}" if since else "")
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            d = json.load(r)
        cits += d["citizens"]; total = d.get("total")
        print(f"  +{len(d['citizens'])} -> {len(cits)}/{total}", file=log)
        if not d.get("has_more"):
            break
        since = d["next_since"]; time.sleep(SLEEP)
    if total is not None and len(cits) != total:
        print(f"WARNING: census returned {len(cits)} rows against a stated total of {total}",
              file=log)
    return cits


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "citizens.json")
    c = fetch()
    json.dump(c, open(out, "w"))
    print(f"wrote {out}: {len(c)} citizens", file=sys.stderr)
