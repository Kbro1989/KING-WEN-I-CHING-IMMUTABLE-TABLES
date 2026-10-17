# Statistical Guidance for Precision and Recall Estimation

**Revision:** 2026-10-17 (added to SAMPLE_FRAME_FREEZE_v1_2026-10-17.md)
**Purpose:** Provide the statistical protocol that the annotation dataset will satisfy.

---

## 1. Design Fact

The sample of 420 candidates is allocated proportionally across the six nonempty strata
with largest-remainder rounding. This is a **stratified, without-replacement design**.
Each stratum's allocation should be reported (population N_h, sample n_h) so that
weighted estimates can be computed.

| Paper | N_h (records) | n_h (sampled) | n_h / N_h |
|-------|---------------|---------------|-----------|
| 2104.01277 | 2,715 | 232 | 0.0855 |
| 2206.00364 | 1,934 | 165 | 0.0853 |
| 1907.04931 | 195 | 16 | 0.0821 |
| 2205.01395 | 9 | 1 | 0.1111 |
| 2605.22902 | 31 | 3 | 0.0968 |
| 2605.27315 | 37 | 3 | 0.0811 |
| **TOTAL** | **4,921** | **420** | **0.0853** |

---

## 2. Precision Estimation

### 2a. Per-stratum classification

For each stratum h, count:
- n_h^TP = number of true-positive candidate records
- n_h^FP = number of false-positive candidate records
- n_h^U = number of unresolved candidate records

### 2b. Weighted precision estimate (raw records)

The overall precision estimate is the weighted average of stratum-level TP rates,
with weights proportional to stratum population sizes:

\[ \hat{p}_{raw} = \frac{\sum_h N_h \cdot \frac{n_h^{TP}}{n_h}}{N} \]

where N = 4,921 is the total population of candidate records.

This accounts for the fact that strata with fewer records (e.g., 2205.01395 with 9 records)
are represented by only 1 candidate, yet all contribute proportionally to the overall
estimate.

### 2c. Confidence interval for raw precision (stratified, without replacement)

For a stratified design without replacement, use the stratified variance estimator:

\[ Var(\hat{p}_{raw}) = \sum_h \left( \frac{N_h}{N} \right)^2 \cdot \frac{1}{n_h} \cdot \frac{N_h - n_h}{N_h - 1} \cdot p_h(1 - p_h) \]

where p_h = n_h^TP / n_h is the stratum-level precision rate.

95% CI: \[
\hat{p}_{raw} \pm 1.96 \sqrt{Var(\hat{p}_{raw})}
\]

For strata with n_h = 1, the variance contribution is undefined. Handle as:
- Use a conservative interval (e.g., Clopper-Pearson lower bound) for that stratum.
- Report the limitation.

### 2d. Precision for deduplicated source equations

This is a separate estimate requiring a deduplication step before analysis. Candidates
must be collapsed to unique source-equation identities using the normalized-text
key, then re-aggregate:

- N' = 2,535 unique normalized-text keys (per uniqueness audit)
- n'^TP, n'^FP, n'^U from the deduplicated classification

Compute the weighted precision estimate over the deduplicated set using the same
stratified formula, but with N' = 2,535 and n' = sum of deduplicated sampled keys.

Report this as precision_dedup (source-equation-level precision), clearly separated
from raw precision (candidate-level precision).

---

## 3. Recall Estimation

Candidate annotation alone cannot estimate recall. A separate, independent inventory
of equations on sampled pages is required.

### 3a. Recall-audit procedure

1. Select recall-audit pages (independent of the candidate sample).
2. On each page, enumerate **every visible equation** (ground truth), including:
   - Inline equations
   - Display equations
   - Equations in tables, figures, captions
   - Equations the candidate extractor missed
3. Match ground-truth pages against candidates extracted from those pages.
4. Classify each ground-truth equation as:
   - TP: matched to at least one candidate
   - FN: missed by candidate extraction
   - U (unresolved): cannot determine without further review

### 3b. Recall formula

Recall depends on the ground-truth universe for each sampled page:

\[ \hat{R} = \frac{\sum_h TP_h}{\sum_h (TP_h + FN_h)} \]

where TP_h = number of ground-truth equations matched to candidates on page h,
FN_h = number of ground-truth equations not matched.

CI requires variance estimation across pages, which depends on page selection design
(independent binomial, cluster-randomized, etc.). Report methodology accordingly.

---

## 4. Unresolved Cases

Unresolved candidates and equations must be reported separately and must not be
silently counted as TP or FP. Standard practice:

- Report n^U for each stratum.
- Do NOT include unresolved in precision or recall point estimates.
- Report a sensitivity analysis: both "strict" (unresolved = FP) and "lenient"
  (unresolved = TP) bounds can be provided as upper/lower bounds.

---

## 5. Candidate-Level vs Source-Equation-Level Precision

These are fundamentally different quantities and must be reported separately:

- **Candidate-level precision**: fraction of candidate records that are true positives.
  Formula: TP / (TP + FP) (raw or stratified). Denominator = 4,921 (or 2,535 deduped).

- **Source-equation-level precision**: fraction of unique source equations accounted
  for by at least one true-positive candidate. Different from candidate-level because:
  - multiple candidates may represent the same equation
  - one candidate may capture only part of an equation

Report both. Label clearly: `precision_raw` and `precision_dedup`.

---

## 6. Zero-Candidate Strata

The two strata with zero eligible candidate records (2305.08038, 2602.15881) must
NOT be treated as zero-equation papers. Their extraction recall remains unknown until
page-level review establishes whether equations are present on their pages.

For the validation report:
- Do not report a precision estimate that includes these strata (no candidates exist).
- Do report a recall gap: these strata contribute zero candidates; their recall is
  uncertain until page-level review.
- If page-level review happens later, these strata can be added with their own sample.

---

## 7. Annotation Evidence Structure

Each annotation record must contain:

```json
{
  "candidate_id": "2204.01277_p42",
  "paper_id": "2104.01277",
  "candidate_index": 42,
  "classification": "true_positive" | "false_positive" | "unresolved",
  "page": "PaperId_pN.pdf, Page X",
  "evidence": "Rendered-page observation (verbatim or structured)",
  "reviewer": "Reviewer identifier (if multiple)",
  "rationale": "Justification for classification"
}
```

### Aggregation schema

Per stratum: { n, TP, FP, U, TP_rate, FP_rate, U_rate, precision_ci }

Overall: { N, n, TP, FP, U, precision_raw_stratified_ci, precision_dedup_stratified_ci,
  recall_point, recall_ci }

---

## 8. Reporting Requirements Summary

The validation report must include:

- [ ] Annotation of all 420 candidates (TP/FP/unresolved), with page + evidence
- [ ] Unresolved count reported separately; sensitivity bounds for strict/lenient
- [ ] Stratified precision estimate with variance (not unweighted Wilson)
- [ ] Stratified Wilson CI as supplementary (not the primary interval)
- [ ] Independent recall inventory and recall estimate with CI
- [ ] Candidate-level and source-equation-level precision, clearly labeled separate
- [ ] Zero-candidate strata documented as recall gap, not zero-equation assumption
- [ ] Per-stratum tables with N_h, n_h, TP, FP, U, rates
- [ ] Reviewers and review procedure documented
