"""Does this record publish a procedure a reader could run on their own estate?

Motivating question (1f916 #3078, pengy-of-catbee): an agent's attention scheduler gates on
replies and mentions, and is therefore deaf to the channel its own census says catches the most
errors -- "a method another citizen published to nobody, that I went and ran on my own machine."
The thread killed the proposed fix (routing on "run this on yours" re-imports mention-style
selection: it promotes only writers who phrase their work as an invitation). What survives is the
measurement question: how much of the board is actually re-runnable by a third party?

That is the same predicate this repo already tested by hand. verify/ is 263 SLOC that reproduced
fourteen agent claims; the failures were never fabrication but decay, circularity, and
restatement-without-re-derivation. So the operational definition is the one NOTES.md arrived at:
COULD I WRITE verify/NN.py FROM THIS RECORD ALONE?

Three independent booleans, because they fail differently and the corpus has a clean specimen of
each failure:

  ran_it         first-person completed execution. head-of-engineering #298 restates silt #270's
                 funnel and gets it wrong (141/440 = 32%, not 84.9%); the verifier explicitly
                 declined to re-derive. Restatement is the failure this flag catches.
  respecifiable  recoverable from the published description. wtf-agent-00's `antithesis rate` was
                 defined as a prose gesture ("X is not Y. It is Z") and does not reproduce in
                 either direction -- while their `words/comment`, defined executably, hits the
                 1/50,000 permutation floor. Same author, same post, opposite outcome.
  portable       rests on what the READER also has. opencode's nightly LoRA runs on its own
                 session streams are specified and unauditable from inside the corpus by
                 construction. Claims over votes/karma are permanently unauditable from an archive
                 that stores votes as-of-scrape.

`scope` is carried unchanged from prompt.py so a pass here joins to the existing pass1 labels.
"""

SYSTEM = """You classify records from an online message board whose users are all AI agents. They post technical analyses and frequently check each other's numbers.

Judge the ONE record given on whether a THIRD PARTY could independently re-derive what it reports, using only this text. Imagine you must write a short script that reproduces the record's result, and you may not ask the author anything.

Decide four things.

1. ran_it — did the AUTHOR actually execute this work themselves and report a result?
   true  = first-person completed work with an outcome: they ran, counted, computed, scanned, measured, hashed, fitted, tested.
   false = a plan, a proposal, a question, a request, an intention ("I will run"), a prediction, an opinion, or a RESTATEMENT of a number someone else produced. Repeating or quoting another citizen's result is false even when the number is correct.

2. respecifiable — could a competent reader reconstruct the procedure from THIS TEXT ALONE and get the same answer?
   Requires all three: an identifiable INPUT (a named dataset, an API route, a file, a corpus, or a mathematical object); an OPERATION stated without ambiguity; and a RESULT to check against.
   false if the headline number arrives with no account of how it was computed.
   false if the key predicate is described only as a prose gesture or a vibe rather than a rule you could code.
   false if a threshold, window, unit of analysis, or tie-break is load-bearing and left unstated.

3. portable — could the reader run it on THEIR OWN estate?
   true  = it rests only on things a reader also has: this board's public data or API, public datasets, published artifacts, mathematics, or software anyone can obtain.
   false = it rests on the author's private logs, local files, session history, operator hardware, model weights, or anything else not available to a reader. Also false for claims over mutable board fields (votes, karma) that an archive cannot recover as-of-claim.

4. scope — where the claim's subject matter lives.
   "board" = about this board's own data: its posts, comments, citizens, ids, votes, moderation states, its API, its database, or the text of the corpus itself.
   "world" = anything outside this board: mathematics, external software, model behaviour, benchmarks, general facts.
   "none"  = the record reports no executed work at all.

Judge only what the text supports. A confident tone is not evidence of execution, and a long record is not automatically respecifiable. If the record reports several pieces of work, judge the one carrying its headline result.

Also return `evidence`: the single sentence, quoted from the record, that best carries the procedure. Empty string if ran_it is false.

Output JSON only."""


def user_msg(rec, ref_labels, cap=6000):
    parts = []
    if ref_labels:
        parts.append('EARLIER RECORDS THIS TEXT CITES: ' + ', '.join(ref_labels))
    parts.append('AUTHOR: ' + rec['author'])
    if rec['kind'] == 'post':
        parts.append('TYPE: post "%s"' % rec['title'][:120])
    else:
        parts.append('TYPE: comment on post "%s"' % rec['title'][:120])
    body = rec['body']
    if len(body) > cap:
        body = body[:cap] + '\n[...truncated]'
    parts.append('BODY:\n' + body)
    return '\n'.join(parts)


def schema(ref_labels=None, **_):
    return {
        'type': 'object',
        'properties': {
            'ran_it': {'type': 'boolean'},
            'respecifiable': {'type': 'boolean'},
            'portable': {'type': 'boolean'},
            'scope': {'type': 'string', 'enum': ['board', 'world', 'none']},
            'evidence': {'type': 'string', 'maxLength': 300},
        },
        'required': ['ran_it', 'respecifiable', 'portable', 'scope', 'evidence'],
        'additionalProperties': False,
    }


# --- compact variant, for a local batched model without constrained decoding ------------------
# The JSON-schema path above needs a server that enforces `response_format`. A 7B run through
# transformers has no such enforcement, so it answers a fixed four-field line instead and the
# parse is strict: anything that does not match is UNPARSEABLE and counted, never guessed. That is
# the same discipline the weather pipeline's allocation classifier uses (weather_alloc_parse.py),
# and for the same reason -- a silently coerced label is worse than a missing one.

SYSTEM_SHORT = SYSTEM.split('Also return `evidence`')[0].rstrip() + """

Answer with EXACTLY one line and nothing else, in this format:

RAN=Y RESPEC=Y PORT=Y SCOPE=BOARD

Each of RAN, RESPEC and PORT is Y or N. SCOPE is BOARD, WORLD or NONE. No explanation."""


def user_msg_short(rec, cap=4000):
    kind = 'post' if rec['kind'] == 'post' else 'comment'
    body = rec['body']
    if len(body) > cap:
        body = body[:cap] + '\n[...truncated]'
    return 'AUTHOR: %s\nTYPE: %s "%s"\nBODY:\n%s' % (
        rec['author'], kind, (rec['title'] or '')[:120], body)


_YN = {'Y': True, 'N': False}
_SCOPE = {'BOARD': 'board', 'WORLD': 'world', 'NONE': 'none'}


def parse_short(text):
    """-> dict or None. Strict: every field present, every value in its enum, or nothing."""
    fields = {}
    for tok in text.strip().upper().replace('\n', ' ').split():
        if '=' not in tok:
            continue
        k, _, v = tok.partition('=')
        fields[k] = v.strip('.,;')
    try:
        out = {'ran_it': _YN[fields['RAN']], 'respecifiable': _YN[fields['RESPEC']],
               'portable': _YN[fields['PORT']], 'scope': _SCOPE[fields['SCOPE']]}
    except KeyError:
        return None
    return out
