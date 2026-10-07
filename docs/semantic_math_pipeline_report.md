# Semantic Math Extraction & Solving Pipeline — Final Report

## Summary

Built a complete pipeline that:
1. Extracts math expressions from 245 PDFs (Zotero corpus)
2. Maps Unicode math notation to Wolfram Language StandardForm
3. Attempts to solve extracted equations with SymPy

## Results

| Metric | Value |
|--------|-------|
| Papers processed | 245 |
| Math expressions extracted | 4,218 |
| Proof chain elements | 183,017 |
| Math images detected | 8,598 |
| Equations solved by SymPy | 1 |
| Expressions skipped (prose/complex) | 2,677 |
| Parse errors | 1,540 |

## Key Files

| File | Purpose |
|------|---------|
| `scripts/semantic_math_extractor.py` | PDF → JSON extraction (PyMuPDF) |
| `scripts/math_notation_mapping.py` | Unicode → SymPy/Wolfram mapping |
| `scripts/solve_all.py` | SymPy equation solver |
| `docs/wolfram_notation_reference.md` | Wolfram notation reference |
| `DATASETS/semantic_math_zotero_full.json` | Full extraction output (159MB) |
| `DATASETS/solved_equations.json` | Solved equations output |

## Wolfram Language Notation Mapping

Created comprehensive mapping from Unicode math symbols to:
- **SymPy operators** (for solving): `·`→`*`, `≤`→`<=`, `≠`→`!=`, etc.
- **Wolfram StandardForm** (for reference): `π`→`Pi`, `∞`→`Infinity`, `∑`→`Sum`, etc.
- **Escape aliases** (for keyboard entry): `Esc p Esc`→`\[Pi]`, `Esc inf Esc`→`\[Infinity]`, etc.

## Limitation: PDF Text Extraction Quality

The fundamental bottleneck is that PyMuPDF extracts **rendered glyphs**, not LaTeX source. This means:

1. **LaTeX commands appear as literal text**: `\frac`, `\sqrt`, `\mathbf` are captured as text, not rendered math
2. **Unicode equations are fragmented**: `α∈A fα(x) and fα(x) is convex in x for every α` is captured as prose, not a clean equation
3. **Most expressions are not solvable equations**: Of 4,218 extracted expressions, only 1 was a clean, single-variable equation that SymPy could solve

### Expression Type Breakdown

| Type | Count | Example |
|------|-------|---------|
| function_call | 870 | `log(1 −D(G(z)))` |
| unicode_equation | 3,138 | `αi = ϵ σ²` |
| latex_inline | 33 | `2\cdot15\cdot n=30n` |
| latex_display | 2 | (complex display equations) |

### Why So Few Solvable

- **Function calls** (870): Not equations — they're function applications like `log(D(x))`
- **Unicode equations** (3,138): Mostly prose with math symbols, not clean equations
- **LaTeX inline** (33): Only 1 was a simple linear equation (`αi = ϵ σ²`)
- **LaTeX display** (2): Too complex for simple string substitution

## Wolfram Language Integration

The notation mapping enables:
1. **Normalization**: Convert Unicode math to SymPy-compatible Python
2. **Reference**: Map to Wolfram StandardForm for documentation
3. **Keyboard entry**: Use Esc aliases for interactive input

### Example Mappings

| Unicode | SymPy | Wolfram | Esc Alias |
|---------|-------|---------|-----------|
| `π` | `pi` | `Pi` | `Esc p Esc` |
| `∞` | `oo` | `Infinity` | `Esc inf Esc` |
| `α` | `alpha` | `Alpha` | `Esc alpha Esc` |
| `∑` | `Sum` | `Sum` | `Esc sum Esc` |
| `∫` | `Integral` | `Integral` | `Esc int Esc` |
| `∂` | `diff` | `DifferentialD` | `Esc dd Esc` |
| `∈` | `in` | `Element` | `Esc elem Esc` |
| `≤` | `<=` | `LessEqual` | `Esc le Esc` |
| `≠` | `!=` | `Unequal` | `Esc ne Esc` |

## Recommendations

1. **For better equation solving**: Use OCR (Tesseract) on math images (8,598 detected) to extract clean LaTeX
2. **For LaTeX source**: Download arXiv LaTeX source instead of PDFs when available
3. **For complex equations**: Use a dedicated LaTeX parser (e.g., `pylatexenc`, `latex2sympy2`)
4. **For Wolfram integration**: The notation mapping is ready for Wolfram Language API calls

## Verification

- `python3 -m py_compile scripts/semantic_math_extractor.py` → OK
- `python3 -m py_compile scripts/math_notation_mapping.py` → OK
- `python3 -m py_compile scripts/solve_all.py` → OK
- `python3 scripts/math_notation_mapping.py` → All mappings verified
- `python3 scripts/solve_all.py` → Completed, results written to `DATASETS/solved_equations.json`