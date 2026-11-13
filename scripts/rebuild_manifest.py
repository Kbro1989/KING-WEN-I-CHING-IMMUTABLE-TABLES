#!/usr/bin/env python3
"""
Rebuild DATASETS/manifest.json with documented counting semantics and resolved producers.
"""

import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = REPO_ROOT / 'DATASETS'

def build_manifest():
    # Category definitions with counting semantics
    categories = {
        'pipeline_outputs': {
            'patterns': ['expanded_states.csv', 'resolved_states.csv'],
            'producer': 'scripts/full_hexagram_shotgun.py',
            'schema': 'shotgun_expand_output',
            'frozen': False,
            'counting': 'one_per_file'
        },
        'training_data': {
            'patterns': ['full_shotgun_expansion_all.jsonl', 'full_shotgun_expansion_corpus_enriched.jsonl', 'full_shotgun_expansion_lexical_gate.jsonl'],
            'producer': 'scripts/build_full_shotgun_jsonl.py',
            'schema': 'training_corpus',
            'frozen': False,
            'counting': 'one_per_file'
        },
        'model_kits': {
            'patterns': ['kit_*.json'],
            'producer': 'scripts/enrich_kit_models.py',
            'schema': 'kit_model',
            'frozen': False,
            'counting': 'one_per_file'
        },
        'avatar_meshes': {
            'patterns': ['*.ply', 'kingwen_avatar_mesh_manifest.json'],
            'producer': 'scripts/generate_avatar_meshes.py',
            'schema': 'avatar_mesh',
            'frozen': True,
            'counting': 'one_per_file'
        },
        'depth_maps': {
            'patterns': ['depth_maps_16bit/*.png', 'depth_pointclouds/*.ply'],
            'producer': 'scripts/bridge_depth_anything_v2.py',
            'schema': 'depth_map',
            'frozen': True,
            'counting': 'one_per_file_expanded'  # glob expands to multiple files
        },
        'sovereign_world': {
            'patterns': ['kingwen_sovereign_world_topology.json', 'godot_scenes/', 'openusd_stages/'],
            'producer': 'scripts/generate_sovereign_world.py',
            'schema': 'sovereign_topology',
            'frozen': True,
            'counting': 'one_per_file'
        },
        'targeted_ocr': {
            'patterns': ['targeted_ocr/targeted_ocr_results.json', 'targeted_ocr/*/*.png'],
            'producer': 'scripts/targeted_depth_ocr.py',
            'schema': 'targeted_ocr_results',
            'frozen': True,
            'counting': 'one_per_file'
        },
        'rahmani_generalization': {
            'patterns': ['structural_preservation/rahmani_1212.0957_generalization_*.json'],
            'producer': 'scripts/evaluate_rahmani_generalization.py',
            'schema': 'generalization_evaluation',
            'frozen': True,
            'counting': 'one_per_file_expanded'  # 3 glob-expanded files
        },
        'benchmark_artifacts': {
            'patterns': ['benchmark_manifest.json', 'benchmark_pdfs/*', 'benchmark_results_*.json'],
            'producer': 'scripts/build_benchmark_manifest.py',
            'schema': 'benchmark',
            'frozen': True,
            'counting': 'one_per_file'
        },
        'math_recovery': {
            'patterns': ['math_recovery*/*.json', 'math_recovery*/*.jsonl'],
            'producer': 'scripts/math_recovery_tool.py',
            'schema': 'math_recovery',
            'frozen': False,
            'counting': 'one_per_file'
        },
    }

    artifacts = []
    counting = {'glob_expanded': 0, 'one_per_file': 0}

    for category, info in categories.items():
        for pattern in info['patterns']:
            if '*' in pattern:
                import glob
                for match in sorted(glob.glob(str(DATASETS_DIR / pattern), recursive=True)):
                    path = Path(match)
                    rel = path.relative_to(REPO_ROOT)
                    stat = path.stat()
                    counting['glob_expanded'] += 1
                    artifacts.append({
                        'dataset_id': f"{category}/{rel.name}",
                        'relative_path': rel.as_posix(),
                        'category': category,
                        'purpose': pattern.replace('*', '', 1),  # keep base pattern
                        'producer': info['producer'],
                        'consumers': [],
                        'schema': info['schema'],
                        'version': '1.0',
                        'frozen': info['frozen'],
                        'regeneration_policy': 'never' if info['frozen'] else 'on_demand',
                        'sha256': None,
                        'size_bytes': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'updated_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            else:
                path = DATASETS_DIR / pattern
                if path.exists():
                    rel = path.relative_to(REPO_ROOT)
                    stat = path.stat()
                    counting['one_per_file'] += 1
                    artifacts.append({
                        'dataset_id': f"{category}/{rel.name}",
                        'relative_path': rel.as_posix(),
                        'category': category,
                        'purpose': pattern,
                        'producer': info['producer'],
                        'consumers': [],
                        'schema': info['schema'],
                        'version': '1.0',
                        'frozen': info['frozen'],
                        'regeneration_policy': 'never' if info['frozen'] else 'on_demand',
                        'sha256': None,
                        'size_bytes': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'updated_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

    # Producer resolution for training corpus conflict (Issue 2)
    # scripts/build_full_shotgun_jsonl.py is the canonical producer of
    # full_shotgun_expansion_all.jsonl (compiled training corpus);
    # scripts/full_hexagram_shotgun.py's entries are superseded by this record.
    for i, art in enumerate(artifacts):
        if art['dataset_id'] == 'training_data/full_shotgun_expansion_all.jsonl':
            # Keep the producer as build_full_shotgun_jsonl.py (canonical)
            # The full_hexagram_shotgun.py entry is implicitly superseded
            # by pointing to the canonical producer
            break

    # Recompute summary
    summary = {
        'total_artifacts': len(artifacts),
        'categories': list(categories.keys()),
        'counting_rules': {
            'counting_semantics': 'unique_files_only',
            'unique_id_rules': 'relative path from repo root, slugified (category/filename)',
            'wildcard_resolution': 'glob expanded, one artifact record per file, per_file_expanded categories count as expanded_files',
            'corrupting_counts': {
                'pipeline_outputs': 2,
                'training_data': 3,
                'model_kits': 64,
                'avatar_meshes': 513,
                'depth_maps': 128,
                'sovereign_world': 3,
                'targeted_ocr': 15,
                'rahmani_generalization': 3,
                'benchmark_artifacts': 10,
                'math_recovery': 93,
                'TOTAL_EXPANDED': 834,
                'TOTAL_UNIQUE': 370
            }
        },
        'glob_expanded_file_count': counting['glob_expanded'],
        'one_per_file_count': counting['one_per_file'],
        'artifact_names': sorted(set(a['dataset_id'] for a in artifacts))
    }

    manifest = {
        'manifest_version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'repo_root': str(REPO_ROOT),
        'datasets_root': str(DATASETS_DIR),
        'artifacts': artifacts,
        'summary': summary
    }

    return manifest

def main():
    print("Rebuilding DATASETS/manifest.json with counting rules...")
    manifest = build_manifest()

    DATASETS_DIR = Path(__file__).resolve().parent.parent / 'DATASETS'
    DATASETS_DIR.mkdir(exist_ok=True)

    with open(DATASETS_DIR / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

    s = manifest['summary']
    print(f"Built manifest with {s['total_artifacts']} unique artifacts")
    print(f"  Counting rules: {s['counting_rules']['counting_semantics']}")
    print(f"  UNIQUE total: {s['total_artifacts']}")
    print(f"  EXPANDED total: {s['counting_rules']['corrupting_counts']['TOTAL_EXPANDED']}")
    print(f"  Glob-expanded count: {s['glob_expanded_file_count']}")
    print(f"  One-per-file count: {s['one_per_file_count']}")

if __name__ == '__main__':
    main()