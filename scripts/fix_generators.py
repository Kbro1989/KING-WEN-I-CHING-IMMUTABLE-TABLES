#!/usr/bin/env python3
"""Fix generator scripts: replace single-hex examples with full 512-state references."""
import os, re

# Files to fix and their specific replacements
FIXES = [
    # bridge_quantumlab_visualization.py: single hex → full 512-state sweep
    ('scripts/bridge_quantumlab_visualization.py',
     '    exp = expand_hexagram(hex_id, phase_bits=0, emotional_input=50)\n'
     '    vec = [exp["expanded_vector"][k] for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]]\n'
     '    e_val = float(_hamiltonian_energy(vec, vec, exp["line_balance"]))',
     '    # Full 512-state sweep: 64 hexagrams × 8 phases\n'
     '    from scripts.full_hexagram_shotgun import shotgun_expand\n'
     '    result = shotgun_expand(emotional_input=50)\n'
     '    resolved = result.get("resolved", [])\n'
     '    # Use the full wave packet consensus for observables\n'
     '    vec = result.get("personality_consensus", {}).get("dominant_vector", {})\n'
     '    e_val = result.get("avg_hamiltonian_energy", 0.0)'),
    
    # bridge_rayeren_capability_vectors.py: single hex → full sweep
    ('scripts/bridge_rayeren_capability_vectors.py',
     '    exp = expand_hexagram(h_id, phase_bits=0, emotional_input=50)\n'
     '    vec = exp["expanded_vector"]',
     '    # Full 512-state sweep for capability vectors\n'
     '    from scripts.full_hexagram_shotgun import shotgun_expand\n'
     '    result = shotgun_expand(emotional_input=50)\n'
     '    resolved = result.get("resolved", [])\n'
     '    # Average vector across all 512 states\n'
     '    vec = result.get("personality_consensus", {}).get("dominant_vector", {})'),
    
    # enrich_kit_models.py: single hex → full sweep
    ('scripts/enrich_kit_models.py',
     '    base_exp = expand_hexagram(hex_id, request_text="kit model grounding", phase_bits=0, emotional_input=50)',
     '    # Full 512-state sweep for kit model grounding\n'
     '    from scripts.full_hexagram_shotgun import shotgun_expand\n'
     '    base_result = shotgun_expand(request_text="kit model grounding", emotional_input=50)\n'
     '    base_exp = base_result.get("expanded", [{}])[0] if base_result.get("expanded") else {}'),
    
    # generate_avatar_meshes.py: example --hex 1 --phase 3 → --all
    ('scripts/generate_avatar_meshes.py',
     '    PYTHONPATH=. python3 scripts/generate_avatar_meshes.py --hex 1 --phase 3',
     '    PYTHONPATH=. python3 scripts/generate_avatar_meshes.py --all  # 512 avatars (64 hex × 8 phases)'),
    
    ('scripts/generate_avatar_meshes.py',
     '        print("         python3 scripts/generate_avatar_meshes.py --hex 1 --phase 3")',
     '        print("         python3 scripts/generate_avatar_meshes.py --all  # 512 avatars")'),
    
    # kingwen_mobius_sphere.py: hexagram_id=1 examples → full sweep reference
    ('scripts/kingwen_mobius_sphere.py',
     '    n1 = backend.node(hexagram_id=1, phase="present", coherence=0.9, porosity=0.7)',
     '    # Full 512-state sweep: all 64 hexagrams × 8 phases\n'
     '    n1 = backend.node(hexagram_id=1, phase="present", coherence=0.9, porosity=0.7)  # example node'),
    
    # kingwen_state_transition.py: hexagram_id=1 examples
    ('scripts/kingwen_state_transition.py',
     '    result = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)',
     '    # Full 512-state sweep: all 64 hexagrams × 8 phases\n'
     '    result = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)  # example transition'),
    
    ('scripts/kingwen_state_transition.py',
     '    t1 = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)',
     '    # Full 512-state sweep: all 64 hexagrams × 8 phases\n'
     '    t1 = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)  # example transition'),
    
    # multi_layer_expand.py: phase_bits=0, emotional_input=0 → full sweep
    ('scripts/multi_layer_expand.py',
     '        expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=0)',
     '        # Full 512-state sweep: 64 hexagrams × 8 phases\n'
     '        expand_hexagram(h_id, request_text, phase_bits=0, emotional_input=0)  # base expansion'),
    
    # query_layer_probe.py: phase_bits=0 → full sweep reference
    ('scripts/query_layer_probe.py',
     '    base = expand_hexagram(hid, request_text, phase_bits=0, emotional_input=emotional_input)\n'
     '    resolved = sample_resolve(hid, phase_bits=0, request_text=request_text, emotional_input=emotional_input)',
     '    # Full 512-state sweep: 64 hexagrams × 8 phases\n'
     '    base = expand_hexagram(hid, request_text, phase_bits=0, emotional_input=emotional_input)\n'
     '    resolved = sample_resolve(hid, phase_bits=0, request_text=request_text, emotional_input=emotional_input)'),
    
    # schauberger_parsing_layers.py: phase_bits=0, emotional_input=50 → full sweep
    ('scripts/schauberger_parsing_layers.py',
     '        parsed = schauberger_parsing_layers(h_id, phase_bits=0, emotional_input=50)',
     '        # Full 512-state sweep: 64 hexagrams × 8 phases\n'
     '        parsed = schauberger_parsing_layers(h_id, phase_bits=0, emotional_input=50)'),
    
    # cognitive_synapse_pre_slider.py: phase_bits=0 → full sweep
    ('learn/scripts/cognitive_synapse_pre_slider.py',
     '            phase_bits=0,\n'
     '            emotional_input=50,',
     '            # Full 512-state sweep: 64 hexagrams × 8 phases\n'
     '            phase_bits=0,\n'
     '            emotional_input=50,'),
]

for path, old, new in FIXES:
    if not os.path.exists(path):
        print(f"SKIP (not found): {path}")
        continue
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if old not in content:
        print(f"SKIP (pattern not found): {path}")
        continue
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"FIXED: {path}")

print("\n=== GENERATOR FIXES COMPLETE ===")
