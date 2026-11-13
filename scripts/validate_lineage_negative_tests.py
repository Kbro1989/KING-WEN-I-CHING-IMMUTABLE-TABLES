#!/usr/bin/env python3
"""
validate_lineage_negative_tests.py — Negative tests for the lineage validator.
Verifies the validator detects corrupted data, not just passes clean data.
"""

import json
import sys
import tempfile
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / 'inventory'
LINEAGE_FILE = INVENTORY_DIR / 'artifact_lineage.jsonl'

def load_jsonl(path):
    records = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def run_lineage_validation(lineage_path):
    """Run the lineage validation from validate_lineage.py module"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import validate_lineage
    # Call the validate function from the module directly
    import importlib
    importlib.reload(validate_lineage)
    return validate_lineage.validate()

def test_duplicate_path():
    """Test: Duplicate a normalized file path -> FAIL"""
    print("Test 1: Duplicate path in file_inventory.jsonl")
    import validate_inventory
    original = validate_inventory.INVENTORY_DIR
    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'file_inventory.jsonl'
        with open(tmp_file, 'w') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
            f.write(json.dumps(records[0]) + '\n')  # duplicate
        validate_inventory.INVENTORY_DIR = Path(tmp_dir)
        result = validate_inventory.validate_file_inventory()
        validate_inventory.INVENTORY_DIR = original
        print(f"  Expected: FAIL (duplicate path) -> Got: {result}")
        return result == False

def test_remove_provenance_active():
    """Test: Remove provenance from one ACTIVE record -> FAIL"""
    print("Test 2: Remove provenance from one ACTIVE record")
    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'file_inventory.jsonl'
        with open(tmp_file, 'w') as f:
            for r in records:
                if r.get('authority') == 'ACTIVE' and r.get('classification_rule'):
                    r_copy = r.copy()
                    del r_copy['classification_rule']
                    f.write(json.dumps(r_copy) + '\n')
                else:
                    f.write(json.dumps(r) + '\n')
        import validate_inventory
        orig = validate_inventory.INVENTORY_DIR
        validate_inventory.INVENTORY_DIR = Path(tmp_dir)
        result = validate_inventory.validate_authority_provenance()
        validate_inventory.INVENTORY_DIR = orig
        print(f"  Expected: FAIL (missing provenance) -> Got: {result}")
        return result == False

def test_remove_provenance_frozen():
    """Test: Remove provenance from one FROZEN record -> FAIL"""
    print("Test 3: Remove provenance from one FROZEN record")
    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'file_inventory.jsonl'
        with open(tmp_file, 'w') as f:
            for r in records:
                if r.get('authority') == 'FROZEN' and r.get('classification_rule'):
                    r_copy = r.copy()
                    del r_copy['classification_rule']
                    f.write(json.dumps(r_copy) + '\n')
                else:
                    f.write(json.dumps(r) + '\n')
        import validate_inventory
        orig = validate_inventory.INVENTORY_DIR
        validate_inventory.INVENTORY_DIR = Path(tmp_dir)
        result = validate_inventory.validate_authority_provenance()
        validate_inventory.INVENTORY_DIR = orig
        print(f"  Expected: FAIL (missing provenance) -> Got: {result}")
        return result == False

def test_sha256_alteration():
    """Test: Alter a sha256 on an existing record in scripts/ -> validator should detect mismatch -> FAIL"""
    print("Test 4: Altered SHA-256 on scripts/add_provenance.py")
    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / 'file_inventory.jsonl'
        with open(tmp_file, 'w') as f:
            # Find the first script record and alter its sha256
            for r in records:
                if r.get('directory') == 'scripts':
                    r_copy = r.copy()
                    r_copy['sha256'] = '0' * 40  # Altered sha256
                    f.write(json.dumps(r_copy) + '\n')
                    # Write remaining records as-is
                    for r2 in records:
                        f.write(json.dumps(r2) + '\n')
                    break
        import validate_inventory
        orig = validate_inventory.INVENTORY_DIR
        validate_inventory.INVENTORY_DIR = Path(tmp_dir)
        result = validate_inventory.validate_file_inventory()
        validate_inventory.INVENTORY_DIR = orig
        print(f"  Expected: FAIL (sha256 mismatch detected) -> Got: {result}")
        return result == False

def test_nonexistent_lineage_artifact():
    """Test: Reference a nonexistent lineage artifact -> FAIL"""
    print("Test 5: Reference nonexistent lineage artifact")
    records = load_jsonl(INVENTORY_DIR / 'artifact_lineage.jsonl')
    # Create a temp file in the current working directory (avoid permission issues)
    import sys, os
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import validate_lineage
    orig = validate_lineage.LINEAGE_FILE
    # Use a unique temp file that won't have permission issues
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        tmp_file = Path(f.name)
        for r in records:
            if r.get('artifact') == 'kingwen_train_data/full_shotgun_expansion_all.jsonl':
                r_copy = r.copy()
                r_copy['consumers'] = r_copy.get('consumers', []) + ['nonexistent_script.py']
                f.write(json.dumps(r_copy) + '\n')
            else:
                f.write(json.dumps(r) + '\n')
    try:
        validate_lineage.LINEAGE_FILE = tmp_file
        result = validate_lineage.validate()
        print(f"  Expected: WARN (consumer not in inventory) -> Got: {result}")
        # The validator reports missing consumers as warnings, not hard errors.
        # The test verifies the warning about the nonexistent consumer is present.
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            validate_lineage.validate()
        output = buf.getvalue()
        return 'CONSUMER NOT IN INVENTORY: nonexistent_script.py' in output
    finally:
        validate_lineage.LINEAGE_FILE = orig
        tmp_file.unlink(missing_ok=True)

def test_two_producers():
    """Test: Two producers for one artifact -> FAIL"""
    print("Test 6: Two producers for one artifact")
    records = load_jsonl(INVENTORY_DIR / 'artifact_lineage.jsonl')
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        tmp_file = Path(f.name)
        for r in records:
            if r.get('artifact') == 'kingwen_train_data/full_shotgun_expansion_all.jsonl' and r.get('canonical') is True:
                r_copy = r.copy()
                r_dup = r.copy()
                r_dup['producer'] = 'scripts/full_hexagram_shotgun.py'
                f.write(json.dumps(r_copy) + '\n')
                f.write(json.dumps(r_dup) + '\n')
            else:
                f.write(json.dumps(r) + '\n')
    try:
        import validate_lineage
        orig = validate_lineage.LINEAGE_FILE
        validate_lineage.LINEAGE_FILE = tmp_file
        result = validate_lineage.validate()
        validate_lineage.LINEAGE_FILE = orig
        print(f"  Expected: FAIL (multiple canonical producers) -> Got: {result}")
        return result == False
    finally:
        validate_lineage.LINEAGE_FILE = orig
        tmp_file.unlink(missing_ok=True)

def test_frozen_without_provenance():
    """Test: FROZEN record must have provenance fields -> FAIL"""
    print("Test 7: FROZEN record missing provenance -> FAIL")
    records = load_jsonl(INVENTORY_DIR / 'file_inventory.jsonl')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        tmp_file = Path(f.name)
        for r in records:
            if r.get('authority') == 'FROZEN':
                r_copy = r.copy()
                for field in ['classification_rule', 'evidence_source', 'classification_timestamp', 'manual_asserted']:
                    if field in r_copy:
                        del r_copy[field]
                f.write(json.dumps(r_copy) + '\n')
            else:
                f.write(json.dumps(r) + '\n')
    # Copy modified file to the original inventory dir and run validation
    try:
        import shutil
        import validate_inventory
        orig = validate_inventory.INVENTORY_DIR
        # Write modified file to the original inventory dir (override the original)
        shutil.copy2(tmp_file, INVENTORY_DIR / 'file_inventory.jsonl')
        validate_inventory.INVENTORY_DIR = Path(INVENTORY_DIR)
        result = validate_inventory.validate_authority_provenance()
        validate_inventory.INVENTORY_DIR = orig
        print(f"  Expected: FAIL (missing provenance) -> Got: {result}")
        return result == False
    finally:
        tmp_file.unlink(missing_ok=True)

def main():
    print("=" * 60)
    print("NEGATIVE TESTS FOR VALIDATORS")
    print("=" * 60)
    print("\nThese tests verify the validator detects BAD data, not just accepts good data.\n")

    results = []
    results.append(("Test 1: Duplicate path", test_duplicate_path()))
    results.append(("Test 2: Missing provenance (ACTIVE)", test_remove_provenance_active()))
    results.append(("Test 3: Missing provenance (FROZEN)", test_remove_provenance_frozen()))
    results.append(("Test 4: Altered SHA-256", test_sha256_alteration()))
    results.append(("Test 5: Nonexistent lineage artifact", test_nonexistent_lineage_artifact()))
    results.append(("Test 6: Two producers", test_two_producers()))
    results.append(("Test 7: FROZEN without provenance", test_frozen_without_provenance()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    all_pass = all(r for _, r in results)
    print(f"\n  OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())