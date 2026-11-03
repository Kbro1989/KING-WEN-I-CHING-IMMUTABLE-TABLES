# M2 Expectation and Consensus Correspondence Evidence Record

**Research Gate:** QSMC-1
**Correspondence ID:** M2-EXPECTATION-CONSENSUS
**Mathematical Object:** Expectation / consensus operation
**Status:** EVIDENCE COLLECTED -- NOT YET VALIDATED
**Date:** 2026-11-02

---

## 1. King Wen Implementation

### Source: `_compute_consensus_from_resolved()` in `emotional_engine.py:1083`

This function computes a "consensus" across all 512 resolved states. It is NOT a simple arithmetic mean. It is a multi-stage weighted aggregation with Gaussian weighting, pool blending, and hexagram-level scoring.

### Stage 1: Temporal consensus

```python
temporal_counts: Dict[str, int] = {}
for item in resolved:
    temporal = str(item.get("phase_temporal", "") or "")
    temporal_counts[temporal] = temporal_counts.get(temporal, 0) + 1
consensus_temporal = max(temporal_counts, key=temporal_counts.__getitem__)
```

**Operation:** Mode (most frequent value) of `phase_temporal` across 512 states.
**Mathematical type:** Mode of a categorical distribution.
**Weighting:** Uniform (each state counts as 1).
**No probability measure.**

### Stage 2: Porosity consensus

```python
porosities = [float(item.get("inject_site", {}).get("porosity", 0.35)) for item in resolved]
porosity_mean = sum(porosities) / len(porosities)
porosity_mode = max(set(porosities), key=porosities.count)
```

**Operation:** Arithmetic mean AND mode of porosity values across 512 states.
**Mathematical type:** First moment (mean) and mode of a finite set.
**Weighting:** Uniform (each state counts as 1).
**No probability measure.**

### Stage 3: Gaussian-weighted vector consensus

```python
tau_values = [_tau_for_resolved(item, emotional_input=emotional_input, hex_variance=...) for item in resolved]
mu = _mode_of_tau(tau_values)
sigma = max(1e-9, (sum(porosity_norms) / len(porosity_norms)) / 2.0)
raw_weights = [_gaussian_weight(t, mu, sigma) for t in tau_values]
weight_sum = sum(raw_weights)
weights = [w / weight_sum for w in raw_weights] if weight_sum > 1e-12 else raw_weights

vec_sums = {k: 0.0 for k in vec_keys}
for item, w in zip(resolved, weights):
    rv = item.get("resolved_vector") or {}
    for k in vec_keys:
        vec_sums[k] += float(rv.get(k, 0.0) or 0.0) * w
consensus_vector = {k: (vec_sums[k] / weight_sum if weight_sum else 0.0) for k in vec_keys}
```

**Operation:** Gaussian-weighted mean of 5-axis vectors across 512 states.
**Mathematical type:** Weighted arithmetic mean with Gaussian kernel weights.
**Weighting:** Gaussian weights derived from tau_values (per-state temporal/porosity composite), centered on mode tau, with sigma from porosity norms.
**Normalization:** Weights sum to 1.0 (renormalized).
**This IS a weighted expectation** under a Gaussian-derived weight distribution over the 512 states.

### Stage 4: Pool blending

```python
pool_blend = 0.3
for i, k in enumerate(vec_keys):
    consensus_vector[k] = (
        consensus_vector[k] * (1 - pool_blend)
        + primary_avg[i] * pool_blend * 0.6
        + secondary_avg[i] * pool_blend * 0.4
    )
```

**Operation:** Linear blend of consensus vector with primary/secondary emotional pool averages.
**Mathematical type:** Convex combination (affine blend).
**Weights:** 0.7 consensus + 0.18 primary + 0.12 secondary (fixed, not data-derived).

### Stage 5: Hexagram scoring (selection, not consensus)

