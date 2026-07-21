#!/usr/bin/env python3
"""Reconcile DATASETS master JSON against immutable tables.
Copy to DATASETS/ and run from that folder.
"""
import json, csv
from pathlib import Path
from collections import OrderedDict

# Load immutable tables directly
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS, HEXAGRAM_INJECTION_SITE

datasets = Path("DATASETS")
master_path = datasets / "kingwen_oracle_master (1).json"
flat_path = datasets / "kingwen_oracle_flat (1).csv"

# Load master JSON preserving order
master = json.loads(master_path.read_text(encoding='utf-8'))
hexagrams = master["hexagrams"] if isinstance(master["hexagrams"], list) else list(master["hexagrams"].values())

# Build lookups from immutable tables
inject_site_by_id = {}
for hid, rec in HEXAGRAM_INJECTION_SITE.items():
    try:
        inject_site_by_id[int(hid)] = {
            "primary_pool": rec["primary_pool"],
            "secondary_pool": rec["secondary_pool"],
            "porosity": rec["porosity"],
            "porosity_label": rec.get("porosity_label", ""),
            "porosity_window": list(rec.get("porosity_window", [])),
            "porosity_description": rec.get("porosity_description", ""),
            "reason": rec["reason"],
        }
    except Exception as e:
        print(f"inject site parse error {hid}: {e}")

weights_by_id = {}
for hid, rec in EMOTIONAL_WEIGHTS.items():
    try:
        weights_by_id[int(hid)] = {
            "voiceWeight": float(rec.get("voiceWeight", 0)),
            "coherence": float(rec.get("coherence", 0)),
            "chaos": float(rec.get("chaos", 0)),
            "whimsy": float(rec.get("whimsy", 0)),
            "darkTone": float(rec.get("darkTone", 0)),
        }
    except Exception as e:
        print(f"weights parse error {hid}: {e}")

# Validate master against immutable canons
inject_diff = []
weights_diff = []
for h in hexagrams:
    hid = int(h.get("hexagram_id", 0))
    if hid not in inject_site_by_id:
        print(f"missing inject site for hex {hid}")
        continue
    if hid not in weights_by_id:
        print(f"missing weights for hex {hid}")
        continue

    can_ins = inject_site_by_id[hid]
    cur_ins = h.get("inject_site", {})
    if (
        cur_ins.get("primary_pool") != can_ins["primary_pool"]
        or cur_ins.get("secondary_pool") != can_ins["secondary_pool"]
        or cur_ins.get("porosity") != can_ins["porosity"]
        or cur_ins.get("reason") != can_ins["reason"]
    ):
        inject_diff.append({
            "hid": hid,
            "old": dict(cur_ins),
            "new": dict(can_ins),
        })

    can_w = weights_by_id[hid]
    cur_w = h.get("emotional_deltas", {})
    if any(abs(float(cur_w.get(k, 0)) - can_w[k]) > 1e-6 for k in can_w):
        weights_diff.append({
            "hid": hid,
            "old": dict(cur_w),
            "new": dict(can_w),
        })

print(f"Inject-site diffs: {len(inject_diff)}")
for d in inject_diff:
    print(f"  hex {d['hid']:>2}: {json.dumps(d['old'], ensure_ascii=False)} -> {json.dumps(d['new'], ensure_ascii=False)}")

print(f"\nWeights diffs: {len(weights_diff)}")
for d in weights_diff[:10]:
    print(f"  hex {d['hid']:>2}: old={d['old']} new={d['new']}")
if len(weights_diff) > 10:
    print(f"  ... {len(weights_diff)-10} more")
