# Phase 4A — PDF Fallback for 8 HTML-Unavailable Papers

**Date:** 2026-10-16
**Status:** COMPLETE — 8/8 PDFs extracted
**Scope:** The 8 papers with no arxiv HTML source

---

## 1. The 8 Papers

These papers returned HTTP 404 from `https://arxiv.org/html/{id}` across all three batch attempts. This is an **arxiv.org HTML coverage limitation**, not an extraction failure.

| # | Paper ID | Category | Title |
|---|----------|----------|-------|
| 1 | `1907.04931` | graph-neural-networks | GraphSAINT: Graph Sampling Based Inductive Learning Method |
| 2 | `2104.01277` | graph-neural-networks | Beyond Low-Pass Filters: Adaptive Feature Propagation on Graphs |
| 3 | `2205.01395` | graph-neural-networks | LinkX: A Unified Framework for Link Prediction with GNNs |
| 4 | `2206.00364` | diffusion-generative | Elucidating the Design Space of Diffusion-Based Generative Models |
| 5 | `2305.08038` | graph-neural-networks | Graph State Space Models |
| 6 | `2602.15881` | llm-alignment | Pluralism in AI Governance |
| 7 | `2605.22902` | multimodal-learning | Transcoders Trace Visual Grounding and Hallucinations in VLMs |
| 8 | `2605.27315` | multimodal-learning | Real Images, Worse Judgments |

## 2. PDF Source Verification

All 8 papers have local PDFs. 7/8 arxiv PDF endpoints return HTTP 200.

| Paper ID | Local PDF (bytes) | arxiv PDF (bytes) | HTTP | Match |
|----------|-------------------|-------------------|------|-------|
| 1907.04931 | 1,228,534 | 1,228,534 | 200 | ✅ byte-identical |
| 2104.01277 | 570,723 | 570,723 | 200 | ✅ byte-identical |
| 2205.01395 | 1,606,584 | 1,606,584 | 200 | ✅ byte-identical |
| 2206.00364 | 19,211,841 | 19,211,841 | 200 | ✅ byte-identical |
| 2305.08038 | 1,639,819 | 1,639,819 | 200 | ✅ byte-identical |
| 2602.15881 | 5,242,434 | 5,242,434 | 200 | ✅ byte-identical |
| **2605.22902** | 20,550,942 | — | **404** | ⚠️ source unavailable; local preserved |
| **2605.27315** | 3,591,704 | 3,453,540 | 200 | ⚠️ arxiv version differs from local |

**Two provenance caveats:**
- `2605.22902`: arxiv PDF endpoint now 404s. The local PDF is preserved but cannot be re-fetched from source.
- `2605.27315`: the arxiv-hosted PDF differs in size from the local copy (3,453,540 vs 3,591,704 bytes) — likely a revision. Local copy is the extraction basis.

## 3. PDF Extraction Results

Route: PyMuPDF 1.28.2 (Python 3.11) — the existing 3A baseline method. **Separate route from HTML/MathML.**

| Paper ID | Pages | Chars | Formula candidates | SHA-256[:16] |
|----------|-------|-------|--------------------|--------------|
| 1907.04931 | 19 | 59,830 | 168 | `4bb966d55aebc4bb` |
| 2104.01277 | 70 | 105,501 | 1,880 | `412998822a05dda0` |
| 2205.01395 | 30 | 95,066 | 8 | `539e2acddd68ade7` |
| 2206.00364 | 47 | 127,007 | 1,445 | `0cf53de9ac234366` |
| 2305.08038 | 9 | 27,448 | 0 | `d865e8b0e9c59165` |
| 2602.15881 | 18 | 41,856 | 0 | `e64fce4204d6caa1` |
| 2605.22902 | 27 | 38,919 | 28 | `7d12808867926f60` |
| 2605.27315 | 27 | 91,545 | 30 | `0d52430cadfa9c34` |
| **Total** | **247** | **587,172** | **3,559** | — |

**Success rate: 8/8**

## 4. Comparison Constraint

PDF-derived results are **NOT merged** into the HTML corpus and **NOT** claimed to have equivalent fidelity.

| Property | HTML/MathML route | PDF route |
|----------|-------------------|-----------|
| Source | arxiv HTML `<math>` + MathML | PDF text layer (PyMuPDF) |
| Structure | Full MathML tree (mrow/mfrac/msub) | Flat text extraction |
| Equation identity | `S<sec>.E<eqn>.m<frag>` | Not available |
| Reference-comparable | Yes (3,409-equation reference set) | No independent reference for these 8 |
| Formula detection | Structural | Regex heuristic (symbol presence) |

The "formula candidates" counts are **heuristic line counts**, not verified equations. No independent reference set exists for these 8 papers, so **no accuracy claim is made** for the PDF route.

## 5. Combined Coverage

| Route | Papers | Equations / Chars |
|-------|--------|-------------------|
| HTML/MathML | 235 | 70,559 equations |
| PDF fallback | 8 | 587,172 chars, 3,559 formula candidates |
| **Combined** | **243 / 243** | — |

**Every paper in the manifest now has at least one documented extraction route.**

## 6. Metrics Separation (per directive)

| Metric | Value | Meaning |
|--------|-------|---------|
| Source coverage (HTML) | 235/243 (96.7%) | Papers with arxiv HTML available |
| Source coverage (combined) | 243/243 (100%) | Papers with ≥1 extraction route |
| Extraction volume (HTML) | 70,559 | Equation occurrences extracted |
| Extraction volume (PDF) | 3,559 | Formula-candidate lines (heuristic) |
| Extraction fidelity (HTML) | 3,409/3,409 reference set | Independently verified (14-paper cohort) |
| Extraction fidelity (PDF) | **Not established** | No independent reference for these 8 |
| Unavailable HTML sources | 8 | Explicitly tracked, PDF-fallback covered |

## 7. Artifacts

| File | Contents |
|------|----------|
| `DATASETS/PDF_FALLBACK_8_PAPERS_2026-10-16.json` | Full page-level text for all 8 |
| `DATASETS/PDF_SOURCE_URLS_8_PAPERS_2026-10-16.json` | Source URL verification |
| `DATASETS/COMBINED_COVERAGE_2026-10-16.json` | Per-paper provenance table (243 rows) |
| `DATASETS/CORPUS_RECONCILIATION_245_VS_243.md` | 245-vs-243 resolution |
| `cache/scripts/pdf_fallback_8.py` | Extraction script |

## 8. Defensible Conclusion

- The HTML pipeline has processed **every paper with an available HTML source** (235/243).
- The 8 remaining papers are **arxiv HTML coverage limits**, not extraction failures.
- All 8 have been extracted via the **separate PDF route** with page-level text preserved.
- The **243-paper denominator** is frozen and reconciled (245 was a file count).
- **HTML and PDF results are reported separately**; PDF fidelity is not claimed.
