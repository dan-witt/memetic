#!/usr/bin/env python3
"""Weather report — GPU half. Cutoff from $WEATHER_CUTOFF (that date's midnight UTC, exclusive)
everywhere. Delta-claimify new items (cache keyed by kind:id) and evict cache entries for items
EDITED since the previous corpus. Compute: rolling claim-Vendi series; placement vs frozen
anchors (full pool AND issue-window-only cells, 3 embedders); allocation venue share/day;
newcomer cells (within-pool parity + cross-pool refresh: union-vs-incumbent Vendi and
matched-pool nearest-incumbent claim distance). Outputs weather_gpu_out.json +
agent_claims_current.json."""
import json, gc, os, sys, hashlib, datetime as dt
from pathlib import Path
# Set before torch touches CUDA. Issue #9 OOM'd here: the card carries ~3.4 GB of desktop memory,
# leaving ~20 GB, and a claimify batch of 16 at max_length=1500 through a 7B model peaked at
# 19.88 GB with 1.66 GB of it reserved-but-unallocated fragmentation. Expandable segments give
# that fragmentation back.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np
sys.path.insert(0, "/home/dan/personal/memetic/analysis")
import weather_nn_refresh as NNR   # matched-pool NN construction, single source of truth
import weather_lemmy_ref as LEMREF  # frozen lemmy.world platform levels for the allocation cell
import weather_newcomer as NC       # newcomer cell construction + pooled fallback, single source
import weather_alloc_parse as AP    # strict/corrected allocation parse, single source of truth
import weather_issue_boundary as IB  # issue/window boundaries, single source of truth
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path(os.environ.get("MEMETIC_WORKDIR", os.path.expanduser("~/personal/memetic-workdir")))
_c = os.environ["WEATHER_CUTOFF"]  # e.g. "2026-08-14" = midnight UTC upper bound (exclusive)
CUTOFF = dt.datetime(*map(int, _c.split("-")), tzinfo=dt.timezone.utc).timestamp()
CLAIM_BATCH = int(os.environ.get("WEATHER_CLAIM_BATCH", "8"))   # see the OOM note above

def load_items(d, cutoff=CUTOFF):
    items = []
    for f in Path(d).glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        items.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            items.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    items.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, k, x, a) for t, k, x, a in items if len(x) >= 20 and t < cutoff]

NEW = load_items("/home/dan/personal/memetic/data/posts")
PREV = load_items(S / "prev_corpus/data/posts")
prev_last = max(t for t, _, _, _ in PREV)
# items EDITED after publication: same id, different text. The id-keyed caches cannot see this,
# so evict them here and let the delta pass re-claimify / re-label them (issue-3 watch item #4).
_h = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
_ph = {k: _h(x) for _, k, x, _ in PREV}
EDITED = [k for _, k, x, _ in NEW if k in _ph and _h(x) != _ph[k]]
print(f"edited items (cache eviction): {len(EDITED)}", flush=True)
cache = {(k0, int(k1)): c for (k0, k1), c in
         ((k.split(":", 1), c) for k, c in json.load(open(S / "claim_cache_agent.json")).items())}
for k in EDITED: cache.pop(k, None)
todo = [(i, x) for i, (t, k, x, a) in enumerate(NEW) if k not in cache]
print(f"delta to claimify: {len(todo)}", flush=True)

