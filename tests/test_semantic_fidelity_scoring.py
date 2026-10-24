"""
Unit tests for Mathematical Semantic Fidelity Scoring Rules
==========================================================
Verifies that scoring rules maintain strict separation between:
1. Lexical token overlap (necessary but not sufficient)
2. Formula isolation (freedom from prose contamination and multiline arrays)
3. Structural agreement (core mathematical operator preserved despite font/boundary noise)
4. Strict mathematical fidelity (target-span exact match vs full-crop exact match)

Prevents regressions where naive substring matching or loose thresholding
falsely certifies incomplete, truncated, or prose-contaminated equations.
"""

import re
import pytest


def naive_token_overlap(recognized_text: str, target_tokens: list[str]) -> bool:
    """The legacy rule in experiments_multi_paper_generalization.py."""
    tokens_found = [tok for tok in target_tokens if tok.lower() in recognized_text.lower()]
    return len(tokens_found) >= max(1, len(target_tokens) - 1)


def strict_token_presence(recognized_text: str, target_tokens: list[str]) -> tuple[bool, list[str]]:
    """
    Strict word-boundary / symbol-aware token presence.
    Prevents single-letter variables (e.g. 'T', 'k', 'x') from matching inside
    unrelated LaTeX command names (e.g. '\\textbf', '\\sqrt', '\\mathrm{data}').
    """
    missing = []
    # Strip backslash macros into a separate token set so variable names don't match command names
    macro_names = set(re.findall(r'\\[a-zA-Z]+', recognized_text))
    # Extract identifiers and symbols outside backslash command names
    non_macro_text = re.sub(r'\\[a-zA-Z]+', ' ', recognized_text)
    
    for tok in target_tokens:
        if tok.startswith('\\'):
            # TeX macro: must match exact macro name
            pattern = re.escape(tok) + r'(?![a-zA-Z])'
            if not re.search(pattern, recognized_text):
                missing.append(tok)
        else:
            # Variable / symbol: match as a standalone word/symbol in non-macro text
            pattern = r'\b' + re.escape(tok) + r'\b'
            if not re.search(pattern, non_macro_text):
                missing.append(tok)
    return len(missing) == 0, missing


def detect_prose_contamination(rec: str) -> tuple[bool, list[str]]:
    """
    Detect prose contamination, including spaced-letter OCR artifacts
    (e.g., 'd e s i r e d ~ d i s t r i', 'S c a n i n g').
    """
    # Strip TeX commands
    stripped = re.sub(r'\\[a-zA-Z]+', ' ', rec)
    # Compact spaced-out individual letters: 'd e s i r e d' -> 'desired'
    compacted = re.sub(r'(?<=[a-zA-Z])\s+(?=[a-zA-Z])', '', stripped)
    
    allowed = {
        'lim', 'sup', 'inf', 'max', 'min', 'sin', 'cos', 'tan',
        'exp', 'log', 'det', 'dim', 'var', 'cov', 'div', 'data',
        'skip', 'out', 'in', 'matrix', 'array', 'aligned', 'cases'
    }
    words = re.findall(r'[a-zA-Z]{4,}', compacted)
    prose_words = [w for w in words if w.lower() not in allowed]
    return len(prose_words) > 0, prose_words


def check_delimiter_completeness(rec: str) -> tuple[bool, str]:
    """Check whether brackets, norms, and inner products are balanced."""
    delims = {
        r'\langle': r'\rangle',
        r'\left(': r'\right)',
        r'\left[': r'\right]',
        r'\left\{': r'\right\}',
    }
    for open_d, close_d in delims.items():
        open_count = len(re.findall(re.escape(open_d), rec))
        close_count = len(re.findall(re.escape(close_d), rec))
        if open_count != close_count:
            return False, f"Unbalanced delimiter: {open_d} ({open_count}) vs {close_d} ({close_count})"
    
    # Check simple angle brackets < >
    if '<' in rec and '>' not in rec and r'\langle' not in rec:
        return False, "Unmatched '<'"
    if r'\langle' in rec and r'\rangle' not in rec:
        return False, "Unmatched '\\langle' (truncated inner product)"
        
    # Check norm bars: || must be paired
    norm_bars = len(re.findall(r'\\\|', rec))
    if norm_bars % 2 != 0:
        return False, f"Unpaired double-bar norms: count={norm_bars}"
        
    return True, "Balanced"


# =========================================================================
# TEST SUITE
# =========================================================================

def test_two_token_expression_missing_one_token():
    """
    A two-token expression (e.g. '\\zeta', 'v') must NOT pass strict semantic
    fidelity if one token is missing. The legacy rule allowed max(1, 2-1) = 1 match.
    """
    target = ['\\zeta', 'v']
    incomplete_ocr = r'\zeta^{( \ell+1 )}'  # missing subscript 'v'
    
    # Legacy rule was flawed and would pass:
    assert naive_token_overlap(incomplete_ocr, target) is True, "Legacy rule unexpectedly failed"
    
    # Strict rule must correctly reject:
    passed, missing = strict_token_presence(incomplete_ocr, target)
    assert not passed, "Strict rule should fail when subscript v is missing"
    assert missing == ['v']


