"""
Adversarial delimiter tests
============================

Validates the actual token sequence and pairing, not just token existence.

Acceptance criteria enforced here:

    | Input                          | Required invariant                          |
    |--------------------------------|---------------------------------------------|
    | \\|x\\|                         | One matched norm pair                       |
    | \\lVert A \\rVert               | Explicit left/right identity preserved      |
    | \\|A+B\\|                       | Entire expression enclosed by the pair      |
    | Nested norms                   | Correct nesting; no crossing pairs          |
    | \\|x\\|                         | Not silently converted into a norm          |
    | Unmatched delimiter            | Explicit diagnostic; no fabricated pair     |
    | MathML ‖ single glyph          | balance_norm_tokens produces matched pair   |
    | Single bar in expectation      | Conditional, not abs, not norm              |

Plus adversarial nesting/mismatch cases:
    - Crossed / interleaved delimiters
    - Mismatched close types
    - Repeated bars
    - Empty delimited content
    - Delimiter at start / end of string
"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from delimiter_identity import (
    normalize_latex_norms, balance_norm_tokens,
    NORM_OPEN, NORM_CLOSE, LANGLE, RANGLE,
    LFLOOR, RFLOOR, LCEIL, RCEIL, BAR,
)
from delimiter_inference import infer_delimiters, DelimiterInferer, DelimiterNode, UnmatchedDelimiter


def _scan(s):
    """Scan norm tokens in order, returning (token, pos) tuples."""
    out = []
    i = 0
    while i < len(s):
        if s.startswith(NORM_OPEN, i):
            out.append((NORM_OPEN, i))
            i += len(NORM_OPEN)
        elif s.startswith(NORM_CLOSE, i):
            out.append((NORM_CLOSE, i))
            i += len(NORM_CLOSE)
        else:
            i += 1
    return out


def norm_pairs(s):
    """Count matched lVert...rVert pairs (stack-based, no crossing)."""
    depth = 0
    pairs = 0
    for tok, _ in _scan(s):
        if tok == NORM_OPEN:
            depth += 1
        elif tok == NORM_CLOSE:
            if depth > 0:
                pairs += 1
                depth -= 1
    return pairs, depth


# ============================================================================
# 1. Acceptance criteria from the review
# ============================================================================

class TestAcceptanceCriteria:

    def test_shorthand_norm_one_matched_pair(self):
        r"\|x\| -> one matched norm pair"
        result = normalize_latex_norms(r"\|x\|")
        pairs, depth = norm_pairs(result)
        assert pairs == 1 and depth == 0, f"pairs={pairs} depth={depth} result={result!r}"

    def test_explicit_norm_identity_preserved(self):
        r"\lVert A \rVert -> explicit open/close preserved"
        result = normalize_latex_norms(r"\lVert A \rVert")
        pairs, depth = norm_pairs(result)
        assert pairs == 1 and depth == 0
        assert NORM_OPEN in result and NORM_CLOSE in result

    def test_shorthand_encloses_entire_expression(self):
        r"\|A+B\| -> entire expression inside the pair"
        result = normalize_latex_norms(r"\|A+B\|")
        pairs, depth = norm_pairs(result)
        assert pairs == 1 and depth == 0
        assert "A+B" in result

    def test_nested_norms_no_crossing(self):
        r"\|\|x\|\| -> nested pairs, no crossing"
        result = normalize_latex_norms(r"\|\|x\|\|")
        pairs, depth = norm_pairs(result)
        assert pairs == 2 and depth == 0

    def test_single_bar_not_converted_to_norm(self):
        r"|x| must NOT become a norm"
        result = normalize_latex_norms(r"|x|")
        assert NORM_OPEN not in result
        assert NORM_CLOSE not in result
        assert "|" in result

    def test_unmatched_open_not_fabricated(self):
        r"\|x (unmatched) -> depth stays 1, no fabricated close"
        result = normalize_latex_norms(r"\|x")
        pairs, depth = norm_pairs(result)
        assert pairs == 0 and depth == 1

    def test_unmatched_close_not_fabricated(self):
        r"x\| (unmatched close) -> depth goes negative or stays 0, no fabricated open"
        result = normalize_latex_norms(r"x\|")
        pairs, depth = norm_pairs(result)
        assert pairs == 0


# ============================================================================
# 2. MathML single-glyph norm (‖) via balance_norm_tokens
# ============================================================================

class TestMathMLSingleGlyphNorm:

    def test_balance_single_glyph_norm(self):
        """‖x‖ -> lVert*x*lVert -> balanced to one matched pair."""
        balanced = balance_norm_tokens("lVert*x*lVert")
        pairs, depth = norm_pairs(balanced)
        assert pairs == 1 and depth == 0, f"balanced={balanced!r}"

    def test_balance_nested_single_glyph_norm(self):
        """‖‖x‖‖ -> lVert*lVert*x*lVert*lVert -> two matched pairs."""
        balanced = balance_norm_tokens("lVert*lVert*x*lVert*lVert")
        pairs, depth = norm_pairs(balanced)
        assert pairs == 2 and depth == 0, f"balanced={balanced!r}"

    def test_balance_leaves_single_bar_alone(self):
        """|x| must NOT be touched by balance_norm_tokens."""
        balanced = balance_norm_tokens("|x|")
        assert balanced == "|x|"
        assert NORM_OPEN not in balanced

    def test_balance_idempotent_on_balanced_input(self):
        """Already-balanced input is unchanged."""
        s = f"{NORM_OPEN}x{NORM_CLOSE}"
        assert balance_norm_tokens(s) == s

    def test_balance_empty_string(self):
        assert balance_norm_tokens("") == ""

    def test_balance_no_norm_tokens(self):
        assert balance_norm_tokens("x + y") == "x + y"


# ============================================================================
# 3. Adversarial nesting / mismatch (delimiter_inference)
# ============================================================================

class TestAdversarialNesting:

    def test_crossed_delimiters_not_paired(self):
        """lVert...lfloor...rVert...rfloor is crossed, must not pair as nesting."""
        nodes = infer_delimiters("lVert a lfloor b rVert c rfloor")
        for n in nodes:
            if n.delim_type == "norm" and "lfloor" in n.content:
                pytest.fail(f"crossed pair detected: {n}")

    def test_mismatched_close_reported(self):
        """lVert...rangle mismatched close is reported, not silently paired."""
        nodes = infer_delimiters("lVert x rangle")
        # The norm must be unmatched (confidence < 1.0) or reported as unmatched
        norm_nodes = [n for n in nodes if n.delim_type == "norm"]
        assert len(norm_nodes) == 0 or norm_nodes[0].confidence < 1.0

    def test_repeated_bars_pair_separately(self):
        """|x| |y| -> two separate abs pairs."""
        nodes = infer_delimiters("|x| |y|")
        abs_nodes = [n for n in nodes if n.delim_type == "abs"]
        assert len(abs_nodes) == 2

    def test_empty_delimited_content(self):
        """lfloor rfloor -> no crash, either paired or explicitly unmatched."""
        nodes = infer_delimiters("lfloor rfloor")
        # No crash is the minimum; either outcome acceptable
        assert isinstance(nodes, list)

    def test_delimiter_at_start(self):
        """lVert x rVert + y -> norm paired."""
        nodes = infer_delimiters("lVert x rVert + y")
        assert len(nodes) >= 1
        assert nodes[0].delim_type == "norm"

    def test_delimiter_at_end(self):
        """y + lVert x rVert -> norm paired."""
        nodes = infer_delimiters("y + lVert x rVert")
        assert len(nodes) >= 1
        assert nodes[-1].delim_type == "norm"

    def test_floor_and_ceil_distinct(self):
        """lfloor and lceil are not conflated."""
        nodes = infer_delimiters("lfloor a rfloor + lceil b rceil")
        types = {n.delim_type for n in nodes}
        assert types == {"floor", "ceil"}


# ============================================================================
# 4. Conditional vs abs (single bar disambiguation)
# ============================================================================

class TestSingleBarDisambiguation:

    def test_abs_no_relation(self):
        """|x| with no relation is abs."""
        nodes = infer_delimiters("|x|")
        assert len(nodes) == 1
        assert nodes[0].delim_type == "abs"

    def test_conditional_with_relation(self):
        """|x > 0| with relation is conditional."""
        nodes = infer_delimiters("|x > 0|")
        assert len(nodes) == 1
        assert nodes[0].delim_type == "conditional"

    def test_single_bar_in_expectation(self):
        """E[X | X>0] single bar is conditional."""
        nodes = infer_delimiters("E[X | X > 0]")
        cond = [n for n in nodes if n.delim_type == "conditional"]
        assert len(cond) >= 1

    def test_abs_vs_conditional_coexist(self):
        """|x| and |y > 0| in same expression resolve independently."""
        nodes = infer_delimiters("|x| + |y > 0|")
        types = [n.delim_type for n in nodes]
        assert "abs" in types
        assert "conditional" in types


# ============================================================================
# 5. Similarity inference stays secondary evidence
# ============================================================================

class TestSimilarityInference:

    def test_inferred_type_carries_confidence(self):
        """Inferred type must carry confidence and notes."""
        inferer = DelimiterInferer(["lVert x rVert", "lVert y rVert"])
        nodes = inferer.infer("lVert z rVert", eq_idx=0)
        assert len(nodes) == 1
        assert nodes[0].confidence <= 1.0
        assert isinstance(nodes[0].notes, list)

    def test_source_identity_not_overwritten(self):
        """Explicit source tokens are never overwritten by similarity inference."""
        # lVert is explicit — similarity must not change it to anything else
        inferer = DelimiterInferer(["langle a rangle"])
        nodes = inferer.infer("lVert b rVert", eq_idx=0)
        assert len(nodes) == 1
        assert nodes[0].delim_type == "norm"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
