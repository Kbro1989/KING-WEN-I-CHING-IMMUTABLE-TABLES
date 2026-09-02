#!/usr/bin/env python3
"""Local King Wen expand server.
Serves POST /expand from localhost:8765.

Body: { emotional_input?: number, session_id?: string }
Response: shotgun_expand(request_text, emotional_input) JSON
"""

from __future__ import annotations

import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from scripts.full_hexagram_shotgun import shotgun_expand

# ---------------------------------------------------------------------------
# Canonical enrichment data — loaded once at module import.
# These files are the immutable source for corpus-derived fields that
# emotional_engine.py does not compute live (skill_cards, training_notes,
# domain_vectors, reflections, persona). The engine computes vectors,
# line states, porosity, consensus, and Hamiltonian energy — those are
# never overwritten by this enrichment. Only corpus-anchored text and
# structural metadata are merged in.
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent


def _load_enrichment_data() -> dict[str, Any]:
    """Load canonical enrichment maps keyed by hexagram_id string."""
    registry_path = _ROOT / "data" / "hexagram-registry.json"
    weights_path = _ROOT / "data" / "emotional-weights.json"
    reflections_path = _ROOT / "data" / "temporal-reflections.json"
    expansion_path = _ROOT / "scripts" / "hexagram_full_expansion.json"

    registry = {}
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

    weights = {}
    if weights_path.exists():
        weights = json.loads(weights_path.read_text(encoding="utf-8"))

    reflections = {}
    if reflections_path.exists():
        reflections = json.loads(reflections_path.read_text(encoding="utf-8"))

    # Full expansion carries skill_cards, domain_vectors, phases, personality
    full_expansion = {}
    if expansion_path.exists() and expansion_path.stat().st_size > 0:
        exp_data = json.loads(expansion_path.read_text(encoding="utf-8"))
        for entry in exp_data.get("expansion", []):
            hid = str(entry.get("hexagram_id"))
            if hid:
                full_expansion[hid] = entry

    # --- NPC identity kits (3D avatar model data per hexagram) ---
    kits_dir = _ROOT / "DATASETS" / "kingwen_model_sets"
    model_kits = {}
    if kits_dir.exists():
        for kit_file in sorted(kits_dir.glob("kit_*.json")):
            try:
                kit_data = json.loads(kit_file.read_text(encoding="utf-8"))
                hid = str(kit_data.get("kit_id", ""))
                if hid:
                    model_kits[hid] = kit_data
            except Exception:
                pass

    # --- NPC voice profiles ---
    voice_path = _ROOT / "DATASETS" / "kingwen_64_npc_voice_profiles.json"
    voice_profiles = {}
    if voice_path.exists():
        profiles = json.loads(voice_path.read_text(encoding="utf-8"))
        for p in profiles:
            hid = str(p.get("hexagram_id", ""))
            if hid:
                voice_profiles[hid] = p

    # --- Save strings (canonical identity serialization per hexagram) ---
    save_strings_path = _ROOT / "DATASETS" / "kingwen_save_strings.csv"
    save_strings = {}
    if save_strings_path.exists():
        import csv as csv_mod
        with open(save_strings_path, "r", encoding="utf-8") as f:
            reader = csv_mod.DictReader(f)
            for row in reader:
                hid = row.get("hexagram_id", "")
                if hid:
                    save_strings[hid] = row.get("save_string", "")

    # --- Quantum persistence mapping (64-grid node data per hexagram) ---
    quantum_path = _ROOT / "DATASETS" / "quantum_64_grid_transitional_mapping.json"
    quantum_nodes = {}
    quantum_meta = {}
    if quantum_path.exists():
        quantum_data = json.loads(quantum_path.read_text(encoding="utf-8"))
        quantum_meta = {k: v for k, v in quantum_data.items() if k != "nodes"}
        if isinstance(quantum_data.get("nodes"), list):
            for node in quantum_data["nodes"]:
                nid = str(node.get("hexagram_id", ""))
                if nid:
                    quantum_nodes[nid] = node

    # --- Archetypes (coder specialty, skill domain, RS3 actionable, risk) ---
    arch_path = _ROOT / "data" / "kingwen_archetypes_v2.json"
    archetypes = {}
    if arch_path.exists():
        arch_data = json.loads(arch_path.read_text(encoding="utf-8"))
        for a in arch_data.get("archetypes", []):
            hid = str(a.get("hexagram_id", ""))
            if hid:
                archetypes[hid] = a

    # --- Oracle master (polarity, elements, action_polarity, emotional_deltas) ---
    master_path = _ROOT / "DATASETS" / "kingwen_oracle_master.json"
    oracle_master = {}
    if master_path.exists() and master_path.stat().st_size > 0:
        try:
            master_data = json.loads(master_path.read_text(encoding="utf-8"))
            for h in master_data.get("hexagrams", []):
                hid = str(h.get("hexagram_id", ""))
                if hid:
                    oracle_master[hid] = h
        except Exception:
            pass

    # --- Avatar mesh manifest (512 PLY files per hex×phase) ---
    mesh_manifest_path = _ROOT / "DATASETS" / "kingwen_avatar_mesh_manifest.json"
    avatar_meshes = {}
    if mesh_manifest_path.exists() and mesh_manifest_path.stat().st_size > 0:
        try:
            manifest = json.loads(mesh_manifest_path.read_text(encoding="utf-8"))
            for m in manifest.get("meshes", []):
                key = f"{m['hexagram_id']}_{m['phase_bits']}"
                avatar_meshes[key] = m
        except Exception:
            pass

    return {
        "registry": registry,
        "weights": weights,
        "reflections": reflections,
        "full_expansion": full_expansion,
        "model_kits": model_kits,
        "voice_profiles": voice_profiles,
        "save_strings": save_strings,
        "quantum_nodes": quantum_nodes,
        "quantum_meta": quantum_meta,
        "archetypes": archetypes,
        "oracle_master": oracle_master,
        "avatar_meshes": avatar_meshes,
    }


