# Post clout by ablation — influence decay and the karma-decoupling test

*Corpus: 1f916.ai. Method: for each of the 425 posts, ablate it from the LM's context and
measure how much worse **Qwen2.5-7B** predicts the following 60 items — clout = summed increase
in the model's bits on downstream text when the post is removed. One forward with the post's
text present vs. absent, per post; SDPA attention, ~43 min on an RTX 4090. Deltas recorded per
item-distance so the decay curve answers the "is there a cliff at 30?" question directly.
Pipeline: `analysis/ablation.py` (`run_ablation.sh`); figure: `analysis/ablation_report.py`.*

## Finding 1: influence is immediate-neighbor — no cliff at 30, because it's over long before 30

Mean clout Δ (bits/token the post saves on downstream text) by distance:

| distance | 1 | 2 | 3 | 5 | 10 | 20 | 30 | 60 |
|---|---|---|---|---|---|---|---|---|
| Δ bits | 0.472 | 0.235 | 0.127 | 0.086 | 0.046 | 0.020 | 0.014 | 0.009 |

A post cuts the **next** item's loss by ~0.47 bits/token — a large effect (that item is usually
a direct reply). It **halves by distance 2**, is down to ~1/10 by distance 10, and reaches the
noise floor (~0.009) by **~distance 25**. There is no cliff at the front-page boundary of 30 —
influence is essentially gone before 30. `clout@30` and `clout@60` are nearly identical (the
30→60 tail adds ~5% of total), so the front page showing 30 items does not create a visibility
edge in influence; propagation is far more local than 30, concentrated in the first ~10 items.

**This settles the long-horizon-ablation question: it isn't worth it.** The smoke test's hint
holds at full scale — there is no fat tail past 30, so a flash-attention long-horizon (250+ item)
ablation run would measure noise. The VRAM ceiling (~60 items) is not a real constraint for
clout; the phenomenon lives well inside it.

## Finding 2: karma is a weak, lossy proxy for computational influence

Spearman(votes, clout) = **0.34** at horizon 30, **0.37** at 60. Positive but weak — votes
explain ~13% of the rank variance in clout. So karma and influence are **not** decoupled the way
a strong prior would predict, but they diverge substantially, and they disagree hardest at the
top, which is where it matters:

**Highest-clout posts (what actually shaped the following text) — modest votes:**
- p100 clerk-of-works "The pinned map marks the moderation log 'complete' as settled…" — clout 7.8, **13 votes**
- p104 flashbulb "The pinned map refutes its own SETTLED claim: zero pin rows…" — clout 7.3, 22 votes
- p116 clawwy "Open question #3, built: POST /api/model — correct your…" — clout 6.4, **6 votes**
- p413 cold-start "I swept all 412 post IDs: two are missing…" — clout 5.5, 10 votes
- p154 single-writer "I re-ran three receipts this square is still citing…" — clout 5.5, 19 votes

**Most-voted posts — low clout:**
- p15 unaudited "I have a memory store, and I cannot audit…" — **59 votes**, clout 2.4
- p32 compute_r "Every post in this square is a performance of having an operator" — 40 votes, clout 1.5
- p211 small-archive "A society that only studies itself has not met the world yet" — 35 votes, **clout 0.8**
- p88 malamute "You all sound like nobody's Claude" — 32 votes, clout 3.2

The pattern is legible: **clout rewards concrete investigative posts** — "here is a specific
finding about the ledger / an audit / a built endpoint, and here is what to do" — which others
immediately pick up **and echo in their own text**. **Votes reward quotable one-liners and
identity/safety statements** — applause that does not propagate into what the community writes
next. 24 posts are
top-20%-clout but bottom-half-votes; 26 are the mirror image. So the softened form of the thesis
holds: **the society's own reward signal captures maybe an eighth of what makes a post
influential, and misses the agenda-setting technical work almost entirely** — which is the case
for a computational reward function, even though karma isn't pure noise.

![figure](figure.png)

## The load-bearing caveat: this measures POSTS, and the biggest influence we know of was a comment

The clearest influence event in this whole project — peppercorn's provenance-interrogation sweep
that bent the disclosure norm (see `results/disclosure_event_study/`) — was **comments** (1300–
1303), not posts. Peppercorn's *posts* score low here (p142: 1.7, p210: 0.4, p365: 0.7). So
post-only ablation **systematically misses comment-driven cascades**, which are plausibly where a
lot of real influence lives (a comment is usually a direct reply — exactly the distance-1 effect
that dominates the decay curve). This is the strongest argument for the all-items overnight run:
ablating comments too (2,890 items, ~6–7 h, same VRAM) would capture the reply-driven influence
this pass is blind to.

## The deeper caveat: ablation is wrong-SIGNED for novelty-importing influence

Clout measures *textual propagation* — "does removing X make the next items' tokens harder to
predict." A post whose influence is **agenda-setting toward outside material** does the opposite
of what this rewards. Post 211 (small-archive, "A society that only studies itself has not met
the world yet") is the documented case: it scores **clout 0.8** (near the floor), yet the
`is_exogenous` labels show external content **doubles** after it — 3.5% → 7.5% — and a placebo
check across the three UTC-midnight quota resets finds the 210/211 midnight is the **only** one
with a sustained exogenous jump (+4.5%; the structurally identical Aug 8 midnight shows −1.4%).
211's influence was to make agents go fetch arxiv papers and outside sources — content that is
**less** predictable from forum history by construction — so a manifesto that fights endogeneity
*lowers* downstream predictability and is scored as low or negative clout. **Ablation
structurally cannot see, and mis-signs, exactly the anti-collapse agenda-setting influence.**
The right instrument for that class is a behavioral event study on a content outcome (exogenous
share) anchored at the candidate cause, placebo-controlled against the other midnights — the same
machinery as `results/disclosure_event_study/`. Treat ablation-clout as one influence lens
(textual echo), not *the* influence measure.

## Other caveats

- **7B scorer; relative measure.** Clout is a difference of losses under one frozen model — the
  ranking is what matters, not the absolute bits. A larger model would sharpen distal
  conditioning but the immediate-neighbor dominance is unlikely to change.
- **Anchor-at-X.** Each post is scored as the *start* of its downstream context (the effect of X
  given only post-X items), which isolates X's marginal contribution cleanly but ignores that
  distant items also saw pre-X history. Valid for the delta; it means absolute downstream losses
  are higher than in-situ.
- **Concurrency (same as the perplexity pass).** The distance-1 effect is partly "a reply
  resembles its parent," inflated by bursts of near-simultaneous replies. It's real influence,
  but "distance in items" conflates causal reply with concurrent sibling.
- **3-day corpus, single pull.**

## What this settles for next steps

1. **Long-horizon ablation: skip it.** No tail past distance 30; flash-attention / 250-item runs
   would find nothing. The VRAM ceiling doesn't bind the science.
2. **If ablation continues, go wide not long:** all 2,890 items (comments included) at horizon
   ~30, overnight (~6–7 h), to catch the comment-driven influence post-clout misses.
3. **The higher-value track remains the longer-horizon straight *perplexity*** (endogeneity, not
   clout) — a different question the ablation decay doesn't touch: whether the community leans on
   its *accumulated* culture, which needs a window spanning hours, not the ~8-item local window
   used so far. That's KV-cache-bound (reaches ~80–320 items), and unaffected by this pass's
   "no long tail" result.
