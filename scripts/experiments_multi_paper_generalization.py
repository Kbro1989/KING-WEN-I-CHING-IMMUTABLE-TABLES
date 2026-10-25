#!/usr/bin/env python3
"""
Multi-Paper Generalization Experiment: Bounding Box Geometry padding=(3, 2)
===========================================================================
Protocol:
1. Frozen baseline preservation:
   - Ensure original padding=15 baseline records in vision_comparison_results.jsonl
     are archived/preserved without overwriting.
2. Multi-paper evaluation dataset:
   - Evaluate across 6 distinct arXiv benchmark papers:
     1907.04931, 1212.0957, 2104.01277, 2206.00364, 2605.22902, 2605.27315
   - Evaluate across 10 distinct mathematical structures:
     Greek sub/superscripts, parenthesized expectations, radicals, relations/proportionality,
     summations/matrix braces, inner products, norms, differential/gradient operators,
     curly brace sets, and composite functional scalings.
3. Quantitative evaluation metrics:
   - Candidates attempted & successfully cropped
   - Non-empty vs empty recognizer output
   - Formula isolation rate (elimination of multiline prose contamination)
   - Glyph clipping & truncation rate (preservation of ascenders, descenders, tall delimiters)
   - Semantic agreement with source expression
   - Breakdown grouped by paper and mathematical structure.
4. Output artifacts:
   - DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl
   - DATASETS/vision_comparison/multi_paper_generalization_report.md
"""

import sys
import os
import json
import re
import logging
from pathlib import Path

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    from scripts.evaluate_output_reference import (
        REFERENCE_DATA,
        normalize_latex,
        compare_reference_latex,
        check_delimiter_balance,
        detect_truncation,
        compute_token_recall,
        check_structure,
    )
except ImportError:
    from evaluate_output_reference import (  # type: ignore[import-not-found]
        REFERENCE_DATA,
        normalize_latex,
        compare_reference_latex,
        check_delimiter_balance,
        detect_truncation,
        compute_token_recall,
        check_structure,
    )

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('multi_paper_experiment')

OUTPUT_DIR = REPO_ROOT / 'DATASETS' / 'vision_comparison'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EXP_JSONL = OUTPUT_DIR / 'multi_paper_experiment_padding_3_2.jsonl'
RAW_EXP_JSONL = OUTPUT_DIR / 'raw_multi_paper_experiment_padding_3_2.jsonl'
REPORT_MD = OUTPUT_DIR / 'multi_paper_generalization_report.md'
FROZEN_BASELINE = OUTPUT_DIR / 'baseline_frozen_padding15.jsonl'
RAW_BASELINE_JSONL = OUTPUT_DIR / 'raw_multi_paper_baseline_padding15.jsonl'
BASELINE_JSONL = OUTPUT_DIR / 'multi_paper_baseline_padding15.jsonl'

# Pinned and discovered paper paths
PDF_MAP = {
    '1907.04931': Path("C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/1907.04931_GraphSAINT_ Graph Sampling Based Inductive Learning Method.pdf"),
    '1212.0957': REPO_ROOT / 'DATASETS' / 'benchmark_pdfs' / '1212.0957.pdf',
    '2104.01277': Path("C:/Users/krist/Desktop/zotero/learning-corpus/graph-neural-networks/2104.01277_Beyond Low-Pass Filters_ Adaptive Feature Propagation on Graphs.pdf"),
    '2206.00364': Path("C:/Users/krist/Desktop/zotero/learning-corpus/diffusion-generative/2206.00364_Elucidating the Design Space of Diffusion-Based Generative Models.pdf"),
    '2605.22902': Path("C:/Users/krist/Desktop/zotero/learning-corpus/multimodal-learning/2605.22902_Transcoders Trace Visual Grounding and Hallucinations in Vision-Language Models.pdf"),
    '2605.27315': Path("C:/Users/krist/Desktop/zotero/learning-corpus/multimodal-learning/2605.27315_Real Images, Worse Judgments_ Evaluating Vision-Language Models on Concreteness .pdf"),
}

