# Appendix: Attachment File Analysis — Math Extraction Pipeline Results

## File Overview

| Field | Value |
|-------|-------|
| File name | `pasted_content_2026-10-16_19-14-35-912_77f5f9.txt` |
| File size | 1,648,575 bytes |
| Lines | 3,541 |
| JSON entries | 1,954 |

## Pipeline Architecture

The attachment file contains results from a math extraction pipeline that:
1. Fetches arXiv HTML pages
2. Extracts LaTeX from MathML elements
3. Normalizes LaTeX using several strategies
4. Parses with SymPy `parse_latex()`
5. Attempts to solve equations with `sympy.solve()`

## Error Classification System

Each error is classified into one of 24 categories based on the error message:

| Category | Description | Count |
|----------|-------------|-------|
| no_equality | No equality operator found in expression | 514 |
| invalid syntax | LaTeX syntax error | 286 |
| not_equation | Compiler identified as not equation | 222 |
| empty_side | Empty side after normalization | 142 |
| None | None returned from parser | 95 |
| variables | Variables issue | 61 |
| argument of type 'Symbol' is not iterable | SymPy type error | 42 |
| multiple_equalities | Multiple equality operators | 21 |
| unexpected character after line continuation | LaTeX line continuation syntax error | 17 |
| Attribute 'free_symbols' not installed | SymPy registry issue | 13 |
| unsupported operand type(s) for ** or pow(): 'Integer' and 'builtin_function_or_method' | Type error | 12 |
| tuple object has no attribute 'free_symbols' | Attribute error | 11 |
| function object has no attribute 'free_symbols' | Attribute error | 10 |
| I don't understand this | Python parser error | 171 |
| can't multiply sequence by non-int of type 'Symbol' | Type error | 4 |
| unsupported operand type(s) for ** or pow(): 'Symbol' and 'tuple' | Type error | 6 |
| multiple generators | Multiple generators in expression | 2 |
| empty_after_normalization | Empty result after normalization | 8 |
| empty_after_definitions | Empty after definitions | 3 |
| unsupported operand type(s) for *: 'Mul' and 'function' | Type error | 3 |
| unsupported operand type(s) for -: 'Mul' and 'StrictGreaterThan' | Type error | 3 |
| unsupported operand type(s) for -: 'StrictGreaterThan' and 'Mul' | Type error | 3 |
| unsupported operand type(s) for Symbol and Or | Type error | 2 |
| empty_after_conversion | Empty after conversion | 1 |

## Paper-Specific Findings

### 2009.00031 (Galactic Habitable Zone)
- **Records:** 667
- **Strategies:** comprehensive (179), definitions (179), pylatexenc (179), attempts (129), regex (1)
- **Dominant error:** no_equality (479 records)
- **Success rate:** 0%

### 2102.03334 (SLIM)
- **Records:** 66
- **Strategies:** comprehensive (17), definitions (17), pylatexenc (17), attempts (13), regex (2)
- **Dominant error:** empty_side (24 records)
- **Success rate:** 0%

### 2605.18130 (Deep SLAM)
- **Records:** 131
- **Strategies:** comprehensive (34), definitions (34), pylatexenc (34), attempts (27), regex (2)
- **Dominant error:** invalid syntax (54 records)
- **Success rate:** 0%

### 2605.24807 (Computers & Education)
- **Records:** 50
- **Strategies:** comprehensive (10), definitions (10), pylatexenc (10), attempts (7), regex (1)
- **Dominant error:** variables (14 records)
- **Success rate:** 0%

## Recommendations

1. **Upgrade SymPy** to resolve registry compatibility issues
2. **Improve LaTeX preprocessing** to handle line continuation characters
3. **Add fallback extraction methods** for malformed LaTeX
4. **Implement error logging** to track failed extractions for manual review
5. **Verify pipeline versions** (SymPy, pylatexenc) against target paper dependencies
6. **Consider alternative extraction methods** for papers with heavy LaTeX notation

## Conclusion

These results help identify PDF fidelity issues and candidate precision problems in formula extraction. The pipeline's universal failures (0% success rate) indicate that supplementary validation methods are needed before concluding on paper content.
