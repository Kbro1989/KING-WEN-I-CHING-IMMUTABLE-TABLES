# Occurrence Reconciliation — 2026-10-11

Frozen baseline is **immutable**. This report explains every difference.

## Counts

| Ledger | Occurrences | Unique keys |
| --- | ---: | ---: |
| Source | 4235 | 4235 |
| Baseline (frozen 2026-10-09) | 3409 | 3409 |
| Recovery (v16) | 4235 | 4235 |

## Categories

| Category | Count |
| --- | ---: |
| source_only | 826 |
| baseline_only | 0 |
| recovery_missing | 0 |
| recovery_only | 0 |
| content_changed | 165 |
| duplicate_source_keys | 0 |
| duplicate_baseline_keys | 0 |
| duplicate_recovery_keys | 0 |

## Per-paper

| Paper | Version | Source | Baseline | Recovery | Src-Base | Src-Rec |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2009.00031 | v1 | 360 | 360 | 360 | 0 | 0 |
| 2102.03334 | v2 | 94 | 94 | 94 | 0 | 0 |
| 2605.00155 | v4 | 991 | 991 | 991 | 0 | 0 |
| 2605.00224 | v1 | 156 | 156 | 156 | 0 | 0 |
| 2605.06070 | v1 | 991 | 165 | 991 | 826 | 0 |
| 2605.18130 | v1 | 339 | 339 | 339 | 0 | 0 |
| 2605.22715 | v2 | 133 | 133 | 133 | 0 | 0 |
| 2605.23244 | v1 | 305 | 305 | 305 | 0 | 0 |
| 2605.24807 | v1 | 52 | 52 | 52 | 0 | 0 |
| 2605.24856 | v2 | 168 | 168 | 168 | 0 | 0 |
| 2605.25036 | v1 | 211 | 211 | 211 | 0 | 0 |
| 2605.25334 | v1 | 147 | 147 | 147 | 0 | 0 |
| 2605.28615 | v1 | 94 | 94 | 94 | 0 | 0 |
| 2605.28896 | v1 | 194 | 194 | 194 | 0 | 0 |

## Verdict

- Unexplained differences: **0**
- Every difference categorically explained: **True**
- Source == Baseline: **False**
- Source == Recovery: **True**

A non-zero `source_only` with zero `recovery_missing` means the current
source legitimately contains occurrences the frozen baseline predates;
recovery covers all of them. The baseline is not updated here.
