import json
from pathlib import Path

ROOT = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open(ROOT / 'DATASETS/CORPUS_MANIFEST_2026-10-16.json', encoding='utf-8') as f:
    manifest = json.load(f)
manifest_ids = set(m['paper_id'] for m in manifest)

corpus_dir = ROOT / 'DATASETS/arxiv_html_corpus'
disk_ids = set()
disk_eq = {}
for f in corpus_dir.glob('*.json'):
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    pid = d.get('arxiv_id', f.stem)
    disk_ids.add(pid)
    disk_eq[pid] = len(d.get('equations', []))

print(f'Manifest IDs: {len(manifest_ids)}')
print(f'Disk IDs: {len(disk_ids)}')
print()
extra = sorted(disk_ids - manifest_ids)
missing = sorted(manifest_ids - disk_ids)
print(f'=== On disk but NOT in manifest ({len(extra)}) ===')
for pid in extra:
    print(f'  {pid}: {disk_eq[pid]:,} equations')
print()
print(f'=== In manifest but NOT on disk ({len(missing)}) ===')
for pid in missing:
    print(f'  {pid}')

# Check if extras are the reference cohort
ref_cohort = ['2009.00031','2102.03334','2605.00155','2605.00224','2605.06070',
              '2605.18130','2605.22715','2605.23244','2605.24807','2605.24856',
              '2605.25036','2605.25334','2605.28615','2605.28896']
print()
print('=== Are extras in the 14-paper reference cohort? ===')
for pid in extra:
    print(f'  {pid}: {"YES - REFERENCE COHORT" if pid in ref_cohort else "no"}')

# Total equations from extras
extra_eq = sum(disk_eq[p] for p in extra)
print()
print(f'Equations from extra files: {extra_eq:,}')
print(f'Manifest sum: {sum(m.get("html_equation_count",0) for m in manifest):,}')
print(f'Disk sum: {sum(disk_eq.values()):,}')
