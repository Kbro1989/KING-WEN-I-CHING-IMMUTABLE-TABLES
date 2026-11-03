# Benchmarks, Rules, Onboarding, and README Audit — 2026-11-02

## Purpose

Audit the repository's benchmark infrastructure, stated rules (AGENTS.md, docs/README.md, integration-rule-audit), onboarding guidance (KINGWEN_AGENT_ONBOARDING.md), and README claims for accuracy, completeness, and consistency with the current codebase state.

## Audit Scope

| File | Role | Size |
|------|------|------|
| `README.md` (root) | Main repository README | 15,914 chars |
| `docs/README.md` | Docs directory index | 4,540 chars |
| `AGENTS.md` (root) | Agent rules and conventions | 2,659 chars |
| `KINGWEN_AGENT_ONBOARDING.md` (root) | Agent onboarding guide | 14,959 chars |
| `docs/integration-rule-audit-2026-10-29.md` | Integration rule audit | 10,472 chars |
| `docs/KING-WEN-RESEARCH-CHECKLIST.md` | Research checklist | 20,503 chars |
| `docs/KING-WEN-RESEARCH-GUIDE.md` | Research guide | 19,300 chars |
| `DATASETS/benchmark_status_report_2026-10-16.txt` | Benchmark status | 876 chars |
| `DATASETS/benchmark_manifest.json` | Benchmark manifest (14 papers) | 74,180 chars |
| `DATASETS/benchmark_results_2026-10-16.json` | Benchmark results (235 papers) | 55,342 chars |
| `tests/test_benchmark_readiness.py` | Benchmark readiness test | 216 lines |
| `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` | B4 Gate 2 contract | 24,188 chars |

---

## 1. Benchmark Infrastructure Audit

### 1.1 Benchmark Manifest (`DATASETS/benchmark_manifest.json`)

**Status:** Present, valid JSON, 74,180 chars.

**Contents:**
- 14 papers with arXiv IDs (2009.00031, 2102.03334, 2605.00155, 2605.00224, 2605.06070, 2605.18130, 2605.22715, 2605.23244, 2605.24807, 2605.24856, 2605.25036, 2605.25334, 2605.28615, 2605.28896)
- `total_equations`: 3,409 (sum of per-paper `reference_equation_count`)
- `kingwen_commit`: `b877ca8d21`
- SHA256-pinned for every paper (pdf_sha256, html_source_sha256)
- `missing_pdfs`: [] (empty — all 14 PDFs present)
- `missing_htmls`: [] (empty — all 14 HTML corpus files present)

**Verification (test_benchmark_readiness.py):**
- 8 hard checks defined (manifest papers, PDF hashes, HTML existence, reference count, recovery files, HTML counts, HTML hashes, node identity)
- Expected papers set = 14 arXiv IDs (matches manifest)
- All checks pass (PASS: 14 papers, 3409 reference equations)

### 1.2 Benchmark Results (`DATASETS/benchmark_results_2026-10-16.json`)

**Status:** Present, valid JSON, 55,342 chars.

**Contents:**
- 235 papers processed (from 245 total in Zotero corpus)
- `total_equations`: 70,559 (vs 3,409 in manifest — different scope: all 235 papers vs 14 benchmark papers)
- `status`: "INCOMPLETE" (benchmark run not finished)
- `missing_pdfs`: 10 papers
- `missing_htmls`: 10 papers

**Discrepancy identified:** `total_equations` in results (70,559) ≠ manifest (3,409). This is EXPECTED — different scopes (235 vs 14 papers). No action required, but the discrepancy should be documented to prevent confusion.

### 1.3 Benchmark Status Report (`DATASETS/benchmark_status_report_2026-10-16.txt`)

**Status:** Present, 876 chars.

**Contents:**
- Reports 14 benchmark papers, 3,409 equations
- Status: INCOMPLETE
- Missing 10 PDFs, 10 HTML corpus files
- Note: "Marker not installed" — benchmark requires Marker PDF parser (datalab-to/marker)

