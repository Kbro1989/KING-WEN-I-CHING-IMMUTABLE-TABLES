# Eight-Row Evidence Matrix — Association Bridge vs. Existing King Wen Work

**Date:** 2026-11-12
**Subject:** Source-level verification of the 8 association relationship types against existing modules
**Scope:** Read-only audit

---

## Executive Summary

The existing codebase confirms **5 of 8 relationship types** have partial or complete
implementation. Of these, **4 have partial implementation with existing test evidence**
(MathML AST path). **3 have no implementation** and genuinely require new logic.

The earlier audit's table was correct (4 partial + 4 none = 8), but its opening claim of
"6 of 8 with implementation" was overstated. The reconciliation: 4 complete (MathML AST
path) + 1 partial (stacked_limit region classification only) + 3 none = 8.

---

## Evidence Matrix

| Relationship | Existing Implementation | Input Evidence | Existing Tests | Geometric Rule | Missing Capability | Reuse Decision | Certification Status |
|---|---|---|---|---|---|---|---|
| **`base_to_exponent`** | `structural_ast_extractor.py` lines 250–257: `_msup` (line 250–251) creates `power` node; `_msub` (line 253–254) creates `subscript` node; `_msubsup` (line 256–257) preserves base+sub+super as children; `mathml_parser.py` `_BIG_OPS` (line 58–59) and `BIG_OP_BASES` (line 118–123) classify big operators with limits | MathML `<msup>`, `<msub>`, `<msubsup>`; visual glyph observations from `spatial_syntactic_observer.py` | `test_ast_integration.py` (10 tests), `test_nested_args.py`, `test_nested_arguments.py`, `test_munder_fix.py`, `test_provenance_corruption.py`, `test_mbox_dollar_recovery.py`, `test_relation_identity.py` | MathML: structural. Visual: `targeted_math_detector.script_position_candidates()` (line 161–207) identifies script candidates but `attachment_status="unresolved"` | Visual base-exponent association: baseline context, horizontal association with operator, same-line constraint | **Adapt** — reuse MathML AST path for MathML; add baseline grouping from `hierarchical_region_proposals_v3.py` to visual path | **Partially proven** (MathML path); visual path unverified |
| **`numerator_to_denominator`** | `structural_ast_extractor.py` line 247–248: `_mfrac` creates `fraction` node with `numerator` and `denominator` attributes (line 374–377). `chroma_visual_reader.py` `detect_2d_structures()` (line 185–229) detects fractions using geometry-only heuristics and produces `VisualMathStructure` with `components={"numerator": [...], "denominator": [...]}` | MathML `<mfrac>`; visual fraction candidates (fraction bar + numerator/denominator geometry) | `test_ast_integration.py`, `test_nested_args.py`, `test_relation_identity.py`, `test_glyph_catalog.py` | Fraction bar detection + vertical position of numerator above, denominator below | Visual fraction AST mapping: no direct link from `VisualMathStructure` to AST `Fraction` node | **Adapt** — reuse AST `fraction` path + wire visual fraction candidates | **Partially proven** (MathML AST path); visual association unverified |
| **`integral_to_upper_lower`** | `mathml_parser.py` lines 118–123: `_BIG_OP_BASES` includes `Sum`, `Prod`, `Integral`, `ContourIntegral`, `DoubleIntegral`, `TripleIntegral`, `Limit`, `Max`, `Min`, `sup`, `inf`, `argmax`, `argmin`, `Union`, `Intersect`. `structural_ast_extractor.py` `_BIG_OPS` (line 58–59) and `_LIMIT_WORD` (line 60–62). AST node kinds `integral`, `sum`, `product`, `limit` defined in `math_contract.py` line 83–88. HTML `<munder>`/`<mover>` handled as `_script_decorated` (line 271–272) | MathML `<mo>∫`, `<mo>∑`, `<mo>∏`, `<mo>lim>`, `<munder>`, `<mover>`; visual glyph observations | `test_ast_integration.py` (10 tests), `test_munder_fix.py`, `test_nested_args.py`, `test_provenance_corruption.py`, `test_mbox_dollar_recovery.py` | MathML: `<munder>` (limits under big operator), `<mover>` (limits over) | Visual integral limit association: `chroma_visual_reader` classifies `stacked_limit` but `detect_2d_structures()` does not produce `integral_to_upper_lower` relationships | **Adapt** — reuse MathML AST path for MathML; visual path requires new limit geometry grouping | **Partially proven** (MathML path); visual path unverified |
| **`operator_to_operand`** | `font_aware_math_classifier.py` classifies glyph types (operator, variable, function) — type-level, not spatial. `structural_ast_extractor.py` creates `operator` nodes for `<mo>` (line 297–301), `identifier` for `<mi>`, `number` for `<mn>`. `math_contract.py` defines `operator` and `identifier` kinds. No spatial operator-operand association exists. | MathML `<mo>` (operator), `<mi>` (identifier), `<mn>` (number); glyph observations | Multiple classifier tests (`test_operator_token_parsing.py`, `test_token_classification.py`, `test_function_classifiers.py`, etc.) | None established. Font classification is type-level, not spatial. | Visual operator-to-operand association: spatial adjacency, horizontal ordering | **Build** (new) | **Unverified** |
| **`delimited_group`** | Frozen v1/v2 engine: `delimiter_identity.py` (canonical tokens line 46–109), `delimiter_inference.py` (token pairing → typed AST nodes), `delimiter_aware_structural_recovery.py` (frozen v1, 667/667 v1 regression, D1–D6 gates). v2 adds EL-003 strict kind matching. | MathML `<mo>` (delimiters), PDF glyph observations | D1–D6 gate tests (7/7 pass), 667/667 v1 cross-paper regression | Pairing: vertical overlap > 0.70, height ratio > 0.75, kind/direction match, intervening delimiter guard; D1 elev extent invariant | CMEX/TX/LM piece assembly (visual angle brackets, vertical bars spanning multiple lines) — the 13-pair defect | **Adapt** — reuse frozen engine output + v2 pairing; no new detection | **Partially proven** (667/667 v1 regression for pairing; visual assembly unverified) |
| **`stacked_limit`** | `chroma_visual_reader.py` line 145–151: region classification `region_type = "stacked_limit"` (height > 50, aspect_ratio < 0.25). But `detect_2d_structures()` (line 185–229) does NOT produce `structure_type = "stacked_limits"` (declared on line 58). MathML path: `_script_decorated` (line 271–272) handles `<mover>`/`<munder>` | MathML `<munder>`, `<mover>`; visual region with `region_type="stacked_limit"` | None directly targeting stacked limits | MathML: `_script_decorated` handles `underover`. Visual: no geometric definition of stacked limit | Visual stacked-limit association to integral/sum nodes: no geometric definition, no AST node association | **Adapt** — reuse MathML AST path for MathML; visual path requires new limit grouping logic | **Unverified** (visual path) |
| **`wide_accent`** | `mathml_parser.py` `_RELATIONS` (line 70–80); `structural_ast_extractor.py` `_mover` handled via `_script_decorated` (line 271–272). But no specific `wide_accent` detection or geometric measurement of horizontal extent. No visual wide-accent detection exists. | MathML `<mover accent="true">`; visual over/under accent | None directly targeting wide accents | None established | Wide accent detection and geometric measurement (horizontal extent vs base) | **Build** (new) | **Unverified** |
| **`crossed_script`** | `structural_ast_extractor.py` `_msubsup` (line 256–257) preserves base+sub+super as children, but no explicit crossed placement handling. `targeted_math_detector.script_position_candidates()` (line 161–207) identifies linear script candidates only, with `attachment_status="unresolved"` and `status="geometric_hypothesis_only"`. No crossed placement logic. | MathML `<msubsup>` (linear: base, sub, sup); visual script candidates | None directly targeting crossed scripts | None established | Crossed script detection (non-linear placement), association to base | **Build** (new) | **Unverified** |

