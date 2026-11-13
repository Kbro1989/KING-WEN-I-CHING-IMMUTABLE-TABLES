# Producer Manifest Coverage Reconciliation

## Document Metadata

- **File**: `docs/producer_manifest_coverage_reconciliation.md`
- **Parent**: `docs/producer_manifest_coverage_reconciliation.md`
- **Generated**: 2026-11-10
- **Status**: Source-level review of the earlier Producer-to-Manifest Existence Audit
- **Disposition**: `MERGED` — superseded the existence-audit-only classification; adds coverage coding

---

## 1. Correct Producer/Family Arithmetic

### Original claim

> "The 10 producers with existing manifests cover 11 of 13 output families."

This is **not supported** by the table.

### Corrected counts

| Measurement                            | Count |
| -------------------------------------- | ----- |
| Total producer entries                 | 13    |
| Producers with identified manifests    | 10    |
| Producers without identified manifests | 3     |
| Distinct output-family names           | 12    |
| Manifest files identified              | 10    |

**Correction**: The claim "11 of 13 output families" is invalid. The correct statement is:

> The 10 producers with existing manifests cover **11 manifests across 12 distinct output families** (because one manifest, `kingwen_model_sets/kit_version_manifest.json`, covers two producers sharing the same directory).

### Resolution

- 13 producer entries
- 10 manifest files
- 12 distinct output families
- 3 producers without any directory-level manifest

---

## 2. Reconcile Rahmani Artifact Count

### Original claim

| Proposed manifest | Listed artifacts | Report's stated count |
|-------------------|------------------|-----------------------|
| `rahmani_generalization_manifest.json` | 3 | 2 |

### Reconciliation

The report incorrectly states 2; it should be **3 artifacts**. The three named artifacts are:

| Artifact | Role |
|----------|------|
| `rahmani_1212.0957_generalization_evaluation.json` | Evaluation result |
| `rahmani_1212.0957_generalization_freeze_manifest.json` | Freeze manifest |
| `rahmani_1212.0957_generalization_target.json` | Evaluation target |

**Correction**: The Rahmani family has **3 distinct artifacts** with different roles. The freeze manifest is not interchangeable with the evaluation result.

### Resolution

- `rahmani_generalization_manifest.json` must preserve the distinction between:
  - Evaluation result
  - Freeze manifest
  - Evaluation target
- These three artifacts serve different roles in the pipeline and should not be conflated in any manifest structure.

---

## 3. Manifest Presence Does Not Establish Manifest Coverage

### Core principle

Checking whether a directory-level manifest file exists does **not** establish that it:

- Names the correct producer
- Lists every expected output
- Records actual output paths
- Records hashes and sizes
- Identifies source inputs and producer versions
- Distinguishes generated, consumed, superseded, and frozen artifacts
- Matches the current filesystem
- Has been validated against its producer

### Example

`kingwen_avatar_mesh_manifest.json` being 707,865 bytes does not prove it correctly accounts for all 512 PLY files. Similarly, two producers sharing `kit_version_manifest.json` does not prove the manifest distinguishes their respective contributions.

### Resolution

This audit records **existence status only**. Coverage certification requires a separate pass that verifies each manifest against:
1. Producer identity
2. Expected artifact list
3. Hash and size verification
4. Frozen/active classification
5. Current filesystem consistency

---

## 4. Three Missing-Manifest Candidates — Different Treatment

### A. `scripts/full_hexagram_shotgun.py`

**Producer-lineage history**:

- `build_full_shotgun_jsonl.py` is the canonical producer of `full_shotgun_expansion_all.jsonl`
- `full_hexagram_shotgun.py` is a superseded producer for that specific output

**But**: That does not mean `full_hexagram_shotgun.py` is superseded for every output it produces.

The agent identifies two outputs:

- `expanded_states.csv`
- `resolved_states.csv`

**Disposition**: `PRODUCER_AUTHORITY_UNRESOLVED` — requires independent producer-function and artifact-lineage verification. Do not transfer the superseded status from one output to every function in the module.

### B. `scripts/generate_sovereign_world.py`

**Reported outputs**:

- `kingwen_sovereign_world_topology.json`
- `godot_scenes/`
- `openusd_stages/`

**Disposition**: `CREATION_GATE_BLOCKED` — requires verification of the missing `DATASETS/quantum_64_grid_transitional_mapping.json` (currently 0 bytes) before a sovereign-world manifest can be created. A sovereign-world manifest could help establish the topology producer, input dependencies, and output inventory — but must not be used to infer or fabricate the missing transitional mapping.

