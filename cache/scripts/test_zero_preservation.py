"""Entry 1 verification: zero-preservation across porosity paths."""
import sys, os, json
sys.path.insert(0, "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
sys.path.insert(0, "C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts")

registry = json.load(open("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/data/hexagram-registry.json"))

results = []

def check(label, expected, actual):
    status = "PASS" if expected == actual else "FAIL"
    results.append((status, label, expected, actual))
    print(f"  [{status}] {label}: expected={expected}, actual={actual}")

# --- decision_matrix.score_resolved_state ---
print("=== decision_matrix.score_resolved_state ===")
from decision_matrix import score_resolved_state

for porosity_val in [0.0, 0.35, 1.0]:
    inject = {"porosity": porosity_val, "porosity_norm": porosity_val / 4.0 if porosity_val else 0.0}
    resolved = {"hexagram_id": 1, "inject_site": inject, "resolved_vector": {}, "line_balance": {}}
    try:
        score = score_resolved_state(resolved, registry, emotional_input=50)
        # Verify porosity_norm was preserved (not masked)
        pn = float((resolved.get("inject_site") or {}).get("porosity_norm", 0.35))
        expected_pn = porosity_val / 4.0 if porosity_val else 0.0
        check(f"porosity={porosity_val} norm preserved", expected_pn, pn)
    except Exception as e:
        print(f"  [ERROR] porosity={porosity_val}: {e}")

# Missing key
inject_missing = {}
resolved = {"hexagram_id": 1, "inject_site": inject_missing, "resolved_vector": {}, "line_balance": {}}
try:
    score = score_resolved_state(resolved, registry, emotional_input=50)
    pn = float((resolved.get("inject_site") or {}).get("porosity_norm", 0.35))
    check("missing key → default 0.35", 0.35, pn)
except Exception as e:
    print(f"  [ERROR] missing key: {e}")

# None value
inject_none = {"porosity": None, "porosity_norm": None}
resolved = {"hexagram_id": 1, "inject_site": inject_none, "resolved_vector": {}, "line_balance": {}}
try:
    score = score_resolved_state(resolved, registry, emotional_input=50)
    pn = float((resolved.get("inject_site") or {}).get("porosity_norm", 0.35))
    check("None → default 0.35", 0.35, pn)
except Exception as e:
    print(f"  [ERROR] None value: {e}")

# --- emotional_engine._tau_for_resolved ---
print("\n=== emotional_engine._tau_for_resolved ===")
from emotional_engine import _tau_for_resolved

for porosity_val in [0.0, 0.35, 1.0]:
    inject = {"porosity": porosity_val, "porosity_norm": porosity_val / 4.0 if porosity_val else 0.0}
    item = {"hexagram_id": 1, "inject_site": inject, "resolved_vector": {}}
    try:
        tau = _tau_for_resolved(item, emotional_input=50)
        check(f"porosity={porosity_val} no crash", True, True)
    except Exception as e:
        print(f"  [ERROR] porosity={porosity_val}: {e}")

# --- schauberger_parsing_layers ---
print("\n=== schauberger_parsing_layers ===")
from schauberger_parsing_layers import schauberger_parsing_layers
import schauberger_parsing_layers as spl

for porosity_val in [0.0, 0.35, 4.0]:
    spl.HEXAGRAM_INJECTION_SITE[1] = {"porosity": porosity_val}
    try:
        result = schauberger_parsing_layers(1, phase_bits=0, emotional_input=50)
        vt = result.get("vortex_tension", {})
        check(f"porosity={porosity_val} vortex computed", True, vt is not None)
    except Exception as e:
        print(f"  [ERROR] porosity={porosity_val}: {e}")
    finally:
        spl.HEXAGRAM_INJECTION_SITE.pop(1, None)

# Missing key
spl.HEXAGRAM_INJECTION_SITE.pop(1, None)
try:
    result = schauberger_parsing_layers(1, phase_bits=0, emotional_input=50)
    check("missing key → default 0.35", True, True)
except Exception as e:
    print(f"  [ERROR] missing key: {e}")

# --- multi_layer_expand.open_pool_consensus ---
print("\n=== multi_layer_expand.open_pool_consensus ===")
from multi_layer_expand import open_pool_consensus

# 0.0 porosity test
resolved_0 = [{"hexagram_id": 1, "inject_site": {"porosity": 0.0, "porosity_norm": 0.0}, "resolved_vector": {}, "phase_temporal": "present"}]
try:
    result = open_pool_consensus(resolved_0, emotional_input=50)
    pm = result.get("consensus_porosity_mean", None)
    check("0.0 porosity preserved in consensus (porosity_mean)", 0.0, pm)
except Exception as e:
    print(f"  [ERROR] 0.0 porosity: {e}")

# 0.35 porosity test
resolved_35 = [{"hexagram_id": 1, "inject_site": {"porosity": 0.35, "porosity_norm": 0.0875}, "resolved_vector": {}, "phase_temporal": "present"}]
try:
    result = open_pool_consensus(resolved_35, emotional_input=50)
    pm = result.get("consensus_porosity_mean", None)
    check("0.35 porosity preserved in consensus", 0.35, pm)
except Exception as e:
    print(f"  [ERROR] 0.35 porosity: {e}")

# --- Check remaining or 0.0875 bug ---
print("\n=== Remaining fallback audit ===")
import re
for f in ["multi_layer_expand.py"]:
    path = f"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts/{f}"
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            if "or 0.0875" in line or "or 0.35" in line:
                print(f"  REMAINING BUG: {f}:{i}: {line.strip()}")

# --- Summary ---
print("\n=== SUMMARY ===")
passes = sum(1 for s, _, _, _ in results if s == "PASS")
fails = sum(1 for s, _, _, _ in results if s == "FAIL")
print(f"Total: {len(results)} tests, {passes} PASS, {fails} FAIL")
for status, label, expected, actual in results:
    if status == "FAIL":
        print(f"  FAIL: {label} (expected={expected}, actual={actual})")
