# PDF Equation-Level Validation Report — v1

**Baseline frozen:** `main@7172dd32d1` (accepted 2026-10-16)
**Validation phase:** v1
**Date:** 2026-10-17
**Status:** Draft — awaiting human reference annotations

---

## 1. Executive Summary

This report presents the equation-level validation of the 4,921 PDF candidate records produced by the King Wen corpus audit (2026-10-16).

**Key results pending:**
- Human reference annotations (required for precision and recall)
- Automated uniqueness audit (completed)
- Precision estimate (0/420 human-verified → pending)
- Recall estimate (0/4,921 reference-annotated → pending)

The accepted reconciliation baseline (3,559 → 4,921 transition) is unchanged and remains authoritative for count documentation.

---

## 2. Validation Context

| Item | Value |
|------|-------|
| Frozen baseline | `main@7172dd32d1` |
| Accepted reconciliation | `PDF_CANDIDATE_RECONCILIATION_2026-10-16.json` |
| Candidate file | `candidates_<paper>.json` (8 files, 4,921 records) |
| Reference equations | `reference_equations.jsonl` (3,409 lines, HTML MathML) |
| Validation artifacts | `DATASETS/validation/` directory |

---

## 3. Automated Uniqueness Audit (Completed)

### 3.1 Metrics

| Metric | Value |
|--------|-------|
| Total candidate records | 4,921 |
| Unique line keys | 2,535 |
| Duplicate records | 2,386 |
| Fraction unique | 51.51% |

### 3.2 Per-Paper Breakdown

| Paper | Candidates | Unique Keys | Fraction Unique |
|-------|-----------|-------------|-----------------|
| 1907.04931 | 195 | 107 | 54.9% |
| 2104.01277 | 2,715 | 1,673 | 61.6% |
| 2205.01395 | 9 | 9 | 100.0% |
| 2206.00364 | 1,934 | 716 | 37.0% |
| 2305.08038 | 0 | 0 | N/A |
| 2602.15881 | 0 | 0 | N/A |
| 2605.22902 | 31 | 12 | 38.7% |
| 2605.27315 | 37 | 18 | 48.6% |

### 3.3 Interpretation
- **2,386 duplicates** are records sharing identical (paper_id, page, normalized_line_text). These may reflect:
  - Same expression appearing multiple times on the same page
  - OCR repeated text artifacts
  - Repeated patterns (e.g., equation templates)
- **Uniqueness varies by paper** — 2206.00364 has the lowest fraction (37.0%), suggesting many repeated patterns or heavier OCR artifacts.

### 3.4 Notes
- Automated classifier marks: 1,982 `true_positive`, 1,877 `false_positive`, 1,062 `uncertain`
- These are **provisional** and require human verification
- Spatial overlap: checked via (page, bbox) matching, 0 spatial duplicate groups

---

## 4. Human Reference Annotations (In Progress)

**Status:** 0/4,921 records annotated.

### 4.1 Sample Design (Precision Pathway)
- **Target sample size:** 420 records (stratified by paper)
- **Selection method:** Stratified sampling proportional to candidate count
- **Confidence interval:** 95% CI ±4.5% (Wilson score)

### 4.2 Human Annotation File
- `PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl`
- Schema: `annotation_id`, `candidate_id`, `ground_truth`, `annotation_notes`

### 4.3 Expected Outcomes
- Precision = TP / (TP + FP) from human annotations
- 95% Wilson CI for precision
- Unresolved count reported separately

---

## 5. Open Items (Not Yet Completed)

| Item | Status | Required To Complete |
|------|--------|----------------------|
| Automated uniqueness audit | ✅ Done | — |
| Human reference annotations | ⏳ In progress | Human review of 420 candidates + 4,921 reference pages |
| Precision estimate | ⏳ Pending | Human annotations (ground_truth field) |
| Recall estimate | ⏳ Pending | Reference annotations (full-page equation inventory) |
| Sample size documentation | ✅ Done | Documented in Section 4.1 |
| Confidence intervals | ⏳ Pending | Compute from annotation results |

---

## 6. Provenance Chain

```
DATASETS/candidates_<paper>.json (accepted baseline, 4,921 records)
  → PDF_CANDIDATE_UNIQUENESS_AUDIT_v1_2026-10-17.json (automated uniqueness)
  → PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl (human annotation)
  → PDF_EQUATION_LEVEL_VALIDATION_REPORT_v1_2026-10-17.md (final metrics)
```

---

## 7. Acceptance Criteria and Completion Gates

| Gate | Current | Required |
|------|---------|----------|
| Baseline unchanged | ✅ `7172dd32d1` verified | — |
| Sample size documented | ✅ n=420 | — |
| Human annotations filed | ⏳ 0/4,921 | 420+ human-verified records |
| Precision published | ⏳ Pending | TP/(TP+FP) with 95% CI |
| Recall published | ⏳ Pending | reference_hits confirmed |
| Unresolved cases reported | ⏳ 0 | All unresolved cases explicitly counted |

---

## 8. Next Steps

1. **Human annotation** — reviewer opens PDF pages, classifies each sampled record
2. **Precision computation** — TP/(TP+FP) with 95% Wilson CI
3. **Recall computation** — reference_hits confirmed with full-page inventory
4. **Version 2 report** — compute and publish metrics once annotations complete
5. **Versioning** — new, versioned report with reference to v1 baseline

---

*This report is a draft. Metrics will be finalized when human reference annotations are complete.*
