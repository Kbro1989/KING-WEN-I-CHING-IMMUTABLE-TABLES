# QSMC-1 M3 Floor, Ceiling, and Extremum Attainment Research

## Purpose

Read-only research document examining whether the King Wen M3 Hamiltonian zero output represents an artificial computational floor, an unattainable supremum, a numerical optimizer failure, or a genuine mathematical property. This document links to findings F-10 and F-12 from the remediation verification matrix without modifying either finding or the frozen QSMC-1 baseline.

## Non-negotiable constraints

- No source modifications authorized by this document.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.

## 1. Observed M3 state

### Computed values (1,536-state population)

| Metric | Value | Assessment |
|--------|-------|------------|
| Total states tested | 1,536 | Full population (64 hex × 8 phases × 3 inputs) |
| States with H == 0.0 | 1,536 (100%) | UNCHANGED from pre-fix |
| States with H != 0.0 | 0 (0%) | No improvement |
| avg_hamiltonian_energy | 0.0 | Still zero |
| min_hamiltonian_energy | 0.0 | Still zero |
| max_hamiltonian_energy | 0.0 | Still zero |

### Dimensional analysis (hex 1, phase 0)

| Component | Value | Scale | Source |
|-----------|-------|-------|--------|
| pq_dot (Σ momentum × q̇) | 0.00947 | ~0.01 | Vector axes 0-1, differences ~0.01-0.05 |
| lagrangian (abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2) | 5.1 | ~1-5 | Line counts 0-6, scaled by 0.5/0.3/0.2 |
| raw H (no clamp) | -5.0905 | Negative | pq_dot - lagrangian |
| clamped H | 0.0 | Floors to 0.0 | _clamp(pq_dot - lagrangian, 0.0, 1.0) |

### Related findings

| Finding | Location | Severity | Status |
|---------|----------|----------|--------|
| F-09 | full_hexagram_shotgun.py:678-683 | Low (resolved) | q̇ degeneracy fixed (resolved vs expanded vectors) |
| F-10 | emotional_engine.py:408-450 | High | Semantic and scale incompatibility (dimensional compatibility established; semantic compatibility not established) |
| F-11 | downstream consumers | High | M6 imaginary amplitude remains zero (consequence of F-10) |
| F-12 | emotional_engine.py:450 | Medium | _clamp is one-sided (negative H floored to 0.0) |

## 2. Four distinct categories

The literature supports separating four conditions that can produce similar observed behavior. These must not be conflated.

### Category A: Artificial floor (computational clipping)

**Definition:** A model's output is artificially constrained by a computational mechanism (clamp, clip, saturation) that prevents it from expressing values outside a prescribed range. The floor is a property of the implementation, not the mathematical system.

**Evidence in King Wen:**
- `_clamp(pq_dot - lagrangian)` with default bounds 0.0-1.0 floors all negative values to 0.0.
- 1,536 distinct raw H values (all negative, ranging from approximately -5.1 to -0.1) collapse to a single observed value (0.0).
- The raw values preserve magnitude and differences; the observed values do not.

**Literature support:**
- Elkelesh et al. (2017): Clipping log-likelihood ratios in belief-propagation decoders produced error-floor behavior. More restrictive clipping made the floor more pronounced. The floor was a property of the decoder implementation, not the underlying code.
- Teshima et al. (2018): Clipping removes information about values beyond a threshold. Multiple original values map to the same bounded observation. Recovery requires methods specifically designed for clipped observations.

**Assessment:** The one-sided clamp is an artificial floor. It is a computational restriction, not a mathematical property of the Hamiltonian. The underlying mathematical system permits negative H values.

### Category B: Artificial ceiling (computational saturation)

**Definition:** A model's output is artificially capped at an upper bound by a computational mechanism. Values exceeding the bound are compressed to the bound.

**Evidence in King Wen:**
- `_clamp` also imposes an upper bound of 1.0. If raw H exceeded 1.0, it would be compressed to 1.0.
- Currently, no raw H exceeds 1.0 (all are negative), so the ceiling is not currently active.
- However, if the dimensional mismatch were resolved (e.g., by rescaling), raw H could potentially exceed 1.0, activating the ceiling.

**Assessment:** The upper clamp is a latent artificial ceiling. It is not currently active but would become relevant if the scale mismatch is addressed.

### Category C: Unattainable supremum (theoretical limit)

**Definition:** A mathematical objective has a finite supremum that is not attained by any feasible point in the state space. The supremum exists as a theoretical limit but is never realized.

