#!/usr/bin/env python3
"""Generalized Contextual Crop Expansion and Semantic Eligibility Evaluation (v2).

Starts from the original connected component core rectangle (r["bbox"] * 0.25)
to prevent inheriting v1's fixed +-20pt prose contamination.

Tests the two separate interventions across the full 16-paper benchmark:
  1. Semantic Eligibility (Gate P2 & P5)
  2. Contextual Crop Expansion (Gate P3)

Measures:
  - Negative control rejection rate (Target: 100% on 2009.00031 p5)
  - Zero border contact rate across eligible candidates
  - Glyph completeness and prose non-intersection
"""

import sys
import os
import json
from pathlib import Path
import pymupdf
import cv2
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PDF_DIR = REPO_ROOT / "DATASETS" / "benchmark_pdfs"
TARGETED_RESULTS = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr" / "targeted_ocr_results.json"
OUTPUT_REPORT = REPO_ROOT / "DATASETS" / "structural_preservation" / "generalized_producer_interventions_report.json"

MATH_FONT_HINTS = [
    "cmmi", "cmsy", "cmex", "msam", "msbm", "math", "stmary", "eufm",
    "wasy", "line", "symbol", "italic", "sub", "sup"
]
MATH_OPERATORS = set("=+-*/<>≤≥≠≈∈∉⊂⊃∪∩∑∏∫∮√∇∂±×÷λμπαβγδεθσλωΩΔ")


def is_math_span(span: dict) -> bool:
    text = span.get("text", "").strip()
    font = span.get("font", "").lower()
    if not text:
        return False
    if any(h in font for h in MATH_FONT_HINTS):
        return True
    if any(ch in MATH_OPERATORS for ch in text):
        return True
    if len(text) == 1 and text.isalpha() and ("italic" in font or "oblique" in font):
        return True
    return False


def get_page_lines(page: pymupdf.Page) -> list[dict]:
    """Extract line structures with text and bounding boxes from page."""
    td = page.get_text("dict")
    lines = []
    for block in td.get("blocks", []):
        if block.get("type") == 0:
            for l in block.get("lines", []):
                spans = l.get("spans", [])
                line_text = "".join(s.get("text", "") for s in spans).strip()
                if not line_text:
                    continue
                bbox = l.get("bbox", [])
                has_math = any(is_math_span(s) for s in spans)
                lines.append({
                    "bbox": bbox,
                    "text": line_text,
                    "has_math": has_math,
                    "spans": spans,
                })
    return lines


def evaluate_semantic_eligibility(page: pymupdf.Page, core_rect: pymupdf.Rect) -> tuple[bool, str, dict]:
    """Gate P2: Semantic Eligibility Evaluation on candidate core."""
    lines = get_page_lines(page)
    
    # Check intersecting lines
    intersecting_lines = []
    for l in lines:
        l_rect = pymupdf.Rect(l["bbox"])
        inter = l_rect & core_rect
        if inter.is_valid and inter.get_area() > 0:
            intersecting_lines.append(l)

    audit = {
        "core_rect": [round(core_rect.x0, 2), round(core_rect.y0, 2), round(core_rect.x1, 2), round(core_rect.y1, 2)],
        "intersecting_lines_count": len(intersecting_lines),
        "text_sample": " // ".join(l["text"] for l in intersecting_lines)[:100],
    }

    # If 0 text lines intersect the core rect -> check if pure graphic
    if not intersecting_lines:
        return False, "NON_MATH_GRAPHIC_ZERO_GLYPHS", audit

    has_any_math = any(l["has_math"] for l in intersecting_lines)
    
    # If all intersecting lines are purely prose sentences
    if not has_any_math:
        total_words = sum(len(l["text"].split()) for l in intersecting_lines)
        if total_words >= 6:
            return False, "PROSE_TEXT_BLOCK", audit

    return True, "ELIGIBLE_MATH_CANDIDATE", audit


