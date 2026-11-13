#!/usr/bin/env python3
"""
Test the association bridge against the actual KING-WEN-I-CHING-IMMUTABLE-TABLES
repo data. This is a runbook for the sidecar association contract.

Run: python scripts/test_association_bridge.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from association_bridge import AssociationRecord, generate_id, load_glyph_observations, \
    load_visual_regions, load_ast_nodes, build_node_association, write_ledger

print("=" * 60)
print("Association Bridge Test Suite")
print("=" * 60)

# Clear ledger before test
from association_bridge import LEDGER_PATH
if LEDGER_PATH.exists():
    LEDGER_PATH.unlink()

# Test 1: Generate assertion
print("\n[TEST 1] Generate association ID")
test_id = generate_id("1212.0957", 8, "Fraction")
print(f"  Expected pattern: assoc_1212.0957_p008_Fraction")
print(f"  Got: {test_id}")
assert "assoc_1212.0957_p008_Fraction" in test_id
print("  PASS")

# Test 2: Association builder with mock data
print("\n[TEST 2] Build association with mock data")
glyphs = [
    {"unicode_char": "x", "pdf_bbox": [100, 200, 110, 210]},
    {"unicode_char": "2", "pdf_bbox": [115, 160, 125, 170]},  # superscript above
]
node = {
    "node_id": "Fraction",
    "unicode_char": "2",  # exponent
    "parent_child_relationship": {"relationship_type": "base_to_exponent"},
}
regions = [
    {"bbox": [95, 185, 130, 215], "confidence": 0.9}
]
record = build_node_association("1212.0957", 8, node, glyphs, regions)
assert record is not None
assert record.confidence["verification_status"] == "verified"
assert record.confidence["overall"] > 0.5
print(f"  ASC: {record.association_id}")
print(f"  Status: {record.confidence['verification_status']}")
print(f"  Overall: {record.confidence['overall']:.3f}")
print(f"  Glyph count: {len(record.glyph_observations)}")
print("  PASS")

# Test 3: Test run_spatial_probe for base_to_exponent
print("\n[TEST 3] Spatial probe: base_to_exponent")
from association_bridge import run_spatial_probe
glyphs2 = [
    {"unicode_char": "2", "pdf_bbox": [115, 160, 125, 170]},  # exponent above base
]
node2 = {
    "unicode_char": "2",
    "parent_child_relationship": {"relationship_type": "base_to_exponent"},
}
region2 = {"bbox": [95, 185, 130, 215]}
probe = run_spatial_probe(node2, region2, glyphs2)
print(f"  probe_passed={probe['probe_passed']}")
print(f"  probe_fail_reason={probe['probe_fail_reason']}")
print(f"  score={probe['score']}")
assert probe["probe_passed"] == True
print("  PASS")

# Test 4: Test ledger writing
print("\n[TEST 4] Write ledger and read back")
records = [
    AssociationRecord(
        association_id="test_001",
        source_occurrence={"pdf_sha256": "abc123", "paper_id": "test", "page_number": 1},
        glyph_observations=[{"unicode_char": "x", "pdf_bbox": [100, 200, 110, 210]}],
        visual_evidence={"bbox": [90, 190, 120, 210], "confidence": 0.8},
        ast_node={"node_id": "test", "kind": "identifier"},
        parent_child_relationship={"parent": "root", "child": "test", "relationship_type": "containment"},
        confidence={"overall": 0.8, "per_layer": {"glyph_observation": 1.0, "visual_region": 0.8, "ast_node": 1.0, "spatial_probe": 0.9}, "verification_status": "verified"},
        recorded_at="2026-11-12T14:30:00Z",
    )
]
count = write_ledger(records)
assert count == 1
# Read back and verify
from pathlib import Path
ledger = []
for line in Path("association_ledger.jsonl").read_text(encoding="utf-8").splitlines():
    ledger.append(json.loads(line))
assert len(ledger) == 1
assert ledger[0]["association_id"] == "test_001"
print(f"  Wrote {count} record, read back {len(ledger)}")
print("  PASS")

# Test 5: Test verification status semantics
print("\n[TEST 5] Verification status semantics")
from association_bridge import build_node_association
glyphs3 = [
    {"unicode_char": "a", "pdf_bbox": [100, 200, 110, 210]},
]
node3 = {
    "node_id": "DelimitedGroup",
    "unicode_char": "a",
    "parent_child_relationship": {"relationship_type": "delimited_group"},
}
regions3 = []  # No visual regions — probe cannot run
record3 = build_node_association("1212.0957", 8, node3, glyphs3, regions3)
assert record3.confidence["verification_status"] == "unverified"
assert record3.confidence["per_layer"]["glyph_observation"] == 1.0
print(f"  Status: {record3.confidence['verification_status']}")
print("  PASS")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
