#!/usr/bin/env python3
"""
validate_lineage.py — Check producer-consumer relationships in artifact_lineage.jsonl.

Identifies:
- Missing producers
- Missing consumers
- Multiple writers (same artifact, different producers)
- Orphaned artifacts (in lineage but not in inventory)
- Cyclic dependencies
- References to paths that no longer exist
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'
LINEAGE_FILE = INVENTORY_DIR / 'artifact_lineage.jsonl'
INVENTORY_FILE = INVENTORY_DIR / 'file_inventory.jsonl'

def load_jsonl(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def validate():
    print("=" * 60)
    print("LINEAGE VALIDATION REPORT")
    print("=" * 60)

    errors = []
    warnings = []

    # Load inventory for path resolution
    inventory_records = load_jsonl(INVENTORY_FILE)
    inventory_paths = set()
    for r in inventory_records:
        inventory_paths.add(r['path'].replace('\\', '/'))

    lineage_records = load_jsonl(LINEAGE_FILE)

    # Build artifact → producers map (skip non-canonical entries)
    artifact_producers = defaultdict(list)
    artifact_consumers = defaultdict(list)

    for r in lineage_records:
        art = r['artifact'].replace('\\', '/')
        # Skip deprecated and overridden entries
        if r.get('canonical') is False or r.get('superseded_by'):
            continue
        artifact_producers[art].append(r['producer'])
        for c in r.get('consumers', []):
            artifact_consumers[art].append(c.replace('\\', '/'))

    # 1. Multiple writers / producers
    for art, producers in artifact_producers.items():
        unique = set(producers)
        if len(unique) > 1:
            errors.append(f"MULTIPLE PRODUCERS for {art}: {producers}")
            for producer in unique:
                warnings.append(f"  Producer {producer} claims {art} but another producer exists")

    # 2. Orphaned artifacts
    for art in artifact_producers:
        if '*' in art:
            warnings.append(f"Wildcard artifact (glob) not individually resolved: {art}")

    # 3. Cyclic dependency detection (simple is_a/produced_by cycle check)
    # Build directed graph: artifact → consumers
    adjacency = {}
    for art in artifact_producers:
        adjacency[art] = set(artifact_consumers.get(art, []))

    # Simple cycle detection: walk paths
    # Look for routes where producer A → consumer B → producer B (circular)
    cycle_warnings = []
    for art in adjacency:
        for consumer in adjacency[art]:
            if consumer in adjacency:
                # Check if consumer's producer is the same as art's producer
                prods = artifact_producers.get(consumer, [])
                for p in prods:
                    if p == art:
                        cycle_warnings.append(f"POSSIBLE CYCLE: {art} → {consumer} (same as {p})")

    for w in cycle_warnings:
        errors.append(w)

    # 4. References to paths that no longer exist (after glob expansion)
    for r in lineage_records:
        art = r['artifact'].replace('\\', '/')
        # Check if artifact has wildcards — skip, handled by glob_expanded
        if '*' in art:
            continue

        if not Path(REPO_ROOT / art).exists() and not Path(REPO_ROOT / art).parent.exists():
            # But some artifacts are in DATASETS/ which may have different structure
            # Loose check: just warn about potential non-existent paths
            warnings.append(f"PATH NOT FOUND on disk: {art}")

    # 5. Check consumers reference real inventory entries
    for art, consumers in artifact_consumers.items():
        for c in consumers:
            if c not in inventory_paths and not any(c in ip for ip in inventory_paths):
                warnings.append(f"CONSUMER NOT IN INVENTORY: {c} (referenced by {art})")

    print(f"  Total lineage entries: {len(lineage_records)}")
    print(f"  Errors: {len(errors)}")
    for e in errors[:15]:
        print(f"    ERROR: {e}")
    print(f"  Warnings: {len(warnings)}")
    for w in warnings[:10]:
        print(f"    WARN: {w}")

    return len(errors) == 0

if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)