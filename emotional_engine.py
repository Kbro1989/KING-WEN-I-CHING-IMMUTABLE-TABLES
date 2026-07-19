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
        "matched_intents": matched,
        "dominant_intent": dominant,
        "intensity": intensity,
        "word_count": len(words),
        "intent_vector": _intent_to_vector(normalized),
    }


def _intent_to_vector(intent_scores: Dict[str, float]) -> List[float]:
    """Map intent distribution to 5-axis vector seed."""
    base = [0.1, 0.1, 0.1, 0.8, 0.85]
    
    chaos_boost = (
        intent_scores.get("conflict", 0.0) * 0.4 +
        intent_scores.get("destroy", 0.0) * 0.3 +
        intent_scores.get("transform", 0.0) * 0.2
    )
    base[0] = _clamp(base[0] + chaos_boost)
    
    whimsy_boost = (
        intent_scores.get("explore", 0.0) * 0.3 +
        intent_scores.get("feel", 0.0) * 0.3 +
        intent_scores.get("heal", 0.0) * 0.2
    )
    base[1] = _clamp(base[1] + whimsy_boost)
    
    dark_boost = (
        intent_scores.get("destroy", 0.0) * 0.3 +
        intent_scores.get("conflict", 0.0) * 0.25
    )
    base[2] = _clamp(base[2] + dark_boost)
    
    coh_boost = (
        intent_scores.get("understand", 0.0) * 0.15 +
        intent_scores.get("focus", 0.0) * 0.15 +
        intent_scores.get("speak", 0.0) * 0.1
    )
    base[3] = _clamp(base[3] + coh_boost)
    
    vw_boost = (
        intent_scores.get("speak", 0.0) * 0.15 +
        intent_scores.get("protect", 0.0) * 0.1 +
        intent_scores.get("connect", 0.0) * 0.1
    )
    base[4] = _clamp(base[4] + vw_boost)
    
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


def _hamiltonian_energy(resolved_vector: List[float], line_balance: Dict[str, Any], phase_shift: List[float]) -> float:
    """ℋ(p,q,t) = Σ p_i q̇^i - ℒ

    - p_i : resolved vector axes as momentum
    - q̇^i: phase shift rate
    - ℒ   : line-state Lagrangian from yin/yang/yao balance
    """
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    lagrangian = (
        abs(line_balance.get("yin_ratio", 0.0) - line_balance.get("yang_ratio", 0.0)) * 0.5
        + line_balance.get("yao_ratio", 0.0) * 0.3
        + line_balance.get("changing_ratio", 0.0) * 0.2
    )
    pq_dot = sum(m * abs(s) for m, s in zip(momentum, phase_shift))
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
    
    # === SECONDARY: trigram context blends in ===
    upper_vec = _trigram_vector(upper)
    lower_vec = _trigram_vector(lower)
    trigram_vec = _lerp(upper_vec, lower_vec, 0.5)
    
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
    
    # Porosity: driven by yao count, changing lines, intent intensity
    porosity_score = _clamp(
        yao_ratio * 0.6 +          # more yao = more porous
        changing_ratio * 0.3 +     # more changing = more porous
        intent_intensity * 0.3     # stronger intent = more porous
    )
    porosity_index = int(porosity_score * 4.0)
    porosity_index = min(porosity_index, 4)
    porosity_meta = POROSITY_LEVELS[porosity_index]
    porosity_norm = porosity_index / 4.0
    
    # Neighbor bleed through porosity
    bleed = _clamp(porosity_norm * 0.7)
    expanded = _lerp(expanded, neighbor_mix, bleed)
    
    # === INTENT match modulation ===
    intent_match = _compute_intent_match(hexagram_id, category, action, intent_dict)
    intent_mod = [intent_match * 0.15, intent_match * 0.15, intent_match * 0.08,
                  intent_match * 0.08, intent_match * 0.12]
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
    changing_r = balance["changing_ratio"]
    old_yin = balance["old_yin_count"]
    old_yang = balance["old_yang_count"]
    old_yao = balance["old_yao_count"]
    
    # Yin-heavy: softer, more whimsical, less voice weight
    # Yang-heavy: stronger, more coherent, more voice weight
    # Yao-heavy: chaotic, adaptive, changing
    # Old lines: add tension/darkness based on count
    
    old_count = old_yin + old_yang + old_yao
    old_ratio = old_count / 6.0
    
    return [
        _clamp(yao_r * 0.5 + old_ratio * 0.3 + abs(yang_r - yin_r) * 0.2),  # chaos
        _clamp(yin_r * 0.4 + yao_r * 0.3 + old_ratio * 0.1),                # whimsy
        _clamp(old_yang * 0.15 + old_yao * 0.2 + yang_r * 0.1),             # darkTone
        _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.3 - old_ratio * 0.1),      # coherence
        _clamp(yang_r * 0.3 + (1.0 - yao_r) * 0.2 + old_yang * 0.1),       # voiceWeight
    ]


# =============================================================================
# Expansion and resolution
# =============================================================================

def expand_hexagram(
    hexagram_id: int,
    request_text: str = "",
    *,
    phase_bits: int = 0,
    emotional_input: int = 50,
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
    expanded_vec, porosity_norm, inject = _pool_weights_for_hex(
        hexagram_id, intent_dict, phase_bits
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
        "hexagram_symbols": base_expansion["hexagram_symbols"],
        "yao_vocabulary": base_expansion["yao_vocabulary"],
        "inject_site": base_expansion["inject_site"],
        "line_states": base_expansion["line_states"],
        "sample_paths": base_expansion["sample_paths"],
        "expanded_vector": base_expansion["expanded_vector"],
        "resolved_vector": resolved,
        "intent": base_expansion["intent"],
        "pre_slider": base_expansion["pre_slider"],
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
        phase_shift = [0.0, 0.0, 0.0, 0.0, 0.0]
        expanded_vector = item.get("expanded_vector") or {}
        expanded_hamiltonian_energy.append(
            _hamiltonian_energy([float(expanded_vector.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]], item.get("line_balance", {}), phase_shift)
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
        "avg_hamiltonian_energy": sum(expanded_hamiltonian_energy) / max(1, len(expanded_hamiltonian_energy)),
        "min_hamiltonian_energy": min(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
        "max_hamiltonian_energy": max(expanded_hamiltonian_energy) if expanded_hamiltonian_energy else 0.0,
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
