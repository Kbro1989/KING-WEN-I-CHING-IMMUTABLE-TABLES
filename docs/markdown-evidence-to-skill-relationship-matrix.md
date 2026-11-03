# Markdown Evidence-to-Skill Relationship Matrix — Inventory

## Scope and Method

- **Read-only investigation.** No files, frontmatter, skill definitions, or graph edges were modified.
- **Three evidence populations** classified per the proposed framework:
  - **Population A — Modified tracked:** 1 modified `.md` file (`README.md`)
  - **Population B — Newly created (untracked):** 63 `docs/*.md` files
  - **Population C — Unmodified historical:** 102 tracked `.md` files (committed, unchanged)
- **Total Markdown files in repo:** 166 (103 tracked in `docs/`, 1 modified tracked, 63 untracked docs, plus root-level and other directories)

## Git State Reconciliation

| Check | Result |
|-------|--------|
| Modified tracked files | 18 (not 16 — detailed breakdown is controlling) |
| Staged changes | 0 |
| Untracked files | 98 |
| HEAD commit | `71fbf28f8e92c6a7de74c50a304906ef81963a7d` |
| @{u} commit | `71fbf28f8e92c6a7de74c50a304906ef81963a7d` |
| Commits ahead/behind upstream | 0 / 0 |
| Branches diverged | No |

---

## Population A — Modified Tracked Markdown

| # | Path | Subject | Evidence Type | Status | Relevant Skills | Related Skills Implication |
|---|------|---------|---------------|--------|-----------------|---------------------------|
| A1 | `README.md` | Repository overview — King Wen cognitive state machine, 512 states, 64 hexagrams × 8 phases | Specification | Authoritative (root-level project doc) | `kingwen`, `kingwen-ternary-expansion`, `openjarvis-kingwen-integration` | Root README is the primary project identity document; its content should inform skill descriptions |

---

## Population B — Newly Created (Untracked) Markdown Documents

### B1: QSMC-1 Audit / Verification Series (25 files)

