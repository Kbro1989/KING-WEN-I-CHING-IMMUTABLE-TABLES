# Post-`c40286cd6a` Development Reconciliation Ledger
**Date:** 2026-11-05  
**Scope:** Reconciling Committed Git History (`3cbffa0958` $\to$ `c40286cd6a`) with Uncommitted Post-Commit Pipeline Developments and the MPRD Reproducibility Register  
**Governing Rule:**
* **Git history** establishes *when and why* an artifact entered the repository.
* **Current tests and reproducibility evidence** establish *what it does now*.
* **The MPRD register** establishes *what remains unresolved*.

---

## 1. The Seven Committed Development Phases

The 123 commits between the rebased baseline (`3cbffa0958`, equivalent to `74e44a9791`) and `HEAD` ([`c40286cd6a`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/.gitignore)) established the foundational eight-layer architecture of the King Wen mathematical extraction system:

| Phase | Commit Range | Established Capability | Primary Landed Artifacts | Architectural Significance |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | `dd8d26c81f` $\to$ `7172dd32d1`<br>(Merge `b7e126d20d`) | Evidence chains and benchmark freezing | [`scripts/build_repo_relationship_registry.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/build_repo_relationship_registry.py)<br>[`scripts/build_benchmark_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/build_benchmark_manifest.py)<br>[`tests/test_benchmark_readiness.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_benchmark_readiness.py) | Pinned input fixtures; established relational joins between arXiv papers, code repos, and extraction failures. |
| **Phase 2** | `bdfd5eeaea` $\to$ `ecaa272771` | Visual math fidelity & combinatorics | [`symbols/symbols/`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/symbols/symbols/)<br>[`scripts/validators/stirling_transform.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validators/stirling_transform.py)<br>[`scripts/vision_comparison_pipeline.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/vision_comparison_pipeline.py) | Built symbol template library; validated numerical/symbolic Stirling transforms; tested cross-paper layout generalization. |
| **Phase 3** | `4d98c49c78` $\to$ `c032acc314` | Crop auditing and evaluator hardening | [`scripts/audit_candidate_crops.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_candidate_crops.py)<br>[`scripts/evaluate_output_reference.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_output_reference.py)<br>[`scripts/build_visual_review_log.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/build_visual_review_log.py)<br>[`scripts/phase2c_token_alignment.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/phase2c_token_alignment.py) | Fixed `evaluate_output()` argument inversion; established 3-axis visual review of 21 candidates; implemented whole-token LCS alignment. |
| **Phase 4** | `d6e1c09aec` $\to$ `4b32e4b83a` | Five-gate evaluation framework | [`scripts/phase2c_gate_library.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/phase2c_gate_library.py)<br>[`scripts/phase2c_evaluate_gates.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/phase2c_evaluate_gates.py)<br>[`scripts/phase2c_heldout_expanded_evaluate.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/phase2c_heldout_expanded_evaluate.py) | Formulated 5 verification gates (syntax, bounds, operators, semantics, numerical residuals); tested held-out sets with non-identical negative controls. |
| **Phase 5** | `4f4257ab41` $\to$ `a7692bfdbe` | Source-to-visual traceability | [`scripts/verify_provenance_trace.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/verify_provenance_trace.py)<br>[`scripts/run_provenance_integration.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/run_provenance_integration.py)<br>[`tests/test_equation_reconciliation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_equation_reconciliation.py) | Traced equations from HTML source through parser SHA to PDF crops; validated 5-equation gold set from `1505.05770` (Normalizing Flows). |
| **Phase 6** | `b0c7d27738` $\to$ `87f4d34c8d` | Pix2Text harvesting & adjudication | [`scripts/pix2text_harvest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/pix2text_harvest.py)<br>[`scripts/adjudicate_candidates_v2.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/adjudicate_candidates_v2.py)<br>[`scripts/adjudicate_targets.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/adjudicate_targets.py)<br>[`scripts/test_adjudication_consistency.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/test_adjudication_consistency.py) | Added candidate harvesting with page-scoped element IDs; established adjudication states (`MATCHED`, `REJECTED`, `AMBIGUOUS`) with explicit denominators. |
| **Phase 7** | `85edfa696f` $\to$ `c40286cd6a` | Tooling integration & cleanup | [`docs/lua-math-tool.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/lua-math-tool.md)<br>[`scripts/full_hexagram_shotgun.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/full_hexagram_shotgun.py)<br>`DATASETS/` (quarantine) | Mapped 41 Python math scripts to unified Lua plugin; fixed Pylance diagnostics; quarantined corrupted JSONL streams. |

---

## 2. Significant Post-Commit Developments (Working-Tree State)

Following commit `c40286cd6a`, the system underwent substantial development in the working tree across detection, parsing, occurrence accounting, and reproducibility diagnostics:

```
[Raw PDF / PyMuPDF] ───────► Character Geometry Detector (scripts/targeted_math_detector.py)
                                     │
[Spatial Representation] ───► Spatial-Syntactic Preservation Spec (docs/spatial-syntactic-preservation-specification.md)
                                     │
[Candidate Processing] ────► Targeted Depth OCR (scripts/targeted_depth_ocr.py)
                             OCR Polarity Ablation (scripts/polarity_ablation.py)
                             15-Region Pilot (2009.00031 p5)
                                     │
[Mathematical Parsing] ────► Six-Layer Parsing (scripts/schauberger_parsing_layers.py)
                             MathML Tree Parser (scripts/mathml_parser.py)
                             Semantic Math Extractor (scripts/semantic_math_extractor.py)
                                     │
[Reproducibility & Ledger] ─► MPRD-001 Repair (tests/test_source_hash_none_mathml.py)
                             Occurrence Lifecycle Ledger (docs/occurrence-lifecycle-ledger-contract-2026-11-03.md)
                             MPRD-002, 003, 004, 005, 006 Diagnostic Reports
```

### Detailed Component Inventory:
1. **Raw PDF Character Geometry Detector:** [`scripts/targeted_math_detector.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_math_detector.py), [`tests/test_detect_math_regions_on_page.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_detect_math_regions_on_page.py), and [`tests/test_extract_text_boundaries.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_extract_text_boundaries.py) operate directly on PyMuPDF character-level dictionaries to extract math spans without rasterization.
2. **Targeted Depth OCR:** [`scripts/targeted_depth_ocr.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_depth_ocr.py) and [`scripts/controlled_depth_run.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/controlled_depth_run.py) render high-resolution crops at variable zoom levels ($4\times, 8\times$) and depth passes.
3. **OCR Polarity Ablation:** [`scripts/polarity_ablation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/polarity_ablation.py) and [`scripts/ocr_polarity_ablation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/ocr_polarity_ablation.py) evaluate recognition sensitivity across inverted contrast polarities.
4. **Spatial-Syntactic Preservation Specification:** [`docs/spatial-syntactic-preservation-specification.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/spatial-syntactic-preservation-specification.md) establishes the formal representation for two-dimensional mathematical arrangements (scripts, fraction bars, stretched delimiters, line continuations).
5. **Six-Layer PDF Math Parser:** [`scripts/schauberger_parsing_layers.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/schauberger_parsing_layers.py) and [`scripts/semantic_math_extractor.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/semantic_math_extractor.py) separate text blocks, inline math, display equations, and tabular environments.
6. **Occurrence Lifecycle Ledger:** [`docs/occurrence-lifecycle-ledger-contract-2026-11-03.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/occurrence-lifecycle-ledger-contract-2026-11-03.md) and [`scripts/reconcile_occurrences.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/reconcile_occurrences.py) formalize immutable occurrence keys across multiple extraction runs.
7. **Math Pipeline Reproducibility Defect Register (MPRD):** [`docs/math-pipeline-reproducibility-defect-register-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/math-pipeline-reproducibility-defect-register-2026-11-04.md) and dedicated diagnostic reports (`mprd002`, `mprd003`, `mprd004`).

---

## 3. Which Existing Capabilities Were Extended

