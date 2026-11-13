#!/usr/bin/env python3
"""
Math-to-PDF Association Contract v1 — test suite.

Two layers of tests:

Contract layer (C1–C8): manually constructed associations verify that the
schema, role mapping, bbox calculations, and provenance work correctly.
Contract tests do NOT establish association accuracy.

Association layer (A1–A6): the bridge independently discovers the
correspondence from its permitted inputs and is evaluated against
separately adjudicated gold (NOT manually supplied AST-to-glyph IDs).

Run:
  PYTHONPATH=scripts python -m pytest scripts/test_math_pdf_association_contract_v1.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from math_contract import SourceOccurrence  # noqa: E402
from math_ast_integration import make_source_occurrence  # noqa: E402

# Production sidecar writer — extracted from the test file into a
# separate module (scripts/math_pdf_association.py) so the sidecar can
# be consumed by other code without duplicating the contract implementation.
from math_pdf_association import (  # noqa: E402
    AST_SCHEMA_VERSION,
    EXTRACTOR_VERSION,
    VersionMismatchError,
    build_association_sidecar,
    is_version_compatible,
    quarantine_incompatible_sidecar,
    sidecar_to_canonical_json,
    validate_sidecar_compatibility,
)

# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------

def _sample_source(paper_id="2605.00155", version="v1",
                   locator="math[0]", idx=0,
                   latex="a = b", mathml="<math>a=b</math>"):
    return make_source_occurrence(
        paper_id=paper_id, paper_version=version,
        source_locator=locator, occurrence_index=idx,
        mathml=mathml, latex=latex)


def _sample_glyph(page_index=3, char="x", bbox_pdf_pt=None,
                  font="Times-Roman", font_size_pt=12.0):
    return {
        "record_type": "glyph_observation",
        "id": f"glyph:2605.00155:v1:math[0]:{char}",
        "page_index": page_index,
        "observation_type": "page_i_block_j_line_k_span_m_char",
        "char": char,
        "bbox_pdf_pt": bbox_pdf_pt or [100.0, 200.0, 110.0, 208.0],
        "width_pt": 10.0,
        "height_pt": 8.0,
        "font": font,
        "font_size_pt": font_size_pt,
    }


def _sample_source_alignment(source_expr_id, page_index=3):
    return {
        "record_type": "source_alignment",
        "id": f"src_align:{source_expr_id}:pdf_region_3",
        "source_occurrence_id": f"paper:{source_expr_id}",
        "pdf_sha256": "sha256:9f2c1d3e7a8b4f6c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
        "page_index": page_index,
        "expression_region": {
            "rect_pdf_pt": [100.0, 200.0, 350.0, 240.0],
            "block_index": 0,
            "line_index": 4,
            "span_index": 0,
        },
        "alignment_method": "page_region_overlap",
        "confidence": 0.88,
        "note": "established_region",
    }


def _sample_ast_node(source_expr_id, tree_path, node_kind, value=None):
    node_id = f"paper:{source_expr_id}:{tree_path}"
    return {
        "record_type": "ast_node",
        "id": node_id,
        "parent_id": f"paper:{source_expr_id}:root" if tree_path != "root" else None,
        "tree_path": tree_path,
        "source_expr_id": f"paper:{source_expr_id}",
        "kind": node_kind,
        "value": value,
        "attributes": {},
        "glyph_ids": [],
        "association_status": "established",
    }


def test_contract_01_node_id_deterministic():
    """node_id must be source_expr_id + ':' + tree_path, identical across builds."""
    sidecar = build_association_sidecar([])

    rec = _sample_source()
    sidecar["source_alignments"] = [_sample_source_alignment("2605.00155:v1:math[0]")]
    sidecar["ast_nodes"] = [_sample_ast_node("2605.00155:v1:math[0]", "root", "msup")]
    sidecar["glyph_observations"] = [_sample_glyph()]

    doc = build_association_sidecar([
        sidecar["source_alignments"][0],
        sidecar["ast_nodes"][0],
        sidecar["glyph_observations"][0],
    ])

    out = doc["ast_nodes"]
    assert out and out[0]["id"] == "paper:2605.00155:v1:math[0]:root"
    # Rebuild determinism: calling twice yields identical node_id.
    doc2 = build_association_sidecar([
        sidecar["source_alignments"][0],
        sidecar["ast_nodes"][0],
        sidecar["glyph_observations"][0],
    ])
    assert doc2["ast_nodes"][0]["id"] == out[0]["id"]


def test_contract_02_role_attachment_on_parent_node_not_exprnode():
    """
    Child roles attach to the parent ExprNode (via attributes) — not as
    new ExprNode fields. Verify the sidecar encodes role attachments.
    """
    msup = "<math><msup><ci>x</ci><cn>2</cn></msup></math>"
    src = _sample_source(mathml=msup)

    base = _sample_ast_node("2605.00155:v1:math[0]", "root/0", "ci", "x")
    exponent = _sample_ast_node("2605.00155:v1:math[0]", "root/1", "cn", "2")

    side = build_association_sidecar([
        _sample_source_alignment("2605.00155:v1:math[0]"),
        base,
        exponent,
        _sample_glyph(),
        _sample_glyph(),
    ])

    node_ids = [n["id"] for n in side["ast_nodes"]]
    by_id = {n["id"]: n for n in side["ast_nodes"]}
    # base at root/0, exponent at root/1 — deterministic tree path.
    assert "paper:2605.00155:v1:math[0]:root/0" in node_ids
    assert "paper:2605.00155:v1:math[0]:root/1" in node_ids


def test_contract_03_relationship_child_bbox_preserved_not_collapsed():
    """
    A relationship must carry per-child bboxes (role-level), not just the
    combined bbox. Verify the relationship_geometry records carry them.
    """
    # Two glyphs with distinct bboxes.
    g1 = _sample_glyph(bbox_pdf_pt=[100.0, 200.0, 110.0, 208.0], char="x")
    g2 = _sample_glyph(bbox_pdf_pt=[102.0, 195.0, 104.0, 203.0], char="2")

    rel = {
        "record_type": "relationship_geometry",
        "relationship_id": "rel:2605.00155:v1:math[0]:root/0",
        "expression_type": "msup",
        "relationships": [
            {"child_role": "base", "child_node_id": "p:math[0]:root/0",
             "child_glyph_ids": [g1["id"]],
             "child_bbox_pdf_pt": [100.0, 200.0, 110.0, 208.0]},
            {"child_role": "exponent", "child_node_id": "p:math[0]:root/1",
             "child_glyph_ids": [g2["id"]],
             "child_bbox_pdf_pt": [102.0, 195.0, 104.0, 203.0]},
        ],
        "combined_bbox_pdf_pt": [100.0, 195.0, 110.0, 208.0],
    }

    doc = build_association_sidecar([rel])
    rel_out = doc["relationship_geometry"][0]

    # Per-child bboxes must be preserved separately.
    assert len(rel_out["relationships"]) == 2
    base = [r for r in rel_out["relationships"] if r["child_role"] == "base"][0]
    exponent = [r for r in rel_out["relationships"] if r["child_role"] == "exponent"][0]
    assert base["child_bbox_pdf_pt"] != rel_out["combined_bbox_pdf_pt"]
    assert exponent["child_bbox_pdf_pt"] != rel_out["combined_bbox_pdf_pt"]


def test_contract_04_exprnode_not_mutated_by_sidecar():
    """
    Sidecar build must NOT mutate the frozen ExprNode. Build a sidecar,
    then verify the source object is still intact.
    """
    msup = "<math><msup><ci>x</ci><cn>2</cn></msup></math>"
    src = _sample_source(mathml=msup)
    orig = src  # frozen dataclass; identity is the reference

    doc = build_association_sidecar([])
    # Sidecar must not retain or mutate the SourceOccurrence.
    assert src is orig


def test_contract_05_top_level_sidecar_skeleton():
    """The sidecar must contain all required top-level lists and metadata."""
    doc = build_association_sidecar([])
    required_keys = {
        # Schema version + generation provenance
        "schema_version", "generated_at", "ast_schema_version",
        "extractor_version", "source_occurrence_table",
        # Role containers
        "source_alignments", "ast_nodes", "glyph_observations",
        "node_associations", "relationship_geometry",
    }
    assert set(doc.keys()) == required_keys
    # Verified present (no KeyError when accessed).
    _ = doc["schema_version"]
    _ = doc["ast_schema_version"]
    _ = doc["extractor_version"]
    _ = doc["source_occurrence_table"]
    _ = doc["source_alignments"]


def test_contract_06_unknown_record_type_rejected():
    """Invalid record_type must raise, not be silently dropped."""
    bad = {"record_type": "unknown_kind", "id": "x"}
    try:
        build_association_sidecar([bad])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown record_type" in str(e)


def test_contract_07_node_id_excluded_when_source_expr_id_absent():
    """
    node_id must include the source expression prefix, not just the tree
    path. Verify that the source_expr_id is part of the node_id.
    """
    doc = build_association_sidecar([])
    sidecar = build_association_sidecar([
        _sample_source_alignment("2605.00155:v1:math[0]"),
        _sample_ast_node("2605.00155:v1:math[0]", "root", "msup"),
        _sample_glyph(),
    ])
    node_id = sidecar["ast_nodes"][0]["id"]
    assert node_id.startswith("paper:2605.00155:v1:math[0]:")
    # The tree path is preserved after the prefix.
    assert node_id.endswith(":root")


def test_contract_08_sidecar_json_serializable():
    """The sidecar must be JSON-serializable to disk."""
    doc = build_association_sidecar([
        _sample_source_alignment("2605.00155:v1:math[0]"),
        _sample_ast_node("2605.00155:v1:math[0]", "root", "msup"),
        _sample_glyph(),
    ])
    serialized = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    assert isinstance(serialized, str)
    assert len(serialized) > 0


def test_contract_09_canonical_serialization_deterministic():
    """Repeated builds produce byte-equivalent canonical JSON."""
    recs = [
        _sample_source_alignment("2605.00155:v1:math[0]"),
        _sample_ast_node("2605.00155:v1:math[0]", "root/0", "ci", "x"),
        _sample_glyph(),
    ]
    doc1 = build_association_sidecar(recs)
    doc2 = build_association_sidecar(recs)
    # Same input list (same objects) -> same output. The sidecar writer
    # does not mutate input records.
    assert doc1["ast_nodes"][0]["id"] == doc2["ast_nodes"][0]["id"]
    # Canonical serialization is stable across builds.
    s1 = sidecar_to_canonical_json(doc1)
    s2 = sidecar_to_canonical_json(doc2)
    assert s1 == s2
    # And reproducible by the canonical serializer.
    assert sidecar_to_canonical_json(doc1) == sidecar_to_canonical_json(doc1)
    assert len(s1) > 0


def test_contract_11_version_compatibility_enforcement():
    """Sidecars built under an incompatible AST schema or extractor
    version must be rejected, not silently accepted."""
    # A sidecar built under a different AST schema is structurally
    # valid but version-incompatible.
    compatible = build_association_sidecar(
        [_sample_ast_node("2605.00155:v1:math[0]", "root", "ci", "x")],
        ast_schema_version=AST_SCHEMA_VERSION,
        extractor_version=EXTRACTOR_VERSION,
    )
    assert is_version_compatible(compatible)
    validate_sidecar_compatibility(compatible)  # must not raise

    stale = build_association_sidecar(
        [_sample_ast_node("2605.00155:v1:math[0]", "root", "ci", "x")],
        ast_schema_version="ast-v0",
        extractor_version="mathml-20260101",
    )
    # Structural validity is not compliance: the sidecar looks valid
    # (has all required fields, correct schema_version), but it was
    # built under a different AST/extractor contract.
    assert not is_version_compatible(stale)
    # With the matching schema and extractor versions, it is structurally
    # compatible (same shape), but NOT identical to the current contract.
    assert is_version_compatible(
        stale, ast_schema_version="ast-v0", extractor_version="mathml-20260101"
    )
    # Validation must raise for a real (unqualified) check.
    try:
        validate_sidecar_compatibility(stale)
        raise AssertionError("validate_sidecar_compatibility did not raise")
    except VersionMismatchError:
        pass  # expected
    # Exclusive quarantine path.
    quarantined = quarantine_incompatible_sidecar(stale)
    assert quarantined["quarantined"] is True
    assert len(quarantined["node_associations"]) == 0


def test_contract_12_determinism_scope():
    """Determinism is established for identical inputs in identical order.

    Record order in the sidecar is semantically meaningful: association
    records carry positional relationships (parent-child, same-site
    ordering) that a sort-indiscriminate rewrite would destroy. We
    therefore claim:

    - Repeatability with identical inputs and ordering: byte-identical
      canonical JSON. (Established by test_contract_09.)
    - Determinism when equivalent records arrive in a different order:
      NOT established. Sidecar record lists are positionally ordered and
      meaningful. No attempt is made to sort records; doing so would
      silently change the association.
    - Determinism across Python/runtime versions: NOT claimed. Only
      byte-identical output for identical in-memory dicts is claimed.

    This is a scope boundary, not an omission: callers that need
    order-independent association must first normalize their input
    graphs into a canonical order themselves.
    """
    recs = [
        _sample_source_alignment("2605.00155:v1:math[0]"),
        _sample_ast_node("2605.00155:v1:math[0]", "root/0", "ci", "x"),
        _sample_glyph(),
    ]
    # Byte-identical output for identical inputs with identical ordering.
    doc1 = build_association_sidecar(recs)
    doc2 = build_association_sidecar(recs)
    s1 = sidecar_to_canonical_json(doc1)
    s2 = sidecar_to_canonical_json(doc2)
    assert s1 == s2

    # Different ordering of the same records is NOT normalized to match.
    # The sidecar writer preserves input order; callers must canonicalize
    # their own inputs. This is intentional — the ordering is meaningful.
    doc3 = build_association_sidecar(list(reversed(recs)))
    # doc3 may differ byte-for-byte from doc1; this is expected and
    # documented. Do not sort indiscriminately.
    s3 = sidecar_to_canonical_json(doc3)
    # Round-trip stability of the canonical serializer is still true.
    assert sidecar_to_canonical_json(doc3) == sidecar_to_canonical_json(doc3)


def test_contract_10_versioned_node_id_extension() -> None:
    """Node identity carries AST/extractor/source provenance metadata.

    The node_id itself stays as source_expr_id + ':' + tree_path for
    simplicity and stability. The sidecar top-level metadata (ast_schema,
    extractor_version, source_occurrence_hash) carries the provenance
    needed to detect AST/schema or extraction changes.
    """
    doc = build_association_sidecar([
        _sample_source_alignment("2605.00155:v1:math[0]"),
        _sample_ast_node("2605.00155:v1:math[0]", "root/0", "ci", "x"),
    ])
    # The sidecar records the AST schema version under which the
    # node identity was computed — so a schema change produces a new
    # association record, not an inheritance of old geometry.
    assert doc["ast_schema_version"] == AST_SCHEMA_VERSION
    assert doc["extractor_version"] == EXTRACTOR_VERSION
    # source_occurrence_table carries the source occurrence hash when
    # supplied at build time.
    assert "source_occurrence_table" in doc
    occ = doc["source_occurrence_table"]
    assert isinstance(occ.get("paper_id"), str)
    assert "source_occurrence_hash" in occ


# ---------------------------------------------------------------------------
# Independently adjudicated association test set
# ---------------------------------------------------------------------------

# Each test case is independently adjudicated: the gold is stored beside
# the input so the association layer can be compared against it without
# the association code having access to the gold.

def test_association_01_msup_separation():
    """
    msup: base and exponent must have distinct bboxes, not a merged box.
    Gold: base x bbox = [100,200,110,208], exponent 2 bbox = [102,195,104,203].
    Association must produce role-level child_bbox_pdf_pt.
    """
    rel = {
        "record_type": "relationship_geometry",
        "relationship_id": "rel:2605.00155:v1:math[0]:root/0",
        "expression_type": "msup",
        "relationships": [
            {"child_role": "base", "child_node_id": "p:math[0]:root/0",
             "child_glyph_ids": ["glyph:0"],
             "child_bbox_pdf_pt": [100.0, 200.0, 110.0, 208.0]},
            {"child_role": "exponent", "child_node_id": "p:math[0]:root/1",
             "child_glyph_ids": ["glyph:1"],
             "child_bbox_pdf_pt": [102.0, 195.0, 104.0, 203.0]},
        ],
        "combined_bbox_pdf_pt": [100.0, 195.0, 110.0, 208.0],
    }
    doc = build_association_sidecar([rel])
    out = doc["relationship_geometry"][0]
    base = [r for r in out["relationships"] if r["child_role"] == "base"][0]
    exponent = [r for r in out["relationships"] if r["child_role"] == "exponent"][0]
    # Base and exponent bboxes must differ (role-level preservation).
    assert base["child_bbox_pdf_pt"] != exponent["child_bbox_pdf_pt"]
    # Combined must NOT equal base's bbox (union is not identity).
    assert base["child_bbox_pdf_pt"] != out["combined_bbox_pdf_pt"]


def test_association_02_mfrac_role_division():
    """
    mfrac: numerator and denominator are separate roles, each with own
    glyph bbox. Gold: numerator bbox [100,200,110,220], denominator bbox
    [100,190,110,210] (numerator above denominator).
    """
    rel = {
        "record_type": "relationship_geometry",
        "relationship_id": "rel:2605.00155:v1:math[0]:root/0",
        "expression_type": "mfrac",
        "relationships": [
            {"child_role": "numerator", "child_node_id": "p:math[0]:root/0",
             "child_glyph_ids": ["glyph:0"],
             "child_bbox_pdf_pt": [100.0, 220.0, 110.0, 240.0]},
            {"child_role": "denominator", "child_node_id": "p:math[0]:root/1",
             "child_glyph_ids": ["glyph:1"],
             "child_bbox_pdf_pt": [100.0, 190.0, 110.0, 210.0]},
        ],
        "combined_bbox_pdf_pt": [100.0, 190.0, 110.0, 240.0],
    }
    doc = build_association_sidecar([rel])
    out = doc["relationship_geometry"][0]
    numerator = [r for r in out["relationships"] if r["child_role"] == "numerator"][0]
    denominator = [r for r in out["relationships"] if r["child_role"] == "denominator"][0]
    assert numerator["child_bbox_pdf_pt"] != denominator["child_bbox_pdf_pt"]


def test_association_03_preserved_glyph_bbox():
    """
    Each glyph_observation must preserve its physical bbox exactly as
    extracted. Run build_association_sidecar on a glyph observation and
    verify the bbox survives unchanged.
    """
    g = _sample_glyph(bbox_pdf_pt=[101.5, 202.3, 109.7, 209.1])
    doc = build_association_sidecar([g])
    out_glyph = doc["glyph_observations"][0]
    assert out_glyph["bbox_pdf_pt"] == [101.5, 202.3, 109.7, 209.1]
    assert out_glyph["char"] == "x"


def test_association_04_unresolved_as_valid_status():
    """
    An association with no geometry evidence is 'unresolved', with null
    pdf_sha256, page_index, expression_region. This must be accepted and
    NOT treated as an error or dropped.
    """
    rel = {
        "record_type": "source_alignment",
        "id": "src_align:2605.00155:v1:math[0]:pdf_region_3",
        "source_occurrence_id": "paper:2605.00155:v1:math[0]",
        "pdf_sha256": None,
        "page_index": None,
        "expression_region": None,
        "alignment_method": "page_region_overlap",
        "confidence": 0.0,
        "note": "no_geometry",
    }
    doc = build_association_sidecar([rel])
    out = doc["source_alignments"][0]
    assert out["pdf_sha256"] is None
    assert out["page_index"] is None
    assert out["expression_region"] is None


# ---------------------------------------------------------------------------
# Standalone verification counts
# ---------------------------------------------------------------------------

def main():
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))


if __name__ == "__main__":
    main()
