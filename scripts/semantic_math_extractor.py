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
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pymupdf
except ImportError:
    print("ERROR: PyMuPDF required. Install: pip install pymupdf", file=sys.stderr)
    sys.exit(2)


# ── Math symbol detection ──────────────────────────────────
MATH_SYMBOLS = set(
    "φψχωΩΨΧπΠΣ∆∂∇αβγδεζηθικλμνξρστυϕ"
    "≡≠≤≥≈∝∞∈∉⊂⊃⊆⊇∪∩∀∃∅ℝℕℤℚℂ"
    "√∫∮∑∏∐⋀⋁⋂⋃"
    "−×÷±∓"
    "ˆ¯˙¨"
    "₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹"
    "ⁱⁿ⁺⁻⁼⁽⁾"
)

# ── LaTeX command detection ──────────────────────────────────
LATEX_COMMANDS = set(
    "frac sum int sqrt prod coprod bigcap bigcup bigvee bigwedge"
    "cdot times div pm mp circ bullet prime backprime"
    "ell forall partial nabla infty exists nexists emptyset varnothing"
    "nabla partial Delta abla acute grave dot ddot tilde bar hat vec"
    "check hat widevec dot ddot tilde bar acute grave dot"
    "mathrm mathbf mathit mathcal mathbb mathsf mathrm"
    "left right big Big LARGE huge huge"
    "limits displaystyle textstyle scriptscriptstyle"
    "binom pmatrix matrix cases align gather multline equation"
    "begin end item enumerate description"
    "langle rangle lfloor rfloor lceil rceil vert Vbar"
    "Vert backvert forwardvert doublevert"
    "longrightarrow longleftarrow longleftrightarrow"
    "Rightarrow Leftarrow Leftrightarrow"
    "tomapsto longmapsto"
    "oplus otimes bigodot bigotimes bigoplus"
    "cap cup subset supset subseteq supseteq"
    "subseteqq supseteqq subsetneq supsetneq"
    "sqsubseteq sqsupseteq sqsubset sqsupset"
    "in ni notin subset supset"
    "land lor lnot neg flat natural sharp"
    "wp therefore because ell imax imin"
    "DeclareMathOperator arccos arcsin arctan cosh sinh tanh"
    "argmax argmin ker im rank null"
    "mathalpha mathnormal mathit mathbf mathrm mathsf mathcal"
    "mathbb oldstyle boldsymbol mathfrak mathbb"
    "qquad qquad qquad qquad"
)

# ── Math image indicators ──────────────────────────────────
MATH_IMAGE_INDICATORS = {
    "equation", "fig:", "figure", "table", "diagram", "graph", "chart",
    "screenshot", "render", "plot", "math", "formula", "display",
}

# ── Bracket pairs ──────────────────────────────────────────
BRACKET_PAIRS = {
    "(": ")", "[": "]", "{": "}",
    "⟨": "⟩", "«": "»", "【": "】",
    "(": ")", "[": "]", "{": "}",
}

# ── Operators ──────────────────────────────────────────────
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

# ── Functions ──────────────────────────────────────────────
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
    "tensor": "tensor-product", "direct": "direct-sum",
    "union": "union", "intersection": "intersection",
    "complement": "complement", "power": "power-set",
    "cartesian": "cartesian-product",
}

