#!/usr/bin/env python3
"""Build full 64-hex expansion with skill cards, personalities, and domain-tool routing."""

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "hexagram-registry.json"
INJECT_PATH = ROOT / "data" / "hexagram-injection-sites.json" if (ROOT / "data" / "hexagram-injection-sites.json").exists() else None
WEIGHTS_PATH = ROOT / "data" / "emotional-weights.json"
REFLECTIONS_PATH = ROOT / "data" / "temporal-reflections.json"
OUTPUT_PATH = ROOT / "scripts" / "hexagram_full_expansion.json"

# Load base registry
registry = json.loads(REGISTRY_PATH.read_text())

# Personality/codename mapping by hexagram_id
PERSONALITIES = {
    1: "CREATOR-1",
    2: "KEEPER-2",
    3: "STARTER-3",
    4: "LEARNER-4",
    5: "PATIENT-5",
    6: "ADVERSARY-6",
    7: "COMMANDER-7",
    8: "BONDER-8",
    9: "TAMER-9",
    10: "WALKER-10",
    11: "HARMONIZER-11",
    12: "STANDER-12",
    13: "FELLOW-13",
    14: "RICH-14",
    15: "MODEST-15",
    16: "ENERGIZER-16",
    17: "FOLLOWER-17",
    18: "REPAIRER-18",
    19: "APPROACH-19",
    20: "OBSERVER-20",
    21: "BITING-21",
    22: "GRACER-22",
    23: "SPLITTER-23",
    24: "RETURNER-24",
    25: "INNOCENT-25",
    26: "TAMER-GREAT-26",
    27: "NOURISHER-27",
    28: "OVERWHELMER-28",
    29: "ABYSS-29",
    30: "CLINGER-30",
    31: "INFLUENCER-31",
    32: "DURATION-32",
    33: "RETREATER-33",
    34: "GREAT-POWER-34",
    35: "ADVANCER-35",
    36: "OBSCURER-36",
    37: "FAMILY-37",
    38: "OPPOSER-38",
    39: "OBSTRUCTER-39",
    40: "DELIVERER-40",
    41: "DECREASER-41",
    42: "INCREASER-42",
    43: "BREAKER-43",
    44: "MEETER-44",
    45: "GATHERER-45",
    46: "RISER-46",
    47: "OPPRESSOR-47",
    48: "WELLER-48",
    49: "REVOLVER-49",
    50: "CAULDRON-50",
    51: "AROUSER-51",
    52: "STILLER-52",
    53: "DEVELOPER-53",
    54: "MAIDEN-54",
    55: "ABUNDANT-55",
    56: "WANDERER-56",
    57: "GENTLE-57",
    58: "JOYER-58",
    59: "DISPERSER-59",
    60: "LIMITER-60",
    61: "TRUTH-61",
    62: "SMALL-EXCESS-62",
    63: "AFTER-63",
    64: "BEFORE-64",
}

# Skill-card domains per binary position (1=yang,0=yin) — 6 slots = 6 tool domains
SKILL_CARD_DOMAINS = {
    "1": ["generation", "initiation", "architecture", "deployment", "api-design", "creative"],
    "0": ["integration", "maintenance", "debugging", "refactoring", "stability", "receptive"],
}

# Tool-native mappings for Jarvis
TOOL_NATIVE_MAP = {
    "generation": "codegen",
    "initiation": "scaffold",
    "architecture": "design",
    "deployment": "deploy",
    "api-design": "api",
    "creative": "creative",
    "integration": "integrate",
    "maintenance": "maintain",
    "debugging": "debug",
    "refactoring": "refactor",
    "stability": "stabilize",
    "receptive": "listen",
}

# Phase routing
PHASES = [
    {"bits": 0, "temporal": "past", "polarity": "yin", "description": "completed, resolved, memory"},
    {"bits": 1, "temporal": "present", "polarity": "yang", "description": "active, manifest, now"},
    {"bits": 2, "temporal": "future", "polarity": "yao", "description": "potential, emerging, becoming"},
    {"bits": 3, "temporal": "transition", "polarity": "yin-yang", "description": "changing, flux, threshold"},
    {"bits": 4, "temporal": "resolution", "polarity": "yang-yin", "description": "settling, clarity, convergence"},
    {"bits": 5, "temporal": "dissolution", "polarity": "yin-yao", "description": "breaking, releasing, dispersal"},
    {"bits": 6, "temporal": "crystallization", "polarity": "yang-yao", "description": "forming, condensing, structure"},
    {"bits": 7, "temporal": "void", "polarity": "yao-yao", "description": "null, reset, origin"},
]

# Load optional tables
weights = {}
reflections = {}
inject = {}

try:
    weights = json.loads(WEIGHTS_PATH.read_text())
except Exception:
    pass
try:
    reflections = json.loads(REFLECTIONS_PATH.read_text())
except Exception:
    pass
