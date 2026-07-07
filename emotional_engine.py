# =============================================================================
# EMOTIONAL ENGINE — expand/collapse/sample/resolve
# Reads: immutable tables from kingwen_ternary_tables_complete.py
#
# Note: ternary state is intentionally implicit in outputs.
# past/present/future, yin/yang/yao, and young/old/present vocabulary
# already resolve ternary expression from the immutable tables.
# =============================================================================

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from kingwen_ternary_tables_complete import (
    EMOTIONAL_POOL,
    HEXAGRAM_INJECTION_SITE,
    HEXAGRAM_BASE,
    PHASE_INFO,
    PHASE_LINE_MAP,
    POROSITY_LEVELS,
    SLIDER_CHECKLIST,
    TOTAL_ENCODINGS,
    YAO_VOCABULARY,
)


VEC_KEYS: Final[List[str]] = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
YAO_ORDER: Final[List[str]] = [
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


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _as_tuple5(vec: Tuple[float, ...]) -> Tuple[float, float, float, float, float]:
    if not vec:
        return (0.0, 0.0, 0.0, 1.0, 1.0)
    padded = list(vec) + [0.0, 0.0, 0.0, 1.0, 1.0]
    return (float(padded[0]), float(padded[1]), float(padded[2]), float(padded[3]), float(padded[4]))


def _lerp(a: Tuple[float, ...], b: Tuple[float, float, float, float, float], t: float) -> Tuple[float, float, float, float, float]:
    a = _as_tuple5(a)
    b = _as_tuple5(b)
    return (
        _clamp(a[0] + (b[0] - a[0]) * t),
        _clamp(a[1] + (b[1] - a[1]) * t),
        _clamp(a[2] + (b[2] - a[2]) * t),
        _clamp(a[3] + (b[3] - a[3]) * t),
        _clamp(a[4] + (b[4] - a[4]) * t),
    )


def _pool_by_name(name: str) -> Tuple[float, float, float, float, float]:
    vec = EMOTIONAL_POOL.get(name)
    if vec is None:
        return (0.0, 0.0, 0.0, 1.0, 1.0)
    return _as_tuple5(vec)


def _yao_vocabulary_map() -> Dict[str, str]:
    return YAO_VOCABULARY[0]


def _line_yao_key(ternary_state: int, temporal: str) -> str:
    # Resolve vocabulary from ternary state + temporal context without exposing raw ternary.
    if ternary_state == 0:
        if temporal == "past":
            return "old_yin"
        if temporal == "present":
            return "stable_yin"
        return "young_yin"
    if ternary_state == 1:
        if temporal == "past":
            return "old_yang"
        if temporal == "present":
            return "stable_yang"
        return "new_yang"
    if ternary_state == 2:
        if temporal == "past":
            return "old_yao"
        if temporal == "present":
            return "stable_yao"
        if temporal == "future":
            return "new_yao"
        if temporal == "transition":
            return "new_yao"
        if temporal == "resolution":
            return "old_yao"
        if temporal == "dissolution":
            return "old_yao"
        if temporal == "crystallization":
            return "stable_yao"
        return "old_yao"
    return "stable_yang" if ternary_state >= 1 else "stable_yin"


def expand_hexagram(
    hexagram_id: int,
    request_text: str = "",
    *,
    phase_bits: int = 0,
    emotional_input: int = 50,
) -> Dict[str, Any]:
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id)
    if inject is None:
        inject = HEXAGRAM_INJECTION_SITE[1]
    porosity = inject["porosity"]
    primary_vec = _pool_by_name(inject["primary_pool"])
    secondary_vec = _pool_by_name(inject["secondary_pool"])

    porosity_meta = POROSITY_LEVELS[porosity]
    porosity_lo, porosity_hi = porosity_meta["window"]
    slider_factor = _clamp(emotional_input / 100.0)
    bleed = _clamp(porosity_lo + (porosity_hi - porosity_lo) * slider_factor)

    base = primary_vec
    expanded = _lerp(base, secondary_vec, bleed)

    changing_positions = PHASE_LINE_MAP.get(phase_bits, [])
    base_ternary = HEXAGRAM_BASE[hexagram_id]["binary_bottom_to_top"]
    phase_line_states = []
    for idx, bit in enumerate(base_ternary):
        line_pos = idx + 1
        ternary_state = 2 if line_pos in changing_positions else int(bit)
        yao_key = _line_yao_key(ternary_state, PHASE_INFO[phase_bits]["temporal"])
        phase_line_states.append({
            "position": line_pos,
            "yao_key": yao_key,
            "yao_label": _yao_vocabulary_map().get(yao_key, ""),
        })

    hex_symbols = HEXAGRAM_BASE[hexagram_id]
    symbols_first = {
        "hexagram_id": hexagram_id,
        "name": hex_symbols.get("name"),
        "unicode": hex_symbols.get("unicode"),
        "chinese": hex_symbols.get("chinese"),
        "pinyin": hex_symbols.get("pinyin"),
        "upper_trigram": hex_symbols.get("upper_trigram"),
        "lower_trigram": hex_symbols.get("lower_trigram"),
        "category": hex_symbols.get("category"),
        "action": hex_symbols.get("action"),
        "binary_bottom_to_top": hex_symbols.get("binary_bottom_to_top"),
        "binary_top_to_bottom": hex_symbols.get("binary_top_to_bottom"),
        "upper_idx": hex_symbols.get("upper_idx"),
        "lower_idx": hex_symbols.get("lower_idx"),
    }
    symbols_first["binary"] = symbols_first.get("binary_bottom_to_top")
    symbols_first["binary_symbolic"] = symbols_first.get("binary_bottom_to_top")
    symbols_first["binary_derived"] = symbols_first.get("binary_top_to_bottom")

    return {
        "hexagram_id": hexagram_id,
        "request_text": request_text,
        "phase_bits": phase_bits,
        "hexagram_symbols": symbols_first,
        "inject_site": {
            "primary_pool": inject["primary_pool"],
            "secondary_pool": inject["secondary_pool"],
            "porosity": porosity,
            "porosity_label": porosity_meta["label"],
            "porosity_window": porosity_meta["window"],
            "porosity_description": porosity_meta["description"],
            "reason": inject["reason"],
        },
        "yao_vocabulary": _yao_vocabulary_map(),
        "line_states": phase_line_states,
        "sample_paths": [
            {
                "label": "primary",
                "pool": inject["primary_pool"],
                "vector": dict(zip(VEC_KEYS, base)),
            },
            {
                "label": "secondary",
                "pool": inject["secondary_pool"],
                "vector": dict(zip(VEC_KEYS, secondary_vec)),
            },
            {
                "label": "porous_mix",
                "bleed": bleed,
                "emotional_input": emotional_input,
                "vector": dict(zip(VEC_KEYS, expanded)),
            },
        ],
        "expanded_vector": dict(zip(VEC_KEYS, expanded)),
    }


