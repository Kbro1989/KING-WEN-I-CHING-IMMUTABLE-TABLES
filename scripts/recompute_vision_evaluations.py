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

import os
import shutil
import hashlib
import datetime
import uuid
from evaluate_output_reference import REFERENCE_DATA
from experiments_multi_paper_generalization import (
    CANDIDATES,
    OUTPUT_DIR,
    EXP_JSONL,
    RAW_EXP_JSONL,
    BASELINE_JSONL,
    RAW_BASELINE_JSONL,
    FROZEN_BASELINE,
    REPORT_MD,
    generate_report,
    evaluate_output,
)
from audit_candidate_crops import run_audit
from build_visual_review_log import generate_logs

GENERATIONS_DIR = OUTPUT_DIR / 'generations'
CURRENT_POINTER_FILE = OUTPUT_DIR / 'CURRENT.json'
SNAPSHOT_DIR = OUTPUT_DIR / '.snapshot_prior'
MANIFEST_PATH = OUTPUT_DIR / 'candidate_audit_manifest.json'
REF_FILE = REPO_ROOT / 'scripts' / 'evaluate_output_reference.py'

CANONICAL_FILES = [
    'candidate_audit_manifest.json',
    'multi_paper_baseline_padding15.jsonl',
    'multi_paper_experiment_padding_3_2.jsonl',
    'multi_paper_generalization_report.md',
    'visual_review_audit_log.json',
    'visual_review_audit_log.md',
]


def resolve_active_generation(output_dir: Path | None = None) -> Path:
    """Resolve the currently active generation directory via CURRENT.json pointer."""
    out_dir = output_dir if output_dir is not None else OUTPUT_DIR
    current_file = out_dir / 'CURRENT.json'
    if current_file.exists():
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            gen_rel = data.get('generation_dir')
            if gen_rel:
                gen_path = out_dir / gen_rel
                if gen_path.exists():
                    return gen_path
        except Exception:
            pass
    return out_dir


def get_active_artifact(artifact_name: str, output_dir: Path | None = None) -> Path:
    """Resolve artifact path inside the active generation, falling back to canonical path."""
    out_dir = output_dir if output_dir is not None else OUTPUT_DIR
    active_gen = resolve_active_generation(out_dir)
    candidate = active_gen / artifact_name
    if candidate.exists():
        return candidate
    return out_dir / artifact_name


