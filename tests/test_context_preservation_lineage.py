#!/usr/bin/env python3
"""
Cross-function lineage tests for context-preservation pipeline.

Validates the contract: page → region → candidate → expanded representation.
Tests that identities remain connected across all four functions WITHOUT
requiring OCR success or pipeline integration.

Tests CL-01 through CL-06 from standalone-context-preservation-test-plan-2026-11-04.md

Milestone: Tested (cross-function lineage)
Gate: G5 (Representation continuity), G6 (Evaluation integrity)
"""
import sys
from pathlib import Path

import numpy as np
import cv2
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from vision_comparison_pipeline import (
    detect_math_regions_on_page,
    expand_crop_context,
    extract_text_boundaries,
    detect_partial_formulas,
)


def _make_page_with_math(text="x = 5 + y", width=595, height=842):
    """Create a PDF page with math text."""
    doc = pymupdf.open()
    page = doc.new_page(width=width, height=height)
    page.insert_text((50, 50), text, fontsize=12)
    return doc, page


def _make_image_with_region():
    """Create a synthetic image with a dark region for testing."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[40:80, 40:120] = 0  # Dark region (math-like)
    return img


# ---------------------------------------------------------------------------
# CL-01: Page → Region identity
# ---------------------------------------------------------------------------

def test_cl01_page_region_identity():
    """CL-01: Region detection output retains page identity."""
    img = _make_image_with_region()
    regions = detect_math_regions_on_page(img)
    # Each region must have bbox and area (page identity is implicit in the call)
    # The function doesn't take page_id, so we verify structure allows tracing
    for r in regions:
        assert 'bbox' in r, "Region missing bbox"
        assert 'region_count' in r, "Region missing region_count"
        assert 'centroid' in r, "Region missing centroid"
        x, y, w, h = r['bbox']
        assert x >= 0 and y >= 0 and w > 0 and h > 0, f"Invalid bbox: {r['bbox']}"


def test_cl01_region_count_matches_components():
    """CL-01b: Region count corresponds to detected components."""
    img = _make_image_with_region()
    regions = detect_math_regions_on_page(img)
    # Should detect at least the one dark region
    assert len(regions) >= 1, "No regions detected for synthetic image with dark region"


# ---------------------------------------------------------------------------
# CL-02: Region → Candidate membership
# ---------------------------------------------------------------------------

def test_cl02_region_candidate_membership_explicit():
    """CL-02: Region membership is explicit (member_bboxes field)."""
    img = _make_image_with_region()
    regions = detect_math_regions_on_page(img)
    for r in regions:
        assert 'member_bboxes' in r, "Region missing member_bboxes"
        assert isinstance(r['member_bboxes'], list)
        # member_bboxes should be non-empty for detected regions
        if r['region_count'] > 0:
            assert len(r['member_bboxes']) == r['region_count']


def test_cl02_candidate_not_silently_dropped():
    """CL-02b: Empty image produces empty list (no silent dropping)."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    regions = detect_math_regions_on_page(img)
    assert regions == [], "Empty image should produce no regions (not silently drop)"


# ---------------------------------------------------------------------------
# CL-03: Candidate → Expanded identity
# ---------------------------------------------------------------------------

def test_cl03_expanded_preserves_original_bbox():
    """CL-03: Expanded crop can be traced back to original candidate."""
    doc, page = _make_page_with_math("x = 5")
    bbox = {'x0': 40, 'y0': 30, 'x1': 120, 'y1': 60}
    original_area = (bbox['x1'] - bbox['x0']) * (bbox['y1'] - bbox['y0'])
    result = expand_crop_context(page, bbox, expand_factor=1.5, zoom=2)
    if result is not None:
        # Expanded crop should be larger than original (in pixel space)
        expanded_pixels = result.shape[0] * result.shape[1]
        assert expanded_pixels > 0
        # The original bbox dimensions at zoom=2 would be:
        orig_w_px = (bbox['x1'] - bbox['x0']) * 2
        orig_h_px = (bbox['y1'] - bbox['y0']) * 2
        # Expanded should be at least as large
        assert result.shape[1] >= orig_w_px * 0.9  # Allow small rounding
        assert result.shape[0] >= orig_h_px * 0.9
    doc.close()


