"""Unit & Integration Tests for Multimodal Mathematical PDF Recovery Engine (V2.3).

Verifies multi-layer mathematical recovery across:
  - arXiv:2605.25821 (PIAA) fixtures (PIAA-001 to PIAA-008)
  - Delimiters (tall vs short, extensible parens, determinant bars)
  - Symbols/glyphs (bold vectors, bold Greek, math italics, blackboard bold, accents, transpose)
  - Mathematical formats (display math, clustered math with quad separation, inline math in prose)
  - Vector path geometry (fraction bars, radical vinculums)
  - Canonical AST extraction (structural_ast_extractor)
  - Gate D4 physical clearance verification and anti-override guarantee
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from v2_3_multimodal_math_recovery import MultimodalMathRecoveryEngine


PDF_PATH = Path(
    r"C:\Users\krist\Desktop\zotero\learning-corpus\efficient-inference-quantization"
    r"\2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via Patch-Level Inference and Adapt.pdf"
)


@pytest.fixture(scope="module")
def engine():
    return MultimodalMathRecoveryEngine(zoom=20, ink_threshold=128)


def test_pdf_existence():
    """Verify that the primary PIAA specimen PDF exists and has expected size."""
    assert PDF_PATH.exists(), f"Specimen PDF not found at {PDF_PATH}"
    assert PDF_PATH.stat().st_size == 1901586


def test_vector_drawings_extraction(engine):
    """Verify extraction of horizontal vector rules (fraction bars, vinculums)."""
    import pymupdf
    doc = pymupdf.open(str(PDF_PATH))
    # Page 4 (0-based page 3) has Eq 1 fraction rules
    rules_p4 = engine.extract_page_vector_drawings(doc[3])
    assert len(rules_p4) >= 3
    # Check that fraction rules and square root vinculum are detected
    rule_widths = [r["width"] for r in rules_p4]
    assert any(w > 30.0 for w in rule_widths), "Long fraction/vinculum rule should be detected"


def test_piaa_001_multiline_tall_delimiters_and_gate_d4(engine):
    """
    PIAA-001 (Eq 1):
      - Extensible parentheses \x12 / \x13
      - Determinant bars |
      - Radical CMEX10 'p'
      - Gate D4 MUST fail (1.8 pt upper gutter < 2.0 pt required)
      - Anti-override: final_verdict MUST be NOT_VERIFIED despite valid AST
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=3,
        bbox_clip=[313.4, 580.0, 535.5, 620.5],
        column_x_bounds=(307.1, 542.1),
        equation_hint_id="PIAA-001",
    )
    assert res["status"] == "RECOVERED"
    assert res["canonical_ast"]["success"] is True
    # Gate D4 MUST fail due to 1.8 pt gutter
    gate_d4 = res["gate_d4_verification"]
    assert gate_d4["gate_d4_passed"] is False
    assert "sub_2pt_clearance_failure" in gate_d4["failure_reason"]
    # Final verdict MUST be NOT_VERIFIED (no override allowed)
    assert res["final_verdict"].startswith("NOT_VERIFIED")


def test_piaa_002_proportional_and_greek_prior(engine):
    r"""
    PIAA-002 (Eq 2):
      - Proportional to relation \propto
      - Greek prior \pi_c
      - Gaussian distribution \mathcal{N}
      - Gate D4 passes
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_clip=[102.93, 100.44, 278.0, 112.31],
        column_x_bounds=(55.0, 290.7),
        equation_hint_id="PIAA-002",
    )
    assert res["status"] == "RECOVERED"
    assert res["canonical_ast"]["success"] is True
    assert res["gate_d4_verification"]["gate_d4_passed"] is True
    assert res["final_verdict"] == "PASSED_VERIFIED"
    assert r"\propto" in res["reconstructed_latex"]
    assert r"\pi" in res["reconstructed_latex"] or "π" in res["reconstructed_latex"]


def test_piaa_003_linear_discriminant_tilde_and_transpose(engine):
    """
    PIAA-003 (Eq 3):
      - Tilde accent \tilde{y}
      - Transpose operator ^\top
      - Bold vector w_c, x_i
      - Gate D4 passes
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_clip=[134.83, 197.23, 278.0, 211.52],
        column_x_bounds=(55.0, 290.7),
        equation_hint_id="PIAA-003",
    )
    assert res["status"] == "RECOVERED"
    assert res["canonical_ast"]["success"] is True
    assert res["gate_d4_verification"]["gate_d4_passed"] is True
    assert res["final_verdict"] == "PASSED_VERIFIED"
    assert r"\tilde" in res["reconstructed_latex"]
    assert r"\mathbf" in res["reconstructed_latex"]


