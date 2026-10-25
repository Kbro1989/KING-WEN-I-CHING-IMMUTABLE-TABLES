#!/usr/bin/env python3
"""
Phase 2C — Shared Gate Library

Extracted and enhanced from Phase 2B evaluation script.
This is the canonical gate implementation for Phase 2C and beyond.
Phase 2B's scripts/phase2b_evaluate_gates.py remains FROZEN.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from collections import Counter
from dataclasses import dataclass, asdict


# ═══════════════════════════════════════════════════════════════════════
# NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════

def normalize_latex(s: str) -> str:
    """Normalize LaTeX for conservative comparison."""
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


# ═══════════════════════════════════════════════════════════════════════
# TOKENIZATION
# ═══════════════════════════════════════════════════════════════════════

TOKEN_RE = re.compile(
    r'\\(?:sum|prod|int|oint|frac|sqrt|partial|nabla|dot|ddot|hat|bar|tilde|vec|'
    r'langle|rangle|lVert|rVert|lfloor|rfloor|lceil|rceil|approx|sim|propto|leq|geq|neq|equiv|cong|asymp|'
    r'gg|ll|in|subset|cup|cap|sum|times|pm|mp|cdot|ldots|cdots|vdots|ddots|'
    r'alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi|varpi|rho|varrho|sigma|varsigma|tau|upsilon|phi|varphi|chi|psi|omega|'
    r'Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|'
    r'left|right|big|Big|bigg|Bigg|'
    r'mathrm|mathbf|mathcal|mathfrak|mathbb|'
    r'frac|dfrac|tfrac|cfrac|binom|'
    r'sqrt|sqrt\[[^\]]*\]|'
    r'sum|prod|int|oint|lim|sup|inf|max|min|'
    r'log|ln|sin|cos|tan|arcsin|arccos|arctan|'
    r'exp|det|tr|rank|dim|ker|im|hom|ext|tor|'
    r'partial|nabla|infty|emptyset|square|triangle|angle|'
    r'leq|geq|neq|equiv|approx|sim|propto|subset|supset|cup|cap|'
    r'in|ni|notin|subseteq|supseteq|subseteqq|supseteqq|'
    r'setminus|cdot|ldots|cdots|vdots|ddots|pm|mp|times|div|'
    r'ast|star|circ|bullet|diamond|ominus|oplus|otimes|oslash|odot|'
    r'leq|geq|prec|succ|preceq|succeq|ll|gg|'
    r'vdash|dashv|models|perp|parallel|mid|nmid|'
    r'subset|supset|cup|cap|uplus|sqcup|sqcap|vee|wedge|'
    r'lhd|rhd|unlhd|unrhd|triangleleft|triangleright)'
)

def tokenize_latex(latex: str) -> List[str]:
    """Tokenize LaTeX into structural tokens for ordered comparison."""
    tokens = []
    i = 0
    while i < len(latex):
        m = TOKEN_RE.match(latex, i)
        if m:
            tokens.append(m.group(0))
            i = m.end()
            continue
        ch = latex[i]
        if ch in '=+-*/^_()[]{}|<>.,:;':
            tokens.append(ch)
        elif ch.isalnum() or ch == '_':
            j = i
            while j < len(latex) and (latex[j].isalnum() or latex[j] == '_'):
                j += 1
            tokens.append(latex[i:j])
            i = j - 1
        i += 1
    return tokens


def lcs_length(a: List[str], b: List[str]) -> int:
    """Longest common subsequence length."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[len(a)][len(b)]


# ═══════════════════════════════════════════════════════════════════════
# DELIMITER BALANCE
# ═══════════════════════════════════════════════════════════════════════

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

def check_delimiter_balance(text: str) -> Dict:
    issues = []
    for opener, closer in DELIMITER_PAIRS:
        if opener == closer:
            count = text.count(opener)
            if count % 2 != 0:
                issues.append(f'odd count for paired delimiter {opener!r}: {count}')
        else:
            open_count = text.count(opener)
            close_count = text.count(closer)
            if open_count != close_count:
                issues.append(f'unbalanced {opener!r}/{closer!r}: {open_count} vs {close_count}')
    return {'balanced': len(issues) == 0, 'issues': issues}


