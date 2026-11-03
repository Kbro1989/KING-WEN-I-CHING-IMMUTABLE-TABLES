# Research-to-Test Traceability Matrix

**Date:** 2026-10-29
**Purpose:** Consolidate six research documents into a single traceable matrix. Maps each research claim to King Wen invariant, producer/transformation/consumer, evidence, falsifiable test, expected result, failure condition, and decision authority. No runtime code changes.
**Canonical engine:** `emotional_engine.py` at git revision `71fbf28f8e92c6a7de74c50a304906ef81963a7d`
**Gate 2:** OPEN. No representation choice, Path A/B, or invalid-input policy authorized.

---

## Three Audit Questions (from Polymorphism Is Rotation)

1. **Representation fidelity**: Did a transformation preserve the source identity and meaningful information?
2. **Evaluation validity**: Does the chosen metric actually measure the property being claimed?
3. **Uncertainty calibration**: Does the system distinguish verified results, estimates, defaults, and unresolved states?

---

## Matrix: Research Claim → Testable Invariant

### Section 1: Representation Fidelity

| ID | Research Source | Claim | King Wen Invariant | Producer | Transformation | Consumer | Evidence Available | Falsifiable Test | Expected Result | Failure Condition | Decision Authority |
|----|----------------|-------|-------------------|----------|----------------|----------|-------------------|-------------------|-----------------|-------------------|-------------------|
| RF-1 | Polymorphism Is Rotation | Geometric similarity ≠ functional equivalence | `(hexagram_id, phase_bits)` identity is canonical, not vector similarity | `expand_hexagram()` in `emotional_engine.py` | Binary→phase expansion (64→512) | Voice, 3D, routing | 29 duplicate expanded_vector groups, all within same hexagram | Given two records with identical expanded_vector, assert they have distinct `(hexagram_id, phase_bits)` | No cross-hexagram identity collapse | Any record where same vector maps to different hexagram_id | Audit-level (no Gate 2) |
| RF-2 | Polymorphism Is Rotation | Determinism ≠ correctness | Identical inputs produce identical outputs (necessary but not sufficient) | `shotgun_expand()` in `scripts/full_hexagram_shotgun.py` | Full expansion (64 expanded + 512 resolved) | All downstream | SHA-256 hash match across runs (reported) | Run `shotgun_expand()` 3× with identical inputs; assert hash equality; assert hash differs when input changes | Hash stable for same input, different for different input | Hash instability OR hash collision (same hash, different input) | Audit-level |
| RF-3 | Polymorphism Is Rotation | Structural identity alone insufficient | Field-level conservation: all required keys present in every record | `capture_pre_slider()` in `emotional_engine.py` | Per-hexagram value extraction | All downstream | Audit: 8 phase types × 64 = 512, all required fields present, 482 distinct expanded vectors | Assert every resolved record has non-null `hexagram_id`, `phase_bits`, `expanded_vector`, `resolved_vector`, `line_states`, `porosity`, `inject_site` | 512/512 records with all required fields non-null | Any null required field | Audit-level |
| RF-4 | Polymorphism Is Rotation | Alignment must preserve original | Provenance chain immutable through pipeline | `math_to_kingwen_adapter.py` `build_request_text()` | Equation→King Wen expansion | Fixture JSON | Fixture: 6 provenance fields (paper_id, equation_index, extraction_method, recovery_status, source_url, file_hash) | Assert all 6 provenance fields non-null for every equation in regression report (991/991) | 991/991 with complete provenance | Any null provenance field | Audit-level |
| RF-5 | Polymorphism Is Rotation | Consumer integrity separate from structural | Downstream output matches input identity | `kingwen_voice_router.py`, `cartesia_adapter.py`, `kingwen_oracle_consult_tool.py` | Consult/voice/3D consumption | Voice, 3D, routing | No consumer tests exist | Given input (hexagram_id, phase_bits, emotional_vector), assert downstream output is deterministic function of input | Deterministic, identity-preserving output | Non-deterministic output OR identity mismatch | Audit-level (consumer access required) |
| RF-6 | In-Context Reward Adaptation | Binary preference insufficient → need magnitude | Binary line (0/1) → ternary (0/1/2) → five-valued (0-4) adds magnitude progressively | `expand_hexagram()` in `emotional_engine.py` | Binary→phase→ternary→yao | Emotional vector | 9-term yao vocabulary intact; 5-valued differential model exists | Assert each pipeline stage adds information (state count increases: 64→512→729→15,625) without losing identity | Monotonic state count increase, identity preserved at each stage | State count decrease or identity loss at any stage | Gate 2 (representation choice) |

