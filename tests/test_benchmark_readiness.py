#!/usr/bin/env python3
"""
Validate the benchmark inputs before running Marker.

HARD CHECKS
===========
1. All 14 baseline papers have PDFs with matching SHA256
2. All 14 baseline papers have HTML corpus files
3. Reference equation count matches manifest
4. All reference IDs are unique
5. No missing recovery files for baseline papers
6. HTML corpus equation count matches manifest

RUN
===
    python tests/test_benchmark_readiness.py

EXIT CODE
=========
0 = all checks pass, ready to run Marker
1 = at least one check failed
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "DATASETS" / "benchmark_manifest.json"
REF_JSONL = ROOT / "DATASETS" / "reference_equations.jsonl"
HTML_CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"
BENCHMARK_PDFS = ROOT / "DATASETS" / "benchmark_pdfs"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery"

EXPECTED_PAPERS = {
    "2009.00031", "2102.03334", "2605.00155", "2605.00224",
    "2605.06070", "2605.18130", "2605.22715", "2605.23244",
    "2605.24807", "2605.24856", "2605.25036", "2605.25334",
    "2605.28615", "2605.28896",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors = []

    # Load manifest
    if not MANIFEST.exists():
        print(f"FAIL: {MANIFEST.relative_to(ROOT)} not found")
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Check 1: all 14 papers in manifest
    manifest_papers = {p["paper_id"] for p in manifest["papers"]}
    if manifest_papers != EXPECTED_PAPERS:
        missing = EXPECTED_PAPERS - manifest_papers
        extra = manifest_papers - EXPECTED_PAPERS
        if missing:
            errors.append(f"manifest missing papers: {sorted(missing)}")
        if extra:
            errors.append(f"manifest has extra papers: {sorted(extra)}")

    # Check 2: PDF hashes match
    for p in manifest["papers"]:
        pid = p["paper_id"]
        pdf_path = BENCHMARK_PDFS / f"{pid}.pdf"
        if not pdf_path.exists():
            errors.append(f"{pid}: PDF not found at {pdf_path.relative_to(ROOT)}")
            continue
        actual_hash = sha256_file(pdf_path)
        if actual_hash != p["pdf_sha256"]:
            errors.append(f"{pid}: PDF hash mismatch (manifest={p['pdf_sha256'][:16]}... actual={actual_hash[:16]}...)")

    # Check 3: HTML corpus files exist
    for p in manifest["papers"]:
        pid = p["paper_id"]
        html_path = HTML_CORPUS / f"{pid}.json"
        if not html_path.exists():
            errors.append(f"{pid}: HTML corpus not found")

    # Check 4: reference equation count matches manifest
    if not REF_JSONL.exists():
        errors.append(f"reference equations file not found: {REF_JSONL.relative_to(ROOT)}")
    else:
        ref_count = 0
        ref_ids = set()
        for line in REF_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                ref_count += 1
                rid = r["reference_id"]
                if rid in ref_ids:
                    errors.append(f"duplicate reference ID: {rid}")
                ref_ids.add(rid)

        if ref_count != manifest["total_equations"]:
            errors.append(f"reference count mismatch: {ref_count} != {manifest['total_equations']}")

    # Check 5: no missing recovery files
    for pid in EXPECTED_PAPERS:
        recovery_path = RECOVERY_DIR / f"{pid}_recovery.json"
        if not recovery_path.exists():
            errors.append(f"{pid}: recovery file not found")

    # Check 6: HTML corpus equation count matches manifest
    for p in manifest["papers"]:
        pid = p["paper_id"]
        html_path = HTML_CORPUS / f"{pid}.json"
        if html_path.exists():
            d = json.loads(html_path.read_text(encoding="utf-8"))
            html_count = len(d.get("equations", []))
            if html_count != p["reference_equation_count"]:
                errors.append(
                    f"{pid}: HTML count {html_count} != manifest {p['reference_equation_count']}"
                )

    # Report
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: 14 papers, {manifest['total_equations']} reference equations")
    print("  all PDF hashes match manifest")
    print("  all HTML corpus files present")
    print("  all reference IDs unique")
    print("  all recovery files present")
    print("  all HTML counts match manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())