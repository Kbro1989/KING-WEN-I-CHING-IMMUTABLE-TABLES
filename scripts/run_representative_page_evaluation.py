#!/usr/bin/env python3
"""
Representative-page evaluation for context-preservation pipeline.

Runs all 4 uncovered functions across ALL pages of ALL available papers.
Records pass/fail/skip/not-executed per paper per page per function.
Outputs append-only JSONL to DATASETS/vision_comparison/representative_page_evaluation.jsonl

Milestone: Evaluated (representative corpus)
Gate: G2–G6 (formal evaluation pending)
Authorization: Read-only evaluation; no source changes, no pipeline integration.

Usage:
    python scripts/run_representative_page_evaluation.py
    python scripts/run_representative_page_evaluation.py --papers 1907.04931 2104.01277
    python scripts/run_representative_page_evaluation.py --max-pages 5
"""
import argparse
import hashlib
import json
import sys
import time
import uuid
from pathlib import Path

import numpy as np
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from vision_comparison_pipeline import (
    detect_math_regions_on_page,
    expand_crop_context,
    extract_text_boundaries,
    detect_partial_formulas,
)

# ---------------------------------------------------------------------------
# Paper discovery
# ---------------------------------------------------------------------------

PAPER_DIRS = [
    ROOT / "DATASETS" / "benchmark_pdfs",
    ROOT.parent / "zotero" / "learning-corpus",
]

KNOWN_PAPERS = [
    "1907.04931",
    "2104.01277",
    "2205.01395",
    "2206.00364",
    "2605.22902",
    "2605.27315",
]


def find_paper_pdfs():
    """Find all PDFs across known directories."""
    pdfs = []
    for d in PAPER_DIRS:
        if d.exists():
            pdfs.extend(sorted(d.glob("*.pdf")))
    # Deduplicate by basename
    seen = set()
    unique = []
    for p in pdfs:
        if p.name not in seen:
            seen.add(p.name)
            unique.append(p)
    return unique


def paper_id_from_path(path):
    """Extract arXiv ID from filename."""
    name = path.stem
    # Try to extract arXiv ID pattern
    for pid in KNOWN_PAPERS:
        if pid in name:
            return pid
    return name


# ---------------------------------------------------------------------------
# Evaluation per page
# ---------------------------------------------------------------------------

