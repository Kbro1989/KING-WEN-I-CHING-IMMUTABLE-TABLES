# Cross-Document Finding Authority Map

**Date:** 2026-11-03
**Scope:** Documentation governance and traceability only — read-only artifact.
**No source modifications, commits, remediation acceptance, or gate-status changes implied.**

---

## 1. Purpose and Authority Rules

### 1.1 Purpose

This document assigns exactly one canonical identity and owner to every substantive finding across the King Wen math-pipeline documentation set. It prevents the failure mode where five documents independently describe the same defect with slightly different wording, status, and implied authority.

### 1.2 Authority Rules

1. **Canonical ownership ≠ exclusive evidence ownership.** The canonical owner is where the finding is *governed* — where its status, scope, and unresolved questions are authoritatively recorded. Other documents may contain valid measurements, historical observations, or downstream consequences without becoming competing authorities.
2. **Supporting references are links, not duplications.** A document that discusses a finding must reference the canonical owner, not restate the finding as if it originated there.
3. **Historical findings are preserved.** A finding that was later superseded or reclassified remains visible in its original document. The canonical owner records the current interpretation and the supersession chain.
4. **Evidence status ≠ implementation status ≠ acceptance status.** These three dimensions must remain separate. A finding can have evidence collected, implementation unchanged, and acceptance not established — all simultaneously.
5. **Gate contexts are independent.** QSMC-1 Gate 2, B4 Gate 2, and the Lua migration prerequisite are three separate gate systems. Their statuses must not be consolidated.
6. **No unsupported relationship is promoted to a dependency.** A finding's cross-references must not imply that one finding depends on another unless that dependency is explicitly documented and verified.
7. **No finding is silently deleted, merged, or reclassified.** If a finding is superseded, the supersession is explicitly recorded with both the original and new finding IDs.

---

## 2. Canonical Finding Registry

Each finding has one stable ID (CF-NNN), one canonical owner, and a status.

### CF-001: Hamiltonian formula returns 0.0 for all 512 states

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (`docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md`) |
| **Status** | VALIDATED (F-10, F-11, F-12) — scale mismatch root cause, one-sided clamp sole information-loss mechanism |
| **Evidence dimensions** | Implementation: `_hamiltonian_energy()` in `emotional_engine.py` lines 408-455. Measurement: 727 distinct raw H values, all negative (-5.09 to -0.56), clamped to 0.0. Provenance: present since commit `ea89a9cf2d`, coefficients carried V1→V2 without scale adjustment. Downstream: all avatar animations zeroed (rotation, scale, phase). |
| **Cross-references** | `vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §1 (earlier diagnostic), `traceability-matrix-2026-10-27.md` 3.1.9, `pipeline-gap-analysis-2026-10-27.md` (R-14), `audit-drift-report-2026-10-27.md` |
| **Unresolved** | Origin of coefficients 0.5/0.3/0.2; whether normalization was intended; sign convention; model classification (physical/heuristic/analogy/custom); Legendre transform claim; field-name collision (M3 vs JKD) |

### CF-002: Hamiltonian coefficients have no documented origin

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (§3.1, §8.3, §12.3) |
| **Status** | UNRESOLVED — no derivation found in code, docs, or git history |
| **Evidence dimensions** | Implementation: hardcoded in `emotional_engine.py` lines 450-452. Provenance: present in V1 (ratios) and V2 (raw counts) without adjustment. Wiki corpus search: no Hamiltonian-related entry contains 0.5, 0.3, or 0.2. QuantumLab search: no matching coefficients. |
| **Cross-references** | `docs/hamiltonian-equation-comparison-2026-10-27.md`, `docs/formula-design-review-2026-10-27.md`, `docs/audit-drift-report-2026-10-27.md` |
| **Unresolved** | Origin and intent of 0.5, 0.3, 0.2. Whether sum-to-1.0 is intentional (convex combination) or coincidental. |

### CF-003: Hamiltonian formula evolution V1 → V2

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (§2.2, §11.2) |
| **Status** | SOURCE-ESTABLISHED |
| **Evidence dimensions** | V1 (commit `780d9c4bfe`): ratios (0-1 scale) + phase_shift + 0.5/0.3/0.2 coefficients. V2 (commit `6239ba9bd7`): raw counts (0-6 scale) + resolved-expanded + same coefficients. Coefficients were NOT adjusted for the scale change — root cause of scale incompatibility. |
| **Cross-references** | `vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §1 (earlier, less precise), `math-term-usage-analysis-2026-10-27.md` |
| **Unresolved** | Whether the scale change was intentional or accidental. Whether coefficients should have been adjusted. |

### CF-004: October 27 document describes a formula that never existed in source code

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (§11) |
| **Status** | SOURCE-ESTABLISHED — documentation-integrity finding, not mathematical finding |
| **Evidence dimensions** | The October 27 document's formula (4 differentials, equal weights, /6.0) appears in exactly 2 files: `hamiltonian-equation-comparison-2026-10-27.md` and `vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md`. It does not appear in any source code file, test file, or data file. All consumers use the actual V2 implementation. |
| **Cross-references** | `traceability-matrix-2026-10-27.md` §11; `pipeline-gap-analysis-2026-10-27.md` |
| **Unresolved** | Whether the October 27 formula represents an intended future design, a misunderstood current implementation, or a theoretical ideal. |

