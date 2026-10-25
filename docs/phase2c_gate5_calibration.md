# Phase 2C — Gate 5 Calibration Specification

## Frozen Baseline Reference

- **Baseline commit:** `d6e1c09aec` (Phase 2B five-gate evaluation)
- **Gate 5 frozen implementation:** `scripts/phase2b_evaluate_gates.py` (unchanged)
- **Gate 5 frozen inputs:** `DATASETS/phase2b_adversarial_challenge.jsonl` (20 challenges)

## Scope of Calibration

Gate 5 (Authoritative provenance) must be calibrated to:
1. Document its role as an eligibility prerequisite, NOT a detector of extraction errors
2. Never count an eligibility check that always passes on eligible inputs as evidence of extraction accuracy
3. Block or mark as ineligible when provenance is missing, invalid, or mismatched

## Calibration Test Set (Gate 5)

### 5.1 Provenance Eligibility — Valid Inputs (must pass eligibility gate)

| Control ID | Description | Reference ID | Provenance Source | Expected Gate 5 |
|------------|-------------|--------------|-------------------|-----------------|
| G5-CTL-001 | Valid arXiv HTML source (x-tex annotation) | `2605.00155:S4.E11Xa.m3` | `html` | verified |
| G5-CTL-002 | Valid MathML annotation | `2009.00031:m1` | `mathml` | verified |
| G5-CTL-003 | Valid PDF fallback with page reference | `2605.00224:S2.SS2.SSS0.Px1.p1.m2` | `pdf_footer` | verified |
| G5-CTL-004 | Valid reference with node ID | `2009.00031:S3.SS1.p1.m1` | `html_node` | verified |
| G5-CTL-005 | Valid reference with composite ID | `2605.18130:alg1.l15.m1` | `latex_source` | verified |

### 5.2 Provenance Deficiency — Invalid/Missing Inputs (must be blocked/ineligible)

| Control ID | Description | Reference ID | Provenance Source | Expected Gate 5 |
|------------|-------------|--------------|-------------------|-----------------|
| G5-CTL-006 | Missing provenance (no source reference) | `dummy` | null | blocked (ineligible) |
| G5-CTL-007 | Unsupported provenance source | `2605.00155:S4.E11Xa.m3` | `legacy_format` | blocked (ineligible) |
| G5-CTL-008 | Mismatched provenance (source does not match reference) | `2605.00155:S4.E11Xa.m3` | `pdf_footer` | blocked (ineligible) |
| G5-CTL-009 | Corrupted provenance data | `2605.00155:S4.E11Xa.m3` | `corrupted` | blocked (ineligible) |

### 5.3 Expected Gate 5 Outcomes

| Control ID | Expected Gate 5 Outcome | Status |
|------------|------------------------|--------|
| G5-CTL-001 | verified | eligible |
| G5-CTL-002 | verified | eligible |
| G5-CTL-003 | verified | eligible |
| G5-CTL-004 | verified | eligible |
| G5-CTL-005 | verified | eligible |
| G5-CTL-006 | blocked | ineligible |
| G5-CTL-007 | blocked | ineligible |
| G5-CTL-008 | blocked | ineligible |
| G5-CTL-009 | blocked | ineligible |

**Gate 5 Calibration Target:**
- Eligible (verified): 5 (G5-CTL-001 through G5-CTL-005)
- Ineligible (blocked): 4 (G5-CTL-006 through G5-CTL-009)
- False positives (eligible flagged without authorization): 0
- False negatives (ineligible passed as eligible): 0

---

## Gate 5 Definition (for calibration)

Gate 5 (Authoritative provenance) evaluates whether the evaluation record carries a valid, authoritative provenance reference. It is a **prerequisite for accepting an evaluation record**, not a detector of extraction errors.

**Rule:**
- **Eligible provenance:** `verified` — evaluation may proceed to gate scoring and disposition.
- **Missing, invalid, or mismatched provenance:** `blocked` — evaluation is ineligible; no gate scoring applied; result recorded as `insufficient_provenance`.

**Critical distinction:**
- Gate 5 outcome (`verified` vs `blocked`) is NOT evidence of extraction accuracy.
- A candidate with verified provenance may still fail gates 1-4 (extraction errors are not detected by provenance alone).
- A candidate with missing provenance is blocked before any extraction accuracy can be evaluated.

---

## Expected Outcome (Pre-Specified)

| Control Type | Count | Expected Outcome |
|------------|-------|------------------|
| Valid provenance (eligible) | 5 | verified |
| Invalid/Missing provenance (ineligible) | 4 | blocked |

**Calibration target:** 5/5 eligible cases correctly approved; 4/4 ineligible cases correctly blocked. Zero false positives (eligible flagged without authorization) and zero false negatives (ineligible passed as eligible).

---

## Post-Calibration Verification

1. Run Phase 2C Gate 5 on calibration test set — all expected outcomes achieved.
2. Re-run frozen adversarial challenge set — Gate 5 metrics recorded before/after.
3. Verify Py_compile / import checks.
4. Document that Gate 5 is an eligibility prerequisite, not a detector of extraction errors.

---

## Downstream Interpretation

After calibration:

- A candidate with `gate_5 = verified` requires gate scoring (1-4) to determine final disposition.
- A candidate with `gate_5 = blocked` requires provenance repair before evaluation can proceed.
- A candidate with `gate_5 = unresolved` (if introduced) requires human adjudication.
- No per-gate metric from Gate 5 may be interpreted as an extraction accuracy metric.