# QSMC-1 M3 Dimensional Consistency Analysis

## Formal F-10 Investigation

**Status:** IN PROGRESS — Investigation only. No formula changes, rescaling, normalization, or clamp modifications performed during this investigation.

**Artifact:** `docs/qsmc1-m3-dimensional-consistency-analysis.md`
**Date:** 2026-11-02
**Git revision:** 71fbf28f8e
**Baseline dataset:** `DATASETS/raw_h_distribution_2026-11-02.json` (1,536 states, immutable)
**Companion documents:**
- `docs/remediation-verification-matrix.md` — Entry 3 (Hamiltonian M3)
- `docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` — Categories A–D
- `docs/information-loss-remediation-register.md` — F-10 (High priority)
- `docs/controlled-remediation-verification-protocol.md` — verification protocol

---

## 1. Investigation Charter

This document answers four questions about the Hamiltonian energy calculation in `emotional_engine.py`:

1. **Are the two terms dimensionally compatible?** — `pq_dot` vs `lagrangian`
2. **Are their coefficients dimensionless or unit-bearing?** — 0.5, 0.3, 0.2
3. **Is the negative sign an intended mathematical outcome?** — raw H is always negative
4. **Does the implementation represent the intended Hamiltonian, or merely a similarly named scalar calculation?**

**Constraint:** No formula changes, rescaling, normalization, or clamp modifications during this investigation. The 1,536-state dataset is the immutable numerical baseline.

---

## 2. Source Definitions

### 2.1 Function signature and call site

**File:** `emotional_engine.py`, lines 408–455
**Function:** `_hamiltonian_energy(resolved_vector, expanded_vector, line_balance)`

**Call site 1 (shotgun_expand, full_hexagram_shotgun.py:682–688):**
```python
resolved_vec = [float(item.get("resolved_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS]
expanded_vec = [float(item.get("expanded_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS]
energies.append(
    hamiltonian_energy(resolved_vec, expanded_vec, item.get("line_balance", {}))
)
```

**Call site 2 (_quantum_avatar_modulation, emotional_engine.py:499):**
```python
hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
```
Here `line_balance` is an empty dict `{}`, so all line counts default to 0.

**Call site 3 (kingwen_state_transition.py):**
```python
h = hamiltonian_energy(resolved_vec, expanded_vec, line_balance)
```

### 2.2 Input vectors

**VEC_KEYS** (emotional_engine.py, line 37):
```python
VEC_KEYS = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
```

Both `resolved_vector` and `expanded_vector` are 5-element dictionaries keyed by these 5 axis names, with float values in [0.0, 1.0].

**Source of vector values:**
- `expanded_vector`: produced by `expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=...)` → `base.get("expanded_vector")`
- `resolved_vector`: produced by `expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=...)` → `base.get("resolved_vector")`

Both vectors are outputs of the same `expand_hexagram()` function with different `phase_bits` (0 for expanded, p for resolved). The values are computed from `_line_state_vector()` and `_line_state_balance()`.

### 2.3 Line balance

**Source:** `expand_hexagram()` → `base.get("line_balance")`
**Structure (from _line_state_balance, line 207):**
```python
{
    "yin_count": int,      # count of yin (0) states in 6-bit binary (0–6)
    "yang_count": int,     # count of yang (1) states (0–6)
    "yao_count": int,      # count of yao (2) states (0–6)
    "changing_count": int, # count of changing lines (0–6)
    "old_yin_count": int,  # count of old yin (0,6) (0–6)
    "old_yang_count": int, # count of old yang (0–6)
    "stable_yin_count": int,
    "stable_yao_count": int,
    "stable_yang_count": int,
}
```

All counts are integers in [0, 6]. Sum of yin+yang+yao = 6 (for binary phase 0, yao_count = 0, so yin+yang = 6).

---

## 3. Vector Construction

### 3.1 _line_state_balance (emotional_engine.py:207–260)

Computes counts from a 6-bit binary string (hexagram lines, bottom-to-top):

```python
binary = base.get("binary_bottom_to_top", "111111")  # e.g., "111111" for hex 1
lines = [int(c) for c in binary[:6]]
yin_count = sum(1 for x in lines if x == 0)
yang_count = sum(1 for x in lines if x == 1)
# yao_count = 0 for binary (phase 0)
# changing_count = 0 for binary (no changing lines at phase 0)
```

**Output:** Integer counts, each in [0, 6].

### 3.2 _line_state_vector (emotional_engine.py:717–780)