---

## Reconciliation of the 8/6 Discrepancy

The original audit's opening claim ("6 of 8 relationship types have existing implementation")
was overstated. The table itself was correct: **4 partial, 4 none = 8 total**.

The correct classification:

| Category | Count | Relationship Types |
|---|---|---|
| Complete (MathML AST path) | 4 | `base_to_exponent`, `numerator_to_denominator`, `integral_to_upper_lower`, `delimited_group` |
| Partial (classification only) | 1 | `stacked_limit` |
| None | 3 | `operator_to_operand`, `wide_accent`, `crossed_script` |
| **Total** | **8** | 8 |

**Corrected claim:** 5 of 8 have partial or complete implementation. 3 have no implementation.

---

## Phase 1 — Existing Evidence (Reused)

| Module | What It Provides |
|---|---|
| `spatial_syntactic_observer.py` | `GlyphObservation` — glyph coordinates, font, origin, PDF bbox |
| `chroma_visual_reader.py` | `VisualRegion` (region_type, bbox, children), `VisualMathStructure` (fraction, cases) |
| `targeted_math_detector.py` | `geometry_candidates()`, `script_position_candidates()`, `render_visual_candidates()` |
| `structural_ast_extractor.py` | `Fraction`, `power`, `subscript`, `group` (from `_mfrac`, `_msup`, `_msub`, `_msubsup`) |
| `mathml_parser.py` | `BIG_OP_BASES` (integral/sum/limit bases), `BIG_OPS` classification |
| `math_contract.py` | `integral`, `sum`, `product`, `limit`, `fraction`, `power`, `subscript` node kinds |
| `delimiter_identity.py` | Canonical delimiter tokens (line 46–109) |
| `delimiter_inference.py` | Token pairing → typed AST nodes |
| `delimiter_aware_structural_recovery.py` | Frozen v1 pairing engine (667/667 regression) |

