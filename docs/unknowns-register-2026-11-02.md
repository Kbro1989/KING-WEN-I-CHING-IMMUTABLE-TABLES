# Unknowns Register — Definition and Usage Provenance

## Scope

Read-only investigation artifact. No source changes, no commits, no remediation acceptance.
This register tracks terminology and mathematical meaning that have not yet been established, separate from the remediation matrix which tracks existing implementation findings.

**Date**: 2026-11-02
**Repository**: KING-WEN-I-CHING-IMMUTABLE-TABLES
**Baseline commit**: `71fbf28f8e92c6a7de74c50a304906ef81963a7d`

## 1. Purpose

The remediation matrix (`docs/remediation-verification-matrix.md`) tracks implementation defects (F-01 through F-12). This register tracks a different category: terms and mathematical concepts that are used in the system but whose definitions have not been established from authoritative sources.

These two registers must remain separate because:
- Remediation concerns what the code does wrong.
- Unknowns concerns what the code means and whether that meaning is supported.

A term can be correctly implemented while its definition remains unverified, and a definition can be found while the implementation's relationship to it remains unestablished.

## 2. Evidence Layers

Each unknown is investigated through three independent evidence layers:

| Layer | Question | Evidence type |
|---|---|---|
| E1 — Lexical | Does the source actually use the term? | Exact terminology, notation, first occurrence, attribution, definition vs. description vs. equation |
| E2 — Conceptual | Does the source establish what the term represents? | Object described, role served, assumptions, conditions, inherited vs. specific meaning |
| E3 — Mathematical | Does the actual mathematics support the claimed meaning? | Variables, domains, equations, operators vs. scalars, units, invariants, boundary conditions, observed behavior |

A successful lexical extraction is not conceptual verification. A conceptual description is not mathematical proof.

## 3. Graduated Investigation Process

Each unknown follows a four-stage investigation with a stopping condition at each stage.

### Stage A — Establish the actual usage

Record exact term, source document and location, first occurrence, subsequent occurrences, and whether usage is descriptive, operational, or mathematical.

### Stage B — Trace the definition backward

Search in order:
1. The source's own definitions, notation, preliminary sections.
2. Appendices, supplementary material, referenced equations.
3. Specific works cited near first occurrence.
4. Earlier foundational papers cited by those works.
5. Established mathematical/scientific literature for the relevant discipline.

### Stage C — Test whether the definition transfers

Compare the candidate definition against the actual implementation:
- Mathematical structure
- Input/output types
- Variable domains
- Assumptions
- Transformations
- Invariants
- Expected behavior vs. actual observed behavior

### Stage D — Preserve the unresolved portion

If the source establishes only part of the meaning, document that part and leave the remainder unresolved. Do not manufacture a definition.

## 4. Disposition Rules

| Disposition | Minimum justification |
|---|---|
| Defined | Authoritative definition located AND actual usage consistent with it |
| Partial | Some meaning or behavior supported, but important semantic/mathematical elements unestablished |
| Incompatible | Affirmative evidence that actual usage contradicts proposed definition |
| Undetermined | Available evidence cannot distinguish between competing interpretations |

**Critical rule**: "Not found" is not equivalent to "does not exist." If a definition cannot be found in examined literature, record the search boundary. Do not claim the term has no definition anywhere.

## 5. Unknowns Register

### U-01: Hamiltonian energy (M3)

