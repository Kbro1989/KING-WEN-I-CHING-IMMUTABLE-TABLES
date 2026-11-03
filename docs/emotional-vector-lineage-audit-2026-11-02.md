# L1 — Emotional Vector Field-Level Lineage Audit

## Scope

Read-only investigation. No source changes, no commits, no remediation acceptance.
Investigates the complete lifecycle of the 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) from definition through production, serialization, import, transformation, consumption, and export.

## 1. Producer

### 1.1 Definition

- **File**: `emotional_engine.py:34`
- **Symbol**: `VEC_KEYS: List[str] = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]`
- **Pool**: `EMOTIONAL_POOL = VOICEBOX_VOICE_POOL` (imported from voicebox integration)

### 1.2 Production path

```
_pool_weights_for_hex(hex_id, intent, phase_bits, emotional_input)
  ├── _line_state_balance(binary, phase_bits) → balance dict
  ├── _line_state_vector(balance) → 5-axis vector (PRIMARY)
  ├── _trigram_vector(upper/lower) → 5-axis vector (SECONDARY, 60/40 blend)
  ├── _lerp(line_vec, trigram_vec, 0.3) → expanded
  ├── _hex_neighbors → prev/next vectors (TERTIARY, porosity-modulated bleed)
  ├── intent_vector blend (15% weight)
  ├── intent_mod blend (25% weight)
  ├── _clamp(expanded) → expanded_vec (each axis clamped to [0,1])
  └── Returns: (expanded_vec, porosity_norm, inject)
        │
        ▼
expand_hexagram(hex_id, request_text, phase_bits, emotional_input)
  ├── expanded_vec, porosity_norm, inject = _pool_weights_for_hex(...)
  ├── shift = PHASE_INFO[phase_bits]["temporal"] → hardcoded 5-tuple
  ├── sampled = [_clamp(expanded_vec[i] + shift[i]) for i in range(5)]
  └── Returns dict with:
        "expanded_vector": dict(zip(VEC_KEYS, expanded_vec))
        "resolved_vector": dict(zip(VEC_KEYS, sampled))
        "domain_vector": {k: float(resolved.get(k, 0.0)) for k in VEC_KEYS}
        "sample_paths": [
            {"label": "primary", "vector": dict(zip(VEC_KEYS, expanded_vec))},
            {"label": "phase_shifted", "vector": dict(zip(VEC_KEYS, sampled))},
            {"label": "neighbor_blend", "bleed": porosity_norm * 0.7, "vector": dict(zip(VEC_KEYS, expanded_vec))},
        ]
        "structural_vector": dict(zip(VEC_KEYS, expanded_vec))  # in pre_slider
```

### 1.3 shotgun_expand() integration

- **File**: `scripts/full_hexagram_shotgun.py:563`
- **Expanded (64 states)**: `base = expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=...)`
  - `vector = base.get("expanded_vector") or {}`
  - `inject = base.get("inject_site") or {}`
  - Stores: `expanded_vector`, `resolved_vector`, `domain_vector` (= resolved), `sample_paths`, `structural_vector` (in pre_slider)
- **Resolved (512 states)**: `r_base = expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=...)`
  - Stores: `expanded_vector`, `resolved_vector`, `domain_vector` (= resolved), `line_states`, `line_balance`, `sample_paths`, `yao_vocabulary`, `pre_slider`

### 1.4 Key production characteristics

| Characteristic | Value |
|---|---|
| Vector dimensionality | 5 axes (chaos, whimsy, darkTone, coherence, voiceWeight) |
| Value range | [0.0, 1.0] (clamped) |
| Expanded states | 64 (one per hexagram, phase=0) |
| Resolved states | 512 (64 hexagrams × 8 phases) |
| Unique expanded vectors | 64 (one per hexagram) |
| Unique resolved vectors | 512 (phase shifts create diversity) |
| domain_vector == resolved_vector | Yes (0 mismatches) |
| sample_paths labels | primary, phase_shifted, neighbor_blend |
| primary == neighbor_blend | Yes (both use expanded_vec — redundant) |

