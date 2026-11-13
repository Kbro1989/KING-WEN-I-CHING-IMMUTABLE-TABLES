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
    association_id: str
    source_occurrence: Dict[str, Any]
    glyph_observations: List[Dict[str, Any]]
    visual_evidence: Optional[Dict[str, Any]]
    ast_node: Dict[str, Any]
    parent_child_relationship: Dict[str, Any]
    confidence: Dict[str, Any]
    recorded_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "association_id": self.association_id,
            "source_occurrence": self.source_occurrence,
            "glyph_observations": self.glyph_observations,
            "visual_evidence": self.visual_evidence,
            "ast_node": self.ast_node,
            "parent_child_relationship": self.parent_child_relationship,
            "confidence": self.confidence,
            "recorded_at": self.recorded_at,
        }


def generate_id(paper_id: str, page_number: int, node_id: str) -> str:
    return f"assoc_{paper_id}_p{page_number:03d}_{node_id.replace(':', '_')[:20]}"


def load_glyph_observations(paper_id: str, page_number: int) -> List[Dict[str, Any]]:
    """Load glyph observations from spatial_syntactic_observer (placeholder)."""
    return []


def load_visual_regions(paper_id: str, page_number: int) -> List[Dict[str, Any]]:
    """Load visual regions from chroma_visual_reader (placeholder)."""
    return []


def load_ast_nodes(paper_id: str, page_number: int) -> List[Dict[str, Any]]:
    """Load AST nodes from structural_ast_extractor (placeholder)."""
    return []


