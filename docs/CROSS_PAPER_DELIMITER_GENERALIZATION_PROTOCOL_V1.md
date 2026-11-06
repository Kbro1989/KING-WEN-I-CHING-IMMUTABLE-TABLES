# Cross-Paper Delimiter Generalization Protocol v1

**Specification Identifier:** `CROSS-PAPER-DELIMITER-GENERALIZATION-SPEC-V1`  
**JSON Specification:** [`DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json)  
**Schema Validator:** [`scripts/validate_cross_paper_generalization_spec.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validate_cross_paper_generalization_spec.py)  
**Immutable Engine Baseline:** [`scripts/delimiter_aware_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/delimiter_aware_structural_recovery.py) (`8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1`)  
**Status:** FROZEN ACCEPTANCE SPECIFICATION (Pre-Paper Selection)

---

## 1. Objective and Boundary Isolation

The purpose of Cross-Paper Generalization v1 is to challenge the delimiter-aware structural recovery pipeline across diverse mathematical typographical layouts and font encodings. 

The two existing benchmarks establish evidence on two specific geometries:
1. `1505.05770` (Rezende & Mohamed): Tall single-column vector ($7 \times 1$).
2. `1212.0957` (Rahmani): Multi-column matrix ($6 \times 6$ numeric grid with horizontal and vertical continuation indicators, $7 \times 6$ structural layout with 40 recovered tokens).

Both prior cases utilized Computer Modern Extension (`CMEX10`) fonts. Cross-Paper Generalization v1 extends evaluation to at least three independent external papers, requiring font diversity beyond CMEX10 (e.g. STIX, TeX Gyre, Nimbus, Times-Math, TrueType/Type 1 math encodings).

The delimiter engine remains strictly **immutable** during baseline generalization evaluation. Source papers are selected only after this acceptance contract is frozen.

---

## 2. Seven Test Families

| Family ID | Family Name | Required Evidence | Primary Failure Mode | Mandatory Guard |
|---|---|---|---|---|
| `FAM_001` | **Delimiter Identity** | LaTeX environments: `bmatrix` (`[...]`), `Bmatrix` (`{...}`), `pmatrix` (`(...)`), `vmatrix` (`\|...\|`) | Wrong enclosure type or inline flattening | Rejection of single-line punctuation flattening; font lineage mapping |
| `FAM_002` | **Nested Structures** | Parent-child delimiter hierarchy (e.g. matrix within parenthesis, vector within norm) | Flattened nesting or boundary collision | Inner delimiter pairing resolves prior to/distinct from outer delimiter band |
| `FAM_003` | **Adjacent Matrices** | Horizontally or vertically adjacent mathematical enclosures associate to distinct pairs | Cross-pairing across intervening delimiters | Intervening delimiter guard halts candidate ray propagation |
| `FAM_004` | **Embedded Mathematics** | Matrix cells containing fractions ($\frac{a}{b}$), superscripts, or multiline expressions | Cell structure collapse or row corruption | Numerator/denominator preserved within single topological matrix cell |
| `FAM_005` | **Extensible Glyphs** | Assembly of top, extension, and bottom glyph pieces into unified scalable objects | Missing extension pieces or truncated height | $H_{\text{crop}} \ge H_{\text{glyph}}$ relative invariant verified without fixed thresholds |
| `FAM_006` | **Continuation Symbols** | Accurate extraction and grid positioning for horizontal ($\cdots$), vertical ($\vdots$), diagonal ($\ddots$) dots | Semantic substitution or dropped dots | Ellipsis tokens mapped to grid coordinates; series vs matrix row truncation distinguished |
| `FAM_007` | **Prose Adjacency** | Boundary isolation against immediately adjacent prose and following display/inline equations | Text contamination or equation absorption | Gutter clamping algorithm $crop\_y_1 < y_{\text{max\_bound}}$ with verified zero token leakage |

---

## 3. Strict Five-Axis Conjunctive Acceptance Policy

A test case is accepted as `PASSED_CERTIFIED` if and only if **all five** mandatory dimensions achieve `PASS`:

$$\text{Verdict} = \bigwedge_{i=1}^5 \left(\text{Dim}_i == \text{PASS}\right)$$

If any dimension fails, the case is marked `FAILED` with the corresponding failure verdict. If any required measurement or evidence artifact is missing, the verdict strictly evaluates to `NOT_VERIFIED`, never an inferred pass. **No composite score, harmonic mean, or IoU metric may override a failed or missing mandatory dimension.**

### The Five Mandatory Dimensions

1. **Geometric Localization (`dim_1_geometric_localization`):**
   - Complete mathematical enclosure covered with certified gutter clearance.
   - Bounding box boundary does not truncate delimiter serifs or interior entries.
2. **Glyph Completeness (`dim_2_glyph_completeness`):**
   - Every constituent glyph piece (top, extension, bottom, interior tokens) accounted for.
   - Zero missing extension segments.
3. **Structural Recovery Completeness (`dim_3_structural_recovery`):**
   - Row/column grid topology, parent-child nesting hierarchies, and alignment conventions preserved without collapse.
   - Non-conventional structural grids (e.g. $7 \times 6$ layout with 40 recovered tokens) explicitly mapped.
4. **Mathematical Semantic Fidelity (`dim_4_semantic_fidelity`):**
   - Zero cell value residual ($|\text{target} - \text{actual}| = 0$).
   - Negative signs strictly preserved (Unicode `U+2212` / `-` distinction from hyphen/prose em-dash).
   - Continuation markers semantically typed.
5. **Boundary Isolation (`dim_5_boundary_isolation`):**
   - Zero absorbed external tokens (prose lines, following display equations, equation numbers).
   - Perturbation stability verified against coordinate rounding margins.

---

## 4. Experimental Controls Protocol

For every evaluated test case, the evidence record must capture:
- `source_pdf`: Relative path, paper identifier, and cryptographically verified SHA-256.
- `page_1based`: 1-based page index.
- `gold_annotation_sha256`: Cryptographic hash of the reference annotation JSON.
- `engine_sha256`: Cryptographic hash of the delimiter engine (must equal `8211592af549c292...`).
- `candidate_hash`: SHA-256 of the emitted candidate record.
- `reconstruction_hash`: SHA-256 of the reconstructed AST and LaTeX output.
- `exact_test_command`: Verbatim CLI invocation.
- `test_exit_code`: Numeric process exit code.
- `positive_verdict`: `PASSED_CERTIFIED`, `FAILED`, or `NOT_VERIFIED`.
- `negative_control_verdicts`: Verification across all four required negative controls.

### Mandatory Negative Controls
1. `NEG_MISMATCHED_DELIMITER_TYPES`: Pairing opening parenthesis with closing bracket must be rejected.
2. `NEG_MISSING_CLOSING_PARTNER`: Opening delimiter without closing partner must be preserved as single structural candidate without speculative box synthesis.
3. `NEG_INTERVENING_DELIMITER_COLLISION`: Delimiters from adjacent matrices must not cross-pair over intervening candidates.
4. `NEG_TALL_NON_MATH_GRAPHIC`: Tall vertical rules, table borders, or non-math graphics must be rejected from delimiter classification based on font lineage and aspect ratio.

---

## 5. Structural Layout Convention

Downstream evaluators must strictly distinguish between:
- **Structural Layout Geometry:** The bounding dimensions of the 2D matrix environment (e.g., a $7 \times 6$ `pmatrix` layout).
- **Populated Cell Count:** The number of extracted tokens (e.g., 36 numeric cell tokens + 3 horizontal dot tokens + 1 vertical continuation token = 40 recovered tokens).

Evaluators must **never** assume that a $7 \times 6$ matrix implies 42 fully populated numeric entries. Sparse cells and continuation annotations must retain their distinct structural semantics.

