"""
MATH CONTRACT — canonical schema for math recovery pipeline
===========================================================

This module is the shared contract between extraction, parsing, solving,
and reporting. Every production pipeline component must use it.

Contract version: 2026.10.09-v1

Rules:
  - One source occurrence → one recovery record.
  - Source evidence is immutable. LaTeX and MathML are preserved separately.
  - Parsing is not structural verification.
  - Backend acceptance is not solution.
  - Partial is explicit. Unsupported nodes cannot disappear silently.
  - Every metric is derived from records, not from scattered counter increments.

Four independent status dimensions:
  — ParseStatus: did the parser handle the input?
  — StructuralStatus: is the mathematical structure preserved?
  — BackendStatus: did a backend accept the expression?
  — SolutionStatus: did a backend solve/evaluate the expression?

These four dimensions must never be conflated. A "solvable" count means
backend acceptance, not structural fidelity or solution.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Status types — four independent dimensions
# ---------------------------------------------------------------------------

ParseStatus = Literal[
    "complete",       # parser handled the entire input
    "partial",        # parser handled some but not all
    "unsupported",    # parser encountered constructs it cannot represent
    "failed",         # parser could not produce any output
]

StructuralStatus = Literal[
    "verified",       # all source children accounted for, no lossy transforms
    "equivalent",     # different surface, same structure (documented)
    "lossy",          # some source structure was lost
    "corrupted",      # output does not represent the source
    "unverified",     # not yet checked against source
    "partial",        # extractor found unsupported content; source not fully covered
]

BackendStatus = Literal[
    "not_attempted",  # never sent to a backend
    "accepted",       # backend parsed/evaluated the expression
    "rejected",       # backend refused the expression
    "error",          # backend raised an error
]

SolutionStatus = Literal[
    "not_attempted",  # never asked to solve
    "solved",         # backend found a solution
    "evaluated",      # backend evaluated the expression (not solved)
    "no_solution",    # backend determined no solution exists
    "undetermined",    # backend could not determine
    "error",          # solver raised an error
]

# ---------------------------------------------------------------------------
# Recursive expression tree
# ---------------------------------------------------------------------------

# Kinds the parser can emit. Extend as new constructs are supported.
NODE_KINDS = frozenset({
    "identifier",     # <mi> — single symbol
    "number",         # <mn> — numeric literal
    "operator",       # <mo> — operator or relation
    "relation",       # typed relation (sim, approx, eq, etc.)
    "fraction",       # <mfrac> — numerator/denominator
    "power",          # <msup> — base^exponent
    "subscript",      # <msub> — base_subscript
    "integral",       # ∫, ∮, ∬, ∭ — with bounds, integrand, differentials
    "differential",   # dx, dy, dz — measure of integration
    "sum",            # ∑ — with bounds and summand
    "product",        # ∏ — with bounds and multiplicand
    "limit",          # lim — with approach and function
    "sqrt",           # √ — with radicand
    "root",           # \sqrt[n] — with radicand and index
    "matrix",         # <mtable> — rows of cells
    "group",          # <mrow> — implicit product/sequence
    "text",           # <mtext> — text label in math
    "unsupported",    # MathML subtree the parser cannot represent
})


@dataclass(frozen=True)
class ExprNode:
    """
    Recursive expression tree node.

    kind: what mathematical construct this node represents
    value: the original token/symbol, preserved from source
    children: subexpressions in source order
    attributes: kind-specific data (e.g., operator kind, relation type)

    Invariants:
      - children is a tuple (immutable, hashable)
      - attributes is a dict with string keys and JSON-serializable values
      - an unsupported node must preserve the source representation
      - attributes are defensively copied on construction; post-construction
        mutation of the original dict does not affect the node
    """
    kind: str
    value: str | None = None
    children: tuple["ExprNode", ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.kind not in NODE_KINDS:
            raise ValueError(f"Unknown node kind: {self.kind}")
        # Defensive copy — caller's dict mutations after construction are isolated
        object.__setattr__(self, "attributes", dict(self.attributes))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        out: dict[str, Any] = {"kind": self.kind}
        if self.value is not None:
            out["value"] = self.value
        if self.children:
            out["children"] = [c.to_dict() for c in self.children]
        if self.attributes:
            out["attributes"] = self.attributes
        return out

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ExprNode":
        """Deserialize from dict produced by to_dict()."""
        return cls(
            kind=d["kind"],
            value=d.get("value"),
            children=tuple(cls.from_dict(c) for c in d.get("children", [])),
            attributes=dict(d.get("attributes", {})),
        )


# ---------------------------------------------------------------------------
# Source occurrence — immutable identity of a math expression in a paper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceOccurrence:
    """
    Identifies a single math expression occurrence in a pinned paper.

    paper_id:       arXiv identifier (e.g., "2605.00155")
    paper_version:  version string (e.g., "v1") or "latest"
    source_locator: document-order locator (e.g., "math[42]")
    occurrence_index: sequential index within the source document
    source_hash:    SHA-256 of the serialized <math> element from source HTML
    latex:          original LaTeX annotation (or None)
    mathml:         complete MathML markup (or None)
    """
    paper_id: str
    paper_version: str
    source_locator: str
    occurrence_index: int
    source_hash: str
    latex: str | None = None
    mathml: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "paper_version": self.paper_version,
            "source_locator": self.source_locator,
            "occurrence_index": self.occurrence_index,
            "source_hash": self.source_hash,
            "latex": self.latex,
            "mathml": self.mathml,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SourceOccurrence":
        return cls(
            paper_id=d["paper_id"],
            paper_version=d["paper_version"],
            source_locator=d["source_locator"],
            occurrence_index=d["occurrence_index"],
            source_hash=d["source_hash"],
            latex=d.get("latex"),
            mathml=d.get("mathml"),
        )


# ---------------------------------------------------------------------------
# Recovery record — the result of processing one source occurrence
# ---------------------------------------------------------------------------


@dataclass
class RecoveryRecord:
    """
    One record per source occurrence. Tracks four independent statuses.

    parse_status:       did the parser handle the input?
    structural_status:  is the mathematical structure preserved?
    backend_status:     did a backend accept the expression?
    solution_status:    did a backend solve/evaluate?

    canonical_tree:     ExprNode tree (or None if parsing failed)
    backend_input_hash: SHA-256 of the exact tree sent to the backend
    unsupported_nodes:  source nodes the parser cannot represent (retained)
    warnings:           parser notes about lossy transformations
    """
    source: SourceOccurrence
    parse_status: ParseStatus
    structural_status: StructuralStatus = "unverified"
    canonical_tree: ExprNode | None = None
    backend_status: BackendStatus = "not_attempted"
    solution_status: SolutionStatus = "not_attempted"
    unsupported_nodes: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    backend_input_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "source": self.source.to_dict(),
            "parse_status": self.parse_status,
            "structural_status": self.structural_status,
            "backend_status": self.backend_status,
            "solution_status": self.solution_status,
        }
        if self.canonical_tree is not None:
            out["canonical_tree"] = self.canonical_tree.to_dict()
        if self.backend_input_hash:
            out["backend_input_hash"] = self.backend_input_hash
        if self.unsupported_nodes:
            out["unsupported_nodes"] = self.unsupported_nodes
        if self.warnings:
            out["warnings"] = self.warnings
        return out

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RecoveryRecord":
        tree = d.get("canonical_tree")
        return cls(
            source=SourceOccurrence.from_dict(d["source"]),
            parse_status=d["parse_status"],
            structural_status=d.get("structural_status", "unverified"),
            canonical_tree=ExprNode.from_dict(tree) if tree else None,
            backend_status=d.get("backend_status", "not_attempted"),
            solution_status=d.get("solution_status", "not_attempted"),
            unsupported_nodes=list(d.get("unsupported_nodes", [])),
            warnings=list(d.get("warnings", [])),
            backend_input_hash=d.get("backend_input_hash"),
        )


# ---------------------------------------------------------------------------
# Canonical serialization and hashing
# ---------------------------------------------------------------------------


def canonical_json(obj: Any) -> str:
    """
    Deterministic JSON encoding for hashing.

    Rules:
      - sort keys
      - no whitespace
      - ensure_ascii=True (UTF-8 encoding is handled at the byte level)
      - separators: (",", ":") — compact
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def hash_bytes(data: bytes) -> str:
    """SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def source_hash(mathml: str) -> str:
    """
    Hash of the complete serialized <math> element from source HTML.

    Input is the MathML string as extracted from the HTML document.
    The string is encoded as UTF-8 before hashing.

    IMPORTANT: this hashes the DOM-serialized element, not necessarily the
    original byte sequence from the HTML file. A DOM parser may normalize
    whitespace and attribute ordering. This is documented behavior.
    """
    return hash_bytes(mathml.encode("utf-8"))


def extraction_hash(latex: str | None, mathml: str | None) -> str:
    """
    Hash of the extracted (latex, mathml) pair.

    Encoding: canonical_json of {"latex": latex, "mathml": mathml}.
    None and "" are distinct — None means the field was absent from source,
    "" means it was present but empty.
    """
    return hash_bytes(canonical_json({"latex": latex, "mathml": mathml}).encode("utf-8"))


def backend_input_hash(tree: ExprNode) -> str:
    """
    Hash of the canonical expression tree submitted to the backend.

    This binds the solver output to a specific tree version. If the tree
    changes, the backend_input_hash changes, and the old solver result
    is no longer valid.
    """
    return hash_bytes(canonical_json(tree.to_dict()).encode("utf-8"))


def occurrence_key(source: SourceOccurrence) -> str:
    """
    Stable occurrence identity key.

    Derived from paper_id, paper_version, source_locator, and occurrence_index.
    Uses canonical JSON + SHA-256 to avoid ambiguity if components contain colons.

    The key identifies an occurrence within a pinned source snapshot.
    source_hash detects changes to that source occurrence.
    """
    payload = {
        "paper_id": source.paper_id,
        "paper_version": source.paper_version,
        "source_locator": source.source_locator,
        "occurrence_index": source.occurrence_index,
    }
    return hash_bytes(canonical_json(payload).encode("utf-8"))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_record(record: RecoveryRecord) -> list[str]:
    """
    Validate a recovery record against contract invariants.

    Returns a list of violation strings. Empty list = valid.

    Invariants checked:
      1. parse_status is a valid ParseStatus
      2. structural_status is a valid StructuralStatus
      3. backend_status is a valid BackendStatus
      4. solution_status is a valid SolutionStatus
      5. if parse_status == "failed", canonical_tree must be None
      6. if canonical_tree is None, backend_status must be "not_attempted"
      7. if backend_status != "not_attempted", backend_input_hash must be set
      8. if structural_status == "verified", unsupported_nodes must be empty
      9. if parse_status == "partial", unsupported_nodes must be non-empty
    """
    violations: list[str] = []

    if record.parse_status not in ("complete", "partial", "unsupported", "failed"):
        violations.append(f"Invalid parse_status: {record.parse_status}")

    if record.structural_status not in ("verified", "equivalent", "lossy", "corrupted", "unverified"):
        violations.append(f"Invalid structural_status: {record.structural_status}")

    if record.backend_status not in ("not_attempted", "accepted", "rejected", "error"):
        violations.append(f"Invalid backend_status: {record.backend_status}")

    if record.solution_status not in ("not_attempted", "solved", "evaluated", "no_solution", "undetermined", "error"):
        violations.append(f"Invalid solution_status: {record.solution_status}")

    if record.parse_status == "failed" and record.canonical_tree is not None:
        violations.append("parse_status=failed but canonical_tree is not None")

    if record.canonical_tree is None and record.backend_status != "not_attempted":
        violations.append("backend_status is not 'not_attempted' but canonical_tree is None")

    if record.backend_status != "not_attempted" and record.backend_input_hash is None:
        violations.append("backend_status is set but backend_input_hash is missing")

    # Backend hash integrity — the stored hash must match the actual tree
    if record.backend_status != "not_attempted" and record.canonical_tree is not None:
        actual_hash = backend_input_hash(record.canonical_tree)
        if record.backend_input_hash != actual_hash:
            violations.append(
                f"backend_input_hash mismatch: stored={record.backend_input_hash[:12]}... "
                f"actual={actual_hash[:12]}..."
            )

    # Solution/backend consistency
    if record.solution_status in ("solved", "evaluated", "no_solution") and record.backend_status == "not_attempted":
        violations.append(f"solution_status={record.solution_status} but backend_status=not_attempted")

    if record.structural_status == "verified" and record.unsupported_nodes:
        violations.append("structural_status=verified but unsupported_nodes is non-empty")

    if record.parse_status == "partial" and not record.unsupported_nodes:
        violations.append("parse_status=partial but unsupported_nodes is empty")

    return violations


def validate_occurrence_set(
    source_keys: list[str],
    record_keys: list[str],
) -> list[str]:
    """
    Validate occurrence conservation.

    Every source occurrence key must have exactly one recovery record key.
    No duplicate keys, no missing keys, no extra keys.

    Accepts lists (not sets) so duplicate detection is possible.

    Returns a list of violation strings. Empty list = conserved.
    """
    violations: list[str] = []

    src_set = set(source_keys)
    rec_set = set(record_keys)

    missing = src_set - rec_set
    if missing:
        violations.append(f"Missing recovery records for {len(missing)} source occurrences: {sorted(missing)[:5]}")

    extra = rec_set - src_set
    if extra:
        violations.append(f"Extra recovery records for {len(extra)} unknown source keys: {sorted(extra)[:5]}")

    # Duplicate detection — requires the original sequences
    src_dupes = _find_duplicates(source_keys)
    if src_dupes:
        violations.append(f"Duplicate source occurrence keys: {src_dupes[:5]}")

    rec_dupes = _find_duplicates(record_keys)
    if rec_dupes:
        violations.append(f"Duplicate recovery record keys: {rec_dupes[:5]}")

    return violations


def _find_duplicates(keys: list[str]) -> list[str]:
    """Return keys that appear more than once in the sequence."""
    seen: set[str] = set()
    dupes: list[str] = []
    for k in keys:
        if k in seen and k not in dupes:
            dupes.append(k)
        seen.add(k)
    return dupes


# ---------------------------------------------------------------------------
# Summary metrics — derived from records, never from scattered counters
# ---------------------------------------------------------------------------


def summarize_records(records: list[RecoveryRecord]) -> dict[str, Any]:
    """
    Compute summary metrics from recovery records.

    Every metric is derived from the record list. No separate counters.

    Returns a dict with:
      total: total number of source occurrences
      parse: {complete, partial, unsupported, failed}
      structural: {verified, equivalent, lossy, corrupted, unverified}
      backend: {not_attempted, accepted, rejected, error}
      solution: {not_attempted, solved, evaluated, no_solution, undetermined, error}
    """
    parse_counts: dict[str, int] = {}
    structural_counts: dict[str, int] = {}
    backend_counts: dict[str, int] = {}
    solution_counts: dict[str, int] = {}

    for r in records:
        parse_counts[r.parse_status] = parse_counts.get(r.parse_status, 0) + 1
        structural_counts[r.structural_status] = structural_counts.get(r.structural_status, 0) + 1
        backend_counts[r.backend_status] = backend_counts.get(r.backend_status, 0) + 1
        solution_counts[r.solution_status] = solution_counts.get(r.solution_status, 0) + 1

    return {
        "total": len(records),
        "parse": parse_counts,
        "structural": structural_counts,
        "backend": backend_counts,
        "solution": solution_counts,
    }


# ---------------------------------------------------------------------------
# Contract version
# ---------------------------------------------------------------------------

CONTRACT_VERSION = "2026.10.09-v1"
CONTRACT_MODULE = "scripts/math_contract.py"
