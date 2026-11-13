# HEX43-003 — Live Runtime Behavioral Verification Specification

**Trace ID:** HEX43-003  
**Timestamp:** 2026-11-07T07:01:00Z  
**Target:** Hexagram 43 (Breakthrough) — Runtime behavioral verification  
**Preceding trace:** HEX43-002 — Preparation complete; live execution not performed  
**Audit baseline:** Agent-reported file updates; final inspection not independently confirmed

---

## 1. Audit Status

| Trace | Status | Milestone |
|-------|--------|-----------|
| HEX43-001 | COMPLETE | Static producer-consumer trace, source/artifact verification, discrepancy resolution |
| HEX43-002 | PREPARATION COMPLETE | Runtime checkpoints documented; live execution not performed |
| HEX43-003 | PENDING | Live Runtime Behavioral Verification |

**Note:** All evidence in this audit is agent-reported. Files may differ from actual repository state. Live execution is required before runtime claims are accepted.

---

## 2. HEX43-003 Acceptance Criteria

The HEX43-003 run is accepted only if all seven checkpoints below return captured evidence with observable results.

### Checkpoint 1: parseKitToNPC() output preserved

**Required evidence:** Actual `parseKitToNPC(kit_43_json)` output, not just the expected identity.

| Verification | Required observation |
|--------------|---------------------|
| Capture | Raw return value of `parseKitToNPC()` |
| Field check | `kitId`, `hexagramId`, `codename`, `name`, `category`, `action`, `domain`, `kColorMap`, `elementSubset` all present |
| Identity | `hexagramId == 43`, `name == "Breakthrough"` |
| Evidence file | `capture/parseKitToNPC_output.json` |

### Checkpoint 2: PLY loader completion and geometry measurements

**Required evidence:** Loader completion, vertex count, and geometry bounds—not merely a non-error response.

| Verification | Required observation |
|--------------|---------------------|
| Loader | `loader.load()` returns COMPLETE (not error) |
| Vertex count | Parsed geometry has >0 vertices |
| Bounds | Computed bounding box from vertex data |
| Screenshot | Loaded mesh visible in rendered view |
| Evidence file | `capture/PLY_loader_output.json` (vertex count, aabb, center, radius) |

### Checkpoint 3: Material on rendered mesh verified

**Required evidence:** The material on the rendered mesh itself carries color `#C58E09`—not just the configuration value.

| Verification | Required observation |
|--------------|---------------------|
| Material | `MeshStandardMaterial` on the rendered mesh |
| Color | `material.color.getHex() == 0xC58E09` |
| Method | Read `material.color` from the rendered `THREE.Mesh`, not from the kit JSON |
| Evidence file | `capture/material_color.json` |

### Checkpoint 4: Scene membership and actual coordinates

**Required evidence:** The mesh is actually added to the `THREE.Scene` and at the configured grid coordinate.

| Verification | Required observation |
|--------------|---------------------|
| Scene member | Mesh is in `scene.children` array |
| Coordinate | `mesh.position.x == -8` and `mesh.position.z == 6` (or configured value) |
| Identity | `mesh.userData.kitId == 43` |
| Evidence file | `capture/scene_membership.json` |

### Checkpoint 5: Rendered frame and console output

**Required evidence:** A frame is captured and the browser console contains no relevant errors.

| Verification | Required observation |
|--------------|---------------------|
| Frame | Image or data URL of the rendered page |
| Console | Zero ERROR-level messages |
| Mesh | 3D mesh visible in the rendered scene |
| Evidence file | `capture/frame.png` (or data URL) + `capture/console.log` |

### Checkpoint 6: Interaction resolves to Hexagram 43

**Required evidence:** Click or pointer event on the rendered NPC identifies Hexagram 43.

| Verification | Required observation |
|--------------|---------------------|
| Click | Click event on the rendered mesh returns Hexagram 43 |
| Result | `hexagramId == 43` in the interaction response |
| Not generic | Response is tied to the specific clicked mesh |
| Evidence file | `capture/interaction_event.json` |

### Checkpoint 7: Collision-record selection against confirmed schema

**Required evidence:** The correct collision record is selected and its `hexagram_id` field equals 43.

| Verification | Required observation |
|--------------|---------------------|
| Schema | Confirmed field names (e.g., `hexagram_id`) |
| Selection | `selected_physics_record["hexagram_id"] == 43` |
| Evidence file | `capture/collision_record.json` |

---

## 3. Confirmed Schema Gates

Before Checkpoint 7 can be executed, the following facts must be confirmed from the actual `collisionvis_64_npc_physics.json` file:

| Question | Required confirmation |
|----------|----------------------|
| Effective field name | `hexagram_id` or `id` or something else? |
| Record owner field | Does the file contain an owner/id field for record selection? |
| Hexagram 43 record exists | The record for hexagram_id=43 is present in the file |
| Record structure | The record contains the fields the consumer expects |

