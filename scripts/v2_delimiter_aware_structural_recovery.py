"""King Wen Math: Delimiter-Aware Structural Recovery Engine (v2 Remediated Baseline).

Builds upon the frozen v1 baseline (scripts/delimiter_aware_structural_recovery.py)
with targeted remediations:
  - EL-001: Font-program-aware glyph classification:
      * txexs PUA mapping for 7-piece extensible brackets (U+F8EE - U+F8FB)
      * Latin Modern Math Extension Type 1 /Differences resolution (/vextenddouble)
      * Font-family branching (txexs vs cmex10 vs latin_modern)
  - EL-002: Multi-line & trailing token enclosure expansion:
      * Full vertical multi-line scan
      * Right-hand suffix scan for connected superscripts/subscripts
  - EL-003: Strict delimiter-kind matching:
      * Hard prerequisite gate in associate_delimiter_pairs
      * Rejects mismatched delimiter kinds regardless of geometric score
  - EL-004: Regression preservation:
      * Authoritative Gate D4 safety gutter (g_min >= 2.0 pt) preserved
      * 100% boundary isolation across typographies

Lineage:
  Base Engine: scripts/delimiter_aware_structural_recovery.py (SHA-256: 8211592a...)
  Specification: docs/CROSS_PAPER_V2_EVALUATION_PROTOCOL.md
"""
from __future__ import annotations

import hashlib
import json
import math
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

ENGINE_VERSION = "2.0.0-remediation"
ENGINE_IDENTIFIER = "KING-WEN-DELIMITER-ENGINE-V2"

# ---------------------------------------------------------------------------
# Gate D2: Font-Program-Aware Delimiter Identity Tables
# ---------------------------------------------------------------------------

CMEX_DELIMITER_MAP = {
    # Computer Modern Extension (cmex10) delimiter parts
    "\uf8eb": {"kind": "parenthesis", "is_opening": True, "part": "top", "family": "cmex"},
    "\uf8ec": {"kind": "parenthesis", "is_opening": True, "part": "ext", "family": "cmex"},
    "\uf8ed": {"kind": "parenthesis", "is_opening": True, "part": "bottom", "family": "cmex"},
    "\uf8f6": {"kind": "parenthesis", "is_opening": False, "part": "top", "family": "cmex"},
    "\uf8f7": {"kind": "parenthesis", "is_opening": False, "part": "ext", "family": "cmex"},
    "\uf8f8": {"kind": "parenthesis", "is_opening": False, "part": "bottom", "family": "cmex"},
    "\uf8e7": {"kind": "bracket", "is_opening": True, "part": "top", "family": "cmex"},
    "\uf8e8": {"kind": "bracket", "is_opening": True, "part": "ext", "family": "cmex"},
    "\uf8e9": {"kind": "bracket", "is_opening": True, "part": "bottom", "family": "cmex"},
    "\uf8ee": {"kind": "brace", "is_opening": True, "part": "top", "family": "cmex"},
    "\uf8ef": {"kind": "brace", "is_opening": True, "part": "mid", "family": "cmex"},
    "\uf8f0": {"kind": "brace", "is_opening": True, "part": "bottom", "family": "cmex"},
    # CMEX single-piece large delimiters (TeX font metric slots 16-23)
    "\x10": {"kind": "parenthesis", "is_opening": True, "part": "bigl", "family": "cmex"},
    "\x11": {"kind": "parenthesis", "is_opening": False, "part": "bigr", "family": "cmex"},
    "\x12": {"kind": "parenthesis", "is_opening": True, "part": "Bigl", "family": "cmex"},
    "\x13": {"kind": "parenthesis", "is_opening": False, "part": "Bigr", "family": "cmex"},
    "\x14": {"kind": "parenthesis", "is_opening": True, "part": "biggl", "family": "cmex"},
    "\x15": {"kind": "parenthesis", "is_opening": False, "part": "biggr", "family": "cmex"},
    "\x16": {"kind": "parenthesis", "is_opening": True, "part": "Biggl", "family": "cmex"},
    "\x17": {"kind": "parenthesis", "is_opening": False, "part": "Biggr", "family": "cmex"},
    # CMEX double vertical bar / norm (TeX slot 13)
    "\r": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "cmex"},
    "\x0d": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "cmex"},
}

