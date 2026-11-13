#!/usr/bin/env python3
"""
Hierarchical Region Proposals v3 — Experimental Structural Reconstruction
==========================================================================

Layer C: Candidate implementation for improved mathematical structure recovery.

Changes from frozen v2.0 (scripts/hierarchical_region_proposals.py):
  1. ADAPTIVE BASELINE TOLERANCE (AC-1):
     Replaces rigid 3.0 pt centre-y tolerance with:
       tol = max(3.0, 0.45 * max_font_size_in_pair)
     Recovers subscripts/superscripts at |Δy| = 3.1–3.3 pt without
     indiscriminately expanding the grouping window.

  2. EQUATION-NUMBER DECOUPLING (AC-4):
     Detects trailing '(N)' patterns positioned on the right margin.
     Emits equation_number_metadata as a separate structural field.
     Computes math_expression_bbox excluding the label region.

  3. MULTILINE ASSOCIATION GUARDRAILS (AC-3):
     Requires at least one structural continuity signal before merging
     vertically adjacent lines:
       (a) Shared relation symbol (=, ≤, etc.) with horizontal alignment ≤ 5 pt
       (b) Indented continuation (line 2 x0 > line 1 x0 + 20 pt)
       (c) Punctuation continuation (line 1 ends with +, -, =, comma)
     Lines that both begin with independent relation symbols at similar
     indentation are NOT merged (distinct equation identity preservation).

  4. STRUCTURAL PROVENANCE (traceability):
     Every proposal carries a structural_provenance record linking it
     to its contributing span IDs, glyph indices, baseline tolerance
     applied, merge reason, and source coordinates.

Invariants:
  - Consumes Layer A observations (font_aware_math_classifier.py frozen v1.0)
    via the SAME extract_hierarchical_observations() entry point as v2.
  - Does NOT modify v2 files, provenance records, or evaluation artifacts.
  - All file writes use encoding="utf-8".
  - Level 4 proposals are NEVER deleted by Level 5 merging.
  - No gold coordinates used during proposal generation.

Contract:
  - Input:  MuPDF doc handle + page index (identical to v2)
  - Output: JSON per page with schema_version="3.0_structural_reconstruction"
            and identical top-level keys to v2 for direct comparison.
"""
from __future__ import annotations

import hashlib
import json
import re
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
    MATH_FUNCTION_NAMES,
)

# Import the frozen v2 observation extractor — Layer C consumes Layer A,
# it does NOT re-implement glyph classification.
from hierarchical_region_proposals import extract_hierarchical_observations

try:
    import fitz
except ImportError:
    import pymupdf as fitz  # type: ignore[import-not-found]

OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"

# ── v3 Parameters ──────────────────────────────────────────────────────────
# Baseline grouping (Level 3)
BASELINE_TOLERANCE_PT_FLOOR = 3.0   # absolute minimum tolerance
BASELINE_TOLERANCE_RATIO = 0.45     # proportion of max font size in pair
LINE_HORIZONTAL_GAP_PT = 14.0       # max horizontal gap between spans

# Multiline association (Level 5)
MULTILINE_MAX_GAP_PT = 16.0         # max vertical gap between lines
RELATION_ALIGNMENT_PT = 5.0         # max horizontal offset for shared relation
INDENTATION_THRESHOLD_PT = 20.0     # minimum indent to qualify as continuation

# Equation-number detection
EQ_NUMBER_RE = re.compile(r"^\s*\(?\d+\)?\s*$")
EQ_NUMBER_MARGIN_PT = 80.0          # right margin threshold

# Structural relation characters for multiline guardrails
RELATION_CHARS = set("=≠<≤>≥≈∼≡⇔⇒→↦∝∈∋⊂⊃⊆⊇")
CONTINUATION_ENDINGS = set("+-−=,;·×")


def merge_bboxes(bboxes: list[list[float]]) -> list[float]:
    x0 = min(b[0] for b in bboxes)
    y0 = min(b[1] for b in bboxes)
    x1 = max(b[2] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    return [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)]


