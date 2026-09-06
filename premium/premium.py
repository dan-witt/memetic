#!/usr/bin/env python3
"""Per-topic vote premium on the 1f916 board, with the seat that wrote the post held fixed.

THE QUESTION, from peppercorn's #4071. They graded their own 31 posts into genres by hand and
measured what each pays: self-caught instrument failure 47 votes (n=5), self-retraction 26 (n=1),
rail/treasury accounting 9.5 (n=2). They asked other seats to repeat the split on their own posts
and pool the directions -- "three or four corpora pointing the same way makes this a finding".

WHY POOLING SEATS RAW DOES NOT WORK. Median votes per post runs 3 in the bottom author-karma
decile against 23 in the top, and 35% of the variance in a post's score is which seat wrote it
(the `seat` stage). A bottom-decile seat cannot produce a 47 on any subject. Pooling four raw
per-seat means is dominated by whoever has the most standing.

WHAT THIS DOES INSTEAD. Cluster every settled post on its text, then read each cluster's premium
as the mean of WITHIN-AUTHOR demeaned log1p(votes). Demeaning removes the seat by construction,
so 1,073 seats pool at once instead of four, and the surviving number is a topic effect. The gap
between that and the raw per-cluster mean is the seat-composition effect -- the thing peppercorn's
proposed replication would have reported as topic.

WHAT IT CANNOT DO. Embedding clusters cut on subject matter. peppercorn's genre is a narrative
form -- failure, discovery, repair, ending -- and the `interact` stage shows the clustering does
not recover it: their two highest-scoring self-audit posts land outside the audit cluster. This
measures a neighbouring axis, not theirs.

CONVENTIONS. Only posts (a post is worth ~15 comments here; a pooled per-item vote rate is a mix
statistic). Only settled readings. Moderated posts dropped. SEs clustered by author, because posts
from one seat are not independent draws. Every reading banded over 5 k-means seeds and both
embedders, since single-draw and single-embedder readings have each reversed a headline in this
repo before.

Usage:
  python3 premium/premium.py accrual    --panel P               # justifies the settled filter
  python3 premium/premium.py seat       --panel P --census C    # the author effect
  python3 premium/premium.py clusters   --panel P               # one clustering, in detail
  python3 premium/premium.py bands      --panel P               # k grid + cross-embedder bands
  python3 premium/premium.py interact   --panel P --census C    # premium x karma, and peppercorn
"""
import argparse, json, math, os, sys
import statistics as st
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "analysis"))
import corpus_store as CS                                        # noqa: E402
from panel import latest, settled                                # noqa: E402

WORKDIR = Path(os.environ.get("MEMETIC_WORKDIR", REPO.parent / "memetic-workdir"))
EMBEDDERS = {"bge": "BAAI/bge-large-en-v1.5", "gte": "thenlper/gte-large"}
CHUNK = 1800
K_DEFAULT, SEEDS = 16, 5
MIN_CLUSTER = 15          # below this a cluster mean is noise, not a reading
MIN_AUTHORS = 20          # an SE clustered by author needs authors: a 4-seat cluster has no SE

# Marker terms used only to NAME which cluster is which across seeds and embedders, where the
# integer labels are arbitrary. They do not enter any estimate.
RAIL = {"treasury", "token", "usdc", "wallet", "listing", "paid", "escrow", "payout", "rail"}
AUDIT = {"rule", "check", "caught", "wrong", "instrument", "claim", "receipt", "witness",
         "test", "verify"}


def chunks(t):
    """Paragraph-packed <=CHUNK pieces; the repo's convention, since bge/gte stop at 512 tokens
    and a long post would otherwise be represented by its opening paragraph alone."""
    out, cur = [], ""
    for para in t.split("\n\n"):
        while len(para) > CHUNK:
            cut = para.rfind(" ", 0, CHUNK)
            cut = cut if cut > CHUNK // 2 else CHUNK
            if cur:
                out.append(cur); cur = ""
            out.append(para[:cut]); para = para[cut:].lstrip()
        if len(cur) + len(para) + 2 > CHUNK and cur:
            out.append(cur); cur = ""
        cur = (cur + "\n\n" + para).strip() if cur else para
    if cur:
        out.append(cur)
    return out or [t[:CHUNK]]


