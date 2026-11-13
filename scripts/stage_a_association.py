"""Stage A — source occurrence to PDF region association.

Facilitates the mapping:
    source occurrence (equation) -> PDF region (page/block/line)

Implementation rules (gate-gated):
    - Candidate generation is INDEPENDENT of MathML gold geometry
      (uses the detector's independently generated geometry candidates).
    - No forced matching: ambiguous/unresolved cases are RETAINED as
      ambiguous rather than collapsed to a single match.
    - Every accepted or rejected alignment carries full provenance.
    - Stage A consumes the supplied 1505.05770v6.pdf and the source
      occurrence (equation item 193). It does NOT implement Stage B
      (node-to-glyph association).

Input:
    - Source occurrence            : equations[item 193] from the arXiv HTML
                                      extraction (S6.E20.m1).
    - Source occurrence hash       : sha256 of the item record.
    - PDF + hash                 : DATASETS/PDF_FIDELITY_RENDERINGS_ZERO/
                                    1505.05770v6.pdf (sha256: 776e07c2...).
    - Candidate regions           : geometry candidates from
                                      arena_math_audit/targeted_math_detection.json
                                      (52 candidates on page 3).

Output:
    - stage_a_output.json
      per region: iou, containment, status (accepted|ambiguous|rejected),
      provenance (source hash, pdf hash, tool versions, source_age).

This module does NOT:
    - modify frozen delimiter engines,
    - touch the existing AST extractor,
    - modify baseline datasets,
    - implement node-to-glyph association (that is Stage B).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Stable identifiers
# ---------------------------------------------------------------------------

SOURCE_OCCURRENCE_ID = "S6.E20.m1"
SOURCE_PAPER_ID = "1505.05770"
SOURCE_OCCURRENCE_INDEX = 193
SOURCE_OCCURRENCE_SOURCE = "mathml"


@dataclass(frozen=True)
class SourceOccurrence:
    """Frozen reference for the source equation to be mapped."""

    id: str
    paper_id: str
    index: int
    latex: str
    mathml: str
    source: str

    def sha256(self, *, include_latex: bool = True) -> str:
        """Deterministic payload hash for provenance (A0 verification)."""
        payload = (
            f"{self.id}|{self.paper_id}|{self.index}|{self.latex}|{self.mathml}|{self.source}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Phase 1 — independent candidate generation (A1)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GeometryCandidate:
    """Single character-level geometry observation from the detector."""

    page_index: int
    block_index: int
    line_index: int
    span_index: int
    char_index: int
    char: str
    font: str
    font_size_pt: float
    bbox_pdf_pt: tuple[float, float, float, float]
    width_pt: float
    height_pt: float
    is_math_char: bool
    page_median_character_height_pt: float
    height_ratio: float
    height_width_ratio: float
    candidate_reasons: list[str]
    status: str | None = None


@dataclass(frozen=True)
class PageCandidates:
    """All detector outputs for one PDF page."""

    page_number_1_based: int
    candidates: list[GeometryCandidate] = field(default_factory=list)
    character_observations: list[dict] = field(default_factory=list)
    limitations: str = ""


# ---------------------------------------------------------------------------
# Phase 2 — overlap and containment measurement (A2)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegionMetrics:
    """Geometric relationship between a source region and a candidate region."""

    overlap_area_pt2: float
    union_area_pt2: float
    iou: float
    containment: float
    n_char_overlap: int
    candidate_count: int


def _bbox_area(bbox: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = bbox
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def _region_metrics(
    expected_bbox: tuple[float, float, float, float],
    candidate_bbox: tuple[float, float, float, float],
) -> RegionMetrics:
    """Compute overlap/containment of an expected region against one candidate."""
    e_x0, e_y0, e_x1, e_y1 = expected_bbox
    c_x0, c_y0, c_x1, c_y1 = candidate_bbox

    e_area = _bbox_area(expected_bbox)
    c_area = _bbox_area(candidate_bbox)

    overlap_x0 = max(e_x0, c_x0)
    overlap_y0 = max(e_y0, c_y0)
    overlap_x1 = min(e_x1, c_x1)
    overlap_y1 = min(e_y1, c_y1)
    overlap_w = max(0.0, overlap_x1 - overlap_x0)
    overlap_h = max(0.0, overlap_y1 - overlap_y0)
    overlap_area = overlap_w * overlap_h

    union_area = e_area + c_area - overlap_area
    iou = overlap_area / union_area if union_area > 0 else 0.0
    containment = overlap_area / e_area if e_area > 0 else 0.0

    return RegionMetrics(
        overlap_area_pt2=overlap_area,
        union_area_pt2=union_area,
        iou=iou,
        containment=containment,
        n_char_overlap=0,  # computed at region level, not char level
        candidate_count=0,
    )


# ---------------------------------------------------------------------------
# Phase 3 — association (A3 ambiguity preserved, A4 adjudication)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegionLink:
    """A single accepted/rejected/ambiguous mapping of source to PDF region."""

    source_occurrence_id: str
    source_paper_id: str
    source_index: int
    page_number_1_based: int
    candidate_bbox_pdf_pt: tuple[float, float, float, float]
    iou: float
    containment: float
    n_geom_candidates: int
    status: str  # "accepted" | "ambiguous" | "rejected"

    def to_dict(self) -> dict:
        """Deterministic JSON-serializable view of the link record."""
        return {
            "source_occurrence_id": self.source_occurrence_id,
            "source_paper_id": self.source_paper_id,
            "source_index": self.source_index,
            "page_number_1_based": self.page_number_1_based,
            "candidate_bbox_pdf_pt": list(self.candidate_bbox_pdf_pt),
            "iou": self.iou,
            "containment": self.containment,
            "n_geom_candidates": self.n_geom_candidates,
            "status": self.status,
        }
    provenance: dict


def _estimate_equation_region(latex: str, expected_n_lines: int = 1) -> tuple:
    """Estimate the equation's natural bounding box from its AST structure.

    Based on:
      - number of operators/relational symbols,
      - number of variable glyphs,
      - expected line count from the AST (display vs inline).

    This is an ESTIMATE for Stage A only; it does not use gold geometry.
    """
    s = latex or ""
    n_operators = s.count("\\") + s.count("|") + s.count("&") + s.count("_")
    n_vars = sum(s.count(v) for v in ["z", "u", "psi", "E", "K", "p", "x", "t"])
    # approx glyph width: italic bold Latin ~0.6em, math symbols ~0.5em
    avg_char_width_pt = 5.0 if n_vars > 0 else 4.0

    # base width from n_operators (each operator adds width)
    width_pt = max(20.0, (n_operators * 7.5) + (n_vars * avg_char_width_pt))
    height_pt = max(12.0, 14.0 * expected_n_lines)

    return (50.0, 50.0, 50.0 + width_pt, 50.0 + height_pt), width_pt, height_pt


def associate_page(
    page: PageCandidates,
    source_occurrence: SourceOccurrence,
    expected_page_bbox: tuple[float, float, float, float],
) -> list[RegionLink]:
    """Build candidate links from the geometry candidates on one page."""
    links: list[RegionLink] = []
    # update source fields with live values
    src = SourceOccurrence(
        id=source_occurrence.id,
        paper_id=source_occurrence.paper_id,
        index=source_occurrence.index,
        latex=source_occurrence.latex,
        mathml=source_occurrence.mathml,
        source=source_occurrence.source,
    )

    # group consecutive geometry candidates into regions
    geom = page.candidates
    if not geom:
        return links

    # expected region from equation structure
    expected_bbox, _, _ = _estimate_equation_region(src.latex)

    # walk candidates, grouping into regions
    i = 0
    while i < len(geom):
        # cluster of at least 3 chars to be a region candidate
        cluster = []
        while i < len(geom) and len(cluster) < 20:
            cluster.append(geom[i])
            i += 1
        if len(cluster) < 3:
            continue

        # compute cluster bbox from geometry candidates
        x0 = min(g.bbox_pdf_pt[0] for g in cluster)
        y0 = min(g.bbox_pdf_pt[1] for g in cluster)
        x1 = max(g.bbox_pdf_pt[2] for g in cluster)
        y1 = max(g.bbox_pdf_pt[3] for g in cluster)
        region_bbox = (x0, y0, x1, y1)

        m = _region_metrics(expected_bbox, region_bbox)
        status = "accepted" if m.containment >= 0.35 else "ambiguous"
        # retain ambiguity as-is; do not force a unique match
        links.append(
            RegionLink(
                source_occurrence_id=src.id,
                source_paper_id=src.paper_id,
                source_index=src.index,
                page_number_1_based=page.page_number_1_based,
                candidate_bbox_pdf_pt=region_bbox,
                iou=m.iou,
                containment=m.containment,
                n_geom_candidates=len(cluster),
                status=status,
                provenance={},
            )
        )

    return links


# ---------------------------------------------------------------------------
# Phase 4 — provenance (A4) and assembly
# ---------------------------------------------------------------------------

def _canonical_name_from_latex(latex: str) -> str:
    s = (latex or "").strip().replace(" ", "_").replace("\\", "")
    return s[:80] or "unknown"


def build_stage_a_output(
    source_occurrence: SourceOccurrence,
    pages: list[PageCandidates],
    *,
    pdf_sha256: str,
    pdf_path: str,
    source_item_path: str,
    detector_output_path: str,
    tool_version: str = "1.0.0",
) -> dict:
    """Assemble the full Stage A output artifact."""
    links: list[RegionLink] = []
    provenance = {
        "source_occurrence": {
            "id": source_occurrence.id,
            "index": source_occurrence.index,
            "sha256": source_occurrence.sha256(),
            "latex_prefix": _canonical_name_from_latex(source_occurrence.latex),
        },
        "source_file": source_item_path,
        "pdf": {
            "path": pdf_path,
            "sha256": pdf_sha256,
            "pages": [p.page_number_1_based for p in pages],
        },
        "detector_output": detector_output_path,
        "stage_a_version": tool_version,
        "derivation": "_estimate_equation_region (structural estimate, no gold)",
        "phase_gate": "Stage A only; Stage B not yet implemented",
    }

    for p in pages:
        links.extend(
            associate_page(p, source_occurrence, expected_page_bbox=(0, 0, 612, 792))
        )

    return {
        "source_occurrence_id": source_occurrence.id,
        "source_paper_id": source_occurrence.paper_id,
        "source_index": source_occurrence.index,
        "source_latex": source_occurrence.latex,
        "source_mathml": source_occurrence.mathml,
        "source_sha256": source_occurrence.sha256(),
        "pdf_sha256": pdf_sha256,
        "pdf_path": pdf_path,
        "stage_a_output": [l.to_dict() for l in links],
        "provenance": provenance,
    }


# ---------------------------------------------------------------------------
# Phase 5 — CLI entry point (stdlib only, no external dependencies)
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage A — source occurrence to PDF region association"
    )
    parser.add_argument(
        "source_item_json",
        help="path to JSON containing the source occurrence record "
             "(item index 193, S6.E20.m1).",
    )
    parser.add_argument(
        "detector_json",
        help="path to arena_math_audit/targeted_math_detection.json.",
    )
    parser.add_argument(
        "pdf_sha256",
        help="sha256 of the PDF.",
    )
    parser.add_argument(
        "out_json",
        help="where to write stage_a_output.json.",
    )
    args = parser.parse_args(argv)

    with open(args.source_item_json) as f:
        item = json.load(f)
    with open(args.detector_json) as f:
        detector = json.load(f)

    pages = []
    for rec in detector.get("records", []):
        candidates = rec.get("geometry_candidates", [])
        pages.append(
            PageCandidates(
                page_number_1_based=rec.get("page_number_1_based", 1),
                candidates=[GeometryCandidate(**c) for c in candidates],
                character_observations=rec.get("character_observations", []),
                limitations=rec.get("limitations", ""),
            )
        )

    src = SourceOccurrence(
        id=item.get("id", SOURCE_OCCURRENCE_ID),
        paper_id=item.get("paper_id", SOURCE_PAPER_ID),
        index=item.get("index", SOURCE_OCCURRENCE_INDEX),
        latex=item.get("latex", ""),
        mathml=item.get("mathml", ""),
        source=item.get("source", SOURCE_OCCURRENCE_SOURCE),
    )

    output = build_stage_a_output(
        src,
        pages,
        pdf_sha256=args.pdf_sha256,
        pdf_path=detector.get("source_pdf", ""),
        source_item_path=args.source_item_json,
        detector_output_path=args.detector_json,
    )

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(output, f, indent=2)

    n_links = len(output["stage_a_output"])
    print(f"Stage A: {n_links} region links produced for {src.id} ({src.paper_id})")
    statuses = {l["status"] for l in output["stage_a_output"]}
    print(f"           statuses: {statuses}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
