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

    def do_POST(self) -> None:  # noqa: N802
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
            result = collapse_full_128(emotional_input=emotional_input)
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
            "source": "local-python",
            "expanded_count": len(expanded),
            "resolved_count": len(resolved),
            "resolved": resolved,
            "consensus": result.get("consensus", {}),
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
