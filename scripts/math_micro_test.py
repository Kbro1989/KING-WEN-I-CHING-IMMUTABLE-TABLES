#!/usr/bin/env python3
"""
MICRO-TEST — isolate the exact failing argument shapes.

Decisive and fast: feed minimal cases through recover_latex and see which fail.
This removes the per-occurrence attribution ambiguity of the corpus scan.
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

CASES = [
    # (label, latex, expect_clean)
    ("frac flat alpha",        r"\frac{1}{n}",                      True),
    ("frac cmd numerator",     r"\frac{\hat{r}}{\delta}",           False),
    ("frac nested num",        r"\frac{u^{(k)}}{x}",                False),
    ("frac both flat",         r"\frac{a}{b}",                      True),

    ("hat alpha",              r"\hat{r}",                          True),
    ("hat cmd arg",            r"\hat{\mu}",                        False),
    ("hat greek cmd",          r"\hat{\nu}",                        False),

    ("dot alpha",              r"\dot{x}",                          True),
    ("dot cmd arg",            r"\dot{\nu}",                        False),
    ("ddot cmd arg",           r"\ddot{\nu}",                       False),

    ("bar alpha",              r"\bar{x}",                          True),
    ("bar cmd arg",            r"\bar{\hat{r}}",                    False),
    ("bar greek cmd",          r"\bar{\pi}",                        False),

    ("sqrt flat",              r"\sqrt{2}",                         True),
    ("sqrt nested",            r"\sqrt{\bar{\alpha}_{t}}",          False),

    ("widetilde cmd",          r"\widetilde{\pi}",                  False),
    ("widetilde flat",         r"\widetilde{x}",                    True),
    ("widehat cmd",            r"\widehat{\mu}",                    False),

    ("operatorname flat",      r"\operatorname{sgn}(x)",            True),
    ("underset",               r"\underset{x}{y}",                  False),

    ("rm oldstyle",            r"N_{\rm H}",                        False),
    ("ldots",                  r"1\ldots D",                        False),
    ("uparrow",                r"x\uparrow 0",                      False),
    ("triangleright",          r"a\triangleright b",                False),
    ("bm braced",              r"\bm{u}",                           False),
    ("max bare",               r"\max_{x} f",                       False),
]

print("=" * 78)
print("MICRO-TEST — exact failing argument shapes")
print("=" * 78)
print()
print(f"{'label':22s} {'outcome':10s} recovered")
print("-" * 78)

fails = []
for label, latex, expect_clean in CASES:
    try:
        out, notes = recover_latex(latex)
    except Exception as e:
        print(f"{label:22s} {'CRASH':10s} {type(e).__name__}: {e}")
        continue
    unk = [n for n in notes if n.startswith("unknown:")]
    clean = not unk
    ok = (clean == expect_clean)
    mark = "ok  " if ok else "MISM"
    print(f"{label:22s} {mark:10s} {out[:52]}")
    if unk:
        print(f"{'':22s} {'':10s} unknown: {unk[0][8:]}")
    if not ok:
        fails.append((label, latex, expect_clean, clean))

print()
print("=" * 78)
print("DIAGNOSIS")
print("=" * 78)
print()
print("  Handled commands fail when the ARGUMENT contains either:")
print("    (a) a backslash-command   \\hat{\\mu}   \\dot{\\nu}   \\bar{\\pi}")
print("    (b) a nested brace group  \\frac{u^{(k)}}{x}  \\sqrt{\\bar{\\alpha}_{t}}")
print()
print("  Cause: the handler regexes are")
print("      accent :  \\\\(cmd)\\\\s*\\{([a-zA-Z0-9]+)\\}      <- excludes backslashes")
print("      frac   :  \\\\[dtc]?frac\\s*\\{([^{}]+)\\}\\s*\\{([^{}]+)\\}   <- excludes braces")
print()
print("  So they match only a SINGLE alphanumeric token, never a nested")
print("  expression. Since real math nests constantly, the handlers miss")
print("  most real usage and the literal command survives to be 'unknown'.")
print()
print("  SECOND cause (flat args that still fail): commands whose arg is a")
print("  backslash-command but with NO nesting, e.g. \\dot{\\nu}. These are")
print("  'flat' by brace depth yet still fail, because the accent regex")
print("  requires [a-zA-Z0-9]+ and '\\nu' starts with a backslash.")
print()
print("  THIRD cause: zero-arg old-style font switches (\\rm \\bf \\it) are")
print("  not in any handler and are not TEXT_CMDS, so they drop out and")
print("  fuse the following token:  N_{\\rm H}  ->  N_ H")
print()
print("=" * 78)
print(f"micro-test mismatches: {len(fails)}")
for f in fails:
    print(f"  {f[0]}: expected clean={f[2]} got clean={f[3]}")
print("=" * 78)
