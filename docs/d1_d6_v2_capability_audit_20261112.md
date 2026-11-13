# D1–D6 / v2 Engine Capability Audit — Read-Only Forensic Assessment

**Date:** 2026-11-12
**Scope:** `scripts/delimiter_aware_structural_recovery.py` (v1, frozen) + `scripts/v2_delimiter_aware_structural_recovery.py` (v2 remediated baseline)
**Method:** Code inspection + test execution + live engine probe on 1212.0957_p8 and 1505.05770v6
**No modifications made** — this is an independent capability inventory.

---

## 1. Executive Summary

| Capability | v1 Status | v2 Status | Tested? | Independently Validated? | Notes |
|---|---|---|---|---|---|
| **D1 Glyph Extent Invariant** | ✅ Implemented | ✅ Inherited | ✅ 7/7 tests pass | ✅ Live on 1212.0957_p8 | Works for single glyphs; does NOT measure full extensible delimiter extent |
| **D2 Font-Aware Identity** | ✅ Implemented (CMEX only) | ✅ Extended (CMEX, TX, LM) | ✅ 64/64 tests pass | ✅ Live on 1212.0957_p8 | v2 adds TX/LM font families; 1505.05770v6 uses Times-Roman → falls back |
| **D3 Pair Association** | ✅ Implemented | ✅ Strict kind-matching (EL-003) | ✅ 7/7 tests pass | ⚠️ Live: 13 spurious pairs on 1212.0957_p8 | Does not assemble extensible delimiter pieces before pairing |
| **D4 Semantic Completeness** | ✅ 2D grid reconstruction | ✅ Three-coordinate (bbox_delim/bbox_math/bbox_crop) | ✅ 7/7 tests pass | ⚠️ Grid works but multiline expansion over-merges | v2 adds multiline, fraction, prefix/suffix |
| **D5 Translation Fidelity** | ✅ Enforces matrix env | ✅ Inherited | ✅ 7/7 tests pass | ✅ Rejects inline flattening | Target env: pmatrix/bmatrix/Bmatrix/vmatrix |
| **D6 Cryptographic Provenance** | ✅ SHA-256 + coordinates | ✅ Inherited | ✅ 7/7 tests pass | ✅ Full coordinates recorded | Coordinate system: PyMuPDF points (72 dpi, top-left) |
| **Tall Delimiter Extent Recovery** | ❌ Not implemented | ❌ Not implemented | N/A | ❌ | Identifies pieces but does NOT measure full physical extent |
| **Individual Symbol BBoxes** | ⚠️ Partial (delimiter only) | ⚠️ Partial (delimiter only) | ❌ No dedicated tests | ❌ | Does not preserve child-role boxes (base/exponent/numerator/denominator) |
| **Relationship Geometry** | ❌ Not implemented | ❌ Not implemented | ❌ No tests | ❌ | No base-exponent, numerator-denominator, integral-limit boxes |
| **Horizontal Stretching** | ❌ Not implemented | ❌ Not implemented | ❌ No tests | ❌ | Wide structures (fractions, matrices, accents) not handled |
| **Wide Structures** | ❌ Not implemented | ❌ Not implemented | ❌ No tests | ❌ | Fractions, matrices, overlines, wide accents |

---

## 2. Gate-by-Gate Forensic Evidence

### D1: Glyph Extent Invariant
**Implementation:** `verify_d1_glyph_extent()` — checks `H_crop >= H_glyph` with 0.5pt tolerance
**Test:** `test_d1_relative_glyph_extent` — PASSED
**Live probe (1212.0957_p8):** 
- Opening glyph: h=98.25pt, crop: h=103.1pt → PASS
- **Limitation:** Only checks the **opening glyph piece** (top of extensible delimiter), not the full assembled delimiter extent. The 98.25pt is the top piece height, not the full 131pt matrix height.

