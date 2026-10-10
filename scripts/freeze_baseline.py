#!/usr/bin/env python3
"""
FREEZE BASELINE — save current pipeline state before contract migration.

Creates DATASETS/baseline_2026-10-09/ with:
  manifest.json          — paper IDs, versions, source hashes
  contract_version.txt   — this contract version
  parser_generation.txt  — parser commit SHA
  test_results.json      — output of running all current tests
  scoreboard_v15.json    — preserved original baseline (copied, not regenerated)
  run_metadata.json      — timestamp, Python version, environment

This is an immutable snapshot. Do not overwrite it with new-semantics output.
"""
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from math_contract import source_hash, extraction_hash, occurrence_key, CONTRACT_VERSION

BASELINE_DIR = ROOT / "DATASETS" / "baseline_2026-10-09"
CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"


def get_parser_generation() -> str:
    """Get the current git commit SHA for the parser."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"unknown ({e})"


def run_test(name: str, cmd: list[str]) -> dict[str, Any]:
    """Run a test command and capture results."""
    print(f"  Running: {name}")
    print(f"    Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "name": name,
            "command": cmd,
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:],  # tail only
            "stderr": result.stderr[-1000:],
            "passed": result.returncode == 0,
        }
    except Exception as e:
        return {
            "name": name,
            "command": cmd,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "passed": False,
        }


def build_manifest() -> dict[str, Any]:
    """Build a manifest of all papers in the corpus with source hashes."""
    manifest = {
        "corpus_dir": str(CORPUS_DIR.relative_to(ROOT)),
        "papers": [],
    }

    if not CORPUS_DIR.exists():
        return manifest

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue

        paper_id = data.get("arxiv_id", jf.stem)
        url = data.get("url", "")
        equations = data.get("equations", [])

        # Compute source hashes for each equation
        eq_manifest = []
        for i, eq in enumerate(equations):
            mathml = eq.get("mathml", "") or ""
            latex = eq.get("latex", "") or ""
            eq_manifest.append({
                "index": i,
                "source_hash": source_hash(mathml) if mathml else None,
                "extraction_hash": extraction_hash(latex, mathml),
                "mathml_len": len(mathml),
            })

        manifest["papers"].append({
            "paper_id": paper_id,
            "url": url,
            "equation_count": len(equations),
            "equations": eq_manifest,
        })

    return manifest


def main():
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("FREEZE BASELINE — pre-contract-migration snapshot")
    print("=" * 70)
    print()

    # 1. Contract version
    print("1. Writing contract_version.txt")
    (BASELINE_DIR / "contract_version.txt").write_text(
        f"{CONTRACT_VERSION}\n",
        encoding="utf-8",
    )

    # 2. Parser generation
    print("2. Writing parser_generation.txt")
    gen = get_parser_generation()
    (BASELINE_DIR / "parser_generation.txt").write_text(
        f"commit: {gen}\n"
        f"contract: {CONTRACT_VERSION}\n",
        encoding="utf-8",
    )

    # 3. Manifest
    print("3. Building corpus manifest")
    manifest = build_manifest()
    (BASELINE_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   Papers: {len(manifest['papers'])}")
    print(f"   Total equations: {sum(p['equation_count'] for p in manifest['papers'])}")

    # 4. Test results
    print("4. Running current test suite")
    tests = [
        ("test_integral_ir", [sys.executable, "scripts/test_integral_ir.py"]),
        ("test_relation_identity", [sys.executable, "scripts/test_relation_identity.py"]),
        ("test_structural_conservation", [sys.executable, "scripts/test_structural_conservation.py"]),
        ("test_nested_args", [sys.executable, "scripts/test_nested_args.py"]),
        ("test_mbox_dollar_recovery", [sys.executable, "scripts/test_mbox_dollar_recovery.py"]),
        ("test_munder_fix", [sys.executable, "scripts/test_munder_fix.py"]),
    ]
    test_results = []
    for name, cmd in tests:
        result = run_test(name, cmd)
        test_results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"    {status} (exit={result['exit_code']})")

    # npm test
    npm_result = run_test("npm_test", ["npm", "test"])
    test_results.append(npm_result)
    status = "PASS" if npm_result["passed"] else "FAIL"
    print(f"    {status} (exit={npm_result['exit_code']})")

    (BASELINE_DIR / "test_results.json").write_text(
        json.dumps(test_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # 5. Copy existing scoreboard
    print("5. Copying scoreboard_v15.json")
    src = ROOT / "DATASETS" / "scoreboard_v15.json"
    if src.exists():
        dst = BASELINE_DIR / "scoreboard_v15.json"
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print("   Copied (immutable baseline)")
    else:
        print("   WARNING: scoreboard_v15.json not found")

    # 6. Run metadata
    print("6. Writing run_metadata.json")
    metadata = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contract_version": CONTRACT_VERSION,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "parser_commit": gen,
        "tests_run": len(test_results),
        "tests_passed": sum(1 for t in test_results if t["passed"]),
    }
    (BASELINE_DIR / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print(f"BASELINE FROZEN: {BASELINE_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
