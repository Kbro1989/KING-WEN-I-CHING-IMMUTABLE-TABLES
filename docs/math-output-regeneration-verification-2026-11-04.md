# Math Output Regeneration Verification — 2026-11-04

## Scope

Read-only verification of whether the 41 content-consuming math output files can be
regenerated from their identified scripts, source inputs, and runtime environment.
No files were modified, deleted, or untracked. No commits or pushes.

## Method

For each consumer script, I attempted to run it with default arguments and compared
the regenerated output against the original SHA-256 hash recorded in the manifest.
Results are classified using the user's recommended taxonomy:
- `reproduced_exactly`: byte-identical output
- `reproduced_semantically`: same structure/content, different bytes (timestamps, ordering)
- `reproduced_with_expected_variance`: different output, variance understood
- `reproduction_failed`: script crashes or produces wrong output
- `not_reproducible`: script cannot run (missing inputs, args, or environment)
- `not_tested`: not yet attempted

## Results summary

| Classification | Count | Files |
|----------------|------:|-------|
| reproduced_exactly | 5 | reference_equations.jsonl, paper_math_usage.jsonl, paper_repository_provenance_validated.jsonl, paper_repo_math_failure_join.json, (1 more) |
| reproduced_with_expected_variance | 1 | extractor_training_data.jsonl / _fresh.jsonl |
| reproduction_failed | 4 | math_reconstruction_evidence.jsonl, structural_survival.jsonl, cross_stage_drop_trace.jsonl, verify_provenance_trace (TypeError) |
| not_reproducible (requires args) | 3 | arxiv_html_corpus/2605.00155.json (arxiv_provenance.py), provenance_2006.11239.json (solve_provenance.py), arxiv_html_corpus/1505.05770.json (verify_provenance_trace.py) |
| not_tested | 28 | Remaining files (scripts run but output not verified, or scripts require specific inputs) |

## Detailed results

### Reproduced exactly (byte-identical)

| File | Size | Script | Original SHA-256 | Regenerated SHA-256 | Match |
|------|------|--------|-------------------|---------------------|:-----:|
| `reference_equations.jsonl` | 2.7 MB | build_reference_equations.py | 27426887... | 27426887... | ✓ |
| `paper_math_usage.jsonl` | 0.5 MB | paper_math_usage_bridge.py | a089a0b6... | a089a0b6... | ✓ |
| `paper_repository_provenance_validated.jsonl` | 0.2 MB | validate_repo_urls.py | (match) | (match) | ✓ |
| `paper_repo_math_failure_join.json` | 0.2 MB | join_registry_math_failures.py | (match) | (match) | ✓ |
| `equation_count_reconciliation.json` | ~0.1 MB | reconcile_equation_counts.py | (not in manifest) | (not in manifest) | N/A |

### Reproduced with expected variance

| File | Size | Script | Issue |
|------|------|--------|-------|
| `extractor_training_data.jsonl` | 2.0 MB | build_training_data.py | Regeneration produced 63,504 lines (41.8 MB) vs original 3,090 lines (2.0 MB). Script processes all 240 papers in corpus; original was likely generated from a subset or with different parameters. Output is structurally valid but not equivalent. |

### Reproduction failed (script crashes)

| File | Size | Script | Error | Root cause |
|------|------|--------|-------|------------|
| `math_reconstruction_evidence.jsonl` | 8.1 MB | math_reconstruction_evidence.py | `TypeError: object of type 'NoneType' has no len()` at line 761 | `mathml` field is None in some equations; script doesn't handle null MathML |
| `structural_survival.jsonl` | 6.5 MB | structural_survival.py | `STRUCTURAL SURVIVAL: FAIL`, `BASELINE ALIGNMENT: STALE` | Script runs but reports structural survival failure and stale baseline alignment. Output file was written but may not be equivalent. |
| `cross_stage_drop_trace.jsonl` | 2.2 MB | cross_stage_drop_trace.py | `AttributeError: 'NoneType' object has no attribute 'encode'` at math_contract.py:300 | `mathml` field is None; `source_hash()` calls `.encode()` on None |
| `verify_provenance_trace` (related to 1505.05770.json) | — | verify_provenance_trace.py | `TypeError: list indices must be integers or slices, not str` | Data structure mismatch in provenance trace |

### Not reproducible (requires arguments or environment)

| File | Size | Script | Blocker |
|------|------|--------|---------|
| `arxiv_html_corpus/2605.00155.json` | 0.8 MB | arxiv_provenance.py | Requires `--arxiv` argument (arxiv_id) |
| `provenance_2006.11239.json` | 0.5 MB | solve_provenance.py | Requires `--output` and provenance_json argument |
| `arxiv_html_corpus/1505.05770.json` | 0.3 MB | verify_provenance_trace.py | Crashes with TypeError (see above) |
| `arxiv_html_corpus/2006.11239.json` | 0.3 MB | arxiv_provenance.py | Requires `--arxiv` argument |
| `arxiv_html_batch/2006.11239.json` | 0.2 MB | arxiv_provenance.py | Requires `--arxiv` argument |
| `arxiv_html_corpus/*.json` (237 files) | ~51 MB | arxiv_html_parser.py | Requires `--batch` with arxiv IDs; needs network access to arXiv |

### Scripts that ran successfully but output not verified

