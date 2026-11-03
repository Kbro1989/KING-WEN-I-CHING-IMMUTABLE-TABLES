# QSMC-1 M3 Mathematical Provenance and Formulation Audit

## Audit of Formula Lineage, Coefficient Provenance, and Model Classification

**Status:** IN PROGRESS — Read-only investigation. No formula changes, rescaling, normalization, or clamp modifications performed during this audit.

**Artifact:** `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md`
**Date:** 2026-11-02
**Git revision:** 71fbf28f8e
**Baseline dataset:** `DATASETS/raw_h_distribution_2026-11-02.json` (1,536 states, immutable)
**Companion documents:**
- `docs/qsmc1-m3-dimensional-consistency-analysis.md` — F-10 dimensional analysis (620 lines)
- `docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` — Categories A–D (405 lines)
- `docs/remediation-verification-matrix.md` — Entry 3 (Hamiltonian M3)
- `docs/hamiltonian-equation-comparison-2026-10-27.md` — Candidate equations and worked cases
- `docs/ternary-paired-differential-math-correction-2026-08-02.md` — Governing spec for signed differentials
- `docs/formula-design-review-2026-10-27.md` — Axis-level design review (chaos, coherence, voiceWeight)
- `docs/audit-drift-report-2026-10-27.md` — Audit drift findings
- `docs/consumer-repair-specification-2026-10-29.md` — Consumer repair spec

---

## 1. Audit Charter

This document answers seven questions about the Hamiltonian energy calculation:

| Area | Question |
|------|----------|
| Formula lineage | Where did the implemented expression originate? |
| Coefficient provenance | Why 0.5, 0.3, and 0.2? |
| State representation | Why are six-line counts used alongside five-axis vectors? |
| Scale interpretation | Was normalization intended or deliberately omitted? |
| Sign convention | What does negative raw H represent? |
| Model classification | Physical Hamiltonian, heuristic, analogy, or custom scalar? |
| Historical intent | Do earlier implementations or documentation explain the design? |

**Preservation rule:** Three classifications are kept separate throughout:
- **Source-established:** Directly supported by implementation or documentation.
- **Historically established:** Supported by earlier versions, commits, or design records.
- **Unresolved:** Plausible interpretations without sufficient provenance.

Do not let a mathematically conventional formulation replace the implementation's historical intent simply because it looks more familiar.

**Constraint:** No formula changes, rescaling, normalization, or clamp modifications during this audit.

---

## 2. Formula Lineage

### 2.1 First appearance

**Git commit:** `ea89a9cf2d` — "Add emotional engine and temporal emotional engine with expand/collapse functionality"

This is the earliest commit in the repository's history that touches `emotional_engine.py`. The Hamiltonian function `_hamiltonian_energy()` was introduced in this commit as part of the initial emotional engine implementation.

**Source-established:** The function has existed since the first commit that added the emotional engine. No earlier version of the formula exists in the repository's git history.

### 2.2 Evolution through commits

| Commit | Message | Change to _hamiltonian_energy |
|--------|---------|-------------------------------|
| `ea89a9cf2d` | Add emotional engine and temporal emotional engine | Initial implementation |
| `ae1aa53b01` | feat: add consensus computation to collapse_full_128 | Hamiltonian used in consensus computation |
| `1bc45da38c` | feat: add Chinese-symbol-derived per-hexagram color resonance | Hamiltonian referenced in color derivation |
| `780d9c4bfe` | feat: Add full pool voice pick and multi-layer expansion scripts | Hamiltonian in multi-layer expansion |
| `4dc129cb6e` | formalize expansion-first state machine and readme map | Hamiltonian in expansion-first architecture |
| `f25af0e8d6` | ... | Hamiltonian referenced |
| `982cd484c8` | chore: update codebase with multiple empty change entries | No functional change |
| `6239ba9bd7` | Add new scripts for hexagram matching, lexical gate processing, and domain mapping | Hamiltonian in hexagram matching |
| `216a576268` | feat: Add King Wen 9-Bit State Resolver VHDL implementation | VHDL parity with Hamiltonian |
| `427521aedb` | Implement dynamic emotional input derivation in emotional_engine | Hamiltonian with dynamic input |
| `3c3d073c2d` | Enhance emotional engine with query token support and refactor consensus computation | Hamiltonian in consensus refactor |
| `7f2a06e256` | forming assets | Hamiltonian referenced |
| `2b17e46744` | Refactor code structure for improved readability and maintainability | Hamiltonian refactored |
| `10aac5e489` | Add wave-packet consistency tests, 2-clock testbed, and manifest validation scripts | Hamiltonian in wave-packet tests |
| `71fbf28f8e` | Add lua-math-tool.md | Current HEAD (no Hamiltonian change) |

**Historically established:** The Hamiltonian formula has been present since the emotional engine's inception. It has been referenced in multiple commits but the core formula (`pq_dot - lagrangian`, clamped) appears unchanged in structure. The argument was corrected from `hamiltonian_energy(vec, vec, ...)` to `hamiltonian_energy(resolved_vec, expanded_vec, ...)` during the ternary paired differential correction (commit `427521aedb` or nearby), fixing q̇ degeneracy.

### 2.2 Current implementation (as of 71fbf28f8e)

**File:** `emotional_engine.py`, lines 408–455

```python
def _hamiltonian_energy(resolved_vector, expanded_vector, line_balance):
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))
    
    lb = line_balance
    yin = lb.get('yin_count', 0)
    yang = lb.get('yang_count', 0)
    yao = lb.get('yao_count', 0)
    changing = lb.get('changing_count', 0)
    old_yang = lb.get('old_yang_count', 0)
    old_yin = lb.get('old_yin_count', 0)
    old_yao = lb.get('old_yao_count', 0)
    stable_yao = lb.get('stable_yao_count', 0)
    stable_yin = lb.get('stable_yin_count', 0)
    
    dy = (yang - yin) / 6.0          # NOTE: current code uses yang_count - yin_count (NOT /6.0)
    yao_dy = yao / 6.0 - 0.5          # NOTE: current code uses yao_count - 3.0 (NOT /6.0)
    old_dy = (old_yang - old_yin) / 6.0  # NOTE: current code uses old_yang_count - old_yin_count (NOT /6.0)
    stable_dy = (stable_yao - stable_yin) / 6.0  # NOTE: current code uses stable_yao_count - stable_yin_count (NOT /6.0)
    
    # Current: uses abs() — discards sign
    L = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2  # NOTE: current code uses abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2 where dy=yang_count-yin_count (NOT /6.0)
    
    raw = pq_dot - L
    return _clamp(raw, 0.0, 1.0)
```

**Important discrepancy:** The `hamiltonian-equation-comparison-2026-10-27.md` document (line 13-41) shows a *different* version of the formula than what exists in the actual source code. The document version divides by 6.0 and sums all four differentials; the actual source code uses raw counts (not divided by 6.0) and uses only three terms (dy, yao_dy, changing_dy — not old_dy or stable_dy).

**Source-established:** The actual implementation (lines 408-455 of emotional_engine.py) is the authoritative formula. The comparison document's formula is a *documentation* of a different (possibly earlier or intended) version.

### 2.3 Code comments and documentation

