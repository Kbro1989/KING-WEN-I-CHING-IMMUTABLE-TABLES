# Targeted Adjudication Report - 1907.04931

Layer 3 of the adjudication contract (see docs/adjudication-layer-contract.md). Carries forward Layer-2 explicit statuses; adjudicates UNADJUDICATED records.

| Metric | Value |
|---|---|
| Total records | 158 |
| Carried forward | 38 |
| Newly adjudicated | 120 |

## Status distribution (denominator = total records = 158)

| Status | Count |
|---|---|
| ADJUDICATED | 120 |
| VISUALLY_VERIFIED | 37 |
| TEXT_MATCH | 1 |

## Newly-adjudicated reasons (denominator = newly adjudicated = 120)

| Detail | Count |
|---|---|
| DUPLICATE_OBSERVATION | 18 |
| FRAGMENT_SINGLE_TOKEN | 17 |
| MALFORMED_OCR_WARN_SAFE_SKIP | 48 |
| PARSE_GAP_DISCOVERY | 37 |

## Carried-forward detail (denominator = carried forward = 38)

| Detail | Count |
|---|---|
| UNKNOWN | 38 |
