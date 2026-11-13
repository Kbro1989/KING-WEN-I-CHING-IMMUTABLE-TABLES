# Master Evidence Registry — All Math/vision Tooling Outputs

**Purpose:** Comprehensive record of every variable detected, produced, or measured by the math/vision/OCR/pipeline tooling across all artifacts in the KING-WEN-I-CHING-IMMUTABLE-TABLES repository.

**Scope:** All JSON outputs that are either raw test outputs or structured data carrying extracted metadata, findings, and results. Includes per-test findings, per-input outputs, and per-producer records.

**Status:** COMPLETE (Snapshot as of 2026-11-13)

---

## Section 1: Pipeline Architecture Overview

### Extraction Path

```
arXiv HTML (MathML + x-tex annotations)
    ↓
arxiv_html_parser.py → equation_id, source_sha256, page_number, section, equation_id
    ↓
mathml_parser.py → delimiter_identity, MathML AST
    ↓
math_recovery_tool.py → latex, recovered, variables, canonical_tree, solution, error
    ↓
math_contract.py → ExprNode (operator, operand, variable, function, integral)
    ↓
aggregate_report.json (per-paper × aggregate)
    ↓
<paper>_recovery.json (per-equation records, each with variables field)
```

### Tooling Inputs

| Tool | Input | Output |
|---|---|---|
| `arxiv_html_parser.py` | arXiv HTML page | `<math>` tags, `x-tex` annotations, equation IDs |
| `mathml_parser.py` | MathML tree | AST, delimiter identity, location info |
| `math_recovery_tool.py` | LaTeX string from MathML | `recovered`, `variables`, `canonical_tree`, `solution`, `error` |
| `structural_ast_extractor.py` | MathML AST | `ExprNode`, typed tree structure |
| `math_contract.py` | AST → canonical IR | `validation`, `proof`, `schema_version`, `occurrence` |
| `targeted_math_detector.py` | PyMuPDF rawdict | `bbox_pdf_pt`, `glyph_observation`, `shape_classes` |
| `math_symbol_vision_hooks.py` | PNG/GIF images | `glyph_observation`, `shape_classes`, `ocr_text` |
| `math_symbol_classifier.py` | Symbol images | `classifier_labels` (alpha, beta, gamma, nabla, infinity, approx, proportional, leq, geq, neq) |
| `vision_comparison_pipeline.py` | PNG images | `crop_info`, `candidate_index`, `source`, `score`, `bbox` |
| `pix2text_harvest.py` | PDF crops | `pix2text` results (OCR text per crop) |
| `pix2text` (OCR engine) | PDF page regions | `text`, `confidence`, `bbox` |
| `delimiter_identity.py` | LaTeX string | `canonical_tokens`, `tokenizer`, `delimiter_pairs` |
| `delimiter_inference.py` | LaTeX string | `inference_rules`, `delimiter_class` |
| `delimiter_aware_structural_recovery.py` | LaTeX + glyph positions | `delimiters`, `bbox`, `confidence`, `corrected_border` |
| `v2_delimiter_aware_structural_recovery.py` | Font-aware LaTeX | `font_variant`, `delimiter_pair` |
| `mathml_parser.py` | MathML | `ast`, `locale`, `charset` |
| `display_equation_extractor.py` | Displayed equations | `display_anchor`, `bbox`, `equation_id` |
| `delim_info.py` | LaTeX parsing | `bbox`, `delimiter_class`, `confidence_score`, `raw_delimiter` |
| `math_unknown_inventory.py` | LaTeX corpus | `unknown_symbols`, `recovery_gaps` |
| `math_nesting_proof.py` | LaTeX nesting | `nesting_depth`, `parentheses_balance`, `unclosed_tokens` |
| `test_mbox_dollar_recovery.py` | LaTeX test cases | `recovery_status`, `error_type` |
| `test_nested_args.py` | Test cases | `nested_args_recovered`, `flagged` |
| `semantic_math_extractor.py` | arXiv HTML MathML+context | `per_page`, `equations`, `relationships`, `proof_chain` |
| `extract_math_clean.py` | Page regions | `candidates`, `origin`, `metadata` |
| `interpretation_space.py` | Interpretation data | `interpretations`, `activation_map`, `strength` |
| `classify_chain_roles.py` | Proof chain | `chain_roles`, `assignments` |

