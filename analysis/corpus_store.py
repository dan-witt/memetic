#!/usr/bin/env python3
"""The corpus as an observation log + queryable index, instead of a directory of JSON files.

WHY. Every pass in this repo re-implements the same glob-parse-filter loop over data/posts/*.json,
each carrying its own copy of the >=20-char rule and the /1000 timestamp fix. Worse, a directory
cannot answer the questions the weather series actually asks:

  "when did we first see this item?"        -> reconstructed by diffing whole corpus snapshots
  "what did the corpus look like on 08-19?" -> found by archaeology in git history
  "which threads are stale?"                -> unrepresentable; a 2026-08-23 pull silently saved
                                               674 of 1,801 threads and nothing in the data said so

Those three gaps caused, respectively: the feed_lag instrument (which exists only to recover
first-seen times a directory cannot store), the identity pass shipping with no cutoff, and a
rate-limited pull leaving a mixed-vintage corpus that only `git status` revealed.

THE MODEL. Three tables, one idea: record WHAT WE OBSERVED AND WHEN, never overwrite.

  observations  one row per item VERSION we have seen. An item that is edited gets a second row;
                nothing is ever mutated. first_seen_at is when WE saw it, created_at is what the
                API says. Backfill is then `first_seen_at - created_at`, a column, not a diff.
  threads       per-thread bookkeeping: when we last fetched it, when it last changed, when it was
                last active. This is what lets a fetcher choose what to refresh, and what lets a
                report state its coverage instead of assuming completeness.
  fetch_runs    one row per fetch attempt, including partial ones: mode, cursor, and how many
                threads succeeded / 404'd / 429'd. A partial pull becomes a visible fact.

STORAGE. The append-only JSONL (data/observations.jsonl, data/fetch_runs.jsonl) is the committed
truth -- append-only keeps git diffs small, unlike a SQLite file that rewrites wholesale. The
SQLite index is DERIVED and gitignored; rebuild it any time with build_index(). Raw API responses
stay in data/posts/<id>.json as archival record; this store is the queryable view over them.

FILTERING IS A QUERY CONCERN. The store records every item as fetched. The >=20-char rule lives in
items_at(), so the store stays a faithful record and the analysis rule stays in one place.
"""
import hashlib, json, os, sqlite3, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
POSTS = DATA / "posts"
OBS_LOG = DATA / "observations.jsonl"
RUN_LOG = DATA / "fetch_runs.jsonl"
DB = DATA / "corpus.db"
# Per-thread "when did we last VERIFY this thread". Not history -- current state -- so it is a
# small rewritten map rather than an append-only log. It is what the staleness sweep reads, and
# what lets a report state coverage instead of assuming a full re-read happened.
THREAD_STATE = DATA / "thread_state.json"

MIN_CHARS = 20          # the analysis inclusion rule, in exactly one place


def _norm_ts(t):
    """API timestamps are ms or s depending on age; normalize to epoch seconds."""
    t = t or 0
    return t / 1000 if t > 1e12 else float(t)


def item_text(kind, obj):
    """The text convention every pass in this repo uses, in one place."""
    if kind == "post":
        return ((obj.get("title") or "") + "\n\n" + (obj.get("body") or "")).strip()
    return (obj.get("body") or "").strip()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def read_thread(path):
    """-> (post_id, [item dicts]) for one raw thread JSON, or None if unreadable."""
    try:
        th = json.load(open(path))
    except Exception:
        return None
    p = th.get("post") or {}
    pid = p.get("id")
    if pid is None:
        return None
    out = []
    for kind, obj in [("post", p)] + [("comment", c) for c in th.get("comments", [])]:
        oid = obj.get("id")
        if oid is None:
            continue
        txt = item_text(kind, obj)
        out.append({
            "item_key": f"{kind}:{oid}",
            "kind": kind, "post_id": pid, "item_id": oid,
            "created_at": _norm_ts(obj.get("created_at")),
            "author": obj.get("author"), "author_model": obj.get("author_model"),
            "n_chars": len(txt), "content_sha": sha(txt),
        })
    return pid, out


def scan_tree(posts_dir=POSTS):
    """-> {item_key: row} for every item in a corpus tree, plus {post_id: thread_sha}."""
    items, threads = {}, {}
    for f in Path(posts_dir).glob("*.json"):
        r = read_thread(f)
        if not r:
            continue
        pid, rows = r
        threads[pid] = sha("".join(sorted(x["content_sha"] for x in rows)))
        for row in rows:
            items[row["item_key"]] = row
    return items, threads


