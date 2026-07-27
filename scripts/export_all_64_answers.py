#!/usr/bin/env python3
"""export_all_64_answers.py
Exports the exact question asked vs. the full 64 individual hexagram archetype answers,
vectors, stances, and resolutions computed dynamically by the King Wen Shotgun Engine.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from full_hexagram_shotgun import shotgun_expand

def export_64_hexagram_answers(question: str) -> None:
    payload = shotgun_expand(question, emotional_input=50)
    pellets = payload["expanded"]

    print("=" * 90)
    print("THE EXACT QUESTION ASKED TO THE KING WEN 64-HEXAGRAM SHOTGUN ORACLE ENGINE:")
    print("=" * 90)
    print(f"\"{question}\"\n")

    print("=" * 90)
    print("ALL 64 HEXAGRAM INDIVIDUAL ARCHETYPE ANSWERS & RESOLUTIONS")
    print("=" * 90)

    for p in pellets:
        hid = p["hexagram_id"]
        name = p["name"]
        binary = p["binary_bottom_to_top"]
        unicode_sym = p.get("unicode", "")
        spec = p["coder_specialty"]
        rs3 = p["rs3_actionable"]
        vec = p["expanded_vector"]
        chaos = vec["chaos"]
        whimsy = vec["whimsy"]
        dark = vec["darkTone"]
        coherence = vec["coherence"]
        vweight = vec["voiceWeight"]
        inject = p.get("inject_site", {})
        porosity = inject.get("porosity", 0.0)
        plabel = inject.get("porosity_label", "sealed")
        hermes = p.get("hermes_layer", {})
        vmode = hermes.get("voice_mode", "idle")
        schaub = p.get("schauberger_metrics", {})
        vtension = schaub.get("vortex_tension", 0.0)
        motion = schaub.get("motion_type", "centripetal")
        proj = p.get("projections", {})
        voicebox_engine = proj.get("voicebox", {}).get("preset_engine", "qwen")
        agency_prompt = proj.get("agency_3d", {}).get("visual_prompt", "")

        print(f"\n[HEXAGRAM #{hid:02d}] {name} (Binary: {binary})")

        print(f"  • Coder Specialty   : {spec}")
        print(f"  • RS3 3D Actionable : {rs3}")
        print(f"  • Vector Signature  : Chaos={chaos:.3f} | Whimsy={whimsy:.3f} | Dark={dark:.3f} | Coherence={coherence:.3f} | VoiceWeight={vweight:.3f}")
        print(f"  • Substrate State   : Porosity={porosity:.3f} ({plabel})")
        print(f"  • Hermes VHDL       : Nominal Voice Mode '{vmode}'")
        print(f"  • Schauberger       : Vortex Tension {vtension:.3f} ({motion} motion)")
        print(f"  • Voicebox Engine   : '{voicebox_engine}'")
        print(f"  • Visual Prompt     : \"{agency_prompt}\"")
        print(f"  • Specific Resolve  : {spec} perspective on '{question}' via {rs3} actionable.")

if __name__ == "__main__":
    question = (
        "Design a resilient, asynchronous WebSocket event dispatcher in TypeScript/Python "
        "that implements circuit breaking under high chaos, zero-trust security auditing, "
        "and state rehydration from shared memory storage pools."
    )
    export_64_hexagram_answers(question)
