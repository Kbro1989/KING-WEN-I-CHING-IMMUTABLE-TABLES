#!/usr/bin/env python3
"""
Build DATASETS/manifest.json - Artifact provenance manifest
"""

import json
import os
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / 'DATASETS'
INVENTORY_DIR = REPO_ROOT / 'inventory'

def build_manifest():
    """Build DATASETS manifest from inventory and known artifacts"""
    manifest = {
        'manifest_version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'repo_root': str(REPO_ROOT),
        'datasets_root': str(DATASETS_DIR),
        'artifacts': []
    }
    
    # Known artifact categories with their patterns
    categories = {
        'pipeline_outputs': {
            'patterns': ['full_shotgun_expansion_all.jsonl', 'expanded_states.csv', 'resolved_states.csv'],
            'producer': 'scripts/full_hexagram_shotgun.py',
            'schema': 'shotgun_expand_output',
            'frozen': False
        },
        'training_data': {
            'patterns': ['full_shotgun_expansion_all.jsonl', 'full_shotgun_expansion_corpus_enriched.jsonl', 'full_shotgun_expansion_lexical_gate.jsonl'],
            'producer': 'scripts/build_full_shotgun_jsonl.py',
            'schema': 'training_corpus',
            'frozen': False
        },
        'model_kits': {
            'patterns': ['kit_*.json'],
            'producer': 'scripts/enrich_kit_models.py',
            'schema': 'kit_model',
            'frozen': False
        },
        'avatar_meshes': {
            'patterns': ['*.ply', 'kingwen_avatar_mesh_manifest.json'],
            'producer': 'scripts/generate_avatar_meshes.py',
            'schema': 'avatar_mesh',
            'frozen': True
        },
        'depth_maps': {
            'patterns': ['depth_maps_16bit/*.png', 'depth_pointclouds/*.ply'],
            'producer': 'scripts/bridge_depth_anything_v2.py',
            'schema': 'depth_map',
            'frozen': True
        },
        'sovereign_world': {
            'patterns': ['kingwen_sovereign_world_topology.json', 'godot_scenes/', 'openusd_stages/'],
            'producer': 'scripts/generate_sovereign_world.py',
            'schema': 'sovereign_topology',
            'frozen': True
        },
        'targeted_ocr': {
            'patterns': ['targeted_ocr/targeted_ocr_results.json', 'targeted_ocr/*/*.png'],
            'producer': 'scripts/targeted_depth_ocr.py',
            'schema': 'targeted_ocr_results',
            'frozen': True
        },
        'rahmani_generalization': {
            'patterns': ['structural_preservation/rahmani_1212.0957_generalization_*.json'],
            'producer': 'scripts/evaluate_rahmani_generalization.py',
            'schema': 'generalization_evaluation',
            'frozen': True
        },
        'benchmark_artifacts': {
            'patterns': ['benchmark_manifest.json', 'benchmark_pdfs/*', 'benchmark_results_*.json'],
            'producer': 'scripts/build_benchmark_manifest.py',
            'schema': 'benchmark',
            'frozen': True
        },
        'math_recovery': {
            'patterns': ['math_recovery*/*.json', 'math_recovery*/*.jsonl'],
            'producer': 'scripts/math_recovery_tool.py',
            'schema': 'math_recovery',
            'frozen': False
        },
    }
    
    artifacts = []
    
    for category, info in categories.items():
        for pattern in info['patterns']:
            # Find matching files
            if '*' in pattern:
                # Handle glob patterns
                import glob
                for match in glob.glob(str(DATASETS_DIR / pattern), recursive=True):
                    rel = Path(match).relative_to(REPO_ROOT)
                    artifacts.append({
                        'dataset_id': f"{category}/{rel.name}",
                        'relative_path': str(rel),
                        'category': category,
                        'purpose': info['producer'],
                        'producer': info['producer'],
                        'consumers': [],  # Would need lineage analysis
                        'schema': info['schema'],
                        'version': '1.0',
                        'frozen': info['frozen'],
                        'regeneration_policy': 'on_demand' if not info['frozen'] else 'never',
                        'sha256': None,  # Would need to compute
                        'size_bytes': 0,  # Would need to compute
                        'created_at': None,
                        'updated_at': None
                    })
            else:
                # Direct file
                path = DATASETS_DIR / pattern
                if path.exists():
                    rel = path.relative_to(REPO_ROOT)
                    stat = path.stat()
                    artifacts.append({
                        'dataset_id': f"{category}/{rel.name}",
                        'relative_path': str(rel),
                        'category': category,
                        'purpose': info['producer'],
                        'producer': info['producer'],
                        'consumers': [],
                        'schema': info['schema'],
                        'version': '1.0',
                        'frozen': info['frozen'],
                        'regeneration_policy': 'on_demand' if not info['frozen'] else 'never',
                        'sha256': None,
                        'size_bytes': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'updated_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
    
    manifest['artifacts'] = artifacts
    manifest['total_artifacts'] = len(artifacts)
    manifest['categories'] = list(categories.keys())
    
    return manifest

def main():
    print("Building DATASETS/manifest.json...")
    manifest = build_manifest()
    
    REPO_ROOT = Path(__file__).resolve().parent.parent
    DATASETS_DIR = REPO_ROOT / 'DATASETS'
    
    with open(DATASETS_DIR / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Built manifest with {len(manifest['artifacts'])} artifacts")
    print(f"Categories: {manifest['categories']}")

if __name__ == '__main__':
    import json
    from pathlib import Path
    import glob
    
    main()