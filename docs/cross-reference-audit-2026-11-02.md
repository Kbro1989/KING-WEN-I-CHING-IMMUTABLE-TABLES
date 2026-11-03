# Cross-Reference: Older Audit Reports vs. Current Run Findings

## Purpose

This document cross-references findings from older audit reports against what was established in the current run (2026-11-02). It identifies which older findings are now confirmed, superseded, or still open.

## Current run findings (F-10 through F-12)

| Finding | Status | Core result |
|---|---|---|
| F-10 | VALIDATED | Semantic/scale incompatibility — V1→V2 coefficients unchanged across scale change |
| F-11 | VALIDATED | M3-dependent imaginary amplitude — multiplicative dependency, type 2 |
| F-12 | VALIDATED | Clamp-induced information loss — 727→1 distinct values, 100% loss |

---

## 1. Audit-drift-report-2026-10-27.md — Cross-reference

### 1.1 Hamiltonian Energy = 0.0 (All States) — §1.1

| Older report status | Current run status | Cross-reference |
|---|---|---|
| "FIXED (partially)" — `or 0.35` fixed, `_hamiltonian_energy` signature updated, but H still 0.0 | F-10 VALIDATED, F-12 VALIDATED | **CONFIRMED and EXTENDED.** The older report correctly identified H=0.0 as unresolved. The current run established the root cause (F-10: scale mismatch) and the mechanism (F-12: one-sided clamp). The "partially fixed" status is now superseded: the zero-preservation fix (Entry 1) was verified (13/13 PASS), but the scale mismatch and clamp are confirmed as independent, unresolved findings. |

### 1.2 Ternary 729/5832 Not in Pipeline Output — §1.2

| Older report status | Current run status | Cross-reference |
|---|---|---|
| NOT FIXED — 729 permutations computed but discarded, ternary not in pipeline | Not investigated in this run | **STILL OPEN.** Not addressed by F-10/F-11/F-12. R-21 (intentional boundary) and R-17 (provenance gap) remain open. |

### 1.3 Porosity: 3 Independent Computations — §1.3

| Older report status | Current run status | Cross-reference |
|---|---|---|
| PARTIALLY FIXED — `or 0.35` fixed, but 3 computations not reconciled | Not investigated in this run | **STILL OPEN.** F-01/F-02 (zero/None handling) relate to this but are separate. R-05 through R-10 (porosity consumer dependency) remain open. |

### 1.4 Temporal Distribution Gap — §1.4

| Older report status | Current run status | Cross-reference |
|---|---|---|
| NEW FINDING — 320/512 states unclassified | Not investigated in this run | **STILL OPEN.** No current-run finding addresses temporal classification. |

### 1.5 `or 0.35` Fallback Bug — §1.5

| Older report status | Current run status | Cross-reference |
|---|---|---|
| FIXED — all 9 locations fixed, Hex 7/52 now preserve 0.0 | F-01/F-02 still OPEN | **CONFIRMED FIXED but INCOMPLETE.** The `or 0.35` fix is verified. However, F-01 (remaining `or 0.0875` at multi_layer_expand.py:235) and F-02 (None handling) are new findings from the current run that the older report did not identify. The older report's "FIXED" status applies only to the `or 0.35` pattern, not to all zero-preservation code paths. |

### 1.6 LFS Pointer Reversion — §1.6

| Older report status | Current run status | Cross-reference |
|---|---|---|
| FIXED — pointer reverted, working tree clean | Not investigated in this run | **STILL FIXED.** No regression. |

### 2.1 B1 — Auto-git-push (RESOLVED) — §2.1

| Status | FIXED ✅ | Not affected by current run. |

### 2.2 B2 — Single-hex winner (OPEN) — §2.2

| Status | OPEN | Not addressed by current run. |

### 2.3 B3 — Stale source feeding 3D backends (OPEN) — §2.3

| Status | OPEN | Not addressed by current run. R-02/R-06 relate. |

### 2.4 B4 — Random params in quantum expand (OPEN) — §2.4

| Status | OPEN | Not addressed by current run. |

