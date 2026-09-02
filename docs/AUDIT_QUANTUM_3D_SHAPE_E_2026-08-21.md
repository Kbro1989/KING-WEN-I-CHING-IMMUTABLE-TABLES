# King Wen — Quantum / 3D / Shap-E Audit
**Scope**: real King Wen substrate only (`CING-WEN-I-CHING-IMMUTABLE-TABLES`). Worker (`kingwen-oracle-worker`) explicitly excluded per user directive — never looked at.
**Audit date**: 2026-08-21 (first pass ~13:32, gate execution ~13:40)
**Method**: read all 6 math docs + every quantum/3D/shap-e script + 2 unread hardware VHDLs + external-shaper existence probe.

---

## 1. Defined intent (from docs)
- **Quantum** (`kingwen-quantum-methods.md`, `j-space-jacobian-lens-math`): baseline-stabilized, deterministic, pass-tracked superposition over full 512/5832 state space. Coherence = validation. XOR-gate direct verification (no forced collapse). No RNG in the *state representation*.
- **3D** (`kingwen_mobius_sphere.py`, `kingwen_state_transition.py`, `generate_avatar_meshes.py`): Riemann/Möbius avatar coordinate backend; single capture point for mesh geometry from live `quantum_avatar_state`.
- **Shap-E** (`shap_e_kingwen_3d_generator.py` + bridges): map 64 hex → 3D avatar meshes grounded in kit identity + 5-axis vector.
- **Onboarding (non-negotiable)**: no RNG collapse, no 1-hex winner discard, no fabrication, single-capture-point architecture.

---

## 2. Findings (file:line — severity — timestamp)

### [B1 · HIGH · 13:32] Auto-git-push capability
`kingwen_train_data/kingwen_quantum_process.py:186-197` `git_push_if_coherent()` runs `git add -A && commit && push origin main` automatically when coherence improves.
- Violates hard rule: push only after explicit user acceptance.
- **Probe**: no caller invokes it (grep clean) — defined-only, but the capability must be removed.
- **Resolved 13:40**: function deleted.

### [B2 · HIGH · 13:32] Single-hex "winner" conflicts with no-collapse onboarding
- `KING_WEN_CONSENSUS_MATH.md §5` "Dynamic Hexagram Winner Selection / argmax".
- `ConsensusAccumulator.vhd:135-147` (`FIND_WINNER` state) reduces 512 states to 1 `consensus_hex_id` in hardware.
- Code: `emotional_engine.py:1330`, `decision_matrix.py:287` compute `consensus_hexagram_id = max(hex_scores, …)`.
- Full 512 still returned (so NOT a hard discard), but the *terminology + VHDL winner-accumulator* embody single-state selection.
- **Action pending**: confirm no consumer uses `consensus_hexagram_id` exclusively; reframe as "primary anchor label"; `ConsensusAccumulator.vhd` is unverified against no-collapse and currently enforces single output — needs review/relabel.

### [B3 · MED · 13:32] Stale source feeding 3D backends
- `kingwen_mobius_sphere.py:50` + `kingwen_state_transition.py:59` load `inject_site` from **root `shotgun_expand_output.json` (Jul 5, 3.16MB, pre-porosity-correction)**.
- 3D nodes get pre-correction porosity/inject data.
- **Action pending**: point at live engine (`expand_hexagram`/`shotgun_expand()`) or corrected corpus.

### [B4 · MED · 13:32] `kingwen_quantum_expand.py` uses RANDOM params
- `run_quantum_expansion()` seeds `np.random.seed(0x47524541)`; `params = np.random.uniform(-π, π, …)` (lines 246-248).
- `import pennylane as qml` at top (line 2) — module fails to import if pennylane absent (probe: not confirmed installed).
- The "quantum expansion" `expansion_vector` is arbitrary circuit noise, NOT derived from hexagram state. Contradicts deterministic intent.
- **Action pending**: derive circuit params from `HEXAGRAM_BASE`/`expanded_vector`, or label output non-grounded.