### C. `scripts/evaluate_rahmani_generalization.py`

**Three artifacts have different roles**:

| Artifact | Role |
|----------|------|
| `rahmani_1212.0957_generalization_evaluation.json` | Evaluation result |
| `rahmani_1212.0957_generalization_freeze_manifest.json` | Freeze manifest |
| `rahmani_1212.0957_generalization_target.json` | Evaluation target |

**Disposition**: `MANIFEST_COVERED` — a single manifest must preserve these three role distinctions. The freeze manifest must not be treated as interchangeable with the evaluation result.

---

## 5. Producer-to-Family Coverage Classification

| Producer | Output family | Manifest status | Coverage class | Evidence |
|----------|---------------|-----------------|----------------|----------|
| `scripts/bridge_depth_anything_v2.py` | `depth_maps_16bit/` | `depth_anything_v2_manifest.json` | `MANIFEST_COVERED` | File exists, 37,170 bytes |
| `scripts/build_benchmark_manifest.py` | `benchmark_artifacts/` | `benchmark_manifest.json` | `MANIFEST_COVERED` | File exists, 110,215 bytes |
| `scripts/generate_avatar_meshes.py` | `kingwen_avatar_meshes/` | `kingwen_avatar_mesh_manifest.json` | `MANIFEST_COVERED` | File exists, 707,865 bytes |
| `generate_godot_729.py` | `godot_scenes/` | `godot_mesh_conversion_manifest.json` | `MANIFEST_COVERED` | File exists, 141,036 bytes |
| `shap_e_kingwen_3d_generator.py` | `kingwen_3d_meshes/` | `shap_e_3d_manifest.json` | `MANIFEST_COVERED` | File exists, 46,223 bytes |
| `build_3d_kit_meshes.py` | `kingwen_model_sets/` | `kit_version_manifest.json` | `MANIFEST_COVERED` | File exists, 19,054 bytes |
| `build_kingwen_model_sets.py` | `kingwen_model_sets/` | `kit_version_manifest.json` | `MANIFEST_COVERED` | Same file shared with #6 |
| `generate_collisionvis.py` | `collisionvis_physics/` | `collisionvis_upgrade_manifest.json` | `MANIFEST_COVERED` | File exists, 377 bytes |
| `scripts/math_recovery_tool.py` | `math_symbols/` | `math_symbols/manifest.json` | `MANIFEST_COVERED` | File exists, 243,392 bytes |
| `transform_object_rsmv.py` | `kingwen_rsmv_models/` | `rsmv_shap_e_manifesto.json` | `MANIFEST_COVERED` | File exists, 8,819 bytes |
| `scripts/full_hexagram_shotgun.py` | `pipeline_outputs/` | *(none)* | `PRODUCER_AUTHORITY_UNRESOLVED` | Requires producer/lineage verification |
| `scripts/generate_sovereign_world.py` | `sovereign_world/` | *(none)* | `CREATION_GATE_BLOCKED` | Blocked by empty `quantum_64_grid_transitional_mapping.json` |
| `scripts/evaluate_rahmani_generalization.py` | `rahmani_generalization/` | *(none)* | `NO_MANIFEST` | 3 artifacts with distinct roles (eval/freeze/target) |

### Summary

- `MANIFEST_COVERED`: 10 producers (6 with direct per-family manifest, 3 sharing a manifest, 1 alternative manifest)
- `PRODUCER_AUTHORITY_UNRESOLVED`: 1 producer (`full_hexagram_shotgun.py`)
- `CREATION_GATE_BLOCKED`: 1 producer (`generate_sovereign_world.py`)
- `NO_MANIFEST`: 1 producer (`evaluate_rahmani_generalization.py`)

---

## 6. Existing Records That Complement This Audit

| Record | What it answers |
|--------|-----------------|
| `DATASETS/manifest.json` | What artifacts are registered |
| `inventory/file_inventory.jsonl` | What files are on disk |
| `inventory/authority_lifecycle.json` | Authority/lifecycle classifications |
| `inventory/artifact_lineage.jsonl` | Producer-to-artifact relationships |
| Directory-level manifests | What a specific output family claims to contain |

These are complementary records, not substitutes.

---

## 7. Key Missing Relationship

The complete producer-to-consumer chain that is missing:

```
Producer scripts →
  input dependencies (version, hash) →
  execution → generated outputs → hashes → output artifacts →
    downstream consumers
```

This relationship is not currently captured in any single record or manifest.

---

## 8. Status Matrix for Historical Validation

Apply this matrix separately for historical validation vs. current runtime state:

