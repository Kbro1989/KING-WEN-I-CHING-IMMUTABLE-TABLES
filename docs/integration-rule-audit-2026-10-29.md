# Integration-Rule Audit: Corrected Rule Application (2026-10-29)

## Corrected Integration Rule (authoritative)

1. `collapse` was removed. Its absence is intentional, not automatically a defect to repair by restoring the old symbol or recreating its behavior.
2. Expansion is preferred over normalization. Preserve the expanded state space and its distinctions rather than collapsing, coercing, or normalizing states to satisfy legacy consumers.
3. Consumer compatibility must adapt to the canonical producer. Do not recreate a removed API or introduce a legacy alias without explicit authorization and evidence that its semantics are required.
4. Preserve identity and provenance. Retain `(hexagram_id, phase_bits)`, candidate records, temporal information, and derived-state distinctions through downstream processing.
5. The appropriate investigation is to trace the adapter's actual needs and determine how it should consume the expanded output. Any replacement must preserve the producer's semantics rather than recreate collapse under a different name.

## Audit Scope

All `.md` files in `docs/` related to: King Wen, math, vision, jacobian, hamiltonian, lua, gaussian, consumer repair, shotgun expansion, collapse, adapter, contract.

## Violations Found

### V-1: `docs/consumer-repair-specification-2026-10-29.md` line 40

**Current text:**
> 1.2. **Define `shotgun_expand` → `collapse` bridge.** The `expand_server.py` already bridges `personality_consensus` → `consensus` shape. The adapter needs the same bridge. The bridge must be documented and tested before implementation.

**Violation:** Suggests creating a "bridge" that maps `shotgun_expand` output to legacy `collapse` output schema. This recreates collapse under a different name, violating rule 3. Also violates rule 1 (collapse absence is intentional, not a defect to repair).

**Corrected text:**
> 1.2. **Trace adapter's actual needs against expanded output.** The adapter was written for `collapse_full_128`'s output schema, which no longer exists. The investigation must determine what the adapter actually consumes and how it should consume `shotgun_expand`'s output. Any replacement must preserve the producer's semantics rather than recreate collapse under a different name. The `expand_server.py` already exposes `personality_consensus` → `consensus` shape as a reference for how a consumer can read expanded output, but this is a consumer-side adaptation, not a bridge to restore collapse.

### V-2: `docs/consumer-boundary-audit-2026-10-29.md` line 231

**Current text:**
> 1. **Fix OpenJarvis adapter import** — replace `collapse_full_128` with `shotgun_expand` (or add try/except fallback + bridge). This is the highest-priority consumer fix because it unblocks 3 downstream consumers.

**Violation:** The "(or add try/except fallback + bridge)" parenthetical suggests creating a bridge/alias, violating rule 3.

**Corrected text:**
> 1. **Fix OpenJarvis adapter import** — replace `collapse_full_128` with `shotgun_expand` or trace the adapter's actual needs and determine how it should consume the expanded output. This is the highest-priority consumer fix because it unblocks 3 downstream consumers.

### V-3: `docs/shotgun-expand-output-contract-2026-10-29.md` lines 187-188

**Current text:**
> 1. **Schema bridge:** adapter must map `personality_consensus`/`dominant_agent_type` to the legacy `consensus`/`consensus_hexagram_id` fields with documented semantics, or explicitly replace the old fields with new ones and update all consumers

**Violation:** Suggests mapping to "legacy" fields, which is recreating collapse under a different name. Violates rules 1 and 3.

**Corrected text:**
> 1. **Consumer adaptation:** adapter must consume `personality_consensus`/`dominant_agent_type` from the expanded output with documented semantics, or explicitly define how the adapter reads expanded output and update all consumers. The adapter must not map expanded fields to legacy collapse field names without evidence that the legacy semantics are required.

### V-4: `docs/consumer-repair-specification-2026-10-29.md` line 159

**Current text:**
> | Schema bridge | Every mapped field has documented, tested semantics | `tests/test_schema_bridge.py` | Not written |

**Violation:** References "Schema bridge" as a workstream name, implying bridge creation is the intended approach.

**Corrected text:**
> | Consumer adaptation | Every consumed field has documented, tested semantics | `tests/test_consumer_adaptation.py` | Not written |

### V-5: `docs/shotgun-expand-output-contract-2026-10-29.md` line 210

**Current text:**
> - **Fix (NOT authorized yet):** Map `personality_consensus` fields to legacy fields or replace

**Violation:** "Map ... to legacy fields" suggests recreating collapse output schema.

**Corrected text:**
> - **Fix (NOT authorized yet):** Trace adapter's actual field needs against expanded output; consume expanded fields directly or define adapter-specific consumption with documented semantics

### V-6: `docs/shotgun-expand-output-contract-2026-10-29.md` line 256

**Current text:**
> 2. `personality_consensus` → legacy field semantics are explicitly documented (Section: Legacy Consensus Field Semantics)

