"""
Integration-Level Eligibility Enforcement Test (Qualification 3)
Structural Preservation Pipeline — Layer 1 → Layer 2 Boundary

Verifies that the gating contract between the observer and the expectation
builder is enforced end-to-end: regions classified as ineligible by the
observer must produce zero structural expectations when passed through the
expectation generator entry point.

This test is intentionally separate from test_spatial_syntactic_observer.py,
which covers the observer's internal unit contracts.  This test covers the
downstream boundary: a consumer of the region assessments JSON must honour
the expectation_generation_eligible flag.
"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
REGION_ASSESS_PATH = (
    REPO_ROOT / "DATASETS" / "structural_preservation"
    / "2009.00031_p005_region_assessments.json"
)


# ---------------------------------------------------------------------------
# Stub expectation generator
# ---------------------------------------------------------------------------
# Layer 2 (Structural Expectation Ledger) is not yet implemented.  This stub
# models the entry-point contract: given a region assessment record, produce
# a list of structural expectations.  Note: This test suite verifies the
# proposed gating contract across the Layer 1 -> Layer 2 interface, not
# production enforcement (which awaits production consumer implementation).
# The contract rule is:
#
#   if region["assessment"]["expectation_generation_eligible"] is False:
#       return []   # zero expectations, no exceptions, no silent bypass
#
# When the real builder is implemented it must satisfy this same interface and
# the assertions below must still pass without modification to this test.

def stub_expectation_generator(region_record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Stub entry point representing the Layer 2 expectation builder.

    Returns an empty list for ineligible regions and raises NotImplementedError
    for eligible regions (indicating the real builder has not been wired yet).
    This makes the gating contract testable independently of Layer 2 work.
    """
    eligible = region_record["assessment"]["expectation_generation_eligible"]
    if not eligible:
        return []
    # Eligible path: real builder not yet implemented.
    raise NotImplementedError(
        f"Expectation builder not implemented for eligible region "
        f"{region_record['region_id']}"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def region_data() -> Dict[str, Any]:
    assert REGION_ASSESS_PATH.exists(), (
        f"Region assessment file missing: {REGION_ASSESS_PATH}\n"
        "Run: python scripts/spatial_syntactic_observer.py"
    )
    with open(REGION_ASSESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_ineligible_regions_produce_zero_expectations(region_data):
    """
    Core gating contract: every ineligible region must produce an empty
    expectation list.  No exceptions, no silently skipped regions.
    """
    regions = region_data["regions"]
    ineligible_regions = [
        r for r in regions
        if not r["assessment"]["expectation_generation_eligible"]
    ]

    # Confirm we have the expected negative-control population
    assert len(ineligible_regions) == 15, (
        f"Expected 15 ineligible regions from 2009.00031 pilot; "
        f"got {len(ineligible_regions)}"
    )

    for reg in ineligible_regions:
        expectations = stub_expectation_generator(reg)
        assert expectations == [], (
            f"Region {reg['region_id']} is ineligible but produced "
            f"{len(expectations)} expectation(s): {expectations}"
        )


def test_all_negative_controls_are_ineligible(region_data):
    """
    Every NEGATIVE_CONTROL_NON_MATH region must have
    expectation_generation_eligible=False.  Verifies the JSON contract is
    self-consistent before the stub is applied.
    """
    for reg in region_data["regions"]:
        assess = reg["assessment"]
        if assess["classification"] == "NEGATIVE_CONTROL_NON_MATH":
            assert assess["expectation_generation_eligible"] is False, (
                f"Region {reg['region_id']} is NEGATIVE_CONTROL_NON_MATH "
                f"but expectation_generation_eligible is True"
            )


def test_no_eligible_regions_in_negative_control_population(region_data):
    """
    The 2009.00031 pilot is a pure negative-control population.
    No region should be eligible for expectation generation.
    This distinguishes it from a future positive population (1505.05770).
    """
    eligible = [
        r["region_id"] for r in region_data["regions"]
        if r["assessment"]["expectation_generation_eligible"]
    ]
    assert eligible == [], (
        f"Unexpected eligible regions in negative-control population: {eligible}"
    )


def test_eligible_regions_would_reach_builder(region_data):
    """
    Structural test: confirms the stub correctly propagates to the builder
    for any eligible region.  Since this is a pure negative-control population,
    no region should reach the builder, and no NotImplementedError should fire.
    This test documents the expected stub behaviour for the future positive
    population test suite.
    """
    regions = region_data["regions"]
    eligible_regions = [
        r for r in regions
        if r["assessment"]["expectation_generation_eligible"]
    ]
    # In the negative-control population there are none — which is correct.
    assert len(eligible_regions) == 0

    # Verify stub raises for a synthetic eligible record (documents the contract)
    synthetic_eligible = {
        "region_id": "reg_synthetic_eligible",
        "assessment": {
            "expectation_generation_eligible": True,
            "classification": "PENDING_CLASSIFICATION",
        },
    }
    with pytest.raises(NotImplementedError):
        stub_expectation_generator(synthetic_eligible)


# ---------------------------------------------------------------------------
# Layer A/B Representation Recovery Tests (Milestone 2)
# ---------------------------------------------------------------------------

def test_font_aware_classifier_identifies_integral_and_blackboard():
    """
    Verifies that font-aware interpretation resolves TeX font encodings:
    CMEX10 'Z' -> \\int (integral operator)
    MSBM10 'E' -> \\mathbb{E}
    CMMI10 'p' -> math italic variable
    Ordinary CMR10 'Z' is NOT mathematical.
    """
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from font_aware_math_classifier import classify_glyph

    cmex_z = classify_glyph("Z", "CMEX10")
    assert cmex_z["is_math"] is True
    assert cmex_z["latex_interpretation"] == r"\int"
    assert cmex_z["operator_role"] == "operator_integral"

    cmr_z = classify_glyph("Z", "CMR10")
    assert cmr_z["is_math"] is False
    assert cmr_z["latex_interpretation"] is None

    msbm_e = classify_glyph("E", "MSBM10")
    assert msbm_e["is_math"] is True
    assert msbm_e["latex_interpretation"] == r"\mathbb{E}"

    cmmi_p = classify_glyph("p", "CMMI10")
    assert cmmi_p["is_math"] is True
    assert cmmi_p["math_category"] == "math_italic_variable"


def test_citation_discrimination_flags_bibliographic_years():
    """
    Verifies that bibliographic citations like (Kingma & Welling, 2014) or (2000; 2014)
    are flagged as citations, while real mathematical expressions with operators are not.
    """
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from font_aware_math_classifier import discriminate_citation

    c1 = discriminate_citation("(Kingma & Welling, 2014)")
    assert c1["is_citation_candidate"] is True
    assert c1["citation_confidence"] >= 0.7

    c2 = discriminate_citation("(2000; 2014)")
    assert c2["is_citation_candidate"] is True

    # Real math equation with 'log' and '=' should not be flagged as citation
    m1 = discriminate_citation("log pθ(x) = log ∫ pθ(x|z)p(z)dz")
    assert m1["is_citation_candidate"] is False
    assert m1["has_math_operators"] is True


def test_gs001_geometry_provenance_preserves_both_bboxes():
    """
    Verifies that the positive control manifest preserves both original and
    corrected bounding boxes for GS-001, along with provenance reason and evidence.
    """
    manifest_path = (
        REPO_ROOT / "DATASETS" / "structural_preservation"
        / "1505.05770_positive_control_manifest.json"
    )
    assert manifest_path.exists()
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gs1 = next(g for g in data["gold_equations"] if g["gold_id"] == "GS-001")
    loc = gs1["pdf_localization"]

    assert "original_gold_pdf_bbox" in loc
    assert "corrected_gold_pdf_bbox" in loc
    assert "geometry_correction_provenance" in loc

    assert loc["original_gold_pdf_bbox"] == [138.5, 90.2, 282.5, 112.0]
    assert loc["corrected_gold_pdf_bbox"] == [87.3, 90.2, 282.5, 112.0]
    assert loc["gold_pdf_bbox"] == [87.3, 90.2, 282.5, 112.0]

    prov = loc["geometry_correction_provenance"]
    assert prov["status"] == "CORRECTED_WITH_EVIDENCE"
    assert "51.2" in prov["reason"] or "truncated" in prov["reason"].lower()


def test_hierarchical_proposals_preserves_level4_children():
    """
    Verifies the hierarchical proposal invariant: Level 4 single-line proposals
    exist and are not eliminated by Level 5 multiline grouping.
    """
    p002_path = (
        REPO_ROOT / "DATASETS" / "structural_preservation"
        / "1505.05770_hierarchical_proposals_p002.json"
    )
    assert p002_path.exists()
    with open(p002_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    props = data["level4_level5_proposals"]
    l4_props = [p for p in props if p["hierarchy_level"] == 4]
    l5_props = [p for p in props if p["hierarchy_level"] == 5]

    assert len(l4_props) > 0, "No Level 4 single-line proposals found"
    assert len(l5_props) > 0, "No Level 5 multiline proposals found"

    # Verify Equation (3) GS-005 is preserved as an L4 proposal
    gs5_match = [p for p in l4_props if "≥−" in p["text"] and "(3)" in p["text"]]
    assert len(gs5_match) == 1, f"Expected GS-005 proposal in Level 4; found {len(gs5_match)}"


def test_frozen_boundary_manifest_hashes_match_disk():
    """
    Verifies that the frozen boundary manifest exists and its recorded hashes
    match the actual files on disk for the classifier, proposal generator, and evaluator.
    """
    import hashlib
    manifest_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "layer_ab_frozen_boundary_manifest.json"
    assert manifest_path.exists()
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for comp_name, comp_info in data["frozen_components"].items():
        comp_file = REPO_ROOT / comp_info["path"]
        assert comp_file.exists(), f"Component file missing: {comp_file}"
        h = hashlib.sha256()
        with open(comp_file, "rb") as f:
            for chunk in iter(lambda: f.read(1048576), b""):
                h.update(chunk)
        actual_hash = h.hexdigest()
        assert actual_hash == comp_info["sha256"], (
            f"Hash mismatch for {comp_name}: expected {comp_info['sha256']}, got {actual_hash}"
        )


def test_independent_validation_2102_preserves_equations_without_missing():
    """
    Verifies the independent validation results on 2102.03334:
    - Zero equations are classified as MISSING.
    - Negative control invariant is UPHELD (100% rejection rate).
    """
    eval_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "2102.03334_three_fidelity_evaluation.json"
    assert eval_path.exists()
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["equations_evaluated"] == 6
    assert data["structural_verdicts"]["MISSING"] == 0
    assert data["negative_control_verification"]["invariant_status"] == "UPHELD"
    assert data["negative_control_verification"]["rejection_rate"] == 1.0


def test_layer_b1_structural_completeness_audit_artifact_integrity():
    """
    Verifies the integrity of the Layer B.1 structural completeness audit JSON artifact:
    - All 6 equations audited in priority order.
    - All 6 diagnostic dimensions populated for each equation.
    - Layer ownership attributed.
    - Frozen detector status confirmed.
    """
    audit_path = (
        REPO_ROOT / "DATASETS" / "structural_preservation"
        / "2102.03334_structural_completeness_audit.json"
    )
    assert audit_path.exists(), f"Audit file missing: {audit_path}"
    with open(audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "1.0"
    assert data["audit_document"] == "2102.03334"
    assert data["audit_page"] == 4
    assert data["detector_frozen_status"]["font_aware_classifier_frozen"] is True
    assert data["detector_frozen_status"]["hierarchical_generator_frozen"] is True
    assert data["detector_frozen_status"]["two_population_invariant"] == "UPHELD"
    assert data["detector_frozen_status"]["negative_control_rejection_rate"] == 1.0

    eqs = data["equations_audited"]
    assert len(eqs) == 6

    # Verify priority sequence: VILT-004, 006, 005, 003, 002, 001
    priorities = [e["gold_id"] for e in sorted(eqs, key=lambda x: x["audit_priority"])]
    assert priorities == ["VILT-004", "VILT-006", "VILT-005", "VILT-003", "VILT-002", "VILT-001"]

    required_dimensions = [
        "missing_glyphs",
        "incorrect_glyph_interpretation",
        "incorrect_grouping",
        "incorrect_mathematical_relationships",
        "bounding_box_exclusion",
        "evaluation_manifest_omissions",
    ]

    for eq in eqs:
        diag = eq["diagnostic_analysis"]
        for dim in required_dimensions:
            assert dim in diag, f"Equation {eq['gold_id']} missing dimension {dim}"
            assert "status" in diag[dim], f"Equation {eq['gold_id']} missing status in {dim}"
        assert "layer_ownership_attribution" in eq
        assert "primary_owner" in eq["layer_ownership_attribution"]


def test_equation_number_metadata_contract_formalization():
    """
    Verifies that docs/spatial-syntactic-preservation-specification.md contains
    the formalized Section 10 on the Equation-Number Metadata Contract and Dual-Bounding-Box Specification.
    """
    spec_path = REPO_ROOT / "docs" / "spatial-syntactic-preservation-specification.md"
    assert spec_path.exists()
    content = spec_path.read_text(encoding="utf-8")

    assert "## 10. Equation-Number Metadata Contract and Dual-Bounding-Box Specification" in content
    assert "math_expression_bbox" in content
    assert "equation_number_bbox" in content
    assert "full_row_bbox" in content
    assert "Substring Check Disqualification" in content


def test_independent_validation_1406_gans_evaluation():
    """
    Verifies the independent positive-control validation on Paper C (1406.2661, GANs):
    - 4 equations evaluated across Pages 3, 4, 5.
    - Zero equations classified as MISSING.
    - GAN-006 achieves near-perfect spatial overlap (IoU > 0.95) under math_expression_bbox.
    - Mean math expression IoU exceeds 0.60.
    - Negative control invariant is UPHELD (100% rejection rate).
    """
    eval_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "1406.2661_three_fidelity_evaluation.json"
    assert eval_path.exists(), f"Evaluation file missing: {eval_path}"
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["equations_evaluated"] == 4
    assert data["structural_verdicts"]["MISSING"] == 0
    assert data["structural_verdicts"]["PRESERVED"] >= 3
    assert data["mean_math_expression_iou"] >= 0.60
    assert data["negative_control_verification"]["invariant_status"] == "UPHELD"
    assert data["negative_control_verification"]["rejection_rate"] == 1.0

    # Verify GAN-006 high-fidelity capture
    gan6 = next(r for r in data["per_equation_results"] if r["gold_id"] == "GAN-006")
    spat6 = gan6["dimension2_spatial_fidelity"]
    assert spat6["math_expression_iou"] >= 0.95
    assert gan6["dimension3_structural_fidelity"]["verdict"] == "PRESERVED"


def test_layer_b2_unified_evaluation_scoreboard():
    """
    Verifies the Layer B.2 unified evaluation scoreboard across all three positive populations:
    - 15 total equations evaluated.
    - Detection recall is 100% (15/15), zero equations MISSING.
    - VILT-001 is reclassified to PARTIAL upon eliminating bare numeral '1' substring check.
    - Structural completeness is strictly decoupled from detection recall.
    - Negative control invariant is UPHELD (15/15 rejected).
    - Frozen component hashes are verified intact.
    """
    unified_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "unified_layer_b2_evaluation.json"
    assert unified_path.exists(), f"Unified evaluation file missing: {unified_path}"
    with open(unified_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Scoreboard checks
    sb = data["scoreboard_overview"]
    assert sb["total_positive_populations"] == 3
    assert sb["total_equations_evaluated"] == 15
    assert sb["total_equations_detected"] == 15
    assert sb["detection_recall"] == 1.0
    assert sb["total_equations_missing"] == 0

    # 2. Frozen baseline integrity
    for comp, info in data["frozen_baseline_verification"].items():
        assert info["frozen_intact"] is True, f"Frozen component modified: {comp}"

    # 3. Negative control invariant
    assert data["negative_control_verification"]["invariant_status"] == "UPHELD"
    assert data["negative_control_verification"]["rejection_rate"] == 1.0

    # 4. Populations integrity
    pops = data["populations"]
    assert "1505.05770" in pops
    assert "2102.03334" in pops
    assert "1406.2661" in pops

    # Verify ViLT reclassification
    assert pops["2102.03334"]["structural_verdicts"]["PARTIAL"] == 6
    assert pops["2102.03334"]["structural_verdicts"]["PRESERVED"] == 0
    assert pops["2102.03334"]["structural_verdicts"]["MISSING"] == 0


def test_layer_c_comparison_evaluation_artifact_integrity():
    """
    Verifies Layer C (v3.0) vs Layer B (v2.0) comparison evaluation:
    - 15 total equations evaluated across all 3 positive populations.
    - Zero regressions: REGRESSED == 0 across all equations.
    - At least 6 equations improved: IMPROVED >= 6.
    - Fully preserved equations jumped from 7/15 (46.7%) in v2 to 10/15 (66.7%) in v3.
    - Negative control invariant remains 100% rejected (15/15).
    - Acceptance criteria gate is PASSED.
    """
    eval_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "v2_v3_comparison_evaluation.json"
    assert eval_path.exists(), f"Comparison evaluation file missing: {eval_path}"
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sb = data["scoreboard_overview"]
    assert sb["total_equations_evaluated"] == 15
    assert sb["v2_fully_preserved_count"] == 7
    assert sb["v3_fully_preserved_count"] >= 10
    assert sb["per_equation_verdicts"]["REGRESSED"] == 0
    assert sb["per_equation_verdicts"]["IMPROVED"] >= 6
    assert sb["negative_control_rejection_rate"] == 1.0
    assert sb["negative_control_status"] == "UPHELD"
    assert sb["acceptance_criteria_gate"] == "PASSED"


def test_layer_c_acceptance_criteria_ac1_through_ac7():
    """
    Verifies that all 7 acceptance criteria (AC-1 through AC-7) are marked SATISFIED
    in the comparison evaluation record.
    """
    eval_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "v2_v3_comparison_evaluation.json"
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ac = data["acceptance_criteria_verification"]
    assert len(ac) == 7
    for ac_key, ac_info in ac.items():
        assert ac_info["status"] == "SATISFIED", f"Acceptance criterion not satisfied: {ac_key}"


def test_layer_c_vilt_structural_preservation_and_subscript_recovery():
    """
    Verifies that Layer C adaptive baseline tolerance (AC-1) recovers scripts and restores
    structural preservation on the ViLT population:
    - VILT-001, VILT-002, and VILT-003 achieved PRESERVED verdict.
    - Math expression IoU exceeds 0.99 on VILT-001, VILT-002, and VILT-003.
    - Contributing structural provenance is attached to every candidate proposal.
    """
    eval_path = REPO_ROOT / "DATASETS" / "structural_preservation" / "v2_v3_comparison_evaluation.json"
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    per_eq = {r["gold_id"]: r for r in data["per_equation_comparison"]}

    # VILT-001
    v1 = per_eq["VILT-001"]["candidate_v3"]
    assert v1["structural_verdict"] == "PRESERVED"
    assert v1["math_expression_iou"] >= 0.99
    assert v1["has_structural_provenance"] is True
    assert "pos" in v1["extracted_text"]

    # VILT-002
    v2 = per_eq["VILT-002"]["candidate_v3"]
    assert v2["structural_verdict"] == "PRESERVED"
    assert v2["math_expression_iou"] >= 0.99
    assert v2["has_structural_provenance"] is True
    assert "pos" in v2["extracted_text"]

    # VILT-003
    v3 = per_eq["VILT-003"]["candidate_v3"]
    assert v3["structural_verdict"] == "PRESERVED"
    assert v3["math_expression_iou"] >= 0.99
    assert v3["has_structural_provenance"] is True







