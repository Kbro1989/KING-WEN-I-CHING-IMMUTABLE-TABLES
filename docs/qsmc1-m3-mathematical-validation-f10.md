# F-10 Mathematical Validation — Semantic and Scale Compatibility

## 1. Investigation charter

**Question:** Are the 5-axis continuous emotional vector and the 6-line discrete state counts semantically compatible for subtraction in `H = pq_dot - lagrangian`?

**Authorization:** User-authorized, 2026-11-02. No source-code modifications. No formula changes. No normalization, rescaling, or clamp changes. No alteration of the 1,536-state baseline or frozen provenance artifacts. No implementation consolidation or deletion. No commits.

**Governing constraint:** Distinguish numerical compatibility, semantic compatibility, and theoretical justification. Establishing that two quantities are dimensionless does not establish that subtracting them is mathematically meaningful.

**Deliverable:** This document (`docs/qsmc1-m3-mathematical-validation-f10.md`). Analytical investigation only.

**Gate 2 remains OPEN.** Mathematical validation is authorized; remediation is not.

---

## 2. Source definitions

### 2.1 The Hamiltonian function (current implementation)

Location: `emotional_engine.py`, lines 408–455.

```python
def _hamiltonian_energy(
    resolved_vector: List[float],
    expanded_vector: List[float],
    line_balance: Dict[str, Any],
) -> float:
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))

    yin_count = float(line_balance.get("yin_count", 0) or 0)
    yang_count = float(line_balance.get("yang_count", 0) or 0)
    yao_count = float(line_balance.get("yao_count", 0) or 0)
    changing_count = float(line_balance.get("changing_count", 0) or 0)
    old_yang_count = float(line_balance.get("old_yang_count", 0) or 0)
    old_yin_count = float(line_balance.get("old_yin_count", 0) or 0)
    stable_yao_count = float(line_balance.get("stable_yao_count", 0) or 0)
    stable_yin_count = float(line_balance.get("stable_yin_count", 0) or 0)

    old_yao_count = float(line_balance.get("old_yao_count", 0) or 0)
    old_dy = old_yang_count - old_yin_count
    stable_dy = stable_yao_count - stable_yin_count

    dy = yang_count - yin_count
    yao_dy = yao_count - 3.0
    changing_dy = changing_count - (6.0 - changing_count)

    lagrangian = (
        abs(dy) * 0.5
        + abs(yao_dy) * 0.3
        + abs(changing_dy) * 0.2
    )
    return _clamp(pq_dot - lagrangian)
```

### 2.2 The clamp function

Location: `emotional_engine.py`, lines 71–72.

```python
def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
```

### 2.3 Resolved and expanded vectors

The 5-axis vectors come from `_pool_weights_for_hex()` and `expand_hexagram()`:

- `resolved_vector`: sampled phase-shifted vector (5 floats in [0,1])
- `expanded_vector`: primary pool vector blended with trigram/neighbor/intent modulation (5 floats in [0,1])
- `line_balance`: dict of 6-line counts (yin_count, yang_count, yao_count, changing_count, etc.) and ratios

The vectors and line_balance are produced by the same function (`expand_hexagram`) but represent different aspects of the hexagram state: the vector is an emotional state representation, the line_balance is a structural line-state summary.

---

## 3. Vector construction

### 3.1 The 5-axis emotional vector space

VEC_KEYS: `["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]`

Each component is a float in [0, 1], derived from:
- Line-state balance (yin/yang/yao ratios)
- Trigram structural context (upper/lower trigram vectors)
- Neighbor continuity (adjacent hexagram blending)
- Intent match (request text keyword scoring)
- Phase shift (temporal displacement)

The vector represents an **emotional state** — a point in a 5-dimensional continuous space where each axis measures a distinct emotional dimension.

### 3.2 The 6-line discrete state space