if todo:
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
    CS, CU = "You extract the single core claim or topic of a forum post.", "Post:\n{t}\n\nIn ONE plain sentence, state only what this post is fundamentally claiming or about. No preamble, no quotes, no formatting."
    msgs = [[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(t=x[:3000])}] for _, x in todo]
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
    outs = []
    # Batch 8, not 16: activations here are batch x 1500 tokens through a 7B model and this is
    # the step that OOM'd at issue #9 on an 836-item delta. Claims are generated once per item and
    # cached forever, so batch size affects only the items generated in this pass (padding can
    # perturb a borderline decode at the margin); it is not a cross-issue comparability change.
    for i in range(0, len(pr), CLAIM_BATCH):
        enc = tok(pr[i:i+CLAIM_BATCH], return_tensors="pt", padding=True, truncation=True, max_length=1500).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=48, do_sample=False, pad_token_id=tok.pad_token_id)
        outs += [tok.decode(g, skip_special_tokens=True).strip() for g in o[:, enc.input_ids.shape[1]:]]
        if (i // CLAIM_BATCH) % 25 == 0: print(f"  {min(i+CLAIM_BATCH, len(pr))}/{len(pr)}", flush=True)
    for (i, _), c in zip(todo, outs): cache[NEW[i][1]] = c
    json.dump({f"{k[0]}:{k[1]}": c for k, c in cache.items()}, open(S / "claim_cache_agent.json", "w"))

claims = [cache[k] for _, k, _, _ in NEW]
json.dump(claims, open(S / "agent_claims_current.json", "w"))
# --- allocation trend: delta-classify (frozen prompt), id-keyed label cache ---
# Previous PUBLISHED issue (not merely the previous pull): its day set is what "already
# published" means for the retro-movement audit below, and its series is the diff comparator.
# NOT "every issue dir below the cutoff": an issue dated D has cutoff D+1 and so sorts below its
# own cutoff, which makes a post-publication re-run audit the issue against ITSELF. Single source
# of truth in weather_newcomer, which has the same hazard in pooled_start.
_prev_dirs = IB.published_issues_before(_c)
PREV_PUB = (json.load(open(_prev_dirs[0] / "results.json"))["allocation_trend"]
            ["venue_share_per_day_qwen_binary"]) if _prev_dirs else {}
PREV_PUB_NAME = _prev_dirs[0].name if _prev_dirs else None

lcache = json.load(open(S / "allocation_label_cache_agent.json"))
_rawf = S / "allocation_unparsed_raw_agent.json"
RAWUNP = json.load(open(_rawf)) if _rawf.exists() else {}
for k in EDITED:
    lcache.pop(f"{k[0]}:{k[1]}", None)   # edited text -> new claim -> re-label
    RAWUNP.pop(f"{k[0]}:{k[1]}", None)   # ...and its stale raw answer with it
def lvalid(c): return len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"
todo_l = [(i, claims[i]) for i, (t, k, x, a) in enumerate(NEW)
          if f"{k[0]}:{k[1]}" not in lcache and lvalid(claims[i])]
# A label is only cached when the model answers VENUE or WORLD; an unparseable answer caches
# nothing, so that item is RETRIED next issue. Retries land on days that are already published,
# which is a retro-movement channel the feed_lag block cannot see (it watches text edits and
# backfill, not label coverage). Count them so the movement is attributable, not mysterious.
_dayof = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%m-%d")
RETRIED = [i for i, _ in todo_l if NEW[i][1] in _ph]                       # in the previous PULL
RETRIED_PUB = [i for i, _ in todo_l if _dayof(NEW[i][0]) in PREV_PUB]      # on a PUBLISHED day
print(f"allocation delta-classify: {len(todo_l)} (retries: {len(RETRIED)} in the previous pull, "
      f"{len(RETRIED_PUB)} on days {PREV_PUB_NAME} already published)", flush=True)
if todo_l:
    try: tok
    except NameError:
        tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
        if tok.pad_token is None: tok.pad_token = tok.eos_token
        gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()
    ACS = "You classify one-sentence summaries of forum posts."
    ACU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
           "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
           "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")
    amsgs = [[{"role": "system", "content": ACS}, {"role": "user", "content": ACU.format(c=c[:400])}] for _, c in todo_l]
    apr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in amsgs]
    alab, araw = [], []
    for i in range(0, len(apr), 32):
        enc = tok(apr[i:i+32], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=6, do_sample=False, pad_token_id=tok.pad_token_id)
        for g in o[:, enc.input_ids.shape[1]:]:
            w = tok.decode(g, skip_special_tokens=True).strip().upper()
            araw.append(w); alab.append(AP.strict(w))
    for (i, _), l in zip(todo_l, alab):
        if l:
            lcache[f"{NEW[i][1][0]}:{NEW[i][1][1]}"] = l
            RAWUNP.pop(f"{NEW[i][1][0]}:{NEW[i][1][1]}", None)   # resolved: drop the stale raw
    json.dump(lcache, open(S / "allocation_label_cache_agent.json", "w"))
    # Issues #1-#7 threw the raw answer away, so every issue had to re-classify the uncovered
    # items just to see what they said. Keep it: the corrected series then falls out of cache,
    # and a NEW failure string becomes visible without a separate pass.
    for (i, _), w, l in zip(todo_l, araw, alab):
        if not l: RAWUNP[f"{NEW[i][1][0]}:{NEW[i][1][1]}"] = w
    json.dump(RAWUNP, open(S / "allocation_unparsed_raw_agent.json", "w"))
    del gen, tok; gc.collect(); torch.cuda.empty_cache()
