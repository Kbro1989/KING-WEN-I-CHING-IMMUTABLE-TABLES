#!/usr/bin/env python3
"""
Source-to-Visual Provenance Verification Script

Traces one real equation from HTML/MathML source through PDF crop
and into the evaluation record. Verifies each link in the chain.

Usage:
    python scripts/verify_provenance_trace.py
"""

import json
import hashlib
import os
import sys

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_SET_PATH = os.path.join(REPO_ROOT, 'DATASETS', 'provenance_gold_set_1505.05770.json')
HTML_CORPUS_PATH = os.path.join(REPO_ROOT, 'DATASETS', 'arxiv_html_corpus', '1505.05770.json')

def verify_source_pin(gold):
    """Step 1: Verify source pinning."""
    pin = gold['source_pin']
    errors = []

    # Check HTML corpus file exists and hash matches
    if not os.path.exists(HTML_CORPUS_PATH):
        errors.append(f"HTML corpus file missing: {HTML_CORPUS_PATH}")
    else:
        html_data = json.load(open(HTML_CORPUS_PATH))
        if html_data['equation_count'] != pin['html_equation_count']:
            errors.append(f"Equation count mismatch: gold={pin['html_equation_count']}, actual={html_data['equation_count']}")
        if html_data['arxiv_id'] != pin['arxiv_id']:
            errors.append(f"arxiv_id mismatch: gold={pin['arxiv_id']}, actual={html_data['arxiv_id']}")
        # Verify HTML corpus SHA-256
        if 'html_corpus_sha256' in pin:
            actual_hash = sha256_file(HTML_CORPUS_PATH)
            if actual_hash != pin['html_corpus_sha256']:
                errors.append(f"HTML corpus SHA-256 mismatch: gold={pin['html_corpus_sha256']}, actual={actual_hash}")

    # Check PDF exists
    pdf_path = pin['pdf_path']
    if not os.path.exists(pdf_path):
        errors.append(f"PDF missing: {pdf_path}")
    else:
        h = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        if h.hexdigest() != pin['pdf_sha256']:
            errors.append(f"PDF SHA-256 mismatch: gold={pin['pdf_sha256']}, actual={h.hexdigest()}")

    # Check parser exists and hash matches
    parser_path = os.path.join(REPO_ROOT, pin['parser'])
    if not os.path.exists(parser_path):
        errors.append(f"Parser missing: {parser_path}")
    elif 'parser_sha256' in pin:
        actual_hash = sha256_file(parser_path)
        if actual_hash != pin['parser_sha256']:
            errors.append(f"Parser SHA-256 mismatch: gold={pin['parser_sha256']}, actual={actual_hash}")

    return errors

def verify_gold_set_mapping(gold):
    """Step 2: Verify each gold set entry maps to a real HTML equation."""
    errors = []
    html_data = json.load(open(HTML_CORPUS_PATH))

    for gs in gold['gold_set']:
        idx = gs['html_equation_index']
        if idx >= len(html_data['equations']):
            errors.append(f"{gs['gold_id']}: index {idx} out of range (max {len(html_data['equations'])-1})")
            continue

        html_eq = html_data['equations'][idx]
        if html_eq['latex'] != gs['html_latex']:
            errors.append(f"{gs['gold_id']}: LaTeX mismatch at index {idx}")
            print(f"  Expected: {gs['html_latex'][:60]}")
            print(f"  Actual:   {html_eq['latex'][:60]}")

        # Verify source field
        if html_eq['source'] not in ('mathml', 'ltx_math_span', 'ltx_equation_div', 'annotation'):
            errors.append(f"{gs['gold_id']}: unexpected source '{html_eq['source']}'")

    return errors

def verify_pdf_pages(gold):
    """Step 3: Verify PDF page references are valid."""
    errors = []
    pin = gold['source_pin']
    pdf_path = pin['pdf_path']

    try:
        import fitz
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        for gs in gold['gold_set']:
            page_1based = gs['pdf_page']
            page_0based = gs['pdf_page_index_0based']

            if page_1based < 1 or page_1based > total_pages:
                errors.append(f"{gs['gold_id']}: page {page_1based} out of range (1-{total_pages})")
            if page_0based != page_1based - 1:
                errors.append(f"{gs['gold_id']}: 0-based index {page_0based} != {page_1based}-1")

            # Verify bbox has positive area and is within page dimensions
            bbox = gs['pdf_bbox']
            width = bbox['x1'] - bbox['x0']
            height = bbox['y1'] - bbox['y0']
            if width <= 0 or height <= 0:
                errors.append(f"{gs['gold_id']}: bbox has non-positive area ({width:.1f}x{height:.1f})")
            if bbox.get('x0', 0) < 0 or bbox.get('y0', 0) < 0:
                errors.append(f"{gs['gold_id']}: negative bbox coordinates")
            if page_0based < total_pages:
                page = doc[page_0based]
                pw, ph = page.rect.width, page.rect.height
                if bbox['x1'] > pw + 5 or bbox['y1'] > ph + 5:
                    errors.append(f"{gs['gold_id']}: bbox exceeds page dimensions ({pw:.0f}x{ph:.0f})")

            # Check visual status
            if gs.get('visual_status') == 'PENDING_ADJUDICATION':
                print(f"  NOTE: {gs['gold_id']} is PENDING visual adjudication (approximate bbox)")

        doc.close()

    except ImportError:
        errors.append("PyMuPDF (fitz) not available for PDF verification")

    return errors

def main():
    print("=" * 60)
    print("Source-to-Visual Provenance Verification")
    print("=" * 60)

    gold = json.load(open(GOLD_SET_PATH))

    # Step 1: Source pin
    print("\n[Step 1] Source Pinning")
    errors = verify_source_pin(gold)
    if errors:
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: All source pins verified")

    # Step 2: Gold set mapping
    print("\n[Step 2] Gold Set Mapping (HTML <-> PDF)")
    errors = verify_gold_set_mapping(gold)
    if errors:
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print(f"  PASS: All {len(gold['gold_set'])} gold set entries map to valid HTML equations")

    # Step 3: PDF page references
    print("\n[Step 3] PDF Page References")
    errors = verify_pdf_pages(gold)
    if errors:
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print(f"  PASS: All {len(gold['gold_set'])} gold set entries have valid PDF page references")

    # Summary
    print("\n" + "=" * 60)
    print("Provenance Chain Status")
    print("=" * 60)
    print(f"Paper: {gold['paper_id']} ({gold['title']})")
    print(f"HTML equations: {gold['source_pin']['html_equation_count']}")
    print(f"PDF pages: {gold['source_pin']['pdf_pages']}")
    print(f"Gold set size: {len(gold['gold_set'])}")
    print(f"Evaluation: {gold['evaluation_link']['evaluation_status']}")
    print(f"Next step: {gold['evaluation_link']['next_step']}")

    print("\nProvenance chain: HTML MathML -> [GAP: no html_equation_index in candidates] -> PDF crop -> [GAP: no automated association] -> Gate evaluation")

if __name__ == '__main__':
    main()