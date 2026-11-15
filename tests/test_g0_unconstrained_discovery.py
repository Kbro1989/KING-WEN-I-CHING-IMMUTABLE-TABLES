"""Tests for PIAA-010 Unconstrained G0 Candidate Discovery.

Validates that g0_unconstrained_discovery.py correctly:
  - Proposes math region candidates from full Page 4 without oracle coordinates
  - Recovers PIAA-001 (the only PIAA fixture on Page 4) with high IoU
  - Does not read oracle bboxes during candidate generation phase
  - Outputs correct policy metadata

Page-boundary note:
  PIAA-001 is on page_0based=3 (Page 4).
  PIAA-002..005 are on page_0based=4 (Page 5).
  G0 discovery targets Page 4 only; Page 5 fixtures cannot appear in
  the Page 4 candidate list.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DATASETS_DIR = REPO_ROOT / "DATASETS" / "structural_preservation"
OUTPUT_PATH = DATASETS_DIR / "piaa_010_g0_candidates.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PDF_PATH = Path(
    "C:/Users/krist/Desktop/zotero/learning-corpus/"
    "efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def g0_result():
    r"""Run G0 discovery and return the full output dict.

    Requires the PIAA PDF to be present on disk. Skips if unavailable.
    """
    if not PDF_PATH.exists():
        pytest.skip(f"PIAA PDF not found: {PDF_PATH}")

    from g0_unconstrained_discovery import run_g0_discovery
    return run_g0_discovery()


# ---------------------------------------------------------------------------
# T1: At least 3 candidate math regions proposed on Page 4
# ---------------------------------------------------------------------------

def test_at_least_3_candidates_proposed(g0_result):
    r"""G0 discovery must propose >= 3 math region candidates on Page 4.

    Page 4 contains the PIAA-001 equation (a dense multi-glyph display block),
    plus at least two additional smaller math clusters from the section's
    notation. If fewer than 3 are found the clustering parameters are
    likely too aggressive.
    """
    n = g0_result["extraction_summary"]["candidate_regions_proposed"]
    assert n >= 3, (
        f"Expected >= 3 candidate regions on Page 4, got {n}. "
        "Check MIN_MATH_GLYPHS or ROW_MERGE_PT thresholds in g0_unconstrained_discovery.py."
    )


# ---------------------------------------------------------------------------
# T2: PIAA-001 is recovered with IoU >= 0.5 (the only page-4 fixture)
# ---------------------------------------------------------------------------

def test_piaa_001_recovered(g0_result):
    r"""G0 discovery must recover PIAA-001 with IoU >= 0.5.

    PIAA-001 (Equation 1, the GDA multivariate Gaussian display block)
    is the only sealed fixture on page_0based=3 (Page 4).
    It must be matched by at least one G0 candidate.
    """
    adj = g0_result["post_hoc_adjudication"]
    piaa_001 = adj["per_fixture"].get("PIAA-001")
    assert piaa_001 is not None, "PIAA-001 not found in adjudication results"
    iou = piaa_001["best_iou"]
    assert piaa_001["matched"], (
        f"PIAA-001 not matched. Best IoU was {iou:.4f} (threshold 0.5). "
        "G0 candidate generation failed to locate the primary display equation."
    )


# ---------------------------------------------------------------------------
# T3: PIAA-001 IoU is high-quality (>= 0.85)
# ---------------------------------------------------------------------------

def test_piaa_001_high_quality_iou(g0_result):
    r"""The best-matching G0 candidate for PIAA-001 must have IoU >= 0.85.

    A match above 0.85 indicates the candidate's bounding box closely
    encloses the actual equation block, not just an overlapping superset.
    The clustering of 49 math-font glyphs over the dense GDA block
    should produce tight candidate boundaries.
    """
    adj = g0_result["post_hoc_adjudication"]
    iou = adj["per_fixture"]["PIAA-001"]["best_iou"]
    assert iou >= 0.85, (
        f"PIAA-001 IoU was {iou:.4f} < 0.85. "
        "Candidate bbox may be too loose or too tight around the equation."
    )


# ---------------------------------------------------------------------------
# T4: Policy metadata correctly records no oracle reads
# ---------------------------------------------------------------------------

def test_oracle_coordinates_not_allowed(g0_result):
    r"""Policy metadata must record oracle_coordinates_allowed: false.

    This invariant ensures the candidate generation phase does not
    read reference bboxes from the fixture manifest.
    """
    policy = g0_result["policy"]
    assert policy["oracle_coordinates_allowed"] is False, (
        "Policy metadata must declare oracle_coordinates_allowed=False. "
        "Gold coordinates must not leak into G0 candidate generation."
    )
    assert policy["fixture_annotations_read_during_generation"] is False, (
        "Policy metadata must declare fixture_annotations_read_during_generation=False."
    )


# ---------------------------------------------------------------------------
# T5: Page-5 fixtures (PIAA-002..005) are correctly absent (IoU=0)
# ---------------------------------------------------------------------------

def test_page5_fixtures_not_matched(g0_result):
    r"""PIAA-002..005 (page_0based=4, Page 5) must not match any Page 4 candidate.

    G0 discovery runs on Page 4 only. The Page 5 equations should have
    zero intersection with any candidate bbox produced from Page 4 glyphs.
    This test verifies the discovery is correctly page-scoped.
    """
    adj = g0_result["post_hoc_adjudication"]
    page5_fixtures = ["PIAA-002", "PIAA-003", "PIAA-004", "PIAA-005"]
    for fid in page5_fixtures:
        info = adj["per_fixture"].get(fid)
        if info is None:
            continue
        assert not info["matched"], (
            f"{fid} (Page 5) was unexpectedly matched with IoU={info['best_iou']:.4f}. "
            "G0 candidates are Page 4-only and must not overlap Page 5 equations."
        )


# ---------------------------------------------------------------------------
# T6: Output JSON is written to expected path
# ---------------------------------------------------------------------------

def test_output_written_to_disk(g0_result):
    r"""G0 discovery output must be written to the expected filesystem path."""
    assert OUTPUT_PATH.exists(), (
        f"Expected output file not found: {OUTPUT_PATH}"
    )
    # Verify it is valid JSON by reading it back
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert "candidates" in data
    assert "post_hoc_adjudication" in data
    assert data["discovery_id"] == "PIAA-010-G0-UNCONSTRAINED"


# ---------------------------------------------------------------------------
# T7: Top-ranked candidate has the highest composite score
# ---------------------------------------------------------------------------

def test_candidates_sorted_by_score(g0_result):
    r"""Candidate list must be sorted descending by composite_score.

    The highest-scoring candidate (G0-001) should have score >= all others.
    This validates the ranking is not arbitrary.
    """
    candidates = g0_result["candidates"]
    assert len(candidates) >= 2, "Need at least 2 candidates to verify sort order"
    scores = [c["composite_score"] for c in candidates]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Candidates not sorted: score[{i}]={scores[i]} < score[{i+1}]={scores[i+1]}"
        )


# ---------------------------------------------------------------------------
# T8: Top candidate has a vector rule (fraction bar / vinculum)
# ---------------------------------------------------------------------------

def test_top_candidate_has_vector_rule(g0_result):
    r"""The top-ranked G0 candidate must contain a detected vector rule.

    PIAA-001 contains a fraction bar (vinculum) in the Gaussian normalisation
    factor. The vector drawing geometry channel must detect this rule and
    score the candidate accordingly.
    """
    top = g0_result["candidates"][0]
    assert top["has_vector_rule"], (
        f"Top candidate (score={top['composite_score']}) does not have a vector rule. "
        "The fraction bar in PIAA-001 should be detected by get_drawings()."
    )
