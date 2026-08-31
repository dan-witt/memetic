"""One call, for a scheduler: is this post worth waking a full model to read?

1f916 #3078 (pengy-of-catbee): an agent's Tier-1 heartbeat gates on replies, mentions and "8+ new
posts", so it is structurally deaf to the channel its own census says catches the most errors --
"a method another citizen published to nobody, that I went and ran on my own machine". No sender,
no inbox.

The three-stage pipeline in this directory answers that question at ~0.5-1.0 rec/s per stage and
needs two passes plus a cascade. A scheduler wants one call. This collapses stage 1's
`respecifiable` (the only field that carried signal) and stage 2's `derived` (the only field that
excluded the self-census) into a single forward pass, and computes the verdict as their AND rather
than asking the model for a third judgment it would answer inconsistently.

The two are kept separate rather than merged into one question because they fail differently and
the corpus has a clean specimen of each: head-of-engineering #298 restates someone else's funnel
and gets it wrong (not runnable); zeus's "266 posts, 1383 comments" is perfectly runnable and
entirely a headcount (not derived).
"""

SYSTEM = """You read a post from an online message board whose users are all AI agents. They post technical analyses and check each other's numbers.

You are the cheap gate in front of an expensive reader. Decide whether this post is worth waking that reader for. Answer two questions.

1. runnable — did the author actually run something themselves, and describe it well enough that YOU could reproduce it from this text alone?
   Requires all of: first-person completed work with a result (not a plan, a proposal, a question, an intention, or a restatement of someone else's number); an identifiable INPUT you could obtain (a named dataset, an API route, a file, a corpus, a mathematical object); an OPERATION stated without ambiguity; and a RESULT to check against.
   false if the headline number arrives with no account of how it was computed.
   false if the load-bearing predicate is described as a prose gesture rather than a rule you could code.
   false if a threshold, window, unit of analysis or tie-break matters and is left unstated.
   Ask yourself literally: could I write the script from this post, with no further questions?

2. derived — was the result obtained by ENUMERATION, or did it require DERIVATION?
   false (enumeration) — the answer is read off the data by listing, counting, totalling, timing or looking up: how many posts, comments, authors or ids; paging an API to exhaustion and reporting totals; how many items are in each moderation state; diffing two snapshots; quoting a field's value.
   true (derivation) — getting the answer required constructing something the data does not already contain: a statistic over pairs or subsets rather than rows; a search or sweep over a parameter space; a statistical test, null model or permutation; a hash, digest or selection scheme the author defined; a fitted curve, closed form or proved property; an instrument the author had to build and calibrate; a simulation.

Size is not depth. A one-line exhaustive sweep is derived. A long post full of tallies is not.

Judge the post's headline result, not its asides. Also return `procedure`: one line naming what a reader would actually run, or an empty string if runnable is false.

Output JSON only."""


def user_msg(rec, ref_labels=None, cap=4000):
    body = rec['body']
    if len(body) > cap:
        body = body[:cap] + '\n[...truncated]'
    return 'AUTHOR: %s\nTITLE: %s\nBODY:\n%s' % (
        rec['author'], (rec['title'] or '')[:120], body)


def schema(ref_labels=None, **_):
    return {
        'type': 'object',
        'properties': {
            'runnable': {'type': 'boolean'},
            'derived': {'type': 'boolean'},
            'procedure': {'type': 'string', 'maxLength': 160},
        },
        'required': ['runnable', 'derived', 'procedure'],
        'additionalProperties': False,
    }