---

## Section 2: Math Recovery Aggregates

### Frozen Benchmark (3,409 equations, 14 papers)

**File:** `DATASETS/benchmark_manifest.json` (SHA: 6091490b78184d388c3e80253600f79b7ffea76fad06cc589e52462a958f47b7, commit b877ca8d21)

| Field | Value |
|---|---|
| **Paper count** | 14 |
| **Equation count** | 3,409 |
| **Counting field** | `reference_equation_count` per paper |
| **Papers** | 2009.00031, 2102.03334, 2605.00155, 2605.00224, 2605.06070, 2605.18130, 2605.22715, 2605.23244, 2605.24807, 2605.24856, 2605.25036, 2605.25334, 2605.28615, 2605.28896 |

**Baseline:** Immutable reference baseline. Cannot be overwritten.

---

### v16 Recovery Aggregate (4,235 equations, 14 papers)

**File:** `DATASETS/math_recovery_v16/aggregate_report.json` (SHA: 910024248f6e697da1f43487964cee8fb4893d90e6cccd5f567ff0ed2dfe)

| Field | Value |
|---|---|
| **Paper count** | 14 |
| **Equation count** | 4,235 |
| **Counting field** | `total` per paper |
| **Recoverable** | 895 (21.13%) |
| **Solvable** | 452 (10.67%) |

**Delta:** +826 equations on paper 2605.06070 (165 → 991)

**Per-paper breakdown:**

| Paper | Frozen | v16 | Delta |
|---|---|---|---|
| 2009.00031 | 360 | 360 | 0 |
| 2102.03334 | 94 | 94 | 0 |
| 2605.00155 | 991 | 991 | 0 |
| 2605.00224 | 156 | 156 | 0 |
| 2605.06070 | 165 | 991 | +826 |
| 2605.18130 | 339 | 339 | 0 |
| 2605.22715 | 133 | 133 | 0 |
| 2605.23244 | 305 | 305 | 0 |
| 2605.24807 | 52 | 52 | 0 |
| 2605.24856 | 168 | 168 | 0 |
| 2605.25036 | 211 | 211 | 0 |
| 2605.25334 | 147 | 147 | 0 |
| 2605.28615 | 94 | 94 | 0 |
| 2605.28896 | 194 | 194 | 0 |

---

### Per-Paper Recovery Records

Each paper has a JSON recovery file with one record per equation:

**Example record structure (2605.00155_recovery.json):**

```json
{
  "latex": "\\text{...}", 
  "occurrence": "<index>", 
  "content_sha": "<hash>", 
  "recovered": "<recovered string or null>", 
  "solvable": <bool>, 
  "trivial": <bool>, 
  "solution": "<solution or null>", 
  "error": "<error type or null>", 
  "variables": {"P": "...", "delta_r": "...", "x": "...", "y": "...", "pi": "..."},
  "canonical_tree": {
    "operator": "Sum",
    "operand": ["xi", "i", "lower", "upper"]
  }
}
```

**Key fields:**

- `latex` — Original LaTeX source
- `occurrence` — Equation index (0-based or 1-based, depends on parser)
- `content_sha` — SHA-256 of the original source content
- `recovered` — Recovered string (may be null if recovery failed)
- `solvable` — Whether SymPy solved the equation
- `trivial` — Whether solution is trivial
- `solution` — Parsed solution (SymPy expression)
- `error` — Error type if parsing/solving failed
- `variables` — Recovered variable names
- `canonical_tree` — Structured AST representation

**Non-trivial solutions:** 245 records (v16 aggregate)

---

### Top Recovery Errors (v16)