def find_glyphs_for_node(node: Dict[str, Any], glyphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find glyph observations that support this AST node."""
    return [g for g in glyphs if g.get("unicode_char") == node.get("unicode_char")]


def find_region_for_node(node: Dict[str, Any], regions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find visual region that supports this AST node."""
    if not regions:
        return None
    return regions[0]


def extract_glyph_bbox(glyphs: List[Dict[str, Any]]) -> Optional[List[float]]:
    """Extract bounding box from a list of glyph observations."""
    if not glyphs:
        return None
    x0 = min(g["pdf_bbox"][0] for g in glyphs)
    y0 = min(g["pdf_bbox"][1] for g in glyphs)
    x1 = max(g["pdf_bbox"][2] for g in glyphs)
    y1 = max(g["pdf_bbox"][3] for g in glyphs)
    return [x0, y0, x1, y1]


def run_spatial_probe(node: Dict[str, Any], region: Dict[str, Any], glyphs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run geometric probe for a proposed parent-child relationship.
    Returns probe result regardless of outcome.
    """
    if not glyphs:
        return {
            "probe_passed": False,
            "probe_fail_reason": "no_glyph_coordinates",
            "score": 0.0
        }

    child_box = extract_glyph_bbox(glyphs)
    if not child_box:
        return {
            "probe_passed": False,
            "probe_fail_reason": "no_coordinates",
            "score": 0.0
        }

    parent_box = region.get("bbox", [])
    relationship_type = node.get("parent_child_relationship", {}).get("relationship_type", "containment")

    parent_center = [(parent_box[0] + parent_box[2]) / 2, (parent_box[1] + parent_box[3]) / 2]
    child_center = [(child_box[0] + child_box[2]) / 2, (child_box[1] + child_box[3]) / 2]

    if relationship_type == "base_to_exponent":
        if child_center[1] < parent_box[1]:
            return {"probe_passed": True, "probe_fail_reason": None, "score": 0.8}
        else:
            return {"probe_passed": False, "probe_fail_reason": "exponent_not_above_base", "score": 0.2}

    if relationship_type == "numerator_to_denominator":
        return {
            "probe_passed": False,
            "probe_fail_reason": "no_fraction_bar_geometry",
            "score": 0.0
        }

    parent_height = parent_box[3] - parent_box[1]
    probe_passed = (
        parent_box[0] <= child_box[0] and parent_box[2] >= child_box[2]
        and parent_box[1] <= child_box[1] and parent_box[3] >= child_box[3]
    )
    return {
        "probe_passed": probe_passed,
        "probe_fail_reason": None if probe_passed else "bbox_containment_failed",
        "score": 0.9 if probe_passed else 0.1
    }


def build_node_association(
    paper_id: str,
    page_number: int,
    node: Dict[str, Any],
    glyphs: List[Dict[str, Any]],
    regions: List[Dict[str, Any]]
) -> Optional[AssociationRecord]:
    """Build a single association record for one AST node."""
    glyph_obs = find_glyphs_for_node(node, glyphs)
    region = find_region_for_node(node, regions) if regions else None

    relationship = node.get("parent_child_relationship", {})
    relationship_type = relationship.get("relationship_type", "containment")

    record = AssociationRecord(
        association_id=generate_id(paper_id, page_number, node.get("node_id", "unknown")),
        source_occurrence={
            "pdf_sha256": "placeholder",
            "paper_id": paper_id,
            "page_number": page_number,
            "source_type": "text_layer",
        },
        glyph_observations=glyph_obs,
        visual_evidence=region,
        ast_node=node,
        parent_child_relationship={
            "parent": "root",
            "child": node.get("node_id", "unknown"),
            "relationship_type": relationship_type,
            "bbox_provenance": {
                "parent_box": region.get("bbox", []) if region else [],
                "child_box": extract_glyph_bbox(glyph_obs) if glyph_obs else [],
                "spatial_rule": relationship.get("spatial_rule"),
                "probe_passed": False,
                "probe_fail_reason": None,
            }
        },
        confidence={
            "overall": 0.0,
            "per_layer": {
                "glyph_observation": 0.0,
                "visual_region": 0.0,
                "ast_node": 0.0,
                "spatial_probe": 0.0,
            },
            "verification_status": "unverified",
            "evidence_notes": "",
        },
        recorded_at=datetime.now(timezone.utc).isoformat(),
    )

    record.confidence["per_layer"]["glyph_observation"] = len(glyph_obs) / max(len(glyphs), 1)

    if region:
        record.visual_evidence = region
        record.confidence["per_layer"]["visual_region"] = region.get("confidence", 0.0)

    if glyph_obs and region is not None:
        probe = run_spatial_probe(node, region, glyph_obs)
        record.parent_child_relationship["bbox_provenance"]["parent_box"] = region.get("bbox", []) if region else []
        record.parent_child_relationship["bbox_provenance"]["child_box"] = extract_glyph_bbox(glyph_obs)
        record.parent_child_relationship["bbox_provenance"]["spatial_rule"] = relationship.get("spatial_rule")
        record.parent_child_relationship["bbox_provenance"]["probe_passed"] = probe["probe_passed"]
        record.parent_child_relationship["bbox_provenance"]["probe_fail_reason"] = probe["probe_fail_reason"]
        record.confidence["per_layer"]["spatial_probe"] = probe["score"]
        record.confidence["overall"] = (
            record.confidence["per_layer"]["glyph_observation"] * 0.25
            + record.confidence["per_layer"]["visual_region"] * 0.25
            + record.confidence["per_layer"]["spatial_probe"] * 0.50
        )
        if probe["probe_passed"]:
            record.confidence["verification_status"] = "verified"
        elif probe["probe_fail_reason"]:
            record.confidence["verification_status"] = "unresolved"

    return record


def build_association(paper_id: str, page_number: int) -> List[AssociationRecord]:
    """Build association records for a single paper page."""
    glyphs = load_glyph_observations(paper_id, page_number)
    regions = load_visual_regions(paper_id, page_number)
    ast_nodes = load_ast_nodes(paper_id, page_number)

    records = []
    for node in ast_nodes:
        record = build_node_association(paper_id, page_number, node, glyphs, regions)
        if record:
            records.append(record)
    return records


def write_ledger(records: List[AssociationRecord]) -> int:
    """Append association records to the ledger file."""
    count = 0
    for record in records:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        count += 1
    return count


def main():
    if len(sys.argv) < 3:
        print("Usage: association_bridge.py <paper_id> <page_number>")
        sys.exit(1)

    paper_id = sys.argv[1]
    page_number = int(sys.argv[2])

    records = build_association(paper_id, page_number)
    count = write_ledger(records)
    print(f"Built {count} association records for {paper_id} page {page_number}")


if __name__ == "__main__":
    main()
