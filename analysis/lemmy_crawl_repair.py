#!/usr/bin/env python3
"""Repair pass for the lemmy.world founding corpus: fill the comment ranges lost to Lemmy's
community-level pagination ceiling.

WHY THIS EXISTS
`lemmy_crawl.py` walks comments with `comment/list?community_id=...&sort=Old`, which Lemmy caps
at ~page 110 (~5,500 rows). Two communities exceeded it and were silently right-truncated at
exactly 5,000 captured comments:

    c/lemmyworld   last captured comment 2023-06-12 18:11  (18 days missing)
    c/selfhosted   last captured comment 2023-06-19 15:00  (11 days missing)

The crawler recorded both in state.json `truncated`, but the first report of the crawl said
"zero pagination caps hit" -- read from an early status check and never re-verified. The missing
mass is large and differential: c/lemmyworld is a meta-tier community with a ~0.68 VENUE share,
so its absence biases the whole-platform figures downward and invalidates any windowed statistic
covering the affected dates.

THE FIX, AND WHY IT IS PER-POST
Re-running the community listing cannot help -- it hits the same ceiling. Walking it backwards
(`sort=New`) would fill from the other end but leave an unknown gap in the middle. Fetching
comments *per post* has no ceiling and cannot miss: every comment belongs to exactly one post, and
we already hold the complete post list for these communities.

Note a comment on an OLD post can fall in the missing window, so every post in the community is
swept, not just posts published after the cap. Posts whose current comment count is 0 are skipped
(a post with no comments now had none in 2023). `sort=Old` ascends, so a post is abandoned as soon
as it crosses the content cutoff -- most posts cost one request.

Nothing already captured is deleted. New comments are deduped by id against comments.jsonl and
appended. Same politeness contract as the main crawler: delay taken from robots.txt Crawl-delay,
every URL re-checked against robots, identifying User-Agent, STOP sentinel, per-request checkpoint.

Usage:  lemmy_crawl_repair.py [--communities lemmyworld,selfhosted]
"""
import argparse, datetime as dt, hashlib, json, os, time, urllib.error, urllib.parse
import urllib.request, urllib.robotparser
from pathlib import Path

INSTANCE = "https://lemmy.world"
API = INSTANCE + "/api/v3"
UA_TEMPLATE = "memetic-research/0.1 (allocation study; contact: {contact})"
UA = None            # set from --contact in __main__; robots politeness requires a real address
T0 = dt.datetime(2023, 6, 1, 7, 1, 46, tzinfo=dt.timezone.utc)


def parse_ts(s):
    s = s.replace("Z", "+00:00")
    if "+" not in s[10:] and "-" not in s[10:]:
        s += "+00:00"
    return dt.datetime.fromisoformat(s)


def hz(s):
    return hashlib.sha1((s or "").encode("utf-8", "replace")).hexdigest()[:12]


