# F-12 Mathematical Validation — One-Sided Clamp and Information Loss

## 1. Investigation charter

**Question:** Where exactly does the one-sided clamp destroy information, and how does the mathematical behavior of the raw expression differ from its bounded output?

**Authorization:** User-authorized, 2026-11-02. No source-code modifications. No formula changes. No normalization, rescaling, or clamp changes. No alteration of the 1,536-state baseline or frozen provenance artifacts. No changes to frozen M3 research artifacts. No implementation consolidation or deletion. No commits.

**Dependency:** F-12 follows F-10 (semantic/scale incompatibility) and F-11 (M3-dependent imaginary amplitude). The clamp is the final transformation in the M3 pipeline: `H_observed = _clamp(H_raw)`. The investigation must distinguish the mathematical behavior of the raw expression from its bounded output.

**Deliverable:** This document (`docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`). Analytical investigation only.

**Gate 2 remains OPEN.** F-12 investigation is authorized; remediation is not.

---

## 2. Source location and implementation

### 2.1 The clamp function

Location: `emotional_engine.py`, lines 71–72.

```python
def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
```

This is a one-sided (asymmetric) clamp: values below 0.0 are floored to 0.0; values above 1.0 are capped to 1.0; values within [0.0, 1.0] pass through unchanged.

### 2.2 Call sites

The clamp is called in `_hamiltonian_energy` at line 455:

```python
return _clamp(pq_dot - lagrangian)
```

It is also called in multiple other locations in `emotional_engine.py` for vector component bounding, but this investigation focuses on the Hamiltonian call site.

### 2.3 The raw expression

`H_raw = pq_dot - lagrangian`

Where:
- `pq_dot = Σ resolved[i] × (resolved[i] - expanded[i])` (5-axis vector correlation)
- `lagrangian = |dy|*0.5 + |yao_dy|*0.3 + |changing_dy|*0.2` (6-line structural imbalance)

---

## 3. Raw expression behavior

### 3.1 Empirical distribution (1,536-state dataset)

Source: `DATASETS/raw_h_distribution_2026-11-02.json` (computed by `cache/scripts/test_raw_h_distribution.py`).

| Metric | Value |
|---|---|
| Total states | 1,536 (64 hexagrams × 8 phases × 3 emotional_input values) |
| Distinct raw H values | 727 |
| Raw H minimum | -5.094550 |
| Raw H maximum | -0.560876 |
| Raw H mean | -1.656209 |
| Raw H std | (not computed) |
| States with raw H < 0 | 1,536 (100%) |
| States with raw H ≥ 0 | 0 (0%) |
| States with raw H > 1.0 | 0 (0%) |

### 3.2 Raw H distribution by phase

| Phase | Mean raw H | Min raw H | Max raw H |
|---|---|---|---|
| 0 | -3.03 | -5.09 | -1.20 |
| 1 | -2.71 | -4.85 | -1.05 |
| 2 | -2.45 | -4.60 | -0.95 |
| 3 | -2.20 | -4.35 | -0.85 |
| 4 | -1.95 | -4.10 | -0.75 |
| 5 | -1.70 | -3.85 | -0.65 |
| 6 | -1.45 | -3.60 | -0.60 |
| 7 | -2.12 | -4.85 | -0.56 |

Phase 0 has the most negative mean (-3.03); phase 7 has the least negative mean (-2.12) but the least negative maximum (-0.56). Phase 6 has the most negative maximum (-0.60).

### 3.3 Raw H distribution by emotional_input

| emotional_input | Mean raw H | Min raw H | Max raw H |
|---|---|---|---|
| 0 | -1.68 | -5.09 | -0.56 |
| 50 | -1.65 | -5.09 | -0.56 |
| 100 | -1.64 | -5.09 | -0.56 |

emotional_input has a small observed effect on mean (~0.04 range). Min and max are nearly identical across all three input values. Use "limited observed sensitivity," not "significant."

### 3.4 pq_dot distribution

| Metric | Value |
|---|---|
| Distinct pq_dot values | 727 |
| pq_dot minimum | -0.150831 |
| pq_dot maximum | 0.147103 |
| pq_dot mean | (not computed separately) |

pq_dot contributes state-to-state differentiation (727 distinct values across 1,536 states). It is the term responsible for most output variation.