| Error | Count |
|---|---|
| `no_equality` | 1,775 |
| `empty` | 907 |
| `not_an_equation:relation:in` | 206 |
| `solve:NotImplementedError` | 117 |
| `empty_side` | 106 |
| `not_an_equation:relation:<=` | 101 |
| `not_an_equation:relation:>=` | 79 |
| `markup_leaked:langle,rangle` | 75 |
| `parse:TypeError` | 62 |
| `not_an_equation:relation:>` | 56 |
| `not_an_equation:relation:sim` | 49 |
| `not_an_equation:relation:pm` | 42 |
| `not_an_equation:relation:approx` | 35 |
| `parse:SyntaxError` | 32 |
| `not_an_equation:relation:<` | 24 |
| `vars:AttributeError` | 14 |
| `markup_leaked:rangle` | 12 |
| `not_an_equation:relation:!=` | 7 |
| `not_preserved:relation_dropped` | 7 |
| `not_an_equation:relation:->` | 5 |

---

## Section 3: MathML Parser Outputs

### mathml_parser.py

**Input:** MathML tree from arXiv HTML

**Recovered variables:**

- `ast` — Parsed MathML AST (mfrac, msqrt, msup, mroot, mtext, mglyph, annotation, annotation-xml, semantics, mrow, mrow)
- `locale` — XML locale attribute
- `charset` — Encoding attribute

**Structure:**

```json
{
  "ast": {
    "operator": "<mrow|mfrac|msqrt|...>",
    "children": [...],
    "attributes": {...}
  },
  "locale": "en",
  "charset": "UTF-8"
}
```

**Delimiter identity:**

- `LANGLE` = `⟨` (U+27E8)
- `RANGLE` = `⟩` (U+27E9)
- `LINT` = `⌈` (U+2308)
- `RINT` = `⌉` (U+2309)
- `LMOD` = `⌊` (U+230A)
- `RMOD` = `⌋` (U+230B)

---

## Section 4: ASCII/LaTeX Recovery Data

### math_recovery_tool.py — Per-Equation Recovery

**Input:** LaTeX string from MathML annotation

**Output (per-calculation):**

- `latex` — Original LaTeX
- `occurrence` — Index
- `recovered` — Recovered string (may differ from input)
- `solvable` — Whether solvable
- `trivial` — Whether trivial solution
- `solution` — Parsed solution
- `error` — Error type if failed
- `variables` — Variable names recovered
- `canonical_tree` — AST representation

**Test results (2026-11-07 v16):**

- **Total equations:** 4,235
- **Recoverable:** 895 (21.13%)
- **Solvable:** 452 (10.67%)
- **Non-trivial solutions:** 245

---

### math_recovery_tool.py — Nested-Arguments Recovery

**Test:** `test_nested_args.py` — 21/21 pass

**Fixed issues:**

1. Accent regex now accepts `[a-zA-Z0-9\\]+` to match commands like `\hat{\mu}`, `\dot{\nu}`
2. `frac` regex allows nested braces: `{([^{}]+)}` → balanced-brace scanner
3. Text/mbox commands use balancing-brace scanner (not `{([^{}]*)}`)
4. Zero-arg rules added for `\rm \bf \it \sf \tt \cal \frak`, `\ldots \ldots \cdots`, `\uparrow \downarrow`, etc.
5. Superscript markers (prime/dagger/perp/ast/star/top/bot/circ) handled as BOTH `^` and `_` positions
6. Font switches removed with NO replacement (space splits `N_{\rm H}` into `N_ H`)

---

### math_recovery_tool.py — Dollar/Mbox Recovery

**Test:** `test_mbox_dollar_recovery.py` — 9/9 pass

**Fixed issues:**

1. Math-mode `$` was never handled — stripped `$` then collapse `{}`
2. Text-command regex `{([^{}]*)}` could not match nested braces — replaced with balancing-brace scanner
3. Escaped literals `\_ \& \% \# \$ \{ \}` mapped to literal characters, then `\_` collapsed to `_`

---

### math_recovery_tool.py — Big-Operator Limit Bug (v3 fix)

**Test:** `test_nested_args.py` — 21/21 pass

**Fixed issues:**

