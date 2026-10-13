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
