"""Fetch specific reference code routines from external document parsing and OCR frameworks.

Fetches individual target files directly from raw GitHub repositories without
cloning entire repositories or installing external dependencies.

Records every fetched file with its source URL, commit SHA, byte size,
and SHA-256 hash in references/comparative_study/fetch_manifest.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
REF_DIR = ROOT / "references" / "comparative_study"
RAW_DIR = REF_DIR / "raw_code"
MANIFEST_PATH = REF_DIR / "fetch_manifest.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)

# Target file manifest definitions
TARGETS = [
    # 1. OmniDocBench
    {
        "framework": "OmniDocBench",
        "repo": "opendatalab/OmniDocBench",
        "commit": "0604d9843f1dfa3a292bd5f253ae83a1ba47cd24",
        "remote_path": "src/core/matching/match_quick.py",
        "local_rel_path": "omnidocbench/match_quick.py",
        "description": "Spatial sorting, text normalization, Levenshtein distance matrix, and chunked Hungarian matching fallback",
    },
    {
        "framework": "OmniDocBench",
        "repo": "opendatalab/OmniDocBench",
        "commit": "0604d9843f1dfa3a292bd5f253ae83a1ba47cd24",
        "remote_path": "src/core/matching/match.py",
        "local_rel_path": "omnidocbench/match.py",
        "description": "Core layout block matching, IoU calculation, and text overlap alignment",
    },
    {
        "framework": "OmniDocBench",
        "repo": "opendatalab/OmniDocBench",
        "commit": "0604d9843f1dfa3a292bd5f253ae83a1ba47cd24",
        "remote_path": "src/metrics/cdm/modules/visual_matcher.py",
        "local_rel_path": "omnidocbench/visual_matcher.py",
        "description": "Character Detection Matching (CDM) Hungarian cost function (token=1.0, pos=0.05, order=0.15) and token normalization",
    },
    {
        "framework": "OmniDocBench",
        "repo": "opendatalab/OmniDocBench",
        "commit": "0604d9843f1dfa3a292bd5f253ae83a1ba47cd24",
        "remote_path": "src/dataset/end2end_dataset.py",
        "local_rel_path": "omnidocbench/end2end_dataset.py",
        "description": "End-to-end dataset loading, reading order, and block hierarchy parser",
    },

    # 2. PureDocBench
    {
        "framework": "PureDocBench",
        "repo": "zhihengli-casia/PureDocBench",
        "commit": "4e9d64d73077761d54d10f9c4e66ad06bf8a267b",
        "remote_path": "scripts/apply_degradation_ablation.py",
        "local_rel_path": "puredocbench/apply_degradation_ablation.py",
        "description": "Deterministic 4-stage degradation ablation pipeline (printing, paper, capture, digital) seeded by filename hash",
    },
    {
        "framework": "PureDocBench",
        "repo": "zhihengli-casia/PureDocBench",
        "commit": "4e9d64d73077761d54d10f9c4e66ad06bf8a267b",
        "remote_path": "scripts/degradation_v2/apply_degradation_v2.py",
        "local_rel_path": "puredocbench/apply_degradation_v2.py",
        "description": "Second-generation synthetic and camera degradation operations and severity levels",
    },
    {
        "framework": "PureDocBench",
        "repo": "zhihengli-casia/PureDocBench",
        "commit": "4e9d64d73077761d54d10f9c4e66ad06bf8a267b",
        "remote_path": "docs/ANNOTATION_CORRECTIONS.md",
        "local_rel_path": "puredocbench/ANNOTATION_CORRECTIONS.md",
        "description": "Ground truth correction workflow, review application contract, and patch schema",
    },

    # 3. MinerU
    {
        "framework": "MinerU",
        "repo": "opendatalab/MinerU",
        "commit": "8cd08422055858f55a64dff79f942318b51b96cc",
        "remote_path": "docs/en/reference/output_files.md",
        "local_rel_path": "mineru/output_files.md",
        "description": "MiddleJson and ModelJson structured output schema, block hierarchies, and layout geometry conventions",
    },
    {
        "framework": "MinerU",
        "repo": "opendatalab/MinerU",
        "commit": "8cd08422055858f55a64dff79f942318b51b96cc",
        "remote_path": "tests/unittest/test_source_metadata.py",
        "local_rel_path": "mineru/test_source_metadata.py",
        "description": "Unit tests verifying extraction and retention of source PDF metadata and page indices",
    },
    {
        "framework": "MinerU",
        "repo": "opendatalab/MinerU",
        "commit": "8cd08422055858f55a64dff79f942318b51b96cc",
        "remote_path": "docs/en/reference/migration_4_1.md",
        "local_rel_path": "mineru/migration_4_1.md",
        "description": "Version 4.1 contract migration details, block level definitions, and API boundary definitions",
    },

    # 4. UniMERNet
    {
        "framework": "UniMERNet",
        "repo": "opendatalab/UniMERNet",
        "commit": "5a2c80d96b1d2dba447ff18d873e5fb73ba03c35",
        "remote_path": "unimernet/processors/formula_processor.py",
        "local_rel_path": "unimernet/formula_processor.py",
        "description": "Formula image preprocessing: margin crop, aspect-ratio resize, centered/random padding, and augmentations",
    },
    {
        "framework": "UniMERNet",
        "repo": "opendatalab/UniMERNet",
        "commit": "5a2c80d96b1d2dba447ff18d873e5fb73ba03c35",
        "remote_path": "demo.py",
        "local_rel_path": "unimernet/demo.py",
        "description": "Formula inference entry point, image loading, and LaTeX decoding pipeline",
    },

    # 5. PaddleOCR
    {
        "framework": "PaddleOCR",
        "repo": "PaddlePaddle/PaddleOCR",
        "commit": "dab3fe35379033fdcb2d0e9572fac0b36c9a9ebf",
        "remote_path": "docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md",
        "local_rel_path": "paddleocr/PaddleOCR-VL.en.md",
        "description": "End-to-end document parsing pipeline documentation, layout detection, and block merging specifications",
    },
    {
        "framework": "PaddleOCR",
        "repo": "PaddlePaddle/PaddleOCR",
        "commit": "dab3fe35379033fdcb2d0e9572fac0b36c9a9ebf",
        "remote_path": "docs/version3.x/pipeline_usage/formula_recognition.en.md",
        "local_rel_path": "paddleocr/formula_recognition.en.md",
        "description": "Formula recognition pipeline connecting PP-DocLayoutV3 with PP-FormulaNet and UniMERNet",
    },

    # 6. TeleOCR
    {
        "framework": "TeleOCR",
        "repo": "caipeng328/TeleOCR",
        "commit": "1e71f4fe792d12bbb86d2671c5ed6f3a1499b27d",
        "remote_path": "infer.py",
        "local_rel_path": "teleocr/infer.py",
        "description": "Inference script with vLLM and HuggingFace backends for high-resolution document processing",
    },
    {
        "framework": "TeleOCR",
        "repo": "caipeng328/TeleOCR",
        "commit": "1e71f4fe792d12bbb86d2671c5ed6f3a1499b27d",
        "remote_path": "TeleOCR/vlm_utils/TeleOCR_model.py",
        "local_rel_path": "teleocr/TeleOCR_model.py",
        "description": "Model interface and document parsing prompt wrappers",
    },
]


def fetch_file(target: dict) -> dict:
    url = f"https://raw.githubusercontent.com/{target['repo']}/{target['commit']}/{target['remote_path']}"
    out_file = RAW_DIR / target["local_rel_path"]
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching: {target['framework']} -> {target['remote_path']}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    # Try fetching with retries
    max_retries = 3
    content = None
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                break
        except Exception as e:
            print(f"  [Attempt {attempt}/{max_retries}] Fetch failed: {e}")
            if attempt < max_retries:
                time.sleep(1.5)
            else:
                raise

    with open(out_file, "wb") as f:
        f.write(content)

    sha = hashlib.sha256(content).hexdigest()
    print(f"  Saved: {out_file.relative_to(ROOT)} ({len(content):,} bytes, sha256: {sha[:16]}...)")

    return {
        "framework": target["framework"],
        "repo": target["repo"],
        "commit": target["commit"],
        "remote_path": target["remote_path"],
        "local_path": str(out_file.relative_to(ROOT)),
        "source_url": url,
        "byte_size": len(content),
        "sha256": sha,
        "description": target["description"],
    }


def main():
    print("=== FETCHING EXTERNAL FRAMEWORK REFERENCE CODE ROUTINES ===")
    records = []
    failed = []

    for t in TARGETS:
        try:
            rec = fetch_file(t)
            records.append(rec)
        except Exception as e:
            print(f"  ERROR fetching {t['remote_path']}: {e}")
            failed.append({"target": t, "error": str(e)})

    manifest = {
        "manifest_identifier": "EXTERNAL-FRAMEWORKS-CODE-REFERENCE-MANIFEST-V1",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_targets": len(TARGETS),
        "successful_fetches": len(records),
        "failed_fetches": len(failed),
        "files": records,
        "failures": failed,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n=== SUMMARY ===")
    print(f"Total: {len(TARGETS)} | Success: {len(records)} | Failed: {len(failed)}")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

