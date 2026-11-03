# Quantum-Sim Mathematical Correspondence Audit

**Research Gate:** QSMC-1
**Status:** PROPOSED -- NOT YET VERIFIED
**Scope:** Read-only mathematical correspondence investigation
**Source baseline:** King Wen <-> Quantum-Sim cross-reference, 184 shared terms
**Authority:** Research framework only; no canonical mappings established

---

## 1. Purpose

Determine whether mathematical structures implemented in the King Wen system have demonstrable correspondences with mathematical structures implemented in Quantum-Sim.

The investigation distinguishes shared vocabulary from shared concepts and from mathematically validated equivalence.

The objective is not to make either system conform to the other. Both systems retain their existing identities, definitions, domains, and implementation boundaries.

## 2. Evidence Levels

Every proposed correspondence must be evaluated across three independent evidence levels.

### E1 -- Lexical overlap

The same term, identifier, or recognizable variation appears in both codebases.

Examples:

- `hamiltonian`
- `phase`
- `gaussian`
- `momentum`
- `expectation`

Lexical overlap establishes only that terminology is shared. It does not establish that the terms have equivalent meanings or implementations.

### E2 -- Conceptual correspondence

The implementations use related concepts or describe related phenomena, but mathematical equivalence has not been established.

Examples:

- King Wen's discrete phase classification and Quantum-Sim's continuous wavefunction phase.
- King Wen's 512-state arithmetic consensus and Quantum-Sim's expectation values.
- King Wen's Gaussian-weighted phase projection and Quantum-Sim's Gaussian wave packets.

Conceptual correspondence requires examination of definitions, purpose, and operational behavior.

### E3 -- Mathematical correspondence

The mathematical objects or operations have a demonstrable mapping.

Required evidence may include:

- Formal definitions.
- Mathematical types and domains.
- Input and output spaces.
- Units and dimensional consistency.
- Operator or transformation definitions.
- Parameterization and normalization.
- Invariants and boundary conditions.
- Reproducible numerical or symbolic validation.

A mathematical correspondence must be demonstrated, not inferred from terminology or conceptual resemblance.

## 3. Disposition System

Every investigated relationship receives one of four dispositions.

| Disposition    | Definition                                                                                     |
| -------------- | ---------------------------------------------------------------------------------------------- |
| `defined`      | A mathematical correspondence has been demonstrated within a specified scope.                    |
| `partial`      | A limited correspondence exists, but important components, assumptions, or domains do not map.  |
| `incompatible` | The investigated mathematical definitions or constraints conflict.                             |
| `undetermined` | Available evidence is insufficient to establish or reject a correspondence.                     |

A disposition is independent of investigation depth. An `undetermined` result does not mean the relationship is impossible. A `partial` result must identify exactly what does and does not correspond.

## 4. Audit Organization: Mathematical Objects

The investigation is organized around mathematical objects and operations rather than a list of shared words.

### M1 -- Gaussian kernels

**King Wen**

- `_project_gaussian_future()` in `emotional_engine.py`
- Gaussian-weighted phase bias
- Reported FWHM: 2.5

**Quantum-Sim**

- Gaussian barriers (`potentials/barriers.py`)
- Gaussian wave packets (`WaveFunction1D.gaussian()`)

**Required examination**

- Exact kernel definitions.
- Width and parameter conventions.
- FWHM-to-standard-deviation relationship.
- Normalization.
- Input domain and dimensionality.
- Whether the same mathematical kernel is implemented.

**Initial disposition:** `undetermined`

### M2 -- Expectation and consensus

**King Wen**

- `_compute_consensus_from_resolved()` in `emotional_engine.py`
- Arithmetic mean across 512 expanded states.

**Quantum-Sim**

- Position, momentum, and energy expectation values (`observables/expectation.py`)

**Required examination**

- Weighting measure.
- Normalization.
- Observable definition.
- State representation.
- Probability interpretation.
- Whether the 512-state mean is uniform, weighted, or otherwise constrained.

