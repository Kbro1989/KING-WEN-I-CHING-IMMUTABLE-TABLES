# Full-Page Text and Mathematical Extraction Cross-Reference Evaluation Plan

## Status: Documentation only — no implementation authorized
## Date: 2026-11-04

---

## 1. Purpose

This plan specifies a read-only cross-reference evaluation that compares three independent evidence layers: (1) full-page text extraction from PDFs, (2) mathematical parser extraction records, and (3) vision-pipeline region geometry. Its purpose is to identify where these systems agree, where they diverge, and what each system actually observes — not to benchmark, accept, or integrate any component.

## 2. Governing Rules

1. **Read-only.** No source code modifications, no pipeline integration, no baseline changes, no gate claims.
2. **Three populations remain separate.** The 988-page vision execution, the 127-page spatial-analysis cohort, and the math parser's existing corpora are distinct populations. Do not assume they contain identical papers or pages.
3. **Three coverage types are independent.** Text coverage ≠ mathematical extraction coverage ≠ spatial correspondence coverage. A page can have excellent text coverage and poor extraction coverage, or vice versa.
4. **Cross-reference ≠ benchmark.** This evaluation identifies agreement and divergence between systems. It does not establish accuracy, superiority, or acceptance.
5. **Preserve unmatched records.** Unmatched, ambiguous, duplicated, partial, and missing records are evidence, not noise. Do not force matches or discard exceptions.

## 3. Corpus and Page Populations

### Population 1: Vision execution corpus
- **Papers:** 16 benchmark PDFs
- **Pages:** 988
- **Source:** `DATASETS/benchmark_pdfs/` (16 PDFs)
- **Evidence:** `DATASETS/vision_comparison/representative_page_evaluation.jsonl` (988 page records)
- **Identity:** paper_id + page_number (1-indexed)

### Population 2: Spatial-analysis cohort
- **Papers:** 6 (subset of 16, or distinct — must be verified)
- **Pages:** 127
- **Source:** Lossy-coverage cross-examination dataset
- **Evidence:** `docs/lossy-coverage-cross-examination-2026-11-04.md`
- **Identity:** paper_id + page_number

### Population 3: Math parser corpus
- **Papers:** 14 (arXiv HTML papers with MathML)
- **Equations:** 3,409 (14-paper benchmark)
- **Source:** `DATASETS/arxiv_html_corpus/` (14 JSON files)
- **Evidence:** `DATASETS/baseline_2026-10-09/occurrences.jsonl` (3,409 entries)
- **Identity:** paper_id + equation identity (SHA-256 over paper/version/locator/index)

### Population overlap
- **Must be verified, not assumed.** The 16 vision PDFs, 6 spatial-analysis papers, and 14 math-parser papers may overlap partially or completely. The cross-reference plan must document exact intersection before any comparison.

## 4. Extraction Fields and Coordinate Conventions

### 4.1 Full-page text extraction

For each page in each PDF:

| Field | Type | Description |
|---|---|---|
| `page_id` | string | `{paper_id}_p{page_number}` (stable, deterministic) |
| `paper_id` | string | Paper identifier matching vision and parser records |
| `page_number` | integer | 1-indexed page within paper |
| `pdf_path` | string | Path to source PDF |
| `extraction_tool` | string | Tool used (e.g., "pymupdf_1.28.2") |
| `extraction_timestamp` | string (ISO 8601) | When extraction was performed |
| `page_dimensions` | [float, float] | Width × height in PDF points |
| `render_zoom` | integer | Zoom level used for rendering (4) |
| `rendered_dimensions` | [int, int] | Width × height in rendered pixels |
| `text_blocks` | list | List of text blocks (see 4.1.1) |
| `extraction_status` | enum | `success`, `partial`, `failed` |
| `extraction_failure_reason` | string \| null | If failed/partial, reason |
| `total_char_count` | integer | Total characters extracted |
| `total_block_count` | integer | Total text blocks |

#### 4.1.1 Text block schema

| Field | Type | Description |
|---|---|---|
| `block_id` | string | `{page_id}_b{block_index}` (stable) |
| `text` | string | Extracted text content |
| `bbox` | [float, float, float, float] | [x0, y0, x1, y1] in PDF points |
| `rendered_bbox` | [int, int, int, int] | [x0, y0, x1, y1] in rendered pixels (× zoom) |
| `font_size` | float | Font size in points |
| `font_name` | string | Font family/name |
| `is_math` | boolean | Whether block contains math symbols (heuristic) |
| `char_count` | integer | Characters in this block |

### 4.2 Coordinate conventions

