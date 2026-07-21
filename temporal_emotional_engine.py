# =============================================================================
# TEMPORAL EMOTIONAL ENGINE — 64-hexagram source pool with past/present/future
# simultaneous injection, expanded states, emotional agreement sampling,
# and ternary-resolved consensus per hexagram.
# =============================================================================

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Final

from kingwen_ternary_tables_complete import (
    EMOTIONAL_POOL,
    EMOTIONAL_WEIGHTS,
    HEXAGRAM_BASE,
    HEXAGRAM_INJECTION_SITE,
    PHASE_INFO,
    PHASE_LINE_MAP,
    POROSITY_LEVELS,
    SLIDER_CHECKLIST,
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


PHASE_TEMPORAL_ORDER: Final[List[str]] = ["past", "present", "future"]

BASE_PHASE_SHIFTS: Final[Dict[str, Tuple[float, float, float, float, float]]] = {
    "past": (0.0, 0.0, 0.05, 0.01, -0.01),
    "present": (0.04, 0.08, 0.0, -0.01, 0.01),
    "future": (0.02, 0.09, 0.0, 0.0, 0.02),
}
PHASE_SHIFTS = BASE_PHASE_SHIFTS


_VEC_KEYS = VEC_KEYS


def _hexagram_emotion_bias(hexagram_id: int) -> Tuple[float, float, float]:
    weights = EMOTIONAL_WEIGHTS.get(str(hexagram_id))
    hex_symbols = HEXAGRAM_BASE.get(hexagram_id, {})
    if not weights or not hex_symbols:
        return 0.33, 0.34, 0.33

    chaos = _clamp(weights.get("chaos", 0.0))
    whimsy = _clamp(weights.get("whimsy", 0.0))
    dark = _clamp(weights.get("darkTone", 0.0))
    coherence = _clamp(weights.get("coherence", 0.0))
    voice = _clamp(weights.get("voiceWeight", 0.0))

    upper_idx = _clamp(hex_symbols.get("upper_idx", 0), 0, 7)
    lower_idx = _clamp(hex_symbols.get("lower_idx", 0), 0, 7)
    binary_str = hex_symbols.get("binary_bottom_to_top", "000000")
    if not isinstance(binary_str, str):
        binary_str = "".join(str(b) for b in binary_str)
    binary_ones = _clamp(binary_str.count("1") / 6.0, 0.0, 1.0)

    # Weight-derived temporal preference: sum-to-one to prevent ratio explosion
    w_sum = chaos + whimsy + dark + coherence + voice + 1e-9
    w_past = dark / w_sum
    w_present = (chaos + whimsy) / w_sum
    w_future = (coherence + voice) / w_sum

    # Trigram calibration: 0=pure yin past, 7=pure yang future, 3.5=balanced present
    trigram_yang = (upper_idx + lower_idx) / 14.0
    t_past = _clamp((1.0 - trigram_yang) * 0.5)
    t_future = _clamp(trigram_yang * 0.5)
    t_present = _clamp(1.0 - t_past - t_future)

    # Binary momentum: 0s=past, 1s=future
    b_past = _clamp((1.0 - binary_ones) * 0.3)
    b_future = _clamp(binary_ones * 0.3)
    b_present = _clamp(1.0 - b_past - b_future)

    # Blend: weights dominant, trigram midpoint, binary weakest
    raw_past = 0.5 * w_past + 0.3 * t_past + 0.2 * b_past
    raw_present = 0.5 * w_present + 0.3 * t_present + 0.2 * b_present
    raw_future = 0.5 * w_future + 0.3 * t_future + 0.2 * b_future

    s = raw_past + raw_present + raw_future + 1e-9
    return raw_past / s, raw_present / s, raw_future / s


def _hexagram_emotion_bias_scale(hexagram_id: int) -> float:
    weights = EMOTIONAL_WEIGHTS.get(str(hexagram_id))
    if not weights:
        return 0.25

    chaos = _clamp(weights.get("chaos", 0.0))
    whimsy = _clamp(weights.get("whimsy", 0.0))
    coherence = _clamp(weights.get("coherence", 0.0))
    voice = _clamp(weights.get("voiceWeight", 0.0))

    disorder = chaos + whimsy
    order = coherence + voice
    if order <= 1e-6:
        return 0.40
    raw = disorder / order
    return _clamp(0.15 + raw * 0.25, 0.15, 0.40)


def _apply_emotional_bias_to_shift(
    base_shift: Tuple[float, float, float, float, float],
    bias: Tuple[float, float, float],
    scale: float = 0.08,
) -> Tuple[float, float, float, float, float]:
    past_bias, present_bias, future_bias = bias
    return (
        _clamp(base_shift[0] + (past_bias - 1.0 / 3.0) * scale),
        _clamp(base_shift[1] + (present_bias - 1.0 / 3.0) * scale),
        _clamp(base_shift[2] + (future_bias - 1.0 / 3.0) * scale),
        _clamp(base_shift[3] + ((past_bias + present_bias + future_bias) / 3.0 - 1.0 / 3.0) * scale),
        _clamp(base_shift[4] + ((past_bias + present_bias + future_bias) / 3.0 - 1.0 / 3.0) * scale),
    )


def _anti_convergence_noise(vec: Tuple[float, ...]) -> Tuple[float, float, float, float, float]:
    center = _as_tuple5(vec)
    noise = [center[i] + _clamp((0.5 - center[i]) * 0.08 + (0.5 - center[i])) for i in range(5)]
    return _as_tuple5(noise)


def _hexagram_emotion_base(hexagram_id: int) -> Tuple[float, float, float, float, float]:
    weights = EMOTIONAL_WEIGHTS.get(str(hexagram_id))
    if weights:
        return _as_tuple5((
            weights.get("chaos", 0.0),
            weights.get("whimsy", 0.0),
            weights.get("darkTone", 0.0),
            weights.get("coherence", 0.0),
            weights.get("voiceWeight", 0.0),
        ))
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id)
    if not inject:
        inject = HEXAGRAM_INJECTION_SITE[1]
    return _pool_by_name(inject["primary_pool"])


