#!/usr/bin/env python3
"""Verify the full 16-phase-per-hex collapse + full emotional pool."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from emotional_engine import (
    collapse_full_128,
    EMOTIONAL_WEIGHTS,
    EMOTIONAL_POOL,
    VEC_KEYS,
)


def main() -> int:
    result = collapse_full_128(emotional_input=50)
    expanded = result["expanded"]
    resolved = result["resolved"]

    assert result["total_expanded"] == 64, result["total_expanded"]
    assert result["total_resolved"] == 1024, result["total_resolved"]
    assert len(expanded) == 64
    assert len(resolved) == 1024

    # Full emotional pool influence per hexagram.
    pool_names = set(EMOTIONAL_POOL.keys())
    missing_influence = []
    for item in expanded:
        influences = item.get("sample_paths") or []
        pools = {path.get("pool") for path in influences}
        if not pool_names.issubset(pools):
            missing_influence.append((item.get("hexagram_id"), sorted(pool_names)[:3]))
    assert not missing_influence, missing_influence[:3]

    # Consensus must vary across slider steps.
    states = [collapse_full_128(emotional_input=step)["consensus"] for step in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
    intents = [state.get("consensus_intent") for state in states]
    seen = {}
    for intent in intents:
        seen[intent] = seen.get(intent, 0) + 1
    assert len(seen) > 1, intents

    print("full_collapse_1024: PASS")
    print(f"total_expanded={result['total_expanded']}")
    print(f"total_resolved={result['total_resolved']}")
    print(f"states={len(states)}")
    print(f"intents={intents}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
