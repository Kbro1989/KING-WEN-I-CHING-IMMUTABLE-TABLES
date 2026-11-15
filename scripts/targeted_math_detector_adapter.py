#!/usr/bin/env python3
"""Targeted Math Detector Adapter — Layer 1 Discovery Channel.

Wraps observation extraction from `scripts/targeted_math_detector.py` without
the `TARGET_LATEX_NAMES` prior. Performs unconditioned discovery of candidate
mathematical notation regions and outputs standardized evidence sidecars
strictly adhering to the V2.3 Evidence Channel Registry schema.

Invariants:
  - Zero gold leakage: Candidate generation never reads reference bboxes or ground truth.
  - Zero corpus-specific priors: `TARGET_LATEX_NAMES` is removed; discovery relies on
    intrinsic character sets, math font families, and spatial relations.
  - Output coordinates are normalized to `bbox_pdf_pt` in PDF points (72 DPI).
"""
from __future__ import annotations

import hashlib
import re
import statistics
from pathlib import Path
from typing import Any

import pymupdf

from targeted_math_detector import (
    GREEK,
    MATH,
    MATH_PUNCT,
    is_math_char,
    rect4,
    geometry_candidates,
    script_position_candidates,
)

MATH_FONT_TOKENS = ("cmex", "cmsy", "cmmi", "cmbx", "cmmib", "msbm", "nimbus")
RELATION_SYMBOLS = set("=<>≤≥≠≈∝∈∉∼≡|")
EQ_LABEL_PATTERN = re.compile(r"^\((\d+|[A-Za-z0-9\.\-]+)\)$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_math_font(font_name: str | None) -> bool:
    if not font_name:
        return False
    fn = font_name.lower()
    return any(tok in fn for tok in MATH_FONT_TOKENS)


def extract_raw_observations_unconditioned(page: pymupdf.Page, page_index: int) -> tuple[list[dict], list[dict]]:
    """Extract raw spans and characters without TARGET_LATEX_NAMES prior."""
    raw = page.get_text("rawdict")
    spans: list[dict] = []
    chars: list[dict] = []

    for block_i, block in enumerate(raw.get("blocks", [])):
        if block.get("type") != 0 or "lines" not in block:
            continue
        for line_i, line in enumerate(block["lines"]):
            for span_i, span in enumerate(line.get("spans", [])):
                raw_chars = span.get("chars", [])
                text = "".join(c.get("c", "") for c in raw_chars)
                if not text:
                    continue
                math_count = sum(is_math_char(c) for c in text)
                has_m_font = is_math_font(span.get("font"))

                if math_count > 0 or has_m_font:
                    spans.append({
                        "page_index": page_index,
                        "block_index": block_i,
                        "line_index": line_i,
                        "span_index": span_i,
                        "text": text,
                        "font": span.get("font"),
                        "font_size_pt": round(float(span.get("size", 0.0)), 3),
                        "bbox_pdf_pt": rect4(span.get("bbox", (0, 0, 0, 0))),
                        "math_character_count": math_count,
                        "math_character_ratio": round(math_count / max(1, len(text)), 4),
                        "is_math_font": has_m_font,
                        "source": "unconditioned_rawdict_span",
                    })

                for char_i, item in enumerate(raw_chars):
                    c = item.get("c", "")
                    bbox = item.get("bbox")
                    if not bbox or not c.strip():
                        continue
                    x0, y0, x1, y1 = map(float, bbox)
                    chars.append({
                        "page_index": page_index,
                        "block_index": block_i,
                        "line_index": line_i,
                        "span_index": span_i,
                        "char_index": char_i,
                        "char": c,
                        "font": span.get("font"),
                        "font_size_pt": round(float(span.get("size", 0.0)), 3),
                        "bbox_pdf_pt": rect4(bbox),
                        "width_pt": round(x1 - x0, 3),
                        "height_pt": round(y1 - y0, 3),
                        "is_math_char": is_math_char(c),
                        "is_math_font": has_m_font,
                    })

    return spans, chars


def _extract_candidate_lines(page: pymupdf.Page) -> list[dict]:
    """Group character spans into candidate lines with math density scoring."""
    raw = page.get_text("rawdict")
    candidate_lines = []

    for block in raw.get("blocks", []):
        if block.get("type") != 0 or "lines" not in block:
            continue
        for line in block.get("lines", []):
            line_chars = []
            fonts = set()
            for s in line.get("spans", []):
                line_chars.extend(s.get("chars", []))
                if s.get("font"):
                    fonts.add(s["font"])
            if not line_chars:
                continue

            text = "".join(c.get("c", "") for c in line_chars)
            stripped = text.strip()
            if not stripped:
                continue

            math_chars = sum(is_math_char(c) for c in text)
            ratio = math_chars / len(text)
            has_relation = any(c in RELATION_SYMBOLS for c in text)
            has_mfont = any(is_math_font(f) for f in fonts)
            is_label = bool(EQ_LABEL_PATTERN.match(stripped))

            # Include if math density is high, has relation, has math font, or is equation label
            if ratio >= 0.20 or (has_relation and ratio >= 0.10) or (has_mfont and ratio >= 0.15) or is_label:
                candidate_lines.append({
                    "bbox": rect4(line["bbox"]),
                    "text": text,
                    "math_char_count": math_chars,
                    "char_count": len(text),
                    "math_ratio": round(ratio, 4),
                    "has_relation": has_relation,
                    "is_label": is_label,
                    "fonts": sorted(list(fonts)),
                })

    return candidate_lines


def cluster_candidate_lines(lines: list[dict], max_vertical_gap: float = 16.0) -> list[list[dict]]:
    """Cluster lines into candidate mathematical blocks by spatial proximity."""
    if not lines:
        return []

    # Sort lines by vertical position y0
    sorted_lines = sorted(lines, key=lambda l: (l["bbox"][1], l["bbox"][0]))
    clusters: list[list[dict]] = []

    for line in sorted_lines:
        if not clusters:
            clusters.append([line])
            continue

        assigned = False
        # Try to match with existing cluster in same column region
        for cluster in reversed(clusters):
            last_line = cluster[-1]
            # Column check (e.g., col1 x < 300, col2 x >= 300)
            same_col = (line["bbox"][0] < 300 and last_line["bbox"][0] < 300) or (
                line["bbox"][0] >= 300 and last_line["bbox"][0] >= 300
            )
            v_gap = line["bbox"][1] - last_line["bbox"][3]

            # Horizontal overlap or adjacent horizontal alignment (e.g. equation formula and label)
            h_overlap = not (line["bbox"][2] < last_line["bbox"][0] or line["bbox"][0] > last_line["bbox"][2])
            y_overlap = not (line["bbox"][3] < last_line["bbox"][1] or line["bbox"][1] > last_line["bbox"][3])

            # If cluster already contains an equation label and incoming line is below, do not merge
            has_label = any(l.get("is_label") for l in cluster)
            if has_label and v_gap > 0.5:
                continue

            if same_col and ((0 <= v_gap <= max_vertical_gap) or y_overlap):
                cluster.append(line)
                assigned = True
                break

        if not assigned:
            clusters.append([line])

    return clusters


def discover_candidates(
    page: pymupdf.Page,
    page_index: int,
    pdf_path: str | Path | None = None,
    min_confidence: float = 0.25,
) -> list[dict[str, Any]]:
    """Discover unconditioned mathematical candidate regions on a page.

    Returns standardized evidence sidecars adhering to the L1 specification.
    """
    if pdf_path:
        p = Path(pdf_path)
        input_sha256 = sha256_file(p) if p.exists() else hashlib.sha256(str(p).encode()).hexdigest()
    else:
        # Fallback hash of raw text stream
        input_sha256 = hashlib.sha256(page.get_text().encode("utf-8")).hexdigest()

    candidate_lines = _extract_candidate_lines(page)
    clusters = cluster_candidate_lines(candidate_lines)

    evidence_records: list[dict[str, Any]] = []

    for idx, cluster in enumerate(clusters):
        # Discard clusters that are only a standalone label without formula context
        if len(cluster) == 1 and cluster[0]["is_label"]:
            continue

        x0 = min(l["bbox"][0] for l in cluster)
        y0 = min(l["bbox"][1] for l in cluster)
        x1 = max(l["bbox"][2] for l in cluster)
        y1 = max(l["bbox"][3] for l in cluster)

        all_text = " ".join(l["text"].strip() for l in cluster)
        total_chars = sum(l["char_count"] for l in cluster)
        total_math = sum(l["math_char_count"] for l in cluster)
        math_ratio = total_math / max(1, total_chars)
        has_relation = any(l["has_relation"] for l in cluster)
        all_fonts = sorted(list({f for l in cluster for f in l["fonts"]}))
        has_mfont = any(is_math_font(f) for f in all_fonts)
        has_label = any(l["is_label"] for l in cluster)

        # Confidence calculation based strictly on intrinsic mathematical properties
        conf = 0.0
        conf += min(0.40, math_ratio * 0.6)
        if has_relation:
            conf += 0.25
        if has_mfont:
            conf += 0.25
        if has_label:
            conf += 0.10

        confidence = round(min(1.0, conf), 3)
        if confidence < min_confidence:
            continue

        evidence_id = f"EVID-L1-TMD-P{page_index + 1:02d}-{idx + 1:04d}"
        sidecar: dict[str, Any] = {
            "evidence_id": evidence_id,
            "producer": "scripts/targeted_math_detector_adapter.py:discover_candidates",
            "producer_version": "1.0.0",
            "layer": "L1",
            "input_sha256": input_sha256,
            "page_id": {
                "page_0based": page_index,
                "page_1based": page_index + 1,
            },
            "bbox_pdf_pt": rect4([x0, y0, x1, y1]),
            "crop_sha256": None,
            "observation": {
                "text": all_text,
                "character_count": total_chars,
                "math_character_count": total_math,
                "math_character_ratio": round(math_ratio, 4),
                "has_relation": has_relation,
                "has_math_font": has_mfont,
                "has_equation_label": has_label,
                "fonts": all_fonts,
                "line_count": len(cluster),
            },
            "confidence": confidence,
            "dependencies": [],
            "status": "OBSERVED",
        }
        evidence_records.append(sidecar)

    # Sort records vertically by y0
    evidence_records.sort(key=lambda r: (r["bbox_pdf_pt"][1], r["bbox_pdf_pt"][0]))
    return evidence_records
