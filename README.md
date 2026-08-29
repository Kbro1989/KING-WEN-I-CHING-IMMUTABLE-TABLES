# King Wen I Ching — Immutable Tables

> Python · TypeScript · Symbolic Data · 27-Ternary Expansion · 5,832 States

This repository is the **read-only source of truth** for the King Wen state machine:
- **64 canonical binary hexagrams** with upper/lower trigrams, Unicode, category, action
- **8 binary trigrams** mapped to names and symbols
- **27 ternary trigrams** as math-first vectors (`3^3`)
- **729 ternary hexagrams** (`27 × 27`) with 64 canonical subset preserved
- **5,832 resolved states** (`729 × 8`)
- **512 binary resolved states** (`64 × 8`) for backward-compatible consumers

## Folder Map

### `data/`
Canonical immutable tables. Do **not** edit history; append-only only.

| File | Purpose |
|---|---|
| `hexagram-registry.json` | 64 canonical hexagrams with `binary`, `unicode`, `upper_trigram`, `lower_trigram`, `category`, `action` |
| `emotional-weights.json` | 5-axis voice vectors per hexagram: `voiceWeight`, `coherence`, `chaos`, `whimsy`, `darkTone` |
| `temporal-reflections.json` | `past`, `present`, `future` reflection strings per hexagram |

### `scripts/`
The active formalization surface. **5,832-state runtime path** is built here.

| File | Purpose |
|---|---|
| `build_ternary_expansion.py` | Generates `ternary_full_expansion.json` from immutable tables: 27 trigrams, 729 hexagrams, 5,832 resolved states |
| `ternary_full_expansion.json` | **2.9 MB** canonical artifact: full ternary expansion with `trigrams`, `hexagrams`, `resolved` |
| `build_hexagram_skill_cards.py` | Builds per-binary-position `/skill` cards: `{}`/`[]`/`()`/`!` mappings |
| `hexagram_full_expansion.json` | Binary expansion artifact: 64 hexagrams, 512 states, personalities, inversion pairs |
| `ingest_jkd_gutenberg.py` | Batch ingestion runner: `jkd_full_text.txt` → `jkd_ingestion_binary.jsonl` + `jkd_ingestion_ternary.jsonl` |
| `full_hexagram_shotgun.py` | First-parse shotgun blast: 64 expanded + 512 resolved, no early collapse |
| `multi_layer_expand.py` | Layer 1–5 expansion with ternary line options and pool descriptives |
| `open_pool_consensus.py` | Open-pool consensus across all 512 states with tau scoring, no hardcoded booleans |
| `run.py`, `run_all.py`, `run_generators.py` | Convenience runners for generators |
| `generate_engine.py`, `generate_parser.py`, `generate_types.py`, `generate_utils.py` | TypeScript table generators |
| `schauberger_parsing_layers.py` | Viktor Schauberger parsing layer: original mechanism → inversions → drift classification |
| `export_voicebox_training.py` | Voicebox training export |
| `query_layer_probe.py` | Query-layer diagnostics |
| `sandbox_verify_final.py` | Sandbox verification |
| `demo.js` | JS demo |
| `verify_registry.py` | Registry verification |
| `bridge_depth_anything_v2.py` | Bridges 64 QuantumLab plots into Depth Anything V2 16-bit displacement maps and 3D point clouds |
| `prewarm_quantum_wavepackets.py` | Deterministic 1D→2D→3D split-step Fourier operator pre-warming ($U_V, U_T$, 5,832 phase states) |
| `generate_sovereign_world.py` | Generates 64-sovereign macro world with 8 biomes, Schauberger vortices, 6-yao orbiting pellets, and DA-V2 depth metrics |
| `generate_avatar_meshes.py` | Generates 512 binary PLY avatar meshes with Depth Anything V2 depth relief displacement |
| `verify_cross_engine_cli_validation.py` | 8-suite cross-engine validation (OpenUSD, Godot 4, RSMV, Red9, MUGEN, CollisionVis, DA-V2, Wave Packet Pre-Warm) |
| `verify_vhdl_resolver_parity.py` | 512-address functional simulation verifying hardware VHDL resolver parity |
| `verify_output_mismatches.py` | Exhaustive zero-mismatch output audit across 7 subsystem component sets |

### `docs/`
Research and math first, not hand-wavy definitions.

