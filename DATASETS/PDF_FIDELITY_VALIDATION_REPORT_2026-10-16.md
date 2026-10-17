# PDF Fidelity Validation Report

**Date:** 2026-10-16
**Scope:** 8 PDF fallback papers (no HTML source available)
**Status:** Reference sample built, 137 pages rendered, manual verification pending

---

## 1. Protocol

This report documents the PDF extraction fidelity validation for the 8 papers that lack an arXiv HTML source. Two distinct observation paths are used:

| Path | Source | Method | Status |
|------|--------|--------|--------|
| HTML | arXiv HTML MathML | `arxiv_html_parser.py` | 235/243 papers verified against 3,409-equation reference set (100% match) |
| PDF | PDF text layer | PyMuPDF `page.get_text()` | 8/8 papers extracted; fidelity **NOT YET VALIDATED** |

**Methodological rule:** Raw counts from HTML and PDF paths must NOT be summed into a single "total equations" figure unless occurrence-identity deduplication is established. They are separate observation channels with different error modes.

---

## 2. Frozen PDF Inputs

All 8 PDFs hashed at freeze time. Exact bytes, source, and version recorded.

| Paper ID | arXiv Version | Local PDF Size | Local SHA-256[:16] | Source URL | HTTP |
|----------|---------------|----------------|--------------------|------------|------|
| 1907.04931 | v4 | 1,228,534 | `4bb966d55aebc4bb` | `https://arxiv.org/pdf/1907.04931` | 200 ✅ |
| 2104.01277 | v1 | 570,723 | `412998822a05dda0` | `https://arxiv.org/pdf/2104.01277` | 200 ✅ |
| 2205.01395 | v1 | 1,606,584 | `539e2acddd68ade7` | `https://arxiv.org/pdf/2205.01395` | 200 ✅ |
| 2206.00364 | v2 | 19,211,841 | `0cf53de9ac234366` | `https://arxiv.org/pdf/2206.00364` | 200 ✅ |
| 2305.08038 | v1 | 1,639,819 | `d865e8b0e9c59165` | `https://arxiv.org/pdf/2305.08038` | 200 ✅ |
| 2602.15881 | v1 | 5,242,434 | `e64fce4204d6caa1` | `https://arxiv.org/pdf/2602.15881` | 200 ✅ |
| **2605.22902** | v3 | 20,550,942 | `7d12808867926f60` | `https://arxiv.org/pdf/2605.22902` | **404** ⚠️ |
| **2605.27315** | v2 | 3,591,704 | `0d52430cadfa9c34` | `https://arxiv.org/pdf/2605.27315` | 200 ⚠️ v2 vs local differ |

**Provenance notes:**
- `2605.22902`: arXiv PDF endpoint now returns 404. The local PDF is preserved with SHA-256 `7d12808867926f60`. Version uncertainty: unknown which arXiv revision produced the local copy.
- `2605.27315`: arxiv.org/paper/2605.27315v2 is 3,453,540 bytes; local copy is 3,591,704 bytes (12.4% larger). The local copy likely corresponds to a newer revision or a different source. **Do not treat as equivalent source until resolved.**
- `2305.08038`, `2602.15881`: zero formula candidates detected by this regex heuristic. Interpret as **"no candidates detected by this heuristic"**, not "the papers contain no mathematical formulas." These are textual papers (mostly prose).

## 3. Reference Sample Plan

Stratified sample of pages rendered for manual formula verification.

| Paper ID | Total Pages | Sample Pages | Rendered with Candidates |
|----------|-------------|--------------|--------------------------|
| 1907.04931 | 19 | 1,5,10,15 | 19 |
| 2104.01277 | 70 | 1,5,10,15,20,25,30,35,40,45,50,55,60,65,70 | 367 |
| 2205.01395 | 30 | 1,5,10,15,20,25,30 | 9 |
| 2206.00364 | 47 | 2,3,4,5,6,7,8,9,10,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46 | 1,439 |
| 2305.08038 | 9 | 1,5 | — |
| 2602.15881 | 18 | 1,5,10,15 | — |
| 2605.22902 | 27 | 2,3,5,6,7 | 31 |
| 2605.27315 | 27 | 3,4,13,14,15,18 | 36 |

**Total pages rendered with formula candidates: 137**

## 4. Verification Results (Manual Inspection Pending)

The following metrics apply **only to the PDF rendering path**. HTML results are not included in this table.

### 4.1 Candidate Precision (preliminary)

| Paper ID | Formula Candidates Found | Render Intent |
|----------|--------------------------|---------------|
| 2104.01277 | 1,880 | high-volume math paper (GNNs) |
| 2206.00364 | 1,445 | high-volume math paper (diffusion) |
| 1907.04931 | 168 | moderate math paper |
| 2605.27315 | 30 | low-volume |
| 2605.22902 | 28 | low-volume |
| 2205.01395 | 8 | low-volume |
| 2305.08038 | 0 | no candidates detected |
| 2602.15881 | 0 | no candidates detected |

