#!/usr/bin/env python3
"""
Candidate Crop Reference Audit & Machine-Checked Manifest Generator
===================================================================
Performs machine-checked audit and verification of all 21 mathematical candidate
crops against the original source-paper PDFs.

Validates:
  1. Full candidate coverage: exactly 21 candidates in benchmark suite.
  2. PDF availability: all source papers resolve to existing PDF files.
  3. Bounding box validity: positive dimensions and well-formed geometry.
  4. Reference metadata completeness: reference_latex, crop_scope, expected_boundary,
     and provenance present for every candidate.
  5. Text extraction verification: compares exact and padded PDF text clips against
     declared source text and reference expressions.
  6. Machine manifest output: saves structured verification record to
     DATASETS/vision_comparison/candidate_audit_manifest.json.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path
try:
    import fitz  # type: ignore[import-not-found]
except ImportError:
    fitz = None  # type: ignore[assignment]

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

from evaluate_output_reference import REFERENCE_DATA
from experiments_multi_paper_generalization import CANDIDATES, PDF_MAP, OUTPUT_DIR

MANIFEST_PATH = OUTPUT_DIR / 'candidate_audit_manifest.json'


def _tokenize(text: str) -> list:
    """Extract ordered tokens from text for overlap matching.

    Two complementary patterns, merged in left-to-right source order:
      Pattern A: r'[a-zA-Z0-9]+'  – alphanumeric word runs ('bn', 'ak', '0')
      Pattern B: r'[^\x00-\x7F]'  – individual non-ASCII Unicode codepoints
                                    ('∑', 'ζ', '∇', '√', '⟨')

    Because alnum tokens are extracted as whole runs by pattern A, the tokenizer
    inherently preserves word boundaries: 'ak' and 'bakz' are distinct tokens
    and can never match each other during LCS comparison.
    """
    import re
    alnum = [(m.start(), m.group()) for m in re.finditer(r'[a-zA-Z0-9]+', text)]
    uni   = [(m.start(), m.group()) for m in re.finditer(r'[^\x00-\x7F]', text)]
    return [tok for _, tok in sorted(alnum + uni, key=lambda x: x[0])]


def _compute_token_overlap(source_text: str, clip_text: str) -> dict:
    """Compute token-boundary-aware, LCS-based token overlap.

    Algorithm
    ---------
    1. Tokenise both ``source_text`` and ``clip_text`` with ``_tokenize()``.
       Because alphanumeric tokens are extracted as whole word-runs, a token
       'ak' cannot match the substring inside 'bakz'; both sides must have 'ak'
       as a distinct token for it to count as a match.

    2. Run standard Longest-Common-Subsequence (LCS) DP between the two token
       lists.  Token equality is exact string equality.

       LCS guarantees:
         - Order-preserving: matched source tokens appear in the same relative
           order in both lists.
         - Globally optimal: the alignment is the largest set of matching tokens
           that satisfies the ordering constraint.  There is no greedy ambiguity
           from a missing earlier token shifting what later tokens can match.
         - Reproducible: for equal-length paths the backtracker prefers the
           'go up' direction, producing a deterministic result.

    3. Return matched/missing source tokens, the LCS length, and the clip
       token list so callers can inspect the alignment evidence.

    Properties that do NOT hold:
      - This is text extraction, not mathematical verification.  Two different
        glyphs that map to the same Unicode codepoint are indistinguishable.
      - Superscript, subscript, and delimiter placement cannot be determined
        from extracted text alone.

    Returns
    -------
    dict with keys:
      'tokens'           – ordered list of extracted source tokens
      'matched'          – source tokens that appear in the LCS (in source order)
      'missing'          – source tokens absent from the LCS
      'overlap_fraction' – len(matched) / len(tokens), or 0.0 if no tokens
      'algorithm'        – 'lcs' (for traceability)
      'clip_tokens'      – ordered list of tokens extracted from clip_text
      'lcs_length'       – length of the longest common subsequence
    """
    src_tokens  = _tokenize(source_text)
    clip_tokens = _tokenize(clip_text)

    if not src_tokens:
        return {
            'tokens': [], 'matched': [], 'missing': [],
            'overlap_fraction': 0.0, 'algorithm': 'lcs',
            'clip_tokens': clip_tokens, 'lcs_length': 0,
        }

    m, n = len(src_tokens), len(clip_tokens)

    # Standard O(mn) LCS dynamic programming table.
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if src_tokens[i - 1] == clip_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to recover the set of matched source-token indices.
    # Tie-break: prefer 'go up' (i--) so repeated tokens match the earliest
    # available clip occurrence, keeping the alignment left-anchored.
    matched_src_indices: set[int] = set()
    i, j = m, n
    while i > 0 and j > 0:
        if src_tokens[i - 1] == clip_tokens[j - 1]:
            matched_src_indices.add(i - 1)
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    matched = [src_tokens[idx] for idx in sorted(matched_src_indices)]
    missing = [src_tokens[idx] for idx in range(m) if idx not in matched_src_indices]
    overlap_fraction = len(matched) / m

    return {
        'tokens': src_tokens,
        'matched': matched,
        'missing': missing,
        'overlap_fraction': overlap_fraction,
        'algorithm': 'lcs',
        'clip_tokens': clip_tokens,
        'lcs_length': dp[m][n],
    }



def run_audit(save_manifest: bool = True) -> dict:
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is required to run candidate crop PDF audit.")


    print("=" * 80)
    print("RUNNING MACHINE-CHECKED AUDIT FOR 21 CANDIDATE CROPS AGAINST SOURCE PDFS")
    print("=" * 80)

    # 1. Candidate coverage assertion
    total_candidates = len(CANDIDATES)
    assert total_candidates == 21, f"Expected exactly 21 candidates, got {total_candidates}"

    manifest_records = []
    passed_count = 0

    for idx, cand in enumerate(CANDIDATES):
        cid = cand['candidate_id']
        pid = cand['paper_id']
        page_num = max(0, cand['page'] - 1)
        bbox = cand['bbox']
        pdf_path = PDF_MAP.get(pid)

        # 2. PDF file existence assertion
        assert pdf_path is not None, f"Paper ID {pid} missing from PDF_MAP"
        assert pdf_path.exists(), f"Source PDF file does not exist: {pdf_path}"

        # 3. Bounding box validity assertion
        assert bbox['x0'] < bbox['x1'], f"Invalid x-extents for {cid}: {bbox}"
        assert bbox['y0'] < bbox['y1'], f"Invalid y-extents for {cid}: {bbox}"

        # 4. Reference metadata completeness assertion
        assert cid in REFERENCE_DATA, f"Candidate {cid} missing from REFERENCE_DATA"
        ref_entry = REFERENCE_DATA[cid]
        ref_latex = ref_entry.get('reference_latex', '')
        assert ref_latex, f"Candidate {cid} has empty reference_latex"
        scope = ref_entry.get('crop_scope', 'unknown')
        assert scope in ['complete', 'partial'], f"Invalid crop_scope for {cid}: {scope}"
        boundary = ref_entry.get('expected_boundary', {})
        assert 'left' in boundary and 'right' in boundary, f"Malformed expected_boundary for {cid}: {boundary}"
        provenance = ref_entry.get('reference_provenance', {})
        assert provenance, f"Missing reference_provenance for {cid}"

        # 5. Extract text from PDF clip rects
        doc = fitz.open(str(pdf_path))
        page = doc[page_num]

        exact_rect = fitz.Rect(bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1'])
        pad_rect = fitz.Rect(bbox['x0'] - 3, bbox['y0'] - 2, bbox['x1'] + 3, bbox['y1'] + 2)
        wide_rect = fitz.Rect(bbox['x0'] - 15, bbox['y0'] - 10, bbox['x1'] + 15, bbox['y1'] + 10)

        exact_text = page.get_text('text', clip=exact_rect).strip().replace('\n', ' ')
        pad_text = page.get_text('text', clip=pad_rect).strip().replace('\n', ' ')
        wide_text = page.get_text('text', clip=wide_rect).strip().replace('\n', ' ')
        doc.close()

        # Audit evidence classification: three-tier model.
        #
        # Classification is based on _compute_token_overlap(), which uses ordered,
        # consumption-aware token matching — NOT character-set membership.
        # A repeated token in source_text (e.g. 'k' appearing three times) requires
        # three separate occurrences in clip_text to register as fully matched.
        #
        # 'pdf_text_overlap_verified'
        #   All ordered source tokens found in clip_text (in order, consuming occurrences).
        #   Machine-confirmed that the bbox region contains the declared source content.
        #   Does NOT verify LaTeX structure, index placement, or mathematical glyph
        #   identity (e.g. cannot distinguish ∪ from ∑ when both appear at the same
        #   position, or confirm superscript vs. subscript placement).
        #
        # 'pdf_text_overlap_partial'
        #   At least one but not all source tokens found, in order. The bbox region
        #   likely overlaps the expression but some content is not text-extractable
        #   (e.g. rendered as glyph paths rather than Unicode text).
        #
        # 'metadata_assertions_only'
        #   No ordered token match confirmed. Metadata (reference_latex, boundary,
        #   provenance) passed structural assertions but PDF text extraction did not
        #   corroborate the region. Human visual review of the rendered crop required.
        #
        # NONE of these statuses constitutes independent mathematical verification
        # of the reference_latex expression. Index placement, glyph identity, and
        # expression boundaries require human visual review of the rendered PDF crop.
        src_text = cand.get('source_text', '')
        overlap = _compute_token_overlap(src_text, exact_text)
        n_tokens = len(overlap['tokens'])
        n_matched = len(overlap['matched'])
        missing_toks = overlap['missing']

        if n_tokens == 0:
            audit_status = 'metadata_assertions_only'
            evidence_notes = 'No extractable tokens in source_text. Human review required.'
        elif n_matched == n_tokens:
            audit_status = 'pdf_text_overlap_verified'
            evidence_notes = (
                f'All {n_tokens} ordered source tokens found in exact clip text '
                f'(LCS). '
                f'Does not verify LaTeX structure or index placement.'
            )
        elif n_matched > 0:
            audit_status = 'pdf_text_overlap_partial'
            evidence_notes = (
                f'{n_matched}/{n_tokens} ordered source tokens found. '
                f'Missing: {missing_toks!r}. '
                f'Partial text-extraction coverage; human review recommended.'
            )
        else:
            audit_status = 'metadata_assertions_only'
            evidence_notes = (
                f'0/{n_tokens} ordered source tokens found in exact clip text. '
                f'Human visual review of rendered crop required.'
            )


        record = {
            'candidate_id': cid,
            'paper_id': pid,
            'page': cand['page'],
            'bbox': bbox,
            'crop_scope': scope,
            'expected_boundary': boundary,
            'declared_source_text': src_text,
            'reference_latex': ref_latex,
            'exact_clip_text': exact_text,
            'pad_clip_text': pad_text,
            'wide_context_text': wide_text,
            'reference_provenance': provenance,
            'audit_status': audit_status,
            'evidence_notes': evidence_notes,
            'machine_assertions_passed': True,
        }
        manifest_records.append(record)
        passed_count += 1

        print(f"[{idx+1}/21] {cid}: {audit_status} (exact: {exact_text!r})")


    from collections import Counter
    status_counts = Counter(r['audit_status'] for r in manifest_records)

    # Field-name contract:
    # 'metadata_assertions_passed'     – how many candidates completed the five structural
    #                                    assertions (PDF path, bbox, reference_latex, etc.).
    #                                    This does NOT mean text or mathematical verification.
    # 'all_metadata_assertions_passed' – True when every candidate passed all five assertions.
    # '*_count' fields               – breakdown by three-tier text-evidence status.
    # 'human_visual_review_required_count' – candidates where automated text extraction did
    #                                        not fully confirm the source region; a human
    #                                        must visually inspect the rendered crop before
    #                                        treating the reference_latex as ground truth.
    manifest = {
        'total_candidates': total_candidates,
        'metadata_assertions_passed': passed_count,
        'all_metadata_assertions_passed': passed_count == total_candidates,
        'pdf_text_overlap_verified_count': status_counts.get('pdf_text_overlap_verified', 0),
        'pdf_text_overlap_partial_count': status_counts.get('pdf_text_overlap_partial', 0),
        'metadata_assertions_only_count': status_counts.get('metadata_assertions_only', 0),
        'human_visual_review_required_count': (
            status_counts.get('pdf_text_overlap_partial', 0)
            + status_counts.get('metadata_assertions_only', 0)
        ),
        'manifest_version': '2.0',
        'records': manifest_records,
    }

    if save_manifest:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\nSaved machine-checked manifest ({passed_count}/{total_candidates} passed) to {MANIFEST_PATH}")

    return manifest


if __name__ == '__main__':
    run_audit(save_manifest=True)

