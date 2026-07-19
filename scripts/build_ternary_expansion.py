#!/usr/bin/env python3
"""Build full ternary expansion: 27 trigrams, 729 hexagrams, 5,832 resolved states.

Source of truth: data/hexagram-registry.json (64 canonical hexagrams).
This script derives the full ternary math layer and identifies the canonical subset.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "hexagram-registry.json"
OUTPUT_PATH = ROOT / "scripts" / "ternary_full_expansion.json"


def _ternary_trigram_id(a: int, b: int, c: int) -> int:
    """a=bottom, b=middle, c=top. Returns 0..26."""
    return a + b * 3 + c * 9


def _hexagram_id(lower_id: int, upper_id: int) -> int:
    """upper_id × 27 + lower_id. Returns 0..728."""
    return upper_id * 27 + lower_id


def _vector_to_name(vector: List[int]) -> str:
    """Return name if vector matches a canonical binary trigram, else ''."""
    binary_to_name = {
        (0, 0, 0): "Kun",
        (0, 0, 1): "Zhen",
        (0, 1, 0): "Kan",
        (0, 1, 1): "Dui",
        (1, 0, 0): "Gen",
        (1, 0, 1): "Li",
        (1, 1, 0): "Xun",
        (1, 1, 1): "Qian",
    }
    return binary_to_name.get(tuple(vector), "")


def _vector_to_symbol(vector: List[int]) -> str:
    """Return Unicode symbol if vector matches a canonical binary trigram, else ''."""
    binary_to_symbol = {
        (0, 0, 0): "☷",
        (0, 0, 1): "☳",
        (0, 1, 0): "☵",
        (0, 1, 1): "☱",
        (1, 0, 0): "☶",
        (1, 0, 1): "☲",
        (1, 1, 0): "☴",
        (1, 1, 1): "☰",
    }
    return binary_to_symbol.get(tuple(vector), "")


def _line_name(x: int) -> str:
    if x == 0:
        return "yin"
    if x == 1:
        return "yang"
    return "yao"


def _build_trigram_table() -> Dict[int, Dict[str, Any]]:
    table: Dict[int, Dict[str, Any]] = {}
    for a in [0, 1, 2]:
        for b in [0, 1, 2]:
            for c in [0, 1, 2]:
                tid = _ternary_trigram_id(a, b, c)
                vector = [a, b, c]
                table[tid] = {
                    "trigram_id": tid,
                    "vector": vector,
                    "lines": [_line_name(x) for x in vector],
                    "name": _vector_to_name(vector),
                    "symbol": _vector_to_symbol(vector),
                    "is_canonical": bool(_vector_to_name(vector)),
                }
    return table


def _build_hexagram_table(
    trigrams: Dict[int, Dict[str, Any]], registry: Dict[str, Any]
) -> Dict[int, Dict[str, Any]]:
    # Build canonical lookup by 6-bit binary vector
    canonical_by_vector: Dict[str, int] = {}
    for key, entry in registry.items():
        binary = entry.get("binary", "")
        if len(binary) == 6 and all(ch in "01" for ch in binary):
            canonical_by_vector[binary] = int(key)

    table: Dict[int, Dict[str, Any]] = {}
    for lower_id in range(27):
        for upper_id in range(27):
            hid = _hexagram_id(lower_id, upper_id)
            lower = trigrams[lower_id]
            upper = trigrams[upper_id]
            vector = lower["vector"] + upper["vector"]  # 6-element ternary
            binary = "".join(str(x) for x in vector if x in (0, 1))
            canonical_id = canonical_by_vector.get(binary)
            table[hid] = {
                "hexagram_id": hid,
                "vector": vector,
                "upper_trigram_id": upper_id,
                "lower_trigram_id": lower_id,
                "lines": [_line_name(x) for x in vector],
                "is_canonical": canonical_id is not None,
                "canonical_id": canonical_id,
            }
    return table


def _build_resolved_table(
    hexagrams: Dict[int, Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    phases = [
        {"phase_bits": 0, "phase_temporal": "past", "phase_polarity": "yin", "phase_description": "completed, resolved, memory"},
        {"phase_bits": 1, "phase_temporal": "present", "phase_polarity": "yang", "phase_description": "active, manifest, now"},
        {"phase_bits": 2, "phase_temporal": "future", "phase_polarity": "yao", "phase_description": "potential, emerging, becoming"},
        {"phase_bits": 3, "phase_temporal": "transition", "phase_polarity": "yin-yang", "phase_description": "changing, flux, threshold"},
        {"phase_bits": 4, "phase_temporal": "resolution", "phase_polarity": "yang-yin", "phase_description": "settling, clarity, convergence"},
        {"phase_bits": 5, "phase_temporal": "dissolution", "phase_polarity": "yin-yao", "phase_description": "breaking, releasing, dispersal"},
        {"phase_bits": 6, "phase_temporal": "crystallization", "phase_polarity": "yang-yao", "phase_description": "forming, condensing, structure"},
        {"phase_bits": 7, "phase_temporal": "void", "phase_polarity": "yao-yao", "phase_description": "null, reset, origin"},
    ]
    table: Dict[int, Dict[str, Any]] = {}
    for hid, hex_entry in hexagrams.items():
        for phase in phases:
            key = hid * 8 + phase["phase_bits"]
            table[key] = {
                "resolved_id": key,
                "hexagram_id": hid,
                "phase_bits": phase["phase_bits"],
                "phase_temporal": phase["phase_temporal"],
                "phase_polarity": phase["phase_polarity"],
                "phase_description": phase["phase_description"],
                "vector": hex_entry["vector"],
                "upper_trigram_id": hex_entry["upper_trigram_id"],
                "lower_trigram_id": hex_entry["lower_trigram_id"],
                "is_canonical": hex_entry["is_canonical"],
                "canonical_id": hex_entry.get("canonical_id"),
            }
    return table


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    trigrams = _build_trigram_table()
    hexagrams = _build_hexagram_table(trigrams, registry)
    resolved = _build_resolved_table(hexagrams)

    canonical_count = sum(1 for h in hexagrams.values() if h["is_canonical"])
    ternary_count = sum(1 for h in hexagrams.values() if not h["is_canonical"])
    resolved_count = len(resolved)

    out = {
        "schema_version": "2026-07-18-ternary",
        "total_trigrams": len(trigrams),
        "total_hexagrams": len(hexagrams),
        "total_resolved": resolved_count,
        "canonical_count": canonical_count,
        "ternary_count": ternary_count,
        "trigrams": trigrams,
        "hexagrams": hexagrams,
        "resolved": resolved,
    }

    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Trigrams: {len(trigrams)}")
    print(f"Hexagrams: {len(hexagrams)} ({canonical_count} canonical, {ternary_count} ternary)")
    print(f"Resolved: {resolved_count}")
    print(f"Sample canonical hexagrams:")
    for hid, entry in sorted(hexagrams.items()):
        if entry.get("is_canonical"):
            print(f"  {hid:3d}: {entry['vector']} upper={entry['upper_trigram_id']} lower={entry['lower_trigram_id']} canonical={entry.get('canonical_id')}")
            if sum(1 for h in hexagrams.values() if h.get("is_canonical")) >= 5:
                break


if __name__ == "__main__":
    main()
