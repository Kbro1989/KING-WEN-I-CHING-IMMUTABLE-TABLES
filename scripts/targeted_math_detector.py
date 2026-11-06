#!/usr/bin/env python3
"""
Targeted mathematical notation detector — ArenaPO pilot, v1.1

Observation-only detector. It does not reconstruct equations, infer missing
symbols, close delimiters, or certify mathematical correctness.

Dependencies:
    pip install pymupdf numpy opencv-python

Usage:
    python targeted_math_detector.py paper.pdf --pages 1-8 --out arena_math_audit
    python targeted_math_detector.py paper.pdf --pages all --zoom 4 --out arena_math_audit

CLI page numbers are 1-based.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path

try:
    import fitz
except ImportError:
    import pymupdf as fitz
import numpy as np
import cv2

GREEK = set("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩϕϑϖϱς")
MATH = set("∫∑∏√∞∂∇±∓×·≤≥≠≈∝∈∉⊂⊆→⇒↔∼")
MATH_PUNCT = set("=<>+-−*/^_{}[]()|,:;")
TARGET_LATEX_NAMES = (
    "theta", "mu", "sigma", "beta", "phi", "Phi", "lambda",
    "alpha", "Q_D", "Q_w", "Q_l", "Q_D*", "sigma_D", "mu_D"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rect4(rect):
    return [round(float(v), 3) for v in rect]


def selected_pages(spec: str, total: int):
    if spec.lower().strip() == "all":
        return list(range(total))
    chosen = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            first, last = map(int, part.split("-", 1))
            if first < 1 or last < first or last > total:
                raise ValueError(f"Invalid page range: {part}")
            chosen.update(range(first - 1, last))
        elif part:
            page = int(part)
            if page < 1 or page > total:
                raise ValueError(f"Invalid page number: {page}")
            chosen.add(page - 1)
    return sorted(chosen)


def is_math_char(char: str) -> bool:
    return bool(char) and (
        char in GREEK or char in MATH or char in MATH_PUNCT
        or char.isdigit() or char in "∅"
    )


def extract_raw_observations(page, page_index: int):
    """
    Use get_text('rawdict'), not get_text('dict'):
    rawdict supplies per-character records and bounding boxes.
    """
    raw = page.get_text("rawdict")
    spans, chars = [], []
    for block_i, block in enumerate(raw.get("blocks", [])):
        if "lines" not in block:
            continue
        for line_i, line in enumerate(block["lines"]):
            for span_i, span in enumerate(line.get("spans", [])):
                raw_chars = span.get("chars", [])
                text = "".join(c.get("c", "") for c in raw_chars)
                math_count = sum(is_math_char(c) for c in text)
                if math_count or any(name in text for name in TARGET_LATEX_NAMES):
                    spans.append({
                        "page_index": page_index,
                        "block_index": block_i,
                        "line_index": line_i,
                        "span_index": span_i,
                        "text": text,
                        "font": span.get("font"),
                        "font_size_pt": round(float(span.get("size", 0)), 3),
                        "bbox_pdf_pt": rect4(span.get("bbox", (0, 0, 0, 0))),
                        "math_character_count": math_count,
                        "math_character_ratio": round(math_count / max(1, len(text)), 4),
                        "source": "pymupdf_rawdict_span",
                    })
                for char_i, item in enumerate(raw_chars):
                    char = item.get("c", "")
                    bbox = item.get("bbox")
                    if not bbox or not char.strip():
                        continue
                    x0, y0, x1, y1 = map(float, bbox)
                    chars.append({
                        "page_index": page_index,
                        "block_index": block_i,
                        "line_index": line_i,
                        "span_index": span_i,
                        "char_index": char_i,
                        "char": char,
                        "font": span.get("font"),
                        "font_size_pt": round(float(span.get("size", 0)), 3),
                        "bbox_pdf_pt": rect4(bbox),
                        "width_pt": round(x1 - x0, 3),
                        "height_pt": round(y1 - y0, 3),
                        "is_math_char": is_math_char(char),
                    })
    return spans, chars


def geometry_candidates(chars):
    heights = [c["height_pt"] for c in chars if c["height_pt"] > 0.1]
    if not heights:
        return []
    page_median = statistics.median(heights)
    found = []
    for c in chars:
        w, h = c["width_pt"], c["height_pt"]
        if h <= 0:
            continue
        aspect = h / max(w, 0.25)
        reasons = []
        if h > 1.35 * page_median and aspect > 1.25:
            reasons.append("tall_glyph_or_stretched_delimiter_candidate")
        if h < 0.72 * page_median:
            reasons.append("small_script_or_small_symbol_candidate")
        if w > 1.8 * page_median:
            reasons.append("wide_operator_or_stretched_symbol_candidate")
        if reasons:
            found.append({
                **c,
                "page_median_character_height_pt": round(page_median, 3),
                "height_ratio": round(h / page_median, 3),
                "height_width_ratio": round(aspect, 3),
                "candidate_reasons": reasons,
                "status": "unverified_visual_candidate",
            })
    return found


def script_position_candidates(chars):
    """
    Compare small glyphs against nearby normal-size glyphs.
    PDF y coordinates increase downward: raised glyphs have smaller y-centres.
    This is a geometric hint only; attachment is not inferred.
    """
    if not chars:
        return []
    heights = [c["height_pt"] for c in chars if c["height_pt"] > 0.1]
    if not heights:
        return []
    normal_h = statistics.median(heights)
    normal = [c for c in chars if 0.78 * normal_h <= c["height_pt"] <= 1.35 * normal_h]
    candidates = []
    for small in chars:
        if small["height_pt"] >= 0.78 * normal_h:
            continue
        sx0, sy0, sx1, sy1 = small["bbox_pdf_pt"]
        scy = (sy0 + sy1) / 2
        nearby = []
        for base in normal:
            bx0, by0, bx1, by1 = base["bbox_pdf_pt"]
            # Local horizontal neighborhood; avoid comparing unrelated lines.
            gap = max(0.0, max(bx0 - sx1, sx0 - bx1))
            if gap <= max(8.0, 0.8 * normal_h):
                nearby.append((gap, base))
        if not nearby:
            continue
        nearby.sort(key=lambda x: x[0])
        reference = [x[1] for x in nearby[:6]]
        ref_centres = [
            (x["bbox_pdf_pt"][1] + x["bbox_pdf_pt"][3]) / 2
            for x in reference
        ]
        ref_cy = statistics.median(ref_centres)
        delta = scy - ref_cy
        if abs(delta) < 0.18 * normal_h:
            continue
        candidates.append({
            **small,
            "script_position_candidate": "superscript_candidate" if delta < 0 else "subscript_candidate",
            "vertical_offset_from_nearby_glyphs_pt": round(delta, 3),
            "reference_characters": [x["char"] for x in reference],
            "attachment_status": "unresolved",
            "status": "geometric_hypothesis_only",
        })
    return candidates


def render_visual_candidates(page, page_index, zoom, out_dir):
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    otsu_value, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    count, labels, stats, centers = cv2.connectedComponentsWithStats(binary, 8)

    page_dir = out_dir / f"page_{page_index + 1:04d}"
    page_dir.mkdir(parents=True, exist_ok=True)
    render_path = page_dir / "page_render.png"
    threshold_path = page_dir / "page_threshold.png"
    cv2.imwrite(str(render_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(threshold_path), binary)

    candidates = []
    margin = round(8 * zoom)
    for component_id in range(1, count):
        x, y, w, h, area = map(int, stats[component_id])
        if area < 3:
            continue
        reasons = []
        if h >= 1.5 * max(w, 1) and h >= 12:
            reasons.append("tall_narrow_component")
        if w >= 30 and h >= 5 and w / max(h, 1) >= 2.0:
            reasons.append("wide_horizontal_component")
        if not reasons:
            continue

        x0, y0 = max(0, x - margin), max(0, y - margin)
        x1, y1 = min(gray.shape[1], x + w + margin), min(gray.shape[0], y + h + margin)
        crop = image[y0:y1, x0:x1]
        crop_path = page_dir / f"component_{len(candidates):04d}.png"
        cv2.imwrite(str(crop_path), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))

        candidates.append({
            "component_id": component_id,
            "bbox_render_px": [x, y, x + w, y + h],
            "bbox_pdf_pt_approx": [round(v / zoom, 3) for v in (x, y, x + w, y + h)],
            "crop_bbox_render_px": [x0, y0, x1, y1],
            "crop_path": str(crop_path),
            "width_px": w,
            "height_px": h,
            "area_px": area,
            "height_width_ratio": round(h / max(w, 1), 3),
            "centroid_px": [round(float(centers[component_id][0]), 2),
                            round(float(centers[component_id][1]), 2)],
            "candidate_reasons": reasons,
            "status": "unverified_visual_candidate",
        })

    return {
        "render_size_px": [pix.width, pix.height],
        "render_zoom": zoom,
        "otsu_threshold": int(otsu_value),
        "render_path": str(render_path),
        "threshold_path": str(threshold_path),
        "connected_component_count": count - 1,
        "visual_candidates": candidates,
    }


def main():
    parser = argparse.ArgumentParser(description="Targeted mathematical notation detector")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", default="all")
    parser.add_argument("--zoom", type=float, default=4.0)
    parser.add_argument("--out", type=Path, default=Path("arena_math_audit"))
    args = parser.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")
    if not 1 <= args.zoom <= 8:
        raise SystemExit("--zoom must be between 1 and 8")

    args.out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    page_indexes = selected_pages(args.pages, len(doc))
    source_hash = sha256_file(args.pdf)
    records = []

    for page_index in page_indexes:
        page = doc[page_index]
        spans, chars = extract_raw_observations(page, page_index)
        geometry = geometry_candidates(chars)
        scripts = script_position_candidates(chars)
        visual = render_visual_candidates(page, page_index, args.zoom, args.out)

        record = {
            "schema_version": "1.1",
            "page_number_1_based": page_index + 1,
            "page_size_pdf_pt": [round(page.rect.width, 3), round(page.rect.height, 3)],
            "math_like_text_spans": spans,
            "character_observations": chars,
            "geometry_candidates": geometry,
            "script_position_candidates": scripts,
            "visual_component_analysis": visual,
            "limitations": [
                "PDF text extraction can omit or mis-map glyphs because of font encodings.",
                "Visual connected components are marks, not semantic symbols.",
                "Tall components are not automatically delimiters; wide components are not automatically fraction bars.",
                "Superscript/subscript labels are positional hypotheses, not validated attachments.",
                "No OCR, equation reconstruction, delimiter repair, or semantic validation is performed.",
            ],
        }
        records.append(record)
        print(
            f"Page {page_index + 1}: spans={len(spans)}, chars={len(chars)}, "
            f"geometry_candidates={len(geometry)}, script_candidates={len(scripts)}, "
            f"visual_candidates={len(visual['visual_candidates'])}"
        )

    output = {
        "tool": "targeted_math_detector",
        "version": "1.1",
        "source_pdf": str(args.pdf.resolve()),
        "source_pdf_sha256": source_hash,
        "selected_pages_1_based": [i + 1 for i in page_indexes],
        "processed_page_count": len(page_indexes),
        "records": records,
    }
    out_path = args.out / "targeted_math_detection.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {out_path}")
    print("Inspect candidate crops; candidate labels are not mathematical interpretations.")


if __name__ == "__main__":
    main()
