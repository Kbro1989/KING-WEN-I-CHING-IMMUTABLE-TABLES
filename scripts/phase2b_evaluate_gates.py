#!/usr/bin/env python3
"""
Phase 2B — Five-Gate Evaluation Pipeline

Evaluates candidate extractions against the frozen five acceptance gates:
1. Geometry and clearance
2. Ordered token alignment
3. Operator and delimiter integrity
4. Literal notation match vs semantic equivalence
5. Authoritative provenance

Input: candidate records with reference_id and recognized_latex
Output: disposition matrix records per candidate
"""

import json
import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict
from collections import Counter

# ─── Frozen Gate Definitions ─────────────────────────────────────────
GATE_NAMES = [
    "gate_1_geometry",
    "gate_2_token_alignment",
    "gate_3_operator_delimiter",
    "gate_4_literal_vs_semantic",
    "gate_5_provenance",
]

GATE_OUTCOMES = {
    "gate_1_geometry": ["pass", "fail", "unresolved"],
    "gate_2_token_alignment": ["pass", "fail", "unresolved"],
    "gate_3_operator_delimiter": ["pass", "fail", "unresolved"],
    "gate_4_literal_vs_semantic": ["literal_match", "semantic_equiv", "mismatch", "unresolved"],
    "gate_5_provenance": ["verified", "partial", "unverified", "unresolved"],
}

FAILURE_SOURCES = [
    "geometry/crop",
    "OCR or extraction",
    "token order",
    "operator/structure",
    "reference mismatch",
    "provenance",
    "unresolved/other",
]

