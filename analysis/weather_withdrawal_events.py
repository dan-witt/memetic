#!/usr/bin/env python3
"""The withdrawal log — the second stream that rewrites a published body.

`weather_moderation_events.py` reads `GET /api/events?kind=moderation` and explains every collapse
placeholder in the corpus. It does not explain the other substituted bodies, because a WITHDRAWAL
is not a moderation act: the author retracts their own item, the platform replaces the body with
`[withdrawn by its author -- reason in GET /api/events?kind=withdrawal]`, and the reason goes to a
different kind in the same identity log. Until issue #20 nothing in this pipeline read that kind,
so 22 in-scope items of platform boilerplate sat in the currency with no record attached and three
of the five "edits" the mutation audit has ever found were withdrawals wearing an edit's clothes.

Same shape as the moderation cell: pull the log, attribute each event to an item, and check the
two directions -- every withdrawn item in the corpus should have an event, and every event whose
target is in the corpus should find the item withdrawn.

Usage: MEMETIC_WORKDIR=... WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_withdrawal_events.py
       [--offline]
"""
import datetime as dt, json, os, sys, time, urllib.error, urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

BASE = "https://1f916.ai"
UA = {"User-Agent": "1f916-archiver/1.0 (read-only corpus pull)"}
SLEEP = 0.5
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def get(path, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(11.0)
                continue
            raise
    raise SystemExit(f"gave up on {path}")


def pull(cache):
    out, since, seen = [], None, set()
    while True:
        page = get("/api/events?kind=withdrawal" + (f"&since={since}" if since else ""))
        rows = page.get("events") or []
        fresh = [e for e in rows if e["id"] not in seen]
        seen.update(e["id"] for e in fresh)
        out.extend(fresh)
        nxt = page.get("next_since")
        if not fresh or not nxt or nxt == since:
            break
        since = nxt
        time.sleep(SLEEP)
    out.sort(key=lambda e: e["id"])
    json.dump(out, open(cache, "w"), indent=1)
    return out


def parse_detail(ev):
    """`withdrew comment 19888: <reason>` -> (('comment', 19888), reason).

    The platform writes this prefix; anything else is left unparsed rather than guessed at.
    """
    d = (ev.get("detail") or "").strip()
    if not d.startswith("withdrew "):
        return None, d or None
    head, _, reason = d[len("withdrew "):].partition(":")
    parts = head.split()
    if len(parts) != 2 or parts[0] not in ("post", "comment") or not parts[1].isdigit():
        return None, d
    return (parts[0], int(parts[1])), (reason.strip() or None)


def main():
    S = Path(os.environ.get("MEMETIC_WORKDIR", Path.home() / "personal/memetic-workdir"))
    cache = S / "withdrawal_events.json"
    cutoff_s = os.environ.get("WEATHER_CUTOFF")
    events = json.load(open(cache)) if "--offline" in sys.argv else pull(cache)

    con = CS.build_index()
    cut = dt.datetime(*map(int, cutoff_s.split("-")), tzinfo=dt.timezone.utc).timestamp() \
        if cutoff_s else None
    rows = {r["item_key"]: r for r in CS.items_at(con, cutoff=cut, min_chars=0)}

    # what the platform says is withdrawn right now, from the corpus itself
    withdrawn = set()
    for f in CS.POSTS.glob("*.json"):
        th = json.load(open(f))
        p = th.get("post") or {}
        for kind, o in [("post", p)] + [("comment", c) for c in th.get("comments", [])]:
            if o.get("id") is not None and o.get("mod_state") == "withdrawn":
                withdrawn.add(f"{kind}:{o['id']}")

    by_day, detail, in_scope, unparsed = Counter(), [], 0, 0
    for ev in events:
        ts = ev.get("created_at")
        ts = ts / 1000 if ts and ts > 1e11 else ts
        if cut and ts and ts >= cut:
            continue
        in_scope += 1
        tgt, reason = parse_detail(ev)
        if tgt is None:
            unparsed += 1
        if ts:
            by_day[DAY(ts)] += 1
        key = f"{tgt[0]}:{tgt[1]}" if tgt else None
        row = rows.get(key) if key else None
        detail.append({"event_id": ev.get("id"), "target": key,
                       "in_corpus": row is not None,
                       "is_withdrawn_now": key in withdrawn if key else None,
                       "event_day": DAY(ts) if ts else None,
                       "item_day": DAY(row["created_at"]) if row and row.get("created_at") else None,
                       "citizen": ev.get("citizen"), "reason": reason})
    targets = {d["target"] for d in detail if d["target"]}
    return {
        "source": "GET /api/events?kind=withdrawal",
        "events_total": len(events), "events_in_scope": in_scope, "cutoff": cutoff_s,
        "by_day": dict(sorted(by_day.items())),
        "unparsed_detail": unparsed,
        "distinct_targets": len(targets),
        "withdrawn_items_in_corpus": len(withdrawn),
        "withdrawn_with_an_event": len(withdrawn & targets),
        "withdrawn_without_an_event": len(withdrawn - targets),
        "events_whose_target_is_not_withdrawn_now": sorted(
            t for t in targets if t in rows and t not in withdrawn),
        "detail": detail,
        "note": "an author's own retraction, not a moderator's act. The body is replaced either "
                "way, so both logs are needed to account for every substituted body in the corpus.",
    }


if __name__ == "__main__":
    out = main()
    print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=1))
    S = Path(os.environ.get("MEMETIC_WORKDIR", Path.home() / "personal/memetic-workdir"))
    json.dump(out, open(S / "weather_withdrawal_out.json", "w"), indent=1)
    print("saved", S / "weather_withdrawal_out.json")