**Evidence in King Wen:**
- The Hamiltonian objective is ℋ(p,q,t) = Σ p_i · q̇^i - ℒ.
- The state space is 512 resolved states (64 hexagrams × 8 phases).
- Whether the maximum of ℋ over this state space is attained or merely a supremum requires analysis of the state space (compactness, continuity, feasibility).

**Literature support:**
- Litvinov (2026): A supremum can be finite but unattained when a sequence approaches the bound without ever realizing it. The attainable region must be characterized separately from its closed convex envelope.
- Nguyen (2026): Strict primal feasibility, zero duality gap, and dual attainment can coexist with failure of primal attainment. Optimizing states can escape toward infinity as a boundary value is approached.
- Wolfram MaxValue documentation: The returned value can be a supremum that is not attained by any variable assignment.
- Wolfram Constrained Optimization: If a function is continuous and its feasible domain is nonempty, closed, and bounded (compact), then a global minimum is attained. Without these conditions, attainment is not guaranteed.

**Assessment:** Whether the King Wen Hamiltonian has an attainable maximum or merely a supremum has NOT been determined. The state space (512 discrete states) is finite and bounded, which suggests compactness holds for the discrete case. However, the objective function's continuity over this discrete space has not been verified. This requires further investigation.

### Category D: Numerical optimizer failure

**Definition:** A numerical optimization method fails to find a global optimum that mathematically exists. The optimizer's failure is a computational limitation, not a mathematical property.

**Evidence in King Wen:**
- The current implementation does not perform optimization — it computes H for each state and takes the clamp.
- There is no optimizer in the current pipeline. The "maximum" is simply the maximum of the computed values.
- Therefore, Category D does not currently apply. It would become relevant only if an optimization step were added.

**Assessment:** Not applicable to current implementation. Relevant only if future work adds optimization.

## 3. Dimensional consistency analysis

### Term scales

| Term | Formula | Scale | Basis |
|------|---------|-------|-------|
| pq_dot | Σ max(0, resolved_i) × (resolved_i - expanded_i) | ~0.01 | Vector axes 0-1, differences ~0.01-0.05 |
| lagrangian | abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2 | ~1-5 | Line counts 0-6, scaled by 0.5/0.3/0.2 |
| raw H | pq_dot - lagrangian | ~-5 to -0.1 | Always negative |
| clamped H | max(0, raw H) | 0.0 | Floors all values |

### Dimensional interpretation

The lagrangian terms (dy, yao_dy, changing_dy) are counts of lines in a 6-line hexagram. They range 0-6. The pq_dot term is a product of 0-1 vector axes. There is no documented unit conversion between these scales.

**Question:** Is the lagrangian intended to be on the same scale as pq_dot, or is it intentionally larger to dominate the Hamiltonian?

**Current behavior:** The lagrangian dominates pq_dot by 2-3 orders of magnitude. The Hamiltonian is effectively always negative.

**Implication:** Even if the clamp were removed (making H signed), the H values would be approximately -5.1 to -0.1 for all states. The variation would be preserved (different states would have different H values), but all would be negative.

### Recommended diagnostic: raw value distribution

Before any remediation, measure:
1. Number of distinct raw H values (pre-clamp) across all 1,536 states.
2. Whether raw H values are all identical (suggesting a different problem) or vary (suggesting the clamp is the sole issue).
3. Whether the variation in raw H correlates with any meaningful state property (hexagram ID, phase, emotional input).

This diagnostic has NOT been run. It is the next logical step.

## 4. Verification procedure

Six tests, in order of priority:

| Test | Investigation | What it establishes |
|------|--------------|---------------------|
| 1. Raw-output distribution | Examine every pre-clamp H value | Whether the floor masks a range of negative values |
| 2. Bound analysis | Identify every lower/upper restriction in the formula and consumers | Whether the floor or ceiling is explicit or implicit |
| 3. Dimensional consistency | Establish units and scaling of each contributing term | Whether the objective is mathematically comparable |
| 4. Feasible-state analysis | Define the full state space and its constraints | Whether expected extrema are reachable |
| 5. Attainment analysis | Determine maximum versus supremum | Whether the theoretical extreme is achievable |
| 6. Numerical reproducibility | Compare exact/symbolic and numerical calculations where possible | Whether a result is mathematical or computational |

### Additional diagnostic: value collapse measurement

Measure the number of distinct raw values that collapse to each observed value. If 1,536 distinct raw values become 1,536 zeros, the output has lost all variation. If the raw values are themselves identical, that suggests a different problem (e.g., all inputs produce the same output).