# ── Proof indicators ───────────────────────────────────────
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
    """Check if a word/block contains math symbols or patterns."""
    if not word:
        return False
    if word in OPERATORS:
        return False
    # Control characters and CRLF artifacts → not math (garbled PDF content)
    if '\x00' in word or '\ufffd' in word or '\r\n' in word or '\x0c' in word:
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
    # Skip text with control characters / CRLF artifacts — garbled PDF blocks
    if '\x00' in text or '\ufffd' in text or '\r\n' in text or '\x0c' in text:
        return expressions

    # LaTeX inline (must have content)
    for m in re.finditer(r"\$([^$\n]+)\$", text):
        expr = m.group(1).strip()
        if expr and len(expr) > 2:
            expressions.append({
                "expression": expr,
                "type": "latex_inline",
                "position": m.start(),
                "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
                "text": text[:200],
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
                "text": text[:200],
            })

    # Unicode math (Greek letter + operator, must have complete structure)
    for m in re.finditer(r"[φψχωΩΨΧπΠΣ∆∂∇αβγδεζηθικλμνξρστυϕ][^\n]{0,80}[=≡≤≥][^\n]{0,80}", text):
        expr = m.group(0).strip()
        # Require at least 5 chars and a math symbol after the operator
        if len(expr) > 5 and any(c in MATH_SYMBOLS for c in expr[1:]):
            expressions.append({
                "expression": expr,
                "type": "unicode_equation",
                "position": m.start(),
                "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
                "text": text[:200],
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
                    "text": text[:200],
                })

    # LaTeX commands (rendered as glyphs in PDF, but present as text)
    for cmd in sorted(LATEX_COMMANDS, key=len, reverse=True):
        for m in re.finditer(rf"\\{cmd}\b", text):
            expr = m.group(0).strip()
            if expr and len(expr) > 2:
                expressions.append({
                    "expression": expr,
                    "type": "latex_command",
                    "command": cmd,
                    "position": m.start(),
                    "context": text[max(0, m.start()-30):m.end()+30].replace("\n", " "),
                })

    # Sort by position
    expressions.sort(key=lambda x: x["position"])
    return expressions


def detect_math_images(page) -> List[Dict[str, Any]]:
    """Detect images that may contain math (equations, diagrams)."""
    images = []
    try:
        # Get image list from page
        page_images = page.get_images(full=True)
        for img in page_images:
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            if base_image:
                images.append({
                    "xref": xref,
                    "width": base_image.get("width", 0),
                    "height": base_image.get("height", 0),
                    "ext": base_image.get("ext", "unknown"),
                    "size": len(base_image.get("image", b"")),
                })
    except Exception:
        pass

    # Also check for inline image blocks (PyMuPDF block type 1)
    try:
        blocks = page.get_text("blocks")
        for block in blocks:
            if block[6] == 1:  # Image block
                images.append({
                    "block_bbox": list(block[:4]),
                    "type": "inline_image",
                })
    except Exception:
        pass

    return images


def analyze_spatial(bbox: tuple, page_width: float, page_height: float) -> Dict[str, Any]:
    """Analyze spatial layout of a text block."""
    x0, y0, x1, y1 = bbox
    return {
        "x0": round(x0, 1), "y0": round(y0, 1),
        "x1": round(x1, 1), "y1": round(y1, 1),
        "width": round(x1 - x0, 1), "height": round(y1 - y0, 1),
        "center_x": round((x0 + x1) / 2, 1),
        "center_y": round((y0 + y1) / 2, 1),
        "page_width": round(page_width, 1), "page_height": round(page_height, 1),
        "is_left": x0 < page_width * 0.3,
        "is_center": page_width * 0.3 <= x0 < page_width * 0.7,
        "is_right": x0 >= page_width * 0.7,
        "is_display": y0 < page_height * 0.25,
        "is_footnote": y1 > page_height * 0.85,
    }


def extract_proof_chain(text: str, page_num: int) -> List[Dict[str, Any]]:
    """Extract proof chain elements from page text."""
    chain = []
    for indicator, ptype in PROOF_INDICATORS.items():
        pattern = rf"\b{indicator}\b"
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            context = text[start:end].replace("\n", " ")
            chain.append({
                "type": ptype,
                "keyword": indicator,
                "page": page_num,
                "position": m.start(),
                "context": context,
            })
    return chain


