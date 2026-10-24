"""
Regression tests for evaluate_output(): semantic fidelity, structural completeness,
and negative counterexample rejection.
"""
import sys
from pathlib import Path
import pytest  # type: ignore[import-not-found]

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    from scripts.experiments_multi_paper_generalization import evaluate_output
except ImportError:
    from experiments_multi_paper_generalization import evaluate_output  # type: ignore[import-not-found]


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
    assert 'semantic_agreement' in result
    assert result['semantic_agreement'] is False


def test_evaluate_output_with_summation_marker():
    """Summation should be detected as a structural operator."""
    result = evaluate_output(
        recognized_text="\\sum_{k=0}^{n} a_{k}",
        target_tokens=['b_{n}', '\\sum', 'a_{k}'],
        source_text="bn = ∑ S(n,k) ak",
    )
    assert result['semantic_agreement'] is True
    assert result['structural_score'] >= 0
    assert '\\sum' in result['tokens_found'] or '\\\\sum' in result['tokens_found']


# ===========================================================================
# Negative Regression Tests: Specific counterexamples from commit review
# ===========================================================================

def test_negative_truncated_inner_product():
    """Truncated inner product ending in pipe must be rejected for delimiter/truncation."""
    result = evaluate_output(
        recognized_text=r"\langle T \chi_{I} , \|",
        target_tokens=['T', r'\chi'],
        source_text="⟨TχI,",
        candidate_id='2104_01277_cand1_inner_product',
    )
    assert result['semantic_agreement'] is False
    assert result['delimiter_balance'] is False or result['truncation_detected'] is True


def test_negative_incomplete_absolute_inner_product():
    """Incomplete absolute inner product missing closure must fail semantic agreement."""
    result = evaluate_output(
        recognized_text=r"\| \langle T \chi_{I} , \|",
        target_tokens=['T', r'\chi'],
        source_text="|⟨TχI,",
        candidate_id='2104_01277_cand3_abs_inner_product',
    )
    assert result['semantic_agreement'] is False
    assert result['truncation_detected'] is True or 'unmatched_langle_pipe_truncation' in result['structural_issues'] or 'unmatched_langle' in result['structural_issues']


def test_negative_missing_parameter_bound():
    """Parameter set with empty bound operand (k=) must fail structural completeness."""
    result = evaluate_output(
        recognized_text=r"\{\rho_{k} \}_{k=}^{K^{\cdot}}",
        target_tokens=[r'\rho', 'k'],
        source_text="{ρk}K",
        candidate_id='2605_27315_cand0_parameter_set',
    )
    assert result['semantic_agreement'] is False
    assert result['required_structures_complete'] is False or 'empty_bound_operand' in result['structural_issues']


def test_negative_extra_derivative_operators():
    """Spurious derivative operators not present in source must be rejected."""
    result = evaluate_output(
        recognized_text=r"\mathbf{\partial}=-\dot{\sigma}(t)\,\mathbf{\partial}",
        target_tokens=[r'\sigma', 't'],
        source_text="-σ˙(t)",
        candidate_id='2206_00364_cand6_dot_derivative',
    )
    assert result['semantic_agreement'] is False
    assert 'unexpected_operator' in result['structural_issues']


def test_negative_overlined_denoiser():
    """Overlined denoiser with trailing relational operator must fail."""
    result = evaluate_output(
        recognized_text=r"\overline{{D_{\theta}(\boldsymbol{x};\sigma)}}=",
        target_tokens=['D', r'\theta', r'\mathbf{x}', r'\sigma'],
        source_text="Dθ(x;σ)",
        candidate_id='2206_00364_cand7_denoiser_function',
    )
    assert result['semantic_agreement'] is False
    assert 'trailing_operator' in result['structural_issues'] or 'unexpected_operator' in result['structural_issues']


def test_negative_altered_skip_scaling():
    """Corrupted skip scaling with spurious stackrel must fail."""
    result = evaluate_output(
        recognized_text=r"\stackrel{\iota\mathbf{j},...}",
        target_tokens=['c', r'\sigma', r'\mathbf{x}'],
        source_text="cskip(σ)x",
        candidate_id='2206_00364_cand8_skip_scaling',
    )
    assert result['semantic_agreement'] is False
    assert result['required_structures_complete'] is False or 'unexpected_operator' in result['structural_issues'] or result['token_recall'] < 0.5