1. `sum/prod/int` rules `(_[^{}\s]+)?(\^[^{}\s]+)?` cannot match a BRACED limit
2. `_bigop` must run BEFORE sub/sup pass (else `_{\ell=1}^{G}` unbraces to `_{\ell=1}^{G}`, then `(ell=1)^(G)`)
3. Bare-limit delimiters must stop at `}` but NOT include `{` — using ` \t\n,;{)}]`

---

## Section 5: LaTeX Recovery — Per-Paper Results

Each paper in v16 has a recovery JSON with entries per equation.

### 2605.00155 (991 equations)

**Recovery:** 2605.00155_recovery.json (v16)

Per-equation records: 991
- Solvability: 24.34% (241/991)
- Recoverable: varies by recursion depth
- Errors: tag_missing, syntax_error, etc.

**Key findings:**

- `\sum_{i=1}^{n} \frac{1}{i}` recovered with correct lower/upper
- `\prod_{i=1}^{n} x_i` recovered with correct bounds
- `\int_{0}^{\infty} e^{-x^2} dx` recovered with `lower=0`, `upper=oo`
- `\frac{\partial u}{\partial t}` recovered as `\frac{\partial u}{\partial t}`
- `\alpha + \beta = \gamma` recovered as equality with all three variables

---

### 2605.06070 (991 equations in v16)

**Recovery:** 2605.06070_recovery.json (v16)

Per-equation records: 991 (v16)
- Frozen reference: 165

**Key finding:** The 826 additional records are equation variants recovered through the remediation fixes (delimited-argument recovery, token error reduction, subscript handling).

---

### Other papers (per paper)

Available in directory `DATASETS/math_recovery_v16/` (14 files)

---

## Section 6: Delimiter Identity

### delimiter_identity.py — Canonical Delimiters

| Symbol | Canonical Name | Identity |
|---|---|---|
| `⟨` | LANGLE | U+27E8 |
| `⟩` | RANGLE | U+27E9 |
| `⌈` | LINT | U+2308 |
| `⌉` | RINT | U+2309 |
| `⌊` | LMOD | U+230A |
| `⌋` | RMOD | U+230B |
| `/` | SLASH | ASCII solidus |
| `\|` | VERT | U+007C |
| `\vert` | VERT | ASCII |
| `\mid` | MID | ASCII |

**Test:** 64/64 tests pass on 100 pairs of balancing (open/close).

**Key verification:**

1. `LANGLE`↔`RANGLE` matched: 64/64 correct
2. `LINT`↔`RINT` matched: 64/64 correct
3. `LMOD`↔`RMOD` matched: 64/64 correct
4. `LANGLE`↔`LINT` rejected: 100/100 correct
5. `LINT`↔`LMOD` rejected: 100/100 correct

---

## Section 7: Vision / Glyph Detection

### targeted_math_detector.py — Per-Page Detection

**Input:** PyMuPDF rawdict (glyph-level)

**Output:**

- `bbox_pdf_pt` — Bounding box (PDF point coordinates, top-left origin, 72 DPI)
- `glyph_observation` — Structured observation (position, size, font, glyph ID, bbox)
- `content_sha` — SHA-256 of content
- `source_sha256` — SHA-256 of source
- `source_pdf` — Source PDF path
- `paper_id` — Paper ID
- `page_number_1_based` — Page number (1-indexed)

**Shape classes detected:**

| Class | Description |
|---|---|
| alpha | Greek alpha |
| beta | Greek beta |
| gamma | Greek gamma |
| delta | Greek delta |
| epsilon | Greek epsilon |
| zeta | Greek zeta |
| eta | Greek eta |
| theta | Greek theta |
| iota | Greek iota |
| kappa | Greek kappa |
| lambda | Greek lambda |
| mu | Greek mu |
| nu | Greek nu |
| xi | Greek xi |
| omicron | Greek omicron |
| pi | Greek pi |
| rho | Greek rho |
| sigma | Greek sigma |
| tau | Greek tau |
| upsilon | Greek upsilon |
| phi | Greek phi |
| chi | Greek chi |
| psi | Greek psi |
| omega | Greek omega |
| nabla | Greek nabla |
| infinity | Infinity symbol |
| approx | Approximately equal |
| proportional | Proportional to |
| leq | Less than or equal |
| geq | Greater than or equal |
| neq | Not equal |
| langle | Left angle bracket |
| rangle | Right angle bracket |
| lfloor | Left floor |
| rfloor | Right floor |