def test_single_character_variable_no_false_macro_match():
    """
    Single-letter variable 'T' must NOT match inside '\textbf', '\theta', or 'data'.
    """
    target = ['T']
    
    # OCR output with '\textbf' and 'data', but no independent variable 'T'
    false_match_ocr = r'\textbf{data} + \theta'
    
    # Legacy rule matches 't' inside '\textbf' or 'data' case-insensitively:
    assert naive_token_overlap(false_match_ocr, target) is True, "Legacy rule falsely matched"
    
    # Strict rule must NOT match:
    passed, missing = strict_token_presence(false_match_ocr, target)
    assert not passed, "Strict rule should not match 'T' inside macro name or prose word"
    assert missing == ['T']
    
    # True match should pass:
    true_match_ocr = r'\langle T \chi_I, \chi_J \rangle'
    passed, missing = strict_token_presence(true_match_ocr, target)
    assert passed, f"Strict rule should match 'T' in inner product: {missing}"


def test_single_character_variable_k_and_x():
    r"""
    Variables 'k' and 'x' must not match inside macro names like '\kappa' or '\chi'.
    """
    assert not strict_token_presence(r'\chi_{Q}', ['k'])[0]
    assert not strict_token_presence(r'\kappa_{1}', ['k'])[0]
    assert strict_token_presence(r'\sum_{k=0}^{n} a_{k}', ['k'])[0]
    
    assert not strict_token_presence(r'\exp(\sigma)', ['x'])[0]
    assert strict_token_presence(r'f(x)', ['x'])[0]


def test_truncated_inner_product_delimiter_detected():
    """
    Candidate 2104_01277_cand1 was recognized as '\\langle T \\chi_{I} , |'.
    Delimiter check must flag the missing '\\rangle' as truncation.
    """
    truncated_ocr = r'\langle T \chi_{I} , |'
    balanced, reason = check_delimiter_completeness(truncated_ocr)
    assert not balanced, "Truncated inner product should fail delimiter completeness"
    assert r'\langle' in reason or "Unpaired" in reason or "Unbalanced" in reason


def test_prose_spaced_letters_detected():
    """
    Pix2Text output with spaced letters ('d e s i r e d ~ d i s t r i')
    must be flagged as prose contamination, not an isolated formula.
    """
    ocr_spaced_prose = r'\smile_{\mathrm{d e s i r e d ~ d i s t r i}}'
    has_prose, words = detect_prose_contamination(ocr_spaced_prose)
    assert has_prose, "Spaced prose letters must be detected as prose"
    assert any('desired' in w.lower() for w in words)

    ocr_table_header = r'\frac{\mathrm{S c a n i n g}} {\mathrm{N e t w o r k ~ a n d ~ p r e}}'
    has_prose, words = detect_prose_contamination(ocr_table_header)
    assert has_prose, "Table header text in math environment must be detected as prose"
    assert any('scaning' in w.lower() or 'network' in w.lower() for w in words)


def test_clean_math_not_flagged_as_prose():
    """
    Legitimate math subscripts like \\sigma_{\\mathrm{data}} or c_{\\mathrm{skip}}
    must NOT be flagged as prose contamination.
    """
    clean_sigma = r'\mathbf{\sigma}_{\mathrm{d a t a}}'
    has_prose, words = detect_prose_contamination(clean_sigma)
    assert not has_prose, f"Legitimate subscript data should not be flagged as prose: {words}"

    clean_stirling = r'b_{n}=\sum_{k=0}^{n} \biggl\{\begin{matrix} {n} \\ {k} \\ \end{matrix} \biggr\} a_{k} ,'
    has_prose, words = detect_prose_contamination(clean_stirling)
    assert not has_prose, f"Stirling matrix formula should not be flagged as prose: {words}"


def test_tier_separation_contract():
    """
    Verifies that lexical token overlap != formula isolation != strict fidelity.
    An output can have token overlap while failing isolation and fidelity.
    """
    # Example: OCR output with the target tokens but embedded in prose array
    contaminated_rec = (
        r'\begin{array} {l} {\mathrm{with ~ the ~ fact ~ that}} \\ '
        r'{\mathrm{pair ~} \langle T \chi_{I} , \chi_{J} \rangle} \\ '
        r'{\mathrm{the ~ cubes ~} I , J} \\ \end{array}'
    )
    tokens = ['T', '\\chi']
    
    # 1. Lexical presence: passes
    lex_pass, _ = strict_token_presence(contaminated_rec, tokens)
    assert lex_pass is True
    
    # 2. Formula isolation: FAILS (multiline array + prose words)
    is_array = bool(r'\begin{array}' in contaminated_rec or r'\\' in contaminated_rec)
    has_prose, _ = detect_prose_contamination(contaminated_rec)
    formula_isolated = (not is_array) and (not has_prose)
    assert formula_isolated is False
    
    # 3. Delimiter completeness: passes
    delim_pass, _ = check_delimiter_completeness(contaminated_rec)
    assert delim_pass is True
    
    # 4. Strict crop exact fidelity: FAILS because of surrounding prose tokens
    crop_exact = formula_isolated and delim_pass
    assert crop_exact is False
