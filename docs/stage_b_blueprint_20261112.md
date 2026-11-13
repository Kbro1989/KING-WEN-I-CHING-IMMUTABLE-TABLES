# Stage B — Node-to-Glyph Association: Research & Implementation Blueprint

## 1. Purpose and scope

Stage B is the second phase of the math PDF recovery pipeline. It consumes Stage A
output and produces a versioned association sidecar that links **semantic AST nodes**
to **physical PDF glyph observations**, preserving structural roles, ambiguity, and
geometric evidence — without modifying any frozen engine, benchmark population, or the
16-test association-contract baseline.

Stage B boundary (confirmed):

| Item | Status |
|---|---|
| Stage A output consumer | `cache/stage_a_output.json` |
| Stage B implementation | Not implemented |
| Gold annotation protocol | Independent, produced before matcher runs |
| Frozen engines | Untouched |
| Benchmark populations | Untouched |
| Baseline tests | Untouched (existing 16-test baseline separate) |

In-scope inputs: Stage A output JSON, MathML source occurrence, AST (`ExprNode`
tree), spatial-syntactic observer glyph records, targeted math detector region
candidates, font-aware classifier output, delimiter identity tables.

Out-of-scope: large-corpus batch processing, generalization claims, OCR substitution
for PDF glyph extraction, Stage C (relationship geometry adjudication).

---

## 2. Architectural distinction: evidence-constrained correspondence

Stage B is **not** an OCR assignment problem. It does not re-recognize the whole
expression. It solves a constrained inverse problem:

> Given the existing semantic AST (from MathML extraction) and the physical PDF
> glyph observations (from the spatial-syntactic observer), determine which physical
> observations support each existing semantic node.

This is bounded by three constraints:

1. The AST is **given** — the semantic structure exists. Stage B never reconstructs
   expression-level grouping from scratch.
2. Physical observations are **given** — the detector candidates from Stage A and the
   glyph observations from the spatial-syntactic observer are fixed inputs.
3. Ambiguity is **preserved** — no forced match. Multiple viable assignments remain
   available for adjudication.

Reference architecture (three-pass separation of concerns):

| Pass | Concern | Existing component |
|---|---|---|
| Layout | Spatial relationships, baseline structure | `spatial_syntactic_observer.py`, `targeted_math_detector.py` |
| Lexical | Group physical symbols into semantic tokens | `hierarchical_region_proposals.py` (v3) |
| Expression | Construct/solve operator tree | `structural_ast_extractor.py` → `ExprNode` |

---

## 3. Stage B input contract (field-by-field)

The Stage B input is the Stage A output artifact. Its schema is version-pinned.

```
cache/stage_a_output.json
```

Top-level fields:

| Field | Type | Description |
|---|---|---|
| `source_occurrence_id` | str | Identification string for the source occurrence, e.g. `S6.E20.m1` |
| `source_paper_id` | str | arXiv identifier, e.g. `1505.05770` |
| `source_index` | int | Zero-padded occurrence index in the source file |
| `source_latex` | str | LaTeX annotation of the occurrence |
| `source_mathml` | str | MathML annotation of the occurrence |
| `source_sha256` | str | SHA-256 of the source occurrence (hex, 64 chars) |
| `pdf_sha256` | str | SHA-256 of the source PDF (hex, 64 chars) |
| `pdf_path` | str | Absolute path to the source PDF file |
| `stage_a_output` | list[dict] | Stage A candidate region links |
| `provenance` | dict | Derivation chain |

Each entry in `stage_a_output`:

| Field | Type | Description |
|---|---|---|
| `source_occurrence_id` | str | Which occurrence this link maps |
| `page_number_1_based` | int | 1-based PDF page number |
| `candidate_bbox_pdf_pt` | list[float] | Candidate region bbox in PDF points `[x0, y0, x1, y1]` |
| `iou` | float | IoU with gold (0.0 = no gold, Stage A did not have gold) |
| `containment` | float | Containment ratio (0.0 = no gold) |
| `n_geom_candidates` | int | Number of geometry candidates produced by detector |
| `status` | str | `ambiguous` (only legal value in Stage A output) |

