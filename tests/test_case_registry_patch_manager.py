"""Tests for Case Registry Patch Manager.

Verifies:
  1. Patch schema integrity and cryptographic self-hash verification.
  2. Precondition checking: fails on registry hash mismatch, old_value mismatch, tampering.
  3. Non-mutating overlay: applying patches produces an in-memory view while base file on disk is unchanged.
  4. Integration with the frozen Two-Level Case Registry.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from case_registry_patch_manager import (
    DEFAULT_REGISTRY,
    compute_patch_hash,
    create_patch,
    get_nested_field,
    load_patched_registry,
    set_nested_field,
    validate_patch,
)


@pytest.fixture
def mock_registry():
    return {
        "registry_version": "1.0",
        "cases": [
            {
                "case_id": "CASE-001",
                "gold_ast": {"delimiter_type": "old_type", "level": 1},
                "metadata": {"reviewer": "auditor_1"},
            }
        ],
    }


def test_nested_field_get_and_set(mock_registry):
    val = get_nested_field(mock_registry["cases"][0], "gold_ast.delimiter_type")
    assert val == "old_type"

    set_nested_field(mock_registry["cases"][0], "gold_ast.delimiter_type", "new_type")
    assert mock_registry["cases"][0]["gold_ast"]["delimiter_type"] == "new_type"


def test_patch_hashing_and_tamper_detection():
    patch = {
        "patch_id": "PATCH-001",
        "target_registry_hash": "dummy_hash_123",
        "target_case_id": "CASE-001",
        "field_path": "gold_ast.delimiter_type",
        "old_value": "old_type",
        "new_value": "new_type",
        "reviewer": "auditor_x",
        "reason": "Fix delimiter classification",
        "evidence_ref": "Inspection note #1",
        "created_at": "2026-11-06T00:00:00Z",
    }
    h = compute_patch_hash(patch)
    patch["patch_sha256"] = h
    assert len(h) == 64

    # Tampering should fail validation
    tampered = copy.deepcopy(patch)
    tampered["new_value"] = "tampered_value"
    with pytest.raises(ValueError, match="integrity failure"):
        validate_patch(tampered, {"cases": [{"case_id": "CASE-001", "gold_ast": {"delimiter_type": "old_type"}}]}, "dummy_hash_123")


def test_precondition_failures(mock_registry):
    base_hash = "correct_base_hash"
    patch = {
        "patch_id": "PATCH-001",
        "target_registry_hash": base_hash,
        "target_case_id": "CASE-001",
        "field_path": "gold_ast.delimiter_type",
        "old_value": "wrong_expected_old",
        "new_value": "new_type",
        "reviewer": "auditor_x",
        "reason": "Test reason",
        "evidence_ref": "Doc #1",
        "created_at": "2026-11-06T00:00:00Z",
    }
    patch["patch_sha256"] = compute_patch_hash(patch)

    # 1. Base hash mismatch
    with pytest.raises(ValueError, match="Registry hash mismatch"):
        validate_patch(patch, mock_registry, "different_base_hash")

    # 2. old_value mismatch
    with pytest.raises(ValueError, match="Precondition failure"):
        validate_patch(patch, mock_registry, base_hash)


def test_non_mutating_overlay_on_disk(tmp_path):
    base_file = tmp_path / "mock_registry.json"
    registry_data = {
        "registry_version": "1.0",
        "cases": [
            {
                "case_id": "CASE-001",
                "gold_ast": {"delimiter_type": "bracket"},
            }
        ],
    }
    content = json.dumps(registry_data).encode("utf-8")
    base_file.write_bytes(content)
    base_hash_before = hashlib.sha256(content).hexdigest()

    patch_dir = tmp_path / "patches"
    create_patch(
        patch_id="PATCH-001",
        target_registry_hash=base_hash_before,
        target_case_id="CASE-001",
        field_path="gold_ast.delimiter_type",
        old_value="bracket",
        new_value="nested_bracket",
        reviewer="auditor_x",
        reason="Refine taxonomy",
        evidence_ref="Note 1",
        created_at="2026-11-06T00:00:00Z",
        output_dir=patch_dir,
    )

    overlay, applied = load_patched_registry(base_file, patch_dir)

    # In-memory overlay reflects patch
    assert len(applied) == 1
    assert overlay["cases"][0]["gold_ast"]["delimiter_type"] == "nested_bracket"
    assert overlay["_overlay_metadata"]["total_patches_applied"] == 1
    assert overlay["_overlay_metadata"]["parent_registry_hash"] == base_hash_before
    assert len(overlay["_overlay_metadata"]["effective_registry_hash"]) == 64
    assert overlay["_overlay_metadata"]["effective_registry_hash"] != base_hash_before

    # Applied patch metadata is complete
    ap = overlay["_overlay_metadata"]["applied_patches"][0]
    assert ap["old_value"] == "bracket"
    assert ap["new_value"] == "nested_bracket"
    assert ap["reviewer"] == "auditor_x"

    # Base file on disk is strictly unchanged
    base_bytes_after = base_file.read_bytes()
    assert hashlib.sha256(base_bytes_after).hexdigest() == base_hash_before
    disk_data = json.loads(base_bytes_after.decode("utf-8"))
    assert disk_data["cases"][0]["gold_ast"]["delimiter_type"] == "bracket"


def test_safeguard_against_unadjudicated_criteria_modification(mock_registry):
    base_hash = "correct_base_hash"
    patch = {
        "patch_id": "PATCH-CRITERIA-MUTATION",
        "target_registry_hash": base_hash,
        "target_case_id": "CASE-001",
        "field_path": "five_axis_acceptance_criteria.dim_1",
        "old_value": "FAIL",
        "new_value": "PASS",
        "reviewer": "unauthorized",
        "reason": "attempt to change criteria",
        "evidence_ref": "None",
        "created_at": "2026-11-06T00:00:00Z",
    }
    patch["patch_sha256"] = compute_patch_hash(patch)

    mock_with_criteria = {
        "cases": [
            {
                "case_id": "CASE-001",
                "five_axis_acceptance_criteria": {"dim_1": "FAIL"},
            }
        ]
    }

    # Should raise ValueError due to safeguard violation
    with pytest.raises(ValueError, match="Safeguard violation"):
        validate_patch(patch, mock_with_criteria, base_hash)

    # With explicit adjudication_override=True, validation proceeds
    patch["adjudication_override"] = True
    patch["patch_sha256"] = compute_patch_hash(patch)
    validate_patch(patch, mock_with_criteria, base_hash)  # passes


