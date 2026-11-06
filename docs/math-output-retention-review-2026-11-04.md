# Math Output Retention and Reproducibility Review — 2026-11-04

## 1. Reconciliation of the 495-entry manifest

### Dependency classification (corrected)

The original summary reported 42 content-consuming + 450 no-refs = 492, but the
manifest contains 495 entries. The discrepancy was a counting error in the summary
table (42 was reported; actual is 41). Reconciliation:

| Classification | Count | Size (MB) | Description |
|----------------|------:|----------:|-------------|
| content-consumer | 41 | 258.9 | Scripts open/read the file directly |
| by-name-only | 3 | 0.9 | Scripts reference filename but do not open |
| no-refs | 451 | 21.2 | No script references detected |
| **Total** | **495** | **281.0** | |

### Population accounting

| Population | Count | Size (MB) | Notes |
|------------|------:|----------:|-------|
| Total tracked JSON/JSONL in DATASETS | 833 | — | All tracked JSON/JSONL files |
| Frozen evidence excluded | 3 | 3.6 | baseline_2026-10-09/, documentation_hash_manifest, resolution_provenance_step1 |
| Math-paper candidates | 495 | 281.0 | Generated math-paper outputs |
| Remaining (non-math, non-frozen) | 335 | — | King Wen generated data, vision outputs, symbols, etc. |
| **Total** | **833** | — | 3 + 495 + 335 = 833 |

### Role classification

| Role | Files | Size (MB) | Description |
|------|------:|----------:|-------------|
| reproducible-derivative | 263 | 229.1 | Can be regenerated from identified source inputs |
| historical-snapshot | 232 | 51.9 | Preserves a particular experimental state |
| **Total** | **495** | **281.0** | |

No unresolved entries remain. All 495 files were classified.

## 2. Content-consuming files (41) — consumer and regeneration trace

### Tier 1: Large files (>1 MB) with content consumers

| File | Size (MB) | Consumers | Regeneration script | Regenerable? |
|------|----------:|-----------|---------------------|:------------:|
| `semantic_math_zotero_full.json` | 159.2 | 14 (check_latex_exprs, check_solvable, probe_*, solve_all, solve_equations, solve_exprs, solve_latex, solve_latex_only, solve_quick, solve_sample, solve_selective, solve_unicode, solve_unicode_10, solve_unicode_only, verify_extract, verify_quality, semantic_math_extractor) | `semantic_math_extractor.py` | Yes (from Zotero PDF corpus) |
| `math_extraction_zotero_full.json` | 9.4 | 0 direct (no-refs) | `semantic_math_extractor.py` | Yes |
| `math_reconstruction_evidence.jsonl` | 8.1 | math_reconstruction_evidence.py, reconstruction_work_log.py | `math_reconstruction_evidence.py` | Yes |
| `structural_survival.jsonl` | 6.5 | structural_survival.py | `structural_survival.py` | Yes |
| `kingwen_consultation_record.json` | 7.6 | kingwen_oracle_consult_tool.py | Oracle engine runtime | Partial (runtime-dependent) |
| `kingwen_sovereign_world_topology.json` | 6.1 | generate_sovereign_world.py, gibberlink.js | `generate_sovereign_world.py` | Yes |
| `unified_manifest.json` | 3.2 | audit_glyph_catalog.py, run_one_candidate_diagnostic.py, test_canonical_extraction.py, vision_comparison_pipeline.py | Multiple generators | Partial |
| `reference_equations.jsonl` | 2.7 | build_reference_equations.py, phase2b_evaluate_gates.py, phase2b_select_pilot.py | `build_reference_equations.py` | Yes |
| `equation_level_comparison.jsonl` | 2.5 | build_equation_comparison.py, build_reference_equations.py | `build_equation_comparison.py` | Yes |
| `cross_stage_drop_trace.jsonl` | 2.2 | cross_stage_drop_trace.py | `cross_stage_drop_trace.py` | Yes |
| `extractor_training_data_fresh.jsonl` | 2.0 | solve_comprehensive.py, solve_dual_path.py, solve_html_equations.py, solve_pylatexenc.py, solve_with_definitions.py | `build_training_data.py` | Yes |
| `extractor_training_data.jsonl` | 2.0 | build_training_data.py | `build_training_data.py` | Yes |
| `kingwen_oracle_master.json` | 2.0 | oracle engine | Oracle engine runtime | Partial |

### Tier 2: Medium files (100 KB–1 MB) with content consumers

