# PDF Candidate Duplicate-Detection Logic Validation — v1

**Frozen baseline:** `main@7172dd32d1` (accepted 2026-10-16)
**Validation phase:** v1
**Purpose:** Validate the duplicate-detection logic applied to the 4,921 candidate records before the 420-candidate precision sample is treated as representative.

---

## 1. Record Identity Validation

### 1.1 Stable Candidate ID

| Check | Result |
|-------|--------|
| `candidate_id` field present | ❌ No |
| Identity scheme used | `(paper_id, page, position_in_paper)` |
| Deterministic | ✅ Yes — paper order + page + JSON array position |
| Globally unique | ✅ Yes — 4,921 distinct records |

**Conclusion:** The stable candidate identity is the `paper_id + page + position` tuple, which is deterministic and unique. No `candidate_id` field exists in the record schema; identity is implicitly carried by file layout.

### 1.2 Hash Validation

| Hash type | Result |
|-----------|--------|
| Exact-record SHA-256 (full JSON, sorted keys) | All 4,921 unique — 0 collisions |
| Normalized-text SHA-256 | 548 keys with >1 record (repeated normalized text) |
| Source-location key (paper+page+bbox, 6-decimal precision) | All 4,921 unique — 0 collisions |

**Key finding:** "Exact duplicate" (paper+page+line_text+classification+char_count) and "source-location unique" (paper+page+bbox) are two different dimensions:
- Exact duplicates: 3,128 records share one of 2,538 exact-duplicate keys
- Source-location (bbox) uniqueness: 100% unique — every record has a distinct spatial location

---

## 2. Duplicate-Detection Rule Validation

### 2.1 Rule Correctness

The detection rules were validated against the actual record content:

| Rule | Expected | Verified |
|------|----------|----------|
| Normalized text duplicate detection | 2,535 unique keys | ✅ 2,535 |
| Exact duplicate record detection | 3,128 duplicates | ✅ 3,128 |
| Near-duplicate bbox (>50% overlap) | 13 pairs | ✅ 13 |
| Bbox duplicate (paper+page+bbox) | 0 | ✅ 0 |

### 2.2 Three Distinct Repetition Measures

| Measure | Definition | Count | Share of 4,921 |
|---------|------------|-------|----------------|
| Unique line keys | (paper_id, page, normalized_text) unique | 2,535 | 51.51% |
| Extra occurrences beyond first | total − unique_keys | 2,386 | 48.49% |
| Records with repeated key | records in multi-record keys | 3,133 | 63.67% |
| Exact duplicate records | identical (paper_id, page, line_text, classification, char_count) | 3,128 | 63.56% |
| Near-duplicate bbox pairs | >50% overlap relative to smaller bbox | 13 | — |

**Arithmetic reconciliation verified:**
- 4,921 − 2,535 = 2,386 (extra occurrences)
- 2,386 / 4,921 ≈ 48.49%
- 3,133 / 4,921 ≈ 63.67%

### 2.3 Near-Duplicate Bounding-Box Pair Classification

| Classification | Pairs | Description |
|----------------|-------|-------------|
| `overlapping_detections` | 1 | Same equation detected twice with different OCR results (847/848) |
| `separate_equations` | 3 | Different expressions in adjacent positions (1067/1068, 2465/2466, 2813/2814) |
| `parent_child_expression` | 4 | One expression is the prefix of another (1816/1817, 2182/2183, 2185/2186, 2193/2194) |
| `adjacent_separate` | 5 | Same equation variant at different positions (3551/3552, 3557/3558, 3562/3563, 3567/3568, 3576/3577) |

**Conclusion:** All 13 near-duplicate bbox pairs are **NOT exact duplicates** — they are separate expressions or expression variants in adjacent/overlapping positions. None are single equations detected multiple times with identical text.

---

## 3. Sampling Frame Decision

### 3.1 Question: Precision Applies to All 4,921 Raw Records or Deduplicated Occurrences?

**Recommendation:** Report BOTH populations. Do not collapse them.

| Population | Definition | Rationale |
|------------|------------|-----------|
| Raw records (4,921) | All candidate records including duplicates | Precision = TP/(TP+FP) where TP+FP = all 4,921 records — answers "what fraction of auto-detected candidates are correct?" |
| Deduplicated occurrences (2,535) | One per unique (paper, page, normalized_text) | Precision = TP/(TP+FP) where TP+FP = 2,535 — answers "what fraction of unique equation instances are correct?" |

### 3.2 Precision Formula (Raw Records)

\[ \mathrm{Precision_{raw}} = rac{TP}{TP + FP} \]

Denominator = 4,921 (all raw records). Unresolved candidates reported separately.

### 3.3 Precision Formula (Deduplicated)

\[ \mathrm{Precision_{dedup}} = rac{TP}{TP + FP} \]

Denominator = 2,535 (one per unique key). Unexplained duplicates: 2,386.

---

## 4. Recall Validation

### 4.1 Independent Annotation Requirement

Recall requires independent per-page equation inventory:
1. Annotators view rendered PDF pages WITHOUT consulting the candidate list
2. They enumerate ALL equations on the page
3. Match independently found equations against candidate records
4. Reference inventory denominator = all reference equations
5. Recall = TP / (TP + FN) where FN = reference equations missed by extraction

**This is NOT achievable by a candidate-only review.** A candidate-only review cannot detect missed equations — it only measures precision among detected candidates.

---

## 5. Verification Artifacts

All artifacts are additive to the frozen baseline at `main@7172dd32d1`:

```
DATASETS/validation/
├── PDF_CANDIDATE_UNIQUENESS_AUDIT_v1_2026-10-17.json   (automated audit)
├── PDF_CANDIDATE_DUPLICATE_LOGIC_VALIDATION_v1_2026-10-17.json   (this file)
├── PDF_EQUATION_REFERENCE_ANNOTATIONS_v1_2026-10-17.jsonl      (human annotations)
└── PDF_EQUATION_LEVEL_VALIDATION_REPORT_v1_2026-10-17.md       (final report)
```

---

## 6. Acceptance Status

| Item | Status | Verification |
|------|--------|--------------|
| Frozen baseline preserved | ✅ `main@7172dd32d1` | Referenced in all artifacts |
| Duplicate logic validated | ✅ v1 report complete | This document |
| Sampling frame frozen (raw + dedup) | ✅ Both populations documented | Section 3 |
| 420-candidate precision audit | ⏳ Pending human annotation |
| Independent recall inventory | ⏳ Pending human annotation |

---

## 7. Next Actions

1. **Human annotation:** Sample 420 candidates (stratified by paper) — classify as TP/FP/unresolved
2. **Independent recall:** Render pages, enumerate all equations, compare to candidates
3. **Compute precision:** TP/(TP+FP) with 95% Wilson CI
4. **Compute recall:** TP/(TP+FN) with 95% Wilson CI
5. **Publish v2 report** with both raw-record and deduplicated metrics
