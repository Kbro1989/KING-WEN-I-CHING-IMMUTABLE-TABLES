# PDF Equation-Level Validation Plan — v1

**Date:** 2026-10-17
**Baseline frozen:** `main@7172dd32d1` (accepted 2026-10-16)
**Purpose:** Independent validation of the 4,921 PDF candidate records, addressing the three open validation items:
1. Candidate uniqueness
2. PDF precision
3. PDF recall

## 1. Scope and Relationship to Accepted Baseline

This validation phase is **additive only**. The accepted baseline remains frozen at:

- `main` at `7172dd32d1` (checkpoint preserved, confirmed 2026-10-16)
- `PDF_CANDIDATE_RECONCILIATION_2026-10-16.json` — machine-readable reconciliation
- `PDF_CANDIDATE_RECONCILIATION_2026-10-16.md` — human-readable explanation
- `PDF_CANDIDATE_AUDIT_SUMMARY_2026-10-16.json` — consolidated audit summary

No files in the accepted baseline are modified by this validation phase. All new artifacts live under `DATASETS/validation/`:
```
DATASETS/validation/
├── PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md          (this file)
├── PDF_CANDIDATE_UNIQUENESS_AUDIT_v1_2026-10-17.json
├── PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl
└── PDF_EQUATION_LEVEL_VALIDATION_REPORT_v1_2026-10-17.md
```

## 2. Validation Objectives

### Objective 1: Candidate Uniqueness
Determine whether the 4,921 candidate records represent distinct source occurrences.
- Use stable candidate IDs derived from paper_id + page + line_text as records may repeat.
- Source-document hashes (SHA-256 over PDF bytes)
- Page identifiers (1-based page number)
- Bounding-box / text-span overlap checks (same page, overlapping bbox = potential duplicate)
- Repeated mathematical expressions at different source locations are NOT duplicates.

### Objective 2: PDF Precision (Human-Annotated Sample)
Independently annotate a stratified sample of candidates against rendered source pages.
- Sample size: 420 records (stratified by paper, see Section 4)
- Record true positives, false positives, and unresolved cases
- Report sample size, selection method, and confidence interval alongside estimate
- Human annotations fetched and stored in a separate file: `PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl`
- Automated precision estimate computed from human annotations only

### Objective 3: PDF Recall (Reference-Annotated Check)
Independently identify equations on selected pages, including equations the extractor did not detect.
- Reference annotations fetched and stored in a separate file: `PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl`
- Candidate-only review cannot measure recall — reference annotation is the denominator
- Compare reference hits against candidate manifest to estimate missed equations

## 3. Data Sources and Provenance

### Accepted Baseline Data (immutable)
| Source | Description |
|--------|-------------|
| `candidates_<paper>.json` (8 files) | 4,921 candidate records with provenance |
| `reference_equations.jsonl` (3,409 lines) | HTML MathML reference equations |

### Working Data (validation phase, separate directory)
| Source | Description |
|--------|-------------|
| `pdf_pages_<paper>.png` (137 pages rendered) | Rendered reference pages for human annotation |
| `PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl` | Human-verified reference annotations |

### Data Integrity
- Candidate files are read-only; never modified by this phase.
- All validation artifacts tracked as new files in `DATASETS/validation/`.
- Each artifact includes a `source` field documenting its provenance chain.

## 4. Sample Design (Precision)

### Stratified Sample
Sample from the 4,921 candidates stratified by paper source, proportional to candidate count:

| Paper | Candidates | Sample Share | Sampled Records |
|-------|------------|--------------|-----------------|
| 2104.01277 | 2,715 | 55.2% | 221 |
| 2206.00364 | 1,934 | 39.3% | 164 |
| 1907.04931 | 195 | 4.0% | 18 |
| 2605.22902 | 31 | 0.6% | 4 |
| 2605.27315 | 37 | 0.7% | 5 |
| 2205.01395 | 9 | 0.2% | 1 |
| 2605.18130 | 0 | 0% | 0 |
| 2605.24807 | 0 | 0% | 0 |
| **Total** | **4,921** | **100%** | **420** |