### 2.5 B5 — Fabricated "100% Verified Parity" (RESOLVED) — §2.5

| Status | FIXED ✅ | Not affected by current run. |

### 2.6 B6 — Shap-E mutates canonical kit files (OPEN) — §2.6

| Status | OPEN | Not addressed by current run. |

### 2.7 B7 — Two divergent 3D coordinate systems (OPEN) — §2.7

| Status | OPEN | Not addressed by current run. |

### 2.8 B8 — Doc/code drift (RESOLVED) — §2.8

| Status | FIXED ✅ | Not affected by current run. |

### 2.9 B9 — Vortex formula split (OPEN) — §2.9

| Status | OPEN | Not addressed by current run. |

### 2.10 B10 — Fake placeholder meshes (OPEN) — §2.10

| Status | OPEN | Not addressed by current run. |

### 2.11 B11 — Synthetic ψ mislabeled (OPEN) — §2.11

| Status | OPEN | Not addressed by current run. |

### 2.12 B12 — Flat-50 band-aid (NOTE ONLY) — §2.12

| Status | NOTE ONLY | Not addressed by current run. |

### 3.1-3.5 External reverence gaps (OPEN) — §3

| Status | OPEN (all 5) | Not addressed by current run. |

### 4.1 PROVEN count discrepancy (CORRECTED) — §4.1

| Status | CORRECTED ✅ | Not affected by current run. |

### 4.2 coherence uses abs(old_dy) (OPEN — design decision) — §4.2

| Older report status | Current run status | Cross-reference |
|---|---|---|
| OPEN — design decision needed | Not investigated in this run | **STILL OPEN.** This is a formula design question (does sign matter for coherence?), not a scale mismatch. F-10/F-12 do not address it. R-14 (M3 scale mismatch) is separate from this design question. |

### 4.3 voiceWeight uses absolute terms (OPEN — design decision) — §4.3

| Status | OPEN | Design decision, not scale mismatch. Not addressed by current run. |

### 4.4 chaos uses abs(dy) (OPEN — design decision) — §4.4

| Status | OPEN | Design decision, not scale mismatch. Not addressed by current run. |

### 4.5 T10 not in build order (OPEN) — §4.5

| Status | OPEN | Not addressed by current run. |

### 4.6 Test-to-invariant mapping (OPEN) — §4.6

| Status | OPEN | Not addressed by current run. |

### 4.7 YAO_VOCABULARY expected column (OPEN) — §4.7

| Status | OPEN | Not addressed by current run. |

### 5.1-5.5 Formula design review (OPEN) — §5

| Status | OPEN (all 5) | Not addressed by current run. |

### 6.1 Hamiltonian (ANALYZED) — §6.1

| Older report status | Current run status | Cross-reference |
|---|---|---|
| ANALYZED — Candidate C recommended, not implemented | F-10 VALIDATED, F-12 VALIDATED | **CONFIRMED and EXTENDED.** The older report identified the Hamiltonian as a canonical Hamiltonian construction (Legendre transform) with scale/variable-meaning issues. The current run formally validated F-10 (scale incompatibility) and F-12 (clamp information loss). Candidate C remains unimplemented. The older report's analysis of `abs()` discarding sign is related to but distinct from F-10's scale mismatch. |

### 6.2 Porosity (ANALYZED) — §6.2

| Status | ANALYZED | Not addressed by current run. |

### 6.3 Jacobian (ANALYZED) — §6.3

| Status | ANALYZED | Not addressed by current run. |

### 6.4 Gaussian (FUNCTIONAL) — §6.4

| Status | FUNCTIONAL | Not addressed by current run. |

### 7.1 Candidate Analysis (NOT VALIDATED) — §7

| Older report status | Current run status | Cross-reference |
|---|---|---|
| Candidate C leading, 0 of 7 validation gates complete | Not investigated in this run | **STILL OPEN.** F-10/F-11/F-12 do not validate Candidate C. Candidate C remains untested. |

---

## 2. Traceability-matrix-audit-2026-10-27.md — Cross-reference

