#!/usr/bin/env python3
"""Regression: NESTED arguments must now translate (balancing-brace scanner)."""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CASES = [
    # (label, latex, must_not_contain)
    ("frac nested sup",    r"\frac{u^{(k)}}{x}",                        r"\frac"),
    ("frac cmd numerator", r"\frac{\hat{r}}{\delta}",                   r"\frac"),
    ("frac deep nest",     r"\frac{\operatorname{sgn}((e_{k}-\pi)_{j})}{n}", r"\frac"),
    ("frac triple nest",   r"\frac{\bar{\hat{r}}}{1-\bar{\alpha}_{t}}",  r"\frac"),
    ("sqrt nested",        r"\sqrt{\bar{\alpha}_{t}}",                  r"\sqrt"),
    ("sqrt deep",          r"\sqrt{(x_{t}-\mu)^{2}}",                   r"\sqrt"),
    ("sqrt indexed",       r"\sqrt[3]{x}",                              r"\sqrt"),
    ("norm pipes",         r"\left\|s(x)\right\|_{p}",                  "\\"),
    ("lVert",              r"\lVert x \rVert",                          "\\"),
    ("max subscript",      r"\max_{x} f(x)",                            r"\max"),
    ("min subscript",      r"\min_{\pi} g",                             r"\min"),
    ("underset",           r"\underset{x}{y}",                          r"\underset"),
    ("mathop argmax",      r"\mathop{\mathrm{arg\,max}}_{i}",           r"\mathop"),
    ("binomial nest",      r"\binom{n}{k}",                             r"\binom"),
    ("frac in frac",       r"\frac{\frac{a}{b}}{c}",                    r"\frac"),
    # --- escaped literals and text commands (2026-10-07) ---
    ("escaped underscore", r"\mathcal{L}_{text\_aux}",                  "\\"),
    ("escaped amp",        r"a \& b",                                   "\\"),
    ("bm braced",          r"\bm{u}^{k+1}",                             r"\bm"),
    ("textup",             r"\textup{diag}",                            r"\textup"),
    ("textnormal",         r"\textnormal{abc}",                         r"\textnormal"),
    ("operatorname star",  r"\operatorname*{ess\,sup}",                 r"\operatorname"),
]

print("=" * 78)
print("NESTED-ARGUMENT REGRESSION")
print("=" * 78)
print()
fails = 0
for label, latex, bad in CASES:
    try:
        out, notes = recover_latex(latex)
    except Exception as e:
        print(f"  CRASH {label:20s} {type(e).__name__}: {e}")
        fails += 1
        continue
    ok = bad not in out
    unk = [n for n in notes if n.startswith("unknown:")]
    if unk:
        ok = False
    mark = "ok  " if ok else "FAIL"
    if not ok:
        fails += 1
    print(f"  {mark} {label:20s} {latex[:34]:34s} -> {out[:34]}")
    if unk:
        print(f"       unknown: {unk[0][8:]}")
print()
print("=" * 78)
print(f"RESULT: {len(CASES)-fails}/{len(CASES)} pass")
print("=" * 78)
sys.exit(1 if fails else 0)