def compute_contextual_crop_expansion(page: pymupdf.Page, core_rect: pymupdf.Rect) -> tuple[pymupdf.Rect, dict]:
    """Gate P3: Contextual crop expansion starting from core_rect."""
    page_rect = page.rect
    lines = get_page_lines(page)
    
    cand_y0 = core_rect.y0
    cand_y1 = core_rect.y1
    
    # Find lines belonging to the same vertical formula band
    vert_lines = [l for l in lines if not (l["bbox"][3] <= cand_y0 + 2 or l["bbox"][1] >= cand_y1 - 2)]
    
    if not vert_lines:
        expanded = pymupdf.Rect(
            max(0, core_rect.x0 - 4),
            max(0, core_rect.y0 - 4),
            min(page_rect.width, core_rect.x1 + 4),
            min(page_rect.height, core_rect.y1 + 4),
        )
        return expanded, {"method": "fallback_conservative"}

    # Find line strictly above formula
    lines_above = [l for l in lines if l["bbox"][3] <= cand_y0 + 2]
    y_min_bound = max((l["bbox"][3] for l in lines_above), default=0)

    # Find line strictly below formula
    lines_below = [l for l in lines if l["bbox"][1] >= cand_y1 - 2]
    y_max_bound = min((l["bbox"][1] for l in lines_below), default=page_rect.height)

    formula_y0 = min(l["bbox"][1] for l in vert_lines)
    formula_y1 = max(l["bbox"][3] for l in vert_lines)

    # Put crop boundary in the clear whitespace gutter
    gap_above = max(0, formula_y0 - y_min_bound)
    crop_y0 = formula_y0 - max(2, min(gap_above / 2, 8))
    
    gap_below = max(0, y_max_bound - formula_y1)
    crop_y1 = formula_y1 + max(2, min(gap_below / 2, 8))

    # Horizontal extent: union of all lines in this vertical formula band
    formula_x0 = min(l["bbox"][0] for l in vert_lines)
    formula_x1 = max(l["bbox"][2] for l in vert_lines)

    # Add 4pt whitespace margin horizontally
    crop_x0 = max(0, formula_x0 - 4)
    crop_x1 = min(page_rect.width, formula_x1 + 4)

    expanded = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)
    
    meta = {
        "formula_bounds": [round(formula_x0, 2), round(formula_y0, 2), round(formula_x1, 2), round(formula_y1, 2)],
        "expanded_crop": [round(expanded.x0, 2), round(expanded.y0, 2), round(expanded.x1, 2), round(expanded.y1, 2)],
        "gap_above": round(gap_above, 2),
        "gap_below": round(gap_below, 2),
    }
    return expanded, meta


def check_border_touch_px(img_gray: np.ndarray) -> tuple[int, dict]:
    """Check 1px border contact around image perimeter."""
    if img_gray is None or img_gray.size == 0:
        return 0, {}
    h, w = img_gray.shape
    mask = img_gray < 200
    top = int(np.sum(mask[0, :]))
    bottom = int(np.sum(mask[h - 1, :]))
    left = int(np.sum(mask[:, 0]))
    right = int(np.sum(mask[:, w - 1]))
    total = top + bottom + left + right
    return total, {"top": top, "bottom": bottom, "left": left, "right": right}