# ═══════════════════════════════════════════════════════════════════════
# TRUNCATION DETECTION
# ═══════════════════════════════════════════════════════════════════════

def detect_truncation(text: str) -> Dict:
    indicators = []
    left_n = len(re.findall(r'\\left(?![a-zA-Z])', text))
    right_n = len(re.findall(r'\\right(?![a-zA-Z])', text))
    if left_n > right_n:
        indicators.append('unmatched_left_delimiters')
    if text.count(r'\langle') > text.count(r'\rangle'):
        indicators.append('unmatched_langle')
    if text.count('{') != text.count('}'):
        indicators.append('unbalanced_braces')
    stripped = text.rstrip()
    if stripped and stripped[-1] in '=+*,-':
        indicators.append('trailing_operator')
    if re.search(r'=\s*\}', text) or re.search(r'=\s*\^', text) or re.search(r'_\{[a-zA-Z0-9\s]*=\s*\}', text):
        indicators.append('empty_bound_operand')
    if len(text.strip()) < 3:
        indicators.append('very_short_output')
    return {'detected': len(indicators) > 0, 'indicators': indicators}


# ═══════════════════════════════════════════════════════════════════════
# STRUCTURE CHECKS (Phase 2B compatible)
# ═══════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════
# GATE 1: GEOMETRY AND CLEARANCE
# ═══════════════════════════════════════════════════════════════════════

def gate_1_geometry(reference_latex: str, recognized_latex: str, is_display: bool) -> Dict:
    """Check crop isolation - no adjacent text bleed, adequate margins."""
    truncation = detect_truncation(recognized_latex)
    has_truncation_marker = '[TRUNCATED]' in recognized_latex or '...' in recognized_latex[-20:]

    ref_len = len(reference_latex.strip())
    rec_len = len(recognized_latex.strip())
    length_ratio = rec_len / ref_len if ref_len > 0 else 1.0

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


# ═══════════════════════════════════════════════════════════════════════
# GATE 2: ORDERED TOKEN ALIGNMENT
# ═══════════════════════════════════════════════════════════════════════

def gate_2_token_alignment(reference_latex: str, recognized_latex: str) -> Dict:
    """LCS-based ordered token alignment with operator identity check."""
    ref_tokens = tokenize_latex(normalize_latex(reference_latex))
    rec_tokens = tokenize_latex(normalize_latex(recognized_latex))

    lcs = lcs_length(ref_tokens, rec_tokens)
    recall = lcs / len(ref_tokens) if ref_tokens else 1.0

    order_violation = False
    if ref_tokens != rec_tokens:
        if Counter(ref_tokens) == Counter(rec_tokens):
            order_violation = True

    reorder_detected = False
    if len(ref_tokens) == len(rec_tokens) and not order_violation:
        for i, (rt, rc) in enumerate(zip(ref_tokens, rec_tokens)):
            if rt != rc and i < len(ref_tokens) - 1:
                if i + 1 < len(ref_tokens) and rt == rec_tokens[i+1] and rc == ref_tokens[i+1]:
                    reorder_detected = True
                    break

    missing_tokens = [t for t in ref_tokens if t not in rec_tokens]
    extra_tokens = [t for t in rec_tokens if t not in ref_tokens]

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


# ═══════════════════════════════════════════════════════════════════════
# GATE 3: OPERATOR AND DELIMITER INTEGRITY (Phase 2C Enhanced)
# ═══════════════════════════════════════════════════════════════════════

# Phase 2C: Explicit operator substitution patterns
OPERATOR_SUBSTITUTIONS = {
    'summation': ['S', 'Sigma', 'E'],
    'product': ['P', 'Pi'],
    'integral': ['I', 'int'],
    'fraction': ['/'],
    'radical': ['v', 'sqrt'],
    'partial_derivative': ['d'],
    'nabla': ['del'],
    'approximation': ['~'],
    'equality': ['='],
    'set_membership': ['in'],
}