The function has a docstring (line 408) and the surrounding module has comments referencing "Hamiltonian" in the context of:
- Line 392: `# Hamiltonian / Gaussian / Trigram math from parsed wiki sources`
- Line 484: `the Hamiltonian energy, Gaussian kernel across temporal phases, and`
- Line 498: `# Hamiltonian energy drives animation intensity`

**Source-established:** The code comments describe the Hamiltonian as part of a broader mathematical framework that includes Gaussian kernels and trigram analysis. The Hamiltonian is described as driving "animation intensity" — a concrete downstream application, not an abstract physical model.

### 2.4 Downstream consumers

| Consumer | Usage | File:Line |
|----------|-------|-----------|
| full_hexagram_shotgun.py | `hamiltonian_energy(resolved_vec, expanded_vec, line_balance)` | 682-688 |
| kingwen_state_transition.py | `hamiltonian_energy(resolved_vec, expanded_vec, line_balance)` | (various) |
| _quantum_avatar_modulation | `hamiltonian_energy(resolved_vector, expanded_vector, {})` | 499 |
| verify_restored_state.py | Reads `HAMILTONIAN_PAIRED_DIFFERENTIALS` global (print-only) | 19 |

**Source-established:** The Hamiltonian output feeds into quantum avatar state modulation (animation intensity, color shift, scale factor) and is included in the shotgun expansion output. It is not used in any physics simulation or energy conservation calculation.

---

## 3. Coefficient Provenance

### 3.1 The coefficients: 0.5, 0.3, 0.2

**Source:** Hardcoded in `emotional_engine.py`, lines 450-452:
```python
lagrangian = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2
```

**Search results:** No documentation, comment, or git commit message explains the origin of these specific values. No specification document (including `ternary-paired-differential-math-correction-2026-08-02.md`) defines them.

**Source-established:** The coefficients are hardcoded constants with no documented derivation. They sum to 1.0 (0.5 + 0.3 + 0.2 = 1.0), suggesting they were intended as a convex combination (weights that sum to 1). However, they are applied to different-scale quantities:
- `abs(dy)` ∈ [0, 6] (line count differential)
- `abs(yao_dy)` ∈ [0, 3] (yao count minus midpoint)
- `abs(changing_dy)` ∈ [0, 6] (changing count differential)

So the "convex combination" interpretation is mathematically invalid — the weights sum to 1 but the terms they weight have different ranges.

**Unresolved:** The origin of 0.5, 0.3, and 0.2. No derivation, citation, or design rationale found in the codebase, documentation, or git history.

### 3.2 The 3.0 midpoint constant

**Source:** `yao_dy = yao_count - 3.0` (line 442)

The constant 3.0 represents the midpoint of the 6-line hexagram (6/2 = 3). This is a positional midpoint, not a physical quantity.

**Source-established:** The 3.0 is derived from the 6-line structure of the hexagram (6/2). It is not a tunable parameter.

### 3.3 The clamp bounds

**Source:** `return _clamp(pq_dot - lagrangian)` (line 455)

The `_clamp` function (defined earlier in emotional_engine.py) presumably clamps to [0.0, 1.0] based on the `__pycache__` and downstream usage patterns. The clamp bounds are not explicitly documented in the function.

**Source-established:** The clamp bounds are [0.0, 1.0] (inferred from downstream usage and the `_clamp` implementation). The exact implementation was not read during this audit.

---

## 4. State Representation

### 4.1 Why six-line counts alongside five-axis vectors?

The Hamiltonian combines two different state representations:

1. **Five-axis emotional vector** (chaos, whimsy, darkTone, coherence, voiceWeight): A continuous, normalized [0, 1] representation of the hexagram's emotional state. Produced by `_line_state_vector()` from line ratios.

2. **Six-line counts** (yin_count, yang_count, yao_count, etc.): Discrete integer counts (0–6) of line types in the hexagram's binary/ternary representation. Produced by `_line_state_balance()`.

**Source-established:** The five-axis vector represents the *emotional* state (continuous, normalized). The six-line counts represent the *structural* state (discrete, count-based). The Hamiltonian attempts to combine these two representations into a single scalar.

**Unresolved:** No documentation explains why these two representations should be combined, or what the resulting scalar is supposed to measure. The combination of a continuous vector-space quantity (pq_dot) with a discrete count-space quantity (lagrangian) is the root of the scale incompatibility.

### 4.2 The 5-axis vs. 6-line mismatch

| Property | 5-axis vector | 6-line counts |
|----------|---------------|---------------|
| Representation | Continuous | Discrete |
| Domain | [0, 1] per axis | [0, 6] per count |
| Number of dimensions | 5 | 6 (lines) |
| Source function | `_line_state_vector()` | `_line_state_balance()` |
| Semantic meaning | Emotional state | Structural state |
| Granularity | 727 distinct values (observed) | 7 distinct values (observed) |

**Source-established:** The two representations have different dimensionality (5 vs. 6), different granularity (continuous vs. discrete), and different semantic meaning (emotional vs. structural). Their combination in a single subtraction is not explained by any documented mathematical framework.

---

## 5. Scale Interpretation

### 5.1 Was normalization intended or deliberately omitted?

**Source search:** No documentation, comment, or git commit message mentions normalization, rescaling, or unit conversion between the vector scale (~0.01) and the line-count scale (~1-5).

**Source-established:** Normalization was neither implemented nor documented. The coefficients (0.5, 0.3, 0.2) are applied directly to raw line counts, producing a lagrangian in the 0–5.1 range. No scaling factor converts this to the vector scale (~0.01).

**Unresolved:** Whether normalization was:
- **Deliberately omitted** (the author intended the large lagrangian to dominate, making H always negative, with the clamp as a floor)
- **Accidentally omitted** (the author intended comparable scales but failed to normalize)
- **Not considered** (the author did not analyze the scale relationship)

No evidence distinguishes between these interpretations.

### 5.2 The "convex combination" hypothesis

The coefficients sum to 1.0 (0.5 + 0.3 + 0.2 = 1.0), which is consistent with a convex combination (weights that sum to 1). However:

1. The terms have different ranges (dy ∈ [-6,6], yao_dy ∈ [-3,3], changing_dy ∈ [-6,6]), so the weights do not normalize the output.
2. The `abs()` removes sign, making the "combination" a magnitude sum, not a signed combination.
3. No documentation confirms the convex combination intent.

**Source-established:** The coefficients sum to 1.0. The terms have different ranges. The abs() removes sign.

**Unresolved:** Whether the sum-to-1.0 is intentional (convex combination) or coincidental.

---

## 6. Sign Convention

### 6.1 What does negative raw H represent?

**Source search:** No documentation defines the meaning of negative Hamiltonian energy. The clamp (`max(0, raw)`) converts negative values to 0.0, but no comment or spec explains whether negative values are:
- Meaningful (energy deficit, potential-dominated regime)
- An error (scale bug producing invalid negative energies)
- A design choice (the formula is intended to produce non-negative values, and negative inputs indicate "no energy")

**Source-established:** The clamp floors negative values to 0.0. The raw values are always negative in the tested population (1,536 states). The clamp is one-sided (only floors negatives, does not ceiling positives).

**Unresolved:** The intended meaning of negative raw H. Three interpretations are possible (see dimensional consistency analysis §7.1), and no evidence distinguishes between them.

### 6.2 Sign asymmetry

