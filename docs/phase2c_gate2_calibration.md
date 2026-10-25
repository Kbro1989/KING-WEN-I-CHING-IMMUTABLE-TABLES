# Phase 2C — Gate 2 Calibration Specification

## Frozen Baseline Reference

- **Baseline commit:** `d6e1c09aec` (Phase 2B five-gate evaluation)
- **Gate 2 frozen implementation:** `scripts/phase2b_evaluate_gates.py` (unchanged)
- **Gate 2 frozen inputs:** `DATASETS/phase2b_adversarial_challenge.jsonl` (20 challenges)

## Scope of Calibration

Gate 2 (Ordered token alignment) must be calibrated to:
1. Distinguish token-order defects from operator-identity and structure problems
2. Separate alignment evidence from operator correctness
3. Report alignment evidence without allowing it alone to determine operator correctness

## Calibration Test Set (Gate 2)

### 2.1 Ordered Token Alignment — Defect Cases (must fail Gate 2)

| Case ID | Defect Type | Reference LaTeX | Synthetic (recognized) LaTeX | Expected Gate 2 |
|-----------|-------------|-----------------|------------------------------|-----------------|
| G2-DEF-001 | Token reorder (bounds swapped) | `\\sum_{\\ell=1}^{G}` | `\\sum^{G}_{\\ell=1}` | fail (token order) |
| G2-DEF-002 | Token reorder (sub/sup swapped) | `x_{i}^{2}` | `x^{2}_{i}` | fail (token order) |
| G2-DEF-003 | Missing token | `\\frac{a}{b}` | `\\frac{a}{}` | fail (OCR or extraction) |
| G2-DEF-004 | Duplicated token | `\\sum_{i=1}^{n}` | `\\sum_{i=1}^{n} a_i` | fail (OCR or extraction) |
| G2-DEF-005 | Substitution in operator | `\\sum` | `S` | fail (token order) |
| G2-DEF-006 | Discontinuous alignment | `\\int_{a}^{b} f(x) dx` | `\\int f(x) dx` | fail (OCR or extraction) |

### 2.2 Valid Equivalent Representations (must pass Gate 2)

| Control ID | Description | Reference LaTeX | Synthetic (recognized) LaTeX | Expected Gate 2 |
|------------|-------------|-----------------|------------------------------|-----------------|
| G2-CTL-001 | Simple sum (valid) | `\\sum_{i=1}^{n} a_i` | `\\sum_{i=1}^{n} a_i` | pass |
| G2-CTL-002 | Integral with bounds (valid) | `\\int_{0}^{\\infty} f(x) dx` | `\\int_{0}^{\\infty} f(x) dx` | pass |
| G2-CTL-003 | Product with bounds (valid) | `\\prod_{i=1}^{n} a_i` | `\\prod_{i=1}^{n} a_i` | pass |
| G2-CTL-004 | Partial derivative (valid) | `\\frac{\\partial f}{\\partial x}` | `\\frac{\\partial f}{\\partial x}` | pass |
| G2-CTL-005 | Fraction (valid) | `\\frac{a}{b}` | `\\frac{a}{b}` | pass |
| G2-CTL-006 | Power/exponent (valid) | `x^{2}` | `x^{2}` | pass |
| G2-CTL-007 | Radical (valid) | `\\sqrt{x}` | `\\sqrt{x}` | pass |
| G2-CTL-008 | Relation (≤) (valid) | `x \\leq y` | `x \\leq y` | pass |
| G2-CTL-009 | Set membership (valid) | `x \\in A` | `x \\in A` | pass |
| G2-CTL-010 | Multiple operators (valid) | `\\sum_{i=1}^{n} \\frac{1}{i}` | `\\sum_{i=1}^{n} \\frac{1}{i}` | pass |

### 2.3 Unresolved Cases (record explicitly)

| Case ID | Description | Reference LaTeX | Synthetic (recognized) LaTeX | Expected Outcome |
|----------|-------------|-----------------|------------------------------|-----------------|
| G2-UNRES-001 | Operator substitution with structural difference | `\\frac{d}{dx}` | `d/dx` | unresolved (both alignment and operator) |

### 2.4 Expected Gate 2 Outcomes

| Case ID | Expected Gate 2 Outcome | Failure Source |
|-----------|------------------------|----------------|
| G2-DEF-001 | fail | token order |
| G2-DEF-002 | fail | token order |
| G2-DEF-003 | fail | OCR or extraction |
| G2-DEF-004 | fail | OCR or extraction |
| G2-DEF-005 | fail | token order |
| G2-DEF-006 | fail | OCR or extraction |
| G2-CTL-001 | pass | — |
| G2-CTL-002 | pass | — |
| G2-CTL-003 | pass | — |
| G2-CTL-004 | pass | — |
| G2-CTL-005 | pass | — |
| G2-CTL-006 | pass | — |
| G2-CTL-007 | pass | — |
| G2-CTL-008 | pass | — |
| G2-CTL-009 | pass | — |
| G2-CTL-010 | pass | — |
| G2-UNRES-001 | unresolved | (no failure source; ambiguous) |

**Gate 2 Calibration Target:**
- True positives: 6 (G2-DEF-001 through G2-DEF-006)
- True negatives: 10 (G2-CTL-001 through G2-CTL-010)
- Unresolved: 1 (G2-UNRES-001)
- False positives: 0

---

## Gate 2 Definition (for calibration)

Gate 2 evaluates ordered token alignment independently from operator identity and mathematical structure. A candidate passes Gate 2 if:

1. The token sequence alignment (LCS length / reference token count) ≥ 0.8
2. No token-order violations (adjacent token permutation)
3. No substantial missing tokens (>3 tokens missing)
4. No reordered adjacent tokens detected

Under the Phase 2B frozen implementation, operator substitutions (e.g. `\sum`→`S`) cause Gate 2 to fail because the token set differs. This is the behavioral flaw: operator correctness is captured by Gate 3, not Gate 2. Phase 2C must separate alignment evidence (token order/sequence) from operator correctness (captured by Gate 3).

---

## Expected Outcome (Pre-Specified)

| Case Type | Count | Expected Outcome |
|------------|-------|------------------|
| Ordered token defects (must fail) | 6 | fail |
| Valid equivalent representations (must pass) | 10 | pass |
| Unresolved | 1 | unresolved |

**Calibration target:** 6/6 defect cases detected, 10/10 valid cases pass, 1 unresolved recorded explicitly.

---

## Post-Calibration Verification

1. Run Phase 2C Gate 2 on calibration test set — all expected outcomes achieved.
2. Re-run frozen adversarial challenge set — Gate 2 metrics recorded before/after.
3. Verify Py_compile / import checks.
4. Compare: Gate 2 false positives on operator substitutions corrected; missing/duplicated token detection preserved.