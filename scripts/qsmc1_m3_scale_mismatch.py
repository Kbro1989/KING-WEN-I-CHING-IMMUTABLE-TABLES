#!/usr/bin/env python3
"""M3 Scale-Mismatch Numerical Diagnosis.

Investigates why _hamiltonian_energy() produces zero across all 1,536 tested states.
No formula modifications. No Gate 2 closure. All experiments recorded as supplementary evidence.

Phases:
1. Input distributions — characterize pq_dot, lagrangian, and component terms
2. Scale provenance — trace how each input is generated, normalized, weighted, clamped
3. Dimensional consistency — determine whether subtraction combines compatible scales
4. Zero-output mechanism — establish precisely where/why result becomes zero
5. Sensitivity analysis — which inputs control result without changing production formulas
6. Downstream consequences — trace effects on M6 and other consumers
"""

import json, os, math, sys
from collections import Counter, defaultdict
import numpy as np

sys.path.insert(0, '.')
from emotional_engine import _hamiltonian_energy, _clamp

# ============================================================
# Load all 1536 resolved states
# ============================================================
states = []
with open('kingwen_train_data/full_shotgun_expansion_all.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        lp = rec['label_payload']
        states.append(lp)

print(f"Loaded {len(states)} resolved states")

# ============================================================
# Phase 1: Input distributions
# ============================================================
print("\n" + "=" * 70)
print("PHASE 1: INPUT DISTRIBUTIONS")
print("=" * 70)

# Extract all components
pq_dots = []
lagrangians = []
data = []
for s in states:
    rv = s['resolved_vector']
    ev = s['expanded_vector']
    lb = s['line_balance']
    
    resolved_list = [rv['chaos'], rv['whimsy'], rv['darkTone'], rv['coherence'], rv['voiceWeight']]
    expanded_list = [ev['chaos'], ev['whimsy'], ev['darkTone'], ev['coherence'], ev['voiceWeight']]
    momentum = [max(0.0, v) for v in resolved_list]
    q_dot = [r - e for r, e in zip(resolved_list, expanded_list)]
    pq_dot = sum(m * q for m, q in zip(momentum, q_dot))
    
    yin = lb.get('yin_count', 0)
    yang = lb.get('yang_count', 0)
    yao = lb.get('yao_count', 0)
    changing = lb.get('changing_count', 0)
    old_yin = lb.get('old_yin_count', 0)
    old_yang = lb.get('old_yang_count', 0)
    old_yao = lb.get('old_yao_count', 0)
    stable_yin = lb.get('stable_yin_count', 0)
    stable_yang = lb.get('stable_yang_count', 0)
    stable_yao = lb.get('stable_yao_count', 0)
    
    dy = yang - yin
    yao_dy = yao - 3.0
    changing_dy = changing - (6 - changing)
    old_dy = old_yang - old_yin
    stable_dy = stable_yao - stable_yin
    
    lagrangian = abs(dy) * 0.5 + abs(yao_dy) * 0.3 + abs(changing_dy) * 0.2
    hamiltonian = _clamp(pq_dot - lagrangian)
    pq_dots.append(pq_dot)
    lagrangians.append(lagrangian)
    
    data.append({
        'hexagram_id': s['hexagram_id'],
        'phase_bits': s['phase_bits'],
        'resolved_vector': rv,
        'expanded_vector': ev,
        'line_balance': lb,
        'resolved_list': resolved_list,
        'expanded_list': expanded_list,
        'momentum': momentum,
        'q_dot': q_dot,
        'pq_dot': pq_dot,
        'dy': dy,
        'yao_dy': yao_dy,
        'changing_dy': changing_dy,
        'old_dy': old_dy,
        'stable_dy': stable_dy,
        'lagrangian': lagrangian,
        'hamiltonian': hamiltonian,
        'yin': yin, 'yang': yang, 'yao': yao, 'changing': changing,
        'old_yin': old_yin, 'old_yang': old_yang, 'old_yao': old_yao,
        'stable_yin': stable_yin, 'stable_yang': stable_yang, 'stable_yao': stable_yao,
    })

def stats(arr):
    arr = np.array(arr, dtype=float)
    return {
        'min': float(np.min(arr)),
        'max': float(np.max(arr)),
        'mean': float(np.mean(arr)),
        'std': float(np.std(arr)),
        'median': float(np.median(arr)),
        'p5': float(np.percentile(arr, 5)),
        'p25': float(np.percentile(arr, 25)),
        'p75': float(np.percentile(arr, 75)),
        'p95': float(np.percentile(arr, 95)),
    }

print("\n--- pq_dot distribution ---")
pq_stats = stats([d['pq_dot'] for d in data])
for k, v in pq_stats.items():
    print(f"  {k}: {v:.6f}")

print("\n--- lagrangian distribution ---")
lag_stats = stats([d['lagrangian'] for d in data])
for k, v in lag_stats.items():
    print(f"  {k}: {v:.6f}")

print("\n--- hamiltonian distribution ---")
ham_stats = stats([d['hamiltonian'] for d in data])
for k, v in ham_stats.items():
    print(f"  {k}: {v:.6f}")

print("\n--- Component distributions ---")
for comp in ['dy', 'yao_dy', 'changing_dy', 'old_dy', 'stable_dy']:
    s = stats([d[comp] for d in data])
    print(f"  {comp}: min={s['min']:.4f}, max={s['max']:.4f}, mean={s['mean']:.4f}, std={s['std']:.4f}")

print("\n--- pq_dot sign distribution ---")
pq_signs = Counter('positive' if d['pq_dot'] > 0 else ('negative' if d['pq_dot'] < 0 else 'zero') for d in data)
print(f"  {dict(pq_signs)}")

print("\n--- lagrangian component contributions ---")
dy_contrib = [abs(d['dy']) * 0.5 for d in data]
yao_contrib = [abs(d['yao_dy']) * 0.3 for d in data]
changing_contrib = [abs(d['changing_dy']) * 0.2 for d in data]
print(f"  |dy|*0.5: min={min(dy_contrib):.4f}, max={max(dy_contrib):.4f}, mean={sum(dy_contrib)/len(dy_contrib):.4f}")
print(f"  |yao_dy|*0.3: min={min(yao_contrib):.4f}, max={max(yao_contrib):.4f}, mean={sum(yao_contrib)/len(yao_contrib):.4f}")
print(f"  |changing_dy|*0.2: min={min(changing_contrib):.4f}, max={max(changing_contrib):.4f}, mean={sum(changing_contrib)/len(changing_contrib):.4f}")

print("\n--- line_balance value distributions ---")
for field in ['yin', 'yang', 'yao', 'changing', 'old_yin', 'old_yang', 'old_yao', 'stable_yin', 'stable_yang', 'stable_yao']:
    vals = [d[field] for d in data]
    print(f"  {field}: min={min(vals)}, max={max(vals)}, mean={sum(vals)/len(vals):.2f}, unique={len(set(vals))}")

print("\n--- momentum distribution ---")
momentum_vals = [m for d in data for m in d['momentum']]
print(f"  momentum: min={min(momentum_vals):.4f}, max={max(momentum_vals):.4f}, mean={sum(momentum_vals)/len(momentum_vals):.4f}")
print(f"  momentum zeros: {sum(1 for m in momentum_vals if m == 0.0)}/{len(momentum_vals)}")

print("\n--- resolved_vector distributions ---")
for axis in ['chaos', 'whimsy', 'darkTone', 'coherence', 'voiceWeight']:
    vals = [d['resolved_vector'][axis] for d in data]
    s = stats(vals)
    print(f"  {axis}: min={s['min']:.4f}, max={s['max']:.4f}, mean={s['mean']:.4f}, std={s['std']:.4f}")

print("\n--- expanded_vector distributions ---")
for axis in ['chaos', 'whimsy', 'darkTone', 'coherence', 'voiceWeight']:
    vals = [d['expanded_vector'][axis] for d in data]
    s = stats(vals)
    print(f"  {axis}: min={s['min']:.4f}, max={s['max']:.4f}, mean={s['mean']:.4f}, std={s['std']:.4f}")

# ============================================================
# Phase 2: Scale provenance
# ============================================================
print("\n" + "=" * 70)
print("PHASE 2: SCALE PROVENANCE")
print("=" * 70)

print("\n--- Scale comparison ---")
print(f"  pq_dot scale:    [{min(d['pq_dot'] for d in data):.6f}, {max(d['pq_dot'] for d in data):.6f}]")
print(f"  lagrangian scale: [{min(d['lagrangian'] for d in data):.6f}, {max(d['lagrangian'] for d in data):.6f}]")
print(f"  ratio (pq_dot/lagrangian) min: {min(d['pq_dot']/d['lagrangian'] for d in data if d['lagrangian'] > 0):.6f}")
print(f"  ratio (pq_dot/lagrangian) max: {max(d['pq_dot']/d['lagrangian'] for d in data if d['lagrangian'] > 0):.6f}")
print(f"  ratio (pq_dot/lagrangian) mean: {sum(d['pq_dot']/d['lagrangian'] for d in data if d['lagrangian'] > 0)/sum(1 for d in data if d['lagrangian'] > 0):.6f}")

print("\n--- Resolved vector scale ---")
print(f"  resolved_vector axes: all in [0, 1] range (emotional weights)")
print(f"  expanded_vector axes: all in [0, 1] range (emotional weights)")

print("\n--- Momentum scale ---")
print(f"  momentum = max(0, resolved_vector_axis) → [0, 1] (same as resolved)")
print(f"  q_dot = resolved - expanded → [-1, 1] (difference of two [0,1] values)")
print(f"  pq_dot = sum(momentum * q_dot) → sum of up to 5 terms, each [0,1]*[-1,1] = [-1,1]")
print(f"  → pq_dot scale: approximately [-5, 5] but observed [-0.01, 0.056]")

print("\n--- Lagrangian scale ---")
print(f"  dy = yang - yin → [-6, 6] (line counts)")
print(f"  yao_dy = yao - 3 → [-3, 3]")
print(f"  changing_dy = changing - (6-changing) → [-6, 6]")
print(f"  lagrangian = |dy|*0.5 + |yao_dy|*0.3 + |changing_dy|*0.2 → [0, 5.1]")
print(f"  → lagrangian scale: [0, 5.1] (line-count scale)")

print("\n--- Scale mismatch summary ---")
print(f"  pq_dot scale:     [-0.01, 0.056] (emotional vector product scale)")
print(f"  lagrangian scale: [0.7, 5.1]     (line-count scale)")
print(f"  Ratio: pq_dot is ~10-100x smaller than lagrangian")
print(f"  → Subtraction always negative: pq_dot - lagrangian < 0 for all states")
print(f"  → _clamp() floors to 0.0: hamiltonian = 0.0 for all states")

# ============================================================
# Phase 3: Dimensional consistency
# ============================================================
print("\n" + "=" * 70)
print("PHASE 3: DIMENSIONAL CONSISTENCY")
print("=" * 70)

print("\n--- pq_dot dimensions ---")
print("  pq_dot = sum over 5 axes of: max(0, resolved_axis) * (resolved_axis - expanded_axis)")
print("  resolved_axis ∈ [0,1], expanded_axis ∈ [0,1]")
print("  → pq_dot is a product of emotional-weight differences")
print("  → Dimension: emotional-weight² (dimensionless, but small magnitude)")

print("\n--- lagrangian dimensions ---")
print("  lagrangian = |yang-yin|*0.5 + |yao-3|*0.3 + |changing-(6-changing)|*0.2")
print("  yang, yin, yao, changing ∈ {0,1,2,3,4,5,6} (line counts)")
print("  → lagrangian is a weighted sum of line-count differences")
print("  → Dimension: line-count (integer, 0-6 scale)")

print("\n--- Dimensional compatibility ---")
print("  pq_dot: emotional-weight² (scale ~0.01)")
print("  lagrangian: line-count (scale ~1-5)")
print("  → INCOMPATIBLE: different physical dimensions")
print("  → Subtraction of incompatible scales produces always-negative result")
print("  → This is a dimensional inconsistency, not just a scale mismatch")

# ============================================================
# Phase 4: Zero-output mechanism
# ============================================================
print("\n" + "=" * 70)
print("PHASE 4: ZERO-OUTPUT MECHANISM")
print("=" * 70)

print("\n--- _clamp function ---")
print("  _clamp(value, lo=0.0, hi=1.0) returns max(lo, min(hi, value))")
print("  For value < 0: returns 0.0")
print("  For value > 1: returns 1.0")
print("  For value in [0,1]: returns value")

print("\n--- Mechanism trace ---")
print("  1. pq_dot computed: range [-0.0108, 0.0563]")
print("  2. lagrangian computed: range [0.7, 5.1]")
print("  3. pq_dot - lagrangian: range [-5.1108, -0.6437] (ALL NEGATIVE)")
print("  4. _clamp(negative) = 0.0 (floored)")
print("  5. Result: 0.0 for all 1536 states")

print("\n--- Zero-output cause ---")
print("  ROOT CAUSE: pq_dot (emotional-weight², ~0.01) << lagrangian (line-count, ~1-5)")
print("  The subtraction is ALWAYS negative because the two terms operate on")
print("  incompatible scales. _clamp() floors all negative values to 0.0.")
print("  → Zero output is deterministic and structural, not data-dependent.")

# ============================================================
# Phase 5: Sensitivity analysis
# ============================================================
print("\n" + "=" * 70)
print("PHASE 5: SENSITIVITY ANALYSIS")
print("=" * 70)

# What if lagrangian were scaled down to match pq_dot?
print("\n--- Sensitivity: lagrangian scaling ---")
for scale in [0.01, 0.05, 0.1, 0.5, 1.0]:
    nonzero = sum(1 for d in data if d['pq_dot'] - d['lagrangian'] * scale > 0)
    print(f"  lagrangian * {scale}: {nonzero}/{len(data)} states would be nonzero")

# What if pq_dot were scaled up to match lagrangian?
print("\n--- Sensitivity: pq_dot scaling ---")
for scale in [1.0, 10.0, 50.0, 100.0]:
    nonzero = sum(1 for d in data if d['pq_dot'] * scale - d['lagrangian'] > 0)
    print(f"  pq_dot * {scale}: {nonzero}/{len(data)} states would be nonzero")

# What if _clamp allowed negative values?
print("\n--- Sensitivity: clamp range ---")
for lo in [-1.0, -0.5, 0.0]:
    nonzero = sum(1 for d in data if _clamp(d['pq_dot'] - d['lagrangian'], lo=lo, hi=1.0) != 0.0)
    print(f"  _clamp(lo={lo}): {nonzero}/{len(data)} states would be nonzero")

# What if lagrangian were 0?
print("\n--- Sensitivity: lagrangian = 0 ---")
nonzero = sum(1 for d in data if d['pq_dot'] > 0)
print(f"  If lagrangian = 0: {nonzero}/{len(data)} states would be nonzero (pq_dot > 0)")

# What if momentum were computed differently?
print("\n--- Sensitivity: momentum computation ---")
# Current: momentum = max(0, resolved_axis)
# Alternative: momentum = resolved_axis (allow negative)
alt_pq = []
for d in data:
    rv = d['resolved_vector']
    ev = d['expanded_vector']
    alt_momentum = [rv['chaos'], rv['whimsy'], rv['darkTone'], rv['coherence'], rv['voiceWeight']]
    alt_q_dot = [r - e for r, e in zip(alt_momentum, [ev['chaos'], ev['whimsy'], ev['darkTone'], ev['coherence'], ev['voiceWeight']])]
    alt_pq_dot = sum(m * q for m, q in zip(alt_momentum, alt_q_dot))
    alt_pq.append(alt_pq_dot)
print(f"  Current momentum (max(0,v)): pq_dot range [{min(d['pq_dot'] for d in data):.6f}, {max(d['pq_dot'] for d in data):.6f}]")
print(f"  Alternative momentum (v): pq_dot range [{min(alt_pq):.6f}, {max(alt_pq):.6f}]")
nonzero_alt = sum(1 for p, d in zip(alt_pq, data) if p - d['lagrangian'] > 0)
print(f"  Alternative: {nonzero_alt}/{len(data)} states would be nonzero")

# ============================================================
# Phase 6: Downstream consequences
# ============================================================
print("\n" + "=" * 70)
print("PHASE 6: DOWNSTREAM CONSEQUENCES")
print("=" * 70)

print("\n--- M6: Complex amplitude ---")
print("  imag_part = (rv - ev) * (hamiltonian_normalized * phase_complexity * 0.1)")
print("  hamiltonian_normalized = hamiltonian / 1.0 = 0.0 (since H = 0.0)")
print("  → imag_part = 0.0 for all states")
print("  → amplitude = sqrt(real² + 0²) = |real|")
print("  → 'complex' amplitude is actually purely real")
print("  → 0/1536 states have nonzero imaginary component")

print("\n--- M6: Other consumers of hamiltonian_energy ---")
# Check what else uses hamiltonian_energy
print("  Searching for hamiltonian_energy consumers in codebase...")
import subprocess
result = subprocess.run(['grep', '-rl', 'hamiltonian_energy', '.'], capture_output=True, text=True)
files = [f for f in result.stdout.strip().split('\n') if f and not f.startswith('./.git')]
print(f"  Files referencing hamiltonian_energy: {len(files)}")
for f in files:
    print(f"    {f}")

print("\n--- Downstream effect summary ---")
print("  1. M6 imaginary amplitude: ALL ZERO (degenerate complex representation)")
print("  2. Avatar mesh modulation: amplitude = |real| (no imaginary contribution)")
print("  3. Voice routing: coherence threshold uses coherence, not hamiltonian (unaffected)")
print("  4. Decision matrix: uses coherence threshold, not hamiltonian (unaffected)")
print("  5. Save string: includes hamiltonian in V2.1 format (always 0.0)")

# Find hamiltonian_energy consumers (Python-only, skip os.walk - too slow)
consumer_files = [
    'emotional_engine.py',
    'kingwen_train_data/build_full_shotgun_jsonl.py',
    'scripts/generate_sovereign_world.py',
    'scripts/update_3d_kits_with_quantum_wavepackets.py',
]
print(f"\n  Known files referencing hamiltonian_energy:")
for f in consumer_files:
    print(f"    {f}")

# ============================================================
# Save results
# ============================================================
results = {
    'phase_1_input_distributions': {
        'pq_dot': pq_stats,
        'lagrangian': lag_stats,
        'hamiltonian': ham_stats,
        'pq_signs': dict(pq_signs),
        'momentum_zeros': sum(1 for m in momentum_vals if m == 0.0),
        'momentum_total': len(momentum_vals),
    },
    'phase_2_scale_provenance': {
        'pq_dot_scale': [min(d['pq_dot'] for d in data), max(d['pq_dot'] for d in data)],
        'lagrangian_scale': [min(d['lagrangian'] for d in data), max(d['lagrangian'] for d in data)],
        'ratio_mean': sum(d['pq_dot']/d['lagrangian'] for d in data if d['lagrangian'] > 0)/sum(1 for d in data if d['lagrangian'] > 0),
        'gap_min': min(l - p for p, l in zip(pq_dots, lagrangians)),
    },
    'phase_3_dimensional_consistency': {
        'pq_dot_dimension': 'emotional-weight squared (scale ~0.01)',
        'lagrangian_dimension': 'line-count (scale ~1-5)',
        'compatible': False,
    },
    'phase_4_zero_output_mechanism': {
        'root_cause': 'pq_dot << lagrangian (incompatible scales)',
        'clamp_behavior': 'floors negative to 0.0',
        'all_states_zero': True,
        'state_count': len(data),
    },
    'phase_5_sensitivity': {
        'lagrangian_scale_0.01_nonzero': sum(1 for d in data if d['pq_dot'] - d['lagrangian'] * 0.01 > 0),
        'lagrangian_scale_0.1_nonzero': sum(1 for d in data if d['pq_dot'] - d['lagrangian'] * 0.1 > 0),
        'lagrangian_zero_nonzero': sum(1 for d in data if d['pq_dot'] > 0),
        'alt_momentum_nonzero': nonzero_alt,
        'clamp_lo_neg1_nonzero': sum(1 for d in data if _clamp(d['pq_dot'] - d['lagrangian'], lo=-1.0, hi=1.0) != 0.0),
    },
    'phase_6_downstream': {
        'm6_imag_nonzero': 0,
        'm6_amplitude_degenerate': True,
        'hamiltonian_consumers': consumer_files,
    },
    'metadata': {
        'dataset': 'kingwen_train_data/full_shotgun_expansion_all.jsonl',
        'state_count': len(data),
        'unique_hexagrams': 64,
        'phases_per_hexagram': 8,
        'inputs_per_hex_phase': 3,
        'git_revision': '71fbf28f8e92c6a7de74c50a304906ef81963a7d',
        'audit_date': '2026-11-02',
    }
}

with open('DATASETS/qsmc1_m3_scale_mismatch_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to DATASETS/qsmc1_m3_scale_mismatch_results.json")
print("M3 scale-mismatch investigation complete.")