The ternary paired differential spec (`docs/ternary-paired-differential-math-correction-2026-08-02.md`) defines signed differentials:
- `dy = yang - yin` (signed)
- `old_dy = old_yang - old_yin` (signed)
- `stable_dy = stable_yao - stable_yin` (signed)

However, the Hamiltonian implementation uses `abs()` on all three:
```python
lagrangian = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2
```

**Source-established:** The spec says "signed ternary differentials" and "boolean only at final decision gates." The implementation uses `abs()` which removes sign information. The `hamiltonian-equation-comparison-2026-10-27.md` document (line 100) notes: "The current code uses `abs()` which is a form of magnitude gating — it removes sign information from the differential layer. This violates the spec's requirement that differentials remain signed."

**Unresolved:** Whether the `abs()` is a spec violation (should be removed) or a design choice (magnitude is intended). The spec does not explicitly address whether `abs()` is permitted in the Hamiltonian context.

---

## 7. Model Classification

### 7.1 Classification options

| Classification | Definition | Evidence for | Evidence against |
|----------------|-----------|-------------|-----------------|
| **Physical Hamiltonian** | Implements Hamilton's equations with canonical variables | Name "Hamiltonian energy"; form `p·q̇ - L` resembles Legendre transform | No canonical variables, no time derivative, no Hamilton's equations, no mass matrix, no energy conservation |
| **Heuristic scoring function** | A hand-designed formula that produces a scalar score | Coefficients are tuning weights (sum to 1.0); output is used as "animation intensity" and "energy" in downstream consumers | Name implies more mathematical structure than a heuristic |
| **Analogy/metaphor** | Borrows physics vocabulary to describe a non-physical quantity | Formula is not derived from first principles; no units, no conservation laws | The name and form suggest a specific mathematical structure |
| **Custom scalar calculation** | An ad-hoc formula with Hamiltonian-inspired naming | No documentation of mathematical intent; formula combines unrelated quantities | The name "Hamiltonian" is misleading if the formula is ad-hoc |

### 7.2 Evidence assessment

**Source-established:**
- The formula is used as "animation intensity" (emotional_engine.py:498: `# Hamiltonian energy drives animation intensity`) and as an "energy" scalar in downstream consumers.
- The formula does not implement Hamilton's equations, canonical variables, or energy conservation.
- The coefficients are undocumented tuning weights.
- The formula combines two different state representations (5-axis vectors and 6-line counts) without normalization.

**Unresolved:** The intended classification. The codebase does not state whether the Hamiltonian is meant to be a physical model, a heuristic, an analogy, or a custom scalar. The name "Hamiltonian energy" implies more structure than the implementation provides, but the downstream usage ("animation intensity") suggests a heuristic role.

### 7.3 Field-name collision

**Source-established (R-12):** There are two distinct producers of the `hamiltonian_energy` field:
1. **M3 Hamiltonian** (`emotional_engine.py`): `pq_dot - lagrangian`, clamped to [0, 1]
2. **JKD ingestion scalar** (`ingest_jkd_megatron_wavepackets.py`): `coherence - chaos - 0.5*darkTone + 0.3*voiceWeight - 0.2*whimsy`

These are two different mathematical expressions that produce the same field name. No production code distinguishes between them.

**Unresolved:** Whether this collision is intentional (both are "Hamiltonian energy" in different contexts) or accidental (different authors used the same name for different calculations).

---

## 8. Historical Intent

### 8.1 Documentation search

Searched the following sources for Hamiltonian design rationale:

| Source | Search result |
|--------|--------------|
| `emotional_engine.py` comments | "Hamiltonian energy drives animation intensity" (line 498); "Hamiltonian / Gaussian / Trigram math from parsed wiki sources" (line 392) |
| `docs/ternary-paired-differential-math-correction-2026-08-02.md` | Defines signed differentials; does not define Hamiltonian formula or coefficients |
| `docs/ternary-paired-differential-math-correction-2026-08-02.md` (Boolean gating rule) | "Boolean only at final decision gates, forbidden in math/scoring/phase-rate layers" — relevant to `abs()` usage |
| `docs/hamiltonian-equation-comparison-2026-10-27.md` | Candidate equations and worked cases; no historical derivation of coefficients |
| `docs/formula-design-review-2026-10-27.md` | Axis-level design review (chaos, coherence, voiceWeight); no Hamiltonian coefficient rationale |
| `docs/audit-drift-report-2026-10-27.md` | Notes "King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian" |
| `docs/consumer-repair-specification-2026-10-29.md` | Consumer repair spec; Hamiltonian contract not yet defined |
| Git commit messages | No commit message mentions Hamiltonian coefficient derivation |
| `docs/KING-WEN-RESEARCH-CHECKLIST.md` | J-space renders Hamiltonian panel; no formula derivation |

**Source-established:** The only documentation of Hamiltonian intent is:
1. `emotional_engine.py:498`: "Hamiltonian energy drives animation intensity" — describes downstream usage, not mathematical intent
2. `emotional_engine.py:392`: "Hamiltonian / Gaussian / Trigram math from parsed wiki sources" — describes provenance (parsed wiki sources), not derivation
3. `docs/audit-drift-report-2026-10-27.md:289`: "King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian" — a classification claim, not a derivation

**Unresolved:** No documentation explains:
- Why 0.5, 0.3, and 0.2 were chosen
- Why line counts and vector components are combined
- Whether normalization was intended
- What negative raw H represents
- Whether the formula is a physical model, heuristic, analogy, or custom scalar

### 8.2 The "parsed wiki sources" reference

The comment at `emotional_engine.py:392` references "parsed wiki sources" as the origin of the Hamiltonian math. This suggests the formula may have been derived from wiki-parsed mathematical content (possibly from the J-space/Jacobian lens math document or similar).

**Source-established:** The Hamiltonian math is described as coming from "parsed wiki sources." This is a provenance hint, not a derivation.

**Unresolved:** Which specific wiki source, which specific page/section, and which specific mathematical content was parsed to produce this formula. No traceable reference to the original source has been found.

### 8.3 The Legendre transform claim

The audit-drift-report (line 289) states: "King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian."

**Assessment:** The form `H = p·q̇ - L` does resemble the Legendre transform that converts a Lagrangian L(q, q̇, t) into a Hamiltonian H(q, p, t) = p·q̇ - L(q, q̇, t). However:

1. In classical mechanics, the Legendre transform requires that p_i = ∂L/∂q̇_i (canonical momentum). Here, "momentum" is set to max(0, resolved_vec_i) — not derived from the Lagrangian.
2. The transform also requires that the Lagrangian be a function of (q, q̇, t). Here, the "Lagrangian" is computed from line counts, not from q or q̇.
3. The transform produces a function H(q, p, t) of canonical variables. Here, H is a scalar with no functional dependence on canonical variables.

**Source-established:** The form resembles the Legendre transform. The variables are not canonical.

**Unresolved:** Whether the author intended a Legendre transform (and failed to implement it correctly) or borrowed the form without intending the mathematical structure.

---

## 9. Evidence Trace

### Source code references