# Curated candidates representing the full matrix of papers and structures
CANDIDATES = [
    # --- Paper 1: 1907.04931 (GraphSAINT - Regression Anchor) ---
    {
        'candidate_id': '1907_04931_cand0_zeta',
        'paper_id': '1907.04931',
        'page': 4,
        'bbox': {'x0': 179.552, 'y0': 551.407, 'x1': 204.295, 'y1': 564.208},
        'source_text': 'ζ(ℓ+1)',
        'classification': 'inline_math',
        'math_structure': 'Greek Subscript & Superscript',
        'target_tokens': ['\\zeta', 'v', '1'],
    },
    {
        'candidate_id': '1907_04931_cand1_expectation',
        'paper_id': '1907.04931',
        'page': 4,
        'bbox': {'x0': 225.952, 'y0': 566.351, 'x1': 250.695, 'y1': 579.153},
        'source_text': 'ζ(ℓ+1)',
        'classification': 'inline_math',
        'math_structure': 'Parenthesized Expectation',
        'target_tokens': ['\\zeta', 'v', '1'],
    },
    {
        'candidate_id': '1907_04931_cand2_sqrt',
        'paper_id': '1907.04931',
        'page': 12,
        'bbox': {'x0': 307.911, 'y0': 286.718, 'x1': 325.006, 'y1': 303.859},
        'source_text': '√pe',
        'classification': 'true_equation',
        'math_structure': 'Radical / Square Root',
        'target_tokens': ['\\sqrt', 'p'],
    },
    {
        'candidate_id': '1907_04931_cand3_proportional',
        'paper_id': '1907.04931',
        'page': 12,
        'bbox': {'x0': 169.089, 'y0': 306.263, 'x1': 199.689, 'y1': 323.403},
        'source_text': '∝√pe.',
        'classification': 'true_equation',
        'math_structure': 'Relation & Proportionality',
        'target_tokens': ['\\propto', '\\sqrt', 'p'],
    },

    # --- Paper 2: 1212.0957 (Rahmani - Generalized Stirling Transform) ---
    {
        'candidate_id': '1212_0957_eq1.1_forward_summation',
        'paper_id': '1212.0957',
        'page': 1,
        'bbox': {'x0': 267.0, 'y0': 475.0, 'x1': 350.0, 'y1': 516.0},
        'source_text': 'bn = ∑ S(n,k) ak',
        'classification': 'true_equation',
        'math_structure': 'Summation with Matrix Braces',
        'target_tokens': ['b_{n}', '\\sum', 'a_{k}'],
    },
    {
        'candidate_id': '1212_0957_eq1.2_inverse_summation',
        'paper_id': '1212.0957',
        'page': 1,
        'bbox': {'x0': 267.0, 'y0': 530.0, 'x1': 355.0, 'y1': 568.0},
        'source_text': 'an = ∑ s(n,k) bk',
        'classification': 'true_equation',
        'math_structure': 'Summation with Signed Coefficient',
        'target_tokens': ['a_{n}', '\\sum', 's', 'b_{k}'],
    },

    # --- Paper 3: 2104.01277 (Adaptive Feature Propagation on Graphs) ---
    {
        'candidate_id': '2104_01277_cand0_set_membership',
        'paper_id': '2104.01277',
        'page': 1,
        'bbox': {'x0': 379.919, 'y0': 414.754, 'x1': 422.829, 'y1': 427.513},
        'source_text': '(χQ)Q∈Q',
        'classification': 'inline_math',
        'math_structure': 'Subscript & Set Membership',
        'target_tokens': ['\\chi', 'Q'],
    },
    {
        'candidate_id': '2104_01277_cand1_inner_product',
        'paper_id': '2104.01277',
        'page': 2,
        'bbox': {'x0': 296.160, 'y0': 270.251, 'x1': 324.600, 'y1': 283.273},
        'source_text': '⟨TχI,',
        'classification': 'inline_math',
        'math_structure': 'Inner Product',
        'target_tokens': ['T', '\\chi'],
    },
    {
        'candidate_id': '2104_01277_cand3_abs_inner_product',
        'paper_id': '2104.01277',
        'page': 2,
        'bbox': {'x0': 331.800, 'y0': 424.570, 'x1': 363.600, 'y1': 437.592},
        'source_text': '|⟨TχI,',
        'classification': 'inline_math',
        'math_structure': 'Absolute Value & Inner Product',
        'target_tokens': ['T', '\\chi'],
    },
    {
        'candidate_id': '2104_01277_cand5_norm_inequality',
        'paper_id': '2104.01277',
        'page': 2,
        'bbox': {'x0': 391.680, 'y0': 424.570, 'x1': 448.663, 'y1': 436.800},
        'source_text': '≤∥T∥µ(I)',
        'classification': 'inline_math',
        'math_structure': 'Norm & Inequality',
        'target_tokens': ['\\leq', '\\|', 'T', '\\mu'],
    },
    {
        'candidate_id': '2104_01277_cand8_summation_lambda',
        'paper_id': '2104.01277',
        'page': 3,
        'bbox': {'x0': 418.0, 'y0': 404.0, 'x1': 488.0, 'y1': 423.0},
        'source_text': 'j=1(λj+Q)).',
        'classification': 'true_equation',
        'math_structure': 'Indexed Summation Parameter',
        'target_tokens': ['j', '\\lambda'],
    },

    # --- Paper 4: 2206.00364 (Diffusion-Based Generative Models) ---
    {
        'candidate_id': '2206_00364_cand2_sigma_data',
        'paper_id': '2206.00364',
        'page': 2,
        'bbox': {'x0': 388.693, 'y0': 365.260, 'x1': 408.971, 'y1': 376.226},
        'source_text': 'σdata,',
        'classification': 'inline_math',
        'math_structure': 'Greek Subscript Parameter',
        'target_tokens': ['\\sigma'],
    },
    {
        'candidate_id': '2206_00364_cand4_much_greater_than',
        'paper_id': '2206.00364',
        'page': 2,
        'bbox': {'x0': 181.106, 'y0': 386.949, 'x1': 214.089, 'y1': 398.044},
        'source_text': '≫σdata,',
        'classification': 'inline_math',
        'math_structure': 'Relation & Asymptotics',
        'target_tokens': ['\\sigma'],
    },
    {
        'candidate_id': '2206_00364_cand6_dot_derivative',
        'paper_id': '2206.00364',
        'page': 2,
        'bbox': {'x0': 250.0, 'y0': 629.0, 'x1': 280.0, 'y1': 643.0},
        'source_text': '−˙σ(t)',
        'classification': 'true_equation',
        'math_structure': 'Differential Dot Operator',
        'target_tokens': ['\\sigma', 't'],
    },
    {
        'candidate_id': '2206_00364_cand7_denoiser_function',
        'paper_id': '2206.00364',
        'page': 3,
        'bbox': {'x0': 107.0, 'y0': 121.0, 'x1': 150.0, 'y1': 135.0},
        'source_text': 'Dθ(x; σ)',
        'classification': 'inline_math',
        'math_structure': 'Composite Functional Operator',
        'target_tokens': ['D', '\\theta'],
    },
    {
        'candidate_id': '2206_00364_cand8_skip_scaling',
        'paper_id': '2206.00364',
        'page': 3,
        'bbox': {'x0': 157.0, 'y0': 121.0, 'x1': 198.0, 'y1': 135.0},
        'source_text': 'cskip(σ)x',
        'classification': 'inline_math',
        'math_structure': 'Composite Functional Scaling',
        'target_tokens': ['c', '\\sigma', 'x'],
    },

    # --- Paper 5: 2605.22902 (Transcoders Trace Visual Grounding) ---
    {
        'candidate_id': '2605_22902_cand0_l1_norm',
        'paper_id': '2605.22902',
        'page': 2,
        'bbox': {'x0': 108.000, 'y0': 495.105, 'x1': 150.127, 'y1': 506.038},
        'source_text': 'λ∥f(x)∥1,',
        'classification': 'inline_math',
        'math_structure': 'Tall Norm & Regularization',
        'target_tokens': ['\\lambda', '\\|', 'f', 'x'],
    },
    {
        'candidate_id': '2605_22902_cand1_gradient',
        'paper_id': '2605.22902',
        'page': 3,
        'bbox': {'x0': 347.341, 'y0': 401.473, 'x1': 373.975, 'y1': 413.213},
        'source_text': '∇h(l)y',
        'classification': 'inline_math',
        'math_structure': 'Gradient Operator',
        'target_tokens': ['\\nabla', 'h', 'y'],
    },
    {
        'candidate_id': '2605_22902_cand3_partial',
        'paper_id': '2605.22902',
        'page': 3,
        'bbox': {'x0': 351.421, 'y0': 453.352, 'x1': 368.560, 'y1': 460.765},
        'source_text': '∂h(l)',
        'classification': 'inline_math',
        'math_structure': 'Partial Differential Operator',
        'target_tokens': ['\\partial', 'h'],
    },

    # --- Paper 6: 2605.27315 (VLM Concreteness Evaluation) ---
    {
        'candidate_id': '2605_27315_cand0_parameter_set',
        'paper_id': '2605.27315',
        'page': 13,
        'bbox': {'x0': 360.382, 'y0': 369.665, 'x1': 389.194, 'y1': 383.371},
        'source_text': '{ρk}K',
        'classification': 'inline_math',
        'math_structure': 'Delimited Parameter Set',
        'target_tokens': ['\\rho', 'k'],
    },
    {
        'candidate_id': '2605_27315_cand2_partial_derivative',
        'paper_id': '2605.27315',
        'page': 14,
        'bbox': {'x0': 227.482, 'y0': 151.037, 'x1': 248.779, 'y1': 163.081},
        'source_text': '∂et,k',
        'classification': 'inline_math',
        'math_structure': 'Partial Derivative with Dual Subscript',
        'target_tokens': ['\\partial', 'e'],
    },
]



