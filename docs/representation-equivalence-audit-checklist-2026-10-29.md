# Representation-Equivalence Audit Checklist

**Date:** 2026-10-29
**Purpose:** Read-only audit checklist for the King Wen pipeline. Identifies exactly where representation-equivalence tests belong. No source code changes.
**Basis:** Polymorphism Is Rotation (McCann, arXiv:2605.30323v1) — methodological framework for distinguishing geometric similarity from functional equivalence.
**Canonical engine:** `emotional_engine.py` at git revision `71fbf28f8e92c6a7de74c50a304906ef81963a7d`
**Gate 2:** OPEN. No representation choice, Path A/B, or invalid-input policy authorized.

---

## Three Audit Questions

### Q1: Identity Preservation

> Does every transformation preserve the original `(hexagram_id, phase_bits)` and its provenance?

### Q2: Functional Equivalence

> When two records look identical under a chosen metric, do they actually produce equivalent downstream behavior under matched inputs?

### Q3: Information Loss

> Can a transformation merge, discard, or obscure distinctions that a downstream consumer needs?

---

## Checklist

### A. Expansion Pipeline: shotgun_expand() → capture_pre_slider()

| # | Transformation | Source Function | Destination Function | Source Keys | Destination Keys | Identity Preserved? | Evidence | Test Required | Status |
|---|----------------|-----------------|---------------------|-------------|-----------------|---------------------|----------|---------------|--------|
| A1 | Hexagram expansion | `shotgun_expand()` in `scripts/full_hexagram_shotgun.py` | `capture_pre_slider()` in `emotional_engine.py` | `hexagram_id`, `phase_bits`, `binary`, `ternary`, `intent`, `expanded_vector`, `resolved_vector`, `line_states`, `yao_vocabulary`, `porosity`, `inject_site`, `sample_paths`, `training_notes`, `projections`, `schauberger_parsing`, `personality_subsets`, `ternary_slots` | Same keys retained | YES — identity keys `(hexagram_id, phase_bits)` present in all 512 resolved records | Audit: 512 resolved records, 8 phase types × 64 = 512, SHA-256 hash match across repeated runs | Unit test: assert every resolved record has `hexagram_id` and `phase_bits`; assert no record has null identity keys | NOT YET VERIFIED |
| A2 | Consensus collapse (REMOVED) | `_compute_consensus_from_resolved()` | `capture_pre_slider()` (patched) | 512 resolved records | 512 resolved records returned directly, `consensus=None` | YES — collapse removed; per-hexagram values preserved | Audit: capture_pre_slider patched to return 64 expanded + 512 resolved, consensus=None | Regression test: assert `result["consensus"] is None` and `len(result["resolved"]) == 512` | NOT YET VERIFIED |
| A3 | Vector identity | `expand_hexagram()` in `emotional_engine.py` | Resolved record `expanded_vector` and `resolved_vector` | 5-axis vectors per (hexagram, phase) | Same 5-axis vectors | PARTIAL — 29 duplicate expanded_vector groups exist, all within same hexagram (different phases). No cross-hexagram duplicates. | Audit: 482 distinct expanded vectors, 29 duplicate groups (59 records), 448 records where resolved ≠ expanded | Test: assert no cross-hexagram vector duplicates; assert within-hexagram duplicates have distinct phase_bits | NOT YET VERIFIED |
| A4 | Phase coverage | `shotgun_expand()` | Resolved records | 8 phases per hexagram | 8 phase types: past, present, future, transition, resolution, dissolution, crystallization, void | YES — 8 types × 64 = 512, 64 each | Audit: 8 phase types, 64 each, 512 total | Test: assert all 8 phase types present for every hexagram_id | NOT YET VERIFIED |

### B. Voice / Porosity Subsystem

