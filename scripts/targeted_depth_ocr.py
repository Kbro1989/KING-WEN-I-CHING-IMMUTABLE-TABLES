"""Targeted high-zoom OCR for tall/wide symbols on PDF pages.

Detects tall narrow regions (stretched symbols: braces, delimiters) and
wide regions (multi-line expressions, fraction bars) in the original page
image, then crops those regions from the PDF at high zoom for better
Pix2Text recognition.
"""
import argparse
import cv2
import json
import os
import sys
import hashlib
import numpy as np
import pymupdf
from pathlib import Path

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
PDF_DIR = REPO_ROOT / "DATASETS" / "benchmark_pdfs"
OUT_DIR = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr"

SELECTED_PAGES = {
    "0806.2366": 3, "1212.0957": 8, "2009.00031": 5,
    "2102.03334": 6, "2605.00155": 27, "2605.00224": 1,
    "2605.06070": 12, "2605.18130": 4, "2605.22715": 19,
    "2605.23244": 4, "2605.24807": 9, "2605.24856": 17,
    "2605.25036": 3, "2605.25334": 6, "2605.28615": 15,
    "2605.28896": 16,
}


def detect_tall_regions(img, min_height_px=60, min_width_px=10, max_width_px=100):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    row_sums = np.sum(gray < 128, axis=1)
    lines = []
    in_line = False
    start = 0
    for i, s in enumerate(row_sums):
        if s > 0 and not in_line:
            in_line = True
            start = i
        elif s == 0 and in_line:
            in_line = False
            if i - start > 3:
                lines.append((start, i))
    if in_line and len(row_sums) - start > 3:
        lines.append((start, len(row_sums)))
    avg_lh = np.median([e - s for s, e in lines]) if lines else 20

    text_mask = (gray < 128).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = rh / max(rw, 1)

        if rh > 3 * avg_lh and min_width_px <= rw <= max_width_px and aspect > 2.5 and area > 100:
            regions.append({
                "bbox": (int(x), int(y), int(rw), int(rh)),
                "area": int(area),
                "aspect_ratio": round(aspect, 2),
                "height_lines": round(rh / avg_lh, 1),
                "centroid": (float(centroids[i][0]), float(centroids[i][1])),
                "type": "tall_narrow",
            })

    regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
    return regions, avg_lh