1. **Candidate Generation:** Extended from fixed-size bounding boxes to multi-scale aspect-ratio crops (tall-narrow aspect $>2.5$ vs wide $>10$ text lines), isolating tall delimiters and multi-line equation arrays.
2. **Fidelity Verification:** Extended from 1D string/token distance to a two-tier evaluation separating *visual crop isolation* from *semantic mathematical agreement*.
3. **AST Comparison:** Extended from alphanumeric token sets to ordered whole-token LCS alignment ([`scripts/phase2c_token_alignment.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/phase2c_token_alignment.py)) and structural subtree matching.
4. **Provenance Tracking:** Extended from single-hash document checks to complete dependency chains linking source HTML SHA-256, parser script SHA-256, character bboxes, crop SHA-256, and frozen evaluation gates.
5. **Identity Invariant:** Formally decoupled occurrence identity (`occurrence_key()`, based on paper + locator + index) from representation identity (`source_hash()`, based on normalized MathML bytes).

---

## 4. Which Defects Were Resolved

| Defect ID / Target | Resolution Date | Affected Components | Nature of Repair & Verification Evidence |
| :--- | :--- | :--- | :--- |
| **MPRD-001** | 2026-11-04 | [`scripts/math_contract.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/math_contract.py)<br>[`scripts/math_reconstruction_evidence.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/math_reconstruction_evidence.py)<br>[`scripts/cross_stage_drop_trace.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/cross_stage_drop_trace.py) | **`source_hash()` NoneType Crash:** Fixed crash when encountering `None` MathML. Contract now returns 3 distinct, deterministic hashes for `None` (unavailable), `""` (empty), and valid MathML. Validated by [`tests/test_source_hash_none_mathml.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_source_hash_none_mathml.py). |
| **MPRD-002** | 2026-11-04 | Corpus occurrence accounting | **Occurrence Count Drop (Closed as Explained):** Confirmed drop was an intended filtering change (transition from un-deduplicated formula fragments to validated, unique occurrence records), not data loss. Documented in [`docs/mprd002-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd002-diagnostic-report-2026-11-04.md). |
| **MPRD-001-compat** | 2026-11-04 | Occurrence key join semantics | **Historical Join Compatibility (Assessed):** Verified that `occurrence_key()` was not altered by the `source_hash()` repair. Historical joins remain valid; no database migration required. |
| **Evaluator Param Bug** | Phase 3 Commit `d782e1f04d` | [`scripts/evaluate_output_reference.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_output_reference.py) | **Argument Inversion:** Fixed parameter order inversion in `evaluate_output(candidate, reference)`. Validated by [`tests/test_evaluate_output_bug.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_evaluate_output_bug.py). |
| **Element ID Collisions** | Phase 6 Commit `09e134287b` | [`scripts/pix2text_harvest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/pix2text_harvest.py) | **Duplicate IDs:** Scoped `pix2text_element_id` per page (`f"p{page}_{idx}"`) preventing cross-page collision. Validated by [`scripts/test_pix2text_harvest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/test_pix2text_harvest.py). |

---

## 5. Specifications & Defects Resolution Status

### Priority 1: Spatial-Syntactic Preservation Specification
* **Specification File:** [`docs/spatial-syntactic-preservation-specification.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/spatial-syntactic-preservation-specification.md)
* **Status:** **IMPLEMENTED & VERIFIED WITH EVIDENCE (2026-11-05 / 2026-11-06)**.
* **Implementation:** Layer A ([`scripts/font_aware_math_classifier.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/font_aware_math_classifier.py)), Layer B ([`scripts/hierarchical_region_proposals.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/hierarchical_region_proposals.py)), and Layer C ([`scripts/hierarchical_region_proposals_v3.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/hierarchical_region_proposals_v3.py)).
* **Verified Outcomes:**
  1. *Subscripts / superscripts:* Adaptive baseline tolerance $\max(3.0, 0.45 \times \text{size}_{\text{max}})$ recovered $T^{\text{pos}}$, $V^{\text{pos}}$, $t_{\text{type}}$, $v_{\text{type}}$ at $\Delta y = 3.1\text{--}3.3\text{ pt}$ (AC-1 satisfied).
  2. *Equation-number decoupling:* Delimited labels decoupled from expression body; `math_expression_bbox` isolated (AC-4 satisfied).
  3. *Multiline continuity:* Structural guardrails requiring shared relation alignment, indentation continuation, or punctuation continuation prevented orphan chimera mergers (AC-3 satisfied; GS-003 prose decoupled).
  4. *Multi-population benchmark:* 10/15 fully preserved, 0 regressions, 15/15 negative controls rejected. Validated by 17 tests in [`tests/test_structural_preservation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_structural_preservation.py).

### Priority 2: MPRD-004 — Bounding-Box Producer-Consumer Contract
* **Diagnostic Report:** [`docs/mprd004-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd004-diagnostic-report-2026-11-04.md)
* **Status:** **RESOLVED & VERIFIED (2026-11-05)**.
* **Resolution:** Normalized bounding-box consumers across [`scripts/audit_candidate_crops.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_candidate_crops.py) and [`tests/test_candidate_audit_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_candidate_audit_manifest.py) to support both dictionary mappings and 4-tuple coordinates. Repaired PyMuPDF / `fitz` import aliasing. All 21 candidate crops verified against source PDFs (21/21 passed).

### Priority 3: MPRD-006 — Source-Corpus Preservation vs Retrieval Reproducibility
* **Status:** **Open investigation**.
* **Issue:** Generating reference equations dynamically from arXiv breaks offline repeatability due to upstream network and format drift.
* **Requirement:** Construct a fully offline reproduction path using the existing 240-paper local corpus in `DATASETS/arxiv_html_corpus/`.

