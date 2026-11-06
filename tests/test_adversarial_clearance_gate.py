"""Adversarial Clearance Gate Tests: Demonstration of Sub-4.0 pt Gutter Conflict.

Demonstrates that under true external neighbor clearance measurement:
  - When the physical gap between math target and neighboring ink is < 4.0 pt (e.g. 3.0 pt),
    any crop padding >= 2.0 pt forces the remaining physical clearance to neighboring ink
    to be strictly < 2.0 pt (e.g. 1.0 pt), violating Gate D4 clearance to external ink.
  - The previous code self-referentially reported `bbox_math.y0 - crop_y0` as clearance,
    which was always >= 2.0 pt by construction, masking the physical gutter compression.
"""
from __future__ import annotations

import sys
from pathlib import Path

# pyrefly: ignore[missing-import]
import pymupdf
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

import v2_delimiter_aware_structural_recovery as v2


def measure_true_clearance_to_external_ink(
    crop_rect: pymupdf.Rect,
    neighbor_rects: list[pymupdf.Rect],
) -> dict[str, float]:
    """Measure true physical clearance from crop_rect to nearest external neighbor.

    For each edge, checks neighbors with perpendicular axis overlap.
    """
    clearance = {"above": float("inf"), "below": float("inf"), "left": float("inf"), "right": float("inf")}
    for nr in neighbor_rects:
        # Check above: neighbor is above crop_rect (nr.y1 <= crop_rect.y0)
        # requires horizontal overlap: max(nr.x0, crop_rect.x0) < min(nr.x1, crop_rect.x1)
        if nr.y1 <= crop_rect.y0 + 1e-3:
            h_overlap = max(nr.x0, crop_rect.x0) < min(nr.x1, crop_rect.x1)
            if h_overlap:
                clearance["above"] = min(clearance["above"], crop_rect.y0 - nr.y1)

        # Check below: neighbor is below crop_rect (nr.y0 >= crop_rect.y1)
        if nr.y0 >= crop_rect.y1 - 1e-3:
            h_overlap = max(nr.x0, crop_rect.x0) < min(nr.x1, crop_rect.x1)
            if h_overlap:
                clearance["below"] = min(clearance["below"], nr.y0 - crop_rect.y1)

        # Check left: neighbor is to the left (nr.x1 <= crop_rect.x0)
        if nr.x1 <= crop_rect.x0 + 1e-3:
            v_overlap = max(nr.y0, crop_rect.y0) < min(nr.y1, crop_rect.y1)
            if v_overlap:
                clearance["left"] = min(clearance["left"], crop_rect.x0 - nr.x1)

        # Check right: neighbor is to the right (nr.x0 >= crop_rect.x1)
        if nr.x0 >= crop_rect.x1 - 1e-3:
            v_overlap = max(nr.y0, crop_rect.y0) < min(nr.y1, crop_rect.y1)
            if v_overlap:
                clearance["right"] = min(clearance["right"], nr.x0 - crop_rect.x1)

    return clearance


def test_adversarial_sub_4pt_gutter_fails_true_clearance():
    """Case A: Neighbor at 3.0 pt distance.

    Math is at y0=200, y1=230. Neighbor line above ends at y1=197.0 (gap = 3.0 pt).
    Current engine padding of max(2.0, ...) expands crop to y0 = 198.0.
    True clearance from crop to neighbor is: 198.0 - 197.0 = 1.0 pt (< 2.0 pt requirement).
    Under true measurement, this MUST FAIL the >= 2.0 pt Gate D4 clearance.
    """
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    # Text line above ending at y1=197.0 (baseline at 194.0)
    page.insert_text(pymupdf.Point(100, 194.0), "ordinary prose line above", fontsize=10)

    # Delimiter pair at y in [200, 230], x in [150, 255]
    pair = {
        "_opening_rect_raw": pymupdf.Rect(150, 200, 155, 230),
        "_closing_rect_raw": pymupdf.Rect(250, 200, 255, 230),
    }
    crop_rect, meta = v2.build_enclosure_completeness(page, pair)

    # 1. Show the flaw in current engine report: it reports >= 2.0 pt by definition of padding!
    assert meta["gate_d4_clearance_above_pt"] >= 2.0, "Current engine reports its own padding as clearance"

    # 2. Get the neighbor word rects
    words = page.get_text("words")
    neighbor_rects = [pymupdf.Rect(w[:4]) for w in words]

    # 3. True clearance to external neighbor is strictly < 2.0 pt
    true_clear = measure_true_clearance_to_external_ink(crop_rect, neighbor_rects)
    assert true_clear["above"] < 2.0, (
        f"Demonstration: True physical clearance {true_clear['above']} pt is < 2.0 pt, proving conflict!"
    )
    # The physical clearance is approximately 1.0 pt (gap 3.0 pt - padding 2.0 pt)
    assert true_clear["above"] <= 1.1, f"Expected clearance ~1.0 pt, got {true_clear['above']}"
    doc.close()


def test_adversarial_4pt_gutter_passes_true_clearance():
    """Case B: Neighbor at 4.0 pt distance.

    Math is at y0=200, y1=230. Neighbor line above ends at y1=196.0 (gap = 4.0 pt).
    Engine padding of 2.0 pt leaves crop at y0=198.0.
    True clearance to neighbor is: 198.0 - 196.0 = 2.0 pt (satisfies >= 2.0 pt requirement).
    """
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    # Text line above ending at y1=196.0 (baseline at 193.0)
    page.insert_text(pymupdf.Point(100, 193.0), "ordinary prose line above", fontsize=10)

    # Delimiter pair at y in [200, 230], x in [150, 255]
    pair = {
        "_opening_rect_raw": pymupdf.Rect(150, 200, 155, 230),
        "_closing_rect_raw": pymupdf.Rect(250, 200, 255, 230),
    }
    crop_rect, meta = v2.build_enclosure_completeness(page, pair)

    words = page.get_text("words")
    neighbor_rects = [pymupdf.Rect(w[:4]) for w in words]

    true_clear = measure_true_clearance_to_external_ink(crop_rect, neighbor_rects)
    assert true_clear["above"] >= 1.99, (
        f"4.0 pt gap must provide at least 2.0 pt physical clearance, got {true_clear['above']}"
    )
    doc.close()