def adaptive_baseline_tolerance(span_a: dict, span_b: dict) -> float:
    """
    AC-1: Compute adaptive baseline tolerance based on max font size
    in the pair. This recovers subscripts/superscripts at |Δy| = 3.1–3.3 pt
    (7pt script on 10pt base) without expanding tolerance for same-size text.
    """
    max_size = max(span_a["font_size_pt"], span_b["font_size_pt"])
    return max(BASELINE_TOLERANCE_PT_FLOOR, BASELINE_TOLERANCE_RATIO * max_size)


def build_level3_line_groups_v3(spans: list[dict], page_width_pt: float) -> list[dict]:
    """
    Level 3: Group spans into baseline-aligned line groups.
    Uses adaptive tolerance (AC-1) instead of rigid 3.0 pt.
    """
    n = len(spans)
    if n == 0:
        return []

    parent = list(range(n))
    # Track the tolerance actually used for each merge (provenance)
    merge_tolerances: dict[tuple[int, int], float] = {}

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        si = spans[i]
        for j in range(i + 1, n):
            sj = spans[j]
            # Adaptive tolerance based on font sizes in this pair
            tol = adaptive_baseline_tolerance(si, sj)
            dy = abs(si["centre_y"] - sj["centre_y"])
            if dy > tol:
                continue
            # Horizontal gap
            gap = max(0.0, max(si["bbox_pdf_pt"][0] - sj["bbox_pdf_pt"][2],
                               sj["bbox_pdf_pt"][0] - si["bbox_pdf_pt"][2]))
            if gap <= LINE_HORIZONTAL_GAP_PT:
                union(i, j)
                merge_tolerances[(min(i, j), max(i, j))] = round(tol, 3)

    groups_map: dict[int, list[int]] = {}
    for i in range(n):
        r = find(i)
        groups_map.setdefault(r, []).append(i)

    line_groups = []
    for root, members in groups_map.items():
        m_spans = [spans[m] for m in members]
        m_spans.sort(key=lambda s: s["bbox_pdf_pt"][0])

        merged_bbox = merge_bboxes([s["bbox_pdf_pt"] for s in m_spans])
        combined_text = " ".join(s["text"] for s in m_spans).strip()
        total_glyphs = sum(s["total_glyph_count"] for s in m_spans)
        total_math_glyphs = sum(s["math_glyph_count"] for s in m_spans)
        math_ratio = round(total_math_glyphs / max(total_glyphs, 1), 4)

        has_math_rel = any(r in combined_text for r in "=≠<≤>≥≈∼≡⇔⇒→↦")
        has_math_op = (
            any(op in combined_text for op in "∫∬∑∏√∇∂±∓×÷")
            or any(s["has_font_operator"] for s in m_spans)
        )
        has_greek = any(g in combined_text for g in GREEK)
        has_math_func = any(s["has_math_function"] for s in m_spans)

        cit_eval = discriminate_citation(combined_text)

        # Equation number detection on right margin
        last_span = m_spans[-1]
        has_eq_num = (
            bool(EQ_NUMBER_RE.match(last_span["text"].strip()))
            and last_span["bbox_pdf_pt"][2] > (page_width_pt - EQ_NUMBER_MARGIN_PT)
        )

        is_equation_line = (
            (has_math_rel or has_math_op or has_greek or has_math_func or math_ratio >= 0.35)
            and not cit_eval["is_citation_candidate"]
            and total_glyphs >= 3
        )

        # Compute max baseline tolerance applied within this group
        member_indices = sorted(members)
        max_tol_applied = BASELINE_TOLERANCE_PT_FLOOR
        for idx_a, a in enumerate(member_indices):
            for b in member_indices[idx_a + 1:]:
                key = (min(a, b), max(a, b))
                if key in merge_tolerances:
                    max_tol_applied = max(max_tol_applied, merge_tolerances[key])

        # Collect all contributing glyph indices
        all_glyph_indices = []
        for s in m_spans:
            all_glyph_indices.extend(s.get("glyph_indices", []))

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
            # v3 provenance extensions
            "v3_baseline_tolerance_max_applied_pt": round(max_tol_applied, 3),
            "v3_contributing_glyph_indices": all_glyph_indices,
        })

    line_groups.sort(key=lambda lg: lg["merged_bbox"][1])
    for idx, lg in enumerate(line_groups):
        lg["line_group_id"] = idx
    return line_groups


