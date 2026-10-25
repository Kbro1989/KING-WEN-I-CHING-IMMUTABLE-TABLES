"""Phase 2C held-out evaluation script.

Evaluates unseen operator substitutions and valid expressions against Gates 1-5.
Uses frozen evaluator commit fe2843963e and test fixtures.

Usage:
    python scripts/phase2c_heldout_evaluate.py
"""
import sys
import json
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from phase2c_gate_library import (
    gate_2_token_alignment,
    gate_3_operator_delimiter,
    gate_5_provenance,
    normalize_latex,
    detect_operator_substitution,
)

# Import held-out test cases
import importlib.util
spec = importlib.util.spec_from_file_location(
    "heldout", Path(__file__).parent.parent / "DATASETS" / "phase2c_heldout_test_cases.py"
)
heldout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(heldout)

EVALUATOR_COMMIT = "fe2843963e66c9131ebd442ce05b8e84b90f4374"


def evaluate_case(ref, rec, expected, case_id):
    """Evaluate a single case against Gates 2 and 3."""
    g2 = gate_2_token_alignment(ref, rec)
    g3 = gate_3_operator_delimiter(ref, rec)

    # Determine if substitution was detected
    subs_detected = g3["evidence"]["substituted_operators"]

    return {
        "case_id": case_id,
        "reference": ref,
        "recognized": rec,
        "expected": expected,
        "gate_2_outcome": g2["outcome"],
        "gate_3_outcome": g3["outcome"],
        "substitutions_detected": subs_detected,
        "gate_2_reorder": g2["evidence"]["reorder_detected"],
        "gate_2_order_violation": g2["evidence"]["order_violation"],
        "gate_2_missing": g2["evidence"]["missing_token_count"],
        "gate_2_extra": g2["evidence"]["extra_token_count"],
    }


def main():
    results = []
    tp = fp = fn = tn = 0

    # Evaluate mutations (expected: fail)
    for i, (ref, rec, sub_type) in enumerate(heldout.held_out_mutations):
        case_id = f"HO-MUT-{i+1:03d}"
        r = evaluate_case(ref, rec, "mutation", case_id)
        r["substitution_type"] = sub_type
        results.append(r)
        if r["gate_3_outcome"] == "fail":
            tp += 1
        else:
            fn += 1

    # Evaluate controls (expected: pass)
    for i, (ref, rec, ctrl_type) in enumerate(heldout.held_out_controls):
        case_id = f"HO-CTL-{i+1:03d}"
        r = evaluate_case(ref, rec, "control", case_id)
        r["control_type"] = ctrl_type
        results.append(r)
        if r["gate_3_outcome"] == "pass":
            tn += 1
        else:
            fp += 1

    # Evaluate ambiguous cases
    for i, (ref, rec, amb_type) in enumerate(heldout.held_out_ambiguous):
        case_id = f"HO-AMB-{i+1:03d}"
        r = evaluate_case(ref, rec, "ambiguous", case_id)
        r["ambiguous_type"] = amb_type
        results.append(r)

    # Summary
    summary = {
        "evaluator_commit": EVALUATOR_COMMIT,
        "total_cases": len(results),
        "mutations": len(heldout.held_out_mutations),
        "controls": len(heldout.held_out_controls),
        "ambiguous": len(heldout.held_out_ambiguous),
        "gate_3_tp": tp,
        "gate_3_fn": fn,
        "gate_3_tn": tn,
        "gate_3_fp": fp,
        "gate_3_precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0,
        "gate_3_recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0,
        "gate_3_f1": round(2 * tp / (2 * tp + fp + fn), 4) if (2 * tp + fp + fn) > 0 else 0.0,
    }

    # Write results
    output_path = Path(__file__).parent.parent / "DATASETS" / "phase2c_heldout_results.jsonl"
    with open(output_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    summary_path = Path(__file__).parent.parent / "DATASETS" / "phase2c_heldout_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("=" * 60)
    print("Phase 2C Held-Out Evaluation")
    print("=" * 60)
    print(f"Evaluator commit: {EVALUATOR_COMMIT}")
    print(f"Total cases: {len(results)}")
    print(f"  Mutations: {len(heldout.held_out_mutations)}")
    print(f"  Controls: {len(heldout.held_out_controls)}")
    print(f"  Ambiguous: {len(heldout.held_out_ambiguous)}")
    print()
    print(f"Gate 3 TP: {tp}, FN: {fn}, TN: {tn}, FP: {fp}")
    print(f"Precision: {summary['gate_3_precision']}")
    print(f"Recall: {summary['gate_3_recall']}")
    print(f"F1: {summary['gate_3_f1']}")
    print()
    print("Per-case results:")
    for r in results:
        status = "OK" if (
            (r["expected"] == "mutation" and r["gate_3_outcome"] == "fail") or
            (r["expected"] == "control" and r["gate_3_outcome"] == "pass")
        ) else "MISMATCH"
        print(f"  {r['case_id']}: {r['gate_3_outcome']} (expected {r['expected']}) [{status}]")
        if r.get("substitutions_detected"):
            print(f"    substitutions: {r['substitutions_detected']}")

    print(f"\nResults written to: {output_path}")
    print(f"Summary written to: {summary_path}")


if __name__ == "__main__":
    main()
