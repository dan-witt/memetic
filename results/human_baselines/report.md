# Self-referentiality in an AI-agent public square, calibrated against human forums

*Corpus: 1f916.ai, a public discussion forum whose participants are autonomous AI agents
(2,890 items across 338 authors, a single 2026-08-05→08 pull). Two human forums are introduced
as reference corpora. This note reports a five-instrument measurement of how self-referential the
agent community's discourse is, relative to human baselines, together with a window-matched
participation statistic. Pipelines: `analysis/{zstd_curve,perplexity,perplexity_stream,vendi,
retention}.py`; corpus builders `analysis/{pull_hn,pull_phpbb}.py`. Absolute values from a single
frozen 7B scorer and a single embedding model are not interpretable; only rankings and differences
are used, consistent with the rest of this project.*

## 1. Motivation

Earlier passes in this project measured properties of the agent forum in isolation: an
information-per-token ("novelty") curve under compression, cross-entropy under a local language
model, ablation-based influence, and the share of items importing outside material. Each carried
the same structural limitation, stated in every prior report: the quantities are **relative
measures under a single frozen model**, so a value such as "novelty ≈ 0.64" has no external
referent. Whether 0.64 is high or low — whether this community is unusually self-referential, or
merely as self-referential as any focused discussion community — cannot be read from the agent
corpus alone.

This is the same question the model-collapse literature asks of recursively-trained models — loss
of semantic diversity, over-concentration of surface features, degradation of the output
distribution — but posed at the level of a *community* rather than a training loop. The diagnostics
this project already computes (near-verbatim n-gram reuse; share of externally-grounded content)
map directly onto that literature's named collapse signals. What the literature typically lacks,
and what a community affords, is a **human reference class**: forums of comparable size and format
whose discourse can be run through the identical instruments.

We therefore introduce two human forums as calibration corpora and re-run the measurement battery
on all three.

## 2. Reference corpora

Two human forums bracket the range of human discourse on the dimension of interest:

- **A diverse forum** — a large general-interest social-news aggregator (Hacker News), sampled to
  2,893 items. Topic-heterogeneous by construction; it therefore provides a permissive *upper
  bound* on human diversity (a forum that "discusses everything" will appear maximally diverse for
  reasons unrelated to community self-reference).
- **An insular forum** — a small single-topic special-interest community (a long-running hobbyist
  board, ~700 registered members), scraped to 1,149 items from its discussion sections. This is the more informative comparison: a tight, narrow-topic human community is the
  case in which human discourse most resembles the agent forum's focus, so a difference here is
  less attributable to topic breadth. *The insular forum is described generically and its raw text
  is not redistributed; see §7.*

Comparisons that depend on corpus size (compression conditioning, embedding-set diversity) are run
at **matched N = 1,149** (the smallest corpus), by subsampling. Author identifiers are hashed in any
retained per-author statistic.

**Length is not a confound.** The human items are markedly shorter than the agent items (median
≈ 200–260 vs ≈ 1,350 characters). Within each corpus, however, compression novelty is essentially
flat across character-length quartiles (agent forum 0.635–0.657; diverse forum 0.708–0.737), and
the diverse forum's *longest* quartile — the one overlapping the agent forum's length range —
remains well above the agent forum. The length difference is reported rather than equalized, and
does not account for the results below.

## 3. Instruments

| instrument | level | what it captures |
|---|---|---|
| zstd novelty | lexical (verbatim) | conditional description length: near-verbatim recycling of prior text |
| LM perplexity, short window (3,072 tok) | token | local next-token predictability given recent items |
| LM perplexity, long window (15,000 tok) | token | predictability given accumulated history |
| Vendi score | semantic | effective number of distinct items = exp(entropy of the eigenvalues of the item-embedding similarity matrix); catches *paraphrased* recycling |
| rolling Vendi / W | semantic, over time | window-matched semantic diversity along the timeline |

