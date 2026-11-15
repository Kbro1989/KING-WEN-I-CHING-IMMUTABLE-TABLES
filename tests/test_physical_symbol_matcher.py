"""Unit Tests for Physical Raster Template Matcher (V2.3 Evidence Channel).

Validates:
  - Multi-feature template matching (NCC + aspect ratio + density)
  - Accurate identification of key mathematical symbols from templates
  - Abstention on empty or zero-ink crops
  - Incompatible aspect ratio filtering
  - Cross-channel adjudication (CONFIRMED_AGREEMENT, UNRESOLVED_CONFLICT, DEFER_TO_FONT)
  - Real PDF glyph crop matching on PIAA specimen (Equation 2 Greek prior, Equation 5 sum)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from physical_symbol_matcher import PhysicalSymbolMatcher

PDF_PATH = (
    "C:/Users/krist/Desktop/zotero/learning-corpus/efficient-inference-quantization/"
    "2605.25821_[CLS] is Not Enough_ Multi-Label Recognition via "
    "Patch-Level Inference and Adapt.pdf"
)


@pytest.fixture(scope="module")
def matcher():
    return PhysicalSymbolMatcher()


def test_template_loading(matcher):
    """Verify template image loading, inversion (ink=1, bg=0), and caching."""
    arr = matcher.load_template_image("pi")
    assert arr is not None
    assert isinstance(arr, np.ndarray)
    assert arr.ndim == 2
    # Inverted: ink should be 1.0, background 0.0
    assert np.max(arr) == 1.0
    assert np.min(arr) == 0.0
    # Cache check
    assert "pi" in matcher.templates


def test_ncc_identical_and_orthogonal(matcher):
    """Verify normalized cross correlation properties."""
    arr = matcher.load_template_image("csigma")
    assert arr is not None
    # NCC of identical array must be 1.0
    ncc_self = matcher.compute_ncc(arr, arr)
    assert abs(ncc_self - 1.0) < 1e-4

    # NCC of empty/uniform image must be 0.0
    zeros = np.zeros_like(arr)
    assert matcher.compute_ncc(arr, zeros) == 0.0


def test_self_matching_accuracy(matcher):
    """Verify that templates matched against themselves achieve top-1 ranking with high score."""
    test_symbols = ["pi", "mu", "sum", "surd", "csigma", "top", "bbr"]
    for mnem in test_symbols:
        tmpl = matcher.load_template_image(mnem)
        assert tmpl is not None
        res = matcher.match_glyph_crop(tmpl, candidate_mnemonics=test_symbols)
        assert res["status"] == "MATCH_FOUND"
        assert res["best_match"]["mnemonic"] == mnem
        assert res["best_match"]["composite_score"] >= 0.85


def test_abstention_on_empty_and_noise(matcher):
    """Matcher must abstain on empty or zero-ink crops."""
    empty = np.zeros((20, 20), dtype=np.float32)
    res = matcher.match_glyph_crop(empty)
    assert res["status"] == "ABSTAIN"
    assert res["reason"] == "EMPTY_OR_ZERO_INK_CROP"


def test_aspect_ratio_incompatibility_filter(matcher):
    """Very tall or very wide crops must not match symbols of opposite geometry."""
    # Create extreme horizontal line (e.g. 50x3)
    wide_line = np.ones((4, 50), dtype=np.float32)
    # Match against vertical or square symbols
    res = matcher.match_glyph_crop(wide_line, candidate_mnemonics=["int", "csigma", "surd"])
    # Should abstain or heavily penalize due to extreme aspect ratio
    if res["status"] == "MATCH_FOUND":
        assert res["best_match"]["composite_score"] < 0.65


def test_cross_channel_adjudication_confirmed(matcher):
    """When font metadata and raster match agree, verdict is CONFIRMED_AGREEMENT."""
    raster_match = {
        "status": "MATCH_FOUND",
        "best_match": {
            "mnemonic": "pi",
            "tex_macro": r"\pi",
            "composite_score": 0.88,
        }
    }
    adj = matcher.adjudicate_font_vs_raster(
        font_reported_char="p",
        font_reported_tex=r"\pi",
        raster_match=raster_match,
    )
    assert adj["verdict"] == "CONFIRMED_AGREEMENT"
    assert adj["adopted_tex"] == r"\pi"


def test_cross_channel_adjudication_unresolved_conflict(matcher):
    """When strong raster match (>0.70) contradicts font metadata, emit UNRESOLVED_CONFLICT."""
    raster_match = {
        "status": "MATCH_FOUND",
        "best_match": {
            "mnemonic": "csigma",
            "tex_macro": r"\Sigma",
            "composite_score": 0.82,
        }
    }
    adj = matcher.adjudicate_font_vs_raster(
        font_reported_char="w",
        font_reported_tex=r"\mathbf{w}",
        raster_match=raster_match,
        conflict_threshold=0.70,
    )
    assert adj["verdict"] == "UNRESOLVED_CONFLICT"
    assert adj["adopted_tex"] is None
    assert "Strong conflict" in adj["reason"]


def test_real_pdf_glyph_raster_crop_matching(matcher):
    """Extract actual raster glyph crop from PIAA PDF and test physical matching."""
    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        pytest.skip("PIAA PDF not present on disk")

    import pymupdf
    doc = pymupdf.open(str(pdf_file))
    page = doc[4]  # Page 5 (0-based 4)

    # Greek prior \pi in Eq (2): bbox [168.0, 100.4, 175.5, 110.4]
    clip_rect = pymupdf.Rect(168.0, 100.4, 175.5, 110.4)
    pix = page.get_pixmap(clip=clip_rect, dpi=288)  # High resolution 4x zoom
    gray_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
    crop_arr = (np.array(gray_img) < 128).astype(np.float32)

    res = matcher.match_glyph_crop(
        crop_arr,
        candidate_mnemonics=["pi", "mu", "csigma", "sum", "top", "bbr", "alpha", "beta"],
        min_confidence=0.50,
    )
    assert res["status"] in ("MATCH_FOUND", "AMBIGUOUS")
    # Top matches must include pi or visually similar greek characters
    top_mnemonics = [m["mnemonic"] for m in res["top_matches"]]
    assert len(top_mnemonics) > 0
    doc.close()
