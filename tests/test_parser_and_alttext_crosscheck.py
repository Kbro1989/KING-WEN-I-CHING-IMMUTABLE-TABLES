"""
Unit tests for MathMLParser improvements:
- Empty-base sub/sup/subsup grafting (LaTeXML oxide pattern)
- Lowercase max/min in BIG_OP_BASES and limit preservation in msub/munder
- Prime marks mapping (′ -> _prime, ″ -> _prime_prime)
- Transpose operator (⊤ -> _T)
- AltText cross-checker token extraction, gap detection, and verdict integration
"""

import pytest
from bs4 import BeautifulSoup
from mathml_parser import MathMLParser, BIG_OP_BASES
from alttext_cross_checker import cross_check
from math_reconstruction_evidence import validate_solution


def _parse_mathml(mathml_str: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(mathml_str, "html.parser")
    node = soup.find(["math", "mrow"]) or soup
    parser = MathMLParser()
    return parser.parse(node)


def test_oxide_empty_base_sum_grafting():
    """
    LaTeXML oxide renderer puts summation limits as sibling <msub>/<msup>
    with an empty base <mrow/>. The parser must attach them to the preceding 'Sum'.
    """
    xml = """
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <mrow>
        <mstyle displaystyle="true"><mo movablelimits="false">∑</mo></mstyle>
        <msub><mrow/><mrow><mi>ℓ</mi><mo>=</mo><mn>1</mn></mrow></msub>
        <msup><mrow/><mi>G</mi></msup>
        <mi>x</mi>
      </mrow>
    </math>
    """
    expr, unsup = _parse_mathml(xml)
    assert expr is not None
    assert "Sum_l_eq_1_G" in expr, f"Expected limits attached to Sum, got: {expr}"
    assert "*(G)" not in expr, f"Spurious multiplied exponent found: {expr}"


def test_oxide_empty_base_variable_subscript_superscript():
    """
    LaTeXML oxide renders variables like s_r^2 as:
    <mi>s</mi><msub><mrow/><mi>r</mi></msub><msup><mrow/><mn>2</mn></msup>
    The parser must produce s_r**2 instead of detached tokens.
    """
    xml = """
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <mrow>
        <mi>s</mi>
        <msub><mrow/><mi>r</mi></msub>
        <msup><mrow/><mn>2</mn></msup>
      </mrow>
    </math>
    """
    expr, unsup = _parse_mathml(xml)
    assert expr is not None
    assert "s_r" in expr, f"Expected subscript 'r' on 's', got: {expr}"
    assert "2" in expr, f"Expected exponent '2', got: {expr}"
    assert expr == "((s_r)**(2))", f"Expected exact exponent form, got: {expr}"


def test_max_min_limit_preservation():
    """
    Lowercase max and min in BIG_OP_BASES must preserve domain bounds
    like max_{beta in Delta_n} via _limit_token rather than stripping them.
    """
    assert "max" in BIG_OP_BASES
    assert "min" in BIG_OP_BASES

    xml = """
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <mrow>
        <munder>
          <mi>max</mi>
          <mrow>
            <mi>β</mi>
            <mo>∈</mo>
            <msub><mi>Δ</mi><mi>n</mi></msub>
          </mrow>
        </munder>
        <mi>f</mi>
      </mrow>
    </math>
    """
    expr, unsup = _parse_mathml(xml)
    assert expr is not None
    assert "max_beta_in_Delta_n" in expr, f"Expected bound preserved on max, got: {expr}"


def test_prime_glyphs_mapped():
    """
    Prime marks must map to _prime tokens rather than being stripped to empty strings.
    """
    xml = """
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <mrow>
        <mi>f</mi>
        <mo>′</mo>
        <mo stretchy="false">(</mo>
        <mi>x</mi>
        <mo stretchy="false">)</mo>
      </mrow>
    </math>
    """
    expr, unsup = _parse_mathml(xml)
    assert expr is not None
    assert "_prime" in expr, f"Expected _prime token in expr, got: {expr}"


def test_transpose_operator_mapped():
    """
    Transpose symbol ⊤ must map to _T token.
    """
    xml = """
    <math xmlns="http://www.w3.org/1998/Math/MathML">
      <mrow>
        <msup>
          <mi>A</mi>
          <mo>⊤</mo>
        </msup>
      </mrow>
    </math>
    """
    expr, unsup = _parse_mathml(xml)
    assert expr is not None
    assert "A_T" in expr, f"Expected A_T, got: {expr}"


def test_alttext_cross_checker_detects_missing_operator():
    """
    Alttext cross checker must flag dropped operators or symbols.
    """
    alttext = r"\max_{\beta \in \Delta} f(\beta) = 0"
    expr = "f(beta)=0"  # max and in dropped
    diff = cross_check(alttext, expr, scope="display")
    missing_names = [m["name"] for m in diff["missing_from_expr"]]
    assert "Max" in missing_names or "max" in missing_names or "in" in missing_names
    assert len(diff["gap_categories"]) > 0


def test_alttext_cross_checker_audit_numbers_in_expr():
    """
    In d = 3 - 5, expr_tokens must include numbers '3' and '5' as well as 'd'.
    """
    diff = cross_check("d=3-5", "d=3-5", scope="inline_context")
    assert "3" in diff["expr_tokens"]
    assert "5" in diff["expr_tokens"]
    assert "d" in diff["expr_tokens"]
    assert len(diff["missing_from_expr"]) == 0


def test_validate_solution_rejects_on_alttext_gap():
    """
    A solver-accepted equation that passes numeric substitution must be REJECTED
    if alttext cross-check reveals a missing recognized source token.
    """
    recovered = "x = 2"
    solution = "[2]"
    original = "x = 2"
    fake_tree = {
        "kind": "group",
        "children": [
            {"kind": "identifier", "value": "x"},
            {"kind": "relation", "value": "="},
            {"kind": "number", "value": "2"},
        ]
    }
    # Alttext has \Delta but recovered does not
    alttext_diff_with_gap = {
        "missing_from_expr": [{"kind": "greek", "latex": r"\Delta", "name": "Delta"}],
        "gap_categories": ["Greek letter"],
    }
    res = validate_solution(
        recovered, solution, original, canonical_tree=fake_tree, alttext_diff=alttext_diff_with_gap
    )
    assert res["passed"] is False, "Equation with alttext gap must not pass validation"
    assert res["failed_alttext_gap"] is True, "failed_alttext_gap flag must be set"
    assert "alttext gap" in res["detail"]


def test_large_operator_inf_vs_infty_lookahead():
    """
    Justify the 71-record drop in Large operator gaps:
    Ensure \\infty does NOT false-match \\inf as a missing infimum operator.
    """
    # 1. Expression with infinity only: must NOT flag \inf (Large operator) as missing
    diff = cross_check(r"p^{\ast} = \infty", "p_star=oo", scope="inline_context")
    bigop_missing = [m for m in diff["missing_from_expr"] if m["kind"] == "bigop"]
    assert len(bigop_missing) == 0, f"\\infty must not trigger missing \\inf: {bigop_missing}"

    # 2. Expression with genuine infimum: MUST detect if 'inf' is dropped
    diff_inf = cross_check(r"t = \inf \{ t \geq t_0 \}", "t=t_0", scope="display")
    missing_names = [m["name"] for m in diff_inf["missing_from_expr"]]
    assert "inf" in missing_names, f"Genuine dropped \\inf must be detected: {missing_names}"


def test_operator_swap_fails_stage1_and_passes_alttext():
    """
    Demonstrates the complementary two-stage separation:
    If MathML swaps + for -, AltText check (which focuses on entities/tokens)
    cannot detect sign swaps, but Stage 1 catches it immediately.
    """
    tree_sub = {
        "kind": "group",
        "children": [
            {"kind": "identifier", "value": "d"},
            {"kind": "relation", "value": "="},
            {"kind": "number", "value": "3"},
            {"kind": "operator", "value": "−"},
            {"kind": "number", "value": "5"},
        ],
    }
    source_latex = "d = 3 - 5"
    recovered = "d = 3 + 5"  # Swapped operator!
    solution = "[8]"

    alttext_diff = cross_check(source_latex, recovered, scope="inline_context")
    # Alttext sees 'd', '3', '5' in both, so it has no token gap
    assert len(alttext_diff["missing_from_expr"]) == 0

    # But validate_solution Stage 1 Catches it!
    res = validate_solution(
        recovered, solution, source_latex, canonical_tree=tree_sub, alttext_diff=alttext_diff
    )
    assert res["passed"] is False, "Operator swap must fail overall validation"
    assert res["failed_stage1"] is True, "Stage 1 must catch swapped operator"
    assert "stage1 failed" in res["detail"]


def test_occurrences_134_and_138_glyph_map_and_subscript_handling():
    """
    Occ 134: mu_hat_1 = E[theta_1 | D]
    Occ 138: sigma_hat_1^2 = Var[theta_1 | D]
    With U+2223 in GLYPH_MAP and local_dict for SymPy names, Stage 1 passes
    (the conditioning bar is recognized), avoiding false glyph mismatch.
    """
    tree_134 = {
        "kind": "group",
        "children": [
            {"kind": "identifier", "value": "mu"},
            {"kind": "relation", "value": "="},
            {"kind": "identifier", "value": "E"},
            {"kind": "relation", "value": "∣"},  # U+2223
            {"kind": "identifier", "value": "D"},
        ],
    }
    res134 = validate_solution(
        recovered="mu_hat_1=E[theta_1|D]",
        solution="[E(theta_1, D)]",
        original=r"\displaystyle\hat{\mu}_{1}=\mathbb{E}[\theta_{1}\mid D]",
        canonical_tree=tree_134,
    )
    assert res134["stage1_source_fidelity"]["passed"] is True
    assert not res134["failed_stage1"]

    tree_138 = {
        "kind": "group",
        "children": [
            {"kind": "identifier", "value": "sigma"},
            {"kind": "relation", "value": "="},
            {"kind": "identifier", "value": "Var"},
            {"kind": "relation", "value": "∣"},  # U+2223
            {"kind": "identifier", "value": "D"},
        ],
    }
    res138 = validate_solution(
        recovered="sigma_hat_1**(2)=Var[theta_1|D]",
        solution="[-sqrt(Var(theta_1, D)), sqrt(Var(theta_1, D))]",
        original=r"\displaystyle\hat{\sigma}_{1}^{2}=\mathrm{Var}[\theta_{1}\mid D]",
        canonical_tree=tree_138,
    )
    assert res138["stage1_source_fidelity"]["passed"] is True
    assert not res138["failed_stage1"]


def test_occurrence_151_trailing_punctuation_cleanup():
    """
    Occ 151: alpha=((a-mu)/(sigma))*.
    Trailing sentence-ending punctuation (*.) is cleanly stripped and verified.
    """
    res151 = validate_solution(
        recovered="alpha=((a-mu)/(sigma))*.",
        solution="[(a - mu)/sigma]",
        original=r"\alpha=\frac{a-\mu}{\sigma}.",
        canonical_tree={"kind": "group", "children": [{"kind": "identifier", "value": "alpha"}, {"kind": "relation", "value": "="}]},
    )
    assert res151["passed"] is True
    assert res151["verified_algebraic"] is True


def test_occurrence_152_multi_clause_system():
    """
    Occ 152: z=((x-mu)/(sigma)),x=mu+sigmaz,dx=sigmadz*.
    Multi-clause statement is detected as a system, split at bracket depth 0,
    and evaluated on the primary clause without SyntaxError.
    """
    res152 = validate_solution(
        recovered="z=((x-mu)/(sigma)),x=mu+sigmaz,dx=sigmadz*.",
        solution="[(-mu + x)/sigma]",
        original=r"z=\frac{x-\mu}{\sigma}, x=\mu+\sigma z, dx=\sigma dz.",
        canonical_tree={"kind": "group", "children": [{"kind": "identifier", "value": "z"}, {"kind": "relation", "value": "="}]},
    )
    assert res152["is_system"] is True
    assert res152["passed"] is True
    assert res152["verified_algebraic"] is True


def test_occurrences_155_and_156_opaque_integral_definitions():
    """
    Occ 155: Integral_alpha_oo*phi(z)d*z=1-Phi(alpha),
    Occ 156: Integral_alpha_oo*zphi(z)d*z=phi(alpha),
    Opaque operators (Integral, min, :=) are classified as definition_recorded
    and kept out of verified_algebraic.
    """
    res155 = validate_solution(
        recovered="Integral_alpha_oo*phi(z)d*z=1-Phi(alpha),",
        solution="[(1 - Phi(alpha))/(d*z*phi(z))]",
        original=r"\int_{\alpha}^{\infty}\phi(z)\,dz=1-\Phi(\alpha),",
        canonical_tree={"kind": "group", "children": [{"kind": "integral", "value": "int"}, {"kind": "relation", "value": "="}]},
    )
    assert res155["is_definition"] is True
    assert res155["definition_recorded"] is True
    assert res155["passed"] is None
    assert res155["verified_algebraic"] is False

    res156 = validate_solution(
        recovered="Integral_alpha_oo*zphi(z)d*z=phi(alpha),",
        solution="[phi(alpha)/(d*z*zphi(z))]",
        original=r"\int_{\alpha}^{\infty}z\phi(z)\,dz=\phi(\alpha),",
        canonical_tree={"kind": "group", "children": [{"kind": "integral", "value": "int"}, {"kind": "relation", "value": "="}]},
    )
    assert res156["is_definition"] is True
    assert res156["definition_recorded"] is True
    assert res156["passed"] is None
    assert res156["verified_algebraic"] is False