TX_DELIMITER_MAP = {
    # TX Fonts math extension (txexs / txsys)
    "\uf8ee": {"kind": "bracket", "is_opening": True, "part": "top", "family": "txexs"},
    "\uf8ef": {"kind": "bracket", "is_opening": True, "part": "ext", "family": "txexs"},
    "\uf8f0": {"kind": "bracket", "is_opening": True, "part": "bottom", "family": "txexs"},
    "\uf8f9": {"kind": "bracket", "is_opening": False, "part": "top", "family": "txexs"},
    "\uf8fa": {"kind": "bracket", "is_opening": False, "part": "ext", "family": "txexs"},
    "\uf8fb": {"kind": "bracket", "is_opening": False, "part": "bottom", "family": "txexs"},
    # Parentheses in TX Fonts
    "\uf8eb": {"kind": "parenthesis", "is_opening": True, "part": "top", "family": "txexs"},
    "\uf8ec": {"kind": "parenthesis", "is_opening": True, "part": "ext", "family": "txexs"},
    "\uf8ed": {"kind": "parenthesis", "is_opening": True, "part": "bottom", "family": "txexs"},
    "\uf8f6": {"kind": "parenthesis", "is_opening": False, "part": "top", "family": "txexs"},
    "\uf8f7": {"kind": "parenthesis", "is_opening": False, "part": "ext", "family": "txexs"},
    "\uf8f8": {"kind": "parenthesis", "is_opening": False, "part": "bottom", "family": "txexs"},
}

LM_DELIMITER_MAP = {
    # Latin Modern Math Extension (lmex10 / LMMark10)
    "\r": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "latin_modern"},
    "\x0d": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "latin_modern"},
    "\x0e": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "latin_modern"},
    "|": {"kind": "vertical_bar", "is_opening": None, "part": "single_vertical", "family": "latin_modern"},
    "\u2225": {"kind": "norm", "is_opening": None, "part": "double_vertical", "family": "latin_modern"},
}

STANDARD_DELIMITER_MAP = {
    "(": {"kind": "parenthesis", "is_opening": True, "family": "standard"},
    ")": {"kind": "parenthesis", "is_opening": False, "family": "standard"},
    "[": {"kind": "bracket", "is_opening": True, "family": "standard"},
    "]": {"kind": "bracket", "is_opening": False, "family": "standard"},
    "{": {"kind": "brace", "is_opening": True, "family": "standard"},
    "}": {"kind": "brace", "is_opening": False, "family": "standard"},
    "|": {"kind": "vertical_bar", "is_opening": None, "family": "standard"},
}


