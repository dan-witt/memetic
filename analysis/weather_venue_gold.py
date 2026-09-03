#!/usr/bin/env python3
"""A high-precision VENUE subset by exact match, and the classifier's rate on it.

`results/venue_conflation` measured the VENUE/WORLD axis against a second LLM predicate and found
the two disagree by about eight points, with no hand-labelled reference to say which is closer to
the truth. Its own standing limit names the cheap source of one: exact matching on each venue's
published identifiers. This is that check for 1f916, and only for 1f916 -- the comparator corpus is
frozen and its identifiers are not in hand.

WHAT "OWN" MEANS HERE. Not a guess. The square publishes a canonical record of what it operates --
`GET /api/official` (`operated_properties.meaning`: "This list is COMPLETE"; `official_token
.this_field_wins`: any other contract named as its token "is not") and `GET /api/surface` (every
route it serves). `data/1f916_own_identifiers.json` is a dated snapshot of both, and every marker
below is read from it. Anchoring the markers to the platform's own statement keeps the subset from
being selected on the outcome it is used to test.

The construction. An item that quotes one of those identifiers is, on its face, about the
community's existence or infrastructure -- the VENUE side of the predicate as written. The share of
such items the published classifier labels VENUE is therefore a RECALL estimate on a subset where
the answer is close to known.

What this is not:
  - not a gold set. High-precision, not perfect: an item can quote the treasury address while
    making a claim about a token price, which is external by the predicate.
  - one-sided. It bounds recall on VENUE-true items and says nothing about the WORLD side, so it
    yields no precision figure and no accuracy figure.
  - not a correction. The published labels are untouched.

The comparator is the corpus venue share DIRECTLY STANDARDISED to the subset's own day mix. The
corpus share falls about fifteen points over the observed month, so a raw base rate would be a
comparator only if the subset carried the corpus's day mix, and it does not.

Also reported, and NOT part of any marker: `unowned_addresses`. 40-hex addresses that are not in
the square's record. It is a control, because the naive version of this check matched any address
and mixed them in.

THE WORLD SIDE (added at issue #20, pre-registered by issue #18 and carried by #19). The markers
above bound recall on VENUE-true items and nothing on the other side, so an axis that labels
everything VENUE would pass them. The symmetric subset is the one the same record defines by
exclusion: an item carrying an absolute http(s) URL that is not under any operated property, when
`operated_properties.meaning` says that list is COMPLETE. It is a WEAKER marker than the own-side
ones -- an item can link an outside article while arguing about the square's governance, and the
link is then not the subject -- so it is a recall floor for WORLD, not a gold set, and its cell is
read for SIGN and rough size rather than as a rate. `world_side.exclusive` drops items that also
carry an own marker and is the cell to read.

Usage: python3 analysis/weather_venue_gold.py     (WEATHER_CUTOFF sets the cutoff;
       WEATHER_OWN_IDENTIFIERS points at a snapshot other than the current one)
"""
import collections, datetime as dt, json, os, re, sys
from pathlib import Path
from urllib.parse import urlsplit

R = Path(__file__).resolve().parent.parent
S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
sys.path.insert(0, str(R / "analysis"))
import corpus_store as CS

CUTOFF = os.environ.get("WEATHER_CUTOFF")
OWN_PATH = Path(os.environ.get("WEATHER_OWN_IDENTIFIERS", R / "data/1f916_own_identifiers.json"))
OWN = json.load(open(OWN_PATH))

ADDR = re.compile(r"\b0x[0-9a-fA-F]{40}\b")
# A published route with a :param becomes a prefix: "/api/post/:id" matches "/api/post/1916".
_ROUTES = sorted({p.split("/:")[0].rstrip("/") for p in OWN["api_routes"]}, key=len, reverse=True)
_HOSTS = tuple(h.split("//")[-1].rstrip("/") for h in OWN["operated_sites"])
_REPOS = tuple(r.split("//")[-1].rstrip("/") for r in OWN["operated_repos"])
_TOKEN = OWN["official_token_contract"].lower()
_TREASURY = OWN["treasury_address"].lower()
_OWN_ADDR = {_TOKEN, _TREASURY}


