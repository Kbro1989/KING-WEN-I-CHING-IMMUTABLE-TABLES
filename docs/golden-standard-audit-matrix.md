# Golden-Standard Audit Matrix — PDF Math Parser Evaluation

**Date:** 2026-11-06
**Branch:** `v2-remediation` (befa228927)
**Reference:** Attachment file inventory (pasted_content_2026-11-06_20-10-55-471_cb3ba1.txt)

---

## Purpose

This matrix categorizes every file relevant to updating the PDF math-parser golden standard. The important distinction is between:

1. **Gold truth** — files that define adjudicated labels, geometry, and expected structures
2. **Adjudication** — files that govern how candidates are classified and resolved
3. **Evaluation** — files that test engine output against the gold standard

These three layers must not become one authority layer. Each layer has its own authority level.

---

## Summary Table

| Category | Count | Authority Level |
|----------|-------|-----------------|
| 1. Primary authority | 8 | HIGH — frozen, handle with care |
| 2. Structural/semantic gold | 10 | MEDIUM — evidence for what output should contain |
| 3. Evaluator integrity (G0–G5) | 11 | HIGH — govern testing, not gold definitions |
| 4. Source data/registries/code | 16 | MEDIUM-HIGH — path from evidence to frozen targets |
| 5. Supporting evidence/defect probes | 10 | LOW — inform changes, do not authorize them |

**Total:** 55 files across 5 categories.

---

## Category 1 — Primary Authority

> **Rule:** These files establish the adjudication authority chain. Read before changing any golden labels, geometry, or expected structures.

