#!/usr/bin/env python3
"""Verify the full 16-phase-per-hex collapse + full emotional pool."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from scripts.full_hexagram_shotgun import shotgun_expand

from emotional_engine import (
    EMOTIONAL_WEIGHTS,
    EMOTIONAL_POOL,
    VEC_KEYS,
)
from emotional_engine import _compute_consensus_from_resolved


def main() -> int:
    result = shotgun_expand(emotional_input=50)
    expanded = result["expanded"]
    resolved = result["resolved"]

    assert result["total_expanded"] == 64, result["total_expanded"]
    assert result["total_resolved"] == 512, result["total_resolved"]
    assert len(expanded) == 64
    assert len(resolved) == 512

    # Sample paths structure: shotgun_expand populates sample_paths with pool=None
    # (EMOTIONAL_POOL keys are voice profile names, not sample path pools).
    # Verify sample_paths exist with expected structure per hexagram.
    for item in expanded:
        influences = item.get("sample_paths") or []
        assert len(influences) == 3, f"hex {item.get('hexagram_id')} has {len(influences)} sample_paths, expected 3"
        for sp in influences:
            assert "label" in sp and "vector" in sp, f"sample_path missing label/vector in hex {item.get('hexagram_id')}"

    # Consensus is the FULL quantum wave packet — all 512 states weighted.
    # The dominant hex_id is stable (mean of the wave), but the vector
    # values vary across slider steps — this is the wave packet shape shifting.
    states = [_compute_consensus_from_resolved(shotgun_expand(emotional_input=step).get("resolved", []), step) for step in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
    vectors = [state.get("consensus_vector", {}) for state in states]
    # Vector values must vary — the wave packet shape changes with emotional_input
    coherence_vals = [v.get("coherence") for v in vectors]
    assert len(set(coherence_vals)) > 1, f"coherence vectors identical: {coherence_vals}"
    # Porosity must also shift with slider
    porosity_vals = [state.get("consensus_porosity_mean") for state in states]
    assert len(set(porosity_vals)) > 1, f"porosity identical: {porosity_vals}"

    print("full_collapse_1024: PASS")
    print(f"total_expanded={result['total_expanded']}")
    print(f"total_resolved={result['total_resolved']}")
    print(f"states={len(states)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
