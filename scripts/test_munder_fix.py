#!/usr/bin/env python3
"""
Verify the munder/munderover fix on the actual corpus equation.

Target: ‖e‖_{1,μ_x} := ∑_{y∈𝒴} μ_x(y)|e(y)|
The ∑ has its limit UNDERNEATH (display mode) → <munder> in MathML.
Before the fix: the limit was dropped → "Sum" alone.
After the fix:  → "Sum_{y in Y}" or similar.
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402
from mathml_parser import MathMLParser  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus" / "2605.00155.json"
d = json.loads(CORPUS.read_text(encoding="utf-8", errors="replace"))
eqs = d.get("equations", [])

# Find the target equation
TARGET = r"\|e\|_{1,\mu_{x}}"
hits = [e for e in eqs if TARGET in (e.get("latex") or "")]
print("=" * 80)
print("VERIFY munder/munderover FIX")
print("=" * 80)
print()
print(f"  target latex : {hits[0].get('latex')[:100] if hits else 'NOT FOUND'}")
print()

if not hits:
    print("  (searching looser)")
    hits = [e for e in eqs if "mu_{x}" in (e.get("latex") or "") and "sum" in (e.get("latex") or "")]
    print(f"  loose matches: {len(hits)}")

if hits:
    h = hits[0]
    mml = h.get("mathml") or ""
    print(f"  stored mathml len: {len(mml)}")
    print()

    # Show the munder/munderover structure
    soup = BeautifulSoup(mml, "html.parser")
    for tag in soup.find_all(["munder", "munderover"]):
        kids = [c.name for c in tag.find_all(recursive=False)]
        print(f"  <{tag.name}> children: {kids}")
        for c in tag.find_all(recursive=False):
            print(f"    <{c.name}> text={c.get_text()[:40]!r}")
    print()

    # Parse it
    parser = MathMLParser()
    tag = soup.find("math")
    if tag:
        expr, unsup = parser.parse(tag)
        print(f"  PARSED EXPR : {expr}")
        print(f"  UNSUPPORTED : {unsup}")
        print()

        # Check: does the expression contain the summation limits?
        has_sum = "Sum" in str(expr)
        has_limit = "y" in str(expr) and ("in" in str(expr) or "Y" in str(expr))
        print(f"  contains 'Sum'           : {has_sum}")
        print(f"  contains limit (y in Y)  : {has_limit}")
        print()
        if has_sum and has_limit:
            print("  ✓ FIX VERIFIED — summation limits preserved")
        elif has_sum:
            print("  ✗ STILL BROKEN — Sum present but limits dropped")
        else:
            print("  ? Sum not in expression (may be nested or renamed)")
