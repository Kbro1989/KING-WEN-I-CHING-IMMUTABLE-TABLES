import re
import json
from pathlib import Path
import fitz  # PyMuPDF

zero_papers = ['2305.08038', '2602.15881']
pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')

paper_index = {}
for f in pdf_dir.rglob('*.pdf'):
    for pid in zero_papers:
        if f.name.startswith(pid):
            paper_index[pid] = f
            break

render_dir = Path('DATASETS/PDF_FIDELITY_RENDERINGS_ZERO')
render_dir.mkdir(exist_ok=True)

results = []
for pid in zero_papers:
    p = paper_index.get(pid)
    if not p:
        results.append({'paper_id': pid, 'status': 'NOT FOUND'})
        continue
    doc = fitz.open(str(p))
    total = len(doc)
    zero_count = 0
    formula_pages = []
    for i in range(len(doc)):
        text = doc[i].get_text()
        count = len(re.findall(r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]', text))
        if count > 0:
            formula_pages.append((i+1, count))
    # Render ALL pages (even zero-candidate) to verify
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(dpi=150)
        img_path = render_dir / pid.replace('.','_') / f'page_{i+1}_all.png'
        img_path.parent.mkdir(exist_ok=True)
        pix.save(str(img_path))
        results.append({
            'paper_id': pid,
            'page': i+1,
            'formula_candidates': 0,
            'image_path': str(img_path.relative_to(render_dir)),
        })
    doc.close()
    results.append({'paper_id': pid, 'status': 'done', 'total_pages': total, 'formula_pages': formula_pages})

out = Path('DATASETS/PDF_FIDELITY_RENDERINGS_ZERO_PLAN.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f'Saved: {out}')
for pid in zero_papers:
    p = paper_index.get(pid)
    if p:
        doc = fitz.open(str(p))
        print(f'{pid}: {doc.page_count} pages, formula pages: {formula_pages}')
        doc.close()