def _phase_bleed(porosity: int) -> float:
    lo, hi = POROSITY_LEVELS[porosity]["window"]
    return _clamp(lo + (hi - lo) * 0.5)


def _clamp_shifted(vec: Tuple[float, ...], shift: Tuple[float, float, float, float, float]) -> Tuple[float, float, float, float, float]:
    return (_clamp(vec[0] + shift[0]), _clamp(vec[1] + shift[1]), _clamp(vec[2] + shift[2]), _clamp(vec[3] + shift[3]), _clamp(vec[4] + shift[4]))


def expand_hexagram_tri_temporal(hexagram_id: int, request_text: str = "") -> Dict[str, Any]:
    base_vec = _hexagram_emotion_base(hexagram_id)
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id)
    if not inject:
        inject = HEXAGRAM_INJECTION_SITE[1]
    secondary_vec = _pool_by_name(inject["secondary_pool"])
    bleed = _phase_bleed(inject["porosity"])
    expanded_base = _lerp(base_vec, secondary_vec, bleed)

    bias = _hexagram_emotion_bias(hexagram_id)
    scale = _hexagram_emotion_bias_scale(hexagram_id)
    past_shift = _apply_emotional_bias_to_shift(PHASE_SHIFTS["past"], bias, scale=scale)
    present_shift = _apply_emotional_bias_to_shift(PHASE_SHIFTS["present"], bias, scale=scale)
    future_shift = _apply_emotional_bias_to_shift(PHASE_SHIFTS["future"], bias, scale=scale)

    raw_past = _clamp_shifted(expanded_base, past_shift)
    raw_present = _clamp_shifted(expanded_base, present_shift)
    raw_future = _clamp_shifted(expanded_base, future_shift)

    past_vec = _as_tuple5(raw_past)
    present_vec = _as_tuple5(raw_present)
    future_vec = _as_tuple5(raw_future)

    distances = (
        _vector_distance(past_vec, present_vec),
        _vector_distance(present_vec, future_vec),
        _vector_distance(past_vec, future_vec),
    )
    mean_dist = sum(distances) / 3.0
    if mean_dist < 0.06:
        anti = _anti_convergence_noise(expanded_base)
        past_vec = _as_tuple5(_clamp_shifted(anti, past_shift))
        present_vec = _as_tuple5(_clamp_shifted(anti, present_shift))
        future_vec = _as_tuple5(_clamp_shifted(anti, future_shift))

    hex_symbols = HEXAGRAM_BASE[hexagram_id]

    return {
        "hexagram_id": hexagram_id,
        "request_text": request_text,
        "hexagram_symbols": {
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
            "binary": hex_symbols.get("binary_bottom_to_top"),
            "binary_symbolic": hex_symbols.get("binary_bottom_to_top"),
            "binary_derived": hex_symbols.get("binary_top_to_bottom"),
        },
        "inject_site": {
            "primary_pool": inject["primary_pool"],
            "secondary_pool": inject["secondary_pool"],
            "porosity": inject["porosity"],
            "porosity_label": POROSITY_LEVELS[inject["porosity"]]["label"],
            "porosity_window": POROSITY_LEVELS[inject["porosity"]]["window"],
            "porosity_description": POROSITY_LEVELS[inject["porosity"]]["description"],
            "reason": inject["reason"],
        },
        "yao_vocabulary": _yao_vocabulary_map(),
        "temporal_emotions": {
            "past": dict(zip(VEC_KEYS, _as_tuple5(past_vec))),
            "present": dict(zip(VEC_KEYS, _as_tuple5(present_vec))),
            "future": dict(zip(VEC_KEYS, _as_tuple5(future_vec))),
        },
        "expanded_vector": dict(zip(VEC_KEYS, expanded_base)),
    }