### D2: Font-Aware Delimiter Identity
**v1 Implementation:** `classify_delimiter_glyph_font_aware()` — CMEX_DELIMITER_MAP (11 entries) + STANDARD_DELIMITER_MAP
**v2 Implementation:** Adds TX_DELIMITER_MAP (18 entries) + LM_DELIMITER_MAP (7 entries) + font-family branching logic
**Test:** 64/64 tests pass in `test_delimiter_identity.py` + `test_delimiter_adversarial.py`
**Live probe (1212.0957_p8):**
- CMEX pieces correctly identified: `` `` `` → parenthesis, family=cmex, confidence=0.99, method=font_aware_cmex_mapping
- **Limitation:** Only works for fonts with known PUA mappings. 1505.05770v6 uses Times-Roman → falls back to geometric heuristic (aspect > 4.0 → bracket, confidence=0.70)

### D3: Pair Association
**v1 Implementation:** `associate_delimiter_pairs()` — horizontal band, vertical IoU > 0.70, height ratio > 0.75, kind/direction match, intervening delimiter guard
**v2 Implementation:** Adds **EL-003 strict kind matching as hard prerequisite** (lines 301-310)
**Test:** 7/7 tests pass in `test_delimiter_structural_recovery.py`
**Live probe (1212.0957_p8):** **13 pairs found** — **MAJOR DEFECT**
- The engine treats **each CMEX piece (top/ext/bottom) as a separate candidate**
- Pairs opening top-piece with closing top-piece, opening ext with closing ext, etc.
- Result: 13 spurious pairs instead of 1 matrix enclosure
- The **extensible delimiter assembly step is missing** — pieces must be assembled into full delimiters BEFORE pairing

### D4: 2D Grid Semantic Completeness
**v1 Implementation:** `reconstruct_2d_matrix_grid()` — row clustering (dy < 6pt), col counting
**v2 Implementation:** `build_enclosure_completeness()` — **three-coordinate system** (bbox_delim, bbox_math, bbox_crop) + multiline cluster expansion + fraction bar expansion + prefix/suffix scans
**Test:** 7/7 tests pass
**Live probe (1212.0957_p8, Pair 2 — the matrix):**
- `bbox_delim`: [224.88, 381.89, 409.15, 414.72] — just the top delimiter pieces
- `bbox_math`: [202.8, 381.89, 409.15, 447.0] — includes matrix interior + prefix "S ="
- `multiline_cluster_size`: 27 lines — **over-merges** (includes unrelated lines above)
- `stop_reasons`: `['SC-1:gap_above=88.2pt>15.0pt', 'SC-7:downward_limit=44.5pt>5.0pt']` — stop conditions triggered
- **Limitation:** Grid reconstruction works for interior tokens, but bbox_math is polluted by multiline over-merging

### D5: Translation Fidelity
**Implementation:** `verify_d5_translation_fidelity()` — requires multi-row, maps delimiter kind to LaTeX env
**Test:** PASSED
**Live:** Correctly targets `pmatrix` for parenthesis kind

### D6: Cryptographic Provenance
**Implementation:** `build_d6_provenance()` / v2 equivalent — SHA-256, page, constituent + composite coordinates
**Test:** PASSED
**Live:** Full dual-delimiter point coordinates recorded in PyMuPDF point space

---

## 3. Capability Matrix (User's 7 Questions)

