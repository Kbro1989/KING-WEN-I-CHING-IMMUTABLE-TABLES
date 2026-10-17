import json
from pathlib import Path

# Load OCR results for 2305.08038
with open('DATASETS/PDF_FIDELITY_RENDERINGS_ZERO_RESULTS.json', encoding='utf-8') as f:
    zero_results = json.load(f)

hits_2005 = [r for r in zero_results if r['paper_id'] == '2305']
print(f'2305.08038 OCR results: {len(hits_2005)} pages with results')
for r in hits_2005:
    print(f'  page: {r["page"]}, tokens: {r.get("tokens", "N/A")}, math_hits: {r.get("math_hits", "N/A")}, chars: {r.get("char_count", "N/A")}')
    if 'text_preview' in r:
        preview = r['text_preview']
        print(f'    preview: {preview[:200]}')

# Also check the OCR text of the specific pages with hits
import subprocess
render_dir = Path(r'DATASETS/PDF_FIDELITY_RENDERINGS_ZERO/2305_08038')
for png in sorted(render_dir.rglob('*.png')):
    rel = png.relative_to(render_dir)
    proc = subprocess.run(
        ['C:\Program Files\Tesseract-OCR\tesseract.exe', str(png), 'stdout', '--psm', '3'],
        capture_output=True, text=True, timeout=60
    )
    text = proc.stdout
    math_symbols = r'[=+\-×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]'
    hits = re.findall(math_symbols, text)
    if hits:
        print(f'\n  Page {rel.stem} has {len(hits)} math hits:')
        # Show context around hits
        for i, char in enumerate(text):
            if char in re.findall(math_symbols, text):
                start = max(0, i-40)
                end = min(len(text), i+40)
                print(f'    context: ...{text[start:end]}...')
                break
