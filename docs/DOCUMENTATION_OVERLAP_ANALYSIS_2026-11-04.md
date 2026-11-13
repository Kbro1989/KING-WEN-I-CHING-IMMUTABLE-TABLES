# Documentation Overlap Analysis — KING-WEN-I-CHING-IMMUTABLE-TABLES

**Generated:** 2026-11-04
**Scope:** 200 project `.md` files (excluding vendored `node_modules/`, `.venv/`, `.pytest_cache/`, `cache/`)
**Method:** Read-only analysis. No files modified, moved, merged, or deleted.
**Hash manifest:** `DATASETS/documentation_hash_manifest_2026-11-04.json` (200 files, SHA-256)

## 1. Exact Duplicates (2 groups, 5 files)

### Group 1: `visual_review_audit_log.md` — 3 identical copies

| Copy | Path | SHA-256 |
|---|---|---|
| A (canonical) | `DATASETS/vision_comparison/visual_review_audit_log.md` | identical |
| B (snapshot) | `DATASETS/vision_comparison/.snapshot_prior/visual_review_audit_log.md` | identical |
| C (generation) | `DATASETS/vision_comparison/generations/gen_20261025_013355_8e463793/visual_review_audit_log.md` | identical |

**Classification:** Exact duplicate (Jaccard = 1.000)
**Recommended action:** Preserve all three. Copy B is a pre-run snapshot, Copy C is a generation-scoped artifact, Copy A is the canonical working copy. They serve different evidentiary roles (baseline snapshot vs. generation output vs. current state). Do NOT delete any. If consolidation is authorized later, designate Copy A as canonical and add `supersedes` metadata to B and C.

### Group 2: `multi_paper_generalization_report.md` — 2 exact copies

| Copy | Path | SHA-256 |
|---|---|---|
| A (snapshot) | `DATASETS/vision_comparison/.snapshot_prior/multi_paper_generalization_report.md` | identical |
| B (generation) | `DATASETS/vision_comparison/generations/gen_20261025_013355_8e463793/multi_paper_generalization_report.md` | identical |

**Classification:** Exact duplicate (Jaccard = 1.000)
**Recommended action:** Preserve both. Same reasoning as Group 1 — snapshot vs. generation-scoped artifact. The main working copy (`DATASETS/vision_comparison/multi_paper_generalization_report.md`) is a near-duplicate (0.871) but NOT identical, indicating it was updated after the snapshot/generation.

## 2. Near-Duplicates (7 pairs)

### Pair 1–2: `multi_paper_generalization_report.md` variants (Jaccard = 0.871)

| File A | File B | Similarity |
|---|---|---|
| `DATASETS/vision_comparison/multi_paper_generalization_report.md` | `DATASETS/vision_comparison/.snapshot_prior/multi_paper_generalization_report.md` | 0.871 |
| `DATASETS/vision_comparison/multi_paper_generalization_report.md` | `DATASETS/vision_comparison/generations/gen_20261025_013355_8e463793/multi_paper_generalization_report.md` | 0.871 |

**Classification:** Near duplicate — main copy was updated after snapshot/generation
**Recommended action:** Keep separate. The main copy represents the current state; snapshot/generation copies are historical. Add `supersedes` metadata from main → snapshot/generation if consolidation is authorized.

### Pair 3: `PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md` (Jaccard = 0.791)

| File A | File B |
|---|---|
| `DATASETS/PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md` | `DATASETS/validation/PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md` |

**Classification:** Near duplicate — same filename in two locations
**Recommended action:** Compare contents to determine if one is a copy or a variant. Likely one is a working copy and the other is an archived/validated version. Preserve both until authority is established.

## 3. Orphaned Documents (26)

These documents have no inbound references from other project `.md` files. Most are expected orphans (generated outputs, per-page reports, audit logs, snapshots).