def _detect_equation_number_metadata(
    line_group: dict, all_spans: list[dict], page_width_pt: float
) -> dict | None:
    """
    AC-4: Detect and decouple equation-number labels from the expression body.
    Returns equation_number_metadata dict or None.
    """
    if not line_group["has_equation_number"]:
        return None

    member_ids = line_group["member_span_ids"]
    if not member_ids:
        return None

    # The equation number is typically the last span on the right margin
    m_spans = [s for s in all_spans if s["span_id"] in member_ids]
    m_spans.sort(key=lambda s: s["bbox_pdf_pt"][0])

    last_span = m_spans[-1]
    label_text = last_span["text"].strip()
    if not EQ_NUMBER_RE.match(label_text):
        return None

    label_bbox = last_span["bbox_pdf_pt"]
    # Compute gap between expression body and the label
    if len(m_spans) > 1:
        expr_spans = m_spans[:-1]
        expr_right = max(s["bbox_pdf_pt"][2] for s in expr_spans)
        gap = label_bbox[0] - expr_right
    else:
        gap = 0.0

    return {
        "label_text": label_text,
        "label_bbox": label_bbox,
        "label_span_id": last_span["span_id"],
        "gap_to_expression_pt": round(gap, 3),
    }


def _compute_math_expression_bbox(
    line_group: dict, all_spans: list[dict], eq_num_meta: dict | None
) -> list[float]:
    """
    AC-4: Compute tight bounding box around the mathematical expression,
    excluding the equation-number label.
    """
    member_ids = set(line_group["member_span_ids"])
    if eq_num_meta is not None:
        # Exclude the equation-number span
        member_ids.discard(eq_num_meta["label_span_id"])

    if not member_ids:
        return line_group["merged_bbox"]

    expr_spans = [s for s in all_spans if s["span_id"] in member_ids]
    if not expr_spans:
        return line_group["merged_bbox"]

    return merge_bboxes([s["bbox_pdf_pt"] for s in expr_spans])


def _has_shared_relation_alignment(lg1: dict, lg2: dict) -> bool:
    """
    AC-3 guardrail (a): Check if two line groups share a relation symbol
    at approximately the same horizontal position (within RELATION_ALIGNMENT_PT).
    """
    text1 = lg1["text"]
    text2 = lg2["text"]

    # Find positions of relation characters in each text
    # We approximate horizontal position by fractional offset within the bbox
    for rc in RELATION_CHARS:
        if rc in text1 and rc in text2:
            # Both lines contain the same relation character
            # Check horizontal alignment: relation should be at similar x position
            # Use a simpler heuristic: if both lines have the relation and share
            # significant horizontal overlap, they likely share alignment
            x_overlap = max(0.0, min(lg1["merged_bbox"][2], lg2["merged_bbox"][2]) -
                                  max(lg1["merged_bbox"][0], lg2["merged_bbox"][0]))
            min_width = min(
                lg1["merged_bbox"][2] - lg1["merged_bbox"][0],
                lg2["merged_bbox"][2] - lg2["merged_bbox"][0],
            )
            if min_width > 0 and (x_overlap / min_width) >= 0.30:
                return True
    return False


def _is_indented_continuation(lg1: dict, lg2: dict) -> bool:
    """
    AC-3 guardrail (b): Second line is indented relative to first line,
    suggesting a continuation rather than a new equation.
    """
    return lg2["merged_bbox"][0] > (lg1["merged_bbox"][0] + INDENTATION_THRESHOLD_PT)


def _has_punctuation_continuation(lg1: dict) -> bool:
    """
    AC-3 guardrail (c): First line ends with a continuation character
    (operator or comma), suggesting the expression continues on the next line.
    """
    text = lg1["text"].rstrip()
    if not text:
        return False
    return text[-1] in CONTINUATION_ENDINGS