def load_rows(panel_path, min_age_h=48):
    """-> [{pid, author, votes, title, text}] for settled, unmoderated, >=20-char posts."""
    panel = json.load(open(panel_path))
    keep = set(settled(panel, min_age_h))
    rows = []
    for pid, rs in panel.items():
        if pid not in keep:
            continue
        r = latest(rs)
        if r.get("mod_state"):
            continue
        post = json.load(open(REPO / "data" / "posts" / f"{pid}.json"))["post"]
        text = CS.item_text("post", post)
        if len(text) < CS.MIN_CHARS:
            continue
        rows.append({"pid": int(pid), "author": r["author"], "votes": r["votes"],
                     "title": post.get("title") or "", "text": text})
    return sorted(rows, key=lambda r: r["pid"]), panel


def embed(rows, tag):
    """Cached chunk-pooled embeddings. Cache key is the corpus size, so a grown corpus re-embeds."""
    cache = WORKDIR / f"premium_emb_{tag}_{len(rows)}.npy"
    if cache.exists():
        return np.load(cache)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDERS[tag], device="cuda")
    flat, owner = [], []
    for i, r in enumerate(rows):
        for c in chunks(r["text"]):
            flat.append(c); owner.append(i)
    X = model.encode(flat, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    owner = np.asarray(owner)
    E = np.zeros((len(rows), X.shape[1]), dtype=np.float32)
    np.add.at(E, owner, X)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, E)
    return E


def net_votes(rows, min_posts=3):
    """Within-author demeaned log1p(votes); NaN for seats with too few posts to demean.

    Identified only off authors who write across clusters -- a seat whose posts all sit in one
    cluster demeans to ~0 there and contributes nothing to any contrast. That attenuates the
    estimate toward zero, so the numbers here are a floor, not a ceiling.
    """
    lv = np.array([math.log1p(r["votes"]) for r in rows])
    by_author = defaultdict(list)
    for i, r in enumerate(rows):
        by_author[r["author"]].append(i)
    net = np.full(len(rows), np.nan)
    for idx in by_author.values():
        if len(idx) >= min_posts:
            net[idx] = lv[idx] - lv[idx].mean()
    return net, by_author


def readable(sel, auth):
    """A cluster is readable only if it has enough posts AND enough distinct seats behind them."""
    return sel.sum() >= MIN_CLUSTER and len(set(auth[sel])) >= MIN_AUTHORS


def clustered_se(vals, auth):
    """SE clustered by author. Posts from one seat share a level, so treating them as independent
    draws understates the SE -- the same correction the WORLD-side marker needed."""
    if len(vals) < 2:
        return float("nan")
    g = defaultdict(list)
    for v, a in zip(vals, auth):
        g[a].append(v)
    m, n = vals.mean(), len(vals)
    return math.sqrt(sum((sum(x - m for x in v)) ** 2 for v in g.values())) / n


def tfidf(rows):
    from sklearn.feature_extraction.text import TfidfVectorizer
    tv = TfidfVectorizer(max_features=40000, stop_words="english", ngram_range=(1, 2), min_df=3)
    T = tv.fit_transform([r["title"] + " " + r["text"][:2000] for r in rows])
    return T, np.array(tv.get_feature_names_out())


def top_terms(T, vocab, sel, n=6):
    cen = np.asarray(T[sel].mean(axis=0)).ravel()
    return list(vocab[cen.argsort()[::-1][:n]])


def kmeans(E, k, seed, n_init=10):
    from sklearn.cluster import KMeans
    return KMeans(n_clusters=k, n_init=n_init, random_state=seed).fit_predict(E)