Versioning fields (placed in sidecar metadata, NOT in every record):

| Field | Value |
|---|---|
| `ast_schema_version` | `ast-v1` |
| `extractor_version` | `mathml-20261112` |
| `schema_version` | `1.0.0` (association sidecar) |

---

## 4. Sidecar output contract (field-by-field)

Stage B produces the versioned association sidecar. The schema is defined by
`math_pdf_association.py` (`SIDECAR_SCHEMA_VERSION = "1.0.0"`). Stage B appends
records to the five record collections.

### 4.1 Sidecar top-level metadata

| Field | Type | Description |
|---|---|---|
| `schema_version` | str | `"1.0.0"` |
| `generated_at` | str | ISO-8601 generation timestamp |
| `ast_schema_version` | str | `"ast-v1"` |
| `extractor_version` | str | `"mathml-20261112"` |
| `source_occurrence_table` | dict | `paper_id`, `paper_version`, `extraction_revision`, `source_occurrence_hash` |

### 4.2 Record collections

Each record carries the common provenance block:

| Common field | Type | Description |
|---|---|---|
| `pdf_sha256` | str | SHA-256 of source PDF |
| `source_occurrence_id` | str | Identification string |
| `source_occurrence_hash` | str | Source occurrence SHA-256 |
| `extractor_version` | str | `"mathml-20261112"` |
| `ast_schema_version` | str | `"ast-v1"` |

#### 4.2.1 `source_alignments`

Links the source occurrence to the sidecar. One entry per occurrence.

| Field | Type | Description |
|---|---|---|
| `source_occurrence_id` | str | Occurrence ID |
| `source_occurrence_hash` | str | SHA-256 of the source occurrence |
| `paper_id` | str | arXiv ID |
| `ast_schema_version` | str | `"ast-v1"` |

#### 4.2.2 `ast_nodes`

One entry per AST node (from `ExprNode`). Exports the semantic node with its role.

| Field | Type | Description |
|---|---|---|
| `node_id` | str | Deterministic identifier: `{source_occurrence_id}:{tree_path}` |
| `kind` | str | AST node kind from `NODE_KINDS` (e.g. `operand`, `relation`, `operator`, `sqrt`, `munderover`, `limit`) |
| `value` | str \| null | Original token from source |
| `tree_path` | str | Source AST path, e.g. `root/1/0` |
| `semantic_role` | str | Role: `base`, `exponent`, `numerator`, `denominator`, `lower`, `upper`, `radicand`, `operand`, `function`, `big_operator` |
| `role_confidence` | float | 0.0–1.0, derived from geometric evidence |
| `status` | str | `established`, `ambiguous`, `unresolved`, `unverified_regression`, `not_applicable` |
| `missing_observation` | bool | true if the node has no matching glyph observation |
| `glyph_observation_ids` | list[str] | Reference glyph observation IDs supporting this node |
| `observed_geometry` | list[dict] | Raw per-glyph PDF observation coordinates |
| `inferred_geometry` | dict | Computed extent of the node: `bbox_pdf_pt`, `bbox_points` |
| `residuals` | list[dict] | Per-dimension geometric residuals |

#### 4.2.3 `glyph_observations`

One entry per physical PDF glyph observation. Imports from the spatial-syntactic
observer output. Each one carries its own `observed_geometry`.

| Field | Type | Description |
|---|---|---|
| `glyph_id` | str | Stable glyph identifier |
| `unicode_char` | str | Unicode character |
| `font_name` | str | PDF font name |
| `font_size_pts` | float | Font size in points |
| `observed_geometry` | dict | Raw PDF bbox: `bbox_pdf_pt` `[x0,y0,x1,y1]`, `origin` |
| `status` | str | `assigned` / `assigned_ambiguous` / `held` |
| `association_ids` | list[str] | Node IDs this observation supports |

#### 4.2.4 `node_associations`