```python
hex_scores: Dict[int, float] = {}
for item, w in zip(resolved, weights):
    h_id = int(item.get("hexagram_id") or 0)
    # ... multi-factor scoring ...
    score = (vector_score * 0.4 + inject_score * 0.15 + temporal_alignment * 0.1 + pool_alignment * 0.1 + temporal_bias * 0.25) * w
    hex_scores[h_id] = hex_scores.get(h_id, 0.0) + score

consensus_hexagram_id = max(hex_scores, key=hex_scores.__getitem__)
```

**Operation:** Weighted aggregation of per-hexagram scores, then argmax selection.
**Mathematical type:** Weighted sum followed by maximum (not an expectation -- this is a selection operation).
**Weighting:** Same Gaussian weights as Stage 3.

### King Wen Expectation Summary

| Property | Value |
|---|---|
| Input space | 512 resolved states (64 hexagrams x 8 phases) |
| Weighting | Gaussian (tau-derived, centered on mode, sigma from porosity) + fixed pool blend |
| Operations | Mode (temporal), mean (porosity), weighted mean (vectors), convex blend (pools), argmax (hexagram selection) |
| Probability measure | NOT a formal probability measure -- weights are Gaussian-derived but not from a normalized probability distribution over a sigma-algebra |
| Observable | 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) |
| Normalization | Weights renormalized to sum to 1.0; consensus vector divided by weight_sum |
| Output | consensus_vector (5D), consensus_hexagram_id (single selection), consensus_temporal (mode), consensus_porosity_mean/mode |

---

## 2. Quantum-Sim Implementation

### Source: `quantumlab/observables/expectation.py`

Quantum-Sim computes expectation values of physical observables over quantum wavefunctions. The standard quantum mechanical definition:

```
<O> = integral(psi* O psi) dx = integral(|psi|^2 * O) dx  (for multiplicative operators)
```

### Position expectation

```python
def position_expectation(wf) -> float:
    prob = wf.probability_density  # |psi|^2
    if isinstance(wf, WaveFunction1D):
        return float(np.sum(wf.grid.x * prob) * wf.grid.dx)
    elif isinstance(wf, WaveFunction2D):
        return float(np.sum(wf.grid.X * prob) * wf.grid.dx * wf.grid.dy)
    elif isinstance(wf, WaveFunction3D):
        return float(np.sum(wf.grid.X * prob) * wf.grid.dx * wf.grid.dy * wf.grid.dz)
```

**Operation:** Discrete Riemann sum approximating `integral(x * |psi(x)|^2) dx`.
**Mathematical type:** Expectation value of position operator under Born rule probability measure `P(x) = |psi(x)|^2`.
**Weighting:** Probability density `|psi|^2` (normalized to unit total probability).
**Normalization:** `wf.normalize()` ensures `integral(|psi|^2) dx = 1`, so weights sum to 1.
**Measure:** Born rule probability measure on continuous spatial domain.

### Momentum expectation

```python
def momentum_expectation(wf, direction='x', hbar=1.0) -> float:
    phi = wf.fourier_transform()  # momentum-space wavefunction
    phi_prob = np.abs(phi) ** 2
    # ... integral(k * |phi(k)|^2) dk
```

**Operation:** Expectation value of momentum operator in momentum space.
**Mathematical type:** Fourier-transformed expectation under Born rule in momentum basis.
**Weighting:** Momentum-space probability density `|phi(k)|^2`.

### Energy expectation

```python
def total_energy_expectation(wf, potential, hbar=1.0, m=1.0) -> float:
    T_exp = kinetic_energy_expectation(wf, hbar, m)  # <p^2>/(2m)
    V_exp = potential_energy_expectation(wf, potential)  # <V(x)>
    return float(T_exp + V_exp)
```

**Operation:** Sum of kinetic and potential energy expectations.
**Mathematical type:** Expectation of Hamiltonian operator H = T + V under Born rule.
**Weighting:** Position-space probability density `|psi(x)|^2` for V; momentum-space for T.

### Quantum-Sim Expectation Summary

