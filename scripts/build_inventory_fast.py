#!/usr/bin/env python3
"""
King Wen Repository Inventory Builder - Ultra-Fast
Focuses on key files, skips heavy computation for bulk files.
"""

import json
import os
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', 'dist', '.wrangler', '.vscode'}

# Pre-compute git status once
GIT_STATUS_MAP = {}
try:
    result = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)
    for line in result.stdout.strip().split('\n'):
        if line:
            status = line[:2]
            path = line[3:].strip()
            GIT_STATUS_MAP[path] = 'untracked' if status.startswith('?') else 'modified' if status.strip() else 'tracked'
except:
    pass

def get_git_status(path: Path) -> str:
    rel = str(path.relative_to(REPO_ROOT)).replace('\\', '/')
    return GIT_STATUS_MAP.get(rel, 'tracked')

# Only compute hashes for important files
IMPORTANT_EXTS = {'.json', '.jsonl', '.csv', '.py', '.md', '.bin', '.npz', '.ply', '.png'}
IMPORTANT_DIRS = {'DATASETS/', 'scripts/', 'src/', 'data/', 'tests/', 'learn/', 'docs/'}

def should_hash(path: Path) -> bool:
    rel = str(path.relative_to(REPO_ROOT))
    if path.suffix not in IMPORTANT_EXTS:
        return False
    return any(rel.startswith(d) for d in IMPORTANT_DIRS)

def get_file_hash(path: Path) -> str:
    try:
        size = path.stat().st_size
        if size > 10_000_000:
            return f"size:{size}"
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()[:16]
    except:
        return None

