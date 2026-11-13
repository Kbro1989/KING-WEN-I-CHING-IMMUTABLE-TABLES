#!/usr/bin/env python3
"""Inventory of DATASETS/ 3D output families for cross-output drift analysis."""
import os
import sys

REPO = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'
DATASETS = os.path.join(REPO, 'DATASETS')

if not os.path.isdir(DATASETS):
    print(f'FATAL: DATASETS/ not found at {DATASETS}')
    sys.exit(1)

print(f'DATASETS real path: {os.path.realpath(DATASETS)}')

targets = [
    'kingwen_avatar_meshes',
    'kingwen_avatar_meshes_rsc',
    'kingwen_3d_meshes',
    'kingwen_3d_kit_meshes',
    'kingwen_model_sets',
    'godot_scenes',
    'kingwen_rsmv_models',
    'collisionvis_physics',
    'quantumlab_plots',
    'depth_maps_16bit',
    'depth_pointclouds',
    'openusd_stages',
    'rsc_npc_meshes',
]

grand_total_files = 0
grand_total_bytes = 0

for name in targets:
    path = os.path.join(DATASETS, name)
    print(f'\n=== {name} ===')
    if not os.path.isdir(path):
        print('MISSING')
        continue

    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, DATASETS)
            files.append((rel, os.path.getsize(full)))

    bytes_sum = sum(s for _, s in files)
    grand_total_files += len(files)
    grand_total_bytes += bytes_sum

    print(f'Files: {len(files)}')
    print(f'Total bytes: {bytes_sum:,}')

    ext_count = {}
    for rel, size in files:
        ext = os.path.splitext(rel)[1].lower() or '[none]'
        ext_count[ext] = ext_count.get(ext, 0) + 1
    print('Extensions:')
    for ext, cnt in sorted(ext_count.items(), key=lambda x: -x[1]):
        print(f'  {ext}: {cnt}')

    print('Representative files:')
    for rel, size in sorted(files)[:6]:
        print(f'  {rel}  ({size:,} bytes)')

print(f'\n=== GRAND TOTAL: {grand_total_files} files, {grand_total_bytes:,} bytes ===')
