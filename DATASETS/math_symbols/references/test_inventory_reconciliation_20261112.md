# Test Inventory Reconciliation — Math-to-PDF Association Contract v1

## Result

**16 tests collected and passing — NOT 19.**

The reported test count of 19 (as summarized in the prior audit) does not
reconcile with the actual test suite. The correct inventory, per
`python -m pytest scripts/test_math_pdf_association_contract_v1.py
--collect-only -q` (exit 0, "16 tests collected in 0.08s"), is:

| Group | Tests | Count |
|-------|-------|-------|
| Contract (C1–C8) | test_contract_01..08 | 8 |
| Association (A1–A4) | test_association_01..04 | 4 |
| Contract boundary (C9–C12) | test_contract_09..12 | 4 |
| **Total** | | **16** |

## Where the 19-count came from

The earlier audit's reconciliation table listed:

| Claimed group | Claimed count | Actual |
|---------------|---------------|--------|
| C1–C8         | 8             | 8      |
| A1–A6         | 6             | **4**  |
| C11–C12       | 2             | 2      |
| C13           | 1             | **0** (no test_contract_13 exists) |
| C10           | 1             | 1      |
| C9            | 1             | 1      |
| **Total**     | **19**        | **16** |

The two sources of inflation:

1. **A1–A6 was miscounted.** The test file defines four association tests
   (`test_association_01_msup_separation`, `test_association_02_mfrac_role_division`,
   `test_association_03_preserved_glyph_bbox`, `test_association_04_unresolved_as_valid_status`).
   There is no `test_association_05` or `test_association_06`.

2. **C9, C10, C11, C12 were consumed as five separate slots (C11–C12, C13,
   C10, C9) when they are four tests.** There is no `test_contract_13`.

## Correct reconciliation table

| Area                                      | Actual tests | Reported | Verdict        |
| ----------------------------------------- | ------------ | -------- | -------------- |
| Production sidecar module                 | Implemented  | complete | OK             |
| AST/extractor version metadata            | Implemented  | complete | OK             |
| Version compatibility enforcement         | Implemented  | complete | OK             |
| Stale-record quarantine                   | Implemented  | complete | OK             |
| Identical-input determinism               | 1 (C9)       | tested   | OK             |
| Input-order determinism                   | 1 (C12)      | excluded | correct qual.  |
| Cross-runtime determinism                 | not claimed  | excluded | correct qual.  |
| Automatic AST-to-glyph association accuracy | not tested | open     | correct qual.  |
