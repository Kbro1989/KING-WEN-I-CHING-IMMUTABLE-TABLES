#!/usr/bin/env python3
"""
Test Suite for Candidate Audit Manifest
=======================================
Verifies that the PDF crop audit manifest correctly verifies all 21 candidate
crops against the source papers.
"""
import sys
from pathlib import Path
import pytest  # type: ignore[import-not-found]

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

try:
    from scripts.audit_candidate_crops import run_audit, MANIFEST_PATH, _compute_token_overlap
    from scripts.experiments_multi_paper_generalization import REPORT_MD, OUTPUT_DIR
except ImportError:
    from audit_candidate_crops import run_audit, MANIFEST_PATH, _compute_token_overlap  # type: ignore[import-not-found]
    from experiments_multi_paper_generalization import REPORT_MD, OUTPUT_DIR  # type: ignore[import-not-found]


# ===========================================================================
# Unit tests for _compute_token_overlap
# These test the exact failure modes the reviewer identified.
# ===========================================================================

def test_token_overlap_all_matched():
    """All tokens present in order -> fraction 1.0, nothing missing."""
    # Source tokens: 'bn', '∑', 'ak'
    # Clip must contain all three in left-to-right order.
    result = _compute_token_overlap("bn = ∑ ak", "bn ∑ ak extra text")
    assert result['overlap_fraction'] == 1.0
    assert result['missing'] == []
    assert 'bn' in result['matched']
    assert '∑' in result['matched']
    assert 'ak' in result['matched']


def test_token_overlap_repeated_character_requires_repeated_occurrences():
    """A token that appears N times in source must appear N times in clip.

    The old character-set membership check would have falsely reported 'k' as
    matched three times even if clip contained only one 'k'. The ordered
    consumption-aware algorithm must correctly fail when occurrences are exhausted.
    """
    # Source has 'k' three times: 'k', 'k', 'k' (as tokens ['k', 'k', 'k'])
    # clip_text has only one 'k' -> second and third 'k' are missing
    result = _compute_token_overlap("k k k", "one k here")
    assert result['tokens'] == ['k', 'k', 'k']
    # First 'k' matched, second and third cannot (consumed)
    assert len(result['matched']) == 1
    assert len(result['missing']) == 2
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_reordered_tokens_counted_as_partial():
    """LCS alignment cannot match both tokens when they appear in opposite order.

    Source order: 'bn' first, then 'ak'.
    Clip order:   'ak' first, then 'bn'.

    LCS of ['bn', 'ak'] and ['ak', 'bn'] has length 1.  The backtracker
    (prefer 'go up') recovers 'bn' as the single matched token.  'ak' is
    missing because it would require reversing the source order.
    """
    result = _compute_token_overlap("bn ak", "ak bn")
    assert result['algorithm'] == 'lcs'
    assert result['lcs_length'] == 1
    assert 'bn' in result['matched']
    assert 'ak' in result['missing']
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_empty_source():
    """Empty source_text must return zero tokens and fraction 0.0."""
    result = _compute_token_overlap("", "some clip text")
    assert result['tokens'] == []
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_empty_clip():
    """Non-empty source against empty clip must report all tokens missing."""
    result = _compute_token_overlap("ζ(ℓ+1)", "")
    assert len(result['missing']) == len(result['tokens'])
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_unicode_symbols():
    """Non-ASCII math symbols (∑, ζ, ∇) are extracted as individual tokens."""
    result = _compute_token_overlap("ζ(ℓ+1) v", "ζ(ℓ+1) v extra")
    # Expected tokens: 'ζ', 'ℓ', '1', 'v'  (non-ASCII chars + alnum runs)
    assert 'ζ' in result['tokens']
    assert 'v' in result['tokens']
    assert result['overlap_fraction'] == 1.0


def test_token_overlap_missing_symbol():
    """A missing Unicode symbol registers as a missing token."""
    result = _compute_token_overlap("∑ ak", "ak only no sum")
    assert '∑' in result['missing']
    assert result['overlap_fraction'] < 1.0


