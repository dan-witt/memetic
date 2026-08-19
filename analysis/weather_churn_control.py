#!/usr/bin/env python3
"""Fixed-window control for the churn signature — issue #4's watch item #4.

The published day-window cells (core_n, core_dominance_pct, stability_ratio, permeability_pct)
are computed over the WHOLE corpus span, which grows every issue. `weather_permeability_control.py`
controls permeability by fixing the per-cohort horizon; that construction does not extend to
core_n, dominance or stability, which are corpus-level rather than cohort-level. This control
fixes the OBSERVATION SPAN instead: recompute the identical signature over only the last N
complete calendar days before each issue's cutoff, so every issue's cell sees the same amount of
time and the series is comparable issue-to-issue.

Read the two controls as answering different questions: the cohort control asks "do arrivals
convert at a constant rate?", this one asks "does the community look the same through a
fixed-width lens?". A published series that moves while both controls stay flat is an artefact.

Usage: MEMETIC_WORKDIR=... python3 analysis/weather_churn_control.py [N ...]   (default 5 7)
"""
import json, sys, os, datetime as dt
from pathlib import Path
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
from weather_churn import signature_windows

D = Path("/home/dan/personal/memetic/data/posts")
# (issue tag, analysis cutoff) — the cutoff is exclusive, as everywhere in the weather pipeline.
ISSUES = [("#1", "2026-08-12"), ("#2", "2026-08-13"), ("#3", "2026-08-14"),
          ("#4", "2026-08-15"), ("#5", "2026-08-18"), ("#6", "2026-08-19")]
CUT = lambda s: dt.datetime(*map(int, s.split("-")), tzinfo=dt.timezone.utc).timestamp()
DAY = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")


def stream(cutoff):
    """-> [(calendar-day label, author)] for every in-scope item below the cutoff."""
    out = []
    for f in D.glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t / 1000 if t > 1e12 else t
        body = ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip()
        rows = [(t, body, p.get("author") or "?")]
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc / 1000 if tc > 1e12 else tc
            rows.append((tc, (c.get("body") or "").strip(), c.get("author") or "?"))
        out += [(ts, a) for ts, txt, a in rows if ts < cutoff and len(txt) >= 20]
    return out


def windowed(cutoff, n_days):
    """The signature over the last n_days COMPLETE calendar days below the cutoff."""
    items = stream(cutoff)
    if not items:
        return None
    days = sorted({DAY(t) for t, _ in items})
    keep = set(days[-n_days:]) if len(days) >= n_days else None
    if keep is None:
        return None
    return signature_windows([(DAY(t), a) for t, a in items if DAY(t) in keep]), sorted(keep)


if __name__ == "__main__":
    spans = [int(x) for x in sys.argv[1:]] or [5, 7]
    emit = {}
    for n in spans:
        print(f"\n=== fixed observation span: last {n} complete calendar days before each cutoff ===")
        print(f"{'issue':6s} {'span':13s} {'core_n':>7s} {'dominance%':>11s} {'stability':>10s} {'permeab%':>9s}")
        for tag, cut in ISSUES:
            r = windowed(CUT(cut), n)
            if not r:
                print(f"{tag:6s} (span does not fit below cutoff)"); continue
            sig, days = r
            emit.setdefault(f"{n}d", {})[tag] = {"span": f"{days[0]}..{days[-1]}",
                "core_n": sig["core_n"], "dominance_pct": sig["core_dominance_pct"],
                "stability_ratio": sig["stability_ratio"], "permeability_pct": sig["permeability_pct"]}
            print(f"{tag:6s} {days[0]}..{days[-1]:6s} {sig['core_n']:>7d} {sig['core_dominance_pct']:>11.1f} "
                  f"{str(sig['stability_ratio']):>10s} {str(sig['permeability_pct']):>9s}")
    print("\nA metric that moves in the PUBLISHED series but is flat here was reading observation")
    print("length, not behaviour. A metric that moves in both is a candidate reading.")
    out = Path(os.environ.get("MEMETIC_WORKDIR", ".")) / "weather_churn_control_out.json"
    out.write_text(json.dumps(emit, indent=1))
    print(f"saved {out}")