def classify_authority(rel: str) -> str:
    r = rel.lower()
    if any(p in r for p in ('.deprecated', 'debug_', 'fix_', 'patch_', 'trial_')):
        return 'DEPRECATED'
    if any(p in r for p in ('_manifest.json', '_results.json', 'freeze_', 'frozen_', 'baseline_', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm', 'kingwen_model_sets/')):
        return 'FROZEN'
    if any(p in r for p in ('historical', 'superseded', 'old_', 'legacy_')):
        return 'HISTORICAL'
    if r.startswith(('scripts/audit_', 'scripts/test_')) and not r.startswith('scripts/verify_'):
        return 'EXPERIMENTAL'
    if any(p in r for p in ('experimental', 'temp_', 'tmp_', 'trial_')):
        return 'EXPERIMENTAL'
    
    # Active patterns
    active_scripts = frozenset([
        'scripts/full_hexagram_shotgun.py', 'scripts/expand_server.py', 'scripts/run_all_unified_pipeline.py',
        'emotional_engine.py', 'kingwen_ternary_tables_complete.py', 'decision_matrix.py',
        'temporal_emotional_engine.py', 'hexagram_personality.py', 'KING_WEN_TABLES.py',
        'scripts/verify_registry.py', 'scripts/verify_vhdl_resolver_parity.py',
        'scripts/verify_math_jacobian_hamiltonian.py', 'scripts/verify_output_mismatches.py',
        'scripts/verify_unbound_persona_domains.py', 'scripts/enrich_kit_models.py',
    ])
    if rel in active_scripts or rel.startswith(('scripts/bridge_', 'scripts/shap_e_', 'scripts/sync_', 'scripts/test_jkd_', 'scripts/verify_', 'scripts/shotgun_', 'scripts/rl_shotgun_')):
        return 'ACTIVE'
    if rel.startswith(('scripts/validators/', 'src/', 'data/', 'tests/', 'learn/', 'data/')):
        return 'ACTIVE'
    if rel.startswith('scripts/') and not any(x in rel for x in ('debug_', 'fix_', 'patch_', 'trial_', 'old_')):
        if 'audit_' in rel: return 'EXPERIMENTAL'
        if 'test_' in rel and 'verify_' not in rel: return 'EXPERIMENTAL'
        return 'ACTIVE'
    if rel.startswith(('src/', 'data/', 'tests/', 'learn/', 'data/')):
        return 'ACTIVE'
    if rel.startswith('DATASETS/'):
        if any(p in rel for p in ('_manifest.json', '_results.json', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm', 'kingwen_model_sets/')):
            return 'FROZEN'
        if 'math_recovery' in rel or 'recovery' in rel or 'audit' in rel: return 'EXPERIMENTAL'
        return 'ACTIVE'
    if rel.endswith('.md') or rel.endswith('.txt'):
        if 'CONSOLIDATED_' in rel.upper(): return 'ACTIVE'
        if 'CHANGELOG' in rel.upper() or 'HISTORY' in rel.upper(): return 'HISTORICAL'
        return 'ACTIVE'
    return 'UNVERIFIED'

def scan_repository():
    inventory = []
    total = 0
    
    print(f"Scanning {REPO_ROOT}...")
    
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in files:
            path = Path(root) / f
            if path.suffix in {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.temp', '.cache', '.lock', '.pid'}:
                continue
            if any(d in str(path) for d in EXCLUDE_DIRS):
                continue
            
            try:
                stat = path.stat()
                rel_path = str(path.relative_to(REPO_ROOT))
                
                # Only hash important files
                sha = None
                rel = str(path.relative_to(REPO_ROOT))
                if path.suffix in {'.json', '.jsonl', '.csv', '.py', '.md', '.bin', '.npz', '.ply', '.png'} and any(rel.startswith(d) for d in {'DATASETS/', 'scripts/', 'src/', 'data/', 'tests/', 'learn/', 'docs/'}):
                    try:
                        size = path.stat().st_size
                        if size <= 10_000_000:
                            h = hashlib.sha256()
                            with open(path, 'rb') as f:
                                for chunk in iter(lambda: f.read(8192), b''):
                                    h.update(chunk)
                            sha = h.hexdigest()[:16]
                        else:
                            sha = f"size:{size}"
                    except:
                        pass
                
                inventory.append({
                    'path': rel,
                    'size_bytes': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': Path(f).suffix,
                    'directory': str(Path(rel).parent),
                    'git_status': 'tracked',  # simplified
                    'sha256': sha,
                    'authority': classify_authority(rel),
                    'scan_timestamp': datetime.now().isoformat()
                })
            except:
                pass
            
            total += 1
            if total % 50000 == 0:
                print(f"  Scanned {total} files...")
    
    print(f"Total files scanned: {len(inventory)}")
    return inventory

def classify_authority(rel: str) -> str:
    r = rel.lower()
    if any(p in r for p in ('.deprecated', 'debug_', 'fix_', 'patch_', 'trial_')):
        return 'DEPRECATED'
    if any(p in r for p in ('_manifest.json', '_results.json', 'freeze_', 'frozen_', 'baseline_', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm', 'kingwen_model_sets/')):
        return 'FROZEN'
    if any(p in r for p in ('historical', 'superseded', 'old_', 'legacy_')):
        return 'HISTORICAL'
    if r.startswith(('scripts/audit_', 'scripts/test_')) and not r.startswith('scripts/verify_'):
        return 'EXPERIMENTAL'
    if any(p in r for p in ('experimental', 'temp_', 'tmp_', 'trial_')):
        return 'EXPERIMENTAL'
    
    active_scripts = frozenset([
        'scripts/full_hexagram_shotgun.py', 'scripts/expand_server.py', 'scripts/run_all_unified_pipeline.py',
        'emotional_engine.py', 'kingwen_ternary_tables_complete.py', 'decision_matrix.py',
        'temporal_emotional_engine.py', 'hexagram_personality.py', 'KING_WEN_TABLES.py',
        'scripts/verify_registry.py', 'scripts/verify_vhdl_resolver_parity.py',
        'scripts/verify_math_jacobian_hamiltonian.py', 'scripts/verify_output_mismatches.py',
        'scripts/verify_unbound_persona_domains.py', 'scripts/enrich_kit_models.py',
    ])
    if rel in active_scripts or rel.startswith(('scripts/bridge_', 'scripts/shap_e_', 'scripts/sync_', 'scripts/test_jkd_', 'scripts/verify_', 'scripts/shotgun_', 'scripts/rl_shotgun_')):
        return 'ACTIVE'
    if rel.startswith(('scripts/validators/', 'src/', 'data/', 'tests/', 'learn/', 'data/')):
        return 'ACTIVE'
    if rel.startswith('scripts/') and not any(x in rel for x in ('debug_', 'fix_', 'patch_', 'trial_', 'old_')):
        if 'audit_' in rel: return 'EXPERIMENTAL'
        if 'test_' in rel and 'verify_' not in rel: return 'EXPERIMENTAL'
        return 'ACTIVE'
    if rel.startswith(('src/', 'data/', 'tests/', 'learn/', 'data/')):
        return 'ACTIVE'
    if rel.startswith('DATASETS/'):
        if any(p in rel for p in ('_manifest.json', '_results.json', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm', 'kingwen_model_sets/')):
            return 'FROZEN'
        if 'math_recovery' in rel or 'recovery' in rel or 'audit' in rel: return 'EXPERIMENTAL'
        return 'ACTIVE'
    if rel.endswith('.md') or rel.endswith('.txt'):
        if 'CONSOLIDATED_' in rel.upper(): return 'ACTIVE'
        if 'CHANGELOG' in rel.upper() or 'HISTORY' in rel.upper(): return 'HISTORICAL'
        return 'ACTIVE'
    return 'UNVERIFIED'

def main():
    import json
    from pathlib import Path
    from datetime import datetime
    from collections import defaultdict
    
    REPO_ROOT = Path(__file__).resolve().parent.parent
    EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', 'dist', '.wrangler', '.vscode'}
    
    print("=" * 60)
    print("KING WEN REPOSITORY INVENTORY BUILDER (Fast)")
    print("=" * 60)
    
    output_dir = REPO_ROOT / 'inventory'
    output_dir.mkdir(exist_ok=True)
    
    print("\n[1/4] Scanning repository...")
    inventory = []
    total = 0
    
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in files:
            path = Path(root) / f
            if path.suffix in {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.temp', '.cache', '.lock', '.pid'}:
                continue
            if any(d in str(path) for d in EXCLUDE_DIRS):
                continue
            
            try:
                stat = path.stat()
                rel_path = str(path.relative_to(REPO_ROOT))
                
                sha = None
                if path.suffix in {'.json', '.jsonl', '.csv', '.py', '.md', '.bin', '.npz', '.ply', '.png'} and any(rel_path.startswith(d) for d in {'DATASETS/', 'scripts/', 'src/', 'data/', 'tests/', 'learn/', 'docs/'}):
                    try:
                        size = stat.st_size
                        if size <= 10_000_000:
                            h = hashlib.sha256()
                            with open(path, 'rb') as fp:
                                for chunk in iter(lambda: fp.read(8192), b''):
                                    h.update(chunk)
                            sha = h.hexdigest()[:16]
                        else:
                            sha = f"size:{size}"
                    except:
                        pass
                
                inventory.append({
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': Path(f).suffix,
                    'directory': str(Path(rel_path).parent),
                    'git_status': 'tracked',
                    'sha256': sha,
                    'authority': classify_authority(rel_path),
                    'scan_timestamp': datetime.now().isoformat()
                })
            except:
                pass
            
            total += 1
            if total % 50000 == 0:
                print(f"  Scanned {total} files...")
    
    print(f"Total files scanned: {len(inventory)}")
    
    output_dir = Path(__file__).resolve().parent.parent / 'inventory'
    output_dir.mkdir(exist_ok=True)
    
    print("\n[2/4] Writing file inventory...")
    with open(output_dir / 'file_inventory.jsonl', 'w', encoding='utf-8') as f:
        for entry in inventory:
            f.write(json.dumps(entry) + '\n')
    
    print("\n[3/4] Generating authority summary...")
    summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0, 'extensions': set()})
    for entry in inventory:
        auth = entry['authority']
        summary[auth]['count'] += 1
        summary[auth]['total_bytes'] += entry['size_bytes']
        summary[auth]['extensions'].add(entry['extension'])
    
    for auth in summary:
        summary[auth]['extensions'] = list(summary[auth]['extensions'])
    
    with open(output_dir / 'authority_lifecycle.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n[4/4] Building execution topology...")
    topology = {
        'entry_points': [],
        'python_modules': [],
        'typescript_modules': [],
        'data_artifacts': [],
        'test_files': [],
        'config_files': [],
        'documentation': [],
        'pipeline_stages': []
    }
    
    for entry in inventory:
        path = entry['path']
        ext = entry['extension']
        auth = entry['authority']
        
        if path.endswith('.py') and not path.startswith('test_'):
            if any(x in path for x in ['run_all', 'expand_server', 'main', 'cli']):
                topology['entry_points'].append(path)
        
        if ext == '.py' and 'test_' not in path:
            if auth in ['ACTIVE', 'FROZEN']:
                topology['python_modules'].append(path)
        
        if ext in ['.ts', '.js'] and 'node_modules' not in path:
            topology['typescript_modules'].append(path)
        
        if 'DATASETS/' in path and ext in ['.json', '.jsonl', '.csv', '.bin', '.npz', '.ply', '.png']:
            topology['data_artifacts'].append({
                'path': path, 'authority': auth, 'size_bytes': entry['size_bytes']
            })
        
        if 'test_' in path or path.startswith('tests/'):
            topology['test_files'].append(path)
        
        if ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'] and path in ['package.json', 'tsconfig.json', 'pyproject.toml', 'requirements.txt']:
            topology['config_files'].append(path)
        
        if ext in ['.md', '.txt'] and 'DATASETS/' not in path:
            topology['documentation'].append(path)
        
        if path.startswith('scripts/') and auth == 'ACTIVE':
            for marker in ['full_hexagram_shotgun', 'enrich_kit_models', 'bridge_pog2_ontology',
                'shap_e_kingwen_3d_generator', 'sync_voicebox_npc_profiles',
                'test_jkd_chapter_chorus', 'bridge_math_diagram_extractor',
                'bridge_desktop_3d_engines', 'sync_all_desktop_viewers',
                'test_cognitive_variation', 'bridge_rsmv_shap_e_manifesto',
                'bridge_quantumlab_visualization', 'bridge_collisionvis_upgrade',
                'bridge_rayeren_capability_vectors', 'verify_unbound_persona_domains',
                'bridge_quantum_64_grid', 'verify_math_jacobian_hamiltonian',
                'verify_output_mismatches', 'shotgun_rollout_runtime', 'rl_shotgun_measurables']:
                if marker in path:
                    topology['pipeline_stages'].append({'stage': marker, 'script': path, 'authority': auth})
    
    with open(Path(__file__).resolve().parent.parent / 'inventory' / 'execution_topology.json', 'w') as f:
        json.dump(topology, f, indent=2)
    
    print("\n" + "=" * 60)
    print("INVENTORY COMPLETE")
    print("=" * 60)
    print(f"Total files: {len(inventory)}")
    for auth, data in sorted(summary.items()):
        print(f"  {auth:15} {data['count']:>8} files  {data['total_bytes']:>12} bytes")

if __name__ == '__main__':
    import os, json, hashlib
    from pathlib import Path
    from datetime import datetime
    from collections import defaultdict
    
    REPO_ROOT = Path(__file__).resolve().parent.parent
    EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', 'dist', '.wrangler', '.vscode'}
    
    total = 0
    inventory = []
    print("Scanning...")
    
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            path = Path(root) / f
            if path.suffix in {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.temp', '.cache', '.lock', '.pid'}:
                continue
            if any(d in str(path) for d in EXCLUDE_DIRS):
                continue
            
            try:
                stat = path.stat()
                rel_path = str(path.relative_to(REPO_ROOT))
                
                sha = None
                if path.suffix in {'.json', '.jsonl', '.csv', '.py', '.md', '.bin', '.npz', '.ply', '.png'} and any(rel_path.startswith(d) for d in {'DATASETS/', 'scripts/', 'src/', 'data/', 'tests/', 'learn/', 'docs/'}):
                    try:
                        size = stat.st_size
                        if size <= 10_000_000:
                            h = hashlib.sha256()
                            with open(path, 'rb') as fp:
                                for chunk in iter(lambda: fp.read(8192), b''):
                                    h.update(chunk)
                            sha = h.hexdigest()[:16]
                        else:
                            sha = f"size:{size}"
                    except:
                        pass
                
                inventory.append({
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': Path(f).suffix,
                    'directory': str(Path(rel_path).parent),
                    'git_status': 'tracked',
                    'sha256': sha,
                    'authority': classify_authority(rel_path),
                    'scan_timestamp': datetime.now().isoformat()
                })
            except:
                pass
            
            total += 1
            if total % 50000 == 0:
                print(f"  Scanned {total} files...")
    
    print(f"Total files scanned: {len(inventory)}")
    
    output_dir = REPO_ROOT / 'inventory'
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'file_inventory.jsonl', 'w', encoding='utf-8') as f:
        for entry in inventory:
            f.write(json.dumps(entry) + '\n')
    
    summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0, 'extensions': set()})
    for entry in inventory:
        auth = entry['authority']
        summary[auth]['count'] += 1
        summary[auth]['total_bytes'] += entry['size_bytes']
        summary[auth]['extensions'].add(entry['extension'])
    
    for auth in summary:
        summary[auth]['extensions'] = list(summary[auth]['extensions'])
    
    with open(output_dir / 'authority_lifecycle.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    topology = {'entry_points': [], 'python_modules': [], 'typescript_modules': [], 'data_artifacts': [], 'test_files': [], 'config_files': [], 'documentation': [], 'pipeline_stages': []}
    
    for entry in inventory:
        path = entry['path']
        ext = entry['extension']
        auth = entry['authority']
        
        if path.endswith('.py') and not path.startswith('test_'):
            if any(x in path for x in ['run_all', 'expand_server', 'main', 'cli']):
                topology['entry_points'].append(path)
        if ext == '.py' and 'test_' not in path and auth in ['ACTIVE', 'FROZEN']:
            topology['python_modules'].append(path)
        if ext in ['.ts', '.js'] and 'node_modules' not in path:
            topology['typescript_modules'].append(path)
        if 'DATASETS/' in path and ext in ['.json', '.jsonl', '.csv', '.bin', '.npz', '.ply', '.png']:
            topology['data_artifacts'].append({'path': path, 'authority': auth, 'size_bytes': entry['size_bytes']})
        if 'test_' in path or path.startswith('tests/'):
            topology['test_files'].append(path)
        if ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'] and path in ['package.json', 'tsconfig.json', 'pyproject.toml', 'requirements.txt']:
            topology['config_files'].append(path)
        if ext in ['.md', '.txt'] and 'DATASETS/' not in path:
            topology['documentation'].append(path)
        if path.startswith('scripts/') and auth == 'ACTIVE':
            for marker in ['full_hexagram_shotgun', 'enrich_kit_models', 'bridge_pog2_ontology', 'shap_e_kingwen_3d_generator', 'sync_voicebox_npc_profiles', 'test_jkd_chapter_chorus', 'bridge_math_diagram_extractor', 'bridge_desktop_3d_engines', 'sync_all_desktop_viewers', 'test_cognitive_variation', 'bridge_rsmv_shap_e_manifesto', 'bridge_quantumlab_visualization', 'bridge_collisionvis_upgrade', 'bridge_rayeren_capability_vectors', 'verify_unbound_persona_domains', 'bridge_quantum_64_grid', 'verify_math_jacobian_hamiltonian', 'verify_output_mismatches', 'shotgun_rollout_runtime', 'rl_shotgun_measurables']:
                if marker in path:
                    topology['pipeline_stages'].append({'stage': marker, 'script': path, 'authority': auth})
    
    with open(Path(__file__).resolve().parent.parent / 'inventory' / 'execution_topology.json', 'w') as f:
        json.dump(topology, f, indent=2)
    
    print("=" * 60)
    print("INVENTORY COMPLETE")
    print("=" * 60)
    print(f"Total files: {len(inventory)}")
    for auth, data in sorted(summary.items()):
        print(f"  {auth:15} {data['count']:>8} files  {data['total_bytes']:>12} bytes")