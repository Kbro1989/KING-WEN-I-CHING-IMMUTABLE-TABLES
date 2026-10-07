#!/usr/bin/env python3
"""
Regression test: parse_latex corruption detector must catch silent corruption.

parse_latex does not raise on several input classes — it returns a
mathematically DIFFERENT expression. A pipeline that reports these as
"parsed" is producing false passes. This test pins the detector against
known cases so a future edit cannot silently disable it.

Run:  python3 scripts/test_provenance_corruption.py
Exit: 0 if all assertions hold, 1 otherwise.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from solve_provenance import clean_for_sympy, detect_corruption  # noqa: E402

try:
    from sympy.parsing.latex import parse_latex
except ImportError:
    print("SKIP: sympy not available")
    sys.exit(0)


# (label, latex, expect_corruption)
CASES = [
    # --- must be flagged: silent corruption ---
    ("multi_char_subscript", r"L_{simple}(\theta)=E_t[x]", True),
    ("multi_char_subscript2", r"D_{KL}(q(x))", True),
    ("relation_approx", r"a \approx b", True),
    ("relation_sim", r"a \sim b", True),

    # --- must NOT be flagged: clean math ---
    ("single_char_sub", r"x_{t}=y_{t}", False),
    ("plain_equation", r"a = b + c", False),
    ("leq_relation", r"a \leq b", False),
    ("geq_relation", r"a \geq b", False),
    ("frac_clean", r"\frac{a}{b} = c", False),
    ("compound_sub", r"x_{t-1} = y", False),
]


def main() -> int:
    failures = []

    for label, latex, expect in CASES:
        cleaned = clean_for_sympy(latex)
        try:
            expr = parse_latex(cleaned)
        except Exception as e:
            # A raise is acceptable for cases we expect to be flagged
            # (we treat "raised" as detected), but not for clean cases.
            if expect:
                print(f"  ok   {label:24s} raised (counts as detected): {str(e)[:40]}")
                continue
            failures.append(f"{label}: unexpected parse failure: {str(e)[:60]}")
            print(f"  FAIL {label:24s} unexpected parse failure")
            continue

        findings = detect_corruption(cleaned, expr)
        detected = bool(findings)

        if detected == expect:
            mark = "ok  "
            detail = findings[0]["class"] if findings else "clean"
            print(f"  {mark} {label:24s} {detail}")
        else:
            failures.append(
                f"{label}: expected corruption={expect}, detected={detected} "
                f"({[f['class'] for f in findings]})"
            )
            print(f"  FAIL {label:24s} expected={expect} detected={detected}")

    print()
    if failures:
        print(f"FAILED ({len(failures)}/{len(CASES)}):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"PASSED: {len(CASES)}/{len(CASES)} corruption-detector assertions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
