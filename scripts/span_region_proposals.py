#!/usr/bin/env python3
"""
Span-Based Region Proposals for 1505.05770
Layer B: Group spatially related MuPDF spans and characters into candidate
mathematical region proposals.

Three-layer contract:
  Layer A — Raw observations   : MuPDF spans, glyphs, font sizes, origins, bboxes
  Layer B — Region proposals   : THIS FILE — groups A into equation-candidate regions
  Layer C — Gold comparison    : scripts/positive_control_comparison.py (unchanged)

Layer B does NOT:
  - Use gold coordinates or gold equation IDs
  - Modify the blind detection outputs (those are frozen)
  - Generate structural expectations
  - Perform OCR

Proposal algorithm:
  1. Load Layer A observations from the blind detection JSON (spans + characters).
  2. For each page, build candidate spans using math-content signals:
       a. Contains Greek letters, math operators, or math punctuation
       b. Has significantly smaller or larger font size than page median (scripts)
       c. Is adjacent horizontally to a known math span (within gap threshold)
  3. Cluster math-candidate spans by baseline proximity:
       a. Spans on the same baseline (|Δy_centre| < vertical_tolerance) and
          sufficiently close horizontally (gap < horizontal_gap_threshold) are merged.
       b. Multiline equations: allow vertical gaps ≤ interline_tolerance when
          the baseline delta is consistent with display-math spacing.
  4. Apply prose-separation filters:
       a. Minimum math-character fraction within the cluster.
       b. Minimum span count or character count.
       c. Equation-number pattern adjacent to right margin (optional annotation).
  5. Produce region proposals with:
       - merged_bbox in mupdf_page_points
       - member span indices and character counts
       - math_char_fraction
       - multiline flag
       - candidate_reasons list
       - gold_coverage placeholder (populated in Layer C)

Outputs:
    DATASETS/structural_preservation/1505.05770_region_proposals_p002.json
    DATASETS/structural_preservation/1505.05770_region_proposals_p003.json

Invariants:
    - Input: blind detection JSON (Layer A) — not the gold manifest
    - Gold coordinates never read in this script
    - All file writes use encoding="utf-8"
    - Page coordinate space: mupdf_page_points (same as gold bboxes)
"""
from __future__ import annotations

import json
import math
import re
import statistics
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = REPO_ROOT / "DATASETS" / "structural_preservation"

DETECTION_PATHS = {
    2: OUT_ROOT / "1505.05770_blind_detection_p002.json",
    3: OUT_ROOT / "1505.05770_blind_detection_p003.json",
}

# ── Character classification sets (from targeted_math_detector.py) ─────────
GREEK = set("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩϕϑϖϱς")
MATH  = set("∫∑∏√∞∂∇±∓×·≤≥≠≈∝∈∉⊂⊆→⇒↔∼")
MATH_PUNCT = set("=<>+-−*/^_{}[]()|,:;")

# ── Clustering parameters (fixed before evaluation; not tuned to gold) ─────
# Vertical tolerance: spans within this many points of centre are on same baseline
BASELINE_TOLERANCE_PT = 3.0
# Maximum horizontal gap between adjacent spans on the same baseline (points).
# Kept deliberately tight to avoid merging prose columns. Display-math spans
# are typeset on a single baseline with small inter-glyph gaps.
HORIZONTAL_GAP_PT = 8.0
# Maximum vertical gap between lines of a multiline equation (points).
# Roughly one font-size; display math lines are closer than body text interline.
INTERLINE_GAP_PT = 14.0
# Maximum cluster width as a fraction of page width.
# A cluster spanning the full page width is prose, not an equation.
MAX_CLUSTER_WIDTH_FRACTION = 0.65
# Minimum fraction of characters that must be math-like for a cluster to qualify
MIN_MATH_CHAR_FRACTION = 0.30
# Minimum character count in a cluster
MIN_CHAR_COUNT = 3
# Maximum span count: very large clusters are prose paragraphs, not equations
MAX_SPAN_COUNT = 25
# Equation number pattern: isolated digit(s) or (N) near right margin
EQ_NUMBER_RE = re.compile(r"^\s*\(?\d+\)?\s*$")
# Right-margin threshold: within this many points of page right edge
EQ_NUMBER_MARGIN_PT = 60.0


def is_math_char(ch: str) -> bool:
    return bool(ch) and (
        ch in GREEK or ch in MATH or ch in MATH_PUNCT or ch.isdigit() or ch in "∅"
    )


