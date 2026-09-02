#!/usr/bin/env python3
"""Build complete King Wen shotgun expansion JSONL for Megatron training.

Captures ALL tagging/expanding layers from the shotgun blast into one JSONL
row per resolved state. No fields omitted. No mock.

Output schema per row:
  {
    "text": "",
    "label_payload": {
      ...expanded state fields,
      ...shotgun expanded fields,
      ...multi_layer_expand fields,
      ...skill cards,
      ...domain vectors,
      ...jspace projections,
      ...schauberger metrics,
      ...porosity metadata
    }
  }

Count: 64 hexagrams × 8 phases × N inputs = full corpus.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from emotional_engine import expand_hexagram  # noqa: E402
from scripts.full_hexagram_shotgun import (  # noqa: E402
    shotgun_expand,
    _ternary_slot_matrix,
    _personality_subsets_for_slot,
    _expand_729_ternary_line_permutations,
    _build_jspace_projections,
    _compute_schauberger_metrics,
    schauberger_parsing_layers,
    CODER_SPECIALTIES,
    RS3_ACTIONABLES,
    NOMINAL_STATES,
)
from scripts.build_hexagram_skill_cards import skill_cards_for_binary, TOOL_NATIVE_MAP  # noqa: E402
from kingwen_ternary_tables_complete import (  # noqa: E402
    HEXAGRAM_BASE,
    PHASE_INFO,
    EMOTIONAL_WEIGHTS,
    VOICEBOX_VOICE_POOL,
)
from kingwen_train_data.kingwen_quantum_process import _hamiltonian_energy  # noqa: E402

OUT_DIR = ROOT / "kingwen_train_data"
OUT = OUT_DIR / "full_shotgun_expansion_all.jsonl"
INPUTS = [0, 50, 100]


def _vec(vec: dict[str, object], keys: list[str]) -> list[float]:
    return [float(vec.get(k, 0.0) or 0.0) for k in keys]


def _phase_meta(phase_bits: int) -> dict[str, object]:
    return PHASE_INFO.get(phase_bits, {})


def build_record(
    hexagram_id: int,
    phase_bits: int,
    emotional_input: int,
    request_text: str,
    shotgun_cache: dict[str, object] | None = None,
) -> dict[str, object]:
    base = expand_hexagram(hexagram_id, request_text, phase_bits=phase_bits, emotional_input=emotional_input)
    inject = base.get("inject_site") or {}
    vector = base.get("expanded_vector") or {}
    resolved_vector = base.get("resolved_vector") or {}
    hex_data = HEXAGRAM_BASE[hexagram_id]
    category = hex_data.get("category", "")
    action = hex_data.get("action", "")
    binary = hex_data.get("binary_bottom_to_top", "")
    pm = _phase_meta(phase_bits)
    phase_temporal = str(pm.get("temporal", ""))
    phase_polarity = str(pm.get("polarity", ""))
    phase_description = str(pm.get("description", ""))
    training_notes = str((EMOTIONAL_WEIGHTS.get(str(hexagram_id)) or {}).get("trainingNotes", ""))
    hamiltonian = _hamiltonian_energy(
        _vec(resolved_vector, ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]),
        _vec(vector, ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]),
        base.get("line_balance", {}),
    )
    if shotgun_cache is None:
        shotgun_cache = shotgun_expand(request_text, emotional_input=emotional_input)
    expanded_lookup = {int(item.get("hexagram_id") or 0): item for item in shotgun_cache.get("expanded", [])}
    shotgun_hex = expanded_lookup.get(hexagram_id, {})
    ternary_slots = _ternary_slot_matrix(hexagram_id, phase_bits=phase_bits)
    personality_subsets = []
    for slot in ternary_slots:
        personality_subsets.extend(_personality_subsets_for_slot(slot, inject, vector))
    ternary_729 = _expand_729_ternary_line_permutations(hexagram_id, inject)
    jspace = _build_jspace_projections(hexagram_id, vector, inject, request_text)
    schauberger = _compute_schauberger_metrics(
        hexagram_id,
        float(vector.get("chaos", 0.0) or 0.0),
        float(vector.get("whimsy", 0.0) or 0.0),
        float(vector.get("coherence", 0.0) or 0.0),
    )
    schauberger_parsing = schauberger_parsing_layers(
        hexagram_id,
        phase_bits=phase_bits,
        emotional_input=emotional_input,
        line_states=base.get("line_states", []),
    )
    skill_cards = skill_cards_for_binary(binary, category=category)
    domain_vector = {
        "chaos": float(vector.get("chaos", 0.0) or 0.0),
        "whimsy": float(vector.get("whimsy", 0.0) or 0.0),
        "darkTone": float(vector.get("darkTone", 0.0) or 0.0),
        "coherence": float(vector.get("coherence", 0.0) or 0.0),
        "voiceWeight": float(vector.get("voiceWeight", 0.0) or 0.0),
    }
    record = dict(base)
    record.update({
        "text": "",
        "emotional_input": emotional_input,
        "source": "shotgun-full",
        "category": category,
        "action": action,
        "binary": binary,
        "phase_temporal": phase_temporal,
        "phase_polarity": phase_polarity,
        "phase_description": phase_description,
        "training_notes": training_notes,
        "domain_vector": domain_vector,
        "hamiltonian_energy": round(hamiltonian, 6),
        "inject_site": inject,
        "expanded_vector": vector,
        "resolved_vector": resolved_vector,
        "line_states": base.get("line_states", []),
        "line_balance": base.get("line_balance", {}),
        "sample_paths": base.get("sample_paths", []),
        "yao_vocabulary": base.get("yao_vocabulary", {}),
        "pre_slider": base.get("pre_slider"),
        "post_slider": base.get("post_slider"),
        "ternary_slots": ternary_slots,
        "personality_subsets": personality_subsets,
        "ternary_729_permutations_count": len(ternary_729),
        "skill_cards": skill_cards,
        "tool_native_map": TOOL_NATIVE_MAP,
        "avalokiteshvara_arm": jspace.get("avalokiteshvara_arm"),
        "jkd_pedagogy_anchor": jspace.get("jkd_pedagogy_anchor"),
        "quantum_superposition": jspace.get("quantum_superposition"),
        "hermes_layer": jspace.get("hermes_layer"),
        "schauberger_metrics": schauberger,
        "schauberger_parsing": schauberger_parsing,
        "projections": jspace.get("projections"),
        "coder_specialty": CODER_SPECIALTIES[(hexagram_id - 1) % len(CODER_SPECIALTIES)],
        "rs3_actionable": RS3_ACTIONABLES[(hexagram_id - 1) % len(RS3_ACTIONABLES)],
        "nominal_state": NOMINAL_STATES.get(hexagram_id, "recovery/fault_hold"),
        "voice_pool_size": len(VOICEBOX_VOICE_POOL),
    })
    return record


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    total = 0
    distinct_hexagrams = set()
    # One shotgun cache per input is enough; expanded[] carries 64 hex payloads.
    input_cache: dict[int, dict[str, object]] = {}
    for emotional_input in INPUTS:
        input_cache[emotional_input] = shotgun_expand("", emotional_input=emotional_input)

    for emotional_input in INPUTS:
        cache = input_cache[emotional_input]
        for h_id in range(1, 65):
            for phase_bits in range(8):
                record = build_record(h_id, phase_bits, emotional_input, "", shotgun_cache=cache)
                distinct_hexagrams.add(int(record.get("hexagram_id") or h_id))
                lines.append(json.dumps({"text": "", "label_payload": record}, ensure_ascii=False))
                total += 1

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(OUT),
        "total_lines": total,
        "distinct_hexagrams": len(distinct_hexagrams),
        "expected_hexagrams": 64,
        "complete_coverage": len(distinct_hexagrams) == 64,
        "inputs_probed": INPUTS,
        "bytes": OUT.stat().st_size,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