### Priority 4: MPRD-003 Closure — `no_mathml` Population Baseline Disposition
* **Diagnostic Report:** [`docs/mprd003-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd003-diagnostic-report-2026-11-04.md)
* **Status:** **Pending formal baseline disposition**.
* **Issue:** 64 records in the expanded corpus lack MathML representations (`None` MathML).
* **Requirement:** Formally record these 64 records as a documented corpus-data limitation without invalidating the 14-paper frozen baseline (`DATASETS/baseline_2026-10-09/`).

### Priority 5: MPRD-005 — `PYEOF` Heredoc Execution Impact
* **Status:** **Open investigation**.
* **Issue:** Inspect working-tree test artifacts for leaked `PYEOF` strings resulting from shell heredoc execution and verify whether they are purely inert comments or cause runtime defects in test harnesses.

---

## 6. Experiments Producing Measurable Results

| Experiment | Target Scope | Measurable Outcome | Key Takeaway |
| :--- | :--- | :--- | :--- |
| **Pix2Text Crop Isolation** | 21 equations across multiple papers | Baseline isolation: **2/21**<br>Adjusted padding: **17/21**<br>Final configuration: **20/21** | Successful crop isolation does not imply mathematical semantic agreement; they must be evaluated as separate layers. |
| **Provenance Gold Set (`1505.05770`)** | 5 equations from Variational Normalizing Flows | **5/5 VERIFIED** (GS-005 reconciled with 8/8 features; GS-001 corrected) | Proved end-to-end traceability from HTML source $\to$ parser SHA $\to$ PDF crop. |
| **Layer B Baseline Evaluation** | 15 equations across 3 papers + 15 negative controls | **15/15 detected**, 7/15 PRESERVED, 8/15 PARTIAL, **15/15 negative controls rejected** | Established two-population decoupled evaluation invariant. |
| **Layer C Structural Reconstruction** | 15 equations across 3 papers + 15 negative controls | **10/15 PRESERVED** (66.7%), 6 IMPROVED, 0 REGRESSED, **15/15 negative controls rejected** | Adaptive baseline + multiline guardrails + decoupled equation numbers restored ViLT subscripts and prevented prose mergers. |
| **Targeted Adjudication (`1907.04931`)** | Page 12 math comparisons | **126 records adjudicated** with explicit denominators | Established explicit non-lossy adjudication contract preserving all candidate counts. |
| **15-Region Geometry Pilot (`2009.00031` p5)** | Page 5 dense formula regions | 11 tall-narrow + 4 wide = **15 regions**; **15/15 nonempty OCR** | Confirmed tall-narrow bounding captures multiline matrices and arrays that standard horizontal bboxes fragment. |
| **OCR Polarity Ablation** | 8 test formula crops | Normal vs Inverted contrast evaluated | Identified contrast-reversal thresholds for white-on-black vs black-on-white text blocks. |
| **Held-Out Five-Gate Evaluation** | 25 held-out mutated cases & non-identical controls | 100% detection of bounds-swaps and operator mutations across Gates 1–5 | Non-identical negative controls prevent verification leakage. |

---

## 7. Frozen Artifacts (Must Not Be Overwritten)

The following artifacts represent baseline contracts and verification points. Under pipeline invariants, they must not be modified or overwritten during subsequent experiments:

1. `DATASETS/baseline_2026-10-09/`
   - `contract_version.txt` (`2026.10.09-v1`)
   - `manifest.json`
   - `occurrences.jsonl` (3,409 immutable baseline records across 14 papers)
   - `pinned_versions.txt`
   - `run_metadata.json`
2. `DATASETS/FROZEN_INPUTS_2026-10-16.json` (Frozen input fixtures for Marker vs King Wen comparisons).
3. `DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/`
   - `adjudication_report.jsonl`
   - `adjudication_summary.json`
   - `adjudication_targets.jsonl`
   - `crop_00.png` through `crop_06.png` (4x renders and depth maps).
4. `DATASETS/documentation_hash_manifest_2026-11-04.json` (SHA-256 integrity manifest for 200 project documentation files).
5. `DATASETS/resolution_provenance_step1.json` (Step 1 provenance record).
6. [`docs/phase2c_specification.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/phase2c_specification.md) & [`docs/phase2c_closure_record.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/phase2c_closure_record.md) (Frozen criteria for the five-gate evaluator).
7. `DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json` (Blind-render regeneration freeze manifest, 3,644 image files, aggregate hash `b566c01fecff6ca7...`).

---

## 8. Exact Git Commit and Working-Tree Provenance

### Committed Progression (`main` branch)
* `3cbffa0958`: Rebased equivalent of `74e44a9791` (*100% full-page audit scope, strict one-to-one AST matching*).
* `dd8d26c81f` $\to$ `7172dd32d1`: Phase 1 evidence chains, reference sets, and benchmark readiness.
* `b7e126d20d`: Merge resolving dual-branch development histories.
* `bdfd5eeaea` $\to$ `ecaa272771`: Phase 2 symbol assets, Stirling transforms, and generalization suites.
* `4d98c49c78` $\to$ `c032acc314`: Phase 3 candidate crop localization, evaluator argument repair, 21-candidate review.
* `d6e1c09aec` $\to$ `4b32e4b83a`: Phase 4 five-gate evaluation framework, gate calibration, held-out controls.
* `4f4257ab41` $\to$ `a7692bfdbe`: Phase 5 source-to-visual traceability and Normalizing Flows gold set.
* `b0c7d27738` $\to$ `87f4d34c8d`: Phase 6 Pix2Text candidate harvesting and arXiv 1907.04931 adjudication.
* `85edfa696f` $\to$ `c40286cd6a` (HEAD): Phase 7 Lua mapping spec, Pylance diagnostic fixes, JSONL quarantine.

### Uncommitted Working-Tree Files (as of 2026-11-05)
* **Modified tracked files (`M`):**
  - [`scripts/audit_candidate_crops.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_candidate_crops.py) (line 300 active; under MPRD-004 review)
  - [`scripts/math_contract.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/math_contract.py) (contains MPRD-001 `source_hash()` fix)
  - [`scripts/cross_stage_drop_trace.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/cross_stage_drop_trace.py)
  - [`scripts/experiments_multi_paper_generalization.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/experiments_multi_paper_generalization.py)
  - [`scripts/reconcile_occurrences.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/reconcile_occurrences.py)
  - [`scripts/run_provenance_integration.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/run_provenance_integration.py)
  - [`scripts/schauberger_parsing_layers.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/schauberger_parsing_layers.py)
  - [`scripts/semantic_math_extractor.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/semantic_math_extractor.py)
  - [`scripts/vision_comparison_pipeline.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/vision_comparison_pipeline.py)
  - [`tests/test_candidate_audit_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_candidate_audit_manifest.py)
* **Untracked diagnostic & test artifacts (`??`):**
  - [`tests/test_source_hash_none_mathml.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_source_hash_none_mathml.py) (regression test for MPRD-001)
  - [`docs/math-pipeline-reproducibility-defect-register-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/math-pipeline-reproducibility-defect-register-2026-11-04.md)
  - [`docs/mprd002-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd002-diagnostic-report-2026-11-04.md)
  - [`docs/mprd003-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd003-diagnostic-report-2026-11-04.md)
  - [`docs/mprd004-diagnostic-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/mprd004-diagnostic-report-2026-11-04.md)
  - [`docs/spatial-syntactic-preservation-specification.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/spatial-syntactic-preservation-specification.md)
  - [`docs/comparative-reevaluation-report-2026-11-04.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/comparative-reevaluation-report-2026-11-04.md)
  - [`scripts/targeted_math_detector.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_math_detector.py)
  - [`scripts/targeted_depth_ocr.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_depth_ocr.py)
  - [`scripts/polarity_ablation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/polarity_ablation.py)

---

## 9. Strategic Architectural Separation for Next Milestone

To ensure future verification avoids conflating spatial isolation with semantic correctness, subsequent implementation will enforce four independently measured gates:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Detection Gate                                                       │
│    "Where is the mathematical content?"                                 │
│    Metrics: Precision, recall, bounding-box IoU against page geometry. │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ 2. Structural Preservation Gate                                         │
│    "Which symbols belong together, and how?"                            │
│    Metrics: Delimiter extent, script baseline attachment, vinculum     │
│             span, multiline continuity.                                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ 3. Mathematical Reconstruction Gate                                     │
│    "Can the expression be represented in a formal AST / MathML / IR?"   │
│    Metrics: Parser success, non-fabricated tokens, syntax validity.     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ 4. Independent Validation Gate                                          │
│    "Does the reconstructed expression preserve mathematical meaning?"    │
│    Metrics: Five-gate evaluation (bounds, operator substitutions,        │
│             semantic fidelity, numerical residual = 0).                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**Immediate Next Action:** Implement the spatial-syntactic preservation specification against the existing 15-region pilot on arXiv `2009.00031` page 5, rather than initiating another broad detector rewrite.

---

## 10. Milestone 1 Closure Ledger & Audit Disposition (2026-11-05)

### 10.1 Milestone 1 Evidence Ledger

Observer implementation and negative-control fixture established on arXiv `2009.00031` printed page 5 (`doc[4]`):

| Evidence | Reported Result |
| :--- | :--- |
| **Page observations** | 4,001 characters |
| **Negative-control regions** | 15 |
| **Character intersections** | 0 |
| **Character containment** | 0 |
| **Image intersections** | 1–3 per region |
| **Observer tests (`tests/test_spatial_syntactic_observer.py`)** | 10 passed |
| **Structural-preservation tests (`tests/test_structural_preservation.py`)** | 4 passed |
| **Paper-integrity tests (`tests/test_paper_integrity.py`)** | 6 passed |
| **Combined suite** | 20 passed (exit code 0) |

### 10.2 Audit Disposition

| Qualification | Assessment | Details |
| :--- | :--- | :--- |
| **Q1 — Test-run evidence** | **Closed** | PowerShell quoting failure (`python -c`) distinguished from successful pytest test run (`python -m pytest ...`, exit code 0). |
| **Q2 — Image intersection geometry** | **Closed** | Added `ImageIntersectionGeometry` dataclass and `intersecting_image_details` field. Intersection rectangles, areas, and `intersection_over_region` ratios are preserved in JSON and verified by test. |
| **Q3 — Downstream eligibility enforcement** | **Partially closed** | Contract verified via integration harness (`tests/test_structural_preservation.py`); awaiting production consumer implementation. The ledger explicitly records that the integration test verifies the proposed contract across the layer boundary, not production enforcement, as the production expectation generator does not yet exist. |

### 10.3 Next Milestone: Positive Mathematical Population (`1505.05770`)

Following the 7-step sequence:

1. Select five gold equations (GS-001 through GS-005) independently of observer and OCR output.
2. Establish source-page coordinates and exact PDF identity.
3. Run observer without giving gold-equation locations as detection hints.
4. Compare observer's detected regions against independently established gold locations.
5. Assign `PENDING_CLASSIFICATION` to candidates until source evidence supports classification.
6. Record missed gold equations separately from false-positive detections.
7. Only then build structural expectations for approved mathematical regions.

Key metrics remain decoupled:

* Detection recall and false-positive rate
* Source-content classification accuracy
* Spatial relationship preservation
* Syntactic reconstruction fidelity
* Mathematical equivalence

---

## 11. Milestone 2 & 3 Closure: Multi-Paper Validation and Layer C Reconstruction (2026-11-05 / 2026-11-06)

### 11.1 Positive-Control Benchmarks Established
1. **Development Population (`1505.05770`):**
   - 5/5 gold equations verified (`GS-001` through `GS-005`).
   - Corrected GS-001 bounding box (+51.2 pt truncation repair) preserved with audit trail.
   - Preserved verbatim notation for blackboard-bold $\mathbb{ID}_{\text{KL}}$ in GS-005 (8/8 features, IoU 0.9952).
2. **Independent Positive Control 1 (`2102.03334`, ViLT):**
   - 6/6 Transformer equations evaluated on Page 4.
   - Identified root-cause of v2.0 failure: rigid 3.0 pt baseline tolerance split 7 pt scripts.
   - Candidate v3.0 adaptive tolerance recovered $T^{\text{pos}}$, $V^{\text{pos}}$, $t_{\text{type}}$: **3/6 restored to PRESERVED** (up from 0/6), mean expression IoU rose from 0.7076 to 0.8610.
3. **Independent Positive Control 2 (`1406.2661`, GANs):**
   - 4/4 equations evaluated across single-column NIPS layout (Pages 3, 4, 5).
   - GAN-006 achieved 0.9994 IoU under decoupled math expression bounding box.
   - 3/4 PRESERVED, 1/4 PARTIAL, 0 MISSING.
4. **Negative-Control Invariant (`2009.00031` p5):**
   - 15/15 astrophysics plot regions rejected (100.0% rejection rate). Invariant strictly UPHELD.

### 11.2 Tooling Usages & Verification Executables

| Tool / Script | CLI Usage | Purpose / Benchmark Verification |
|---|---|---|
| [`scripts/run_v2_v3_comparison.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/run_v2_v3_comparison.py) | `python scripts/run_v2_v3_comparison.py` | Side-by-side execution comparing Layer B (v2) and Layer C (v3) across all 4 populations. |
| [`scripts/audit_contract_verification_paths.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_contract_verification_paths.py) | `python scripts/audit_contract_verification_paths.py` | Machine-checks the 6 gates (G1–G6) and 3 reference domains of the cyber-physical engineering contract. |
| [`scripts/targeted_depth_ocr.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_depth_ocr.py) | `python scripts/targeted_depth_ocr.py --paper 2009.00031 --page 5 --zoom 4` | Targeted high-zoom OCR for stretched symbols (tall delimiters, multiline arrays, fraction bars). |
| [`scripts/targeted_math_detector.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_math_detector.py) | `python scripts/targeted_math_detector.py PDF_PATH --pages 4 --zoom 4 --out DIR` | Character-geometry observation detector utilizing PyMuPDF `rawdict` character bounds. |
| [`scripts/audit_candidate_crops.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_candidate_crops.py) | `python scripts/audit_candidate_crops.py` | Machine-checked audit verifying 21 candidate crops against source PDF text boundaries. |
| [`scripts/evaluate_structural_completeness_b2.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_structural_completeness_b2.py) | `python scripts/evaluate_structural_completeness_b2.py` | Unified Layer B baseline evaluator across all three positive populations. |
| [`tests/test_structural_preservation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_structural_preservation.py) | `python -m pytest tests/test_structural_preservation.py` | 17 integration tests verifying eligibility gating, dual bbox schemas, and Layer C acceptance criteria. |
| [`scripts/freeze_1505_blind_renders_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/freeze_1505_blind_renders_manifest.py) | `python scripts/freeze_1505_blind_renders_manifest.py` | Generates SHA-256 freeze manifest and verifies input/evaluation isolation for `1505.05770` blind renders. |
| [`scripts/delimiter_aware_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/delimiter_aware_structural_recovery.py) | `python scripts/delimiter_aware_structural_recovery.py` | Delimiter-aware structural recovery engine (Gates D1–D6) reconstructing scalable delimited enclosures. |

