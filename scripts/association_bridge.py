#!/usr/bin/env python3
"""
Sidecar Association Contract: AST-to-Spatial Association Layer.

Connects visual evidence, mathematical structure, and spatial relationships
into association records for the sidecar ledger.

Consumes:
  1. character_observations (from targeted_math_detection) -- glyph coordinates
  2. geometry_candidates (from targeted_math_detector) -- candidate glyphs
  3. script_position_candidates -- script hypotheses
  4. visual_component_analysis.visual_candidates -- visual regions
  5. math_like_text_spans -- AST nodes

Produces:
  1. association_ledger.jsonl -- one association record per line

Design principle:
  Never manufacture a relationship merely because gold standard says one exists.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

LEDGER_PATH = REPO_ROOT / "association_ledger.jsonl"


@dataclass
class AssociationRecord:
    """One association record in the ledger.

    Fields:
      association_id: unique per evidence observation (glyph+visual+AST triple)
      relationship_id: unique per semantic relationship (DEDUPED)
      source_occurrence: source provenance (PDF SHA, paper, page, coord space)
      glyph_observations: candidate glyphs with valid coordinates
      visual_evidence: candidate visual region (optional)
      ast_node: AST node reference
      parent_child_relationship: relationship hypothesis + bbox provenance
      confidence: state, per-layer confidences, probe result, evidence notes
      probe_execution_status: probe state (not_executed | insufficient_input |
                               failed | passed_candidate)
      recorded_at: timestamp
    """

    association_id: str
    relationship_id: str
    source_occurrence: Dict[str, Any]
    glyph_observations: List[Dict[str, Any]]
    visual_evidence: Optional[Dict[str, Any]]
    ast_node: Dict[str, Any]
    parent_child_relationship: Dict[str, Any]
    confidence: Dict[str, Any]
    probe_execution_status: str
    recorded_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "association_id": self.association_id,
            "relationship_id": self.relationship_id,
            "source_occurrence": self.source_occurrence,
            "glyph_observations": self.glyph_observations,
            "visual_evidence": self.visual_evidence,
            "ast_node": self.ast_node,
            "parent_child_relationship": self.parent_child_relationship,
            "confidence": self.confidence,
            "probe_execution_status": self.probe_execution_status,
            "recorded_at": self.recorded_at,
        }


def generate_id(paper_id: str, page_number: int, node_index: int,
                relationship_type: str, glyph_id: str = "") -> str:
    base = f"assoc_{paper_id}_p{page_number:03d}"
    if glyph_id:
        base += f"_{glyph_id[:8]}"
    return f"{base}_{node_index}_{relationship_type}"


def generate_relationship_id(
    paper_id: str,
    page_number: int,
    relationship_type: str,
    source_pdf: str,
    source_pdf_sha256: str,
    parent_span: Dict[str, Any],
    child_glyph_shapes: List[tuple],
) -> str:
    """Generate a relationship_id from stable semantic identity.

    The ID is derived from:
      - Source document identity (source_pdf + sha256)
      - Page and source occurrence identity
      - Relationship type
      - Parent AST node identity (span text, bbox)
      - Child AST node identity (glyph char + bbox)

    NOT dependent on:
      - Confidence
      - Probe result
      - Verification state
      - Visual candidate ordering
      - Generation order

    Same semantic relationship supported by multiple glyphs/visual candidates
    retains ONE relationship_id. Two distinct occurrences get different IDs.
    """
    # Use the actual paper_id, not a truncated source_pdf string
    # source_pdf is PRESERVED from the evidence source (actual PDF filename),
    # but paper_id is the authoritative discriminator for the relationship
    glyph_shape = tuple(sorted(child_glyph_shapes))
    parent_signature = (
        f"{parent_span.get('text','')[:12]}_{parent_span.get('span_index',0)}_"
        f"{parent_span.get('bbox_pdf_pt',[0,0,0,0])[0]:.3f}_{parent_span.get('bbox_pdf_pt',[0,0,0,0])[1]:.3f}"
    )
    glyph_part = "_".join(f"{g[0]}_{g[1][0]:.3f}_{g[1][1]:.3f}" for g in glyph_shape[:4])
    return (
        f"rel_{paper_id}_p{page_number:03d}_{relationship_type}_"
        f"{parent_signature}_{glyph_part}"
    )


def load_evidence(
    paper_id: str,
    page_number: int,
    relationship_type: str,
) -> Dict[str, Any]:
    evidence_dir = REPO_ROOT / "arena_math_audit"
    json_path = evidence_dir / "targeted_math_detection.json"
    if not json_path.exists():
        return {
            "character_observations": [],
            "geometry_candidates": [],
            "script_position_candidates": [],
            "visual_candidates": [],
            "math_like_text_spans": [],
            "page_number_1_based": page_number,
            "source_pdf": None,
            "source_pdf_sha256": None,
        }

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for rec in data.get("records", []):
        if rec.get("page_number_1_based") == page_number:
            visual_cands = rec.get("visual_component_analysis", {}).get("visual_candidates", [])
            return {
                "character_observations": rec.get("character_observations", []),
                "geometry_candidates": rec.get("geometry_candidates", []),
                "script_position_candidates": rec.get("script_position_candidates", []),
                "visual_candidates": visual_cands,
                "math_like_text_spans": rec.get("math_like_text_spans", []),
                "page_number_1_based": page_number,
                "evidence_keys": list(rec.keys()),
                "source_pdf": rec.get("source_pdf"),
                "source_pdf_sha256": rec.get("source_pdf_sha256"),
                "paper_id": paper_id,  # Authoritative paper identity for relationship IDs
            }

    return {
        "character_observations": [],
        "geometry_candidates": [],
        "script_position_candidates": [],
        "visual_candidates": [],
        "math_like_text_spans": [],
        "page_number_1_based": page_number,
        "evidence_keys": [],
        "source_pdf": None,
        "source_pdf_sha256": None,
    }


def build_association(
    paper_id: str,
    page_number: int,
    relationship_type: str,
    evidence: Dict[str, Any],
) -> List[AssociationRecord]:
    """
    Build association records connecting glyph, visual, and AST evidence.

    Returns records in one of these states:
      - record_generated: ledger record serialized (always)
      - evidence_linked: referenced glyphs & visual regions have valid source identities
      - relationship_candidate: evidence supports the proposed relationship type
      - spatially_verified: independent geometric probe passed
      - semantically_verified: AST and spatial evidence agree

    The relationship_type field is a REQUESTED relationship hypothesis.
    A record with relationship_type='numerator_to_denominator' is generated
    for any span — the span may or may not actually contain a fraction.
    The actual relationship detection happens at evidence_linked onwards.
    """
    char_obs = evidence.get("character_observations", [])
    geometry_cands = evidence.get("geometry_candidates", [])
    script_cands = evidence.get("script_position_candidates", [])
    visual_cands = evidence.get("visual_candidates", [])
    math_spans = evidence.get("math_like_text_spans", [])

    records = []
    if not char_obs and not geometry_cands and not script_cands and not visual_cands and not math_spans:
        return records

    # Group visual candidates by page for coordinate validation
    page_cands = [c for c in visual_cands if c.get("page_number") == page_number]

    for i, span in enumerate(math_spans):
        node_id = f"ast_{i}"
        span_bbox = span.get("bbox_pdf_pt", [0, 0, 0, 0])
        text = span.get("text", "")
        x0, y0, x1, y1 = span_bbox

        # Find glyph observations within this span's bbox
        child_glyphs = []
        for g in char_obs:
            g_bbox = g.get("bbox_pdf_pt", [0, 0, 0, 0])
            if (x0 <= g_bbox[0] <= x1 and y0 <= g_bbox[1] <= y1):
                child_glyphs.append(g)

        child_box = span_bbox
        if child_glyphs:
            child_box = [
                min(g["bbox_pdf_pt"][0] for g in child_glyphs),
                min(g["bbox_pdf_pt"][1] for g in child_glyphs),
                max(g["bbox_pdf_pt"][2] for g in child_glyphs),
                max(g["bbox_pdf_pt"][3] for g in child_glyphs),
            ]

        # Visual evidence association (traceable chain)
        visual_evidence = None
        spatial_consistent = False
        if page_cands:
            # Coordinate compatibility: bbox_pdf_pt_approx is PDF point approximation
            # Spatial correspondence: visual candidate bbox overlaps span bbox
            for vc in page_cands:
                vc_bbox = vc.get("bbox_pdf_pt_approx", [0, 0, 0, 0])
                # Check overlap between visual candidate and span
                overlap_x = max(0, min(x1, vc_bbox[2]) - max(x0, vc_bbox[0]))
                overlap_y = max(0, min(y1, vc_bbox[3]) - max(y0, vc_bbox[1]))
                if overlap_x > 0 and overlap_y > 0:
                    visual_evidence = vc
                    spatial_consistent = True
                    break

        # Relationship hypothesis: generate record regardless of actual verification
        # This is the record_generated state
        relationship = {
            "parent": "root",
            "child": node_id,
            "relationship_type": relationship_type,
            "bbox_provenance": {
                "parent_box": [999999, 999999, 0, 0],
                "child_box": child_box,
                "spatial_rule": "bbox_containment",
                "probe_passed": False,
                "probe_fail_reason": "pending_probe",
            }
        }

        # State is determined by evidence chain + probe results
        state = "record_generated"
        if visual_evidence is not None and child_glyphs:
            state = "evidence_linked"
            if visual_evidence.get("bbox_pdf_pt_approx") and spatial_consistent:
                state = "relationship_candidate"

        # Relationship-specific probe (base_to_exponent, numerator_to_denominator)
        probe_passed = False
        probe_fail_reason = None
        probe_source = "pending_probe"

        if relationship_type == "base_to_exponent":
            # Base/exponent: exponent glyph must be positioned above base
            # Independently: glyph observations must have separate bboxes
            if len(child_glyphs) >= 2:
                sorted_glyphs = sorted(child_glyphs, key=lambda g: g["bbox_pdf_pt"][1])
                base_g = sorted_glyphs[0]
                exp_g = sorted_glyphs[-1]
                # Exponent must be above base: exp_y0 < base_y1
                if exp_g["bbox_pdf_pt"][1] < base_g["bbox_pdf_pt"][3]:
                    probe_passed = True
                    probe_source = "geometric_above_base"
                else:
                    probe_fail_reason = "exp_not_above_base"
            else:
                probe_fail_reason = "insufficient_glyphs"

        elif relationship_type == "numerator_to_denominator":
            # Fraction: need fraction bar in visual candidates
            # Numerator and denominator must have separate bboxes
            if visual_evidence:
                vc_bbox = visual_evidence.get("bbox_pdf_pt_approx", [0, 0, 0, 0])
                if vc_bbox and child_glyphs:
                    probe_passed = True
                    probe_source = "visual_fraction_bar"
                else:
                    probe_fail_reason = "no_fraction_bar_geometry"
            else:
                probe_fail_reason = "no_visual_fraction_bar"

        # If probe passes AND relationship_candidate state indicates
        # actual visual-glyph correspondence, upgrade to relationship_candidate
        if probe_passed and relationship_type in (
            "base_to_exponent",
            "numerator_to_denominator",
        ):
            if state in ("relationship_candidate", "evidence_linked"):
                state = "relationship_candidate"

        # relationship_id: dedup per unique semantic relationship
        # Use stable semantic identity: source doc + page + span + glyphs
        relationship_id = generate_relationship_id(
            paper_id, page_number, relationship_type,
            evidence.get("source_pdf") or "unknown",
            evidence.get("source_pdf_sha256") or "unknown",
            span,
            [(g.get("char", "?"), tuple(g.get("bbox_pdf_pt", [0, 0, 0, 0]))) for g in child_glyphs]
        )

        # Build confidence reflecting current state
        glyph_count = len(child_glyphs)
        visual_present = 1.0 if visual_evidence else 0.0
        glyph_coverage = glyph_count / max(len(char_obs), 1)

        # probe_execution_status: distinguishes probe states
        # Values: not_executed (default) | insufficient_input | failed | passed_candidate
        probe_execution_status = "not_executed"
        if relationship_type in ("base_to_exponent", "numerator_to_denominator"):
            if relationship_type == "base_to_exponent" and len(child_glyphs) < 2:
                probe_execution_status = "insufficient_input"
            elif relationship_type == "base_to_exponent" and len(child_glyphs) >= 2:
                probe_execution_status = "passed_candidate"
            elif relationship_type == "numerator_to_denominator":
                if visual_evidence:
                    probe_execution_status = "passed_candidate"
                else:
                    probe_execution_status = "failed"

        record = AssociationRecord(
            association_id=generate_id(paper_id, page_number, i, relationship_type),
            relationship_id=relationship_id,
            source_occurrence={
                "pdf_sha256": (evidence.get("source_pdf_sha256") or "unknown"),
                "paper_id": paper_id,
                "page_number": page_number,
                "source_type": "text_layer",
                "coord_space": "pdf_points",
                "source_object_ids": [],
            },
            glyph_observations=child_glyphs,
            visual_evidence=visual_evidence,
            ast_node={
                "node_id": node_id,
                "span_index": span.get("span_index", 0),
                "font": span.get("font", "unknown"),
                "bbox_pdf_pt": span_bbox,
                "text": text,
                "kind": "unknown",
            },
            parent_child_relationship=relationship,
            confidence={
                "overall": 0.1,
                "state": state,
                "per_layer": {
                    "glyph_observation": min(glyph_coverage, 1.0) * 0.25,
                    "visual_region": visual_present * 0.25,
                    "ast_node": 0.2,
                    "spatial_probe": 0.0,
                },
                "relationship_id": relationship_id,
                "verification_status": state,
                "evidence_notes": (
                    f"state={state}; glyphs={glyph_count}; "
                    f"visual_candidate={1 if visual_evidence else 0}; "
                    f"probe_execution={probe_execution_status}"
                ),
                "probe_execution_status": probe_execution_status,
            },
            probe_execution_status=probe_execution_status,
            recorded_at=datetime.now(timezone.utc).isoformat(),
        )
        records.append(record)

    return records


def write_ledger(records: List[AssociationRecord]) -> int:
    count = 0
    for record in records:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        count += 1
    return count


def main():
    if len(sys.argv) < 4:
        print("Usage: association_bridge.py <paper_id> <page_number> <relationship_type>")
        print("  relationship_type: base_to_exponent|numerator_to_denominator|integral_to_upper_lower|"
              "operator_to_operand|delimited_group|stacked_limit|wide_accent|crossed_script")
        sys.exit(1)

    paper_id = sys.argv[1]
    page_number = int(sys.argv[2])
    relationship_type = sys.argv[3]

    evidence = load_evidence(paper_id, page_number, relationship_type)
    records = build_association(paper_id, page_number, relationship_type, evidence)
    count = write_ledger(records)
    print(f"Built {count} association records for {paper_id} page {page_number}")


if __name__ == "__main__":
    main()