def detect_wide_regions(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape[:2]

    row_sums = np.sum(gray < 128, axis=1)
    lines = []
    in_line = False
    start = 0
    for i, s in enumerate(row_sums):
        if s > 0 and not in_line:
            in_line = True
            start = i
        elif s == 0 and in_line:
            in_line = False
            if i - start > 3:
                lines.append((start, i))
    if in_line and len(row_sums) - start > 3:
        lines.append((start, len(row_sums)))
    avg_lh = np.median([e - s for s, e in lines]) if lines else 20

    text_mask = (gray < 128).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    closed = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 500:
            continue
        if rw > 10 * avg_lh and rh > avg_lh:
            regions.append({
                "bbox": (int(x), int(y), int(rw), int(rh)),
                "area": int(area),
                "aspect_ratio": round(rw / rh, 1),
                "width_lines": round(rw / avg_lh, 1),
                "height_lines": round(rh / avg_lh, 1),
                "centroid": (float(centroids[i][0]), float(centroids[i][1])),
                "type": "wide",
            })

    regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
    return regions, avg_lh


def pdf_rect_from_bbox(bbox, img_shape, page_rect):
    x, y, rw, rh = bbox
    scale = 1.0 / 4.0
    x0 = max(0, x * scale - 20)
    y0 = max(0, y * scale - 20)
    x1 = min(page_rect.width, (x + rw) * scale + 20)
    y1 = min(page_rect.height, (y + rh) * scale + 20)
    return pymupdf.Rect(x0, y0, x1, y1)


def crop_and_ocr(paper_id, page_num, regions, high_zoom=8):
    pdf_path = PDF_DIR / f"{paper_id}.pdf"
    if not pdf_path.exists():
        print(f"  No PDF: {pdf_path}")
        return []

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_num - 1]
    page_rect = page.rect

    pix4 = page.get_pixmap(matrix=pymupdf.Matrix(4, 4))
    img4 = np.frombuffer(pix4.tobytes("png"), dtype=np.uint8)
    img4 = cv2.imdecode(img4, cv2.IMREAD_COLOR)

    results = []
    for idx, region in enumerate(regions):
        bbox = region["bbox"]
        pdf_rect = pdf_rect_from_bbox(bbox, img4.shape, page_rect)

        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(high_zoom, high_zoom),
            clip=pdf_rect,
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        img_bytes = pix.tobytes("png")
        img_array = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

        out_subdir = OUT_DIR / paper_id
        out_subdir.mkdir(parents=True, exist_ok=True)
        crop_name = f"{paper_id}_p{page_num}_{region.get('type','region')}_{idx:02d}_z{high_zoom}.png"
        crop_path = out_subdir / crop_name
        cv2.imwrite(str(crop_path), img_array)

        try:
            from pix2text import Pix2Text
            p2t = Pix2Text()
            rec_result = p2t.recognize_formula(str(crop_path))
            if isinstance(rec_result, str):
                rec_text = rec_result.strip()
            elif isinstance(rec_result, dict):
                rec_text = (rec_result.get("latex") or rec_result.get("text") or "").strip()
            else:
                rec_text = str(rec_result).strip() if rec_result else ""
        except Exception as e:
            rec_text = f"ERROR: {e}"

        results.append({
            "region_index": idx,
            "type": region.get("type", "unknown"),
            "bbox": bbox,
            "aspect_ratio": region.get("aspect_ratio", 0),
            "height_lines": region.get("height_lines", 0),
            "width_lines": region.get("width_lines", 0),
            "pdf_rect": [round(pdf_rect.x0, 2), round(pdf_rect.y0, 2), round(pdf_rect.x1, 2), round(pdf_rect.y1, 2)],
            "crop_size": [pix.width, pix.height],
            "crop_path": str(crop_path),
            "pix2text_result": rec_text,
        })
        print(f"  Region {idx} ({region.get('type','?')}): bbox={bbox}, crop={pix.width}x{pix.height}, OCR={rec_text[:80]}")

    doc.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Targeted high-zoom OCR for tall/wide symbols")
    parser.add_argument("--paper", type=str, help="Paper ID (e.g. 2009.00031)")
    parser.add_argument("--page", type=int, help="Page number (1-indexed)")
    parser.add_argument("--zoom", type=int, default=8, help="High zoom factor for crops")
    parser.add_argument("--min-height", type=int, default=60, help="Min tall region height in px at zoom=4")
    parser.add_argument("--all", action="store_true", help="Process all 16 benchmark pages")
    args = parser.parse_args()

    if args.all:
        targets = list(SELECTED_PAGES.items())
    elif args.paper and args.page:
        targets = [(args.paper, args.page)]
    else:
        print("Specify --paper ID --page N or --all")
        sys.exit(1)

    all_results = {}
    for paper_id, page_num in targets:
        print(f"\n=== {paper_id} p{page_num} ===")
        pdf_path = PDF_DIR / f"{paper_id}.pdf"
        if not pdf_path.exists():
            print(f"  No PDF")
            continue

        # Source PDF identity
        pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

        doc = pymupdf.open(str(pdf_path))
        page = doc[page_num - 1]
        pix4 = page.get_pixmap(matrix=pymupdf.Matrix(4, 4))
        img4 = np.frombuffer(pix4.tobytes("png"), dtype=np.uint8)
        img4 = cv2.imdecode(img4, cv2.IMREAD_COLOR)
        doc.close()

        # Save original 4x detection image for provenance
        det_subdir = OUT_DIR / paper_id
        det_subdir.mkdir(parents=True, exist_ok=True)
        det_img_path = det_subdir / f"{paper_id}_p{page_num}_detection_z4.png"
        cv2.imwrite(str(det_img_path), img4)

        tall_regions, avg_lh = detect_tall_regions(img4, min_height_px=args.min_height)
        wide_regions, _ = detect_wide_regions(img4)
        all_regions = tall_regions + wide_regions
        print(f"  Detected {len(tall_regions)} tall + {len(wide_regions)} wide regions (avg line height: {avg_lh:.0f}px)")

        # Region overlap detection
        overlap_pairs = []
        for i, r1 in enumerate(all_regions):
            for j, r2 in enumerate(all_regions):
                if j <= i:
                    continue
                b1 = r1["bbox"]
                b2 = r2["bbox"]
                # IoU
                x1 = max(b1[0], b2[0])
                y1 = max(b1[1], b2[1])
                x2 = min(b1[0]+b1[2], b2[0]+b2[2])
                y2 = min(b1[1]+b1[3], b2[1]+b2[3])
                inter = max(0, x2-x1) * max(0, y2-y1)
                area1 = b1[2]*b1[3]
                area2 = b2[2]*b2[3]
                union = area1 + area2 - inter
                iou = inter / union if union > 0 else 0
                if iou > 0.1:
                    overlap_pairs.append({
                        "region_a": i, "region_b": j,
                        "iou": round(iou, 3),
                        "intersection_px": inter,
                        "containment": round(inter / min(area1, area2), 3) if min(area1, area2) > 0 else 0,
                    })

        if not all_regions:
            print("  No regions found, skipping")
            continue

        results = crop_and_ocr(paper_id, page_num, all_regions, high_zoom=args.zoom)

        # Empty/nonempty tracking
        nonempty = [r for r in results if r["pix2text_result"].strip() and not r["pix2text_result"].startswith("ERROR")]
        empty = [r for r in results if not r["pix2text_result"].strip() or r["pix2text_result"].startswith("ERROR")]

        all_results[f"{paper_id}_p{page_num}"] = {
            "paper_id": paper_id,
            "page_num": page_num,
            "source_pdf_hash": pdf_hash,
            "detection_image": str(det_img_path),
            "detection_params": {
                "min_height_px": args.min_height,
                "zoom_detection": 4,
                "zoom_crop": args.zoom,
            },
            "avg_line_height_px": round(float(avg_lh), 1),
            "tall_region_count": len(tall_regions),
            "wide_region_count": len(wide_regions),
            "total_region_count": len(all_regions),
            "unique_region_count": len(all_regions) - len(overlap_pairs),
            "overlap_pairs": overlap_pairs,
            "ocr_model": "pix2text 1.1.7",
            "ocr_method": "recognize_formula",
            "nonempty_count": len(nonempty),
            "empty_count": len(empty),
            "empty_region_indices": [r["region_index"] for r in empty],
            "regions": results,
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "targeted_ocr_results.json"
    evidence_record = {
        "evidence_version": "1.0",
        "evidence_type": "targeted_ocr_pilot",
        "run_date": "2026-11-04",
        "ocr_model": "pix2text 1.1.7",
        "ocr_method": "recognize_formula",
        "detection_zoom": 4,
        "crop_zoom": args.zoom,
        "min_height_px": args.min_height,
        "page_population": "16 benchmark papers, selected formula pages",
        "results": all_results,
    }
    with open(out_path, "w") as f:
        json.dump(evidence_record, f, indent=2)
    print(f"\nResults saved: {out_path}")
    total = sum(v["tall_region_count"] + v["wide_region_count"] for v in all_results.values())
    print(f"Total regions processed: {total}")
    print(f"Nonempty: {sum(v['nonempty_count'] for v in all_results.values())}, Empty: {sum(v['empty_count'] for v in all_results.values())}")
    print(f"Overlap pairs: {sum(len(v['overlap_pairs']) for v in all_results.values())}")


if __name__ == "__main__":
    main()
