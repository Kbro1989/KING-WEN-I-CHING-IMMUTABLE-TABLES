"""Clean capture of every consensus pass to find hard-coded direction bias.

Writes one JSONL record per slider step with:
- tau_stats
- weight_stats
- top_hex_scores
- top_hex_weights_lookup
- top_hex_inject_sites
- top_hex_line_compositions
- consensus_output
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
EXPORT_DIR = ROOT / "learn" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))

from emotional_engine import (
    VEC_KEYS,
    _clamp,
    _gaussian_weight,
    _mode_of_tau,
    _pool_by_name,
    _tau_for_resolved,
    collapse_full_128,
    EMOTIONAL_WEIGHTS,
)


def capture(emotional_input: int) -> dict:
    collapse = collapse_full_128(emotional_input=emotional_input)
    resolved = collapse["resolved"]
    consensus = collapse["consensus"]

    tau_values = [_tau_for_resolved(item, emotional_input=emotional_input) for item in resolved]
    mu = _mode_of_tau(tau_values)
    porosities = [float(item.get("inject_site", {}).get("porosity_norm", 0.35) or 0.35) for item in resolved]
    sigma = max(1e-9, (sum(porosities) / len(porosities)) / 2.0)
    raw_weights_list = [_gaussian_weight(t, mu, sigma) for t in tau_values]
    raw_weight_sum = sum(raw_weights_list)
    weights = [w / raw_weight_sum for w in raw_weights_list] if raw_weight_sum > 1e-12 else raw_weights_list
    weight_sum = sum(weights)

    slider_factor = _clamp((int(emotional_input or 50)) / 100.0)

    hex_scores = defaultdict(float)
    hex_weight_sums = defaultdict(float)
    hex_inject = {}
    hex_line_composition = defaultdict(lambda: defaultdict(int))
    hex_table_weights = {}
    yin_keys = {"young_yin", "old_yin", "stable_yin"}
    yang_keys = {"old_yang", "new_yang", "stable_yang"}
    yao_keys = {"new_yao", "old_yao", "stable_yao"}
    for item, w in zip(resolved, weights):
        hex_id = int(item.get("hexagram_id") or 0)
        if not hex_id:
            continue
        hex_weight_sums[hex_id] += w
        inject = item.get("inject_site") or {}
        porosity_norm = float(inject.get("porosity_norm", 0.0) or 0.0)
        line_states = item.get("line_states") or []
        line_count = len(line_states) or 6
        yin_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yin_keys)
        yang_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yang_keys)
        yao_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yao_keys)
        hex_line_composition[hex_id]["yin"] += yin_count
        hex_line_composition[hex_id]["yang"] += yang_count
        hex_line_composition[hex_id]["yao"] += yao_count
        hex_line_composition[hex_id]["lines"] += line_count
        if hex_id not in hex_inject:
            hex_inject[hex_id] = {
                "primary_pool": inject.get("primary_pool"),
                "secondary_pool": inject.get("secondary_pool"),
                "porosity": inject.get("porosity"),
                "porosity_norm": inject.get("porosity_norm"),
                "porosity_label": inject.get("porosity_label"),
            }
        raw_weights_map = EMOTIONAL_WEIGHTS.get(str(hex_id), EMOTIONAL_WEIGHTS.get("1", {}))
        if hex_id not in hex_table_weights:
            hex_table_weights[hex_id] = {k: float(raw_weights_map.get(k, 0.0) or 0.0) for k in VEC_KEYS}

        yin_ratio = yin_count / max(1, line_count)
        yang_ratio = yang_count / max(1, line_count)
        yao_ratio = yao_count / max(1, line_count)
        ideal_yin = _clamp(1.0 - slider_factor)
        ideal_yang = _clamp(slider_factor)
        composition_match = _clamp(1.0 - (abs(yin_ratio - ideal_yin) * 0.5 + abs(yang_ratio - ideal_yang) * 0.5 + abs(yao_ratio - 0.25) * 1.0))
        alignment = sum(float(raw_weights_map.get(k, 0.0) or 0.0) for k in VEC_KEYS) / max(1, len(VEC_KEYS))
        hex_score = alignment * (0.3 + composition_match * 0.7)
        hex_score = hex_score * (0.5 + porosity_norm * 0.5)
        hex_score = hex_score * (0.3 + slider_factor * 0.7)
        hex_scores[hex_id] += hex_score * w

    top = sorted(hex_scores.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
    top_lookup = []
    for hex_id, score in top:
        comp = hex_line_composition[hex_id]
        lines = max(1, comp.get("lines", 6))
        top_lookup.append({
            "hexagram_id": hex_id,
            "score": score,
            "weight_sum": hex_weight_sums[hex_id],
            "table_weights": hex_table_weights.get(hex_id),
            "inject_site": hex_inject.get(hex_id),
            "line_composition": {
                "yin_ratio": comp.get("yin", 0) / lines,
                "yang_ratio": comp.get("yang", 0) / lines,
                "yao_ratio": comp.get("yao", 0) / lines,
            },
        })

    record = {
        "emotional_input": emotional_input,
        "slider_factor": slider_factor,
        "tau_stats": {
            "mu": mu,
            "sigma": sigma,
            "min": min(tau_values),
            "max": max(tau_values),
            "mean": sum(tau_values) / max(1, len(tau_values)),
        },
        "weight_stats": {
            "raw_sum": raw_weight_sum,
            "normalized_sum": weight_sum,
            "min": min(weights),
            "max": max(weights),
        },
        "top_hex_scores": top_lookup,
        "consensus_output": consensus,
    }
    return record


def main() -> int:
    out = EXPORT_DIR / "debug_progressive_intents.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for value in range(0, 101, 10):
            record = capture(value)
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"debug_capture={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
