# Sampling Frame Freeze — v2

**Frozen baseline:** `main@7172dd32d1` (accepted 2026-10-16)
**Date:** 2026-10-17
**Purpose:** Freeze the sampling frame for the 420-candidate precision audit.
**Revision:** v2 — corrected selection-method documentation + zero-allocation strata

---

## 1. Sampling Frame Fixed

| Parameter | Value |
|-----------|-------|
| Sample size | 420 candidates |
| Papers | 6 listed + 2 zero-allocation strata |
| Total candidates available | 4,921 records |
| Selection method | Deterministic hash-ranked sampling (sha256(paper_id \| index) within paper) |
| Random seed | 20261017 — run identifier only; does NOT influence ranking |
| Determinism | sha256(paper_id \| index), sorted within each paper |
| Notes | The seed does not affect selection; existing 420 candidates preserved exactly |

## 2. Allocation

### Seven listed strata (six with candidates + two zero-allocation)

| Paper | Records | Allocated |
|-------|---------|-----------|
| 2104.01277 | 2,715 | 232 |
| 2206.00364 | 1,934 | 165 |
| 1907.04931 | 195 | 16 |
| 2205.01395 | 9 | 1 |
| 2605.22902 | 31 | 3 |
| 2605.27315 | 37 | 3 |
| **TOTAL** | **4,921** | **420** |

### Zero-allocation strata (explicitly recorded per user correction)

| Paper | Eligible candidates | Status |
|-------|---------------------|--------|
| 2305.08038 | 0 | Zero-allocation stratum — no eligible candidates after documented exclusions |
| 2602.15881 | 0 | Zero-allocation stratum — no eligible candidates after documented exclusions |

Both papers are in the PDF fallback set but contain zero candidate records after exclusions.

---

## 3. Saved Artifacts

| Artifact | Path |
|----------|------|
| Sampling seed | `DATASETS/sampling_seed_2026-10-17.json` |
| Annotation template | `DATASETS/annotation_template_v1_2026-10-17.json` |
| Sampling frame freeze | `DATASETS/SAMPLE_FRAME_FREEZE_v1_2026-10-17.md` (v2 revision) |

### Selection Parameters

```json
{
  "sample_size": 420,
  "selection_method": "Deterministic hash-ranked sampling: within each paper, records ranked by sha256(paper_id | index), then take first N",
  "seed": 20261017,
  "seed_role": "run identifier only — does NOT influence ranking",
  "determinism": "sha256(paper_id | index), sorted within paper",
  "result_columns": ["candidate_id", "classification", "evidence_ref", "annotator_note"]
}
```

---

## 4. Precision and Recall Definitions

### Precision (raw records)

\[ \mathrm{Precision_{raw}} = rac{TP}{TP + FP} \]

Denominator = 4921 (all candidate records including duplicates). Classified as TP/FP/unresolved.

### Precision (deduplicated occurrences)

\[ \mathrm{Precision_{dedup}} = rac{TP}{TP + FP} \]

Denominator = 2,535 (unique normalized-text keys). Only records classified as `true_positive` or `false_positive` (not `unresolved`).

### Recall (independent)

Annotators enumerate all visible equations on independently selected pages WITHOUT consulting the candidate list. Then match against candidates.

\[ \mathrm{Recall} = rac{TP}{TP + FN} \]

---

## 5. Next Steps

1. **Human annotation:** Reviewer inspects rendered PDF pages for the 420 candidates. Classify each as TP/FP/unresolved with evidence reference.
2. **Recall audit:** Independently select recall-audit pages, inventory all visible equations, match against candidates.
3. **Compute metrics:** Precision (raw + dedup) with 95% Wilson CI, Recall with 95% Wilson CI.
4. **Publish v2 report** with annotated diversity and confidence intervals.

---

## 6. Revision Notes

| Revision | Change |
|----------|--------|
| v1 | Initial freeze: proportional allocation, 420 candidates, seed assumed active |
| v2 | (1) Corrected selection-method: seed is run identifier only, not ranking seed; (2) Added zero-allocation strata 2305.08038 and 2602.15881 |

---

## 7. Boundary Preserved

- Frozen baseline: unchanged
- Prior report versions: unchanged
- All artifacts in `DATASETS/validation/`
- New artifacts: `sampling_seed_2026-10-17.json` (v2), `annotation_template_v1_2026-10-17.json`, `SAMPLE_FRAME_FREEZE_v1_2026-10-17.md` (v2 revision)
