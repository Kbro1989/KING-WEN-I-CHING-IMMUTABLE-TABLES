#!/usr/bin/env python3
"""Open-pool consensus verification.

Verifies that multi_layer_expand produces distinct consensus outputs across
emotional_input values and that all 64 hexagrams are present in every pass.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from scripts.multi_layer_expand import multi_layer_expand  # noqa: E402


def main() -> int:
    inputs = [0, 25, 50, 75, 100]
    results = []
    for val in inputs:
        payload = multi_layer_expand(request_text="verify open pool consensus", emotional_input=val)
        consensus = payload.get("consensus") or {}
        results.append({
            "emotional_input": val,
            "total_expanded": payload.get("total_expanded"),
            "total_resolved": payload.get("total_resolved"),
            "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
            "consensus_temporal": consensus.get("consensus_temporal"),
            "consensus_yao": consensus.get("consensus_yao"),
            "open_pool_meta": consensus.get("open_pool_meta"),
        })

    # All 64 hexagrams must be present in expanded every pass
    bad = [r for r in results if r.get("total_expanded") != 64]
    if bad:
        print("FAIL: not all 64 hexagrams expanded: " + repr(bad))
        return 1

    # Distinct consensus across at least 2 of the 5 inputs
    hex_ids = [r.get("consensus_hexagram_id") for r in results]
    if len(set(hex_ids)) <= 1:
        print("DIAGNOSTIC: consensus still locked: " + repr(hex_ids))
        return 2

    print("open_pool_consensus: PASS")
    for r in results:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
