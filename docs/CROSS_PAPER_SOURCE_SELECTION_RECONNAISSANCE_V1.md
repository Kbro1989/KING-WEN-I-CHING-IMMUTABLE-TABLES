# Cross-Paper Source Selection & Typography Reconnaissance v1

**Specification Reference:** [`DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json) (`0368689c5da4...`)  
**Source Matrix JSON:** [`DATASETS/structural_preservation/cross_paper_source_selection_matrix_v1.json`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/structural_preservation/cross_paper_source_selection_matrix_v1.json)  
**Immutable Engine Baseline:** [`scripts/delimiter_aware_structural_recovery.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/delimiter_aware_structural_recovery.py) (`8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1`)  
**Status:** RECONNAISSANCE COMPLETE (Pre-Execution Baseline)

---

## 1. Reconnaissance Overview

To ensure that the mathematical delimiter recovery engine is not overfitted to Computer Modern (`CMEX10`) typography or simple single-matrix layouts, three independent candidate papers were surveyed across the corpus.

### Mandatory Reconnaissance Requirements Satisfied
- **Non-CMEX10 Extensible Delimiters:** Identified in TX Fonts (`txexs`), STIX OpenType (`STIXVariants`), and Latin Modern Math (`LMMathExtension10`).
- **Nested Structures:** Identified in multimodal sequence vector concatenation (nested brackets) and metric definitions (embedded brackets within norm expressions).
- **Fractions & Multiline Content:** Identified in linear discriminant metrics with $\frac{1}{2}[\text{tr}(\Sigma_A) + \dots]$.
- **Continuation Marker Diversity:** Identified in $3 \times 3$ symbolic block matrices exercising horizontal ($\cdots$), vertical ($\vdots$), and diagonal ($\ddots$) ellipses simultaneously.
- **Adjacent-Expression Boundaries:** Identified in adjacent stacked display equations and adjacent block-diagonal matrix pairings.

---

## 2. Nine-Field Source Selection Matrix

| Field | Candidate Paper 1 (Cluster-GCN) | Candidate Paper 2 (ViLT) | Candidate Paper 3 (Linear Probing) |
|---|---|---|---|
| **1. Paper Identifier** | `arXiv:1905.07953` | `arXiv:2102.03334` | `arXiv:2605.24856` |
| **2. PDF SHA-256** | `5e37bd23d65f20d215ad11e229816dfdf77b2debb15a5c2668a6c5b6d5a1aaab` | `916b5f4abe2bb5fdd2093bd1ca6ad8a6268e3f16b3837f51970c5dbb787e677c` | `6f9ec8acdb97ca691970982600c87618cef09526e53315afc2dd0e50741cceaf` |
| **3. Page & Coordinates** | Page 4 (0-based 3), $[116.2, 470.0, 230.0, 525.0]$ pt | Page 4 (0-based 3), $[318.0, 500.0, 465.0, 550.0]$ pt | Page 11 (0-based 10), $[231.5, 150.0, 380.0, 195.0]$ pt |
| **4. Delimiter Family** | Square brackets (`bmatrix`) | Square brackets (`[...]`) with sequence vectors | Extended norm ($\|\cdot\|$) and brackets (`[...]`) |
| **5. Font Encoding** | TX Fonts (`txexs`, `txsys`), Linux Libertine (`LinLibertine`) | STIX OpenType (`STIXVariants`, `STIXGeneral-Italic`) | Latin Modern Math (`LMMathExtension10`, `LMMathSymbols`) |
| **6. Structural Challenge** | `bmatrix` mapping, $3 \times 3$ block grid with $\cdots, \vdots, \ddots$, adjacent block matrix $\bar{A}$ | Nested concatenation ($z_0 = [\bar{t}+\dots; \bar{v}+\dots]$), stacked equations | Embedded fraction $\frac{1}{2} [\text{tr}(\Sigma_A) + \dots]$, adjacent superscript $^2$ |
| **7. Positive-Control Suitability** | Explicit block adjacency matrix $A = \bar{A} + \Delta = \begin{bmatrix} A_{11} & \cdots & A_{1c} \\ \vdots & \ddots & \vdots \\ A_{c1} & \cdots & A_{cc} \end{bmatrix}$ | Multimodal transformer input embedding equation with semicolon token vectors | Fisher linear concept separation metric combining vector distance with covariance traces |
| **8. Negative-Control Opportunity** | Intervening delimiter guard: $\bar{A} = \begin{bmatrix} \dots \end{bmatrix}$ below must not cross-pair with $A$ | Stacked display line $\hat{z}_d = \text{MSA}(\dots)$ at $y=548.8$ pt tests boundary clamping | Outer superscript $^2$ immediately adjacent to delimiter tests right-hand crop margin |
| **9. Independence Classification** | Distinct authors (Google/UT Austin), venue (KDD 2019), TX Fonts | Distinct authors (Kakao Enterprise), venue (ICML 2021), STIX fonts | Modern interpretability corpus, Latin Modern Math fonts |