| File | Purpose |
|---|---|
| `immutable-table-math-decoded.md` | 9-bit formula, 512 → 729 expansion, `encode_hex_phase`, `decode_9bit` |
| `j-space-jacobian-lens-math-2026-07-11.md` | J-lens math: `J(a; v) ≈ E[∂y_v/∂a] · Δa`, Hamiltonian energy |
| `kingwen-jspace-domain-layer-2026-07-11.md` | Maps Anthropic’s J-space onto King Wen: 512/5,832 broadcast layer |
| `kingwen-quantum-methods-2026-07-11.md` | Quantum methods: collapse_full_128, superposition capture, tomography |
| `kingwen-superposition-expansion-plan-2026-07-11.md` | 27³ math, first-parse shotgun, layer expansion, consensus |
| `avalokiteshvara-kingwen-mapping.md` | 64-arm mapping for compassionate voice reconfiguration |
| `query_probe/` | Query probe artifacts |

### `src/`
TypeScript/JavaScript consumers of the immutable tables.

| File/Dir | Purpose |
|---|---|
| `index.ts`, `index.js` | Entry points |
| `core/` | Core runtime |
| `parser/` | Binary/ternary parsing |
| `types/` | TypeScript types |
| `utils/` | Utilities |

### `tests/`
Verification tests.

| File | Purpose |
|---|---|
| `oracle.test.ts` | Oracle contract tests |

### `learn/`
Training specs and integration maps. Not code edits.

| File/Dir | Purpose |
|---|---|
| `README.md` | Learning suite overview |
| `specs/` | Blueprint-mined integration specs |
| `exports/` | Integration maps and audits |
| `scripts/` | Learning pipeline scripts |
| `cache_version_correlation_2025_2026.json` | Cache version correlation |
| `runescape_updates_2025_2026.json` | RS cache updates 2025–2026 |

### `kingwen_train_data/`
Training data source layer for Megatron/jarvis/multi-domain learning.

| File | Purpose |
|---|---|
| `kingwen_quantum_process.py` | Hamiltonian energy, Gaussian kernel, trigram frequency weight |
| `superposition_capture.py` | Superposition capture |
| `kingwen_expansion_wrapper.py` | Expansion wrapper |
| `*.jsonl` | Pre-captured train/eval corpora |
| `rsmv_*` | RuneScape model viewer cache format samples |

### `kingwen_train_data_demo2/`
Demo/validation corpora.

| File | Purpose |
|---|---|
| `consensus_gaussian.json` | Per-hexagram/phase 6D stats |
| `expanded_source.jsonl` | Expanded source samples |
| `resolved_source.jsonl` | Resolved source samples |
| `learned_sequential_64.json` | Sequential 64 learned |
| `megatron_weights.csv` | Weight dump |

### `DATASETS/`
Ingestion outputs and raw source text.

| File | Purpose |
|---|---|
| `jkd_full_text.txt` | Tao of Jeet Kune Do — OCR raw source for batch ingestion |
| `jkd_ingestion_binary.jsonl` | 470 binary-mode consult records |
| `jkd_ingestion_ternary.jsonl` | 18 sampled ternary-mode consult records |
| `jkd_ingestion_summary.json` | Aggregate counts |
| `kingwen_consultation_record.json` | Consultation record |
| `depth_maps_16bit/` | 64 × 16-bit PNG depth displacement maps computed via Depth Anything V2 |
| `depth_pointclouds/` | 64 × Open3D PLY point clouds (122,000–131,000 vertices each) |
| `depth_anything_v2_manifest.json` | Master DA-V2 depth telemetry and point cloud manifest linking all 64 hexagrams |
| `quantum_prewarm_cache.npz` | Pre-warmed 1D/2D/3D split-step Fourier operator cache ($U_V, U_T$, $\psi_{\text{warm}}$) |
| `quantum_prewarm_manifest.json` | Pre-warm timing and dimension manifest (64 basis, 512 binary, 729 ternary, 5,832 phase states) |
| `kingwen_avatar_meshes/` | 512 binary PLY avatar meshes ($64 \times 8$ phases) with DA-V2 depth relief sculpting |
| `openusd_stages/` | 64 individual + 1 master OpenUSD stage (`kingwen_sovereign_master_stage.usda`) |
| `godot_scenes/` | 64 individual + 1 master Godot 4 scene (`kingwen_sovereign_world_scene.tscn`) |
| `kingwen_sovereign_world_topology.json` | Master 64-sector macro-world topology with 8 biomes, Schauberger vortices, porosity, and DA-V2 stats |
| `kingwen_sovereign_world_viewer.html` | Interactive 3D macro-world visualizer with live orbital mechanics, telemetry HUD, and DA-V2 inspector |
| `*.csv` | Category, emotional timeseries, save strings, transition graph, trigram reference |

