"""Decision matrix for King Wen 512-state consensus.

Replaces single-slider bleed with an explicit multi-axis scoring surface:
  line-balance 0.35
  + porosity-window 0.20
  + neighbor-continuity 0.15
  + hamiltonian-alignment 0.15
  + intent-modulation 0.10
  + hex-weight×slider 0.05

Source of truth:
  - oracle/interfaces.ts ModulatedProsody + ConsistencyMetrics coefficients
  - oracle/constants.ts thresholds
  - OpenJarvis emotion/kingwen_engine_adapter.py consult payload
  - emotional_engine.py line-state / Hamiltonian / Gaussian math

This module is additive. It does not modify immutable tables or
emotional_engine.py. Import it as a drop-in consensus replacement.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

VEC_KEYS: List[str] = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]

# Oracle-informed coefficients (interfaces.ts + voice modulation)
VOICE_MODULATION_COEFFICIENTS: Dict[str, float] = {
    "continuity": 0.3,
    "drift": 0.2,
    "darktone": 0.2,
    "emotion": 0.2,
    "user_override": 0.1,
}

EMOTIONAL_THRESHOLDS: Dict[str, float] = {
    "LOW": 0.3,
    "HIGH": 0.8,
    "CRISIS": 0.9,
}

# Decision-matrix weights derived from oracle prosody formula:
#   line_balance dominates, neighbor/porosity secondary, intent tertiary,
#   slider as explicit axis instead of hidden bleed scalar.
MATRIX_AXES: Dict[str, float] = {
    "line_balance": 0.35,
    "porosity_window": 0.20,
    "neighbor_continuity": 0.15,
    "hamiltonian_alignment": 0.15,
    "intent_modulation": 0.10,
    "hex_slider_weight": 0.05,
}


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _safe_mean(values: List[float], default: float = 0.0) -> float:
    return float(sum(values) / len(values)) if values else default


def _gaussian_weight(value: float, center: float, sigma: float) -> float:
    if sigma <= 1e-9:
        return 1.0 if value == center else 0.0
    return math.exp(-((value - center) ** 2) / (2.0 * sigma * sigma))


def _load_ternary_module():
    try:
        import kingwen_ternary_tables_complete as mod  # type: ignore
        return mod
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Axis 1: line-state balance — PRIMARY trigger (emotional_engine parity)
# ---------------------------------------------------------------------------
def _line_balance_score(balance: Dict[str, Any]) -> float:
    """Score yin/yang/yao balance as the primary axis."""
    yin_r = float(balance.get("yin_ratio", 0.0) or 0.0)
    yang_r = float(balance.get("yang_ratio", 0.0) or 0.0)
    yao_r = float(balance.get("yao_ratio", 0.0) or 0.0)
    changing_r = float(balance.get("changing_ratio", 0.0) or 0.0)
    # Oracle polarity: yin → whimsy/cooperation, yang → voice/authority, yao → chaos/change
    score = (
        yin_r * 0.25
        + yang_r * 0.25
        + yao_r * 0.35
        + changing_r * 0.15
    )
    return _clamp(score)


# ---------------------------------------------------------------------------
# Axis 2: porosity window — explicit slider + porosity, not hidden bleed
# ---------------------------------------------------------------------------
def _porosity_window_score(porosity_norm: float, emotional_input: int) -> float:
    """Map porosity + emotional_input to an open bounded decision window."""
    slider_factor = _clamp(emotional_input / 100.0)
    # Low slider prefers sealed/stable; high slider opens porous/changing paths
    lo = 0.05 + 0.25 * slider_factor
    hi = 0.55 + 0.45 * slider_factor
    score = _clamp((porosity_norm - lo) / max(1e-9, hi - lo))
    return _clamp(score)


# ---------------------------------------------------------------------------
# Axis 3: neighbor continuity — previous/next hex emotional distance
# ---------------------------------------------------------------------------
def _neighbor_continuity_score(resolved_item: Dict[str, Any], registry: Dict[str, Any]) -> float:
    hex_id = int(resolved_item.get("hexagram_id") or 0)
    if not hex_id:
        return 0.0
    prev_id = ((hex_id - 2) % 64) + 1
    next_id = (hex_id % 64) + 1
    current_vec = resolved_item.get("resolved_vector") or {}
    current_mag = _safe_mean([float(current_vec.get(k, 0.0) or 0.0) for k in VEC_KEYS])
    prev_mag = _safe_mean([
        float(registry.get(str(prev_id), {}).get("emotional_weights", {}).get(k, 0.0) or 0.0)
        for k in VEC_KEYS
    ])
    next_mag = _safe_mean([
        float(registry.get(str(next_id), {}).get("emotional_weights", {}).get(k, 0.0) or 0.0)
        for k in VEC_KEYS
    ])
    avg_neighbor = (prev_mag + next_mag) / 2.0
    return _clamp(1.0 - abs(current_mag - avg_neighbor))


# ---------------------------------------------------------------------------
# Axis 4: Hamiltonian alignment — trajectory/phase fit
# ---------------------------------------------------------------------------
def _hamiltonian_alignment_score(resolved_item: Dict[str, Any]) -> float:
    """Simplified Hamiltonian alignment from momentum minus line-state Lagrangian."""
    rv = resolved_item.get("resolved_vector") or {}
    lb = resolved_item.get("line_balance") or {}
    momentum = [float(rv.get(k, 0.0) or 0.0) for k in VEC_KEYS]
    lagrangian = (
        abs(lb.get("yin_ratio", 0.0) - lb.get("yang_ratio", 0.0)) * 0.5
        + lb.get("yao_ratio", 0.0) * 0.3
        + lb.get("changing_ratio", 0.0) * 0.2
    )
    pq_dot = sum(momentum) * 1.0  # phase shift rate proxy
    return _clamp(pq_dot - lagrangian)


# ---------------------------------------------------------------------------
# Axis 5: intent modulation — category/action alignment
# ---------------------------------------------------------------------------
def _intent_modulation(intent_match: float, category: str, action: str) -> float:
    """Open-pool intent modulation replacing hard-coded scalar blends."""
    cat_weights: Dict[str, float] = {
        "sovereign": 1.0,
        "boundary": 0.85,
        "transformer": 0.75,
        "dissipator": 0.6,
    }
    action_weights: Dict[str, float] = {
        "ASSERT": 1.0,
        "YIELD": 0.8,
        "ADAPT": 0.9,
        "WAIT": 0.7,
    }
    cat_score = cat_weights.get(category, 0.5)
    act_score = action_weights.get(action, 0.5)
    return _clamp((cat_score + act_score + float(intent_match or 0.0)) / 3.0)


# ---------------------------------------------------------------------------
# Axis 6: hex-weight × slider — explicit emotional_input modulation
# ---------------------------------------------------------------------------
def _hex_slider_weight(hex_weight: float, emotional_input: int) -> float:
    slider_factor = _clamp(emotional_input / 100.0)
    return _clamp(hex_weight * slider_factor)


# ---------------------------------------------------------------------------
# Master score
# ---------------------------------------------------------------------------
def score_resolved_state(
    resolved_item: Dict[str, Any],
    registry: Dict[str, Any],
    emotional_input: int = 50,
) -> float:
    """Score one resolved 512 state through the explicit decision matrix."""
    inject = resolved_item.get("inject_site") or {}
    lb = resolved_item.get("line_balance") or {}
    rv = resolved_item.get("resolved_vector") or {}
    h_id = int(resolved_item.get("hexagram_id") or 0)

    line_balance = _line_balance_score(lb)
    porosity_norm = float(inject.get("porosity_norm", inject.get("porosity", 0.35) or 0.35))
    porosity_window = _porosity_window_score(porosity_norm, emotional_input)
    neighbor = _neighbor_continuity_score(resolved_item, registry)
    hamiltonian = _hamiltonian_alignment_score(resolved_item)
    intent_mod = _intent_modulation(
        inject.get("intent_match", 0.0),
        inject.get("category", ""),
        inject.get("action", ""),
    )

    hex_weight = 0.5
    ternary = _load_ternary_module()
    if ternary and h_id:
        try:
            hex_weight = float(ternary.EMOTIONAL_WEIGHTS[str(h_id)].get("voiceWeight", 0.5))
        except Exception:
            pass
    slider_weight = _hex_slider_weight(hex_weight, emotional_input)

    total = (
        MATRIX_AXES["line_balance"] * line_balance
        + MATRIX_AXES["porosity_window"] * porosity_window
        + MATRIX_AXES["neighbor_continuity"] * neighbor
        + MATRIX_AXES["hamiltonian_alignment"] * hamiltonian
        + MATRIX_AXES["intent_modulation"] * intent_mod
        + MATRIX_AXES["hex_slider_weight"] * slider_weight
    )
    return _clamp(total)


# ---------------------------------------------------------------------------
# Consensus over full 512 resolved list
# ---------------------------------------------------------------------------
def decision_matrix_consensus(
    resolved: List[Dict[str, Any]],
    registry: Dict[str, Any],
    emotional_input: int = 50,
) -> Dict[str, Any]:
    """Compute consensus from all resolved states using explicit decision matrix.

    Returns a payload compatible with kingwen_engine_adapter.consult()
    consensus shape, but sourced from open matrix rather than single slider.
    """
    if not resolved:
        return {
            "consensus_hexagram_id": None,
            "consensus_hexagram_name": "",
            "consensus_temporal": "present",
            "consensus_yao": "stable_yao",
            "consensus_porosity_mean": 0.0,
            "consensus_vector": {k: 0.0 for k in VEC_KEYS},
            "consensus_intent": "",
            "consensus_explanation": "No resolved states available.",
            "emotional_input": emotional_input,
            "source": "decision-matrix",
            "score_details": {},
        }

    hex_scores: Dict[int, float] = {}
    hex_names: Dict[int, str] = {}
    hex_categories: Dict[int, str] = {}
    hex_actions: Dict[int, str] = {}
    hex_temporals: Dict[int, str] = {}
    score_details: Dict[int, List[Dict[str, Any]]] = {}

    for item in resolved:
        h_id = int(item.get("hexagram_id") or 0)
        if not h_id:
            continue
        score = score_resolved_state(item, registry, emotional_input)
        rv = item.get("resolved_vector") or {}
        hex_scores[h_id] = hex_scores.get(h_id, 0.0) + score
        hex_names[h_id] = str(item.get("hexagram_symbols", {}).get("name", "") or "")
        hex_categories[h_id] = str(item.get("hexagram_symbols", {}).get("category", "") or "")
        hex_actions[h_id] = str(item.get("hexagram_symbols", {}).get("action", "") or "")
        hex_temporals[h_id] = item.get("phase_temporal", "present") or "present"
        score_details.setdefault(h_id, []).append({
            "score": score,
            "phase_temporal": hex_temporals[h_id],
            "resolved_vector": {k: float(rv.get(k, 0.0) or 0.0) for k in VEC_KEYS},
            "porosity_norm": float((item.get("inject_site") or {}).get("porosity_norm", 0.35) or 0.35),
        })

    if not hex_scores:
        consensus_hexagram_id = None
        consensus_hexagram_name = ""
        consensus_temporal = "present"
        consensus_intent = ""
    else:
        consensus_hexagram_id = max(hex_scores, key=hex_scores.__getitem__)
        consensus_hexagram_name = hex_names.get(consensus_hexagram_id, "")
        consensus_temporal = hex_temporals.get(consensus_hexagram_id, "present")

        winner_vectors = [
            (item.get("resolved_vector") or {})
            for item in resolved
            if int(item.get("hexagram_id") or 0) == consensus_hexagram_id
        ]
        consensus_vector = {k: 0.0 for k in VEC_KEYS}
        if winner_vectors:
            for k in VEC_KEYS:
                consensus_vector[k] = _safe_mean([
                    float(v.get(k, 0.0) or 0.0) for v in winner_vectors
                ])

        consensus_intent = _resolve_intent(
            consensus_hexagram_id,
            consensus_temporal,
            hex_categories.get(consensus_hexagram_id, ""),
            hex_actions.get(consensus_hexagram_id, ""),
            consensus_vector,
        )

    winner_porosities = [
        float((item.get("inject_site") or {}).get("porosity", 0.35) or 0.35)
        for item in resolved
        if int(item.get("hexagram_id") or 0) == consensus_hexagram_id
    ]
    consensus_porosity_mean = _safe_mean(winner_porosities, default=0.0)

    return {
        "consensus_hexagram_id": consensus_hexagram_id,
        "consensus_hexagram_name": consensus_hexagram_name,
        "consensus_temporal": consensus_temporal,
        "consensus_yao": "stable_yao",
        "consensus_porosity_mean": consensus_porosity_mean,
        "consensus_vector": consensus_vector if winner_vectors else {k: 0.0 for k in VEC_KEYS},
        "consensus_intent": consensus_intent,
        "consensus_explanation": (
            f"Decision matrix from {len(resolved)} states: "
            f"hexagram {consensus_hexagram_id} ({consensus_hexagram_name}) "
            f"in {consensus_temporal}, "
            f"score={hex_scores.get(consensus_hexagram_id, 0.0):.4f}."
        ),
        "emotional_input": emotional_input,
        "source": "decision-matrix",
        "score_details": score_details,
    }


def _resolve_intent(
    hexagram_id: int,
    temporal: str,
    category: str,
    action: str,
    vector: Dict[str, float],
) -> str:
    parts = [f"hexagram {hexagram_id}", temporal]
    if category:
        parts.append(f"category={category}")
    if action:
        parts.append(f"action={action}")
    voice = float(vector.get("voiceWeight", 0.0) or 0.0)
    coherence = float(vector.get("coherence", 0.0) or 0.0)
    chaos = float(vector.get("chaos", 0.0) or 0.0)
    whimsy = float(vector.get("whimsy", 0.0) or 0.0)
    dark = float(vector.get("darkTone", 0.0) or 0.0)
    if voice > 0.7:
        parts.append("authoritative")
    if coherence > 0.7:
        parts.append("focused")
    if chaos > 0.6:
        parts.append("adaptive")
    if whimsy > 0.6:
        parts.append("exploratory")
    if dark > 0.6:
        parts.append("cautious")
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# Demo / verification harness
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import os
    import sys

    tables_dir = os.environ.get("KING_WEN_IMMUTABLE_TABLES") or os.path.dirname(__file__)
    sys.path.insert(0, tables_dir)

    try:
        from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS  # type: ignore
    except ImportError:
        print("decision_matrix: cannot import immutable tables")
        sys.exit(1)

    # Build a minimal resolved-state proxy from static weights + inject site
    resolved: List[Dict[str, Any]] = []
    for h_id in range(1, 65):
        weights = EMOTIONAL_WEIGHTS.get(str(h_id), {})
        inject = {}
        try:
            from kingwen_ternary_tables_complete import HEXAGRAM_INJECTION_SITE  # type: ignore
            inject = HEXAGRAM_INJECTION_SITE.get(h_id, {})
        except ImportError:
            pass
        for phase_bits in range(8):
            resolved.append({
                "hexagram_id": h_id,
                "phase_bits": phase_bits,
                "phase_temporal": "present",
                "hexagram_symbols": HEXAGRAM_BASE.get(h_id, {}),
                "resolved_vector": {
                    "chaos": float(weights.get("chaos", 0.0) or 0.0),
                    "whimsy": float(weights.get("whimsy", 0.0) or 0.0),
                    "darkTone": float(weights.get("darkTone", 0.0) or 0.0),
                    "coherence": float(weights.get("coherence", 0.0) or 0.0),
                    "voiceWeight": float(weights.get("voiceWeight", 0.0) or 0.0),
                },
                "inject_site": {
                    "porosity_norm": float(inject.get("porosity", 0) or 0) / 4.0,
                    "porosity": float(inject.get("porosity", 0) or 0),
                    "intent_match": 0.5,
                    "category": HEXAGRAM_BASE.get(h_id, {}).get("category", ""),
                    "action": HEXAGRAM_BASE.get(h_id, {}).get("action", ""),
                },
                "line_balance": {
                    "yin_ratio": 0.5,
                    "yang_ratio": 0.5,
                    "yao_ratio": 0.0,
                    "changing_ratio": 0.0,
                },
            })

    registry = {str(h_id): {"emotional_weights": EMOTIONAL_WEIGHTS.get(str(h_id), {})} for h_id in range(1, 65)}
    for ei in (0, 50, 100):
        out = decision_matrix_consensus(resolved, registry, emotional_input=ei)
        print(json.dumps({
            "emotional_input": ei,
            "consensus_hexagram_id": out["consensus_hexagram_id"],
            "consensus_hexagram_name": out["consensus_hexagram_name"],
            "consensus_temporal": out["consensus_temporal"],
            "consensus_vector": out["consensus_vector"],
            "score": out["score_details"].get(out["consensus_hexagram_id"], [{}])[0].get("score"),
        }, ensure_ascii=False))
