#!/usr/bin/env python3
"""Multi-layer King Wen expansion projecting off immutable tables only.

Layer 1: inject all 64 hexagrams every query/statement
Layer 2: ternary line-state expansion at each of 6 positions using YAO_VOCABULARY[0]
Layer 3: 8-phase resolution per hexagram -> 512 resolved states
Layer 4: descriptive pool expansion from VOICEBOX_VOICE_POOL / EMOTIONAL_POOL, 3x minimum
Layer 5: open-pool consensus from weighted ternary collapse across all 512 states

Immutable tables are never modified.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import (  # noqa: E402
    HEXAGRAM_BASE,
    PHASE_INFO,
    PHASE_LINE_MAP,
    POROSITY_LEVELS,
    YAO_VOCABULARY,
    EMOTIONAL_WEIGHTS,
    HEXAGRAM_INJECTION_SITE,
    VOICEBOX_VOICE_POOL,
)
from emotional_engine import (  # noqa: E402
    VEC_KEYS,
    YAO_ORDER,
    _clamp,
    _lerp,
    expand_hexagram,
    sample_resolve,
    _hamiltonian_energy,
    _yao_vocabulary_map,
)

EMOTIONAL_POOL = VOICEBOX_VOICE_POOL


def _ternary_line_options(position: int, base_bit: int, changing_positions: List[int]) -> List[Dict[str, Any]]:
    """Layer 2: ternary possibility at each line position before anything passes.

    Returns 3 options per position: yin=0, yang=1, yao=2 with vocabulary labels.
    """
    is_changing = position in changing_positions
    options = []
    for ternary_state in (0, 1, 2):
        yao_key = _line_yao_key(ternary_state, "present", is_changing)
        options.append({
            "position": position,
            "ternary_state": ternary_state,
            "yao_key": yao_key,
            "yao_label": _yao_vocabulary_map().get(yao_key, ""),
            "is_changing": is_changing,
        })
    return options


def _line_yao_key(ternary_state: int, temporal: str, is_changing: bool) -> str:
    """Map ternary state + temporal + changing flag to 9-item yao vocabulary."""
    vocab = YAO_VOCABULARY[0]
    if ternary_state == 0:
        if is_changing:
            return "old_yin"
        if temporal in ("past", "void"):
            return "stable_yin"
        return "young_yin"
    if ternary_state == 1:
        if is_changing:
            return "old_yang"
        if temporal in ("future", "crystallization"):
            return "new_yang"
        return "stable_yang"
    if ternary_state == 2:
        if is_changing:
            return "old_yao"
        if temporal in ("transition", "dissolution"):
            return "new_yao"
        return "stable_yao"
    return "stable_yao"


def _pool_descriptives_for_hex(hexagram_id: int, inject: Dict[str, Any], vector: Dict[str, float]) -> List[Dict[str, Any]]:
    """Layer 4: expand descriptive pool 3x minimum from EMOTIONAL_POOL options."""
    primary = inject.get("primary_pool", "")
    secondary = inject.get("secondary_pool", "")
    porosity = float(inject.get("porosity_norm", inject.get("porosity", 0.35) or 0.35))

    # Seed options from pool names that match inject site pools
    matching = [name for name in EMOTIONAL_POOL if primary in name or secondary in name or name.startswith("voice_") or name.startswith("personality_")]

    # Open decision pool: never hardcode; derive from available pool options
    if not matching:
        matching = ["voice_narrator", "voice_character", "voice_steady"]

    # Expand 3x: primary selector, secondary selector, blended selector
    base_pool = {
        "primary": matching[0],
        "secondary": matching[1] if len(matching) > 1 else matching[0],
        "blend": "voice_narrator",
    }
    options = []
    for label, pool_name in base_pool.items():
        pool_vec = EMOTIONAL_POOL.get(pool_name, (0.1, 0.2, 0.1, 0.85, 0.85))
        option = {
            "pool_name": pool_name,
            "selector": label,
            "pool_vector": dict(zip(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"], pool_vec)),
            "vector_blend": _clamp_blend(vector, pool_vec, porosity),
        }
        options.append(option)
    # Always keep stable fallback as a real option, not a default
    fallback = {
        "pool_name": "voice_narrator",
        "selector": "stable_fallback",
        "pool_vector": dict(zip(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"], EMOTIONAL_POOL["voice_narrator"])),
        "vector_blend": dict(zip(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"], vector)),
    }
    options.append(fallback)
    return options


def _clamp_blend(vector: Dict[str, float], pool_vec: Tuple[float, float, float, float, float], porosity: float) -> Dict[str, float]:
    """Blend resolved vector with pool vector by porosity; never return hardcoded bool."""
    out = {}
    for i, k in enumerate(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]):
        out[k] = _clamp(vector.get(k, 0.0) * (1.0 - porosity * 0.5) + pool_vec[i] * porosity * 0.5)
    return out


def multi_layer_expand(request_text: str = "", emotional_input: int = 50) -> Dict[str, Any]:
    """Layer 1-5 expansion projecting off immutable tables only.

    Returns full 64-hex ternary expansion with 512 resolved states and
    3x+ descriptive pool options per state.
    """
    # Layer 1: all 64 hexagrams injected every query/statement
    expanded = [
        expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=0)
        for h_id in range(1, 65)
    ]

    # Attach ternary-line options and pool descriptives to each expanded hexagram
    for item in expanded:
        hid = int(item.get("hexagram_id") or 0)
        base_ternary = HEXAGRAM_BASE[hid].get("binary_bottom_to_top", "")
        phase_bits = int(item.get("phase_bits") or 0)
        changing_positions = PHASE_LINE_MAP.get(phase_bits, [])
        item["tertiary_line_options"] = [
            _ternary_line_options(pos, int(base_ternary[pos - 1]) if pos <= len(base_ternary) else 0, changing_positions)
            for pos in range(1, 7)
        ]
        item["descriptive_pool_options"] = _pool_descriptives_for_hex(
            hid, item.get("inject_site") or {}, item.get("expanded_vector") or {}
        )

    # Layer 3: 8-phase resolution per hexagram -> 512 resolved states
    resolved = [
        sample_resolve(h_id, phase_bits=p, request_text=request_text, emotional_input=emotional_input)
        for h_id in range(1, 65)
        for p in range(8)
    ]

    # Layer 5: open-pool consensus across all 512 states
    consensus = open_pool_consensus(resolved, emotional_input)

    # Hamiltonian energy over all expanded hexagrams
    expanded_hamiltonian_energy = []
    for item in expanded:
        expanded_vector = item.get("expanded_vector") or {}
        expanded_hamiltonian_energy.append(
            _hamiltonian_energy(
                [float(expanded_vector.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]],
                item.get("line_balance", {}),
                [0.0, 0.0, 0.0, 0.0, 0.0],
            )
        )

    return {
        "source": "kingwen-multi-layer-expand",
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "request_text": request_text,
        "emotional_input": emotional_input,
        "capture_point": "pre_slider",
        "expanded": expanded,
        "resolved": resolved,
        "consensus": consensus,
        "expanded_hamiltonian_energy": expanded_hamiltonian_energy,
        "avg_hamiltonian_energy": sum(expanded_hamiltonian_energy) / max(1, len(expanded_hamiltonian_energy)),
        "min_hamiltonian_energy": min(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
        "max_hamiltonian_energy": max(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
    }


def open_pool_consensus(resolved: List[Dict[str, Any]], emotional_input: int) -> Dict[str, Any]:
    """Layer 5: consensus from weighted ternary collapse across all 512 states.

    Replaces hardcoded weighting with open-pool decision surface:
    - primary/secondary pool vectors
    - porosity window
    - yin/yang/yao line balance
    - emotional_input variance
    """
    if not resolved:
        return {
            "emotional_input": emotional_input,
            "total_resolved": 0,
            "consensus_hexagram_id": None,
            "consensus_hexagram_name": "",
            "consensus_temporal": "present",
            "consensus_yao": "stable_yao",
            "consensus_line_states": [],
            "consensus_porosity_mean": 0.0,
            "consensus_porosity_mode": 0.0,
            "consensus_vector": {"chaos": 0.0, "whimsy": 0.0, "darkTone": 0.0, "coherence": 0.0, "voiceWeight": 0.0},
            "consensus_intent": "",
            "consensus_explanation": "No resolved states available.",
            "open_pool_meta": {"decision_surface": "open-pool", "table_source": "kingwen_ternary_tables_complete"},
        }

    # Temporal and porosity stats
    temporal_counts: Dict[str, int] = {}
    porosities = []
    porosity_norms = []
    for item in resolved:
        temporal_counts[str(item.get("phase_temporal", "") or "")] = temporal_counts.get(str(item.get("phase_temporal", "") or ""), 0) + 1
        porosities.append(float(item.get("inject_site", {}).get("porosity", 0.35) or 0.35))
        porosity_norms.append(float(item.get("inject_site", {}).get("porosity_norm", 0.0875) or 0.0875))
    consensus_temporal = max(temporal_counts, key=temporal_counts.__getitem__) if temporal_counts else "present"
    porosity_mean = sum(porosities) / len(porosities)
    porosity_mode = max(set(porosities), key=porosities.count)

    # Open-pool tau: inject porosity_norm, emotional_input, EMOTIONAL_WEIGHTS, line balance
    tau_values = []
    for item in resolved:
        rv = item.get("resolved_vector") or {}
        inject = item.get("inject_site") or {}
        h_id = int(item.get("hexagram_id") or 0)

        base = sum(float(rv.get(k, 0.0) or 0.0) for k in VEC_KEYS)
        porosity = float(inject.get("porosity_norm", inject.get("porosity", 0.35) or 0.35))

        # Emotional weight from immutable table
        try:
            hex_weight = float(EMOTIONAL_WEIGHTS[str(h_id)].get("voiceWeight", 0.5))
        except Exception:
            hex_weight = 0.5

        # Line balance from ternary line states
        line_states = item.get("line_states") or []
        yin = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yin"))
        yang = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yang"))
        yao = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yao"))
        balance = (abs(yin - yang) + abs(yang - yao) + abs(yao - yin)) / 6.0

        # Primary/secondary pool influence
        primary_pool = inject.get("primary_pool", "")
        secondary_pool = inject.get("secondary_pool", "")
        primary_vec = EMOTIONAL_POOL.get(primary_pool, (0.1, 0.2, 0.1, 0.85, 0.85))
        secondary_vec = EMOTIONAL_POOL.get(secondary_pool, (0.1, 0.2, 0.1, 0.85, 0.85))
        pool_influence = sum(primary_vec[:2]) * 0.5 + sum(secondary_vec[2:]) * 0.5

        # Open-pool tau: no hardcoded boolean, 3+ option pools
        tau = (
            base * 0.25
            + porosity * 0.25
            + (emotional_input / 100.0) * 0.2
            + hex_weight * 0.15
            + balance * 0.25
            + pool_influence * 0.15
        )
        tau_values.append(tau)

    mu = sum(tau_values) / len(tau_values)
    sigma = max(1e-9, (sum(porosity_norms) / len(porosity_norms)) / 2.0) if porosity_norms else 1e-9

    raw_weights = [math.exp(-((t - mu) ** 2) / (2 * sigma * sigma)) for t in tau_values]
    weight_sum = sum(raw_weights)
    weights = [w / weight_sum for w in raw_weights] if weight_sum > 1e-12 else raw_weights
    weight_sum = sum(weights)

    # Weighted vector mean
    vec_keys = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
    vec_sums = {k: 0.0 for k in vec_keys}
    for item, w in zip(resolved, weights):
        rv = item.get("resolved_vector") or {}
        for k in vec_keys:
            vec_sums[k] += float(rv.get(k, 0.0) or 0.0) * w
    consensus_vector = {k: (vec_sums[k] / weight_sum if weight_sum else 0.0) for k in vec_keys}

    # Open-pool hexagram scoring: primary/secondary/fallback
    hex_scores: Dict[int, float] = {}
    hex_names: Dict[int, str] = {}
    hex_categories: Dict[int, str] = {}
    hex_actions: Dict[int, str] = {}
    for item, w in zip(resolved, weights):
        h_id = int(item.get("hexagram_id") or 0)
        if not h_id:
            continue
        hex_names[h_id] = str(item.get("hexagram_symbols", {}).get("name", "") or "")
        hex_categories[h_id] = str(item.get("hexagram_symbols", {}).get("category", "") or "")
        hex_actions[h_id] = str(item.get("hexagram_symbols", {}).get("action", "") or "")

        rv = item.get("resolved_vector") or {}
        inject = item.get("inject_site") or {}
        primary_pool = inject.get("primary_pool", "")
        secondary_pool = inject.get("secondary_pool", "")
        pool_vec = EMOTIONAL_POOL.get(primary_pool, (0.1, 0.2, 0.1, 0.85, 0.85))

        base_score = sum(float(rv.get(k, 0.0) or 0.0) for k in vec_keys) * w
        pool_score = sum(pool_vec[:2]) * 0.5 * w
        hex_scores[h_id] = hex_scores.get(h_id, 0.0) + base_score + pool_score

    if not hex_scores:
        consensus_hexagram_id = None
        consensus_hexagram_name = ""
        consensus_intent = ""
        line_states: List[Dict[str, Any]] = []
    else:
        consensus_hexagram_id = max(hex_scores, key=hex_scores.__getitem__)
        consensus_hexagram_name = hex_names.get(consensus_hexagram_id, "")
        consensus_intent = _resolve_intent_open_pool(
            consensus_hexagram_id,
            consensus_temporal,
            hex_categories.get(consensus_hexagram_id, ""),
            hex_actions.get(consensus_hexagram_id, ""),
            consensus_vector,
        )
        line_states = _weighted_line_states_from_resolved(resolved, weights, consensus_hexagram_id)

    yaolabel = line_states[0].get("yao_key") if line_states else "stable_yao"
    return {
        "emotional_input": emotional_input,
        "total_resolved": len(resolved),
        "consensus_hexagram_id": consensus_hexagram_id,
        "consensus_hexagram_name": consensus_hexagram_name,
        "consensus_temporal": consensus_temporal,
        "consensus_yao": yaolabel,
        "consensus_line_states": line_states,
        "consensus_porosity_mean": porosity_mean,
        "consensus_porosity_mode": porosity_mode,
        "consensus_vector": consensus_vector,
        "consensus_intent": consensus_intent,
        "consensus_explanation": (
            f"Open-pool consensus from {len(resolved)} states: "
            f"hexagram {consensus_hexagram_id} ({consensus_hexagram_name}) "
            f"in {consensus_temporal}, "
            f"voiceWeight={consensus_vector.get('voiceWeight', 0.0):.4f}, "
            f"coherence={consensus_vector.get('coherence', 0.0):.4f}. "
            f"Intent: {consensus_intent}"
        ),
        "open_pool_meta": {
            "decision_surface": "open-pool",
            "table_source": "kingwen_ternary_tables_complete",
            "primary_pool_source": "HEXAGRAM_INJECTION_SITE",
            "weight_source": "EMOTIONAL_WEIGHTS",
            "pool_vector_source": "VOICEBOX_VOICE_POOL",
            "yao_source": "YAO_VOCABULARY",
        },
    }


def _resolve_intent_open_pool(
    hexagram_id: int,
    temporal: str,
    category: str,
    action: str,
    vector: Dict[str, float],
) -> str:
    """Open-pool intent resolution; never hardcode binary decisions."""
    if not hexagram_id:
        return "unresolved"
    voice = float(vector.get("voiceWeight", 0.0) or 0.0)
    coherence = float(vector.get("coherence", 0.0) or 0.0)
    chaos = float(vector.get("chaos", 0.0) or 0.0)
    whimsy = float(vector.get("whimsy", 0.0) or 0.0)
    dark = float(vector.get("darkTone", 0.0) or 0.0)

    intent_parts = [f"hexagram {hexagram_id}", temporal]
    if category:
        intent_parts.append(f"category={category}")
    if action:
        intent_parts.append(f"action={action}")

    # Open-pool decision labels from vector thresholds, not fixed options
    if voice > 0.7:
        intent_parts.append("authoritative")
    if coherence > 0.7:
        intent_parts.append("focused")
    if chaos > 0.6:
        intent_parts.append("adaptive")
    if whimsy > 0.6:
        intent_parts.append("exploratory")
    if dark > 0.6:
        intent_parts.append("cautious")
    return "; ".join(intent_parts)


def _weighted_line_states_from_resolved(
    resolved: List[Dict[str, Any]],
    weights: List[float],
    hexagram_id: int,
) -> List[Dict[str, Any]]:
    if not resolved or not weights:
        return []
    vote_sums: Dict[int, Dict[str, float]] = {}
    for item, w in zip(resolved, weights):
        if int(item.get("hexagram_id") or 0) != hexagram_id:
            continue
        for ls in item.get("line_states", []):
            pos = int(ls.get("position") or 0)
            if not pos:
                continue
            label = str(ls.get("yao_key") or "stable_yao")
            bucket = vote_sums.setdefault(pos, {"yin": 0.0, "yang": 0.0, "yao": 0.0})
            if label.startswith("old_yin") or label.startswith("stable_yin") or label.startswith("young_yin"):
                bucket["yin"] += w
            elif label.startswith("old_yang") or label.startswith("stable_yang") or label.startswith("new_yang"):
                bucket["yang"] += w
            else:
                bucket["yao"] += w

    line_states: List[Dict[str, Any]] = []
    for pos in range(1, 7):
        bucket = vote_sums.get(pos)
        if not bucket:
            line_states.append({"position": pos, "yao_key": "stable_yao", "yao_label": _yao_vocabulary_map().get("stable_yao", "")})
            continue
        winner = max(bucket.items(), key=lambda kv: kv[1])[0]
        label_map = {
            "yin": "old_yin" if bucket["yin"] >= bucket["yao"] and bucket["yin"] >= bucket["yang"] else "stable_yin",
            "yang": "old_yang" if bucket["yang"] >= bucket["yao"] and bucket["yang"] >= bucket["yin"] else "stable_yang",
            "yao": "old_yao" if bucket["yao"] >= bucket["yin"] and bucket["yao"] >= bucket["yang"] else "stable_yao",
        }
        yao_key = label_map[winner]
        line_states.append({"position": pos, "yao_key": yao_key, "yao_label": _yao_vocabulary_map().get(yao_key, "")})
    return line_states


def main() -> int:
    for emotional_input in (0, 50, 75, 100):
        payload = multi_layer_expand(request_text="open consensus decision", emotional_input=emotional_input)
        consensus = payload.get("consensus") or {}
        print(json.dumps({
            "emotional_input": emotional_input,
            "total_expanded": payload.get("total_expanded"),
            "total_resolved": payload.get("total_resolved"),
            "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
            "consensus_temporal": consensus.get("consensus_temporal"),
            "consensus_yao": consensus.get("consensus_yao"),
            "consensus_vector": consensus.get("consensus_vector"),
            "open_pool_meta": consensus.get("open_pool_meta"),
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
