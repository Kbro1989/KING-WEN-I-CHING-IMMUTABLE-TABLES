#!/usr/bin/env python3
"""
Unit tests for Chroma Visual Reader and 2D Math Translator.
===========================================================
Validates:
- 2D fraction vinculum detection and numerator/denominator association
- Multi-row piecewise cases brace detection and row branching
- Structural AST translation to ExprNode
- Discrepancy auditing catching skipped division and collapsed cases
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chroma_visual_reader import (
    VisualRegion,
    VisualMathStructure,
    detect_2d_structures,
)
from visual_math_translator import (
    VisualMathTranslator,
    DiscrepancyReport,
)
from math_contract import ExprNode


def test_fraction_vinculum_detection_and_association():
    """A horizontal fraction bar should associate with regions above and below it."""
    # Bar at y=100, h=3, w=60 (aspect ratio 20.0)
    bar = VisualRegion(
        region_id=0,
        bbox=(50.0, 100.0, 60.0, 3.0),
        centroid=(80.0, 101.5),
        aspect_ratio=20.0,
        fill_ratio=0.8,
        normalized_stroke=0.05,
        region_type="fraction_bar",
        is_math=True,
    )
    # Numerator at y=80, h=15, w=25 (above bar)
    num = VisualRegion(
        region_id=1,
        bbox=(65.0, 80.0, 25.0, 15.0),
        centroid=(77.5, 87.5),
        aspect_ratio=1.67,
        fill_ratio=0.4,
        normalized_stroke=0.1,
        region_type="symbol",
        is_math=True,
        text="sin_z",
    )
    # Denominator at y=110, h=15, w=15 (below bar)
    den = VisualRegion(
        region_id=2,
        bbox=(70.0, 110.0, 15.0, 15.0),
        centroid=(77.5, 117.5),
        aspect_ratio=1.0,
        fill_ratio=0.4,
        normalized_stroke=0.1,
        region_type="symbol",
        is_math=True,
        text="z",
    )

    regions = [bar, num, den]
    structures = detect_2d_structures(regions)

    assert len(structures) == 1
    s = structures[0]
    assert s.structure_type == "fraction"
    assert s.main_region_id == 0
    assert s.components["numerator"] == [1]
    assert s.components["denominator"] == [2]
    assert s.confidence == 1.0


def test_piecewise_cases_brace_detection():
    """A tall curly brace should associate with multi-row branches to its right."""
    # Cases brace at x=50, y=100, w=12, h=80 (tall aspect ratio < 0.25)
    brace = VisualRegion(
        region_id=0,
        bbox=(50.0, 100.0, 12.0, 80.0),
        centroid=(56.0, 140.0),
        aspect_ratio=0.15,
        fill_ratio=0.3,
        normalized_stroke=0.03,
        region_type="cases_brace",
        is_math=True,
    )
    # Row 1 branch at y=115, x=75
    r1 = VisualRegion(
        region_id=1,
        bbox=(75.0, 110.0, 40.0, 15.0),
        centroid=(95.0, 117.5),
        aspect_ratio=2.6,
        fill_ratio=0.4,
        normalized_stroke=0.05,
        region_type="symbol",
        is_math=True,
        text="1_if_z_eq_0",
    )
    # Row 2 branch at y=155, x=75
    r2 = VisualRegion(
        region_id=2,
        bbox=(75.0, 150.0, 50.0, 15.0),
        centroid=(100.0, 157.5),
        aspect_ratio=3.3,
        fill_ratio=0.4,
        normalized_stroke=0.05,
        region_type="symbol",
        is_math=True,
        text="sin_z_over_z",
    )

    regions = [brace, r1, r2]
    structures = detect_2d_structures(regions)

    assert len(structures) == 1
    s = structures[0]
    assert s.structure_type == "cases"
    assert s.main_region_id == 0
    assert "row_0" in s.components
    assert "row_1" in s.components
    assert s.components["row_0"] == [1]
    assert s.components["row_1"] == [2]


def test_translator_emits_typed_fraction_ast():
    """VisualMathTranslator should produce an ExprNode of kind 'fraction'."""
    struct = VisualMathStructure(
        structure_type="fraction",
        main_region_id=0,
        bbox=(50.0, 80.0, 60.0, 45.0),
        components={"numerator": [1], "denominator": [2]},
    )
    reg_map = {
        1: VisualRegion(1, (65.0, 80.0, 25.0, 15.0), (77.5, 87.5), 1.6, 0.4, 0.1, "symbol", True, text="cos_z"),
        2: VisualRegion(2, (70.0, 110.0, 15.0, 15.0), (77.5, 117.5), 1.0, 0.4, 0.1, "symbol", True, text="z"),
    }

    ast = VisualMathTranslator.translate_fraction(struct, reg_map)
    assert ast.kind == "fraction"
    assert len(ast.children) == 2
    assert ast.children[0].value == "cos_z"
    assert ast.children[1].value == "z"


def test_translator_emits_typed_cases_ast():
    """VisualMathTranslator should produce an ExprNode of kind 'cases' with row branches."""
    struct = VisualMathStructure(
        structure_type="cases",
        main_region_id=0,
        bbox=(50.0, 100.0, 100.0, 80.0),
        components={"row_0": [1], "row_1": [2]},
    )
    reg_map = {
        1: VisualRegion(1, (75.0, 110.0, 40.0, 15.0), (95.0, 117.5), 2.6, 0.4, 0.05, "symbol", True, text="branch1"),
        2: VisualRegion(2, (75.0, 150.0, 50.0, 15.0), (100.0, 157.5), 3.3, 0.4, 0.05, "symbol", True, text="branch2"),
    }

    ast = VisualMathTranslator.translate_cases(struct, reg_map)
    assert ast.kind == "cases"
    assert len(ast.children) == 2


def test_audit_catches_skipped_division():
    """Discrepancy audit flags when visual fraction vinculum is read as 1D multiplication."""
    struct = VisualMathStructure(
        structure_type="fraction",
        main_region_id=0,
        bbox=(10.0, 20.0, 40.0, 30.0),
        components={"numerator": [1], "denominator": [2]},
    )
    # 1D reader parsed "a b" without any division symbol
    report = VisualMathTranslator.audit_discrepancy_with_text(struct, "a b")
    assert report.issue_kind == "skipped_division"
    assert report.detected_in_visual is True
    assert report.detected_in_text is False


def test_audit_passes_consistent_fraction():
    """Discrepancy audit confirms consistency when 1D text contains division."""
    struct = VisualMathStructure(
        structure_type="fraction",
        main_region_id=0,
        bbox=(10.0, 20.0, 40.0, 30.0),
        components={"numerator": [1], "denominator": [2]},
    )
    report = VisualMathTranslator.audit_discrepancy_with_text(struct, r"\frac{a}{b}")
    assert report.issue_kind == "consistent"
    assert report.detected_in_text is True


def test_audit_catches_collapsed_cases():
    """Discrepancy audit flags when visual piecewise cases is flattened to plain text."""
    struct = VisualMathStructure(
        structure_type="cases",
        main_region_id=0,
        bbox=(10.0, 20.0, 40.0, 80.0),
        components={"row_0": [1], "row_1": [2]},
    )
    report = VisualMathTranslator.audit_discrepancy_with_text(struct, "f(x) = 1 for x=0, 2 for x>0")
    assert report.issue_kind == "collapsed_cases"
    assert report.detected_in_visual is True
    assert report.detected_in_text is False
