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

    # Check 7: HTML source hash matches manifest (content integrity)
    # Fails if the hash is missing from the manifest, not just if it mismatches.
    for p in manifest["papers"]:
        pid = p["paper_id"]
        html_path = HTML_CORPUS / f"{pid}.json"
        if not html_path.exists():
            continue  # already caught by check 3
        manifest_hash = p.get("html_source_sha256")
        if not manifest_hash:
            errors.append(f"{pid}: html_source_sha256 missing from manifest")
            continue
        actual_hash = sha256_file(html_path)
        if actual_hash != manifest_hash:
            errors.append(
                f"{pid}: HTML hash mismatch "
                f"(manifest={manifest_hash[:16]}... actual={actual_hash[:16]}...)"
            )

    # Check 8: reference equations match HTML corpus node-by-node
    # Verifies node identity (reference_id contains the correct node_id
    # that appears in the HTML MathML), not just sequential LaTeX match.
    if REF_JSONL.exists():
        ref_by_paper = {}
        for line in REF_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                pid = r["paper_id"]
                if pid not in ref_by_paper:
                    ref_by_paper[pid] = []
                ref_by_paper[pid].append(r)

        for p in manifest["papers"]:
            pid = p["paper_id"]
            html_path = HTML_CORPUS / f"{pid}.json"
            if html_path.exists() and pid in ref_by_paper:
                d = json.loads(html_path.read_text(encoding="utf-8"))
                html_eqs = d.get("equations", [])
                ref_eqs = ref_by_paper[pid]

                if len(html_eqs) != len(ref_eqs):
                    errors.append(
                        f"{pid}: reference count {len(ref_eqs)} != HTML count {len(html_eqs)}"
                    )
                    continue

                for i, (html_eq, ref_eq) in enumerate(zip(html_eqs, ref_eqs)):
                    html_latex = html_eq.get("latex", "")
                    ref_latex = ref_eq.get("latex", "")
                    ref_id = ref_eq.get("reference_id", "")
                    ref_node_id = ref_eq.get("node_id")
                    html_mathml = html_eq.get("mathml", "")

                    # Verify node identity: reference_id must contain the node_id
                    # that appears in the HTML MathML
                    if ref_node_id:
                        if ref_node_id not in html_mathml:
                            errors.append(
                                f"{pid}: eq {i} node_id {ref_node_id} not in HTML MathML"
                            )
                        if ref_id != f"{pid}:{ref_node_id}":
                            errors.append(
                                f"{pid}: eq {i} reference_id {ref_id} != {pid}:{ref_node_id}"
                            )

                    # Then compare LaTeX content
                    if html_latex != ref_latex:
                        errors.append(
                            f"{pid}: eq {i} LaTeX mismatch "
                            f"(html={html_latex[:40]}... ref={ref_latex[:40]}...)"
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
    print("  all HTML source hashes match manifest")
    print("  reference equations match HTML corpus node-by-node")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())