## 6-Layer Deterministic Pipeline Architecture

The King Wen 64 Sovereign Model Engine executes through an exact **6-layer deterministic pipeline** with zero pseudo-RNG, zero 1-hex early collapse, and continuous Hamiltonian field rehydration:

$$\text{Input } \xrightarrow{\text{Layer 2: Parse}} \mathbf{v}_{\text{intent}} \xrightarrow{\text{Layer 3: Pool}} \text{Porosity Bleed} \xrightarrow{\text{Layer 4: Expand}} \text{Hamiltonian Field } \mathcal{H} \xrightarrow{\text{Layer 5: Tag}} \text{64 Coder Pellets} \xrightarrow{\text{Layer 6: Consensus}} \text{Shotgun Telemetry}$$

### Layer 1: Ground Truth & Immutable Tables
- **Source**: `kingwen_ternary_tables_complete.py`
- **Tables**: 8 Trigrams, 64 Canonical Binary Hexagrams (`HEXAGRAM_BASE`), 8 Temporal Phases (`PHASE_INFO`).

### Layer 2: Parse Layer (Coprime Prime Extractor)
- **Moduli**: Coprime prime field $(97, 89, 83, 79, 73)$ driven by ASCII token summation $H = \sum \text{ord}(c)$:
  $$p_{\text{chaos}} = \left(\frac{H \bmod 97}{97.0}\right) \times 0.12, \quad p_{\text{whimsy}} = \left(\frac{\lfloor H/7 \rfloor \bmod 89}{89.0}\right) \times 0.12, \dots$$
- **Seed Vector**: $\mathbf{v}_{\text{intent}} = \text{clamp}(\mathbf{v}_{\text{base}} + \mathbf{v}_{\text{boost}} + \mathbf{p}_{\text{prime}}, 0.0, 1.0)$.

### Layer 3: Pool Layer (Porosity & Injection Dynamics)
- **Overdrive**: $P_{\text{score}} = \text{clamp}\left(\frac{P_{\text{base}}}{4.0} + \left[\frac{p}{8} \cdot \left(0.5 + 0.5 \cdot \frac{E_{\text{in}}}{100}\right)\right] \times 0.5, 0.0, 1.0\right)$.
- **Neighbor Bleed**: $\mathbf{v}_{\text{bleed}} = \text{lerp}(\mathbf{v}_{\text{hex}}, \mathbf{v}_{\text{neighbor\_mix}}, \text{clamp}(P_{\text{norm}} \times 0.7))$.

### Layer 4: Expand Layer (Dual Orthogonal Spaces & Hamiltonian Mechanics)
- **Dual Coordinates**:
  - **512-State Phase Space** ($64 \times 8$): 9-bit binary ROM addressing $(h-1) \times 8 + p$.
  - **729-State Ternary Manifold** ($3^6 = 27 \times 27$): Structural line-state resolution.
  - **5,832 Total Resolved Phase States**: $729 \times 8 = 5,832$.
- **Hamiltonian Mechanics**: $\mathcal{H}(p, q, t) = \sum p_i \dot{q}^i - \mathcal{L}$ where $\mathcal{L} = 0.5|dy| + 0.3|\text{yao\_}dy| + 0.2|\text{changing\_}dy|$.

### Layer 5: Tag Layer (Domain & Identity Registration)
- **Entities**: 64 Coder Specialties, RS3 Actionables, Hermes VHDL Voice Modes, 12-Slot Skill Cards across $27 \times 27$ permutations, and Avalokiteshvara Arms.

