"""Entry 3 hypothesis test: raw Hamiltonian value distribution across 1,536 states."""
import sys, json, math
sys.path.insert(0, "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts")

from full_hexagram_shotgun import shotgun_expand
from emotional_engine import VEC_KEYS

def raw_hamiltonian(resolved_vector, expanded_vector, line_balance):
    """Compute raw H WITHOUT clamp — replicates _hamiltonian_energy but returns raw."""
    momentum = [max(0.0, float(v)) for v in resolved_vector]
    q_dot = [float(rv) - float(ev) for rv, ev in zip(resolved_vector, expanded_vector)]
    pq_dot = sum(m * qd for m, qd in zip(momentum, q_dot))

    yin_count = float(line_balance.get("yin_count", 0) or 0)
    yang_count = float(line_balance.get("yang_count", 0) or 0)
    yao_count = float(line_balance.get("yao_count", 0) or 0)
    changing_count = float(line_balance.get("changing_count", 0) or 0)
    old_yang_count = float(line_balance.get("old_yang_count", 0) or 0)
    old_yin_count = float(line_balance.get("old_yin_count", 0) or 0)
    stable_yao_count = float(line_balance.get("stable_yao_count", 0) or 0)
    stable_yin_count = float(line_balance.get("stable_yin_count", 0) or 0)

    old_dy = old_yang_count - old_yin_count
    stable_dy = stable_yao_count - stable_yin_count
    dy = yang_count - yin_count
    yao_dy = yao_count - 3.0
    changing_dy = changing_count - (6.0 - changing_count)

    lagrangian = (
        abs(dy) * 0.5
        + abs(yao_dy) * 0.3
        + abs(changing_dy) * 0.2
    )
    return pq_dot, lagrangian, pq_dot - lagrangian

# Collect raw H for all 1,536 states
all_raw = []
all_pq_dot = []
all_lagrangian = []
all_hex_ids = []
all_phases = []
all_emotional_inputs = []

for ei in [0, 50, 100]:
    result = shotgun_expand(request_text="test", emotional_input=ei)
    expanded = result["expanded"]
    resolved = result["resolved"]
    # Build expanded lookup by hexagram_id
    expanded_by_hex = {}
    for e in expanded:
        expanded_by_hex[e["hexagram_id"]] = e

    for r in resolved:
        h_id = r["hexagram_id"]
        phase = r["phase_bits"]
        ev = expanded_by_hex.get(h_id, {})
        rv = [float(r.get("resolved_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS]
        ev_vec = [float(ev.get("expanded_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS]
        lb = r.get("line_balance", {})
        pq_dot, lagrangian, raw_h = raw_hamiltonian(rv, ev_vec, lb)
        all_raw.append(raw_h)
        all_pq_dot.append(pq_dot)
        all_lagrangian.append(lagrangian)
        all_hex_ids.append(h_id)
        all_phases.append(phase)
        all_emotional_inputs.append(ei)

# Analysis
print("=" * 60)
print("RAW HAMILTONIAN DISTRIBUTION (no clamp)")
print("=" * 60)
print(f"Total states: {len(all_raw)}")
print(f"Distinct raw H values: {len(set(round(x, 10) for x in all_raw))}")
print(f"Min raw H: {min(all_raw):.6f}")
print(f"Max raw H: {max(all_raw):.6f}")
print(f"Mean raw H: {sum(all_raw)/len(all_raw):.6f}")
print(f"All raw H < 0: {all(x < 0 for x in all_raw)}")
print(f"All raw H == 0: {all(x == 0.0 for x in all_raw)}")
print()

# pq_dot distribution
print("pq_dot:")
print(f"  Distinct: {len(set(round(x, 10) for x in all_pq_dot))}")
print(f"  Min: {min(all_pq_dot):.6f}, Max: {max(all_pq_dot):.6f}, Mean: {sum(all_pq_dot)/len(all_pq_dot):.6f}")
print()

# lagrangian distribution
print("lagrangian:")
print(f"  Distinct: {len(set(round(x, 10) for x in all_lagrangian))}")
print(f"  Min: {min(all_lagrangian):.6f}, Max: {max(all_lagrangian):.6f}, Mean: {sum(all_lagrangian)/len(all_lagrangian):.6f}")
print()

# Collapse analysis: how many distinct raw values collapse to 0?
print("Collapse analysis:")
print(f"  Distinct raw H values: {len(set(round(x, 10) for x in all_raw))}")
print(f"  All collapse to 0.0 under clamp: {all(x <= 0 for x in all_raw)}")
print(f"  Information lost: {len(set(round(x, 10) for x in all_raw))} distinct values → 1 observed value (0.0)")
print()

# Correlation with emotional_input
for ei in [0, 50, 100]:
    subset = [x for x, e in zip(all_raw, all_emotional_inputs) if e == ei]
    print(f"  emotional_input={ei}: min={min(subset):.6f}, max={max(subset):.6f}, mean={sum(subset)/len(subset):.6f}, distinct={len(set(round(x,10) for x in subset))}")

# Correlation with phase
print()
for phase in range(8):
    subset = [x for x, p in zip(all_raw, all_phases) if p == phase]
    print(f"  phase={phase}: min={min(subset):.6f}, max={max(subset):.6f}, mean={sum(subset)/len(subset):.6f}, distinct={len(set(round(x,10) for x in subset))}")

# Value collapse histogram (how many raw values per distinct value)
from collections import Counter
rounded = [round(x, 6) for x in all_raw]
counts = Counter(rounded)
print(f"\nTop 5 most common raw H values:")
for val, count in counts.most_common(5):
    print(f"  {val}: {count} states ({count/len(all_raw)*100:.1f}%)")
print(f"Number of distinct raw H values: {len(counts)}")
print(f"States per distinct value (avg): {len(all_raw)/len(counts):.1f}")

# Save results
import json
output = {
    "total_states": len(all_raw),
    "distinct_raw_h": len(set(round(x, 10) for x in all_raw)),
    "min_raw_h": min(all_raw),
    "max_raw_h": max(all_raw),
    "mean_raw_h": sum(all_raw)/len(all_raw),
    "all_negative": all(x < 0 for x in all_raw),
    "all_collapse_to_zero": all(x <= 0 for x in all_raw),
    "pq_dot_distinct": len(set(round(x, 10) for x in all_pq_dot)),
    "pq_dot_min": min(all_pq_dot),
    "pq_dot_max": max(all_pq_dot),
    "pq_dot_mean": sum(all_pq_dot)/len(all_pq_dot),
    "lagrangian_distinct": len(set(round(x, 10) for x in all_lagrangian)),
    "lagrangian_min": min(all_lagrangian),
    "lagrangian_max": max(all_lagrangian),
    "lagrangian_mean": sum(all_lagrangian)/len(all_lagrangian),
    "information_lost": f"{len(set(round(x, 10) for x in all_raw))} distinct values -> 1 observed value (0.0)",
}
with open("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/raw_h_distribution_2026-11-02.json", "w") as f:
    json.dump(output, f, indent=2)
print("\nResults saved to DATASETS/raw_h_distribution_2026-11-02.json")
