#!/usr/bin/env python3
"""
Targeted regression test for the $ / \mbox{} fix.

Uses the REAL failing LaTeX from equation_solve_results_dual.jsonl.
Before the fix these produced "invalid syntax" and were lost.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from math_recovery_tool import recover_latex  # noqa: E402

CASES = [
    r"\mu_{\rm R.A.}=-(0.\!\!″067\pm 0.\!\!″010)\mbox{ yr${}^{-1}$}",
    r"N_{\rm H}=(13.1\pm 0.9)\times 10^{22}\mbox{ cm${}^{-2}$}",
    r"\dot{E}=5.6\times 10^{37}\mbox{ erg s${}^{-1}$}",
    r"f_{\rm X}=1.8\times 10^{-11}\mbox{ erg cm${}^{-2}$ s${}^{-1}$}",
    r"L_{\rm X}=5.4\times 10^{34}\mbox{ erg s${}^{-1}$}\,(d/\mbox{ 5 kpc})^{2}",
    r"N_{\rm H}=9.8_{-0.9}^{+1.2}\times 10^{22}\mbox{ cm${}^{-2}$}",
    # controls: must still work
    r"a = b + c",
    r"\frac{x}{y} = z",
    r"E = mc^{2}",
]

print("=" * 78)
print("REGRESSION TEST — $ / \\mbox{} recovery")
print("=" * 78)
print()

fail = 0
for latex in CASES:
    try:
        out, notes = recover_latex(latex)
    except Exception as e:
        print(f"  CRASH  {latex[:60]}")
        print(f"         {type(e).__name__}: {e}")
        fail += 1
        continue

    # the specific defects we are fixing
    has_dollar = "$" in out
    has_mbox = "\\mbox" in out
    has_textcmd = any(c in out for c in ("\\text", "\\mathrm", "\\mathcal",
                                         "\\mathbb", "\\rm{"))

    status = "ok  "
    if has_dollar or has_mbox:
        status = "FAIL"
        fail += 1

    print(f"  {status} {latex[:64]}")
    print(f"       -> {out[:110]}")
    if has_dollar:
        print("       ^^ DOLLAR SURVIVED")
    if has_mbox:
        print("       ^^ \\mbox SURVIVED")
    if notes:
        print(f"       notes: {notes}")
    print()

print("=" * 78)
print(f"RESULT: {len(CASES) - fail}/{len(CASES)} pass")
print("=" * 78)
sys.exit(1 if fail else 0)