| # | File | Likely Role | Expected Orphan? |
|---|---|---|---|
| 1 | `DATASETS/FINAL_KINGWEN_CORPUS_AUDIT_REPORT_2026-10-16.md` | Audit report | Yes — top-level report |
| 2–9 | `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_output/page_*_pix2text.md` (8 files) | Per-page OCR output | Yes — generated artifacts |
| 10 | `DATASETS/REPRODUCIBILITY_REPORT_2026-10-16.md` | Reproducibility report | Yes — top-level report |
| 11 | `DATASETS/STATISTICAL_GUIDANCE_v1_2026-10-17.md` | Statistical guidance | Yes — standalone spec |
| 12 | `DATASETS/VALIDATION_CHECKPOINT_2026-10-16.md` | Validation checkpoint | Yes — top-level report |
| 13 | `DATASETS/combinatorics_benchmark/combinatorics_benchmark_report.md` | Benchmark report | Yes — subdirectory report |
| 14 | `DATASETS/cross_reference/discrepancy_report.md` | Discrepancy report | Yes — subdirectory report |
| 15 | `DATASETS/cross_reference/reconciliation_note.md` | Reconciliation note | Yes — subdirectory note |
| 16 | `DATASETS/math_symbols/references/size_aware_symbol_reference.md` | Symbol reference | Yes — reference doc |
| 17 | `DATASETS/reconciliation_2026-10-11.md` | Reconciliation report | Yes — top-level report |
| 18 | `DATASETS/validation/PDF_CANDIDATE_DUPLICATE_LOGIC_VALIDATION_v1_2026-10-17.md` | Validation report | Yes — subdirectory report |
| 19 | `DATASETS/vision_comparison/.snapshot_prior/visual_review_audit_log.md` | Snapshot (exact dup of #1) | Yes — snapshot |
| 20 | `DATASETS/vision_comparison/crop_isolation_experiment/crop_isolation_report.md` | Experiment report | Yes — subdirectory report |
| 21–26 | 6 additional orphans (see full list in terminal output) | Various | Likely generated artifacts |

**Assessment:** All 26 orphans are expected — they are generated outputs, per-page reports, audit logs, or snapshot copies. No orphan appears to be a lost or misplaced specification. No action required.

## 4. Unresolved Relationships (not duplicates)

The following documents share topics but serve different evidentiary roles. They should NOT be consolidated:

| Document A | Document B | Relationship |
|---|---|---|
| `docs/remediation-verification-matrix.md` | `docs/controlled-remediation-verification-protocol.md` | Remediation proposal vs. verification protocol — different authority levels |
| `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `docs/qsmc1-m3-dimensional-consistency-analysis.md` | Provenance audit vs. dimensional analysis — different scope |
| `docs/traceability-matrix-2026-10-27.md` | `docs/research-to-test-traceability-matrix-2026-10-29.md` | Different dates, different scope |
| `docs/pipeline-gap-analysis-2026-10-27.md` | `docs/pipeline-output-measurement-2026-10-27.md` | Gap analysis vs. output measurement — different concerns |

## 5. Summary

| Classification | Count | Action |
|---|---|---|
| Exact duplicates | 2 groups (5 files) | Preserve all; designate canonical copies if consolidation authorized |
| Near-duplicates | 3 pairs (7 files) | Compare authority; preserve until relationship established |
| Orphaned documents | 26 | Expected — no action needed |
| Unresolved relationships | 4+ pairs | Keep separate; cross-reference only |
| Related but distinct | ~170 files | Keep separate; no consolidation |

## 6. Recommended Next Steps

1. **Freeze documentation snapshot** — record registry version, Git state, content-hash manifest (✅ completed: `DATASETS/documentation_hash_manifest_2026-11-04.json`)
2. **Read-only overlap analysis** — completed above; findings recorded
3. **Review relationship candidates** — establish which relationships are exact, inferred, or explicitly documented
4. **Update registry** — add confirmed relationships only; preserve unresolved candidates as unresolved
5. **Consolidate selectively** — only after review, and only where documents have compatible authority and lifecycle status

### Important Notes
- No files were modified, moved, merged, or deleted during this analysis.
- The King Wen JSONL deletion decision remains independent of this work.
- P1 glyph-catalog spec remains read-only until separately authorized.
- Gate 2 remains OPEN; QSMC-1 baseline remains frozen.
- No commits were made.