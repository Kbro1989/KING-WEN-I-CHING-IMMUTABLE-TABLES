"""Final verification: immutable King Wen 9-bit table math."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

p = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")
spec = importlib.util.spec_from_file_location("kwt_final3", str(p))
mod = importlib.util.module_from_spec(spec)
sys.modules["kwt_final3"] = mod
spec.loader.exec_module(mod)

ENCODING_TABLE = mod.ENCODING_TABLE
HEXAGRAM_BASE = mod.HEXAGRAM_BASE
PHASE_LINE_MAP = mod.PHASE_LINE_MAP
HEX_PHASE_TO_9BIT = mod.HEX_PHASE_TO_9BIT
BIT6_TO_HEXAGRAM = mod.BIT6_TO_HEXAGRAM

# Test A: 9-bit formula
m1 = []
for (hid, phase), expected in HEX_PHASE_TO_9BIT.items():
    base = HEXAGRAM_BASE[hid]
    computed = (base["upper_idx"] * 8 + base["lower_idx"]) * 8 + (phase & 0b111)
    if computed != expected:
        m1.append((hid, phase, expected, computed))
print(f"Test A 9-bit formula: {len(m1)} mismatches", "PASS" if not m1 else "FAIL")

# Test B: changing lines match PHASE_LINE_MAP
m2 = []
for hid, entry in ENCODING_TABLE.items():
    expected = PHASE_LINE_MAP.get(entry["phase_bits"], [])
    actual = entry["phase_changing_lines"]
    if sorted(expected) != sorted(actual):
        m2.append((hid, entry["phase_bits"], expected, actual))
print(f"Test B changing lines: {len(m2)} mismatches", "PASS" if not m2 else "FAIL")

# Test C: ternary lines derived from binary_top_to_bottom + phase yao substitutions
# CONFIRMED RULE: stored array is binary_top_to_bottom left-to-right.
# Changing lines are numbered 1-6 bottom-to-top, applied at array index (line_num - 1).
m3 = []
for hid, entry in ENCODING_TABLE.items():
    phase_bits = entry["phase_bits"]
    changing = set(PHASE_LINE_MAP.get(phase_bits, []))
    base = HEXAGRAM_BASE[entry["hexagram_id"]]
    bits = [int(c) for c in base["binary_top_to_bottom"]]
    derived = bits.copy()
    for line_num in changing:
        idx = line_num - 1
        if 0 <= idx < len(derived):
            derived[idx] = 2
    actual = entry["ternary_lines_top_to_bottom"]
    if derived != actual:
        m3.append((hid, phase_bits, derived, actual, bits, changing))
print(f"Test C ternary lines (confirmed derivation): {len(m3)} mismatches", "PASS" if not m3 else "FAIL")
if m3:
    for x in m3[:10]:
        print("  ", x)

# Test D: 9-bit space coverage
vals = set(HEX_PHASE_TO_9BIT.values())
missing = set(range(512)) - vals
extra = vals - set(range(512))
print(f"Test D 9-bit space: {len(vals)} values, missing={len(missing)}, extra={len(extra)}", "PASS" if not missing and not extra else "FAIL")

# Test E: BIT6 roundtrip
m5 = []
for hid, entry in HEXAGRAM_BASE.items():
    bit6 = (entry["upper_idx"] << 3) | entry["lower_idx"]
    if BIT6_TO_HEXAGRAM.get(bit6) != hid:
        m5.append((hid, bit6, BIT6_TO_HEXAGRAM.get(bit6)))
print(f"Test E BIT6 roundtrip: {len(m5)} mismatches", "PASS" if not m5 else "FAIL")

all_pass = not any([m1, m2, m3, missing, extra, m5])
print(f"\nOVERALL: {'ALL PASS' if all_pass else 'FAILURES PRESENT'}")