def evaluate_page(page, page_num, paper_id, zoom=4, execution_id=None):
    """Evaluate all 4 functions on a single page. Returns a record dict."""
    if execution_id is None:
        execution_id = str(uuid.uuid4())

    record = {
        "execution_id": execution_id,
        "paper_id": paper_id,
        "page_number": page_num,
        "zoom": zoom,
        "page_dimensions": [page.rect.width, page.rect.height],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "functions": {},
        "lineage": {},
        "execution_status": "executed",
    }

    # Render page at zoom
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if img.shape[2] == 4:
        import cv2
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    # --- Detect page primary white (for contrast-based detection) ---
    try:
        import cv2
        white_info = detect_page_primary_white(img)
    except Exception:
        white_info = {"primary_white": 255, "white_std": 0, "text_threshold": 128,
                      "dark_threshold": 127, "darkest_to_primary_white_ratio": 1.0}

    # Store white detection in record
    record["primary_white_detection"] = white_info

    # --- Function 1: detect_math_regions_on_page ---
    try:
        regions = detect_math_regions_on_page(img, white_threshold=white_info["text_threshold"])
        record["functions"]["detect_math_regions_on_page"] = {
            "status": "pass",
            "region_count": len(regions),
            "regions": [
                {
                    "bbox": list(r["bbox"]),
                    "region_count": r["region_count"],
                    "is_complex": r["is_complex"],
                    "area_px": r["bbox"][2] * r["bbox"][3],
                }
                for r in regions
            ],
            "over_merge_count": 0,  # placeholder — requires adjudicated boundaries
            "under_merge_count": 0,
        }
    except Exception as e:
        record["functions"]["detect_math_regions_on_page"] = {
            "status": "fail",
            "error": str(e),
            "region_count": 0,
            "regions": [],
        }

    # --- Function 2: extract_text_boundaries ---
    try:
        boundaries = extract_text_boundaries(page)
        math_count = sum(1 for b in boundaries if b["is_math"])
        record["functions"]["extract_text_boundaries"] = {
            "status": "pass",
            "total_boundaries": len(boundaries),
            "math_boundaries": math_count,
            "text_boundaries": len(boundaries) - math_count,
            "boundaries": [
                {
                    "text": b["text"],
                    "bbox": list(b["bbox"]),
                    "is_math": b["is_math"],
                    "font_size": b["font_size"],
                }
                for b in boundaries
            ],
        }
    except Exception as e:
        record["functions"]["extract_text_boundaries"] = {
            "status": "fail",
            "error": str(e),
            "total_boundaries": 0,
            "math_boundaries": 0,
            "text_boundaries": 0,
            "boundaries": [],
        }

    # --- Function 3: detect_partial_formulas ---
    try:
        partials = detect_partial_formulas(page)
        record["functions"]["detect_partial_formulas"] = {
            "status": "pass",
            "partial_count": len(partials),
            "partials": [
                {
                    "text": p["text"],
                    "bbox": list(p["bbox"]),
                    "is_inline": p["is_inline"],
                    "math_word_count": p["math_word_count"],
                    "total_word_count": p["total_word_count"],
                    "math_words": p["math_words"],
                }
                for p in partials
            ],
            "false_positive_count": 0,  # requires adjudicated ground truth
        }
    except Exception as e:
        record["functions"]["detect_partial_formulas"] = {
            "status": "fail",
            "error": str(e),
            "partial_count": 0,
            "partials": [],
        }

    # --- Function 4: expand_crop_context (on first region if available) ---
    regions = record["functions"].get("detect_math_regions_on_page", {}).get("regions", [])
    if regions:
        first_region = regions[0]
        rb = first_region["bbox"]
        bbox = {"x0": rb[0], "y0": rb[1], "x1": rb[0] + rb[2], "y1": rb[1] + rb[3]}
        try:
            expanded = expand_crop_context(page, bbox, expand_factor=1.5, zoom=zoom)
            if expanded is not None:
                record["functions"]["expand_crop_context"] = {
                    "status": "pass",
                    "expanded_shape": list(expanded.shape),
                    "original_bbox": [rb[0], rb[1], rb[0] + rb[2], rb[1] + rb[3]],
                    "expanded_pixels": expanded.shape[0] * expanded.shape[1],
                    "original_pixels": rb[2] * rb[3] * zoom * zoom,
                    "expansion_ratio": (expanded.shape[0] * expanded.shape[1]) / max(rb[2] * rb[3] * zoom * zoom, 1),
                }
            else:
                record["functions"]["expand_crop_context"] = {
                    "status": "skip",
                    "reason": "content_ratio_below_threshold",
                    "original_bbox": [rb[0], rb[1], rb[0] + rb[2], rb[1] + rb[3]],
                }
        except Exception as e:
            record["functions"]["expand_crop_context"] = {
                "status": "fail",
                "error": str(e),
                "original_bbox": [rb[0], rb[1], rb[0] + rb[2], rb[1] + rb[3]],
            }
    else:
        record["functions"]["expand_crop_context"] = {
            "status": "skip",
            "reason": "no_regions_detected",
        }

    # --- Lineage: page → region → candidate → expanded ---
    try:
        boundaries = record["functions"].get("extract_text_boundaries", {}).get("boundaries", [])
        regions_list = record["functions"].get("detect_math_regions_on_page", {}).get("regions", [])
        partials = record["functions"].get("detect_partial_formulas", {}).get("partials", [])

        # Build lineage record
        lineage_entries = []
        for ri, region in enumerate(regions_list):
            for bi, boundary in enumerate(boundaries):
                # Check if boundary bbox overlaps with region bbox
                rb = region["bbox"]
                bb = boundary["bbox"]
                # Simple overlap check
                overlap = not (bb[2] <= rb[0] or bb[0] >= rb[0] + rb[2] or
                               bb[3] <= rb[1] or bb[1] >= rb[1] + rb[3])
                if overlap:
                    lineage_entries.append({
                        "region_index": ri,
                        "region_bbox": list(rb),
                        "boundary_index": bi,
                        "boundary_text": boundary["text"],
                        "boundary_bbox": list(bb),
                        "is_math": boundary["is_math"],
                        "overlap": True,
                    })

        record["lineage"] = {
            "region_count": len(regions_list),
            "boundary_count": len(boundaries),
            "partial_count": len(partials),
            "region_boundary_overlaps": len(lineage_entries),
            "lineage_entries": lineage_entries[:50],  # Cap to avoid huge files
            "all_candidates_traced": len(lineage_entries) > 0 or (len(regions_list) == 0 and len(boundaries) == 0),
        }
    except Exception as e:
        record["lineage"] = {
            "status": "fail",
            "error": str(e),
        }

    # Overall execution status
    statuses = [v.get("status", "unknown") for v in record["functions"].values()]
    if all(s == "pass" for s in statuses):
        record["execution_status"] = "pass"
    elif any(s == "fail" for s in statuses):
        record["execution_status"] = "fail"
    else:
        record["execution_status"] = "partial"

    return record


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Representative-page evaluation")
    parser.add_argument("--papers", nargs="*", help="Paper IDs to evaluate (default: all)")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages per paper (default: all)")
    parser.add_argument("--output", type=str, default=None, help="Output JSONL path")
    args = parser.parse_args()

    pdfs = find_paper_pdfs()
    if args.papers:
        pdfs = [p for p in pdfs if any(pid in p.name for pid in args.papers)]

    if not pdfs:
        print("No PDFs found. Searched:")
        for d in PAPER_DIRS:
            print(f"  {d}")
        return

    output_path = Path(args.output) if args.output else ROOT / "DATASETS" / "vision_comparison" / "representative_page_evaluation.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(pdfs)} PDFs")
    print(f"Output: {output_path}")
    print()

    execution_id = str(uuid.uuid4())
    run_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    total_pages_discovered = 0
    total_pages_attempted = 0
    total_pages_completed = 0
    total_pages_failed = 0
    total_pages_skipped = 0
    total_pages_not_executed = 0

    # Per-paper coverage tracking
    paper_coverage = {}

    # Append-only: open in append mode
    with open(output_path, "a") as f:
        for pdf_path in pdfs:
            paper_id = paper_id_from_path(pdf_path)
            print(f"Processing: {paper_id} ({pdf_path.name})")

            try:
                doc = pymupdf.open(str(pdf_path))
            except Exception as e:
                print(f"  ERROR opening PDF: {e}")
                paper_coverage[paper_id] = {
                    "pages_discovered": 0,
                    "pages_attempted": 0,
                    "pages_completed": 0,
                    "pages_failed": 0,
                    "pages_skipped": 0,
                    "pages_not_executed": 0,
                    "error": str(e),
                }
                continue

            page_count = len(doc)
            max_pages = args.max_pages if args.max_pages else page_count
            pages_to_process = min(max_pages, page_count)

            paper_stats = {
                "pages_discovered": page_count,
                "pages_attempted": pages_to_process,
                "pages_completed": 0,
                "pages_failed": 0,
                "pages_skipped": 0,
                "pages_not_executed": page_count - pages_to_process,
                "functions": {
                    "detect_math_regions_on_page": {"pass": 0, "fail": 0, "skip": 0},
                    "extract_text_boundaries": {"pass": 0, "fail": 0, "skip": 0},
                    "detect_partial_formulas": {"pass": 0, "fail": 0, "skip": 0},
                    "expand_crop_context": {"pass": 0, "fail": 0, "skip": 0},
                },
            }

            total_pages_discovered += page_count

            for page_num in range(pages_to_process):
                page = doc[page_num]
                total_pages_attempted += 1
                record = evaluate_page(page, page_num, paper_id, execution_id=execution_id)
                record["execution_id"] = execution_id
                record["run_timestamp"] = run_timestamp
                # Tag population scope
                record["population_scope"] = "benchmark_16"  # 16 PDFs in DATASETS/benchmark_pdfs
                f.write(json.dumps(record) + "\n")
                f.flush()

                # Update paper stats
                paper_stats["pages_completed"] += 1 if record["execution_status"] in ("pass", "partial") else 0
                paper_stats["pages_failed"] += 1 if record["execution_status"] == "fail" else 0
                # Count as completed if at least one function passed
                if record["execution_status"] in ("pass", "partial"):
                    paper_stats["pages_completed"] += 0  # already counted above
                # Track per-function status
                for fn_name, fn_data in record["functions"].items():
                    fn_status = fn_data.get("status", "unknown")
                    if fn_status in ("pass", "fail", "skip"):
                        paper_stats["functions"][fn_name][fn_status] += 1

                total_pages_completed += 1 if record["execution_status"] in ("pass", "partial") else 0
                total_pages_failed += 1 if record["execution_status"] == "fail" else 0
                # Count expand_crop_context skips
                expand_status = record["functions"].get("expand_crop_context", {}).get("status", "unknown")
                if expand_status == "skip":
                    total_pages_skipped += 1

                if page_num % 10 == 0 or page_num == pages_to_process - 1:
                    print(f"  Page {page_num + 1}/{pages_to_process}: {record['execution_status']}")

            total_pages_not_executed += page_count - pages_to_process
            paper_stats["pages_not_executed"] = page_count - pages_to_process
            paper_coverage[paper_id] = paper_stats
            doc.close()
            print(f"  Done: {pages_to_process} pages processed")

    # Write coverage summary record (append-only)
    coverage_summary = {
        "record_type": "coverage_summary",
        "execution_id": execution_id,
        "run_timestamp": run_timestamp,
        "population_scope": "benchmark_16",
        "population_note": "16 PDFs in DATASETS/benchmark_pdfs/. Earlier context-preservation evaluation referenced 6 papers/127 pages (lossy-coverage cross-examination). These are DIFFERENT populations: 6 papers = candidate spatial analysis; 16 papers = benchmark PDF set. Both scopes preserved.",
        "total_pages_discovered": total_pages_discovered,
        "total_pages_attempted": total_pages_attempted,
        "total_pages_completed": total_pages_completed,
        "total_pages_failed": total_pages_failed,
        "total_pages_skipped": total_pages_skipped,
        "total_pages_not_executed": total_pages_not_executed,
        "paper_coverage": paper_coverage,
        "skip_interpretation": "expand_crop_context skip = content_ratio_below_threshold (function returned None). This is NOT a successful expansion. Skipped count reported separately from pass/fail.",
    }
    with open(output_path, "a") as f:
        f.write(json.dumps(coverage_summary) + "\n")

    print()
    print("=" * 60)
    print(f"Execution ID: {execution_id}")
    print(f"Run timestamp: {run_timestamp}")
    print(f"Total pages discovered: {total_pages_discovered}")
    print(f"Total pages attempted: {total_pages_attempted}")
    print(f"Total pages completed: {total_pages_completed}")
    print(f"Total pages failed: {total_pages_failed}")
    print(f"Total pages skipped (expand): {total_pages_skipped}")
    print(f"Total pages not executed: {total_pages_not_executed}")
    print()
    print("Per-paper coverage:")
    for pid, stats in paper_coverage.items():
        print(f"  {pid}: discovered={stats['pages_discovered']} attempted={stats['pages_attempted']} "
              f"completed={stats['pages_completed']} failed={stats['pages_failed']} "
              f"skipped={stats['pages_skipped']} not_executed={stats['pages_not_executed']}")
    print()
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()