| # | Transformation | Source Function | Destination Function | Source Keys | Destination Keys | Identity Preserved? | Evidence | Test Required | Status |
|---|----------------|-----------------|---------------------|-------------|-----------------|---------------------|----------|---------------|--------|
| B1 | Porosity normalization | `HEXAGRAM_INJECTION_SITE[hex_id]["porosity"]` (0-4 int) | `emotional_engine.py` line 651-666 | `porosity_index` (0-4) | `porosity_norm = porosity_index / 4.0` (0.0-1.0) | YES — identity key unchanged; porosity is a modulator, not identity | Audit: porosity distribution 2+18+22+12+10=64; porosity_norm trace confirmed | Test: assert porosity_norm ∈ [0.0, 1.0] for all 64 hexagrams; assert no hexagram has porosity_norm outside range | NOT YET VERIFIED |
| B2 | Bleed modulation | `porosity_norm` | `_pool_weights_for_hex()` | `porosity_norm` (0.0-1.0) | `bleed = porosity_norm * 0.7` | YES — hexagram identity preserved; bleed is a weight, not identity | Audit: phase-gated sensitivity (phases 0-2 none, phases 3-7 thresholded at emo≥25/75/100) | Test: assert bleed ∈ [0.0, 0.7] for all phases; assert phases 0-2 have bleed=0 regardless of porosity | NOT YET VERIFIED |
| B3 | Voice pool lookup | `VOICEBOX_VOICE_POOL` (64×5D) | `emotional_engine.py` | `hexagram_id` → 5D tuple | 5D vector (voiceWeight, coherence, chaos, whimsy, darkTone) | YES — hexagram_id is the lookup key; voice pool is canonical data | Audit: 64 entries, 5D tuples, porosity separate | Test: assert every hexagram_id maps to exactly one 5D tuple; assert no null or missing entries | NOT YET VERIFIED |
| B4 | Voice router | `kingwen_voice_router.py` | `_oracle_speak.py` | Consult payload + user text | Router result injected into consult payload as `_voice_router` | PARTIAL — router result injected but no test verifies downstream consumer behavior | Code review: `_ensure_voice_router()` singleton, result injected into payload | Test: matched inputs → verify router result fields present in payload; verify voice output varies with emotional vector | NOT YET VERIFIED |

### C. Math-to-King-Wen Adapter

| # | Transformation | Source Function | Destination Function | Source Keys | Destination Keys | Identity Preserved? | Evidence | Test Required | Status |
|---|----------------|-----------------|---------------------|-------------|-----------------|---------------------|----------|---------------|--------|
| C1 | Equation extraction | `arxiv_html_parser.py` (MathML tree walk) | `math_to_kingwen_adapter.py` `build_request_text()` | `equation_source` (original LaTeX verbatim) | `equation_source` (preserved verbatim) | YES — equation index and source URL tracked separately from semantic content | Adapter: equation_source preserved in fixture | Test: assert fixture `equation_source` equals arxiv HTML x-tex annotation verbatim | NOT YET VERIFIED |
| C2 | Feature separation | `e2e_2605.00155.json` (991 equations) | Adapter fixture | `context_before`, `context_after`, `symbols`, `context_keywords` | `equation_source`, `equation_features`, `prose_context` (three separate fields) | YES — three fields separated; equation index stripped from request_text via `re.sub(r"\b\d+(\.\d+)*\b", "", ctx)` | Adapter: tokenization fix verified; `\delta` → `delta` (no spurious `4`) | Test: assert `query_tokens` contains no numeric section references; assert three fields are non-empty and distinct | NOT YET VERIFIED |
| C3 | Provenance tracking | Adapter `build_request_text()` | Fixture JSON | `paper_id`, `equation_index`, `extraction_method`, `recovery_status`, `source_url`, `file_hash` | Same provenance fields in fixture | YES — all 6 provenance fields present in every fixture | Fixture: provenance chain complete for equation 0 | Test: assert all 6 provenance fields non-null for every equation in regression report | NOT YET VERIFIED |
| C4 | Expansion integrity | `shotgun_expand()` | Adapter fixture | 64 expanded, 512 resolved | `expanded_count=64`, `resolved_count=512`, `expanded_unique_hexagrams=64`, `resolved_unique_identities=512` | YES — cardinality and identity preserved | Regression: 991/991 equations, identity 991/991 | Test: assert expanded_count=64 and resolved_count=512 for every equation; assert expanded_unique_hexagrams=64 | NOT YET VERIFIED |
| C5 | Routing transparency | `extract_intent()` in `emotional_engine.py` | Adapter fixture | `matched_intents`, `dominant_intent` | `matched_intents` (empty for math terms), `dominant_intent` (default "understand") | PARTIAL — empty matched_intents correctly recorded (not falsely reported as match); default routing is transparent but not semantically classified | Regression: 989/991 default-routed (99.8%) | Test: assert `matched_intents` is empty list (not null) when no keywords match; assert `dominant_intent` defaults to "understand" | NOT YET VERIFIED |
| C6 | Recovery tracking | `math_recovery_tool.py` (LaTeX→SymPy) | Adapter regression report | `recovery_status` (recovered/unrecovered) | `recovery_status` in per-equation report | YES — recovery status tracked per equation | Regression: 448/991 recovered (45.2%) | Test: assert recovery_status is one of {recovered, unrecovered}; assert recovered count matches SymPy parse success | NOT YET VERIFIED |