---

## 3. Structural Challenge & Test Family Coverage

No single paper supplies all seven test families. The three papers collectively cover the required test conditions:

```
Test Family Coverage Distribution:
  FAM_001 (Delimiter Identity)    : Paper 1 (bmatrix), Paper 2 (brackets)
  FAM_002 (Nested Structures)     : Paper 2 (nested z0), Paper 3 (nested fraction-bracket)
  FAM_003 (Adjacent Matrices)     : Paper 1 (A vs \bar{A} on same page)
  FAM_004 (Embedded Mathematics)  : Paper 3 (fraction 1/2 + matrix traces)
  FAM_005 (Extensible Glyphs)     : Paper 1 (txexs), Paper 3 (LMMathExtension10)
  FAM_006 (Continuation Symbols)  : Paper 1 (\cdots, \vdots, \ddots), Paper 2 (\cdots)
  FAM_007 (Prose Adjacency)       : Paper 1 (prose gutter), Paper 2 (stacked equations)
```

---

## 4. Next Experimental Steps (Preserving Sequence)

Following the established protocol, execution will proceed in strict order:
1. **Gold Annotation Generation:** Establish ground-truth target files for the 3 candidate equations with verified coordinate lineage.
2. **Case Registry Schema Validation:** Validate every case against `cross_paper_delimiter_generalization_spec_v1.json` using [`scripts/validate_cross_paper_generalization_spec.py`](file:///c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/validate_cross_paper_generalization_spec.py).
3. **Registry Freeze:** Cryptographically freeze the input registry before detector execution.
4. **Baseline Engine Verification:** Confirm engine SHA-256 equals `8211592af549c292...`.
5. **Detector Run & Evaluation:** Execute the unchanged pipeline and report all five acceptance dimensions independently.

---

## 5. Typographical Resolution & Font Program Discrepancy Reconciliation

### 5.1 ViLT Font Program Discrepancy Resolution
- **Initial Reconnaissance Hypothesis:** STIXVariants / OpenType math.
- **Ground Truth PDF Stream Audit:** Direct inspection of `DATASETS/benchmark_pdfs/2102.03334.pdf` revealed that ViLT utilizes Computer Modern / Nimbus Roman Type 1 math fonts (`CMR10`, `CMMI10`, `CMSY10`, `NimbusRomNo9L-Regu`, `CMR7`, `CMMI7`).
- **Structural Classification:** Sequence vector concatenation brackets (`\mathbf{z}_0 = [\bar{\mathbf{t}} + \mathbf{t}_{\text{type}}; \bar{\mathbf{v}} + \mathbf{v}_{\text{type}}]`), evaluated under `FAM_002` (nested structures) with tight 2.45 pt vertical equation gutters to Equation (4), strictly distinguished from 2D matrix environments (`FAM_003`).

### 5.2 Linear Probing Glyph Identity: PostScript `/vextenddouble` Mapping
- **Font Program:** `DMPDUO+LMMathExtension10-Regular` (Type 1 math extension).
- **PDF Encoding Architecture:** Character code 13 (ASCII `0x0D` / `\r`) is explicitly mapped in PDF font dictionary Encoding Object 152 via:
  ```postscript
  /Differences [ 13 /vextenddouble 16 /parenleftBig ... ]
  ```
- **Glyph Semantics:** `/vextenddouble` is the standard TeX Math Extension glyph for extensible double vertical bars (norm delimiters). In Equation $S(l)$, 3 stacked `/vextenddouble` glyphs at $y \in [151.11, 173.03]$ assemble the extensible norm delimiter of total height 21.92 pt.

### 5.3 Trailing Superscript Boundary Isolation Guard
- **Superscript Position:** `LMRoman8-Regular` glyph `2` at `[348.74, 163.95, 352.97, 171.92]` directly abuts the closing norm delimiter at $x=348.74$ pt.
- **Evaluation Contract:**
  1. The superscript belongs to the squared norm term ($\|\dots\|^2$).
  2. The superscript is **not** part of the delimiter glyph inventory.
  3. The superscript must not be absorbed into the delimiter or truncated from the mathematical candidate.

