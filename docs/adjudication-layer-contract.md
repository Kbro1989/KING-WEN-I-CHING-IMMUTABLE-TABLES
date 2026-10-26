# Adjudication Layer Contract — 1907.04931

Pipeline: candidate discovery (Layer 1) → adjudication classification (Layer 2) →
targeted adjudication (Layer 3). Each layer owns a distinct file set and a distinct
status meaning. Downstream consumers must read a status **against the file it lives
in**, never against a sibling file.

## Layer 1 — Discovery (harvest)

- Script: `scripts/pix2text_harvest.py`
- Output: `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl`
- Records: 158 (originating from the Pix2Text render set).
- Status: `UNADJUDICATED` (pre-classification); `candidate_class` distinguishes
  `PROSE`, `INLINE_MATH`, `TITLE`, `DISPLAY_EQUATION`.
- Mutability: raw OCR files are immutable evidence; this JSONL is derived and
  reproducible.

## Layer 2 — Adjudication (classification)

- Script: `scripts/adjudicate_candidates_v2.py`
- Output: `adjudication_report.jsonl`, `adjudication_summary.json`,
  `adjudication_report.md`
- Status model (4-level, exclusive within this layer):
  `SPATIAL_MATCH`, `TEXT_MATCH`, `VISUALLY_VERIFIED`, `ADJUDICATED`, `UNADJUDICATED`
- Canonical status source for the earlier classification step. Read status here
  only from `adjudication_report.jsonl`.

## Layer 3 — Targeted adjudication

- Script: `scripts/adjudicate_targets.py`
- Output: `adjudication_targets.jsonl`, `adjudication_targets_summary.json`,
  `adjudication_targets_report.md`
- Contract: carries forward Layer-2 explicit statuses (`VISUALLY_VERIFIED`,
  `SPATIAL_MATCH`, `TEXT_MATCH`); reclassifies `UNADJUDICATED` records to
  `ADJUDICATED` with a `adjudication_detail`.
- Authoritative: `adjudication_targets.jsonl` is the final status for this layer
  set. It does **not** change Layer-2's file.

## Status semantics (what different statuses mean)

| Status | Meaning |
|---|---|
| `SPATIAL_MATCH` | parser candidate boxes overlap / are contained; from Layer 2 |
| `TEXT_MATCH` | normalized math content agrees; from Layer 2 |
| `VISUALLY_VERIFIED` | source PNG exists and is non-blank; from Layer 2 |
| `ADJUDICATED` | reviewed; `adjudication_detail` records the non-semantic determination |
| `UNVERIFIED` | malformed OCR page, no source image, or no parser association |
| `NO_MATCH` | no parser association and no spatial/visual evidence |

## Denominators declared in summary files

- `adjudication_summary.json` (Layer 2): `status_distribution` denominator =
  `region_count` (158).
- `adjudication_targets_summary.json` (Layer 3):
  - `status_distribution` denominator = `total_records` (158) — all records in the file.
  - `newly_adjudicated_detail_distribution` denominator = `newly_adjudicated_count` (120).
  - `carried_forward_detail_distribution` denominator = `carried_forward_count` (38).
- The arithmetic `detail_counts` (18+17+48+37 = 120) divide only among records this
  layer newly adjudicated; carried-forward records carry no detail.

## Cross-artifact consistency

`scripts/test_adjudication_consistency.py` verifies: record identity and count
equality across `pix2text_candidates.jsonl`, `adjudication_report.jsonl`, and
`adjudication_targets.jsonl`; carry-forward status preservation; and that
`adjudication_report.jsonl` matches the committed Layer-2 generator
(`adjudicate_candidates_v2.py`).

## Do not fold manually inferred semantic corrections into generated records

A record may carry only provenance it is derived from: raw OCR, bbox, source-image
hash, parser association, explicit status. `corrected_expression` is a separate,
humans-vouched field — never promoted into `raw_ocr`.
