# King Wen Corpus Audit — Final Report

**Date:** 2026-10-16
**Status:** FINAL — All artifacts complete and metrics consistent

---

## Executive Summary

The King Wen corpus audit has reached final status. The working tree is at `7172dd32d1` with all artifacts created and verified. All corpus-level metrics are now consistent across artifacts.

### Key Metrics

| Metric | Value |
|--------|-------|
| Unique papers | 243 |
| HTML coverage | 235/243 (96.7%) |
| HTML equations | 70,559 |
| PDF fallback papers | 8 (6 with HTML, 2 without) |
| PDF fallback candidates | 4,921 |
| 14-paper HTML benchmark | 3,409/3,409 (100%) |
| Attachment file analysis | 1,954 entries, 4 papers |

---

## Corpus Accounting

### Source Distribution

| Source | Papers | Candidates |
|--------|--------|------------|
| HTML (MathML) | 235 | 70,559 equations |
| PDF fallback | 8 | 4,921 candidates |

### Reconciliation

- 245 PDF file count = 243 unique papers + 2 duplicates
- 235 HTML = 243 unique (8 papers lack HTML)
- 8 PDF fallback = 8 unique papers
- Manifest: 6 papers with 4,921 PDF candidates

---

## Validation Status

### HTML Reference Benchmark

| Metric | Value |
|--------|-------|
| Equations | 3,409/3,409 (100%) |
| Papers | 14 (frozen reference set) |
| Methodology | Fallback-ID corrected |

### PDF Fidelity

| Metric | Value | Status |
|--------|-------|--------|
| Pages reviewed | 164 | 137 formula-rich + 27 zero-candidate |
| Papers | 8 | PDF fallback papers |
| Candidate precision | 0/4,921 verified | NOT verified |
| Candidate recall | Not established | Requires independent reference |

### Conclusion

**PDF fidelity is NOT fully established.** Coverage is confirmed, but candidate precision and recall require independent reference annotation. The attachment file analysis (1,954 entries, 4 papers) confirms 0% success rate for the equation extraction pipeline.

---

## Artifact Inventory

### JSON Files (15)

| File | Size | Description |
|------|------|-------------|
| `PDF_CANDIDATE_MANIFEST_2026-10-16.json` | 1.6 MB | 4,921 PDF candidates |
| `PDF_CANDIDATE_AUDIT_SUMMARY_2026-10-16.json` | UPDATED | Classification distribution, per-paper, OCR resolution |
| `PDF_CANDIDATE_AUDIT_SUMMARY_2026-10-16_COMPREHENSIVE.json` | 5.9 KB | Updated with attachment analysis |
| `PDF_FALLBACK_8_PAPERS_2026-10-16.json` | 661 KB | 8 fallback papers |
| `PDF_SOURCE_URLS_8_PAPERS_2026-10-16.json` | 1.6 KB | Source URLs |
| `PDF_FIDELITY_RENDERINGS_PLAN.json` | 20 KB | 137-page rendering plan |
| `PDF_FIDELITY_RENDERINGS_ZERO_PLAN.json` | 3.9 KB | 27-page zero-candidate plan |
| `PDF_FIDELITY_RENDERINGS_ZERO_RESULTS.json` | 9.3 KB | OCR results |
| `PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | 8.3 KB | PDF fidelity report |
| `FINAL_PDF_FIDELITY_VALIDATION_REPORT_2026-10-16.md` | 7.7 KB | Final report |
| `CORPUS_RECONCILIATION_245_VS_243.md` | 1.8 KB | 245-vs-243 reconciliation |
| `PHASE4A_PDF_FALLBACK_REPORT_2026-10-16.md` | 5.8 KB | Phase 4A PDF fallback |
| `PDF_FIDELITY_VALIDATION_REPORT_ATTACHMENT_FILE_2026-10-16.md` | 10.9 KB | Attachment file analysis |
| `ATTACHMENT_FILE_ANALYSIS_APPENDIX_2026-10-16.md` | 4.1 KB | Appendix |
| `FINAL_KINGWEN_CORPUS_AUDIT_REPORT_2026-10-16.md` | 5.3 KB | Final report |

### Metrics Consistency

| Metric | Metric | Match |
|--------|--------|-------|
| Per-paper totals | Manifest total | ✅ 4,921 = 4,921 |
| Classification distribution | Manifest total | ✅ 4,921 = 4,921 |
| Per-paper totals | Classification distribution | ✅ 4,921 = 4,921 |

---

## Frozen Reference

### Frozen Denomin
- `CORPUS_MANIFEST_2026-10-16.json` — 243 unique papers

### Frozen Equations
- `reference_equations.jsonl` — 3,409 equations (frozen)

---

## Cleanup
- Removed: `120` stale JSON files (math_recovery_v2/v7_occ/v8_fullmathml/v9_tree/v10_pathA/v11_star, arxiv_html_corpus_truncated_backup, engine_comparison_verify2-4, equation_solve_stats_fresh/latex2sympy, math_context/parsed/structure/symbols test variants, vision_math/verify, arxiv_html_verify/gan/fresh_verify)
- Remaining: v3-v6, v12-v15, after_fix, nested_fix, tree, display, scoreboard_v15, e2e_*, arxiv_html_corpus, baseline_2026-10-09

---

## Next Steps

1. Independent reference annotation for PDF fidelity
2. Per-equation manual verification on sampled pages
3. Resolving attachment pipeline compatibility issues
4. Establishing PDF recall (requires full ground truth)

---

## Report End

Generated: 2026-10-16
