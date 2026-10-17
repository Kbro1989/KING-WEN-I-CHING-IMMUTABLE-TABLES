import json
import urllib.request
from pathlib import Path

missing = ['1907.04931', '2104.01277', '2205.01395', '2206.00364',
           '2305.08038', '2602.15881', '2605.22902', '2605.27315']

print('=== arxiv PDF source availability ===')
results = []
for pid in missing:
    url = f'https://arxiv.org/pdf/{pid}'
    try:
        req = urllib.request.Request(url, method='HEAD',
                                     headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            status = r.status
            clen = r.headers.get('Content-Length')
            ctype = r.headers.get('Content-Type')
        results.append({'paper_id': pid, 'url': url, 'status': status,
                        'content_type': ctype, 'content_length': clen,
                        'available': True})
        print(f'{pid}: HTTP {status} | {ctype} | {clen} bytes')
    except Exception as e:
        results.append({'paper_id': pid, 'url': url, 'status': None,
                        'error': str(e), 'available': False})
        print(f'{pid}: FAILED - {e}')

out = Path('DATASETS/PDF_SOURCE_URLS_8_PAPERS_2026-10-16.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print()
print(f'Saved: {out}')
