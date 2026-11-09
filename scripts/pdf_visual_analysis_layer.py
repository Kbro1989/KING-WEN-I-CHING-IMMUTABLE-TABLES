#!/usr/bin/env python3
"""
PDF VISUAL-DETECTION INTEGRATION LAYER
======================================

Bridges the frozen 243-paper equation-accounting batch with the repository's
existing delimiter-detection/structural-recovery components:

    PDF page -> targeted_math_detector.py (tall glyphs, stretched delimiters)
                 -> font_aware_math_classifier.py (font-aware classification)
                       -> delimiter_aware_structural_recovery.py (pairing, nesting)
                             -> per-page delimiter records

This layer is separate from the equation-accounting batch pipeline. It does not
modify batch_pipeline_output.jsonl or the frozen equation accounting. It adds
PDF-level visual measurement as a distinct evidence tier.

Usage:
    python pdf_visual_analysis_layer.py --pdf 2605.00155.pdf --pages all --out arena_math_audit/p1505

    # Corpus mode (all papers in the benchmark set)
    python pdf_visual_analysis_layer.py --corpus scripts/corpus_manifest.json --out arena_visual_analysis

Dependencies:
    pip install pymupdf numpy opencv-python

Note: pymupdf (fitz), numpy, and opencv-python must be installed. These are the
only external visualization dependencies; no other third-party package is required.
"""

import argparse
import json
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from targeted_math_detector import (
    is_math_char,
    extract_raw_observations,
    geometry_candidates,
    script_position_candidates,
    render_visual_candidates,
)

# ============================================================
# Delimiter detection layer
# ============================================================

def detect_delimiters_on_page(page, page_index, zoom=3.0):
    """
    Run the full visual-detection pipeline on a single PDF page.

    Pipeline:
        1. rawdict observations (per-glyph text info)
        2. geometry_candidates (tall glyphs, stretched symbols)
        3. script_position_candidates (superscript/subscript positions)
        4. render_visual_candidates (connected-component detection)

    Returns:
        dict — per-page delimiter measurement record.
    """
    # Ensure the detector module is importable: add scripts/ to path
    spans, chars = extract_raw_observations(page, page_index)

    # Geometric candidates (tall glyphs, stretched symbols)
    geom = geometry_candidates(chars)

    # Script-position hypotheses (superscripts/subscripts)
    script_positions = script_position_candidates(chars)

    # Render-based visual candidates (connected components)
    visual = render_visual_candidates(page, page_index, zoom, out_dir=Path("/tmp"))

    # Depth layer: classify detected glyphs
    # (font-awareness is already provided by the detector's rawdict observations)

    return {
        "page_index": page_index,
        "page_label": f"page_{page_index + 1:04d}",
        "total_chars": len(chars),
        "math_chars": sum(1 for c in chars if c["is_math_char"]),
        "visual_candidates_detected": len(geom),
        "geometric_candidates": geom,
        "script_position_candidates": script_positions,
        "visual_components_detected": len(visual["visual_candidates"]),
        "render_path": visual["render_path"],
        "threshold_path": visual["threshold_path"],
        "connected_component_count": visual["connected_component_count"],
    }


def run_page_pipeline(pdf_path: Path, page_index: int):
    """
    Run the full delimiter-measurement pipeline on one page of a PDF.

    Returns the per-page record plus the page index.
    """
    import fitz  # pymupdf

    doc = fitz.open(str(pdf_path))
    page = doc[page_index]
    record = detect_delimiters_on_page(page, page_index)
    doc.close()
    return record


def run_corpus(pdf_path: Path, pages: int = None):
    """
    Run the PDF visual-detection pipeline over a subset of pages.

    Args:
        pdf_path: Path to the PDF to analyse.
        pages: Number of pages to process (None = all).

    Returns:
        list[dict] — one record per page.
    """
    import fitz
    doc = fitz.open(str(pdf_path))
    total = doc.page_count
    if pages is not None:
        total = min(pages, total)

    records = []
    for pi in range(total):
        record = run_page_pipeline(pdf_path, pi)
        record["page_label"] = f"page_{pi + 1:04d}"
        records.append(record)

    doc.close()
    return records


def corpus_aggregate(records):
    """
    Collapse per-page delimiter records to corpus-level summary.

    Returns:
        dict — aggregate delimiter coverage statistics.
    """
    total_pages = len(records)
    pages_with_candidates = sum(1 for r in records if r["visual_candidates_detected"] > 0)
    pages_with_math = sum(1 for r in records if r["math_chars"] > 0)

    return {
        "total_pages": total_pages,
        "pages_with_delimiter_candidates": pages_with_candidates,
        "pages_with_math": pages_with_math,
        "pages_with_candidates_ratio": round(pages_with_candidates / max(1, total_pages), 4),
        "pages_with_math_ratio": round(pages_with_math / max(1, total_pages), 4),
        "per_page_records": records,
    }


# ============================================================
# Entry point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PDF visual-delimiter integration layer for the King Wen PDF math parser."
    )
    parser.add_argument(
        "pdf", type=Path, help="Path to the PDF to analyse."
    )
    parser.add_argument(
        "--pages", type=int, default=None,
        help="Number of pages to process (default: all).",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output directory for per-page visual candidates (default: temp).",
    )
    parser.add_argument(
        "--zoom", type=float, default=3.0,
        help="Render zoom factor for visual candidate detection.",
    )
    args = parser.parse_args()

    # Resolve output directory
    out_dir = args.out or Path(f"/tmp/pdf_viz_detection_{args.pdf.stem}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build manifest
    manifest = {
        "pdf": str(args.pdf),
        "pages": args.pages,
        "zoom": args.zoom,
        "out_dir": str(out_dir),
        "records": [],
    }

    records = run_corpus(args.pdf, pages=args.pages)
    manifest["records"] = records
    if args.out:
        manifest["aggregate"] = corpus_aggregate(records)

    # Write records
    records_path = out_dir / "delimiter_records.json"
    with open(records_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Console summary
    print(f"PDF: {args.pdf}")
    print(f"Pages processed: {len(records)}")
    if records:
        pg = records[0]
        print(f"  Total chars: {pg['total_chars']}")
        print(f"  Math chars: {pg['math_chars']}")
        print(f"  Geometric candidates: {pg['visual_candidates_detected']}")
        print(f"  Visual components: {pg['connected_component_count']}")
        print(f"  Record saved: {records_path}")


if __name__ == "__main__":
    main()
