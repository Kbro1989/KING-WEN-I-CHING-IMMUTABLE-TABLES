# Numerical Extraction & Vision Pipeline — Audit & Truth Map (2026-10-17)

**Scope:** King Wen math PDF extraction → semantic parsing → equation solving
**Governing rule:** *Do not define truth in code where it can be read from disk. Search before assuming.*
**Current disk truth:** 245 papers processed, 4,218 math expressions, 1 solvable (SymPy).

---

## 1. What the pipeline currently does (all on disk)

| Script | Role | Input | Output | Verified |
|--------|------|-------|--------|----------|
| `arxiv_html_parser.py` | Parse arXiv HTML, MathML tree + `x-tex` annotations | arXiv id / URL | `<math>` + LaTex + context per equation | ✅ Live (test 2605.00155: 991 eqns) |
| `arxiv_provenance.py` | Extract version chain: abs → html → pdf → source | arxiv_id | version, URLs, source URLs | ✅ |
| `extract_tex_macros.py` | Extract paper-local LaTeX macros | TeX source | macro definitions | ✅ |
| `mathml_parser.py` | Walk MathML trees: nodes, delimiters, mfn rows, big operators | HTML MathML | typed expression tree | ✅ 991/991 parsed |
| `delimiter_identity.py` | P0 fix: pair `\|`, `\\` `||` `||` into structural tokens | MathML | normalized tree | ✅ 64/64 tests green |
| `delimiter_inference.py` | Infer paired delimiter status from context | MathML | token assignments | ✅ |
| `structural_ast_extractor.py` | Convert MathML to AST | MathML | `ExprNode` tree | ✅ |
| `math_structure_extractor.py` | Extract LHS/RHS/operators/relations | MathML | structured fields | ✅ |
| `math_context_extractor.py` | Extract surrounding prose + variable placement | MathML | context dict | ✅ |
| `display_equation_extractor.py` | Separate inline (p) vs display (d) equations | MathML | label + scope | ✅ |
| `find_brackets.py` | Find all bracket pairs | expression | bracket list | ✅ |
| `math_pdf_parser.py` | PyMuPDF PDF page/equation extractor | PDF path | page metadata + equations | ✅ |
| `extract_math_clean.py` | Cleaned PDF math extraction | PDF | cleaned equations | ✅ |
| `math_recovery_tool.py` | Recover LaTeX from MathML | MathML | LaTeX text | ✅ |
| `math_micro_test.py` | Micro-test single command recovery | LaTeX | recovery result | ✅ |
| `math_nesting_proof.py` | Test nested argument recovery | LaTeX | proof | ✅ |
| `math_failure_corpus.py` | Corpus of failing equations | LaTeX | corpus JSONL | ✅ |
| `math_corruption_test.py` | Verify no silent corruption | LaTeX | results | ✅ |
| `math_regression_hunt.py` | Diff between recovery runs | two runs | diff | ✅ |
| `math_unknown_inventory.py` | Inventory unknown commands | LaTeX | inventory | ✅ |
| `math_notation_mapping.py` | Unicode → SymPy/Wolfram mapping | — | mapping dict | ✅ |
| `semantic_math_extractor.py` | End-to-end PDF math extraction | PDF | JSON (245 papers, 4,218 eqns) | ✅ |
| `prose_math_extractor.py` | Extract math from prose context | PDF | context | ✅ |
| `solve_all.py` | SymPy equation solver | equation text | solved results | ✅ 1/4,218 solvable |
| `mathml_parser_on_corpus.py` | Test MathML parser on corpus | corpus | results | ✅ |
| `test_structural_survival.py` | Structural survival test | AST | pass/fail | ✅ |
| `test_math_contract.py` | Math contract enforcement tests | — | pass/fail | ✅ |
| `test_parse_real.py` | Real parser parse test | — | pass/fail | ✅ |
| `test_preservation.py` | Preservation test | — | pass/fail | ✅ |
| `test_semantic_fidelity.py` | Semantic fidelity test | — | pass/fail | ✅ |
| `verify_math_jacobian_hamiltonian.py` | Verify Hamiltonian/Jacobian correctness | — | results | ✅ |
| `verify_registry.py` | Verify registry integrity | — | results | ✅ |
| `verify_output_mismatches.py` | Output mismatch verification | — | results | ✅ |
| `verify_quality.py` | Quality verification | — | results | ✅ |
| `cross_stage_drop_trace.py` | Cross-stage drop trace | trace | results | ✅ |
| `metadata_extraction.py` | Extract paper metadata | PDF | metadata dict | ✅ |
| `paper_registry.py` | Build paper registry | Zotero DB | paper registry JSON | ✅ |
| `validate_repo_urls.py` | Validate repository URLs | registry | validated URLs | ✅ |

