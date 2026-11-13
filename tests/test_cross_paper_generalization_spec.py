#!/usr/bin/env python3
"""Test Suite: Cross-Paper Delimiter Generalization Specification v1.

Verifies:
  1. Spec schema completeness across all 7 test families.
  2. Strict conjunctive 5-axis acceptance policy (missing/failing dimension -> NOT_VERIFIED or FAILED).
  3. Immutable engine baseline hash alignment with disk repository state.
  4. Structural layout convention: 7x6 layout with 40 recovered tokens vs 42 populated cells.
  5. Case record schema validator behavior under positive and adversarial inputs.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_cross_paper_generalization_spec import (
    validate_spec,
    validate_case_record,
    SPEC_PATH,
    ENGINE_PATH,
    sha256_file,
    REQUIRED_FAMILIES,
    REQUIRED_DIMENSIONS,
    REQUIRED_NEGATIVE_CONTROLS,
)


@pytest.fixture(scope="module")
def spec_json():
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_spec_schema_and_seven_families(spec_json):
    """Test 1: Verify all 7 mandatory test families are present with complete fields."""
    res = validate_spec(SPEC_PATH)
    assert res["valid"] is True, f"Spec validation failed: {res['errors']}"
    assert res["families_count"] == 7
    assert res["dimensions_count"] == 5

    families = {fam["family_id"]: fam for fam in spec_json["test_families"]}
    for fam_id in REQUIRED_FAMILIES:
        assert fam_id in families
        fam = families[fam_id]
        assert len(fam["required_evidence"]) > 10
        assert len(fam["primary_failure_mode"]) > 5
        assert len(fam["mandatory_guards"]) >= 2


def test_conjunctive_five_axis_rule_and_not_verified_rejection(spec_json):
    """Test 2: Ensure strict conjunctive 5-axis policy rejects non-conjunctive passes."""
    acc_dims = spec_json["acceptance_dimensions"]
    assert acc_dims["evaluation_policy"] == "CONJUNCTIVE_STRICT_FIVE_AXIS"
    dims = acc_dims["dimensions"]
    for d in REQUIRED_DIMENSIONS:
        assert d in dims
        assert "failure_verdict" in dims[d]

    # Adversarial Case A: 4 PASS, 1 FAIL, but marked PASSED_CERTIFIED -> Validator MUST reject
    adversarial_case_fail = {
        "case_id": "MOCK-001",
        "test_family_id": "FAM_001_DELIMITER_IDENTITY",
        "source_document": {"paper_id": "test", "pdf_rel_path": "test.pdf", "pdf_sha256": "0"*64, "page_1based": 1, "math_font_family": "STIX"},
        "gold_reference": {},
        "experimental_controls": {"gold_annotation_sha256": "0"*64, "engine_sha256": "0"*64, "candidate_hash": "0"*64, "reconstruction_hash": "0"*64, "exact_test_command": "pytest", "test_exit_code": 0},
        "five_dimension_results": {
            "dim_1_geometric_localization": {"status": "PASS"},
            "dim_2_glyph_completeness": {"status": "PASS"},
            "dim_3_structural_recovery": {"status": "PASS"},
            "dim_4_semantic_fidelity": {"status": "FAIL"},  # Failing dimension!
            "dim_5_boundary_isolation": {"status": "PASS"},
        },
        "negative_control_results": {nc: {"status": "PASS"} for nc in REQUIRED_NEGATIVE_CONTROLS},
        "certification_status": "PASSED_CERTIFIED",  # Illegitimate pass!
    }
    errors_fail = validate_case_record(adversarial_case_fail, spec_json)
    assert any("Violation of CONJUNCTIVE_STRICT_FIVE_AXIS" in e for e in errors_fail)

    # Adversarial Case B: Missing measurement -> NOT_VERIFIED, cannot be PASSED_CERTIFIED
    adversarial_case_unverified = dict(adversarial_case_fail)
    adversarial_case_unverified["five_dimension_results"] = {
        "dim_1_geometric_localization": {"status": "PASS"},
        "dim_2_glyph_completeness": {"status": "PASS"},
        "dim_3_structural_recovery": {"status": "PASS"},
        "dim_4_semantic_fidelity": {"status": "NOT_VERIFIED"},  # Missing evidence!
        "dim_5_boundary_isolation": {"status": "PASS"},
    }
    errors_unverified = validate_case_record(adversarial_case_unverified, spec_json)
    assert any("Violation of CONJUNCTIVE_STRICT_FIVE_AXIS" in e for e in errors_unverified)


def test_immutable_engine_hash_matches_disk(spec_json):
    """Test 3: Verify spec immutable engine baseline matches repository disk state."""
    engine_sha_disk = sha256_file(ENGINE_PATH)
    spec_engine_sha = spec_json["immutable_engine_baseline"]["engine_sha256"]
    assert engine_sha_disk == spec_engine_sha
    assert engine_sha_disk.startswith("8211592af549c292")


def test_structural_layout_40_token_convention(spec_json):
    """Test 4: Verify the 7x6 layout with 40 recovered tokens convention is codified."""
    layout_note = spec_json["benchmark_architecture"]["structural_layout_convention_note"]
    assert "7x6" in layout_note
    assert "40 recovered tokens" in layout_note
    assert "42 populated cells" in layout_note


def test_case_record_validator_accepts_valid_certified_case(spec_json):
    """Test 5: Valid case record with all 5 passing dimensions passes validation cleanly."""
    valid_case = {
        "case_id": "VALID-001",
        "test_family_id": "FAM_001_DELIMITER_IDENTITY",
        "source_document": {"paper_id": "test", "pdf_rel_path": "test.pdf", "pdf_sha256": "0"*64, "page_1based": 1, "math_font_family": "STIX"},
        "gold_reference": {},
        "experimental_controls": {"gold_annotation_sha256": "0"*64, "engine_sha256": "0"*64, "candidate_hash": "0"*64, "reconstruction_hash": "0"*64, "exact_test_command": "pytest", "test_exit_code": 0},
        "five_dimension_results": {
            "dim_1_geometric_localization": {"status": "PASS"},
            "dim_2_glyph_completeness": {"status": "PASS"},
            "dim_3_structural_recovery": {"status": "PASS"},
            "dim_4_semantic_fidelity": {"status": "PASS"},
            "dim_5_boundary_isolation": {"status": "PASS"},
        },
        "negative_control_results": {nc: {"status": "PASS"} for nc in REQUIRED_NEGATIVE_CONTROLS},
        "certification_status": "PASSED_CERTIFIED",
    }
    errors = validate_case_record(valid_case, spec_json)
    assert len(errors) == 0, f"Valid case record produced unexpected errors: {errors}"