### 2.1 PROVEN count discrepancy (CORRECTED) — §1

| Status | CORRECTED ✅ | Not affected by current run. |

### 2.2 19 of 40 PROVEN entries are presence-only — §1.2

| Status | OPEN (recommendation) | Not addressed by current run. |

### 2.3 coherence uses abs(old_dy) (genuine non-compliance) — §4

| Older report status | Current run status | Cross-reference |
|---|---|---|
| OPEN — design decision needed | Not investigated | **STILL OPEN.** This is a formula design question. F-10 (scale mismatch) is separate from this sign-discarding design question. The traceability audit's finding that Hexagram 2 would get coherence = +0.6 with signed old_dy (vs 0.0 with abs) remains valid and unaddressed. |

### 2.4 voiceWeight uses absolute terms (non-compliance) — §4

| Status | OPEN | Not addressed by current run. |

### 2.5 chaos uses abs(dy) (not flagged) — §4

| Status | OPEN | Not addressed by current run. |

### 2.6 Test T10 missing from build order — §3

| Status | OPEN | Not addressed by current run. |

### 2.7 Test-to-invariant mapping missing — §3

| Status | OPEN | Not addressed by current run. |

---

## 3. Information-loss-remediation-register.md — Cross-reference

### R-entries confirmed by current run

| R-entry | Description | Current run cross-reference |
|---|---|---|
| R-14 | M3 Hamiltonian energy = 0.0 for all states | **CONFIRMED and EXTENDED by F-10/F-12.** F-10 established scale mismatch as root cause. F-12 established clamp as sole information-loss mechanism. F-11 established downstream propagation. The register's R-14 finding is now superseded by the more detailed F-10/F-11/F-12 chain. |
| R-15 | M3→M6 degenerate complex-amplitude | **CONFIRMED and EXTENDED by F-11.** F-11 established type 2 dependency (derived from M3, not independent). The register's R-15 finding is now superseded by F-11's more detailed dependency analysis. |
| R-11 | Viewer zero masking (`|| 0.75` fallback) | **STILL OPEN.** Not addressed by current run. JavaScript `||` operator treats 0 as falsy. |
| R-12 | Field-name collision: `hamiltonian_energy` | **STILL OPEN.** Not addressed by current run. Two different formulas produce same field name. |
| R-13 | Default intent "understand" for 989/991 equations | **STILL OPEN.** Not addressed by current run. |
| R-16 | 3D PLY mesh provenance unverified | **STILL OPEN.** Not addressed by current run. |
| R-17 | Ternary source lineage untraced | **STILL OPEN.** Not addressed by current run. |
| R-18 | Corpus evidence cardinality unvalidated | **STILL OPEN.** Not addressed by current run. |
| R-19 | Output differentiation unverified | **STILL OPEN.** Not addressed by current run. |
| R-20 | Personality-subset intent unverified | **STILL OPEN.** Not addressed by current run. |

### R-entries NOT affected by current run

| R-entry | Description | Status |
|---|---|---|
| R-01 | Missing `scripts/__init__.py` | OPEN (CRITICAL) |
| R-02 | Nonexistent `shotgun_expand_output.json` | OPEN (CRITICAL) |
| R-03 | Empty `text` in all 1,536 JSONL records | OPEN (HIGH) |
| R-04 | `intent.dominant_intent` = "understand" for 989/991 | OPEN (HIGH) |
| R-05 | `pre_slider.emotional_input` = 0 (placeholder) | OPEN (MEDIUM) |
| R-06 | `personality_subsets` None for 512 resolved | OPEN (MEDIUM) |
| R-07 | `ternary_slots` None for 512 resolved | OPEN (MEDIUM) |
| R-08 | `schauberger_parsing` None for 512 resolved | OPEN (MEDIUM) |
| R-09 | `projections` absent from resolved | OPEN (MEDIUM) |
| R-10 | `domain_routing_palette` absent from resolved | OPEN (MEDIUM) |
| R-21 through R-27 | Intentional boundaries | PRESERVED |

