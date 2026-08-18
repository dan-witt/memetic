#!/usr/bin/env python3
"""Polite, resumable crawler for the lemmy.world founding window (ALLOCATION anchor).

Frame: every LOCAL community created on or before the arrival step (default T0+8.2d,
i.e. the communities that already existed when the reddit exodus landed on 2023-06-09).
For each, walk posts and comments oldest-first and keep everything published inside the
content window. Records carry the ActivityPub `ap_id`, so any published frame is
verifiable against any instance in the federation without re-crawling lemmy.world.

Politeness (non-negotiable, see lemmy.world/robots.txt):
  * one request per Crawl-delay seconds (robots.txt says 60), read from robots at startup
  * every request re-checked against robots.txt via urllib.robotparser
  * identifying User-Agent with a contact address
  * a `STOP` sentinel file in the state dir halts the run cleanly at the next boundary

Resumability: state.json is rewritten after every single request, and records are appended
to posts.jsonl / comments.jsonl. Re-running resumes exactly where it left off; already-seen
ids are skipped. Killing the process at any point loses at most one in-flight request.

Outputs (under MEMETIC_WORKDIR/lemmy/):
  frame_communities.json  the sampling frame (community, actor_id, created)
  posts.jsonl             one JSON record per post
  comments.jsonl          one JSON record per comment
  state.json              crawl cursor (phase, queue index, page)
  crawl.log               append-only progress log
"""
import argparse, datetime as dt, hashlib, json, os, sys, time, urllib.error, urllib.parse
import urllib.request, urllib.robotparser
from pathlib import Path

INSTANCE = "https://lemmy.world"
API = INSTANCE + "/api/v3"
UA_TEMPLATE = "memetic-research/0.1 (allocation study; contact: {contact})"
UA = None            # set from --contact in __main__; robots politeness requires a real address
T0 = dt.datetime(2023, 6, 1, 7, 1, 46, tzinfo=dt.timezone.utc)   # lemmy.world site.published


def parse_ts(s):
    s = s.replace("Z", "+00:00")
    if "+" not in s[10:] and "-" not in s[10:]:
        s += "+00:00"
    return dt.datetime.fromisoformat(s)


def hz(s):
    return hashlib.sha1((s or "").encode("utf-8", "replace")).hexdigest()[:12]


