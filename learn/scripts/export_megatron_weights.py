"""Deterministic King Wen export for Megatron training.

Exports:
- expanded_source.jsonl : all unrolled hexagram states/vectors/symbols
- resolved_source.jsonl : phase-resolved terminal states
- megatron_weights.csv   : compact parser-ready tensor rows

All data comes from immutable tables via `emotional_engine`.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
EXPORT_DIR = ROOT / "learn" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))

from emotional_engine import VEC_KEYS, collapse_full_128


def _write_jsonl(path: Path, records):
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_csv(path: Path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export(emotional_input: int = 50):
    collapse = collapse_full_128(emotional_input=emotional_input)
    expanded = collapse["expanded"]
    resolved = collapse["resolved"]
    consensus = collapse["consensus"]

    expanded_rows = []
    for item in expanded:
        sym = item["hexagram_symbols"]
        inject = item["inject_site"]
        lines = item["line_states"]
        expanded_rows.append(
            {
                "hexagram_id": item["hexagram_id"],
                "name": sym.get("name"),
                "unicode": sym.get("unicode"),
                "category": sym.get("category"),
                "action": sym.get("action"),
                "upper_trigram": sym.get("upper_trigram"),
                "lower_trigram": sym.get("lower_trigram"),
                "binary_bottom_to_top": sym.get("binary_bottom_to_top"),
                "binary_top_to_bottom": sym.get("binary_top_to_bottom"),
                "primary_pool": inject.get("primary_pool"),
                "secondary_pool": inject.get("secondary_pool"),
                "porosity": inject.get("porosity"),
                "porosity_norm": inject.get("porosity_norm"),
                "porosity_label": inject.get("porosity_label"),
                "line_count": len(lines),
                "line_yao_keys": [ls.get("yao_key") for ls in lines],
                "expanded_vector": item["expanded_vector"],
            }
        )

    resolved_rows = []
    for item in resolved:
        sym = item.get("hexagram_symbols") or {}
        inject = item.get("inject_site") or {}
        resolved_rows.append(
            {
                "hexagram_id": item.get("hexagram_id"),
                "phase_bits": item.get("phase_bits"),
                "phase_temporal": item.get("phase_temporal"),
                "phase_polarity": item.get("phase_polarity"),
                "phase_description": item.get("phase_description"),
                "name": sym.get("name"),
                "unicode": sym.get("unicode"),
                "category": sym.get("category"),
                "action": sym.get("action"),
                "primary_pool": inject.get("primary_pool"),
                "secondary_pool": inject.get("secondary_pool"),
                "porosity": inject.get("porosity"),
                "porosity_norm": inject.get("porosity_norm"),
                "porosity_label": inject.get("porosity_label"),
                "resolved_vector": item.get("resolved_vector"),
                "line_count": len(item.get("line_states") or []),
                "line_yao_keys": [ls.get("yao_key") for ls in (item.get("line_states") or [])],
                "request_text": item.get("request_text"),
                "emotional_input": item.get("emotional_input"),
            }
        )

    megatron_rows = []
    for item in resolved_rows:
        vec = item.get("resolved_vector") or {}
        line_yao_keys = item.get("line_yao_keys") or []
        counts = {
            "young_yin": line_yao_keys.count("young_yin"),
            "old_yin": line_yao_keys.count("old_yin"),
            "stable_yin": line_yao_keys.count("stable_yin"),
            "new_yao": line_yao_keys.count("new_yao"),
            "old_yao": line_yao_keys.count("old_yao"),
            "stable_yao": line_yao_keys.count("stable_yao"),
            "old_yang": line_yao_keys.count("old_yang"),
            "new_yang": line_yao_keys.count("new_yang"),
            "stable_yang": line_yao_keys.count("stable_yang"),
        }
        megatron_rows.append(
            {
                "hexagram_id": item.get("hexagram_id"),
                "phase_bits": item.get("phase_bits"),
                "phase_temporal": item.get("phase_temporal"),
                "porosity": item.get("porosity"),
                "porosity_norm": item.get("porosity_norm"),
                "chaos": vec.get("chaos"),
                "whimsy": vec.get("whimsy"),
                "darkTone": vec.get("darkTone"),
                "coherence": vec.get("coherence"),
                "voiceWeight": vec.get("voiceWeight"),
                "young_yin": counts["young_yin"],
                "old_yin": counts["old_yin"],
                "stable_yin": counts["stable_yin"],
                "new_yao": counts["new_yao"],
                "old_yao": counts["old_yao"],
                "stable_yao": counts["stable_yao"],
                "old_yang": counts["old_yang"],
                "new_yang": counts["new_yang"],
                "stable_yang": counts["stable_yang"],
                "emotional_input": item.get("emotional_input"),
            }
        )

    expanded_path = EXPORT_DIR / "expanded_source.jsonl"
    resolved_path = EXPORT_DIR / "resolved_source.jsonl"
    weights_path = EXPORT_DIR / "megatron_weights.csv"
    _write_jsonl(expanded_path, expanded_rows)
    _write_jsonl(resolved_path, resolved_rows)
    _write_csv(
        weights_path,
        megatron_rows,
        [
            "hexagram_id",
            "phase_bits",
            "phase_temporal",
            "porosity",
            "porosity_norm",
            "chaos",
            "whimsy",
            "darkTone",
            "coherence",
            "voiceWeight",
            "young_yin",
            "old_yin",
            "stable_yin",
            "new_yao",
            "old_yao",
            "stable_yao",
            "old_yang",
            "new_yang",
            "stable_yang",
            "emotional_input",
        ],
    )
    return expanded_path, resolved_path, weights_path, consensus


def main() -> int:
    expanded_path, resolved_path, weights_path, consensus = export(emotional_input=50)
    print(f"expanded_source={expanded_path}")
    print(f"resolved_source={resolved_path}")
    print(f"megatron_weights={weights_path}")
    print(
        f"consensus={consensus['consensus_hexagram_id']} {consensus['consensus_temporal']} "
        f"{consensus['consensus_yao']} intent={consensus['consensus_intent']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
