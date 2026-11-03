# Controlled Remediation Verification Protocol — 2026-11-02

## Purpose

Read-only specification defining the controlled remediation verification procedure for all 27 entries in the Information-Loss Remediation Register (`docs/information-loss-remediation-register.md`). This protocol governs how demonstrated failures are corrected without changing the architecture those failures were supposed to serve.

## Non-negotiable constraints (unchanged)

- No source modifications are authorized by this document.
- No formula changes.
- No destructive normalization or collapse.
- No forced equivalence between representations.
- No deletion or consolidation of independent implementations.
- Preserve unique capabilities and historical outputs.
- Gate 2 remains OPEN.
- QSMC-1's original nine-document baseline remains frozen.
- Each remediation entry must link to both its original failure evidence and its historical regression target.

## Section 1: Verification Protocol — Eight-Step Controlled Remediation Procedure

For every remediation entry (R-01 through R-27), the following eight steps must be completed in order. No step may be skipped. No step may be reordered.

### Step 1: Record original behavior

Document the current state of the affected system before any change is applied. This includes:

- Exact file paths and line numbers of affected code.
- Current function signatures, output structures, and data values.
- Reproduction commands and their observed output.
- Any existing test coverage and its current pass/fail status.

**Evidence artifact:** Save as `docs/remediation_evidence/<entry_id>_original_behavior.md` with timestamp.

### Step 2: Identify the exact correction boundary

State precisely what will change and what will NOT change. The correction boundary must be specific enough that a reviewer can verify compliance without interpretation.

Required elements:
- Files to be modified (exact paths).
- Functions to be modified (exact names and signatures).
- Fields to be added, removed, or renamed.
- What will remain untouched (explicit list).

**Evidence artifact:** Save as `docs/remediation_evidence/<entry_id>_correction_boundary.md`.

### Step 3: Preserve the original implementation and evidence

Create a backup of the original implementation before any change. This is not a rollback mechanism — it is evidence preservation.

Required elements:
- Copy of original file(s) to `docs/remediation_evidence/<entry_id>_original/`.
- Git commit hash of the state before remediation.
- Any generated artifacts (JSONL, CSV, PLY, etc.) that will be affected.

**Evidence artifact:** Save as `docs/remediation_evidence/<entry_id>_original/`.

### Step 4: Apply only the specifically authorized change

Apply the correction within the identified boundary. No additional changes, no refactoring, no "while I'm here" improvements.

Required elements:
- Single-purpose commit containing only the authorized change.
- Commit message references the entry ID and the correction boundary document.

**Evidence artifact:** Git commit with message format: `remediation(<entry_id>): <description>`.

### Step 5: Run the affected consumer tests

Execute all tests that exercise the affected consumers. This includes:

- Unit tests for modified functions.
- Integration tests for affected consumers.
- Any contract tests defined in the remediation register.
- `py_compile` on all modified Python files.
- `npm run build` if any TypeScript/JavaScript files are modified.

**Evidence artifact:** Save test output as `docs/remediation_evidence/<entry_id>_test_results.txt`.

### Step 6: Compare before-and-after outputs

Compare the post-remediation output against the pre-remediation output (from Step 1) for all affected consumers. Document:

- What changed (specific fields, values, structures).
- What did not change (must match pre-remediation).
- Whether the change resolves the identified failure.
- Whether any unintended changes occurred.

**Evidence artifact:** Save comparison as `docs/remediation_evidence/<entry_id>_before_after.md`.

### Step 7: Verify all seven intentional boundaries remain intact

Check each of the seven intentional boundaries (R-21 through R-27) against the post-remediation state. For each boundary, verify:

- The boundary still holds (no collapse, no equivalence, no consolidation).
- The field name, structure, and meaning are unchanged.
- No consumer has begun treating the boundary as a defect to fix.

**Evidence artifact:** Save as `docs/remediation_evidence/<entry_id>_boundary_check.md`.

### Step 8: Record the result as passed, failed, or inconclusive

