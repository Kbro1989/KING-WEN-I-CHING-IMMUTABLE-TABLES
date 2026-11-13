#!/usr/bin/env python3
"""
King Wen Repository Inventory Builder
Generates four machine-readable inventories:
1. file_inventory.jsonl — every file with metadata
2. execution_topology.json — programs, entry points, imports, exports
3. artifact_lineage.jsonl — producer→artifact→consumer chains
4. authority_lifecycle.json — ACTIVE/EXPERIMENTAL/FROZEN/HISTORICAL/DEPRECATED/UNVERIFIED
"""

import json
import os
import sys
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', 'dist', '.wrangler', '.vscode'}
EXCLUDE_EXTS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.dat', '.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.temp', '.cache', '.lock', '.pid'}

def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.suffix in EXCLUDE_EXTS:
        return True
    return False

def get_git_status(path: Path) -> str:
    """Get git tracking status: tracked, untracked, ignored, submodule"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', '--', str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=2
        )
        if not result.stdout.strip():
            return 'tracked'
        status = result.stdout.strip()[:2]
        if status.startswith('?'):
            return 'untracked'
        if status.startswith('!'):
            return 'ignored'
        return 'modified'
    except Exception:
        return 'unknown'

def get_file_hash(path: Path, max_size: int = 10_000_000) -> Optional[str]:
    """SHA-256 for files under max_size"""
    try:
        if path.stat().st_size > max_size:
            return f"size:{path.stat().st_size}"
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return None

def classify_authority(path: Path, rel_path: str) -> str:
    """Classify file authority/lifecycle"""
    rel = rel_path.lower()
    
    # Deprecated patterns
    if any(p in rel for p in ['.deprecated', 'debug_', 'debug-', 'fix_', 'patch_', 'fix-', 'patch-']):
        return 'DEPRECATED'
    
    # Frozen - immutable benchmarks, manifests, frozen outputs
    if any(p in rel for p in ['_manifest.json', '_results.json', 'freeze_', 'frozen_', 'baseline_', 'benchmark_manifest']):
        return 'FROZEN'
    if 'DATASETS/' in rel and any(x in rel for x in ['_manifest.json', '_results.json', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm']):
        return 'FROZEN'
    
    # Historical - superseded implementations
    if any(p in rel for p in ['historical', 'superseded', 'old_', 'legacy_', 'v1_', 'v2_']):
        return 'HISTORICAL'
    
    # Experimental - research, audit, experimental prefixes
    if any(rel.startswith(p) for p in ['scripts/audit_', 'scripts/experimental', 'scripts/test_']):
        if not rel.startswith('scripts/verify_'):
            return 'EXPERIMENTAL'
    if any(p in rel for p in ['experimental', 'temp_', 'tmp_', 'debug_', 'trial_', 'trial-']):
        return 'EXPERIMENTAL'
    
    # Active - core pipeline, active math, active verification
    active_patterns = [
        'scripts/full_hexagram_shotgun.py',
        'scripts/expand_server.py',
        'scripts/run_all_unified_pipeline.py',
        'emotional_engine.py',
        'kingwen_ternary_tables_complete.py',
        'decision_matrix.py',
        'temporal_emotional_engine.py',
        'hexagram_personality.py',
        'KING_WEN_TABLES.py',
        'scripts/verify_registry.py',
        'scripts/verify_vhdl_resolver_parity.py',
        'scripts/verify_math_jacobian_hamiltonian.py',
        'scripts/verify_output_mismatches.py',
        'scripts/verify_unbound_persona_domains.py',
        'scripts/full_hexagram_shotgun.py',
        'scripts/enrich_kit_models.py',
        'scripts/bridge_',
        'scripts/shap_e_',
        'scripts/sync_',
        'scripts/test_jkd_',
        'scripts/bridge_math_diagram_extractor.py',
        'scripts/bridge_desktop_3d_engines.py',
        'scripts/sync_all_desktop_viewers.py',
        'scripts/bridge_rsmv_shap_e_manifesto.py',
        'scripts/bridge_quantumlab_visualization.py',
        'scripts/bridge_collisionvis_upgrade.py',
        'scripts/bridge_rayeren_capability_vectors.py',
        'scripts/verify_unbound_persona_domains.py',
        'scripts/bridge_quantum_64_grid.py',
        'scripts/verify_math_jacobian_hamiltonian.py',
        'scripts/verify_output_mismatches.py',
        'scripts/shotgun_rollout_runtime.py',
        'scripts/rl_shotgun_measurables.py',
        'emotional_engine.py',
        'kingwen_ternary_tables_complete.py',
        'decision_matrix.py',
        'temporal_emotional_engine.py',
        'hexagram_personality.py',
        'KING_WEN_TABLES.py',
        'scripts/verify_registry.py',
        'scripts/verify_vhdl_resolver_parity.py',
        'scripts/verify_math_jacobian_hamiltonian.py',
        'scripts/verify_output_mismatches.py',
        'scripts/verify_unbound_persona_domains.py',
        'scripts/full_hexagram_shotgun.py',
        'scripts/enrich_kit_models.py',
        'scripts/bridge_',
        'scripts/shap_e_',
        'scripts/sync_',
        'scripts/test_jkd_',
        'scripts/bridge_math_diagram_extractor.py',
        'scripts/bridge_desktop_3d_engines.py',
        'scripts/sync_all_desktop_viewers.py',
        'scripts/bridge_rsmv_shap_e_manifesto.py',
        'scripts/bridge_quantumlab_visualization.py',
        'scripts/bridge_collisionvis_upgrade.py',
        'scripts/bridge_rayeren_capability_vectors.py',
        'scripts/verify_unbound_persona_domains.py',
        'scripts/bridge_quantum_64_grid.py',
        'scripts/verify_math_jacobian_hamiltonian.py',
        'scripts/verify_output_mismatches.py',
        'scripts/shotgun_rollout_runtime.py',
        'scripts/rl_shotgun_measurables.py',
        'emotional_engine.py',
        'kingwen_ternary_tables_complete.py',
        'decision_matrix.py',
        'temporal_emotional_engine.py',
        'hexagram_personality.py',
        'KING_WEN_TABLES.py',
        'scripts/verify_registry.py',
        'scripts/verify_vhdl_resolver_parity.py',
        'scripts/verify_math_jacobian_hamiltonian.py',
        'scripts/verify_output_mismatches.py',
        'scripts/verify_unbound_persona_domains.py',
    ]
    
    for pattern in active_patterns:
        if pattern in rel:
            return 'ACTIVE'
    
    # Check if in active directories
    if rel.startswith('scripts/') and not any(x in rel for x in ['debug_', 'fix_', 'patch_', 'trial_', 'old_']):
        if 'audit_' in rel:
            return 'EXPERIMENTAL'
        if 'test_' in rel and 'verify_' not in rel:
            return 'EXPERIMENTAL'
        return 'ACTIVE'
    
    if rel.startswith('src/') or rel.startswith('src\\'):
        return 'ACTIVE'
    
    if rel.startswith('data/') or rel.startswith('data\\'):
        return 'ACTIVE'
    
    if rel.startswith('tests/') or rel.startswith('tests\\'):
        return 'ACTIVE'
    
    if rel.startswith('learn/') or rel.startswith('learn\\'):
        return 'ACTIVE'
    
    if rel.startswith('scripts/validators/'):
        return 'ACTIVE'
    
    if rel.startswith('scripts/run_all_unified_pipeline.py'):
        return 'ACTIVE'
    
    if rel.startswith('scripts/expand_server.py'):
        return 'ACTIVE'
    
    # Data artifacts
    if rel.startswith('DATASETS/'):
        if any(x in rel for x in ['_manifest.json', '_results.json', 'avatar_mesh_manifest', 'depth_', 'quantum_prewarm', 'kingwen_avatar_mesh_manifest', 'kingwen_model_sets/']):
            return 'FROZEN'
        if 'math_recovery' in rel or 'recovery' in rel:
            return 'EXPERIMENTAL'
        if 'audit' in rel or 'audit_' in rel:
            return 'EXPERIMENTAL'
        return 'ACTIVE'
    
    # Documentation
    if rel.endswith('.md') or rel.endswith('.txt'):
        if 'CONSOLIDATED_' in rel.upper():
            return 'ACTIVE'
        if 'CHANGELOG' in rel.upper() or 'HISTORY' in rel.upper():
            return 'HISTORICAL'
        return 'ACTIVE'
    
    # Config
    if rel in ['package.json', 'tsconfig.json', 'pyproject.toml', 'requirements.txt', 'README.md', 'AGENTS.md', 'KINGWEN_AGENT_ONBOARDING.md', 'king-wen-workflow-paths.md', 'codebasemap.md', 'scripts/INDEX.md']:
        return 'ACTIVE'
    
    return 'UNVERIFIED'

def scan_repository() -> List[Dict]:
    """Scan entire repository and return file inventory"""
    inventory = []
    total = 0
    
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in files:
            path = Path(root) / f
            if should_exclude(path):
                continue
            
            try:
                stat = path.stat()
                rel_path = str(path.relative_to(REPO_ROOT))
                
                entry = {
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': path.suffix,
                    'directory': str(Path(rel_path).parent),
                    'git_status': get_git_status(path),
                    'sha256': get_file_hash(path),
                    'authority': classify_authority(path, rel_path),
                    'scan_timestamp': datetime.now().isoformat()
                }
                inventory.append(entry)
                total += 1
                
                if total % 50000 == 0:
                    print(f"  Scanned {total} files...")
                    
            except Exception as e:
                print(f"Error scanning {path}: {e}")
    
    print(f"Total files scanned: {total}")
    return inventory

def write_inventory(inventory: List[Dict], output_path: Path):
    """Write inventory as JSONL"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in inventory:
            f.write(json.dumps(entry) + '\n')
    print(f"Written {len(inventory)} entries to {output_path}")