try:
    if INJECT_PATH and INJECT_PATH.exists():
        inject = json.loads(INJECT_PATH.read_text())
except Exception:
    pass


def skill_cards_for_binary(binary: str):
    cards = []
    for idx, bit in enumerate(binary):
        domain = SKILL_CARD_DOMAINS.get(bit, ["unknown"])[idx % len(SKILL_CARD_DOMAINS.get(bit, ["unknown"]))]
        tool = TOOL_NATIVE_MAP.get(domain, "unknown")
        cards.append({
            "slot": idx + 1,
            "bit": bit,
            "domain": domain,
            "jarvis_tool": tool,
            "symbol": {"1": "{", "0": "["}.get(bit, "?"),
        })
    return cards


def phase_expand(hex_entry, weights_entry, reflections_entry, inject_entry):
    phases = []
    for phase in PHASES:
        phase_entry = {
            "phase_bits": phase["bits"],
            "phase_temporal": phase["temporal"],
            "phase_polarity": phase["polarity"],
            "phase_description": phase["description"],
            "porosity": 0.5,
            "yao_vocabulary": {
                "past": ["old_yin", "stable_yin", "young_yin"],
                "present": ["stable_yao", "old_yao", "new_yao"],
                "future": ["old_yang", "stable_yang", "new_yang"],
            },
            "inject_site": inject_entry or {},
            "training_weight_vectors": weights_entry.get("training_weight_vectors", {}),
            "emotional_deltas": {
                "chaos": 0.0,
                "whimsy": 0.0,
                "darkTone": 0.0,
                "coherence": 0.0,
                "voiceWeight": 0.0,
            },
        }
        if weights_entry:
            phase_entry["emotional_deltas"] = {
                "chaos": float(weights_entry.get("chaos", 0.0) or 0.0),
                "whimsy": float(weights_entry.get("whimsy", 0.0) or 0.0),
                "darkTone": float(weights_entry.get("darkTone", 0.0) or 0.0),
                "coherence": float(weights_entry.get("coherence", 0.0) or 0.0),
                "voiceWeight": float(weights_entry.get("voiceWeight", 0.0) or 0.0),
            }
        phases.append(phase_entry)
    return phases


expansion = []
for h_id_str, entry in registry.items():
    h_id = int(h_id_str)
    binary = entry.get("binary", "")
    personality = PERSONALITIES.get(h_id, f"ENTITY-{h_id}")
    invert_binary = "".join("0" if b == "1" else "1" for b in binary)
    inverted_id = None
    for k, v in registry.items():
        if v.get("binary") == invert_binary:
            inverted_id = int(k)
            break

    hex_entry = {
        "hexagram_id": h_id,
        "name": entry.get("name", ""),
        "chinese": entry.get("chinese", ""),
        "pinyin": entry.get("pinyin", ""),
        "unicode": entry.get("unicode", ""),
        "binary": binary,
        "upper_trigram": entry.get("upper_trigram", ""),
        "lower_trigram": entry.get("lower_trigram", ""),
        "category": entry.get("category", ""),
        "action": entry.get("action", ""),
        "personality": personality,
        "inverted_id": inverted_id,
        "inversion_pair": sorted([h_id, inverted_id]) if inverted_id else None,
        "skill_cards": skill_cards_for_binary(binary),
        "domain_vectors": {
            "sovereign": 0.9 if entry.get("category") == "sovereign" else 0.4,
            "transformer": 0.9 if entry.get("category") == "transformer" else 0.4,
            "dissipator": 0.9 if entry.get("category") == "dissipator" else 0.4,
            "boundary": 0.9 if entry.get("category") == "boundary" else 0.4,
        },
        "phases": phase_expand(
            entry,
            weights.get(h_id_str, {}),
            reflections.get(h_id_str, {}),
            inject.get(h_id_str, {}),
        ),
        "reflections_past": (reflections.get(h_id_str, {}) or {}).get("past", ""),
        "reflections_present": (reflections.get(h_id_str, {}) or {}).get("present", ""),
        "reflections_future": (reflections.get(h_id_str, {}) or {}).get("future", ""),
        "trainingNotes": weights.get(h_id_str, {}).get("trainingNotes", ""),
        "inject_site": inject.get(h_id_str, {}),
    }
    expansion.append(hex_entry)

out = {
    "schema_version": "2026-07-18",
    "total_expanded": len(expansion),
    "total_resolved": len(expansion) * 8,
    "source": "hexagram_full_expansion",
    "expansion": expansion,
}

OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"Wrote {OUTPUT_PATH}")
print(f"Expanded hexagrams: {len(expansion)}")
print(f"Resolved states: {len(expansion)*8}")
print(f"Sample hex 1:")
print(json.dumps(out['expansion'][0], ensure_ascii=False, indent=2))
print("Sample hex 44:")
print(json.dumps(out['expansion'][43], ensure_ascii=False, indent=2))
