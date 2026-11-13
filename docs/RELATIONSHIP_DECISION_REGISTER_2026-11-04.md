# Relationship Decision Register — KING-WEN-I-CHING-IMMUTABLE-TABLES

**Generated:** 2026-11-04
**Method:** Read-only adjudication. No files modified, moved, merged, or deleted.
**Hash manifest:** `DATASETS/documentation_hash_manifest_2026-11-04.json` (200 files, SHA-256)
**Overlap analysis:** `docs/DOCUMENTATION_OVERLAP_ANALYSIS_2026-11-04.md`

## Register Schema

| Field | Purpose |
|---|---|
| `relationship_id` | Stable identifier (RD-001, RD-002, ...) |
| `document_a` / `document_b` | Exact paths |
| `relationship_type` | Duplicate, near-duplicate, snapshot-of, generated-from, supersedes, related |
| `evidence` | Hash match, diff, metadata, references, commit history |
| `authority_decision` | Which document is authoritative, if established |
| `disposition` | Keep both, cross-reference, archive, consolidate, unresolved |
| `reviewer_decision` | Explicitly reviewed decision |
| `decision_date` | Date of adjudication |

## Adjudicated Relationships

### RD-001: visual_review_audit_log.md — Exact Duplicate (3 copies)

| Field | Value |
|---|---|
| `relationship_id` | RD-001 |
| `document_a` | `DATASETS/vision_comparison/visual_review_audit_log.md` |
| `document_b` | `DATASETS/vision_comparison/.snapshot_prior/visual_review_audit_log.md` |
| `document_c` | `DATASETS/vision_comparison/generations/gen_20261025_013355_8e463793/visual_review_audit_log.md` |
| `relationship_type` | Exact duplicate (SHA-256 identical, Jaccard = 1.000) |
| `evidence` | Hash match (all 3 identical); git history shows generation copy and main copy added in commit `c032acc314`; snapshot copy is gitignored (`.snapshot_prior/` in `.gitignore` line 35) |
| `authority_decision` | Main copy (`DATASETS/vision_comparison/visual_review_audit_log.md`) is the canonical working copy — it has the longest git history (2 commits: `3601c79df2`, `c032acc314`) |
| `disposition` | Keep all three. Snapshot is a pre-run baseline; generation copy is a generation-scoped artifact; main copy is the current working version. They serve different evidentiary roles. |
| `reviewer_decision` | Unresolved — no consolidation authorized. Copies serve distinct provenance roles. |
| `decision_date` | 2026-11-04 |

### RD-002: multi_paper_generalization_report.md — Exact Duplicate (2 copies) + Near-Duplicate (1)

| Field | Value |
|---|---|
| `relationship_id` | RD-002 |
| `document_a` | `DATASETS/vision_comparison/multi_paper_generalization_report.md` (main) |
| `document_b` | `DATASETS/vision_comparison/.snapshot_prior/multi_paper_generalization_report.md` (snapshot) |
| `document_c` | `DATASETS/vision_comparison/generations/gen_20261025_013355_8e463793/multi_paper_generalization_report.md` (generation) |
| `relationship_type` | B and C are exact duplicates (SHA-256 identical); A is a near-duplicate of B/C (Jaccard = 0.871) |
| `evidence` | Hash match (B ≡ C); diff shows A was updated after B/C were snapshotted (5 commits on A vs 1 on B/C); git history: A has 5 commits, B/C have 1 commit (`c032acc314`) |
| `authority_decision` | Main copy (A) is authoritative — it has the most recent updates and longest history |
| `disposition` | Keep all three. A is current working copy; B is pre-run snapshot; C is generation-scoped artifact. |
| `reviewer_decision` | Unresolved — no consolidation authorized. The 0.871 similarity indicates A diverged from B/C after snapshotting, which is expected for a working document. |
| `decision_date` | 2026-11-04 |

### RD-003: PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md — Near-Duplicate (0.791)

