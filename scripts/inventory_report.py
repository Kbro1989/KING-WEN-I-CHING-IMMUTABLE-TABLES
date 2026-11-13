#!/usr/bin/env python3
"""
inventory_report.py — Generate human-readable summaries from machine-readable inventory.

Usage:
    python scripts/inventory_report.py --inventory inventory/file_inventory.jsonl \
        --output report.txt
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
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

def generate_report():
    print("=" * 60)
    print("KING WEN REPOSITORY INVENTORY REPORT")
    print("=" * 60)

    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')

    # Authority summary
    authority_summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0})
    for r in records:
        auth = r['authority']
        authority_summary[auth]['count'] += 1
        authority_summary[auth]['total_bytes'] += r['size_bytes']

    print(f"\nSCAN DATE: {datetime.now().isoformat()}")
    print(f"TOTAL FILES INDEXED: {len(records)}")

    print("\n" + "=" * 50)
    print("AUTHORITY CLASSIFICATION")
    print("=" * 50)
    for auth in ['ACTIVE', 'FROZEN', 'UNVERIFIED', 'DEPRECATED', 'HISTORICAL']:
        data = authority_summary.get(auth, {'count': 0, 'total_bytes': 0})
        print(f"  {auth:12} {data['count']:>8} files  {data['total_bytes']:>14,} bytes")

    # Top extensions
    extension_summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0})
    for r in records:
        ext = r['extension'] or '(none)'
        extension_summary[ext]['count'] += 1
        extension_summary[ext]['total_bytes'] += r['size_bytes']

    print("\n" + "=" * 50)
    print("TOP 15 EXTENSIONS")
    print("=" * 50)
    for ext, data in sorted(extension_summary.items(), key=lambda x: x[1]['count'], reverse=True)[:15]:
        print(f"  {ext:15} {data['count']:>8} files  {data['total_bytes']:>14,} bytes")

    # Top directories
    dir_summary = defaultdict(lambda: {'count': 0, 'total_bytes': 0})
    for r in records:
        d = r['directory']
        dir_summary[d]['count'] += 1
        dir_summary[d]['total_bytes'] += r['size_bytes']

    print("\n" + "=" * 50)
    print("TOP 15 DIRECTORIES")
    print("=" * 50)
    for d, data in sorted(dir_summary.items(), key=lambda x: x[1]['count'], reverse=True)[:15]:
        print(f"  {d:40} {data['count']:>8} files  {data['total_bytes']:>14,} bytes")

    # Frozen artifacts
    frozen = [r for r in records if r['authority'] == 'FROZEN']
    active = [r for r in records if r['authority'] == 'ACTIVE']

    print("\n" + "=" * 50)
    print("FROZEN ARTIFACTS (representative)")
    print("=" * 50)
    for r in frozen[:10]:
        print(f"  {r['path']} ({r['size_bytes']} bytes)")

    print("\n" + "=" * 50)
    print("ACTIVE SCRIPTS")
    print("=" * 50)
    for r in active[:15]:
        print(f"  {r['path']} ({r['size_bytes']} bytes)")

    # Check for stale entries
    stale = [r for r in records if r['authority'] == 'UNVERIFIED' and r['size_bytes'] > 100_000]
    if stale:
        print(f"\n  NOTICE: {len(stale)} UNVERIFIED files > 100KB (may need classification)")

    # Human-readable summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"""
  Files: {len(records)}
  Total size: {sum(r['size_bytes'] for r in records):,} bytes
  Active + Frozen: {len([r for r in records if r['authority'] in ('ACTIVE', 'FROZEN')])} ({len([r for r in records if r['authority'] in ('ACTIVE', 'FROZEN')]) / len(records) * 100:.4f}% of total)
  UNVERIFIED: {len([r for r in records if r['authority'] == 'UNVERIFIED'])}
  DEPRECATED: {len([r for r in records if r['authority'] == 'DEPRECATED'])}
  HISTORICAL: {len([r for r in records if r['authority'] == 'HISTORICAL'])}
  Unexplained: {len(records) - len([r for r in records if r['authority'] in ('ACTIVE', 'FROZEN')]) - len([r for r in records if r['authority'] == 'UNVERIFIED']) - len([r for r in records if r['authority'] == 'DEPRECATED']) - len([r for r in records if r['authority'] == 'HISTORICAL'])}
""")

    return {
        'files': len(records),
        'total_bytes': sum(r['size_bytes'] for r in records),
        'directories': len(set(r['directory'] for r in records)),
        'active': len(active),
        'frozen': len(frozen),
        'unverified': len([r for r in records if r['authority'] == 'UNVERIFIED'])
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate human-readable inventory report')
    parser.add_argument('--inventory', default=None, help='Inventory JSONL (default: internal path)')
    parser.add_argument('--output', default=None, help='Output file (default: stdout)')
    args = parser.parse_args()

    report = generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"INVENTORY REPORT\n")
            f.write(f"{'='*40}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"Files: {report['files']}\n")
            f.write(f"Total bytes: {report['total_bytes']:,}\n")
            f.write(f"Directories: {report['directories']}\n")
            f.write(f"Active: {report['active']}, Frozen: {report['frozen']}, Unverified: {report['unverified']}\n")
        print(f"\nReport written to {args.output}")
    else:
        print(json.dumps(report, indent=2))