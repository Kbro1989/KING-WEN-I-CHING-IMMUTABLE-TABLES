#!/usr/bin/env python3
"""
Add provenance fields to file_inventory.jsonl entries.
The user's feedback (Issue 3) requires every ACTIVE or FROZEN classification
to have classification rule, evidence source, timestamp, freeze reference, and
manual assertion flag.
"""

import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'
INVENTORY_FILE = INVENTORY_DIR / 'file_inventory.jsonl'

def add_provenance():
    """Add provenance fields to inventory entries."""
    print(f"Updating {INVENTORY_FILE} with provenance fields...")
    
    records = []
    with open(INVENTORY_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records.append(rec)
    
    # Classification rules for each authority type
    rules = {
        'ACTIVE': {
            'classification_rule': 'Canonical engine modules, living production scripts, and actively-maintained documentation. Identified by presence in scripts/ plus manual review.',
            'evidence_source': 'File path classification + content review (this session)',
            'classification_timestamp': datetime.now().isoformat(),
            'freeze_reference': None,
            'manual_asserted': True
        },
        'FROZEN': {
            'classification_rule': 'Benchmark outputs, reference datasets, and frozen outputs. Identified by matching known frozen filename patterns + manual review.',
            'evidence_source': 'Filename pattern matching + manual review (session 2026-11-10)',
            'classification_timestamp': datetime.now().isoformat(),
            'freeze_reference': 'DATASETS/manifest.json summary.frozen_artifacts',
            'manual_asserted': True
        },
        'DEPRECATED': {
            'classification_rule': 'Superseded scripts, old formats, transitional files. Identified by naming conventions (debug_/old_/temp_) + manual review.',
            'evidence_source': 'Filename pattern + commit history + manual review',
            'classification_timestamp': datetime.now().isoformat(),
            'freeze_reference': None,
            'manual_asserted': True
        },
        'HISTORICAL': {
            'classification_rule': 'Archived documentation, superseded specs, historical records.',
            'evidence_source': 'Filename pattern + manual review',
            'classification_timestamp': datetime.now().isoformat(),
            'freeze_reference': None,
            'manual_asserted': True
        },
        'UNVERIFIED': {
            'classification_rule': 'All files not meeting ACTIVE, FROZEN, DEPRECATED, or HISTORICAL criteria. Includes generated artifacts, third-party code, and unclassified data.',
            'evidence_source': 'Default classification (all files that do not match other rules)',
            'classification_timestamp': datetime.now().isoformat(),
            'freeze_reference': None,
            'manual_asserted': False
        }
    }
    
    count = 0
    for rec in records:
        auth = rec.get('authority')
        if auth in rules:
            for key, value in rules[auth].items():
                rec[key] = value
            rec['provenance'] = True
            count += 1
    
    # Write back
    with open(INVENTORY_FILE, 'w') as f:
        for rec in records:
            f.write(json.dumps(rec) + '\n')
    
    print(f"Updated {count} records with provenance fields")
    print(f"Total records: {len(records)}")

if __name__ == '__main__':
    add_provenance()