---

## 12. Milestone 4 Closure: 1505.05770 Blind-Render Regeneration and Pipeline Revalidation (2026-11-05 / 2026-11-06)

### 12.1 Regeneration Integrity & Exact Accounting
Following detection engine updates, all 3,644 rendered images in `DATASETS/structural_preservation/1505.05770_blind_renders/` were cleared and regenerated cleanly from the frozen source PDF and detector without introducing regressions.

| Evidence Category | Page 2 | Page 3 | Total |
|---|---|---|---|
| PDF text spans | 221 | 247 | 468 |
| Extracted characters | 4,609 | 4,436 | 9,045 |
| Geometry candidates | 28 | 52 | 80 |
| Visual component crops (`component_*.png`) | 1,867 | 1,773 | 3,640 |
| Full-page diagnostic images (`page_render.png`, `page_threshold.png`) | 2 | 2 | 4 |
| **Total image artifacts regenerated** | **1,869** | **1,775** | **3,644** |

- **Source PDF SHA-256:** `776e07c2b5cf56963a6c3d2d5727146baa8ac096435db17df06d9b2a3a44f70a` (matches manifest).
- **Detector Script SHA-256:** `78651d74afc8e71d2f2de952963905a5cfb56696c071109d10cfd1903ab41949`.
- **All Renders Aggregate SHA-256:** `b566c01fecff6ca74678644d3f56b630f8b0cb67bd8ee7eb4a6c49be4fb00bd5`.
- **Freeze Manifest:** [`DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json).

### 12.2 Four-Point Verification Ledger
1. **Render Determinism:** Cryptographic hash captured per page directory and across all 3,644 files (`b566c01fecff...`).
2. **Input Isolation:** Machine-checked verification confirming [`scripts/blind_detection_run_1505.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/blind_detection_run_1505.py) and [`scripts/targeted_math_detector.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/targeted_math_detector.py) contain zero imports, references, or knowledge of gold manifests, gold bounding boxes, or equation identifiers (`GS-001` through `GS-005`). Candidate generation is strictly blind.
3. **Output Lineage:** Generated candidate records in `1505.05770_blind_detection_p002.json` and `p003.json` explicitly map every component to source page index, pixel coordinates (`bbox_render_px`), MuPDF point coordinates (`bbox_pdf_pt_approx`), candidate reasons, and the detector version and hash.
4. **Evaluation Isolation & Artifact Freshness:** Gold annotations enter exclusively at downstream evaluation (`scripts/positive_control_comparison.py`), which loads detection JSONs and verifies source PDF hashes before reading the gold manifest. Timestamp auditing verified all downstream outputs were produced in non-stale chronological succession.

### 12.3 Revalidated Scoreboard
- **Structural Completeness B2 Recall:** 15/15 (100.0%) across all three positive populations.
- **Negative Control Rejection:** 15/15 (100.0%) on `2009.00031` Page 5.
- **Layer B (v2) to Layer C (v3) Preservation:** 10/15 (66.7%) preserved.
- **Evaluated Regressions:** 0 (6 improved, 9 unchanged, 0 regressed).
- **Delimiter Recovery:** Canonical $7 \times 7$ matrix recovered (7/7 effective rows, 0 px border contact).
- **Repository Regression Suite:** 569 / 569 passing tests (including 5 certified reconciliation tests).

### 12.4 Gold-to-Component Evidence Reconciliation Ledger
1. **GS-002 Operator Inventory Discrepancy Resolved:**
   - Discrepancy identified between standard textbook VAE notation (which expresses the score gradient identity with an equality `$=$`) and the actual arXiv publication `1505.05770` (Rezende & Mohamed 2015, Section 2).
   - Machine verification of the source PDF character stream (font CMSY10 `0x21d4`) and source MathML confirms the authors literally formatted this display using the biconditional operator `\Leftrightarrow`, not `$=$`.
   - The test suite [`tests/test_gold_to_component_reconciliation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_gold_to_component_reconciliation.py) verifies the operator inventories across all 5 gold equations against source verbatim.
2. **Component Identifier Namespaces Clarified:**
   - `page_candidate_index`: 0-based local sequential index within filtered candidates on that page, producing filenames `component_{idx:04d}.png` (`component_0000.png` through `component_1866.png` on Page 2).
   - `opencv_component_id`: 1-based global label integer returned by OpenCV `connectedComponentsWithStats` on the full binarized page image (e.g. Component `#4241`).
3. **Dual-Channel Complementary Recovery (GS-004):**
   - The PDF text stream drops the stretched integral operator $\int$ (`has_integral_operator: false`, leading to a `PARTIAL` verdict).
   - The visual candidate channel independently and cleanly recovers the tall integral operator in `page_0002/component_1568.png` (OpenCV `#4241`, aspect ratio 2.472, PDF bbox `[133.25, 598.0, 142.25, 620.25]`).
4. **Multi-Metric Independence:**
   - Geometric localization (IoU) is decoupled from structural fidelity. GS-003 achieves full structural feature fidelity (7/7 features, `PRESERVED`) under a loose bounding box (IoU 0.3916), while GS-004 fails structural fidelity (5/6 features, `PARTIAL`) despite higher geometric IoU (0.5170).

### 12.5 End-to-End Audit Completion and Adversarial Operator Disambiguation

**12.5.1 End-to-End Audit Output**

Script: [`scripts/audit_gold_equation_chains_1505.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/audit_gold_equation_chains_1505.py)
Output: [`DATASETS/structural_preservation/1505.05770_end_to_end_audit.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/1505.05770_end_to_end_audit.json)
Output SHA-256: `6fdc6ce984da9f01921d00202a02fdd84da5c992b201953c4435d6a1bdacba09`
Output size: 47,869 bytes

| Gold Equation | Page | Structural Verdict | Features | IoU    | Visual Candidates in Region | Notes                              |
|---------------|------|--------------------|----------|--------|-----------------------------|------------------------------------|
| GS-001        | 3    | PRESERVED          | 8/8      | 0.5289 | 11                          | Equivalence and distribution notation recovered |
| GS-002        | 3    | PRESERVED          | 6/6      | 0.4772 | 15                          | Biconditional ⇔ correctly present  |
| GS-003        | 3    | PRESERVED          | 7/7      | 0.3916 | 65                          | Low IoU; full structural fidelity  |
| GS-004        | 2    | PARTIAL            | 5/6      | 0.5170 | 12 (1 visual-only)          | ∫ absent from text stream; visually recovered as component_1568.png |
| GS-005        | 2    | PRESERVED          | 8/8      | 0.9952 | 24                          | High geometric precision; ‖ KL separator confirmed |

Summary: 4 PRESERVED, 1 PARTIAL, 0 MISSING. 1 cross-channel recovery case (GS-004 integral). 4 adversarial operator cases documented.

**12.5.2 Adversarial Operator Disambiguation Cases (ADV-001 through ADV-004)**

| Case   | Equation | Operator Present                    | Operator Absent / Confused With        | Evidence Channel          |
|--------|----------|-------------------------------------|----------------------------------------|---------------------------|
| ADV-001 | GS-002  | ⇔ (U+21D4, biconditional)           | = (U+003D, equals)                     | PDF text + HTML LaTeX     |
| ADV-002 | GS-001  | ∼ (U+223C, `\sim`, distributed-as)  | ≈ (U+2248, approximately-equal)        | HTML LaTeX verbatim       |
| ADV-003 | GS-002  | ⇔ (U+21D4, biconditional)           | ⇒ (U+21D2, implication)               | PDF text stream           |
| ADV-004 | GS-005  | `\|` (double-bar, KL separator)     | `|` (U+007C, single-bar conditional)   | HTML LaTeX verbatim       |

ADV-004 structural note: `\|` appears exactly once as a binary infix KL-divergence separator in `q_φ(z|x) ‖ p(z)`, not as a matched-pair norm delimiter. The three single `|` occurrences are conditional bars in `q(z|x)` and `p(x|z)`. Detector implementations must not conflate the two.

**12.5.3 Test Suite Extension**

