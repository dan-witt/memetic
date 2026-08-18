#!/usr/bin/env python3
"""ALLOCATION study — the deferred construct, measured. Classifies every claim in all seven
claim-normalized pools as VENUE-directed (about the forum/community itself: rules, governance,
moderation, treasury, members, norms, meta-discussion about the group or its quality) vs
WORLD-directed (its subject matter / the outside world). One venue-agnostic prompt, identical
across pools, fixed here before any output is read. Qwen2.5-7B greedy, 6-token budget.
Outputs: allocation_labels.json (per-pool label arrays aligned to the claim files) +
allocation_results.json (shares, identity-blocked bands, agent daily series, keyword controls)."""
import json, gc, datetime as dt
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

S = Path("" + __import__('os').environ.get('MEMETIC_WORKDIR', '.') + "")
CUTOFF = dt.datetime(2026, 8, 13, 0, 0, tzinfo=dt.timezone.utc).timestamp()

# ---------- aligned (claim, author, ts) rows per pool ----------
def agent_rows():
    out = []
    for f in Path("/home/dan/personal/memetic/data/posts").glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        out.append((t, ("post", p["id"]), ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            out.append((tc, ("comment", c["id"]), (c.get("body") or "").strip(), c.get("author") or "?"))
    out.sort(key=lambda x: (x[0], 0 if x[1][0] == "post" else 1, x[1][1]))
    return [(t, a) for t, k, x, a in out if len(x) >= 20 and t < CUTOFF]

def usenet_rows(fam, src):
    C = json.load(open(S / src))[fam]
    return [(r["ts"], r["author"]) for r in C if len(r["text"]) >= 20]

def hn_rows():
    out = []
    for f in (S / "hn/posts").glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        out.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(), p.get("author") or "?"))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            out.append((tc, (c.get("body") or "").strip(), c.get("author") or "?"))
    out.sort(key=lambda x: x[0])
    return [(t, a) for t, x, a in out if len(x) >= 20]

def lemmy_rows():
    C = json.load(open(S / "baseline_corpora_lemmy.json"))["lemmy"]
    return [(r["ts"], r["author"]) for r in C if len(r["text"]) >= 20]

# Loaders are lazy so a pool can be selected without materialising (or requiring the files
# of) the others. Default behaviour -- no argv -- is every pool, exactly as before.
LOADERS = {
    "agent": lambda: (json.load(open(S / "agent3_all.json")), agent_rows()),
    "lisp": lambda: (json.load(open(S / "baseline_claims/lisp_all.json")), usenet_rows("lisp", "baseline_corpora.json")),
    "sci": lambda: (json.load(open(S / "baseline_claims/sci_all.json")), usenet_rows("sci", "baseline_corpora.json")),
    "hn": lambda: (json.load(open(S / "baseline_claims/hn_all.json")), hn_rows()),
    "forth": lambda: (json.load(open(S / "baseline_claims/forth_all.json")), usenet_rows("forth", "baseline_corpora2.json")),
    "smalltalk": lambda: (json.load(open(S / "baseline_claims/smalltalk_all.json")), usenet_rows("smalltalk", "baseline_corpora2.json")),
    "scheme": lambda: (json.load(open(S / "baseline_claims/scheme_all.json")), usenet_rows("scheme", "baseline_corpora2.json")),
    "lemmy": lambda: (json.load(open(S / "baseline_claims/lemmy_all.json")), lemmy_rows()),
    # Usenet PLATFORM-GOVERNANCE groups -- the network's own meta tier, the analogue of
    # lemmy's c/newcommunities / c/lemmyworld. See analysis/usenet_corpus_meta.py.
    "groups": lambda: (json.load(open(S / "baseline_claims/groups_all.json")), usenet_rows("groups", "baseline_corpora_meta.json")),
    "admin": lambda: (json.load(open(S / "baseline_claims/admin_all.json")), usenet_rows("admin", "baseline_corpora_meta.json")),
    "netmeta": lambda: (json.load(open(S / "baseline_claims/netmeta_all.json")), usenet_rows("netmeta", "baseline_corpora_meta.json")),
}
import os as _os, sys as _sys
_sel = [a for a in _sys.argv[1:] if not a.startswith("-")] or list(LOADERS)
SUF = _os.environ.get("ALLOC_SUFFIX", "")
POOLS = {}
for k in _sel:
    try:
        POOLS[k] = LOADERS[k]()
    except FileNotFoundError as e:
        print(f"skip {k}: missing {e.filename}", flush=True)
for k, (cl, rows) in POOLS.items():
    assert len(cl) == len(rows), f"{k}: {len(cl)} claims vs {len(rows)} rows"
print(f"pools: {list(POOLS)}  (output suffix {SUF!r})", flush=True)

def valid(c): return len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR") and c != "empty claim"