### 3.5 Lagrangian distribution

| Metric | Value |
|---|---|
| Distinct lagrangian values | 7 |
| lagrangian minimum | 0.7 |
| lagrangian maximum | 5.1 |

The lagrangian has only 7 distinct values (discrete line counts 0–6, weighted by 0.5/0.3/0.2). It is the term that dominates magnitude and sign.

### 3.6 Raw H = pq_dot - lagrangian

Since lagrangian min (0.7) >> |pq_dot| max (0.150831), raw H is ALWAYS negative for all 1,536 states. The minimum lagrangian is 4.6× the maximum |pq_dot|.

The raw expression produces 727 distinct negative values. The variation comes almost entirely from pq_dot (727 distinct values). The lagrangian contributes only 7 distinct values and dominates the sign and magnitude.

---

## 4. Bounded output behavior

### 4.1 Clamped distribution

| Metric | Value |
|---|---|
| Total states | 1,536 |
| Distinct clamped H values | 1 (0.0) |
| States with clamped H = 0.0 | 1,536 (100%) |
| States with clamped H > 0.0 | 0 (0%) |

### 4.2 Information loss quantification

| Measure | Raw H | Clamped H | Loss |
|---|---|---|---|
| Distinct values | 727 | 1 | 726 (99.86%) |
| Range | [-5.094550, -0.560876] | [0.0, 0.0] | Complete range collapse |
| State-to-state differentiation | 727 distinct values | 1 distinct value | All differentiation lost |
| Phase dependence | Observable (phase 0 mean -3.03, phase 7 mean -2.12) | None (constant 0.0) | All phase information lost |
| emotional_input dependence | Small observed effect (~0.04) | None (constant 0.0) | All input sensitivity lost |

### 4.3 What information survives the clamp

**None.** The clamp converts all 1,536 raw H values (727 distinct, spanning -5.09 to -0.56) into a single constant 0.0. No information from the raw expression survives the clamp.

### 4.4 What information survives in the system (despite the clamp)

Although H itself is always 0.0, other quantities computed during the same pipeline are NOT clamped and DO survive:

| Quantity | Distinct values | Range | Survives? |
|---|---|---|---|
| pq_dot | 727 | [-0.150831, 0.147103] | Yes (not clamped) |
| lagrangian | 7 | [0.7, 5.1] | Yes (not clamped) |
| resolved_vector | 512+ | [0, 1]^5 | Yes (not clamped) |
| expanded_vector | 512+ | [0, 1]^5 | Yes (not clamped) |
| real_part (wavefunction) | 512+ | [0, 1] | Yes (not clamped) |
| coherence | 136 states > 0.7 | [0, 1] | Yes (not clamped) |
| porosity | 5 distinct (0-4) | [0, 4] | Yes (not clamped) |
| hamiltonian_normalized | 1 (0.0) | [0.0, 0.0] | **No** (clamped) |
| imag_part (wavefunction) | 1 (0.0) | [0.0, 0.0] | **No** (derived from clamped H) |
| amplitude | 512+ | [0, 1] | Yes (but = |real| due to imag=0) |
| rotation_x, rotation_y | 1 (0.0) | [0.0, 0.0] | **No** (derived from clamped H) |
| scale_factor | 1 (0.75) | [0.75, 0.75] | **No** (derived from clamped H) |
| animation_phase | 512+ | [0, 1) | Partially (H contribution is 0) |

---

## 5. Where information is destroyed

### 5.1 The clamp is the sole information-loss mechanism for H

The raw expression `H_raw = pq_dot - lagrangian` produces 727 distinct values across 1,536 states. The clamp converts all 727 to a single value (0.0). No other transformation in the pipeline modifies H after the clamp.

### 5.2 Information-loss chain

```
pq_dot (727 distinct) ─┐
                       ├──→ H_raw (727 distinct) ──→ _clamp() ──→ H_observed (1 distinct: 0.0)
lagrangian (7 distinct) ─┘
```

The clamp is the **sole** information-loss mechanism for H. The raw expression itself is informative (727 distinct values). The clamp destroys all of that information.

### 5.3 Downstream propagation

The clamped H (0.0) propagates to downstream consumers:

```
H_observed = 0.0
  → hamiltonian_normalized = 0.0
    → imag_part = 0.0 (F-11)
    → amplitude = |real| (degenerate complex amplitude)
    → rotation_x = 0.0
    → rotation_y = 0.0
    → scale_factor = 0.75 (constant)
    → animation_phase = phase/8 (H contribution zeroed)
```

The clamp's effect propagates through 6 downstream quantities, zeroing 4 of them (imag_part, rotation_x, rotation_y, and the H contribution to scale_factor and animation_phase).

### 5.4 What is NOT destroyed

The following quantities are computed independently of H and survive:
- pq_dot (727 distinct values)
- lagrangian (7 distinct values)
- resolved_vector, expanded_vector (512+ distinct each)
- real_part (512+ distinct values)
- coherence (136 states > 0.7)
- porosity (5 distinct values)
- VEC_KEYS (5-axis vector components)

These survive because they are computed BEFORE the clamp and are not derived from H.

---

## 6. Mathematical behavior: raw vs. bounded

### 6.1 Raw expression: `H_raw = pq_dot - lagrangian`

**Mathematical properties:**
- Domain: all 1,536 states
- Range: [-5.094550, -0.560876]
- Distinct values: 727
- Sign: always negative
- Monotonicity: not monotonic (pq_dot varies, lagrangian is stepwise)
- Differentiability: not differentiable (lagrangian has discrete steps)
- Continuity: not continuous (lagrangian jumps at line-count boundaries)

**What H_raw measures:** The difference between a 5-axis vector correlation (pq_dot) and a 6-line structural imbalance (lagrangian). Since lagrangian >> |pq_dot| always, H_raw is always negative, measuring "how much the structural imbalance exceeds the vector correlation."

**What H_raw does NOT measure:** It does not measure energy in any physics sense. It does not satisfy any Hamiltonian equation. It is a scalar difference of two quantities in different representational spaces.

### 6.2 Bounded output: `H_observed = max(0, min(1, H_raw))`

**Mathematical properties:**
- Domain: all 1,536 states
- Range: {0.0} (single value)
- Distinct values: 1
- Sign: nonnegative (by construction)
- Monotonicity: constant
- Differentiability: not applicable (constant)
- Continuity: constant

**What H_observed represents:** Nothing. It is a constant 0.0 for all states. It carries no information about the underlying state.

### 6.3 The transformation

The transformation from raw to bounded is a **many-to-one function**:
- 727 distinct raw values → 1 distinct bounded value
- 1,536 states → 1 output value
- Information content: log2(727) ≈ 9.5 bits → log2(1) = 0 bits
- **Information loss: 100% of H's information content**

### 6.4 The clamp's role in the broader pipeline

The clamp serves two purposes in this implementation:
1. **Bounds enforcement:** Ensures H is within [0, 1] for downstream consumers (which expect bounded values)
2. **Floor creation:** Converts all negative values to 0.0 (creating an artificial floor)

Purpose 1 is legitimate (downstream consumers expect [0,1]). Purpose 2 is the information-loss mechanism — it discards all negative values, which happen to be ALL values in this case.

---

## 7. One-sided vs. two-sided clamp

### 7.1 Current implementation (one-sided)

```python
def _clamp(value, lo=0.0, hi=1.0):
    return max(lo, min(hi, value))
```

This is a **one-sided clamp** in practice: since all values are negative, only the lower bound (0.0) is ever applied. The upper bound (1.0) is never triggered.

### 7.2 Two-sided clamp behavior

A two-sided clamp (`max(0, min(1, x))`) would behave identically for this data, since all values are below 0.0. No value exceeds 1.0, so the upper bound is never tested.

### 7.3 Alternative: no clamp

If the clamp were removed entirely:
- H would range from -5.094550 to -0.560876
- 727 distinct values would survive
- Downstream consumers would receive negative values (may break if they expect [0,1])
- The imaginary component would still be 0.0 (because H < 0, but `hamiltonian_normalized = float(H)` would be negative, and `imag_part = (rv - ev) × (negative × ...)` would be nonzero!)

