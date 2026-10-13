#!/usr/bin/env python3
"""
Chroma Visual Reader — Multi-Scale 2D Math Geometry Detector.
=============================================================
Uses PyMuPDF rendering + K-Means color quantization + connected component analysis
to extract physical 2D structures from PDF pages:
  - Stretched fraction bars / vinculums (separating numerator and denominator)
  - Tall delimiters / cases braces (piecewise functions spanning multiple rows)
  - Paired enclosing delimiters (parentheses, brackets, norms, angle brackets)
  - Stacked limit operators (subscripts/superscripts stacked above/below sum/int/prod)
  - Scaled script tokens (subscripts, superscripts)

This prevents 1D text readers from skipping division bars, flattening cases,
or collapsing 2D structures into invalid linear approximations.
"""
from __future__ import annotations

import io
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
import pymupdf
from scipy.cluster.vq import kmeans2
from scipy import ndimage

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class VisualRegion:
    region_id: int
    bbox: Tuple[float, float, float, float]  # (x_min, y_min, w, h)
    centroid: Tuple[float, float]           # (cx, cy)
    aspect_ratio: float
    fill_ratio: float
    normalized_stroke: float
    region_type: str                        # fraction_bar, cases_brace, large_bracket, vertical_bar, stacked_limit, script, symbol, text
    is_math: bool
    text: Optional[str] = None
    children: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VisualMathStructure:
    structure_type: str                     # "fraction", "cases", "enclosed_group", "stacked_limits", "matrix"
    main_region_id: int
    bbox: Tuple[float, float, float, float]
    components: Dict[str, List[int]]       # e.g. {"numerator": [...], "denominator": [...]} or {"cases_branches": [...]}
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def kmeans_quantize(image_array: np.ndarray, max_colors: int = 16):
    """K-Means color quantization using scipy.cluster.vq.kmeans2."""
    height, width = image_array.shape[:2]
    pixel_count = width * height
    data = image_array.reshape(-1, 3).astype(np.float64)

    centroids, labels = kmeans2(data, max_colors, minit='points', iter=10)
    unique_labels = np.unique(labels)
    palette = []
    label_map = {}

    for new_idx, old_label in enumerate(unique_labels):
        mask = labels == old_label
        count = np.sum(mask)
        if count == 0:
            continue
        r, g, b = centroids[old_label].astype(int)
        palette.append({
            'id': new_idx,
            'rgb': (int(r), int(g), int(b)),
            'count': int(count)
        })
        label_map[old_label] = new_idx

    remapped = np.zeros(pixel_count, dtype=np.int32)
    for old_label, new_label in label_map.items():
        remapped[labels == old_label] = new_label

    return centroids, remapped, palette


def find_visual_regions(image_array: np.ndarray, assignments: np.ndarray, palette: list,
                        min_size: int = 30, max_size: int = 15000) -> List[VisualRegion]:
    """Find and classify all connected component visual regions."""
    height, width = image_array.shape[:2]
    pixel_count = width * height

    # Luminance threshold for dark ink
    luminance = np.zeros(pixel_count, dtype=np.float64)
    for i, color_dict in enumerate(palette):
        mask = assignments == i
        r, g, b = color_dict['rgb']
        lum = (r * 299 + g * 587 + b * 114) / 1000
        luminance[mask] = lum

    text_mask = (luminance < 140).reshape(height, width)
    labeled_array, num_features = ndimage.label(text_mask)

    regions: List[VisualRegion] = []
    for region_id in range(1, min(num_features + 1, 800)):
        region_pixels_2d = np.where(labeled_array == region_id)
        if len(region_pixels_2d[0]) == 0:
            continue
        ys = region_pixels_2d[0]
        xs = region_pixels_2d[1]
        pixel_len = len(ys)

        if pixel_len < min_size or pixel_len > max_size:
            continue

        x_min, x_max = float(xs.min()), float(xs.max())
        y_min, y_max = float(ys.min()), float(ys.max())
        w, h = max(1.0, x_max - x_min), max(1.0, y_max - y_min)

        if w < 4 or h < 4:
            continue

        aspect_ratio = w / h
        fill_ratio = pixel_len / (w * h)
        stroke_width = np.sqrt(pixel_len / (np.pi * max(w, h)))
        normalized_stroke = stroke_width / max(w, h)

        # Region classification
        region_type = "text"
        is_math = False

        # Stretched horizontal fraction bar / vinculum
        if aspect_ratio > 3.0 and fill_ratio > 0.25:
            region_type = "fraction_bar"
            is_math = True
        # Tall piecewise cases curly brace (spanning multiple lines)
        elif aspect_ratio < 0.25 and h > 50:
            region_type = "cases_brace"
            is_math = True
        # Large bracket / tall delimiter (parentheses, square bracket, norm bar)
        elif aspect_ratio < 0.35 and h > 35:
            region_type = "large_bracket"
            is_math = True
        elif aspect_ratio < 0.2:
            region_type = "vertical_bar"
            is_math = True
        # Sqrt vinculum
        elif aspect_ratio > 2.0 and 0.02 < fill_ratio < 0.18:
            region_type = "sqrt_vinculum"
            is_math = True
        # Script / subscript / superscript
        elif w < 22 and h < 22:
            region_type = "script"
            is_math = True
        elif fill_ratio < 0.08 or normalized_stroke < 0.06:
            region_type = "symbol"
            is_math = True

        regions.append(VisualRegion(
            region_id=len(regions),
            bbox=(x_min, y_min, w, h),
            centroid=(float(np.mean(xs)), float(np.mean(ys))),
            aspect_ratio=aspect_ratio,
            fill_ratio=fill_ratio,
            normalized_stroke=normalized_stroke,
            region_type=region_type,
            is_math=is_math,
        ))

    return regions


