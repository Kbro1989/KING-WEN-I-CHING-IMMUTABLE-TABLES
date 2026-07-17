#!/usr/bin/env python3
"""Sequential hexagram-by-hexagram learning pass.

Learned output: section-by-section pattern extraction, no mock data.
All values derive from kingwen_ternary_tables_complete.py immutable tables.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import kingwen_ternary_tables_complete as m


def _section(h: int) -> str:
    if h <= 12:
        return "first"
    if h <= 24:
        return "second"
    if h <= 36:
        return "third"
    if h <= 48:
        return "fourth"
    if h <= 60:
        return "fifth"
    return "sixth"


def _pattern_shape(base: dict, inj: dict, ew: dict) -> dict:
    binary = base["binary_bottom_to_top"]
    yang = binary.count("1")
    yin = binary.count("0")
    stability = max(yang, yin) / 6.0
    change = min(yang, yin) / 6.0
    vec = {k: float(ew.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]}
    alignment = sum(vec.values()) / max(1, len(vec))
    porosity_norm = float(inj.get("porosity", 0) or 0) / 4.0
    dominant = max(vec, key=vec.get)
    return {
        "binary": binary,
        "yang_count": yang,
        "yin_count": yin,
        "stability": stability,
        "change": change,
        "alignment": alignment,
        "dominant_axis": dominant,
        "dominant_value": vec[dominant],
        "porosity_norm": porosity_norm,
        "inject_pools": [inj.get("primary_pool"), inj.get("secondary_pool")],
        "reason": inj.get("reason", ""),
    }


def learn_sequential() -> dict:
    learned = {}
    prev_shape = None
    for h in range(1, 65):
        base = m.HEXAGRAM_BASE[h]
        inj = m.HEXAGRAM_INJECTION_SITE[h]
        ew = m.EMOTIONAL_WEIGHTS[str(h)]
        shape = _pattern_shape(base, inj, ew)

        # sequence deltas relative to previous hex
        delta = {}
        if prev_shape is not None:
            delta["stability_delta"] = shape["stability"] - prev_shape["stability"]
            delta["change_delta"] = shape["change"] - prev_shape["change"]
            delta["alignment_delta"] = shape["alignment"] - prev_shape["alignment"]
            delta["dominant_shift"] = (
                f"{prev_shape['dominant_axis']}->{shape['dominant_axis']}"
                if prev_shape["dominant_axis"] != shape["dominant_axis"]
                else "same"
            )

        learned[str(h)] = {
            "section": _section(h),
            "name": base["name"],
            "trigrams": {
                "upper": base["upper_trigram"],
                "lower": base["lower_trigram"],
                "upper_idx": int(base.get("upper_idx", 0) or 0),
                "lower_idx": int(base.get("lower_idx", 0) or 0),
            },
            "category": base["category"],
            "action": base["action"],
            "emotional_weights": {
                k: float(ew.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
            },
            "pattern_shape": shape,
            "sequence_delta": delta,
            "training_notes": ew.get("trainingNotes", ""),
            "unique_pattern_summary": (
                f"{base['name']}: {base['binary_bottom_to_top']} | "
                f"stability={shape['stability']:.2f} change={shape['change']:.2f} "
                f"alignment={shape['alignment']:.2f} dominant={shape['dominant_axis']}={shape['dominant_value']:.2f} "
                f"porosity={shape['porosity_norm']:.2f}"
            ),
        }
        prev_shape = shape
    return learned


def main() -> int:
    learned = learn_sequential()
    out_path = Path("learn/exports/learned_sequential_64.json")
    out_path.write_text(json.dumps(learned, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    print("ALL HEXAGRAMS")
    for h in range(1, 65):
        item = learned[str(h)]
        print(f"{h:02d}: {item['unique_pattern_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