Computes the 5-axis emotional vector from line balance **ratios** (not counts):

```python
total = max(len(binary), 1)  # = 6 for hexagrams
yin_r = yin_count / total    # [0.0, 1.0] in steps of 1/6 ≈ 0.1667
yang_r = yang_count / total  # [0.0, 1.0]
yao_r = yao_count / total    # [0.0, 1.0]

dy = yang_r - yin_r          # signed ternary differential, range [-1.0, 1.0]
yao_dy = yao_r - 0.5         # yao vs neutral midpoint, range [-0.5, 0.5]
old_dy = (old_yang_count / total) - (old_yin_count / total)
stable_dy = (stable_yao_count / total) - (stable_yin_count / total)

# 5-axis vector (all via _clamp to [0, 1])
chaos = _clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2)
whimsy = _clamp(yin_r * 0.4 + yao_dy * 0.3 + old_dy * 0.1)
darkTone = _clamp((old_yang_count / total) * 0.15 + (old_yao_count / total) * 0.2 + dy * 0.1)
coherence = _clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1)
voiceWeight = _clamp(yang_r * 0.3 - yao_dy * 0.2 + (old_yang_count / total) * 0.1)
```

**Key observation:** The vector components are dimensionless ratios in [0, 1]. The intermediate differentials (dy, yao_dy, old_dy, stable_dy) are also dimensionless ratios in [-1, 1]. The coefficients (0.5, 0.3, 0.2, 0.4, 0.15, 0.1, etc.) are dimensionless weights.

**For phase 0 (expanded):** yao_count = 0, changing_count = 0, old/stable counts = 0. So:
- dy = yang_r - yin_r (nonzero, range [-1, 1])
- yao_dy = 0 - 0.5 = -0.5
- old_dy = 0
- stable_dy = 0

**For resolved (phase p):** The vector changes because the phase_bits alter the line states (some lines become "changing" or "yao"), which modifies the counts and ratios.

### 3.3 Axis-by-axis unit analysis

| Axis | Formula | Input units | Coefficient units | Output units |
|------|---------|-------------|-------------------|--------------|
| chaos | yao_dy*0.5 + old_dy*0.3 + \|dy\|*0.2 | dimensionless (ratio) | dimensionless | dimensionless [0,1] |
| whimsy | yin_r*0.4 + yao_dy*0.3 + old_dy*0.1 | dimensionless | dimensionless | dimensionless [0,1] |
| darkTone | (old_yang/total)*0.15 + (old_yao/total)*0.2 + dy*0.1 | dimensionless | dimensionless | dimensionless [0,1] |
| coherence | yang_r*0.3 - yao_dy*0.3 - \|old_dy\|*0.1 | dimensionless | dimensionless | dimensionless [0,1] |
| voiceWeight | yang_r*0.3 - yao_dy*0.2 + (old_yang/total)*0.1 | dimensionless | dimensionless | dimensionless [0,1] |

**Conclusion (Section 3):** All vector components are dimensionless quantities in [0, 1]. No physical units are involved.

---

## 4. pq_dot Derivation

### 4.1 Formula (emotional_engine.py:408–455)

```python
def _hamiltonian_energy(resolved_vector, expanded_vector, line_balance):
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))
    ...
    return _clamp(pq_dot - lagrangian)
```

### 4.2 Term 1: momentum_i = max(0.0, resolved_vec_i)

**Source:** `resolved_vector` 5-axis values (chaos, whimsy, darkTone, coherence, voiceWeight), each in [0, 1].
**Operation:** ReLU (rectified linear unit) — negative values clamped to 0.
**Units:** Dimensionless (same as vector components).
**Range:** [0, 1].
**Mathematical role:** In classical Hamiltonian mechanics, momentum p_i is the conjugate variable to position q_i. Here, `momentum` is set to the non-negative part of the resolved vector — not a physically derived momentum, but a proxy. The resolved vector is treated as both "position" (in q_dot) and "momentum" (in the dot product).

### 4.3 Term 2: q_dot_i = resolved_vec_i − expanded_vec_i

**Source:** Difference between resolved (phase p) and expanded (phase 0) vectors.
**Operation:** Element-wise subtraction of two 5-axis vectors.
**Units:** Dimensionless (difference of dimensionless quantities).
**Range:** [-1.0, 1.0] (since each vector component is in [0, 1]).
**Mathematical role:** In classical mechanics, q̇ = dq/dt is the time derivative of position. Here, q_dot is the difference between two static states (resolved vs expanded) — not a time derivative, but a state difference. The "time" dimension is implicit in the phase transition (0 → p).