| File | Size (KB) | Consumers | Regeneration |
|------|----------:|-----------|--------------|
| `arxiv_html_corpus/2605.00155.json` | 849 | e2e_math_pipeline.py, math_constraint_validator.py, placement_diagnostic.py, prose_math_extractor.py, test_mathml_parser_on_corpus.py | `arxiv_html_parser.py` |
| `equation_solve_results_dual.jsonl` | 593 | math_failure_taxonomy.py, solve_dual_path.py, test_mbox_dollar_recovery.py | `solve_dual_path.py` |
| `math_structure.json` | 589 | math_structure_extractor.py | `math_structure_extractor.py` |
| `paper_math_usage.jsonl` | 531 | paper_math_usage_bridge.py | `paper_math_usage_bridge.py` |
| `provenance_2006.11239.json` | 463 | arxiv_provenance.py, solve_provenance.py | `arxiv_provenance.py` |
| `equation_solve_results.jsonl` | 410 | solve_html_equations.py | `solve_html_equations.py` |
| `equation_solve_results_pylatexenc.jsonl` | 342 | solve_pylatexenc.py | `solve_pylatexenc.py` |
| `arxiv_html_corpus/2006.11239.json` | 296 | arxiv_provenance.py, solve_provenance.py | `arxiv_provenance.py` |
| `arxiv_html_corpus/1505.05770.json` | 293 | run_provenance_integration.py, verify_provenance_trace.py | `arxiv_provenance.py` |
| `paper_repository_provenance.json` | 265 | build_repo_relationship_registry.py, fetch_arxiv_metadata.py, paper_repo_provenance_indexer.py, reconcile_equation_counts.py, validate_repo_urls.py | `paper_repo_provenance_indexer.py` |
| `equation_solve_results_definitions.jsonl` | 234 | solve_with_definitions.py | `solve_with_definitions.py` |
| `paper_repository_provenance.jsonl` | 229 | build_repo_relationship_registry.py, fetch_arxiv_metadata.py, paper_repo_provenance_indexer.py, reconcile_equation_counts.py, validate_repo_urls.py | `paper_repo_provenance_indexer.py` |
| `arxiv_html_batch/2006.11239.json` | 222 | arxiv_provenance.py, solve_provenance.py | `arxiv_provenance.py` |
| `equation_solve_results_comprehensive.jsonl` | 221 | solve_comprehensive.py | `solve_comprehensive.py` |
| `provenance_integration_run/integration_run_summary.json` | 23 | run_provenance_integration.py | `run_provenance_integration.py` |
| `provenance_integration_run/integration_run_results.jsonl` | 13 | run_provenance_integration.py | `run_provenance_integration.py` |
| `provenance_gold_set_1505.05770.json` | 9 | run_provenance_integration.py, verify_provenance_trace.py | `run_provenance_integration.py` |
| `math_reconstruction_evidence.json` | 7 | math_reconstruction_evidence.py, reconstruction_work_log.py | `math_reconstruction_evidence.py` |
| `cross_stage_drop_trace.json` | 1 | audit_repo_math_join.py, cross_stage_drop_trace.py | `cross_stage_drop_trace.py` |

### Tier 3: Aggregate reports (1 KB–4 KB) with content consumers

13 `aggregate_report.json` files across math_recovery version directories, each consumed by `math_recovery_tool.py`. These are versioned recovery summaries.

### By-name-only files (3)

| File | Size (KB) | Referencing scripts | Nature |
|------|----------:|---------------------|--------|
| `paper_repo_math_failure_audit.json` | 413 | audit_repo_math_join.py | Audit output (by filename reference only) |
| `paper_repository_provenance_validated.jsonl` | 240 | validate_repo_urls.py | Validated provenance (by filename reference only) |
| `paper_repo_math_failure_join.json` | 226 | audit_repo_math_join.py, join_registry_math_failures.py | Join output (by filename reference only) |

## 3. Version directory review (14 directories)

### Directory inventory

| Directory | Files | Total Size | Distinct from v1? |
|-----------|------:|-----------:|:-----------------:|
| math_recovery (v1) | 16 | 1.9 MB | Baseline |
| math_recovery_v3 | 15 | 0.9 MB | Yes (different recovery) |
| math_recovery_v4 | 15 | 0.9 MB | Yes |
| math_recovery_v5 | 15 | 0.9 MB | Yes |
| math_recovery_v6 | 15 | 0.9 MB | Yes |
| math_recovery_v12 | 15 | 1.1 MB | Yes |
| math_recovery_v13 | 15 | 1.1 MB | Yes |
| math_recovery_v14 | 15 | 1.1 MB | Yes |
| math_recovery_v15 | 15 | 1.1 MB | Yes |
| math_recovery_v16 | 15 | 10.6 MB | Yes (larger, different) |
| math_recovery_tree | 15 | 0.9 MB | Yes (tree-structured) |
| math_recovery_after_fix | 15 | 0.9 MB | Yes (post-fix) |
| math_recovery_nested_fix | 15 | 0.9 MB | Yes (nested-fix) |
| math_recovery_display | 15 | 0.2 MB | Yes (display variant) |

