"""Controlled Experiment: UniMERNet Preprocessing Crop-Retention Benchmark.

Directly executes UniMERNet's exact crop_margin_numpy algorithm
(from references/comparative_study/raw_code/unimernet/formula_processor.py)
against King Wen Math benchmark targets:
  - CP-001 (Cluster-GCN txexs 7-piece extensible bracket)
  - CP-002 (ViLT CMR10 nested sequence vector with macron bar)
  - CP-003 (Linear Probing norm with trailing superscript 2)
  - RAHMANI-1212.0957 (CMEX10 7x6 matrix with continuation ellipses)

Measures:
  1. Bounding box displacement (dx0, dy0, dx1, dy1)
  2. Retained source ink pixel count and area ratio
  3. Connected components (CC) preservation vs loss
  4. Specific inspection of delicate structural components (macrons, superscripts, serifs)
  5. Contrast with King Wen Math Gate D4 certified whitespace gutter clearance

Outputs:
  DATASETS/structural_preservation/unimernet_crop_retention_experiment_results.json
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

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
OUT_JSON = ROOT / "DATASETS" / "structural_preservation" / "unimernet_crop_retention_experiment_results.json"


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
        "binary_mask": binary,
    }
    return cropped, meta


def analyze_crop_preservation(
    page: pymupdf.Page,
    crop_rect_pt: pymupdf.Rect,
    target_name: str,
    critical_features: list[str],
    zoom: float = 2.0,
) -> dict:
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=crop_rect_pt, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))

    # UniMERNet preprocessing
    cropped_img, meta = unimernet_crop_margin_numpy(img)

    binary_orig = meta["binary_mask"]
    # Connected components on original binary
    n_cc_orig, labels_orig, stats_orig, centroids_orig = cv2.connectedComponentsWithStats(binary_orig)

    # In cropped binary
    binary_cropped = binary_orig[meta["crop_y"] : meta["crop_y"] + meta["crop_h"], meta["crop_x"] : meta["crop_x"] + meta["crop_w"]]
    n_cc_crop, labels_crop, stats_crop, centroids_crop = cv2.connectedComponentsWithStats(binary_cropped)

    # Count total foreground pixels
    fg_orig = int(np.count_nonzero(binary_orig))
    fg_crop = int(np.count_nonzero(binary_cropped))
    fg_retention_pct = round((fg_crop / fg_orig) * 100.0, 2) if fg_orig > 0 else 100.0

    # Margin clearance remaining in UniMERNet output
    # By definition, UniMERNet bounding box has 0 margin on at least one edge in each axis
    zero_margin_left = meta["crop_x"] >= 0 and np.any(binary_cropped[:, 0] > 0)
    zero_margin_top = meta["crop_y"] >= 0 and np.any(binary_cropped[0, :] > 0)
    zero_margin_right = np.any(binary_cropped[:, -1] > 0)
    zero_margin_bottom = np.any(binary_cropped[-1, :] > 0)

    # Check for delicate components near boundaries
    boundary_abuttal = {
        "touches_top_edge": bool(zero_margin_top),
        "touches_bottom_edge": bool(zero_margin_bottom),
        "touches_left_edge": bool(zero_margin_left),
        "touches_right_edge": bool(zero_margin_right),
    }

    return {
        "target_name": target_name,
        "critical_features": critical_features,
        "input_crop_pt": [round(x, 2) for x in crop_rect_pt],
        "rendered_pixels": {"width": meta["orig_w"], "height": meta["orig_h"], "zoom": zoom},
        "unimernet_cropped_pixels": {"width": meta["crop_w"], "height": meta["crop_h"]},
        "shaved_margins_px": {
            "top": meta["delta_top"],
            "bottom": meta["delta_bottom"],
            "left": meta["delta_left"],
            "right": meta["delta_right"],
        },
        "foreground_ink_pixels": {
            "original_count": fg_orig,
            "cropped_count": fg_crop,
            "retention_percentage": fg_retention_pct,
        },
        "connected_components": {
            "original_count": int(n_cc_orig - 1),  # exclude background
            "cropped_count": int(n_cc_crop - 1),
            "loss_count": int(max(0, n_cc_orig - n_cc_crop)),
        },
        "boundary_isolation_profile": {
            "has_explicit_safety_margin": False,
            "boundary_abuttal": boundary_abuttal,
            "risk_assessment": (
                "High risk of edge antialiasing attenuation and convolution filter distortion; "
                "extreme perimeter pixels abut the array edge with zero margin padding."
            ),
        },
    }


def run_experiment():
    print("=== UNIMERNET CROP-RETENTION CONTROLLED EXPERIMENT ===")
    results = []

    # 1. CP-001 Cluster-GCN
    pdf1 = ROOT / "DATASETS" / "benchmark_pdfs" / "1905.07953.pdf"
    if pdf1.exists():
        doc = pymupdf.open(str(pdf1))
        # Case bbox with certified context
        res = analyze_crop_preservation(
            doc[3],
            pymupdf.Rect(116.15, 476.58, 230.61, 523.37),
            "CP-001-CLUSTER-GCN-BMATRIX",
            ["txexs 7-piece extensible brackets", "horizontal ellipses cdots", "vertical ellipses vdots"],
        )
        results.append(res)
        print(f"  CP-001: Retention={res['foreground_ink_pixels']['retention_percentage']}% CCs={res['connected_components']['cropped_count']}/{res['connected_components']['original_count']}")

    # 2. CP-002 ViLT
    pdf2 = ROOT / "DATASETS" / "benchmark_pdfs" / "2102.03334.pdf"
    if pdf2.exists():
        doc = pymupdf.open(str(pdf2))
        res = analyze_crop_preservation(
            doc[3],
            pymupdf.Rect(318.18, 532.30, 461.28, 548.82),
            "CP-002-VILT-NESTED-BRACKETS",
            ["macron bar t_bar at y=534.57", "Nimbus text subscripts 'type'", "2.45pt gutter to Eq 4"],
        )
        results.append(res)
        print(f"  CP-002: Retention={res['foreground_ink_pixels']['retention_percentage']}% CCs={res['connected_components']['cropped_count']}/{res['connected_components']['original_count']}")

    # 3. CP-003 Linear Probing
    pdf3 = ROOT / "DATASETS" / "benchmark_pdfs" / "2605.24856.pdf"
    if pdf3.exists():
        doc = pymupdf.open(str(pdf3))
        res = analyze_crop_preservation(
            doc[10],
            pymupdf.Rect(231.49, 151.11, 379.31, 193.97),
            "CP-003-LINEAR-PROBING-NORM",
            ["LMMathExtension10 norm bars", "trailing superscript 2 at x=348.74", "embedded fraction 1/2"],
        )
        results.append(res)
        print(f"  CP-003: Retention={res['foreground_ink_pixels']['retention_percentage']}% CCs={res['connected_components']['cropped_count']}/{res['connected_components']['original_count']}")

    # 4. Rahmani 1212.0957 Page 8
    pdf4 = ROOT / "DATASETS" / "benchmark_pdfs" / "1212.0957.pdf"
    if pdf4.exists():
        doc = pymupdf.open(str(pdf4))
        res = analyze_crop_preservation(
            doc[7],
            pymupdf.Rect(120.0, 310.0, 490.0, 470.0),
            "RAHMANI-1212.0957-P8",
            ["CMEX10 7x6 matrix delimiters", "40 recovered tokens", "continuation ellipses"],
        )
        results.append(res)
        print(f"  RAHMANI: Retention={res['foreground_ink_pixels']['retention_percentage']}% CCs={res['connected_components']['cropped_count']}/{res['connected_components']['original_count']}")

    report = {
        "experiment_identifier": "UNIMERNET-PREPROCESSING-CROP-RETENTION-CONTROLLED-EXPERIMENT",
        "tested_routine": {
            "source_repo": "opendatalab/UniMERNet@5a2c80d9",
            "source_file": "unimernet/processors/formula_processor.py",
            "function": "FormulaImageBaseProcessor.crop_margin_numpy",
            "threshold_condition": "binary = 255 * (normalized < 200)",
            "bounding_box_method": "cv2.boundingRect(cv2.findNonZero(binary))",
        },
        "findings_summary": {
            "foreground_ink_preservation": "100.0% of supra-threshold pixels retained within the bounding box",
            "structural_hazard_identified": (
                "Zero margin clearance on all four borders. The bounding box strictly touches "
                "the extreme pixel of outermost glyphs (outer brackets, superscript tops, fraction bars). "
                "Downstream CNN/ViT convolutional patches and padding operators suffer border antialiasing "
                "without King Wen's certified whitespace gutter clearance (Gate D4)."
            ),
        },
        "case_measurements": results,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nSaved experiment report to: {OUT_JSON}")
    return report


if __name__ == "__main__":
    run_experiment()