---

## 4. Remediation-verification-matrix.md — Cross-reference

### Entries 1-8 (all INCONCLUSIVE)

| Entry | Description | Current run cross-reference |
|---|---|---|
| Entry 1 | Zero-preservation fixes (explicit 0.0) | F-01/F-02 extend Entry 1 findings. `or 0.35` fix verified (13/13 PASS), but F-01 (remaining `or 0.0875`) and F-02 (None handling) are new. Entry 1 remains INCONCLUSIVE. |
| Entry 2 | Import path fixes | F-05/F-06/F-07/F-08 extend Entry 2 findings. 3/7 consumers functional, 4/7 not runnable. Entry 2 remains INCONCLUSIVE. |
| Entry 3 | Hamiltonian argument correction | F-09 (resolved), F-10 (VALIDATED), F-11 (VALIDATED), F-12 (VALIDATED). The argument fix (F-09) addressed q̇ degeneracy but did NOT resolve scale mismatch (F-10) or clamp (F-12). Entry 3 remains INCONCLUSIVE. |
| Entry 4 | Deterministic token ordering | Not investigated in current run. Remains INCONCLUSIVE. |
| Entry 5 | Pre-slider consensus removal | Not investigated in current run. Remains INCONCLUSIVE. |
| Entry 6 | Porosity None resolution | Not investigated in current run. Remains INCONCLUSIVE. |
| Entry 7 | README count updates | Not investigated in current run. Remains INCONCLUSIVE. |
| Entry 8 | Schauberger parsing emotional_input propagation | Not investigated in current run. Remains INCONCLUSIVE. |

---

## 4b. Vortex-Hamiltonian-Jacobian-Gaussian-Diagnostic — Cross-reference

### Section 1 Hamiltonian: Root Cause Confirmed

| Older report status | Current run status | Cross-reference |
|---|---|---|
| Root cause: scale mismatch — pq_dot 0-1 vs L 0-6 | F-10 VALIDATED | CONFIRMED and EXTENDED. Older diagnostic correctly identified scale mismatch (pq_dot 0.009543 vs L 2.500000 for Hex 1) and downstream impact. Current run formalized as F-10 (semantic/scale incompatibility) and F-12 (clamp as sole information-loss mechanism). Proposed fix (normalize L to /4.0) remains unimplemented. |
| Downstream: rotation=0, scale=0.75, imag=0 | F-11 VALIDATED | CONFIRMED. Diagnostic's downstream impact table matches F-11's findings exactly. F-11 extended to identify multiplicative dependency and empty line_balance consumer integration defect. |
| Proposed fix: normalize L to /4.0 | Not authorized | STILL OPEN. No formula changes authorized. Candidate C remains untested. |

### Section 2 Vortex: Porosity Scale Mismatch + or Bug

| Older report status | Current run status | Cross-reference |
|---|---|---|
| or 0.35 bug: Hex 15/20 got 0.35 instead of 0.0 | F-01/F-02 OPEN | PARTIALLY CONFIRMED. Bug is real but diagnostic had wrong hex numbers — actual is Hex 7 and Hex 52, not Hex 15/20. or 0.35 fix applied and verified (13/13 PASS). F-01 (remaining or 0.0875) and F-02 (None handling) are new findings diagnostic did not identify. |
| Porosity scale mismatch: 0-4 int treated as 0-1 float | Not investigated | STILL OPEN. Vortex formula 0.5 + porosity * 0.5 maxes out at porosity=4. Not addressed by current run. |

### Section 3 Jacobian: Verification Only, No Production Consumer

| Status | OPEN | Not addressed by current run. Interface specification still required. |

### Section 4 Gaussian: Functional, Needs Validation

| Status | FUNCTIONAL (needs validation) | Not addressed by current run. |

### Section 5 Porosity: Three Independent Sources, No Reconciliation

| Older report status | Current run status | Cross-reference |
|---|---|---|
| 3 independent sources: injection site (0-4), kit QWP (0.15-0.71), emotional engine (0-1) | Not investigated | STILL OPEN. F-01/F-02 relate to porosity handling but do not reconcile the three sources. R-05 through R-10 remain open. |