Two new tests added to [`tests/test_gold_to_component_reconciliation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_gold_to_component_reconciliation.py) (SHA-256: `ff466cce4763c9d5b0917c24ae5638dc228f5d230a4b6a773f2e3478eb1ca6da`):

- **Test 6 — `test_adversarial_operator_disambiguation`:** Asserts all four ADV cases by Unicode codepoint, verifying that biconditional is not confused with equals, tilde-operator is not confused with approximately-equal, biconditional is not confused with implication, and double-bar is not confused with single-bar.
- **Test 7 — `test_source_channel_attribution`:** Pins each gold equation's operators to their source extraction channel (HTML LaTeX verbatim and MuPDF PDF text stream independently), enforcing dual-channel consistency for GS-002 and cross-channel divergence for GS-004 (source LaTeX has `\int`; PDF extraction drops it).

**Full regression suite: 571/571 passing** (up from 569; 2 new adversarial tests).

### 12.6 Freeze Manifest v2.0 Final Seal
- **Freeze Manifest Path:** [`DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/1505.05770_blind_renders_freeze_manifest.json)
- **Manifest Self-Hash (SHA-256):** `02d7af7a95e8cf930ec543ba64672fb174afd3ea0840df9436742f605dee65db`
- **Verification Script:** [`scripts/scratch/verify_freeze_manifest_v3.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/scratch/verify_freeze_manifest_v3.py)
- **Audit Findings:** All 8 verification dimensions (3,644 individual image hashes, aggregate hash `b566c01f...`, source PDF hash, detector hash, downstream audit freshness, 571 regression count, and disk-vs-record identity) verified as strictly matching.

---

## 13. Rahmani Generalization Benchmark: Multi-Column Matrix Recovery (arXiv:1212.0957 Page 8)

### 13.1 Strict Isolation Boundary
The Rahmani matrix target (`RAHMANI-1212.0957-P008-MATRIX`) is an independent generalization challenge registered outside the `1505.05770` positive control population. It tests whether the delimiter-aware structural recovery pipeline generalizes from single-column tall vectors to wide, multi-column enclosures ($6 \times 6$ numeric grid + continuation indicators) without pipeline overfitting or parameter retraining.

### 13.2 Generalization Target Registration
- **Target Specification:** [`DATASETS/structural_preservation/rahmani_1212.0957_generalization_target.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/rahmani_1212.0957_generalization_target.json)
- **Target JSON SHA-256:** `2775435bf9013584436a69932fc929e629c85cf11a2fa4bd9dcdfebafd8a1091`
- **Source Document:** `arXiv:1212.0957` (Mourad Rahmani, *Generalized Stirling transform*), Page 8 (0-based page 7)
- **Source PDF SHA-256:** `1c734a4e0a29c8eae4b94d8033351b62bf8411a78e5d9798b904dcd4e86c14d1`
- **Prefix:** `S =` at `[202.80, 425.62, 221.84, 444.27]`
- **Opening Delimiter:** Parenthesis (`(`) at `[224.88, 381.89, 234.43, 493.20]`, CMEX10 font lineage, aspect ratio 11.66
- **Closing Delimiter:** Parenthesis (`)`) at `[399.60, 381.89, 409.15, 493.20]`, CMEX10 font lineage, aspect ratio 11.66
- **Matrix Grid:** 6 numeric rows $\times$ 6 columns + Row 0 horizontal ellipsis (`···`) + Row 6 vertical continuation (`⋮`)
- **Trailing External Boundary:** Inline equation $A_0(z) = \frac{e^z}{1+z}$ and prose at $y \in [483.11, 538.53]$ must remain strictly outside the matrix enclosure.