| # | Path | Subject | Evidence Status | Confidence | Supersedes/Extends | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-------------------|-----------------|--------------------------|
| B1-1 | `qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | M3 Hamiltonian provenance — 15 sections, formula lineage, V1 vs V2, QuantumLab ruled out | Validated (F-10/F-11/F-12) | High | Extends `immutable-table-math-decoded.md` | `kingwen`, `kingwen-ternary-expansion`, `megatron`, `openjarvis-kingwen-integration` | Math extraction skills should reference this as the M3 provenance authority |
| B1-2 | `qsmc1-m3-mathematical-validation-f10.md` | F-10 semantic/scale compatibility validation | Validated | High | Extends B1-1 | `kingwen-ternary-expansion`, `math-pdf-parser` | Math extraction skills consume M3 validation results |
| B1-3 | `qsmc1-m3-one-sided-clamp-information-loss-f12.md` | F-12 clamp information loss (727→1 distinct values) | Validated | High | Extends B1-1 | `kingwen`, `kingwen-ternary-expansion` | Core King Wen skill should reference clamp finding |
| B1-4 | `qsmc1-m3-m6-imaginary-amplitude-f11.md` | F-11 imaginary amplitude (type 2 dependency) | Validated | High | Extends B1-1 | `kingwen`, `kingwen-emotion-voice` | Emotion voice skill should reference F-11 |
| B1-5 | `qsmc1-m3-dimensional-consistency-analysis.md` | F-10 formal dimensional analysis (608 lines) | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | Math extraction skills should reference |
| B1-6 | `qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md` | M3 floor/ceiling/extremum research | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | |
| B1-7 | `qsmc1-m3-scale-mismatch-diagnosis.md` | M3 scale mismatch numerical diagnosis | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | |
| B1-8 | `qsmc1-m3-hamiltonian-energy-correspondence.md` | M3 Hamiltonian correspondence evidence | Validated | High | Extends B1-1 | `kingwen`, `kingwen-ternary-expansion` | |
| B1-9 | `qsmc1-m3-m6-reproduction.md` | M3–M6 numerical reproduction | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | |
| B1-10 | `qsmc1-m4-phase-representations-correspondence.md` | M4 phase representations | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-11 | `qsmc1-m5-angular-momentum-vortex-correspondence.md` | M5 angular momentum/vortex | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-12 | `qsmc1-m6-interference-coherence-correspondence.md` | M6 interference/coherence | Validated | High | — | `kingwen`, `kingwen-emotion-voice` | |
| B1-13 | `qsmc1-m7-evolution-propagation-correspondence.md` | M7 evolution/propagation | Validated | High | — | `kingwen`, `megatron` | |
| B1-14 | `qsmc1-m7-numerical-equivalence.md` | M7 numerical equivalence | Validated | High | — | `kingwen`, `megatron` | |
| B1-15 | `qsmc1-m7-source-provenance.md` | M7 source provenance | Validated | High | — | `kingwen`, `megatron` | |
| B1-16 | `qsmc1-m1-gaussian-kernel-correspondence.md` | M1 Gaussian kernel | Validated | High | — | `kingwen-ternary-expansion` | |
| B1-17 | `qsmc1-m1-m2-normalization-validation.md` | M1–M2 normalization | Validated | High | — | `kingwen-ternary-expansion` | |
| B1-18 | `qsmc1-m2-expectation-consensus-correspondence.md` | M2 expectation/consensus | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-19 | `qsmc1-cross-group-consistency-validation.md` | Cross-group consistency | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-20 | `qsmc1-cross-group-correspondence-synthesis.md` | Cross-group synthesis | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-21 | `qsmc1-quantum-sim-mathematical-correspondence-audit.md` | Quantum-sim correspondence | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |
| B1-22 | `qsmc1-consumer-boundary-audit.md` | Consumer boundary audit | Validated | High | — | `kingwen`, `openjarvis-kingwen-integration` | |
| B1-23 | `qsmc1-m3-scale-mismatch-diagnosis.md` | Scale mismatch diagnosis (supplementary) | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | |
| B1-24 | `qsmc1-m3-m6-reproduction.md` | M3–M6 reproduction | Validated | High | Extends B1-1 | `kingwen-ternary-expansion` | |
| B1-25 | `qsmc1-cross-group-consistency-validation.md` | Cross-group consistency validation | Validated | High | — | `kingwen`, `kingwen-ternary-expansion` | |

### B2: Lineage / Audit Series (12 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B2-1 | `emotional-vector-lineage-audit-2026-11-02.md` | L1 — Emotional vector field-level lineage | Validated | High | `kingwen`, `kingwen-ternary-expansion`, `kingwen-emotion-voice` | Lineage audit links King Wen core to emotion voice skill |
| B2-2 | `porosity-lineage-audit-2026-11-02.md` | L2 — Porosity field-level lineage | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-3 | `hamiltonian-lineage-audit-2026-11-02.md` | L3 — Hamiltonian field-level lineage | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-4 | `cross-field-dependency-matrix-2026-11-02.md` | Cross-field dependency matrix | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-5 | `cross-reference-audit-2026-11-02.md` | Cross-reference audit (10 reports) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-6 | `pre-remediation-evidence-freeze-2026-11-02.md` | Evidence freeze (16-artifact index) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-7 | `unknowns-register-2026-11-02.md` | Unknowns register (U-01 through U-10) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-8 | `journey-weave-audit-2026-11-03.md` | Journey weave audit (Step 1 archive filtering) | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | Journey weave links King Wen to OpenJarvis integration |
| B2-9 | `remediation-verification-matrix.md` | 8-entry verification matrix (F-01–F-08) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-10 | `information-loss-remediation-register.md` | 27-entry remediation register (R-01–R-27) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-11 | `controlled-remediation-verification-protocol.md` | 5-section RVG protocol | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B2-12 | `rv-governance-addition-2026-11-03.md` | RVG governance addition (6-stage lifecycle) | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |

### B3: King Wen Math / Pipeline Series (15 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B3-1 | `immutable-table-math-decoded.md` | King Wen immutable table math decoded | Authoritative (source of truth) | High | `kingwen`, `kingwen-ternary-expansion` | Core math reference |
| B3-2 | `j-space-jacobian-lens-math-2026-07-11.md` | J-lens exact math formulation | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-3 | `KING_WEN_CONSENSUS_MATH.md` | 512-state Gaussian consensus mathematical spec | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-4 | `ternary-paired-differential-math-correction-2026-08-02.md` | Ternary paired differential math correction | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-5 | `kingwen-superposition-expansion-plan-2026-07-11.md` | King Wen quantum expansion plan | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-6 | `kingwen-jspace-domain-layer-2026-07-11.md` | King Wen J-Space domain layer | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-7 | `kingwen-quantum-methods-2026-07-11.md` | King Wen quantum methods | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-8 | `chain-role-classification-and-momentum-map-2026-10-04.md` | Chain role classification & momentum map | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-9 | `math-term-usage-analysis-2026-10-27.md` | Math term usage analysis for King Wen engine | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-10 | `formula-design-review-2026-10-27.md` | Formula-level design review: emotional vector axes | Validated | High | `kingwen`, `kingwen-ternary-expansion`, `kingwen-emotion-voice` | Emotion voice skill should reference formula design |
| B3-11 | `audit-drift-report-2026-10-27.md` | Audit drift: old findings vs pipeline output measurement | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-12 | `pipeline-gap-analysis-2026-10-27.md` | Pipeline output measurement gap analysis | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-13 | `pipeline-output-measurement-2026-10-27.md` | Pipeline output measurement report | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-14 | `vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` | Vortex/Hamiltonian/Jacobian/Gaussian diagnostic | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B3-15 | `hamiltonian-equation-comparison-2026-10-27.md` | Hamiltonian equation comparison | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |

### B4: Integration / Architecture Series (8 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B4-1 | `consumer-boundary-audit-2026-10-29.md` | Consumer boundary audit — OpenJarvis King Wen integration | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | Consumer boundary links King Wen to OpenJarvis integration |
| B4-2 | `consumer-repair-specification-2026-10-29.md` | Consumer repair spec and contract-test plan | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | |
| B4-3 | `integration-rule-audit-2026-10-29.md` | Integration-rule audit: corrected rule application | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | |
| B4-4 | `shotgun-expand-output-contract-2026-10-29.md` | shotgun_expand output contract | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B4-5 | `shotgun-expansion-integrity-audit.md` | Shotgun expansion integrity audit | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B4-6 | `shotgun-authority-lineage-audit.md` | Shotgun authority lineage audit | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B4-7 | `shotgun-representation-consumer-continuity-audit.md` | Representation-to-consumer continuity audit | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | |
| B4-8 | `shotgun-reinvention-audit.md` | Shotgun reinvention audit | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |

### B5: Math Extraction / Pipeline Series (10 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B5-1 | `numerical-extraction-vision-pipeline.md` | Numerical extraction & vision pipeline audit | Validated | High | `kingwen`, `research/math-pdf-parser`, `research/vision-math-symbol-detection` | Math extraction skills should reference |
| B5-2 | `pix2text-assessment-2026-10-20.md` | King Wen math pipeline vs Pix2Text assessment | Validated | High | `kingwen`, `research/math-pdf-parser` | |
| B5-3 | `pix2text-three-layer-experiment.md` | Pix2Text three-layer glyph recognition | Validated | High | `kingwen`, `research/math-pdf-parser` | |
| B5-4 | `semantic_math_pipeline_report.md` | Semantic math extraction & solving pipeline | Validated | High | `kingwen`, `research/math-pdf-parser` | |
| B5-5 | `room-5-typed-integral-ir-2026-10-08.md` | Room 5 — typed integral IR | Validated | High | `kingwen`, `research/math-pdf-parser` | |
| B5-6 | `adjudication-layer-contract.md` | Adjudication layer contract | Validated | High | `kingwen`, `research/math-pdf-parser` | |
| B5-7 | `traceability-matrix-2026-10-27.md` | Documentation-to-implementation traceability matrix | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B5-8 | `traceability-matrix-audit-2026-10-27.md` | Traceability matrix audit report | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B5-9 | `research-to-test-traceability-matrix-2026-10-29.md` | Research-to-test traceability matrix | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B5-10 | `read-only-evidence-pass-2026-10-29.md` | Read-only evidence pass | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |

### B6: Pair Dynamics / Yao / Phase Series (5 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B6-1 | `pair_dynamics_audit_2026-10-27.md` | Pair dynamics audit report | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B6-2 | `pair_dynamics_audit_corrected.md` | Pair dynamics audit — verified against canonical tables | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B6-3 | `pair_dynamics_audit_summary_2026-10-27.md` | Pair-dynamics audit — verification script passed | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B6-4 | `yao-line-semantic-audit-2026-10-29.md` | Yao-line semantic audit | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B6-5 | `phase2b_adversarial_challenge_set.md` | Phase 2B — adversarial challenge set | Validated | Medium | `kingwen`, `kingwen-ternary-expansion` | |

### B7: Phase / Pipeline / Quantum Series (8 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B7-1 | `phase2b_final_report.md` | Phase 2B — final report: 100-equation pilot | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-2 | `phase2b_selection_procedure.md` | Phase 2B — selection procedure | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-3 | `phase2c_closure_record.md` | Phase 2C closure record | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-4 | `phase2c_specification.md` | Phase 2C — gate calibration specification | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-5 | `phase2c_gate1_calibration.md` | Phase 2C — Gate 1 calibration | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-6 | `phase2c_gate2_calibration.md` | Phase 2C — Gate 2 calibration | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-7 | `phase2c_gate5_calibration.md` | Phase 2C — Gate 5 calibration | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B7-8 | `qsmc1-m3-m6-reproduction.md` | M3–M6 numerical reproduction | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |

### B8: Other Research / Audit Series (10 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B8-1 | `audit-drift-report-2026-10-27.md` | Audit drift: old findings vs pipeline output | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B8-2 | `representation-equivalence-audit-checklist-2026-10-29.md` | Representation-equivalence audit checklist | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B8-3 | `persona-personality-coder-agent-usage-audit.md` | Persona/personality/coder/agent usage audit | Validated | High | `kingwen`, `openjarvis-kingwen-integration` | |
| B8-4 | `research-archaeology-baseline-2026-10-07.md` | Research archaeology corrected baseline | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B8-5 | `BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md` | Benchmarks/rules/onboarding/README audit | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B8-6 | `avalokiteshvara-kingwen-mapping.md` | Avalokiteshvara King Wen registry | Authoritative | High | `kingwen`, `avalokiteshvara-kingwen` | Direct skill reference |
| B8-7 | `CLOUDFLARE_DEPLOYMENT_GUIDE.md` | Cloudflare deployment guide | Operational | Medium | `kingwen`, `openjarvis-kingwen-integration` | |
| B8-8 | `OEIS_KING_WEN_SEQUENCE.md` | OEIS submission draft | Authoritative | High | `kingwen`, `kingwen-ternary-expansion` | |
| B8-9 | `KING-WEN-RESEARCH-CHECKLIST.md` | King Wen research execution checklist | Operational | Medium | `kingwen`, `kingwen-ternary-expansion` | |
| B8-10 | `KING-WEN-RESEARCH-GUIDE.md` | King Wen research execution guide | Operational | Medium | `kingwen`, `kingwen-ternary-expansion` | |

### B9: Other / Infrastructure (5 files)

| # | Path | Subject | Evidence Status | Confidence | Relevant Skills | Relationship Implication |
|---|------|---------|-----------------|------------|-----------------|--------------------------|
| B9-1 | `README.md` (docs/) | docs/ directory README | Operational | Medium | `kingwen` | |
| B9-2 | `cross-verification-checklist-2026-09-01.md` | Cross-verification checklist | Validated | High | `kingwen`, `kingwen-ternary-expansion` | |
| B9-3 | `VISUAL_MATH_RECONSTRUCTION_CHECKLIST_2026-10-13.md` | Visual math reconstruction checklist | Validated | High | `kingwen`, `research/vision-math-symbol-detection` | |
| B9-4 | `source_to_visual_traceability_audit.md` | Source-to-visual traceability audit | Validated | High | `kingwen`, `research/vision-math-symbol-detection` | |
| B9-5 | `numerical-extraction-vision-pipeline.md` | Numerical extraction & vision pipeline | Validated | High | `kingwen`, `research/vision-math-symbol-detection` | |

---

## Population C — Unmodified Historical Markdown (Tracked, Not Modified)

### C1: King Wen Core Math / Tables (2 files)

| # | Path | Subject | Evidence Type | Status | Relevant Skills |
|---|------|---------|---------------|--------|-----------------|
| C1-1 | `docs/immutable-table-math-decoded.md` | King Wen immutable table math decoded | Authoritative | Authoritative | `kingwen`, `kingwen-ternary-expansion` |
| C1-2 | `docs/KING_WEN_LINK_ACOUSTIC_PROTOCOL.md` | King Wen Link acoustic wave-packet protocol | Authoritative | Authoritative | `kingwen`, `kingwen-emotion-voice` |

### C2: King Wen Domain / J-Space (3 files)

| # | Path | Subject | Evidence Type | Status | Relevant Skills |
|---|------|---------|---------------|--------|-----------------|
| C2-1 | `docs/kingwen-jspace-domain-layer-2026-07-11.md` | King Wen J-Space domain layer | Authoritative | Authoritative | `kingwen`, `kingwen-ternary-expansion` |
| C2-2 | `docs/kingwen-quantum-methods-2026-07-11.md` | King Wen quantum methods | Authoritative | Authoritative | `kingwen`, `kingwen-ternary-expansion` |
| C2-3 | `docs/KING-WEN-RESEARCH-CHECKLIST.md` | King Wen research execution checklist | Operational | Medium | `kingwen`, `kingwen-ternary-expansion` |

### C3: King Wen Research / Interop (5 files)

| # | Path | Subject | Evidence Type | Status | Relevant Skills |
|---|------|---------|---------------|--------|-----------------|
| C3-1 | `docs/interop-algebra-empirical-graph.md` | Interop algebra empirical graph | Validated | High | `kingwen`, `kingwen-ternary-expansion` |
| C3-2 | `docs/chain-role-classification-and-momentum-map-2026-10-04.md` | Chain role classification & momentum map | Validated | High | `kingwen`, `kingwen-ternary-expansion` |
| C3-3 | `docs/avalokiteshvara-kingwen-mapping.md` | Avalokiteshvara King Wen registry | Authoritative | High | `kingwen`, `avalokiteshvara-kingwen` |
| C3-4 | `docs/adjudication-layer-contract.md` | Adjudication layer contract | Validated | High | `kingwen`, `kingwen-ternary-expansion` |
| C3-5 | `docs/KING-WEN-RESEARCH-GUIDE.md` | King Wen research execution guide | Operational | Medium | `kingwen`, `kingwen-ternary-expansion` |

### C4: King Wen Pipeline / Output (4 files)

| # | Path | Subject | Evidence Type | Status | Relevant Skills |
|---|------|---------|---------------|--------|-----------------|
| C4-1 | `docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md` | Cloudflare deployment guide | Operational | Medium | `kingwen`, `openjarvis-kingwen-integration` |
| C4-2 | `docs/numerical-extraction-vision-pipeline.md` | Numerical extraction & vision pipeline | Validated | High | `kingwen`, `research/vision-math-symbol-detection` |
| C4-3 | `docs/semantic_math_pipeline_report.md` | Semantic math extraction & solving pipeline | Validated | High | `kingwen`, `research/math-pdf-parser` |
| C4-4 | `docs/wolfram_notation_reference.md` | Wolfram notation reference | Authoritative | High | `kingwen`, `research/math-pdf-parser` |

### C5: Other Committed Docs (3 files)

| # | Path | Subject | Evidence Type | Status | Relevant Skills |
|---|------|---------|---------------|--------|-----------------|
| C5-1 | `docs/README.md` | docs/ directory README | Operational | Medium | `kingwen` |
| C5-2 | `AGENTS.md` | Agent instructions | Operational | Medium | `kingwen` |
| C5-3 | `codebasemap.md` | Codebase map | Operational | Medium | `kingwen` |

---

## Proposed Relationship Matrix (Validation-Only, No Edits)

Based on the inventory above, the following are candidate `related_skills` relationships for future validation. These are **proposed, not authorized**.

| Source Skill | Candidate Target | Rationale (from Markdown evidence) | Evidence Status | Proposed Disposition |
|-------------|-----------------|-----------------------------------|-----------------|---------------------|
| `kingwen` | `kingwen-ternary-expansion` | Direct capability dependency; ternary expansion is the core math engine | Authoritative (immutable-table-math-decoded.md) | **Supported** |
| `kingwen` | `openjarvis-kingwen-integration` | Integration bridge; 12+ audit docs reference this relationship | Validated (qsmc1-consumer-boundary-audit.md) | **Supported** |
| `kingwen` | `megatron` | Training substrate; megatron-king-wen skill exists; wiki_math_corpus referenced | Validated (qsmc1-m3-mathematical-provenance) | **Supported** |
| `kingwen` | `research/kingwen-jarvis-megatron-learn` | Learning loop bridge | Validated (qsmc1-cross-group-correspondence-synthesis.md) | **Supported** |
| `kingwen` | `research/kingwen-oracle-advisory` | Oracle advisory interface | Validated (qsmc1-m3-* series) | **Supported** |
| `kingwen` | `research/kingwen-learn-suite-runner` | /learn verification suite | Validated (qsmc1-m3-* series) | **Supported** |
| `kingwen` | `research/avalokiteshvara-kingwen` | Capability registry | Validated (avalokiteshvara-kingwen-mapping.md) | **Supported** |
| `kingwen` | `research/learn_king_wen_math_extractors` | Math extractors | Validated (numerical-extraction-vision-pipeline.md) | **Supported** |
| `kingwen` | `autonomous-ai-agents/kingwen-3d-tooling` | 3D generators | Validated (AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md) | **Supported** |
| `kingwen` | `autonomous-ai-agents/kingwen-paper-math-bridge` | Paper-to-math bridge | Validated (research-lead-* series) | **Supported** |
| `kingwen` | `autonomous-ai-agents/kingwen-emotion-voice` | Emotion voice | Validated (kingwen-emotion-voice SKILL.md) | **Supported** |
| `kingwen` | `openjarvis/openjarvis-kingwen-integration` | OpenJarvis integration | Validated (qsmc1-consumer-boundary-audit.md) | **Supported** |
| `kingwen` | `verification/capability-pulse` | Capability pulse verification | Validated (BENCHMARKS_RULES_ONBOARDING_README_AUDIT) | **Supported** |
| `kingwen` | `verification/verification-artifact-hygiene` | Artifact hygiene | Validated (BENCHMARKS_RULES_ONBOARDING_README_AUDIT) | **Supported** |
| `kingwen` | `software-development/verified-engineering` | Verified engineering | Validated (BENCHMARKS_RULES_ONBOARDING_README_AUDIT) | **Supported** |
| `kingwen` | `software-development/systematic-debugging` | Systematic debugging | Validated (BENCHMARKS_RULES_ONBOARDING_README_AUDIT) | **Supported** |
| `kingwen` | `research/pdf-math-extraction-quality` | PDF math extraction | Validated (numerical-extraction-vision-pipeline.md) | **Supported** |
| `kingwen` | `research/multi-engine-math-parsing` | Multi-engine math parsing | Validated (numerical-extraction-vision-pipeline.md) | **Supported** |
| `kingwen` | `research/math-structural-ast-fidelity` | Math AST fidelity | Validated (numerical-extraction-vision-pipeline.md) | **Supported** |
| `kingwen` | `rsmv` | RSMV cache tooling | Validated (cross-verification-checklist-2026-09-01.md) | **Supported** |
| `kingwen` | `autonomous-ai-agents/rsmv-cache-archaeology` | RSMV cache archaeology | Validated (cross-verification-checklist-2026-09-01.md) | **Supported** |
| `kingwen` | `devops/rsmv-cache-crossref` | RSMV cache crossref | Validated (cross-verification-checklist-2026-09-01.md) | **Supported** |
| `kingwen` | `devops/rsmv-model-identity-kit` | RSMV model identity kit | Validated (cross-verification-checklist-2026-09-01.md) | **Supported** |
| `kingwen` | `research/vision-math-symbol-detection` | Vision math symbol detection | Validated (numerical-extraction-vision-pipeline.md) | **Supported** |

### Phantom Reference Classification

| Phantom Target | Count | Proposed Disposition |
|----------------|-------|---------------------|
| airtable | 1 | External tool — document as external reference |
| ascii-video | 1 | External tool — document as external reference |
| audiocraft | 1 | External tool — document as external reference |
| browser | 1 | External tool — document as external reference |
| claude-code | 5 | External tool — document as external reference |
| claude-design | 1 | External tool — document as external reference |
| cloudflare-capability-audit | 2 | External tool — document as external reference |
| dogfood | 2 | External tool — document as external reference |
| github-code-review | 3 | External tool — document as external reference |
| grok | 1 | External tool — document as external reference |
| hermes-agent | 2 | External tool — document as external reference |
| hermes-agent-skill-authoring | 1 | External tool — document as external reference |
| image_gen | 1 | External tool — document as external reference |
| kanban-orchestrator | 1 | External tool — document as external reference |
| notion | 1 | External tool — document as external reference |
| openjarvis-save-string | 1 | External tool — document as external reference |
| pog2-local-build | 1 | Ghost of archived skill — historical artifact |
| powerpoint | 4 | External tool — document as external reference |
| reddit-reading | 2 | External tool — document as external reference |
| rss-feeds | 2 | External tool — document as external reference |
| sovereign-state-agents | 2 | External tool — document as external reference |
| test-driven-development | 3 | External tool — document as external reference |
| verification-rules | 1 | Path mismatch — resolves to `verification/verification-artifact-hygiene` |
| verified-engineering | 1 | Path mismatch — resolves to `software-development/verified-engineering` |
| canonical-table-audit | 1 | Path mismatch — resolves to `verification/canonical-table-audit` |

### Path-Mismatched References (2, fixable)

| Missing Target | Resolves To | Fix |
|----------------|-------------|-----|
| `canonical-table-audit` | `verification/canonical-table-audit` | Update `related_skills` to use full path |
| `verification-rules` | `verification/verification-artifact-hygiene` | Update `related_skills` to use full path |

---

## Summary

- **Documents inventoried:** 166 total Markdown files (1 tracked modified, 63 untracked docs, 102 committed unmodified)
- **Evidence populations:** A (modified tracked), B (newly created untracked), C (unmodified historical)
- **Proposed relationships:** 24 candidate `related_skills` entries for King Wen, all with supporting Markdown evidence
- **Phantom references:** 24 unique phantom targets (26 edges), all classified as external tools (22), ghost of archived skill (1), or path mismatch (3)
- **No changes made:** This inventory is read-only. No files, frontmatter, skill definitions, or graph edges were modified.

**Authorization boundary respected:** Steps 2–6 remain unauthorized. This inventory provides the evidence foundation for future validation-only investigation.