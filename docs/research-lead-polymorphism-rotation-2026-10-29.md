# Polymorphism Is Rotation: Comparative Analysis for King Wen

**Date:** 2026-10-29
**Source:** McCann, Jordan F. "Polymorphism Is Rotation: Operational Mechanistic Interpretability from a Two-Layer Transformer to Pythia-70m." arXiv:2605.30323v1, 2026.
**Purpose:** Comparative methodological analysis. This document does NOT validate the Hamiltonian formula, authorize any code change, or close Gate 2.

---

## 1. Paper Summary

The paper investigates whether independently trained transformers implement the same function while expressing internal activations in substantially different coordinate systems. Key findings:

- **SAE decoder columns** can show high cosine similarity across models while **encoder transfer fails badly** — geometric similarity did not establish functional compatibility.
- **Orthogonal Procrustes alignment** can recover cross-model compatibility in tested models (small transformer + 9 Pythia-70m seeds).
- **Frontier-scale replication remains open** — the strongest results are at small scale.
- The paper distinguishes multiple verification criteria: behavioral agreement, parameter alignment, causal effects, predictive effects — and explicitly separates substantive tests from checks that pass by construction.

Core claim: **independently trained models can implement the same function in different coordinate systems.** The rotation between coordinate systems is a property of the representations, not of the function.

---

## 2. Three Methodological Lessons for King Wen

### 2.1 Lesson 1: Geometric similarity ≠ functional equivalence

The paper's central warning: SAE decoder columns showed high cosine similarity across independently trained models, but transferring the encoder to another model's activations failed. High cosine similarity was **not** evidence of functional compatibility.

**King Wen analog**: The audit found 29 duplicate `expanded_vector` groups — all within the same hexagram, different phases. These duplicates have high geometric similarity (identical or near-identical vectors). But geometric similarity does not establish that:
- The downstream resolver interprets them equivalently
- The temporal phase metadata carries the same meaning
- The emotional vector produces the same voice output
- Consumer behavior is identical

**Audit consequence**: Vector identity tests (structural) and semantic-equivalence tests (functional) must remain separate. The current audit's "512 unique identities" and "29 duplicate groups" are structural findings. They do not establish functional equivalence or inequivalence.

### 2.2 Lesson 2: Verify behavior, not just structure

The paper uses multiple distinct verification criteria and explicitly distinguishes substantive tests from checks that pass by construction. A test that passes by construction (e.g., "the output has 512 records") does not verify correctness.

**King Wen analog**: The current audit has structural tests (identity, phase coverage, field presence) but lacks:
- **Numerical integrity tests**: exact calculations, ranges, boundary behavior (partially addressed by Hamiltonian audit)
- **Semantic integrity tests**: whether output retains intended meaning of input
- **Consumer integrity tests**: whether downstream tools interpret records as intended
- **Adversarial integrity tests**: whether misleading similarities, missing fields, or altered inputs expose false passes

**Audit consequence**: A deterministic pipeline can consistently produce the wrong interpretation. Determinism is necessary for reproducibility but not sufficient for correctness. The 991/991 equation regression report demonstrates pipeline connectivity, not semantic validity.

### 2.3 Lesson 3: Keep alignment transformations outside canonical state

The paper uses orthogonal Procrustes alignment to compare internal representations. This is a **learned coordinate transformation** applied for comparison purposes — not a universal rule that every vector space should be normalized or aligned.

**King Wen analog**: Any future alignment, normalization, or dimensional analysis (e.g., making pq_dot and lagrangian comparable) should live in a **separate analysis layer**. The original vectors and their provenance must be preserved. Alignment must not overwrite:
- Hexagram identity
- Phase metadata
- Canonical tables
- Provenance chains

**Hamiltonian connection**: A transformation that makes pq_dot and lagrangian numerically comparable still needs a justified mathematical contract. The paper does not supply that contract. Procrustes alignment is a comparison tool, not a justification for rescaling.

---

## 3. Representation-Equivalence Test Specification

Based on the paper's methodology, the following test categories should be distinguished:

| Question | Evidence Required | Current Status |
|----------|-------------------|----------------|
| Are two records structurally identical? | Canonical keys and field-by-field comparison | Partially tested (identity, phase coverage) |
| Are their vectors geometrically similar? | Declared metric and coordinate system | Not yet tested with declared metric |
| Are their outputs functionally equivalent? | Matched inputs and downstream behavior | Not tested |
| Is an alignment legitimate? | Stated transformation, assumptions, held-out validation | Not applicable (no alignment proposed) |
| Does equivalence preserve identity? | Original identities recoverable without collisions | Partially tested (29 within-hexagram duplicates) |

### 3.1 What would NOT be sufficient

- High cosine similarity between vectors (paper showed this can coexist with failed encoder transfer)
- Structural identity alone (paper showed structurally similar models can have different functional behavior)
- Deterministic output (paper showed deterministic pipelines can consistently produce wrong interpretations)
- Zero error reports (paper showed checks can pass by construction)

### 3.2 What WOULD be sufficient

- Matched inputs producing matched downstream behavior
- Causal intervention tests (change one field, observe expected change in output)
- Predictive tests (predict output from input, verify against held-out data)
- Held-out validation of any alignment transformation

---

## 4. Important Limitations

1. **The paper's models are not King Wen's models.** The paper studies transformer internal representations. King Wen studies hexagram/emotional vector representations. The mathematical structures are different. The paper provides a methodological framework, not a proof about King Wen.

2. **The paper's strongest results are at small scale.** The Pythia-70m experiments are the strongest scale; frontier-scale replication is open. King Wen's 512-state space is small, but the paper's results do not automatically transfer.

3. **The paper does not supply a mathematical contract.** Procrustes alignment is a comparison tool, not a justification for rescaling pq_dot and lagrangian. The Hamiltonian contract must be established independently.

4. **This analysis does not validate the Hamiltonian formula.** The paper's framework is a methodological research lead, not a code patch or Gate 2 decision.

5. **This analysis does not authorize any source change.** It is a comparative document for future test specification development.

---

## 5. Open Questions for Future Investigation

1. **Representation equivalence vs functional equivalence**: The audit's 29 duplicate expanded_vector groups are structurally identified but not functionally tested. Do downstream consumers (voice, 3D, routing) produce identical output for these duplicates? If yes, the duplicates are functionally redundant. If no, the duplicates encode meaningful phase distinctions that the vector alone doesn't capture.

2. **Alignment layer design**: If a future Hamiltonian contract requires making pq_dot and lagrangian comparable, should the alignment live in a separate analysis layer (per the paper's lesson 3)? What would the alignment's assumptions, transformation, and held-out validation look like?

3. **Adversarial test design**: What inputs would expose false passes in the current pipeline? The paper's framework suggests testing with misleading similarities, missing fields, and altered inputs. What would these look like for King Wen?

4. **Consumer integrity**: The paper's verification criteria include "consumer integrity" — whether downstream tools interpret records as intended. Does OpenJarvis, voicebox, or the 3D avatar consume King Wen output correctly? This has not been tested.

5. **Provenance preservation under alignment**: If an alignment transformation is applied, can the original vectors and their provenance be recovered? The paper preserves original representations; King Wen should do the same.

---

## 6. Recommended Disposition

- **Use this paper as evidence for a representation-equivalence test specification.** It strengthens the case for testing the difference between representation similarity and functional equivalence.
- **Do not treat this paper as validation.** It does not establish that King Wen has the same rotational phenomenon, nor that its pipeline is correct.
- **Do not change source code.** This is a methodological research lead, not an implementation authorization.
- **Gate 2 remains open.** This analysis does not choose between binary-first, ternary-first, or dual-track representation.

### Relevant existing artifacts
- `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` — semantic contract (Gate 2 evidence)
- `docs/hamiltonian-equation-comparison-2026-10-27.md` — Hamiltonian candidate analysis (updated with audit findings)
- `docs/research-lead-incontext-reward-adaptation-2026-10-29.md` — first research lead (reward adaptation)
- `docs/audit-drift-report-2026-10-27.md` — audit drift report
- `DATASETS/math_kingwen_regression_2605.00155.json` — 991-equation regression report