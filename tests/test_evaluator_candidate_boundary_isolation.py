"""Adversarial tests for evaluate_cross_paper_v2_strict_candidate.py.

These fixtures target the four defects identified in the read-only audit of
V2.1 against CP-002:

  DEFECT-A: Contamination measured only on bbox_math → crop-penetrating tokens
            below the 10% area-threshold were silently missed.
  DEFECT-B: measure_external_gutter_clearance() exterior-only filter excluded
            penetrating tokens from clearance accounting entirely.
  DEFECT-C: 10% area-threshold was the sole boundary-isolation gate.
  DEFECT-D: Gate D4 could pass while penetrating tokens existed, if one exterior
            token happened to satisfy the clearance criterion.

Required test coverage from user specification (Section 4):

  F-01  CP-002 actual geometry        → all three penetrating tokens detected
  F-02  CP-002 without ¯v             → still detect penetration (not accidental)
  F-03  1% token intrusion            → fails boundary isolation
  F-04  9% token intrusion            → fails boundary isolation
  F-05  11% token intrusion           → fails boundary isolation
  F-06  Exactly touching boundary     → explicitly defined contact policy (zero-area → exterior)
  F-07  Foreign token fully inside crop → fails boundary isolation
  F-08  Clean crop with 2+ pt clearance → passes, given all other dims pass
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pymupdf
import pytest

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from evaluate_cross_paper_v2_strict_candidate import (
    MIN_CLEARANCE_THRESHOLD,
    check_math_contamination,
    measure_crop_boundary_isolation,
)

# ---------------------------------------------------------------------------
# Helpers — synthetic page construction
# ---------------------------------------------------------------------------

def make_page_with_words(words_list: list[tuple]) -> MagicMock:
    """Return a minimal pymupdf.Page mock whose get_text('words') yields words_list.

    Each entry is a tuple: (x0, y0, x1, y1, text).
    get_text('words') returns tuples of (x0, y0, x1, y1, text, block_no, line_no, word_no).
    """
    expanded = [(x0, y0, x1, y1, text, 0, i, 0) for i, (x0, y0, x1, y1, text) in enumerate(words_list)]
    page = MagicMock()
    page.get_text.return_value = expanded
    return page


# ---------------------------------------------------------------------------
# F-01: CP-002 actual geometry — all three penetrating tokens detected
# ---------------------------------------------------------------------------

class TestF01_CP002ActualGeometry:
    """Exact coordinates recovered from the read-only audit of CP-002."""

    CROP = [314.18, 530.30, 421.91, 548.37]
    GOLD = [318.18, 534.57, 417.91, 546.37]

    # Row format: (x0, y0, x1, y1, text)
    WORDS = [
        # Line above — tokens that penetrate the crop
        (341.010, 520.231, 365.428, 531.196, "[vclass;"),   # y1=531.196 > crop.y0=530.30 → penetrates
        (367.085, 520.231, 382.192, 531.035, "v1V"),         # y1=531.035 > crop.y0=530.30 → penetrates
        (408.209, 520.231, 426.402, 531.035, "vNV"),         # y1=531.035 > crop.y0=530.30 → penetrates
        # Exterior above — does NOT penetrate crop
        (322.536, 520.231, 327.896, 530.193, "¯v"),          # y1=530.193 < crop.y0=530.30 → exterior
        (330.490, 520.231, 338.241, 530.193, "="),
        # Gold target tokens (should be skipped)
        (341.010, 534.572, 417.910, 546.370, "expr"),
        # Exterior below
        (341.010, 551.07, 411.29, 563.13, "MSA(LN(zd-1))"),
    ]

    def test_all_three_penetrating_tokens_detected(self):
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        pen_tokens = {t["token"] for t in result["penetrating_tokens"]}
        assert "[vclass;" in pen_tokens, "Expected [vclass; to be classified as penetrating"
        assert "v1V" in pen_tokens, "Expected v1V to be classified as penetrating"
        assert "vNV" in pen_tokens, "Expected vNV to be classified as penetrating"
        assert result["penetrating_token_count"] == 3

    def test_has_penetration_flag_set(self):
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True

    def test_gate_d4_fails(self):
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is False

    def test_vclass_signed_penetration_above_negative(self):
        """signed_penetration_above_pt < 0 indicates intrusion from above."""
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        vclass = next(t for t in result["penetrating_tokens"] if t["token"] == "[vclass;")
        assert vclass["signed_penetration_above_pt"] < 0, (
            f"Expected negative penetration_above, got {vclass['signed_penetration_above_pt']}"
        )

    def test_exterior_above_v_bar_still_reported(self):
        """¯v is strictly exterior; it should appear as nearest_neighbor_above, not as penetrating."""
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        pen_tokens = {t["token"] for t in result["penetrating_tokens"]}
        assert "¯v" not in pen_tokens, "¯v is exterior, must not appear in penetrating_tokens"
        # Its clearance should be reported
        assert result["clearance_above_pt"] == pytest.approx(0.11, abs=0.02)


# ---------------------------------------------------------------------------
# F-02: CP-002 without ¯v — penetration still detected (not accidental gate)
# ---------------------------------------------------------------------------

class TestF02_CP002WithoutVBar:
    """Remove the exterior ¯v token. Penetration must still be detected.

    This eliminates the accidental-failure path: if Gate D4 had relied solely
    on the exterior ¯v to trigger failure (0.11 pt < 2.0 pt), removing it
    would have falsely certified CP-002.
    """

    CROP = [314.18, 530.30, 421.91, 548.37]
    GOLD = [318.18, 534.57, 417.91, 546.37]

    WORDS = [
        # Penetrating tokens — no exterior ¯v present this time
        (341.010, 520.231, 365.428, 531.196, "[vclass;"),
        (367.085, 520.231, 382.192, 531.035, "v1V"),
        (408.209, 520.231, 426.402, 531.035, "vNV"),
        # Gold
        (341.010, 534.572, 417.910, 546.370, "expr"),
        # Exterior below (provides below clearance)
        (341.010, 551.07, 411.29, 563.13, "MSA(LN(zd-1))"),
    ]

    def test_penetration_detected_without_vbar(self):
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True

    def test_gate_d4_fails_without_vbar(self):
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is False

    def test_clearance_above_reports_infinity_when_no_exterior_above(self):
        """With no strictly exterior token above, clearance_above should be 999.0 (sentinel)."""
        page = make_page_with_words(self.WORDS)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        # penetration detected → gate fails regardless; clearance sentinel is 999.0
        assert result["clearance_above_pt"] == 999.0


# ---------------------------------------------------------------------------
# F-03 through F-05: Intrusion percentage variants
# ---------------------------------------------------------------------------

def _make_intrusion_scene(crop, gold, token_overlap_fraction: float):
    """Construct a synthetic scene where one foreign token intrudes into crop
    by exactly `token_overlap_fraction` of its own area.

    The token's total area is set to 100 pt² for easy arithmetic.
    Token height is 10 pt, width is 10 pt.
    The intrusion height into the crop is chosen so that:
        (intrusion_height * 10 pt) / (10 pt * 10 pt) == token_overlap_fraction

    So intrusion_height = 10 * token_overlap_fraction.
    Token y1 = crop_y0 + intrusion_height (token extends inside crop).
    Token y0 = crop_y0 + intrusion_height - 10.
    """
    crop_x0, crop_y0, crop_x1, crop_y1 = crop
    intrusion_height = 10 * token_overlap_fraction  # pt
    t_x0 = (crop_x0 + crop_x1) / 2 - 5  # centre horizontally
    t_x1 = t_x0 + 10
    t_y1 = crop_y0 + intrusion_height
    t_y0 = t_y1 - 10
    words = [(t_x0, t_y0, t_x1, t_y1, "PROBE")]
    # Also include a clean exterior below token so below-clearance is satisfied
    words.append((t_x0, crop_y1 + 10.0, t_x1, crop_y1 + 20.0, "BELOW"))
    return words


class TestF03_OnePercentIntrusion:
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 220.0, 195.0, 280.0]

    def test_1pct_intrusion_fails_gate_d4(self):
        words = _make_intrusion_scene(self.CROP, self.GOLD, 0.01)
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True
        assert result["pass_gate_d4"] is False


class TestF04_NinePercentIntrusion:
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 220.0, 195.0, 280.0]

    def test_9pct_intrusion_fails_gate_d4(self):
        """9% is below the old 10% threshold — this was a silent pass in V2.1."""
        words = _make_intrusion_scene(self.CROP, self.GOLD, 0.09)
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True
        assert result["pass_gate_d4"] is False, (
            "9% intrusion must fail under DEFECT-C fix (zero-tolerance for crop penetration)"
        )


class TestF05_ElevenPercentIntrusion:
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 220.0, 195.0, 280.0]

    def test_11pct_intrusion_fails_gate_d4(self):
        words = _make_intrusion_scene(self.CROP, self.GOLD, 0.11)
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True
        assert result["pass_gate_d4"] is False


# ---------------------------------------------------------------------------
# F-06: Exactly touching boundary — contact policy (zero-area intersection)
# ---------------------------------------------------------------------------

class TestF06_ExactlyTouchingBoundary:
    """A token whose y1 == crop.y0 exactly.

    Policy: zero-area intersection (width > 0, height == 0 because y1 == y0)
    is classified as exterior-above, not penetrating. clearance_above = 0.0 pt,
    which still fails the >= 2.0 pt exterior clearance requirement.
    """
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 220.0, 195.0, 280.0]

    def test_touching_token_is_exterior_not_penetrating(self):
        # Token y1 exactly == crop y0
        words = [
            (110.0, 190.0, 160.0, 200.0, "TOUCHING"),   # y1 = crop.y0 = 200.0
            (110.0, 310.0, 160.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        pen_tokens = {t["token"] for t in result["penetrating_tokens"]}
        assert "TOUCHING" not in pen_tokens, (
            "A token with y1 == crop.y0 produces zero intersection height → exterior"
        )

    def test_touching_token_produces_zero_clearance_above(self):
        words = [
            (110.0, 190.0, 160.0, 200.0, "TOUCHING"),
            (110.0, 310.0, 160.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["clearance_above_pt"] == pytest.approx(0.0, abs=0.01)

    def test_touching_token_still_fails_gate_d4(self):
        """Zero clearance is below 2.0 pt threshold → Gate D4 fails."""
        words = [
            (110.0, 190.0, 160.0, 200.0, "TOUCHING"),
            (110.0, 310.0, 160.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is False


# ---------------------------------------------------------------------------
# F-07: Foreign token fully inside crop
# ---------------------------------------------------------------------------

class TestF07_ForeignTokenFullyInsideCrop:
    """A foreign token entirely contained within bbox_crop but outside gold_bbox_math.

    This is the worst case: fully-interior foreign content. Must fail.
    """
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [120.0, 240.0, 180.0, 260.0]  # narrower gold

    def test_fully_interior_foreign_token_detected(self):
        # Token is inside crop but outside gold
        words = [
            (101.0, 201.0, 119.0, 230.0, "INTERIOR"),  # left of gold, inside crop
            (101.0, 310.0, 119.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        pen_tokens = {t["token"] for t in result["penetrating_tokens"]}
        assert "INTERIOR" in pen_tokens, "Fully interior foreign token must be classified as penetrating"

    def test_fully_interior_foreign_token_fails_gate_d4(self):
        words = [
            (101.0, 201.0, 119.0, 230.0, "INTERIOR"),
            (101.0, 310.0, 119.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is False

    def test_fully_interior_overlap_ratio_is_one(self):
        words = [
            (101.0, 201.0, 119.0, 230.0, "INTERIOR"),
            (101.0, 310.0, 119.0, 320.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        interior = next(t for t in result["penetrating_tokens"] if t["token"] == "INTERIOR")
        assert interior["overlap_ratio"] == pytest.approx(1.0, abs=0.001)


# ---------------------------------------------------------------------------
# F-08: Clean crop with 2+ pt clearance — passes
# ---------------------------------------------------------------------------

class TestF08_CleanCropWithSufficientClearance:
    """A clean crop geometry: no penetrating tokens, exterior clearance >= 2.0 pt."""
    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 215.0, 195.0, 285.0]

    def test_clean_crop_no_penetration(self):
        words = [
            (110.0, 190.0, 160.0, 197.0, "ABOVE"),   # y1=197 → clearance = 200-197 = 3.0 pt
            (110.0, 303.0, 160.0, 310.0, "BELOW"),    # y0=303 → clearance = 303-300 = 3.0 pt
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is False
        assert result["penetrating_token_count"] == 0

    def test_clean_crop_clearance_sufficient(self):
        words = [
            (110.0, 190.0, 160.0, 197.0, "ABOVE"),
            (110.0, 303.0, 160.0, 310.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["clearance_above_pt"] == pytest.approx(3.0, abs=0.01)
        assert result["clearance_below_pt"] == pytest.approx(3.0, abs=0.01)
        assert result["pass_clearance_above"] is True
        assert result["pass_clearance_below"] is True

    def test_clean_crop_gate_d4_passes(self):
        words = [
            (110.0, 190.0, 160.0, 197.0, "ABOVE"),
            (110.0, 303.0, 160.0, 310.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is True

    def test_clean_crop_exactly_at_threshold_passes(self):
        """Clearance exactly at MIN_CLEARANCE_THRESHOLD (2.0 pt) must pass."""
        words = [
            (110.0, 180.0, 160.0, 198.0, "ABOVE"),   # y1=198 → clearance = 200-198 = 2.0 pt
            (110.0, 302.0, 160.0, 310.0, "BELOW"),    # y0=302 → clearance = 302-300 = 2.0 pt
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is True

    def test_clean_crop_just_below_threshold_fails(self):
        """Clearance 1.99 pt is below 2.0 pt threshold → Gate D4 must fail."""
        words = [
            (110.0, 180.0, 160.0, 198.01, "ABOVE"),  # y1=198.01 → clearance = 200-198.01 = 1.99 pt
            (110.0, 302.0, 160.0, 310.0, "BELOW"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["pass_gate_d4"] is False


# ---------------------------------------------------------------------------
# Structural invariant: math contamination check is independent of crop check
# ---------------------------------------------------------------------------

class TestDefectA_MathVsCropContaminationSeparation:
    """DEFECT-A regression: check_math_contamination must only evaluate bbox_math.

    The CP-002 scenario: penetrating tokens have y1 > bbox_math.y0 (above math)
    but y1 > crop.y0 (inside crop). The math contamination check must NOT
    report them, because they don't overlap bbox_math.
    """

    # CP-002 exact values
    MATH_BOX = [318.18, 532.30, 417.91, 546.37]
    GOLD = [318.18, 534.57, 417.91, 546.37]

    def test_penetrating_token_above_math_box_not_flagged_in_math_check(self):
        """[vclass; ends at y1=531.196, which is above bbox_math.y0=532.30.
        It should NOT appear in math contamination because it has zero overlap with bbox_math.
        """
        words = [(341.010, 520.231, 365.428, 531.196, "[vclass;")]
        page = make_page_with_words(words)
        has_contam, contam = check_math_contamination(page, self.MATH_BOX, self.GOLD)
        contam_tokens = {t["token"] for t in contam}
        assert "[vclass;" not in contam_tokens, (
            "[vclass; is above bbox_math and must not appear in math contamination"
        )

    def test_math_contamination_catches_tokens_inside_math_box(self):
        """A token inside bbox_math but outside gold must be caught by math contamination."""
        # Token inside bbox_math=[318.18,532.30,417.91,546.37] but outside gold=[318.18,534.57,...]:
        # Place it in the vertical strip [532.30, 534.57) — inside math, above gold.
        words = [(320.0, 532.5, 380.0, 534.0, "MATHINTRUDER")]
        page = make_page_with_words(words)
        has_contam, contam = check_math_contamination(page, self.MATH_BOX, self.GOLD)
        contam_tokens = {t["token"] for t in contam}
        # Token area = 60 * 1.5 = 90 pt²; overlap with bbox_math = 90 pt² (100%); > 10% threshold
        assert "MATHINTRUDER" in contam_tokens


# ---------------------------------------------------------------------------
# DEFECT-D structural test: conjunctive gate cannot pass on partial conditions
# ---------------------------------------------------------------------------

class TestDefectD_ConjunctiveGate:
    """Gate D4 must require ALL three conditions simultaneously."""

    CROP = [100.0, 200.0, 200.0, 300.0]
    GOLD = [105.0, 220.0, 195.0, 280.0]

    def test_penetration_alone_sufficient_to_fail(self):
        """Even with good exterior clearance, penetration fails Gate D4."""
        words = [
            # Exterior above with 5 pt clearance
            (110.0, 180.0, 160.0, 195.0, "ABOVE"),
            # Exterior below with 5 pt clearance
            (110.0, 305.0, 160.0, 315.0, "BELOW"),
            # Penetrating: y1 = 201.0 (1 pt inside crop)
            (110.0, 190.0, 160.0, 201.0, "PENETRATOR"),
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is True
        # Exterior clearance may still look good — the gate must still fail
        assert result["pass_gate_d4"] is False, (
            "Penetrating token alone must fail Gate D4 regardless of exterior clearance"
        )

    def test_insufficient_clearance_alone_sufficient_to_fail(self):
        """No penetration, but only 1.0 pt exterior clearance — Gate D4 must fail."""
        words = [
            (110.0, 193.0, 160.0, 199.0, "ABOVE"),   # clearance = 200-199 = 1.0 pt
            (110.0, 305.0, 160.0, 315.0, "BELOW"),    # clearance = 305-300 = 5.0 pt
        ]
        page = make_page_with_words(words)
        crop_rect = pymupdf.Rect(*self.CROP)
        result = measure_crop_boundary_isolation(page, crop_rect, self.GOLD)
        assert result["has_crop_penetration"] is False
        assert result["pass_clearance_above"] is False
        assert result["pass_gate_d4"] is False