### D. Hamiltonian Energy Subsystem

| # | Transformation | Source Function | Destination Function | Source Keys | Destination Keys | Identity Preserved? | Evidence | Test Required | Status |
|---|----------------|-----------------|---------------------|-------------|-----------------|---------------------|----------|---------------|--------|
| D1 | Energy calculation | `_hamiltonian_energy()` in `emotional_engine.py` | `HAMILTONIAN_PAIRED_DIFFERENTIALS` global dict | `resolved_vector`, `expanded_vector`, `line_balance` | `pq_dot`, `lagrangian`, `energy` (always 0.0) | YES — identity not lost, but energy is uninformative (0.0 for all 512 states) | Audit: pq_dot 0.005-0.013, lagrangian 2.1-5.1, gap ≥2.09, 64/64 paired comparisons | Test: assert energy is computed (not null); assert energy value is recorded for every (hexagram_id, phase_bits) | NOT YET VERIFIED |
| D2 | Diagnostic retention | `_hamiltonian_energy()` | `HAMILTONIAN_PAIRED_DIFFERENTIALS` (module-level global) | Per-hexagram paired values | Last-write-wins (hex 64, phase 0 only) | NO — earlier hexagram values are overwritten and lost | Audit: one print-only consumer (`verify_restored_state.py` line 19); no production code reads global | Test: assert global dict contains all 64 hexagram values after full run, OR assert documented as last-write-wins diagnostic | NOT YET VERIFIED |
| D3 | Scale commensurability | `pq_dot` (vector-scale ~0.01) | `lagrangian` (line-count-scale ~2-5) | pq_dot ∈ [0.005, 0.013] | lagrangian ∈ [2.1, 5.1] | N/A — terms are incommensurable (different scales) | Audit: gap ≥ 2.09 in all 64 paired comparisons | Test: assert pq_dot and lagrangian share a common scale before subtraction, OR assert scale mismatch is documented | NOT YET VERIFIED |
| D4 | Clamp behavior | `raw = pq_dot - lagrangian` | `_clamp(raw, 0.0, 1.0)` | raw ∈ [-5.1, -0.49] (always negative) | 0.0 (floors all negative to zero) | N/A — clamp erases all information | Audit: all 512 states produce 0.0 | Test: assert clamp output is not universally 0.0, OR assert 0.0 is documented as valid energy | NOT YET VERIFIED |

### E. Downstream Consumers