| Historical evidence | Evidence file | Current runtime? | Disposition |
|---------------------|---------------|------------------|-------------|
| Training freshness (1,536 records) | Project context | N/A | `HISTORICALLY_VERIFIED` |
| Widget `/expand` runtime | Deployment guide only | Blocked (import error) | `HISTORICALLY_VERIFIED — CURRENT RUNTIME BLOCKED` |
| Widget `/capture` | No prior end-to-end test | Blocked | `BLOCKED` |
| Widget `/voice/{id}` | Voice architecture docs | Not tested | `NOT_RETESTED` |
| Widget `/scene/count` | No prior test | Blocked | `BLOCKED` |
| Browser baked-data fallback | Widget architecture only | Not tested | `NOT_RETESTED` |
| Cartesia adapter | Voice routing docs | Not runtime-certified | `NOT_RETESTED` |
| Voice pellet visualization | No prior visual test | N/A | `NOT_RETESTED` |
| Quantum topology | Topology generation docs | Not validated | `NOT_RETESTED` |
| Inventory/artifact lineage | Multiple inventory reports | `INVENTORY_PASS` | `CURRENTLY_VERIFIED` |
| External systems registry | Registry reconciliation | `7/7 NEGATIVE PASS` (reported) | `CURRENTLY_VERIFIED` |

---

## 9. Recommended Next Actions

| Action | Required |
|--------|----------|
| Correct the producer/family arithmetic in the existence audit | Yes |
| Reconcile Rahmani artifact count (3, not 2) | Yes |
| Determine if existing manifests contain complete artifact inventories | Yes |
| Reconcile `full_hexagram_shotgun.py` output-level authority | Yes |
| Verify sovereign-world output paths and producer inputs | Yes |
| Verify Rahmani evaluation/freeze/target relationships | Yes |
| Determine whether a central manifest covers missing families | Yes |
| Create the three new manifests | **DEFERRED** — pending evidence from reconciliation pass |
| Write `docs/HISTORICAL_VALIDATION_RECONCILIATION.md` | Yes (user-requested deliverable) |

---

## 10. Disposition Summary

| Producer | Disposition | Notes |
|----------|-------------|-------|
| `bridge_depth_anything_v2.py` | `MANIFEST_COVERED` | Per-family manifest exists |
| `build_benchmark_manifest.py` | `MANIFEST_COVERED` | Per-family manifest exists |
| `generate_avatar_meshes.py` | `MANIFEST_COVERED` | Per-family manifest exists |
| `generate_godot_729.py` | `MANIFEST_COVERED` | Per-family manifest exists |
| `shap_e_kingwen_3d_generator.py` | `MANIFEST_COVERED` | Per-family manifest exists |
| `build_3d_kit_meshes.py` | `MANIFEST_COVERED` | Shared `kit_version_manifest.json` |
| `build_kingwen_model_sets.py` | `MANIFEST_COVERED` | Shared `kit_version_manifest.json` |
| `generate_collisionvis.py` | `MANIFEST_COVERED` | Alternative manifest exists |
| `scripts/math_recovery_tool.py` | `MANIFEST_COVERED` | Alternative manifest exists |
| `transform_object_rsmv.py` | `MANIFEST_COVERED` | Alternative manifest exists |
| `scripts/full_hexagram_shotgun.py` | `PRODUCER_AUTHORITY_UNRESOLVED` | Requires producer/lineage verification |
| `scripts/generate_sovereign_world.py` | `CREATION_GATE_BLOCKED` | Blocked by zero-byte transitional mapping |
| `scripts/evaluate_rahmani_generalization.py` | `NO_MANIFEST` | 3 distinct artifacts, no manifest |

---

## 11. Key Discrepancies Preserved in Audit History

| Discrepancy | Original report claim | Corrected claim | Resolution |
|-------------|----------------------|-----------------|------------|
| Producer/family count | "11 of 13 output families" | "10 producers, 12 distinct families, 10 manifests" | Arithmetic correction |
| Rahmani count | 2 artifacts | 3 artifacts (eval, freeze, target) | Role distinction |
| Manifest presence → coverage | Implicitly treated as coverage | Existence only; coverage requires verification | Methodology correction |
| `full_hexagram_shotgun.py` authority | Superseded | `PRODUCER_AUTHORITY_UNRESOLVED` | Producer-function verification needed |

---

*This reconciliation document supersedes the earlier Producer-to-Manifest Existence Audit for purposes of manifest coverage classification. The existence audit alone remains valid for directory-structure checks only.*
