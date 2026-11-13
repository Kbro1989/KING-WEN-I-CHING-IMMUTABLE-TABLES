# Source-Level Reuse Audit: Association Bridge vs. Existing King Wen Work

**Date:** 2026-11-12
**Subject:** Mapping of 8 relationship types to existing code modules
**Scope:** Read-only audit of `scripts/` directory against the 8 association relationship contract types

---

## Executive Summary

The newly created `association_bridge.py` is correct in its design, but 6 of the 8
relationship types already have partial or complete implementations in the existing
codebase. Only 3 types (`integral_to_upper_lower`, `operator_to_operand`, `wide_accent`,
`crossed_script`) require genuinely new logic. `base_to_exponent` needs refinement of
existing script-position candidates.

**Recommendation:** Do not build new recovery modules. Reuse existing modules and wire
the association contract into them.

---

## 8 Relationship Types — Reuse Audit

### 1. `base_to_exponent`

**Status:** PARTIAL — no test evidence for association, only candidate generation

**Existing code:**
- `targeted_math_detector.py::script_position_candidates()` identifies small glyphs
  near normal-sized glyphs as `superscript_candidate` or `subscript_candidate`.
- `glyphs["attachment_status"] = "unresolved"`, `status = "geometric_hypothesis_only"`.

**Gap:** Identifies *candidates* but does not attach them to a specific base operator.
No baseline context, no horizontal association, no operator-to-operand mapping.

