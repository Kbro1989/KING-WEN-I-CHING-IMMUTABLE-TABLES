#!/usr/bin/env python3
"""
Adversarial structural fixtures — stress the contract with hard cases.

Covers:
  1. Nested integrals with bounds and differentials
  2. Limits with approach conditions
  3. Relation-token identity (sim, approx, propto, to, cong, equiv)
  4. Repeated identical equations at different source locations
  5. Unsupported MathML nodes (must be preserved, not dropped)
  6. Empty and malformed expressions
  7. Multi-variable differentials (double/triple integrals)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (
    ExprNode, SourceOccurrence, RecoveryRecord,
    validate_occurrence_set, validate_record,
    backend_input_hash, occurrence_key,
    NODE_KINDS,
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


print("=== Nested integrals with bounds and differentials ===")

# ∫_0^∞ f(x) dx — single integral with bounds and differential
integral = ExprNode(
    kind="integral",
    value="∫",
    children=(
        ExprNode(kind="identifier", value="x"),
    ),
    attributes={
        "operator": "integral",
        "integrand": "f(x)",
        "lower": "0",
        "upper": "∞",
        "differentials": ["dx"],
        "variable": "x",
    },
)
check("integral node created", integral.kind == "integral")
check("integral has differentials", integral.attributes.get("differentials") == ["dx"])
check("integral has bounds", "lower" in integral.attributes and "upper" in integral.attributes)

# Round-trip preserves integral structure
d = integral.to_dict()
i2 = ExprNode.from_dict(d)
check("integral round-trip differentials", i2.attributes.get("differentials") == ["dx"])
check("integral round-trip bounds", i2.attributes.get("lower") == "0")

# Double integral: ∬ f(x,y) dx dy — two differentials
double_integral = ExprNode(
    kind="integral",
    value="∬",
    attributes={
        "operator": "double_integral",
        "integrand": "f(x,y)",
        "differentials": ["dx", "dy"],  # ORDER MATTERS
        "variables": ["x", "y"],
    },
)
check("double integral has ordered differentials", double_integral.attributes["differentials"] == ["dx", "dy"])
d = double_integral.to_dict()
di2 = ExprNode.from_dict(d)
check("double integral round-trip order preserved", di2.attributes["differentials"] == ["dx", "dy"])

# Triple integral
triple = ExprNode(
    kind="integral",
    value="∭",
    attributes={
        "operator": "triple_integral",
        "differentials": ["dx", "dy", "dz"],
        "variables": ["x", "y", "z"],
    },
)
check("triple integral differentials", triple.attributes["differentials"] == ["dx", "dy", "dz"])


print("\n=== Limits with approach conditions ===")

lim = ExprNode(
    kind="limit",
    value="lim",
    children=(ExprNode(kind="fraction", children=(
        ExprNode(kind="identifier", value="f"),
        ExprNode(kind="identifier", value="g"),
    )),),
    attributes={
        "variable": "x",
        "approach": "0",
        "direction": "both",
    },
)
check("limit has approach", lim.attributes.get("approach") == "0")
d = lim.to_dict()
l2 = ExprNode.from_dict(d)
check("limit round-trip approach", l2.attributes.get("approach") == "0")
check("limit round-trip direction", l2.attributes.get("direction") == "both")


print("\n=== Relation-token identity ===")

# Each relation must be preserved as a distinct type, never collapsed to "="
relations = {
    "=": "eq",
    "∼": "sim",
    "≈": "approx",
    "≃": "simeq",
    "≅": "cong",
    "→": "to",
    "≡": "equiv",
    "∝": "propto",
}

for symbol, rel_type in relations.items():
    node = ExprNode(kind="relation", value=symbol, attributes={"relation_type": rel_type})
    d = node.to_dict()
    n2 = ExprNode.from_dict(d)
    check(f"relation {symbol} preserved as {rel_type}", n2.attributes.get("relation_type") == rel_type)

# Two different relations must produce different hashes
eq_node = ExprNode(kind="relation", value="=", attributes={"relation_type": "eq"})
sim_node = ExprNode(kind="relation", value="∼", attributes={"relation_type": "sim"})
check("eq != sim hash", backend_input_hash(eq_node) != backend_input_hash(sim_node))


print("\n=== Repeated identical equations at different locations ===")

# Same LaTeX, different source locations — must have different occurrence keys
occ_a = SourceOccurrence(
    paper_id="2605.00155", paper_version="v1",
    source_locator="math[5]", occurrence_index=5,
    source_hash="hash_a", latex="E = mc^2", mathml="<math>E=mc^2</math>",
)
occ_b = SourceOccurrence(
    paper_id="2605.00155", paper_version="v1",
    source_locator="math[42]", occurrence_index=42,
    source_hash="hash_a", latex="E = mc^2", mathml="<math>E=mc^2</math>",
)
ka = occurrence_key(occ_a)
kb = occurrence_key(occ_b)
check("same equation different location = different keys", ka != kb)
check("same equation same source_hash", occ_a.source_hash == occ_b.source_hash)

# But same location = same key
occ_c = SourceOccurrence(
    paper_id="2605.00155", paper_version="v1",
    source_locator="math[5]", occurrence_index=5,
    source_hash="hash_a", latex="E = mc^2", mathml="<math>E=mc^2</math>",
)
check("same location = same key", occurrence_key(occ_a) == occurrence_key(occ_c))

# Conservation with repeated equations
src_keys = [occurrence_key(occ_a), occurrence_key(occ_b)]
rec_keys = [occurrence_key(occ_a), occurrence_key(occ_b)]
v = validate_occurrence_set(src_keys, rec_keys)
check("repeated equations conserved", v == [], str(v))


print("\n=== Unsupported MathML nodes ===")

# An unsupported node must be preserved with its source representation
unsupported = ExprNode(
    kind="unsupported",
    value="<mmultiscripts>...</mmultiscripts>",
    attributes={"source_tag": "mmultiscripts", "reason": "not in NODE_KINDS handler"},
)
check("unsupported node created", unsupported.kind == "unsupported")
d = unsupported.to_dict()
u2 = ExprNode.from_dict(d)
check("unsupported round-trip preserves value", u2.value == unsupported.value)
check("unsupported round-trip preserves reason", u2.attributes.get("reason") == unsupported.attributes.get("reason"))

# Record with unsupported nodes and partial parse
rec_partial = RecoveryRecord(
    source=occ_a,
    parse_status="partial",
    structural_status="lossy",
    canonical_tree=ExprNode(kind="group", children=(unsupported,)),
    unsupported_nodes=[{"tag": "mmultiscripts", "reason": "not handled"}],
    warnings=["mmultiscripts node preserved but not interpreted"],
)
v = validate_record(rec_partial)
check("partial record with unsupported nodes valid", v == [], str(v))


print("\n=== Empty and malformed expressions ===")

# Empty tree
empty = ExprNode(kind="group")
check("empty node created", empty.kind == "group")
d = empty.to_dict()
e2 = ExprNode.from_dict(d)
check("empty round-trip", e2.kind == "group" and len(e2.children) == 0)

# Record with failed parse
rec_failed = RecoveryRecord(
    source=occ_a,
    parse_status="failed",
    structural_status="unverified",
    canonical_tree=None,
)
v = validate_record(rec_failed)
check("failed record valid", v == [], str(v))

# Failed parse with tree = violation
rec_bad = RecoveryRecord(
    source=occ_a,
    parse_status="failed",
    canonical_tree=ExprNode(kind="identifier", value="x"),
)
v = validate_record(rec_bad)
check("failed with tree detected", any("failed" in x for x in v), str(v))


print("\n=== Node kind validation ===")

try:
    ExprNode(kind="nonexistent_kind")
    check("invalid kind rejected", False, "no error raised")
except ValueError:
    check("invalid kind rejected", True)

check("all integral kinds valid", "integral" in NODE_KINDS)
check("all differential kinds valid", "differential" in NODE_KINDS)
check("all sum kinds valid", "sum" in NODE_KINDS)
check("all limit kinds valid", "limit" in NODE_KINDS)


print(f"\n{'=' * 40}")
print(f"PASS: {PASS}")
print(f"FAIL: {FAIL}")
if FAIL:
    sys.exit(1)