| # | Consumer | Source | Input Fields | Output Behavior | Identity Preserved? | Evidence | Test Required | Status |
|---|----------|--------|-------------|-----------------|---------------------|----------|---------------|--------|
| E1 | Voice router | `kingwen_voice_router.py` | Consult payload + user text | Router result injected into payload as `_voice_router` | PARTIAL — router result present but no test verifies voice output varies with emotional vector | Code review: `_ensure_voice_router()` singleton | Test: matched inputs → verify router result fields present; verify voice output varies with emotional vector | NOT YET VERIFIED |
| E2 | Voicebox adapter | `cartesia_adapter.py` | 5-axis emotional vector + trajectory + porosity | Discrete Cartesia API call (voice_id, speed, emotion tags) | NOT TESTED — no test verifies voice output matches input vector | Code review: adapter wired into `cartesia_tts.py` dual path | Test: given emotional vector V, assert voice_id/speed/emotion tags are deterministic function of V | NOT YET VERIFIED |
| E3 | 3D avatar | `kingwen_avatar_meshes/` (512 PLY files) | Hexagram + phase → PLY mesh | 3D mesh rendering | NOT TESTED — no test verifies mesh geometry matches hexagram state | File inventory: 512 PLY files (64×8) | Test: given hexagram_id + phase_bits, assert correct PLY file loaded; assert mesh vertex count > 0 | NOT YET VERIFIED |
| E4 | OpenJarvis consult | `kingwen_oracle_consult_tool.py` | `shotgun_expand()` output | Consultation record with save-string lineage | PARTIAL — tool registered, no test verifies output matches input | Code review: tool wraps `consult()` from adapter | Test: matched inputs → verify consult output preserves (hexagram_id, phase_bits) and save-string lineage | NOT YET VERIFIED |

---

## Summary

| Category | Items | Not Yet Verified | Passing (Reported) |
|----------|-------|-----------------|-------------------|
| A. Expansion pipeline | 4 | 4 | 0 |
| B. Voice / porosity | 4 | 4 | 0 |
| C. Math adapter | 6 | 6 | 0 |
| D. Hamiltonian energy | 4 | 4 | 0 |
| E. Downstream consumers | 4 | 4 | 0 |
| **Total** | **22** | **22** | **0** |

**No item is marked as passing.** All items require explicit verification before status changes. Determinism and structural agreement alone do not establish correctness (per Polymorphism Is Rotation methodological lesson).

### Key Gaps

1. **No downstream consumer tests exist.** Voice, 3D avatar, and OpenJarvis consult have no tests verifying that output matches input.
2. **No functional-equivalence tests.** The 29 duplicate expanded_vector groups are structurally identified but not tested for downstream behavioral equivalence.
3. **No adversarial tests.** No test checks whether misleading similarities, missing fields, or altered inputs expose false passes.
4. **Hamiltonian energy is uninformative.** 0.0 for all states; diagnostic retention loses 63 of 64 hexagrams.

### Recommended Next Steps

1. **Identity preservation tests first** (A1, A3, A4, B1, C1, C3, C4) — these are the cheapest to write and establish the baseline invariant.
2. **Functional-equivalence tests second** (A3 downstream behavior, E1-E4) — these require consumer access but establish whether structural duplicates are functionally redundant.
3. **Information-loss tests third** (C2, C5, D1-D4) — these require understanding of intended semantics and may need the Hamiltonian contract first.
4. **Adversarial tests last** (all categories) — these require the above three to be established first.

### F. Identity Alphabet & Relationship Registry (from external assessment 2026-10-29)