### 13.3 Independent Generalization Evaluation Results
Script: [`scripts/evaluate_rahmani_generalization.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_rahmani_generalization.py)
Report: [`DATASETS/structural_preservation/rahmani_1212.0957_generalization_evaluation.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/rahmani_1212.0957_generalization_evaluation.json)
Report SHA-256: `a7377eaabb24ed40c479a6a8150c7aea5d51876cca5995abb5f9ef2853ecd187`
**Pipeline State:** Unmodified Baseline ([`scripts/delimiter_aware_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/delimiter_aware_structural_recovery.py) SHA-256: `8211592af549c292...`)
**Overall Generalization Verdict:** **PASSED_UNMODIFIED**

| Gate / Criterion | Evaluation Result | Verdict |
|---|---|---|
| **Criterion 1: Independent Detection** | Both opening (CMEX10 U+F8EB..ED) and closing (CMEX10 U+F8F6..F8) detected | **PASS** |
| **Criterion 2: Correct Pairing** | Pair formed with compatibility score 1.00; horizontal span $[228.0, 406.0]$ pt | **PASS** |
| **Criterion 3: Column/Row Ordering** | All 6 numeric rows and 6 columns matched reference values in exact index order | **PASS** |
| **Criterion 4: Ellipsis Preservation** | Horizontal `···` preserved in Row 0; vertical `⋮` preserved in Row 6 | **PASS** |
| **Criterion 5: Boundary Isolation** | Enclosure $y_1 = 482.25$ pt; trailing equation $y_0 = 483.11$ pt cleanly excluded | **PASS** |
| **Criterion 6: AST Preservation** | Maps to LaTeX `\begin{pmatrix} ... \end{pmatrix}` ($7 \times 6$ effective grid) | **PASS** |
| **Criterion 7: Mathematical Fidelity** | Cell value error rate: 0.0% (exact agreement across all 42 tokens) | **PASS** |

#### Negative Controls Evaluation
| Negative Control Case | Guard Mechanism | Verdict |
|---|---|---|
| **NEG_001: Mismatched Delimiters** | Opening parenthesis + closing bracket pair rejected ($0$ pairs formed) | **PASS** |
| **NEG_002: Missing Closing Delimiter** | Unpaired opening candidate preserved as single structural token; no speculative box | **PASS** |
| **NEG_003: Adjacent Matrix Cross-Association** | Intervening delimiter guard forces 2 distinct pairs; zero cross-over | **PASS** |
| **NEG_004: Tall Non-Math Graphic** | Aspect ratio and non-CMEX font lineage safely rejected from delimiter classification | **PASS** |

**Regression Suite Status:** 575 / 575 passing tests (including 4 dedicated Rahmani generalization certification tests). Zero regressions introduced.

### 13.4 Audit Details Reconciliation (2A, 2B, 2C)

#### 13.4.1 Audit Detail 2A: Effective Matrix Dimensions & 40-Token Accounting
- **Layout Convention:**
  - 6 numeric rows $\times$ 6 columns = 36 numeric cell tokens.
  - Row 0 horizontal ellipsis (`···`) = 3 dot tokens (`['·', '·', '·']`), indicating series continuation for $m \ge 6$.
  - Row 6 vertical continuation (`⋮`) = 1 token (`['...']`), indicating matrix row continuation for $r \ge 6$.
  - **Total grid tokens in recovered structure:** $36 + 3 + 1 = 40$ tokens.
  - The AST translation targets a $7 \times 6$ `pmatrix` layout where Row 0 carries the horizontal truncation annotation at column index 6, Rows 1–5 carry $1 \times 6$ numeric vectors, and Row 6 carries the vertical truncation annotation at column index 0.

#### 13.4.2 Audit Detail 2B: Trailing Expression Boundary & Geometric Perturbation Analysis
- Delimiter enclosure bottom $y_1 = 480.25$ pt.
- First trailing glyph ascender (numerator $e^z$ of $\frac{e^z}{1+z}$) begins at $y_0 = 483.11$ pt.
- Separation gutter: $\Delta y = 483.11 - 480.25 = 2.86$ pt.
- Clamping algorithm: `crop_y1 = y1 + max(2, min((y_max_bound - y1) / 2, 8))` produces $y_1 = 482.25$ pt, leaving an exact margin of $0.86$ pt below the crop.
- **Perturbation Testing:**
  - Displacements $\Delta y \in [-1.0, +5.0]$ pt tested against PyMuPDF word extraction: **0 trailing tokens absorbed** (effective centroid elevation of $e^z$ provides $\approx 7.5$ pt buffer).
  - Adversarial sensitivity check at $\Delta y = +10.0$ pt confirms trailing text detection triggers as expected.

#### 13.4.3 Audit Detail 2C: Five-Tier Mathematical Fidelity Breakdown
1. **Tier 1 — Numeric Token Accuracy:** 36 / 36 numeric cells match gold reference exactly with negative signs preserved (cell value error rate: $0.0\%$).
2. **Tier 2 — Row/Column Topology:** $6 \times 6$ coordinate matrix structure strictly preserved.
3. **Tier 3 — Continuation Semantics:** Horizontal ellipsis (Row 0, Col 6) and vertical continuation (Row 6, Col 0) are semantically differentiated.
4. **Tier 4 — Enclosure Semantics:** CMEX10 extensible tall delimiters map directly to LaTeX `pmatrix`, rejecting single-line punctuation flattening.
5. **Tier 5 — Full Display Expression:** Prefix `S =` unified with enclosure; external trailing equation $A_0(z) = \frac{e^z}{1+z}$ completely excluded.

### 13.5 Rahmani Generalization Benchmark Freeze Manifest
- **Manifest Path:** [`DATASETS/structural_preservation/rahmani_1212.0957_generalization_freeze_manifest.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/rahmani_1212.0957_generalization_freeze_manifest.json)
- **Manifest Self-Hash (SHA-256):** `8ee78a756cb45cdbcfcb8438e477eb4439b37d278083fbfeabda7918636a6a2c`
- **Source PDF:** `1212.0957.pdf` (`1c734a4e0a29c8eae4b94d8033351b62bf8411a78e5d9798b904dcd4e86c14d1`)
- **Unmodified Engine Hash:** `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1` (matches baseline `8211592af549c292...`)
- **Generalization Target Hash:** `b7ed54e3a03a93fdb8ab586f8ccb9d9132e71f7512d74a1e5121c7741d5295e4`
- **Evaluation Output Hash:** `a7377eaabb24ed40c479a6a8150c7aea5d51876cca5995abb5f9ef2853ecd187`
- **Evaluation Script Hash:** `2a303cc6b61f3dc0781c46e03aa725fe6e6b63f5d293278ed2be307b89d6b0ea`
- **Generalization Test Suite Hash:** `2c1644d3c9b275ff336611254dc2eccdd0ab515487c2523bb5737611a5eaef4e`
- **Regression Suite:** 575 passed in 20.94s.

---

## 14. Cross-Paper Delimiter Generalization v1: Acceptance Specification Deliverable

### 14.1 Acceptance Contract & Schema Deliverable
Following closure of the single-paper benchmarks, the acceptance contract for the cross-paper evaluation suite was formalized and frozen before any new source papers are selected or ingested.

- **Machine Specification:** [`DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json)
  - Authoritative On-Disk & Frozen Evaluation SHA-256: `188ac350a7b50166d34ac6dabcc00c7a49d540b0e01873e684739f614304b4ae`
  - Preliminary Staging / Reconnaissance Hash: `0368689c5da4a854054acb22c2f5085d208b542b618b77ae1eaa28c7c9e2119a` (superseded by CRLF line-ending normalization prior to case registry generation)
- **Specification Protocol Document:** [`docs/CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/docs/CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md)
  - SHA-256: `34fc1b3e2f91ac78ea63d2ab36381ccb2d7b2f4bdf9619c32a0645e0f3428f38`
- **Automated Schema & Policy Validator:** [`scripts/validate_cross_paper_generalization_spec.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validate_cross_paper_generalization_spec.py)
  - SHA-256: `5678ddbee16f9c498e450855407a421cf3bcabbe579520722fafd39444140112`
- **Unit & Certification Test Suite:** [`tests/test_cross_paper_generalization_spec.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_cross_paper_generalization_spec.py)
  - SHA-256: `6b84b9a33b170e530596751169b794140606b46ea98e675dfbf153e981c43f99`

### 14.2 Seven Test Families Specification
| Family ID | Name | Required Evidence | Primary Failure Mode |
|---|---|---|---|
| `FAM_001` | Delimiter Identity | `bmatrix`, `Bmatrix`, `pmatrix`, `vmatrix` | Wrong enclosure type or inline flattening |
| `FAM_002` | Nested Structures | Parent-child delimiter hierarchy (matrix in parens, etc.) | Flattened nesting or collision |
| `FAM_003` | Adjacent Matrices | Independent candidate associations along horizontal band | Cross-pairing over intervening delimiters |
| `FAM_004` | Embedded Mathematics | Fractions and multiline expressions inside cells | Cell structure collapse or row corruption |
| `FAM_005` | Extensible Glyphs | Complete assembly of top, ext, and bottom glyph pieces | Truncated height or missing pieces |
| `FAM_006` | Continuation Symbols | Correct ellipsis identity and grid position ($\cdots, \vdots, \ddots$) | Semantic substitution or dropped dots |
| `FAM_007` | Prose Adjacency | Independent boundary isolation against adjacent text | Text contamination or equation absorption |

### 14.3 Strict Five-Axis Conjunctive Policy
$$\text{Verdict} = \bigwedge_{i=1}^5 \left(\text{Dim}_i == \text{PASS}\right)$$
- If any dimension fails $\to$ `FAILED`.
- If any measurement is missing $\to$ `NOT_VERIFIED` (never an inferred pass).
- No composite score, harmonic mean, or IoU metric overrides a failed mandatory dimension.

### 14.4 Structural Layout Invariant
Downstream evaluators must strictly distinguish between:
- **Structural Layout Geometry:** The $7 \times 6$ layout dimensions of the matrix environment.
- **Populated Cell Count:** The 40 recovered tokens (36 numeric cells + 3 horizontal dot tokens in Row 0 + 1 vertical continuation token in Row 6).
Evaluators must never assume that a $7 \times 6$ matrix implies 42 fully populated numeric cells.

### 14.5 Full Repository Test Suite Status
- Command: `python -m pytest tests/`
- Result: **580 passed in 20.96s** (up from 575; 5 new specification validation tests). Zero regressions.

---

## 15. Development Environment Remediation, Reproducibility Boundary, and Manifest Registration

### 15.1 Static-Analysis & Environment Disconnect Root Cause
Following the completion of Cross-Paper Generalization v1 specification, IDE static analysis (Pyrefly) emitted missing-module diagnostics across core files ([`scripts/delimiter_aware_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/delimiter_aware_structural_recovery.py), [`scripts/freeze_1505_blind_renders_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/freeze_1505_blind_renders_manifest.py), [`tests/test_delimiter_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_delimiter_structural_recovery.py)) for `pymupdf`, `cv2`, `numpy`, `pytest`, and `delimiter_aware_structural_recovery`.

Investigation revealed two architectural factors:
1. **Virtual Environment Isolation Disconnect:** The repository `.venv` had `include-system-site-packages = false` in `.venv/pyvenv.cfg`. The language server evaluated against `.venv`, where dependencies were absent.
2. **Static Search Path Evaluation:** Pyrefly evaluates module imports before runtime execution of dynamic `sys.path.insert(0, str(REPO_ROOT / "scripts"))`.

### 15.2 Surgical Remediation
1. **System Site-Packages Inheritance:** Enabled `include-system-site-packages = true` in [`.venv/pyvenv.cfg`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/.venv/pyvenv.cfg).
2. **Local Machine Path File:** Created [`.venv/Lib/site-packages/kingwen_paths.pth`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/.venv/Lib/site-packages/kingwen_paths.pth) registering `KING-WEN-I-CHING-IMMUTABLE-TABLES` and `KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts`.
3. **Repository Cleanliness Guard:** Explicitly added `.venv/` to [`.gitignore`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/.gitignore) to ensure machine-specific path files and virtual environments are never committed to version control.

### 15.3 Strict Reproducibility Boundary & Environment Separation
Enabling system site-packages inheritance introduces a critical reproducibility boundary. The repository strictly separates:
- **Historical Frozen Rendering Baseline:** PyMuPDF 1.25.3, OpenCV 4.11.0, NumPy 2.2.3. The 3,644 rendered images and benchmark ledger hashes for `1505.05770` and `1212.0957` are cryptographically locked in their freeze manifests and **MUST NOT be regenerated**.
- **Active Development & Regression Environment:** PyMuPDF 1.28.2, OpenCV 5.0.0, NumPy 2.4.6, pytest 9.1.1 under Python 3.11.9. This environment is designated for test execution and development; it makes no claim to hermetic isolation.
- **Future Generalization Experiments:** Cross-paper evaluations will run against frozen source PDFs under explicit provenance logging.

### 15.4 Development Environment Manifest
The complete environment state, dependency inventory, and path configurations were formally recorded in:
- **Artifact:** [`DATASETS/structural_preservation/development_environment_manifest.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/development_environment_manifest.json)
- **Manifest SHA-256:** `4ab874f2cf9a035fca991f6fcba29a982a4647f4f73fc7e99e0429f85b1afeeb`
- **Engine Baseline Hash Verified:** `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1` (unchanged).

### 15.5 Verification Closure Status
- Environment import resolution: **PASS**
- Internal module resolution at runtime: **PASS**
- Full regression suite under `.venv`: **PASS (580/580 passed in 19.92s)**
- Frozen recovery engine integrity: **PASS**
- Historical rendering baseline separation: **PRESERVED**
- Static analysis (Pyrefly) diagnostics: **PENDING EXPLICIT IDE RELOAD**

---

## 16. Two-Level Cross-Paper Case Registry v1 (Independent Ground Truth Frozen)

### 16.1 Design Principles & Engine Isolation
Following the v1 acceptance specification, the Two-Level Case Registry was constructed strictly from independent character-level stream extraction and manual transcription **without executing the recovery engine**. This guarantees that gold reference ASTs, constituent glyph inventories, and bounding boxes are completely isolated from detector-derived assumptions.

The registry explicitly implements status state progression:
$$\text{ANNOTATED} \longrightarrow \text{VALIDATED} \longrightarrow \text{FROZEN}$$

### 16.2 Two-Level Architectural Structure
1. **Paper Records (Level 1):** Captures paper metadata, exact PDF SHA-256, coordinate systems, font inventories, and typography classifications.
   - `PAPER_01_CLUSTER_GCN` (`arXiv:1905.07953`, KDD 2019): TX Fonts (`txexs`, `txsys`, `LinLibertine`). PDF SHA-256: `5e37bd23d65f...`.
   - `PAPER_02_VILT` (`arXiv:2102.03334`, ICML 2021): Computer Modern / Nimbus Roman Type 1 math (`CMR10`, `CMMI10`, `CMSY10`). PDF SHA-256: `916b5f4abe2b...`.
   - `PAPER_03_LINEAR_PROBING` (`arXiv:2605.24856`, 2026): Latin Modern Math (`LMMathExtension10-Regular`, `LMMathSymbols10-Regular`). PDF SHA-256: `6f9ec8acdb97...`.
2. **Case Records (Level 2):** Captures case IDs, exact display bboxes, gold mathematical ASTs, constituent piece inventories, 5-axis acceptance criteria, and complete negative control sets.
   - `CP-001-CLUSTER-GCN-BMATRIX`: Verified 7-piece extensible brackets in `txexs` ($h=41.24$ pt), 3 distinct continuation directions ($\cdots, \vdots, \ddots$), and adjacent $\bar{A}$ block matrix distractor.
   - `CP-002-VILT-NESTED-BRACKETS`: Verified nested sequence concatenation vector $\mathbf{z}_0 = [\bar{\mathbf{t}} + \mathbf{t}_{\text{type}}; \bar{\mathbf{v}} + \mathbf{v}_{\text{type}}]$ (FAM_002), strictly distinguished from a 2D matrix, with tight 2.45 pt vertical equation gutters.
   - `CP-003-LINEAR-PROBING-NORM`: Verified 3-piece extensible norm bars in `LMMathExtension10-Regular` ($h=21.92$ pt), trailing superscript $^2$ boundary isolation guard, and embedded fraction $\frac{1}{2}$.

### 16.3 Dedicated Validator & Unit Test Suite
- Dedicated Validator Script: [`scripts/validate_cross_paper_case_registry.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validate_cross_paper_case_registry.py)
- Unit Test Suite: [`tests/test_cross_paper_case_registry.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_cross_paper_case_registry.py) (6 tests)
- Full Regression Count: **586 passed in 26.23s** (zero regressions across all 586 tests).

### 16.4 Cryptographic Freeze Manifest
- Registry Artifact: [`DATASETS/structural_preservation/cross_paper_case_registry_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_case_registry_v1.json)
  - Status: **FROZEN**
  - Registry SHA-256: `da4c166b7a5c7b1808d33b2d9f2ca0d71a0d60bf19d6844796506a51da36e6ba`
- Freeze Generator: [`scripts/freeze_cross_paper_case_registry_manifest.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/freeze_cross_paper_case_registry_manifest.py)
- Freeze Manifest: [`DATASETS/structural_preservation/cross_paper_case_registry_freeze_manifest.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_case_registry_freeze_manifest.json)
  - Manifest Self-Hash: `66bcf276accfae67f845a05fb38f4e44c4c80316ce3c1a7e6e9c4051f79d693a`
  - Delimiter Engine Baseline SHA-256 Verified: `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1` (100% untouched)


## 17. Cross-Paper Generalization v1 Evaluation: Baseline Results and Failure Mode Analysis

### 17.1 Evaluation Execution

The unchanged frozen engine (`scripts/delimiter_aware_structural_recovery.py`, SHA-256: `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1`) was evaluated against the three frozen cross-paper cases via [`scripts/evaluate_cross_paper_generalization_v1.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/evaluate_cross_paper_generalization_v1.py).

Evaluation report:
- Artifact: [`DATASETS/structural_preservation/cross_paper_generalization_evaluation_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_generalization_evaluation_v1.json)
- Report SHA-256: `85320ae710afe3af4cb56c626691c6c76b9f93611258610d11eb76d505614454`

Verdict summary (conjunctive strict five-axis policy):

| Case ID | Verdict |
| ------- | ------- |
| `CP-001-CLUSTER-GCN-BMATRIX` | **FAILED** |
| `CP-002-VILT-NESTED-BRACKETS` | **FAILED** |
| `CP-003-LINEAR-PROBING-NORM` | **FAILED** |

This is the correct baseline result. All three cases fail because the frozen engine was designed and validated against CMEX10 font streams; the cross-paper evaluation intentionally probes its limits on three typographically distinct papers.

### 17.2 Per-Case Failure Mode Analysis

#### CP-001 (Cluster-GCN, TX Fonts)

| Dimension | Status | Root Cause |
| --------- | ------ | ---------- |
| dim_1 Geometric Localization | **FAIL** | Recovered enclosure bbox `[112.15, 480.13, 234.61, 525.37]` does not match target `[116.15, 476.58, 230.61, 523.37]` (prefix absorber adds padding beyond bounding box of delimiter pair) |
| dim_2 Glyph Completeness | **FAIL** | `txexs` glyph `U+F8EE` classified as `brace` (CMEX10 table lookup), not `bracket`. `U+F8F9` (closing top) classified as `unknown`. Font-program bias in CMEX map. |
| dim_3 Structural Recovery | **PASS** | 3×3 block grid topology correctly recovered; pairs despite misclassification |
| dim_4 Semantic Fidelity | **FAIL** | Environment misidentified as `brace` instead of `bmatrix` (consequence of dim_2 failure) |
| dim_5 Boundary Isolation | **PASS** | Preceding `A = \bar{A} + \Delta =` correctly excluded |

**Architectural takeaway:** The CMEX Private Use Area mapping (`U+F8EE`→`brace_top`) is calibrated to CMEX10 only. TX Fonts share the same PUA codepoints but map them to bracket parts. A font-family-aware lookup table—branching on `txexs` vs `cmex10`—is the minimum required fix. This is a targeted addition to the font glyph classification gate, not a structural change to the recovery algorithm.

#### CP-002 (ViLT, Computer Modern)

| Dimension | Status | Root Cause |
| --------- | ------ | ---------- |
| dim_1 Geometric Localization | **FAIL** | Recovered enclosure bbox `[326.49, 534.41, 421.91, 548.37]` covers only the innermost bracket row of the multi-line expression. The target spans `y=[503.45, 546.60]` across two display rows and a subscript line. `build_enclosure_completeness` uses only the delimiter pair's y-span; it does not expand to cover the full multi-line display sequence. |
| dim_2 Glyph Completeness | **PASS** | Standard CMR10 `U+005B` / `U+005D` correctly recognized by `STANDARD_DELIMITER_MAP` |
| dim_3 Structural Recovery | **PASS** | Sequence vector concatenation structure correctly retained (not misclassified as 2D matrix) |
| dim_4 Semantic Fidelity | **PASS** | Semicolon-delimited multimodal elements verified |
| dim_5 Boundary Isolation | **PASS** | Equation (4) excluded across tight 2.45 pt gutter |

**Architectural takeaway:** The enclosure bbox expansion logic anchors on the delimiter glyph bboxes alone. For multi-line sequence vector expressions, the full display bbox extends beyond the innermost bracket row. The engine needs a vertical content-scan pass within the delimiter band, not just the delimiter pair's immediate y-span. This is a targeted enhancement to `build_enclosure_completeness`, not a structural rewrite.

#### CP-003 (Linear Probing, Latin Modern Math Extension)

| Dimension | Status | Root Cause |
| --------- | ------ | ---------- |
| dim_1 Geometric Localization | **FAIL** | Enclosure bbox `[227.49, 143.11, 352.74, 175.03]` truncates the closing delimiter at $x=352.74$ while the full expression (including trailing superscript) extends to $x=379.31$ |
| dim_2 Glyph Completeness | **FAIL** | `LMMathExtension10-Regular` emits `U+000D` (ASCII 13 / CR) for `/vextenddouble`. Neither `STANDARD_DELIMITER_MAP` nor the CMEX PUA table contains code 13. Classification: `unknown`, confidence 0.0. |
| dim_3 Structural Recovery | **FAIL** | Cascades from dim_2: unrecognized glyph means no orientation is assigned; `is_opening=None` means the pairing condition fails at the kind-match check |
| dim_4 Semantic Fidelity | **FAIL** | Cascades from dim_2 / dim_3: norm delimiter unrecognized |
| dim_5 Boundary Isolation | **PASS** | Trailing prose (`where \bar{h}_A^{(l)}...`) correctly excluded |

**Architectural takeaway:** The Latin Modern Math Extension encoding uses the PDF Type 1 Encoding Object's `/Differences` array to remap character code 13 to PostScript glyph name `/vextenddouble`. PyMuPDF delivers `\r` (the raw byte value 13). The fix requires an encoding-aware glyph-name resolver: when a font's encoding maps code 13 → `/vextenddouble`, the glyph classifier must look up `/vextenddouble` in a PostScript glyph name table that includes TeX Math Extension glyph names, not just Unicode codepoints. This is targeted to the font classification gate.

### 17.3 Negative Control Results

| Control | CP-001 | CP-002 | CP-003 | Notes |
| ------- | ------ | ------ | ------ | ----- |
| `NEG_MISMATCHED_DELIMITER_TYPES` | **FAIL** | **FAIL** | **FAIL** | Known engine limitation (see §17.4) |
| `NEG_MISSING_CLOSING_PARTNER` | PASS | PASS | PASS | Unpaired opening correctly preserved |
| `NEG_INTERVENING_DELIMITER_COLLISION` | PASS | PASS | PASS | Adjacent pairs correctly separated |
| `NEG_TALL_NON_MATH_GRAPHIC` | PASS | PASS | PASS | Tall non-math region classified unknown / low-confidence |

### 17.4 Known Engine Limitation: NEG_MISMATCHED_DELIMITER_TYPES

`associate_delimiter_pairs` accepts a pair at a threshold of `score >= 0.70`. When two candidates have perfect vertical overlap and equal height, their geometric score is:

$$\text{score} = \underbrace{1.0 \times 0.4}_{\text{y\_iou}} + \underbrace{1.0 \times 0.3}_{\text{h\_ratio}} + \underbrace{0.0}_{\text{kind\_mismatch}} = 0.70$$

This equals the threshold exactly. The kind-mismatch penalty (`+0.0` instead of `+0.3`) is insufficient to reject the pair when geometry is favorable. The correct fix is to make kind-match a **hard gate** (strict rejection) rather than a soft scoring component. This would cause `NEG_MISMATCHED_DELIMITER_TYPES` to pass without changing any other pairing behavior in the existing passing tests.

This limitation is **explicitly documented** in `tests/test_cross_paper_generalization_evaluation.py` (test `test_neg_mismatched_delimiter_types_is_documented_failure`), which asserts `FAIL` as the expected baseline behavior. Any future fix must cause this test to be updated to assert `PASS`.

### 17.5 Five-Axis Summary (Across All Three Cases)

| Dimension | CP-001 | CP-002 | CP-003 | Shared root cause cluster |
| --------- | ------ | ------ | ------ | ------------------------- |
| dim_1 Geometric Localization | FAIL | FAIL | FAIL | Enclosure bbox expansion; multi-line and trailing-token coverage |
| dim_2 Glyph Completeness | FAIL | PASS | FAIL | Font-program table coverage (txexs PUA; LM Math Extension encoding) |
| dim_3 Structural Recovery | PASS | PASS | FAIL | Cascades from dim_2 for CP-003 only |
| dim_4 Semantic Fidelity | FAIL | PASS | FAIL | Cascades from dim_2 misclassification |
| dim_5 Boundary Isolation | PASS | PASS | PASS | **Fully preserved across all three cases** |

**Strongest result:** `dim_5_boundary_isolation` PASS in all three cases. The engine correctly isolates external content in every case despite failing on font classification and bbox coverage. This confirms that the boundary isolation mechanism generalizes across typographies, even when the core delimiter classification does not.

### 17.6 Evaluation Test Suite

[`tests/test_cross_paper_generalization_evaluation.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_cross_paper_generalization_evaluation.py) — **44 tests, 44 passed in 0.11s**.

The test suite asserts:
- Report artifact SHA-256 and input hashes (engine, spec, registry).
- All five dimensions present and valid for each case.
- All four negative controls present and valid for each case.
- Conjunctive verdict consistency (verdict matches observed dimension statuses).
- Specific baseline engine behaviors per case (what the unchanged engine actually does).
- Known engine limitation (`NEG_MISMATCHED_DELIMITER_TYPES` asserted **FAIL** as a documented baseline).

Full regression suite after adding evaluation tests: **630 / 630 passed** (586 existing + 44 new).

### 17.7 Structural Evidence Graph: Next Development Direction

The evaluation results confirm three targeted gaps that can be addressed without modifying the frozen engine:

1. **Font-program-aware glyph table extension** (dim_2: txexs + LMMathExtension10 encoding).
2. **Multi-line enclosure bbox expansion** (dim_1: extend y-band beyond the delimiter pair y-span).
3. **Kind-match hard gate** (NEG_MISMATCHED: convert score component to rejection guard).

In parallel, the cross-paper evaluation produced a richer understanding of the evidence structure: each recovered equation involves multiple heterogeneous observation channels (PDF text stream, font glyph identity, geometric bbox, continuation topology, gold AST). These channels can agree or disagree, and disagreement currently causes silent failure rather than an explicit diagnostic object.

A planned `structural_evidence_graph` module will represent these cross-modal relationships as an explicit, inspectable graph—following the architectural principle identified in ContractShield (Tran-Duong et al., arXiv:2604.02771)—using PyGraphviz for DOT-format visualization. This module will operate as a non-invasive diagnostic layer that does not modify the frozen engine, registry, or acceptance specification.

---

## 18. Implementation-Level Comparative Study & v2 Foundational Implementations (2026-11-06)

### 18.1 Pinned Retrieval of 16 External Reference Source Files
To avoid ungrounded architectural comparisons, 16 authoritative source files were retrieved directly from external repositories (OmniDocBench, PureDocBench, MinerU, UniMERNet, PaddleOCR, TeleOCR) without downloading full repositories or installing third-party packages. Each retrieved file is cryptographically inventoried in [`references/comparative_study/fetch_manifest.json`](../references/comparative_study/fetch_manifest.json) (self-hash `7e1634b16323a60a...`).

### 18.2 Empirical & Architectural Findings Resolved
1. **MinerU Intermediate Data-Flow Decoupling:** Reclassified from "source-file destruction" to "intermediate display-equation text suppression". In TXT mode, DocVortex suppresses native equation text from model output, materializes image crops at `images/page_{page_idx}_equation_{parent_index}.{ext}`, and routes raster images to downstream OCR recognizers while leaving the source PDF file untouched.
2. **UniMERNet Crop Margin vs. PDF Vector Geometry:** Independent verification in [`scripts/experiments/glyph_source_boundary_audit.py`](../scripts/experiments/glyph_source_boundary_audit.py) established that UniMERNet's zero-margin cropping achieves 100% foreground pixel retention on supplied ROIs, but forces 0 px perimeter margins. Crucially, the 89-pixel reduction in `CP-002` was proven to be pure whitespace removal ($43.37$ pt of empty margin to the right of the closing bracket `]`), not glyph loss.
3. **OmniDocBench CDM Token Collisions:** Automated cataloging revealed 44 normalization rules collapsed into 30 buckets, conflating essential mathematical operators (`\cdot \to .`, `\lVert \to \|`, `\sim \to =`). This confirmed the architectural requirement for a 3-channel evaluation boundary separating raw string matching (Channel A), perceptual alignment (Channel B), and semantic structural certification (Channel C).

### 18.3 Four Foundational v2 Modules Implemented & Regression-Tested
All modules were implemented strictly outside the frozen v1 boundary, adhering to cross-platform UTF-8 invariants and zero package installations:

1. **Content-Addressed Degradation Harness:** [`scripts/robustness/degradation_harness.py`](../scripts/robustness/degradation_harness.py)
   - Implements PureDocBench's 15 operations across 4 stages (print, paper, capture, digital).
   - Enforces content-addressed seeding: $S = \text{SHA-256}(H_{\text{source}} \parallel H_{\text{profile}} \parallel \text{seed\_version})$ and $s_{32} = \text{int}(S[:8], 16) \pmod{2^{32}}$.
   - Preserves both 256-bit digest and 32-bit PRNG seed alongside RFC 8785 canonical JSON serialization.
   - Tested in [`tests/test_degradation_harness.py`](../tests/test_degradation_harness.py): **19 / 19 passed**.

2. **Versioned Case-Registry Patch Overlay:** [`scripts/case_registry_patch_manager.py`](../scripts/case_registry_patch_manager.py)
   - Implements PureDocBench's non-mutating correction schema (`patch_id`, `target_registry_hash`, `field_path`, `old_value`, `new_value`, `reviewer`, `reason`, `patch_sha256`).
   - Produces in-memory overlays for v2 consumers while preserving the frozen baseline file on disk.
   - Tested in [`tests/test_case_registry_patch_manager.py`](../tests/test_case_registry_patch_manager.py): **4 / 4 passed**.

3. **OmniDocBench Hungarian CDM Evaluation Adapter:** [`scripts/external_metrics/cdm_adapter.py`](../scripts/external_metrics/cdm_adapter.py)
   - Provides Channel B perceptual similarity evaluation using `scipy.optimize.linear_sum_assignment` and self-contained Wagner-Fischer Levenshtein distance.
   - Strictly decouples perceptual layout scoring from Channel C semantic validation.
   - Tested in [`tests/test_cdm_adapter.py`](../tests/test_cdm_adapter.py): **4 / 4 passed**.

4. **Independent Glyph-Source Boundary Audit:** [`scripts/experiments/glyph_source_boundary_audit.py`](../scripts/experiments/glyph_source_boundary_audit.py)
   - Extracts character vector bounding boxes and font cell envelopes directly from PDF streams via PyMuPDF.
   - Audits clearances and whitespace reductions against zero-margin crops across all benchmark targets.
   - Tested in [`tests/test_glyph_source_boundary_audit.py`](../tests/test_glyph_source_boundary_audit.py): **3 / 3 passed**.

### 18.4 Full Repository Regression Milestone
- **Total Test Suite:** **697 / 697 passed in 51.23s** (zero failures across all suites).
- **Frozen Engine Baseline Integrity:** Verified unchanged at `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1`.
- **Two-Level Case Registry Integrity:** Verified unchanged at `da4c166b7a5c7b1808d33b2d9f2ca0d71a0d60bf19d6844796506a51da36e6ba`.
- **Cross-Paper Evaluation Report Integrity:** Verified unchanged at `85320ae710afe3af4cb56c626691c6c76b9f93611258610d11eb76d505614454`.