### Layer 6: Consensus & Observable Telemetry (No Early Collapse)
- **Gaussian Accumulator**: $\sigma = \max(10^{-9}, \bar{\eta}_{\text{norm}}/2.0)$, $\mathbf{v}_{\text{consensus}} = 0.7 \sum w_j \mathbf{v}_{\text{resolved}, j} + 0.3 \mathbf{u}_{\text{pool}}$.
- **Quantum Wave Packet Observables**: $\psi_i = (v_{\text{resolved}, i} e^{-\tau_i^2/2\sigma^2}) + i ((v_{\text{resolved}, i} - v_{\text{expanded}, i}) \mathcal{H}_{\text{norm}} p_{\text{comp}} 0.1)$.
- **Deterministic 729-Vertex Embedding**: $x_k = (1 + 0.2\sin 6t_k)\cos t_k, y_k = (1 + 0.2\sin 6t_k)\sin t_k, z_k = 0.5\cos(t_k \cdot [(h \bmod 8) + 1])$.

---

## Key Rules

1. **Immutable tables only.** `data/` is append-only. Do not delete or rewrite historical files.
2. **Expansion-first, normalization-last.** Always capture all 64 canonical + 665 ternary hexagrams before any selection layer.
3. **Zero pseudo-RNG or rolls.** All coordinates and vectors are deterministically derived from closed-form algebra and coprime primes.
4. **No 1-hex early collapse.** Emit full 64-pellet shotgun telemetry across all 512/729 states.
5. **No mock/stub/placeholder** in `src/`, `scripts/`, `tests/`.

---

## Quick Start & Verification

```bash
# Run the complete self-contained 18-stage pipeline
python scripts/run_all_unified_pipeline.py

# Build TypeScript core engine and run unit tests
npm run build
npm test

# Run local HTTP expansion server
python expand_server.py

# Run 1D→2D→3D Wave Packet Pre-Warming Engine (Scipy FFT JIT warmup)
python scripts/prewarm_quantum_wavepackets.py

# Bridge QuantumLab plots through Depth Anything V2 (16-bit depth + point clouds)
python scripts/bridge_depth_anything_v2.py --encoder vits

# Generate 64-Sovereign Macro-World (OpenUSD, Godot, Topology, HTML Viewfinder)
python scripts/generate_sovereign_world.py

# Run exhaustive 8-suite cross-engine validation
python scripts/verify_cross_engine_cli_validation.py

# Generate full 3D avatar meshes (729-vertex deterministic geometry + DA-V2 depth relief)
python scripts/generate_avatar_meshes.py --all

# Audit 27x27 unbound persona domains
python scripts/verify_unbound_persona_domains.py

# Audit SaveString V2.1 parity & output mismatches
python scripts/verify_output_mismatches.py

# Verify hardware VHDL 9-bit resolver parity
python scripts/verify_vhdl_resolver_parity.py
```

---

## Outputs & Artifacts

- `scripts/ternary_full_expansion.json` — 27 trigrams, 729 hexagrams, 5,832 resolved states (2.9 MB)
- `DATASETS/full_shotgun_expansion_all.jsonl` — Full 64-hexagram × 8-phase × 3-probe training dataset (1,536 lines, 32.2 MB)
- `DATASETS/quantumlab_plots/` — 64/64 3D Quantum Wave Packet Space-Time surface plots
- `DATASETS/depth_maps_16bit/` — 64/64 16-bit PNG depth displacement maps computed via Depth Anything V2
- `DATASETS/depth_pointclouds/` — 64/64 Open3D PLY point clouds (122k–131k vertices each)
- `DATASETS/kingwen_avatar_meshes/` — 512/512 binary PLY avatar meshes with DA-V2 wave-packet depth relief
- `DATASETS/quantum_prewarm_cache.npz` — Pre-warmed $U_V, U_T$ split-step Fourier operator cache (1D/2D/3D)
- `DATASETS/quantum_prewarm_manifest.json` — Pre-warm telemetry and verification manifest
- `DATASETS/openusd_stages/` — 64 individual + 1 master OpenUSD macro-world stage
- `DATASETS/godot_scenes/` — 64 individual + 1 master Godot 4 3D world scene
- `DATASETS/kingwen_sovereign_world_viewer.html` — Interactive 3D macro-world visualizer with live orbital mechanics, telemetry HUD, and DA-V2 inspector
- `scripts/quantum_avatar_field.html` — Interactive 512-avatar quantum shotgun visualizer with DA-V2 depth relief and pre-warmed wave packet cache
- `DATASETS/kingwen_model_sets/kit_*.json` — 64 NPC 3D model kits with deduplicated extra tags
- `DATASETS/kingwen_64_npc_voice_profiles.json` — 64 designed NPC voice profiles (FastSpeech F0, WaveNet mel channels, KD fidelity)
