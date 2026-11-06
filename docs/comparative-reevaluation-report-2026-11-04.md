# Comparative Reevaluation Report — Mathematical Structure Detection

**Date:** 2026-11-04  
**Paper:** 2605.06070 (ArenaPO)  
**Status:** Additive experiment — not a benchmark-validated improvement  
**Source:** External reviewer assessment + project evidence inventory

---

## 1. Purpose

This report compares existing spatial-observation machinery against the new `targeted_math_detector.py` rawdict-based character-geometry approach. The goal is to identify overlap, fragmentation, misses, and duplicate candidates—not to declare a winner.

## 2. Existing Components Already Developed

### A. `detect_math_regions_on_page()` + `expand_crop_context()`

- **Location:** `scripts/vision_comparison_pipeline.py`
- **Tests:** 88/88 context-preservation tests passing (reported)
- **Capability:** Connected-component grouping, math-region candidate detection, crop-context expansion with 2pt padding (8px at zoom=4)
- **Key distinction:** Region detection and context preservation are separate operations
- **Relevance to new detector:** The new detector's connected-component candidates may duplicate or fragment what this already identifies. The existing function groups components into math regions; the new detector treats each component independently.

### B. `targeted_depth_ocr.py` (existing pilot)

- **Location:** `scripts/targeted_depth_ocr.py`
- **Result on 2009.00031 p5:** 11 tall-narrow + 4 wide = 15 regions, 15/15 nonempty OCR
- **Method:** Original page at 4×, tall-narrow (3+ lines, aspect >2.5) + wide (10+ lines wide), crops at 8×
- **OCR output:** Matrix, array, fraction-like LaTeX structures
- **Caveat:** Recognition of `\begin{matrix}` does not prove correct structural recovery

### C. Spatial-Syntactic Preservation Specification

- **Location:** `docs/spatial-syntactic-preservation-specification.md` (284 lines)
- **Architecture:** Observation Layer → Structural Expectation Ledger → Reconstructed Hypothesis Layer
- **Expectation types (9):** delimiter pairing, fraction bar, superscript attachment, subscript attachment, multi-line alignment, notation definition, horizontal separator, vertical separator, indentation
- **Hypothesis types (7):** complete expression, partial expression, symbol substitution, structural ambiguity, missing component, false positive, unresolved
- **Key principle:** Unresolved expectations must remain visible, not silently discarded

### D. Pix2Text Crop-Isolation Experiments

- **Reported results:** 20/21 isolated crops (later config), 9/21 recognition agreement (42.9%)
- **Earlier baseline:** 2/21 isolated, 1/21 agreement
- **Key lesson:** Crop isolation improved dramatically; semantic agreement remained much lower. Detection success ≠ recognition success.

### E. OCR Polarity Ablation

- **8 crops tested:** original vs inverted polarity
- **Results:** 0/5 nonempty originals match inverted; 3 empty-to-empty (shared failures)
- **Error classes:** deletion, substitution, case_change, recognition failure
- **Conclusion:** Original polarity better-supported for tested sample

### F. Glyph Catalog Audit

- **3,304 catalog entries, 2,120 unique names, 1,184 duplicate names, 1,595 unique image hashes**
- **21 visually identical groups with different names**
- **P1 template-matching spec:** normalized image representations, candidate retrieval, provenance
- **Key lesson:** Visual similarity ≠ mathematical identity

---

## 3. New Detector: `targeted_math_detector.py` v1.1

### Method

1. **Character-level extraction** via PyMuPDF `get_text('rawdict')` — per-character bounding boxes
2. **Math-character filtering** via Greek/MATH/MATH_PUNCT sets + TARGET_LATEX_NAMES
3. **Geometry candidates** — tall glyphs (h > 1.35×median, aspect > 1.25), small scripts (h < 0.72×median), wide operators (w > 1.8×median)
4. **Script position candidates** — small glyphs compared against nearby normal glyphs; superscript/subscript by vertical offset
5. **Visual components** — connected components via Otsu threshold + connectedComponentsWithStats; tall_narrow (h ≥ 1.5×w, h ≥ 12) or wide_horizontal (w ≥ 30, h ≥ 5, w/h ≥ 2.0)