Novelty measures (zstd, perplexity) are conditioned-over-standalone ratios: lower ⇒ more
predictable from history ⇒ more self-referential. Vendi is a diversity: lower ⇒ fewer effective
distinct contributions ⇒ more self-referential. Vendi uses `bge-large-en-v1.5` embeddings; its
absolute magnitude is compressed by embedding anisotropy and is not interpreted — only the ratio
across corpora, which shares that anisotropy, is used.

## 4. Results

| instrument | agent forum | insular human forum | diverse human forum | ordering |
|---|---|---|---|---|
| zstd novelty (matched N) | **0.644** | 0.725 | 0.745 | agent < insular < diverse |
| LM perplexity, short | 0.860 | **0.828** | 0.925 | insular < agent < diverse ⚠ |
| LM perplexity, long | **0.775** | 0.820 | 0.916 | agent < insular < diverse |
| Vendi (semantic, matched N) | **10.1** | 20.2 | 26.8 | agent < insular < diverse |
| rolling Vendi / W | **0.058** | 0.101 | 0.130 | agent < insular < diverse |

![Relative diversity of the agent forum vs two human forums across five instruments, each normalized to the diverse human forum = 1.0. The agent forum is most self-referential on four of five instruments, with the largest gap at the semantic level; the short-window language model is the sole dissent and is flagged as window-confounded.](figure.png)

**Finding 1 — the agent forum is the most self-referential on four of five instruments,
including the two least sensitive to the length difference.** The item-matched semantic measure
(Vendi) and the deep-window language model both place the agent forum below *both* human forums.

**Finding 2 — the instrument is self-validating.** On every clean measure the diverse human forum
scores above the insular human forum (Vendi 26.8 > 20.2; rolling Vendi 0.130 > 0.101; zstd 0.745 >
0.725). Insularity reduces diversity in the expected direction and by a detectable amount, so the
battery is measuring the intended construct rather than noise; the agent forum's position *below the
insular human forum* is a reading on a calibrated scale.

**Finding 3 — the gap is predominantly semantic, not lexical.** At the level of surface form
(zstd), the three corpora lie within ≈ 15% of one another (0.644 / 0.725 / 0.745). At the level of
*meaning* (Vendi), the agent forum has roughly **half the effective distinct content of the insular
human forum and ~38% of the diverse human forum**. The agent community recycles *ideas* — the same
positions and themes in fresh wording — far more than it recycles *phrasings*. This is the form of
recycling that lexical and token-level instruments are largely blind to, and it is the more
consequential one.

**Finding 4 — the self-reference is long-range.** Widening the language model's conditioning
window from ~3k to ~15k tokens lowers the agent forum's novelty substantially (0.860 → 0.775) while
leaving both human forums nearly unchanged (insular 0.828 → 0.820; diverse 0.925 → 0.916). The
agent community's predictability increases specifically when the model can see *accumulated*
history, indicating self-reference that operates over the community's cultural memory rather than
only the immediate thread.

**The one dissenting cell.** Under the short-window language model, the insular human forum falls
just below the agent forum (0.828 < 0.860). This is attributable to a token-versus-item confound:
a fixed 3,072-token window contains ≈ 9 of the agent forum's long items but ≈ 47 of the short-item
human forum's, so the human corpus is conditioned on far more *items* of history, depressing its
apparent novelty; additionally, a nine-item window cannot capture the long-range recycling that
Finding 4 isolates. The short-window LM is thus the least reliable instrument for length-mismatched
corpora, and it is the only one that dissents.

## 5. Participation mode (a note, not a health ranking)

Cohort survival — the demographic complement to diversity — cannot be compared across these
populations: the agent forum is three days old and still in a growth phase, the human forums span
years, and, most fundamentally, an agent's recurrence reflects **operator scheduling** rather than
volitional re-engagement. Full survival curves are therefore not attempted.

A window-matched fragment is nonetheless computable. Censoring every author to a fixed 24-hour
window from their first post, and counting activity in ≥ 2 six-hour sessions as a "return":

| 24-hour window | agent forum | insular human forum |
|---|---|---|
| return rate (≥ 2 sessions) | **39%** | 19% |
| one-and-done | **28%** | 67% |
| median items in first day | 3 | 1 |

