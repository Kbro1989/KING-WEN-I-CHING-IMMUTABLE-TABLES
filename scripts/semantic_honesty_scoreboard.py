#!/usr/bin/env python3
"""
SEMANTIC HONESTY SCOREBOARD — measure preservation, not solver acceptance.

The single `solvable` number conflates three different things:
    1. structural recovery   (is the structure preserved?)
    2. backend compatibility (will SymPy accept it?)
    3. semantic honesty      (does the recovered form MEAN the same thing?)

(2) is not a quality metric. A parser can raise it by manufacturing '='.
This script measures (1) and (3) using the IMMUTABLE SOURCE as the witness.

Classes (from the corpus work):
    EXACT              reconstructed == source structure
    STRUCTURAL_EQUIV   different surface, same structure
    LOSSY              something disappeared
    CORRUPTED          something changed meaning
    FALSE_RECOVERY     solver accepted while the mathematics is wrong
    UNRECOVERED        no recovery produced
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

GENS = [
    ("v6 regex",  "math_recovery_v6"),
    ("v12 tree",  "math_recovery_v12"),
    ("v13 tree",  "math_recovery_v13"),
]

# ── relation tokens that must NEVER become '=' ──────────────────────────
NON_EQ_RELATIONS = {
    "~=": r"\\sim(?![a-zA-Z])|\\approx(?![a-zA-Z])|\\simeq|\\cong|∼|≈|≃|≅",
    "->": r"\\to(?![a-zA-Z])|\\rightarrow|→|⟶",
    # \\in must NOT match the \\in prefix of \\infty — that produced 18 bogus
    # FALSE_RECOVERY hits on plain 'p=\\infty'. Require a non-letter after.
    "in": r"\\in(?![a-zA-Z])|∈",
    "propto": r"\\propto|∝",
    "le": r"\\leq|≤",
    "ge": r"\\geq|≥",
    "neq": r"\\neq|≠",
}

# ── structural features whose presence must survive ─────────────────────
STRUCT_FEATURES = {
    "integral":  r"\\int|∫",
    "sum":       r"\\sum|∑",
    "prod":      r"\\prod|∏",
    "frac":      r"\\frac|/",
    "sqrt":      r"\\sqrt|√",
    "norm":      r"\\\||\\lVert|\\rVert|‖|∥",
    "set":       r"\\\{|\\\}",
    "conditional": r"\\mid|∣",
    "differential": r"\\,d|d[a-zA-Z]|𝑑",
    "log":       r"\\log|\blog\b",
    "exp":       r"\\exp|\bexp\b",
    "max":       r"\\max|\bMax\b",
    "min":       r"\\min|\bMin\b",
    "expect":    r"\\mathbb\{E\}|\\E\b|\bE\[",
    "matrix":    r"\\begin\{[pbvBV]?matrix\}|\\begin\{cases\}",
}


def has(pat, s):
    return bool(re.search(pat, s))


def classify(src_latex: str, recovered: str, error: str, solvable: bool):
    """Return one honesty class for this equation."""
    if not recovered:
        return "UNRECOVERED"

    # --- FALSE RECOVERY: solver accepted, but a relation was turned into '=' ---
    if solvable:
        for name, pat in NON_EQ_RELATIONS.items():
            if has(pat, src_latex):
                # source has this relation; did the recovered form lose it?
                if name == "~=" and "~=" not in recovered and "≈" not in recovered:
                    return "FALSE_RECOVERY"
                if name == "->" and "->" not in recovered:
                    return "FALSE_RECOVERY"
                if name == "in":
                    # 'in' may be fused into a limit token (Sum_iinP) — accept
                    # any occurrence, not just the space-delimited form.
                    if "in" not in recovered and "∈" not in recovered:
                        return "FALSE_RECOVERY"
                if name == "propto" and "propto" not in recovered:
                    return "FALSE_RECOVERY"
                if name == "neq" and "!=" not in recovered:
                    return "FALSE_RECOVERY"

    # --- structural feature loss ---
    lost = []
    for fname, pat in STRUCT_FEATURES.items():
        if has(pat, src_latex) and not has(pat, recovered):
            # allow transliteration
            if fname == "integral" and "Integral" in recovered:
                continue
            if fname == "sum" and "Sum" in recovered:
                continue
            if fname == "prod" and "Prod" in recovered:
                continue
            if fname == "max" and "Max" in recovered:
                continue
            if fname == "min" and "Min" in recovered:
                continue
            if fname == "differential":
                # d must appear somewhere as a token
                if re.search(r"\bd\b|d[a-zA-Z]|𝑑", recovered):
                    continue
            if fname == "set" and ("{" in recovered or "}" in recovered):
                continue
            lost.append(fname)

    if lost:
        return "LOSSY"

    # --- relation preserved but not an equation: that is honest ---
    if error and str(error).startswith("not_an_equation"):
        return "STRUCTURAL_EQUIV"

    return "EXACT" if recovered.strip() else "UNRECOVERED"


print("=" * 92)
print("SEMANTIC HONESTY SCOREBOARD")
print("=" * 92)
print()

results = {}
for label, sub in GENS:
    d = ROOT / "DATASETS" / sub
    if not d.exists():
        continue
    counts = Counter()
    n = 0
    for f in sorted(d.glob("*_recovery.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for r in j.get("results", []):
            n += 1
            c = classify(
                str(r.get("latex") or ""),
                str(r.get("recovered") or ""),
                str(r.get("error") or ""),
                bool(r.get("solvable")),
            )
            counts[c] += 1
    results[label] = (n, counts)

ORDER = ["EXACT", "STRUCTURAL_EQUIV", "LOSSY", "CORRUPTED",
         "FALSE_RECOVERY", "UNRECOVERED"]

print(f"{'class':20s}" + "".join(f"{l:>16s}" for l, _ in results.items()))
print("-" * 92)
for c in ORDER:
    row = f"{c:20s}"
    for label, (n, counts) in results.items():
        v = counts.get(c, 0)
        row += f"{v:>10d} ({100*v/max(n,1):>4.1f}%)"
    print(row)
print("-" * 92)
tot_row = f"{'TOTAL':20s}"
for label, (n, counts) in results.items():
    tot_row += f"{n:>16d}"
print(tot_row)

print()
print("=" * 92)
print("HEADLINE")
print("=" * 92)
print()
for label, (n, counts) in results.items():
    false_rec = counts.get("FALSE_RECOVERY", 0)
    honest = counts.get("EXACT", 0) + counts.get("STRUCTURAL_EQUIV", 0)
    print(f"  {label}:")
    print(f"    structurally faithful : {honest:>5}  ({100*honest/max(n,1):.1f}%)")
    print(f"    lossy but recognisable: {counts.get('LOSSY',0):>5}")
    print(f"    FALSE RECOVERY        : {false_rec:>5}   <- must be 0")
    print()