def test_negative_duplicated_expression():
    """Recognized output repeating the target expression must be rejected."""
    result = evaluate_output(
        recognized_text=r"\mathbf{\sigma}_{\mathrm{d a t a}} , \mathbf{\sigma}_{\mathrm{d a t a}}",
        target_tokens=[r'\sigma'],
        source_text="σdata,",
        candidate_id='2206_00364_cand2_sigma_data',
    )
    assert result['semantic_agreement'] is False
    assert result['reference_match'] is False
    assert 'reference_duplicated' in result['structural_issues'] or 'reference_mismatch' in result['structural_issues']


def test_negative_extraneous_trailing_break():
    """Recognized output with extraneous trailing break and dots must be rejected."""
    result = evaluate_output(
        recognized_text=r"\gg\sigma_{\mathrm{d a t a}} , \break\cdot\cdot\cdot\cdot",
        target_tokens=[r'\sigma'],
        source_text="≫σdata,",
        candidate_id='2206_00364_cand4_much_greater_than',
    )
    assert result['semantic_agreement'] is False
    assert result['reference_match'] is False
    assert 'reference_extraneous_content' in result['structural_issues'] or 'reference_mismatch' in result['structural_issues']


def test_negative_extraneous_trailing_tokens():
    """Recognized output with extra tokens after valid norm term must fail."""
    result = evaluate_output(
        recognized_text=r"\lambda\| f ( x ) \|_{1} , 1",
        target_tokens=[r'\lambda', r'\|', 'f', 'x'],
        source_text="λ∥f(x)∥1,",
        candidate_id='2605_22902_cand0_l1_norm',
    )
    assert result['semantic_agreement'] is False
    assert result['reference_match'] is False
    assert 'reference_extraneous_content' in result['structural_issues'] or 'reference_mismatch' in result['structural_issues']


# ===========================================================================
# Positive Control Tests: Valid versions of counterexample expressions
# ===========================================================================

def test_positive_valid_inner_product_crop():
    """Valid partial crop of inner product should pass semantic agreement."""
    result = evaluate_output(
        recognized_text=r"\langle T \chi_{I} ,",
        target_tokens=['T', r'\chi'],
        source_text="⟨TχI,",
        candidate_id='2104_01277_cand1_inner_product',
    )
    assert result['semantic_agreement'] is True
    assert result['required_structures_complete'] is True
    assert result['delimiter_balance'] is True


def test_positive_valid_parameter_set():
    """Complete, well-formed parameter set must pass all checks."""
    result = evaluate_output(
        recognized_text=r"\{ \rho_k \}_{k=1}^{K}",
        target_tokens=[r'\rho', 'k'],
        source_text="{ρk}K",
        candidate_id='2605_27315_cand0_parameter_set',
    )
    assert result['semantic_agreement'] is True
    assert result['required_structures_complete'] is True
    assert result['delimiter_balance'] is True


def test_positive_valid_derivative():
    """Correct noise schedule derivative must pass."""
    result = evaluate_output(
        recognized_text=r"-\dot{\sigma}(t)",
        target_tokens=[r'\sigma', 't'],
        source_text="-σ˙(t)",
        candidate_id='2206_00364_cand6_dot_derivative',
    )
    assert result['semantic_agreement'] is True
    assert result['required_structures_complete'] is True


def test_positive_valid_denoiser():
    """Correct denoiser application must pass."""
    result = evaluate_output(
        recognized_text=r"D_{\theta}(\mathbf{x} ; \sigma)",
        target_tokens=['D', r'\theta', r'\mathbf{x}', r'\sigma'],
        source_text="Dθ(x;σ)",
        candidate_id='2206_00364_cand7_denoiser_function',
    )
    assert result['semantic_agreement'] is True
    assert result['required_structures_complete'] is True


def test_positive_valid_skip_scaling():
    """Correct skip scaling expression must pass."""
    result = evaluate_output(
        recognized_text=r"c_{\mathrm{skip}}(\sigma) \mathbf{x}",
        target_tokens=['c', r'\sigma', r'\mathbf{x}'],
        source_text="cskip(σ)x",
        candidate_id='2206_00364_cand8_skip_scaling',
    )
    assert result['semantic_agreement'] is True
    assert result['required_structures_complete'] is True