### Section 2: Evaluation Validity

| ID | Research Source | Claim | King Wen Invariant | Producer | Transformation | Consumer | Evidence Available | Falsifiable Test | Expected Result | Failure Condition | Decision Authority |
|----|----------------|-------|-------------------|----------|----------------|----------|-------------------|-------------------|-----------------|-------------------|-------------------|
| EV-1 | TUR-DPO | Structural validity ≠ semantic fidelity | `matched_intents` empty ≠ successful classification | `extract_intent()` in `emotional_engine.py` | Text→intent routing | Adapter fixture | 989/991 equations (99.8%) default-routed to "understand"; `matched_intents` empty | Assert `matched_intents` is empty list (not null) when no keywords match; assert `dominant_intent` defaults to "understand" only when no match | Empty list recorded, default intent assigned | `matched_intents` null OR default intent reported as classified | Audit-level |
| EV-2 | TUR-DPO | Multi-dimensional evaluation needed | Structural, semantic, and task success are distinct criteria | `math_to_kingwen_adapter.py` regression report | Per-equation 5-criteria assessment | Regression report | 5 criteria tracked (extraction, recovery, routing, identity, provenance); no semantic-fidelity or consumer-satisfaction criteria | Add 2 criteria to regression report: (a) semantic fidelity (math terms in query_tokens are meaningful, not LaTeX artifacts), (b) consumer satisfaction (downstream can use the output) | Report has 7 criteria with explicit pass/fail per equation | Report conflates structural pass with semantic pass | Audit-level |
| EV-3 | In-Context Reward Adaptation | Binary preference insufficient → need magnitude | Hamiltonian energy must be informative (not universally 0.0) | `_hamiltonian_energy()` in `emotional_engine.py` | pq_dot - lagrangian → clamp | Wavefunction, rotation, scale | All 512 states produce 0.0; pq_dot 0.005-0.013, lagrangian 2.1-5.1, gap ≥2.09 | Assert energy ≠ 0.0 for at least one state, OR document 0.0 as valid energy with explicit justification | Nonzero energy OR documented justification for zero | Universal 0.0 without documented justification | Hamiltonian contract (Gate 2 adjacent) |
| EV-4 | TUR-DPO | Evaluation must distinguish verified/estimate/default/unresolved | `dominant_intent: understand` must be classified as default, not verified | `extract_intent()` in `emotional_engine.py` | Text→intent routing | Adapter fixture, regression report | 989/991 default-routed; `matched_intents` empty | Assert regression report distinguishes "classified" (matched_intents non-empty) from "defaulted" (matched_intents empty) | Separate counts: classified vs defaulted | Single count conflating classified and defaulted | Audit-level |
| EV-5 | Polymorphism Is Rotation | Checks can pass by construction | "512 output records" ≠ "512 correct records" | `math_to_kingwen_adapter.py` regression report | Per-equation accounting | Regression report | 991/991, 0 errors reported | Assert regression report includes semantic-fidelity column (not just structural pass/fail) | Report has semantic column with per-equation values | Report has only structural columns | Audit-level |
| EV-6 | Polymorphism Is Rotation | Adversarial tests needed | Misleading similarities, missing fields, altered inputs must expose false passes | All pipeline stages | All transformations | All consumers | No adversarial tests exist | Create test inputs with: (a) missing required fields, (b) altered equation indices, (c) misleadingly similar vectors; assert pipeline fails or flags appropriately | Pipeline rejects or flags adversarial inputs | Pipeline silently accepts adversarial inputs as valid | Audit-level |

### Section 3: Uncertainty Calibration