def sample_temporal_slider(hexagram_id: int, request_text: str = "") -> Dict[str, Any]:
    expansion = expand_hexagram_tri_temporal(hexagram_id, request_text)
    temporal_emotions = expansion["temporal_emotions"]

    sampled: Dict[str, Dict[str, Any]] = {}
    for temporal in PHASE_TEMPORAL_ORDER:
        vec = tuple(temporal_emotions[temporal][k] for k in VEC_KEYS)
        sampled[temporal] = {
            "hexagram_id": hexagram_id,
            "temporal": temporal,
            "vector": dict(zip(VEC_KEYS, vec)),
            "checklist": _run_temporal_slider_checklist(vec, temporal),
        }

    temporal_consensus = _build_temporal_consensus(sampled)
    temporal_resolution = _resolve_temporal_meta(sampled)
    temporal_resolution = _resolve_temporal_meta(sampled)

    return {
        "hexagram_id": hexagram_id,
        "request_text": request_text,
        "hexagram_symbols": expansion["hexagram_symbols"],
        "inject_site": expansion["inject_site"],
        "yao_vocabulary": expansion["yao_vocabulary"],
        "temporal_emotions": expansion["temporal_emotions"],
        "sampled_temporal": sampled,
        "temporal_consensus": temporal_consensus,
        "temporal_resolution": temporal_resolution,
    }


