#!/usr/bin/env python3
"""
Phase 2C — Baseline Comparison Script

Runs both Phase 2B (frozen) and Phase 2C evaluations against:
1. Phase 2B adversarial challenges (20 challenges, frozen)
2. Phase 2C Gate 3 mutation tests (4 mutations + 8 controls)

Produces per-gate comparison report with:
- Detections, misses, false positives, valid controls
- Before/after delta for each gate
"""

import json
import subprocess
import sys
from pathlib import Path
from collections import Counter


def run_evaluation(script: str, pilot_json: str, recognized_json: str, output_jsonl: str) -> list:
    """Run an evaluation script and return parsed results."""
    result = subprocess.run([
        sys.executable, script, pilot_json, recognized_json, output_jsonl
    ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    if result.returncode != 0:
        print(f"ERROR running {script}: {result.stderr}")
        return []
    # Parse output JSONL
    results = []
    with open(output_jsonl, encoding='utf-8') as f:
        for line in f:
            results.append(json.loads(line))
    return results


def load_challenges(path: str) -> dict:
    """Load challenge expected outcomes."""
    challenges = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            ch = json.loads(line)
            challenges[ch.get('challenge_id', ch.get('mutation_id', ch.get('control_id')))] = ch
    return challenges


def evaluate_gate_results(results: list, challenges: dict, gate_name: str) -> dict:
    """Evaluate gate results against expected outcomes."""
    tp = fp = fn = tn = 0  # true pos, false pos, false neg, true neg
    details = []

    for r in results:
        cid = r['candidate_id']
        ch = challenges.get(cid)
        if not ch:
            continue

        actual = r[gate_name]
        expected = ch.get('expected_gate_3_outcome', ch.get('expected_gate_failures', []))

        # Normalize expected to set of failing gates
        if isinstance(expected, list):
            expected_fail = gate_name in expected
        else:
            expected_fail = (expected == 'fail')

        actual_fail = (actual == 'fail')

        if expected_fail and actual_fail:
            tp += 1
        elif not expected_fail and actual_fail:
            fp += 1
        elif expected_fail and not actual_fail:
            fn += 1
        else:
            tn += 1

        details.append({
            'id': cid,
            'expected_fail': expected_fail,
            'actual_fail': actual_fail,
            'match': (expected_fail == actual_fail),
        })

    return {
        'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
        'precision': tp / (tp + fp) if (tp + fp) else 0,
        'recall': tp / (tp + fn) if (tp + fn) else 0,
        'details': details,
    }


def main():
    repo_root = Path(__file__).parent.parent

    # ─── Paths ────────────────────────────────────────────────────────────
    phase2b_eval = repo_root / 'scripts' / 'phase2b_evaluate_gates.py'
    phase2c_eval = repo_root / 'scripts' / 'phase2c_evaluate_gates.py'

    # Frozen Phase 2B adversarial challenges
    adv_challenges = repo_root / 'DATASETS' / 'phase2b_adversarial_challenge.jsonl'

    # Phase 2C Gate 3 mutations and controls
    mut_path = repo_root / 'DATASETS' / 'phase2c_gate3_mutations.jsonl'
    ctl_path = repo_root / 'DATASETS' / 'phase2c_gate3_controls.jsonl'

    # Pilot selections
    pilot_2b = repo_root / 'DATASETS' / 'phase2b_adversarial_pilot.json'
    pilot_2c = repo_root / 'DATASETS' / 'phase2c_gate3_pilot.json'  # to create

    # Outputs
    out_2b = repo_root / 'DATASETS' / 'phase2c_comparison_2b.jsonl'
    out_2c = repo_root / 'DATASETS' / 'phase2c_comparison_2c.jsonl'

    # ─── Build Phase 2C pilot (mutations + controls) ─────────────────────
    with open(mut_path, encoding='utf-8') as f:
        mutations = [json.loads(line) for line in f]
    with open(ctl_path, encoding='utf-8') as f:
        controls = [json.loads(line) for line in f]

    pilot_2c_data = {
        'benchmark': 'phase2c_gate3_calibration',
        'candidates': []
    }
    for m in mutations:
        pilot_2c_data['candidates'].append({
            'reference_id': m['mutation_id'],
            'paper_id': 'phase2c_gate3',
            'latex': m['reference_latex'],
            'is_display': False,
            'html_index': -1,
        })
    for c in controls:
        pilot_2c_data['candidates'].append({
            'reference_id': c['control_id'],
            'paper_id': 'phase2c_gate3',
            'latex': c['reference_latex'],
            'is_display': False,
            'html_index': -1,
        })

    with open(pilot_2c, 'w', encoding='utf-8') as f:
        json.dump(pilot_2c_data, f, indent=2)

    # Build recognized outputs
    rec_2b = {}
    with open(adv_challenges, encoding='utf-8') as f:
        for line in f:
            ch = json.loads(line)
            rec_2b[ch['challenge_id']] = ch['synthetic_latex']

    rec_2c = {}
    for m in mutations:
        rec_2c[m['mutation_id']] = m['synthetic_latex']
    for c in controls:
        rec_2c[c['control_id']] = c['synthetic_latex']

    with open(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2c.json', 'w', encoding='utf-8') as f:
        json.dump(rec_2c, f, indent=2)

    with open(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2b.json', 'w', encoding='utf-8') as f:
        json.dump(rec_2b, f, indent=2)

    # ─── Run Phase 2B evaluation on adversarial challenges ───────────────
    print("=== Running Phase 2B (frozen) on adversarial challenges ===")
    results_2b = run_evaluation(
        str(phase2b_eval),
        str(pilot_2b),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2b.json'),
        str(out_2b)
    )

    # ─── Run Phase 2C evaluation on adversarial challenges ───────────────
    print("=== Running Phase 2C on adversarial challenges ===")
    results_2c_adv = run_evaluation(
        str(phase2c_eval),
        str(pilot_2b),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2b.json'),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_2c_adv.jsonl')
    )

    # ─── Run Phase 2B on Gate 3 mutations/controls ──────────────────────
    print("=== Running Phase 2B on Gate 3 mutations/controls ===")
    results_2b_cal = run_evaluation(
        str(phase2b_eval),
        str(pilot_2c),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2c.json'),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_2b_cal.jsonl')
    )

    # ─── Run Phase 2C on Gate 3 mutations/controls ──────────────────────
    print("=== Running Phase 2C on Gate 3 mutations/controls ===")
    results_2c_cal = run_evaluation(
        str(phase2c_eval),
        str(pilot_2c),
        str(repo_root / 'DATASETS' / 'phase2c_comparison_recognized_2c.json'),
        str(out_2c)
    )

    # ─── Load expected outcomes ─────────────────────────────────────────
    adv_challenges_dict = {}
    with open(adv_challenges, encoding='utf-8') as f:
        for line in f:
            ch = json.loads(line)
            adv_challenges_dict[ch['challenge_id']] = ch

    cal_challenges = {}
    for m in mutations:
        cal_challenges[m['mutation_id']] = m
    for c in controls:
        cal_challenges[c['control_id']] = c

    # ─── Evaluate Gate 3 on calibration set ─────────────────────────────
    print("\n=== Gate 3 Calibration Results ===")
    eval_2b = evaluate_gate_results(results_2b_cal, cal_challenges, 'gate_3_operator_delimiter')
    eval_2c = evaluate_gate_results(results_2c_cal, cal_challenges, 'gate_3_operator_delimiter')

    print(f"Phase 2B: TP={eval_2b['tp']}, FP={eval_2b['fp']}, FN={eval_2b['fn']}, TN={eval_2b['tn']}")
    print(f"  Precision: {eval_2b['precision']:.3f}, Recall: {eval_2b['recall']:.3f}")
    print(f"Phase 2C: TP={eval_2c['tp']}, FP={eval_2c['fp']}, FN={eval_2c['fn']}, TN={eval_2c['tn']}")
    print(f"  Precision: {eval_2c['precision']:.3f}, Recall: {eval_2c['recall']:.3f}")

    # Detail failures
    print("\nPhase 2B misses (FN):")
    for d in eval_2b['details']:
        if d['expected_fail'] and not d['actual_fail']:
            print(f"  {d['id']}: expected fail, got pass")

    print("\nPhase 2C misses (FN):")
    for d in eval_2c['details']:
        if d['expected_fail'] and not d['actual_fail']:
            print(f"  {d['id']}: expected fail, got pass")

    print("\nPhase 2C false positives (FP):")
    for d in eval_2c['details']:
        if not d['expected_fail'] and d['actual_fail']:
            print(f"  {d['id']}: expected pass, got fail")

    # ─── Gate 3 on adversarial challenges ───────────────────────────────
    print("\n=== Gate 3 on Adversarial Challenges ===")
    eval_2b_adv = evaluate_gate_results(results_2b, adv_challenges_dict, 'gate_3_operator_delimiter')
    eval_2c_adv = evaluate_gate_results(results_2c_adv, adv_challenges_dict, 'gate_3_operator_delimiter')

    print(f"Phase 2B: TP={eval_2b_adv['tp']}, FP={eval_2b_adv['fp']}, FN={eval_2b_adv['fn']}")
    print(f"Phase 2C: TP={eval_2c_adv['tp']}, FP={eval_2c_adv['fp']}, FN={eval_2c_adv['fn']}")

    # ─── All gates comparison on adversarial ============================
    print("\n=== All Gates on Adversarial (2B vs 2C) ===")
    for gate in ['gate_1_geometry', 'gate_2_token_alignment', 'gate_3_operator_delimiter', 'gate_4_literal_vs_semantic', 'gate_5_provenance']:
        e2b = evaluate_gate_results(results_2b, adv_challenges_dict, gate)
        e2c = evaluate_gate_results(results_2c_adv, adv_challenges_dict, gate)
        print(f"\n{gate}:")
        print(f"  2B: TP={e2b['tp']} FP={e2b['fp']} FN={e2b['fn']} TN={e2b['tn']} P={e2b['precision']:.3f} R={e2b['recall']:.3f}")
        print(f"  2C: TP={e2c['tp']} FP={e2c['fp']} FN={e2c['fn']} TN={e2c['tn']} P={e2c['precision']:.3f} R={e2c['recall']:.3f}")
        print(f"  Delta: TP={e2c['tp']-e2b['tp']:+d} FP={e2c['fp']-e2b['fp']:+d} FN={e2c['fn']-e2b['fn']:+d} TN={e2c['tn']-e2b['tn']:+d}")

    # ─── Summary report ─────────────────────────────────────────────────
    report = {
        'gate3_calibration': {
            'phase2b': {'tp': eval_2b['tp'], 'fp': eval_2b['fp'], 'fn': eval_2b['fn'], 'tn': eval_2b['tn'],
                        'precision': eval_2b['precision'], 'recall': eval_2b['recall']},
            'phase2c': {'tp': eval_2c['tp'], 'fp': eval_2c['fp'], 'fn': eval_2c['fn'], 'tn': eval_2c['tn'],
                        'precision': eval_2c['precision'], 'recall': eval_2c['recall']},
            'delta': {
                'tp': eval_2c['tp'] - eval_2b['tp'],
                'fp': eval_2c['fp'] - eval_2b['fp'],
                'fn': eval_2c['fn'] - eval_2b['fn'],
                'tn': eval_2c['tn'] - eval_2b['tn'],
                'precision': eval_2c['precision'] - eval_2b['precision'],
                'recall': eval_2c['recall'] - eval_2b['recall'],
            }
        },
        'adversarial_all_gates': {}
    }

    for gate in ['gate_1_geometry', 'gate_2_token_alignment', 'gate_3_operator_delimiter', 'gate_4_literal_vs_semantic', 'gate_5_provenance']:
        e2b = evaluate_gate_results(results_2b, adv_challenges_dict, gate)
        e2c = evaluate_gate_results(results_2c_adv, adv_challenges_dict, gate)
        report['adversarial_all_gates'][gate] = {
            'phase2b': {'tp': e2b['tp'], 'fp': e2b['fp'], 'fn': e2b['fn'], 'tn': e2b['tn'],
                        'precision': e2b['precision'], 'recall': e2b['recall']},
            'phase2c': {'tp': e2c['tp'], 'fp': e2c['fp'], 'fn': e2c['fn'], 'tn': e2c['tn'],
                        'precision': e2c['precision'], 'recall': e2c['recall']},
            'delta': {
                'tp': e2c['tp'] - e2b['tp'],
                'fp': e2c['fp'] - e2b['fp'],
                'fn': e2c['fn'] - e2b['fn'],
                'tn': e2c['tn'] - e2b['tn'],
            }
        }

    with open(repo_root / 'DATASETS' / 'phase2c_comparison_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Comparison report saved to DATASETS/phase2c_comparison_report.json ===")


if __name__ == '__main__':
    main()