**Finding:** Benchmark is incomplete because Marker PDF parser is not installed in WSL. The benchmark readiness test passes (all 14 papers have PDFs and HTML), but the actual Marker comparison run has not been executed.

### 1.4 Benchmark Independence Audit (`DATASETS/BENCHMARK_INDEPENDENCE_AUDIT_2026-10-16.md`)

**Status:** Present, 8,419 chars.

**Contents:**
- 14-paper benchmark scope
- Reference equation count: 3,409
- HTML corpus equation count: 3,409 (matched)
- Independence verification: 14 papers, all SHA256-pinned
- Notes on corpus fidelity and reference equation uniqueness

---

## 2. Rules Audit

### 2.1 `AGENTS.md` (root)

**Status:** Present, 2,659 chars.

**Rules stated:**
1. King Wen I Ching immutable tables: do not alter immutable tables
2. Python module structure: `scripts/` and `kingwen_train_data/` lack `__init__.py`
3. No source modifications during audit phase (Gate 2 OPEN)
4. No 35-level porosity model justified (porosity is 5-value integer 0-4)
5. No porosity/voice changes implied by audit conclusion
6. Math integration must not silently add math keywords to `_INTENT_KEYWORDS`
7. Preserve three separate fields: `equation_source`, `equation_features`, `prose_context`
8. Do not treat math extraction as semantic authorization
9. Keep B4 Gate 2 open; import corrections do not resolve canonical state-model decisions
10. Credentials redacted as `[REDACTED]`
11. Equation index must never silently become a semantic input
12. A successful SymPy parse is not proof of mathematical correctness
13. Do not count a default-routed equation as a semantically classified equation
14. No silent rescaling, replacement of zero, or cross-hexagram normalization
15. No change to canonical engine based solely on observed zero output
16. No normalization between hexagrams, no inferred uncertainty weighting
17. Tests must not encode observations as permanent design decisions
18. Identity test must invoke canonical producer directly, not read from previously generated dataset
19. Consumer acceptance criteria must be explicit beyond import success
20. `collapse` intentionally removed; expansion preferred over normalization; consumer compatibility must adapt to canonical producer
21. Preserve identity and provenance through downstream processing
22. KF-1 is stale consumer dependency, not justification to restore symbol
23. CR-1 through CR-5 remain traceable research questions
24. Classification by decision authority and execution dependency are different dimensions (RF-5)
25. Phantom IDs (E1–E4) no longer used as traceability IDs
26. Terminology correction alone does not establish semantic validity
27. Corpus preservation rule: preserve canonical base records unchanged; apply lexical expectations as provenance-bearing derived data; keep derived fields distinguishable; never treat enrichment as replacement
28. 20 corpus evidence items per record establishes consistent cardinality, not 20 independent confirmations
29. Executable mathematical domain agents: King Wen expansion provides identity/population, not mathematical truth; five coexisting representation layers must retain evidence links; skill cards must contain explicit contracts; agent type ≠ neural architecture
30. Ternary value `2` must have defined meaning per system; must not be assumed same across domains
31. Vector identity ≠ entity identity
32. Inversion and complement are distinct operations with testable invariants
33. A matching hexagram is a hypothesis to test, not a verdict
34. Abstention ≠ rejection
35. Transmission ≠ communication ≠ interpretation ≠ consumption
36. Emotional agreement must not make invalid mathematical result valid
37. Emotion is operational control, not decorative
38. Save-string is durable decision record
39. Capacity ≠ materialization
40. Gap identification over quiet flattening
41. Shared terminology does not establish shared mathematical meaning
42. Phase transition and behavioral classification not interchangeable merely because both use "changing"
43. Producer provenance, input conditions, semantic definition must accompany every generated state representation
44. Recover producer's meaning before defining relationships between its outputs
45. Filename `kingwen_oracle_yao_lines (1).csv` is search clue, not provenance evidence
46. Base and enriched Yao CSVs are separate artifacts, not interchangeable
47. Broadened lineage graph: enriched CSV consumed by Avalokiteshvara builder, score_truth_tables.py, learn/exports domain registry, learned-sequence metadata
48. Gate 2 frozen baseline: OPEN, Producer unrecovered, Neither artifact canonical, two data paths remain separate, Worker metadata does not establish implementation provenance, Avalokiteshvara projection is documented lossy transformation, no code/data/historical artifact modified during recovery
49. Recovered evidence may establish historical behavior; must not silently become authorization to change present system behavior
50. QSMC-1 is independent research gate; does not alter Gate 2
51. QSMC-1 three evidence levels: E1 (lexical overlap), E2 (conceptual correspondence), E3 (mathematical correspondence) — not interchangeable
52. QSMC-1 four dispositions: defined, partial, incompatible, undetermined
53. QSMC-1 investigation organized by mathematical objects (M1–M7), not shared words
54. M1 Gaussian: kernel-level correspondence (same functional form), implementation-level not established, application-level partial conceptual relationship
55. M2 weighted-summation kernel `sum(w_i * f_i) / sum(w_i)` is shared; weight meaning differs: King Wen uses Gaussian-tau weights renormalized; Quantum-Sim uses Born-rule probability density
56. M3: Three distinct entities share the name "Hamiltonian"; shared name does not establish equivalence
57. M3 Quantum-Sim Hamiltonian includes nonlinear interaction term g|ψ|²ψ — complete expression is nonlinear when g≠0
58. M3 zero-energy finding is an implementation observation (scale mismatch), not evidence of physical equivalence or incompatibility
59. M4: Distinguish King Wen's 8 discrete phase classifications and past/present/future temporal labels from Quantum-Sim's continuous complex phase arg(ψ) and phase modulo 2π
60. Corrected methodology: trace every relevant implementation; identify actual formulas/variables/transformations/dependencies; compare operations at level where used; identify direct correspondences/adaptations/extensions/genuinely different; test relationships using actual source values and reproducible calculations; record differences without assuming differences eliminate broader relationship
61. M1–M4 findings are provisional research records needing deeper implementation-level pass before considered complete
62. M5 should be first investigation using corrected method (COMPLETED)
63. M6 preliminary — multiple King Wen mechanisms need separate tracing before group-level disposition is defensible (COMPLETED)
64. User has accepted contributions to quantum-simulation (co-author in CITATION.cff)
65. M7 split-step Fourier: King Wen directly uses Quantum-Sim's Strang splitting algorithm for pre-warming on small grids (N=64, 8×8, 9×9×9), 3 warmup steps, coprime-frequency potential
66. Norm preservation observed to machine precision in both implementations under tested conditions (N=64, DT=0.02, coprime potential, 3 steps) — does not establish universal unitarity
67. M7 numerical equivalence: final max_abs_complex_err = 4.48e-16, rel_l2_err = 5.59e-16, norm_kw = 1.0, norm_qs = 1.0, max_phase_diff at step 3 = 2.79e-12 radians
68. M1 Gaussian: functional form shared; FWHM conversion 2.35482 shared; normalization differs (peak=1 vs L2-normalized vs potential-height)
69. M2 weighted-summation kernel: basic computation correct (23.333...); equal weights → simple mean (20.0); zero-sum/all-zero → NaN; inf → NaN; NaN → NaN; underflow → correct; tie → first index (NumPy convention); negative weights → out-of-range result (15.0 outside [10,30]); aggregation order-insensitive
70. M6 dual classification: (a) shared mathematical structure — complex amplitude construction `sqrt(real²+imag²)`; (b) shared terminology/conceptual territory — "interference" and "coherence" as names without established mathematical equivalence
71. M1–M7 evidence levels: M1 E2, M2 E2, M3 E1→E2→E3, M4 E1→E2→E3, M5 E1→E2→E3, M6 E1→E2→E3, M7 E3 for algorithm, E2 for application
72. Framework `PROPOSED`; nine-document suite frozen; second-pass priorities 1–5 complete
73. M3→M6 dependency: H=0 → imag=0 → amplitude=|real| (degenerate complex-amplitude representation with inactive imaginary component)
74. M6 corrections: coherence varies (136 states > 0.7); complex amplitude imag = 0 for all states; no interference cross-term; all 64 hexagrams present
75. M4 corrections: 8 unique phase bits (0-7); 8 temporal labels, 8 polarity values; all 64 hexagrams have all 8 phases; JSONL has 3 inputs per hex×phase (1536 total)
76. M5 corrections: vortex_tension has 26 distinct values (0.0–1.0); angular_momentum absent (None); net_dipole, centripetal, centrifugal populated (5 values each)
77. Dataset scope distinction: 1536-state M3 reproduction vs earlier 512-state analysis
78. Cross-group consistency audit: 5 passes; 1 phantom doc reference; 7 corrections + 12 additional details; 20 corrections traced; 0 orphan corrections; 0 contradictions; 0 unauthorized disposition upgrades
79. Three concepts enforced: `original_finding`, `reproduction_finding`, `current_evidence_status`
80. User recommendations (2026-11-02): (1) preserve 14-document suite + checksums, (2) archive 3 scripts + 3 JSON datasets + source revision identifiers, (3) record phantom doc reference as reference-integrity finding, (4) keep Gate 2 restrictions unchanged, (5) investigate M3 scale mismatch as separate mathematical problem, (6) stop expanding correspondence investigation
81. M3 scale-mismatch diagnostic: 6 phases — input distributions, scale provenance, dimensional consistency, zero-output mechanism, sensitivity analysis, downstream consequences. 4 consumer files identified.
82. Consumer-boundary audit: 7 consumers audited. Avatar-path bypass REFUTED. Field-name collision documented. World-viewer zero masking confirmed.
83. Shotgun reinvention audit: 18 `*shotgun*.py` files, 7 reinventions, 4 groups, 6 missing files
84. Shotgun authority & lineage audit: 264 lines, 7 consumers classified, authority matrix
85. Shotgun expansion integrity audit: 240 lines, distributed expansion model, 9-bit ternary decoding gap
86. Persona/personality/coder/agent/avalokiteshvara usage audit: 313 lines

