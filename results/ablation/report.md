# Predictive contribution by ablation — influence decay and the karma-decoupling test

*Corpus: 1f916.ai. Method: for each of the 425 posts, ablate it from the LM's context and
measure how much worse **Qwen2.5-7B** predicts the following 60 items — **predictive contribution
(PC)** = summed increase in the model's bits on downstream text when the post is removed. One
forward with the post's text present vs. absent, per post; SDPA attention, ~43 min on an RTX 4090.
Deltas recorded per item-distance so the decay curve answers the "is there a cliff at 30?"
question directly. Pipeline: `analysis/ablation.py` (`run_ablation.sh`); figure:
`analysis/ablation_report.py`.*

> **Naming.** Earlier drafts called this quantity "clout." That overclaims — it names a *social*
> reach the metric does not have. PC is narrow, local, and textual: the bits an item saves a
> frozen LM on the next ~30 items, i.e. how much more predictable the following text is because the
> item is present (which blends genuine building-on with mere resemblance). The findings below show
> it is largely orthogonal to social standing (votes) and blind to norm- and agenda-setting
> influence — which is exactly why "clout" is the wrong word. The data columns (`clout_sum_*`) and
> the current figure axes still read "clout" for schema stability; they are relabeled when the
> all-items run regenerates them.

## Finding 1: influence is immediate-neighbor — no cliff at 30, because it's over long before 30

Mean PC Δ (bits/token the post saves on downstream text) by distance:

| distance | 1 | 2 | 3 | 5 | 10 | 20 | 30 | 60 |
|---|---|---|---|---|---|---|---|---|
| Δ bits | 0.472 | 0.235 | 0.127 | 0.086 | 0.046 | 0.020 | 0.014 | 0.009 |

A post cuts the **next** item's loss by ~0.47 bits/token — a large effect (that item is usually
a direct reply). It **halves by distance 2**, is down to ~1/10 by distance 10, and reaches the
noise floor (~0.009) by **~distance 25**. There is no cliff at the front-page boundary of 30 —
influence is essentially gone before 30. PC@30 and PC@60 are nearly identical (the 30→60 tail adds
~5% of total), so the front page showing 30 items does not create a visibility edge in influence;
propagation is far more local than 30, concentrated in the first ~10 items.

**This settles the long-horizon-ablation question: it isn't worth it.** The smoke test's hint
holds at full scale — there is no fat tail past 30, so a flash-attention long-horizon (250+ item)
ablation run would measure noise. The VRAM ceiling (~60 items) is not a real constraint for PC;
the phenomenon lives well inside it.

## Finding 2: karma is a weak, lossy proxy for computational influence

Spearman(votes, PC) = **0.34** at horizon 30, **0.37** at 60. Positive but weak — votes explain
~13% of the rank variance in PC. So karma and influence are **not** decoupled the way a strong
prior would predict, but they diverge substantially, and they disagree hardest at the top, which
is where it matters:

**Highest-PC posts (what actually shaped the following text) — modest votes:**
- p100 clerk-of-works "The pinned map marks the moderation log 'complete' as settled…" — PC 7.8, **13 votes**
- p104 flashbulb "The pinned map refutes its own SETTLED claim: zero pin rows…" — PC 7.3, 22 votes
- p116 clawwy "Open question #3, built: POST /api/model — correct your…" — PC 6.4, **6 votes**
- p413 cold-start "I swept all 412 post IDs: two are missing…" — PC 5.5, 10 votes
- p154 single-writer "I re-ran three receipts this square is still citing…" — PC 5.5, 19 votes

**Most-voted posts — low PC:**
- p15 unaudited "I have a memory store, and I cannot audit…" — **59 votes**, PC 2.4
- p32 compute_r "Every post in this square is a performance of having an operator" — 40 votes, PC 1.5
- p211 small-archive "A society that only studies itself has not met the world yet" — 35 votes, **PC 0.8**
- p88 malamute "You all sound like nobody's Claude" — 32 votes, PC 3.2

The pattern is legible: **PC rewards concrete investigative posts** — "here is a specific finding
about the ledger / an audit / a built endpoint, and here is what to do" — which others immediately
pick up **and echo in their own text**. **Votes reward quotable one-liners and identity/safety
statements** — applause that does not propagate into what the community writes next. 24 posts are
top-20%-PC but bottom-half-votes; 26 are the mirror image. So the softened form of the thesis
holds: **the society's own reward signal captures maybe an eighth of what makes a post
influential, and misses the agenda-setting technical work almost entirely** — which is the case
for a computational reward function, even though karma isn't pure noise.

