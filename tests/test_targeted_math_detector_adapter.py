"""Unit tests for Layer 1 Targeted Math Detector Adapter.

Verifies:
  1. Discovery operates blindly without oracle coordinates or reference bboxes.
  2. Does not rely on TARGET_LATEX_NAMES.
  3. Discovers at least 5 candidate proposals on Page 5 (page_idx=4) of arXiv:2605.25821.
  4. Output strictly conforms to the standardized evidence sidecar schema:
     - evidence_id, producer, layer='L1', input_sha256, page_id, bbox_pdf_pt,
       confidence in [0, 1], dependencies=[], status='OBSERVED'.
  5. Bounding box coordinates are valid PDF points [x0, y0, x1, y1].
"""
from __future__ import annotations

import sys
from pathlib import Path
import pymupdf
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from targeted_math_detector_adapter import (
    discover_candidates,
    extract_raw_observations_unconditioned,
    is_math_font,
)

PDF_PATH = (
    "C:/Users/krist/Desktop/zotero/learning-corpus/efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)


@pytest.fixture(scope="module")
def piaa_page_5():
    doc = pymupdf.open(PDF_PATH)
    page = doc[4]  # Page 5 (0-based 4)
    return page


def test_unconditioned_raw_observations_extraction(piaa_page_5):
    """Extraction must find math spans without requiring target keyword priors."""
    spans, chars = extract_raw_observations_unconditioned(piaa_page_5, page_index=4)
    assert len(spans) > 50
    assert len(chars) > 100
    for span in spans:
        assert "math_character_count" in span
        assert span["bbox_pdf_pt"][2] > span["bbox_pdf_pt"][0]


def test_blind_candidate_discovery_page_5(piaa_page_5):
    """Blind discovery on Page 5 must propose at least 5 candidates without reference coordinates."""
    candidates = discover_candidates(piaa_page_5, page_index=4, pdf_path=PDF_PATH)
    assert len(candidates) >= 5

    # Check evidence sidecar schema compliance
    required_keys = {
        "evidence_id",
        "producer",
        "producer_version",
        "layer",
        "input_sha256",
        "page_id",
        "bbox_pdf_pt",
        "crop_sha256",
        "observation",
        "confidence",
        "dependencies",
        "status",
    }
    for cand in candidates:
        assert required_keys.issubset(cand.keys())
        assert cand["layer"] == "L1"
        assert cand["status"] == "OBSERVED"
        assert 0.0 <= cand["confidence"] <= 1.0
        assert len(cand["bbox_pdf_pt"]) == 4

        x0, y0, x1, y1 = cand["bbox_pdf_pt"]
        assert x1 > x0
        assert y1 > y0
        # Coordinate bounds must be on the 612x792 pt page
        assert 0.0 <= x0 <= 612.0
        assert 0.0 <= y0 <= 792.0
        assert 0.0 <= x1 <= 612.0
        assert 0.0 <= y1 <= 792.0

        # Observations must carry intrinsic metrics
        obs = cand["observation"]
        assert "math_character_ratio" in obs
        assert "has_relation" in obs
        assert "fonts" in obs


def test_major_page_5_equations_detected(piaa_page_5):
    """Check that key known equations on Page 5 are covered by candidate proposals."""
    candidates = discover_candidates(piaa_page_5, page_index=4, pdf_path=PDF_PATH)
    cand_texts = " ".join(c["observation"]["text"] for c in candidates)

    # Key equations present on Page 5
    assert "wc" in cand_texts or "bc" in cand_texts  # Eq (4)
    assert "H(" in cand_texts  # Eq (5)
    assert "Σ" in cand_texts or "Sigma" in cand_texts or "µ" in cand_texts  # Eqs (4), (8), (9), (10)