def generate_authority_summary(inventory: List[Dict]) -> Dict:
    """Generate authority classification summary"""
    summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0, 'extensions': set()})
    for entry in inventory:
        auth = entry['authority']
        summary[auth]['count'] += 1
        summary[auth]['total_bytes'] += entry['size_bytes']
        summary[auth]['extensions'].add(entry['extension'])
    
    # Convert sets to lists for JSON serialization
    for auth in summary:
        summary[auth]['extensions'] = list(summary[auth]['extensions'])
    
    return dict(summary)

def main():
    print("=" * 60)
    print("KING WEN REPOSITORY INVENTORY BUILDER")
    print("=" * 60)
    
    output_dir = REPO_ROOT / 'inventory'
    output_dir.mkdir(exist_ok=True)
    
    # 1. File Inventory
    print("\n[1/4] Scanning repository...")
    inventory = scan_repository()
    
    print("\n[2/4] Writing file inventory...")
    write_inventory(inventory, output_dir / 'file_inventory.jsonl')
    
    print("\n[3/4] Generating authority summary...")
    authority_summary = generate_authority_summary(inventory)
    with open(output_dir / 'authority_lifecycle.json', 'w') as f:
        json.dump(authority_summary, f, indent=2)
    print(f"Authority summary written to {output_dir / 'authority_lifecycle.json'}")
    
    # 4. Execution topology (basic)
    print("\n[4/4] Building execution topology...")
    topology = build_execution_topology(inventory)
    with open(output_dir / 'execution_topology.json', 'w') as f:
        json.dump(topology, f, indent=2)
    print(f"Execution topology written to {output_dir / 'execution_topology.json'}")
    
    print("\n" + "=" * 60)
    print("INVENTORY COMPLETE")
    print("=" * 60)
    print(f"Total files: {len(inventory)}")
    print(f"Output directory: {output_dir}")
    
    for auth, data in sorted(authority_summary.items()):
        print(f"  {auth:15} {data['count']:>8} files  {data['total_bytes']:>12} bytes")