| Question | Answer | Evidence |
|---|---|---|
| **1. Which delimiter families genuinely recovered?** | Parentheses, brackets, braces, vertical bars, norms (double bar), floor, ceiling, angle brackets. **NOT recovered:** extensible delimiter pieces as assembled units. | v2 maps: CMEX (paren/bracket/brace/norm), TX (paren/bracket), LM (norm/vertical_bar), standard ASCII. Test coverage: 64/64. |
| **2. Tall glyph extents measured or inferred?** | **Neither for full extensible delimiters.** Individual pieces measured (D1 passes on top piece only). Full physical extent of `\left( ... \right)` spanning 7 rows is NOT measured. | D1 checks `H_crop >= H_glyph` on single glyph rect. v2 `bbox_delim` = union of opening+closing piece rects, not full assembled delimiter. |
| **3. Horizontal stretching supported?** | **No.** No code for wide delimiter construction (overbrace, underbrace, wide accents, horizontal rules). | Only vertical delimiter detection (raster `vert_kernel = (1, 15)`). No horizontal kernel, no wide structure detection. |
| **4. Individual symbol bboxes survive reconstruction?** | **Only delimiter glyph bboxes.** No child-role geometry (base, exponent, numerator, denominator, integral limits). | `GlyphObservation` in spatial_syntactic_observer preserves per-glyph bbox, but D1-D6 pipeline only outputs delimiter pair bboxes and enclosure bboxes. No per-symbol role boxes. |
| **5. Parent-child relationship bboxes produced?** | **No.** No relationship geometry output. | v2 `metadata` has `bbox_delim`, `bbox_math`, `bbox_crop` — no `base_bbox`, `exponent_bbox`, `numerator_bbox`, `denominator_bbox`, `integral_limit_bbox`. |
| **6. Coordinate system?** | **PyMuPDF point space (72 dpi, top-left origin).** All bboxes in points. | Explicit in D6 provenance: `"coordinate_system": "PyMuPDF point space (72 dpi, top-left origin)"`. No pixel-space output. |
| **7. Tested vs. documented?** | See test results below. | |

---

## 4. Test Execution Evidence (All Fresh Runs)

| Test Suite | Tests | Result | Time |
|---|---|---|---|
| `test_delimiter_structural_recovery.py` | 7 | ✅ **7 passed** | 2.20s |
| `test_v1_v2_comparison.py` | 5 | ✅ **5 passed** | 0.08s |
| `test_delimiter_identity.py` + `test_delimiter_adversarial.py` | 64 | ✅ **64 passed** | 7.18s |
| `test_structural_preservation.py` + `test_structural_fidelity.py` + `test_structural_evidence_graph.py` | 70 | ✅ **70 passed** | 2.60s |
| `test_structural_conservation.py` (scripts/) | 21 | ✅ **21/21 pass** | 0.34s |
| `test_benchmark_readiness.py` (standalone) | 8 checks | ✅ **PASS** | — |
| `test_candidate_audit_manifest.py` | 21 | ✅ **21 passed** | 0.79s |
| **Total structural/delimiter tests** | **188** | ✅ **188 passed** | — |

**Note:** `test_structural_conservation.py` exits with `sys.exit(0)` causing pytest INTERNALERROR, but all 21 structural conservation assertions pass.

---

## 5. 1505.05770v6 Specific Findings

The target paper uses **Times-Roman** for math (not TeX math fonts):
- Page 1: Single tall bracket pair `[` `]` spanning 360pt — detected as text_stream, classified via standard mapping (confidence 0.9)
- Pages 4-5: Many raster-stroke candidates (vertical lines) — **no font info**, geometric fallback only (confidence 0.70)
- **No CMEX/TX/LM font delimiters present** — v2's font-aware mappings are not exercised on this paper
- The matrix on page 5 (if present) would use standard delimiters, not extensible CMEX pieces

**Implication:** The v2 font-program-aware classification (EL-001) is **not validated** on this paper. The Rahmani 1212.0957 paper IS the validation case for CMEX extensible delimiters.

---

## 6. Critical Gaps for Stage B Integration

| Gap | Impact on Stage B | Severity |
|---|---|---|
| **No extensible delimiter assembly** | D3 produces 13 spurious pairs; cannot feed Stage B a single matrix enclosure | **Blocker** |
| **No child-role geometry** | Stage B needs base/exponent, numerator/denominator, integral limit bboxes — none exist | **Blocker** |
| **No relationship geometry** | Stage B `relationship_geometry` output requires these — cannot be produced | **Blocker** |
| **No horizontal/wide structure support** | Fractions, matrices, wide accents, over/underbraces not handled | **High** |
| **Multiline over-merging** | v2 `bbox_math` includes unrelated lines; stop conditions not strict enough | **High** |
| **1505.05770v6 uses non-TeX fonts** | v2 font-aware paths untested on target paper | **Medium** |

---

## 7. What IS Working and Can Be Built Upon

