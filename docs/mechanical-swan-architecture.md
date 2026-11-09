# The Mechanical Swan — Formal Architecture Record
**Date:** 2026-11-07
**Project date:** 2026-11-06
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`
**Branch:** `v2-remediation`

---

## 1. Definition

> The Mechanical Swan is a unified computational system composed of independently bounded capability wings. Its immutable-ternary core provides shared state resolution and expansion; each wing transforms defined inputs into domain-specific outputs for a defined consumer. Shared infrastructure does not imply shared scientific purpose, and architectural integration does not imply validation or certification.

**Governing principle:** Unity at the orchestration level. Separation at the evidence and domain level.

---

## 2. Four Architectural Layers

| Layer | Evidence | Responsibility |
|-------|----------|----------------|
| Core engine | `KING_WEN_TABLES.py`, `kingwen_ternary_tables_complete.py`, `full_hexagram_shotgun.py` | Immutable state definitions, expansion, resolution, decision logic |
| Capability execution | `scripts/`, `src/`, `functions/`, `runtime/` | Math recovery, depth processing, OCR, 3D, audio, agents, orchestration |
| Artifact substrate | `DATASETS/`, `data/`, `output/`, `cache/`, `references/` | Inputs, intermediate representations, outputs, baselines, manifests, provenance |
| Governance and verification | `docs/`, `tests/`, `scripts/evaluation/`, `scripts/validators/` | Contracts, audit evidence, regression tests, validation, certification gates |

The repository supports the capability-wing model with four distinct architectural layers. This is the correct direction for a system with this many interacting components.

## 3. Unified Program Structure

### 2.1 Program Identity

| Attribute | Value |
|-----------|-------|
| Program | King Wen (The Mechanical Swan) |
| Program type | Unified computational system |
| Core | Immutable-ternary state machine |
| State cardinality | 64 × 8 = 512 resolved states |
| Expansion layers | 512 → 729 (ternary) → 5,832 (ternary+temporal) → 46,656 (routes) |
| Shared orchestration | Single program, multiple capability wings |

### 2.2 Immutable-Ternary Core (Shared)

The immutable-ternary core is the shared computation substrate. It is read-only and consumed by all wings.

| Component | File(s) | Output | Consumers |
|-----------|---------|--------|-----------|
| Canonical immutable tables | `immutable-tables/` | 64 hexagrams × 8 phases | All wings (read-only) |
| Emotional engine | `emotional_engine.py` | 5-axis vector, porosity, consensus | Voice, agents, audio |
| State resolution | `main.py`, `state.py` | Current state + historical state | All wings |
| Math contracts | `math_contract.py` | Parse status, structural status, backend status, solution status | Math wing, ingestion |
| Ternary expansion | `multi_layer_expand.py`, `kingwen_quantum_expand.py` | 729, 5,832, 46,656 states | All wings |

### 2.3 Shared Infrastructure

| Infrastructure | Role | Consumers |
|---------------|------|-----------|
| Journals | Crop processing, run tracking | Math wing |
| OCR pipeline | Text extraction for math evidence | Math wing |
| Corpus | 243 papers, 4,921 candidates | Math wing |
| Provenance | SHA-256 lineage, metadata | All wings |
| Migration records | `migration_manifest_20261107_readonly.json` | All wings |

---

## 3. Capability Wings

### 3.1 Math Recovery — PDF/HTML/Equation Evidence

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ⚠️ **Running — 137/137 failed (Run 1 checkpoint); 20/137 completed, 117/137 failed (Run 2)** |
| Artifact status | ✅ Preserved (journals, manifests, pipelines) |
| Validation status | ⚠️ **Untested as a complete pipeline** |
| Consumer | PDF fidelity inspection |

**Producer scripts:**
- `render_fullpage_depth.py` — 16 fullpage renders
- `controlled_depth_run.py` — 137 controlled crop renders
- Script schema: `scripts/render_fullpage_depth.py`, `scripts/controlled_depth_run.py`, `scripts/pdf_depth_lineage_audit.json`

**Input lineage:** Benchmark PDFs (245 papers, 4,921 candidates) → PDF crops → DA-V2 depth inference → depth maps

**Output population:** `DATASETS/PDF_FIDELITY_RENDERINGS/` — 64 fullpage + 137 crop renders

**Validation target:** Document-region fidelity (spatial reconstruction of formula regions)

**Known defects:**
- Run 1: 137/137 failed (checkpoint load path issue)
- Run 2: 20/137 completed, 117/137 failed (output validation error, OSError: [Errno 22])
- `pdf_depth_lineage_audit.json` — 152 baseline crops, 15 processed, 137 unprocessed

**Evidence status:** The pipeline is running but the controlled-run execution is incomplete. Do not certify as fully producing artifacts until newer execution resolves the discrepancy.

### 3.2 Quantum Depth — QuantumLab → Depth/Point Clouds

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running (128 artifacts produced: 64 PNGs + 64 PLYs) |
| Artifact status | ✅ Preserved (SHA-256 recorded) |
| Validation status | ⚠️ Partial (generated, not independently verified) |
| Consumer | King Wen 3D/avatar visualization |

**Producer scripts:**
- `bridge_depth_anything_v2.py` — 64 hexagram depth maps + PLY point clouds
- Schema: `DATASETS/quantum_depth/`

**Input lineage:** QuantumLab 3D surface plots (`quantum_3d_hex_XX.png`) → DA-V2 inference → 16-bit depth maps + point clouds

**Output population:** `DATASETS/quantum_depth/`
- `depth_maps_16bit/` — 64 PNGs (1.7–1.9 MB each)
- `depth_pointclouds/` — 64 PLY files (4.1–4.4 MB each)

**Validation target:** Spatial reconstruction (3D geometry consistency)

**Checkpoint:** `Upgraded-Depth-Anything-V2/checkpoints/depth_anything_v2_vits.safetensors` (SHA-256: `a7c1a8c8cdd7885fb8391069cd1eee789126c8d896f7de6750499b1097f817ea`, 49,595,202 bytes)

### 3.3 Audio — DSP Clock / Voice / Cadence

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running |
| Artifact status | ✅ Preserved |
| Validation status | ⚠️ Untested as standalone |
| Consumer | Agent cadence, voice rendering |

**Producer scripts:**
- `dsp_clock.py` — -640Hz DSP clock (negative-frequency phasor)
- `kingwen_game_tick.py` — game tick driver
- Voice routing surfaces (agent TTS, voice synthesis)

**Input lineage:** King Wen state deltas + signer weights → DSP clock → audio signal

**Output population:** Audio signals (voice, clock cadence, agent audio)

**Core DSP formula:** `-640 Hz` negative-frequency phasor (healing clock)

### 3.4 3D/Vertex — State Geometry / Avatar Rendering

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running |
| Artifact status | ✅ Preserved |
| Validation status | ⚠️ Untested as standalone |
| Consumer | Avatar rendering, GGWave bridge |

**Producer scripts:**
- `kingwen_mobius_sphere.py` — Riemann sphere coordinates
- `kingwen_state_transition.py` — state transition logic
- Avatar compute surfaces

**Input lineage:** King Wen state (hex × phase × mask × coherence × porosity) → Riemann sphere coordinates

**Output population:** `DATASETS/quantum_avatar_state/` (state JSON), `DATASETS/quantum_depth/` (mesh, PLY)

**Core math:** Möbius transformation, stereographic projection, elliptic period-4

### 3.5 Agents — Consults / Execution / Lineage

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ⚠️ Partial (consults produced, execution lineage tracked) |
| Artifact status | ✅ Preserved |
| Validation status | ⚠️ Partial |
| Consumer | Jarvis agent execution |

**Producer scripts:**
- `kingwen_oracle_consult_tool.py` — consult tool
- `kingwen_game_tick.py` — game tick
- `journey_executor.py` — journey execution

**Input lineage:** Journeys (cluster affinity) → King Wen consult → agent instructions

**Output population:** Consult payloads, save-string lineage, agent directives

**Key contract:** Consult produces 64-hex + 512-resolve payload; agent picks top-k

### 3.6 I-Ching — Hexagram and Phase Computation

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running (all 64 hexagrams, 512 resolved) |
| Artifact status | ✅ Preserved |
| Validation status | ✅ Verified |
| Consumer | All wings (via shared core) |

**Note:** I-Ching is classified as a core computational subsystem, not an ordinary wing. All other wings consume its capabilities.

**Producer scripts:**
- `immutable-tables/` — canonical immutable tables (read-only)
- `emotional_engine.py` — emotional vector, consensus
- `decision_matrix.py` — consensus computation

**Input lineage:** Immutable tables → state resolution → hexagram/phase → emotional weights

**Output population:** 512 resolved states, 5-axis vector, porosity, 64-hex expansion

**Core contract:** 64 × 8 = 512 resolved states; all 64 hexagrams exist simultaneously

### 3.7 Ternary Expansion — 729 / 5,832 / Route Expansion

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running |
| Artifact status | ✅ Preserved |
| Validation status | ✅ Verified |
| Consumer | All wings via compute |

**Producer scripts:**
- `multi_layer_expand.py` — 512 → 729 ternary
- `kingwen_quantum_expand.py` — 512 → 5,832, 46,656
- `ternary_full_expansion.json` — canonical expansion (2.9 MB)

**Input lineage:** 512 resolved states + phases + emotional weights → ternary expansion

**Output population:** `DATASETS/ternary_full_expansion.json` (2.9 MB, 729 hexagrams, 5,832 resolved states, 46,656 routes)

**State cardinality:**
- 512 resolved (binary layer)
- 729 ternary (3^6)
- 5,832 resolved (729 × 8)
- 46,656 routes (64 × 729)

### 3.8 Presentation — Widgets / Manifests / Inspection

| Attribute | Value |
|-----------|-------|
| Architecturally built | ✅ |
| Execution status | ✅ Running |
| Artifact status | ✅ Preserved |
| Validation status | ⚠️ Untested |
| Consumer | Human visual inspection |

**Producer scripts:**
- `quantum_avatar_field.html` — quantum avatar field
- `fullpage_depth_manifest.json` — fullpage depth manifest
- `math_xml_output.json` — equation manifests

**Input lineage:** Visualization layer (no computation; reads producer artifacts)

**Output population:** HTML/JSON manifests, visual inspection surfaces

**Note:** Presentation is classified as an interface surface, not a computational wing.

### 3.9 Supporting Infrastructure — Journals · OCR · Corpus · Provenance · Migration Records

| Infrastructure | Role | Consumers |
|---------------|------|-----------|
| Journals | Crop processing, run tracking | Math wing, DA-V2 |
| OCR pipeline | Text extraction (Pix2Text, RapidOCR, Tesseract) | Math wing |
| Corpus | 243 papers, 4,921 candidates | Math wing, ingestion |
| Provenance | SHA-256 lineage | All wings |
| Migration records | `migration_manifest_20261107_readonly.json` | All wings |

**Artifact:** `DATASETS/migration_manifest_20261107_readonly.json` (96 KB)

---

## 4. DA-V2 Distinction

The two DA-V2 applications share an inference implementation, not a scientific purpose.

| Dimension | Quantum depth | Math PDF depth |
|-----------|---------------|----------------|
| Population | QD-001 | MD-001 |
| Input | QuantumLab plots | Math paper pages/crops |
| Output | 16-bit depth maps + PLY point clouds | Depth-rendered images |
| Consumer | 3D/avatar system | PDF fidelity inspection |
| Validation target | Spatial reconstruction | Document-region fidelity |
| Retention | Preserved archive | Diagnostic evidence |

**Key principle:** A common helper does not make the outputs interchangeable.

---

## 5. State Cardinalities

### 5.1 Expansion Layers

| Layer | Input | Expansion Operation | Output |
|-------|-------|--------------------|--------|
| Binary | 64 hexagrams | × 8 phases | 512 resolved (64×8) |
| Ternary | 27 trigrams | × 27 trigrams | 729 hexagrams (3^6) |
| Ternary + temporal | 729 hexagrams | × 8 phases | 5,832 resolved (729×8) |
| Route | 729 hexagrams | 6 permutations | 46,656 routes (64×729) |

**Clarification:** 512 (binary) and 729 (ternary) are different expansion layers. The 8-phase expansion produces 5,832 from 729, not from 512.

### 5.2 Phase Mapping

| Phase | Encoding |
|-------|----------|
| Past | 'a' |
| Present | 'p' |
| Future | 'f' |

### 5.3 Yodo Vocabulary (9-member)

| Position | Yina | Old yin | Present yin | New yin |
|----------|------|---------|-------------|---------|
|          | yang | young yin | stable yin | old yin |
| Row 1    | yang | young yin | stable yin | old yin |
| Row 2    | yang | young yang | stable yang | old yang |
| Row 3    | yang | young yang | stable yang | old yang |

---

## 6. Status Dimensions

### 6.1 Dimension Definitions

| Dimension | Values | Description |
|-----------|--------|-------------|
| `ARCHITECTURE` | designed / implemented | Is the wing architecturally defined? |
| `EXECUTION` | not-run / running / completed / failed | Current execution state |
| `ARTIFACT` | absent / generated / preserved / hashed | Artifact state |
| `VALIDATION` | untested / tested / independently verified / certified | Validation depth |
| `CONSUMER` | disconnected / integrated / verified | Downstream integration |

### 6.2 Wing Status Matrix

| Wing | ARCHITECTURE | EXECUTION | ARTIFACT | VALIDATION | CONSUMER |
|------|-------------|-----------|----------|------------|----------|
| **Math Recovery** | implemented | running (partially failed) | preserved | untested | integrated |
| **Quantum Depth** | implemented | running (128 artifacts) | preserved (hashed) | partially tested | integrated |
| **Audio** | designed | running | preserved | untested | integrated |
| **3D/Vertex** | designed | running | preserved | untested | integrated |
| **Agents** | implemented | partial (consults) | preserved | partially tested | integrated |
| **I-Ching** | implemented | running | preserved | independently verified | integrated (core) |
| **Ternary Expansion** | implemented | running | preserved | independently verified | integrated |
| **Presentation** | designed | running | preserved | untested | connected (human) |
| **Supporting** | implemented | running | preserved | untested | integrated |

### 6.3 Status Interpretation Rules

1. **Architecture ≠ execution**: A wing can exist architecturally while a producer is unverified or failing.
2. **Execution ≠ artifact**: A script may run successfully but produce no artifacts (or vice versa).
3. **Artifact ≠ validation**: On-disk files exist, but independent verification may be pending.
4. **Validation ≠ certification**: Tested is not certified. Certified is the highest level.
5. **Consumer ≠ integrated**: A wing may have a registered consumer without that consumer being verified.

---

## 7. Shared-Core Boundary

### 7.1 Dependency Flow

```
Impure-ternary core (immutable tables, emotional engine, state resolution, expansion)
  ↑
  ■■■ All wings (arrow = "consumes")
