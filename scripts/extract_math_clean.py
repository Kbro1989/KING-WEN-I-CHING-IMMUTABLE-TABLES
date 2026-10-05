#!/usr/bin/env python3
"""
extract_math_clean.py — Extract clean mathematical expressions from PDFs using PyMuPDF.

pdftotext strips Greek letters and math symbols. PyMuPDF preserves them.
This script extracts both Unicode math (φ, √, ∫, ≡, ≤) and LaTeX ($...$, \\frac).

Usage:
    python extract_math_clean.py --pdf papers/2605.30912v2v1.pdf --out output/math.json
    python extract_math_clean.py --pdf-dir papers/ --out output/math_batch.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import pymupdf
except ImportError:
    print("ERROR: PyMuPDF required. Install: pip install pymupdf", file=sys.stderr)
    sys.exit(2)


# ── Unicode math symbols ────────────────────────────────────────────────────
UNICODE_MATH_CHARS = set(
    "φψχωΩΨΧπΠΣ∆∂∇αβγδεζηθικλμνξρστυϕ"
    "≡≠≤≥≈∝∞∈∉⊂⊃⊆⊇∪∩∀∃∅ℝℕℤℚℂ"
    "√∫∮∑∏∐⋀⋁⋂⋃"
    "−×÷±∓"
    "ˆ¯˙¨"
    "₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹"
    "ⁱⁿ⁺⁻⁼⁽⁾"
)

# Patterns for Unicode math expressions
# Each pattern must contain at least one math symbol to avoid matching prose/URLs
UNICODE_MATH_PATTERNS = [
    # Equation with = or ≡ or ≤ or ≥ (starting with Greek letter, must have math symbol)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,80}[=≡≤≥][^\n]{0,80}"),
    # Square root (must have content after √)
    re.compile(r"√[^\n]{1,40}"),
    # Integral (must have content after ∫)
    re.compile(r"∫[^\n]{1,40}"),
    # Proportional (must have math context)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,30}∝[^\n]{0,30}"),
    # Not equal (must have math context)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,30}≠[^\n]{0,30}"),
    # Less/greater equal (must have math context)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,30}[≤≥][^\n]{0,30}"),
    # Superscript/subscript patterns (Greek letter + subscript/superscript)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹ⁱⁿ⁺⁻]+"),
    # Hat/circumflex notation (Greek letter + hat + content)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ]ˆ[^\n]{1,40}"),
    # Fraction-like with slash (must have math symbols on both sides)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,10}/[^\n]{0,10}[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ]"),
    # Greek letter followed by parenthesized expression (function call)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ]\([^\n]{1,40}\)"),
    # exp, log, sin, cos, tan, arctan with parenthesized argument
    re.compile(r"(?:exp|log|ln|sin|cos|tan|arctan)\s*\([^\n]{1,40}\)"),
    # Partial derivative notation (d<var>/d<var>)
    re.compile(r"d[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ]/d[^\n]{1,20}"),
    # Math symbol followed by number (e.g., σ², α₁)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹]+"),
    # Number with math symbol (e.g., 2π, 3σ)
    re.compile(r"\d+[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ]"),
    # Greek letter with subscript number (e.g., x₁, y₂)
    re.compile(r"[a-z]_[₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹]"),
    # Math operator between variables (e.g., x + y, α − β)
    re.compile(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕa-z]\s*[+−×÷]\s*[φψχωπΣ∆αβγδεζηθικλμνξρστυϕa-z]"),
    # Inequality with variables (e.g., x ≤ y, α ≥ β)
    re.compile(r"[a-z]\s*[≤≥]\s*[a-z]"),
    # Function composition (e.g., f(g(x)))
    re.compile(r"[a-z]\([a-z]\([a-z]\)\)"),
    # Power/exponent (e.g., x^2, e^x)
    re.compile(r"[a-z]\^[₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹{a-z}]"),
    # Absolute value (e.g., |x|, |v|)
    re.compile(r"\|[a-z][^\n]{0,20}\|"),
    # Norm (e.g., ||v||, ||x||)
    re.compile(r"\|[a-z][^\n]{0,20}\|"),
    # Subscript with brace (e.g., x_{i}, y_{n})
    re.compile(r"[a-z]_\{[a-z]+\}"),
    # Superscript with brace (e.g., x^{2}, e^{x})
    re.compile(r"[a-z]\^\{[a-z0-9]+\}"),
]

# LaTeX patterns
LATEX_PATTERNS = {
    "inline": re.compile(r"\$[^$\n]+\$"),
    "display": re.compile(r"\$\$[^$]+\$\$", re.DOTALL),
    "frac": re.compile(r"\\frac\{[^}]+\}\{[^}]+\}"),
    "sum": re.compile(r"\\sum[_\^]*\{?[^}]*\}?"),
    "int": re.compile(r"\\int[_\^]*\{?[^}]*\}?"),
    "sqrt": re.compile(r"\\sqrt\{[^}]+\}"),
    "alpha": re.compile(r"\\alpha"),
    "beta": re.compile(r"\\beta"),
    "sigma": re.compile(r"\\sigma"),
    "lambda": re.compile(r"\\lambda"),
    "omega": re.compile(r"\\omega"),
    "pi": re.compile(r"\\pi"),
    "theta": re.compile(r"\\theta"),
    "phi": re.compile(r"\\phi"),
    "psi": re.compile(r"\\psi"),
    "epsilon": re.compile(r"\\epsilon"),
    "mu": re.compile(r"\\mu"),
    "nu": re.compile(r"\\nu"),
    "rho": re.compile(r"\\rho"),
    "tau": re.compile(r"\\tau"),
    "gamma": re.compile(r"\\gamma"),
    "delta": re.compile(r"\\delta"),
    "infty": re.compile(r"\\infty"),
    "leq": re.compile(r"\\leq"),
    "geq": re.compile(r"\\geq"),
    "neq": re.compile(r"\\neq"),
    "approx": re.compile(r"\\approx"),
    "in": re.compile(r"\\in"),
    "subset": re.compile(r"\\subset"),
    "cup": re.compile(r"\\cup"),
    "cap": re.compile(r"\\cap"),
    "forall": re.compile(r"\\forall"),
    "exists": re.compile(r"\\exists"),
    "emptyset": re.compile(r"\\emptyset"),
    "mathbb": re.compile(r"\\mathbb\{[^}]+\}"),
    "mathcal": re.compile(r"\\mathcal\{[^}]+\}"),
    "mathrm": re.compile(r"\\mathrm\{[^}]+\}"),
    "hat": re.compile(r"\\hat\{[^}]+\}"),
    "bar": re.compile(r"\\bar\{[^}]+\}"),
    "vec": re.compile(r"\\vec\{[^}]+\}"),
    "dot": re.compile(r"\\dot\{[^}]+\}"),
    "ddot": re.compile(r"\\ddot\{[^}]+\}"),
    "superscript": re.compile(r"\^\{[^}]+\}"),
    "subscript": re.compile(r"_\{[^}]+\}"),
    "binom": re.compile(r"\\binom\{[^}]+\}\{[^}]+\}"),
    "lim": re.compile(r"\\lim[_\^]*\{?[^}]*\}?"),
    "exp": re.compile(r"\\exp"),
    "log": re.compile(r"\\log"),
    "sin": re.compile(r"\\sin"),
    "cos": re.compile(r"\\cos"),
    "tan": re.compile(r"\\tan"),
    "min": re.compile(r"\\min"),
    "max": re.compile(r"\\max"),
    "det": re.compile(r"\\det"),
    "trace": re.compile(r"\\mathrm\{tr\}|\\trace"),
    "norm": re.compile(r"\\|[^|]+\\|"),
    "inner_product": re.compile(r"\\langle[^|]+\\rangle"),
    "floor": re.compile(r"\\lfloor[^}]+\\rfloor"),
    "ceil": re.compile(r"\\lceil[^}]+\\rceil"),
}


def extract_unicode_math(text: str) -> List[Dict[str, Any]]:
    """Extract math expressions from Unicode plain text."""
    results = []
    seen = set()

    for pattern in UNICODE_MATH_PATTERNS:
        for m in pattern.finditer(text):
            expr = m.group(0).strip()
            if len(expr) < 3:
                continue
            key = (m.start(), m.end())
            if key in seen:
                continue
            seen.add(key)

            context_start = max(0, m.start() - 40)
            context_end = min(len(text), m.end() + 40)
            context = text[context_start:context_end].replace("\n", " ")

            math_char_count = sum(1 for c in expr if c in UNICODE_MATH_CHARS)

            results.append({
                "expression": expr,
                "position": m.start(),
                "context": context,
                "math_symbol_count": math_char_count,
                "length": len(expr),
                "type": "unicode",
            })

    results.sort(key=lambda x: x["position"])
    return results


def extract_latex_math(text: str) -> List[Dict[str, Any]]:
    """Extract LaTeX math expressions from text."""
    results = []
    seen = set()

    for name, pattern in LATEX_PATTERNS.items():
        for m in pattern.finditer(text):
            expr = m.group(0).strip()
            if len(expr) < 2:
                continue
            key = (m.start(), m.end())
            if key in seen:
                continue
            seen.add(key)

            context_start = max(0, m.start() - 40)
            context_end = min(len(text), m.end() + 40)
            context = text[context_start:context_end].replace("\n", " ")

            results.append({
                "expression": expr,
                "position": m.start(),
                "context": context,
                "math_symbol_count": len(expr),
                "length": len(expr),
                "type": f"latex_{name}",
            })

    results.sort(key=lambda x: x["position"])
    return results


def extract_math_from_text(text: str) -> Dict[str, Any]:
    """Extract all math expressions from clean text (both Unicode and LaTeX)."""
    unicode_math = extract_unicode_math(text)
    latex_math = extract_latex_math(text)

    all_math = unicode_math + latex_math
    all_math.sort(key=lambda x: x["position"])

    # Count unique math symbols
    symbol_counts: Dict[str, int] = {}
    for expr in all_math:
        for c in expr["expression"]:
            if c in UNICODE_MATH_CHARS:
                symbol_counts[c] = symbol_counts.get(c, 0) + 1

    # Calculate math density
    math_chars = sum(len(e["expression"]) for e in all_math)
    total_chars = len(text)
    math_density = round(math_chars / total_chars, 6) if total_chars > 0 else 0.0

    return {
        "math_expressions": all_math,
        "total_math_expressions": len(all_math),
        "unicode_math_count": len(unicode_math),
        "latex_math_count": len(latex_math),
        "math_density": math_density,
        "unique_math_symbols": len(symbol_counts),
        "symbol_frequency": dict(sorted(symbol_counts.items(), key=lambda x: -x[1])[:20]),
    }


def extract_from_pdf(pdf_path: Path) -> Dict[str, Any]:
    """Extract math from a single PDF using PyMuPDF."""
    try:
        doc = pymupdf.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        return {"error": str(e)}

    math_results = extract_math_from_text(text)
    math_results["source_pdf"] = str(pdf_path)
    math_results["text_length"] = len(text)
    math_results["text_preview"] = text[:500].replace("\n", " ")

    return math_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract clean math from PDFs")
    parser.add_argument("--pdf", type=Path, help="Single PDF file")
    parser.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON file")
    args = parser.parse_args()

    if not args.pdf and not args.pdf_dir:
        print("ERROR: specify --pdf or --pdf-dir", file=sys.stderr)
        return 2

    results: Dict[str, Any] = {
        "extractor": "PyMuPDF (pymupdf)",
        "papers": [],
    }

    if args.pdf:
        print(f"Processing: {args.pdf}")
        result = extract_from_pdf(args.pdf)
        results["papers"].append(result)
        print(f"  -> {result.get('total_math_expressions', 0)} math expressions")
        print(f"  -> math density: {result.get('math_density', 0.0)}")

    if args.pdf_dir:
        if args.recursive:
            pdfs = sorted(args.pdf_dir.rglob("*.pdf"))
        else:
            pdfs = sorted(args.pdf_dir.glob("*.pdf"))
        print(f"Found {len(pdfs)} PDFs in {args.pdf_dir}")
        for pdf in pdfs:
            print(f"Processing: {pdf.name}")
            result = extract_from_pdf(pdf)
            results["papers"].append(result)
            print(f"  -> {result.get('total_math_expressions', 0)} math expressions")
            print(f"  -> math density: {result.get('math_density', 0.0)}")

    # Summary
    total_exprs = sum(p.get("total_math_expressions", 0) for p in results["papers"])
    avg_density = (
        sum(p.get("math_density", 0.0) for p in results["papers"]) / len(results["papers"])
        if results["papers"]
        else 0.0
    )
    results["summary"] = {
        "total_papers": len(results["papers"]),
        "total_math_expressions": total_exprs,
        "average_math_density": round(avg_density, 6),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nOutput: {args.out}")
    print(f"Total: {total_exprs} math expressions across {len(results['papers'])} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
