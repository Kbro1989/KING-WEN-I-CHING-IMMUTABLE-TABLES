# Combinatorics Benchmark Report — End-to-End Stirling Validation

**Date:** 2026-10-23
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Branch:** main
**Scope:** Real-document combinatorics benchmark with independent reference oracles

---

## 1. Pinned Source Documents (SHA-256 Provenance)

To ensure full reproducibility and prevent silent drift, all benchmark source documents are pinned with cryptographic hashes:

| Document Role | Citation / Title | arXiv ID | Local PDF Path | SHA-256 Checksum |
|:---|:---|:---:|:---|:---|
| **Primary Benchmark Paper** | Mourad Rahmani (2012), *The Generalized Stirling Transform* | `1212.0957v1` | `DATASETS/benchmark_pdfs/1212.0957.pdf` | `1c734a4e0a29c8eae4b94d8033351b62bf8411a78e5d9798b904dcd4e86c14d1` |
| **Independent Reference Oracle** | Milan Janjić (2008), *On a non-combinatorial definition of Stirling numbers* | `0806.2366v1` | `DATASETS/benchmark_pdfs/0806.2366.pdf` | `ed9e309127125306f12da104d810cfb1a7f6cefb8123382f9167d730b2496dde` |

---

## 2. Independent Reference Fixtures (External Oracles)

To prevent shared-error survivorship (where an implementation and an expected value share the same formula transcription error), claimed outputs are cross-verified against independently curated sequences:

- **OEIS A000110** (Bell numbers): $1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147$
- **OEIS A000670** (Ordered Bell / Fubini numbers): $1, 1, 3, 13, 75, 541, 4683, 47293, 545835$
- **OEIS A000045** (Fibonacci numbers): $0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55$

---

## 3. Two-Stage Separation: Extraction Correctness vs Mathematical Validation

Following the structural invariants in `AGENTS.md`:
- **Stage 1 (Extraction Correctness):** Verifies that the mathematical expression, conventions, index bounds, and coefficient definitions match the source paper PDF exactly.
- **Stage 2 (Mathematical Residual Validation):** Verifies that the forward/inverse transform implementation computes the claimed sequence with zero residual ($|b_{\text{comp}} - b_{\text{claim}}| = 0$).

---

## 4. Benchmark Trial Cases & Execution Results

| Case ID | Source Locator | Equation / Context | Direction | Input Sequence | Claimed / Expected Sequence | Computed Sequence | First Mismatch | Extraction Verdict | Math Validation Verdict |
|:---|:---|:---|:---:|:---|:---|:---|:---:|:---:|:---:|
| `rahmani_2012_eq1.1_bell_forward` | Page 1, Eq (1.1); Page 6, Ex 1 | $b_n = \sum_{k=0}^n S(n,k) \cdot 1 = B_n$ | Forward (EGF) | $[1, 1, 1, 1, 1, 1, 1]$ | $[1, 1, 2, 5, 15, 52, 203]$ (A000110) | $[1, 1, 2, 5, 15, 52, 203]$ | None | `verified_exact` | **PASS** |
| `rahmani_2012_eq1.2_bell_inverse` | Page 1, Eq (1.2); Page 6, Ex 1 | $a_n = \sum_{k=0}^n s(n,k) B_k = 1$ | Inverse (EGF) | $[1, 1, 2, 5, 15, 52, 203]$ (Bell) | $[1, 1, 1, 1, 1, 1, 1]$ (All-ones) | $[1, 1, 1, 1, 1, 1, 1]$ | None | `verified_exact` | **PASS** |
| `rahmani_2012_p1_ordered_bell_forward` | Page 1, paragraph 3 | $b_n = \sum_{k=0}^n S(n,k) k! = F_n$ | Forward (EGF) | $[1, 1, 2, 6, 24, 120, 720]$ ($n!$) | $[1, 1, 3, 13, 75, 541, 4683]$ (A000670) | $[1, 1, 3, 13, 75, 541, 4683]$ | None | `verified_exact` | **PASS** |
| `rahmani_2012_example2_fibonacci_inverse` | Page 6, Ex 2; Matrix $S$ Row 0 | $a_{0,m} = \sum_{k=0}^m s(m,k) F_k$ | Inverse (EGF) | $[0, 1, 1, 2, 3, 5, 8, 13]$ (Fibonacci) | $[0, 1, 0, 1, -4, 19, -108, 719]$ | $[0, 1, 0, 1, -4, 19, -108, 719]$ | None | `verified_exact` | **PASS** |
| `negative_control_bell_deliberate_corruption` | Synthetic Control | Deliberate mutation: $B_4 = 999$ | Forward (EGF) | $[1, 1, 1, 1, 1, 1, 1]$ | $[1, 1, 2, 5, 999, 52, 203]$ | $[1, 1, 2, 5, 15, 52, 203]$ | Index 4 | `verified_exact` | **MISMATCH** (expected) |

---

## 5. Artifact Summary

- **Runner Script:** [`scripts/validators/combinatorics_benchmark.py`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validators/combinatorics_benchmark.py)
- **JSONL Trial Output:** [`DATASETS/combinatorics_benchmark/combinatorics_validation_trial.jsonl`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/combinatorics_benchmark/combinatorics_validation_trial.jsonl)
- **Manifest:** [`DATASETS/combinatorics_benchmark/benchmark_manifest.json`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/combinatorics_benchmark/benchmark_manifest.json)
- **Unit Test Suite:** [`tests/test_combinatorics_benchmark.py`](file:///C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/tests/test_combinatorics_benchmark.py) (8/8 tests passing)
- **Total Test Suite:** 320/320 tests passing across entire repository.