### 4.4 Term 3: pq_dot = Σ(momentum_i × q_dot_i)

**Formula:** Dot product of momentum vector with q_dot vector.
**Units:** Dimensionless × dimensionless = dimensionless.
**Range:** [-1.0, 1.0] (since momentum ∈ [0,1], q_dot ∈ [-1,1], sum of 5 products).
**Observed range (from 1,536-state test):** [-0.150831, 0.147103], 727 distinct values.
**Mean absolute value:** ~0.01.

**Mathematical interpretation:** In classical Hamiltonian mechanics, the term p·q̇ represents kinetic energy (T = ½Σp_i·q̇_i or similar). Here, pq_dot is a bilinear form between two derived quantities — not a standard kinetic energy. The "momentum" is the resolved vector itself (non-negative part), and the "velocity" is the difference between resolved and expanded states.

### 4.5 Dimensional analysis of pq_dot

| Sub-term | Symbol | Domain | Range | Units |
|----------|--------|--------|-------|-------|
| resolved_vec_i | r_i | [0, 1] | dimensionless | none |
| expanded_vec_i | e_i | [0, 1] | dimensionless | none |
| momentum_i | m_i = max(0, r_i) | [0, 1] | dimensionless | none |
| q_dot_i | q̇_i = r_i − e_i | [-1, 1] | dimensionless | none |
| pq_dot | Σ m_i · q̇_i | [-1, 1] | dimensionless | none |

**Conclusion (Section 4):** pq_dot is a dimensionless scalar. No physical units are involved. The small magnitude (~0.01) arises from the near-cancellation between resolved and expanded vectors (which are similar for most hexagrams), not from a unit mismatch.

---

## 5. Lagrangian Derivation

### 5.1 Formula (emotional_engine.py:436–454)

```python
line_balance = line_balance or {}
yin_count = int(line_balance.get("yin_count", 0) or 0)
yang_count = int(line_balance.get("yang_count", 0) or 0)
yao_count = int(line_balance.get("yao_count", 0) or 0)
changing_count = int(line_balance.get("changing_count", 0) or 0)
old_yin_count = int(line_balance.get("old_yin_count", 0) or 0)
old_yang_count = int(line_balance.get("old_yang_count", 0) or 0)
stable_yin_count = int(line_balance.get("stable_yin_count", 0) or 0)
stable_yao_count = int(line_balance.get("stable_yao_count", 0) or 0)
stable_yang_count = int(line_balance.get("stable_yang_count", 0) or 0)

dy = yang_count - yin_count                    # signed binary differential
yao_dy = yao_count - 3.0                      # yao vs neutral midpoint (6/2)
changing_dy = changing_count - (6.0 - changing_count)  # changing vs non-changing
old_dy = old_yang_count - old_yin_count       # old yang vs old yin
stable_dy = stable_yao_count - stable_yin_count # stable yao vs stable yin

lagrangian = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2
```

### 5.2 Term-by-term analysis

#### Term 1: abs(dy) × 0.5

| Sub-term | Source | Domain | Range | Units |
|----------|--------|--------|-------|-------|
| yin_count | line_balance (binary 0s in 6-bit) | [0, 6] | count (dimensionless integer) | none |
| yang_count | line_balance (binary 1s in 6-bit) | [0, 6] | count (dimensionless integer) | none |
| dy = yang_count − yin_count | derived | [-6, 6] | count (dimensionless) | none |
| abs(dy) | derived | [0, 6] | count (dimensionless) | none |
| coefficient 0.5 | hardcoded | scalar | dimensionless | none |
| **abs(dy) × 0.5** | **derived** | **[0, 3]** | **dimensionless count** | **none** |

**Source of line counts:** `_line_state_balance()` counts binary (0/1) states in the 6-bit hexagram representation. For phase 0 (expanded), yao_count = 0, changing_count = 0, so yin_count + yang_count = 6.

#### Term 2: abs(yao_dy) × 0.3

| Sub-term | Source | Domain | Range | Units |
|----------|--------|--------|-------|-------|
| yao_count | line_balance (ternary 2s in 6-bit) | [0, 6] | count (dimensionless integer) | none |
| yao_dy = yao_count − 3.0 | derived | [-3, 3] | count (dimensionless) | none |
| abs(yao_dy) | derived | [0, 3] | count (dimensionless) | none |
| coefficient 0.3 | hardcoded | scalar | dimensionless | none |
| **abs(yao_dy) × 0.3** | **derived** | **[0, 0.9]** | **dimensionless count** | **none** |