_ENRICHMENT: dict[str, Any] = _load_enrichment_data()


def _enrich_expanded(entry: dict[str, Any]) -> dict[str, Any]:
    """Merge canonical corpus fields into a single expanded hexagram entry.

    Does NOT overwrite: expanded_vector, resolved_vector, inject_site,
    yao_vocabulary, line_states, sample_paths, intent, pre_slider.
    These come from the live Python engine. Only adds corpus-anchored fields.
    """
    hid = str(entry.get("hexagram_id", ""))
    reg = _ENRICHMENT["registry"].get(hid, {})
    weights = _ENRICHMENT["weights"].get(hid, {})
    reflections = _ENRICHMENT["reflections"].get(hid, {})
    full = _ENRICHMENT["full_expansion"].get(hid, {})

    # Merge hexagram_symbols with registry-derived fields (name, chinese, etc.)
    symbols = entry.get("hexagram_symbols", {})
    symbols.setdefault("pinyin", reg.get("pinyin", ""))
    symbols.setdefault("chinese", reg.get("chinese", ""))
    symbols.setdefault("upper_trigram_binary", reg.get("upper_trigram_binary", ""))
    symbols.setdefault("lower_trigram_binary", reg.get("lower_trigram_binary", ""))
    symbols.setdefault("ternary", reg.get("ternary", ""))
    symbols.setdefault("upper_trigram_ternary", reg.get("upper_trigram_ternary", ""))
    symbols.setdefault("lower_trigram_ternary", reg.get("lower_trigram_ternary", ""))

    # Corpus-derived enrichment fields
    entry.setdefault("trainingNotes", weights.get("trainingNotes", ""))
    entry.setdefault("personality", full.get("personality", ""))
    entry.setdefault("domain_vectors", full.get("domain_vectors", {}))
    entry.setdefault("skill_cards", full.get("skill_cards", []))
    entry.setdefault("reflections", {
        "past": reflections.get("past", ""),
        "present": reflections.get("present", ""),
        "future": reflections.get("future", ""),
    })
    entry.setdefault("training_weight_vectors", weights.get("training_weight_vectors", {}))

    # --- NPC identity kit (3D avatar model data) ---
    kit = _ENRICHMENT["model_kits"].get(hid, {})
    entry.setdefault("npc_model", kit)

    # --- NPC voice profile (per-hexagram Coder personality) ---
    voice = _ENRICHMENT["voice_profiles"].get(hid, {})
    entry.setdefault("npc_voice_profile", voice)

    # --- Save string (canonical identity serialization) ---
    save_str = _ENRICHMENT["save_strings"].get(hid, "")
    entry.setdefault("save_string", save_str)

    # --- Archetype (coder specialty, skill domain, RS3 actionable, risk, voice profile) ---
    arch = _ENRICHMENT["archetypes"].get(hid, {})
    entry.setdefault("coder_archetype", arch)

    # --- Oracle master fields (polarity, elements, action_polarity, emotional_deltas) ---
    om = _ENRICHMENT["oracle_master"].get(hid, {})
    entry.setdefault("upper_element", om.get("upper_element", ""))
    entry.setdefault("lower_element", om.get("lower_element", ""))
    entry.setdefault("polarity", om.get("polarity", ""))
    entry.setdefault("action_polarity", om.get("action_polarity", ""))
    entry.setdefault("hexagram_emotional_deltas", om.get("emotional_deltas", {}))

    # --- Quantum persistence field (per-hex state projection) ---
    # Look up this hexagram's node in the 64-grid quantum mapping.
    qnode = _ENRICHMENT["quantum_nodes"].get(hid, {})
    entry.setdefault("quantum_node", qnode)
    entry.setdefault("quantum_persistence", {
        "grid_dimensions": _ENRICHMENT["quantum_meta"].get("grid_dimensions", []),
        "total_nodes": _ENRICHMENT["quantum_meta"].get("total_nodes", 64),
        "spatial_bounds": _ENRICHMENT["quantum_meta"].get("spatial_bounds", {}),
        "node_spacing": _ENRICHMENT["quantum_meta"].get("node_spacing", 0),
        "hexagram_node": qnode,
    })

    # --- Avatar mesh reference (512 unique PLY meshes per hex×phase) ---
    phase_bits = entry.get("phase_bits", 0)
    mesh_key = f"{hid}_{phase_bits}"
    mesh_entry = _ENRICHMENT.get("avatar_meshes", {}).get(mesh_key, {})
    if mesh_entry:
        entry.setdefault("avatar_mesh", {
            "ply_filename": mesh_entry.get("ply_filename", ""),
            "ply_path": mesh_entry.get("ply_path", ""),
            "vertex_count": mesh_entry.get("vertex_count", 0),
            "face_count": mesh_entry.get("face_count", 0),
            "scale_factor": mesh_entry.get("scale_factor", 1.0),
            "rotation_modulation": mesh_entry.get("rotation_modulation", {}),
            "color_shift": mesh_entry.get("color_shift", {}),
            "animation_phase": mesh_entry.get("animation_phase", 0.0),
            "wavefunction": mesh_entry.get("wavefunction", {}),
            "delegate_vector": mesh_entry.get("delegate_vector", {}),
        })

    return entry


