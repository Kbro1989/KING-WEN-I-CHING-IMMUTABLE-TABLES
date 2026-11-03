**Cross-reference to current run (2026-11-02):** F-05 (4 of 7 consumers still reference nonexistent `shotgun_expand_output.json`), F-06 (`build_full_shotgun_jsonl.py` import path broken), and F-07 (no `scripts/__init__.py`) are now VALIDATED as separate findings. The `or 0.35` fix was verified (13/13 PASS) but F-01 (`or 0.0875` remaining) and F-02 (None handling) are new findings not identified in this report. See `docs/remediation-verification-matrix.md` Entries 1–2 and `docs/cross-reference-audit-2026-11-02.md`.

# Consumer-Boundary Audit: Hamiltonian Dependency and Impact Map

**Date:** 2026-11-02  
**Status:** SUPPLEMENTARY EVIDENCE — no formula modifications  
**Gate 2:** OPEN  
**Script:** `scripts/qsmc1_consumer_boundary_avatar.py`  
**Results:** `DATASETS/qsmc1_consumer_boundary_avatar_results.json`

---

## Correction to External Audit Claim

The external consumer-boundary audit claimed that `_quantum_avatar_modulation()` calls `_hamiltonian_energy(resolved_vector, expanded_vector, {})` with an empty `line_balance` dictionary, and that this "bypasses the Lagrangian" because "the Lagrangian's line-count inputs all default to zero."

**This claim is INCORRECT.** Runtime verification confirms:

With empty `line_balance` (all counts default to 0):
- `yin_count = 0`, `yang_count = 0`, `yao_count = 0`, `changing_count = 0`
- `dy = 0 - 0 = 0`
- `yao_dy = 0 - 3.0 = -3.0` → `abs(-3.0) * 0.3 = 0.9`
- `changing_dy = 0 - (6 - 0) = -6.0` → `abs(-6.0) * 0.2 = 1.2`
- **lagrangian = 0 + 0.9 + 1.2 = 2.1 (NOT 0)**

The empty dictionary does NOT bypass the Lagrangian. It produces a **constant lagrangian of 2.1** from default values. This is worse than the populated path (which varies 0.7–5.1) because it's a fixed constant, but it still makes `H = clamp(pq_dot - 2.1) = 0.0` for all states.

**Result:** Both execution paths produce H=0.0 for all 1,536 states. The M3→M6 degeneracy is UNIFORM across both paths. The external audit's "most important qualification" (avatar path bypasses Lagrangian) is refuted by runtime evidence.

## Verified Consumer-Boundary Findings

### 1. `emotional_engine.py` — Internal consumer, SAME zero result

**Source:** `emotional_engine.py:499`

```python
hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
```

**Runtime verification:**
- Populated path: H=0.0 for 1536/1536 states
- Empty path: H=0.0 for 1536/1536 states
- States where populated ≠ empty: 0
- Imaginary amplitude nonzero: 0 for both paths

**Consumers of H within this function:**
| Output | Depends on H? | Value when H=0 |
|--------|---------------|----------------|
| Wavefunction imag | Direct | 0.0 |
| Rotation X | Direct | 0.0 |
| Rotation Y | Direct | 0.0 |
| Scale factor | Direct | 0.5 (scale_base + (0-0.5)*0.5) |
| Animation phase | Independent (phase_bits/8) | varies |
| Color shift | Independent (resolved_vector) | varies |

**Finding:** The avatar path does NOT bypass the Lagrangian. Both paths produce identical H=0.0. The M3→M6 degeneracy is uniform.

### 2. `build_full_shotgun_jsonl.py` — Intended direct consumer, import blocker

**Source:** `kingwen_train_data/build_full_shotgun_jsonl.py:53`

```python
from emotional_engine import _hamiltonian_energy  # noqa: E402
```

**Import verification:** `from emotional_engine import _hamiltonian_energy` SUCCEEDS when run from repo root with `sys.path` including `.`.

