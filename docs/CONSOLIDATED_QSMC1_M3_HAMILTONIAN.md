# QSMC-1 / M3 Hamiltonian — Consolidated Domain Document

**Domain:** QSMC-1 Correspondence Audit / M3 Hamiltonian Energy / M6 Imaginary Amplitude / F-10/F-11/F-12 Validations
**Consolidated from:** 14 source documents (5,239 lines total)
**Date:** 2026-11-03
**Status:** Gate 2 OPEN; M3 provenance FROZEN; F-10/F-11/F-12 VALIDATED

---

## Source Document Index

| # | File | Lines | Role |
|---|------|-------|------|
| 1 | docs/qsmc1-m3-mathematical-validation-f10.md | 459 | F-10 validation (VALIDATED) |
| 2 | docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md | 452 | F-12 validation (VALIDATED) |
| 3 | docs/qsmc1-m3-m6-imaginary-amplitude-f11.md | 327 | F-11 validation (VALIDATED) |
| 4 | docs/qsmc1-m3-dimensional-consistency-analysis.md | 620 | Formal F-10 investigation |
| 5 | docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md | 829 | Provenance audit (Sections 1-15) |
| 6 | docs/qsmc1-m3-floor-ceiling-and-extremum-attainment-research.md | 405 | Raw H distribution research |
| 7 | docs/hamiltonian-lineage-audit-2026-11-02.md | 274 | L3 lineage audit |
| 8 | docs/qsmc1-m3-hamiltonian-energy-correspondence.md | 320 | Hamiltonian energy correspondence |
| 9 | docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md | 186 | Vortex diagnostic (hex 7/52 corrected) |
| 10 | docs/math-term-usage-analysis-2026-10-27.md | 224 | Math term usage analysis |
| 11 | docs/formula-design-review-2026-10-27.md | 235 | Formula design review (abs() sign question OPEN) |
| 12 | docs/hamiltonian-equation-comparison-2026-10-27.md | 451 | October 27 comparison (design intent, never implemented) |
| 13 | docs/qsmc1-m3-scale-mismatch-diagnosis.md | 214 | Scale mismatch diagnosis |
| 14 | docs/qsmc1-m3-m6-reproduction.md | 243 | M6 reproduction |

---

## KNOWN (Established Facts)

### Formula (Current Implementation — emotional_engine.py:408-450)

H = max(0.0, pq_dot - lagrangian)
pq_dot = Σ(momentum_i × q̇_i)
  momentum_i = max(0.0, resolved_vec_i)
  q̇_i = resolved_vec_i - expanded_vec_i
lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2
dy = yang - yin (line count)
yao_dy = yao - 3.0
changing_dy = changing - (6 - changing)

### Coefficients
- 0.5, 0.3, 0.2 — sum to 1.0, dimensionless, undocumented, no theoretical basis
- Designed for ratio-scale (V1) but applied to raw counts (V2) without normalization

### Formula Evolution
- V1 (commit 780d9c4bfe): ratios + phase_shift
- V2 (commit 6239ba9bd7, current): raw counts + resolved/expanded
- October 27 document formula (never implemented): four differentials, /6.0 scaling, equal weights → classified as design intent

### F-10: Semantic and Scale Incompatibility — VALIDATED
- **Numerical compatibility:** pq_dot ~0.01 scale vs lagrangian ~1-5 scale
- **Semantic compatibility:** NOT established — coefficients dimensionless/undocumented
- **Theoretical justification:** NOT established — scalar calculation, not formal Hamiltonian
- lagrangian min 0.7 >> |pq_dot| max 0.15 (4.7× minimum ratio)
- Four questions: (1) dimensional compatibility YES/semantic NO, (2) coefficients dimensionless/undocumented, (3) negative sign consequence of scale disparity, (4) scalar calculation not formal Hamiltonian

### F-11: Imaginary Amplitude — VALIDATED
- Type 2 dependency on M3 (analytical capability ≠ demonstrated nonzero runtime behavior)
- Formula: imag_part = (rv - ev) × (hamiltonian_normalized × phase_complexity × 0.1) — multiplicative path
- Secondary finding: empty line_balance {} at emotional_engine.py:499 — consumer integration defect (F-08)
- Test coverage gap: no test exercises imaginary amplitude path with nonzero inputs

### F-12: One-Sided Clamp Information Loss — VALIDATED
- Clamp formula: H_observed = max(0, H_raw) — 727 distinct raw H → 1 observed (0.0)
- 100% information loss: 727 distinct values collapse to single 0.0
- Raw H distribution: min -5.094550, max -0.560876, mean -1.656209
- pq_dot: min -0.150831, max 0.147103 (727 distinct)
- lagrangian: 7 distinct values (0.700000 to 5.100000)
- Raw H is always negative, so clamped H is always 0.0
- Even if F-10 resolved, clamp would still affect inputs outside [0,1]

### Raw H Distribution (Hypothesis Test)
- 727 distinct raw H values (NOT identical — clamp is sole information-loss mechanism)
- H == 0.0 for all 1,536 states after clamp
- Category A (artificial floor): confirmed
- Category B (artificial ceiling): latent
- Category C (unattainable supremum): not needed
- Category D (numerical optimizer failure): not applicable

### Provenance
- Formula first appeared: commit 6239ba9bd7 (V2)
- V1 formula (commit 780d9c4bfe): ratios + phase_shift
- QuantumLab: 9 user commits (infrastructure only); Hamiltonian by rasidi3112 in e85f38b — RULED OUT as source
- Wiki math corpus: 139 entries; standard vocabulary only; no M3 formula or coefficients — RULED OUT
- Three layers: (1) Implementation, (2) Documentation, (3) Mathematical interpretation

