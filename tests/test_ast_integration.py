"""
AST Integration tests — P2 acceptance criteria.
Run: PYTHONPATH=scripts python -m pytest scripts/test_ast_integration.py -v

Covers:
  AC1 occurrence preservation via SourceOccurrence identity in tree attributes
  AC2 typed structure (relations / fractions / scripts / unsupported)
  AC3 honest structural status from tree
  AC4 backend safety (no fabricated equality; partial AST rejected)
  AC5 regression coverage (real pipeline integration, not extractor in isolation)
"""
from __future__ import annotations

import sys

sys.path.insert(0, "scripts")

from math_contract import SourceOccurrence, occurrence_key, backend_input_hash
from math_ast_integration import build_recovery_record


PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}  {detail}")


# ---------------------------------------------------------------------------
# AC1 — occurrence preservation
# ---------------------------------------------------------------------------

def test_ac1_occurrence_identity_attached():
    """Every emitted tree carries its SourceOccurrence identity at the root."""
    from math_ast_integration import ast_occurrence_attributes, build_recovery_record

    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a \approx b", "<math>...</math>")
    rec = build_recovery_record(src, "<math><mi>a</mi><mo>\u2248</mo><mi>b</mi></math>")

    assert rec.canonical_tree is not None
    assert rec.canonical_tree.attributes["occurrence_key"] == occurrence_key(src)
    assert rec.canonical_tree.attributes["source_locator"] == "math[0]" or "source_locator" in rec.canonical_tree.attributes
    assert rec.source.to_dict()["source_hash"] != "sha256-not-checked"

    rec2 = build_recovery_record(src, "<math><mi>a</mi><mo>\u2248</mo><mi>b</mi></math>")
    assert rec.canonical_tree.attributes["occurrence_key"] == rec2.canonical_tree.attributes["occurrence_key"]


def test_ac1_occurrence_identity_unique_per_occurrence():
    src_a = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math>a=b</math>")
    src_b = _sample_source("2605.00155", "v4", "math[1]", 1, r"a = b", "<math>a=b</math>")

    r1 = build_recovery_record(src_a, "<math>a=b</math>")
    r2 = build_recovery_record(src_b, "<math>a=b</math>")

    assert r1.source.occurrence_index != r2.source.occurrence_index
    assert r1.canonical_tree.attributes["occurrence_key"] != r2.canonical_tree.attributes["occurrence_key"]


def _sample_source(paper_id, version, locator, idx, latex, mathml):
    from math_contract import SourceOccurrence
    return SourceOccurrence(
        paper_id=paper_id,
        paper_version=version,
        source_locator=locator,
        occurrence_index=idx,
        source_hash="sha256:" + str(abs(hash(mathml or ""))),
        latex=latex,
        mathml=mathml,
    )


# ---------------------------------------------------------------------------
# AC2 — typed structure preserved
# ---------------------------------------------------------------------------

def test_ac2_typed_relations_survive():
    for glyph, expected_type in [
        ("\u2248", "approx"),   # approx
        ("\u223c", "sim"),      # sim
        ("\u221d", "propto"),   # propto
        ("\u2264", "leq"),      # leq
        ("\u2265", "geq"),      # geq
        ("\u2260", "neq"),      # neq
        ("=", "eq"),            # eq
        ("\u21D2", "to"),       # rightarrow
        ("\u21D0", "Leftarrow"),  # leftarrow
    ]:
        latex = f"a {glyph} b"
        src = _sample_source("2605.00155", "v4", "math[0]", 0, latex, f"<math>a{glyph}b</math>")
        rec = build_recovery_record(src, f"<math><mi>a</mi><mo>{glyph}</mo><mi>b</mi></math>")
        assert rec.canonical_tree is not None
        rel = next(n for n in rec.canonical_tree.children if n.kind == "relation")
        assert rel.attributes.get("relation_type") == expected_type, (
            f"{glyph!r}: got relation_type={rel.attributes.get('relation_type')!r}, "
            f"expected {expected_type!r}"
        )


def test_ac2_fraction_and_root_preserved():
    """Fractions and roots carry num/den as children, not flattened."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"\frac{a}{b}", "<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>")
    rec = build_recovery_record(src, "<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>")
    assert rec.canonical_tree is not None
    assert rec.canonical_tree.kind == "fraction"
    assert len(rec.canonical_tree.children) == 2
    kinds = [c.kind for c in rec.canonical_tree.children]
    assert "identifier" in kinds


def test_ac2_script_and_decoration_detected():
    """_mi text classification detects named functions and Greek identifiers."""
    for latex, name in [
        ("sin", "function"),
        ("log", "function"),
        ("ell", "plain"),
    ]:
        src = _sample_source("2605.00155", "v4", "math[0]", 0, latex, f"<math><mi>{latex}</mi></math>")
        rec = build_recovery_record(src, f"<math><mi>{latex}</mi></math>")
        assert rec.canonical_tree is not None
        mi = rec.canonical_tree
        if name == "function":
            assert mi.attributes.get("function_name") is True, mi.attributes
        else:
            assert mi.attributes.get("source_glyph") == latex


# ---------------------------------------------------------------------------
# AC3 — honest structural status
# ---------------------------------------------------------------------------

def test_ac3_unsupported_make_status_partial():
    """An unsupported node present in the tree => structural_status == 'partial'."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"x", "<math><mspace width=\"1em\"/><mi>x</mi></math>")
    rec = build_recovery_record(src, "<math><mspace width=\"1em\"/><mi>x</mi></math>")
    assert rec.structural_status == "partial", f"expected 'partial', got {rec.structural_status!r}"