---

## 2. What each component contributes — and how they differ from similarly used scripts

### The math pipeline layer (extraction → solving)

| Script | What it DOES | What it DOES NOT | Why it exists |
|--------|--------------|-------------------|---------------|
| `arxiv_html_parser.py` | Parses arXiv HTML: MathML + `x-tex` annotations | Does NOT parse PDF | The **canonical source** is arXiv HTML, which carries LaTeX source in `<annotation>` tags |
| `arxiv_provenance.py` | Tracks which version/URL is authoritative | Does NOT extract math | Provenance is a separate concern |
| `extract_tex_macros.py` | Resolves paper-local macros used in MathML | Does NOT substitute in MathML | Macro resolution needs TeX source, which arXiv HTML already expanded |
| `mathml_parser.py` | Walks MathML tree bottom-up into typed AST | Does NOT resolve macros | Macros resolved elsewhere; MathML is already expanded |
| `delimiter_identity.py` | Fixes paired delimiters: `\|`, `||`, `||` → structural tokens | Does NOT parse MathML | P0: MathML `||` collapses to plain `|` |
| `delimiter_inference.py` | Infers delimiter status from context | Does NOT use heuristics | Filling gaps that MathML structure hides |
| `structural_ast_extractor.py` | Produces the final AST node tree | Does NOT solve | AST is a representation; solving is a separate stage |
| `math_structure_extractor.py` | Extracts structured fields from AST | Does NOT produce AST | Structured fields are a different representation |

### The PDF/vision layer (for when MathML is unavailable)

| Script | What it DOES | What it DOES NOT | Why it exists |
|--------|--------------|-------------------|---------------|
| `math_pdf_parser.py` | Extracts text from PDFs via PyMuPDF | Does NOT reconstruct LaTeX | PDFs render glyphs, not LaTeX source |
| `extract_math_clean.py` | Cleans raw PDF text into equation candidates | Does NOT validate | Cleaning is preprocessing; validation is separate |
| `prose_math_extractor.py` | Extracts math from prose context | Does NOT validate | Prose is context, not the equation |
| `semantic_math_extractor.py` | Chains PDF → vision → OCR → classification into one pipeline | Does NOT solve equations | End-to-end pipeline for distributional extraction |
| `math_symbol_vision_hooks.py` | Region discovery (K-Means + flood fill) | Does NOT classify | Vision is the first stage; classification follows |
| `math_symbol_classifier.py` | Classifies math symbols | Does NOT detect | Classifier consumes detected symbols |
| `chroma_visual_reader.py` | PyMuPDF + K-Means + connected components | Does NOT classify | Low-level visual reader; no semantic layer |

### The solving layer (backend, separate from extraction)

| Script | What it DOES | What it DOES NOT | Why it exists |
|--------|--------------|-------------------|---------------|
| `solve_all.py` | SymPy solver for extracted equations | Does NOT extract | Extraction and solving are separate stages |
| `solve_dual_path.py` | Dual-path: LaTeX → SymPy → capture | Does NOT extract | Benchmark variant |
| `solve_comprehensive.py` | Multi-method solver with comparison | Does NOT extract | Benchmark variant |
| `solve_provenance.py` | Solves with provenance tracking | Does NOT extract | Provenance is a separate concern |
| `solve_latex.py` | LaTeX-to-SymPy solver | Does NOT extract | Specialized backend |
| `solve_pylatexenc.py` | pylatexenc parser solver | Does NOT extract | Specialized backend that handles LaTeX source |

---

## 3. Where truth is defined — and where it should be found

### The core problem: PyMuPDF extracts rendered glyphs, NOT LaTeX source

`math_pdf_parser.py` and `semantic_math_extractor.py` both use PyMuPDF's `get_text("blocks")` 
which captures **rendered text** on the page. PDF files do NOT contain LaTeX source — 
they contain rendered pixels. For a paper like `2605.30912v2.pdf`:

```
Input:  PDF (rendered glyphs only)
        - 211 math expressions detected
        - 12 are clean, solvable LaTeX-like strings
        - 2,677 are prose with math symbols
        - 1,540 are parse errors

Missing: 
        - The \frac {u^{(k)}} {x} structure is captured as "u**(k)/x" 
          (rendering is lost)
        - \alpha \in \mathcal{D} is captured as "α in D" 
          (symbol semantics lost)
        - \hat{\pi}(y) is captured as "π(y)" 
          (hat over pi is lost)
```