These must be confirmed before the assertion `assert selected_physics_record["hexagram_id"] == 43` can be adopted.

---

## 4. Evidence Preservation Rule

Failures must be preserved and reported:

1. A mesh-loading failure does NOT erase evidence that identity parsing succeeded.
2. A render error does NOT change the parser output evidence.
3. Any checkpoint failure is recorded with its own evidence file.
4. Partial results are preserved (e.g., checkpoint 1 passes, checkpoint 2 fails).
5. The `capture/` directory is append-only; no evidence is deleted.

---

## 5. Milestone Boundary

| Scope | Criteria |
|-------|----------|
| HEX43-003 | Validates one representative runtime path (Hexagram 43) |
| 64-kit certification | Would require population-level coverage or justified equivalence strategy |

**Rule:** Successful Hexagram 43 runtime verification does NOT certify all 64 kits. Separate milestone.

---

## 6. Execution Sequence

To run HEX43-003:

1. Serve the frontend (`SovereignSceneComposer`) in a browser window
2. Wait for `loadAllNPCs()` to complete and render the 8×8 grid
3. Capture the rendered frame (checkpoint 5)
4. Record the actual `parseKitToNPC()` output (checkpoint 1)
5. Verify PLY loader outputs (checkpoint 2)
6. Read material color from the rendered mesh (checkpoint 3)
7. Assert scene membership and coordinates (checkpoint 4)
8. Capture console output (checkpoint 5)
9. Trigger click interaction (checkpoint 6)
10. Read collision record (checkpoint 7)

**Documentation rule:** Do not modify the 8-phase mesh architecture merely to make the test pass. First establish the actual consumer contract and capture its real behavior.

---

## 7. Reproducibility Metadata

A successful result must be reproducible. Capture the following alongside the seven checkpoints:

| Metadata item | Required value | Source |
|--------------|----------------|--------|
| Repository commit | `git rev-parse HEAD` (KING-WEN-I-CHING-IMMUTABLE-TABLES) | `git rev-parse HEAD` |
| Repository branch | `git branch --show-current` | `git branch --show-current` |
| Runtime version | Node.js version, Python version, browser version | runtime environment |
| PLY asset hash | SHA-256 of `hex43_phase0.ply` (or loaded phase) | `sha256sum DATASETS/kingwen_avatar_meshes/hex43_phaseN.ply` |
| Kit 43 JSON hash | SHA-256 of `kit_43.json` | `sha256sum DATASETS/kingwen_model_sets/kit_43.json` |
| Collision record hash | SHA-256 of `collisionvis_64_npc_physics.json` | `sha256sum DATASETS/collisionvis_physics/collisionvis_64_npc_physics.json` |
| DA-V2 checkpoint hash | SHA-256 of loaded DA-V2 checkpoint file | `sha256sum` of the checkpoint file |

**Evidence file:** `capture/reproducibility_metadata.json`

---

## 8. Failure Preservation Rule

The test must not silently repair any failure. All failures are recorded as evidence:

1. Parse failure → record `parseKitToNPC()` error with full traceback
2. Loader failure → record loader error with URL and response status
3. Material mismatch → record actual color value read from mesh
4. Coordinate mismatch → record actual position of mesh in scene
5. Console error → full error message, stack trace, conditions at time
6. Interaction mismatch → record event dispatched and response received
7. Collision schema mismatch → record actual field names found

**Rule:** Failures are evidence, not obstacles. Do not modify source to make the test pass.

---

## 9. Evidence Artifact Manifest

All captured artifacts are written to `capture/` with their SHA-256:

| Artifact | File | SHA-256 |
|----------|------|---------|
| Parser output | `capture/parseKitToNPC_output.json` | computed |
| PLY loader result | `capture/PLY_loader_output.json` | computed |
| Material color | `capture/material_color.json` | computed |
| Scene membership | `capture/scene_membership.json` | computed |
| Rendered frame | `capture/frame.png` | computed |
| Console log | `capture/console.log` | computed |
| Interaction event | `capture/interaction_event.json` | computed |
| Collision record | `capture/collision_record.json` | computed |
| Reproducibility metadata | `capture/reproducibility_metadata.json` | computed |

---

## 10. Status Summary

| Item | Status |
|------|--------|
| Source-level static trace | COMPLETE (HEX43-001) |
| Documentation | COMPLETE (HEX43-002) |
| Runtime verification spec | COMPLETE (HEX43-003) |
| Live execution | PENDING |
| Acceptance criteria | 7 checkpoints + reproducibility metadata |

---

*Generated: 2026-11-07T07:01:00Z*  
*Audit baseline: agent-reported file updates*  
*Source: KING-WEN-I-CHING-IMMUTABLE-TABLES*