| ID | Research Source | Claim | King Wen Invariant | Producer | Transformation | Consumer | Evidence Available | Falsifiable Test | Expected Result | Failure Condition | Decision Authority |
|----|----------------|-------|-------------------|----------|----------------|----------|-------------------|-------------------|-----------------|-------------------|-------------------|
| UC-1 | TUR-DPO | Uncertainty must be explicit, not hidden behind defaults | Default "understand" intent must be reported as uncertainty | `extract_intent()` in `emotional_engine.py` | Text→intent routing | Adapter, regression report | 989/991 default-routed (99.8%) | Assert regression report has separate `classified_count` and `defaulted_count` fields | Both counts present and sum to total | Single `routing_pass` count conflating both | Audit-level |
| UC-2 | TUR-DPO | `emotional_input` should not become uncertainty weight without contract | emotional_input slider modulates porosity, not uncertainty | `shotgun_expand()` in `scripts/full_hexagram_shotgun.py` | Slider→porosity modulation | All downstream | Porosity 0-4 integer, bleed = porosity_norm × 0.7 | Assert emotional_input is documented as porosity modulator, not uncertainty weight, OR establish explicit contract for uncertainty interpretation | Documented contract exists | emotional_input used as uncertainty weight without contract | Hamiltonian/porosity contract (Gate 2 adjacent) |
| UC-3 | TUR-DPO | Reasoning topology must be observable | Transformation sequence must be traceable with intermediate states retained | `math_to_kingwen_adapter.py`, `shotgun_expand()`, `capture_pre_slider()` | Full pipeline (arxiv→fixture→expansion→resolved) | All downstream | Provenance chain: 6 fields (paper_id, equation_index, extraction_method, recovery_status, source_url, file_hash) | Assert intermediate states (MathML tree, recovered LaTeX, extracted features) are retained as first-class provenance, not just final fixture | Intermediate states present in fixture or separate provenance file | Only final fixture retained; intermediate states lost | Audit-level |
| UC-4 | TUR-DPO | Uncertainty-weighted objective needs explicit calibration | Any uncertainty weight must have documented assumptions and failure tests | N/A (no uncertainty weight currently exists) | N/A | N/A | No uncertainty weight in current pipeline | Assert no uncertainty weight is introduced without explicit contract and independent validation | No uncertainty weight without contract | Uncertainty weight introduced without contract | Gate 2 (representation choice) |
| UC-5 | In-Context Reward Adaptation | Binary preference insufficient → need magnitude | Yao vocabulary (young/old/stable) adds magnitude to binary direction | `expand_hexagram()` in `emotional_engine.py` | Binary→yao (strength dimension) | Emotional vector | 9-term yao vocabulary intact | Assert yao strength is tracked separately from binary direction in every resolved record | Both binary and yao fields present and distinct | Yao collapsed into binary or binary lost | Gate 2 (representation choice) |
| UC-6 | Polymorphism Is Rotation | Alignment must be separate experimental layer | Geometric alignment must not overwrite canonical state | N/A (no alignment currently exists) | N/A | N/A | No alignment transformation in current pipeline | Assert any future alignment lives in separate analysis layer with original vectors preserved | Alignment in separate layer, originals preserved | Alignment overwrites canonical vectors | Hamiltonian contract (Gate 2 adjacent) |

---

## Cross-Cutting: Hamiltonian Energy

