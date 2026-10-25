"""Phase 2C expanded held-out evaluation.

Evaluates diverse expressions: nested operators, similar-looking symbols,
multiple simultaneous defects, valid notational variants.

Usage:
    python scripts/phase2c_heldout_expanded_evaluate.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from phase2c_gate_library import gate_3_operator_delimiter

import importlib.util
spec = importlib.util.spec_from_file_location(
    "expanded", Path(__file__).parent.parent / "DATASETS" / "phase2c_heldout_expanded.py"
)
expanded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expanded)

EVALUATOR_COMMIT = "fe2843963e66c9131ebd442ce05b8e84b90f4374"


def main():
    tp = fp = fn = tn = 0
    results = []

    # Mutations (expected: fail)
    for i, (ref, rec, sub_type) in enumerate(expanded.held_out_mutations_expanded):
        r = gate_3_operator_delimiter(ref, rec)
        detected = r["evidence"]["substituted_operators"]
        ok = r["outcome"] == "fail"
        if ok:
            tp += 1
        else:
            fn += 1
        results.append({"case_id": f"EXP-MUT-{i+1:03d}", "expected": "mutation",
                        "outcome": r["outcome"], "subs": detected, "type": sub_type, "ok": ok})

    # Controls (expected: pass)
    for i, (ref, rec, ctrl_type) in enumerate(expanded.held_out_controls_expanded):
        r = gate_3_operator_delimiter(ref, rec)
        detected = r["evidence"]["substituted_operators"]
        ok = r["outcome"] == "pass"
        if ok:
            tn += 1
        else:
            fp += 1
        results.append({"case_id": f"EXP-CTL-{i+1:03d}", "expected": "control",
                        "outcome": r["outcome"], "subs": detected, "type": ctrl_type, "ok": ok})

    # Multi-defect (expected: fail)
    for i, (ref, rec, mt) in enumerate(expanded.held_out_multi_defect):
        r = gate_3_operator_delimiter(ref, rec)
        detected = r["evidence"]["substituted_operators"]
        ok = r["outcome"] == "fail"
        if ok:
            tp += 1
        else:
            fn += 1
        results.append({"case_id": f"EXP-MDF-{i+1:03d}", "expected": "mutation",
                        "outcome": r["outcome"], "subs": detected, "type": mt, "ok": ok})

    # Variants (expected: pass)
    for i, (ref, rec, vt) in enumerate(expanded.held_out_variants):
        r = gate_3_operator_delimiter(ref, rec)
        detected = r["evidence"]["substituted_operators"]
        ok = r["outcome"] == "pass"
        if ok:
            tn += 1
        else:
            fp += 1
        results.append({"case_id": f"EXP-VAR-{i+1:03d}", "expected": "control",
                        "outcome": r["outcome"], "subs": detected, "type": vt, "ok": ok})

    n_mut = len(expanded.held_out_mutations_expanded) + len(expanded.held_out_multi_defect)
    n_ctl = len(expanded.held_out_controls_expanded) + len(expanded.held_out_variants)

    print("=" * 60)
    print("Phase 2C Expanded Held-Out Evaluation")
    print("=" * 60)
    print(f"Evaluator commit: {EVALUATOR_COMMIT}")
    print(f"Total cases: {len(results)}")
    print(f"  Mutations: {n_mut}")
    print(f"  Controls: {n_ctl}")
    print()
    print(f"Gate 3 TP: {tp}, FN: {fn}, TN: {tn}, FP: {fp}")
    print(f"Precision: {round(tp/(tp+fp), 4) if (tp+fp) > 0 else 0.0}")
    print(f"Recall: {round(tp/(tp+fn), 4) if (tp+fn) > 0 else 0.0}")
    print(f"F1: {round(2*tp/(2*tp+fp+fn), 4) if (2*tp+fp+fn) > 0 else 0.0}")
    print()
    for r in results:
        status = "OK" if r["ok"] else "MISMATCH"
        print(f"  {r['case_id']}: {r['outcome']} (expected {r['expected']}) [{status}] {r['type']}")
        if r["subs"]:
            print(f"    subs: {r['subs']}")

    # Write results
    out = Path(__file__).parent.parent / "DATASETS" / "phase2c_heldout_expanded_results.jsonl"
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
