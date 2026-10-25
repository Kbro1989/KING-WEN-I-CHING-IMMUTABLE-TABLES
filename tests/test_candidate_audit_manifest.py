#!/usr/bin/env python3
"""
Test Suite for Candidate Audit Manifest
=======================================
Verifies that the PDF crop audit manifest correctly verifies all 21 candidate
crops against the source papers.
"""
import sys
from pathlib import Path
import pytest  # type: ignore[import-not-found]

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    from scripts.audit_candidate_crops import run_audit, MANIFEST_PATH, _compute_token_overlap
    from scripts.experiments_multi_paper_generalization import REPORT_MD, OUTPUT_DIR
except ImportError:
    from audit_candidate_crops import run_audit, MANIFEST_PATH, _compute_token_overlap  # type: ignore[import-not-found]
    from experiments_multi_paper_generalization import REPORT_MD, OUTPUT_DIR  # type: ignore[import-not-found]


# ===========================================================================
# Unit tests for _compute_token_overlap
# These test the exact failure modes the reviewer identified.
# ===========================================================================

def test_token_overlap_all_matched():
    """All tokens present in order -> fraction 1.0, nothing missing."""
    # Source tokens: 'bn', '∑', 'ak'
    # Clip must contain all three in left-to-right order.
    result = _compute_token_overlap("bn = ∑ ak", "bn ∑ ak extra text")
    assert result['overlap_fraction'] == 1.0
    assert result['missing'] == []
    assert 'bn' in result['matched']
    assert '∑' in result['matched']
    assert 'ak' in result['matched']


def test_token_overlap_repeated_character_requires_repeated_occurrences():
    """A token that appears N times in source must appear N times in clip.

    The old character-set membership check would have falsely reported 'k' as
    matched three times even if clip contained only one 'k'. The ordered
    consumption-aware algorithm must correctly fail when occurrences are exhausted.
    """
    # Source has 'k' three times: 'k', 'k', 'k' (as tokens ['k', 'k', 'k'])
    # clip_text has only one 'k' -> second and third 'k' are missing
    result = _compute_token_overlap("k k k", "one k here")
    assert result['tokens'] == ['k', 'k', 'k']
    # First 'k' matched, second and third cannot (consumed)
    assert len(result['matched']) == 1
    assert len(result['missing']) == 2
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_reordered_tokens_counted_as_partial():
    """LCS alignment cannot match both tokens when they appear in opposite order.

    Source order: 'bn' first, then 'ak'.
    Clip order:   'ak' first, then 'bn'.

    LCS of ['bn', 'ak'] and ['ak', 'bn'] has length 1.  The backtracker
    (prefer 'go up') recovers 'bn' as the single matched token.  'ak' is
    missing because it would require reversing the source order.
    """
    result = _compute_token_overlap("bn ak", "ak bn")
    assert result['algorithm'] == 'lcs'
    assert result['lcs_length'] == 1
    assert 'bn' in result['matched']
    assert 'ak' in result['missing']
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_empty_source():
    """Empty source_text must return zero tokens and fraction 0.0."""
    result = _compute_token_overlap("", "some clip text")
    assert result['tokens'] == []
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_empty_clip():
    """Non-empty source against empty clip must report all tokens missing."""
    result = _compute_token_overlap("ζ(ℓ+1)", "")
    assert len(result['missing']) == len(result['tokens'])
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_unicode_symbols():
    """Non-ASCII math symbols (∑, ζ, ∇) are extracted as individual tokens."""
    result = _compute_token_overlap("ζ(ℓ+1) v", "ζ(ℓ+1) v extra")
    # Expected tokens: 'ζ', 'ℓ', '1', 'v'  (non-ASCII chars + alnum runs)
    assert 'ζ' in result['tokens']
    assert 'v' in result['tokens']
    assert result['overlap_fraction'] == 1.0


def test_token_overlap_missing_symbol():
    """A missing Unicode symbol registers as a missing token."""
    result = _compute_token_overlap("∑ ak", "ak only no sum")
    assert '∑' in result['missing']
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_whole_token_boundary_no_substring_collision():
    """Whole-token matching: 'ak' must not match inside 'bakz' or 'bakk'."""
    result = _compute_token_overlap("ak", "bakz and bakk")
    assert result['matched'] == []
    assert result['missing'] == ['ak']
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_lcs_order_preservation():
    """Source ['a', 'b', 'c'] against clip 'c b' has LCS length 1, not matching both out-of-order."""
    result = _compute_token_overlap("a b c", "c b")
    assert result['algorithm'] == 'lcs'
    assert result['lcs_length'] == 1
    assert len(result['matched']) == 1
    assert len(result['missing']) == 2
    assert abs(result['overlap_fraction'] - 1 / 3) < 1e-6