## 5. Research sources

| Source | Primary contribution | Relevance |
|--------|---------------------|-----------|
| Elkelesh et al. (2017) — arXiv:1711.05572 | Clipping-induced error floors | Artificial computational floors |
| Teshima et al. (2018) — arXiv:1809.04997 | Recovery from clipped observations | Information loss |
| Litvinov (2026) — arXiv:2608.18999 | Sharp bias-energy bounds and unattainable suprema | Expected extrema and clipping |
| Nguyen (2026) — arXiv:2608.10341 | Attainment boundaries and escape rates | Unreachable extrema |
| Wolfram — MaxValue | Supremum versus attained maximum | Formal extremum testing |
| Wolfram — Constrained Optimization | Compactness and existence | Feasible-state analysis |
| Wolfram — Exact Global Optimization | Symbolic global extrema | Exact verification |

## 6. Conclusion

The M3 zero output has at least two independent causes:
1. **Artificial floor (Category A):** The one-sided `_clamp()` floors all negative H values to 0.0. This is a computational restriction, not a mathematical property.
2. **Dimensional mismatch (F-10):** pq_dot (~0.01) and lagrangian (~1-5) operate on different scales. The subtraction is always negative regardless of inputs.

The argument fix (F-09) addressed q̇ degeneracy but did not resolve either cause. H remains 0.0 for all 1,536 states.

The next useful artifact is the raw-value distribution diagnostic (Test 1), which has been run. It established that 727 distinct raw H values exist (all negative, -5.09 to -0.56) and are destroyed by the clamp into a single 0.0.

This document does not authorize any source changes. F-10, F-11, and F-12 remain unresolved findings. Gate 2 remains OPEN. The QSMC-1 baseline remains frozen.

## 7. Refinements from first external assessment (2026-11-02)

### F-10 and F-12 separation

Two findings must be kept explicitly distinct:

| Finding | Role | Status |
|---------|------|--------|
| F-10: Dimensional mismatch | Produces scale imbalance and contributes to negative raw results | Unresolved |
| F-12: One-sided clamp | Erases all negative raw values and their differences | Confirmed information-loss mechanism |

These are independent questions:
- Even if raw H is mathematically supposed to be negative, the clamp still destroys information.
- Removing the clamp would preserve negative values but would not establish that the formula is dimensionally valid.

### Refined conclusions

**A. Dimensional mismatch causes all-negative H**
The observed data strongly supports Lagrangian dominance numerically. However, a magnitude comparison alone does not prove dimensional incompatibility or establish causation. That requires intended units and mathematical definitions of both terms.

Suggested disposition: The observed scale disparity is consistent with Lagrangian dominance and explains the negative raw values under the implemented subtraction. Dimensional incompatibility remains a mathematical finding requiring formal unit analysis.

**B. Category C is not the issue**
Correct in the narrower sense that an unattainable supremum is unnecessary to explain the observed collapse. But the 1,536-state experiment does not establish whether a global theoretical supremum exists or is attainable over the entire feasible state space.

Suggested disposition: Unattainable supremum is not required to explain the observed zero-output condition. Global extremum attainment remains outside the scope of this experiment.

**C. Emotional input has minimal effect**
Nearly identical minima and maxima do not establish that emotional input has no significant effect. The reported mean difference of approximately 0.04 is evidence of some sensitivity.

Suggested disposition: Emotional input has a comparatively small observed effect on the raw Hamiltonian over the tested settings. Statistical significance and intended sensitivity remain unestablished.

Similarly, phase variation is descriptive evidence. The word "significant" should be reserved for a documented statistical test if that is what was performed.

### Structural observation: two kinds of variation

The Hamiltonian calculation combines two structurally different contributions:

| Component | Distinct values | Driver |
|-----------|----------------|--------|
| Lagrangian | 7 | Line counts (discrete: 0-6) |
| pq_dot | 727 | State-dependent vector differences (continuous-ish) |
| Raw H | 727 | Dominated by pq_dot variation |
| Clamped H | 1 | All negative values floored to 0.0 |

The clamp removes all distinctions from both contributions. This structural feature may explain why phase has more influence than emotional input: phase affects line counts (lagrangian) which are coarse but dominant, while emotional input affects vector axes (pq_dot) which are granular but subdominant.

Follow-up questions:
1. Do the seven Lagrangian values correspond to seven actual structural classes?
2. Are the 727 pq_dot values reproducible across independent runs?

### Population composition clarification