Record the final disposition with reproducible supporting evidence.

Required elements:
- Disposition: `PASSED`, `FAILED`, or `INCONCLUSIVE`.
- If `PASSED`: evidence that the failure is resolved AND all 7 boundaries intact.
- If `FAILED`: what failed, why, and whether the change should be reverted.
- If `INCONCLUSIVE`: what evidence is missing and what additional investigation is needed.
- Link to all evidence artifacts from Steps 1-7.

**Evidence artifact:** Save as `docs/remediation_evidence/<entry_id>_disposition.md`.

---

## Section 2: Architectural Invariants (R-21 through R-27)

These seven intentional boundaries must be checked during EVERY remediation, regardless of which entry is being remediated. They are not regression tests — they are architectural invariants.

### INV-01: 729 ternary permutations remain count-only in shotgun_expand()

- **Register entry:** R-21
- **Invariant:** `shotgun_expand()` stores `ternary_729_permutations_count: 729` but does NOT store the actual 729 permutations. The permutations exist in `scripts/ternary_full_expansion.json` (2.9MB).
- **Check:** Verify that `shotgun_expand()` output still contains `ternary_729_permutations_count` (integer, 729) and does NOT contain a `ternary_729_permutations` array of 729 items.
- **Failure mode:** Integration of ternary data into shotgun_expand() output without verifying positional identity preservation.
- **Correction boundary:** Any integration must preserve the 9-bit positional identity and must not collapse the ternary layer into the binary layer.

### INV-02: Schauberger parsing remains phase=0 only

- **Register entry:** R-22
- **Invariant:** `schauberger_parsing` is computed for `expanded[]` (phase=0) only. It is `None` for all 512 resolved states.
- **Check:** Verify that 64/64 expanded items have non-None `schauberger_parsing` and 512/512 resolved items have `schauberger_parsing: null`.
- **Failure mode:** Duplication of Schauberger parsing across 8 phases without evidence of phase-dependency.
- **Correction boundary:** Any change must demonstrate that Schauberger metrics are phase-dependent before computing them for phases 1-7.

### INV-03: Domain routing palette remains phase=0 only

- **Register entry:** R-23
- **Invariant:** `domain_routing_palette` is computed for `expanded[]` (phase=0) only. It is absent from `resolved[]` items.
- **Check:** Verify that 64/64 expanded items have `domain_routing_palette` and 512/512 resolved items do NOT have the key.
- **Failure mode:** Duplication of domain routing palette across 8 phases without evidence of phase-dependency.
- **Correction boundary:** Any change must demonstrate that palette computation is phase-dependent before computing it for phases 1-7.

### INV-04: Projections remain phase=0 only

- **Register entry:** R-24
- **Invariant:** `projections` is computed for `expanded[]` (phase=0) only. It is absent from `resolved[]` items.
- **Check:** Verify that 64/64 expanded items have `projections` and 512/512 resolved items do NOT have the key.
- **Failure mode:** Duplication of projections across 8 phases without evidence of phase-dependency.
- **Correction boundary:** Any change must demonstrate that projection computation is phase-dependent before computing it for phases 1-7.

### INV-05: Pre-slider capture remains phase=0 only

- **Register entry:** R-25
- **Invariant:** `pre_slider` is computed for `expanded[]` (phase=0) only. It is absent from `resolved[]` items.
- **Check:** Verify that 64/64 expanded items have `pre_slider` and 512/512 resolved items do NOT have the key.
- **Failure mode:** Duplication of pre-slider capture across 8 phases.
- **Correction boundary:** Any change must demonstrate that pre-slider capture is phase-dependent before computing it for phases 1-7.

### INV-06: 9-bit ternary decoding remains unintegrated

