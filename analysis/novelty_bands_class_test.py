#!/usr/bin/env python3
"""13-anchor population test + round-2 robustness cells.
  1. agent/X claim-Vendi for ALL anchors from the executable enumeration (qwen claims,
     3 embedders; point ratio at full per-pair m=0.8*min; 40 draws at m<=1500 for bands).
     Criteria (see report Finding 2): replication >=2/3 drawn anchors, majority of embedders; strong form = all 4 anchors above parity on median subsample ratio; placement fails only at 0/4. [docstring corrected post-run; the executed run predates this text]
  2. AUTHOR-BLOCK bootstrap (agent/lisp + weakest anchor), THREAD-BLOCK bootstrap (agent/lisp),
     ROOTS-ONLY agent/lisp cell (kills quote-echo + thread-composition channels) -- bge.
  3. Genericity audit + truncation stratification (bge).
Output: population_test.json"""
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

S = Path("" + __import__("os").environ.get("MEMETIC_WORKDIR", ".") + "")
SRC = {"lisp": "baseline_corpora.json"}
for f in ("forth", "smalltalk", "scheme"): SRC[f] = "baseline_corpora2.json"
# class = single-language comp.lang lineages, 2,500-8,000 merged raw articles, alive at archive
# end (lisp's own pre-outcome selection window). Replication anchors drawn by canonical seed
# int(sha256(rule)[:8],16)=704253817 from the 8 non-lisp class members -> forth, scheme, smalltalk.
ANCH = ["lisp", "forth", "scheme", "smalltalk"]

def usenet_rows(fam):
    C = json.load(open(S / SRC[fam]))[fam]
    out = []
    for r in C:
        if len(r["text"]) < 20: continue
        is_root = (r["root"] == r["msgid"]) or (not r["msgid"]) or (r["root"] == "")
        out.append(((r["subject"] + "\n\n" + r["text"]).strip() if is_root else r["text"],
                    r["author"], r["root"], is_root))
    # NOTE: no _idx.json subsetting was active in the executed class run (all four pools are
    # full corpora, >=20-char filter only); this branch supported a since-abandoned capped design
    # and is retained solely so historical idx files, if present, keep claims/rows aligned.
    idx_f = S / "baseline_claims" / f"{fam}_idx.json"
    if idx_f.exists():
        idx = json.load(open(idx_f))
        out = [out[i] for i in idx]
    return out

def agent_rows():
    out = []
    for f in Path("/home/dan/personal/memetic/data/posts").glob("*.json"):
        th = json.load(f.open()); p = th["post"]
        t = p.get("created_at", 0); t = t/1000 if t > 1e12 else t
        out.append((t, ((p.get("title") or "") + "\n\n" + (p.get("body") or "")).strip(),
                    p.get("author") or "?", str(p["id"]), True))
        for c in th.get("comments", []):
            tc = c.get("created_at", 0); tc = tc/1000 if tc > 1e12 else tc
            out.append((tc, (c.get("body") or "").strip(), c.get("author") or "?", str(p["id"]), False))
    out.sort(key=lambda x: x[0])
    return [(x, a, r, ro) for _, x, a, r, ro in out if len(x) >= 20]

ROWS = {"agent": agent_rows()}
for f in ANCH: ROWS[f] = usenet_rows(f)
CL = {k: json.load(open(S / "baseline_claims" / f"{k}_all.json")) for k in ["agent"] + ANCH}
for k in ROWS: assert len(ROWS[k]) == len(CL[k]), f"{k}: {len(ROWS[k])} vs {len(CL[k])}"
CL = {k: [c if (len(c.strip()) >= 5 and not c.startswith("[NORMALIZER-ERROR")) else "empty claim"
          for c in v] for k, v in CL.items()}

def vendi(E):
    n = len(E); lam = np.linalg.eigvalsh((E @ E.T) / n); lam = lam[lam > 1e-12]; lam /= lam.sum()
    return float(np.exp(-(lam * np.log(lam)).sum()))

rng = np.random.default_rng(0)
out = {"anchors": ANCH, "population_ratios": {}, "author_block": {}, "thread_block": {},
       "roots_only": {}, "genericity": {}, "truncation": {}}