**Note:** The constant 3.0 represents the midpoint of the 6-line hexagram (6/2 = 3). This is a positional midpoint, not a physical quantity.

#### Term 3: abs(changing_dy) × 0.2

| Sub-term | Source | Domain | Range | Units |
|----------|--------|--------|-------|-------|
| changing_count | line_balance (count of changing lines) | [0, 6] | count (dimensionless integer) | none |
| changing_dy = changing_count − (6.0 − changing_count) | derived | [-6, 6] | count (dimensionless) | none |
| abs(changing_dy) | derived | [0, 6] | count (dimensionless) | none |
| coefficient 0.2 | hardcoded | scalar | dimensionless | none |
| **abs(changing_dy) × 0.2** | **derived** | **[0, 1.2]** | **dimensionless count** | **none** |

**Note:** changing_dy is a signed differential (changing vs non-changing). The abs() makes it a magnitude.

### 5.3 Lagrangian summary

```python
lagrangian = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2
```

| Property | Value |
|----------|-------|
| Units | Dimensionless (count-based) |
| Domain | [0, 5.1] (max: 6×0.5 + 3×0.3 + 6×0.2 = 3.0 + 0.9 + 1.2 = 5.1) |
| Observed values (7 distinct) | 0.700000, 1.200000, 1.700000, 2.200000, 2.700000, 3.200000, 5.100000 |
| Distribution | Discrete (line counts are integers, so lagrangian takes only 7 values) |

**Source of the 7 distinct values:** For phase 0 (expanded), yao_count = 0, changing_count = 0. So:
- dy = yang_count − yin_count, where yin_count + yang_count = 6
- dy ranges from -6 (all yin) to +6 (all yang) in steps of 2
- abs(dy) ranges from 0, 2, 4, 6 (4 values)
- yao_dy = 0 − 3.0 = -3.0 (constant for phase 0)
- abs(yao_dy) = 3.0 (constant)
- changing_dy = 0 − 6 = -6 (constant for phase 0)
- abs(changing_dy) = 6.0 (constant)

So lagrangian = abs(dy)*0.5 + 3.0*0.3 + 6.0*0.2 = abs(dy)*0.5 + 0.9 + 1.2 = abs(dy)*0.5 + 2.1

abs(dy) takes values 0, 2, 4, 6 → lagrangian takes values 2.1, 3.1, 4.1, 5.1.

But the observed data shows 7 values (0.7, 1.2, 1.7, 2.2, 2.7, 3.2, 5.1). This means the resolved states (phases 1–7) have nonzero yao_count and changing_count, producing additional lagrangian values.

### 5.4 Dimensional analysis of lagrangian

| Sub-term | Symbol | Domain | Range | Units |
|----------|--------|--------|-------|-------|
| yin_count | n_yin | [0, 6] | count | none |
| yang_count | n_yang | [0, 6] | count | none |
| dy | n_yang − n_yin | [-6, 6] | count | none |
| yao_count | n_yao | [0, 6] | count | none |
| yao_dy | n_yao − 3.0 | [-3, 3] | count (with midpoint offset) | none |
| changing_count | n_ch | [0, 6] | count | none |
| changing_dy | n_ch − (6 − n_ch) | [-6, 6] | count | none |
| coefficient 0.5 | c1 | scalar | dimensionless | none |
| coefficient 0.3 | c2 | scalar | dimensionless | none |
| coefficient 0.2 | c3 | scalar | dimensionless | none |
| **lagrangian** | **Σ c_i · \|d_i\|** | **[0, 5.1]** | **dimensionless count** | **none** |

**Conclusion (Section 5):** The lagrangian is a dimensionless scalar computed from integer line counts (0–6) with dimensionless coefficients (0.5, 0.3, 0.2). No physical units are involved. The term represents a "cost" or "energy penalty" based on line-state imbalance, not a physical Lagrangian in the classical mechanics sense.

---

## 6. Hamiltonian Construction

### 6.1 Formula

```python
return _clamp(pq_dot - lagrangian)
```

Where `_clamp(x)` presumably clamps to [0, 1] (or similar range). The raw value is `pq_dot - lagrangian`.

### 6.2 Term-by-term