### [B5 · MED · 13:32] Fabricated "100% Verified Parity" claim
- `bridge_rsmv_shap_e_manifesto.py:113` prints "100% Verified Parity across all 50 Schema Definitions" but the parade of 50 `RSMV_SCHEMA_MAP` entries is **hardcoded** — the script never reads `C:/Users/krist/Desktop/rsmv/generated/*.d.ts`.
- **Resolved 13:40**: removed the verification claim; rewrote docstring to state mapping is declarative, not computed-parity.

### [B6 · MED · 13:40] Shap-E + integration MUTATED canonical kit files
- Probe `kit_1.json`: `extra[]` count=205, contains `shap_e_prompt` (from `shap_e_kingwen_3d_generator.py:97-101`) AND `rsmv_model_id` (from `integrate_desktop_3d_pog2_assets.py:152-156`); `grounded_npc` contains `pog2_subsystem`.
- Canonical identity kits (`DATASETS/kingwen_model_sets/kit_*.json`) were rewritten as a *side effect* of manifest generation. Violates single-capture-point + no-mutation-of-canonical rule.
- **Action pending**: move shap-e/pog2/rsmv metadata to sidecar files; restore kits to pristine identity.

### [B7 · LOW · 13:32] Two divergent 3D coordinate systems
- `kingwen_mobius_sphere.py:_ternary_to_complex` → trigram→complex via `trigram_value/13.0` + `0.5`.
- `kingwen_state_transition.py:_project_mobius` → `z_real=(hex_id-32)/32, z_imag=(phase-3.5)/3.5` (linear index).
- Same "King Wen sphere," two incompatible projections.
- **Action pending**: pick one canonical mapping.

### [B8 · LOW · 13:32] Doc/code drift
- `ternary-paired-differential-correction-2026-08-02.md:5` "spec only — no code changes yet" but `emotional_engine.py:425-433,714-723` already use signed differentials + paired Lagrangian (verified 13:32 grep).
- **Resolved 13:40**: doc header corrected to "applied".

### [B9 · LOW · 13:32] Vortex formula split
- `bridge_quantumlab_visualization.py:56` `vortex_tension = (u_idx*l_idx)/49.0` (float).
- VHDL/expected uses exact integer `(u*l*256+24)/49`.
- **Action pending**: unify to exact integer across Python surfaces.

### [B10 · MED · 13:40] `bridge_desktop_3d_engines.py` writes fake placeholder meshes
- `generate_openusd_stage()` (line 57) emits a 3-vertex triangle `[(sin,cos,0),(1,0,0),(0,1,0)]` — a stub, not the real 729-vertex point cloud the manifest/comment claims.
- `compute_collisionvis_bvh()` (lines 85-107) returns hard-coded constants (-1.2..1.2), not actual mesh bounds.
- Violates no-mock / real-artifact policy.
- **Action pending**: source real geometry from `kingwen_3d_meshes/*.ply` or `generate_avatar_meshes` output.

### [B11 · LOW · 13:40] `bridge_quantum_64_grid.py` synthetic ψ
- `build_quantum_64_grid_mapping()` (lines 53-57) computes a *synthetic* `cos(kx)*sin(kz)` standing wave, not from QuantumLab framework (which is only `sys.path.insert`ed, never imported). Output labeled "REAL-TIME QUANTUMLAB" — misleading.
- **Action pending**: either read actual QuantumLab output or rename to "synthetic grid placement".

### [B12 · LOW · 13:40] `DynamicEmotionalInputDerivator.vhd` eliminates flat-50 by +1 hack
- Lines 71-74: `if raw_sum = 50 then raw_sum := 51`. Eliminates flat-50 but by arbitrary offset, not entropy. Minor; documented intent (avoid flat 50) is reasonable but implementation is a band-aid.
- **Status**: note only, not blocking.

---