The 1,536 states represent one combined population across three emotional-input settings:
- 512 states per setting (64 hexagrams × 8 phases)
- 3 settings: emotional_input = 0, 50, 100
- Total: 1,536 = 512 × 3

This affects how distributions and comparisons should be interpreted. The "distinct" counts (727, 511 per setting) reflect the combined population, not per-setting populations.

### Recommended additions to evidence record

| Test | Purpose | Status |
|------|---------|--------|
| Raw H histogram | Establish distribution shape, not just min/max | Not run |
| Raw H by phase | Verify phase-dependent variation | Partial (phase means reported) |
| Raw H by emotional input | Quantify slider sensitivity | Partial (min/max/mean reported) |
| Lagrangian by line-count configuration | Confirm seven-value structural grouping | Not run |
| pq_dot by resolved state | Verify granular state dependence | Partial (distinct count reported) |
| Clamp collision analysis | Identify which distinct raw values map to each observed value | Not run (all map to 0.0) |
| Independent reproduction | Confirm identical results across runs | Not run |

### Updated disposition

| Item | Updated assessment |
|------|-------------------|
| F-09 — q̇ degeneracy | Resolved |
| F-10 — Dimensional mismatch | Open (scale disparity consistent with Lagrangian dominance; formal unit analysis needed) |
| F-11 — M6 imaginary amplitude | Open; upstream dependency implicated |
| F-12 — One-sided clamp | Confirmed information-loss mechanism |
| Category A — Artificial floor | Confirmed |
| Category C — Unattainable supremum | Not needed to explain observed collapse; global extremum attainment remains outside scope |
| Entry 3 | INCONCLUSIVE |

### Next question

The next important question is no longer whether the floor destroys information — the results demonstrate that it does. The next question is whether the underlying Hamiltonian's sign and scale are mathematically intended. That is where the dimensional analysis needs to go next.

| Source | Primary contribution | Relevance |
|--------|---------------------|-----------|
| Elkelesh et al. (2017) — arXiv:1711.05572 | Clipping-induced error floors | Artificial computational floors |
| Teshima et al. (2018) — arXiv:1809.04997 | Recovery from clipped observations | Information loss |
| Litvinov (2026) — arXiv:2608.18999 | Sharp bias-energy bounds and unattainable suprema | Expected extrema and clipping |
| Nguyen (2026) — arXiv:2608.10341 | Attainment boundaries and escape rates | Unreachable extrema |
| Wolfram — MaxValue | Supremum versus attained maximum | Formal extremum testing |
| Wolfram — Constrained Optimization | Compactness and existence | Feasible-state analysis |
| Wolfram — Exact Global Optimization | Symbolic global extrema | Exact verification |

## 8. Refinements from second external assessment (2026-11-02)

### Variation vs magnitude/sign distinction

Two statements that are compatible but must not be conflated:

- **Variation:** `pq_dot` contributes fine-grained state-to-state differentiation (727 distinct values). The Lagrangian has only 7 distinct values but determines the overall scale.
- **Magnitude and sign:** The Lagrangian dominates the raw Hamiltonian's magnitude and sign because it is approximately 1-5 while `pq_dot` is approximately 0.01.

A term can determine the number of distinct outputs without determining their overall scale.

The more precise interpretation:

> `pq_dot` contributes much of the observed state-to-state differentiation, while the Lagrangian dominates the raw Hamiltonian's magnitude and sign.

### Dimensional consistency investigation (F-10)

This is a mathematical investigation, NOT authorization to modify the formula. It is separate from the remediation matrix.

| Question | Required evidence |
|----------|-------------------|
| What are the units of each vector component? | Source definitions and construction lineage |
| What are the units of the resolved/expanded vector differences? | Vector-generation formulas |
| What are the units of `pq_dot`? | Complete calculation and dimensional derivation |
| What are the units of each Lagrangian contribution? | Individual terms and coefficients |
| Are the coefficients dimensionless or dimensional? | Their definitions and intended interpretation |
| Are both terms expressed in compatible units? | Formal dimensional comparison |
| Is subtraction mathematically justified? | Derivation of the implemented Hamiltonian |

Critical caveat: Numerical scale disparity is not itself proof of dimensional incompatibility. Two quantities can have the same units but very different magnitudes. Conversely, two quantities can have similar numerical magnitudes but incompatible dimensions. We need the actual definitions and units to distinguish those cases.

### Phase vs emotional input isolation

The test population has a useful factorial structure: 64 hexagrams × 8 phases × 3 emotional inputs.

