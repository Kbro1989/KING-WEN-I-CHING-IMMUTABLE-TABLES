# Field-Level Lineage Audits — Consolidated Domain Document

**Domain:** L1 Emotional Vectors / L2 Porosity / L3 Hamiltonian / Cross-Field Dependency Matrix / Pre-Remediation Evidence Freeze / Unknowns Register
**Consolidated from:** 6 source documents (88,349 bytes total)
**Date:** 2026-11-03
**Status:** Discovery phase CLOSED; evidence freeze COMPLETE

---

## Source Document Index

| # | File | Bytes | Role |
|---|------|-------|------|
| 1 | docs/emotional-vector-lineage-audit-2026-11-02.md | ~245 lines | L1 emotional vectors |
| 2 | docs/porosity-lineage-audit-2026-11-02.md | ~190 lines | L2 porosity |
| 3 | docs/hamiltonian-lineage-audit-2026-11-02.md | ~274 lines | L3 Hamiltonian |
| 4 | docs/cross-field-dependency-matrix-2026-11-02.md | ~160 lines | Cross-field matrix |
| 5 | docs/pre-remediation-evidence-freeze-2026-11-02.md | ~248 lines | Evidence freeze (16 artifacts) |
| 6 | docs/unknowns-register-2026-11-02.md | ~10 unknowns | Unknowns register (U-01–U-10) |

---

## L1: Emotional Vector Lineage — Integrity PARTIALLY PRESERVED

### 5-Axis Vector
- **Axes:** chaos, whimsy, darkTone, coherence, voiceWeight
- **Sources:** line state balance (primary), trigram vector (secondary, 60/40 blend), neighbor blend (tertiary, 70/30), intent vector (15% + intent_mod 25%)
- **Phase shifts:** hardcoded (chaos +0.1, whimsy +0.05, darkTone -0.1)
- **Porosity bleed:** 20%
- **Fallbacks:** `or 0.0` at multiple points
- **domain_vector == resolved_vector:** 0 mismatches (redundant)
- **primary == neighbor_blend in sample_paths:** redundant

### Known
- 5-axis vector structure defined and computed
- 4-source blending documented
- Phase shifts hardcoded (not derived)
- Porosity bleed 20% applied
- domain_vector == resolved_vector (0 mismatches) — redundant field

### Unknown
- Whether phase shifts are semantically correct
- Whether 60/40 and 70/30 blend ratios are justified
- Whether porosity bleed 20% is appropriate
- Whether domain_vector redundancy is intentional

### Partial
- Integrity partially preserved: vector structure exists but blend ratios and phase shifts undocumented

---

## L2: Porosity Lineage — Integrity NOT PRESERVED

### Three Unreconciled Computations
1. **Injection site porosity:** int 0-4 (from HEXAGRAM_INJECTION_SITE)
2. **Phase-modulated porosity:** float 0.0-1.0 (base/4 + phase_overdrive*0.5)
3. **Kit QWP porosity:** float 0.15-0.71 (from quantum wave packet)

### Issues
- base_porosity not preserved separately
- `or` fallbacks conflate int 0-4 with float 0.0-1.0
- Phase 6-7 (void) has no porosity=0 states
- Three computations not reconciled

### Known
- Three porosity computations exist
- Injection site porosity is int 0-4
- Phase-modulated porosity is float 0.0-1.0
- Kit QWP porosity is float 0.15-0.71

### Unknown
- Which porosity computation is canonical
- How to reconcile the three computations
- Whether porosity=0 states should exist for void phases

### Partial
- Integrity not preserved: three unreconciled computations, `or` fallbacks conflate types

---

## L3: Hamiltonian Lineage — Integrity NOT PRESERVED

### Summary
- 100% information loss (727 distinct raw H → 1 observed 0.0)
- Empty line_balance {} at emotional_engine.py:499 (F-08)
- pq_dot vs lagrangian scale mismatch
- Dependency chain: F-10 → F-12 → F-11
- See CONSOLIDATED_QSMC1_M3_HAMILTONIAN.md for full details

---

## Cross-Field Dependency Matrix

### 4 Concern Classes
1. **Provenance loss** — information lost during transformation
2. **Representation inconsistency** — same concept represented differently across layers
3. **Information collapse** — multiple distinct values collapse to single value
4. **Integration defects** — consumer integration issues (empty line_balance, broken imports)

