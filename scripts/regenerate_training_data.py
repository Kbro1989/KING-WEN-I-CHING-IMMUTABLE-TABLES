#!/usr/bin/env python3
"""Regenerate training data from current shotgun_expand() output.

The existing full_shotgun_expansion_all.jsonl is stale - missing ternary_slots
and ternary_729_permutations_count. This script regenerates all training data
from the current live engine output.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.full_hexagram_shotgun import shotgun_expand


def regenerate_full_shotgun_jsonl():
    """Regenerate full_shotgun_expansion_all.jsonl from current engine."""
    print("Regenerating full_shotgun_expansion_all.jsonl...")
    
    # Get live engine output for multiple emotional_input values
    all_records = []
    
    for emotional_input in [0, 25, 50, 75, 100]:
        result = shotgun_expand(emotional_input=emotional_input)
        
        for expanded in result.get('expanded', []):
            record = {
                "emotional_input": emotional_input,
                "source": "kingwen-shotgun-expand",
                **expanded
            }
            all_records.append(record)
        
        for resolved in result.get('resolved', []):
            record = {
                "emotional_input": emotional_input,
                "source": "kingwen-shotgun-expand",
                **resolved
            }
            all_records.append(record)
    
    # Write to file
    output_path = ROOT / "kingwen_train_data" / "full_shotgun_expansion_all.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"  Wrote {len(all_records)} records to {output_path}")
    return len(all_records)


def regenerate_kingwen_pretrain_jsonl():
    """Regenerate kingwen_pretrain.jsonl from current engine."""
    print("Regenerating kingwen_pretrain.jsonl...")
    
    result = shotgun_expand(emotional_input=50)
    
    records = []
    for expanded in result.get('expanded', []):
        hex_id = expanded.get('hexagram_id')
        hex_info = HEXAGRAM_BASE.get(hex_id, {})
        
        record = {
            "domain": hex_info.get('category', 'sovereign'),
            "source": "kingwen-shotgun-expand",
            "hexagram_id": hex_id,
            "name": hex_info.get('name', ''),
            "category": hex_info.get('category', ''),
            "action": hex_info.get('action', ''),
            "text": expanded.get('training_notes', ''),
            "math": {
                "domain_vector": expanded.get('domain_vector', {}),
                "expanded_vector": expanded.get('expanded_vector', {}),
                "resolved_vector": expanded.get('resolved_vector', {}),
                "line_balance": expanded.get('line_balance', {}),
            },
            "emotional_weights": expanded.get('expanded_vector', {}),
            "porosity": expanded.get('inject_site', {}).get('porosity', 0.5),
            "ternary_slots": expanded.get('ternary_slots', []),
            "personality_subsets": expanded.get('personality_subsets', []),
            "ternary_729_permutations_count": expanded.get('ternary_729_permutations_count', 729),
        }
        records.append(record)
    
    output_path = ROOT / "kingwen_train_data" / "kingwen_pretrain.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"  Wrote {len(records)} records to {output_path}")
    return len(records)


def main():
    print("=" * 60)
    print("TRAINING DATA REGENERATION")
    print("=" * 60)
    
    # Import here to avoid circular imports
    global HEXAGRAM_BASE
    from kingwen_ternary_tables_complete import HEXAGRAM_BASE
    
    count1 = regenerate_full_shotgun_jsonl()
    count2 = regenerate_kingwen_pretrain_jsonl()
    
    print()
    print("=" * 60)
    print("REGENERATION COMPLETE")
    print("=" * 60)
    print(f"full_shotgun_expansion_all.jsonl: {count1} records")
    print(f"kingwen_pretrain.jsonl: {count2} records")
    print("All training data now matches current engine output")


if __name__ == "__main__":
    main()
