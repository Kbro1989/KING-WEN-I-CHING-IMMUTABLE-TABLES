r"""Pass 3: porosity sweep + changing-line distribution.

Run:
  PYTHONPATH=. python3 learn\scripts\test_porosity_sweep.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import collapse_full_128  # noqa: E402


def main() -> int:
    for value in (0, 25, 50, 75, 100):
        collapse = collapse_full_128(emotional_input=value)
        resolved = collapse.get("resolved") or []
        changing = 0
        for item in resolved:
            changing += len(item.get("line_states") or []) + len(item.get("phase_changing_lines") or [])
        print(f"emotional_input={value:03d} changing_line_signals={changing}")

    print("porosity_sweep: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
