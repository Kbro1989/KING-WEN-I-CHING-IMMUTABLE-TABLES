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
    ("v14 relid", "math_recovery_v14"),
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

    # --- FALSE RECOVERY: solver accepted, but the TOP-LEVEL relation was
    # turned into '='.
    #
    # The relation must be at the TOP LEVEL. A relation inside a subscript or
    # argument does not make the equation a relation:
    #   \Delta \coloneqq s(x) - E_{R \sim P_0}[R(x)]
    # Here the top-level relation is \coloneqq (a true equality/definition) and
    # \sim sits inside a subscript. Flagging this was a false positive.
    # Strip subscript/superscript groups before testing.
    def _top_level(s):
        """
        Remove subscript/superscript GROUPS so only the top-level relation
        remains testable.

        Must handle NESTED braces: `\mathbb{E}_{R\sim P_{0}}[R(x)]` contains a
        subscript whose body has its own group. A flat `[^{}]*` regex leaves the
        inner `\sim` behind and reports a false positive.

        Uses a balancing-brace scan (same discipline as the parser).
        """
        out = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch in "_^" and i + 1 < len(s):
                j = i + 1
                while j < len(s) and s[j].isspace():
                    j += 1
                if j < len(s) and s[j] == "{":
                    # balancing scan
                    depth = 0
                    k = j
                    while k < len(s):
                        if s[k] == "{":
                            depth += 1
                        elif s[k] == "}":
                            depth -= 1
                            if depth == 0:
                                break
                        k += 1
                    i = k + 1
                    continue
                if j < len(s) and (s[j].isalnum() or s[j] == "\\"):
                    # bare sub/superscript token (possibly a command)
                    k = j
                    if s[k] == "\\":
                        k += 1
                        while k < len(s) and s[k].isalpha():
                            k += 1
                    else:
                        while k < len(s) and s[k].isalnum():
                            k += 1
                    i = k
                    continue
            out.append(ch)
            i += 1
        return "".join(out)

    src_top = _top_level(src_latex)

    if solvable:
        for name, pat in NON_EQ_RELATIONS.items():
            if has(pat, src_top):
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
print("OCCURRENCE CONSERVATION")
print("=" * 92)
print()
# The scoreboard itself must conserve occurrences. A classification that drops
# equations is the same class of defect it is meant to detect.
conservation_ok = True
for label, (n, counts) in results.items():
    classified = sum(counts.get(c, 0) for c in ORDER)
    if classified != n:
        conservation_ok = False
        print(f"  FAIL {label}: classified={classified} != occurrences={n} "
              f"(drift {classified - n:+d})")
    else:
        print(f"  ok   {label}: {classified}/{n} classified")
assert conservation_ok, "classification conservation failure"
print()

print("=" * 92)
print("HEADLINE")
print("=" * 92)
print()
for label, (n, counts) in results.items():
    false_rec = counts.get("FALSE_RECOVERY", 0)
    # computed FROM the buckets so it can never disagree with them
    honest = sum(counts.get(c, 0) for c in ("EXACT", "STRUCTURAL_EQUIV"))
    print(f"  {label}:")
    print(f"    structurally faithful : {honest:>5}  ({100*honest/max(n,1):.1f}%)")
    print(f"    lossy but recognisable: {counts.get('LOSSY',0):>5}")
    print(f"    FALSE RECOVERY        : {false_rec:>5}   <- must be 0")
    print()
