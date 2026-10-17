import json
import re
from pathlib import Path
import fitz  # PyMuPDF

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

# Papers to render (prioritize formula density)
render_papers = ['2104.01277', '2206.00364', '1907.04931', '2605.27315', '2605.22902']

paper_index = {}
for f in pdfs:
    for pid in missing:
        if f.name.startswith(pid):
            paper_index[pid] = f
            break

# Output directory
render_dir = Path('DATASETS/PDF_FIDELITY_RENDERINGS')
render_dir.mkdir(exist_ok=True)

rendered = []
for pid in render_papers:
    p = paper_index.get(pid)
    if not p:
        continue
    doc = fitz.open(str(p))
    out_dir = render_dir / pid.replace('.', '_')
    out_dir.mkdir(exist_ok=True)
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        count = len(re.findall(r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]', text))
        if count > 0:
            # Render this page
            pix = page.get_pixmap(dpi=150)
            img_path = out_dir / f'page_{i+1}_formulas_{count}.png'
            pix.save(str(img_path))
            rendered.append({
                'paper_id': pid,
                'page': i + 1,
                'formula_candidates': count,
                'image_path': str(img_path.relative_to(render_dir)),
            })
    doc.close()

out = Path('DATASETS/PDF_FIDELITY_RENDERINGS_PLAN.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(rendered, f, indent=2, ensure_ascii=False)
print(f'Saved: {out}')
print(f'Rendered {len(rendered)} pages with formula candidates')
for r in rendered:
    print(f'  {r["paper_id"]}: page {r["page"]}, {r["formula_candidates"]} candidates')
