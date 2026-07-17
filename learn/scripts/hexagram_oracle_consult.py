#!/usr/bin/env python3
"""hexagram_oracle_consult.py

CLI tool to consult the King Wen 512-state oracle using the POG3
hexagram runtime substrate.

Usage:
  python hexagram_oracle_consult.py --chaos 0.2 --whimsy 0.9 --darkTone 0.1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.core.pog3_hexagram_runtime_substrate import POG3Runtime, IntentVector


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consult the POG3 King Wen oracle substrate.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--session-id", default="cli_session", help="Session ID")
    parser.add_argument("--chaos", type=float, default=0.5, help="Intent chaos sub-vector weight [0-1]")
    parser.add_argument("--whimsy", type=float, default=0.5, help="Intent whimsy sub-vector weight [0-1]")
    parser.add_argument("--darkTone", type=float, default=0.5, help="Intent darkTone sub-vector weight [0-1]")
    parser.add_argument("--temporal-past", type=int, default=0, choices=[0, 1], help="Temporal past phase bit")
    parser.add_argument("--temporal-present", type=int, default=1, choices=[0, 1], help="Temporal present phase bit")
    parser.add_argument("--temporal-future", type=int, default=0, choices=[0, 1], help="Temporal future phase bit")
    parser.add_argument("--action-move", type=int, default=0, choices=[0, 1], help="Action move bit")
    parser.add_argument("--action-attack", type=int, default=0, choices=[0, 1], help="Action attack bit")
    parser.add_argument("--action-interact", type=int, default=0, choices=[0, 1], help="Action interact bit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON only")

    args = parser.parse_args()

    runtime = POG3Runtime.for_session(args.session_id)
    intent = IntentVector(
        temporal=(args.temporal_past, args.temporal_present, args.temporal_future),
        emotional=(args.chaos, args.whimsy, args.darkTone),
        action=(args.action_move, args.action_attack, args.action_interact),
    )

    state_obj, capture = runtime.engine.consult(intent)

    if args.json:
        print(json.dumps(capture.to_telemetry(), indent=2))
        return 0

    print("==================================================")
    print("      POG3 KING WEN ORACLE VOLITION CONSULT       ")
    print("==================================================")
    print(f"Session ID: {args.session_id}")
    print(f"Collapsed State ID: {state_obj.state_id}")
    print(f"King Wen Hexagram: #{state_obj.to_king_wen_id()} ({state_obj.provenance['king_wen_name']})")
    print(f"Yao Lines: {state_obj.yao_lines}")
    print(f"Temporal Phase: {state_obj.temporal_phase}")
    print(f"Oracle Action: {state_obj.provenance['king_wen_action']}")
    print(f"Oracle Category: {state_obj.provenance['king_wen_category']}")
    print("--------------------------------------------------")
    print("Emotional Weights:")
    for k, v in state_obj.emotional_signature.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------")
    print(f"POG2 Save String:\n  {state_obj.to_save_string()}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