- **PDF space:** Points (1/72 inch). Origin at top-left. x increases right, y increases down.
- **Rendered space:** Pixels at zoom=4. Conversion: `rendered = pdf × zoom`.
- **Vision region bbox:** Stored in rendered pixels (zoom=4). Conversion to PDF points: `pdf = rendered / zoom`.
- **All bboxes** must record which coordinate space they occupy (`coord_space: "pdf_points"` or `"rendered_pixels"`).

## 5. Parser-Record Matching Rules

### 5.1 Matching criteria (in priority order)

1. **Paper identity match.** Parser record's `paper_id` must match the cross-reference record's `paper_id`.
2. **Page number match.** Parser record's page number must match the cross-reference record's `page_number`.
3. **Source locator match.** If the parser record has a source locator (e.g., `S1.E3.m2`), it must resolve to the correct page.
4. **Equation identity match.** If the parser record has an occurrence identity (SHA-256 over paper/version/locator/index), it must match the cross-reference record's equation identity.

### 5.2 Prohibited matching methods

- **Text similarity alone.** Two equations with similar LaTeX may be different equations on different pages. Text similarity is supporting evidence only.
- **Positional proximity alone.** Two equations on the same page may be at different positions. Proximity is supporting evidence only.
- **Page number without paper identity.** Page numbers are only meaningful within a paper.

### 5.3 Match classification

| Classification | Definition |
|---|---|
| `exact_match` | Paper + page + locator + equation identity all match |
| `page_match` | Paper + page match, but locator or identity differs |
| `partial_match` | Paper matches, page differs by ≤1, or locator partially matches |
| `no_match` | No matching parser record found |
| `duplicate` | Multiple parser records match the same cross-reference record |
| `ambiguous` | Multiple cross-reference records match the same parser record |

## 6. Vision-Region Matching Rules

### 6.1 Matching criteria (in priority order)

1. **Paper identity match.** Vision region's `paper_id` must match.
2. **Page number match.** Vision region's page must match.
3. **Spatial containment.** The parser's equation location (if available) or the text block's bbox must be contained within or overlap the vision region's bbox.
4. **Region identity match.** If the vision region has a region ID, it must match the cross-reference record's region ID.

### 6.2 Prohibited matching methods

- **Region count alone.** A page with 96 vision regions and 41 math-boundary text blocks does not mean 96 regions correspond to 41 equations.
- **Area ratio alone.** A large region containing a small equation does not establish correspondence.
- **Text similarity alone.** Same prohibition as parser matching.

### 6.3 Match classification

| Classification | Definition |
|---|---|
| `region_contains_equation` | Vision region bbox fully contains the parser's equation location |
| `region_overlaps_equation` | Vision region bbox partially overlaps the parser's equation location |
| `region_contains_text_block` | Vision region bbox contains a text block with math symbols |
| `no_region_match` | No vision region corresponds to the parser record |
| `vision_only_region` | Vision region with no corresponding parser record or text block |
| `ambiguous_region` | Multiple vision regions could correspond to the same parser record |

## 7. Unmatched-Record Classifications

Every record in the cross-reference must be classified. No record is discarded or silently merged.

### 7.1 Parser records without vision correspondence

| Classification | Definition | Example |
|---|---|---|
| `parser_only` | Parser identified an equation; no vision region corresponds | Equation extracted from PDF text layer but vision pipeline did not detect a region |
| `text_layer_only` | Equation exists in PDF text layer but not in vision regions | Rasterized equation invisible to text extraction but visible to vision |
| `locator_mismatch` | Parser record's page/locator does not resolve to a vision page | Page number mismatch or paper identity mismatch |

### 7.2 Vision regions without parser correspondence

| Classification | Definition | Example |
|---|---|---|
| `vision_only` | Vision region exists; no parser record corresponds | Region detected but no equation extracted by parser |
| `region_no_text` | Vision region has no corresponding text block | Region may be a figure, table, or non-text element |
| `region_no_equation` | Vision region contains text but no identified equation | Region contains prose, not math |

### 7.3 Text blocks without parser or vision correspondence

| Classification | Definition | Example |
|---|---|---|
| `text_only` | Text block exists; no parser equation and no vision region | Prose text, not mathematical content |
| `text_math_unparsed` | Text block contains math symbols but parser did not extract an equation | Parser coverage gap |
| `text_math_unregioned` | Text block contains math symbols but vision did not detect a region | Vision coverage gap |

### 7.4 Cross-system discrepancies

| Classification | Definition | Example |
|---|---|---|
| `count_mismatch` | Number of parser equations ≠ number of vision regions on the same page | Parser found 5 equations; vision found 8 regions |
| `location_mismatch` | Parser and vision agree an equation exists but disagree on location | Parser says page 3, column 2; vision says page 3, column 1 |
| `identity_mismatch` | Parser and vision identify different equations at the same location | Parser: `\sum`, Vision: `\int` at same bbox |
| `coverage_gap` | One system has data the other lacks | Parser has equation; vision has no region (or vice versa) |

