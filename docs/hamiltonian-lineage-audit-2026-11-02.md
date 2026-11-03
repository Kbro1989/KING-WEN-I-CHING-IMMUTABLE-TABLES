# L3 — Hamiltonian Field-Level Lineage Audit

## Scope

Read-only investigation. No source changes, no commits, no remediation acceptance.
Investigates the complete lifecycle of the Hamiltonian energy from definition through production, serialization, import, transformation, consumption, and export.

## 1. Producer

### 1.1 Definition

- **File**: `emotional_engine.py:408-455`
- **Symbol**: `_hamiltonian_energy(resolved_vector, expanded_vector, line_balance) -> float`
- **Docstring**: `ℋ(p,q,t) = Σ p_i · q̇^i - ℒ`

### 1.2 Formula

```python
momentum = [max(0.0, float(v)) for v in resolved_vector]          # p_i
q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved, expanded)]  # q̇^i
pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))              # Σ p_i · q̇^i

# Paired ternary differentials
dy = yang_count - yin_count                      # signed binary differential
yao_dy = yao_count - 3.0                        # yao vs neutral midpoint (6/2)
changing_dy = changing_count - (6.0 - changing_count)  # changing vs stable
old_dy = old_yang_count - old_yin_count         # old_yang vs old_yin
stable_dy = stable_yao_count - stable_yin_count # stable ternary opposition

lagrangian = (
    abs(dy) * 0.5
    + abs(yao_dy) * 0.3
    + abs(changing_dy) * 0.2
)

return _clamp(pq_dot - lagrangian)  # max(0.0, min(1.0, value))
```

### 1.3 Production path

```
_pool_weights_for_hex(hex_id, intent, phase_bits, emotional_input)
  ├── expanded_vec = blend of 4 sources (line balance, trigram, neighbor, intent)
  ├── resolved_vec = _clamp(expanded_vec + phase_shift)
  ├── line_balance = {yin_count, yang_count, yao_count, changing_count, old_yang_count, old_yin_count, stable_yao_count, stable_yin_count, old_yao_count}
  └── Returns: (expanded_vec, porosity_norm, inject)

expand_hexagram(hex_id, request_text, phase_bits, emotional_input)
  ├── expanded_vec, porosity_norm, inject = _pool_weights_for_hex(...)
  ├── hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
  │     └── line_balance = {} (EMPTY — F-08 consumer integration defect)
  ├── hamiltonian_normalized = float(hamiltonian)  # 0..1
  └── Returns dict with:
        "hamiltonian_energy": hamiltonian
        "hamiltonian_normalized": hamiltonian_normalized
        "wavefunction": {
            "real": round(expanded_vec[i], 6),
            "imag": round((resolved_i - expanded_i) * (hamiltonian_normalized * phase_complexity * 0.1), 6),
            "amplitude": round(sqrt(real^2 + imag^2), 6),
        }
        "rotation_x": hamiltonian_normalized * 0.35 * sin(phase_bits * pi/4)
        "rotation_y": hamiltonian_normalized * 0.35 * cos(phase_bits * pi/4)
        "scale_factor": scale_base + (hamiltonian_normalized - 0.5) * 0.5
        "animation_phase": (phase_bits/8.0 + hamiltonian_normalized * 0.125) % 1.0
```

### 1.4 Key production characteristics

| Characteristic | Value |
|---|---|
| Population size | 1,536 states (64 hexagrams × 8 phases × 3 emotional_input values) |
| Distinct raw H values | 727 (out of 1,536) |
| Distinct observed H values | 1 (0.0, due to clamp) |
| Raw H range | -5.094550 to -0.560876 |
| Raw H mean | -1.656209 |
| pq_dot range | -0.150831 to 0.147103 |
| Lagrangian distinct values | 7 (0.700000 to 5.100000) |
| Information loss | 100% (727 distinct → 1 observed) |
| H = 0.0 for all states | Yes (F-12 VALIDATED: clamp is sole mechanism) |

### 1.5 Empty line_balance defect (F-08)