An arithmetic mean is not automatically a quantum expectation value.

**Initial disposition:** `partial` at the conceptual level; mathematical correspondence remains `undetermined`.

### M3 -- Hamiltonian and energy

**King Wen**

- `_hamiltonian_energy()` in `emotional_engine.py` (line 408)
- Paired differentials.
- `pq_dot` and Lagrangian comparison.
- Known: produces 0.0 for all 512 states (scale mismatch + empty line_balance)

**Quantum-Sim**

- `Hamiltonian` class (`stationary/hamiltonian.py`)
- Spectral application of H.
- Kinetic and potential energy terms.

**Required examination**

- State space.
- Operator definition.
- Energy functional.
- Operator domain.
- Units and dimensional consistency.
- Boundary conditions.
- Hermiticity or self-adjointness, where applicable.
- Numerical invariants and validation.

**Known implementation finding:** Prior King Wen testing reported zero energy across 512 phase states because of the scale relationship between `pq_dot` and the Lagrangian followed by clamping. Preserve this finding as implementation evidence. Do not assume that it establishes equivalence or incompatibility with Quantum-Sim.

**Initial disposition:** `undetermined`

### M4 -- Phase representations

**King Wen**

- Three-bit `phase_bits` values, 0-7.
- Temporal labels: past, present, future.
- `PHASE_INFO[0]["temporal"] = "past"`

**Quantum-Sim**

- Continuous phase, `arg(psi)`, of a complex wavefunction.

**Required examination**

- Discrete versus continuous domains.
- State representation.
- Phase periodicity.
- Mapping function, if one exists.
- Information lost or introduced by any transformation.
- Whether temporal labels have a defined mathematical relationship to wavefunction phase.

**Initial disposition:** `partial` at the conceptual level; mathematical mapping `undetermined`.

### M5 -- Angular momentum and vortex quantities

**King Wen**

- Schauberger-related parsing (`schauberger_parsing_layers.py`).
- `vortex_strength`.
- `angular_momentum`.

**Quantum-Sim**

- Angular momentum expectation values such as `<L_z>` (`observables/current.py`).
- Vortex detection and vortex lattices.

**Required examination**

- Coordinate systems.
- Momentum definitions.
- Velocity fields.
- Circulation and vorticity, where applicable.
- Angular-momentum operator.
- Units and dimensional consistency.
- Whether King Wen quantities represent physical observables or descriptive metrics.

**Initial disposition:** `undetermined`

### M6 -- Interference and coherence

**King Wen**

- Interference in domain routing.
- Five-axis emotional vector including `coherence` (correlates 0.968 with voiceWeight).

**Quantum-Sim**

- Wavefunction overlap.
- Double-slit interference.
- Complex amplitudes and probability density.

**Required examination**

- Whether superposition is implemented.
- Whether amplitudes are complex-valued.
- Whether interference is constructive/destructive wave interference or a routing-overlap operation.
- Coherence definition and measurement.
- Whether any correlation or overlap quantity has a shared formal definition.

**Initial disposition:** `undetermined`

### M7 -- Evolution and propagation

**King Wen**

- Discrete phase transitions.
- Temporal phase.
- State evolution and next-state selection.

**Quantum-Sim**

- Time evolution.
- Split-step propagation (`SplitStep1DSolver.step()`).
- Wavefunction evolution.

**Required examination**

- State-transition definitions.
- Evolution operator.
- Time parameter and units.
- Reversibility or irreversibility.
- Conservation properties.
- Whether either system defines a transformation corresponding to the other's evolution operator.

**Initial disposition:** `undetermined`

## 5. Source Cross-Reference Corrections

The original 184-term cross-reference remains a discovery artifact. The following seven inconsistencies must be qualified in any derivative analysis.

