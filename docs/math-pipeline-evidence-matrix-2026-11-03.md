# Math Extraction & Recovery Pipeline — Evidence Matrix

**Date:** 2026-11-03
**Repository:** Kbro1989/KING-WEN-I-CHING-IMMUTABLE-TABLES
**Scope:** Math extraction and recovery pipeline ONLY — separate from King Wen integration
**Status:** Read-only. No code modifications. No baselines disturbed.
**Overall disposition:** Research-grade / not production-validated

---

## Pipeline Status Definitions

| Status | Meaning |
|---|---|
| EXTRACTED | An equation occurrence was identified in the source. |
| PARSED | Its mathematical representation was successfully constructed. |
| RECOVERED | A usable representation was reconstructed from incomplete or damaged source material. |
| SOLVABLE | A solver produced a result under a specified solving policy. |
| VALIDATED | The result passed an independent correctness or structural verification. |
| PRESERVED | The original occurrence, representation, source location, and transformation history remain traceable. |

These are NOT interchangeable. A system reporting 457 SOLVABLE does not establish 457 VALIDATED.

---

## Workstream A: Source Extraction Integrity

| ID | Finding | Source Artifact | Measured Population | Verification Method | Status | Acceptance Requirement |
|---|---|---|---|---|---|---|
| A-01 | Arxiv HTML corpus exists with 241 papers, 72,478 equations | DATASETS/arxiv_html_corpus/*.json | 241 papers, 72,478 equations | Counted all equation entries | VERIFIED | Corpus count must be reproducible by independent script |
| A-02 | 99.9% of equations have MathML | Same as A-01 | 72,414 / 72,478 = 99.9% | Field presence check on mathml key | VERIFIED | MathML presence rate must be >= 99% for corpus to be usable |
| A-03 | 100% of equations have LaTeX (with 22 None) | Same as A-01 | 72,456 / 72,478 = 100.0% (22 None) | Field presence check on latex key | VERIFIED (caveat) | 22 equations have latex: None — these crash the pipeline |
| A-04 | 70.1% of equations have context | Same as A-01 | 50,791 / 72,478 = 70.1% | Field presence check on context_before/after | VERIFIED | Context coverage must be >= 70% for contextual solving |
| A-05 | 22 equations have latex: None | Same as A-01 | 5 of 241 papers affected | eq.get('latex') is None filter | VERIFIED (bug) | Must be handled gracefully — currently crashes pipeline |
| A-06 | Null-LaTeX crash in learn_dictionary() | scripts/math_recovery_tool.py:246 | 5 papers | re.finditer on None raises TypeError | VERIFIED (bug confirmed) | Fix: skip None latex equations |
| A-07 | PyMuPDF baseline extraction exists | DATASETS/math_extraction_zotero_full.json | 245 papers, 16,693 expressions | JSON file exists | VERIFIED (exists) | Quality assessment not performed |
| A-08 | No test for arxiv HTML parser correctness | scripts/arxiv_html_parser.py | N/A | No test file exists | UNTESTED | Need cross-examination: raw math tag count vs parsed equation count |
| A-09 | No test for PyMuPDF extraction quality | scripts/semantic_math_extractor.py | 16,693 expressions | No test file exists | UNTESTED | Need independent per-expression validation |

---

---

## Dependency Edge Classification (2026-11-11)

Dependency edges are labeled by evidence type:

| Edge | Label | Evidence |
|------|-------|----------|
| arxiv_html_parser -> mathml_parser | declared_dependency | arxiv_html_parser imports mathml_parser.extract_from_html |
| mathml_parser -> math_recovery_tool | declared_dependency | mathml_parser tokens used by recovery |
| math_recovery_tool -> delimiter_identity | declared_dependency | delimiter_identity imported for token normalization |
| targeted_math_detector -> v2_delimiter_aware_structural_recovery | declared_dependency | Interface documented; no runtime caller confirmed |
| delimiter_aware_structural_recovery -> evaluate_cross_paper_v2_strict | verified_runtime_dependency | Caller verified at evaluate_cross_paper_v2_strict.py:55 |
| math_contract -> math_reconstruction_evidence | declared_dependency | Import verified |
| math_contract -> cross_stage_drop_trace | declared_dependency | Import verified |
| semantic_honesty_scoreboard -> solve_all / solve_dual_path | proposed_integration | Shared call path not yet established |

## Workstream B: Mathematical Reconstruction

| ID | Finding | Source Artifact | Measured Population | Verification Method | Status | Acceptance Requirement |
|---|---|---|---|---|---|---|
| B-01 | Delimiter identity preservation | scripts/delimiter_identity.py | 38 tests pass | pytest tests/test_delimiter_identity.py | TESTED (component) | Must be verified on every equation, not just test cases |
| B-02 | Delimiter adversarial tests | scripts/delimiter_inference.py | 26 tests pass | pytest tests/test_delimiter_adversarial.py | TESTED (component) | Adversarial cases must cover all delimiter types in corpus |
| B-03 | AST construction from MathML | scripts/mathml_parser.py | 17 structural fidelity tests pass | pytest tests/test_structural_fidelity.py | TESTED (component) | Structural fidelity must be verified on full corpus |
| B-04 | Semantic fidelity (AST persistence) | scripts/math_recovery_tool.py | 17 regression tests pass | pytest tests/test_semantic_fidelity_regression.py | TESTED (component) | Semantic fidelity must be verified on full corpus |
| B-05 | Semantic fidelity scoring | scripts/math_recovery_tool.py | 7 tests pass | pytest tests/test_semantic_fidelity_scoring.py | TESTED (component) | Scoring must be applied to all equations |
| B-06 | Math contract validation | scripts/math_contract.py | 4 tests pass | pytest tests/test_math_contract_status.py | TESTED (component) | Contract must be enforced on all pipeline outputs |
| B-07 | Occurrence accounting | scripts/math_occurrence_accounting.py | 12 tests pass | pytest tests/test_occurrence_accounting.py | TESTED (component) | Occurrence identity must be verified on full corpus |
| B-08 | Math recovery tool (full corpus) | scripts/math_recovery_tool.py | 15 papers, 3,491 equations | Manual run on 241-paper corpus | INCOMPLETE | Only 15 of 241 papers have recovery data |
| B-09 | Math recovery tool crashes on None latex | scripts/math_recovery_tool.py:246 | 5 papers affected | Confirmed by running tool on corpus | BUG | Fix required before full-corpus run |
| B-10 | Recovery coverage: 15.6% recoverable | DATASETS/math_recovery/*_recovery.json | 543/3,491 = 15.6% | Count from 15 recovery files | MEASURED | Population is 15 papers only — not generalizable |
| B-11 | Recovery coverage: 6.8% solvable | Same as B-10 | 237/3,491 = 6.8% | Count from 15 recovery files | MEASURED | Solvable = SymPy produces a result, not validated for correctness |
| B-12 | E2E pipeline (single paper) | scripts/e2e_math_pipeline.py | 2605.00155: 991 eqs, 457 solvable (45.9%) | Manual run | RUNS (no test) | No test exists; solvable definition differs from math recovery tool |
| B-13 | Discrepancy: 991 vs 884 equations | E2E vs math recovery tool | Same paper, different counts | Side-by-side comparison | UNRESOLVED | Need to determine which extraction is correct and why they differ |
| B-14 | Discrepancy: 457 vs 120 solvable | E2E vs math recovery tool | Same paper, different solvable counts | Side-by-side comparison | UNRESOLVED | Different solving policies — must be documented before either number is canonical |
| B-15 | No test for e2e pipeline | scripts/e2e_math_pipeline.py | N/A | No test file exists | UNTESTED | Need integration test covering full pipeline on at least one paper |

---



### Capability Attribution (C1-C11) — added 2026-11-11

| # | Capability | Tool | Input | Output | Status |
|---|-----------|------|-------|--------|--------|
| C1 | MathML extraction | mathml_parser.py | MathML + x-tex | ExprNode tree | CONFIRMED |
| C2 | LaTeX reconstruction | math_recovery_tool.py | MathML, gold, LaTeX | Reconstructed LaTeX | CONFIRMED |
| C3 | Structural recovery V1 | delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | CONFIRMED caller |
| C4 | Structural recovery V2 | v2_delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | DECLARATION only |
| C5 | AST extraction | structural_ast_extractor.py | MathML tree | ExprNode tree | NOT_TESTED |
| C6 | Visual detection | targeted_math_detector.py, vision_math_extractor.py | PDF page rawdict | Bbox, candidates | CONFIRMED CLI |
| C7 | OCR | Pix2Text, Tesseract (Lua doc only) | PDF image/crop | Char/text | n/a - Lua doc |
| C8 | Semantic validation | math_contract.py, semantic_honesty_scoreboard.py | Recovered math tree | Validation status | PARTIAL |
| C9 | Equation solving | solve_all.py, solve_dual_path.py | Recovered IR | Solution | PARTIAL |
| C10 | Geometric validation | test_geometry_generalization.py | Geometry ops | Pass/fail | NOT_TESTED |
| C11 | Provenance tracing | verify_provenance_trace.py | Artifact + trace | Verification result | n/a - not executed |

### JSON / PNG / PDF / HTML Usage Pointers (tagged items, re-examined)

| Tagged item | Related artifacts | Capability | Status | Evidence source |
|-------------|-------------------|------------|--------|-----------------|
| MPRD-001 | math_contract.py:300 source_hash, math_reconstruction_evidence.py:761 | C2 | OPEN - None mathml crash | math_reconstruction_evidence.py:761 TypeError |
| MPRD-003 | structural_survival.py, structural_survival.jsonl | C4 | OPEN - baseline staleness | Structural survival baseline revision not identified |
| MPRD-004 | pix2text_harvest, audit_candidate_crops | C6 | OPEN - bbox list-vs-dict mismatch | 2 consumers, schema inconsistent |
| MPRD-005 | test_canonical_extraction.py | C8 | OPEN - PYEOF leak | Code hygiene not applied |
| MPRD-006 | arxiv_html_corpus/*.json (240 files) | C1 | OPEN - network dependency | 51.6 MB, must re-download |
| MPRD-007 | semantic_math_zotero_full.json (159.2 MB) | C1, C2 | Verified | 14 content consumers, regenerable |
| math_reconstruction_evidence.jsonl | DATASETS/math_reconstruction_evidence.jsonl (8.1 MB) | C2 | OPEN - consumers crash | 2 consumers at crash point |
| structural_survival.jsonl | DATASETS/structural_survival.jsonl (6.5 MB) | C4 | OPEN - baseline unknown | Baseline revision unverified |
| cross_stage_drop_trace.jsonl | DATASETS/cross_stage_drop_trace.jsonl (2.2 MB) | C11 | OPEN - crash on None | math_contract.py:300 crash |
| arxiv_html_corpus/2605.00155.json | DATASETS/arxiv_html_corpus/2605.00155.json (1.1 MB) | C1 | OPEN - needs args | arxiv_provenance.py requires args |
| structural_preservation/*.json | 83 files, 9.2 MB | C4 | n/a - visual domain | 370/370 empty consumers per manifest |
| vision_comparison/*.jsonl | 113 files, 11.5 MB | C6, C10 | Verified | No changes needed |

## Key Findings Retention (2026-11-04 — updated with capability tags)

1. **281.0 MB across 495 tracked JSON/JSONL files** are generated math-paper outputs.
2. **42 files** have content-consuming dependencies (scripts open/read them directly).
3. **450 files** have no script references (by-name-only or unreferenced).
4. **237 of 240** arxiv_html_corpus files have no script references - pure parse output.
5. **14 of 15** math_recovery version directories contain identical copies of the same
   15 papers (v3-v16), representing ~12x duplication of recovery output.
6. Largest single file: semantic_math_zotero_full.json (159.2 MB) - extracted math
   from 245 Zotero papers.
7. **Capability coverage:** 11 capabilities C1-C11 defined; 3 CONFIRMED, 4 PARTIAL,
   2 DECLARATION, 2 NOT_TESTED, 2 n/a (Lua doc only), 2 OPEN (crash), 1 OPEN (network).





## Candidate Test Qualification Criteria (2026-11-11)

Each test script in the pipeline must be qualified before being treated as
an oracle. The following six criteria are enforced:

| # | Criterion | How to verify |
|---|----------|---------------|
| 1 | Expected result comes from independently adjudicated evidence | Cross-check test expected values against gold corpus (GS-001 through GS-005), not test-authored values |
| 2 | Fixtures do not leak the evaluator's answer into candidate generation | Audit test fixtures for unintended information flow |
| 3 | Assertions test the stated capability rather than merely successful execution | Read each assertion; verify it validates capability-specific behavior, not just that the function returned |
| 4 | Meaningful negative controls present | Test fails on malformed input (e.g., broken MathML, unrecoverable LaTeX) |
| 5 | Actually runs against intended corpus or bounded population | Execute test and record pass/fail counts; do not infer from test existence |
| 6 | Does not share implementation defect with the system being evaluated | Independent implementation required for oracle status |

### Application to current candidate tests

| Test script | Cap | Criterion 3 | Criterion 4 | Verdict |
|------------|-----|-------------|-------------|---------|
| test_structural_conservation.py | C1, C4 | Unknown | Unknown | NOT READY |
| test_semantic_fidelity.py | C8 | Unknown | Unknown | NOT READY |
| test_provenance_corruption.py | C11 | Unknown | Unknown | NOT READY |
| test_geometry_generalization.py | C10 | Unknown | Unknown | NOT READY |
| test_adversarial_clearance_gate.py | C10 | Unknown | Unknown | NOT READY |
| test_mathml_parser_on_corpus.py | C1 | Unknown | Unknown | NOT READY |
| test_nested_args.py | C2 | Unknown | Unknown | NOT READY |
| test_mbox_dollar_recovery.py | C2 | Unknown | Unknown | NOT READY |
| test_relation_identity.py | C2 | Unknown | Unknown | NOT READY |
| test_structural_survival.py | C4 | Unknown | Unknown | NOT READY |

**All 10 tests remain CANDIDATES until their assertions are read, fixtures
audited, and negative controls added. A passing test is not yet an oracle.**

## Workstream C: Solving and Validation

| ID | Finding | Source Artifact | Measured Population | Verification Method | Status | Acceptance Requirement |
|---|---|---|---|---|---|---|
| C-01 | SymPy solving works (single equations) | scripts/math_recovery_tool.py | 237 solvable across 15 papers | Tool output | FUNCTIONAL | Solving must be validated for mathematical correctness, not just parse success |
| C-02 | FALSE_RECOVERY = 0 (tree path) | DATASETS/math_failure_corpus.jsonl | 3,409 equations (14-paper baseline) | scripts/semantic_honesty_scoreboard.py | VERIFIED (on baseline) | FALSE_RECOVERY must be verified on full 241-paper corpus |
| C-03 | Structural conservation (17/17 tests) | scripts/test_structural_conservation.py | 17 test cases | pytest | TESTED (component) | Conservation must be verified on all extracted equations |
| C-04 | Semantic honesty scoreboard | scripts/semantic_honesty_scoreboard.py | 3,409 equations (14-paper baseline) | Manual run | RUNS (no test) | Must be run on full corpus; currently only 14-paper baseline |
| C-05 | Trivial vs nontrivial solutions | DATASETS/math_recovery/*_recovery.json | 237 solvable: 57 trivial, 63 nontrivial (from 2605.00155 run) | Tool output | MEASURED | Distinction must be preserved in all downstream artifacts |
| C-06 | No independent correctness validation | All solving outputs | N/A | No independent checker exists | MISSING | Need a checker that validates solved results against source equations |
| C-07 | ANTLR version conflict (4.9.3 vs 4.7.2) | Environment | latex2sympy2 requires 4.7.2, sympy requires >= 4.11 | Import test | ENVIRONMENT ISSUE | Two Python environments needed; latex2sympy2 scripts are import-broken by design in SymPy environment |

---

## Workstream D: Corpus Reconciliation

| ID | Finding | Source Artifact | Measured Population | Verification Method | Status | Acceptance Requirement |
|---|---|---|---|---|---|---|
| D-01 | Reconciliation test (2 failures) | tests/test_reconciliation.py | 14-paper baseline (3,409 equations) | pytest tests/test_reconciliation.py | 2 FAILING | 69,069 missing occurrences — scope mismatch between 14-paper baseline and 72,478-equation corpus |
| D-02 | Reconciliation scope mismatch | DATASETS/equation_count_reconciliation.json | 14 papers vs 241 papers | Compare reconciliation report to corpus | IDENTIFIED | Reconciliation must either cover full corpus or explicitly scope to 14-paper baseline |
| D-03 | Equation count reconciliation (14 papers) | DATASETS/equation_count_reconciliation.json | 14 papers, 3,409 equations | python tests/test_equation_reconciliation.py (script) | PASSES | 3,266 recovered (95.8%), 228 solvable (6.7%), 143 unresolved (4.2%) |
| D-04 | Occurrence accounting (P3) | scripts/math_occurrence_accounting.py | 9-point checklist | pytest tests/test_occurrence_accounting.py | 12 TESTS PASS | Occurrence identity must be verified on full corpus |
| D-05 | No duplicate detection | All extraction outputs | N/A | No test exists | MISSING | Need duplicate detection across papers (same equation in multiple papers) |
| D-06 | PDF vs HTML comparison | DATASETS/math_extraction_zotero_full.json (PyMuPDF) vs DATASETS/arxiv_html_corpus/ (HTML) | 245 papers (PDF) vs 241 papers (HTML) | Manual comparison | NOT PERFORMED | PyMuPDF and HTML extraction have different source characteristics — must be assessed independently |
| D-07 | 15 of 241 papers have recovery data | DATASETS/math_recovery/*_recovery.json | 15/241 = 6.2% | File count | MEASURED | Coverage gap must be closed or explicitly scoped |

---

## Workstream E: Downstream Preservation and Integration

| ID | Finding | Source Artifact | Measured Population | Verification Method | Status | Acceptance Requirement |
|---|---|---|---|---|---|---|
| E-01 | Equation-level provenance not connected to King Wen | scripts/recover_training_data.py | 82,224 training records | Manual code review | NOT CONNECTED | Math extraction occurrence identities never referenced by training data generator |
| E-02 | bridge_math_diagram_extractor.py (only bridge calling King Wen) | scripts/bridge_math_diagram_extractor.py | 128 lines | grep -rl bridge_math_diagram_extractor | PARTIAL | Has synthetic fallback when external extractor output is missing |
| E-03 | math_to_kingwen_adapter.py (CLI-only, never called) | scripts/math_to_kingwen_adapter.py | N/A | grep -rl math_to_kingwen_adapter returns 0 callers | INACTIVE | Experimental single-equation adapter; never tested in pipeline context |
| E-04 | 8 additional bridge/adapter/registry candidates | Various scripts | 7 files | grep -rl returns 0 callers for most | UNCLASSIFIED | Need execution map, data-flow map, and provenance map for each |
| E-05 | 6.8GB training corpus has no equation provenance | kingwen_train_data/full_shotgun_expansion_verified.jsonl | 82,224 records | File inspection | VERIFIED | Only paper text hash (16 chars) and 500-char source_text_span — no equation IDs |
| E-06 | Four-layer architecture proposed | Reviewer response (pasted_content_2026-11-03_22-08-27-620_b02dc8.txt) | N/A | Documentation only | PROPOSED | Not yet implemented; design only |
| E-07 | Four-layer architecture not implemented | N/A | N/A | No implementation exists | NOT IMPLEMENTED | Requires user authorization before implementation |

---

## Summary of Pipeline State

### What Works (Component-Level)

| Component | Tests | Pass | Coverage |
|---|---|---|---|
| Delimiter identity | 38 | 38 | Component only |
| Delimiter adversarial | 26 | 26 | Component only |
| Math contract validation | 4 | 4 | Component only |
| Occurrence accounting | 12 | 12 | Component only |
| Semantic fidelity regression | 17 | 17 | Component only |
| Semantic fidelity scoring | 7 | 7 | Component only |
| Structural fidelity | 16 | 16 | Component only |
| Reconciliation (equation counts) | 1 (script) | 1 | 14-paper baseline |
| Total | 121 | 121 | Component only |

### What Fails

| Test | Failure | Root Cause |
|---|---|---|
| tests/test_reconciliation.py::test_reconciliation_explains_every_difference | 69,069 missing | Scope mismatch: 14-paper baseline vs 72,478-equation corpus |
| tests/test_reconciliation.py::test_recovery_covers_source_exactly | 69,069 missing | Same scope mismatch |

### What Is Untested

| Pipeline Stage | Test Exists? | Notes |
|---|---|---|
| Arxiv HTML parser correctness | No | Cross-examination pattern established but not automated |
| PyMuPDF extraction quality | No | 16,693 expressions with no quality assessment |
| E2E math pipeline | No | Runs but produces inconsistent results vs math recovery tool |
| Math recovery tool (full corpus) | No | Only 15 of 241 papers processed |
| Null-LaTeX handling | No | 22 equations crash the pipeline |
| Cross-tool consistency | No | E2E says 457 solvable, math recovery says 120 for same paper |
| Equation-level provenance | No | Not connected to training data |
| Full-corpus FALSE_RECOVERY | No | Only verified on 14-paper baseline |

### What Is Missing for Production

1. Consistent solving policy — Two tools produce different solvable counts (457 vs 120) for the same paper. Need a single canonical solving approach with documented acceptance rules.
2. Full-corpus coverage — Only 15 of 241 papers have recovery data. Need to process all 241 papers.
3. Null-safety — 22 equations with latex: None crash the pipeline.
4. End-to-end pipeline test — No test verifies the full extraction to parsing to recovery to solving to preservation flow.
5. Equation-level provenance — Math extraction occurrence identities are not connected to King Wen training data.
6. Independent correctness validation — Solving produces results but no independent checker validates them.
7. PDF vs HTML comparison — PyMuPDF and HTML extraction have different source characteristics; must be assessed independently.

### Overall Disposition

Research-grade / not production-validated.

The pipeline demonstrates functional extraction, reconstruction, and solving capabilities across several independently tested components. It does not yet demonstrate consistent end-to-end mathematical fidelity, full-corpus recovery coverage, or complete occurrence-level provenance.

This assessment is separate from King Wen integration claims. The math extraction pipeline and the King Wen state machine are distinct systems that intersect at provenance and downstream consumption, but they have different failure modes and acceptance criteria.

This document is read-only. No code was modified, no baselines were disturbed, no commits were made.
