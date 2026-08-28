#!/usr/bin/env python3
"""What the square moderates, from 1f916's own identity log.

Issue #13 measured the collapse placeholder as a corpus defect -- 145 items whose bodies the
platform had replaced -- but the pipeline could only count them. The placeholder text names where
the reason lives:

    [collapsed - flagged by the community or hidden by the maintainer; not deleted.
     Reason in GET /api/events?kind=moderation]

That endpoint is public, unauthenticated and cheap: the identity log is append-only and filterable
by kind, so one paged read gives every exercise of moderation power the app has recorded. This
script pulls it, joins each event to the corpus item it acted on, and reports what was moderated
and why. Issue #14's watch item #3.

BOUNDARY, stated because the log states it: the chain witnesses only what passed through the
application. Whoever holds the database can write to it directly, which no log row can show. So
this is the full record of moderation THROUGH THE APP, not a proof that nothing else happened.

Usage:
  python3 analysis/weather_moderation_events.py            # pull + report
  python3 analysis/weather_moderation_events.py --offline   # re-report from the cached pull
"""
import datetime as dt, json, os, sys, time, urllib.error, urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_store as CS

BASE = "https://1f916.ai"
UA = {"User-Agent": "1f916-archiver/1.0 (read-only corpus pull)"}
SLEEP = 0.5                       # the published sustained limit: 120/min
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def get(path, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(11.0)    # the edge blocks for 10 s
                continue
            raise
    raise SystemExit(f"gave up on {path}")


def pull(cache):
    """Every kind=moderation row, paged with ?since=. -> [event]"""
    out, since, seen = [], None, set()
    while True:
        page = get("/api/events?kind=moderation" + (f"&since={since}" if since else ""))
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


# The log's `detail` is prose with a fixed prefix grammar the platform writes:
#     "<verb> <kind> <id>[: <reason>]"      e.g. "collapsed comment 15591: Collapsed at the ..."
#     "bulletin posted ..."                  (no target)
# Split on whitespace and the first colon; no pattern matching is needed and none is used.
TARGET_KINDS = ("post", "comment")


def parse_detail(ev):
    """-> {'action', 'kind', 'item_id', 'reason'}; kind/item_id are None for targetless rows."""
    d = (ev.get("detail") or "").strip()
    head, sep, reason = d.partition(":")
    words = head.split()
    out = {"action": words[0] if words else "(empty)", "kind": None, "item_id": None,
           "reason": reason.strip() if sep else None}
    if len(words) >= 3 and words[1] in TARGET_KINDS and words[2].isdigit():
        out["kind"], out["item_id"] = words[1], int(words[2])
    return out


def target_of(ev):
    """-> (kind, id) the event acted on, or None."""
    d = parse_detail(ev)
    return (d["kind"], d["item_id"]) if d["kind"] else None


def reason_of(ev):
    return parse_detail(ev)["reason"]


def action_of(ev):
    return parse_detail(ev)["action"]


def main():
    S = Path(os.environ.get("MEMETIC_WORKDIR", Path.home() / "personal/memetic-workdir"))
    cache = S / "moderation_events.json"
    cutoff_s = os.environ.get("WEATHER_CUTOFF")

    if "--offline" in sys.argv:
        events = json.load(open(cache))
    else:
        events = pull(cache)
    print(f"{len(events)} moderation events in the identity log")

    con = CS.build_index()
    ph = CS.placeholder_keys(con)
    cut = dt.datetime(*map(int, cutoff_s.split("-")), tzinfo=dt.timezone.utc).timestamp() \
        if cutoff_s else None

    # the corpus rows, so an event can be attributed to a day and an author
    rows = {r["item_key"]: r for r in CS.items_at(con, cutoff=cut, min_chars=0)}

    by_day, actions, reasons, matched, unmatched = Counter(), Counter(), Counter(), [], 0
    all_actions = []
    for ev in events:
        ts = ev.get("created_at")
        ts = ts / 1000 if ts and ts > 1e11 else ts
        if cut and ts and ts >= cut:
            continue
        tk = target_of(ev)
        all_actions.append(action_of(ev))
        actions[action_of(ev)] += 1
        r = reason_of(ev)
        reasons[(r or "(none given)")[:60]] += 1
        if ts:
            by_day[DAY(ts)] += 1
        if tk:
            key = f"{tk[0]}:{tk[1]}"
            row = rows.get(key)
            matched.append({"event_id": ev.get("id"), "target": key,
                            "in_corpus": row is not None,
                            "is_placeholder_now": key in ph,
                            "day": DAY(ts) if ts else None,
                            "author": (row or {}).get("author"),
                            "action": action_of(ev), "reason": r})
        else:
            unmatched += 1

    emit = {
        "source": "GET /api/events?kind=moderation",
        "events_total": len(events),
        "events_in_scope": sum(by_day.values()),
        "cutoff": cutoff_s,
        "by_day": dict(sorted(by_day.items())),
        "actions": dict(actions.most_common()),
        "reasons": dict(reasons.most_common(20)),
        "targets_resolved": len(matched),
        "targets_unresolved": unmatched,
        # An item can carry several events (collapse, restore, collapse again), so every join
        # figure below counts DISTINCT ITEMS, not event rows.
        "distinct_targets": len({m["target"] for m in matched}),
        "placeholders_in_corpus": len(ph),
        "placeholders_with_an_event": len({m["target"] for m in matched
                                           if m["is_placeholder_now"]}),
        "placeholders_without_an_event": len(ph - {m["target"] for m in matched}),
        # Counted over EVERY in-scope event, not only those whose target resolved: 11 bulletin
        # rows name a timestamp rather than an item, and counting only the resolvable ones made
        # publication_actions disagree with `actions` (5 vs 16).
        "content_actions": dict(Counter(
            a for a in all_actions if a in ("collapsed", "removed"))),
        "publication_actions": dict(Counter(
            a for a in all_actions if a not in ("collapsed", "removed"))),
        "items_acted_on_but_not_placeholders": len({
            m["target"] for m in matched if m["in_corpus"] and not m["is_placeholder_now"]}),
        "boundary": "The chain witnesses what passed through the application only; a direct "
                    "database write is outside it by construction.",
        "detail": matched,
    }
    out = S / "weather_moderation_out.json"
    json.dump(emit, open(out, "w"), indent=1)

    print(f"by day: {emit['by_day']}")
    print(f"actions: {emit['actions']}")
    print(f"placeholders in corpus {len(ph)}; with a log event "
          f"{emit['placeholders_with_an_event']}, without one "
          f"{emit['placeholders_without_an_event']}")
    print(f"content actions {emit['content_actions']}, publication actions "
          f"{emit['publication_actions']}")
    print(f"distinct items acted on that are NOT placeholders now: "
          f"{emit['items_acted_on_but_not_placeholders']}")
    print(f"top reasons: {list(emit['reasons'].items())[:8]}")
    print(f"saved {out}")


if __name__ == "__main__":
    main()