### ArenaPO Run (partial — killed at page 17/19)

| Page | Components | Notes |
|------|-----------|-------|
| 1-17 | 10,829 total | Process killed before completion; page 17 had 496 components |
| 18-19 | Not processed | Process terminated |

**Critical observation:** Page-wide median character height is used as baseline, but different font sizes and equation styles distort this. The visual connected-component count is extremely high (1,000+ per page), producing massive crop output.

---

## 4. Comparative Lineage-Preserving Table

| Source region | Observed glyphs | Geometry | Expected relationship | Candidate interpretation | Validation |
|---|---|---|---|---|---|
| 2009.00031 p5 (existing pilot) | 229 regions, 202/229 (88.2%) text overlap | Region boxes [347,310,31,35] etc. | Math region candidate | region_no_equation (360 parser candidates) | 98.6% overlap, 0 OOB |
| ArenaPO p1-17 (new detector) | 10,829 visual components | Connected components via Otsu | Tall delimiter / wide bar candidate | unverified_visual_candidate | **NOT VALIDATED** — process killed, no JSON output |
| ArenaPO p5 (existing targeted_ocr) | 11 tall + 4 wide regions | Horizontal projection + connected components | Tall-narrow (3+ lines, aspect >2.5) + wide (10+ lines) | `\begin{matrix}`, `\begin{array}` OCR | 15/15 nonempty, but structural correctness not established |
| ArenaPO Appendix A (expected) | θ, μ, σ, β, Φ, posterior means/variances | — | Subscript/superscript attachment, Gaussian density | Not yet tested | Pending |
| ArenaPO Appendix B (expected) | Q_D, μ_D, σ_D², φ, Φ, λ(α), integrals | — | Fraction structure, conditional inequality Q_D>0 | Not yet tested | Pending |
| ArenaPO Section 4.2 (expected) | Q_w, Q_l, Q_D*, normal distributions | — | Subscripts, squared terms, sqrt, conditional inequality | Not yet tested | Pending |

---

## 5. Specific Weaknesses of the New Detector (Avoidable)

| Current behavior | Problem | Existing work to reevaluate |
|---|---|---|
| Page-wide median character height | Different font sizes and equation styles distort baseline | `extract_text_boundaries()` (PDF text boundaries) |
| Small glyph = script candidate | Small Greek symbols, footnotes, subscripts look similar | Spatial expectation ledger (attachment unresolved, not classified) |
| Tall connected component = delimiter candidate | Stretched brace may consist of multiple disconnected pieces | `detect_math_regions_on_page()` (groups components into regions) |
| Wide component = horizontal operator | Bar can be fragmented or share geometry with unrelated marks | `detect_partial_formulas()` (partial/inline formula regions) |
| Nearby glyphs as attachment references | Nearby characters may not be mathematically related | Spatial relation extraction (not yet implemented) |
| Otsu threshold as detection representation | Thin strokes and adjacent symbols may split or merge | Crop-isolation and polarity experiments (original image canonical) |
| PDF text as symbol source | Font encoding may omit or mis-map symbols | Original-page image + multiscale OCR |

**Critical issue:** `script_position_candidates()` compares small glyphs against nearby normal characters from across the page. It does not first establish that those characters belong to the same expression or baseline. This makes superscript/subscript classifications preliminary at best.

---

## 6. Reevaluation Priority Order

1. **Existing candidate geometry vs new detector** — Compare 15-region `2009.00031` pilot with new detector. Establish overlap, fragmentation, misses, duplicates.
2. **Character-level coordinate extraction** — Verify PyMuPDF `rawdict` character boxes against actual page renders. Pay attention to font substitutions, Greek glyphs, unusual font metrics.
3. **Tall delimiter reconstruction** — Test braces, brackets, parentheses, overbraces spanning multiple lines. Preserve component parts and relationships.
4. **Superscript/subscript attachment** — Use actual expressions from Appendices A-B. Test raised/lowered symbols against candidate base glyphs, not page-wide median.
5. **Fraction and horizontal-bar relationships** — Distinguish fraction bars from minus signs, overlines, separators. A horizontal line alone cannot establish mathematical role.
6. **Page-level structural continuity** — Test whether detector preserves expressions spanning multiple lines and retains page-local definitions/notation.

