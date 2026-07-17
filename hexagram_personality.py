"""Hexagram personality and agent-type layer.

Uses ONLY the immutable table tags as baseline, repeated per hexagram per slot.
No synthetic normalization across truth sources.

Source tags from immutable tables:
- category: sovereign/transformer/dissipator/boundary
- action: ASSERT/YIELD/ADAPT/WAIT
- upper_trigram/lower_trigram: name, nature, attribute
- binary_bottom_to_top: 6-bit string, 0/1 per slot
- phase_bits: 3-bit temporal selector

Per-slot personality: each binary position carries the tag of the bit value
at that position, repeated across all 64 hexagrams using the same baseline.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from emotional_engine import (
    VEC_KEYS,
    collapse_full_128,
    expand_hexagram,
    sample_resolve,
    _clamp,
)

# ---------------------------------------------------------------------------
# Source of truth: immutable table tags only
# ---------------------------------------------------------------------------
# These are REPEATED per hexagram, not normalized across sources.

# Category -> agent type mapping from immutable tables
CATEGORY_AGENT_TYPE: Dict[str, str] = {
    "sovereign": "architect",
    "transformer": "integrator",
    "dissipator": "navigator",
    "boundary": "guardian",
}

# Action -> domain mapping from immutable tables
ACTION_DOMAIN: Dict[str, str] = {
    "ASSERT": "assertion",
    "YIELD": "reception",
    "ADAPT": "adaptation",
    "WAIT": "patience",
}

# Trigram nature -> element subset from immutable tables
TRIGRAM_ELEMENT: Dict[str, str] = {
    "Qian": "heaven",
    "Kun": "earth",
    "Zhen": "thunder",
    "Kan": "water",
    "Li": "fire",
    "Xun": "wind",
    "Gen": "mountain",
    "Dui": "lake",
}

# ---------------------------------------------------------------------------
# Per-slot binary personality: repeat baseline per position
# ---------------------------------------------------------------------------
def slot_personality(bit_value: int, position: int, upper_bits: str, lower_bits: str) -> Dict[str, Any]:
    """Return personality tags for a single binary slot.

    Baseline is the bit value + position. Repeated per hexagram.
    No normalization across truth sources.
    """
    is_upper = position <= 3
    trigram_bits = upper_bits if is_upper else lower_bits
    trigram_pos = position if is_upper else position - 3
    trigram_name_map = {"000": "Kun", "001": "Gen", "010": "Kan", "011": "Xun",
                        "100": "Zhen", "101": "Li", "110": "Dui", "111": "Qian"}
    trigram_name = trigram_name_map.get(trigram_bits, "unknown")

    return {
        "position": position,
        "bit_value": bit_value,
        "is_yin": bit_value == 0,
        "is_yang": bit_value == 1,
        "trigram_bits": trigram_bits,
        "trigram_name": trigram_name,
        "trigram_position": trigram_pos,
        "element_subset": TRIGRAM_ELEMENT.get(trigram_name, "unknown"),
        "slots_repeat_baseline": True,
    }

# ---------------------------------------------------------------------------
# Hexagram personality from immutable table tags
# ---------------------------------------------------------------------------
def hexagram_tags_from_table(hexagram_id: int) -> Dict[str, Any]:
    """Extract personality tags directly from immutable table data.

    No synthesis. No normalization. Just the table's own tags.
    """
    try:
        from kingwen_ternary_tables_complete import HEXAGRAM_BASE  # type: ignore
    except ImportError:
        try:
            from KING_WEN_TABLES import HEXAGRAMS  # type: ignore
            hex_data = HEXAGRAMS[hexagram_id - 1]
        except Exception:
            return {"hexagram_id": hexagram_id, "source": "missing"}
    else:
        hex_data = HEXAGRAM_BASE.get(hexagram_id, {})

    binary = hex_data.get("binary_bottom_to_top", "")
    if not binary:
        return {"hexagram_id": hexagram_id, "source": "missing_binary"}

    upper_bits = binary[:3]
    lower_bits = binary[3:]

    # Table tags - repeated baseline, not normalized
    category = hex_data.get("category", "")
    action = hex_data.get("action", "")
    upper_trigram = hex_data.get("upper_trigram", "")
    lower_trigram = hex_data.get("lower_trigram", "")

    # Agent type from category tag
    agent_type = CATEGORY_AGENT_TYPE.get(category, "unknown")

    # Domain from action tag
    domain = ACTION_DOMAIN.get(action, "unknown")

    # Per-slot tags - repeat baseline for each position
    slot_tags = []
    for pos, bit_char in enumerate(binary, 1):
        bit = int(bit_char)
        slot_tags.append(slot_personality(bit, pos, upper_bits, lower_bits))

    return {
        "hexagram_id": hexagram_id,
        "binary": binary,
        "source": "immutable_table",
        "category": category,
        "action": action,
        "agent_type": agent_type,
        "domain": domain,
        "upper_trigram": upper_trigram,
        "lower_trigram": lower_trigram,
        "element_subset": TRIGRAM_ELEMENT.get(upper_trigram, "unknown"),
        "slot_tags": slot_tags,
        "slots_repeat_baseline": True,
    }

# ---------------------------------------------------------------------------
# Build full personality map from table tags
# ---------------------------------------------------------------------------
def build_hexagram_personality_map() -> Dict[int, Dict[str, Any]]:
    """Build personality map for all 64 hexagrams from immutable table tags."""
    mapping: Dict[int, Dict[str, Any]] = {}
    for h_id in range(1, 65):
        tags = hexagram_tags_from_table(h_id)
        if tags.get("source") == "missing_binary":
            continue
        mapping[h_id] = tags
    return mapping

HEXAGRAM_PERSONALITY_MAP = build_hexagram_personality_map()

# ---------------------------------------------------------------------------
# Consensus-based personality resolver using table tags
# ---------------------------------------------------------------------------
def resolve_personality_by_consensus(
    resolved: List[Dict[str, Any]],
    consensus_vector: Dict[str, float],
) -> Dict[str, Any]:
    """Resolve active personalities using consensus weights + table tags.

    No synthetic normalization. Uses actual table tags per hexagram.
    """
    if not resolved:
        return {"dominant_agent_type": "unknown", "dominant_domain": "unknown", "slot_tags": []}

    # Aggregate agent types and domains from table tags
    agent_scores: Dict[str, float] = {}
    domain_scores: Dict[str, float] = {}
    slot_tag_accum: Dict[int, Dict[str, Any]] = {}

    for item in resolved:
        h_id = int(item.get("hexagram_id") or 0)
        if not h_id:
            continue
        rv = item.get("resolved_vector") or {}
        vec_mag = sum(float(rv.get(k, 0.0) or 0.0) for k in VEC_KEYS)

        tags = HEXAGRAM_PERSONALITY_MAP.get(h_id, {})
        agent_type = tags.get("agent_type", "unknown")
        domain = tags.get("domain", "unknown")

        agent_scores[agent_type] = agent_scores.get(agent_type, 0.0) + vec_mag
        domain_scores[domain] = domain_scores.get(domain, 0.0) + vec_mag

        # Accumulate slot tags
        for slot in tags.get("slot_tags", []):
            pos = slot.get("position", 0)
            if pos not in slot_tag_accum:
                slot_tag_accum[pos] = {"count": 0, "bits": defaultdict(int), "trigrams": defaultdict(int)}
            slot_tag_accum[pos]["count"] += 1
            slot_tag_accum[pos]["bits"][slot.get("bit_value", 0)] += 1
            slot_tag_accum[pos]["trigrams"][slot.get("trigram_name", "unknown")] += 1

    # Top agent type and domain from table tags
    dominant_agent = max(agent_scores, key=agent_scores.__getitem__) if agent_scores else "unknown"
    dominant_domain = max(domain_scores, key=domain_scores.__getitem__) if domain_scores else "unknown"

    # Slot distribution: repeat baseline per position
    slot_distribution = {}
    for pos, accum in sorted(slot_tag_accum.items()):
        total = accum["count"] or 1
        bit_dist = {k: v / total for k, v in accum["bits"].items()}
        trigram_dist = {k: v / total for k, v in accum["trigrams"].items()}
        slot_distribution[pos] = {
            "bit_distribution": bit_dist,
            "dominant_trigram": max(trigram_dist, key=trigram_dist.__getitem__) if trigram_dist else "unknown",
            "trigram_distribution": trigram_dist,
        }

    return {
        "dominant_agent_type": dominant_agent,
        "agent_distribution": dict(sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)[:8]),
        "dominant_domain": dominant_domain,
        "domain_distribution": dict(sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[:8]),
        "slot_distribution": slot_distribution,
        "source": "immutable_table_tags",
    }

# ---------------------------------------------------------------------------
# Full expansion with table-tag personality layer
# ---------------------------------------------------------------------------
def expand_with_personality(emotional_input: int = 50, request_text: str = "") -> Dict[str, Any]:
    """Full 64-hex expansion with table-tag personality layer.

    Adds per-slot binary tags from immutable tables, repeated baseline.
    """
    base = collapse_full_128(emotional_input=emotional_input, request_text=request_text)
    resolved = base.get("resolved", [])
    consensus = base.get("consensus", {})

    # Resolve personalities from consensus weights + table tags
    personality = resolve_personality_by_consensus(
        resolved,
        consensus.get("consensus_vector", {}),
    )

    # Add table-tag slot metadata to each resolved state
    for item in resolved:
        h_id = int(item.get("hexagram_id") or 0)
        binary = item.get("hexagram_symbols", {}).get("binary", "")
        if h_id and binary and len(binary) == 6:
            tags = HEXAGRAM_PERSONALITY_MAP.get(h_id, {})
            item["table_tags"] = {
                "category": tags.get("category", ""),
                "action": tags.get("action", ""),
                "agent_type": tags.get("agent_type", ""),
                "domain": tags.get("domain", ""),
                "upper_trigram": tags.get("upper_trigram", ""),
                "lower_trigram": tags.get("lower_trigram", ""),
            }
            item["slot_tags"] = tags.get("slot_tags", [])

    base["personality_layer"] = personality
    base["table_tag_count"] = sum(1 for h_id in HEXAGRAM_PERSONALITY_MAP if h_id > 0)
    return base

# ---------------------------------------------------------------------------
# Quick verification
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    out = expand_with_personality(emotional_input=50)
    print(f"total_resolved: {out.get('total_resolved')}")
    print(f"consensus_hexagram: {out.get('consensus', {}).get('consensus_hexagram_id')}")
    print(f"dominant_agent_type: {out.get('personality_layer', {}).get('dominant_agent_type')}")
    print(f"dominant_domain: {out.get('personality_layer', {}).get('dominant_domain')}")
    print(f"table_tag_count: {out.get('table_tag_count')}")
    print(f"slot_positions: {sorted(out.get('personality_layer', {}).get('slot_distribution', {}).keys())}")

    # Verify hex 1 and 2 use only table tags
    for h_id in [1, 2]:
        tags = HEXAGRAM_PERSONALITY_MAP.get(h_id, {})
        print(f"\nhex{h_id:02d}: category={tags.get('category')} action={tags.get('action')} agent={tags.get('agent_type')} domain={tags.get('domain')}")
        print(f"  slot_tags_count={len(tags.get('slot_tags', []))}")
        if tags.get('slot_tags'):
            print(f"  slot1={tags['slot_tags'][0]}")
