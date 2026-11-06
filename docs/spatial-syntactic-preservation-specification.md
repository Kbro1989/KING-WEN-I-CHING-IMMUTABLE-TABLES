# Spatial-Syntactic Preservation and Reconstruction — Specification

## Purpose

This specification defines a representation that preserves both original observations and
reconstructed hypotheses about the spatial-syntactic structure of mathematical expressions
on PDF pages. It addresses the third preservation problem identified in the vision
comparison pipeline review:

<|message|> Workstream | Preservation target | Current position |
|---|---|---|
| Image representation | Preserve original pixels and derived-image provenance | Documented |
| Crop/context preservation | Preserve complete expressions, stretched symbols, neighboring content | Functions tested; pipeline integration not established |
| **Spatial-syntactic preservation** | Reconstruct grouping, delimiter extent, superscript attachment, separators, page-local notation | **Newly identified; specified here** |

**Core principle:** Preserving an image is not necessarily preserving the information encoded
by its spatial arrangement. A stretched brace present in the original PDF but divided across
several crops loses its relationship to the equations it spans. The pipeline boundary
protects the original pixels but does not reconstruct the brace's structural role.

This specification does NOT propose a new OCR model. Its first deliverable is a
representation capable of preserving observations and hypotheses with measurable fidelity.

---

## 1. Observation Layer (Original Evidence)

Every spatial observation must retain its source coordinates, supporting evidence,
confidence, and resolution status. No observation is silently discarded.

### 1.1 Glyph Identity and Font/Shape Alternatives

Each detected glyph retains:

| Field | Type | Description |
|---|---|---|
| `glyph_id` | string | Unique identifier within page scope |
| `unicode_char` | string | Best-effort Unicode mapping (may be ambiguous) |
| `font_name` | string | PDF font resource name |
| `font_size` | float | Point size at render zoom |
| `shape_alternatives` | list[string] | Candidate Unicode chars if font mapping is ambiguous (e.g., `["{" , "⦃", "{" ]`) |
| `rendered_bbox` | [x, y, w, h] | Rendered pixel coordinates at zoom=4 |
| `pdf_bbox` | [x0, y0, x1, y1] | PDF point coordinates (rendered / 4) |
| `confidence` | float [0,1] | Glyph recognition confidence |
| `source` | enum | `text_layer` (PyMuPDF), `ocr` (Pix2Text), `vision` (region detector), `manual` |

### 1.2 Baseline, Bounding Box, and Relative Spatial Position

Each glyph carries its vertical position relative to the line baseline:

| Field | Type | Description |
|---|---|---|
| `baseline_y` | float | Y-coordinate of the glyph's baseline in PDF points |
| `x_offset_from_line_start` | float | Horizontal offset from the start of the containing line |
| `vertical_offset_from_baseline` | float | Signed vertical offset (negative = above baseline, positive = below) |
| `line_id` | string | Identifier of the text line this glyph belongs to |
| `reading_order` | int | Position in reading order within the page |

### 1.3 Multi-Line Region Membership

Each detected region (math or text) retains its line membership:

| Field | Type | Description |
|---|---|---|
| `region_id` | string | Unique identifier within page scope |
| `line_ids` | list[string] | All text lines whose content falls within this region |
| `is_multi_line` | bool | True if the region spans more than one text line |
| `line_span` | [int, int] | [first_line_index, last_line_index] in reading order |
| `region_bbox` | [x, y, w, h] | Rendered pixel bounding box |
| `region_type` | enum | `equation`, `inline_math`, `text`, `figure`, `table`, `unknown` |

---

## 2. Structural Expectation Ledger

A structural expectation is a hypothesis about a mathematical relationship derived from
spatial observations. Each expectation is recorded with its source coordinates, supporting
evidence, confidence, and resolution status. Unresolved expectations remain visible —
they are never silently discarded.

### 2.1 Expectation Schema

```json
{
  "expectation_id": "string (unique within page scope)",
  "expectation_type": "enum (see 2.2)",
  "source_observation_ids": ["glyph_id or region_id references"],
  "source_coordinates": {
    "rendered": [x, y, w, h],
    "pdf": [x0, y0, x1, y1]
  },
  "supporting_evidence": ["description of what supports this hypothesis"],
  "confidence": 0.0,
  "resolution_status": "unresolved | resolved | contradicted | ambiguous",
  "resolved_by": "string or null (observation/hypothesis that resolved this)",
  "notes": "string"
}
```

### 2.2 Expectation Types