| Property | Value |
|---|---|
| Input space | Normalized wavefunction psi(x) on spatial grid |
| Weighting | Born rule probability density \|psi(x)\|^2 (normalized to 1) |
| Operations | Riemann sum: sum(x * \|psi(x)\|^2) * dx |
| Probability measure | Born rule: P(x) = \|psi(x)\|^2, with integral(P) = 1 |
| Observable | Position, momentum, energy (multiplicative or differential operators) |
| Normalization | L2 unit norm: integral(\|psi\|^2) dx = 1 |
| Output | Scalar expectation value (real number) |
| Mathematical foundation | Quantum mechanical expectation value <O> = <psi|O|psi> |

---

## 3. Comparison

### 3.1 Structural comparison

| Property | King Wen | Quantum-Sim |
|---|---|---|
| Input space | 512 discrete resolved states | Normalized wavefunction on spatial grid |
| Weighting | Gaussian-derived weights (tau-centered, porosity-scaled) + fixed pool blend | Born rule probability density \|psi(x)\|^2 |
| Weight normalization | Weights renormalized to sum to 1.0 | L2 norm of wavefunction = 1 (weights inherently normalized) |
| Probability measure | NOT a formal probability measure | Born rule probability measure |
| Observable | 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) | Position, momentum, energy (physical operators) |
| Output type | 5D vector + single hexagram selection + temporal mode | Scalar real number |
| Operation type | Weighted mean + convex blend + argmax selection | Riemann sum (integral approximation) |
| Dimensionality | 5D emotional space | 1D/2D/3D physical space |

### 3.2 What IS structurally similar

1. **Weighted summation form**: Both compute `sum(w_i * f_i)` where `w_i` are weights and `f_i` are values. This is the general form of an expectation-like operation.

2. **Normalization to unit total**: Both renormalize weights so they sum to 1.0.

3. **Multi-component aggregation**: Both aggregate over multiple components (512 states / spatial grid points) to produce a single result.

### 3.3 What is NOT the same

1. **Probability measure**: Quantum-Sim uses the Born rule (`P(x) = |psi(x)|^2`), a fundamental postulate of quantum mechanics. King Wen uses Gaussian-derived weights from tau values and porosity -- these are not derived from a probability measure over a sigma-algebra.

2. **State representation**: Quantum-Sim operates on a normalized wavefunction (complex-valued, L2-normalized). King Wen operates on 512 discrete records (dicts with vectors, metadata, inject_site).

3. **Observable**: Quantum-Sim computes expectations of physical operators (position, momentum, energy). King Wen computes a weighted mean of emotional vectors. The "observable" in King Wen is not a physical operator but a 5-axis emotional state.

4. **Weighting basis**: Quantum-Sim weights are derived from the wavefunction itself (Born rule). King Wen weights are derived from tau values (per-state temporal/porosity composite) and then Gaussian-transformed. The weights are not intrinsic to the state representation.

5. **Selection vs expectation**: King Wen includes an argmax selection (`consensus_hexagram_id = max(hex_scores, key=...)`) which is NOT an expectation operation -- it is a decision/selection operation. Quantum-Sim has no analogous selection step.

6. **Pool blending**: King Wen blends the consensus with primary/secondary emotional pool averages using fixed weights (0.7/0.18/0.12). Quantum-Sim has no analogous blending -- the expectation is purely from the wavefunction.

7. **Temporal mode**: King Wen computes a mode (most frequent temporal label) alongside the vector consensus. Quantum-Sim has no temporal mode concept.

---

## 4. Mathematical Correspondence Assessment

### 4.1 Kernel-level

Both operations use the general form `sum(w_i * f_i) / sum(w_i)` where weights are normalized. This is the arithmetic mean formula, which is a special case of the expectation value under a uniform probability measure.

**Status: Shared at the formula level.**

### 4.2 Implementation-level

The weighting mechanisms are fundamentally different:
- Quantum-Sim: Born rule probability density (intrinsic to state, normalized by construction)
- King Wen: Gaussian-transformed tau values (extrinsic to state, renormalized)

The state representations are fundamentally different:
- Quantum-Sim: normalized complex wavefunction on spatial grid
- King Wen: 512 discrete records with vectors and metadata

**Status: NOT ESTABLISHED.**

### 4.3 Application-level