### Reversibility Breakdown
| Finding | Type | Reversibility |
|---------|------|---------------|
| F-01 | Code fix | Reversible |
| F-02 | Code fix | Reversible |
| F-05 | Code fix | Reversible |
| F-05b | Code fix | Reversible |
| F-06 | Code fix | Reversible |
| F-07 | Code fix | Reversible |
| F-08 | Existing data | Reversible (data available) |
| F-10 | Semantic redefinition | NOT reversible (requires semantic decision) |
| F-11 | Derived | Derived from F-10 |
| F-12 | Data-recoverable | Reversible (raw H recoverable) |

### Intentional Boundaries
- expanded vs resolved (binary layer)
- binary vs ternary (3^6 permutations)
- emotional vector vs Hamiltonian scalar (different representations)
- pq_dot vs lagrangian (different scales)

### Non-Intentional Redundancy
- domain_vector == resolved_vector (0 mismatches)
- primary == neighbor_blend in sample_paths

---

## Pre-Remediation Evidence Freeze

**Status:** COMPLETE (docs/pre-remediation-evidence-freeze-2026-11-02.md, 248 lines)
**Git HEAD:** 71fbf28f8e
**Working tree:** 18 modified tracked + 98 untracked files

### 8 Specific Artifacts
1. Modified tracked files (18) with diff stats
2. Untracked files (98) with categorization
3. Remediation verification matrix (8 entries, all INCONCLUSIVE)
4. Information-loss remediation register (27 entries)
5. QSMC-1 correspondence audit (M1-M7)
6. Field-level lineage audits (L1, L2, L3)
7. Cross-field dependency matrix
8. Unknowns register (U-01–U-10)

### Three Milestones
1. Evidence freeze (COMPLETE)
2. Controlled resolution (AUTHORIZED at process level)
3. Individual change authorization (PENDING)

---

## Unknowns Register (U-01–U-10)

| ID | Unknown | Evidence Layers | Status |
|----|---------|----------------|--------|
| U-01 | Dual disposition (porosity) | E1/E2/E3 | OPEN |
| U-02 | Porosity reconciliation | E1/E2/E3 | OPEN |
| U-03 | Coherence/voiceWeight semantic | E1/E2/E3 | OPEN |
| U-04 | Audio pellet range | E1/E2/E3 | OPEN |
| U-05 | 111111 collapse / consensus | E1/E2/E3 | OPEN |
| U-06 | Import path resolution | E1/E2/E3 | OPEN |
| U-07 | Ternary semantics (BLOCKS B4 Gate 2) | E1/E2/E3 | OPEN |
| U-08 | Output contract (23+ consumers, 448/512 None) | E1/E2/E3 | OPEN |
| U-09 | 9-bit encoding (save_string_v21.py not found) | E1/E2/E3 | OPEN |
| U-10 | Integration defects (empty line_balance, broken imports) | E1/E2/E3 | OPEN |

---

## Machine-Readable Summary

```json
{
  "domain": "field_lineage_audits",
  "status": "discovery_closed",
  "evidence_freeze": "complete",
  "lineage": {
    "L1_emotional_vectors": {"status": "PARTIALLY_PRESERVED", "issues": ["phase_shifts_hardcoded", "blend_ratios_undocumented", "porosity_bleed_undocumented", "domain_vector_redundant"]},
    "L2_porosity": {"status": "NOT_PRESERVED", "issues": ["three_unreconciled_computations", "or_fallbacks_conflate_types", "no_porosity_zero_for_void", "base_porosity_not_preserved"]},
    "L3_hamiltonian": {"status": "NOT_PRESERVED", "issues": ["100%_information_loss", "empty_line_balance", "scale_mismatch", "F-10_F-11_F-12"]}
  },
  "cross_field": {
    "concern_classes": ["provenance_loss", "representation_inconsistency", "information_collapse", "integration_defects"],
    "reversible": 6,
    "not_reversible": 1,
    "derived": 1,
    "data_recoverable": 1
  },
  "unknowns": 10,
  "frozen": ["M3_provenance", "QSMC1_baseline", "evidence_freeze"]
}
```