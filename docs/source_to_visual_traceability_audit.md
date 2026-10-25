# Source-to-Visual Traceability Audit

## Purpose

This document traces the complete data path from a real paper's HTML/MathML source through its PDF crop and into the evaluation record. It identifies which layers are connected and where the provenance chain breaks.

## Test Paper

- **arXiv ID**: 1505.05770
- **Title**: Variational Inference with Normalizing Flows
- **HTML corpus**: `DATASETS/arxiv_html_corpus/1505.05770.json` (308 equations)
- **PDF**: `zotero/learning-corpus/diffusion-generative/1505.05770_Variational Inference with Normalizing Flows.pdf`
- **Candidate file**: None (no `candidates_1505.05770.json` exists)

## Layer 1: Source Acquisition (HTML/MathML)

**Status: IMPLEMENTED**

The arxiv HTML parser (`scripts/arxiv_html_parser.py`) fetches `https://arxiv.org/html/1505.05770` and extracts equations with:
- `index`: Sequential equation index (0-based)
- `latex`: LaTeX source from `<annotation encoding="application/x-tex">`
- `mathml`: Full MathML from `<math>` tag (NOT truncated)
- `context_before` / `context_after`: Surrounding text
- `is_display`: Whether equation is display or inline
- `source`: Origin (`mathml`, `ltx_math_span`, `ltx_equation_div`, `annotation`)

**Evidence**: 308 equations extracted, each with complete MathML and LaTeX. Full MathML preserved (no truncation).

**Provenance gap**: The HTML corpus stores `version: null` for this paper. The arXiv version is not recorded. The URL is `https://arxiv.org/html/1505.05770` without version suffix.

## Layer 2: PDF Geometry and Crop Generation

**Status: IMPLEMENTED but DISCONNECTED**

The vision comparison pipeline (`scripts/vision_comparison_pipeline.py`) crops PDF regions using bounding boxes from `candidates_*.json` files. For paper 1505.05770:

- **No candidate file exists**: `DATASETS/candidates_1505.05770.json` does not exist
- **No PDF in benchmark_pdfs**: PDF is in Zotero corpus, not in `DATASETS/benchmark_pdfs/`
- **No bbox-to-equation mapping**: Even if PDF existed, there is no mapping from HTML equation index to PDF bounding box

**The candidate files** (9 papers total: 1907.04931, 2104.01277, 2205.01395, 2206.00364, 2305.08038, 2602.15881, 2605.22902, 2605.27315) contain manually curated bounding boxes with:
- `paper_id`, `page`, `bbox` (x0, y0, x1, y1)
- `line_text` (declared source text)
- `reference_latex` (manually provided LaTeX)
- `classification` (true_equation, etc.)

**Provenance gap**: Candidate `reference_latex` is manually provided, not extracted from HTML. There is no `html_equation_index` field linking the candidate to a specific HTML equation.

## Layer 3: Mathematical Verification and Evaluation

**Status: CALIBRATED (Phase 2C)**

The frozen gate library (`scripts/phase2c_gate_library.py` at commit `fe2843963e`) tests:
- Gate 1: Geometry and clearance
- Gate 2: Ordered token alignment
- Gate 3: Operator and delimiter integrity
- Gate 4: Literal-match vs semantic-equivalence reporting
- Gate 5: Authoritative provenance

**Provenance gap**: Gate inputs are synthetic or candidate-derived strings, not source-grounded equations from real papers. The 47-case aggregate tests gate logic, not end-to-end source-to-visual traceability.

## Gap Summary

| Gap | Description | Impact |
|-----|-------------|--------|
| G1 | No paper has both HTML corpus entry AND candidate file | Cannot trace HTML equation → PDF crop for any paper |
| G2 | No `html_equation_index` in candidate records | Cannot link PDF crop to specific HTML equation |
| G3 | Candidate `reference_latex` is manually provided | Not source-derived; may not match HTML LaTeX |
| G4 | No PDF in benchmark_pdfs for candidate papers | Vision pipeline cannot crop without manual PDF placement |
| G5 | No candidate file for HTML corpus papers | Cannot evaluate HTML equations with PDF visual evidence |
| G6 | HTML corpus `version` is null | Cannot pin arXiv version for reproducibility |
| G7 | Candidate `page` is 1-based, PDF crop uses 0-based | Off-by-one risk in page indexing |

## What Exists vs. What's Missing

### Exists
- 241 papers with full HTML/MathML source (arxiv_html_corpus)
- 233 papers with both HTML and PDF (Zotero corpus)
- 9 papers with PDF candidate bounding boxes
- 5-gate evaluation framework (Phase 2C calibrated)
- 47-case gate evaluation aggregate (20 TP + 27 TN)
- 434 software tests

### Missing
- Any paper with BOTH HTML source AND candidate PDF crops
- Any mapping from HTML equation index to PDF bounding box
- Any automated HTML→PDF equation association
- Any source-grounded evaluation case (all are synthetic or candidate-derived)
- Any paper-level holdout set

## Recommended Next Steps

1. **Select one paper** with both HTML and PDF (e.g., 1505.05770 with 308 equations)
2. **Manually identify 3-5 equations** in the PDF that correspond to HTML equations
3. **Record the mapping**: HTML equation index → PDF page → bounding box → crop hash
4. **Run the full pipeline**: HTML LaTeX → PDF crop → Pix2Text OCR → Gate evaluation
5. **Document the provenance chain** for each equation
6. **Scale to 10-20 equations** across 2-3 papers
7. **Freeze a paper-level holdout** before any evaluator tuning

## Conclusion

The three layers (source parsing, PDF vision, evaluation) are each partially implemented but not connected. No equation has been traced end-to-end from HTML/MathML source through PDF crop to evaluation record. The next milestone must prove this data path before expanding the evaluator.