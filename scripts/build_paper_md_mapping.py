#!/usr/bin/env python3
"""
Paper to .md paper mapping + Python files audit for OpenJarvis
"""
import json
from pathlib import Path

# Use raw string to avoid unicode escape issues with Windows paths
REPO = Path(r"/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")

paper_recovery = json.loads((REPO / 'scripts/paper_id_recovery_mapping.json').read_text(encoding='utf-8'))
paper_data = paper_recovery['paper_data']

# All .md files in docs/
md_files = sorted(repo.glob('docs/*.md'))
md_names = {f.name for f in md_files}

# All Python files
py_files = sorted([f.relative_to(repo) for f in repo.rglob('*.py') if '.git' not in f.parts and 'node_modules' not in f.parts and 'venv' not in f.parts])
test_py = [f for f in py_files if 'test' in f.name or '_test' in f.name or 'spec' in f.name]

# Build paper -> usage md mapping
paper_md_map = {}
for pid, data in sorted(paper_data.items()):
    if pid == 'V2P':
        continue
    paper_md_map[pid] = {
        'math_recovery': data.get('source', ''),
        'recoverable': data.get('recoverable'),
        'solvable': data.get('solvable'),
        'total_equations': data.get('total_equations'),
        'recoverable_pct': data.get('recoverable_pct'),
        'unique_commands': data.get('unique_commands'),
        'top_errors': data.get('top_errors'),
        'notes': []
    }

# Add cross-reference info
cr_dir = repo / 'DATASETS/cross_reference'
for f in cr_dir.glob('cross_refs_*.json'):
    pid = f.stem.replace('cross_refs_', '')
    if pid in paper_md_map:
        paper_md_map[pid]['cross_reference'] = str(f.relative_to(repo))

# Add structural preservation info
sp_dir = repo / 'DATASETS/structural_preservation'
for f in sp_dir.glob('*.json'):
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
        pid = data.get('arxiv_id', f.stem)
        if pid in paper_md_map:
            paper_md_map[pid].setdefault('sp_files', []).append({
                'source': str(f.relative_to(repo)),
                'fields': list(data.keys())[:10] if isinstance(data, dict) else type(data).__name__
            })
    except:
        pass

# Output summary
print(f"Total paper_ids with math_recovery data: {sum(1 for v in paper_md_map.values() if 'math_recovery' in v and v.get('math_recovery') is not None)}")
print(f"Total paper_ids with cross_reference: {sum(1 for v in paper_md_map.values() if 'cross_reference' in v)}")
print(f"Total paper_ids with structural_preservation: {sum(1 for v in paper_md_map.values() if 'sp_files' in v)}")

# List of all .md files sorted by category
print(f"\n=== .md PAPER FILES ({len(md_names)}) ===")
for name in sorted(md_names):
    print(f"  {name}")