One entry per (node, glyph) pair. The association record is the core Stage B unit.
It carries both the semantic role and the geometric evidence.

| Field | Type | Description |
|---|---|---|
| `node_id` | str | AST node identifier |
| `glyph_id` | str | Glyph observation identifier |
| `semantic_role` | str | Role assigned by the matcher |
| `role_confidence` | float | 0.0–1.0 |
| `association_status` | str | `established` / `ambiguous` / `unresolved` |
| `relationship_type` | str | `primary` / `composite` / `shared` / `covering` |
| `observed_geometry` | dict | Glyph bbox with residuals |
| `inferred_geometry` | dict | Node-level extent contribution |
| `residuals` | dict | Geometric residuals (see §5) |
| `reading_order` | int | Source-order position within the node |
| `confidence` | float | Combined confidence (evidence + structural fit) |

#### 4.2.5 `relationship_geometry`

One entry per derived geometric relationship (fraction bar, radical vinculum, script
anchor line, delimiter pair, etc.). Captures the **structural** geometry that the
semantic AST encodes.

| Field | Type | Description |
|---|---|---|
| `relationship_type` | str | `fraction_bar`, `radical_vinculum`, `script_anchor`, `delimiter_pair`, `big_operator_extent`, `baseline` |
| `supported_by` | list[str] | Node IDs that support this relationship |
| `bbox_pdf_pt` | list[float] | `[x0, y0, x1, y1]` of the relationship extent |
| `geometry_kind` | str | `line`, `arc`, `rectangle`, `composite` |
| `established_by` | str | `geometric` / `geometric_inferred` / `residual_based` |
| `status` | str | `established` / `ambiguous` / `unresolved` |
| `residuals` | list[dict] | Geometric residuals |

---

## 5. Association algorithms (five-part procedure)

### Part 1 — Input normalization

1. Load Stage A output (`cache/stage_a_output.json`).
2. Load the source occurrence: MathML and LaTeX, with `source_sha256` and `pdf_sha256` verified.
3. Extract the semantic AST: walk the MathML `<math>` element with
   `StructuralASTExtractor`, producing an `ExprNode` tree.
4. Extract PDF glyph observations: run the spatial-syntactic observer, which yields
   `GlyphObservation` records with `pdbf_bbox`, `font_name`, `font_size_pts`, and
   `reading_order`.
5. Load region candidates: geometry candidates from `targeted_math_detector.py`
   (the `n_geom_candidates` count in Stage A output).
6. Load font metadata and delimiter identity tables: `font_aware_math_classifier.py`,
   `delimiter_identity.py`.

### Part 2 — Spatial constraints (filtering using evidence only)

For each AST node, define candidate glyph observations using only spatial predicates:

| Predicate | Description |
|---|---|
| `bbox_intersection(n, g)` | Node bbox intersects glyph bbox by area ≥ 0 |
| `bbox_contains(n, g)` | Node bbox contains glyph bbox |
| `script_match(g, n)` | Glyph is a subscript/superscript candidate relative to the node |
| `baseline_match(g, n)` | Glyph baseline within ±0.5pt of node baseline |
| `font_match(g, n)` | Glyph font compatible with node representation |

Filtering rule: **use only spatial predicates during the candidate-generation stage.**
MathML AST semantics enter only in Part 4.

Results: for each node `n`, a set of candidate glyphs `C(n) ⊆ G` (glyphs G).
A glyph `g` may appear in multiple candidate sets (many-to-many is legal).

### Part 3 — Geometric residuals (pattern 5)

For each candidate pair `(n, g)`, compute evidence residuals:

| Residual | Formula / source |
|---|---|
| `horizontal_displacement` | `g.bbox.x0 - n.bbox.x0` |
| `vertical_displacement` | `g.bbox.y0 - n.bbox.y0` |
| `baseline_difference` | `g.font_baseline - n.font_baseline` |
| `relative_height` | `g.bbox.height / n.bbox.height` |
| `bbox_overlap` | IoU of `g` and `n` bboxes |
| `script_offset` | Vertical distance from node baseline |
| `font_size_compat` | `1 - |g.font_size_pts - n.font_size_pts| / max_font_size` |
| `reading_order_consistency` | Ordinal index mismatch |

