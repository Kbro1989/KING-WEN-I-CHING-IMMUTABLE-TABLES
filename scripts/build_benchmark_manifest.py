#!/usr/bin/env python3
"""
Build the Marker vs. King Wen benchmark manifest.

PURPOSE
=======
Freeze the inputs for the Marker benchmark: PDF hashes, HTML source hashes,
equation-level references, and version pins. This ensures both parsers
are evaluated on identical inputs.

THE MANIFEST
============
For each of the 14 baseline papers:
  - paper_id: arXiv ID
  - pdf_sha256: hash of the PDF file (both parsers use the same PDF)
  - html_source_sha256: hash of the HTML corpus file (King Wen reference)
  - reference_equation_count: number of reference equations
  - reference_equation_ids: stable IDs for each reference equation
  - kingwen_commit: the King Wen extraction code version
  - marker_version: (to be filled when Marker is run)

OUTPUT
======
DATASETS/benchmark_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_INDEX = ROOT / "DATASETS" / "zotero_pdf_index.json"
HTML_CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"
RECOVERY_DIR = ROOT / "DATASETS" / "math_recovery"
BENCHMARK_PDFS = ROOT / "DATASETS" / "benchmark_pdfs"
OUT_JSON = ROOT / "DATASETS" / "benchmark_manifest.json"

BASELINE_PAPERS = {
    "2009.00031", "2102.03334", "2605.00155", "2605.00224",
    "2605.06070", "2605.18130", "2605.22715", "2605.23244",
    "2605.24807", "2605.24856", "2605.25036", "2605.25334",
    "2605.28615", "2605.28896",
}

KINGWEN_COMMIT = "b877ca8d21"  # frozen baseline commit


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_pdf(paper_id: str) -> Path | None:
    """Find the PDF for a paper in the benchmark directory."""
    candidate = BENCHMARK_PDFS / f"{paper_id}.pdf"
    if candidate.exists():
        return candidate
    # Also check zotero corpus
    for ext in ["pdf", "PDF"]:
        for base in [Path("/c/Users/krist/Desktop/zotero/learning-corpus")]:
            if base.exists():
                for f in base.rglob(f"*{paper_id}*.{ext}"):
                    return f
    return None


def build_equation_ids(paper_id: str, count: int) -> list[str]:
    """Build stable equation IDs for a paper."""
    return [f"{paper_id}:eq{i:04d}" for i in range(1, count + 1)]


def main() -> int:
    # Load PDF index for metadata
    pdf_index = json.loads(PDF_INDEX.read_text(encoding="utf-8"))

    papers = []
    missing_pdfs = []

    for pid in sorted(BASELINE_PAPERS):
        # PDF hash
        pdf_path = find_pdf(pid)
        if pdf_path:
            pdf_hash = sha256_file(pdf_path)
        else:
            pdf_hash = None
            missing_pdfs.append(pid)

        # HTML source hash
        html_path = HTML_CORPUS / f"{pid}.json"
        if html_path.exists():
            html_hash = sha256_file(html_path)
        else:
            html_hash = None

        # Recovery file for equation count
        recovery_path = RECOVERY_DIR / f"{pid}_recovery.json"
        if recovery_path.exists():
            d = json.loads(recovery_path.read_text(encoding="utf-8"))
            eq_count = len(d.get("results", []))
        else:
            eq_count = 0

        # PDF metadata from index
        pdf_meta = pdf_index.get(pid, {})

        papers.append({
            "paper_id": pid,
            "pdf_path": str(pdf_path.relative_to(ROOT)) if pdf_path else None,
            "pdf_sha256": pdf_hash,
            "pdf_page_count": pdf_meta.get("page_count"),
            "html_source_path": str(html_path.relative_to(ROOT)) if html_path.exists() else None,
            "html_source_sha256": html_hash,
            "reference_equation_count": eq_count,
            "reference_equation_ids": build_equation_ids(pid, eq_count),
            "kingwen_commit": KINGWEN_COMMIT,
            "marker_version": None,  # to be filled when Marker is run
        })

    out = {
        "benchmark_name": "marker_vs_kingwen_14paper",
        "kingwen_commit": KINGWEN_COMMIT,
        "paper_count": len(papers),
        "total_equations": sum(p["reference_equation_count"] for p in papers),
        "missing_pdfs": missing_pdfs,
        "papers": papers,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"benchmark papers: {len(papers)}")
    print(f"total equations: {out['total_equations']}")
    if missing_pdfs:
        print(f"missing PDFs: {missing_pdfs}")
    else:
        print("all PDFs found")
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())