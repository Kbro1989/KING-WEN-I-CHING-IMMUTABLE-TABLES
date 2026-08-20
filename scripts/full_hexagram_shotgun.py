#!/usr/bin/env python3
"""Single-pass shotgun blast: fully unbound hexagram expansion.

Projects off immutable tables only. No table modifications.
Emits ALL 64 hexagrams with full 6-slot ternary trigram positions,
512 resolved states, and 3x+ descriptive pool options in one pass.

Architecture:
  query -> parse -> inject all 64 -> expand ternary positions -> personality subsets -> downstream
"""
from __future__ import annotations

import csv
import json
import math
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
from hexagram_personality import HEXAGRAM_PERSONALITY_MAP, resolve_personality_by_consensus, build_hexagram_personality_map  # noqa: E402

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


import itertools

def _expand_729_ternary_line_permutations(hexagram_id: int, inject: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates all 3^6 = 729 ternary line state permutations for a single hexagram.
    
    Each line position (1..6) has 3 ternary states (0=yin, 1=yang, 2=yao changing).
    3^6 = 729 full line-state permutations per hexagram.
    64 hexagrams x 729 = 46,656 total ternary line permutations.
    """
    permutations = []
    # All 729 ternary tuples of length 6
    for idx, perm in enumerate(itertools.product([0, 1, 2], repeat=6)):
        # Calculate line balance and changing line count for this permutation
        yin_count = sum(1 for s in perm if s == 0)
        yang_count = sum(1 for s in perm if s == 1)
        yao_count = sum(1 for s in perm if s == 2)
        
        permutations.append({
            "permutation_id": idx + 1,
            "hexagram_id": hexagram_id,
            "line_states": list(perm),
            "yin_count": yin_count,
            "yang_count": yang_count,
            "yao_changing_count": yao_count,
            "route_key": f"hex_{hexagram_id:02d}_perm_{idx+1:03d}"
        })
    return permutations

CODER_SPECIALTIES = [
    "Research", "Dev", "HTML", "Robotics", "Game Dev", "Analytics",
    "Blueprinting", "Scribe", "Security Red-Team", "Database/Storage",
    "Async/Networking", "DevOps/CI-CD"
]

RS3_ACTIONABLES = [
    "attack", "interact", "traverse", "harvest", "craft",
    "bank", "equip", "cast", "dialogue", "forensics"
]

NOMINAL_STATES = {
    1: "idle",          # Creative - ready to speak
    2: "stealth",       # Receptive - listening mode
    8: "transit",       # Holding Together - consensus forming
    11: "tr_salt",      # Peace - stable advice
    12: "tr_crit",      # Standstill - high-stakes deliberation
    29: "limp",         # The Abysmal - degraded voice, minimal output
    58: "purge",        # The Joyous - channel reset
    52: "st_crit",      # Keeping Still - critical hold
}

def _compute_schauberger_metrics(h_id: int, chaos: float, whimsy: float, coherence: float) -> Dict[str, Any]:
    """Calculates Viktor Schauberger implosion/vortex resonance metrics."""
    upper = (h_id >> 3) & 0b111
    lower = h_id & 0b111
    vortex_tension = round((upper * lower) / 49.0, 4)
    suction = round(chaos * whimsy * (1.0 - coherence), 4)
    temp_dev = round(abs(chaos * 10.0 - 4.0), 4)
    anomaly_resonance = round(math.exp(-temp_dev), 4)
    dist_to_center = abs(h_id - 32.5)
    egg_resonance = round(math.exp(-dist_to_center / 16.0), 4)
    motion_balance = coherence - chaos
    motion_type = "centripetal" if motion_balance >= 0 else "centrifugal"
    
    return {
        "vortex_tension": vortex_tension,
        "suction_coefficient": suction,
        "temperature_anomaly_dev": temp_dev,
        "anomaly_resonance": anomaly_resonance,
        "egg_resonance": egg_resonance,
        "motion_type": motion_type,
    }

def _build_jspace_projections(h_id: int, vector: Dict[str, float], inject: Dict[str, Any], request_text: str) -> Dict[str, Any]:
    """Projects shotgun expansion state to Voicebox, Megatron, Kimi, 3D Agency, Hermes VHDL, and Schauberger."""
    chaos = float(vector.get("chaos", 0.1))
    whimsy = float(vector.get("whimsy", 0.2))
    dark_tone = float(vector.get("darkTone", 0.1))
    coherence = float(vector.get("coherence", 0.85))
    voice_weight = float(vector.get("voiceWeight", 0.85))
    porosity = float(inject.get("porosity", 0.1))
    porosity_label = str(inject.get("porosity_label", "Crystallized"))
    
    coder_specialty = CODER_SPECIALTIES[(h_id - 1) % len(CODER_SPECIALTIES)]
    rs3_actionable = RS3_ACTIONABLES[(h_id - 1) % len(RS3_ACTIONABLES)]
    
    voice_engine = "qwen"
    if voice_weight > 0.90 and porosity <= 0.20:
        voice_engine = "qwen_custom_voice"
    elif coherence > 0.90:
        voice_engine = "kokoro"
    elif dark_tone > 0.50:
        voice_engine = "chatterbox_turbo"

    schauberger = _compute_schauberger_metrics(h_id, chaos, whimsy, coherence)

    arm_id = ((h_id - 1) % 42) + 1

    return {
        "coder_specialty": coder_specialty,
        "rs3_actionable": rs3_actionable,
        "avalokiteshvara_arm": {
            "arm_id": arm_id,
            "arm_name": f"Avalokiteshvara Arm #{arm_id:02d}",
            "hexagram_mapping": f"hex_{h_id:02d}_arm_{arm_id:02d}"
        },
        "jkd_pedagogy_anchor": {
            "skill_domain": coder_specialty,
            "pedagogy_corpus_anchor": f"jkd_anchor_hex_{h_id:02d}",
            "ingestion_format": "ternary_binary_hybrid"
        },
        "quantum_superposition": {
            "capture_id": f"quantum_superposition_hex_{h_id:02d}",
            "state_fidelity": round(coherence, 4),
            "megatron_target_head": f"head_hex_{h_id:02d}"
        },
        "hermes_layer": {
            "voice_mode": NOMINAL_STATES.get(h_id, "recovery/fault_hold"),
            "transition_valid": h_id in (1, 2, 8, 11, 12, 29, 52, 58),
            "vhdl_constrained": True
        },
        "schauberger_metrics": schauberger,
        "projections": {
            "voicebox": {
                "profile_id": f"kingwen-hex-{h_id:02d}",
                "preset_engine": voice_engine,
                "instruct": f"kingwen_hex={h_id} | chaos={chaos:.3f} | coherence={coherence:.3f} | dark={dark_tone:.3f}",
                "prosody": {"speed": round(1.0 + (whimsy * 0.1), 3), "weight": round(voice_weight, 3)}
            },
            "megatron": {
                "hexagram_id": h_id,
                "porosity_score": round(porosity, 4),
                "porosity_head_label": porosity_label,
                "training_prompt": f"[HEX_{h_id:02d}] {request_text}"
            },
            "kimi": {
                "hexagram_id": h_id,
                "context_window_bias": "expand" if porosity > 0.5 else "strict",
                "multi_doc_anchor": f"kingwen_anchor_hex_{h_id:02d}"
            },
            "agency_3d": {
                "hexagram_id": h_id,
                "rs3_actionable": rs3_actionable,
                "mesh_stability": round(coherence, 3),
                "camera_track_mode": "locked" if coherence > 0.85 else "dynamic_pan",
                "visual_prompt": f"Avatar executing RS3 '{rs3_actionable}' in hexagram {h_id} spatial domain."
            }
        }
    }




def shotgun_expand(request_text: str = "", emotional_input: int | None = None) -> Dict[str, Any]:
    """Single-pass shotgun blast: all 64 hexagrams, full ternary, no early collapse."""
    from emotional_engine import derive_dynamic_emotional_input
    emotional_input = derive_dynamic_emotional_input(request_text, emotional_input)

    # Build personality map here — after all table imports are fully resolved
    # Module-level HEXAGRAM_PERSONALITY_MAP may be empty due to import-order;
    # calling build_hexagram_personality_map() at runtime guarantees HEXAGRAM_BASE is loaded.
    pers_map = build_hexagram_personality_map()

    expanded = []
    for h_id in range(1, 65):
        base = expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=emotional_input)
        inject = base.get("inject_site") or {}
        vector = base.get("expanded_vector") or {}
        slots = _ternary_slot_matrix(h_id, phase_bits=0)
        personality_subsets = []
        for slot in slots:
            personality_subsets.extend(_personality_subsets_for_slot(slot, inject, vector))
        
        jspace = _build_jspace_projections(h_id, vector, inject, request_text)

        ternary_729_permutations = _expand_729_ternary_line_permutations(h_id, inject)

        category = HEXAGRAM_BASE[h_id].get("category", "")
        action = HEXAGRAM_BASE[h_id].get("action", "")
        training_notes = EMOTIONAL_WEIGHTS.get(str(h_id), {}).get("trainingNotes", "")

        expanded.append({
            "hexagram_id": h_id,
            "name": HEXAGRAM_BASE[h_id].get("name"),
            "unicode": HEXAGRAM_BASE[h_id].get("unicode"),
            "upper_trigram": HEXAGRAM_BASE[h_id].get("upper_trigram"),
            "lower_trigram": HEXAGRAM_BASE[h_id].get("lower_trigram"),
            "binary_bottom_to_top": HEXAGRAM_BASE[h_id].get("binary_bottom_to_top"),
            "coder_specialty": jspace["coder_specialty"],
            "rs3_actionable": jspace["rs3_actionable"],
            "category": category,
            "action": action,
            "domain_vector": {
                "chaos": float(vector.get("chaos", 0.0) or 0.0),
                "whimsy": float(vector.get("whimsy", 0.0) or 0.0),
                "darkTone": float(vector.get("darkTone", 0.0) or 0.0),
                "coherence": float(vector.get("coherence", 0.0) or 0.0),
                "voiceWeight": float(vector.get("voiceWeight", 0.0) or 0.0),
            },
            "training_notes": training_notes,
            # Full individual ternary identity — sourced from pers_map (runtime-built from immutable tables)
            # Includes: agent_type, domain, element_subset, category, action, binary, slot_tags (6 ternary positions)
            "table_personality": pers_map.get(h_id, {}),
            "hexagram_symbols": base.get("hexagram_symbols", {}),
            "intent": base.get("intent", {}),
            "phase_bits": base.get("phase_bits", 0),
            "request_text": request_text,
            "avalokiteshvara_arm": jspace["avalokiteshvara_arm"],
            "jkd_pedagogy_anchor": jspace["jkd_pedagogy_anchor"],
            "quantum_superposition": jspace["quantum_superposition"],
            "hermes_layer": jspace["hermes_layer"],
            "schauberger_metrics": jspace["schauberger_metrics"],
            "phase_temporal": base.get("phase_temporal"),


            "inject_site": inject,
            "expanded_vector": vector,
            "resolved_vector": base.get("resolved_vector"),
            "ternary_slots": slots,
            "personality_subsets": personality_subsets,
            "ternary_729_permutations_count": len(ternary_729_permutations),
            "line_states": base.get("line_states"),
            "line_balance": base.get("line_balance"),
            "sample_paths": base.get("sample_paths"),
            "yao_vocabulary": base.get("yao_vocabulary"),
            "pre_slider": base.get("pre_slider"),
            "projections": jspace["projections"],
            "schauberger_parsing": schauberger_parsing_layers(
                h_id,
                phase_bits=0,
                emotional_input=0,
                line_states=base.get("line_states", []),
            ),
            })



    resolved = []
    for h_id in range(1, 65):
        for p in range(8):
            r_base = expand_hexagram(h_id, request_text, phase_bits=p, emotional_input=emotional_input)
            ptags = pers_map.get(h_id, {})
            resolved.append({
                "hexagram_id": h_id,
                "category": HEXAGRAM_BASE[h_id].get("category", ""),
                "action": HEXAGRAM_BASE[h_id].get("action", ""),
                "coder_specialty": CODER_SPECIALTIES[(h_id - 1) % len(CODER_SPECIALTIES)],
                "rs3_actionable": RS3_ACTIONABLES[(h_id - 1) % len(RS3_ACTIONABLES)],
                "training_notes": EMOTIONAL_WEIGHTS.get(str(h_id), {}).get("trainingNotes", ""),
                "hexagram_symbols": HEXAGRAM_BASE[h_id],
                "intent": r_base.get("intent", {}),
                # Full individual identity from immutable table — NOT averaged or blended
                "table_personality": ptags,
                "domain_vector": {k: float(r_base.get("resolved_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS},
                "phase_bits": p,
                "phase_temporal": PHASE_INFO[p]["temporal"],
                "inject_site": r_base.get("inject_site", {}),
                "expanded_vector": r_base.get("expanded_vector", {}),
                "resolved_vector": r_base.get("resolved_vector", {}),
                "line_states": r_base.get("line_states", []),
                "line_balance": r_base.get("line_balance", {}),
            })

    energies = []
    for item in expanded:
        vec = [float(item.get("expanded_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS]
        energies.append(
            _hamiltonian_energy(vec, vec, item.get("line_balance", {}))
        )

    # Compute real consensus vector as mean across all 64 expanded hexagram vectors
    n = max(1, len(expanded))
    consensus_vector = {
        k: round(sum(float(item.get("expanded_vector", {}).get(k, 0.0) or 0.0) for item in expanded) / n, 5)
        for k in VEC_KEYS
    }
    # Dominant intent: majority vote across all 64
    intent_counts: Dict[str, int] = {}
    for item in expanded:
        di = item.get("intent", {}).get("dominant_intent", "understand")
        intent_counts[di] = intent_counts.get(di, 0) + 1
    dominant_intent = max(intent_counts, key=intent_counts.get) if intent_counts else "understand"

    personality_consensus = resolve_personality_by_consensus(resolved, consensus_vector)
    personality_consensus["consensus_vector"] = consensus_vector
    personality_consensus["dominant_intent"] = dominant_intent

    return {
        "source": "kingwen-shotgun-expand",
        "request_text": request_text,
        "emotional_input": emotional_input,
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "ternary_line_permutations_per_hex": 729,
        "total_ternary_line_permutations": len(expanded) * 729,  # 46,656
        "total_domained_routes": 35000,                           # ~35,000 active domained routes
        "capture_point": "first-parse",
        "expanded": expanded,
        "resolved": resolved,
        "personality_map": pers_map,           # runtime-built individual ternary identity map
        "personality_consensus": personality_consensus,
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
            "personality": "HEXAGRAM_PERSONALITY_MAP",
        },
    }



def _write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    """Write a list of flat dicts to CSV, creating parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    payload = shotgun_expand(request_text="shotgun blast", emotional_input=50)
    expanded = payload["expanded"]
    resolved = payload["resolved"]
    personality_consensus = payload.get("personality_consensus", {})
    datasets = ROOT / "DATASETS"

    # ------------------------------------------------------------------
    # CSV 1: expanded_states.csv  — 64 rows, one per hexagram
    # Individuality: every hexagram carries its own identity columns.
    # ------------------------------------------------------------------
    exp_fields = [
        "hexagram_id", "name", "unicode", "binary_bottom_to_top",
        "upper_trigram", "lower_trigram",
        "category", "action",
        # personality from immutable table
        "agent_type", "domain", "element_subset",
        # coder/rs3 tags
        "coder_specialty", "rs3_actionable",
        # schauberger
        "vortex_tension", "suction_coefficient", "motion_type",
        # vectors
        "chaos", "whimsy", "darkTone", "coherence", "voiceWeight",
        # hermes nominal state
        "hermes_voice_mode",
        # intent
        "dominant_intent", "intensity", "query_tokens",
        "training_notes",
    ]
    exp_rows = []
    for e in expanded:
        tp = e.get("table_personality", {})
        dv = e.get("domain_vector", {})
        sc = e.get("schauberger_metrics", {})
        intent = e.get("intent", {})
        hermes = e.get("hermes_layer", {})
        exp_rows.append({
            "hexagram_id": e.get("hexagram_id"),
            "name": e.get("name"),
            "unicode": e.get("unicode"),
            "binary_bottom_to_top": e.get("binary_bottom_to_top"),
            "upper_trigram": e.get("upper_trigram"),
            "lower_trigram": e.get("lower_trigram"),
            "category": e.get("category"),
            "action": e.get("action"),
            "agent_type": tp.get("agent_type", ""),
            "domain": tp.get("domain", ""),
            "element_subset": tp.get("element_subset", ""),
            "coder_specialty": e.get("coder_specialty"),
            "rs3_actionable": e.get("rs3_actionable"),
            "vortex_tension": sc.get("vortex_tension"),
            "suction_coefficient": sc.get("suction_coefficient"),
            "motion_type": sc.get("motion_type"),
            "chaos": dv.get("chaos"),
            "whimsy": dv.get("whimsy"),
            "darkTone": dv.get("darkTone"),
            "coherence": dv.get("coherence"),
            "voiceWeight": dv.get("voiceWeight"),
            "hermes_voice_mode": hermes.get("voice_mode"),
            "dominant_intent": intent.get("dominant_intent"),
            "intensity": intent.get("intensity"),
            "query_tokens": "|".join(intent.get("query_tokens", [])),
            "training_notes": e.get("training_notes"),
        })
    _write_csv(datasets / "expanded_states.csv", exp_rows, exp_fields)

    # ------------------------------------------------------------------
    # CSV 2: resolved_states.csv  — 512 rows, one per (hexagram × phase)
    # Every row carries the full individual identity of its hexagram.
    # ------------------------------------------------------------------
    res_fields = [
        "hexagram_id", "name", "phase_bits", "phase_temporal",
        "category", "action",
        # individual personality
        "agent_type", "domain", "element_subset",
        "coder_specialty", "rs3_actionable",
        # vectors
        "chaos", "whimsy", "darkTone", "coherence", "voiceWeight",
        # expanded (pre-slider)
        "exp_chaos", "exp_whimsy", "exp_darkTone", "exp_coherence", "exp_voiceWeight",
        # hamiltonian (q̇ per axis)
        "qdot_chaos", "qdot_whimsy", "qdot_darkTone", "qdot_coherence", "qdot_voiceWeight",
        # line balance paired differentials
        "dy_yang_yin", "yao_dy", "changing_dy",
        # intent
        "dominant_intent", "intensity", "query_tokens",
        "training_notes",
    ]
    res_rows = []
    for r in resolved:
        tp = r.get("table_personality", {})
        dv = r.get("resolved_vector", {}) or {}
        ev = r.get("expanded_vector", {}) or {}
        lb = r.get("line_balance", {}) or {}
        intent = r.get("intent", {})
        hname = r.get("hexagram_symbols", {}).get("name", "")
        yin_c = float(lb.get("yin_count", 0) or 0)
        yang_c = float(lb.get("yang_count", 0) or 0)
        yao_c = float(lb.get("yao_count", 0) or 0)
        ch_c = float(lb.get("changing_count", 0) or 0)
        res_rows.append({
            "hexagram_id": r.get("hexagram_id"),
            "name": hname,
            "phase_bits": r.get("phase_bits"),
            "phase_temporal": r.get("phase_temporal"),
            "category": r.get("category"),
            "action": r.get("action"),
            "agent_type": tp.get("agent_type", ""),
            "domain": tp.get("domain", ""),
            "element_subset": tp.get("element_subset", ""),
            "coder_specialty": r.get("coder_specialty"),
            "rs3_actionable": r.get("rs3_actionable"),
            "chaos": round(float(dv.get("chaos", 0) or 0), 5),
            "whimsy": round(float(dv.get("whimsy", 0) or 0), 5),
            "darkTone": round(float(dv.get("darkTone", 0) or 0), 5),
            "coherence": round(float(dv.get("coherence", 0) or 0), 5),
            "voiceWeight": round(float(dv.get("voiceWeight", 0) or 0), 5),
            "exp_chaos": round(float(ev.get("chaos", 0) or 0), 5),
            "exp_whimsy": round(float(ev.get("whimsy", 0) or 0), 5),
            "exp_darkTone": round(float(ev.get("darkTone", 0) or 0), 5),
            "exp_coherence": round(float(ev.get("coherence", 0) or 0), 5),
            "exp_voiceWeight": round(float(ev.get("voiceWeight", 0) or 0), 5),
            "qdot_chaos": round(float(dv.get("chaos", 0) or 0) - float(ev.get("chaos", 0) or 0), 5),
            "qdot_whimsy": round(float(dv.get("whimsy", 0) or 0) - float(ev.get("whimsy", 0) or 0), 5),
            "qdot_darkTone": round(float(dv.get("darkTone", 0) or 0) - float(ev.get("darkTone", 0) or 0), 5),
            "qdot_coherence": round(float(dv.get("coherence", 0) or 0) - float(ev.get("coherence", 0) or 0), 5),
            "qdot_voiceWeight": round(float(dv.get("voiceWeight", 0) or 0) - float(ev.get("voiceWeight", 0) or 0), 5),
            # paired differentials per math spec
            "dy_yang_yin": round(yang_c - yin_c, 3),
            "yao_dy": round(yao_c - 3.0, 3),
            "changing_dy": round(ch_c - (6.0 - ch_c), 3),
            "dominant_intent": intent.get("dominant_intent"),
            "intensity": round(float(intent.get("intensity", 0) or 0), 4),
            "query_tokens": "|".join(intent.get("query_tokens", [])),
            "training_notes": r.get("training_notes"),
        })
    _write_csv(datasets / "resolved_states.csv", res_rows, res_fields)

    # ------------------------------------------------------------------
    # CSV 3: personality_map.csv  — 64 rows, pure table-tag identity
    # No synthesis. No blending. Just each hexagram's own character.
    # ------------------------------------------------------------------
    pers_fields = [
        "hexagram_id", "name", "binary",
        "category", "action", "agent_type", "domain",
        "upper_trigram", "lower_trigram", "element_subset",
        "source",
        # slot-level individuality (6 positions)
        "s1_bit", "s1_trigram", "s1_element",
        "s2_bit", "s2_trigram", "s2_element",
        "s3_bit", "s3_trigram", "s3_element",
        "s4_bit", "s4_trigram", "s4_element",
        "s5_bit", "s5_trigram", "s5_element",
        "s6_bit", "s6_trigram", "s6_element",
    ]
    pers_rows = []
    runtime_pers_map = payload.get("personality_map", {})
    for h_id in range(1, 65):
        tp = runtime_pers_map.get(h_id, {})
        slots = tp.get("slot_tags", [])
        row = {
            "hexagram_id": h_id,
            "name": HEXAGRAM_BASE[h_id].get("name"),
            "binary": tp.get("binary", ""),
            "category": tp.get("category", ""),
            "action": tp.get("action", ""),
            "agent_type": tp.get("agent_type", ""),
            "domain": tp.get("domain", ""),
            "upper_trigram": tp.get("upper_trigram", ""),
            "lower_trigram": tp.get("lower_trigram", ""),
            "element_subset": tp.get("element_subset", ""),
            "source": tp.get("source", ""),
        }
        for i, slot in enumerate(slots[:6], 1):
            row[f"s{i}_bit"] = slot.get("bit_value")
            row[f"s{i}_trigram"] = slot.get("trigram_name")
            row[f"s{i}_element"] = slot.get("element_subset")
        pers_rows.append(row)
    _write_csv(datasets / "personality_map.csv", pers_rows, pers_fields)

    # ------------------------------------------------------------------
    # Summary print — show per-hexagram individuality, not aggregate
    # ------------------------------------------------------------------
    print(json.dumps({
        "source": payload.get("source"),
        "total_expanded": payload.get("total_expanded"),
        "total_resolved": payload.get("total_resolved"),
        "avg_hamiltonian_energy": payload.get("avg_hamiltonian_energy"),
        "table_sources": payload.get("table_sources"),
        "personality_consensus": {
            "dominant_agent_type": personality_consensus.get("dominant_agent_type"),
            "dominant_domain": personality_consensus.get("dominant_domain"),
            "agent_distribution": personality_consensus.get("agent_distribution"),
            "domain_distribution": personality_consensus.get("domain_distribution"),
            "source": personality_consensus.get("source"),
        },
        "csv_output": {
            "expanded_states": str(datasets / "expanded_states.csv"),
            "resolved_states": str(datasets / "resolved_states.csv"),
            "personality_map": str(datasets / "personality_map.csv"),
        },
        # Sample: first 3 hexagrams, full individual identity
        "hexagram_samples": [
            {
                "hexagram_id": e.get("hexagram_id"),
                "name": e.get("name"),
                "agent_type": runtime_pers_map.get(e.get("hexagram_id"), {}).get("agent_type"),
                "domain": runtime_pers_map.get(e.get("hexagram_id"), {}).get("domain"),
                "element_subset": runtime_pers_map.get(e.get("hexagram_id"), {}).get("element_subset"),
                "category": e.get("category"),
                "action": e.get("action"),
                "coder_specialty": e.get("coder_specialty"),
                "rs3_actionable": e.get("rs3_actionable"),
                "motion_type": e.get("schauberger_metrics", {}).get("motion_type"),
                "hermes_voice_mode": e.get("hermes_layer", {}).get("voice_mode"),
                "query_tokens": e.get("intent", {}).get("query_tokens", []),
            }
            for e in expanded[:3]
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
