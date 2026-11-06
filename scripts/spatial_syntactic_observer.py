#!/usr/bin/env python3
"""
Spatial-Syntactic Observer: Layer 1 Observation & Negative-Control Assessment

Extracts two decoupled datasets:
1. Page Observation Layer: Complete raw character observations from PyMuPDF rawdict
   (preserving glyph, font, size in points, baseline origin, bbox in mupdf_page_points).
2. Region Assessment Layer: Evaluates candidate regions against page observations and
   embedded raster images, classifying non-mathematical visual artifacts as negative controls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pymupdf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


@dataclass
class PageIdentity:
    document_id: str
    page_index_zero_based: int
    page_number_one_based: int
    printed_page_number: int
    pdf_sha256: str
    rotation: int
    page_rect_mupdf: List[float]
    mediabox: List[float]
    cropbox: List[float]
    mupdf_version: str


@dataclass
class GlyphObservation:
    glyph_id: str
    unicode_char: str
    font_name: str
    font_size_pts: float
    pdf_bbox: List[float]
    origin: List[float]
    block_index: int
    line_index: int
    span_index: int
    char_index: int
    reading_order: int
    coordinate_space: str = "mupdf_page_points"
    source: str = "text_layer_mupdf"


@dataclass
class RegionGeometry:
    detector_bbox_pixels: List[int]
    detector_coordinate_space: str
    detection_zoom: int
    crop_padding_points: float
    crop_clip_pdf_rect: List[float]
    crop_size_pixels: List[int]
    pdf_coordinate_space: str = "mupdf_page_points"


@dataclass
class ImageIntersectionGeometry:
    """Per-image intersection geometry for a region. All coordinates in mupdf_page_points."""
    image_index: int
    image_bbox: List[float]
    region_bbox: List[float]
    intersection_rect: List[float]
    intersection_area_pts2: float
    region_area_pts2: float
    intersection_over_region: float


@dataclass
class RegionSourceObservations:
    intersecting_character_count: int
    contained_character_count: int
    intersecting_image_count: int
    intersecting_image_indices: List[int]
    intersecting_image_details: List[Dict[str, Any]]
    visual_source_type: str
    intersecting_char_ids: List[str] = field(default_factory=list)
    contained_char_ids: List[str] = field(default_factory=list)


@dataclass
class RegionOcrObservation:
    engine: str
    raw_output_preserved: bool
    pix2text_result: str
    structural_fidelity: str


@dataclass
class RegionAssessment:
    classification: str
    classification_basis: List[str]
    structural_preservation_eligible: bool
    expectation_generation_eligible: bool


@dataclass
class RegionAssessmentRecord:
    region_id: str
    source: Dict[str, Any]
    region_type: str
    crop_path: str
    geometry: RegionGeometry
    source_observations: RegionSourceObservations
    ocr_observation: RegionOcrObservation
    assessment: RegionAssessment


def compute_sha256(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_page_observations(
    pdf_path: Path | str,
    page_index: int,
    document_id: str,
    printed_page_number: int,
) -> tuple[PageIdentity, List[GlyphObservation], List[Dict[str, Any]]]:
    """
    Extracts complete raw character observations from PyMuPDF rawdict without normalization.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pdf_sha256 = compute_sha256(pdf_path)
    doc = pymupdf.open(str(pdf_path))
    if page_index < 0 or page_index >= len(doc):
        doc.close()
        raise IndexError(f"Page index {page_index} out of range [0, {len(doc) - 1}]")

    page = doc[page_index]
    page_identity = PageIdentity(
        document_id=document_id,
        page_index_zero_based=page_index,
        page_number_one_based=page_index + 1,
        printed_page_number=printed_page_number,
        pdf_sha256=pdf_sha256,
        rotation=page.rotation,
        page_rect_mupdf=[page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1],
        mediabox=[page.mediabox.x0, page.mediabox.y0, page.mediabox.x1, page.mediabox.y1],
        cropbox=[page.cropbox.x0, page.cropbox.y0, page.cropbox.x1, page.cropbox.y1],
        mupdf_version=pymupdf.__version__,
    )

    # Extract embedded image metadata
    images_info = page.get_image_info()
    image_records = []
    for idx, img in enumerate(images_info):
        image_records.append({
            "image_index": idx,
            "bbox": [img["bbox"][0], img["bbox"][1], img["bbox"][2], img["bbox"][3]],
            "width": img.get("width"),
            "height": img.get("height"),
            "coordinate_space": "mupdf_page_points",
        })

    # Extract raw character stream
    raw = page.get_text("rawdict")
    glyph_records: List[GlyphObservation] = []
    global_char_idx = 0

    p_str = f"p{printed_page_number:03d}"
    doc_slug = document_id.replace(".", "_")

    for b_idx, block in enumerate(raw.get("blocks", [])):
        for l_idx, line in enumerate(block.get("lines", [])):
            for s_idx, span in enumerate(line.get("spans", [])):
                font_name = span.get("font", "")
                font_size = float(span.get("size", 0.0))
                for c_idx, char_obj in enumerate(span.get("chars", [])):
                    global_char_idx += 1
                    glyph_id = f"g_{doc_slug}_{p_str}_{global_char_idx:04d}"
                    glyph = GlyphObservation(
                        glyph_id=glyph_id,
                        unicode_char=char_obj.get("c", ""),
                        font_name=font_name,
                        font_size_pts=round(font_size, 3),
                        pdf_bbox=[round(float(v), 3) for v in char_obj.get("bbox", [])],
                        origin=[round(float(v), 3) for v in char_obj.get("origin", [])],
                        block_index=b_idx,
                        line_index=l_idx,
                        span_index=s_idx,
                        char_index=c_idx,
                        reading_order=global_char_idx,
                        coordinate_space="mupdf_page_points",
                        source="text_layer_mupdf",
                    )
                    glyph_records.append(glyph)

    doc.close()
    return page_identity, glyph_records, image_records