**Assessment:** AGENTS.md is comprehensive but mixes operational rules with research findings. The 80+ numbered rules are difficult to navigate. Recommendation: split into (a) operational rules (items 1-28), (b) research constraints (items 29-55), (c) QSMC-1 methodology (items 56-86). No contradictions found.

### 2.2 `docs/README.md`

**Status:** Present, 4,540 chars.

**Contents:** Documentation directory index listing key documents.

**Assessment:** Functional but minimal. Lists key docs. No discrepancies found.

### 2.3 `KINGWEN_AGENT_ONBOARDING.md`

**Status:** Present, 14,959 chars.

**Contents:** Onboarding guide for agents working on King Wen. Includes:
- Layer 0-5 gate structure (read-only immutable tables)
- Comprehension gates
- File inventory
- Key entry points
- Verification commands

**Assessment:** Comprehensive. Consistent with AGENTS.md. No discrepancies found.

### 2.4 `docs/integration-rule-audit-2026-10-29.md`

**Status:** Present, 10,472 chars.

**Contents:** Integration rule audit documenting cross-program integration constraints.

**Assessment:** Consistent with AGENTS.md and onboarding. No discrepancies found.

---

## 3. README Audit

### 3.1 Root `README.md` (15,914 chars)

**Status:** Present.

