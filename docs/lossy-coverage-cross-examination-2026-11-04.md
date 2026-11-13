# Lossy Coverage Cross-Examination — Math Coordinates vs Crop Boundaries

**Date:** 2026-11-04
**Scope:** Cross-examination of candidate bbox coordinates against actual crop behavior in vision pipeline
**Status:** Investigation only — no source changes

---

## 1. Candidate Population

| Metric | Value |
|---|---|
| Total candidates | 4,730 |
| Papers | 6 (1907.04931, 2104.01277, 2205.01395, 2206.00364, 2605.22902, 2605.27315) |
| Pages with candidates | 127 |
| Classifications | true_equation: 1,808 / inline_math: 2,366 / isolated_symbol: 556 |

## 2. Spatial Layout Findings

### 2.1 Multi-Line Clustering

| Metric | Value |
|---|---|
| Pages with multi-line clusters (gap < 5pt) | 118 / 127 (92.9%) |
| Total multi-line clusters | 1,000 |
| Max cluster size | 43 candidates |
| Isolated candidates (no neighbor) | 348 (7.4%) |
| Clustered candidates | 4,382 (92.6%) |
| Largest vertical span | 141.8pt (25 candidates, page 64 of 2104.01277) |

**Conclusion:** 92.6% of candidates are part of multi-line mathematical expressions. The current crop pipeline processes each candidate individually, destroying multi-line context.

### 2.2 Vertical Gap Distribution

| Gap range | Count | Meaning |
|---|---|---|
| Overlap (gap < 0) | 2,882 | Bboxes overlap vertically — same expression split across rows |
| < 2pt | 299 | Nearly touching — consecutive lines of same expression |
| 2-5pt | 201 | Close — likely same expression |
| 5-10pt | 308 | Moderate — possibly separate but related |
| 10-20pt | 389 | Larger — likely separate expressions |
| > 20pt | 524 | Clear separation |

**Conclusion:** 3,382 of 4,730 gaps (71.5%) are < 5pt, meaning the vast majority of math is spatially contiguous. Treating each bbox as an isolated crop loses this contiguity.

### 2.3 Height Distribution

| Classification | Count | Min | Max | Avg | Tall (>15pt) |
|---|---|---|---|---|---|
| true_equation | 1,808 | 4.7 | 22.2 | 11.3 | 65 (3.6%) |
| inline_math | 2,366 | 5.2 | 29.4 | 12.1 | 92 (3.9%) |
| isolated_symbol | 556 | 3.8 | 20.1 | 10.3 | 1 (0.2%) |

**Tall bboxes (>20pt):** 84 total, all from paper 2104.01277. These are stretched symbols (likely delimiters, large operators, fraction bars) that span 2-3 lines of normal text height.

### 2.4 Width Distribution

| Range | Count |
|---|---|
| < 10pt | 1,549 |
| 10-30pt | 1,871 |
| 30-60pt | 1,031 |
| 60-100pt | 228 |
| > 100pt | 51 |

**Conclusion:** 1,549 candidates (32.8%) are < 10pt wide — these are tiny symbols (Greek letters, single operators) that may be part of larger expressions but are cropped in isolation.

### 2.5 Crop Padding vs Content

Current crop_pdf_region() padding: (3, 2) points (horizontal, vertical).

At PDF scale (1 point ~ 1/72 inch ~ 0.35mm):
- 3pt horizontal padding ~ 1.06mm
- 2pt vertical padding ~ 0.71mm

For a typical 12pt-height math expression, the crop captures only ~12pt + 4pt = 16pt of vertical space. This is insufficient for:
- Stretched delimiters spanning 20-29pt
- Multi-line expressions spanning 80-140pt
- Greek symbols with descenders/ascenders
- Fraction bars that extend beyond the numerator/denominator bbox

## 3. Lossy Coverage Mechanisms

### 3.1 Tight Crop Padding (Primary Cause)

The crop_pdf_region() function uses padding=(3, 2) points. This means:
- Only ~1mm of context around each expression
- Consecutive lines of the same expression are cropped separately
- Stretched symbols that extend beyond the bbox are clipped
- No surrounding prose/context is captured

### 3.2 No Multi-Line Grouping in Main Pipeline

The detect_math_regions_on_page() function (connected-component grouping) exists but is NOT called in the main process_candidates() loop. Each candidate is processed individually.

### 3.3 No Context Expansion in Main Pipeline