| Symbol | File | Lines | Description |
|--------|------|-------|-------------|
| `_hamiltonian_energy` | emotional_engine.py | 408–455 | Hamiltonian calculation (current) |
| `_line_state_balance` | emotional_engine.py | 207–260 | Line count computation |
| `_line_state_vector` | emotional_engine.py | 717–780 | 5-axis vector computation |
| `_quantum_avatar_modulation` | emotional_engine.py | 471–510 | Avatar modulation (calls _hamiltonian_energy with {}) |
| `VEC_KEYS` | emotional_engine.py | 37 | ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"] |
| `hamiltonian_energy` (alias) | emotional_engine.py | (exported) | Public alias for _hamiltonian_energy |
| shotgun_expand call site | full_hexagram_shotgun.py | 682–688 | Calls hamiltonian_energy(resolved_vec, expanded_vec, line_balance) |
| kingwen_state_transition call site | kingwen_state_transition.py | (various) | Calls hamiltonian_energy(resolved_vec, expanded_vec, line_balance) |

### Documentation references

| Document | Relevant content |
|----------|-----------------|
| `docs/ternary-paired-differential-math-correction-2026-08-02.md` | Signed differentials spec; Boolean gating rule; Hamiltonian spec (q̇^i = q_resolved^i - q_expanded^i) |
| `docs/hamiltonian-equation-comparison-2026-10-27.md` | Candidate equations (A–F); worked reference cases; acceptance criteria |
| `docs/formula-design-review-2026-10-27.md` | Axis-level design review (chaos, coherence, voiceWeight); sign sensitivity questions |
| `docs/audit-drift-report-2026-10-27.md` | "King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian" |
| `docs/consumer-repair-specification-2026-10-29.md` | Consumer repair spec; Hamiltonian contract not yet defined; field-name collision (R-12) |
| `docs/controlled-remediation-verification-protocol.md` | R-14 (M3 Hamiltonian energy = 0.0); R-12 (field-name collision) |
| `docs/information-loss-remediation-register.md` | R-14 (M3 Hamiltonian energy = 0.0 for all states) |

### Git history references

| Commit | Message | Relevance |
|--------|---------|-----------|
| `ea89a9cf2d` | Add emotional engine and temporal emotional engine | First appearance of _hamiltonian_energy |
| `ae1aa53b01` | feat: add consensus computation to collapse_full_128 | Hamiltonian in consensus |
| `427521aedb` | Implement dynamic emotional input derivation | Hamiltonian with dynamic input |
| `3c3d073c2d` | Enhance emotional engine with query token support | Hamiltonian in consensus refactor |
| `71fbf28f8e` | Add lua-math-tool.md | Current HEAD |

### Baseline data references

| Artifact | Path | Description |
|----------|------|-------------|
| Raw H distribution | DATASETS/raw_h_distribution_2026-11-02.json | 1,536-state raw H values |
| Remediation matrix | docs/remediation-verification-matrix.md | Entry 3 (Hamiltonian M3) |
| Dimensional analysis | docs/qsmc1-m3-dimensional-consistency-analysis.md | F-10 dimensional analysis |
| Floor/ceiling research | docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md | Categories A–D |
| Equation comparison | docs/hamiltonian-equation-comparison-2026-10-27.md | Candidate equations A–F |

---

## 10. Classification Summary

### Source-established findings

1. The formula `H = max(0, pq_dot - lagrangian)` has been present since the emotional engine's first commit.
2. The coefficients (0.5, 0.3, 0.2) are hardcoded with no documented derivation.
3. The 3.0 midpoint constant is derived from the 6-line hexagram structure (6/2).
4. The clamp bounds are [0.0, 1.0] (inferred from downstream usage).
5. The Hamiltonian is used as "animation intensity" and an "energy" scalar in downstream consumers.
6. The formula combines 5-axis vectors (continuous) with 6-line counts (discrete) without normalization.
7. The `abs()` removes sign information from all three differentials.
8. There are two distinct producers of the `hamiltonian_energy` field (M3 and JKD).
9. The formula does not implement Hamilton's equations, canonical variables, or energy conservation.
10. The code comments describe the Hamiltonian as coming from "parsed wiki sources."

### Historically established findings

1. The Hamiltonian formula has been referenced in 15+ commits since the emotional engine's inception.
2. The argument was corrected from `hamiltonian_energy(vec, vec, ...)` to `hamiltonian_energy(resolved_vec, expanded_vec, ...)` during the ternary paired differential correction.
3. The ternary paired differential spec defines signed differentials but does not explicitly address the Hamiltonian's use of `abs()`.
4. The audit-drift-report classifies `pq_dot - L` as a "canonical Hamiltonian construction (Legendre transform)."
5. The `hamiltonian-equation-comparison-2026-10-27.md` document proposes 6 candidate equations (A–F) for potential remediation.

### Unresolved questions

1. **Origin of coefficients:** Why 0.5, 0.3, and 0.2? No derivation found.
2. **Origin of formula:** Which "parsed wiki source" produced this formula? No traceable reference found.
3. **Normalization intent:** Was normalization deliberately omitted or accidentally omitted?
4. **Sign convention:** What does negative raw H represent? Three interpretations possible.
5. **Model classification:** Is this a physical Hamiltonian, heuristic, analogy, or custom scalar?
6. **Legendre transform claim:** Was the author intending a Legendre transform, or borrowing the form?
7. **Field-name collision:** Is the M3/JKD collision intentional or accidental?
8. **`abs()` in Hamiltonian:** Does the spec's "signed differentials" requirement apply to the Hamiltonian? The spec does not explicitly address this.
9. **Clamp bounds:** Are [0, 1] the intended bounds, or a default? No documentation found.
10. **Ternary integration:** The ternary layer (5,832 states) exists but is not integrated into the Hamiltonian. Is this intended?

---

## 11. Track A — Formula/Documentation Reconciliation

### 11.1 The discrepancy

The `docs/hamiltonian-equation-comparison-2026-10-27.md` document describes a formula that **has never existed in the source code**. The document's formula and the actual implementation differ in four ways:

| Component | October 27 document | Actual source (current) | Actual source (pre-6239ba9bd7) |
|-----------|---------------------|------------------------|-------------------------------|
| Differential treatment | Four differentials (dy, yao_dy, old_dy, stable_dy) | Three terms (dy, yao_dy, changing_dy) | Three terms (yin_ratio-yang_ratio, yao_ratio, changing_ratio) |
| Count scaling | Divides by 6.0 | Raw counts (no division) | Ratios (0-1 scale) |
| Weighting | Equal unit weights (sum) | Coefficients 0.5, 0.3, 0.2 | Coefficients 0.5, 0.3, 0.2 |
| pq_dot | Not specified | `sum(m * qd)` where qd = resolved - expanded | `sum(m * abs(s))` where s = phase_shift |
| Parameters | Not specified | resolved_vector, expanded_vector, line_balance | resolved_vector, line_balance, phase_shift |

**Source-established:** The October 27 document's formula (`abs(dy) + abs(yao_dy) + abs(old_dy) + abs(stable_dy)`) appears in exactly two files: `docs/hamiltonian-equation-comparison-2026-10-27.md` and `docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md`. It does not appear in any source code file, test file, or data file in the repository.

**Source-established:** The actual source formula (`abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2`) appears in `emotional_engine.py` and is used by `full_hexagram_shotgun.py`, `kingwen_state_transition.py`, and `_quantum_avatar_modulation`.

### 11.2 Formula evolution through git history