def test_piaa_004_clustered_quad_expressions(engine):
    r"""
    PIAA-004 (Eq 4):
      - Two distinct equations on one line separated by quad spacing (\qquad)
      - Inv matrix \Sigma^{-1}
      - Fraction -1/2
      - Gate D4 passes
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_clip=[90.73, 247.42, 278.0, 270.96],
        column_x_bounds=(55.0, 290.7),
        equation_hint_id="PIAA-004",
    )
    assert res["status"] == "RECOVERED"
    assert res["cluster_count"] >= 2, "Should partition line into clustered quad expressions"
    assert r"\qquad" in res["reconstructed_latex"]
    assert res["gate_d4_verification"]["gate_d4_passed"] is True
    assert res["final_verdict"] == "PASSED_VERIFIED"


def test_piaa_005_summation_operator(engine):
    r"""
    PIAA-005 (Eq 5):
      - Large summation operator \sum
      - Entropy expression H(x_i)
      - Gate D4 passes
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=4,
        bbox_clip=[116.23, 456.28, 278.0, 487.34],
        column_x_bounds=(55.0, 290.7),
        equation_hint_id="PIAA-005",
    )
    assert res["status"] == "RECOVERED"
    assert res["canonical_ast"]["success"] is True
    assert res["gate_d4_verification"]["gate_d4_passed"] is True
    assert res["final_verdict"] == "PASSED_VERIFIED"
    assert r"\sum" in res["reconstructed_latex"]


def test_piaa_006_inline_prose_math(engine):
    r"""
    PIAA-006 (Sec 3.1):
      - Inline math in text paragraph: \mathbf{z}_{\mathrm{cls}} \in \mathbb{R}^d
      - Set membership \in
      - Blackboard bold \mathbb{R}
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=2, # Page 3
        bbox_clip=[407.1, 354.8, 447.7, 368.3],
        column_x_bounds=(307.1, 542.1),
        equation_hint_id="PIAA-006_inline1",
    )
    assert res["status"] == "RECOVERED"
    assert res["canonical_ast"]["success"] is True
    assert r"\in" in res["reconstructed_latex"]
    assert r"\mathbb{R}" in res["reconstructed_latex"]


def test_piaa_008_metric_and_complexity(engine):
    """
    PIAA-008 (Sec 4.4):
      - Complexity notation (O(C))
      - Speedup notation 362.1x
    """
    res = engine.recover_equation_region(
        pdf_path=PDF_PATH,
        page_idx=8, # Page 9
        bbox_clip=[180.2, 635.4, 213.3, 645.8],
        column_x_bounds=(55.0, 290.7),
        equation_hint_id="PIAA-008_complexity",
    )
    assert res["status"] == "RECOVERED"
    assert "O" in res["reconstructed_latex"]
    assert "C" in res["reconstructed_latex"]


def test_gate_d4_anti_override_invariant(engine):
    """
    Verify that Gate D4 physical failure can NEVER be overridden by AST success or confidence.
    """
    import pymupdf
    doc = pymupdf.open(str(PDF_PATH))
    # Test on PIAA-001 where upper clearance is 1.8 pt < 2.0 pt
    page = doc[3]
    math_bbox = [313.4, 580.0, 535.5, 620.5]
    gate_d4 = engine.verify_gate_d4_clearance(page, math_bbox, required_clearance_pt=2.0)
    assert gate_d4["gate_d4_passed"] is False
    # Below clearance is violated by equation number (1) (0.24 pt < 2.0 pt)
    assert gate_d4["clearance_below_pt"] < 2.0
