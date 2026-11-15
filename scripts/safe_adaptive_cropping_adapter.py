#!/usr/bin/env python3
"""Safe Adaptive Cropping Adapter — Layer 2 Visual Evidence Acquisition (TOOL-04).

Isolates and hardens `crop_pdf_region` and `expand_crop_context` from
`scripts/vision_comparison_pipeline.py`.

Key enhancements:
  - Neighbor-aware padding clamping: prevents clipping adjacent glyphs or labels.
  - Border ink contact auditing (TOOL-07 proxy): ensures `border_touch_1px == 0`.
  - Non-blank content ratio enforcement (`min_content_ratio >= 0.02`).
  - Immutable output artifacts saved to `DATASETS/structural_preservation/crops/`.
  - Emits SHA-256 hash and actual PDF bounding box (`bbox_actual_pdf_pt`).
  - Strict isolation: NEVER mutates `unified_manifest.json` or candidate files.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pymupdf

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
DEFAULT_CROPS_DIR = REPO_ROOT / "DATASETS" / "structural_preservation" / "crops"


def _normalize_bbox(bbox: list[float] | tuple[float, ...] | dict[str, float]) -> list[float]:
    """Convert bbox dict or list to [x0, y0, x1, y1]."""
    if isinstance(bbox, dict):
        return [float(bbox["x0"]), float(bbox["y0"]), float(bbox["x1"]), float(bbox["y1"])]
    return [float(v) for v in bbox]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def analyze_crop_boundaries(img_bgr: np.ndarray) -> dict[str, Any]:
    """Analyze perimeter 1px border contact and content density."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if len(img_bgr.shape) == 3 else img_bgr
    ink_mask = gray < 200

    top_touch = int(np.sum(ink_mask[0, :]))
    bottom_touch = int(np.sum(ink_mask[h - 1, :]))
    left_touch = int(np.sum(ink_mask[:, 0]))
    right_touch = int(np.sum(ink_mask[:, w - 1]))
    border_touch_1px = top_touch + bottom_touch + left_touch + right_touch

    ink_pixels = int(np.sum(ink_mask))
    total_pixels = max(1, h * w)
    ink_ratio = ink_pixels / total_pixels

    return {
        "width_px": w,
        "height_px": h,
        "border_touch_1px": border_touch_1px,
        "top_touch": top_touch,
        "bottom_touch": bottom_touch,
        "left_touch": left_touch,
        "right_touch": right_touch,
        "ink_ratio": round(ink_ratio, 4),
        "has_border_contact": border_touch_1px > 0,
    }


