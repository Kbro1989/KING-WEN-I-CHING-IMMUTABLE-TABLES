#!/usr/bin/env python3
"""
AST DUNGEON LEVEL 0 — fix the duplicate-witness collapse.

DEFECT (found by external audit, verified here):
    by_latex[L] = r
keys on `latex` alone, so duplicate occurrences COLLAPSE. For 2605.00155:
    991 source equations but only 651 unique LaTeX -> 340 occurrences lost.

Consequence: "651 matched" does NOT mean 651 of 991 occurrences were matched.
It means 651 unique strings were represented.

FIX: the witness needs a LOCATION dimension.
    (paper, source_index, latex) -> recovery

This script verifies the collapse, then re-runs the match with occurrence
identity preserved, and measures how much the collapse was hiding.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
PAPER = "2605.00155"

GENS = [
    ("original",   "math_recovery"),
    ("after_fix",  "math_recovery_after_fix"),
    ("nested_fix", "math_recovery_nested_fix"),
    ("v3_bigop",   "math_recovery_v3"),
    ("v4_escapes", "math_recovery_v4"),
    ("v5_logfix",  "math_recovery_v5"),
    ("v6_funcjoin", "math_recovery_v6"),
]

# ---------------------------------------------------------------- 1. the defect
src = json.loads((ROOT / "DATASETS" / "arxiv_html_corpus" / f"{PAPER}.json")
                 .read_text(encoding="utf-8", errors="replace"))
src_eqs = src.get("equations", [])
src_latex = [e.get("latex") for e in src_eqs if e.get("latex")]

print("=" * 80)
print("LEVEL 0 — VERIFY THE DUPLICATE-WITNESS COLLAPSE")
print("=" * 80)
print()
print(f"  source equations        : {len(src_eqs)}")
print(f"  with latex              : {len(src_latex)}")
print(f"  UNIQUE latex            : {len(set(src_latex))}")
print(f"  COLLAPSED occurrences   : {len(src_latex) - len(set(src_latex))}")
print()

dupes = Counter(src_latex)
print("  most-repeated witnesses:")
for L, n in dupes.most_common(6):
    print(f"    x{n:<3d} {L[:96]}")
print()

# ---------------------------------------------------------------- 2. the fix
print("=" * 80)
print("LEVEL 0 — MATCH WITH OCCURRENCE IDENTITY PRESERVED")
print("=" * 80)
print()
print("  key: (source_index, latex)   — not latex alone")
print()

per_gen = {}
for label, sub in GENS:
    p = ROOT / "DATASETS" / sub / f"{PAPER}_recovery.json"
    if not p.exists():
        continue
    j = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    # occurrence-aware: keep EVERY record, keyed by (index, latex)
    by_occ = {}
    for r in j.get("results", []):
        L = r.get("latex")
        if not L:
            continue
        # Occurrence-aware key. Fall back to (index, latex) if the run predates
        # occurrence identity, so old artifacts still load.
        occ = r.get("occurrence")
        key = (occ if occ is not None else r.get("index"), L)
        by_occ[key] = r
    per_gen[label] = by_occ

print(f"  {'generation':13s} {'records':>9s} {'unique_latex':>13s} {'occurrences':>12s}")
print("-" * 80)
for label, _ in GENS:
    if label not in per_gen:
        continue
    occ = per_gen[label]
    uniq = len({L for (_i, L) in occ})
    print(f"  {label:13s} {len(occ):>9d} {uniq:>13d} {len(occ):>12d}")

print()
print("  source-side occurrence count vs recovery-side occurrence count:")
for label, _ in GENS:
    if label not in per_gen:
        continue
    print(f"    {label:13s} recovery occurrences = {len(per_gen[label])}   "
          f"(source = {len(src_latex)})")

# ---------------------------------------------------------------- 3. what it hid
print()
print("=" * 80)
print("LEVEL 0 — WHAT THE COLLAPSE WAS HIDING")
print("=" * 80)
print()
print("  For each generation, count solvable by OCCURRENCE vs by UNIQUE LATEX.")
print()
print(f"  {'generation':13s} {'solvable_occ':>13s} {'solvable_uniq':>14s} {'delta':>8s}")
print("-" * 80)
for label, _ in GENS:
    if label not in per_gen:
        continue
    occ = per_gen[label]
    sol_occ = sum(1 for r in occ.values() if r.get("solvable"))
    # unique view: first record per latex (what the old script did)
    seen = {}
    for (_i, L), r in occ.items():
        seen.setdefault(L, r)
    sol_uniq = sum(1 for r in seen.values() if r.get("solvable"))
    print(f"  {label:13s} {sol_occ:>13d} {sol_uniq:>14d} {sol_occ - sol_uniq:>+8d}")

print()
print("  => If delta != 0, the old 'matched/solvable' figures under-counted")
print("     because duplicate occurrences were silently dropped.")