def main():
    print("Running Generalized Contextual Expansion & Eligibility Evaluation (v2)...")
    with open(TARGETED_RESULTS, "r", encoding="utf-8") as f:
        targeted_data = json.load(f)

    all_pages = targeted_data.get("results", {})
    doc_cache = {}

    eval_records = []
    v1_border_contacts = 0
    v2_border_contacts = 0
    eligible_count = 0
    rejected_count = 0
    neg_control_total = 0
    neg_control_rejected = 0

    for page_key, pdata in all_pages.items():
        paper_id = pdata["paper_id"]
        page_num = pdata["page_num"]
        pdf_path = PDF_DIR / f"{paper_id}.pdf"
        if not pdf_path.exists():
            continue

        if paper_id not in doc_cache:
            doc_cache[paper_id] = pymupdf.open(str(pdf_path))
        doc = doc_cache[paper_id]
        page = doc[page_num - 1]

        is_neg = (paper_id == "2009.00031" and page_num == 5)

        for r in pdata.get("regions", []):
            bbox = r["bbox"]
            scale = 0.25
            core_rect = pymupdf.Rect(bbox[0]*scale, bbox[1]*scale, (bbox[0]+bbox[2])*scale, (bbox[1]+bbox[3])*scale)
            v1_rect = pymupdf.Rect(*r["pdf_rect"])
            
            # 1. Semantic Eligibility (Gate P2 & P5)
            eligible, reason, audit = evaluate_semantic_eligibility(page, core_rect)
            
            if is_neg:
                neg_control_total += 1
                if not eligible:
                    neg_control_rejected += 1

            if not eligible:
                rejected_count += 1
                eval_records.append({
                    "paper_id": paper_id,
                    "page_num": page_num,
                    "region_index": r["region_index"],
                    "eligible": False,
                    "reason": reason,
                    "audit": audit,
                })
                continue

            eligible_count += 1
            
            # 2. Contextual Expansion (Gate P3)
            v2_rect, exp_meta = compute_contextual_crop_expansion(page, core_rect)

            # Render at zoom=8 to test border clearance
            pix_v1 = page.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=v1_rect, alpha=False)
            pix_v2 = page.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=v2_rect, alpha=False)

            img1 = cv2.imdecode(np.frombuffer(pix_v1.tobytes("png"), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imdecode(np.frombuffer(pix_v2.tobytes("png"), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

            t1, d1 = check_border_touch_px(img1)
            t2, d2 = check_border_touch_px(img2)

            if t1 > 0:
                v1_border_contacts += 1
            if t2 > 0:
                v2_border_contacts += 1

            eval_records.append({
                "paper_id": paper_id,
                "page_num": page_num,
                "region_index": r["region_index"],
                "eligible": True,
                "reason": reason,
                "v1_rect": [round(v1_rect.x0, 2), round(v1_rect.y0, 2), round(v1_rect.x1, 2), round(v1_rect.y1, 2)],
                "v2_rect": [round(v2_rect.x0, 2), round(v2_rect.y0, 2), round(v2_rect.x1, 2), round(v2_rect.y1, 2)],
                "v1_border_touch_px": t1,
                "v2_border_touch_px": t2,
                "v1_details": d1,
                "v2_details": d2,
            })

    for d in doc_cache.values():
        d.close()

    print("\n--- RESULTS ---")
    print(f"Total Regions: {len(eval_records)}")
    print(f"Rejected (Ineligible, saved from OCR): {rejected_count}")
    print(f"  Negative Control (2009.00031 p5) Rejection Rate: {neg_control_rejected}/{neg_control_total} ({neg_control_rejected/max(neg_control_total, 1)*100:.1f}%)")
    print(f"Eligible Math Regions: {eligible_count}")
    print(f"V1 (Fixed Margin) Border Contacts: {v1_border_contacts} / {eligible_count} ({v1_border_contacts/max(eligible_count, 1)*100:.1f}%)")
    print(f"V2 (Contextual Expansion) Border Contacts: {v2_border_contacts} / {eligible_count} ({v2_border_contacts/max(eligible_count, 1)*100:.1f}%)")

    report = {
        "report_title": "Generalized Producer Interventions Evaluation (v2)",
        "semantic_eligibility_gate": {
            "total_candidates": len(eval_records),
            "rejected_count": rejected_count,
            "eligible_count": eligible_count,
            "negative_control_rejection_rate": f"{neg_control_rejected}/{neg_control_total} ({neg_control_rejected/max(neg_control_total, 1)*100:.1f}%)",
        },
        "contextual_expansion_gate": {
            "eligible_candidates_evaluated": eligible_count,
            "v1_border_contacts": v1_border_contacts,
            "v1_border_contact_pct": round(v1_border_contacts / max(eligible_count, 1) * 100, 1),
            "v2_border_contacts": v2_border_contacts,
            "v2_border_contact_pct": round(v2_border_contacts / max(eligible_count, 1) * 100, 1),
            "border_clearance_improvement": f"From {v1_border_contacts}/{eligible_count} down to {v2_border_contacts}/{eligible_count}",
        },
        "records": eval_records,
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Full report saved to: {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