def bbox_centre_y(bbox):
    return (bbox[1] + bbox[3]) / 2


def bbox_centre_x(bbox):
    return (bbox[0] + bbox[2]) / 2


def horizontal_gap(a_bbox, b_bbox):
    """Gap between two horizontally ordered bboxes (negative = overlap)."""
    return max(0.0, max(a_bbox[0] - b_bbox[2], b_bbox[0] - a_bbox[2]))


def merge_bboxes(bboxes):
    x0 = min(b[0] for b in bboxes)
    y0 = min(b[1] for b in bboxes)
    x1 = max(b[2] for b in bboxes)
    y1 = max(b[3] for b in bboxes)
    return [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)]


# ── Layer A span loading ───────────────────────────────────────────────────

def load_spans_and_chars(det_data: dict) -> tuple[list, list]:
    """
    Extract math-like text spans and all character observations from Layer A.
    Returns (spans, chars).
    """
    spans = det_data.get("math_like_text_spans", [])
    chars = det_data.get("character_observations", [])
    return spans, chars


def build_span_records(spans: list, chars: list, page_width_pt: float) -> list:
    """
    Build enriched span records from Layer A detection output.

    Field name mapping from blind detection JSON schema:
      span["bbox_pdf_pt"]          → bbox (mupdf_page_points)
      span["font_size_pt"]         → font_size_pt (already named correctly)
      span["math_character_count"] → math_char_count
      span["math_character_ratio"] → math_char_fraction (pre-computed by detector)

    is_eq_number: span text matches isolated digit pattern and is near right margin.
    """
    records = []
    for idx, sp in enumerate(spans):
        text = sp.get("text", "")
        # Detection JSON uses "bbox_pdf_pt", not "bbox"
        bbox = sp.get("bbox_pdf_pt", sp.get("bbox", None))
        if bbox is None:
            continue
        font_size = sp.get("font_size_pt", sp.get("font_size", 0.0))
        char_count = max(len(text.replace(" ", "")), 1)
        # Use detector's pre-computed counts if available, else recompute
        math_count = sp.get("math_character_count",
                             sum(1 for c in text if is_math_char(c)))
        math_frac = sp.get("math_character_ratio",
                            math_count / char_count if char_count else 0.0)
        is_eq_num = bool(EQ_NUMBER_RE.match(text)) and bbox[0] > (page_width_pt - EQ_NUMBER_MARGIN_PT)

        records.append({
            "span_index": idx,
            "text": text,
            "bbox": bbox,
            "font_size_pt": font_size,
            "char_count": char_count,
            "math_char_count": math_count,
            "math_char_fraction": round(math_frac, 4),
            "is_equation_number": is_eq_num,
            "centre_y": bbox_centre_y(bbox),
            "centre_x": bbox_centre_x(bbox),
        })
    return records


# ── Clustering ─────────────────────────────────────────────────────────────

