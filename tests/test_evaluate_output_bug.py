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
    from scripts.evaluate_output_reference import compare_reference_latex
except ImportError:
    from experiments_multi_paper_generalization import evaluate_output  # type: ignore[import-not-found]
    from evaluate_output_reference import compare_reference_latex  # type: ignore[import-not-found]


def test_evaluate_output_accepts_source_text():
    """evaluate_output() should accept source_text and evaluate with candidate reference."""
    result = evaluate_output(
        recognized_text=r"\left( \zeta_{v}^{(\ell+1)} \right)",
        target_tokens=['\\zeta', 'v'],
        source_text="ζ(ℓ+1)",
        candidate_id='1907_04931_cand1_expectation',
    )
    # Should complete without NameError
    assert 'semantic_agreement' in result
    assert 'structural_score' in result
    assert result['reference_match'] is True
    assert result['semantic_agreement'] is True


def test_evaluate_output_missing_reference_strictly_fails():
    """A candidate with no reference must receive semantic_agreement=False in strict mode."""
    result = evaluate_output(
        recognized_text=r"\left( \zeta_{v}^{(\ell+1)} \right)",
        target_tokens=['\\zeta', 'v'],
        source_text="ζ(ℓ+1)",
        # Missing candidate_id and cand_meta
    )
    assert result['semantic_agreement'] is False
    assert result['reference_match'] is None
    assert result['reference_status'] == 'no_reference'
    assert 'reference_missing' in result['structural_issues']


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
    """Summation should be detected as a structural operator with valid reference."""
    result = evaluate_output(
        recognized_text=r"\sum_{k=0}^{n} a_{k}",
        target_tokens=['b_{n}', r'\sum', 'a_{k}'],
        source_text="bn = ∑ S(n,k) ak",
        cand_meta={'reference_latex': r'\sum_{k=0}^{n} a_k'},
    )
    assert result['semantic_agreement'] is True
    assert result['structural_score'] >= 0
    assert r'\sum' in result['tokens_found'] or '\\sum' in result['tokens_found']


def test_escape_table_pipe_preserves_latex_backslashes():
    """escape_table_pipe must escape unescaped pipes without stripping existing backslashes."""
    import re
    def escape_table_pipe(t: str) -> str:
        return re.sub(r'(?<!\\)((\\\\)*)\|', r'\1\\|', t)

    # 1. Raw pipe -> escaped
    assert escape_table_pipe('|⟨TχI,') == r'\|⟨TχI,'
    # 2. LaTeX single backslash norm delimiter -> unchanged
    assert escape_table_pipe(r'\leq\| T \| \mu') == r'\leq\| T \| \mu'
    # 3. Double backslash before pipe -> double backslash preserved, pipe escaped
    assert escape_table_pipe(r'foo\\|bar') == r'foo\\\|bar'


def test_expected_boundary_enforcement():
    """Boundary enforcement must reject spurious delimiters after open comma."""
    # Inner product fragment with open comma: valid fragment passes
    valid_res = compare_reference_latex(
        recognized=r"\langle T \chi_{I} ,",
        reference=r"\langle T \chi_I ,",
        crop_scope='partial',
        expected_boundary={'left': 'closed', 'right': 'open_at_comma'},
    )
    assert valid_res['match'] is True

    # Inner product fragment with spurious trailing pipe delimiter fails boundary check
    invalid_res = compare_reference_latex(
        recognized=r"\langle T \chi_{I} , |",
        reference=r"\langle T \chi_I ,",
        crop_scope='partial',
        expected_boundary={'left': 'closed', 'right': 'open_at_comma'},
    )
    assert invalid_res['match'] is False
    assert invalid_res['status'] in ['boundary_violation', 'extraneous_content']



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
