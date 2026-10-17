import json
from pathlib import Path
import fitz  # PyMuPDF

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

paper_index = {}
for f in pdfs:
    for rec in missing:
        if f.name.startswith(rec):
            paper_index[rec] = f
            break

SAMPLING_STEP = 5

def select_sample_pages(total_pages):
    """Select stratified sample of pages."""
    sel = {1}  # always include page 1
    for i in range(SAMPLING_STEP, total_pages + 1, SAMPLING_STEP):
        sel.add(i)
    return sorted(sel)

reference_plan = []
for pid in missing:
    p = paper_index.get(pid)
    if not p:
        reference_plan.append({'paper_id': pid, 'status': 'pdf_not_found'})
        continue
    doc = fitz.open(str(p))
    total = len(doc)
    pages_to_check = select_sample_pages(total)
    page_details = []
    for pg in pages_to_check:
        text = doc[pg - 1].get_text()
        page_details.append({
            'page': pg,
            'char_count': len(text),
            'has_math_symbols': bool(__import__('re').search(r'[=∑∫√±×÷≤≥≠≈∞∂∇αβγδεζηθλμπρστφχψω]', text)),
        })
    doc.close()
    reference_plan.append({
        'paper_id': pid,
        'total_pages': total,
        'sampled_pages': page_details,
    })

plan_path = Path('DATASETS/PDF_FIDELITY_REFERENCE_PLAN_2026-10-16.json')
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(reference_plan, f, indent=2, ensure_ascii=False)

print(f'Saved: {plan_path}')
for r in reference_plan:
    if 'total_pages' in r:
        pages = ','.join(str(x['page']) for x in r['sampled_pages'])
        print(f'{r["paper_id"]}: {r["total_pages"]} pages, sample: {pages}')
    else:
        print(f'{r["paper_id"]}: NOT FOUND')
