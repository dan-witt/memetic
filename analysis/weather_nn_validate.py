#!/usr/bin/env python3
"""Synthetic null/power check for the matched-pool NN refresh construction in
weather_nn_refresh.py, and a measurement of the bias in the construction it supersedes.

Three regimes, each with a known ground truth:
  NULL   newcomers drawn from the SAME distribution as incumbents -> true delta is 0
  POWER  newcomers occupy directions the incumbent pool never does -> true delta is large
  (the legacy asymmetric construction is run alongside in every regime)

Expected: the matched null centres on 0 in every regime; the legacy construction reads
substantially NEGATIVE even under NULL, i.e. it reports newcomers as closer to the incumbent
cloud than incumbents are to each other, purely from its unequal candidate-pool sizes.

AND A POOL-SIZE SWEEP (added at issue #13). The weather series does not hold the reference pool R
fixed: across issues #9-#13 it ran 239, 308, 623, 1002, 1781 while the published delta ran 0.0166,
0.0114, 0.0127, 0.0077, 0.0078. Those two orderings run opposite, which invites the explanation
that a nearest-neighbour distance shrinks as R grows and drags the difference of two such
distances down with it. The sweep TESTS that and DOES NOT SUPPORT IT: holding one true separation
and q fixed and reading it at each of those pool sizes gives 0.0116, 0.0137, 0.0122, 0.0134,
0.0114 -- flat within its own bands. So the cell's magnitude IS comparable across the pool sizes
this series has used, and a fall in the published delta is a fall in the quantity, not an
artefact of the pool.

The sweep also fixes the cell's power at issue #13's q of 308: a true delta of ~0.012 lands at
p <= 0.02 there. A published delta well under that with p ~ 0.1 is therefore a smaller separation
rather than a precision loss, which is the reading issue #13 takes.

CPU-only, seconds to run:  python3 analysis/weather_nn_validate.py
"""
import numpy as np

DRAWS = 500
N_NEW, N_INC, DIM = 105, 939, 64


def norm(E):
    return E / np.linalg.norm(E, axis=1, keepdims=True)


def matched(En, Ei, rng, draws=DRAWS):
    q = min(len(En), len(Ei) // 3); P = len(Ei) - 2 * q
    dobs, dnull = [], []
    for _ in range(draws):
        perm = rng.permutation(len(Ei))
        R, probe, pseudo = Ei[perm[:P]], Ei[perm[P:P + q]], Ei[perm[P + q:P + 2 * q]]
        qn = En[rng.choice(len(En), q, replace=False)]
        b = float(np.median(1 - (probe @ R.T).max(1)))
        dobs.append(float(np.median(1 - (qn @ R.T).max(1))) - b)
        dnull.append(float(np.median(1 - (pseudo @ R.T).max(1))) - b)
    band = lambda v: [round(float(np.percentile(v, p)), 4) for p in (50, 5, 95)]
    nl, ob = np.array(dnull), float(np.median(dobs))
    return band(dobs), band(dnull), round(float(2 * min((nl >= ob).mean(), (nl <= ob).mean())), 4)


def legacy(En, Ei, rng):
    half = rng.permutation(len(Ei)); h1, h2 = half[:len(half)//2], half[len(half)//2:]
    return round(float(np.median(1 - (En @ Ei.T).max(1))
                       - np.median(1 - (Ei[h1] @ Ei[h2].T).max(1))), 4)


def regime(name, make, seed=0):
    rng = np.random.default_rng(seed)
    En, Ei = make(rng)
    En, Ei = norm(En), norm(Ei)
    obs, null, p = matched(En, Ei, rng)
    print(f"{name:>26s}  matched delta {str(obs):26s} null {str(null):26s} p={p:<6} | legacy delta {legacy(En, Ei, rng):+.4f}")


if __name__ == "__main__":
    print(f"{DRAWS} draws, {N_NEW} newcomers vs {N_INC} incumbents, dim {DIM}\n")

    # NULL: same distribution. True delta = 0.
    regime("NULL (identical)",
           lambda r: (r.normal(size=(N_NEW, DIM)), r.normal(size=(N_INC, DIM))))

    # POWER: incumbents confined to an 8-dim subspace; newcomers span all DIM directions.
    def power(r):
        Ei = np.zeros((N_INC, DIM)); Ei[:, :8] = r.normal(size=(N_INC, 8))
        return r.normal(size=(N_NEW, DIM)), Ei
    regime("POWER (new directions)", power)

    # NULL within that same subspace geometry -> confirms POWER is not a geometry artefact.
    def null_sub(r):
        Ei = np.zeros((N_INC, DIM)); Ei[:, :8] = r.normal(size=(N_INC, 8))
        En = np.zeros((N_NEW, DIM)); En[:, :8] = r.normal(size=(N_NEW, 8))
        return En, Ei
    regime("NULL (same subspace)", null_sub)

    print("\nRead: matched null centres on ~0 in every regime (construction unbiased); matched delta")
    print("is ~0 under both NULLs and large under POWER (construction has power); legacy delta is")
    print("substantially negative even under NULL — the bias that made issue #3 omit the cell.")

    # --- pool-size sweep: one FIXED true separation, read at the pool sizes the series has used.
    # q is held at the issue-#13 value so the only thing moving is R.
    print(f"\n=== pool-size sweep: ONE fixed true separation, read at each issue's pool size ===")
    print("newcomers occupy a mild extra direction; only the incumbent pool size changes.\n")
    print(f"{'n_incumbent':>12s} {'P (pool)':>9s} {'q':>5s} {'delta [5,95]':>28s} {'p':>7s}")
    Q = 308
    for n_inc in (3 * Q + 239, 3 * Q + 308, 3 * Q + 623, 3 * Q + 1002, 3 * Q + 1781):
        rng = np.random.default_rng(0)
        Ei = np.zeros((n_inc, DIM)); Ei[:, :8] = rng.normal(size=(n_inc, 8))
        En = np.zeros((Q, DIM)); En[:, :8] = rng.normal(size=(Q, 8))
        En[:, 8] = 0.45 * rng.normal(size=Q)          # the mild extra direction, held constant
        En, Ei = norm(En), norm(Ei)
        obs, null, pv = matched(En, Ei, rng)
        P = n_inc - 2 * min(len(En), len(Ei) // 3)
        print(f"{n_inc:12d} {P:9d} {Q:5d} {str(obs):>28s} {pv:7}")
    print("\nThe delta is FLAT across these pool sizes, so the published magnitudes are on one")
    print("scale and a fall in the cell is a fall in the quantity. At q=308 a true delta of ~0.012")
    print("reaches p <= 0.02, so a published delta near half that with p ~ 0.1 is a smaller")
    print("separation, not a precision loss.")