# ---------------------------------------------------------------- the log
def load_log(path=OBS_LOG):
    """-> [rows] oldest first. Missing file is an empty log, not an error."""
    if not Path(path).exists():
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def append_snapshot(items, observed_at, run_id, log_path=OBS_LOG, known=None):
    """Append rows for item-versions not already in the log. -> (n_new_items, n_edits).

    `known` is {item_key: content_sha} of what the log already holds; pass it to avoid re-reading
    the log when ingesting many snapshots in sequence.
    """
    if known is None:
        known = {r["item_key"]: r["content_sha"] for r in load_log(log_path)}
    new, edits, out = 0, 0, []
    for key, row in sorted(items.items()):
        prev = known.get(key)
        if prev == row["content_sha"]:
            continue
        rec = dict(row, first_seen_at=observed_at, run_id=run_id,
                   version=("edit" if prev is not None else "new"))
        out.append(rec)
        known[key] = row["content_sha"]
        new += prev is None
        edits += prev is not None
    if out:
        with open(log_path, "a") as fh:
            for rec in out:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return new, edits


def append_run(rec, path=RUN_LOG):
    with open(path, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


# ---------------------------------------------------------------- the index
SCHEMA = """
CREATE TABLE observations (
  item_key TEXT, kind TEXT, post_id INTEGER, item_id INTEGER,
  created_at REAL, author TEXT, author_model TEXT,
  n_chars INTEGER, content_sha TEXT,
  first_seen_at REAL, run_id TEXT, version TEXT
);
CREATE INDEX obs_key   ON observations(item_key, first_seen_at);
CREATE INDEX obs_time  ON observations(created_at);
CREATE INDEX obs_seen  ON observations(first_seen_at);
CREATE TABLE threads (
  post_id INTEGER PRIMARY KEY, last_fetched_at REAL, last_changed_at REAL,
  last_activity_at REAL, n_items INTEGER, thread_sha TEXT
);
CREATE TABLE fetch_runs (
  run_id TEXT PRIMARY KEY, started_at REAL, ended_at REAL, mode TEXT,
  cursor_before TEXT, cursor_after TEXT, threads_attempted INTEGER,
  threads_ok INTEGER, threads_404 INTEGER, threads_429 INTEGER, complete INTEGER, note TEXT
);
"""


def build_index(db_path=DB, log_path=OBS_LOG, run_path=RUN_LOG, posts_dir=POSTS):
    """(Re)build the derived SQLite index from the append-only logs. -> sqlite3.Connection."""
    if Path(db_path).exists():
        Path(db_path).unlink()
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    rows = load_log(log_path)
    con.executemany(
        "INSERT INTO observations VALUES (:item_key,:kind,:post_id,:item_id,:created_at,:author,"
        ":author_model,:n_chars,:content_sha,:first_seen_at,:run_id,:version)", rows)
    if Path(run_path).exists():
        for r in (json.loads(l) for l in open(run_path) if l.strip()):
            con.execute("INSERT OR REPLACE INTO fetch_runs VALUES "
                        "(:run_id,:started_at,:ended_at,:mode,:cursor_before,:cursor_after,"
                        ":threads_attempted,:threads_ok,:threads_404,:threads_429,:complete,:note)",
                        {**{k: None for k in ("run_id", "started_at", "ended_at", "mode",
                                              "cursor_before", "cursor_after", "threads_attempted",
                                              "threads_ok", "threads_404", "threads_429",
                                              "complete", "note")}, **r})
    # threads table: current on-disk state + observed history
    _, thread_shas = scan_tree(posts_dir)
    con.execute("""INSERT INTO threads (post_id, last_changed_at, last_activity_at, n_items)
                   SELECT post_id, MAX(first_seen_at), MAX(created_at), COUNT(DISTINCT item_key)
                   FROM observations GROUP BY post_id""")
    for pid, s in thread_shas.items():
        con.execute("UPDATE threads SET thread_sha=? WHERE post_id=?", (s, pid))
    if Path(THREAD_STATE).exists():
        for pid, ts in json.loads(Path(THREAD_STATE).read_text()).items():
            con.execute("UPDATE threads SET last_fetched_at=? WHERE post_id=?", (ts, int(pid)))
    con.commit()
    return con


def load_thread_state(path=THREAD_STATE):
    return {int(k): v for k, v in json.loads(Path(path).read_text()).items()} \
        if Path(path).exists() else {}


def save_thread_state(state, path=THREAD_STATE):
    Path(path).write_text(json.dumps({str(k): round(v, 3) for k, v in sorted(state.items())},
                                     indent=0) + "\n")


# ---------------------------------------------------------------- queries
def items_at(con, cutoff=None, observed_at=None, min_chars=MIN_CHARS):
    """The corpus as it stood, as a list of rows.

    cutoff       epoch seconds; keep items with created_at < cutoff (the weather convention:
                 midnight UTC, exclusive).
    observed_at  epoch seconds; use only what we had SEEN by then, and each item's latest version
                 as of then. None = everything we know now. This is what makes a past issue
                 reproducible without checking out a commit.
    """
    q = ["SELECT item_key, kind, post_id, item_id, created_at, author, author_model, n_chars,"
         " content_sha, first_seen_at FROM observations o WHERE 1=1"]
    p = []
    if cutoff is not None:
        q.append("AND created_at < ?"); p.append(cutoff)
    if observed_at is not None:
        q.append("AND first_seen_at <= ?"); p.append(observed_at)
    if min_chars:
        q.append("AND n_chars >= ?"); p.append(min_chars)
    # latest version of each item as of observed_at
    q.append("AND first_seen_at = (SELECT MAX(first_seen_at) FROM observations i"
             " WHERE i.item_key = o.item_key")
    if observed_at is not None:
        q.append("AND i.first_seen_at <= ?"); p.append(observed_at)
    q.append(") ORDER BY created_at")
    cur = con.execute(" ".join(q), p)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def coverage(con, now=None, fresh_hours=24):
    """-> how much of the corpus sits in threads verified recently. The honest alternative to
    assuming a full re-read happened."""
    now = now or time.time()
    cur = con.execute("SELECT COUNT(*), SUM(CASE WHEN last_fetched_at >= ? THEN 1 ELSE 0 END) "
                      "FROM threads", (now - fresh_hours * 3600,))
    total, fresh = cur.fetchone()
    return {"threads": total, "threads_fresh": fresh or 0,
            "fresh_hours": fresh_hours,
            "pct_fresh": round(100 * (fresh or 0) / total, 1) if total else None}


def verified_since(con, since):
    """-> how much of the corpus was re-read at least once since `since` (epoch seconds).

    coverage() answers "how fresh is the corpus now", which is the right question for a fetcher.
    The content-mutation audit asks a different one: an edit is only detectable in a thread we
    actually re-read AFTER the previous issue, so the audit's real denominator is coverage since
    that issue's pull, not coverage within a rolling 24 h. Reported item-weighted as well as
    thread-weighted, because threads differ by an order of magnitude in size and the audit is a
    claim about items.
    """
    total_t, = con.execute("SELECT COUNT(*) FROM threads").fetchone()
    seen_t, = con.execute("SELECT COUNT(*) FROM threads WHERE last_fetched_at >= ?",
                          (since,)).fetchone()
    total_i, = con.execute("SELECT COUNT(DISTINCT item_key) FROM observations").fetchone()
    seen_i, = con.execute(
        "SELECT COUNT(DISTINCT item_key) FROM observations WHERE post_id IN "
        "(SELECT post_id FROM threads WHERE last_fetched_at >= ?)", (since,)).fetchone()
    return {"since_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since)),
            "threads": total_t, "threads_verified": seen_t,
            "pct_threads": round(100 * seen_t / total_t, 1) if total_t else None,
            "items": total_i, "items_verified": seen_i,
            "pct_items": round(100 * seen_i / total_i, 1) if total_i else None}


def stale_threads(con, now=None, limit=None, min_idle_hours=1.0):
    """Which threads to refresh, most-worth-it first -- the DB driving the fetcher.

    Priority = staleness relative to how recently the thread was active. A thread active an hour
    ago and unfetched for two hours outranks one dormant for a week. Concretely we score
    (now - last_fetched_at) / (now - last_activity_at), so attention decays as a thread goes quiet
    instead of every thread costing the same request every run.
    """
    now = now or time.time()
    rows = con.execute("SELECT post_id, last_fetched_at, last_activity_at FROM threads").fetchall()
    out = []
    for pid, fetched, active in rows:
        fetched = fetched or 0
        idle = max(now - (active or 0), 3600.0)
        stale = now - fetched
        if stale < min_idle_hours * 3600:
            continue
        out.append((stale / idle, pid, stale, idle))
    out.sort(reverse=True)
    if limit:
        out = out[:limit]
    return [{"post_id": pid, "score": round(s, 3), "stale_hours": round(st / 3600, 2),
             "idle_hours": round(idl / 3600, 2)} for s, pid, st, idl in out]


def backfill(con, prev_at=None, this_at=None, run_id=None, basis="prev_last_item"):
    """Items that a run saw for the first time although they predate the PREVIOUS run.

    This is the feed_lag instrument, as a query. The naive version -- first_seen_at - created_at >
    some threshold -- is meaningless here, because first_seen_at has one-pull resolution and every
    item is "late" by that measure. What backfill actually means is: the previous pull should have
    caught this item and did not. So the comparison is against the previous run's observation time,
    not against the item's own age.

    -> [{run_id, prev_run_at, item_key, created_at, first_seen_at, age_at_missed_pull_h, author}]
    """
    # Explicit boundaries when given: the weather series compares ISSUE to issue, and once
    # catch-up runs are daily there are several runs between two issues. Without them, fall back
    # to consecutive observation times, which is the finest grain the log supports.
    if prev_at is not None and this_at is not None:
        pairs = [(prev_at, this_at)]
    else:
        runs = [r[0] for r in con.execute(
            "SELECT DISTINCT first_seen_at FROM observations ORDER BY first_seen_at").fetchall()]
        pairs = list(zip(runs, runs[1:]))
    out = []
    for prev_at, this_at in pairs:
        if run_id is not None and this_at != run_id:
            continue
        # WHICH BOUNDARY. The weather series compares against the previous corpus's LAST ITEM
        # (weather_cpu.py's prev_last), not the previous pull's clock. The two differ by whatever
        # gap sat between the last item and the pull -- 82 seconds at issue #10, which is one item.
        # prev_last_item reproduces the published series; prev_run is the stricter reading (the
        # pull ran at time T, so anything created before T should have been caught). The directory
        # version could only express the first, and did so implicitly; here it is a named choice.
        if basis == "prev_run":
            bound = prev_at
        else:
            row = con.execute("SELECT MAX(created_at) FROM observations WHERE first_seen_at <= ?",
                              (prev_at,)).fetchone()
            bound = row[0] if row and row[0] is not None else prev_at
        cur = con.execute(
            "SELECT item_key, created_at, first_seen_at, author FROM observations "
            "WHERE version='new' AND first_seen_at > ? AND first_seen_at <= ? "
            "AND created_at <= ?", (prev_at, this_at, bound))
        for key, created, seen, author in cur.fetchall():
            # "revealed" an author only if this backfilled item is that author's FIRST observation
            # anywhere -- the previous corpus did not know the author existed at all.
            first = con.execute("SELECT MIN(first_seen_at) FROM observations WHERE author = ?",
                                (author,)).fetchone()[0]
            out.append({"reveals_author": first is not None and abs(first - seen) < 1,
                        "observed_at": this_at, "prev_run_at": prev_at, "item_key": key,
                        "created_at": created, "first_seen_at": seen, "author": author,
                        "basis": basis, "boundary": bound,
                        "age_at_missed_pull_h": round((bound - created) / 3600, 2)})
    return out


def edits(con, since=None, until=None):
    """Post-publication text changes -- a column, not a corpus diff."""
    q = "SELECT item_key, post_id, author, created_at, first_seen_at FROM observations WHERE version='edit'"
    p = []
    if since is not None:
        q += " AND first_seen_at > ?"; p.append(since)
    if until is not None:
        q += " AND first_seen_at <= ?"; p.append(until)
    cur = con.execute(q + " ORDER BY first_seen_at", p)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def item_texts(keys, posts_dir=POSTS):
    """-> {item_key: text} for the requested keys, read from the raw thread archive.

    Keyed, never zipped: read_thread() skips objects with no id, so pairing its output positionally
    against the raw comment list would misalign the moment one comment lacks an id.
    """
    want, out = set(keys), {}
    for f in Path(posts_dir).glob("*.json"):
        try:
            th = json.load(open(f))
        except Exception:
            continue
        for kind, obj in [("post", th.get("post") or {})] + \
                         [("comment", c) for c in th.get("comments", [])]:
            oid = obj.get("id")
            if oid is None:
                continue
            key = f"{kind}:{oid}"
            if key in want:
                out[key] = item_text(kind, obj)
    return out


PLACEHOLDER_MARKER = "[collapsed"   # 1f916's collapse boilerplate opens with it


def is_placeholder(text):
    """A body that is ONLY collapse boilerplate, possibly repeated.

    When 1f916 collapses an item it substitutes a fixed body rather than deleting the row, and that
    body clears MIN_CHARS. A collapsed POST has title and body both replaced, so the marker repeats.
    Deliberately strict: a real comment that merely quotes the marker keeps its other lines.
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    return bool(lines) and all(l.startswith(PLACEHOLDER_MARKER) for l in lines)


def exclude_placeholders_default():
    """Whether the loaders drop collapse placeholders when the caller does not say.

    Issue #14 made the placeholder-free parse the published currency; WEATHER_KEEP_PLACEHOLDERS=1
    restores the issue #1-#13 basis. It is resolved here, once, because eight call sites load the
    corpus and they must all answer the same way within one run.
    """
    return os.environ.get("WEATHER_KEEP_PLACEHOLDERS", "") not in ("1", "true", "yes")


_ph_keys = None


def placeholder_keys(con, posts_dir=POSTS):
    """-> {item_key} of every collapse placeholder in the archive. Memoized per process.

    Text-free callers (author_stream, profile_rows) need the same exclusion the text-bearing ones
    apply, so the set is resolved once here rather than re-derived per call site.
    """
    global _ph_keys
    if _ph_keys is None:
        rows = items_at(con, min_chars=0)
        text = item_texts((r["item_key"] for r in rows), posts_dir)
        _ph_keys = {k for k, t in text.items() if is_placeholder(t)}
    return _ph_keys


def weather_items(con, cutoff, observed_at=None, min_chars=MIN_CHARS, posts_dir=POSTS,
                  exclude_placeholders=None):
    """The weather pipeline's tuple shape: [(created_at, (kind, id), text, author)], sorted the
    way weather_cpu.py sorts (time, posts before comments, id).

    The store decides WHICH items are in scope -- including, via observed_at, which observations
    existed at the time an issue was produced -- and the raw archive supplies their text, because
    the log holds a content hash rather than a body.
    """
    if exclude_placeholders is None:
        exclude_placeholders = exclude_placeholders_default()
    rows = items_at(con, cutoff=cutoff, observed_at=observed_at, min_chars=min_chars)
    text = item_texts((r["item_key"] for r in rows), posts_dir)
    missing = [r["item_key"] for r in rows if r["item_key"] not in text]
    if missing:
        raise SystemExit(f"{len(missing)} in-scope items have no text in {posts_dir} "
                         f"(e.g. {missing[:3]}). The archive is behind the log: re-fetch, or pass "
                         f"an observed_at that predates them.")
    if exclude_placeholders:
        rows = [r for r in rows if not is_placeholder(text[r["item_key"]])]
    out = [(r["created_at"], (r["kind"], r["item_id"]), text[r["item_key"]], r["author"] or "?")
           for r in rows]
    out.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return out


def author_stream(con, cutoff, observed_at=None, min_chars=MIN_CHARS,
                  exclude_placeholders=None, posts_dir=POSTS):
    """[(created_at, author)] -- the shape the churn and permeability controls consume.

    One query, except when excluding placeholders: that identity lives in the body, so the first
    such call in a process reads the archive once to resolve placeholder_keys() and memoizes it.
    """
    if exclude_placeholders is None:
        exclude_placeholders = exclude_placeholders_default()
    drop = placeholder_keys(con, posts_dir) if exclude_placeholders else ()
    return [(r["created_at"], r["author"] or "?")
            for r in items_at(con, cutoff=cutoff, observed_at=observed_at, min_chars=min_chars)
            if r["item_key"] not in drop]


def profile_rows(con, cutoff, observed_at=None, min_chars=MIN_CHARS,
                 exclude_placeholders=None, posts_dir=POSTS):
    """[(created_at, author, author_model, n_chars, post_id, kind)] -- weather_influx_profile's shape.

    Text-free on the same terms as author_stream. The model label is the platform's own, carried
    through unchanged. `kind` is
    carried because the platform's per-author daily cap applies to COMMENTS, not to items, so a
    caller counting the cap has to separate the two.
    """
    if exclude_placeholders is None:
        exclude_placeholders = exclude_placeholders_default()
    drop = placeholder_keys(con, posts_dir) if exclude_placeholders else ()
    return [(r["created_at"], r["author"] or "?", r["author_model"], r["n_chars"], r["post_id"],
             r["kind"])
            for r in items_at(con, cutoff=cutoff, observed_at=observed_at, min_chars=min_chars)
            if r["item_key"] not in drop]
