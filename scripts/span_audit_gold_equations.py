#!/usr/bin/env python3
"""
Independent Span Audit — GS-001 through GS-005
1505.05770 · Variational Inference with Normalizing Flows

Purpose:
    Establish the source-layer representation of each gold equation in the
    MuPDF text extraction WITHOUT modifying clustering parameters or running
    Layer B. This is a pure observation script.

Questions answered per gold equation:
    1. Which MuPDF text spans from Layer A fall inside or overlap the gold bbox?
    2. What is the text, font, font_size_pt, and bbox of each such span?
    3. What math_character_ratio does the detector report for each?
    4. Are there gaps in coverage (portions of gold bbox with no span)?
    5. Are any spans partially outside the gold bbox (reading-order boundary effects)?
    6. For GS-005: is the equation present in the text layer at all, or only as
       drawing objects / rendered glyphs?
    7. For GS-001: what is the reading-order relationship of the three fragments?
    8. For GS-004: is the integral sign in a separate span? What is its bbox?

This script reads:
    - DATASETS/structural_preservation/1505.05770_blind_detection_p002.json (Layer A)
    - DATASETS/structural_preservation/1505.05770_blind_detection_p003.json (Layer A)
    - DATASETS/structural_preservation/1505.05770_positive_control_manifest.json (gold)

It does NOT:
    - Modify any files
    - Change clustering parameters
    - Run the PDF reader directly (uses already-extracted Layer A data)

Output:
    DATASETS/structural_preservation/1505.05770_span_audit.json
    (also printed to stdout)

Clustering parameters are NOT consulted here. This audit is upstream of clustering.
"""
from __future__ import annotations

import json
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "DATASETS" / "structural_preservation"

MANIFEST_PATH = OUT_ROOT / "1505.05770_positive_control_manifest.json"
DETECTION_PATHS = {
    1: OUT_ROOT / "1505.05770_blind_detection_p002.json",   # page_index_0_based = 1
    2: OUT_ROOT / "1505.05770_blind_detection_p003.json",   # page_index_0_based = 2
}
AUDIT_OUT = OUT_ROOT / "1505.05770_span_audit.json"


# ── Geometry helpers ───────────────────────────────────────────────────────

def boxes_intersect(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def intersection(a, b):
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)]


def area(bbox):
    return max(0.0, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))


def coverage_fraction(span_bbox, gold_bbox):
    """Fraction of gold_bbox area covered by span_bbox intersection."""
    ix = intersection(span_bbox, gold_bbox)
    if ix is None:
        return 0.0
    return round(area(ix) / max(area(gold_bbox), 1e-9), 6)


def span_containment(span_bbox, gold_bbox):
    """Is span_bbox fully inside gold_bbox?"""
    return (
        span_bbox[0] >= gold_bbox[0] and span_bbox[1] >= gold_bbox[1]
        and span_bbox[2] <= gold_bbox[2] and span_bbox[3] <= gold_bbox[3]
    )


def iou(a, b):
    ix = intersection(a, b)
    if ix is None:
        return 0.0
    i = area(ix)
    u = area(a) + area(b) - i
    return round(i / max(u, 1e-9), 6)


# ── Span matching ──────────────────────────────────────────────────────────

def audit_gold_equation(geq: dict, all_spans: list) -> dict:
    """
    For one gold equation, find all Layer A spans that intersect its gold_pdf_bbox.
    Returns a detailed audit record.
    """
    gold_bbox = geq["pdf_localization"]["gold_pdf_bbox"]
    gold_text = geq["pdf_localization"]["pdf_text_extracted"]
    gold_id = geq["gold_id"]
    gold_area = area(gold_bbox)

    matching_spans = []
    for sp in all_spans:
        sp_bbox = sp.get("bbox_pdf_pt", sp.get("bbox"))
        if sp_bbox is None:
            continue
        if not boxes_intersect(sp_bbox, gold_bbox):
            continue
        ix = intersection(sp_bbox, gold_bbox)
        cov = coverage_fraction(sp_bbox, gold_bbox)
        fully_inside = span_containment(sp_bbox, gold_bbox)
        outside_gold = not fully_inside
        overlap_area = area(ix) if ix else 0.0

        matching_spans.append({
            "span_index": sp.get("span_index", sp.get("block_index")),
            "text": sp.get("text", ""),
            "font": sp.get("font", ""),
            "font_size_pt": sp.get("font_size_pt", 0.0),
            "bbox_pdf_pt": sp_bbox,
            "math_character_count": sp.get("math_character_count", 0),
            "math_character_ratio": sp.get("math_character_ratio", 0.0),
            "intersection_with_gold": ix,
            "overlap_area_pt2": round(overlap_area, 3),
            "gold_coverage_fraction": cov,
            "span_fully_inside_gold": fully_inside,
            "span_extends_outside_gold": outside_gold,
            "iou_with_gold": iou(sp_bbox, gold_bbox),
        })

    # Sort by y then x (reading order)
    matching_spans.sort(key=lambda s: (s["bbox_pdf_pt"][1], s["bbox_pdf_pt"][0]))

    # Total coverage: union of all intersection areas as fraction of gold area
    # (approximate: sum of individual coverages, capped at 1.0)
    total_coverage_approx = min(1.0, sum(s["gold_coverage_fraction"] for s in matching_spans))

    # Identify gaps: sort spans by x within each y-band, detect horizontal gaps
    gap_analysis = detect_coverage_gaps(matching_spans, gold_bbox)

    return {
        "gold_id": gold_id,
        "gold_pdf_bbox": gold_bbox,
        "gold_pdf_text_extracted": gold_text,
        "gold_area_pt2": round(gold_area, 3),
        "matching_span_count": len(matching_spans),
        "total_coverage_fraction_approx": round(total_coverage_approx, 4),
        "gap_analysis": gap_analysis,
        "matching_spans": matching_spans,
        "audit_questions": {
            "has_any_intersecting_span": len(matching_spans) > 0,
            "all_spans_fully_inside_gold": all(s["span_fully_inside_gold"] for s in matching_spans),
            "has_high_math_ratio_span": any(s["math_character_ratio"] > 0.5 for s in matching_spans),
            "span_count_note": (
                "single_span" if len(matching_spans) == 1
                else f"fragmented_into_{len(matching_spans)}_spans" if len(matching_spans) > 1
                else "NO_SPANS_FOUND"
            ),
        },
    }