def assess_candidate_regions(
    pilot_regions: List[Dict[str, Any]],
    page_identity: PageIdentity,
    glyph_observations: List[GlyphObservation],
    image_observations: List[Dict[str, Any]],
) -> List[RegionAssessmentRecord]:
    """
    Assesses candidate detector regions against raw character observations and image bboxes.
    Explicitly tags regions intersecting raster plots with 0 text characters as negative controls.
    """
    assessed_regions: List[RegionAssessmentRecord] = []
    doc_slug = page_identity.document_id.replace(".", "_")
    p_str = f"p{page_identity.printed_page_number:03d}"

    for r in pilot_regions:
        reg_idx = int(r["region_index"])
        region_id = f"reg_{doc_slug}_{p_str}_{reg_idx:02d}"
        rtype = r.get("type", "unknown")
        pdf_rect = r.get("pdf_rect", [0.0, 0.0, 0.0, 0.0])
        rx0, ry0, rx1, ry1 = pdf_rect

        # 1. Character containment and intersection analysis
        intersecting_chars: List[str] = []
        contained_chars: List[str] = []

        for g in glyph_observations:
            gx0, gy0, gx1, gy1 = g.pdf_bbox
            # Intersect check
            if not (gx1 < rx0 or gx0 > rx1 or gy1 < ry0 or gy0 > ry1):
                intersecting_chars.append(g.glyph_id)
                # Strict containment check
                if gx0 >= rx0 and gy0 >= ry0 and gx1 <= rx1 and gy1 <= ry1:
                    contained_chars.append(g.glyph_id)

        # 2. Image object intersection analysis (with per-image geometry)
        intersecting_images: List[int] = []
        intersecting_image_details: List[Dict[str, Any]] = []
        region_area = max(0.0, (rx1 - rx0)) * max(0.0, (ry1 - ry0))
        for img in image_observations:
            ix0, iy0, ix1, iy1 = img["bbox"]
            if not (ix1 < rx0 or ix0 > rx1 or iy1 < ry0 or iy0 > ry1):
                img_idx = int(img["image_index"])
                intersecting_images.append(img_idx)
                inter_x0 = max(rx0, ix0)
                inter_y0 = max(ry0, iy0)
                inter_x1 = min(rx1, ix1)
                inter_y1 = min(ry1, iy1)
                inter_w = max(0.0, inter_x1 - inter_x0)
                inter_h = max(0.0, inter_y1 - inter_y0)
                inter_area = inter_w * inter_h
                iog = round(inter_area / region_area, 6) if region_area > 0.0 else 0.0
                detail = asdict(ImageIntersectionGeometry(
                    image_index=img_idx,
                    image_bbox=[round(v, 3) for v in [ix0, iy0, ix1, iy1]],
                    region_bbox=[round(v, 3) for v in [rx0, ry0, rx1, ry1]],
                    intersection_rect=[round(v, 3) for v in [inter_x0, inter_y0, inter_x1, inter_y1]],
                    intersection_area_pts2=round(inter_area, 3),
                    region_area_pts2=round(region_area, 3),
                    intersection_over_region=iog,
                ))
                intersecting_image_details.append(detail)

        # 3. Geometry mapping
        geometry = RegionGeometry(
            detector_bbox_pixels=r.get("bbox", [0, 0, 0, 0]),
            detector_coordinate_space="detection_image_pixels",
            detection_zoom=4,
            crop_padding_points=20.0,
            crop_clip_pdf_rect=pdf_rect,
            crop_size_pixels=r.get("crop_size", [0, 0]),
            pdf_coordinate_space="mupdf_page_points",
        )

        # 4. Source classification & basis
        has_images = len(intersecting_images) > 0
        has_text = len(intersecting_chars) > 0

        if has_images and not has_text:
            visual_type = "spectral_plot_subpanel" if rtype == "tall_narrow" else "spectral_plot_panel"
            classification = "NEGATIVE_CONTROL_NON_MATH"
            basis = [
                "visual_plot_content",
                "no_text_layer_intersection",
                "no_equation_structure_observed",
                f"intersects_raster_images_{intersecting_images}",
            ]
            ocr_fidelity = "CONTRADICTED_BY_SOURCE"
            eligible = False
        elif has_text:
            visual_type = "text_or_formula_candidate"
            classification = "PENDING_CLASSIFICATION"
            basis = ["text_layer_intersection_observed"]
            ocr_fidelity = "UNVERIFIED"
            eligible = True
        else:
            visual_type = "whitespace_or_vector"
            classification = "NEGATIVE_CONTROL_NON_MATH"
            basis = ["no_text_layer_intersection", "no_image_intersection"]
            ocr_fidelity = "CONTRADICTED_BY_SOURCE"
            eligible = False

        source_obs = RegionSourceObservations(
            intersecting_character_count=len(intersecting_chars),
            contained_character_count=len(contained_chars),
            intersecting_image_count=len(intersecting_images),
            intersecting_image_indices=intersecting_images,
            intersecting_image_details=intersecting_image_details,
            visual_source_type=visual_type,
            intersecting_char_ids=intersecting_chars,
            contained_char_ids=contained_chars,
        )

        ocr_obs = RegionOcrObservation(
            engine="Pix2Text 1.1.7",
            raw_output_preserved=True,
            pix2text_result=r.get("pix2text_result", ""),
            structural_fidelity=ocr_fidelity,
        )

        assessment = RegionAssessment(
            classification=classification,
            classification_basis=basis,
            structural_preservation_eligible=eligible,
            expectation_generation_eligible=eligible,
        )

        rec = RegionAssessmentRecord(
            region_id=region_id,
            source={
                "document_id": page_identity.document_id,
                "pdf_sha256": page_identity.pdf_sha256,
                "page_index_zero_based": page_identity.page_index_zero_based,
                "page_number_one_based": page_identity.page_number_one_based,
                "printed_page_number": page_identity.printed_page_number,
            },
            region_type=rtype,
            crop_path=r.get("crop_path", ""),
            geometry=geometry,
            source_observations=source_obs,
            ocr_observation=ocr_obs,
            assessment=assessment,
        )
        assessed_regions.append(rec)

    return assessed_regions


