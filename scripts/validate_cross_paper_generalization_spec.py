#!/usr/bin/env python3
"""Validator for Cross-Paper Delimiter Generalization Specification v1.

Verifies:
  1. Spec schema completeness (all 7 families, 5 dimensions, experimental controls, negative controls).
  2. Conjunctive strict 5-axis policy enforcement (missing evidence -> NOT_VERIFIED).
  3. Immutable delimiter engine baseline hash matching repository disk state.
  4. Structural layout convention (sparse/truncated matrices vs populated cells).
  5. Case record validation helper for future candidate evaluation records.
"""
from __future__ import annotations

import sys
import io
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
SPEC_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_delimiter_generalization_spec_v1.json"
ENGINE_PATH = REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py"

REQUIRED_FAMILIES = [
    "FAM_001_DELIMITER_IDENTITY",
    "FAM_002_NESTED_STRUCTURES",
    "FAM_003_ADJACENT_MATRICES",
    "FAM_004_EMBEDDED_MATHEMATICS",
    "FAM_005_EXTENSIBLE_GLYPHS",
    "FAM_006_CONTINUATION_SYMBOLS",
    "FAM_007_PROSE_ADJACENCY",
]

REQUIRED_DIMENSIONS = [
    "dim_1_geometric_localization",
    "dim_2_glyph_completeness",
    "dim_3_structural_recovery",
    "dim_4_semantic_fidelity",
    "dim_5_boundary_isolation",
]

REQUIRED_NEGATIVE_CONTROLS = [
    "NEG_MISMATCHED_DELIMITER_TYPES",
    "NEG_MISSING_CLOSING_PARTNER",
    "NEG_INTERVENING_DELIMITER_COLLISION",
    "NEG_TALL_NON_MATH_GRAPHIC",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def validate_spec(spec_path: Path = SPEC_PATH) -> dict:
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    errors = []

    # 1. Spec header
    if spec.get("spec_identifier") != "CROSS-PAPER-DELIMITER-GENERALIZATION-SPEC-V1":
        errors.append("Invalid or missing spec_identifier")
    if spec.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    # 2. Immutable Engine Baseline
    engine_meta = spec.get("immutable_engine_baseline", {})
    expected_engine_sha = engine_meta.get("engine_sha256")
    if ENGINE_PATH.exists():
        actual_engine_sha = sha256_file(ENGINE_PATH)
        if actual_engine_sha != expected_engine_sha:
            errors.append(f"Engine hash mismatch: spec says {expected_engine_sha}, disk is {actual_engine_sha}")
    else:
        errors.append(f"Engine script not found at {ENGINE_PATH}")

    # 3. Acceptance Dimensions & Conjunctive Policy
    acc_dims = spec.get("acceptance_dimensions", {})
    if acc_dims.get("evaluation_policy") != "CONJUNCTIVE_STRICT_FIVE_AXIS":
        errors.append("evaluation_policy must be 'CONJUNCTIVE_STRICT_FIVE_AXIS'")

    dims = acc_dims.get("dimensions", {})
    for d in REQUIRED_DIMENSIONS:
        if d not in dims:
            errors.append(f"Missing mandatory dimension: {d}")
        else:
            if not dims[d].get("failure_verdict"):
                errors.append(f"Dimension {d} missing failure_verdict")

    # 4. Seven Test Families
    families = {fam["family_id"]: fam for fam in spec.get("test_families", []) if "family_id" in fam}
    for fam_id in REQUIRED_FAMILIES:
        if fam_id not in families:
            errors.append(f"Missing mandatory test family: {fam_id}")
        else:
            fam = families[fam_id]
            for field in ["name", "required_evidence", "primary_failure_mode", "mandatory_guards"]:
                if field not in fam or not fam[field]:
                    errors.append(f"Family {fam_id} missing or empty field: {field}")

    # 5. Negative Controls
    neg_controls = spec.get("negative_control_requirements", {}).get("required_negative_cases", [])
    for nc in REQUIRED_NEGATIVE_CONTROLS:
        if nc not in neg_controls:
            errors.append(f"Missing required negative control: {nc}")

    # 6. Case Record Schema & Status Enums
    case_schema = spec.get("case_record_schema", {})
    expected_status_enum = ["PASSED_CERTIFIED", "FAILED", "NOT_VERIFIED"]
    actual_status_enum = case_schema.get("certification_status_enum", [])
    if actual_status_enum != expected_status_enum:
        errors.append(f"certification_status_enum must be {expected_status_enum}, got {actual_status_enum}")

    # 7. Structural Layout Convention Note
    layout_note = spec.get("benchmark_architecture", {}).get("structural_layout_convention_note", "")
    if "40 recovered tokens" not in layout_note and "7x6" not in layout_note:
        errors.append("benchmark_architecture must contain explicit structural layout convention note")

    return {
        "valid": len(errors) == 0,
        "spec_identifier": spec.get("spec_identifier"),
        "errors": errors,
        "families_count": len(families),
        "dimensions_count": len(dims),
        "engine_sha256_verified": len(errors) == 0,
    }


def validate_case_record(case_record: dict, spec: dict) -> list[str]:
    """Helper to validate an individual candidate evaluation record against the spec."""
    errors = []
    case_schema = spec.get("case_record_schema", {})
    required_fields = case_schema.get("required_case_fields", [])
    for f in required_fields:
        if f not in case_record:
            errors.append(f"Case record missing required field: {f}")

    # 5-axis completeness
    five_dim = case_record.get("five_dimension_results", {})
    for d in REQUIRED_DIMENSIONS:
        if d not in five_dim:
            errors.append(f"Case record missing dimension: {d}")
        else:
            dim_status = five_dim[d].get("status")
            if dim_status not in ["PASS", "FAIL", "NOT_VERIFIED"]:
                errors.append(f"Dimension {d} invalid status: {dim_status}")

    # Conjunctive strict policy check
    cert_status = case_record.get("certification_status")
    any_fail = any(five_dim.get(d, {}).get("status") == "FAIL" for d in REQUIRED_DIMENSIONS)
    any_unverified = any(five_dim.get(d, {}).get("status") == "NOT_VERIFIED" for d in REQUIRED_DIMENSIONS)

    if (any_fail or any_unverified) and cert_status == "PASSED_CERTIFIED":
        errors.append("Violation of CONJUNCTIVE_STRICT_FIVE_AXIS: case marked PASSED_CERTIFIED despite failing/unverified dimension")

    return errors


def main():
    print("[validate_spec] Validating Cross-Paper Delimiter Generalization Spec v1...")
    res = validate_spec(SPEC_PATH)
    if res["valid"]:
        print(f"SUCCESS: Spec is valid! ({res['families_count']} families, {res['dimensions_count']} dimensions)")
        print(f"Engine Baseline SHA-256 verified against repository disk state.")
    else:
        print("FAILED: Spec validation encountered errors:")
        for e in res["errors"]:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    main()