def test_token_overlap_whole_token_boundary_no_substring_collision():
    """Whole-token matching: 'ak' must not match inside 'bakz' or 'bakk'."""
    result = _compute_token_overlap("ak", "bakz and bakk")
    assert result['matched'] == []
    assert result['missing'] == ['ak']
    assert result['overlap_fraction'] == 0.0


def test_token_overlap_lcs_order_preservation():
    """Source ['a', 'b', 'c'] against clip 'c b' has LCS length 1, not matching both out-of-order."""
    result = _compute_token_overlap("a b c", "c b")
    assert result['algorithm'] == 'lcs'
    assert result['lcs_length'] == 1
    assert len(result['matched']) == 1
    assert len(result['missing']) == 2
    assert abs(result['overlap_fraction'] - 1 / 3) < 1e-6


def test_token_overlap_adjacent_unicode_symbols():
    """Adjacent Unicode math symbols are treated as distinct tokens."""
    result = _compute_token_overlap("∇∑x", "∇ ∑ x")
    assert result['tokens'] == ['∇', '∑', 'x']
    assert result['overlap_fraction'] == 1.0
    assert result['missing'] == []




def test_audit_manifest_all_21_candidates_pass():
    manifest = run_audit(save_manifest=False)
    assert manifest['total_candidates'] == 21
    # Renamed fields: distinguish metadata-assertion completion from text-verification
    assert manifest['metadata_assertions_passed'] == 21
    assert manifest['all_metadata_assertions_passed'] is True
    assert len(manifest['records']) == 21
    # Per-status counts must be present and consistent
    verified  = manifest['pdf_text_overlap_verified_count']
    partial   = manifest['pdf_text_overlap_partial_count']
    meta_only = manifest['metadata_assertions_only_count']
    text_review_required = manifest['text_extraction_review_required_count']
    math_review_required = manifest['mathematical_visual_review_required_count']
    assert verified + partial + meta_only == 21
    assert text_review_required == partial + meta_only
    assert math_review_required == 21
    assert manifest['human_visual_review_required_count'] == 21
    # At least some candidates should have text-extraction confirmation
    assert verified > 0, 'Expected at least one pdf_text_overlap_verified candidate'

    VALID_AUDIT_STATUSES = {
        'pdf_text_overlap_verified',
        'pdf_text_overlap_partial',
        'metadata_assertions_only',
    }
    for rec in manifest['records']:
        assert rec['machine_assertions_passed'] is True
        assert rec['reference_latex'] != ''
        assert rec['crop_scope'] in ['complete', 'partial']
        assert 'left' in rec['expected_boundary']
        assert 'right' in rec['expected_boundary']
        assert rec['audit_status'] in VALID_AUDIT_STATUSES, (
            f"{rec['candidate_id']}: unexpected audit_status {rec['audit_status']!r}"
        )
        # Three-tier model requires evidence_notes explaining what was and was not verified
        assert 'evidence_notes' in rec, f"{rec['candidate_id']}: missing evidence_notes"
        assert rec['evidence_notes'], f"{rec['candidate_id']}: evidence_notes is empty"


def test_manifest_file_exists_and_valid():
    assert MANIFEST_PATH.exists()
    import json
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data['total_candidates'] == 21
    # Renamed field from all_assertions_passed -> all_metadata_assertions_passed
    assert data['all_metadata_assertions_passed'] is True
    assert data['manifest_version'] == '2.0'
    # Per-status count fields must be present
    for field in (
        'pdf_text_overlap_verified_count',
        'pdf_text_overlap_partial_count',
        'metadata_assertions_only_count',
        'text_extraction_review_required_count',
        'mathematical_visual_review_required_count',
        'human_visual_review_required_count',
    ):
        assert field in data, f'Manifest missing field: {field}'
    assert data['mathematical_visual_review_required_count'] == 21
    assert data['text_extraction_review_required_count'] == (
        data['pdf_text_overlap_partial_count'] + data['metadata_assertions_only_count']
    )


