#!/usr/bin/env python3
"""
RELATION IDENTITY CONSERVATION

Invariant: no two DISTINCT source relations may collapse into the same
recovered relation kind.

Preventing  \\sim -> '='  is anti-fabrication.
Preventing  \\sim and \\approx -> the SAME token  is relation IDENTITY.

Both are required. This test enforces the second.

Also covers bound structures: big operators must keep operator + limits, and
integrals must keep the differential.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402
from mathml_parser import MathMLParser, MO_MAP  # noqa: E402


def parse(mml):
    t = BeautifulSoup(mml, "html.parser").find("math")
    return MathMLParser().parse(t) if t is not None else (None, [])


print("=" * 80)
print("RELATION IDENTITY CONSERVATION")
print("=" * 80)
print()

# ── 1. every distinct source relation must map to a DISTINCT token ──────
DISTINCT = {
    "\\sim":      "∼",   # U+223C
    "\\approx":   "≈",   # U+2248
    "\\simeq":    "≃",   # U+2243
    "\\cong":     "≅",   # U+2245
    "\\asymp":    "≍",   # U+224D
    "\\propto":   "∝",   # U+221D
    "\\to":       "→",   # U+2192
    "\\mapsto":   "↦",   # U+21A6
    "\\in":       "∈",   # U+2208
    "\\equiv":    "≡",   # U+2261
    "\\neq":      "≠",   # U+2260
    "\\leq":      "≤",   # U+2264
    "\\geq":      "≥",   # U+2265
    ">":          ">",
    "<":          "<",
}

# build reverse map: token -> [source relations]
rev = {}
for src, glyph in DISTINCT.items():
    tok = MO_MAP.get(glyph)
    rev.setdefault(tok, []).append(src)

print("  source relation -> token:")
for src, glyph in DISTINCT.items():
    tok = MO_MAP.get(glyph)
    mark = "" if tok is not None else "   *** UNMAPPED ***"
    print(f"    {src:12s} ({glyph}) -> {tok!r}{mark}")

print()
collisions = {t: s for t, s in rev.items() if len(s) > 1}
if collisions:
    print("  COLLISIONS (distinct sources sharing one token):")
    for tok, srcs in collisions.items():
        print(f"    {tok!r}  <-  {srcs}")
else:
    print("  no collisions — every distinct relation has its own token")

print()
print("=" * 80)
print("BOUND STRUCTURES")
print("=" * 80)
print()

BOUNDS = [
    ("sum with limits",
     '<math><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover></math>',
     ["Sum", "i", "1", "n"]),

    ("integral with limits + differential",
     '<math><msubsup><mo>∫</mo><mi>α</mi><mi>∞</mi></msubsup><mi>φ</mi>'
     '<mo>(</mo><mi>z</mi><mo>)</mo><mi>𝑑</mi><mi>z</mi></math>',
     ["Integral", "alpha", "oo", "phi", "z", "d"]),

    ("max with domain bound",
     '<math><munder><mo>max</mo><mrow><mi>β</mi><mo>∈</mo><mi>Δ</mi></mrow></munder></math>',
     ["Max", "beta", "in", "Delta"]),

    # inside a limit token the relation is encoded as '_ge_' — that IS the
    # preserved form; requiring the literal '>=' would be wrong.
    ("inf with set body",
     '<math><munder><mo>inf</mo><mrow><mi>t</mi><mo>≥</mo><msub><mi>t</mi><mn>0</mn></msub></mrow></munder></math>',
     ["inf", "t", "ge", "0"]),

    ("bar decoration not multiplication",
     '<math><mover><mi>π</mi><mo>‾</mo></mover></math>',
     ["pi", "bar"]),

    ("hat decoration not disappearance",
     '<math><mover><mi>r</mi><mo>ˆ</mo></mover></math>',
     ["r", "hat"]),
]

bound_pass = 0
for label, mml, required in BOUNDS:
    expr, unsup = parse(mml)
    e = str(expr)
    missing = [t for t in required if t not in e]
    ok = not missing
    if ok:
        bound_pass += 1
    mark = "ok  " if ok else "FAIL"
    print(f"  {mark} {label:38s} -> {e!r}")
    if missing:
        print(f"       MISSING: {missing}")

print()
print("=" * 80)
rel_ok = not collisions
print(f"RELATION IDENTITY : {'PASS' if rel_ok else 'FAIL'}")
print(f"BOUND STRUCTURES  : {bound_pass}/{len(BOUNDS)} pass")
print("=" * 80)

if not rel_ok or bound_pass < len(BOUNDS):
    sys.exit(1)
print()
print("  ✓ relations distinct; bounds preserved")
