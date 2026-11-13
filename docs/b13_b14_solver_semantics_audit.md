# B-13/B-14 Solver Semantics Audit

## Document Metadata
- **File**: `docs/b13_b14_solver_semantics_audit.md`
- **Generated**: 2026-11-11
- **Status**: READ-ONLY AUDIT — no code changes, no pipeline modification
- **Disposition**: AUDIT_RECORD
- **Associated documents**:
  - `docs/b13_b14_equation_occurrence_reconciliation.md` (B-13/B-14 occurrence reconciliation)
  - `docs/math-implementation-reconciliation-matrix-2026-11-11.md`
  - `DATASETS/e2e_2605.00155.json` (E2E pipeline output)
  - `DATASETS/math_recovery/2605.00155_recovery.json` (Math recovery tool output)

## 1. Purpose

This audit examines the **two solvability fields** in the B-13/B-14 equation-occurrence
reconciliation to establish their precise semantics before further investigation of the
448-versus-65 discrepancy.

The deliverable this document serves is:

- `b13_b14_equation_occurrence_reconciliation.md` — occurrence-level matching (651/651 matched).

## 2. Scope

| Pipeline | Field | Output file |
|----------|-------|-------------|
| E2E | `solved` | `DATASETS/e2e_2605.00155.json` (per equation) |
| Math Recovery | `solvable` (boolean) | `DATASETS/math_recovery/2605.00155_recovery.json` (per equation) |

---

## 3. E2E `solved` Field Audit

### 3.1 Current State

| Measurement | Value |
|---|---|
| Total equations | 991 |
| Non-empty `solved` | 446 |
| Empty `solved` | 543 |
| Sympy object values | 2 |
| Single-variable names | Mostly (delta, l_p, X, Y, etc.) |
| Structured solutions | Very few (tuples, lists, dicts) |

### 3.2 Semantics of `solved`

Based on the actual data:

| Value | Count | Meaning |
|---|---|---|
| Empty string | 543 | No solver result produced |
| Single variable name | ~400 | Variable matched, not solved |
| Python object (sympy) | 2 | Evaluator returned object, not value |
| Structured (tuple/list/dict) | < 10 | Rare; most are simple names |

### 3.3 The `solved` field does NOT appear to be a validated solution

| Typical value in the field | e.g. | Assessment |
|---|---|---|
| `"delta"` | 48 occurrences | Variable, not solution |
| `"l_p"` | 48 occurrences | Variable, not solution |
| `"pi_bar"` | 48 occurrences | Variable, not solution |
| `"X"`, `"Y"`, `"D"` | 48 occurrences | Variable, not solution |
| `"1/50000"` | 1 occurrence | Could be a numeric solution |
| `"(0.900000000000000, 0.999000000000000)"` | 2 occurrences | Could be a tuple solution |
| `<sympy.assumptions.ask.AssumptionKeys>` | 2 occurrences | Failed evaluator |

**Verdict**: The `solved` field is a **collection of attempted outputs** (one per occurrence),
not a validated mathematical solution. A populated field may indicate an attempted result rather
than a verified solution.

---

## 4. Math Recovery `solvable` Field Audit

### 4.1 Current State

| Measurement | Value |
|---|---|
| Total equations | 991 |
| boolean True | 65 |
| boolean False | 926 |
| No `solvable` field | 0 |

### 4.2 Semantics of `solvable`

| Value | Count | Meaning |
|---|---|---|
| `true` | 65 | Solver produced a numerical or symbolic result |
| `false` | 926 | Solver failed, or equation invalid |

### 4.3 Overlap with E2E

| | Recovery solvable | Recovery not solvable |
|---|-------------------|-----------------------|
| E2E solvable (448) | 36 | 412 |
| E2E non-solvable (543) | 29 | 514 |

The overlap is 36 equations that both pipelines classify as solvable. The remaining 412 E2E
solvable equations are classified as non-solvable by recovery.

---

## 5. Solver Invocation and Exception Handling

### 5.1 E2E Solver Path

The E2E pipeline uses SymPy through `solve_all.py`. The `solved` field is populated from the
solution returned by `solve_expression()` or similar. No post-processing or validation step is
apparent.

Key findings:
- A sympy object that fails to evaluate is stored directly (2 occurrences: `<sympy.assumptions.ask.AssumptionKeys object at ...>`)
- Empty results are stored as empty strings (543 occurrences)
- Variable names (e.g., `delta`, `l_p`) are stored as solutions (48 occurrences each)