| ID | Research Source | Claim | King Wen Invariant | Producer | Transformation | Consumer | Evidence Available | Falsifiable Test | Expected Result | Failure Condition | Decision Authority |
|----|----------------|-------|-------------------|----------|----------------|----------|-------------------|-------------------|-----------------|-------------------|-------------------|
| H-1 | Hamiltonian audit (2026-10-29) | Energy is zero-by-construction (scale mismatch) | Energy must be informative, not universally 0.0 | `_hamiltonian_energy()` in `emotional_engine.py` | pq_dot - lagrangian → clamp | Wavefunction, rotation, scale | pq_dot 0.005-0.013, lagrangian 2.1-5.1, gap ≥2.09, 64/64 paired comparisons, all 512 states = 0.0 | Assert energy value is recorded (not null) for every (hexagram_id, phase_bits); assert energy ≠ 0.0 OR document 0.0 as valid with justification | Nonzero energy OR documented justification | Universal 0.0 without documented justification | Hamiltonian contract |
| H-2 | Hamiltonian audit | Diagnostic retention loses 63/64 hexagrams | Paired-differential evidence must retain (hexagram_id, phase_bits) identity | `_hamiltonian_energy()` | Per-hexagram computation → global dict | `verify_restored_state.py` (print-only) | Global dict: last-write-wins (hex 64, phase 0 only); one print-only consumer | Assert global dict contains all 64 hexagram values after full run, OR document as last-write-wins diagnostic | All 64 values OR documented limitation | Silent data loss without documentation | Hamiltonian contract |
| H-3 | Hamiltonian audit | Terms are incommensurable without normalization | pq_dot and lagrangian must share common scale before subtraction | `_hamiltonian_energy()` | pq_dot (vector-scale) - lagrangian (line-count-scale) | Energy output | Gap ≥ 2.09 in all 64 paired comparisons | Assert pq_dot and lagrangian are on common scale before subtraction, OR assert scale mismatch is documented | Common scale OR documented mismatch | Subtraction of incommensurable terms without documentation | Hamiltonian contract |
| H-4 | Hamiltonian audit | Clamp floors all negative to zero | Clamp behavior must be documented as physical constraint, normalization, or safety bound | `_clamp()` in `emotional_engine.py` | raw → clamped [0,1] | Energy output | raw ∈ [-5.1, -0.49] (always negative); clamp → 0.0 | Assert clamp behavior is documented with explicit justification, OR assert clamp output is not universally 0.0 | Documented justification OR nonzero output | Undocumented universal clamping | Hamiltonian contract |

## Cross-Cutting: Cross-Representation Consistency (from Enhanced EWC)

| ID | Research Source | Claim | King Wen Invariant | Producer | Transformation | Consumer | Evidence Available | Falsifiable Test | Expected Result | Failure Condition | Decision Authority |
|----|----------------|-------|-------------------|----------|----------------|----------|-------------------|-------------------|-----------------|-------------------|-------------------|
| CR-1 | Enhanced EWC (arXiv 2605.30323) | Local correctness ≠ relational correctness | Canonical identity preserved across all derived artifacts (voice, 3D, avatar, consult) | `shotgun_expand()` in `scripts/full_hexagram_shotgun.py` | Full expansion (64 expanded + 512 resolved) | Voice, 3D, routing, avatar | No consumer-boundary tests exist yet | Given canonical output (hexagram_id, phase_bits, emotional_vector), assert every downstream consumer output is a deterministic function of input | Deterministic, identity-preserving output | Non-deterministic output OR identity mismatch | Audit-level (consumer access required) |
| CR-2 | Enhanced EWC | Preserve relationships, not just individual values | Relationships between identity, phase, vectors, voice, avatar must remain stable across consumer repairs | `kingwen_voice_router.py`, `cartesia_adapter.py`, `kingwen_oracle_consult_tool.py` | Consult/voice/3D consumption | Voice, 3D, routing, avatar | No relationship-invariant tests exist | Record (identity, phase, vector) → (consumer output) mapping before repair; assert same mapping after repair | Same mapping before and after | Changed mapping without documented justification | Audit-level (consumer access required) |
| CR-3 | Enhanced EWC | Permitted variation must be distinguished from corruption | Geometric/semantic differences across phases are expected; identity/provenance mismatch is corruption | `kingwen_avatar_meshes/` (512 PLY files) | Phase-specific mesh generation | 3D avatar | No manifest mapping file→(hexagram_id, phase_bits) | Assert each PLY file maps to exactly one (hexagram_id, phase_bits) in manifest; assert mesh geometry differs across phases for same hexagram | 512/512 mapped, phase-specific geometry | Unmapped file OR identical geometry across phases | Audit-level (consumer access required) |
| CR-4 | Enhanced EWC | Change isolation: each repair preserves unaffected outputs | Consumer repair must not alter outputs outside its scope | `kingwen_engine_adapter.py` (cannot load) | Adapter boundary restoration | All OpenJarvis consumers | No before-and-after comparison exists | Record consumer outputs before repair; assert only expected fields change after repair | Only targeted fields change | Unintended field changes in unaffected consumers | Audit-level (consumer access required) |
| CR-5 | Enhanced EWC | Measurement validity: scores must measure intended relationship, not numerical similarity | Consistency must be exact identity/provenance match, not cosine similarity or aggregate score | All consumer boundaries | All transformations | All consumers | No consistency measurement exists | Assert any consistency metric is defined in terms of exact identity match, not aggregate similarity | Exact match or documented mismatch | Aggregate similarity substituted for exact match | Audit-level (no Gate 2) |