The line_balance dict contains:
- `yin_count`, `yang_count`, `yao_count`: counts of each line type (integers, sum = 6)
- `changing_count`: count of changing lines (integer, 0–6)
- `old_yin_count`, `old_yang_count`, `old_yao_count`: temporal variants
- `stable_yin_count`, `stable_yang_count`, `stable_yao_count`: temporal variants
- `yin_ratio`, `yang_ratio`, `yao_ratio`, `changing_ratio`: normalized counts (floats, sum = 1.0)

The line balance represents **structural hexagram state** — a discrete 6-line configuration with ternary (yin/yang/yao) values.

### 3.3 The representational gap

The two spaces are **not the same space**:
- The 5-axis vector is a **continuous emotional representation** (what the hexagram "feels like")
- The 6-line state is a **discrete structural representation** (what the hexagram "is")

There is no documented mapping between these spaces. The vector is derived from the line state (via `_line_state_vector`), but the derivation involves multiple transformations (trigram blending, neighbor continuity, intent modulation, phase shift) that make the relationship non-trivial and non-invertible.

---

## 4. pq_dot derivation

### 4.1 Definition

```python
momentum = [max(0.0, float(v)) for v in resolved_vector]
q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))
```

### 4.2 Scale analysis

- `resolved_vector[i]` ∈ [0, 1] (sampled phase-shifted emotional vector)
- `expanded_vector[i]` ∈ [0, 1] (primary pool vector with modulation)
- `momentum[i]` = max(0, resolved[i]) = resolved[i] (since resolved ≥ 0)
- `q_dot[i]` = resolved[i] - expanded[i] ∈ [-1, 1]
- `term_i` = resolved[i] × (resolved[i] - expanded[i]) ∈ [-1, 1]

**Empirical range (from 1,536-state dataset):** pq_dot ∈ [-0.150831, 0.147103], with 727 distinct values.

### 4.3 Semantic analysis

pq_dot is a sum of products: resolved_vector[i] × (resolved_vector[i] - expanded_vector[i]). This is a **dot product** of the resolved vector with its own difference from the expanded vector. It measures the correlation between the resolved emotional state and the change from the expanded state.

**What pq_dot represents:** The degree to which the resolved emotional state "agrees with" its own phase-shifted deviation from the base expanded state. Higher values indicate the resolved state is both large and moving in the same direction as its deviation.

**What pq_dot does NOT represent:** It is not a momentum in the physics sense. It is not a time derivative of a canonical coordinate. It is a heuristic correlation measure between two vectors in a 5-dimensional emotional space.

### 4.4 The `momentum = max(0, resolved)` simplification

Since resolved_vector components are already in [0, 1] (non-negative), `max(0, resolved[i])` is an identity operation. The `max(0, ...)` guard is defensive but has no mathematical effect in the current implementation. It does not change the value.

---

## 5. Lagrangian derivation

### 5.1 Definition (current V2)

```python
dy = yang_count - yin_count                      # signed binary differential
yao_dy = yao_count - 3.0                        # yao vs neutral midpoint (6/2)
changing_dy = changing_count - (6.0 - changing_count)  # changing vs stable

lagrangian = (
    abs(dy) * 0.5
    + abs(yao_dy) * 0.3
    + abs(changing_dy) * 0.2
)
```

### 5.2 Scale analysis

| Differential | Definition | Range | Distinct values |
|---|---|---|---|
| dy | yang_count - yin_count | [-6, 6] (integers, same parity as 6) | 7 (even values: -6,-4,-2,0,2,4,6) |
| yao_dy | yao_count - 3.0 | [-3, 3] (integers) | 7 (-3,-2,-1,0,1,2,3) |
| changing_dy | 2*changing_count - 6 | [-6, 6] (even integers) | 7 (-6,-4,-2,0,2,4,6) |

**Empirical range (from 1,536-state dataset):** lagrangian ∈ [0.7, 5.1], with 7 distinct values.

### 5.3 Semantic analysis

The lagrangian is a **weighted sum of absolute line-state differentials**:

- `abs(dy) * 0.5`: The absolute imbalance between yang and yin lines, weighted 0.5
- `abs(yao_dy) * 0.3`: The absolute deviation of yao count from the neutral midpoint (3), weighted 0.3
- `abs(changing_dy) * 0.2`: The absolute imbalance between changing and stable lines, weighted 0.2