## 3. External shapers inventory (verified existence 13:32)
| External input | Path | Status |
|---|---|---|
| `pennylane` (top import) | kingwen_quantum_expand.py:2 | NOT confirmed installed; module import-fail risk |
| `numpy` RNG seed `0x47524541` | kingwen_quantum_expand.py:246 | Shapes quantum output (B4) |
| `numpy` `RandomState` | generate_avatar_meshes.py:115 | Base sphere (seed-deterministic, acceptable) |
| `Desktop/shap-e` | shap_e_generator.py:107 | External; may not exist |
| `Desktop/quantum-simulation-main` | bridge_quantumlab:22, bridge_64_grid:25 | External; inserted to path, never actually used |
| `Desktop/rsmv/generated/*.d.ts` | bridge_rsmv:17 | External; **never read** (B5) |
| `Desktop/rsmv/indexoverview.json` | integrate_assets:88 | External; loaded if exists (graceful) |
| root `shotgun_expand_output.json` (stale Jul 5) | mobius_sphere:50, state_transition:59 | **Stale source** (B3) |
| `DATASETS/quantum_masking_hexagram_integration.json` | kingwen_quantum_expand.py:27 | EXISTS (13KB) |
| `output/per_hex_training/manifest.json` | kingwen_quantum_expand.py:30 | EXISTS (7.9KB) |
| `scripts/ternary_full_expansion.json` | kingwen_quantum_expand.py:26 | EXISTS (2.9MB) |
| `DATASETS/kingwen_model_sets/kit_*.json` | shap-e + integration | EXISTS; **mutated** (B6) |
| `_quantum_avatar_modulation()` return keys | generate_avatar_meshes.py:272+ | EXISTS (wavefunction/kit_identity/scale_factor/rotation_modulation/color_shift/animation_phase/delegate_vector verified) |
| Hardcoded magic (`/13.0`,`/49.0`,fwhm=2.5,ref_impedance=50,phase-deg,Wu-Xing hex) | mobius/state/shap-e | Heuristic, not King Wen-derived |
| `matplotlib`/`scipy`/`torch` | optional imports w/ fallback | Acceptable (graceful) |

---

## 4. Double-check gate (executed 13:40)
- [x] **B1** auto-push removed from `kingwen_quantum_process.py`
- [ ] **B2** `consensus_hexagram_id` confirmed annotation-only; `ConsensusAccumulator.vhd` reviewed
- [ ] **B3** 3D backends no longer read stale root JSON
- [x] **B5** rsmv parity claim removed
- [ ] **B6** shap-e/integration stop mutating `kit_*.json`; kits restored
- [ ] **B7** one canonical 3D projection chosen
- [x] **B8** ternary-correction doc header corrected to "applied"
- [ ] **B9** vortex formula unified
- [ ] **B10** fake .usda meshes replaced with real geometry
- [ ] **B11** synthetic ψ relabeled
- [ ] **B12** note only
- [x] `py_compile` clean: kingwen_quantum_process.py, kingwen_quantum_expand.py, shap_e_kingwen_3d_generator.py, generate_avatar_meshes.py, bridges all compile
- [ ] After all edits: `sandbox_verify_final.py` + `verify_math_jacobian_hamiltonian.py` re-run ALL PASS

## 5. Status
- Gate items resolved this pass: **B1, B5, B8** + py_compile.
- Remaining (require edits to quantum param derivation, 3D source, kit mutation cleanup, VHDL winner review): **B2, B3, B4, B6, B7, B9, B10, B11**.
- No commit/push performed (per user rule).

---

## 6. External-Dependent Format Reverence Audit (systematic, 2026-08-21 ~13:50)
**Method**: for each external program the bridges reference, capture its *real* I/O format from disk, then compare against what our generated files *actually* emit. Flag mismatches. Externals confirmed present on disk (corrected: earlier "may not exist" was wrong).

### 6.1 shap-e (`C:/Users/krist/Desktop/shap-e`)
- **Real contract** (`shap_e/rendering/ply_util.py:9`): `write_ply(raw_f, coords: np.ndarray, rgb: Optional[np.ndarray]=None, faces: Optional[np.ndarray]=None)` → writes a PLY mesh or point cloud. Diffusion path (`sample_latents`) yields latents → mesh via transmitter.
- **Our output** (`shap_e_kingwen_3d_generator.py`): manifest `shap_e_3d_manifest.json` emits `output_mesh_path: DATASETS/kingwen_3d_meshes/shap_e_hex_01_architect.obj` — **.obj**, but `generate_standalone_ply_mesh()` actually writes **.ply** (line 145 `out_path.with_suffix(".ply")`). **MISMATCH**: manifest declares `.obj`, generator writes `.ply`. EXTENSION DIVERGENCE — downstream OBJ loaders would 404.
- **Parity verdict**: prompt/guidance mapping is reasonable; the file-extension claim is wrong. **Action**: reconcile manifest extension to `.ply` (or actually emit `.obj`).