## 8. Coverage Metrics and Denominators

### 8.1 Three independent coverage types

| Coverage Type | Definition | Denominator |
|---|---|---|
| **Text coverage** | Proportion of pages where full-page text extraction succeeded | Pages in population |
| **Mathematical extraction coverage** | Proportion of pages where parser identified ≥1 equation | Pages in population |
| **Spatial correspondence coverage** | Proportion of parser equations that match a vision region | Parser equations in population |

### 8.2 Per-population metrics

For each population (vision 16/988, spatial 6/127, parser 14/3409):

| Metric | Definition | Denominator |
|---|---|---|
| `pages_in_population` | Total pages in population | — |
| `pages_with_text` | Pages where text extraction succeeded | `pages_in_population` |
| `pages_with_parser_equations` | Pages where parser identified ≥1 equation | `pages_in_population` |
| `pages_with_vision_regions` | Pages where vision detected ≥1 region | `pages_in_population` |
| `parser_equations_total` | Total parser equations across population | — |
| `vision_regions_total` | Total vision regions across population | — |
| `text_blocks_total` | Total text blocks across population | — |
| `exact_matches` | Parser equations with exact vision match | `parser_equations_total` |
| `page_matches` | Parser equations with page-level match only | `parser_equations_total` |
| `no_matches` | Parser equations with no vision match | `parser_equations_total` |
| `vision_only_regions` | Vision regions with no parser match | `vision_regions_total` |
| `text_only_blocks` | Text blocks with no parser or vision match | `text_blocks_total` |

### 8.3 Denominator discipline

- Each metric must state its denominator explicitly.
- No metric may use a denominator from a different population without qualification.
- The 988-page vision population, 127-page spatial population, and 3,409-equation parser population must not be conflated.
- Cross-population comparisons must use intersection (pages present in both populations), not union.

## 9. Immutable Source Evidence

### 9.1 Sources that must not be modified

| Source | Path | Purpose |
|---|---|---|
| Vision execution JSONL | `DATASETS/vision_comparison/representative_page_evaluation.jsonl` | 988 page records, region/boundary/partial data |
| Lossy-coverage analysis | `docs/lossy-coverage-cross-examination-2026-11-04.md` | 4,730 candidates, 6 papers, 127 pages |
| ArXiv HTML corpus | `DATASETS/arxiv_html_corpus/` | 14 papers, 3,409 equations |
| Baseline occurrences | `DATASETS/baseline_2026-10-09/occurrences.jsonl` | 3,409 occurrence identities |
| Frozen regression mapping | `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | 21 candidates, 6 populations |
| Border evaluation results | `DATASETS/vision_comparison/border_evaluation_results.jsonl` | 12-crop pilot results |
| Frozen baseline | `DATASETS/vision_comparison/baseline_frozen_padding15.jsonl` | Frozen baseline records |

### 9.2 Derived outputs

All cross-reference outputs must be stored in a **separate directory** from source evidence:

| Output | Path | Format |
|---|---|---|
| Full-page text extraction | `DATASETS/cross_reference/full_page_text/` | JSONL (one record per page) |
| Cross-reference record | `DATASETS/cross_reference/cross_reference_records.jsonl` | JSONL (one record per page) |
| Discrepancy report | `docs/cross-reference-discrepancy-report-2026-11-04.md` | Markdown |
| Coverage summary | `DATASETS/cross_reference/coverage_summary.json` | JSON |

Derived outputs must:
- Link to source records via stable identifiers (execution_id, paper_id, page_number)
- Not modify source files
- Record their own extraction tool, timestamp, and version
- Be reproducible from source evidence alone

## 10. Governance Constraints

This plan is **documentation only**. The following are explicitly prohibited until authorized:

1. Implementing the cross-reference evaluation (no code changes, no extraction runs)
2. Modifying any source evidence file
3. Claiming G2–G6 gate satisfaction based on cross-reference results
4. Wiring `process_candidates()` into the pipeline
5. Merging the 988-page, 127-page, or 3,409-equation populations into a single denominator
6. Treating text coverage as mathematical extraction coverage or spatial correspondence coverage
7. Treating unmatched records as failures rather than evidence

## 11. Recommended Next Step

The next artifact is a **cross-reference implementation plan** (read-only) that specifies:

1. The extraction tool and its coordinate conventions
2. The matching algorithm (rule-based, not ML-based)
3. The unmatched-record classification procedure
4. The coverage metric computation
5. The governance gate for authorizing execution

No extraction, no matching, and no gate claims are authorized by this plan.