Both operations produce a single representative value from a collection of states. Both can be interpreted as "what is the central tendency of this collection." However:
- Quantum-Sim's expectation is a physical prediction (measurable quantity)
- King Wen's consensus is a synthetic aggregation (emotional/semantic state)

**Status: Partial conceptual relationship.**

### 4.4 Disposition

**M2-EXPECTATION-CONSENSUS: `partial` at conceptual level; mathematical correspondence `undetermined`**

The operations share the general form of weighted summation, but the weighting measures, state representations, observables, and mathematical foundations are different. A uniform arithmetic mean over 512 records is not automatically a quantum expectation value.

The weighting measure, normalization, observable, and state representation must be specified before mathematical correspondence can be assessed.

### 4.5 Three-Level Distinction

| Level | King Wen | Quantum-Sim | Status |
|---|---|---|---|
| Kernel-level | Weighted summation `sum(w_i * f_i) / sum(w_i)` | Same weighted summation form | SHARED -- general expectation formula |
| Implementation-level | Gaussian-tau weights + pool blend + argmax selection | Born rule probability density + Riemann sum | NOT ESTABLISHED -- weighting measure and state representation differ |
| Application-level | Emotional/semantic consensus + hexagram selection | Physical observable prediction | PARTIAL CONCEPTUAL -- both produce central tendency from collection |

### 4.6 What would be needed to upgrade to `defined`

1. A formal definition of the King Wen weight distribution as a probability measure (or proof that it is one).
2. A demonstration that the 512 states form a sample space with a defined sigma-algebra.
3. A specification of the King Wen "observable" as a mathematical operator (not just a vector component).
4. Reproducible numerical validation comparing King Wen consensus against a known expectation value.

### 4.7 What would make it `incompatible`

1. If the King Wen weights were found to not form a valid probability measure (e.g., negative weights, non-normalizable).
2. If the 512 states were found to not be independent samples (e.g., deterministic duplicates).
3. If the consensus operation were found to include non-linear transformations that violate expectation linearity.

---

## 5. Known Limitations

1. The King Wen consensus includes an argmax selection step (`consensus_hexagram_id`) which is not an expectation operation. This must be separated from the vector consensus.
2. The pool blending step uses fixed weights (0.7/0.18/0.12) that are not derived from the data. This is a design choice, not a mathematical necessity.
3. The temporal mode computation is a separate statistical operation (mode) that does not correspond to any Quantum-Sim quantity.
4. The `_tau_for_resolved` function (which computes per-state tau values) has not been fully inspected. Its definition affects the weighting measure.

---

## 6. Unresolved Questions

1. What is the mathematical definition of tau in `_tau_for_resolved`? Is it a physical quantity or a composite score?
2. Are the 512 resolved states independent samples, or are they deterministically generated from 64 hexagrams x 8 phases?
3. Does the Gaussian weighting produce a valid probability measure (non-negative, normalizable)?
4. Is the consensus operation commutative and associative (required for expectation under standard probability theory)?
5. What is the relationship between the 5-axis emotional vector and any physical observable?

### 6A. Additional Audit Questions (from external assessment)

A. Weight validity: Are all Gaussian-tau weights finite and nonnegative? What happens if their sum is zero, underflows, or becomes non-finite?

B. Record dependence: If the 512 states are deterministically generated from shared inputs, what does treating them as a collection imply statistically? They should not automatically be described as independent samples.

C. Aggregation order: Does changing the order of operations change the result? For example, does pool blending before Gaussian weighting produce the same result as Gaussian weighting before pool blending? Does the final argmax preserve ties or resolve them by iteration order?

---

## 7. Evidence Provenance

- King Wen source: `emotional_engine.py:1083-1260` (canonical engine, revision 71fbf28f8e92c6a7de74c50a304906ef81963a7d)
- Quantum-Sim source: `quantumlab/observables/expectation.py:1-185` (v1.3.0, merged 2026-11-02)
- Audit date: 2026-11-02
- Evidence level: E2 (conceptual correspondence) for weighted summation form; E1 (lexical overlap) for terminology
- Mathematical correspondence (E3): NOT YET DEMONSTRATED
- Gate 2 status: UNCHANGED (OPEN -- Producer unrecovered)
