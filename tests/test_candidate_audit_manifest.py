#!/usr/bin/env python3
"""
Test Suite for Candidate Audit Manifest
=======================================
Verifies that the PDF crop audit manifest correctly verifies all 21 candidate
crops against the source papers.
"""
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

from audit_candidate_crops import run_audit, MANIFEST_PATH


def test_audit_manifest_all_21_candidates_pass():
    manifest = run_audit(save_manifest=False)
    assert manifest['total_candidates'] == 21
    assert manifest['passed_assertions'] == 21
    assert manifest['all_assertions_passed'] is True
    assert len(manifest['records']) == 21

    for rec in manifest['records']:
        assert rec['machine_assertions_passed'] is True
        assert rec['reference_latex'] != ''
        assert rec['crop_scope'] in ['complete', 'partial']
        assert 'left' in rec['expected_boundary']
        assert 'right' in rec['expected_boundary']
        assert rec['audit_status'] in ['verified_pdf_match', 'manual_review_verified']


def test_manifest_file_exists_and_valid():
    assert MANIFEST_PATH.exists()
    import json
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data['total_candidates'] == 21
    assert data['all_assertions_passed'] is True


def test_generated_report_table_column_integrity():
    """Verify that every row in every table in REPORT_MD has the expected column count."""
    import re
    from experiments_multi_paper_generalization import REPORT_MD
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
    from experiments_multi_paper_generalization import REPORT_MD, OUTPUT_DIR
    content = REPORT_MD.read_text(encoding='utf-8')

    # Extract SHA-256 hashes from section 5
    matches = re.findall(r'\[`([^`]+)`\]\(file:///[^)]+\) \(SHA-256: `([a-f0-9]{64})`\)', content)
    assert len(matches) >= 4, f"Expected at least 4 hashed artifacts in report, found {len(matches)}"

    for rel_path, expected_hash in matches:
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Report references non-existent artifact: {rel_path}"
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"

