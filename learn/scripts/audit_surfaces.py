#!/usr/bin/env python3
"""Scan King Wen / OpenJarvis / Megatron integration surfaces without edits."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_KINGWEN = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
ROOT_OPENJARVIS = Path("C:/Users/krist/Desktop/OpenJarvis/src/openjarvis")
ROOT_MEGATRON = Path("C:/Users/krist/Desktop/Megatron-LM-review/kingwen_train_data")

FILES = {
    "kingwen_engine": ROOT_KINGWEN / "emotional_engine.py",
    "expand_server": ROOT_KINGWEN / "expand_server.py",
    "openjarvis_adapter": ROOT_OPENJARVIS / "emotion/kingwen_engine_adapter.py",
    "openjarvis_oracle_speak": ROOT_OPENJARVIS / "cli/_oracle_speak.py",
    "openjarvis_api_routes": ROOT_OPENJARVIS / "server/api_routes.py",
    "openjarvis_desktop": ROOT_OPENJARVIS / "bridge_servers/desktop_execution.py",
    "openjarvis_chat_cmd": ROOT_OPENJARVIS / "cli/chat_cmd.py",
    "megatron_dataset": ROOT_MEGATRON / "runtime/kingwen_dataset.py",
    "megatron_build_usage": ROOT_MEGATRON / "build_usage_labels.py",
    "megatron_jarvis_loader": ROOT_MEGATRON / "jarvis_dataset.py",
    "megatron_integrity": ROOT_MEGATRON / "integrity_check.py",
    "megatron_manifest": ROOT_MEGATRON / "model/jarvis-native-kingwen-life/manifest.json",
}


def main() -> int:
    results = {}
    for name, path in FILES.items():
        results[name] = {
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else -1,
        }
    print(json.dumps(results, indent=2, sort_keys=True))
    missing = [k for k, v in results.items() if not v["exists"]]
    if missing:
        print("MISSING=" + ",".join(sorted(missing)))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