def sample_resolve(
    hexagram_id: int,
    *,
    phase_bits: int,
    request_text: str = "",
    emotional_input: int = 50,
) -> Dict[str, Any]:
    base_expansion = expand_hexagram(
        hexagram_id,
        request_text,
        phase_bits=phase_bits,
        emotional_input=emotional_input,
    )
    expanded_vec = tuple(base_expansion["expanded_vector"][k] for k in VEC_KEYS)

    phase_meta = PHASE_INFO[phase_bits]
    temporal = phase_meta["temporal"]

    shifts = {
        "present": (0.04, 0.08, 0.0, -0.01, 0.01),
        "future": (0.02, 0.09, 0.0, 0.0, 0.02),
        "past": (0.0, 0.0, 0.05, 0.01, -0.01),
        "transition": (0.05, 0.05, 0.02, -0.02, 0.0),
        "resolution": (-0.03, -0.02, -0.02, 0.05, 0.03),
        "dissolution": (0.06, 0.04, 0.05, -0.03, -0.02),
        "crystallization": (-0.02, -0.01, -0.01, 0.04, 0.04),
        "void": (0.0, 0.0, 0.0, 0.0, 0.0),
    }

    shift = shifts.get(temporal, (0.0, 0.0, 0.0, 0.0, 0.0))
    sampled = (
        _clamp(expanded_vec[0] + shift[0]),
        _clamp(expanded_vec[1] + shift[1]),
        _clamp(expanded_vec[2] + shift[2]),
        _clamp(expanded_vec[3] + shift[3]),
        _clamp(expanded_vec[4] + shift[4]),
    )

    resolved = dict(zip(VEC_KEYS, sampled))

    return {
        "hexagram_id": hexagram_id,
        "phase_bits": phase_bits,
        "phase_temporal": temporal,
        "phase_polarity": phase_meta["polarity"],
        "phase_description": phase_meta["description"],
        "request_text": request_text,
        "hexagram_symbols": base_expansion["hexagram_symbols"],
        "yao_vocabulary": base_expansion["yao_vocabulary"],
        "inject_site": base_expansion["inject_site"],
        "line_states": base_expansion["line_states"],
        "sample_paths": base_expansion["sample_paths"],
        "expanded_vector": base_expansion["expanded_vector"],
        "resolved_vector": resolved,
        "checklist": _run_slider_checklist(resolved, phase_bits, temporal),
        "emotional_input": emotional_input,
    }


