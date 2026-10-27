# King Wen Math Extraction/Recovery/Vision/Debugging → Lua Plugin Mapping

## Purpose

This document maps each math extraction, recovery, vision, and debugging tool in
`KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/` to its Lua plugin usage pattern.
The goal is a **King Wen math specific Lua plugin** that reuses the verified
Python extraction/recovery/vision/debugging pipeline as a Lua module.

**Canonical repo:** `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES`
**Read-only constraint:** `C:\ProgramData\Jagex` is read-only — no edits there.
**Default math source:** arXiv HTML MathML + x-tex annotations. PDF requires `--pdf`.
**Output:** `lua-math-tool.md` (this file) + future Lua plugin.

---

## 1. semantic_math_extractor.py — Core Math Extraction

**Purpose:** Extract math expressions from 245 Zotero PDFs with Unicode math
preservation. Block-based PyMuPDF extraction. Outputs semantic_math_zotero_full.json
(159MB, 4218 expressions, 183017 proof chain elements).

**Key needs:**
- Block-level text extraction preserving spatial layout
- Unicode math symbol preservation (φ, √, ∫, ≡, ≤)
- Proof chain element collection
- arXiv ID → PDF path resolution
- Paper-level metadata (category, page count)

**Lua mapping:**
```lua
-- Semantic math extraction module
local semantic_math = {}

function semantic_math.extract(pdf_path)
    -- PyMuPDF block extraction → Lua table of expressions
    -- Returns: { expressions = [...], proof_chain = [...], metadata = {...} }
end

function semantic_math.extract_batch(pdf_dir)
    -- Batch extraction across directory
end

function semantic_math.resolve_arxiv(arxiv_id)
    -- arXiv ID → PDF path resolution
end
```

**Dependencies:** pymupdf (Lua binding: lupa or LuaJIT FFI)
**Lua usage:** `semantic_math.extract(path)` returns structured extraction table

---

## 2. mathml_parser.py — MathML Tree Parsing

**Purpose:** Parse arXiv HTML MathML into canonical expression trees.
Structural conservation invariant: no MathML structural child may disappear
merely because its node type is unsupported.

**Key needs:**
- MathML tree walk (bottom-up)
- Structural conservation: munder/mover/munderover must preserve under/over children
- Delimiter identity: langle/rangle, lVert/rVert, lfloor/rfloor, lceil/rceil
- Conditional bar (∣) preservation
- Differential (ⅆ) preservation
- Integral limits + differential preservation
- Big operator limit handling (sum/prod/int with braced limits)

**Lua mapping:**
```lua
local mathml_parser = {}

function mathml_parser.parse(mathml_string)
    -- Returns ExprNode tree
    -- { kind="fraction", num=..., den=... }
    -- { kind="operator", name="Sum", lower=..., upper=..., body=... }
    -- { kind="identifier", name="alpha" }
end

function mathml_parser.walk_bottom_up(node, fn)
    -- Bottom-up tree traversal
end

function mathml_parser.conserve_structure(node)
    -- Ensure no structural child disappears
    -- munder: base + under (not just base)
    -- munderover: base + under + over
    -- mtable: all rows/cells
    -- mfrac: numerator + denominator
end
```

**Dependencies:** Lua XML parser (lxp or xml2lua)
**Lua usage:** `mathml_parser.parse(html_math_tag)` → ExprNode tree

---

## 3. math_recovery_tool.py — Math Recovery/Translation

**Purpose:** Recover and translate math expressions from LaTeX to canonical
form. Handles nested arguments, accents, big operators, escaped literals.

