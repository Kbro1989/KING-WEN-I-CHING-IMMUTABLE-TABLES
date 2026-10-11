#!/usr/bin/env python3
"""
AST INTEGRATION — bind the typed structural AST to the recovery contract.

P1 preserved relation identity in the recovered STRING. That is not enough:
a string cannot round-trip, cannot carry occurrence identity, and cannot tell
the difference between "no unsupported content" and "not yet checked".

This module is the ADDITIVE bridge between:
  - structural_ast_extractor.py  (MathML -> typed ExprNode tree)
  - math_contract.py             (SourceOccurrence, RecoveryRecord, statuses)

It builds ONE RecoveryRecord per source occurrence with a populated
canonical_tree, and derives structural_status HONESTLY from the tree:

  unsupported nodes present in the tree  -> "partial"   (never "verified")
  no unsupported nodes, tree built        -> "unverified" (structural fidelity
                                              of the walk is not proof of
                                              equivalence; equivalence needs a
                                              dedicated structural checker)
  tree could not be built                 -> parse_status="failed",
                                              canonical_tree stays None

DESIGN BOUNDARY (deliberate, per review):
  This module does NOT change solve_recovered(). The string recovery path
  stays intact. A tree -> solver-string conversion is a separate change that
  needs its own correctness tests before any solver consumes a typed tree.

OCCURRENCE IDENTITY:
  ExprNode does not carry occurrence_key as a field (see structural_ast_extractor.py
  docstring, which claimed otherwise). Identity is bound at the RECORD level via
  SourceOccurrence + occurrence_key(). This module makes that binding explicit
  and correct rather than relying on a document-order index.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from math_contract import (  # noqa: E402
    ExprNode,
    RecoveryRecord,
    SourceOccurrence,
    occurrence_key,
)
from structural_ast_extractor import extract_structural_ast  # noqa: E402

__all__ = [
    "iter_unsupported",
    "has_unsupported",
    "derive_structural_status",
    "collect_unsupported_nodes",
    "build_recovery_record",
    "build_records_from_corpus",
    "ast_occurrence_attributes",
]


# ---------------------------------------------------------------------------
# Tree traversal
# ---------------------------------------------------------------------------

def iter_nodes(node: ExprNode | None):
    """Yield every node in the tree, pre-order. None-safe."""
    if node is None:
        return
    yield node
    for child in node.children:
        yield from iter_nodes(child)


def iter_unsupported(tree: ExprNode | None) -> list[ExprNode]:
    """Return all kind == 'unsupported' nodes anywhere in the tree."""
    return [n for n in iter_nodes(tree) if n.kind == "unsupported"]


def has_unsupported(tree: ExprNode | None) -> bool:
    """True if the tree contains any unsupported node."""
    return bool(iter_unsupported(tree))


# ---------------------------------------------------------------------------
# Honest structural status
# ---------------------------------------------------------------------------

def derive_structural_status(tree: ExprNode | None) -> str:
    """
    Derive StructuralStatus from the canonical tree.

    Rules:
      - tree is None                 -> "corrupted" is NOT appropriate; the
                                         caller handles parse failure via
                                         parse_status. We return "unverified"
                                         and the caller must set parse_status.
      - any unsupported node present -> "partial"
                                         (source not fully covered — the
                                          contract's own definition of partial)
      - otherwise                    -> "unverified"
                                         (a successful walk does not prove
                                          structural EQUIVALENCE to the source;
                                          that requires a structural checker,
                                          which is deliberately not claimed here)

    Never returns "verified". "verified" is a claim this layer cannot make.
    """
    if tree is None:
        return "unverified"
    if has_unsupported(tree):
        return "partial"
    return "unverified"


def collect_unsupported_nodes(tree: ExprNode | None) -> list[dict[str, Any]]:
    """
    Materialize unsupported nodes as JSON-serializable records for
    RecoveryRecord.unsupported_nodes. Preserves the source representation.
    """
    out: list[dict[str, Any]] = []
    for node in iter_unsupported(tree):
        attrs = node.attributes or {}
        out.append({
            "source_tag": attrs.get("source_tag"),
            "reason": attrs.get("reason"),
            "value": node.value,
        })
    return out


# ---------------------------------------------------------------------------
# Occurrence binding on the tree
# ---------------------------------------------------------------------------

def ast_occurrence_attributes(source: SourceOccurrence) -> dict[str, Any]:
    """
    Occurrence identity carried as tree attributes.

    ExprNode has no occurrence_key field, so attribution is attached as
    attributes on the ROOT node by the caller. These attributes are
    serialized by ExprNode.to_dict(), so the identity survives to disk and
    can be traced back to the pinned source occurrence.
    """
    return {
        "occurrence_key": occurrence_key(source),
        "source_locator": source.source_locator,
        "occurrence_index": source.occurrence_index,
    }


# ---------------------------------------------------------------------------
# RecoveryRecord construction
# ---------------------------------------------------------------------------

def build_recovery_record(
    source: SourceOccurrence,
    mathml: str | None = None,
    attach_occurrence: bool = True,
) -> RecoveryRecord:
    """
    Build one RecoveryRecord for one source occurrence.

    Populates canonical_tree with the typed AST and derives structural_status
    honestly from it. Does NOT touch the backend or solution statuses — those
    remain "not_attempted" until a backend is actually invoked.

    If mathml is absent/unparseable, parse_status="failed" and
    canonical_tree stays None (never a fabricated tree).
    """
    if not mathml:
        return RecoveryRecord(
            source=source,
            parse_status="failed",
            structural_status="unverified",
            canonical_tree=None,
            warnings=["no_mathml"],
        )

    tree, reasons = extract_structural_ast(mathml)
    if tree is None:
        return RecoveryRecord(
            source=source,
            parse_status="failed",
            structural_status="unverified",
            canonical_tree=None,
            warnings=[f"ast_extract_failed:{r}" for r in reasons],
        )

    # Bind occurrence identity to the root of the tree.
    if attach_occurrence:
        attrs = dict(tree.attributes or {})
        attrs.update(ast_occurrence_attributes(source))
        # ExprNode is frozen; rebuild via to_dict to re-attach attributes.
        tree = ExprNode.from_dict({**tree.to_dict(), "attributes": attrs})

    structural = derive_structural_status(tree)
    unsupported_nodes = collect_unsupported_nodes(tree)

    # parse_status: "unsupported" if the tree is entirely unsupported content,
    # "partial" if some content was unsupported, else "complete".
    if tree.kind == "unsupported":
        parse_status = "unsupported"
    elif unsupported_nodes:
        parse_status = "partial"
    else:
        parse_status = "complete"

    warnings: list[str] = []
    if reasons:
        warnings.extend(f"unsupported:{r}" for r in reasons)

    return RecoveryRecord(
        source=source,
        parse_status=parse_status,
        structural_status=structural,
        canonical_tree=tree,
        unsupported_nodes=unsupported_nodes,
        warnings=warnings,
    )


def make_source_occurrence(
    *,
    paper_id: str,
    paper_version: str,
    source_locator: str,
    occurrence_index: int,
    mathml: str | None,
    latex: str | None = None,
) -> SourceOccurrence:
    """Build a SourceOccurrence with a real source_hash of the MathML."""
    return SourceOccurrence(
        paper_id=paper_id,
        paper_version=paper_version,
        source_locator=source_locator,
        occurrence_index=occurrence_index,
        source_hash=hashlib.sha256((mathml or "").encode("utf-8")).hexdigest(),
        latex=latex,
        mathml=mathml,
    )


# ---------------------------------------------------------------------------
# Corpus -> records
# ---------------------------------------------------------------------------

def build_records_from_corpus(
    corpus: dict[str, Any],
    *,
    paper_id: str | None = None,
    paper_version: str = "latest",
    max_records: int | None = None,
) -> list[RecoveryRecord]:
    """
    Build RecoveryRecords from an arxiv_html_corpus/*.json document.

    corpus["equations"] entries carry 'id', 'latex', 'mathml'. Each becomes
    one record bound to its own SourceOccurrence.

    One source occurrence -> one recovery record. No collapsing, no dedup.
    """
    pid = paper_id or corpus.get("arxiv_id") or "unknown"
    records: list[RecoveryRecord] = []

    for pos, eq in enumerate(corpus.get("equations", [])):
        if max_records is not None and len(records) >= max_records:
            break
        mathml = eq.get("mathml")
        latex = eq.get("latex")
        locator = eq.get("id") or f"math[{pos}]"
        source = make_source_occurrence(
            paper_id=pid,
            paper_version=paper_version,
            source_locator=locator,
            occurrence_index=pos,
            mathml=mathml,
            latex=latex,
        )
        records.append(build_recovery_record(source, mathml))

    return records


def summarize_records(records: list[RecoveryRecord]) -> dict[str, Any]:
    """Count records by status. Occurrence-level, not backend-level."""
    from collections import Counter

    parse = Counter(r.parse_status for r in records)
    structural = Counter(r.structural_status for r in records)
    with_tree = sum(1 for r in records if r.canonical_tree is not None)
    with_unsupported = sum(1 for r in records if r.unsupported_nodes)

    return {
        "total": len(records),
        "unique_occurrences": len({occurrence_key(r.source) for r in records}),
        "with_canonical_tree": with_tree,
        "with_unsupported_nodes": with_unsupported,
        "parse_status": dict(parse),
        "structural_status": dict(structural),
    }


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    samples = [
        ("<math><mi>a</mi><mo>\u2248</mo><mi>b</mi></math>", "approx preserved"),
        ("<math><mi>a</mi><mo>=</mo><mi>b</mi></math>", "eq preserved"),
        ("<math><mi>a</mi><mo>=</mo><mspace width=\"1em\"/><mi>b</mi></math>",
         "unsupported -> partial"),
        ("<math><mspace width=\"1em\"/></math>", "fully unsupported"),
    ]
    for i, (mml, label) in enumerate(samples):
        src = make_source_occurrence(
            paper_id="selftest", paper_version="v1",
            source_locator=f"math[{i}]", occurrence_index=i,
            mathml=mml, latex="x",
        )
        rec = build_recovery_record(src, mml)
        ok = (
            rec.parse_status
            and rec.structural_status
            and rec.canonical_tree is not None and (rec.canonical_tree.attributes or {}).get('occurrence_key') == occurrence_key(rec.source)
        ) if rec.canonical_tree else False
        print(f"  {'ok ' if ok else 'ERR'} {label:28s} parse={rec.parse_status:11s} "
              f"structural={rec.structural_status:11s} unsupported={len(rec.unsupported_nodes)}")
