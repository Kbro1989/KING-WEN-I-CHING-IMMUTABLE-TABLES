# King Wen Documentation Authority Map (V1.0)

**Date:** 2026-11-11
**Repository:** `KING-WEN-I-CHING-IMMUTABLE-TABLES`
**Status:** FROZEN — authority map committed, SHA-256 recorded in
  `docs/documentation_authority_registry.json`

---

## 1. Executive Summary

This document defines the cross-document authority map for the repository. It
distinguishes four capability domains:

| Domain | Files | Authority tier |
|--------|-------|----------------|
| Architecture | `docs/mechanical-swan-architecture.md`, `docs/mechanical-swan-component-registry.json` | Architecture authority |
| Implementation | `lua-math-tool.md`, `scripts/math_recovery/recovery_registry.py` | Implementation |
| Frozen evaluation (8 artifacts) | adjudication-layer-contract, CROSS_PAPER_V2_EVALUATION_PROTOCOL, golden-standard-audit-matrix, frozen-regression-evaluation-mapping, frozen-regression-execution-results, baseline_frozen_padding15.jsonl, phase2b_final_report, phase2c_gate5_calibration | Frozen evaluation authority |
| Exploratory research (9 artifacts) | QSMC-1 correspondence/analysis suite | Exploratory research |

**Disrepancies resolved:**
- Golden-standard artifact count: **8**, not 9. The textual description
  ("three frozen-regression, one frozen baseline, two Phase-2, two
  evaluation-authority") names 8; the 9th artifact is not in the supplied
  inventory. Current disposition: unknown, no path assigned.
- Documentation registry: 201 `.md` files on disk. The earlier abbreviated
  subtotal (130+48+5+9=192) was not an error.
- Golden-standard paths: `PATH_UNVERIFIED` → `PATH_CONFIRMED`.

---

## 2. Frozen Standard Artifact Set (golden-standard authority chain)

The following eight artifacts form the immutable evaluation authority chain:

| # | File | Status | Authority tier | SHA-256 (short) |
|---|------|--------|----------------|-----------------|
| 1 | `docs/adjudication-layer-contract.md` | FROZEN | Frozen evaluation authority | c7ed1b58a8f1e85e... |
| 2 | `docs/CROSS_PAPER_V2_EVALUATION_PROTOCOL.md` | FROZEN | Frozen evaluation authority | 8fefa6efebf94f0c... |
| 3 | `docs/golden-standard-audit-matrix.md` | FROZEN | Frozen evaluation authority | 584f49973bd54bae... |
| 4 | `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | FROZEN | Frozen evaluation authority | 1e04e75c1e5f47c0... |
| 5 | `docs/frozen-regression-execution-results-2026-11-03.md` | FROZEN | Frozen evaluation evidence | 309cad6ab266d5c8... |
| 6 | `DATASETS/vision_comparison/baseline_frozen_padding15.jsonl` | FROZEN | Frozen baseline | fc3ecdbea30c9abd... |
| 7 | `docs/phase2b_final_report.md` | FROZEN | Frozen milestone evidence | 863ed31d7e5a1d17... |
| 8 | `docs/phase2c_gate5_calibration.md` | FROZEN | Frozen calibration authority | 8a3fd177b67aba1b... |

**Preservation rule (from `frozen-regression-evaluation-mapping-2026-11-03.md`):**
- `baseline_frozen_padding15.jsonl` — NEVER overwrite.
- New evaluation results → `DATASETS/vision_comparison/frozen_regression_results.jsonl`.
- Do not modify frozen evaluator.

---

## 3. Authority boundary rule

**QSMC-1 must NOT alter frozen regression baselines, evaluation protocols,
adjudication contracts, or historical execution results.**
Conversely, **frozen evaluation results must NOT be presented as validation**
of QSMC-1 mathematical correspondences.

QSMC-1 is 9 research documents (status PROPOSED or IN_PROGRESS). These remain
independent and must not acquire frozen evaluation authority by appearing in
the same registry.

---

## 4. Document registry schema

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `document_id` | string | Yes | Stable unique identifier (sanitized relative path) |
| `document_type` | string | Yes | md \| json \| py \| jsonl |
| `status` | string | Yes | FROZEN \| CONFIRMED \| IN_PROGRESS \| PROPOSED \| PENDING_REVIEW |
| `authority_tier` | string | Yes | Architecture \| Implementation \| Frozen evaluation \| Frozen baseline \| Exploratory |
| `path_status` | string | Yes | PATH_CONFIRMED \| PATH_UNVERIFIED \| PATH_MISSING |
| `sha256` | string | Yes | SHA-256 of on-disk content |
| `size_bytes` | integer | Yes | Current file size |
| `path` | string | Yes | Relative path from repository root |
| `supersedes` | string[] | No | Explicit predecessor IDs (empty array if none) |

**Registry file:**
`docs/documentation_authority_registry.json` (21 entries)

---

## 5. Evidence-role taxonomy

Per the Math Recovery Puzzle Box design:

| Role | Meaning | Example |
|------|---------|---------|
| CAPTURE | Real source, non-fabricable values | benchmark PDFs, crop PNGs |
| MIRROR | Wraps external behavior in local interface | html parser, OCR extractor |
| SIMULATION | Models external transitions to test local logic | delimiter recovery engine |
| SYNTHETIC | Deliberate abstraction/test values | counting sequences |

---

## 6. Next milestone

56-file provenance audit — individual provenance dispositions for each of 56
pending files. This authority map does NOT complete that audit.
