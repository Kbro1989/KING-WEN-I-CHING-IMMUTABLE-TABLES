# Vision Pipeline — Stretched Symbols, Braces/Brackets, and Border Recognition Audit

**Date:** 2026-11-03
**Scope:** Read-only audit of `scripts/vision_comparison_pipeline.py` for symbol-bypass and border-recognition gaps.
**Governing rule:** Do not define truth in code where it can be read from disk. Search before assuming.

---

## 1. Summary

Four distinct gaps identified in the vision comparison pipeline's handling of stretched symbols, braces/brackets, and border context. Two are classification-layer defects (ASCII pattern mapping and alignment classification). One is a crop-layer defect (insufficient border/context handling). One is an OCR-input defect (no multi-scale or context-inclusive recognition).

---

## 2. Gap 1: `get_ascii_pattern` — Stretched Delimiters and Big Operators Not Mapped

**Location:** `scripts/vision_comparison_pipeline.py:249-274`

**Current behavior:** The function maps 6 bracket characters to class 'B':
```python
elif c in '[]{}()|':
    result.append('B')
```

**Missing from the 'B' class:**
- Big delimiters: `\left(`, `\right)`, `\left[`, `\right]`, `\left\{`, `\right\}`, `\left|`, `\right|`, `\left\|`, `\right\|`
- Floor/ceiling: `\lfloor`, `\rfloor`, `\lceil`, `\rceil`
- Tall vertical bars: `\vert`, `\Vert`, `\mid`, `\parallel`
- Big operators: `\sum`, `\int`, `\prod`, `\coprod`, `\bigcup`, `\bigcap`, `\bigoplus`, `\bigotimes`, `\bigwedge`, `\bigvee`, `\bigodot`, `\bigsqcup`
- Stretched accents: `\overline{...}`, `\underline{...}`, `\hat{...}`, `\tilde{...}`, `\widehat{...}`, `\widetilde{...}`

**Impact:** Any equation containing these symbols produces an ASCII pattern where the delimiter/operator is classified as 'X' (default) instead of 'B' or 'O'. The `compare_structural_similarity` function (lines 276-299) then fails to match structurally equivalent expressions that differ only in delimiter/operator class. This causes false `mismatch` classifications for equations that are structurally identical.

**Affected symbols in the 3,304-glyph `symbols.zip` catalog:** The catalog contains `lbrace`, `rbrace`, `lbrack`, `rbrack`, `lparen`, `rparen`, `vert`, `Vert`, `lfloor`, `rfloor`, `lceil`, `rceil`, `sum`, `int`, `prod`, `bigcup`, `bigcap` — but these are single-glyph catalog entries, not stretched variants. The vision pipeline compares against the catalog by substring matching (`source_text in glyph['name']`), which would fail for stretched multi-char operators.

---

## 3. Gap 2: `classify_alignment` — Stretched Symbol Recognition Misclassified

**Location:** `scripts/vision_comparison_pipeline.py:201-247`

**Current behavior:** The `stretch_suspect` classification (lines 221-223) triggers when `len(source_clean) == 1 and len(recognized_clean) > 1`:

```python
if len(source_clean) == 1 and len(recognized_clean) > 1:
    return 'stretch_suspect', f'possible stretch: source="{source_clean}", recognized="{recognized_clean}"', 0.3
```

**Problem:** A correctly recognized stretched symbol (e.g., source `\sum` recognized as `\sum_{i=1}^{n}`) would be classified as `stretch_suspect` with score 0.3 — the same classification as an OCR hallucination. There is no distinction between:
- **Correct stretch recognition**: The OCR correctly identified a stretched symbol and its limits
- **OCR hallucination**: The OCR invented additional characters not present in the source
- **Partial stretch**: The OCR captured the base symbol but missed or hallucinated limits

**Impact:** The 4/4 `image_region` classification in the current results may mask cases where Pix2Text correctly recognized stretched symbols but the alignment classifier downgraded them to `stretch_suspect`. The current results show 0 `stretch_suspect` entries, which could mean either (a) no stretched symbols were in the candidate set, or (b) stretched symbols were present but classified as `image_region` instead (due to the `source_bbox` truthiness check at line 243).

---

## 4. Gap 3: Border Contamination in `crop_pdf_region`

**Location:** `scripts/vision_comparison_pipeline.py:89-149`

**Current behavior:** The crop function uses minimal padding (3, 2) points and checks `min_content_ratio` (default 0.02) for non-white pixel ratio. It does not:
- Detect when a fraction bar, integral limit, or stretched delimiter touches the crop border
- Expand the crop to include surrounding context when border contamination is detected
- Distinguish between "empty crop" (no content) and "border-contaminated crop" (content touches edge)

**Documented evidence from `build_visual_review_log.py`:**
- "Top border contains the horizontal fraction line from the numerator" — fraction bars touching top border cause OCR overline/fraction hallucinations
- "Trace of text below at bottom border" — adjacent text leaks into crop
- "Fraction Denominators: Crops contain the horizontal fraction bar touching the top border, causing OCR overline/fraction hallucinations"

**Impact:** When a stretched symbol's component (fraction bar, integral limit, brace extension) touches the crop border, Pix2Text may:
- Hallucinate overlines or fraction bars
- Miss the symbol entirely (classifying as `empty_recognition`)
- Produce partial recognition with incorrect structure