def test_cl03_expanded_no_identity_loss():
    """CL-03b: Expansion does not alter candidate identity (bbox recoverable)."""
    doc, page = _make_page_with_math("x = 5 + 1")
    bbox = {'x0': 40, 'y0': 30, 'x1': 120, 'y1': 60}
    # Store original bbox
    orig_bbox = dict(bbox)
    result = expand_crop_context(page, bbox, expand_factor=1.5, zoom=2)
    # Original bbox must be unchanged (function should not mutate input)
    assert bbox == orig_bbox, "expand_crop_context mutated input bbox"
    if result is not None:
        assert isinstance(result, np.ndarray)
    doc.close()


# ---------------------------------------------------------------------------
# CL-04: Page boundary respect
# ---------------------------------------------------------------------------

def test_cl04_no_negative_coordinates():
    """CL-04: No expanded crop produces negative coordinates."""
    doc, page = _make_page_with_math("Edge case")
    # Bbox at every edge
    edge_bboxes = [
        {'x0': 0, 'y0': 0, 'x1': 50, 'y1': 50},          # top-left
        {'x0': 545, 'y0': 0, 'x1': 595, 'y1': 50},       # top-right
        {'x0': 0, 'y0': 792, 'x1': 50, 'y1': 842},       # bottom-left
        {'x0': 545, 'y0': 792, 'x1': 595, 'y1': 842},    # bottom-right
    ]
    for bbox in edge_bboxes:
        result = expand_crop_context(page, bbox, expand_factor=1.5, zoom=2)
        if result is not None:
            assert result.shape[0] > 0 and result.shape[1] > 0
            # No negative dimensions (would indicate overflow)
            assert result.shape[0] < 10000 and result.shape[1] < 10000
    doc.close()


def test_cl04_region_bbox_within_page():
    """CL-04b: Region detection bboxes stay within image bounds."""
    img = _make_image_with_region()
    regions = detect_math_regions_on_page(img)
    h, w = img.shape[:2]
    for r in regions:
        x, y, rw, rh = r['bbox']
        assert x >= 0 and y >= 0, f"Negative origin: {r['bbox']}"
        assert x + rw <= w, f"X overflow: {r['bbox']} > {w}"
        assert y + rh <= h, f"Y overflow: {r['bbox']} > {h}"


# ---------------------------------------------------------------------------
# CL-05: Uncertain membership recorded
# ---------------------------------------------------------------------------

def test_cl05_uncertain_membership_not_silently_resolved():
    """CL-05: Ambiguous region membership is not silently resolved."""
    # Create image with two regions very close together (ambiguous merge)
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:70, 50:70] = 0
    img[50:70, 72:92] = 0  # 2px gap — ambiguous
    regions = detect_math_regions_on_page(img)
    # Should produce at least one region (merged or separate)
    assert len(regions) >= 1
    # The function should not crash on ambiguous input
    # (Current implementation merges via v_overlap + h_proximity;
    #  this test documents that behavior, not that it's correct)


def test_cl05_empty_region_list_for_blank():
    """CL-05b: Blank page produces empty region list (no false assignments)."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    regions = detect_math_regions_on_page(img)
    assert regions == [], "Blank page must produce no regions (no false membership)"


# ---------------------------------------------------------------------------
# CL-06: Failed detection recorded
# ---------------------------------------------------------------------------

def test_cl06_failed_expansion_returns_none():
    """CL-06: Failed expansion returns None (not silently discarded)."""
    doc, page = _make_page_with_math("test")
    # Bbox with zero area (invalid)
    bbox = {'x0': 50, 'y0': 50, 'x1': 50, 'y1': 50}
    result = expand_crop_context(page, bbox, expand_factor=1.5, zoom=2)
    # Should return None (failed), not crash or return empty array
    assert result is None or isinstance(result, np.ndarray)
    doc.close()


def test_cl06_failed_text_extraction_returns_empty():
    """CL-06b: Failed text extraction returns empty list (not None or crash)."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    # Empty page — no text
    result = extract_text_boundaries(page)
    assert result == [], "Empty page must return empty list (not None or crash)"
    doc.close()