def cluster_spans_into_regions(span_records: list) -> list:
    """
    Union-find clustering in two passes:
      Pass 1: Same-baseline merging (|Δy_centre| ≤ BASELINE_TOLERANCE_PT
              and horizontal gap ≤ HORIZONTAL_GAP_PT).
      Pass 2: Multiline merging (vertically adjacent single-line clusters
              within INTERLINE_GAP_PT whose bboxes horizontally overlap).

    Returns list of cluster dicts.
    """
    n = len(span_records)
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

    # Pass 1 — same-baseline, horizontally adjacent
    for i in range(n):
        for j in range(i + 1, n):
            si, sj = span_records[i], span_records[j]
            if abs(si["centre_y"] - sj["centre_y"]) > BASELINE_TOLERANCE_PT:
                continue
            if horizontal_gap(si["bbox"], sj["bbox"]) > HORIZONTAL_GAP_PT:
                continue
            union(i, j)

    # Build intermediate cluster bboxes for pass 2
    def build_cluster_map():
        clmap: dict[int, list] = {}
        for i in range(n):
            root = find(i)
            clmap.setdefault(root, []).append(i)
        return clmap

    clmap = build_cluster_map()

    def cluster_bbox(members):
        return merge_bboxes([span_records[m]["bbox"] for m in members])

    def clusters_horizontally_overlap(bbox_a, bbox_b):
        return bbox_a[0] < bbox_b[2] and bbox_a[2] > bbox_b[0]

    # Pass 2 — multiline vertical merging
    roots = list(clmap.keys())
    for ii in range(len(roots)):
        for jj in range(ii + 1, len(roots)):
            ri, rj = roots[ii], roots[jj]
            # Recompute roots in case they changed
            ri = find(ri)
            rj = find(rj)
            if ri == rj:
                continue
            bb_i = cluster_bbox(clmap[roots[ii]])
            bb_j = cluster_bbox(clmap[roots[jj]])
            # Vertical gap between the two clusters
            vert_gap = max(0.0, max(bb_i[1] - bb_j[3], bb_j[1] - bb_i[3]))
            if vert_gap > INTERLINE_GAP_PT:
                continue
            if not clusters_horizontally_overlap(bb_i, bb_j):
                continue
            union(roots[ii], roots[jj])

    # Collect final clusters
    final_map: dict[int, list] = {}
    for i in range(n):
        root = find(i)
        final_map.setdefault(root, []).append(i)

    clusters = []
    for root, members in final_map.items():
        member_spans = [span_records[m] for m in members]
        merged = merge_bboxes([s["bbox"] for s in member_spans])
        total_chars = sum(s["char_count"] for s in member_spans)
        total_math = sum(s["math_char_count"] for s in member_spans)
        math_frac = total_math / max(total_chars, 1)
        all_text = " ".join(s["text"] for s in sorted(member_spans, key=lambda s: (s["centre_y"], s["centre_x"])))
        # Detect multiline: member spans span more than 1.5× the median font size vertically
        font_sizes = [s["font_size_pt"] for s in member_spans if s["font_size_pt"] > 0]
        median_fs = statistics.median(font_sizes) if font_sizes else 10.0
        y_range = merged[3] - merged[1]
        is_multiline = y_range > 1.5 * median_fs

        # Equation number annotation
        eq_numbers = [s["text"].strip() for s in member_spans if s["is_equation_number"]]

        reasons = []
        if math_frac >= MIN_MATH_CHAR_FRACTION:
            reasons.append("math_char_fraction_threshold")
        if any(s["math_char_fraction"] > 0.5 for s in member_spans):
            reasons.append("high_density_math_span_present")
        if is_multiline:
            reasons.append("multiline_cluster")
        if eq_numbers:
            reasons.append("equation_number_adjacent")

        clusters.append({
            "cluster_id": len(clusters),
            "merged_bbox": merged,
            "span_count": len(member_spans),
            "char_count": total_chars,
            "math_char_count": total_math,
            "math_char_fraction": round(math_frac, 4),
            "is_multiline": is_multiline,
            "equation_number_text": eq_numbers if eq_numbers else None,
            "candidate_reasons": reasons,
            "member_span_indices": sorted([span_records[m]["span_index"] for m in members]),
            "representative_text": all_text[:200],
        })

    return clusters


def filter_prose(clusters: list, page_width_pt: float) -> tuple[list, list]:
    """
    Split clusters into equation_candidates and prose_filtered.

    Prose filters (any one is sufficient to reject):
      - math_char_fraction < MIN_MATH_CHAR_FRACTION
      - char_count < MIN_CHAR_COUNT
      - cluster width > MAX_CLUSTER_WIDTH_FRACTION × page_width  (prose paragraph)
      - span_count > MAX_SPAN_COUNT  (prose paragraph)
    """
    candidates = []
    filtered = []
    for cl in clusters:
        cluster_width = cl["merged_bbox"][2] - cl["merged_bbox"][0]
        width_fraction = cluster_width / max(page_width_pt, 1.0)
        reject_reason = None

        if cl["math_char_fraction"] < MIN_MATH_CHAR_FRACTION:
            reject_reason = f"math_char_fraction={cl['math_char_fraction']:.3f} < {MIN_MATH_CHAR_FRACTION}"
        elif cl["char_count"] < MIN_CHAR_COUNT:
            reject_reason = f"char_count={cl['char_count']} < {MIN_CHAR_COUNT}"
        elif width_fraction > MAX_CLUSTER_WIDTH_FRACTION:
            reject_reason = f"width_fraction={width_fraction:.3f} > {MAX_CLUSTER_WIDTH_FRACTION} (prose paragraph)"
        elif cl["span_count"] > MAX_SPAN_COUNT:
            reject_reason = f"span_count={cl['span_count']} > {MAX_SPAN_COUNT} (prose paragraph)"

        if reject_reason:
            cl["filter_reason"] = reject_reason
            filtered.append(cl)
        else:
            candidates.append(cl)
    return candidates, filtered


# ── IoU and gold_coverage helpers ──────────────────────────────────────────

