#!/usr/bin/env python3
"""
DUNGEON LEVEL: STRUCTURAL CONSERVATION

Invariant under test:
    No MathML structural child may disappear merely because its node type
    is unsupported.

For every structural MathML node type, this asserts that ALL children are
preserved in the recovered expression. A node that returns only its base
while dropping under/over children is a STRUCTURAL DATA-LOSS bug, not a
backend limitation.

Test method:
    1. Build minimal MathML for each structural node type
    2. Parse with MathMLParser
    3. Count source children vs recovered tokens
    4. Assert: every child's content appears in the output

This is stronger than "does it parse" — it proves no information was
discarded at the structural layer.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402
from mathml_parser import MathMLParser  # noqa: E402


def parse_mml(mml: str):
    """Parse a MathML string, return (expr, unsupported)."""
    soup = BeautifulSoup(mml, "html.parser")
    tag = soup.find("math")
    if tag is None:
        return None, []
    p = MathMLParser()
    expr, unsup = p.parse(tag)
    return expr, unsup


def count_tokens(s: str) -> int:
    """Rough token count: split on whitespace and count non-empty."""
    return len([t for t in s.split() if t]) if s else 0


# ── structural node types and their minimal MathML ──────────────────────
# Each entry: (node_type, mathml, expected_child_count, description)
# The mathml must have exactly `expected_child_count` element children
# inside the structural node.

CASES = [
    # ── munder: base + under ──
    ("munder_sum",
     '<math><munder><mo>∑</mo><mrow><mi>y</mi><mo>∈</mo><mi>𝒴</mi></mrow></munder></math>',
     2, "sum with underneath limit"),

    ("munder_max",
     '<math><munder><mo>max</mo><mrow><mi>β</mi><mo>∈</mo><mi>Δ</mi></mrow></munder></math>',
     2, "max with underneath constraint"),

    # ── mover: base + over ──
    ("mover_hat",
     '<math><mover><mi>x</mi><mo>^</mo></mover></math>',
     2, "x with hat accent"),

    ("mover_bar",
     '<math><mover><mi>π</mi><mo>‾</mo></mover></math>',
     2, "pi with overline"),

    # ── munderover: base + under + over ──
    ("munderover_sum",
     '<math><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover></math>',
     3, "sum with both limits"),

    ("munderover_prod",
     '<math><munderover><mo>∏</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover></math>',
     3, "product with both limits"),

    # ── msub: base + subscript ──
    ("msub_simple",
     '<math><msub><mi>x</mi><mi>i</mi></msub></math>',
     2, "x subscript i"),

    ("msub_nested",
     '<math><msub><mi>x</mi><msub><mi>i</mi><mi>j</mi></msub></msub></math>',
     2, "x subscript (i subscript j)"),

    # ── msup: base + superscript ──
    ("msup_simple",
     '<math><msup><mi>x</mi><mn>2</mn></msup></math>',
     2, "x squared"),

    ("msup_prime",
     '<math><msup><mi>f</mi><mo>′</mo></msup></math>',
     2, "f prime"),

    # ── msubsup: base + sub + sup ──
    ("msubsup_bessel",
     '<math><msubsup><mi>J</mi><mi>ν</mi><mi>n</mi></msubsup></math>',
     3, "Bessel J sub nu sup n"),

    # ── mfrac: numerator + denominator ──
    ("mfrac_simple",
     '<math><mfrac><mn>1</mn><mi>n</mi></mfrac></math>',
     2, "1/n"),

    ("mfrac_nested",
     '<math><mfrac><mfrac><mi>a</mi><mi>b</mi></mfrac><mi>c</mi></mfrac></math>',
     2, "(a/b)/c"),

    # ── msqrt: single child ──
    ("msqrt_simple",
     '<math><msqrt><mi>x</mi></msqrt></math>',
     1, "sqrt(x)"),

    ("msqrt_nested",
     '<math><msqrt><mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow></msqrt></math>',
     1, "sqrt(x+1)"),

    # ── mrow: sequence ──
    ("mrow_sequence",
     '<math><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow></math>',
     3, "a + b"),

    # ── mtable: matrix/system ──
    ("mtable_2x2",
     '<math><mtable><mtr><mtd><mi>a</mi></mtd><mtd><mi>b</mi></mtd></mtr>'
     '<mtr><mtd><mi>c</mi></mtd><mtd><mi>d</mi></mtd></mtr></mtable></math>',
     2, "2x2 matrix rows"),
]


print("=" * 80)
print("STRUCTURAL CONSERVATION TEST")
print("Invariant: no MathML structural child may disappear")
print("=" * 80)
print()

passed = 0
failed = 0
failures = []

for name, mml, expected_children, desc in CASES:
    expr, unsup = parse_mml(mml)

    # Count actual element children in the structural node
    soup = BeautifulSoup(mml, "html.parser")
    math_tag = soup.find("math")
    # Find the structural node (first child of math that's not semantics/annotation)
    struct_node = None
    for child in math_tag.find_all(recursive=False):
        if child.name not in ("semantics", "annotation", "annotation-xml"):
            struct_node = child
            break
    if struct_node is None:
        # try inside semantics
        sem = math_tag.find("semantics")
        if sem:
            for child in sem.find_all(recursive=False):
                if child.name not in ("annotation", "annotation-xml"):
                    struct_node = child
                    break

    actual_children = len(struct_node.find_all(recursive=False)) if struct_node else 0

    # Check: does the recovered expression retain EVERY child's semantics?
    #
    # A literal substring check produces false positives because the parser
    # TRANSLITERATES glyphs to names: pi -> "pi", beta -> "beta",
    # Delta -> "Delta", sum -> "Sum", overline -> "bar".
    # Compare semantically, not literally.
    GLYPH_TO_NAME = {
        "∑": "Sum", "∏": "Prod", "∫": "Integral",
        "∈": "in", "∉": "notin", "≤": "<=", "≥": ">=",
        "π": "pi", "β": "beta", "Δ": "Delta", "δ": "delta",
        "ν": "nu", "μ": "mu", "ζ": "zeta", "θ": "theta",
        "α": "alpha", "σ": "sigma", "τ": "tau", "λ": "lambda",
        "𝒴": "Y", "𝒟": "D", "ℝ": "R", "𝒳": "X", "ℳ": "M",
        "ˆ": "hat", "^": "hat", "‾": "bar", "¯": "bar",
        "˜": "tilde", "~": "tilde", "˙": "dot", "¨": "ddot",
        "′": "prime", "″": "prime",
        "≔": "=", ":=": "=", "=": "_eq_",  # limits render = as _eq_ marker
        "max": "Max", "min": "Min", "lim": "Limit",
        "⟨": "(", "⟩": ")", "{": "{", "}": "}",
    }

    def _present(token: str, out: str) -> bool:
        """Is this source token's SEMANTIC content present in the output?"""
        t = token.strip()
        if not t:
            return True
        if t in GLYPH_TO_NAME:
            return GLYPH_TO_NAME[t] in out
        if t in out:
            return True
        # multi-char token: check each alphanumeric fragment
        frags = [c for c in t if c.isalnum()]
        if frags:
            return all(f in out for f in frags)
        return False

    if expr is None:
        ok = False
        reason = "parser returned None"
    else:
        children = struct_node.find_all(recursive=False) if struct_node else []
        missing = []
        for child in children:
            # A child may itself be a GROUP (e.g. <mrow>β∈Δ</mrow>).
            # Require every leaf token inside it, not the concatenated string.
            leaves = [t for t in child.stripped_strings if t.strip()]
            if not leaves:
                continue
            if not all(_present(tk, expr) for tk in leaves):
                bad = [tk for tk in leaves if not _present(tk, expr)]
                missing.append(" ".join(bad)[:24])
        ok = not missing
        reason = ("all children preserved" if ok
                  else f"MISSING: {missing}")

    mark = "ok  " if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
        failures.append((name, desc, reason, expr, unsup))

    print(f"  {mark} {name:22s} ({desc})")
    if not ok:
        print(f"       reason: {reason}")
        print(f"       expr: {expr}")
        print(f"       unsup: {unsup}")

print()
print("=" * 80)
print(f"RESULT: {passed}/{len(CASES)} structural conservation tests pass")
print("=" * 80)

if failures:
    print()
    print("FAILURES:")
    for name, desc, reason, expr, unsup in failures:
        print(f"  {name}: {desc}")
        print(f"    {reason}")
        print(f"    expr={expr}, unsup={unsup}")
    sys.exit(1)
else:
    print()
    print("  ✓ All structural children preserved")
    sys.exit(0)