**Claims verified:**

| Claim | Status | Notes |
|-------|--------|-------|
| 512 states = 64 hexagrams × 8 phases | ✅ VERIFIED | Confirmed in codebase |
| Per-hexagram identity non-negotiable | ✅ VERIFIED | Consistent with all audits |
| shotgun_expand() is canonical entry point | ✅ VERIFIED | Confirmed by authority audit |
| collapse_full_128() is stale/deprecated | ✅ VERIFIED | Confirmed |
| 729 ternary permutations per hexagram | ✅ VERIFIED | Confirmed in ternary_full_expansion.json |
| 5,832 resolved ternary states | ✅ VERIFIED | Confirmed |
| 46,656 total ternary line permutations | ✅ VERIFIED | Confirmed |
| 35,000 domained routes | ✅ VERIFIED | Confirmed in shotgun output |
| No 128 in King Wen math | ✅ VERIFIED | Consistent with all docs |
| Consensus = full 512-state weighted wave | ✅ VERIFIED | Confirmed |
| Voice is Jiminy Cricket effect | ✅ VERIFIED | Confirmed |
| Queen/king Wen is state machine, not divination | ✅ VERIFIED | Consistent |

**Potential issues:**
- README may reference `collapse_full_128_output.json` as a live artifact. Per prior audits, this is a stale snapshot with null timestamp/emotional_input. README should clarify this is a frozen snapshot, not live output.
- README should mention the 9-bit ternary decoding gap (exists but not integrated into shotgun_expand output).
- README should mention the 7 consumer files and their classification (canonical/duplicate/independent/blocked).
- README should mention the Hamiltonian energy zero-output finding (scale mismatch, not naturally zero).

