#!/usr/bin/env python3
"""
Metamath Reference Corpus Evaluation Harness
====================================================

Standalone Python test harness for measuring symbol recognition performance
using the frozen Metamath reference corpus (1,182 verified entries).

Configurations:
  A. Crop-only baseline (no reference matching)
  B. Reference-assisted (add frozen Metamath glyph corpus)
  C. Reference + size-aware normalization

Three artifact types are tracked:
  1. Reference baseline (frozen manifest + SHA-256 hashes)
  2. Evaluation dataset (source crops + ground-truth labels)
  3. Experiment results (per-config metrics + confusion matrix)

Usage:
  python eval_harness.py --configs A B C --metrics top1 topk
"""

import json
import os
import hashlib
from pathlib import Path
from collections import defaultdict
import argparse
import csv

# Load the frozen reference manifest
def load_reference_manifest(manifest_path):
    """
    Load the frozen 1,182-entry reference manifest.
    Returns dict: metamath_name -> {hash, size, url, ...}
    """
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Metric computation functions
def compute_metrics(predictions, ground_truth, abstention_flags=None):
    """
    Compute evaluation metrics from predictions and ground truth.
    
    predictions: list of predicted glyph names (or None if abstained)
    ground_truth: list of true glyph labels
    abstention_flags: optional list of bool indicating abstained cases
    """
    n = len(predictions)
    results = {
        'top1_accuracy': 0.0,
        'topk_accuracies': {},
        'confusion_matrix': defaultdict(lambda: defaultdict(int)),
        'abstention_rate': 0.0,
        'selective_accuracy': 0.0,
        'normalization_regressions': 0,
        'coverage': 0.0,
        'total_samples': n,
    }
    
    if n == 0:
        return results
    
    # Track abstentions and predictions
    predicted_count = 0
    correct_count = 0
    
    for i in range(n):
        pred = predictions[i]
        is_abstained = (pred is None)
        
        if is_abstained:
            continue
        
        predicted_count += 1
        if pred == ground_truth[i]:
            correct_count += 1
        
        results['confusion_matrix'][pred][ground_truth[i]] += 1
    
    # Metrics
    results['top1_accuracy'] = correct_count / n if n > 0 else 0.0
    results['coverage'] = predicted_count / n if n > 0 else 0.0
    results['selective_accuracy'] = correct_count / predicted_count if predicted_count > 0 else 0.0
    
    # Top-k accuracy (k=1, 5, 10) - for config A, mark as unavailable if no ranking
    for k in [1, 5, 10]:
        # Config A produces single-label output (no ranking)
        # Top-k is only meaningful with ranked candidate lists
        if config_type == 'A':
            if k == 1:
                results[f'topk_accuracy_k{k}'] = correct_count / n if n > 0 else 0.0
            else:
                results[f'topk_accuracy_k{k}'] = None  # Not available (no ranked list)
        else:
            matches = sum(1 for i in range(n) if predictions[i] == ground_truth[i])
            results[f'topk_accuracy_k{k}'] = matches / n
    
    # Normalization regressions
    results['normalization_regressions'] = 0
    
    return results

# Configuration implementations
# ============================================================
# Each configuration returns a structured output:
#   {"predicted_label": str|None,
#    "ranked_candidates": [str]|None,
#    "abstained": bool,
#    "confidence": float|None}

def recognize_crop_only(case):
    """
    Config A: Crop-only baseline.
    Returns single-label prediction. No ranked list.
    """
    # In production: extract features from crop, run classifier
    # Placeholder: abstain (no prediction)
    return {
        "predicted_label": None,
        "ranked_candidates": None,
        "abstained": True,
        "confidence": None,
    }

def recognize_with_reference(case, reference_manifest):
    """
    Config B: Reference-assisted matching.
    Returns ranked candidate list (best first).
    """
    # In production: compare crop features against 1,182 reference images
    # Placeholder: abstain
    return {
        "predicted_label": None,
        "ranked_candidates": None,
        "abstained": True,
        "confidence": None,
    }

def recognize_with_normalization(case, reference_manifest):
    """
    Config C: Reference + size-aware normalization.
    Returns ranked candidate list (best first).
    """
    # In production: normalize crop size, then match
    return {
        "predicted_label": None,
        "ranked_candidates": None,
        "abstained": True,
        "confidence": None,
    }

