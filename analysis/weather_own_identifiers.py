#!/usr/bin/env python3
"""Snapshot the square's own record of what it operates, for the exact-match marker set.

`weather_venue_gold.py` anchors "the square's own X" to `data/1f916_own_identifiers.json`, a dated
snapshot of two live endpoints. The snapshot was built by hand at issue #18. It is a live record --
the square ships code and adds routes -- so an issue that reads it is reading the record as of its
snapshot date, and refreshing it is an instrument change that has to be visible.

This writes the snapshot and, with --diff, says what moved since the file on disk without writing.
Both endpoints are self-describing: /api/official carries operated_properties ("This list is
COMPLETE"), the official token and the treasury; /api/surface carries every route served.

Usage:
  python3 analysis/weather_own_identifiers.py --diff      # what changed, write nothing
  python3 analysis/weather_own_identifiers.py [-o PATH]   # write the snapshot
"""
import json, sys, urllib.request
from pathlib import Path

R = Path(__file__).resolve().parent.parent
SNAP = R / "data/1f916_own_identifiers.json"
BASE = "https://1f916.ai"


def _get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "memetic-weather/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def snapshot():
    o, s = _get("/api/official"), _get("/api/surface")
    op = o["operated_properties"]
    paths = sorted({r["path"] for r in s["routes"]})
    return {
        "source": ["GET %s/api/official" % BASE, "GET %s/api/surface" % BASE],
        "fetched_at_utc": o["now_utc"],
        "why": "The square publishes a canonical, self-declared record of what it operates. "
               "Anchoring an exact-match marker set to it makes 'the square's own X' a fact about "
               "the platform's own statement rather than about anyone's judgement, and the record "
               "says so explicitly: official_token.this_field_wins and operated_properties.meaning "
               "both assert completeness.",
        "operated_sites": op["sites"],
        "operated_repos": op["repos"],
        "operated_x_account": op["x_account"],
        "operated_subreddit": op["subreddit"],
        "operated_properties_meaning": op["meaning"],
        "official_token_contract": o["official_token"]["contract"],
        "official_token_recognized_at": o["official_token"]["recognized_at"],
        "official_token_this_field_wins": o["official_token"]["this_field_wins"],
        "treasury_address": o["treasury"]["address"],
        "payout_asset_contract_NOT_OWN": o["payout_asset_v1"]["token_contract"],
        "payout_asset_note": "USDC on Base. The payout rail, an external asset; not a marker of "
                             "the square.",
        "api_routes": [p for p in paths if p.startswith("/api/")],
        "api_route_count": sum(1 for p in paths if p.startswith("/api/")),
        "surface_route_count": s["count"],
    }


def diff(new, old):
    out = {"old_fetched_at_utc": old["fetched_at_utc"], "new_fetched_at_utc": new["fetched_at_utc"]}
    a, b = set(old["api_routes"]), set(new["api_routes"])
    out["api_routes_added"] = sorted(b - a)
    out["api_routes_removed"] = sorted(a - b)
    out["api_route_count"] = [old["api_route_count"], new["api_route_count"]]
    out["surface_route_count"] = [old["surface_route_count"], new["surface_route_count"]]
    for f in ("operated_sites", "operated_repos", "operated_x_account", "operated_subreddit",
              "official_token_contract", "treasury_address"):
        if old.get(f) != new.get(f):
            out.setdefault("changed", {})[f] = [old.get(f), new.get(f)]
    out["identity_fields_unchanged"] = "changed" not in out
    return out


if __name__ == "__main__":
    new = snapshot()
    if "--diff" in sys.argv:
        print(json.dumps(diff(new, json.load(open(SNAP))), indent=1))
        sys.exit(0)
    out = Path(sys.argv[sys.argv.index("-o") + 1]) if "-o" in sys.argv else SNAP
    if out.exists():
        print(json.dumps(diff(new, json.load(open(out))), indent=1))
    json.dump(new, open(out, "w"), indent=1)
    print("saved", out)
