#!/usr/bin/env python3
"""
Update file_inventory.jsonl with pipeline-aware authority classifications.

Maps authority based on pipeline position from artifact_lineage.jsonl:
- Canonical producer scripts -> ACTIVE
- Deprecated producer scripts -> DEPRECATED
- Pipeline artifact outputs -> FROZEN (immutable) or ACTIVE (living)
- Consumer scripts -> ACTIVE
- Documentation in docs/ -> ACTIVE (if current) or HISTORICAL (if archived)
- Tests -> ACTIVE
- Everything else -> UNVERIFIED (preserves existing for unclassified)
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'
INVENTORY_FILE = INVENTORY_DIR / 'file_inventory.jsonl'
LINEAGE_FILE = INVENTORY_DIR / 'artifact_lineage.jsonl'


def load_jsonl(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(path, records):
    with open(path, 'w') as f:
        for r in records:
            f.write(json.dumps(r) + '\n')


def normalize_path(p):
    return p.replace('\\', '/')


def main():
    # Load lineage for pipeline authority mapping
    lineage = load_jsonl(LINEAGE_FILE)

    # Build pipeline authority mapping
    canonical_producers = set()
    deprecated_producers = set()
    pipeline_artifacts = {}  # artifact -> authority
    consumer_scripts = set()

    for entry in lineage:
        if entry.get('canonical'):
            canonical_producers.add(normalize_path(entry['producer']))
            artifact = normalize_path(entry['artifact'])
            # Outputs of canonical producers are FROZEN (immutable pipeline artifacts)
            pipeline_artifacts[artifact] = entry.get('authority', 'FROZEN')
        else:
            deprecated_producers.add(normalize_path(entry['producer']))

        for consumer in entry.get('consumers', []):
            consumer_scripts.add(normalize_path(consumer))

    # Additional pipeline authority points from known structure
    # Source scripts in scripts/ that are not in lineage but are part of the pipeline
    additional_active_scripts = {
        'scripts/validate_inventory.py',
        'scripts/validate_lineage.py',
        'scripts/inventory_diff.py',
        'scripts/inventory_report.py',
        'scripts/add_provenance.py',
        'scripts/build_inventory_fast.py',
        'scripts/build_lineage.py',
        'scripts/build_datasets_manifest.py',
        'scripts/rebuild_manifest.py',
        'scripts/validate_lineage_negative_tests.py',
        'scripts/inventory_schema.json',  # not a script but part of inventory system
    }

    # Documentation in docs/ that is current
    # Tests that are active
    # Config/data files

    print(f"Canonical producers: {len(canonical_producers)}")
    print(f"Deprecated producers: {len(deprecated_producers)}")
    print(f"Pipeline artifacts: {len(pipeline_artifacts)}")
    print(f"Consumer scripts: {len(consumer_scripts)}")

    # Load inventory
    records = load_jsonl(INVENTORY_FILE)
    print(f"Loaded {len(records)} inventory records")

    # Track changes
    changes = Counter()

    # Update authority based on pipeline position
    for r in records:
        path = normalize_path(r['path'])
        directory = normalize_path(r.get('directory', '.'))

        old_authority = r.get('authority', 'UNVERIFIED')
        new_authority = old_authority

        # 1. Canonical producer scripts -> ACTIVE
        if path in canonical_producers:
            new_authority = 'ACTIVE'

        # 2. Deprecated producer scripts -> DEPRECATED
        elif path in deprecated_producers:
            new_authority = 'DEPRECATED'

        # 3. Pipeline artifacts (outputs) -> FROZEN
        elif path in pipeline_artifacts:
            new_authority = pipeline_artifacts[path]

        # 4. Consumer scripts -> ACTIVE
        elif path in consumer_scripts:
            new_authority = 'ACTIVE'

        # 5. Additional active scripts
        elif path in additional_active_scripts:
            new_authority = 'ACTIVE'

        # 6. Documentation in docs/ -> ACTIVE (current)
        elif directory.startswith('docs/'):
            # Check if it's archived/historical (could add logic)
            new_authority = 'ACTIVE'

        # 7. Tests -> ACTIVE
        elif directory.startswith('tests/'):
            new_authority = 'ACTIVE'

        # 8. Scripts in scripts/ that are pipeline-related -> ACTIVE
        elif directory.startswith('scripts/'):
            # If it's a .py file and not already classified, check if it's a known pipeline script
            if r.get('extension') == '.py' and path not in pipeline_artifacts:
                # Default to ACTIVE for Python scripts in scripts/
                new_authority = 'ACTIVE'

        # 9. Data files in DATASETS/ that are pipeline outputs -> FROZEN
        elif directory.startswith('DATASETS/'):
            # If it matches a known pipeline artifact pattern
            # For now, keep as UNVERIFIED unless explicitly in pipeline_artifacts
            pass

        # 10. Source code in src/ -> ACTIVE (if part of runtime)
        elif directory.startswith('src/'):
            if r.get('extension') in {'.py', '.ts', '.tsx'}:
                new_authority = 'ACTIVE'

        # 11. Learn/specs -> HISTORICAL (they're specs, not living code)
        elif directory.startswith('learn/specs'):
            new_authority = 'HISTORICAL'

        # 12. Scripts in scripts/output, scripts/scratch -> DEPRECATED (build artifacts)
        elif directory.startswith('scripts/output') or directory.startswith('scripts/scratch'):
            new_authority = 'DEPRECATED'

        if new_authority != old_authority:
            r['authority'] = new_authority
            changes[old_authority + '->' + new_authority] += 1

    # Save updated inventory
    save_jsonl(INVENTORY_FILE, records)

    print("\nAuthority changes:")
    for change, count in sorted(changes.items()):
        print(f"  {change}: {count}")

    # Print final distribution
    final_auth = Counter(r.get('authority', 'NONE') for r in records)
    print("\nFinal authority distribution:")
    for auth, count in final_auth.most_common():
        print(f"  {auth}: {count}")


if __name__ == '__main__':
    main()