This allows separate examination of:
- Phase effects while holding emotional input constant.
- Emotional-input effects while holding phase constant.
- Hexagram-specific interactions.
- Whether phase effects operate through line counts, vector differences, or both.

This could establish whether the observed phase sensitivity is genuinely attributable to the Lagrangian contribution rather than merely correlated with it.

The current explanation (phase affects line counts → lagrangian → dominant) is plausible but should be preserved as a hypothesis until the effects are isolated.

### Updated research disposition

| Finding | Status |
|---------|--------|
| Raw H variation | Established |
| Artificial floor | Confirmed |
| Information loss from clamp | Confirmed |
| q̇ degeneracy | Resolved |
| Lagrangian scale dominance | Strongly supported |
| Formal dimensional compatibility | Unresolved |
| Intended Hamiltonian sign | Unresolved |
| M6 downstream consequence | Still under investigation |
| Entry 3 | INCONCLUSIVE |

### Recommendation

Make the next artifact a formal F-10 dimensional analysis, tracing every term backward to its source definition. Preserve the existing 1,536-state dataset as the numerical baseline. Do not rescale, normalize, remove the clamp, or alter the Hamiltonian during that investigation.

The central question has now narrowed considerably: not whether the calculation contains information, but whether the mathematical operations combining that information are dimensionally and semantically justified.

The M3 zero output has at least two independent causes:
1. **Artificial floor (Category A):** The one-sided `_clamp()` floors all negative H values to 0.0. This is a computational restriction, not a mathematical property.
2. **Dimensional mismatch (F-10):** pq_dot (~0.01) and lagrangian (~1-5) operate on different scales. The subtraction is always negative regardless of inputs.

The argument fix (F-09) addressed q̇ degeneracy but did not resolve either cause. H remains 0.0 for all 1,536 states.

The next useful artifact is the raw-value distribution diagnostic (Test 1), which has not been run. It would establish whether the 1,536 raw H values vary (confirming the clamp is the sole information-loss mechanism) or are identical (suggesting a deeper problem).

This document does not authorize any source changes. F-10, F-11, and F-12 remain unresolved findings. Gate 2 remains OPEN. The QSMC-1 baseline remains frozen.
## 9. Refinements from third external assessment (2026-11-02)

### Three distinctions to preserve

#### 1. Numerical dominance is established; dimensional incompatibility is not yet proven

The evidence establishes:
- `pq_dot` is approximately 0.01.
- The Lagrangian is approximately 1-5.
- The Lagrangian dominates the numerical magnitude and sign of the subtraction.

However, formal dimensional incompatibility requires identifying the units of both terms. Different magnitudes alone do not prove different dimensions.

F-10 should be phrased as:
> Observed scale disparity and suspected dimensional incompatibility; formal unit derivation pending.

#### 2. Distinct-value contribution is different from magnitude contribution

The structural finding must remain explicit:
- The Lagrangian contributes seven discrete values and dominates magnitude and sign.
- `pq_dot` contributes much finer state-dependent variation.
- The raw Hamiltonian retains 727 distinct values.
- The clamp eliminates all observed variation.

The term responsible for most of the output variation is not necessarily the term controlling its overall magnitude.

#### 3. Statistical significance needs a defined test

The phase and emotional-input comparisons establish observed differences. Unless formal statistical tests were performed, use observed phase dependence and limited observed emotional-input sensitivity, rather than claiming statistical significance.

### Proposed scope for F-10 dimensional analysis

Suggested artifact: `docs/qsmc1-m3-dimensional-consistency-analysis.md`

Organize around this trace:

| Section | Required evidence |
|---------|-------------------|
| Source definitions | Where each input and coefficient originates |
| Vector construction | Resolved vectors, expanded vectors, axes, differences |
| `pq_dot` derivation | Units, coefficients, mathematical interpretation |
| Lagrangian derivation | Individual terms, weights, scaling, units |
| Hamiltonian construction | Whether subtraction is dimensionally justified |
| Sign and scale interpretation | Whether negative raw values are mathematically expected |

The investigation should answer four questions:
1. Are the two terms dimensionally compatible?
2. Are their coefficients dimensionless or unit-bearing?
3. Is the negative sign an intended mathematical outcome?
4. Does the implementation represent the intended Hamiltonian, or merely a similarly named scalar calculation?

No formula changes, rescaling, normalization, or clamp modifications should occur during this investigation.

The strongest part of the current evidence is that it has separated the computational information-loss problem from the underlying mathematical validity question. Those should remain separate until both have independent evidence.
