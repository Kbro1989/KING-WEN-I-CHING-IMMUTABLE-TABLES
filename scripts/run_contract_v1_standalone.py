#!/usr/bin/env python3
"""Standalone runner for test_math_pdf_association_contract_v1.py (no pytest needed)."""
import importlib.util
import sys

REPO_ROOT = "/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES"

spec = importlib.util.spec_from_file_location(
    "suit",
    f"{REPO_ROOT}/scripts/test_math_pdf_association_contract_v1.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tests = []
for name in dir(mod):
    if name.startswith("test_"):
        tests.append((name, getattr(mod, name)))

passed = 0
failed = []
for name, fn in tests:
    try:
        fn()
        passed += 1
        print(f"PASS {name}")
    except AssertionError as e:
        failed.append(name)
        print(f"FAIL {name}: {e}")
    except Exception as e:
        failed.append(name)
        print(f"ERROR {name}: {type(e).__name__}: {e}")

print(f"\n{passed} passed, {len(failed)} failed")
if failed:
    print("Failed:", failed)
    sys.exit(1)