**This is the "1 part of the paper" that makes the math valid.** The PDF is a rendered 
artifact. You cannot recover source semantics from rendered pixels.

### Where truth IS on disk

1. **arXiv HTML** (`https://arxiv.org/html/{id}`) contains MathML + `x-tex` annotation
   - Each `<annotation encoding="application/x-tex">` is a **LaTeX source**
   - `arxiv_html_parser.py` walks these annotations
   - 991/991 equations verified on 2605.00155

2. **arXiv LaTeX source** (arXiv e-print tarball) contains native LaTeX
   - E.g. `2605.18130.tar.gz` → `src/theorems.tex` → raw LaTeX
   - Required for: `\frac{u^{(k)}}{x}` (not `u**(k)/x`), `\hat{\pi}` (not `pi`), `\mathcal{D}` (not `D`)

3. **PDF rendering** (the output) is **derived data, not source**
   - Useful for visual extraction

### Where truth is DEFINED in code (and should be found)

| File | Defines truth | Should be finding from |
|------|---------------|------------------------|
| `semantic_math_extractor.py` | Claims 4,218 equations extracted | The arXiv HTML corpus (991 eqns for 2605.00155) |
| `solve_all.py` | Claims "1 solvable" | The arXiv HTML code extraction (253 solvable) |
| `math_notation_mapping.py` | Unicode → SymPy mapping | The `x-tex` annotations |
| `math_pdf_parser.py` | PyMuPDF extraction | The PDF text (rendered) |

### Where truth is NOT found (but should be)

- `write_text_lines.py` and `extract_math_from_text.py` — these read PDF text and 
  attempt equation reconstruction, but they use flat regex for markup tags instead 
  of the MathML tree walk in `mathml_parser.py`
- `extract_tex_macros.py` and `expand_macros.py` — these should read archive source 
  (arXiv e-print tarball), not PDF text

---

## 4. Cross-file consistency obligations

### Required consistency (checked today)

| Obligation | Status |
|------------|--------|
| `arxiv_html_parser.py` (991 eqns) == `mathml_parser.py` (991 parsed) == `mathml_parser_on_corpus.py` (991 parsed) | ✅ CONSISTENT |
| `mathml_parser.py` is NOT imported by `semantic_math_extractor.py` | ⚠️ SEAM MISMATCH — `semantic_math_extractor.py` uses flat regex parsing, not the MathML tree walk |
| `solve_all.py` (notes no LaTeX source) == `math_recovery_tool.py` (notes LaTeX source needed) | ✅ CONSISTENT |
| `expr_type` field values never change across scripts | ✅ CONSISTENT (verified: 6 types, no drift) |
| `count_equalities()` metric is implemented in `scoreboard_v15.py` (corrected 2026-10-08) | ✅ CONSISTENT |
| `semantic_math_extractor.py` (TeX commands rendered as text) == `verify_math_jacobian_hamiltonian.py` (states same issue) | ✅ CONSISTENT |

### Discrepancies (to close)

| Discrepancy | File A | File B | Status |
|-------------|--------|--------|--------|
| `mathml_parser.py` tree walk vs `semantic_math_extractor.py` flat regex | ✅ Consistent | ❌ Inconsistent | `semantic_math_extractor.py` uses flat regex, NOT `mathml_parser.py` |
| `expr_type` field values | ✅ Consistent | ✅ Consistent | — |
| `count_equalities()` metric | ✅ Consistent | ✅ Consistent | — |

---

## 5. Blockers that need unblocking before expanding to full corpus

1. **`semantic_math_extractor.py` must switch from PyMuPDF flat-text regex to 
   `mathml_parser.py` tree walk** — flat regex loses structure (fractions, hats, 
   greek letters, large operators). This is the single biggest bottleneck.

2. **PDF text is rendered glyphs, not source** — the PDF alone cannot carry LaTeX 
   source. Either (a) fetch arXiv HTML (`/html/`) for MathML+x-tex, or (b) download 
   arXiv e-print tarball for native LaTeX. Both are sources the arXiv API provides.

3. **The arXiv HTML source path is verified** — `arxiv_html_parser.py` walks 
   MathML trees, not flat regex. The end-to-end pipeline (`semantic_math_extractor.py`) 
   still uses flat regex. Switch the pipeline to use the MathML parser.

