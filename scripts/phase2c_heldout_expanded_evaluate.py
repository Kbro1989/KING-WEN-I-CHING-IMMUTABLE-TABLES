"""Phase 2C expanded held-out evaluation.

Evaluates diverse expressions: nested operators, similar-looking symbols,
multiple simultaneous defects, valid notational variants.

The evaluator is loaded from the frozen commit fe2843963e via git show,
ensuring the recorded EVALUATOR_COMMIT matches the actual code executed.
Fail closed if the commit is unreachable or the file cannot be loaded.

Usage:
    python scripts/phase2c_heldout_expanded_evaluate.py
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

EVALUATOR_COMMIT = "fe2843963e66c9131ebd442ce05b8e84b90f4374"
REPO_ROOT = Path(__file__).parent.parent


def load_frozen_gate_library():
    """Load gate library from the frozen evaluator commit via git show.
    Fail closed if the commit is unreachable or the file cannot be loaded."""
    try:
        result = subprocess.run(
            ["git", "show", f"{EVALUATOR_COMMIT}:scripts/phase2c_gate_library.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git show failed: {result.stderr}")
        frozen_code = result.stdout
    except FileNotFoundError:
        raise RuntimeError("git not found; cannot load frozen evaluator")
    except subprocess.TimeoutExpired:
        raise RuntimeError("git show timed out")

    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / "phase2c_gate_library_frozen.py"
    tmp_path.write_text(frozen_code, encoding="utf-8")

    spec = importlib.util.spec_from_file_location("phase2c_gate_library_frozen", tmp_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    actual_hash = hashlib.sha256(frozen_code.encode("utf-8")).hexdigest()
    print(f"Evaluator commit verified: {EVALUATOR_COMMIT}")
    print(f"Gate library SHA-256 (frozen): {actual_hash}")

    return mod


try:
    gate_lib = load_frozen_gate_library()
    gate_3_operator_delimiter = gate_lib.gate_3_operator_delimiter
except RuntimeError as e:
    print(f"FATAL: {e}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location(
    "expanded", REPO_ROOT / "DATASETS" / "phase2c_heldout_expanded.py"
)
expanded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expanded)


def main():
    tp = fp = fn = tn = 0
    results = []

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

    # Non-identical controls (expected: pass)
    for i, (ref, rec, ctrl_type) in enumerate(expanded.held_out_non_identical_controls):
        r = gate_3_operator_delimiter(ref, rec)
        detected = r['evidence']['substituted_operators']
        ok = r['outcome'] == 'pass'
        if ok:
            tn += 1
        else:
            fp += 1
        results.append({'case_id': f'EXP-NIC-{i+1:03d}', 'expected': 'control',
                        'outcome': r['outcome'], 'subs': detected, 'type': ctrl_type, 'ok': ok})

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
    n_ctl = len(expanded.held_out_controls_expanded) + len(expanded.held_out_variants) + len(expanded.held_out_non_identical_controls)

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

    out = REPO_ROOT / "DATASETS" / "phase2c_heldout_expanded_results.jsonl"
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nResults: {out}")


if __name__ == "__main__":
    main()