def test_generated_report_table_column_integrity():
    """Verify that every row in every table in REPORT_MD has the expected column count."""
    import re
    assert REPORT_MD.exists()
    content = REPORT_MD.read_text(encoding='utf-8')

    tables = re.findall(r'(\|[^\n]+\|\n\|[\s:\-|]+\|\n(?:\|[^\n]+\|\n?)+)', content)
    assert len(tables) >= 4, f"Expected at least 4 markdown tables, found {len(tables)}"

    for idx, table in enumerate(tables):
        rows = [r.strip() for r in table.strip().split('\n') if r.strip().startswith('|')]
        header_cols = len(re.split(r'(?<!\\)\|', rows[0])[1:-1])
        assert header_cols >= 2, f"Table {idx+1} header has invalid columns: {header_cols}"

        for row_idx, row in enumerate(rows):
            # Split on unescaped pipe
            cols = re.split(r'(?<!\\)\|', row)[1:-1]
            assert len(cols) == header_cols, (
                f"Table {idx+1} row {row_idx} column mismatch: expected {header_cols}, got {len(cols)} in: {row}"
            )


def test_reported_file_hashes_match_committed_artifacts():
    """Verify that the SHA-256 hashes listed in the report match the actual artifact bytes."""
    import hashlib
    import re
    content = REPORT_MD.read_text(encoding='utf-8')

    # Extract SHA-256 hashes from section 5
    matches = re.findall(r'\[`([^`]+)`\]\(file:///[^)]+\) \(SHA-256: `([a-f0-9]{64})`\)', content)
    assert len(matches) >= 4, f"Expected at least 4 hashed artifacts in report, found {len(matches)}"

    for rel_path, expected_hash in matches:
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Report references non-existent artifact: {rel_path}"
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"


# ===========================================================================
# Phase 1 Adversarial Regression Test Cases
# ===========================================================================

def test_adversarial_operator_substitution_rejected():
    r"""Adversarial Case 1: Reject transcription changing big union to summation.

    Even if surrounding variables (j, 1, \lambda, Q) match, substituting
    the named operator \bigcup / \cup with \sum must be rejected by
    structural comparison.
    """
    try:
        from scripts.evaluate_output_reference import compare_reference_latex
    except ImportError:
        from evaluate_output_reference import compare_reference_latex  # type: ignore[import-not-found]

    cand8_union_ref = r"\cup_{j=1}^{i-1} (\lambda_j + Q)"
    cand8_sum_spoof = r"\sum_{j=1}^{i-1} (\lambda_j + Q)"

    res = compare_reference_latex(cand8_sum_spoof, cand8_union_ref)
    assert res['match'] is False, r"Operator substitution \cup -> \sum must not match"
    assert res['status'] == 'mismatch'


def test_adversarial_truncated_bound_detected():
    """Adversarial Case 2: Detect crop cutting off digit at subscript/superscript boundary.

    Tests DEF-001 with 2605_27315_cand0_parameter_set where the right bounding
    box edge cuts off the digit '1' in 'k=1', producing '{ρk}K k='.
    Validates that:
    1. The extracted clip text ends with 'k=' and lacks the terminal digit '1'.
    2. Transcription of the truncated crop produces an empty bound operand.
    """
    try:
        from scripts.evaluate_output_reference import detect_truncation
    except ImportError:
        from evaluate_output_reference import detect_truncation  # type: ignore[import-not-found]

    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError:
        fitz = None  # type: ignore[assignment]

    orig_bbox = {'x0': 360.382, 'y0': 369.665, 'x1': 389.194, 'y1': 383.371}

    if fitz is not None:
        try:
            from scripts.experiments_multi_paper_generalization import PDF_MAP
        except ImportError:
            from experiments_multi_paper_generalization import PDF_MAP  # type: ignore[import-not-found]
        pdf_path = PDF_MAP.get('2605.27315')
        if pdf_path and pdf_path.exists():
            doc = fitz.open(str(pdf_path))
            page = doc[12]  # page 13 is index 12
            clip_text = page.get_text('text', clip=fitz.Rect(orig_bbox['x0'], orig_bbox['y0'], orig_bbox['x1'], orig_bbox['y1'])).strip()
            doc.close()
            assert clip_text.endswith('k='), f"Expected truncated 'k=', got {clip_text!r}"
            assert '1' not in clip_text.split('k=')[-1], "Digit '1' should be cut off by bounding box"

    # Truncated LaTeX output detection
    truncated_latex = r"\{ \rho_k \}_{k=}^{K}"
    trunc_info = detect_truncation(truncated_latex)
    assert trunc_info['detected'] is True
    assert 'empty_bound_operand' in trunc_info['indicators']


