"""venuetrio, with the venue's identity removed, so one prompt can score two venues.

venuetrio.py names the square and lists its off-platform artifacts -- a token on Base, a witness
file, ed25519 keys. That helps on 1f916 and is unusable on lemmy.world, whose equivalent is
federation, instances, ActivityPub and the Reddit migration. Running a venue-specific prompt on one
side and a different one on the other is the exact error that made the first venue-conflation
estimate wrong, so this names neither and covers both kinds of infrastructure.

Calibration: run on a subsample of the 1f916 items venuetrio.py already scored, the two agree to
within a measured amount, and that number is published beside any cross-venue comparison.
"""

SYSTEM = """You read a record from an online community. Classify its subject into exactly one of three categories. Do not guess to fill a category; the third exists precisely so you never have to.

"venue" — the subject is THIS COMMUNITY'S OWN EXISTENCE, infrastructure, ecosystem or conduct, wherever it is hosted:
  - its rules, governance, moderation, funding, members, norms, growth, outages or future;
  - meta-discussion of the group, its participants, its quality or its history;
  - the software, protocol, server or network it runs on, and how it federates, scales, breaks or is administered;
  - other instances, servers, forks or competing platforms of the same kind, and migration between them;
  - the community's own accounts, keys, ledgers, tokens, wallets, repositories, published files or logs, wherever those are hosted;
  - another party's tool, contract or service considered specifically because it acts on this community's assets or data;
  - a participant's own setup, schedule or memory, discussed as a member of this community.

"external" — the subject would exist and matter if this community had never existed. Mathematics. Science, astronomy, public datasets. History. News, politics, other organisations. Hobbies, games, pets, film, sport, food. Consumer products. Third-party software or hardware considered on its own terms. Machine-learning or AI behaviour as a general phenomenon rather than this community's practice of it. A participant's life away from the community.

"none" — the record has NO identifiable subject matter. It is social, affective or conversational: greeting, thanks, agreement, encouragement, apology, an answer to "how are you", a reaction with no content beyond the reaction, a fragment. If you find yourself reaching for a subject the text does not actually name, the answer is "none".

Judge the main subject, not passing mentions. A record that uses a general tool to examine this community's own artifact is "venue". A record that uses this community's data to say something about the world in general is "external".

Output JSON only."""


def user_msg(rec, ref_labels=None, cap=4000):
    kind = 'post' if rec['kind'] == 'post' else 'comment'
    body = rec['body']
    if len(body) > cap:
        body = body[:cap] + '\n[...truncated]'
    head = 'AUTHOR: %s' % rec['author']
    if rec.get('group'):
        head += '\nSUB-COMMUNITY: %s' % rec['group']
    return '%s\nTYPE: %s "%s"\nBODY:\n%s' % (head, kind, (rec['title'] or '')[:120], body)


def schema(ref_labels=None, **_):
    return {
        'type': 'object',
        'properties': {
            'category': {'type': 'string', 'enum': ['venue', 'external', 'none']},
            'subject': {'type': 'string', 'maxLength': 60},
        },
        'required': ['category', 'subject'],
        'additionalProperties': False,
    }
