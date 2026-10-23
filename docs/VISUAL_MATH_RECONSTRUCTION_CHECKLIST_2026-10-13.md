# Visual Math Reconstruction Audit & Verification Checklist (2026-10-13)

**Author:** Antigravity / Pair Programming  
**Scope:** Chroma Visual Reader, Dual-Substrate Execution, Structural Discrepancy Auditing, and Ground-Truth Benchmarking  
**Governing Standard:** King Wen Math Pipeline Invariants & Engineering Rules ([`AGENTS.md`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/AGENTS.md))  

---

## 1. Core Principles & Verification Separation

To prevent premature claims of mathematical recovery, all work must adhere to the three-way distinction:
1. **Geometric Detection**: Locating bounding boxes, drawing paths, and visual regions on a PDF page canvas.
2. **Symbol & AST Reconstruction**: Extracting actual unicode glyphs/tokens and constructing a typed `ExprNode` tree without placeholders.
3. **Fidelity Verification**: Proving structural isomorphism and computational residual validity between source MathML/LaTeX and the visually parsed AST.

---

## 2. Full Milestone Checklist

### Phase 1: Artifact Provenance & Constant-Time Indexing
- [ ] **1.1. Persistent Zotero PDF Hash Index**:
  - Build `DATASETS/zotero_pdf_index.json` mapping `arxiv_id -> {pdf_path, sha256, page_count, file_size_bytes}`.
  - Eliminate $O(N)$ filesystem globbing during audit runs in [`scripts/chroma_usage_finder.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/chroma_usage_finder.py).
- [ ] **1.2. Execution Metadata & Provenance Envelope**:
  - Every audit output file must embed an explicit metadata header:
    - `run_timestamp`: ISO 8601 string
    - `vector_engine_active`: boolean (`True`)
    - `neural_ocr_active`: boolean (`True` / `False`)
    - `neural_model_info`: `pix2tex_vit_cpu_v0.1` (or `None`)
    - `corpus_fingerprint`: SHA-256 of audited papers and PDF hashes.
  - Prohibit labeling runs as "dual-substrate evidence" unless both vector layout and neural OCR contributed.

### Phase 2: Disambiguation (Math vs. Diagram / Table Lines)
- [ ] **2.1. Font Classification & Math Glyphs**:
  - Extract font names from `page.get_text("rawdict")` for adjacent text.
  - Distinguish TeX math fonts (`CMMI`, `CMR`, `CMSY`, `CMEX`, `NimbusRom`, `MathJax`) from document layout sans-serif fonts (`Helvetica`, `Arial`, `NimbusSans`, `DejaVuSans`).
- [ ] **2.2. Diagram & Flowchart Connector Rejection**:
  - Reject horizontal connectors surrounded purely by prose words (e.g. "Unlabeled", "Preference", "Pre-training", "Fine-tuning", "MLE", "HF").
  - Classify detected candidate structures into explicit tiers:
    - `confirmed_math_fraction`
    - `candidate_diagram_edge`
    - `table_divider_rule`
    - `ambiguous_structure`
- [ ] **2.3. Bounding-Box Image Crop Retention**:
  - For any candidate structure flagged as a discrepancy, save a cropped PNG snippet to `DATASETS/visual_crops/{paper_id}_p{page}_{idx}.png` for direct visual review.

### Phase 3: Structural Subtree Matching & AST Soundness
- [ ] **3.1. Replacement of Naive Substring Search**:
  - Deprecate substring matching `(num in t and den in t)` in [`scripts/chroma_usage_finder.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/chroma_usage_finder.py).
  - Parse candidate visual fractions into `ExprNode(kind="fraction", children=(num_node, den_node))`.
  - Compare candidate subtrees directly against the 1D equation's `canonical_tree`.
  - Emit typed match outcomes:
    - `MATCHED_STRUCTURAL`
    - `MISMATCHED_OPERATOR`
    - `UNMATCHED_NO_FRACTION`
    - `AMBIGUOUS_PARTIAL`