| # | Item | Expectation | Evidence Required | Status |
|---|------|-------------|-------------------|--------|
| F1 | Ternary `2` semantic definition | Value `2` must have a defined meaning for the particular system (changing-line sentinel in King Wen); must not be assumed to mean the same thing in every mathematical domain | Documented definition in `kingwen_ternary_tables_complete.py` + per-domain contract | NOT YET VERIFIED |
| F2 | Encoding ≠ definition | `1a` (or any composite code) has no inherent meaning merely because it exists; meaning comes from versioned definition, structure, relationships, domain contract | Canonical symbol-and-relationship registry with versioned definitions | NOT YET VERIFIED |
| F3 | Vector identity ≠ entity identity | Two entities with identical vectors can remain distinct (different identities, histories, inputs, phase states); vector equality must not collapse identity | Test: assert two records with identical `expanded_vector` but different `(hexagram_id, phase_bits)` are treated as distinct entities | NOT YET VERIFIED |
| F4 | Inversion as explicit operation | Inversion (reverse position ordering) must be implemented as explicit operation with testable invariants, not conflated with complement | Test: assert `invert(invert(x)) == x` (involution); assert inversion and complement produce different results for at least one input | NOT YET VERIFIED |
| F5 | Complement as explicit operation | Complement (flip each binary value) must be implemented as explicit operation with testable invariants, distinct from inversion | Test: assert `complement(complement(x)) == x` (involution); assert complement and inversion produce different results for at least one input | NOT YET VERIFIED |
| F6 | Symbol-and-relationship registry | Canonical versioned registry defining: symbols, valid combinations, transformations, invariants, domain-specific interpretations | Registry file with version, schema, and testable contract entries | NOT YET VERIFIED |
| F7 | Capacity ≠ materialization | Theoretical state-space capacity (e.g., 52^6) is a capacity calculation, not a claim that all combinations should be materialized; constraints and dependencies determine validity | Documented constraints in registry; no exhaustive materialization without evidence of meaningful states | NOT YET VERIFIED |

### G. Domain Fit Testing (from external assessment 2026-10-29)

| # | Item | Expectation | Evidence Required | Status |
|---|------|-------------|-------------------|--------|
| G1 | Four-outcome fit test | Domain fit must have four outcomes: fits, partial fit, does not fit, undetermined (abstention, not rejection) | Test: assert all four outcomes are reachable and distinguishable in fit-test output | NOT YET VERIFIED |
| G2 | Abstention is not rejection | "Undetermined" means evidence is missing or inconclusive; system abstains rather than inventing agreement or rejecting | Test: assert undetermined outcome does not trigger rejection logic | NOT YET VERIFIED |
| G3 | Multi-evidence agreement | Agreement measured using multiple evidence types: structural compatibility, symbolic correspondence, semantic relevance, mathematical invariants, historical provenance, consistency across transformations | Documented evidence types with explicit weights and calibrated thresholds | NOT YET VERIFIED |
| G4 | Hexagram is hypothesis, not verdict | A matching hexagram is a hypothesis to test, not a verdict to assume; fit requires documented compatibility rules, required invariants, and evidence threshold | Test: assert fit outcome requires all three (compatibility rules + invariants + evidence threshold) | NOT YET VERIFIED |
| G5 | Transmission ≠ communication ≠ interpretation ≠ consumption | Four stages must be tracked separately: generation, transport, interpretation, consumption; success at one stage does not imply success at others | Test: assert each stage's success/failure is independently measurable | NOT YET VERIFIED |
| G6 | Emotional validity boundary | Emotional controller may influence which domain is explored, how response is expressed, or how information is routed — but must NOT make an invalid mathematical result valid | Test: assert emotional_input change does not alter mathematical correctness verdict | NOT YET VERIFIED |

### H. Save-String Control Contract (from external assessment 2026-10-29)

| # | Item | Expectation | Evidence Required | Status |
|---|------|-------------|-------------------|--------|
| H1 | Save-string field groups | Save string must carry: identity (hexagram, phase, position, entity), input (verbatim), emotional control (affect, intensity, mixtures, temporal), audio reference (voice, timing, acoustic measurements), text reference (exact text, segmentation, expression), domain candidate (domain, assumptions), agreement evidence (tests passed/failed/unresolved), decision (fit/partial/reject/abstain), provenance (transformations, agents) | Schema document with all field groups | NOT YET VERIFIED |
| H2 | Save string as durable decision record | Save string preserves not only final answer but why domain was accepted, how emotion influenced output, and whether receiving entity interpreted correctly | Audit: inspect save string for all field groups; verify round-trip fidelity | NOT YET VERIFIED |
| H3 | Dual channel preservation | Both audio channel (voice identity, prosody, timing, emotional expression, machine-readable signals) and save-string channel (structured state, identity, relationships, provenance) must be preserved; audio consumption failure does not invalidate save-string record | Test: assert save string is complete even when audio consumer is absent | NOT YET VERIFIED |

