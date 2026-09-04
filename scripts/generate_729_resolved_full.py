#!/usr/bin/env python3
"""Generate 729 resolved states with full ternary expansion and inject pool accumulation.

This creates the 729 ternary permutations per hexagram, each with proper
emotional vectors derived from inject pool expansion passes.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.full_hexagram_shotgun import (
    shotgun_expand, _expand_729_ternary_line_permutations, 
    _ternary_slot_matrix, _personality_subsets_for_slot,
    _build_jspace_projections
)
from kingwen_ternary_tables_complete import (
    HEXAGRAM_BASE, EMOTIONAL_WEIGHTS, HEXAGRAM_INJECTION_SITE,
    EMOTIONAL_POOL, VEC_KEYS
)
from emotional_engine import (
    expand_hexagram, derive_dynamic_emotional_input, extract_intent,
    _hamiltonian_energy, _line_state_vector
)
from hexagram_personality import build_hexagram_personality_map


def compute_ternary_emotional_vector(hex_id: int, slot_values: list, 
                                      base_vector: dict, inject: dict,
                                      pool_vec: dict, secondary_vec: dict,
                                      bleed: float) -> dict:
    """Calculate emotional vector for a specific ternary permutation.
    
    Uses ternary slot values to derive unique emotional state from inject pools.
    """
    # Calculate ternary influence from slot values
    ternary_influence = {k: 0.0 for k in VEC_KEYS}
    
    for i, slot_val in enumerate(slot_values):
        position_weight = 1.0 + (i * 0.1)
        
        if slot_val == 0:  # Yin
            ternary_influence['chaos'] += 0.02 * position_weight
            ternary_influence['darkTone'] += 0.03 * position_weight
            ternary_influence['coherence'] -= 0.01 * position_weight
        elif slot_val == 1:  # Yang
            ternary_influence['coherence'] += 0.03 * position_weight
            ternary_influence['voiceWeight'] += 0.02 * position_weight
            ternary_influence['chaos'] -= 0.01 * position_weight
        else:  # Yao (changing)
            ternary_influence['whimsy'] += 0.04 * position_weight
            ternary_influence['chaos'] += 0.01 * position_weight
            ternary_influence['voiceWeight'] += 0.01 * position_weight
    
    # Combine pool vectors with bleed factor
    combined = {}
    for key in VEC_KEYS:
        primary_val = pool_vec.get(key, 0.1)
        secondary_val = secondary_vec.get(key, 0.1)
        base_val = primary_val * (1.0 - bleed) + secondary_val * bleed
        final_val = base_val + ternary_influence[key]
        combined[key] = round(max(0.0, min(1.0, final_val)), 6)
    
    return combined


def generate_729_resolved():
    """Generate 729 resolved states per hexagram with full ternary expansion.
    
    For each of 64 hexagrams:
    - Generate 729 ternary permutations
    - For each permutation, compute emotional vector from ternary slots + inject pools
    - Compute Hamiltonian energy, quantum state, line states, etc.
    - Return 46,656 total records (64 × 729)
    """
    print("Generating 729 resolved states per hexagram...")
    print("64 hexagrams × 729 permutations = 46,656 total records")
    
    # Build personality map
    pers_map = build_hexagram_personality_map()
    
    all_records = []
    
    for h_id in range(1, 65):
        hex_info = HEXAGRAM_BASE[h_id]
        inject = HEXAGRAM_INJECTION_SITE.get(h_id, {})
        pool_vec = EMOTIONAL_POOL.get(inject.get('primary_pool', 'genesis_spark'), {})
        secondary_vec = EMOTIONAL_POOL.get(inject.get('secondary_pool', 'void_origin'), {})
        
        # Calculate bleed factor from inject site
        porosity = inject.get('porosity', 0.5)
        porosity_window = inject.get('porosity_window', [0.0, 1.0])
        porosity_lo = porosity_window[0] if len(porosity_window) > 0 else 0.0
        porosity_hi = porosity_window[1] if len(porosity_window) > 1 else 1.0
        bleed = porosity_lo + (porosity_hi - porosity_lo) * (porosity / 4.0)
        bleed = max(0.0, min(1.0, bleed))
        
        # Get base hexagram data
        base_vector = EMOTIONAL_WEIGHTS.get(str(h_id), {})
        slots = _ternary_slot_matrix(h_id, phase_bits=0)
        
        # Generate all 729 permutations
        for perm_index in range(729):
            # Decode permutation index into 6 ternary slot values
            slot_values = []
            temp = perm_index
            for _ in range(6):
                slot_values.append(temp % 3)
                temp //= 3
            
            # Compute emotional vector for this permutation
            perm_vector = compute_ternary_emotional_vector(
                h_id, slot_values, base_vector, inject,
                pool_vec, secondary_vec, bleed
            )
            
            # Build line states for this permutation
            line_states = []
            for i, slot_val in enumerate(slot_values):
                yao_key_map = {0: 'young_yin', 1: 'young_yang', 2: 'new_yao'}
                line_states.append({
                    "position": i + 1,
                    "yao_key": yao_key_map.get(slot_val, 'stable_yin'),
                    "yao_label": {0: 'young yin', 1: 'young yang', 2: 'new yao'}.get(slot_val, 'stable yin')
                })
            
            # Calculate line balance for this permutation
            yin_count = sum(1 for v in slot_values if v == 0)
            yang_count = sum(1 for v in slot_values if v == 1)
            yao_count = sum(1 for v in slot_values if v == 2)
            line_balance = {
                "yin_count": yin_count,
                "yang_count": yang_count,
                "yao_count": yao_count,
                "changing_count": yao_count,
                "yin_ratio": yin_count / 6.0,
                "yang_ratio": yang_count / 6.0,
                "yao_ratio": yao_count / 6.0,
                "changing_ratio": yao_count / 6.0,
            }
            
            # Compute Hamiltonian energy for this permutation
            perm_vec_list = [perm_vector.get(k, 0.0) for k in VEC_KEYS]
            hamiltonian = 0.0
            try:
                from emotional_engine import _hamiltonian_energy
                hamiltonian = _hamiltonian_energy(perm_vec_list, perm_vec_list, line_balance)
            except:
                hamiltonian = 0.0
            
            # Build record
            record = {
                "hexagram_id": h_id,
                "hexagram_name": HEXAGRAM_BASE[h_id].get("name", ""),
                "hexagram_unicode": HEXAGRAM_BASE[h_id].get("unicode", ""),
                "binary_bottom_to_top": HEXAGRAM_BASE[h_id].get("binary_bottom_to_top", ""),
                "upper_trigram": HEXAGRAM_BASE[h_id].get("upper_trigram", ""),
                "lower_trigram": HEXAGRAM_BASE[h_id].get("lower_trigram", ""),
                "category": HEXAGRAM_BASE[h_id].get("category", ""),
                "action": HEXAGRAM_BASE[h_id].get("action", ""),
                "permutation_index": perm_index,
                "ternary_slot_values": slot_values,
                "ternary_slots": [
                    {"slot_position": i+1, "base_bit": s["base_bit"], "options": s["options"], "changing": s["changing"]}
                    for i, s in enumerate(_ternary_slot_matrix(h_id, 0))
                ],
                "emotional_vector": perm_vector,
                "line_states": [
                    {"position": i+1, "yao_key": {0: 'young_yin', 1: 'young_yang', 2: 'new_yao'}.get(v, 'stable_yin'), "yao_label": {0: 'young yin', 1: 'young yang', 2: 'new yao'}.get(v, 'stable yin')}
                    for i, v in enumerate(slot_values)
                ],
                "line_balance": {
                    "yin_count": sum(1 for v in slot_values if v == 0),
                    "yang_count": sum(1 for v in slot_values if v == 1),
                    "yao_count": sum(1 for v in slot_values if v == 2),
                    "changing_count": sum(1 for v in slot_values if v == 2),
                },
                "inject_site": inject,
                "hamiltonian_energy": hamiltonian,
                "ternary_permutation": perm_index,
                "hexagram_id": h_id,
            }
            all_records.append(record)
        
        if h_id % 10 == 0:
            print(f"  Completed hexagram {h_id}/64")
    
    return all_records


def main():
    print("=" * 70)
    print("729 RESOLVED STATES GENERATOR")
    print("Full ternary expansion with inject pool accumulation")
    print("=" * 70)
    
    records = generate_729_resolved()
    
    # Write to JSONL
    output_path = ROOT / "DATASETS" / "kingwen_729_resolved_full.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nWriting {len(records):,} records to {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    size = output_path.stat().st_size
    print(f"\n=== COMPLETE ===")
    print(f"Total records: {len(records):,}")
    print(f"File size: {size:,} bytes ({size/1024/1024:.1f} MB)")
    print(f"Output: {output_path}")
    
    # Verify structure
    with open(output_path, 'r') as f:
        first = json.loads(f.readline())
    print(f"\nFirst record keys: {list(first.keys())}")
    print(f"Sample emotional vector: {first.get('emotional_vector', {})}")


if __name__ == "__main__":
    main()