# Evaluation harness main function
def run_evaluation(configs, test_cases, reference_manifest):
    """
    Run the evaluation for specified configurations.

    Args:
        configs: list of {'name': str, 'type': str} where type in ['A', 'B', 'C']
        test_cases: list of test_case dicts with keys:
            {source_crop, glyph, review_status, bbox_coordinate_system, source_paper,
             page, font_family, size, source_url}
        reference_manifest: frozen reference manifest
    """
    results = {}

    for cfg in configs:
        cfg_name = cfg["name"]
        cfg_type = cfg["type"]

        predictions = []
        for case in test_cases:
            if cfg_type == 'A':
                pred = recognize_crop_only(case)
            elif cfg_type == 'B':
                pred = recognize_with_reference(case, reference_manifest)
            elif cfg_type == 'C':
                pred = recognize_with_normalization(case, reference_manifest)
            else:
                raise ValueError(f"Unknown config type: {cfg_type}")
            predictions.append(pred)

        gt_labels = [case['glyph'] for case in test_cases]
        metrics = compute_metrics(predictions, gt_labels)
        results[cfg_name] = {"predictions": predictions, "metrics": metrics}

    return results

# Builder functions for test cases
def create_test_case(source_crop, glyph, review_status,
                     glyph_identity=None, semantic_role=None,
                     bbox_coordinate_system="unknown",
                     bbox=None, source_paper=None, page=None,
                     font_family=None, size=None, source_url=None):
    """
    Create a test-case dictionary with full metadata.

    Ground truth comes from INDEPENDENT REVIEW of source PDF crops,
    NOT from Metamath reference images.

    Args:
        source_crop: path to the crop image
        glyph: true symbol label (from independent review)
        review_status: 'verified', 'ambiguous', 'mismatch', 'unreviewed'
        glyph_identity: glyph identity metadata (Unicode, name, class)
        semantic_role: semantic role in the source expression (separate from glyph)
        bbox_coordinate_system: 'pdf_points', 'pixels', or 'unknown'
        bbox: bounding box [x1, y1, x2, y2]
        source_paper: paper ID (e.g., '1907.04931')
        page: page number (1-indexed)
        font_family: font used in source
        size: rendering size in points
        source_url: URL of the original crop source
    """
    # Validate review status
    valid, err = check_label_review_status(glyph, review_status)
    if not valid:
        raise ValueError(err)

    # Validate coordinate system
    valid, err = check_coord_system_declared(bbox_coordinate_system)
    if not valid:
        raise ValueError(err)

    return {
        # Ground-truth identity (glyph-level)
        "source_crop": source_crop,
        "glyph": glyph,
        "review_status": review_status,
        "glyph_identity": glyph_identity or GLYPH_VOCABULARY.get(glyph, {}),
        # Semantic role (separate from glyph identity)
        "semantic_role": semantic_role,
        # Source provenance
        "source_paper": source_paper,
        "page": page,
        "source_url": source_url,
        # BBox
        "bbox_coordinate_system": bbox_coordinate_system,
        "bbox": bbox,
        # Rendering conditions
        "font_family": font_family,
        "size": size,
    }