def iou(a, b):
    ix0 = max(a[0], b[0]); iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2]); iy1 = min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return round(inter / max(area_a + area_b - inter, 1e-9), 6)


def gold_coverage(proposal_bbox, gold_bbox):
    """fraction of gold_bbox area covered by proposal_bbox intersection"""
    ix0 = max(proposal_bbox[0], gold_bbox[0]); iy0 = max(proposal_bbox[1], gold_bbox[1])
    ix1 = min(proposal_bbox[2], gold_bbox[2]); iy1 = min(proposal_bbox[3], gold_bbox[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    gold_area = max((gold_bbox[2] - gold_bbox[0]) * (gold_bbox[3] - gold_bbox[1]), 1e-9)
    return round(inter / gold_area, 6)


# ── Main ───────────────────────────────────────────────────────────────────

def process_page(page_1based: int, det_data: dict) -> dict:
    page_width = det_data["page_size_pdf_pt"][0]
    spans, chars = load_spans_and_chars(det_data)
    span_records = build_span_records(spans, chars, page_width)

    print(f"  {len(span_records)} math-span records loaded", flush=True)

    all_clusters = cluster_spans_into_regions(span_records)
    equation_candidates, prose_filtered = filter_prose(all_clusters, page_width)

    print(
        f"  {len(all_clusters)} clusters total → "
        f"{len(equation_candidates)} equation candidates, "
        f"{len(prose_filtered)} filtered as prose",
        flush=True,
    )

    return {
        "schema_version": "1.0",
        "layer": "B_region_proposals",
        "step": "span_clustering",
        "document_id": "1505.05770",
        "source_detection_file": str(DETECTION_PATHS[page_1based]),
        "source_pdf_sha256": det_data["source_pdf_sha256"],
        "gold_coordinates_used": False,
        "page_number_1_based": page_1based,
        "page_index_0_based": page_1based - 1,
        "page_size_pdf_pt": det_data["page_size_pdf_pt"],
        "coordinate_space": "mupdf_page_points",
        "clustering_parameters": {
            "baseline_tolerance_pt": BASELINE_TOLERANCE_PT,
            "horizontal_gap_pt": HORIZONTAL_GAP_PT,
            "interline_gap_pt": INTERLINE_GAP_PT,
            "max_cluster_width_fraction": MAX_CLUSTER_WIDTH_FRACTION,
            "max_span_count": MAX_SPAN_COUNT,
            "min_math_char_fraction": MIN_MATH_CHAR_FRACTION,
            "min_char_count": MIN_CHAR_COUNT,
            "eq_number_margin_pt": EQ_NUMBER_MARGIN_PT,
            "page_width_pt": page_width,
        },
        "summary": {
            "input_math_span_count": len(span_records),
            "total_cluster_count": len(all_clusters),
            "equation_candidate_count": len(equation_candidates),
            "prose_filtered_count": len(prose_filtered),
        },
        "equation_candidates": equation_candidates,
        "prose_filtered_clusters": prose_filtered,
        "limitations": [
            "Span-based proposals rely on the PDF text layer; glyphs mis-mapped by font encoding appear as wrong characters.",
            "Math-character fraction thresholds are fixed and not tuned against this gold population.",
            "Multiline merging uses vertical proximity; equation rows with large vertical gaps may be split.",
            "Ordinary prose with mathematical symbols (e.g., probability notation) may pass the math-fraction filter.",
            "No structural expectations are generated here; this is Layer B only.",
            "gold_coverage values are populated in Layer C (positive_control_comparison.py), not here.",
        ],
    }


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    for page_1based, det_path in DETECTION_PATHS.items():
        if not det_path.is_file():
            sys.exit(
                f"[ERROR] Detection file not found: {det_path}\n"
                "Run scripts/blind_detection_run_1505.py first."
            )
        with det_path.open(encoding="utf-8") as f:
            det_data = json.load(f)

        # Verify provenance
        expected_sha = "776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a"
        if det_data.get("source_pdf_sha256") != expected_sha:
            sys.exit(f"[ERROR] PDF SHA-256 mismatch in {det_path}")

        print(f"\n[span_proposals] Page {page_1based} ...", flush=True)
        result = process_page(page_1based, det_data)

        out_path = OUT_ROOT / f"1505.05770_region_proposals_p{page_1based:03d}.json"
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Saved → {out_path}", flush=True)

    print("\n[span_proposals] Done.", flush=True)


if __name__ == "__main__":
    main()