| Field | Value |
|---|---|
| Usage ID | U-01 |
| Term / notation | Hamiltonian energy / ℋ(p,q,t) |
| Actual usage | `_hamiltonian_energy()` in `emotional_engine.py:408-455` computes `H = max(0.0, pq_dot - lagrangian)` where `pq_dot = Σ(max(0, resolved_i) × (resolved_i - expanded_i))` and `lagrangian = abs(dy)*0.5 + abs(yao_dy)*0.3 + abs(changing_dy)*0.2` |
| Source location | `emotional_engine.py:408-455`; docstring claims `ℋ(p,q,t) = Σ p_i · q̇^i - ℒ` |
| Candidate definition | Classical Hamiltonian mechanics: H(q,p,t) = Σ p_i q̇^i - L(q,q̇,t) where L is Lagrangian, p_i = ∂L/∂q̇^i |
| Definition provenance | Classical mechanics (Goldstein, Landau & Lifshitz); no specific paper cited in codebase |
| E1 status | Lexical: Term used in docstring and variable names. "Hamiltonian" appears in 15+ audit docs. |
| E2 status | Conceptual: Claimed as Hamiltonian mechanics. Actual computation is a scalar calculation with Hamiltonian-inspired naming. |
| E3 status | Mathematical: pq_dot ~0.01 scale (continuous emotional vector) vs lagrangian ~1-5 scale (discrete state counts). Coefficients 0.5/0.3/0.2 undocumented. No theoretical derivation. |
| Transferability | Incompatible — the implementation does not satisfy the formal Hamiltonian definition (no canonical coordinates, no Legendre transform, no phase space) |
| Contradictory evidence | F-10 VALIDATED: scale/semantic incompatibility. F-12 VALIDATED: 100% information loss via clamp. QuantumLab ruled out as source. Wiki math corpus ruled out. |
| Missing evidence | Whether any paper in the 243-paper Zotero corpus defines a compatible Hamiltonian-like energy for this domain |
| Disposition | **Incompatible** (with respect to formal Hamiltonian mechanics); **Partial** (as a scalar scoring function with Hamiltonian-inspired naming) |
| Confidence basis | F-10, F-11, F-12 VALIDATED; provenance investigation complete; no theoretical basis found |
| Next evidence requirement | Search Zotero corpus for "Hamiltonian" in math context; compare against formal definition |

### U-02: Porosity (three computations)

| Field | Value |
|---|---|
| Usage ID | U-02 |
| Term / notation | Porosity (three independent computations) |
| Actual usage | (1) Injection site: integer 0-4 from HEXAGRAM_INJECTION_SITE; (2) Phase-modulated: float 0.0-1.0 via `_pool_weights_for_hex()`; (3) Kit QWP: float 0.15-0.71 from `kingwen_model_sets/kit_*.json` |
| Source location | `emotional_engine.py:651` (canonical), `emotional_engine.py:659-663` (phase-modulated), `enrich_kit_models.py` (kit QWP) |
| Candidate definition | (1) Topological openness of hexagram inject site; (2) Phase-modulated bleed factor; (3) Quantum wave packet porosity |
| Definition provenance | HEXAGRAM_INJECTION_SITE (immutable tables); kit QWP from Godot 3D mesh generation |
| E1 status | Lexical: "porosity" used in 539 locations across codebase |
| E2 status | Conceptual: Three different concepts sharing one name; no documented relationship |
| E3 status | Mathematical: Three different scales (0-4 int, 0.0-1.0 float, 0.15-0.71 float); no conversion function |
| Transferability | Not applicable — three computations are independent, not transfers |
| Contradictory evidence | No affirmative contradiction, but no documented relationship either |
| Missing evidence | Whether the three computations are intended to represent the same concept or different concepts |
| Disposition | **Undetermined** (relationship between three computations not established) |
| Confidence basis | Three computations identified; no conversion or semantic contract found |
| Next evidence requirement | Search immutable tables docs and Godot mesh docs for porosity definitions |

### U-03: Coherence

| Field | Value |
|---|---|
| Usage ID | U-03 |
| Term / notation | Coherence (5-axis emotional vector component) |
| Actual usage | `VEC_KEYS[3] = "coherence"`; computed in `_pool_weights_for_hex()` as blend of line-state balance, trigram context, neighbor continuity, and intent modulation; used in `abs(old_dy)` in formula-design-review context |
| Source location | `emotional_engine.py:34` (definition), `emotional_engine.py:604-690` (computation) |
| Candidate definition | Quantum coherence (superposition maintenance) or signal processing coherence (phase alignment) |
| Definition provenance | No specific paper cited; term used descriptively |
| E1 status | Lexical: Used as 5-axis vector component name |
| E2 status | Conceptual: Describes how aligned/consistent the hexagram state is; no formal definition |
| E3 status | Mathematical: Computed as `_clamp` of blended contributions; `abs(old_dy)` in design review (sign-discarding question OPEN) |
| Transferability | Partial — numerical value computed but semantic role as "coherence" not formally established |
| Contradictory evidence | `abs(old_dy)` gives 0.05 for all-yin vs signed 0.25 — sign-discarding changes meaning |
| Missing evidence | Whether "coherence" in this context maps to any established coherence definition |
| Disposition | **Partial** |
| Confidence basis | Computation documented; semantic role not formally established |
| Next evidence requirement | Search Zotero corpus for coherence definitions in quantum/AI context |

