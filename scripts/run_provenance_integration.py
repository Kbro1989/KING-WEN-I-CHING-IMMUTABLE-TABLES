#!/usr/bin/env python3
"""
Source-to-Visual Integration Run

Runs the complete provenance pipeline on the gold set:
  HTML LaTeX -> PDF crop -> Pix2Text OCR -> Gate evaluation

Usage:
    python scripts/run_provenance_integration.py

Requires: PyMuPDF (fitz), Pix2Text, frozen gate library at fe2843963e
"""

import json
import hashlib
import os
import sys
import subprocess
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_SET_PATH = os.path.join(REPO_ROOT, 'DATASETS', 'provenance_gold_set_1505.05770.json')
HTML_CORPUS_PATH = os.path.join(REPO_ROOT, 'DATASETS', 'arxiv_html_corpus', '1505.05770.json')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'DATASETS', 'provenance_integration_run')
FROZEN_COMMIT = 'fe2843963e66c9131ebd442ce05b8e84b90f4374'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def crop_pdf_region(pdf_path, page_0based, bbox, output_path):
    """Crop a PDF region and save as PNG. Returns crop metadata."""
    import fitz
    doc = fitz.open(pdf_path)
    page = doc[page_0based]
    if isinstance(bbox, (list, tuple)):
        rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
    else:
        rect = fitz.Rect(bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1'])
    # Add small padding
    rect = rect + (-2, -2, 2, 2)
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect)
    pix.save(output_path)
    doc.close()

    # Compute crop hash
    crop_hash = sha256_file(output_path)
    return {
        'crop_path': output_path,
        'crop_bbox': bbox,
        'crop_sha256': crop_hash,
        'crop_dimensions': {'width': pix.width, 'height': pix.height},
        'dpi': 216,  # 3x scale of 72 DPI
    }


def run_ocr(crop_path):
    """Run Pix2Text OCR on a crop. Returns OCR result."""
    try:
        from pix2text import Pix2Text
        p2t = Pix2Text.from_config()
        result = p2t.recognize(crop_path)
        return {
            'status': 'success',
            'text': str(result),
            'confidence': getattr(result, 'confidence', None),
            'method': 'pix2text',
        }
    except Exception as e:
        return {
            'status': 'error',
            'text': '',
            'error': str(e),
            'method': 'pix2text',
        }


def run_gate_evaluation(reference_latex, ocr_text, html_index=-1, gold_id='unknown'):
    """Run frozen gate library evaluation on reference vs OCR output."""
    # Load gate library from frozen commit
    try:
        import subprocess
        gate_code = subprocess.run(
            ['git', 'show', f'{FROZEN_COMMIT}:scripts/phase2c_gate_library.py'],
            capture_output=True, text=True, cwd=REPO_ROOT
        ).stdout
        # Write to temp file and import
        temp_path = os.path.join(REPO_ROOT, 'scripts', '_frozen_gate_lib.py')
        with open(temp_path, 'w') as f:
            f.write(gate_code)
        sys.path.insert(0, os.path.join(REPO_ROOT, 'scripts'))
        import _frozen_gate_lib as gate_lib
        # Build candidate dict for evaluate_candidate
        candidate = {
            'latex': reference_latex,
            'reference_id': f'GS-{gold_id}',
            'paper_id': '1505.05770',
            'html_index': html_index,
            'is_display': False,
        }
        result = gate_lib.evaluate_candidate(candidate, ocr_text)
        os.remove(temp_path)
        return result
    except Exception as e:
        return {'error': str(e), 'status': 'gate_evaluation_failed'}