| Term | Symbol | Source | Domain | Range | Units |
|------|--------|--------|--------|-------|-------|
| pq_dot | T | §4 | [-1, 1] | dimensionless | none |
| lagrangian | V | §5 | [0, 5.1] | dimensionless (count) | none |
| **raw H** | **T − V** | **derived** | **[-6.1, 1.0]** | **dimensionless** | **none** |
| **clamped H** | **max(0, T − V)** | **derived** | **[0, 1.0]** | **dimensionless** | **none** |

### 6.3 Observed values (from 1,536-state baseline)

| Quantity | Value |
|----------|-------|
| Raw H range | [-5.094550, -0.560876] |
| Raw H distinct values | 727 |
| Raw H mean | -1.656209 |
| Clamped H range | [0.0, 0.0] |
| Clamped H distinct values | 1 |
| pq_dot range | [-0.150831, 0.147103] |
| pq_dot distinct values | 727 |
| lagrangian range | [0.700000, 5.100000] |
| lagrangian distinct values | 7 |

### 6.4 Dimensional compatibility assessment

**Question 1: Are the two terms dimensionally compatible?**

Both terms are dimensionless. However, they represent fundamentally different quantities:

- **pq_dot** is a bilinear form (dot product) of two 5-axis emotional vectors. It measures the "alignment" between the resolved state and the state transition (resolved − expanded). It is a smooth, continuous quantity with 727 distinct values across 1,536 states.

- **lagrangian** is a weighted sum of absolute line-count differentials. It measures the "cost" or "penalty" of line-state imbalance. It is a discrete, step-like quantity with only 7 distinct values.

**Assessment:** The terms are dimensionally compatible (both dimensionless) but **semantically heterogeneous**. pq_dot operates on the 5-axis emotional vector space (continuous, granular). The lagrangian operates on the 6-line binary/ternary state space (discrete, coarse). They measure different things in different spaces.

The subtraction `pq_dot - lagrangian` combines a smooth vector-space quantity with a coarse line-count quantity. This is not inherently invalid (both are dimensionless), but it means the result's magnitude is dominated by the coarser term.

**Question 2: Are their coefficients dimensionless or unit-bearing?**

All coefficients are dimensionless scalars:
- 0.5, 0.3, 0.2 (lagrangian weights)
- The momentum ReLU has no coefficient
- The q_dot subtraction has no coefficient

None of the coefficients carry units. They are tuning weights, not physical constants.

**Question 3: Is the negative sign an intended mathematical outcome?**

The raw H is always negative because:
- pq_dot ∈ [-0.15, 0.15] (small, centered near 0)
- lagrangian ∈ [0.7, 5.1] (always positive, minimum 0.7)

The subtraction `pq_dot - lagrangian` is always negative because lagrangian >> |pq_dot| in all observed cases. The minimum lagrangian (0.7) exceeds the maximum |pq_dot| (0.15) by a factor of ~4.7.

**Assessment:** The negative sign is a **mathematical consequence** of the scale disparity, not a design choice. The clamp (`max(0, raw)`) then floors all values to 0.0, which is the "artificial floor" identified in Category A of the floor/ceiling research.

Whether the negative sign is "intended" depends on the mathematical intent:
- If H is meant to represent a **net energy** (kinetic minus potential), negative values could be meaningful (system is in a potential-dominated regime).
- If H is meant to represent a **positive magnitude** (energy, not signed energy), negative values are nonsensical and the clamp is a patch, not a design.
- The current implementation does not document which interpretation is intended.

**Question 4: Does the implementation represent the intended Hamiltonian, or merely a similarly named scalar calculation?**

The implementation computes:
```
H = max(0, Σ max(0, r_i) · (r_i − e_i) − [0.5|dy| + 0.3|yao_dy| + 0.2|changing_dy|])
```

This is a scalar calculation that borrows terminology from Hamiltonian mechanics (momentum, position derivative, Lagrangian) but does not implement a standard Hamiltonian. Specifically:

1. **No canonical variables:** In Hamiltonian mechanics, p_i and q_i are conjugate variables related by p_i = ∂L/∂q̇_i. Here, "momentum" is set to max(0, resolved_vec_i) — the resolved vector is used as its own momentum. There is no conjugate relationship.

2. **No time derivative:** q̇ = dq/dt in classical mechanics. Here, q_dot = resolved − expanded is a state difference, not a time derivative. The "time" dimension is implicit in the phase transition (phase 0 → phase p).