---

## 7. ArenaPO Fixed Test Vocabulary

Instead of testing arbitrary symbols, use the paper's actual mathematics as a controlled target set.

### Appendix A — Bayesian updating
- θ_i, μ_i, σ_i, β_i
- Φ(·), Gaussian density terms
- Posterior means and variances
- Subscripts, superscripts, squared terms
- Conditional probability and likelihood expressions

### Appendix B — Truncated normal
- Q_D = Q_w - Q_l
- μ_D, σ_D²
- φ(α), Φ(α)
- Integrals, fraction structures, conditional inequality Q_D > 0

### Section 4.2 — Quality-gap estimation
- Q_w, Q_l, Q_D*
- Normal distributions
- Difference variance
- Truncation and inverse Mills ratio

### Appendix C — Arena tables
- μ, σ, score columns
- Decimal values, row/column alignment
- Header-to-value relationships

### Appendix E — Evaluation tables
- Numeric scores, decimal precision
- Method labels, column alignment
- Relative ordering

---

## 8. Required Controls Before Next Detector Run

The partial run exposed four missing controls. These must be implemented before any further full-page detector execution.

| Control | Required behavior |
|---------|-------------------|
| **Incremental persistence** | Write one page record at a time, preferably append-only JSONL. Page 17 failing must not erase structured evidence from pages 1–16. |
| **Candidate grouping** | Group related components into regions before producing crops. A delimiter may consist of multiple disconnected pieces; a fraction bar may relate to several components. |
| **Candidate limits** | Record thresholds, candidate counts, and rejected components. Do not discard small components (tiny superscripts, decimal points, Greek symbols may be significant) — reduce redundant crop generation while preserving original observations. |
| **Duplicate control** | Preserve overlapping candidates but identify their overlap relationships (IoU, intersection, containment). |

**Separate execution outputs into:**
- `page_observations.jsonl` — per-page character and geometry observations
- `region_candidates.jsonl` — grouped region candidates with overlap relationships
- `candidate_crop_manifest.jsonl` — crop metadata without the actual PNGs
- `execution_manifest.json` — run-level summary with thresholds, counts, rejected components

---

## 9. Three Independent Architectural Questions

These must remain independent. A system can succeed at one and fail at another.

| Question | Definition | Current status |
|----------|-----------|----------------|
| **Detection** | Did we find the relevant visual material? | Partial — 10,829 components found, but unclassified |
| **Preservation** | Did we retain the material and its spatial context? | Partial — crops generated but not structured; no JSON output |
| **Interpretation** | Did we correctly understand its mathematical relationships? | Not started — no structural validation performed |

This separation is particularly important for ArenaPO because distinguishing σ from β depends not only on recognizing Greek letters but correctly preserving their subscripts and mathematical roles.

---

## 10. Recommended Execution Sequence

1. **Complete** — Freeze comparative report (this document) and partial detector output as separate evidence artifacts.
2. **Complete** — OCR polarity ablation (8 crops, original/inverted distinctions preserved).
3. **Preserve** — 137-crop DA-V2 baseline (no changes or regeneration).
4. **Bounded detector comparison** — Compare existing 15-region pilot with new detector observations. Establish overlap, fragmentation, misses, false positives. Do NOT launch another full 19-page run yet.
5. **Spatial-syntactic Observation Layer** — Implement existing specification independently, beginning with source geometry and structural expectations.
6. **Structural recovery evaluation** — Measure delimiter pairing, script attachment, fraction relationships, multiline continuity, semantic correctness independently of OCR accuracy.

---

## 11. Key Principle

The missing piece is not another detection algorithm. It is the **controlled relationship between observations**: which glyphs belong together, what spatial structure they form, and whether the resulting mathematical interpretation is correct.

Detection precision and recall, crop/context preservation, symbol recognition accuracy, and structural relationship accuracy must be measured independently. Successful component detection must not be used as a proxy for successful symbol recognition or structural recovery.

No frozen baseline needs to be modified to implement the controls in Section 8.