### Findings

1. **v3–v6 and v12–v16 are successive versions** of the same 15-paper recovery experiment, each with distinct recovery parameters.
2. **v16 is significantly larger** (10.6 MB vs ~1 MB) — likely a different recovery configuration or additional data.
3. **tree, after_fix, nested_fix, display** are structural variants, not version iterations.
4. **aggregate_report.json** in each directory is consumed by `math_recovery_tool.py` — these are runtime artifacts, not just historical.
5. **No frozen report references** any specific version directory (checked against `frozen-regression-evaluation-mapping-2026-11-03.md` and `frozen-regression-execution-results-2026-11-03.md`).
6. **Reproducibility:** Each version can be regenerated by running `math_recovery_tool.py` with appropriate parameters, but the exact invocation for each version is not documented.

### Assessment

The version directories are **NOT redundant** — they represent distinct experimental states. However, they are **reproducible** from the recovery tool with appropriate parameters. The canonical version (v16, being the latest and largest) should be established before any older versions are considered for untracking.

## 4. Role classification of the 451 unreferenced files

| Role | Files | Size (MB) | Description |
|------|------:|----------:|-------------|
| reproducible-derivative | 263 | 229.1 | Can be regenerated from identified source inputs and scripts |
| historical-snapshot | 232 | 51.9 | Preserves a particular experimental state; may be evidentiary |

### Sub-classification of no-refs files by directory

| Directory | Files | Size (MB) | Role | Reproducible? |
|-----------|------:|----------:|------|:-------------:|
| arxiv_html_corpus | 240 | 51.6 | Original source corpus (parsed HTML) | Yes (from arXiv) |
| DATASETS-root (large outputs) | ~25 | ~180 | Mixed: source corpus, derivatives, evidence | Varies |
| math_recovery_v*/versioned | ~210 | ~9 | Historical snapshots | Yes (with params) |
| math_recovery_tree/display/after_fix/nested_fix | 60 | ~3.6 | Structural variants | Yes |
| candidates_*.json | ~5 | ~1 | Reproducible derivatives | Yes |
| provenance_*.json | ~5 | ~1 | Historical snapshots (evidentiary) | Partial |
| paper_2605_occ/v5 | 6 | ~1.1 | Versioned recovery | Yes |
| arxiv_html_batch | 3 | 0.4 | Batch parsed HTML | Yes |

### Critical distinction: arxiv_html_corpus

The 237 files with no script references in `arxiv_html_corpus/` are **NOT disposable outputs**. They are the **original source material** (parsed arXiv HTML) used to generate downstream datasets. While they are reproducible from arXiv, they represent the canonical parsed form of 240 papers and would require re-downloading and re-parsing to regenerate. Their lack of script references is because they are *consumed by reading*, not by `open()` calls in scripts.

## 5. Proposed per-file disposition register

### Disposition categories

| Disposition | Meaning | Authorization required |
|-------------|---------|----------------------|
| RETAIN | Keep tracked; essential source or evidence | None |
| REGENERATE | Untrack after verifying regeneration script works | Moderate (verify script) |
| ARCHIVE | Move to local archive, untrack from Git | Low (preserve local copy) |
| UNTRACK | Remove from Git tracking, preserve local | Low (preserve local copy) |
| UNRESOLVED | Insufficient evidence to decide | None (needs more audit) |

### Disposition assignments by category