def _build_temporal_consensus(sampled: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    vectors = {t: tuple(sampled[t]["vector"][k] for k in VEC_KEYS) for t in PHASE_TEMPORAL_ORDER}
    agreement = _temporal_agreement(sampled)
    spread = _temporal_spread(sampled)

    center = [
        sum(vectors[t][i] for t in PHASE_TEMPORAL_ORDER) / 3.0
        for i in range(5)
    ]

    expanded_base = center
    past_bias = _clamp(expanded_base[2] * 1.0 + expanded_base[4] * 0.5 - expanded_base[0] * 0.5 - expanded_base[1] * 0.5)
    present_bias = _clamp(expanded_base[0] * 1.0 + expanded_base[1] * 0.5 - expanded_base[2] * 0.5 - expanded_base[3] * 0.25)
    future_bias = _clamp(expanded_base[3] * 1.0 + expanded_base[4] * 0.5 - expanded_base[0] * 0.5 - expanded_base[2] * 0.5)

    bias_score = {
        "past": past_bias,
        "present": present_bias,
        "future": future_bias,
    }

    b_sum = sum(bias_score.values()) + 1e-9
    bias_score = {k: v / b_sum for k, v in bias_score.items()}

    best_temporal = PHASE_TEMPORAL_ORDER[0]
    best_score = spread[best_temporal] - bias_score[best_temporal]
    for t in PHASE_TEMPORAL_ORDER[1:]:
        score = spread[t] - bias_score[t]
        if score < best_score:
            best_score = score
            best_temporal = t

    return {
        "past": sampled["past"]["vector"],
        "present": sampled["present"]["vector"],
        "future": sampled["future"]["vector"],
        "agreement": agreement,
        "spread": spread,
        "bias": bias_score,
        "agree_temporal": best_temporal,
        "selection": "bias_plus_spread",
    }


def _temporal_agreement(sampled: Dict[str, Dict[str, Any]]) -> float:
    vectors = [tuple(sampled[t]["vector"][k] for k in VEC_KEYS) for t in PHASE_TEMPORAL_ORDER]
    pairwise = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            pairwise.append(_vector_distance(vectors[i], vectors[j]))
    if not pairwise:
        return 1.0
    max_dist = sum((1.0 - 0.0) ** 2 for _ in range(5)) ** 0.5 * 3
    mean_dist = sum(pairwise) / len(pairwise)
    return _clamp(1.0 - (mean_dist / max_dist))


def _temporal_spread(sampled: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    vectors = [tuple(sampled[t]["vector"][k] for k in VEC_KEYS) for t in PHASE_TEMPORAL_ORDER]
    center = [sum(v[i] for v in vectors) / 3.0 for i in range(5)]
    return {
        temporal: sum((vectors[i][k] - center[k]) ** 2 for k in range(5)) ** 0.5
        for i, temporal in enumerate(PHASE_TEMPORAL_ORDER)
    }


def _resolve_temporal_meta(sampled: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    past_vec = tuple(sampled["past"]["vector"][k] for k in VEC_KEYS)
    present_vec = tuple(sampled["present"]["vector"][k] for k in VEC_KEYS)
    future_vec = tuple(sampled["future"]["vector"][k] for k in VEC_KEYS)

    past_present = _vector_distance(past_vec, present_vec)
    present_future = _vector_distance(present_vec, future_vec)
    past_future = _vector_distance(past_vec, future_vec)

    if past_present < 1e-6 and present_future < 1e-6:
        trajectory = "still"
    elif present_future < past_present:
        trajectory = "converging"
    elif past_present < present_future:
        trajectory = "diverging"
    else:
        trajectory = "cycling"

    tension = (past_present + present_future + past_future) / 3.0
    resolution = _clamp(1.0 - tension)

    meta_vector = (
        _clamp((past_vec[0] + present_vec[0] + future_vec[0]) / 3.0),
        _clamp((past_vec[1] + present_vec[1] + future_vec[1]) / 3.0),
        _clamp((past_vec[2] + present_vec[2] + future_vec[2]) / 3.0),
        _clamp((past_vec[3] + present_vec[3] + future_vec[3]) / 3.0),
        _clamp((past_vec[4] + present_vec[4] + future_vec[4]) / 3.0),
    )

    dominant = max(zip(VEC_KEYS, meta_vector), key=lambda kv: kv[1])[0]

    return {
        "trajectory": trajectory,
        "tension": _clamp(tension),
        "resolution": resolution,
        "meta_vector": dict(zip(VEC_KEYS, meta_vector)),
        "dominant_axis": dominant,
        "past_present_distance": past_present,
        "present_future_distance": present_future,
        "past_future_distance": past_future,
        "description": _meta_description(trajectory, resolution, dominant),
    }


def _meta_description(trajectory: str, resolution: float, dominant: str) -> str:
    trajectory_map = {
        "still": "the emotional field holds steady across all three times",
        "converging": "past and future are collapsing toward the present",
        "diverging": "the present is splitting away from both past and future",
        "cycling": "emotion cycles through past, present, and future without settling",
    }
    resolution_map = {
        "low": "unresolved emotional tension remains high",
        "mid": "partial resolution between temporal states",
        "high": "strong emotional consensus across time",
    }
    if resolution < 0.33:
        resolution_label = "low"
    elif resolution < 0.66:
        resolution_label = "mid"
    else:
        resolution_label = "high"

    return f"{trajectory_map.get(trajectory, trajectory)}; {resolution_map.get(resolution_label, '')}; dominant axis: {dominant}"


def sample_all_hexagrams_temporal(request_text: str = "") -> Dict[str, Any]:
    expanded = [expand_hexagram_tri_temporal(h_id, request_text) for h_id in range(1, 65)]
    sampled = [sample_temporal_slider(h_id, request_text) for h_id in range(1, 65)]

    return {
        "total_hexagrams": len(expanded),
        "total_sampled": len(sampled),
        "expanded": expanded,
        "sampled": sampled,
        "global_consensus": _global_hexagram_consensus(sampled),
    }


def _run_temporal_slider_checklist(vec: Tuple[float, ...], temporal: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    vec_map = dict(zip(VEC_KEYS, vec))

    checks = [
        {"axis": "chaos", "shift": 0.05, "expect_temporal": "present"},
        {"axis": "whimsy", "shift": 0.1, "expect_temporal": "future"},
        {"axis": "darkTone", "shift": 0.05, "expect_temporal": "past"},
        {"axis": "coherence", "shift": 0.05, "expect_temporal": "resolution"},
        {"axis": "voiceWeight", "shift": 0.05, "expect_temporal": "void"},
    ]
    mix_checks = [
        {"axis": "pool_mix", "expect_temporal": ["dissolution", "crystallization"], "expected": "pool swap at dispersal/forming"},
        {"axis": "collapse", "expect_temporal": ["void"], "expected": "full 512 state collapse resets to origin"},
    ]

    for item in checks:
        axis = item["axis"]
        shift = item["shift"]
        expect = item["expect_temporal"]
        value = vec_map.get(axis, 0.0)
        lo = max(0.0, value - shift)
        hi = min(1.0, value + shift)
        active = temporal == expect
        results.append({
            "axis": axis,
            "expected_temporal": expect,
            "expected": f"{axis} peaks at {expect}",
            "status": "in_window" if active else "idle",
            "allowed_window": (lo, hi),
            "value": value,
        })

    for item in mix_checks:
        axis = item["axis"]
        expect = item["expect_temporal"]
        expected = item["expected"]
        active = temporal in expect
        results.append({
            "axis": axis,
            "direction": f"+{'|'.join(expect)}",
            "expected": expected,
            "status": "expected" if active else "idle",
            "temporal": temporal,
        })

    results.append({
        "axis": "porosity",
        "direction": "+transition",
        "expected": "boundary bleed peaks at threshold",
        "status": "in_window" if temporal == "transition" else "idle",
        "window": (0.05, 1.0) if temporal != "past" else (0.0, 0.05),
    })

    return results


def _vector_distance(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    a = _as_tuple5(a)
    b = _as_tuple5(b)
    return sum((a[i] - b[i]) ** 2 for i in range(5)) ** 0.5


def _global_hexagram_consensus(sampled: List[Dict[str, Any]]) -> Dict[str, Any]:
    winners = [s["temporal_consensus"]["agree_temporal"] for s in sampled]
    agreements = [s["temporal_consensus"]["agreement"] for s in sampled]
    counts = {t: winners.count(t) for t in PHASE_TEMPORAL_ORDER}
    return {
        "winner_counts": counts,
        "mean_agreement": sum(agreements) / len(agreements),
        "min_agreement": min(agreements),
        "max_agreement": max(agreements),
        "dominant_temporal": max(counts, key=counts.get),
        "trajectory_distribution": dict(zip(PHASE_TEMPORAL_ORDER, [counts[t] / max(1, len(sampled)) for t in PHASE_TEMPORAL_ORDER])),
    }


__all__ = [
    "PHASE_TEMPORAL_ORDER",
    "PHASE_SHIFTS",
    "expand_hexagram_tri_temporal",
    "sample_temporal_slider",
    "sample_all_hexagrams_temporal",
    "build_temporal_consensus",
    "resolve_temporal_meta",
]