### Section 6 Traceability Matrix Corrections

| Finding | Status | Cross-reference |
|---|---|---|
| 19 PROVEN entries presence-only | CORRECTED | Not affected by current run. |
| T10 missing from build order | OPEN | Not addressed by current run. |
| Test-to-invariant mapping incomplete | OPEN | Not addressed by current run. |
| coherence/voiceWeight/chaos design questions | OPEN | Not addressed by current run. |
| YAO_VOCABULARY expected column | OPEN | Not addressed by current run. |

---

## 5. Summary: What this run confirmed, extended, or left open

### Confirmed by this run (older findings now validated)

| Older finding | Older status | Current run result |
|---|---|---|
| Audit-drift §1.1: Hamiltonian = 0.0 | FIXED (partially) | F-10 VALIDATED: scale mismatch root cause identified |
| Audit-drift §1.1: H=0.0 persists | Not resolved | F-12 VALIDATED: clamp is sole information-loss mechanism |
| R-14: M3 Hamiltonian = 0.0 | Verified | F-10 VALIDATED: semantic/scale incompatibility |
| R-15: M3→M6 degenerate amplitude | Verified | F-11 VALIDATED: type 2 dependency, not independent |
| Audit-drift §6.1: Hamiltonian ANALYZED | Candidate C recommended | F-10 VALIDATED extends this: scale mismatch is root cause, not just "variable meanings" |
| Audit-drift §1.5: `or 0.35` FIXED | Fixed | Confirmed fixed; F-01/F-02 extend with remaining bugs |
| Traceability §4.2: coherence uses abs(old_dy) | OPEN design decision | Not addressed; remains open and separate from F-10 |

### Left open (not addressed by this run)

| Finding | Source | Status |
|---|---|---|
| Ternary 729/5832 not in pipeline | Audit-drift §1.2 | OPEN |
| Porosity 3 independent computations | Audit-drift §1.3 | OPEN (F-01/F-02 relate but separate) |
| Temporal distribution gap (320/512) | Audit-drift §1.4 | OPEN |
| B2-B12 (10 items) | Audit-drift §2 | OPEN |
| External reverence gaps (5 items) | Audit-drift §3 | OPEN |
| coherence/voiceWeight/chaos design review (3 items) | Audit-drift §4, §5 | OPEN |
| Candidate C validation (0/7 gates) | Audit-drift §7 | OPEN |
| R-01 through R-13 (13 items) | Remediation register | OPEN |
| R-16 through R-20 (5 items) | Remediation register | OPEN |
| R-21 through R-27 (7 intentional boundaries) | Remediation register | PRESERVED |
| Entries 1-8 verification matrix | Remediation matrix | ALL INCONCLUSIVE |

### Key insight

The current run (F-10 → F-12) established the **mathematical validation chain** for the M3 Hamiltonian zero-output:
- F-10: Why H is always negative (scale mismatch)
- F-12: Why H is always 0.0 (one-sided clamp)
- F-11: Why downstream imag is 0.0 (multiplicative dependency)

This is a **mathematical validation** result, not a remediation result. The older audit reports identified H=0.0 as a symptom and recommended Candidate C as a fix. The current run established the root cause and mechanism, but did not implement any fix. The older reports' recommendations (Candidate C, normalization, field contracts) remain unimplemented and unvalidated.

The F-10 → F-12 chain does NOT address:
- Formula design questions (coherence/voiceWeight/chaos abs issues)
- Ternary integration gaps
- Porosity reconciliation
- Consumer execution failures (F-01/F-02/F-05-F-08)
- Candidate C validation
- Any remediation or source changes

### Disposition

- **Mathematical validation (F-10/F-11/F-12):** COMPLETE at reported evidence boundary
- **Remediation:** NOT STARTED
- **Gate 2:** OPEN
- **Open findings:** F-01, F-02, F-05-F-08, plus 38 still-broken items from audit-drift report
- **No source modifications authorized**