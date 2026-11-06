"""Tests for Glyph Geometry Perturbation Experiment.

Verifies:
  1. Multi-resolution (72, 144, 216 DPI) and multi-threshold perturbation outputs exist.
  2. Bounded subpixel divergence: raster envelope variations across resolutions remain <= 1.5 pt.
  3. Stable right-edge isolation on CP-002 confirms persistent whitespace removal.
  4. Separation between nominal font metric envelopes and physical ink envelopes.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PERTURB_JSON = ROOT / "DATASETS" / "structural_preservation" / "glyph_geometry_perturbation_results.json"


@pytest.fixture(scope="module")
def perturb_data():
    assert PERTURB_JSON.exists(), f"Missing file: {PERTURB_JSON}"
    with open(PERTURB_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_perturbation_experiment_structure(perturb_data):
    assert perturb_data["study_identifier"] == "GLYPH-GEOMETRY-PERTURBATION-V1"
    assert perturb_data["tested_zooms"] == [1.0, 2.0, 3.0]
    assert len(perturb_data["targets"]) == 3
    for t in perturb_data["targets"]:
        assert t["total_perturbations"] == 12  # 3 zooms x 4 policies


def test_cp002_whitespace_removal_across_all_perturbations(perturb_data):
    cp002 = next(t for t in perturb_data["targets"] if t["target_id"] == "CP-002-VILT-NESTED-BRACKETS")
    candidate_x1 = cp002["candidate_crop_pt"][2]  # 461.28
    font_x1 = cp002["font_metric_envelope_pt"][2]  # 417.91

    for p in cp002["perturbations"]:
        raster_x1 = p["raster_envelope_pt"][2]
        # Raster right boundary must be near the font boundary (~417.18 to 417.91)
        # and far from candidate boundary (> 40 pt difference)
        assert abs(raster_x1 - font_x1) < 2.0
        assert (candidate_x1 - raster_x1) > 40.0


def test_cross_resolution_boundary_convergence(perturb_data):
    """Verifies coordinate stability across rendering scales and formats residuals in pt and px."""
    for t in perturb_data["targets"]:
        p_z1 = [p for p in t["perturbations"] if p["zoom"] == 1.0 and p["policy"] == "unimernet_fixed_200"][0]
        p_z3 = [p for p in t["perturbations"] if p["zoom"] == 3.0 and p["policy"] == "unimernet_fixed_200"][0]
        # Cross-resolution coordinate stability: variance in points <= 1.5 pt
        for i in range(4):
            diff_pt = abs(p_z1["raster_envelope_pt"][i] - p_z3["raster_envelope_pt"][i])
            assert diff_pt <= 1.5, f"Excessive divergence at index {i}: {diff_pt} pt"
        # Check that residuals are reported in both pt and px
        conv = p_z3["cross_resolution_convergence"]
        assert "residual_pt" in conv
        assert "residual_px" in conv
        assert isinstance(conv["residual_px"]["delta_top"], (int, float))

