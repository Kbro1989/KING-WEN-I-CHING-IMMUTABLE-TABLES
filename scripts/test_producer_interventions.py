#!/usr/bin/env python3
"""Producer-Integrity Interventions: Isolated Experiments.

Evaluates two separate interventions against the frozen baseline manifest:
  Intervention 1: Semantic Eligibility Gate (Gate P2 & P5)
    - Independent text/glyph analysis before OCR
    - Strict non-math graphic rejection (suppressing plot ticks/axes)
    - Rejection audit logging (Gate P5)
    
  Intervention 2: Contextual Crop Expansion (Gate P3)
    - Glyph-aware cluster expansion replacing fixed +-20pt margins
    - Prevents slicing through matrix columns and adjacent characters
    - Evaluates border contact reduction and glyph completeness

Evaluates on the exact same 16 benchmark papers and pages as the baseline.
"""

import sys
import os
import json
import re
from pathlib import Path
import pymupdf
import cv2
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PDF_DIR = REPO_ROOT / "DATASETS" / "benchmark_pdfs"
BASELINE_MANIFEST = REPO_ROOT / "DATASETS" / "structural_preservation" / "producer_integrity_baseline_manifest.json"
TARGETED_RESULTS = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr" / "targeted_ocr_results.json"
OUTPUT_REPORT = REPO_ROOT / "DATASETS" / "structural_preservation" / "producer_interventions_evaluation_report.json"

MATH_FONT_HINTS = [
    "cmmi", "cmsy", "cmex", "msam", "msbm", "math", "stmary", "eufm",
    "wasy", "line", "symbol", "italic", "sub", "sup"
]

MATH_OPERATORS = set("=+-*/<>≤≥≠≈∈∉⊂⊃∪∩∑∏∫∮√∇∂±×÷λμπαβγδεθσλωΩΔ")


def is_math_span(span: dict) -> bool:
    """Assess whether a text span carries mathematical characteristics."""
    text = span.get("text", "").strip()
    font = span.get("font", "").lower()
    
    if not text:
        return False
        
    # Check font name
    for hint in MATH_FONT_HINTS:
        if hint in font:
            return True
            
    # Check for math operators or single letter variables
    if any(ch in MATH_OPERATORS for ch in text):
        return True
        
    # Single italic or isolated letter (variable)
    if len(text) == 1 and text.isalpha():
        if "italic" in font or "oblique" in font:
            return True
            
    return False


def evaluate_semantic_eligibility(page: pymupdf.Page, rect: pymupdf.Rect) -> tuple[bool, str, dict]:
    """Gate P2: Evaluate semantic eligibility of a candidate bounding box.
    
    Returns:
      (is_eligible, reason, audit_metadata)
    """
    # 1. Extract words and spans intersecting the candidate rect
    words = page.get_text("words", clip=rect)
    spans_info = []
    
    text_page = page.get_text("dict", clip=rect)
    total_spans = 0
    math_spans = 0
    raw_chars = 0
    text_content = []
    
    for block in text_page.get("blocks", []):
        if block.get("type") == 0:  # text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    total_spans += 1
                    txt = span.get("text", "")
                    raw_chars += len(txt.strip())
                    text_content.append(txt)
                    if is_math_span(span):
                        math_spans += 1
                    spans_info.append({
                        "text": txt,
                        "font": span.get("font", ""),
                        "size": span.get("size", 0),
                        "bbox": span.get("bbox", []),
                    })

    joined_text = " ".join(text_content).strip()
    
    audit_data = {
        "word_count": len(words),
        "span_count": total_spans,
        "math_span_count": math_spans,
        "char_count": raw_chars,
        "text_sample": joined_text[:120],
        "rect": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
    }
    
    # RULE 1: Pure graphic / zero glyphs -> REJECT
    if raw_chars == 0 and len(words) == 0:
        return False, "NON_MATH_GRAPHIC_ZERO_GLYPHS", audit_data
        
    # RULE 2: Prose paragraph -> If long english words and no math spans -> REJECT
    words_list = joined_text.split()
    avg_word_len = np.mean([len(w) for w in words_list]) if words_list else 0
    if len(words_list) >= 8 and math_spans == 0 and avg_word_len > 3.5:
        # Check if contains standard english prose words
        prose_stops = {"the", "of", "and", "in", "to", "for", "with", "that", "this", "from", "as", "by"}
        stop_matches = [w.lower() for w in words_list if w.lower() in prose_stops]
        if len(stop_matches) >= 2:
            return False, "PROSE_TEXT_BLOCK", audit_data

    # RULE 3: Check for isolated plot axis label without math structure
    if len(words_list) == 1 and not math_spans:
        # Check if word is purely numeric or simple non-math label like 'Figure', 'Page', 'arXiv'
        if words_list[0].isdigit() and (rect.height > 100 or rect.width > 200):
            return False, "GRAPHIC_AXIS_TICK_LABEL", audit_data

    # Otherwise accepted as candidate with math potential
    return True, "ELIGIBLE_MATH_CANDIDATE", audit_data


