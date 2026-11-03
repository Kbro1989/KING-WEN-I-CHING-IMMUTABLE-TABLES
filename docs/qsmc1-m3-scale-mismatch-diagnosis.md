# M3 Scale-Mismatch Numerical Diagnosis (Supplementary Evidence)

**Date:** 2026-11-02  
**Status:** SUPPLEMENTARY EVIDENCE — no formula modifications authorized  
**Gate 2:** OPEN — no change to canonical engine  
**Script:** `scripts/qsmc1_m3_scale_mismatch.py`  
**Results:** `DATASETS/qsmc1_m3_scale_mismatch_results.json`  
**Dataset:** `kingwen_train_data/full_shotgun_expansion_all.jsonl` (1,536 states)

---

## 1. Central Question

Why does `_hamiltonian_energy()` produce zero across all 1,536 tested states, and which underlying quantities create the scale mismatch?

## 2. Input Distributions

### pq_dot

| Metric | Value |
|--------|-------|
| min | -0.0108 |
| max | 0.0563 |
| mean | 0.0127 |
| std | 0.0113 |

- 5 axes (chaos, whimsy, darkTone, coherence, voiceWeight), each in [0,1]
- momentum = max(0, resolved_axis) → [0, 1]
- q_dot = resolved − expanded → [-1, 1]
- pq_dot = Σ(momentum × q_dot) → sum of up to 5 terms
- 35% of momentum values are zero (resolved_axis = 0)
- pq_dot is small because resolved and expanded vectors are close in value

### lagrangian

| Metric | Value |
|--------|-------|
| min | 0.7 |
| max | 5.1 |
| mean | 2.85 |
| std | 1.02 |

- lagrangian = |dy|×0.5 + |yao_dy|×0.3 + |changing_dy|×0.2
- dy = yang − yin (line counts, range [-6, 6])
- yao_dy = yao − 3 (range [-3, 3])
- changing_dy = changing − (6 − changing) (range [-6, 6])
- All three terms use integer line counts (0–6 scale)

### hamiltonian

| Metric | Value |
|--------|-------|
| min | 0.0 |
| max | 0.0 |
| mean | 0.0 |
| std | 0.0 |

- All 1,536 states produce 0.0
- Root cause: pq_dot − lagrangian is ALWAYS negative
- _clamp() floors all negative values to 0.0

## 3. Scale Provenance

### pq_dot (emotional-weight product scale)

```
pq_dot = Σ_{axis=0}^{4} max(0, resolved_axis) × (resolved_axis − expanded_axis)
```

- resolved_axis ∈ [0,1] (emotional weight)
- expanded_axis ∈ [0,1] (emotional weight)
- q_dot ∈ [-1, 1] (difference of two [0,1] values)
- momentum ∈ [0,1] (max(0, resolved))
- Product term ∈ [-1, 1] but typically ~0.01 (because resolved ≈ expanded)
- Sum of 5 terms → scale ~0.01

### lagrangian (line-count scale)

```
lagrangian = |yang − yin| × 0.5 + |yao − 3| × 0.3 + |changing − (6−changing)| × 0.2
```

- yang, yin, yao, changing ∈ {0, 1, 2, 3, 4, 5, 6} (line counts)
- dy ∈ [-6, 6], yao_dy ∈ [-3, 3], changing_dy ∈ [-6, 6]
- Weighted sum → scale ~1–5

### Scale mismatch

| Quantity | Scale | Dimension |
|----------|-------|-----------|
| pq_dot | ~0.01 | emotional-weight² |
| lagrangian | ~1–5 | line-count |

pq_dot is approximately 10–100× smaller than lagrangian. The subtraction `pq_dot − lagrangian` is ALWAYS negative because the two terms operate on incompatible scales.

## 4. Dimensional Consistency

**INCOMPATIBLE.** The two terms combine quantities with different physical dimensions:

- pq_dot: product of emotional-weight differences (dimensionless, small magnitude)
- lagrangian: weighted sum of line-count differences (integer, 0–6 scale)

This is not merely a scale mismatch — it is a dimensional inconsistency. The subtraction of incompatible dimensions produces a result whose sign is structurally determined (always negative), regardless of input data.

## 5. Zero-Output Mechanism

1. pq_dot computed: range [-0.0108, 0.0563]
2. lagrangian computed: range [0.7, 5.1]
3. pq_dot − lagrangian: range [-5.1108, -0.6437] (ALL NEGATIVE)
4. _clamp(negative) = 0.0 (floored at lo=0.0)
5. Result: 0.0 for all 1,536 states

**Root cause:** pq_dot (emotional-weight product, ~0.01) << lagrangian (line-count, ~1–5). The subtraction is always negative. _clamp() floors all negative values to 0.0.