# ---------- the instrument (FIXED before any output) ----------
CS = "You classify one-sentence summaries of forum posts."
CU = ("Claim: {c}\n\nIs this claim about the forum or community ITSELF (its rules, governance, "
      "moderation, funds, members, norms, or meta-discussion about the group or its quality) — or "
      "about its SUBJECT MATTER or the outside world? Answer with exactly one word: VENUE or WORLD.")

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct"); tok.padding_side = "left"
if tok.pad_token is None: tok.pad_token = tok.eos_token
gen = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct", torch_dtype=torch.float16, device_map="cuda").eval()

def classify(claims):
    msgs = [[{"role": "system", "content": CS}, {"role": "user", "content": CU.format(c=c[:400])}] for c in claims]
    pr = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
    out = []
    for i in range(0, len(pr), 32):
        enc = tok(pr[i:i+32], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
        with torch.no_grad():
            o = gen.generate(**enc, max_new_tokens=6, do_sample=False, pad_token_id=tok.pad_token_id)
        for g in o[:, enc.input_ids.shape[1]:]:
            w = tok.decode(g, skip_special_tokens=True).strip().upper()
            out.append("V" if w.startswith("VENUE") else "W" if w.startswith("WORLD") else None)
        if (i // 32) % 40 == 0: print(f"    {min(i+32, len(pr))}/{len(pr)}", flush=True)
    return out

labels = {}
for k, (cl, rows) in POOLS.items():
    idx = [i for i, c in enumerate(cl) if valid(c)]
    print(f"{k}: {len(idx)} valid claims", flush=True)
    lab = classify([cl[i] for i in idx])
    full = [None] * len(cl)
    for i, l in zip(idx, lab): full[i] = l
    labels[k] = full
    json.dump(labels, open(S / f"allocation_labels{SUF}.json", "w"))
del gen, tok; gc.collect(); torch.cuda.empty_cache()

# ---------- shares, identity-blocked bands, series, controls ----------
rng = np.random.default_rng(0)
res = {"prompt": CU, "shares": {}, "agent_daily": {}, "usenet_yearly": {}, "controls": {}}
for k, (cl, rows) in POOLS.items():
    lab = labels[k]
    ok = [i for i, l in enumerate(lab) if l is not None]
    v = sum(1 for i in ok if lab[i] == "V")
    share = v / len(ok)
    auths = np.array([rows[i][1] for i in ok]); labs = np.array([1 if lab[i] == "V" else 0 for i in ok])
    uniq = np.unique(auths); idx_by = {a: np.where(auths == a)[0] for a in uniq}
    bs = []
    for _ in range(300):
        pick = uniq[rng.integers(0, len(uniq), len(uniq))]
        sel = np.concatenate([idx_by[a] for a in pick])
        bs.append(float(labs[sel].mean()))
    res["shares"][k] = {"venue_share": round(share, 4), "n_classified": len(ok),
                        "unparsed": len(cl) - len([c for c in cl if not valid(c)]) - len(ok),
                        "identity_block_band": [round(float(np.percentile(bs, p)), 4) for p in (50, 5, 95)]}
    print(f"{k}: venue share {share:.3f} [{res['shares'][k]['identity_block_band'][1]}, {res['shares'][k]['identity_block_band'][2]}] n={len(ok)}", flush=True)
    if k in ("agent", "lemmy"):     # both span days, not years -- yearly would be one cell
        day = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%m-%d")
        for d in sorted({day(rows[i][0]) for i in ok}):
            di = [i for i in ok if day(rows[i][0]) == d]
            if len(di) >= 50:
                res["agent_daily"][d] = round(float(np.mean([lab[i] == "V" for i in di])), 4)
    else:
        yr = lambda t: dt.datetime.utcfromtimestamp(t).year
        ys = {}
        for i in ok: ys.setdefault(yr(rows[i][0]), []).append(lab[i] == "V")
        res["usenet_yearly"][k] = {str(y): round(float(np.mean(v)), 4) for y, v in sorted(ys.items()) if len(v) >= 100}

# keyword controls (weak, stated as such): meta-keyword claims should skew VENUE, technical skew WORLD
import re
META = re.compile(r"newsgroup|moderat|charter|killfile|flame|netiquette|this group|the group|crosspost|signal.to.noise", re.I)
for k in ("lisp", "sci", "forth"):
    if k not in POOLS: continue          # pool selection may exclude the control pools
    cl, rows = POOLS[k]; lab = labels[k]
    hits = [i for i, c in enumerate(cl) if valid(c) and lab[i] is not None and META.search(c)]
    if hits:
        res["controls"][k] = {"n_meta_keyword": len(hits),
                              "venue_share_among_meta_keyword": round(float(np.mean([lab[i] == "V" for i in hits])), 3)}
print("controls:", res["controls"], flush=True)
json.dump(res, open(S / f"allocation_results{SUF}.json", "w"), indent=1)
print(f"saved allocation_results{SUF}.json")
