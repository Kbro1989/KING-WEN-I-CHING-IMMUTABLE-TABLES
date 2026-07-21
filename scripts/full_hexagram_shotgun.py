#!/usr/bin/env python3
"""Single-pass shotgun blast: fully unbound hexagram expansion.

Projects off immutable tables only. No table modifications.
Emits ALL 64 hexagrams with full 6-slot ternary trigram positions,
512 resolved states, and 3x+ descriptive pool options in one pass.

Architecture:
  query -> parse -> inject all 64 -> expand ternary positions -> personality subsets -> downstream
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import (  # noqa: E402
    HEXAGRAM_BASE,
    PHASE_INFO,
    PHASE_LINE_MAP,
    YAO_VOCABULARY,
    EMOTIONAL_WEIGHTS,
    HEXAGRAM_INJECTION_SITE,
    VOICEBOX_VOICE_POOL,
)
from emotional_engine import (  # noqa: E402
    VEC_KEYS,
    _clamp,
    _lerp,
    expand_hexagram,
    _hamiltonian_energy,
    _yao_vocabulary_map,
    _line_yao_key,
)
from scripts.schauberger_parsing_layers import schauberger_parsing_layers  # noqa: E402

EMOTIONAL_POOL = VOICEBOX_VOICE_POOL


def _ternary_slot_matrix(hexagram_id: int, phase_bits: int = 0) -> List[Dict[str, Any]]:
    """Fully unbound 6-slot ternary trigram positions for a single hexagram.

    Each slot carries its own ternary state options (0/1/2) before anything passes.
    No aggregation, no early collapse. Changing is inferred from phase changing map.
    """
    base_ternary = HEXAGRAM_BASE[hexagram_id].get("binary_bottom_to_top", "")
    changing_positions = PHASE_LINE_MAP.get(phase_bits, [])
    slots = []
    for pos in range(1, 7):
        bit = int(base_ternary[pos - 1]) if pos <= len(base_ternary) else 0
        options = []
        for ternary_state in (0, 1, 2):
            is_changing = pos in changing_positions
            yao_key = _line_yao_key(ternary_state, "present")
            options.append({
                "ternary_state": ternary_state,
                "yao_key": yao_key,
                "yao_label": _yao_vocabulary_map().get(yao_key, ""),
                "is_changing": is_changing,
                "slot_position": pos,
            })
        slots.append({
            "slot_position": pos,
            "base_bit": bit,
            "options": options,
            "changing": pos in changing_positions,
        })
    return slots


def _personality_subsets_for_slot(slot: Dict[str, Any], inject: Dict[str, Any], vector: Dict[str, float]) -> List[Dict[str, Any]]:
    """Expand a single ternary slot into personality subset options.

    Each option is a possible expression of that trigram slot,
    projected into descriptive pool space for downstream selection.
    """
    primary_pool = inject.get("primary_pool", "voice_narrator")
    secondary_pool = inject.get("secondary_pool", "voice_narrator")
    primary_vec = EMOTIONAL_POOL.get(primary_pool, (0.1, 0.2, 0.1, 0.85, 0.85))
    secondary_vec = EMOTIONAL_POOL.get(secondary_pool, (0.1, 0.2, 0.1, 0.85, 0.85))

    subsets = []
    for opt in slot.get("options", []):
        ternary_state = opt.get("ternary_state", 0)
        yao_key = opt.get("yao_key", "stable_yao")
        # Project ternary state into pool space: no hardcoded bool, open from available pools
        if ternary_state == 0:  # yin
            pool_names = [primary_pool, "voice_warmth", "voice_subtlety"]
            blend_weights = [0.6, 0.25, 0.15]
        elif ternary_state == 1:  # yang
            pool_names = [secondary_pool, "voice_forward", "voice_clarity"]
            blend_weights = [0.6, 0.25, 0.15]
        else:  # yao
            pool_names = [primary_pool, secondary_pool, "voice_raw"]
            blend_weights = [0.4, 0.4, 0.2]

        pooled_vecs = [EMOTIONAL_POOL.get(name, (0.1, 0.2, 0.1, 0.85, 0.85)) for name in pool_names]
        blended = [0.0, 0.0, 0.0, 0.0, 0.0]
        for i in range(5):
            blended[i] = _clamp(sum(pooled_vecs[j][i] * blend_weights[j] for j in range(3)))

        subsets.append({
            "slot_position": slot.get("slot_position"),
            "ternary_state": ternary_state,
            "yao_key": yao_key,
            "yao_label": opt.get("yao_label", ""),
            "pool_names": pool_names,
            "blend_weights": blend_weights,
            "pooled_vector": dict(zip(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"], blended)),
            "expression": (
                f"slot {slot.get('slot_position')} {yao_key}: "
                f"chaos={blended[0]:.3f} whimsy={blended[1]:.3f} darkTone={blended[2]:.3f} "
                f"coherence={blended[3]:.3f} voiceWeight={blended[4]:.3f}"
            ),
        })
    return subsets


def shotgun_expand(request_text: str = "", emotional_input: int = 50) -> Dict[str, Any]:
    """Single-pass shotgun blast: all 64 hexagrams, full ternary, no early collapse."""
    expanded = []
    for h_id in range(1, 65):
        base = expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=0)
        inject = base.get("inject_site") or {}
        vector = base.get("expanded_vector") or {}
        slots = _ternary_slot_matrix(h_id, phase_bits=0)
        personality_subsets = []
        for slot in slots:
            personality_subsets.extend(_personality_subsets_for_slot(slot, inject, vector))
        expanded.append({
            "hexagram_id": h_id,
            "name": HEXAGRAM_BASE[h_id].get("name"),
            "unicode": HEXAGRAM_BASE[h_id].get("unicode"),
            "upper_trigram": HEXAGRAM_BASE[h_id].get("upper_trigram"),
            "lower_trigram": HEXAGRAM_BASE[h_id].get("lower_trigram"),
            "binary_bottom_to_top": HEXAGRAM_BASE[h_id].get("binary_bottom_to_top"),
            "phase_temporal": base.get("phase_temporal"),
            "inject_site": inject,
            "expanded_vector": vector,
            "resolved_vector": base.get("resolved_vector"),
            "ternary_slots": slots,
            "personality_subsets": personality_subsets,
            "line_states": base.get("line_states"),
            "line_balance": base.get("line_balance"),
            "sample_paths": base.get("sample_paths"),
            "yao_vocabulary": base.get("yao_vocabulary"),
            "pre_slider": base.get("pre_slider"),
            "schauberger_parsing": schauberger_parsing_layers(
                h_id,
                phase_bits=0,
                emotional_input=0,
                line_states=base.get("line_states", []),
            ),
            })

    resolved = [
        {
            "hexagram_id": h_id,
            "phase_bits": p,
            "phase_temporal": PHASE_INFO[p]["temporal"],
            "inject_site": expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=0).get("inject_site", {}),
            "resolved_vector": expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=emotional_input).get("resolved_vector", {}),
            "line_states": expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=emotional_input).get("line_states", []),
        }
        for h_id in range(1, 65)
        for p in range(8)
    ]

    energies = []
    for item in expanded:
        vec = item.get("expanded_vector") or {}
        energies.append(
            _hamiltonian_energy(
                [float(vec.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]],
                item.get("line_balance", {}),
                [0.0, 0.0, 0.0, 0.0, 0.0],
            )
        )

    return {
        "source": "kingwen-shotgun-expand",
        "request_text": request_text,
        "emotional_input": emotional_input,
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "capture_point": "first-parse",
        "expanded": expanded,
        "resolved": resolved,
        "personality_subsets_total": sum(len(item.get("personality_subsets", [])) for item in expanded),
        "avg_hamiltonian_energy": sum(energies) / max(1, len(energies)),
        "min_hamiltonian_energy": min(energies) if energies else 0.0,
        "max_hamiltonian_energy": max(energies) if energies else 0.0,
        "table_sources": {
            "hexagram_base": "HEXAGRAM_BASE",
            "phase_line_map": "PHASE_LINE_MAP",
            "yao_vocabulary": "YAO_VOCABULARY",
            "inject_site": "HEXAGRAM_INJECTION_SITE",
            "emotional_weights": "EMOTIONAL_WEIGHTS",
            "pool": "VOICEBOX_VOICE_POOL",
        },
    }


def main() -> int:
    payload = shotgun_expand(request_text="shotgun blast", emotional_input=50)
    print(json.dumps({
        "source": payload.get("source"),
        "total_expanded": payload.get("total_expanded"),
        "total_resolved": payload.get("total_resolved"),
        "personality_subsets_total": payload.get("personality_subsets_total"),
        "avg_hamiltonian_energy": payload.get("avg_hamiltonian_energy"),
        "table_sources": payload.get("table_sources"),
        "first_hexagram": {
            "hexagram_id": payload["expanded"][0].get("hexagram_id"),
            "name": payload["expanded"][0].get("name"),
            "ternary_slots": len(payload["expanded"][0].get("ternary_slots", [])),
            "personality_subsets": len(payload["expanded"][0].get("personality_subsets", [])),
        },
        "last_hexagram": {
            "hexagram_id": payload["expanded"][-1].get("hexagram_id"),
            "name": payload["expanded"][-1].get("name"),
            "ternary_slots": len(payload["expanded"][-1].get("ternary_slots", [])),
            "personality_subsets": len(payload["expanded"][-1].get("personality_subsets", [])),
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