## 2. Transformation

### 2.1 Vector construction (expanded_vec)

The expanded vector is a 5-axis blend of four sources:

1. **Line-state balance** (PRIMARY, 70% weight): `_line_state_vector(balance)` converts yin/yang/yao counts to 5-axis vector using signed ternary differentials (dy, yao_dy, old_dy, stable_dy)
2. **Trigram structural context** (SECONDARY, 30% weight): `_trigram_vector(upper/lower)` blends upper (60%) and lower (40%) trigram vectors
3. **Neighbor continuity** (TERTIARY): `_lerp(prev_vec, next_vec, 0.5)` blended via porosity-modulated bleed
4. **Intent modulation**: intent_vector seed (15% × intensity) + intent_match (25%)

Final clamp to [0,1] on each axis.

**Information loss**: The individual source contributions (line balance, trigram, neighbor, intent) are blended and clamped. The original source vectors are not preserved separately — only the final blended result.

### 2.2 Phase shift (resolved_vec)

Each resolved state applies a hardcoded 5-tuple shift based on `phase_temporal`:

| Phase | Shift (chaos, whimsy, darkTone, coherence, voiceWeight) |
|---|---|
| past | (0.0, 0.0, 0.05, 0.01, -0.01) |
| present | (0.04, 0.08, 0.0, -0.01, 0.01) |
| future | (0.02, 0.09, 0.0, 0.0, 0.02) |
| transition | (0.05, 0.05, 0.02, -0.02, 0.0) |
| resolution | (-0.03, -0.02, -0.02, 0.05, 0.03) |
| dissolution | (0.06, 0.04, 0.05, -0.03, -0.02) |
| crystallization | (-0.02, -0.01, -0.01, 0.04, 0.04) |
| void | (0.0, 0.0, 0.0, 0.0, 0.0) |

**Information loss**: The shift values are hardcoded constants, not derived from the hexagram's state. The phase shift is applied as a simple addition, not a transformation that preserves the source structure.

### 2.3 Hamiltonian computation

- **File**: `emotional_engine.py:408-450` (`_hamiltonian_energy`)
- **Input**: resolved_vector, expanded_vector, line_balance
- **Formula**: `H = max(0.0, pq_dot - lagrangian)` where:
  - `pq_dot = Σ(momentum_i × q̇_i)` with `momentum_i = max(0.0, resolved_i)`, `q̇_i = resolved_i - expanded_i`
  - `lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2`
- **Result**: H = 0.0 for all 1,536 states (F-10/F-12 VALIDATED)
- **Information loss**: pq_dot ~0.01 scale vs lagrangian ~1-5 scale; one-sided clamp destroys all 727 distinct raw H values

## 3. Serialization

### 3.1 In-memory (live producer)

- `shotgun_expand()` returns dict with `expanded[]` (64) and `resolved[]` (512)
- Each entry has `expanded_vector`, `resolved_vector`, `domain_vector` (all 5-axis dicts)
- No file is written by `shotgun_expand()` itself

### 3.2 JSONL serialization

- **File**: `kingwen_train_data/build_full_shotgun_jsonl.py` (calls `shotgun_expand()`)
- **Output**: `kingwen_train_data/full_shotgun_expansion_all.jsonl` (32MB, 1536 records)
- **Format**: One JSON object per line, includes all fields from shotgun_expand output
- **Import path**: `from scripts.full_hexagram_shotgun import shotgun_expand` (broken without `scripts/__init__.py` — F-06)

### 3.3 JSON export (broken consumers)

- 5 consumers reference `shotgun_expand_output.json` which never existed (F-05 + F-05b)
- No canonical JSON file export of `shotgun_expand()` output exists on disk

### 3.4 Cloudflare Worker

- `src/core/OracleEngine.ts` comment references Python `shotgun_expand()` but worker is a consumer, not producer
- Worker does not produce emotional vectors; it consumes them

## 4. Consumers

### 4.1 Direct consumers (call shotgun_expand())