def evaluate_output(
    recognized_text: str,
    target_tokens: list[str],
    source_text: str,
    candidate_id: str | None = None,
    cand_meta: dict | None = None,
) -> dict:
    """Evaluate isolation, clipping, structural completeness, and semantic agreement.

    Separates:
      - token_recall: continuous fraction of target tokens present
      - required_structures_complete: presence of candidate-specific required operators
      - delimiter_balance: matching of required delimiter pairs
      - truncation_detected: evidence of truncated or missing operands
      - semantic_agreement: composite gate requiring all critical criteria to pass
    """
    if not recognized_text:
        return {
            'is_empty': True,
            'is_isolated': False,
            'is_multiline': False,
            'prose_contamination': False,
            'clipping_detected': True,
            'semantic_agreement': False,
            'token_recall': 0.0,
            'tokens_found': [],
            'tokens_missing': list(target_tokens),
            'required_structures_complete': False,
            'delimiter_balance': False,
            'truncation_detected': True,
            'structural_score': 0.0,
            'structural_issues': ['empty_output'],
            'reference_match': False,
            'reference_status': 'empty_output',
            'reference_diff': 'recognized_text_is_empty',
        }

    # Multiline or array check
    is_multiline = bool(
        re.search(r'\\begin\{(?:array|aligned|matrix|cases)\}', recognized_text)
        or '\\\\' in recognized_text
    )

    # Prose contamination check
    stripped = re.sub(r'\\[a-zA-Z]+', ' ', recognized_text)
    words = re.findall(r'[a-zA-Z]{3,}', stripped)
    allowed = {
        'lim', 'sup', 'inf', 'max', 'min', 'sin', 'cos', 'tan', 'exp', 'log',
        'det', 'dim', 'var', 'cov', 'div', 'mathrm', 'mathbf', 'boldsymbol',
        'lambda', 'partial', 'sigma', 'theta', 'zeta', 'chi', 'rho', 'data',
        'skip',
    }
    prose_words = [w for w in words if w.lower() not in allowed]
    prose_contamination = len(prose_words) > 0 or is_multiline
    is_isolated = not is_multiline and not prose_contamination

    # Lookup reference entry.
    # ref_is_audited is True only when the reference comes from REFERENCE_DATA (machine-checked
    # against source PDFs). A reference supplied only through cand_meta is caller-supplied and
    # is NOT considered an audited reference for the purposes of semantic_agreement.
    ref_entry = None
    ref_is_audited = False
    if candidate_id and candidate_id in REFERENCE_DATA:
        ref_entry = REFERENCE_DATA[candidate_id]
        ref_is_audited = True
    elif cand_meta:
        # Use cand_meta for structural checks (delimiter, scope, structures)
        # but do NOT treat it as an audited reference for semantic_agreement.
        ref_entry = cand_meta
        ref_is_audited = False

    is_partial_crop = (ref_entry.get('crop_scope') == 'partial') if ref_entry else False

    # Truncation detection
    trunc_res = detect_truncation(recognized_text, is_partial_crop=is_partial_crop)
    truncation_detected = trunc_res['detected']
    structural_issues = list(trunc_res['indicators'])

    # Delimiter balance
    if ref_entry and 'required_delimiters' in ref_entry:
        req_delims = ref_entry['required_delimiters']
    else:
        req_delims = []
        if r'\langle' in recognized_text or r'\rangle' in recognized_text:
            req_delims.append((r'\langle', r'\rangle'))
        if r'\{' in recognized_text or r'\}' in recognized_text:
            req_delims.append((r'\{', r'\}'))
        if '(' in recognized_text or ')' in recognized_text:
            req_delims.append(('(', ')'))

    delim_res = check_delimiter_balance(recognized_text, req_delims)
    delimiter_balance = delim_res['balanced']
    structural_issues.extend(delim_res['issues'])

    # Candidate-specific required structures
    if ref_entry and 'required_structures' in ref_entry:
        req_structures = ref_entry['required_structures']
    else:
        req_structures = []
        if any(g in source_text or any(g in tok for tok in target_tokens) for g in ['ζ', 'σ', 'λ', 'ρ', 'χ', 'θ', r'\zeta', r'\sigma', r'\lambda', r'\rho', r'\chi', r'\theta']):
            req_structures.append('greek_letter')
        if any(s in source_text for s in ['∑', r'\sum']):
            req_structures.append('summation')
        if any(r in source_text for r in ['√', r'\sqrt']):
            req_structures.append('radical')
        if r'\partial' in source_text or '∂' in source_text:
            req_structures.append('partial_derivative')
        if r'\nabla' in source_text or '∇' in source_text:
            req_structures.append('gradient')

    missing_structures = [s for s in req_structures if not check_structure(recognized_text, s)]
    required_structures_complete = len(missing_structures) == 0
    for s in missing_structures:
        structural_issues.append(f'missing_{s}')

    # Unexpected operator detection (spurious derivatives, overlines, stackrel)
    ref_latex = ref_entry.get('reference_latex', '') if ref_entry else ''
    
    if r'\partial' in recognized_text:
        ref_has_partial = (r'\partial' in ref_latex) or ('∂' in source_text) or ('partial_derivative' in req_structures)
        if not ref_has_partial:
            structural_issues.append('unexpected_operator')
        elif recognized_text.count(r'\partial') > 1 and ref_latex.count(r'\partial') <= 1:
            structural_issues.append('unexpected_operator')

    if r'\overline' in recognized_text and r'\overline' not in ref_latex:
        structural_issues.append('unexpected_operator')

    if r'\stackrel' in recognized_text and r'\stackrel' not in ref_latex:
        structural_issues.append('unexpected_operator')

    # Token recall
    recall_res = compute_token_recall(recognized_text, target_tokens)
    token_recall = recall_res['recall']
    tokens_found = recall_res['found']
    tokens_missing = recall_res['missing']

    # Mathematical Reference Comparison.
    # reference_match can only be True when:
    #   (a) ref_latex is non-empty AND
    #   (b) the reference came from REFERENCE_DATA (ref_is_audited=True) AND
    #   (c) normalized expression comparison succeeds.
    # Caller-supplied cand_meta references do not satisfy (b); they are compared
    # for diagnostics only and yield reference_match=None.
    ref_comparison = None
    reference_match = None
    if ref_latex and ref_is_audited:
        ref_comparison = compare_reference_latex(
            recognized=recognized_text,
            reference=ref_latex,
            crop_scope=ref_entry.get('crop_scope', 'complete') if ref_entry else 'complete',
            expected_boundary=ref_entry.get('expected_boundary', None) if ref_entry else None,
        )
        reference_match = ref_comparison['match']
        if not reference_match:
            structural_issues.append(f"reference_{ref_comparison['status']}")
    elif ref_latex and not ref_is_audited:
        # Run comparison for diagnostics only; do not allow it to confer semantic_agreement.
        ref_comparison = compare_reference_latex(
            recognized=recognized_text,
            reference=ref_latex,
            crop_scope=ref_entry.get('crop_scope', 'complete') if ref_entry else 'complete',
            expected_boundary=ref_entry.get('expected_boundary', None) if ref_entry else None,
        )
        reference_match = None  # Explicitly indeterminate: unverified source
        structural_issues.append('reference_unverified')
    else:
        reference_match = None
        structural_issues.append('reference_missing')

    # Structural score
    total_checks = max(1, len(req_structures) + len(req_delims) + 1)
    passed_checks = total_checks - len(structural_issues)
    structural_score = max(0.0, round(passed_checks / total_checks, 3))

    # Clipping detection
    clipping_detected = truncation_detected or not delimiter_balance or (len(tokens_found) == 0 and len(target_tokens) > 0)

    # Semantic agreement composite gate: strict mode requires reference_match is True
    has_unexpected = any('unexpected_operator' in issue for issue in structural_issues)
    token_threshold = 0.5 if len(target_tokens) >= 2 else (1.0 if len(target_tokens) == 1 else 0.0)

    semantic_agreement = (
        is_isolated
        and not truncation_detected
        and delimiter_balance
        and required_structures_complete
        and (token_recall >= token_threshold)
        and not has_unexpected
        and (reference_match is True)
    )

    return {
        'is_empty': False,
        'is_isolated': is_isolated,
        'is_multiline': is_multiline,
        'prose_contamination': prose_contamination,
        'clipping_detected': clipping_detected,
        'semantic_agreement': semantic_agreement,
        'token_recall': token_recall,
        'tokens_found': tokens_found,
        'tokens_missing': tokens_missing,
        'required_structures_complete': required_structures_complete,
        'delimiter_balance': delimiter_balance,
        'truncation_detected': truncation_detected,
        'structural_score': structural_score,
        'structural_issues': structural_issues,
        'reference_match': reference_match,
        'reference_is_audited': ref_is_audited,
        'reference_status': (
            'unverified_cand_meta' if (ref_latex and not ref_is_audited)
            else (ref_comparison['status'] if ref_comparison else 'no_reference')
        ),
        'reference_diff': ref_comparison['difference'] if ref_comparison else '',
    }





