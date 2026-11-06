#!/usr/bin/env python3
"""Source-to-artifact lineage audit for the PDF depth branch (Workstream B).

Establishes a reproducible baseline BEFORE processing the 4 pending papers.
Records: source crop -> model -> encoder -> params -> output -> hash.

Usage:
  python scripts/audit_pdf_depth_lineage.py
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
UDA_V2 = Path("C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2")
DEPTH_OUTPUT = UDA_V2 / "depth_output"
FIDELITY_DIR = ROOT / "DATASETS" / "PDF_FIDELITY_RENDERINGS"
OUTPUT = ROOT / "DATASETS" / "pdf_depth_lineage_audit.json"

PENDING_PAPERS = ["2104_01277", "2206_00364", "2605_22902", "2605_27315"]
COMPLETED_PAPER = "1907_04931"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_paper(paper_id):
    """Audit all crops and depth outputs for a single paper."""
    crop_dir = FIDELITY_DIR / paper_id
    crops = sorted(crop_dir.glob("*.png")) if crop_dir.exists() else []

    crop_records = []
    for crop in crops:
        # Find matching depth outputs
        stem = crop.stem  # e.g., "crop_00" or "crop_00_4x"
        depth_files = []
        if DEPTH_OUTPUT.exists():
            for suffix in ["_depth_grayscale.png", "_depth.png", "_combined.png"]:
                for df in DEPTH_OUTPUT.glob(f"{stem}*{suffix}"):
                    depth_files.append({
                        "filename": df.name,
                        "path": str(df),
                        "size_bytes": df.stat().st_size,
                        "sha256": sha256_file(df),
                    })

        # Eligibility assessment (separate from processing status)
        # A crop is eligible if it is a readable PNG with non-zero dimensions
        eligible = True
        eligibility_reason = "eligible"
        try:
            from PIL import Image
            with Image.open(crop) as img:
                w, h = img.size
                if w < 10 or h < 10:
                    eligible = False
                    eligibility_reason = f"too_small ({w}x{h})"
                elif img.mode not in ("RGB", "L", "RGBA", "P"):
                    eligible = False
                    eligibility_reason = f"unsupported_mode ({img.mode})"
        except Exception as e:
            eligible = False
            eligibility_reason = f"unreadable ({type(e).__name__})"

        crop_records.append({
            "crop_id": stem,
            "crop_path": str(crop),
            "crop_size_bytes": crop.stat().st_size,
            "crop_sha256": sha256_file(crop),
            "depth_outputs": depth_files,
            "depth_output_count": len(depth_files),
            "processing_status": "processed" if len(depth_files) > 0 else "unprocessed",
            "eligibility": "eligible" if eligible else "ineligible",
            "eligibility_reason": eligibility_reason,
        })

    return {
        "paper_id": paper_id,
        "crop_dir": str(crop_dir),
        "crop_dir_exists": crop_dir.exists(),
        "crop_count": len(crops),
        "crops_with_depth": sum(1 for c in crop_records if c["depth_output_count"] > 0),
        "crops_without_depth": sum(1 for c in crop_records if c["depth_output_count"] == 0),
        "crop_records": crop_records,
    }


def main():
    audit = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_type": "source-to-artifact lineage audit for PDF depth branch (Workstream B)",
        "generator_script": "C:/Users/krist/Desktop/Upgraded-Depth-Anything-V2/run_image-depth_8bit.py",
        "model": "Depth Anything V2",
        "encoder": "vits",
        "input_size": 518,
        "colormap_8bit": "Spectral_r",
        "colormap_16bit": "gray (raw)",
        "output_variants": ["_depth_grayscale.png", "_depth.png", "_combined.png"],
        "zoom_variants": ["1x (crop_XX.png)", "4x (crop_XX_4x.png)"],
        "completed_papers": {},
        "pending_papers": {},
        "summary": {},
    }

    # Audit completed paper
    completed = audit_paper(COMPLETED_PAPER)
    audit["completed_papers"][COMPLETED_PAPER] = completed

    # Audit pending papers
    for pid in PENDING_PAPERS:
        pending = audit_paper(pid)
        audit["pending_papers"][pid] = pending

    # Summary
    total_crops = sum(
        p["crop_count"]
        for p in [completed] + [audit["pending_papers"][pid] for pid in PENDING_PAPERS]
    )
    total_depth = sum(
        p["crops_with_depth"]
        for p in [completed] + [audit["pending_papers"][pid] for pid in PENDING_PAPERS]
    )
    all_papers = [completed] + [audit["pending_papers"][pid] for pid in PENDING_PAPERS]
    eligible_count = sum(
        sum(1 for c in p["crop_records"] if c["eligibility"] == "eligible")
        for p in all_papers
    )
    ineligible_count = total_crops - eligible_count
    unprocessed_eligible = sum(
        sum(1 for c in p["crop_records"] if c["processing_status"] == "unprocessed" and c["eligibility"] == "eligible")
        for p in all_papers
    )

    audit["summary"] = {
        "completed_papers": 1,
        "pending_papers": len(PENDING_PAPERS),
        "total_papers": 1 + len(PENDING_PAPERS),
        "total_crops": total_crops,
        "crops_with_depth": total_depth,
        "crops_without_depth": total_crops - total_depth,
        "eligible_crops": eligible_count,
        "ineligible_crops": ineligible_count,
        "unprocessed_eligible_crops": unprocessed_eligible,
        "baseline_established": True,
        "note": "crops_without_depth != unprocessed_eligible: some crops may be ineligible for the same DA-V2 configuration. Eligibility is assessed separately from processing status.",
    }

    OUTPUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print(f"Completed: {COMPLETED_PAPER} — {completed['crop_count']} crops, {completed['crops_with_depth']} with depth")
    for pid in PENDING_PAPERS:
        p = audit["pending_papers"][pid]
        print(f"Pending: {pid} — {p['crop_count']} crops, {p['crops_with_depth']} with depth, exists={p['crop_dir_exists']}")
    print(f"Total: {total_crops} crops, {total_depth} with depth, {total_crops - total_depth} without")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
