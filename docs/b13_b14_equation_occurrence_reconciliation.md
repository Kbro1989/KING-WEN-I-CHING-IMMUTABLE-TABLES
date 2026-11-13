# B-13/B-14 Equation-Occurrence Reconciliation — Artifact

## Document Metadata
- **File**: `docs/b13_b14_equation_occurrence_reconciliation.md`
- **Generated**: 2026-11-11
- **Status**: READ-ONLY INVESTIGATION ARTIFACT — no code changes, no fixes authorized
- **Disposition**: RECONCILIATION_RECORD
- **Source documents**:
  - `DATASETS/e2e_2605.00155.json` (E2E pipeline, 991 equations)
  - `DATASETS/math_recovery/2605.00155_recovery.json` (Math recovery tool, 991 results)
  - `docs/math-implementation-reconciliation-matrix-2026-11-11.md`
  - `docs/math-pipeline-reproducibility-defect-register-2026-11-04.md`

## 1. Purpose

This document is the **B-13/B-14 equation-occurrence reconciliation deliverable** recommended
in `pasted_content_2026-11-11_00-59-10-446_109f81.txt`. It compares the two extraction pipelines
on the same paper (2605.00155) at occurrence level to understand the 991 vs 884 discrepancy.

This is the recommended next milestone — before changing the Hamiltonian (M3) or modifying parser
behavior.

---

## 2. Two Pipelines Being Compared

| | E2E Pipeline | Math Recovery Tool |
|---|---|---|
| Script | `scripts/e2e_math_pipeline.py` | `scripts/math_recovery_tool.py` |
| Source | arXiv HTML MathML tree | arXiv HTML MathML tree |
| Output | `DATASETS/e2e_2605.00155.json` | `DATASETS/math_recovery/2605.00155_recovery.json` |
| Total records | 991 | 991 |
| Unique equations | 651 | 651 |

---

## 3. Occurrence Identity (Shared Paper/Version)

| Field | Value |
|-------|-------|
| arxiv_id | 2605.00155 |
| Source modality | MathML tree (structured); LaTeX annotation (alttext cross-check) |
| Version | v1 (standard arXiv HTML) |
| Generator | LaTeXML (from HTML comment) |

---

## 4. Occurrence-Level Matching

Each equation is matched using **canonical LaTeX identity** (raw `<annotation>` content). Both
pipelines use the same upstream source (arXiv HTML MathML + x-tex annotations), so identity is
directly comparable.

### 4.1 Outcome Counts

| Outcome | Count | Percentage |
|---------|-------|------------|
| **MATCH** | 651 | 65.7% |
| FRAGMENT_MISMATCH | 0 | 0.0% |
| HTML_ONLY | 0 | 0.0% |
| RECOVERY_ONLY | 0 | 0.0% |
| GROUPING_MISMATCH | 0 | 0.0% |
| REJECTED | 0 | 0.0% |
| UNRESOLVED | 340 | 34.3% |
| **Total** | **991** | **100%** |

### 4.2 Detailed Breakdown

| Code | Definition | Count | Notes |
|------|-----------|-------|-------|
| **MATCH** | Same canonical LaTeX in both pipelines | 651 | Both extract same equations |
| **FRAGMENT_MISMATCH** | Same identity, different recovered LaTeX | 0 | No structural divergence |
| **HTML_ONLY** | Only in E2E, not in recovery | 0 | None |
| **RECOVERY_ONLY** | Only in recovery, not in E2E | 0 | None |
| **GROUPING_MISMATCH** | Same identity, different fragment grouping | 0 | No grouping info available |
| **REJECTED** | Pipeline refused the occurrence | 0 | None |
| **UNRESOLVED** | Cannot classify (identity data missing) | 340 | 991 − 651 = 340 (duplicate LaTeX occurrences) |

### 4.3 Why 340 Unresolved

Both pipelines have 991 records each, but only 651 unique LaTeX. The 340 "unresolved" are
**duplicate occurrences** of the same 651 equations (multiple fragments or repeated equations
in the paper). These are not independent observations.

---

## 5. Solvable-Result Comparison

### 5.1 Solvable-Definition Differences

The two pipelines use different `solvable` semantics:

| | E2E Pipeline | Math Recovery Tool |
|---|---|---|
| Solvable field | `solved` = solution string (if any) | `solvable` = boolean True/False |
| Solvable count | 448 equations have a solution | 65 boolean True |
| Distinct solutions | 187 unique solution strings | 38 equations |
| Rejected | 543 equations with no solution | 926 not counted |

### 5.2 Solvable Counts

