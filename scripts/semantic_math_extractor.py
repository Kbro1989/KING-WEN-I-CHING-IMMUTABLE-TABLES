#!/usr/bin/env python3
"""
semantic_math_extractor.py — Extract semantic mathematical understanding from PDFs.

Uses PyMuPDF's word-level spatial data to reconstruct math expressions with:
1. Spatial layout — position, area, alignment, page context
2. Structural parsing — operators, functions, variables, brackets
3. Proof chain — premises, inference steps, conclusions, references
4. Page-level context — page number, total pages, page ID, cross-references

Usage:
    python semantic_math_extractor.py --pdf paper.pdf --out output.json
    python semantic_math_extractor.py --pdf-dir papers/ --recursive --out output.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pymupdf
except ImportError:
    print("ERROR: PyMuPDF required. Install: pip install pymupdf", file=sys.stderr)
    sys.exit(2)


# ── Math symbol detection ──────────────────────────────────────────
MATH_SYMBOLS = set(
    "φψχωΩΨΧπΠΣ∆∂∇αβγδεζηθικλμνξρστυϕ"
    "≡≠≤≥≈∝∞∈∉⊂⊃⊆⊇∪∩∀∃∅ℝℕℤℚℂ"
    "√∫∮∑∏∐⋀⋁⋂⋃"
    "−×÷±∓"
    "ˆ¯˙¨"
    "₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹"
    "ⁱⁿ⁺⁻⁼⁽⁾"
)

# ── Structural patterns ────────────────────────────────────────────
BRACKET_PAIRS = {
    "(": ")",
    "[": "]",
    "{": "}",
    "⟨": "⟩",
    "⌊": "⌋",
    "⌈": "⌉",
    "|": "|",
    "‖": "‖",
}

OPERATORS = {
    "+": "addition", "−": "subtraction", "×": "multiplication", "÷": "division",
    "±": "plus-minus", "∓": "minus-plus", "=": "equality", "≡": "equivalence",
    "≠": "inequality", "≤": "less-equal", "≥": "greater-equal",
    "≈": "approximation", "∝": "proportional", "∈": "element-of",
    "∉": "not-element-of", "⊂": "subset", "⊃": "superset",
    "⊆": "subset-equal", "⊇": "superset-equal", "∪": "union", "∩": "intersection",
    "∀": "for-all", "∃": "exists", "∅": "empty-set", "∞": "infinity",
    "∂": "partial-derivative", "∇": "nabla", "√": "square-root",
    "∫": "integral", "∮": "contour-integral", "∑": "summation", "∏": "product",
    "∐": "coproduct", "⋀": "wedge", "⋁": "vee", "⋂": "bigcap", "⋃": "bigcup",
}

FUNCTIONS = {
    "exp": "exponential", "log": "logarithm", "ln": "natural-log",
    "sin": "sine", "cos": "cosine", "tan": "tangent", "arctan": "arctangent",
    "arcsin": "arcsine", "arccos": "arccosine", "sinh": "hyperbolic-sine",
    "cosh": "hyperbolic-cosine", "tanh": "hyperbolic-tangent",
    "min": "minimum", "max": "maximum", "det": "determinant", "trace": "trace",
    "dim": "dimension", "rank": "rank", "ker": "kernel", "im": "image",
    "span": "span", "sup": "supremum", "inf": "infimum", "lim": "limit",
    "liminf": "limit-infimum", "limsup": "limit-supremum", "arg": "argument",
    "deg": "degree", "gcd": "greatest-common-divisor", "lcm": "least-common-multiple",
    "mod": "modulo", "floor": "floor", "ceil": "ceiling", "round": "round",
    "abs": "absolute-value", "norm": "norm", "inner": "inner-product",
    "outer": "outer-product", "cross": "cross-product", "dot": "dot-product",
    "tensor": "tensor-product", "direct": "direct-sum", "union": "union",
    "intersection": "intersection", "complement": "complement",
    "power": "power-set", "cartesian": "cartesian-product",
}

PROOF_INDICATORS = {
    "theorem": "theorem", "lemma": "lemma", "corollary": "corollary",
    "proposition": "proposition", "definition": "definition", "proof": "proof",
    "proofof": "proof-of", "sketch": "sketch", "remark": "remark",
    "example": "example", "exercise": "exercise", "conjecture": "conjecture",
    "axiom": "axiom", "assumption": "assumption", "hypothesis": "hypothesis",
    "claim": "claim", "fact": "fact", "observation": "observation",
    "note": "note", "warning": "warning", "caution": "caution",
    "property": "property", "condition": "condition", "criterion": "criterion",
    "algorithm": "algorithm", "procedure": "procedure", "method": "method",
    "construction": "construction", "induction": "induction",
    "contradiction": "contradiction", "contrapositive": "contrapositive",
    "bijection": "bijection", "injection": "injection", "surjection": "surjection",
    "isomorphism": "isomorphism", "homomorphism": "homomorphism",
    "automorphism": "automorphism", "endomorphism": "endomorphism",
    "epimorphism": "epimorphism", "monomorphism": "monomorphism",
}


def is_math_word(word: str) -> bool:
    """Check if a word contains math symbols or patterns."""
    if not word:
        return False
    if word in OPERATORS:
        return False
    if any(c in MATH_SYMBOLS for c in word):
        return True
    for func in FUNCTIONS:
        if re.search(rf"\b{func}\s*\(", word):
            return True
    for op in OPERATORS:
        if op in word:
            return True
    if "$" in word or "\\" in word:
        return True
    return False


def extract_math_expressions(text: str) -> List[Dict[str, Any]]:
    """Extract math expressions from text with structural info."""
    expressions = []
    
    # LaTeX inline (must have content)
    for m in re.finditer(r"\$([^$\n]+)\$", text):
        expr = m.group(1).strip()
        if expr and len(expr) > 2:
            expressions.append({
                "expression": expr,
                "type": "latex_inline",
                "position": m.start(),
                "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
            })
    
    # LaTeX display (must have content)
    for m in re.finditer(r"\$\$([^$]+)\$\$", text, re.DOTALL):
        expr = m.group(1).strip()
        if expr and len(expr) > 2:
            expressions.append({
                "expression": expr,
                "type": "latex_display",
                "position": m.start(),
                "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
            })
    
    # Unicode math (Greek letter + operator, must have complete structure)
    for m in re.finditer(r"[φψχωπΣ∆αβγδεζηθικλμνξρστυϕ][^\n]{0,80}[=≡≤≥][^\n]{0,80}", text):
        expr = m.group(0).strip()
        # Require at least 5 chars and a math symbol after the operator
        if len(expr) > 5 and any(c in MATH_SYMBOLS for c in expr[1:]):
            expressions.append({
                "expression": expr,
                "type": "unicode_equation",
                "position": m.start(),
                "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
            })
    
    # Function calls (must have content in parentheses)
    for func in FUNCTIONS:
        for m in re.finditer(rf"\b{func}\s*\([^\n]{{1,40}}\)", text):
            expr = m.group(0).strip()
            if len(expr) > 5:
                expressions.append({
                    "expression": expr,
                    "type": "function_call",
                    "function": func,
                    "position": m.start(),
                    "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
                })
    
    # Sort by position
    expressions.sort(key=lambda x: x["position"])
    return expressions


def analyze_spatial(bbox: tuple, page_width: float, page_height: float) -> Dict[str, Any]:
    """Analyze spatial layout of a text block."""
    x0, y0, x1, y1 = bbox
    
    # Calculate relative position
    rel_x = x0 / page_width if page_width > 0 else 0
    rel_y = y0 / page_height if page_height > 0 else 0
    rel_width = (x1 - x0) / page_width if page_width > 0 else 0
    rel_height = (y1 - y0) / page_height if page_height > 0 else 0
    
    # Calculate area
    area = (x1 - x0) * (y1 - y0)
    rel_area = area / (page_width * page_height) if page_width > 0 and page_height > 0 else 0
    
    # Determine alignment
    center_x = (x0 + x1) / 2
    page_center = page_width / 2
    if abs(center_x - page_center) < page_width * 0.1:
        alignment = "center"
    elif x0 < page_width * 0.2:
        alignment = "left"
    elif x1 > page_width * 0.8:
        alignment = "right"
    else:
        alignment = "left"
    
    # Determine if likely display math (centered, isolated)
    is_display_math = (
        alignment == "center"
        and rel_width > 0.3
        and rel_height < 0.1
    )
    
    return {
        "bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
        "relative_position": [round(rel_x, 4), round(rel_y, 4)],
        "relative_size": [round(rel_width, 4), round(rel_height, 4)],
        "area": round(area, 1),
        "relative_area": round(rel_area, 6),
        "alignment": alignment,
        "is_display_math": is_display_math,
    }


def extract_proof_chain(text: str, page_num: int) -> List[Dict[str, Any]]:
    """Extract proof chain elements from text."""
    chain = []
    
    for indicator, indicator_type in PROOF_INDICATORS.items():
        for m in re.finditer(rf"\b{indicator}\b", text, re.IGNORECASE):
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 100)
            context = text[start:end].replace("\n", " ")
            
            if indicator_type in ("note", "fact", "property", "condition"):
                if m.start() > 0 and text[m.start()-1] not in ".:\n":
                    continue
            
            chain.append({
                "type": indicator_type,
                "indicator": indicator,
                "position": m.start(),
                "page": page_num,
                "context": context,
            })
    
    for m in re.finditer(r"(?:Eq\.?|Equation)\s*\(?(\d+\.\d+)\)?", text):
        ref = m.group(1)
        chain.append({
            "type": "equation_reference",
            "reference": ref,
            "position": m.start(),
            "page": page_num,
            "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
        })
    
    for m in re.finditer(r"(?:by|from|using|via|see)\s+(?:Eq\.?|Theorem|Lemma|Corollary|Proposition|Definition)\s*\(?(\d+\.?\d*)\)?", text, re.IGNORECASE):
        chain.append({
            "type": "cross_reference",
            "reference": m.group(1),
            "position": m.start(),
            "page": page_num,
            "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
        })
    
    chain.sort(key=lambda x: x["position"])
    return chain


def extract_semantic_math_from_pdf(pdf_path: Path) -> Dict[str, Any]:
    """Extract semantic math understanding from a PDF."""
    try:
        doc = pymupdf.open(str(pdf_path))
    except Exception as e:
        return {"error": str(e)}
    
    total_pages = len(doc)
    pages_data = []
    
    for page_num in range(total_pages):
        page = doc[page_num]
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Get text blocks (pre-grouped by line)
        blocks = page.get_text("blocks")
        
        page_expressions = []
        
        for block in blocks:
            if block[6] != 0:  # Skip image blocks
                continue
            
            text = block[4]
            bbox = block[:4]
            
            if not text.strip():
                continue
            
            # Check if block contains math
            if not is_math_word(text):
                continue
            
            # Analyze spatial layout
            spatial = analyze_spatial(bbox, page_width, page_height)
            
            # Extract math expressions
            expressions = extract_math_expressions(text)
            
            # Count math symbols
            math_char_count = sum(1 for c in text if c in MATH_SYMBOLS)
            
            # Identify operators and functions
            operators_found = [op for op in OPERATORS if op in text]
            functions_found = [func for func in FUNCTIONS if re.search(rf"\b{func}\s*\(", text)]
            
            # Identify variables
            variables = re.findall(r"[a-zA-Z](?:_[a-zA-Z0-9]+)?", text)
            
            page_expressions.append({
                "text": text[:200],
                "spatial": spatial,
                "math_symbol_count": math_char_count,
                "operators": operators_found,
                "functions": functions_found,
                "variables": variables,
                "expressions": expressions,
            })
        
        # Get full text for proof chain
        full_text = page.get_text()
        proof_chain = extract_proof_chain(full_text, page_num + 1)
        
        pages_data.append({
            "page_number": page_num + 1,
            "total_pages": total_pages,
            "page_width": round(page_width, 1),
            "page_height": round(page_height, 1),
            "math_blocks": page_expressions,
            "proof_chain": proof_chain,
        })
    
    doc.close()
    
    # Aggregate
    all_expressions = []
    all_proof_chain = []
    for page in pages_data:
        for block in page["math_blocks"]:
            for expr in block["expressions"]:
                expr["page"] = page["page_number"]
                all_expressions.append(expr)
            for chain_elem in page["proof_chain"]:
                all_proof_chain.append(chain_elem)
    
    return {
        "source_pdf": str(pdf_path),
        "total_pages": total_pages,
        "pages": pages_data,
        "total_math_expressions": len(all_expressions),
        "total_proof_chain_elements": len(all_proof_chain),
        "math_expressions": all_expressions,
        "proof_chain": all_proof_chain,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract semantic math from PDFs")
    parser.add_argument("--pdf", type=Path, help="Single PDF file")
    parser.add_argument("--pdf-dir", type=Path, help="Directory of PDFs")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON file")
    args = parser.parse_args()

    if not args.pdf and not args.pdf_dir:
        print("ERROR: specify --pdf or --pdf-dir", file=sys.stderr)
        return 2

    results: Dict[str, Any] = {
        "extractor": "PyMuPDF semantic math extractor (block-level)",
        "papers": [],
    }

    if args.pdf:
        print(f"Processing: {args.pdf}")
        result = extract_semantic_math_from_pdf(args.pdf)
        results["papers"].append(result)
        print(f"  -> {result.get('total_math_expressions', 0)} math expressions")
        print(f"  -> {result.get('total_proof_chain_elements', 0)} proof chain elements")

    if args.pdf_dir:
        if args.recursive:
            pdfs = sorted(args.pdf_dir.rglob("*.pdf"))
        else:
            pdfs = sorted(args.pdf_dir.glob("*.pdf"))
        print(f"Found {len(pdfs)} PDFs in {args.pdf_dir}")
        for pdf in pdfs:
            print(f"Processing: {pdf.name}")
            result = extract_semantic_math_from_pdf(pdf)
            results["papers"].append(result)
            print(f"  -> {result.get('total_math_expressions', 0)} math expressions")
            print(f"  -> {result.get('total_proof_chain_elements', 0)} proof chain elements")

    total_exprs = sum(p.get("total_math_expressions", 0) for p in results["papers"])
    total_chain = sum(p.get("total_proof_chain_elements", 0) for p in results["papers"])
    results["summary"] = {
        "total_papers": len(results["papers"]),
        "total_math_expressions": total_exprs,
        "total_proof_chain_elements": total_chain,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nOutput: {args.out}")
    print(f"Total: {total_exprs} math expressions, {total_chain} proof chain elements across {len(results['papers'])} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