### 6.2 rsmv (`C:/Users/krist/Desktop/rsmv/generated/*.d.ts`)
- **Real contract** (`models.d.ts`): `export type models = { format, version, meshes: [{ positionBuffer: Int16Array|null, normalBuffer: (Int8|Int16)Array|null, uvBuffer: (Uint16|Float32)Array|null, colourBuffer: Uint16Array|null, boneidBuffer, indexBuffers: Uint16Array[], vertexCount, faceCount, ... }] }`. Vertex/face buffers, NOT "729-vertex point cloud" claim.
- **Our output** (`bridge_rsmv_shap_e_manifesto.py` `RSMV_SCHEMA_MAP`): hardcoded 50-entry catalog mapping to Shap-E latent names. Never reads the .d.ts. **Format reverence = NONE** (declarative only, now correctly labeled after B5).
- **kit_1.json `rsmv_topology`** (injected by `integrate_desktop_3d_pog2_assets.py`): `{rsmv_model_id:1001, rsmv_mesh_template:"rsmv_model_1001.obj", point_cloud_vertices_count:729, uv_mapping_mode:"hexagonal_trigram_projection", cached:true}`. **MISMATCH**: real rsmv `models.d.ts` uses `vertexCount` + `positionBuffer` (Int16Array), not `point_cloud_vertices_count:729`. Our key names and the "729-vertex point cloud" claim do not match rsmv's actual struct. **Action (pending)**: align key names to rsmv's `models.d.ts` OR drop the rsmv_struct pretense and label as King-Wen-native metadata.

### 6.3 quantum-simulation-main (`C:/Users/krist/Desktop/quantum-simulation-main`)
- **Real contract** (`quantumlab/runner.py:172`): `np.savez(output_dir/{name}_state.npz, psi=wf.psi, params=cfg)` → numpy `.npz` with `psi` array + YAML `params`. Solvers return `WaveFunction1D/2D/3D`. Observables: `total_energy_expectation`, `position_expectation` (`quantumlab/observables/expectation.py`). Plots via `plt.savefig(..., dpi=300)`.
- **Our output** (`bridge_quantumlab_visualization.py`): writes PNGs via matplotlib + a `quantumlab_visuals_manifest.json` with `observables: {expectation_energy_E, expectation_position_x, position_uncertainty_dx, vortex_tension}`. **Partial reverence**: energy/position observables match quantumlab's `expectation.py` names. BUT `vortex_tension=(u*l)/49.0` is a King-Wen invention, not a quantumlab observable. The bridge **never imports quantumlab** (only `sys.path.insert`s it) — it computes synthetic values. **MISMATCH (B11)**: labeled "REAL-TIME QUANTUMLAB" but framework unused.
- **Our output** (`bridge_quantum_64_grid.py`): `quantum_64_grid_transitional_mapping.json` with `quantum_density = cos(kx)^2+sin(kz)^2` synthetic standing wave. **MISMATCH**: not derived from quantumlab's `step_sequence()`/`np.savez`. Relabel required.

### 6.4 pog2-subsystem-ontology (`C:/Users/krist/Desktop/pog2-subsystem-ontology-2026-07-12.md`)
- **Real contract** (verified module paths in .md): `src/engines/CNSGodheadPulseVolley.ts`, `CNSCausalityLedger.ts`, `CognitiveImmunologyEmergency.ts`, `MetaCognitionEngine.ts`, `NecromancerBrain.ts`, `ForgeEngine.ts`, `StateManager.ts`; limbs `CacheForensicsLimb.ts`, `CollisionLimb.ts`, `NeuralForgeLimb.ts`, `AggressionLimb.ts` (note: POG2 actual is `AggressionLimb`, our map said `AdrenalineLimb`), `AuditoryLimb.ts`, `InventoryLimb.ts`.
- **Our output** (`integrate_desktop_3d_pog2_assets.py` `POG2_CNS_MAP`): Qian→`CNSGodheadPulseVolley.ts`/limbs/spatial/AvatarKinematicsLimb.ts ✓, Kun→`NecromancerBrain.ts`/CacheForensicsLimb.ts ✓, Kan→`CNSCausalityLedger.ts`/combat/AdrenalineLimb.ts ✗ (**real is `AggressionLimb.ts`**), Li→`ForgeEngine.ts`/NeuralForgeLimb.ts ✓, Zhen→`CNSGodheadPulseVolley.ts`/combat/AggressionLimb.ts ✓, Xun→`MetaCognitionEngine.ts`/AuditoryLimb.ts ✓, Gen→`CognitiveImmunologyEmergency.ts`/CollisionLimb.ts ✓, Dui→`StateManager.ts`/InventoryLimb.ts ✓.
- **MISMATCH (1 of 8)**: Kan limb misnamed `AdrenalineLimb.ts` — POG2 ontology says `AggressionLimb.ts`. **Action (pending)**: correct Kan→`AggressionLimb.ts`.