### I. Emotion as Operational Control Signal (from external assessment 2026-10-29)

| # | Item | Expectation | Evidence Required | Status |
|---|------|-------------|-------------------|--------|
| I1 | Emotion is operational, not decorative | Emotional state must influence processing, expression, and routing — not just be attached as metadata | Test: assert emotional_input change produces measurable change in at least one of: voice parameters, text features, routing decision | NOT YET VERIFIED |
| I2 | Emotion preserves richness | Emotional control should preserve intensity, competing tendencies, uncertainty, and temporal change — not force into single label | Test: assert emotional state can represent mixed/competing tendencies, not just single category | NOT YET VERIFIED |
| I3 | Emotion does not override validity | Emotional agreement must not make invalid mathematical result valid; validity and emotion are separate measurable outcomes | Test: assert mathematical correctness verdict is independent of emotional_input | NOT YET VERIFIED |
| I4 | Three responsibilities separated | System must separate: control (emotion influences processing/expression/routing), communication (voices exchange structured/acoustic info), validation (receiver determines fit and success) | Architecture doc: three responsibilities with explicit boundaries | NOT YET VERIFIED |

### J. Mathematical Domain Agent Contract (from external assessment 2026-10-29)

| # | Item | Expectation | Evidence Required | Status |
|---|------|-------------|-------------------|--------|
| J1 | Multi-layer math representation | Five representations must coexist: source (page, crop, coordinates), structural (equation tree, grouping, spatial relationships), symbolic (operators, variables, indices, scopes), semantic (definitions, assumptions, units, relationships), executable (verified transformation when source supports) | Pipeline: assert all five layers are produced and linked for at least one benchmark problem | NOT YET VERIFIED |
| J2 | Uncertainty survives downstream | If a symbol or binding is uncertain, uncertainty must survive downstream instead of disappearing during conversion | Test: assert uncertainty flags are present in output when input is ambiguous | NOT YET VERIFIED |
| J3 | Domain agent skill card contract | Skill card must specify: domain identity, mathematical objects, transformation rules, preconditions, invariants, provenance, validation, uncertainty | Schema document with all eight components | NOT YET VERIFIED |
| J4 | Mathematical contract independent of implementation | Skill specifies what transformation is valid; implementations (symbolic, numerical, neural, hybrid) attempt to satisfy contract | Architecture: contract and implementation are separate layers | NOT YET VERIFIED |
| J5 | Agent type ≠ neural architecture | Specialized mathematical agent's domain constrains processing; neural architecture is implementation detail, not agent identity | Architecture: agent type and model architecture are separate concepts | NOT YET VERIFIED |
| J6 | End-to-end problem recovery milestone | One complete mathematical problem recovered with all seven preservation criteria: source evidence, equation structure, definitions/dependencies, derivation sequence, source/reconstructed/inferred distinction, reproducible validation, provenance | Benchmark problem with all seven criteria measured and recorded | NOT YET VERIFIED |
| J7 | Gap identification over quiet flattening | If a binding cannot be recovered reliably, pipeline must identify the gap rather than flatten into plausible expression | Test: assert unresolved bindings are reported, not silently resolved | NOT YET VERIFIED |

---

## Summary (Updated)

| Category | Items | Not Yet Verified |
|----------|-------|-----------------|
| A. Expansion pipeline | 4 | 4 |
| B. Voice / porosity | 4 | 4 |
| C. Math adapter | 6 | 6 |
| D. Hamiltonian energy | 4 | 4 |
| E. Downstream consumers | 4 | 4 |
| F. Identity alphabet & relationships | 7 | 7 |
| G. Domain fit testing | 6 | 6 |
| H. Save-string control contract | 3 | 3 |
| I. Emotion as operational control | 4 | 4 |
| J. Mathematical domain agent contract | 7 | 7 |
| **Total** | **55** | **55** |

**No item is marked as passing.** All items require explicit verification before status changes.