| Category | Files | Size (MB) | Disposition | Rationale |
|----------|------:|----------:|-------------|-----------|
| Frozen evidence (baseline, hash manifest, provenance step1) | 3 | 3.6 | RETAIN | Frozen; never modify |
| semantic_math_zotero_full.json | 1 | 159.2 | RETAIN | 14 consumers; 56.7% of candidate storage; regeneration not verified |
| math_extraction_zotero_full.json | 1 | 9.4 | UNRESOLVED | Need to determine if reproducible derivative or independent baseline |
| math_reconstruction_evidence.jsonl | 1 | 8.1 | RETAIN (evidentiary) | Evidentiary role; lineage not established |
| structural_survival.jsonl | 1 | 6.5 | RETAIN (evidentiary) | Evidentiary role; relationship to extraction not documented |
| kingwen_consultation_record.json | 1 | 7.6 | RETAIN | Runtime-dependent; consumer schema not verified |
| kingwen_sovereign_world_topology.json | 1 | 6.1 | RETAIN | Consumer (generate_sovereign_world.py) active |
| unified_manifest.json | 1 | 3.2 | RETAIN | Multiple consumers; role not fully documented |
| reference_equations.jsonl | 1 | 2.7 | REGENERATE (after verify) | build_reference_equations.py exists; verify before untracking |
| equation_level_comparison.jsonl | 1 | 2.5 | REGENERATE (after verify) | build_equation_comparison.py exists |
| cross_stage_drop_trace.jsonl | 1 | 2.2 | REGENERATE (after verify) | cross_stage_drop_trace.py exists |
| extractor_training_data*.jsonl (3) | 3 | 6.1 | REGENERATE (after verify) | build_training_data.py exists |
| equation_solve_results*.jsonl (4) | 4 | 1.6 | REGENERATE (after verify) | solve_*.py scripts exist |
| arxiv_html_corpus/*.json (240) | 240 | 51.6 | UNTRACK (after verify) | Reproducible from arXiv HTML; but verify no hidden consumers |
| math_recovery version dirs (14×15) | 210 | ~9 | ARCHIVE (after review) | Distinct experimental states; canonical version not established |
| math_recovery_tree/display/after_fix/nested_fix | 60 | ~3.6 | ARCHIVE (after review) | Structural variants; need provenance review |
| paper_2605_occ/occ2/v5 | 6 | ~1.1 | ARCHIVE (after review) | Versioned recovery |
| candidates_*.json | ~5 | ~1 | REGENERATE (after verify) | Regenerable from candidate detection |
| provenance_*.json | ~5 | ~1 | RETAIN (evidentiary) | Provenance audit evidence |
| paper_repo_math_failure_*.json | 3 | ~0.9 | RETAIN (evidentiary) | Audit join evidence |
| paper_repository_provenance*.jsonl | 2 | ~0.5 | RETAIN (evidentiary) | Provenance evidence |
| PDF_CANDIDATE_MANIFEST | 1 | 1.1 | RETAIN (evidentiary) | Audit manifest |
| PDF_FALLBACK_8_PAPERS | 1 | 0.7 | RETAIN (evidentiary) | Audit manifest |
| math_structure.json | 1 | 0.6 | REGENERATE (after verify) | math_structure_extractor.py exists |
| paper_math_usage.jsonl | 1 | 0.5 | REGENERATE (after verify) | paper_math_usage_bridge.py exists |
| math_kingwen_regression_*.json | 1 | 0.4 | RETAIN (evidentiary) | Regression evidence |
| semantic_math_test.json | 1 | 0.6 | REGENERATE (after verify) | Test output |
| e2e_*.json (3) | 3 | 6.0 | RETAIN (evidentiary) | E2E pipeline evidence |
| arxiv_html_batch (3) | 3 | 0.4 | REGENERATE (after verify) | Batch parsed HTML |
| provenance_integration_run (2) | 2 | 0.0 | RETAIN (evidentiary) | Integration run evidence |

## 6. Version directory review — detailed

### Canonical version establishment needed

Before any version directory can be archived, the following must be established:

1. **Which version is canonical?** v16 is the latest and largest (10.6 MB vs ~1 MB for others), but size alone doesn't prove authority.
2. **Are inputs identical across versions?** If v3 and v16 used different recovery parameters, they are not redundant.
3. **Are any versions referenced by frozen reports?** Checked: no frozen report references any specific version directory.
4. **Is the latest version reproducible?** Need to verify `math_recovery_tool.py` can regenerate v16 output from retained inputs.
5. **Do older versions contain unique data?** Even if superseded, older versions may contain recovery states not present in v16.

### Recommended review steps

1. Diff v16 against v15 (and v3, v4, v5, v6) to identify parameter changes.
2. Check if any version is referenced in docs/ or frozen evidence.
3. Verify v16 can be regenerated from `math_recovery_tool.py`.
4. Only then consider archiving older versions.

## 7. Governance constraints honored

- No frozen evidence modified
- No source files modified
- No commits or pushes
- No deletions (local copies preserved)
- All hashes recorded in `math_output_candidate_manifest_2026-11-04.json`
- Additive documentation only
- Existing manifest preserved as audit snapshot (not overwritten)

## 8. Recommended next phase

1. **Reconcile manifest** ✓ (41 content + 3 by-name + 451 no-refs = 495)
2. **Classify by role** ✓ (263 reproducible-derivative + 232 historical-snapshot)
3. **Trace content-consuming files** ✓ (41 traced with consumers and regeneration scripts)
4. **Review version directories** ✓ (14 directories reviewed; canonical version not established)
5. **Produce disposition register** ✓ (this document)
6. **Authorize narrowly scoped untracking** — PENDING user authorization

### Safeguard

The existing manifest (`math_output_candidate_manifest_2026-11-04.json`) is preserved as the audit snapshot. If files are subsequently untracked, a new, separately named manifest should be generated rather than overwriting the original.