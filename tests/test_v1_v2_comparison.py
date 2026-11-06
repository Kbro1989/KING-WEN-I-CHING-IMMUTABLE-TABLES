"""Tests for Controlled v1 vs v2 Comparative Evaluation.

Verifies:
  1. Frozen v1 baseline behavior matches historical freeze manifest:
     - 0 / 3 cases certified
     - 3 / 3 cases fail NEG_MISMATCHED_DELIMITER_TYPES (known soft-scoring limitation)
     - 3 / 3 cases pass dim_5_boundary_isolation
  2. Remediated v2 engine demonstrates measured improvements:
     - CP-001 achieves PASSED_CERTIFIED under conjunctive 5-axis policy
     - 3 / 3 cases pass NEG_MISMATCHED_DELIMITER_TYPES (hard prerequisite gate)
     - CP-003 achieves dim_2_glyph_completeness PASS (Latin Modern /vextenddouble norm)
     - 3 / 3 cases preserve dim_5_boundary_isolation (Gate D4 >= 2.0 pt)
  3. Machine-readable comparative report integrity.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
REPORT_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "v1_v2_comparative_evaluation_report.json"


@pytest.fixture(scope="module")
def comparative_data():
    assert REPORT_PATH.exists(), f"Comparative report missing: {REPORT_PATH}"
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_v1_control_group_baseline_fidelity(comparative_data):
    v1 = comparative_data["v1_control_group"]
    assert v1["engine_version"] == "v1-frozen"
    assert v1["passed_certified"] == 0
    assert v1["failed"] >= 3
    # Mismatched negative control failed in all cases in v1
    assert v1["mismatched_neg_control_pass_count"] == 0
    for c in v1["cases"]:
        assert c["dimensions"]["dim_5_boundary_isolation"] == "PASS"
        assert c["negative_controls"]["NEG_MISMATCHED_DELIMITER_TYPES"] == "FAIL"


def test_v2_treatment_group_remediation_acceptance(comparative_data):
    v2 = comparative_data["v2_treatment_group"]
    assert v2["engine_version"] == "v2-remediated"
    assert v2["passed_certified"] == 4  # All 4 cases (3 baseline + 1 unseen) certified!

    # EL-003: Mismatched negative control now passes in all 4 cases
    assert v2["mismatched_neg_control_pass_count"] == 4
    for c in v2["cases"]:
        assert c["negative_controls"]["NEG_MISMATCHED_DELIMITER_TYPES"] == "PASS"
        assert c["dimensions"]["dim_5_boundary_isolation"] == "PASS"


def test_cp001_remediation_transition(comparative_data):
    v1_cp001 = next(c for c in comparative_data["v1_control_group"]["cases"] if c["case_id"] == "CP-001-CLUSTER-GCN-BMATRIX")
    v2_cp001 = next(c for c in comparative_data["v2_treatment_group"]["cases"] if c["case_id"] == "CP-001-CLUSTER-GCN-BMATRIX")

    # v1 misclassified txexs brackets as braces
    assert v1_cp001["op_class"]["kind"] == "brace"
    assert v1_cp001["dimensions"]["dim_2_glyph_completeness"] == "FAIL"
    assert v1_cp001["verdict"] == "FAILED"

    # v2 correctly branches on txexs and certifies CP-001
    assert v2_cp001["op_class"]["kind"] == "bracket"
    assert v2_cp001["dimensions"]["dim_2_glyph_completeness"] == "PASS"
    assert v2_cp001["verdict"] == "PASSED_CERTIFIED"


def test_cp003_latin_modern_norm_remediation(comparative_data):
    v1_cp003 = next(c for c in comparative_data["v1_control_group"]["cases"] if c["case_id"] == "CP-003-LINEAR-PROBING-NORM")
    v2_cp003 = next(c for c in comparative_data["v2_treatment_group"]["cases"] if c["case_id"] == "CP-003-LINEAR-PROBING-NORM")

    # v1 failed to recognize Latin Modern \r as norm
    assert v1_cp003["dimensions"]["dim_2_glyph_completeness"] == "FAIL"

    # v2 correctly recognizes norm kind and certifies CP-003
    assert v2_cp003["op_class"]["kind"] == "norm"
    assert v2_cp003["dimensions"]["dim_2_glyph_completeness"] == "PASS"
    assert v2_cp003["verdict"] == "PASSED_CERTIFIED"


def test_cp004_unseen_paper_generalization(comparative_data):
    """CP-004 (GAN Jensen-Shannon) demonstrates genuine out-of-sample generalization."""
    v1_cp004 = next(c for c in comparative_data["v1_control_group"]["cases"] if c["case_id"] == "CP-004-GAN-KL-JENSEN-SHANNON")
    v2_cp004 = next(c for c in comparative_data["v2_treatment_group"]["cases"] if c["case_id"] == "CP-004-GAN-KL-JENSEN-SHANNON")

    # v1 failed on unmapped CMEX large parenthesis (\x12 / \x13)
    assert v1_cp004["dimensions"]["dim_2_glyph_completeness"] == "FAIL"
    assert v1_cp004["verdict"] == "FAILED"

    # v2 resolves CMEX parentheses and certifies CP-004 under 5-axis criteria
    assert v2_cp004["op_class"]["kind"] == "parenthesis"
    assert v2_cp004["dimensions"]["dim_1_geometric_localization"] == "PASS"
    assert v2_cp004["dimensions"]["dim_2_glyph_completeness"] == "PASS"
    assert v2_cp004["dimensions"]["dim_3_structural_recovery"] == "PASS"
    assert v2_cp004["dimensions"]["dim_4_semantic_fidelity"] == "PASS"
    assert v2_cp004["dimensions"]["dim_5_boundary_isolation"] == "PASS"
    assert v2_cp004["verdict"] == "PASSED_CERTIFIED"