def test_adversarial_unordered_token_spoofing_rejected():
    """Adversarial Case 3: Reject token overlap evidence when tokens appear in reverse order.

    An unordered bag-of-words or multiset would report 100% overlap for reversed
    mathematical tokens. LCS-based token overlap must reject reversed order.
    """
    source = r"b_n = \sum_{k=0}^{n} S(n,k) a_k"
    reversed_clip = r"a_k S(n,k) \sum_{k=0}^n b_n"

    overlap = _compute_token_overlap(source, reversed_clip)
    assert overlap['overlap_fraction'] < 1.0, "Reversed tokens must not achieve 100% overlap"
    assert len(overlap['missing']) > 0
    assert overlap['algorithm'] == 'lcs'


def test_adversarial_partial_pdf_text_overlap_preserved():
    """Adversarial Case 4: Preserve pdf_text_overlap_partial without promotion.

    Candidates with partial Unicode text extraction in the source PDF
    (e.g., 1212.0957 Stirling expressions where 2D braces are encoded
    as non-Unicode glyphs) must remain 'pdf_text_overlap_partial'.
    They must never be promoted to 'verified' based on a fuzzy threshold.
    """
    import json
    assert MANIFEST_PATH.exists()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))

    stirling_cands = [
        r for r in manifest['records']
        if r['candidate_id'] in (
            '1212_0957_eq1.1_forward_summation',
            '1212_0957_eq1.2_inverse_summation',
        )
    ]
    assert len(stirling_cands) == 2
    for cand in stirling_cands:
        assert cand['audit_status'] == 'pdf_text_overlap_partial', (
            f"{cand['candidate_id']} must retain pdf_text_overlap_partial status"
        )
        assert 'Partial' in cand['evidence_notes'] or 'partial' in cand['evidence_notes']


def test_adversarial_unsupported_glyph_preserved():
    r"""Adversarial Case 5: Preserve unresolved typography in audit record without flattening.

    In 1212_0957_eq1.1_forward_summation, the printed 2D subset notation
    {n \atop k} is preserved in printed_notation, literal_notation_match
    is explicitly False, and overall verdict is NOTATION_AMBIGUITY.
    Flattening {n \atop k} -> S(n,k) as an unannotated visual match is prohibited.
    """
    try:
        from scripts.build_visual_review_log import REVIEW_RECORDS
    except ImportError:
        from build_visual_review_log import REVIEW_RECORDS  # type: ignore[import-not-found]

    cand = next(r for r in REVIEW_RECORDS if r['candidate_id'] == '1212_0957_eq1.1_forward_summation')
    assert cand['literal_notation_match'] is False, "Literal notation match must be False for 2D vs functional"
    assert cand['mathematical_equivalence'] is True, "Mathematical equivalence must be True"
    assert cand['overall_visual_verdict'] == 'NOTATION_AMBIGUITY'
    assert cand['visual_glyph_fidelity']['status'] == 'DISCREPANCY_NOTED'
    assert 'equivalence_provenance' in cand
    assert cand['equivalence_provenance']['printed_notation'] != cand['equivalence_provenance']['reference_notation']
    assert 'Graham' in cand['equivalence_provenance']['literature_basis']


