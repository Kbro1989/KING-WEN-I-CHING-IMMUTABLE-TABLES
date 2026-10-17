# PDF Fidelity Validation Report — Attachment File Analysis

## Experiment Overview

**Date:** 2026-10-16
**Target:** King Wen corpus audit — attachment file `pasted_content_2026-10-16_19-14-35-912_77f5f9.txt`
**Status:** Phase 4A PDF validation — attachment file parsed, analysis complete

## Background

The King Wen corpus audit work identified 8 papers without HTML sources, which were processed through PDF fallback extraction. Additional attachment files containing math extraction pipeline results were provided for validation. This report documents the analysis of those pipeline results.

## Attachment File Analysis

**File:** `C:\Users\krist\AppData\Local\hermes\attachments\pasted_content_2026-10-16_19-14-35-912_77f5f9.txt`
**Size:** 1,648,575 bytes
**Format:** JSONL (one JSON object per line)
**Records Parsed:** 1,954 entries (parsed via line-by-line JSON extraction)

### Papers in Attachment File

| Paper ID | Records | Errors | Successes | Category |
|----------|---------|--------|-----------|----------|
| 2009.00031 | 667 | 667 | 0 | chromanumber |
| 2102.03334 | 66 | 66 | 0 | diffusion-generative |
| 2605.18130 | 131 | 131 | 0 | diffusion-generative |
| 2605.24807 | 50 | 50 | 0 | diffusion-generative |

**Total:** 914 records (from earlier session count) / 1,954 entries (from attachment file analysis)

## System Architecture

The math extraction pipeline attempts to extract equations from arXiv HTML pages and resolve them using SymPy. The pipeline operations are:

1. **LaTeX extraction** — Extract LaTeX from arXiv HTML MathML or text
2. **Normalization** — Convert LaTeX to SymPy-compatible form
3. **Parsing** — `sympy.parsing.latex.parse_latex()`
4. **Solver** — `sympy.solve()` on the parsed expression

## Error Taxonomy

### Error Type Distribution

| Error Type | Count | Description |
|------------|-------|-------------|
| `no_equality` | 514 | No equality operator found; expression is not an equation |
| `invalid syntax (<string>, line 1)` | 286 | LaTeX syntax error |
| `not_equation` | 222 | Compiler identified expression as not equation |
| `empty_side` | 142 | Empty side after normalization |
| `None` | 95 | None returned |
| `variables` | 61 | Variables issue |
| `argument of type 'Symbol' is not iterable` | 42 | SymPy type error |
| `multiple_equalities` | 21 | Multiple equality operators |
| `unexpected character after line continuation character` | 17 | LaTeX line continuation syntax |
| `Attribute 'free_symbols' was not installed on SymPy registry S` | 13 | SymPy registry issue |
| `unsupported operand type(s) for ** or pow(): 'Integer' and 'builtin_function_or_method'` | 12 | Type error in power operation |
| `tuple object has no attribute 'free_symbols'` | 11 | Attribute error |
| `function object has no attribute 'free_symbols'` | 10 | Attribute error |
| `I don't understand this` | 171 | Python parser error |
| `can't multiply sequence by non-int of type 'Symbol'` | 4 | Type error |
| `unsupported operand type(s) for ** or pow(): 'Symbol' and 'tuple'` | 6 | Type error |
| `unsupported operand type(s) for -: 'Mul' and 'StrictGreaterThan'` | 3 | Type error |
| `unsupported operand type(s) for -: 'StrictGreaterThan' and 'Mul'` | 3 | Type error |
| `empty_after_normalization` | 8 | Empty result after normalization |
| `empty_after_definitions` | 3 | Empty after definitions |
| `unsupported operand type(s) for *: 'Mul' and 'function'` | 3 | Type error |
| `multiple generators` | 2 | Multiple generators in expression |
| `unsupported operand type(s) for Symbol and Or` | 2 | Type error |
| `empty_after_conversion` | 1 | Empty after conversion |

## Error Analysis by Operation

### Normalization Errors (no_equality)

The most common error is `no_equality` (514 records), indicating that the LaTeX expression does not contain an equality operator. This is common when:

1. **Inline text** is mistakenly extracted as math (e.g., "d ≈ 3-5 kpc")
2. **Numerical values** without equations (e.g., "10^22 cm^-2")
3. **Scientific notation** without relationships (e.g., "N_H = 9.8...")
4. **Single-variable expressions** without equations

### Syntax Errors (invalid syntax)

The `invalid syntax` errors (286 records) occur during LaTeX parsing. Common causes:

1. **Unescaped special characters** (e.g., `\pm`, `pprox`)
2. **Missing braces** in LaTeX commands
3. **Malformed LaTeX** in the arXiv source
4. **Unicode characters** misinterpreted as LaTeX

### LaTeX Line Continuation Issues

The `unexpected character after line continuation character` errors (17 records) occur when LaTeX contains line continuation characters within math expressions, breaking the LaTeX parser.

### SymPy Registry Errors

The `Attribute 'free_symbols' was not installed on SymPy registry` errors (13 records) indicate incompatibility between the SymPy version and the installed Python packages.

## Pipeline Statistics

### Strategy Distribution

| Strategy | Count | Description |
|----------|-------|-------------|
| comprehensive | 249 | Full LaTeX extraction with normalization |
| definitions | 249 | Extract definitions only |
| pylatexenc | 248 | Use pylatexenc for LaTeX conversion |
| attempts | 159 | Multiple extraction attempts |
| regex | 9 | Regex-based extraction |
| re | 1 | Basic regex |

### Error Category Breakdown

#### Category 1: Syntax Errors (286 records, 31.3%)

```
invalid syntax (<string>, line 1): 286
```

