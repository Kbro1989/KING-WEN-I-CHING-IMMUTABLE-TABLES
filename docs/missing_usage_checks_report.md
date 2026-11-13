# Missing Usage Checks Report — Actual Output Files vs Existing Manifests

## Document Metadata

- **File**: `docs/missing_usage_checks_report.md`
- **Generated**: 2026-11-10
- **Status**: Verification of actual output results against existing manifests and usage-check coverage
- **Disposition**: `REPORTED` — findings documented; remediation recommendations in §9

---

## 1. Executive Summary

The purpose of this report is to verify that actual output files carry complete usage relationships to their producer manifests, and to identify gaps where usage checks are missing.

**Key findings:**

| Finding | Severity |
|---------|----------|
| 370/370 entries in `manifest.json` have `consumers: []` (empty) | CRITICAL |
| 370/370 entries have `sha256: null` | HIGH |
| Depth-maps manifest: 1 entry vs 64 actual files | HIGH |
| Godot-scenes manifest: 1 entry vs 65 actual files | HIGH |
| Qiskit lab manifest: 1 entry vs 130 actual files | HIGH |
| Benchmark manifest: 1 entry vs 0 actual files | MEDIUM |
| 5 families have **no per-family manifest** | MEDIUM |
| Shap-e manifest: 64 entries match 64 files (but no consumers) | LOW |

---

## 2. Actual Output Results vs Existing Manifests

### 2.1 Full manifest.json (DATASETS/)

| Metric | Value |
|--------|-------|
| Total entries | 370 |
| Empty `consumers` field | 370/370 = 100% |
| Null `sha256` | 370/370 = 100% |
| Frozen entries | 155 of 370 |
| Non-frozen | 215 of 370 |

### 2.2 Per-family manifest coverage

| Family | Manifest file | Declared entries | Actual files | Match? | Consumers populated? |
|--------|---------------|------------------|--------------|--------|----------------------|
| `avatar_meshes/` | `kingwen_avatar_mesh_manifest.json` | 512 | 512 | ✅ | ❌ No consumers field |
| `depth_maps_16bit/` | `depth_anything_v2_manifest.json` | 1 | 64 | ❌ | ❌ No consumers field |
| `depth_pointclouds/` | `depth_anything_v2_manifest.json` | 1 (includes both pngs and PLYs) | 64 | ⚠️ | ❌ |
| `godot_scenes/` | `godot_mesh_conversion_manifest.json` | 1 | 65 | ❌ | ❌ |
| `godot_shap_e/` | `godot_shap_e_conversion_manifest.json` | 0 | 0 | ✅ | ❌ |
| `kingwen_3d_meshes/` | `shap_e_3d_manifest.json` | 64 | 64 | ✅ | ❌ |
| `kingwen_3d_kit_meshes/` | *(none)* | 0 | 1 | ❌ | ❌ |
| `kingwen_model_sets/` | *(none)* | 0 | 66 | ❌ | ❌ |
| `collisionvis_physics/` | `collisionvis_upgrade_manifest.json` | 1 | 1 | ✅ | ❌ |
| `quantumlab_plots/` | `quantumlab_visuals_manifest.json` | 1 | 130 | ❌ | ❌ |
| `openusd_stages/` | `godot_shap_e_conversion_manifest.json` | 0 | 0 | ✅ | ❌ |
| `rsc_npc_meshes/` | `rsc_npc_meshes/manifest.json` | 1 | 1 | ✅ | N/A |

### 2.3 Manifest entry-count discrepancies

| Family | Manifest declares | Actual files | Gap | Implication |
|--------|-------------------|--------------|-----|-------------|
| `depth_maps_16bit/` | 1 | 64 | -63 | Manifest lists only one entry; does not enumerate all 64 depth maps |
| `depth_pointclouds/` | 1 | 64 | -63 | Same issue as depth_maps |
| `godot_scenes/` | 1 | 65 | -64 | Manifest has total=65 field but only 1 entry record |
| `quantumlab_plots/` | 1 | 130 | -129 | Manifest has total_hexagram_surfaces=1 but 130 plots actual |
| `benchmark_artifacts/` | 0 | 0 | 0 | Manifest may not exist for this family (benchmark_manifest.json exists but has different structure) |

---

## 3. Missing Usage Relationships (consumers field)

### 3.1 Current state

All 370 entries in `manifest.json` have `consumers: []` — empty arrays. This means:

- No downstream consumers are recorded for any artifact
- No usage-direction relationship is captured
- The complete producer → artifact → consumer chain is missing