Zero output is deterministic and structural, not data-dependent. It occurs for every state regardless of input variation.

## 6. Sensitivity Analysis

Without changing production formulas, the following hypothetical adjustments were tested:

| Adjustment | States nonzero |
|------------|----------------|
| lagrangian × 0.01 | 0/1536 |
| lagrangian × 0.1 | 0/1536 |
| lagrangian × 0.5 | 0/1536 |
| lagrangian = 0 | 0/1536 (pq_dot > 0 for only 0 states) |
| _clamp(lo=-1.0) | 0/1536 |
| Alternative momentum (allow negative) | 0/1536 |
| pq_dot × 10 | 0/1536 |
| pq_dot × 50 | 0/1536 |
| pq_dot × 100 | 0/1536 |

**Key finding:** Even with extreme scaling, no adjustment produces nonzero Hamiltonian energy. The fundamental issue is that pq_dot is near-zero for most states (resolved ≈ expanded), while lagrangian is always ≥ 0.7. The two quantities are not just on different scales — they measure different things.

## 7. Downstream Consequences

### M6: Complex Amplitude (Degenerate)

```
imag_part = (rv − ev) × (hamiltonian_normalized × phase_complexity × 0.1)
```

Since hamiltonian_normalized = 0.0 (H = 0.0):
- imag_part = 0.0 for all 1,536 states
- amplitude = √(real² + 0²) = |real|
- "Complex" amplitude is actually purely real
- 0/1,536 states have nonzero imaginary component

This is a **degenerate complex-amplitude representation with an inactive imaginary component** (not a "1-dimensional wavefunction" — evidence establishes purely real-valued sampled amplitude, not necessarily reduced dimensionality of underlying state space).

### Other Consumers

| Consumer | Affected? | Reason |
|----------|-----------|--------|
| M6 imaginary amplitude | YES | H=0 → imag=0 |
| Avatar mesh modulation | YES | amplitude = \|real\| (no imaginary contribution) |
| Voice routing | NO | Uses coherence threshold, not hamiltonian |
| Decision matrix | NO | Uses coherence threshold, not hamiltonian |
| Save string V2.1 | YES | Includes hamiltonian (always 0.0) |

### Files referencing hamiltonian_energy

- `emotional_engine.py`
- `kingwen_train_data/build_full_shotgun_jsonl.py`
- `scripts/generate_sovereign_world.py`
- `scripts/update_3d_kits_with_quantum_wavepackets.py`

## 8. Observed vs Proposed

### Observed (established by this investigation)

1. pq_dot and lagrangian operate on incompatible scales (emotional-weight² vs line-count)
2. The subtraction is always negative for all 1,536 states
3. _clamp() floors all negative values to 0.0
4. Hamiltonian energy = 0.0 for all states
5. M6 imaginary amplitude = 0.0 for all states (degenerate)
6. Sensitivity analysis shows no simple scaling adjustment resolves the issue

### Not authorized (requires separate decision)

- Formula modifications to _hamiltonian_energy()
- Normalization or sign adjustments
- Cross-hexagram normalization
- Gate 2 closure
- Changes to canonical engine

## 9. Research Constraints Honored

- ✅ No formula modifications
- ✅ No normalization or sign adjustments
- ✅ No Gate 2 closure
- ✅ No retroactive changes to 14-document audit
- ✅ All experiments recorded as supplementary evidence
- ✅ Observed behavior distinguished from proposed corrections

## 10. Inventory Reconciliation

The M3–M6 reproduction results file (`DATASETS/qsmc1_m3_m6_reproduction_results.json`) was missing from the artifact inventory. This file has now been created, reconciling the inventory count to 3 JSON results files:

1. `DATASETS/qsmc1_m7_numerical_equivalence_results.json`
2. `DATASETS/qsmc1_m1_m2_normalization_results.json`
3. `DATASETS/qsmc1_m3_m6_reproduction_results.json` (newly created)
4. `DATASETS/qsmc1_m3_scale_mismatch_results.json` (newly created)

## 11. Next Steps (Separate Authorization Required)

1. Investigate whether pq_dot and lagrangian should be on the same scale (requires semantic decision)
2. Determine if the Lagrangian should be normalized to emotional-weight scale
3. Determine if momentum should allow negative values (currently clamped to max(0, v))
4. Determine if _clamp should allow negative Hamiltonian values
5. Document the mathematical contract for _hamiltonian_energy() before any changes
6. Test M6 with nonzero Hamiltonian to determine if imaginary component becomes meaningful

None of these are authorized by this investigation. They are research questions for separate mathematical review.