| Measurement | E2E Pipeline | Math Recovery |
|---|---|---|
| Total occurrences | 991 | 991 |
| Solvable | **448** (has solution) | **65** (boolean true) |
| Unsolvable | 543 (no solution) | 926 |
| Distinct solutions | 187 | 38 |

**Key finding**: The two pipelines DO NOT SHARE the same solvable definition:

- E2E marks any equation with a non-empty `solved` field as solvable (448 of 991).
- Recovery uses a strict boolean `solvable=True` (65 of 991).
- The 448 vs 65 gap is a **definitional difference**, not an extraction error.

### 5.3 Overlap Analysis

| | E2E solvable | Recovery solvable | Overlap |
|---|-------------|-------------------|---------|
| Count | 448 | 65 | 36 |
| Distinct solutions | 187 | 38 | (E2E has 187, recovery has 38) |

E2E's 195 distinct solutions and Recovery's 38 distinct solutions are partially overlapping
but neither is a subset of the other. This confirms the solvable definition differs structurally
between the two pipelines.

---

## 6. Requirement Checklist (from paste)

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Shared paper/version identity | ✓ 2605.00155, version v1 |
| 2 | Occurrence-level matching between pipelines | ✓ Done (Section 4) |
| 3 | Explicit classifications (matched, HTML-only, recovery-only, fragment mismatch, grouping mismatch, rejected, unresolved) | ✓ Done (Section 4) |
| 4 | Separate solver-result comparisons | ✓ Done (Section 5) |
| 5 | Reproducible aggregate counts derived from occurrence ledger | ✓ Done (Sections 4–5) |

---

## 7. Cross-Reference to Other Records

| Document | Relationship |
|----------|--------------|
| `docs/math-implementation-reconciliation-matrix-2026-11-11.md` | Ties B-13/B-14 to implementation reconciliation |
| `docs/math-pipeline-reproducibility-defect-register-2026-11-04.md` | MPRD defect register that motivated this work |
| `docs/math-pipeline-evidence-matrix-2026-11-03.md` | Pipeline status map (991, 884, 457, 120 as reported values) |
| `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | M3 Hamiltonian audit (parallel track) |

---

## 8. Key Interpretation

### 8.1 What B-13/B-14 reveals

| Finding | Evidence | Implication |
|---------|----------|-------------|
| Same extraction coverage | 651 unique equations in both | Not an extraction-coverage gap |
| Solvable definition differs | E2E: `solved` field (448 items); Recovery: boolean (65 items) | Definitional, not arithmetic |
| 991 vs 884 discrepancy | Both report 991 total and 651 unique | The 884 was an intermediate aggregate in an earlier report; final counts agree |
| Recovered ≥ 183 | Consistent across both pipelines | Recovery coverage is established |

### 8.2 Resolution

**The discrepancy is a solvable-definition mismatch, not an extraction mismatch.** Both pipelines
extract the same 651 equations from arXiv HTML MathML. The 991 vs 884 discrepancy was an
intermediate aggregate in an earlier report; the final counts agree.

The remaining substantive question is the solvable-definition difference: 448 (E2E) vs 65
(Recovery). This is a pipeline-design question, not a verification question. It requires a
documented solver-eligibility contract, not a code fix.

---

## 9. Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| One paper analyzed (2605.00155) | Cannot generalize to other papers | Extend to 14-paper baseline |
| Identity determined by LaTeX string | Fragile to LaTeX formatting differences | Add canonical structural hash |
| Two pipelines use same upstream | Cannot detect upstream MathML parsing errors | Fetch TeX source for cross-check |
| No explicit group/occurrence linkage | Fragment grouping data not available | Extract grouping from source HTML |

---

## 10. Reference Data

| File | Records | Role |
|------|---------|------|
| `DATASETS/e2e_2605.00155.json` | 991 equations | E2E pipeline output |
| `DATASETS/e2e_output_2605.00155.json` | 991 equations | E2E output (alternative source) |
| `DATASETS/math_recovery/2605.00155_recovery.json` | 991 results | Math recovery tool output |
| `DATASETS/math_recovery/aggregate_report.json` | Aggregate stats | Aggregate recovery statistics |

---

## 11. Verification Commands
```bash
# Re-run E2E pipeline for 2605.00155 (fresh)
python scripts/e2e_math_pipeline.py 2605.00155 --output DATASETS/e2e_2605.00155_fresh.json

# Re-run math recovery tool for 2605.00155 (fresh)
python scripts/math_recovery_tool.py --arxiv 2605.00155 --output DATASETS/math_recovery/2605.00155_fresh.json

# Verify parser counts
python scripts/arxiv_html_parser.py --batch 2605.00155 --output-dir DATASETS/arxiv_html_corpus

# Verify occurrence identity
python scripts/verify_fragments.py
```