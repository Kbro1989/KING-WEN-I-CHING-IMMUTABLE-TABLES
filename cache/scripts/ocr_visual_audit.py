import json
import subprocess
import re
from pathlib import Path

render_dir = Path(r'DATASETS/PDF_FIDELITY_RENDERINGS')
tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Collect all pages sorted
all_pages = []
for png in sorted(render_dir.rglob('*.png')):
    all_pages.append(png)

print(f'Total pages to audit: {len(all_pages)}')
print(f'Processing...')

results = []
for png in all_pages:
    rel = png.relative_to(render_dir)
    # Run tesseract, output to stdout
    try:
        proc = subprocess.run(
            [tesseract, str(png), 'stdout', '--psm', '3'],
            capture_output=True, text=True, timeout=60
        )
        text = proc.stdout
        # Count OCR tokens (words + symbols)
        tokens = len(re.findall(r'\S+', text))
        # Detect math-like content
        math_symbols = r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]'
        math_hits = len(re.findall(math_symbols, text, re.UNICODE))
        # Detect special formatting
        has_subscripts = '_' in text
        has_superscripts = '\u00B2' in text or '\u00B3' in text
        # Detect multi-line content (page boundaries)
        line_count = text.count('\n') + 1
        results.append({
            'path': str(rel),
            'paper_id': str(rel).split('_')[0],
            'tokens': tokens,
            'math_hits': math_hits,
            'has_subscripts': has_subscripts,
            'has_superscripts': has_superscripts,
            'char_count': len(text),
            'line_count': line_count,
            'ocr_status': 'success',
            'ocr_preview': text[:300],
        })
    except Exception as e:
        results.append({
            'path': str(rel),
            'paper_id': str(rel).split('_')[0],
            'ocr_status': f'error: {e}',
            'ocr_preview': '',
        })

# Save results
with open('DATASETS/PDF_FIDELITY_RENDERINGS_OCR_RESULTS.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Summary
ok = sum(1 for r in results if r['ocr_status'] == 'success')
err = sum(1 for r in results if r['ocr_status'] != 'success')
total_tokens = sum(r['tokens'] for r in results if r['tokens'] is not None)
total_math = sum(r['math_hits'] for r in results if r['math_hits'] is not None)
total_chars = sum(r['char_count'] for r in results if r['char_count'] is not None)

print(f'Success: {ok}/137')
print(f'Errors: {err}')
print(f'Total tokens: {total_tokens:,}')
print(f'Total math hits: {total_math:,}')
print(f'Total chars: {total_chars:,}')

# Per-paper summary
from collections import Counter
paper_counts = Counter(r['paper_id'] for r in results)
for pid, cnt in sorted(paper_counts.items()):
    ok_c = sum(1 for r in results if r['paper_id'] == pid and r['ocr_status'] == 'success')
    print(f'  {pid}: {cnt} pages, {ok_c} OCR OK')
