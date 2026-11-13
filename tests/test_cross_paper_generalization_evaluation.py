"""Tests for the Cross-Paper Generalization v1 Evaluation Report.

Asserts that:
  - The evaluation report artifact exists and is well-formed.
  - The report's input hashes match the frozen registry and engine.
  - Each of the three cases has all five mandatory dimension results.
  - Each case has all four mandatory negative control results.
  - Specific expected verdicts are recorded (baseline behavior, not aspirational).
  - The identified engine limitation (NEG_MISMATCHED_DELIMITER_TYPES) is explicitly
    documented as a known failure, not silently ignored.
  - The report verdict summary matches the per-case results.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
EVAL_REPORT = (
    REPO_ROOT
    / "DATASETS"
    / "structural_preservation"
    / "cross_paper_generalization_evaluation_v1.json"
)
REGISTRY_PATH = (
    REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
)
ENGINE_PATH = REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py"
SPEC_PATH = (
    REPO_ROOT
    / "DATASETS"
    / "structural_preservation"
    / "cross_paper_delimiter_generalization_spec_v1.json"
)

EXPECTED_ENGINE_SHA = "8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1"
EXPECTED_SPEC_SHA = "188ac350a7b50166d34ac6dabcc00c7a49d540b0e01873e684739f614304b4ae"
EXPECTED_REGISTRY_SHA = "da4c166b7a5c7b1808d33b2d9f2ca0d71a0d60bf19d6844796506a51da36e6ba"
EXPECTED_REPORT_SHA = "85320ae710afe3af4cb56c626691c6c76b9f93611258610d11eb76d505614454"

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
EXPECTED_CASE_IDS = [
    "CP-001-CLUSTER-GCN-BMATRIX",
    "CP-002-VILT-NESTED-BRACKETS",
    "CP-003-LINEAR-PROBING-NORM",
]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def report() -> dict:
    assert EVAL_REPORT.exists(), f"Evaluation report not found: {EVAL_REPORT}"
    with open(EVAL_REPORT, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def cases_by_id(report) -> dict:
    return {c["case_id"]: c for c in report["case_evaluations"]}


# ---------------------------------------------------------------------------
# 1. Artifact existence and integrity
# ---------------------------------------------------------------------------


def test_evaluation_report_exists():
    assert EVAL_REPORT.exists(), f"Evaluation report missing: {EVAL_REPORT}"


def test_evaluation_report_sha256():
    actual = _sha256_file(EVAL_REPORT)
    assert actual == EXPECTED_REPORT_SHA, (
        f"Evaluation report SHA-256 changed.\n"
        f"  Expected: {EXPECTED_REPORT_SHA}\n"
        f"  Actual:   {actual}"
    )


def test_engine_sha256_unchanged():
    actual = _sha256_file(ENGINE_PATH)
    assert actual == EXPECTED_ENGINE_SHA, (
        f"Engine drift detected during evaluation test.\n"
        f"  Expected: {EXPECTED_ENGINE_SHA}\n"
        f"  Actual:   {actual}"
    )


def test_spec_sha256_unchanged():
    actual = _sha256_file(SPEC_PATH)
    assert actual == EXPECTED_SPEC_SHA, (
        f"Spec drift detected.\n"
        f"  Expected: {EXPECTED_SPEC_SHA}\n"
        f"  Actual:   {actual}"
    )


def test_registry_sha256_unchanged():
    actual = _sha256_file(REGISTRY_PATH)
    assert actual == EXPECTED_REGISTRY_SHA, (
        f"Registry drift detected.\n"
        f"  Expected: {EXPECTED_REGISTRY_SHA}\n"
        f"  Actual:   {actual}"
    )


# ---------------------------------------------------------------------------
# 2. Report structure
# ---------------------------------------------------------------------------


def test_report_identifier(report):
    assert report["evaluation_identifier"] == "CROSS-PAPER-GENERALIZATION-EVALUATION-V1"


def test_report_acceptance_policy(report):
    assert report["acceptance_policy"] == "CONJUNCTIVE_STRICT_FIVE_AXIS"


def test_report_has_three_cases(report):
    assert len(report["case_evaluations"]) == 3


def test_report_case_ids(report):
    actual_ids = [c["case_id"] for c in report["case_evaluations"]]
    for cid in EXPECTED_CASE_IDS:
        assert cid in actual_ids, f"Missing case ID: {cid}"


def test_report_input_engine_hash_recorded(report):
    recorded = report["evaluation_inputs"]["delimiter_engine_baseline"]["sha256"]
    assert recorded == EXPECTED_ENGINE_SHA


def test_report_input_spec_hash_recorded(report):
    recorded = report["evaluation_inputs"]["specification"]["sha256"]
    assert recorded == EXPECTED_SPEC_SHA


def test_report_input_registry_hash_recorded(report):
    recorded = report["evaluation_inputs"]["case_registry"]["sha256"]
    assert recorded == EXPECTED_REGISTRY_SHA


# ---------------------------------------------------------------------------
# 3. Dimension coverage: all five axes present for every case
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_all_five_dimensions_present(cases_by_id, case_id):
    case = cases_by_id[case_id]
    dims = case["five_dimension_results"]
    for d in REQUIRED_DIMENSIONS:
        assert d in dims, f"{case_id} missing dimension: {d}"


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_all_dimension_statuses_are_valid(cases_by_id, case_id):
    case = cases_by_id[case_id]
    for d, r in case["five_dimension_results"].items():
        assert r["status"] in {"PASS", "FAIL", "NOT_VERIFIED"}, (
            f"{case_id}/{d} has invalid status: {r['status']}"
        )


# ---------------------------------------------------------------------------
# 4. Negative control coverage: all four controls present for every case
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_all_negative_controls_present(cases_by_id, case_id):
    case = cases_by_id[case_id]
    nc_ids = {n["control_id"] for n in case["negative_control_results"]}
    for required in REQUIRED_NEGATIVE_CONTROLS:
        assert required in nc_ids, f"{case_id} missing negative control: {required}"


# ---------------------------------------------------------------------------
# 5. Conjunctive verdict consistency
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_verdict_is_conjunctive(cases_by_id, case_id):
    """Verify that the terminal verdict is consistent with the conjunctive rule."""
    case = cases_by_id[case_id]
    dims = case["five_dimension_results"]
    all_pass = all(dims[d]["status"] == "PASS" for d in REQUIRED_DIMENSIONS)
    any_fail = any(dims[d]["status"] == "FAIL" for d in REQUIRED_DIMENSIONS)
    verdict = case["terminal_verdict"]
    if all_pass:
        assert verdict == "PASSED_CERTIFIED", f"{case_id}: all dims PASS but verdict={verdict}"
    elif any_fail:
        assert verdict == "FAILED", f"{case_id}: some dim FAIL but verdict={verdict}"
    else:
        assert verdict == "NOT_VERIFIED", f"{case_id}: indeterminate but verdict={verdict}"


# ---------------------------------------------------------------------------
# 6. Baseline engine behavior assertions (what the FROZEN engine actually does)
# ---------------------------------------------------------------------------


def test_cp001_cluster_gcn_verdict(cases_by_id):
    """CP-001: FAILED — txexs U+F8EE classified as brace (not bracket) by CMEX table.
    dim_1 and dim_2 fail; dim_3 and dim_5 pass. This is the expected baseline.
    """
    c = cases_by_id["CP-001-CLUSTER-GCN-BMATRIX"]
    assert c["terminal_verdict"] == "FAILED"
    assert c["five_dimension_results"]["dim_2_glyph_completeness"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_3_structural_recovery"]["status"] == "PASS"
    assert c["five_dimension_results"]["dim_5_boundary_isolation"]["status"] == "PASS"
    assert c["engine_classification"]["opening"]["kind"] == "brace"
    assert c["engine_classification"]["closing"]["kind"] == "unknown"


def test_cp001_cluster_gcn_paired(cases_by_id):
    """CP-001: Engine still forms a pair despite kind=brace vs kind=unknown."""
    c = cases_by_id["CP-001-CLUSTER-GCN-BMATRIX"]
    assert c["engine_classification"]["paired"] is True


def test_cp002_vilt_verdict(cases_by_id):
    """CP-002: FAILED — dim_1 geometric localization fails (enclosure bbox mismatch).
    dim_2–dim_5 pass. Standard CMR10 brackets correctly recognized.
    """
    c = cases_by_id["CP-002-VILT-NESTED-BRACKETS"]
    assert c["terminal_verdict"] == "FAILED"
    assert c["five_dimension_results"]["dim_1_geometric_localization"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_2_glyph_completeness"]["status"] == "PASS"
    assert c["five_dimension_results"]["dim_3_structural_recovery"]["status"] == "PASS"
    assert c["five_dimension_results"]["dim_4_semantic_fidelity"]["status"] == "PASS"
    assert c["five_dimension_results"]["dim_5_boundary_isolation"]["status"] == "PASS"


def test_cp002_vilt_bracket_recognition(cases_by_id):
    """CP-002: Standard CMR10 brackets (U+005B, U+005D) are correctly recognized."""
    c = cases_by_id["CP-002-VILT-NESTED-BRACKETS"]
    assert c["engine_classification"]["opening"]["kind"] == "bracket"
    assert c["engine_classification"]["closing"]["kind"] == "bracket"
    assert c["engine_classification"]["opening"]["family"] == "standard"


def test_cp003_linear_probing_verdict(cases_by_id):
    """CP-003: FAILED — LMMathExtension10 U+000D (vextenddouble) unrecognized by engine.
    Four dimensions fail; only dim_5 passes.
    """
    c = cases_by_id["CP-003-LINEAR-PROBING-NORM"]
    assert c["terminal_verdict"] == "FAILED"
    assert c["five_dimension_results"]["dim_1_geometric_localization"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_2_glyph_completeness"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_3_structural_recovery"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_4_semantic_fidelity"]["status"] == "FAIL"
    assert c["five_dimension_results"]["dim_5_boundary_isolation"]["status"] == "PASS"


def test_cp003_linear_probing_unresolved_glyph(cases_by_id):
    """CP-003: U+000D from LMMathExtension10 classified as 'unknown' — documented limitation."""
    c = cases_by_id["CP-003-LINEAR-PROBING-NORM"]
    assert c["engine_classification"]["opening"]["kind"] == "unknown"
    assert c["engine_classification"]["opening"]["resolution_method"] == "unresolved"
    assert "U+000D" in c["engine_classification"]["opening"]["raw_characters"]


# ---------------------------------------------------------------------------
# 7. Known engine limitations (must remain documented, not silently removed)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_neg_mismatched_delimiter_types_is_documented_failure(cases_by_id, case_id):
    """NEG_MISMATCHED_DELIMITER_TYPES fails for all three cases.

    Root cause: associate_delimiter_pairs pairs candidates at geometric score 0.7
    even without kind_match, because: score = y_iou*0.4 + h_ratio*0.3 + 0.0 = 0.70
    exactly meets the >=0.70 threshold.  This is a known engine limitation.
    The test asserts it FAILS (baseline documentation), not that it should pass.
    """
    c = cases_by_id[case_id]
    nc = {n["control_id"]: n for n in c["negative_control_results"]}
    assert nc["NEG_MISMATCHED_DELIMITER_TYPES"]["status"] == "FAIL", (
        f"{case_id}: NEG_MISMATCHED_DELIMITER_TYPES expected FAIL (known engine limitation) "
        f"but got PASS — verify that the engine threshold was not silently changed."
    )


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_neg_missing_closing_partner_passes(cases_by_id, case_id):
    """NEG_MISSING_CLOSING_PARTNER: opening-only candidate preserved as unpaired."""
    c = cases_by_id[case_id]
    nc = {n["control_id"]: n for n in c["negative_control_results"]}
    assert nc["NEG_MISSING_CLOSING_PARTNER"]["status"] == "PASS"


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_neg_intervening_collision_passes(cases_by_id, case_id):
    """NEG_INTERVENING_DELIMITER_COLLISION: adjacent pairs do not cross-associate."""
    c = cases_by_id[case_id]
    nc = {n["control_id"]: n for n in c["negative_control_results"]}
    assert nc["NEG_INTERVENING_DELIMITER_COLLISION"]["status"] == "PASS"


@pytest.mark.parametrize("case_id", EXPECTED_CASE_IDS)
def test_neg_tall_non_math_graphic_passes(cases_by_id, case_id):
    """NEG_TALL_NON_MATH_GRAPHIC: tall non-math region classified as unknown / low-confidence."""
    c = cases_by_id[case_id]
    nc = {n["control_id"]: n for n in c["negative_control_results"]}
    assert nc["NEG_TALL_NON_MATH_GRAPHIC"]["status"] == "PASS"


# ---------------------------------------------------------------------------
# 8. Verdict summary consistency
# ---------------------------------------------------------------------------


def test_verdict_summary_matches_case_results(report, cases_by_id):
    summary = report["verdict_summary"]
    counted = {"PASSED_CERTIFIED": 0, "FAILED": 0, "NOT_VERIFIED": 0}
    for c in report["case_evaluations"]:
        counted[c["terminal_verdict"]] += 1
    assert counted == summary, (
        f"Verdict summary mismatch.\n  Counted: {counted}\n  Reported: {summary}"
    )


def test_verdict_summary_values(report):
    summary = report["verdict_summary"]
    assert summary["PASSED_CERTIFIED"] == 0
    assert summary["FAILED"] == 3
    assert summary["NOT_VERIFIED"] == 0

