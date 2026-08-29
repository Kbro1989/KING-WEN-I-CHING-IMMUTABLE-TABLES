#!/usr/bin/env python3
"""Enrich 64 King Wen Kit models (kit_1.json .. kit_64.json) with grounded NPC metadata.

Incorporate:
1. Systematic persona tagging (agent_type, domain, element_subset, codename)
2. Input tagging (intent categories, trigger domains, legal crosswalks)
3. Output tagging (sovereign action, Hermes VHDL voice mode, TTS speaker hints, Schauberger motion)
4. Quantitative paired differentials (dy_yang_yin, yao_dy, changing_dy) & 5-axis emotional vectors
5. Structured `grounded_npc` block + enriched `extra` key-value array
"""

import json
import sys
from typing import Any, Dict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS
from emotional_engine import expand_hexagram, _line_state_vector
from hexagram_personality import HEXAGRAM_PERSONALITY_MAP
from scripts.full_hexagram_shotgun import CODER_SPECIALTIES, RS3_ACTIONABLES, NOMINAL_STATES, _compute_schauberger_metrics
from scripts.build_hexagram_skill_cards import PERSONALITIES, skill_cards_for_binary

KIT_DIR = ROOT / "DATASETS" / "kingwen_model_sets"


def enrich_kit_file(hex_id: int) -> Dict[str, Any]:
    kit_path = KIT_DIR / f"kit_{hex_id}.json"
    if not kit_path.exists():
        print(f"Skipping missing kit_{hex_id}.json")
        return {}

    kit_data = json.loads(kit_path.read_text(encoding="utf-8"))

    # Load baseline expansion
    base_exp = expand_hexagram(hex_id, request_text="kit model grounding", phase_bits=0, emotional_input=50)
    symbols = HEXAGRAM_BASE.get(hex_id, {})
    pers = HEXAGRAM_PERSONALITY_MAP.get(hex_id, {})

    category = symbols.get("category", "")
    action = symbols.get("action", "")
    binary = symbols.get("binary_bottom_to_top", "")

    agent_type = pers.get("agent_type", "unknown")
    domain = pers.get("domain", "unknown")
    element_subset = pers.get("element_subset", "unknown")

    coder_specialty = CODER_SPECIALTIES[(hex_id - 1) % len(CODER_SPECIALTIES)]
    rs3_actionable = RS3_ACTIONABLES[(hex_id - 1) % len(RS3_ACTIONABLES)]
    codename = PERSONALITIES.get(hex_id, f"ENTITY-{hex_id}")

    # Vectors & differentials
    exp_vec = base_exp.get("expanded_vector", {})
    lb = base_exp.get("line_balance", {})
    yin_c = float(lb.get("yin_count", 0) or 0)
    yang_c = float(lb.get("yang_count", 0) or 0)
    yao_c = float(lb.get("yao_count", 0) or 0)
    ch_c = float(lb.get("changing_count", 0) or 0)

    dy_yang_yin = yang_c - yin_c
    yao_dy = yao_c - 3.0
    changing_dy = ch_c - (6.0 - ch_c)

    # Schauberger & Hermes
    chaos = float(exp_vec.get("chaos", 0.1))
    whimsy = float(exp_vec.get("whimsy", 0.2))
    coherence = float(exp_vec.get("coherence", 0.85))
    schauberger = _compute_schauberger_metrics(hex_id, chaos, whimsy, coherence)
    hermes_mode = NOMINAL_STATES.get(hex_id, "recovery/fault_hold")

    # Skill cards (Input/Domain trigger tags)
    cards = skill_cards_for_binary(binary, category)
    input_tags = list(dict.fromkeys([c["domain"] for c in cards]))

    # Speaker hint
    voice_weight = float(exp_vec.get("voiceWeight", 0.5))
    dark_tone = float(exp_vec.get("darkTone", 0.1))
    if voice_weight > 0.90:
        tts_speaker = "qwen_custom_voice"
    elif coherence > 0.90:
        tts_speaker = "kokoro"
    elif dark_tone > 0.50:
        tts_speaker = "chatterbox_turbo"
    else:
        tts_speaker = "qwen"

    output_tags = [action, category, agent_type, domain, tts_speaker, hermes_mode, schauberger["motion_type"]]

    # Build `grounded_npc` object
    grounded_npc = {
        "hexagram_id": hex_id,
        "name": symbols.get("name", ""),
        "codename": codename,
        "unicode": symbols.get("unicode", ""),
        "binary": binary,
        "category": category,
        "action": action,
        "agent_type": agent_type,
        "domain": domain,
        "element_subset": element_subset,
        "coder_specialty": coder_specialty,
        "rs3_actionable": rs3_actionable,
        "hermes_voice_mode": hermes_mode,
        "tts_speaker_hint": tts_speaker,
        "schauberger": schauberger,
        "input_tags": input_tags,
        "output_tags": output_tags,
        "baseline_vector": {
            "chaos": round(chaos, 4),
            "whimsy": round(whimsy, 4),
            "darkTone": round(dark_tone, 4),
            "coherence": round(coherence, 4),
            "voiceWeight": round(voice_weight, 4),
        },
        "paired_differentials": {
            "dy_yang_yin": round(dy_yang_yin, 2),
            "yao_dy": round(yao_dy, 2),
            "changing_dy": round(changing_dy, 2),
        },
        "skill_cards": cards,
    }

    kit_data["grounded_npc"] = grounded_npc

    # Update or add entries to `extra` array for backward compatibility
    extra_map = {item["key"]: item for item in kit_data.get("extra", []) if isinstance(item, dict) and "key" in item}

    # Helper to set extra entry
    def set_extra(key: str, str_val: str = None, int_val: int = 0):
        if key in extra_map:
            if str_val is not None:
                extra_map[key]["stringvalue"] = str_val
            if int_val is not None:
                extra_map[key]["intvalue"] = int_val
        else:
            new_item = {"type": 0, "key": key, "intvalue": int_val or 0, "stringvalue": str_val}
            kit_data.setdefault("extra", []).append(new_item)
            extra_map[key] = new_item

    set_extra("category", str_val=category)
    set_extra("action", str_val=action)
    set_extra("agent_type", str_val=agent_type)
    set_extra("domain", str_val=domain)
    set_extra("element_subset", str_val=element_subset)
    set_extra("coder_specialty", str_val=coder_specialty)
    set_extra("rs3_actionable", str_val=rs3_actionable)
    set_extra("personality_codename", str_val=codename)
    set_extra("hermes_voice_mode", str_val=hermes_mode)
    set_extra("motion_type", str_val=schauberger["motion_type"])
    set_extra("input_tags", str_val="|".join(input_tags))
    set_extra("output_tags", str_val="|".join(output_tags))
    set_extra("tts_speaker_hint", str_val=tts_speaker)

    # Convert floats to 10000-based fixed point ints for vector extras
    set_extra("chaos", int_val=int(chaos * 10000))
    set_extra("whimsy", int_val=int(whimsy * 10000))
    set_extra("darkTone", int_val=int(dark_tone * 10000))
    set_extra("coherence", int_val=int(coherence * 10000))
    set_extra("voiceWeight", int_val=int(voice_weight * 10000))

    # Deduplicate extra array to unique keys only
    kit_data["extra"] = list(extra_map.values())

    kit_path.write_text(json.dumps(kit_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return grounded_npc


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 80)
    print("ENRICHING 64 KING WEN KIT MODELS WITH GROUNDED MODEL NPC IN/OUT TAGS")
    print("=" * 80)

    enriched_count = 0
    for h_id in range(1, 65):
        npc = enrich_kit_file(h_id)
        if npc:
            enriched_count += 1

    print(f"\nSuccessfully enriched {enriched_count}/64 Kit models in {KIT_DIR}!")
    print("\nSample Enriched Kit #1 (The Creative / Architect):")
    sample_path = KIT_DIR / "kit_1.json"
    sample_json = json.loads(sample_path.read_text(encoding="utf-8"))
    sample_str = json.dumps({
        "kit_id": sample_json.get("kit_id"),
        "grounded_npc": sample_json.get("grounded_npc"),
        "extra_sample": sample_json.get("extra")[:8],
    }, indent=2)
    print(sample_str)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