def recompute(
    output_dir: Path | None = None,
    failure_injection_point: str | None = None,
) -> dict:
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

        b_total = len(updated_baseline)

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

    # --- STAGED GENERATION & ATOMIC PUBLICATION PROTOCOL ---
    out_dir = output_dir if output_dir is not None else OUTPUT_DIR
    generations_dir = out_dir / 'generations'
    current_file = out_dir / 'CURRENT.json'
    snapshot_dir = out_dir / '.snapshot_prior'

    timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')
    short_id = uuid.uuid4().hex[:8]
    gen_id = f"gen_{timestamp_str}_{short_id}"
    stage_dir = out_dir / f".staging_{gen_id}"
    stage_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Stage candidate crop manifest
        staged_manifest = stage_dir / 'candidate_audit_manifest.json'
        run_audit(save_manifest=True, output_path=staged_manifest)

        # 2. Stage visual review audit logs (JSON & MD)
        staged_vlog_json = stage_dir / 'visual_review_audit_log.json'
        staged_vlog_md = stage_dir / 'visual_review_audit_log.md'
        generate_logs(json_path=staged_vlog_json, md_path=staged_vlog_md)

        # 3. Stage baseline evaluation
        staged_baseline = stage_dir / 'multi_paper_baseline_padding15.jsonl'
        with open(staged_baseline, 'w', encoding='utf-8') as f:
            for r in updated_baseline:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

        # 4. Stage experiment evaluation
        staged_exp = stage_dir / 'multi_paper_experiment_padding_3_2.jsonl'
        with open(staged_exp, 'w', encoding='utf-8') as f:
            for r in updated_exp:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

        if failure_injection_point == 'fail_staging_write':
            raise IOError("Simulated failure during staging write")

        # 5. Compute SHA-256 hashes for staged inputs & artifacts
        file_hashes = {
            'raw_exp_sha256': hashlib.sha256(RAW_EXP_JSONL.read_bytes()).hexdigest() if RAW_EXP_JSONL.exists() else None,
            'raw_base_sha256': hashlib.sha256(RAW_BASELINE_JSONL.read_bytes()).hexdigest() if RAW_BASELINE_JSONL.exists() else None,
            'exp_sha256': hashlib.sha256(staged_exp.read_bytes()).hexdigest(),
            'base_sha256': hashlib.sha256(staged_baseline.read_bytes()).hexdigest(),
            'manifest_sha256': hashlib.sha256(staged_manifest.read_bytes()).hexdigest(),
            'ref_sha256': hashlib.sha256(REF_FILE.read_bytes()).hexdigest() if REF_FILE.exists() else None,
            'legacy_sha256': hashlib.sha256(FROZEN_BASELINE.read_bytes()).hexdigest() if FROZEN_BASELINE.exists() else 'missing',
        }

        # 6. Generate staged report
        staged_report = stage_dir / 'multi_paper_generalization_report.md'
        attempted = len(updated_exp)
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
            output_path=staged_report,
        )

        # 7. Collect digests for all 6 generation artifacts
        artifact_digests = {}
        for fname in CANONICAL_FILES:
            fpath = stage_dir / fname
            assert fpath.exists() and fpath.stat().st_size > 0, f"Missing staged artifact: {fname}"
            artifact_digests[fname] = hashlib.sha256(fpath.read_bytes()).hexdigest()

        # 8. Write generation_manifest.json inside staging
        gen_manifest = {
            'generation_id': gen_id,
            'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'evaluator_version': 'v2.0-strict-reference-comparison',
            'artifact_digests': artifact_digests,
            'total_candidates': len(CANDIDATES),
            'status': 'staged',
        }
        with open(stage_dir / 'generation_manifest.json', 'w', encoding='utf-8') as f:
            json.dump(gen_manifest, f, indent=2, ensure_ascii=False)

        # 9. Stage-gate validation of entire generation
        expected_ids = [c['candidate_id'] for c in CANDIDATES]
        assert len(updated_baseline) == len(expected_ids), f"Baseline count mismatch: {len(updated_baseline)} vs {len(expected_ids)}"
        assert len(updated_exp) == len(expected_ids), f"Experiment count mismatch: {len(updated_exp)} vs {len(expected_ids)}"
        assert [r['candidate_id'] for r in updated_baseline] == expected_ids, "Baseline candidate ID order mismatch"
        assert [r['candidate_id'] for r in updated_exp] == expected_ids, "Experiment candidate ID order mismatch"

        report_content = staged_report.read_text(encoding='utf-8')
        assert f"SHA-256: `{file_hashes['exp_sha256']}`" in report_content, "Staged report missing experiment SHA-256"
        assert f"SHA-256: `{file_hashes['base_sha256']}`" in report_content, "Staged report missing baseline SHA-256"
        assert "(provisional; visual review outstanding)" in report_content, "Missing provisional qualification in report"

        with open(staged_vlog_json, 'r', encoding='utf-8') as f:
            vlog = json.load(f)
        assert vlog['summary']['glyph_fidelity_passes'] == 19
        assert vlog['summary']['glyph_fidelity_non_passes'] == 2
        assert vlog['summary']['structure_passes'] == 19
        assert vlog['summary']['structure_non_passes'] == 2
        assert vlog['summary']['boundary_passes'] == 10
        assert vlog['summary']['boundary_non_passes'] == 11
        assert len(vlog['records']) == 21

        with open(staged_manifest, 'r', encoding='utf-8') as f:
            cman = json.load(f)
        assert cman['all_metadata_assertions_passed'] is True
        assert cman['metadata_assertions_passed'] == 21
        assert len(cman['records']) == 21

        if failure_injection_point == 'fail_validation':
            raise AssertionError("Simulated validation failure on staged generation")

        gen_manifest['status'] = 'validated'
        with open(stage_dir / 'generation_manifest.json', 'w', encoding='utf-8') as f:
            json.dump(gen_manifest, f, indent=2, ensure_ascii=False)

    except Exception:
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        raise

    # --- PUBLICATION STAGE ---
    target_gen_dir = generations_dir / gen_id
    generations_dir.mkdir(parents=True, exist_ok=True)
    stage_dir.rename(target_gen_dir)

    prior_pointer_data = None
    if current_file.exists():
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                prior_pointer_data = json.load(f)
        except Exception:
            pass

    tmp_pointer = out_dir / f"CURRENT_{gen_id}.tmp"
    try:
        if failure_injection_point == 'fail_publish_pointer':
            raise IOError("Simulated failure before atomic pointer switch")

        pointer_data = {
            'generation_id': gen_id,
            'generation_dir': f"generations/{gen_id}",
            'published_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'artifact_digests': artifact_digests,
        }

        if failure_injection_point == 'fail_pointer_write':
            raise IOError("Simulated failure during temporary pointer write")

        with open(tmp_pointer, 'w', encoding='utf-8') as f:
            json.dump(pointer_data, f, indent=2)

        if failure_injection_point == 'fail_pointer_replace':
            raise IOError("Simulated failure during atomic pointer replacement")

        os.replace(tmp_pointer, current_file)
    except Exception:
        # Prevent leaving an orphaned generation directory in generations/
        if target_gen_dir.exists():
            shutil.rmtree(target_gen_dir, ignore_errors=True)
        if tmp_pointer.exists():
            tmp_pointer.unlink(missing_ok=True)
        raise

    # Transactional canonical files synchronization with rollback
    pre_existing_canonical = {fname for fname in CANONICAL_FILES if (out_dir / fname).exists()}
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for fname in pre_existing_canonical:
        shutil.copy2(out_dir / fname, snapshot_dir / fname)

    try:
        for idx, fname in enumerate(CANONICAL_FILES):
            if failure_injection_point == 'fail_canonical_sync' and idx == 2:
                raise IOError("Simulated failure during canonical file synchronization")
            src_f = target_gen_dir / fname
            dst_f = out_dir / fname
            tmp_dst = out_dir / f"{fname}.pub_tmp"
            shutil.copy2(src_f, tmp_dst)
            os.replace(tmp_dst, dst_f)
    except Exception:
        print("Transactional publication failed: rolling back canonical files from snapshot...")
        for fname in CANONICAL_FILES:
            dst_f = out_dir / fname
            pub_tmp = out_dir / f"{fname}.pub_tmp"
            if pub_tmp.exists():
                pub_tmp.unlink(missing_ok=True)
            if fname in pre_existing_canonical:
                snap_f = snapshot_dir / fname
                if snap_f.exists():
                    shutil.copy2(snap_f, dst_f)
            else:
                # Was absent prior to publication attempt; restore original absence
                if dst_f.exists():
                    dst_f.unlink(missing_ok=True)
        if prior_pointer_data is not None:
            tmp_rp = out_dir / "CURRENT_rollback.tmp"
            with open(tmp_rp, 'w', encoding='utf-8') as f:
                json.dump(prior_pointer_data, f, indent=2)
            os.replace(tmp_rp, current_file)
        elif current_file.exists():
            current_file.unlink(missing_ok=True)
        raise

    print(f"Publication successful: generation {gen_id} published atomically to CURRENT.json and canonical files synced.")
    return {
        'generation_id': gen_id,
        'generation_dir': str(target_gen_dir),
        'artifact_digests': artifact_digests,
        'attempted': attempted,
        'cropped': cropped_count,
        'nonempty': nonempty_count,
        'isolated': isolated_count,
        'clipped': clipped_count,
        'agreement': agreement_count,
        'baseline_summary': baseline_summary,
    }


if __name__ == '__main__':
    recompute()


