#!/usr/bin/env python3
"""
PLACEMENT DIAGNOSTIC — is the missing structure in the MathML, or lost later?

The pipeline has TWO paths (math_recovery_tool.process_paper):
    PATH A: tree-derived expression from MathML   (preferred)
    PATH B: regex recovery from the LaTeX alttext (fallback)

If PATH A is producing the broken output, the fix is in the tree parser.
If PATH A is not being used at all, we are throwing away the placement data
that MathML already encodes (mrow/mfrac/msub/msup nesting).

This prints, for the specific failing equations the user identified:
    - the LaTeX alttext (source witness)
    - the MathML tree  (PLACEMENT — authoritative)
    - what PATH A produced
    - what PATH B produced
    - which path was actually used
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus" / "2605.00155.json"
d = json.loads(CORPUS.read_text(encoding="utf-8", errors="replace"))
eqs = d.get("equations", [])

print("=" * 80)
print("PLACEMENT DIAGNOSTIC — 2605.00155")
print("=" * 80)
print(f"  source equations: {len(eqs)}")
print(f"  unique latex    : {len({e.get('latex') for e in eqs})}")
print()

# does the corpus even STORE the tree expression?
with_expr = sum(1 for e in eqs if e.get("expr"))
with_unsup = sum(1 for e in eqs if e.get("tree_unsupported"))
print(f"  records with tree expr  : {with_expr}")
print(f"  records with unsupported: {with_unsup}")
print()

# what keys does a record have?
print("  record keys:", sorted(eqs[0].keys()) if eqs else "none")
print()

TARGETS = [
    ("SET BUILDER (Delta_n)", r"\Delta_{n}\coloneqq"),
    ("CUSTOM OPERATOR (Reg)", r"\Reg_{x}"),
    ("STARRED OPERATOR", r"\operatorname*{ess"),
]

for label, needle in TARGETS:
    print("=" * 80)
    print(f"{label}   searching: {needle}")
    print("=" * 80)
    hits = [e for e in eqs if needle in (e.get("latex") or "")]
    if not hits:
        print("  (no exact match — searching looser)")
        key = needle.split("{")[0].strip("\\")
        hits = [e for e in eqs if key in (e.get("latex") or "")]
    print(f"  matches: {len(hits)}")
    for h in hits[:2]:
        print()
        print(f"  LATEX  : {h.get('latex')}")
        print(f"  EXPR   : {str(h.get('expr'))[:200]}")
        print(f"  UNSUP  : {h.get('tree_unsupported')}")
        print(f"  SOURCE : {h.get('source')}")
        print(f"  DISPLAY: {h.get('is_display')}")
        # show the stored mathml if present
        mml = h.get("mathml")
        if mml:
            print(f"  MATHML : {str(mml)[:400]}")
        else:
            print("  MATHML : (not stored in corpus)")
    print()
