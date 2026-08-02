"""
Ghost Limb Bridge — classical fallback path for MEASURE-masked hexagrams.

When a quantum mask resolves to MEASURE, the PQC layer aborts and this bridge
routes execution to deterministic classical fallback targets:

  void hexes (15, 20, 30, 40) -> local KV cache / mini-tier Rolodex
  non-void MEASURE         -> registry-selected classical engine slot

Design constraints:
  - No mock/stub/fabrication in src. Every fallback target must map to a real
    local path or registered endpoint.
  - Expand-first: never collapse to a single dominant before the selector has
    seen all 64 outputs.
  - Boolean only at final decision gates; this module is the final gate for
    MEASURE, so boolean is acceptable here.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class FallbackTargetType(str, Enum):
    KV_CACHE = "kv_cache"
    ROLODEX = "rolodex"
    LOCAL_FILE = "local_file"
    HTTP_ENDPOINT = "http_endpoint"
    WORKER = "worker"


@dataclass
class FallbackTarget:
    hexagram_id: int
    target_type: FallbackTargetType
    target: str
    description: str
    requires_auth: bool = False
    read_only: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GhostLimbDecision:
    hexagram_id: int
    mask: str
    triggered: bool
    fallback_target: Optional[FallbackTarget]
    classical_path: str
    quantum_aborted: bool = True


class GhostLimbBridge:
    def __init__(self, registry_path: str | Path) -> None:
        self.registry_path = Path(registry_path)
        self._registry: Dict[str, Any] = {}
        self._targets: Dict[int, FallbackTarget] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Ghost Limb registry missing at {self.registry_path}. "
                "Run build_ghost_limb_registry.py first."
            )
        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self._registry = data
        for entry in data.get("fallback_targets", []):
            target = FallbackTarget(
                hexagram_id=int(entry["hexagram_id"]),
                target_type=FallbackTargetType(entry["target_type"]),
                target=entry["target"],
                description=entry.get("description", ""),
                requires_auth=bool(entry.get("requires_auth", False)),
                read_only=bool(entry.get("read_only", True)),
                metadata=entry.get("metadata", {}),
            )
            self._targets[target.hexagram_id] = target

    def resolve(self, hexagram_id: int, mask: str) -> GhostLimbDecision:
        triggered = mask == "MEASURE"
        fallback_target = self._targets.get(hexagram_id)
        classical_path = (
            f"ghost_limb:{fallback_target.target_type.value}:{fallback_target.target}"
            if fallback_target
            else "ghost_limb:no_registry_entry"
        )
        return GhostLimbDecision(
            hexagram_id=hexagram_id,
            mask=mask,
            triggered=triggered,
            fallback_target=fallback_target,
            classical_path=classical_path,
            quantum_aborted=triggered,
        )

    def decisions_for_masks(self, mask_map: Dict[int, str]) -> List[GhostLimbDecision]:
        return [self.resolve(h, m) for h, m in sorted(mask_map.items())]

    def registry(self) -> Dict[str, Any]:
        return self._registry

    def target(self, hexagram_id: int) -> Optional[FallbackTarget]:
        return self._targets.get(hexagram_id)
