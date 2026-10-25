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
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    import pytest  # type: ignore[import-not-found]
except ImportError:
    pytest = None  # type: ignore[assignment]
try:
    from scripts.audit_candidate_crops import MANIFEST_PATH
    from scripts.experiments_multi_paper_generalization import OUTPUT_DIR, CANDIDATES
    from scripts.recompute_vision_evaluations import (
        recompute,
        resolve_active_generation,
        get_active_artifact,
        CANONICAL_FILES,
        CURRENT_POINTER_FILE,
    )
except ImportError:
    from audit_candidate_crops import MANIFEST_PATH  # type: ignore[import-not-found]
    from experiments_multi_paper_generalization import OUTPUT_DIR, CANDIDATES  # type: ignore[import-not-found]
    from recompute_vision_evaluations import (  # type: ignore[import-not-found]
        recompute,
        resolve_active_generation,
        get_active_artifact,
        CANONICAL_FILES,
        CURRENT_POINTER_FILE,
    )

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


def test_summary_reconciliation_exact_counts():
    """Derive headline counts directly from the 21 candidate records and compare against JSON & MD."""
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data['records']
    assert len(records) == 21, f"Expected 21 records, found {len(records)}"

    # Verify uniqueness of candidate IDs
    cids = [r['candidate_id'] for r in records]
    assert len(set(cids)) == 21, "Duplicate candidate IDs found in visual review log"
    expected_ids = [c['candidate_id'] for c in CANDIDATES]
    assert cids == expected_ids, "Candidate ID sequence does not match CANDIDATES list"

    # Derive counts directly from the candidate records
    glyph_passes = sum(1 for r in records if r['visual_glyph_fidelity']['status'] == 'PASS')
    glyph_non_passes = sum(1 for r in records if r['visual_glyph_fidelity']['status'] != 'PASS')
    struct_passes = sum(1 for r in records if r['mathematical_structure']['status'] == 'PASS')
    struct_non_passes = sum(1 for r in records if r['mathematical_structure']['status'] != 'PASS')
    bound_passes = sum(1 for r in records if r['crop_boundary_fidelity']['status'] == 'PASS')
    bound_non_passes = sum(1 for r in records if r['crop_boundary_fidelity']['status'] != 'PASS')

    # Frozen baseline verification
    assert glyph_passes == 19 and glyph_non_passes == 2, f"Glyph count mismatch: {glyph_passes}/{glyph_non_passes}"
    assert struct_passes == 19 and struct_non_passes == 2, f"Structure count mismatch: {struct_passes}/{struct_non_passes}"
    assert bound_passes == 10 and bound_non_passes == 11, f"Boundary count mismatch: {bound_passes}/{bound_non_passes}"

    # Verify against JSON summary block
    summary = data['summary']
    assert summary['glyph_fidelity_passes'] == glyph_passes
    assert summary['glyph_fidelity_non_passes'] == glyph_non_passes
    assert summary['structure_passes'] == struct_passes
    assert summary['structure_non_passes'] == struct_non_passes
    assert summary['boundary_passes'] == bound_passes
    assert summary['boundary_non_passes'] == bound_non_passes

    # Verify against Markdown summary table
    md_text = VISUAL_LOG_MD.read_text(encoding='utf-8')
    assert f"| **Visual Glyph Fidelity** | {glyph_passes}/21 | {glyph_non_passes} |" in md_text
    assert f"| **Mathematical Structure** | {struct_passes}/21 | {struct_non_passes} |" in md_text
    assert f"| **Crop Boundary Fidelity** | {bound_passes}/21 | {bound_non_passes} |" in md_text

    # Verify allowed verdicts set
    allowed_overall = {
        'CONFIRMED_ACCURATE',
        'NOTATION_AMBIGUITY',
        'INTENDED_PARTIAL_FRAGMENT',
        'BOUNDARY_AMBIGUITY',
        'BOUNDARY_TRUNCATION',
    }
    for r in records:
        assert r['overall_visual_verdict'] in allowed_overall, f"Disallowed verdict: {r['overall_visual_verdict']}"


