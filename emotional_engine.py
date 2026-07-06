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

    return {
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "expanded": expanded,
        "resolved": resolved,
    }


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