### CF-005: QuantumLab and wiki math corpus ruled out as Hamiltonian sources

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (§14, §15) |
| **Status** | SOURCE-ESTABLISHED — both candidate sources investigated and excluded |
| **Evidence dimensions** | QuantumLab: Hamiltonian math added by rasidi3112 after user's infrastructure contributions ended; fundamentally different formula structure (split-step Fourier vs. pq_dot - lagrangian). Wiki corpus: 139 entries, 3 Hamiltonian-related; standard theoretical vocabulary only; no coefficients 0.5/0.3/0.2 in Hamiltonian context; no pq_dot/lagrangian/emotional vector structure. |
| **Cross-references** | `math-term-usage-analysis-2026-10-27.md` (term provenance) |
| **Unresolved** | The "parsed wiki sources" reference in `emotional_engine.py:392` remains unverified. No traceable reference to original source found. |

### CF-006: Occurrence identity contract

| Attribute | Value |
|---|---|
| **Canonical owner** | Math-pipeline evidence matrix / occurrence-accounting contract (`scripts/math_occurrence_accounting.py`) |
| **Status** | SOURCE-ESTABLISHED — SHA-256 over paper_id/version/locator/index, no LaTeX in identity key |
| **Evidence dimensions** | Implementation: `OccurrenceLedger` in `math_occurrence_accounting.py` with 12 tests (`test_occurrence_accounting.py`). Principle: occurrence identity ≠ mathematical expression identity ≠ parsed AST identity ≠ reconstructed expression identity ≠ solver-result identity. 3,409 occurrences in 14-paper benchmark; 72,478 in HTML corpus. |
| **Cross-references** | `traceability-matrix-2026-10-27.md` §5.2; `room-5-typed-integral-ir-2026-10-08.md` (occurrence conservation) |
| **Unresolved** | Whether occurrence identity is preserved across all extraction stages end-to-end. Multiset conservation tests not yet written. |

### CF-007: Measurement-layer defects (5 found)

| Attribute | Value |
|---|---|
| **Canonical owner** | Typed Integral IR / measurement diagnostic evidence (`docs/room-5-typed-integral-ir-2026-10-08.md`) |
| **Status** | SOURCE-ESTABLISHED — 5 defects identified, each needs individual impact mapping |
| **Evidence dimensions** | Defects: (1) dropped corpus field (preferred code path never ran), (2) glyph-vs-transliteration checker (reported phantom failures), (3) `\in`/`\infty` prefix match (18 phantom findings), (4) subscript relation count (relations inside subscripts counted as top-level), (5) missing argparse (`--output` silently ignored, file never written). Impact: each defect affects different measurements — must be mapped individually, not blanket "all invalid." |
| **Cross-references** | `semantic_honesty_scoreboard.py`, `scripts/test_structural_conservation.py`, `scripts/test_relation_identity.py` |
| **Unresolved** | Individual impact mapping for each defect: which measurements are affected, unaffected, or unverified. |

### CF-008: Typed Integral IR

| Attribute | Value |
|---|---|
| **Canonical owner** | Math reconstruction workstream (`docs/room-5-typed-integral-ir-2026-10-08.md`) |
| **Status** | SOURCE-ESTABLISHED — 5/5 fixtures pass; `Differential(variable=z)` as typed node |
| **Evidence dimensions** | Implementation: `scripts/test_integral_ir.py` (5/5 pass). Acceptance: independent fields (integrand/lower/upper/differential), scope preservation, nested expression safety, limit variation, conservation, honest fallback (measure=None + "measure_missing"). Scoreboard v15: 667 recoverable (19.6%), 331 solvable (9.7%), 0 FALSE_RECOVERY. |
| **Cross-references** | `math_contract.py` (ExprNode, Integral), `scripts/math_recovery_tool.py` (count_equalities), `DATASETS/scoreboard_v15.json` |
| **Unresolved** | Whether typed IR is consumed by any downstream pipeline. Whether double-integral case preserves both differentials. |

### CF-009: Porosity representations — three independent sources, no reconciliation