**What the lagrangian represents:** A measure of structural imbalance in the 6-line hexagram configuration. Higher values indicate greater deviation from a balanced (3 yin, 3 yang, 3 yao, 3 changing) state.

**What the lagrangian does NOT represent:** It is not a Lagrangian in the physics sense (L = T - V). It does not involve kinetic or potential energy. It is not derived from a variational principle. It is a heuristic weighted sum of structural imbalances.

### 5.4 The V1 → V2 evolution

**V1 (commit 780d9c4bfe):**
```python
lagrangian = (
    abs(line_balance.get("yin_ratio", 0.0) - line_balance.get("yang_ratio", 0.0)) * 0.5
    + line_balance.get("yao_ratio", 0.0) * 0.3
    + line_balance.get("changing_ratio", 0.0) * 0.2
)
```
- Inputs: ratios (yin_ratio, yang_ratio, yao_ratio, changing_ratio) — all in [0, 1]
- Scale: ~0 to 1 (ratio scale)
- Coefficients 0.5/0.3/0.2 applied to ratio-scale quantities
- pq_dot used `abs(phase_shift)` (phase shift values, scale ~0.01-0.1)

**V2 (commit 6239ba9bd7, current):**
```python
lagrangian = (
    abs(dy) * 0.5
    + abs(yao_dy) * 0.3
    + abs(changing_dy) * 0.2
)
```
- Inputs: raw counts (yang_count - yin_count, yao_count - 3.0, 2*changing_count - 6) — scale 0-6
- Scale: ~0.7 to 5.1 (count scale)
- Coefficients 0.5/0.3/0.2 carried through **unchanged** from V1
- pq_dot uses `(resolved[i] - expanded[i])` (vector differences, scale ~0.01-0.1)

**Critical finding:** The coefficients 0.5, 0.3, and 0.2 were designed for ratio-scale inputs (V1, where all inputs were in [0,1]) but are now applied to raw count-scale inputs (V2, where inputs are in [0,6]). The coefficients were carried through unchanged across both versions without adjustment for the scale change. This is the root cause of the scale incompatibility.

### 5.5 Coefficient provenance

**Source search results:**
- `git log -S "abs(dy) * 0.5"` → commit 6239ba9bd7 (first appearance of V2 formula)
- `git log -S "abs(yin_ratio - yang_ratio) * 0.5"` → commit 780d9c4bfe (first appearance of V1 formula)
- No commit message, code comment, or documentation explains the choice of 0.5/0.3/0.2
- No wiki_math_corpus.jsonl entry contains these coefficients in a Hamiltonian context
- No QuantumLab code contains these coefficients
- The coefficients sum to 1.0, suggesting a convex-combination interpretation, but this is invalid (see Section 7)

**Assessment:** The coefficients are undocumented. They appear to have been chosen heuristically in V1 (where they produced reasonable results on ratio-scale inputs) and carried through to V2 without adjustment for the scale change. There is no theoretical basis for their values.

---

## 6. Numerical compatibility

### 6.1 Definition

Two quantities are **numerically compatible** if they are both dimensionless (pure numbers) and subtraction is defined.

### 6.2 Analysis

- pq_dot: dimensionless (sum of products of dimensionless vector components)
- lagrangian: dimensionless (sum of products of dimensionless counts and dimensionless coefficients)

**Both terms are dimensionless. Subtraction is defined.**

### 6.3 Verdict

**Numerical compatibility: ESTABLISHED.** Both quantities are pure numbers. No dimensional incompatibility exists in the physical sense.

---

## 7. Semantic compatibility

### 7.1 Definition

Two quantities are **semantically compatible** if they represent comparable aspects of the same mathematical space, such that their difference has a meaningful interpretation.

### 7.2 Analysis