| File | Authority | Depends On | Evidence Req. | Safe to Modify? |
|------|-----------|------------|---------------|-----------------|
| `docs/adjudication-layer-contract.md` | HIGH | — | Layer-2 and Layer-3 files | **NO** — frozen authority |
| `docs/CROSS_PAPER_V2_EVALUATION_PROTOCOL.md` | HIGH | All five-axis spec | V1/V2 evaluator results | **NO** — frozen protocol |
| `docs/CROSS_PAPER_SOURCE_SELECTION_RECONNAISSANCE_V1.md` | MEDIUM-HIGH | Source-paper corpus | Source-selection logic | Conditional |
| `docs/CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md` | MEDIUM-HIGH | V2 engine outputs | Delimiter taxonomy | Conditional |
| `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | HIGH | Frozen cases | V1 execution evidence | **NO** — frozen mapping |
| `docs/frozen-regression-execution-results-2026-11-03.md` | MEDIUM | V1 evaluation runs | Pre-v1 engine outputs | Conditional |
| `docs/phase2c_specification.md` | HIGH | Gate definitions | Phase-2C gate runs | **NO** — frozen spec |
| `docs/phase2c_closure_record.md` | MEDIUM | Closure decisions | Closure rationale | Conditional |

**Priority order:** `adjudication-layer-contract.md` → `CROSS_PAPER_V2_EVALUATION_PROTOCOL.md` → `frozen-regression-evaluation-mapping-2026-11-03.md`.

---

## Category 2 — Structural and Semantic Gold Evidence

> **Rule:** These documents inform **what** the expected output should contain, not **where**. They support the semantic-content side of the authority chain.

| File | Authority | Depends On | Evidence Req. | Safe to Modify? |
|------|-----------|------------|---------------|-----------------|
| `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` | HIGH | B4 semantic contract | Source math content | Conditional |
| `docs/spatial-syntactic-preservation-specification.md` | HIGH | Spatial relations | Source rendering | Conditional |
| `docs/semantic_math_pipeline_report.md` | MEDIUM | Pipeline runs | Pipeline artifacts | Conditional |
| `docs/math-pipeline-evidence-matrix-2026-11-03.md` | MEDIUM | Pipeline traces | Evidence files | Conditional |
| `docs/math-output-candidate-audit-2026-11-04.md` | MEDIUM | Candidate outputs | Parser outputs | Conditional |
| `docs/math-output-regeneration-verification-2026-11-04.md` | MEDIUM | Regeneration runs | Regeneration artifacts | Conditional |
| `docs/math-output-retention-review-2026-11-04.md` | MEDIUM | Retention records | Retention evidence | Conditional |
| `docs/occurrence-lifecycle-ledger-contract-2026-11-03.md` | MEDIUM | Occurrence records | Lifecycle data | Conditional |
| `docs/CONSOLIDATED_FIELD_LINEAGE.md` | MEDIUM | Field derivation | Lineage traces | NO |
| `docs/B4-PARAM-SPEC-KW-B4-PARAM-001.md` | HIGH | B4 parameter spec | Parameter definitions | Conditional |

> **Note:** The B4 contract distinguishes: correct localization → complete glyph recovery → correct structural reconstruction → mathematical semantic equivalence → boundary isolation. A correct crop is not proof of a correct equation.

---

## Category 3 — Evaluator Integrity (G0–G5)

> **Rule:** These files govern **how** the golden standard is tested, not **what** the gold standard means. They should not silently change the gold standard.

| File | Authority | Depends On | Evidence Req. | Safe to Modify? |
|------|-----------|------------|---------------|-----------------|
| `docs/standalone-context-preservation-test-plan-2026-11-04.md` | HIGH | Preservation scenario | Context preservation runs | Conditional |
| `docs/context-preservation-implementation-evaluation-spec-2026-11-04.md` | HIGH | Implementation | Implementation state | Conditional |
| `docs/context-preservation-gate-verification-matrix-2026-11-04.md` | HIGH | Gate definitions | Gate test runs | Conditional |
| `docs/controlled-remediation-verification-protocol.md` | HIGH | Remediation cases | Remediation evidence | Conditional |
| `docs/remediation-verification-matrix.md` | HIGH | Remediation runs | Remediation artifacts | Conditional |
| `docs/phase2b_adversarial_challenge_set.md` | HIGH | Adversarial cases | Challenge test runs | Conditional |
| `docs/phase2b_selection_procedure.md` | MEDIUM | Selection rules | Selection process | Conditional |
| `docs/phase2b_final_report.md` | MEDIUM | Historical results | Historical runs | Conditional |
| `scripts/positive_control_comparison.py` | HIGH | Positive controls | Control comparisons | NO |

**G0–G5 wiring (from the attachment):**

- **G0:** independent engine prediction
- **G1:** comparable localization
- **G2:** four-edge clearance and contamination
- **G3:** direct semantic comparison
- **G4:** real adversarial perturbations through production paths
- **G5:** three-state gate verdicts and correct denominator accounting

---

## Category 4 — Source Data, Registries, and Executable Evaluation Code

> **Rule:** These files form the path from source evidence to the frozen target set. Inspect before changing the golden standard.

| File | Role | Authority | Safe to Modify? |
|------|------|-----------|-----------------|
| `scripts/build_cross_paper_case_registry.py` | Builds cross-paper registry | HIGH | NO |
| `scripts/validate_cross_paper_case_registry.py` | Validates registry consistency | MEDIUM | NO |
| `scripts/freeze_cross_paper_case_registry_manifest.py` | Freezes identity/provenance | HIGH | **NO** — freezes truth |
| `scripts/adjudicate_targets.py` | Target adjudication (Layer 3) | HIGH | Conditional |
| `scripts/adjudicate_candidates_v2.py` | Candidate adjudication (Layer 2) | HIGH | Conditional |
| `scripts/case_registry_patch_manager.py` | Registry modifications | MEDIUM | NO |
| `scripts/evaluate_cross_paper_v2_strict.py` | Strict evaluator (G0–G5) | HIGH | Conditional |
| `scripts/evaluate_cross_paper_generalization_v1.py` | V1 generalization evaluator | HIGH | Conditional |
| `scripts/evaluate_v1_v2_cross_paper_comparison.py` | Cross-version comparison | HIGH | Conditional |
| `scripts/phase2c_evaluate_gates.py` | Phase 2C gate execution | HIGH | Conditional |
| `scripts/phase2c_gate_library.py` | Gate definitions/measurement | HIGH | NO |
| `scripts/positive_control_comparison.py` | Positive-control comparison | HIGH | NO |
| `scripts/span_audit_gold_equations.py` | Gold equation span audit | MEDIUM | Conditional |
| `scripts/audit_gold_equation_chains_1505.py` | Gold equation-chain audit | MEDIUM | Conditional |
| `scripts/paper_registry.py` | Paper registry | HIGH | Conditional |
| `scripts/verify_registry.py` | Registry verification | MEDIUM | NO |

---

## Category 5 — Supporting Evidence and Known Defect Investigations

> **Rule:** These files inform changes but do not independently authorize gold-label changes. They are reference, not authority.

| File | Relevance |
|------|-----------|
| `docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md` | Border recognition findings |
| `docs/glyph-catalog-template-matching-p1-spec-2026-11-03.md` | Template matching spec |
| `docs/math-pipeline-reproducibility-defect-register-2026-11-04.md` | Reproducibility defects |
| `docs/mprd002-diagnostic-report-2026-11-04.md` | Diagnostic report 2 |
| `docs/mprd003-diagnostic-report-2026-11-04.md` | Diagnostic report 3 |
| `docs/mprd004-diagnostic-report-2026-11-04.md` | Diagnostic report 4 |
| `docs/information-loss-remediation-register.md` | Information loss remediations |
| `docs/lossy-coverage-cross-examination-2026-11-04.md` | Lossy coverage cross-examination |
| `docs/unknowns-register-2026-11-02.md` | Unknowns register |
| `docs/read-only-evidence-pass-2026-10-29.md` | Evidence read-only pass |

---

## Recommended Inspection Order

> Do not begin by editing the registry. First establish whether the existing gold standard is internally consistent.

1. **Establish the current authority** — Read `adjudication-layer-contract.md`, `CROSS_PAPER_V2_EVALUATION_PROTOCOL.md`, `frozen-regression-evaluation-mapping-2026-11-03.md`, and the case-registry manifest.
2. **Reconcile source evidence** — Inspect the gold-equation span audit, equation-chain audit, source-selection reconnaissance, and case registry.
3. **Check semantic and structural requirements** — Compare B4, spatial-syntactic preservation, occurrence lifecycle, and semantic pipeline contracts.
4. **Audit evaluator independence** — Apply G0–G5 to the evaluator implementation without changing v1 or v2.
5. **Propose gold-standard changes** — Only after the previous stages, create explicit, traceable additions or corrections to the adjudicated cases.

---

## Three-Version Truth Policy

> Maintain three separate versions of the truth:

1. **Original frozen gold:** immutable record of what was previously adjudicated.
2. **Proposed revised gold:** proposed corrections or additions, each with source evidence and rationale.
3. **Certified gold:** revised gold accepted only after independent adjudication and consistency checks.

**Do not overwrite the original gold labels to make an evaluator pass.** That would make it impossible to distinguish an actual engine improvement from a moving acceptance target.

---

## Evaluation Gates — Quick Reference

| Gate | Requirement | G0/G1/G2/G3/G4/G5 |
|------|-------------|-------------------|
| G0 | Independent engine prediction | G0 |
| G1 | Comparable localization | G1 |
| G2 | Four-edge clearance and contamination | G2 |
| G3 | Direct semantic comparison | G3 |
| G4 | Real adversarial perturbations through production paths | G4 |
| G5 | Three-state gate verdicts and correct denominator accounting | G5 |

---

## Notes on the Attachment's Classification

The attachment's table lists `docs/positive_control_comparison.py` as "Not listed; the actual file in your inventory is `scripts/positive_control_comparison.py`." This matrix uses the actual on-disk file path: `scripts/positive_control_comparison.py`.

The attachment's Section 2 table lists 10 files. This matrix includes 10 files. The attachment's Section 4 table lists 16 files. This matrix categorizes 16 files. The attachment's Section 5 lists 10 files. This matrix lists 10 files.

---

## Files Safe to Modify (Summary)

| Category | Files Safe to Modify |
|----------|----------------------|
| 1 (Primary authority) | None — all frozen |
| 2 (Structural/semantic gold) | Conditional — only with source evidence |
| 3 (Evaluator integrity) | Conditional — only with audit evidence |
| 4 (Source data/registries) | Conditional — only with audit evidence |
| 5 (Supporting evidence) | Low — do not use to override gold |

**Files that must NEVER be modified:**
- `docs/adjudication-layer-contract.md`
- `docs/CROSS_PAPER_V2_EVALUATION_PROTOCOL.md`
- `docs/frozen-regression-evaluation-mapping-2026-11-03.md`
- `docs/phase2c_specification.md`
- `scripts/phase2c_gate_library.py`
- `scripts/freeze_cross_paper_case_registry_manifest.py`
- `scripts/positive_control_comparison.py`
- `scripts/phase2c_evaluate_gates.py`