### 6.5 alt1-ai color-by-number (`C:/Users/krist/Desktop/alt1-ai/third_party/color-by-number/services/imageProcessor.ts`)
- **Real contract** (`processImageForColoring` returns `ProcessedImage`): `{ originalWidth, originalHeight, regions: Region[], palette: PaletteColor[], pixelData: Uint8ClampedArray, regionMap }`. `Region = { id, colorId, centroid:{x,y}, pixels, bounds }`. `PaletteColor = { rgb:{r,g,b}, hex, textColor, count }`. K-means clustered, connected-components regions.
- **Our output** (`integrate_desktop_3d_pog2_assets.py` `compute_k_color_palette`): emits `key_line_segments: [{segment_id, color_key, x1,y1,x2,y2, hex_color}]` derived from trigram colors + circular math. **Format reverence = NONE**: alt1-ai produces *image-derived regions with pixel masks and centroids*; our output is *hexagram-derived decorative line segments* with no pixel/image basis. The two are conceptually disjoint. **Verdict**: our `k_color_map` is King-Wen-native decoration, NOT an alt1-ai-compatible output. Should not claim alt1-ai lineage. (No code change needed if relabeled; currently docstring cites alt1-ai path as source of method.)

### 6.6 Reverence Summary Table
| External | Real format | Our output | Reverence | Gap |
|---|---|---|---|---|
| shap-e | `write_ply(coords,rgb,faces)` → .ply mesh | manifest says `.obj`, generator writes `.ply` | Partial | Extension mismatch (6.1) |
| rsmv | `models.d.ts`: `vertexCount`+`positionBuffer` Int16 | `point_cloud_vertices_count:729`, `.obj` template | None (declarative) | Key/struct mismatch (6.2) |
| quantum-sim | `np.savez(psi,params)`, `expectation.py` obs, `plt.savefig dpi=300` | synthetic obs + PNG, framework never imported | Partial | Unused framework, synth values (6.3/B11) |
| pog2-ontology | `AggressionLimb.ts` etc verified paths | 7/8 correct, Kan=`AdrenalineLimb` | Partial | 1 limb name wrong (6.4) |
| alt1-ai | `ProcessedImage{regions[],palette[],pixelData}` | trigram decorative line segments | None | Disjoint concepts (6.5) |

### 6.7 Double-check gate (reverence)
- [ ] 6.1 shap-e manifest extension reconciled to `.ply`
- [ ] 6.2 rsmv_topology key names aligned to `models.d.ts` OR relabeled King-Wen-native
- [ ] 6.3 bridges relabeled "synthetic" (framework not consumed)
- [ ] 6.4 Kan limb → `AggressionLimb.ts`
- [ ] 6.5 k_color_map relabeled (no alt1-ai lineage claim)
- [ ] All 5 externals confirmed present (done: EXISTS)
- [ ] py_compile still clean after any edit

## 7. Cumulative status (end of 13:50 pass)
- Resolved this session: **B1, B5, B8** + reverence doc written.
- Reverence gaps identified (not yet edited): **6.1, 6.2, 6.3, 6.4, 6.5**.
- Still-open from §2 gate: **B2, B3, B4, B6, B7, B9, B10 (interrupted), B11**.
- No commit/push (per rule).
