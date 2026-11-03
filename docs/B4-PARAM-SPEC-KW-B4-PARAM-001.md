# B4 Parameter Specification — Draft v0.1

**Specification ID:** KW-B4-PARAM-001
**Version:** 0.1 — Draft
**Status:** Pending contract review and Gate 3 validation
**Scope:** Replacement of RNG-based parameter generation in `scripts/kingwen_quantum_expand.py`

## 1. Objective

Replace pseudorandom quantum rotation parameter generation with a deterministic, canonical-state-derived mapping that conforms to the King Wen repository contract.

The implementation must preserve all 64 canonical hexagram identities and all eight phase states per identity. It must not normalize across hexagrams, substitute missing identities, introduce random fallbacks, or collapse candidate evidence.

The existing RNG-based implementation remains an open contract violation until an approved replacement is implemented and validated.

## 2. Input contract

The proposed mapping is:

`(canonical_identity, phase, coherence) → parameters[4, 12, 3]`

### 2.1 Canonical identity

- `canonical_identity`: integer in `[0, 63]`, resolved through the canonical King Wen table.
- `upper_id`: upper-trigram identifier derived from the canonical table.
- `lower_id`: lower-trigram identifier derived from the canonical table.
- The exact encoding, orientation, and relationship between these identifiers and the canonical identity must be documented against the authoritative table.

Trigram identifiers must not be inferred from arbitrary record ordering.

### 2.2 Phase

- `phase`: integer in `[0, 7]`.
- Phase 7 represents the project's defined void phase.
- The mapping from phase indices to phase meanings must use the authoritative phase table.
- `phase_bits` must be defined explicitly as either a phase index or a bitmask. These representations must not be silently interchanged.

Phase must influence parameter derivation according to a documented formula.

### 2.3 Coherence

- `coherence`: finite numeric value in `[0, 1]`.
- Its upstream source, units, validation, and missing-value behavior must be documented.
- Coherence must affect parameter derivation if retained as a mandatory input.
- The specification must define whether coherence changes angle bounds, a modulation amplitude, or another mathematically explicit quantity.

No unexplained default such as `0.5` may replace missing coherence.

## 3. Output contract

The output is a finite tensor with shape `(4, 12, 3)`:

- Four circuit layers.
- Twelve qubits.
- Three rotation channels per qubit: RX, RY, and RZ.

Every tensor coordinate must have a stable, documented relationship to its inputs and index tuple `(layer, qubit, rotation)`.

All angles must satisfy:

`-π ≤ angle < π`

The implementation must reject or explicitly classify invalid inputs rather than silently substituting another canonical state.

## 4. Candidate derivation architecture

The following is a proposed architecture, not an approved mathematical formula.

1. Resolve canonical identity and phase from authoritative tables.
2. Derive upper- and lower-trigram identifiers from the canonical identity.
3. Construct a versioned, unambiguous encoding of the identity, phase, coherence representation, and parameter coordinate.
4. Derive a deterministic value for each tensor coordinate.
5. Apply the documented prime-based algebraic transformation, if confirmed by the contract.
6. Map the resulting value to the permitted angular domain using an explicitly specified transformation.
7. Emit the tensor together with its canonical identity, phase, derivation version, and provenance.

### Hashing constraint

A SHA-256 digest contains 32 bytes, or eight non-overlapping four-byte chunks. A single digest cannot supply 71 independently indexed four-byte chunks.

If hashing is approved, derive values through a documented per-coordinate or domain-separated construction. Define byte order, integer interpretation, digest-to-number conversion, and floating-point conversion explicitly.

Hashing must not be described as proof of compliance with the closed-form algebra requirement. That compliance requires a separate contract decision.

### Coprime-prime constraint

The candidate prime set is:

`257, 263, 269, 271, 277, 281, 283`

Before implementation, document:

- The mathematical role of each prime.
- The modulus and arithmetic domain.
- Which parameter channels use which multipliers.
- Why the construction meets the repository's algebraic requirements.
- Whether the proposed prime set and hashing mechanism are jointly permitted by the canonical contract.

Coprimality alone does not establish uniqueness, collision freedom, or semantic correctness.

