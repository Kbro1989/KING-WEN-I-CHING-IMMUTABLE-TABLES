#!/usr/bin/env python3
"""Local King Wen expand server.
Serves POST /expand from localhost:8765.

Body: { emotional_input?: number, session_id?: string }
Response: collapse_full_128(emotional_input) JSON
"""

from __future__ import annotations

import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from emotional_engine import collapse_full_128


class ExpandHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
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
                hex_str = self.path.split("/3d/")[1].split("?")[0]
                hex_id = int(hex_str)
                ply_path = Path(__file__).resolve().parent / "DATASETS" / "kingwen_3d_meshes" / f"shap_e_hex_{hex_id:02d}.ply"
                usd_path = Path(__file__).resolve().parent / "DATASETS" / "openusd_stages" / f"npc_hex_{hex_id:02d}.usda"
                godot_path = Path(__file__).resolve().parent / "DATASETS" / "godot_scenes" / f"npc_hex_{hex_id:02d}.tscn"
                
                ply_text = ply_path.read_text(encoding="utf-8") if ply_path.exists() else ""
                usd_text = usd_path.read_text(encoding="utf-8") if usd_path.exists() else ""
                godot_text = godot_path.read_text(encoding="utf-8") if godot_path.exists() else ""
                
                payload = {
                    "hexagram_id": hex_id,
                    "ply_mesh_available": ply_path.exists(),
                    "ply_content": ply_text,
                    "usda_content": usd_text,
                    "godot_tscn_content": godot_text,
                    "ply_path": str(ply_path),
                    "usd_path": str(usd_path),
                    "godot_path": str(godot_path),
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

        return self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/capture":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b"{}"
                body = json.loads(raw.decode("utf-8") or "{}")
            except Exception:
                return self._send_json(400, {"error": "Bad JSON"})

            # Perform standard collapse_full_128
            try:
                emotional_input = int(body.get("emotional_input", 50))
            except (TypeError, ValueError):
                emotional_input = 50
            
            try:
                result = collapse_full_128(emotional_input=emotional_input, request_text=str(body.get("text") or ""))
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
            response = {
                "total": len(resolved),
                "emotional_input": emotional_input,
                "session_id": str(body.get("session_id") or "local"),
                "text": str(body.get("text") or ""),
                "request_text_injected": str(body.get("text") or ""),
                "source": "local-python",
                "expanded_count": len(expanded),
                "resolved_count": len(resolved),
                "expanded": expanded,
                "resolved": resolved,
                "consensus": result.get("consensus", {}),
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

        text = str(body.get("text") or "").strip()
        session_id = str(body.get("session_id") or "local")
        try:
            emotional_input = int(body.get("emotional_input", 50))
        except (TypeError, ValueError):
            emotional_input = 50
        if emotional_input < 0:
            emotional_input = 0
        if emotional_input > 100:
            emotional_input = 100

        try:
            result = collapse_full_128(emotional_input=emotional_input, request_text=text)
        except Exception as exc:
            return self._send_json(
                500, {"error": str(exc), "trace": traceback.format_exc()}
            )

        resolved = result.get("resolved", [])
        expanded = result.get("expanded", [])

        response = {
            "total": len(resolved),
            "emotional_input": emotional_input,
            "session_id": session_id,
            "text": text,
            "request_text_injected": text,  # confirm intent was passed to collapse_full_128
            "source": "local-python",
            "expanded_count": len(expanded),
            "resolved_count": len(resolved),
            "expanded": expanded,           # full 64-hex pre-slider expansion
            "resolved": resolved,
            "consensus": result.get("consensus", {}),
            "voice_ensemble": result.get("voice_ensemble", {}),
            "avg_resolved_hamiltonian_energy": result.get("avg_resolved_hamiltonian_energy"),
            "avg_expanded_hamiltonian_energy": result.get("avg_expanded_hamiltonian_energy"),
        }
        self._send_json(200, response)

    def log_message(self, fmt: str, *args: object) -> None:
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