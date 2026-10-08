#!/usr/bin/env python3
"""
CORRUPTION vs LOSS — the decisive classification.

"unknown:" is only a warning note. The real question is what the FINAL
FALLBACK does to the math:

    s = re.sub(r"\\[a-zA-Z]+\s*\{([^{}]*)\}", r"\1", s)   # keep arg
    s = re.sub(r"\\[a-zA-Z]+", "", s)                       # drop cmd

That silently DELETES the operation while keeping the operand. So
\\frac{u}{x} -> u(x)  (division gone) and \\sqrt{a} -> (a)  (root gone).
A parseable, confident, WRONG expression. Same class as the known
operator-superscript and nested-accent corruptions.

This measures: for each command, what operation is LOST, and is the
result still parseable (=> silent corruption) or obviously broken?
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
from math_recovery_tool import recover_latex  # noqa: E402

# command -> (operation that must be preserved, minimal probe, expected fragment)
PROBES = [
    (r"\frac",       "division",     r"\frac{a}{b}",           "/"),
    (r"\sqrt",       "root",         r"\sqrt{a}",              "sqrt"),
    (r"\bar",        "mean/overline",r"\bar{x}",               "bar"),
    (r"\hat",        "estimator",    r"\hat{x}",               "hat"),
    (r"\dot",        "time-deriv",   r"\dot{x}",               "dot"),
    (r"\ddot",       "2nd-deriv",    r"\ddot{x}",              "ddot"),
    (r"\tilde",      "perturbation", r"\tilde{x}",             "tilde"),
    (r"\widetilde",  "perturbation", r"\widetilde{x}",         "tilde"),
    (r"\widehat",    "estimator",    r"\widehat{x}",           "hat"),
    (r"\vec",        "vector",       r"\vec{x}",               "vec"),
    (r"\bm",         "bold-vector",  r"\bm{x}",                "x"),
    (r"\mathbf",     "bold",         r"\mathbf{x}",            "x"),
    (r"\underbrace", "grouping",     r"\underbrace{a}_{b}",    "a"),
    (r"\overbrace",  "grouping",     r"\overbrace{a}^{b}",     "a"),
    (r"\underset",   "limit-under",  r"\underset{x}{y}",       "y"),
    (r"\operatorname","named-op",    r"\operatorname{sgn}(x)", "sgn"),
]

# zero-arg commands: what do they leave behind?
ZERO_ARG = [
    (r"\rm",             "font switch",  r"N_{\rm H}"),
    (r"\bf",             "font switch",  r"{\bf x}"),
    (r"\it",             "font switch",  r"{\it x}"),
    (r"\ldots",          "ellipsis",     r"1\ldots D"),
    (r"\dots",           "ellipsis",     r"1\dots D"),
    (r"\cdots",          "ellipsis",     r"a\cdots b"),
    (r"\uparrow",        "tends-to",     r"x\uparrow 0"),
    (r"\downarrow",      "tends-to",     r"x\downarrow 0"),
    (r"\triangleright",  "operator",     r"a\triangleright b"),
    (r"\checkmark",      "marker",       r"a\checkmark"),
    (r"\textdegree",     "degree",       r"90\textdegree"),
    (r"\prime",          "derivative",   r"f^{\prime}"),
    (r"\perp",           "perpendicular",r"v_{\perp}"),
    (r"\dagger",         "conjugate",    r"A^{\dagger}"),
    (r"\emptyset",       "empty set",    r"\emptyset"),
    (r"\color",          "colour",       r"{\color[rgb]{0,0,0.7}x}"),
]

print("=" * 78)
print("SILENT CORRUPTION TEST — is the OPERATION preserved?")
print("=" * 78)
print()
print(f"{'cmd':16s} {'operation':14s} {'probe':22s} -> {'result':22s} verdict")
print("-" * 78)

corrupt, lost, ok = [], [], []
for cmd, op, probe, expect in PROBES:
    try:
        out, _ = recover_latex(probe)
    except Exception as e:
        print(f"{cmd:16s} {op:14s} {probe:22s} -> CRASH {type(e).__name__}")
        continue
    keep = expect in out
    # decide verdict
    if keep:
        v = "PRESERVED"
        ok.append(cmd)
    elif out.strip():
        v = "LOST-op (still parses)"
        corrupt.append((cmd, op, probe, out))
    else:
        v = "LOST-op (empty)"
        lost.append(cmd)
    print(f"{cmd:16s} {op:14s} {probe:22s} -> {out[:22]:22s} {v}")

print()
print("=" * 78)
print("ZERO-ARG COMMANDS — token fusion / dropped tokens")
print("=" * 78)
print()
print(f"{'cmd':16s} {'role':13s} {'probe':22s} -> result")
print("-" * 78)
fusion = []
for cmd, role, probe in ZERO_ARG:
    try:
        out, _ = recover_latex(probe)
    except Exception as e:
        print(f"{cmd:16s} {role:13s} {probe:22s} -> CRASH")
        continue
    flag = ""
    if out != probe:
        # detect fusion: a letter pair that should have a space
        if re.search(r"[A-Za-z]_[A-Za-z]{2,}", out) or "  " in out:
            flag = "  <- SPACING/FUSION"
        fusion.append((cmd, probe, out))
    print(f"{cmd:16s} {role:13s} {probe:22s} -> {out!r}{flag}")

print()
print("=" * 78)
print("VERDICT")
print("=" * 78)
print()
print(f"  PRESERVED          : {len(ok)}   {' '.join(ok)}")
print(f"  OPERATION LOST     : {len(corrupt)}")
for cmd, op, probe, out in corrupt:
    print(f"      {cmd:14s} ({op:14s})  {probe:20s} -> {out!r}")
print()
print(f"  ZERO-ARG, output changed : {len(fusion)}")
for cmd, probe, out in fusion:
    print(f"      {cmd:14s}  {probe:20s} -> {out!r}")
print()
print("  The OPERATION LOST set is the dangerous one: the result still")
print("  parses, so it is reported as a success while the mathematics has")
print("  been silently altered. These must either be translated correctly")
print("  or refused — never silently stripped.")