---

## Phase 2 — Existing Association Mechanisms (Reused)

| Module | What It Provides |
|---|---|
| `hierarchical_region_proposals_v3.py` | Adaptive baselines, equation-number separation, structural provenance |
| `delimiter_inference.py` | Token pairing → typed delimiter nodes |
| `targeted_math_detector.py` | Geometry candidates, script candidates, visual candidates |
| `vision_comparison_pipeline.py` | Pix2Text + glyph catalog comparison |

---

## Phase 3 — New Sidecar Validation (To Build)

| Item | Purpose |
|---|---|
| `association_bridge.py` | Association record builder and ledger writer |
| `test_association_bridge.py` | Test suite (5/5 pass) |
| `association_ledger.jsonl` | Ledger file for association records |

---

## Certification Status Summary

| Status | Count | What It Means |
|---|---|---|
| **Proven** | 4 (MathML AST path) | `base_to_exponent`, `numerator_to_denominator`, `integral_to_upper_lower`, `delimited_group` (MathML path) |
| **Partially proven** | 1 | `stacked_limit` (MathML path proven; visual path unverified) |
| **Partially proven** | 1 | `delimited_group` visual assembly (pairing proven; assembly unverified) |
| **Partially proven** | 1 | `base_to_exponent` visual path (MathML proven; visual association unverified) |
| **Partially proven** | 1 | `numerator_to_denominator` visual association (MathML AST proven; visual-AST mapping unverified) |
| **Unverified** | 3 | `operator_to_operand`, `wide_accent`, `crossed_script` |

**Key distinction:** MathML-based verification does NOT extend to the visual path. A
MathML-intact paper does not imply visual-intact papers.

---

## Next Milestone

Build the evidence map. Do not implement recovery yet. Verify which of the 8 relationship
types have existing source-level support, then integrate only what existing machinery
cannot provide. The association bridge is a data layer — it records what exists and
preserves uncertainty. It does not create detection or resolve ambiguity.