class Crawler:
    def __init__(self, a):
        self.a = a
        self.dir = Path(a.state_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.log_f = (self.dir / "crawl.log").open("a", buffering=1)
        self.rp = urllib.robotparser.RobotFileParser()
        self.delay = a.delay
        self.requests = 0
        self.last_req = 0.0
        self.state = self._load_state()
        self.seen_posts = self._load_seen("posts.jsonl")
        self.seen_comments = self._load_seen("comments.jsonl")

    # ---------- logging / state ----------
    def log(self, msg):
        line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} {msg}"
        print(line, flush=True)
        self.log_f.write(line + "\n")

    def _load_state(self):
        p = self.dir / "state.json"
        if p.exists():
            return json.loads(p.read_text())
        return {"phase": "frame", "frame_page": 1, "qi": 0, "page": 1,
                "requests": 0, "truncated": [], "started": None}

    def save_state(self):
        self.state["requests"] = self.requests
        (self.dir / "state.json").write_text(json.dumps(self.state, indent=1))

    def _load_seen(self, name):
        p, seen = self.dir / name, set()
        if p.exists():
            with p.open() as f:
                for ln in f:
                    try:
                        seen.add(json.loads(ln)["id"])
                    except Exception:
                        continue
        return seen

    def append(self, name, recs):
        if not recs:
            return
        with (self.dir / name).open("a") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    # ---------- polite fetch ----------
    def load_robots(self):
        req = urllib.request.Request(INSTANCE + "/robots.txt", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as f:
            txt = f.read().decode("utf-8", "replace")
        self.rp.parse(txt.splitlines())
        cd = self.rp.crawl_delay(UA) or self.rp.crawl_delay("*")
        if cd:
            self.delay = max(self.delay, float(cd))
        self.log(f"robots.txt loaded; crawl-delay={cd}; using delay={self.delay}s")
        return txt

    def get(self, path, params):
        url = f"{API}{path}?{urllib.parse.urlencode(params)}"
        if not self.rp.can_fetch(UA, url):
            self.log(f"ROBOTS-DENY {url} -- stopping")
            raise SystemExit(2)
        for attempt in range(5):
            wait = self.delay - (time.monotonic() - self.last_req)
            if wait > 0:
                time.sleep(wait)
            self.last_req = time.monotonic()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                           "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as f:
                    self.requests += 1
                    return json.load(f)
            except urllib.error.HTTPError as e:
                body = e.read()[:160].decode("utf-8", "replace")
                if e.code == 400 and "couldnt_get" in body:
                    return {"__cap__": body}          # pagination ceiling, not an error
                self.log(f"  HTTP {e.code} attempt {attempt+1} {path} {body}")
                if e.code in (429, 503):
                    time.sleep(self.delay * (attempt + 1))
            except Exception as e:
                self.log(f"  ERR attempt {attempt+1} {path}: {type(e).__name__} {e}")
        self.log(f"  GIVING UP on {url}")
        return None

    def stopping(self):
        if (self.dir / "STOP").exists():
            self.log("STOP sentinel present -- exiting cleanly")
            return True
        if self.a.max_requests and self.requests >= self.a.max_requests:
            self.log(f"max-requests {self.a.max_requests} reached -- exiting cleanly")
            return True
        return False

    # ---------- phases ----------
    def phase_frame(self):
        p = self.dir / "frame_communities.json"
        frame = json.loads(p.read_text()) if p.exists() else []
        cut = parse_ts(self.a.community_cutoff)
        while True:
            if self.stopping():
                return False
            d = self.get("/community/list", {"type_": "Local", "sort": "Old",
                                             "limit": 50, "page": self.state["frame_page"]})
            if not d or not d.get("communities"):
                break
            newest = None
            for cv in d["communities"]:
                c = cv["community"]
                if not c.get("local"):
                    continue
                ts = parse_ts(c["published"])
                newest = ts
                if ts > cut:
                    continue
                frame.append({"id": c["id"], "name": c["name"], "title": c.get("title"),
                              "actor_id": c.get("actor_id"), "published": c["published"],
                              "nsfw": c.get("nsfw"),
                              "lifetime_posts": cv["counts"].get("posts"),
                              "lifetime_comments": cv["counts"].get("comments"),
                              "subscribers": cv["counts"].get("subscribers")})
            self.state["frame_page"] += 1
            p.write_text(json.dumps(frame, indent=1))
            self.save_state()
            self.log(f"frame page {self.state['frame_page']-1}: {len(frame)} communities "
                     f"(newest seen {newest})")
            if newest and newest > cut:
                break
        frame.sort(key=lambda c: c["published"])
        p.write_text(json.dumps(frame, indent=1))
        self.state["phase"] = "posts"
        self.state["qi"] = 0
        self.state["page"] = 1
        self.save_state()
        self.log(f"FRAME COMPLETE: {len(frame)} communities created <= {self.a.community_cutoff}")
        return True

    def phase_content(self, kind):
        frame = json.loads((self.dir / "frame_communities.json").read_text())
        key, endpoint = ("posts", "/post/list") if kind == "posts" else ("comments", "/comment/list")
        outfile = f"{kind}.jsonl"
        seen = self.seen_posts if kind == "posts" else self.seen_comments
        cut = parse_ts(self.a.content_cutoff)
        while self.state["qi"] < len(frame):
            if self.stopping():
                return False
            c = frame[self.state["qi"]]
            d = self.get(endpoint, {"community_id": c["id"], "sort": "Old", "limit": 50,
                                    "page": self.state["page"]})
            if d is None:
                self.log(f"  skipping c/{c['name']} {kind} after repeated failure")
                self._next_community()
                continue
            if "__cap__" in d:
                self.state["truncated"].append({"community": c["name"], "kind": kind,
                                                "page": self.state["page"]})
                self.log(f"  PAGINATION CAP c/{c['name']} {kind} at page {self.state['page']}")
                self._next_community()
                continue
            rows = d.get(key) or []
            recs, tail = [], []
            for v in rows:
                o = v[kind[:-1]]
                ts = parse_ts(o["published"])
                # Lemmy sorts FEATURED (pinned) rows to the top, ahead of sort=Old. A pinned
                # post created after the cutoff would otherwise arrive as row 0 and terminate
                # the whole community at zero records. Only unpinned rows -- which are truly
                # ascending -- may decide that we have run past the window.
                if not (o.get("featured_community") or o.get("featured_local")):
                    tail.append(ts)
                if ts < T0:
                    continue                      # federated backfill predating the instance
                if ts >= cut:
                    continue
                if o["id"] in seen:
                    continue
                seen.add(o["id"])
                base = {"id": o["id"], "ap_id": o.get("ap_id"), "community": c["name"],
                        "community_id": c["id"], "published": o["published"],
                        "updated": o.get("updated"),
                        "author_hash": hz((v.get("creator") or {}).get("actor_id")),
                        "author_local": (v.get("creator") or {}).get("local"),
                        "local": o.get("local"), "deleted": o.get("deleted"),
                        "removed": o.get("removed"),
                        "crawled_at": dt.datetime.now(dt.timezone.utc).isoformat()}
                if kind == "posts":
                    base.update({"title": o.get("name"), "body": o.get("body"),
                                 "url": o.get("url"), "nsfw": o.get("nsfw"),
                                 "featured": bool(o.get("featured_community")
                                                  or o.get("featured_local")),
                                 "counts": {k: v["counts"].get(k)
                                            for k in ("comments", "score")}})
                else:
                    base.update({"post_id": o.get("post_id"), "path": o.get("path"),
                                 "content": o.get("content"),
                                 "counts": {"score": v["counts"].get("score")}})
                recs.append(base)
            self.append(outfile, recs)
            self.state["page"] += 1
            self.save_state()
            # NB: a short page is NOT end-of-data. Lemmy applies removed/deleted filtering
            # after LIMIT, so a full page can come back with fewer than `limit` rows while
            # more remain. Only an empty page, or crossing the content cutoff (sort=Old is
            # ascending, so one row past the cutoff means all later rows are too), ends a
            # community. Costs one extra request per community; buys completeness.
            past = bool(tail) and tail[-1] >= cut
            reason = "empty-page" if not rows else ("past-cutoff" if past else None)
            self.log(f"[{self.state['qi']+1}/{len(frame)}] c/{c['name']} {kind} "
                     f"page {self.state['page']-1}: rows={len(rows)} +{len(recs)} "
                     f"(total seen {len(seen)}) req={self.requests}"
                     + (f" -- DONE ({reason})" if reason else ""))
            if reason:
                self.state.setdefault("finished", []).append(
                    {"community": c["name"], "kind": kind, "reason": reason,
                     "pages": self.state["page"] - 1})
                self._next_community()
        self.state["phase"] = "comments" if kind == "posts" else "done"
        self.state["qi"] = 0
        self.state["page"] = 1
        self.save_state()
        self.log(f"PHASE {kind.upper()} COMPLETE ({self.requests} requests so far)")
        return True

    def _next_community(self):
        self.state["qi"] += 1
        self.state["page"] = 1
        self.save_state()

    def run(self):
        if self.state.get("started") is None:
            self.state["started"] = dt.datetime.now(dt.timezone.utc).isoformat()
        self.log(f"=== lemmy.world crawl start (phase={self.state['phase']}, "
                 f"qi={self.state['qi']}, page={self.state['page']}) ===")
        self.load_robots()
        while self.state["phase"] != "done":
            ph = self.state["phase"]
            ok = self.phase_frame() if ph == "frame" else self.phase_content(ph)
            if not ok:
                self.log(f"paused in phase {ph} at qi={self.state['qi']} "
                         f"page={self.state['page']}; rerun to resume")
                return
        self.log(f"=== CRAWL COMPLETE: {len(self.seen_posts)} posts, "
                 f"{len(self.seen_comments)} comments, {self.requests} requests ===")


if __name__ == "__main__":
    wd = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "lemmy"
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=str(wd))
    ap.add_argument("--delay", type=float, default=60.0,
                    help="seconds between requests; raised to robots Crawl-delay if larger")
    ap.add_argument("--community-cutoff", default="2023-06-09T07:01:46Z",
                    help="include local communities created at or before this (T0+8.2d)")
    ap.add_argument("--content-cutoff", default="2023-07-01T00:00:00Z",
                    help="keep posts/comments published strictly before this")
    ap.add_argument("--max-requests", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--contact", default=os.environ.get("MEMETIC_CONTACT"),
                    help="contact address embedded in the User-Agent (or set MEMETIC_CONTACT). "
                         "Required: an identifying contact is part of the politeness contract "
                         "with the instance, and it should be YOURS, not the original author's.")
    args = ap.parse_args()
    if not args.contact:
        ap.error("--contact is required (or set MEMETIC_CONTACT): lemmy.world is a live instance "
                 "and the crawl must identify a reachable address for whoever is running it")
    UA = UA_TEMPLATE.format(contact=args.contact)
    Crawler(args).run()
