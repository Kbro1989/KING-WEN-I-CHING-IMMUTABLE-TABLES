# King Wen Chain: Role Classification & Momentum Map

**Requirement (from operator):** everything in the chain must be shotgun-generatable —
each stage generating *upon the last*, without losing momentum or splitting from the
original intentions fed in.

**Audited:** 2026-10-04, against disk. Every claim below is traceable to a file:line
or a live probe.

---

## The A–E Taxonomy

| Role | Meaning | Test |
|---|---|---|
| **A** | **Input** — values/variables/ranges/pools fed in | Has no upstream dependency in the chain |
| **B** | **Output** — generated artifact | Written to disk, consumed by something |
| **C** | **Translator** — converts representation for an ability | Reads one format, writes another |
| **D** | **Description of needs** — spec/contract | Declares what must exist; runs nothing |
| **E** | **Deployment + measurement** — reusable vs measured-over-time | Ships it, or scores it across time |

---

## Classification of the 3D chain

### A — INPUTS (the intention source)

| Path | Role | Notes |
|---|---|---|
| `data/hexagram-registry.json` | A | 64 identities. Canonical, read-only. |
| `data/emotional-weights.json` | A | 5-axis weight vectors. |
| `data/temporal-reflections.json` | A | Corpus text by hexagram_id. |
| `DATASETS/kingwen_model_sets/kit_{1..64}.json` | A | Embodiment schema. **Currently mutated (B6)** — carries `shap_e_prompt` + `rsmv_model_id` in `extra[]`. |
| `DATASETS/kingwen_3d_meshes/shap_e_hex_{01..64}.ply` | A (nominal) | 729-vert ascii point clouds, **no faces**. Procedural fallback, not diffusion. |
| `DATASETS/depth_maps_16bit/*.png` | A | 64 × 16-bit DA-V2 depth maps (real: std≈57, 701×697). |
| `DATASETS/depth_pointclouds/*.ply` | A | 64 × ~122k-vertex point clouds (real: 4.1 MB each). |
| **`emotional_input` (runtime scalar)** | **A** | The operator's intention. **Enters at exactly one point and stops.** |

### B — OUTPUTS (generated artifacts)

| Path | Role | Carries momentum? |
|---|---|---|
| `DATASETS/kingwen_avatar_meshes/hex{XX}_phase{N}.ply` | B | ✅ geometry yes (real Delaunay, 729 v / 10004 f) |
| `DATASETS/kingwen_avatar_mesh_manifest.json` | B | ❌ **NO** — see Break 1 |
| `godot/meshes/avatar/*.obj` | B | ⚠️ colour only (RGB in `v` line) |
| `godot/import/*.import` | B | n/a (config) |
| `godot/scenes/hexagrams/hex_{XX}.tscn` | B | ❌ **NO** — see Break 2 |
| `DATASETS/godot_scenes/npc_hex_{XX}.tscn` | B | ❌ **NO** — see Break 2 |
| `DATASETS/openusd_stages/npc_hex_{XX}.usda` | B | ❌ **NO** — see Break 2 |
| `DATASETS/kingwen_rsmv_models/hex_{XX}_models.json` | B | ❌ **NO** — see Break 3 |
| `DATASETS/collisionvis_physics/*.json` | B | ❌ geometry only |
| `DATASETS/sandbox_mugen_red9_bridge_manifest.json` | B | ⚠️ `motion_prompt` text only |

### C — TRANSLATORS (the abilities)

| Path | Role | Reads | Writes |
|---|---|---|---|
| `scripts/full_hexagram_shotgun.py` | C | emotional_input | 64 expanded + 512 resolved |
| `scripts/expand_hexagram` (via `emotional_engine.py`) | C | hexagram_id, phase_bits, emotional_input | `quantum_avatar_state` |
| `scripts/generate_avatar_meshes.py` | C | `quantum_avatar_state` + depth + kit | 512 PLY + manifest |
| `scripts/bridge_ply_to_godot_mesh.py` | C | PLY | OBJ + `.import` |
| `scripts/shap_e_kingwen_3d_generator.py` | C | kit identity | PLY (procedural fallback) |
| `scripts/transform_object_rsmv.py` | C | PLY | rsmv `models` wire |
| `scripts/bridge_desktop_3d_engines.py` | C | `HEXAGRAM_BASE` (static) | `.tscn` + `.usda` + BVH |
| `scripts/generate_godot_project.py` | C | OBJ + registry | Godot project |
| `scripts/bridge_depth_anything_v2.py` | C | quantumlab plots | depth PNG + PLY |
| `scripts/generate_sovereign_world.py` | C | shotgun_expand | world topology |