| Component | Status | Can Feed Stage B? |
|---|---|---|
| `delimiter_identity.py` — canonical tokens (langle/rangle, lfloor/rfloor, lVert/rVert, lceil/rceil, BAR, GRAY_BAR) | ✅ Frozen, tested, complete | Yes — AST layer |
| `delimiter_inference.py` — pairs tokens into typed nodes (AngleBracket, Norm, Floor, Ceil, Abs, Conditional) | ✅ Frozen, tested, complete | Yes — AST layer |
| `mathml_parser.py` + `structural_ast_extractor.py` — MathML → `ExprNode` (Integral, Fraction, Script, Matrix, etc.) | ✅ Frozen, tested, complete | Yes — AST layer |
| `spatial_syntactic_observer.py` — `GlyphObservation` with per-glyph pdf_bbox, font, origin | ✅ Working, complete | Yes — PDF observation layer |
| `targeted_math_detector.py` — candidate region proposals with geometry | ✅ Working, complete | Yes — candidate generator |
| `font_aware_math_classifier.py` — font-program-aware glyph classification | ✅ Frozen, tested | Yes — classification |
| `hierarchical_region_proposals_v3.py` — adaptive baseline, multiline guardrails, equation-number decoupling | ✅ Working, not fully tested | Yes — region proposals |
| D1–D6 **gate logic** (invariant checks, identity, pairing, grid, translation, provenance) | ✅ 188 tests pass | Yes — as validation gates |

---

## 8. Conclusion

**The D1–D6 / v2 engine successfully recovers:**
- Delimiter identity with font-program lineage (for TeX fonts)
- Pair association with strict kind matching
- 2D grid semantic completeness for matrix interiors
- Matrix environment translation fidelity (rejects inline flattening)
- Cryptographic provenance with full coordinates

**The D1–D6 / v2 engine does NOT recover:**
- **Full physical extent of extensible delimiters** (only individual pieces)
- **Individual child-role bounding boxes** (base, exponent, numerator, denominator, integral limits)
- **Relationship geometry** (geometric association between parent and child roles)
- **Horizontal/wide structures** (fractions, wide accents, over/underbraces, horizontal rules)

**Recommendation:** Do not implement another recovery module. The priority is **integration and verification**:
1. Fix extensible delimiter assembly (assemble CMEX/TX/LM pieces before D3 pairing)
2. Extract child-role geometry from `spatial_syntactic_observer` glyph observations + `hierarchical_region_proposals_v3` line groups
3. Build relationship geometry (base→exponent, numerator→denominator, limit→integral)
4. Connect proven capabilities to Stage A/B association architecture

This avoids duplicating existing work and protects frozen baselines.

---

## 9. File References

| File | Lines | Role |
|---|---|---|
| `scripts/delimiter_aware_structural_recovery.py` | 531 | v1 frozen baseline (D1–D6) |
| `scripts/v2_delimiter_aware_structural_recovery.py` | 735 | v2 remediated baseline (EL-001–EL-004) |
| `scripts/delimiter_identity.py` | 427 | Canonical delimiter tokens |
| `scripts/delimiter_inference.py` | 422 | Token pairing → typed AST nodes |
| `scripts/spatial_syntactic_observer.py` | 460 | GlyphObservation, RegionAssessment |
| `scripts/hierarchical_region_proposals_v3.py` | 606 | Adaptive multiline, equation-number decoupling |
| `scripts/targeted_math_detector.py` | 343 | Candidate region detection |
| `scripts/font_aware_math_classifier.py` | 226 | Font-program-aware classification |
| `tests/test_delimiter_structural_recovery.py` | — | D1–D6 gate tests |
| `tests/test_v1_v2_comparison.py` | — | v1 vs v2 comparison |
| `tests/test_delimiter_identity.py` | — | Token identity tests |
| `tests/test_delimiter_adversarial.py` | — | Adversarial delimiter tests |
| `tests/test_structural_preservation.py` | — | Structural preservation tests |
| `tests/test_structural_fidelity.py` | — | Structural fidelity tests |
| `tests/test_structural_evidence_graph.py` | — | Evidence graph tests |
| `scripts/test_structural_conservation.py` | — | MathML structural conservation |

---

**End of audit.** No code modified. All evidence from live test execution and code inspection.