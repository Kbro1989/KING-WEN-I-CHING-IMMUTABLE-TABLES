#!/usr/bin/env python3
"""Controlled 137-crop DA-V2 processing run — review-corrected version.

Addresses all 6 inspection points from review:

1. Journal recovery: --resume <journal_path> reads existing journal, skips completed crops
2. Atomicity: journal fsync per crop; final JSON via temp-file + os.replace()
3. Output attribution: per-run isolated output directory (not global diff)
4. Validation semantics: ALL 3 expected variants must be present and valid for "completed"
5. Accounting: 152 baseline crops reconcile exactly once (15 original + 137 attempted)
6. Original protection: original 15 hashes verified BEFORE and AFTER processing

Usage:
  python controlled_depth_run.py                    # fresh run
  python controlled_depth_run.py --resume <path>    # resume from journal
"""
import json
import hashlib
import os
import sys
import importlib.util
import argparse
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

# Paths
ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")
GLOBAL_DEPTH_OUTPUT = UDA_V2 / "depth_output"
FIDELITY_DIR = ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS"
BASELINE = ROOT / "DATASETS" / "pdf_depth_lineage_audit.json"
RUNS_DIR = ROOT / "DATASETS" / "pdf_depth_runs"

# Expected output variants (all 3 must be present for "completed")
EXPECTED_VARIANTS = ["_depth_grayscale.png", "_depth.png", "_combined.png"]

# DA-V2 import via importlib (hyphenated filename)
# Add DA-V2 directory to sys.path so its internal imports resolve
sys.path.insert(0, str(UDA_V2))
spec = importlib.util.spec_from_file_location("da_v2", UDA_V2 / "run_image-depth_8bit.py")
da_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(da_v2)
process_image = da_v2.process_image

# Verify signature
import inspect
sig = inspect.signature(process_image)
assert list(sig.parameters.keys()) == ["img_path", "output_path", "input_size", "encoder", "pred_only", "grayscale"], \
    f"Unexpected signature: {sig}"


def _checkpoint(journal_path, result):
    """Append a single crop result to the journal with fsync."""
    with open(journal_path, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(result) + "\n")
        jf.flush()
        os.fsync(jf.fileno())


# Load baseline
baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("--resume", type=str, default=None, help="Path to existing journal to resume from")
args = parser.parse_args()

# Create or resume run identity
if args.resume:
    journal_path = Path(args.resume)
    run_id = journal_path.stem.replace("pdf_depth_journal_", "")
    print(f"Resuming run: {run_id}")
    completed_ids = set()
    failed_ids = set()
    if journal_path.exists():
        for line in journal_path.read_text(encoding="utf-8").strip().split("\n"):
            if line.strip():
                entry = json.loads(line)
                if entry["terminal_state"] == "completed":
                    completed_ids.add(entry["crop_id"])
                elif entry["terminal_state"] == "failed":
                    failed_ids.add(entry["crop_id"])
    print(f"  Already completed: {len(completed_ids)}")
    print(f"  Already failed: {len(failed_ids)}")
else:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    completed_ids = set()
    failed_ids = set()

RUNS_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_RECORD = RUNS_DIR / f"pdf_depth_execution_{run_id}.json"
JOURNAL = RUNS_DIR / f"pdf_depth_journal_{run_id}.jsonl"

# Per-run isolated output directory (not global)
RUN_OUTPUT_DIR = GLOBAL_DEPTH_OUTPUT / f"run_{run_id}"
RUN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Collect ALL baseline crops (152 total)
all_baseline_crops = []
for paper_id, paper in {**baseline["completed_papers"], **baseline["pending_papers"]}.items():
    for crop in paper["crop_records"]:
        all_baseline_crops.append((paper_id, crop))

# Original 15 crops (from completed paper) — crop IDs for accounting
original_15_crops = []
for crop in baseline["completed_papers"]["1907_04931"]["crop_records"]:
    if crop["processing_status"] == "processed":
        original_15_crops.append(crop["crop_id"])

# Original output files (individual files for hash protection)
original_output_files = []
for crop in baseline["completed_papers"]["1907_04931"]["crop_records"]:
    if crop["processing_status"] == "processed":
        for out in crop["depth_outputs"]:
            original_output_files.append({"crop_id": crop["crop_id"], "filename": out["filename"], "sha256": out["sha256"]})

# Verify original 15 hashes BEFORE processing (assert, not warn)
print(f"\n=== Pre-run verification of original 15 outputs ===")
original_hashes_before = {}
for out in original_output_files:
    p = GLOBAL_DEPTH_OUTPUT / out["filename"]
    if p.exists():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        original_hashes_before[out["filename"]] = h
        assert h == out["sha256"], f"BASELINE MISMATCH: {out['filename']} expected {out['sha256']} got {h}"
    else:
        original_hashes_before[out["filename"]] = None
        raise FileNotFoundError(f"Original output missing: {out['filename']}")

print(f"  All {len(original_output_files)} original outputs verified against baseline hashes.")

