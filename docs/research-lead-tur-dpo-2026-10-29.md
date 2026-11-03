# TUR-DPO: Comparative Analysis for King Wen

**Date:** 2026-10-29
**Source:** arXiv:2605.00224, "TUR-DPO — Topology- and Uncertainty-Aware Direct Preference Optimization." Submitted April 30, 2026. Identified as ICML 2026 paper.
**Purpose:** Comparative methodological analysis. This document does NOT validate the Hamiltonian formula, authorize any code change, or close Gate 2.

---

## 1. Paper Summary

TUR-DPO modifies Direct Preference Optimization (DPO) so that preference learning accounts for more than a binary chosen-vs-rejected label. It combines three signals:

1. **Semantic faithfulness** — whether an answer remains faithful to the relevant meaning
2. **Utility** — whether the answer accomplishes its intended purpose
3. **Reasoning topology** — the structure by which the answer is derived

These signals contribute to a **calibrated uncertainty measure**, which is then incorporated into an **uncertainty-weighted DPO objective**. The approach remains reinforcement-learning-free and uses a fixed or moving reference policy.

The abstract reports improvements in judge win rates, faithfulness, and calibration across several task categories. The pasted source contains the abstract and related-paper listings only — not the method, equations, ablation studies, or full experimental tables.

---

## 2. Potential Connections to King Wen

The most interesting connection is the **separation of answer quality from the structure of the process that produced the answer**. This maps directly onto King Wen's distinction between canonical state, derived features, and consumer behavior.

### 2.1 Semantic faithfulness → source preservation

| TUR-DPO concept | King Wen analog |
|-----------------|----------------|
| Semantic faithfulness | Does the transformed record preserve the source equation, text, and identity? |

In King Wen, `equation_source` (original LaTeX verbatim) must survive through the pipeline unchanged. The adapter already separates `equation_source`, `equation_features`, and `prose_context`. The TUR-DPO framework reinforces this: faithfulness is a distinct signal, not implied by structural validity.

**Question**: Does every transformation in the King Wen pipeline preserve `equation_source` verbatim? The adapter's fixture for equation 0 shows `equation_source` present, but this has not been verified across all 991 equations.

### 2.2 Utility → consumer satisfaction

| TUR-DPO concept | King Wen analog |
|-----------------|----------------|
| Utility | Does the output actually satisfy the requested operation? |

In King Wen, the expansion pipeline produces 64 expanded + 512 resolved states. But "utility" asks: does this output actually help the downstream consumer (voice, 3D, routing) accomplish its task? The current audit has no consumer-integrity tests.

**Question**: When OpenJarvis calls `shotgun_expand()`, does the returned payload actually enable the voice router, 3D avatar, and consult tool to function? Or does the pipeline produce structurally valid but functionally useless output?

### 2.3 Reasoning topology → transformation traceability

| TUR-DPO concept | King Wen analog |
|-----------------|----------------|
| Reasoning topology | Is the sequence of transformations traceable, with intermediate states retained? |

In King Wen, the pipeline is: arxiv HTML → MathML tree → math recovery → adapter → shotgun_expand → resolved states → downstream consumers. Each step transforms the data. The TUR-DPO framework asks: is the structure of that transformation process itself observable and auditable?

**Question**: Can you trace a single equation from arxiv HTML through to its final resolved state, examining every intermediate transformation? The adapter's provenance chain (paper_id, equation_index, extraction_method, recovery_status, source_url, file_hash) is a start, but intermediate transformation states are not retained.

### 2.4 Uncertainty weighting → explicit uncertainty

| TUR-DPO concept | King Wen analog |
|-----------------|----------------|
| Uncertainty weighting | Is uncertainty explicit, rather than hidden behind a default or a confident-looking result? |

In King Wen, the default intent "understand" is assigned to 989/991 equations (99.8%). This is a default, not a classification. The TUR-DPO framework would flag this as hidden uncertainty — the pipeline appears confident (991/991, 0 errors) but 99.8% of equations received no semantic routing.

**Question**: Should the default "understand" intent be reported as uncertainty rather than as a successful classification? The regression report currently counts routing as passing (956/991 = 96.5%) even though 989/991 received the default.

### 2.5 Preference signal → evidence-based evaluation

| TUR-DPO concept | King Wen analog |
|-----------------|----------------|
| Preference signal | Is the evaluation evidence-based, or merely a winner/loser judgment? |

