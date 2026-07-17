r"""Pass 1: full 64-hexagram collapse verification + Jarvis subconscious payload.

Validates in one run:
- All 64 hexagrams present with yin/yang/yao line states
- Porosity, trigrams, Unicode, binary per hexagram
- Past/present/future temporal states captured
- Consensus resolved across all 512 paths
- Payload shape matches Jarvis pause-after-thinking contract

Run from C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES:
  PYTHONPATH=. python3 learn\scripts\test_collapse_full_128.py --emotional-input 50
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import collapse_full_128  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emotional-input", type=int, default=50)
    args = parser.parse_args()

    collapse = collapse_full_128(emotional_input=args.emotional_input)
    expanded = collapse.get("expanded") or []
    resolved = collapse.get("resolved") or []
    consensus = collapse.get("consensus") or {}

    # 1. Top-level shape: 64 expanded, 512 resolved
    assert len(expanded) == 64, f"expanded != 64: {len(expanded)}"
    assert len(resolved) == 512, f"resolved != 512: {len(resolved)}"

    # 2. All hexagram IDs 1..64 present exactly once in expanded
    expanded_ids = {int(item.get("hexagram_id") or 0) for item in expanded}
    assert expanded_ids == set(range(1, 65)), f"missing/duplicate hex_ids: {expanded_ids}"

    # 3. Per-hexagram mandatory fields and yin/yang/yao + past/present/future
    missing_fields = []
    line_state_failures = []
    temporal_failures = []
    trigram_failures = []
    symbol_failures = []

    for item in expanded:
        hid = int(item.get("hexagram_id") or 0)
        symbols = item.get("hexagram_symbols") or {}
        inject = item.get("inject_site") or {}
        lines = item.get("line_states") or []

        # Mandatory identity fields from actual HEXAGRAM_BASE schema
        for field in ["name", "unicode", "upper_trigram", "lower_trigram",
                      "binary_bottom_to_top", "category", "action"]:
            if not symbols.get(field):
                missing_fields.append((hid, field))

        # Trigrams must be non-empty strings
        for trig_field in ["upper_trigram", "lower_trigram"]:
            if not str(symbols.get(trig_field, "")).strip():
                trigram_failures.append((hid, trig_field))

        # Unicode must be present; Chinese is registry-only, not base schema
        if not symbols.get("unicode"):
            symbol_failures.append(hid)

        # Porosity present and numeric
        porosity = inject.get("porosity")
        if porosity is None:
            missing_fields.append((hid, "inject_site.porosity"))
        else:
            try:
                float(porosity)
            except Exception:
                missing_fields.append((hid, "inject_site.porosity.nan"))

        # yin/yang/yao: exactly 6 line states with valid yao_key
        if len(lines) != 6:
            line_state_failures.append((hid, f"line_count={len(lines)}"))
        else:
            for ls in lines:
                yao = str(ls.get("yao_key", "") or "")
                if not any(yao.startswith(prefix) for prefix in ("old_yin", "stable_yin", "young_yin",
                                                                  "old_yang", "stable_yang", "new_yang",
                                                                  "old_yao", "stable_yao", "new_yao")):
                    line_state_failures.append((hid, f"bad_yao={yao}"))

        # Past/present/future: captured in the resolved states for this hexagram
        hex_resolved = [r for r in resolved if int(r.get("hexagram_id") or 0) == hid]
        temporals = {str(r.get("phase_temporal", "") or "") for r in hex_resolved}
        for required in ["past", "present", "future"]:
            if required not in temporals:
                temporal_failures.append((hid, required))

    assert not missing_fields, f"missing fields: {missing_fields[:5]}"
    assert not line_state_failures, f"line state failures: {line_state_failures[:5]}"
    assert not temporal_failures, f"temporal failures: {temporal_failures[:5]}"
    assert not trigram_failures, f"trigram failures: {trigram_failures[:5]}"
    assert not symbol_failures, f"symbol failures: {symbol_failures[:5]}"

    # 4. Consensus must be resolved on real paths
    consensus_hex = int(consensus.get("consensus_hexagram_id") or 0)
    assert consensus_hex in range(1, 65), f"invalid consensus hexagram: {consensus_hex}"
    assert consensus.get("consensus_vector"), "missing consensus_vector"
    assert consensus.get("consensus_intent"), "missing consensus_intent"
    assert consensus.get("consensus_temporal") in (
        "past", "present", "future", "all",
        "resolution", "void", "transition", "dissolution", "crystallization"
    ), f"invalid consensus_temporal: {consensus.get('consensus_temporal')}"

    # 5. Jarvis subconscious pause payload shape
    #    When Jarvis is overwhelmed, it should be able to hand over:
    #    { hexagram_id, consensus_vector, porosity, emotional_input,
    #      resolved_count, top_3_paths, next_action_hint }
    payload = {
        "hexagram_id": consensus_hex,
        "consensus_vector": consensus.get("consensus_vector", {}),
        "consensus_porosity_mean": consensus.get("consensus_porosity_mean"),
        "consensus_temporal": consensus.get("consensus_temporal"),
        "emotional_input": args.emotional_input,
        "resolved_count": len(resolved),
        "top_3_paths": [
            {
                "hexagram_id": int(r.get("hexagram_id") or 0),
                "phase_bits": int(r.get("phase_bits") or 0),
                "phase_temporal": r.get("phase_temporal"),
                "resolved_vector": r.get("resolved_vector"),
                "yao_keys": [ls.get("yao_key") for ls in (r.get("line_states") or [])],
            }
            for r in resolved[:3]
        ],
        "next_action_hint": consensus.get("consensus_intent"),
    }
    assert payload["resolved_count"] == 512
    assert len(payload["top_3_paths"]) == 3

    print("collapse_full_128: PASS")
    print(f"emotional_input={args.emotional_input}")
    print(f"expanded={len(expanded)}, resolved={len(resolved)}")
    print(f"consensus_hexagram={consensus_hex}")
    print(f"consensus_temporal={consensus.get('consensus_temporal')}")
    print(f"consensus_yao={consensus.get('consensus_yao')}")
    print(f"consensus_vector={consensus.get('consensus_vector')}")
    print(f"jarvis_payload={payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