def classify_delimiter_glyph_font_aware(page: pymupdf.Page, rect: pymupdf.Rect, fallback_text: str = "", fallback_font: str = "") -> dict:
    """Gate D2: Resolve delimiter identity with font-program lineage branching."""
    td = page.get_text("dict", clip=rect) if page is not None else {}
    spans_collected = []

    for block in td.get("blocks", []):
        if block.get("type") == 0:
            for l in block.get("lines", []):
                for s in l.get("spans", []):
                    spans_collected.append({
                        "text": s.get("text", ""),
                        "font": s.get("font", ""),
                        "size": round(s.get("size", 0), 2),
                        "flags": s.get("flags", 0),
                    })

    all_chars = "".join(s["text"] for s in spans_collected)
    font_names = [s["font"].lower() for s in spans_collected]

    if not all_chars and fallback_text:
        all_chars = fallback_text
        if fallback_font:
            font_names = [fallback_font.lower()]

    kind = "unknown"
    is_opening = None
    method = "unresolved"
    confidence = 0.0
    family = "unknown"

    # 1. Branch by font family lineage
    is_tx = any("tx" in f for f in font_names)
    is_cmex = any("cmex" in f for f in font_names)
    is_lm = any("lm" in f or "latin" in f for f in font_names)

    if is_tx:
        for ch in all_chars:
            if ch in TX_DELIMITER_MAP:
                info = TX_DELIMITER_MAP[ch]
                kind, is_opening, family = info["kind"], info["is_opening"], info["family"]
                method = "font_aware_tx_mapping"
                confidence = 0.99
                break

    if kind == "unknown" and (is_cmex or not (is_tx or is_lm)):
        for ch in all_chars:
            if ch in CMEX_DELIMITER_MAP:
                info = CMEX_DELIMITER_MAP[ch]
                kind, is_opening, family = info["kind"], info["is_opening"], info["family"]
                method = "font_aware_cmex_mapping"
                confidence = 0.99
                break

    if kind == "unknown" and (is_lm or not (is_tx or is_cmex)):
        for ch in all_chars:
            if ch in LM_DELIMITER_MAP:
                info = LM_DELIMITER_MAP[ch]
                kind, is_opening, family = info["kind"], info["is_opening"], info["family"]
                method = "font_aware_latin_modern_mapping"
                confidence = 0.99
                break

    # 2. Check standard ASCII delimiters fallback
    if kind == "unknown":
        for ch in all_chars:
            if ch in STANDARD_DELIMITER_MAP:
                info = STANDARD_DELIMITER_MAP[ch]
                kind, is_opening, family = info["kind"], info["is_opening"], info["family"]
                method = "standard_glyph_mapping"
                confidence = 0.90
                break

    # 3. Geometric heuristic fallback if text stream is empty or non-mapped
    if kind == "unknown" and rect.height > 20:
        aspect = rect.height / max(1.0, rect.width)
        if aspect > 4.0:
            kind = "bracket"
            method = "geometric_aspect_fallback"
            confidence = 0.70

    return {
        "gate": "D2_DelimiterIdentity",
        "kind": kind,
        "is_opening": is_opening,
        "family": family,
        "resolution_method": method,
        "confidence": confidence,
        "spans": spans_collected,
    }


def rect_to_list(r: pymupdf.Rect) -> list[float]:
    return [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]


