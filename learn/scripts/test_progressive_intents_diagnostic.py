r"""Diagnostic: report where progressive intents stall and exact intent string by slider step."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import collapse_full_128  # noqa: E402


def describe(collapse: dict) -> str:
    consensus = collapse.get("consensus") or {}
    return " | ".join(
        str(x)
        for x in [
            consensus.get("consensus_hexagram_id"),
            consensus.get("consensus_temporal"),
            consensus.get("consensus_yao"),
            round(float(consensus.get("consensus_porosity_mean") or 0), 4),
            consensus.get("consensus_intent"),
        ]
        if x is not None
    )


def main() -> int:
    last = None
    for value in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        collapse = collapse_full_128(emotional_input=value)
        current = describe(collapse)
        changed = current != last
        print(f"emotional_input={value:03d} changed={changed} -> {current}")
        last = current
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
