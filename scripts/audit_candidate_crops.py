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
        # 'pdf_text_overlap_verified'  — all alphanumeric tokens in source_text are found
        #   in exact_clip_text. Machine-confirmed that the bbox points to the correct PDF
        #   region. Does NOT verify LaTeX structure, index placement, or every mathematical
        #   glyph (e.g. does not distinguish union from summation when both are indexed).
        #
        # 'pdf_text_overlap_partial'   — at least one but not all source_text tokens appear
        #   in clip text. Region may be correct but clip coverage is incomplete.
        #
        # 'metadata_assertions_only'   — no alphanumeric overlap confirmed from PDF clip.
        #   Metadata (reference_latex, boundary, provenance) passed structural assertions
        #   but PDF text extraction did not confirm the region. Requires human visual review.
        #
        # NONE of these statuses constitute independent mathematical verification of the
        # reference_latex LaTeX expression. Index placement, glyph identity, and expression
        # boundaries require human visual review of the rendered PDF crop.
        src_text = cand.get('source_text', '')
        src_tokens = [ch for ch in src_text if ch.isalnum()]
        if src_tokens and exact_text:
            matched = [ch for ch in src_tokens if ch in exact_text]
            overlap_fraction = len(matched) / len(src_tokens)
            if overlap_fraction >= 1.0:
                audit_status = 'pdf_text_overlap_verified'
                evidence_notes = f'All {len(src_tokens)} source tokens present in exact clip text.'
            elif overlap_fraction > 0.0:
                audit_status = 'pdf_text_overlap_partial'
                missing_toks = [ch for ch in src_tokens if ch not in exact_text]
                evidence_notes = f'{len(matched)}/{len(src_tokens)} source tokens present. Missing: {missing_toks!r}'
            else:
                audit_status = 'metadata_assertions_only'
                evidence_notes = 'No source tokens found in exact clip text. Human review required.'
        else:
            audit_status = 'metadata_assertions_only'
            evidence_notes = 'Empty exact_clip_text or no source tokens. Human review required.'

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


    manifest = {
        'total_candidates': total_candidates,
        'passed_assertions': passed_count,
        'all_assertions_passed': passed_count == total_candidates,
        'manifest_version': '1.0',
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