def _routes_in(t):
    """Own /api/ routes quoted in t, ignoring paths served by some other host."""
    out = set()
    for m in re.finditer(r"(?:https?://([^\s/]+))?(/api/[A-Za-z][\w/:.-]*)", t):
        host, path = m.group(1), m.group(2).rstrip(".,);:")
        if host and not host.lower().endswith(_HOSTS):
            continue
        for r in _ROUTES:
            if path == r or path.startswith(r + "/"):
                out.add(r); break
    return out


MARKERS = {
    "own_site": lambda t: any(h in t.lower() for h in _HOSTS),
    "own_repo": lambda t: any(r in t.lower() for r in _REPOS),
    "own_api_route": lambda t: bool(_routes_in(t)),
    "official_token_or_treasury": lambda t: any(m.group(0).lower() in _OWN_ADDR
                                                for m in ADDR.finditer(t)),
}
# Not a marker. The control the naive version of this check needed.
CONTROL = {"unowned_addresses": lambda t: any(m.group(0).lower() not in _OWN_ADDR
                                              for m in ADDR.finditer(t))}

# Every operated property as (host, path prefix). The x account and the subreddit are paths on
# hosts the square does not operate, so a host-only test would hand x.com and reddit.com to the
# WORLD side wholesale and the square's own account with them.
_OWNED = []
for _u in (OWN["operated_sites"] + OWN["operated_repos"]
           + [OWN["operated_x_account"], OWN["operated_subreddit"]]):
    _p = urlsplit(_u)
    _OWNED.append((_p.netloc.lower().removeprefix("www."), _p.path.rstrip("/").lower()))


def _urls_in(t):
    """Absolute http(s) URLs in free text, parsed rather than pattern-matched.

    No stdlib parser finds URLs inside prose, so the text is split on whitespace and each token is
    handed to urlsplit; a token is a URL if it parses with an http(s) scheme and a host. Trailing
    sentence punctuation and wrapping brackets are stripped first. Misses URLs glued to a preceding
    word, which is why the cell is a recall floor.
    """
    out = []
    for tok in t.split():
        tok = tok.strip("<>()[]{}\"'`").rstrip(".,;:!?")
        if "://" not in tok:
            continue
        p = urlsplit(tok)
        if p.scheme in ("http", "https") and p.netloc:
            out.append((p.netloc.lower().removeprefix("www."), p.path.rstrip("/").lower()))
    return out


def _unowned_url(t):
    """An outbound URL under no operated property -- the record's own definition of not-ours."""
    return any(not any(h == oh and (p == op or p.startswith(op + "/")) for oh, op in _OWNED)
               for h, p in _urls_in(t))


def rows(cutoff=CUTOFF, observed_at=None):
    con = CS.build_index()
    cut = dt.datetime(*map(int, cutoff.split("-")), tzinfo=dt.timezone.utc).timestamp()
    return CS.weather_items(con, cut, observed_at=observed_at)


def _daymix(items, labels):
    """-> {day: (labelled, venue)} for the whole corpus, and a key -> day map."""
    day = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
    per, when = collections.defaultdict(lambda: [0, 0]), {}
    for t, k, _, _ in items:
        q = f"{k[0]}:{k[1]}"
        if q not in labels:
            continue
        when[q] = day(t)
        r = per[day(t)]
        r[0] += 1; r[1] += labels[q] == "V"
    return per, when