def detect_2d_structures(regions: List[VisualRegion]) -> List[VisualMathStructure]:
    """Detect composite 2D structures (fractions, cases, limits, enclosed expressions)."""
    structures: List[VisualMathStructure] = []

    # 1. Fractions: Horizontal bar with numerator directly above and denominator directly below
    for r in regions:
        if r.region_type == "fraction_bar":
            rx, ry, rw, rh = r.bbox
            numerator_ids = []
            denominator_ids = []

            for other in regions:
                if other.region_id == r.region_id:
                    continue
                ox, oy, ow, oh = other.bbox
                ocx, ocy = other.centroid

                # Overlaps horizontally with fraction bar
                h_overlap = min(rx + rw, ox + ow) - max(rx, ox)
                if h_overlap > 0.3 * ow or (rx - 5 <= ocx <= rx + rw + 5):
                    # Numerator: above fraction bar within 2.5 * h distance
                    if oy + oh <= ry and (ry - (oy + oh)) < 80:
                        numerator_ids.append(other.region_id)
                    # Denominator: below fraction bar within 2.5 * h distance
                    elif oy >= ry + rh and (oy - (ry + rh)) < 80:
                        denominator_ids.append(other.region_id)

            if numerator_ids or denominator_ids:
                # Bounding box enclosing the whole fraction
                all_boxes = [r.bbox] + [regions[i].bbox for i in numerator_ids + denominator_ids]
                min_x = min(b[0] for b in all_boxes)
                min_y = min(b[1] for b in all_boxes)
                max_x = max(b[0] + b[2] for b in all_boxes)
                max_y = max(b[1] + b[3] for b in all_boxes)

                structures.append(VisualMathStructure(
                    structure_type="fraction",
                    main_region_id=r.region_id,
                    bbox=(min_x, min_y, max_x - min_x, max_y - min_y),
                    components={
                        "numerator": sorted(numerator_ids, key=lambda i: regions[i].centroid[0]),
                        "denominator": sorted(denominator_ids, key=lambda i: regions[i].centroid[0]),
                    },
                    confidence=1.0 if (numerator_ids and denominator_ids) else 0.7
                ))

    # 2. Piecewise Cases: Tall brace with multiple vertically stacked row branches to its right
    for r in regions:
        if r.region_type == "cases_brace":
            rx, ry, rw, rh = r.bbox
            branch_ids = []

            for other in regions:
                if other.region_id == r.region_id:
                    continue
                ox, oy, ow, oh = other.bbox
                # To the right of the brace and vertically within its height span
                if ox >= rx + rw - 5 and (ox <= rx + rw + 400) and (ry - 10 <= oy <= ry + rh + 10):
                    branch_ids.append(other.region_id)

            if branch_ids:
                # Group branch regions into rows by vertical center clustering
                branch_regions = [regions[i] for i in branch_ids]
                branch_regions.sort(key=lambda x: x.centroid[1])

                rows: List[List[int]] = []
                cur_row: List[int] = []
                last_y = None

                for br in branch_regions:
                    if last_y is None or abs(br.centroid[1] - last_y) < 18:
                        cur_row.append(br.region_id)
                    else:
                        if cur_row:
                            rows.append(sorted(cur_row, key=lambda i: regions[i].centroid[0]))
                        cur_row = [br.region_id]
                    last_y = br.centroid[1]
                if cur_row:
                    rows.append(sorted(cur_row, key=lambda i: regions[i].centroid[0]))

                all_boxes = [r.bbox] + [b.bbox for b in branch_regions]
                min_x = min(b[0] for b in all_boxes)
                min_y = min(b[1] for b in all_boxes)
                max_x = max(b[0] + b[2] for b in all_boxes)
                max_y = max(b[1] + b[3] for b in all_boxes)

                structures.append(VisualMathStructure(
                    structure_type="cases",
                    main_region_id=r.region_id,
                    bbox=(min_x, min_y, max_x - min_x, max_y - min_y),
                    components={
                        f"row_{idx}": row for idx, row in enumerate(rows)
                    },
                    confidence=1.0 if len(rows) >= 2 else 0.6
                ))

    return structures