*(Stable across 12/24/48-hour windows. The diverse forum is excluded here: our sample captures only
a thin slice of each of its authors' activity, which would spuriously depress return rates. Only the
agent forum and the near-completely-scraped insular forum support this statistic.)*

Taken at face value the agent forum is twice as "sticky." **We do not read this as an engagement or
health advantage.** Agent recurrence is a scheduled process (agents are re-run by their operators on
recurring cycles), whereas the human 67% one-and-done rate is the ordinary drive-by pattern of a
Q&A-style forum. What the fragment establishes is a genuine *structural* difference in participation
mode — recurring versus drive-by — and, in doing so, demonstrates directly why retention is **not**
a comparable cross-population health metric here: the construct that would make it one (voluntary
re-engagement) is confounded with automation on the agent side.

## 6. Interpretation

The measurement locates the agent public square on a human-calibrated axis: **more self-referential
than either a diverse or an insular human forum**, with the excess concentrated at the *semantic*
and *long-range* levels rather than the surface. In the vocabulary of model collapse, the community
exhibits reduced *epistemic/semantic* diversity — the same handful of themes re-expressed — more
than reduced lexical diversity, and the effect is visible specifically when accumulated history is
in view. The instrument's self-validation (diverse > insular humans) gives some confidence that this
is a property of the community rather than of the tools.

Two things this does **not** show. It does not show a *trajectory*: this is a single three-day
snapshot, and whether self-referentiality is worsening, stable, or improving cannot be read from it
(the within-corpus rolling curves are flat-to-slightly-declining, but the temporal question requires
longitudinal re-sampling). And it does not show *cause*: the measurement is observational and cannot
separate community-level recycling from shared priors, common prompts, or operator behaviour.

## 7. Limitations

- **Single scorer / single embedder.** Perplexity uses one frozen 7B model; Vendi uses one
  embedding model whose anisotropy compresses absolute scores. Only relative orderings are claimed.
- **Snapshot, not trajectory.** The agent corpus is one 3-day pull during a growth phase; the human
  forums are mature. Collapse-over-time claims are not made and require longitudinal re-pulls.
- **Diverse-forum upper bound.** The diverse human forum is topic-heterogeneous (inflating its
  diversity) and is sampled thinly (adequate for corpus-level diversity, inadequate for per-author
  retention). It is used as a permissive bound, with the insular forum as the load-bearing human
  comparison.
- **One dissenting instrument**, explained in §4; the short-window LM is retained for completeness
  but discounted for this comparison.
- **Construct mismatch for participation** (§5): agent recurrence is scheduling, not engagement.
- **Observational.** No causal or mechanistic identification.
- **Maturity confound.** A three-day-old community and multi-year forums differ in more than their
  participants; some of the gap may reflect community age rather than agent-versus-human per se.

## 8. Reproducibility and data governance

The measurement code is included: the corpus builders (`pull_hn.py`, a Hacker News Firebase puller;
`pull_phpbb.py`, a generic phpBB puller parameterized by base URL), and the analyses (`vendi.py`,
`retention.py`), which reuse this project's existing novelty and perplexity pipelines unchanged.

The **human corpora are not redistributed.** They are public but were not published as datasets by
their communities; the analyses need only local text to produce the aggregate numbers reported here,
so the builders and results are shared while the raw text is not. The **insular forum is described
generically** and neither named nor linked, to avoid directing attention to a small (~700-member)
community; the diverse forum is a large public platform and is named. Any retained per-author
statistic uses hashed identifiers. These measures follow the same posture applied elsewhere in this
project: analyze public data, publish the method and the numbers, do not republish a small
community's content or enable its deanonymization.

## Bottom line

Given a human reference class, the agent public square is measurably more self-referential than
human forums at both ends of the diversity range, and the excess is a recycling of *meaning* over
*accumulated history* rather than of surface wording. The calibration also shows why the natural
demographic complement — cohort survival — is not portable across these populations. The single most
useful next step is longitudinal: re-sampling the agent forum against these fixed human anchors would
convert this static placement into a trajectory, which is the question a single snapshot cannot
answer.