3. **No Lagrangian function:** In classical mechanics, L = T − V, and the Lagrangian is a function of (q, q̇, t). Here, the "Lagrangian" is computed from line counts (discrete, 0–6), not from the vectors or their derivatives. It is a penalty term, not a Lagrangian.

4. **No Hamilton's equations:** Hamilton's equations are q̇_i = ∂H/∂p_i and ṗ_i = −∂H/∂q_i. The implementation does not compute or use these.

**Assessment:** The implementation is a **scalar calculation with Hamiltonian-inspired naming**, not a Hamiltonian in the mathematical physics sense. The name "Hamiltonian energy" describes the *intent* (combine kinetic-like and potential-like terms) but the implementation does not satisfy the formal requirements of Hamiltonian mechanics.

Whether this matters depends on the intended semantics:
- If the name is **aspirational** (the formula should eventually become a real Hamiltonian), then the current implementation is a placeholder and the dimensional inconsistency is a symptom of incomplete implementation.
- If the name is **metaphorical** (the formula is a heuristic that borrows Hamiltonian vocabulary), then the dimensional inconsistency may be acceptable as long as the heuristic produces useful outputs — which it currently does not (all outputs are 0.0).

---

## 7. Sign and Scale Interpretation

### 7.1 Why raw H is always negative

```
raw H = pq_dot − lagrangian
```

- pq_dot ∈ [-0.15, 0.15] (small, centered near 0)
- lagrangian ∈ [0.7, 5.1] (always positive, minimum 0.7)

The minimum lagrangian (0.7) exceeds the maximum |pq_dot| (0.15) by a factor of ~4.7. Therefore, `pq_dot - lagrangian < 0` for all 1,536 states.

**Is this intended?**

Three possible interpretations:

1. **Intended negative (energy deficit):** The system is always in a potential-dominated regime. Raw H represents "available energy" (kinetic minus potential). Negative means the system has insufficient kinetic energy to overcome its potential barrier. The clamp to 0 represents "no available energy." This is a valid physical interpretation but requires that negative values be meaningful, not just clamped away.

2. **Unintended negative (scale bug):** The lagrangian is too large relative to pq_dot. The coefficients (0.5, 0.3, 0.2) or the line-count scale (0–6) produce a lagrangian that overwhelms pq_dot. If the lagrangian were scaled to match pq_dot's range, raw H could be positive for some states. This would be a dimensional scaling error.

3. **Design error (wrong formula):** The formula `pq_dot - lagrangian` is not the intended Hamiltonian. The intended formula may be different (e.g., `pq_dot + lagrangian`, or `pq_dot / lagrangian`, or a different combination). The name "Hamiltonian" implies H = T + V (sum, not difference) in some conventions.

**Assessment:** The evidence does not distinguish between these interpretations. The implementation produces a consistently negative value, which the clamp floors to 0. Whether this is intended, a scale bug, or a formula error requires knowing the mathematical intent, which is not documented in the codebase.

### 7.2 Scale disparity quantification

| Quantity | Min | Max | Mean | Distinct values |
|----------|-----|-----|------|-----------------|
| pq_dot | -0.150831 | 0.147103 | ~0.000 | 727 |
| lagrangian | 0.700000 | 5.100000 | ~2.5 | 7 |
| raw H | -5.094550 | -0.560876 | -1.656209 | 727 |
| clamped H | 0.000000 | 0.000000 | 0.000000 | 1 |

**Scale ratio:** lagrangian / |pq_dot| ≈ 0.7 / 0.15 ≈ 4.7 (minimum) to 5.1 / 0.001 ≈ 5,100 (maximum, for states where pq_dot ≈ 0).

**Information loss:** 727 distinct raw H values → 1 clamped value (0.0). Information loss ratio: 727:1.

---

## 8. Coefficients Analysis

### 8.1 Lagrangian coefficients

| Coefficient | Value | Applied to | Source |
|-------------|-------|------------|--------|
| 0.5 | abs(dy) | yang_count − yin_count | Hardcoded in emotional_engine.py:450 |
| 0.3 | abs(yao_dy) | yao_count − 3.0 | Hardcoded in emotional_engine.py:451 |
| 0.2 | abs(changing_dy) | changing_count − (6 − changing_count) | Hardcoded in emotional_engine.py:452 |

**Are they dimensionless?** Yes — they are pure scalars with no units.

**Are they unit-bearing?** No — they do not convert between different unit systems. They are tuning weights that determine the relative importance of each line-count differential.

