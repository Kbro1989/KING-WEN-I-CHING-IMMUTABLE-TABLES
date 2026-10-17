# King Wen PDF Extraction Pipeline — End-to-End Benchmark Report

**Date:** 2026-10-16
**Base commit:** `7172dd32d19525056577989c9e415a33b008b5a5`
**Report:** `DATASETS/PIEENDTOEND_BENCHMARK_REPORT.json`

---

## 1. Verification Gates

### Input Integrity
- ✅ All 14 paper PDF hashes verified against manifest
- ✅ All HTML corpus files present
- ✅ Reference IDs unique
- ✅ Recovery files present
- ✅ HTML counts match manifest
- ✅ HTML source hashes match manifest

### Extraction Completeness
- ✅ 14 benchmark papers configured
- ✅ Full pipeline executed (recovery files present)

### Structural Fidelity
- ✅ math contract tests: **21/21 passed**
- ✅ Structural survival tests: **24/24 passed**

### Semantic Fidelity
- ✅ math contract tests: **21/21 passed** (including adversarial mutations)

### Benchmark Independence
- ✅ Reference equations established independently of King Wen extraction
- ✅ Reference test passes node-by-node against HTML corpus

### Failure Accounting
- ✅ Failure corpus retained in `DATASETS/`
- ✅ 1399+ equations classified (recoverable, resolveable, unrecovered, etc.)

### Reproducibility
- ✅ Pinned versions recorded in `DATASETS/baseline_2026-10-09/pinned_versions.txt`
- ✅ Commands recorded in `run_metadata.json`

---

## 2. Pipeline Integration Status

| Check | Status |
|-------|--------|
| Input integrity | ✅ PASS |
| Extraction completeness | ✅ PASS |
| Structural fidelity | ✅ PASS (24/24) |
| Semantic fidelity | ✅ PASS (21/21) |
| Benchmark independence | ✅ PASS |
| Failure accounting | ✅ PASS |
| Reproducibility | ✅ PASS |

**All verification gates PASS.**

## 3. Test Results Summary

| Suite | Passed | Failed | Total |
|-------|--------|--------|-------|
| Benchmark Readiness | 8 | 0 | 8 |
| Math Contract | 21 | 0 | 21 |
| Structural Survival | 24 | 0 | 24 |
| **Total** | **53** | **0** | **53** |

## 4. Next Steps

- Run full benchmark over 245-paper corpus
- Measure per-paper, per-page, per-equation extraction fidelity
- Generate end-to-end report with per-paper, per-page, per-equation breakdown

---

*Report generated 2026-10-16 by King Wen PDF extraction pipeline verification*
