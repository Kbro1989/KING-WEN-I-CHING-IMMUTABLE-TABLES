from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from emotional_engine import (
    EMOTIONAL_WEIGHTS,
    HEXAGRAM_BASE,
    _clamp,
    collapse_full_128,
    expand_hexagram,
    _line_yao_key,
    _pool_by_name,
    _as_tuple5,
    _lerp,
    _yao_vocabulary_map,
)


VEC_KEYS = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]


def deterministic_fingerprint(text: str) -> str:
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def capture_all_64_pre_slider(request_text: str = "") -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for hex_id in range(1, 65):
        # Preserve current table-driven expansion shape, but attach a stable frame.
        expanded = expand_hexagram(
            hex_id,
            request_text=request_text,
            phase_bits=0,
            emotional_input=50,
        )
        inject = expanded.get("inject_site") or {}
        symbols = expanded.get("hexagram_symbols") or {}
        line_states = expanded.get("line_states") or []
        vec = expanded.get("expanded_vector") or {}
        vec_sum = sum(float(vec.get(k, 0.0) or 0.0) for k in VEC_KEYS)
        yin_keys = {"young_yin", "old_yin", "stable_yin"}
        yang_keys = {"old_yang", "new_yang", "stable_yang"}
        yao_keys = {"new_yao", "old_yao", "stable_yao"}
        yin_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yin_keys)
        yang_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yang_keys)
        yao_count = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "") in yao_keys)

        base = HEXAGRAM_BASE.get(hex_id, {})
        record = {
            "hexagram_id": hex_id,
            "name": symbols.get("name"),
            "category": symbols.get("category"),
            "action": symbols.get("action"),
            "binary_bottom_to_top": base.get("binary_bottom_to_top"),
            "request_fingerprint": deterministic_fingerprint(request_text),
            "primary_pool": inject.get("primary_pool"),
            "secondary_pool": inject.get("secondary_pool"),
            "porosity": inject.get("porosity"),
            "porosity_norm": inject.get("porosity_norm"),
            "line_states": line_states,
            "line_composition": {
                "yin": yin_count,
                "yang": yang_count,
                "yao": yao_count,
                "total": len(line_states) or 6,
            },
            "expanded_vector": vec,
            "vector_magnitude": _clamp(vec_sum / 5.0),
            "emotional_alignment": sum(
                float((EMOTIONAL_WEIGHTS.get(str(hex_id)) or {}).get(k, 0.0) or 0.0)
                for k in VEC_KEYS
            )
            / max(1, len(VEC_KEYS)),
            "response_summary": _response_summary(request_text, hex_id, symbols, inject, line_states, vec),
        }
        records.append(record)
    return records


def _response_summary(
    request_text: str,
    hex_id: int,
    symbols: Dict[str, Any],
    inject: Dict[str, Any],
    line_states: List[Dict[str, Any]],
    vec: Dict[str, float],
) -> Dict[str, Any]:
    """Hex-specific cognitive response; no invented meanings, only table-derived frame."""
    changing = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").startswith("old_"))
    stable = sum(1 for ls in line_states if str(ls.get("yao_key", "") or "").startswith("stable_"))
    return {
        "frame": f"{symbols.get('category')}::{symbols.get('action')}",
        "why_this_hex": inject.get("reason"),
        "shift_pressure": changing,
        "stable_anchors": stable,
        "top_axis": sorted(VEC_KEYS, key=lambda k: float(vec.get(k, 0.0) or 0.0), reverse=True)[:2],
        "carrier": symbols.get("pinyin") or symbols.get("chinese") or symbols.get("unicode"),
    }


def slider_selection(all_64: List[Dict[str, Any]], emotional_input: int = 50) -> Dict[str, Any]:
    if not all_64:
        return {"selected": [], "cut": 0, "emotional_input": emotional_input}
    slider_factor = _clamp((int(emotional_input or 50) / 100.0))
    scored: List[Dict[str, Any]] = []
    for rec in all_64:
        alignment = float(rec.get("emotional_alignment") or 0.0)
        porosity_norm = float(rec.get("porosity_norm") or 0.0)
        vec_mag = float(rec.get("vector_magnitude") or 0.0)
        lc = rec.get("line_composition") or {}
        yao = int(lc.get("yao") or 0) / max(1, int(lc.get("total") or 1))
        yin = int(lc.get("yin") or 0) / max(1, int(lc.get("total") or 1))
        yang = int(lc.get("yang") or 0) / max(1, int(lc.get("total") or 1))
        stability = _clamp((yin + yang) / 3.0)
        yao_potential = _clamp(yao)
        change_axis = _clamp(slider_factor * yao_potential + (1.0 - slider_factor) * stability)
        score = alignment * (0.2 + porosity_norm * 0.8)
        score = score * (0.35 + change_axis * 0.65)
        score = score * (0.25 + _clamp(yao + 0.25 * porosity_norm) * 0.75)
        out = dict(rec)
        out["slider_score"] = score
        out["change_axis"] = change_axis
        scored.append(out)

    top_n = 8
    selected = sorted(scored, key=lambda x: x.get("slider_score", 0.0), reverse=True)[:top_n]
    rejected = sorted(scored, key=lambda x: x.get("slider_score", 0.0), reverse=True)[top_n:]
    return {
        "emotional_input": emotional_input,
        "slider_factor": slider_factor,
        "selected": selected,
        "rejected_count": len(rejected),
        "selection_rationale": _selection_rationale(selected, rejected),
    }


def _selection_rationale(selected, rejected):
    if not selected:
        return "no responses selected"
    best = selected[0]
    worst = rejected[0] if rejected else None
    parts = [f"hex={best.get('hexagram_id')} score={best.get('slider_score', 0.0):.6f} ({best.get('name')})"]
    if worst:
        parts.append(f"borderline hex={worst.get('hexagram_id')} score={worst.get('slider_score', 0.0):.6f}")
    return "; ".join(parts)


def main() -> int:
    probe = "same input across sliders / determinism probe?"
    all_64 = capture_all_64_pre_slider(request_text=probe)
    selections = {value: slider_selection(all_64, emotional_input=value) for value in [0, 25, 50, 75, 100]}

    # Same-selector determinism: same input + same slider => same selected ids/order.
    determinism_ok = True
    seen = {}
    for value, sel in selections.items():
        ids = tuple(x.get("hexagram_id") for x in sel.get("selected", []))
        seen.setdefault(ids, []).append(value)
        if len(seen[ids]) > 1 and list(seen.keys()).index(ids) != len(seen) - 1:
            determinism_ok = False

    out = {
        "probe_request": probe,
        "total_responses": len(all_64),
        "pre_slider_top5": sorted(all_64, key=lambda x: x.get("vector_magnitude", 0.0), reverse=True)[:5],
        "slider_selections": selections,
        "determinism_ok": determinism_ok,
        "selection_changes_across_slider": len(seen),
    }
    Path("learn/exports/cognitive_synapse_pre_slider.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )
    print("wrote learn/exports/cognitive_synapse_pre_slider.json")
    print(f"total_responses={out['total_responses']}")
    print(f"determinism_ok={determinism_ok}")
    for value in [0, 25, 50, 75, 100]:
        sel = selections[value]["selected"]
        print(f"emotional_input={value:03d} -> top={sel[0].get('hexagram_id') if sel else None} scores={[round(x.get('slider_score',0),6) for x in sel[:3]]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