| Consumer | Vector field used | Transformation applied |
|---|---|---|
| `emotional_engine.py` (line 1012) | resolved_vector, expanded_vector | Hamiltonian computation, consensus |
| `expand_server.py` (lines 674, 751) | expanded_vector, resolved_vector | HTTP response serialization |
| `hexagram_personality.py` (line 246) | expanded_vector | Personality map construction |
| `kingwen_train_data/build_full_shotgun_jsonl.py` (lines 94, 174) | All fields | JSONL serialization |
| `kingwen_train_data/kingwen_expansion_wrapper.py` (line 103) | expanded_vector, resolved_vector | Wrapper aggregation |
| `kingwen_train_data/superposition_capture.py` (line 143) | expanded_vector, resolved_vector | Superposition capture |
| `kingwen_training.py` (line 199) | expanded_vector | Training data preparation |
| `kingwen_voice_router.py` (line 294) | resolved_vector | Voice routing |
| `scripts/enrich_kit_models.py` (line 40) | expanded_vector | Kit model enrichment |
| `scripts/generate_canonical_manifest.py` (line 25) | expanded_vector | Manifest generation |
| `scripts/generate_godot_729*.py` (4 versions) | resolved_vector | Godot 3D generation |
| `scripts/generate_reference_files.py` (lines 23, 92) | expanded_vector | Reference file generation |
| `scripts/generate_sovereign_world.py` (line 445) | resolved_vector | Sovereign world generation |
| `scripts/math_to_kingwen_adapter.py` (line 105) | expanded_vector | Math-to-King Wen adapter |
| `scripts/recover_training_data.py` (line 105) | expanded_vector | Training data recovery |
| `scripts/regenerate_training_data.py` (lines 27, 59) | expanded_vector | Training data regeneration |
| `scripts/solve_and_capture.py` (line 34) | expanded_vector | Solve and capture |
| `scripts/test_*.py` (12 scripts) | expanded_vector, resolved_vector | Testing |
| `scripts/verify_*.py` (5 scripts) | expanded_vector, resolved_vector | Verification |
| `scripts/bridge_*.py` (4 scripts) | expanded_vector, resolved_vector | Bridge operations |

### 4.2 Indirect consumers (read from serialized data)

| Consumer | Source file | Vector field used | Transformation |
|---|---|---|---|
| `decision_matrix.py` (line 119-121) | resolved states from registry | resolved_vector | Neighbor continuity, Hamiltonian alignment |
| `multi_layer_expand.py` (line 231) | resolved states | resolved_vector | Consensus computation, F-01 bug (`or 0.0875`) |
| `hexagram_personality.py` (line 246) | shotgun_expand (live) | expanded_vector | Personality map construction |

### 4.3 Broken consumers (reference nonexistent JSON) — F-05 + F-05b

| Consumer | Line | Reference | Status |
|---|---|---|---|
| `scripts/build_512_widget.py` | 6 | `DATA_PATH = BASE / 'shotgun_expand_output.json'` | NOT RUNNABLE |
| `scripts/build_per_hex_training_data.py` | 30 | `SHOTGUN = ROOT / "shotgun_expand_output.json"` | NOT RUNNABLE |
| `scripts/hexagram_shotgun_matcher.py` | 28 | `SHOTGUN = ROOT / "shotgun_expand_output.json"` | NOT RUNNABLE |
| `scripts/kingwen_quantum_expand.py` | 46 | `ORACLE_MASTER = PROJECT_ROOT / "shotgun_expand_output.json"` | NOT RUNNABLE |
| `scripts/build_unified_bin.py` | 23 | `"shotgun_expand_output.json"` | NOT RUNNABLE (F-05b) |

## 5. Information Loss Points