| Attribute | Value |
|---|---|
| **Canonical owner** | Field-lineage audit (`docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §5) |
| **Status** | SOURCE-ESTABLISHED — 3 sources, no reconciliation, `or` bug confirmed |
| **Evidence dimensions** | Source 1: Injection site porosity (integer 0-4) — `HEXAGRAM_INJECTION_SITE[h_id]['porosity']`. Source 2: Kit QWP (float 0.15-0.71) — `0.15 + u_idx*0.05 + l_idx*0.03`. Source 3: Emotional engine (float 0-1) — `_line_state_balance` + phase adjustment. Bug: `float(0) or 0.35` → 0.35 for Hex 7 and Hex 52 (should be 0.0). Scale mismatch: vortex formula treats porosity as 0-1 but source is 0-4. |
| **Cross-references** | `yao-line-semantic-audit-2026-10-29.md` §11 (porosity reconciliation); `pipeline-gap-analysis-2026-10-27.md` (porosity in shotgun output) |
| **Unresolved** | Whether vortex expects raw or normalized porosity. Whether normalization should occur at a documented boundary. Whether `structural_porosity`, `injection_site_porosity`, `line_balance_porosity` field names should be adopted. |

### CF-010: Yao-line semantic incompatibility

| Attribute | Value |
|---|---|
| **Canonical owner** | B4 semantic contract and U-07 register (`docs/yao-line-semantic-audit-2026-10-29.md`) |
| **Status** | SOURCE-ESTABLISHED — 163/384 records differ; 27 vs 156 yao lines; only 10 overlap |
| **Evidence dimensions** | Base CSV: 27 yao (all dissipator category, all porosity=4, category-specific filter). Enriched CSV: 156 yao (42 hexagrams, all categories, stress/activation criterion). Neither matches PHASE_LINE_MAP (0 of 13 / 0 of 42). Provenance: base generated by `shotgun_expand(emotional_input=50)` (Jul 21), enriched by Cloudflare Worker (emotional_input=88, session ws-openjarvis, Jul 6). `is_stressed` and `is_activated` perfectly correlated (same signal, two names). |
| **Cross-references** | `pipeline-gap-analysis-2026-10-27.md` (ternary not integrated); `traceability-matrix-2026-10-27.md` §3.2 (identity preservation) |
| **Unresolved** | Which criterion is correct. Generator provenance (no script exists). Whether `ternary_state` is safe as shared cross-generation field. Whether enriched `direction` is semantically validated. |

### CF-011: Ternary integration gap

| Attribute | Value |
|---|---|
| **Canonical owner** | King Wen integration audit (`docs/pipeline-gap-analysis-2026-10-27.md`) |
| **Status** | SOURCE-ESTABLISHED — 729 ternary hexagrams and 5,832 resolved states exist but are not consumed by shotgun_expand() |
| **Evidence dimensions** | `scripts/ternary_full_expansion.json` (2.9MB) contains 27 trigrams, 729 hexagrams, 5,832 resolved states. `shotgun_expand()` produces 64 expanded + 512 resolved (binary only). 448/512 resolved states have `ternary_slots=None`. 320/512 resolved states have unclassified temporal labels. `kingwen_quantum_expand.py` loads ternary data but `shotgun_expand()` does not. |
| **Cross-references** | `pipeline-output-measurement-2026-10-27.md` §1; `yao-line-semantic-audit-2026-10-29.md` §12.2; `traceability-matrix-2026-10-27.md` §3.2 |
| **Unresolved** | Whether ternary integration is intended or whether binary-only is the canonical path. Whether `ternary_slots`, `schauberger_parsing`, `personality_subsets` should be populated for all states. |

### CF-012: Math extraction and recovery pipeline

| Attribute | Value |
|---|---|
| **Canonical owner** | Math-pipeline evidence matrix (`docs/semantic_math_pipeline_report.md`, `docs/math-term-usage-analysis-2026-10-27.md`) |
| **Status** | PARTIALLY ESTABLISHED — substantial working components, end-to-end reliability not demonstrated |
| **Evidence dimensions** | 245 papers processed. 4,218 expressions extracted. 183,017 proof chain elements. 8,598 math images. 14-paper HTML benchmark: 3,409/3,409 (100%). 15 of 241 papers recovered. 69,069 missing occurrences. Solvability discrepancy: 457 (E2E) vs 120 (recovery). Null-LaTeX crash affects 5 of 241 papers. |
| **Cross-references** | `docs/pipeline-gap-analysis-2026-10-27.md`; `docs/pipeline-output-measurement-2026-10-27.md`; `docs/room-5-typed-integral-ir-2026-10-08.md` |
| **Unresolved** | End-to-end extraction-to-recovery reliability. Whether 457 vs 120 solvable is a mathematical contradiction or a methodological discrepancy. Whether extraction-path discrepancy (991 vs 884) is resolved. |

### CF-013: Lua interface fidelity (8 mismatches)

| Attribute | Value |
|---|---|
| **Canonical owner** | Lua migration contract (`docs/lua-math-tool.md`, `docs/traceability-matrix-2026-10-27.md` §4) |
| **Status** | KNOWN CONCERN — 8 mismatches documented, not corrected |
| **Evidence dimensions** | 4 renamed (`semantic_math.extract`→`extract_pdf_math`, `math_context.extract_with_context`→`extract_text_blocks`, `display_eq.extract`→`extract_display_equations`, `symbol_classifier.LOOKUP`→`MATH_SYMBOL_LOOKUP`), 2 unsupported as documented (`extract_clean.extract`, `tex_macros.extract_macros` — CLI scripts, no module function), 1 adapter-required (`jspace_math.extract_function` — contract mismatch), 1 renamed+type-mismatch (`mathml_parser.parse` — returns str, not tree). |
| **Cross-references** | `docs/traceability-matrix-2026-10-27.md` §4, §10 (build order) |
| **Unresolved** | Whether mismatches are naming differences or genuine capability differences. Whether lua-math-tool.md should be corrected against actual Python implementations before Lua port begins. |

### CF-014: Hamiltonian field-name collision (M3 vs JKD)

| Attribute | Value |
|---|---|
| **Canonical owner** | QSMC-1 mathematical provenance audit (§7.3, R-12) |
| **Status** | SOURCE-ESTABLISHED — two distinct producers, same field name |
| **Evidence dimensions** | Producer 1: M3 Hamiltonian (`emotional_engine.py`) — `pq_dot - lagrangian`, clamped [0,1]. Producer 2: JKD ingestion scalar (`ingest_jkd_megatron_wavepackets.py`) — `coherence - chaos - 0.5*darkTone + 0.3*voiceWeight - 0.2*whimsy`. Same field name `hamiltonian_energy`. No production code distinguishes between them. |
| **Cross-references** | `docs/consumer-repair-specification-2026-10-29.md` (R-12), `docs/information-loss-remediation-register.md` |
| **Unresolved** | Whether collision is intentional (both are "Hamiltonian energy" in different contexts) or accidental. |

### CF-015: Vortex porosity `or` bug

| Attribute | Value |
|---|---|
| **Canonical owner** | Field-lineage audit (`docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §2) |
| **Status** | SOURCE-ESTABLISHED — confirmed, fix not applied |
| **Evidence dimensions** | Code: `porosity = float(inject.get("porosity", 0.35) or 0.35)` in `scripts/schauberger_parsing_layers.py` line 19. Bug: `float(0) or 0.35` → 0.35 for Hex 7 and Hex 52 (should be 0.0). Scale mismatch: vortex treats porosity as 0-1 float, source is 0-4 integer. Porosity 2/3/4 all max out vortex strength. |
| **Cross-references** | `yao-line-semantic-audit-2026-10-29.md` §11 (porosity reconciliation); `pipeline-gap-analysis-2026-10-27.md` |
| **Unresolved** | Whether vortex expects raw or normalized porosity. Whether normalization should occur at a documented boundary. |

