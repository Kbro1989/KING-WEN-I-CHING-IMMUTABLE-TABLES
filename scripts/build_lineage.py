#!/usr/bin/env python3
"""
Build Artifact Lineage - Producer → Artifact → Consumer chains
"""

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'

def load_inventory():
    inventory = []
    with open(INVENTORY_DIR / 'file_inventory.jsonl', 'r') as f:
        for line in f:
            inventory.append(json.loads(line))
    return inventory

def build_artifact_lineage(inventory):
    """Build producer→artifact→consumer chains"""
    lineage = []
    
    # Known producer→artifact mappings from workflow paths and docs
    producer_map = {
        'scripts/full_hexagram_shotgun.py': {
            'produces': ['kingwen_train_data/full_shotgun_expansion_all.jsonl', 'DATASETS/expanded_states.csv', 'DATASETS/resolved_states.csv'],
            'consumes': ['emotional_engine.py', 'kingwen_ternary_tables_complete.py']
        },
        'scripts/enrich_kit_models.py': {
            'produces': ['DATASETS/kingwen_model_sets/kit_*.json'],
            'consumes': ['kingwen_train_data/full_shotgun_expansion_all.jsonl']
        },
        'scripts/bridge_depth_anything_v2.py': {
            'produces': ['DATASETS/depth_maps_16bit/', 'DATASETS/depth_pointclouds/'],
            'consumes': ['DATASETS/quantumlab_plots/']
        },
        'scripts/generate_avatar_meshes.py': {
            'produces': ['DATASETS/kingwen_avatar_meshes/', 'DATASETS/kingwen_avatar_mesh_manifest.json'],
            'consumes': ['DATASETS/kingwen_model_sets/', 'DATASETS/depth_pointclouds/']
        },
        'scripts/generate_sovereign_world.py': {
            'produces': ['DATASETS/kingwen_sovereign_world_topology.json', 'DATASETS/godot_scenes/', 'DATASETS/openusd_stages/'],
            'consumes': ['DATASETS/kingwen_avatar_meshes/', 'DATASETS/kingwen_model_sets/']
        },
        'scripts/targeted_depth_ocr.py': {
            'produces': ['DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/targeted_ocr_results.json'],
            'consumes': ['DATASETS/benchmark_pdfs/']
        },
        'scripts/evaluate_rahmani_generalization.py': {
            'produces': ['DATASETS/structural_preservation/rahmani_1212.0957_generalization_evaluation.json'],
            'consumes': ['DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/targeted_ocr_results.json', 'DATASETS/structural_preservation/rahmani_1212.0957_generalization_target.json']
        },
        'scripts/build_full_shotgun_jsonl.py': {
            'produces': ['kingwen_train_data/full_shotgun_expansion_all.jsonl', 'kingwen_train_data/full_shotgun_expansion_corpus_enriched.jsonl'],
            'consumes': ['scripts/full_hexagram_shotgun.py', 'kingwen_train_data/kingwen_expansion_wrapper.py']
        },
        'scripts/expand_server.py': {
            'produces': ['POST /expand endpoint (512-state payload)'],
            'consumes': ['scripts/full_hexagram_shotgun.py']
        },
        'scripts/bridge_depth_anything_v2.py': {
            'produces': ['DATASETS/depth_maps_16bit/', 'DATASETS/depth_pointclouds/'],
            'consumes': ['DATASETS/quantumlab_plots/']
        },
        'scripts/generate_avatar_meshes.py': {
            'produces': ['DATASETS/kingwen_avatar_meshes/', 'DATASETS/kingwen_avatar_mesh_manifest.json'],
            'consumes': ['DATASETS/kingwen_model_sets/', 'DATASETS/depth_pointclouds/']
        },
        'scripts/generate_sovereign_world.py': {
            'produces': ['DATASETS/kingwen_sovereign_world_topology.json', 'DATASETS/godot_scenes/', 'DATASETS/openusd_stages/'],
            'consumes': ['DATASETS/kingwen_avatar_meshes/', 'DATASETS/kingwen_model_sets/']
        },
        'scripts/targeted_depth_ocr.py': {
            'produces': ['DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/targeted_ocr_results.json'],
            'consumes': ['DATASETS/benchmark_pdfs/']
        },
        'scripts/evaluate_rahmani_generalization.py': {
            'produces': ['DATASETS/structural_preservation/rahmani_1212.0957_generalization_evaluation.json'],
            'consumes': ['DATASETS/PDF_FIDELITY_RENDERINGS/targeted_ocr/targeted_ocr_results.json', 'DATASETS/structural_preservation/rahmani_1212.0957_generalization_target.json']
        },
        'scripts/build_full_shotgun_jsonl.py': {
            'produces': ['kingwen_train_data/full_shotgun_expansion_all.jsonl', 'kingwen_train_data/full_shotgun_expansion_corpus_enriched.jsonl'],
            'consumes': ['scripts/full_hexagram_shotgun.py', 'kingwen_train_data/kingwen_expansion_wrapper.py']
        },
    }
    
    lineage = []
    
    for producer, info in producer_map.items():
        for artifact in info['produces']:
            lineage.append({
                'artifact': artifact,
                'producer': producer,
                'consumers': info.get('consumes', []),
                'authority': 'ACTIVE',
                'type': 'pipeline_artifact'
            })
    
    return lineage

def main():
    print("Building artifact lineage...")
    lineage = build_artifact_lineage([])
    
    REPO_ROOT = Path(__file__).resolve().parent.parent
    INVENTORY_DIR = REPO_ROOT / 'inventory'
    output_dir = REPO_ROOT / 'inventory'
    output_dir.mkdir(exist_ok=True)
    
    with open(INVENTORY_DIR / 'artifact_lineage.jsonl', 'w') as f:
        for entry in lineage:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Built {len(lineage)} lineage entries")
    for entry in lineage:
        print(f"  {entry['producer']} → {entry['artifact']}")

if __name__ == '__main__':
    import json
    from pathlib import Path
    
    REPO_ROOT = Path(__file__).resolve().parent.parent
    INVENTORY_DIR = REPO_ROOT / 'inventory'
    
    main()