def compute_contextual_crop_expansion(page: pymupdf.Page, orig_rect: pymupdf.Rect) -> tuple[pymupdf.Rect, dict]:
    """Gate P3: Contextual crop expansion based on local glyph clusters.
    
    Expands boundary to preserve complete tokens and delimiters without slicing.
    """
    page_rect = page.rect
    
    # Search in an expanded neighborhood (+-40 pt)
    search_rect = pymupdf.Rect(
        max(0, orig_rect.x0 - 40),
        max(0, orig_rect.y0 - 20),
        min(page_rect.width, orig_rect.x1 + 40),
        min(page_rect.height, orig_rect.y1 + 20),
    )
    
    # Find all words/spans that intersect orig_rect
    dict_content = page.get_text("dict", clip=search_rect)
    intersecting_span_boxes = []
    neighboring_prose_boxes = []
    
    for block in dict_content.get("blocks", []):
        if block.get("type") == 0:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    sbox = pymupdf.Rect(span["bbox"])
                    # Check overlap with orig_rect
                    inter = sbox & orig_rect
                    if inter.is_valid and inter.get_area() > 0:
                        intersecting_span_boxes.append(sbox)
                    elif is_math_span(span):
                        # Closely adjacent math span (e.g. adjacent matrix column or sign)
                        if abs(sbox.x0 - orig_rect.x1) < 15 or abs(orig_rect.x0 - sbox.x1) < 15:
                            intersecting_span_boxes.append(sbox)
                    else:
                        neighboring_prose_boxes.append(sbox)

    # Compute bounding union of all intersecting spans
    if intersecting_span_boxes:
        union_rect = intersecting_span_boxes[0]
        for sb in intersecting_span_boxes[1:]:
            union_rect = union_rect | sb
            
        # Ensure we cover at least the orig_rect
        expanded = union_rect | orig_rect
        
        # Add safety margin (6pt horizontal, 4pt vertical)
        expanded.x0 = max(0, expanded.x0 - 6)
        expanded.y0 = max(0, expanded.y0 - 4)
        expanded.x1 = min(page_rect.width, expanded.x1 + 6)
        expanded.y1 = min(page_rect.height, expanded.y1 + 4)
    else:
        # Fallback to conservative margin (8pt instead of 20pt)
        expanded = pymupdf.Rect(
            max(0, orig_rect.x0 - 8),
            max(0, orig_rect.y0 - 8),
            min(page_rect.width, orig_rect.x1 + 8),
            min(page_rect.height, orig_rect.y1 + 8),
        )

    # Constrain against neighboring prose
    for pb in neighboring_prose_boxes:
        if pb.x1 <= orig_rect.x0 and expanded.x0 < pb.x1:
            expanded.x0 = pb.x1 + 2
        if pb.x0 >= orig_rect.x1 and expanded.x1 > pb.x0:
            expanded.x1 = pb.x0 - 2

    metadata = {
        "orig_rect": [round(orig_rect.x0, 2), round(orig_rect.y0, 2), round(orig_rect.x1, 2), round(orig_rect.y1, 2)],
        "expanded_rect": [round(expanded.x0, 2), round(expanded.y0, 2), round(expanded.x1, 2), round(expanded.y1, 2)],
        "intersecting_spans": len(intersecting_span_boxes),
        "neighboring_prose": len(neighboring_prose_boxes),
    }
    return expanded, metadata