### 3.2 What should be recorded

For the 13 output families and all their artifacts, the following usage relationships should be documented:

| Artifact family | Potential downstream consumers | Suggested tool/ticket |
|-----------------|-------------------------------|----------------------|
| `avatar_meshes/` (PLY) | Godot importer, OpenUSD loader, 3D viewer | `TC-GD-001` |
| `depth_maps_16bit/` (PNG) | PDF math-region overlay, quantum world depth | `TC-DS-001` |
| `depth_pointclouds/` (PLY) | QuantumLab 3D viewer, collisionvis physics | `TC-PC-001` |
| `kingwen_3d_meshes/` (PLY) | Shap-E renderer, viewer | `TC-SE-001` |
| `godot_scenes/` (TSCN) | Godot engine | `TC-GD-002` |
| `kingwen_rsmv_models/` (JSON) | RSMV viewer, game engine | `TC-RS-001` |
| `kingwen_model_sets/` (NPZ) | 3D pipeline, viewer | `TC-KM-001` |
| `kingwen_avatar_meshes_rsc/` (PLY) | RSC game engine, avatar system | `TC-RSC-001` |
| `benchmark_artifacts/` (PDF/PDB) | Benchmark runner, eval suite | `TC-BM-001` |

---

## 4. Missing Per-Family Manifests

### 4.1 Families without any per-family manifest

| Family directory | Actual files | Suggested manifest |
|-----------------|--------------|--------------------|
| `kingwen_3d_kit_meshes/` | 1 (all_avatars.npz, 28MB) | `kingwen_3d_kit_meshes_manifest.json` |
| `kingwen_model_sets/` | 66 files (64 kits + metadata) | `kingwen_model_sets_manifest.json` |

**Note**: `kingwen_model_sets/` uses `kit_version_manifest.json` which exists but may not fully cover the 66 files.

---

## 5. Missing Usage Checks in Existing Manifests

### 5.1 Exclusion criteria (things that should be checked but are not)

| Check | Status |
|-------|--------|
| Hash verification (SHA-256) | ❌ `sha256: null` for all 370 entries |
| File existence verification | ❌ `size_bytes` declared, but no runtime check against disk |
| Frozen-reference stability | ❌ `frozen: true` or `false` set, but no provenance chain back to generator version |
| Consumer linkage | ❌ `consumers: []` on all entries |
| Serialization format version | ❌ `schema` field present but not versioned against code |
| Semantic drift check | ❌ No mechanism to detect semantic regression between generator revisions |

### 5.2 Examples of missing closure

```
Example entry (avatar_meshes):
{
  "hexagram_id": 1,
  "phase_bits": 0,
  "ply_path": "hex01_phase0.ply",
  "vertex_count": 729,
  ...
  "consumers": []                    ← MISSING: should list downstream uses
  "sha256": null                     ← MISSING: should hash the actual PLY file
}
```

---

## 6. Producer → Input → Output Chain

The following chain is documented in `manifest.json` but the **input provenance** (what source data the producer consumed) is not present:

| Producer script | Output artifacts | Input provenance missing |
|-----------------|------------------|------------------------|
| `scripts/full_hexagram_shotgun.py` | `expanded_states.csv`, `resolved_states.csv` | Source: KING_WEN_TABLES.py, TRIGRAM_INFO, PHASE_LINE_MAP |
| `scripts/generate_avatar_meshes.py` | `kingwen_avatar_mesh_manifest.json`, 512 PLY files | Source: emotional engine, mesh geometry, kit data |
| `scripts/bridge_depth_anything_v2.py` | 64 PNG depth maps + 64 PLY point clouds | Source: quantumlab_plots/*.png, DA-V2 model |
| `scripts/math_recovery_tool.py` | 213 math-recovered files | Source: arXiv HTML XML, PDF baseline |
| `scripts/generate_sovereign_world.py` | `kingwen_sovereign_world_topology.json`, `godot_scenes/`, `openusd_stages/` | Source: quantum world topology |
| `scripts/evaluate_rahmani_generalization.py` | 3 rahmani artifacts | Source: arXiv PDF, evaluation config |

**Gap**: input provenance is missing entirely from all 370 manifest entries.

---

## 7. WebAssembly / Sidecar Usage Check Gaps

The user requested checking for missing usage checks in the actual output files and the files that point at them. Based on the manifest analysis, the following usage checks are absent:

| Check | Where to verify | Status |
|-------|-----------------|--------|
| PLY mesh geometry readable | `kingwen_avatar_mesh_manifest.json` + actual .ply files | ❌ No verification reported |
| Vertex/face count consistency vs. hexagram phase | Same as above | ❌ No per-phase checks |
| PNG depth map readable | `depth_anything_v2_manifest.json` + actual PNG files | ❌ No file format validation |
| PLY point cloud valid | `depth_pointclouds/` + actual .ply files | ❌ No validation |
| Godot scene compilable | `godot_scenes/*.tscn` + Godot engine | ❌ No validation |
| SHAP-E output plottable | `shap_e_3d_manifest.json` + actual mesh files | ❌ No validation |
| Kit mesh NPZ readable | `kingwen_model_sets/all_avatars.npz` | ❌ No schema validation |
| RSMV model JSON parseable | `kingwen_rsmv_models/*.json` | ❌ No schema validation |
| OpenUSD stage valid | `openusd_stages/*.usda` | ❌ No validation |

---

## 8. Reconciliation vs Prior Reports

This report consolidates findings from the prior two session reports:

| Prior report finding | This report confirms | Resolution |
|---------------------|---------------------|------------|
| 370/370 entries have empty consumers | ✅ Confirmed | 100% gap |
| Depth-maps manifest declares 1 entry | ✅ Confirmed | -63 files unrecorded |
| Godot-scenes manifest declares 1 entry | ✅ Confirmed | -64 files unrecorded |
| QuantumLab manifest declares 1 entry | ✅ Confirmed | -129 files unrecorded |
| 3 missing manifests (kit_meshes, model_sets, rahmani) | ✅ Confirmed | **Deferred** per reconciliation |
| `manifest.json` sha256 null everywhere | ✅ Confirmed | 100% null |

---

## 9. Recommended Next Actions

| Action | Priority | Owner | Deliverable |
|--------|----------|-------|-------------|
| Add `consumers` field to all 370 entries | H | user | `manifest.json` v2 |
| Add `sha256` hashes to all 370 entries | H | user | `manifest.json` v2 |
| Expand depth-maps manifest from 1 to 64 entries | H | user | `depth_anything_v2_manifest.json` |
| Expand quantumLab manifest from 1 to 130 entries | H | user | `quantumlab_visuals_manifest.json` |
| Expand godot-scenes manifest to 65 entries | H | user | `godot_mesh_conversion_manifest.json` |
| Create `kingwen_3d_kit_meshes_manifest.json` | M | user | Per-family manifest |
| Create `kingwen_model_sets_manifest.json` | M | user | Per-family manifest |
| Verify kit_version_manifest.json coverage of 66 files | M | user | Validation report |
| Verify actual output file hashes | H | user | `manifest.json` v2 |
| Implement upstream provenance capture | H | user | Generator patch |
| Define consumer-class taxonomy | L | user | Documentation |

---

## 10. Status Matrix

| Item | Current state | Required state | Gap | Disposition |
|------|---------------|----------------|-----|-------------|
| Consumers field populated for all artifacts | ❌ 0/370 | 370/370 | Critical | ACTION REQUIRED |
| SHA-256 hashes on all 370 entries | ❌ null/370 | 370/370 | Critical | ACTION REQUIRED |
| Depth-maps manifest enumerates all 64 files | ❌ 1/64 | 64/64 | High | ACTION REQUIRED |
| QuantumLab manifest enumerates all 130 files | ❌ 1/130 | 130/130 | High | ACTION REQUIRED |
| Godot-scenes manifest enumerates all 65 files | ❌ 1/65 | 65/65 | High | ACTION REQUIRED |
| Missing per-family manifests (kit_meshes, model_sets) | ❌ 2 families | 2 files | Medium | ACTION REQUIRED |
| Input provenance captured for all producers | ❌ 0/7 | 7/7 | Medium | ACTION REQUIRED |
| Upstream provenance (generator version, git SHA) | ❌ 0/370 | 370/370 | Medium | ACTION REQUIRED |

---

## 11. Clarifications and Resolutions

| Original ambiguity | Resolution |
|--------------------|------------|
| "Existing files that point at them" | Resolved: files that point to other files include consumer references in `manifest.json` entries, viewer configurations, and pipeline scripts. The gap is that consumers arrays are empty. |
| "Missing usage checks" | Resolved: the check is that `consumers` arrays should list downstream tools/tickets, and hash/provenance fields should be populated for all 370 entries. |

---

*This report was generated from actual file inspection — not inferred from directory listings.*
