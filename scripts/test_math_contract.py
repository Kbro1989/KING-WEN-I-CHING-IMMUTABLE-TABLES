#!/usr/bin/env python3
"""
Contract tests — verify math_contract invariants.

Covers:
  1. validate_occurrence_set: complete, missing, extra, duplicate
  2. validate_record: status consistency, backend hash integrity
  3. ExprNode: serialization round-trip, post-construction mutation isolation
  4. extraction_hash: None vs "" distinction
  5. canonical_json determinism
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (
    ExprNode, SourceOccurrence, RecoveryRecord,
    validate_occurrence_set, validate_record,
    extraction_hash, canonical_json, hash_bytes,
    backend_input_hash, occurrence_key,
)

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}: {detail}")


print("=== Occurrence conservation ===")

# Complete set — no violations
src = ["a", "b", "c"]
rec = ["a", "b", "c"]
v = validate_occurrence_set(src, rec)
check("complete set passes", v == [], str(v))

# Missing record
v = validate_occurrence_set(["a", "b", "c"], ["a", "b"])
check("missing detected", len(v) == 1 and "Missing" in v[0], str(v))

# Extra record
v = validate_occurrence_set(["a", "b"], ["a", "b", "c"])
check("extra detected", len(v) == 1 and "Extra" in v[0], str(v))

# Duplicate source key
v = validate_occurrence_set(["a", "a", "b"], ["a", "b"])
check("duplicate source detected", any("Duplicate source" in x for x in v), str(v))

# Duplicate record key
v = validate_occurrence_set(["a", "b"], ["a", "a", "b"])
check("duplicate record detected", any("Duplicate recovery" in x for x in v), str(v))

# Empty sets
v = validate_occurrence_set([], [])
check("empty sets pass", v == [], str(v))


print("\n=== Record validation ===")

src_occ = SourceOccurrence(
    paper_id="2605.00155",
    paper_version="v1",
    source_locator="math[0]",
    occurrence_index=0,
    source_hash="abc123",
    latex="x = 1",
    mathml="<math>x=1</math>",
)

# Valid record
tree = ExprNode(kind="relation", value="=", children=(
    ExprNode(kind="identifier", value="x"),
    ExprNode(kind="number", value="1"),
))
bh = backend_input_hash(tree)
rec = RecoveryRecord(
    source=src_occ,
    parse_status="complete",
    structural_status="verified",
    canonical_tree=tree,
    backend_status="accepted",
    solution_status="solved",
    backend_input_hash=bh,
)
v = validate_record(rec)
check("valid record passes", v == [], str(v))

# Stale backend hash
rec_bad = RecoveryRecord(
    source=src_occ,
    parse_status="complete",
    canonical_tree=tree,
    backend_status="accepted",
    backend_input_hash="0000000000000000",
)
v = validate_record(rec_bad)
check("stale backend hash detected", any("hash mismatch" in x for x in v), str(v))

# Solution without backend
rec_no_backend = RecoveryRecord(
    source=src_occ,
    parse_status="complete",
    canonical_tree=tree,
    backend_status="not_attempted",
    solution_status="solved",
)
v = validate_record(rec_no_backend)
check("solution without backend detected", any("not_attempted" in x for x in v), str(v))


print("\n=== ExprNode immutability ===")

attrs = {"operator": "sum"}
node = ExprNode(kind="operator", value="∑", attributes=attrs)
attrs["operator"] = "CHANGED"
attrs["injected"] = True
check("post-construction mutation isolated", node.attributes == {"operator": "sum"},
      f"got {node.attributes}")

# Round-trip
d = node.to_dict()
node2 = ExprNode.from_dict(d)
check("round-trip preserves kind", node2.kind == node.kind)
check("round-trip preserves value", node2.value == node.value)
check("round-trip preserves attributes", node2.attributes == node.attributes)

# Nested round-trip
nested = ExprNode(kind="fraction", children=(
    ExprNode(kind="identifier", value="a"),
    ExprNode(kind="identifier", value="b"),
))
d = nested.to_dict()
nested2 = ExprNode.from_dict(d)
check("nested round-trip children count", len(nested2.children) == 2)
check("nested round-trip child kind", nested2.children[0].kind == "identifier")


print("\n=== extraction_hash None vs empty ===")

h_none = extraction_hash(None, None)
h_empty = extraction_hash("", "")
h_mixed = extraction_hash("x", None)
check("None != empty", h_none != h_empty, f"{h_none[:12]} == {h_empty[:12]}")
check("None != mixed", h_none != h_mixed)
check("deterministic", extraction_hash("a", "b") == extraction_hash("a", "b"))


print("\n=== canonical_json ===")

a = {"z": 1, "a": 2}
b = {"a": 2, "z": 1}
check("key order independent", canonical_json(a) == canonical_json(b))
check("compact separators", ", " not in canonical_json({"x": 1, "y": 2}))
check("unicode escaped", canonical_json({"k": "é"}) == '{"k":"\\u00e9"}')


print(f"\n{'=' * 40}")
print(f"PASS: {PASS}")
print(f"FAIL: {FAIL}")
if FAIL:
    sys.exit(1)