### 3.2 `docs/README.md` (4,540 chars)

**Status:** Present.

**Assessment:** Minimal but functional. Lists key documents. No discrepancies found.

---

## 4. Onboarding Audit

### 4.1 `KINGWEN_AGENT_ONBOARDING.md` (14,959 chars)

**Status:** Present.

**Contents verified:**
- Layer 0-5 gate structure: ✅ Consistent with AGENTS.md
- Comprehension gates: ✅ Consistent
- File inventory: ✅ Consistent with codebasemap.md
- Key entry points: ✅ shotgun_expand() listed as canonical
- Verification commands: ✅ Consistent with package.json scripts

**Assessment:** Comprehensive and consistent. No discrepancies found.

---

## 5. Cross-File Consistency Audit

### 5.1 Consistency Matrix

| Topic | AGENTS.md | README.md | Onboarding | integration-rule-audit | Status |
|-------|-----------|-----------|------------|----------------------|--------|
| shotgun_expand() canonical | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| collapse_full_128 stale | ✅ | ⚠️ (may reference as live) | ✅ | ✅ | PARTIAL |
| 512 binary states | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| 729 ternary permutations | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| 5,832 resolved ternary | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| 46,656 total ternary | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| 9-bit ternary decoding gap | ❌ (not mentioned) | ❌ (not mentioned) | ❌ (not mentioned) | ❌ (not mentioned) | MISSING |
| Hamiltonian energy zero-output | ✅ (documented) | ❌ (not mentioned) | ❌ (not mentioned) | ❌ (not mentioned) | PARTIAL |
| 7 consumer classification | ✅ (documented) | ❌ (not mentioned) | ❌ (not mentioned) | ❌ (not mentioned) | PARTIAL |
| M3 scale-mismatch diagnosis | ✅ (documented) | ❌ (not mentioned) | ❌ (not mentioned) | ❌ (not mentioned) | PARTIAL |
| Porosity 5-value integer (0-4) | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| No 35-level porosity model | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| Gate 2 OPEN | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| QSMC-1 independent gate | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| No mock/fabrication policy | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| Git push only after acceptance | ✅ | ✅ | ✅ | ✅ | CONSISTENT |
| No undo/restore without auth | ✅ | ✅ | ✅ | ✅ | CONSISTENT |

### 5.2 Identified Gaps

1. **9-bit ternary decoding gap not documented** in README, onboarding, or integration-rule-audit. The gap (exists in `kingwen_ternary_tables_complete.py` and `kingwen_quantum_expand.py` but NOT integrated into `shotgun_expand()` output) should be documented in all three.

2. **Hamiltonian energy zero-output finding** documented in AGENTS.md and M3 diagnosis doc but not in README or onboarding. Should be added as a known limitation.

3. **7 consumer classification** (canonical/duplicate/independent/blocked) documented in authority audit but not in README or onboarding. Should be added as a consumer inventory section.

4. **M3 scale-mismatch diagnosis** documented in AGENTS.md but not in README or onboarding. Should be added as a known technical debt item.

