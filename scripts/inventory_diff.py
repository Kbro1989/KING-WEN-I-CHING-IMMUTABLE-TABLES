#!/usr/bin/env python3
"""
inventory_diff.py — Compare successive inventory snapshots.

Usage:
    python scripts/inventory_diff.py --baseline inventory/baseline_2026-11-10.jsonl \
        --compare inventory/file_inventory.jsonl

Produces a report of:
- Added files
- Removed files
- Modified files (size or hash changed)
- Authority changes
- New categories
- Deprecated files
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent

def load_jsonl(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def sha256_file(path, limit=10_000_000):
    h = hashlib.sha256()
    try:
        size = path.stat().st_size
        if size > limit:
            return f"size:{size}"
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return None

def normalize_path(p):
    return p.replace('\\', '/').strip()

def diff_inventories(baseline_path, compare_path):
    print("=" * 60)
    print("INVENTORY DIFF REPORT")
    print("=" * 60)
    print(f"Baseline: {baseline_path}")
    print(f"Compare:  {compare_path}")
    print(f"Generated: {datetime.now().isoformat()}")

    baseline = {}
    for r in load_jsonl(baseline_path):
        baseline[normalize_path(r['path'])] = r

    compare = {}
    for r in load_jsonl(compare_path):
        compare[normalize_path(r['path'])] = r

    added = {}
    removed = {}
    modified = {}
    authority_changes = {}

    for path, rec in compare.items():
        if path not in baseline:
            added[path] = rec
        else:
            base_rec = baseline[path]
            if base_rec['size_bytes'] != rec['size_bytes']:
                modified[path] = {'baseline': base_rec, 'compare': rec}
            elif base_rec.get('sha256') != rec.get('sha256'):
                modified[path] = {'baseline': base_rec, 'compare': rec}
            if base_rec.get('authority') != rec.get('authority'):
                authority_changes[path] = {
                    'before': base_rec.get('authority'),
                    'after': rec.get('authority')
                }

    for path in baseline:
        if path not in compare:
            removed[path] = baseline[path]

    print(f"\n  ADDED: {len(added)}")
    for p in sorted(added.keys()):
        print(f"    + {p}")

    print(f"\n  REMOVED: {len(removed)}")
    for p in sorted(removed.keys()):
        print(f"    - {p}")

    print(f"\n  MODIFIED: {len(modified)}")
    for p, data in sorted(modified.items()):
        print(f"    * {p} ({data['baseline']['size_bytes']} -> {data['compare']['size_bytes']} bytes)")

    print(f"\n  AUTHORITY CHANGES: {len(authority_changes)}")
    for p, change in sorted(authority_changes.items()):
        print(f"    ~ {p}: {change['before']} -> {change['after']}")

    # Summary
    total_changed = len(added) + len(removed) + len(modified) + len(authority_changes)
    print(f"\n  TOTAL CHANGES: {total_changed}")
    print(f"  {datetime.now().isoformat()}")

    return {
        'added': list(added.keys()),
        'removed': list(removed.keys()),
        'modified': list(modified.keys()),
        'authority_changes': list(authority_changes.keys()),
        'total': total_changed
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Compare inventory snapshots')
    parser.add_argument('--baseline', required=True, help='Baseline inventory JSONL')
    parser.add_argument('--compare', required=True, help='Compare inventory JSONL')
    args = parser.parse_args()

    diff_inventories(Path(args.baseline), Path(args.compare))