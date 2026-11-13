# Glyph Identity Registry — Implementation Boundary & Unicode Expansion Plan

**Generated:** 2026-11-13
**Status:** Baseline registry frozen; Unicode expansion pending

---

## Implementation Boundary (Frozen)

| Component | Role | Status |
|---|---|---|
| **Canonical source** | Metamath manifest (1,182 entries) | `DATASETS/math_symbols/manifest.json` |
| **Unicode authority** | Metamath `symbols.html` | Authoritative Unicode ↔ Metamath name mappings |
| **Visual catalog** | `symbols.zip` (3,301 images) | Reconciled: 1,181/1,182 manifest entries mapped |
| **Provenance** | `provenance_manifest.json` | 1,182 SHA-256 hashes, source revision, license |
| **Existing notation dictionaries** | Read-only inputs | Wolfram (82 keys), SymPy (77 keys) in `scripts/math_notation_mapping.py` |
| **Regression anchors** | Original crosswalk entries | sigma, sum, subscrl, rmw (4 entries) |
| **Association bridge** | Untouched | No modifications to `AssociationRecord` or bridge logic |

---

## Versioning Protocol

| Artifact | Purpose | Mutability |
|---|---|---|
| `glyph_identity_registry_baseline.json` | Pre-Unicode expansion snapshot | **IMMUTABLE** |
| `glyph_identity_registry.json` | Working registry (will become v1) | Mutable during expansion |
| `glyph_identity_registry_v1.json` | Post-Unicode expansion | **IMMUTABLE** (produced after acceptance) |
| `glyph_unicode_reconciliation_report.md` | Mapping accounting report | **IMMUTABLE** |

---

## Unicode Expansion — Acceptance Checkpoint

### Required Outputs

1. **Updated registry** (`glyph_identity_registry_v1.json`)
   - 1,182 canonical identities retained
   - `unicode_code_point` populated for all entries (from Metamath `symbols.html`)
   - `wolfram_name` / `sympy_name` populated where Unicode matches existing dicts
   - `mapping_status` ∈ {`verified`, `unmapped`, `ambiguous`} for each entry
   - `ambiguity_notes` for explicit one-to-many or conflicting mappings
   - All provenance fields preserved (`provenance_sha256`, `source_reference`, etc.)

2. **Reconciliation report** (`glyph_unicode_reconciliation_report.md`)
   - Per-entry accounting: mapped / unmapped / ambiguous counts
   - Unicode coverage statistics
   - Comparison against Wolfram (82) + SymPy (77) dictionaries
   - Explicit list of ambiguous mappings (multiple visual identities → same Unicode)
   - Regression test results for original 4 crosswalk entries

3. **Regression tests**
   - `test_glyph_identity_registry.py` validates:
     - 1,182 entries retained
     - Original 4 crosswalk entries unchanged
     - No inferred mappings (all `None` for missing)
     - `ambiguity_notes` populated where applicable

### Acceptance Criteria

| Criterion | Verification |
|---|---|
| 1,182 canonical identities retained | Registry entry count |
| Every Unicode assignment has source provenance | `source_reference` + `verification_method` fields |
| No inferred mappings | All missing = explicit `null`, no fallback values |
| Ambiguous mappings explicit | `ambiguity_notes` non-empty for affected entries |
| Notation dictionaries unchanged | `scripts/math_notation_mapping.py` not modified |
| Original 4 crosswalk pass regression | Test suite passes |
| Baseline registry preserved | `glyph_identity_registry_baseline.json` exists, identical to pre-expansion |

### No Certification Until

- Actual Metamath `symbols.html` parsing completes
- Regression tests execute and pass
- Reconciliation report reviewed and accepted

---

## File Usage Summary

| File | Purpose | Modified During Expansion |
|---|---|---|
| `DATASETS/math_symbols/manifest.json` | Canonical 1,182 entries | No |
| `DATASETS/math_symbols/provenance_manifest.json` | SHA-256, revision, license | No |
| `symbols.zip` | Visual asset catalog | No |
| `scripts/math_notation_mapping.py` | Wolfram/SymPy dicts (read-only) | No |
| `glyph_identity_registry_baseline.json` | Immutable pre-expansion registry | No (reference only) |
| `glyph_identity_registry.json` → `glyph_identity_registry_v1.json` | Working → immutable output | Yes |
| `glyph_unicode_reconciliation_report.md` | Mapping accounting report | Yes (produced) |
| `test_glyph_identity_registry.py` | Regression tests | Yes (produced) |

---

## Provenance Separation (Protected)

| Provenance Type | Source | Does NOT Establish |
|---|---|---|
| Source-document SHA-256 | `provenance_manifest.json` | Individual asset integrity |
| Individual asset SHA-256 | Not yet computed | Mapping integrity |
| Mapping-record identity | Registry entry identity | Visual asset integrity |
| Verification evidence | `verification_method` + `verified_by` | Automatic certification |

---

## Variant Convention (Protected)

| Pattern | Interpretation |
|---|---|
| `rma.gif` / `rma.png` | Direct match to Metamath name `rma` |
| `_rma.gif` / `_rma.png` | Variant of `rma` (font/style/rendering) |
| **One `glyph_identity`** | Can have multiple `glyph_asset_id` entries |

---

## Pluto Exception (Protected)

| Entry | Status | Handling |
|---|---|---|
| `asteroid number 134340 formerly known as Pluto` | No visual asset in ZIP | Investigate independently; do not force into mathematical glyph classification |

---

## Next Action

When Unicode expansion begins:

1. Parse Metamath `symbols.html` → extract Unicode ↔ Metamath name mappings
2. Update `glyph_identity_registry.json` in place (working copy)
3. Produce `glyph_identity_registry_v1.json` + `glyph_unicode_reconciliation_report.md`
4. Run regression tests
5. Acceptance review against criteria above
6. Freeze `glyph_identity_registry_v1.json` as immutable

**No association bridge modifications until checkpoint accepted.**