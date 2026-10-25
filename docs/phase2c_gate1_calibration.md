# Phase 2C — Gate 1 Calibration Specification

## Frozen Baseline Reference

- **Baseline commit:** `d6e1c09aec` (Phase 2B five-gate evaluation)
- **Gate 1 frozen implementation:** `scripts/phase2b_evaluate_gates.py` (unchanged)
- **Gate 1 frozen inputs:** `DATASETS/phase2b_adversarial_challenge.jsonl` (20 challenges)

## Scope of Calibration

Gate 1 (Geometry and clearance) must be calibrated to distinguish:
- **Short valid equations** that should pass (negative controls)
- **Genuine clipping/boundary contact** that should fail (positive controls)
- **Short-equation false positives** preserved as validated failures

## Calibration Test Set (Gate 1)

### 1.1 Negative Controls (valid short equations — must pass)

| Control ID | Description | Reference LaTeX | Expected Gate 1 |
|------------|-------------|-----------------|-----------------|
| G1-CTRL-001 | Short valid equation (single term) | `a^2 + b^2 = c^2` | pass |
| G1-CTRL-002 | Short valid equation (product) | `pq = rs` | pass |
| G1-CTRL-003 | Short valid equation (power) | `x^2 = 4` | pass |
| G1-CTRL-004 | Short valid equation (difference) | `x - y = z` | pass |
| G1-CTRL-005 | Short valid equation (fraction) | `a/b = c/d` | pass |
| G1-CTRL-006 | Short valid equation (relation) | `x ≥ 0` | pass |
| G1-CTRL-007 | Short valid equation (simple radical) | `√x = 3` | pass |

### 1.2 Positive Controls (genuine geometry/violation cases — must fail)

| Control ID | Description | Reference LaTeX | Expected Gate 1 |
|------------|-------------|-----------------|-----------------|
| G1-CTRL-008 | Truncated right edge | `x^2 + y^2 = c` [TRUNCATED] | fail (geometry/crop) |
| G1-CTRL-009 | Boundary contact (operand touching crop edge) | `sin(x) = 0` (crop at symbol edge) | fail (geometry/crop) |
| G1-CTRL-010 | Insufficient clearance (tight crop around equal sign) | `a = b` (micro-cropped) | fail (geometry/crop) |
| G1-CTRL-011 | Missing left operand | `= x + 1` (left side cropped) | fail (geometry/crop) |
| G1-CTRL-012 | Missing right operand | `x + 1 =` (right side cropped) | fail (geometry/crop) |

### 1.3 Preserved Phase 2B Short-Equation False Positives

| Control ID | Description | Reference LaTeX | Expected Gate 1 |
|------------|-------------|-----------------|-----------------|
| G1-P2B-001 | Short equation from Phase 2B adversarial set (retained) | `x^2 + y^2 = c` (truncated variant) | fail (validate trace) |
| G1-P2B-002 | Short equation from Phase 2B adversarial set (retained) | `sin(x) = 0` (boundary variant) | fail (validate trace) |

### 1.4 Expected Gate 1 Outcomes

| Control ID | Expected Gate 1 Outcome | Failure Source |
|------------|------------------------|----------------|
| G1-CTRL-001 | pass | — |
| G1-CTRL-002 | pass | — |
| G1-CTRL-003 | pass | — |
| G1-CTRL-004 | pass | — |
| G1-CTRL-005 | pass | — |
| G1-CTRL-006 | pass | — |
| G1-CTRL-007 | pass | — |
| G1-CTRL-008 | fail | geometry/crop (truncation) |
| G1-CTRL-009 | fail | geometry/crop (boundary contact) |
| G1-CTRL-010 | fail | geometry/crop (insufficient clearance) |
| G1-CTRL-011 | fail | geometry/crop (missing operand) |
| G1-CTRL-012 | fail | geometry/crop (missing operand) |
| G1-P2B-001 | fail | geometry/crop (or pending trace review) |
| G1-P2B-002 | fail | geometry/crop (or pending trace review) |

**Gate 1 Calibration Target:**
- True positives (defects detected): 5 (G1-CTRL-008 through G1-CTRL-012)
- False positives (controls flagged): 0 (G1-CTRL-001 through G1-CTRL-007)
- Preserved P2B failures: 2 (G1-P2B-001 through G1-P2B-002)

---

## Gate 1 Definition (for calibration)

Gate 1 evaluates crop geometry and clearance for mathematical content. A candidate passes Gate 1 if:

1. No truncation indicators (unmatched `\left`, unmatched `<`...`>`, unbalanced braces, trailing operator, empty bound operand, very short output)
2. No explicit truncation markers (`[TRUNCATED]`, `...` near end of output)
3. Length ratio (recognized/reference) ≥ 0.5 (no significant clipping)

Under the Phase 2B frozen implementation, short equations that are structurally complete but visually small fail Gate 1 due to the length-ratio heuristic. This is the behavioral flaw to calibrate for Phase 2C — not to remove the geometric check, but to distinguish genuine clearance violations from legitimate short equations.

---

## Expected Outcome (Pre-Specified)

| Control Type | Count | Expected Outcome |
|--------------|-------|------------------|
| Valid short equations (negative controls) | 7 | pass |
| Genuine geometry violations (positive controls) | 5 | fail |
| Preserved P2B failures | 2 | fail |

**Calibration target:** 0 false positives on valid equations, 5/5 genuine violations detected, 2/2 P2B failures retained.

---

## Post-Calibration Verification

1. Run Phase 2C Gate 1 on calibration test set — all expected outcomes achieved.
2. Re-run frozen adversarial challenge set — Gate 1 metrics recorded before/after.
3. Verify Py_compile / import checks.
4. Compare: Gate 1 false-positive count on valid short equations decreases from 26 (Phase 2B) to 0 (Phase 2C), while genuine violation detection remains 5/5.