### 5.1 Production-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| Source blending | `_pool_weights_for_hex()` | 4 sources (line balance, trigram, neighbor, intent) blended via `_lerp` — individual contributions not preserved | Medium |
| Clamping | `_pool_weights_for_hex()` line 685 | `expanded = [_clamp(v) for v in expanded]` — raw values outside [0,1] lost | Low (values naturally in range) |
| Phase shift hardcoded | `expand_hexagram()` lines 830-839 | 8 phase shifts are hardcoded 5-tuples, not derived from hexagram state | Medium |
| Phase shift clamping | `expand_hexagram()` line 840 | `sampled = [_clamp(expanded_vec[i] + shift[i])` — shift may push values to boundary | Low |
| Hamiltonian zero | `_hamiltonian_energy()` | H = 0.0 for all 1,536 states (F-10/F-12) | High |
| Empty line_balance | `emotional_engine.py:499` | `line_balance={}` passed to `_hamiltonian_energy` — F-08 consumer integration defect | Medium |

### 5.2 Serialization-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| No canonical JSON export | `shotgun_expand()` | Returns in-memory dict only; no file written | High (5 consumers broken) |
| JSONL serialization | `build_full_shotgun_jsonl.py` | Writes 32MB JSONL but import path broken (F-06) | High |
| Redundant sample_paths | `expand_hexagram()` lines 916-928 | "primary" and "neighbor_blend" both use expanded_vec — duplicate data | Low |
| domain_vector == resolved_vector | `shotgun_expand()` line 663 | `domain_vector` is a copy of `resolved_vector` — redundant field, no information loss but creates field-name collision risk | Low |

### 5.3 Consumer-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| F-01: `or 0.0875` | `multi_layer_expand.py:235` | Masks explicit 0.0 in porosity_norm | High |
| F-02: `float(None)` | 3 locations | Crashes when None reaches numeric conversion | High |
| F-08: porosity unverified | 4 consumers | Cannot verify porosity consumption for broken consumers | Medium |
| `or 0.0` fallbacks | Various consumers | `rv.get(k, 0.0) or 0.0` masks explicit 0.0 in vector values | Medium |

### 5.4 Field-name collisions

| Field | Meaning in expanded | Meaning in resolved | Risk |
|---|---|---|---|
| `expanded_vector` | Phase-0 vector | Phase-0 vector (same, from r_base) | None — consistent |
| `resolved_vector` | Phase-0 sampled vector | Phase-p sampled vector | None — consistent |
| `domain_vector` | Copy of resolved (phase 0) | Copy of resolved (phase p) | None — consistent |
| `sample_paths` | 3 paths (primary, phase_shifted, neighbor_blend) | Not computed (None) | Medium — resolved states lack sample_paths |

## 6. Summary

### Emotional vector integrity: PARTIALLY PRESERVED

- **Production**: Vectors are correctly produced with 5-axis structure. Phase shifts create meaningful diversity (512 unique resolved vectors).
- **Serialization**: No canonical JSON export exists. JSONL serialization exists but import path is broken.
- **Consumption**: 20+ consumers read vectors directly. 5 consumers are broken (reference nonexistent JSON). Multiple consumers apply `or 0.0` fallbacks that mask explicit zeros.
- **Transformation**: Vectors are blended from 4 sources (individual contributions not preserved), clamped to [0,1], and phase-shifted with hardcoded constants.
- **Hamiltonian**: H = 0.0 for all states due to scale mismatch + one-sided clamp (F-10/F-12 VALIDATED). F-11 imaginary amplitude inherits zero.

### Open findings affecting emotional vectors
- F-01: `or 0.0875` masks 0.0 in porosity_norm (multi_layer_expand.py:235)
- F-02: `float(None)` crashes in 3 locations
- F-05/F-05b: 5 consumers reference nonexistent JSON
- F-06: Broken import path
- F-07: Missing `__init__.py`
- F-08: Porosity consumption unverified for 4 consumers
- F-10: Scale/semantic incompatibility (pq_dot ~0.01 vs lagrangian ~1-5)
- F-11: M6 imaginary amplitude inherits M3 zero
- F-12: One-sided clamp destroys 727 distinct H values

### Recommended next investigation
L2 — Porosity lineage audit. Trace calculation → propagation → interpretation, including the 3 independent porosity computations (injection site 0-4 int, kit QWP 0.15-0.71 float, emotional engine from line balance) that are not reconciled.