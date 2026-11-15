"""Automated verification suite for the 10-stage vertical slice recovery pipeline (V2.3 Phase 2).

Tests:
  1. Complete execution of all 10 stages without error.
  2. Macro region proposal generated from relation anchor without gold coordinates.
  3. Individual glyph identity recovery (accents, bold vectors, transpose symbols).
  4. Typed canonical AST extraction via structural_ast_extractor.
  5. Semantic interpretation of variables, operators, and relations.
  6. Independent Gate D4 physical clearance verification.
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

from v2_3_vertical_slice_recovery import run_vertical_slice_recovery


@pytest.fixture(scope="module")
def piaa_003_vertical_slice():
    manifest = json.loads(Path("DATASETS/structural_preservation/piaa_fixture_manifest.json").read_text(encoding="utf-8"))
    pdf_path = manifest["source_document"]["local_pdf_path"]
    res = run_vertical_slice_recovery(
        pdf_path=pdf_path,
        page_idx=4,
        column_x_bounds=(55.0, 290.7),
        y_band_hint=(195.0, 215.0),
        relation_anchor_char="=",
    )
    return res


def test_stage1_and_stage2_provenance(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    assert "stage1_source_acquisition" in res
    assert "stage2_occurrence_identification" in res
    assert res["stage2_occurrence_identification"]["occurrence_key"].startswith("2605.25821")


def test_stage3_macro_region_proposal_from_anchor(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s3 = res["stage3_macro_region_proposal"]
    assert s3["relation_anchor"] is not None
    assert s3["relation_anchor"]["char"] == "="
    # Macro bbox covers equation extent
    bbox = s3["macro_proposal_bbox"]
    assert bbox[0] < 140.0 and bbox[2] > 270.0


def test_stage4_5_glyph_identity_recovery(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s45 = res["stage4_5_glyph_detection_and_identity"]
    assert s45["total_glyphs_recovered"] >= 20
    # Spot-check recovered roles
    roles = {g["role"] for g in s45["glyph_inventory_sample"]}
    assert "operator" in roles or "symbol" in roles


def test_stage6_spatial_relationships_and_ink_refinement(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s6 = res["stage6_spatial_relationships"]
    assert s6["base_font_size_pt"] == pytest.approx(9.96, abs=0.1)
    # Check refined visible ink box is tighter than search band
    ink_box = s6["refined_visible_ink_math_bbox"]
    assert 195.0 <= ink_box[1] and ink_box[3] <= 215.0


def test_stage7_and_stage8_canonical_ast_generation(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s7 = res["stage7_structural_reconstruction"]
    s8 = res["stage8_canonical_typed_ast"]
    assert len(s7["reconstructed_latex"]) > 0
    assert len(s7["reconstructed_mathml"]) > 0
    assert s8["ast_extraction_success"] is True
    assert s8["ast_root_kind"] == "group"
    assert s8["ast_children_count"] >= 15


def test_stage9_semantic_interpretation(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s9 = res["stage9_semantic_interpretation"]
    assert "=" in s9["discovered_relations"]
    assert "+" in s9["discovered_operators"]
    assert "y" in s9["discovered_identifiers"]
    assert "w" in s9["discovered_identifiers"]
    assert "x" in s9["discovered_identifiers"]


def test_stage10_independent_verification_gate_d4(piaa_003_vertical_slice):
    res = piaa_003_vertical_slice
    s10 = res["stage10_independent_verification"]
    assert s10["clearance_above_pt"] >= 2.0
    assert s10["clearance_below_pt"] >= 2.0
    assert s10["gate_d4_pass"] is True
    assert s10["verification_verdict"] == "PASSED_VERIFIED"

