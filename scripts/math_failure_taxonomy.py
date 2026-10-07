#!/usr/bin/env python3
"""
Classify solve failures by LATEX FEATURE, not by Python error string.

The error histogram mixes two very different things:
  (a) genuine non-equations  -> correctly unsolvable, must NOT be "fixed"
  (b) real parser bugs       -> fixable

Grouping by Python error hides which LaTeX construct is at fault. This groups
by the construct so the highest-value fix is visible.
"""
import json
import re
from collections import Counter
from pathlib import Path

D = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\DATASETS")
SRC = D / "equation_solve_results_dual.jsonl"

# LaTeX constructs that commonly break naive -> Python translation
FEATURES = {
    "mbox": r"\\mbox\s*\{",
    "hbox": r"\\hbox\s*\{",
    "text": r"\\text\s*\{",
    "mathrm": r"\\mathrm\s*\{",
    "nested_dollar": r"\$\{",
    "pm": r"\\pm",
    "times": r"\\times",
    "approx": r"\\approx",
    "sim": r"\\sim",
    "perp": r"\\perp",
    "prime": r"['′]",
    "dbl_prime": r"″",
    "left_right": r"\\left|\\right",
    "frac": r"\\frac",
    "sqrt": r"\\sqrt",
    "sum": r"\\sum",
    "int": r"\\int",
    "prod": r"\\prod",
    "lim": r"\\lim",
    "sub_brace": r"_\s*\{",
    "sup_brace": r"\^\s*\{",
    "comma": r",",
    "semicolon": r";",
    "colon": r":",
    "pipe": r"\|",
    "tilde": r"~",
    "hat": r"\\hat",
    "bar": r"\\bar",
    "vec": r"\\vec",
    "dot": r"\\dot",
    "prime_sup": r"\^\{\\prime",
    "mathbb": r"\\mathbb",
    "mathcal": r"\\mathcal",
    "bf": r"\\mathbf",
    "displaystyle": r"\\displaystyle",
    "quad": r"\\quad",
    "nonascii": r"[^\x00-\x7F]",
    "degree": r"°|\\deg",
    "arcsec": r"″|\\arcsec",
    "rm": r"\\rm\b",
    "subscript_text": r"_\{\\rm",
}


def feats(s):
    return {k for k, p in FEATURES.items() if re.search(p, s)}


rows = []
with open(SRC, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue

print(f"loaded {len(rows)} rows from {SRC.name}")
print()

ok = [r for r in rows if r.get("solvable") or r.get("solved") or r.get("solution")]
bad = [r for r in rows if r not in ok]

print(f"  solvable   : {len(ok)}")
print(f"  unsolvable : {len(bad)}")
print()

# --- separate genuine non-equations from parse failures ---
GENUINE = ("no_equality", "multiple_equalities", "no_variables")
PARSE = ("invalid syntax", "line continuation", "tuple", "not subscriptable",
         "can't multiply sequence", "starred expression", "unsupported operand")

genuine, parsefail, other = [], [], []
for r in bad:
    e = str(r.get("error") or "")
    if any(g in e for g in GENUINE):
        genuine.append(r)
    elif any(p in e for p in PARSE):
        parsefail.append(r)
    else:
        other.append(r)

print("=" * 74)
print("SPLIT: genuine non-equations vs real parser failures")
print("=" * 74)
print(f"  genuine non-equation (correctly unsolvable) : {len(genuine):>5}")
print(f"  REAL parser failure (fixable)               : {len(parsefail):>5}")
print(f"  other / unclassified                        : {len(other):>5}")
print()

# --- what LaTeX constructs dominate the FIXABLE set? ---
print("=" * 74)
print("LATEX CONSTRUCTS IN THE FIXABLE SET (top 20)")
print("=" * 74)
c = Counter()
for r in parsefail:
    for f in feats(str(r.get("latex") or "")):
        c[f] += 1
for k, v in c.most_common(20):
    pct = 100 * v / max(len(parsefail), 1)
    print(f"  {v:>5}  {pct:>5.1f}%  {k}")
print()

print("=" * 74)
print("SAME CONSTRUCTS IN THE GENUINE NON-EQUATION SET (control)")
print("=" * 74)
c2 = Counter()
for r in genuine:
    for f in feats(str(r.get("latex") or "")):
        c2[f] += 1
for k, _ in c.most_common(12):
    print(f"  {c2.get(k,0):>5}  {k}")
print()

# --- show actual fixable samples ---
print("=" * 74)
print("FIXABLE SAMPLES — invalid syntax")
print("=" * 74)
n = 0
for r in parsefail:
    if "invalid syntax" in str(r.get("error") or ""):
        print(f"  {str(r.get('latex'))[:130]}")
        n += 1
        if n >= 15:
            break
print()

print("=" * 74)
print("FIXABLE SAMPLES — mbox / text wrapping")
print("=" * 74)
n = 0
for r in parsefail:
    L = str(r.get("latex") or "")
    if re.search(r"\\mbox|\\text\{", L):
        print(f"  {L[:130]}")
        n += 1
        if n >= 12:
            break
print()

# --- how many fixable rows contain \mbox alone? ---
mbox_only = [r for r in parsefail if re.search(r"\\mbox", str(r.get("latex") or ""))]
print(f"fixable rows containing \\mbox: {len(mbox_only)}")
print(f"  -> if \\mbox were neutralised, up to {len(mbox_only)} could move to solvable")