# Collect unprocessed eligible crops (excluding already-completed in journal)
unprocessed = []
for paper_id, crop in all_baseline_crops:
    if crop["processing_status"] == "unprocessed" and crop["eligibility"] == "eligible":
        if crop["crop_id"] not in completed_ids and crop["crop_id"] not in failed_ids:
            unprocessed.append((paper_id, crop))

print(f"\nUnprocessed eligible crops to process: {len(unprocessed)}")
print(f"Already completed (from journal): {len(completed_ids)}")
print(f"Already failed (from journal): {len(failed_ids)}")
print(f"Per-run output directory: {RUN_OUTPUT_DIR}")

# Execution record
execution = {
    "run_id": run_id,
    "execution_timestamp": datetime.now(timezone.utc).isoformat(),
    "execution_type": "controlled_137_crop_run",
    "resume_from": str(args.resume) if args.resume else None,
    "baseline_file": str(BASELINE),
    "baseline_audit_timestamp": baseline["audit_timestamp"],
    "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
    "generator_script": str(UDA_V2 / "run_image-depth_8bit.py"),
    "model": "Depth Anything V2",
    "encoder": "vits",
    "input_size": 518,
    "colormap_8bit": "Spectral_r",
    "output_directory": str(RUN_OUTPUT_DIR),
    "original_outputs_preserved": True,
    "original_output_count": len(original_output_files),
    "total_attempted": 0,
    "terminal_states": {"completed": 0, "failed": 0, "skipped": 0, "not_started": 0},
    "crop_results": [],
}

# If resuming, load existing crop results from journal
if args.resume and JOURNAL.exists():
    for line in JOURNAL.read_text(encoding="utf-8").strip().split("\n"):
        if line.strip():
            entry = json.loads(line)
            execution["crop_results"].append(entry)
            execution["terminal_states"][entry["terminal_state"]] += 1
            execution["total_attempted"] += 1

