# =============================================================================
# EMOTIONAL ENGINE — expand/collapse/sample/resolve/capture
# Source of truth: kingwen_ternary_tables_complete immutable tables
#
# Design:
#   - Yin/yang/yao is the PRIMARY expansion trigger
#   - Trigram structure provides contextual weighting, not primary driver
#   - Neighbor continuity and intent modulate on top of line-state foundation
#   - Pre-slider capture point preserves full expansion before slider bleed
# =============================================================================

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Tuple

from kingwen_ternary_tables_complete import (
    VOICEBOX_VOICE_POOL,
    HEXAGRAM_BASE,
    PHASE_INFO,
    PHASE_LINE_MAP,
    POROSITY_LEVELS,
    TOTAL_ENCODINGS,
    YAO_VOCABULARY,
    EMOTIONAL_WEIGHTS,
    HEXAGRAM_INJECTION_SITE,
)

# Re-export voicebox pool under the generic alias used by /learn tests and
# downstream exporters. Immutable table source remains `VOICEBOX_VOICE_POOL`.
EMOTIONAL_POOL = VOICEBOX_VOICE_POOL

VEC_KEYS: List[str] = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
YAO_ORDER: List[str] = [
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

# Intent vocabulary for text extraction
_INTENT_KEYWORDS: Dict[str, List[str]] = {
    "create": ["create", "build", "make", "generate", "new", "start", "begin", "initiate"],
    "destroy": ["destroy", "end", "kill", "stop", "break", "collapse", "remove", "delete"],
    "transform": ["transform", "change", "evolve", "morph", "shift", "transition", "become"],
    "explore": ["explore", "discover", "find", "search", "wander", "journey", "seek"],
    "understand": ["understand", "learn", "see", "clarity", "know", "comprehend", "insight"],
    "feel": ["feel", "emotion", "love", "fear", "joy", "pain", "heart", "soul"],
    "speak": ["speak", "voice", "say", "tell", "express", "communicate", "utter"],
    "listen": ["listen", "hear", "silence", "quiet", "still", "pause", "receive"],
    "connect": ["connect", "join", "unite", "bond", "link", "bridge", "weave"],
    "protect": ["protect", "defend", "guard", "secure", "shelter", "preserve", "safe"],
    "conflict": ["conflict", "fight", "oppose", "clash", "battle", "resist", "challenge"],
    "heal": ["heal", "repair", "restore", "renew", "mend", "fix", "revive"],
    "grow": ["grow", "expand", "increase", "amplify", "scale", "rise", "flourish"],
    "release": ["release", "let go", "free", "surrender", "yield", "open", "flow"],
    "focus": ["focus", "concentrate", "center", "aim", "direct", "target", "precision"],
}


# =============================================================================
# Utility functions
# =============================================================================

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _yao_vocabulary_map() -> Dict[str, str]:
    return YAO_VOCABULARY.get(0, {})


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


# =============================================================================
# Intent extraction from request_text
# =============================================================================

def extract_intent(request_text: str) -> Dict[str, Any]:
    """Extract intent signals from user request_text."""
    text = (request_text or "").lower()
    words = re.findall(r"[a-z0-9]+", text)
    word_set = set(words)
    
    matched: Dict[str, float] = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        score = sum(1.0 / (i + 1) for i, kw in enumerate(keywords) if kw in word_set)
        if score > 0:
            matched[intent] = score
    
    dominant = max(matched, key=matched.get) if matched else "understand"
    total = sum(matched.values())
    normalized = {k: v / total for k, v in matched.items()} if total > 0 else {}
    intensity = _clamp(len(text.split()) / 50.0) if text.strip() else 0.0
    
    return {
        "request_text": request_text,
        "query_tokens": list(word_set),
        "matched_intents": matched,
        "dominant_intent": dominant,
        "intensity": intensity,
        "word_count": len(words),
        "intent_vector": _intent_to_vector(normalized, word_set),
    }


def _intent_to_vector(intent_scores: Dict[str, float], word_set: set = None) -> List[float]:
    """Map intent distribution and semantic tokens to dynamic 5-axis vector seed."""
    base = [0.1, 0.1, 0.1, 0.8, 0.85]
    
    chaos_boost = (
        intent_scores.get("conflict", 0.0) * 0.4 +
        intent_scores.get("destroy", 0.0) * 0.3 +
        intent_scores.get("transform", 0.0) * 0.2 +
        intent_scores.get("create", 0.0) * 0.15
    )
    base[0] = _clamp(base[0] + chaos_boost)
    
    whimsy_boost = (
        intent_scores.get("explore", 0.0) * 0.3 +
        intent_scores.get("feel", 0.0) * 0.3 +
        intent_scores.get("heal", 0.0) * 0.2 +
        intent_scores.get("release", 0.0) * 0.2
    )
    base[1] = _clamp(base[1] + whimsy_boost)
    
    dark_boost = (
        intent_scores.get("destroy", 0.0) * 0.3 +
        intent_scores.get("conflict", 0.0) * 0.25 +
        intent_scores.get("transform", 0.0) * 0.15
    )
    base[2] = _clamp(base[2] + dark_boost)
    
    coh_boost = (
        intent_scores.get("understand", 0.0) * 0.15 +
        intent_scores.get("focus", 0.0) * 0.15 +
        intent_scores.get("speak", 0.0) * 0.1 +
        intent_scores.get("protect", 0.0) * 0.1
    )
    base[3] = _clamp(base[3] + coh_boost)
    
    vw_boost = (
        intent_scores.get("speak", 0.0) * 0.15 +
        intent_scores.get("protect", 0.0) * 0.1 +
        intent_scores.get("connect", 0.0) * 0.1 +
        intent_scores.get("grow", 0.0) * 0.15
    )
    base[4] = _clamp(base[4] + vw_boost)

    # Deterministic semantic token hash perturbation for continuous input variation
    if word_set:
        hash_val = sum(sum(ord(c) for c in w) for w in word_set)
        p_chaos = ((hash_val % 97) / 97.0) * 0.12
        p_whimsy = (((hash_val // 7) % 89) / 89.0) * 0.12
        p_dark = (((hash_val // 13) % 83) / 83.0) * 0.12
        p_coh = (((hash_val // 19) % 79) / 79.0) * 0.12
        p_vw = (((hash_val // 23) % 73) / 73.0) * 0.12
        base[0] = _clamp(base[0] + p_chaos)
        base[1] = _clamp(base[1] + p_whimsy)
        base[2] = _clamp(base[2] + p_dark)
        base[3] = _clamp(base[3] + p_coh)
        base[4] = _clamp(base[4] + p_vw)
    
    return base


# =============================================================================
# Structural derivation — yin/yang/yao is PRIMARY trigger
# =============================================================================

def _line_state_balance(binary_bottom_to_top: str, phase_bits: int) -> Dict[str, Any]:
    """Compute yin/yang/yao balance from binary + phase.
    
    This is the PRIMARY expansion trigger. Line states determine
    pool selection, porosity, and vector direction.
    """
    changing_positions = PHASE_LINE_MAP.get(phase_bits, [])
    temporal = PHASE_INFO[phase_bits]["temporal"]
    line_states = []
    yin_count = 0
    yang_count = 0
    yao_count = 0
    changing_count = 0
    old_yin_count = 0
    old_yang_count = 0
    old_yao_count = 0
    stable_yin_count = 0
    stable_yang_count = 0
    stable_yao_count = 0
    
    for idx, bit in enumerate(binary_bottom_to_top):
        line_pos = idx + 1
        ternary_state = 2 if line_pos in changing_positions else int(bit)
        yao_key = _line_yao_key(ternary_state, temporal)
        
        if ternary_state == 0:
            yin_count += 1
            if "old" in yao_key:
                old_yin_count += 1
            elif "stable" in yao_key:
                stable_yin_count += 1
        elif ternary_state == 1:
            yang_count += 1
            if "old" in yao_key:
                old_yang_count += 1
            elif "stable" in yao_key:
                stable_yang_count += 1
        else:
            yao_count += 1
            changing_count += 1 if line_pos in changing_positions else 0
            if "old" in yao_key:
                old_yao_count += 1
            elif "stable" in yao_key:
                stable_yao_count += 1
        
        line_states.append({
            "position": line_pos,
            "ternary_state": ternary_state,
            "yao_key": yao_key,
            "yao_label": _yao_vocabulary_map().get(yao_key, ""),
        })
    
    total = max(len(binary_bottom_to_top), 1)
    yin_ratio = yin_count / total
    yang_ratio = yang_count / total
    yao_ratio = yao_count / total
    
    return {
        "line_states": line_states,
        "yin_count": yin_count,
        "yang_count": yang_count,
        "yao_count": yao_count,
        "changing_count": changing_count,
        "old_yin_count": old_yin_count,
        "old_yang_count": old_yang_count,
        "old_yao_count": old_yao_count,
        "stable_yin_count": stable_yin_count,
        "stable_yang_count": stable_yang_count,
        "stable_yao_count": stable_yao_count,
        "yin_ratio": yin_ratio,
        "yang_ratio": yang_ratio,
        "yao_ratio": yao_ratio,
        "changing_ratio": changing_count / total,
    }


def _trigram_vector(name: str) -> List[float]:
    """Trigram context vector — SECONDARY to line-state balance."""
    mapping = {
        "Qian":  [0.1, 0.2, 0.05, 0.9, 0.95],
        "Kun":   [0.05, 0.1, 0.05, 0.95, 0.85],
        "Zhen":  [0.4, 0.35, 0.1, 0.75, 0.85],
        "Kan":   [0.5, 0.15, 0.55, 0.5, 0.7],
        "Li":    [0.2, 0.3, 0.1, 0.85, 0.88],
        "Xun":   [0.2, 0.5, 0.1, 0.75, 0.78],
        "Dui":   [0.25, 0.6, 0.05, 0.8, 0.82],
        "Gen":   [0.1, 0.1, 0.2, 0.92, 0.85],
    }
    return mapping.get(name, [0.15, 0.25, 0.1, 0.82, 0.85])


def _pool_by_name(name: str) -> List[float]:
    vec = VOICEBOX_VOICE_POOL.get(name)
    if vec is not None:
        return list(vec)
    # Fallback for neighbor pool names
    if name.startswith("hex_") and name.endswith("_primary"):
        hid = int(name.split("_")[1])
        return _primary_pool_for_hex(hid)
    if name.startswith("hex_") and name.endswith("_secondary"):
        hid = int(name.split("_")[1])
        return _secondary_pool_for_hex(hid)
    # Deterministic fallback
    digest = abs(hash(name)) % 1000
    return [
        _clamp((digest % 100) / 100.0),
        _clamp(((digest * 7) % 100) / 100.0),
        _clamp(((digest * 13) % 100) / 100.0),
        _clamp(((digest * 17) % 100) / 100.0),
        _clamp(((digest * 23) % 100) / 100.0),
    ]


def _primary_pool_for_hex(hexagram_id: int) -> List[float]:
    """Derive primary pool from line-state dominance."""
    hex_data = HEXAGRAM_BASE[hexagram_id]
    binary = hex_data.get("binary_bottom_to_top", "")
    phase_bits = 0
    balance = _line_state_balance(binary, phase_bits)
    
    # Yin-heavy → warm_cooperation, yang-heavy → hierarchical_command
    # Balanced → harmonic_flow, yao-heavy → birth_chaos
    yin_r = balance["yin_ratio"]
    yang_r = balance["yang_ratio"]
    yao_r = balance["yao_ratio"]
    
    if yao_r > 0.3:
        return [0.65, 0.35, 0.45, 0.35, 0.55]  # birth_chaos
    if yin_r > 0.6:
        return [0.15, 0.45, 0.08, 0.88, 0.82]  # warm_cooperation
    if yang_r > 0.6:
        return [0.08, 0.08, 0.25, 0.97, 0.95]  # hierarchical_command
    if yin_r > 0.4 and yang_r > 0.4:
        return [0.05, 0.2, 0.0, 0.95, 0.9]     # harmonic_flow
    return [0.1, 0.25, 0.05, 0.9, 0.95]        # genesis_spark


def _secondary_pool_for_hex(hexagram_id: int) -> List[float]:
    """Derive secondary pool from neighboring hexagrams."""
    neighbors = _hex_neighbors(hexagram_id)
    prev_vec = _primary_pool_for_hex(neighbors["previous"])
    next_vec = _primary_pool_for_hex(neighbors["next"])
    return _lerp(prev_vec, next_vec, 0.5)


def _lerp(a: List[float], b: List[float], t: float) -> List[float]:
    return [_clamp(a[i] + (b[i] - a[i]) * t) for i in range(len(a))]


def _hex_neighbors(hexagram_id: int) -> Dict[str, int]:
    prev_id = ((hexagram_id - 2) % 64) + 1
    next_id = (hexagram_id % 64) + 1
    return {"previous": prev_id, "next": next_id}


# =============================================================================
# Intent matching
# =============================================================================

def _compute_intent_match(hexagram_id: int, category: str, action: str, intent_dict: Dict[str, Any]) -> float:
    matched = intent_dict.get("matched_intents", {})
    if not matched:
        return 0.5
    
    category_intent_map = {
        "sovereign": ["create", "speak", "protect", "focus"],
        "transformer": ["transform", "heal", "grow", "release"],
        "dissipator": ["destroy", "conflict", "release", "explore"],
        "boundary": ["understand", "focus", "protect", "connect"],
    }
    action_intent_map = {
        "ASSERT": ["create", "speak", "protect", "focus"],
        "YIELD": ["release", "heal", "connect", "listen"],
        "ADAPT": ["transform", "explore", "grow", "understand"],
        "WAIT": ["understand", "focus", "listen", "release"],
    }
    
    cat_intents = category_intent_map.get(category, [])
    act_intents = action_intent_map.get(action, [])
    cat_score = sum(matched.get(i, 0.0) for i in cat_intents)
    act_score = sum(matched.get(i, 0.0) for i in act_intents)
    return _clamp((cat_score + act_score) / 2.0) if (cat_score + act_score) > 0 else 0.3


# =============================================================================
# Hamiltonian / Gaussian / Trigram math from parsed wiki sources
# =============================================================================


def _hamiltonian_energy(
    resolved_vector: List[float],
    expanded_vector: List[float],
    line_balance: Dict[str, Any],
) -> float:
    """ℋ(p,q,t) = Σ p_i · q̇^i - ℒ

    - p_i     : resolved vector axis as momentum
    - q̇^i    : per-axis phase derivative = resolved[i] - expanded[i]
    - ℒ       : line-state Lagrangian from paired ternary differentials

    Boolean is forbidden in this layer. All state comparisons use signed
    quantitative differentials. Final gating only.
    """
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))

    # Paired ternary differentials — no absolute ratios
    yin_count = float(line_balance.get("yin_count", 0) or 0)
    yang_count = float(line_balance.get("yang_count", 0) or 0)
    yao_count = float(line_balance.get("yao_count", 0) or 0)
    changing_count = float(line_balance.get("changing_count", 0) or 0)
    old_yang_count = float(line_balance.get("old_yang_count", 0) or 0)
    old_yin_count = float(line_balance.get("old_yin_count", 0) or 0)
    old_yao_count = float(line_balance.get("old_yao_count", 0) or 0)
    stable_yao_count = float(line_balance.get("stable_yao_count", 0) or 0)
    stable_yin_count = float(line_balance.get("stable_yin_count", 0) or 0)

    dy = yang_count - yin_count                      # signed binary differential
    yao_dy = yao_count - 3.0                        # yao vs neutral midpoint (6/2)
    changing_dy = changing_count - (6.0 - changing_count)  # changing vs stable
    old_dy = old_yang_count - old_yin_count         # old_yang vs old_yin
    stable_dy = stable_yao_count - stable_yin_count # stable ternary opposition

    lagrangian = (
        abs(dy) * 0.5
        + abs(yao_dy) * 0.3
        + abs(changing_dy) * 0.2
    )
    return _clamp(pq_dot - lagrangian)


def _gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    """f(x) = a * exp(-(x - b)^2 / (2c^2))

    a=1 normalized. c = FWHM / (2*sqrt(2*ln 2)) ≈ FWHM/2.35482.
    Source: Gaussian function wiki parse.
    """
    if fwhm <= 1e-9:
        return 1.0 if value == center else 0.0
    c = fwhm / 2.3548200
    exponent = -((value - center) ** 2) / (2.0 * c * c)
    return math.exp(exponent)


def _quantum_avatar_modulation(
    hexagram_id: int,
    phase_bits: int,
    resolved_vector: List[float],
    expanded_vector: List[float],
    request_text: str = "",
    emotional_input: int = 50,
) -> Dict[str, Any]:
    """Compute quantum wavefunction state for NPC avatar individualization.

    Maps each (hexagram_id, phase_bits) pair to a unique 512-state quantum
    wavefunction that modulates the NPC's 3D kit model: rotation, scale,
    position, color, and animation phase. The wavefunction is derived from
    the Hamiltonian energy, Gaussian kernel across temporal phases, and
    intent-driven perturbation.

    Returns avatar state dict with:
    - wavefunction: complex amplitude (real, imag) per VEC_KEY
    - rotation_modulation: 3-axis rotation deltas
    - scale_factor: overall mesh scale (0.5..2.0)
    - color_shift: RGB perturbation from canonical palette
    - animation_phase: temporal phase [0..1) for interpolation
    - delegate_vector: 5-axis vector indicating NPC's delegation propensity
    """
    phase_info = PHASE_INFO[phase_bits]
    phase_temporal = phase_info["temporal"]

    # Hamiltonian energy drives animation intensity
    hamiltonian = _hamiltonian_energy(resolved_vector, expanded_vector, {})
    hamiltonian_normalized = float(hamiltonian)  # 0..1

    # Gaussian perturbation across temporal phases: center on present phase
    # FWHM=2.5 means phases ~2 away get ~50% modulation
    phase_center = 1.0  # present phase
    temporal_gaussian = _gaussian_kernel(float(phase_bits), phase_center, 2.5)

    # Intent-driven perturbation from request_text
    intent_dict = extract_intent(request_text)
    intent_intensity = float(intent_dict.get("intensity", 0.0))
    slider_factor = _clamp(float(emotional_input) / 100.0)

    # Wavefunction: |psi> = a|canonical> + b|phase> + c|intent>
    # Real/imaginary components for each vector axis
    wavefunction = {}
    for i, key in enumerate(VEC_KEYS):
        rv = float(resolved_vector[i]) if i < len(resolved_vector) else 0.0
        ev = float(expanded_vector[i]) if i < len(expanded_vector) else 0.0

        # Phase drives the imaginary component (temporal dynamics)
        phase_complexity = (phase_bits % 3) + 1  # 1..3
        real_part = rv * temporal_gaussian
        imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)

        wavefunction[key] = {
            "real": round(real_part, 6),
            "imag": round(imag_part, 6),
            "amplitude": round(math.sqrt(real_part**2 + imag_part**2), 6),
        }

    # Rotation modulation: derived from phase_polarity + hamiltonian
    # Each phase produces unique rotation signature
    rotation_x = hamiltonian_normalized * 0.35 * math.sin(phase_bits * 0.785)  # pi/4 step
    rotation_y = hamiltonian_normalized * 0.35 * math.cos(phase_bits * 0.785)
    rotation_z = (float(phase_bits) / 8.0) * slider_factor * 0.2

    # Scale factor: high-energy phases expand, stable phases contract
    scale_base = 1.0
    scale_factor = scale_base + (hamiltonian_normalized - 0.5) * 0.5

    # Color shift: map vector axes to RGB perturbation
    # chaos -> R, darkTone -> G, whimsy -> B (color space of emotional payload)
    chaos = float(resolved_vector[0]) if len(resolved_vector) > 0 else 0.0
    dark_tone = float(resolved_vector[2]) if len(resolved_vector) > 2 else 0.0
    whimsy = float(resolved_vector[1]) if len(resolved_vector) > 1 else 0.0

    color_shift = {
        "r": round(chaos * 255.0 * slider_factor * 0.3, 1),
        "g": round(dark_tone * 255.0 * slider_factor * 0.3, 1),
        "b": round(whimsy * 255.0 * slider_factor * 0.3, 1),
    }

    # Animation phase: cycles through [0..1) based on phase_bits + hamiltonian
    animation_phase = (float(phase_bits) / 8.0 + hamiltonian_normalized * 0.125) % 1.0

    # Delegate vector: which of the 5 axes this NPC is most "agentic" in
    # (high amplitude = strong delegation signal for that domain)
    delegate_vector = {
        k: round(v["amplitude"], 6) for k, v in wavefunction.items()
    }

    # NPC kit identity for 3D mesh selection
    kit_identity = {
        "hexagram_id": hexagram_id,
        "phase_bits": phase_bits,
        "phase_temporal": phase_temporal,
        "phase_polarity": phase_info["polarity"],
        "codename": f"HEX-{hexagram_id:02d}-PHASE-{phase_bits}",
        "animation_speed": round(1.0 + (intent_intensity * 0.5), 3),
    }

    return {
        "wavefunction": wavefunction,
        "rotation_modulation": {
            "x": round(rotation_x, 6),
            "y": round(rotation_y, 6),
            "z": round(rotation_z, 6),
        },
        "scale_factor": round(scale_factor, 4),
        "color_shift": color_shift,
        "animation_phase": round(animation_phase, 6),
        "delegate_vector": delegate_vector,
        "kit_identity": kit_identity,
    }


def _trigram_frequency_weight(upper: str, lower: str) -> float:
    """Domain-agnostic trigram weight derived from frequency/structural context.

    Source: Trigram/Bagua wiki parse.
    Not tied to fixed semantic meanings; only frequency/position weighting.
    """
    weight = 0.5
    if upper:
        weight += sum(ord(ch) for ch in upper) % 97 / 1000.0
    if lower:
        weight += sum(ord(ch) for ch in lower) % 89 / 1000.0
    return _clamp(weight)


# =============================================================================
# Core expansion — yin/yang/yao as PRIMARY trigger
# =============================================================================

def _pool_weights_for_hex(
    hexagram_id: int,
    intent_dict: Dict[str, Any],
    phase_bits: int = 0,
    emotional_input: int = 50,
) -> Tuple[List[float], float, Dict[str, Any]]:
    """Derive pool, porosity, and inject metadata from structure + intent.
    
    PRIMARY trigger: yin/yang/yao line-state balance
    SECONDARY: trigram structural context
    TERTIARY: neighbor continuity + intent match
    """
    hex_data = HEXAGRAM_BASE[hexagram_id]
    upper = hex_data.get("upper_trigram", "")
    lower = hex_data.get("lower_trigram", "")
    binary = hex_data.get("binary_bottom_to_top", "")
    name = hex_data.get("name", "")
    category = hex_data.get("category", "")
    action = hex_data.get("action", "")
    
    # === PRIMARY: line-state balance drives pool/porosity ===
    balance = _line_state_balance(binary, phase_bits)
    line_vec = _line_state_vector(balance)
    
    # === SECONDARY: trigram structural context (upper=outer 60%, lower=inner 40%) ===
    upper_vec = _trigram_vector(upper)
    lower_vec = _trigram_vector(lower)
    trigram_vec = _lerp(lower_vec, upper_vec, 0.6)
    
    # Blend: line states dominate (0.7), trigrams context (0.3)
    expanded = _lerp(line_vec, trigram_vec, 0.3)
    
    # === TERTIARY: neighbor continuity ===
    neighbors = _hex_neighbors(hexagram_id)
    prev_vec = _primary_pool_for_hex(neighbors["previous"])
    next_vec = _primary_pool_for_hex(neighbors["next"])
    neighbor_mix = _lerp(prev_vec, next_vec, 0.5)
    
    # Intent modulates neighbor blend strength
    intent_intensity = float(intent_dict.get("intensity", 0.0))
    yao_ratio = balance["yao_ratio"]
    changing_ratio = balance["changing_ratio"]
    
    # Porosity: canonical base from HEXAGRAM_INJECTION_SITE (hexagram topology)
    # plus phase-derived overdrive (changing/yao lines add bleed).
    # The immutable table defines each hexagram's structural porosity; phases
    # modulate within that topological envelope.
    base_porosity = float(HEXAGRAM_INJECTION_SITE[int(hexagram_id)]["porosity"])
    
    # emotional_input (0..100) modulates phase bleed: higher input amplifies
    # phase-driven porosity changes beyond the canonical base
    slider_factor = _clamp(float(emotional_input) / 100.0)
    phase_overdrive = _clamp(float(phase_bits) / 8.0) * (0.5 + slider_factor * 0.5)  # 0.0 to 0.875
    
    # Final porosity: canonical base + phase overdrive (clamped 0..4)
    porosity_score = _clamp(base_porosity / 4.0 + phase_overdrive * 0.5)
    porosity_index = int(porosity_score * 4.0)
    porosity_index = min(porosity_index, 4)
    porosity_meta = POROSITY_LEVELS[porosity_index]
    porosity_norm = porosity_index / 4.0
    
    # Neighbor bleed through porosity
    bleed = _clamp(porosity_norm * 0.7)
    expanded = _lerp(expanded, neighbor_mix, bleed)
    
    # === INTENT match & vector modulation ===
    intent_vector = intent_dict.get("intent_vector", [0.1, 0.1, 0.1, 0.8, 0.85])
    intent_match = _compute_intent_match(hexagram_id, category, action, intent_dict)
    intent_mod = [intent_match * 0.15, intent_match * 0.15, intent_match * 0.08,
                  intent_match * 0.08, intent_match * 0.12]
    # Blend intent vector seed (15% weight scaled by intensity) and intent match
    expanded = _lerp(expanded, intent_vector, 0.15 * (1.0 + intent_intensity))
    expanded = _lerp(expanded, _lerp(expanded, intent_mod, 0.35), 0.25)
    
    # Final clamp
    expanded = [_clamp(v) for v in expanded]
    
    inject = {
        "primary_pool": HEXAGRAM_INJECTION_SITE[int(hexagram_id)]["primary_pool"],
        "secondary_pool": HEXAGRAM_INJECTION_SITE[int(hexagram_id)]["secondary_pool"],
        "porosity": porosity_index,
        "porosity_norm": porosity_norm,
        "porosity_label": porosity_meta["label"],
        "porosity_window": porosity_meta["window"],
        "porosity_description": porosity_meta["description"],
        "reason": (
            f"{name}: {category} {action} | "
            f"yin={balance['yin_ratio']:.2f} yang={balance['yang_ratio']:.2f} yao={balance['yao_ratio']:.2f} | "
            f"changing={changing_ratio:.2f} intent_match={intent_match:.2f}"
        ),
        "neighbors": neighbors,
        "intent_match": intent_match,
        "line_balance": {
            "yin_count": balance["yin_count"],
            "yang_count": balance["yang_count"],
            "yao_count": balance["yao_count"],
            "changing_count": balance["changing_count"],
            "old_yin_count": balance["old_yin_count"],
            "old_yang_count": balance["old_yang_count"],
            "old_yao_count": balance["old_yao_count"],
            "stable_yin_count": balance["stable_yin_count"],
            "stable_yang_count": balance["stable_yang_count"],
            "stable_yao_count": balance["stable_yao_count"],
            "yin_ratio": balance["yin_ratio"],
            "yang_ratio": balance["yang_ratio"],
            "yao_ratio": balance["yao_ratio"],
            "changing_ratio": changing_ratio,
        },
    }
    
    return expanded, porosity_norm, inject


def _line_state_vector(balance: Dict[str, Any]) -> List[float]:
    """Convert line-state balance to 5-axis vector.
    
    This is the PRIMARY vector derived from yin/yang/yao distribution.
    """
    yin_r = balance["yin_ratio"]
    yang_r = balance["yang_ratio"]
    yao_r = balance["yao_ratio"]
    
    old_yin = balance["old_yin_count"]
    old_yang = balance["old_yang_count"]
    old_yao = balance["old_yao_count"]
    stable_yin = balance["stable_yin_count"]
    stable_yao = balance["stable_yao_count"]
    
    dy = yang_r - yin_r                          # signed ternary differential
    yao_dy = yao_r - 0.5                         # yao vs neutral midpoint
    old_dy = (old_yang / 6.0) - (old_yin / 6.0)  # old_yang vs old_yin differential
    stable_dy = (stable_yao / 6.0) - (stable_yin / 6.0)  # stable ternary opposition
    
    return [
        _clamp(yao_dy * 0.5 + old_dy * 0.3 + abs(dy) * 0.2),    # chaos
        _clamp(yin_r * 0.4 + yao_dy * 0.3 + old_dy * 0.1),      # whimsy
        _clamp((old_yang / 6.0) * 0.15 + (old_yao / 6.0) * 0.2 + dy * 0.1), # darkTone
        _clamp(yang_r * 0.3 - yao_dy * 0.3 - abs(old_dy) * 0.1),  # coherence
        _clamp(yang_r * 0.3 - yao_dy * 0.2 + (old_yang / 6.0) * 0.1),   # voiceWeight
    ]


def derive_dynamic_emotional_input(
    request_text: str = "",
    emotional_input: int | None = None,
    intent_dict: Dict[str, Any] | None = None,
) -> int:
    """Derive dynamic emotional input (1-99) from request text sentiment, intensity, & character entropy.
    Eliminates flat static 50 fallback state.
    """
    if emotional_input is not None and emotional_input != 50 and 0 <= emotional_input <= 100:
        return emotional_input
    
    if not request_text or not request_text.strip():
        return 52  # Dynamic non-flat default baseline

    if intent_dict is None:
        intent_dict = extract_intent(request_text)

    # 1. Text ASCII entropy modulation (1-35 points)
    char_sum = sum(ord(c) for c in request_text)
    entropy_offset = (char_sum % 37) + 1  # 1 to 37

    # 2. Intent intensity scaling (0-25 points)
    intensity = float(intent_dict.get("intensity", 0.5))
    intensity_offset = int(intensity * 25.0)

    # 3. Vector Seed modulation (0-30 points)
    intent_vec = intent_dict.get("intent_vector", [0.1, 0.1, 0.1, 0.8, 0.85])
    vector_offset = int((intent_vec[0] * 15.0) + (intent_vec[1] * 10.0) + (intent_vec[2] * 10.0))

    dynamic_val = 15 + entropy_offset + intensity_offset + vector_offset
    dynamic_val = max(1, min(99, dynamic_val))

    # Guarantee we NEVER resolve to flat 50
    if dynamic_val == 50:
        dynamic_val = 51

    return dynamic_val


def expand_hexagram(
    hexagram_id: int,
    request_text: str = "",
    *,
    phase_bits: int = 0,
    emotional_input: int | None = None,
) -> Dict[str, Any]:
    """Expand a single hexagram with yin/yang/yao as primary trigger.
    
    Expansion layers (in order of influence):
    1. Yin/yang/yao line-state balance → primary vector + porosity
    2. Trigram structural context → secondary weighting
    3. Neighbor continuity → bleed through porosity
    4. Intent match → final modulation
    5. Phase shift → temporal displacement
    """
    intent_dict = extract_intent(request_text)
    resolved_emotional_input = derive_dynamic_emotional_input(request_text, emotional_input, intent_dict)
    expanded_vec, porosity_norm, inject = _pool_weights_for_hex(
        hexagram_id, intent_dict, phase_bits, resolved_emotional_input
    )
    
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
    sampled = [_clamp(expanded_vec[i] + shift[i]) for i in range(5)]
    
    changing_positions = PHASE_LINE_MAP.get(phase_bits, [])
    base_ternary = HEXAGRAM_BASE[hexagram_id]["binary_bottom_to_top"]
    phase_line_states = []
    yin_count = 0
    yang_count = 0
    yao_count = 0
    changing_count = 0
    old_yin_count = 0
    old_yang_count = 0
    old_yao_count = 0
    stable_yin_count = 0
    stable_yang_count = 0
    stable_yao_count = 0
    for idx, bit in enumerate(base_ternary):
        line_pos = idx + 1
        ternary_state = 2 if line_pos in changing_positions else int(bit)
        yao_key = _line_yao_key(ternary_state, temporal)
        if ternary_state == 0:
            yin_count += 1
            if "old" in yao_key:
                old_yin_count += 1
            elif "stable" in yao_key:
                stable_yin_count += 1
        elif ternary_state == 1:
            yang_count += 1
            if "old" in yao_key:
                old_yang_count += 1
            elif "stable" in yao_key:
                stable_yang_count += 1
        else:
            yao_count += 1
            changing_count += 1 if line_pos in changing_positions else 0
            if "old" in yao_key:
                old_yao_count += 1
            elif "stable" in yao_key:
                stable_yao_count += 1
        phase_line_states.append({
            "position": line_pos,
            "ternary_state": ternary_state,
            "yao_key": yao_key,
            "yao_label": _yao_vocabulary_map().get(yao_key, ""),
        })
    yin_ratio = yin_count / max(len(base_ternary), 1)
    yang_ratio = yang_count / max(len(base_ternary), 1)
    yao_ratio = yao_count / max(len(base_ternary), 1)
    changing_ratio = changing_count / max(len(base_ternary), 1)
    
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
        "phase_temporal": temporal,
        "hexagram_symbols": symbols_first,
        "intent": intent_dict,
        "inject_site": inject,
        "yao_vocabulary": _yao_vocabulary_map(),
        "line_states": phase_line_states,
        "line_balance": {
            "yin_count": yin_count,
            "yang_count": yang_count,
            "yao_count": yao_count,
            "changing_count": changing_count,
            "old_yin_count": old_yin_count,
            "old_yang_count": old_yang_count,
            "old_yao_count": old_yao_count,
            "stable_yin_count": stable_yin_count,
            "stable_yang_count": stable_yang_count,
            "stable_yao_count": stable_yao_count,
            "yin_ratio": yin_ratio,
            "yang_ratio": yang_ratio,
            "yao_ratio": yao_ratio,
            "changing_ratio": changing_ratio,
        },
        "sample_paths": [
            {
                "label": "primary",
                "vector": dict(zip(VEC_KEYS, expanded_vec)),
            },
            {
                "label": "phase_shifted",
                "vector": dict(zip(VEC_KEYS, sampled)),
            },
            {
                "label": "neighbor_blend",
                "bleed": porosity_norm * 0.7,
                "vector": dict(zip(VEC_KEYS, expanded_vec)),
            },
        ],
        "expanded_vector": dict(zip(VEC_KEYS, expanded_vec)),
        "resolved_vector": dict(zip(VEC_KEYS, sampled)),
        # Quantum wavefunction modulation for NPC avatar individualization
        "quantum_avatar_state": _quantum_avatar_modulation(
            hexagram_id, phase_bits, sampled, expanded_vec, request_text, resolved_emotional_input
        ),
        # Pre-slider capture fields
        "pre_slider": {
            "structural_vector": dict(zip(VEC_KEYS, expanded_vec)),
            "intent_seed": intent_dict.get("intent_vector", []),
            "porosity_norm": porosity_norm,
            "porosity_label": inject.get("porosity_label"),
            "line_balance": {
                "yin_count": yin_count,
                "yang_count": yang_count,
                "yao_count": yao_count,
                "changing_count": changing_count,
                "old_yin_count": old_yin_count,
                "old_yang_count": old_yang_count,
                "old_yao_count": old_yao_count,
                "stable_yin_count": stable_yin_count,
                "stable_yang_count": stable_yang_count,
                "stable_yao_count": stable_yao_count,
                "yin_ratio": yin_ratio,
                "yang_ratio": yang_ratio,
                "yao_ratio": yao_ratio,
                "changing_ratio": changing_ratio,
            },
            "intent_match": inject.get("intent_match", 0.0),
            "neighbors": inject.get("neighbors", {}),
            "emotional_input": 0,  # pre-slider
        },
    }


def sample_resolve(
    hexagram_id: int,
    *,
    phase_bits: int,
    request_text: str = "",
    emotional_input: int = 50,
) -> Dict[str, Any]:
    """Resolve a hexagram state for a specific phase."""
    base_expansion = expand_hexagram(
        hexagram_id,
        request_text,
        phase_bits=phase_bits,
        emotional_input=emotional_input,
    )
    resolved = base_expansion["resolved_vector"]
    
    return {
        "hexagram_id": hexagram_id,
        "phase_bits": phase_bits,
        "phase_temporal": base_expansion["phase_temporal"],
        "phase_polarity": PHASE_INFO[phase_bits]["polarity"],
        "phase_description": PHASE_INFO[phase_bits]["description"],
        "request_text": request_text,
        "query_tokens": base_expansion["intent"].get("query_tokens", []),
        "hexagram_symbols": base_expansion["hexagram_symbols"],
        "yao_vocabulary": base_expansion["yao_vocabulary"],
        "inject_site": base_expansion["inject_site"],
        "line_states": base_expansion["line_states"],
        "sample_paths": base_expansion["sample_paths"],
        "expanded_vector": base_expansion["expanded_vector"],
        "resolved_vector": resolved,
        "intent": base_expansion["intent"],
        "pre_slider": base_expansion["pre_slider"],
        "quantum_avatar_state": base_expansion["quantum_avatar_state"],
        "emotional_input": emotional_input,
    }


def collapse_full_128(emotional_input: int = 50, request_text: str = "") -> Dict[str, Any]:
    """Full 64-hexagram expansion across all 8 phases.
    
    All hexagrams expand with maximum pooled states derived from
    yin/yang/yao line states, trigram context, neighbor continuity,
    and user intent. Pre-slider capture preserves full expansion.
    """
    expanded = [
        expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=0)
        for h_id in range(1, 65)
    ]
    resolved = [
        sample_resolve(h_id, phase_bits=p, request_text=request_text, emotional_input=emotional_input)
        for h_id in range(1, 65)
        for p in range(8)
    ]
    
    consensus = _compute_consensus_from_resolved(resolved, emotional_input)
    
    expanded_hamiltonian_energy = []
    for item in expanded:
        expanded_vector = item.get("expanded_vector") or {}
        vec = [float(expanded_vector.get(k, 0.0) or 0.0) for k in VEC_KEYS]
        # Pre-slider: resolved == expanded, so q_dot = 0 and energy = -ℒ
        expanded_hamiltonian_energy.append(
            _hamiltonian_energy(vec, vec, item.get("line_balance", {}))
        )

    resolved_hamiltonian_energy = []
    for item in resolved:
        resolved_vector = item.get("resolved_vector") or {}
        expanded_vector = item.get("expanded_vector") or {}
        rv = [float(resolved_vector.get(k, 0.0) or 0.0) for k in VEC_KEYS]
        ev = [float(expanded_vector.get(k, 0.0) or 0.0) for k in VEC_KEYS]
        resolved_hamiltonian_energy.append(
            _hamiltonian_energy(rv, ev, item.get("line_balance", {}))
        )
    
    # Voice ensemble: summary of all 512 resolved states as simultaneous voices
    # across past/present/future expansion. This is the voice field, not the prize.
    temporal_groups = {}
    for item in resolved:
        phase_temporal = str(item.get("phase_temporal", "") or "")
        temporal_groups.setdefault(phase_temporal, []).append(item)

    dominant_voices = {}
    for temporal, group in temporal_groups.items():
        vec_sums = {k: 0.0 for k in VEC_KEYS}
        for item in group:
            rv = item.get("resolved_vector") or {}
            for k in VEC_KEYS:
                vec_sums[k] += float(rv.get(k, 0.0) or 0.0)
        count = len(group)
        if count:
            for k in VEC_KEYS:
                vec_sums[k] /= count
        top_hex = sorted(
            [(item.get("hexagram_id"), item.get("hexagram_symbols", {}).get("name", "")) for item in group],
            key=lambda x: x[0] or 0
        )[:5]
        dominant_voices[temporal] = {
            "count": count,
            "vector": vec_sums,
            "top_hexagrams": [{"hexagram_id": h, "name": n} for h, n in top_hex],
        }

    all_inject_sites = sorted(set(
        (item.get("inject_site") or {}).get("primary_pool", "")
        for item in resolved
        if (item.get("inject_site") or {}).get("primary_pool")
    ))

    voice_ensemble = {
        "total_voices": len(resolved),
        "total_hexagrams": len(set(item.get("hexagram_id") for item in resolved if item.get("hexagram_id"))),
        "temporal_voices": dominant_voices,
        "inject_site_count": len(all_inject_sites),
        "inject_sites": all_inject_sites,
        "yao_vocabulary_coverage": len(set(
            ls.get("yao_key")
            for item in resolved
            for ls in item.get("line_states", [])
            if ls.get("yao_key")
        )),
    }

    return {
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "request_text": request_text,
        "emotional_input": emotional_input,
        "capture_point": "pre_slider",
        "expanded": expanded,
        "resolved": resolved,
        "consensus": consensus,
        "voice_ensemble": voice_ensemble,
        "expanded_hamiltonian_energy": expanded_hamiltonian_energy,
        "avg_expanded_hamiltonian_energy": sum(expanded_hamiltonian_energy) / max(1, len(expanded_hamiltonian_energy)),
        "min_expanded_hamiltonian_energy": min(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
        "max_expanded_hamiltonian_energy": max(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
        "resolved_hamiltonian_energy": resolved_hamiltonian_energy,
        "avg_resolved_hamiltonian_energy": sum(resolved_hamiltonian_energy) / max(1, len(resolved_hamiltonian_energy)),
        "min_resolved_hamiltonian_energy": min(resolved_hamiltonian_energy) if resolved_hamiltonian_energy else 0.0,
        "max_resolved_hamiltonian_energy": max(resolved_hamiltonian_energy) if resolved_hamiltonian_energy else 0.0,
    }


def capture_pre_slider(request_text: str = "") -> Dict[str, Any]:
    """Capture all expansion BEFORE slider modulation.

    Returns:
        dict with metadata plus full 64-hex expansion and 512 resolved states.
    """
    result = collapse_full_128(emotional_input=0, request_text=request_text)
    result["capture_metadata"] = {
        "request_text": request_text,
        "emotional_input": 0,
        "capture_point": "pre_slider",
        "total_expanded": len(result.get("expanded", [])),
        "total_resolved": len(result.get("resolved", [])),
        "consensus_hexagram_id": result.get("consensus", {}).get("consensus_hexagram_id"),
        "consensus_temporal": result.get("consensus", {}).get("consensus_temporal"),
        "yao_primary_trigger": True,
        "source": "local-python",
    }
    return result


# =============================================================================
# Consensus computation
# =============================================================================

def _tau_for_resolved(item: Dict[str, Any], emotional_input: int = 50, hex_variance: float = 0.0) -> float:
    rv = item.get("resolved_vector") or {}
    base = sum(float(rv.get(k, 0.0) or 0.0) for k in VEC_KEYS)
    inject = item.get("inject_site") or {}
    porosity = float(inject.get("porosity_norm", inject.get("porosity", 0.35) or 0.35))
    h_id = item.get("hexagram_id")
    try:
        hex_weight = float(EMOTIONAL_WEIGHTS[str(int(h_id))].get("voiceWeight", 0.5))
    except Exception:
        hex_weight = 0.5
    line_states = item.get("line_states") or []
    yin = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yin"))
    yang = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yang"))
    yao = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yao"))
    balance = (abs(yin - yang) + abs(yang - yao) + abs(yao - yin)) / 6.0
    slider_factor = _clamp(emotional_input / 100.0)
    # State-dependent temperature: amplifies differences only when intra-hex variance exists.
    base_temperature = 1.0
    variance_term = base_temperature * (1.0 + slider_factor * max(hex_variance, 0.0))
    # Emotional input drives tau with stronger gradient: 0.5 (at 0) to 3.0 (at 100)
    emotional_drive = 0.5 + slider_factor * 2.5
    # Reduce base/porosity/balance contribution, amplify emotional_drive + hex_weight
    return (base * 0.15) + (porosity * 0.1) + (balance * 0.05) + variance_term + (hex_weight * 0.15) + (emotional_drive * 0.55)


def _gaussian_weight(x: float, mu: float, sigma: float) -> float:
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def _mode_of_tau(values: List[float]) -> float:
    if not values:
        return 0.0
    bucket = {}
    for v in values:
        key = round(v, 2)
        bucket[key] = bucket.get(key, 0) + 1
    return max(bucket, key=bucket.__getitem__)


def _compute_consensus_from_resolved(
    resolved: List[Dict[str, Any]],
    emotional_input: int,
) -> Dict[str, Any]:
    """Compute true consensus across all 512 resolved states with open-pool surface."""
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
        }

    temporal_counts: Dict[str, int] = {}
    for item in resolved:
        temporal = str(item.get("phase_temporal", "") or "")
        temporal_counts[temporal] = temporal_counts.get(temporal, 0) + 1
    consensus_temporal = max(temporal_counts, key=temporal_counts.__getitem__) if temporal_counts else "present"

    porosities = [float(item.get("inject_site", {}).get("porosity", 0.35) or 0.35) for item in resolved]
    porosity_mean = sum(porosities) / len(porosities)
    porosity_mode = max(set(porosities), key=porosities.count)
    porosity_norms = [float(item.get("inject_site", {}).get("porosity_norm", porosity_mean / 4.0) or porosity_mean / 4.0) for item in resolved]

    # Compute per-hexagram variance before tau assignment
    hex_groups: Dict[int, List[Dict[str, Any]]] = {}
    for item in resolved:
        h_id = int(item.get("hexagram_id") or 0)
        if h_id:
            hex_groups.setdefault(h_id, []).append(item)
    hex_variance_map: Dict[int, float] = {}
    for h_id, group in hex_groups.items():
        vec_means = {k: 0.0 for k in VEC_KEYS}
        for item in group:
            rv = item.get("resolved_vector") or {}
            for k in VEC_KEYS:
                vec_means[k] += float(rv.get(k, 0.0) or 0.0)
        if group:
            for k in VEC_KEYS:
                vec_means[k] /= len(group)
        variance = sum((vec_means[k] - sum(vec_means.values()) / len(vec_means))**2 for k in VEC_KEYS) / max(len(VEC_KEYS), 1)
        hex_variance_map[h_id] = float(variance)

    tau_values: List[float] = [
        _tau_for_resolved(item, emotional_input=emotional_input, hex_variance=hex_variance_map.get(int(item.get("hexagram_id") or 0), 0.0))
        for item in resolved
    ]
    mu = _mode_of_tau(tau_values)
    sigma = max(1e-9, (sum(porosity_norms) / len(porosity_norms)) / 2.0) if porosity_norms else 1e-9

    raw_weights: List[float] = [_gaussian_weight(t, mu, sigma) for t in tau_values]
    weight_sum = sum(raw_weights)
    weights = [w / weight_sum for w in raw_weights] if weight_sum > 1e-12 else raw_weights
    weight_sum = sum(weights)

    vec_keys = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
    vec_sums = {k: 0.0 for k in vec_keys}
    for item, w in zip(resolved, weights):
        rv = item.get("resolved_vector") or {}
        if isinstance(rv, dict):
            for k in vec_keys:
                vec_sums[k] += float(rv.get(k, 0.0) or 0.0) * w
    consensus_vector = {k: (vec_sums[k] / weight_sum if weight_sum else 0.0) for k in vec_keys}

    # Open-pool surface: primary/secondary pool vectors + porosity window + yin/yang/yao balance
    # Build pool vectors from inject_site primary/secondary pools
    primary_pool_vecs = []
    secondary_pool_vecs = []
    for item in resolved:
        inject_site = item.get("inject_site") or {}
        primary_pool = inject_site.get("primary_pool", "")
        secondary_pool = inject_site.get("secondary_pool", "")
        if primary_pool and primary_pool in EMOTIONAL_POOL:
            primary_pool_vecs.append(EMOTIONAL_POOL[primary_pool])
        if secondary_pool and secondary_pool in EMOTIONAL_POOL:
            secondary_pool_vecs.append(EMOTIONAL_POOL[secondary_pool])

    # Average pool vectors
    def avg_vec(vecs):
        if not vecs:
            return [0.1, 0.2, 0.1, 0.85, 0.85]
        n = len(vecs)
        return [sum(v[i] for v in vecs) / n for i in range(5)]

    primary_avg = avg_vec(primary_pool_vecs)
    secondary_avg = avg_vec(secondary_pool_vecs)

    # Porosity window: filter states within emotional range
    porosity_window = 0.35  # base window
    filtered_pool = [
        r for r in resolved
        if abs(r.get("inject_site", {}).get("porosity", 0.5) - (emotional_input / 100.0)) < porosity_window
    ]

    # Yin/yang/yao balance across all states
    yin_count = sum(1 for r in resolved for ls in r.get("line_states", []) if str(ls.get("yao_key", "") or "").endswith("_yin"))
    yang_count = sum(1 for r in resolved for ls in r.get("line_states", []) if str(ls.get("yao_key", "") or "").endswith("_yang"))
    yao_count = sum(1 for r in resolved for ls in r.get("line_states", []) if str(ls.get("yao_key", "") or "").endswith("_yao"))

    # Blend consensus vector with pool vectors (open-pool surface)
    pool_blend = 0.3
    for i, k in enumerate(vec_keys):
        consensus_vector[k] = (
            consensus_vector[k] * (1 - pool_blend)
            + primary_avg[i] * pool_blend * 0.6
            + secondary_avg[i] * pool_blend * 0.4
        )

    hex_scores: Dict[int, float] = {}
    hex_names: Dict[int, str] = {}
    hex_categories: Dict[int, str] = {}
    hex_actions: Dict[int, str] = {}
    emotional_factor = emotional_input / 100.0  # 0.0 to 1.0
    for item, w in zip(resolved, weights):
        h_id = int(item.get("hexagram_id") or 0)
        if not h_id:
            continue
        hex_names[h_id] = str(item.get("hexagram_symbols", {}).get("name", "") or "")
        hex_categories[h_id] = str(item.get("hexagram_symbols", {}).get("category", "") or "")
        hex_actions[h_id] = str(item.get("hexagram_symbols", {}).get("action", "") or "")
        rv = item.get("resolved_vector") or {}
        line_states = item.get("line_states") or []
        yin = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yin"))
        yang = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yang"))
        yao = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yao"))
        yao_ratio = yao / 6.0
        if yao_ratio > 0.4:
            ctx_weights = {"chaos": 0.3, "whimsy": 0.3, "darkTone": 0.2, "coherence": 0.1, "voiceWeight": 0.1}
        else:
            ctx_weights = {"chaos": 0.1, "whimsy": 0.1, "darkTone": 0.2, "coherence": 0.3, "voiceWeight": 0.3}
        vector_score = sum(ctx_weights[k] * float(rv.get(k, 0.0) or 0.0) for k in vec_keys)
        inject_site = item.get("inject_site") or {}
        inject_score = float(inject_site.get("porosity_norm", inject_site.get("porosity", 0.0) or 0.0))
        phase_temporal = str(item.get("phase_temporal", "") or "")
        temporal_alignment = 1.0 if phase_temporal == consensus_temporal else 0.5
        # Add pool alignment score
        primary_pool = inject_site.get("primary_pool", "")
        secondary_pool = inject_site.get("secondary_pool", "")
        pool_alignment = 0.0
        if primary_pool and primary_pool in EMOTIONAL_POOL:
            pool_vec = EMOTIONAL_POOL[primary_pool]
            pool_alignment += sum(float(rv.get(k, 0.0) or 0.0) * pool_vec[i] for i, k in enumerate(vec_keys))
        if secondary_pool and secondary_pool in EMOTIONAL_POOL:
            pool_vec = EMOTIONAL_POOL[secondary_pool]
            pool_alignment += sum(float(rv.get(k, 0.0) or 0.0) * pool_vec[i] for i, k in enumerate(vec_keys)) * 0.5
        # Emotional input directly biases temporal preference: low=wait/past, high=assert/future
        temporal_preference = {
            "past": 1.0 - emotional_factor * 0.8,
            "present": 1.0 - abs(emotional_factor - 0.5) * 0.5,
            "future": emotional_factor * 0.8,
            "transition": emotional_factor * 0.5,
            "resolution": (1.0 - emotional_factor) * 0.3,
            "dissolution": emotional_factor * 0.6,
            "crystallization": emotional_factor * 0.7,
            "void": 0.5,
        }.get(phase_temporal, 0.5)
        temporal_bias = temporal_preference * 0.2
        score = (vector_score * 0.4 + inject_score * 0.15 + temporal_alignment * 0.1 + pool_alignment * 0.1 + temporal_bias * 0.25) * w
        hex_scores[h_id] = hex_scores.get(h_id, 0.0) + score

    if not hex_scores:
        consensus_hexagram_id = None
        consensus_hexagram_name = ""
        consensus_intent = ""
        line_states = []
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
            f"Consensus from {len(resolved)} states: "
            f"hexagram {consensus_hexagram_id} ({consensus_hexagram_name}) "
            f"in {consensus_temporal}, "
            f"voiceWeight={consensus_vector.get('voiceWeight', 0.0):.4f}, "
            f"coherence={consensus_vector.get('coherence', 0.0):.4f}. "
            f"Intent: {consensus_intent}"
        ),
        # Open-pool metadata
        "open_pool_meta": {
            "primary_pool_vector": dict(zip(vec_keys, primary_avg)),
            "secondary_pool_vector": dict(zip(vec_keys, secondary_avg)),
            "filtered_pool_size": len(filtered_pool),
            "yin_count": yin_count,
            "yang_count": yang_count,
            "yao_count": yao_count,
            "porosity_window": porosity_window,
            "pool_blend": pool_blend,
        },
    }


# =============================================================================
# Helper functions
# =============================================================================

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
            line_states.append({"position": pos, "yao_key": "stable_yao", "yao_label": "stable_yao"})
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


def _resolve_intent_from_consensus(
    hexagram_id: int,
    temporal: str,
    category: str,
    action: str,
    vector: Dict[str, float],
) -> str:
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
    if not line_states:
        return "stable_yao"
    
    changing = [ls for ls in line_states if str(ls.get("yao_key", "") or "").startswith("old_")]
    if not changing:
        present = [ls for ls in line_states if "present" in str(ls.get("yao_label", "") or "")]
        if present:
            return str(present[0].get("yao_key", "stable_yao") or "stable_yao")
        return "stable_yao"
    
    def _score(ls: Dict[str, Any]) -> float:
        pos = int(ls.get("position") or 0)
        label = str(ls.get("yao_label") or "")
        pos_score = pos / 6.0
        label_score = 1.0 if "old" in label else 0.5
        return pos_score + label_score
    
    best = max(changing, key=_score)
    return str(best.get("yao_key") or "old_yao")


def _run_slider_checklist(resolved: Dict[str, float], phase_bits: int, temporal: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for item in [
        {"axis": "chaos", "phase_shift": 0.05, "direction": "+present", "expected": "entropy increases at manifest phase"},
        {"axis": "whimsy", "phase_shift": 0.1, "direction": "+future", "expected": "playfulness widens toward potential"},
        {"axis": "darkTone", "phase_shift": 0.05, "direction": "+past", "expected": "shadow deepens in memory"},
        {"axis": "coherence", "phase_shift": 0.05, "direction": "+resolution", "expected": "pattern tightens at settlement"},
        {"axis": "voiceWeight", "phase_shift": 0.05, "direction": "+void", "expected": "speech authority resets at origin"},
        {"axis": "porosity", "phase_shift": 1, "direction": "+transition", "expected": "boundary bleed peaks at threshold"},
    ]:
        axis = item["axis"]
        shift = item["phase_shift"]
        direction = item["direction"]
        expected = item["expected"]
        
        if axis == "porosity":
            lo, hi = (0.0, 0.05) if phase_bits == 0 else (0.05, 1.0)
            results.append({
                "axis": axis, "direction": direction, "expected": expected,
                "status": "in_window" if lo <= resolved.get("chaos", 0.0) <= hi else "out_of_window",
                "window": (lo, hi), "phase_bits": phase_bits,
            })
            continue
        
        allowed_min = max(0.0, resolved.get(axis, 0.0) - shift)
        allowed_max = min(1.0, resolved.get(axis, 0.0) + shift)
        active = (
            (direction.startswith("+past") and temporal == "past") or
            (direction.startswith("+present") and temporal == "present") or
            (direction.startswith("+future") and temporal == "future") or
            (direction.startswith("+resolution") and temporal == "resolution") or
            (direction.startswith("+void") and temporal == "void") or
            ("transition" in direction and temporal == "transition")
        )
        results.append({
            "axis": axis, "direction": direction, "expected": expected,
            "status": "in_window" if active else "idle",
            "allowed_window": (allowed_min, allowed_max),
            "value": resolved.get(axis),
        })
    return results