### Three-Layer Finding
1. Implementation: Scalar calculation with Hamiltonian-inspired naming; not a formal Hamiltonian
2. Documentation: October 27 document describes different formula (never implemented); classified as design intent
3. Mathematical interpretation: Coefficients dimensionless/undocumented; no theoretical basis; scale mismatch

### M6 Inheritance
- M6 (interference/coherence) inherits zero-energy condition from M3
- Imaginary amplitude formula: imag_part = (rv - ev) × (hamiltonian_normalized × phase_complexity × 0.1) — multiplicative path
- Empty line_balance {} at emotional_engine.py:499 — consumer integration defect (F-08)
- Test coverage gap: no test exercises imaginary amplitude path with nonzero inputs

### Vortex Diagnostic
- Scale mismatch: pq_dot 0.009543 vs L 2.500000 for Hex 1 (confirmed by F-10)
- Downstream impact: rotation=0, scale=0.75, imag=0, phase=phase/8 (confirmed by F-11)
- Proposed /4.0 normalization: STILL OPEN/untested
- Hex numbers corrected: 15/20 → 7/52

### Formula Design Review (abs() Sign Question — SEPARATE from F-10/F-12)
- coherence: abs(old_dy) gives 0.05 vs signed 0.25 for all-yin
- voiceWeight: uses absolute old_yang count instead of signed old_dy
- chaos: abs(dy) — likely intentional for magnitude
- Status: OPEN — semantics not established

### M3 Provenance Investigation: FROZEN
- Complete at evidence boundary
- No reason to reopen unless new primary evidence appears

---

## UNKNOWN (Gaps and Unresolved)

1. F-10 semantic compatibility: Not established — coefficients dimensionless/undocumented; theoretical justification not established
2. F-10 theoretical justification: Not established — scalar calculation, not formal Hamiltonian
3. F-11 imaginary amplitude runtime behavior: Analytical capability ≠ demonstrated nonzero runtime behavior (test coverage gap)
4. F-12 clamp resolution: Even if F-10 resolved, clamp would still affect inputs outside [0,1]; resolution strategy undecided
5. abs() sign question: Separate from F-10/F-12; semantics not established; expected outputs not defined
6. /4.0 normalization: Proposed in vortex diagnostic; unimplemented and untested
7. October 27 document formula: Never implemented; classified as design intent; no code changes authorized
8. M6 line_balance integration: Empty line_balance {} at emotional_engine.py:499; consumer integration defect (F-08)
9. Convex-combination interpretation: Weights sum to 1.0 but elements not in common mathematical space — unsupported
10. Dimensional mismatch root cause: Coefficients designed for ratio-scale but applied to raw counts; formal unit derivation not completed

---

## PARTIAL (Incomplete Items)

1. F-10 VALIDATED — numerical compatibility established; semantic compatibility not established; theoretical justification not established
2. F-11 VALIDATED — type 2 dependency; analytical capability; empty line_balance secondary finding; test coverage gap
3. F-12 VALIDATED — clamp sole information-loss mechanism; 727→1 distinct values; 100% information loss
4. Vortex diagnostic — scale mismatch confirmed; downstream impact confirmed; /4.0 normalization still open
5. Formula design review — abs() sign question identified; semantics not established
6. M3 provenance — frozen; three layers identified; no source found
7. Raw H distribution — 727 distinct values confirmed; hypothesis test complete

---

## Cross-Reference Status

| Document | Cross-Reference Note |
|----------|---------------------|
| docs/hamiltonian-equation-comparison-2026-10-27.md | Added |
| docs/formula-design-review-2026-10-27.md | Added |
| docs/audit-drift-report-2026-10-27.md | Added (§1.1, §6.1, Category 6) |
| docs/traceability-matrix-audit-2026-10-27.md | Added |
| docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md | Added (hex 7/52 corrected) |
| docs/math-term-usage-analysis-2026-10-27.md | Added |
| docs/information-loss-remediation-register.md | Added (R-14, R-15) |
| docs/cross-reference-audit-2026-11-02.md | Created (348 lines) |
| docs/remediation-verification-matrix.md | Authoritative for F-01–F-08 |

---

## Machine-Readable Summary

```json
{
  "domain": "qsmc1_m3_hamiltonian",
  "status": "gate_2_open",
  "m3_provenance": "frozen",
  "findings": {
    "F-10": {"status": "VALIDATED", "numerical": "established", "semantic": "not_established", "theoretical": "not_established"},
    "F-11": {"status": "VALIDATED", "dependency": "type_2", "runtime": "not_demonstrated", "secondary": "F-08_empty_line_balance"},
    "F-12": {"status": "VALIDATED", "mechanism": "sole", "distinct_raw": 727, "distinct_observed": 1, "information_loss": "100%"}
  },
  "formula": {
    "current": "H = max(0.0, pq_dot - lagrangian)",
    "pq_dot": "Σ(momentum_i × q̇_i), momentum_i = max(0.0, resolved_vec_i), q̇_i = resolved_vec_i - expanded_vec_i",
    "lagrangian": "abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2",
    "coefficients": [0.5, 0.3, 0.2],
    "raw_H_range": [-5.094550, -0.560876],
    "raw_H_distinct": 727,
    "observed_H": 0.0,
    "observed_distinct": 1
  },
  "open_items": ["F-10_semantic", "F-10_theoretical", "F-11_runtime", "F-12_resolution", "abs_sign_question", "normalization_4.0", "M6_line_balance", "convex_combination", "dimensional_mismatch_root"],
  "frozen": ["M3_provenance", "QSMC1_baseline"]
}
```