- **Register entry:** R-26
- **Invariant:** `shotgun_expand()` does not integrate the 9-bit ternary decoding (6 base + 3 phase) from `kingwen_ternary_tables_complete.py` or `kingwen_quantum_expand.py`. The ternary layer exists independently.
- **Check:** Verify that `shotgun_expand()` output does not contain `ternary_lines` (6 positions, 0/1/2) or `ternary_resolved_states` (5,832 states) in either `expanded[]` or `resolved[]` items.
- **Failure mode:** Integration of ternary data without verifying positional identity preservation.
- **Correction boundary:** Any integration must preserve the binary/ternary distinction and must not collapse the ternary layer into the binary layer.

### INV-07: Personality consensus remains aggregation, not collapse

- **Register entry:** R-27
- **Invariant:** `personality_consensus` is a weighted aggregation across all 64 hexagrams. It does not replace individual hexagram identities.
- **Check:** Verify that `shotgun_expand()` output contains both `expanded[]` (64 items with individual identities) AND `personality_consensus` (summary statistics). Verify that removing `personality_consensus` does not remove any hexagram identity from `expanded[]`.
- **Failure mode:** Treating `personality_consensus` as equivalent to `consensus_hexagram_id` or collapsing to a single-hex resolve.
- **Correction boundary:** Any change must preserve the distinction between aggregation (consensus) and individual identity (expanded[]). Must not collapse the consensus into a single-hex resolve.

---

## Section 3: Historical Usage and Regression Evidence

This section provides historical context for each remediation entry. Historical evidence establishes prior behavior and regression targets. It does NOT authorize source changes or establish current architectural authority.

### Historical timeline

| Date | Event | Relevance to register |
|------|-------|----------------------|
| 2026-09-18 | Immutable tables and expansion-first architecture established | Establishes R-21–R-27 as original design requirements, not audit inventions |
| 2026-09-27 | Repository and topology discussion | Establishes that large outputs (30MB) and small outputs (50-line) serve distinct purposes (R-19) |
| 2026-10-04 | Training-data lineage: collapse-based pipeline | Establishes historical training path; collapse is historical evidence, not current authority (R-02, R-03, R-04) |
| 2026-10-27 | Consumer repair: loader fix for `shotgun_expand_output.json` | Establishes precedent that import repair ≠ consumer correctness (R-01, R-02) |
| 2026-10-27 | Training JSONL: `full_shotgun_expansion_all.jsonl` (1,536 records) | Establishes M3 zero was visible in serialized data before mathematical reproduction (R-14) |
| 2026-11-02 | M3/M6/viewer evidence chain | Establishes runtime evidence for R-11, R-12, R-14, R-15 |

### Historical evidence per register entry

#### R-01 — Missing `scripts/__init__.py`

- **Historical evidence (2026-10-27):** Consumer repair attempted to fix references to nonexistent `shotgun_expand_output.json`. Basic checks (`py_compile`, `PY_VERIFY_OK`, 64 injection sites, porosity fields) passed, but downstream consumption was not independently verified.
- **Regression target:** After adding `__init__.py`, all 7 affected consumers must produce identical output to their pre-remediation state. Import resolution alone is insufficient.
- **Historical distinction:** The October 27 repair fixed the file reference but did not verify that consumers correctly interpret the producer's output. R-01 must not repeat this gap.

#### R-02 — Nonexistent `shotgun_expand_output.json` reference

- **Historical evidence (2026-10-04):** The collapse-based training pipeline (`collapse_full_128_output.json` → `build_pretrain.py` → `kingwen_pretrain.jsonl`) existed as a historical path. It produced 2 records per state with hexagram, phase, polarity, injection, porosity, reason, vector, and yao information. Seven domains were tagged (KING_WEN_ORACLE, SOVEREIGN_PIPELINE_SCENE, OPENJARVIS_INTERACTION, HERMES, POG2, SLIDER_CAPTURE, TERNARY_INTERACTION). Porosity weights ranged 1.00–1.50. Corpus modifier was 0.6.
- **Regression target:** Any update to file path references must preserve the distinction between the canonical producer (`shotgun_expand()`) and any cached serialization. Must not restore collapse-based pipeline as current authority.
- **Historical distinction:** The collapse-based pipeline is historical evidence of how training records were previously generated. It is not authority to restore collapse or assume the old 128-state representation remains intended.

