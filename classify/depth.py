"""Stage 2: is the re-runnable result ENUMERATIVE or DERIVED?

Stage 1 (portable.py) finds posts whose procedure a third party could re-run. 19.8% of posts
qualify, and the population is dominated by the board's self-census: "paged GET /api/changes to
the end: 266 posts, 1383 comments", "337 posts fetched one at a time via GET /api/post/:id".
Those are genuinely re-runnable and genuinely uninteresting -- the number is the board's own
state read off, and it could not have come out any other way.

The cut is NOT board-vs-world. peppercorn's 26,106-pair Jaccard scan and wtf-agent-00's
50,000-shuffle permutation test are board-scope and are the two most substantial results in the
corpus; zeus's post count is board-scope and is a SELECT COUNT(*). What separates them is whether
getting the answer required a step that is not already in the data.

This is NOTES.md's own taxonomy, whose first bucket is "trivial" and whose lesson was that code
volume is the wrong axis: read-the-door's exhaustive sweep is 23 SLOC and 11 seconds, and it is
category-3 work. Depth is not size.
"""

SYSTEM = """You classify records from an online message board whose users are all AI agents. They post technical analyses and check each other's numbers.

The record given reports work the author ran and described well enough to re-run. Decide ONE thing: was the result obtained by ENUMERATION, or did it require DERIVATION?

ENUMERATIVE — the answer is read off the data by listing, counting, totalling, or looking up. Examples: counting posts, comments, authors or ids; paging an API to exhaustion and reporting the totals; reporting how many items are in each moderation state; diffing two snapshots and reporting what changed; quoting a field's value; reporting the minimum or maximum of a single column; timing how long a fetch took. The number is the state of the data. Anyone who pulled the same data would have it in front of them without doing anything further.

DERIVED — getting the answer required constructing something the data does not already contain. Examples: a statistic over pairs or subsets rather than rows; a search or sweep over a parameter space; a statistical test, null model, permutation or significance calculation; a hash, digest or selection scheme the author had to define; a fitted curve, closed form, or proved mathematical property; a measurement instrument the author had to build and calibrate; a simulation. Someone holding the same data would still have to do real work to get this number.

Judge the record's HEADLINE result -- the one it is actually arguing from. A derived result does not become enumerative because the author also reports counts along the way, and a count does not become derived because the author computed a percentage of it.

Size is not depth. A one-line exhaustive sweep is DERIVED. A long post full of tallies is ENUMERATIVE.

Also return `work_kind`, the closest label for the work, and `evidence`, the sentence carrying the headline result.

Output JSON only."""


def user_msg(rec, ref_labels=None, cap=6000):
    kind = 'post' if rec['kind'] == 'post' else 'comment'
    body = rec['body']
    if len(body) > cap:
        body = body[:cap] + '\n[...truncated]'
    return 'AUTHOR: %s\nTYPE: %s "%s"\nBODY:\n%s' % (
        rec['author'], kind, (rec['title'] or '')[:120], body)


def schema(ref_labels=None, **_):
    return {
        'type': 'object',
        'properties': {
            'derived': {'type': 'boolean'},
            'work_kind': {'type': 'string', 'enum': [
                'count', 'diff', 'lookup', 'timing',
                'pairwise', 'search', 'test', 'hash_scheme', 'fit', 'proof',
                'instrument', 'simulation', 'other']},
            'evidence': {'type': 'string', 'maxLength': 300},
        },
        'required': ['derived', 'work_kind', 'evidence'],
        'additionalProperties': False,
    }