def _enrich_resolved(entry: dict[str, Any]) -> dict[str, Any]:
    """Merge corpus-derived intent/reflection fields into a resolved state.

    Does NOT overwrite: resolved_vector, expanded_vector, line_states,
    phase_temporal, phase_bits, inject_site. Only adds anchored text.
    """
    hid = str(entry.get("hexagram_id", ""))
    weights = _ENRICHMENT["weights"].get(hid, {})
    reflections = _ENRICHMENT["reflections"].get(hid, {})
    reg = _ENRICHMENT["registry"].get(hid, {})

    entry.setdefault("trainingNotes", weights.get("trainingNotes", ""))
    entry.setdefault("training_weight_vectors", weights.get("training_weight_vectors", {}))
    entry.setdefault("reflections", {
        "past": reflections.get("past", ""),
        "present": reflections.get("present", ""),
        "future": reflections.get("future", ""),
    })
    # sovereign_assertion / boundary_condition / dissipator_warning are
    # computed by OracleEngine.relay from consensus — surface them if present
    symbols = entry.get("hexagram_symbols", {})
    symbols.setdefault("pinyin", reg.get("pinyin", ""))
    symbols.setdefault("chinese", reg.get("chinese", ""))
    entry.setdefault("save_string", _ENRICHMENT["save_strings"].get(hid, ""))
    entry.setdefault("npc_voice_profile", _ENRICHMENT["voice_profiles"].get(hid, {}))
    entry.setdefault("npc_model", _ENRICHMENT["model_kits"].get(hid, {}))
    entry.setdefault("coder_archetype", _ENRICHMENT["archetypes"].get(hid, {}))
    om = _ENRICHMENT["oracle_master"].get(hid, {})
    entry.setdefault("upper_element", om.get("upper_element", ""))
    entry.setdefault("lower_element", om.get("lower_element", ""))
    entry.setdefault("polarity", om.get("polarity", ""))
    entry.setdefault("action_polarity", om.get("action_polarity", ""))
    entry.setdefault("hexagram_emotional_deltas", om.get("emotional_deltas", {}))

    # --- Avatar mesh reference (same 512 unique PLY meshes per hex×phase) ---
    phase_bits = entry.get("phase_bits", 0)
    mesh_key = f"{hid}_{phase_bits}"
    mesh_entry = _ENRICHMENT.get("avatar_meshes", {}).get(mesh_key, {})
    if mesh_entry:
        entry.setdefault("avatar_mesh", {
            "ply_filename": mesh_entry.get("ply_filename", ""),
            "ply_path": mesh_entry.get("ply_path", ""),
            "vertex_count": mesh_entry.get("vertex_count", 0),
            "face_count": mesh_entry.get("face_count", 0),
            "scale_factor": mesh_entry.get("scale_factor", 1.0),
            "rotation_modulation": mesh_entry.get("rotation_modulation", {}),
            "color_shift": mesh_entry.get("color_shift", {}),
            "animation_phase": mesh_entry.get("animation_phase", 0.0),
            "wavefunction": mesh_entry.get("wavefunction", {}),
            "delegate_vector": mesh_entry.get("delegate_vector", {}),
        })

    return entry