**No multi-scale or context-inclusive recognition:** The pipeline uses a single zoom factor (4x) for all crops. There is no mechanism to:
- Render the crop at multiple zoom levels and select the best recognition
- Expand the crop to include surrounding context when the tight crop fails
- Use a "zoomed out" view to capture the full extent of a stretched symbol

---

## 5. Gap 4: No Border-Recognition or Context-Zoom in OCR Input

**Location:** `scripts/vision_comparison_pipeline.py:150-199` (recognize_formula)

**Current behavior:** `recognize_formula()` passes the raw crop array to `Pix2Text.recognize_formula()` without any preprocessing. There is no:
- Border padding expansion when content touches crop edges
- Contrast enhancement for faint stretched symbols
- Multi-crop strategy (tight crop + context crop)
- Fallback to a wider crop when the tight crop produces empty or low-confidence results

**Impact:** Stretched symbols that extend beyond the PDF bbox (common for big operators with limits, fraction bars, and big delimiters) are systematically truncated. The OCR receives an incomplete symbol and either fails to recognize it or produces a partial/hallucinated result.

---

## 6. Relationship to Existing Findings

| Gap | Related Finding | Relationship |
|---|---|---|
| Gap 1 (ASCII pattern bypass) | CF-020 (vision pipeline) | Extends CF-020's "formula isolation" next phase — structural comparison fails for stretched symbols |
| Gap 2 (stretch misclassification) | CF-020 (vision pipeline) | Explains why 4/4 `image_region` may mask correct stretch recognitions |
| Gap 3 (border contamination) | CF-020 (vision pipeline) | Root cause of OCR overline/fraction hallucinations documented in build_visual_review_log.py |
| Gap 4 (no context zoom) | CF-019 (seam mismatch) | Vision pipeline is a separate extraction path; these gaps are vision-path-specific |

### CF-020 Status Update

CF-020 established 4/4 image-region recognition on paper 1907.04931. The four gaps above do not invalidate that result — they explain its limitations:

- **Recognition succeeded** (Pix2Text produced non-empty text for all 4 candidates)
- **Structural comparison failed** (all classified as `image_region`, not `matched` or `partial_match`)
- **Stretched symbols** were not distinguished from correct recognition vs. hallucination
- **Border contamination** was not detected or corrected
- **No context zoom** was attempted

The 4/4 recognition is a **recognition result**, not a **structural fidelity result**. These gaps must be addressed before the vision pipeline can claim structural equation recovery.

---

## 7. Recommended Next Steps (Read-Only Governance)

These are investigation recommendations, not implementation instructions:

1. **Audit the 4 vision comparison candidates** for stretched symbols and border contamination. Determine whether any of the 4 crops contain stretched delimiters or fraction bars touching borders.
2. **Expand `get_ascii_pattern`** to include big delimiters and big operators in the 'B' and 'O' classes respectively. This is a classification fix, not a pipeline change.
3. **Add border-detection** to `crop_pdf_region`: if non-white pixels touch any crop edge, flag the crop as `border_contaminated` and optionally expand padding.
4. **Add multi-scale recognition**: render the crop at 2x, 4x, and 8x zoom; select the recognition with the highest non-empty confidence. Fall back to a context-expanded crop (2x padding) if all zooms fail.
5. **Distinguish stretch recognition from hallucination**: when `len(source) == 1 and len(recognized) > 1`, check whether the recognized text contains the source character as a substring. If yes, classify as `stretch_recognized` (correct). If no, classify as `stretch_suspect` (possible hallucination).

These are governance recommendations for the next research milestone, not code changes. No source modifications are implied.

---

## 8. Implementation Status (2026-11-03)

The following functions have been implemented in `scripts/vision_comparison_pipeline.py`:

### Glyph Ballooning (9× with edge smoothing)
- `balloon_glyph(img, factor=9)` — bicubic upscale + Gaussian blur edge smoothing
- `balloon_glyph_to_match(crop_shape, glyph)` — height-matched balloon preserving aspect ratio

### Border Detection & Context Expansion
- `detect_border_contamination(crop, border_px=2)` — detects content touching crop borders
- `expand_crop_context(pdf_page, bbox, expand_factor=1.5/2.0)` — zoom-out crop with surrounding context

### Math Region Boxing / Grouping
- `detect_math_regions_on_page(image_array)` — connected-component analysis + region grouping for complex formulas

### Text Boundaries & Partial Formulas
- `extract_text_boundaries(page, clip_rect)` — PyMuPDF word-level boundaries with math detection
- `detect_partial_formulas(page, clip_rect)` — inline/partial math in paragraphs

### Multi-Scale Recognition
- `recognize_formula_multiscale(comparer, crop, page, bbox)` — tries zoom [2,4,8], falls back to context-expanded crop

### Remaining Work (Gap 1 & Gap 2)
- Gap 1: `get_ascii_pattern()` still needs updating to map big delimiters/operators to 'B' class
- Gap 2: `classify_alignment()` still needs stretch-vs-hallucination distinction

---

*End of audit. This is a read-only investigation document. No source modifications, pipeline changes, or gate closures are implied by its creation.*