**Required new logic:** Baseline context (line group), horizontal association (same baseline
or within operator's horizontal span), attachment to a specific operator node.

**Verdict:** Do not build from scratch. Wire `script_position_candidates` into the
association bridge as a candidate provider; add baseline grouping from
`hierarchical_region_proposals_v3` to establish operator context.

---

### 2. `numerator_to_denominator`

**Status:** PARTIAL — detection exists, semantic confirmation missing

**Existing code:**
- `chroma_visual_reader.detect_2d_structures()` detects fractions using geometry-only
  heuristics. Produces `VisualMathStructure` with `components={"numerator": [...], "denominator": [...]}`.
- `targeted_math_detector.py` has fraction candidates but no explicit numerator/denominator
  association beyond pixel coordinates.

**Gap:** Visual fraction detection works, but there is no semantic confirmation that a
particular visual fraction corresponds to an AST `Fraction` node. No mapping to the
`structural_ast_extractor` AST.

**Required new logic:** Only association logic — map visual fraction coordinates to AST
node via glyph overlap and tree path.

**Verdict:** Wire `chroma_visual_reader.VisualMathStructure` into the bridge. No new
detection code needed.

---

### 3. `integral_to_upper_lower`

**Status:** NONE — no existing code handles integral or summation limits

**Existing code:**
- No module handles `\\int`, `\\sum`, `\\prod` with upper/lower limits.
- `chroma_visual_reader` classifies `stacked_limit` regions but does not produce
  `integral_to_upper_lower` relationships.

**Required new logic:** Integral/sum operator detection, limit detection above/below,
association to AST `Integral`/`Sum` nodes.

**Verdict:** Genuinely requires new logic. This is the highest-risk new relationship type.

---

### 4. `operator_to_operand`

**Status:** NONE — no existing code distinguishes operators from operands spatially

**Existing code:**
- `font_aware_math_classifier.py` classifies glyph *types* (operator, variable, function),
  but not *relationships*.
- No module produces `operator_to_operand` geometric associations.

**Required new logic:** Operator detection (functions, relations, operators), operand
detection (variables, numbers), geometric association via adjacency and AST order.

**Verdict:** Genuinely requires new logic. This is the most architecturally significant
new relationship type.

---

### 5. `delimited_group`

**Status:** PARTIAL — frozen v1 regression suite verifies pairing, but CMEX/TX/LM
piece assembly is not complete.

**Existing code:**
- `delimiter_identity.py`: canonical delimiter tokens.
- `delimiter_inference.py`: token pairing and typed AST nodes (AngleBracket, Norm, Floor,
  Ceil, Abs, Conditional).
- `delimiter_aware_structural_recovery.py`: frozen v1 pairing engine, 667/667 regression.
- D1–D6 gates test pair association and composite enclosure.
- v2 engine: `associate_delimiter_pairs` with strict kind matching (EL-003).

**Gap:** Existing work establishes token identity and pairing. What is missing is assembly
of CMEX/TX/LM pieces into a single physical delimiter (the 13-pair defect).

**Required new logic:** Only assembly of piece delimigers into single physical delimiters.

**Verdict:** Wire frozen v1/v2 engine output plus v2 `associate_delimiter_pairs` into the
bridge. No new detection logic.

---

### 6. `stacked_limit`

**Status:** PARTIAL — `chroma_visual_reader` classifies `stacked_limit` regions, but
no AST association or geometric definition

**Existing code:**
- `chroma_visual_reader.py`: `region_type = "stacked_limit"` is a classification label.
- No further logic for `integral_to_upper_lower` or operator limit association.

**Gap:** Classification label only. No geometric relationship definition, no AST node
association.

**Required new logic:** When is a region a `stacked_limit` vs a `script`? What is the
associated operator? Associate with `Integral`/`Sum`/`Product` nodes.

**Verdict:** Wire `chroma_visual_reader` classification into bridge. No new detection logic.

---

### 7. `wide_accent`

**Status:** NONE — no existing code handles over/under braces (overbrace, underbrace,
wide accents)

**Existing code:**
- `chroma_visual_reader` handles vertical structures (tall delimiters, fraction bars).
- No horizontal stretch/measurement logic.

**Required new logic:** Over/under accent detection, width measurement vs base, association
to AST node.

**Verdict:** Genuinely requires new logic.

---

### 8. `crossed_script`

**Status:** NONE — no existing code handles crossed scripts or cross-placement

**Existing code:**
- `targeted_math_detector.script_position_candidates()` identifies scripts relative to
  a single base glyph. Linear vertical positioning only.

**Required new logic:** Detection of scripts that are neither above (superscript) nor
below (subscript) relative to a base. Non-linear placement, e.g. Unicode subscript/superscript
characters.

**Verdict:** Genuinely requires new logic.

---

## Audit Summary Table

| Relationship Type | Existing Implementation | Test Evidence | New Logic |
|---|---|---|---|
| `base_to_exponent` | Partial (script candidates) | None | Medium |
| `numerator_to_denominator` | Partial (visual fractions) | Architecture documented | Medium |
| `integral_to_upper_lower` | None | None | High |
| `operator_to_operand` | None | None | High |
| `delimited_group` | Partial (token pairing + frozen regression) | 667/667 v1 regression | Medium |
| `stacked_limit` | Partial (region classification) | None | Medium |
| `wide_accent` | None | None | High |
| `crossed_script` | None | None | High |

---

## Revised Recommendation

Do not add four new recovery modules. Reuse existing:

| Relationship Type | Action |
|---|---|
| `base_to_exponent` | Reuse `targeted_math_detector.script_position_candidates`, add baseline grouping from `hierarchical_region_proposals_v3` |
| `numerator_to_denominator` | Reuse `chroma_visual_reader.detect_2d_structures()` |
| `integral_to_upper_lower` | New logic in association bridge |
| `operator_to_operand` | New logic in association bridge |
| `delimited_group` | Reuse frozen v1/v2 engine output + v2 `associate_delimiter_pairs` |
| `stacked_limit` | Reuse `chroma_visual_reader` region classification |
| `wide_accent` | New logic in association bridge |
| `crossed_script` | New logic in association bridge |

This replaces the proposed four new modules with:
- **1 new module** (3 high-risk relationship types: integral, operator, wide_accent, crossed_script)
- **0 rewrite modules** (delimited_group reused from frozen v1/v2)
- **0 replacement modules** (base_to_exponent, numerator_to_denominator, stacked_limit)

---

## Verification Boundaries

| Boundary | Preservation rule |
|---|---|
| MathML canonical route | Do not replace MathML-AST extraction with visual-only association |
| Pixel verification | PDF vision provides recovery and independent comparison, not canonical source |
| GlyphObservation | Consume, do not replace |
| VisualRegion | Consume, do not replace |
| Pix2Text adjudication | Preserve distinction: `SPATIAL_MATCH`, `TEXT_MATCH`, `VISUALLY_VERIFIED`, `ADJUDICATED`, `UNADJUDICATED` |
| Benchmark populations | Do not merge #14-paper benchmark with 243-paper batch population |
| Paper identity | Preserve paper_id in all association records |
| Occurrence identity | Preserve `source_occurrence` in all association records — expression hash is NOT occurrence identity |

---
**End of source-level reuse audit.**