def _cell(keys, labels, per=None, when=None):
    """A subset's venue rate, and the corpus rate standardised to that subset's own day mix.

    The corpus venue share falls about fifteen points over the observed month, so a raw base rate
    compares a subset to a different mixture of days. Every row therefore carries its own
    direct-standardised comparator, and `lift` is against that.
    """
    lab = [labels[q] for q in keys if q in labels]
    if not lab:
        return {"items": len(keys), "labelled": 0, "venue": 0, "venue_rate": None,
                "counting_se": None}
    v = sum(1 for q in lab if q == "V")
    p = v / len(lab)
    out = {"items": len(keys), "labelled": len(lab), "venue": v, "venue_rate": round(p, 4),
           "counting_se": round((p * (1 - p) / len(lab)) ** 0.5, 4)}
    if per is not None:
        mix = collections.Counter(when[q] for q in keys if q in when)
        n = sum(mix.values())
        std = sum((c / n) * (per[d][1] / per[d][0]) for d, c in mix.items() if per[d][0])
        out["corpus_venue_share_standardised_to_subset_day_mix"] = round(std, 4)
        out["lift_over_corpus_standardised"] = round(p - std, 4)
        out["lift_in_counting_se"] = round((p - std) / out["counting_se"], 2) if out["counting_se"] else None
    return out


# Third-party properties that exist to watch or mirror THIS square. Unlike every other list in
# this file these are a judgement, not the platform's record -- the record can only say what the
# square operates, and by construction an unofficial watcher is not on it. Used for one sensitivity
# row, never for a published marker.
ABOUT_THE_SQUARE = ("openwitness.net", "f916-watch.fly.dev")


def _cluster_se(keys, labels, authors, p):
    """Author-clustered SE for a subset's venue rate.

    The binomial SE every marker row carries assumes independent items. One author writing thirty
    of a 513-item subset breaks that, and this subset is small enough for it to matter. Standard
    cluster-robust sandwich for a mean: sum the per-author residuals, not the per-item ones.
    """
    n = sum(1 for q in keys if q in labels)
    if not n:
        return None
    g = collections.defaultdict(lambda: [0, 0])
    for q in keys:
        if q in labels:
            r = g[authors.get(q, "?")]
            r[0] += 1
            r[1] += labels[q] == "V"
    return round((sum((v - c * p) ** 2 for c, v in g.values()) / n ** 2) ** 0.5, 4)


def world_side(items, labels, per, when):
    """The symmetric subset: items pointing at material the square's own record disclaims.

    Same arithmetic as a marker row, opposite expected sign -- if the axis carries subject matter,
    these items should fall BELOW the day-mix-standardised corpus venue share. `exclusive` is the
    cell to read; `all` keeps the items that also quote an own identifier, where the two markers
    point opposite ways and the item is genuinely mixed.

    Two controls, because the headline row has two obvious alternative explanations:
      `owned_url_only`  -- items whose URLs are ALL under an operated property. If merely carrying
                           a link pushed the classifier toward WORLD, this row would move too.
      `about_the_square_excluded` -- the exclusive row minus items whose unowned hosts are all
                           third-party properties that watch this square. Those are outbound links
                           about the venue, so they attenuate the cell; dropping them says by how
                           much. The host list is a judgement and is named in ABOUT_THE_SQUARE.
    """
    own = {f"{k[0]}:{k[1]}" for _, k, x, _ in items if any(f(x) for f in MARKERS.values())}
    hit = {f"{k[0]}:{k[1]}" for _, k, x, _ in items if _unowned_url(x)}
    authors = {f"{k[0]}:{k[1]}": a for _, k, _, a in items}
    unowned = lambda x: [(h, p) for h, p in _urls_in(x)
                         if not any(h == oh and (p == op or p.startswith(op + "/"))
                                    for oh, op in _OWNED)]
    hosts = collections.Counter(h for _, k, x, _ in items if f"{k[0]}:{k[1]}" in (hit - own)
                                for h, _ in unowned(x))
    with_url = {f"{k[0]}:{k[1]}" for _, k, x, _ in items if _urls_in(x)}
    about = {f"{k[0]}:{k[1]}" for _, k, x, _ in items
             if f"{k[0]}:{k[1]}" in (hit - own)
             and all(h in ABOUT_THE_SQUARE for h, _ in unowned(x))}

    excl = _cell(hit - own, labels, per, when)
    excl["author_clustered_se"] = _cluster_se(hit - own, labels, authors, excl["venue_rate"])
    excl["distinct_authors"] = len({authors.get(q, "?") for q in (hit - own) if q in labels})
    if excl["author_clustered_se"]:
        excl["lift_in_author_clustered_se"] = round(
            excl["lift_over_corpus_standardised"] / excl["author_clustered_se"], 2)
    return {
        "marker": "an absolute http(s) URL under no property in operated_properties",
        "all": _cell(hit, labels, per, when),
        "exclusive": excl,
        "also_bearing_an_own_marker": len(hit & own),
        "top_unowned_hosts": hosts.most_common(12),
        "controls": {
            "owned_url_only": _cell(with_url - hit, labels, per, when),
            "about_the_square_excluded": _cell((hit - own) - about, labels, per, when),
            "about_the_square_only": _cell(about, labels, per, when),
            "about_the_square_hosts": list(ABOUT_THE_SQUARE),
        },
        "read": "a recall FLOOR for the WORLD side, not a gold set: an item can link an outside "
                "page while arguing about the square itself, and URL-finding in prose misses links "
                "glued to a preceding word. Read the sign and rough size of "
                "lift_over_corpus_standardised on `exclusive`, against its AUTHOR-CLUSTERED SE "
                "rather than the binomial one; a lift at or above zero would say the axis does not "
                "separate the two sides at all. One-sided either way: it says nothing about "
                "whether the VENUE label is right.",
    }