def run_observation_pipeline(
    pdf_path: Path | str,
    pilot_json_path: Path | str,
    output_dir: Path | str,
    document_id: str = "2009.00031",
    page_index: int = 4,
    printed_page_number: int = 5,
) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(pilot_json_path, "r", encoding="utf-8") as f:
        pilot_data = json.load(f)["results"][f"{document_id}_p{printed_page_number}"]

    page_id, glyphs, images = extract_page_observations(
        pdf_path=pdf_path,
        page_index=page_index,
        document_id=document_id,
        printed_page_number=printed_page_number,
    )

    regions = assess_candidate_regions(
        pilot_regions=pilot_data["regions"],
        page_identity=page_id,
        glyph_observations=glyphs,
        image_observations=images,
    )

    # Serialize Dataset 1: Page Observations
    page_obs_file = output_dir / f"{document_id}_p{printed_page_number:03d}_page_observations.json"
    with open(page_obs_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "contract_version": "1.0",
                "page_identity": asdict(page_id),
                "total_glyphs_extracted": len(glyphs),
                "total_embedded_images": len(images),
                "embedded_images": images,
                "glyphs": [asdict(g) for g in glyphs],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Serialize Dataset 2: Region Assessments
    region_assess_file = output_dir / f"{document_id}_p{printed_page_number:03d}_region_assessments.json"
    with open(region_assess_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "contract_version": "1.0",
                "page_identity": asdict(page_id),
                "total_regions": len(regions),
                "negative_control_count": sum(
                    1 for r in regions if r.assessment.classification == "NEGATIVE_CONTROL_NON_MATH"
                ),
                "structural_preservation_eligible_count": sum(
                    1 for r in regions if r.assessment.structural_preservation_eligible
                ),
                "regions": [asdict(r) for r in regions],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return page_obs_file, region_assess_file


def main():
    parser = argparse.ArgumentParser(description="Spatial-Syntactic Observer: Observation & Assessment Layer")
    parser.add_argument("--pdf", default="DATASETS/benchmark_pdfs/2009.00031.pdf")
    parser.add_argument(
        "--pilot-results", default="DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/targeted_ocr_results.json"
    )
    parser.add_argument("--output-dir", default="DATASETS/structural_preservation")
    parser.add_argument("--doc-id", default="2009.00031")
    parser.add_argument("--page-index", type=int, default=4)
    parser.add_argument("--printed-page", type=int, default=5)
    args = parser.parse_args()

    page_file, reg_file = run_observation_pipeline(
        pdf_path=args.pdf,
        pilot_json_path=args.pilot_results,
        output_dir=args.output_dir,
        document_id=args.doc_id,
        page_index=args.page_index,
        printed_page_number=args.printed_page,
    )
    print(f"Observation layer complete:")
    print(f"  Page Observations:  {page_file}")
    print(f"  Region Assessments: {reg_file}")


if __name__ == "__main__":
    main()

