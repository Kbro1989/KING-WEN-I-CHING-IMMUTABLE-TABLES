import json
import re
import subprocess
from pathlib import Path

render_dir = Path(r'DATASETS/PDF_FIDELITY_RENDERINGS_ZERO')
tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

all_pages = sorted(render_dir.rglob('*.png'))
print(f'Total pages: {len(all_pages)}')

results = []
for png in all_pages:
    rel = png.relative_to(render_dir)
    try:
        proc = subprocess.run(
            [tesseract, str(png), 'stdout', '--psm', '3'],
            capture_output=True, text=True, timeout=60
        )
        text = proc.stdout
        math_symbols = r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]'
        math_hits = len(re.findall(math_symbols, text, re.UNICODE))
        tokens = len(re.findall(r'\S+', text))
        results.append({
            'paper_id': str(rel).split('_')[0],
            'page': rel.stem.split('_')[-1],
            'tokens': tokens,
            'math_hits': math_hits,
            'char_count': len(text),
            'text_preview': text[:200],
        })
    except Exception as e:
        results.append({'paper_id': str(rel).split('_')[0], 'page': str(rel).stem, 'error': str(e)})

with open('DATASETS/PDF_FIDELITY_RENDERINGS_ZERO_RESULTS.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

ok = sum(1 for r in results if 'error' not in r)
print(f'Success: {ok}/{len(results)}')
for r in results:
    if 'error' not in r:
        print(f'  {r["paper_id"]}: page {r["page"]}, {r["tokens"]} tokens, {r["math_hits"]} math hits, {r["char_count"]} chars')
