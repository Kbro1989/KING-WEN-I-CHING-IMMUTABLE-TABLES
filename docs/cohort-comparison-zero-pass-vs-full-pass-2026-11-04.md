# Cohort Comparison: Zero-Pass vs Full-Pass Papers

## Authoritative JSONL Source
- File: `DATASETS/vision_comparison/representative_page_evaluation.jsonl`
- 988 page records + 2 coverage summaries = 990 lines
- 16 papers, 0 failures

## Cohort Definitions

| Cohort | Papers | Pages | Expansion behavior |
|---|---|---|---|
| Zero-pass | 0806.2366, 1212.0957, 2605.24807 | 103 | 100% skip |
| Full-pass | 2605.25036 | 48 | 0% skip |

## Comparative Metrics

| Metric | Zero-pass (103 pages) | Full-pass (48 pages) | Ratio (full/zero) |
|---|---|---|---|
| Region count per page (avg) | 107.5 | 125.2 | 1.16× |
| Boundary count per page (avg) | 282.9 | 616.6 | 2.18× |
| Math boundaries per page (avg) | 64.4 | 47.1 | 0.73× |
| Partial formulas per page (avg) | 19.9 | 25.5 | 1.28× |
| Region area (px, avg) | 11,383 | 26,352 | 2.31× |
| Region area (px, median) | 2,465 | 3,503 | 1.42× |
| Complex regions (%) | 50.6% | 42.9% | 0.85× |
| Page dimensions | 612×792 | 612×792 | 1.00× |

## Key Findings

### 1. Region area is the strongest differentiator
Full-pass papers have **2.31× larger average region area** (26,352 vs 11,383 px). The `expand_crop_context()` function uses `min_content_ratio=0.01` (fraction of non-white pixels). Larger regions contain more content per pixel, making it more likely that the expanded crop meets the threshold. Smaller, more scattered regions (zero-pass cohort) produce expanded crops with too much white space, pushing the content ratio below 0.01.

### 2. Text density differs significantly
Full-pass papers have **2.18× more text boundaries** per page (616.6 vs 282.9). This suggests full-pass papers have denser text layouts with more inline mathematical content, while zero-pass papers may be more figure-heavy or have sparser layouts.

### 3. Math density is NOT the differentiator
Zero-pass papers actually have **more math boundaries** per page (64.4 vs 47.1). This rules out "math-poor" as an explanation for the skip rate. The issue is not the absence of math but the **spatial distribution** of math regions.

### 4. Page size is identical
Both cohorts use 612×792 (8.5×11") pages. Page dimensions are not a factor.

### 5. Complex region ratio is similar
50.6% (zero-pass) vs 42.9% (full-pass) — not a major differentiator. Both cohorts have substantial complex regions.

## Root Cause Analysis

The expansion skip is caused by the interaction between two factors:

1. **Small region areas** in zero-pass papers produce expanded crops with low content ratios.
2. **The 0.01 threshold** is applied uniformly regardless of region size or document layout.

When a small region (e.g., 2,465 px median area) is expanded by 1.5×, the resulting crop contains the original small region plus a large margin of white space. The content ratio (non-white pixels / total pixels) drops below 0.01, and the function returns None.

This is a **scale-dependent threshold** issue, not a data quality issue. The same mathematical content, rendered at a different scale or with different padding, could pass or fail the threshold.

## Implications for Gate Review

### G3 (Context expansion) — Needs attention
The 46.3% skip rate is not a failure, but it is a **coverage gap**. The external assessment correctly identified that:
- Skip is not success (no expanded representation produced)
- Skip is not failure (no crash, no error)
- Skip is an **eligibility decision** that may be too restrictive

### Recommended threshold investigation
Before deciding whether to adjust the threshold, compare:
1. The content_ratio distribution for skipped vs. non-skipped pages
2. Whether skipped pages produce meaningfully different crops when the threshold is lowered
3. Whether the expanded crops on skipped pages actually contain useful context or just white space

### Three zero-pass papers as layout cohort
The three zero-pass papers (0806.2366, 1212.0957, 2605.24807) form a distinct layout cohort characterized by:
- Smaller, more scattered math regions
- Lower text density
- Higher math boundary count (more math per page, but less text context)

This cohort may require a different expansion strategy (e.g., adaptive expansion based on region size, or region-aware padding rather than uniform 1.5×).

## Governance Status

| Milestone | Status |
|---|---|
| Test specification | Complete |
| Standalone tests | 88/88 passed |
| Corpus execution | 988 pages, 16 papers, 0 failures |
| Aggregate reconciliation | Resolved (531/457/988) |
| Cohort comparison | Complete (zero-pass vs full-pass) |
| Behavioral accuracy | Not established |
| G2–G6 formal evaluation | Not evaluated |
| Pipeline integration | Not authorized |

## Population Scope

Two distinct populations remain separate throughout:
1. **16-paper/988-page benchmark corpus** (this evaluation) — representative execution coverage
2. **6-paper/127-page spatial analysis population** (lossy-coverage cross-examination) — candidate spatial analysis

Both scopes are preserved in the append-only JSONL. Their evidence can inform each other without being merged into one denominator.