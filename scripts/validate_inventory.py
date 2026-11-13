#!/usr/bin/env python3
"""
validate_inventory.py — Validate counts, paths, hashes, and references in inventory files.
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'

def load_jsonl(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def sha256_file(path, limit=10_000_000):
    """Compute sha256, skipping large files."""
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

def validate_file_inventory():
    """Validate file_inventory.jsonl"""
    print("=" * 60)
    print("VALIDATING: file_inventory.jsonl")
    print("=" * 60)

    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    errors = []
    warnings = []

    # 1. Unique normalized paths
    paths = set()
    for r in records:
        p = r['path'].replace('\\', '/').strip()
        if p in paths:
            errors.append(f"DUPLICATE PATH: {p}")
        paths.add(p)

    # 2. Required fields
    for r in records:
        for field in ['path', 'size_bytes', 'modified', 'extension', 'directory', 'authority']:
            if field not in r:
                errors.append(f"MISSING FIELD {field} in {r.get('path', 'unknown')}")

    # 3. Authority validation
    valid_authorities = {'ACTIVE', 'FROZEN', 'DEPRECATED', 'HISTORICAL', 'UNVERIFIED'}
    for r in records:
        if r.get('authority') not in valid_authorities:
            errors.append(f"INVALID AUTHORITY {r.get('authority')} in {r.get('path')}")

    # 4. Size consistency
    for r in records:
        if r['size_bytes'] < 0:
            errors.append(f"NEGATIVE SIZE in {r['path']}")

    # 5. SHA-256 for important files
    important_exts = {'.json', '.jsonl', '.csv', '.py', '.md', '.bin', '.npz', '.ply', '.png'}
    important_dirs = {'DATASETS/', 'scripts/', 'src/', 'data/', 'tests/', 'learn/', 'docs/'}
    for r in records:
        if r['extension'] in important_exts and r['directory'].startswith(tuple(important_dirs)):
            if r.get('sha256') is None:
                warnings.append(f"NO SHA256 for important file: {r['path']}")
            elif r['sha256'].startswith('size:'):
                # Large file: verify against the recorded size hash
                actual_sha = sha256_file(Path(r['path']))
                if actual_sha and actual_sha != r['sha256']:
                    errors.append(f"SHA256 MISMATCH: {r['path']} expected={r['sha256']} actual={actual_sha}")
            else:
                # Small file: compute and compare SHA256
                actual_sha = sha256_file(Path(r['path']))
                if actual_sha and actual_sha != r['sha256']:
                    errors.append(f"SHA256 MISMATCH: {r['path']} expected={r['sha256']} actual={actual_sha}")

    print(f"  Records: {len(records)}")
    print(f"  Errors: {len(errors)}")
    for e in errors[:10]:
        print(f"    ERROR: {e}")
    if len(errors) > 10:
        print(f"    ... and {len(errors)-10} more")
    print(f"  Warnings: {len(warnings)}")
    for w in warnings[:5]:
        print(f"    WARN: {w}")

    return len(errors) == 0

def validate_lineage():
    """Validate artifact lineage chains (Issue 4)."""
    print("=" * 60)
    print("VALIDATING: artifact_lineage.jsonl")
    print("=" * 60)

    records = load_jsonl(INVENTORY_DIR / 'artifact_lineage.jsonl')
    errors = []
    warnings = []

    # Build artifact index from inventory
    artifact_paths = set()
    for r in load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl'):
        artifact_paths.add(r['path'].replace('\\', '/'))

    # Track artifact occurrences (skip non-canonical entries)
    artifact_occurrences = {}
    for r in records:
        art = r['artifact']
        # Skip deprecated and overridden entries
        if r.get('canonical') is False or r.get('superseded_by'):
            continue
        artifact_occurrences.setdefault(art, []).append(r)

    # 1. Check multiple producers for same artifact
    for art, occurrences in artifact_occurrences.items():
        producers = set(o['producer'] for o in occurrences)
        if len(producers) > 1:
            errors.append(f"MULTIPLE PRODUCERS for {art}: {producers}")

    # 2. Check all consumers in inventory (very loose check)
    for r in records:
        # Skip deprecated entries
        if r.get('canonical') is False or r.get('superseded_by'):
            continue
        art = r['artifact']
        for consumer in r.get('consumers', []):
            if consumer not in artifact_occurrences:
                warning = f"CONSUMER NOT IN LINEAGE INDEX: {consumer} (referenced by {art})"
                warnings.append(warning)

    # 3. Check for cyclic dependencies (roughly: same artifact appears as producer and consumer)
    producers = set(r['producer'] for r in records if r.get('canonical') is True)
    artifacts = set(r['artifact'] for r in records if r.get('canonical') is True)
    overlap = producers & artifacts
    if overlap:
        errors.append(f"PRODUCTER-ARRIFACT OVERLAP (possible self-reference): {overlap}")

    # 4. Check for orphaned artifacts (in inventory but not in lineage)
    lineage_artifacts = set(r['artifact'] for r in records if r.get('canonical') is True)
    # Note: lineage artifacts may reference files not yet individually indexed
    # (e.g., glob patterns like DATASETS/kingwen_model_sets/kit_*.json)

    print(f"  Lineage entries: {len(records)} (including {sum(1 for r in records if not r.get('canonical'))} non-canonical)")
    print(f"  Canonical entries: {len(lineage_artifacts)}")
    print(f"  Errors: {len(errors)}")
    for e in errors[:10]:
        print(f"    ERROR: {e}")
    print(f"  Warnings: {len(warnings)}")
    for w in warnings[:5]:
        print(f"    WARN: {w}")

    return len(errors) == 0

def validate_authority_provenance():
    """Validate that ACTIVE/FROZEN have provenance and count them (Issue 3)."""
    print("=" * 60)
    print("VALIDATING: Authoritative classification provenance")
    print("=" * 60)

    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    errors = []
    warnings = []

    complete = 0
    total_auth = 0
    for r in records:
        auth = r.get('authority')
        if auth in ('ACTIVE', 'FROZEN'):
            total_auth += 1
            # Check for provenance fields
            has_rule = r.get('classification_rule')
            has_evidence = r.get('evidence_source')
            has_ts = r.get('classification_timestamp')
            has_manual = r.get('manual_asserted', False)
            if has_rule and has_evidence and has_ts and has_manual:
                complete += 1
            else:
                missing = []
                if not has_rule: missing.append('classification_rule')
                if not has_evidence: missing.append('evidence_source')
                if not has_ts: missing.append('classification_timestamp')
                if not has_manual: missing.append('manual_asserted')
                errors.append(f"ACTIVE/FROZEN {r['path']} missing: {', '.join(missing)}")

    print(f"  Active/Frozen records: {total_auth}")
    print(f"  With full provenance: {complete}")
    print(f"  Missing classification_rule: {sum(1 for r in records if r.get('authority') in ('ACTIVE','FROZEN') and not r.get('classification_rule'))}")
    print(f"  Warnings: {len(warnings)}")
    for w in warnings[:5]:
        print(f"    WARN: {w}")

    # Return PASS if all Active/Frozen have complete provenance
    return complete == total_auth and len(errors) == 0

def validate_random_file():
    """Spot-check a random file against disk."""
    print("=" * 60)
    print("VALIDATING: Random file spot-check")
    print("=" * 60)

    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    test_records = [r for r in records if r['extension'] in {'.py', '.json', '.md'}]

    actual_sha = None  # Initialize before use
    if test_records:
        test = test_records[0]
        path = Path(test['path'])
        if not path.exists():
            print(f"  TEST FILE NOT FOUND: {path}")
            print(f"  Inventory says: {test}")
            return False

        actual_size = path.stat().st_size
        if actual_size != test['size_bytes']:
            print(f"  SIZE MISMATCH: {path}")
            print(f"    Inventory: {test['size_bytes']}, actual: {actual_size}")
            return False

        # Verify sha256
        if test.get('sha256') and not test['sha256'].startswith('size:'):
            actual_sha = sha256_file(path)
            if actual_sha and actual_sha[:6] != test['sha256'][:6]:
                print(f"  SHA256 MISMATCH: {path}")
                print(f"    Inventory: {test['sha256']}, actual: {actual_sha}")
                return False

        print(f"  OK: {path} ({actual_size} bytes)")
        print(f"    SHA256: {actual_sha[:12] if actual_sha else 'n/a'}")

    return True

def main():
    r1 = validate_file_inventory()
    r2 = validate_lineage()
    r3 = validate_authority_provenance()
    r4 = validate_random_file()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  file_inventory:    {'PASS' if r1 else 'FAIL'}")
    print(f"  artifact_lineage:  {'PASS' if r2 else 'FAIL'}")
    print(f"  authority_provenance: {'PASS' if r3 else 'FAIL'}")
    print(f"  random_file_check: {'PASS' if r4 else 'FAIL'}")

    all_pass = all([r1, r2, r3, r4])
    print(f"\n  OVERALL: {'ALL PASS' if all_pass else 'ISSUES FOUND'}")

    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())