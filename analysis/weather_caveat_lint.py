#!/usr/bin/env python3
"""Keep the caveats block a caveats block.

Across issues #1-#13 the caveat block grew 24x (110 -> 2,632 words) while the report body grew 10x,
taking it from 13% of the issue to 31%. The mechanism is not that the series acquired 24x more
limitations: it is that each issue's FINDINGS were appended to the block as a permanent record, so
the block became a second copy of the report. A caveat that restates a reading is not a caveat.

THE RULE THIS ENFORCES: a caveat earns its place only if it changes how a number should be READ.
If it says what a number IS, it is a reading and belongs in the body.

Three checks, all objective -- no judgement about prose is automated here:

  duplicate    the caveat's content words substantially overlap one body paragraph. That is the
               shadow-copy failure, and it is measurable.
  carried      the caveat is near-identical to one in the previous issue. Carried caveats are
               fine (a permanent limitation IS permanent) but they should be short and stated
               once, not re-argued at length every issue.
  parity       results.json's caveat list and the report's method-notes list must match. They
               drifted to 39 vs 43 by issue #13, so the two files were saying different things.

Usage:
  python3 analysis/weather_caveat_lint.py                      # newest issue vs its predecessor
  python3 analysis/weather_caveat_lint.py 2026-08-25           # a specific issue
  python3 analysis/weather_caveat_lint.py --history            # the growth series
"""
import json, sys
from pathlib import Path

WEATHER = Path(__file__).resolve().parent.parent / "results" / "weather"
HEADING = "## Method notes"
STOP = set("the a an and or of to in on is are was were be been it its this that these those for "
           "with as at by from not no than then so if but which what when where who whom whose "
           "we our us you your they their them he she his her i me my one two three four five "
           "have has had do does did can could would should may might must will shall".split())


def issues(root=WEATHER):
    return sorted(q for q in Path(root).glob("20*-*-*") if (q / "results.json").exists())


def split_report(path):
    """-> (body, caveats) text. The caveats block is the method-notes heading to end of file."""
    txt = Path(path).read_text()
    i = txt.find(HEADING)
    return (txt, "") if i < 0 else (txt[:i], txt[i:])


def md_caveats(caveat_text):
    """The '- ' bullets of the method-notes block, unwrapped."""
    out, cur = [], None
    for line in caveat_text.splitlines():
        s = line.strip()
        if s.startswith("- "):
            if cur:
                out.append(" ".join(cur))
            cur = [s[2:]]
        elif cur is not None and s:
            cur.append(s)
        elif cur:
            out.append(" ".join(cur)); cur = None
    if cur:
        out.append(" ".join(cur))
    return out


def words(s):
    """Content words, lowercased, punctuation-stripped, stop-words dropped."""
    out = []
    for w in s.lower().split():
        w = "".join(c for c in w if c.isalnum() or c in ".-%")
        if w and w not in STOP and len(w) > 1:
            out.append(w)
    return out


def overlap(a, b):
    """Fraction of a's distinct content words that also appear in b."""
    A, B = set(words(a)), set(words(b))
    return len(A & B) / len(A) if A else 0.0


def paragraphs(body):
    return [p for p in body.split("\n\n") if len(p.split()) >= 25]


def lint(issue_dir, prev_dir=None, dup_at=0.62, carry_at=0.85):
    res = json.load(open(issue_dir / "results.json"))
    cav_json = [str(c) for c in (res.get("caveats") or [])]
    body, cav_text = split_report(issue_dir / "report.md")
    cav_md = md_caveats(cav_text)
    paras = paragraphs(body)
    prev_json = []
    if prev_dir:
        prev_json = [str(c) for c in (json.load(open(prev_dir / "results.json")).get("caveats") or [])]

    bw, cw = len(body.split()), len(cav_text.split())
    total = bw + cw
    print(f"=== {issue_dir.name} ===")
    print(f"  report {total} words; caveats {cw} ({100*cw/total:.1f}%); "
          f"{len(cav_json)} in results.json, {len(cav_md)} in report.md")
    if len(cav_json) != len(cav_md):
        print(f"  [PARITY] the two files disagree: {len(cav_json)} vs {len(cav_md)}")

    dup, carried, keep = [], [], []
    for c in cav_json:
        best = max((overlap(c, p) for p in paras), default=0.0)
        prev_best = max((overlap(c, p) for p in prev_json), default=0.0)
        if best >= dup_at:
            dup.append((best, c))
        elif prev_best >= carry_at:
            carried.append((prev_best, c))
        else:
            keep.append(c)

    jw = sum(len(c.split()) for c in cav_json)          # the json list, the base for the cut
    dw = sum(len(c.split()) for _, c in dup)
    print(f"  [DUPLICATE] {len(dup)} of {len(cav_json)} caveat(s), {dw} of {jw} list words "
          f"({100*dw/jw:.0f}%), restate a body paragraph (>= {dup_at:.0%} content-word overlap)")
    for s, c in sorted(dup, reverse=True):
        print(f"      {s:.0%}  {c[:96]}")
    print(f"  [CARRIED]   {len(carried)} caveat(s) near-identical to the previous issue's")
    for s, c in sorted(carried, reverse=True):
        print(f"      {s:.0%}  {c[:96]}")
    print(f"  [KEEP]      {len(keep)} caveat(s), {sum(len(c.split()) for c in keep)} words")
    if dw:
        # Both figures are on the json list; the rendered md block differs slightly in wording.
        print(f"  removing the duplicates: caveat list {jw} -> {jw-dw} words, and the issue's "
              f"caveat share falls from {100*cw/total:.1f}% to about "
              f"{100*(cw-dw)/(total-dw):.1f}%")
    return {"issue": issue_dir.name, "caveat_words": cw, "caveat_pct": round(100*cw/total, 1),
            "n_json": len(cav_json), "n_md": len(cav_md), "duplicate": len(dup),
            "duplicate_words": dw, "carried": len(carried), "keep": len(keep)}


def history():
    print(f"{'issue':12s} {'report_w':>9s} {'caveat_w':>9s} {'caveat%':>8s} {'n':>4s}")
    for q in issues():
        body, cav = split_report(q / "report.md")
        bw, cw = len(body.split()), len(cav.split())
        n = len(json.load(open(q / "results.json")).get("caveats") or [])
        print(f"{q.name:12s} {bw+cw:9d} {cw:9d} {100*cw/(bw+cw):7.1f}% {n:4d}")


if __name__ == "__main__":
    if "--history" in sys.argv:
        history(); sys.exit(0)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    qs = issues()
    cur = WEATHER / args[0] if args else qs[-1]
    prev = next((q for q in reversed(qs) if q.name < cur.name), None)
    lint(cur, prev)
