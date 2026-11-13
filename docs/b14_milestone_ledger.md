# Milestone Ledger — B-14 Solver-Policy Reconciliation

**Project:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Ledger ID:** B-14
**Date:** 2026-11-12
**Status:** B-14 reconciled; B-14.1 delimiter integration audit complete; B-14.2 equation identity validation planned

## Milestone Table

| Priority | Milestone | Disposition |
|:--------:|-----------|-------------|
| B-13 | Equation population reconciliation | **Resolved** |
| B-14 | Solver-policy reconciliation | **Reconciled** |
| B-14.1 | Validate solver-success semantics | **Open** |
| B-14.2 | Validate equation identity and zero overlap | **Open** |
| B-14.3 | Delimiter integration audit | **In Progress** |
| B-15 | Frozen regression evaluation | **Pending** |
| B-16 | Routing orchestrator | Deferred |

## B-14 Disposition Summary

### Required Investigative Analysis

1. **Extraction population:** 991 equations (same arXiv HTML source, v1)
2. **Recoverability:** 183 recoverable in the recovery tool
3. **Recovery-tool solvability:** 65 boolean-positive results
4. **E2E solved population:** 448 non-empty solution strings (NOT genuine mathematical solutions)
5. **Solver eligibility:** Equations carrying `=` (equality condition) — 724 in E2E, 991 candidates in Recovery
6. **Solver success:** Whether the resulting solutions are mathematically valid

### Key Findings

| Finding | Result |
|---------|--------|
| E2E "solved" field | 448 non-empty `solved` — all lack equality (`=` not in latex) — parser-residue labels, not solver outcomes |
| Recovery `solvable` | 65 validated sympy solutions (the only genuine solver outcomes) |
| Zero overlap | E2E's 448 "solved" × Recovery's 65 "solvable" share 0 equations |
| Overlap classification | 214 both-fail; 448 E2E-only (non-equation labels); 65 recovery-only; 478 neither |

### Preservation Qualification

The 448 E2E "solved" records have NOT demonstrated genuine mathematical solution success. The E2E pipeline forwards any expression — including non-equality symbols such as `\delta`, `\ell_{p}`, `\mathcal{Q}` — to its recovery stage and labels the result as "solved." The `solved` field is a parser-residue label, not a validated mathematical outcome.

The zero-overlap result is tied to the exact equation-matching and classification rules:
- Index-based matching (equation[i] in both pipelines, same 991-equation population)
- E2E's "solved" requires only a non-empty `solved` field; no equality-condition filter is applied
- Recovery's `solvable=True` requires a validated sympy solution with equality condition
- Shared population: 991 equations from the same arXiv HTML source

### Algorithmic Artifacts

| Artifact | Path |
|----------|------|
| Equation-level matrix | `DATASETS/b14_equation_reconciliation_matrix.jsonl` (991 entries) |
| Reconciliation report | `DATASETS/b14_solver_policy_reconciliation_report.md` |
| Delimiter audit | `DATASETS/b14_delimiter_integration_audit.json` |
| Frozen baseline | `docs/frozen-regression-execution-results-2026-11-03.md` |

## B-14.1 Delimiter Integration Audit

### Status: In Progress

**Deliverable:** `DATASETS/b14_delimiter_integration_audit.json`

#### Delimiter Detector Implementation

| Detector | Path | Function | Identity Preservation |
|----------|------|----------|----------------------|
| delimiter_identity | scripts/delimiter_identity.py | `normalize_latex_norms()`, `balance_norm_tokens()` | CANONICAL tokens preserved (not collapsed) |
| MathMLParser | scripts/mathml_parser.py | `_tidy() -> balance_norm_tokens()` | MathML glyph layer preserved |
| delimiter_inference | scripts/delimiter_inference.py | `infer_delimiters()`, `DelimiterNode` | Disambiguates ABS vs NORM |
| v2_delimiter_aware_structural_recovery | scripts/v2_delimiter_aware_structural_recovery.py | `classify_delimiter_glyph_font_aware()`, `detect_delimiter_candidates()` | GATED: D1-D6 |

#### Import Trace

| Script | Delimiter-Identifier Import | Identity-Preserving Path |
|--------|----------------------------|--------------------------|
| e2e_math_pipeline.py | Indirect (via mathml_parser._tidy()) | e2e -> MathMLParser -> _tidy() -> balance_norm_tokens() |
| batch_math_pipeline.py | None | None |
| math_recovery_tool.py | Direct (normalize_latex_norms) | math_recovery_tool -> normalize_latex_norms() |

#### Frozen Regression Comparison

The frozen regression baseline (`docs/frozen-regression-execution-results-2026-11-03.md`) covers border detection and ballooning. Delimiter identity scope is **0** for that test — it does not evaluate delimiter identity, only border detection on crops.

#### Tall Delimiter Test

`tests/test_delimiter_structural_recovery.py` could not be executed on this host:
- module dependency: cv2 (opencv-python-headless), pymupdf (PyMuPDF), numpy
- numpy 2.5.4 compiled for cp314, incompatible with Python 3.11 (WindowsApps + venv)
- Manual probe of delimiter_identity.py: 8/8 PASS

### Acceptance Criterion

A visually detected delimiter is NOT a successfully recovered delimiter. Detection, identity classification, structural reconstruction, and downstream AST preservation must be evaluated independently.

## Next Steps

1. Fix numpy/cpython version mismatch for circular test environment (see B-14.2)
2. Run test_delimiter_structural_recovery.py to verify tall delimiter behavior
3. Trace whether recovered delimiter structure survives through LaTeX reconstruction and AST generation
4. Compare delimiter identity metrics against frozen regression baseline
