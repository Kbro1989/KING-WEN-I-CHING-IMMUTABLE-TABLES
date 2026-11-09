#!/usr/bin/env python3
"""
BATCH PDF MATH EXTRACTION PIPELINE
===================================
Process papers listed in paper_math_usage.jsonl through the e2e math pipeline.

Usage:
    python batch_math_pipeline.py

Output:
    DATASETS/batch_pipeline_output.jsonl   (one JSONL record per paper)
    DATASETS/batch_pipeline_manifest.json  (summary manifest)
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from e2e_math_pipeline import fetch_arxiv_html, process_paper

# Pipeline stages (for reporting)
STAGE_FETCH = "fetch"


def run_single_paper(paper, paper_idx, verbose=False):
    """
    Run the full pipeline on a single paper.
    Returns a result record.
    """
    arxiv_id = paper.get("arxiv_id", f"paper_{paper_idx}")
    record = {
        "paper_idx": paper_idx,
        "arxiv_id": arxiv_id,
        "status": "processing",
        "equations_extracted": 0,
        "solvable": 0,
        "partial": 0,
        "rejected": 0,
        "error": None,
        "timings": {},
    }

    start = time.time()
    html_content, url = fetch_arxiv_html(arxiv_id)
    record["timings"][STAGE_FETCH] = time.time() - start

    if html_content is None:
        record["status"] = "failed"
        record["error"] = "fetch_failed"
        return record

    # Process through the full e2e pipeline
    result_doc = process_paper(arxiv_id, html_content, url)

    record["equations_extracted"] = result_doc.get("total_equations", 0)
    record["solvable"] = result_doc.get("solvable", 0)
    record["partial"] = result_doc.get("partial", 0)
    record["rejected"] = result_doc.get("rejected", 0)
    record["result_document"] = result_doc
    record["url"] = url
    record["status"] = "completed"

    if verbose:
        print(f"  [{arxiv_id}] {result_doc['total_equations']} eqs, "
              f"{result_doc['solvable']} solvable, "
              f"{result_doc['partial']} partial, "
              f"{result_doc['rejected']} rejected")

    return record


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch PDF math extraction pipeline")
    parser.add_argument(
        "--corpus",
        default="DATASETS/paper_math_usage.jsonl",
        help="Path to paper metadata JSONL (default: paper_math_usage.jsonl)",
    )
    parser.add_argument(
        "--output",
        default="DATASETS/batch_pipeline_output.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=None,
        help="Process only this many papers (optional, for smoke tests)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run only the first 3 papers as a smoke test",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("BATCH PDF MATH PIPELINE — START")
    print(f"Corpus: {args.corpus}")
    print(f"Output: {args.output}")
    print("=" * 70)

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f"ERROR: Corpus not found: {corpus_path}")
        sys.exit(1)

    # Load corpus
    corpus = []
    with open(corpus_path) as f:
        for line in f:
            line = line.strip()
            if line:
                corpus.append(json.loads(line))

    total = len(corpus)
    if args.max_papers:
        total = min(total, args.max_papers)

    print(f"Total papers to process: {total}")
    print()

    results = []
    successful = 0
    error_count = 0

    for i, paper in enumerate(corpus[:total]):
        record = run_single_paper(paper, i, verbose=(i < 5 or args.smoke_test))
        results.append(record)

        if record["status"] == "completed":
            successful += 1
            if args.smoke_test:
                r = record["result_document"]
                print(f"  [OK] {i+1}/{total} {record['arxiv_id']}: "
                      f"{r['total_equations']} eqs, "
                      f"{r['solvable']} solvable, "
                      f"{r['partial']} partial, "
                      f"{r['rejected']} rejected")
        else:
            error_count += 1
            print(f"  [FAIL] {i+1}/{total} {record['arxiv_id']}: {record.get('error')}")

        # Save progress incrementally
        with open(args.output, "w") as fo:
            for r in results:
                fo.write(json.dumps(r, default=str) + "\n")

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{total} saved")

    # Build manifest
    manifest = {
        "manifest_version": "1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus": str(corpus_path),
        "total_papers": total,
        "successful": successful,
        "failed": error_count,
        "smoke_test": args.smoke_test,
        "output_file": args.output,
    }

    with open("DATASETS/batch_pipeline_manifest.json", "w") as fo:
        json.dump(manifest, fo, indent=2)

    print()
    print("=" * 70)
    print(f"BATCH PIPELINE — COMPLETE")
    print(f"  Total processed: {total}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {error_count}")
    print(f"  Output: {args.output}")
    print(f"  Manifest: DATASETS/batch_pipeline_manifest.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