def main():
    print("Evaluating Producer-Integrity Interventions...")
    
    with open(TARGETED_RESULTS, "r", encoding="utf-8") as f:
        targeted_data = json.load(f)

    # Load all baseline regions
    all_pages = targeted_data.get("results", {})
    
    # -------------------------------------------------------------
    # INTERVENTION 1: Semantic Eligibility Gate (Gate P2 & P5)
    # -------------------------------------------------------------
    print("\n--- Running Intervention 1: Semantic Eligibility Gate ---")
    eligibility_results = []
    rejected_count = 0
    accepted_count = 0
    negative_control_rejected = 0
    negative_control_total = 0
    
    doc_cache = {}

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
        
        is_neg_control = (paper_id == "2009.00031" and page_num == 5)
        
        for r in pdata.get("regions", []):
            pdf_rect_coords = r.get("pdf_rect", [])
            if len(pdf_rect_coords) != 4:
                continue
            orig_rect = pymupdf.Rect(*pdf_rect_coords)
            
            is_eligible, reason, audit = evaluate_semantic_eligibility(page, orig_rect)
            
            if is_neg_control:
                negative_control_total += 1
                if not is_eligible:
                    negative_control_rejected += 1
                    
            if is_eligible:
                accepted_count += 1
            else:
                rejected_count += 1
                
            eligibility_results.append({
                "paper_id": paper_id,
                "page_num": page_num,
                "region_index": r.get("region_index", 0),
                "type": r.get("type", "unknown"),
                "is_negative_control": is_neg_control,
                "eligible": is_eligible,
                "reason": reason,
                "audit": audit,
                "original_ocr": r.get("pix2text_result", ""),
            })

    print(f"Total candidate regions evaluated: {len(eligibility_results)}")
    print(f"Accepted candidates (eligible for OCR): {accepted_count}")
    print(f"Rejected candidates (suppressed from OCR): {rejected_count}")
    print(f"Negative control (2009.00031 p5) rejections: {negative_control_rejected} / {negative_control_total} ({negative_control_rejected / max(negative_control_total, 1) * 100:.1f}%)")

    # -------------------------------------------------------------
    # INTERVENTION 2: Contextual Crop Expansion (Gate P3)
    # -------------------------------------------------------------
    print("\n--- Running Intervention 2: Contextual Crop Expansion ---")
    expansion_results = []
    border_touch_v1 = 0
    border_touch_v2 = 0
    evaluated_crops = 0

    for item in eligibility_results:
        # Only evaluate contextual expansion on eligible math candidates
        if not item["eligible"]:
            continue
            
        paper_id = item["paper_id"]
        page_num = item["page_num"]
        doc = doc_cache[paper_id]
        page = doc[page_num - 1]
        
        coords = item["audit"]["rect"]
        orig_rect = pymupdf.Rect(*coords)
        
        # Contextual expansion
        context_rect, exp_meta = compute_contextual_crop_expansion(page, orig_rect)
        
        # Render both at zoom=8 to check border touch
        pix_v1 = page.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=orig_rect, alpha=False)
        pix_v2 = page.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=context_rect, alpha=False)
        
        img1 = cv2.imdecode(np.frombuffer(pix_v1.tobytes("png"), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imdecode(np.frombuffer(pix_v2.tobytes("png"), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        
        def check_border(gray_img):
            if gray_img is None or gray_img.size == 0:
                return 0
            h, w = gray_img.shape
            mask = gray_img < 200
            t = np.sum(mask[0, :])
            b = np.sum(mask[h - 1, :])
            l = np.sum(mask[:, 0])
            r = np.sum(mask[:, w - 1])
            return int(t + b + l + r)

        b1 = check_border(img1)
        b2 = check_border(img2)
        
        if b1 > 0:
            border_touch_v1 += 1
        if b2 > 0:
            border_touch_v2 += 1
        evaluated_crops += 1
        
        expansion_results.append({
            "paper_id": paper_id,
            "page_num": page_num,
            "region_index": item["region_index"],
            "v1_rect": coords,
            "v2_context_rect": exp_meta["expanded_rect"],
            "v1_border_touch_px": b1,
            "v2_border_touch_px": b2,
            "border_improved": b2 < b1 or (b1 > 0 and b2 == 0),
        })

    for d in doc_cache.values():
        d.close()

    print(f"Eligible crops evaluated for border contact: {evaluated_crops}")
    print(f"V1 (Fixed Margin) crops with 1px border contact: {border_touch_v1} / {evaluated_crops} ({border_touch_v1 / max(evaluated_crops, 1) * 100:.1f}%)")
    print(f"V2 (Contextual Expansion) crops with 1px border contact: {border_touch_v2} / {evaluated_crops} ({border_touch_v2 / max(evaluated_crops, 1) * 100:.1f}%)")
    improved_crops = sum(1 for e in expansion_results if e["border_improved"])
    print(f"Crops with improved border clearance: {improved_crops} / {evaluated_crops} ({improved_crops / max(evaluated_crops, 1) * 100:.1f}%)")

    # Persist report
    full_report = {
        "evaluation_title": "Isolated Producer-Integrity Interventions Evaluation",
        "timestamp": "2026-11-05T22:00:00Z",
        "intervention_1_semantic_eligibility": {
            "total_candidates": len(eligibility_results),
            "accepted_eligible": accepted_count,
            "rejected_ineligible": rejected_count,
            "negative_control_2009_00031_p5": {
                "total_candidates": negative_control_total,
                "rejected": negative_control_rejected,
                "rejection_rate_pct": round(negative_control_rejected / max(negative_control_total, 1) * 100, 1),
            },
            "rejections_by_reason": {
                "NON_MATH_GRAPHIC_ZERO_GLYPHS": sum(1 for r in eligibility_results if r["reason"] == "NON_MATH_GRAPHIC_ZERO_GLYPHS"),
                "PROSE_TEXT_BLOCK": sum(1 for r in eligibility_results if r["reason"] == "PROSE_TEXT_BLOCK"),
                "GRAPHIC_AXIS_TICK_LABEL": sum(1 for r in eligibility_results if r["reason"] == "GRAPHIC_AXIS_TICK_LABEL"),
            },
        },
        "intervention_2_contextual_crop_expansion": {
            "evaluated_crops": evaluated_crops,
            "v1_fixed_margin_border_touch_count": border_touch_v1,
            "v1_border_touch_pct": round(border_touch_v1 / max(evaluated_crops, 1) * 100, 1),
            "v2_contextual_border_touch_count": border_touch_v2,
            "v2_border_touch_pct": round(border_touch_v2 / max(evaluated_crops, 1) * 100, 1),
            "improved_crops_count": improved_crops,
            "border_clearance_reduction_factor": round((border_touch_v1 - border_touch_v2) / max(border_touch_v1, 1) * 100, 1),
        },
        "detailed_sample_records": {
            "eligibility_samples": eligibility_results[:15],
            "expansion_samples": expansion_results[:15],
        },
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print(f"\nEvaluation report written to: {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()

