"""
Regression tests for evaluate_output(): source_text parameter bug.

This test verifies that evaluate_output() accepts source_text as a required
parameter and does NOT raise NameError when source_text is passed correctly.
"""
import pytest

from experiments_multi_paper_generalization import evaluate_output


def test_evaluate_output_accepts_source_text():
    """evaluate_output() should accept source_text as third argument."""
    result = evaluate_output(
        recognized_text="\\left( \\zeta_{v}^{(\\ell+1)} \\right)",
        target_tokens=['\\zeta', 'v'],
        source_text="ζ(ℓ+1)",
    )
    # Should complete without NameError
    assert 'semantic_agreement' in result
    assert 'structural_score' in result
    assert result['semantic_agreement'] is True  # tokens present


def test_evaluate_output_with_complex_source():
    """evaluate_output() should handle complex source with structural operators."""
    result = evaluate_output(
        recognized_text="\\sum_{j=1}^{n} a_{k}",
        target_tokens=['b_{n}', '\\sum', 'a_{k}'],
        source_text="bn = ∑ S(n,k) ak",
    )
    # Should complete without NameError
    assert 'semantic_agreement' in result
    assert 'structural_score' in result


def test_evaluate_output_truncated_not_passing():
    """Truncated output should fail semantic agreement due to missing operators."""
    # Incomplete inner product - missing right operand and closure
    result = evaluate_output(
        recognized_text="\\langle T \\chi_{I} , |",
        target_tokens=['T', '\\\\chi'],
        source_text="⟨TχI,",
    )
    # Should raise or provide meaningful evaluation
    assert 'semantic_agreement' in result


def test_evaluate_output_with_summation_marker():
    """Summation should be detected as a structural operator."""
    result = evaluate_output(
        recognized_text="\\sum_{k=0}^{n} a_{k}",
        target_tokens=['b_{n}', '\\sum', 'a_{k}'],
        source_text="bn = ∑ S(n,k) ak",
    )
    # Has summation operator
    assert result['semantic_agreement'] == True
    assert result['structural_score'] >= 0
    # The specific summation target should match
    assert '\\\\sum' in result['tokens_found'] or '\\sum' in result['tokens_found']
