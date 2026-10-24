#!/usr/bin/env python3
"""
Audit all 21 candidate crops directly against the source PDFs.
Prints:
  - Candidate ID
  - Paper ID, Page, BBox
  - Exact text extracted from PDF at bbox
  - Padded text extracted at bbox + (3, 2)
  - Current reference_latex in REFERENCE_DATA
  - Current recognized_latex from OCR
"""
import sys
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
from experiments_multi_paper_generalization import CANDIDATES, PDF_MAP

def audit():
    print("=" * 80)
    print("AUDITING 21 CANDIDATES AGAINST SOURCE PDFS")
    print("=" * 80)

    for idx, cand in enumerate(CANDIDATES):
        cid = cand['candidate_id']
        pid = cand['paper_id']
        page_num = max(0, cand['page'] - 1)
        bbox = cand['bbox']
        pdf_path = PDF_MAP.get(pid)

        doc = fitz.open(str(pdf_path))
        page = doc[page_num]

        exact_rect = fitz.Rect(bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1'])
        pad_rect = fitz.Rect(bbox['x0'] - 3, bbox['y0'] - 2, bbox['x1'] + 3, bbox['y1'] + 2)
        wide_rect = fitz.Rect(bbox['x0'] - 15, bbox['y0'] - 10, bbox['x1'] + 15, bbox['y1'] + 10)

        exact_text = page.get_text('text', clip=exact_rect).strip().replace('\n', ' ')
        pad_text = page.get_text('text', clip=pad_rect).strip().replace('\n', ' ')
        wide_text = page.get_text('text', clip=wide_rect).strip().replace('\n', ' ')

        doc.close()

        ref_entry = REFERENCE_DATA.get(cid, {})
        ref_latex = ref_entry.get('reference_latex', 'MISSING')
        scope = ref_entry.get('crop_scope', 'unknown')

        print(f"\n--- [{idx+1}/21] {cid} ({pid} p{cand['page']}) ---")
        print(f"  BBox: {bbox}")
        print(f"  Crop scope: {scope}")
        print(f"  Exact clip text: {exact_text!r}")
        print(f"  Pad(3,2) clip text: {pad_text!r}")
        print(f"  Wide(15,10) context: {wide_text!r}")
        print(f"  Declared source_text: {cand['source_text']!r}")
        print(f"  Current reference_latex: {ref_latex!r}")

if __name__ == '__main__':
    audit()
