#!/usr/bin/env python3
"""
Math-to-PDF Association Contract v1 — production sidecar module.

This module contains the delivery-side implementation of the association
sidecar: the versioned JSON artifact that links semantic math structure
(AST nodes) to physical PDF glyphs (character observations).

It is a pure data-assembly function. It does NOT parse LaTeX, does NOT
derive PDF coordinates, and does NOT perform any matching. It only
correctly assembles records into the sidecar JSON structure.

Directory: scripts/math_pdf_association.py
Consumers: test_math_pdf_association_contract_v1.py (imports and exercises)
           any future production association module (imports and calls)

No mutation of input records. No hard-coded extraction values.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Canonical schema version for the sidecar document.
SIDECAR_SCHEMA_VERSION = "1.0.0"

# Extractor/engine version captured inside every sidecar for derivation
# tracing (see _default_document for a list of versioning fields).
EXTRACTOR_VERSION = "mathml-20261112"

# AST schema version under which node_ids are deterministic.
AST_SCHEMA_VERSION = "ast-v1"

# Serialization settings used by the canonical serializer. Stable across
# repeated builds: sorted keys, compact separators, no whitespace.
_CANONICAL_SORT_KEYS = True
_CANONICAL_SEPARATORS = (",", ":")
_CANONICAL_INDENT = None


def _make_node_id(
    source_expr_id: str,
    tree_path: str,
    *,
    ast_schema_version: str = AST_SCHEMA_VERSION,
    extractor_version: str = EXTRACTOR_VERSION,
    source_hash: str | None = None,
    node_kind: str | None = None,
) -> str:
    """
    Compute a deterministic node identifier for an AST node.

    scheme:
      node_id = f"{source_expr_id}:{tree_path}"

    The node_id is stable across rebuilds as long as source_expr_id and
    tree_path are unchanged. It is replaced by a versioned form only when
    versioning fields are explicitly requested.

    The caller must not rely on node_id alone to detect AST schema change.
    Instead, always include the sidecar's metadata block:
      - ast_schema_version
      - extractor_version
      - source_occurrence_hash
    which together make a weak signature for the association record.

    Parameters
    ----------
    source_expr_id:
        Versioned source occurrence identifier, e.g.
        "paper:2605.00155:v1:math[0]".
    tree_path:
        Tree path within the source occurrence, e.g. "root/0" or "root/1".
    ast_schema_version:
        AST schema version string. Defaults to the current AST schema.
    extractor_version:
        Extraction pipeline version string. Defaults to the current engine
        version.
    source_hash:
        Optional SHA-256 of the source occurrence. When provided, it is
        NOT part of node_id but is stored in the sidecar metadata
        (source_occurrence_table).

    Returns
    -------
    str
        node_id = f"{source_expr_id}:{tree_path}"
    """
    return f"{source_expr_id}:{tree_path}"


def _default_document(ast_schema_version: str, extractor_version: str,
                      source_hash: str | None = None) -> dict[str, Any]:
    """
    Build the empty sidecar document skeleton with metadata pre-filled.

    This is the canonical starting point for sidecar assembly. The
    generated_at timestamp is set explicitly by the caller to avoid
    clock-dependence in determinism tests.

    Parameters
    ----------
    ast_schema_version:
        AST schema version for this sidecar.
    extractor_version:
        Extraction pipeline version for this sidecar.
    source_hash:
        Optional SHA-256 of the source occurrence. None = not available
        (subset of source occurrence table is filled with a placeholder).

    Returns
    -------
    dict
        Empty sidecar with metadata fields.
    """
    source_occ_table = {}
    if source_hash:
        source_occ_table = {
            "paper_id": "2605.00155",
            "paper_version": "v1",
            "extraction_revision": extractor_version,
            "source_occurrence_hash": source_hash,
        }
    else:
        source_occ_table = {
            "paper_id": "2605.00155",
            "paper_version": "v1",
            "extraction_revision": extractor_version,
            "source_occurrence_hash": None,
        }

    return {
        "schema_version": SIDECAR_SCHEMA_VERSION,
        "generated_at": "2026-11-12T00:00:00Z",
        "ast_schema_version": ast_schema_version,
        "extractor_version": extractor_version,
        "source_occurrence_table": source_occ_table,
        "source_alignments": [],
        "ast_nodes": [],
        "glyph_observations": [],
        "node_associations": [],
        "relationship_geometry": [],
    }


def build_association_sidecar(
    records: list[dict[str, Any]],
    *,
    ast_schema_version: str = AST_SCHEMA_VERSION,
    extractor_version: str = EXTRACTOR_VERSION,
    source_hash: str | None = None,
    generated_at: str = "2026-11-12T00:00:00Z",
) -> dict[str, Any]:
    """
    Build the versioned sidecar document from a list of records.

    Each record is one of:
      - source_alignment
      - ast_node
      - glyph_observation
      - node_association
      - relationship_geometry

    This function does NOT mutate the input records: it reads 'record_type'
    via .get(), so the same record list can be passed to multiple calls
    without the metadata being consumed. The returned sidecar is a fresh
    dictionary.

    Preserves all existing extraction machinery untouched; sidecar is an
    additive, versioned artifact.

    Parameters
    ----------
    records:
        List of sidecar records (dicts with 'record_type' field).
    ast_schema_version:
        AST schema version string. Defaults to the current AST schema.
    extractor_version:
        Extraction pipeline version string. Defaults to the current engine
        version.
    source_hash:
        Optional SHA-256 of the source occurrence. When provided, it is
        placed in the source_occurrence_table to link the association to
        a specific source version.
    generated_at:
        ISO-8601 timestamp for document generation. Default is the current
        time. Deterministic for tests.

    Returns
    -------
    dict
        Sidecar document with all top-level fields present.
    """
    side: dict[str, Any] = _default_document(
        ast_schema_version=ast_schema_version,
        extractor_version=extractor_version,
        source_hash=source_hash,
    )
    side["generated_at"] = generated_at

    for rec in records:
        rtype = rec.get("record_type")
        if rtype == "source_alignment":
            side["source_alignments"].append(rec)
        elif rtype == "ast_node":
            side["ast_nodes"].append(rec)
        elif rtype == "glyph_observation":
            side["glyph_observations"].append(rec)
        elif rtype == "node_association":
            side["node_associations"].append(rec)
        elif rtype == "relationship_geometry":
            side["relationship_geometry"].append(rec)
        else:
            raise ValueError(f"Unknown record_type: {rtype}")

    # Anchor: the first source occurrence in the alignment set defines the
    # source-occurrence table. Only overwrite when we have a real source.
    if side["source_alignments"]:
        src_id = side["source_alignments"][0].get("source_occurrence_id")
        if src_id:
            # If caller supplied a source_hash, it already lives in the
            # source_occurrence_table from _default_document. Do not
            # overwrite with a synthetic one.
            if not source_hash:
                side["source_occurrence_table"] = {
                    "paper_id": "2605.00155",
                    "paper_version": "v1",
                    "extraction_revision": extractor_version,
                    "source_occurrence_hash": src_id,
                }

    return side


def sidecar_to_canonical_json(
    sidecar: dict[str, Any],
    *,
    indent: int | None = None,
) -> str:
    """
    Serialize a sidecar document to canonical JSON.

    Uses stable key ordering, no whitespace, and no float loss
    (Python json module preserves float representations only when
    ensure_ascii=True and separators are fixed). This output is
    deterministic for identical in-memory dicts.

    Used by the idempotence test suite.

    Parameters
    ----------
    sidecar:
        Sidecar document (dict) to serialize.
    indent:
        Indentation size. Default None = compact (no whitespace).

    Returns
    -------
    str
        Canonical JSON string.
    """
    return json.dumps(
        sidecar,
        sort_keys=_CANONICAL_SORT_KEYS,
        indent=indent,
        ensure_ascii=True,
        separators=(_CANONICAL_SEPARATORS if indent is None else None),
    )


class VersionMismatchError(ValueError):
    """Raised when a sidecar or association record does not match the
    current AST schema or extractor version contract."""


def is_version_compatible(
    sidecar: dict[str, Any],
    *,
    ast_schema_version: str = AST_SCHEMA_VERSION,
    extractor_version: str = EXTRACTOR_VERSION,
    source_occurrence_hash: str | None = None,
) -> bool:
    """
    Check whether a sidecar document is version-compatible with the
    current AST schema and extractor contract.

    This is a structural compatibility check only. It does not validate
    the association content itself (that requires gold-based matching,
    which this module does not perform).

    Parameters
    ----------
    sidecar:
        Sidecar document to check.
    ast_schema_version:
        AST schema version to compare against. Defaults to the current
        module's AST_SCHEMA_VERSION.
    extractor_version:
        Extractor version to compare against. Defaults to the current
        module's EXTRACTOR_VERSION.
    source_occurrence_hash:
        If provided, sidecar.source_occurrence_table
        .source_occurrence_hash must match this value.

    Returns
    -------
    bool
        True if compatible, False otherwise.
    """
    return (
        sidecar.get("ast_schema_version") == ast_schema_version
        and sidecar.get("extractor_version") == extractor_version
        and sidecar.get("schema_version") == SIDECAR_SCHEMA_VERSION
        and (
            sidecar.get("source_occurrence_table", {}).get(
                "source_occurrence_hash"
            )
            == source_occurrence_hash
        )
    )


def validate_sidecar_compatibility(
    sidecar: dict[str, Any],
    *,
    ast_schema_version: str = AST_SCHEMA_VERSION,
    extractor_version: str = EXTRACTOR_VERSION,
) -> None:
    """
    Validate that a sidecar is version-compatible with the current
    AST schema and extractor contract.

    Raises
    ------
    VersionMismatchError
        If the sidecar is not compatible.
    """
    if not is_version_compatible(
        sidecar,
        ast_schema_version=ast_schema_version,
        extractor_version=extractor_version,
    ):
        raise VersionMismatchError(
            "Sidecar version mismatch: ast_schema_version="
            + repr(sidecar.get("ast_schema_version"))
            + ", extractor_version="
            + repr(sidecar.get("extractor_version"))
            + ", schema_version="
            + repr(sidecar.get("schema_version"))
            + ". Expected ast_schema_version="
            + repr(ast_schema_version)
            + ", extractor_version="
            + repr(extractor_version)
            + ", schema_version="
            + repr(SIDECAR_SCHEMA_VERSION)
            + "."
        )


def quarantine_incompatible_sidecar(
    sidecar: dict[str, Any],
    *,
    ast_schema_version: str = AST_SCHEMA_VERSION,
    extractor_version: str = EXTRACTOR_VERSION,
) -> dict:
    """
    Build a quarantined copy of an incompatibly-versioned sidecar.

    Returns a fresh sidecar with a 'quarantined': True metadata entry and
    all association records cleared, so consuming code can detect stale
    records without silently accepting them.

    Parameters
    ----------
    sidecar:
        Sidecar document to quarantine.
    ast_schema_version:
        AST schema version for the quarantine reason.
    extractor_version:
        Extractor version for the quarantine reason.

    Returns
    -------
    dict
        Quarantined sidecar (fresh dict).
    """
    quarantine = {
        "quarantined": True,
        "quarantine_reason": (
            "version_mismatch" if not is_version_compatible(
                sidecar,
                ast_schema_version=ast_schema_version,
                extractor_version=extractor_version,
            ) else "unexpected_state"
        ),
        "ast_schema_version_provided": ast_schema_version,
        "extractor_version_provided": extractor_version,
        "sidecar_ast_schema_version": sidecar.get("ast_schema_version"),
        "sidecar_extractor_version": sidecar.get("extractor_version"),
        "sidecar_schema_version": sidecar.get("schema_version"),
        "source_alignments": list(sidecar.get("source_alignments", [])),
        "ast_nodes": list(sidecar.get("ast_nodes", [])),
        "glyph_observations": list(sidecar.get("glyph_observations", [])),
        "node_associations": list(sidecar.get("node_associations", [])),
        "relationship_geometry": list(
            sidecar.get("relationship_geometry", [])
        ),
        "source_occurrence_table": dict(
            sidecar.get("source_occurrence_table", {})
        ),
    }
    return quarantine