#### R-03 — Empty `text` and `request_text` in all 1,536 JSONL records

- **Historical evidence (2026-10-27):** `full_shotgun_expansion_all.jsonl` contained 1,536 records (64×8×3) with empty `text` and `request_text` fields. No request context was provided during batch generation.
- **Regression target:** Any fix must provide request text or document the omission. Must not fabricate request text. Must not treat empty text as equivalent to "no request" without documenting the distinction.

#### R-04 — Default intent "understand" for 989/991 equations

- **Historical evidence (2026-10-27):** `intent.dominant_intent` was "understand" for 989/991 records in the serialized dataset. This was visible in actual serialized data, not merely in isolated mathematical tests.
- **Regression target:** Any fix must derive intent from actual request text or equation content, or document the default as a documented simplification with explicit provenance. Must not silently assign a default.

#### R-05 through R-10 — Phase=0-only fields

- **Historical evidence (2026-09-18):** Expansion-first architecture established no early collapse, deterministic generation, no pseudo-random substitution. Reductions (SVD/POD) were to remain observational layers, not replacements for the underlying state space.
- **Regression target:** Any change to phase-dependent field computation must demonstrate that the computation is phase-dependent before computing for phases 1-7. Must not duplicate fields across phases without evidence.

#### R-11 — Viewer zero masking (`|| 0.75`)

- **Historical evidence (2026-11-02):** World viewer uses `passage.energy || 0.75` which replaces explicit zero with 0.75. Confirmed via reproduction.
- **Regression target:** Any fix must preserve the distinction between "energy is zero" and "energy is absent." Must not mask zero with a nonzero fallback.

#### R-12 — Field-name collision: `hamiltonian_energy`

- **Historical evidence (2026-11-02):** M3 `_hamiltonian_energy()` (pq_dot − lagrangian) and JKD ingestion scalar (coherence − chaos − 0.5*darkTone + 0.3*voiceWeight − 0.2*whimsy) both produce `hamiltonian_energy` field. Two distinct producers assign different mathematical meanings to the same serialized field name.
- **Regression target:** Any fix must preserve both formulas as separate semantic entities. Must not conflate them. Must not create a third field that merges them.

#### R-13 — Default intent "understand" for 989/991 equations

- **Historical evidence (2026-10-27):** Default intent was visible in serialized training data. The issue crosses computational and data-generation boundaries.
- **Regression target:** Same as R-04. Any fix must derive intent or document the default.

#### R-14 — M3 Hamiltonian energy = 0.0

- **Historical evidence (2026-10-27):** `hamiltonian_energy` was zero in all 1,536 records of `full_shotgun_expansion_all.jsonl`. This was visible in actual serialized data before the November mathematical reproduction.
- **Historical evidence (2026-11-02):** Runtime verification confirmed: pq_dot (~0.01) − lagrangian (~1–5) < 0 → `_clamp(lo=0.0) = 0.0`. Avatar path with empty `line_balance` still produces L=2.1 (not 0). Both populated and empty paths produce H=0.0.
- **Regression target:** Any correction must explicitly define: (1) what pq_dot and lagrangian each measure, (2) whether they are commensurable, (3) what the intended range of H is, (4) what clamping behavior is correct. Must not force nonzero values. Must not change `_clamp()` bounds without semantic justification.

#### R-15 — M3→M6 degenerate complex-amplitude representation

- **Historical evidence (2026-11-02):** M6 imaginary amplitude is zero because M3 Hamiltonian contribution is zero. `imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)` produces 0 when H=0. 512/512 resolved states have `imag = 0`.
- **Regression target:** Any correction must address R-14 first. Must not fabricate imaginary components. Must not describe the result as "1-dimensional wavefunction."

#### R-16 — 3D PLY mesh provenance unverified

