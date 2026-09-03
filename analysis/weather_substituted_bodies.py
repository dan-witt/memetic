#!/usr/bin/env python3
"""Platform-substituted bodies the currency still counts as content.

Issue #13 measured one of these and issue #14 excluded it: when 1f916 COLLAPSES an item it replaces
the body with fixed boilerplate, the boilerplate clears MIN_CHARS, and every cell downstream was
reading it as a citizen's text. `corpus_store.is_placeholder` matches that one marker.

The platform substitutes a body in three cases, not one. `mod_state` names them, and the other two
are still in the published currency:

    collapsed   excluded since issue #14 (is_placeholder matches its marker)
    removed     counted; body is "[removed by the maintainer -- reason in GET /api/events?...]"
    withdrawn   counted; body is "[withdrawn by its author -- reason in GET /api/events?...]"

Found at issue #20 by opening the item the mutation audit had just flagged as edited: it was not
edited, it was withdrawn, and the platform had replaced its body. One of issue #19's two edits is
the same substitution, which is why it flipped a venue label from WORLD to VENUE -- the replacement
quotes an own API route, so a platform notice is scored as an item about the venue. That is the
defect in one sentence: the platform's own boilerplate sits in a corpus of citizens' writing, it
quotes `/api/events`, and the venue classifier reads it exactly as written. Counts move with the
cutoff and are in the output, not here.

This measures the effect and changes nothing. Detection is `mod_state`, the platform's own field,
rather than text matching -- the text is the symptom.

Usage: MEMETIC_WORKDIR=... WEATHER_CUTOFF=YYYY-MM-DD python3 analysis/weather_substituted_bodies.py
"""
import collections, datetime as dt, json, os, sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
sys.path.insert(0, str(R / "analysis"))
import corpus_store as CS

CUTOFF = os.environ.get("WEATHER_CUTOFF")
SUBSTITUTED = ("collapsed", "removed", "withdrawn")


def states(cutoff=CUTOFF):
    """-> {item_key: (mod_state, day, n_chars)} for every in-scope item the platform rewrote."""
    cut = dt.datetime(*map(int, cutoff.split("-")), tzinfo=dt.timezone.utc).timestamp()
    out = {}
    for f in (CS.POSTS).glob("*.json"):
        th = json.load(open(f))
        p = th.get("post") or {}
        for kind, o in [("post", p)] + [("comment", c) for c in th.get("comments", [])]:
            if o.get("id") is None or o.get("mod_state") not in SUBSTITUTED:
                continue
            t = CS._norm_ts(o.get("created_at"))
            if t is None or t >= cut:
                continue
            txt = CS.item_text(kind, o)
            if len(txt) < CS.MIN_CHARS:
                continue
            out[f"{kind}:{o['id']}"] = (o["mod_state"], dt.datetime.fromtimestamp(
                t, dt.timezone.utc).strftime("%m-%d"), len(txt))
    return out


def main():
    sub = states()
    labels = json.load(open(S / "allocation_label_cache_agent.json"))
    con = CS.build_index()
    cut = dt.datetime(*map(int, CUTOFF.split("-")), tzinfo=dt.timezone.utc).timestamp()
    ph = CS.placeholder_keys(con)

    counted = {k: v for k, v in sub.items() if k not in ph}   # in the published currency today
    per_day = collections.defaultdict(lambda: [0, 0])          # day -> [labelled, venue]
    for t, k, _, _ in CS.weather_items(con, cut):
        q = f"{k[0]}:{k[1]}"
        if q not in labels:
            continue
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
        per_day[d][0] += 1
        per_day[d][1] += labels[q] == "V"

    hit = collections.defaultdict(lambda: [0, 0])
    for q, (st, day, _) in counted.items():
        if q in labels:
            hit[day][0] += 1
            hit[day][1] += labels[q] == "V"

    days = {}
    for d, (n, v) in sorted(per_day.items()):
        hn, hv = hit.get(d, [0, 0])
        days[d] = {
            "labelled": n, "venue_share": round(v / n, 4) if n else None,
            "substituted_labelled": hn, "substituted_venue": hv,
            "venue_share_excluding_substituted": round((v - hv) / (n - hn), 4) if n - hn else None,
            "move": round((v - hv) / (n - hn) - v / n, 4) if n - hn and n else None,
        }
    lab = [q for q in counted if q in labels]
    return {
        "cutoff": CUTOFF,
        "detection": "post/comment.mod_state, the platform's own field",
        "by_state": dict(collections.Counter(v[0] for v in sub.values())),
        "in_the_published_currency": {
            "items": len(counted),
            "by_state": dict(collections.Counter(v[0] for v in counted.values())),
            "chars": dict(collections.Counter(v[2] for v in counted.values())),
        },
        "excluded_already_as_placeholders": len(sub) - len(counted),
        "labelled": len(lab),
        "venue_labelled": sum(1 for q in lab if labels[q] == "V"),
        "venue_rate": round(sum(1 for q in lab if labels[q] == "V") / len(lab), 4) if lab else None,
        "per_day": days,
        "largest_day_move": min((d["move"] for d in days.values() if d["move"] is not None),
                                default=None),
        "read": "the counterfactual series is what the currency WOULD read with the platform's own "
                "substituted bodies dropped, on the labels as they stand. Every move is <= 0 "
                "because the boilerplate labels VENUE far above the corpus rate, so the published "
                "venue-share series is an upper bound in this respect as well as in coverage.",
    }


if __name__ == "__main__":
    out = main()
    print(json.dumps({k: v for k, v in out.items() if k != "per_day"}, indent=1))
    print("per-day moves:", json.dumps({d: v["move"] for d, v in out["per_day"].items()
                                        if v["move"]}, indent=1))
    json.dump(out, open(S / "weather_substituted_bodies_out.json", "w"), indent=1)
    print("saved", S / "weather_substituted_bodies_out.json")