| Property | pq_dot | lagrangian |
|---|---|---|
| **Domain** | 5-axis continuous emotional vector space | 6-line discrete structural state space |
| **Representation** | Point in 5D continuous space [0,1]^5 | 6-line ternary configuration (yin/yang/yao) |
| **Scale** | ~[-0.15, 0.15] (vector differences) | ~[0.7, 5.1] (weighted line counts) |
| **Meaning** | Correlation between resolved emotional state and its deviation from expanded state | Structural imbalance in the 6-line hexagram configuration |
| **Derivation** | Derived from vector components via dot product | Derived from line counts via weighted absolute differences |
| **Units** | Dimensionless (emotional intensity) | Dimensionless (structural imbalance) |

### 7.3 The scale disparity

- pq_dot range: [-0.150831, 0.147103] (727 distinct values)
- lagrangian range: [0.7, 5.1] (7 distinct values)
- Minimum lagrangian (0.7) >> maximum |pq_dot| (0.150831)
- Ratio: minimum lagrangian is 4.6× the maximum |pq_dot|

**Consequence:** `pq_dot - lagrangian` is ALWAYS negative for all 1,536 tested states. The _clamp() function converts all negative values to 0.0.

### 7.4 The convex-combination problem

The coefficients 0.5, 0.3, 0.2 sum to 1.0, which superficially suggests a convex combination (weighted average). However:

1. A convex combination requires elements of a **common mathematical space** with nonnegative weights summing to one.
2. The three Lagrangian terms (|dy|, |yao_dy|, |changing_dy|) are all line-count differentials on the scale [0,6] — they ARE in a common space.
3. But pq_dot is NOT in this space — it is a vector-space correlation on the scale [0,1].
4. Therefore, the subtraction `pq_dot - lagrangian` combines elements from **different mathematical spaces** (5D continuous vector vs. 6-line discrete counts).
5. The convex-combination interpretation applies only to the Lagrangian terms, not to the overall `pq_dot - lagrangian` expression.

### 7.5 Verdict

**Semantic compatibility: NOT ESTABLISHED.**

The two terms are dimensionless (numerically compatible) but represent fundamentally different aspects of the hexagram state:
- pq_dot measures emotional state variation in a 5-dimensional continuous space
- lagrangian measures structural line-state imbalance in a 6-line discrete configuration

There is no documented mapping between these spaces. The subtraction combines a vector-space correlation with a line-count imbalance, which is not a standard mathematical operation. The result is always negative, which is then clamped to zero, producing a constant output.

---

## 8. Theoretical justification

### 8.1 Definition

**Theoretical justification** exists when there is a documented mathematical derivation or principled reason for the operation, coefficients, and expected behavior.

### 8.2 Analysis

| Question | Answer | Evidence |
|---|---|---|
| Why subtract lagrangian from pq_dot? | Undocumented | No code comment, commit message, or spec explains the subtraction |
| Why coefficients 0.5, 0.3, 0.2? | Undocumented | No derivation found; coefficients carried from V1 to V2 without scale adjustment |
| Why no normalization between scales? | Undocumented | V1 used ratio-scale inputs; V2 uses raw counts; coefficients unchanged |
| What does negative H represent? | Undocumented | Three interpretations possible (see Section 9) |
| Is this a Hamiltonian? | No | No canonical variables, no time derivative, no Lagrangian function, no Hamilton's equations |
| Is this a convex combination? | No | Elements not in common space (different scales, different representations) |
| Is this a heuristic? | Likely | Downstream usage ("animation intensity") suggests heuristic role; no documentation confirms |

### 8.3 The "parsed wiki sources" reference

The code comment at line 392 references "Hamiltonian / Gaussian / Trigram math from parsed wiki sources" and `wiki_math_corpus.jsonl`.

**Investigation result (Section 15 of provenance audit):** The wiki_math_corpus.jsonl contains standard Wikipedia articles on Hamiltonian mechanics. The Hamiltonian mechanics article provides vocabulary (H, p, q, L, Legendre transform) but contains NO `pq_dot - lagrangian` formula, NO 0.5/0.3/0.2 coefficients in Hamiltonian context, and NO emotional vectors or line counts. The reference is aspirational — it claims a source that does not contain the formula.

