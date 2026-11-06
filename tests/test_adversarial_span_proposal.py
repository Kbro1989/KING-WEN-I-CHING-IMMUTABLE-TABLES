"""Tests for EL-002 Independent Content-Span Proposal and Stop Conditions.

Verifies:
  - SC-1: Vertical gap stop condition (gap > 15 pt terminates expansion)
  - SC-2: Maximum vertical expansion ceiling (expansion > 50 pt terminates expansion)
  - SC-3: Body text exclusion (prose without math fonts is rejected)
  - SC-4: Far-margin equation number exclusion (x >= 500 excluded from math span)
  - SC-6: Column alignment and cross-column bleeding prevention
  - SC-7: Downward expansion conservatism past closing delimiter
  - Gate D4: Authoritative 2.0 pt safety gutter preservation invariant
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


def test_adversarial_sc1_vertical_gap_stop_condition():
    """SC-1: Lines separated by > 15 pt vertical gap must terminate expansion."""
    anchor = pymupdf.Rect(100, 200, 300, 220)
    lines = [
        {"bbox": pymupdf.Rect(100, 200, 300, 220), "text": "A = [B]", "fonts": {"CMMI10"}},
        # Line with 25 pt gap above
        {"bbox": pymupdf.Rect(100, 150, 300, 175), "text": "X = Y", "fonts": {"CMMI10"}},
    ]
    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert any("SC-1:gap_above" in s for s in stops), f"Expected SC-1 stop, got: {stops}"
    assert len(cluster) == 1, "Distant line must not be added to cluster"


def test_adversarial_sc2_max_expansion_ceiling():
    """SC-2: Total vertical expansion exceeding 50 pt must terminate expansion."""
    anchor = pymupdf.Rect(100, 300, 300, 320)
    # Series of closely spaced math lines (gap 5 pt each) extending 100 pt above
    lines = [{"bbox": pymupdf.Rect(100, 300, 300, 320), "text": "L0", "fonts": {"CMMI10"}}]
    y_curr = 300
    for i in range(1, 10):
        y_top = y_curr - 15
        lines.append({
            "bbox": pymupdf.Rect(100, y_top, 300, y_curr - 5),
            "text": f"L{i} = M{i}",
            "fonts": {"CMMI10"}
        })
        y_curr = y_top

    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert any("SC-2:expansion_above" in s for s in stops), f"Expected SC-2 cap, got: {stops}"
    # Verify expansion from anchor y0 is at most ~55 pt
    assert anchor.y0 - exp.y0 <= 60.0


def test_adversarial_sc3_body_text_rejection():
    """SC-3: Prose line using standard roman text fonts must be rejected."""
    anchor = pymupdf.Rect(100, 200, 300, 220)
    lines = [
        {"bbox": pymupdf.Rect(100, 200, 300, 220), "text": "z = [t]", "fonts": {"CMMI10"}},
        # Body text line 5 pt above with standard text font
        {"bbox": pymupdf.Rect(100, 185, 300, 195), "text": "This is ordinary prose with = and + signs.", "fonts": {"Times-Roman"}},
    ]
    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert any("SC-3:body_text_above" in s for s in stops), f"Expected SC-3 stop, got: {stops}"
    assert len(cluster) == 1


def test_adversarial_sc4_far_margin_equation_numbers():
    """SC-4: Equation labels at margin (x >= 500) must not inflate horizontal span."""
    anchor = pymupdf.Rect(100, 200, 300, 220)
    lines = [
        {"bbox": pymupdf.Rect(100, 200, 300, 220), "text": "A = B", "fonts": {"CMMI10"}},
        {"bbox": pymupdf.Rect(530, 205, 550, 215), "text": "(1)", "fonts": {"CMR10"}},
    ]
    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert exp.x1 < 500.0, f"Equation number at x=530 must be excluded, exp.x1={exp.x1}"


def test_adversarial_sc6_column_gutter_bleeding_blocked():
    """SC-6: Left margin alignment deviation > 30 pt must terminate expansion."""
    anchor = pymupdf.Rect(320, 200, 450, 220)
    lines = [
        {"bbox": pymupdf.Rect(320, 200, 450, 220), "text": "z = [v]", "fonts": {"CMMI10"}},
        # Line from adjacent column (starts at x=60)
        {"bbox": pymupdf.Rect(60, 185, 250, 195), "text": "x = y", "fonts": {"CMMI10"}},
    ]
    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert exp.x0 >= 300.0, f"Left column line must not enter cluster, exp.x0={exp.x0}"


def test_adversarial_sc7_downward_expansion_conservatism():
    """SC-7: Downward expansion past anchor must not sweep subsequent equations."""
    anchor = pymupdf.Rect(320, 200, 450, 220)
    lines = [
        {"bbox": pymupdf.Rect(320, 200, 450, 220), "text": "z0 = [v]", "fonts": {"CMMI10"}},
        # Next independent equation starting 8 pt below anchor
        {"bbox": pymupdf.Rect(320, 228, 450, 245), "text": "z_next = f(z0)", "fonts": {"CMMI10"}},
    ]
    exp, cluster, stops = v2._expand_multiline_cluster(anchor, lines, 612.0)
    assert any("SC-7:downward_limit" in s for s in stops), f"Expected SC-7 stop, got: {stops}"
    assert exp.y1 <= 225.0, f"Next equation must not be included, exp.y1={exp.y1}"


def test_adversarial_gate_d4_safety_gutter_invariant():
    """Gate D4 Invariant: Clearance must strictly satisfy g_min >= 2.0 pt."""
    # Create mock page with text line immediately above math bbox (tight gutter)
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    # Insert text 3 pt above math
    page.insert_text(pymupdf.Point(100, 197), "Text immediately above equation", fontsize=10)
    # Insert math pair
    pair = {
        "_opening_rect_raw": pymupdf.Rect(150, 200, 155, 230),
        "_closing_rect_raw": pymupdf.Rect(250, 200, 255, 230),
    }
    crop_rect, meta = v2.build_enclosure_completeness(page, pair)
    # Gate D4 clearance above must be >= 2.0 pt
    assert meta["gate_d4_clearance_above_pt"] >= 2.0, (
        f"Clearance above {meta['gate_d4_clearance_above_pt']} violated g_min >= 2.0 pt"
    )
    # Gate D4 clearance below must be >= 2.0 pt
    assert meta["gate_d4_clearance_below_pt"] >= 2.0, (
        f"Clearance below {meta['gate_d4_clearance_below_pt']} violated g_min >= 2.0 pt"
    )
    doc.close()

