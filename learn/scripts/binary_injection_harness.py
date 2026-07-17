"""Binary-table injection harness.

Reads exact binary state from `kingwen_ternary_tables_complete.HEXAGRAM_BASE`
and exposes it as the inject/premise substrate for each hexagram turn.
No invented constants: all state comes from the immutable tables.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from typing import Any, Dict, List

from kingwen_ternary_tables_complete import (
    EMOTIONAL_POOL,
    HEXAGRAM_BASE,
    PHASE_INFO,
    YAO_VOCABULARY,
)


YAO_ORDER = [
    "young_yin",
    "old_yin",
    "stable_yin",
    "new_yao",
    "old_yao",
    "stable_yao",
    "old_yang",
    "new_yang",
    "stable_yang",
]


def ternary_label_map() -> Dict[int, Dict[str, str]]:
    vocabulary = YAO_VOCABULARY[0]
    return {
        0: {
            "past": "old_yin",
            "present": "stable_yin",
            "default": "young_yin",
        },
        1: {
            "past": "old_yang",
            "present": "stable_yang",
            "default": "new_yang",
        },
        2: {
            "past": "old_yao",
            "present": "stable_yao",
            "future": "new_yao",
            "transition": "new_yao",
            "resolution": "old_yao",
            "dissolution": "old_yao",
            "crystallization": "stable_yao",
            "default": "old_yao",
        },
    }


def yao_key_for(ternary_state: int, temporal: str) -> str:
    family_map = ternary_label_map().get(ternary_state, {})
    candidate = family_map.get(temporal, family_map.get("default", "stable_yao"))
    vocabulary = YAO_VOCABULARY[0]
    if candidate in vocabulary:
        return candidate
    for key in YAO_ORDER:
        if vocabulary.get(key) and candidate in key:
            return key
    return "stable_yao"


def hexagram_injection_state_from_binary(hexagram_id: int) -> Dict[str, Any]:
    base = HEXAGRAM_BASE[hexagram_id]
    binary_bottom_to_top = str(base.get("binary_bottom_to_top") or "")
    line_states = []
    for idx, bit in enumerate(binary_bottom_to_top):
        line_pos = idx + 1
        ternary_state = int(bit)
        line_states.append(
            {
                "position": line_pos,
                "ternary_state": ternary_state,
                "yao_key": yao_key_for(ternary_state, "present"),
            }
        )
    return {
        "hexagram_id": hexagram_id,
        "name": base.get("name"),
        "unicode": base.get("unicode"),
        "category": base.get("category"),
        "action": base.get("action"),
        "binary_bottom_to_top": binary_bottom_to_top,
        "binary_top_to_bottom": base.get("binary_top_to_bottom"),
        "upper_trigram": base.get("upper_trigram"),
        "lower_trigram": base.get("lower_trigram"),
        "upper_idx": base.get("upper_idx"),
        "lower_idx": base.get("lower_idx"),
        "line_states": line_states,
    }


def per_turn_hexagram_subtables(
    hexagram_id: int,
    turns: int = 8,
) -> List[Dict[str, Any]]:
    base_state = hexagram_injection_state_from_binary(hexagram_id)
    phase_items = list(PHASE_INFO.items())
    subtables: List[Dict[str, Any]] = []
    for turn in range(turns):
        phase_bits, phase_meta = phase_items[turn % len(phase_items)]
        temporal = str(phase_meta.get("temporal", "") or "")
        line_states = []
        for ls in base_state["line_states"]:
            ternary_state = int(ls.get("ternary_state") or 0)
            line_states.append(
                {
                    "position": ls.get("position"),
                    "ternary_state": ternary_state,
                    "yao_key": yao_key_for(ternary_state, temporal),
                }
            )
        subtable = {
            "turn": turn + 1,
            "hexagram_id": hexagram_id,
            "phase_bits": phase_bits,
            "phase_temporal": temporal,
            "phase_polarity": phase_meta.get("polarity"),
            "phase_description": phase_meta.get("description"),
            "injection_binary": base_state["binary_bottom_to_top"],
            "symbols": {
                "name": base_state.get("name"),
                "unicode": base_state.get("unicode"),
                "category": base_state.get("category"),
                "action": base_state.get("action"),
                "upper_trigram": base_state.get("upper_trigram"),
                "lower_trigram": base_state.get("lower_trigram"),
            },
            "line_states": line_states,
        }
        subtables.append(subtable)
    return subtables


def collapse_full_binary_injection(emotional_input: int = 50) -> Dict[str, Any]:
    expanded = [hexagram_injection_state_from_binary(h_id) for h_id in range(1, 65)]
    resolved = []
    for h_id in range(1, 65):
        resolved.extend(per_turn_hexagram_subtables(h_id, turns=8))
    return {
        "emotional_input": emotional_input,
        "source": "binary_table_injection",
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "expanded": expanded,
        "resolved": resolved,
    }


def main() -> int:
    result = collapse_full_binary_injection(emotional_input=50)
    print(
        f"source={result['source']} emotional_input={result['emotional_input']} "
        f"expanded={result['total_expanded']} resolved={result['total_resolved']}"
    )
    sample = result["resolved"][0]
    print("sample_resolved_turn=", sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