### CF-016: Jacobian has no production consumer

| Attribute | Value |
|---|---|
| **Canonical owner** | Field-lineage audit (`docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §3) |
| **Status** | SOURCE-ESTABLISHED — diagnostic only, no production consumer |
| **Evidence dimensions** | Spec: `docs/j-space-jacobian-lens-math-2026-07-11.md` documents J(a; v) = E[dY/dA] * dA. Diagnostic: `scripts/verify_math_jacobian_hamiltonian.py` computes perturbation vector. Production: no consumer in emotional_engine.py or state-transition paths. 5 prerequisites: input activation, output state representation, derivative convention, perturbation vector shape, production decision. |
| **Cross-references** | `traceability-matrix-2026-10-27.md` §3.3; `docs/hamiltonian-equation-comparison-2026-10-27.md` |
| **Unresolved** | All 5 prerequisites. Whether Jacobian should be integrated or remains diagnostic-only. |

### CF-017: Gaussian functional, needs validation

| Attribute | Value |
|---|---|
| **Canonical owner** | Field-lineage audit (`docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` §4) |
| **Status** | SOURCE-ESTABLISHED — functional, 4 validation tests needed |
| **Evidence dimensions** | `_gaussian_kernel()` in emotional_engine.py: functional, used for temporal phase modulation (FWHM=2.5). `gaussian_kernel()` in kingwen_state_transition.py: functional, used for future-phase bias. `_project_gaussian_future()`: functional, weights future phase through Gaussian. Validation needed: kernel normalization (sum to 1), FWHM interpretation (2.5 = phases ~2 away get ~50%), boundary behavior (phase 0 and 7), downstream identity preservation. |
| **Cross-references** | `traceability-matrix-2026-10-27.md` §2.7-2.9; `docs/ternary-paired-differential-math-correction-2026-08-02.md` |
| **Unresolved** | Whether FWHM=2.5 is correct. Whether Gaussian blending preserves hexagram identity. |

### CF-018: No cross-hexagram normalization invariant

| Attribute | Value |
|---|---|
| **Canonical owner** | Traceability matrix (`docs/traceability-matrix-2026-10-27.md` §8, Invariant A) |
| **Status** | SPECIFIED — 64 canonical identities must retain own mappings; no universal fallback to Hexagram 1 |
| **Evidence dimensions** | Governing invariant: no cross-hexagram normalization, no semantic convergence, no identity-erasing deduplication. Referenced by Sections 1-7 of traceability matrix. T10 (no cross-hexagram normalization test) missing from build order. |
| **Cross-references** | `docs/yao-line-semantic-audit-2026-10-29.md` §12 (phase terminology); `docs/representation-equivalence-audit-checklist-2026-10-29.md` |
| **Unresolved** | Whether the invariant is enforced by any automated test. Whether any pipeline stage violates it. |

---

## 3. Cross-Document Reference Map

| Document | Role | Findings Discussed |
|---|---|---|
| `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` | Provenance authority | CF-001, CF-002, CF-003, CF-004, CF-005, CF-014 |
| `docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md` | Diagnostic report | CF-001, CF-009, CF-015, CF-016, CF-017 |
| `docs/traceability-matrix-2026-10-27.md` | Traceability authority | CF-001, CF-006, CF-009, CF-013, CF-018 (all sections) |
| `docs/yao-line-semantic-audit-2026-10-29.md` | Semantic audit | CF-009, CF-010, CF-011, CF-018 (§13) |
| `docs/room-5-typed-integral-ir-2026-10-08.md` | IR spec | CF-006, CF-007, CF-008 |
| `docs/semantic_math_pipeline_report.md` | Pipeline report | CF-012 |
| `docs/math-term-usage-analysis-2026-10-27.md` | Term usage | CF-001 (term provenance), CF-005 |
| `docs/pipeline-gap-analysis-2026-10-27.md` | Gap analysis | CF-001 (R-14), CF-009, CF-011, CF-012 |
| `docs/pipeline-output-measurement-2026-10-27.md` | Output measurement | CF-011, CF-012 |
| `docs/lua-math-tool.md` | Migration contract | CF-013 |
| `docs/hamiltonian-equation-comparison-2026-10-27.md` | Design intent | CF-001, CF-003, CF-004 |
| `docs/audit-drift-report-2026-10-27.md` | Drift findings | CF-001, CF-014 |
| `docs/consumer-repair-specification-2026-10-29.md` | Consumer repair | CF-001, CF-014 |
| `docs/information-loss-remediation-register.md` | Remediation register | CF-001 (R-14), CF-014 (R-12) |
| `docs/representation-equivalence-audit-checklist-2026-10-29.md` | Equivalence checklist | CF-018 (cross-hexagram normalization) |
| `docs/shotgun-expand-output-contract-2026-10-29.md` | Output contract | CF-011 (ternary integration) |
| `docs/ternary-paired-differential-math-correction-2026-08-02.md` | Math spec | CF-001 (signed differentials), CF-003 (abs() violation) |
| `docs/frozen-regression-execution-results-2026-11-03.md` | Frozen regression execution | CF-020 (vision pipeline), CF-023 (stretched symbols, border recognition) |
| `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | Frozen regression mapping | CF-020 (vision pipeline), CF-023 (stretched symbols, border recognition) |
| `docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md` | Vision audit | CF-020 (vision pipeline), CF-023 (stretched symbols, braces/brackets, border recognition) |
| `docs/occurrence-lifecycle-ledger-contract-2026-11-03.md` | Occurrence lifecycle contract | CF-006 (occurrence identity), CF-019 (extraction paths), CF-022 (integration levels) |
| `docs/cross-document-finding-authority-map-2026-11-03.md` | This document | All findings (CF-001 through CF-023) |
| `docs/numerical-extraction-vision-pipeline.md` | Vision pipeline audit | CF-012 (pipeline architecture), CF-019 (seam mismatch), CF-020 (vision pipeline), CF-021 (reference catalog discrepancy) |
| `docs/pix2text-assessment-2026-10-20.md` | Pix2Text assessment | CF-020 (vision pipeline), CF-021 (reference catalog) |
| `docs/pix2text-three-layer-experiment.md` | Pix2Text experiment design | CF-020 (three-layer design), CF-021 (reference library) |
| `docs/adjudication-layer-contract.md` | Adjudication contract | CF-020 (layer 1-3 status model) |
| `docs/cross-verification-checklist-2026-09-01.md` | Cross-verification | CF-019 (seam mismatch noted), CF-020 (vision pipeline verification) |

### CF-019: Seam mismatch — semantic_math_extractor.py uses flat regex, not MathML tree walk

| Attribute | Value |
|---|---|
| **Canonical owner** | Math-pipeline evidence matrix / extraction integrity (`docs/numerical-extraction-vision-pipeline.md` §2, §4) |
| **Status** | SOURCE-ESTABLISHED — verified seam mismatch |
| **Evidence dimensions** | Implementation: `semantic_math_extractor.py` uses flat regex parsing (PyMuPDF `get_text("blocks")`), not the MathML tree walk in `mathml_parser.py`. 991/991 equations verified on 2605.00155 via `arxiv_html_parser.py` but extraction pipeline does not consume the MathML parser. Seam mismatch: `mathml_parser.py` tree walk is NOT imported by `semantic_math_extractor.py`. Verified by `grep -n "mathml_parser" scripts/semantic_math_extractor.py` returning no matches. |
| **Cross-references** | `docs/semantic_math_pipeline_report.md` (pipeline report, 245 papers, 4,218 expressions); `docs/pix2text-assessment-2026-10-20.md` §5 (pipeline run 4/4); `docs/cross-verification-checklist-2026-09-01.md` (seam mismatch noted) |
| **Unresolved** | Whether `semantic_math_extractor.py` should be switched to use `mathml_parser.py` tree walk. Whether the flat-regex path has any legitimate use (e.g., PDF fallback when MathML unavailable). |

### CF-020: Vision comparison pipeline — Pix2Text OCR on PDF crops

| Attribute | Value |
|---|---|
| **Canonical owner** | Math-pipeline evidence matrix / vision pipeline (`docs/numerical-extraction-vision-pipeline.md` §7, `docs/pix2text-assessment-2026-10-20.md`) |
| **Status** | SOURCE-ESTABLISHED — 4/4 candidates processed and recognized |
| **Evidence dimensions** | Implementation: `scripts/vision_comparison_pipeline.py --paper 1907.04931 --max-per-paper 4`. Crop method: PyMuPDF pixmap → OpenCV decode. 4 non-empty OCR recognitions, 0 empty/failed. All 4 classified as `image_region` (OCR captures target formula alongside surrounding prose/line fragments within crop bounding box). Output: `DATASETS/vision_comparison/vision_comparison_results.jsonl`. Reference catalog: `symbols.zip` = 3,304 glyphs (NOT the 1,182-entry Metamath HTML manifest). |
| **Cross-references** | `docs/pix2text-three-layer-experiment.md` (three-layer design); `docs/adjudication-layer-contract.md` (layer 1-3 status model); `docs/cross-verification-checklist-2026-09-01.md` (vision pipeline verification) |
| **Unresolved** | Semantic formula isolation from surrounding text remains the next phase. Whether Pix2Text reliably preserves `munderover` limit placement. Whether vision errors cascade into source-fidelity failures. |

### CF-021: Reference catalog discrepancy — symbols.zip (3,304) vs Metamath HTML manifest (1,182)

| Attribute | Value |
|---|---|
| **Canonical owner** | Math-pipeline evidence matrix / vision pipeline (`docs/pix2text-assessment-2026-10-20.md` §5, `docs/pix2text-three-layer-experiment.md` §2) |
| **Status** | SOURCE-ESTABLISHED — pipeline uses symbols.zip, not Metamath HTML |
| **Evidence dimensions** | Implementation: `self.glyph_catalog = self.manifest.get('symbols_zip_catalog', {}).get('catalog', [])` — uses `symbols.zip` = 3,304 glyphs as reference catalog. Metamath HTML corpus has 1,182 symbol entries (`<area>` chart tags), 29 local GIF files, 1,158 remote hrefs, 0 PNG files. These are distinct reference sources used for different purposes: symbols.zip for pipeline glyph matching, Metamath HTML for Layer 1 (glyph recognition) ground truth. |
| **Cross-references** | `docs/pix2text-three-layer-experiment.md` §2 (reference library); `docs/numerical-extraction-vision-pipeline.md` §7 (layer reference catalog) |
| **Unresolved** | Whether 3,304 vs 1,182 is a coverage gap or a design choice. Whether the Metamath manifest should be the canonical reference for Layer 1. |

### CF-022: King Wen integration levels — three distinct routes, only two established

| Attribute | Value |
|---|---|
| **Canonical owner** | Occurrence lifecycle ledger contract (`docs/occurrence-lifecycle-ledger-contract-2026-11-03.md` §8) |
| **Status** | SOURCE-ESTABLISHED — 3 levels identified, only 2 established |
| **Evidence dimensions** | Level 1 (paper text → King Wen intent): Established. `recover_training_data.py` processes paper text through `extract_intent()` → `shotgun_expand()` → consensus. 6.8 GB artifact, 54 papers, 82,224 records, 1,536 records per paper. Level 2 (equation text/context → King Wen lexical intent): Working experiment. `math_to_kingwen_adapter.py` routes equation-level text. 989/991 classified as "understand", 2/991 as "destroy", 989/991 zero matched intents. Working but not meaningful mathematical-semantic discrimination. Level 3 (structured mathematical evidence → King Wen expansion): Unestablished. ExprNode IR, SymPy solutions, structural conservation scores, recovery adjudication, and occurrence identities are not shown to be consumed by any King Wen generator. |
| **Cross-references** | `docs/numerical-extraction-vision-pipeline.md` (CF-019 pipeline); `docs/math-pipeline-evidence-matrix-2026-11-03.md` (CF-012 extraction/recovery) |
| **Unresolved** | Whether Level 3 integration is intended. Whether the 6.8 GB artifact should be preserved as historical evidence (recommended: yes). Whether `math_to_kingwen_adapter.py` routing constitutes meaningful integration or lexical approximation. |

### CF-023: Vision pipeline — stretched symbols, braces/brackets, and border recognition bypassed

| Attribute | Value |
|---|---|
| **Canonical owner** | Vision stretched-symbols audit (`docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md`) |
| **Status** | IMPLEMENTED — 8 new functions added to `vision_comparison_pipeline.py` (2026-11-03). `balloon_glyph()`, `balloon_glyph_to_match()`, `detect_border_contamination()`, `expand_crop_context()`, `detect_math_regions_on_page()`, `extract_text_boundaries()`, `detect_partial_formulas()`, `recognize_formula_multiscale()`. Gaps 1 & 2 still need `get_ascii_pattern()` and `classify_alignment()` updates.
| **Evidence dimensions** | Gap 1: `get_ascii_pattern()` (line 249-274) maps only 6 bracket chars to 'B' class; big delimiters (`\left(`, `\right)`, `\lfloor`, `\rfloor`, etc.) and big operators (`\sum`, `\int`, `\prod`, etc.) fall to 'X' (default), causing structural similarity to fail. Gap 2: `classify_alignment()` (line 201-247) classifies correctly-recognized stretched symbols as `stretch_suspect` (score 0.3) with no distinction from OCR hallucination. Gap 3: `crop_pdf_region()` (line 89-149) uses minimal padding (3, 2) points; no border-contamination detection; fraction bars touching borders cause OCR overline/fraction hallucinations (documented in `build_visual_review_log.py`). Gap 4: `recognize_formula()` (line 150-199) passes raw crop to Pix2Text without multi-scale or context-inclusive recognition; no fallback to wider crop when tight crop fails. |
| **Cross-references** | `docs/numerical-extraction-vision-pipeline.md` (CF-019/CF-020); `docs/pix2text-assessment-2026-10-20.md`; `docs/pix2text-three-layer-experiment.md` |
| **Unresolved** | Whether any of the 4 vision comparison candidates contain stretched symbols or border contamination. Whether `get_ascii_pattern` expansion would change the 4/4 `image_region` classification. Whether multi-scale recognition would improve structural fidelity. |

---

## 4. Evidence Dimensions:

Each finding is assessed across five independent evidence dimensions. These must not be conflated.

| Dimension | Definition | Example |
|---|---|---|
| **Implementation behavior** | What the code actually does when executed | `_hamiltonian_energy()` returns 0.0 for all 512 states |
| **Mathematical validity** | Whether the formula is mathematically sound | `pq_dot - L` with 0-1 vs 0-6 scales is dimensionally invalid |
| **Measurement validity** | Whether the tools that measure the system are correct | 5 measurement-layer defects found; `count('=')` counts `<=` as equations |
| **Provenance** | Where the formula/constant/data originated | Coefficients 0.5/0.3/0.2: no derivation found; QuantumLab and wiki corpus ruled out |
| **Downstream impact** | What breaks or degrades because of the finding | All avatar animations zeroed; 448/512 states have `ternary_slots=None` |

**Cross-cutting rule:** A finding can be valid in one dimension and invalid in another. For example, CF-007 (measurement-layer defects) affects measurement validity but does not invalidate implementation behavior or mathematical validity. CF-001 (Hamiltonian 0.0) affects implementation behavior and downstream impact but the mathematical validity question (is `pq_dot - L` the right formula?) remains unresolved.

---

## 5. Gate-Status Registry

Three independent gate contexts. Their statuses must not be consolidated.

| Gate | Context | Status | Blocking | Canonical Owner |
|---|---|---|---|---|
| QSMC-1 Gate 2 | Mathematical provenance audit (Hamiltonian) | **OPEN** | No remediation until semantics established | `docs/qsmc1-m3-mathematical-provenance-and-formulation-audit.md` |
| B4 Gate 2 | Ternary semantic contract (U-07) | **BLOCKED by U-07** | Unresolved ternary semantic contract blocks parameter generation | `docs/yao-line-semantic-audit-2026-10-29.md` §12.9 |
| Lua migration prerequisite | Gates 1-5 must be green before Lua port begins | **Not yet passed** | 8 interface mismatches remain; gates 1-5 not all verified | `docs/traceability-matrix-2026-10-27.md` §10 |

**Rule:** QSMC-1 Gate 2 is "investigated but open." B4 Gate 2 is "blocked by missing contract." The Lua prerequisite is "migration gate, not evidence of completion." These are substantively different statuses and must not be merged.

---

## 6. Conflict and Supersession Rules

### 6.1 Known conflicts

| Conflict | Doc A | Doc B | Resolution |
|---|---|---|---|
| Hamiltonian formula version | `vortex-hamiltonian-diagnostic` §1: 4 terms (`dy + yao_dy + old_dy + stable_dy`) | `qsmc1-m3-audit` §2.2: 3 terms (`dy, yao_dy, changing_dy`) with 0.5/0.3/0.2 | **qsmc1-m3-audit is authoritative** — vortex doc describes the October 27 design-intent formula, not the implementation. The vortex doc is an earlier diagnostic; the audit is the deeper investigation. |
| Hamiltonian classification | `math-term-usage-analysis`: "heuristic scoring function" | `qsmc1-m3-audit`: "scalar calculation with Hamiltonian-inspired naming" | **qsmc1-m3-audit is authoritative** — more precise; distinguishes "heuristic" from "custom scalar" and notes naming/interpretation gap. |
| Porosity scale | `vortex-hamiltonian-diagnostic`: "0-4 integer, needs normalization" | `yao-line-semantic-audit` §11: "3 independent sources, no reconciliation" | Both agree on the finding; yao audit adds field-naming recommendation. No conflict — complementary. |
| Equation count for 2605.00155 | `semantic_math_pipeline_report`: "991 equations" | `room-5-typed-integral-ir`: "3,409 equations across 14 papers" | **Not a conflict** — different scopes (one paper vs. 14-paper corpus). Easily confused; must be labeled by scope. |

### 6.2 Supersession chain

| Original Finding | Superseded By | Reason |
|---|---|---|
| "recoverable = 721 (21.2%)" (v14, inflated) | "recoverable = 667 (19.6%)" (v15, honest) | `count('=')` counted `<=`, `>=`, `!=` as equations. Corrected `count_equalities()` strips these first. |
| "solvable = 457" (E2E pipeline) | Not yet superseded — under investigation | Methodological discrepancy, not necessarily mathematical contradiction. May be different acceptance rules or input populations. |
| "solvable = 120" (recovery tool) | Not yet superseded — under investigation | Same as above. |
| "Hex 15/20/30/40 get 0 assignments" (build_per_hex_training_data.py) | "Hex 7 and Hex 52 affected by `or` bug" | Original statement was wrong; corrected to identify actual affected hexagrams. |

### 6.3 Historical findings preserved

The following findings were later superseded or reclassified but remain visible in their original documents:

- `vortex-hamiltonian-diagnostic` §1's 4-term formula description (superseded by qsmc1-m3-audit's 3-term finding, but preserved as evidence of the design-intent formula)
- `room-5-typed-integral-ir` §"Defect found during verification" (5 measurement-layer defects — preserved as historical record of measurement-system failures)
- `yao-line-semantic-audit` §9 (git history provenance — preserved as evidence of generation lineage)

