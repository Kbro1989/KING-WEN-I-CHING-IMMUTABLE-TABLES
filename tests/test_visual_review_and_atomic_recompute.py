#!/usr/bin/env python3
"""
Unit tests for 21-candidate Visual Review Audit Log and Atomic Recomputation.
Validates:
1. Three-axis independent judgments (Visual glyph fidelity, Mathematical structure, Crop-boundary fidelity).
2. Presence and validity of render image artifacts for all 21 candidates.
3. Verification of 2104_01277_cand8_summation_lambda operator identity (big union, not summation).
4. Preservation of pdf_text_overlap_partial status for 1212_0957 Stirling expressions.
5. Atomic recomputation staging and error abort semantics.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    from scripts.audit_candidate_crops import MANIFEST_PATH
    from scripts.experiments_multi_paper_generalization import OUTPUT_DIR, CANDIDATES
    from scripts.recompute_vision_evaluations import recompute
except ImportError:
    from audit_candidate_crops import MANIFEST_PATH  # type: ignore[import-not-found]
    from experiments_multi_paper_generalization import OUTPUT_DIR, CANDIDATES  # type: ignore[import-not-found]
    from recompute_vision_evaluations import recompute  # type: ignore[import-not-found]

VISUAL_LOG_JSON = OUTPUT_DIR / 'visual_review_audit_log.json'
VISUAL_LOG_MD = OUTPUT_DIR / 'visual_review_audit_log.md'
RENDERS_DIR = OUTPUT_DIR / 'candidate_visual_audit_renders'


def test_visual_review_log_exists_and_reconciles():
    assert VISUAL_LOG_JSON.exists(), f"Missing {VISUAL_LOG_JSON}"
    assert VISUAL_LOG_MD.exists(), f"Missing {VISUAL_LOG_MD}"

    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data['total_candidates_audited'] == 21
    assert len(data['records']) == 21

    candidate_ids = [r['candidate_id'] for r in data['records']]
    expected_ids = [c['candidate_id'] for c in CANDIDATES]
    assert candidate_ids == expected_ids, "Candidate ID mismatch between visual log and CANDIDATES"


def test_three_axis_independent_judgments_per_candidate():
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    valid_glyph_statuses = {'PASS', 'DISCREPANCY_NOTED', 'TRUNCATION_NOTED'}
    valid_struct_statuses = {'PASS', 'PARTIAL_CONTEXT'}
    valid_boundary_statuses = {'PASS', 'BOUNDARY_TOUCH', 'BOUNDARY_CLIPPED', 'LEAKAGE_NOTED'}

    for r in data['records']:
        cid = r['candidate_id']
        # Axis 1: Visual glyph fidelity
        assert 'visual_glyph_fidelity' in r, f"{cid} missing visual_glyph_fidelity"
        assert r['visual_glyph_fidelity']['status'] in valid_glyph_statuses, f"{cid} invalid glyph status"
        assert len(r['visual_glyph_fidelity']['details']) > 0

        # Axis 2: Mathematical structure
        assert 'mathematical_structure' in r, f"{cid} missing mathematical_structure"
        assert r['mathematical_structure']['status'] in valid_struct_statuses, f"{cid} invalid struct status"
        assert len(r['mathematical_structure']['details']) > 0

        # Axis 3: Crop-boundary fidelity
        assert 'crop_boundary_fidelity' in r, f"{cid} missing crop_boundary_fidelity"
        assert r['crop_boundary_fidelity']['status'] in valid_boundary_statuses, f"{cid} invalid boundary status"
        assert len(r['crop_boundary_fidelity']['details']) > 0

        # Overall verdict must be specified
        assert 'overall_visual_verdict' in r


def test_render_image_artifacts_exist_for_all_candidates():
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for r in data['records']:
        cid = r['candidate_id']
        crop_path = OUTPUT_DIR / r['render_path']
        context_path = OUTPUT_DIR / r['context_render_path']

        assert crop_path.exists(), f"Missing crop render for {cid}: {crop_path}"
        assert context_path.exists(), f"Missing context render for {cid}: {context_path}"
        assert crop_path.stat().st_size > 0
        assert context_path.stat().st_size > 0


def test_cand8_operator_is_big_union_not_summation():
    """Verify 2104_01277_cand8_summation_lambda is confirmed as union \\cup / \\bigcup, not \\sum."""
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cand8 = next((r for r in data['records'] if r['candidate_id'] == '2104_01277_cand8_summation_lambda'), None)
    assert cand8 is not None, "Candidate 8 record not found"

    glyph_details = cand8['visual_glyph_fidelity']['details']
    assert 'UNION' in glyph_details or 'union' in glyph_details
    assert 'NOT a summation' in glyph_details
    assert cand8['declared_reference_latex'].startswith(r'\cup')
    assert cand8['overall_visual_verdict'] == 'CONFIRMED_ACCURATE'


def test_stirling_candidates_preserve_partial_text_status():
    """Verify 1212.0957 Stirling candidates retain pdf_text_overlap_partial without promotion."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    eq1_1 = next((c for c in manifest['records'] if c['candidate_id'] == '1212_0957_eq1.1_forward_summation'), None)
    eq1_2 = next((c for c in manifest['records'] if c['candidate_id'] == '1212_0957_eq1.2_inverse_summation'), None)

    assert eq1_1 is not None
    assert eq1_2 is not None
    assert eq1_1['audit_status'] == 'pdf_text_overlap_partial'
    assert eq1_2['audit_status'] == 'pdf_text_overlap_partial'

    # Check that in visual audit log they note the typographic and encoding reasons
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        vlog = json.load(f)

    v_eq1_1 = next((r for r in vlog['records'] if r['candidate_id'] == '1212_0957_eq1.1_forward_summation'), None)
    assert 'Stirling' in v_eq1_1['visual_glyph_fidelity']['details']
    assert v_eq1_1['overall_visual_verdict'] == 'NOTATION_AMBIGUITY'


def test_atomic_recomputation_staging_safety():
    """Verify recomputation imports and staging logic validate counts and preserve snapshots."""
    # recompute() is designed to run idempotently with atomic swap
    recompute()

    # Staging directory must be cleaned up after successful completion
    stage_dir = OUTPUT_DIR / '.staging'
    assert not stage_dir.exists(), "Staging directory was not cleaned up after atomic publication"

    # Prior snapshot directory must exist
    snapshot_dir = OUTPUT_DIR / '.snapshot_prior'
    assert snapshot_dir.exists(), "Snapshot directory was not created"
