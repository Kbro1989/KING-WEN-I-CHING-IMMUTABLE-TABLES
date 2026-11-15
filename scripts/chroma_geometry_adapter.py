#!/usr/bin/env python3
"""Chroma 2D Geometry & Physical Perimeter Gate Adapter (TOOL-02 & TOOL-07).

Integrates:
  1. Layer 3 Physical Cross-Verification via Chroma 2D geometry (fraction vinculums,
     tall delimiters, brackets) on high-resolution rendered pixmaps.
  2. Multi-substrate evidence reconciliation: compares 2D raster vinculum observations
     against font-stream and vector path layers (fuses on agreement, emits UNRESOLVED_CONFLICT
     on contradiction).
  3. Layer 5 Perimeter Contact Gate: evaluates 1px/2px outer crop boundaries and calculates
     physical clearance in PDF points (`min_margin_px / zoom`) for Gate D4 adjudication.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pymupdf

from chroma_visual_reader import kmeans_quantize, find_visual_regions, detect_2d_structures
from audit_rendered_png_producers import analyze_crop_image

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_chroma_vinculums(
    page: pymupdf.Page,
    page_index: int,
    target_bbox_pt: list[float] | None = None,
    zoom: int = 4,
    pdf_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Detect horizontal fraction vinculums in a region or page using Chroma 2D geometry.

    Reconciles raster-detected vinculums with vector drawings and rawdict text stream.
    """
    if pdf_path:
        p = Path(pdf_path)
        input_sha256 = sha256_file(p) if p.exists() else hashlib.sha256(str(p).encode()).hexdigest()
    else:
        input_sha256 = hashlib.sha256(page.get_text().encode("utf-8")).hexdigest()

    clip_rect = (
        pymupdf.Rect(target_bbox_pt[0], target_bbox_pt[1], target_bbox_pt[2], target_bbox_pt[3])
        if target_bbox_pt
        else None
    )

    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip_rect, colorspace=pymupdf.csRGB, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))

    offset_x = clip_rect.x0 if clip_rect else 0.0
    offset_y = clip_rect.y0 if clip_rect else 0.0

    centroids, remapped, palette = kmeans_quantize(img, max_colors=8)
    regions = find_visual_regions(img, remapped, palette, min_size=5, max_size=15000)

    # Collect vector rules for cross-substrate verification
    vector_rules = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r and (r.x1 - r.x0) >= 3.0 and (r.y1 - r.y0) <= 2.5:
            vector_rules.append([round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)])

    # Rawdict characters on page
    raw = page.get_text("rawdict", clip=clip_rect)
    chars = []
    for b in raw.get("blocks", []):
        if b.get("type") != 0:
            continue
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                for c in s.get("chars", []):
                    chars.append({
                        "char": c.get("c", ""),
                        "bbox": [round(v, 3) for v in c.get("bbox", (0, 0, 0, 0))],
                        "font": s.get("font", ""),
                    })

    evidence_records: list[dict[str, Any]] = []
    fraction_candidates = [r for r in regions if r.region_type == "fraction_bar"]

    for idx, fb in enumerate(fraction_candidates):
        x0_pt = round(offset_x + fb.bbox[0] / zoom, 3)
        y0_pt = round(offset_y + fb.bbox[1] / zoom, 3)
        x1_pt = round(offset_x + (fb.bbox[0] + fb.bbox[2]) / zoom, 3)
        y1_pt = round(offset_y + (fb.bbox[1] + fb.bbox[3]) / zoom, 3)
        vinculum_bbox = [x0_pt, y0_pt, x1_pt, y1_pt]

        # Check if matched by vector drawing
        matched_vector = None
        for vr in vector_rules:
            if abs(vr[1] - y0_pt) <= 1.5 and abs(vr[0] - x0_pt) <= 3.0 and abs(vr[2] - x1_pt) <= 3.0:
                matched_vector = vr
                break

        # Check for numerator (above vinculum) and denominator (below vinculum)
        nums = [c for c in chars if c["bbox"][3] <= y0_pt + 1.0 and abs(c["bbox"][3] - y0_pt) <= 18.0 and not (c["bbox"][2] < x0_pt - 4.0 or c["bbox"][0] > x1_pt + 4.0)]
        dens = [c for c in chars if c["bbox"][1] >= y1_pt - 1.0 and abs(c["bbox"][1] - y1_pt) <= 18.0 and not (c["bbox"][2] < x0_pt - 4.0 or c["bbox"][0] > x1_pt + 4.0)]

        num_text = "".join(c["char"] for c in nums).strip()
        den_text = "".join(c["char"] for c in dens).strip()

        # Check for conflict: if font stream has a non-fraction glyph right across the bar center
        conflicting_chars = [
            c for c in chars
            if abs((c["bbox"][1] + c["bbox"][3]) / 2.0 - (y0_pt + y1_pt) / 2.0) <= 0.8
            and not (c["bbox"][2] < x0_pt or c["bbox"][0] > x1_pt)
            and c["char"] not in "-–—="
        ]

        if conflicting_chars:
            status = "UNRESOLVED_CONFLICT"
            confidence = 0.30
        elif matched_vector or (num_text and den_text):
            status = "VERIFIED_BY_GATE" if matched_vector else "OBSERVED"
            confidence = 0.95 if matched_vector else 0.80
        else:
            status = "OBSERVED"
            confidence = 0.60

        evidence_id = f"EVID-L3-CHROMA-P{page_index + 1:02d}-{idx + 1:04d}"
        evidence_records.append({
            "evidence_id": evidence_id,
            "producer": "scripts/chroma_geometry_adapter.py:detect_chroma_vinculums",
            "producer_version": "1.0.0",
            "layer": "L3",
            "input_sha256": input_sha256,
            "page_id": {
                "page_0based": page_index,
                "page_1based": page_index + 1,
            },
            "bbox_pdf_pt": vinculum_bbox,
            "crop_sha256": None,
            "observation": {
                "structure_type": "fraction",
                "vinculum_bbox_pdf_pt": vinculum_bbox,
                "aspect_ratio": round(fb.aspect_ratio, 2),
                "matched_vector_rule": matched_vector,
                "numerator_text": num_text,
                "denominator_text": den_text,
                "conflicting_glyphs": [c["char"] for c in conflicting_chars],
            },
            "confidence": confidence,
            "dependencies": [],
            "status": status,
        })

    return evidence_records


