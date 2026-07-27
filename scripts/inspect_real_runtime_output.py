#!/usr/bin/env python3
"""inspect_real_runtime_output.py
Queries the ACTUAL LIVE RUNTIME ENGINE (pog3_hexagram_runtime_substrate.py & full_hexagram_shotgun.py)
and prints the raw, un-edited dynamic output directly produced by the table math and schauberger layers.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from full_hexagram_shotgun import shotgun_expand
from src.core.pog3_hexagram_runtime_substrate import HexagramRuntimeEngine, IntentVector

def inspect_real_runtime():
    code_problem = "Design a resilient asynchronous WebSocket event dispatcher"
    
    # 1. LIVE POG3 RUNTIME SUBSTRATE CONSULTATION
    runtime = HexagramRuntimeEngine("live_runtime_inspection")
    intent = IntentVector(temporal=(1, 0, 0), emotional=(0.6, 0.4, 0.8), action=(1, 0, 0))
    state, capture = runtime.consult(intent, context={"query": code_problem})

    print("=" * 80)
    print("LIVE RUNTIME SUBSTRATE OUTPUT (pog3_hexagram_runtime_substrate.py)")
    print("=" * 80)
    print("State ID                 :", state.state_id)
    print("Hexagram ID              :", state.to_king_wen_id())
    print("Yao Lines                :", state.yao_lines)
    print("Temporal Phase           :", state.temporal_phase)
    print("Emotional Signature      :", state.emotional_signature)
    print("Save String              :", state.to_save_string())
    print("Provenance               :", json.dumps(state.provenance, indent=2))

    # 2. LIVE SHOTGUN BLAST ENGINE OUTPUT (full_hexagram_shotgun.py)
    shotgun_res = shotgun_expand(code_problem, emotional_input=50)

    print("\n" + "=" * 80)
    print("LIVE SHOTGUN ENGINE REAL OUTPUT (full_hexagram_shotgun.py)")
    print("=" * 80)
    print("Total Expanded Pellets   :", shotgun_res["total_expanded"])
    print("Total Resolved Entries   :", shotgun_res["total_resolved"])
    print("Ternary Permutations/Hex :", shotgun_res["ternary_line_permutations_per_hex"])
    print("Total Line Permutations  :", shotgun_res["total_ternary_line_permutations"])
    print("Total Domained Routes    :", shotgun_res["total_domained_routes"])

    # Show raw un-edited pellet entries from live engine
    print("\nRAW PELLET 1 (HEXAGRAM 1):")
    print(json.dumps(shotgun_res["expanded"][0], indent=2))

    print("\nRAW PELLET 29 (HEXAGRAM 29):")
    print(json.dumps(shotgun_res["expanded"][28], indent=2))

if __name__ == "__main__":
    inspect_real_runtime()