- **Location**: `emotional_engine.py:499`: `hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})`
- **Impact**: `line_balance` is `{}` (empty), so all ternary differential counts (yin, yang, yao, changing, old_yang, old_yin, stable_yao, stable_yin, old_yao) default to 0
- **Result**: `dy = 0 - 0 = 0`, `yao_dy = 0 - 3.0 = -3.0`, `changing_dy = 0 - 6 = -6`, `old_dy = 0 - 0 = 0`, `stable_dy = 0 - 0 = 0`
- **Lagrangian**: `abs(0)*0.5 + abs(-3)*0.3 + abs(-6)*0.2 = 0 + 0.9 + 1.2 = 2.1`
- **pq_dot**: ~0.01 (momentum × q̇, both small)
- **H_raw**: ~0.01 - 2.1 = ~-2.09 (always negative)
- **H_clamped**: 0.0 (always)

**This is a consumer integration defect**: `expand_hexagram()` calls `_hamiltonian_energy()` with `line_balance={}` instead of the actual line balance from `_pool_weights_for_hex()`. The actual line balance is computed but not passed.

## 2. Transformation

### 2.1 Scale incompatibility (F-10 VALIDATED)

- **pq_dot**: ~0.01 scale (5-axis continuous emotional vector, values 0-1)
- **lagrangian**: ~1-5 scale (6-line discrete state counts, 0-6)
- **Ratio**: lagrangian min (0.7) >> |pq_dot| max (0.15) → 4.7× minimum
- **Coefficients**: 0.5, 0.3, 0.2 (sum to 1.0, dimensionless, undocumented)
- **Root cause**: Coefficients designed for ratio-scale (V1) but applied to raw counts (V2) without normalization
- **Semantic compatibility**: NOT established (dimensional compatibility established, semantic compatibility not established)

### 2.2 One-sided clamp (F-12 VALIDATED)

- **Formula**: `H = max(0.0, min(1.0, pq_dot - lagrangian))`
- **Effect**: All 727 distinct raw H values collapse to single 0.0
- **Information loss**: 100% (727 distinct → 1 observed)
- **Independently significant**: Even if F-10 resolved, clamp would still affect inputs outside [0,1]

### 2.3 M6 imaginary amplitude (F-11 VALIDATED)

- **Formula**: `imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)`
- **Dependency**: Type 2 (derived from M3 Hamiltonian) — inherits zero
- **Result**: `imag = 0.0` for all states (because hamiltonian_normalized = 0.0)
- **Downstream impact**: Wavefunction is purely real; no temporal dynamics; no interference
- **Rotation**: `rotation_x = 0.0`, `rotation_y = 0.0` (because hamiltonian_normalized = 0.0)
- **Scale factor**: `scale_factor = scale_base + (0.0 - 0.5) * 0.5 = scale_base - 0.25` (constant offset)
- **Animation phase**: `animation_phase = (phase/8.0 + 0.0) % 1.0 = phase/8.0` (no Hamiltonian contribution)

### 2.4 V1 vs V2 formula evolution

| Version | Commit | Formula | Coefficients |
|---|---|---|---|
| V1 | 780d9c4bfe | Ratios + phase_shift | 0.5, 0.3, 0.2 (ratio-scale) |
| V2 (current) | 6239ba9bd7 | Raw counts + resolved/expanded | Same 0.5, 0.3, 0.2 (unchanged, now applied to raw counts) |

**Root cause**: Coefficients were designed for V1's ratio-scale inputs but were not adjusted when V2 changed to raw-count inputs.

### 2.5 October 27 document formula (never implemented)

- **File**: `docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md`
- **Formula**: Four differentials (dy, yao_dy, changing_dy, old_dy), /6.0 scaling, equal weights
- **Status**: Classified as design intent — never implemented in code

## 3. Serialization

### 3.1 In-memory (live producer)

- `shotgun_expand()` stores `hamiltonian_energy` and `hamiltonian_normalized` in each expanded/resolved entry
- `wavefunction` dict contains `real`, `imag`, `amplitude` per resolved state
- `rotation_x`, `rotation_y`, `scale_factor`, `animation_phase` stored in resolved entries

### 3.2 JSONL serialization