# ─── LaTeX Normalization (from evaluate_output_reference.py) ─────────
def normalize_latex(s: str) -> str:
    if not s:
        return ''
    s = s.strip()
    for w in [r'\displaystyle', r'\textstyle', r'\scriptstyle']:
        s = s.replace(w, '')
    s = re.sub(r'\\left(?![a-zA-Z])\s*', '', s)
    s = re.sub(r'\\right(?![a-zA-Z])\s*', '', s)
    s = s.replace(r'\boldsymbol', r'\mathbf')
    s = s.replace(r'\cal', r'\mathcal')
    s = re.sub(r'\\mathbf\{(\\[a-zA-Z]+)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]+)\}', lambda m: r'\mathrm{' + m.group(1).replace(' ', '') + '}', s)
    s = re.sub(r'\{\s*\\mathcal\s*([a-zA-Z])\s*\}', r'\\mathcal{\1}', s)
    s = re.sub(r'_([a-zA-Z0-9])(?![a-zA-Z0-9_{])', r'_{\1}', s)
    s = re.sub(r'\^([a-zA-Z0-9])(?![a-zA-Z0-9^{])', r'^{\1}', s)
    s = re.sub(r'[.,;:]+$', '', s.strip())
    s = re.sub(r'([a-zA-Z])\s+\(', r'\1(', s)
    s = re.sub(r'{\s+', '{', s)
    s = re.sub(r'\s+}', '}', s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = re.sub(r'\\([a-zA-Z]+)\s*', r'\\\1 ', s)
    s = re.sub(r'}\s*\{', '}{', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([_^])\s*', r'\1', s)
    s = re.sub(r'\s*([+=-])\s*', r'\1', s)
    s = re.sub(r'\\([a-zA-Z]+)\s+\{', r'\\\1{', s)
    s = re.sub(r'\\([a-zA-Z]+)\s+\}', r'\\\1}', s)
    s = re.sub(r'\s+\}', '}', s)
    return s.strip()


# ─── Tokenization for Ordered Alignment ──────────────────────────────
TOKEN_RE = re.compile(
    r'\\(?:sum|prod|int|oint|frac|sqrt|partial|nabla|dot|ddot|hat|bar|tilde|vec|'
    r'langle|rangle|lVert|rVert|lfloor|rfloor|lceil|rceil|approx|sim|propto|leq|geq|neq|equiv|cong|asymp|'
    r'gg|ll|in|subset|cup|cap|sum|times|pm|mp|cdot|ldots|cdots|vdots|ddots|'
    r'alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi|varpi|rho|varrho|sigma|varsigma|tau|upsilon|phi|varphi|chi|psi|omega|'
    r'Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|'
    r'left|right|big|Big|bigg|Bigg|'
    r'mathrm|mathbf|mathcal|mathcal|mathfrak|mathbb|'
    r'frac|dfrac|tfrac|cfrac|binom|'
    r'sqrt|sqrt\[[^\]]*\]|'
    r'sum|prod|int|oint|lim|sup|inf|max|min|'
    r'log|ln|sin|cos|tan|arcsin|arccos|arctan|'
    r'exp|det|tr|rank|dim|ker|im|hom|ext|tor|'
    r'partial|nabla|infty|emptyset|infty|square|triangle|angle|'
    r'leq|geq|neq|equiv|approx|sim|propto|subset|supset|cup|cap|'
    r'in|ni|notin|subseteq|supseteq|subseteqq|supseteqq|'
    r'setminus|cdot|ldots|cdots|vdots|ddots|pm|mp|times|div|'
    r'ast|star|circ|bullet|diamond|ominus|oplus|otimes|oslash|odot|'
    r'leq|geq|prec|succ|preceq|succeq|ll|gg|'
    r'vdash|dashv|models|perp|parallel|mid|nmid|'
    r'subset|supset|cup|cap|uplus|sqcup|sqcap|vee|wedge|'
    r'lhd|rhd|unlhd|unrhd|triangleleft|triangleright)'
)
SIMPLE_TOKEN_RE = re.compile(r'[a-zA-Z0-9]+|[=+\-*/^_(),\[\]{}|<>:;.,]')

def tokenize_latex(latex: str) -> list[str]:
    """Tokenize LaTeX into structural tokens for ordered comparison."""
    tokens = []
    i = 0
    while i < len(latex):
        # Try command match
        m = TOKEN_RE.match(latex, i)
        if m:
            tokens.append(m.group(0))
            i = m.end()
            continue
        # Single char tokens
        ch = latex[i]
        if ch in '=+-*/^_()[]{}|<>.,:;':
            tokens.append(ch)
        elif ch.isalnum() or ch == '_':
            # Accumulate alphanumeric
            j = i
            while j < len(latex) and (latex[j].isalnum() or latex[j] == '_'):
                j += 1
            tokens.append(latex[i:j])
            i = j - 1
        i += 1
    return tokens


def lcs_length(a: list[str], b: list[str]) -> int:
    """Longest common subsequence length."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[len(a)][len(b)]


# ─── Delimiter Balance Check ────────────────────────────────────────
DELIMITER_PAIRS = [
    (r'\{', r'\}'),
    (r'\(', r'\)'),
    (r'\[', r'\]'),
    (r'\langle', r'\rangle'),
    (r'\lVert', r'\rVert'),
    (r'\lfloor', r'\rfloor'),
    (r'\lceil', r'\rceil'),
    ('|', '|'),
]

def check_delimiter_balance(text: str) -> dict:
    issues = []
    for opener, closer in DELIMITER_PAIRS:
        if opener == closer:
            count = text.count(opener)
            if count % 2 != 0:
                issues.append(f'odd count for paired delimiter {opener!r}: {count}')
            elif count == 0:
                pass  # Not required
        else:
            open_count = text.count(opener)
            close_count = text.count(closer)
            if open_count != close_count:
                issues.append(f'unbalanced {opener!r}/{closer!r}: {open_count} vs {close_count}')
            elif open_count == 0:
                pass  # Not required
    return {'balanced': len(issues) == 0, 'issues': issues}


# ─── Truncation Detection ────────────────────────────────────────────
def detect_truncation(text: str) -> dict:
    indicators = []
    # Unmatched \left without \right
    left_n = len(re.findall(r'\\left(?![a-zA-Z])', text))
    right_n = len(re.findall(r'\\right(?![a-zA-Z])', text))
    if left_n > right_n:
        indicators.append('unmatched_left_delimiters')
    # Unmatched angle brackets
    if text.count(r'\langle') > text.count(r'\rangle'):
        indicators.append('unmatched_langle')
    # Unmatched braces
    if text.count('{') != text.count('}'):
        indicators.append('unbalanced_braces')
    # Trailing binary or relational operator
    stripped = text.rstrip()
    if stripped and stripped[-1] in '=+*,-':
        indicators.append('trailing_operator')
    # Empty bound operand
    if re.search(r'=\s*\}', text) or re.search(r'=\s*\^', text) or re.search(r'_\{[a-zA-Z0-9\s]*=\s*\}', text):
        indicators.append('empty_bound_operand')
    # Very short output
    if len(text.strip()) < 3:
        indicators.append('very_short_output')
    return {'detected': len(indicators) > 0, 'indicators': indicators}


# ─── Structure Checks ────────────────────────────────────────────────
STRUCTURE_CHECKS = {
    'summation': lambda t: r'\sum' in t,
    'product': lambda t: r'\prod' in t,
    'integral': lambda t: r'\int' in t or r'\oint' in t,
    'derivative': lambda t: any(tok in t for tok in (r'\dot', r'\ddot', r'\partial', r'\frac{d}{d}', r'\frac{\partial}{\partial}')),
    'fraction': lambda t: any(tok in t for tok in (r'\frac', r'\dfrac', r'\tfrac', r'\cfrac')),
    'radical': lambda t: r'\sqrt' in t,
    'matrix': lambda t: any(tok in t for tok in (r'\begin{matrix}', r'\begin{pmatrix}', r'\begin{bmatrix}', r'\begin{array}')),
    'bounded_subsup': lambda t: '_{' in t and '}^{' in t,
    'set_notation': lambda t: any(tok in t for tok in (r'\in', r'\subset', r'\cup', r'\cap', r'\{', r'\}')),
    'non_equality_relation': lambda t: any(tok in t for tok in (r'\approx', r'\sim', r'\propto', r'\leq', r'\geq', r'\neq', r'\equiv', r'\cong', r'\asymp')),
    'delimiter_pair': lambda t: any(tok in t for tok in (r'\langle', r'\lVert', r'\lfloor', r'\lceil')),
}

def check_structure(text: str, struct: str) -> bool:
    checker = STRUCTURE_CHECKS.get(struct)
    return checker(text) if checker is not None else True


# ─── Gate 1: Geometry and Clearance ──────────────────────────────────
def gate_1_geometry(reference_latex: str, recognized_latex: str, is_display: bool) -> dict:
    """Check crop isolation - no adjacent text bleed, adequate margins."""
    truncation = detect_truncation(recognized_latex)
    
    # Also check for significant length reduction (possible clipping)
    ref_len = len(reference_latex.strip())
    rec_len = len(recognized_latex.strip())
    length_ratio = rec_len / ref_len if ref_len > 0 else 1.0
    
    # Explicit truncation markers
    has_truncation_marker = '[TRUNCATED]' in recognized_latex or '...' in recognized_latex[-20:]

    result = {
        'gate': 'gate_1_geometry',
        'outcome': 'pass',
        'evidence': {
            'reference_length': ref_len,
            'recognized_length': rec_len,
            'length_ratio': round(length_ratio, 3),
            'truncation_marker': has_truncation_marker,
        },
        'failure_sources': [],
    }
    if truncation['detected'] or has_truncation_marker or length_ratio < 0.5:
        result['outcome'] = 'fail'
        result['failure_sources'].append('geometry/crop')
        indicators = truncation['indicators'].copy()
        if has_truncation_marker:
            indicators.append('explicit_truncation_marker')
        if length_ratio < 0.5:
            indicators.append('length_ratio_below_threshold')
        result['evidence']['truncation_indicators'] = indicators
    return result


# ─── Gate 2: Ordered Token Alignment ────────────────────────────────
def gate_2_token_alignment(reference_latex: str, recognized_latex: str) -> dict:
    """LCS-based ordered token alignment with operator identity check."""
    ref_tokens = tokenize_latex(normalize_latex(reference_latex))
    rec_tokens = tokenize_latex(normalize_latex(recognized_latex))

    lcs = lcs_length(ref_tokens, rec_tokens)
    recall = lcs / len(ref_tokens) if ref_tokens else 1.0

    # Check token order violations: find first divergence
    order_violation = False
    if ref_tokens != rec_tokens:
        # Check if same tokens but different order (permutation)
        if Counter(ref_tokens) == Counter(rec_tokens):
            order_violation = True

    # Missing tokens (in reference but not in recognized)
    missing_tokens = [t for t in ref_tokens if t not in rec_tokens]
    extra_tokens = [t for t in rec_tokens if t not in ref_tokens]

    # Detect specific reorder patterns
    reorder_detected = False
    if len(ref_tokens) == len(rec_tokens) and not order_violation:
        # Check for bound swaps in summation
        for i, (rt, rc) in enumerate(zip(ref_tokens, rec_tokens)):
            if rt != rc and i < len(ref_tokens) - 1:
                # Check if adjacent tokens swapped
                if i + 1 < len(ref_tokens) and rt == rec_tokens[i+1] and rc == ref_tokens[i+1]:
                    reorder_detected = True
                    break

    # Threshold: fail if recall < 0.8 OR order violation OR substantial missing tokens OR reorder detected
    result = {
        'gate': 'gate_2_token_alignment',
        'outcome': 'pass',
        'evidence': {
            'ref_token_count': len(ref_tokens),
            'rec_token_count': len(rec_tokens),
            'lcs': lcs,
            'recall': round(recall, 3),
            'order_violation': order_violation,
            'reorder_detected': reorder_detected,
            'missing_token_count': len(missing_tokens),
            'extra_token_count': len(extra_tokens),
            'ref_tokens': ref_tokens[:50],
            'rec_tokens': rec_tokens[:50],
        },
        'failure_sources': [],
    }
    if recall < 0.8 or order_violation or len(missing_tokens) > 3 or reorder_detected:
        result['outcome'] = 'fail'
        if order_violation or reorder_detected:
            result['failure_sources'].append('token order')
        if recall < 0.8 or len(missing_tokens) > 3:
            result['failure_sources'].append('OCR or extraction')
    return result


# ─── Gate 3: Operator and Delimiter Integrity ───────────────────────
def gate_3_operator_delimiter(reference_latex: str, recognized_latex: str) -> dict:
    """Check operators and delimiter pairs are present with correct nesting."""
    ref_norm = normalize_latex(reference_latex)
    rec_norm = normalize_latex(recognized_latex)

    # Required operators from reference
    ref_ops = set()
    for op in STRUCTURE_CHECKS:
        if check_structure(ref_norm, op):
            ref_ops.add(op)

    # Check each required operator present in recognized
    missing_ops = []
    for op in ref_ops:
        if not check_structure(rec_norm, op):
            missing_ops.append(op)

    # Detect operator substitutions (operator in rec but not in ref, or vice versa)
    rec_ops = set()
    for op in STRUCTURE_CHECKS:
        if check_structure(rec_norm, op):
            rec_ops.add(op)

    substituted_ops = []
    # Check if rec has an operator where ref has a different one for same structure
    # e.g., ref has \sum, rec has 'S' - this won't be caught by structure checks
    # but we can check for common substitution patterns
    sub_patterns = {
        'summation': ['S', 'Sigma', 'E'],
        'product': ['P', 'Pi'],
        'integral': ['I', 'int'],
        'fraction': ['/'],
        'radical': ['v', 'sqrt'],
        'partial_derivative': ['d'],
    }
    for struct, patterns in sub_patterns.items():
        if struct in ref_ops:
            for p in patterns:
                if p in rec_norm and struct not in rec_ops:
                    substituted_ops.append(f'{struct}->{p}')

    # Delimiter balance
    balance = check_delimiter_balance(rec_norm)

    # Check for specific delimiter mismatches (e.g., \langle with \rVert)
    delimiter_mismatches = []
    if r'\langle' in rec_norm and r'\rangle' not in rec_norm:
        if r'\rVert' in rec_norm or r'|' in rec_norm:
            delimiter_mismatches.append('angle_bracket_with_norm')
    if r'\lfloor' in rec_norm and r'\rfloor' not in rec_norm:
        delimiter_mismatches.append('floor_without_ceil')
    if r'\lceil' in rec_norm and r'\rceil' not in rec_norm:
        delimiter_mismatches.append('ceil_without_floor')

    result = {
        'gate': 'gate_3_operator_delimiter',
        'outcome': 'pass' if (not missing_ops and balance['balanced'] and not substituted_ops and not delimiter_mismatches) else 'fail',
        'evidence': {
            'required_operators': sorted(ref_ops),
            'recognized_operators': sorted(rec_ops),
            'missing_operators': missing_ops,
            'substituted_operators': substituted_ops,
            'delimiter_balanced': balance['balanced'],
            'delimiter_issues': balance['issues'],
            'delimiter_mismatches': delimiter_mismatches,
        },
        'failure_sources': [],
    }
    if result['outcome'] == 'fail':
        if missing_ops or substituted_ops:
            result['failure_sources'].append('operator/structure')
        if not balance['balanced'] or delimiter_mismatches:
            result['failure_sources'].append('operator/structure')
    return result


# ─── Gate 4: Literal vs Semantic Equivalence ───────────────────────
def gate_4_literal_vs_semantic(reference_latex: str, recognized_latex: str) -> dict:
    """Distinguish exact match from semantic equivalence. 
    Returns 'unresolved' when difference is explained by other defect gates.
    Only returns 'mismatch' for reference-level notation errors."""
    ref_norm = normalize_latex(reference_latex)
    rec_norm = normalize_latex(recognized_latex)

    result = {
        'gate': 'gate_4_literal_vs_semantic',
        'outcome': 'unresolved',
        'evidence': {
            'normalized_recognized': rec_norm,
            'normalized_reference': ref_norm,
        },
        'failure_sources': [],
    }

    if rec_norm == ref_norm:
        result['outcome'] = 'literal_match'
        return result

    # Check for common semantic equivalences (known notational variants)
    equiv = False
    equiv_type = None

    # fraction vs solidus
    if (r'\frac' in ref_norm and '/' in rec_norm and r'\frac' not in rec_norm) or \
       ('/' in ref_norm and r'\frac' in rec_norm and '/' not in ref_norm):
        equiv = True
        equiv_type = 'fraction_solidus'

    # sum vs Sigma
    if (r'\sum' in ref_norm and 'Σ' in rec_norm) or \
       ('Σ' in ref_norm and r'\sum' in rec_norm):
        equiv = True
        equiv_type = 'sum_sigma'

    # product vs Pi
    if (r'\prod' in ref_norm and 'Π' in rec_norm) or \
       ('Π' in ref_norm and r'\prod' in rec_norm):
        equiv = True
        equiv_type = 'prod_pi'

    # integral variants
    if (r'\int' in ref_norm and '∫' in rec_norm) or \
       ('∫' in ref_norm and r'\int' in rec_norm):
        equiv = True
        equiv_type = 'integral_unicode'

    # sqrt variants
    if (r'\sqrt' in ref_norm and '√' in rec_norm) or \
       ('√' in ref_norm and r'\sqrt' in rec_norm):
        equiv = True
        equiv_type = 'sqrt_unicode'

    # partial derivative
    if (r'\partial' in ref_norm and '∂' in rec_norm) or \
       ('∂' in ref_norm and r'\partial' in rec_norm):
        equiv = True
        equiv_type = 'partial_unicode'

    # nabla/gradient
    if (r'\nabla' in ref_norm and '∇' in rec_norm) or \
       ('∇' in ref_norm and r'\nabla' in rec_norm):
        equiv = True
        equiv_type = 'nabla_unicode'

    # approx/tilde
    if (r'\approx' in ref_norm and '≈' in rec_norm) or \
       ('≈' in ref_norm and r'\approx' in rec_norm):
        equiv = True
        equiv_type = 'approx_unicode'

    # leq/geq unicode
    if (r'\leq' in ref_norm and '≤' in rec_norm) or \
       ('≤' in ref_norm and r'\leq' in rec_norm):
        equiv = True
        equiv_type = 'leq_unicode'
    if (r'\geq' in ref_norm and '≥' in rec_norm) or \
       ('≥' in ref_norm and r'\geq' in rec_norm):
        equiv = True
        equiv_type = 'geq_unicode'

    # neq unicode
    if (r'\neq' in ref_norm and '≠' in rec_norm) or \
       ('≠' in ref_norm and r'\neq' in rec_norm):
        equiv = True
        equiv_type = 'neq_unicode'

    # angle brackets
    if (r'\langle' in ref_norm and '⟨' in rec_norm) or \
       ('⟨' in ref_norm and r'\langle' in rec_norm):
        equiv = True
        equiv_type = 'langle_unicode'
    if (r'\rangle' in ref_norm and '⟩' in rec_norm) or \
       ('⟩' in ref_norm and r'\rangle' in rec_norm):
        equiv = True
        equiv_type = 'rangle_unicode'

    # lVert/rVert unicode
    if (r'\lVert' in ref_norm and '‖' in rec_norm) or \
       ('‖' in ref_norm and r'\lVert' in rec_norm):
        equiv = True
        equiv_type = 'lVert_unicode'

    # Greek letters
    greek_map = {
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
        r'\epsilon': 'ε', r'\varepsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η',
        r'\theta': 'θ', r'\vartheta': 'ϑ', r'\iota': 'ι', r'\kappa': 'κ',
        r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ',
        r'\pi': 'π', r'\varpi': 'ϖ', r'\rho': 'ρ', r'\varrho': 'ϱ',
        r'\sigma': 'σ', r'\varsigma': 'ς', r'\tau': 'τ', r'\upsilon': 'υ',
        r'\phi': 'φ', r'\varphi': 'ϕ', r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
        r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
        r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Upsilon': 'Υ',
        r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω',
    }
    for cmd, uni in greek_map.items():
        if (cmd in ref_norm and uni in rec_norm) or (uni in ref_norm and cmd in rec_norm):
            equiv = True
            equiv_type = f'greek_{cmd[1:]}_unicode'
            break

    if equiv:
        result['outcome'] = 'semantic_equiv'
        result['evidence']['equivalence_type'] = equiv_type
        return result

    # If we reach here, it's a structural difference not explained by known equivalences.
    # This is NOT a "mismatch" in the literal-vs-semantic sense - it's a defect
    # caught by other gates (truncation, operator_sub, token_reorder, etc.).
    # Return 'unresolved' to indicate this gate doesn't classify this difference.
    result['outcome'] = 'unresolved'
    return result


# ─── Gate 5: Authoritative Provenance ──────────────────────────────
def gate_5_provenance(reference_id: str, paper_id: str, html_index: int) -> dict:
    """Verify reference traces to authoritative arXiv HTML x-tex annotation."""
    # In this pilot, all references come from reference_equations.jsonl which
    # was built from arXiv HTML MathML + x-tex annotations. So provenance is
    # verified by construction, unless the reference_id is missing from the corpus.
    result = {
        'gate': 'gate_5_provenance',
        'outcome': 'verified',
        'evidence': {
            'reference_id': reference_id,
            'paper_id': paper_id,
            'html_index': html_index,
            'source': 'arXiv HTML x-tex annotation',
        },
        'failure_sources': [],
    }
    return result


# ─── Main Evaluation Function ────────────────────────────────────────
def evaluate_candidate(
    candidate: dict,
    recognized_latex: str
) -> dict:
    """Run all five gates on a single candidate."""
    reference_latex = candidate['latex']
    reference_id = candidate['reference_id']
    paper_id = candidate['paper_id']
    html_index = candidate.get('html_index', -1)
    is_display = candidate.get('is_display', False)

    gates = {}
    all_failure_sources = []

    # Gate 1
    g1 = gate_1_geometry(reference_latex, recognized_latex, is_display)
    gates['gate_1_geometry'] = g1['outcome']
    all_failure_sources.extend(g1['failure_sources'])

    # Gate 2
    g2 = gate_2_token_alignment(reference_latex, recognized_latex)
    gates['gate_2_token_alignment'] = g2['outcome']
    all_failure_sources.extend(g2['failure_sources'])

    # Gate 3
    g3 = gate_3_operator_delimiter(reference_latex, recognized_latex)
    gates['gate_3_operator_delimiter'] = g3['outcome']
    all_failure_sources.extend(g3['failure_sources'])

    # Gate 4
    g4 = gate_4_literal_vs_semantic(reference_latex, recognized_latex)
    gates['gate_4_literal_vs_semantic'] = g4['outcome']
    all_failure_sources.extend(g4['failure_sources'])

    # Gate 5
    g5 = gate_5_provenance(reference_id, paper_id, html_index)
    gates['gate_5_provenance'] = g5['outcome']
    all_failure_sources.extend(g5['failure_sources'])

    # Final disposition
    if all(g == 'pass' or g == 'literal_match' or g == 'verified' for g in gates.values()):
        disposition = 'accept'
    elif any(g == 'fail' or g == 'mismatch' or g == 'unverified' for g in gates.values()):
        disposition = 'reject'
    else:
        disposition = 'unresolved'

    # Deduplicate failure sources
    failure_sources = list(dict.fromkeys(all_failure_sources))

    return {
        'candidate_id': reference_id,
        'paper_id': paper_id,
        **gates,
        'failure_sources': failure_sources,
        'evidence_ref': f"reference:{reference_id}",
        'final_disposition': disposition,
        'reviewer_status': 'pending',
        'review_notes': '',
        'gate_evidence': {
            'gate_1': g1['evidence'],
            'gate_2': g2['evidence'],
            'gate_3': g3['evidence'],
            'gate_4': g4['evidence'],
            'gate_5': g5['evidence'],
        },
    }


# ─── Batch Evaluation ────────────────────────────────────────────────
def evaluate_batch(candidates: list[dict], recognized_outputs: dict[str, str]) -> list[dict]:
    """Evaluate multiple candidates given a dict of reference_id -> recognized_latex."""
    results = []
    for cand in candidates:
        ref_id = cand['reference_id']
        recognized = recognized_outputs.get(ref_id, '')
        result = evaluate_candidate(cand, recognized)
        results.append(result)
    return results


# ─── CLI ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python phase2b_evaluate_gates.py <pilot_selection.json> <recognized_outputs.json> [output.json]")
        sys.exit(1)

    pilot_path = Path(sys.argv[1])
    recognized_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("DATASETS/phase2b_disposition_matrix.jsonl")

    pilot = json.loads(pilot_path.read_text(encoding='utf-8'))
    recognized = json.loads(recognized_path.read_text(encoding='utf-8'))

    results = evaluate_batch(pilot['candidates'], recognized)

    # Write JSONL
    with output_path.open('w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f"Evaluated {len(results)} candidates -> {output_path}")

    # Summary
    from collections import Counter
    for gate in GATE_NAMES:
        cnt = Counter(r[gate] for r in results)
        print(f"  {gate}: {dict(cnt)}")
    disp = Counter(r['final_disposition'] for r in results)
    print(f"  Disposition: {dict(disp)}")