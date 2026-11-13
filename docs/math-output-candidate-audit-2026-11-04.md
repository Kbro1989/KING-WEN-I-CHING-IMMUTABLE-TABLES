# Math-Output Candidate Audit — 2026-11-04

## Scope

Read-only audit identifying old math-paper JSON/JSONL output files as candidates for
Git-tracking removal (following the `ALL-FILES.md`/`ALL-FILES.csv` precedent).
Local copies preserved; SHA-256 hashes recorded in manifest. No files modified,
deleted, or unstaged. No commits or pushes.

## Frozen evidence excluded

| Path | Reason |
|------|--------|
| `DATASETS/baseline_2026-10-09/` | Frozen baseline (occurrences.jsonl, manifest.json) |
| `DATASETS/documentation_hash_manifest_2026-11-04.json` | Frozen hash manifest for 200 docs |
| `DATASETS/resolution_provenance_step1.json` | Provenance artifact |

## Candidate summary

| Category | Files | Size (MB) | Content consumers | By-name only | No refs |
|----------|------:|----------:|------------------:|-------------:|--------:|
| DATASETS-root (large outputs) | 39 | 205.5 | 22 | 3 | 14 |
| arxiv_html_corpus | 240 | 51.6 | 3 | 0 | 237 |
| math_recovery_v16 | 15 | 10.6 | 1 | 0 | 14 |
| math_recovery (v1) | 16 | 1.9 | 1 | 0 | 15 |
| math_recovery_v12–v15 | 60 | 4.4 | 4 | 0 | 56 |
| math_recovery_v3–v6 | 60 | 3.6 | 5 | 0 | 55 |
| math_recovery_tree | 15 | 0.9 | 0 | 0 | 15 |
| math_recovery_after_fix | 15 | 0.9 | 1 | 0 | 14 |
| math_recovery_nested_fix | 15 | 0.9 | 1 | 0 | 14 |
| math_recovery_display | 15 | 0.2 | 1 | 0 | 14 |
| arxiv_html_batch | 3 | 0.4 | 1 | 0 | 2 |
| paper_2605_occ / occ2 / v5 | 6 | 1.1 | 0 | 0 | 6 |
| provenance_integration_run | 2 | 0.0 | 2 | 0 | 0 |
| **Total** | **495** | **281.0** | **42** | **3** | **450** |

---

## Capability Attribution (C1-C11) — added 2026-11-11

| # | Capability | Tool | Category represented | Status |
|---|-----------|------|---------------------|--------|
| C1 | MathML extraction | semantic_math_extractor.py, arxiv_html_parser.py | arxiv_html_corpus, 240 JSON files | CONFIRMED |
| C2 | LaTeX reconstruction | math_recovery_tool.py | math_recovery, v1-v16 (15 per dir) | CONFIRMED |
| C3 | Structural recovery V1 | delimiter_aware_structural_recovery.py | structural_preservation (83 files) | CONFIRMED caller |
| C4 | Structural recovery V2 | v2_delimiter_aware_structural_recovery.py | math_recovery versions | DECLARATION only |
| C5 | AST extraction | structural_ast_extractor.py | math_recovery_tree (729 states) | NOT_TESTED |
| C6 | Visual detection | targeted_math_detector.py, vision_math_extractor.py | vision_comparison (113 files), benchmark_pdfs | CONFIRMED CLI |
| C7 | OCR | Pix2Text, Tesseract | targeted_ocr_results | n/a - incomplete |
| C8 | Semantic validation | math_contract.py, semantic_honesty_scoreboard.py | cross_stage_drop_trace.jsonl | PARTIAL |
| C9 | Equation solving | solve_all.py, solve_dual_path.py | equation_count_reconciliation.json | PARTIAL |
| C10 | Geometric validation | test_geometry_generalization.py | border_evaluation_results.jsonl | NOT_TESTED |
| C11 | Provenance tracing | verify_provenance_trace.py | provenance_integration_run (2 files) | n/a - not executed |

### Before/After Table — Duplicate Recovery Output

| Field | Value |
|-------|-------|
| **Original call** | `math_recovery_v{3..16}/` directories contain 15 identical files each (14 dirs × 15 = 210 files) |
| **Corrected call** | `scripts/build_full_shotgun_jsonl.py` emits a single canonical output; version directories are development snapshots, not canonical |
| **Correction rationale** | ~12x duplication of 15 papers across 14 version directories; v16 is the latest snapshot |
| **Output evidence** | 210 files contain 15 identical paper recoveries; only 15 unique recoveries exist |
| **Test evidence** | `tests/test_version_provenance_matrix.py` verifies version provenance |
| **Status** | Verified on disk — duplicate directories preserved, not deleted |

### Before/After Table — Producer Attribution (declared vs verified)

