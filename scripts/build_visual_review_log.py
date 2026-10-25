#!/usr/bin/env python3
"""
Visual Review Audit Log Generator
=================================
Records per-candidate independent judgments across three axes:
1. Visual glyph fidelity (symbols, accents, font glyphs)
2. Mathematical structure (subscripts, superscripts, grouping, bounds, operator scope)
3. Crop-boundary fidelity (intended expression/fragment scope, open/partial boundaries)

Outputs:
  - DATASETS/vision_comparison/visual_review_audit_log.json
  - DATASETS/vision_comparison/visual_review_audit_log.md
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

from experiments_multi_paper_generalization import CANDIDATES, PDF_MAP
from evaluate_output_reference import REFERENCE_DATA

OUTPUT_DIR = REPO_ROOT / 'DATASETS' / 'vision_comparison'
RENDERS_DIR = OUTPUT_DIR / 'candidate_visual_audit_renders'

REVIEW_RECORDS = [
    {
        'candidate_id': '1907_04931_cand0_zeta',
        'paper_id': '1907.04931',
        'page': 4,
        'declared_reference_latex': r'\zeta_v^{(\ell+1)}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1907_04931_cand0_zeta_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1907_04931_cand0_zeta_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Printed glyphs match Greek zeta (\\zeta), subscript v, and superscript (\\ell+1).'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Node embedding at layer ell+1. Superscript grouping in parentheses is correct.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Clean isolation; no ascender/descender clipping or extraneous adjacent prose.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'None. Baseline padding(15,15) leaked surrounding array text; padding(3,2) achieves clean isolation.',
    },
    {
        'candidate_id': '1907_04931_cand1_expectation',
        'paper_id': '1907.04931',
        'page': 4,
        'declared_reference_latex': r'(\zeta_v^{(\ell+1)})',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1907_04931_cand1_expectation_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1907_04931_cand1_expectation_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Parentheses enclose zeta with subscript v and superscript (\\ell+1).'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Parenthesized embedding factor under expectation operator.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Both outer parentheses cleanly captured without clipping.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'None. Cleanly isolated.',
    },
    {
        'candidate_id': '1907_04931_cand2_sqrt',
        'paper_id': '1907.04931',
        'page': 12,
        'declared_reference_latex': r'(\sqrt{p_e})',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1907_04931_cand2_sqrt_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1907_04931_cand2_sqrt_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Parenthesized radical with radicand p and subscript e.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Square root of sampling probability p_e with outer parentheses.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Radical vinculum and parentheses fully contained within crop.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'None.',
    },
    {
        'candidate_id': '1907_04931_cand3_proportional',
        'paper_id': '1907.04931',
        'page': 12,
        'declared_reference_latex': r'\propto \sqrt{p_e}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1907_04931_cand3_proportional_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1907_04931_cand3_proportional_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Proportionality symbol \\propto distinct from alpha; radical over p_e followed by period.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Binary proportionality relation followed by square root term.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Expression completely captured. Minor trace of numerator pe from line above at top border does not contaminate formula.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'Contains sentence-ending period in source equation.',
    },
    {
        'candidate_id': '1212_0957_eq1.1_forward_summation',
        'paper_id': '1212.0957',
        'page': 1,
        'declared_reference_latex': r'b_n = \sum_{k=0}^{n} S(n,k) a_k',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1212_0957_eq1.1_forward_summation_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1212_0957_eq1.1_forward_summation_context.png',
        'visual_glyph_fidelity': {
            'status': 'DISCREPANCY_NOTED',
            'details': 'Source equation (1.1) visually prints 2D vertical curly braces {n \\atop k} for Stirling numbers of the second kind, NOT functional S(n,k). In PDF font, braces are non-Unicode glyphs.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Forward Stirling transform: b_n equals sum over k from 0 to n of Stirling subset numbers times a_k.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Complete standalone display equation captured cleanly with trailing comma.'
        },
        'overall_visual_verdict': 'NOTATION_AMBIGUITY',
        'ambiguities_or_notes': 'OCR recognized \\biggl\\{\\begin{matrix} {n} \\\\ {k} \\end{matrix} \\biggr\\}, reflecting actual printed typography. Reference was declared as functional S(n,k). Kept as pdf_text_overlap_partial.',
    },
    {
        'candidate_id': '1212_0957_eq1.2_inverse_summation',
        'paper_id': '1212.0957',
        'page': 1,
        'declared_reference_latex': r'a_n = \sum_{k=0}^{n} s(n,k) b_k',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/1212_0957_eq1.2_inverse_summation_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/1212_0957_eq1.2_inverse_summation_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Visually prints a_n = \\sum_{k=0}^n s(n,k) b_k. with lowercase s(n,k) cycle notation.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Inverse Stirling transform with display limits above and below summation.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Complete equation captured with trailing period. Trace of text below at bottom border.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'OCR recognized display limits via \\overset/\\underset, causing evaluator mismatch under strict comparator. Text extraction was partial due to leading a_n encoding.',
    },
    {
        'candidate_id': '2104_01277_cand0_set_membership',
        'paper_id': '2104.01277',
        'page': 1,
        'declared_reference_latex': r'(\chi_Q)_{Q \in \mathcal{Q}}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2104_01277_cand0_set_membership_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2104_01277_cand0_set_membership_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Parenthesized chi_Q with outer subscript Q \\in \\mathcal{Q}.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Indexed family of characteristic functions over cube collection Q.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Cleanly isolated inline formula.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'None. Evaluator confirmed exact match.',
    },
    {
        'candidate_id': '2104_01277_cand1_inner_product',
        'paper_id': '2104.01277',
        'page': 2,
        'declared_reference_latex': r'\langle T \chi_I ,',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed', 'right': 'open_at_comma'},
        'render_path': 'candidate_visual_audit_renders/2104_01277_cand1_inner_product_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2104_01277_cand1_inner_product_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Left angle bracket, operator T, chi with subscript I, comma.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Left operand of inner product pairing; right operand chi_J outside crop.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Right crop edge cuts immediately after comma; leftmost stroke of adjacent chi_J is visible on margin.'
        },
        'overall_visual_verdict': 'INTENDED_PARTIAL_FRAGMENT',
        'ambiguities_or_notes': 'Declared as partial / open_at_comma. OCR hallucinated closing vertical bar \\|, causing boundary_violation rejection.',
    },
    {
        'candidate_id': '2104_01277_cand3_abs_inner_product',
        'paper_id': '2104.01277',
        'page': 2,
        'declared_reference_latex': r'| \langle T \chi_I ,',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed', 'right': 'open_at_comma'},
        'render_path': 'candidate_visual_audit_renders/2104_01277_cand3_abs_inner_product_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2104_01277_cand3_abs_inner_product_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Leading absolute value bar, left angle bracket, T chi_I, comma.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Opening of absolute inner product |<T chi_I, chi_J>|.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Right crop edge cuts at comma; edge stroke of chi_J enters margin.'
        },
        'overall_visual_verdict': 'INTENDED_PARTIAL_FRAGMENT',
        'ambiguities_or_notes': 'Declared as partial / open_at_comma. Correctly rejected by evaluator when OCR added trailing bar.',
    },
    {
        'candidate_id': '2104_01277_cand5_norm_inequality',
        'paper_id': '2104.01277',
        'page': 2,
        'declared_reference_latex': r'\leq \| T \| \mu(I)^{\frac{1}{2}}',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_rel', 'right': 'closed_at_power'},
        'render_path': 'candidate_visual_audit_renders/2104_01277_cand5_norm_inequality_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2104_01277_cand5_norm_inequality_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Relation \\leq, double bar norm \\|T\\|, factor \\mu(I) with exponent 1/2.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Right-hand side of operator norm bound.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Starts at relation \\leq and ends cleanly at exponent 1/2.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'Evaluator confirmed exact match.',
    },
    {
        'candidate_id': '2104_01277_cand8_summation_lambda',
        'paper_id': '2104.01277',
        'page': 3,
        'declared_reference_latex': r'\cup_{j=1}^{i-1} (\lambda_j + Q)',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_op', 'right': 'closed_at_paren'},
        'render_path': 'candidate_visual_audit_renders/2104_01277_cand8_summation_lambda_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2104_01277_cand8_summation_lambda_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Operator is definitively a large UNION \\bigcup, NOT a summation \\sum. Operand contains \\lambda_j + \\mathbb{Q}.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Indexed union with lower bound j=1 and upper bound i-1. Operand is (lambda_j + Q).'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Left boundary begins at union operator. Right boundary contains closing parens and period. Slight prose descender at bottom.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'Crucial verification: candidate name contains legacy word "summation", but visual rendering proves operator is union \\cup / \\bigcup. Reference LaTeX correctly declares \\cup.',
    },
    {
        'candidate_id': '2206_00364_cand2_sigma_data',
        'paper_id': '2206.00364',
        'page': 2,
        'declared_reference_latex': r'\sigma_{\mathrm{data}}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2206_00364_cand2_sigma_data_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2206_00364_cand2_sigma_data_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Greek sigma with text subscript "data", followed by comma.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Standard deviation parameter for training data distribution.'
        },
        'crop_boundary_fidelity': {
            'status': 'PASS',
            'details': 'Formula captured cleanly. Comma included in crop; dash trace on far left.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'OCR hallucinated duplicated token, correctly rejected by evaluator.',
    },
    {
        'candidate_id': '2206_00364_cand4_much_greater_than',
        'paper_id': '2206.00364',
        'page': 2,
        'declared_reference_latex': r'\gg \sigma_{\mathrm{data}}',
        'crop_scope': 'partial',
        'expected_boundary': {'left': 'closed_at_rel', 'right': 'closed_at_param'},
        'render_path': 'candidate_visual_audit_renders/2206_00364_cand4_much_greater_than_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2206_00364_cand4_much_greater_than_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Double relation \\gg followed by sigma_data.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Asymptotic inequality regime.'
        },
        'crop_boundary_fidelity': {
            'status': 'LEAKAGE_NOTED',
            'details': 'Crop contains descender of p( from line above at top-right, and dot ascenders at bottom.'
        },
        'overall_visual_verdict': 'INTENDED_PARTIAL_FRAGMENT',
        'ambiguities_or_notes': 'Prose ascenders caused OCR to emit extraneous trailing breaks/dots.',
    },
    {
        'candidate_id': '2206_00364_cand6_dot_derivative',
        'paper_id': '2206.00364',
        'page': 2,
        'declared_reference_latex': r'-\dot{\sigma}(t)',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2206_00364_cand6_dot_derivative_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2206_00364_cand6_dot_derivative_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Minus sign, sigma with dot accent \\dot{\\sigma}, argument (t).'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Time derivative of diffusion noise schedule.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop contains equals sign = on left and partial stroke of sigma on right.'
        },
        'overall_visual_verdict': 'BOUNDARY_AMBIGUITY',
        'ambiguities_or_notes': 'The crop spans = -\\dot{\\sigma}(t) \\sigma. OCR emitted \\partial=-\\dot{\\sigma}(t)\\partial.',
    },
    {
        'candidate_id': '2206_00364_cand7_denoiser_function',
        'paper_id': '2206.00364',
        'page': 3,
        'declared_reference_latex': r'D_{\theta}(\mathbf{x} ; \sigma)',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2206_00364_cand7_denoiser_function_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2206_00364_cand7_denoiser_function_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Function D with subscript \\theta, bold x, semicolon, sigma.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Denoiser network parameterized by theta.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop includes trailing equals sign = and descenders of prose line above.'
        },
        'overall_visual_verdict': 'BOUNDARY_AMBIGUITY',
        'ambiguities_or_notes': 'OCR recognized overline and trailing =, correctly rejected as boundary_violation.',
    },
    {
        'candidate_id': '2206_00364_cand8_skip_scaling',
        'paper_id': '2206.00364',
        'page': 3,
        'declared_reference_latex': r'c_{\mathrm{skip}}(\sigma) \mathbf{x}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2206_00364_cand8_skip_scaling_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2206_00364_cand8_skip_scaling_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Coefficient c with subscript skip, argument (\\sigma), bold vector x.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Skip connection scaling function.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop contains leading = and trailing + sign from the full equation D = c_skip x + c_out F.'
        },
        'overall_visual_verdict': 'BOUNDARY_AMBIGUITY',
        'ambiguities_or_notes': 'Crop boundary touches surrounding operators.',
    },
    {
        'candidate_id': '2605_22902_cand0_l1_norm',
        'paper_id': '2605.22902',
        'page': 2,
        'declared_reference_latex': r'\lambda \| f(x) \|_1',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2605_22902_cand0_l1_norm_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2605_22902_cand0_l1_norm_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Lambda, norm bars enclosing f(x), subscript 1.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Sparsity regularization term in transcoder objective.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop includes trailing comma and initial stroke of the word "where".'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'OCR emitted extra token from trailing stroke; evaluator correctly rejected as extraneous_content.',
    },
    {
        'candidate_id': '2605_22902_cand1_gradient',
        'paper_id': '2605.22902',
        'page': 3,
        'declared_reference_latex': r'\nabla_{h^{(l)}} y',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2605_22902_cand1_gradient_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2605_22902_cand1_gradient_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Del operator \\nabla, subscript h with parenthesized superscript (l), variable y.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Gradient of scalar output with respect to layer l activations.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop contains closing parenthesis ) on right from enclosing inner product.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'OCR captured the closing parenthesis \\big); evaluator correctly rejected as extraneous_content.',
    },
    {
        'candidate_id': '2605_22902_cand3_partial',
        'paper_id': '2605.22902',
        'page': 3,
        'declared_reference_latex': r'\partial h^{(l)}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2605_22902_cand3_partial_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2605_22902_cand3_partial_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Partial derivative symbol \\partial, variable h with superscript (l).'
        },
        'mathematical_structure': {
            'status': 'PARTIAL_CONTEXT',
            'details': 'Visually the denominator of a fraction \\frac{\\partial y}{\\partial h^{(l)}}; the fraction bar and bottom of y are visible.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Crop cuts horizontally through fraction, isolating denominator.'
        },
        'overall_visual_verdict': 'INTENDED_PARTIAL_FRAGMENT',
        'ambiguities_or_notes': 'Declared as standalone \\partial h^{(l)}, but visually embedded under fraction bar.',
    },
    {
        'candidate_id': '2605_27315_cand0_parameter_set',
        'paper_id': '2605.27315',
        'page': 13,
        'declared_reference_latex': r'\{ \rho_k \}_{k=1}^{K}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2605_27315_cand0_parameter_set_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2605_27315_cand0_parameter_set_context.png',
        'visual_glyph_fidelity': {
            'status': 'TRUNCATION_NOTED',
            'details': 'Set braces with rho_k, superscript K, subscript k=. The lower bound digit "1" is clipped by the right crop bbox.'
        },
        'mathematical_structure': {
            'status': 'PASS',
            'details': 'Finite set of parameter values indexed from k=1 to K.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_CLIPPED',
            'details': 'Bbox right boundary cuts through the subscript "1", leaving only "k=" visible.'
        },
        'overall_visual_verdict': 'BOUNDARY_TRUNCATION',
        'ambiguities_or_notes': 'OCR recognized \\{\\rho_k\\}_{k=}^{K}, matching physical image content. Evaluator correctly rejected as mismatch against declared reference \\{\\rho_k\\}_{k=1}^K.',
    },
    {
        'candidate_id': '2605_27315_cand2_partial_derivative',
        'paper_id': '2605.27315',
        'page': 14,
        'declared_reference_latex': r'\partial e_{t,k}',
        'crop_scope': 'complete',
        'expected_boundary': {'left': 'closed', 'right': 'closed'},
        'render_path': 'candidate_visual_audit_renders/2605_27315_cand2_partial_derivative_crop_pad3_2.png',
        'context_render_path': 'candidate_visual_audit_renders/2605_27315_cand2_partial_derivative_context.png',
        'visual_glyph_fidelity': {
            'status': 'PASS',
            'details': 'Partial derivative symbol \\partial, variable e with dual subscript t,k.'
        },
        'mathematical_structure': {
            'status': 'PARTIAL_CONTEXT',
            'details': 'Denominator of gradient component \\frac{\\partial F}{\\partial e_{t,k}}.'
        },
        'crop_boundary_fidelity': {
            'status': 'BOUNDARY_TOUCH',
            'details': 'Top border contains the horizontal fraction line from the numerator.'
        },
        'overall_visual_verdict': 'CONFIRMED_ACCURATE',
        'ambiguities_or_notes': 'OCR recognized \\overline{{\\partial e_{t,k}}} due to the fraction line; evaluator rejected as mismatch.',
    },
]


def generate_logs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / 'visual_review_audit_log.json'
    md_path = OUTPUT_DIR / 'visual_review_audit_log.md'

    log_data = {
        'audit_title': '21-Candidate Visual Crop Audit Log',
        'audit_date': '2026-10-24',
        'reviewer': 'Antigravity Autonomous Math Reviewer & Human-in-the-Loop Pair',
        'evaluation_axes': [
            'visual_glyph_fidelity',
            'mathematical_structure',
            'crop_boundary_fidelity',
        ],
        'total_candidates_audited': len(REVIEW_RECORDS),
        'summary': {
            'glyph_fidelity_passes': sum(1 for r in REVIEW_RECORDS if r['visual_glyph_fidelity']['status'] == 'PASS'),
            'structure_passes': sum(1 for r in REVIEW_RECORDS if r['mathematical_structure']['status'] == 'PASS'),
            'boundary_passes': sum(1 for r in REVIEW_RECORDS if r['crop_boundary_fidelity']['status'] == 'PASS'),
            'fully_confirmed_exact_reference': sum(1 for r in REVIEW_RECORDS if r['overall_visual_verdict'] == 'CONFIRMED_ACCURATE'),
            'intended_partial_fragments': sum(1 for r in REVIEW_RECORDS if r['overall_visual_verdict'] == 'INTENDED_PARTIAL_FRAGMENT'),
            'boundary_ambiguities_or_truncations': sum(1 for r in REVIEW_RECORDS if 'AMBIGUITY' in r['overall_visual_verdict'] or 'TRUNCATION' in r['overall_visual_verdict'] or 'NOTATION' in r['overall_visual_verdict']),
        },
        'records': REVIEW_RECORDS,
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote visual review audit JSON to {json_path}")

    # Build Markdown table
    md = [
        "# Visual Review Audit Log — 21 Candidates",
        "",
        "**Date:** 2026-10-24  ",
        "**Reviewer:** Antigravity Autonomous Math Reviewer (Machine-Checked Visual Inspection)  ",
        "**Audit Basis:** Rendered 288 DPI PDF Crops vs. Declared Mathematical References  ",
        "**Status:** Provisional Benchmark Ground-Truth Audit  ",
        "",
        "---",
        "",
        "## 1. Audit Summary Across Independent Axes",
        "",
        "| Evaluation Axis | Pass Count | Pass Rate (%) | Criteria |",
        "| :--- | :---: | :---: | :--- |",
        f"| **Visual Glyph Fidelity** | {log_data['summary']['glyph_fidelity_passes']}/21 | {log_data['summary']['glyph_fidelity_passes']/21*100:.1f}% | Visible symbols, accents, and font glyphs correspond to reference |",
        f"| **Mathematical Structure** | {log_data['summary']['structure_passes']}/21 | {log_data['summary']['structure_passes']/21*100:.1f}% | Subscripts, superscripts, bounds, grouping, and operator scope |",
        f"| **Crop Boundary Fidelity** | {log_data['summary']['boundary_passes']}/21 | {log_data['summary']['boundary_passes']/21*100:.1f}% | Matches declared complete or partial/open boundary specification |",
        "",
        "---",
        "",
        "## 2. Per-Candidate Visual Audit Matrix",
        "",
        "| Candidate ID | Declared Reference | Scope / Boundary | Glyph Fidelity | Math Structure | Boundary Fidelity | Overall Verdict |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |",
    ]

    for r in REVIEW_RECORDS:
        cid = r['candidate_id']
        ref = r['declared_reference_latex'].replace('|', '\\|')
        bnd = f"{r['crop_scope']} ({list(r['expected_boundary'].values())[0]})"
        g_stat = r['visual_glyph_fidelity']['status']
        s_stat = r['mathematical_structure']['status']
        b_stat = r['crop_boundary_fidelity']['status']
        verdict = r['overall_visual_verdict']
        md.append(f"| `{cid}` | `{ref}` | {bnd} | {g_stat} | {s_stat} | {b_stat} | `{verdict}` |")

    md.append("")
    md.append("---",)
    md.append("")
    md.append("## 3. Key Forensic Visual Observations")
    md.append("")
    md.append("1. **`2104_01277_cand8_summation_lambda` Operator Identity:** Visually confirmed to be a big union $\\bigcup_{j=1}^{i-1} (\\lambda_j + \\mathbb{Q})$, NOT a summation $\\sum$. The legacy candidate ID is misnamed, but the declared reference LaTeX is mathematically correct.")
    md.append("2. **`1212_0957_eq1.1_forward_summation` Stirling Notation:** Source paper visually prints 2D vertical curly braces $\\left\\{ \\begin{matrix} n \\\\ k \\end{matrix} \\right\\}$ rather than horizontal $S(n,k)$. The PDF text layer uses non-Unicode glyphs (`\\x1a`/`\\x1b`), explaining why automated text extraction is partial.")
    md.append("3. **`1212_0957_eq1.2_inverse_summation` Display Limits:** Source paper visually prints display limits $\\sum_{k=0}^n$ with lowercase Stirling cycle notation $s(n,k)$.")
    md.append("4. **`2605_27315_cand0_parameter_set` Right BBox Truncation:** Physical crop cuts off the subscript bound digit `1`, leaving only $k=$. The OCR model faithfully read what was in the crop.")
    md.append("5. **Fraction Denominators (`2605_22902_cand3`, `2605_27315_cand2`):** Crops contain the horizontal fraction bar touching the top border, causing OCR overline/fraction hallucinations.")
    md.append("")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print(f"Wrote visual review audit Markdown to {md_path}")


if __name__ == '__main__':
    generate_logs()