def report(items, labels):
    n_lab = sum(1 for _, k, _, _ in items if f"{k[0]}:{k[1]}" in labels)
    base_v = sum(1 for _, k, _, _ in items if labels.get(f"{k[0]}:{k[1]}") == "V")
    per, when = _daymix(items, labels)
    out = {"cutoff": CUTOFF, "own_identifiers": {
        "source": OWN["source"], "fetched_at_utc": OWN["fetched_at_utc"],
        "api_routes": OWN["api_route_count"], "sites": OWN["operated_sites"],
        "repos": OWN["operated_repos"], "official_token": OWN["official_token_contract"],
        "treasury": OWN["treasury_address"]},
        "items": len(items), "labelled": n_lab,
        "corpus_venue_share": round(base_v / n_lab, 4) if n_lab else None, "markers": {}}
    union = set()
    for name, hit in MARKERS.items():
        keys = {f"{k[0]}:{k[1]}" for _, k, x, _ in items if hit(x)}
        union |= keys
        out["markers"][name] = _cell(keys, labels, per, when)
    out["control_not_a_marker"] = {
        name: _cell({f"{k[0]}:{k[1]}" for _, k, x, _ in items if hit(x)}, labels, per, when)
        for name, hit in CONTROL.items()}
    out["control_note"] = (
        "Addresses the square's own record does not claim. NOT part of the union, and reported "
        "because the first version of this check matched any 40-hex address: 94 distinct addresses "
        "appear in the corpus and only two of them are the square's. "
        + OWN["official_token_this_field_wins"])

    u = _cell(union, labels, per, when)
    u["lift_over_corpus_raw"] = round(u["venue_rate"] - out["corpus_venue_share"], 4)
    u["dominated_by"] = ("own_api_route: %d of the union's %d items. The union is one marker with "
                         "a rounding error attached, and the component rows are the reading."
                         % (out["markers"]["own_api_route"]["items"], u["items"]))
    out["union"] = u
    mk = collections.Counter(when[q] for q in union if q in when)
    out["per_day"] = {d: {"labelled": r[0], "venue_rate": round(r[1] / r[0], 4),
                          "marker_labelled": mk.get(d, 0),
                          "marker_venue_rate": round(
                              sum(1 for q in union if when.get(q) == d and labels.get(q) == "V")
                              / mk[d], 4) if mk.get(d) else None,
                          "z": round((sum(1 for q in union if when.get(q) == d
                                          and labels.get(q) == "V") / mk[d] - r[1] / r[0]) /
                                     (((r[1] / r[0]) * (1 - r[1] / r[0]) / mk[d]) ** 0.5), 2)
                          if mk.get(d) and 0 < r[1] < r[0] else None}
                      for d, r in sorted(per.items())}
    out["per_day_beyond_2se"] = [d for d, v in out["per_day"].items()
                                 if v["z"] is not None and abs(v["z"]) > 2]
    out["world_side"] = world_side(items, labels, per, when)
    out["read"] = (
        "venue_rate is the published classifier's RECALL on a subset where the VENUE answer is "
        "close to known by exact match against the square's own published record. One-sided, and "
        "high-precision rather than perfect; it bounds nothing on the WORLD side. Read "
        "lift_over_corpus_standardised, not lift_over_corpus_raw: the corpus venue share has a "
        "strong time trend and the subset does not carry the corpus's day mix.")
    return out


