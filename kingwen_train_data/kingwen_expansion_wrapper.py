#!/usr/bin/env python3
"""Mutable expansion wrapper for King Wen /learn path engineering.

Adds:
- trigram-derived domain routing
- qutrit-like ternary line-state encoding
- multi-pass expansion tags
- velocity preservation between passes
- domain pool additions beyond voice-only inject pools

This file lives in kingwen_train_data/ because the immutable tables root
is read-only source of truth.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

_ENGINE_PATH = Path(__file__).resolve().parent.parent / "emotional_engine.py"
_EE_SPEC = importlib.util.spec_from_file_location("emotional_engine_runtime", _ENGINE_PATH)
_EE_MOD = importlib.util.module_from_spec(_EE_SPEC)
_EE_SPEC.loader.exec_module(_EE_MOD)
collapse_full_128 = _EE_MOD.collapse_full_128

_DOMAIN_TABLE = [
    "voice",
    "motion",
    "structure",
    "logic",
    "memory",
    "perception",
    "generation",
    "resolution",
]


def _trigram_indices(hexagram_id: int) -> Dict[str, int]:
    upper = ((hexagram_id - 1) // 8) + 1
    lower = ((hexagram_id - 1) % 8) + 1
    return {"upper_idx": upper, "lower_idx": lower}


def _yao_key_to_ternary(yao_key: str) -> int:
    key = str(yao_key or "").lower()
    if "yang" in key:
        return 1
    if "yao" in key:
        return 2
    return 0


def _qutrit_state_for_lines(line_states: List[Dict[str, Any]]) -> Dict[str, Any]:
    amplitudes: List[Dict[str, Any]] = []
    for ls in line_states[:6]:
        amplitudes.append(
            {
                "position": int(ls.get("line_index") or 0),
                "ternary": _yao_key_to_ternary(ls.get("yao_key") or ""),
                "yao_key": str(ls.get("yao_key") or ""),
            }
        )
    return {"amplitudes": amplitudes, "norm": math.sqrt(sum((a["ternary"] ** 2) for a in amplitudes) or 1.0)}


def _velocity(before: Dict[str, Any], after: Dict[str, Any]) -> float:
    bv = (before.get("resolved_vector") or {}).get("voiceWeight", 0.0)
    av = (after.get("resolved_vector") or {}).get("voiceWeight", 0.0)
    bc = (before.get("resolved_vector") or {}).get("coherence", 0.0)
    ac = (after.get("resolved_vector") or {}).get("coherence", 0.0)
    return math.sqrt((av - bv) ** 2 + (ac - bc) ** 2)


def _domain_tags(hexagram_id: int, phase_temporal: str) -> List[str]:
    trigrams = _trigram_indices(hexagram_id)
    domain_idx = (trigrams["upper_idx"] * 8 + trigrams["lower_idx"]) % len(_DOMAIN_TABLE)
    phase_slug = str(phase_temporal or "present").lower()
    return [
        f"domain-{_DOMAIN_TABLE[domain_idx]}",
        f"temporal-{phase_slug}",
        f"trigram-{trigrams['upper_idx']}-{trigrams['lower_idx']}",
    ]


def expand_state(state: Dict[str, Any]) -> Dict[str, Any]:
    hexagram_id = int(state.get("hexagram_id") or 0)
    phase_temporal = str(state.get("phase_temporal") or "present")
    line_states = list(state.get("line_states") or [])
    expanded = {
        "domain_tags": _domain_tags(hexagram_id, phase_temporal),
        "qutrit_state": _qutrit_state_for_lines(line_states),
        "expansion_pass_tags": ["structural", "temporal", "domain-neighbor"],
        "velocity": 0.0,
        "domain_pools": list(dict.fromkeys(list((state.get("inject_site") or {}).get("inject_pools") or []) + ["domain-memory", "domain-reasoning"])),
    }
    return {**state, **expanded}


def run_multi_pass(query: str, emotional_input: int = 50, max_passes: int = 3) -> Dict[str, Any]:
    base = collapse_full_128(emotional_input=emotional_input, request_text=query)
    resolved = list(base.get("resolved", []) or [])
    if not resolved:
        return {"query": query, "emotional_input": emotional_input, "passes": [], "status": "no_resolved"}

    enriched: List[Dict[str, Any]] = []
    previous = expanded = expand_state(resolved[0])
    for pass_index in range(1, max_passes + 1):
        current = expand_state(expanded)
        current["expansion_pass"] = pass_index
        current["velocity"] = _velocity(previous, current)
        enriched.append(current)
        previous = expanded = current

    return {
        "query": query,
        "emotional_input": emotional_input,
        "passes": enriched,
        "resolved_count": len(resolved),
        "status": "ok",
    }


if __name__ == "__main__":
    import json
    summary = run_multi_pass("King Wen state expansion with trigram domain routing", emotional_input=50)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
