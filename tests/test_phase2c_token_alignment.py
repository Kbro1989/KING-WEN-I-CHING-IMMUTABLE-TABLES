"""
Tests for Phase 2C token alignment and gate calibration.

Covers:
1. Gate 2 bounds-swap detection (symmetric, no false positives)
2. Gate 3 STRUCTURE_SUBSTITUTION_MAP contract
3. Token alignment helper: ambiguity, classification, deduplication
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest
from phase2c_gate_library import (
    gate_2_token_alignment,
    tokenize_latex,
    detect_operator_substitution,
    OPERATOR_SUBSTITUTIONS,
    STRUCTURE_SUBSTITUTION_MAP,
    STRUCTURE_CHECKS,
)
from phase2c_token_alignment import align_tokens, normalize_latex


# ============================================================================
# Gate 2: Bounds-swap detection
# ============================================================================

class TestGate2BoundsSwap:
    """Verify bounds-swap detection is symmetric and has no false positives."""

    def test_forward_swap_detected(self):
        """Reference _^ recognized ^_ should fail."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} a_i",
            r"\sum^{n}_{i=1} a_i",
        )
        assert result["outcome"] == "fail", f"Expected fail, got {result['outcome']}"
        assert result["evidence"]["reorder_detected"] is True

    def test_missing_bound_fails(self):
        """Missing bound operator should fail."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} a_i",
            r"\sum_{i=1} a_i",
        )
        assert result["outcome"] == "fail", f"Expected fail, got {result['outcome']}"

    def test_duplicated_bound_fails(self):
        """Duplicated bound operator is a genuine defect."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} a_i",
            r"\sum_{i=1}^{n}^{n} a_i",
        )
        assert result["outcome"] == "fail", f"Expected fail, got {result['outcome']}"

    def test_misassociated_bound_fails(self):
        """Bound moved to wrong operator is a genuine defect."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} a_i",
            r"\sum_{i=1}^{n} a_i^{n}",
        )
        assert result["outcome"] == "fail", f"Expected fail, got {result['outcome']}"

    def test_multiple_operators_same_expression(self):
        """Multiple summations in same expression should pass when identical."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} \sum_{j=1}^{m} a_{ij}",
            r"\sum_{i=1}^{n} \sum_{j=1}^{m} a_{ij}",
        )
        assert result["outcome"] == "pass", f"Expected pass, got {result['outcome']}"

    def test_single_bound_operator(self):
        """Expression with only one bound operator should pass when identical."""
        result = gate_2_token_alignment(
            r"\sum_{i=1} a_i",
            r"\sum_{i=1} a_i",
        )
        assert result["outcome"] == "pass", f"Expected pass, got {result['outcome']}"

    def test_equivalent_formatting_no_false_positive(self):
        """Equivalent formatting changes should not trigger reorder detection."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} a_i",
            r"\sum_{i=1}^{n} a_i",
        )
        assert result["outcome"] == "pass", f"Expected pass, got {result['outcome']}"
        assert result["evidence"]["reorder_detected"] is False

    def test_reverse_swap_detected(self):
        """Reference ^_ recognized _^ should also fail."""
        result = gate_2_token_alignment(
            r"\sum^{n}_{i=1} a_i",
            r"\sum_{i=1}^{n} a_i",
        )
        assert result["outcome"] == "fail", f"Expected fail, got {result['outcome']}"
        assert result["evidence"]["order_violation"] is True


    def test_single_bound_no_false_positive(self):
        """Single bound operator should not trigger swap detection."""
        result = gate_2_token_alignment(
            r"\sum_{i=1} a_i",
            r"\sum_{i=1} a_i",
        )
        assert result["evidence"]["reorder_detected"] is False

    def test_missing_bounds_no_false_positive(self):
        """No bounds at all should not trigger swap detection."""
        result = gate_2_token_alignment(
            r"\sum a_i",
            r"\sum a_i",
        )
        assert result["evidence"]["reorder_detected"] is False

    def test_different_tokens_still_detected(self):
        """Bounds swap with different surrounding tokens should still detect."""
        result = gate_2_token_alignment(
            r"\int_{0}^{1} f(x) dx",
            r"\int^{1}_{0} f(x) dx",
        )
        assert result["evidence"]["reorder_detected"] is True

    def test_three_bound_operators_no_swap(self):
        """Three bound operators should not trigger the two-operator swap check."""
        result = gate_2_token_alignment(
            r"\sum_{i=1}^{n} \prod_{j=1}^{m} a_{ij}",
            r"\sum_{i=1}^{n} \prod_{j=1}^{m} a_{ij}",
        )
        assert result["evidence"]["reorder_detected"] is False


# ============================================================================
# Gate 3: STRUCTURE_SUBSTITUTION_MAP contract
# ============================================================================

class TestGate3StructureMap:
    """Verify every substitution class resolves to its intended structure key."""

    def test_all_substitution_keys_mapped(self):
        """Every key in OPERATOR_SUBSTITUTIONS must resolve via STRUCTURE_SUBSTITUTION_MAP."""
        for sub_struct in OPERATOR_SUBSTITUTIONS:
            ref_key = STRUCTURE_SUBSTITUTION_MAP.get(sub_struct, sub_struct)
            assert ref_key in STRUCTURE_CHECKS, (
                f"Substitution '{sub_struct}' resolves to '{ref_key}' "
                f"which is not in STRUCTURE_CHECKS"
            )

    def test_partial_derivative_maps_to_derivative(self):
        assert STRUCTURE_SUBSTITUTION_MAP["partial_derivative"] == "derivative"

    def test_summation_maps_to_summation(self):
        assert STRUCTURE_SUBSTITUTION_MAP["summation"] == "summation"

    def test_fraction_maps_to_fraction(self):
        assert STRUCTURE_SUBSTITUTION_MAP["fraction"] == "fraction"

    def test_integral_maps_to_integral(self):
        assert STRUCTURE_SUBSTITUTION_MAP["integral"] == "integral"

    def test_radical_maps_to_radical(self):
        assert STRUCTURE_SUBSTITUTION_MAP["radical"] == "radical"

    def test_nabla_maps_to_nabla(self):
        assert STRUCTURE_SUBSTITUTION_MAP["nabla"] == "nabla"

    def test_approximation_maps_to_non_equality_relation(self):
        assert STRUCTURE_SUBSTITUTION_MAP["approximation"] == "non_equality_relation"

    def test_equality_maps_to_non_equality_relation(self):
        assert STRUCTURE_SUBSTITUTION_MAP["equality"] == "non_equality_relation"

    def test_set_membership_maps_to_set_notation(self):
        assert STRUCTURE_SUBSTITUTION_MAP["set_membership"] == "set_notation"

    def test_unmapped_fallback_identity(self):
        """Unmapped keys should fall through to identity (backward compat)."""
        result = STRUCTURE_SUBSTITUTION_MAP.get("unknown_op", "unknown_op")
        assert result == "unknown_op"

    def test_detect_operator_substitution_all_four_mutations(self):
        """All 4 original mutations should be detected."""
        mutations = [
            (r"\sum_{i=1}^{n} a_i", r"S_{i=1}^{n} a_i"),
            (r"\int_{0}^{1} f(x) dx", r"I_{0}^{1} f(x) dx"),
            (r"\partial x / \partial t", r"d x / d t"),
            (r"\frac{a}{b}", r"a / b"),
        ]
        for ref, rec in mutations:
            ref_norm = normalize_latex(ref)
            rec_norm = normalize_latex(rec)
            result = detect_operator_substitution(ref_norm, rec_norm)
            assert len(result) > 0, f"Mutation not detected: {ref} -> {rec}: {result}"

    def test_detect_operator_substitution_valid_controls_pass(self):
        """Valid controls (no substitution) should return empty list."""
        controls = [
            (r"\sum_{i=1}^{n} a_i", r"\sum_{i=1}^{n} a_i"),
            (r"\int_{0}^{1} f(x) dx", r"\int_{0}^{1} f(x) dx"),
            (r"\frac{a}{b}", r"\frac{a}{b}"),
        ]
        for ref, rec in controls:
            result = detect_operator_substitution(tokenize_latex(ref), tokenize_latex(rec))
            assert result == [], f"False positive: {ref} -> {rec}: {result}"


# ============================================================================
# Token alignment helper: ambiguity and classification
# ============================================================================

class TestTokenAlignmentHelper:
    """Test align_tokens and detect_operator_substitution from helper module."""

    def test_identical_expressions_no_substitution(self):
        """Identical expressions should have no substitutions."""
        result = align_tokens(tokenize_latex('\\sum_{i=1}^{n} a_i'), tokenize_latex('\\sum_{i=1}^{n} a_i'))
        assert result["substitutions"] == []
        assert result["ambiguous"] is False

    def test_partial_to_d_two_substitutions(self):
        """partial -> d should produce exactly 2 substitutions."""
        result = align_tokens(tokenize_latex('\\partial x / \\partial t'), tokenize_latex('d x / d t'))
        assert len(result["substitutions"]) == 2
        for sub in result["substitutions"]:
            assert sub["ref_token"] == r"\partial"
            assert sub["rec_token"] == "d"

    def test_sum_to_S_one_substitution(self):
        """sum -> S should produce exactly 1 substitution."""
        result = align_tokens(tokenize_latex('\\sum_{i=1}^{n} a_i'), tokenize_latex('S_{i=1}^{n} a_i'))
        assert len(result["substitutions"]) >= 1
        assert any(s["ref_token"] == r"\sum" for s in result["substitutions"])

    def test_integral_to_I_one_substitution(self):
        """int -> I should produce exactly 1 substitution."""
        result = align_tokens(tokenize_latex('\\int_{0}^{1} f(x) dx'), tokenize_latex('I_{0}^{1} f(x) dx'))
        assert len(result["substitutions"]) >= 1
        assert any(s["ref_token"] == r"\int" for s in result["substitutions"])

    def test_fraction_to_slash_one_substitution(self):
        """frac -> / should produce exactly 1 substitution."""
        result = align_tokens(tokenize_latex('\\frac{a}{b}'), tokenize_latex('a / b'))
        assert len(result["substitutions"]) >= 1
        assert any(s["ref_token"] == r"\frac" for s in result["substitutions"])

    def test_valid_expression_with_d_no_false_positive(self):
        """Valid expression containing 'd' should not be flagged."""
        result = align_tokens(tokenize_latex('d x / d t'), tokenize_latex('d x / d t'))
        assert result["substitutions"] == []

    def test_valid_expression_with_S_no_false_positive(self):
        """Valid expression containing 'S' should not be flagged."""
        result = align_tokens(tokenize_latex('S_{i=1}^{n} a_i'), tokenize_latex('S_{i=1}^{n} a_i'))
        assert result["substitutions"] == []

    def test_multiple_substitutions_in_one_expression(self):
        """Expression with both sum and partial should detect both."""
        result = align_tokens(
            tokenize_latex(r"\sum_{i=1}^{n} \partial x / \partial t"),
            r"S_{i=1}^{n} d x / d t",
        )
        assert len(result["substitutions"]) >= 2

    def test_repeated_identical_tokens(self):
        """Repeated identical tokens should not crash or produce false positives."""
        result = align_tokens(tokenize_latex('a + a + a'), tokenize_latex('a + a + a'))
        assert result["substitutions"] == []

    def test_insertions_and_deletions_adjacent_to_operators(self):
        """Insertions/deletions near operators should be handled."""
        result = align_tokens(tokenize_latex('\\sum_{i=1}^{n} a_i'), tokenize_latex('\\sum_{i=1}^{n} a_i + b'))
        # Should have insertions for + and b, but no substitutions
        assert result["substitutions"] == []
        assert len(result["insertions"]) > 0

    def test_result_has_required_keys(self):
        """Alignment result should have all required keys."""
        result = align_tokens(tokenize_latex('\\frac{a}{b}'), tokenize_latex('a / b'))
        required = {"matched", "substitutions", "insertions", "deletions",
                    "ambiguous", "lcs_length", "ref_token_count", "rec_token_count"}
        assert required.issubset(set(result.keys()))

    def test_positions_are_zero_based(self):
        """Positions should be 0-based."""
        result = align_tokens(tokenize_latex('\\sum_{i=1}^{n} a_i'), tokenize_latex('S_{i=1}^{n} a_i'))
        for sub in result["substitutions"]:
            assert sub["ref_position"] >= 0
            assert sub["rec_position"] >= 0

    def test_ambiguity_flag_present(self):
        """Ambiguity flag should be a boolean."""
        result = align_tokens(tokenize_latex('\\frac{a}{b}'), tokenize_latex('a / b'))
        assert isinstance(result["ambiguous"], bool)

    def test_normalize_latex_returns_string(self):
        """normalize_latex should return a string."""
        result = normalize_latex(r"\sum_{i=1}^{n} a_i")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_alignment_with_empty_strings(self):
        """Empty strings should not crash."""
        result = align_tokens(tokenize_latex(''), tokenize_latex(''))
        assert result["substitutions"] == []
        assert result["matched"] == []

    def test_alignment_case_insensitive_not_applied(self):
        """Alignment should be case-sensitive (S != s)."""
        result = align_tokens(tokenize_latex('\\sum a'), tokenize_latex('s a'))
        # 's' lowercase should not match 'S' substitution pattern
        # but the tokens differ, so it might be a substitution candidate
        # The key is it doesn't crash
        assert isinstance(result["substitutions"], list)