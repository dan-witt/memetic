#!/usr/bin/env python3
"""The replication-anchor draw, end to end, exactly as executed on 2026-08-11.
The seed derives from the byte-exact rule string below — published so the derivation is
checkable, NOT as a claim of pre-registration (it was authored by the analyst mid-session;
the report's design-history section discloses the sequencing).

DISCLOSED ENUMERATION ERROR: at draw time the class was believed to have 8 non-lisp members;
a post-hoc audit found comp.lang.perl (5,348 merged raw articles) inside the window, making the
true population 9. The draw is NOT re-rolled: its results had been read, and re-randomizing a
draw after outcomes are known is an inadmissible post-hoc alteration (forking paths) regardless
of motive. The executed draw below stands; perl is DISCLOSED, NOT MEASURED — no perl cell exists
in this repository (measuring an anchor discovered after the verdict was read would extend the
analysis under the guise of repairing it); it remains runnable by any reader via the published
pipeline. See the report's Finding 2."""
import hashlib
import numpy as np

RULE = "single-language comp.lang lineage, merged raw articles in [2500,8000], lineage alive at tape >= 141"
POPULATION_AS_ENUMERATED_AT_DRAW_TIME = sorted(
    ["pascal", "ada", "forth", "fortran", "prolog", "modula2", "smalltalk", "scheme"])
OMITTED_IN_ERROR_FOUND_POST_HOC = ["perl"]

seed = int(hashlib.sha256(RULE.encode()).hexdigest()[:8], 16)
draw = sorted(np.random.default_rng(seed).choice(POPULATION_AS_ENUMERATED_AT_DRAW_TIME, 3,
                                                 replace=False).tolist())
print(f"seed = {seed}")
print(f"draw = {draw}")
assert seed == 704253817 and draw == ["forth", "scheme", "smalltalk"]
print("reproduces the executed draw")
