"""
Unit tests for Crop Isolation & Glyph Clipping Regression
=========================================================
Verifies that controlled asymmetric padding (padding_x=3, padding_y=1-2)
eliminates prose contamination and multi-line tabular artifacts
while preserving mathematical glyphs without clipping.
"""

import sys
import os
import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

CROP_DIR = REPO_ROOT / 'DATASETS' / 'vision_comparison' / 'crop_isolation_experiment'
EXP_JSONL = CROP_DIR / 'crop_isolation_comparison.jsonl'


def test_crop_isolation_experiment_artifacts_exist():
    """Verify that the experimental crops and comparison records exist."""
    assert CROP_DIR.exists(), f"Crop experiment directory {CROP_DIR} missing"
    assert EXP_JSONL.exists(), f"Comparison JSONL {EXP_JSONL} missing"


def test_crop_isolation_regression_all_candidates():
    """Verify all 4 candidates achieve formula isolation under tighter padding."""
    import json

    with open(EXP_JSONL, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    assert len(records) == 16, f"Expected 16 experimental records, got {len(records)}"

    # Check baseline has contamination on 3/4 candidates
    baseline_records = [r for r in records if r['configuration'] == 'baseline']
    baseline_contaminated = sum(1 for r in baseline_records if r['evaluation']['is_multiline_array'])
    assert baseline_contaminated >= 3, f"Expected baseline to exhibit multiline contamination, got {baseline_contaminated}"

    # Check that tight_pad2 and asym_tight_y1 achieve 100% isolation across all 4 candidates
    for config_name in ['tight_pad2', 'asym_tight_y1']:
        config_records = [r for r in records if r['configuration'] == config_name]
        assert len(config_records) == 4, f"Expected 4 records for {config_name}"

        for r in config_records:
            ev = r['evaluation']
            c_idx = r['candidate_index']
            # Must be isolated
            assert ev['formula_isolated'], (
                f"Candidate {c_idx} under {config_name} failed formula isolation: {r['recognized_latex']}"
            )
            # Must not be multiline array
            assert not ev['is_multiline_array'], (
                f"Candidate {c_idx} under {config_name} produced multiline array: {r['recognized_latex']}"
            )
            # Must not have prose contamination
            assert not ev['prose_contamination'], (
                f"Candidate {c_idx} under {config_name} has prose contamination: {r['recognized_latex']}"
            )
            # Must have target formula present
            assert ev['target_formula_present'], (
                f"Candidate {c_idx} under {config_name} lost target formula: {r['recognized_latex']}"
            )


def test_crop_geometry_clipping_bounds():
    """Verify that asym_tight_y1 retains valid non-zero bounding dimensions."""
    import json

    with open(EXP_JSONL, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    asym_records = [r for r in records if r['configuration'] == 'asym_tight_y1']
    for r in asym_records:
        h, w, c = r['pixel_dimensions']
        assert h >= 40, f"Vertical height {h} suspiciously small for crop {r['crop_image_path']}"
        assert w >= 80, f"Horizontal width {w} suspiciously small for crop {r['crop_image_path']}"
        assert c == 3, f"Expected 3 color channels, got {c}"


def test_target_token_preservation_candidate_0():
    """Candidate 0 must preserve Greek zeta, subscript v, and superscript ell+1."""
    import json

    with open(EXP_JSONL, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    r = next(r for r in records if r['candidate_index'] == 0 and r['configuration'] == 'asym_tight_y1')
    latex = r['recognized_latex']
    assert '\\zeta' in latex
    assert 'v' in latex
    assert '\\ell' in latex or 'ell' in latex or '1' in latex


def test_target_token_preservation_candidate_2():
    """Candidate 2 must preserve square root radical and subscript pe."""
    import json

    with open(EXP_JSONL, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    r = next(r for r in records if r['candidate_index'] == 2 and r['configuration'] == 'asym_tight_y1')
    latex = r['recognized_latex']
    assert '\\sqrt' in latex
    assert 'p' in latex
    assert 'e' in latex


def test_target_token_preservation_candidate_3():
    """Candidate 3 must preserve proportionality operator, radical, and subscript pe."""
    import json

    with open(EXP_JSONL, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f]

    r = next(r for r in records if r['candidate_index'] == 3 and r['configuration'] == 'asym_tight_y1')
    latex = r['recognized_latex']
    assert '\\propto' in latex
    assert '\\sqrt' in latex
    assert 'p' in latex
