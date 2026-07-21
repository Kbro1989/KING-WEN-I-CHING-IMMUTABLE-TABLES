r"""Pass 4: deterministic replay invariance.

Identical inputs must yield identical collapsed outputs.
Run:
  PYTHONPATH=. python3 learn\scripts\test_deterministic_replay.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import collapse_full_128  # noqa: E402


def main() -> int:
    first = collapse_full_128(emotional_input=42)
    second = collapse_full_128(emotional_input=42)
    assert first == second, "collapse_full_128 is not deterministic"
    print("deterministic_replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
