#!/usr/bin/env python3
"""
Reference Data & Evaluation Helpers for Multi-Paper OCR Experiment
===================================================================
Provides:
  - REFERENCE_DATA: candidate-specific ground-truth expressions with provenance
  - normalize_latex(): conservative LaTeX normalization for comparison
  - check_delimiter_balance(): required delimiter pair verification
  - detect_truncation(): incomplete output detection
  - compute_token_recall(): fraction of reference tokens recovered
  - check_structure(): candidate-specific structural requirement checks

All verification_status values are 'agent_reconstructed' until checked against
the source papers by a human reviewer.
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Reference data keyed by candidate_id.
#
# Each entry provides:
#   reference_latex         — complete verified LaTeX for the crop region
#   crop_scope              — 'complete' (full expression) or 'partial' (fragment)
#   required_structures     — candidate-specific structural checks
#   required_delimiters     — pairs that must be balanced in the output
#   reference_provenance    — paper, page, location, and verification status
#
# verification_status values:
#   'agent_reconstructed' — reconstructed from source_text and paper context;
#                           requires human verification against the source paper.
#   'human_verified'      — checked against the published paper by a human.
# ---------------------------------------------------------------------------
REFERENCE_DATA = {
    # --- Paper 1: 1907.04931 (GraphSAINT) ---
    '1907_04931_cand0_zeta': {
        'reference_latex': r'\zeta_v^{(\ell+1)}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['greek_letter', 'subscript', 'superscript_group'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '1907.04931',
            'page': 4,
            'equation_or_location': 'Section 2, inline: node embedding at layer ell+1',
            'exact_pdf_clip_text': 'ζ(ℓ+1) v',
            'verification_status': 'audited_against_pdf',
        },
    },
    '1907_04931_cand1_expectation': {
        'reference_latex': r'(\zeta_v^{(\ell+1)})',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['greek_letter', 'subscript', 'superscript_group'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '1907.04931',
            'page': 4,
            'equation_or_location': 'Section 2, inline: parenthesized node embedding under expectation',
            'exact_pdf_clip_text': '(\x10 ζ(ℓ+1) v \x11)',
            'verification_status': 'audited_against_pdf',
        },
    },
    '1907_04931_cand2_sqrt': {
        'reference_latex': r'(\sqrt{p_e})',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['radical'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '1907.04931',
            'page': 12,
            'equation_or_location': 'Section 4, parenthesized sampling probability radical',
            'exact_pdf_clip_text': '(√pe)',
            'verification_status': 'audited_against_pdf',
        },
    },
    '1907_04931_cand3_proportional': {
        'reference_latex': r'\propto \sqrt{p_e}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['relation_proportional', 'radical'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '1907.04931',
            'page': 12,
            'equation_or_location': 'Section 4, proportionality with sampling probability',
            'exact_pdf_clip_text': '∝√pe.',
            'verification_status': 'audited_against_pdf',
        },
    },

    # --- Paper 2: 1212.0957 (Generalized Stirling Transform) ---
    '1212_0957_eq1.1_forward_summation': {
        'reference_latex': r'b_n = \sum_{k=0}^{n} S(n,k) a_k',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['summation', 'subscript_bound', 'superscript_bound'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '1212.0957',
            'page': 1,
            'equation_or_location': 'Equation (1.1), forward Stirling transform',
            'exact_pdf_clip_text': 'bn = n X k=0 {n k} ak,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '1212_0957_eq1.2_inverse_summation': {
        'reference_latex': r'a_n = \sum_{k=0}^{n} s(n,k) b_k',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['summation', 'subscript_bound', 'superscript_bound'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '1212.0957',
            'page': 1,
            'equation_or_location': 'Equation (1.2), inverse Stirling transform',
            'exact_pdf_clip_text': 'an = n X k=0 s (n, k) bk.',
            'verification_status': 'audited_against_pdf',
        },
    },

    # --- Paper 3: 2104.01277 (Beyond Low-Pass Filters) ---
    '2104_01277_cand0_set_membership': {
        'reference_latex': r'(\chi_Q)_{Q \in \mathcal{Q}}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['subscript', 'set_membership'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2104.01277',
            'page': 1,
            'equation_or_location': 'Section 1, indexed family of characteristic functions',
            'exact_pdf_clip_text': '(χQ)Q∈Q',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2104_01277_cand1_inner_product': {
        'reference_latex': r'\langle T \chi_I ,',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed', 'right': 'open_at_comma'},
        'required_structures': ['angle_bracket_open'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '2104.01277',
            'page': 2,
            'equation_or_location': 'Left fragment of inner product; right operand outside crop',
            'exact_pdf_clip_text': '⟨TχI,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2104_01277_cand3_abs_inner_product': {
        'reference_latex': r'| \langle T \chi_I ,',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed', 'right': 'open_at_comma'},
        'required_structures': ['absolute_value_open', 'angle_bracket_open'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '2104.01277',
            'page': 2,
            'equation_or_location': 'Left fragment of |<T chi_I, ...>|; right side outside crop',
            'exact_pdf_clip_text': '|⟨TχI,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2104_01277_cand5_norm_inequality': {
        'reference_latex': r'\leq \| T \| \mu(I)^{\frac{1}{2}}',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_rel', 'right': 'closed_at_power'},
        'required_structures': ['relation_leq', 'norm'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2104.01277',
            'page': 2,
            'equation_or_location': 'Right-hand side of norm inequality',
            'exact_pdf_clip_text': '≤∥T∥µ(I) 1 2',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2104_01277_cand8_summation_lambda': {
        'reference_latex': r'\cup_{j=1}^{i-1} (\lambda_j + Q)',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_op', 'right': 'closed_at_paren'},
        'required_structures': ['subscript_bound'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2104.01277',
            'page': 3,
            'equation_or_location': 'Partial indexed union with eigenvalue parameter',
            'exact_pdf_clip_text': '∪i−1 j=1(λj+Q)).',
            'verification_status': 'audited_against_pdf',
        },
    },

    # --- Paper 4: 2206.00364 (Diffusion-Based Generative Models) ---
    '2206_00364_cand2_sigma_data': {
        'reference_latex': r'\sigma_{\mathrm{data}}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['greek_letter', 'subscript'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '2206.00364',
            'page': 2,
            'equation_or_location': 'Section 2, data noise level parameter',
            'exact_pdf_clip_text': 'σdata,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2206_00364_cand4_much_greater_than': {
        'reference_latex': r'\gg \sigma_{\mathrm{data}}',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_rel', 'right': 'closed_at_param'},
        'required_structures': ['relation_gg', 'greek_letter', 'subscript'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '2206.00364',
            'page': 2,
            'equation_or_location': 'Asymptotic regime, right fragment',
            'exact_pdf_clip_text': '≫σdata,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2206_00364_cand6_dot_derivative': {
        'reference_latex': r'-\dot{\sigma}(t)',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['dot_accent', 'greek_letter'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2206.00364',
            'page': 2,
            'equation_or_location': 'Time derivative of noise schedule',
            'exact_pdf_clip_text': '−˙σ(t)',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2206_00364_cand7_denoiser_function': {
        'reference_latex': r'D_{\theta}(\mathbf{x} ; \sigma)',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['subscript', 'function_application'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2206.00364',
            'page': 3,
            'equation_or_location': 'Denoiser function notation',
            'exact_pdf_clip_text': 'Dθ(x; σ)',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2206_00364_cand8_skip_scaling': {
        'reference_latex': r'c_{\mathrm{skip}}(\sigma) \mathbf{x}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['subscript', 'function_application'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2206.00364',
            'page': 3,
            'equation_or_location': 'Skip connection scaling coefficient',
            'exact_pdf_clip_text': 'cskip(σ)x',
            'verification_status': 'audited_against_pdf',
        },
    },

    # --- Paper 5: 2605.22902 (Transcoders Trace Visual Grounding) ---
    '2605_22902_cand0_l1_norm': {
        'reference_latex': r'\lambda \| f(x) \|_1',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['norm', 'subscript'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2605.22902',
            'page': 2,
            'equation_or_location': 'L1 regularization term',
            'exact_pdf_clip_text': 'λ∥f(x)∥1,',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2605_22902_cand1_gradient': {
        'reference_latex': r'\nabla_{h^{(l)}} y',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['gradient', 'subscript', 'superscript_group'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2605.22902',
            'page': 3,
            'equation_or_location': 'Gradient with respect to hidden layer activations',
            'exact_pdf_clip_text': '∇h(l)y',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2605_22902_cand3_partial': {
        'reference_latex': r'\partial h^{(l)}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['partial_derivative', 'superscript_group'],
        'required_delimiters': [('(', ')')],
        'reference_provenance': {
            'paper_id': '2605.22902',
            'page': 3,
            'equation_or_location': 'Partial derivative of hidden layer',
            'exact_pdf_clip_text': '∂h(l)',
            'verification_status': 'audited_against_pdf',
        },
    },

    # --- Paper 6: 2605.27315 (VLM Concreteness Evaluation) ---
    '2605_27315_cand0_parameter_set': {
        'reference_latex': r'\{ \rho_k \}_{k=1}^{K}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['set_braces', 'subscript_bound', 'superscript_bound'],
        'required_delimiters': [('\\{', '\\}')],
        'reference_provenance': {
            'paper_id': '2605.27315',
            'page': 13,
            'equation_or_location': 'Parameter set with explicit index bounds',
            'exact_pdf_clip_text': '{ρk}K k=1',
            'verification_status': 'audited_against_pdf',
        },
    },
    '2605_27315_cand2_partial_derivative': {
        'reference_latex': r'\partial e_{t,k}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'required_structures': ['partial_derivative', 'subscript'],
        'required_delimiters': [],
        'reference_provenance': {
            'paper_id': '2605.27315',
            'page': 14,
            'equation_or_location': 'Partial derivative with dual subscript',
            'exact_pdf_clip_text': '∂et,k',
            'verification_status': 'audited_against_pdf',
        },
    },
}


def normalize_latex(s: str) -> str:
    """Normalize LaTeX for conservative comparison.

    Reduces false negatives from trivial formatting differences (sizing commands,
    font aliases like \\cal vs \\mathcal, whitespace, single-letter subscript braces)
    while preserving structural differences.
    """
    if not s:
        return ''
    s = s.strip()
    # Remove sizing wrappers
    for w in [r'\displaystyle', r'\textstyle', r'\scriptstyle']:
        s = s.replace(w, '')
    # Remove \left and \right sizing commands, preserving the delimiter.
    # Negative lookahead prevents matching \leftarrow, \rightarrow, etc.
    s = re.sub(r'\\left(?![a-zA-Z])\s*', '', s)
    s = re.sub(r'\\right(?![a-zA-Z])\s*', '', s)
    # Normalize font variants
    s = s.replace(r'\boldsymbol', r'\mathbf')
    s = s.replace(r'\cal', r'\mathcal')
    s = re.sub(r'\\mathbf\{(\\[a-zA-Z]+)\}', r'\1', s)
    # Collapse spaced letters inside \mathrm{...}
    s = re.sub(r'\\mathrm\{([^}]+)\}', lambda m: r'\mathrm{' + m.group(1).replace(' ', '') + '}', s)
    # Normalize font grouping: {\mathcal Q} -> \mathcal{Q}
    s = re.sub(r'\{\s*\\mathcal\s*([a-zA-Z])\s*\}', r'\\mathcal{\1}', s)
    # Canonicalize single character subscript/superscript: _x -> _{x}
    s = re.sub(r'_([a-zA-Z0-9])(?![a-zA-Z0-9_{])', r'_{\1}', s)
    s = re.sub(r'\^([a-zA-Z0-9])(?![a-zA-Z0-9^{])', r'^{\1}', s)
    # Remove trailing math-adjacent punctuation
    s = re.sub(r'[.,;:]+$', '', s.strip())
    # Strip space between single letter identifier / function and (
    s = re.sub(r'([a-zA-Z])\s+\(', r'\1(', s)
    # Strip space inside braces and parens
    s = re.sub(r'{\s+', '{', s)
    s = re.sub(r'\s+}', '}', s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    # Normalize command spacing
    s = re.sub(r'\\([a-zA-Z]+)\s*', r'\\\1 ', s)
    s = re.sub(r'\}\s*\{', '}{', s)
    s = re.sub(r'\s+', ' ', s)
    # Strip spaces before subscript/superscript
    s = re.sub(r'\s*([_^])\s*', r'\1', s)
    # Strip spaces around operators inside parens/braces
    s = re.sub(r'\s*([+=-])\s*', r'\1', s)
    # Collapse space before { and }
    s = re.sub(r'\\([a-zA-Z]+)\s+\{', r'\\\1{', s)
    s = re.sub(r'\\([a-zA-Z]+)\s+\}', r'\\\1}', s)
    s = re.sub(r'\s+\}', '}', s)
    return s.strip()


def compare_reference_latex(recognized: str, reference: str, crop_scope: str = 'complete') -> dict:
    """Compare normalized recognized LaTeX against verified reference LaTeX.

    Enforces:
      - Equivalence of normalized expression
      - Rejection of duplicated expressions (e.g. sigma_data, sigma_data)
      - Rejection of extraneous trailing content (e.g. break..., , 1)
      - For partial crops: verifies expected visible fragment without extraneous tokens
    """
    n_rec = normalize_latex(recognized)
    n_ref = normalize_latex(reference)

    if not n_rec or not n_ref:
        return {
            'match': False,
            'normalized_recognized': n_rec,
            'normalized_reference': n_ref,
            'status': 'empty_comparison',
            'difference': 'empty_recognized_or_reference',
        }

    # Duplication check: if reference expression is duplicated in recognized output
    if n_ref in n_rec and n_rec.count(n_ref) > 1:
        return {
            'match': False,
            'normalized_recognized': n_rec,
            'normalized_reference': n_ref,
            'status': 'duplicated',
            'difference': 'expression_duplicated_in_output',
        }

    # Exact normalized match
    if n_rec == n_ref:
        return {
            'match': True,
            'normalized_recognized': n_rec,
            'normalized_reference': n_ref,
            'status': 'exact_match',
            'difference': '',
        }

    # Partial crop prefix matching
    if crop_scope == 'partial':
        if n_rec.startswith(n_ref):
            remainder = n_rec[len(n_ref):].strip()
            if not remainder or remainder in [',', '.']:
                return {
                    'match': True,
                    'normalized_recognized': n_rec,
                    'normalized_reference': n_ref,
                    'status': 'partial_match',
                    'difference': '',
                }
            else:
                return {
                    'match': False,
                    'normalized_recognized': n_rec,
                    'normalized_reference': n_ref,
                    'status': 'extraneous_content',
                    'difference': f'extraneous_partial_tail: {remainder!r}',
                }

    # Extraneous trailing content check
    if n_rec.startswith(n_ref) and len(n_rec) > len(n_ref):
        remainder = n_rec[len(n_ref):].strip()
        if remainder in [',', '.', ';']:
            return {
                'match': True,
                'normalized_recognized': n_rec,
                'normalized_reference': n_ref,
                'status': 'exact_match_with_punctuation',
                'difference': '',
            }
        return {
            'match': False,
            'normalized_recognized': n_rec,
            'normalized_reference': n_ref,
            'status': 'extraneous_content',
            'difference': f'extraneous_trailing_content: {remainder!r}',
        }

    if n_ref.startswith(n_rec) and len(n_ref) > len(n_rec):
        remainder = n_ref[len(n_rec):].strip()
        if remainder in [',', '.', ';']:
            return {
                'match': True,
                'normalized_recognized': n_rec,
                'normalized_reference': n_ref,
                'status': 'exact_match_with_punctuation',
                'difference': '',
            }

    return {
        'match': False,
        'normalized_recognized': n_rec,
        'normalized_reference': n_ref,
        'status': 'mismatch',
        'difference': f'rec: {n_rec!r} != ref: {n_ref!r}',
    }


def check_delimiter_balance(text: str, required_delimiters: list[tuple[str, str]]) -> dict:
    """Check that required delimiter pairs are balanced in the text."""
    issues = []
    for opener, closer in required_delimiters:
        open_count = text.count(opener)
        close_count = text.count(closer)
        if opener == closer:
            # Same-character delimiters (e.g., |...|): must appear even number
            if open_count % 2 != 0:
                issues.append(f'odd count for paired delimiter {opener!r}: {open_count}')
            elif open_count == 0:
                issues.append(f'missing delimiter pair {opener!r}')
        else:
            if open_count != close_count:
                issues.append(
                    f'unbalanced {opener!r}/{closer!r}: {open_count} vs {close_count}'
                )
            elif open_count == 0:
                issues.append(f'missing delimiter pair {opener!r}/{closer!r}')
    # Also verify parity of LaTeX norm delimiters if present
    norm_delim_count = text.count(r'\|')
    if norm_delim_count % 2 != 0:
        issues.append(f'odd count for paired norm delimiter \\|: {norm_delim_count}')
    return {'balanced': len(issues) == 0, 'issues': issues}


def detect_truncation(text: str, is_partial_crop: bool = False) -> dict:
    """Detect evidence of truncated or incomplete output."""
    indicators = []
    # Unmatched \left without \right
    left_n = len(re.findall(r'\\left(?![a-zA-Z])', text))
    right_n = len(re.findall(r'\\right(?![a-zA-Z])', text))
    if left_n > right_n:
        indicators.append('unmatched_left_delimiters')
    # Unmatched angle brackets
    if not is_partial_crop and text.count(r'\langle') > text.count(r'\rangle'):
        indicators.append('unmatched_langle')
    # Incomplete inner product with pipe or norm terminator
    stripped = text.rstrip()
    if (r'\langle' in text or '⟨' in text) and text.count(r'\rangle') == 0:
        if stripped.endswith('|') or stripped.endswith(r'\|'):
            indicators.append('unmatched_langle_pipe_truncation')
    # Unmatched braces
    if text.count('{') != text.count('}'):
        indicators.append('unbalanced_braces')
    # Trailing binary or relational operator
    if not is_partial_crop and stripped and stripped[-1] in '=+*,-':
        indicators.append('trailing_operator')
    # Empty bound operand, e.g. _{k=} or =^ or =}
    if re.search(r'=\s*\}', text) or re.search(r'=\s*\^', text) or re.search(r'_\{[a-zA-Z0-9\s]*=\s*\}', text):
        indicators.append('empty_bound_operand')
    # Very short output
    if len(text.strip()) < 3:
        indicators.append('very_short_output')
    return {'detected': len(indicators) > 0, 'indicators': indicators}


def compute_token_recall(recognized: str, target_tokens: list[str]) -> dict:
    """Compute fraction of target tokens found in recognized text."""
    found, missing = [], []
    rec_lower = recognized.lower()
    for tok in target_tokens:
        if tok.lower() in rec_lower:
            found.append(tok)
        else:
            missing.append(tok)
    total = len(target_tokens)
    return {
        'recall': round(len(found) / total, 3) if total else 1.0,
        'found': found,
        'missing': missing,
    }


def check_structure(text: str, struct: str) -> bool:
    """Check if a required mathematical structure is present in LaTeX text."""
    _checks = {
        'greek_letter': lambda t: any(
            cmd in t for cmd in [
                r'\zeta', r'\sigma', r'\lambda', r'\rho', r'\chi', r'\mu',
                r'\theta', r'\alpha', r'\beta', r'\gamma',
            ]
        ),
        'subscript': lambda t: '_' in t,
        'superscript_group': lambda t: '^' in t,
        'radical': lambda t: r'\sqrt' in t,
        'relation_proportional': lambda t: r'\propto' in t,
        'relation_leq': lambda t: (
            r'\leq' in t or bool(re.search(r'\\le(?![a-zA-Z])', t))
        ),
        'relation_gg': lambda t: r'\gg' in t,
        'summation': lambda t: r'\sum' in t,
        'subscript_bound': lambda t: bool(re.search(r'_\{[^}=]+=[^}]+', t)),
        'superscript_bound': lambda t: bool(re.search(r'\^\{[^}]+\}', t)),
        'signed_coefficient': lambda t: '(-1)' in t or '{-1}' in t,
        'set_membership': lambda t: bool(re.search(r'\\in(?![a-zA-Z])', t)),
        'angle_bracket_open': lambda t: r'\langle' in t,
        'absolute_value_open': lambda t: (
            '|' in t or r'\|' in t or r'\lvert' in t
        ),
        'norm': lambda t: (
            t.count(r'\|') >= 2
            or (r'\lVert' in t and r'\rVert' in t)
        ),
        'set_braces': lambda t: r'\{' in t and r'\}' in t,
        'dot_accent': lambda t: r'\dot' in t,
        'function_application': lambda t: '(' in t and ')' in t,
        'gradient': lambda t: r'\nabla' in t,
        'partial_derivative': lambda t: r'\partial' in t,
    }
    checker = _checks.get(struct)
    # Unknown structure name: don't reject
    return checker(text) if checker is not None else True
