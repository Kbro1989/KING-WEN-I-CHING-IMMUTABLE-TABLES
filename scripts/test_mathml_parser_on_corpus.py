#!/usr/bin/env python3
"""
Test MathMLParser on the STORED MathML — does it work at all?

The corpus contains full MathML with placement (msub/msubsup/mo/mrow).
If MathMLParser.parse() returns None for these, that is the bug: PATH A
never produces anything, so the pipeline always falls back to regex on the
LaTeX alttext, discarding placement.
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

print("=" * 80)
print("MathMLParser ON STORED MATHML")
print("=" * 80)
print()

TARGETS = [
    r"\Delta_{n}\coloneqq",
    r"\Reg_{x}",
    r"\operatorname*{ess",
    r"\log\bar{\pi}",
]

parser = MathMLParser()

for needle in TARGETS:
    hits = [e for e in eqs if needle in (e.get("latex") or "")]
    if not hits:
        print(f"  {needle}: NO MATCH")
        continue
    for h in hits[:1]:
        mml = h.get("mathml") or ""
        print(f"--- {needle} ---")
        print(f"  LATEX : {h.get('latex')[:100]}")
        print(f"  MATHML len: {len(mml)}")
        try:
            soup = BeautifulSoup(mml, "html.parser")
            tag = soup.find("math")
            if tag is None:
                print("  -> soup.find('math') returned None")
                continue
            expr, unsupported = parser.parse(tag)
            print(f"  -> EXPR : {expr}")
            print(f"  -> UNSUP: {unsupported}")
        except Exception as e:
            print(f"  -> CRASH: {type(e).__name__}: {e}")
        print()

# --- bulk test: how many of the 991 produce a tree expression? ---
print("=" * 80)
print("BULK — how many of 991 equations yield a tree expression?")
print("=" * 80)
ok = 0
none = 0
crash = 0
samples = []
for e in eqs:
    mml = e.get("mathml")
    if not mml:
        none += 1
        continue
    try:
        soup = BeautifulSoup(mml, "html.parser")
        tag = soup.find("math")
        if tag is None:
            none += 1
            continue
        expr, unsup = parser.parse(tag)
        if expr:
            ok += 1
            if len(samples) < 5:
                samples.append((e.get("latex"), expr))
        else:
            none += 1
    except Exception:
        crash += 1

print(f"  produced an expression : {ok}")
print(f"  produced None          : {none}")
print(f"  crashed                : {crash}")
print()
for L, x in samples:
    print(f"  LATEX : {str(L)[:80]}")
    print(f"  EXPR  : {str(x)[:100]}")
    print()