def collapse_full_128(emotional_input: int = 50) -> Dict[str, Any]:
    expanded = [
        expand_hexagram(h_id, emotional_input=emotional_input)
        for h_id in range(1, 65)
    ]
    resolved = [
        sample_resolve(h_id, phase_bits=p, emotional_input=emotional_input)
        for h_id in range(1, 65)
        for p in range(8)
    ]

    consensus = _compute_consensus_from_resolved(resolved, emotional_input)

    return {
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "expanded": expanded,
        "resolved": resolved,
        "consensus": consensus,
    }


def _compute_consensus_from_resolved(
    resolved: List[Dict[str, Any]],
    emotional_input: int,
) -> Dict[str, Any]:
    """Compute true consensus across all 512 resolved states.

    Consensus is not a normalized slider and not a coin flip.
    It is the outcome that stands out across all possibilities:
    - porosity levels that appear most frequently / strongly
    - yin/yang/yao best match from changing-line porosity
    - past/present/future temporal resolution
    - hexagram + intent that the majority of paths converge on
    """
    if not resolved:
        return {
            "emotional_input": emotional_input,
            "total_resolved": 0,
            "consensus_hexagram_id": None,
            "consensus_hexagram_name": "",
            "consensus_temporal": "present",
            "consensus_yao": "stable_yao",
            "consensus_porosity_mean": 0.0,
            "consensus_porosity_mode": 0.0,
            "consensus_vector": {"chaos": 0.0, "whimsy": 0.0, "darkTone": 0.0, "coherence": 0.0, "voiceWeight": 0.0},
            "consensus_intent": "",
            "consensus_explanation": "No resolved states available.",
        }

    # --- Temporal distribution ---
    temporal_counts: Dict[str, int] = {}
    for item in resolved:
        temporal = str(item.get("phase_temporal", "") or "")
        temporal_counts[temporal] = temporal_counts.get(temporal, 0) + 1
    consensus_temporal = max(temporal_counts, key=temporal_counts.__getitem__) if temporal_counts else "present"

    # --- Porosity consensus ---
    porosities = [float(item.get("inject_site", {}).get("porosity", 0.35) or 0.35) for item in resolved]
    porosity_mean = sum(porosities) / len(porosities)
    porosity_mode = max(set(porosities), key=porosities.count)

    # --- Vector consensus: mean across all resolved states ---
    vec_keys = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
    vec_sums = {k: 0.0 for k in vec_keys}
    vec_count = 0
    for item in resolved:
        rv = item.get("resolved_vector") or {}
        if isinstance(rv, dict):
            for k in vec_keys:
                vec_sums[k] += float(rv.get(k, 0.0) or 0.0)
            vec_count += 1
    consensus_vector = {k: (vec_sums[k] / vec_count if vec_count else 0.0) for k in vec_keys}

    # --- Hexagram consensus: score by vector alignment + frequency ---
    hex_scores: Dict[int, float] = {}
    hex_names: Dict[int, str] = {}
    hex_categories: Dict[int, str] = {}
    hex_actions: Dict[int, str] = {}
    for item in resolved:
        h_id = int(item.get("hexagram_id") or 0)
        if not h_id:
            continue
        hex_names[h_id] = str(item.get("hexagram_symbols", {}).get("name", "") or "")
        hex_categories[h_id] = str(item.get("hexagram_symbols", {}).get("category", "") or "")
        hex_actions[h_id] = str(item.get("hexagram_symbols", {}).get("action", "") or "")
        rv = item.get("resolved_vector") or {}
        voice = float(rv.get("voiceWeight", 0.0) or 0.0)
        coherence = float(rv.get("coherence", 0.0) or 0.0)
        score = voice * 0.6 + coherence * 0.4
        hex_scores[h_id] = hex_scores.get(h_id, 0.0) + score

    if not hex_scores:
        consensus_hexagram_id = None
        consensus_hexagram_name = ""
        consensus_intent = ""
    else:
        consensus_hexagram_id = max(hex_scores, key=hex_scores.__getitem__)
        consensus_hexagram_name = hex_names.get(consensus_hexagram_id, "")
        consensus_intent = _resolve_intent_from_consensus(
            consensus_hexagram_id,
            consensus_temporal,
            hex_categories.get(consensus_hexagram_id, ""),
            hex_actions.get(consensus_hexagram_id, ""),
            consensus_vector,
        )

    # --- yin/yang/yao best match from changing-line porosity ---
    # Collect line states from all resolved states for the winning hexagram
    winning_line_states = []
    for item in resolved:
        if int(item.get("hexagram_id") or 0) == consensus_hexagram_id:
            ls = item.get("line_states") or []
            if isinstance(ls, list):
                winning_line_states.extend(ls)

    consensus_yao = _best_match_yao_from_lines(winning_line_states, porosity_mean)

    # --- Explanation ---
    consensus_explanation = (
        f"Consensus resolved from {len(resolved)} states: "
        f"hexagram {consensus_hexagram_id} ({consensus_hexagram_name}) "
        f"in {consensus_temporal} phase, "
        f"yao={consensus_yao}, porosity={porosity_mode:.2f}, "
        f"voiceWeight={consensus_vector.get('voiceWeight', 0.0):.2f}, "
        f"coherence={consensus_vector.get('coherence', 0.0):.2f}. "
        f"Intent: {consensus_intent}"
    )

    return {
        "emotional_input": emotional_input,
        "total_resolved": len(resolved),
        "consensus_hexagram_id": consensus_hexagram_id,
        "consensus_hexagram_name": consensus_hexagram_name,
        "consensus_temporal": consensus_temporal,
        "consensus_yao": consensus_yao,
        "consensus_porosity_mean": round(porosity_mean, 4),
        "consensus_porosity_mode": round(porosity_mode, 4),
        "consensus_vector": {k: round(v, 4) for k, v in consensus_vector.items()},
        "consensus_intent": consensus_intent,
        "consensus_explanation": consensus_explanation,
        "temporal_distribution": temporal_counts,
    }