Each residual is retained as a numbered evidence item. No scalar score is computed
at this stage. Residuals are stored, not collapsed.

### Part 4 — Role-based structural matching (evidence + structural fit)

For each node, use the AST semantic role to define geometric expectations:

| Semantic role | Geometric expectation |
|---|---|
| `base` (e.g. `x` in `x^2`) | Glyph at node baseline; size ≤ node bbox |
| `exponent` (e.g. `2` in `x^2`) | Glyph placed above exponent line (0.8–1.2× node fontsize offset) |
| `numerator` (e.g. `a` in `a/b`) | Glyph in upper fraction region |
| `denominator` (e.g. `b` in `a/b`) | Glyph in lower fraction region |
| `lower` (e.g. `k` in `sum_k`) | Glyph below the baseline |
| `upper` (e.g. `K` in `sum_k`) | Glyph above the baseline |
| `radicand` (e.g. `x+y` in `sqrt{x+y}`) | Glyph under the radical sign |
| `function` (e.g. `ln`, `prod`) | Multi-glyph; glyph cluster; left-aligned |

Role assignment rule:
- Use the **structural role** from the AST. The AST provides the role; geometry
  validates the fit.
- A glyph that satisfies the role expectations is assigned to the node.
- If multiple glyphs satisfy the role, retain all assignments — do NOT pick one.
- If no glyph satisfies, mark the node as `unresolved` — do not force a match.

### Part 5 — Composite and shared representations

Some semantic nodes have multiple physical representations. These require
explicitly-typed associations:

| AST pattern | Physical representation | Relationship type |
|---|---|---|
| `ln` | two character observations `l` + `n` | `composite` |
| `∑` | one character or multiple drawing primitives | `covering` |
| tall brace | multiple glyph pieces | `composite` |
| `q_\phi` | multiple observations grouped | `composite` |
| delimiter pair | two glyphs | `delimiter_pair` |

If a glyph is assigned to two unrelated nodes, add a `relationship_type` field
(otherwise the same observation is not silently assigned).

### Part 6 — Resolution status

Every association records one of:

| Status | Meaning |
|---|---|
| `established` | Geometric evidence supports the assignment |
| `ambiguous` | Multiple viable assignments remain; no single winner |
| `unresolved` | No viable assignment; node has no glyph |
| `unverified_regression` | A downgrade from `established` on schema re-run |
| `not_applicable` | This relation does not apply to this instance |

Constraint: **preserve `ambiguous` and `unresolved`**. Do not collapse to a single
best match. Do not allow candidate generation to leak gold.

---

## 6. Independent gold annotation protocol

Gold is produced **before** the matcher runs. The gold annotation is independent of
Stage B predictions — the annotator never sees matcher output.

### 6.1 Initial gold set (paper 1505.05770v6)

| Case | Structure | Tests |
|---|---|---|
| B01 | `x^2` | base/exponent separation |
| B02 | `a/b` | numerator/denominator separation |
| B03 | `sum_{k=1}^{K}` | under/over scripts |
| B04 | `sqrt{x+y}` | radical and extent |
| B05 | `left{ begin{matrix}a\ b end{matrix} right.` | extensible delimiter |
| B06 | `q_phi(z|x)` | subscripts and conditional bar |
| B07 | `ln p(x,z)` | multi-character function grouping |
| B08 | `prod_{k=1}^{K} f_k` | big operator and script relationships |

### 6.2 Gold annotation fields (per case)

For every case, the independent annotator records:

1. Physical glyph observations — character, font, size, bbox
2. Glyph bounding boxes — PDF points
3. AST node identities — from `ExprNode` tree walk
4. Semantic roles — base, exponent, numerator, denominator, lower, upper, radicand, function
5. Parent-child relationships — from AST
6. Ambiguous or unobservable elements — explicitly marked