The expand_crop_context() function (1.5x zoom-out) exists but is NOT called in the main loop. The recognize_formula_multiscale() function (2x/4x/8x + context fallback) exists but is NOT called in the main loop.

### 3.4 No Catalog Image Comparison

The 3,304 glyph images in symbols/symbols/ are loaded but never compared to crops. The glyph_catalog naive substring match (source_text in glyph['name']) almost never matches full LaTeX expressions.

### 3.5 No Wolfram Symbol Integration

The 143 Wolfram notation entries in docs/wolfram_notation_reference.md are not connected to the vision pipeline. No candidate matching against Wolfram symbol names occurs.

## 4. Specific Limitations Observed

### 4.1 Stretched Brackets (Open/Close)

- 84 tall bboxes (>20pt) from paper 2104.01277 are likely stretched delimiters
- These span 20-29pt height (2-3 lines of normal text)
- Current crop captures only the bbox + 2pt padding = ~24pt max
- The bracket's full extent may extend beyond the crop boundary
- detect_border_contamination() with vertical_border_strokes and stretched_symbols_at_border detects this but doesn't capture the full symbol

### 4.2 Large Operators (Sum, Integral, Product)

- 51 wide bboxes (>100pt) include long expressions with large operators
- Large operators like sum, int, prod span multiple lines
- Current crop captures the operator's bbox but not its full height
- No separate handling for "large operator" class in crop extraction

### 4.3 Greek Symbols

- 1,549 candidates (32.8%) are < 10pt wide — many are Greek letters
- These are cropped in isolation, losing their mathematical context
- The catalog has Greek symbols but no image comparison is performed
- Size-based classification (isolated glyph vs. large operator) is not applied during crop extraction

### 4.4 Multi-Line Expressions

- 1,000 multi-line clusters with gap < 5pt
- Max cluster size: 43 candidates
- Largest vertical span: 141.8pt (25 candidates)
- Each candidate is cropped individually, losing the relationship between consecutive lines
- No grouping of multi-line expressions into a single crop region

### 4.5 Open/Close Bracket Pairing

- No tracking of whether a left bracket has a matching right bracket
- unmatched_brackets_at_border field added to detect_border_contamination() but not populated with actual pairing logic
- Stretched symbols spanning >50% height are flagged but not captured as full symbols

## 5. What the Existing Tools Can See vs What They Miss

| Feature | Can See | Misses |
|---|---|---|
| Single-line inline math | Yes (crop captures it) | Nothing |
| Single-line display math | Yes (crop captures it) | Nothing |
| Multi-line expressions | Each line separately | Relationship between lines |
| Stretched brackets (2-3 lines) | Partial (bbox only) | Full extent beyond bbox |
| Large operators (sum, int) | Partial (bbox only) | Full height, limits |
| Greek symbols (isolated) | Yes (crop captures it) | Mathematical context |
| Fraction bars | Partial (bbox only) | Numerator/denominator relationship |
| Surrounding prose context | No | Entirely excluded by tight crop |
| Open/close bracket pairing | No | Not tracked |

## 6. Quantified Impact

| Metric | Value |
|---|---|
| Candidates in multi-line clusters | 4,382 / 4,730 (92.6%) |
| Candidates with overlapping bboxes | 2,882 / 4,730 (60.9%) |
| Tall bboxes (>20pt) | 84 (1.8%) |
| Very small bboxes (<10pt) | 2,182 (46.1%) |
| Wide bboxes (>100pt) | 51 (1.1%) |
| Pages with multi-line clusters | 118 / 127 (92.9%) |
| Max vertical span | 141.8pt (25 candidates) |

## 7. Recommended Next Steps

1. Wire detect_math_regions_on_page() into main pipeline — group connected components into full math regions before cropping.
2. Increase default crop padding — from (3, 2) to at least (8, 6) points to capture surrounding context.
3. Implement large symbol handling — detect symbols spanning >50% region height and match against catalog's large-operator class separately.
4. Implement bracket pairing — track open/close correspondence across full region height.
5. Connect catalog image comparison — load 1,595 unique glyph images and compare against detected regions.
6. Connect Wolfram symbol reference — use 143 entries as additional candidate names.
7. Evaluate expand_crop_context() — test on real multi-line formula crops to verify context capture.
8. Cross-examine bbox coordinates — verify that detected bboxes actually correspond to complete mathematical expressions, not fragments.