def _resolve_intent_from_consensus(
    hexagram_id: int,
    temporal: str,
    category: str,
    action: str,
    vector: Dict[str, float],
) -> str:
    """Derive intent path from consensus hexagram + temporal + vectors."""
    if not hexagram_id:
        return " unresolved"
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


def _best_match_yao_from_lines(
    line_states: List[Dict[str, Any]],
    porosity_mean: float,
) -> str:
    """Pick yin/yang/yao best match from changing-line porosity."""
    if not line_states:
        return "stable_yao"

    changing = [ls for ls in line_states if str(ls.get("yao_key", "") or "").startswith("old_")]
    if not changing:
        # No changing lines: stable
        present = [ls for ls in line_states if "present" in str(ls.get("yao_label", "") or "")]
        if present:
            return str(present[0].get("yao_key", "stable_yao") or "stable_yao")
        return "stable_yao"

    # Score changing lines by proximity to consensus porosity
    def _score(ls: Dict[str, Any]) -> float:
        pos = int(ls.get("position") or 0)
        label = str(ls.get("yao_label") or "")
        # Prefer changing lines in upper positions (closer to present/future)
        pos_score = pos / 6.0
        label_score = 1.0 if "old" in label else 0.5
        return pos_score + label_score

    best = max(changing, key=_score)
    return str(best.get("yao_key") or "old_yao")


def _run_slider_checklist(resolved: Dict[str, float], phase_bits: int, temporal: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for item in SLIDER_CHECKLIST:
        axis = item["axis"]
        shift = item["phase_shift"]
        direction = item["direction"]
        expected = item["expected"]

        if axis == "collapse":
            results.append({"axis": axis, "direction": direction, "expected": expected, "note": "run collapse_full_128()"})
            continue

        if axis == "pool_mix":
            if temporal in ("dissolution", "crystallization"):
                status = "expected"
            else:
                status = "idle"
            results.append({
                "axis": axis,
                "direction": direction,
                "expected": expected,
                "status": status,
                "temporal": temporal,
            })
            continue

        if axis == "porosity":
            lo, hi = (0.0, 0.05) if phase_bits == 0 else (0.05, 1.0)
            bleed_lo = lo + (hi - lo) * 0.5
            results.append({
                "axis": axis,
                "direction": direction,
                "expected": expected,
                "status": "in_window" if lo <= resolved.get("chaos", 0.0) <= hi else "out_of_window",
                "window": (lo, hi),
                "phase_bits": phase_bits,
            })
            continue

        allowed_min = max(0.0, resolved.get(axis, 0.0) - shift)
        allowed_max = min(1.0, resolved.get(axis, 0.0) + shift)

        active = (
            (direction.startswith("+past") and temporal == "past")
            or (direction.startswith("+present") and temporal == "present")
            or (direction.startswith("+future") and temporal == "future")
            or (direction.startswith("+resolution") and temporal == "resolution")
            or (direction.startswith("+void") and temporal == "void")
            or ("transition" in direction and temporal == "transition")
            or ("dissolution|crystallization" in direction and temporal in ("dissolution", "crystallization"))
        )

        results.append({
            "axis": axis,
            "direction": direction,
            "expected": expected,
            "status": "in_window" if active else "idle",
            "allowed_window": (allowed_min, allowed_max),
            "value": resolved.get(axis),
        })

    return results
