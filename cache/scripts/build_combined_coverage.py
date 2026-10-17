import json
from pathlib import Path

ROOT = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

# Load manifest
with open(ROOT / 'DATASETS/CORPUS_MANIFEST_2026-10-16.json', encoding='utf-8') as f:
    manifest = json.load(f)

# Load PDF fallback data
with open(ROOT / 'DATASETS/PDF_FALLBACK_8_PAPERS_2026-10-16.json', encoding='utf-8') as f:
    pdf_fallback = json.load(f)
pdf_by_id = {r['paper_id']: r for r in pdf_fallback}

# Load PDF source URLs
with open(ROOT / 'DATASETS/PDF_SOURCE_URLS_8_PAPERS_2026-10-16.json', encoding='utf-8') as f:
    pdf_urls = json.load(f)
url_by_id = {r['paper_id']: r for r in pdf_urls}

# Build combined coverage
rows = []
for m in manifest:
    pid = m['paper_id']
    if m['has_html_corpus']:
        rows.append({
            'paper_id': pid,
            'category': m['category'],
            'html_status': 'processed',
            'html_equations': m.get('html_equation_count', 0),
            'pdf_status': 'not_required',
            'pdf_pages': None,
            'pdf_chars': None,
            'source': 'arxiv_html',
        })
    else:
        pf = pdf_by_id.get(pid, {})
        pu = url_by_id.get(pid, {})
        rows.append({
            'paper_id': pid,
            'category': m['category'],
            'html_status': 'no_html_source',
            'html_equations': 0,
            'pdf_status': pf.get('status', 'unknown'),
            'pdf_pages': pf.get('page_count'),
            'pdf_chars': pf.get('total_chars'),
            'pdf_formula_candidates': pf.get('formula_candidates'),
            'pdf_sha256': pf.get('pdf_sha256', '')[:16],
            'arxiv_pdf_url': pu.get('url'),
            'arxiv_pdf_http': pu.get('status'),
            'source': 'pdf_fallback',
        })

# Summary
html_papers = [r for r in rows if r['html_status'] == 'processed']
pdf_papers = [r for r in rows if r['html_status'] == 'no_html_source']
total_html_eq = sum(r['html_equations'] for r in html_papers)

print(f'Total papers: {len(rows)}')
print(f'HTML-processed: {len(html_papers)} ({total_html_eq:,} equations)')
print(f'PDF-fallback: {len(pdf_papers)}')
print(f'Coverage: {len(rows)}/{len(rows)} papers have at least one extraction route')
print()

# Save combined coverage
out = ROOT / 'DATASETS/COMBINED_COVERAGE_2026-10-16.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump({
        'generated_at': '2026-10-16T21:00:00Z',
        'total_papers': len(rows),
        'html_processed': len(html_papers),
        'pdf_fallback': len(pdf_papers),
        'total_html_equations': total_html_eq,
        'rows': rows,
    }, f, indent=2, ensure_ascii=False)
print(f'Saved: {out}')