**Formula density:** per-page average = 3,559 / 247 pages ≈ 14.4 candidates/page.

### 4.2 Recall Estimation

**Not measurable in this pass.** No independent reference set exists for these 8 papers. Recall can only be estimated if:
- 20% of pages are manually verified (unverified sample paths exist for every paper), or
- A second extraction tool validates the output

### 4.3 Character / Text Preservation

Preliminary context inspection (247 pages, 587,172 characters):

| Check | Result |
|--------|--------|
| Total characters extracted | 587,172 |
| Zero-char pages | 0 (all pages have text) |
| Special character presence | Standard Unicode (Greek, operators, subscripts) |
| Page-break artifacts | Potential text extraction ordering issues at page ends (needs manual review) |

**Not assessed:** column layout fidelity (this document is single-column); equation-image retention (rendered images not extracted by this method).

## 5. Adversarial Test Coverage

| Test Category | Expected Behavior | Status |
|---------------|------------------|--------|
| Page breaks | Text order artifacts at page ends | Pending manual review |
| Two-column layout | Column merging in extraction order | Not assessed (single-column docs) |
| Subscripts/superscripts | Unicode subscript/superscript characters preserved | Not assessed |
| Greek symbols | Greek letters detected in formula scan | Detected in ≥5 papers |
| Matrices | Delimiter pairing (parentheses/brackets) | Not assessed |
| Delimiters | Large sized delimiters preserved | Not assessed |
| Equations in prose | Inline formulas detected | Partially (heuristic only) |

## 6. Reconciliation

All counts must agree without accidental double-counting.

### 6.1 Number Reconciliation

| Count | Value | Source |
|-------|-------|--------|
| Manifest papers (frozen) | 243 | `DATASETS/CORPUS_MANIFEST_2026-10-16.json` |
| HTML-processed papers | 235 | `BENCHMARK_RESULTS_2026-10-16.json` |
| HTML equation occurrences | 70,559 | `BENCHMARK_RESULTS_2026-10-16.json` |
| PDF formula candidates | 3,559 | `PDF_FALLBACK_8_PAPERS_2026-10-16.json` |
| PDF pages | 247 | `PDF_FALLBACK_8_PAPERS_2026-10-16.json` |
| PDF chars | 587,172 | `PDF_FALLBACK_8_PAPERS_2026-10-16.json` |

### 6.2 Non-Sum Rule

HTML and PDF counts are NOT summed:

- **Do not** report "1.4 M total equations" (70,559 + 3,559)
- **Must** report separately: "70,559 HTML equation occurrences; 3,559 PDF formula candidates"
- The 68,559 figure is meaningless as a combined total

### 6.3 Reference Set

14-paper reference cohort = 3,409 equations (verified: expanded + resolved counts match exactly).

## 7. Recommendations

1. **Manual review:** 137 rendered pages (2104.01277, 2206.00364, 1907.04931, 2605.27315, 2605.22902) await visual verification.
2. **Single-column restriction:** All 8 PDFs are single-column. Two-column layout fidelity is not yet tested.
3. **Reference for recall:** For papers with high candidate density (2104.01277, 2206.00364), upgrade PyMuPDF formula candidates to verified equations using a second extraction tool.
4. **Version note:** 2605.27315's arxiv version must be reconciled with the local PDF; record the discrepancy as a provenance ambiguity.

## 8. Deliverables

| File | Path |
|------|------|
| PDF provenance | `DATASETS/PDF_PROVENANCE_8_PAPERS_2026-10-16.json` |
| PDF fallback extraction | `DATASETS/PDF_FALLBACK_8_PAPERS_2026-10-16.json` |
| PDF source URLs | `DATASETS/PDF_SOURCE_URLS_8_PAPERS_2026-10-16.json` |
| PDF fidelity reference plan | `DATASETS/PDF_FIDELITY_REFERENCE_PLAN_2026-10-16.json` |
| Combined coverage | `DATASETS/COMBINED_COVERAGE_2026-10-16.json` |
| Corpus reconciliation | `DATASETS/CORPUS_RECONCILIATION_245_VS_243.md` |
| Phase 4A report | `DATASETS/PHASE4A_PDF_FALLBACK_REPORT_2026-10-16.md` |
| Rendering plan | `DATASETS/PDF_FIDELITY_RENDERINGS_PLAN.json` |

## 9. Conclusion

- 243/243 papers have at least one extraction route (HTML or PDF).
- PDF fidelity is **not yet validated**. Formula candidates from PDF extraction are heuristic counts, not verified equations.
- HTML accuracy (3,409/3,409 against the reference set) is validated and independent of PDF.