### 8.4 Verdict

**Theoretical justification: NOT ESTABLISHED.**

No documented derivation, theoretical basis, or principled reason exists for:
- The subtraction operation
- The coefficient values
- The absence of normalization
- The sign convention

The implementation is most consistent with a **heuristic scoring function** or **custom scalar calculation** with Hamiltonian-inspired naming, not a formal Hamiltonian.

---

## 9. Three interpretations of negative H

Since `pq_dot - lagrangian` is always negative (lagrangian min 0.7 >> |pq_dot| max 0.15), the _clamp() always returns 0.0. Three interpretations exist:

### 9.1 Energy deficit interpretation

**Claim:** H represents an energy deficit when the system is "out of balance" (lagrangian exceeds momentum). Negative H means the system is in a deficit state, clamped to zero (minimum energy).

**Assessment:** Plausible as a heuristic, but undocumented. The concept of "energy deficit" is not defined anywhere in the codebase. The clamp to zero means the "deficit" information is discarded (all deficits map to the same value).

**Status:** Plausible but unverified. Not supported by documentation.

### 9.2 Scale bug interpretation

**Claim:** The lagrangian should be normalized to the same scale as pq_dot before subtraction. The coefficients were designed for ratio-scale inputs (V1) but applied to raw count-scale inputs (V2) without adjustment. If the lagrangian were divided by an appropriate factor (e.g., 6.0 or 10.0), H could produce meaningful nonzero values.

**Assessment:** Supported by the V1→V2 evolution analysis. In V1, all inputs were ratios in [0,1], and the coefficients produced a lagrangian in [0,1]. In V2, the inputs are raw counts in [0,6], but the same coefficients produce a lagrangian in [0.7, 5.1]. The scale mismatch is a direct consequence of carrying coefficients across a scale change without adjustment.

**Status:** Strongly supported by implementation history. This is the most likely explanation for the always-negative result.

### 9.3 Formula error interpretation

**Claim:** The subtraction is simply wrong — the two terms should not be combined this way. The lagrangian and pq_dot measure different things and should not be subtracted.

**Assessment:** Possible, but the existence of V1 (where the formula worked on ratio-scale inputs) suggests the operation was intended to work in some form. The issue is the scale change, not necessarily the operation itself.

**Status:** Possible but less likely than interpretation 2, given V1's functional behavior.

---

## 10. Model classification

### 10.1 Classification options

| Classification | Definition | Evidence for | Evidence against |
|---|---|---|---|
| Physical Hamiltonian | Formal Hamiltonian mechanics with canonical variables, Hamilton's equations, conservation laws | Uses vocabulary (H, p, q, L, Legendre transform) | No canonical variables, no time derivative, no Hamilton's equations, no conservation law |
| Heuristic scoring function | Custom scalar calculation producing a score for downstream use | Coefficients sum to 1.0 (suggests weighted combination); downstream usage ("animation intensity") suggests heuristic role | No documentation confirms heuristic intent |
| Analogy | Borrows Hamiltonian concepts metaphorically | Hamiltonian-inspired naming and structure | No explicit "this is an analogy" documentation |
| Custom scalar calculation | Arbitrary formula with no theoretical basis | No derivation found; coefficients undocumented; scale mismatch | — |

### 10.2 Evidence assessment

