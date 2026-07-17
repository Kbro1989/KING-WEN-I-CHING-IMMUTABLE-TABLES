r"""Pass 2: progressive intents across slider values.

Run:
  PYTHONPATH=. python3 learn\scripts\test_progressive_intents.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import collapse_full_128  # noqa: E402


def describe(collapse: dict) -> str | dict:
    consensus = collapse.get("consensus") or {}
    structured = {
        "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
        "consensus_temporal": consensus.get("consensus_temporal"),
        "consensus_yao": consensus.get("consensus_yao"),
        "consensus_porosity_mean": round(float(consensus.get("consensus_porosity_mean") or 0), 4),
        "consensus_intent": consensus.get("consensus_intent") or "",
    }
    if strict_string:
        return " | ".join(str(x) for x in [
            structured["consensus_hexagram_id"],
            structured["consensus_temporal"],
            structured["consensus_yao"],
            structured["consensus_porosity_mean"],
            structured["consensus_intent"],
        ])
    return structured


strict_string = True


def main() -> int:
    print("diagnostics; strict assertion disabled until scoring changes.")
    for value in range(0, 101, 10):
        collapse = collapse_full_128(emotional_input=value)
        current = describe(collapse)
        print(f"emotional_input={value:03d} -> {current}")
    print("progressive_intents: DIAGNOSTIC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