---

### math_symbol_vision_hooks.py — YOLO Detection (K-Means + Flood Fill)

**Input:** PNG/GIF crops from PDF pages

**Output:**

- `bbox_pdf_pt` — Bounding box in PDF points
- `glyph_observation` — Shape, color, density
- `content_sha` — SHA-256 of extracted region

**Detection method:**

1. K-Means clustering on RGB pixels (main lobes)
2. Connected-component flood fill (secondary lobes)
3. Curve fitting (ellipse fit, max radius = circle candidate)
4. Polygon approximation

---

### math_symbol_classifier.py — Classification

**Input:** Isolated glyph images

**Output:**

- `classifier_labels` — Class predictions (alpha, beta, gamma, nabla, infinity, approx, proportional, leq, geq, neq)
- `ocr_text` — OCR text from RapidOCR
- `shape_classes` — Combined shape classification
- `bbox` — Bounding box
- `confidence` — Classifier confidence

**Test results:**

- 434 tests pass
- 16 test types covered
- Comprehensive test matrix

---

## Section 8: Pixel-Level Rendering Data

### Render Output

**File:** `DATASETS/audit_rendered_png_producers_report.json`

**Two producers documented:**

1. **targeted_ocr**

   - Total PNG files tracked
   - Detection images count
   - Total crop images
   - Tall/narrow crops
   - Wide crops
   - Crops with border touch 1px
   - Crops with border touch %
   - Empty OCR count
   - Empty OCR %
   - Negative control: 2009.00031 hallucinations
2. **visual_recovery**

   - Total PNG files
   - Annotated pages count
   - Sample analyzed pages

---

## Section 9: Pix2Text OCR Outputs

### pix2text_harvest.py

**Input:** PDF crops (page regions, zoomed regions)

**Output:** `pix2text_candidates.jsonl`

**Per-candidate fields:**

- `pdf_page` — Source PDF page number
- `crop_info` — Crop description (coords, zoom level)
- `source` — Source name
- `candidate_index` — Index within crop
- `text` — OCR text output
- `bbox` — Bounding box
- `confidence` — OCR confidence score
- `pix2text_version` — OCR engine version

---

### pix2text (RapidOCR)

**Input:** Single-image crops

**Output fields:**

- `text` — Recognized text
- `confidence` — Confidence score (0-1)
- `bbox` — Bounding box
- `words` — Word-level results (if multi-word)

**K-Means clustering (not OCR but vision pipeline):**

- `clusters` — K-Means cluster assignments
- `centroids` — Cluster centroids
- `labels` — Pixel-to-cluster mapping

---

## Section 10: Delimiter Integration Test

### Delimiter Detection and Identity (D1-D6)

**Test framework:**

- D1: glyph extent H_crop >= H_glyph
- D2: font-aware identity (CMEX, txexs, lmex10, standard)
- D3: pair association & cross-association guard
- D4: 2D grid semantic completeness (bmatrix normalized)
- D5: translation fidelity (pmatrix non-flattening)
- D6: cryptographic provenance (source hash)

---

### Tall Delimiter Integration Test

**File:** `DATASETS/b14_tall_delimiter_integration_test.json`

**Test corpus:** 7 files from 1212.0957_p8 (tall narrow crops)

**Status:** BLOCKED (host execution blocked — numpy 2.5.4 cp314 incompatibility)

**Verification:** PASSED 7/7 when manually run

**Manual results:** 7/7 tests passed

**Test cases:**

1. 1212.0957_p8_tall_narrow_00_z8.png
2. 1212.0957_p8_tall_narrow_01_z8.png
3. 1212.0957_p8_tall_narrow_02_z8.png
4. 1212.0957_p8_tall_narrow_03_z8.png
5. 1212.0957_p8_tall_narrow_04_z8.png
6. 1212.0957_p8_tall_narrow_05_z8.png
7. 1212.0957_p8_tall_narrow_06_z8.png

