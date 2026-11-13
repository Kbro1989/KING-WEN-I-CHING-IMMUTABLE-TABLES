#!/usr/bin/env python3
"""Freeze Producer-Integrity Baseline Manifest.

Captures the frozen state of all 79 visual artifacts:
  - 48 PNGs from DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/
  - 31 PNGs from DATASETS/cross_reference/visual_recovery/
  - Producer script hashes and exact execution metrics
  - Formalizes Gates P1-P6 criteria and baseline error signatures
"""

import sys
import hashlib
import json
from pathlib import Path
import cv2

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
TARGETED_DIR = REPO_ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS" / "targeted_ocr"
VISUAL_REC_DIR = REPO_ROOT / "DATASETS" / "cross_reference" / "visual_recovery"
MANIFEST_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "producer_integrity_baseline_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def inspect_image(path: Path) -> dict:
    img = cv2.imread(str(path))
    if img is None:
        return {"error": "Failed to read image"}
    h, w, c = img.shape
    return {
        "width": w,
        "height": h,
        "channels": c,
        "aspect_ratio": round(w / max(h, 1), 3),
    }


def main():
    print("Freezing Producer-Integrity Baseline...")
    
    # 1. Producer Script Hashes
    producers = {
        "targeted_depth_ocr.py": {
            "path": "scripts/targeted_depth_ocr.py",
            "sha256": sha256_file(REPO_ROOT / "scripts" / "targeted_depth_ocr.py"),
            "role": "Candidate extraction and formula recognition (Producer 1)",
            "status": "FROZEN_BASELINE_V1",
        },
        "cross_reference_pipeline.py": {
            "path": "scripts/cross_reference_pipeline.py",
            "sha256": sha256_file(REPO_ROOT / "scripts" / "cross_reference_pipeline.py"),
            "role": "Visual evidence and spatial diagnostics (Producer 2)",
            "status": "DIAGNOSTIC_INFRASTRUCTURE",
        },
    }

    # 2. Targeted OCR Artifacts
    targeted_files = sorted(TARGETED_DIR.rglob("*.png"))
    targeted_artifacts = []
    for p in targeted_files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        info = inspect_image(p)
        targeted_artifacts.append({
            "path": rel,
            "filename": p.name,
            "category": "detection_page" if "_detection_z4.png" in p.name else "high_zoom_crop",
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "dimensions": info,
        })

    # 3. Visual Recovery Artifacts
    visual_files = sorted(VISUAL_REC_DIR.glob("*.png"))
    visual_artifacts = []
    for p in visual_files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        info = inspect_image(p)
        visual_artifacts.append({
            "path": rel,
            "filename": p.name,
            "category": "annotated_page_overlay",
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "dimensions": info,
        })

    total_pngs = len(targeted_artifacts) + len(visual_artifacts)
    print(f"  Targeted OCR PNGs: {len(targeted_artifacts)}")
    print(f"  Visual Recovery PNGs: {len(visual_artifacts)}")
    print(f"  Total Frozen PNGs: {total_pngs}")

    # 4. Manifest Assembly
    manifest = {
        "manifest_version": "1.0",
        "manifest_title": "Frozen Producer-Integrity Adversarial Baseline Manifest",
        "freeze_timestamp": "2026-11-05T21:58:00Z",
        "producer_scripts": producers,
        "producer_integrity_gates": {
            "P1_Provenance": {
                "requirement": "Identify original PDF and producer script",
                "failure_condition": "Untraceable visual artifact",
            },
            "P2_SemanticEligibility": {
                "requirement": "Establish mathematical candidate status via independent glyph/text analysis before OCR",
                "failure_condition": "Graphics/plots accepted as equations",
            },
            "P3_SpatialCompleteness": {
                "requirement": "Contextual crop expansion preserving delimiters, matrices, and scripts without border clipping",
                "failure_condition": "Clipped mathematical structure",
            },
            "P4_RecognitionFidelity": {
                "requirement": "Evaluate reconstructed expression against independent ground truth",
                "failure_condition": "Incorrect or incomplete LaTeX",
            },
            "P5_RejectionIntegrity": {
                "requirement": "Preserve rejected candidates, reasons, bounding boxes, and OCR attempt status in audit log",
                "failure_condition": "Silent candidate loss",
            },
            "P6_IndependentAudit": {
                "requirement": "Reconcile crop boundaries and visual elements against source PDF coordinate space",
                "failure_condition": "Unverified visual fidelity",
            },
        },
        "baseline_metrics": {
            "total_visual_artifacts": total_pngs,
            "targeted_ocr_pngs": len(targeted_artifacts),
            "visual_recovery_pngs": len(visual_artifacts),
            "high_zoom_crops": 32,
            "border_contact_baseline": {
                "contact_count": 29,
                "total": 32,
                "percentage": 90.6,
            },
            "empty_ocr_baseline": {
                "empty_count": 0,
                "total": 32,
                "percentage": 0.0,
            },
            "negative_control_hallucination_baseline": {
                "paper_id": "2009.00031",
                "page": 5,
                "detected_regions": 15,
                "hallucinated_formulas": 15,
                "hallucination_rate_pct": 100.0,
            },
            "rejection_evidence_logging": {
                "status": "ABSENT_IN_V1",
                "logged_rejections": 0,
            },
        },
        "artifacts": {
            "targeted_ocr": targeted_artifacts,
            "visual_recovery": visual_artifacts,
        },
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest successfully frozen to: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