| Version | Commit | Formula | pq_dot | Parameters |
|---------|--------|---------|--------|------------|
| V1 (earliest) | `780d9c4bfe` | `abs(yin_ratio - yang_ratio) * 0.5 + yao_ratio * 0.3 + changing_ratio * 0.2` | `sum(m * abs(s))` (phase_shift) | resolved_vector, line_balance, phase_shift |
| V2 (current) | `6239ba9bd7` | `abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2` where dy=yang_count-yin_count, yao_dy=yao_count-3.0, changing_dy=changing_count-(6-changing_count) | `sum(m * qd)` where qd=resolved-expanded | resolved_vector, expanded_vector, line_balance |

**Source-established:** The coefficients (0.5, 0.3, 0.2) were present in V1 and carried through to V2 unchanged. The formula structure changed (ratios → raw counts, phase_shift → resolved-expanded) but the coefficients did not.

**Historically established:** The formula evolved from using ratios (0-1 scale) to raw counts (0-6 scale). The coefficients were NOT adjusted for the scale change. This is the root cause of the scale incompatibility: the coefficients were designed for ratio-scale inputs but are now applied to count-scale inputs.

### 11.3 Classification of the October 27 document

The October 27 document describes a formula that:
1. Has never existed in source code
2. Uses four differentials (the source uses three)
3. Divides by 6.0 (the source doesn't)
4. Uses equal weights (the source uses 0.5, 0.3, 0.2)

**Classification:** The October 27 document is a **design intent document** — it describes what the author *believed* the formula should be or *intended* it to be, not what it actually is. It is not an inaccurate account of the implementation (which would imply the author was trying to describe the implementation and got it wrong). It is a separate formulation that was never implemented.

**Unresolved:** Whether the October 27 formula represents:
- An intended future design (the author planned to implement it but didn't)
- A misunderstood current implementation (the author believed the source matched the document)
- A theoretical ideal (the author described what they thought the formula *should* be)

No evidence distinguishes between these interpretations.

### 11.4 Consumers of the actual implementation

| Consumer | File | Uses which version | Depends on |
|----------|------|-------------------|------------|
| full_hexagram_shotgun.py | scripts/full_hexagram_shotgun.py | V2 (current) | `_hamiltonian_energy(resolved_vec, expanded_vec, line_balance)` |
| kingwen_state_transition.py | scripts/kingwen_state_transition.py | V2 (current) | `_hamiltonian_energy(resolved_vec, expanded_vec, line_balance)` |
| _quantum_avatar_modulation | emotional_engine.py:471-510 | V2 (current) | `_hamiltonian_energy(resolved_vector, expanded_vector, {})` — note: empty line_balance |
| verify_restored_state.py | scripts/verify_restored_state.py | V2 (current) | Reads `HAMILTONIAN_PAIRED_DIFFERENTIALS` global (print-only) |

**Source-established:** All consumers use the actual implementation (V2), not the October 27 document's formula. No consumer relies on the four-differential/equal-weight formula.

### 11.5 Documentation/source discrepancy classification

The discrepancy between the October 27 document and the actual source is a **documentation-integrity finding**, not a mathematical finding. It should be tracked as:
- **R-12 adjacent:** Field-name collision (M3 vs. JKD Hamiltonian) — already tracked
- **New finding:** Documentation describes a formula that does not exist in source code
- **Cross-reference:** The October 27 document should be annotated to note that its formula is a design intent, not an implementation description

**Source-established:** The discrepancy is real and verifiable. The October 27 document's formula has never existed in the source code.

---

## 12. Track B — Theoretical Provenance

### 12.1 "Parsed wiki sources" investigation

The code comment at `emotional_engine.py:392` reads: `# Hamiltonian / Gaussian / Trigram math from parsed wiki sources`

**Source search results:**

| Source | Search result |
|--------|--------------|
| `docs/kingwen-superposition-expansion-plan-2026-07-11.md` | Line 98: "Use `wiki_math_corpus.jsonl` Hamiltonian pages as mathematical grounding for: phase-space ranking, energy formulations, path-cost ordering" |
| `docs/kingwen-superposition-expansion-plan-2026-07-11.md` | Line 100: "Use Gaussian beam/function sources from parsed wiki pages to parameterize: smoothing kernel width, phase-continuity weights" |
| `DATASETS/wiki_math_corpus.jsonl` | Searched for Hamiltonian-related content (not read in detail) |

**Source-established:** The "parsed wiki sources" reference is `wiki_math_corpus.jsonl` Hamiltonian pages, used for "phase-space ranking, energy formulations, path-cost ordering." The plan document explicitly states: "No hard-coded Hamiltonian constants unless they come from parsed source math."

**Unresolved:** Whether the constants 0.5, 0.3, 0.2 actually came from parsed wiki sources. The plan document says "No hard-coded Hamiltonian constants unless they come from parsed source math," but no evidence links the specific constants to any parsed source. The plan was written on 2026-07-11; the Hamiltonian was introduced in commit `780d9c4bfe` (date unknown, but after the plan). The plan may have been aspirational (describing intended future work) rather than a record of what was actually done.

### 12.2 Legendre transform classification

The audit-drift-report (line 289) states: "King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian."

**Assessment:** The form `H = p·q̇ - L` resembles the Legendre transform H(q, p, t) = p·q̇ - L(q, q̇, t). However:

1. **Canonical momentum requirement:** In classical mechanics, p_i = ∂L/∂q̇_i. Here, "momentum" is set to max(0, resolved_vec_i) — not derived from the Lagrangian. The resolved vector is an emotional vector, not a generalized momentum.

2. **Lagrangian functional dependence:** The transform requires L to be a function of (q, q̇, t). Here, the "Lagrangian" is computed from line counts, not from q or q̇.

3. **Canonical variables:** The transform produces H(q, p, t) as a function of canonical variables. Here, H is a scalar with no functional dependence on canonical variables.

4. **Energy conservation:** A Hamiltonian conserves energy only if the system is conservative and the Hamiltonian has no explicit time dependence. Here, there is no conservation law — the formula is applied per-state with no time evolution.

**Source-established:** The form resembles the Legendre transform. The variables are not canonical. No conservation law exists.

**Unresolved:** Whether the author intended a Legendre transform (and failed to implement it correctly) or borrowed the form without intending the mathematical structure. The classification as "Legendre transform" is a naming observation, not a derivation.

### 12.3 Coefficient origin investigation

Searched for any reference to 0.5, 0.3, or 0.2 in:
- Code comments in emotional_engine.py
- Documentation files (grep across docs/)
- Git commit messages
- The wiki_math_corpus.jsonl file

**Result:** No documentation, comment, or commit message explains the origin of 0.5, 0.3, or 0.2. The plan document's rule ("No hard-coded Hamiltonian constants unless they come from parsed source math") is aspirational — no evidence links the constants to any parsed source.

**Source-established:** The coefficients are arbitrary tuning weights. Their sum to 1.0 is consistent with a convex combination, but the terms they weight have different scales, making the convex combination interpretation mathematically invalid.

**Unresolved:** The origin and intent of 0.5, 0.3, and 0.2. No derivation found.

### 12.4 Heuristic vs. physical model assessment

| Criterion | Physical Hamiltonian | Heuristic scoring function | Analogy/metaphor | Custom scalar |
|-----------|---------------------|---------------------------|-----------------|---------------|
| Canonical variables | ❌ | N/A | N/A | N/A |
| Hamilton's equations | ❌ | N/A | N/A | N/A |
| Energy conservation | ❌ | N/A | N/A | N/A |
| Documented intent | ❌ | ❌ | ❌ | ❌ |
| Downstream usage | "animation intensity" | Plausible | Plausible | Plausible |
| Coefficients as tuning weights | ❌ (should be derived) | ✅ | ✅ | ✅ |
| Formula from parsed sources | Claimed | Claimed | Claimed | Claimed |

**Assessment:** The formula is most consistent with a **heuristic scoring function** or **custom scalar calculation** with Hamiltonian-inspired naming. The downstream usage ("animation intensity") supports a heuristic role. The coefficients (0.5, 0.3, 0.2) behave as tuning weights. The lack of canonical variables, Hamilton's equations, or conservation laws rules out a physical Hamiltonian.

However, the name "Hamiltonian energy" and the form `p·q̇ - L` imply more mathematical structure than a heuristic provides. This is a naming/interpretation gap, not a mathematical defect.

**Source-established:** The formula is a scalar calculation with Hamiltonian-inspired naming. It does not implement a formal Hamiltonian.

**Unresolved:** Whether the author intended a heuristic, an analogy, or a (failed) formal Hamiltonian. No documentation states the intent.

---

## 13. Disposition

**F-10 Status:** INVESTIGATED (provenance traced). This document provides the formal mathematical provenance and formulation audit requested. The seven questions have been answered to the extent possible from the available evidence:

1. **Formula lineage:** Present since commit 780d9c4bfe (first Hamiltonian version). Core structure (`pq_dot - lagrangian`) has been present since inception. Evolved from ratios+phase_shift to raw counts+resolved-expanded. Coefficients (0.5, 0.3, 0.2) carried through both versions unchanged. October 27 document describes a formula that has NEVER existed in source code — it is a design intent document, not an implementation description.

2. **Coefficient provenance:** Hardcoded, undocumented, no derivation found. Present in V1 and carried to V2 without adjustment for scale change. Sum to 1.0 but applied to different-scale quantities.

3. **State representation:** Two different representations (5-axis continuous vs. 6-line discrete) combined without documented rationale. Different dimensionality, granularity, and semantic meaning.

4. **Scale interpretation:** Normalization neither implemented nor documented. Whether deliberately omitted is unresolved. The scale change from ratios (V1) to raw counts (V2) without coefficient adjustment is the root cause of the scale incompatibility.

5. **Sign convention:** Negative raw H is a mathematical consequence of scale disparity. Intent undocumented. Three interpretations possible.

6. **Model classification:** Scalar calculation with Hamiltonian-inspired naming. Not a formal Hamiltonian. Most consistent with heuristic or custom scalar. Downstream usage ("animation intensity") supports heuristic role.

7. **Historical intent:** Only provenance hint is "parsed wiki sources" (wiki_math_corpus.jsonl Hamiltonian pages). No traceable reference to original source found. Legendre transform classification is a naming observation, not a derivation.

**Track A (Formula/documentation reconciliation):** The October 27 document describes a formula that has never existed in source code. It is a design intent document, not an inaccurate account. All consumers use the actual implementation (V2). The discrepancy is a documentation-integrity finding, not a mathematical finding.

**Track B (Theoretical provenance):** The "parsed wiki sources" reference is wiki_math_corpus.jsonl Hamiltonian pages, used for phase-space ranking, energy formulations, and path-cost ordering. The plan document's rule ("No hard-coded Hamiltonian constants unless they come from parsed source math") is aspirational — no evidence links the constants to any parsed source. The Legendre transform classification is a naming observation, not a derivation. The formula is most consistent with a heuristic or custom scalar.

**No formula changes were made.** The audit is complete. Remediation (if any) requires:
- Establishing the intended mathematical semantics of H
- Tracing the original source of the formula and coefficients (wiki_math_corpus.jsonl)
- Determining whether normalization was intended (V1 used ratios, V2 uses raw counts — coefficients were not adjusted)
- Defining the sign convention
- Classifying the model (physical, heuristic, analogy, or custom)
- Resolving the field-name collision between M3 and JKD Hamiltonians
- Reconciling the October 27 documentation with the actual implementation

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline.

---

*End of mathematical provenance and formulation audit.*

## 14. QuantumLab Provenance Investigation and Exclusion

### 14.1 Investigation scope

This section documents an investigation into whether the QuantumLab project (github.com/Kbro1989/quantum-simulation, forked from rasidi3112/quantum-simulation) served as a provenance source for the King Wen M3 Hamiltonian formula. The investigation was prompted by the user's statement that commits 8c54f3fb–14be7c0 were their additions, and that "some terms and usages of my program ended up in the program at this point which maybe useful to what should had migrated with equal or better integrated usages."

### 14.2 Commit-history boundary (user's contributions)

The user's contributions span nine commits from 8c54f3f to 14be7c0:

| Commit | Message | Scope |
|--------|---------|-------|
| `8c54f3f` | Restore workspace files and prepare for upstream sync | Infrastructure setup |
| `b59a20e` | feat: Extend framework to full 2D/3D — Grid3D, WaveFunction3D, SplitStep3DSolver, Gaussian2D/3DBarrier, plots_2d, ABL 3D, 3D observables, examples 05/06, 25 tests green | 2D/3D grid, wavefunction, solver, barrier, plot, ABL, observable infrastructure |
| `8d9f209` | Merge pull request #1 from Kbro1989/main | PR merge |
| `8250bc4` | docs: update README with 2D/3D features and add simulation gallery images | Documentation |
| `aec5d89` | Merge pull request #1 from rasidi3112/main | PR merge |
| `5ff82af` | feat: add GPU-accelerated 3D Split-Step solver and performance benchmarking tools | GPU solver, benchmarking |
| `44b3d5e` | feat: enhance performance benchmarking with multi-run statistics and correctness validation | Benchmarking validation |
| `9a6d528` | Merge pull request #2 from Kbro1989/main | PR merge |
| `32d8416` | docs: fix README accuracy — parameter name and architecture section | Documentation |
| `5aaab5a` | Merge pull request #2 from rasidi3112/main | PR merge |
| `14be7c0` | Add ALL-FILES.md: 72 files inventory | File inventory |

**Source-established:** The user's contributions are infrastructure-level: 2D/3D grids (`Grid3D`, `WaveFunction3D`), solvers (`SplitStep3DSolver`, GPU-accelerated variant), barriers (Gaussian2D/3D), plots (plots_2d, animation), absorbing boundary layer (ABL 3D), observables (3D observables), performance benchmarking, and documentation.

**Source-established:** No Hamiltonian, King Wen, emotional-engine, or ternary-related terms appear in any of the user's commits. A grep of the full diff (8c54f3f..14be7c0) for `porosity`, `hexagram`, `ternary`, `yao`, `king.?wen`, `shotgun`, `emotion` returned zero matches.

**Source-established:** The user's commits contain no formulas matching the King Wen Hamiltonian coefficients (0.5, 0.3, 0.2) or the `pq_dot - lagrangian` structure.

### 14.3 Hamiltonian implementation ownership and chronology

The Hamiltonian math in QuantumLab was added by **rasidi3112** (Ahmad Rasidi), not by the user:

| Commit | Author | Message | Hamiltonian content |
|--------|--------|---------|---------------------|
| `e85f38b` | rasidi3112 | feat: generic split-operator engine, eigensolvers and Gross-Pitaevskii | `stationary/hamiltonian.py` — spectral application of H (incl. g\|ψ\|²); `stationary/eigensolver.py` — Lanczos/LOBPCG on matrix-free Hamiltonian |
| `18e4085` | rasidi3112 | fix: runner crash on CPU solvers and add 3D observables | 3D observables |
| `04982e1` | rasidi3112 | feat: 3D isosurface renderer with phase colouring and animations | `visualization/volume_3d.py` |
| `eda4be6` | rasidi3112 | feat: 3D showcase examples and validation suite | Examples and validation |

**Source-established:** The QuantumLab Hamiltonian implementation (`stationary/hamiltonian.py`, `stationary/eigensolver.py`) postdates the user's infrastructure contributions. The user's last commit (`14be7c0`, "Add ALL-FILES.md") precedes rasidi3112's Hamiltonian work (`e85f38b`).

**Source-established:** QuantumLab's Hamiltonian uses a **standard split-step Fourier Hamiltonian** (kinetic + potential energy, g\|ψ\|² nonlinearity) — fundamentally different from King Wen's `pq_dot - lagrangian` structure. There is no `pq_dot`, no Lagrangian, no 0.5/0.3/0.2 coefficients, and no line-count-based computation in QuantumLab's Hamiltonian.

### 14.4 3D infrastructure lineage

The user's 2D/3D infrastructure work in QuantumLab provides historical context for subsequent King Wen 3D visualization capabilities:

| QuantumLab infrastructure (user's work) | King Wen 3D usage |
|----------------------------------------|-------------------|
| Grid3D, WaveFunction3D | 3D avatar mesh coordinate systems (`kingwen_mobius_sphere.py`) |
| SplitStep3DSolver, GPU acceleration | Quantum avatar field modulation (animation intensity, color shift, scale factor) |
| plots_2d, animation export | King Wen avatar mesh generation (512 PLY files, 64 hexagrams × 8 phases) |
| ABL 3D (absorbing boundary layer) | Sovereign world topology (boundary conditions in `kingwen_sovereign_world_topology.json`) |
| 3D observables | Quantum wave packet generator (amplitude, phase, coherence metrics) |

**Historically established:** The user's 2D/3D infrastructure work in QuantumLab predates and provides historical context for King Wen's 3D avatar and visualization capabilities. The 3D rendering pipeline (isosurfaces, phase-coloured volumes, animation export) that the user built in QuantumLab later informed King Wen's 3D avatar mesh generation and quantum avatar field modulation.

**Unresolved (qualified):** Whether any code was directly reused between QuantumLab and King Wen. No evidence of direct code migration has been found. The connection appears to be **conceptual and infrastructural** (shared 3D visualization concepts) rather than **code-level** (shared implementations).

### 14.5 Provenance disposition

| Relationship | Finding | Classification |
|-------------|---------|----------------|
| King Wen M3 formula → QuantumLab Hamiltonian implementation | No traceable derivation established | **Ruled out** |
| User's QuantumLab contributions → 2D/3D infrastructure | Supported by identified commit history | **Historically established** |
| QuantumLab 3D infrastructure → King Wen visualization work | Historical technical lineage identified; exact implementation lineage qualified | **Qualified** |
| "Parsed wiki sources" → QuantumLab | Not supported; QuantumLab Hamiltonian postdates user's involvement | **Ruled out** |

**Source-established:** QuantumLab's identified Hamiltonian implementation is **not an established source** for King Wen M3. The Hamiltonian math was added by rasidi3112 after the user's infrastructure contributions ended. The formula structures are fundamentally different (split-step Fourier with kinetic/potential energy vs. pq_dot - lagrangian with emotional vectors and line counts).

**Historically established:** The user's 2D/3D infrastructure work provides historical context for subsequent King Wen 3D visualization capabilities. The 3D rendering pipeline concepts (isosurfaces, phase colouring, animation export) that the user built later informed King Wen's avatar mesh generation and quantum avatar field modulation.

**Unresolved:** The "parsed wiki sources" reference in `emotional_engine.py:392` remains unverified. QuantumLab has been ruled out as a direct source, but the specific wiki source (wiki_math_corpus.jsonl Hamiltonian pages) has not been traced to the formula's coefficients or structure.

### 14.6 Safeguard

This investigation **does not** change the original M3 classification or close F-10. It rules out one candidate source (QuantumLab's Hamiltonian implementation) but does not establish where the coefficients, formula, or intended mathematical interpretation originated. The three-layer finding remains untouched:

1. **Implementation:** A scalar calculation with arbitrary coefficients, no normalization, one-sided clamp
2. **Documentation:** A different formula (never implemented) that describes an intended design
3. **Mathematical interpretation:** Unresolved — no documented intent for the formula's meaning

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline.

---

*End of QuantumLab provenance investigation.*



## 15. Wiki Math Corpus Provenance Investigation and Exclusion

### 15.1 Investigation scope

This section documents an investigation into whether `kingwen_train_data/wiki_math_corpus.jsonl` served as a provenance source for the King Wen M3 Hamiltonian formula. The investigation was prompted by the code comment in `emotional_engine.py:392` referencing "parsed wiki sources" alongside `wiki_math_corpus.jsonl` Hamiltonian pages.

The corpus was examined for:
- Hamiltonian-related entries and their mathematical content
- The presence of coefficients 0.5, 0.3, and 0.2 in Hamiltonian-related entries
- The presence of `pq_dot`, `lagrangian`, or similar formula structures
- The presence of emotional vectors, line counts, or porosity in Hamiltonian-related entries
- The original source URLs and bibliographic references for Hamiltonian entries

### 15.2 Corpus contents

The corpus contains 139 entries. Hamiltonian-related entries:

| Title | Query term | Math node count | Source | Content |
|-------|-----------|-----------------|--------|---------|
| Hamiltonian | Hamiltonian | 0 | wikipedia_action_api | Wikipedia disambiguation page; 1,287 source chars; no math nodes |
| Hamiltonian mechanics | Hamiltonian | 20 | wikipedia_action_api | Standard Wikipedia article on Hamiltonian mechanics; 51,936 source chars; 20 math nodes |
| Hamiltonian path | Hamiltonian | 4 | wikipedia_action_api | Graph theory article on Hamiltonian cycles; 18,836 source chars; 4 math nodes |

Additional corpus entries include Gaussian beam, Gaussian function, Gaussian splatting, RuneScape API versions, and various calculator entries. None of these are Hamiltonian-related.

### 15.3 Hamiltonian mechanics article content

The 20 math nodes from the Hamiltonian mechanics article contain standard theoretical notation:

| Math node | Meaning |
|-----------|---------|
| `\dot q^i` | Time derivative of generalized coordinate |
| `(M, \mathcal L)` | Manifold and Lagrangian |
| `p_i(q, \dot q, t) \stackrel{def}{=} \partial \mathcal L / \partial \dot q^i` | Canonical momentum definition |
| `E_{\mathcal L} = \sum \dot q^i \partial \mathcal L / \partial \dot q^i - \mathcal L` | Energy function |
| `\mathcal H(p, q, t) = \sum p_i \dot q^i - \mathcal L(q, \dot q, t)` | Hamiltonian (Legendre transform of Lagrangian) |
| `\mathcal H(\partial L/\partial \dot q, q, t) = E_{\mathcal L}(q, \dot q, t)` | Hamiltonian as energy function |

**Source-established:** The article provides standard Hamiltonian mechanics vocabulary: phase space coordinates (p, q), Lagrangian \mathcal L, Hamiltonian \mathcal H, canonical momentum p_i, Legendre transform, energy function E_{\mathcal L}. These terms are the likely source of the code's Hamiltonian-inspired naming.

**Source-established:** The article contains NO coefficients 0.5, 0.3, or 0.2 in any Hamiltonian-related context. The coefficients 0.5 (appearing 72 times corpus-wide) and 0.3 (37 times) and 0.2 (22 times) occur in unrelated entries (probabilities, fractions, RuneScape API parameters, etc.), not in Hamiltonian math nodes.

**Source-established:** The article contains NO `pq_dot`, `lagrangian` variable, emotional vector, line count, porosity, or any structure resembling the King Wen M3 formula. The standard Hamiltonian is \mathcal H = \sum p_i \dot q^i - \mathcal L, which has no structural similarity to `pq_dot - lagrangian` where `pq_dot = \sum (momentum_i \times \dot q_i)` with `momentum_i = max(0, resolved_vec_i)` and `lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2`.

**Source-established:** The article contains NO emotional vectors, 5-axis continuous values, 6-line discrete state counts, or any representation matching either of King Wen's two state representations.

### 15.4 Hamiltonian path article content

The Hamiltonian path article is a graph theory article about Hamiltonian cycles in graphs. Its 4 math nodes (`n \geq 3`, `n/2`, `n \geq 3`, `2n-1`) are graph-theoretic. This article is completely unrelated to physics or to King Wen.

### 15.5 Provenance disposition

| Investigation | Disposition |
|---|---|
| Hamiltonian mechanics article | Standard theoretical vocabulary; no M3 formula |
| Hamiltonian path article | Unrelated graph-theory subject |
| Legendre transform | Naming influence, not implemented derivation |
| `pq_dot - lagrangian` | Not found in corpus |
| Coefficients 0.5, 0.3, 0.2 | No source identified in Hamiltonian context |
| Emotional vectors and line-count combination | No source identified |
| Original M3 formula provenance | Unresolved (all identified candidate sources investigated and excluded) |

### 15.6 Three distinctions

**1. Vocabulary provenance (supported):** The wiki_math_corpus.jsonl Hamiltonian mechanics article provides a plausible explanation for the terminology used in the implementation. The code's Hamiltonian-inspired naming (H, pq_dot, lagrangian, Legendre transform classification) is consistent with standard Hamiltonian mechanics vocabulary. This is the most likely source of the code's theoretical framing.

**2. Formula provenance (not established):** The corpus does not establish the origin of the actual calculation. The standard Hamiltonian \mathcal H = \sum p_i \dot q^i - \mathcal L has no structural similarity to King Wen's `pq_dot - lagrangian` with emotional vectors and line-count coefficients. The formula's construction is not traceable to any parsed wiki source.

**3. Coefficient provenance (not established):** The corpus provides no derivation for the three weights (0.5, 0.3, 0.2). While the coefficients appear in the corpus (72, 37, and 22 occurrences respectively), none appear in Hamiltonian-related entries or in any context resembling the King Wen formula. The coefficients remain undocumented and unexplained.

### 15.7 Safeguard

This investigation **does not** change the original M3 classification or close F-10. It rules out the last identified candidate source (wiki_math_corpus.jsonl Hamiltonian pages) but does not establish where the coefficients, formula, or intended mathematical interpretation originated.

The three-layer finding remains untouched:
1. **Implementation:** A scalar calculation with arbitrary coefficients, no normalization, one-sided clamp
2. **Documentation:** A different formula (never implemented) that describes an intended design
3. **Mathematical interpretation:** Unresolved — no documented intent for the formula's meaning

The original M3 formula provenance is **unresolved, with all currently identified candidate sources investigated and excluded.** This is not a claim that no candidate sources exist anywhere — it is a statement that the identified leads (QuantumLab Hamiltonian implementation, wiki_math_corpus.jsonl Hamiltonian pages) have been investigated without establishing a derivation.

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline.

---

*End of wiki math corpus provenance investigation.*

**F-10 Status:** INVESTIGATED (provenance traced). This document provides the formal mathematical provenance and formulation audit requested. The seven questions have been answered to the extent possible from the available evidence:

1. **Formula lineage:** Present since commit 780d9c4bfe (first Hamiltonian version). Core structure (`pq_dot - lagrangian`) has been present since inception. Evolved from ratios+phase_shift to raw counts+resolved-expanded. Coefficients (0.5, 0.3, 0.2) carried through both versions unchanged. October 27 document describes a formula that has NEVER existed in source code — it is a design intent document, not an implementation description.

2. **Coefficient provenance:** Hardcoded, undocumented, no derivation found. Present in V1 and carried to V2 without adjustment for scale change. Sum to 1.0 but applied to different-scale quantities.

3. **State representation:** Two different representations (5-axis continuous vs. 6-line discrete) combined without documented rationale. Different dimensionality, granularity, and semantic meaning.

4. **Scale interpretation:** Normalization neither implemented nor documented. Whether deliberately omitted is unresolved. The scale change from ratios (V1) to raw counts (V2) without coefficient adjustment is the root cause of the scale incompatibility.

5. **Sign convention:** Negative raw H is a mathematical consequence of scale disparity. Intent undocumented. Three interpretations possible.

6. **Model classification:** Scalar calculation with Hamiltonian-inspired naming. Not a formal Hamiltonian. Most consistent with heuristic or custom scalar. Downstream usage ("animation intensity") supports heuristic role.

7. **Historical intent:** Only provenance hint is "parsed wiki sources" (wiki_math_corpus.jsonl Hamiltonian pages). No traceable reference to original source found. Legendre transform classification is a naming observation, not a derivation.

**Track A (Formula/documentation reconciliation):** The October 27 document describes a formula that has never existed in source code. It is a design intent document, not an inaccurate account. All consumers use the actual implementation (V2). The discrepancy is a documentation-integrity finding, not a mathematical finding.

**Track B (Theoretical provenance):** The "parsed wiki sources" reference is wiki_math_corpus.jsonl Hamiltonian pages, used for phase-space ranking, energy formulations, and path-cost ordering. The plan document's rule ("No hard-coded Hamiltonian constants unless they come from parsed source math") is aspirational — no evidence links the constants to any parsed source. The Legendre transform classification is a naming observation, not a derivation. The formula is most consistent with a heuristic or custom scalar.

**No formula changes were made.** The audit is complete. Remediation (if any) requires:
- Establishing the intended mathematical semantics of H
- Tracing the original source of the formula and coefficients (wiki_math_corpus.jsonl)
- Determining whether normalization was intended (V1 used ratios, V2 uses raw counts — coefficients were not adjusted)
- Defining the sign convention
- Classifying the model (physical, heuristic, analogy, or custom)
- Resolving the field-name collision between M3 and JKD Hamiltonians
- Reconciling the October 27 documentation with the actual implementation

**Gate 2 remains OPEN.** The 1,536-state dataset remains the immutable numerical baseline.

---

*End of mathematical provenance and formulation audit.*
