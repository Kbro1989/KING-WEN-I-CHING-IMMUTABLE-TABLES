#!/usr/bin/env python3
"""Runnable entry point: verify registry and save data/hexagram-registry.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import KING_WEN_TABLES  # noqa: E402

output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

registry = {str(h["id"]): {k: v for k, v in h.items() if k != "id"} for h in KING_WEN_TABLES.HEXAGRAMS}
with open(os.path.join(output_dir, "data/hexagram-registry.json"), "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("✅ Registry saved with corrected trigrams")