| Type | Trigger | Expected relationship |
|---|---|---|
| `delimiter_pair` | Opening delimiter glyph (`{`, `[`, `(`, `\|`, `\left.`) | Expected closing delimiter at matching height/position |
| `fraction_bar` | Horizontal line segment at mid-height between baselines | Candidate numerator above, denominator below |
| `superscript_attachment` | Glyph rendered above baseline with smaller font size | Expected attachment to base expression to the left/below |
| `subscript_attachment` | Glyph rendered below baseline with smaller font size | Expected attachment to base expression to the left/above |
| `multi_line_group` | Consecutive lines with shared left alignment and matching indentation | Possible equation-group relationship |
| `horizontal_separator` | Horizontal line spanning significant width | Candidate above/below relationship (cases, piecewise) |
| `notation_definition` | Symbol introduced with `:=`, `=`, or `\coloneqq` | Scoped interpretation rule for subsequent occurrences |
| `accent_pair` | Accent glyph (`^`, `¯`, `˙`, `~`) positioned above a base glyph | Expected binding to the base glyph below |
| `operator_scope` | Binary operator (`+`, `-`, `×`, `=`, `\sum`, `\int`) | Candidate left/right operand boundaries |

### 2.3 Resolution Statuses

| Status | Meaning |
|---|---|
| `unresolved` | Expectation created but not yet matched to a closing/attachment |
| `resolved` | Expectation matched to a corresponding observation with sufficient confidence |
| `contradicted` | A later observation contradicts the expectation (e.g., delimiter closes at wrong height) |
| `ambiguous` | Multiple candidate resolutions exist; none dominates |

**Rule:** Unresolved expectations must remain visible in all outputs. They are never silently
discarded or collapsed into "not applicable." A page with 5 unresolved delimiter pairs is
more informative than a page reporting 0 pairs.

---

## 3. Reconstructed Hypothesis Layer

The hypothesis layer contains reconstructed mathematical structures derived from observations
and expectations. Each hypothesis is linked to its source expectations and observations.

### 3.1 Hypothesis Schema

```json
{
  "hypothesis_id": "string (unique within page scope)",
  "hypothesis_type": "enum (see 3.2)",
  "source_expectation_ids": ["expectation_id references"],
  "source_observation_ids": ["glyph_id or region_id references"],
  "structure": {},
  "confidence": 0.0,
  "validation_status": "unvalidated | validated | invalidated",
  "validation_evidence": "string or null"
}
```

### 3.2 Hypothesis Types

| Type | Description | Required structure fields |
|---|---|---|
| `delimiter_group` | Matched opening/closing delimiter pair with enclosed content | `open_id`, `close_id`, `enclosed_glyph_ids`, `nesting_depth` |
| `fraction` | Numerator/denominator separated by a horizontal bar | `bar_id`, `numerator_glyph_ids`, `denominator_glyph_ids` |
| `superscript` | Superscript attached to base expression | `base_glyph_ids`, `superscript_glyph_ids`, `attachment_confidence` |
| `subscript` | Subscript attached to base expression | `base_glyph_ids`, `subscript_glyph_ids`, `attachment_confidence` |
| `equation_group` | Multi-line equation group with shared alignment | `line_ids`, `alignment_column`, `group_type` (cases, align, gather, etc.) |
| `notation_scope` | Page-local notation definition with scope | `symbol_id`, `definition_expression`, `scope_start_line`, `scope_end_line` |
| `accent_binding` | Accent bound to base glyph | `accent_id`, `base_glyph_id` |

### 3.3 Original Observations vs Reconstructed Hypotheses

The representation MUST preserve both:

- **Original observations**: What was detected on the page (glyphs, bboxes, text layer output)
- **Reconstructed hypotheses**: What the system believes the structure to be (delimiter pairs, fractions, etc.)

These are stored in separate layers. A hypothesis that is later invalidated does not delete
the original observation. The original observation remains available for re-analysis.

---

## 4. Page-Level Structural Summary

Each page produces a structural summary that aggregates observations, expectations, and
hypotheses:

```json
{
  "page_id": "string",
  "paper_id": "string",
  "page_number": int,
  "observation_count": int,
  "expectation_count": int,
  "hypothesis_count": int,
  "unresolved_expectation_count": int,
  "ambiguous_hypothesis_count": int,
  "structural_completeness": float,
  "notes": "string"
}
```

### 4.1 Structural Completeness

`structural_completeness` is defined as:

```text
structural_completeness = (resolved_expectations + validated_hypotheses) / (total_expectations + total_hypotheses)
```

If there are zero expectations and zero hypotheses, `structural_completeness` is undefined
(reported as `null`), not 1.0. An empty page has no structural completeness to measure.

---

## 5. Relationship to Existing Pipeline

### 5.1 Current State