---

## 7. Completeness and Acceptance Checks

### 7.1 Finding completeness

Every finding in the registry has:
- [x] One stable ID (CF-NNN)
- [x] One canonical owner
- [x] A status (VALIDATED / SOURCE-ESTABLISHED / UNRESOLVED / KNOWN CONCERN / PARTIALLY ESTABLISHED / SPECIFIED)
- [x] Evidence dimensions (implementation, mathematical validity, measurement validity, provenance, downstream impact)
- [x] Cross-references to supporting documents
- [x] Unresolved questions recorded

23 findings registered (CF-001 through CF-023). 18 from the original 10-doc comparison, 3 from the vision-related docs that were missed (CF-019 seam mismatch, CF-020 vision pipeline, CF-021 reference catalog discrepancy), 1 from the occurrence lifecycle ledger contract (CF-022 King Wen integration levels), and 1 from the vision stretched-symbols audit (CF-023 stretched symbols, braces/brackets, and border recognition bypassed).

### 7.2 Acceptance criteria verification

| Criterion | Status |
|---|---|
| Every finding has one canonical identity and owner | ✅ 22 findings, each with one owner |
| Supporting documents are linked without duplicating ownership | ✅ Cross-reference map (§3) links without duplicating |
| Conflicting formulas and historical interpretations remain visible | ✅ §6.1 preserves all conflicts with resolution |
| Evidence status is distinct from implementation status and acceptance status | ✅ §4 defines 5 independent dimensions |
| The three gate contexts remain independent | ✅ §5 preserves QSMC-1, B4, and Lua as separate |
| No unsupported relationship is promoted to a dependency | ✅ No finding claims dependency on another unless documented |
| No finding is silently deleted, merged, or reclassified | ✅ §6.2 records all supersessions explicitly |
| CF-019 cited as integration-seam, not comparative-accuracy | ✅ Enforced in CF-019 scope enforcement section |
| CF-020 vision results scoped to recognition only | ✅ Three-layer framework prevents overclaim |
| CF-021 reference catalogs remain separate populations | ✅ Both catalogs documented with distinct purposes |