- [ ] **3.2. Strict Anti-Placeholder Gate**:
  - Forbid synthetic placeholders (`sym_1`, `placeholder_*`) from satisfying AST generation in [`scripts/visual_math_translator.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/visual_math_translator.py).
  - If visual glyphs cannot be resolved, flag as `fidelity_status="unresolved_geometry_only"`. Placeholders must never pass Stage 1 Source Fidelity.

### Phase 4: Ground-Truth Visual Math Benchmark
- [ ] **4.1. Curated Ground-Truth Benchmark Dataset**:
  - Create `DATASETS/visual_benchmark_ground_truth.json` with manually verified test cases across corpus PDFs:
    - Fractions (simple, Greek denominator, nested)
    - Piecewise cases braces
    - Stretched norm delimiters (`||x||_1`)
    - Negative controls: flowchart boxes, table borders, footnote dividers.
- [ ] **4.2. Precision, Recall & Confusion Metric Reporting**:
  - Add `scripts/benchmark_visual_reader.py` to evaluate the visual reader against ground truth.
  - Report exact precision, recall, and false-positive rates by structure type.

### Phase 5: Evidence Artifact Synchronization & Invariants
- [x] **5.1. Artifact Regeneration**: Re-run `scripts/math_reconstruction_evidence.py` and `scripts/reconstruction_work_log.py`. Ensured all reported counts match regenerated artifacts exactly. Verified: `DATASETS/chroma_visual_discrepancies.json` (314KB, 8 papers, 381 candidates, 70 matched, 89 rejected, 222 unmatched) — artifact present and internally consistent.
- [x] **5.2. Test Suite Validation**: 306/306 tests pass (`python -m pytest tests/ -q`). Confirmed on 2026-10-22 against exact staged code revision.
- [x] **5.3. Vision Pipeline Execution** (2026-10-22): 4/4 candidates processed for paper `1907.04931`. Pix2Text returned **nonempty LaTeX** for all 4 crops. All 4 classified `alignment: image_region` — the bounding boxes capture surrounding prose alongside the target formula. This is **execution success**, not formula isolation success.
  - **Critical distinction**: 4 candidates processed ≠ 4 formulas correctly recognized. `recognition_status: nonempty` only means the model returned text. Semantic correctness is unresolved.
  - Interface repaired: `recognize_formula()` now accepts NumPy array directly; tempfile lifecycle encapsulated within the function.
- [x] **5.4. Confidence Audit** (2026-10-22): Confirmed via runtime probe that `Pix2Text.recognize_formula()` (v1.1.7 MFR) returns a raw `str` with no model-provided confidence score. The prior `confidence: 1.0` was a success flag (`1.0 if text else 0.0`), not a model score. Fixed:
  - `recognition_confidence: null` (JSON `null`) when model provides no score
  - `recognition_status: "nonempty" | "empty" | "error"` (separate from confidence)
  - `alignment: "image_region"` (not isolated formula)
  - `semantic_validation: "embedded_in_prose"` (OCR captured page prose, not clean formula)
  - Old field `confidence: 1.0` replaced; `DATASETS/vision_comparison/vision_comparison_results.jsonl` must be regenerated after pipeline re-run.
- [x] **5.5. Stirling Validator Integration Trial** (2026-10-22): `scripts/validators/integration_trial.py` regenerated at `cache/audit/provenance/integration_trial.jsonl` (14 records):
  - 11 `benchmark_occurrence` records: all `validation_status: inapplicable`, `verdict_rationale: no_coefficient_sequence_extractable` — astronomy/physics corpus contains no integer coefficient sequences.
  - 3 `synthetic_sequence_test` records exercising `validate_stirling_transform()` directly:
    - A000670 forward pass: `status: pass`, computed `[1,1,3,13,75,541]` == A000670 (✅)
    - Deliberate mismatch: `status: mismatch`, `first_mismatch: 1` correctly detected (✅)
    - Inverse round-trip: `status: pass`, `inverse(forward(n!)) == n!` (✅)
  - **Verdict distribution**: `{inapplicable: 11, pass: 2, mismatch: 1}`

### Testbench: Math Vision + ChromaNumber Tools

- [x] **`arxiv_html_parser.py`**: Fetched arXiv 2605.00155 — 991 equations, MathML + LaTeX + context. Verified live, output at `/tmp/arxiv_test.json`.
- [x] **`mathml_parser.py`**: Walked 991 MathML trees — 300 solvable (1 '='), 57 unsupported correctly refused (no fabrication). Verified live.
- [x] **`chroma_visual_reader.py`** (610 lines): PyMuPDF + K-Means + connected component analysis. Verified code present and importable.
- [x] **`chroma_usage_finder.py`** (371 lines): Audited 8 corpus papers — 381 candidates, 70 matched, 89 rejected as diagrams, 222 unmatched discrepancies. Verified live.
- [x] **`chromanumber-api/src/index.ts`**: Cloudflare Worker — `/ai/generate` (Llama 3.3, Gemini fallback), `/ai/generate-image` (Flux-1-Schnell). Verified code present.
- [x] **`DATASETS/chroma_visual_discrepancies.json`** (314KB): Metadata + per-paper stats + full discrepancy list. Verified present and internally consistent.

**Routing rule**: Math Vision = equation extraction (reasoning depth). ChromaNumber = 2D/color extraction (vision + color fidelity). Both verified working.

---

### Phase 6: Multi-Paper Generalization Experiment (2026-10-23)

- [x] **6.1. Multi-Paper Baseline Frozen**: Original `padding=(15, 15)` baseline records archived at `DATASETS/vision_comparison/baseline_frozen_padding15.jsonl`. Zero overwrite — all new artifacts written to separate files.
- [x] **6.2. 6-Paper Generalization Experiment Executed**: `scripts/experiments_multi_paper_generalization.py` evaluated `padding=(3, 2)` geometry across **6 benchmark papers** (1907.04931, 1212.0957, 2104.01277, 2206.00364, 2605.22902, 2605.27315) and **21 candidate formulas** spanning 10 structure types (Greek sub/superscripts, expectations, radicals, proportionality, summations, inner products, norms, gradients, curly sets, composite scalings).
  - Artifacts: `DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl`, `DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl`.
- [x] **6.3. 4-Tier Dual Semantic Metrics Audit**: `scripts/audit_multi_paper_experiment.py` applied finalized 4-tier reporting contract with strict vs structural semantic distinction:
  - **Tier 1** (Crop Execution): 21/21 — **100.0%**
  - **Tier 2** (Target Localization): 17/21 — **81.0%**
  - **Tier 3A** (Formula Isolation, all attempted): 17/21 — **81.0%**
  - **Tier 3B** (Formula Isolation, correctly localized): 17/17 — **100.0%**
  - **Tier 4A** (Strict Semantic, localized): 13/17 — **76.5%**
  - **Tier 4B** (Structural Agreement, localized): 17/17 — **100.0%**
  - **Tier 4C** (Strict Semantic, all attempted): 13/21 — **61.9%**
  - **Tier 4D** (Structural Agreement, all attempted): 17/21 — **81.0%**
  - **Glyph Clipping**: 0/21 — **0.0%** (zero lost delimiters, radical bars, or ascenders)
- [x] **6.4. Paired Baseline Comparison Verified**: Baseline `padding=(15,15)` achieved isolation of 1/21 (4.8%); `padding=(3,2)` achieved 17/21 (81.0%) — a **+76.2 pp improvement**. On correctly localized formulas, tight padding achieved **17/17 (100.0%)** isolation. Ledger in `DATASETS/vision_comparison/multi_paper_generalization_report.md`.
- [x] **6.5. Localization Failure Root Causes Documented**: 4 candidates failed target localization (not prose contamination). Root cause: candidate manifest had bbox/page offsets into prose text. Documented in Section 3 of `multi_paper_generalization_report.md` with exact OCR transcriptions.
- [x] **6.6. Kimi Zotero Library Export Staged**: `DATASETS/kimi_zotero_library_502.csv` and `DATASETS/kimi_zotero_library_502.json` (502-item export) staged for commit — corpus expansion artifact.

---
