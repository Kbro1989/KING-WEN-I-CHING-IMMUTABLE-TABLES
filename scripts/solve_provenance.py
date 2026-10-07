#!/usr/bin/env python3
"""
solve_provenance.py — Ladder parity + SymPy solving on arxiv provenance records.

Ladder: TeX -> HTML/MathML -> PDF -> parser -> recovered AST

This script:
  1. Measures structural parity between the TeX and HTML rungs
  2. Converts resolved LaTeX to SymPy and attempts to solve
  3. Reports which equations are genuinely solvable vs merely parsed

Usage:
    python3 scripts/solve_provenance.py DATASETS/provenance_2006.11239.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from sympy.parsing.latex import parse_latex
    from sympy import Symbol, Eq, solve, sympify, latex as sympy_latex
    from sympy.parsing.latex.errors import LaTeXParsingError
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


# ---------------------------------------------------------------------------
# Structural feature extraction (parity measurement)
# ---------------------------------------------------------------------------

FEATURES = {
    "fraction": r"\\frac",
    "sqrt": r"\\sqrt",
    "integral": r"\\int",
    "sum": r"\\sum",
    "prod": r"\\prod",
    "expectation": r"\\mathbb\{E\}",
    "log": r"\\log",
    "underbrace": r"\\underbrace",
    "overline": r"\\overline|\\bar\{",
    "sub_sup": r"[_^]\{",
    "relation": r"=|\\coloneqq|\\leq|\\geq|\\approx|\\sim",
    "vector": r"\\mathbf|\\boldsymbol",
    "mathcal": r"\\mathcal",
    "abs": r"\\left\||\\right\||\|",
    "kl": r"D_\{\\mathrm\{KL\}\}|\\mathrm\{KL\}",
    "hat": r"\\hat",
    "tilde": r"\\tilde",
    "text": r"\\text|\\mathrm",
    "prod_limits": r"\\prod_\{|\\sum_\{|\\int_\{",
    "nabla": r"\\nabla",
    "partial": r"\\partial",
}


def features(latex: str) -> dict:
    """Return which structural features are present in a LaTeX string."""
    return {name: bool(re.search(pat, latex)) for name, pat in FEATURES.items()}


def normalize_latex(s: str) -> str:
    """Normalize for cross-rung comparison (strip presentation-only markup)."""
    s = s.replace("\\displaystyle", "")
    s = s.replace("&amp;", "&")
    s = s.replace("\\!", "").replace("\\,", "").replace("\\;", "")
    s = s.replace("\\\\", " ")
    s = s.replace("&", "")
    # brace style: \mathbf{x}_T vs \mathbf{x}_{T}
    s = re.sub(r"_([A-Za-z0-9])(?![A-Za-z0-9{])", r"_{\1}", s)
    s = re.sub(r"\^([A-Za-z0-9])(?![A-Za-z0-9{])", r"^{\1}", s)
    s = " ".join(s.split())
    return s


def measure_parity(tex_eqs: list, html_eqs: list) -> dict:
    """Compare structural features between the two ground-truth rungs."""
    n = min(len(tex_eqs), len(html_eqs))
    per_eq = []
    feature_totals = {k: {"tex": 0, "html": 0, "agree": 0} for k in FEATURES}

    for i in range(n):
        t = normalize_latex(tex_eqs[i].get("latex", ""))
        h = normalize_latex(html_eqs[i].get("latex", ""))
        tf = features(t)
        hf = features(h)

        agree = sum(1 for k in FEATURES if tf[k] == hf[k])
        disagreements = [k for k in FEATURES if tf[k] != hf[k]]

        for k in FEATURES:
            if tf[k]:
                feature_totals[k]["tex"] += 1
            if hf[k]:
                feature_totals[k]["html"] += 1
            if tf[k] == hf[k]:
                feature_totals[k]["agree"] += 1

        per_eq.append({
            "index": i + 1,
            "tex_features": sum(tf.values()),
            "html_features": sum(hf.values()),
            "agree": agree,
            "total_features": len(FEATURES),
            "disagreements": disagreements,
            "tex_latex": t[:120],
            "html_latex": h[:120],
        })

    return {"compared": n, "per_equation": per_eq, "feature_totals": feature_totals}


# ---------------------------------------------------------------------------
# SymPy solving
# ---------------------------------------------------------------------------

def clean_for_sympy(latex: str) -> str:
    """
    Strip presentation markup SymPy cannot parse, keep math structure.

    Only mechanical normalizations here — no semantic rewriting. If an
    equation still fails after this, it is a genuine parse_latex limitation
    and must be reported as such, not hidden.

    ORDER MATTERS:
      1. Remove presentation wrappers (displaystyle, &, sizes)
      2. Normalize relation/operator commands with surrounding spaces
      3. Rewrite accents to suffixed names
      4. Strip braces ONLY around simple identifiers (never around
         compound subscripts like t-1 — that would silently destroy math)
    """
    s = latex
    s = s.replace("\\displaystyle", "")
    s = s.replace("&", "")
    s = s.replace("\\\\", " ")
    # \text{...} / \mathrm{...} -> plain (spaced so tokens don't fuse)
    s = re.sub(r"\\text\{([^}]*)\}", r" \1 ", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r" \1 ", s)
    # \coloneqq / \defeq -> =
    s = s.replace("\\coloneqq", "=")
    # letter-form commands -> plain letters
    s = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\boldsymbol\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathcal\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathbb\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\hat\s*\\mathbf\{([^}]*)\}", r" \1_hat ", s)
    # spacing commands
    s = s.replace("\\!", "").replace("\\,", " ").replace("\\;", " ")
    s = s.replace("\\quad", " ").replace("\\qquad", " ")
    # sizing wrappers
    s = s.replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\[Bb]igg?[lrm]?", "", s)
    s = re.sub(r"\\[Bb]ig\s*", "", s)
    # norm \| -> ||  (parse_latex cannot read \|)
    s = s.replace("\\|", "||")
    # environments
    s = re.sub(r"\\begin\{[^}]*\}", " ", s)
    s = re.sub(r"\\end\{[^}]*\}", " ", s)
    s = s.replace("\\underbrace", "")
    s = s.replace("\\label", "\\label")  # no-op; labels stripped below
    s = re.sub(r"\\label\{[^}]*\}", "", s)

    # --- Relation/operator commands: spaced BEFORE subscript handling ---
    # so \sum_{t\geq 1} keeps its \geq intact
    for cmd in ["\\leq", "\\geq", "\\approx", "\\sim", "\\propto", "\\equiv", "\\neq"]:
        s = s.replace(cmd, " " + cmd + " ")

    # --- Accents: rewrite to a single fused identifier BEFORE brace stripping.
    #
    # \bar{\alpha} MUST NOT become \alpha_bar: parse_latex reads the
    # multi-char name \alpha_bar as the product alpha * b * a * r, silently
    # corrupting the mathematics. Verified:
    #     \alpha_bar_t  ->  alpha_{b}*(a*r_{t})     WRONG
    #     \alphabar_t   ->  alphabar_{t}            correct, one symbol
    # So the accent marker is fused into the name with no separator.
    def _accent(m, suffix):
        inner = m.group(1)
        # inner may itself carry a subscript: \bar{\alpha_t}
        if "_" in inner:
            base, sub = inner.split("_", 1)
            return f" {base}{suffix}_{sub} "
        return f" {inner}{suffix} "

    s = re.sub(r"\\bar\{([^}]*)\}", lambda m: _accent(m, "bar"), s)
    s = re.sub(r"\\tilde\{([^}]*)\}", lambda m: _accent(m, "tilde"), s)
    s = re.sub(r"\\hat\{([^}]*)\}", lambda m: _accent(m, "hat"), s)
    # bare accent forms: \bar\alpha, \hat\mathbf{x}
    s = re.sub(r"\\bar\s*([A-Za-z])", r" \1bar ", s)
    s = re.sub(r"\\tilde\s*([A-Za-z])", r" \1tilde ", s)
    s = re.sub(r"\\hat\s*([A-Za-z])", r" \1hat ", s)
    s = re.sub(r"\\hat\s+", " ", s)

    # --- Subscripts: strip braces ONLY for simple alphanumeric identifiers.
    # x_{t-1} and x_{0:T} MUST keep their braces — flattening them destroys
    # the minus/colon and silently changes the mathematics.
    s = re.sub(r"_\{([A-Za-z0-9]+)\}", r"_\1", s)
    s = re.sub(r"\^\{([A-Za-z0-9]+)\}", r"^\1", s)

    # Fix accidental space between a name and its subscript (x_hat _0)
    s = re.sub(r"\b([A-Za-z][A-Za-z0-9_]*)\s+_([A-Za-z0-9])", r"\1_\2", s)

    # Trim whitespace immediately inside braces. Substituting \mathrm{KL} with
    # " KL " otherwise yields D_{ KL }, which parse_latex reads as three
    # separate tokens instead of the single symbol D_{KL}.
    s = re.sub(r"\{\s+", "{", s)
    s = re.sub(r"\s+\}", "}", s)

    # LaTeX ~ is a non-breaking space; parse_latex rejects it.
    s = s.replace("~", " ")

    s = " ".join(s.split())
    return s


def detect_corruption(cleaned: str, expr) -> list:
    """
    Detect silent corruption by parse_latex.

    parse_latex does not raise on several classes of input — it produces a
    mathematically DIFFERENT expression. Verified against sympy 1.14:

        L_{simple}    -> L_{s*(i*(m*(p*(e*l))))}     (name exploded into product)
        D_{KL}        -> D_{K*L}                     (name exploded into product)
        a \\approx b   -> a*(approx*b)                (relation became a product)
        a \\sim b     -> a*(b*sim)

    An equation that "parses" while carrying these defects is a false pass.
    Returns a list of corruption findings (empty == clean).
    """
    findings = []

    try:
        free = expr.free_symbols if hasattr(expr, "free_symbols") else set()
        sym_names = {s.name for s in free}
    except Exception:
        return findings

    # --- Class 0: operator characters inside a symbol NAME ---
    # The strongest corruption signal. parse_latex builds a symbol whose name
    # contains a product/quotient operator because it exploded a multi-char
    # identifier. Example: D_{KL} -> symbol literally named "D_{K*L}".
    # A legitimate symbol name never contains * or / inside its subscript.
    for name in sym_names:
        if "*" in name or "/" in name:
            findings.append({
                "class": "operator_in_symbol_name",
                "token": name,
                "leaked_symbols": [],
            })

    # --- Class 1: multi-char identifier exploded into single letters ---
    # clean_for_sympy strips braces from simple identifiers, so the cleaned
    # text shows `L_simple` (unbraced). parse_latex then reads that as
    # L_{s} * i * m * p * l * e. Signature: the parsed symbol is the base
    # letter with ONLY the first letter of the word as subscript.
    for m in re.finditer(r"\b([A-Za-z])_([A-Za-z]{2,})(?![A-Za-z0-9_])", cleaned):
        base, word = m.group(1), m.group(2)
        first = word[0]
        # Healthy: one symbol contains base + full word
        intact = any(base in n and word in n for n in sym_names)
        if intact:
            continue
        # Corrupt signature: symbol is exactly "<base>_{<first>}"
        truncated = f"{base}_{{{first}}}"
        letters = set(word)
        leaked = letters & sym_names
        if truncated in sym_names or len(leaked) >= 2:
            findings.append({
                "class": "multi_char_subscript_exploded",
                "token": f"{base}_{word}",
                "parsed_as": truncated if truncated in sym_names else "letters",
                "leaked_symbols": sorted(leaked),
            })

    # --- Class 2: relation command became a symbol ---
    for cmd in ["approx", "sim", "propto", "equiv"]:
        if re.search(r"\\" + cmd + r"\b", cleaned) and cmd in sym_names:
            findings.append({
                "class": "relation_became_symbol",
                "token": "\\" + cmd,
                "leaked_symbols": [cmd],
            })

    # --- Class 3: multi-char plain identifier split (\alphabar_t) ---
    for m in re.finditer(r"\\([a-z]{2,})(?:_\{?([A-Za-z0-9]+)\}?)?", cleaned):
        name = m.group(1)
        if name in {"frac", "sqrt", "left", "right", "log", "sum", "prod",
                    "int", "cdot", "times", "begin", "end", "text", "mathrm",
                    "mathbf", "boldsymbol", "mathcal", "mathbb", "underbrace",
                    "label", "quad", "qquad", "coloneqq", "theta", "epsilon",
                    "sigma", "alpha", "beta", "mu", "lambda", "gamma", "delta",
                    "nabla", "partial", "infty", "prime", "hat", "bar", "tilde"}:
            continue
        # Expect a symbol whose name contains this identifier
        intact = any(name in n for n in sym_names)
        if intact:
            continue
        letters = set(name)
        leaked = letters & sym_names
        if len(leaked) >= max(2, len(letters) - 1):
            findings.append({
                "class": "multi_char_identifier_split",
                "token": "\\" + name,
                "leaked_symbols": sorted(leaked),
            })

    return findings


def attempt_solve(latex: str) -> dict:
    """Attempt to parse and solve a LaTeX equation with SymPy."""
    if not SYMPY_AVAILABLE:
        return {"status": "sympy_unavailable"}

    cleaned = clean_for_sympy(latex)

    # Must have a relation to be an equation (not just '=')
    relation_re = r"(=|\\leq|\\geq|\\approx|\\sim|\\coloneqq|\\equiv|\\propto)"
    if not re.search(relation_re, cleaned):
        return {"status": "not_an_equation", "cleaned": cleaned[:150]}

    try:
        expr = parse_latex(cleaned)
    except LaTeXParsingError as e:
        return {"status": "latex_parse_error", "error": str(e)[:200], "cleaned": cleaned[:150]}
    except Exception as e:
        return {"status": "parse_exception", "error": f"{type(e).__name__}: {e}"[:200], "cleaned": cleaned[:150]}

    try:
        # parse_latex returns Eq or Relational or Expr
        if hasattr(expr, "lhs") and hasattr(expr, "rhs"):
            lhs, rhs = expr.lhs, expr.rhs
            eq = Eq(lhs, rhs)
        else:
            eq = expr

        free = sorted(eq.free_symbols, key=lambda s: s.name) if hasattr(eq, "free_symbols") else []

        # CRITICAL: parse_latex does not raise on some inputs — it silently
        # produces different mathematics. Check before reporting success.
        corruption = detect_corruption(cleaned, eq)
        if corruption:
            return {
                "status": "corrupted_parse",
                "corruption": corruption,
                "cleaned": cleaned[:200],
                "sympy_repr": str(eq)[:200],
                "free_symbols": [s.name for s in free],
            }

        return {
            "status": "parsed",
            "free_symbols": [s.name for s in free],
            "sympy_repr": str(eq)[:200],
            "is_equation": hasattr(eq, "lhs"),
        }
    except Exception as e:
        return {"status": "symbol_error", "error": f"{type(e).__name__}: {e}"[:200]}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Ladder parity + SymPy solving")
    ap.add_argument("provenance_json", help="Path to provenance JSON")
    ap.add_argument("--output", "-o", help="Write report JSON")
    args = ap.parse_args()

    with open(args.provenance_json, encoding="utf-8") as f:
        d = json.load(f)

    print(f"Paper: {d['paper_key']}")
    print(f"SymPy available: {SYMPY_AVAILABLE}")
    print()

    html_eqs = [e for e in d["equations"] if e.get("is_display")]
    tex_block = d.get("tex_source", {})
    tex_eqs = tex_block.get("equations", []) if tex_block.get("available") else []

    # ---- Parity ----
    print("=" * 60)
    print("LADDER PARITY: TeX vs HTML")
    print("=" * 60)
    if tex_eqs and html_eqs:
        parity = measure_parity(tex_eqs, html_eqs)
        print(f"Equations compared: {parity['compared']}")
        total_agree = sum(e["agree"] for e in parity["per_equation"])
        total_feat = sum(e["total_features"] for e in parity["per_equation"])
        print(f"Feature agreement: {total_agree}/{total_feat} "
              f"({100*total_agree/total_feat:.1f}%)")
        print()
        print("Feature coverage (tex | html | agree):")
        for k, v in parity["feature_totals"].items():
            if v["tex"] or v["html"]:
                print(f"  {k:14s} {v['tex']:3d} | {v['html']:3d} | {v['agree']:3d}")
        print()
        print("Per-equation disagreements:")
        for e in parity["per_equation"]:
            if e["disagreements"]:
                print(f"  eq{e['index']:2d}: {', '.join(e['disagreements'])}")
    else:
        parity = None
        print("TeX rung unavailable — cannot compare")
    print()

    # ---- Solving ----
    print("=" * 60)
    print("SYMPY SOLVING: HTML rung display equations")
    print("=" * 60)
    solve_results = []
    status_counts = {}
    for i, eq in enumerate(html_eqs, 1):
        res = attempt_solve(eq["latex"])
        res["index"] = i
        res["latex"] = eq["latex"][:150]
        solve_results.append(res)
        status_counts[res["status"]] = status_counts.get(res["status"], 0) + 1
        marker = "OK " if res["status"] == "parsed" else "   "
        print(f"  {marker}eq{i:2d} [{res['status']}] {eq['latex'][:70]}")

    print()
    print("Status breakdown:")
    for k, v in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # Also try TeX rung
    if tex_eqs:
        print()
        print("=" * 60)
        print("SYMPY SOLVING: TeX rung display equations")
        print("=" * 60)
        tex_solve = []
        tex_status = {}
        for i, eq in enumerate(tex_eqs, 1):
            res = attempt_solve(eq.get("latex", ""))
            res["index"] = i
            tex_solve.append(res)
            tex_status[res["status"]] = tex_status.get(res["status"], 0) + 1
            marker = "OK " if res["status"] == "parsed" else "   "
            print(f"  {marker}eq{i:2d} [{res['status']}] {eq.get('latex','')[:70]}")
        print()
        print("Status breakdown (TeX rung):")
        for k, v in sorted(tex_status.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")
    else:
        tex_solve = None

    report = {
        "paper_key": d["paper_key"],
        "sympy_available": SYMPY_AVAILABLE,
        "html_display_count": len(html_eqs),
        "tex_display_count": len(tex_eqs),
        "parity": parity,
        "html_solve": solve_results,
        "tex_solve": tex_solve,
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nReport written to: {args.output}")


if __name__ == "__main__":
    main()
