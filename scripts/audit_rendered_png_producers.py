#!/usr/bin/env python3
"""Audit of rendered PNG files and their producers in untracked/unstaged result sets.

Focuses on:
  1. DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr (Producer: scripts/targeted_depth_ocr.py)
  2. DATASETS/cross_reference/visual_recovery (Producer: scripts/cross_reference_pipeline.py)

Evaluates:
  - Image dimensions, aspect ratios, zoom factors
  - Border contamination and clipping (ink contact with image boundary)
  - Ink density, background statistics
  - OCR fidelity and hallucination susceptibility in targeted crops
  - Annotation color fidelity and bounding box distribution in visual recovery overlays
"""

import sys
import os
import json
from pathlib import Path
import numpy as np
import cv2

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
TARGETED_DIR = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr"
VISUAL_REC_DIR = REPO_ROOT / "DATASETS" / "cross_reference" / "visual_recovery"
OUTPUT_REPORT = REPO_ROOT / "DATASETS" / "audit_rendered_png_producers_report.json"


def analyze_crop_image(img_path: Path):
    """Analyze a single crop PNG for border touching, ink margins, and density."""
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        return {"error": f"Failed to load image: {img_path}"}

    h, w, c = img.shape
    file_size_kb = round(img_path.stat().st_size / 1024, 2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Inverted ink mask: foreground pixels (darker than 200)
    ink_mask = gray < 200
    ink_pixel_count = int(np.sum(ink_mask))
    total_pixels = h * w
    ink_ratio = round(ink_pixel_count / max(total_pixels, 1), 4)

    # Check border pixels (1px outer perimeter)
    top_border = np.sum(ink_mask[0, :])
    bottom_border = np.sum(ink_mask[h - 1, :])
    left_border = np.sum(ink_mask[:, 0])
    right_border = np.sum(ink_mask[:, w - 1])
    border_touch_1px = int(top_border + bottom_border + left_border + right_border)

    # Check 2px outer margin
    top_2px = np.sum(ink_mask[:2, :])
    bottom_2px = np.sum(ink_mask[h - 2 :, :])
    left_2px = np.sum(ink_mask[:, :2])
    right_2px = np.sum(ink_mask[:, w - 2 :])
    border_touch_2px = int(top_2px + bottom_2px + left_2px + right_2px)

    # Ink bounding box inside crop
    if ink_pixel_count > 0:
        ys, xs = np.where(ink_mask)
        min_y, max_y = int(np.min(ys)), int(np.max(ys))
        min_x, max_x = int(np.min(xs)), int(np.max(xs))
        margin_top = min_y
        margin_bottom = h - 1 - max_y
        margin_left = min_x
        margin_right = w - 1 - max_x
        min_margin = min(margin_top, margin_bottom, margin_left, margin_right)
    else:
        margin_top = margin_bottom = margin_left = margin_right = min_margin = -1

    return {
        "filename": img_path.name,
        "width": w,
        "height": h,
        "aspect_ratio": round(w / max(h, 1), 3),
        "file_size_kb": file_size_kb,
        "ink_ratio": ink_ratio,
        "border_touch_1px": border_touch_1px,
        "border_touch_2px": border_touch_2px,
        "has_border_contact": border_touch_1px > 0,
        "min_margin_px": min_margin,
        "margins": {
            "top": margin_top,
            "bottom": margin_bottom,
            "left": margin_left,
            "right": margin_right,
        },
    }


def audit_targeted_ocr():
    """Audit DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr."""
    results_json = TARGETED_DIR / "targeted_ocr_results.json"
    metadata = {}
    if results_json.exists():
        with open(results_json, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    all_pngs = sorted(TARGETED_DIR.rglob("*.png"))
    detection_pngs = [p for p in all_pngs if "_detection_z4.png" in p.name]
    crop_pngs = [p for p in all_pngs if "_z8.png" in p.name]
    tall_crops = [p for p in crop_pngs if "_tall_narrow_" in p.name]
    wide_crops = [p for p in crop_pngs if "_wide_" in p.name]

    # Map filename to OCR result from metadata
    ocr_map = {}
    if "results" in metadata:
        for page_key, pdata in metadata["results"].items():
            for r in pdata.get("regions", []):
                crop_path = r.get("crop_path", "")
                if crop_path:
                    fname = Path(crop_path).name
                    ocr_map[fname] = {
                        "ocr": r.get("pix2text_result", ""),
                        "bbox": r.get("bbox", []),
                        "type": r.get("type", ""),
                        "aspect_ratio": r.get("aspect_ratio", 0),
                        "paper_id": pdata.get("paper_id", ""),
                        "page_num": pdata.get("page_num", 0),
                    }

    analyzed_crops = []
    border_touch_count = 0
    empty_ocr_count = 0
    hallucinated_negative_count = 0

    for cp in crop_pngs:
        analysis = analyze_crop_image(cp)
        ocr_info = ocr_map.get(cp.name, {})
        analysis["ocr_result"] = ocr_info.get("ocr", "N/A")
        analysis["declared_type"] = ocr_info.get("type", "unknown")
        analysis["paper_id"] = ocr_info.get("paper_id", cp.parent.name)

        if analysis["has_border_contact"]:
            border_touch_count += 1
        if not analysis["ocr_result"] or analysis["ocr_result"].strip() == "":
            empty_ocr_count += 1

        # Check negative control paper 2009.00031 p5
        if analysis["paper_id"] == "2009.00031":
            if analysis["ocr_result"] and not analysis["ocr_result"].startswith("ERROR"):
                hallucinated_negative_count += 1

        analyzed_crops.append(analysis)

    return {
        "producer_script": "scripts/targeted_depth_ocr.py",
        "total_png_files": len(all_pngs),
        "detection_images_count": len(detection_pngs),
        "total_crop_images": len(crop_pngs),
        "tall_narrow_crops": len(tall_crops),
        "wide_crops": len(wide_crops),
        "crops_with_border_touch_1px": border_touch_count,
        "crops_with_border_touch_pct": round(border_touch_count / max(len(crop_pngs), 1) * 100, 1),
        "empty_ocr_count": empty_ocr_count,
        "empty_ocr_pct": round(empty_ocr_count / max(len(crop_pngs), 1) * 100, 1),
        "negative_control_2009_00031_hallucinations": hallucinated_negative_count,
        "sample_analyzed_crops": analyzed_crops,
    }


def audit_visual_recovery():
    """Audit DATASETS/cross_reference/visual_recovery."""
    all_pngs = sorted(VISUAL_REC_DIR.glob("*.png"))
    annotated_pngs = [p for p in all_pngs if p.name.startswith("annotated_")]

    analyzed_pages = []
    for ap in annotated_pngs:
        img = cv2.imread(str(ap), cv2.IMREAD_COLOR)
        if img is None:
            continue
        h, w, c = img.shape
        file_size_kb = round(ap.stat().st_size / 1024, 2)

        # Detect presence of colored bounding boxes in BGR:
        # Blue (text boundaries): B > 180, R < 50, G < 50
        # Green (clean isolated): G > 180, R < 50, B < 50
        # Red (no text / error): R > 180, G < 50, B < 50
        # Yellow (boundary touch): R > 180, G > 180, B < 50
        # Orange (prose contam): R > 180, G > 80, G < 160, B < 50
        # Purple (stretched / partial): R > 100, B > 100, G < 50

        blue_px = int(np.sum((img[:, :, 0] > 180) & (img[:, :, 2] < 50) & (img[:, :, 1] < 50)))
        green_px = int(np.sum((img[:, :, 1] > 160) & (img[:, :, 2] < 50) & (img[:, :, 0] < 50)))
        red_px = int(np.sum((img[:, :, 2] > 180) & (img[:, :, 1] < 50) & (img[:, :, 0] < 50)))
        yellow_px = int(np.sum((img[:, :, 2] > 180) & (img[:, :, 1] > 180) & (img[:, :, 0] < 50)))
        purple_px = int(np.sum((img[:, :, 2] > 100) & (img[:, :, 0] > 100) & (img[:, :, 1] < 50)))

        analyzed_pages.append({
            "filename": ap.name,
            "width": w,
            "height": h,
            "aspect_ratio": round(w / max(h, 1), 3),
            "file_size_kb": file_size_kb,
            "annotation_pixels": {
                "blue_text_boundary": blue_px,
                "green_clean_math": green_px,
                "red_no_text": red_px,
                "yellow_boundary_touch": yellow_px,
                "purple_stretched_partial": purple_px,
            },
            "has_blue_text_boxes": blue_px > 0,
            "has_region_boxes": (green_px + red_px + yellow_px + purple_px) > 0,
        })

    return {
        "producer_script": "scripts/cross_reference_pipeline.py",
        "total_png_files": len(all_pngs),
        "annotated_pages_count": len(annotated_pngs),
        "sample_analyzed_pages": analyzed_pages,
    }


def main():
    print("Auditing rendered PNG files and producers...")
    targeted_report = audit_targeted_ocr()
    visual_rec_report = audit_visual_recovery()

    full_report = {
        "report_version": "1.0",
        "audit_target": "Rendered PNG artifacts in DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr and DATASETS/cross_reference/visual_recovery",
        "producers": {
            "targeted_ocr": targeted_report,
            "visual_recovery": visual_rec_report,
        },
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print(f"\nAudit Report written to: {OUTPUT_REPORT}")
    print("\n--- SUMMARY OF FINDINGS ---")
    print(f"1. DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr:")
    print(f"   Producer: {targeted_report['producer_script']}")
    print(f"   Total PNGs: {targeted_report['total_png_files']} ({targeted_report['detection_images_count']} detection, {targeted_report['total_crop_images']} high-zoom crops)")
    print(f"   Tall narrow crops: {targeted_report['tall_narrow_crops']}")
    print(f"   Wide crops: {targeted_report['wide_crops']}")
    print(f"   Border touch (1px): {targeted_report['crops_with_border_touch_1px']} / {targeted_report['total_crop_images']} ({targeted_report['crops_with_border_touch_pct']}%)")
    print(f"   Empty OCR count: {targeted_report['empty_ocr_count']} / {targeted_report['total_crop_images']} ({targeted_report['empty_ocr_pct']}%)")
    print(f"   Negative control (2009.00031) hallucinations: {targeted_report['negative_control_2009_00031_hallucinations']}")

    print(f"\n2. DATASETS/cross_reference/visual_recovery:")
    print(f"   Producer: {visual_rec_report['producer_script']}")
    print(f"   Total PNGs: {visual_rec_report['total_png_files']} ({visual_rec_report['annotated_pages_count']} annotated)")
    has_boxes = sum(1 for p in visual_rec_report['sample_analyzed_pages'] if p['has_region_boxes'])
    print(f"   Pages with colored region boxes: {has_boxes} / {visual_rec_report['annotated_pages_count']}")


if __name__ == "__main__":
    main()