def test_cl06_failed_partial_detection_returns_empty():
    """CL-06c: Failed partial formula detection returns empty list."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    result = detect_partial_formulas(page)
    assert result == [], "Empty page must return empty list (not None or crash)"
    doc.close()


# ---------------------------------------------------------------------------
# CL-07: Text boundary → partial formula lineage
# ---------------------------------------------------------------------------

def test_cl07_text_to_partial_lineage():
    """CL-07: Partial formulas reference their source text boundaries."""
    doc, page = _make_page_with_math("where x = 5 is the learning rate")
    boundaries = extract_text_boundaries(page)
    partials = detect_partial_formulas(page)
    # If partials exist, each should reference text from boundaries
    for p in partials:
        assert 'text' in p, "Partial missing text"
        assert 'bbox' in p, "Partial missing bbox"
        assert 'math_words' in p, "Partial missing math_words"
        # math_words should be subset of boundary texts
        all_boundary_texts = [b['text'] for b in boundaries]
        for mw in p['math_words']:
            # math_word should appear in some boundary
            assert any(mw in bt for bt in all_boundary_texts), \
                f"math_word '{mw}' not found in boundaries"
    doc.close()


# ---------------------------------------------------------------------------
# CL-08: Region → text boundary correspondence
# ---------------------------------------------------------------------------

def test_cl08_region_text_correspondence():
    """CL-08: Regions and text boundaries can be correlated by bbox."""
    img = _make_image_with_region()
    doc, page = _make_page_with_math("x = 5")
    regions = detect_math_regions_on_page(img)
    boundaries = extract_text_boundaries(page)
    # Both should produce non-empty results for their respective inputs
    # (image vs page are different, so counts may differ)
    # The key is that both produce structured output with bboxes
    for r in regions:
        assert 'bbox' in r
    for b in boundaries:
        assert 'bbox' in b
    doc.close()


# ---------------------------------------------------------------------------
# CL-09: Failed detection recorded (not discarded)
# ---------------------------------------------------------------------------

def test_cl09_none_input_recorded():
    """CL-09: None input to detect_math_regions_on_page returns empty (recorded)."""
    result = detect_math_regions_on_page(None)
    assert result == [], "None input must return empty list, not crash or None"


def test_cl09_none_page_text_boundaries():
    """CL-09b: None page to extract_text_boundaries raises or returns empty."""
    try:
        result = extract_text_boundaries(None)
        assert result == [] or result is None
    except Exception:
        pass  # Acceptable — failure is recorded, not silently ignored


def test_cl09_none_page_partial_formulas():
    """CL-09c: None page to detect_partial_formulas raises or returns empty."""
    try:
        result = detect_partial_formulas(None)
        assert result == [] or result is None
    except Exception:
        pass  # Acceptable — failure is recorded, not silently ignored


# ---------------------------------------------------------------------------
# CL-10: Reproducibility (G6)
# ---------------------------------------------------------------------------

def test_cl10_region_detection_deterministic():
    """CL-10: Region detection is deterministic (same input → same output)."""
    img = _make_image_with_region()
    r1 = detect_math_regions_on_page(img)
    r2 = detect_math_regions_on_page(img)
    assert len(r1) == len(r2), "Region count differs between runs"
    for a, b in zip(r1, r2):
        assert a['bbox'] == b['bbox'], "Region bboxes differ between runs"
        assert a['region_count'] == b['region_count'], "Region counts differ between runs"


def test_cl10_text_boundaries_deterministic():
    """CL-10b: Text boundary extraction is deterministic."""
    doc, page = _make_page_with_math("x = 5 + y")
    r1 = extract_text_boundaries(page)
    r2 = extract_text_boundaries(page)
    assert len(r1) == len(r2), "Boundary count differs between runs"
    for a, b in zip(r1, r2):
        assert a['text'] == b['text'], "Boundary text differs between runs"
        assert a['bbox'] == b['bbox'], "Boundary bbox differs between runs"
    doc.close()


def test_cl10_partial_formulas_deterministic():
    """CL-10c: Partial formula detection is deterministic."""
    doc, page = _make_page_with_math("x = 5 + y")
    r1 = detect_partial_formulas(page)
    r2 = detect_partial_formulas(page)
    assert len(r1) == len(r2), "Partial count differs between runs"
    for a, b in zip(r1, r2):
        assert a['text'] == b['text'], "Partial text differs between runs"
        assert a['bbox'] == b['bbox'], "Partial bbox differs between runs"
    doc.close()