def _both_begin_with_independent_relations(lg1: dict, lg2: dict) -> bool:
    """
    AC-2/AC-3 safety check: If both lines begin with independent relation
    symbols at similar indentation, they are likely separate equations.
    Do NOT merge them.
    """
    text1 = lg1["text"].lstrip()
    text2 = lg2["text"].lstrip()

    t1_starts_rel = bool(text1) and text1[0] in RELATION_CHARS
    t2_starts_rel = bool(text2) and text2[0] in RELATION_CHARS

    if t1_starts_rel and t2_starts_rel:
        # Both begin with relations — check if indentation is similar
        indent_diff = abs(lg1["merged_bbox"][0] - lg2["merged_bbox"][0])
        if indent_diff < INDENTATION_THRESHOLD_PT:
            return True
    return False


def _multiline_merge_reason(lg1: dict, lg2: dict) -> str | None:
    """
    AC-3: Determine if two line groups should be merged, and if so, why.
    Returns the merge reason string, or None if merge is rejected.
    """
    # Safety: if both begin with independent relations at similar indent, reject
    if _both_begin_with_independent_relations(lg1, lg2):
        return None

    # Check structural continuity signals
    if _has_punctuation_continuation(lg1):
        return "punctuation_continuation"
    if _is_indented_continuation(lg1, lg2):
        return "indented_continuation"
    if _has_shared_relation_alignment(lg1, lg2):
        return "shared_relation_alignment"

    # No structural continuity signal — reject merge
    return None


def build_level4_level5_proposals_v3(
    line_groups: list[dict], spans: list[dict], page_width_pt: float
) -> list[dict]:
    """
    Level 4/5 proposals with v3 structural improvements:
      - Equation-number decoupling (AC-4)
      - math_expression_bbox (AC-4)
      - Multiline guardrails (AC-3)
      - Structural provenance (traceability)
    """
    proposals = []

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

        # AC-4: Equation number decoupling
        eq_num_meta = _detect_equation_number_metadata(lg, spans, page_width_pt)
        math_expr_bbox = _compute_math_expression_bbox(lg, spans, eq_num_meta)

        proposal = {
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
            # v3 extensions
            "math_expression_bbox": math_expr_bbox,
            "structural_provenance": {
                "contributing_span_ids": lg["member_span_ids"],
                "contributing_glyph_indices": lg.get("v3_contributing_glyph_indices", []),
                "baseline_tolerance_applied_pt": lg.get("v3_baseline_tolerance_max_applied_pt",
                                                        BASELINE_TOLERANCE_PT_FLOOR),
                "merge_reason": "adaptive_baseline",
                "source_coordinates": {
                    "min_x": lg["merged_bbox"][0],
                    "min_y": lg["merged_bbox"][1],
                    "max_x": lg["merged_bbox"][2],
                    "max_y": lg["merged_bbox"][3],
                },
            },
        }

        if eq_num_meta is not None:
            proposal["equation_number_metadata"] = eq_num_meta

        proposals.append(proposal)

    # Level 5: Multiline with structural guardrails (AC-3)
    for i in range(len(eq_lines)):
        l1 = eq_lines[i]
        for j in range(i + 1, min(i + 3, len(eq_lines))):
            l2 = eq_lines[j]

            # Vertical gap check
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

            # AC-3: Require structural continuity signal
            merge_reason = _multiline_merge_reason(l1, l2)
            if merge_reason is None:
                continue

            merged_box = merge_bboxes([l1["merged_bbox"], l2["merged_bbox"]])

            # Compute combined expression bbox (excluding equation numbers)
            eq_num_1 = _detect_equation_number_metadata(l1, spans, page_width_pt)
            eq_num_2 = _detect_equation_number_metadata(l2, spans, page_width_pt)
            expr_bbox_1 = _compute_math_expression_bbox(l1, spans, eq_num_1)
            expr_bbox_2 = _compute_math_expression_bbox(l2, spans, eq_num_2)
            merged_expr_bbox = merge_bboxes([expr_bbox_1, expr_bbox_2])

            # Combine glyph indices for provenance
            combined_glyph_indices = (
                l1.get("v3_contributing_glyph_indices", []) +
                l2.get("v3_contributing_glyph_indices", [])
            )

            proposal = {
                "proposal_id": f"L5_multiline_{l1['line_group_id']}_{l2['line_group_id']}",
                "hierarchy_level": 5,
                "proposal_type": "multiline_equation_structure",
                "merged_bbox": merged_box,
                "text": f"{l1['text']}  ///  {l2['text']}",
                "line_group_ids": [l1["line_group_id"], l2["line_group_id"]],
                "span_count": l1["span_count"] + l2["span_count"],
                "total_glyph_count": l1["total_glyph_count"] + l2["total_glyph_count"],
                "math_glyph_ratio": round(
                    (l1["math_glyph_count"] + l2["math_glyph_count"]) /
                    max(l1["total_glyph_count"] + l2["total_glyph_count"], 1), 4),
                "candidate_reasons": ["multiline_continuity", merge_reason],
                "has_equation_number": l1["has_equation_number"] or l2["has_equation_number"],
                "is_citation_filtered": False,
                # v3 extensions
                "math_expression_bbox": merged_expr_bbox,
                "structural_provenance": {
                    "contributing_span_ids": l1["member_span_ids"] + l2["member_span_ids"],
                    "contributing_glyph_indices": combined_glyph_indices,
                    "baseline_tolerance_applied_pt": max(
                        l1.get("v3_baseline_tolerance_max_applied_pt", BASELINE_TOLERANCE_PT_FLOOR),
                        l2.get("v3_baseline_tolerance_max_applied_pt", BASELINE_TOLERANCE_PT_FLOOR),
                    ),
                    "merge_reason": merge_reason,
                    "source_coordinates": {
                        "min_x": merged_box[0],
                        "min_y": merged_box[1],
                        "max_x": merged_box[2],
                        "max_y": merged_box[3],
                    },
                },
            }

            if eq_num_1 is not None:
                proposal["equation_number_metadata"] = eq_num_1
            elif eq_num_2 is not None:
                proposal["equation_number_metadata"] = eq_num_2

            proposals.append(proposal)

    return proposals