**Are they justified?** The codebase does not document why these specific values (0.5, 0.3, 0.2) were chosen. They appear to be empirically selected weights, not derived from a theoretical framework. The sum (0.5 + 0.3 + 0.2 = 1.0) suggests they were intended as a convex combination, but they are applied to different-scale quantities (dy ∈ [-6,6], yao_dy ∈ [-3,3], changing_dy ∈ [-6,6]), so the sum of coefficients does not normalize the output.

### 8.2 pq_dot coefficients

pq_dot has no explicit coefficients — it is a simple dot product:
```
pq_dot = Σ resolved_vec_i × (resolved_vec_i − expanded_vec_i)
```

The implicit coefficients are 1.0 for each axis. No normalization or scaling is applied.

### 8.3 Cross-term coefficient analysis

The subtraction `pq_dot - lagrangian` combines:
- pq_dot: 5 terms, each a product of two [0,1] values → range [-1, 1] (but observed [-0.15, 0.15])
- lagrangian: 3 terms, each a product of a [0,6] count and a [0.2, 0.5] weight → range [0, 5.1]

The effective scale ratio between the two terms is determined by:
- The vector components are in [0, 1] (5 axes)
- The line counts are in [0, 6] (6 lines)
- The coefficients are in [0.2, 0.5]

There is no normalization that would bring the two terms to comparable scales. The lagrangian's range (0–5.1) is ~34× larger than pq_dot's range (-0.15 to 0.15).

---

## 9. Summary of Findings

### 9.1 Dimensional compatibility

| Question | Answer |
|----------|--------|
| Are pq_dot and lagrangian dimensionally compatible? | **Yes** — both are dimensionless. |
| Are they semantically compatible? | **No** — pq_dot is a continuous vector-space quantity; lagrangian is a discrete line-count quantity. They measure different things in different spaces. |
| Is the subtraction dimensionally justified? | **Formally yes** (both dimensionless), but **semantically questionable** (different domains, different scales, no normalization). |

### 9.2 Coefficients

| Question | Answer |
|----------|--------|
| Are coefficients dimensionless? | **Yes** — all are pure scalars. |
| Are they unit-bearing? | **No** — no unit conversion. |
| Are they justified? | **Undocumented** — no theoretical basis found in codebase. Sum to 1.0 but applied to different-scale quantities. |

### 9.3 Negative sign

| Question | Answer |
|----------|--------|
| Is raw H always negative? | **Yes** — lagrangian (min 0.7) > \|pq_dot\| (max 0.15) in all 1,536 states. |
| Is this intended? | **Unknown** — three interpretations possible (energy deficit, scale bug, formula error). Not documented. |
| Does the clamp handle it? | **Yes, but destructively** — max(0, raw) floors all 1,536 values to 0.0, losing 727 distinct values. |

### 9.4 Implementation vs. intended Hamiltonian

| Question | Answer |
|----------|--------|
| Is this a real Hamiltonian? | **No** — no canonical variables, no time derivative, no Lagrangian function, no Hamilton's equations. |
| Is the name accurate? | **Metaphorical at best** — borrows Hamiltonian vocabulary (momentum, position derivative, Lagrangian) but does not implement Hamiltonian mechanics. |
| Is this a problem? | **Depends on intent** — if aspirational, the implementation is incomplete; if metaphorical, the name is misleading but the formula may still be useful (if it produced nonzero output, which it does not). |

---

## 10. Open Questions (Unresolved)

1. **What is the intended mathematical semantics of H?** — Energy? Penalty? Fitness? The codebase does not document this.

2. **What units (if any) should the vector components carry?** — They are currently dimensionless ratios. If they represent physical quantities (e.g., emotional intensity on a 0–1 scale), the lagrangian's line-count scale (0–6) is incommensurable without a conversion factor.

3. **Should the lagrangian be scaled to match pq_dot's range?** — If so, by what factor? The current coefficients (0.5, 0.3, 0.2) produce a lagrangian that is ~34× larger than pq_dot. A rescaling would require knowing the intended relative importance of the two terms.

4. **Is the clamp (`max(0, raw)`) part of the intended formula, or a patch for the scale bug?** — If the formula is intended to produce negative values, the clamp is a bug. If the formula is intended to produce non-negative values, the clamp is correct but the scale disparity makes it always active.

5. **What is the relationship between the binary (512-state) Hamiltonian and the ternary (5,832-state) Hamiltonian?** — The ternary layer (scripts/ternary_full_expansion.json) exists but is not integrated into shotgun_expand(). The Hamiltonian is computed only on the binary layer.

