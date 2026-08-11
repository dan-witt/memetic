#!/usr/bin/env python3
"""Executable enumeration of the narrow-anchor population (no discretion): applies the rule
  "every single-language comp.lang.* lineage in the UTZOO archive with >= 2,500 merged raw
   articles whose lineage is alive at the archive end (a tape >= 141)"
to a full tape listing. Lineage = {net.lang.<old>, comp.lang.<lang>, lang.<lang>} merged
(prefix-stripped late tapes), truncated 1982-era names folded in; dialect/platform subgroups
(an extra dot component, e.g. lang.lisp.x, comp.lang.scheme.c, lang.forth.mac) are separate
groups and are excluded from the lineage. No upper cap. Emits the qualifying set + counts.
Tape listing: reuses <MEMETIC_WORKDIR>/utzoo_inventory.json if present, else scans the tapes
(name listing only) at ~/media/utzoo/tapes."""
import json, os, tarfile, collections
from pathlib import Path

WD = Path(os.environ.get("MEMETIC_WORKDIR", "."))
TAPES = Path(os.path.expanduser("~/media/utzoo/tapes"))
inv_f = WD / "utzoo_inventory.json"
if inv_f.exists():
    inv = json.load(open(inv_f))
else:
    counts, tmax = collections.Counter(), {}
    for fn in sorted(TAPES.glob("news*.tgz")):
        digits = "".join(c for c in fn.name if c.isdigit())
        if not digits: continue
        tno = int(digits[:3])
        try:
            tf = tarfile.open(fn, "r:gz")
            try:
                for mem in tf:
                    if not mem.isfile(): continue
                    p = mem.name.split("/")
                    if len(p) < 4 or not p[-1].isdigit(): continue
                    g = ".".join(p[2:-1])
                    counts[g] += 1; tmax[g] = max(tmax.get(g, 0), tno)
            except (tarfile.ReadError, EOFError, OSError): pass
            finally: tf.close()
        except (tarfile.ReadError, OSError): pass
    inv = {g: {"n": counts[g], "tape_max": tmax[g]} for g in counts}

# old net-era names that differ from the comp-era language name, incl. truncated 1982 dirs
OLD = {"f77": "fortran", "mod2": "modula2", "st80": "smalltalk", "pasca": "pascal", "prolo": "prolog"}
fam = collections.defaultdict(lambda: {"n": 0, "tape_max": 0, "groups": {}})
for g, v in inv.items():
    parts = g.split(".")
    if parts[:2] == ["net", "lang"] and len(parts) == 3:
        lang = OLD.get(parts[2], parts[2])
    elif parts[:2] == ["comp", "lang"] and len(parts) == 3:
        lang = parts[2]
    elif parts[0] == "lang" and len(parts) == 2:
        lang = parts[1]
    else:
        continue          # extra dot component => dialect/platform subgroup, or unrelated
    f = fam[lang]
    f["n"] += v["n"]; f["tape_max"] = max(f["tape_max"], v["tape_max"]); f["groups"][g] = v["n"]

FLOOR, END_TAPE = 2500, 141
# the rule's "single-language" predicate, applied by name: 'misc' is definitionally the
# catch-all for languages WITHOUT their own group, not a language lineage.
NOT_A_LANGUAGE = {"misc"}
qual = {l: f for l, f in fam.items()
        if l not in NOT_A_LANGUAGE and f["n"] >= FLOOR and f["tape_max"] >= END_TAPE}
out = {"rule": f"single-language comp.lang lineage, merged raw articles >= {FLOOR}, lineage alive at tape >= {END_TAPE}; no upper cap",
       "qualifying": {l: {"raw_merged": f["n"], "tape_max": f["tape_max"], "groups": f["groups"]}
                      for l, f in sorted(qual.items(), key=lambda kv: -kv[1]["n"])},
       "excluded_below_floor_or_dead": {l: f["n"] for l, f in sorted(fam.items(), key=lambda kv: -kv[1]["n"]) if l not in qual}}
json.dump(out, open(WD / "anchor_enumeration.json", "w"), indent=1)
print(f"{len(qual)} qualifying lineages:")
for l, f in sorted(qual.items(), key=lambda kv: -kv[1]["n"]):
    print(f"  {f['n']:6d}  {l:12s} {sorted(f['groups'])}")