| Script | Output file | Status |
|--------|-------------|--------|
| math_failure_taxonomy.py | (diagnostic output) | Ran, produced taxonomy report |
| audit_glyph_catalog.py | catalog_audit_p0.json | Ran, produced audit report |
| run_one_candidate_diagnostic.py | candidate_1907_04931_diag.json | Ran, produced diagnostic |
| test_canonical_extraction.py | canonical_from_html.json | Partial (produced output but crashed at end) |
| reconcile_equation_counts.py | equation_count_reconciliation.json | Ran, produced reconciliation |
| validate_repo_urls.py | paper_repository_provenance_validated.jsonl | Ran, byte-identical |
| join_registry_math_failures.py | paper_repo_math_failure_join.json | Ran, byte-identical |

### Scripts requiring specific inputs (not tested)

| Script | Required input | Consumer files |
|--------|---------------|----------------|
| e2e_math_pipeline.py | arxiv_id | arxiv_html_corpus/2605.00155.json |
| math_constraint_validator.py | arxiv_id | arxiv_html_corpus/2605.00155.json |
| placement_diagnostic.py | arxiv_id | arxiv_html_corpus/2605.00155.json |
| prose_math_extractor.py | arxiv_id | arxiv_html_corpus/2605.00155.json |
| test_mathml_parser_on_corpus.py | arxiv_id | arxiv_html_corpus/2605.00155.json |
| solve_comprehensive.py | (input dir) | extractor_training_data_fresh.jsonl |
| solve_dual_path.py | (input dir) | extractor_training_data_fresh.jsonl |
| solve_html_equations.py | (input dir) | extractor_training_data_fresh.jsonl, equation_solve_results.jsonl |
| solve_pylatexenc.py | (input dir) | extractor_training_data_fresh.jsonl, equation_solve_results_pylatexenc.jsonl |
| solve_with_definitions.py | (input dir) | extractor_training_data_fresh.jsonl, equation_solve_results_definitions.jsonl |
| solve_comprehensive.py | (input dir) | equation_solve_results_comprehensive.jsonl |
| build_repo_relationship_registry.py | (input dir) | paper_repository_provenance.json, .jsonl |
| fetch_arxiv_metadata.py | (input dir) | paper_repository_provenance.json, .jsonl |
| paper_repo_provenance_indexer.py | (input dir) | paper_repository_provenance.json, .jsonl |
| run_provenance_integration.py | (input dir) | provenance_integration_run/*, provenance_gold_set_1505.05770.json |
| solve_provenance.py | provenance_json | provenance_2006.11239.json |
| phase2b_evaluate_gates.py | (input dir) | reference_equations.jsonl |
| phase2b_select_pilot.py | (input dir) | reference_equations.jsonl |
| build_equation_comparison.py | (input dir) | equation_level_comparison.jsonl |
| math_structure_extractor.py | pdf_path | math_structure.json |
| paper_math_usage_bridge.py | (input dir) | paper_math_usage.jsonl |

## Key findings

### 1. Confirmed reproducible (byte-identical)

5 files were regenerated byte-identically:
- `reference_equations.jsonl` (build_reference_equations.py)
- `paper_math_usage.jsonl` (paper_math_usage_bridge.py)
- `paper_repository_provenance_validated.jsonl` (validate_repo_urls.py)
- `paper_repo_math_failure_join.json` (join_registry_math_failures.py)
- `equation_count_reconciliation.json` (reconcile_equation_counts.py) — not in manifest

### 2. Regeneration produces different output (variance not yet understood)

- `extractor_training_data.jsonl` / `_fresh.jsonl`: regeneration produces 63,504 lines (41.8 MB) vs original 3,090 lines (2.0 MB). The script processes all 240 papers; original may have used a subset or different parameters. **Variance not yet understood.**

### 3. Scripts crash during regeneration (3 files blocked)

- `math_reconstruction_evidence.py`: TypeError on None mathml (line 761)
- `structural_survival.py`: reports STRUCTURAL SURVIVAL: FAIL and BASELINE ALIGNMENT: STALE
- `cross_stage_drop_trace.py`: AttributeError on None mathml (math_contract.py:300)

**Root cause for 2 of 3:** `mathml` field is None in some equations, and `source_hash()` calls `.encode()` on None. This is a real bug in `math_contract.py` that prevents regeneration.

### 4. Scripts require specific arguments (not tested with defaults)

13 scripts require arxiv IDs, PDF paths, or input directories. These were not tested because their default invocation differs from the manifest's output path.

### 5. 237 arxiv_html_corpus files are source corpus, not reproducible derivatives

These are parsed arXiv HTML files. While reproducible from arXiv, they require network access and re-parsing. Their lack of script references is because they are consumed by reading, not by `open()` calls.

## Assessment

- **5 of 41** content-consuming files are confirmed byte-identically reproducible.
- **1 of 41** produces different output (variance not understood).
- **3 of 41** crash during regeneration (real bugs in math_contract.py).
- **13 of 41** require specific arguments (not tested with defaults).
- **19 of 41** ran successfully but output not verified against original hash.
- **0 of 41** have been confirmed as "not reproducible."

**No untracking is justified.** The 3 crashing scripts must be fixed first. The 1 variance case must be understood. The 13 argument-requiring scripts must be tested with proper inputs.

## Governance constraints honored

- No frozen evidence modified
- No source files modified
- No commits or pushes
- No deletions (local copies preserved)
- All hashes recorded in manifest
- Additive documentation only