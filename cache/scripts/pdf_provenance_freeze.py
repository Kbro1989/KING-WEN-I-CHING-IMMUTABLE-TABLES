import json
import hashlib
import re
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

pdf_dir = Path(r'C:\Users\krist\Desktop\zotero\learning-corpus')
pdfs = list(pdf_dir.rglob('*.pdf'))

def get_arxiv_version(pid):
    """Read version from arxiv abs page."""
    url = f'https://arxiv.org/abs/{pid}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode('utf-8', errors='replace')
        m = re.search(r'arXiv:' + re.escape(pid) + r'v(\d+)', html)
        if m:
            return f'v{m.group(1)}'
        return None
    except Exception as e:
        return f'ERROR: {e}'

records = []
for pid in missing:
    matches = [f for f in pdfs if f.name.startswith(pid)]
    if not matches:
        records.append({'paper_id': pid, 'status': 'pdf_not_found'})
        continue
    p = matches[0]
    data = p.read_bytes()
    rec = {
        'paper_id': pid,
        'local_pdf_path': str(p),
        'local_pdf_size': len(data),
        'local_pdf_sha256': hashlib.sha256(data).hexdigest(),
        'local_pdf_md5': hashlib.md5(data).hexdigest(),
        'arxiv_pdf_url': f'https://arxiv.org/pdf/{pid}',
        'arxiv_html_url': f'https://arxiv.org/html/{pid}',
        'arxiv_abs_url': f'https://arxiv.org/abs/{pid}',
        'arxiv_version': get_arxiv_version(pid),
        'retrieval_date_recorded': '2026-10-16',
        'extraction_engine': 'PyMuPDF',
        'extraction_method': 'page.get_text()',
        'fidelity_status': 'UNVALIDATED',
    }
    records.append(rec)
    print(f'{pid}: {rec["arxiv_version"]} | {rec["local_pdf_size"]:,} bytes | sha256={rec["local_pdf_sha256"][:16]}')

out = Path('DATASETS/PDF_PROVENANCE_8_PAPERS_2026-10-16.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(records, f, indent=2, ensure_ascii=False)
print()
print(f'Saved: {out}')