In King Wen, the audit has been using structural agreement (counts, identities, field presence) as evidence. The TUR-DPO framework suggests evaluating on multiple dimensions: faithfulness, utility, topology, uncertainty. A single "pass/fail" judgment is insufficient.

**Question**: Does the King Wen evaluation framework distinguish between structural validity, semantic fidelity, and task success? Currently, the regression report has 5 criteria (extraction, recovery, routing, identity, provenance) but no semantic-fidelity or consumer-satisfaction criteria.

---

## 3. The Most Useful Question to Investigate

The pasted source asks: **Does the full paper define its reasoning topology as an independently evaluated, observable structure, or does it primarily use a learned signal to estimate the quality of that structure?**

This distinction matters for King Wen:

- **If explicit/observable**: The topology structure could inform a provenance and validation layer in King Wen. Each transformation step would be independently auditable, with intermediate states retained.
- **If learned/estimated**: The topology-quality score would be an additional estimate requiring its own calibration and failure tests. It would not replace explicit structural validation.

**Current King Wen state**: The pipeline has explicit structural validation (identity, phase coverage, field presence) but no topology-quality score. The TUR-DPO framework suggests that explicit structural validation is the stronger approach.

---

## 4. Important Limitations

1. **TUR-DPO is a preference-optimization method.** It does not solve the Hamiltonian scale mismatch, justify changing the energy formula, or authorize normalization between hexagrams.
2. **The pasted source contains only the abstract.** The method, equations, ablation studies, and full experimental tables were not provided. Conclusions are based on the abstract only.
3. **The paper's results are reported, not independently verified.** Judge win rates, faithfulness, and calibration improvements are the authors' claims.
4. **The analogies are proposed, not established.** The mapping between TUR-DPO concepts and King Wen components is a proposed framework, not a proven equivalence.
5. **This analysis does not validate the Hamiltonian formula.** The paper's framework is a research lead, not a code patch or Gate 2 decision.
6. **This analysis does not authorize any source change.** It is a comparative document for future evaluation framework development.

---

## 5. Open Questions for Future Investigation

1. **Reasoning topology as provenance**: Can the King Wen pipeline retain intermediate transformation states (e.g., the MathML tree, the recovered LaTeX, the extracted features) as first-class provenance, rather than only the final fixture? What would the storage cost be?

2. **Uncertainty reporting**: Should the default "understand" intent (99.8% of equations) be reported as uncertainty rather than as a successful classification? How would this change the regression report's pass/fail criteria?

3. **Multi-dimensional evaluation**: Should the regression report distinguish between structural validity (identity, field presence), semantic fidelity (correct math interpretation), and task success (downstream consumer works)? Currently, only structural and partial semantic criteria are tracked.

4. **Topology quality score**: Is there a useful King Wen analog to TUR-DPO's reasoning topology score? Could a score be computed from the provenance chain's completeness (all 6 provenance fields present, all transformation steps traceable)?

5. **Uncertainty-weighted expansion**: Could the emotional_input slider be treated as an uncertainty weight? Higher uncertainty → more expansion (more states), lower uncertainty → less expansion. This would connect TUR-DPO's uncertainty weighting to King Wen's slider mechanism.

---

## 6. Recommended Disposition

- **Use this paper as a source for evaluation framework development.** It strengthens the case for multi-dimensional evaluation (faithfulness, utility, topology, uncertainty) rather than single pass/fail judgments.
- **Do not treat this paper as validation.** It does not establish that King Wen's pipeline is correct, nor that its evaluation framework is sufficient.
- **Do not change source code.** This is a research lead, not an implementation authorization.
- **Gate 2 remains open.** This analysis does not choose between binary-first, ternary-first, or dual-track representation.

### Relevant existing artifacts
- `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` — semantic contract (Gate 2 evidence)
- `docs/hamiltonian-equation-comparison-2026-10-27.md` — Hamiltonian candidate analysis (updated with audit findings)
- `docs/research-lead-incontext-reward-adaptation-2026-10-29.md` — first research lead (reward adaptation)
- `docs/research-lead-polymorphism-rotation-2026-10-29.md` — second research lead (representation equivalence)
- `docs/representation-equivalence-audit-checklist-2026-10-29.md` — audit checklist (3 questions, 22 items)
- `docs/audit-drift-report-2026-10-27.md` — audit drift report
- `DATASETS/math_kingwen_regression_2605.00155.json` — 991-equation regression report