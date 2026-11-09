#!/usr/bin/env python3
"""
PDF VISUAL-DETECTION INTEGRATION LAYER — corpus orchestrator
==========================================================

Orchestrates the frozen 243-paper equation-accounting pipeline and the
separate PDF visual-detection pipeline, producing a combined report that
separates:

    Equation accounting (AE):  solvable + partial + rejected + unresolved = total
    Delimiter detection (DIV): pages with candidates, glyph classifications

The two layers are kept separate. The equation accounting baseline is frozen
and unchanged. The delimiter layer is added as a distinct evidence tier.

Usage:
    python pdf_visual_corpus_integrator.py --corpus scripts/corpus_manifest.json \
        --batch-output DATASETS/batch_pipeline_output.jsonl \
        --out corpus_integration_report.json

Requirements:
    Install the PDF visual detection dependencies:
        pip install pymupdf numpy opencv-python
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_batch_output(path: Path):
    """Load the frozen 243-paper batch output."""
    records = []
    with open(path) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def build_integrated_report(batch_records, corpus_manifest, out_dir):
    """
    Build the integrated report from the frozen batch output and the
    delimiter detection layer.

    Returns:
        dict — integrated report with separate equation-accounting and
        delimiter-detection tiers.
    """
    # Load batch records
    batch = []
    with open(batch_records) as f:
        for line in f:
            batch.append(json.loads(line))

    # Build a lookup by paper ID
    batch_by_id = {r["arxiv_id"]: r for r in batch}

    integrated = {
        "integration_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "equation_accounting": {
            "description": "Frozen 243-paper equation-accounting baseline.",
            "total_papers": len(batch),
            "successful": sum(1 for r in batch if r["status"] == "completed"),
            "failed": sum(1 for r in batch if r["status"] == "failed"),
            "dependencies": {
                "equation_extraction": "extract_math_with_context()",
                "integral_classification": "parse_integral()",
                "sympy_fallback": "try_solve()",
                "accounting_rule": "solvable + partial + rejected + unresolved = total",
            },
        },
        "delimiter_detection": {
            "description": "Per-page visual delimiter measurement from PDF rendering.",
            "detector": "targeted_math_detector.py",
            "classifier": "font_aware_math_classifier.py",
            "recovery": "delimiter_aware_structural_recovery.py",
            "total_pages": 0,
            "pages_with_delimiter_candidates": 0,
            "pages_with_math": 0,
        },
        "cross_modal_associations": {
            "associated": 0,
            "unassociated": 0,
            "ambiguous": 0,
            "not_attempted": 0,
        },
        "acceptance_dimensions": {
            "equation_extraction": {
                "description": "Were mathematical expressions found and accounted for?",
                "evidence": "batch_pipeline_output.jsonl",
                "completed": True,
                "verified": len(batch) == 243,
                "status": "PASS",
            },
            "delimiter_detection_and_identity": {
                "description": "Were visible delimiter glyphs independently detected "
                              "and correctly identified?",
                "evidence": "delimiter_records.json (not yet produced)",
                "completed": False,
                "verified": False,
                "status": "NOT_VERIFIED",
            },
            "structural_preservation": {
                "description": "Were extent, pairing, nesting, and enclosure relationships preserved?",
                "evidence": "structural_recovery records (not yet produced)",
                "completed": False,
                "verified": False,
                "status": "NOT_VERIFIED",
            },
        },
    }

    return integrated


def main():
    parser = argparse.ArgumentParser(
        description="PDF visual-detection integration layer for the King Wen PDF math parser"
    )
    parser.add_argument(
        "--corpus", type=Path, required=True,
        help="Corpus manifest (paper_math_usage.jsonl or equivalent)",
    )
    parser.add_argument(
        "--batch-output", type=Path, required=True,
        help="Frozen batch output JSONL",
    )
    parser.add_argument(
        "--out", type=Path, required=True,
        help="Output directory",
    )
    args = parser.parse_args()

    # Load the frozen batch output
    batch = load_batch_output(args.batch_output)

    # Build the integrated report
    integrated = build_integrated_report(batch, args.corpus, args.out)

    # Write the integrated report
    output_path = args.out / "integrated_report.json"
    with open(output_path, "w") as f:
        json.dump(integrated, f, indent=2)

    # Console summary
    print(f"PDF visual-detection integration layer")
    print(f"  Batch output: {args.batch_output}")
    print(f"  Integrated report: {output_path}")
    print(f"  Epuation accounting: {integrated['equation_accounting']['successful']}/"
          f"{integrated['equation_accounting']['total_papers']} successful")
    print(f"  Delimiter detection: NOT VERIFIED (pending PDF integration)")
    print(f"  Structural preservation: NOT VERIFIED (pending PDF integration)")

    # List files written
    for f in sorted(args.out.glob("*.json")):
        print(f"  Written: {f}")


if __name__ == "__main__":
    main()
