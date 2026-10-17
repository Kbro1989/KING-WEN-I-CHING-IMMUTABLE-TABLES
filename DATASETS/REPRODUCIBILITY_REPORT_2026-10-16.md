# Phase 3 — Clean-Environment Reproducibility Report

**Date:** 2026-10-16
**Base commit:** `7172dd32d19525056577989c9e415a33b008b5a5`
**Isolated environment:** `repro_env/` (Python 3.14.7)
**Status:** ✅ REPRODUCIBLE — All tests pass in clean environment

---

## 1. Executive Summary

| Check | Result |
|-------|--------|
| Input integrity | ✅ All frozen hashes match |
| Test suite | ✅ All expected tests pass |
| Occurrence accounting | ✅ All 3409 reference occurrences have explicit dispositions |
| Match result | ✅ Reproduced under documented matching rules |
| Discrepancy accounting | ✅ Zero unexplained missing, extra, duplicate, or ambiguous occurrences |
| Repeatability | ✅ Second run produces equivalent results |

**Conclusion:** The benchmark is **reproducible** in a clean environment.

---

## 2. Frozen Inputs

| Input | Hash |
|-------|------|
| Reference equations JSONL | `27426887410f8031` |
| HTML corpus directory | `a9066e749ea479ed` |
| Benchmark manifest | `6091490b78184d38` |
| Pinned versions | `493e25a885482091` |
| Reference builder | `3f6d8690cd08b459` |
| HTML parser | `4962032dfd405c49` |
| Git commit | `9e3252bacaaf40a3df3d9eb34c13de0ceaad6653` |

**Frozen inputs manifest:** `DATASETS/FROZEN_INPUTS_2026-10-16.json`

---

## 3. Isolated Environment

| Component | Version |
|-----------|---------|
| Python | 3.14.7 |
| BeautifulSoup4 | 4.15.0 |
| lxml | 6.1.3 |
| sympy | 1.14.0 |

**Environment:** `repro_env/` (separate venv, no global packages)

---

## 4. Benchmark Reproduction

### 4.1 Match Result

| Metric | Original Run | Reproduction Run |
|--------|--------------|------------------|
| Total reference equations | 3409 | 3409 |
| Matched by ID | 3409 | 3409 |
| Unmatched | 0 | 0 |
| **Match rate** | **100.00%** | **100.00%** |

### 4.2 Fallback-ID Validation

| Test | Result |
|------|--------|
| eq0000 and eq0001 resolve to intended source occurrences | ✅ PASS |
| No duplicate fallback IDs in reference set | ✅ PASS |
| No duplicate fallback IDs in extraction | ✅ PASS |
| Reordering input does not change result | ✅ PASS (100% stable) |
| Exact content and structural comparisons agree | ✅ PASS (0 LaTeX mismatches) |
| Unmatched and ambiguous cases remain visible | ✅ PASS (0 unmatched) |

---

## 5. Test Suite Results

| Suite | Passed | Failed | Total |
|-------|--------|--------|-------|
| Benchmark Readiness | 8 | 0 | 8 |
| Math Contract | 21 | 0 | 21 |
| Structural Survival | 24 | 0 | 24 |
| **Total** | **53** | **0** | **53** |

---

## 6. Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| All frozen hashes match | ✅ PASS |
| All expected tests pass | ✅ PASS (53/53) |
| All 3409 reference occurrences have explicit dispositions | ✅ PASS |
| Match result reproduced under documented matching rules | ✅ PASS (100%) |
| Zero unexplained missing, extra, duplicate, or ambiguous occurrences | ✅ PASS |
| Second run produces equivalent results | ✅ PASS |

---

## 7. Important Distinction

**A repeated 100% result supports reproducibility of the benchmark. It does not, by itself, prove universal extraction accuracy across all 245 papers or notation types.**

- ✅ The benchmark is reproducible
- ✅ The reference set is independent
- ✅ The matching logic is stable
- ❌ Full 245-paper corpus accuracy is NOT established
- ❌ Universal extraction accuracy across all notation types is NOT established

---

## 8. Artifacts

| File | Path |
|------|------|
| This report | `DATASETS/REPRODUCIBILITY_REPORT_2026-10-16.md` |
| Frozen inputs | `DATASETS/FROZEN_INPUTS_2026-10-16.json` |
| Reproduction log | `DATASETS/repro_run_2026-10-16.log` |
| Validation log | `DATASETS/repro_validation_2026-10-16.log` |
| Isolated environment | `repro_env/` |

---

## 9. Conclusion

**The benchmark is reproducible in a clean environment.**

- ✅ All frozen input hashes match
- ✅ All 53 tests pass
- ✅ 3409/3409 equations match (100%)
- ✅ Fallback-ID correction validated
- ✅ Results stable under input reordering
- ✅ Zero unexplained discrepancies

**Next steps:**
1. Run full 245-paper corpus benchmark
2. Investigate historical `.venv/` (optional)
3. Address 54MB JSONL and 62MB NPZ files (optional)

---

*Report generated 2026-10-16 by King Wen PDF extraction pipeline verification*
*Status: REPRODUCIBLE — All acceptance criteria met*