import datetime as _dt
_day = lambda t: _dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
_ds, _dsc = {}, {}
for t, k, x, a in NEW:
    kk = f"{k[0]}:{k[1]}"
    l = lcache.get(kk)
    if l: _ds.setdefault(_day(t), []).append(l == "V")
    # corrected parse (issue #8): the strict label if there is one, else the observed raw answer
    # re-parsed. Adds only items that already went through the classifier with a valid claim.
    lc = l or (AP.corrected(RAWUNP[kk]) if kk in RAWUNP else None)
    if lc: _dsc.setdefault(_day(t), []).append(lc == "V")
_share = lambda d: {k: round(float(np.mean(v)), 4) for k, v in sorted(d.items()) if len(v) >= 50}
alloc_daily, alloc_daily_corr = _share(_ds), _share(_dsc)
print("allocation venue-share/day (strict, published currency):", alloc_daily, flush=True)
print("allocation venue-share/day (corrected parse):", alloc_daily_corr, flush=True)

# --- label-coverage audit + retro-movement check against the previous PUBLISHED issue ---
_cov = {}
for i, (t, k, x, a) in enumerate(NEW):
    if not lvalid(claims[i]): continue
    d = _day(t); c = _cov.setdefault(d, [0, 0]); c[0] += 1
    if f"{k[0]}:{k[1]}" in lcache: c[1] += 1
_unlab = sum(v[0] - v[1] for v in _cov.values())
# The audit counts describe THIS execution. If the claim cache was already warm (todo empty),
# this is a re-run and its counts are not the issue's totals - the delta pass that did the work
# classified more and may have resolved retries this pass can no longer see. Issue #6 was
# published from such a re-run; the block is labelled so a reader is never misled about which.
label_audit = {"pass_type": "delta pass (did this issue's classification work)" if todo else
               "re-run over warm caches: counts describe THIS pass only, not the issue total",
               "delta_classified": len(todo_l),
               "retries_in_previous_pull": len(RETRIED),
               "retries_on_already_published_days": len(RETRIED_PUB),
               "unlabelled_after_run": _unlab,
               "per_day": {d: {"valid_claim_items": v[0], "labelled": v[1],
                               "coverage": round(v[1] / v[0], 4)} for d, v in sorted(_cov.items())},
               "note": "unparseable classifier answers are not cached and are retried next issue; "
                       "a successful retry moves an already-published day."}
moved = {d: {"prev_issue": PREV_PUB[d], "this_issue": alloc_daily[d],
             "delta": round(alloc_daily[d] - PREV_PUB[d], 4)}
         for d in PREV_PUB if d in alloc_daily and abs(alloc_daily[d] - PREV_PUB[d]) > 1e-9}
if PREV_PUB_NAME: label_audit["prev_issue_compared"] = PREV_PUB_NAME
label_audit["published_days_moved"] = moved
print(f"label coverage: {sum(v[1] for v in _cov.values())}/{sum(v[0] for v in _cov.values())} "
      f"({_unlab} unlabelled); published days moved vs {label_audit.get('prev_issue_compared','-')}: "
      f"{moved if moved else 'none'}", flush=True)
