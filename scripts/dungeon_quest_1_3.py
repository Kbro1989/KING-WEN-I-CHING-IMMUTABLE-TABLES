#!/usr/bin/env python3
"""
QUEST 1+2 — per-paper inventory and cross-generation matching for one paper.

Verifies the claimed progression for 2605.00155 against actual data, and
establishes the source->recovery mapping keyed on the IMMUTABLE WITNESS:
the original LaTeX, not the recovered string.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
PAPER = "2605.00155"

GENS = [
    ("original",   "math_recovery"),
    ("after_fix",  "math_recovery_after_fix"),
    ("nested_fix", "math_recovery_nested_fix"),
    ("v3_bigop",   "math_recovery_v3"),
    ("v4_escapes", "math_recovery_v4"),
]

# --- source inventory (the witness) ---
src = ROOT / "DATASETS" / "arxiv_html_corpus" / f"{PAPER}.json"
d = json.loads(src.read_text(encoding="utf-8", errors="replace"))
src_eqs = d.get("equations", [])
print("=" * 80)
print(f"QUEST 1 — SOURCE INVENTORY  ({PAPER})")
print("=" * 80)
print()
print(f"  title          : {(d.get('structure') or {}).get('title')}")
print(f"  url            : {d.get('url')}")
print(f"  equations      : {len(src_eqs)}")
disp = sum(1 for e in src_eqs if e.get("is_display"))
print(f"  display        : {disp}")
print(f"  inline         : {len(src_eqs) - disp}")
print()

# --- per-generation match on the immutable witness ---
print("=" * 80)
print("QUEST 2 — CROSS-GENERATION MATCH (keyed on source LaTeX)")
print("=" * 80)
print()

per_gen = {}
for label, sub in GENS:
    p = ROOT / "DATASETS" / sub / f"{PAPER}_recovery.json"
    if not p.exists():
        print(f"  {label:12s} MISSING {p}")
        continue
    j = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    by_latex = {}
    for r in j.get("results", []):
        L = r.get("latex")
        if L:
            by_latex[L] = r
    per_gen[label] = by_latex
    rec = sum(1 for r in by_latex.values() if r.get("recoverable"))
    sol = sum(1 for r in by_latex.values() if r.get("solvable"))
    print(f"  {label:12s} matched={len(by_latex):>5}  recoverable={rec:>5}  solvable={sol:>5}")

print()
print(f"  {'gen':12s} {'recoverable':>12s} {'solvable':>10s} {'delta_sol':>10s}")
print("-" * 80)
prev = None
for label, _ in GENS:
    if label not in per_gen:
        continue
    sol = sum(1 for r in per_gen[label].values() if r.get("solvable"))
    dd = "" if prev is None else f"{sol - prev:+d}"
    print(f"  {label:12s} {'':>12s} {sol:>10d} {dd:>10s}")
    prev = sol

# --- QUEST 3: the regressions ---
print()
print("=" * 80)
print("QUEST 3 — REGRESSIONS between consecutive generations")
print("=" * 80)
print()
order = [l for l, _ in GENS if l in per_gen]
for a, b in zip(order, order[1:]):
    lost = []
    for L, ra in per_gen[a].items():
        rb = per_gen[b].get(L)
        if rb and ra.get("solvable") and not rb.get("solvable"):
            lost.append((L, ra, rb))
    if lost:
        print(f"  {a} -> {b}: {len(lost)} LOST solvable")
        for L, ra, rb in lost:
            print(f"    LATEX   : {L[:100]}")
            print(f"    A recov : {str(ra.get('recovered'))[:90]}")
            print(f"    B recov : {str(rb.get('recovered'))[:90]}")
            print(f"    B err   : {rb.get('error')}")
            print()
    else:
        print(f"  {a} -> {b}: no regressions")