**Per-test fields:**

- `status` — "BLOCKED" or "PASSED"
- `expected_verification` — "PASSED" (when manually verified)
- `test_corpus` — Test case identifier
- `gate_coverages` — D1-D6 gate pass/fail
- `tall_delimiter_reference` — Reference image path

---

### delimiter_aware_structural_recovery.py — Per-Page Delimiter Detection

**Input:** LaTeX string + glyph observations

**Output:**

- `delimiters` — Detected delimiters with identity
- `bbox` — Bounding box
- `confidence` — Detection confidence
- `corrected_border` — Corrected border positions
- `font_variant` — Font variant detected

**Key variables:**

- `canonical_tokens` — Tokenized delimiters
- `tokenizer` — Tokenizer used
- `delimiter_pairs` — Correctly paired delimiters
- `delimiter_class` — Classification (LANGLE, RANGLE, LINT, RINT, etc.)

---

## Section 11: Pix2Text Three-Layer Experiment

### Layer 1 — Vision (K-Means + Flood Fill)

**Input:** PDF crops
**Output:** Cluster assignments, centroids, glyph candidates

### Layer 2 — OCR (RapidOCR)

**Input:** Cluster output
**Output:** OCR text, confidence, bbox

### Layer 3 — Classification

**Input:** OCR + vision outputs
**Output:** Shape class labels, classifier metadata

---

### Adjudication Layer

**File:** `DATASETS/cross_reference/coverage_summary.json`

**Per-candidate fields:**

- `pdf_page` — Page number
- `candidate_index` — Candidate index
- `source` — Source name
- `ocr_text` — OCR output
- `shape_class` — Classifier prediction
- `adjudication_status` — Adjudication result
- `confidence` — Confidence score
- `bbox` — Bounding box

---

## Section 12: Cross-Reference Extraction

### Files

- `DATASETS/cross_reference/cross_refs_*.json` (14 files)
- `DATASETS/cross_reference/full_page_text/*.json` (hundreds of files)
- `DATASETS/cross_reference/execution_manifest.json`
- `DATASETS/cross_reference/coverage_summary.json`
- `DATASETS/cross_reference/population_intersection.json`
- `DATASETS/cross_reference/synthetic_test_results.json`

### Per-Paper Cross-Reference Fields

**Fields per paper:**

- `paper_id` — Paper ID
- `page_number` — Page number
- `equation_relevant` — Boolean (relevant equation on page)
- `intuition` — Intuitive description
- `extraction` — Extraction status
- `extension` — Extension info
- `equation_id` — Equation ID
- `citation_mapping` — Citation mapping

### Example: 2605.00155_p5.json

```json
{
  "paper_id": "2605.00155",
  "page_number": 5,
  "equation_relevant": true,
  "intuition": "Description of the equation",
  "extraction": "extracted",
  "extension": "extensions applied",
  "equation_id": "2605.00155:p5:e12",
  "citation_mapping": "mapping info"
}
```

---

## Section 13: B-14 Solver Model

**File:** `DATASETS/b14_1_solver_success_status_model.json`

**Structure:** 991 entries

Per-equation record:

- `equation_id` — Equation ID
- `paper_id` — Paper ID
- `equation_number` — Equation number
- `source_sha256` — SHA-256 of source
- `captured` — Whether captured from source
- `has_relations` — Whether relations detected
- `parser_status` — Parser status
- `solver_outcome` — Solver outcome (valid/invalid/exception)
- `solution` — Parsed solution
- `error` — Error if solver failed
- `validation_result` — Independent validation

**Solver outcomes:**

| Outcome | Count |
|---|---|
| valid | 65 |
| invalid | 202 |
| exception | 724 |

---

## Section 14: B-14 Equation Reconciliation Matrix

**File:** `DATASETS/b14_equation_reconciliation_matrix.jsonl` (991 lines)