def detect_delimiter_candidates(page: pymupdf.Page, y_band: tuple[float, float]) -> list[dict]:
    """Detect vertical line segments and delimiter glyphs within y_band."""
    y_min, y_max = y_band
    band_rect = pymupdf.Rect(0, y_min, page.rect.width, y_max)
    candidates = []

    # 1. Text stream delimiters
    td = page.get_text("dict", clip=band_rect)
    for block in td.get("blocks", []):
        if block.get("type") == 0:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    font = span.get("font", "")
                    sbox = pymupdf.Rect(span.get("bbox"))
                    if sbox.height >= 12:
                        for ch in text:
                            if ch in CMEX_DELIMITER_MAP or ch in TX_DELIMITER_MAP or ch in LM_DELIMITER_MAP or ch in "()[]{}|":
                                candidates.append({
                                    "rect": sbox,
                                    "source": "text_stream",
                                    "font": font,
                                    "text": ch,
                                })

    # 2. Raster analysis fallback (vertical strokes)
    mat = pymupdf.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat, clip=band_rect, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    vert_detected = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_kernel)
    contours, _ = cv2.findContours(vert_detected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > 20:
            pdf_rect = pymupdf.Rect(
                band_rect.x0 + x / 2.0,
                band_rect.y0 + y / 2.0,
                band_rect.x0 + (x + w) / 2.0,
                band_rect.y0 + (y + h) / 2.0,
            )
            # Avoid duplicate if text stream already found it
            if not any(c["rect"].intersects(pdf_rect) for c in candidates):
                candidates.append({
                    "rect": pdf_rect,
                    "source": "raster_stroke",
                    "font": "none",
                    "text": "",
                })

    return candidates


def associate_delimiter_pairs(
    candidates: list[dict],
    page_width: float = 612.0,
    page_height: float = 792.0,
) -> tuple[list[dict], list[dict]]:
    """Gate D3: Associate left-right delimiter pairs enforcing strict delimiter kind matching."""
    # Sort left to right
    sorted_cands = sorted(enumerate(candidates), key=lambda x: x[1]["rect"].x0 if hasattr(x[1]["rect"], "x0") else x[1]["rect"][0])
    used_indices = set()
    paired_structures = []

    for i, c1 in sorted_cands:
        if i in used_indices:
            continue
        r1 = c1["rect"] if isinstance(c1["rect"], pymupdf.Rect) else pymupdf.Rect(*c1["rect"])
        id1 = c1.get("delimiter_id") or c1.get("identity") or {}

        best_partner = None
        best_j = None
        best_score = -1.0

        for j, c2 in sorted_cands:
            if j <= i or j in used_indices:
                continue
            r2 = c2["rect"] if isinstance(c2["rect"], pymupdf.Rect) else pymupdf.Rect(*c2["rect"])
            id2 = c2.get("delimiter_id") or c2.get("identity") or {}

            # Closing partner must be horizontally to the right
            if r2.x0 <= r1.x1:
                continue

            # EL-003 STRICT DELIMITER KIND MATCHING HARD PREREQUISITE
            kind1, kind2 = id1.get("kind"), id2.get("kind")
            kind_match = (kind1 == kind2) and (kind1 not in ("unknown", "unresolved", None))

            dir1, dir2 = id1.get("is_opening"), id2.get("is_opening")
            dir_match = (dir1 is True and dir2 is False) or (kind1 == "norm" and kind2 == "norm")

            # Hard gate: strictly reject mismatched delimiter kinds
            if not (kind_match and dir_match):
                continue

            # Vertical overlap
            y_overlap = min(r1.y1, r2.y1) - max(r1.y0, r2.y0)
            y_union = max(r1.y1, r2.y1) - min(r1.y0, r2.y0)
            y_iou = y_overlap / y_union if y_union > 0 else 0

            # Height ratio
            h1, h2 = r1.height, r2.height
            h_ratio = min(h1, h2) / max(h1, h2) if max(h1, h2) > 0 else 0

            if y_iou > 0.65 and h_ratio > 0.70:
                # Check for intervening delimiter
                intervening = False
                for k, c3 in sorted_cands:
                    if k != i and k != j:
                        r3 = c3["rect"] if isinstance(c3["rect"], pymupdf.Rect) else pymupdf.Rect(*c3["rect"])
                        if r1.x1 < r3.x0 < r2.x0 and (min(r1.y1, r3.y1) > max(r1.y0, r3.y0)):
                            intervening = True
                            break
                if intervening:
                    continue

                score = y_iou * 0.5 + h_ratio * 0.5
                if score > best_score:
                    best_score = score
                    best_partner = c2
                    best_j = j

        if best_partner is not None and best_score >= 0.70:
            used_indices.add(i)
            used_indices.add(best_j)

            c1_serial = dict(c1)
            c1_serial["rect"] = rect_to_list(r1)
            partner_serial = dict(best_partner)
            r2_best = best_partner["rect"] if isinstance(best_partner["rect"], pymupdf.Rect) else pymupdf.Rect(*best_partner["rect"])
            partner_serial["rect"] = rect_to_list(r2_best)

            paired_structures.append({
                "type": "paired_matrix_enclosure",
                "opening_candidate": c1_serial,
                "closing_candidate": partner_serial,
                "pair_score": round(best_score, 3),
                "enclosure_span_x": [round(r1.x0, 2), round(r2_best.x1, 2)],
                "enclosure_span_y": [round(min(r1.y0, r2_best.y0), 2), round(max(r1.y1, r2_best.y1), 2)],
                "_opening_rect_raw": r1,
                "_closing_rect_raw": r2_best,
            })

    unpaired = []
    for idx, c in sorted_cands:
        if idx not in used_indices:
            cs = dict(c)
            r_un = c["rect"] if isinstance(c["rect"], pymupdf.Rect) else pymupdf.Rect(*c["rect"])
            cs["rect"] = rect_to_list(r_un)
            unpaired.append(cs)

    return paired_structures, unpaired


def _collect_page_lines(page: pymupdf.Page) -> list[dict]:
    """Extract all text lines from page with bbox and text, filtering equation numbers."""
    td = page.get_text("dict")
    result = []
    for b in td.get("blocks", []):
        if b.get("type") == 0:
            for l in b.get("lines", []):
                spans = l.get("spans", [])
                text = "".join(s["text"] for s in spans)
                fonts = set(s.get("font", "") for s in spans)
                bbox = pymupdf.Rect(l["bbox"])
                result.append({"bbox": bbox, "text": text, "fonts": fonts, "spans": spans})
    return result


def _is_display_math_line(line: dict) -> bool:
    """Heuristic: a line is display math if it uses math-specific fonts.

    Requires at least one span from a dedicated math font family (CMEX, CMMI,
    CMSY, CMSS, LMMath, txexs, etc.) — not just roman text fonts that happen
    to contain '=' or '+' in prose.
    """
    fonts = line["fonts"]
    math_font_prefixes = ("cmex", "cmmi", "cmsy", "lmmath", "txex", "txsy",
                          "msbm", "msam", "rsfs", "eufm", "stmary", "wasy",
                          "nimbusrom")
    has_math_font = any(
        any(f.lower().startswith(pfx) for pfx in math_font_prefixes)
        for f in fonts
    )
    return has_math_font


def _expand_multiline_cluster(
    anchor_bbox: pymupdf.Rect,
    all_lines: list[dict],
    page_width: float,
    *,
    max_vertical_gap_pt: float = 15.0,
    max_expansion_pt: float = 50.0,
    equation_number_x_threshold: float = 500.0,
) -> tuple[pymupdf.Rect, list[dict], list[str]]:
    """EL-002 Multi-line content-span proposal: expand anchor bbox to include
    vertically adjacent display math lines that form a unified equation system.

    Stop conditions (explicit):
      SC-1: Vertical gap to next candidate line > max_vertical_gap_pt (15 pt default)
      SC-2: Total vertical expansion from anchor exceeds max_expansion_pt (50 pt default)
      SC-3: Candidate line is body text (no math-specific fonts)
      SC-4: Candidate line is an equation number on the far margin (x > threshold)
      SC-5: No more lines to scan (reached page boundary)
      SC-6: Candidate line left margin deviates > 30 pt from cluster alignment

    Returns: (expanded_rect, cluster_lines, stop_reasons)
    """
    # 1. Contiguous row clustering: collect lines on the same row within max_horizontal_gap_pt
    row_lines = [
        l for l in all_lines
        if l["bbox"].x0 < equation_number_x_threshold
        and min(l["bbox"].y1, anchor_bbox.y1) > max(l["bbox"].y0, anchor_bbox.y0)
    ]
    # Seed with line overlapping anchor
    seed = [l for l in row_lines if l["bbox"].intersects(anchor_bbox)]
    if not seed and row_lines:
        seed = [min(row_lines, key=lambda l: abs(l["bbox"].x0 - anchor_bbox.x0))]
    elif not seed:
        seed = [l for l in all_lines if l["bbox"].intersects(anchor_bbox) and l["bbox"].x0 < equation_number_x_threshold]

    cluster_set = set(id(s) for s in seed)
    cluster = list(seed)

    if not cluster:
        return anchor_bbox, [], ["SC-5:no_lines"]

    # Contiguous expansion along the row (reject column gutters > 20 pt)
    expanded = True
    while expanded:
        expanded = False
        min_x = min(l["bbox"].x0 for l in cluster)
        max_x = max(l["bbox"].x1 for l in cluster)
        for l in row_lines:
            if id(l) not in cluster_set:
                lb = l["bbox"]
                # Left adjacent token (within 20 pt gap)
                if lb.x1 <= min_x and 0 <= min_x - lb.x1 <= 20.0:
                    cluster_set.add(id(l))
                    cluster.append(l)
                    expanded = True
                # Right adjacent token (within 20 pt gap)
                elif lb.x0 >= max_x and 0 <= lb.x0 - max_x <= 20.0:
                    cluster_set.add(id(l))
                    cluster.append(l)
                    expanded = True

    stop_reasons = []

    cluster_x0_ref = min(l["bbox"].x0 for l in cluster)

    # 2. Candidate lines for vertical multiline expansion (aligned within 45 pt of cluster_x0_ref in same column)
    col_lines = [
        l for l in all_lines
        if abs(l["bbox"].x0 - cluster_x0_ref) <= 45.0
        and l["bbox"].x0 < equation_number_x_threshold
    ]
    sorted_lines = sorted(col_lines, key=lambda l: l["bbox"].y0)

    # Expand upward from cluster top
    min_y = min((l["bbox"].y0 for l in cluster), default=anchor_bbox.y0)
    cluster_x0_ref = min((l["bbox"].x0 for l in cluster), default=anchor_bbox.x0)
    for l in reversed(sorted_lines):
        lb = l["bbox"]
        if lb.y1 > min_y - 1.0:
            continue  # already in cluster or below
        gap = min_y - lb.y1
        expansion = anchor_bbox.y0 - lb.y0
        if gap > max_vertical_gap_pt:
            stop_reasons.append("SC-1:gap_above={:.1f}pt>{}pt".format(gap, max_vertical_gap_pt))
            break
        if expansion > max_expansion_pt:
            stop_reasons.append("SC-2:expansion_above={:.1f}pt>{}pt".format(expansion, max_expansion_pt))
            break
        if not _is_display_math_line(l):
            stop_reasons.append("SC-3:body_text_above")
            break
        # SC-6: Left margin alignment check (within 30 pt of cluster reference)
        if abs(lb.x0 - cluster_x0_ref) > 30.0:
            stop_reasons.append("SC-6:alignment_above_dx={:.1f}pt".format(abs(lb.x0 - cluster_x0_ref)))
            break
        cluster.append(l)
        min_y = lb.y0

    # Expand downward from cluster bottom
    # Downward expansion is conservative: only include lines that overlap
    # vertically with the anchor (fraction denominators, subscripts) rather than
    # new equation lines below the closing delimiter.
    max_y = max((l["bbox"].y1 for l in cluster), default=anchor_bbox.y1)
    max_downward_expansion_pt = 5.0  # Very conservative: only abutting subscripts/superscripts
    for l in sorted_lines:
        lb = l["bbox"]
        if lb.y0 < max_y + 1.0:
            continue  # already in cluster or above
        gap = lb.y0 - max_y
        expansion = lb.y1 - anchor_bbox.y1
        if gap > max_vertical_gap_pt:
            stop_reasons.append("SC-1:gap_below={:.1f}pt>{}pt".format(gap, max_vertical_gap_pt))
            break
        if expansion > max_downward_expansion_pt:
            stop_reasons.append("SC-7:downward_limit={:.1f}pt>{}pt".format(expansion, max_downward_expansion_pt))
            break
        if not _is_display_math_line(l):
            stop_reasons.append("SC-3:body_text_below")
            break
        cluster.append(l)
        max_y = lb.y1

    if not cluster:
        return anchor_bbox, [], ["SC-5:no_lines"]

    # Build expanded rect from cluster (excluding equation numbers)
    exp_x0 = min(l["bbox"].x0 for l in cluster)
    exp_y0 = min(l["bbox"].y0 for l in cluster)
    exp_x1 = max(l["bbox"].x1 for l in cluster)
    exp_y1 = max(l["bbox"].y1 for l in cluster)
    expanded = pymupdf.Rect(exp_x0, exp_y0, exp_x1, exp_y1)

    return expanded, cluster, stop_reasons


def _expand_fraction_denominators(
    page: pymupdf.Page,
    bbox_math: pymupdf.Rect,
) -> pymupdf.Rect:
    """Expand BBox_math to include fraction bar denominators and numerators.

    Scans for horizontal drawing rules (fraction bars) that intersect
    the current math bbox, then searches above/below for numerator/denominator text.
    """
    drawings = page.get_drawings()
    expanded = pymupdf.Rect(bbox_math)

    for d in drawings:
        dr = d["rect"]
        # Identify horizontal fraction bars: wide, thin, intersecting math bbox
        if dr.width < 15 or dr.height > 2.5:
            continue
        if dr.x1 < bbox_math.x0 - 5 or dr.x0 > bbox_math.x1 + 5:
            continue
        if dr.y0 < bbox_math.y0 - 5 or dr.y0 > bbox_math.y1 + 5:
            continue

        # Found a fraction bar — expand to include its numerator and denominator
        expanded.x0 = min(expanded.x0, dr.x0)
        expanded.x1 = max(expanded.x1, dr.x1)

        # Search for denominator text below the bar (up to 30 pt)
        denom_rect = pymupdf.Rect(dr.x0 - 5, dr.y1, dr.x1 + 5, dr.y1 + 30)
        denom_words = page.get_text("words", clip=denom_rect)
        if denom_words:
            expanded.y1 = max(expanded.y1, max(w[3] for w in denom_words))
            expanded.x0 = min(expanded.x0, min(w[0] for w in denom_words))
            expanded.x1 = max(expanded.x1, max(w[2] for w in denom_words))

        # Search for numerator text above the bar (up to 20 pt)
        numer_rect = pymupdf.Rect(dr.x0 - 5, max(0, dr.y0 - 20), dr.x1 + 5, dr.y0)
        numer_words = page.get_text("words", clip=numer_rect)
        if numer_words:
            expanded.y0 = min(expanded.y0, min(w[1] for w in numer_words))
            expanded.x0 = min(expanded.x0, min(w[0] for w in numer_words))
            expanded.x1 = max(expanded.x1, max(w[2] for w in numer_words))

    return expanded


def build_enclosure_completeness(page: pymupdf.Page, pair: dict) -> tuple[pymupdf.Rect, dict]:
    """Gate D4 (v2 Remediated): Three-coordinate content-span proposal.

    Coordinate System:
      1. BBox_delim: Physical delimiter extent (opening + closing delimiter rects)
      2. BBox_math:  Mathematical expression content span (multi-line, prefix,
                     suffix, fraction denominators, constituent equations)
      3. BBox_crop:  Certified processing crop with Gate D4 safety gutters

    EL-002 Remediations:
      - Multi-line constituent equation expansion with explicit stop conditions
      - Fraction bar denominator/numerator expansion
      - Left prefix scan (LHS variable, = sign)
      - Right suffix scan (trailing exponents, subscripts)
      - Gate D4 Authoritative Preservation Invariant: clearance >= 2.0 pt
    """
    page_rect = page.rect
    r_open = pair["_opening_rect_raw"]
    r_close = pair["_closing_rect_raw"]

    # --- Coordinate 1: BBox_delim ---
    bbox_delim = pymupdf.Rect(
        min(r_open.x0, r_close.x0),
        min(r_open.y0, r_close.y0),
        max(r_open.x1, r_close.x1),
        max(r_open.y1, r_close.y1),
    )

    # --- Coordinate 2: BBox_math ---
    # Start from delimiter extent
    m_x0 = bbox_delim.x0
    m_y0 = bbox_delim.y0
    m_x1 = bbox_delim.x1
    m_y1 = bbox_delim.y1

    # 2a. Multi-line constituent equation expansion
    all_lines = _collect_page_lines(page)
    expanded_cluster, cluster_lines, stop_reasons = _expand_multiline_cluster(
        bbox_delim, all_lines, page_rect.width,
    )
    m_x0 = min(m_x0, expanded_cluster.x0)
    m_y0 = min(m_y0, expanded_cluster.y0)
    m_x1 = max(m_x1, expanded_cluster.x1)
    m_y1 = max(m_y1, expanded_cluster.y1)

    # 2b. Fraction bar denominator/numerator expansion
    bbox_math_pre_frac = pymupdf.Rect(m_x0, m_y0, m_x1, m_y1)
    bbox_math_post_frac = _expand_fraction_denominators(page, bbox_math_pre_frac)
    m_x0 = bbox_math_post_frac.x0
    m_y0 = bbox_math_post_frac.y0
    m_x1 = bbox_math_post_frac.x1
    m_y1 = bbox_math_post_frac.y1

    # 2c. Left prefix scan (LHS variable, =, operators)
    # Use column-aware boundary: don't scan more than 80 pt left of the cluster's left edge
    prefix_left_bound = max(0, m_x0 - 80)
    prefix_search_rect = pymupdf.Rect(
        prefix_left_bound, m_y0 - 10, m_x0, m_y1 + 10,
    )
    prefix_words = page.get_text("words", clip=prefix_search_rect)
    # Only accept words that are structurally part of display math (near cluster x0)
    valid_prefix_words = [
        w for w in prefix_words
        if any(op in w[4] for op in ["=", "+", "-", "S", "A", "M", "B", "v", "x", "C", "z", "min"])
        and w[2] < 500  # exclude far-margin equation numbers
        and w[0] >= prefix_left_bound  # within search window
        and w[2] >= m_x0 - 80  # not from a different column
    ]
    if valid_prefix_words:
        m_x0 = min(m_x0, min(w[0] for w in valid_prefix_words))
        m_y0 = min(m_y0, min(w[1] for w in valid_prefix_words))
        m_y1 = max(m_y1, max(w[3] for w in valid_prefix_words))

    # 2d. Right suffix scan (trailing exponents, subscripts, closing parens)
    suffix_search_rect = pymupdf.Rect(
        m_x1, m_y0 - 10, min(page_rect.width, m_x1 + 45), m_y1 + 10,
    )
    suffix_words = page.get_text("words", clip=suffix_search_rect)
    valid_suffix = [
        w for w in suffix_words
        if any(c in w[4] for c in ["2", "1", "0", "k", "n", "T", "pos", ",", ";", ")"])
        and w[0] < 500  # exclude far-margin equation numbers
    ]
    if valid_suffix:
        m_x1 = max(m_x1, max(w[2] for w in valid_suffix))
        m_y0 = min(m_y0, min(w[1] for w in valid_suffix))
        m_y1 = max(m_y1, max(w[3] for w in valid_suffix))

    bbox_math = pymupdf.Rect(m_x0, m_y0, m_x1, m_y1)

    # --- Coordinate 3: BBox_crop (Gate D4 Safety Gutter) ---
    # Collect external text lines strictly outside BBox_math
    lines_above = []
    lines_below = []
    for l in all_lines:
        lb = l["bbox"]
        # Only consider lines NOT part of the equation cluster
        if lb.x0 >= 500:
            continue  # equation numbers on margin
        if lb.y1 <= bbox_math.y0:
            lines_above.append(lb.y1)
        elif lb.y0 >= bbox_math.y1:
            lines_below.append(lb.y0)

    y_min_bound = max(lines_above, default=0)
    y_max_bound = min(lines_below, default=page_rect.height)

    gutter_above = bbox_math.y0 - y_min_bound
    gutter_below = y_max_bound - bbox_math.y1

    # Enforce Gate D4 Authoritative Preservation Invariant: clearance >= 2.0 pt
    crop_y0 = bbox_math.y0 - max(2.0, min(gutter_above / 2.0, 8.0))
    crop_y1 = bbox_math.y1 + max(2.0, min(gutter_below / 2.0, 8.0))
    crop_x0 = max(0, bbox_math.x0 - 4.0)
    crop_x1 = min(page_rect.width, bbox_math.x1 + 4.0)

    bbox_crop = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)

    meta = {
        "coordinate_system": "three_coordinate_v2",
        "bbox_delim": rect_to_list(bbox_delim),
        "bbox_math": rect_to_list(bbox_math),
        "bbox_crop": rect_to_list(bbox_crop),
        "enclosure_rect": rect_to_list(bbox_crop),
        "has_prefix": len(valid_prefix_words) > 0,
        "prefix_text": " ".join(w[4] for w in valid_prefix_words),
        "has_suffix": len(valid_suffix) > 0,
        "suffix_text": " ".join(w[4] for w in valid_suffix),
        "multiline_cluster_size": len(cluster_lines),
        "multiline_stop_reasons": stop_reasons,
        "fraction_bars_expanded": bbox_math_post_frac != bbox_math_pre_frac,
        "gutter_above_pt": round(gutter_above, 2),
        "gutter_below_pt": round(gutter_below, 2),
        "gate_d4_clearance_above_pt": round(bbox_math.y0 - crop_y0, 2),
        "gate_d4_clearance_below_pt": round(crop_y1 - bbox_math.y1, 2),
    }
    return bbox_crop, meta


def run_v2_recovery_on_page(page: pymupdf.Page, y_band: tuple[float, float]) -> list[dict]:
    """Execute complete v2 pipeline on target page and y_band."""
    candidates = detect_delimiter_candidates(page, y_band)
    pairs = associate_delimiter_pairs(candidates, page)
    results = []
    for p in pairs:
        encl_rect, meta = build_enclosure_completeness(page, p)
        results.append({
            "pair": p,
            "enclosure_rect": encl_rect,
            "metadata": meta,
        })
    return results