Gold is encoded in a separate sidecar (e.g.
`cache/stage_b_gold/case_B01_sidecar.json`). It must not reference any Stage B output.

### 6.3 Gold verification

Verify gold by a second annotator (or the same annotator on a later pass). Both must
agree. The gold sidecar is committed to the repository before any matcher code is
written.

---

## 7. Evaluation metrics and acceptance gates

### 7.1 Metrics (reported separately by mathematical construct)

| Metric | Establishes |
|---|---|
| Node association precision | Incorrect assignments |
| Node association recall | Missed assignments |
| Role accuracy | Correct base/exponent/numerator/denominator assignment |
| Glyph coverage | Fraction of relevant observations accounted for |
| Bbox IoU | Physical extent agreement |
| Relationship accuracy | Correct structural relationships |
| Ambiguity preservation | No forced assignments |
| Provenance completeness | Every result traceable to evidence |

### 7.2 Proposed acceptance gates

The Stage B evaluator compares matcher output against the independent gold sidecar.

| Gate | Requirement |
|---|---|
| B0 | Freeze Stage B input contract before matcher written |
| B1 | Gold sidecar produced and independently verified |
| B2 | Matcher produces sidecar with correct schema version |
| B3 | Node association precision ≥ threshold (per-case, not aggregate) |
| B4 | Node association recall ≥ threshold |
| B5 | Role accuracy ≥ threshold |
| B6 | Bbox IoU ≥ threshold |
| B7 | Ambiguity preserved (≥ N `ambiguous` links hold) |
| B8 | Relationship geometry present for all structural roles |
| B9 | Provenance complete (all records carry `pdf_sha256` + `source_occurrence_id`) |
| B10 | No forced `unresolved` nodes; `unresolved` count matches gold |
| B11 | No score override: failed mandatory gates produce `unverified_regression` |
| B12 | Second-paper generalization test (paper ≠ 1505.05770v6) |

### 7.3 Reporting

Metrics are reported per-case (B01–B08), never as a single aggregate. Each metric
must show: value, gold reference, and per-case breakdown. An aggregate score could
conceal a catastrophic failure on a specific construct (e.g., delimiters).

---

## 8. Non-negotiable safeguards

Carried into Stage B from the existing project rules:

- Frozen v1 delimiter engines remain untouched.
- No oracle-conditioned candidate generation.
- No gold leakage into candidate selection.
- No silent defaults or forced matches.
- No score overrides for failed mandatory gates.
- No merging of distinct benchmark populations.
- No claiming accuracy from schema or serialization tests.
- Every output retains `pdf_sha256`, `source_occurrence_id`, `extractor_version`,
  `ast_schema_version`.
- Preserve the existing 16-test association-contract baseline separately from new
  Stage B tests.

---

## 9. Implementation sequence

1. **Freeze Stage B input contract** — document field-by-field (§3). Verify no existing
   file changes.
2. **Establish independent gold** — annotate B01–B08 from 1505.05770v6; verify
   independently. Commit gold sidecars.
3. **Implement candidate association engine** — spatial constraints (Part 2),
   geometric residuals (Part 3), role-based matching (Part 4), composite handling
   (Part 5). Preserve all viable alternatives.
4. **Implement Stage B evaluator** — compare matcher output against gold sidecar.
   Report per-case metrics.
5. **Validate relationship geometry** — only after node-to-glyph associations pass
   gates B0–B9.
6. **Second-paper generalization** — run on a paper ≠ 1505.05770v6. Do not tune on
   the evaluation paper and describe it as independent validation.

---

## 10. Deliverable summary

| Artifact | Status |
|---|---|
| Stage B input contract | Done (§3) |
| Sidecar output contract | Done (§4) |
| Association algorithms | Done (§5) |
| Independent gold annotation protocol | Done (§6) |
| Evaluation metrics and gates | Done (§7) |
| Non-negotiable safeguards | Done (§8) |
| Implementation sequence | Done (§9) |

The blueprint is a research artifact. The matcher and evaluator code will be written
only after the gold sidecar is independently verified and committed.
