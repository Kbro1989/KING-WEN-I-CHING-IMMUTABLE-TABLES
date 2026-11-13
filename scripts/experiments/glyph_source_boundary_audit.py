"""Glyph-Source Boundary Audit: Independent PDF Vector Geometry vs. UniMERNet Zero-Margin Cropping.

Validates whether UniMERNet's crop_margin_numpy zero-margin preprocessing
infringes on or safely encloses independently established source PDF vector glyph
bounding boxes across benchmark targets:
  - CP-001 (Cluster-GCN arXiv:1905.07953)
  - CP-002 (ViLT arXiv:2102.03334)
  - CP-003 (Linear Probing arXiv:2605.24856)
  - RAHMANI (arXiv:1212.0957 Page 8)

Compares:
  1. Source PDF vector glyph envelope [min_x, min_y, max_x, max_y]
  2. Input candidate crop bounding box
  3. Preprocessed zero-margin crop bounding box
  4. Outermost glyph-to-boundary clearances (left, right, top, bottom)
  5. Distinction between whitespace reduction vs true glyph truncation

Outputs:
  DATASETS/structural_preservation/glyph_source_boundary_audit_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# pyrefly: ignore[missing-import]
import cv2
# pyrefly: ignore[missing-import]
import numpy as np
# pyrefly: ignore[missing-import]
import pymupdf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
OUT_JSON = ROOT / "DATASETS" / "structural_preservation" / "glyph_source_boundary_audit_results.json"


def unimernet_crop_margin_numpy(img: np.ndarray) -> tuple[np.ndarray, dict]:
    """Exact implementation from unimernet/processors/formula_processor.py lines 36-56."""
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img.copy()

    orig_h, orig_w = gray.shape[:2]
    if gray.max() == gray.min():
        return img, {"x": 0, "y": 0, "w": orig_w, "h": orig_h, "empty": True}

    normalized = (((gray - gray.min()) / (gray.max() - gray.min())) * 255).astype(np.uint8)
    binary = 255 * (normalized < 200).astype(np.uint8)

    coords = cv2.findNonZero(binary)
    if coords is None:
        return img, {"x": 0, "y": 0, "w": orig_w, "h": orig_h, "empty": True}

    x, y, w, h = cv2.boundingRect(coords)
    cropped = img[y : y + h, x : x + w]

    meta = {
        "orig_w": orig_w,
        "orig_h": orig_h,
        "crop_x": int(x),
        "crop_y": int(y),
        "crop_w": int(w),
        "crop_h": int(h),
        "delta_left": int(x),
        "delta_top": int(y),
        "delta_right": int(orig_w - (x + w)),
        "delta_bottom": int(orig_h - (y + h)),
    }
    return cropped, meta


def extract_vector_glyphs_in_region(
    page: pymupdf.Page,
    region_rect: pymupdf.Rect,
) -> tuple[list[dict], list[float]]:
    """Extract individual character vector bounding boxes falling within region_rect."""
    raw = json.loads(page.get_text("rawjson"))
    chars = []
    for b in raw.get("blocks", []):
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                for c in s.get("chars", []):
                    bbox = c.get("bbox", [])
                    if not bbox or len(bbox) != 4:
                        continue
                    # Check overlap with region_rect
                    cb = pymupdf.Rect(bbox)
                    if cb.intersects(region_rect):
                        chars.append({
                            "c": c.get("c"),
                            "font": s.get("font"),
                            "size": s.get("size"),
                            "bbox_pt": [round(v, 4) for v in bbox],
                        })
    if not chars:
        return [], []

    min_x = min(c["bbox_pt"][0] for c in chars)
    min_y = min(c["bbox_pt"][1] for c in chars)
    max_x = max(c["bbox_pt"][2] for c in chars)
    max_y = max(c["bbox_pt"][3] for c in chars)
    envelope = [round(min_x, 4), round(min_y, 4), round(max_x, 4), round(max_y, 4)]
    return chars, envelope


def audit_target(
    doc: pymupdf.Document,
    page_idx: int,
    candidate_rect: pymupdf.Rect,
    target_id: str,
    zoom: float = 2.0,
) -> dict:
    page = doc[page_idx]
    chars, vector_envelope = extract_vector_glyphs_in_region(page, candidate_rect)

    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=candidate_rect, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))

    _, meta = unimernet_crop_margin_numpy(img)

    # Convert cropped image bounds back to PDF point coordinates
    crop_x0_pt = round(candidate_rect.x0 + (meta["crop_x"] / zoom), 4)
    crop_y0_pt = round(candidate_rect.y0 + (meta["crop_y"] / zoom), 4)
    crop_x1_pt = round(candidate_rect.x0 + ((meta["crop_x"] + meta["crop_w"]) / zoom), 4)
    crop_y1_pt = round(candidate_rect.y0 + ((meta["crop_y"] + meta["crop_h"]) / zoom), 4)
    zero_margin_bbox_pt = [crop_x0_pt, crop_y0_pt, crop_x1_pt, crop_y1_pt]

    # Clearances between vector envelope and zero-margin crop bounds
    # Positive clearance means vector glyph lies inside crop; negative means truncation.
    if vector_envelope:
        clearance_left_pt = round(vector_envelope[0] - crop_x0_pt, 4)
        clearance_right_pt = round(crop_x1_pt - vector_envelope[2], 4)
        clearance_top_pt = round(vector_envelope[1] - crop_y0_pt, 4)
        clearance_bottom_pt = round(crop_y1_pt - vector_envelope[3], 4)

        all_glyphs_inside = (
            clearance_left_pt >= -0.75
            and clearance_right_pt >= -0.75
            and clearance_top_pt >= -0.75
            and clearance_bottom_pt >= -0.75
        )
    else:
        clearance_left_pt = clearance_right_pt = clearance_top_pt = clearance_bottom_pt = 0.0
        all_glyphs_inside = True

    return {
        "target_id": target_id,
        "page_index": page_idx,
        "glyph_count": len(chars),
        "source_vector_envelope_pt": vector_envelope,
        "candidate_crop_pt": [round(v, 4) for v in candidate_rect],
        "unimernet_zero_margin_crop_pt": zero_margin_bbox_pt,
        "shaved_margins_px_at_2x": {
            "top": meta["delta_top"],
            "bottom": meta["delta_bottom"],
            "left": meta["delta_left"],
            "right": meta["delta_right"],
        },
        "clearances_to_vector_envelope_pt": {
            "left_pt": clearance_left_pt,
            "right_pt": clearance_right_pt,
            "top_pt": clearance_top_pt,
            "bottom_pt": clearance_bottom_pt,
        },
        "all_source_vector_glyphs_enclosed": all_glyphs_inside,
        "whitespace_reduction_analysis": {
            "is_pure_whitespace_reduction": bool(all_glyphs_inside and meta["delta_right"] > 0),
            "right_shaved_px": meta["delta_right"],
            "right_shaved_pt_equivalent": round(meta["delta_right"] / zoom, 4),
            "distance_from_rightmost_glyph_to_candidate_edge_pt": (
                round(candidate_rect.x1 - vector_envelope[2], 4) if vector_envelope else 0.0
            ),
        },
    }


def main():
    print("Executing Independent Glyph-Source Boundary Audit...")
    targets = [
        {
            "id": "CP-001-CLUSTER-GCN-BMATRIX",
            "pdf": ROOT / "DATASETS" / "benchmark_pdfs" / "1905.07953.pdf",
            "page": 3,
            "rect": pymupdf.Rect(116.15, 476.58, 230.61, 523.37),
        },
        {
            "id": "CP-002-VILT-NESTED-BRACKETS",
            "pdf": ROOT / "DATASETS" / "benchmark_pdfs" / "2102.03334.pdf",
            "page": 3,
            "rect": pymupdf.Rect(318.18, 532.30, 461.28, 548.82),
        },
        {
            "id": "CP-003-LINEAR-PROBING-NORM",
            "pdf": ROOT / "DATASETS" / "benchmark_pdfs" / "2605.24856.pdf",
            "page": 10,
            "rect": pymupdf.Rect(231.49, 151.11, 379.31, 193.97),
        },
        {
            "id": "RAHMANI-1212.0957-P8",
            "pdf": ROOT / "DATASETS" / "benchmark_pdfs" / "1212.0957.pdf",
            "page": 7,
            "rect": pymupdf.Rect(120.0, 310.0, 490.0, 470.0),
        },
    ]

    results = []
    for t in targets:
        if not t["pdf"].exists():
            print(f"Skipping {t['id']}: {t['pdf']} not found")
            continue
        doc = pymupdf.open(str(t["pdf"]))
        res = audit_target(doc, t["page"], t["rect"], t["id"])
        results.append(res)
        print(f"Target {t['id']}:")
        print(f"  Glyphs: {res['glyph_count']}")
        print(f"  Vector Envelope: {res['source_vector_envelope_pt']}")
        print(f"  Zero Margin BBox: {res['unimernet_zero_margin_crop_pt']}")
        print(f"  All Glyphs Enclosed: {res['all_source_vector_glyphs_enclosed']}")
        print(f"  Right Shaved px: {res['shaved_margins_px_at_2x']['right']} (Equivalent pt: {res['whitespace_reduction_analysis']['right_shaved_pt_equivalent']})")
        print(f"  Clearances (L, R, T, B) pt: {list(res['clearances_to_vector_envelope_pt'].values())}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {
                "audit_identifier": "GLYPH-SOURCE-BOUNDARY-AUDIT-V1",
                "total_targets": len(results),
                "all_enclosed_rate": sum(1 for r in results if r["all_source_vector_glyphs_enclosed"]) / len(results) if results else 0,
                "targets": results,
            },
            f,
            indent=2,
        )
    print(f"\nAudit complete. Written to {OUT_JSON}")


if __name__ == "__main__":
    main()

