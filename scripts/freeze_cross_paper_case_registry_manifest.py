#!/usr/bin/env python3
"""Freeze manifest generator for Cross-Paper Case Registry v1.

Locks:
  1. Case registry JSON (transitioned to status FROZEN).
  2. Three benchmark source PDFs.
  3. Acceptance specification v1.
  4. Immutable delimiter recovery engine baseline.
  5. Case registry validator and unit tests.
  6. Self-hash recorded.
"""
from __future__ import annotations

import sys
import json
import hashlib
from pathlib import Path
import subprocess

REPO_ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
REGISTRY_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_v1.json"
SPEC_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_delimiter_generalization_spec_v1.json"
ENGINE_PATH = REPO_ROOT / "scripts" / "delimiter_aware_structural_recovery.py"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_cross_paper_case_registry.py"
TEST_PATH = REPO_ROOT / "tests" / "test_cross_paper_case_registry.py"
MANIFEST_PATH = REPO_ROOT / "DATASETS" / "structural_preservation" / "cross_paper_case_registry_freeze_manifest.json"

EXPECTED_ENGINE_SHA = "8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1"
EXPECTED_SPEC_SHA = "188ac350a7b50166d34ac6dabcc00c7a49d540b0e01873e684739f614304b4ae"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def freeze_registry_manifest() -> dict:
    # 1. Verify engine baseline
    actual_engine_sha = sha256_file(ENGINE_PATH)
    if actual_engine_sha != EXPECTED_ENGINE_SHA:
        raise ValueError(f"Engine baseline changed! Expected {EXPECTED_ENGINE_SHA}, got {actual_engine_sha}")

    # 2. Verify spec
    actual_spec_sha = sha256_file(SPEC_PATH)
    if actual_spec_sha != EXPECTED_SPEC_SHA:
        raise ValueError(f"Spec SHA mismatch! Expected {EXPECTED_SPEC_SHA}, got {actual_spec_sha}")

    # 3. Transition registry status to FROZEN
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    reg["status"] = "FROZEN"
    reg["frozen_at"] = "2026-11-06T06:35:00Z"
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)

    actual_registry_sha = sha256_file(REGISTRY_PATH)

    # 4. Run pytest suite count
    venv_python = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    pytest_res = subprocess.run([str(venv_python), "-m", "pytest", "tests/", "-q"], capture_output=True, text=True)
    last_line = pytest_res.stdout.strip().splitlines()[-1] if pytest_res.stdout else "unknown"

    # 5. Build manifest
    manifest_data = {
        "manifest_identifier": "CROSS-PAPER-CASE-REGISTRY-FREEZE-MANIFEST-V1",
        "schema_version": "1.0",
        "frozen_at": "2026-11-06T06:35:00Z",
        "registry": {
            "path": "DATASETS/structural_preservation/cross_paper_case_registry_v1.json",
            "sha256": actual_registry_sha,
            "status": "FROZEN",
            "papers_count": len(reg["papers"]),
            "cases_count": len(reg["cases"])
        },
        "source_benchmark_pdfs": [
            {
                "paper_id": p["paper_id"],
                "paper_identifier": p["paper_identifier"],
                "path": p["pdf_rel_path"],
                "sha256": p["pdf_sha256"]
            }
            for p in reg["papers"]
        ],
        "frozen_components": {
            "delimiter_engine_baseline": {
                "path": "scripts/delimiter_aware_structural_recovery.py",
                "sha256": actual_engine_sha,
                "status": "IMMUTABLE_PRESERVED"
            },
            "acceptance_specification": {
                "path": "DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json",
                "sha256": actual_spec_sha,
                "status": "FROZEN"
            },
            "case_registry_validator": {
                "path": "scripts/validate_cross_paper_case_registry.py",
                "sha256": sha256_file(VALIDATOR_PATH)
            },
            "case_registry_tests": {
                "path": "tests/test_cross_paper_case_registry.py",
                "sha256": sha256_file(TEST_PATH)
            }
        },
        "regression_verification": {
            "test_summary": last_line,
            "exit_code": pytest_res.returncode
        },
        "manifest_self_hash": None
    }

    # Compute self-hash with manifest_self_hash set to None
    temp_json = json.dumps(manifest_data, indent=2, sort_keys=True)
    manifest_self_hash = hashlib.sha256(temp_json.encode("utf-8")).hexdigest()
    manifest_data["manifest_self_hash"] = manifest_self_hash

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return manifest_data


def main():
    print("[freeze_cross_paper_case_registry_manifest] Freezing Cross-Paper Case Registry v1...")
    m = freeze_registry_manifest()
    print("SUCCESS: Freeze manifest created!")
    print(f"Registry Status: {m['registry']['status']} (SHA-256: {m['registry']['sha256']})")
    print(f"Engine Baseline SHA-256: {m['frozen_components']['delimiter_engine_baseline']['sha256']}")
    print(f"Spec SHA-256: {m['frozen_components']['acceptance_specification']['sha256']}")
    print(f"Regression verification: {m['regression_verification']['test_summary']}")
    print(f"Manifest Self-Hash: {m['manifest_self_hash']}")


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    main()
