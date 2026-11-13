"""
Regression & Contract Test Suite for Spatial-Syntactic Observer (Layer 1)
Tests the 15-Region Negative-Control Population on arXiv 2009.00031 Page 5.

Verifies the 8 core operational requirements:
1. Population integrity (all 15 regions present)
2. Page identity (zero-based index 4, one-based 5, printed page 5)
3. Geometry distinction (detector pixel bbox vs padded crop pdf_rect)
4. Text intersection (all 15 report zero text-character intersections on source page)
5. OCR preservation (verbatim Pix2Text strings preserved)
6. Classification (all 15 classified as NEGATIVE_CONTROL_NON_MATH)
7. Expectation generation gating (expectation_generation_eligible == False)
8. Preservation eligibility (structural_preservation_eligible == False)
"""

import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "DATASETS" / "structural_preservation"
PAGE_OBS_PATH = DATA_DIR / "2009.00031_p005_page_observations.json"
REGION_ASSESS_PATH = DATA_DIR / "2009.00031_p005_region_assessments.json"


@pytest.fixture(scope="module")
def observation_data():
    assert PAGE_OBS_PATH.exists(), f"Page observation file missing: {PAGE_OBS_PATH}"
    with open(PAGE_OBS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def region_data():
    assert REGION_ASSESS_PATH.exists(), f"Region assessment file missing: {REGION_ASSESS_PATH}"
    with open(REGION_ASSESS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_population_integrity(region_data):
    """Requirement 1: All 15 original region IDs must remain present in order."""
    assert region_data["total_regions"] == 15
    regions = region_data["regions"]
    assert len(regions) == 15
    for i in range(15):
        expected_id = f"reg_2009_00031_p005_{i:02d}"
        assert regions[i]["region_id"] == expected_id


def test_page_identity(region_data, observation_data):
    """Requirement 2: Every region and page record points unambiguously to doc[4] / printed page 5."""
    page_id = region_data["page_identity"]
    assert page_id["document_id"] == "2009.00031"
    assert page_id["page_index_zero_based"] == 4
    assert page_id["page_number_one_based"] == 5
    assert page_id["printed_page_number"] == 5
    assert page_id["rotation"] == 0

    for reg in region_data["regions"]:
        src = reg["source"]
        assert src["document_id"] == "2009.00031"
        assert src["page_index_zero_based"] == 4
        assert src["page_number_one_based"] == 5
        assert src["printed_page_number"] == 5


def test_geometry_distinction(region_data):
    """Requirement 3: Detector coordinates (pixels) and crop rectangles (pts) must remain distinct."""
    for reg in region_data["regions"]:
        geom = reg["geometry"]
        assert geom["detector_coordinate_space"] == "detection_image_pixels"
        assert geom["pdf_coordinate_space"] == "mupdf_page_points"
        assert geom["detection_zoom"] == 4
        assert geom["crop_padding_points"] == 20.0
        
        # Detector box is 4-element int list [x, y, w, h]
        det_bbox = geom["detector_bbox_pixels"]
        assert len(det_bbox) == 4
        assert all(isinstance(v, int) for v in det_bbox)
        
        # Crop rect is 4-element float list [x0, y0, x1, y1]
        crop_rect = geom["crop_clip_pdf_rect"]
        assert len(crop_rect) == 4
        assert crop_rect[0] < crop_rect[2]
        assert crop_rect[1] < crop_rect[3]


def test_text_intersection_zero(region_data):
    """Requirement 4: All 15 regions report exactly zero text-character intersections on source page."""
    for reg in region_data["regions"]:
        src_obs = reg["source_observations"]
        assert src_obs["intersecting_character_count"] == 0
        assert src_obs["contained_character_count"] == 0
        assert src_obs["intersecting_char_ids"] == []
        assert src_obs["contained_char_ids"] == []


def test_raster_image_intersection(region_data):
    """Independent evidence: Every region must intersect with Figure 3 raster image objects.
    Verifies per-image intersection geometry fields: intersection_rect, areas, and
    intersection_over_region ratio (must be non-trivial > 0)."""
    for reg in region_data["regions"]:
        src_obs = reg["source_observations"]
        assert src_obs["intersecting_image_count"] > 0
        assert len(src_obs["intersecting_image_indices"]) > 0
        assert "spectral_plot" in src_obs["visual_source_type"]

        # Qualification 2: intersection geometry must be present and non-trivial
        details = src_obs["intersecting_image_details"]
        assert len(details) == src_obs["intersecting_image_count"], (
            f"Region {reg['region_id']}: details length {len(details)} "
            f"!= intersecting_image_count {src_obs['intersecting_image_count']}"
        )
        for d in details:
            assert "intersection_rect" in d
            assert "intersection_area_pts2" in d
            assert "region_area_pts2" in d
            assert "intersection_over_region" in d
            assert len(d["intersection_rect"]) == 4
            assert d["region_area_pts2"] > 0.0, f"Region {reg['region_id']}: region_area_pts2 == 0"
            assert d["intersection_area_pts2"] > 0.0, (
                f"Region {reg['region_id']}: intersection_area_pts2 == 0 (image index {d['image_index']})"
            )
            assert d["intersection_over_region"] > 0.0, (
                f"Region {reg['region_id']}: intersection_over_region == 0"
            )


def test_ocr_preservation(region_data):
    """Requirement 5: Original Pix2Text strings must be preserved verbatim without normalization."""
    for reg in region_data["regions"]:
        ocr = reg["ocr_observation"]
        assert ocr["raw_output_preserved"] is True
        assert ocr["engine"] == "Pix2Text 1.1.7"
        assert len(ocr["pix2text_result"]) > 0
        assert ocr["structural_fidelity"] == "CONTRADICTED_BY_SOURCE"


def test_classification_negative_control(region_data):
    """Requirement 6: All 15 retain NEGATIVE_CONTROL_NON_MATH classification with basis."""
    assert region_data["negative_control_count"] == 15
    for reg in region_data["regions"]:
        assess = reg["assessment"]
        assert assess["classification"] == "NEGATIVE_CONTROL_NON_MATH"
        assert "no_text_layer_intersection" in assess["classification_basis"]
        assert "visual_plot_content" in assess["classification_basis"]


def test_expectation_generation_gating(region_data):
    """Requirement 7: No structural expectations are generated from non-math negative controls."""
    for reg in region_data["regions"]:
        assess = reg["assessment"]
        assert assess["expectation_generation_eligible"] is False


def test_structural_preservation_eligibility(region_data):
    """Requirement 8: All 15 remain ineligible for mathematical preservation scoring."""
    assert region_data["structural_preservation_eligible_count"] == 0
    for reg in region_data["regions"]:
        assess = reg["assessment"]
        assert assess["structural_preservation_eligible"] is False


def test_page_observation_layer(observation_data):
    """Verifies complete raw character extraction of page doc[4]."""
    assert observation_data["total_glyphs_extracted"] == 4001
    assert observation_data["total_embedded_images"] == 3
    glyphs = observation_data["glyphs"]
    assert len(glyphs) == 4001
    
    first_g = glyphs[0]
    assert first_g["coordinate_space"] == "mupdf_page_points"
    assert first_g["source"] == "text_layer_mupdf"
    assert isinstance(first_g["font_size_pts"], float)
    assert first_g["font_size_pts"] > 0