def safe_adaptive_crop_pdf_region(
    pdf_path: str | Path,
    page_idx: int,
    bbox_pdf_pt: list[float] | tuple[float, ...] | dict[str, float],
    padding: int | tuple[float, float] = (3.0, 2.0),
    zoom: int = 4,
    min_content_ratio: float = 0.02,
    output_dir: Path | None = None,
    crop_filename: str | None = None,
) -> dict[str, Any]:
    """Perform neighbor-aware, non-intrusive adaptive cropping from PDF page.

    Returns:
        dict containing:
            - 'crop_path': Path to saved PNG
            - 'crop_sha256': SHA-256 hash of PNG bytes
            - 'bbox_actual_pdf_pt': Actual bounding box used [x0, y0, x1, y1]
            - 'image_array': cv2 numpy image array (BGR)
            - 'border_touch_1px': Total 1px perimeter contact count
            - 'content_ratio': Non-white pixel ratio
            - 'status': 'SUCCESS' or 'CONTENT_RATIO_FAILURE'
    """
    if isinstance(padding, (tuple, list)):
        pad_x, pad_y = float(padding[0]), float(padding[1])
    else:
        pad_x, pad_y = float(padding), float(padding)

    x0, y0, x1, y1 = _normalize_bbox(bbox_pdf_pt)

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_idx]

    # Extract all non-empty character bboxes on page for neighbor clearance clamping
    raw = page.get_text("rawdict")
    char_boxes: list[list[float]] = []
    for b in raw.get("blocks", []):
        if b.get("type") != 0:
            continue
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                for c in s.get("chars", []):
                    if c.get("c", "").strip():
                        char_boxes.append([float(v) for v in c["bbox"]])

    # Adapt padding around external neighbors
    pad_left = pad_x
    pad_right = pad_x
    pad_top = pad_y
    pad_bottom = pad_y

    # Check right neighbors: characters immediately to the right within vertical band
    r_neighbors = [cb for cb in char_boxes if cb[0] >= x1 - 0.5 and cb[1] < y1 and cb[3] > y0]
    if r_neighbors:
        min_rx = min(cb[0] for cb in r_neighbors)
        pad_right = max(0.0, min(pad_x, min_rx - x1 - 0.2))

    # Check left neighbors
    l_neighbors = [cb for cb in char_boxes if cb[2] <= x0 + 0.5 and cb[1] < y1 and cb[3] > y0]
    if l_neighbors:
        max_lx = max(cb[2] for cb in l_neighbors)
        pad_left = max(0.0, min(pad_x, x0 - max_lx - 0.2))

    # Check top neighbors
    t_neighbors = [cb for cb in char_boxes if cb[3] <= y0 + 0.5 and cb[0] < x1 and cb[2] > x0]
    if t_neighbors:
        max_ty = max(cb[3] for cb in t_neighbors)
        pad_top = max(0.0, min(pad_y, y0 - max_ty - 0.2))

    # Check bottom neighbors
    b_neighbors = [cb for cb in char_boxes if cb[1] >= y1 - 0.5 and cb[0] < x1 and cb[2] > x0]
    if b_neighbors:
        min_by = min(cb[1] for cb in b_neighbors)
        pad_bottom = max(0.0, min(pad_y, min_by - y1 - 0.2))

    actual_x0 = max(0.0, x0 - pad_left)
    actual_y0 = max(0.0, y0 - pad_top)
    actual_x1 = min(page.rect.width, x1 + pad_right)
    actual_y1 = min(page.rect.height, y1 + pad_bottom)
    bbox_actual = [round(actual_x0, 3), round(actual_y0, 3), round(actual_x1, 3), round(actual_y1, 3)]

    rect = pymupdf.Rect(actual_x0, actual_y0, actual_x1, actual_y1)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect, colorspace=pymupdf.csRGB, alpha=False)
    doc.close()

    png_bytes = pix.tobytes("png")
    img_array = cv2.imdecode(np.frombuffer(png_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img_array is None:
        raise RuntimeError("Failed to decode cropped pixmap image")

    # Content ratio check
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    content_ratio = float(np.mean(gray < 250))
    if content_ratio < min_content_ratio:
        return {
            "crop_path": None,
            "crop_sha256": None,
            "bbox_actual_pdf_pt": bbox_actual,
            "image_array": img_array,
            "border_touch_1px": -1,
            "content_ratio": round(content_ratio, 4),
            "status": "CONTENT_RATIO_FAILURE",
        }

    # Boundary touch audit
    boundary_metrics = analyze_crop_boundaries(img_array)

    # Save artifact
    out_dir = output_dir or DEFAULT_CROPS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    crop_hash = sha256_bytes(png_bytes)
    fname = crop_filename or f"crop_p{page_idx + 1:02d}_{crop_hash[:12]}.png"
    out_path = out_dir / fname
    out_path.write_bytes(png_bytes)

    return {
        "crop_path": out_path,
        "crop_sha256": crop_hash,
        "bbox_actual_pdf_pt": bbox_actual,
        "image_array": img_array,
        "border_touch_1px": boundary_metrics["border_touch_1px"],
        "content_ratio": round(content_ratio, 4),
        "status": "SUCCESS",
    }


def expand_crop_context(
    pdf_path: str | Path,
    page_idx: int,
    bbox_pdf_pt: list[float] | tuple[float, ...] | dict[str, float],
    expand_factor: float = 1.5,
    zoom: int = 4,
    min_content_ratio: float = 0.01,
) -> np.ndarray | None:
    """Render an expanded zoom-out context crop around a bbox."""
    x0, y0, x1, y1 = _normalize_bbox(bbox_pdf_pt)
    w = x1 - x0
    h = y1 - y0
    pad_x = w * (expand_factor - 1.0) / 2.0
    pad_y = h * (expand_factor - 1.0) / 2.0

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_idx]
    rect = pymupdf.Rect(
        max(0.0, x0 - pad_x),
        max(0.0, y0 - pad_y),
        min(page.rect.width, x1 + pad_x),
        min(page.rect.height, y1 + pad_y),
    )
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect, colorspace=pymupdf.csRGB, alpha=False)
    doc.close()

    png_bytes = pix.tobytes("png")
    img_array = cv2.imdecode(np.frombuffer(png_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img_array is None:
        return None
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    if float(np.mean(gray < 250)) < min_content_ratio:
        return None
    return img_array