def test_stirling_eq1_1_notation_and_equivalence_annotations():
    """Verify 1212_0957_eq1.1 separates literal notation match from mathematical equivalence."""
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rec = next((r for r in data['records'] if r['candidate_id'] == '1212_0957_eq1.1_forward_summation'), None)
    assert rec is not None, "Candidate 1212_0957_eq1.1 not found"

    # Verify explicit notation & equivalence annotations
    assert rec.get('literal_notation_match') is False
    assert rec.get('mathematical_equivalence') is True
    assert 'benchmark_evaluation_note' in rec
    assert len(rec['benchmark_evaluation_note']) > 0

    # Verify original observation and verdict intact
    assert rec['overall_visual_verdict'] == 'NOTATION_AMBIGUITY'
    assert rec['visual_glyph_fidelity']['status'] == 'DISCREPANCY_NOTED'
    assert rec['mathematical_structure']['status'] == 'PASS'
    assert 'Stirling' in rec['visual_glyph_fidelity']['details']


def test_correction_history_tracking():
    """Verify visual review log maintains versioned correction history."""
    with open(VISUAL_LOG_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data.get('audit_version') == '2.1'
    history = data.get('correction_history', [])
    assert len(history) >= 2
    versions = [h['version'] for h in history]
    assert '2.0' in versions
    assert '2.1' in versions


def test_atomic_generation_resolution_and_integrity(tmp_path):
    """Verify generation directory structure, CURRENT pointer resolution, and digest integrity."""
    res = recompute(output_dir=tmp_path)
    assert 'generation_id' in res
    assert 'artifact_digests' in res

    pointer_file = tmp_path / 'CURRENT.json'
    assert pointer_file.exists(), "Missing CURRENT.json pointer file"
    with open(pointer_file, 'r', encoding='utf-8') as f:
        pointer_data = json.load(f)

    assert pointer_data['generation_id'] == res['generation_id']
    active_gen = resolve_active_generation(output_dir=tmp_path)
    assert active_gen.exists()
    assert active_gen.name == res['generation_id']

    # All canonical artifacts must exist in active generation with matching hashes
    for fname in CANONICAL_FILES:
        art_path = get_active_artifact(fname, output_dir=tmp_path)
        assert art_path.exists(), f"Active artifact missing: {fname}"
        actual_hash = hashlib.sha256(art_path.read_bytes()).hexdigest()
        assert actual_hash == pointer_data['artifact_digests'][fname], f"Hash mismatch for {fname}"

    # Staging directories must not linger
    staging_dirs = list(tmp_path.glob('.staging_*'))
    assert len(staging_dirs) == 0, f"Leftover staging directories found: {staging_dirs}"


def test_repository_published_generation():
    """Verify repository has a valid active generation referenced by CURRENT.json."""
    assert CURRENT_POINTER_FILE.exists(), "Missing CURRENT.json in repository"
    with open(CURRENT_POINTER_FILE, 'r', encoding='utf-8') as f:
        pointer_data = json.load(f)
    active_gen = resolve_active_generation()
    assert active_gen.exists(), f"Active generation directory missing: {active_gen}"
    for fname in CANONICAL_FILES:
        art_path = get_active_artifact(fname)
        assert art_path.exists(), f"Missing artifact {fname}"
        assert hashlib.sha256(art_path.read_bytes()).hexdigest() == pointer_data['artifact_digests'][fname]


def test_failure_injection_staging_write_error(tmp_path):
    """Verify failure during staging write aborts cleanly without altering previous generation."""
    # 1. Establish baseline generation in isolated tmp_path
    res1 = recompute(output_dir=tmp_path)
    initial_gen_id = res1['generation_id']
    initial_pointer = (tmp_path / 'CURRENT.json').read_text(encoding='utf-8')
    initial_file_bytes = {f: (tmp_path / f).read_bytes() for f in CANONICAL_FILES}

    # 2. Inject staging-write failure
    with pytest.raises(IOError, match="Simulated failure during staging write"):
        recompute(output_dir=tmp_path, failure_injection_point='fail_staging_write')

    # 3. Assert prior generation remained intact, readable, and byte-identical
    assert list(tmp_path.glob('.staging_*')) == [], "Staging directory was not cleaned up on staging failure"
    assert (tmp_path / 'CURRENT.json').read_text(encoding='utf-8') == initial_pointer
    for f in CANONICAL_FILES:
        assert (tmp_path / f).read_bytes() == initial_file_bytes[f], f"Canonical file {f} modified after failure"

    active_gen = resolve_active_generation(output_dir=tmp_path)
    assert active_gen.name == initial_gen_id


def test_failure_injection_validation_error(tmp_path):
    """Verify failure during staging validation aborts cleanly without altering previous generation."""
    # 1. Establish baseline generation in isolated tmp_path
    res1 = recompute(output_dir=tmp_path)
    initial_gen_id = res1['generation_id']
    initial_pointer = (tmp_path / 'CURRENT.json').read_text(encoding='utf-8')
    initial_file_bytes = {f: (tmp_path / f).read_bytes() for f in CANONICAL_FILES}

    # 2. Inject validation failure
    with pytest.raises(AssertionError, match="Simulated validation failure on staged generation"):
        recompute(output_dir=tmp_path, failure_injection_point='fail_validation')

    # 3. Assert prior generation remained intact and byte-identical
    assert list(tmp_path.glob('.staging_*')) == [], "Staging directory was not cleaned up on validation failure"
    assert (tmp_path / 'CURRENT.json').read_text(encoding='utf-8') == initial_pointer
    for f in CANONICAL_FILES:
        assert (tmp_path / f).read_bytes() == initial_file_bytes[f], f"Canonical file {f} modified after failure"

    active_gen = resolve_active_generation(output_dir=tmp_path)
    assert active_gen.name == initial_gen_id


def test_failure_injection_publish_pointer_error(tmp_path):
    """Verify failure before pointer switch leaves prior active generation active."""
    # 1. Establish baseline generation in isolated tmp_path
    res1 = recompute(output_dir=tmp_path)
    initial_gen_id = res1['generation_id']
    initial_pointer = (tmp_path / 'CURRENT.json').read_text(encoding='utf-8')
    initial_file_bytes = {f: (tmp_path / f).read_bytes() for f in CANONICAL_FILES}

    # 2. Inject failure before pointer replacement
    with pytest.raises(IOError, match="Simulated failure before atomic pointer switch"):
        recompute(output_dir=tmp_path, failure_injection_point='fail_publish_pointer')

    # 3. Assert pointer still points to prior generation and canonical files unchanged
    assert (tmp_path / 'CURRENT.json').read_text(encoding='utf-8') == initial_pointer
    for f in CANONICAL_FILES:
        assert (tmp_path / f).read_bytes() == initial_file_bytes[f], f"Canonical file {f} modified after failure"

    active_gen = resolve_active_generation(output_dir=tmp_path)
    assert active_gen.name == initial_gen_id


def test_failure_injection_canonical_sync_rollback(tmp_path):
    """Verify failure during canonical file synchronization triggers rollback to prior files."""
    # 1. Establish baseline generation in isolated tmp_path
    res1 = recompute(output_dir=tmp_path)
    initial_gen_id = res1['generation_id']
    initial_pointer = (tmp_path / 'CURRENT.json').read_text(encoding='utf-8')
    initial_file_bytes = {f: (tmp_path / f).read_bytes() for f in CANONICAL_FILES}

    # 2. Inject failure during canonical file copy
    with pytest.raises(IOError, match="Simulated failure during canonical file synchronization"):
        recompute(output_dir=tmp_path, failure_injection_point='fail_canonical_sync')

    # 3. Assert rollback restored every canonical file byte-for-byte
    for f in CANONICAL_FILES:
        assert (tmp_path / f).read_bytes() == initial_file_bytes[f], f"Rollback failed for canonical file {f}"

    # 4. Assert pointer was restored to prior generation
    assert (tmp_path / 'CURRENT.json').read_text(encoding='utf-8') == initial_pointer
    active_gen = resolve_active_generation(output_dir=tmp_path)
    assert active_gen.name == initial_gen_id