### U-04: Voice weight

| Field | Value |
|---|---|
| Usage ID | U-04 |
| Term / notation | Voice weight (5-axis emotional vector component) |
| Actual usage | `VEC_KEYS[4] = "voiceWeight"`; computed in `_pool_weights_for_hex()`; used in CartesiaAdapter for voice synthesis parameters; correlates with coherence (0.968) |
| Source location | `emotional_engine.py:34`; `speech/cartesia_adapter.py` (OpenJarvis) |
| Candidate definition | TTS authority axis — weight given to voice output in the emotional expression |
| Definition provenance | User's design intent (Jiminy Cricket effect: voice speaks truth) |
| E1 status | Lexical: Used as 5-axis vector component and voice synthesis parameter |
| E2 status | Conceptual: Describes how much authority the voice output should have |
| E3 status | Mathematical: Correlates with coherence (0.968); used in CartesiaAdapter speed formula |
| Transferability | Partial — numerical value computed and used, but formal definition of "voice weight" as a mathematical quantity not established |
| Contradictory evidence | None identified |
| Missing evidence | Whether voiceWeight has a theoretical basis beyond empirical correlation with coherence |
| Disposition | **Partial** |
| Confidence basis | Used in production (CartesiaAdapter); correlation with coherence documented |
| Next evidence requirement | Search for voice authority / expressivity models in Zotero corpus |

### U-05: Consensus

| Field | Value |
|---|---|
| Usage ID | U-05 |
| Term / notation | Consensus (hexagram consensus) |
| Actual usage | `_compute_consensus_from_resolved()` produces consensus from all 512 resolved states; `consensus_hexagram_id`, `consensus_hexagram_name`, `consensus_temporal`, `consensus_yao`, `consensus_porosity_mean`, `consensus_vector`, `consensus_intent`, `consensus_explanation` |
| Source location | `emotional_engine.py:1090-1160` (approximate) |
| Candidate definition | Arithmetic mean across all 64 expanded vectors (not top-k or single-hex collapse) |
| Definition provenance | User's design principle: "the consensus isn't 1 resolve either. it's the full weight of the quantum wave and audio packet field with metadata shotgunned in" |
| E1 status | Lexical: "consensus" used in 50+ locations; `consensus_hexagram_id` implies single hex but user clarified it's full wave |
| E2 status | Conceptual: Full 512-state weighted wave, not single-hex resolve. Consensus is arithmetic mean, not selection. |
| E3 status | Mathematical: Mean of 512 resolved vectors; `consensus_intent` stable across slider steps (mean of wave) |
| Transferability | Partial — computation matches user's stated intent, but "consensus" as a term implies agreement/selection which contradicts full-wave interpretation |
| Contradictory evidence | Field name `consensus_hexagram_id` implies single hex; user clarified it's full wave |
| Missing evidence | Whether "consensus" is the right term or whether "superposition" or "field" would be more accurate |
| Disposition | **Partial** (computation correct per user intent; terminology may be misleading) |
| Confidence basis | User's explicit clarification; computation verified |
| Next evidence requirement | None — user's intent is clear; terminology question is design choice |

### U-06: Phase bits / temporal states

| Field | Value |
|---|---|
| Usage ID | U-06 |
| Term / notation | Phase bits (0-7) / temporal states (past, present, future, etc.) |
| Actual usage | 8 phases: past='a', present='p', future='f', plus 5 others (transition, resolution, dissolution, crystallization, void). `phase_bits` 0-7. `phase_temporal` string label. |
| Source location | `emotional_engine.py` (PHASE_INFO dict); `kingwen_ternary_tables_complete.py` |
| Candidate definition | 8 temporal phases of I-Ching hexagram change (past/present/future + 5 intermediate states) |
| Definition provenance | I-Ching trigram/hexagram phase theory; 8 phases = 2^3 (three changing lines) |
| E1 status | Lexical: "phase_bits", "phase_temporal", "phase_temporal" used throughout |
| E2 status | Conceptual: 8 phases represent temporal evolution of hexagram state |
| E3 status | Mathematical: 8 phases × 64 hexagrams = 512 states; phase shift is hardcoded 5-tuple per phase |
| Transferability | Partial — 8 phases match I-Ching theory but phase shifts are hardcoded, not derived |
| Contradictory evidence | Phase 6-7 (void) has no porosity=0 states; hardcoded shifts not theoretically justified |
| Missing evidence | Whether phase shifts should be derived from hexagram state rather than hardcoded |
| Disposition | **Partial** |
| Confidence basis | 8-phase structure matches I-Ching theory; shift values undocumented |
| Next evidence requirement | Search I-Ching literature for phase-shift definitions |