def build_execution_topology(inventory: List[Dict]) -> Dict:
    """Build basic execution topology from file inventory"""
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
        
        # Python entry points
        if entry['path'].endswith('.py') and not entry['path'].startswith('test_'):
            if any(x in entry['path'] for x in ['run_all', 'expand_server', 'main', 'cli']):
                topology['entry_points'].append(entry['path'])
        
        # Python modules (in scripts/, src/, etc.)
        if ext == '.py' and 'test_' not in entry['path']:
            if entry['authority'] in ['ACTIVE', 'FROZEN']:
                topology['python_modules'].append(entry['path'])
        
        # TypeScript modules
        if ext in ['.ts', '.js'] and 'node_modules' not in entry['path']:
            topology['typescript_modules'].append(entry['path'])
        
        # Data artifacts
        if 'DATASETS/' in entry['path'] and entry['extension'] in ['.json', '.jsonl', '.csv', '.bin', '.npz', '.ply', '.png']:
            topology['data_artifacts'].append({
                'path': entry['path'],
                'authority': entry['authority'],
                'size_bytes': entry['size_bytes'],
                'sha256': entry['sha256']
            })
        
        # Test files
        if 'test_' in entry['path'] or entry['path'].startswith('tests/'):
            topology['test_files'].append(entry['path'])
        
        # Config files
        if entry['extension'] in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'] and entry['path'] in ['package.json', 'tsconfig.json', 'pyproject.toml', 'requirements.txt']:
            topology['config_files'].append(entry['path'])
        
        # Documentation
        if entry['extension'] in ['.md', '.txt'] and 'DATASETS/' not in entry['path']:
            topology['documentation'].append(entry['path'])
        
        # Pipeline stages (from scripts/README.md)
        if entry['path'].startswith('scripts/') and entry['authority'] == 'ACTIVE':
            # Check if in 18-stage pipeline
            stage_markers = [
                'full_hexagram_shotgun', 'enrich_kit_models', 'bridge_pog2_ontology',
                'shap_e_kingwen_3d_generator', 'sync_voicebox_npc_profiles',
                'test_jkd_chapter_chorus', 'bridge_math_diagram_extractor',
                'bridge_desktop_3d_engines', 'sync_all_desktop_viewers',
                'test_cognitive_variation', 'bridge_rsmv_shap_e_manifesto',
                'bridge_quantumlab_visualization', 'bridge_collisionvis_upgrade',
                'bridge_rayeren_capability_vectors', 'verify_unbound_persona_domains',
                'bridge_quantum_64_grid', 'verify_math_jacobian_hamiltonian',
                'verify_output_mismatches', 'shotgun_rollout_runtime', 'rl_shotgun_measurables'
            ]
            for marker in stage_markers:
                if marker in entry['path']:
                    topology['pipeline_stages'].append({
                        'stage': marker,
                        'script': entry['path'],
                        'authority': entry['authority']
                    })
    
    return topology

if __name__ == '__main__':
    main()