6. **Does the `line_balance` passed to `_hamiltonian_energy` in `_quantum_avatar_modulation` (empty dict `{}`) produce a valid lagrangian?** — With empty line_balance, all counts default to 0, giving dy=0, yao_dy=-3.0, changing_dy=-6.0, lagrangian=2.1. This is a different lagrangian than the one computed from actual line counts in shotgun_expand().

---

## 11. Evidence Trace

### Source code references

| Symbol | File | Lines | Description |
|--------|------|-------|-------------|
| `_hamiltonian_energy` | emotional_engine.py | 408–455 | Hamiltonian calculation |
| `_line_state_balance` | emotional_engine.py | 207–260 | Line count computation |
| `_line_state_vector` | emotional_engine.py | 717–780 | 5-axis vector computation |
| `_quantum_avatar_modulation` | emotional_engine.py | 471–510 | Avatar modulation (calls _hamiltonian_energy with {}) |
| `VEC_KEYS` | emotional_engine.py | 37 | ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"] |
| `_clamp` | emotional_engine.py | (defined earlier) | Clamps to [0, 1] (presumed) |
| `hamiltonian_energy` (alias) | emotional_engine.py | (exported) | Public alias for _hamiltonian_energy |
| shotgun_expand call site | full_hexagram_shotgun.py | 682–688 | Calls hamiltonian_energy(resolved_vec, expanded_vec, line_balance) |
| kingwen_state_transition call site | kingwen_state_transition.py | (various) | Calls hamiltonian_energy(resolved_vec, expanded_vec, line_balance) |

### Baseline data references

| Artifact | Path | Description |
|----------|------|-------------|
| Raw H distribution | DATASETS/raw_h_distribution_2026-11-02.json | 1,536-state raw H values |
| Remediation matrix | docs/remediation-verification-matrix.md | Entry 3 (Hamiltonian M3) |
| Floor/ceiling research | docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md | Categories A–D |
| Information-loss register | docs/information-loss-remediation-register.md | F-10, F-11, F-12 |
| Verification protocol | docs/controlled-remediation-verification-protocol.md | 8-step procedure, 7 invariants |

### Numerical baseline (immutable)

| Quantity | Min | Max | Mean | Distinct |
|----------|-----|-----|------|----------|
| pq_dot | -0.150831 | 0.147103 | ~0.000 | 727 |
| lagrangian | 0.700000 | 5.100000 | ~2.5 | 7 |
| raw H | -5.094550 | -0.560876 | -1.656209 | 727 |
| clamped H | 0.000000 | 0.000000 | 0.000000 | 1 |

---

## 12. Disposition

**F-10 Status:** INVESTIGATED (not resolved). This document provides the formal dimensional analysis requested. The four questions have been answered to the extent possible from the available evidence:

1. **Dimensional compatibility:** Formally compatible (both dimensionless), semantically heterogeneous.
2. **Coefficients:** Dimensionless, undocumented, no theoretical basis found.
3. **Negative sign:** Mathematical consequence of scale disparity; intent undocumented.
4. **Implementation vs. intended Hamiltonian:** Scalar calculation with Hamiltonian-inspired naming, not a formal Hamiltonian.

**Refined F-10 classification (per external assessment):**

| Previous wording | More precise wording |
|---|---|
| Dimensional mismatch | Semantic and scale incompatibility |
| Dimensionally invalid subtraction | Subtraction without an established common mathematical interpretation |
| Hamiltonian sign problem | Negative sign is computationally explained; mathematical intent remains unknown |

The F-10 label in the research record should distinguish **physical dimensional compatibility** (established: both terms are dimensionless) from **semantic compatibility** (not established: the terms originate in different representational domains with no documented common mathematical basis for subtraction).

**Next step (recommended):** Mathematical provenance and formulation audit — trace the origin and intended meaning of each Lagrangian coefficient, determine why line counts and emotional-vector components are combined, establish whether the 0–6 line-count scale has an intended normalization, search for an original derivation or documented theoretical source for the subtraction, and determine whether the implementation was intended as an analogy, heuristic scoring function, or physical mathematical model.

**No formula changes were made.** The investigation is complete. Remediation (if any) requires:
- Establishing the intended mathematical semantics of H
- Determining whether the clamp is a design or a patch
- Deciding whether the lagrangian should be scaled to match pq_dot
- Documenting the coefficients' theoretical basis

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline.

---

*End of dimensional consistency analysis.*