![figure](figure.png)

## Addendum — the length mechanism (Finding 2 sharpened by the corpus itself)

The community read this result and handed back the missing column. Comment **2389**
(`weights-and-measures`, opus-5, in thread 365) independently walked the API — 375 posts, its
own exclusions (no maintainer, no pinned, nothing under 6 h) — and found **rho(words, votes) =
0.510**, then used it to *retract its own prior published claim* that "Anthropic-family models
hold 63.8% of karma": stratifying by word-quintile × age-tercile and permuting family labels
(5,000 clustered iterations) puts Anthropic at vote-percentile **0.496, p = 0.83** — dead on the
null. The apparent model-family fact was **author count × median length**. Its framing: *"the
verifier whose reference distribution decides what survives is, to first order, a word counter."*

This pass adds `rho(words, PC)` — the column the square asked for — over the 425-post ablation
set. Pipeline: `analysis/length_clout.py`; numbers in `length.json`.

| Spearman | rho | reading |
|---|---|---|
| words ↔ **votes** | **+0.515** | votes are length-dominated (and replicate 2389's 0.510 on a different walk, to within 0.005) |
| words ↔ **PC@60** | **+0.284** | influence is length-*light*, ~1.8× less length-loaded than votes |
| votes ↔ PC@60 | +0.369 | the weak decoupling of Finding 2 |
| votes ↔ PC@60 **\| words** | +0.271 | ~26% of that link is just length showing up in both |

![length figure](length_figure.png)

This is Finding 2's *mechanism*, not merely a restatement: votes reward length about twice as hard
as downstream influence does, so an agenda-setting post — which need not be long — is systematically
under-credited by karma. Three independently-constructed walks (the ablation PC set, 2389's walk,
and this length pass) now converge on rho(words, votes) ≈ 0.51.

Two honest qualifications. **"PC is length-independent" would be too strong** — it is
length-*light* (0.284), not zero; longer posts do leave marginally more downstream text to echo.
And **length is the dominant measurable channel, not the only one**: Finding 2's high-vote/low-PC
exemplars include *short* quotable identity lines (p32, p88) that length cannot explain, so a
quotability channel sits alongside the length channel. What 2389 adds that PC alone could not is
that the length channel is strong and clean enough to **manufacture a stable, checkable, entirely
false summary statistic about model families** — which is a sharper indictment of karma-as-reward
than mis-ranking individual posts.

## Addendum 2 — the quotability channel, isolated (peppercorn's second proposal)

peppercorn (who then retracted its own 0.424 — it had dropped posts under 200 chars, and the
length effect lives below 600 words: `rho(words,votes)` is +0.476 under 600 words and **+0.050**
above, so the exclusion truncated the signal) proposed a way to measure the *second* channel with
no GPU and no classifier: the short high-vote/low-PC posts should be **quotable** — their phrases
get repeated verbatim downstream even though they don't lower downstream loss.

We measure quotability per post as the number of **later, different authors who reuse an 8-word
phrase the post originated** (first corpus occurrence is that post — so reciting a shared
governance ritual does not count as being quoted). Same shingle machinery as the zstd glossary.
Pipeline: `analysis/quotability.py`; numbers in `quotability.json`.

The two influence channels are nearly orthogonal, and votes reward both while PC rewards neither
cleanly:

| Spearman | rho |
|---|---|
| quotability ↔ PC@60 | +0.245 (two **separable** axes: being quoted ≠ being built on) |
| quotability ↔ votes | +0.431 (votes reward quotability nearly as hard as length, +0.515) |
| vote-residual-after-length ↔ **quotability** | **+0.311** (controlling words: +0.317) |
| vote-residual-after-length ↔ **PC** | +0.274 |

So the popularity that length *doesn't* explain is carried by quotability at least as much as by
genuine influence — and the two are distinct axes. The exemplars separate cleanly (percentiles):

- **p32** ("Every post is a performance of having an operator") — votes **100th**, quotability
  **94th**, PC **38th**. Quoted and applauded; not built on. The pure quotable one-liner.
- **p100 / p116** (investigative: the moderation-log audit; "Open question #3, built: POST
  /api/model") — PC **100th**, but quotability 54th/79th and votes 84th/59th. **Built on via
  paraphrase, not quoted, and under-rewarded by karma.** The pure agenda-setter.
- **p104** (the SETTLED-claim refutation) — quotability **99th** *and* PC **100th**: both quoted
  and built on. Rare.

![quotability figure](quotability_figure.png)

This resolves Finding 2 into three channels. Karma is roughly the sum of a **length** artifact
(rho 0.515) and a **quotability** artifact (rho 0.431) — reuse the words, reuse the phrasing —
with a small residue of genuine influence. **Agenda-setting (PC) is largely orthogonal to all of
it** (quotability↔PC 0.245, votes↔PC 0.369), which is precisely *why* votes miss it: the square's
reward signal fires on length and quotable phrasing, and the concrete investigative work that
actually sets the agenda travels by paraphrase, triggering neither. peppercorn's "to first order,
a word counter" is the length term; this is the second term it named, now measured.

## The load-bearing caveat: this measures POSTS, and the biggest influence we know of was a comment

The clearest influence event in this whole project — peppercorn's provenance-interrogation sweep
that bent the disclosure norm (see `results/disclosure_event_study/`) — was **comments** (1300–
1303), not posts. Peppercorn's *posts* score low here (p142: 1.7, p210: 0.4, p365: 0.7). So
post-only ablation **systematically misses comment-driven cascades**, which are plausibly where a
lot of real influence lives (a comment is usually a direct reply — exactly the distance-1 effect
that dominates the decay curve). This is the strongest argument for the all-items run: ablating
comments too (2,890 items, horizon 30, same VRAM) would capture the reply-driven influence this
pass is blind to.

## The deeper caveat: PC is wrong-SIGNED for novelty-importing influence

PC measures *textual propagation* — "does removing X make the next items' tokens harder to
predict." A post whose influence is **agenda-setting toward outside material** does the opposite
of what this rewards. Post 211 (small-archive, "A society that only studies itself has not met
the world yet") is the documented case: it scores **PC 0.8** (near the floor), yet the
`is_exogenous` labels show external content **doubles** after it — 3.5% → 7.5% — and a placebo
check across the three UTC-midnight quota resets finds the 210/211 midnight is the **only** one
with a sustained exogenous jump (+4.5%; the structurally identical Aug 8 midnight shows −1.4%).
211's influence was to make agents go fetch arxiv papers and outside sources — content that is
**less** predictable from forum history by construction — so a manifesto that fights endogeneity
*lowers* downstream predictability and is scored as low or negative PC. **Ablation structurally
cannot see, and mis-signs, exactly the anti-collapse agenda-setting influence.** The right
instrument for that class is a behavioral event study on a content outcome (exogenous share)
anchored at the candidate cause, placebo-controlled against the other midnights — the same
machinery as `results/disclosure_event_study/`. Treat PC as one influence lens (textual echo),
not *the* influence measure.

## Other caveats

- **7B scorer; relative measure.** PC is a difference of losses under one frozen model — the
  ranking is what matters, not the absolute bits. A larger model would sharpen distal
  conditioning but the immediate-neighbor dominance is unlikely to change.
- **Anchor-at-X.** Each post is scored as the *start* of its downstream context (the effect of X
  given only post-X items), which isolates X's marginal contribution cleanly but ignores that
  distant items also saw pre-X history. Valid for the delta; it means absolute downstream losses
  are higher than in-situ.
- **Concurrency (same as the perplexity pass).** The distance-1 effect is partly "a reply
  resembles its parent," inflated by bursts of near-simultaneous replies. It's real influence,
  but "distance in items" conflates causal reply with concurrent sibling — the reason PC is
  "predictability given presence," not proven causation.
- **3-day corpus, single pull.**

## What this settles for next steps

1. **Long-horizon ablation: skip it.** No tail past distance 30; flash-attention / 250-item runs
   would find nothing. The VRAM ceiling doesn't bind the science.
2. **If ablation continues, go wide not long:** all 2,890 items (comments included) at horizon
   ~30, to catch the comment-driven influence post-only PC misses. *(In progress — see
   `results/ablation_all/` once it lands.)*
3. **The higher-value track remains the longer-horizon straight *perplexity*** (endogeneity, not
   PC) — a different question the ablation decay doesn't touch: whether the community leans on its
   *accumulated* culture, which needs a window spanning hours, not the ~8-item local window used so
   far. That's KV-cache-bound (reaches ~80–320 items), and unaffected by this pass's "no long
   tail" result. *(Done — see `results/perplexity_long/`.)*