**For physical Hamiltonian:** The code uses Hamiltonian vocabulary and structure (H = pq_dot - lagrangian, resembling Hamilton's equations). However, it lacks all formal requirements: no canonical variables (p, q are vectors and line counts, not conjugate pairs), no time derivative (q_dot is a vector difference, not a dynamical variable), no Lagrangian function (ℒ is a weighted sum of counts, not a function of q and \dot q), no Hamilton's equations (\dot q = ∂H/∂p, \dot p = -∂H/∂q).

**For heuristic:** The coefficients sum to 1.0 (suggesting a weighted combination), the output is clamped to [0,1] (suggesting a score), and the downstream usage is "animation intensity" (a heuristic application). However, no documentation explicitly states "this is a heuristic."

**For analogy:** The code borrows Hamiltonian concepts (energy, Lagrangian, momentum, phase space) but does not implement them. This is consistent with an analogy, but again, no documentation confirms this.

**For custom scalar:** The formula has no theoretical basis, no derivation, and no documentation. It appears to be an independently constructed scalar calculation.

### 10.3 Verdict

**Model classification: Custom scalar calculation with Hamiltonian-inspired naming.**

The implementation is not a formal Hamiltonian (missing all formal requirements). It is most likely a heuristic or custom scalar calculation that borrowed Hamiltonian vocabulary from parsed wiki sources. The coefficients were chosen heuristically in V1 (ratio scale) and carried through to V2 (count scale) without adjustment, producing a scale mismatch that renders the output constant (0.0) for all tested states.

---

## 11. Summary of findings

### 11.1 Numerical compatibility

**ESTABLISHED.** Both terms are dimensionless. Subtraction is defined.

### 11.2 Semantic compatibility

**NOT ESTABLISHED.** The two terms represent fundamentally different aspects of the hexagram state:
- pq_dot: 5-axis continuous emotional vector correlation (scale ~0.01-0.15)
- lagrangian: 6-line discrete structural imbalance (scale ~0.7-5.1)

No documented mapping exists between these spaces. The subtraction combines elements from different mathematical domains.

### 11.3 Theoretical justification

**NOT ESTABLISHED.** No documented derivation, theoretical basis, or principled reason exists for the subtraction, coefficients, absence of normalization, or sign convention.

### 11.4 Root cause of always-zero output

The lagrangian (min 0.7) is always larger than |pq_dot| (max 0.15) by a factor of 4.6× minimum. Therefore `pq_dot - lagrangian` is always negative, and `_clamp(negative)` always returns 0.0.

The root cause is the **V1→V2 scale change without coefficient adjustment**: coefficients designed for ratio-scale inputs (0-1) were applied to raw count-scale inputs (0-6), making the lagrangian 2-3 orders of magnitude larger than pq_dot.

### 11.5 Three interpretations

| Interpretation | Likelihood | Status |
|---|---|---|
| Energy deficit (heuristic) | Plausible | Undocumented |
| Scale bug (normalization needed) | Most likely | Supported by V1→V2 evolution |
| Formula error (incompatible subtraction) | Possible | Less likely given V1 functionality |

### 11.6 Recommendation

The most likely explanation is the **scale bug interpretation** (interpretation 2): the lagrangian should be normalized to the same scale as pq_dot before subtraction. The coefficients were designed for ratio-scale inputs and were not adjusted when the inputs changed to raw counts.

However, this is a **mathematical validation finding**, not a remediation authorization. Any normalization would require:
- Establishing the intended mathematical semantics of H
- Determining the correct normalization factor
- Verifying that normalized H produces meaningful (nonzero) values
- Confirming downstream consumers handle the new range

These are separate from the provenance investigation and require their own authorization.

---

## 12. Safeguard

This investigation **does not** change the original M3 classification or close F-10. It provides a formal mathematical validation of the F-10 finding: semantic and scale incompatibility.

The three-layer finding remains untouched:
1. **Implementation:** A scalar calculation with arbitrary coefficients, no normalization, one-sided clamp
2. **Documentation:** A different formula (never implemented) that describes an intended design
3. **Mathematical interpretation:** Unresolved — no documented intent for the formula's meaning

**F-10 Status:** VALIDATED (semantic and scale incompatibility confirmed). The investigation establishes that:
- Numerical compatibility: YES (both dimensionless)
- Semantic compatibility: NO (different representational domains, different scales, different meanings)
- Theoretical justification: NO (no documented derivation, coefficients, or intent)
- Root cause: V1→V2 scale change without coefficient adjustment (scale bug interpretation most likely)

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline. Mathematical validation is authorized; remediation is not.

---

*End of F-10 mathematical validation.*