### U-07: Yao vocabulary

| Field | Value |
|---|---|
| Usage ID | U-07 |
| Term / notation | Yao vocabulary (9-member: young_yin, old_yin, stable_yin, new_yao, old_yao, stable_yao, old_yang, new_yang, stable_yang) |
| Actual usage | `YAO_VOCABULARY` dict; used in `expand_hexagram()` for yao_vocabulary field; yao_vocabulary passed to downstream consumers |
| Source location | `emotional_engine.py` (YAO_VOCABULARY); `kingwen_ternary_tables_complete.py` |
| Candidate definition | I-Ching yao (line) states: young/old/stable for yin/yao/yang; old = changing, stable = non-changing |
| Definition provenance | User's 9-bit progressive collapse encoding; yao vocabulary standardized to young/old/stable |
| E1 status | Lexical: "yao" used in 100+ locations; 9-member vocabulary defined |
| E2 status | Conceptual: 9 states = 3 (yin/yao/yang) × 3 (young/old/stable); old = changing, stable = non-changing |
| E3 status | Mathematical: 3^6 = 729 ternary permutations per hexagram; 9-member vocabulary maps to 3^2 = 9 combinations per line pair |
| Transferability | Partial — vocabulary defined and used, but mapping from 9-member vocabulary to 3-valued ternary (0/1/2) not formally documented |
| Contradictory evidence | Three incompatible ternary definitions exist (binary recoding 0→1/1→2, full ternary 0/1/2, five-valued differential 0-4) — B4 Gate 2 BLOCKED |
| Missing evidence | Conversion function between 3-valued and 5-valued ternary representations |
| Disposition | **Partial** (vocabulary defined; semantic reconciliation incomplete) |
| Confidence basis | Vocabulary documented in immutable tables; conversion gap confirmed |
| Next evidence requirement | Create `docs/TERNARY-SEMANTICS-RECONCILIATION.md` |

### U-08: Porosity (relationship between computations)

| Field | Value |
|---|---|
| Usage ID | U-08 |
| Term / notation | Porosity (relationship between three computations) |
| Actual usage | See U-02 for three computations; this entry tracks the relationship between them |
| Source location | Multiple (see U-02) |
| Candidate definition | (1) Topological openness, (2) Phase-modulated bleed factor, (3) Quantum wave packet porosity |
| Definition provenance | Three independent sources: immutable tables, emotional engine, Godot 3D |
| E1 status | Lexical: "porosity" used in 539 locations |
| E2 status | Conceptual: Three concepts sharing one name; no documented relationship |
| E3 status | Mathematical: Different scales, no conversion function |
| Transferability | Not applicable — three independent computations |
| Contradictory evidence | None (they don't contradict, they're just unrelated) |
| Missing evidence | Whether the three are intended to be the same concept or different concepts |
| Disposition | **Undetermined** |
| Confidence basis | Three computations identified; no semantic contract found |
| Next evidence requirement | Search immutable tables docs and Godot mesh docs for porosity definitions |

### U-09: shotgun_expand() output contract

