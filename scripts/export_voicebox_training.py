#!/usr/bin/env python3
"""King Wen -> Voicebox training-data exporter.

Reads collapse_full_128() output or live engine state and emits:
- voicebox_training_vector.json   : 5-axis vector metadata for all 512 states
- voicebox_profile_payload.json   : profile-like payloads keyed by hexagram+phase
- voicebox_export_bundle.zip      : optional Voicebox-compatible ZIP with samples/manifest

Source of truth: C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
Voicebox target:  C:/Users/krist/Desktop/voicebox
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT_KINGWEN = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
ROOT_VOICEBOX = Path(r"C:/Users/krist/Desktop/voicebox")
sys.path.insert(0, str(ROOT_KINGWEN))

from emotional_engine import collapse_full_128, EMOTIONAL_POOL  # noqa: E402


def _vector_mean(resolved: list[dict[str, Any]]) -> dict[str, float]:
    vals = {k: 0.0 for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]}
    for item in resolved:
        rv = item.get("resolved_vector") or {}
        for k in vals:
            vals[k] += float(rv.get(k, 0.0))
    n = float(len(resolved)) or 1.0
    return {k: round(v / n, 6) for k, v in vals.items()}


def build_training_vector(emotional_input: int = 50) -> dict:
    collapse = collapse_full_128(emotional_input=emotional_input)
    resolved = collapse.get("resolved") or []
    expanded = collapse.get("expanded") or []
    consensus = collapse.get("consensus") or {}

    by_hex: dict[int, list[dict]] = {}
    for item in resolved:
        hid = int(item.get("hexagram_id") or 0)
        by_hex.setdefault(hid, []).append(item)

    vector_rows = []
    profile_payloads = []
    for item in expanded:
        hid = int(item.get("hexagram_id") or 0)
        inject = item.get("inject_site") or {}
        hex_resolved = by_hex.get(hid, [])
        vec_mean = _vector_mean(hex_resolved)
        vector_rows.append({
            "hexagram_id": hid,
            "phase_bits": 8,
            "emotional_input": emotional_input,
            "inject_site": inject,
            "vector_mean": vec_mean,
            "resolved_count": len(hex_resolved),
        })
        profile_payloads.append({
            "profile_id": f"kingwen-hex-{hid:02d}",
            "name": item.get("name"),
            "hexagram_id": hid,
            "unicode": item.get("unicode"),
            "instruct": _build_instruct(item, vec_mean),
            "design_prompt": _build_design_prompt(item, inject, vec_mean),
            "voice_type": "designed",
            "preset_engine": _select_preset_engine(inject, vec_mean),
            "preset_voice_id": _select_preset_voice_id(inject, vec_mean),
            "personality": _build_personality(item, inject, vec_mean),
            "source": "kingwen-collapse-full-128",
            "consensus_vector": vec_mean,
        })

    return {
        "source": "kingwen-voicebox-export",
        "emotional_input": emotional_input,
        "total_expanded": len(expanded),
        "total_resolved": len(resolved),
        "consensus": {
            "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
            "consensus_temporal": consensus.get("consensus_temporal"),
            "consensus_vector": consensus.get("consensus_vector"),
            "consensus_intent": consensus.get("consensus_intent"),
        },
        "vector_rows": vector_rows,
        "profile_payloads": profile_payloads,
    }


def _build_instruct(item: dict, vec_mean: dict) -> str:
    parts = [
        f"kingwen_hex={item.get('hexagram_id')}",
        f"temporal={item.get('phase_temporal', 'present')}",
        f"chaos={vec_mean['chaos']:.3f}",
        f"whimsy={vec_mean['whimsy']:.3f}",
        f"darkTone={vec_mean['darkTone']:.3f}",
        f"coherence={vec_mean['coherence']:.3f}",
        f"voiceWeight={vec_mean['voiceWeight']:.3f}",
    ]
    return " | ".join(parts)


def _build_design_prompt(item: dict, inject: dict, vec_mean: dict) -> str:
    primary = inject.get("primary_pool", "unknown")
    secondary = inject.get("secondary_pool", "unknown")
    porosity = inject.get("porosity", "?")
    reason = inject.get("reason", "")
    return (
        f"Voice shaped by hexagram {item.get('hexagram_id')} "
        f"{item.get('name')}: primary pool {primary}, secondary {secondary}, "
        f"porosity {porosity}. {reason}. "
        f"Express chaos={vec_mean['chaos']:.3f}, whimsy={vec_mean['whimsy']:.3f}, "
        f"darkTone={vec_mean['darkTone']:.3f}, coherence={vec_mean['coherence']:.3f}, "
        f"voiceWeight={vec_mean['voiceWeight']:.3f}."
    )


def _select_preset_engine(inject: dict, vec_mean: dict) -> str | None:
    porosity = int(inject.get("porosity") or 0)
    if vec_mean.get("voiceWeight", 0) > 0.9 and porosity <= 1:
        return "qwen_custom_voice"
    if vec_mean.get("coherence", 0) > 0.9:
        return "kokoro"
    if vec_mean.get("darkTone", 0) > 0.5:
        return "chatterbox_turbo"
    return "qwen"


def _select_preset_voice_id(inject: dict, vec_mean: dict) -> str | None:
    engine = _select_preset_engine(inject, vec_mean)
    if engine == "qwen_custom_voice":
        return "default_voice_id"
    if engine == "kokoro":
        return "default"
    return None


def _build_personality(item: dict, inject: dict, vec_mean: dict) -> str | None:
    parts = [
        f"You are the voice of hexagram {item.get('hexagram_id')} {item.get('name')}.",
        f"Your tone is shaped by pools {inject.get('primary_pool')} and {inject.get('secondary_pool')}.",
        f"Porosity {inject.get('porosity')} governs how much outside emotion passes through you.",
    ]
    if vec_mean.get("whimsy", 0) > 0.5:
        parts.append("You speak with playful curiosity.")
    if vec_mean.get("darkTone", 0) > 0.5:
        parts.append("You speak with dark, grounded weight.")
    if vec_mean.get("coherence", 0) > 0.85:
        parts.append("You are precise and tightly coherent.")
    return " ".join(parts)


def write_vector_json(payload: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "voicebox_training_vector.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_profile_payloads(payload: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "voicebox_profile_payload.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_voicebox_zip(payload: dict, out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "voicebox_export_bundle.zip"
    profiles = payload.get("profile_payloads", [])
    if not profiles:
        return None
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        manifest = {
            "version": "1.0",
            "source": payload.get("source"),
            "emotional_input": payload.get("emotional_input"),
            "profile_count": len(profiles),
            "consensus": payload.get("consensus"),
        }
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        samples = {}
        for profile in profiles[:8]:
            profile_id = profile["profile_id"]
            samples[f"{profile_id}.wav"] = profile.get("design_prompt", "")
            zf.writestr(
                f"samples/{profile_id}.wav",
                json.dumps({"profile_id": profile_id, "text": profile.get("design_prompt")}, ensure_ascii=False),
            )
        zf.writestr("samples.json", json.dumps(samples, ensure_ascii=False, indent=2))
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emotional-input", type=int, default=50)
    parser.add_argument("--out", type=str, default=str(ROOT_VOICEBOX / "backend" / "exports"))
    args = parser.parse_args()

    out_dir = Path(args.out)
    payload = build_training_vector(emotional_input=args.emotional_input)

    vec_path = write_vector_json(payload, out_dir)
    profile_path = write_profile_payloads(payload, out_dir)
    zip_path = write_voicebox_zip(payload, out_dir)

    print(json.dumps({
        "status": "ok",
        "emotional_input": args.emotional_input,
        "vector_json": str(vec_path),
        "profile_json": str(profile_path),
        "zip": str(zip_path) if zip_path else None,
        "profile_count": len(payload.get("profile_payloads", [])),
        "vector_row_count": len(payload.get("vector_rows", [])),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
