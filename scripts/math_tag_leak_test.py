#!/usr/bin/env python3
"""
Focused: are EQUATION TAGS like "(1)" leaking into the math?

The chrome test was negative overall, but `paren_number` appeared 58x in the
CLEAN set and only 1x in the failing set. That inversion needs explaining —
if tags were contaminating, they would be in the FAILING set.

Two possibilities:
  A) "(1)" is captured chrome  -> it would appear as a trailing tag on
     otherwise-valid equations, and the equation should still parse.
  B) "(1)" is legitimate math  -> e.g. f(1), a coefficient, a binomial.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"

print("=" * 78)
print("EQUATION-TAG LEAK TEST — every latex containing (NNN)")
print("=" * 78)
print()

hits = []
for jf in sorted(CORPUS.glob("*.json")):
    try:
        d = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        continue
    for e in d.get("equations", []):
        L = e.get("latex") or ""
        if re.search(r"\(\s*\d{1,3}\s*\)", L):
            hits.append((jf.stem, L, e.get("is_display"), e.get("index")))

print(f"equations containing (NNN): {len(hits)}")
print()

# Is the tag at the END (=> chrome) or INSIDE (=> real math)?
trailing = []
inside = []
for paper, L, disp, idx in hits:
    if re.search(r"\(\s*\d{1,3}\s*\)\s*[.,]?\s*$", L):
        trailing.append((paper, L, disp, idx))
    else:
        inside.append((paper, L, disp, idx))

print(f"  tag at END of expression   (chrome signature): {len(trailing)}")
print(f"  tag INSIDE the expression  (real math)       : {len(inside)}")
print()

print("=" * 78)
print("END-OF-EXPRESSION CASES (would be chrome)")
print("=" * 78)
print()
for paper, L, disp, idx in trailing[:20]:
    rec, _ = recover_latex(L)
    print(f"[{paper} idx={idx} display={disp}]")
    print(f"  LATEX : {L[:120]}")
    print(f"  RECOV : {rec[:100]}")
    print()
if not trailing:
    print("  NONE. No equation carries a trailing tag.")
print()

print("=" * 78)
print("INSIDE-EXPRESSION CASES (real math) — sample")
print("=" * 78)
print()
for paper, L, disp, idx in inside[:12]:
    m = re.search(r".{0,30}\(\s*\d{1,3}\s*\).{0,30}", L)
    print(f"  [{paper}] …{m.group(0) if m else L[:70]}…")
print()

# --- the decisive check: does the raw HTML put a tag inside <math>? ---
print("=" * 78)
print("EXTRACTOR CHECK — does <math> contain an eqno/tag element?")
print("=" * 78)
print()
# the parser writes is_display; check whether tag-bearing equations are display
disp_tags = sum(1 for _p, _L, d_, _i in hits if d_)
print(f"  tag-bearing equations that are DISPLAY : {disp_tags} / {len(hits)}")
print()
print("  If tags were chrome captured from the display wrapper, they would be")
print("  100% display and always trailing. Above shows the split.")