The existing pipeline has:

- `detect_math_regions_on_page()` — region detection with bounding boxes
- `detect_page_primary_white()` — adaptive threshold based on background
- `cross_reference_pipeline.py` — region-equation correspondence
- `vision_comparison_pipeline.py` — crop isolation, balloon renders, candidate audit

These produce **observations** (regions, bboxes, text overlaps) but do not produce
**structural expectations** or **reconstructed hypotheses**. The spatial-syntactic layer
is a new addition, not a replacement.

### 5.2 Integration Points

| Existing component | Integration |
|---|---|
| Region detection (`detect_math_regions_on_page`) | Each region becomes a `region_id` observation with `region_type` and `line_ids` |
| Text layer (PyMuPDF `get_text("dict")`) | Each span becomes a `glyph_id` observation with font, size, bbox, baseline |
| Cross-reference records | Each correspondence record links a region to an equation; spatial-syntactic expectations can reference these records as supporting evidence |
| Candidate audit renders | Visual verification of unresolved expectations and ambiguous hypotheses |

### 5.3 What This Specification Does NOT Do

- Does NOT propose a new OCR model or recognition architecture
- Does NOT modify existing region detection or text extraction
- Does NOT change the pipeline boundary between math extraction and depth analysis
- Does NOT claim that structural reconstruction improves OCR accuracy
- Does NOT replace original observations with hypotheses

---

## 6. Acceptance Criteria

The spatial-syntactic preservation system is considered functional when:

1. Every detected glyph on a page has an observation record with bbox, font, and confidence.
2. Every spatial expectation (delimiter, fraction, superscript, etc.) is recorded with
   source coordinates and confidence.
3. Every unresolved expectation remains visible in the output (never silently discarded).
4. Every reconstructed hypothesis is linked to its source expectations and observations.
5. Original observations are preserved separately from reconstructed hypotheses.
6. `structural_completeness` is computed correctly (null for empty pages, not 1.0).
7. The representation can be serialized to JSON and deserialized without loss.

---

## 7. First Deliverable

The first deliverable should NOT be a new OCR model. It should be:

**A representation (JSON schema + Python dataclasses) that preserves:**

1. Glyph identity and font/shape alternatives
2. Baseline, bounding box, and relative spatial position
3. Multi-line region membership
4. Delimiter identity, extent, and pairing expectations
5. Fraction bars, horizontal separators, and above/below relationships
6. Superscript and subscript attachment candidates
7. Page-local notation definitions and scope
8. Ambiguous, clipped, missing, or unresolved structural relationships

**And most importantly:** preserve both the original observations and the reconstructed
hypotheses, so that the system can measure whether it recovered something that was
actually on the page, rather than producing something mathematically plausible.

---

## 8. Non-Goals

- This specification does not address OCR accuracy or recognition model selection.
- This specification does not address depth-map generation or 3D reconstruction.
- This specification does not address cross-page or cross-document structural relationships.
- This specification does not address training data generation or model fine-tuning.
- This specification does not claim that structural preservation improves any downstream
  metric. It defines a representation; evaluation of that representation is a separate gate.

---

## 9. Two-Population Design Invariant

The validation of structural preservation requires an explicit separation between two controlled populations:

1. **Negative Controls (Rejection Invariant):**
   - Established on non-mathematical visual structures (e.g., plots, tick marks, figure panels as in `2009.00031` page 5).
   - Confirms that non-mathematical visual material must NOT become mathematical expectations or pass eligibility gating (`expectation_generation_eligible = false`).
   - Prevents hallucination of syntax from non-syntactic ink.

2. **Positive Controls (Preservation Invariant):**
   - Established on independently verified, typeset mathematical equations (e.g., GS-001 through GS-005 in `1505.05770`).
   - Confirms whether genuine mathematical structures can be faithfully observed, spatially clustered, and structurally reconstructed.

**Strict Decoupling Contract:**
- Neither population may manufacture or influence the other's ground truth.
- Metrics from the negative control (rejection rate) and positive control (detection recall, spatial coverage, structural fidelity) must remain strictly decoupled and never blended into a single composite score.
- Observation layers, clustering logic, and expectation ledgers must be evaluated against frozen ground truth manifests without back-channel parameter tuning against the evaluation population.

---

## 10. Equation-Number Metadata Contract and Dual-Bounding-Box Specification

### 10.1 Architectural Principle: Metadata vs. Expression Interior
Equation numbers (e.g., `(1)`, `(2)`, `(6)`) are structural metadata attachments, not geometric contents of the mathematical expression itself. They serve to index and reference equations within the document discourse, rather than forming mathematical arguments or operators within the syntax tree.