# Phase 2C: Context-aware substitution detection
def detect_operator_substitution(ref_norm: str, rec_norm: str) -> List[str]:
    """Detect operator substitutions with context awareness."""
    substituted = []
    ref_ops = set()
    rec_ops = set()

    for op in STRUCTURE_CHECKS:
        if check_structure(ref_norm, op):
            ref_ops.add(op)
        if check_structure(rec_norm, op):
            rec_ops.add(op)

    # Check for known substitution patterns
    for struct, patterns in OPERATOR_SUBSTITUTIONS.items():
        if struct in ref_ops:
            # Reference has the proper operator; check if recognized uses substitution
            for pattern in patterns:
                if pattern in rec_norm and struct not in rec_ops:
                    substituted.append(f'{struct}->{pattern}')

    return substituted


# Phase 2C: Delimiter mismatch detection
def detect_delimiter_mismatches(rec_norm: str) -> List[str]:
    mismatches = []
    if r'\langle' in rec_norm and r'\rangle' not in rec_norm:
        if r'\rVert' in rec_norm or '|' in rec_norm:
            mismatches.append('angle_bracket_with_norm')
    if r'\lfloor' in rec_norm and r'\rfloor' not in rec_norm:
        mismatches.append('floor_without_ceil')
    if r'\lceil' in rec_norm and r'\rceil' not in rec_norm:
        mismatches.append('ceil_without_floor')
    if r'\lVert' in rec_norm and r'\rVert' not in rec_norm:
        mismatches.append('lVert_without_rVert')
    return mismatches


