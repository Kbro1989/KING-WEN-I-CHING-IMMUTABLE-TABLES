#!/usr/bin/env python3
"""Schauberger implosion mechanics mapped to King Wen parsing layers.

Sources:
- archive.org: Implosion by Viktor Schauberger
- archive.org: Hidden Nature - The Startling Insights of Viktor Schauberger

Extracted mechanics:
1. Centripetal/centrifugal motion types
2. Vortex/spiral tension from trigram pair interaction
3. Temperature gradient and anomaly point
4. Bipolarity/dipolarity as force balance
5. Biological vacuum / suction coefficient
6. Egg-form resonance across 64-hexagram set

All projection is off immutable tables only. No table modifications.
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
    HEXAGRAM_INJECTION_SITE,
    EMOTIONAL_WEIGHTS,
    VOICEBOX_VOICE_POOL,
    YAO_VOCABULARY,
)
from emotional_engine import (  # noqa: E402
    VEC_KEYS,
    _clamp,
    _hamiltonian_energy,
    _yao_vocabulary_map,
)

# =============================================================================
# SCHAUBERGER MECHANICS AS TERMS
# =============================================================================

# 1. Motion type: centripetal = constructive/convergent, centrifugal = destructive/divergent
# 2. Vortex tension: spiral interaction between upper/lower trigram
# 3. Temperature gradient: distance from anomaly point (+4C for water = optimal resonance)
# 4. Dipolarity balance: attraction/repulsion between poles creates movement
# 5. Biological vacuum: suction coefficient from porosity
# 6. Egg-form resonance: center-weighted topology across 64-hexagram set

ANOMALY_POINT = 4.0  # Schauberger's water anomaly point as normalized resonance target


def _motion_type_coefficient(hexagram_id: int, phase_bits: int = 0) -> Dict[str, float]:
    """Layer 1: centripetal/centrifugal motion as trigram-position-level dipole.

    Upper trigram = outward/downward vector
    Lower trigram = inward/upward vector
    Interaction = net motion type coefficient.
    """
    upper = HEXAGRAM_BASE[hexagram_id].get("upper_trigram", "")
    lower = HEXAGRAM_BASE[hexagram_id].get("lower_trigram", "")
    binary = HEXAGRAM_BASE[hexagram_id].get("binary_bottom_to_top", "")

    # Trigrams as dipole vectors: solid lines attract, broken lines repel
    # Simplified from Schauberger's dipolarity observation
    upper_attract = sum(1 for ch in upper if ch in ("☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷") and ch in ("☰", "☳", "☵", "☶"))
    upper_repel = len(upper) - upper_attract
    lower_attract = sum(1 for ch in lower if ch in ("☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷") and ch in ("☰", "☳", "☵", "☶"))
    lower_repel = len(lower) - lower_attract

    # Net dipole: positive = centripetal/constructive, negative = centrifugal/destructive
    net_dipole = (upper_attract - upper_repel) + (lower_attract - lower_repel) * -1
    centripetal = _clamp((net_dipole + 4.0) / 8.0)  # normalize to 0..1
    centrifugal = 1.0 - centripetal

    return {
        "centripetal": centripetal,
        "centrifugal": centrifugal,
        "net_dipole": net_dipole,
        "motion_type": "centripetal" if centripetal > 0.5 else "centrifugal",
    }


def _vortex_tension(hexagram_id: int, emotional_input: int = 50) -> Dict[str, Any]:
    """Layer 2: spiral/vortex tension from trigram pair interaction.

    Schauberger: vortex is the basic law of the universe, present from
    inter-stellar nebulae to the atom itself. Here: spiral tension between
    upper and lower trigram as rotational vector.
    """
    upper = HEXAGRAM_BASE[hexagram_id].get("upper_trigram", "")
    lower = HEXAGRAM_BASE[hexagram_id].get("lower_trigram", "")
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id, {})
    porosity = float(inject.get("porosity", 0.35) or 0.35)

    # Spiral tension: difference in "spin" between trigrams creates rotational energy
    # Simplified: trigram length + character sum difference = angular momentum proxy
    upper_spin = sum(ord(ch) for ch in upper) % 360
    lower_spin = sum(ord(ch) for ch in lower) % 360
    angular_momentum = abs(upper_spin - lower_spin) / 360.0

    # Vortex strength grows with porosity and emotional_input
    vortex_strength = _clamp(angular_momentum * (0.5 + porosity * 0.5) * (0.5 + emotional_input / 200.0))

    # Direction: clockwise = centripetal, counterclockwise = centrifugal
    direction = "clockwise" if upper_spin > lower_spin else "counterclockwise"

    return {
        "upper_spin": upper_spin,
        "lower_spin": lower_spin,
        "angular_momentum": angular_momentum,
        "vortex_strength": vortex_strength,
        "direction": direction,
        "spiral_tension": vortex_strength * (1.0 if direction == "clockwise" else -1.0),
    }


def _temperature_gradient(hexagram_id: int, emotional_input: int = 50) -> Dict[str, float]:
    """Layer 3: temperature gradient and distance from anomaly point.

    Schauberger: implosion creates temperature drop toward anomaly point (+4C).
    Explosion creates temperature rise away from anomaly.
    Here: emotional_input modulates temperature; anomaly point is optimal resonance.
    """
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id, {})
    porosity = float(inject.get("porosity", 0.35) or 0.35)
    weights = EMOTIONAL_WEIGHTS.get(str(hexagram_id), {})

    # Base temperature from inject site porosity + emotional_input
    # Low porosity + low emotional_input = near anomaly point
    # High porosity + high emotional_input = high temperature/friction
    base_temp = porosity * 100.0 + emotional_input * 0.5
    distance_from_anomaly = abs(base_temp - ANOMALY_POINT) / 100.0

    # Resonance is highest near anomaly point, drops off with distance
    resonance = math.exp(-(distance_from_anomaly ** 2) / (2.0 * 0.3 ** 2))

    # Cooling/heating tendency from emotional weights
    cooling = float(weights.get("coherence", 0.5)) * 0.5
    heating = float(weights.get("chaos", 0.5)) * 0.5

    return {
        "base_temperature": base_temp,
        "anomaly_point": ANOMALY_POINT,
        "distance_from_anomaly": distance_from_anomaly,
        "resonance": _clamp(resonance),
        "cooling_tendency": _clamp(cooling),
        "heating_tendency": _clamp(heating),
        "gradient_direction": "cooling" if cooling > heating else "heating",
    }


def _bipolarity_balance(hexagram_id: int, line_states: List[Dict[str, Any]]) -> Dict[str, float]:
    """Layer 4: dipolarity as attraction/repulsion balance.

    Schauberger: opposites are essential to nature; attraction + repulsion = movement.
    Here: yin/yang/yao line balance as bipolar force.
    """
    yin = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yin"))
    yang = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yang"))
    yao = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").endswith("_yao"))

    # Attraction = yin-yang pairs, Repulsion = yao disruptors
    attraction = min(yin, yang) * 2.0
    repulsion = yao * 1.5
    total = max(attraction + repulsion, 1.0)

    return {
        "yin_count": yin,
        "yang_count": yang,
        "yao_count": yao,
        "attraction": attraction / total,
        "repulsion": repulsion / total,
        "bipolarity_index": _clamp((attraction - repulsion) / total),
        "movement_potential": _clamp((attraction + repulsion) / 6.0),
    }


def _biological_vacuum(hexagram_id: int, porosity_norm: float) -> Dict[str, float]:
    """Layer 5: suction coefficient / biological vacuum.

    Schauberger: implosion creates biological vacuum; suction augments itself.
    Here: porosity as suction coefficient; higher porosity = stronger vacuum effect.
    """
    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id, {})
    porosity = float(inject.get("porosity", 0.35) or 0.35)

    # Suction coefficient grows non-linearly with porosity
    suction = _clamp(porosity ** 1.5)
    vacuum_pressure = -suction * 0.8  # negative pressure = biological vacuum

    # Augmentation: higher porosity creates self-reinforcing suction
    augmentation = _clamp(suction * 0.3)

    return {
        "suction_coefficient": suction,
        "vacuum_pressure": vacuum_pressure,
        "augmentation": augmentation,
        "biological_vacuum": _clamp(suction + augmentation),
    }


def _egg_form_resonance(hexagram_id: int) -> Dict[str, float]:
    """Layer 6: egg-form resonance across 64-hexagram set.

    Schauberger: egg-shaped bodies generate vortices optimally.
    Here: center hexagrams have different resonance than edge hexagrams.
    Center = 33,34; edge = 1,64.
    """
    center_distance = abs(hexagram_id - 33.5) / 33.5  # 0 at center, 1 at edges
    # Egg-form weighting: center hexagrams resonate more strongly
    egg_form = _clamp(1.0 - center_distance * 0.6)

    # Downstream weighting for consensus
    return {
        "hexagram_id": hexagram_id,
        "center_distance": center_distance,
        "egg_form_resonance": egg_form,
        "edge_factor": 1.0 - egg_form,
    }


def schauberger_parsing_layers(hexagram_id: int, phase_bits: int = 0, emotional_input: int = 50, line_states: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Apply all 6 Schauberger mechanics as parsing layers projecting off immutable tables."""
    if line_states is None:
        base = HEXAGRAM_BASE[hexagram_id]
        binary = base.get("binary_bottom_to_top", "")
        changing = [2] * 6  # placeholder changing positions
        line_states = []
        for pos in range(1, 7):
            bit = int(binary[pos - 1]) if pos <= len(binary) else 0
            yao_key = "old_yang" if bit == 1 else "old_yin"
            line_states.append({"position": pos, "yao_key": yao_key})

    inject = HEXAGRAM_INJECTION_SITE.get(hexagram_id, {})
    porosity_norm = float(inject.get("porosity", 0.35) or 0.35) / 4.0

    motion = _motion_type_coefficient(hexagram_id, phase_bits)
    vortex = _vortex_tension(hexagram_id, emotional_input)
    temp_grad = _temperature_gradient(hexagram_id, emotional_input)
    bipolar = _bipolarity_balance(hexagram_id, line_states)
    vacuum = _biological_vacuum(hexagram_id, porosity_norm)
    egg = _egg_form_resonance(hexagram_id)

    # Composite Schauberger vector projected into 5-axis space
    composite = [
        _clamp(motion["centrifugal"] * 0.3 + vortex["vortex_strength"] * 0.3 + bipolar["repulsion"] * 0.2),  # chaos
        _clamp(motion["centripetal"] * 0.2 + vortex["vortex_strength"] * 0.2 + bipolar["movement_potential"] * 0.3),  # whimsy
        _clamp(vacuum["biological_vacuum"] * 0.4 + bipolar["repulsion"] * 0.3),  # darkTone
        _clamp(temp_grad["resonance"] * 0.5 + motion["centripetal"] * 0.3 + bipolar["attraction"] * 0.2),  # coherence
        _clamp(egg["egg_form_resonance"] * 0.4 + vortex["spiral_tension"] * 0.3 + temp_grad["resonance"] * 0.3),  # voiceWeight
    ]

    return {
        "hexagram_id": hexagram_id,
        "phase_bits": phase_bits,
        "emotional_input": emotional_input,
        "motion": motion,
        "vortex": vortex,
        "temperature_gradient": temp_grad,
        "bipolarity": bipolar,
        "biological_vacuum": vacuum,
        "egg_form": egg,
        "schauberger_vector": dict(zip(["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"], composite)),
        "table_sources": ["HEXAGRAM_BASE", "HEXAGRAM_INJECTION_SITE", "EMOTIONAL_WEIGHTS", "YAO_VOCABULARY", "VOICEBOX_VOICE_POOL"],
    }


def main() -> int:
    samples = [1, 2, 8, 23, 33, 34, 64]
    results = []
    for h_id in samples:
        parsed = schauberger_parsing_layers(h_id, phase_bits=0, emotional_input=50)
        results.append({
            "hexagram_id": h_id,
            "name": HEXAGRAM_BASE[h_id].get("name"),
            "motion": parsed["motion"],
            "vortex_strength": parsed["vortex"]["vortex_strength"],
            "resonance": parsed["temperature_gradient"]["resonance"],
            "biological_vacuum": parsed["biological_vacuum"]["biological_vacuum"],
            "egg_form_resonance": parsed["egg_form"]["egg_form_resonance"],
            "schauberger_vector": parsed["schauberger_vector"],
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
