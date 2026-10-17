# PDF Equation-Level Validation Report — v1

**Baseline frozen:** `main@7172dd32d1` (accepted 2026-10-16)
**Validation phase:** v1
**Date:** 2026-10-17
**Status:** Draft — awaiting human reference annotations

---

## 1. Executive Summary

This report presents the equation-level validation of the 4,921 PDF candidate records produced by the King Wen corpus audit (2026-10-16).

**Key results (automated):**
- Total candidate records: 4,921
- Unique source occurrences (paper+page+bbox): 4,921 — every candidate has a unique spatial position
- Unique text keys (paper+page+normalized_text): 2,535
- Extra occurrences beyond first: 2,386 (48.49%)
- Records sharing a repeated key: 3,133 (63.67%)
- Exact duplicate records: 3,128 (63.56%) — all 3,128 also appear in the repeated-key set
- Near-duplicate bbox pairs: 13

**Pending:** Human reference annotations (required for precision and recall estimates).

---

## 2. Validation Context

| Item | Value |
|------|-------|
| Frozen baseline | `main@7172dd32d1` |
| Accepted reconciliation | `PDF_CANDIDATE_RECONCILIATION_2026-10-16.json` |
| Candidate file | `candidate_<paper>.json` (8 files, 4,921 records) |
| Reference equations | `reference_equations.jsonl` (3,409 lines, HTML MathML) |
| Validation artifacts | `DATASETS/validation/` directory |

---

## 3. Automated Uniqueness Metrics

### 3.1 Primary Metrics

| Metric | Value | Share |
|--------|-------|-------|
| Total records | 4,921 | 100% |
| Unique key share | 2,535 | 51.51% |
| Extra occurrences beyond first | 2,386 | 48.49% |
| Records with repeated key | 3,133 | 63.67% |
| Exact duplicate records | 3,128 | 63.56% |
| Near-duplicate bbox pairs | 13 | — |

### 3.2 Corrected Uniqueness Share

**v1 report error:** The earlier statement "51.51% duplicate-record rate" was the unique-key share, not the duplicate share.

**Corrected metrics:**
- Unique-key share = 2,535 / 4,921 = **51.51%** (records that represent a distinct key)
- Extra-occurrence share = 2,386 / 4,921 = **48.49%** (records that are copies beyond the first)
- Records-with-repeated-key = 3,133 / 4,921 = **63.67%** (records in multi-record groups)

### 3.3 Per-Paper Breakdown

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

### 3.4 Interpretation

- **2,386 extra occurrences** are records sharing a (paper, page, normalized text) key with another record — these are duplicates by definition.
- **13 near-duplicate bbox pairs** confirm spatial overlap corroborates the text-key findings.
- **Exact duplicates (3,128)** are records sharing (paper_id, page, line_text, classification, char_count). All 3,128 are also in the repeated-key set (3,133); the 5 extra are records with different classification/char_count but same (paper, page, text).
- **Candidate types:** `true_equation` (121), `inline_math` (3,835), `display_equation` (892), `display_equation` (41), `text_formula` (40), `formula` (9), `equation` (23).

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

## 5. Open Items

| Item | Status | Required To Complete |
|------|--------|----------------------|
| Automated uniqueness audit (v2) | ✅ Done | — |
| Human reference annotations | ⏳ In progress | 420 candidates + full-page inventory |
| Precision estimate | ⏳ Pending | Human annotations (ground_truth field) |
| Recall estimate | ⏳ Pending | Reference annotations (full-page equation inventory) |

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