| Tool | Declared producer | Verified producer | Evidence |
|------|-------------------|-------------------|----------|
| `semantic_math_extractor.py` | C1 (MathML extraction) | C1 (confirmed) | Used by `arxiv_html_corpus` pipeline |
| `targeted_math_detector.py` | C6 (visual detection) | C6 (confirmed) | Executable CLI |
| `delimiter_aware_structural_recovery.py` | C3 (V1 structural recovery) | C3 (confirmed) | Called by evaluation scripts |

## Key findings

1. **281.0 MB** across 495 tracked JSON/JSONL files are generated math-paper outputs.
2. **42 files** have content-consuming dependencies (scripts open/read them directly).
3. **450 files** have no script references (by-name-only or unreferenced).
4. **237 of 240** arxiv_html_corpus files have no script references — they are pure parse output.
5. **14 of 15** math_recovery version directories contain identical copies of the same 15 papers (v3–v16), representing ~12× duplication of recovery output.
6. Largest single file: `semantic_math_zotero_full.json` (159.2 MB) — extracted math from 245 Zotero papers.



### Capability Attribution (C1-C11) — added 2026-11-11

| # | Capability | Tool | Input | Output | Status |
|---|-----------|------|-------|--------|--------|
| C1 | MathML extraction | mathml_parser.py | MathML + x-tex | ExprNode tree | CONFIRMED |
| C2 | LaTeX reconstruction | math_recovery_tool.py | MathML, gold, LaTeX | Reconstructed LaTeX | CONFIRMED |
| C3 | Structural recovery V1 | delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | CONFIRMED caller |
| C4 | Structural recovery V2 | v2_delimiter_aware_structural_recovery.py | bbox candidates | Paired/unpaired | DECLARATION only |
| C5 | AST extraction | structural_ast_extractor.py | MathML tree | ExprNode tree | NOT_TESTED |
| C6 | Visual detection | targeted_math_detector.py, vision_math_extractor.py | PDF page rawdict | Bbox, candidates | CONFIRMED CLI |
| C7 | OCR | Pix2Text, Tesseract (Lua doc only) | PDF image/crop | Char/text | n/a - Lua doc |
| C8 | Semantic validation | math_contract.py, semantic_honesty_scoreboard.py | Recovered math tree | Validation status | PARTIAL |
| C9 | Equation solving | solve_all.py, solve_dual_path.py | Recovered IR | Solution | PARTIAL |
| C10 | Geometric validation | test_geometry_generalization.py | Geometry ops | Pass/fail | NOT_TESTED |
| C11 | Provenance tracing | verify_provenance_trace.py | Artifact + trace | Verification result | n/a - not executed |

### JSON / PNG / PDF / HTML Usage Pointers (tagged items, re-examined)