def against_three_way(items, labels, trio=R / "results/venue_conflation/trio_1f916.jsonl"):
    """The same markers, scored against the frozen three-way predicate on its own sample.

    `trio_1f916.jsonl` is STRATIFIED on the published binary -- 1,080 of its VENUE-labelled items
    and 1,080 of its WORLD-labelled ones -- so the binary's venue rate inside it is 50% by
    construction and carries no information. What the design does support is the reverse reading:
    if the markers tracked the binary's label, marker-bearing items would not split evenly between
    the two strata. Their split is the statistic here, alongside the three-way rate on the same
    items, where no such stratification applies to the marker. Both rates are sample-level.
    """
    if not Path(trio).exists():
        return None
    tri = {}
    for line in open(trio):
        r = json.loads(line)
        tri[f"comment:{r['cid']}" if r["kind"] == "comment" else f"post:{r['pid']}"] = r["category"]
    marked = {f"{k[0]}:{k[1]}" for _, k, x, _ in items if any(f(x) for f in MARKERS.values())}
    def split(keys):
        n = len(keys)
        return {"n": n,
                "three_way_venue": round(sum(1 for q in keys if tri[q] == "venue") / n, 4),
                "binary_venue": round(sum(1 for q in keys if labels.get(q) == "V") / n, 4)}
    a, b = split([q for q in tri if q in marked]), split([q for q in tri if q not in marked])
    return {"sample": "results/venue_conflation/trio_1f916.jsonl (frozen, 2160 items)",
            "stratification": "1,080 binary-VENUE + 1,080 binary-WORLD; the binary's rate in the "
                              "whole sample is 0.5 by construction, and both rates below are "
                              "sample-level rather than corpus-level",
            "marker_bearing": a, "rest": b,
            "three_way_separation_pts": round(100 * (a["three_way_venue"] - b["three_way_venue"]), 1),
            "binary_separation_pts": round(100 * (a["binary_venue"] - b["binary_venue"]), 1),
            "read": "the markers separate the three-way predicate's label and do not separate the "
                    "published binary's. Under the stratified design the second half is the "
                    "design-robust statement: marker-bearing items fall in the binary's VENUE and "
                    "WORLD strata in equal proportion."}


if __name__ == "__main__":
    labels = json.load(open(S / "allocation_label_cache_agent.json"))
    _items = rows()
    out = report(_items, labels)
    out["vs_three_way_predicate"] = against_three_way(_items, labels)
    print(json.dumps({k: v for k, v in out.items() if k != "per_day"}, indent=1))
    json.dump(out, open(S / "weather_venue_gold_out.json", "w"), indent=1)
    print("saved", S / "weather_venue_gold_out.json")