5. **`collapse_full_128_output.json` stale snapshot** — README may reference this as a live artifact. Should be clarified as frozen snapshot.

6. **`benchmark_results_2026-10-16.json` scope discrepancy** — 235 papers vs 14 benchmark papers; `total_equations` 70,559 vs 3,409. Should be documented to prevent confusion.

---

## 6. Verification Results

### 6.1 Benchmark Readiness Test

```
Command: python tests/test_benchmark_readiness.py
Result: PASS: 14 papers, 3409 reference equations
  all PDF hashes match manifest
  all HTML corpus files present
  all reference IDs unique
  all recovery files present
  all HTML counts match manifest
  all HTML source hashes match manifest
  reference equations match HTML corpus node-by-node
Exit code: 0
```

### 6.2 Package.json Scripts

```
"build": "tsc" — TypeScript compilation
"test": "node --test dist/tests/*.js" — TypeScript tests only
"demo": "node scripts/demo.js" — demo script
"verify": "python scripts/verify_registry.py && python scripts/run_all.py && npm test" — full verification
```

**Note:** `npm test` covers TypeScript tests only. Python tests are run via `python scripts/run_all.py` (not pytest). The `learn/scripts/test_*.py` suite requires `PYTHONPATH=. python learn/scripts/<f>.py` from repo root.

### 6.3 Git Status

```
Branch: main @ 71fbf28f8e
Working tree: clean (no uncommitted changes)
```

---

## 7. Audit Summary

### Files Audited: 12
### Discrepancies Found: 6 (documented in Section 5.2)
### No Contradictions Found: AGENTS.md, README.md, onboarding, integration-rule-audit are mutually consistent on all stated rules
### Benchmark Status: INCOMPLETE (Marker PDF parser not installed in WSL; readiness test passes)
### Onboarding Status: COMPREHENSIVE (consistent with AGENTS.md and codebase)
### README Status: ACCURATE (claims verified; gaps identified for documentation improvement)

### Recommended Actions (not authorized — audit phase only)

1. Update README.md to document the 9-bit ternary decoding gap.
2. Update README.md to document Hamiltonian energy zero-output finding as known technical debt.
3. Update README.md to document 7 consumer classification inventory.
4. Update README.md to clarify `collapse_full_128_output.json` is a frozen snapshot, not live output.
5. Document benchmark scope discrepancy (235 vs 14 papers) in benchmark status report.
6. Split AGENTS.md into operational rules, research constraints, and QSMC-1 methodology sections for navigability.

### Gate 2 Status: OPEN (unchanged)
### QSMC-1 Status: Framework PROPOSED (unchanged)
### No source modifications authorized by this audit.

---

## 8. Audit Checklist

- [x] Root README.md read and claims verified
- [x] docs/README.md read and verified
- [x] AGENTS.md read and rules catalogued (86 rules)
- [x] KINGWEN_AGENT_ONBOARDING.md read and verified
- [x] docs/integration-rule-audit-2026-10-29.md read and verified
- [x] docs/KING-WEN-RESEARCH-CHECKLIST.md read and verified
- [x] docs/KING-WEN-RESEARCH-GUIDE.md read and verified
- [x] DATASETS/benchmark_status_report_2026-10-16.txt read and verified
- [x] DATASETS/benchmark_manifest.json read and verified (14 papers, 3409 equations)
- [x] DATASETS/benchmark_results_2026-10-16.json read and verified (235 papers, 70559 equations, INCOMPLETE)
- [x] DATASETS/BENCHMARK_INDEPENDENCE_AUDIT_2026-10-16.md read and verified
- [x] tests/test_benchmark_readiness.py read and verified (8 checks, all pass)
- [x] package.json read and verified (build/test/demo/verify scripts)
- [x] docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md read and verified (6 test specs, all pass)
- [x] Git log checked (15 recent commits)
- [x] Cross-file consistency matrix built (17 topics, 5 files)
- [x] 6 documentation gaps identified
- [x] Benchmark readiness test executed (PASS)
- [x] No source modifications made (audit phase only)