**Violation:** References "legacy field semantics" as something to be documented, implying the adapter should support legacy field names.

**Corrected text:**
> 2. Consumer adaptation semantics are explicitly documented (Section: Consumer Adaptation Semantics)

## Files Audited (no violations found)

The following files reference "collapse" but do NOT violate the corrected rule (they describe collapse as removed/stale/intentional):

- `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` — "Vectors collapsed to same values" (failure condition, not restoration suggestion)
- `docs/cross-verification-checklist-2026-09-01.md` — "Stale collapse output" (correctly identifies as stale)
- `docs/immutable-table-math-decoded.md` — quantum collapse in math context (not about restoring API)
- `docs/j-space-jacobian-lens-math-2026-07-11.md` — "XOR-gate direct verification without forced collapse" (math concept)
- `docs/KING_WEN_CONSENSUS_MATH.md` — consensus math (not about restoring API)
- `docs/kingwen-quantum-methods-2026-07-11.md` — quantum methods (not about restoring API)
- `docs/kingwen-superposition-expansion-plan-2026-07-11.md` — superposition expansion (not about restoring API)
- `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` — "no RNG collapse" (correctly prohibits collapse)
- `docs/B4-PARAM-SPEC-KW-B4-PARAM-001.md` — "collapse candidate evidence" (prohibits collapse)
- `docs/KING-WEN-RESEARCH-CHECKLIST.md` — "no winner/dominant collapse" (correctly prohibits)
- `docs/numerical-extraction-vision-pipeline.md` — vision pipeline (not about restoring API)
- `docs/read-only-evidence-pass-2026-10-29.md` — documents collapse as removed (correct)
- `docs/representation-equivalence-audit-checklist-2026-10-29.md` — audit checklist (correct)
- `docs/research-lead-incontext-reward-adaptation-2026-10-29.md` — research lead (correct)
- `docs/research-to-test-traceability-matrix-2026-10-29.md` — traceability (correct)
- `docs/traceability-matrix-2026-10-27.md` — traceability (correct)
- `docs/audit-drift-report-2026-10-27.md` — audit drift (correct)
- `docs/math-term-usage-analysis-2026-10-27.md` — math term usage (correct)
- `docs/OEIS_KING_WEN_SEQUENCE.md` — OEIS sequence (correct)
- `docs/pair_dynamics_audit_summary_2026-10-27.md` — pair dynamics (correct)
- `docs/semantic_math_pipeline_report.md` — semantic math (correct)
- `docs/traceability-matrix-audit-2026-10-27.md` — traceability audit (correct)
- `docs/wolfram_notation_reference.md` — wolfram notation (correct)

## Audit Summary

| File | Violations | Status |
|---|---|---|
| `docs/consumer-repair-specification-2026-10-29.md` | V-1, V-4 | Needs correction |
| `docs/consumer-boundary-audit-2026-10-29.md` | V-2 | Needs correction |
| `docs/shotgun-expand-output-contract-2026-10-29.md` | V-3, V-5, V-6 | Needs correction |

## Corrections Applied (2026-10-29)

All 6 violations (V-1 through V-6) have been corrected:

| Violation | File | Status |
|---|---|---|
| V-1 | `docs/consumer-repair-specification-2026-10-29.md` line 40 | Corrected — "Trace adapter's actual needs against expanded output" |
| V-2 | `docs/consumer-boundary-audit-2026-10-29.md` line 231 | Corrected — removed "(or add try/except fallback + bridge)" |
| V-3 | `docs/shotgun-expand-output-contract-2026-10-29.md` lines 196-198 | Corrected — "Consumer adaptation" replacing "Schema bridge" |
| V-4 | `docs/consumer-repair-specification-2026-10-29.md` line 159 | Corrected — "Consumer adaptation" replacing "Schema bridge" |
| V-5 | `docs/shotgun-expand-output-contract-2026-10-29.md` line 217 | Corrected — "Trace adapter's actual field needs" replacing "Map to legacy fields" |
| V-6 | `docs/shotgun-expand-output-contract-2026-10-29.md` line 263 | Corrected — "Consumer adaptation semantics" replacing "Legacy Consensus Field Semantics" |

Additionally:
- `docs/consumer-boundary-audit-2026-10-29.md` line 232: "Bridge personality_consensus → consensus" → "Consumer adaptation for personality_consensus → consensus"
- `OpenJarvis/tests/emotion/test_kingwen_adapter_contract.py` line 481: updated section reference to "Consumer Adaptation Semantics"

Remaining "bridge" references are now in the context of "consumer-side adaptation, not a bridge to restore collapse" and "must not map expanded fields to legacy collapse field names" — both correct per the corrected rule.

## Verification

- All 32 contract tests pass (8.95s)
- No source code modified
- Gate 2 remains OPEN
- Adapter implementation remains NOT authorized