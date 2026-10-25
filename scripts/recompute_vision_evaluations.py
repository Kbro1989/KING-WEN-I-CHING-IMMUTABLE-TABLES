#!/usr/bin/env python3
"""
Recompute Multi-Paper Generalization Evaluations
================================================
Re-evaluates multi_paper_experiment_padding_3_2.jsonl and
multi_paper_baseline_padding15.jsonl using the repaired, candidate-specific
evaluate_output() evaluator with separated metrics and ground-truth references.

Generates:
  - Updated DATASETS/vision_comparison/multi_paper_experiment_padding_3_2.jsonl
  - Regenerated DATASETS/vision_comparison/multi_paper_generalization_report.md
  - Baseline comparison summary table under identical evaluator rules
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

import hashlib
from evaluate_output_reference import REFERENCE_DATA
from experiments_multi_paper_generalization import (
    CANDIDATES,
    OUTPUT_DIR,
    EXP_JSONL,
    RAW_EXP_JSONL,
    BASELINE_JSONL,
    RAW_BASELINE_JSONL,
    FROZEN_BASELINE,
    generate_report,
    evaluate_output,
)

MANIFEST_PATH = OUTPUT_DIR / 'candidate_audit_manifest.json'
REF_FILE = REPO_ROOT / 'scripts' / 'evaluate_output_reference.py'


def recompute():
    # 1. Map candidates
    cand_by_id = {c['candidate_id']: c for c in CANDIDATES}
    for cid, cand in cand_by_id.items():
        if cid in REFERENCE_DATA:
            cand.setdefault('reference_latex', REFERENCE_DATA[cid]['reference_latex'])
            cand.setdefault('crop_scope', REFERENCE_DATA[cid]['crop_scope'])
            cand.setdefault('expected_boundary', REFERENCE_DATA[cid].get('expected_boundary', {}))
            cand.setdefault('required_structures', REFERENCE_DATA[cid]['required_structures'])
            cand.setdefault('required_delimiters', REFERENCE_DATA[cid]['required_delimiters'])
            cand.setdefault('reference_provenance', REFERENCE_DATA[cid]['reference_provenance'])

    # 2. Recompute padding=(15, 15) baseline under the exact same evaluator
    updated_baseline = []
    b_total = 0
    b_cropped = 0
    b_nonempty = 0
    b_isolated = 0
    b_clipped = 0
    b_agreement = 0

    baseline_source = RAW_BASELINE_JSONL if RAW_BASELINE_JSONL.exists() else BASELINE_JSONL

    if baseline_source.exists():
        print(f"Reading and re-evaluating baseline from {baseline_source} under identical evaluator rules...")
        with open(baseline_source, 'r', encoding='utf-8') as f:
            base_records = [json.loads(line) for line in f if line.strip()]

        for r in base_records:
            cid = r.get('candidate_id')
            cand = cand_by_id.get(cid, {})
            rec_text = r.get('recognized_latex', '')
            target_tokens = cand.get('target_tokens', [])
            source_text = cand.get('source_text', '')

            eval_res = evaluate_output(
                recognized_text=rec_text,
                target_tokens=target_tokens,
                source_text=source_text,
                candidate_id=cid,
                cand_meta=cand,
            )
            r['evaluation'] = eval_res
            r['reference_latex'] = cand.get('reference_latex', '')
            r['crop_scope'] = cand.get('crop_scope', 'complete')
            r['expected_boundary'] = cand.get('expected_boundary', {})
            r['reference_provenance'] = cand.get('reference_provenance', {})
            r['evaluator_version'] = 'v2.0-strict-reference-comparison'

            b_cropped += 1
            if not eval_res['is_empty']:
                b_nonempty += 1
            if eval_res['is_isolated']:
                b_isolated += 1
            if eval_res['clipping_detected']:
                b_clipped += 1
            if eval_res['semantic_agreement']:
                b_agreement += 1
            updated_baseline.append(r)

        with open(BASELINE_JSONL, 'w', encoding='utf-8') as f:
            for r in updated_baseline:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        b_total = len(updated_baseline)
        print(f"Wrote {b_total} updated baseline records to {BASELINE_JSONL}")

    baseline_summary = {
        'total': b_total,
        'cropped': b_cropped,
        'nonempty': b_nonempty,
        'isolated': b_isolated,
        'clipped': b_clipped,
        'agreement': b_agreement,
    }

    # 3. Recompute padding=(3, 2) experiment
    exp_source = RAW_EXP_JSONL if RAW_EXP_JSONL.exists() else EXP_JSONL
    print(f"\nReading experiment inputs from {exp_source}...")
    with open(exp_source, 'r', encoding='utf-8') as f:
        exp_records = [json.loads(line) for line in f if line.strip()]

    updated_exp = []
    cropped_count = 0
    nonempty_count = 0
    isolated_count = 0
    clipped_count = 0
    agreement_count = 0

    for r in exp_records:
        cid = r['candidate_id']
        cand = cand_by_id.get(cid, {})
        rec_text = r.get('recognized_latex', '')
        target_tokens = cand.get('target_tokens', r.get('target_tokens', []))
        source_text = cand.get('source_text', r.get('source_text', ''))

        eval_res = evaluate_output(
            recognized_text=rec_text,
            target_tokens=target_tokens,
            source_text=source_text,
            candidate_id=cid,
            cand_meta=cand,
        )

        is_cropped = r.get('crop_successful', True)
        if is_cropped:
            cropped_count += 1
        if not eval_res['is_empty']:
            nonempty_count += 1
        if eval_res['is_isolated']:
            isolated_count += 1
        if eval_res['clipping_detected']:
            clipped_count += 1
        if eval_res['semantic_agreement']:
            agreement_count += 1

        r['evaluation'] = eval_res
        r['reference_latex'] = cand.get('reference_latex', '')
        r['crop_scope'] = cand.get('crop_scope', 'complete')
        r['expected_boundary'] = cand.get('expected_boundary', {})
        r['reference_provenance'] = cand.get('reference_provenance', {})
        r['evaluator_version'] = 'v2.0-strict-reference-comparison'
        updated_exp.append(r)

    with open(EXP_JSONL, 'w', encoding='utf-8') as f:
        for r in updated_exp:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Wrote {len(updated_exp)} updated experiment records to {EXP_JSONL}")

    attempted = len(updated_exp)
    print(f"Padding (15, 15) Baseline Summary: Total={b_total}, NonEmpty={b_nonempty}, Isolated={b_isolated} ({b_isolated/b_total*100:.1f}%), Agreement={b_agreement} ({b_agreement/b_total*100:.1f}%)")
    print(f"Padding (3, 2) Experiment Summary: Attempted={attempted}, Cropped={cropped_count}, NonEmpty={nonempty_count}, Isolated={isolated_count} ({isolated_count/attempted*100:.1f}%), Agreement={agreement_count} ({agreement_count/attempted*100:.1f}%)")

    # Compute SHA-256 hashes
    file_hashes = {
        'raw_exp_sha256': hashlib.sha256(RAW_EXP_JSONL.read_bytes()).hexdigest() if RAW_EXP_JSONL.exists() else None,
        'raw_base_sha256': hashlib.sha256(RAW_BASELINE_JSONL.read_bytes()).hexdigest() if RAW_BASELINE_JSONL.exists() else None,
        'exp_sha256': hashlib.sha256(EXP_JSONL.read_bytes()).hexdigest(),
        'base_sha256': hashlib.sha256(BASELINE_JSONL.read_bytes()).hexdigest() if BASELINE_JSONL.exists() else 'missing',
        'manifest_sha256': hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() if MANIFEST_PATH.exists() else None,
        'ref_sha256': hashlib.sha256(REF_FILE.read_bytes()).hexdigest() if REF_FILE.exists() else None,
        'legacy_sha256': hashlib.sha256(FROZEN_BASELINE.read_bytes()).hexdigest() if FROZEN_BASELINE.exists() else 'missing',
    }

    # Generate Report
    generate_report(
        updated_exp,
        attempted=attempted,
        cropped=cropped_count,
        nonempty=nonempty_count,
        isolated=isolated_count,
        clipped=clipped_count,
        agreement=agreement_count,
        baseline_summary=baseline_summary,
        file_hashes=file_hashes,
    )
    print("Generalization report generated successfully.")


if __name__ == '__main__':
    recompute()