def detect_coverage_gaps(spans: list, gold_bbox: list) -> dict:
    """
    Identify horizontal uncovered intervals within the gold bbox y-extent.
    Reports the leftmost x-extent of each span on the gold baseline.
    """
    if not spans:
        return {"covered_x_intervals": [], "uncovered_leading_x": gold_bbox[2] - gold_bbox[0], "note": "no spans"}

    # Project spans onto the x-axis within the gold y-extent
    intervals = []
    for s in spans:
        sb = s["bbox_pdf_pt"]
        # clip to gold bbox x-extent
        x0 = max(sb[0], gold_bbox[0])
        x1 = min(sb[2], gold_bbox[2])
        if x1 > x0:
            intervals.append((round(x0, 2), round(x1, 2)))

    intervals.sort()
    # Merge overlapping
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append([start, end])

    gold_x_width = gold_bbox[2] - gold_bbox[0]
    covered = sum(e - s for s, e in merged)
    uncovered = max(0.0, gold_x_width - covered)

    return {
        "gold_x_extent": [round(gold_bbox[0], 2), round(gold_bbox[2], 2)],
        "covered_x_intervals": merged,
        "covered_x_width_pt": round(covered, 2),
        "uncovered_x_width_pt": round(uncovered, 2),
        "coverage_fraction": round(covered / max(gold_x_width, 1e-9), 4),
    }


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    # Load manifest (gold)
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        manifest = json.load(f)
    gold_eqs = manifest["gold_equations"]

    # Load Layer A detection data
    det_by_page_0based = {}
    for page_0based, path in DETECTION_PATHS.items():
        if not path.is_file():
            sys.exit(f"[ERROR] Detection file not found: {path}")
        with path.open(encoding="utf-8") as f:
            det_by_page_0based[page_0based] = json.load(f)

    audit_results = []

    for geq in gold_eqs:
        page_0based = geq["pdf_localization"]["page_index_zero_based"]
        det = det_by_page_0based[page_0based]
        all_spans = det.get("math_like_text_spans", [])

        print(f"\n{'='*70}", flush=True)
        print(f"{geq['gold_id']}  page_0based={page_0based}  gold_bbox={geq['pdf_localization']['gold_pdf_bbox']}", flush=True)
        print(f"Gold text (from PDF layer): {repr(geq['pdf_localization']['pdf_text_extracted'][:100])}", flush=True)

        result = audit_gold_equation(geq, all_spans)
        result["page_index_0_based"] = page_0based
        result["total_spans_on_page"] = len(all_spans)
        audit_results.append(result)

        print(f"Intersecting spans: {result['matching_span_count']} / {len(all_spans)} total on page", flush=True)
        print(f"Coverage approx: {result['total_coverage_fraction_approx']:.3f}", flush=True)
        print(f"Gap analysis: covered x-width={result['gap_analysis']['covered_x_width_pt']:.1f}pt / uncovered={result['gap_analysis']['uncovered_x_width_pt']:.1f}pt", flush=True)
        print(f"Questions: {result['audit_questions']}", flush=True)

        for i, sp in enumerate(result["matching_spans"]):
            print(
                f"  span {i}: [{sp['bbox_pdf_pt'][0]:.1f},{sp['bbox_pdf_pt'][1]:.1f},"
                f"{sp['bbox_pdf_pt'][2]:.1f},{sp['bbox_pdf_pt'][3]:.1f}]"
                f"  math_ratio={sp['math_character_ratio']:.2f}"
                f"  cov={sp['gold_coverage_fraction']:.3f}"
                f"  IoU={sp['iou_with_gold']:.3f}"
                f"  inside={sp['span_fully_inside_gold']}"
                f"  text={repr(sp['text'][:60])}",
                flush=True,
            )

    # Write output
    output = {
        "schema_version": "1.0",
        "audit_type": "independent_span_audit",
        "document_id": "1505.05770",
        "source_pdf_sha256": manifest["document_identity"]["pdf_sha256"],
        "layer": "A_observation_audit",
        "note": (
            "This audit is upstream of Layer B clustering. "
            "It examines which MuPDF text spans from Layer A intersect each gold bbox. "
            "Clustering parameters are NOT consulted here."
        ),
        "gold_equations_audited": len(audit_results),
        "results": audit_results,
    }
    AUDIT_OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[span_audit] Saved → {AUDIT_OUT}", flush=True)


if __name__ == "__main__":
    main()