### D — DESCRIPTION OF NEEDS

| Path | Role | State |
|---|---|---|
| `KINGWEN_AGENT_ONBOARDING.md` | D | ⚠️ 8 wrong paths; **zero 3D coverage** |
| `README.md` | D | ✅ 3D coverage present (lines 45–136) |
| `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` | D | ✅ Accurate, already flags B6 |
| `docs/cross-verification-checklist-2026-09-01.md` | D | ✅ |
| `rsmv/generated/models.d.ts` | D | ✅ Canonical consumer contract |
| `generated/*.d.ts` (rsmv) | D | ✅ |

### E — DEPLOYMENT + MEASUREMENT

| Path | Role | State |
|---|---|---|
| `scripts/verify_cross_engine_cli_validation.py` | E | ✅ 8 suites, now hardened |
| `scripts/verify_output_mismatches.py` | E | ✅ |
| `scripts/verify_registry.py` | E | ✅ |
| `scripts/run_all.py` | E | ❌ **5 of 36 generators orchestrated** |
| `scripts/validate_wavepacket_manifest.py` | E | ✅ |
| `npm test` | E | ✅ 2 tests (was 0) |

---

## THE MOMENTUM MAP — where intention is lost

```
emotional_input ──┐
                  ▼
        expand_hexagram()  ──► quantum_avatar_state {wavefunction, delegate_vector}
                  │
                  ▼
   generate_avatar_meshes.py  ──► PLY (geometry ✅)  +  manifest
                  │                     │
                  │                     └──✂ BREAK 1: manifest drops emotional_input
                  │                              (records wavefunction + delegate_vector,
                  │                               but NOT the input that produced them)
                  ▼
          PLY geometry only
                  │
        ┌─────────┼──────────┬───────────────┐
        ▼         ▼          ▼               ▼
   bridge_ply   transform  bridge_desktop  generate_godot
   _to_godot    _object    _3d_engines     _project
        │         _rsmv        │               │
        │           │          └──✂ BREAK 2: never reads the manifest.
        │           │                    Reads HEXAGRAM_BASE (static) and
        │           │                    hardcodes colors: 0.85/0.9/1.0 sky,
        │           │                    (0.5,0.5,0.6) ambient, gold/teal/rose/blue
        │           │
        │           └──✂ BREAK 3: reads PLY float+colour only.
        │                    wavefunction / delegate_vector never enter
        │                    the rsmv wire struct.
        ▼
   OBJ (colour survives) ──► Godot scenes: 8 MeshInstance3D, NO semantic payload
```

### Break 1 — the manifest is an index, not a lineage record

`generate_mesh_manifest()` (`generate_avatar_meshes.py:515`) writes per-mesh:
`hexagram_id, phase_bits, phase_temporal, codename, kit_codename, ply_filename,
ply_path, vertex_count, face_count, scale_factor, rotation_modulation, color_shift,
animation_phase, wavefunction, delegate_vector`

**Absent:** `emotional_input`, `request_text`, `expanded_vector`, `resolved_vector`.

Top level is only `schema_version / generated_at / total_meshes / meshes`.
`generated_at` is a float epoch (`1788018434.9`) — not even a readable timestamp.

**Consequence:** 512 meshes exist whose generating intention is unrecorded. You cannot
re-derive which `emotional_input` produced which mesh, and you cannot re-run "upon the
last" because the last is not described.

### Break 2 — the engine bridges regenerate from static identity