- `build_full_shotgun_jsonl.py` writes `full_shotgun_expansion_all.jsonl` (32MB, 1536 records)
- Hamiltonian fields preserved in JSONL
- Import path broken (F-06)

### 3.3 JSON export (broken consumers)

- 5 consumers reference `shotgun_expand_output.json` which never existed (F-05 + F-05b)
- No canonical JSON file export of Hamiltonian data exists on disk

## 4. Consumers

### 4.1 Direct consumers

| Consumer | Hamiltonian field used | Transformation applied |
|---|---|---|
| `emotional_engine.py` (line 499-500) | `_hamiltonian_energy()` called with empty line_balance | H = 0.0 (F-08 defect) |
| `emotional_engine.py` (line 520) | `hamiltonian_normalized * phase_complexity * 0.1` | M6 imaginary amplitude (0.0 due to H=0) |
| `emotional_engine.py` (line 532-533) | `hamiltonian_normalized * 0.35 * sin/cos(...)` | Rotation (0.0 due to H=0) |
| `emotional_engine.py` (line 538) | `scale_base + (hamiltonian_normalized - 0.5) * 0.5` | Scale factor (constant offset) |
| `emotional_engine.py` (line 553) | `hamiltonian_normalized * 0.125` | Animation phase (no contribution) |
| `decision_matrix.py` (line 316) | `consensus_hamiltonian` | Consensus computation |
| `decision_matrix.py` (line 409-410) | `inject.get("porosity", 0)` | Porosity (not Hamiltonian, but same inject_site) |
| `multi_layer_expand.py` (line 231) | `item.get("inject_site", {}).get("porosity", 0.35)` | Porosity (not Hamiltonian) |
| `scripts/generate_godot_729*.py` (4 versions) | resolved_vector (includes hamiltonian) | Godot 3D generation |
| `scripts/generate_sovereign_world.py` (line 445) | resolved_vector | Sovereign world generation |
| `scripts/kingwen_state_transition.py` | resolved_vector | State transition |
| `scripts/kingwen_mobius_sphere.py` | resolved_vector | Möbius sphere coordinates |
| `scripts/math_to_kingwen_adapter.py` (line 105) | expanded_vector | Math-to-King Wen adapter |

### 4.2 Broken consumers (reference nonexistent JSON) — F-05 + F-05b

| Consumer | Hamiltonian relevance |
|---|---|
| `scripts/build_512_widget.py` | Cannot verify (file not found) |
| `scripts/build_per_hex_training_data.py` | Cannot verify (file not found) |
| `scripts/hexagram_shotgun_matcher.py` | Cannot verify (file not found) |
| `scripts/kingwen_quantum_expand.py` | Cannot verify (file not found) |
| `scripts/build_unified_bin.py` | Cannot verify (file not found) |

## 5. Information Loss Points

### 5.1 Production-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| Empty line_balance | `emotional_engine.py:499` | `_hamiltonian_energy()` called with `{}` instead of actual line balance | High (F-08) |
| Scale mismatch | `_hamiltonian_energy()` | pq_dot ~0.01 vs lagrangian ~1-5 (4.7× minimum ratio) | High (F-10) |
| One-sided clamp | `_hamiltonian_energy()` line 455 | `max(0.0, ...)` destroys all 727 distinct raw H values | High (F-12) |
| Hardcoded coefficients | `_hamiltonian_energy()` line 450-454 | 0.5/0.3/0.2 undocumented, designed for ratio-scale (V1) but applied to raw counts (V2) | High (F-10) |
| Phase shift hardcoded | `expand_hexagram()` lines 830-839 | 8 phase shifts are hardcoded 5-tuples, not derived from hexagram state | Medium |

### 5.2 Propagation-level loss (F-11)

| Point | Location | Description | Severity |
|---|---|---|---|
| M6 imaginary amplitude | `emotional_engine.py:522` | `imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)` — inherits H=0 | High |
| Rotation | `emotional_engine.py:532-533` | `rotation_x/y = hamiltonian_normalized * 0.35 * sin/cos(...)` — 0.0 due to H=0 | High |
| Scale factor | `emotional_engine.py:538` | `scale_base + (hamiltonian_normalized - 0.5) * 0.5` — constant offset | Medium |
| Animation phase | `emotional_engine.py:553` | `hamiltonian_normalized * 0.125` — no contribution | Low |
| Wavefunction amplitude | `emotional_engine.py:527` | `sqrt(real^2 + imag^2)` — imag=0, so amplitude = |real| | Medium |