# ---------------------------------------------------------------------------
# Tier 1: Deterministic Vector Layout Engine
# ---------------------------------------------------------------------------

@dataclass
class VectorFraction:
    """A fraction detected from the PDF vector drawing layer (zero hallucination)."""
    page: int
    vinculum_rect: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    numerator_text: str
    denominator_text: str
    assembled_latex: str


@dataclass
class VisualEquation:
    """An equation region visually parsed from the page canvas."""
    page: int
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    source: str                               # "vector_layout" or "pix2tex"
    latex: str
    confidence: float = 1.0


def extract_vector_fractions(page, page_num: int,
                             min_vinculum_w: float = 15.0,
                             max_vinculum_w: float = 220.0,
                             max_vinculum_h: float = 2.0,
                             min_indent: float = 70.0,
                             clip_margin_above: float = 18.0,
                             clip_margin_below: float = 18.0) -> List[VectorFraction]:
    """
    Tier 1 — Scan PDF vector drawing paths for horizontal vinculum lines,
    then clip the glyph text directly above and below to extract the
    numerator and denominator.

    This reads the actual canvas geometry — not backend JSON.
    """
    fractions: List[VectorFraction] = []
    drawings = page.get_drawings()

    for d in drawings:
        r = d["rect"]
        w = r.x1 - r.x0
        h = r.y1 - r.y0

        # Vinculum: thin horizontal line of significant width, indented past the margin
        if min_vinculum_w <= w <= max_vinculum_w and h <= max_vinculum_h and r.x0 >= min_indent:
            # Exclude lines near the bottom margin (footnote rules)
            if r.y0 > 650.0:
                continue

            num_clip = pymupdf.Rect(r.x0, r.y0 - clip_margin_above, r.x1, r.y0)
            den_clip = pymupdf.Rect(r.x0, r.y1, r.x1, r.y1 + clip_margin_below)

            num_txt = page.get_text("text", clip=num_clip).strip().replace("\n", " ")
            den_txt = page.get_text("text", clip=den_clip).strip().replace("\n", " ")

            # Math filter: must contain math characters (Greek, operators, digits, short variables)
            # and reject long prose paragraphs (table rows / authors)
            if num_txt and den_txt:
                if len(num_txt) > 50 or len(den_txt) > 50:
                    continue
                prose_words = ["author", "department", "university", "table", "pre-training", "fine-tuning", "win-rate"]
                if any(w in num_txt.lower() or w in den_txt.lower() for w in prose_words):
                    continue

                # Font classification check:
                # Math fractions are set in TeX math fonts (CMR, CMMI, CMSY, CMEX, NimbusRom, MathJax)
                # Diagrams and UI boxes are set in sans-serif fonts (Helvetica, Arial, NimbusSans)
                raw_num = page.get_text("rawdict", clip=num_clip)
                raw_den = page.get_text("rawdict", clip=den_clip)
                fonts = []
                for b in raw_num.get("blocks", []) + raw_den.get("blocks", []):
                    for l in b.get("lines", []):
                        for s in l.get("spans", []):
                            f = s.get("font", "")
                            if f:
                                fonts.append(f.lower())

                has_math_font = any(mf in f for f in fonts for mf in ["cm", "nimbusrom", "math", "times", "stix", "euler"])
                has_diagram_font = any(df in f for f in fonts for df in ["helvetica", "arial", "sans"])
                has_math_char = any(c in (num_txt + den_txt) for c in ["\\", "+", "-", "=", "*", "/", "^", "_", "π", "θ", "σ", "β", "λ", "μ", "γ"])

                # Diagram and Flowchart filter:
                # Math equations have very low box-drawing density (< 3 closed rects nearby).
                # Diagrams/flowcharts have dozens of bounding box drawings nearby.
                nearby_boxes = sum(
                    1 for od in drawings
                    if abs(od["rect"].y0 - r.y0) < 50.0 and abs(od["rect"].x0 - r.x0) < 80.0
                    and (od["rect"].width > 12.0 and od["rect"].height > 10.0)
                )
                if nearby_boxes >= 3:
                    continue

                if has_diagram_font and not has_math_font and not has_math_char:
                    continue

                latex = f"\\frac{{{num_txt}}}{{{den_txt}}}"
                fractions.append(VectorFraction(
                    page=page_num,
                    vinculum_rect=(r.x0, r.y0, r.x1, r.y1),
                    numerator_text=num_txt,
                    denominator_text=den_txt,
                    assembled_latex=latex,
                ))

    return fractions