`bridge_desktop_3d_engines.py` imports only `HEXAGRAM_BASE` (static registry) and
never opens `kingwen_avatar_mesh_manifest.json`. Its scenes therefore describe
*identity* (hexagram_id, name, category, action, grid position) — never *state*.

This is why the 64 NPC scenes are indistinguishable in payload from the 64 hexagram
scenes: both are generated from the same static table.

### Break 3 — the rsmv wire drops the semantic layer

`transform_object_rsmv.py` reads PLY float positions + uchar colour and repacks to
Int16 + RGB555. `wavefunction` and `delegate_vector` have no field in the struct, so
they are silently discarded.

---

## The one path that DOES carry momentum

`expand_server.py` `/3d/` (lines 445–468) reads the manifest and returns
`manifest_entry` verbatim, which includes `wavefunction` + `delegate_vector`.

So: **the live API path preserves the field; the static artifact path does not.**
Consumers that fetch `/3d/{hex}/{phase}` get momentum. Consumers that read the `.tscn`
/ `.usda` / `_models.json` files off disk get identity only.

This is the split. Both paths claim to represent the same 512 states.

---

## Orchestration gap — the chain cannot currently run as a chain

| Metric | Value |
|---|---|
| Generator/bridge scripts in `scripts/` | **36** |
| Orchestrated in `run_all.py` | **5** (`generate_types`, `generate_utils`, `generate_parser`, `generate_engine`, `generate_tests`) |
| 3D chain scripts orchestrated | **0** |

`run_all.py` covers only the TypeScript engine codegen. The entire 3D chain
(`generate_avatar_meshes` → `bridge_ply_to_godot_mesh` → `transform_object_rsmv` →
`bridge_desktop_3d_engines` → `generate_godot_project` → `generate_sovereign_world`)
has **no runner**. Each script must be invoked by hand, in an order nothing declares.

Result: artifacts drift out of sync. `kingwen_rsmv_models/` is dated **2026-08-21**;
the engine was committed **2026-10-03**. Six weeks of drift, because nothing regenerates
the chain.

---

## What "shotgun generatable upon the last" requires

1. **Lineage record.** Manifest must record the input that produced each artifact:
   `emotional_input`, `request_text`, `expanded_vector` (5-axis), `resolved_vector`,
   and a `parent_artifact` pointer. Without this there is no "last" to generate upon.

2. **State-carrying bridges.** `bridge_desktop_3d_engines.py` must read the manifest
   and emit `wavefunction` / `delegate_vector` into scene metadata instead of
   hardcoded colours. A Godot scene should be able to answer "what emotional state
   produced me?"

3. **Semantic passthrough in translators.** `transform_object_rsmv.py` should carry the
   5-axis vector alongside the wire struct (sidecar or `_meta`), so the rsmv consumer
   is not blind to state.

4. **One orchestrator.** A single runner declaring the full order, so the chain is
   regenerated end-to-end and cannot drift 6 weeks.

5. **No silent fallbacks.** `try_run_shap_e_live()` falls back to a procedural spiral on
   `ImportError` — but torch and shap_e *are* importable here. The fallback masks a
   runnable path and silently downgrades output. Fallbacks must announce themselves in
   the artifact (`"source": "procedural_fallback"`), never silently.

---

## Invariant to hold

> Every artifact must record the intention that produced it, and every translator must
> pass that intention through. An artifact that cannot name its input has already
> split from the chain.

## Verification hooks

```bash
cd KING-WEN-I-CHING-IMMUTABLE-TABLES

# Does the manifest record lineage?
python3 -c "import json;d=json.load(open('DATASETS/kingwen_avatar_mesh_manifest.json'));print('emotional_input' in d['meshes'][0])"

# Does a Godot scene carry state?
grep -c "wavefunction\|delegate_vector" DATASETS/godot_scenes/npc_hex_01.tscn

# Is the chain orchestrated?
grep -c "generate_\|bridge_" scripts/run_all.py

# Is the rsmv wire stale?
stat -c '%y' DATASETS/kingwen_rsmv_models/hex_01_models.json
```