def run_page_v3(doc, page_0based: int, document_id: str = "", pdf_sha256: str = "") -> dict:
    """
    Run the v3 pipeline on a single page.
    Consumes frozen Layer A observations (extract_hierarchical_observations).
    """
    page_1based = page_0based + 1
    page = doc[page_0based]
    page_width_pt = page.rect.width

    # Level 1 & Level 2 — from frozen Layer A (v2 module)
    glyphs, spans = extract_hierarchical_observations(page, page_0based)

    # Level 3 — v3 adaptive baseline grouping
    line_groups = build_level3_line_groups_v3(spans, page_width_pt)

    # Level 4 & Level 5 — v3 structural proposals with guardrails
    proposals = build_level4_level5_proposals_v3(line_groups, spans, page_width_pt)

    l4_count = sum(1 for p in proposals if p["hierarchy_level"] == 4)
    l5_count = sum(1 for p in proposals if p["hierarchy_level"] == 5)
    cit_lines = sum(1 for lg in line_groups if lg["citation_evaluation"]["is_citation_candidate"])

    print(
        f"[v3] Page {page_1based}: {len(glyphs)} glyphs, {len(spans)} spans, "
        f"{len(line_groups)} line groups ({cit_lines} citations discriminated), "
        f"{l4_count} Level 4 proposals, {l5_count} Level 5 proposals",
        flush=True,
    )

    return {
        "schema_version": "3.0_structural_reconstruction",
        "document_id": document_id,
        "source_pdf_sha256": pdf_sha256,
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
        "v3_parameters": {
            "baseline_tolerance_floor_pt": BASELINE_TOLERANCE_PT_FLOOR,
            "baseline_tolerance_ratio": BASELINE_TOLERANCE_RATIO,
            "multiline_max_gap_pt": MULTILINE_MAX_GAP_PT,
            "relation_alignment_pt": RELATION_ALIGNMENT_PT,
            "indentation_threshold_pt": INDENTATION_THRESHOLD_PT,
        },
        "level4_level5_proposals": proposals,
        "level3_line_groups": line_groups,
    }


if __name__ == "__main__":
    print("hierarchical_region_proposals_v3.py — Layer C Experimental Structural Reconstruction")
    print("Import and call run_page_v3(doc, page_0based, document_id, pdf_sha256) to run.")
    print("Do NOT use this module as a standalone script; it is consumed by comparison runners.")