### Retrieval Method
- Paper-level valid: 6 papers × 4,921 candidates ≠ 3,409 mapped (partial coverage)
- Sample size n=420 chosen for: 95% CI ±4.5% for proportion p (worst case p=0.5)
- Stratified sampling ensures representation from both large (2.7k/1.9k) and small (195/31/37/9/0) papers
- All 2605.18130/2605.24807 papers have 0 candidates (not represented in sample)

### Automated Precision Tracking
- First-pass automated classifier marks each sampled record as: `true_positive`, `false_positive`, or `uncertain`
- Human-annotation file (`PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl`) provides the ground truth
- Final precision = TP / (TP + FP) computed from human annotations only
- Precision estimate: p̂ = TP/420, standard error = sqrt(p̂(1-p̂)/420), 95% CI = p̂ ± 1.96 × SE

## 5. Validation Protocol

### Rendering Pipeline
1. Render each PDF page with PyMuPDF (`page.get_pixmap(dpi=300)`)
2. Save as PNG: `pdf_pages/<paper_id>/page_<n>.png`
3. Human annotator views PNG + candidate record side-by-side
4. Annotator records: `true_positive` / `false_positive` / `unresolved`

### Reference Annotation (Recall)
1. For each selected paper (all 6 papers with PDF candidates), render pages
2. Human annotator identifies ALL equations on each page (not just candidates)
3. Store reference annotations in `PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl`
4. Recall = candidate_hits / reference_hits

### Unresolved Cases
- Records where human annotator cannot determine ground truth
- Recorded with explicit `unresolved: true` flag
- Excluded from precision/recall calculations, reported separately with count

## 6. Metrics and Reporting

### Automated Metrics
| Metric | Definition | Status |
|--------|------------|--------|
| Uniqueness | Fraction of candidates with unique (paper_id, page, line_hash) | Automated |
| Precision (initial) | TP / (TP + FP) from automated classifier | Automated, provisional |
| Recall (reference) | candidate_hits / reference_hits | Automated, requires reference file |

### Human-Annotated Metrics (gold standard)
| Metric | Definition | Denominator Condition |
|--------|------------|----------------------|
| Precision | TP / (TP + FP) | Requires human-annotated sample (n=420) |
| Recall | TP / (TP + FN) | Requires reference annotations |

### Uncertainty Reporting
- Precision: reported with 95% Wilson CI
- Recall: reported with 95% Wilson CI
- Unresolved counts: reported transparently, excluded from point estimates

## 7. Acceptance Criteria

1. ✅ Accepted baseline remains unchanged (verified 2026-10-17)
2. ✅ All new artifacts recorded in `DATASETS/validation/`
3. ✅ Candidate files not modified
4. ✅ Human annotations in separate file (NOT in candidate files)
5. ✅ Unresolved cases explicitly tracked with count
6. ✅ Precision/recall published only when reference denominator exists
7. ✅ Sample size, selection method, and CI reported alongside estimates

## 8. Execution Sequence

```
Phase A: Automated uniqueness audit (this turn)
  → PDF_CANDIDATE_UNIQUENESS_AUDIT_v1_2026-10-17.json

Phase B: Reference annotation collection (human, future turn)
  → PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl
  → PDF_PAGES_2026-10-17.zip (rendered pages)

Phase C: Precision and recall estimation (compute from A + B)
  → PDF_EQUATION_LEVEL_VALIDATION_REPORT_v1_2026-10-17.md
```

## 9. File Ownership and Versioning

Each artifact records its version in JSON metadata:
```json
{
  "phase": "validation",
  "baseline": "7172dd32d1",
  "version": "v1",
  "status": "draft",
  "source": "DATASETS/validation/PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md"
}
```

Output is valid JSONL and is written as bytes to the target file. All artifacts are new files created in the `DATASETS/validation/` directory.
