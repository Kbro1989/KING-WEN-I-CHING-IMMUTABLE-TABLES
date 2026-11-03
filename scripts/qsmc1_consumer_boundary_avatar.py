#!/usr/bin/env python3
"""Consumer-Boundary Audit: Avatar-Path Hamiltonian Reproduction.

Tests whether _hamiltonian_energy() with empty line_balance ({}) produces
different results than with populated line_balance, across all 1,536 states.

This is a RUNTIME BOUNDARY REPRODUCTION, not a formula correction.
No production formulas are modified.
"""

import json, sys
from collections import Counter
import numpy as np

sys.path.insert(0, '.')
from emotional_engine import _hamiltonian_energy, _clamp

states = []
with open('kingwen_train_data/full_shotgun_expansion_all.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        states.append(rec['label_payload'])

print(f"Loaded {len(states)} states")

# Test 1: populated line_balance (M3 diagnostic path)
populated_h = []
empty_h = []
for s in states:
    rv = s['resolved_vector']
    ev = s['expanded_vector']
    lb = s['line_balance']
    rl = [rv['chaos'], rv['whimsy'], rv['darkTone'], rv['coherence'], rv['voiceWeight']]
    el = [ev['chaos'], ev['whimsy'], ev['darkTone'], ev['coherence'], ev['voiceWeight']]
    h_pop = _hamiltonian_energy(rl, el, lb)
    h_empty = _hamiltonian_energy(rl, el, {})
    populated_h.append(h_pop)
    empty_h.append(h_empty)

print("\n--- Avatar-Path Reproduction ---")
print(f"  Populated (M3 path): H=0.0 for {sum(1 for h in populated_h if h==0.0)}/{len(populated_h)} states")
print(f"  Empty (avatar path): H=0.0 for {sum(1 for h in empty_h if h==0.0)}/{len(empty_h)} states")
print(f"  Populated H range: [{min(populated_h):.6f}, {max(populated_h):.6f}]")
print(f"  Empty H range: [{min(empty_h):.6f}, {max(empty_h):.6f}]")
print(f"  States where populated != empty: {sum(1 for p, e in zip(populated_h, empty_h) if p != e)}")

# Test imaginary amplitude for both paths
print("\n--- Imaginary Amplitude Comparison ---")
imag_pop = 0
imag_empty = 0
for s in states:
    rv = s['resolved_vector']
    ev = s['expanded_vector']
    lb = s['line_balance']
    rl = [rv['chaos'], rv['whimsy'], rv['darkTone'], rv['coherence'], rv['voiceWeight']]
    el = [ev['chaos'], ev['whimsy'], ev['darkTone'], ev['coherence'], ev['voiceWeight']]
    h_pop = _hamiltonian_energy(rl, el, lb)
    h_empty = _hamiltonian_energy(rl, el, {})
    # imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)
    for i in range(5):
        phase_complexity = (s['phase_bits'] % 3) + 1
        imag_pop_val = (rl[i] - el[i]) * (h_pop * phase_complexity * 0.1)
        imag_empty_val = (rl[i] - el[i]) * (h_empty * phase_complexity * 0.1)
        if imag_pop_val != 0:
            imag_pop += 1
        if imag_empty_val != 0:
            imag_empty += 1

print(f"  Populated path: {imag_pop} nonzero imag components")
print(f"  Empty path: {imag_empty} nonzero imag components")

# Save results
results = {
    'populated_h_zero_count': sum(1 for h in populated_h if h == 0.0),
    'empty_h_zero_count': sum(1 for h in empty_h if h == 0.0),
    'populated_h_range': [min(populated_h), max(populated_h)],
    'empty_h_range': [min(empty_h), max(empty_h)],
    'states_where_different': sum(1 for p, e in zip(populated_h, empty_h) if p != e),
    'imag_pop_nonzero': imag_pop,
    'imag_empty_nonzero': imag_empty,
    'state_count': len(states),
}
import json as j
with open('DATASETS/qsmc1_consumer_boundary_avatar_results.json', 'w') as f:
    j.dump(results, f, indent=2)
print(f"\nResults saved to DATASETS/qsmc1_consumer_boundary_avatar_results.json")
print("Avatar-path reproduction complete.")