def extract_pdf_math(pdf_path: str) -> Dict[str, Any]:
    """Extract all math from a PDF file."""
    doc = pymupdf.open(pdf_path)
    pages_data = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_width = page.rect.width
        page_height = page.rect.height

        blocks = page.get_text("blocks")
        page_expressions = []

        for block in blocks:
            if block[6] != 0:  # Skip image blocks
                continue

            text = block[4]
            bbox = block[:4]

            if not text.strip():
                continue

            if not is_math_word(text):
                continue

            spatial = analyze_spatial(bbox, page_width, page_height)
            expressions = extract_math_expressions(text)
            math_char_count = sum(1 for c in text if c in MATH_SYMBOLS)
            operators_found = [op for op in OPERATORS if op in text]
            functions_found = [func for func in FUNCTIONS if re.search(rf"\b{func}\s*\(", text)]
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

        math_images = detect_math_images(page)
        full_text = page.get_text()
        proof_chain = extract_proof_chain(full_text, page_num + 1)

        pages_data.append({
            "page_number": page_num + 1,
            "total_pages": len(doc),
            "page_width": round(page_width, 1),
            "page_height": round(page_height, 1),
            "math_blocks": page_expressions,
            "math_images": math_images,
            "proof_chain": proof_chain,
        })

    doc.close()

    # Aggregate
    all_expressions = []
    all_proof_chain = []
    for page in pages_data:
        for block in page['math_blocks']:
            for expr in block['expressions']:
                expr['page'] = page['page_number']
                all_expressions.append(expr)
            for chain_elem in page['proof_chain']:
                all_proof_chain.append(chain_elem)

    return {
        "source_pdf": pdf_path,
        "total_pages": len(pages_data),
        "pages": pages_data,
        "total_math_expressions": len(all_expressions),
        "total_proof_chain_elements": len(all_proof_chain),
        "math_expressions": all_expressions,
        "proof_chain": all_proof_chain,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract semantic math from PDFs")
    parser.add_argument("--pdf", help="Single PDF file")
    parser.add_argument("--pdf-dir", help="Directory of PDFs")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories")
    parser.add_argument("--out", default="DATASETS/semantic_math_zotero_full.json", help="Output JSON path")
    args = parser.parse_args()

    if args.pdf:
        result = extract_pdf_math(args.pdf)
        output = {"extractor": "PyMuPDF semantic math extractor", "papers": [result],
                  "summary": {"total_papers": 1, "total_math_expressions": result["total_math_expressions"],
                              "total_proof_chain_elements": result["total_proof_chain_elements"]}}
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Extracted {result['total_math_expressions']} expressions from {args.pdf}")
        return

    pdf_dir = args.pdf_dir or r'C:\Users\krist\Desktop\zotero\learning-corpus'
    pdfs = []
    if args.recursive:
        for root, dirs, files in os.walk(pdf_dir):
            for f in files:
                if f.endswith('.pdf'):
                    pdfs.append(os.path.join(root, f))
    else:
        for f in os.listdir(pdf_dir):
            if f.endswith('.pdf'):
                pdfs.append(os.path.join(pdf_dir, f))

    print(f"Found {len(pdfs)} PDFs")

    results = []
    errors = []
    for i, pdf_path in enumerate(pdfs):
        try:
            result = extract_pdf_math(pdf_path)
            results.append(result)
            if (i + 1) % 25 == 0:
                print(f"Processed {i + 1}/{len(pdfs)}... {len(results)} papers")
        except Exception as e:
            errors.append((pdf_path, str(e)))

    output = {
        "extractor": "PyMuPDF semantic math extractor (block-level)",
        "papers": results,
        "summary": {
            "total_papers": len(results),
            "total_math_expressions": sum(p.get("total_math_expressions", 0) for p in results),
            "total_proof_chain_elements": sum(p.get("total_proof_chain_elements", 0) for p in results),
            "errors": len(errors),
        },
        "errors": errors[:10],
    }

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {len(results)} papers, {output['summary']['total_math_expressions']} exprs, {output['summary']['total_proof_chain_elements']} chain elements")
    if errors:
        print(f"Errors: {len(errors)}")
        for path, err in errors[:5]:
            print(f"  {os.path.basename(path)}: {err}")


if __name__ == "__main__":
    main()