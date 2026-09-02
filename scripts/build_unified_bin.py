#!/usr/bin/env python3
"""build_unified_bin.py
Analyzes all large output dumps in the workspace, extracts all unique telemetry/state keys,
and packs a unified binary baseline index (`unified_kingwen_baseline.bin`) for complete
save string site guidance.
"""
from __future__ import annotations

import glob
import json
import logging
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Dumps to analyze
DUMP_PATTERNS = [
    "shotgun_expand_output.json",
    "DATASETS/kingwen_save_strings.csv",
    "DATASETS/kingwen_oracle_master.json",
    "DATASETS/kingwen_consultation_record.json",
    "learn/exports/expanded_source.jsonl",
    "learn/exports/resolved_source.jsonl",
    "scripts/hexagram_full_expansion.json",
    "scripts/ternary_full_expansion.json",
    "kingwen_train_data/rsmv_kit_version_manifest.json",
    "kingwen_train_data_demo2/learned_sequential_64.json"
]

def scan_dumps() -> Dict[str, Any]:
    found_files = []
    all_keys: Set[str] = set()
    hex_site_fields: Set[str] = set()

    for rel in DUMP_PATTERNS:
        p = _REPO_ROOT / rel
        if not p.exists():
            continue
        
        file_size = p.stat().st_size
        found_files.append({"path": rel, "size_bytes": file_size})

        if rel.endswith(".json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
                _extract_keys(data, all_keys, hex_site_fields)
            except Exception as e:
                logger.warning("Error reading %s: %s", rel, e)
        elif rel.endswith(".jsonl"):
            try:
                with p.open("r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip():
                            obj = json.loads(line)
                            _extract_keys(obj, all_keys, hex_site_fields)
                            break  # Sample first entry for structure
            except Exception as e:
                logger.warning("Error reading %s: %s", rel, e)
        elif rel.endswith(".csv"):
            try:
                lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                if lines:
                    header = lines[0].split(",")
                    all_keys.update(header)
                    hex_site_fields.update(header)
            except Exception as e:
                logger.warning("Error reading %s: %s", rel, e)

    return {
        "found_dumps": found_files,
        "all_extracted_keys": sorted(list(all_keys)),
        "hex_site_fields": sorted(list(hex_site_fields))
    }

def _extract_keys(obj: Any, keys_set: Set[str], hex_fields: Set[str], prefix: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            keys_set.add(full_key)
            if "hex" in k.lower() or "state" in k.lower() or "vector" in k.lower() or "voice" in k.lower():
                hex_fields.add(k)
            _extract_keys(v, keys_set, hex_fields, full_key)
    elif isinstance(obj, list) and obj:
        _extract_keys(obj[0], keys_set, hex_fields, prefix)

def create_unified_bin(scan_data: Dict[str, Any]) -> str:
    bin_path = _REPO_ROOT / "DATASETS" / "unified_kingwen_baseline.bin"
    bin_path.parent.mkdir(parents=True, exist_ok=True)

    header_magic = b"KW64BIN1"
    version = 2
    num_dumps = len(scan_data["found_dumps"])
    num_fields = len(scan_data["hex_site_fields"])

    keys_json = json.dumps(scan_data["hex_site_fields"]).encode("utf-8")
    keys_len = len(keys_json)

    with bin_path.open("wb") as f:
        f.write(header_magic)
        f.write(struct.pack("<III", version, num_dumps, num_fields))
        f.write(struct.pack("<I", keys_len))
        f.write(keys_json)

    return str(bin_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scan_res = scan_dumps()
    bin_file = create_unified_bin(scan_res)
    print(f"Unified Binary Index Created at: {bin_file}")
    print(f"Analyzed Dumps Count: {len(scan_res['found_dumps'])}")
    print(f"Total Unique Keys Extracted: {len(scan_res['all_extracted_keys'])}")
    print(f"Extracted Hexagram Site Fields: {scan_res['hex_site_fields'][:20]}...")