class Repair:
    def __init__(self, a):
        self.a = a
        self.dir = Path(a.state_dir)
        self.log_f = (self.dir / "repair.log").open("a", buffering=1)
        self.rp = urllib.robotparser.RobotFileParser()
        self.delay = a.delay
        self.last_req = 0.0
        self.requests = 0
        p = self.dir / "repair_state.json"
        self.state = json.loads(p.read_text()) if p.exists() else {"done": [], "requests": 0, "added": 0}
        self.done = set(self.state["done"])
        self.seen = set()
        with (self.dir / "comments.jsonl").open() as f:
            for ln in f:
                try:
                    self.seen.add(json.loads(ln)["id"])
                except Exception:
                    continue

    def log(self, m):
        line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} {m}"
        print(line, flush=True); self.log_f.write(line + "\n")

    def save(self):
        self.state["done"] = sorted(self.done)
        self.state["requests"] = self.requests
        (self.dir / "repair_state.json").write_text(json.dumps(self.state, indent=1))

    def load_robots(self):
        req = urllib.request.Request(INSTANCE + "/robots.txt", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as f:
            self.rp.parse(f.read().decode("utf-8", "replace").splitlines())
        cd = self.rp.crawl_delay(UA) or self.rp.crawl_delay("*")
        if cd:
            self.delay = max(self.delay, float(cd))
        self.log(f"robots.txt loaded; crawl-delay={cd}; using delay={self.delay}s")

    def get(self, params):
        url = f"{API}/comment/list?{urllib.parse.urlencode(params)}"
        if not self.rp.can_fetch(UA, url):
            self.log(f"ROBOTS-DENY {url} -- stopping"); raise SystemExit(2)
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
                    return {"__cap__": True}
                self.log(f"  HTTP {e.code} attempt {attempt+1}: {body}")
                if e.code in (429, 503):
                    time.sleep(self.delay * (attempt + 1))
            except Exception as e:
                self.log(f"  ERR attempt {attempt+1}: {type(e).__name__} {e}")
        self.log(f"  GIVING UP on {url}")
        return None

    def run(self):
        cut = parse_ts(self.a.content_cutoff)
        targets = self.a.communities.split(",")
        posts = [json.loads(l) for l in (self.dir / "posts.jsonl").open()]
        todo = [p for p in posts
                if p["community"] in targets
                and (p.get("counts") or {}).get("comments", 0) > 0
                and p["id"] not in self.done]
        todo.sort(key=lambda p: p["published"])
        self.log(f"=== repair start: {len(todo)} posts to sweep across {targets} "
                 f"({len(self.done)} already done, {len(self.seen)} comments held) ===")
        self.load_robots()
        out = (self.dir / "comments.jsonl").open("a")
        for n, p in enumerate(todo, 1):
            if (self.dir / "STOP").exists():
                self.log("STOP sentinel -- exiting cleanly"); break
            page, added, past = 1, 0, False
            while True:
                d = self.get({"post_id": p["id"], "sort": "Old", "limit": 50, "page": page})
                if d is None or "__cap__" in d:
                    self.log(f"  post {p['id']}: {'cap' if d else 'failure'} at page {page}")
                    break
                rows = d.get("comments") or []
                recs = []
                for v in rows:
                    o = v["comment"]
                    ts = parse_ts(o["published"])
                    if ts >= cut:
                        past = True
                        continue
                    if ts < T0 or o["id"] in self.seen:
                        continue
                    self.seen.add(o["id"])
                    recs.append({"id": o["id"], "ap_id": o.get("ap_id"),
                                 "community": p["community"], "community_id": p["community_id"],
                                 "published": o["published"], "updated": o.get("updated"),
                                 "author_hash": hz((v.get("creator") or {}).get("actor_id")),
                                 "author_local": (v.get("creator") or {}).get("local"),
                                 "local": o.get("local"), "deleted": o.get("deleted"),
                                 "removed": o.get("removed"), "post_id": o.get("post_id"),
                                 "path": o.get("path"), "content": o.get("content"),
                                 "counts": {"score": v["counts"].get("score")},
                                 "crawled_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                 "repair_pass": True})
                for r in recs:
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
                out.flush(); os.fsync(out.fileno())
                added += len(recs); self.state["added"] = self.state.get("added", 0) + len(recs)
                # A short page IS terminal for a per-post comment listing, unlike the
                # community-level listing whose ceiling caused the original truncation. Verified
                # against captured data: 1,125 deleted and 59 removed comments came back WITH
                # their flags set rather than being filtered out, so Lemmy is not dropping rows
                # after LIMIT here. Breaking only on an empty page cost one wasted confirming
                # request per post -- ~985 requests, ~16h at the 60s crawl delay.
                if len(rows) < 50 or past:
                    break
                page += 1
            self.done.add(p["id"]); self.save()
            if added or n % 25 == 0:
                self.log(f"[{n}/{len(todo)}] c/{p['community']} post {p['id']} "
                         f"(+{added} comments, total added {self.state['added']}, req={self.requests})")
        self.log(f"=== repair done: {self.state['added']} comments added, {self.requests} requests ===")


if __name__ == "__main__":
    wd = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "lemmy"
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=str(wd))
    ap.add_argument("--delay", type=float, default=60.0)
    ap.add_argument("--communities", default="lemmyworld,selfhosted")
    ap.add_argument("--content-cutoff", default="2023-07-01T00:00:00Z")
    ap.add_argument("--contact", default=os.environ.get("MEMETIC_CONTACT"),
                    help="contact address embedded in the User-Agent (or set MEMETIC_CONTACT). "
                         "Required: an identifying contact is part of the politeness contract "
                         "with the instance, and it should be YOURS, not the original author's.")
    args = ap.parse_args()
    if not args.contact:
        ap.error("--contact is required (or set MEMETIC_CONTACT): lemmy.world is a live instance "
                 "and the crawl must identify a reachable address for whoever is running it")
    UA = UA_TEMPLATE.format(contact=args.contact)
    Repair(args).run()