## 5. Identity preservation invariants

The implementation must maintain these invariants:

1. Every canonical identity remains explicitly traceable.
2. Every phase remains explicitly traceable.
3. All 512 identity-phase pairs are accounted for.
4. No cross-hexagram normalization occurs.
5. Missing mappings remain missing or unresolved.
6. No random fallback or default-identity substitution occurs.
7. Parameter generation is independent of record processing order.
8. Any downstream selection retains the underlying candidate evidence and provenance.
9. Duplicate output tensors, if any, must not cause distinct canonical records to be merged or discarded.

Output uniqueness is a separate property from identity preservation and must be tested separately if required.

## 6. Gate 3 acceptance tests

### G3-1 — Exhaustive coverage

Enumerate all 64 × 8 identity-phase pairs. Confirm that every pair has exactly the expected processing status and a traceable canonical key.

### G3-2 — Reproducibility

Repeated evaluation of identical inputs must produce identical outputs under the declared supported environment. Reordering records must not alter outputs associated with their keys.

### G3-3 — Identity and phase sensitivity

Test identity and phase changes independently. Confirm that each required input influences derivation as specified. Do not impose universal tensor uniqueness unless that is an explicit contract requirement.

### G3-4 — Tensor validity

Verify the shape, finite values, angular bounds, and documented index-to-rotation mapping for every state.

### G3-5 — Missing and invalid data

Test unknown identities, missing trigram mappings, invalid phase values, missing coherence, NaN, infinity, and out-of-range values. Confirm that no silent substitution or stochastic fallback occurs.

### G3-6 — Coherence semantics

Test boundary values and representative interior values. Confirm that coherence changes the documented modulation or bounds, and that identical complete inputs remain reproducible.

### G3-7 — Downstream integrity

Trace parameters into the quantum circuit and compare the resulting probabilities, Hamiltonian fields, resolved records, and provenance against the approved behavioral contract.

A changed downstream value is not automatically a failure; an unexplained or untraceable change is.

## 7. Regression and reproducibility requirements

Record the current implementation's output as diagnostic evidence only, not as a canonical correctness oracle.

The test report must distinguish:

- Determinism failures.
- Contract violations.
- Missing or unresolved source data.
- Expected numerical changes from replacing the RNG mechanism.
- Downstream behavioral regressions.

Bitwise reproducibility is guaranteed only within explicitly supported numerical environments unless cross-platform equivalence is separately demonstrated.

## 8. Approval questions

Implementation is blocked until these are resolved:

- Is SHA-256 permitted by the closed-form algebra contract?
- What is the authoritative algebraic mapping from canonical inputs to angles?
- What exact role does each prime play?
- How does coherence mathematically affect the result?
- What identity and phase sensitivity properties are mandatory?
- What constitutes acceptable downstream behavioral parity?

## 9. Layer 0 audit status

**Status:** Layer 0 provisionally audited. B4 remains OPEN pending Gate 3 completion.

### Layer 0 comprehension gates — verified

- [x] **G1:** emotional_input=50 → slider_factor=0.5 → 64×8=512 resolved states via shotgun_expand()
- [x] **G2:** phase_bits 0-7 = past/yin, present/yang, future/yao, transition, resolution, dissolution, crystallization, void
- [x] **G3:** porosity_norm is boundary bleed coefficient, NOT probability

### Contract-to-implementation matrix

| Rule | Source | Current | Required |
|-----|--------|---------|----------|
| 512 states | emotional_engine.py:966-1001 | 512 via sample_resolve | All enumerated |
| 64 distinct binaries | KING_WEN_TABLES.py | 64 unique | All distinct |
| 9-bit encoding | kingwen_ternary_tables_complete.py | 9 slots/hex | Full 512 |
| Phase ordering | temporal_emotional_engine.py | past→future→transition→res→diss→cryst→void | 8 phases |

## 10. Related artifacts

- Review: `src/utils/DeterministicHash.ts` — reference for prime-based derivation
- Audit: `docs/audit-drift-report-2026-10-27.md` — B4 violation record
- Contract: `KINGWEN_AGENT_ONBOARDING.md` — zero-pseudo-RNG absolute prohibition