### 7.3 What this map does NOT establish

- It does not establish that any finding is resolved. All findings retain their original status.
- It does not establish that any gate has passed. All gate statuses are preserved as-is.
- It does not establish that any document should be edited, deleted, or merged.
- It does not establish remediation priority or acceptance criteria for source changes.
- It does not establish that the cross-reference comparison is complete — additional math-related docs may exist that were not included in this audit.

### CF-019 scope enforcement

CF-019 establishes an **integration-seam finding**, not a comparative-accuracy finding.

**What CF-019 establishes:**
- `mathml_parser.py` successfully processes the MathML-based representation (991/991 on 2605.00155).
- `semantic_math_extractor.py` uses flat regex against PyMuPDF text blocks.
- The end-to-end extraction path does not consume the MathML parser's tree-walk output.
- These are two different implementations for two different input types (arXiv HTML vs. PDF).

**What CF-019 does NOT establish:**
- That MathML is superior to PDF extraction across the entire corpus.
- That the flat-regex path produces incorrect results.
- That switching to MathML would improve solvability, accuracy, or any other metric.
- Comparative accuracy of the two paths on any shared input.

**Enforced rule:** CF-019 must be cited as an integration-seam problem. Any document, finding, or assessment that cites CF-019 must use the narrower formulation: "two extraction paths have different implementations, and the verified MathML parser is not consumed by the reported semantic extraction path."