| Field | Value |
|---|---|
| `relationship_id` | RD-003 |
| `document_a` | `DATASETS/PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md` |
| `document_b` | `DATASETS/validation/PDF_EQUATION_LEVEL_VALIDATION_PLAN_v1_2026-10-17.md` |
| `relationship_type` | Near-duplicate (Jaccard = 0.791, 176 vs 177 lines) |
| `evidence` | Both added in same commit `bdfd5eeaea`; diff shows substantially different content (176 lines changed); same filename in different directories |
| `authority_decision` | Unresolved — both have identical commit provenance. The `validation/` subdirectory copy appears to be the working copy (per the plan's own directory structure: "All new artifacts live under `DATASETS/validation/`"). The root-level copy may be a staging or reference copy. |
| `disposition` | Keep both. Determine authority by checking which copy is referenced by downstream validation artifacts. |
| `reviewer_decision` | Unresolved — requires manual comparison of section-level differences and downstream references. |
| `decision_date` | 2026-11-04 |

### RD-004: Unresolved Relationship Pairs (4+)

| Relationship ID | Document A | Document B | Topic | Disposition |
|---|---|---|---|---|
| RD-004a | `docs/remediation-verification-matrix.md` | `docs/controlled-remediation-verification-protocol.md` | Remediation vs. verification protocol | Keep separate — different authority levels (proposal vs. protocol) |
| RD-004b | `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | `docs/qsmc1-m3-dimensional-consistency-analysis.md` | Provenance audit vs. dimensional analysis | Keep separate — different scope |
| RD-004c | `docs/traceability-matrix-2026-10-27.md` | `docs/research-to-test-traceability-matrix-2026-10-29.md` | Different dates and scope | Keep separate — temporal evolution |
| RD-004d | `docs/pipeline-gap-analysis-2026-10-27.md` | `docs/pipeline-output-measurement-2026-10-27.md` | Gap analysis vs. output measurement | Keep separate — different concerns |

**Disposition for all RD-004x:** Keep separate. These are related-but-distinct documents serving different evidentiary roles. No consolidation authorized.

## Orphaned Documents (26)

**Disposition:** No action. All 26 orphans are expected — generated outputs, per-page reports, audit logs, or snapshot copies. An orphan is a graph property under a particular reference scan, not evidence that a document is disposable.

## Manifest Population Note

The documentation registry (`docs/DOCUMENTATION_REGISTRY.md`) references 201 files. The hash manifest (`DATASETS/documentation_hash_manifest_2026-11-04.json`) contains 200 files. The difference of 1 is explained by:

- The manifest was generated **after** the registry was created but **before** the overlap analysis file (`docs/DOCUMENTATION_OVERLAP_ANALYSIS_2026-11-04.md`) was created.
- The overlap analysis file is the 201st file.
- The manifest should be regenerated if a complete current-state hash is needed.

## Summary

| Relationship Type | Count | Disposition |
|---|---|---|
| Exact duplicates | 2 groups (5 files) | Preserve all; canonical copies identified |
| Near-duplicates | 3 pairs (7 files) | Preserve; authority partially unresolved |
| Orphaned documents | 26 | No action (expected) |
| Unresolved relationships | 4+ pairs | Keep separate; cross-reference only |
| Related but distinct | ~170 files | No consolidation |

## Next Steps (per external assessment)

1. **Freeze documentation snapshot** — ✅ Hash manifest created (`DATASETS/documentation_hash_manifest_2026-11-04.json`)
2. **Read-only overlap analysis** — ✅ Completed (`docs/DOCUMENTATION_OVERLAP_ANALYSIS_2026-11-04.md`)
3. **Review relationship candidates** — ✅ Completed (this register)
4. **Update registry** — Add confirmed relationships to `docs/DOCUMENTATION_REGISTRY.md` (not yet done; requires authorization)
5. **Consolidate selectively** — Only after review, and only where documents have compatible authority and lifecycle status (not authorized)

## Gate Status

- Gate 2: OPEN (unchanged)
- QSMC-1 baseline: Frozen (unchanged)
- B4 Gate 2: BLOCKED (unchanged)
- No commits made beyond `c40286cd6a`
- King Wen JSONL deletion decision: Independent (unchanged)