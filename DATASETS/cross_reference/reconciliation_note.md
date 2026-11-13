# Population Reconciliation Note

## 988 vs 344 Page Discrepancy

The representative-page evaluation (run_representative_page_evaluation.py) produced
988 records across 16 PDFs. However, only 344 of these are unique (paper_id, page_number)
pairs. The remaining 644 records are repeated processing passes of the same pages
(approximately 2.87 passes per unique page on average).

This cross-reference pipeline processes each unique page exactly once, yielding 344
pages. This is the correct denominator for coverage measurement.

## Classification Reconciliation

The 141,212 cross-reference records are classified into FOUR mutually exclusive
categories:

| Classification | Records | Percentage |
|---|---|---|
| region_contains_equation | 33,368 | 23.6% |
| region_contains_text_block | 3,545 | 2.5% |
| region_no_equation | 98,161 | 69.5% |
| region_no_text | 6,138 | 4.3% |
| **Total** | **141,212** | **100.0%** |

All four categories sum to exactly 141,212. There is no unaccounted remainder.

## Text-Only Regions (98,161)

A region containing text but no equation correspondence does NOT necessarily
indicate a parser failure. Possible explanations include:
- Ordinary prose intersecting the region
- Mathematical notation not represented in the parser corpus
- Inline mathematical content not captured as standalone equations
- Parser equation locators that do not match PDF coordinate geometry
- A genuine parser omission
- An incorrect or overly broad region boundary

These are discrepancy classes, not accuracy judgments.

## No-Text Regions (6,138)

Regions with no text intersection may contain:
- Rasterized mathematics (image-based equations)
- Vector glyphs not in the text layer
- Image content (diagrams, figures)
- Geometry mismatches between region and text coordinates

## Occurrence Identity Stability

The SHA-256 identity uses: paper_id + version + locator + index

This is deterministic for a fixed input ordering. However, the index means that
inserting or reordering records can change identities even when the underlying
equation remains unchanged. This identity should be preserved as the current
execution identity, but distinguished from a future order-independent occurrence
identity. Do NOT change existing IDs retroactively.