def test_token_overlap_adjacent_unicode_symbols():
    """Adjacent Unicode math symbols are treated as distinct tokens."""
    result = _compute_token_overlap("∇∑x", "∇ ∑ x")
    assert result['tokens'] == ['∇', '∑', 'x']
    assert result['overlap_fraction'] == 1.0
    assert result['missing'] == []




def test_audit_manifest_all_21_candidates_pass():
    manifest = run_audit(save_manifest=False)
    assert manifest['total_candidates'] == 21
    # Renamed fields: distinguish metadata-assertion completion from text-verification
    assert manifest['metadata_assertions_passed'] == 21
    assert manifest['all_metadata_assertions_passed'] is True
    assert len(manifest['records']) == 21
    # Per-status counts must be present and consistent
    verified  = manifest['pdf_text_overlap_verified_count']
    partial   = manifest['pdf_text_overlap_partial_count']
    meta_only = manifest['metadata_assertions_only_count']
    review_required = manifest['human_visual_review_required_count']
    assert verified + partial + meta_only == 21
    assert review_required == partial + meta_only
    # At least some candidates should have text-extraction confirmation
    assert verified > 0, 'Expected at least one pdf_text_overlap_verified candidate'

    VALID_AUDIT_STATUSES = {
        'pdf_text_overlap_verified',
        'pdf_text_overlap_partial',
        'metadata_assertions_only',
    }
    for rec in manifest['records']:
        assert rec['machine_assertions_passed'] is True
        assert rec['reference_latex'] != ''
        assert rec['crop_scope'] in ['complete', 'partial']
        assert 'left' in rec['expected_boundary']
        assert 'right' in rec['expected_boundary']
        assert rec['audit_status'] in VALID_AUDIT_STATUSES, (
            f"{rec['candidate_id']}: unexpected audit_status {rec['audit_status']!r}"
        )
        # Three-tier model requires evidence_notes explaining what was and was not verified
        assert 'evidence_notes' in rec, f"{rec['candidate_id']}: missing evidence_notes"
        assert rec['evidence_notes'], f"{rec['candidate_id']}: evidence_notes is empty"


def test_manifest_file_exists_and_valid():
    assert MANIFEST_PATH.exists()
    import json
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data['total_candidates'] == 21
    # Renamed field from all_assertions_passed -> all_metadata_assertions_passed
    assert data['all_metadata_assertions_passed'] is True
    assert data['manifest_version'] == '2.0'
    # Per-status count fields must be present
    for field in (
        'pdf_text_overlap_verified_count',
        'pdf_text_overlap_partial_count',
        'metadata_assertions_only_count',
        'human_visual_review_required_count',
    ):
        assert field in data, f'Manifest missing field: {field}'


def test_generated_report_table_column_integrity():
    """Verify that every row in every table in REPORT_MD has the expected column count."""
    import re
    assert REPORT_MD.exists()
    content = REPORT_MD.read_text(encoding='utf-8')

    tables = re.findall(r'(\|[^\n]+\|\n\|[\s:\-|]+\|\n(?:\|[^\n]+\|\n?)+)', content)
    assert len(tables) >= 4, f"Expected at least 4 markdown tables, found {len(tables)}"

    for idx, table in enumerate(tables):
        rows = [r.strip() for r in table.strip().split('\n') if r.strip().startswith('|')]
        header_cols = len(re.split(r'(?<!\\)\|', rows[0])[1:-1])
        assert header_cols >= 2, f"Table {idx+1} header has invalid columns: {header_cols}"

        for row_idx, row in enumerate(rows):
            # Split on unescaped pipe
            cols = re.split(r'(?<!\\)\|', row)[1:-1]
            assert len(cols) == header_cols, (
                f"Table {idx+1} row {row_idx} column mismatch: expected {header_cols}, got {len(cols)} in: {row}"
            )


def test_reported_file_hashes_match_committed_artifacts():
    """Verify that the SHA-256 hashes listed in the report match the actual artifact bytes."""
    import hashlib
    import re
    content = REPORT_MD.read_text(encoding='utf-8')

    # Extract SHA-256 hashes from section 5
    matches = re.findall(r'\[`([^`]+)`\]\(file:///[^)]+\) \(SHA-256: `([a-f0-9]{64})`\)', content)
    assert len(matches) >= 4, f"Expected at least 4 hashed artifacts in report, found {len(matches)}"

    for rel_path, expected_hash in matches:
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Report references non-existent artifact: {rel_path}"
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"