# Process each crop
for idx, (paper_id, crop) in enumerate(unprocessed, 1):
    crop_path = Path(crop["crop_path"])
    source_sha = crop["crop_sha256"]
    crop_id = crop["crop_id"]

    # Verify source identity
    if not crop_path.exists():
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "terminal_state": "failed",
            "failure_reason": "source_file_missing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["crop_results"].append(result)
        execution["terminal_states"]["failed"] += 1
        execution["total_attempted"] += 1
        _checkpoint(JOURNAL, result)
        continue

    current_sha = hashlib.sha256(crop_path.read_bytes()).hexdigest()
    if current_sha != source_sha:
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "current_sha256": current_sha,
            "terminal_state": "failed",
            "failure_reason": "source_hash_mismatch",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["crop_results"].append(result)
        execution["terminal_states"]["failed"] += 1
        execution["total_attempted"] += 1
        _checkpoint(JOURNAL, result)
        continue

    # Capture exact file set before processing (scoped to run output dir)
    pre_files = set()
    if RUN_OUTPUT_DIR.exists():
        for f in RUN_OUTPUT_DIR.iterdir():
            if f.is_file():
                pre_files.add(f.name)

    # Process with DA-V2 (output to per-run directory)
    # DA-V2 uses relative checkpoint path, so CWD must be DA-V2 dir
    original_cwd = os.getcwd()
    os.chdir(str(UDA_V2))
    try:
        process_image(str(crop_path), str(RUN_OUTPUT_DIR), 518, "vits", pred_only=False, grayscale=False)
    except Exception as e:
        os.chdir(original_cwd)
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "terminal_state": "failed",
            "failure_reason": f"exception: {type(e).__name__}: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["crop_results"].append(result)
        execution["terminal_states"]["failed"] += 1
        execution["total_attempted"] += 1
        _checkpoint(JOURNAL, result)
        continue
    os.chdir(original_cwd)

    # Capture exact file set after processing
    post_files = set()
    if RUN_OUTPUT_DIR.exists():
        for f in RUN_OUTPUT_DIR.iterdir():
            if f.is_file():
                post_files.add(f.name)

    new_files = post_files - pre_files

    # Validate: ALL 3 expected variants must be present and valid
    crop_stem = crop_path.stem
    validated_outputs = []
    validation_failures = []
    missing_variants = []
    validated_variant_types = set()

    for variant in EXPECTED_VARIANTS:
        expected_fname = f"{crop_stem}{variant}"
        fpath = RUN_OUTPUT_DIR / expected_fname
        if not fpath.exists():
            missing_variants.append(variant)
            continue
        try:
            with Image.open(fpath) as img:
                w, h = img.size
                mode = img.mode
                bit_depth = img.info.get("bits", 8)
            fsize = fpath.stat().st_size
            fhash = hashlib.sha256(fpath.read_bytes()).hexdigest()

            if w < 1 or h < 1:
                validation_failures.append(f"{expected_fname}: zero dimensions")
            elif fsize == 0:
                validation_failures.append(f"{expected_fname}: zero bytes")
            else:
                validated_outputs.append({
                    "filename": expected_fname,
                    "path": str(fpath),
                    "size_bytes": fsize,
                    "width": w,
                    "height": h,
                    "mode": mode,
                    "bit_depth": bit_depth,
                    "sha256": fhash,
                })
                validated_variant_types.add(variant)
        except Exception as e:
            validation_failures.append(f"{expected_fname}: unreadable ({type(e).__name__}: {e})")

    if missing_variants:
        validation_failures.append(f"missing_variants: {missing_variants}")

    # Completion requires ALL expected variant types present and valid
    all_variants_valid = len(validated_variant_types) == len(EXPECTED_VARIANTS) and len(validation_failures) == 0

    if all_variants_valid:
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "terminal_state": "completed",
            "output_count": len(validated_outputs),
            "validated_variants": sorted(validated_variant_types),
            "new_files_this_run": len(new_files),
            "outputs": validated_outputs,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["terminal_states"]["completed"] += 1
    elif validation_failures:
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "terminal_state": "failed",
            "failure_reason": f"output_validation_failed: {'; '.join(validation_failures)}",
            "validated_variants": sorted(validated_variant_types),
            "validated_count": len(validated_outputs),
            "new_files_this_run": len(new_files),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["terminal_states"]["failed"] += 1
    else:
        result = {
            "paper_id": paper_id,
            "crop_id": crop_id,
            "crop_path": str(crop_path),
            "source_sha256": source_sha,
            "terminal_state": "failed",
            "failure_reason": "no_output_generated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution["terminal_states"]["failed"] += 1

    execution["crop_results"].append(result)
    execution["total_attempted"] += 1

    # Durable checkpoint (append-only journal, fsync per crop)
    _checkpoint(JOURNAL, result)

    # Progress
    if idx % 10 == 0 or idx == len(unprocessed):
        print(f"Progress: {idx}/{len(unprocessed)} — "
              f"completed={execution['terminal_states']['completed']}, "
              f"failed={execution['terminal_states']['failed']}, "
              f"skipped={execution['terminal_states']['skipped']}")

# Verify original 15 outputs unchanged (AFTER run)
original_hashes_after = {}
for out in original_output_files:
    p = GLOBAL_DEPTH_OUTPUT / out["filename"]
    if p.exists():
        original_hashes_after[out["filename"]] = hashlib.sha256(p.read_bytes()).hexdigest()
    else:
        original_hashes_after[out["filename"]] = None

originals_changed = []
for out in original_output_files:
    before = original_hashes_before.get(out["filename"])
    after = original_hashes_after.get(out["filename"])
    if before != after:
        originals_changed.append(out["filename"])

# Final reconciliation
execution["reconciliation"] = {
    "baseline_processed_crop_count": len(original_15_crops),
    "baseline_processed_output_count": len(original_output_files),
    "newly_attempted": execution["total_attempted"],
    "newly_completed": execution["terminal_states"]["completed"],
    "newly_failed": execution["terminal_states"]["failed"],
    "newly_skipped": execution["terminal_states"]["skipped"],
    "verified_processed_crop_total": len(original_15_crops) + execution["terminal_states"]["completed"],
    "total_source_crops": 152,
    "original_outputs_preserved": len(originals_changed) == 0,
    "original_outputs_changed": originals_changed,
    "equation": f"{len(original_15_crops)} + {execution['terminal_states']['completed']} = {len(original_15_crops) + execution['terminal_states']['completed']}",
}

# Reconcile not_started: any crop in baseline but not in execution record
all_baseline_crops = set()
for paper_id, paper in {**baseline["completed_papers"], **baseline["pending_papers"]}.items():
    for crop in paper["crop_records"]:
        all_baseline_crops.add(crop["crop_id"])

processed_crop_ids = {r["crop_id"] for r in execution["crop_results"]}
already_processed_ids = {c["crop_id"] for c in baseline["completed_papers"]["1907_04931"]["crop_records"] if c["processing_status"] == "processed"}
not_started = all_baseline_crops - processed_crop_ids - already_processed_ids
execution["terminal_states"]["not_started"] = len(not_started)
execution["not_started_crop_ids"] = sorted(not_started)

# Atomic final JSON write (temp file + os.replace)
tmp_fd, tmp_path = tempfile.mkstemp(dir=RUNS_DIR, suffix=".json")
try:
    with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
        json.dump(execution, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, EXECUTION_RECORD)
except Exception:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
    raise

print(f"\nExecution record written: {EXECUTION_RECORD}")
print(f"Run ID: {run_id}")
print(f"Completed: {execution['terminal_states']['completed']}")
print(f"Failed: {execution['terminal_states']['failed']}")
print(f"Skipped: {execution['terminal_states']['skipped']}")
print(f"Not started: {execution['terminal_states']['not_started']}")
print(f"Verified total: {execution['reconciliation']['verified_processed_crop_total']}/152")
print(f"Original 15 preserved: {execution['reconciliation']['original_outputs_preserved']}")
if originals_changed:
    print(f"WARNING: Original outputs changed: {originals_changed}")