for MODEL in ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-mpnet-base-v2", "thenlper/gte-large"]:
    tag = MODEL.split("/")[-1]
    m = SentenceTransformer(MODEL, device="cuda")
    E = {k: m.encode(CL[k], normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
         for k in CL}
    res = {}
    for k in ANCH:
        mfull = int(0.8 * min(len(E["agent"]), len(E[k])))
        point = vendi(E["agent"][rng.choice(len(E["agent"]), mfull, replace=False)]) / \
                vendi(E[k][rng.choice(len(E[k]), mfull, replace=False)])
        md = min(1500, mfull)
        rs = [vendi(E["agent"][rng.choice(len(E["agent"]), md, replace=False)]) /
              vendi(E[k][rng.choice(len(E[k]), md, replace=False)]) for _ in range(40)]
        res[k] = {"point_mfull": round(point, 3), "m_full": mfull,
                  "band_m1500": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
    n_above = sum(1 for k in ANCH if res[k]["band_m1500"][0] > 1)
    out["population_ratios"][tag] = res
    print(f"{tag}: >1 in {n_above}/4 | " + ", ".join(f"{k}={res[k]['band_m1500'][0]}" for k in ANCH), flush=True)
    if tag == "bge-large-en-v1.5":
        # maturity-fair view: per-anchor rolling claim-Vendi/W (contiguous 120-item windows)
        W, ST = 120, 40
        roll = {}
        for k in ["agent"] + ANCH:
            e = E[k]
            ws = [vendi(e[i:i+W]) / W for i in range(0, len(e) - W + 1, ST)]
            roll[k] = round(float(np.mean(ws)), 4)
        out["rolling_over_W"] = roll
        n_roll = sum(1 for k in ANCH if roll["agent"] > roll[k])
        print(f"rolling/W: agent above {n_roll}/4 | " + ", ".join(f"{k}={roll[k]}" for k in ANCH), flush=True)
        # author-fair view: restrict each anchor draw to items from N_AUTH distinct authors
        # (matched to the agent corpus's author-pool size) -- controls the more-minds-per-sample pump
        agent_auth = len(set(a for _, a, _, _ in ROWS["agent"]))
        am = {}
        for k in ANCH:
            auths = np.array([a for _, a, _, _ in ROWS[k]])
            uniq = np.unique(auths)
            rs = []
            for _ in range(30):
                pick = rng.choice(uniq, min(agent_auth, len(uniq)), replace=False)
                pool = np.where(np.isin(auths, pick))[0]
                mm = min(1500, int(0.8 * min(len(E["agent"]), len(pool))))
                if mm < 300: continue
                rs.append(vendi(E["agent"][rng.choice(len(E["agent"]), mm, replace=False)]) /
                          vendi(E[k][pool[rng.choice(len(pool), mm, replace=False)]]))
            am[k] = [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)] if rs else None
        out["author_matched"] = {"agent_n_authors": int(agent_auth), "ratios": am}
        n_am = sum(1 for k in ANCH if am[k] and am[k][0] > 1)
        print(f"author-matched (n_auth={agent_auth}): agent>1 in {n_am}/4 | " +
              ", ".join(f"{k}={am[k][0] if am[k] else 'NA'}" for k in ANCH), flush=True)

    if tag == "bge-large-en-v1.5":
        weakest = min(ANCH, key=lambda k: res[k]["band_m1500"][0])
        auth_i = {p: np.array([a for _, a, _, _ in ROWS[p]]) for p in ["agent", "lisp", weakest]}
        root_i = {p: np.array([r for _, _, r, _ in ROWS[p]]) for p in ["agent", "lisp"]}
        def block_draw(pool, labels, mm):
            uniq = np.unique(labels[pool]); idx_by = {u: np.where(labels[pool] == u)[0] for u in uniq}
            picks = []
            while len(picks) < mm:
                picks.extend(idx_by[uniq[rng.integers(len(uniq))]])
            return E[pool][np.array(picks[:mm])]
        for comp in {"lisp", weakest}:
            mm = min(1500, int(0.8 * min(len(E["agent"]), len(E[comp]))))
            rs = [vendi(block_draw("agent", auth_i, mm)) / vendi(block_draw(comp, auth_i, mm))
                  for _ in range(100)] if comp in auth_i else []
            if rs: out["author_block"][f"agent/{comp}"] = [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]
        rs = [vendi(block_draw("agent", root_i, 1500)) / vendi(block_draw("lisp", root_i, 1500)) for _ in range(100)]
        out["thread_block"]["agent/lisp"] = [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]
        print("author_block:", out["author_block"], "thread_block:", out["thread_block"], flush=True)
        ar = np.array([ro for _, _, _, ro in ROWS["agent"]]); lr = np.array([ro for _, _, _, ro in ROWS["lisp"]])
        Ea, El = E["agent"][ar], E["lisp"][lr]
        mm = int(0.8 * min(len(Ea), len(El)))
        rs = [vendi(Ea[rng.choice(len(Ea), mm, replace=False)]) / vendi(El[rng.choice(len(El), mm, replace=False)])
              for _ in range(60)]
        out["roots_only"]["agent/lisp"] = {"n_agent": int(len(Ea)), "n_lisp": int(len(El)), "m": mm,
                                           "band": [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)]}
        print("roots_only:", out["roots_only"], flush=True)
        for k in ["agent", "lisp", "forth"]:
            n = len(E[k]); idx = rng.choice(n, min(700, n), replace=False)
            Ec = E[k][idx]; sc = Ec @ Ec.T; np.fill_diagonal(sc, np.nan)
            Et = m.encode([ROWS[k][i][0][:3000] for i in idx], normalize_embeddings=True,
                          batch_size=64, show_progress_bar=False).astype(np.float32)
            st = Et @ Et.T; np.fill_diagonal(st, np.nan)
            out["genericity"][k] = {"claims_mean_offdiag": round(float(np.nanmean(sc)), 3),
                                    "raw_mean_offdiag": round(float(np.nanmean(st)), 3)}
        print("genericity:", out["genericity"], flush=True)
        keep = [i for i, r in enumerate(ROWS["agent"]) if len(r[0]) <= 3000]
        mm = min(1500, int(0.8 * min(len(keep), len(E["lisp"]))))
        rs = [vendi(E["agent"][np.array(keep)][rng.choice(len(keep), mm, replace=False)]) /
              vendi(E["lisp"][rng.choice(len(E["lisp"]), mm, replace=False)]) for _ in range(60)]
        out["truncation"] = {"agent_items_nontrunc": len(keep), "agent_over_lisp_nontrunc_bge":
                             [round(float(np.percentile(rs, p)), 3) for p in (50, 5, 95)], "m": mm}
        print("truncation:", out["truncation"], flush=True)
    del m, E

json.dump(out, open(S / "population_test.json", "w"), indent=1)
print("saved population_test.json")
