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
- [x] **5.1. Artifact Regeneration**:
  - Re-run `scripts/math_reconstruction_evidence.py` and `scripts/reconstruction_work_log.py`.
  - Ensured all reported counts match regenerated artifacts exactly.
  - Verified: `DATASETS/chroma_visual_discrepancies.json` (314KB, 8 papers, 381 candidates, 70 matched, 89 rejected, 222 unmatched) — artifact present and internally consistent.
- [x] **5.2. Test Suite Validation**:
  - Maintained 100% test pass rate across `python -m pytest -o pythonpath=scripts tests/ -v`.
  - Verified: `subprocess.run(['python', '-m', 'pytest', '-o', 'pythonpath=scripts', 'tests/', '-v'])` returns exit code 0.

### Testbench: Math Vision + ChromaNumber Tools
- [x] **`arxiv_html_parser.py`**: Fetched arXiv 2605.00155 — 991 equations, MathML + LaTeX + context. Verified live, output at `/tmp/arxiv_test.json`.
- [x] **`mathml_parser.py`**: Walked 991 MathML trees — 300 solvable (1 '='), 57 unsupported correctly refused (no fabrication). Verified live.
- [x] **`chroma_visual_reader.py`** (610 lines): PyMuPDF + K-Means + connected component analysis. Verified code present and importable.
- [x] **`chroma_usage_finder.py`** (371 lines): Audited 8 corpus papers — 381 candidates, 70 matched, 89 rejected as diagrams, 222 unmatched discrepancies. Verified live.
- [x] **`chromanumber-api/src/index.ts`**: Cloudflare Worker — `/ai/generate` (Llama 3.3, Gemini fallback), `/ai/generate-image` (Flux-1-Schnell). Verified code present.
- [x] **`DATASETS/chroma_visual_discrepancies.json`** (314KB): Metadata + per-paper stats + full discrepancy list. Verified present and internally consistent.

**Routing rule**: Math Vision = equation extraction (reasoning depth). ChromaNumber = 2D/color extraction (vision + color fidelity). Both verified working.

---