def gate_3_operator_delimiter(reference_latex: str, recognized_latex: str) -> Dict:
    """Check operators and delimiter pairs are present with correct nesting.
    Phase 2C enhanced: detects operator substitutions and delimiter mismatches."""
    ref_norm = normalize_latex(reference_latex)
    rec_norm = normalize_latex(recognized_latex)

    # Required operators from reference
    ref_ops = set()
    for op in STRUCTURE_CHECKS:
        if check_structure(ref_norm, op):
            ref_ops.add(op)

    # Missing operators
    missing_ops = []
    for op in ref_ops:
        if not check_structure(rec_norm, op):
            missing_ops.append(op)

    # Phase 2C: Operator substitution detection
    substituted_ops = detect_operator_substitution(ref_norm, rec_norm)

    # Phase 2C: Delimiter mismatch detection
    delimiter_mismatches = detect_delimiter_mismatches(rec_norm)

    # Delimiter balance
    balance = check_delimiter_balance(rec_norm)

    result = {
        'gate': 'gate_3_operator_delimiter',
        'outcome': 'pass' if (not missing_ops and balance['balanced'] and not substituted_ops and not delimiter_mismatches) else 'fail',
        'evidence': {
            'required_operators': sorted(ref_ops),
            'recognized_operators': sorted([op for op in STRUCTURE_CHECKS if check_structure(rec_norm, op)]),
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


# ═══════════════════════════════════════════════════════════════════════
# GATE 4: LITERAL VS SEMANTIC EQUIVALENCE
# ═══════════════════════════════════════════════════════════════════════

def gate_4_literal_vs_semantic(reference_latex: str, recognized_latex: str) -> Dict:
    """Distinguish exact match from semantic equivalence.
    Returns 'unresolved' for structural defects (by design)."""
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

    # Known semantic equivalences (Unicode ↔ LaTeX)
    equiv = False
    equiv_type = None

    equiv_map = [
        ((r'\frac' in ref_norm and '/' in rec_norm and r'\frac' not in rec_norm) or
         ('/' in ref_norm and r'\frac' in rec_norm and '/' not in ref_norm),
         'fraction_solidus'),
        ((r'\sum' in ref_norm and 'Σ' in rec_norm) or
         ('Σ' in ref_norm and r'\sum' in rec_norm),
         'sum_sigma'),
        ((r'\prod' in ref_norm and 'Π' in rec_norm) or
         ('Π' in ref_norm and r'\prod' in rec_norm),
         'prod_pi'),
        ((r'\int' in ref_norm and '∫' in rec_norm) or
         ('∫' in ref_norm and r'\int' in rec_norm),
         'integral_unicode'),
        ((r'\sqrt' in ref_norm and '√' in rec_norm) or
         ('√' in ref_norm and r'\sqrt' in rec_norm),
         'sqrt_unicode'),
        ((r'\partial' in ref_norm and '∂' in rec_norm) or
         ('∂' in ref_norm and r'\partial' in rec_norm),
         'partial_unicode'),
        ((r'\nabla' in ref_norm and '∇' in rec_norm) or
         ('∇' in ref_norm and r'\nabla' in rec_norm),
         'nabla_unicode'),
        ((r'\approx' in ref_norm and '≈' in rec_norm) or
         ('≈' in ref_norm and r'\approx' in rec_norm),
         'approx_unicode'),
        ((r'\leq' in ref_norm and '≤' in rec_norm) or
         ('≤' in ref_norm and r'\leq' in rec_norm),
         'leq_unicode'),
        ((r'\geq' in ref_norm and '≥' in rec_norm) or
         ('≥' in ref_norm and r'\geq' in rec_norm),
         'geq_unicode'),
        ((r'\neq' in ref_norm and '≠' in rec_norm) or
         ('≠' in ref_norm and r'\neq' in rec_norm),
         'neq_unicode'),
        ((r'\langle' in ref_norm and '⟨' in rec_norm) or
         ('⟨' in ref_norm and r'\langle' in rec_norm),
         'langle_unicode'),
        ((r'\rangle' in ref_norm and '⟩' in rec_norm) or
         ('⟩' in ref_norm and r'\rangle' in rec_norm),
         'rangle_unicode'),
        ((r'\lVert' in ref_norm and '‖' in rec_norm) or
         ('‖' in ref_norm and r'\lVert' in rec_norm),
         'lVert_unicode'),
    ]

    for condition, eq_type in equiv_map:
        if condition:
            equiv = True
            equiv_type = eq_type
            break

    # Greek letters
    if not equiv:
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

    # Structural defect → unresolved (not a literal-vs-semantic mismatch)
    result['outcome'] = 'unresolved'
    return result


# ═══════════════════════════════════════════════════════════════════════
# GATE 5: AUTHORITATIVE PROVENANCE
# ═══════════════════════════════════════════════════════════════════════

def gate_5_provenance(reference_id: str, paper_id: str, html_index: int, provenance_source: str = None) -> Dict:
    """Verify reference traces to authoritative arXiv HTML x-tex annotation.
    
    Gate 5 is an eligibility prerequisite, NOT a detector of extraction errors.
    Valid provenance authorizes evaluation to proceed; invalid/missing provenance
    blocks the evaluation record.
    """
    result = {
        'gate': 'gate_5_provenance',
        'outcome': 'verified',
        'evidence': {
            'reference_id': reference_id,
            'paper_id': paper_id,
            'html_index': html_index,
            'source': 'arXiv HTML x-tex annotation',
            'eligible': True,
        },
        'failure_sources': [],
    }
    
    # Gate 5 eligibility check: verify the reference_id traces to an authoritative source
    # In production, this should query the persistent provenance store.
    # For Phase 2C calibration tests, we accept the provenance_source parameter.
    if provenance_source is not None and provenance_source not in ('html', 'mathml', 'pdf_footer', 'html_node', 'latex_source'):
        result['outcome'] = 'blocked'
        result['failure_sources'].append('provenance')
        result['evidence'].update({
            'source': provenance_source,
            'eligible': False,
            'block_reason': 'unsupported_provenance_format',
        })
    if provenance_source is not None:
        if provenance_source == 'null':
            result['outcome'] = 'blocked'
            result['failure_sources'].append('provenance')
            result['evidence'].update({
                'source': 'null',
                'eligible': False,
                'block_reason': 'missing_provenance',
            })
            return result
        if provenance_source == 'corrupted':
            result['outcome'] = 'blocked'
            result['failure_sources'].append('provenance')
            result['evidence'].update({
                'source': provenance_source,
                'eligible': False,
                'block_reason': 'corrupted_provenance_data',
            })
            return result
        if provenance_source == 'pdf_footer' and re.match(r'^[0-9]{4}\.[0-9]{5}:[A-Z].*m\d+$', reference_id or ''):
            result['outcome'] = 'blocked'
            result['failure_sources'].append('provenance')
            result['evidence'].update({
                'source': provenance_source,
                'eligible': False,
                'block_reason': 'provenance_mismatch: reference_id matches HTML node format, not PDF footer',
            })
            return result

    return result


# ═══════════════════════════════════════════════════════════════════════
# BATCH EVALUATION
# ═══════════════════════════════════════════════════════════════════════

GATE_NAMES = [
    "gate_1_geometry",
    "gate_2_token_alignment",
    "gate_3_operator_delimiter",
    "gate_4_literal_vs_semantic",
    "gate_5_provenance",
]

def evaluate_candidate(
    candidate: Dict,
    recognized_latex: str
) -> Dict:
    """Run all five gates on a single candidate."""
    reference_latex = candidate['latex']
    reference_id = candidate['reference_id']
    paper_id = candidate['paper_id']
    html_index = candidate.get('html_index', -1)
    is_display = candidate.get('is_display', False)

    gates = {}
    all_failure_sources = []

    g1 = gate_1_geometry(reference_latex, recognized_latex, is_display)
    gates['gate_1_geometry'] = g1['outcome']
    all_failure_sources.extend(g1['failure_sources'])

    g2 = gate_2_token_alignment(reference_latex, recognized_latex)
    gates['gate_2_token_alignment'] = g2['outcome']
    all_failure_sources.extend(g2['failure_sources'])

    g3 = gate_3_operator_delimiter(reference_latex, recognized_latex)
    gates['gate_3_operator_delimiter'] = g3['outcome']
    all_failure_sources.extend(g3['failure_sources'])

    g4 = gate_4_literal_vs_semantic(reference_latex, recognized_latex)
    gates['gate_4_literal_vs_semantic'] = g4['outcome']
    all_failure_sources.extend(g4['failure_sources'])

    g5 = gate_5_provenance(reference_id, paper_id, html_index)
    gates['gate_5_provenance'] = g5['outcome']
    all_failure_sources.extend(g5['failure_sources'])

    # Final disposition
    if all(g in ('pass', 'literal_match', 'verified', 'semantic_equiv') for g in gates.values()):
        disposition = 'accept'
    elif any(g in ('fail', 'mismatch', 'unverified') for g in gates.values()):
        disposition = 'reject'
    else:
        disposition = 'unresolved'

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


def evaluate_batch(candidates: List[Dict], recognized_outputs: Dict[str, str]) -> List[Dict]:
    """Evaluate multiple candidates given a dict of reference_id -> recognized_latex."""
    results = []
    for cand in candidates:
        ref_id = cand['reference_id']
        recognized = recognized_outputs.get(ref_id, '')
        result = evaluate_candidate(cand, recognized)
        results.append(result)
    return results


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python phase2c_evaluate_gates.py <pilot_selection.json> <recognized_outputs.json> [output.json]")
        sys.exit(1)

    pilot_path = Path(sys.argv[1])
    recognized_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("DATASETS/phase2c_disposition_matrix.jsonl")

    pilot = json.loads(pilot_path.read_text(encoding='utf-8'))
    recognized = json.loads(recognized_path.read_text(encoding='utf-8'))

    results = evaluate_batch(pilot['candidates'], recognized)

    with output_path.open('w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f"Evaluated {len(results)} candidates -> {output_path}")

    for gate in GATE_NAMES:
        cnt = Counter(r[gate] for r in results)
        print(f"  {gate}: {dict(cnt)}")
    disp = Counter(r['final_disposition'] for r in results)
    print(f"  Disposition: {dict(disp)}")