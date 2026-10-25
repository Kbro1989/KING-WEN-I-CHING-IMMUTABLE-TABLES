# Phase 2C — Gate Calibration Specification

**Version:** 1.0  
**Date:** 2026-10-25  
**Base commit:** `d6e1c09aec` (Phase 2B frozen baseline)  
**Branch:** `phase2c-gate-calibration` (to be created)

---

## 1. Gate 3 Operator Substitution Detection — Mutation Tests

### 1.1 Required Mutations (must be detected)

| Mutation ID | Original Operator | Substitution | Detection Target |
|-------------|-------------------|--------------|------------------|
| MUT-001 | `\sum` | `S` | Summation operator |
| MUT-002 | `\int` | `I` | Integral operator |
| MUT-003 | `\partial` | `d` | Partial derivative |
| MUT-004 | `\frac` | `/` | Fraction |

### 1.2 Valid Controls (must NOT be flagged)

| Control ID | Description | LaTeX Example |
|------------|-------------|---------------|
| CTL-001 | Legitimate `\sum` | `\sum_{i=1}^{n} a_i` |
| CTL-002 | Legitimate `\int` | `\int_{0}^{\infty} f(x) dx` |
| CTL-003 | Legitimate `\partial` | `\frac{\partial f}{\partial x}` |
| CTL-004 | Legitimate `\frac` | `\frac{a}{b}` |
| CTL-005 | Legitimate `S` as variable | `S = a + b` |
| CTL-006 | Legitimate `I` as variable | `I = V / R` |
| CTL-007 | Legitimate `d` as variable | `d = r \cdot t` |
| CTL-008 | Legitimate `/` as solidus | `a / b` |

### 1.3 Expected Gate 3 Outcomes

| Test Case | Expected Gate 3 Outcome |
|-----------|-------------------------|
| MUT-001 | `fail` — `operator/structure` |
| MUT-002 | `fail` — `operator/structure` |
| MUT-003 | `fail` — `operator/structure` |
| MUT-004 | `fail` — `operator/structure` |
| CTL-001 | `pass` |
| CTL-002 | `pass` |
| CTL-003 | `pass` |
| CTL-004 | `pass` |
| CTL-005 | `pass` |
| CTL-006 | `pass` |
| CTL-007 | `pass` |
| CTL-008 | `pass` |

---

## 2. Gate 3 Contract Clarification

### Literal Operator Identity vs Mathematical Equivalence

- **Literal identity:** The operator token in the recognized output matches the reference operator exactly (after normalization).
- **Mathematical equivalence:** The substitution preserves mathematical meaning (e.g., `\sum` → `S` in context of "sum").
- **Gate 3 rule:** A substitution fails literal operator identity even if mathematically equivalent. The gate reports `fail` with failure source `operator/structure` when the recognized operator differs from the reference operator.

### Scope
- Applies to: `\sum`, `\prod`, `\int`, `\oint`, `\frac`, `\partial`, `\nabla`, `\dot`, `\ddot`, `\sqrt`, `\approx`, `\leq`, `\geq`, `\neq`, `\equiv`, `\sim`, `\propto`, `\in`, `\subset`, `\cup`, `\cap`, `\langle`, `\rangle`, `\lVert`, `\rVert`, `\lfloor`, `\rfloor`, `\lceil`, `\rceil`, `\pm`, `\mp`, `\times`, `\cdot`, `\infty`, `\mathbb`, `\mathcal`, `\mathfrak`, `\mathbf`, `\boldsymbol`, `\hat`, `\bar`, `\tilde`, `\vec`, `\dot`, `\ddot`
- Does NOT apply to: variable names that coincidentally match operator abbreviations (context-aware)

---

## 3. Regression & Baseline Comparison Framework

### 3.1 Frozen Baseline (Phase 2B)
- **Evaluation script:** `scripts/phase2b_evaluate_gates.py` (commit `d6e1c09aec`)
- **Challenge set:** `DATASETS/phase2b_adversarial_challenge.jsonl` (unchanged)
- **Expected outcomes:** Per-challenge expected gate failures documented in challenge file

### 3.2 Phase 2C Implementation
- **Evaluation script:** `scripts/phase2c_evaluate_gates.py` (new, versioned)
- **Mutation test set:** `DATASETS/phase2c_gate3_mutations.jsonl` (new)
- **Valid control set:** `DATASETS/phase2c_gate3_controls.jsonl` (new)
- **Comparison script:** `scripts/phase2c_compare_baselines.py` (new)

### 3.3 Comparison Output
For each gate, report:

| Gate | Baseline (2B) | Phase 2C | Delta |
|------|---------------|----------|-------|
| Gate 1 | detections / total expected | detections / total expected | +/− |
| Gate 2 | detections / total expected | detections / total expected | +/− |
| Gate 3 | detections / total expected | detections / total expected | +/− |
| Gate 4 | detections / total expected | detections / total expected | +/− |
| Gate 5 | detections / total expected | detections / total expected | +/− |

Plus:
- False positives per gate (Phase 2B vs Phase 2C)
- Valid controls passed (Phase 2C)
- Unresolved/ambiguous cases (explicitly identified, not counted as pass/fail)

---

## 4. Phase 2C Artifacts (Versioned, Not Overwriting Phase 2B)

| Artifact | Path | Status |
|----------|------|--------|
| Phase 2C evaluation script | `scripts/phase2c_evaluate_gates.py` | NEW |
| Gate 3 mutation tests | `DATASETS/phase2c_gate3_mutations.jsonl` | NEW |
| Gate 3 valid controls | `DATASETS/phase2c_gate3_controls.jsonl` | NEW |
| Comparison script | `scripts/phase2c_compare_baselines.py` | NEW |
| Comparison report | `docs/phase2c_calibration_report.md` | NEW |
| Updated evaluation library | `scripts/phase2c_gate_library.py` | NEW (shared library) |

**Phase 2B artifacts remain UNCHANGED:**
- `scripts/phase2b_evaluate_gates.py` ✅ frozen
- `DATASETS/phase2b_adversarial_challenge.jsonl` ✅ frozen
- `docs/phase2b_final_report.md` ✅ frozen

---

## 5. Implementation Order

1. **Create `scripts/phase2c_gate_library.py`** — shared gate implementations (extracted from 2B, enhanced)
2. **Create `scripts/phase2c_evaluate_gates.py`** — uses library, adds Gate 3 improvements
3. **Create mutation/control test sets** — `DATASETS/phase2c_gate3_mutations.jsonl`, `DATASETS/phase2c_gate3_controls.jsonl`
4. **Create comparison script** — runs both implementations, produces comparison report
5. **Run comparison** — document before/after per gate
6. **Calibrate Gates 1, 2, 5** — subsequent commits on same branch

---

## 6. Acceptance Checklist for First Phase 2C Commit

- [ ] Gate 3 detects all 4 mutations (MUT-001..MUT-004)
- [ ] All 8 valid controls (CTL-001..CTL-008) pass Gate 3
- [ ] Phase 2B evaluation script unchanged
- [ ] Phase 2B challenge set unchanged
- [ ] Comparison script produces per-gate detection/miss/false-positive/valid-control table
- [ ] Expected outcomes specified before evaluation (in mutation/control files)
- [ ] Unresolved/ambiguous cases explicitly identified in output

---

**Authorization:** User approved Phase 2C work order. First commit will implement Gate 3 operator-substitution detection with mutation tests and valid controls.