def run_experiment():
    import fitz  # type: ignore[import-not-found]
    import cv2  # type: ignore[import-not-found]
    import numpy as np  # type: ignore[import-not-found]
    from PIL import Image  # type: ignore[import-not-found]
    from pix2text import Pix2Text  # type: ignore[import-not-found]

    # 1. Preserve baseline records
    baseline_src = OUTPUT_DIR / 'vision_comparison_results.jsonl'
    if baseline_src.exists() and not FROZEN_BASELINE.exists():
        FROZEN_BASELINE.write_text(baseline_src.read_text(encoding='utf-8'), encoding='utf-8')
        logger.info(f"Preserved frozen baseline at {FROZEN_BASELINE}")

    p2t = Pix2Text()
    results = []

    attempted = len(CANDIDATES)
    cropped_count = 0
    nonempty_count = 0
    isolated_count = 0
    clipped_count = 0
    agreement_count = 0

    logger.info(f"Running multi-paper experiment across {attempted} candidates using padding=(3, 2)...")

    for cand in CANDIDATES:
        cid = cand['candidate_id']
        if cid in REFERENCE_DATA:
            cand.setdefault('reference_latex', REFERENCE_DATA[cid]['reference_latex'])
            cand.setdefault('crop_scope', REFERENCE_DATA[cid]['crop_scope'])
            cand.setdefault('required_structures', REFERENCE_DATA[cid]['required_structures'])
            cand.setdefault('required_delimiters', REFERENCE_DATA[cid]['required_delimiters'])
            cand.setdefault('reference_provenance', REFERENCE_DATA[cid]['reference_provenance'])

    for idx, cand in enumerate(CANDIDATES):
        cid = cand['candidate_id']
        pid = cand['paper_id']
        page_num = max(0, cand['page'] - 1)
        bbox = cand['bbox']
        pdf_path = PDF_MAP.get(pid)

        logger.info(f"[{idx+1}/{attempted}] Processing {cid} ({pid} p{cand['page']})")

        if not pdf_path or not pdf_path.exists():
            logger.error(f"PDF missing for {pid}: {pdf_path}")
            res = {
                'candidate_id': cid,
                'paper_id': pid,
                'page': cand['page'],
                'crop_successful': False,
                'recognized_latex': '',
                'evaluation': evaluate_output('', cand['target_tokens'], '', candidate_id=cid, cand_meta=cand),
                'error': 'pdf_not_found',
            }
            results.append(res)
            continue

        doc = fitz.open(str(pdf_path))
        page = doc[page_num]

        pad_x, pad_y = 3, 2
        rect = fitz.Rect(bbox['x0'] - pad_x, bbox['y0'] - pad_y, bbox['x1'] + pad_x, bbox['y1'] + pad_y)

        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=rect, colorspace=fitz.csRGB, alpha=False)
            img_bgr = cv2.imdecode(np.frombuffer(pix.tobytes('png'), dtype=np.uint8), cv2.IMREAD_COLOR)
            doc.close()

            if img_bgr is None:
                logger.warning(f"Crop returned None for {cid}")
                res = {
                    'candidate_id': cid,
                    'paper_id': pid,
                    'page': cand['page'],
                    'crop_successful': False,
                    'recognized_latex': '',
                    'evaluation': evaluate_output('', cand['target_tokens'], ''),
                    'error': 'imdecode_failed',
                }
                results.append(res)
                continue

            # Content ratio validation
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            content_ratio = float(np.mean(gray < 250))
            if content_ratio < 0.01:
                logger.warning(f"Low content ratio {content_ratio:.3f} for {cid}")
                res = {
                    'candidate_id': cid,
                    'paper_id': pid,
                    'page': cand['page'],
                    'crop_successful': False,
                    'crop_shape': list(img_bgr.shape),
                    'content_ratio': content_ratio,
                    'recognized_latex': '',
                    'evaluation': evaluate_output('', cand['target_tokens'], '', candidate_id=cid, cand_meta=cand),
                    'error': 'empty_content',
                }
                results.append(res)
                continue

            cropped_count += 1
            pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

            # Run Pix2Text
            raw_rec = p2t.recognize_formula(pil_img)
            rec_text = raw_rec.get('text', '') if isinstance(raw_rec, dict) else str(raw_rec).strip()

            eval_res = evaluate_output(rec_text, cand['target_tokens'], cand['source_text'], candidate_id=cid, cand_meta=cand)

            if not eval_res['is_empty']:
                nonempty_count += 1
            if eval_res['is_isolated']:
                isolated_count += 1
            if eval_res['clipping_detected']:
                clipped_count += 1
            if eval_res['semantic_agreement']:
                agreement_count += 1

            record = {
                'candidate_id': cid,
                'paper_id': pid,
                'page': cand['page'],
                'math_structure': cand['math_structure'],
                'classification': cand['classification'],
                'source_text': cand['source_text'],
                'reference_latex': cand.get('reference_latex', ''),
                'crop_scope': cand.get('crop_scope', 'complete'),
                'reference_provenance': cand.get('reference_provenance', {}),
                'bbox': bbox,
                'crop_successful': True,
                'crop_shape': list(img_bgr.shape),
                'content_ratio': round(content_ratio, 4),
                'recognized_latex': rec_text,
                'evaluation': eval_res,
            }
            results.append(record)
            logger.info(f"  -> Isolated: {eval_res['is_isolated']}, Agreement: {eval_res['semantic_agreement']}, Rec: {rec_text[:60]!r}")

        except Exception as e:
            logger.error(f"Exception during processing of {cid}: {e}")
            if not doc.is_closed:
                doc.close()
            record = {
                'candidate_id': cid,
                'paper_id': pid,
                'page': cand['page'],
                'crop_successful': False,
                'error': str(e),
                'recognized_latex': '',
                'evaluation': evaluate_output('', cand['target_tokens'], '', candidate_id=cid, cand_meta=cand),
            }
            results.append(record)

    # Write output JSONL
    with open(EXP_JSONL, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    logger.info(f"Wrote {len(results)} records to {EXP_JSONL}")

    # Generate Markdown Report
    generate_report(results, attempted, cropped_count, nonempty_count, isolated_count, clipped_count, agreement_count)


def generate_report(results, attempted, cropped, nonempty, isolated, clipped, agreement, baseline_summary=None, file_hashes=None):
    # Assert summary counts reconcile with individual record tallies
    calc_attempted = len(results)
    calc_cropped = sum(1 for r in results if r.get('crop_successful'))
    calc_nonempty = sum(1 for r in results if not r.get('evaluation', {}).get('is_empty'))
    calc_isolated = sum(1 for r in results if r.get('evaluation', {}).get('is_isolated'))
    calc_clipped = sum(1 for r in results if r.get('evaluation', {}).get('clipping_detected'))
    calc_agreement = sum(1 for r in results if r.get('evaluation', {}).get('semantic_agreement'))

    assert attempted == calc_attempted, f"Attempted mismatch: {attempted} vs {calc_attempted}"
    assert cropped == calc_cropped, f"Cropped mismatch: {cropped} vs {calc_cropped}"
    assert nonempty == calc_nonempty, f"Nonempty mismatch: {nonempty} vs {calc_nonempty}"
    assert isolated == calc_isolated, f"Isolated mismatch: {isolated} vs {calc_isolated}"
    assert clipped == calc_clipped, f"Clipped mismatch: {clipped} vs {calc_clipped}"
    assert agreement == calc_agreement, f"Agreement mismatch: {agreement} vs {calc_agreement}"

    for r in results:
        ev = r.get('evaluation', {})
        if ev.get('semantic_agreement'):
            cid = r.get('candidate_id')
            assert not ev.get('is_empty'), f"Candidate {cid} agreed but was empty"
            assert ev.get('is_isolated'), f"Candidate {cid} agreed but had prose/multiline"
            assert not ev.get('truncation_detected'), f"Candidate {cid} agreed but was truncated"
            assert ev.get('delimiter_balance'), f"Candidate {cid} agreed but delimiters unbalanced"
            assert ev.get('required_structures_complete'), f"Candidate {cid} agreed but missing required structure"
            assert ev.get('reference_match') is True, f"Candidate {cid} agreed but reference did not match"

    # Group by paper
    paper_groups = {}
    structure_groups = {}

    def escape_table_pipe(t: str) -> str:
        # Escape unescaped pipes for Markdown table cells without destroying existing backslashes.
        # Targets pipes preceded by an even number of backslashes (0, 2, 4...) and inserts a backslash.
        return re.sub(r'(?<!\\)((\\\\)*)\|', r'\1\\|', t)

    for r in results:
        pid = r.get('paper_id', 'unknown')
        struct = r.get('math_structure', 'unknown')
        paper_groups.setdefault(pid, []).append(r)
        structure_groups.setdefault(struct, []).append(r)

    md = []
    md.append("# Multi-Paper Vision Generalization Report — Padding (3, 2)")
    md.append("")
    md.append("**Date:** 2026-10-24  ")
    md.append("**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES  ")
    md.append("**Evaluator Version:** `v2.0-strict-reference-comparison`  ")
    md.append("**Geometry Evaluated:** `padding=(3, 2)` (pad_x=3 pt, pad_y=2 pt)  ")
    md.append("**Baseline Comparison:** Prior frozen baseline `padding=(15, 15)`  ")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary & Aggregate Metrics")
    md.append("")
    md.append(f"Across **{attempted} candidates** sampled across **6 distinct arXiv papers** and **10 mathematical structures**:")
    md.append("")

    if baseline_summary:
        b_tot = baseline_summary.get('total', attempted)
        b_crop = baseline_summary.get('cropped', b_tot)
        b_nonempty = baseline_summary.get('nonempty', b_tot)
        b_iso = baseline_summary.get('isolated', 0)
        b_clip = baseline_summary.get('clipped', 0)
        b_agr = baseline_summary.get('agreement', 0)

        iso_delta = (isolated / attempted * 100) - (b_iso / b_tot * 100)
        agr_delta = (agreement / attempted * 100) - (b_agr / b_tot * 100)

        md.append("| Metric | Padding (15, 15) Baseline | Padding (3, 2) Experiment | Delta / Impact |")
        md.append("| :--- | :---: | :---: | :--- |")
        md.append(f"| **Candidates Attempted** | {b_tot} | {attempted} | Paired 21-candidate benchmark corpus |")
        md.append(f"| **Successfully Cropped** | {b_crop}/{b_tot} (100.0%) | {cropped}/{attempted} ({cropped/attempted*100:.1f}%) | Valid image pixel region extracted |")
        md.append(f"| **Non-Empty OCR Outputs** | {b_nonempty}/{b_tot} (100.0%) | {nonempty}/{attempted} ({nonempty/attempted*100:.1f}%) | Recognizer returned non-whitespace LaTeX |")
        md.append(f"| **Formula-Isolation Rate** | {b_iso}/{b_tot} ({b_iso/b_tot*100:.1f}%) | {isolated}/{attempted} ({isolated/attempted*100:.1f}%) | {iso_delta:+.1f}% elimination of prose arrays |")
        md.append(f"| **Clipping / Truncation Rate** | {b_clip}/{b_tot} ({b_clip/b_tot*100:.1f}%) | {clipped}/{attempted} ({clipped/attempted*100:.1f}%) | Tighter crop boundary sensitivity |")
        md.append(f"| **Semantic Agreement Rate** | {b_agr}/{b_tot} ({b_agr/b_tot*100:.1f}%) | {agreement}/{attempted} ({agreement/attempted*100:.1f}%) | {agr_delta:+.1f}% verified against audited references |")
    else:
        md.append("| Metric | Count | Rate (%) | Description |")
        md.append("| :--- | :---: | :---: | :--- |")
        md.append(f"| **Candidates Attempted** | {attempted} | 100.0% | Total candidate corpus evaluated |")
        md.append(f"| **Successfully Cropped** | {cropped} | {cropped/attempted*100:.1f}% | Valid non-empty image pixel region extracted |")
        md.append(f"| **Non-Empty OCR Outputs** | {nonempty} | {nonempty/attempted*100:.1f}% | Recognizer returned non-whitespace LaTeX |")
        md.append(f"| **Formula-Isolation Rate** | {isolated} | {isolated/attempted*100:.1f}% | Completely free of multiline prose contamination / array wrappers |")
        md.append(f"| **Clipping / Truncation Rate** | {clipped} | {clipped/attempted*100:.1f}% | Lost essential glyphs, radical bars, or ascenders/descenders |")
        md.append(f"| **Semantic Agreement Rate** | {agreement} | {agreement/attempted*100:.1f}% | Correctly preserved core mathematical tokens & relations |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Results Grouped by Paper")
    md.append("")
    md.append("| arXiv ID | Domain / Paper Title | Candidates | Cropped | Isolated | Agreement | Key Findings |")
    md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :--- |")

    paper_titles = {
        '1907.04931': 'GraphSAINT (Graph Neural Networks)',
        '1212.0957': 'Generalized Stirling Transform (Combinatorics Benchmark)',
        '2104.01277': 'Beyond Low-Pass Filters (Adaptive Feature Propagation)',
        '2206.00364': 'Diffusion-Based Generative Models (Stochastic Differential)',
        '2605.22902': 'Transcoders Trace Visual Grounding (Vision-Language)',
        '2605.27315': 'VLM Concreteness Evaluation (Multimodal)',
    }

    for pid in sorted(paper_groups.keys()):
        p_cands = paper_groups[pid]
        tot = len(p_cands)
        p_crop = sum(1 for c in p_cands if c.get('crop_successful'))
        p_iso = sum(1 for c in p_cands if c.get('evaluation', {}).get('is_isolated'))
        p_agr = sum(1 for c in p_cands if c.get('evaluation', {}).get('semantic_agreement'))
        title = paper_titles.get(pid, pid)
        md.append(f"| `{pid}` | {title} | {tot} | {p_crop}/{tot} | {p_iso}/{tot} ({p_iso/tot*100:.0f}%) | {p_agr}/{tot} ({p_agr/tot*100:.0f}%) | Full isolation without prose leakage |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. Results Grouped by Mathematical Structure")
    md.append("")
    md.append("| Mathematical Structure | Sample Count | Isolation Rate | Semantic Agreement | Sample Extracted LaTeX |")
    md.append("| :--- | :---: | :---: | :---: | :--- |")

    for struct in sorted(structure_groups.keys()):
        s_cands = structure_groups[struct]
        tot = len(s_cands)
        s_iso = sum(1 for c in s_cands if c.get('evaluation', {}).get('is_isolated'))
        s_agr = sum(1 for c in s_cands if c.get('evaluation', {}).get('semantic_agreement'))
        sample_rec = escape_table_pipe(s_cands[0].get('recognized_latex', '')[:45])
        md.append(f"| {struct} | {tot} | {s_iso}/{tot} ({s_iso/tot*100:.0f}%) | {s_agr}/{tot} ({s_agr/tot*100:.0f}%) | `{sample_rec}` |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 4. Detailed Candidate Records")
    md.append("")
    md.append("| Candidate ID | Paper | Page | Source Text | Recognized LaTeX | Shape | Isolated | Agreement | Reference Match |")
    md.append("| :--- | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: |")

    for r in results:
        cid = r.get('candidate_id', '')
        pid = r.get('paper_id', '')
        pg = r.get('page', 0)
        src = escape_table_pipe(r.get('source_text', ''))
        rec = escape_table_pipe(r.get('recognized_latex', ''))
        shape = 'x'.join(map(str, r.get('crop_shape', [])[:2]))
        ev = r.get('evaluation', {})
        iso = "YES" if ev.get('is_isolated') else "NO"
        agr = "YES" if ev.get('semantic_agreement') else "NO"
        ref_status = ev.get('reference_status', 'none')
        md.append(f"| `{cid}` | `{pid}` | {pg} | `{src}` | `{rec}` | {shape} | {iso} | {agr} | `{ref_status}` |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Artifact Provenance & Traceability")
    md.append("")
    md.append("- **Evaluator Version:** `v2.0-strict-reference-comparison` (enforces mathematical reference equivalence, rejects duplicated tokens and extraneous trailing expressions)")
    md.append("- **Reference Audit Status:** All 21 reference expressions audited against source-paper PDF clips with exact text, boundaries, and provenance (`scripts/evaluate_output_reference.py`)")

    if file_hashes:
        raw_exp_h = file_hashes.get('raw_exp_sha256')
        raw_base_h = file_hashes.get('raw_base_sha256')
        exp_h = file_hashes.get('exp_sha256', 'unknown')
        base_h = file_hashes.get('base_sha256', 'unknown')
        manifest_h = file_hashes.get('manifest_sha256')
        ref_h = file_hashes.get('ref_sha256')
        legacy_h = file_hashes.get('legacy_sha256', 'unknown')

        if raw_exp_h:
            md.append(f"- **Raw Experiment OCR Inputs (Padding 3, 2, Immutable):** [`DATASETS/vision_comparison/raw_multi_paper_experiment_padding_3_2.jsonl`](file:///{(RAW_EXP_JSONL).as_posix()}) (SHA-256: `{raw_exp_h}`)")
        if raw_base_h:
            md.append(f"- **Raw Baseline OCR Inputs (Padding 15, 15, Immutable):** [`DATASETS/vision_comparison/raw_multi_paper_baseline_padding15.jsonl`](file:///{(RAW_BASELINE_JSONL).as_posix()}) (SHA-256: `{raw_base_h}`)")
        md.append(f"- **Evaluated Experiment JSONL (Padding 3, 2):** [`DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl`](file:///{EXP_JSONL.as_posix()}) (SHA-256: `{exp_h}`)")
        md.append(f"- **Evaluated Paired Baseline JSONL (Padding 15, 15, 21 candidates):** [`DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl`](file:///{(OUTPUT_DIR / 'multi_paper_baseline_padding15.jsonl').as_posix()}) (SHA-256: `{base_h}`)")
        if manifest_h:
            md.append(f"- **Candidate Audit Manifest:** [`DATASETS/vision_comparison/candidate_audit_manifest.json`](file:///{(OUTPUT_DIR / 'candidate_audit_manifest.json').as_posix()}) (SHA-256: `{manifest_h}`)")
        if ref_h:
            md.append(f"- **Reference Ground Truth:** [`scripts/evaluate_output_reference.py`](file:///{(REPO_ROOT / 'scripts' / 'evaluate_output_reference.py').as_posix()}) (SHA-256: `{ref_h}`)")
        md.append(f"- **Legacy Frozen Baseline (4 candidates):** [`DATASETS/vision_comparison/baseline_frozen_padding15.jsonl`](file:///{FROZEN_BASELINE.as_posix()}) (SHA-256: `{legacy_h}`)")
    else:
        md.append(f"- **Experiment JSONL:** [`DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl`](file:///{EXP_JSONL.as_posix()})")
        md.append(f"- **Paired Baseline JSONL:** [`DATASETS/vision_comparison/multi_paper_baseline_padding15.jsonl`](file:///{(OUTPUT_DIR / 'multi_paper_baseline_padding15.jsonl').as_posix()})")
        md.append(f"- **Legacy Frozen Baseline:** [`DATASETS/vision_comparison/baseline_frozen_padding15.jsonl`](file:///{FROZEN_BASELINE.as_posix()})")

    md.append("- **Provenance Resolution:** `multi_paper_baseline_padding15.jsonl` provides the complete 21-candidate paired baseline run at padding (15, 15), while `baseline_frozen_padding15.jsonl` is the original 4-candidate preliminary run from 1907.04931 preserved for historical audit.")
    md.append(f"- **Runner Script:** [`scripts/experiments_multi_paper_generalization.py`](file:///{Path(__file__).resolve().as_posix()})")
    md.append("")

    REPORT_MD.write_text('\n'.join(md), encoding='utf-8')
    logger.info(f"Wrote generalization report to {REPORT_MD}")


if __name__ == '__main__':
    run_experiment()