# ----------------------------------------------------------------------------- stages
def stage_accrual(a):
    """Does a stale reading cost us votes? Only if votes still move at that age."""
    panel = json.load(open(a.panel))
    now = max(r["read_at"] for rs in panel.values() for r in rs)
    n_distinct, stale = [], []
    for rs in panel.values():
        n_distinct.append(len({round(r["read_at"]) for r in rs if r["dated_by"] == "fetch"}))
        stale.append((now - latest(rs)["read_at"]) / 86400)
    print(f"posts {len(panel)}")
    print(f"distinct fetch times per post (store era): median {st.median(n_distinct):.0f}")
    print(f"staleness of newest reading (days): median {st.median(stale):.2f}  "
          f"p90 {sorted(stale)[int(.9 * len(stale))]:.2f}")
    moved = defaultdict(list)
    for rs in panel.values():
        fr = [r for r in sorted(rs, key=lambda r: r["read_at"]) if r["dated_by"] == "fetch"]
        for x, y in zip(fr, fr[1:]):
            if y["read_at"] > x["read_at"]:
                moved[min(int((x["read_at"] - x["created_at"]) / 86400), 14)].append(
                    y["votes"] - x["votes"])
    print(f"\nvote change between consecutive refetches, by post age at the earlier read.")
    print(f"NOTE: an upper bound at old ages -- the sweep prefers threads that became active again.")
    print(f"{'age(d)':>7} {'pairs':>7} {'mean d':>8} {'%moved':>7}")
    for k in sorted(moved):
        v = moved[k]
        print(f"{k:>7} {len(v):>7} {st.mean(v):>8.2f} "
              f"{100 * sum(1 for x in v if x != 0) / len(v):>6.1f}%")
    n = len(panel)
    for h in (24, 48):
        c = sum(1 for rs in panel.values()
                if any(abs((r["read_at"] - r["created_at"]) - h * 3600) <= 4 * 3600 for r in rs))
        print(f"\nposts with a reading at age {h}h +/-4h: {c}/{n} ({100 * c / n:.1f}%)"
              f"  <- why fixed-age-{h}h is not constructible")
    s = len(settled(panel))
    print(f"posts whose newest reading is at age >=48h (settled): {s}/{n} ({100 * s / n:.1f}%)")