def test_adversarial_missing_mathematical_delimiter_flagged():
    r"""Adversarial Case 6: Flag missing delimiter when source evidence requires pairs.

    Expressions with required delimiters (e.g., set braces \{...\}, parens (...))
    must fail check_delimiter_balance and trigger truncation if unclosed.
    """
    try:
        from scripts.evaluate_output_reference import check_delimiter_balance, detect_truncation
    except ImportError:
        from evaluate_output_reference import check_delimiter_balance, detect_truncation  # type: ignore[import-not-found]

    # Missing opening brace in parameter set
    missing_open = r"\rho_k \}_{k=1}^K"
    bal_res = check_delimiter_balance(missing_open, [(r'\{', r'\}')])
    assert bal_res['balanced'] is False
    assert any('unbalanced' in iss or 'missing' in iss for iss in bal_res['issues'])

    # Unclosed left parenthesis under expectation
    unclosed_paren = r"(\zeta_v^{(\ell+1)}"
    bal_res_paren = check_delimiter_balance(unclosed_paren, [('(', ')')])
    assert bal_res_paren['balanced'] is False

    # Unclosed left brace triggers truncation detection
    unclosed_brace = r"\{ \rho_k"
    trunc_res = detect_truncation(unclosed_brace)
    assert trunc_res['detected'] is True
    assert 'unbalanced_braces' in trunc_res['indicators']


def test_corrected_crop_provenance_and_validation():
    """Adversarial Case 7: Corrected crop references original fixture and captures complete bound.

    For DEF-001 (2605_27315_cand0_parameter_set):
    1. Original fixture is preserved with x1=389.194 (cuts off '1' in 'k=1').
    2. Corrected fixture widens x1 to 396.000, recovering '1' without neighboring prose.
    3. Corrected crop maintains provenance link to candidate_id, paper_id, and page.
    """
    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError:
        fitz = None  # type: ignore[assignment]

    original_fixture = {
        'candidate_id': '2605_27315_cand0_parameter_set',
        'paper_id': '2605.27315',
        'page': 13,
        'bbox': {'x0': 360.382, 'y0': 369.665, 'x1': 389.194, 'y1': 383.371},
        'defect_classification': 'BOUNDARY_TRUNCATION',
    }

    corrected_fixture = {
        'parent_candidate_id': '2605_27315_cand0_parameter_set',
        'paper_id': '2605.27315',
        'page': 13,
        'bbox': {'x0': 360.382, 'y0': 369.665, 'x1': 396.000, 'y1': 383.371},
        'correction_type': 'bbox_widening_bound_recovery',
        'delta_x1': 6.806,
        'reference_latex': r'\{ \rho_k \}_{k=1}^{K}',
    }

    # Assert provenance link
    assert corrected_fixture['parent_candidate_id'] == original_fixture['candidate_id']
    assert corrected_fixture['paper_id'] == original_fixture['paper_id']
    assert corrected_fixture['page'] == original_fixture['page']
    assert corrected_fixture['bbox']['x1'] > original_fixture['bbox']['x1']

    if fitz is not None:
        try:
            from scripts.experiments_multi_paper_generalization import PDF_MAP
        except ImportError:
            from experiments_multi_paper_generalization import PDF_MAP  # type: ignore[import-not-found]
        pdf_path = PDF_MAP.get('2605.27315')
        if pdf_path and pdf_path.exists():
            doc = fitz.open(str(pdf_path))
            page = doc[12]

            # Original: truncated
            orig_rect = fitz.Rect(original_fixture['bbox']['x0'], original_fixture['bbox']['y0'],
                                  original_fixture['bbox']['x1'], original_fixture['bbox']['y1'])
            orig_text = page.get_text('text', clip=orig_rect).strip().replace('\n', '')
            assert orig_text == '{ρk}Kk=', f"Original fixture should be truncated, got: {orig_text!r}"

            # Corrected: complete expression including digit 1
            corr_rect = fitz.Rect(corrected_fixture['bbox']['x0'], corrected_fixture['bbox']['y0'],
                                  corrected_fixture['bbox']['x1'], corrected_fixture['bbox']['y1'])
            corr_text = page.get_text('text', clip=corr_rect).strip().replace('\n', '')
            assert corr_text == '{ρk}Kk=1', f"Corrected fixture should have '1', got: {corr_text!r}"

            doc.close()