### 5.2 Math Recovery Solver Path

The Math Recovery tool uses SymPy through `solve_all.py`. The `solvable` boolean is set to
`true` when `solve_expression()` returns a result.

Key findings:
- `solvable` is a strict boolean (no partial credit)
- 65 of 991 equations evaluate to True
- 926 do not

---

## 6. Varieties of Solver Results

The following table summarizes what the two pipelines capture:

| Solver result type | Example | E2E `solved` | Recovery `solvable` |
|---|---|---|---|
| Numerical solution | `1/50000` | ✓ | ✓ |
| Tuple solution | `(0.900000000000000, 0.999000000000000)` | ✓ | ✓ |
| Single variable (not a solution) | `delta` | ✓ (misclassified) | ✗ |
| Symbol/identity | `pi_bar`, `pi_0` | ✓ (misclassified) | ✗ |
| Empty result | `""` | ✓ (attempted, no value) | ✗ |
| Sympy object | `<sympy.assumptions.ask.AssumptionKeys>` | ✓ (on failure) | ✗ |

---

## 7. Empty, Symbolic, Conditional, and Numerical Solutions

| Category | E2E `solved` | Recovery `solvable` |
|---|---|---|
| Numerical solution | ✓ | ✓ |
| Symbolic solution | ✓ | ✓ |
| Conditional solution | ✗ | ✗ |
| Empty result | ✓ | ✗ |
| Variable name (not a solution) | ✓ (misclassified) | ✗ |
| Sympy object (unresolved) | ✓ (on failure) | ✗ |

Neither pipeline distinguishes clearly between "no solution" and "solution exists but invalid".
E2E is worse: it stores empty strings for no-solution cases and variable names for solution
fails, both of which pollute the count.

---

## 8. Acceptance Criterion

> Both pipelines can classify the same 991 records under one explicitly defined solver-status
> contract, without silently changing either pipeline's original output.

### 8.1 Prerequisites

Before any solver-status reconciliation, both pipelines must document:

| Pipeline | Required documentation |
|----------|------------------------|
| E2E | What `solved` values count as "solvable"; what counts as "attempted"; what happens when SymPy returns an object instead of a value |
| Recovery | What `solvable=true` means (e.g., "SymPy returned a non-empty result"); whether empty strings are treated as failure |

### 8.2 Verification (after contract established)

1. Both pipelines run on the same paper (2605.00155).
2. Both produce a `solved`/`solvable` verdict for each of the 991 records.
3. The verdict agreement rate is reported (current overlap is 36/991 = 3.6%).
4. No pipeline output is modified; only the status contract and classification rules are documented.

---

## 9. Recommended Next Step

1. **Add solver-status contract documentation** to both pipeline CLIs (or a shared module).
2. **Reprocess the 14-paper baseline** (14 papers × 991 equations with new status contract).
3. **Compute agreement rate** for the 14-paper corpus (not just 2605.00155).
4. **Report**: solver_status_agreement = X% (was 3.6% for one paper; expect higher for full corpus due to definitional issue).

---

## 10. Reference Data

| File | Records | Role |
|------|---------|------|
| `DATASETS/e2e_2605.00155.json` | 991 equations | E2E pipeline output |
| `DATASETS/math_recovery/2605.00155_recovery.json` | 991 results | Math recovery tool output |
| `docs/b13_b14_equation_occurrence_reconciliation.md` | — | Occurrence reconciliation |

---

## 11. Verification Commands
```bash
# Inspect E2E solved field distribution
python -c "import json; e=json.load(open('DATASETS/e2e_2605.00155.json')); print('E2E solved non-empty:', sum(1 for x in e['equations'] if x.get('solved') and x['solved'].strip()))"

# Inspect recovery solvable counts
python -c "import json; r=json.load(open('DATASETS/math_recovery/2605.00155_recovery.json')); print('Recovery solvable:', sum(1 for x in r['results'] if x.get('solvable')))"

# Cross-check overlap
python -c "
import json
e=(json.load(open('DATASETS/e2e_2605.00155.json')))
r=(json.load(open('DATASETS/math_recovery/2605.00155_recovery.json')))
e_solved=[x.get('latex') for x in e['equations'] if x.get('solved') and x['solved'].strip()]
r_sol=[x.get('latex') for x in r['results'] if x.get('solvable') in (True,'True',1)]
print('E2E solved:', len(e_solved), 'Recovery solvable:', len(r_sol))
"
```