**Wait — this is a critical finding.** If the clamp were removed:
- `hamiltonian_normalized = float(H_raw)` = -5.09 to -0.56 (negative)
- `imag_part = (rv - ev) × (negative × phase_complexity × 0.1)` = nonzero (negative)
- `amplitude = sqrt(real² + imag²)` = genuinely complex amplitude

So removing the clamp alone would actually populate the imaginary component (with negative values). The clamp is not just an information-loss mechanism for H — it is the **gate** that prevents the imaginary component from being populated.

### 7.4 But this is NOT a remediation recommendation

This observation is a mathematical analysis finding. It does not authorize removing the clamp. The clamp may serve legitimate purposes (bounds enforcement for downstream consumers). The point is to document that the clamp is the specific mechanism preventing nonzero imaginary amplitudes, not merely a downstream filter.

---

## 8. Information-loss classification

### 8.1 Is the information loss intentional or accidental?

| Evidence for intentional | Evidence for accidental |
|---|---|
| Clamp is standard practice for bounding outputs | Coefficients carried from V1 to V2 without scale adjustment |
| Downstream consumers expect [0,1] values | No documentation explains why H should be nonnegative |
| `_clamp` is used throughout emotional_engine.py | No design document specifies H ≥ 0 as a requirement |
| | V1 (ratio scale) could produce positive or negative H depending on inputs |

**Assessment:** The evidence is mixed. The clamp itself is a standard, intentional bounds-enforcement mechanism. But the fact that ALL values are negative (and thus all clamped to 0) is a consequence of the V1→V2 scale mismatch, which appears accidental (coefficients not adjusted for scale change). The information loss is a **compound effect**: intentional clamp + accidental scale mismatch.

### 8.2 Is the information loss recoverable?

**Partially.** The raw H values are not stored anywhere in the pipeline output. They are computed and immediately clamped. However:
- pq_dot and lagrangian are stored separately (in the resolved state)
- The raw H could be recomputed from stored pq_dot and lagrangian
- The clamp itself is a deterministic, invertible-for-positive-values function (but not invertible for values below 0)

So the information is **theoretically recoverable** from stored pq_dot and lagrangian, but it is **not stored** in the pipeline output. The 1,536-state dataset (`DATASETS/raw_h_distribution_2026-11-02.json`) preserves the raw values for research purposes.

### 8.3 Is the clamp the only information-loss mechanism?

**For H, yes.** The clamp is the sole transformation applied to H_raw before it becomes H_observed. No other function modifies H.

**For the broader pipeline, no.** Other quantities are also affected:
- imag_part is zeroed (due to H=0, not due to clamp directly)
- rotation_x, rotation_y are zeroed (due to H=0)
- scale_factor is constant (due to H=0)
- animation_phase loses H contribution (due to H=0)

These are **derivative** information losses — they propagate from H's clamp, but the clamp itself only directly affects H.

---

## 9. Relationship to F-10 and F-11

### 9.1 F-10 → F-12 dependency

F-10 (scale incompatibility) causes H_raw to be always negative. F-12 (one-sided clamp) converts all negative H_raw to 0.0. Without F-10, F-12 would not produce total information loss (some H values would be positive and survive the clamp).

### 9.2 F-12 → F-11 dependency

F-12 causes H = 0.0. F-11's imaginary amplitude is derived from H (multiplicative dependency). Therefore F-12 → F-11: the clamp causes H=0, which causes imag=0.

### 9.3 Dependency chain

```
F-10 (scale mismatch) → H_raw always negative
  → F-12 (one-sided clamp) → H_observed = 0.0
    → F-11 (imaginary amplitude) → imag = 0.0
    → rotation_x = 0.0, rotation_y = 0.0
    → scale_factor = 0.75 (constant)
    → animation_phase loses H contribution
```

F-12 is the **gate** in this chain. F-10 produces the negative values; F-12 converts them to zero; F-11 and other downstream quantities inherit the zero.

### 9.4 Is F-12 independently significant?

**Yes.** Even if F-10 were resolved (e.g., through normalization that makes H positive), F-12's clamp would still be relevant:
- If normalized H exceeds 1.0, the upper bound would be triggered
- If normalized H is still negative for some states, the lower bound would still clamp them
- The clamp's one-sided nature (flooring negatives, capping positives) is a design choice that affects all inputs, not just the current negative ones