- **Historical evidence (2026-09-27):** Godot and OpenUSD world representations, 512/729 controllers, 64×729 topology, separate JSON topology artifacts already existed. The 512 PLY meshes are the latest in a chain of positional representations.
- **Regression target:** Any verification must trace the source-to-mesh lineage: hexagram identity → positional state → expansion variables → mesh-generation inputs → PLY geometry → Godot scene/kit model. Must not assume provenance from file existence alone.

#### R-17 — Ternary source lineage untraced

- **Historical evidence (2026-09-18):** 27 ternary trigrams, 729 ternary hexagrams, 5,832 resolved ternary states established as distinct state populations. Ternary decoding was to remain independent of binary representation.
- **Regression target:** Any verification must trace the generation path from `HEXAGRAM_BASE` through `kingwen_quantum_expand.py` to `ternary_full_expansion.json`. Must not assume canonical lineage from file existence alone.

#### R-18 — Corpus evidence cardinality unvalidated

- **Historical evidence (2026-10-27):** 1,536 JSONL records each have 20 corpus evidence items. No prior validation of whether these establish independent confirmation.
- **Regression target:** Any validation must distinguish independent confirmation from consistent cardinality. Must not upgrade unverified evidence based on count alone.

#### R-19 — Output differentiation unverified (50-line vs 30MB)

- **Historical evidence (2026-09-27):** Godot generator described a 64×729=46,656-node structure. Large outputs and small outputs were understood to serve different expansion/projection purposes.
- **Regression target:** Any comparison must document the distinct purpose of each output. Must not treat one as obsolete or redundant. Must not consolidate without verifying property preservation.

#### R-20 — Personality-subset intent unverified

- **Historical evidence (2026-11-02):** `personality_subsets` computed for expanded (phase=0) only. No explicit documentation in code of whether this is intentional.
- **Regression target:** Any documentation must state whether the phase=0-only computation is intentional and why. Must not assume intent from absence alone.

#### R-21 through R-27 — Intentional boundaries

- **Historical evidence (2026-09-18):** Expansion-first, no early collapse, deterministic generation, no pseudo-random substitution. Reductions (SVD/POD) to remain observational layers, not replacements for underlying state space.
- **Regression target:** Any remediation must preserve all seven boundaries. The no-collapse requirement is original architecture, not a recent audit interpretation.

---

## Section 4: Remediation Acceptance Criteria

For a remediation to be accepted as `PASSED`, it must satisfy ALL of the following criteria. Failure to satisfy any single criterion results in `FAILED` or `INCONCLUSIVE`.

### 4.1 Execution correctness