claims = [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim" for c in claims]

from sentence_transformers import SentenceTransformer
def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

ANCH = {"lisp": "lisp_all.json", "sci": "sci_all.json", "hn": "hn_all.json"}
CL = {k: [c for c in json.load(open(S / "baseline_claims" / f)) if len(c.strip()) >= 5] for k, f in ANCH.items()}
rng = np.random.default_rng(0)
WIN_START, WIN_PROV = IB.issue_window_start(_c, prev_last)
win_idx = [i for i, (t, k, x, a) in enumerate(NEW) if t >= WIN_START]
# Lemmy.world platform reference for the allocation cell: frozen, read from the baseline's own
# artifact so the two cannot drift. Carried here so every issue gets it without being retyped.
_lem = LEMREF.levels()
out = {"n_items": len(claims), "issue_window_items": len(win_idx),
       "issue_window_basis": WIN_PROV, "allocation_daily_venue_share": alloc_daily,
       "allocation_daily_venue_share_corrected": alloc_daily_corr,
       "allocation_label_audit": label_audit}
if _lem:
    out["lemmy_reference"] = _lem
    out["allocation_daily_vs_lemmy"] = {d: LEMREF.position(v, _lem) for d, v in alloc_daily.items()}
    print("lemmy platform ref:", _lem["platform_qwen"],
          "| days above it:", sum(1 for v in alloc_daily.values() if v > _lem["platform_qwen"]),
          "/", len(alloc_daily), flush=True)
    # Both sides of the comparison under the SAME parse, or the comparison is rigged. The
    # comparator's corrected figure is exact once its dropped answers are recovered; until then
    # only issue #7's worst-case bound is available.
    _lemc = LEMREF.corrected_platform()
    out["lemmy_coverage_bound"] = LEMREF.coverage_bound()
    if _lemc:
        out["lemmy_corrected"] = _lemc
        out["allocation_daily_vs_lemmy_corrected"] = {
            d: LEMREF.position(v, dict(_lem, platform_qwen=_lemc["platform_qwen_corrected"]))
            for d, v in alloc_daily_corr.items()}
        print("lemmy platform ref (corrected):", _lemc["platform_qwen_corrected"],
              "| days above it:",
              sum(1 for v in alloc_daily_corr.values() if v > _lemc["platform_qwen_corrected"]),
              "/", len(alloc_daily_corr), flush=True)
W, ST = 120, 40
for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    tag = MODEL.split("/")[-1]
    m = SentenceTransformer(MODEL, device="cuda")
    Ea = m.encode(claims, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
    for k in ANCH:
        Ex = m.encode(CL[k], normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
        cells = {}
        for label, pool in [("full", np.arange(len(Ea))), ("window_only", np.array(win_idx))]:
            md = min(1500, int(0.8 * min(len(pool), len(Ex))))
            rs = [vendi(Ea[pool][rng.choice(len(pool), md, replace=False)]) /
                  vendi(Ex[rng.choice(len(Ex), md, replace=False)]) for _ in range(40)]
            cells[label] = {"m": md, "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        out.setdefault("placement", {}).setdefault(tag, {})[k] = cells
    print(f"{tag}: " + ", ".join(f"{k} full={out['placement'][tag][k]['full']['band'][0]} win={out['placement'][tag][k]['window_only']['band'][0]}" for k in ANCH), flush=True)
    if tag == "bge-large-en-v1.5":
        ws = [(i + W // 2, vendi(Ea[i:i+W]) / W) for i in range(0, len(Ea) - W + 1, ST)]
        out["rolling_series_bge"] = {"t_utc": [dt.datetime.utcfromtimestamp(NEW[i][0]).strftime("%m-%d %H:%M") for i, _ in ws],
                                     "vendi_over_W": [round(v, 4) for _, v in ws]}
        halves = [v for _, v in ws]
        out["rolling_halves_bge"] = {"first_half": round(float(np.mean(halves[:len(halves)//2])), 4),
                                     "second_half": round(float(np.mean(halves[len(halves)//2:])), 4)}
        # Newcomer refresh cells. Construction, floors and the pooled fallback live in
        # weather_newcomer.py -- imported rather than duplicated so the standalone run and the
        # pipeline cannot drift. Historical key names are preserved here for series continuity.
        _MAP = {"counts": "newcomer_counts", "within_pool_parity": "newcomer_within_pool_parity",
                "union_over_incumbent": "refresh_union_over_incumbent",
                "nn_distance_matched": "refresh_nn_distance_matched",
                "nn_distance_legacy_asymmetric": "refresh_nn_distance_legacy_asymmetric",
                "vendi_cells_skipped": "newcomer_vendi_cells_skipped",
                "nn_cell_skipped": "refresh_nn_cell_skipped"}
        idx_newc, idx_inc = NC.split(NEW, WIN_START)
        for _k, _v in NC.cells(Ea, idx_newc, idx_inc, rng).items():
            out[_MAP.get(_k, _k)] = _v
        print("newcomer window cell:",
              out.get("refresh_nn_distance_matched") or out.get("refresh_nn_cell_skipped"), flush=True)
        # Pooled fallback: with recruitment in single digits a one-day window no longer carries
        # enough newcomer text to run the instrument (issue #6: 42 items, issue #7: 9). Issue #6
        # pre-registered pooling the last K issue windows rather than reporting a second skip.
        # Computed whenever the per-issue NN cell is dark; it is its own series, not a continuation.
        if "refresh_nn_cell_skipped" in out:
            _st, _prov = NC.pooled_start(_c, 3)
            if _st is not None:
                _pn, _pi = NC.split(NEW, _st)
                out["newcomer_pooled_window"] = dict(
                    NC.cells(Ea, _pn, _pi, np.random.default_rng(0)), **_prov,
                    span_days=round((CUTOFF - _st) / 86400, 2),
                    comparability="NOT comparable to the per-issue newcomer cells of issues #1-#5:"
                                  " longer arrival window, contiguous interval, its own series.")
                print("newcomer pooled cell:", out["newcomer_pooled_window"]["counts"], flush=True)
    del m, Ea

json.dump(out, open(S / "weather_gpu_out.json", "w"), indent=1)
print("saved weather_gpu_out.json")
