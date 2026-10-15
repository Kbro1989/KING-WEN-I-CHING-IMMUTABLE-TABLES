#!/usr/bin/env python3
"""
Build an independent reference equation set from the HTML corpus.

THE PROBLEM WITH THE CURRENT COMPARISON TABLE
=============================================
The equation_level_comparison.jsonl was generated from King Wen's recovery
files. This means:
  1. If King Wen missed an equation, it won't appear in the table
  2. Marker can't discover missed equations through this table
  3. Equation IDs are sequential, not bound to source evidence

THE SOLUTION
============
Generate the reference set from the HTML corpus (the source of truth),
not from King Wen's recovery output. Each equation gets:
  - A stable ID based on the HTML node ID (e.g., "m1", "m2")
  - The page number (from the HTML structure)
  - The MathML source (for structural comparison)
  - The LaTeX annotation (for text comparison)

This way, the reference set is independent of any parser's output.
Both King Wen and Marker are evaluated against the same reference.

OUTPUT
======
DATASETS/reference_equations.jsonl
  - one record per equation from the HTML corpus
  - stable IDs, page numbers, MathML source, LaTeX annotation
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_CORPUS = ROOT / "DATASETS" / "arxiv_html_corpus"
MANIFEST = ROOT / "DATASETS" / "benchmark_manifest.json"
OUT_JSONL = ROOT / "DATASETS" / "reference_equations.jsonl"

BASELINE_PAPERS = {
    "2009.00031", "2102.03334", "2605.00155", "2605.00224",
    "2605.06070", "2605.18130", "2605.22715", "2605.23244",
    "2605.24807", "2605.24856", "2605.25036", "2605.25334",
    "2605.28615", "2605.28896",
}


def extract_node_id(mathml: str) -> str | None:
    """Extract the node ID from a MathML tag."""
    m = re.search(r'id="([^"]+)"', mathml)
    if m:
        return m.group(1)
    return None


def extract_page_from_context(context: str) -> int | None:
    """Try to extract page number from context."""
    # Look for page markers in context
    m = re.search(r'page[:\s]+(\d+)', context, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    records = []
    missing_papers = []
    count_mismatches = []

    for pid in sorted(BASELINE_PAPERS):
        html_path = HTML_CORPUS / f"{pid}.json"
        if not html_path.exists():
            missing_papers.append(pid)
            continue

        d = json.loads(html_path.read_text(encoding="utf-8"))
        equations = d.get("equations", [])

        # Get expected count from manifest
        expected = None
        for p in manifest["papers"]:
            if p["paper_id"] == pid:
                expected = p["reference_equation_count"]
                break

        if expected is not None and len(equations) != expected:
            count_mismatches.append({
                "paper_id": pid,
                "html_count": len(equations),
                "manifest_count": expected,
            })

        for i, eq in enumerate(equations):
            mathml = eq.get("mathml", "")
            node_id = extract_node_id(mathml)
            latex = eq.get("latex", "")

            # Build stable ID: use node_id if available, else sequential
            if node_id:
                eq_id = f"{pid}:{node_id}"
            else:
                eq_id = f"{pid}:eq{i:04d}"

            record = {
                "reference_id": eq_id,
                "paper_id": pid,
                "html_index": i,
                "node_id": node_id,
                "latex": latex,
                "mathml": mathml,
                "mathml_len": eq.get("mathml_len", 0),
                "is_display": eq.get("is_display", False),
                "context_before": eq.get("context_before", ""),
                "context_after": eq.get("context_after", ""),
                "source": eq.get("source", ""),
                "page_number": None,  # HTML corpus doesn't have page numbers
                "location_evidence": "html_node" if node_id else "html_index",
            }
            records.append(record)

    # Write JSONL
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"total reference equations: {len(records)}")
    print(f"papers covered: {len(BASELINE_PAPERS) - len(missing_papers)}")
    if missing_papers:
        print(f"missing papers: {missing_papers}")
    if count_mismatches:
        print(f"count mismatches: {count_mismatches}")
    else:
        print("all counts match manifest")
    print(f"\nwrote {OUT_JSONL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())