---

| Decision Authority | Items | Count |
|-------------------|-------|-------|
| Audit-level (no Gate 2) | RF-1, RF-2, RF-3, RF-4, RF-5, EV-1, EV-2, EV-4, EV-5, EV-6, UC-1, UC-3, CR-5 | 13 |
| Hamiltonian contract (Gate 2 adjacent) | EV-3, UC-2, UC-6, H-1, H-2, H-3, H-4 | 7 |
| Gate 2 (representation choice) | RF-6, UC-4, UC-5 | 3 |
| Consumer access required | RF-5, CR-1, CR-2, CR-3, CR-4 | 5 |

**Total unique items: 27.** RF-5 appears in both Audit-level and Consumer access required (one overlap). CR-5 is audit-level only. No phantom IDs remain (E1-E4 references removed — those IDs do not exist in the matrix).

---

## Key Test: Default Intent Distinguishability

**Question**: Does the pipeline distinguish an explicitly classified intent from a fallback assignment?

**Current state**: 989/991 equations (99.8%) receive `dominant_intent: "understand"` via default. `matched_intents` is empty for all 989. The regression report counts routing as passing (956/991 = 96.5%).

**Falsifiable test**: 
1. Run regression report with explicit `classified_count` and `defaulted_count` fields.
2. Assert `classified_count + defaulted_count == total_equations`.
3. Assert `classified_count` equals count of equations where `matched_intents` is non-empty.
4. Assert `defaulted_count` equals count of equations where `matched_intents` is empty.

**Expected result**: `classified_count` = 2, `defaulted_count` = 989, total = 991.

**Failure condition**: `classified_count` reported as 991 (conflating default with classification) OR `defaulted_count` not reported.

**Decision authority**: Audit-level (no Gate 2). This test establishes whether the evaluation framework distinguishes verified from default.

---

## Key Test: emotional_input as Uncertainty Weight

**Question**: Can `emotional_input` be interpreted as an uncertainty weight?

**Current state**: `emotional_input` modulates porosity via `bleed = porosity_norm * 0.7` where `porosity_norm = porosity_index / 4.0`. It is a porosity modulator, not an uncertainty weight.

**Falsifiable test**:
1. Document current `emotional_input` semantics: porosity modulator, range 0-100, phase-gated sensitivity.
2. Assert no code path uses `emotional_input` as an uncertainty weight without explicit contract.
3. Assert any proposed uncertainty interpretation includes: stated assumptions, independent validation, and failure tests.

**Expected result**: `emotional_input` remains documented as porosity modulator; no uncertainty weight introduced without contract.

**Failure condition**: `emotional_input` used as uncertainty weight without contract, or porosity modulation changed without documentation.

**Decision authority**: Hamiltonian/porosity contract (Gate 2 adjacent). This requires explicit semantic definition before implementation.

---

## Disposition

- **No source code was modified.** This is a documentation-only traceability matrix.
- **Gate 2 remains OPEN.** No representation choice, Path A/B, or invalid-input policy authorized.
- **Canonical engine protected.** No formula change, normalization, or cross-hexagram merging.
- **Geometric alignment remains a separate experimental layer.** No canonical normalization follows from research papers.
- **Research can motivate tests, but does not authorize changes to canonical state, representation semantics, or the Hamiltonian.**