| Term        | Identified issue                                                                                                                   | Required treatment                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `vortex`    | Listed as shared in the main table but also listed as unique to Quantum-Sim.                                                       | Distinguish King Wen's parsing terminology from Quantum-Sim's implemented vortex quantities.                   |
| `amplitude` | Listed as shared and later as unique to Quantum-Sim.                                                                               | Reinspect exact occurrences and definitions before assigning overlap.                                         |
| `grid`      | Listed as shared infrastructure but also described as unused on the King Wen side.                                                 | Distinguish a hexagram/state grid from spatial discretization.                                                |
| `coherence` | Described as lacking a named Quantum-Sim equivalent, then associated with wavefunction overlap.                                    | Require a direct implementation-level definition before treating them as corresponding quantities.            |
| `entropy`   | Listed as absent from both systems.                                                                                                | Exclude from meaningful shared-concept counts unless new evidence establishes usage.                          |
| `matrix`    | King Wen is described as not using matrices despite nearby MathLawRegistry operator references.                                    | Inspect actual mathematical representation; do not infer matrix operations from generic operator terminology. |
| `quantum`   | The conclusion calls both uses quantum mechanics, but the evidence presented establishes terminology, not a common quantum-mechanical model. | Separate quantum terminology, quantum-inspired modeling, and actual quantum-mechanical implementation.        |

These corrections qualify the source report; they do not authorize changing either codebase.

## 6. Required Evidence Record

Each proposed correspondence must have an individual evidence record.

Required fields:

- `correspondence_id`
- `mathematical_object`
- `kingwen_source`
- `quantum_sim_source`
- `kingwen_definition`
- `quantum_sim_definition`
- `evidence_level`
- `mathematical_type`
- `domain`
- `codomain`
- `units`
- `parameters`
- `transformation`
- `normalization`
- `invariants`
- `validation_method`
- `validation_result`
- `disposition`
- `known_limitations`
- `unresolved_questions`
- `source_revision`
- `evidence_provenance`

No field should be populated with an inferred implementation detail presented as a verified fact. Unknown values remain explicitly unknown.

## 7. Investigation Rules

1. Read-only inspection by default.
2. Preserve source revisions and file provenance.
3. Do not rename or normalize mathematical objects to manufacture equivalence.
4. Do not equate identical variable names with identical mathematical types.
5. Do not treat a shared formula name as proof of a shared implementation.
6. Preserve incompatible and unresolved representations independently.
7. Separate mathematical validity from implementation correctness.
8. Do not change either system's behavior to make a proposed mapping pass.
9. Record negative findings and failed correspondence tests.
10. Do not promote a research correspondence to canonical system authority.

## 8. Completion Criteria

The research gate may be closed only when:

- Each of the seven mathematical-object groups has been investigated or explicitly marked not investigated.
- Each proposed relationship has an evidence level and disposition.
- Mathematical definitions are supported by source-level evidence.
- Any claimed mathematical correspondence has reproducible validation.
- Incompatible and unresolved relationships remain documented.
- The final report distinguishes lexical overlap, conceptual correspondence, and mathematical correspondence.
- No unverified mapping is promoted to canonical authority.

## 9. Relationship to Existing Research Gates

This investigation is independent of the existing Gate 2 Yao-line producer investigation.

**Gate 2 remains unchanged:**

- Status: OPEN -- Producer unrecovered.
- No canonical authority assigned.
- Two JSON artifacts remain separate data paths.
- Worker metadata does not establish implementation provenance.

QSMC-1 neither resolves nor modifies Gate 2.

## 10. Initial Research Disposition

**QSMC-1: PROPOSED -- NOT YET VERIFIED**

The 184 shared terms provide a useful discovery index. They do not establish 184 mathematical correspondences.

The investigation will prioritize the mathematical structures with the strongest potential for rigorous comparison: Gaussian kernels, expectation operations, Hamiltonian/energy definitions, and phase representations.

The objective is a small, defensible set of validated mathematical correspondences -- or an explicit record that no correspondence has been demonstrated.

The critical safeguard is that the original 184-term inventory remains intact as the discovery source, while the new gate evaluates its claims independently. Gate 2 is unaffected.