```

**No wing imports another wing.** Each wing consumes the immutable-ternary core directly.

### 7.2 Communication Contract

| Interaction | Format |
|------------|--------|
| State resolution | Typed JSON payload (hex × phase × mask × coherence × porosity) |
| Emotional vector | 5-axis vector (voiceWeight, coherence, chaos, whimsy, darkTone) |
| Porosity | 0-1 float |
| Save-string | `KW64_SAVE_STRING_V2.1::...::SHA256` |
| Trajectory | Categorical label (`past|present|future`) |
| Agreement temporal | Categorical label |

### 7.3 No Cross-Wing Imports

- Math wing does NOT import quantum wing
- Quantum wing does NOT import math wing
- Audio wing does NOT import 3D wing
- Each wing has its own producer script, input schema, output schema, and consumer contract

---

## 8. Recommended Documentation File Layout

```
KING-WEN-I-CHING-IMMUTABLE-TABLES/
├── docs/
│   ├── mechanical-swan-architecture.md      ← THIS FILE
│   ├── kingwen-state-cardinalities.md       ← NEW: cardinality cross-reference
│   ├── kingwen-wing-status-matrix.md        ← NEW: per-wing status
│   └── ...
├── immutable-tables/                         ← Core (read-only)
├── scripts/                                  ← Producer scripts
├── DATASETS/                                 ← Artifacts
│   ├── quantum_depth/
│   ├── PDF_FIDELITY_RENDERINGS/
│   ├── quantum_avatar_state/
│   ├── migration_manifest_20261107_readonly.json
│   └── ...
└── learn/                                    ← Training data
```

---


---

## 9. Artifact and Dataset Layer

> The repository is a 5.22 GB computational workspace, while `DATASETS` is a 1.65 GB evidence and artifact domain. This layer owns and tracks all artifacts by population, producer, lineage, and preservation status.

### 9.1 Filesystem Metrics (Windows Folder Properties)

| Measurement | Repository | DATASETS |
|------------|------------|----------|
| Logical size | 5.22 GB | 1.65 GB |
| Size on disk | 5.15 GB | 1.66 GB |
| Files | 303,940 | 4,277 |
| Folders | 850 | 121 |

**Key facts:**
- `DATASETS` = 31.7% of the repository by logical size
- `DATASETS` = 1.4% of the repository's file count (4,277 of 303,940)
- Difference between logical and on-disk is approximately 3.83 GB (filesystem allocation overhead)
- These are Windows folder-property measurements, not a verified inventory of unique scientific artifacts

### 9.2 Artifact Categories

| Category | Description | Representative Artifacts |
|----------|-------------|--------------------------|
| **Source artifacts** | Immutable tables, source PDFs, original research inputs | `immutable-tables/`, `immutable-table-math-decoded.md` |
| **Derived artifacts** | Depth maps, PLY point clouds, crop renders, parsed equations | `quantum_depth/`, `PDF_FIDELITY_RENDERINGS/`, `processing-output/` |
| **Execution evidence** | Journals, manifests, logs, test outputs | `pdf_depth_runs/`, `acked_evidence/`, `digest/` |
| **Diagnostic artifacts** | OCR experiments, temporary analyses, isolated runs | `ocr_polarity_ablation/`, `d1_diagnostic_2026-11-06/`, `ocr_tesseract_results.json` |
| **Presentation artifacts** | Widgets, visualizations, inspection outputs | `quantum_avatar_field.html`, `fullpage_depth_manifest.json` |

### 9.3 Artifact Population Schema

Each artifact in this layer must carry:

```json
{
  "artifact_id": "QD-001-001",
  "population_id": "QD-001",
  "producer": "bridge_depth_anything_v2.py",
  "input_lineage": "quantumlab_plots/quantum_3d_hex_001.png",
  "output_type": "quantum_depth_16bit_map",
  "consumer": "King Wen 3D/avatar visualization",
  "preservation_status": "hashed"
}
```

### 9.4 Artifact Ownership

| Artifact | Population | Owner | Preservation Status |
|----------|------------|-------|---------------------|
| depth_maps_16bit/ (64 PNGs) | QD-001 | bridge_depth_anything_v2.py | hashed |
| depth_pointclouds/ (64 PLYs) | QD-001 | bridge_depth_anything_v2.py | hashed |
| PDF_FIDELITY_RENDERINGS/ (fullpage + crops) | MD-001 | render_fullpage_depth.py, controlled_depth_run.py | preserved |
| pdf_depth_runs/ (journals + execution records) | MD-001 | controlled_depth_run.py | preserved |
| quantum_avatar_field.html | Presentation | own consumption | preserved |
| fullpage_depth_manifest.json | Presentation | render_fullpage_depth.py | preserved |

### 9.5 Verification: Read-Only Inventory Reconciliation

**Rule:** Do not move or delete anything. Verify counts against documented populations only.

| Population | Documented count | Filesystem count | Status |
|------------|------------------|------------------|--------|
| QD-001 depth maps | 64 | verify | pending |
| QD-001 PLY clouds | 64 | verify | pending |
| MD-001 fullpage renders | 16 | verify | pending |
| MD-001 crop renders | 137 | verify | pending |
| OCR-001 | separate evidence | verify | pending |

**Reconciliation steps (read-only):**
1. Count files by population in `DATASETS/`
2. Verify SHA-256 for QD-001 artifacts
3. Report any discrepancies as unverified, not deleted
4. Do not modify anything

### 9.6 Repository Boundary

| Scope | Files | Size | Role |
|-------|-------|------|--------|
| Full repository | 303,940 | 5.22 GB | Computational workspace + evidence |
| DATASETS/ | 4,277 | 1.65 GB | Evidence and artifact domain |

**Distinction:** The repository is the computational workspace; `DATASETS` is the evidence and artifact domain. Not every file is a scientific artifact — there are source files, dependencies, environments, caches, and generated artifacts alike. The formal architecture should treat `DATASETS` as the artifact layer only.

## 9. Summary

The Mechanical Swan is one unified program with independently bounded capability wings. The immutable-ternary core provides shared state resolution and expansion; each wing transforms defined inputs into domain-specific outputs for a defined consumer.

| Wing | Architecture | Execution | Artifact | Validation | Consumer |
|------|-------------|-----------|----------|------------|----------|
| Math Recovery | implemented | running (partial) | preserved | untested | integrated |
| Quantum Depth | implemented | running (128 artifacts) | preserved (hashed) | partially tested | integrated |
| Audio | designed | running | preserved | untested | integrated |
| 3D/Vertex | designed | running | preserved | untested | integrated |
| Agents | implemented | partial | preserved | partially tested | integrated |
| I-Ching | implemented | running | preserved | independently verified | integrated (core) |
| Ternary Expansion | implemented | running | preserved | independently verified | integrated |
| Presentation | designed | running | preserved | untested | connected |
| Supporting | implemented | running | preserved | untested | integrated |

**Unity at the orchestration level. Separation at the evidence and domain level.**