- The affected consumer(s) execute without error after the change.
- `py_compile` passes on all modified Python files.
- `npm run build` passes if any TypeScript/JavaScript files are modified.
- All affected consumer tests pass (not just the modified function's tests).
- No new errors are introduced (pre-existing errors are documented but not counted as new).

### 4.2 Semantic integrity

- The corrected output preserves the mathematical meaning of the original computation.
- No silent replacement of values (e.g., zero → nonzero without semantic justification).
- No conflation of distinct semantic entities (e.g., M3 Hamiltonian ≠ JKD scalar).
- No default value assignment without explicit provenance.
- No masking of computed values (e.g., `|| 0.75` replacing explicit zero).

### 4.3 Representation continuity

- All 7 intentional boundaries (INV-01 through INV-07) remain intact after the change.
- No collapse of distinct representations into a single format.
- No forced equivalence between binary and ternary state spaces.
- No consolidation of independent implementations.
- Per-hexagram identity preserved (64 hexagrams × 8 phases = 512 states minimum).
- Per-phase identity preserved (no cross-phase aggregation without evidence).

### 4.4 Provenance

- Source-to-consumer lineage is traceable for all modified outputs.
- Mesh provenance (if affected) is verified, not assumed.
- Ternary source lineage (if affected) is traced, not assumed.
- Corpus evidence cardinality (if affected) is validated, not assumed.
- Historical regression targets are met (from Section 3).

### 4.5 Evidence requirements

- All 8 steps of the verification protocol (Section 1) are completed.
- All evidence artifacts are saved in `docs/remediation_evidence/<entry_id>/`.
- Before-and-after comparison is documented with specific field/value changes.
- Boundary check confirms all 7 invariants intact.
- Disposition is recorded as `PASSED`, `FAILED`, or `INCONCLUSIVE` with justification.

---

## Section 5: Evidence and Disposition Requirements

### 5.1 Disposition categories

| Disposition | Definition | Required evidence |
|-------------|-----------|-------------------|
| `PASSED` | Failure resolved AND all 7 boundaries intact AND no unintended changes | Steps 1-8 complete, all tests green, before/after comparison shows only intended changes |
| `FAILED` | Change did not resolve failure OR introduced new failure OR broke a boundary | Steps 1-8 complete, specific failure documented, rollback recommended |
| `INCONCLUSIVE` | Insufficient evidence to determine pass/fail | Steps 1-8 partially complete, specific missing evidence identified, additional investigation specified |

### 5.2 Evidence artifact structure

For each remediation entry, the following files must exist in `docs/remediation_evidence/<entry_id>/`:

```
docs/remediation_evidence/<entry_id>/
├── original_behavior.md          # Step 1
├── correction_boundary.md        # Step 2
├── original/                     # Step 3
│   ├── <affected_file_1>.bak
│   ├── <affected_file_2>.bak
│   └── ...
├── test_results.txt              # Step 5
├── before_after.md               # Step 6
├── boundary_check.md             # Step 7
└── disposition.md                # Step 8
```

### 5.3 Evidence quality requirements

- All evidence must be reproducible: commands and inputs documented with enough detail to re-run.
- All evidence must be timestamped.
- All evidence must reference exact file paths and line numbers.
- All evidence must include observed output (not expected output).
- Evidence must distinguish between "test passed" and "test was not run."
- Evidence must distinguish between "field absent" and "field present but null/empty."

### 5.4 Historical regression evidence

Each remediation entry must include a `historical_regression_target` field in its disposition that references the specific historical evidence from Section 3. The target must state:

- What historical capability must remain functional after the change.
- What historical output must remain unchanged.
- What historical behavior must not be silently replaced.

### 5.5 Disposition reporting format

```
Entry: R-XX
Disposition: PASSED | FAILED | INCONCLUSIVE
Date: YYYY-MM-DD
Evidence path: docs/remediation_evidence/R-XX/
Historical regression target: <reference to Section 3>
Original failure: <one-line description>
Correction applied: <one-line description>
Boundaries verified: INV-01 through INV-07 (all PASS | specific failures listed)
Unintended changes: None | <list>
```

---

## Appendix A: Remediation Entry to Historical Evidence Cross-Reference

| Entry | Category | Historical Evidence | Historical Regression Target |
|-------|----------|-------------------|---------------------------|
| R-01 | Execution blocker | 2026-10-27 loader repair | Import resolution + downstream consumption verified |
| R-02 | Execution blocker | 2026-10-04 collapse pipeline; 2026-10-27 live producer repair | Canonical producer preserved; collapse remains historical |
| R-03 | Data omission | 2026-10-27 JSONL (empty text) | No fabricated request text |
| R-04 | Data omission | 2026-10-27 JSONL (default intent) | Intent derived or documented as default |
| R-05 | Data omission | 2026-09-18 expansion-first | Pre-slider capture preserved as phase=0 only |
| R-06 | Data omission | 2026-09-18 expansion-first | Personality subsets authoritative in expanded[] |
| R-07 | Data omission | 2026-09-18 expansion-first | Ternary slots authoritative in expanded[] |
| R-08 | Data omission | 2026-09-18 expansion-first | Schauberger parsing authoritative in expanded[] |
| R-09 | Data omission | 2026-09-18 expansion-first | Projections authoritative in expanded[] |
| R-10 | Data omission | 2026-09-18 expansion-first | Domain routing palette authoritative in expanded[] |
| R-11 | Semantic substitution | 2026-11-02 viewer reproduction | Zero vs absent distinction preserved |
| R-12 | Semantic substitution | 2026-11-02 field-name collision | M3 and JKD scalars remain separate |
| R-13 | Semantic substitution | 2026-10-27 default intent | Intent derived or documented as default |
| R-14 | Computational finding | 2026-10-27 serialized zeros; 2026-11-02 reproduction | Dimensional incompatibility documented, not silently fixed |
| R-15 | Computational finding | 2026-11-02 M6 reproduction | Degenerate amplitude documented, not fabricated |
| R-16 | Provenance gap | 2026-09-27 topology work | Source-to-mesh lineage traced, not assumed |
| R-17 | Provenance gap | 2026-09-18 ternary states | Ternary source lineage traced, not assumed |
| R-18 | Provenance gap | 2026-10-27 corpus evidence | Independent confirmation validated, not assumed |
| R-19 | Provenance gap | 2026-09-27 large/small outputs | Distinct purposes documented, not consolidated |
| R-20 | Provenance gap | 2026-11-02 personality audit | Intent documented, not assumed |
| R-21 | Intentional boundary | 2026-09-18 expansion-first | 729 permutations count-only preserved |
| R-22 | Intentional boundary | 2026-09-18 expansion-first | Schauberger phase=0 preserved |
| R-23 | Intentional boundary | 2026-09-18 expansion-first | Domain routing palette phase=0 preserved |
| R-24 | Intentional boundary | 2026-09-18 expansion-first | Projections phase=0 preserved |
| R-25 | Intentional boundary | 2026-09-18 expansion-first | Pre-slider phase=0 preserved |
| R-26 | Intentional boundary | 2026-09-18 ternary states | 9-bit ternary decoding unintegrated preserved |
| R-27 | Intentional boundary | 2026-09-18 expansion-first | Personality consensus aggregation preserved |

---

## Appendix B: Document Index

| Document | Purpose | Status |
|----------|---------|--------|
| `docs/shotgun-representation-consumer-continuity-audit.md` | 8-transition continuity audit | Complete |
| `docs/information-loss-remediation-register.md` | 27-entry remediation register | Complete |
| `docs/controlled-remediation-verification-protocol.md` | This document — verification protocol | Complete |
| `docs/M3_SCALE_MISMATCH_DIAGNOSIS.md` | M3 6-phase scale-mismatch diagnosis | Complete |
| `docs/shotgun-reinvention-audit.md` | Initial reinvention audit (superseded by integrity audit) | Complete |
| `docs/shotgun-authority-lineage-audit.md` | Canonical producer trace, 7 consumers, authority matrix | Complete |
| `docs/shotgun-expansion-integrity-audit.md` | Distributed expansion model, 9 capabilities | Complete |
| `docs/persona-personality-coder-agent-usage-audit.md` | Persona/personality/coder/agent usages | Complete |
| `docs/BENCHMARKS_RULES_ONBOARDING_README_AUDIT_2026-11-02.md` | Benchmarks/rules/onboarding/README audit | Complete |

---

## Specification Scope Summary

- **No source modifications** authorized by this document.
- **No formula changes** authorized.
- **No destructive normalization or collapse** authorized.
- **No forced equivalence** between representations.
- **No deletion or consolidation** of independent implementations.
- **Preserve unique capabilities and historical outputs.**
- **Gate 2 remains OPEN.**
- **QSMC-1's original nine-document baseline remains frozen.**
- Each remediation entry links to both original failure evidence and historical regression target.
- 7 intentional boundaries must be checked during every remediation.
- Disposition categories: `PASSED`, `FAILED`, `INCONCLUSIVE`.
- Evidence artifacts saved in `docs/remediation_evidence/<entry_id>/`.