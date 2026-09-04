#!/usr/bin/env python3
"""Generate reference files showing full expanded state.

These files serve as the canonical reference for what complete expansion looks like.
Agents should NEVER collapse below 512 (binary) or 729 (ternary).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.full_hexagram_shotgun import shotgun_expand
from kingwen_ternary_tables_complete import HEXAGRAM_BASE


def generate_kingwen_oracle_master():
    """Generate kingwen_oracle_master.json — full 64-hex expanded state."""
    print("Generating kingwen_oracle_master.json...")
    
    result = shotgun_expand(emotional_input=50)
    expanded = result.get('expanded', [])
    
    # Build master reference
    master = {
        "source": "shotgun_expand(emotional_input=50)",
        "total_hexagrams": len(expanded),
        "total_resolved": len(result.get('resolved', [])),
        "hexagrams": {}
    }
    
    for exp in expanded:
        hid = exp.get('hexagram_id')
        master["hexagrams"][str(hid)] = {
            "hexagram_id": hid,
            "name": exp.get('name', ''),
            "unicode": exp.get('unicode', ''),
            "chinese": exp.get('chinese', ''),
            "pinyin": exp.get('pinyin', ''),
            "category": exp.get('category', ''),
            "action": exp.get('action', ''),
            "binary_bottom_to_top": exp.get('binary_bottom_to_top', ''),
            "binary_top_to_bottom": exp.get('binary_top_to_bottom', ''),
            "upper_trigram": exp.get('upper_trigram', ''),
            "lower_trigram": exp.get('lower_trigram', ''),
            "upper_idx": exp.get('upper_idx', 0),
            "lower_idx": exp.get('lower_idx', 0),
            "domain_vector": exp.get('domain_vector', {}),
            "expanded_vector": exp.get('expanded_vector', {}),
            "resolved_vector": exp.get('resolved_vector', {}),
            "inject_site": exp.get('inject_site', {}),
            "ternary_slots": exp.get('ternary_slots', []),
            "personality_subsets": exp.get('personality_subsets', []),
            "line_states": exp.get('line_states', []),
            "line_balance": exp.get('line_balance', {}),
            "sample_paths": exp.get('sample_paths', []),
            "yao_vocabulary": exp.get('yao_vocabulary', {}),
            "training_notes": exp.get('training_notes', ''),
            "coder_specialty": exp.get('coder_specialty', ''),
            "rs3_actionable": exp.get('rs3_actionable', ''),
            "pre_slider": exp.get('pre_slider', {}),
            "projections": exp.get('projections', {}),
            "schauberger_parsing": exp.get('schauberger_parsing', {}),
            "schauberger_metrics": exp.get('schauberger_metrics', {}),
            "quantum_superposition": exp.get('quantum_superposition', {}),
            "hermes_layer": exp.get('hermes_layer', {}),
            "avalokiteshvara_arm": exp.get('avalokiteshvara_arm', {}),
            "jkd_pedagogy_anchor": exp.get('jkd_pedagogy_anchor', {}),
            "table_personality": exp.get('table_personality', {}),
            "hexagram_symbols": exp.get('hexagram_symbols', {}),
            "intent": exp.get('intent', {}),
        }
    
    # Write to file
    output_path = ROOT / "DATASETS" / "kingwen_oracle_master.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    size = output_path.stat().st_size
    print(f"  Written: {output_path} ({size:,} bytes)")
    return size


def generate_kingwen_consultation_record():
    """Generate kingwen_consultation_record.json — full consultation record."""
    print("Generating kingwen_consultation_record.json...")
    
    result = shotgun_expand(emotional_input=50)
    expanded = result.get('expanded', [])
    resolved = result.get('resolved', [])
    
    # Build consultation record
    record = {
        "source": "shotgun_expand(emotional_input=50)",
        "consultation_type": "full_512_state_expansion",
        "timestamp": "2026-09-03T00:00:00Z",
        "total_hexagrams": len(expanded),
        "total_resolved_states": len(resolved),
        "expanded_states": expanded,
        "resolved_states": resolved,
        "personality_consensus": result.get('personality_consensus', {}),
        "hamiltonian_energy": result.get('avg_hamiltonian_energy', 0),
        "shotgun_blast_profile": {
            "total_expanded": len(expanded),
            "total_resolved": len(resolved),
            "ternary_permutations_per_hex": 729,
            "total_ternary_permutations": 46656,
            "active_domained_routes": result.get('active_domained_routes', 0),
            "table_sources": result.get('table_sources', [])
        }
    }
    
    output_path = ROOT / "DATASETS" / "kingwen_consultation_record.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    
    size = output_path.stat().st_size
    print(f"  Written: {output_path} ({size:,} bytes)")
    return size


def generate_jkd_ingestion_binary():
    """Generate jkd_ingestion_binary.jsonl — full JKD ingestion in binary format."""
    print("Generating jkd_ingestion_binary.jsonl...")
    
    result = shotgun_expand(emotional_input=50)
    expanded = result.get('expanded', [])
    
    output_path = ROOT / "DATASETS" / "jkd_ingestion_binary.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for exp in expanded:
            # Create binary-style record with all fields
            record = {
                "hexagram_id": exp.get('hexagram_id'),
                "binary": exp.get('binary_bottom_to_top'),
                "phase_bits": exp.get('phase_bits', 0),
                "phase_temporal": exp.get('phase_temporal', ''),
                "phase_polarity": exp.get('phase_polarity', ''),
                "category": exp.get('category'),
                "action": exp.get('action'),
                "expanded_vector": exp.get('expanded_vector'),
                "resolved_vector": exp.get('resolved_vector'),
                "inject_site": exp.get('inject_site'),
                "ternary_slots": exp.get('ternary_slots'),
                "personality_subsets": exp.get('personality_subsets'),
                "line_states": exp.get('line_states'),
                "line_balance": exp.get('line_balance'),
                "sample_paths": exp.get('sample_paths'),
                "yao_vocabulary": exp.get('yao_vocabulary'),
                "training_notes": exp.get('training_notes'),
                "coder_specialty": exp.get('coder_specialty'),
                "rs3_actionable": exp.get('rs3_actionable'),
                "pre_slider": exp.get('pre_slider'),
                "projections": exp.get('projections'),
                "schauberger_parsing": exp.get('schauberger_parsing'),
                "schauberger_metrics": exp.get('schauberger_metrics'),
                "quantum_superposition": exp.get('quantum_superposition'),
                "hermes_layer": exp.get('hermes_layer'),
                "avalokiteshvara_arm": exp.get('avalokiteshvara_arm'),
                "jkd_pedagogy_anchor": exp.get('jkd_pedagogy_anchor'),
                "table_personality": exp.get('table_personality'),
                "hexagram_symbols": exp.get('hexagram_symbols'),
                "intent": exp.get('intent'),
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    size = output_path.stat().st_size
    lines = sum(1 for _ in open(output_path))
    print(f"  Written: {output_path} ({size:,} bytes, {lines} lines)")
    return size


def main():
    print("=" * 60)
    print("REFERENCE FILE GENERATION")
    print("Full expanded state for agent guidance")
    print("=" * 60)
    print()
    
    total_size = 0
    
    total_size += generate_kingwen_oracle_master()
    total_size += generate_kingwen_consultation_record()
    total_size += generate_jkd_ingestion_binary()
    
    print()
    print("=" * 60)
    print(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    print("All reference files regenerated with full expanded state")
    print("=" * 60)


if __name__ == "__main__":
    main()
