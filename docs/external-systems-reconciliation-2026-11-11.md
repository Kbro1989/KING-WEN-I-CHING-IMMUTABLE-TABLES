# External Systems Registry — Final Baseline

## Freeze State

| Property | Value |
|----------|-------|
| Date frozen | 2026-11-11 |
| File | `inventory/registries/external_systems.json` |
|| File size | 26382 bytes |
| SHA-256 | `ff34590910893f3160158ffbe421ec286586d79550002dfc35655d4f13ebf9db` |
| Commit status | Uncommitted (no authorization) |
| Push status | Not authorized |

## Reconciliation Reference

This registry is the result of the external-systems portion of the inventory subsystem:

- **Reconciliation report**: `docs/external-systems-reconciliation-2026-11-11.md` (created in this session)
- **Cross-reference**: execution topology (`inventory/execution_topology.json`, 460 files) + artifact lineage (`inventory/artifact_lineage.jsonl`, 17 pipeline artifacts)
- **Validation**: 64/70 integration points verified against real files on disk; 3 path corrections applied

## Schema Definition — Path Basis

**Repository-Relative Path Invariant:**

Every integration point carries two path fields:

- `system_repo`: repository identifier (the repository that owns the file)
- `repo_relative_path`: path relative to the root of `system_repo`

**Canonical schema rule:** For every integration point:

```
system_repo       = repository identifier
repo_relative_path = path relative to the root of system_repo
```

Examples:

| System                     | `system_repo`                       | `repo_relative_path`                         |
| -------------------------- | ----------------------------------- | -------------------------------------------- |
| Voicebox                   | `KING-WEN-I-CHING-IMMUTABLE-TABLES` | `scripts/emotional_engine.py`                |
| Kimi / MoonshotAI          | `KING-WEN-I-CHING-IMMUTABLE-TABLES` | `kingwen_train_data/build_hybrid_kimi_k2.py` |
| Upgraded-Depth-Anything-V2 | `Upgraded-Depth-Anything-V2`        | `run_image-depth_8bit.py`                    |

**Contract:** A correct `repo_relative_path` is validated by resolving `<repo_root>/<repo_relative_path>` and confirming the file exists. A path that redundantly includes the repository name (e.g., `Upgraded-Depth-Anything-V2/run_image-depth_8bit.py` when `system_repo` is already `Upgraded-Depth-Anything-V2`) FAILS validation — it is a duplicated repository prefix.

## Path Corrections Applied

| System                     | Old Path                                  | New Path          |
|----------------------------|-------------------------------------------|-------------------|
| Voicebox                   | `scripts/emotional_engine.py`             | `scripts/emotional_engine.py` (unchanged) |
| Voicebox                   | `scripts/kingwen_ternary_tables_complete.py` | `kingwen_ternary_tables_complete.py` (unchanged) |
| Upgraded-Depth-Anything-V2 | `scripts/run_image-depth_8bit.py`         | `run_image-depth_8bit.py`                    |

The two Kimi / MoonshotAI paths (`kingwen_train_data/build_hybrid_kimi_k2.py`, `kingwen_train_data/hybrid_kimi_k2_config.json`) remain unchanged — they were already correctly rooted under `kingwen_train_data/`.

## Schema Definition — Metadata vs Relationship Types

Repository identity and path provenance are metadata, not relationship types.

| Scope | Fields |
|-------|--------|
| **Repository identity** | `system_repo`, `repo_relative_path` |
| **Relationship type** | `relationship_type` (Produces, Consumes, Integrates, Verifies, Advises, etc.) |

The 15 relationship definitions (`VERIFIED_DEPENDENCY`, `OBSERVED_RELATIONSHIP`, etc.) define relationship semantics but are not location metadata. Repository identity is carried separately via `system_repo` and `repo_relative_path`.

## Status Semantics

The registry preserves six relationship statuses (not flattening all to dependencies):

| Status | Meaning |
|--------|---------|
| `VERIFIED_DEPENDENCY` | Evidenced runtime dependency (11 IPs) |
| `OBSERVED_RELATIONSHIP` | Observed connection, not necessarily executable (2 IPs) |
| `HISTORICAL_PROVENANCE` | Historical origin or artifact lineage (7 IPs) |
| `GENERATED_CONSUMED` | Generated output consumed elsewhere (9 IPs) |
| `MATHEMATICAL_REFERENCE` | Mathematical reference only (0 IPs) |
| `REFERENCE_ONLY` | Reference association, not executable (0 IPs) |

## Archive Note

The earlier reconciliation report had inconsistent per-system arithmetic in its first draft. The corrected report reflects 11 systems, 70 integration points, and 15 relationship type definitions. The discrepancy is preserved in this audit record; do not revise to match the stated totals.

## Reconciliation History

- **2026-11-11**: Initial external_systems.json written with POG2-only listing (rejected by user)
- **2026-11-11**: Corrected to 11 systems, 70 integration points, 14 relationship types
- **2026-11-11**: Reconciliation against execution topology and artifact lineage
- **2026-11-11**: 64/70 verified, 3 path corrections applied
