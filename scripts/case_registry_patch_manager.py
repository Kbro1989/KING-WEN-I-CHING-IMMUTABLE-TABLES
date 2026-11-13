"""Case Registry Patch Manager: Non-Mutating Versioned Overlays.

Adopts PureDocBench's versioned correction-patch model to maintain gold reference
updates, annotations, and typo corrections without in-place mutation of the frozen
Two-Level Case Registry (cross_paper_case_registry_v1.json).

Schema:
  - patch_id: String identifier (e.g. PATCH-20261106-CP002-TYPOGRAPHY)
  - target_registry_hash: SHA-256 of the frozen base registry
  - target_case_id: Target case identifier (e.g. CP-002-VILT-NESTED-BRACKETS)
  - field_path: Dot-delimited path into the case dict (e.g. "gold_ast.delimiter_type")
  - old_value: Expected existing value at field_path
  - new_value: Updated replacement value
  - reviewer: Auditor identity
  - reason: Technical rationale for the correction
  - evidence_ref: Reference to source measurement or documentation
  - created_at: ISO-8601 timestamp
  - patch_sha256: Canonical SHA-256 of the patch fields

Invariants:
  1. Base registry on disk remains strictly immutable.
  2. Patches fail if base registry hash does not match target_registry_hash.
  3. Patches fail if current value at field_path does not match old_value.
  4. Overlay views are produced in-memory for downstream v2 consumers.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
DEFAULT_REGISTRY = ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
DEFAULT_PATCH_DIR = ROOT / "DATASETS" / "structural_preservation" / "case_registry_patches"


def canonical_json_bytes(obj: Any) -> bytes:
    """RFC 8785 canonical JSON serialization."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def get_nested_field(data: dict, field_path: str) -> Any:
    """Retrieve value at dot-delimited path. Returns None if field does not exist."""
    parts = field_path.split(".")
    curr = data
    for p in parts:
        if not isinstance(curr, dict) or p not in curr:
            return None
        curr = curr[p]
    return curr


def set_nested_field(data: dict, field_path: str, value: Any) -> None:
    """Set value at dot-delimited path."""
    parts = field_path.split(".")
    curr = data
    for p in parts[:-1]:
        if p not in curr or not isinstance(curr[p], dict):
            curr[p] = {}
        curr = curr[p]
    curr[parts[-1]] = value


def compute_patch_hash(patch_dict: dict) -> str:
    """Compute canonical SHA-256 over all patch fields except patch_sha256."""
    clean = {k: v for k, v in patch_dict.items() if k != "patch_sha256"}
    return hashlib.sha256(canonical_json_bytes(clean)).hexdigest()