**However:** The module also imports `from scripts.full_hexagram_shotgun import ...` (line 34), and `scripts/` has no `__init__.py`, making it not a Python package. This causes `ImportError: No module named 'scripts.full_hexagram_shotgun'` when the module is imported as a package.

**Runtime status:** BLOCKED — cannot execute as written. The intended JSONL production path is not verified.

**Finding:** The external audit's claim about "import from wrong module" is partially correct — the import of `_hamiltonian_energy` itself works, but the overall module import fails due to missing `scripts/__init__.py`.

### 3. `generate_sovereign_world.py` — Separate Hamiltonian-like scalar

**Source:** `scripts/generate_sovereign_world.py:157-210`

Reads `"energy": rec.get("hamiltonian_energy", 0.75)` from `jkd_megatron_wavepacket_emotions.jsonl`.

**Producer:** `scripts/ingest_jkd_megatron_wavepackets.py:150-180`

```python
H_JKD = coherence - chaos - 0.5 * darkTone + 0.3 * voiceWeight - 0.2 * whimsy
```

**This is NOT a call to `_hamiltonian_energy()`.** It does not use:
- M3 line-count Lagrangian
- pq_dot calculation
- _clamp() mechanism

The same JSON field name (`hamiltonian_energy`) represents a **different scalar calculation**.

**JavaScript fallback (line ~1033):**
```javascript
const hamiltonian = passage.energy || 0.75;
```

`||` is falsy for 0. If `energy: 0`, the viewer substitutes `0.75`. This masks genuine zero values.

**Downstream effects of this value:**
- Pellet oscillator frequency
- Pellet gain
- Master ground-voice gain
- Visual superposition-core pulse

**Finding:** The JKD energy is a separate calculation. The world viewer's `|| 0.75` fallback conceals explicit zero values from the JKD pipeline.

### 4. `update_3d_kits_with_quantum_wavepackets.py` — Independent bypass

**Source:** `scripts/update_3d_kits_with_quantum_wavepackets.py:40-126`

Does NOT import, calculate, read, or normalize `hamiltonian_energy`.

Independently derives:
```
vortex_tension = (upper_idx * lower_idx) / 49
```

Also derives porosity, frequencies, orbital speeds, and pellet energies from trigram indices and spatial calculations.

**Classification:** Independent construction, not an M3 consumer. Does not inherit M3 Hamiltonian result.

### 5. `shotgun_rollout_runtime.py` — Direct M3 consumer

**Source:** `scripts/shotgun_rollout_runtime.py:170-185`

Calls `_hamiltonian_energy()` with populated `line_balance` from `phase_rec`. Directly inherits M3 zero result. Propagates `hamiltonian_energy` into rollout context and trajectory tracking.

**Finding:** Direct consumer of M3 formula. Inherits H=0.0 for all states. Trajectory tracking records all-zero Hamiltonian.

### 6. `rl_shotgun_measurables.py` — Indirect M3 consumer

**Source:** `scripts/rl_shotgun_measurables.py:93-141`

Reads `hamiltonian_energy` from `phase_rec` (which was computed by `_hamiltonian_energy()`). Uses it as `h_signal = float(hamiltonian) * hamiltonian_weight` (default weight 0.1).

**Finding:** Indirect consumer. Since phase_rec's hamiltonian_energy is 0.0 (from M3), h_signal = 0.0 for all states. The RL reward signal has no Hamiltonian contribution.

### 7. `generate_avatar_meshes.py` — Direct M3 consumer

**Source:** `scripts/generate_avatar_meshes.py:66`

Imports `_hamiltonian_energy` from `emotional_engine`. Direct consumer of M3 formula.

**Finding:** Direct consumer of M3 formula. Inherits H=0.0 for all states.

## Consolidated Impact Matrix

