"""
Prose Math Extractor
=====================

Detects math embedded in paragraph text (mid-paragraph math) and captures
the surrounding theory text. This is the "math in relation to words" layer.

For research/theory papers, math is often embedded in worded theory crafting:
    "The policy π is optimized against an estimated reward R̂, where
     R̂(x,y) = E[r(x,y)] + ε, while deployment performance is governed by
     the true reward R."

This module captures BOTH the math AND the surrounding prose, so downstream
consumers can see how the math relates to the theory.

Usage:
    from prose_math_extractor import ProseMathExtractor
    extractor = ProseMathExtractor()
    results = extractor.extract_from_html(html, arxiv_id="2605.00155")
    # results = [{math, latex, context_before, context_after, section, is_display, ...}, ...]

    # Or from a corpus file:
    results = extractor.extract_from_corpus("DATASETS/arxiv_html_corpus/2605.00155.json")
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


@dataclass
class ProseMathOccurrence:
    """A math occurrence with its surrounding prose context."""
    # Math content
    latex: str
    recovered_expr: str
    is_display: bool

    # Prose context
    context_before: str
    context_after: str
    section_title: str
    paragraph_text: str  # full paragraph containing this math

    # Position
    occurrence_index: int
    math_tag_index: int  # index among all <math> tags in document

    # Relationship analysis
    relationship: str = ""  # how the math relates to surrounding text
    theory_keywords: List[str] = field(default_factory=list)

    # Source
    arxiv_id: str = ""
    source: str = ""  # 'mathml_tree' or 'latex_fallback'


# ============================================================================
# Theory keyword detection
# ============================================================================

THEORY_KEYWORDS = [
    # RL / optimization
    "policy", "reward", "optimize", "objective", "constraint", "gradient",
    "convergence", "regret", "robust", "distribution", "ambiguity",
    "wasserstein", "transport", "cost", "distance", "metric",

    # Statistical
    "expectation", "variance", "probability", "distribution", "sample",
    "estimate", "estimator", "bias", "consistency", "asymptotic",

    # Mathematical
    "theorem", "lemma", "proof", "corollary", "proposition", "definition",
    "assumption", "condition", "property", "invariant",

    # ML specific
    "model", "parameter", "training", "inference", "loss", "regularization",
    "generalization", "overfitting", "underfitting", "capacity",

    # Logical
    "if", "then", "else", "when", "where", "such that", "subject to",
    "given", "let", "define", "denote", "write", "express",
]

RELATIONSHIP_PATTERNS = [
    # "where X is Y" — math defines a symbol
    (r"\bwhere\b", "definition"),
    # "if X then Y" — math is a condition
    (r"\bif\b", "condition"),
    # "let X = Y" — math is a definition
    (r"\blet\b", "definition"),
    # "define X as Y" — math is a definition
    (r"\bdefine\b", "definition"),
    # "X is called Y" — math is a naming
    (r"\bis called\b", "naming"),
    # "X denotes Y" — math is a notation
    (r"\bdenotes?\b", "notation"),
    # "X represents Y" — math is a representation
    (r"\brepresents?\b", "representation"),
    # "such that" — math is a constraint
    (r"\bsuch that\b", "constraint"),
    # "subject to" — math is a constraint
    (r"\bsubject to\b", "constraint"),
    # "we have" — math is a result
    (r"\bwe have\b", "result"),
    # "this gives" — math is a result
    (r"\bthis gives\b", "result"),
    # "it follows" — math is a consequence
    (r"\bit follows\b", "consequence"),
    # "therefore" — math is a conclusion
    (r"\btherefore\b", "conclusion"),
    # "thus" — math is a conclusion
    (r"\bthus\b", "conclusion"),
    # "hence" — math is a conclusion
    (r"\bhence\b", "conclusion"),
]


def _detect_relationship(context_before: str, context_after: str) -> str:
    """Detect how the math relates to the surrounding text."""
    combined = (context_before + " " + context_after).lower()
    for pattern, rel_type in RELATIONSHIP_PATTERNS:
        if re.search(pattern, combined):
            return rel_type
    return "embedded"  # default: math is just embedded in prose


def _extract_theory_keywords(text: str) -> List[str]:
    """Extract theory-related keywords from text."""
    text_lower = text.lower()
    found = []
    for kw in THEORY_KEYWORDS:
        if kw.lower() in text_lower:
            found.append(kw)
    return found


# ============================================================================
# Section detection
# ============================================================================

def _find_section_title(math_tag) -> str:
    """Find the nearest section title for a math tag."""
    # Walk up the tree looking for section headers
    for parent in math_tag.parents:
        if parent.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return parent.get_text(strip=True)
        # Also check for ltx_title classes (arxiv specific)
        classes = parent.get("class") or []
        if any("title" in c.lower() for c in classes):
            return parent.get_text(strip=True)
    return ""


def _get_paragraph_text(math_tag) -> str:
    """Get the full paragraph text containing this math tag."""
    # Find the nearest paragraph ancestor
    for parent in math_tag.parents:
        if parent.name in ("p", "div"):
            # Get text but replace math tags with a placeholder
            text = parent.get_text(" ", strip=True)
            # Clean up extra whitespace
            text = re.sub(r"\s+", " ", text).strip()
            return text[:500]  # cap length
    return ""


# ============================================================================
# Main extractor
# ============================================================================

class ProseMathExtractor:
    """Extract math occurrences with their prose context from arxiv HTML."""

    def __init__(self):
        if not HAS_BS4:
            raise RuntimeError("beautifulsoup4 required: pip install beautifulsoup4")

    def extract_from_html(self, html: str, arxiv_id: str = "") -> List[ProseMathOccurrence]:
        """Extract all math occurrences with prose context from HTML."""
        from mathml_parser import MathMLParser

        soup = BeautifulSoup(html, "html.parser")
        results = []
        parser = MathMLParser()

        for occ_idx, math_tag in enumerate(soup.find_all("math")):
            # Get LaTeX
            ann = math_tag.find("annotation")
            latex = ann.get_text().strip() if ann else (math_tag.get("alttext") or "")

            # Get recovered expression
            tree_expr, unsupported = parser.parse(math_tag)

            # Get context
            context_before = ""
            context_after = ""
            prev = math_tag.find_previous_sibling()
            nxt = math_tag.find_next_sibling()
            if prev:
                context_before = prev.get_text(" ", strip=True)[:300]
            if nxt:
                context_after = nxt.get_text(" ", strip=True)[:300]

            # Get section and paragraph
            section = _find_section_title(math_tag)
            paragraph = _get_paragraph_text(math_tag)

            # Detect display vs inline
            is_display = False
            for anc in math_tag.parents:
                cls = anc.get("class") or []
                if any("ltx_equation" in c or "ltx_eqn_row" in c for c in cls):
                    is_display = True
                    break

            # Detect relationship
            relationship = _detect_relationship(context_before, context_after)

            # Extract theory keywords
            theory_kw = _extract_theory_keywords(context_before + " " + context_after)

            results.append(ProseMathOccurrence(
                latex=latex,
                recovered_expr=tree_expr or latex,
                is_display=is_display,
                context_before=context_before,
                context_after=context_after,
                section_title=section,
                paragraph_text=paragraph,
                occurrence_index=occ_idx,
                math_tag_index=occ_idx,
                relationship=relationship,
                theory_keywords=theory_kw,
                arxiv_id=arxiv_id,
                source="mathml_tree" if tree_expr else "latex_fallback",
            ))

        return results

    def extract_from_corpus(self, corpus_path: str) -> List[ProseMathOccurrence]:
        """Extract from a corpus JSON file."""
        path = Path(corpus_path)
        if not path.exists():
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        arxiv_id = data.get("arxiv_id", path.stem)
        html = data.get("html", "")

        if not html:
            raise ValueError(f"No HTML content in {corpus_path}")

        return self.extract_from_html(html, arxiv_id)

    def to_json(self, results: List[ProseMathOccurrence], output_path: str):
        """Write results to JSON."""
        data = [asdict(r) for r in results]
        Path(output_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def get_summary(self, results: List[ProseMathOccurrence]) -> Dict:
        """Get summary statistics."""
        total = len(results)
        display_count = sum(1 for r in results if r.is_display)
        inline_count = total - display_count

        # Relationship distribution
        rel_counts = {}
        for r in results:
            rel_counts[r.relationship] = rel_counts.get(r.relationship, 0) + 1

        # Theory keyword frequency
        kw_counts = {}
        for r in results:
            for kw in r.theory_keywords:
                kw_counts[kw] = kw_counts.get(kw, 0) + 1

        # Section distribution
        section_counts = {}
        for r in results:
            sec = r.section_title or "(no section)"
            section_counts[sec] = section_counts.get(sec, 0) + 1

        return {
            "total_occurrences": total,
            "display_equations": display_count,
            "inline_math": inline_count,
            "relationship_distribution": rel_counts,
            "top_theory_keywords": sorted(kw_counts.items(), key=lambda x: -x[1])[:20],
            "section_distribution": section_counts,
        }


# ============================================================================
# Self-test
# ============================================================================

if __name__ == "__main__":
    # Test with a minimal HTML snippet
    test_html = """
    <html><body>
    <h2>Introduction</h2>
    <p>The policy π is optimized against an estimated reward R̂, where
    <math><mrow><mover><mi>R</mi><mo>^</mo></mover><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo><mo>=</mo><mi>E</mi><mo>[</mo><mi>r</mi><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo><mo>]</mo></mrow></math>
    while deployment performance is governed by the true reward R.</p>
    <p>If <math><mrow><mi>x</mi><mo>&gt;</mo><mn>0</mn></mrow></math> then
    <math><mrow><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi>x</mi></mrow></math>.</p>
    </body></html>
    """

    print("=== Prose Math Extractor Self-Test ===")
    extractor = ProseMathExtractor()
    results = extractor.extract_from_html(test_html, arxiv_id="test")

    print(f"Found {len(results)} math occurrences:")
    for r in results:
        print(f"\n  [{r.occurrence_index}] {r.relationship}")
        print(f"    LaTeX: {r.latex[:80]}")
        print(f"    Recovered: {r.recovered_expr[:80]}")
        print(f"    Context before: {r.context_before[:60]}")
        print(f"    Context after: {r.context_after[:60]}")
        print(f"    Theory keywords: {r.theory_keywords}")
        print(f"    Section: {r.section_title}")

    summary = extractor.get_summary(results)
    print(f"\nSummary: {json.dumps(summary, indent=2)}")