### 10.2 The Whitespace Gap Confound
In standard scientific typesetting (such as LaTeX `equation` environments or ICML two-column formats), mathematical expressions are either centered or left-aligned within their column, while equation numbers are set flush against the right margin.
- In two-column layouts, the blank whitespace gap between the mathematical formula and the equation number typically ranges from 70 pt to 130 pt (e.g., 129.28 pt in ViLT Page 4, Equation 6).
- A monolithic bounding box encompassing both expression and equation number forces substantial empty white space into the ground truth target.
- For tightly bounded expression detectors, this whitespace inclusion mathematically caps the maximum possible Intersection-over-Union (IoU):
  $$\text{IoU}_{\text{max}} = \frac{\text{Area}(\text{Expression})}{\text{Area}(\text{Full Row})} \approx 0.35 \text{ to } 0.55$$
Evaluating tight expression proposals against monolithic full-row targets artificially penalizes spatial fidelity for correctly refusing to hallucinate ink across a 120 pt blank gap.

### 10.3 Dual-Bounding-Box Specification
To eliminate this confound, positive-control manifests must support a dual-bounding-box ground truth schema:

1. `math_expression_bbox` `[x0, y0, x1, y1]`:
   - Tightly bounds the mathematical tokens, operators, delimiters, and subscripts/superscripts of the formula itself.
   - Excludes trailing right-margin whitespace and the equation number.
   - Serves as the primary ground truth for evaluating detector Spatial Fidelity (IoU and coverage).

2. `equation_number_bbox` `[x0, y0, x1, y1]`:
   - Tightly bounds the equation label or number token(s) at the margin (e.g., `(1)`).
   - Serves as the target for metadata association.

3. `full_row_bbox` `[x0, y0, x1, y1]` (optional legacy compatibility):
   - The bounding rectangle enclosing both the expression and the equation number across the whitespace gap.

### 10.4 Metadata Association Contract
Equation numbers are linked to expressions via spatial-syntactic association:
- An equation number belongs to an expression if they share a common baseline ($\Delta y_{\text{baseline}} \le \text{baseline tolerance}$) and occupy the same visual column.
- The system must represent equation numbers as an associated metadata property of the equation region (`associated_equation_number`), not as an interior syntax element.

### 10.5 Substring Check Disqualification
Structural verification rules must not use bare numeral substring tests (such as `"1" in extracted_text`) to evaluate equation numbers. In ViLT Equation 1, the presence of numeral `"1"` in the subscript index $t_1 T$ caused a spurious pass for equation number `(1)`, whereas Equation 2 (lacking index 2) failed. Equation number verification must explicitly target isolated equation-label proposals or delimited label tokens `\(\d+\)`.

---

## 11. Layer C Candidate Implementation and Verified Results (v3.0)

### 11.1 Architectural Mechanisms
Implemented in `scripts/hierarchical_region_proposals_v3.py`, consuming frozen Layer A observations:
1. **Adaptive Baseline Tolerance (AC-1):** $\text{tol} = \max(3.0, 0.45 \times \text{size}_{\text{max}})$ to recover scripts at $|\Delta y| = 3.1\text{--}3.3\text{ pt}$ without flat window inflation.
2. **Multiline Continuity Guardrails (AC-3):** Requires shared relation alignment ($\le 5\text{ pt}$), indented continuation ($> 20\text{ pt}$), or continuation punctuation before merging. Lines with independent relation symbols at similar indentation remain separate.
3. **Decoupled Equation Numbers (AC-4):** Emits `equation_number_metadata` and `math_expression_bbox` excluding label whitespace.
4. **End-to-End Traceability:** Every proposal carries `structural_provenance` linking spans, glyph indices, applied tolerances, and source coordinates.

### 11.2 Multi-Population Scoreboard (v2.0 Baseline vs v3.0 Candidate)
- **Total Equations Evaluated:** 15 across 3 publications (`1505.05770`, `2102.03334`, `1406.2661`).
- **Fully Preserved (v2.0):** 7 / 15 (46.7%).
- **Fully Preserved (v3.0):** 10 / 15 (66.7%) — VILT-001, VILT-002, and VILT-003 restored to PRESERVED.
- **Per-Equation Verdicts:** 6 IMPROVED, 9 UNCHANGED, 0 REGRESSED.
- **Negative Control Invariant:** 15 / 15 rejected on `2009.00031` Page 5 (100.0% rejection rate, 0 escapes).
- **Acceptance Criteria Gate:** All 7 criteria (AC-1 through AC-7) verified SATISFIED.
- **Regression Suite:** 557 / 557 passed.