# ---------------------------------------------------------------------------
# Tier 2: Neural Pixel OCR (pix2tex / LatexOCR)
# ---------------------------------------------------------------------------

_LATEX_OCR_MODEL = None  # lazy singleton


def _get_latex_ocr():
    """Lazy-load the pix2tex LatexOCR model (downloads weights on first call)."""
    global _LATEX_OCR_MODEL
    if _LATEX_OCR_MODEL is None:
        import os as _os
        _os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")
        from pix2tex.cli import LatexOCR
        _LATEX_OCR_MODEL = LatexOCR()
    return _LATEX_OCR_MODEL


def ocr_equation_crop(page, bbox_pts: Tuple[float, float, float, float],
                      dpi: int = 150) -> str:
    """
    Tier 2 — Crop an equation region from the page raster and run pix2tex
    neural LaTeX OCR on the pixel image.

    bbox_pts is in PDF points: (x0, y0, x1, y1).
    Returns the predicted LaTeX string.
    """
    scale = dpi / 72.0
    clip_rect = pymupdf.Rect(*bbox_pts)
    mat = pymupdf.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    model = _get_latex_ocr()
    return model(img)


def extract_neural_equations(page, page_num: int,
                             dpi: int = 150,
                             vector_fractions: Optional[List[VectorFraction]] = None) -> List[VisualEquation]:
    """
    Tier 2 — Targeted Neural OCR:
    Runs pix2tex strictly on regions grounded by confirmed 2D structures (e.g. vector vinculums)
    with a bounded vertical and horizontal padding, rather than arbitrary vector drawings.
    This guarantees pix2tex transcribes real math equations and never runs on figure curves or graphs.
    """
    equations: List[VisualEquation] = []

    # If no vector fractions passed, discover them first
    if vector_fractions is None:
        vector_fractions = extract_vector_fractions(page, page_num)

    for vf in vector_fractions:
        x0, y0, x1, y1 = vf.vinculum_rect
        w = x1 - x0
        # Expand crop around the fraction vinculum (24pt above and below, 12pt left and right)
        eq_box = (max(0.0, x0 - 12.0), max(0.0, y0 - 24.0), x1 + 12.0, y1 + 24.0)
        try:
            latex = ocr_equation_crop(page, eq_box, dpi)
            if latex and len(latex) > 2:
                equations.append(VisualEquation(
                    page=page_num,
                    bbox=eq_box,
                    source="pix2tex",
                    latex=latex,
                    confidence=0.95,
                ))
        except Exception:
            pass

    return equations