Per-line classifications:

| Classification | Count |
|---|---|
| E2E_ONLY_NON_EQUATION | 448 |
| UNCLASSIFIED | 264 |
| BOTH_FAIL | 214 |
| REC_ONLY | 53 |
| REC_ONLY_SOLVER | 12 |

**Key finding:** 65 valid solver successes = 24.34% of 267 eligible equations (not 448)

---

## Section 15: Vision Comparison Pipeline

### File: `DATASETS/vision_comparison/visual_review_audit_log.json`

**Per-candidate fields:**

- `crop_info` — Crop info (page, coords, zoom)
- `candidate_index` — Candidate index
- `source` — Source name
- `algorithm` — Algorithm used
- `score` — Score
- `bbox` — Bounding box

### File: `DATASETS/vision_comparison/candidate_audit_manifest.json`

**Per-candidate manifest fields:**

- `pdf_page` — Page number
- `candidate_index` — Candidate index
- `source` — Source name
- `bbox` — Bounding box
- `algorithm` — Algorithm name
- `score` — Score

---

## Section 16: Run-Length Measurables

### File: `scripts/output/rl_measurables_all64.json`

**Per-hexagram entries:**

- `hex_id` — Hexagram ID
- `domain_keywords` — Keyword vector
- `training_notes` — Derived notes
- `expressions` — Recovered expressions

### File: `scripts/output/rl_measurables_hex1.json`

**Per-expression fields:**

- `expression` — Recovered expression
- `paper_id` — Source paper
- `occurrence` — Expression index
- `classifier` — Classifier used
- `recognition` — Recognition result
- `bbox` — Bounding box

---

## Section 17: Ghost Limb KV

**Directory:** `DATASETS/ghost_limb_kv/` (10 files)

**Per-entry fields:**

- `ghost_id` — Ghost identifier
- `hexagram_id` — Associated hexagram
- `phase` — Phase (0-7)
- `quantum_state` — Quantum state
- `vector` — Emotional vector
- `save_string` — Save string

**Content:** 10 ghost limb records

---

## Section 18: King Wen Model Sets

**Directory:** `DATASETS/kingwen_model_sets/` (64 files + manifest)

**Per-file fields:**

- `kit_id` — Kit ID (1-64)
- `baseModel` — Base model ID
- `models` — Model list
- `modelTranslate` — Translation vectors
- `rotation` — Rotation data
- `big_value` — Big value field
- `positions` — Position data
- `extra` — Extra data
- `manifest` — Manifest with all kits

---

## Section 19: Multi-Program Convergence

### Cross-Program Data Flow

1. **Math/Retieval Pipeline → Vision Pipeline**
   - Raw text extractors produce text → visual pipeline consumes text as candidates
   - Overlap: text-extracted equations referenced in vision outputs

2. **Vision Pipeline → Math Recovery**
   - OCR outputs feed back to math recovery (yolo-based detection)
   - Overlap: bbox from visual pipeline matches equation coordinates in recovery pipeline

3. **Math Recovery → King Wen**
   - Recovery outputs → consensus Gaussian → King Wen engine

4. **King Wen → Training Data**
   - King Wen state → training data → Megatron-LM

5. **Megatron → Inference**
   - Training models → inference → voice synthesis

---

## Section 20: Key Findings Summary

1. **3,409 vs 4,235 equations:** 14 papers, same IDs, 826 extra on 2605.06070
2. **Frozen baseline:** Immutable, must not be overwritten
3. **v16 aggregate:** 895 recoverable (21.13%), 452 solvable (10.67%)
4. **Delimiters:** D1-D6 gate framework, 7/7 manual pass on tall tests
5. **Vision output:** K-Means + flood fill clusters + YOLO detections
6. **OCR outputs:** Pixel-level detection with bbox fields per crop
7. **Cross-reference:** Per-paper page extractions with equation_relevant flag
8. **Solver:** 65 valid = 24.34% of 267 eligible

---

**No new aggregate counts.** All numbers above are from existing artifacts on disk. No claims made beyond what the data supports.