| File | Relationship to M3 | Numerical H usage | Finding |
|------|-------------------|-------------------|---------|
| `emotional_engine.py` | Internal consumer | Direct | Empty lb produces constant lagrangian 2.1, NOT bypass. H=0.0 both paths. |
| `build_full_shotgun_jsonl.py` | Intended direct consumer | Direct | Import blocked by missing `scripts/__init__.py` |
| `generate_sovereign_world.py` | Indirect, separate scalar | Direct use of JKD energy | Different formula; `|| 0.75` fallback masks zero |
| `update_3d_kits_with_quantum_wavepackets.py` | Independent path | None | Bypasses M3 entirely |
| `shotgun_rollout_runtime.py` | Direct consumer | Direct | Inherits H=0.0; propagates to trajectory tracking |
| `rl_shotgun_measurables.py` | Indirect consumer | Reads H from phase_rec | h_signal=0.0; no Hamiltonian contribution to RL reward |
| `generate_avatar_meshes.py` | Direct consumer | Direct | Inherits H=0.0 |

## Cross-Boundary Findings (Corrected)

### A. M3 → M6 dependency IS uniform

The external audit claimed the avatar path bypasses the Lagrangian, making the degeneracy path-dependent. **This is refuted.** Both paths produce H=0.0 for all 1,536 states because empty `line_balance` produces a constant lagrangian of 2.1 (not 0), which still exceeds pq_dot.

The original M3 finding stands: H=0.0 for all states, imag=0 for all states.

### B. `hamiltonian_energy` is not a unique computational identity

Two distinct calculations share this field name:
1. `_hamiltonian_energy()` in `emotional_engine.py` (M3 formula)
2. Independent JKD ingestion scalar (coherence - chaos - 0.5*darkTone + 0.3*voiceWeight - 0.2*whimsy)

They are NOT interchangeable. The JSON field name collision creates a false impression of shared computation.

### C. World viewer conceals explicit zero values

JavaScript `|| 0.75` fallback transforms `energy: 0` into `0.75`. This can obscure upstream numerical behavior during world inspection.

### D. Seven-file inventory (expanded from original four)

Code search surfaced three additional consumers: `shotgun_rollout_runtime.py`, `rl_shotgun_measurables.py`, `generate_avatar_meshes.py`. All three inherit or propagate the M3 zero result.

### E. The `|| 0.75` fallback is a presentation-layer defect

Unlike the M3 formula issue (which is a mathematical design question), the JavaScript `|| 0.75` fallback is a clear presentation-layer bug: it replaces a genuine zero with a nonzero value, making it impossible to distinguish "no energy computed" from "energy is zero" during world inspection.

## Normalization and Artifact Inheritance

| Boundary | Re-normalization | Inheritance |
|----------|-----------------|-------------|
| Avatar modulation | No; float conversion and scaling | Wavefunction and avatar-state outputs (all H=0) |
| Shotgun JSONL builder | Six-decimal rounding (intended) | Training JSONL records (if import resolved) |
| JKD/world pipeline | No; default substitution (0→0.75) | Passage metadata and browser audio/visual behavior |
| 3D kit generator | Not applicable (independent) | Independent kit JSON metadata |
| Rollout runtime | None (direct propagation) | Trajectory tracking (all H=0) |
| RL measurables | None (reads stored H) | Reward signal (h_signal=0.0) |
| Avatar meshes | None (direct computation) | Mesh metadata (all H=0) |

## Recommended Next Authorized Work

1. **Builder import verification:** Resolve `scripts/__init__.py` absence or adjust import path. Do not repair as part of diagnostic.
2. **World-viewer zero propagation:** Feed controlled passage with `energy: 0` through Python ingestion and JavaScript fallback. Verify viewer receives 0.75.
3. **Mathematical contract:** Document the intended mathematical relationship between pq_dot and lagrangian before any formula changes.
4. **Additional consumer scan:** Verify no other files reference `hamiltonian_energy` or `_hamiltonian_energy` beyond the seven identified.

## Research Constraints Honored

- ✅ No formula modifications
- ✅ No normalization or sign adjustments
- ✅ No Gate 2 closure
- ✅ No retroactive changes to 14-document audit
- ✅ All experiments recorded as supplementary evidence
- ✅ Observed behavior distinguished from proposed corrections
- ✅ External audit claims verified against runtime evidence before acceptance
- ✅ Additional consumers discovered and audited beyond original four-file inventory