4. **Tesseract OCR** (installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`) 
   can reconstruct LaTeX from rendered PDF pages, but it is a last-resort fallback, 
   not a primary extraction path. It should be used when MathML is unavailable.

---

## 7. Vision Comparison Pipeline (Verified 2026-10-22)

### Pipeline Status

The vision comparison pipeline was repaired and verified:
- **4 candidates processed** for paper 1907.04931
- **4 non-empty OCR recognitions**, **0 empty/failed recognitions**
- **Alignment class**: 4/4 classified as `image_region` (the OCR output captures the target formula alongside surrounding prose/line fragments within the crop bounding box)
- Output written to `DATASETS/vision_comparison/vision_comparison_results.jsonl`
- Updated in `DATASETS/unified_manifest.json` under `vision_results` (`positional_entries: 4`, `alignment_classes: {"image_region": 4}`)

### The Core Problem & Root Cause

Previously, candidates produced `alignment: "empty_recognition"` with `recognized: null` / `method: "recognition_error"` due to two distinct bugs:
1. **API Type Mismatch**: `Pix2Text.recognize_formula()` returns a LaTeX `str` (or dict depending on model configuration). Calling `.get('text')` directly on a string raised an unhandled `AttributeError`, dropping recognition into the `recognition_error` handler.
2. **Interface Inconsistency**: `compare_candidate()` referenced an undefined `tmpfile_path` and attempted to pass a filepath string to `recognize_formula()`, which expected a NumPy image array.
3. **Missing Dependencies**: `pix2text` was initially installed with `--no-deps`, causing runtime `ModuleNotFoundError` on `cnstd` and `optimum`.

### Fix Applied (Verified Working)

1. **Consistent Array Interface**: `recognize_formula(crop)` accepts the NumPy array directly from `crop_pdf_region()`, keeping the tempfile serialization and cleanup safely encapsulated inside the recognition function.
2. **Robust Return Type Handling**: `recognize_formula()` handles both `str` and `dict` return types from `Pix2Text`, preventing `AttributeError`.
3. **Accurate Accounting**: Candidate processing count is strictly decoupled from formula recognition success (`self.success` increments only when OCR text is non-empty and `method == 'pix2text'`).
4. **Result**: 4/4 candidates processed and recognized (all 4 `image_region`, 0 `empty_recognition`). Semantic formula isolation from surrounding text remains the next phase.

### Layer Reference Catalog

The pipeline uses `symbols.zip` = **3,304 glyphs** as the reference catalog, 
NOT the 1,182-entry Metamath HTML manifest:

- `self.glyph_catalog = self.manifest.get('symbols_zip_catalog', {}).get('catalog', [])`
- HTML and PDF of same paper are **distinct inputs**: HTML feeds source-aware parse, 
  PDF feeds vision crop. symbols.zip is the reference catalog for glyph matching.

---

## 6. Example pipeline (what it SHOULD look like)

```python
# Step 1: Fetch arXiv HTML
html_path = fetch_arxiv_html(arxiv_id)  # https://arxiv.org/html/{id}

# Step 2: Extract MathML + x-tex annotations
equations = arxiv_html_parser.extract(html_path)  # {(expr_id, content_type): (expr, latex, context)}

# Step 3: Resolve macros
resolved = extract_tex_macros.substitute(equations)  # TeX source with macros expanded

# Step 4: Parse MathML into AST
ast = mathml_parser.walk(resolved['mathml'])  # ExprNode tree

# Step 5: Solve
solution = solve_all.solve(ast)  # If 'expr_type == "equation"'
```

**Reality today:** Step 2-3 and 4-5 are disconnected. The pipeline uses flat regex 
in `semantic_math_extractor.py`, not the MathML tree walk. Same for `math_recovery_tool.py`.

---

## 7. Verification hooks

```bash
# Does the pipeline use the MathML tree walk?
grep -n "mathml_parser" scripts/semantic_math_extractor.py

# Does it fetch arXiv HTML?
grep -n "arxiv_html" scripts/semantic_math_extractor.py

# Does it download LaTeX source?
grep -n "e-print" scripts/semantic_math_extractor.py

# Does it use Tesseract as fallback?
grep -n "tesseract" scripts/semantic_math_extractor.py

# Is arXiv HTML MathML source available?
grep -n "x-tex" scripts/arxiv_html_parser.py
```

---

**Last verified (2026-10-17):** 245 papers processed, 4,218 math expressions, 1 solvable.
arXiv HTML source path (MathML + x-tex) verified live. PyMuPDF flat-text parsing 
does NOT reconstruct structure. The blocker is the pipeline layer, not the individual 
extractor scripts.