### Recommended next milestone: CF-019 impact map

**Purpose:** Identify the practical reach of the seam without modifying either pipeline.

**Scope:** Read-only analysis. No source changes, no remediation, no gate changes.

**Required outputs:**
1. Which downstream outputs (JSON, CSV, JSONL, reports) depend on the flat-regex path.
2. Which downstream outputs consume MathML parser output directly.
3. Which downstream outputs operate independently of both paths (e.g., solver backends, adjudication layer).
4. For each dependency, whether the output would change if the seam were closed.

**Acceptance boundary:** The impact map must not recommend closure of the seam, must not estimate improvement metrics, and must not modify any pipeline code. It is a read-only dependency trace.

The following vision-related .md files were **missed** in the original 10-document comparison. They have now been incorporated as CF-019, CF-020, and CF-021:

- `docs/numerical-extraction-vision-pipeline.md` — Vision pipeline audit: seam mismatch (CF-019), vision pipeline run (CF-020), reference catalog discrepancy (CF-021), cross-file consistency obligations, 5 unblocking blockers.
- `docs/pix2text-assessment-2026-10-20.md` — Pix2Text architectural assessment: three-layer comparison framework (glyph recognition, expression reconstruction, source fidelity), verified failure analysis (crop too small, 4/4 recognized after fix), reference library (Metamath HTML 1,182 entries, symbols.zip 3,304 glyphs).
- `docs/pix2text-three-layer-experiment.md` — Three-layer experiment design: reference library (29 local GIFs, 1,182 symbol entries, 1,158 remote hrefs), evaluation examples, three-layer scoring, Pix2Text import compatibility blocker (rapidocr 3.10.0 vs Pix2Text 1.1.7).
- `docs/adjudication-layer-contract.md` — Adjudication layer contract: 3-layer status model (discovery → adjudication → targeted), 5-level status semantics, denominator declarations.
- `docs/cross-verification-checklist-2026-09-01.md` — Cross-verification checklist: vision pipeline verification, OpenJarvis path fix, Tesseract OCR blocker.