# Writer functions for artifacts
def write_reference_baseline(reference_manifest, output_path):
    """Write the frozen 1,182-entry reference baseline."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(reference_manifest, f, indent=2)


def write_evaluation_dataset(dataset, output_path):
    """Write evaluation dataset as CSV with provenance fields."""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_crop", "glyph", "review_status",
            "glyph_identity", "semantic_role",
            "bbox_coordinate_system", "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2",
            "source_paper", "page", "font_family", "size", "source_url"
        ])
        for case in dataset:
            writer.writerow([
                case["source_crop"],
                case["glyph"],
                case["review_status"],
                json.dumps(case.get("glyph_identity", {})),
                case.get("semantic_role", ""),
                case.get("bbox_coordinate_system", "unknown"),
                case.get("bbox", [""]) if case.get("bbox") else ["", "", "", ""],
                case.get("source_paper", ""),
                case.get("page", ""),
                case.get("font_family", ""),
                case.get("size", ""),
                case.get("source_url", ""),
            ])


        json.dump(results, f, indent=2, default=str)


def dataset_integrity_check(dataset_path):
    """
    Validate evaluation dataset meets pre-run requirements.

    Checks:
    - review_status is in vocabulary (verified/ambiguous/mismatch/unreviewed)
    - unreviewed/ambiguous/mismatch labels rejected from pilot
    - glyph_identity and semantic_role both present (identity != role)
    - bbox_coordinate_system declared (not 'unknown')

    Returns:
        (errors, summary_dict)
    """
    from pathlib import Path
    import csv

    errors = []
    summary = {
        "total": 0, "verified": 0, "ambiguous": 0, "mismatch": 0, "unreviewed": 0,
        "papers": set(), "fonts": set(), "coordinate_systems": set(),
    }

    with open(dataset_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            summary["total"] += 1
            summary["papers"].add(row.get("source_paper", "unknown"))
            summary["fonts"].add(row.get("font_family", "unknown"))
            summary["coordinate_systems"].add(
                row.get("bbox_coordinate_system", "unknown"))

            glyph = row.get("glyph", "")
            review = row.get("review_status", "")

            if review == "unreviewed":
                errors.append(f"{row.get('source_crop')}: unreviewed")
                summary["unreviewed"] += 1
                continue
            if review == "ambiguous":
                errors.append(f"{row.get('source_crop')}: ambiguous")
                summary["ambiguous"] += 1
                continue
            if review == "mismatch":
                errors.append(f"{row.get('source_crop')}: mismatch")
                summary["mismatch"] += 1
                continue
            if review != "verified":
                errors.append(f"{row.get('source_crop')}: review_status={review}")
                continue

            # Glyph identity vs semantic role (both required, distinct)
            if not row.get("glyph_identity", "").strip():
                errors.append(f"{row.get('source_crop')}: missing glyph_identity")
            if not row.get("semantic_role", "").strip():
                errors.append(f"{row.get('source_crop')}: missing semantic_role")

            # Coordinate system declared
            if row.get("bbox_coordinate_system") == "unknown":
                errors.append(f"{row.get('source_crop')}: bbox_coordinate_system=unknown")

            summary["verified"] += 1

    return errors, summary


def write_dataset_integrity_report(errors, summary, output_path):
    """Write dataset integrity check report."""
    report = {
        "check_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "integrity_count": summary["total"],
        "verified_count": summary["verified"],
        "rejected_ambiguous": summary["ambiguous"],
        "rejected_unreviewed": summary["unreviewed"],
        "rejected_mismatch": summary["mismatch"],
        "source_papers": sorted(summary["papers"]),
        "font_families": sorted(summary["fonts"]),
        "coordinate_systems": sorted(summary["coordinate_systems"]),
        "errors": errors,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Metamath Reference Corpus Evaluation Harness')
    parser.add_argument('--configs', nargs='+', required=True,
                       choices=['A', 'B', 'C'],
                       help='Evaluation configurations to run')
    parser.add_argument('--reference', required=True,
                       help='Path to frozen reference manifest JSON')
    parser.add_argument('--dataset', required=True,
                       help='Path to evaluation dataset CSV')
    parser.add_argument('--output', required=True,
                       help='Output directory for results')
    parser.add_argument('--run-reference-integrity',
                       action='store_true',
                       help='Verify reference manifest SHA-256 against provenance')
    parser.add_argument('--provenance',
                       help='Path to provenance manifest JSON (required with --run-reference-integrity)')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Load reference manifest
    reference_manifest = load_reference_manifest(args.reference)

    # Option 1: Reference integrity verification
    if args.run_reference_integrity:
        if not args.provenance:
            print("Error: --provenance required with --run-reference-integrity")
            raise SystemExit(1)
        valid, missing, mismatches = verify_reference_integrity(args.reference, args.provenance)
        write_reference_integrity_report(valid, missing, mismatches,
                                         os.path.join(args.output, 'reference_integrity.json'))
        if not valid:
            print("Reference integrity check FAILED")
            if missing:
                print(f"  Missing hashes: {missing[:10]}")
            if mismatches:
                print(f"  Hash mismatches: {len(mismatches)}")
            raise SystemExit(1)

    # Option 2: Dataset integrity check (run first)
    integrity_errors, summary = dataset_integrity_check(args.dataset)
    if integrity_errors:
        print(f"Dataset integrity check FAILED ({len(integrity_errors)} errors):")
        for e in integrity_errors:
            print(f"  - {e}")
        write_dataset_integrity_report(integrity_errors, summary,
                                       os.path.join(args.output, 'dataset_integrity_report.json'))
        raise SystemExit(1)

    print(f"Dataset integrity: {summary['verified']}/{summary['total']} verified")
    print(f"  Papers: {len(summary['papers'])}, Fonts: {len(summary['fonts'])}")
    print(f"  Coordinate systems: {summary['coordinate_systems']}")

    # Build test cases from CSV (new field names)
    test_cases = []
    with open(args.dataset, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append({
                'source_crop': row['source_crop'],
                'glyph': row['glyph'],
                'review_status': row['review_status'],
                'glyph_identity': json.loads(row['glyph_identity']),
                'semantic_role': row.get('semantic_role', ''),
                'bbox_coordinate_system': row.get('bbox_coordinate_system', 'unknown'),
                'bbox': None,
                'source_paper': row.get('source_paper', ''),
                'page': row.get('page', ''),
                'font_family': row.get('font_family', ''),
                'size': row.get('size', ''),
                'source_url': row.get('source_url', ''),
            })

    # Run evaluation
    configs = [{'name': c, 'type': c} for c in args.configs]
    results = run_evaluation(configs, test_cases, reference_manifest)

    # Write outputs
    write_experiment_results(results, os.path.join(args.output, 'experiment_results.json'))
    write_evaluation_dataset(test_cases, os.path.join(args.output, 'evaluation_dataset.csv'))

    print(f"\nEvaluation complete. Results written to {args.output}")