| Field | Value |
|---|---|
| Usage ID | U-09 |
| Term / notation | shotgun_expand() output contract (field names, types, semantics) |
| Actual usage | Returns dict with expanded[] (64), resolved[] (512), consensus, ternary_permutations (729/hex), total_ternary_permutations (46,656), total_domained_routes (35,000), capture_point, personality_consensus, personality_subsets, expanded_vector, resolved_vector, domain_vector, sample_paths, structural_vector, inject_site, line_states, line_balance, yao_vocabulary, pre_slider, hamiltonian_energy, hamiltonian_normalized, wavefunction, rotation_x, rotation_y, scale_factor, animation_phase, consensus_hexagram_id, consensus_hexagram_name, consensus_temporal, consensus_yao, consensus_porosity_mean, consensus_porosity_mode, consensus_vector, consensus_intent, consensus_explanation, temporal_distribution |
| Source location | `scripts/full_hexagram_shotgun.py:549` |
| Candidate definition | In-memory Python dict with no formal schema, no versioning, no validation |
| Definition provenance | Ad hoc — fields added incrementally as features were developed |
| E1 status | Lexical: All field names documented in producer-to-consumer map |
| E2 status | Conceptual: Fields represent expanded/resolved state, consensus, vectors, inject site, wavefunction, rotation, scale, animation |
| E3 status | Mathematical: Field types vary (dict, list, float, int, str, None); no schema enforcement |
| Transferability | Not applicable — no external definition to transfer to |
| Contradictory evidence | `domain_vector == resolved_vector` (0 mismatches) — redundant; `sample_paths` primary == neighbor_blend — redundant; 448/512 resolved states have None for ternary_slots/schauberger/personality_subsets/projections |
| Missing evidence | Formal schema definition; field-level type constraints; which fields are required vs. optional |
| Disposition | **Partial** (fields documented but no formal contract) |
| Confidence basis | Producer-to-consumer map complete; field usage catalogued |
| Next evidence requirement | Create formal output contract document |

### U-10: 9-bit encoding

| Field | Value |
|---|---|
| Usage ID | U-10 |
| Term / notation | 9-bit encoding (6 base ternary + 3 phase bits) |
| Actual usage | `kingwen_ternary_tables_complete.py` — 512-entry 9-bit collapsed state machine; `save_string_v21.py` referenced but not found on disk |
| Source location | `KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_ternary_tables_complete.py` |
| Candidate definition | 9-bit encoding = 6 base ternary line digits + 3 phase bits; 512 = 64 × 8 |
| Definition provenance | User's 9-bit progressive collapse encoding (5 years of translation work) |
| E1 status | Lexical: "9-bit" used in multiple docs and skills |
| E2 status | Conceptual: 6 ternary lines (3^6 = 729) + 3 phase bits (2^3 = 8) = 5,832 |
| E3 status | Mathematical: 512 = 64 × 8 (binary layer); 729 = 3^6 (ternary layer); 5,832 = 729 × 8 (ternary resolved) |
| Transferability | Partial — encoding defined but save-string V2.1 serializer not found on disk |
| Contradictory evidence | `save_string_v21.py` referenced in brain walkthrough but not found on disk |
| Missing evidence | Actual save-string serializer implementation; whether 9-bit encoding is used in production |
| Disposition | **Partial** (encoding defined; serializer not found) |
| Confidence basis | Immutable tables verified; serializer not located |
| Next evidence requirement | Search for save_string_v21.py or equivalent serializer |

## 6. Priority Order

Investigation priority (by downstream impact):

| Priority | Unknown | Reason |
|---|---|---|
| 1 | U-01 (Hamiltonian) | Mathematical identity; affects M6 imaginary amplitude, rotation, scale, animation |
| 2 | U-07 (Yao vocabulary) | Ternary semantics reconciliation; B4 Gate 2 BLOCKED |
| 3 | U-02/U-08 (Porosity) | Three unreconciled computations; affects consensus, voice, 3D |
| 4 | U-09 (Output contract) | No formal schema; 23+ consumers depend on it |
| 5 | U-03 (Coherence) | Sign-discarding question affects vector semantics |
| 6 | U-04 (Voice weight) | Used in production (CartesiaAdapter); correlation with coherence |
| 7 | U-05 (Consensus) | Terminology may be misleading; computation matches user intent |
| 8 | U-06 (Phase bits) | Hardcoded shifts not theoretically justified |
| 9 | U-10 (9-bit encoding) | Serializer not found on disk |
| 10 | U-02 (Porosity relationship) | Whether three computations are same or different concepts |

## 7. Governing State

| Item | Status |
|---|---|
| Unknowns registered | 10 |
| Defined | 0 |
| Partial | 7 (U-01, U-03, U-04, U-05, U-06, U-09, U-10) |
| Incompatible | 1 (U-01) |
| Undetermined | 2 (U-02, U-08) |
| Source modifications | None |
| Commits | None |
| Remediation acceptance | Not started |
| Gate 2 | OPEN |

## 8. Hard Boundary

No candidate definition becomes a system definition merely because it appears in a research paper. It must survive the E1/E2/E3 evidence tests and correspondence with the actual implementation. The remediation matrix and the unknowns register are separate artifacts and must not be conflated.