### 7.5 Documents still not included

The following docs exist but were not included in this comparison. They should be added to a future revision:

- `docs/wolfram_notation_reference.md` — Wolfram notation reference (143 symbols)
- `docs/hamiltonian-equation-comparison-2026-10-27.md` (partially referenced via CF-004)
- `docs/formula-design-review-2026-10-27.md` (partially referenced via CF-001)
- `docs/consumer-repair-specification-2026-10-29.md` (partially referenced via CF-014)
- `docs/representation-equivalence-audit-checklist-2026-10-29.md` (partially referenced via CF-018)
- `docs/shotgun-expand-output-contract-2026-10-29.md` (partially referenced via CF-011)
- `docs/ternary-paired-differential-math-correction-2026-08-02.md` (referenced via CF-001)
- `docs/j-space-jacobian-lens-math-2026-07-11.md` (referenced via CF-016)
- `docs/KING-WEN-RESEARCH-CHECKLIST.md` (referenced via CF-001)
- `docs/immutable-table-math-decoded.md` (referenced via CF-001)
- `docs/KING_WEN_CONSENSUS_MATH.md` (referenced via traceability matrix §2.7-2.9)

---

*End of cross-document finding authority map. This is a read-only governance artifact. No source modifications, commits, remediation acceptance, or gate-status changes are implied by its creation.*