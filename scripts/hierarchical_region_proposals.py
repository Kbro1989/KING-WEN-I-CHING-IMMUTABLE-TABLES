#!/usr/bin/env python3
"""
Hierarchical Region Proposals — Level 1 through Level 5
1505.05770 · Variational Inference with Normalizing Flows

Implementation Version: 2.0_hierarchical (Milestone: Layer A/B Representation Recovery)

Hierarchy:
  Level 1: Glyph observations (rawdict characters with font-aware classification)
  Level 2: Text spans (consecutive glyphs sharing font, size, and baseline)
  Level 3: Line groups (single horizontal rows of spans aligned on baseline |Δy| ≤ 3.0 pt)
  Level 4: Equation-region proposals (individual equation line proposals)
  Level 5: Multi-line mathematical structures (continuation/aligned equations)

Key Invariants:
  - Font-aware glyph classification (CMMI, CMSY, CMEX, MSBM recognised as mathematical)
  - CMEX10 'Z' recognised as integral operator
  - Contextual citation discrimination (years, semicolon citation patterns flagged)
  - Parent clusters do NOT disqualify valid child regions
  - No gold coordinates or equation identifiers used during proposal generation
  - All file writes use encoding="utf-8"

Outputs:
  DATASETS/structural_preservation/1505.05770_hierarchical_proposals_p002.json
  DATASETS/structural_preservation/1505.05770_hierarchical_proposals_p003.json
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
import io
from pathlib import Path

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from font_aware_math_classifier import (
    classify_glyph,
    discriminate_citation,
    MATH_RELATIONS,
    MATH_OPERATORS,
    GREEK,
    MATH_FUNCTION_NAMES
)

try:
    import fitz
except ImportError:
    import pymupdf as fitz

PDF_PATH = Path(
    r"C:\Users\krist\Desktop\zotero\learning-corpus\efficient-inference-quantization"
    r"\1505.05770_Variational Inference with Normalizing Flows.pdf"
)
EXPECTED_PDF_SHA256 = "776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a"

OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"

# Parameters for Hierarchical Clustering (Fixed, not tuned against gold)
BASELINE_TOLERANCE_PT = 3.0      # max |Δy| of span centres for same baseline
LINE_HORIZONTAL_GAP_PT = 14.0    # max horizontal gap between adjacent spans on same line
MULTILINE_MAX_GAP_PT = 16.0      # max vertical gap between lines of a multiline equation
EQ_NUMBER_RE = re.compile(r"^\s*\(?\d+\)?\s*$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def merge_bboxes(bboxes: list[list[float]]) -> list[float]:
    x0 = min(b[0] for b in bboxes)
    y0 = min(b[1] for b in bboxes)
    x1 = max(b[2] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    return [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)]


def extract_hierarchical_observations(page, page_index_0based: int):
    """
    Extract Level 1 (glyphs) and Level 2 (spans) directly from MuPDF rawdict,
    applying font-aware classification.
    """
    raw = page.get_text("rawdict")
    level1_glyphs = []
    level2_spans = []

    for block_i, block in enumerate(raw.get("blocks", [])):
        if "lines" not in block:
            continue
        for line_i, line in enumerate(block["lines"]):
            for span_i, span in enumerate(line.get("spans", [])):
                font = span.get("font", "")
                size = round(float(span.get("size", 10.0)), 3)
                span_bbox = [round(float(v), 3) for v in span.get("bbox", (0, 0, 0, 0))]
                raw_chars = span.get("chars", [])

                span_glyphs = []
                math_glyph_count = 0
                has_font_operator = False
                operator_roles = []

                for char_i, item in enumerate(raw_chars):
                    c = item.get("c", "")
                    c_bbox = [round(float(v), 3) for v in item.get("bbox", (0, 0, 0, 0))]
                    if not c.strip() and not c_bbox:
                        continue

                    # Level 1 classification
                    c_class = classify_glyph(c, font, size)
                    if c_class["is_math"]:
                        math_glyph_count += 1
                    if "operator_role" in c_class:
                        has_font_operator = True
                        operator_roles.append(c_class["operator_role"])

                    glyph_rec = {
                        "glyph_index": len(level1_glyphs),
                        "char": c,
                        "font": font,
                        "font_size_pt": size,
                        "bbox_pdf_pt": c_bbox,
                        "classification": c_class,
                    }
                    level1_glyphs.append(glyph_rec)
                    span_glyphs.append(glyph_rec)

                span_text = "".join(g["char"] for g in span_glyphs)
                total_glyphs = len(span_glyphs)
                math_ratio = round(math_glyph_count / max(total_glyphs, 1), 4)

                # Check for math function names in text (log, sin, exp, diag, etc.)
                words = span_text.lower().split()
                has_math_func = any(w in MATH_FUNCTION_NAMES for w in words)

                span_rec = {
                    "span_id": len(level2_spans),
                    "block_index": block_i,
                    "line_index": line_i,
                    "span_index_in_line": span_i,
                    "text": span_text,
                    "font": font,
                    "font_size_pt": size,
                    "bbox_pdf_pt": span_bbox,
                    "total_glyph_count": total_glyphs,
                    "math_glyph_count": math_glyph_count,
                    "math_glyph_ratio": math_ratio,
                    "has_font_operator": has_font_operator,
                    "operator_roles": operator_roles,
                    "has_math_function": has_math_func,
                    "glyph_indices": [g["glyph_index"] for g in span_glyphs],
                    "centre_y": round((span_bbox[1] + span_bbox[3]) / 2, 3),
                    "centre_x": round((span_bbox[0] + span_bbox[2]) / 2, 3),
                }
                level2_spans.append(span_rec)

    return level1_glyphs, level2_spans


def build_level3_line_groups(spans: list[dict], page_width_pt: float) -> list[dict]:
    """
    Group spans into Level 3 Line Groups (single baseline rows).
    Spans are on the same baseline if |Δy_centre| ≤ BASELINE_TOLERANCE_PT,
    and merged horizontally if gap ≤ LINE_HORIZONTAL_GAP_PT.
    """
    n = len(spans)
    if n == 0:
        return []

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        si = spans[i]
        for j in range(i + 1, n):
            sj = spans[j]
            if abs(si["centre_y"] - sj["centre_y"]) > BASELINE_TOLERANCE_PT:
                continue
            # Horizontal gap
            gap = max(0.0, max(si["bbox_pdf_pt"][0] - sj["bbox_pdf_pt"][2],
                               sj["bbox_pdf_pt"][0] - si["bbox_pdf_pt"][2]))
            if gap <= LINE_HORIZONTAL_GAP_PT:
                union(i, j)

    groups_map: dict[int, list[int]] = {}
    for i in range(n):
        r = find(i)
        groups_map.setdefault(r, []).append(i)

    line_groups = []
    for root, members in groups_map.items():
        m_spans = [spans[m] for m in members]
        # Sort left to right
        m_spans.sort(key=lambda s: s["bbox_pdf_pt"][0])

        merged_bbox = merge_bboxes([s["bbox_pdf_pt"] for s in m_spans])
        combined_text = " ".join(s["text"] for s in m_spans).strip()
        total_glyphs = sum(s["total_glyph_count"] for s in m_spans)
        total_math_glyphs = sum(s["math_glyph_count"] for s in m_spans)
        math_ratio = round(total_math_glyphs / max(total_glyphs, 1), 4)

        has_math_rel = any(r in combined_text for r in "=≠<≤>≥≈∼≡⇔⇒→↦")
        has_math_op = any(op in combined_text for op in "∫∬∑∏√∇∂±∓×÷") or any(s["has_font_operator"] for s in m_spans)
        has_greek = any(g in combined_text for g in GREEK)
        has_math_func = any(s["has_math_function"] for s in m_spans)

        # Citation discrimination
        cit_eval = discriminate_citation(combined_text)

        # Check equation number at line end
        last_span = m_spans[-1]
        has_eq_num = (
            bool(EQ_NUMBER_RE.match(last_span["text"].strip()))
            and last_span["bbox_pdf_pt"][2] > (page_width_pt - 80.0)
        )

        # Equation line qualification:
        # 1. Has genuine math relations/operators/Greek AND not a citation
        # 2. Or high math glyph ratio (>= 0.35) AND not a citation
        is_equation_line = (
            (has_math_rel or has_math_op or has_greek or has_math_func or math_ratio >= 0.35)
            and not cit_eval["is_citation_candidate"]
            and total_glyphs >= 3
        )

        line_groups.append({
            "line_group_id": len(line_groups),
            "merged_bbox": merged_bbox,
            "text": combined_text,
            "span_count": len(m_spans),
            "total_glyph_count": total_glyphs,
            "math_glyph_count": total_math_glyphs,
            "math_glyph_ratio": math_ratio,
            "has_math_relation": has_math_rel,
            "has_math_operator": has_math_op,
            "has_greek": has_greek,
            "has_math_function": has_math_func,
            "has_equation_number": has_eq_num,
            "citation_evaluation": cit_eval,
            "is_equation_line_candidate": is_equation_line,
            "member_span_ids": [s["span_id"] for s in m_spans],
            "centre_y": round((merged_bbox[1] + merged_bbox[3]) / 2, 3),
        })

    # Sort lines vertically
    line_groups.sort(key=lambda lg: lg["merged_bbox"][1])
    for idx, lg in enumerate(line_groups):
        lg["line_group_id"] = idx
    return line_groups


def build_level4_level5_proposals(line_groups: list[dict], page_width_pt: float) -> list[dict]:
    """
    Build Level 4 (Single-Line Equation Proposals) and Level 5 (Multi-Line Equation Structures).
    Key contract: Level 4 proposals are ALWAYS preserved and never deleted by Level 5 merging!
    """
    proposals = []

    # 1. Every qualified Level 3 line group is emitted as a Level 4 Equation Region Proposal
    eq_lines = [lg for lg in line_groups if lg["is_equation_line_candidate"]]

    for lg in eq_lines:
        reasons = []
        if lg["has_math_relation"]:
            reasons.append("contains_mathematical_relation")
        if lg["has_math_operator"]:
            reasons.append("contains_mathematical_operator")
        if lg["has_greek"]:
            reasons.append("contains_greek_symbols")
        if lg["has_math_function"]:
            reasons.append("contains_math_named_function")
        if lg["has_equation_number"]:
            reasons.append("has_adjacent_equation_number")
        if lg["math_glyph_ratio"] >= 0.35:
            reasons.append(f"math_glyph_ratio={lg['math_glyph_ratio']:.2f}")

        proposals.append({
            "proposal_id": f"L4_line_{lg['line_group_id']:03d}",
            "hierarchy_level": 4,
            "proposal_type": "single_line_equation",
            "merged_bbox": lg["merged_bbox"],
            "text": lg["text"],
            "line_group_ids": [lg["line_group_id"]],
            "span_count": lg["span_count"],
            "total_glyph_count": lg["total_glyph_count"],
            "math_glyph_ratio": lg["math_glyph_ratio"],
            "candidate_reasons": reasons,
            "has_equation_number": lg["has_equation_number"],
            "is_citation_filtered": False,
        })

    # 2. Level 5: Multiline clustering over consecutive Level 4 equation lines
    # Only merge if:
    #   - Vertical gap <= MULTILINE_MAX_GAP_PT
    #   - Significant horizontal overlap
    #   - Total lines <= 3 (avoid paragraph runaway)
    #   - Does not bridge distinct equation numbers
    for i in range(len(eq_lines)):
        l1 = eq_lines[i]
        for j in range(i + 1, min(i + 3, len(eq_lines))):
            l2 = eq_lines[j]
            # Vertical gap
            v_gap = l2["merged_bbox"][1] - l1["merged_bbox"][3]
            if v_gap < -2.0 or v_gap > MULTILINE_MAX_GAP_PT:
                continue
            # Horizontal overlap
            h_overlap = max(0.0, min(l1["merged_bbox"][2], l2["merged_bbox"][2]) -
                                  max(l1["merged_bbox"][0], l2["merged_bbox"][0]))
            min_width = min(l1["merged_bbox"][2] - l1["merged_bbox"][0],
                            l2["merged_bbox"][2] - l2["merged_bbox"][0])
            if min_width <= 0 or (h_overlap / min_width) < 0.30:
                continue

            # If both lines have distinct equation numbers, do NOT merge
            if l1["has_equation_number"] and l2["has_equation_number"]:
                continue

            merged_box = merge_bboxes([l1["merged_bbox"], l2["merged_bbox"]])
            proposals.append({
                "proposal_id": f"L5_multiline_{l1['line_group_id']}_{l2['line_group_id']}",
                "hierarchy_level": 5,
                "proposal_type": "multiline_equation_structure",
                "merged_bbox": merged_box,
                "text": f"{l1['text']}  ///  {l2['text']}",
                "line_group_ids": [l1["line_group_id"], l2["line_group_id"]],
                "span_count": l1["span_count"] + l2["span_count"],
                "total_glyph_count": l1["total_glyph_count"] + l2["total_glyph_count"],
                "math_glyph_ratio": round((l1["math_glyph_count"] + l2["math_glyph_count"]) /
                                          max(l1["total_glyph_count"] + l2["total_glyph_count"], 1), 4),
                "candidate_reasons": ["multiline_continuity", "shared_alignment"],
                "has_equation_number": l1["has_equation_number"] or l2["has_equation_number"],
                "is_citation_filtered": False,
            })

    return proposals


def run_page(doc, page_0based: int):
    page_1based = page_0based + 1
    page = doc[page_0based]
    page_width_pt = page.rect.width

    # Level 1 & Level 2
    glyphs, spans = extract_hierarchical_observations(page, page_0based)
    # Level 3
    line_groups = build_level3_line_groups(spans, page_width_pt)
    # Level 4 & Level 5
    proposals = build_level4_level5_proposals(line_groups, page_width_pt)

    l4_count = sum(1 for p in proposals if p["hierarchy_level"] == 4)
    l5_count = sum(1 for p in proposals if p["hierarchy_level"] == 5)
    cit_lines = sum(1 for lg in line_groups if lg["citation_evaluation"]["is_citation_candidate"])

    print(
        f"Page {page_1based}: {len(glyphs)} glyphs, {len(spans)} spans, "
        f"{len(line_groups)} line groups ({cit_lines} citations discriminated), "
        f"{l4_count} Level 4 proposals, {l5_count} Level 5 proposals",
        flush=True
    )

    return {
        "schema_version": "2.0_hierarchical",
        "document_id": "1505.05770",
        "source_pdf_sha256": EXPECTED_PDF_SHA256,
        "page_number_1_based": page_1based,
        "page_index_0_based": page_0based,
        "page_size_pdf_pt": [round(page.rect.width, 3), round(page.rect.height, 3)],
        "coordinate_space": "mupdf_page_points",
        "hierarchy_summary": {
            "level1_glyph_count": len(glyphs),
            "level2_span_count": len(spans),
            "level3_line_group_count": len(line_groups),
            "level3_citation_lines_discriminated": cit_lines,
            "level4_single_line_proposals": l4_count,
            "level5_multiline_proposals": l5_count,
            "total_equation_proposals": len(proposals),
        },
        "level4_level5_proposals": proposals,
        "level3_line_groups": line_groups,
    }


def main():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    if not PDF_PATH.is_file():
        sys.exit(f"[ERROR] PDF not found: {PDF_PATH}")

    actual_pdf_sha = sha256_file(PDF_PATH)
    if actual_pdf_sha != EXPECTED_PDF_SHA256:
        sys.exit(f"[ERROR] PDF SHA-256 mismatch: {actual_pdf_sha}")

    doc = fitz.open(str(PDF_PATH))
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    for page_0based in [1, 2]:  # Pages 2 and 3 (0-based 1 and 2)
        page_1based = page_0based + 1
        res = run_page(doc, page_0based)
        out_file = OUT_ROOT / f"1505.05770_hierarchical_proposals_p{page_1based:03d}.json"
        out_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved -> {out_file}", flush=True)

    doc.close()
    print("\n[hierarchical_proposals] Hierarchical generation complete.", flush=True)


if __name__ == "__main__":
    main()