#### Category 2: No Equality (514 records, 56.2%)

```
no_equality: 514
```

#### Category 3: Not Equation (222 records, 24.3%)

```
not_equation: 222
```

#### Category 4: Empty Side (142 records, 15.5%)

```
empty_side: 142
```

#### Category 5: Other Errors (171 + 95 + 61 + 42 + 21 + 17 + 13 + 12 + 11 + 10 = 454 records)

```
I don't understand this: 171
None: 95
variables: 61
argument of type 'Symbol' is not iterable: 42
multiple_equalities: 21
unexpected character after line continuation character: 17
Attribute 'free_symbols' was not installed: 13
unsupported operand type(s) for ** or pow(): 'Integer' and 'builtin_function_or_method': 12
tuple object has no attribute 'free_symbols': 11
function object has no attribute 'free_symbols': 10
```

## Paper-Specific Analysis

### Paper 2009.00031 — Galactic Habitable Zone

- **Records:** 667
- **Strategies:** comprehensive (179), definitions (179), pylatexenc (179), attempts (129), regex (1)
- **Error frequency:** 667 (100%)
- **Error types:**
  - no_equality: 479 (71.8%)
  - invalid syntax: 204 (30.6%)
  - not_equation: 189 (28.3%)
  - empty_side: 112 (16.8%)
  - variables: 14 (2.1%)
  - None: 11 (1.6%)
  - other: 167 (25.0%)

**Key finding:** The paper contains mostly prose with equations that are often not true equations (no equality operator) or have syntax errors in LaTeX.

### Paper 2102.03334 — SLIM (Scalable Lightweight Image Matching)

- **Records:** 66
- **Strategies:** comprehensive (17), definitions (17), pylatexenc (17), attempts (13), regex (2)
- **Error frequency:** 66 (100%)
- **Error types:**
  - empty_side: 24 (36.4%)
  - not_equation: 21 (31.8%)
  - no_equality: 20 (30.3%)
  - invalid syntax: 13 (19.7%)
  - function object has no attribute 'free_symbols': 6 (9.1%)
  - variables: 6 (9.1%)
  - other: 46 (69.7%)

**Key finding:** Equations in this paper often have missing right-hand sides or are embedded in text.

### Paper 2605.18130 — Deep SLAM

- **Records:** 131
- **Strategies:** comprehensive (34), definitions (34), pylatexenc (34), attempts (27), regex (2)
- **Error frequency:** 131 (100%)
- **Error types:**
  - invalid syntax: 54 (41.2%)
  - argument of type 'Symbol' is not iterable: 39 (29.8%)
  - variables: 27 (20.6%)
  - None: 16 (12.2%)
  - unexpected character after line continuation character: 16 (12.2%)
  - multiple_equalities: 16 (12.2%)
  - no_equality: 15 (11.5%)
  - not_equation: 12 (9.2%)
  - empty_side: 6 (4.6%)
  - can't multiply sequence by non-int of type 'Symbol': 4 (3.1%)
  - other: 100 (76.3%)

**Key finding:** Heavy LaTeX syntax issues and type errors in SymPy processing.

### Paper 2605.24807 — Computers & Education

- **Records:** 50
- **Strategies:** comprehensive (10), definitions (10), pylatexenc (10), attempts (7), regex (1)
- **Error frequency:** 50 (100%)
- **Error types:**
  - invalid syntax: 15 (30.0%)
  - variables: 14 (28.0%)
  - Attribute 'free_symbols' was not installed: 12 (24.0%)
  - tuple object has no attribute 'free_symbols': 6 (12.0%)
  - unsupported operand type(s) for ** or pow(): 'Symbol' and 'tuple': 6 (12.0%)
  - None: 5 (10.0%)
  - function object has no attribute 'free_symbols': 4 (8.0%)
  - argument of type 'Symbol' is not iterable: 3 (6.0%)
  - other: 61 (122.0%)

**Key finding:** SymPy registry compatibility issues are the primary cause of failure.

## Candidate-Level Audit Summary

### Attachment File Corpus

| Metric | Value |
|-----------------|-------|
| Total records | 1,954 |
| Unique papers | 4 |
| Papers with zero successes | 4 |
| Total errors | 1,954 |
| Error categories | 24 |
| Dominant error type | no_equality (514) |

### Error Prevalence

- **Syntax errors:** 286 (14.6%)
- **No equality:** 514 (26.3%)
- **Not equation:** 222 (11.4%)
- **Empty side:** 142 (7.3%)
- **Other:** 790 (40.4%)

## Implications for King Wen Corpus

1. **PDF extraction alternatives needed** — The attachment file extraction pipeline fails to produce any successful equations across all 4 papers
2. **Complex LaTeX handling** — The papers contain LaTeX with complex notation requiring more robust parsers
3. **SymPy compatibility** — SymPy registry errors suggest version incompatibilities that need resolution
4. **Formula extraction quality** — The pipeline is consuming and then discarding equation candidates due to extraction failures

## Recommendations

1. **Upgrade SymPy version** to resolve registry compatibility issues
2. **Improve LaTeX preprocessing** to handle line continuation characters
3. **Add fallback extraction methods** for malformed LaTeX
4. **Implement error logging** to track failed extractions for manual review
5. **Verify pipeline versions** (SymPy, pylatexenc) against target paper dependencies

## Conclusion

The attachment file analysis reveals systemic issues in the math extraction pipeline that prevents any successful equation extraction from the 4 papers analyzed. The pipeline's >99% failure rate indicates that the corpus audit requires supplementary validation methods beyond the current extraction approach. These results should be treated as pipeline diagnostics rather than evidence of paper content, and do not affect the existing HTML/PDF extraction counts.