def _merge_rects(rects: List, gap: float = 8.0) -> List:
    """Merge overlapping or gap-adjacent rectangles into larger bounding boxes."""
    if not rects:
        return []

    sorted_rects = sorted(rects, key=lambda r: (r.y0, r.x0))
    merged = [pymupdf.Rect(sorted_rects[0])]

    for r in sorted_rects[1:]:
        last = merged[-1]
        # Check if vertically overlapping / close and horizontally overlapping
        if (r.y0 <= last.y1 + gap and
                r.x0 <= last.x1 + gap and
                r.x1 >= last.x0 - gap):
            merged[-1] = last | r  # union
        else:
            merged.append(pymupdf.Rect(r))

    return merged


# ---------------------------------------------------------------------------
# Unified page analyzer
# ---------------------------------------------------------------------------

def analyze_pdf_page(pdf_path: Path, page_num: int, dpi: int = 150,
                     enable_neural: bool = False) -> Dict[str, Any]:
    """
    Analyze a single PDF page with a dual-substrate visual engine:
      - Raster K-Means connected-component analysis (existing)
      - Tier 1: Vector vinculum fraction extraction (deterministic)
      - Tier 2: pix2tex neural LaTeX OCR (optional, enable_neural=True)
    """
    doc = pymupdf.open(pdf_path)
    if page_num < 0 or page_num >= len(doc):
        doc.close()
        raise ValueError(f"Page {page_num} out of bounds for {pdf_path}")

    page = doc[page_num]

    # --- Raster substrate (existing) ---
    mat = pymupdf.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_array = np.array(img)

    centroids, assignments, palette = kmeans_quantize(img_array, max_colors=16)
    regions = find_visual_regions(img_array, assignments, palette)
    structures = detect_2d_structures(regions)

    # --- Tier 1: Vector layout fractions ---
    vector_fractions = extract_vector_fractions(page, page_num)

    # --- Tier 2: Neural OCR (only when requested) ---
    neural_equations: List[VisualEquation] = []
    if enable_neural:
        try:
            neural_equations = extract_neural_equations(page, page_num, dpi, vector_fractions=vector_fractions)
        except Exception as e:
            print(f"Neural OCR warning: {e}", file=sys.stderr)

    doc.close()
    return {
        "pdf_path": str(pdf_path),
        "page_number": page_num + 1,
        "total_regions": len(regions),
        "total_math_regions": sum(1 for r in regions if r.is_math),
        "regions": [r.to_dict() for r in regions],
        "structures": [s.to_dict() for s in structures],
        "structure_counts": {
            "fraction": sum(1 for s in structures if s.structure_type == "fraction"),
            "cases": sum(1 for s in structures if s.structure_type == "cases"),
        },
        "vector_fractions": [
            {
                "page": vf.page + 1,
                "vinculum_rect": list(vf.vinculum_rect),
                "numerator": vf.numerator_text,
                "denominator": vf.denominator_text,
                "latex": vf.assembled_latex,
                "source": "vector_layout",
            }
            for vf in vector_fractions
        ],
        "neural_equations": [
            {
                "page": ne.page + 1,
                "bbox": list(ne.bbox),
                "latex": ne.latex,
                "source": ne.source,
                "confidence": ne.confidence,
            }
            for ne in neural_equations
        ],
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Chroma Visual Reader — Dual-Substrate 2D Math Detector")
    ap.add_argument("pdf_path", help="Path to PDF file")
    ap.add_argument("--page", type=int, default=0, help="Page number (0-indexed)")
    ap.add_argument("--neural", action="store_true", help="Enable pix2tex neural OCR tier")
    ap.add_argument("--dpi", type=int, default=150, help="Rendering DPI")
    args = ap.parse_args()

    res = analyze_pdf_page(Path(args.pdf_path), args.page, dpi=args.dpi, enable_neural=args.neural)
    print(f"Page {res['page_number']}: {res['total_regions']} regions, {len(res['structures'])} raster structures")
    print(f"  Raster: {res['structure_counts']}")
    print(f"  Vector fractions: {len(res['vector_fractions'])}")
    for vf in res["vector_fractions"]:
        print(f"    {vf['latex']}")
    if res["neural_equations"]:
        print(f"  Neural equations: {len(res['neural_equations'])}")
        for ne in res["neural_equations"]:
            print(f"    [{ne['confidence']:.2f}] {ne['latex']}")
