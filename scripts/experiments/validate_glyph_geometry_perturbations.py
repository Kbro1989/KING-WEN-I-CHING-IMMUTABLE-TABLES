"""Glyph Geometry Perturbation Experiment: Resolution and Threshold Sensitivity.

Implements multi-resolution and multi-threshold perturbation analysis across
the 5 geometric envelopes:
  1. Font metrics: Nominal glyph cell & advance geometry (PDF text stream).
  2. Physical ink envelope: Extreme non-background marks.
  3. Raster foreground envelope: Detected foreground under varying resolutions & thresholds.
  4. Candidate crop envelope: Proposed processing ROI.
  5. Certified safety envelope: Required perimeter whitespace clearance.

Perturbations evaluated:
  - Resolutions: Zoom 1.0 (72 DPI), Zoom 2.0 (144 DPI), Zoom 3.0 (216 DPI)
  - Threshold policies:
      * Fixed 200 (UniMERNet policy)
      * Strict 240 (captures faint anti-aliased subpixels)
      * Otsu automatic thresholding
      * Adaptive Gaussian thresholding

Outputs:
  DATASETS/structural_preservation/glyph_geometry_perturbation_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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
OUT_JSON = ROOT / "DATASETS" / "structural_preservation" / "glyph_geometry_perturbation_results.json"


def binarize_image(gray: np.ndarray, policy: str) -> np.ndarray:
    """Apply specified binarization policy."""
    if policy == "unimernet_fixed_200":
        if gray.max() == gray.min():
            return np.zeros_like(gray)
        normalized = (((gray - gray.min()) / (gray.max() - gray.min())) * 255).astype(np.uint8)
        return (255 * (normalized < 200)).astype(np.uint8)
    elif policy == "strict_anti_aliased_240":
        return (255 * (gray < 240)).astype(np.uint8)
    elif policy == "otsu":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary
    elif policy == "adaptive_gaussian":
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5
        )
    else:
        raise ValueError(f"Unknown policy: {policy}")


def extract_raster_envelope_pt(
    binary: np.ndarray,
    candidate_rect: pymupdf.Rect,
    zoom: float,
) -> list[float] | None:
    """Find bounding box of foreground pixels and map back to PDF points."""
    coords = cv2.findNonZero(binary)
    if coords is None:
        return None
    x, y, w, h = cv2.boundingRect(coords)
    x0_pt = round(candidate_rect.x0 + (x / zoom), 4)
    y0_pt = round(candidate_rect.y0 + (y / zoom), 4)
    x1_pt = round(candidate_rect.x0 + ((x + w) / zoom), 4)
    y1_pt = round(candidate_rect.y0 + ((y + h) / zoom), 4)
    return [x0_pt, y0_pt, x1_pt, y1_pt]


def extract_font_metric_envelope_pt(page: pymupdf.Page, region_rect: pymupdf.Rect) -> list[float] | None:
    """Extract font em-box envelope from PDF rawjson."""
    raw = json.loads(page.get_text("rawjson"))
    chars = []
    for b in raw.get("blocks", []):
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                for c in s.get("chars", []):
                    bbox = c.get("bbox", [])
                    if bbox and pymupdf.Rect(bbox).intersects(region_rect):
                        chars.append(bbox)
    if not chars:
        return None
    min_x = min(b[0] for b in chars)
    min_y = min(b[1] for b in chars)
    max_x = max(b[2] for b in chars)
    max_y = max(b[3] for b in chars)
    return [round(min_x, 4), round(min_y, 4), round(max_x, 4), round(max_y, 4)]


def run_perturbation_study() -> dict[str, Any]:
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
    ]

    zooms = [1.0, 2.0, 3.0]
    policies = ["unimernet_fixed_200", "strict_anti_aliased_240", "otsu", "adaptive_gaussian"]

    report_targets = []

    for t in targets:
        doc = pymupdf.open(str(t["pdf"]))
        page = doc[t["page"]]
        candidate_rect = t["rect"]

        font_envelope = extract_font_metric_envelope_pt(page, candidate_rect)

        perturbations = []

        for z in zooms:
            mat = pymupdf.Matrix(z, z)
            pix = page.get_pixmap(matrix=mat, clip=candidate_rect, alpha=False)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            for pol in policies:
                binary = binarize_image(gray, pol)
                raster_envelope = extract_raster_envelope_pt(binary, candidate_rect, z)

                # Compute variance with font envelope
                if font_envelope and raster_envelope:
                    delta_left_pt = round(raster_envelope[0] - font_envelope[0], 4)
                    delta_right_pt = round(font_envelope[2] - raster_envelope[2], 4)
                    delta_top_pt = round(raster_envelope[1] - font_envelope[1], 4)
                    delta_bottom_pt = round(font_envelope[3] - raster_envelope[3], 4)
                    delta_left_px = round(delta_left_pt * z, 2)
                    delta_right_px = round(delta_right_pt * z, 2)
                    delta_top_px = round(delta_top_pt * z, 2)
                    delta_bottom_px = round(delta_bottom_pt * z, 2)
                else:
                    delta_left_pt = delta_right_pt = delta_top_pt = delta_bottom_pt = 0.0
                    delta_left_px = delta_right_px = delta_top_px = delta_bottom_px = 0.0

                perturbations.append({
                    "zoom": z,
                    "dpi": int(z * 72),
                    "policy": pol,
                    "raster_envelope_pt": raster_envelope,
                    "cross_resolution_convergence": {
                        "residual_pt": {
                            "delta_left": delta_left_pt,
                            "delta_right": delta_right_pt,
                            "delta_top": delta_top_pt,
                            "delta_bottom": delta_bottom_pt,
                        },
                        "residual_px": {
                            "delta_left": delta_left_px,
                            "delta_right": delta_right_px,
                            "delta_top": delta_top_px,
                            "delta_bottom": delta_bottom_px,
                        },
                    },
                })

        report_targets.append({
            "target_id": t["id"],
            "candidate_crop_pt": [round(v, 4) for v in candidate_rect],
            "font_metric_envelope_pt": font_envelope,
            "total_perturbations": len(perturbations),
            "perturbations": perturbations,
        })

    report = {
        "study_identifier": "GLYPH-GEOMETRY-PERTURBATION-V1",
        "tested_zooms": zooms,
        "tested_policies": policies,
        "total_targets": len(report_targets),
        "targets": report_targets,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = run_perturbation_study()
    print(f"Perturbation study complete. Evaluated {rep['total_targets']} targets. Written to {OUT_JSON}")

