#!/usr/bin/env python3
"""
END-TO-END MATH PIPELINE
========================
Target: fetch arxiv.org/html/ paper → extract math + surrounding words →
parse → solve → relate → machine-readable JSON.

This is the real green test: can we take any paper from arxiv, extract its
math, read the words around it, solve what's solvable, and produce a
machine-readable artifact that relates math to context?

Usage:
  python e2e_math_pipeline.py --arxiv 2605.00155
  python e2e_math_pipeline.py --arxiv 2605.00155 --output DATASETS/e2e_output.json
  python e2e_math_pipeline.py --corpus DATASETS/arxiv_html_corpus/2605.00155.json
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup
from mathml_parser import MathMLParser, extract_from_html
from test_integral_ir import parse_integral, Expression, Limit, Differential, Integral

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

USER_AGENT = "math-e2e-pipeline/1.0"


def fetch_arxiv_html(arxiv_id, timeout=30):
    """Fetch HTML version of an arxiv paper."""
    url = f"https://arxiv.org/html/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), url
    except Exception as e:
        print(f"  [FETCH] failed {url}: {e}")
        return None, url


def _get_context(math_tag):
    """
    Get the text surrounding a math tag by walking up to the nearest
    text-bearing ancestor and extracting text before/after the math tag.
    """
    # Walk up to find a text-bearing ancestor
    ancestor = math_tag.parent
    while ancestor:
        if ancestor.name in ("p", "div", "span", "td", "th", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            break
        ancestor = ancestor.parent

    if ancestor is None:
        return "", ""

    # Get all text in the ancestor
    full_text = ancestor.get_text(" ", strip=True)

    # Get the math tag's text
    math_text = math_tag.get_text(" ", strip=True)

    # Find the math text in the full text
    idx = full_text.find(math_text)
    if idx == -1:
        return "", ""

    before = full_text[:idx].strip()
    after = full_text[idx + len(math_text):].strip()

    # Limit to reasonable length
    return before[-200:], after[:200]


def extract_math_with_context(html):
    """
    Extract every equation with its surrounding context.
    Returns list of dicts with math + words before/after.
    """
    soup = BeautifulSoup(html, "html.parser")
    equations = []

    for occ_index, math_tag in enumerate(soup.find_all("math")):
        alttext = math_tag.get("alttext") or ""
        ann = math_tag.find("annotation")
        latex = ann.get_text().strip() if ann else alttext

        parser = MathMLParser()
        tree_expr, unsupported = parser.parse(math_tag)

        if not tree_expr and not unsupported:
            continue

        # Context: walk up to nearest text-bearing ancestor
        ctx_before, ctx_after = _get_context(math_tag)

        # Display detection
        is_display = False
        for anc in math_tag.parents:
            cls = anc.get("class") or []
            if any("ltx_equation" in c or "ltx_eqn_row" in c for c in cls):
                is_display = True
                break

        equations.append({
            "occurrence": occ_index,
            "latex": latex,
            "expr": tree_expr,
            "mathml": str(math_tag),
            "context_before": ctx_before,
            "context_after": ctx_after,
            "is_display": is_display,
            "unsupported": unsupported,
            "symbols": sorted(parser.symbols),
            "source": "mathml_tree" if tree_expr else "latex_fallback",
        })

    return equations


def count_equalities(s):
    """Count TRUE equality signs, excluding <=, >=, !=, and fused tokens."""
    s = re.sub(r'<=|>=|!=|\\leq|\\geq|\\neq|≤|≥|≠', '', s)
    s = re.sub(r'_eq_', '', s)
    return s.count('=')


def try_solve(expr_str):
    """
    Attempt to parse and evaluate an expression with SymPy.
    Returns (solvable, result, error).
    
    "Solvable" means SymPy can parse and evaluate the expression.
    This includes equations, inequalities, and plain expressions.
    """
    if not expr_str:
        return False, None, "empty"

    # Reject non-equality relations at top level
    non_eq = ["sim", "approx", "simeq", "cong", "asymp", "propto", "equiv",
              "!=", "<=", ">=", "->", "<-", "=>", "<=>", "in", "notin"]
    for tok in non_eq:
        if tok in expr_str:
            return False, None, f"relation:{tok}"

    try:
        result = parse_expr(expr_str, transformations=TRANSFORMS, evaluate=True)
        return True, str(result), None
    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}"


def relate_to_context(eq, all_equations, eq_index):
    """
    Relate an equation to its surrounding context and other equations.
    """
    relations = []
    eq_occurrence = eq.get("occurrence", eq_index)

    # Find equations that share symbols
    my_symbols = set(eq.get("symbols", []))
    for i, other in enumerate(all_equations):
        if i == eq_index:
            continue
        other_symbols = set(other.get("symbols", []))
        shared = my_symbols & other_symbols
        if shared:
            relations.append({
                "type": "shared_symbols",
                "other_occurrence": other.get("occurrence", i),
                "shared": sorted(shared),
            })

    # Context keywords
    ctx = (eq.get("context_before", "") + " " + eq.get("context_after", "")).lower()
    keywords = []
    for kw in ["define", "definition", "theorem", "lemma", "proof", "corollary",
               "proposition", "example", "remark", "note", "observe", "recall",
               "where", "such that", "subject to", "constraint", "objective",
               "loss", "function", "model", "distribution", "probability",
               "expectation", "variance", "gradient", "derivative", "integral",
               "sum", "product", "limit", "maximum", "minimum", "optimal"]:
        if kw in ctx:
            keywords.append(kw)

    return {
        "context_keywords": keywords,
        "related_equations": relations[:5],  # top 5
        "context_snippet": (eq.get("context_before", "") + " ||| " + eq.get("context_after", ""))[:200],
    }


def process_paper(arxiv_id, html, url):
    """
    Full pipeline: extract → parse → solve → relate → output.
    """
    print(f"\n{'='*84}")
    print(f"END-TO-END MATH PIPELINE")
    print(f"Paper: {arxiv_id}")
    print(f"URL: {url}")
    print(f"{'='*84}\n")

    # Step 1: Extract
    print("STEP 1: Extract math + context from HTML")
    equations = extract_math_with_context(html)
    print(f"  Extracted {len(equations)} equations")

    # Step 2: Parse + Solve
    print("\nSTEP 2: Parse and solve")
    solvable_count = 0
    partial_count = 0
    rejected_count = 0

    for eq in equations:
        expr = eq.get("expr", "")

        # Try integral parsing first
        mathml = eq.get("mathml", "")
        if mathml and ("∫" in eq.get("latex", "") or "\\int" in eq.get("latex", "")):
            node, notes = parse_integral(mathml)
            if node:
                eq["integral_ir"] = node.to_dict()
                if notes:
                    eq["integral_notes"] = notes
                    partial_count += 1
                else:
                    solvable_count += 1
            else:
                rejected_count += 1

        # Try SymPy solving
        if expr:
            solvable, result, error = try_solve(expr)
            if solvable:
                eq["solved"] = result
                solvable_count += 1
            elif error and error != "not_equation":
                eq["solve_error"] = error
                if "relation:" in error:
                    partial_count += 1
                else:
                    rejected_count += 1

    print(f"  Solvable: {solvable_count}")
    print(f"  Partial:  {partial_count}")
    print(f"  Rejected: {rejected_count}")

    # Step 3: Relate
    print("\nSTEP 3: Relate equations to context")
    for i, eq in enumerate(equations):
        eq["relations"] = relate_to_context(eq, equations, i)

    # Step 4: Build output
    print("\nSTEP 4: Build machine-readable output")
    output = {
        "arxiv_id": arxiv_id,
        "url": url,
        "total_equations": len(equations),
        "solvable": solvable_count,
        "partial": partial_count,
        "rejected": rejected_count,
        "equations": equations,
    }

    # Summary
    print(f"\n{'='*84}")
    print(f"RESULT: {len(equations)} equations, {solvable_count} solvable, {partial_count} partial, {rejected_count} rejected")
    print(f"{'='*84}")

    return output


def main():
    parser = argparse.ArgumentParser(description="End-to-end math pipeline")
    parser.add_argument("--arxiv", help="Arxiv ID (e.g. 2605.00155)")
    parser.add_argument("--corpus", help="Path to corpus JSON file")
    parser.add_argument("--output", help="Output JSON file", default=None)
    args = parser.parse_args()

    if args.corpus:
        # Load from corpus
        data = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
        arxiv_id = data.get("arxiv_id", "unknown")
        url = data.get("url", "")
        # Reconstruct HTML from mathml (we don't have full HTML in corpus)
        # Instead, process the equations directly
        print(f"\n{'='*84}")
        print(f"END-TO-END MATH PIPELINE (corpus mode)")
        print(f"Paper: {arxiv_id}")
        print(f"{'='*84}\n")

        equations = data.get("equations", [])
        print(f"  Loaded {len(equations)} equations from corpus")

        # Parse + solve
        solvable_count = 0
        partial_count = 0
        rejected_count = 0

        for i, eq in enumerate(equations):
            # Parse expr from MathML if not already present
            if "expr" not in eq and eq.get("mathml"):
                mml_soup = BeautifulSoup(eq["mathml"], "html.parser")
                math_tag = mml_soup.find("math")
                if math_tag:
                    p = MathMLParser()
                    expr, unsupported = p.parse(math_tag)
                    eq["expr"] = expr
                    if unsupported:
                        eq["unsupported"] = unsupported
                    eq["symbols"] = sorted(p.symbols)

            expr = eq.get("expr", "") or ""
            latex = eq.get("latex", "")

            # Try integral parsing
            mathml = eq.get("mathml", "")
            if mathml and ("∫" in latex or "\\int" in latex):
                node, notes = parse_integral(mathml)
                if node:
                    eq["integral_ir"] = node.to_dict()
                    if notes:
                        eq["integral_notes"] = notes
                        partial_count += 1
                    else:
                        solvable_count += 1
                else:
                    rejected_count += 1

            # Try SymPy solving
            if expr:
                solvable, result, error = try_solve(expr)
                if solvable:
                    eq["solved"] = result
                    solvable_count += 1
                elif error and error != "not_equation":
                    eq["solve_error"] = error
                    if "relation:" in error:
                        partial_count += 1
                    else:
                        rejected_count += 1

        # Relate
        for i, eq in enumerate(equations):
            eq["relations"] = relate_to_context(eq, equations, i)

        output = {
            "arxiv_id": arxiv_id,
            "url": url,
            "total_equations": len(equations),
            "solvable": solvable_count,
            "partial": partial_count,
            "rejected": rejected_count,
            "equations": equations,
        }

        print(f"\n  Solvable: {solvable_count}")
        print(f"  Partial:  {partial_count}")
        print(f"  Rejected: {rejected_count}")

        if args.output:
            out_path = Path(args.output)
            out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\n  Output: {out_path}")

        print(f"\n{'='*84}")
        print(f"RESULT: {len(equations)} equations, {solvable_count} solvable, {partial_count} partial, {rejected_count} rejected")
        print(f"{'='*84}")

    elif args.arxiv:
        # Fetch from arxiv
        html, url = fetch_arxiv_html(args.arxiv)
        if html is None:
            print("Failed to fetch paper")
            sys.exit(1)

        output = process_paper(args.arxiv, html, url)

        if args.output:
            out_path = Path(args.output)
            out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\n  Output: {out_path}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