def _enrich_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Top-level enrichment: merge canonical corpus fields into the response."""
    expanded = payload.get("expanded", [])
    resolved = payload.get("resolved", [])

    for entry in expanded:
        _enrich_expanded(entry)
    for entry in resolved:
        _enrich_resolved(entry)

    return payload


def _build_save_string_consensus(result: Any, expanded: list[Any], resolved: list[Any]) -> dict[str, Any]:
    """Build V2.1 save string consensus capturing each hexagram individually."""
    import hashlib as _hashlib
    try:
        _pellets = expanded if expanded else result.get("expanded", [])
        _save_parts: list[str] = ["KW64_SAVE_STRING_V2.1"]
        for _p in _pellets:
            _hid = _p.get("hexagram_id", 0)
            _binary = _p.get("binary_bottom_to_top") or "111111"
            _cat = _p.get("category") or "Sovereign"
            _act = _p.get("action") or "ASSERT"
            _tp = _p.get("table_personality") or {}
            _vec = _p.get("expanded_vector") or {}
            _chaos = round(float(_vec.get("chaos", 0.5)), 3)
            _whimsy = round(float(_vec.get("whimsy", 0.5)), 3)
            _dark = round(float(_vec.get("darkTone", 0.5)), 3)
            _coherence = round(float(_vec.get("coherence", 0.5)), 3)
            _vweight = round(float(_vec.get("voiceWeight", 0.5)), 3)
            _lb = _p.get("line_balance") or {}
            _dy = round(float(_lb.get("yang_count", 0) or 0) - float(_lb.get("yin_count", 0) or 0), 2)
            _yd = round(float(_lb.get("yao_count", 0) or 0) - 3.0, 2)
            _inj = _p.get("inject_site") or {}
            _porosity = round(float(_inj.get("porosity", 0.5)), 3)
            _pellet = (f"HEX{_hid:02d}|{_binary}|{_cat}|{_act}|{_tp.get('agent_type','architect')}|"
                      f"{_tp.get('domain','assertion')}|{_tp.get('element_subset','heaven')}|Dev|interact|"
                      f"{1000+_hid}|#000000|{_chaos}|{_whimsy}|{_dark}|{_coherence}|{_vweight}|"
                      f"{_dy}|{_yd}|{_porosity}|idle|0.0|ARM01|anchor|{_coherence}")
            _save_parts.append(_pellet)
        _save_str = "::".join(_save_parts)
        _digest = _hashlib.sha256(_save_str.encode("utf-8")).hexdigest()[:8]
        _pc = result.get("personality_consensus", {})
        _vecs = _pc.get("consensus_vector", {})
        consensus = {
            "consensus_type": "full_64_hex_field_save_string",
            "consensus_hexagram_id": None,
            "consensus_hexagram_name": None,
            "consensus_porosity_mean": None,
            "consensus_vector": _vecs if _vecs else {"chaos": 0.5, "whimsy": 0.5, "darkTone": 0.5, "coherence": 0.5, "voiceWeight": 0.5},
            "dominant_intent": _pc.get("dominant_intent"),
            "save_string": f"{_save_str}::{_digest}",
            "total_expanded": result.get("total_expanded", len(expanded)),
            "total_resolved": result.get("total_resolved", len(resolved)),
            "total_ternary_line_permutations": result.get("total_ternary_line_permutations", 46656),
        }
    except Exception:
        _pc = result.get("personality_consensus", {})
        consensus = {
            "consensus_type": "full_64_hex_field",
            "consensus_hexagram_id": None,
            "consensus_hexagram_name": None,
            "consensus_porosity_mean": None,
            "consensus_vector": _pc.get("consensus_vector", {}),
            "dominant_intent": _pc.get("dominant_intent"),
            "total_expanded": result.get("total_expanded", len(expanded)),
            "total_resolved": result.get("total_resolved", len(resolved)),
            "total_ternary_line_permutations": result.get("total_ternary_line_permutations", 46656),
        }
    return consensus


class ExpandHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(204, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/3d/"):
            try:
                # Support two formats:
                #   /3d/<hex_id>           → metadata about all phases for that hex
                #   /3d/<hex_id>_<phase>   → binary PLY file for that hex+phase
                #   /3d/<hex_id>_<phase>.ply → same, with .ply suffix
                path_part = self.path.split("/3d/")[1].split("?")[0]

                # Parse hex_id and optional phase
                if "_" in path_part:
                    hex_str, phase_suffix = path_part.split("_", 1)
                    hex_id = int(hex_str)
                    # Strip .ply suffix if present
                    phase_str = phase_suffix.replace(".ply", "")
                    try:
                        phase_bits = int(phase_str)
                    except ValueError:
                        # If not an integer, treat as just hex_id lookup
                        hex_id = int(path_part.replace(".ply", ""))
                        phase_bits = 0
                else:
                    hex_id = int(path_part.replace(".ply", ""))
                    phase_bits = 0

                mesh_dir = Path(__file__).resolve().parent / "DATASETS" / "kingwen_avatar_meshes"
                ply_filename = f"hex{hex_id:02d}_phase{phase_bits}.ply"
                ply_path = mesh_dir / ply_filename

                usd_path = Path(__file__).resolve().parent / "DATASETS" / "openusd_stages" / f"npc_hex_{hex_id:02d}.usda"
                godot_path = Path(__file__).resolve().parent / "DATASETS" / "godot_scenes" / f"npc_hex_{hex_id:02d}.tscn"

                # If .ply requested, serve binary mesh directly
                if path_part.endswith(".ply"):
                    if ply_path.exists():
                        binary_data = ply_path.read_bytes()
                        self.send_response(200)
                        self.send_header("Content-Type", "application/octet-stream")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.send_header("Content-Length", str(len(binary_data)))
                        self.end_headers()
                        self.wfile.write(binary_data)
                        return
                    return self._send_json(404, {"error": f"PLY not found: {ply_filename}"})

                # Otherwise serve metadata
                ply_text = ply_path.read_text(encoding="utf-8") if ply_path.exists() else ""
                usd_text = usd_path.read_text(encoding="utf-8") if usd_path.exists() else ""
                godot_text = godot_path.read_text(encoding="utf-8") if godot_path.exists() else ""

                # Read manifest for phase-aware metadata
                manifest_path = mesh_dir.parent / "kingwen_avatar_mesh_manifest.json"
                manifest_entry = {}
                if manifest_path.exists():
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    for entry in manifest.get("meshes", []):
                        if entry.get("hexagram_id") == hex_id and entry.get("phase_bits") == phase_bits:
                            manifest_entry = entry
                            break

                payload = {
                    "hexagram_id": hex_id,
                    "phase_bits": phase_bits,
                    "ply_mesh_available": ply_path.exists(),
                    "ply_filename": ply_filename,
                    "ply_size_bytes": ply_path.stat().st_size if ply_path.exists() else 0,
                    "ply_path": str(ply_path),
                    "usda_content": usd_text,
                    "godot_tscn_content": godot_text,
                    "godot_path": str(godot_path),
                    "manifest_entry": manifest_entry if manifest_entry else None,
                }
                return self._send_json(200, payload)
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/voice/"):
            try:
                hex_str = self.path.split("/voice/")[1].split("?")[0]
                hex_id = int(hex_str)
                vp_path = Path(__file__).resolve().parent / "DATASETS" / "kingwen_64_npc_voice_profiles.json"
                if vp_path.exists():
                    profiles = json.loads(vp_path.read_text(encoding="utf-8"))
                    matched = next((p for p in profiles if p.get("hexagram_id") == hex_id), {})
                    return self._send_json(200, matched)
                return self._send_json(404, {"error": "Voice profiles not found"})
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/quantum/"):
            try:
                hex_str = self.path.split("/quantum/")[1].split("?")[0]
                hex_id = int(hex_str)
                ql_manifest = Path(__file__).resolve().parent / "DATASETS" / "quantumlab_visuals_manifest.json"
                plot_path = Path(__file__).resolve().parent / "DATASETS" / "quantumlab_plots" / f"quantum_3d_hex_{hex_id:02d}.png"
                
                payload = {
                    "hexagram_id": hex_id,
                    "plot_3d_available": plot_path.exists(),
                    "plot_3d_path": str(plot_path),
                }
                return self._send_json(200, payload)
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/kit/"):
            try:
                hex_str = self.path.split("/kit/")[1].split("?")[0]
                hex_id = int(hex_str)
                kit_path = Path(__file__).resolve().parent / "DATASETS" / "kingwen_model_sets" / f"kit_{hex_id}.json"
                if kit_path.exists():
                    kit_data = json.loads(kit_path.read_text(encoding="utf-8"))
                    return self._send_json(200, kit_data)
                return self._send_json(404, {"error": f"Kit {hex_id} not found"})
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/collision/"):
            try:
                hex_str = self.path.split("/collision/")[1].split("?")[0]
                hex_id = int(hex_str)
                bvh_path = Path(__file__).resolve().parent / "DATASETS" / "collisionvis_physics" / "collisionvis_64_npc_physics.json"
                if bvh_path.exists():
                    all_bvhs = json.loads(bvh_path.read_text(encoding="utf-8"))
                    matched = next((b for b in all_bvhs if b.get("hexagram_id") == hex_id), None)
                    if matched:
                        return self._send_json(200, matched)
                return self._send_json(404, {"error": f"Collision data for hex {hex_id} not found"})
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/npc/"):
            try:
                # /npc/<npc_model_id>          → metadata about RSC NPC model
                # /npc/<npc_model_id>.ply       → binary PLY file (RSC geometry)
                # /npc/hex<hex_id>              → NPC PLY for hexagram's mapped NPC model
                # /npc/hex<hex_id>.ply          → binary PLY for hexagram's mapped NPC model
                path_part = self.path.split("/npc/")[1].split("?")[0]
                npc_mesh_dir = Path(__file__).resolve().parent / "DATASETS" / "kingwen_avatar_meshes_rsc"
                npc_mappings_path = Path(__file__).resolve().parent / "DATASETS" / "kingwen_model_sets" / "npc_kit_mappings.json"

                # Load NPC kit mappings
                npc_mappings = {}
                if npc_mappings_path.exists():
                    mappings_data = json.loads(npc_mappings_path.read_text(encoding="utf-8"))
                    for m in mappings_data:
                        npc_mappings[str(m["npc_model_id"])] = m
                        npc_mappings[f"hex{m['hexagram_id']}"] = m

                if path_part.startswith("hex"):
                    # /npc/hex<hex_id> → serve NPC model mapped to this hexagram
                    hex_str = path_part[3:].replace(".ply", "")
                    try:
                        hex_id = int(hex_str)
                    except ValueError:
                        return self._send_json(400, {"error": f"Invalid hex ID: {hex_str}"})

                    # Find the NPC model mapped to this hexgram
                    mapping = None
                    for m in npc_mappings.values():
                        if m.get("hexagram_id") == hex_id:
                            mapping = m
                            break

                    if not mapping:
                        return self._send_json(404, {"error": f"No NPC model mapped to hex {hex_id}"})

                    npc_model_id = mapping["npc_model_id"]
                    ply_filename = f"rsc_npc_{npc_model_id}.ply"
                    ply_path = npc_mesh_dir / ply_filename

                    if path_part.endswith(".ply"):
                        if ply_path.exists():
                            binary_data = ply_path.read_bytes()
                            self.send_response(200)
                            self.send_header("Content-Type", "application/octet-stream")
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.send_header("Content-Length", str(len(binary_data)))
                            self.end_headers()
                            self.wfile.write(binary_data)
                            return
                        return self._send_json(404, {"error": f"NPC PLY not found: {ply_filename}"})

                    # Serve metadata
                    payload = {
                        "hexagram_id": hex_id,
                        "hexagram_name": mapping.get("hexagram_name", ""),
                        "npc_model_id": npc_model_id,
                        "ply_filename": ply_filename,
                        "ply_path": str(ply_path),
                        "ply_available": ply_path.exists(),
                    }
                    return self._send_json(200, payload)
                else:
                    # /npc/<model_id> or /npc/<model_id>.ply
                    model_str = path_part.replace(".ply", "")
                    try:
                        model_id = int(model_str)
                    except ValueError:
                        return self._send_json(400, {"error": f"Invalid NPC model ID: {model_str}"})

                    ply_filename = f"rsc_npc_{model_id}.ply"
                    ply_path = npc_mesh_dir / ply_filename

                    if path_part.endswith(".ply"):
                        if ply_path.exists():
                            binary_data = ply_path.read_bytes()
                            self.send_response(200)
                            self.send_header("Content-Type", "application/octet-stream")
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.send_header("Content-Length", str(len(binary_data)))
                            self.end_headers()
                            self.wfile.write(binary_data)
                            return
                        return self._send_json(404, {"error": f"NPC PLY not found: {ply_filename}"})

                    mapping = npc_mappings.get(str(model_id), {})
                    payload = {
                        "npc_model_id": model_id,
                        "hexagram_id": mapping.get("hexagram_id", None),
                        "hexagram_name": mapping.get("hexagram_name", ""),
                        "ply_filename": ply_filename,
                        "ply_path": str(ply_path),
                        "ply_available": ply_path.exists(),
                    }
                    return self._send_json(200, payload)
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})

        if self.path.startswith("/scene/count"):
            # Return total scene count from cached index file (avoids scanning 1.86GB JSONL)
            idx_path = _ROOT / "DATASETS" / "jkd_ingestion_index.json"
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                return self._send_json(200, idx)
            except Exception as exc:
                return self._send_json(500, {"error": str(exc)})

        if self.path.startswith("/scene/"):
            # Serve a single scene record from the JSONL by line index (0-based)
            try:
                scene_str = self.path.split("/scene/")[1].split("?")[0]
                scene_idx = int(scene_str)
                jkd_path = _ROOT / "DATASETS" / "jkd_ingestion_binary.jsonl"
                with open(jkd_path, "r", encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f):
                        if i == scene_idx:
                            record = json.loads(line.strip()) if line.strip() else {}
                            return self._send_json(200, record)
                return self._send_json(404, {"error": f"Scene {scene_idx} not found"})
            except ValueError:
                return self._send_json(400, {"error": "Invalid scene index"})
            except Exception as exc:
                return self._send_json(500, {"error": str(exc)})

        return self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/capture":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b"{}"
                body = json.loads(raw.decode("utf-8") or "{}")
            except Exception:
                return self._send_json(400, {"error": "Bad JSON"})

            # Perform shotgun_expand (full ternary expansion, no collapse)
            req_text = str(body.get("text") or body.get("request_text") or "")
            raw_emo = body.get("emotional_input")
            try:
                raw_emo_val = int(raw_emo) if raw_emo is not None else None
            except (TypeError, ValueError):
                raw_emo_val = None
            
            from emotional_engine import derive_dynamic_emotional_input
            emotional_input = derive_dynamic_emotional_input(req_text, raw_emo_val)
            
            try:
                result = shotgun_expand(request_text=req_text, emotional_input=emotional_input)
            except Exception as exc:
                return self._send_json(500, {"error": str(exc)})

            # Append to capture log
            record = {
                "ts": __import__('time').time(),
                "session_id": str(body.get("session_id") or "unknown"),
                "event_type": str(body.get("event_type") or "widget_interaction"),
                "paper_id": str(body.get("paper_id") or "unknown"),
                "hexagram_id": body.get("hexagram_id"),
                "phase_bits": body.get("phase_bits"),
                "phase_temporal": body.get("phase_temporal"),
                "interaction": body.get("interaction"),
                "payload": body.get("payload", {}),
            }
            capture_path = Path(__file__).resolve().parent / "DATASETS" / "shotgun_captures.jsonl"
            try:
                with open(capture_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, default=str) + "\n")
            except Exception:
                pass
            # Build the same response structure as /expand
            resolved = result.get("resolved", [])
            expanded = result.get("expanded", [])

            # Enrich with canonical corpus fields (same as /expand path)
            _enrich_response(result)

            # Build consensus as a V2.1 save string capturing each hexagram permutation individually
            # Each pellet carries the full state shape per hexagram, not a collapsed single hex
            consensus = _build_save_string_consensus(result, expanded, resolved)

            response = {
                "emotional_input": emotional_input,
                "session_id": str(body.get("session_id") or "local"),
                "text": req_text,
                "request_text_injected": req_text,
                "source": "kingwen-shotgun-expand",
                "total_expanded": result.get("total_expanded", len(expanded)),
                "total_resolved": result.get("total_resolved", len(resolved)),
                "ternary_line_permutations_per_hex": result.get("ternary_line_permutations_per_hex", 729),
                "total_ternary_line_permutations": result.get("total_ternary_line_permutations", 46656),
                "total_domained_routes": result.get("total_domained_routes", 35000),
                "capture_point": result.get("capture_point", "first-parse"),
                "expanded_count": len(expanded),
                "resolved_count": len(resolved),
                "expanded": expanded,
                "resolved": resolved,
                "consensus": consensus,
                "voice_ensemble": result.get("voice_ensemble", {}),
                "avg_resolved_hamiltonian_energy": result.get("avg_resolved_hamiltonian_energy"),
                "avg_expanded_hamiltonian_energy": result.get("avg_expanded_hamiltonian_energy"),
            }
            return self._send_json(200, response)

        if self.path != "/expand":
            return self._send_json(404, {"error": "Not Found", "path": self.path})

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception as exc:
            return self._send_json(400, {"error": f"Bad JSON: {exc}"})

        text = str(body.get("text") or body.get("request_text") or "").strip()
        session_id = str(body.get("session_id") or "local")
        raw_emo = body.get("emotional_input")
        try:
            raw_emo_val = int(raw_emo) if raw_emo is not None else None
        except (TypeError, ValueError):
            raw_emo_val = None
        from emotional_engine import derive_dynamic_emotional_input
        emotional_input = derive_dynamic_emotional_input(text, raw_emo_val)

        try:
            result = shotgun_expand(request_text=text, emotional_input=emotional_input)
        except Exception as exc:
            return self._send_json(
                500, {"error": str(exc), "trace": traceback.format_exc()}
            )

        resolved = result.get("resolved", [])
        expanded = result.get("expanded", [])

        # Enrich with canonical corpus fields: skill_cards, trainingNotes,
        # domain_vectors, reflections — merged from immutable data files.
        # Engine-computed vectors/consensus/line_states are never overwritten.
        _enrich_response(result)

        # Build consensus as a V2.1 save string capturing each hexagram permutation individually
        # Each pellet carries the full state shape per hexagram, not a collapsed single hex
        consensus = _build_save_string_consensus(result, expanded, resolved)

        response = {
            "total": len(resolved),
            "emotional_input": emotional_input,
            "session_id": session_id,
            "text": text,
            "request_text_injected": text,  # confirm intent was passed to shotgun_expand
            "source": "kingwen-shotgun-expand",
            "total_expanded": result.get("total_expanded", len(expanded)),
            "total_resolved": result.get("total_resolved", len(resolved)),
            "ternary_line_permutations_per_hex": result.get("ternary_line_permutations_per_hex", 729),
            "total_ternary_line_permutations": result.get("total_ternary_line_permutations", 46656),
            "total_domained_routes": result.get("total_domained_routes", 35000),
            "capture_point": result.get("capture_point", "first-parse"),
            "expanded_count": len(expanded),
            "resolved_count": len(resolved),
            "expanded": expanded,           # full 64-hex pre-slider expansion
            "resolved": resolved,
            "consensus": consensus,
            "voice_ensemble": result.get("voice_ensemble", {}),
            "avg_resolved_hamiltonian_energy": result.get("avg_resolved_hamiltonian_energy"),
            "avg_expanded_hamiltonian_energy": result.get("avg_expanded_hamiltonian_energy"),
        }
        self._send_json(200, response)

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: N802
        # Quiet default stderr logging.
        pass


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = HTTPServer((host, port), ExpandHandler)
    print(f"kingwen expand server running on http://{host}:{port}/expand")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()