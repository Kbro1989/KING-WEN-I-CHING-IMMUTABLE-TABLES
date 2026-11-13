"""Generate Reproducible Content-Addressed Degradation Corpus.

Generates a small, deterministic degradation corpus across benchmark cases
(CP-001, CP-002, CP-003) under three standardized perturbation profiles:
  - profile_print_artifact: ink_bleed (0.25), low_resolution (0.3)
  - profile_paper_aging: crumple_folds (0.3), yellowing_tint (0.5), moisture_stain (0.2)
  - profile_optical_capture: perspective_skew (0.2), gaussian_sensor_noise (0.3), motion_blur (0.2)

Manifest records:
  - source_image_sha256
  - profile_canonical_sha256
  - experiment_identity_sha256 (256-bit digest S)
  - prng_seed_32bit (execution parameter s32)
  - output_image_sha256
  - output_file_path

Outputs:
  DATASETS/structural_preservation/degradation_corpus/
  DATASETS/structural_preservation/degradation_corpus/manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# pyrefly: ignore[missing-import]
import cv2
# pyrefly: ignore[missing-import]
import numpy as np
# pyrefly: ignore[missing-import]
import pymupdf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

REPO_ROOT = Path("c:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
scripts_path = str(REPO_ROOT / "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from robustness.degradation_harness import DegradationHarness, canonical_json_bytes

OUT_DIR = REPO_ROOT / "DATASETS" / "structural_preservation" / "degradation_corpus"
MANIFEST_PATH = OUT_DIR / "manifest.json"


PROFILES = [
    {
        "profile_name": "profile_print_artifact",
        "operations": [
            {"name": "ink_bleed", "severity": 0.25},
            {"name": "low_resolution", "severity": 0.3},
        ],
    },
    {
        "profile_name": "profile_paper_aging",
        "operations": [
            {"name": "crumple_folds", "severity": 0.3},
            {"name": "yellowing_tint", "severity": 0.5},
            {"name": "moisture_stain", "severity": 0.2},
        ],
    },
    {
        "profile_name": "profile_optical_capture",
        "operations": [
            {"name": "perspective_skew", "severity": 0.2},
            {"name": "gaussian_sensor_noise", "severity": 0.3},
            {"name": "motion_blur", "severity": 0.2},
        ],
    },
]

TARGETS = [
    {
        "case_id": "CP-001",
        "pdf": REPO_ROOT / "DATASETS" / "benchmark_pdfs" / "1905.07953.pdf",
        "page": 3,
        "rect": pymupdf.Rect(116.15, 476.58, 230.61, 523.37),
    },
    {
        "case_id": "CP-002",
        "pdf": REPO_ROOT / "DATASETS" / "benchmark_pdfs" / "2102.03334.pdf",
        "page": 3,
        "rect": pymupdf.Rect(318.18, 532.30, 461.28, 548.82),
    },
    {
        "case_id": "CP-003",
        "pdf": REPO_ROOT / "DATASETS" / "benchmark_pdfs" / "2605.24856.pdf",
        "page": 10,
        "rect": pymupdf.Rect(231.49, 151.11, 379.31, 193.97),
    },
]


def render_source_crop(pdf_path: Path, page_idx: int, rect: pymupdf.Rect, zoom: float = 2.0) -> np.ndarray:
    doc = pymupdf.open(str(pdf_path))
    page = doc[page_idx]
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    harness = DegradationHarness()
    corpus_entries = []

    for target in TARGETS:
        cid = target["case_id"]
        source_img = render_source_crop(target["pdf"], target["page"], target["rect"])
        _, source_png = cv2.imencode(".png", source_img)
        source_bytes = source_png.tobytes()
        source_hash = hashlib.sha256(source_bytes).hexdigest()

        # Save source reference crop
        src_path = OUT_DIR / f"{cid}_source.png"
        cv2.imwrite(str(src_path), source_img)

        for prof in PROFILES:
            prof_name = prof["profile_name"]
            prof_hash = hashlib.sha256(canonical_json_bytes(prof)).hexdigest()

            degraded_img, result_meta = harness.apply_profile(source_img, prof)

            out_filename = f"{cid}_{prof_name}.png"
            out_path = OUT_DIR / out_filename
            cv2.imwrite(str(out_path), degraded_img)

            _, out_png = cv2.imencode(".png", degraded_img)
            out_hash = hashlib.sha256(out_png.tobytes()).hexdigest()

            corpus_entries.append({
                "case_id": cid,
                "profile_name": prof_name,
                "source_image_file": src_path.name,
                "source_image_sha256": source_hash,
                "profile_canonical_sha256": prof_hash,
                "experiment_identity_digest_sha256": result_meta["experiment_identity_digest_sha256"],
                "prng_seed_32bit": result_meta["prng_seed_32bit"],
                "output_image_file": out_filename,
                "output_image_sha256": out_hash,
                "output_image_shape": result_meta["output_image_shape"],
                "executed_operations": result_meta["executed_operations"],
            })

    manifest = {
        "corpus_identifier": "KING-WEN-DEGRADATION-CORPUS-V1",
        "total_targets": len(TARGETS),
        "total_profiles": len(PROFILES),
        "total_degraded_samples": len(corpus_entries),
        "corpus_entries": corpus_entries,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Degradation corpus generated successfully: {len(corpus_entries)} samples. Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