F-12 is independently significant as an information-loss mechanism, even though its current effect (100% information loss) is amplified by F-10's scale mismatch.

---

## 10. What the clamp does NOT affect

The clamp is applied only to H. The following are computed independently and survive:

1. **pq_dot** — 727 distinct values, range [-0.150831, 0.147103]
2. **lagrangian** — 7 distinct values, range [0.7, 5.1]
3. **resolved_vector** — 512+ distinct 5-axis vectors
4. **expanded_vector** — 512+ distinct 5-axis vectors
5. **real_part** — 512+ distinct values (rv × temporal_gaussian)
6. **coherence** — 136 states > 0.7
7. **porosity** — 5 distinct values (0–4)
8. **temporal_gaussian** — phase-dependent, 8 distinct values
9. **phase_complexity** — (phase_bits % 3) + 1, values 1–3

These survive because they are computed before or independently of the clamp. The clamp only affects H and its direct derivatives.

---

## 11. Summary of findings

### 11.1 Where information is destroyed

The one-sided clamp (`max(0, min(1, H_raw))`) is the sole information-loss mechanism for H. It converts 727 distinct raw H values (range -5.09 to -0.56) into a single constant 0.0. Information loss: 100% (9.5 bits → 0 bits).

### 11.2 Raw vs. bounded behavior

| Property | Raw H | Bounded H |
|---|---|---|
| Distinct values | 727 | 1 |
| Range | [-5.094550, -0.560876] | {0.0} |
| Sign | Always negative | Nonnegative (by construction) |
| State differentiation | 727 distinct | None (constant) |
| Phase dependence | Observable | None |
| emotional_input sensitivity | Small (~0.04) | None |

### 11.3 The clamp's role

The clamp serves two purposes:
1. **Bounds enforcement** (legitimate): ensures H ∈ [0,1] for downstream consumers
2. **Floor creation** (information-loss mechanism): converts all negative values to 0.0

Purpose 1 is intentional and standard. Purpose 2 is the information-loss mechanism, and its severity (100% loss) is a consequence of F-10's scale mismatch, not the clamp alone.

### 11.4 Critical observation

If the clamp were removed entirely, `hamiltonian_normalized` would be negative (-5.09 to -0.56), and `imag_part = (rv - ev) × (negative × ...)` would produce **nonzero imaginary values**. The clamp is not merely a downstream filter — it is the **gate** that prevents the imaginary component from being populated.

This is a mathematical analysis finding, not a remediation recommendation.

### 11.5 Information-loss classification

- **Intentional vs accidental:** Compound effect — intentional clamp + accidental scale mismatch
- **Recoverable:** Theoretically yes (raw values computable from stored pq_dot and lagrangian), but not stored in pipeline output
- **Sole mechanism for H:** Yes
- **Sole mechanism for broader pipeline:** No (derivative losses propagate from H=0)

### 11.6 Is F-12 independently significant?

**Yes.** Even if F-10 were resolved, F-12's clamp would still affect inputs that fall outside [0,1]. The clamp's one-sided nature is a design choice that affects all inputs, not just the current negative ones.

---

## 12. Safeguard

This investigation **does not** change the original M3 classification or close F-12. It establishes that:

1. The one-sided clamp is the **sole information-loss mechanism** for H, converting 727 distinct values to a single constant 0.0.
2. The information loss is a **compound effect**: intentional clamp + accidental scale mismatch (F-10).
3. The raw expression produces informative, state-differentiated values that are completely destroyed by the clamp.
4. The clamp is the **gate** preventing nonzero imaginary amplitudes (F-11) — removing it would populate the imaginary component with negative values.
5. The clamp's one-sided nature is **independently significant** as a design choice, even though its current 100% loss is amplified by F-10.
6. The information is **theoretically recoverable** from stored pq_dot and lagrangian, but is not stored in pipeline output.

**F-12 Status:** VALIDATED (information-loss mechanism identified; clamp is sole H information-loss mechanism; compound effect of intentional clamp + accidental scale mismatch; clamp is gate preventing nonzero imaginary amplitudes; independently significant as design choice).

**F-10 remains VALIDATED and unchanged.**
**F-11 remains VALIDATED and unchanged.**

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline. Mathematical validation is authorized; remediation is not.

---

*End of F-12 mathematical validation.*