def verify_perimeter_clearance_gate_d4(
    crop_path: str | Path,
    zoom: int = 4,
    gate_d4_threshold_pt: float = 2.0,
) -> dict[str, Any]:
    """Execute Layer 5 Physical Perimeter Contact & Gate D4 Clearance verification."""
    p = Path(crop_path)
    analysis = analyze_crop_image(p)
    if "error" in analysis:
        return {
            "crop_path": str(p),
            "gate_d4_passed": False,
            "clearance_pt": 0.0,
            "border_touch_1px": -1,
            "reason": analysis["error"],
        }

    border_touch = analysis["border_touch_1px"]
    min_margin_px = analysis["min_margin_px"]
    clearance_pt = round(min_margin_px / float(zoom), 3) if min_margin_px >= 0 else 0.0

    passed = (border_touch == 0) and (clearance_pt >= gate_d4_threshold_pt)
    reason = None
    if border_touch > 0:
        reason = f"Border contact detected: border_touch_1px={border_touch}"
    elif clearance_pt < gate_d4_threshold_pt:
        reason = f"Clearance failure: {clearance_pt} pt < {gate_d4_threshold_pt} pt required"

    return {
        "crop_path": str(p),
        "gate_d4_passed": passed,
        "clearance_pt": clearance_pt,
        "min_margin_px": min_margin_px,
        "border_touch_1px": border_touch,
        "border_touch_2px": analysis["border_touch_2px"],
        "reason": reason,
        "status": "PASSED" if passed else "FAILED",
    }
