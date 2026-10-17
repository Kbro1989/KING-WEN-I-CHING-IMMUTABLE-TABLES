import re
import json
import hashlib
from pathlib import Path
import fitz

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

results = []
for pid in missing:
    matches = [f for f in pdfs if f.name.startswith(pid)]
    if not matches:
        results.append({'paper_id': pid, 'status': 'pdf_not_found'})
        continue

    pdf_path = matches[0]
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

    try:
        doc = fitz.open(str(pdf_path))
        pages = []
        total_chars = 0
        formula_candidates = 0
        for i, page in enumerate(doc):
            text = page.get_text()
            total_chars += len(text)
            pages.append({'page': i + 1, 'char_count': len(text), 'text': text})
            for line in text.split('\n'):
                if re.search(r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]', line):
                    formula_candidates += 1

        results.append({
            'paper_id': pid,
            'status': 'ok',
            'pdf_path': str(pdf_path.relative_to(pdf_dir)),
            'pdf_sha256': pdf_hash,
            'pdf_size': pdf_path.stat().st_size,
            'page_count': len(doc),
            'total_chars': total_chars,
            'formula_candidates': formula_candidates,
            'pages': pages,
        })
        print(f'{pid}: {len(doc)} pages, {total_chars:,} chars, {formula_candidates} formula candidates')
        doc.close()
    except Exception as e:
        results.append({'paper_id': pid, 'status': 'extraction_failed', 'error': str(e)})
        print(f'{pid}: FAILED - {e}')

out = Path('DATASETS/PDF_FALLBACK_8_PAPERS_2026-10-16.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print()
print(f'Saved: {out}')
ok = sum(1 for r in results if r['status'] == 'ok')
print(f'Success: {ok}/8')