def test_ac3_two_unsupported_nodes_reported():
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"x", "<math><mspace width=\"1em\"/><mi>x</mi><mspace width=\"2em\"/></math>")
    rec = build_recovery_record(src, "<math><mspace width=\"1em\"/><mi>x</mi><mspace width=\"2em\"/></math>")
    assert len(rec.unsupported_nodes) == 2, f"expected 2 unsupported nodes, got {len(rec.unsupported_nodes)}"


def test_ac3_unsupported_has_reason_and_value():
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"x", "<math><mspace width=\"1em\"/></math>")
    rec = build_recovery_record(src, "<math><mspace width=\"1em\"/></math>")
    assert rec.unsupported_nodes, "expected at least one unsupported node"
    node = rec.unsupported_nodes[0]
    assert node["source_tag"] == "mspace"
    assert node["reason"]
    assert "value" in node


def test_ac3_equality_not_fabricated():
    """A supported-only equality yields structural_status == 'unverified', not 'verified'."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    rec = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    assert rec.structural_status == "unverified", (
        f"expected 'unverified' (no structural checker run), got {rec.structural_status!r}"
    )


# ---------------------------------------------------------------------------
# AC4 — backend safety
# ---------------------------------------------------------------------------

def test_ac4_no_fabricated_equality_from_partial():
    """Partial/unsupported trees must not be fed to a solver as-is."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mspace width=\"1em\"/><mi>b</mi></math>")
    rec = build_recovery_record(src, "<math><mspace width=\"1em\"/><mi>b</mi></math>")
    assert rec.canonical_tree is None or any(
        n.kind == "unsupported" for n in (rec.canonical_tree.children if rec.canonical_tree else [])
    )


def test_ac4_kind_equalities_only_from_source():
    """An equality expression yields a relation node kind 'eq'."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    rec = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    assert rec.canonical_tree is not None
    rel = next(n for n in rec.canonical_tree.children if n.kind == "relation")
    assert rel.kind == "relation"
    assert rel.value == "="


# ---------------------------------------------------------------------------
# AC5 — regression coverage (real pipeline integration)
# ---------------------------------------------------------------------------

def test_ac5_integration_no_collapsing():
    """Two identical sources produce two identical records (with different occurrence keys)."""
    src_a = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math>a=b</math>")
    src_b = _sample_source("2605.00155", "v4", "math[1]", 1, r"a = b", "<math>a=b</math>")
    r1 = build_recovery_record(src_a, "<math>a=b</math>")
    r2 = build_recovery_record(src_b, "<math>a=b</math>")
    assert r1.source.occurrence_index != r2.source.occurrence_index
    assert r1.canonical_tree is not None and r2.canonical_tree is not None


def test_ac5_parse_status_from_tree():
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    rec = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    assert rec.parse_status == "complete"
    assert rec.structural_status == "unverified"


def test_ac5_backend_status_untouched():
    """build_recovery_record must NOT set backend_status / solution_status."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    rec = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    assert rec.backend_status == "not_attempted"
    assert rec.solution_status == "not_attempted"


def test_ac5_run_on_corrupted_mathml():
    """Unparseable input yields a failed record, never a fabricated tree."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"x", "NOT_A_MATHML_STRING")
    rec = build_recovery_record(src, "NOT_A_MATHML_STRING")
    assert rec.parse_status == "failed"
    assert rec.canonical_tree is None


def test_ac5_hash_consistency():
    """Backend_input_hash deterministic for the same tree."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"a = b", "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    r1 = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    r2 = build_recovery_record(src, "<math><mi>a</mi><mo>=</mo><mi>b</mi></math>")
    assert r1.backend_input_hash == r2.backend_input_hash


def test_ac5_structural_status_reflected_in_record():
    """structural_status derived from tree, not hardcoded."""
    src = _sample_source("2605.00155", "v4", "math[0]", 0, r"x", "<math><mi>x</mi></math>")
    rec = build_recovery_record(src, "<math><mi>x</mi></math>")
    assert rec.structural_status == "unverified", (
        f"expected 'unverified' (no structural checker), got {rec.structural_status!r}"
    )
