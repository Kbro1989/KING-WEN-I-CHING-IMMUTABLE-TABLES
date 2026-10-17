import json
from pathlib import Path
from collections import Counter

ROOT = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

# Load manifest
with open(ROOT / 'DATASETS/CORPUS_MANIFEST_2026-10-16.json', encoding='utf-8') as f:
    manifest = json.load(f)

# Load benchmark results
with open(ROOT / 'DATASETS/BENCHMARK_RESULTS_2026-10-16.json', encoding='utf-8') as f:
    bench = json.load(f)

# 1. Manifest count
print(f'1. Manifest papers: {len(manifest)}')
print(f'   With HTML: {sum(1 for m in manifest if m["has_html_corpus"])}')
print(f'   Without HTML: {sum(1 for m in manifest if not m["has_html_corpus"])}')

# 2. Manifest HTML equation sum
manifest_eq = sum(m.get('html_equation_count', 0) for m in manifest if m['has_html_corpus'])
print(f'2. Manifest HTML equations (sum): {manifest_eq:,}')

# 3. Benchmark results sum
bench_eq = bench['total_equations_extracted']
print(f'3. Benchmark results equations: {bench_eq:,}')

# 4. Recompute from disk (source of truth)
corpus_dir = ROOT / 'DATASETS/arxiv_html_corpus'
disk_eq = 0
disk_papers = 0
per_paper = {}
for f in corpus_dir.glob('*.json'):
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    eqs = d.get('equations', [])
    disk_eq += len(eqs)
    disk_papers += 1
    per_paper[f.stem] = len(eqs)
print(f'4. Disk recomputed: {disk_papers} files, {disk_eq:,} equations')

# 5. Check for duplicates in per_paper
print()
print('=== RECONCILIATION ===')
print(f'Manifest sum == Disk sum: {manifest_eq == disk_eq}')
print(f'Benchmark == Disk sum: {bench_eq == disk_eq}')
print(f'Benchmark == Manifest sum: {bench_eq == manifest_eq}')

# 6. Check the 227-paper claim vs final
print()
print('=== SUCCESSFUL BATCH RECONCILIATION ===')
print(f'Successful batch (proc_f5c957e0887c): 227 papers, 69,069 equations')
print(f'Final state: {disk_papers} papers, {disk_eq:,} equations')
print(f'Difference: +{disk_papers - 227} papers, +{disk_eq - 69069:,} equations')
print('(Later batches added papers that the 227-batch did not include)')

# 7. Check for duplicate equation occurrences within each paper
print()
print('=== DUPLICATE OCCURRENCE CHECK ===')
total_dups = 0
for f in sorted(corpus_dir.glob('*.json')):
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    eqs = d.get('equations', [])
    # Check for duplicate IDs
    ids = [e.get('id') or e.get('equation_id') for e in eqs]
    id_counts = Counter(ids)
    dups = {k: v for k, v in id_counts.items() if v > 1 and k is not None}
    if dups:
        total_dups += sum(v - 1 for v in dups.values())
        print(f'  {f.stem}: {len(dups)} duplicate IDs ({sum(v-1 for v in dups.values())} extra)')
print(f'Total duplicate equation IDs across corpus: {total_dups}')
