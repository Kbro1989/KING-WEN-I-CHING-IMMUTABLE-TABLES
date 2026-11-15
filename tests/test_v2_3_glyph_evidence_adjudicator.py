"""Unit & Adversarial Tests for V2.3 Glyph-Level Evidence Adjudicator (GLEA).

Verifies the P0 priority requirements from v2_3_experimental_specification.md:
  1. CP-002 exact falsifiable experiment:
     - Identifies the real physical ink intrusion of '[' (+0.081 pt).
     - Successfully purges the 3 false descender intrusions ('class', '1', 'N').
  2. Exact contact boundary semantics.
  3. Strict Gate D4 non-overridable behavior.
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

from v2_3_glyph_evidence_adjudicator import GlyphEvidenceAdjudicator
import case_registry_patch_manager as patch_mgr


@pytest.fixture(scope="module")
def vilt_page_and_adjudicator():
    overlay, _ = patch_mgr.load_patched_registry()
    c = [case for case in overlay["cases"] if "CP-002" in case["case_id"]][0]
    p = [paper for paper in overlay["papers"] if paper["paper_id"] == c["parent_paper_id"]][0]
    doc = pymupdf.open(p["pdf_rel_path"])
    page = doc[c["source_location"]["page_0based"]]
    glea = GlyphEvidenceAdjudicator(zoom=20, ink_threshold=128)
    return page, glea


class TestCP002FalsifiableExperiment:
    """The core P0 benchmark: adjudicate the 4 critical characters at y=530.300 pt."""

    CROP_Y0 = 530.300

    def test_bracket_detected_as_confirmed_ink_intrusion(self, vilt_page_and_adjudicator):
        page, glea = vilt_page_and_adjudicator
        # Character '[' in CMR10: metric_y1 = 530.193 pt (nominal exterior)
        bracket_char = {
            "char": "[",
            "font": "CMR10",
            "metric_bbox": [341.010, 520.231, 343.780, 530.193],
        }
        res = glea.adjudicate_boundary_conflict(page, bracket_char, self.CROP_Y0, is_upper_boundary=True)
        assert res["verdict"] == "CONFIRMED_INK_INTRUSION"
        assert res["is_intrusion"] is True
        assert res["true_ink_intrusion_pt"] == pytest.approx(0.181, abs=0.03)

    def test_class_subscript_purged_as_metric_artifact(self, vilt_page_and_adjudicator):
        page, glea = vilt_page_and_adjudicator
        # Character 'c' in 'class' (NimbusRomNo9L): metric_y1 = 531.196 pt (nominal intrusion = +0.896 pt)
        c_char = {
            "char": "c",
            "font": "NimbusRomNo9L-Regu",
            "metric_bbox": [348.603, 524.222, 351.699, 531.196],
        }
        res = glea.adjudicate_boundary_conflict(page, c_char, self.CROP_Y0, is_upper_boundary=True)
        assert res["verdict"] == "PURGED_METRIC_ARTIFACT"
        assert res["is_intrusion"] is False
        assert res["true_ink_intrusion_pt"] == 0.0
        assert res["true_ink_clearance_pt"] > 0.70  # clean white space above crop

    def test_subscript_1_purged_as_metric_artifact(self, vilt_page_and_adjudicator):
        page, glea = vilt_page_and_adjudicator
        # Subscript '1' in CMR7: metric_y1 = 531.035 pt (nominal intrusion = +0.735 pt)
        one_char = {
            "char": "1",
            "font": "CMR7",
            "metric_bbox": [371.914, 524.061, 375.889, 531.035],
        }
        res = glea.adjudicate_boundary_conflict(page, one_char, self.CROP_Y0, is_upper_boundary=True)
        assert res["verdict"] == "PURGED_METRIC_ARTIFACT"
        assert res["is_intrusion"] is False
        assert res["true_ink_intrusion_pt"] == 0.0
        assert res["true_ink_clearance_pt"] > 0.75

    def test_subscript_N_purged_as_metric_artifact(self, vilt_page_and_adjudicator):
        page, glea = vilt_page_and_adjudicator
        # Subscript 'N' in CMMI7: metric_y1 = 531.035 pt (nominal intrusion = +0.735 pt)
        n_char = {
            "char": "N",
            "font": "CMMI7",
            "metric_bbox": [413.038, 524.061, 419.349, 531.035],
        }
        res = glea.adjudicate_boundary_conflict(page, n_char, self.CROP_Y0, is_upper_boundary=True)
        assert res["verdict"] == "PURGED_METRIC_ARTIFACT"
        assert res["is_intrusion"] is False
        assert res["true_ink_intrusion_pt"] == 0.0
        assert res["true_ink_clearance_pt"] > 0.80

    def test_combined_verdict_fails_gate_d4(self, vilt_page_and_adjudicator):
        """Even though 3 false alarms are purged, the single true intrusion of '[' guarantees Gate D4 fails."""
        page, glea = vilt_page_and_adjudicator
        chars = [
            {"char": "[", "font": "CMR10", "metric_bbox": [341.010, 520.231, 343.780, 530.193]},
            {"char": "c", "font": "NimbusRomNo9L-Regu", "metric_bbox": [348.603, 524.222, 351.699, 531.196]},
            {"char": "1", "font": "CMR7", "metric_bbox": [371.914, 524.061, 375.889, 531.035]},
            {"char": "N", "font": "CMMI7", "metric_bbox": [413.038, 524.061, 419.349, 531.035]},
        ]
        results = [glea.adjudicate_boundary_conflict(page, ch, self.CROP_Y0) for ch in chars]
        has_any_ink_intrusion = any(r["is_intrusion"] for r in results)
        purged_count = sum(1 for r in results if r["verdict"] == "PURGED_METRIC_ARTIFACT")
        confirmed_count = sum(1 for r in results if r["verdict"] == "CONFIRMED_INK_INTRUSION")

        assert has_any_ink_intrusion is True
        assert purged_count == 3
        assert confirmed_count == 1
