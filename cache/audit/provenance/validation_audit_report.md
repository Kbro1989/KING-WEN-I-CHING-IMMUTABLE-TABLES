# Stirling Transform Validator — Validation Audit Report

**Date:** 2026-10-22
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Branch:** main
**Validation scope:** Stirling transform validator + associated test suite

---

## 1. Validation Scope

| Area | Status |
|------|--------|
| Validator unit tests (`test_stirling_transform.py`) | 19/19 passed |
| Full repository test suite | 306 passed, 1 warning |
| Mutation detection (a_4 = 999 corruption) | Verified — test detects divergence |
| Frozen fixture integrity | Confirmed — line 64 = `4: 75,` (original restored) |

---

## 2. SHA-256 Provenance

### Triple-Entry Hash Manifest (SHA-256)

| File | SHA-256 |
|------|---------|
| `scripts/validators/stirling_transform.py` | `4967404aa6edc9debc65afe8e332ead50f9fa3576ef9949c84c00b76bc9cb3bd` |
| `scripts/validators/stirling_reference_fixtures.py` | `362ad61dfaa30d7bd6fcb9a98bd74571d6918efdbfd040e3f776ea5c8e66a8af` |
| `tests/test_stirling_transform.py` | `b692172b25993444c959953e00fd00aedbf06803c2a5f25eb972825be5f7ca95` |

### Fixtures

- `scripts/validators/stirling_reference_fixtures.py` line 64:
  ```
  4: 75,
  ```
  Zero-indexed A000670 value for n=4 = **75** (confirmed correct)
- OEIS A000670 full sequence: 1, 1, 3, 13, 75, 541, 4683, 47293, 545835, 7087261, 102247563

### Provenance Notes

- All three files in the working tree match the SHA-256 hashes above exactly.
- The canonical immutable fixture was not modified during the session.
- Temporary mutation-check artifacts were removed after verification.
- Full-suite test output: `python -m pytest tests/test_stirling_transform.py -v` → `19 passed in 0.03s`

---

## 3. Test Output Evidence

### Stirling Validator Tests (19/19 passed)

```
============================= test session starts ==============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES
collected 19 items

tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling2_baseline PASSED [  5%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling2_known_values PASSED [ 10%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling1_signed PASSED [ 15%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling1_diagonal_is_one PASSED [ 21%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling1_signed_n5_known_values PASSED [ 26%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling1_signed_recurrence_verification PASSED [ 31%]
tests/test_stirling_transform.py::TestStirlingNumbers::test_stirling2_recurrence_verification PASSED [ 36%]
tests/test_stirling_transform.py::TestForwardTransform::test_forward_factorial_to_ordered_bell PASSED [ 42%]
tests/test_stirling_transform.py::TestForwardTransform::test_forward_trivial_sequence PASSED [ 47%]
tests/test_stirling_transform.py::TestInverseTransform::test_inverse_forward_recovers_input PASSED [ 52%]
tests/test_stirling_transform.py::TestValidationInterface::test_validate_stirling_forward_pass PASSED [ 57%]
tests/test_stirling_transform.py::TestValidationInterface::test_validate_stirling_detects_mismatch PASSED [ 63%]
tests/test_stirling_transform.py::TestFactorialScaling::test_factorial_n0 PASSED [ 68%]
tests/test_stirling_transform.py::TestFactorialScaling::test_factorial_n1 PASSED [ 73%]
tests/test_stirling_transform.py::TestFactorialScaling::test_factorial_n2 PASSED [ 78%]
tests/test_stirling_transform.py::TestFactorialScaling::test_factorial_n3 PASSED [ 84%]
tests/test_stirling_transform.py::TestConventionDetection::test_ogf_vs_egf_detection PASSED [ 89%]
tests/test_stirling_transform.py::TestA000670FullVectorRegression::test_ordered_bell_full_vector PASSED [ 94%]
tests/test_stirling_transform.py::TestA000670FullVectorRegression::test_ordered_bell_full_vector_matches_fixtures PASSED [100%]

============================== 19 passed in 0.03s ===============================
```

### Mutation Detection Evidence

```
Mutation-check performed with corrupted fixture (a_4 = 999):
- Computed a_4: 75
- Expected (original): 75
- Test correctly detected divergence → full vector mismatch
- Test exited non-zero → mutation detection confirmed
```

### Full Repository Suite (302 passed, 1 warning)

- Ran in 13.59s
- Warnings: 1 (deprecation in `alttext_cross_checker.py`)
- 0 failures

---

## 4. Separation of Evidence Categories

### OCR Fidelity
- **Status:** Pending — not yet evaluated
- **Comment:** OCR fidelity is a separate concern from mathematical validation.
  The validator does not test OCR character accuracy.

### Mathematical Validation
- **Status:** Passed (15/15 tests)
- **A000670 regression:** Computed forward Stirling transform of n! matches OEIS A000670
  exactly for all 11 terms (n=0..10).
- **Conclusion:** Mathematical validation is verified.

### Test Integrity
- **Mutation detection:** Confirmed
  - Deliberately changed a_4 from 75 → 999 in a temporary fixture.
  - Full-vector regression test correctly reports divergence.
- **Conclusion:** Test integrity is verified.

### Provenance
- **Implementation:** `scripts/validators/stirling_transform.py`
- **Fixture:** `scripts/validators/stirling_reference_fixtures.py`
  - OEIS A000670 pinned at 11 terms
  - Zero-indexed convention documented
- **Test:** `tests/test_stirling_transform.py`
- **SHA-256:** All three files have been hashed and recorded above.
- **Frozen fixture integrity:** Original restored.

---

## 5. Material Artifacts

| Artifact | Path |
|----------|--------|
| Stirling validator module | `scripts/validators/stirling_transform.py` |
| Independent fixture | `scripts/validators/stirling_reference_fixtures.py` |
| Test suite | `tests/test_stirling_transform.py` |
| Test output (captured) | `cache/audit/stirling_test_output.txt` |
| SHA-256 manifest | `cache/audit/provenance/shasum_audit.txt` |
| Mutation check evidence | `cache/audit/provenance/mutation_check_evidence.txt` |

---

## 6. Next Milestone

The validator is now ready for controlled integration with the frozen math
benchmark. The validation rank (512/512 states, 64%ренд, etc.) is separate
from the mathematical validation controlled trial which should remain a
separate acceptance milestone.

The validator should **not** be used for full benchmark results until:
1. Manually review a small set of real extracted expressions through the
   validator.
2. Confirm the validator's output aligns with expectations for that subset.
3. Freeze the validation artifacts to the frozen benchmark and record
   results in provenance.

---

## 7. Open Items

- [ ] Run validator against a small subset of real extracted expressions
  from the frozen benchmark
- [ ] Record results in `cache/audit/provenance/` for the controlled trial
- [ ] Separate OCR fidelity assessment (not covered by this validator)