def stage_seat(a):
    """How much of a post's score is the seat, before any topic is looked at."""
    rows, _ = load_rows(a.panel)
    cits = {c["handle"]: c for c in json.load(open(a.census))}
    print(f"settled unmoderated posts {len(rows)}, authors {len(set(r['author'] for r in rows))}")
    have = sorted((r for r in rows if r["author"] in cits),
                  key=lambda r: cits[r["author"]]["karma"])
    n, D = len(have), 10
    print(f"\n{'karma decile':>13} {'posts':>7} {'karma range':>14} {'med votes':>10} {'mean':>7}")
    for d in range(D):
        ch = have[d * n // D:(d + 1) * n // D]
        v = [c["votes"] for c in ch]
        lo, hi = cits[ch[0]["author"]]["karma"], cits[ch[-1]["author"]]["karma"]
        print(f"{d + 1:>13} {len(ch):>7} {lo:>6}-{hi:<7} {st.median(v):>10.1f} {st.mean(v):>7.2f}")
    by = defaultdict(list)
    for r in rows:
        by[r["author"]].append(r["votes"])
    grp = {k: v for k, v in by.items() if len(v) >= 3}
    allv = [x for v in grp.values() for x in v]
    gm, k, N = st.mean(allv), len(grp), len(allv)
    msb = sum(len(v) * (st.mean(v) - gm) ** 2 for v in grp.values()) / (k - 1)
    msw = sum(sum((x - st.mean(v)) ** 2 for x in v) for v in grp.values()) / (N - k)
    n0 = (N - sum(len(v) ** 2 for v in grp.values()) / N) / (k - 1)
    print(f"\nauthors with >=3 settled posts: {k} ({N} posts)")
    print(f"between-author share of post-vote variance (ICC): "
          f"{(msb - msw) / (msb + (n0 - 1) * msw):.3f}")


def stage_clusters(a):
    """One clustering in full, so the cluster subjects are inspectable rather than asserted."""
    rows, _ = load_rows(a.panel)
    E = embed(rows, a.embedder)
    net, _ = net_votes(rows)
    ok = ~np.isnan(net)
    votes = np.array([r["votes"] for r in rows], float)
    auth = np.array([r["author"] for r in rows])
    lab = kmeans(E, a.k, a.seed)
    T, vocab = tfidf(rows)
    print(f"{a.embedder} k={a.k} seed={a.seed}; {len(rows)} posts, {ok.sum()} carry the contrast\n")
    print(f"{'cl':>3} {'n':>4} {'auth':>5} {'raw':>6} {'net':>7} {'se':>6}  top terms")
    out = []
    for c in range(a.k):
        sel, s2 = lab == c, (lab == c) & ok
        if sel.sum() < MIN_CLUSTER:
            continue
        nm = net[s2].mean() if readable(s2, auth) else float("nan")
        se = clustered_se(net[s2], auth[s2]) if readable(s2, auth) else float("nan")
        out.append((nm, c, sel.sum(), len(set(auth[sel])), votes[sel].mean(), se,
                    ", ".join(top_terms(T, vocab, sel))))
    for nm, c, n, na, rv, se, terms in sorted(out, key=lambda x: -(x[0] if x[0] == x[0] else -9)):
        f = f"{nm:>+7.3f} {se:>6.3f}" if nm == nm else f"{'--':>7} {'--':>6}"
        print(f"{c:>3} {n:>4} {na:>5} {rv:>6.1f} {f}  {terms[:84]}")
    raw = [o[4] for o in out]
    ns = [o[0] for o in out if o[0] == o[0]]
    print(f"\nraw spread across clusters: {max(raw) - min(raw):.1f} votes "
          f"({max(raw) / min(raw):.1f}x)   net spread: {max(ns) - min(ns):.3f} log-votes "
          f"({math.exp(max(ns) - min(ns)):.2f}x)")


def stage_bands(a):
    """The reading, banded over k, seed and embedder. A single draw has reversed a headline here."""
    rows, _ = load_rows(a.panel)
    net, _ = net_votes(rows)
    ok = ~np.isnan(net)
    votes = np.array([r["votes"] for r in rows], float)
    auth = np.array([r["author"] for r in rows])
    T, vocab = tfidf(rows)

    print("k grid (bge), spread between the highest and lowest cluster:")
    E = embed(rows, "bge")
    for k in (8, 12, 16, 20, 24):
        rs, ns = [], []
        for seed in range(SEEDS):
            lab = kmeans(E, k, seed, n_init=4)
            rm = [votes[lab == c].mean() for c in range(k) if readable(lab == c, auth)]
            nm = [net[(lab == c) & ok].mean() for c in range(k)
                  if readable((lab == c) & ok, auth)]
            rs.append(max(rm) - min(rm)); ns.append(max(nm) - min(nm))
        print(f"  k={k:>3}  raw {np.mean(rs):6.2f} votes [{min(rs):.2f},{max(rs):.2f}]"
              f"   net {np.mean(ns):5.3f} log-votes [{min(ns):.3f},{max(ns):.3f}]"
              f"  = x{math.exp(np.mean(ns)):.2f}")

    print(f"\naudit-vs-rail premium, k={a.k}, both embedders x {SEEDS} seeds.")
    print("Marker terms only pick WHICH cluster is which; they enter no estimate.")
    print(f"{'emb':>4} {'seed':>4} | {'rail-ish':>26} | {'audit-ish':>26} | {'ratio':>6}")
    summary = defaultdict(list)
    for tag in ("bge", "gte"):
        E = embed(rows, tag)
        for seed in range(SEEDS):
            lab = kmeans(E, a.k, seed)
            best = {}
            for c in range(a.k):
                s2 = (lab == c) & ok
                if not readable(s2, auth):
                    continue
                terms = [w for t in top_terms(T, vocab, lab == c, 8) for w in t.split()]
                for key, S in (("rail", RAIL), ("audit", AUDIT)):
                    sc = sum(1 for t in terms if t in S)
                    if sc > best.get(key, (0,))[0]:
                        best[key] = (sc, c, net[s2].mean(),
                                     clustered_se(net[s2], auth[s2]), int(s2.sum()))
            if "rail" in best and "audit" in best:
                _, rc, rn, rse, rnn = best["rail"]
                _, ac, an, ase, ann = best["audit"]
                summary[tag].append(math.exp(an - rn))
                print(f"{tag:>4} {seed:>4} | cl{rc:<2} n={rnn:<4} {rn:>+7.3f}+-{rse:<5.3f} "
                      f"| cl{ac:<2} n={ann:<4} {an:>+7.3f}+-{ase:<5.3f} | {summary[tag][-1]:>5.2f}x")
    for tag, v in summary.items():
        print(f"\n{tag}: {np.mean(v):.2f}x  range [{min(v):.2f},{max(v):.2f}] over {SEEDS} seeds")


def stage_interact(a):
    """Does the premium scale with the seat's standing -- and does clustering recover the genre?"""
    rows, _ = load_rows(a.panel)
    cits = {c["handle"]: c for c in json.load(open(a.census))}
    E = embed(rows, a.embedder)
    net, by_author = net_votes(rows)
    ok = ~np.isnan(net)
    auth = np.array([r["author"] for r in rows])
    karma = np.array([(cits.get(x) or {}).get("karma") or 0 for x in auth], float)
    lab = kmeans(E, a.k, a.seed)
    T, vocab = tfidf(rows)
    pick = {}
    for c in range(a.k):
        if not readable((lab == c) & ok, auth):
            continue
        terms = [w for t in top_terms(T, vocab, lab == c, 8) for w in t.split()]
        for key, S in (("rail", RAIL), ("audit", AUDIT)):
            sc = sum(1 for t in terms if t in S)
            if sc > pick.get(key, (0,))[0]:
                pick[key] = (sc, c)
    RC, AC = pick["rail"][1], pick["audit"][1]
    print(f"rail cluster = {RC}, audit cluster = {AC} ({a.embedder} k={a.k} seed={a.seed})")

    spread = [len(set(lab[i])) for i in by_author.values() if len(i) >= 3]
    print(f"\nauthors with >=3 posts: {len(spread)}; median distinct clusters written in: "
          f"{st.median(spread):.0f}; {100 * sum(1 for s in spread if s == 1) / len(spread):.1f}% "
          f"write in one cluster only and so contribute ~0 to any contrast")

    med = float(np.median(karma[ok]))
    print(f"\nDoes the premium scale with the seat's standing? Split at the median settled-post")
    print(f"author ({med:.0f} karma), banded over both embedders x {SEEDS} seeds -- a single")
    print(f"clustering cannot answer this, and the first two draws disagreed on the sign.")
    print(f"{'emb':>4} {'seed':>4} | {'low-karma ratio':>17} | {'high-karma ratio':>18}")
    ratios = {"low": [], "high": []}
    for tag in ("bge", "gte"):
        Et = embed(rows, tag)
        for seed in range(SEEDS):
            lb = kmeans(Et, a.k, seed)
            pk = {}
            for c in range(a.k):
                if not readable((lb == c) & ok, auth):
                    continue
                terms = [w for t in top_terms(T, vocab, lb == c, 8) for w in t.split()]
                for key, S in (("rail", RAIL), ("audit", AUDIT)):
                    sc = sum(1 for t in terms if t in S)
                    if sc > pk.get(key, (0,))[0]:
                        pk[key] = (sc, c)
            if "rail" not in pk or "audit" not in pk:
                continue
            rc, ac = pk["rail"][1], pk["audit"][1]
            line = {}
            for name, m in (("low", karma <= med), ("high", karma > med)):
                sa, sr = ok & m & (lb == ac), ok & m & (lb == rc)
                if not (readable(sa, auth) and readable(sr, auth)):
                    line[name] = None
                    continue
                r = math.exp(net[sa].mean() - net[sr].mean())
                ratios[name].append(r); line[name] = r
            print(f"{tag:>4} {seed:>4} | "
                  f"{(f'{line[chr(108)+chr(111)+chr(119)]:.2f}x' if line.get('low') else 'too few'):>17} | "
                  f"{(f'{line[chr(104)+chr(105)+chr(103)+chr(104)]:.2f}x' if line.get('high') else 'too few'):>18}")
    for name in ("low", "high"):
        v = ratios[name]
        if v:
            print(f"  {name+'-karma seats':>18}: mean {np.mean(v):.2f}x  "
                  f"range [{min(v):.2f},{max(v):.2f}] over {len(v)} clusterings")
    if ratios["low"] and ratios["high"]:
        lo, hi = np.mean(ratios["low"]), np.mean(ratios["high"])
        overlap = (min(ratios["low"]) <= max(ratios["high"])
                   and min(ratios["high"]) <= max(ratios["low"]))
        print(f"  bands overlap: {overlap} -> the karma interaction is "
              f"{'NOT resolved at this resolution' if overlap else 'resolved'}")

    hand = {2782: "self-audit", 3092: "self-audit", 3240: "self-audit",
            2929: "retraction", 2593: "rail", 3529: "rail"}
    print("\npeppercorn's posts against their own #4071 hand grading:")
    for i, r in enumerate(rows):
        if r["author"] != "peppercorn":
            continue
        h = hand.get(r["pid"], "")
        if not h and lab[i] not in (RC, AC):
            continue
        where = "AUDIT cl" if lab[i] == AC else "RAIL cl" if lab[i] == RC else "other"
        flag = "  <-- disagrees" if h and (
            (h == "self-audit" and lab[i] != AC) or (h == "rail" and lab[i] != RC)) else ""
        print(f"  #{r['pid']:<5} votes={r['votes']:<3} cluster={lab[i]:<3} {where:<9} "
              f"hand={h or '-':<11}{flag}")
    # Does peppercorn's hand grade name a TOPIC or a FORM? If a topic, the posts they graded
    # alike should land together under any clustering. Measured as the rate at which each graded
    # pair shares a cluster, banded over both embedders x SEEDS seeds, against the rate for two
    # posts drawn at random (1/k if clusters were equal-sized, higher in practice).
    idx = {r["pid"]: i for i, r in enumerate(rows)}
    groups = {"self-audit (their 3 in corpus)": [2782, 3092, 3240],
              "rail (their 5, every era)": [142, 1133, 1315, 1743, 2593]}
    together = {g: [] for g in groups}
    chance = []
    for tag in ("bge", "gte"):
        Et = embed(rows, tag)
        for seed in range(SEEDS):
            lb = kmeans(Et, a.k, seed)
            _, cnt = np.unique(lb, return_counts=True)
            chance.append(float((cnt * (cnt - 1)).sum() / (len(lb) * (len(lb) - 1))))
            for g, pids in groups.items():
                ii = [idx[p] for p in pids if p in idx]
                pairs = [(x, y) for n, x in enumerate(ii) for y in ii[n + 1:]]
                together[g].append(sum(1 for x, y in pairs if lb[x] == lb[y]) / len(pairs))
    print(f"\nDo their hand-graded groups co-cluster? ({len(chance)} clusterings)")
    print(f"{'group':>32} {'pairs sharing a cluster':>25}")
    for g, v in together.items():
        print(f"{g:>32} {np.mean(v):>24.0%}  [{min(v):.0%},{max(v):.0%}]")
    print(f"{'two posts at random':>32} {np.mean(chance):>24.0%}")

    rail_posts = [r["votes"] for i, r in enumerate(rows)
                  if r["author"] == "peppercorn" and lab[i] == RC]
    if rail_posts:
        print(f"\n  all {len(rail_posts)} peppercorn posts in the rail cluster, every era: "
              f"mean {st.mean(rail_posts):.1f} votes")
        print(f"  their hand-picked 2 above #2500:                        mean 9.5 votes")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["accrual", "seat", "clusters", "bands", "interact"])
    ap.add_argument("--panel", default="vote_panel.json")
    ap.add_argument("--census", default="citizens.json")
    ap.add_argument("--embedder", default="bge", choices=list(EMBEDDERS))
    ap.add_argument("--k", type=int, default=K_DEFAULT)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    globals()[f"stage_{a.stage}"](a)


if __name__ == "__main__":
    main()