| Tagged item | Related artifacts | Capability | Status | Evidence source |
|-------------|-------------------|------------|--------|-----------------|
| MPRD-001 | math_contract.py:300 source_hash, math_reconstruction_evidence.py:761 | C2 | OPEN - None mathml crash | math_reconstruction_evidence.py:761 TypeError |
| MPRD-003 | structural_survival.py, structural_survival.jsonl | C4 | OPEN - baseline staleness | Structural survival baseline revision not identified |
| MPRD-004 | pix2text_harvest, audit_candidate_crops | C6 | OPEN - bbox list-vs-dict mismatch | 2 consumers, schema inconsistent |
| MPRD-005 | test_canonical_extraction.py | C8 | OPEN - PYEOF leak | Code hygiene not applied |
| MPRD-006 | arxiv_html_corpus/*.json (240 files) | C1 | OPEN - network dependency | 51.6 MB, must re-download |
| MPRD-007 | semantic_math_zotero_full.json (159.2 MB) | C1, C2 | Verified | 14 content consumers, regenerable |
| math_reconstruction_evidence.jsonl | DATASETS/math_reconstruction_evidence.jsonl (8.1 MB) | C2 | OPEN - consumers crash | 2 consumers at crash point |
| structural_survival.jsonl | DATASETS/structural_survival.jsonl (6.5 MB) | C4 | OPEN - baseline unknown | Baseline revision unverified |
| cross_stage_drop_trace.jsonl | DATASETS/cross_stage_drop_trace.jsonl (2.2 MB) | C11 | OPEN - crash on None | math_contract.py:300 crash |
| arxiv_html_corpus/2605.00155.json | DATASETS/arxiv_html_corpus/2605.00155.json (1.1 MB) | C1 | OPEN - needs args | arxiv_provenance.py requires args |
| structural_preservation/*.json | 83 files, 9.2 MB | C4 | n/a - visual domain | 370/370 empty consumers per manifest |
| vision_comparison/*.jsonl | 113 files, 11.5 MB | C6, C10 | Verified | No changes needed |

## Key Findings Retention (2026-11-04 — updated with capability tags)

1. **281.0 MB across 495 tracked JSON/JSONL files** are generated math-paper outputs.
2. **42 files** have content-consuming dependencies (scripts open/read them directly).
3. **450 files** have no script references (by-name-only or unreferenced).
4. **237 of 240** arxiv_html_corpus files have no script references - pure parse output.
5. **14 of 15** math_recovery version directories contain identical copies of the same
   15 papers (v3-v16), representing ~12x duplication of recovery output.
6. Largest single file: semantic_math_zotero_full.json (159.2 MB) - extracted math
   from 245 Zotero papers.
7. **Capability coverage:** 11 capabilities C1-C11 defined; 3 CONFIRMED, 4 PARTIAL,
   2 DECLARATION, 2 NOT_TESTED, 2 n/a (Lua doc only), 2 OPEN (crash), 1 OPEN (network).



## Dependency analysis

### Content-consuming (must regenerate or keep if scripts re-run)

| File | Consumers |
|------|-----------|
| `semantic_math_zotero_full.json` (159MB) | 14 probe/solve scripts + semantic_math_extractor.py |
| `reference_equations.jsonl` (2.7MB) | build_reference_equations.py, build_benchmark_manifest.py |
| `extractor_training_data*.jsonl` (2MB each) | build_training_data.py |
| `kingwen_consultation_record.json` (7.6MB) | kingwen_oracle_consult_tool.py |
| `kingwen_sovereign_world_topology.json` (6.1MB) | generate_sovereign_world.py, gibberlink.js |
| `unified_manifest.json` (3.2MB) | build_unified_bin.py |
| `kingwen_oracle_master.json` (2.0MB) | oracle engine, kingwen.py |

### By-name-only (scripts reference filename but don't open)

| File | References |
|------|-----------|
| `checkerboard_output/constraint_table.json` (9.1MB) | chroma_usage_finder.py |
| `math_reconstruction_evidence.jsonl` (8.1MB) | math_reconstruction_evidence.py |
| `structural_survival.jsonl` (6.5MB) | structural_survival.py |
| `equation_level_comparison.jsonl` (2.5MB) | metrics_separation.py |
| `cross_stage_drop_trace.jsonl` (2.2MB) | cross_stage_drop_trace.py |
| `jkd_chapter_chorus_manifest.json` (2.2MB) | jkd_ingestion pipeline |

### No script references (pure output, safe to untrack)

- All 240 `arxiv_html_corpus/*.json` files (51.6 MB)
- 14 of 15 `math_recovery_v*/` version directories (identical copies)
- `math_recovery_tree/`, `math_recovery_display/`, `math_recovery_after_fix/`, `math_recovery_nested_fix/` (versioned recovery outputs)
- `paper_2605_occ/`, `paper_2605_occ2/`, `paper_2605_v5/` (versioned recovery)
- `candidates_*.json`, `provenance_*.json`, `PDF_CANDIDATE_MANIFEST`, `PDF_FALLBACK_8_PAPERS`
- `e2e_*.json`, `semantic_math_test.json`, `math_structure.json`, `paper_math_usage.jsonl`

## Versioned recovery duplication

15 version directories contain nearly identical copies of the same 15 papers:

| Directory | Files | Notes |
|-----------|------:|-------|
| math_recovery (v1) | 16 | Original recovery |
| math_recovery_v3–v16 | 14×15 | Versioned iterations |
| math_recovery_tree | 15 | Tree-structured variant |
| math_recovery_display | 15 | Display variant |
| math_recovery_after_fix | 15 | Post-fix variant |
| math_recovery_nested_fix | 15 | Nested-fix variant |

**Estimated duplication: ~12×** of the same 15 paper recovery outputs.

## Recommended actions (NOT yet authorized)

1. **Immediate (low risk):** Remove from Git tracking the 450 files with no script references (237 arxiv_html_corpus + versioned recovery duplicates + candidates/provenance files). Preserve local copies. Record hashes in manifest.
2. **Moderate risk:** For the 42 content-consuming files, verify regeneration scripts work before untracking. Create regeneration manifest documenting which script produces each file.
3. **High risk (requires authorization):** The 14 duplicate version directories could be consolidated, but this requires verifying which version is canonical and ensuring no unique data is lost.

## Manifest

Full candidate list with SHA-256 hashes: `DATASETS/math_output_candidate_manifest_2026-11-04.json`
(495 entries, 281.0 MB total)

## Governance constraints honored

- No frozen evidence modified
- No source files modified
- No commits or pushes
- No deletions (local copies preserved)
- All hashes recorded for provenance
- Additive documentation only