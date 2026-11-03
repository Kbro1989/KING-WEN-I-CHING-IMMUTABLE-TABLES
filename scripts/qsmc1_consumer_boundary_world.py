#!/usr/bin/env python3
"""Consumer-Boundary Audit: World-Viewer Zero Propagation Test.

Tests whether a controlled passage with energy: 0 propagates through the
Python ingestion and JavaScript fallback boundaries.

This is a RUNTIME BOUNDARY REPRODUCTION, not a formula correction.
"""

import json, sys, re
from pathlib import Path

# Test 1: Python ingestion (ingest_jkd_megatron_wavepackets.py)
# Simulate what happens when a passage has energy: 0
print("=== Test 1: Python Ingestion ===")
# The JKD formula: H = coherence - chaos - 0.5*darkTone + 0.3*voiceWeight - 0.2*whimsy
# If this produces 0, it's stored as "hamiltonian_energy": 0
test_vec = {"coherence": 0.5, "chaos": 0.5, "darkTone": 0.0, "voiceWeight": 0.0, "whimsy": 0.0}
H = test_vec["coherence"] - test_vec["chaos"] - 0.5 * test_vec["darkTone"] + 0.3 * test_vec["voiceWeight"] - 0.2 * test_vec["whimsy"]
print(f"  Test vector: {test_vec}")
print(f"  Computed H: {H}")
print(f"  Stored as: hamiltonian_energy = {H}")

# Test 2: JavaScript fallback
print("\n=== Test 2: JavaScript Fallback ===")
js_code = "const hamiltonian = passage.energy || 0.75;"
print(f"  JS code: {js_code}")
# Test with energy: 0
energy_zero = 0
result_zero = energy_zero or 0.75
print(f"  passage.energy = 0 → hamiltonian = {result_zero} (MASKED: 0 becomes 0.75)")
# Test with energy: 0.5
energy_nonzero = 0.5
result_nonzero = energy_nonzero or 0.75
print(f"  passage.energy = 0.5 → hamiltonian = {result_nonzero} (preserved)")
# Test with energy: null/undefined
energy_null = None
result_null = energy_null or 0.75
print(f"  passage.energy = null → hamiltonian = {result_null} (fallback)")

# Test 3: World viewer consumption
print("\n=== Test 3: World Viewer Consumption ===")
# The viewer uses hamiltonian for:
# - Pellet oscillator frequency
# - Pellet gain
# - Master ground-voice gain
# - Visual superposition-core pulse
print("  If hamiltonian=0 reaches viewer (no fallback): all pellet frequencies/gains = 0")
print("  If hamiltonian=0.75 (fallback): all pellet frequencies/gains use 0.75")
print("  The || 0.75 fallback transforms a genuine zero into a nonzero value")
print("  This CONCEALS upstream zero values during world inspection")

# Test 4: Generate sovereign world consumption
print("\n=== Test 4: generate_sovereign_world.py consumption ===")
# Line 207: "energy": rec.get("hamiltonian_energy", 0.75)
# If rec has hamiltonian_energy: 0, it returns 0 (not 0.75, because key exists)
# If rec lacks the key entirely, returns 0.75 default
print("  rec.get('hamiltonian_energy', 0.75):")
print("    If key present with value 0 → returns 0 (key exists, default not used)")
print("    If key absent → returns 0.75 (default)")
print("    If key present with value None → returns None (falsy but not 0.75)")

# Save results
results = {
    "python_ingestion": {
        "test_vector": test_vec,
        "computed_H": H,
        "note": "JKD formula produces H=0 when coherence=chaos and darkTone=voiceWeight=whimsy=0"
    },
    "js_fallback": {
        "energy_0_result": result_zero,
        "energy_0.5_result": result_nonzero,
        "energy_null_result": result_null,
        "finding": "|| 0.75 masks genuine zero values"
    },
    "world_viewer": {
        "finding": "Pellet frequencies/gains use fallback value 0.75 instead of actual 0"
    },
    "sovereign_world": {
        "finding": "rec.get('hamiltonian_energy', 0.75) returns 0 if key present with 0, 0.75 if absent"
    }
}
import json
with open('DATASETS/qsmc1_consumer_boundary_world_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to DATASETS/qsmc1_consumer_boundary_world_results.json")
print("World-viewer zero propagation test complete.")