### 5.3 Serialization-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| No canonical JSON export | `shotgun_expand()` | Returns in-memory dict only | High |
| JSONL serialization | `build_full_shotgun_jsonl.py` | Hamiltonian fields preserved but import path broken (F-06) | High |

### 5.4 Consumer-level loss

| Point | Location | Description | Severity |
|---|---|---|---|
| F-08: empty line_balance | `emotional_engine.py:499` | Line balance not passed to Hamiltonian computation | High |
| F-01: `or 0.0875` | `multi_layer_expand.py:235` | Masks explicit 0.0 in porosity_norm | High |
| F-02: `float(None)` | 3 locations | Crashes when None reaches numeric conversion | High |
| F-05/F-05b: 5 broken consumers | Various | Cannot verify Hamiltonian consumption | Medium |

## 6. Dependency Chain

```
F-10 (scale/semantic incompatibility)
  ├── pq_dot ~0.01 (continuous) vs lagrangian ~1-5 (discrete)
  ├── Coefficients 0.5/0.3/0.2 designed for ratio-scale (V1) but applied to raw counts (V2)
  └── Root cause: scale mismatch → H always negative
       │
       ▼
F-12 (one-sided clamp)
  ├── H_raw ~-2.09 (always negative)
  ├── max(0.0, H_raw) → 0.0 (always)
  └── 727 distinct raw H → 1 observed (0.0)
       │
       ▼
F-11 (M6 imaginary amplitude inherits zero)
  ├── hamiltonian_normalized = 0.0
  ├── imag_part = (rv - ev) × (0.0 × phase_complexity × 0.1) = 0.0
  ├── rotation_x = 0.0, rotation_y = 0.0
  └── Wavefunction purely real, no temporal dynamics, no interference
```

## 7. Summary

### Hamiltonian integrity: NOT PRESERVED (100% information loss)

- **Production**: Formula produces 727 distinct raw H values but one-sided clamp destroys all of them (F-12). Scale mismatch is root cause (F-10). Empty line_balance is consumer integration defect (F-08).
- **Transformation**: H=0.0 propagates to M6 imaginary amplitude (F-11), rotation, scale, and animation phase. Wavefunction is purely real.
- **Serialization**: No canonical JSON export. JSONL exists but import path broken.
- **Consumption**: 13+ consumers read Hamiltonian fields. 5 consumers broken (reference nonexistent JSON).
- **Dependency chain**: F-10 → F-12 → F-11 (VALIDATED). F-08 is separate consumer integration defect.

### Open findings affecting Hamiltonian
- F-01: `or 0.0875` masks 0.0 in porosity_norm
- F-02: `float(None)` crashes in 3 locations
- F-05/F-05b: 5 consumers reference nonexistent JSON
- F-06: Broken import path
- F-07: Missing `__init__.py`
- F-08: Empty line_balance not passed to Hamiltonian computation
- F-09: q̇ degeneracy fixed (resolved_vec vs expanded_vec) but dimensional mismatch persists
- F-10: Scale/semantic incompatibility (VALIDATED)
- F-11: M6 imaginary amplitude inherits M3 zero (VALIDATED)
- F-12: One-sided clamp destroys 727 distinct H values (VALIDATED)

### Three-layer distinction
1. **Numerical compatibility**: Established (F-10) — pq_dot and lagrangian are both dimensionless
2. **Semantic compatibility**: NOT established — terms represent different physical quantities
3. **Theoretical justification**: NOT established — no derivation supports the 0.5/0.3/0.2 coefficients

### Recommended next steps
1. Field-level lineage audit complete for all three fields (L1 emotional vectors, L2 porosity, L3 Hamiltonian).
2. Cross-field comparison recommended: emotional vectors → porosity → Hamiltonian → M6 → downstream consumers.
3. No remediation authorized. Gate 2 remains OPEN.