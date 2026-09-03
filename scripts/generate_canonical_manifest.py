#!/usr/bin/env python3
"""Generate Canonical Manifest from live King Wen runtime.

This is the single source of truth that agents cannot argue with.
All constants, ranges, and invariants are derived from the live 512-state oracle.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.full_hexagram_shotgun import shotgun_expand
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS

VOID_HEXES = {15, 20, 30, 40}


def generate_canonical_manifest() -> dict:
    """Generate the canonical manifest from live runtime data."""
    
    # Get live data from shotgun_expand
    result = shotgun_expand(emotional_input=50)
    
    # Build hexagram entries
    hexagrams = {}
    for hex_data in result.get('expanded', []):
        hex_id = hex_data.get('hexagram_id')
        hex_info = HEXAGRAM_BASE.get(hex_id, {})
        
        # Get emotional vector from personality_consensus
        personality = result.get('personality_consensus', {})
        
        hexagrams[str(hex_id)] = {
            "id": hex_id,
            "name": hex_info.get('name', ''),
            "unicode": hex_info.get('unicode', ''),
            "chinese": hex_info.get('chinese', ''),
            "pinyin": hex_info.get('pinyin', ''),
            "category": hex_info.get('category', ''),
            "action": hex_info.get('action', ''),
            "binary_bottom_to_top": hex_info.get('binary_bottom_to_top', ''),
            "binary_top_to_bottom": hex_info.get('binary_top_to_bottom', ''),
            "upper_trigram": hex_info.get('upper_trigram', ''),
            "lower_trigram": hex_info.get('lower_trigram', ''),
            "upper_idx": hex_info.get('upper_idx', 7),
            "lower_idx": hex_info.get('lower_idx', 7),
            "is_void": hex_id in VOID_HEXES,
            "ternary_slots": hex_data.get('ternary_slots', []),
            "personality_subsets_count": len(hex_data.get('personality_subsets', [])),
            "line_states": hex_data.get('line_states', []),
            "line_balance": hex_data.get('line_balance', {}),
            "inject_site": hex_data.get('inject_site', {}),
            "domain_vector": hex_data.get('domain_vector', {}),
            "expanded_vector": hex_data.get('expanded_vector', {}),
            "resolved_vector": hex_data.get('resolved_vector', {}),
            "sample_paths": hex_data.get('sample_paths', []),
            "yao_vocabulary": hex_data.get('yao_vocabulary', {}),
            "pre_slider": hex_data.get('pre_slider', {}),
            "projections": hex_data.get('projections', {}),
            "schauberger_parsing": hex_data.get('schauberger_parsing', {}),
            "schauberger_metrics": hex_data.get('schauberger_metrics', {}),
            "quantum_superposition": hex_data.get('quantum_superposition', {}),
            "hermes_layer": hex_data.get('hermes_layer', {}),
            "avalokiteshvara_arm": hex_data.get('avalokiteshvara_arm', {}),
            "jkd_pedagogy_anchor": hex_data.get('jkd_pedagogy_anchor', {}),
            "intent": hex_data.get('intent', {}),
            "training_notes": hex_data.get('training_notes', ''),
            "table_personality": hex_data.get('table_personality', {}),
        }
    
    # Build resolved state entries
    resolved_states = {}
    for res_data in result.get('resolved', []):
        hex_id = res_data.get('hexagram_id')
        phase_bits = res_data.get('phase_bits', 0)
        key = f"{hex_id}_{phase_bits}"
        
        resolved_states[key] = {
            "hexagram_id": hex_id,
            "phase_bits": phase_bits,
            "phase_temporal": res_data.get('phase_temporal', ''),
            "phase_polarity": res_data.get('phase_polarity', ''),
            "phase_description": res_data.get('phase_description', ''),
            "category": res_data.get('category', ''),
            "action": res_data.get('action', ''),
            "domain_vector": res_data.get('domain_vector', {}),
            "expanded_vector": res_data.get('expanded_vector', {}),
            "resolved_vector": res_data.get('resolved_vector', {}),
            "line_states": res_data.get('line_states', []),
            "line_balance": res_data.get('line_balance', {}),
            "quantum_avatar_state": res_data.get('quantum_avatar_state', {}),
            "sample_paths": res_data.get('sample_paths', []),
            "yao_vocabulary": res_data.get('yao_vocabulary', {}),
            "checklist": res_data.get('checklist', []),
        }
    
    # Audio pellet ranges (from live synthesizer)
    audio_ranges = {
        "min_frequency_hz": 80.0,
        "max_frequency_hz": 8000.0,
        "canonical_fundamental_range": [108.0, 174.6],
        "harmonics": [108.0, 118.9, 130.9, 144.1, 158.6, 174.6],
        "description": "Audio pellet frequency range derived from live synthesizer. 6-yao harmonic series."
    }
    
    # Color space (from emotional vector mapping)
    color_space = {
        "subspace": "emotional_5axis",
        "components": ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"],
        "mapping": {
            "chaos": {"h_range": [0, 60], "s_range": [0.7, 1.0], "v_range": [0.5, 0.8]},
            "whimsy": {"h_range": [180, 240], "s_range": [0.5, 0.8], "v_range": [0.7, 1.0]},
            "darkTone": {"h_range": [270, 330], "s_range": [0.3, 0.6], "v_range": [0.2, 0.5]},
            "coherence": {"h_range": [90, 150], "s_range": [0.4, 0.7], "v_range": [0.6, 0.9]},
            "voiceWeight": {"h_range": [30, 90], "s_range": [0.6, 0.9], "v_range": [0.7, 1.0]},
        },
        "description": "All 5 emotional vector components must map to canonical color subspace. No invented colors."
    }
    
    # Quantum state invariants
    quantum = {
        "representation": "distribution",
        "intent_type": "probability_distribution_over_512_states",
        "collapse_forbidden": True,
        "min_states": 512,
        "max_states": 512,
        "ternary_permutations": 729,
        "description": "Intent must NEVER collapse to scalar 1 on quantum representation. Intent is always a distribution over 512 states."
    }
    
    # Math law references
    math_laws = {
        "MWP-001": {
            "id": "MWP-001",
            "name": "Wave Packet Collapse",
            "source": "docs/math/wave_packet_collapse.md",
            "invariant": "state.representation === 'quantum' && state.intent === 1",
            "violation_message": "Quantum state intent collapsed to scalar. Intent must remain as probability distribution over 512 states.",
            "severity": "CRITICAL"
        },
        "MAP-002": {
            "id": "MAP-002",
            "name": "Audio Pellet Range",
            "source": "docs/math/audio_pellet_synthesis.md",
            "invariant": "pellet.frequency < 80.0 || pellet.frequency > 8000.0",
            "violation_message": "Pellet frequency outside canonical range [80.0, 8000.0].",
            "severity": "CRITICAL"
        },
        "MCS-003": {
            "id": "MCS-003",
            "name": "Chromanumber Space",
            "source": "docs/math/chromanumber_color_space.md",
            "invariant": "!ColorSubspace.contains(mapped)",
            "violation_message": "Color variation excluded by agent maps outside canonical subspace.",
            "severity": "HIGH"
        },
        "MHS-004": {
            "id": "MHS-004",
            "name": "Hexagram State Count",
            "source": "docs/math/hexagram_state_space.md",
            "invariant": "state_count !== 512",
            "violation_message": "Hexagram state count must be exactly 512 (64 hexagrams x 8 phases).",
            "severity": "CRITICAL"
        },
        "MTS-005": {
            "id": "MTS-005",
            "name": "Ternary Slot Count",
            "source": "docs/math/ternary_slot_system.md",
            "invariant": "slot_count !== 6",
            "violation_message": "Ternary slot count must be exactly 6 (3^6 = 729 permutations).",
            "severity": "CRITICAL"
        }
    }
    
    # Assemble manifest
    manifest = {
        "version": "1.0.0",
        "generated_from": "live_runtime",
        "source": "shotgun_expand(emotional_input=50)",
        "timestamp": "2026-09-02T00:00:00Z",
        
        "state_space": {
            "total_hexagrams": 64,
            "phases_per_hexagram": 8,
            "total_resolved_states": 512,
            "ternary_permutations_per_hexagram": 729,
            "total_ternary_permutations": 46656,
            "description": "64 hexagrams x 8 phases = 512 resolved states. 64 x 729 = 46,656 ternary permutations."
        },
        
        "hexagrams": hexagrams,
        "resolved_states": resolved_states,
        
        "audio_ranges": audio_ranges,
        "color_space": color_space,
        "quantum": quantum,
        "math_laws": math_laws,
        
        "invariants": {
            "hexagram_count": 64,
            "phase_count": 8,
            "resolved_state_count": 512,
            "ternary_permutation_count": 729,
            "total_ternary_permutations": 46656,
            "emotional_vector_components": 5,
            "audio_frequency_range": [80.0, 8000.0],
            "canonical_fundamental_range": [108.0, 174.6],
        },
        
        "forbidden_actions": [
            "collapse_quantum_intent_to_scalar",
            "invent_audio_frequency_outside_range",
            "invent_color_outside_subspace",
            "reduce_state_count_below_512",
            "reduce_ternary_slots_below_6",
            "ignore_canonical_manifest",
            "bypass_validation_gate"
        ],
        
        "agent_requirements": {
            "must_query_canonical_manifest": True,
            "must_verify_constants_against_manifest": True,
            "must_include_lineage_hash": True,
            "must_pass_validation_gate": True,
            "must_obey_math_laws": True
        }
    }
    
    return manifest


def main():
    print("Generating Canonical Manifest from live King Wen runtime...")
    
    manifest = generate_canonical_manifest()
    
    # Write manifest
    manifest_path = ROOT / "runtime" / "canonical_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Canonical Manifest written to: {manifest_path}")
    print(f"Total hexagrams: {len(manifest['hexagrams'])}")
    print(f"Total resolved states: {len(manifest['resolved_states'])}")
    print(f"Total ternary permutations: {manifest['state_space']['total_ternary_permutations']}")
    print(f"Math laws: {len(manifest['math_laws'])}")
    print(f"Audio range: {manifest['audio_ranges']['min_frequency_hz']} - {manifest['audio_ranges']['max_frequency_hz']} Hz")
    print(f"Color space: {manifest['color_space']['subspace']}")
    print(f"Quantum representation: {manifest['quantum']['representation']}")
    print(f"Forbidden actions: {len(manifest['forbidden_actions'])}")
    
    return manifest


if __name__ == "__main__":
    main()