def create_patch(
    patch_id: str,
    target_registry_hash: str,
    target_case_id: str,
    field_path: str,
    old_value: Any,
    new_value: Any,
    reviewer: str,
    reason: str,
    evidence_ref: str,
    created_at: str,
    output_dir: Path = DEFAULT_PATCH_DIR,
) -> Path:
    """Create and write a signed patch file."""
    patch_data = {
        "patch_id": patch_id,
        "target_registry_hash": target_registry_hash,
        "target_case_id": target_case_id,
        "field_path": field_path,
        "old_value": old_value,
        "new_value": new_value,
        "reviewer": reviewer,
        "reason": reason,
        "evidence_ref": evidence_ref,
        "created_at": created_at,
    }
    patch_data["patch_sha256"] = compute_patch_hash(patch_data)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{patch_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(patch_data, f, indent=2, ensure_ascii=False)
    return out_file


def validate_patch(patch_data: dict, base_registry: dict, base_hash: str) -> None:
    """Validate a patch against the base registry without applying it."""
    # 1. Verify self-hash
    computed = compute_patch_hash(patch_data)
    if computed != patch_data.get("patch_sha256"):
        raise ValueError(
            f"Patch {patch_data.get('patch_id')} integrity failure: expected {computed}, got {patch_data.get('patch_sha256')}"
        )

    # 2. Verify target registry hash
    if patch_data.get("target_registry_hash") != base_hash:
        raise ValueError(
            f"Registry hash mismatch for patch {patch_data.get('patch_id')}: "
            f"patch targets {patch_data.get('target_registry_hash')}, base has {base_hash}"
        )

    # 3. Locate target case
    cases = base_registry.get("cases", [])
    target_case = next((c for c in cases if c.get("case_id") == patch_data.get("target_case_id")), None)
    if target_case is None:
        raise KeyError(f"Target case {patch_data.get('target_case_id')} not found in registry")

    # 4. Check old_value matches current value
    current_val = get_nested_field(target_case, patch_data.get("field_path", ""))
    if current_val != patch_data.get("old_value"):
        raise ValueError(
            f"Precondition failure on {patch_data.get('field_path')}: "
            f"expected old_value={patch_data.get('old_value')!r}, but current={current_val!r}"
        )

    # 5. Safeguard against silent modification of acceptance criteria or negative controls
    fp = patch_data.get("field_path", "")
    if ("five_axis_acceptance_criteria" in fp or "negative_control_pairs" in fp) and not patch_data.get("adjudication_override", False):
        raise ValueError(
            f"Safeguard violation: patch {patch_data.get('patch_id')} targets acceptance criteria or negative controls "
            "without explicit adjudication_override=True"
        )


def load_patched_registry(
    base_registry_path: Path = DEFAULT_REGISTRY,
    patch_dir: Path = DEFAULT_PATCH_DIR,
) -> tuple[dict, list[dict]]:
    """Load base registry and apply all valid patches from patch_dir in-memory.

    Returns:
      (patched_registry_dict, list_of_applied_patch_records)
    """
    with open(base_registry_path, "rb") as f:
        base_bytes = f.read()
    base_hash = hashlib.sha256(base_bytes).hexdigest()
    base_registry = json.loads(base_bytes.decode("utf-8"))

    overlay = copy.deepcopy(base_registry)
    applied_patches = []

    if patch_dir.exists():
        patch_files = sorted(patch_dir.glob("*.json"))
        for pf in patch_files:
            with open(pf, "r", encoding="utf-8") as f:
                pdata = json.load(f)

            validate_patch(pdata, overlay, base_hash)

            # Apply to overlay
            cases = overlay.get("cases", [])
            target_case = next(c for c in cases if c.get("case_id") == pdata.get("target_case_id"))
            set_nested_field(target_case, pdata.get("field_path", ""), copy.deepcopy(pdata.get("new_value")))
            applied_patches.append({
                "patch_id": pdata.get("patch_id"),
                "file": pf.name,
                "target_case_id": pdata.get("target_case_id"),
                "field_path": pdata.get("field_path"),
                "old_value": pdata.get("old_value"),
                "new_value": pdata.get("new_value"),
                "reviewer": pdata.get("reviewer"),
                "reason": pdata.get("reason"),
                "evidence_ref": pdata.get("evidence_ref"),
                "created_at": pdata.get("created_at"),
                "patch_sha256": pdata.get("patch_sha256"),
            })

    # Strict invariant check: verify parent file on disk was not modified
    with open(base_registry_path, "rb") as f:
        base_bytes_after = f.read()
    base_hash_after = hashlib.sha256(base_bytes_after).hexdigest()
    if base_hash_after != base_hash:
        raise RuntimeError(f"CRITICAL INVARIANT VIOLATION: Parent registry mutated on disk! {base_hash} -> {base_hash_after}")

    # Compute effective registry hash (over overlay without metadata)
    effective_registry_hash = hashlib.sha256(canonical_json_bytes(overlay)).hexdigest()

    # Record overlay provenance metadata
    overlay["_overlay_metadata"] = {
        "base_registry_path": str(base_registry_path),
        "parent_registry_hash": base_hash,
        "effective_registry_hash": effective_registry_hash,
        "total_patches_applied": len(applied_patches),
        "applied_patches": applied_patches,
    }
    return overlay, applied_patches