**Key needs:**
- Balancing-brace scanner (_brace_scan)
- Zero-arg command rules (rm, bf, it, sf, tt, etc.)
- Accent fusion (\bar{\alpha} → alphabar, not alpha_bar)
- Escaped literal handling (\_ \& \% \# \$ \{ \})
- Big operator limit parsing (sum/prod/int with braced limits)
- Function-argument joining
- LaTeX → canonical token stream

**Lua mapping:**
```lua
local math_recovery = {}

function math_recovery.brace_scan(s, start)
    -- Returns (inner, end) for balanced brace pair
end

function math_recovery.apply_command(s, cmd, nargs, fn)
    -- Apply command with nargs arguments
end

function math_recovery.recover(latex_string)
    -- Full recovery pipeline
    -- Returns canonical token stream
end

function math_recovery.normalize_norms(latex_string)
    -- Position-based NORM_OPEN/NORM_CLOSE pairing
end
```

**Dependencies:** Lua pattern matching (string.match/gmatch)
**Lua usage:** `math_recovery.recover(latex)` → canonical tokens

---

## 4. visual_math_translator.py — Visual Math Translation

**Purpose:** Translate visual math structures (fraction bars, delimiters,
cases braces) from 2D PDF geometry into canonical form.

**Key needs:**
- K-Means color quantization (scipy.cluster.vq.kmeans2)
- Connected component analysis (scipy.ndimage.label)
- Region classification (fraction_bar, cases_brace, large_bracket, etc.)
- Structural assembly (fraction: numerator/denominator; cases: branches)
- Confidence scoring per structure

**Lua mapping:**
```lua
local visual_math = {}

function visual_math.quantize(image_array, max_colors)
    -- K-Means color quantization
    -- Returns centroids, labels, palette
end

function visual_math.find_regions(image_array, assignments, palette)
    -- Connected component analysis
    -- Returns region bounding boxes
end

function visual_math.classify_region(region)
    -- Classify: fraction_bar, cases_brace, large_bracket, vertical_bar, etc.
end

function visual_math.assemble_structure(regions)
    -- Assemble fraction/cases/enclosed_group from regions
    -- Returns VisualMathStructure
end
```

**Dependencies:** Lua image processing (limage or custom)
**Lua usage:** `visual_math.quantize(img, 16)` → (centroids, labels, palette)

---

## 5. math_contract.py — Canonical Schema

**Purpose:** Shared contract between extraction, parsing, solving, reporting.
Four independent status dimensions: ParseStatus, StructuralStatus,
BackendStatus, SolutionStatus.

**Key needs:**
- Status type definitions (Literal enums)
- ExprNode recursive tree (fraction, operator, identifier, number, relation)
- SourceOccurrence with dual hashing (source_hash + extraction_hash)
- RecoveryRecord with occurrence conservation
- Occurrence key generation (SHA-256 over paper_id/version/locator/index)
- NODE_KINDS frozenset

**Lua mapping:**
```lua
local math_contract = {}

-- Status types
math_contract.ParseStatus = { "complete", "partial", "unsupported", "failed" }
math_contract.StructuralStatus = { "verified", "equivalent", "lossy", "corrupted", "unverified", "partial" }
math_contract.BackendStatus = { "not_attempted", "accepted", "rejected", "error" }
math_contract.SolutionStatus = { "not_attempted", "solved", "evaluated", "no_solution", "undetermined", "error" }

-- ExprNode
function math_contract.make_node(kind, ...)
    -- kind: identifier, number, operator, relation, fraction, etc.
end

-- Occurrence key
function math_contract.occurrence_key(paper_id, version, locator, index)
    -- SHA-256 over identity tuple
end

-- Recovery record
function math_contract.make_recovery_record(occurrence, parsed, backend_status, solution_status)
end
```

**Dependencies:** Lua crypto (sha256), json
**Lua usage:** `math_contract.occurrence_key(id, ver, loc, idx)` → string key

---

## 6. math_pdf_parser.py — PDF Parser Pipeline

**Purpose:** 6-layer formal math research PDF parser. Layers:
1. Text Extraction (PyMuPDF)
2. Vision Region Detection (K-Means + flood fill)
3. OCR (Tesseract)
4. Math Symbol Classification
5. Spatial Relationship Extraction
6. Equation Structure Assembly

**Key needs:**
- PyMuPDF page rendering and text extraction
- K-Means color quantization
- Flood fill connected component analysis
- Tesseract OCR integration
- Math symbol lookup table (Greek, operators, brackets)
- Spatial relationship extraction (fraction bars, delimiters)
- Equation structure assembly

**Lua mapping:**
```lua
local math_pdf_parser = {}

function math_pdf_parser.extract_text_blocks(pdf_path, page_num)
    -- PyMuPDF text extraction
end

function math_pdf_parser.kmeans_quantize(image_array, max_colors)
    -- K-Means quantization
end

function math_pdf_parser.find_math_regions(image_array, assignments, palette)
    -- Connected component analysis
end

function math_pdf_parser.classify_symbol(ocr_text, shape_features)
    -- Math symbol classification
end

function math_pdf_parser.assemble_equation(regions, relationships)
    -- Equation structure assembly
end

function math_pdf_parser.parse(pdf_path, max_pages, dpi)
    -- Full 6-layer pipeline
end
```

**Dependencies:** pymupdf, tesseract, scipy, PIL
**Lua usage:** `math_pdf_parser.parse(pdf, 10, 300)` → structured JSON

---

## 7. vision_math_extractor.py — Vision-Based Extraction

**Purpose:** Vision-based math expression extractor using PyMuPDF + Tesseract.
ChromaNumber-style K-Means for math region identification. Complements
text-based semantic_math_extractor.py.

**Key needs:**
- RGB to hex conversion
- Color quantization (K-Means)
- Text region detection (connected components)
- OCR integration (Tesseract)
- Math region filtering by size/shape

**Lua mapping:**
```lua
local vision_math = {}

function vision_math.rgb_to_hex(r, g, b)
    return string.format("#%02x%02x%02x", r, g, b)
end

function vision_math.kmeans_quantize(image_array, max_colors)
    -- K-Means quantization
end

function vision_math.find_text_regions(image_array, assignments, palette)
    -- Connected component text region detection
end

function vision_math.ocr_region(image, bbox)
    -- Tesseract OCR on region
end
```

**Dependencies:** Tesseract, PIL, numpy
**Lua usage:** `vision_math.kmeans_quantize(img, 16)` → (centroids, labels, palette)

---

## 8. chroma_visual_reader.py — Chroma Visual Reader

**Purpose:** Multi-scale 2D math geometry detector. Extracts physical 2D
structures from PDF pages: fraction bars/vinculums, tall delimiters/cases
braces, paired enclosing delimiters, stacked limit operators, scaled script
tokens. Prevents 1D text readers from flattening 2D structures.

**Key needs:**
- VisualRegion dataclass (bbox, centroid, aspect_ratio, fill_ratio, region_type)
- VisualMathStructure dataclass (structure_type, components, confidence)
- K-Means quantization
- Connected component analysis with shape metadata
- Region classification by aspect ratio/fill ratio
- Structure assembly (fraction: numerator/denominator; cases: branches)
- Confidence scoring

**Lua mapping:**
```lua
local chroma_visual = {}

-- Data structures
chroma_visual.VisualRegion = {
    region_id = 0,
    bbox = {x_min, y_min, w, h},
    centroid = {cx, cy},
    aspect_ratio = 0.0,
    fill_ratio = 0.0,
    normalized_stroke = 0.0,
    region_type = "fraction_bar",  -- fraction_bar, cases_brace, large_bracket, etc.
    is_math = true,
    text = nil,
    children = {}
}

chroma_visual.VisualMathStructure = {
    structure_type = "fraction",  -- fraction, cases, enclosed_group, stacked_limits, matrix
    main_region_id = 0,
    bbox = {x_min, y_min, w, h},
    components = {},  -- {numerator = [...], denominator = [...]}
    confidence = 1.0
}

function chroma_visual.kmeans_quantize(image_array, max_colors)
end

function chroma_visual.find_regions(image_array, assignments, palette)
end

function chroma_visual.classify_region(region)
end

function chroma_visual.assemble_structure(regions)
end
```

**Dependencies:** numpy, PIL, scipy
**Lua usage:** `chroma_visual.assemble_structure(regions)` → VisualMathStructure

---

## 9. alttext_cross_checker.py — AltText Cross-Checker

**Purpose:** Compare MathML tree walk output against arXiv alttext (original
LaTeX). Alttext is ground truth. Detects missing symbols, gap categories.

**Key needs:**
- LaTeX token families: GREEK_CMD, BIG_OPS, BRACKETS, ACCENTS, RELATIONS
- Token extraction from alttext LaTeX
- Token extraction from MathML-derived expr
- Missing token detection (in alttext but absent from expr)
- Gap category classification (greek, bracket, operator, accent, etc.)
- Scope classification (display_numbered, display_unnumbered, inline_context)
- Context role extraction from surrounding prose

**Lua mapping:**
```lua
local alttext_checker = {}

-- Token families
alttext_checker.GREEK_CMD = { ["\\alpha"] = "alpha", ... }
alttext_checker.BIG_OPS = { ["\\sum"] = "Sum", ... }
alttext_checker.BRACKETS = { ["\\left("] = "(", ... }
alttext_checker.ACCENTS = { ["\\hat"] = "hat", ... }
alttext_checker.RELATIONS = { ["\\sim"] = "sim", ... }

function alttext_checker.extract_tokens(latex_string)
    -- Returns recognized math-object tokens
end

function alttext_checker.compare(alttext, expr_tokens)
    -- Returns { missing_from_expr, extra_in_expr, gap_categories }
end

function alttext_checker.classify_scope(html_context)
    -- display_numbered | display_unnumbered | inline_context
end
```

**Dependencies:** Lua pattern matching
**Lua usage:** `alttext_checker.compare(alttext, expr)` → diff dict

---

## 10. math_context_extractor.py — Context Preservation

**Purpose:** Extract math expressions with surrounding context intact.
Uses ChromaNumber-style region detection. Preserves spatial relationships
and page metadata. No solving, no derivation.

**Key needs:**
- K-Means color quantization
- Math region detection (connected components)
- Context preservation (surrounding text)
- Spatial relationship extraction
- Page metadata

**Lua mapping:** (same as chroma_visual + context layer)
```lua
local math_context = {}

function math_context.extract_with_context(pdf_path, page_num)
    -- Returns { math_regions, context_text, spatial_relationships, page_metadata }
end
```

---

## 11. display_equation_extractor.py — Display Equation Extraction

**Purpose:** Extract ONLY complete display equations from arxiv HTML.
Groups by equation group, preserves equation numbers.

**Key needs:**
- HTML parsing (ltx_equationgroup, ltx_eqn_row, ltx_eqn_eqno)
- Body cell vs padding/eqno cell classification
- Multi-line equation group handling
- Equation number extraction

**Lua mapping:**
```lua
local display_eq = {}

function display_eq.extract(html)
    -- Returns list of { group_id, row_index, eqno, nodes, is_multiline_group }
end

function display_eq.is_body_cell(td)
    -- Classify cell as body/padding/eqno
end
```

**Dependencies:** Lua HTML parser (lxp or luasocket)
**Lua usage:** `display_eq.extract(html)` → display equations list

---

## 12. math_symbol_classifier.py — Symbol Classification

**Purpose:** Classify detected math regions by combining OCR text, shape
characteristics, and spatial context. Confidence scores + alternatives.

**Key needs:**
- MATH_SYMBOL_LOOKUP table (Greek, operators, brackets, accents)
- OCR text → symbol identity mapping
- Shape characteristic analysis (aspect ratio, fill ratio, stroke width)
- Confidence scoring
- Alternative interpretation generation

**Lua mapping:**
```lua
local symbol_classifier = {}

symbol_classifier.LOOKUP = {
    ["α"] = { name = "alpha", category = "greek", unicode = "α", latex = "\\alpha" },
    -- ... full table
}

function symbol_classifier.classify(ocr_text, shape_features)
    -- Returns { symbol, confidence, alternatives }
end
```

**Dependencies:** Lua table lookup
**Lua usage:** `symbol_classifier.classify("α", {aspect=1.2, fill=0.8})` → result

---

## 13. extract_math_clean.py — Clean Math Extraction

**Purpose:** Extract clean math expressions from PDFs using PyMuPDF.
Preserves Unicode math symbols. Handles both Unicode math and LaTeX.

**Key needs:**
- UNICODE_MATH_CHARS set
- UNICODE_MATH_PATTERNS (regex for equations, sqrt, integrals, etc.)
- PyMuPDF text extraction with layout preservation
- Math symbol density filtering

**Lua mapping:**
```lua
local extract_clean = {}

extract_clean.UNICODE_MATH_CHARS = { "φ", "ψ", "χ", ... }

function extract_clean.extract(pdf_path, page_num)
    -- Returns list of { type, expression, page, position }
end

function extract_clean.match_patterns(text)
    -- Apply UNICODE_MATH_PATTERNS to text
end
```

**Dependencies:** Lua pattern matching (lpeg recommended)
**Lua usage:** `extract_clean.extract(pdf, 1)` → math expressions

---

## 14. extract_tex_macros.py — TeX Macro Extraction

**Purpose:** Extract macro definitions from arxiv TeX source to resolve
shorthand. Downloads tarball, parses \newcommand and \def.

**Key needs:**
- arXiv e-print URL construction
- Tarball extraction (tarfile)
- \newcommand parsing with brace-matching
- \def parsing
- Macro body extraction

**Lua mapping:**
```lua
local tex_macros = {}

function tex_macros.fetch(arxiv_id, version)
    -- Download tarball from arxiv
end

function tex_macros.extract_macros(tex_content)
    -- Parse \newcommand and \def
    -- Returns { name = { nargs = n, body = "..." } }
end

function tex_macros.resolve_shorthand(latex, macros)
    -- Replace macro calls with bodies
end
```

**Dependencies:** Lua HTTP (luasocket), tar (ltar)
**Lua usage:** `tex_macros.extract_macros(tex)` → macro table

---

## 15. extract_jspace_math.py — J-Space Math Extraction

**Purpose:** Extract Hamiltonian, Gaussian smoothing, broadcast set
functions from J-space widget HTML. Bridge between widget JS and Python.

**Key needs:**
- JavaScript function extraction by brace counting
- Function name matching
- String/escape handling in JS

**Lua mapping:**
```lua
local jspace_math = {}

function jspace_math.extract_function(content, func_name)
    -- Extract full JS function by brace counting
end

function jspace_math.extract_all(content, func_names)
    -- Extract multiple functions
end
```

**Dependencies:** Lua string manipulation
**Lua usage:** `jspace_math.extract_function(html, "computeHamiltonian")` → JS code

---

## 16. math_occurrence_accounting.py — Occurrence Accounting

**Purpose:** Multiset reconciliation of source occurrences with recovery
records. P3 contract: occurrence is identity, not LaTeX.

**Key needs:**
- OccurrenceLedger dataclass (paper_id, version, stage)
- Multiset reconciliation (Counter-based)
- Match verdicts: matched, missing, unexpected, duplicate, ambiguous
- Content type: same, changed, unknown
- Legacy ambiguity classification
- Occurrence key generation (SHA-256)

**Lua mapping:**
```lua
local occurrence = {}

function occurrence.ledger(paper_id, version, stage)
    -- Create occurrence ledger
end

function occurrence.reconcile(source_keys, record_keys)
    -- Multiset reconciliation
    -- Returns { matched, missing, unexpected, duplicate, ambiguous }
end

function occurrence.content_type(source_hash, record_hash)
    -- same | changed | unknown
end
```

**Dependencies:** Lua crypto (sha256), table manipulation
**Lua usage:** `occurrence.reconcile(src_keys, rec_keys)` → verdict counts

---

## Cross-File Dependencies

```
semantic_math_extractor.py
  ├─ mathml_parser.py (MathML tree walk)
  ├─ math_recovery_tool.py (LaTeX recovery)
  ├─ math_contract.py (canonical schema)
  ├─ alttext_cross_checker.py (ground truth comparison)
  └─ visual_math_translator.py (2D structure detection)

math_pdf_parser.py
  ├─ vision_math_extractor.py (vision regions)
  ├─ math_symbol_classifier.py (symbol lookup)
  ├─ chroma_visual_reader.py (2D geometry)
  └─ math_context_extractor.py (context preservation)

extract_math_clean.py
  └─ PyMuPDF (text extraction)

extract_tex_macros.py
  └─ arXiv e-print tarball

math_occurrence_accounting.py
  └─ math_contract.py (occurrence_key, RecoveryRecord)
```

---

## Lua Plugin Architecture

### Module Structure

```
lua-math-tool/
├── init.lua              -- Main entry point, module loader
├── semantic_math.lua     -- Semantic math extraction
├── mathml_parser.lua     -- MathML tree parsing
├── math_recovery.lua     -- Math recovery/translation
├── visual_math.lua       -- Visual math translation
├── math_contract.lua     -- Canonical schema
├── math_pdf_parser.lua   -- PDF parser pipeline
├── vision_math.lua       -- Vision-based extraction
├── chroma_visual.lua     -- Chroma visual reader
├── alttext_checker.lua   -- AltText cross-checker
├── math_context.lua      -- Context preservation
├── display_eq.lua        -- Display equation extraction
├── symbol_classifier.lua -- Symbol classification
├── extract_clean.lua     -- Clean math extraction
├── tex_macros.lua        -- TeX macro extraction
├── jspace_math.lua       -- J-Space math extraction
├── occurrence.lua        -- Occurrence accounting
├── utils/
│   ├── kmeans.lua        -- K-Means quantization
│   ├── connected.lua     -- Connected component analysis
│   ├── brace_scan.lua    -- Balancing brace scanner
│   ├── sha256.lua        -- SHA-256 hashing
│   └── json.lua          -- JSON encode/decode
└── tests/
    ├── test_math_contract.lua
    ├── test_brace_scan.lua
    ├── test_occurrence.lua
    └── test_structural_conservation.lua
```

### Integration Points

1. **King Wen emotional engine:** Math extraction feeds into King Wen state
   space via `shotgun_expand()` — each paper's math becomes a domain vector
   input to the 512-state expansion.

2. **OpenJarvis receptive agent:** Math recovery output feeds into
   `consult()` as context for hexagram consultation.

3. **Megatron training:** Recovered math expressions become training data
   via `build_full_shotgun_jsonl.py` with math_contract occurrence keys.

4. **Voicebox:** Math symbol classification feeds into voice weight vectors
   (voiceWeight, coherence, chaos, whimsy, darkTone).

5. **3D avatar:** Visual math structures (fraction bars, delimiters) feed
   into kit model generation via `enrich_kit_models.py`.

### Verification Pattern

```bash
# Python verification (current)
python -m py_compile scripts/semantic_math_extractor.py
python -m py_compile scripts/mathml_parser.py
python -m py_compile scripts/math_recovery_tool.py
python -m py_compile scripts/math_contract.py
python -m py_compile scripts/math_pdf_parser.py

# Lua verification (future)
luac -p lua-math-tool/init.lua
lua lua-math-tool/tests/test_math_contract.lua
lua lua-math-tool/tests/test_brace_scan.lua
lua lua-math-tool/tests/test_occurrence.lua
```

### King Wen Math Invariants

1. **No silent substitution:** Missing math must raise, not default to Hexagram 1.
2. **Structural conservation:** No MathML structural child may disappear.
3. **Occurrence identity:** SHA-256 over (paper_id, version, locator, index).
4. **Four status dimensions:** Parse, Structural, Backend, Solution — never conflated.
5. **Alttext ground truth:** When MathML and alttext disagree, alttext wins.
6. **Delimiter identity:** langle/rangle, lVert/rVert, lfloor/rfloor, lceil/rceil
   must preserve paired identity.

---

---

## 17. math_notation_mapping.py — Unicode→SymPy/Wolfram Mapping

**Purpose:** Map Unicode math operators and letter-like forms to SymPy-compatible
Python expressions and Wolfram Language StandardForm equivalents.

**Key needs:**
- UNICODE_TO_SYMPY dict (·→*, ×→*, ≤→<=, ∫→Integral, etc.)
- UNICODE_TO_WOLFRAM dict (parallel mapping)
- Bidirectional lookup (unicode → sympy, sympy → unicode)
- Greek letter mapping (α→alpha, Γ→Gamma)
- Operator mapping (sum, prod, integral, limit, etc.)

**Lua mapping:**
```lua
local notation_mapping = {}

notation_mapping.UNICODE_TO_SYMPY = {
    ["·"] = "*", ["×"] = "*", ["≤"] = "<=", ["∫"] = "Integral",
    -- ... full table
}

notation_mapping.UNICODE_TO_WOLFRAM = {
    ["·"] = "Times", ["×"] = "Times", ["≤"] = "LessEqual", ...
}

function notation_mapping.to_sympy(unicode_char)
    return notation_mapping.UNICODE_TO_SYMPY[unicode_char]
end

function notation_mapping.to_wolfram(unicode_char)
    return notation_mapping.UNICODE_TO_WOLFRAM[unicode_char]
end

function notation_mapping.from_sympy(sympy_str)
    -- Reverse lookup
end
```

**Dependencies:** Lua table lookup
**Lua usage:** `notation_mapping.to_sympy("∫")` → "Integral"

---

## 18. math_structure_extractor.py — Structure Extraction

**Purpose:** Extract math expressions with complete structural relationships.
Preserves bracket nesting, fraction structure, sub/superscripts, spatial
relationships. Output: structured math trees with director signals.

**Key needs:**
- K-Means color quantization (shared with other vision modules)
- Math region detection (connected components)
- Structural relationship preservation (bracket nesting, fraction structure)
- Sub/superscript spatial relationship extraction
- Spatial relationship extraction (fraction bars, delimiters)
- Director signals for relationships

**Lua mapping:** (same pattern as chroma_visual + spatial relationship layer)
```lua
local structure_extractor = {}

function structure_extractor.extract(pdf_path, page_num)
    -- Returns { math_trees, relationships, director_signals }
end

function structure_extractor.preserve_brackets(regions)
    -- Bracket nesting preservation
end

function structure_extractor.extract_subsuperscripts(regions)
    -- Sub/superscript spatial relationships
end
```

---

## 19. prose_math_extractor.py — Prose Math Extraction

**Purpose:** Detect math embedded in paragraph text (mid-paragraph math)
and capture surrounding theory text. "Math in relation to words" layer.

**Key needs:**
- HTML parsing (BeautifulSoup or Lua HTML parser)
- Math tag detection (<math> in paragraph context)
- Context before/after extraction
- Section title extraction
- Paragraph text extraction
- Relationship analysis (how math relates to surrounding text)
- Theory keyword extraction
- Display vs inline classification

**Lua mapping:**
```lua
local prose_math = {}

prose_math.ProseMathOccurrence = {
    latex = "",
    recovered_expr = "",
    is_display = false,
    context_before = "",
    context_after = "",
    section_title = "",
    paragraph_text = "",
    occurrence_index = 0,
    math_tag_index = 0,
    relationship = "",
    theory_keywords = {}
}

function prose_math.extract_from_html(html, arxiv_id)
    -- Returns list of ProseMathOccurrence
end

function prose_math.extract_from_corpus(corpus_path)
    -- Extract from saved corpus file
end

function prose_math.analyze_relationship(math, context_before, context_after)
    -- Determine how math relates to surrounding text
end
```

**Dependencies:** Lua HTML parser (lxp or xml2lua)
**Lua usage:** `prose_math.extract_from_html(html, "2605.00155")` → occurrences

---

## 20. structural_ast_extractor.py — Structural AST Extraction

**Purpose:** Walk MathML tree and emit typed recursive ExprNode (contract).
Preserves operator identity, limits as children, differentials, relations,
decorations, fractions/roots, unsupported nodes.

**Key needs:**
- MathML tag → contract node kind mapping (_TAG_KIND)
- Big operator handling (sum/prod/integral with limits as children)
- Limit word handling (lim/limsup/liminf)
- Fraction/numerator/denominator preservation
- Power/subscript preservation
- Square root/radicand preservation
- Matrix row/column preservation
- Unsupported node preservation (never dropped)
- Occurrence identity attribution (root node binding)

**Lua mapping:**
```lua
local structural_ast = {}

structural_ast.TAG_KIND = {
    ["mi"] = "identifier",
    ["mn"] = "number",
    ["mo"] = "operator",
    ["mfrac"] = "fraction",
    ["msup"] = "power",
    ["msub"] = "subscript",
    ["msqrt"] = "sqrt",
    ["mroot"] = "root",
    ["mtable"] = "matrix",
    ["mtext"] = "text",
    ["mrow"] = "group",
}

structural_ast.BIG_OPS = {
    ["∑"] = "sum", ["∏"] = "product", ["∫"] = "integral",
    ["∮"] = "integral", ["∬"] = "integral", ["∭"] = "integral",
}

function structural_ast.extract(mathml_node)
    -- Returns typed ExprNode tree
    -- Unsupported nodes become { kind="unsupported", source_tag=tag, raw_text=text }
end

function structural_ast.preserve_limits(node)
    -- Ensure munder/mover/munderover limits are children, not dropped
end

function structural_ast.preserve_differentials(node)
    -- dx/dy/dz as ordered measure children
end
```

**Dependencies:** Lua XML parser
**Lua usage:** `structural_ast.extract(mathml_node)` → ExprNode tree

---

## 21. math_symbol_vision_hooks.py — Vision Symbol Hooks

**Purpose:** Hooks for vision-based math symbol detection. Bridges
vision_math_extractor and math_symbol_classifier.

**Key needs:**
- Symbol detection hooks (before/after classification)
- Vision pipeline integration points
- Hook registration/unregistration

**Lua mapping:**
```lua
local vision_hooks = {}

vision_hooks.hooks = {}

function vision_hooks.register(hook_name, fn)
    vision_hooks.hooks[hook_name] = fn
end

function vision_hooks.trigger(hook_name, ...)
    if vision_hooks.hooks[hook_name] then
        return vision_hooks.hooks[hook_name](...)
    end
end
```

---

## 22. math_ast_integration.py — AST Integration

**Purpose:** Integration layer that binds occurrence identity to AST trees.
Sets occurrence_key, source_locator, occurrence_index on root node.

**Key needs:**
- Occurrence attribution on root node
- AST persistence with identity
- Integration with math_occurrence_accounting

**Lua mapping:**
```lua
local ast_integration = {}

function ast_integration.bind_occurrence(ast_tree, occurrence_key, source_locator, occurrence_index)
    -- Bind identity to root node
    ast_tree.occurrence_key = occurrence_key
    ast_tree.source_locator = source_locator
    ast_integration.occurrence_index = occurrence_index
    return ast_tree
end
```

---

## 23. e2e_math_pipeline.py — End-to-End Pipeline

**Purpose:** End-to-end math pipeline: fetch arXiv HTML, extract MathML+context,
parse to ExprNode, solve with SymPy, relate via shared symbols.

**Key needs:**
- arXiv HTML fetching
- MathML extraction + context
- ExprNode parsing
- SymPy solving
- Shared symbol relation extraction
- Occurrence conservation gate

**Lua mapping:**
```lua
local e2e_pipeline = {}

function e2e_pipeline.run(arxiv_id, version)
    -- Full pipeline: fetch → extract → parse → solve → relate
    -- Returns { equations, solutions, relations, occurrence_conservation }
end

function e2e_pipeline.conservation_gate(source_keys, trace_keys)
    -- Assert source_keys == trace_keys
end
```

---

## 24. math_checkerboard.py — Checkerboard Pattern

**Purpose:** Checkerboard pattern for math validation. Tests alternating
correct/incorrect recovery across corpus.

**Key needs:**
- Checkerboard pattern generation
- Validation against alternating expected outcomes

**Lua mapping:**
```lua
local checkerboard = {}

function checkerboard.generate(n)
    -- Generate checkerboard pattern of size n
end

function checkerboard.validate(results, pattern)
    -- Validate results against checkerboard pattern
end
```

---

## 25. math_constraint_validator.py — Constraint Validation

**Purpose:** Validate math expressions against constraints (dimensional
analysis, type checking, domain constraints).

**Key needs:**
- Dimensional analysis
- Type checking (scalar, vector, matrix)
- Domain constraint validation
- Expression equivalence checking

**Lua mapping:**
```lua
local constraint_validator = {}

function constraint_validator.validate(expr, constraints)
    -- Returns { valid, violations }
end

function constraint_validator.check_dimensions(expr)
    -- Dimensional analysis
end
```

---

## 26. math_failure_corpus.py — Failure Corpus

**Purpose:** Write failure corpus JSONL with occurrence identity, crash info,
unknown commands, notes. One record per failing equation.

**Key needs:**
- Failure record creation (paper_id, index, is_display, state, latex, recovered, crash, unknown, notes, structure, max_brace_depth)
- JSONL output
- Summary statistics

**Lua mapping:**
```lua
local failure_corpus = {}

function failure_corpus.write(record, output_path)
    -- Append failure record to JSONL
end

function failure_corpus.summarize(records)
    -- Generate summary statistics
end
```

---

## 27. math_failure_taxonomy.py — Failure Taxonomy

**Purpose:** Classify failure types: NO_EQUATION, MULTI_EQUATION, EMPTY,
UNKNOWN_COMMAND, BACKSLASH_LEFT, RECOVERABLE, SOLVABLE.

**Key needs:**
- Failure type classification
- Taxonomy hierarchy
- Count aggregation per type

**Lua mapping:**
```lua
local failure_taxonomy = {}

failure_taxonomy.TYPES = {
    "NO_EQUATION", "MULTI_EQUATION", "EMPTY",
    "UNKNOWN_COMMAND", "BACKSLASH_LEFT", "RECOVERABLE", "SOLVABLE"
}

function failure_taxonomy.classify(record)
    -- Returns failure type string
end
```

---

## 28. math_nesting_proof.py — Nesting Proof

**Purpose:** Prove nesting depth preservation in math recovery.
Tests that nested structures (frac within frac, sum within integral) preserve depth.

**Key needs:**
- Nesting depth calculation
- Depth preservation verification
- Test cases for nested structures

**Lua mapping:**
```lua
local nesting_proof = {}

function nesting_proof.depth(expr)
    -- Calculate nesting depth of expression
end

function nesting_proof.verify(source, recovered)
    -- Verify depth preservation
end
```

---

## 29. math_occurrence_accounting.py — Occurrence Accounting

**Purpose:** Multiset reconciliation of source occurrences with recovery
records. P3 contract: occurrence is identity, not LaTeX.

**Key needs:**
- OccurrenceLedger (paper_id, version, stage)
- Multiset reconciliation (Counter-based)
- Match verdicts: matched, missing, unexpected, duplicate, ambiguous
- Content type: same, changed, unknown
- Legacy ambiguity classification
- Occurrence key generation (SHA-256)

**Lua mapping:**
```lua
local occurrence = {}

function occurrence.ledger(paper_id, version, stage)
    -- Create occurrence ledger
end

function occurrence.reconcile(source_keys, record_keys)
    -- Multiset reconciliation
    -- Returns { matched, missing, unexpected, duplicate, ambiguous }
end

function occurrence.content_type(source_hash, record_hash)
    -- same | changed | unknown
end

function occurrence.key(paper_id, version, locator, index)
    -- SHA-256 occurrence key
end
```

**Dependencies:** Lua crypto (sha256)
**Lua usage:** `occurrence.reconcile(src_keys, rec_keys)` → verdict counts

---

## 30. math_regression_hunt.py — Regression Hunt

**Purpose:** Hunt for regressions between two recovery runs. Diff lost/gained
solvable equations.

**Key needs:**
- Run comparison (before/after)
- Lost/gained solvable detection
- Regression classification

**Lua mapping:**
```lua
local regression_hunt = {}

function regression_hunt.compare(run_before, run_after)
    -- Returns { lost, gained, unchanged }
end
```

---

## 31. math_tag_leak_test.py — Tag Leak Test

**Purpose:** Test for tag leakage in math extraction. Ensures HTML tags
don't leak into recovered expressions.

**Key needs:**
- Tag detection in recovered expressions
- Leak classification
- Test case generation

**Lua mapping:**
```lua
local tag_leak = {}

function tag_leak.detect(expr)
    -- Returns list of leaked tags
end

function tag_leak.test(exprs)
    -- Test batch for tag leaks
end
```

---

## 32. math_unknown_inventory.py — Unknown Inventory

**Purpose:** Inventory unknown commands/operators in math recovery.
Classifies unknown by type and frequency.

**Key needs:**
- Unknown command detection
- Frequency counting
- Type classification

**Lua mapping:**
```lua
local unknown_inventory = {}

function unknown_inventory.scan(exprs)
    -- Returns { command = count }
end

function unknown_inventory.classify(command)
    -- Returns type: greek, operator, bracket, accent, etc.
end
```

---

## 33. math_chrome_contamination_test.py — Chrome Contamination Test

**Purpose:** Test for Chrome browser contamination in math extraction.
Ensures page numbers, figure numbers, etc. don't leak into math.

**Key needs:**
- Chrome signature detection (page, figure, table, section, arxiv, preprint, doi, copyright, sidebar)
- Contamination classification
- Test case generation

**Lua mapping:**
```lua
local chrome_test = {}

function chrome_test.detect(expr)
    -- Returns list of chrome signatures found
end

function chrome_test.is_contaminated(expr)
    -- Boolean: is expression contaminated?
end
```

---

## 34. math_corruption_test.py — Corruption Test

**Purpose:** Test for corruption in math recovery. Detects silent
corruption (wrong math that parses successfully).

**Key needs:**
- Corruption detection (structural mismatch)
- Silent corruption identification
- Test case generation

**Lua mapping:**
```lua
local corruption_test = {}

function corruption_test.detect(source, recovered)
    -- Returns { corrupted, reason }
end
```

---

## 35. bridge_math_diagram_extractor.py — Diagram Extractor Bridge

**Purpose:** Bridge between math diagram extractor and King Wen pipeline.
Extracts diagrams from PDFs and converts to King Wen domain vectors.

**Key needs:**
- Diagram extraction from PDF
- Domain vector conversion
- King Wen state injection

**Lua mapping:**
```lua
local diagram_bridge = {}

function diagram_bridge.extract(pdf_path)
    -- Extract diagrams → domain vectors
end

function diagram_bridge.to_kingwen(domain_vectors)
    -- Convert to King Wen state
end
```

---

## 36. multi_engine_parser.py — Multi-Engine Parser

**Purpose:** Stack multiple PDF parsing engines (PyMuPDF, Tesseract, etc.)
for math extraction. Engine comparison and voting.

**Key needs:**
- Engine registration
- Multi-engine parsing
- Result voting/consensus
- Engine performance comparison

**Lua mapping:**
```lua
local multi_engine = {}

function multi_engine.parse(pdf_path, engines)
    -- Parse with multiple engines
    -- Returns { engine = result }
end

function multi_engine.vote(results)
    -- Vote on best result
end
```

---

## 37. verify_math_jacobian_hamiltonian.py — Jacobian/Hamiltonian Verification

**Purpose:** Verify math extraction against Jacobian/Hamiltonian formalism.
Tests structural fidelity of recovered math.

**Key needs:**
- Jacobian computation verification
- Hamiltonian energy verification
- Structural fidelity testing

**Lua mapping:**
```lua
local jacobian_verify = {}

function jacobian_verify.check(expr)
    -- Verify Jacobian structure
end

function jacobian_verify.hamiltonian(expr)
    -- Verify Hamiltonian structure
end
```

---

## 38. arxiv_html_parser.py — ArXiv HTML Parser

**Purpose:** Parse arXiv HTML pages. Extract MathML equations, x-tex
annotations, display equations, inline equations.

**Key needs:**
- HTML fetching (arxiv.org/html/{id})
- MathML extraction
- x-tex annotation extraction
- Display/inline classification
- Equation numbering
- Section context extraction

**Lua mapping:**
```lua
local arxiv_html = {}

function arxiv_html.fetch(arxiv_id, version)
    -- Fetch HTML from arxiv
end

function arxiv_html.extract_math(html)
    -- Extract all math (display + inline)
end

function arxiv_html.extract_display(html)
    -- Extract display equations only
end

function arxiv_html.extract_annotations(html)
    -- Extract x-tex annotations
end
```

**Dependencies:** Lua HTTP (luasocket), HTML parser (lxp)
**Lua usage:** `arxiv_html.extract_math(html)` → equations list

---

## 39. math_ast_integration.py — AST Integration

**Purpose:** Integration layer binding occurrence identity to AST trees.

**Key needs:**
- Occurrence attribution on root node
- AST persistence with identity
- Integration with occurrence accounting

**Lua mapping:**
```lua
local ast_integration = {}

function ast_integration.bind(ast_tree, occurrence_key, source_locator, occurrence_index)
    ast_tree.occurrence_key = occurrence_key
    ast_tree.source_locator = source_locator
    ast_tree.occurrence_index = occurrence_index
    return ast_tree
end
```

---

## 40. e2e_math_pipeline.py — End-to-End Pipeline

**Purpose:** Full pipeline: fetch arXiv HTML, extract MathML+context,
parse to ExprNode, solve with SymPy, relate via shared symbols.

**Key needs:**
- arXiv HTML fetching
- MathML extraction + context
- ExprNode parsing
- SymPy solving
- Shared symbol relation extraction
- Occurrence conservation gate

**Lua mapping:**
```lua
local e2e_pipeline = {}

function e2e_pipeline.run(arxiv_id, version)
    -- Full pipeline
end

function e2e_pipeline.conservation_gate(source_keys, trace_keys)
    -- Assert source_keys == trace_keys
end
```

---

## 41. mathml_parser.py — MathML Parser (already listed #2, expanded)

**Additional needs from corpus analysis:**
- Annotation capture bug fix: second loop appends source='annotation' without dedup
- Equation count = len(equations) after merging both sources
- Raw HTML <math> tags vs parsed corpus equation_count must match

**Lua mapping (additional):**
```lua
-- Fix: merge annotation sources into equations list
function mathml_parser.merge_annotations(equations, annotations)
    for _, ann in ipairs(annotations) do
        -- Dedup by position
        table.insert(equations, ann)
    end
    return equations
end
```

---

## Appendix: Complete File Inventory (Math/Extraction/Vision/Debugging)

| # | File | Lines | Purpose | Lua Target |
|---|------|-------|---------|------------|
| 1 | semantic_math_extractor.py | 4368 | Core math extraction | semantic_math.lua |
| 2 | mathml_parser.py | 504 | MathML tree parsing | mathml_parser.lua |
| 3 | math_recovery_tool.py | ~400 | Math recovery/translation | math_recovery.lua |
| 4 | visual_math_translator.py | 337 | Visual math translation | visual_math.lua |
| 5 | math_contract.py | 504 | Canonical schema | math_contract.lua |
| 6 | math_pdf_parser.py | 840 | PDF parser pipeline | math_pdf_parser.lua |
| 7 | vision_math_extractor.py | 337 | Vision-based extraction | vision_math.lua |
| 8 | chroma_visual_reader.py | 610 | Chroma visual reader | chroma_visual.lua |
| 9 | alttext_cross_checker.py | 340 | AltText cross-checker | alttext_checker.lua |
| 10 | math_context_extractor.py | 380 | Context preservation | math_context.lua |
| 11 | display_equation_extractor.py | 253 | Display equation extraction | display_eq.lua |
| 12 | math_symbol_classifier.py | 589 | Symbol classification | symbol_classifier.lua |
| 13 | extract_math_clean.py | 329 | Clean math extraction | extract_clean.lua |
| 14 | extract_tex_macros.py | 84 | TeX macro extraction | tex_macros.lua |
| 15 | extract_jspace_math.py | 58 | J-Space math extraction | jspace_math.lua |
| 16 | math_occurrence_accounting.py | 531 | Occurrence accounting | occurrence.lua |
| 17 | math_notation_mapping.py | 369 | Unicode→SymPy/Wolfram | notation_mapping.lua |
| 18 | math_structure_extractor.py | 369 | Structure extraction | structure_extractor.lua |
| 19 | prose_math_extractor.py | 337 | Prose math extraction | prose_math.lua |
| 20 | structural_ast_extractor.py | 521 | Structural AST extraction | structural_ast.lua |
| 21 | math_symbol_vision_hooks.py | ~100 | Vision symbol hooks | vision_hooks.lua |
| 22 | math_ast_integration.py | ~100 | AST integration | ast_integration.lua |
| 23 | e2e_math_pipeline.py | ~200 | End-to-end pipeline | e2e_pipeline.lua |
| 24 | math_checkerboard.py | ~100 | Checkerboard pattern | checkerboard.lua |
| 25 | math_constraint_validator.py | ~100 | Constraint validation | constraint_validator.lua |
| 26 | math_failure_corpus.py | ~150 | Failure corpus | failure_corpus.lua |
| 27 | math_failure_taxonomy.py | ~100 | Failure taxonomy | failure_taxonomy.lua |
| 28 | math_nesting_proof.py | ~100 | Nesting proof | nesting_proof.lua |
| 29 | math_regression_hunt.py | ~150 | Regression hunt | regression_hunt.lua |
| 30 | math_tag_leak_test.py | ~100 | Tag leak test | tag_leak.lua |
| 31 | math_unknown_inventory.py | ~100 | Unknown inventory | unknown_inventory.lua |
| 32 | math_chrome_contamination_test.py | ~100 | Chrome contamination test | chrome_test.lua |
| 33 | math_corruption_test.py | ~100 | Corruption test | corruption_test.lua |
| 34 | bridge_math_diagram_extractor.py | ~100 | Diagram extractor bridge | diagram_bridge.lua |
| 35 | multi_engine_parser.py | ~200 | Multi-engine parser | multi_engine.lua |
| 36 | verify_math_jacobian_hamiltonian.py | ~100 | Jacobian/Hamiltonian verify | jacobian_verify.lua |
| 37 | arxiv_html_parser.py | ~300 | ArXiv HTML parser | arxiv_html.lua |
| 38 | math_context_extractor.py | 380 | Context preservation | math_context.lua |

---

## Status

- [x] File inventory complete (38 files)
- [x] Cross-examination of all math/extraction/vision/debugging files
- [x] Lua mapping for each file
- [ ] Lua plugin implementation (pending)
- [ ] Lua verification suite (pending)
- [ ] King Wen integration (pending)
- [ ] Megatron training data generation (pending)

---

## King Wen Math Invariants (Lua Plugin)

1. **No silent substitution:** Missing math must raise, not default to Hexagram 1.
2. **Structural conservation:** No MathML structural child may disappear.
3. **Occurrence identity:** SHA-256 over (paper_id, version, locator, index).
4. **Four status dimensions:** Parse, Structural, Backend, Solution — never conflated.
5. **Alttext ground truth:** When MathML and alttext disagree, alttext wins.
6. **Delimiter identity:** langle/rangle, lVert/rVert, lfloor/rfloor, lceil/rceil
   must preserve paired identity.
7. **Annotation capture:** Merge annotation sources into equations list with dedup.
8. **Equation count:** len(equations) after merging both MathML and annotation sources.
9. **Structural AST:** Unsupported nodes preserved as { kind="unsupported", source_tag, raw_text }.
10. **Occurrence conservation:** source_keys == trace_keys (multiset, not set).

---

## Lua Plugin Entry Point

```lua
-- lua-math-tool/init.lua
local math_tool = {}

math_tool.semantic_math = require("lua-math-tool.semantic_math")
math_tool.mathml_parser = require("lua-math-tool.mathml_parser")
math_tool.math_recovery = require("lua-math-tool.math_recovery")
math_tool.visual_math = require("lua-math-tool.visual_math")
math_tool.math_contract = require("lua-math-tool.math_contract")
math_tool.math_pdf_parser = require("lua-math-tool.math_pdf_parser")
math_tool.vision_math = require("lua-math-tool.vision_math")
math_tool.chroma_visual = require("lua-math-tool.chroma_visual")
math_tool.alttext_checker = require("lua-math-tool.alttext_checker")
math_tool.math_context = require("lua-math-tool.math_context")
math_tool.display_eq = require("lua-math-tool.display_eq")
math_tool.symbol_classifier = require("lua-math-tool.symbol_classifier")
math_tool.extract_clean = require("lua-math-tool.extract_clean")
math_tool.tex_macros = require("lua-math-tool.tex_macros")
math_tool.jspace_math = require("lua-math-tool.jspace_math")
math_tool.occurrence = require("lua-math-tool.occurrence")
math_tool.notation_mapping = require("lua-math-tool.notation_mapping")
math_tool.structure_extractor = require("lua-math-tool.structure_extractor")
math_tool.prose_math = require("lua-math-tool.prose_math")
math_tool.structural_ast = require("lua-math-tool.structural_ast")

return math_tool
```

---

## Notes

- All files are in `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\scripts/`
- No edits were made to `C:\ProgramData\Jagex` (read-only constraint honored)
- Lua plugin is a mapping/design document; implementation is pending
- Each Lua module maps 1:1 to a Python script
- Verification pattern: `luac -p` + `lua tests/test_*.lua`

| File | Lines | Purpose | Lua Target |
|------|-------|---------|------------|
| semantic_math_extractor.py | 4368 | Core math extraction | semantic_math.lua |
| mathml_parser.py | 504 | MathML tree parsing | mathml_parser.lua |
| math_recovery_tool.py | ~400 | Math recovery/translation | math_recovery.lua |
| visual_math_translator.py | 337 | Visual math translation | visual_math.lua |
| math_contract.py | 504 | Canonical schema | math_contract.lua |
| math_pdf_parser.py | 840 | PDF parser pipeline | math_pdf_parser.lua |
| vision_math_extractor.py | 337 | Vision-based extraction | vision_math.lua |
| chroma_visual_reader.py | 610 | Chroma visual reader | chroma_visual.lua |
| alttext_cross_checker.py | 340 | AltText cross-checker | alttext_checker.lua |
| math_context_extractor.py | 380 | Context preservation | math_context.lua |
| display_equation_extractor.py | 253 | Display equation extraction | display_eq.lua |
| math_symbol_classifier.py | 589 | Symbol classification | symbol_classifier.lua |
| extract_math_clean.py | 329 | Clean math extraction | extract_clean.lua |
| extract_tex_macros.py | 84 | TeX macro extraction | tex_macros.lua |
| extract_jspace_math.py | 58 | J-Space math extraction | jspace_math.lua |
| math_occurrence_accounting.py | 531 | Occurrence accounting | occurrence.lua |

---

## Status

- [x] File inventory complete
- [x] Cross-examination of 16 key files
- [ ] Lua plugin implementation (pending)
- [ ] Lua verification suite (pending)
- [ ] King Wen integration (pending)
- [ ] Megatron training data generation (pending)