def main():
    print("=" * 60)
    print("Source-to-Visual Integration Run")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    gold = json.load(open(GOLD_SET_PATH))
    pin = gold['source_pin']

    pdf_path = pin['pdf_path']
    results = []

    # Process VERIFIED and CORRECTED entries (CORRECTED = bbox fixed, pending OCR verification)
    verified_entries = [gs for gs in gold['gold_set'] if gs.get('visual_status') in ('VERIFIED', 'CORRECTED - pending OCR verification')]
    pending_entries = [gs for gs in gold['gold_set'] if gs.get('visual_status') not in ('VERIFIED', 'CORRECTED - pending OCR verification')]

    print(f"\nProcessing {len(verified_entries)} VERIFIED equations")
    print(f"Skipping {len(pending_entries)} PENDING equations (GS-005)")

    for gs in verified_entries:
        gold_id = gs['gold_id']
        print(f"\n--- {gold_id}: HTML Eq {gs['html_equation_index']} -> PDF Page {gs['pdf_page']} ---")

        result = {
            'gold_id': gold_id,
            'html_equation_index': gs['html_equation_index'],
            'html_latex': gs['html_latex'],
            'pdf_page': gs['pdf_page'],
            'pdf_page_0based': gs['pdf_page_index_0based'],
            'pdf_bbox': gs['pdf_bbox'],
            'equation_type': gs['equation_type'],
            'visual_status': gs['visual_status'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # Step 1: Crop PDF region
        crop_filename = f"{gold_id}_crop.png"
        crop_path = os.path.join(OUTPUT_DIR, crop_filename)
        try:
            crop_meta = crop_pdf_region(pdf_path, gs['pdf_page_index_0based'], gs['pdf_bbox'], crop_path)
            result['crop'] = crop_meta
            print(f"  Crop: {crop_meta['crop_dimensions']['width']}x{crop_meta['crop_dimensions']['height']} -> {crop_path}")
            print(f"  Crop SHA-256: {crop_meta['crop_sha256']}")
        except Exception as e:
            result['crop'] = {'error': str(e)}
            print(f"  Crop ERROR: {e}")

        # Step 2: Run OCR
        if 'crop' in result and 'error' not in result['crop']:
            ocr_result = run_ocr(crop_path)
            result['ocr'] = ocr_result
            print(f"  OCR status: {ocr_result['status']}")
            if ocr_result['status'] == 'success':
                print(f"  OCR text: {ocr_result['text'][:100]}...")
            else:
                print(f"  OCR error: {ocr_result.get('error', 'unknown')}")
        else:
            result['ocr'] = {'status': 'skipped', 'reason': 'crop failed'}

        # Step 3: Gate evaluation
        if result.get('ocr', {}).get('status') == 'success':
            ocr_text = result['ocr']['text']
            gate_result = run_gate_evaluation(gs['html_latex'], ocr_text, gs['html_equation_index'], gs['gold_id'])
            result['gate_evaluation'] = gate_result
            print(f"  Gate evaluation: {gate_result.get('status', 'unknown')}")
        else:
            result['gate_evaluation'] = {'status': 'skipped', 'reason': 'OCR failed or skipped'}

        results.append(result)

    # Save results
    results_path = os.path.join(OUTPUT_DIR, 'integration_run_results.jsonl')
    with open(results_path, 'w') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')

    summary_path = os.path.join(OUTPUT_DIR, 'integration_run_summary.json')
    summary = {
        'paper_id': gold['paper_id'],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'frozen_commit': FROZEN_COMMIT,
        'total_equations': len(gold['gold_set']),
        'verified_processed': len(verified_entries),
        'pending_skipped': len(pending_entries),
        'pending_ids': [gs['gold_id'] for gs in pending_entries],
        'results': results,
    }
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("Integration Run Complete")
    print("=" * 60)
    print(f"Results: {results_path}")
    print(f"Summary: {summary_path}")
    print(f"Crops: {OUTPUT_DIR}/GS-XXX_crop.png")
    print(f"Verified processed: {len(verified_entries)}")
    print(f"Pending skipped: {len(pending_entries)} ({', '.join(gs['gold_id'] for gs in pending_entries)})")


if __name__ == '__main__':
    main()