#!/usr/bin/env python3
"""
Step 3 — Blind Detection Run for 1505.05770 (Variational Inference with Normalizing Flows)

Runs targeted_math_detector.py detection pipeline on pages 2 and 3 (1-based)
of the positive-control PDF without supplying any gold coordinates.

Outputs:
    DATASETS/structural_preservation/1505.05770_blind_detection_p002.json
    DATASETS/structural_preservation/1505.05770_blind_detection_p003.json

Invariants:
    - Detector receives NO gold coordinates or equation identifiers.
    - OCR (Pix2Text) is excluded; geometry-only detection.
    - All file writes use encoding="utf-8".
    - Page numbering: 1-based in output, 0-based for fitz.open indexing.

Usage:
    python scripts/blind_detection_run_1505.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — import detector without package prefix
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import targeted_math_detector as tmd  # noqa: E402  (must come after sys.path insert)

# ---------------------------------------------------------------------------
# Constants — do NOT read the positive-control manifest; detector is blind
# ---------------------------------------------------------------------------
PDF_PATH = Path(
    "C:/Users/krist/Desktop/zotero/learning-corpus/"
    "efficient-inference-quantization/"
    "1505.05770_Variational Inference with Normalizing Flows.pdf"
)

# Pages to process (1-based, as displayed on the page)
TARGET_PAGES_1BASED = [2, 3]

ZOOM = 4.0

OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"
RENDER_OUT_DIR = REPO_ROOT / "DATASETS" / "structural_preservation" / "1505.05770_blind_renders"

DETECTOR_SCRIPT = SCRIPTS_DIR / "targeted_math_detector.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_blind_detection():
    # Verify inputs exist
    if not PDF_PATH.is_file():
        sys.exit(
            f"[ERROR] PDF not found: {PDF_PATH}\n"
            "Verify Zotero library path before proceeding."
        )
    if not DETECTOR_SCRIPT.is_file():
        sys.exit(f"[ERROR] Detector script not found: {DETECTOR_SCRIPT}")

    # Record detector hash BEFORE opening any gold data
    detector_hash = sha256_file(DETECTOR_SCRIPT)
    source_pdf_hash = sha256_file(PDF_PATH)

    print(f"[blind_detection] detector_script_sha256 = {detector_hash}", flush=True)
    print(f"[blind_detection] source_pdf_sha256       = {source_pdf_hash}", flush=True)

    # Verify the PDF hash matches the frozen manifest value
    EXPECTED_PDF_SHA256 = "776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a"
    if source_pdf_hash != EXPECTED_PDF_SHA256:
        sys.exit(
            f"[ERROR] PDF SHA-256 mismatch.\n"
            f"  expected: {EXPECTED_PDF_SHA256}\n"
            f"  actual:   {source_pdf_hash}\n"
            "Do not proceed with an unverified source file."
        )
    print("[blind_detection] PDF hash VERIFIED against frozen manifest value.", flush=True)

    try:
        import fitz
    except ImportError:
        import pymupdf as fitz

    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    print(f"[blind_detection] PDF opened: {total_pages} pages total.", flush=True)

    RENDER_OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    for page_1based in TARGET_PAGES_1BASED:
        page_0based = page_1based - 1
        page = doc[page_0based]
        page_size = [round(page.rect.width, 3), round(page.rect.height, 3)]

        print(
            f"\n[blind_detection] Processing page {page_1based} "
            f"(doc index {page_0based}), size={page_size} pts ...",
            flush=True,
        )

        # --- Character-stream detection (no gold coords used) ---
        spans, chars = tmd.extract_raw_observations(page, page_0based)
        geometry_cands = tmd.geometry_candidates(chars)
        script_cands = tmd.script_position_candidates(chars)

        # --- Visual / connected-component detection (no gold coords used) ---
        visual_result = tmd.render_visual_candidates(page, page_0based, ZOOM, RENDER_OUT_DIR)
        visual_cands = visual_result["visual_candidates"]

        print(
            f"  spans={len(spans)}, chars={len(chars)}, "
            f"geometry_candidates={len(geometry_cands)}, "
            f"script_candidates={len(script_cands)}, "
            f"visual_candidates={len(visual_cands)}",
            flush=True,
        )

        # Build output record
        output = {
            "schema_version": "1.0",
            "step": "step3_blind_detection",
            "document_id": "1505.05770",
            "source_pdf_sha256": source_pdf_hash,
            "source_pdf_path": str(PDF_PATH),
            "detector_script": "targeted_math_detector.py",
            "detector_script_sha256": detector_hash,
            "detector_version": "1.1",
            "gold_coordinates_supplied": False,
            "ocr_included": False,
            "ocr_exclusion_reason": "Pix2Text initialization hangs; excluded from geometry-only Step 3",
            "zoom": ZOOM,
            "page_number_1_based": page_1based,
            "page_index_0_based": page_0based,
            "page_size_pdf_pt": page_size,
            "coordinate_space": "mupdf_page_points",
            "detection_summary": {
                "math_like_text_span_count": len(spans),
                "character_observation_count": len(chars),
                "geometry_candidate_count": len(geometry_cands),
                "script_position_candidate_count": len(script_cands),
                "visual_candidate_count": len(visual_cands),
            },
            "math_like_text_spans": spans,
            "geometry_candidates": geometry_cands,
            "script_position_candidates": script_cands,
            "visual_component_analysis": {
                "render_size_px": visual_result["render_size_px"],
                "render_zoom": visual_result["render_zoom"],
                "otsu_threshold": visual_result["otsu_threshold"],
                "render_path": visual_result["render_path"],
                "threshold_path": visual_result["threshold_path"],
                "connected_component_count": visual_result["connected_component_count"],
                "visual_candidates": visual_cands,
            },
            "detector_limitations": [
                "PDF text extraction can omit or mis-map glyphs due to font encodings.",
                "Visual connected components are ink marks, not semantic symbols.",
                "Tall components are not automatically delimiters; wide components are not automatically fraction bars.",
                "Superscript/subscript labels are positional hypotheses, not validated attachments.",
                "No OCR, equation reconstruction, delimiter repair, or semantic validation performed.",
                "bbox_pdf_pt_approx in visual candidates is derived by dividing pixel coords by zoom; "
                "accuracy is limited by pixel quantization at zoom=4.",
            ],
        }

        out_path = OUT_ROOT / f"1505.05770_blind_detection_p{page_1based:03d}.json"
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved → {out_path}", flush=True)

    doc.close()
    print("\n[blind_detection] Step 3 complete.", flush=True)


if __name__ == "__main__":
    # Reconfigure stdout/stderr for Windows UTF-8 safety
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    run_blind_detection()

