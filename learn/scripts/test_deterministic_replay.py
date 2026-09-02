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
from scripts.full_hexagram_shotgun import shotgun_expand



def main() -> int:
    first = shotgun_expand(emotional_input=42)
    second = shotgun_expand(emotional_input=42)
    assert first == second, "shotgun_expand is not deterministic"
    print("deterministic_replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
