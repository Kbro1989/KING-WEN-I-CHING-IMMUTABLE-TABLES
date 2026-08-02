#!/usr/bin/env python3
"""
Build Ghost Limb fallback registry for MEASURE-masked hexagrams.

Outputs: DATASETS/ghost_limb_registry.json

Registry shape:
{
  "version": "2026-08-02",
  "fallback_targets": [
    {
      "hexagram_id": 15,
      "target_type": "local_file",
      "target": "DATASETS/ghost_limb_kv/15.json",
      "description": "Modesty classical fallback",
      "requires_auth": false,
      "read_only": true,
      "metadata": {"domain": "infrastructure", "void": true}
    },
    ...
  ]
}
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VOID_HEXES = [15, 20, 30, 40]
MEASURE_NONVOID = [4, 17, 42]  # corpus-dense but still MEASURE in live map

TARGETS: list[dict] = []

# Void hexes -> local file fallback in ghost_limb_kv/
for h in VOID_HEXES:
    TARGETS.append({
        "hexagram_id": h,
        "target_type": "local_file",
        "target": str(REPO_ROOT / "DATASETS" / "ghost_limb_kv" / f"{h}.json"),
        "description": f"Hex {h} classical fallback payload",
        "requires_auth": False,
        "read_only": True,
        "metadata": {"domain": "void", "void": True},
    })

# Non-void MEASURE hexes -> local file with note
for h in MEASURE_NONVOID:
    TARGETS.append({
        "hexagram_id": h,
        "target_type": "local_file",
        "target": str(REPO_ROOT / "DATASETS" / "ghost_limb_kv" / f"{h}.json"),
        "description": f"Hex {h} classical fallback payload",
        "requires_auth": False,
        "read_only": True,
        "metadata": {"domain": "measure_nonvoid", "void": False},
    })

# Future expansion: HTTP / worker targets can be added here once endpoints exist

payload = {
    "version": "2026-08-02",
    "description": "Ghost Limb fallback registry for MEASURE-masked hexagrams. Targets are real local paths only; no mocks.",
    "fallback_targets": TARGETS,
}

out_path = REPO_ROOT / "DATASETS" / "ghost_limb_registry.json"
out_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out_path} with {len(TARGETS)} targets")
