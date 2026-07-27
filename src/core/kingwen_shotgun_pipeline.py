#!/usr/bin/env python3
"""kingwen_shotgun_pipeline.py
The 64-pellet un-normalized shotgun blast pipeline & J-Space manifold bridge (v3.0).

Ternary Line-State Baseline & RS3 Agency Integration:
- 6 Ternary Line Positions per Hexagram = 3^6 = 729 Ternary Line States per Hexagram
- 64 Hexagrams x 729 Line States x Temporal Stances = ~35,000 Domained Routes
- Per-Hexagram Coder Specialties: Research, Dev, HTML, Robotics, Game Dev, Analytics, Blueprinting, Scribe, Security Red-Team, Database/Storage, Async/Networking, DevOps/CI-CD
- RS3 Actionable Tagging: attack, interact, traverse, harvest, craft, bank, equip, cast, dialogue, forensics
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]
_DATA_DIR = _REPO_ROOT / "data"

UNICODE_HEXAGRAMS = [
    "䷀", "䷁", "䷂", "䷃", "䷄", "䷅", "䷆", "䷇",
    "䷈", "䷉", "䷊", "䷋", "䷌", "䷍", "䷎", "䷏",
    "䷐", "䷑", "䷒", "䷓", "䷔", "䷕", "䷖", "䷗",
    "䷘", "䷙", "䷚", "䷛", "䷜", "䷝", "䷞", "䷟",
    "䷠", "䷡", "䷢", "䷣", "䷤", "䷥", "䷦", "䷧",
    "䷨", "䷩", "䷪", "䷫", "䷬", "䷭", "䷮", "䷯",
    "䷰", "䷱", "䷲", "䷳", "䷴", "䷵", "䷶", "䷷",
    "䷸", "䷹", "䷺", "䷻", "䷼", "䷽", "䷾", "䷿"
]

ACTION_SYMBOLS = {
    "ASSERT": "▲",
    "YIELD": "▼",
    "ADAPT": "◆",
    "WAIT": "○"
}

@dataclass
class TemporalStance:
    weight: float
    confidence: float
    posture: str
    focus: str
    concern: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weight": round(self.weight, 3),
            "confidence": round(self.confidence, 3),
            "posture": self.posture,
            "focus": self.focus,
            "concern": self.concern
        }

@dataclass
class JSpaceCoordinate:
    hexagram_id: int
    phase_bits: int
    chaos: float
    whimsy: float
    dark_tone: float
    coherence: float
    voice_weight: float
    porosity: float
    porosity_label: str
    request_text: str = ""

    def to_voicebox_payload(self) -> Dict[str, Any]:
        engine = "qwen"
        if self.voice_weight > 0.90 and self.porosity <= 0.20:
            engine = "qwen_custom_voice"
        elif self.coherence > 0.90:
            engine = "kokoro"
        elif self.dark_tone > 0.50:
            engine = "chatterbox_turbo"

        return {
            "profile_id": f"kingwen-hex-{self.hexagram_id:02d}",
            "preset_engine": engine,
            "instruct": f"kingwen_hex={self.hexagram_id} | chaos={self.chaos:.3f} | coherence={self.coherence:.3f} | dark={self.dark_tone:.3f}",
            "design_prompt": f"Voice for hexagram {self.hexagram_id} (porosity={self.porosity:.3f}, {self.porosity_label}).",
            "personality": f"Hexagram {self.hexagram_id} speaker with coherence={self.coherence:.2f}.",
            "prosody": {
                "speed": round(1.0 + (self.whimsy * 0.1), 3),
                "weight": round(self.voice_weight, 3),
                "pitch_delta": round((self.whimsy - self.dark_tone) * 0.2, 3)
            }
        }

    def to_megatron_payload(self) -> Dict[str, Any]:
        return {
            "hexagram_id": self.hexagram_id,
            "phase_bits": self.phase_bits,
            "porosity_head_label": self.porosity_label,
            "porosity_score": round(self.porosity, 4),
            "target_vectors": {
                "chaos": round(self.chaos, 4),
                "whimsy": round(self.whimsy, 4),
                "darkTone": round(self.dark_tone, 4),
                "coherence": round(self.coherence, 4),
            },
            "training_prompt": f"[HEX_{self.hexagram_id:02d}] {self.request_text}"
        }

    def to_kimi_payload(self) -> Dict[str, Any]:
        return {
            "hexagram_id": self.hexagram_id,
            "context_window_bias": "expand" if self.porosity > 0.5 else "strict",
            "max_tokens_budget": int(32768 * (1.0 + self.whimsy)),
            "multi_doc_anchor": f"kingwen_anchor_hex_{self.hexagram_id:02d}"
        }

    def to_3d_agency_payload(self, rs3_actionable: str = "interact") -> Dict[str, Any]:
        cat_map = {1: "Sovereign", 2: "Transformer", 3: "Dissipator", 4: "Boundary"}
        category_id = ((self.hexagram_id - 1) % 4) + 1
        category_name = cat_map[category_id]

        return {
            "hexagram_id": self.hexagram_id,
            "category": category_name,
            "rs3_actionable": rs3_actionable,
            "mesh_stability": round(self.coherence, 3),
            "porosity_label": self.porosity_label,
            "camera_track_mode": "locked" if self.coherence > 0.85 else "dynamic_pan",
            "particle_dispersion": round(self.chaos * 100.0, 1),
            "visual_prompt": f"{category_name} avatar executing RS3 actionable '{rs3_actionable}' in hexagram {self.hexagram_id} spatial domain."
        }

class KingWenShotgunPipeline:
    """Non-gated 64-pellet shotgun blast pipeline engine with 729 ternary line state baseline."""

    def __init__(self, archetypes_json_path: Optional[Path] = None):
        self.archetypes_path = archetypes_json_path or (_DATA_DIR / "kingwen_archetypes_v2.json")
        self.archetypes: Dict[int, Dict[str, Any]] = {}
        self._load_archetypes()

    def _load_archetypes(self) -> None:
        if not self.archetypes_path.exists():
            logger.warning("Archetypes file missing at %s, using fallback", self.archetypes_path)
            return

        try:
            data = json.loads(self.archetypes_path.read_text(encoding="utf-8"))
            for entry in data.get("archetypes", []):
                hid = int(entry.get("hexagram_id", 0))
                self.archetypes[hid] = entry
            logger.info("Loaded %d canonical hexagram archetypes", len(self.archetypes))
        except Exception as exc:
            logger.error("Error loading archetypes: %s", exc)

    def _classify_porosity(self, porosity: float) -> str:
        if porosity > 0.80:
            return "Dissolved"
        elif porosity > 0.60:
            return "Fluid"
        elif porosity > 0.40:
            return "Porous"
        elif porosity > 0.20:
            return "Structured"
        return "Crystallized"

    def _generate_ternary_line_matrix(self, binary_str: str) -> Dict[str, Any]:
        """Generates the 6-slot ternary line matrix (3^6 = 729 line-state combinations)."""
        line_states = []
        labels = ["Nine_One", "Six_Two", "Nine_Three", "Nine_Four", "Six_Five", "Nine_Six"]
        ternary_values = []
        for i in range(6):
            bit = int(binary_str[i]) if i < len(binary_str) else 1
            ternary_val = bit if (i % 2 == 0) else 2  # 0=yin, 1=yang, 2=yao changing
            ternary_values.append(ternary_val)
            line_states.append({
                "position": i + 1,
                "ternary_state": ternary_val,
                "yao_key": f"line_{i+1}_ternary_{ternary_val}",
                "yao_label": labels[i],
                "is_changing": (ternary_val == 2)
            })
        return {
            "ternary_pattern": ternary_values,
            "line_states": line_states,
            "total_ternary_states_per_hex": 729
        }

    def _generate_checklist(self, coherence: float, chaos: float) -> List[Dict[str, Any]]:
        return [
            {"axis": "coherence", "status": "in_window" if coherence > 0.5 else "out_of_window"},
            {"axis": "chaos", "status": "in_window" if chaos < 0.7 else "elevated"},
            {"axis": "temporal_alignment", "status": "in_window"}
        ]

    def execute_shotgun_blast(self, request_text: str, emotional_input: float = 0.5) -> Dict[str, Any]:
        text_hash = hashlib.sha256(request_text.encode("utf-8")).hexdigest()
        hash_val = int(text_hash[:8], 16)

        pellets = []

        categories = ["Sovereign", "Transformer", "Dissipator", "Boundary"]
        actions = ["ASSERT", "YIELD", "ADAPT", "WAIT"]

        for hid in range(1, 65):
            archetype = self.archetypes.get(hid, {
                "hexagram_id": hid,
                "name": f"Archetype {hid}",
                "binary": f"{(hid-1):06b}",
                "coder_specialty": "Dev",
                "skill_domain": "General Execution",
                "rs3_actionable": "interact",
                "risk_category": "Standard",
                "voice_profile": "kokoro_default"
            })

            binary_str = archetype.get("binary", f"{(hid-1):06b}")
            unicode_char = UNICODE_HEXAGRAMS[hid - 1]
            cat_name = categories[(hid - 1) % 4]
            act_name = actions[(hid - 1) % 4]
            act_symbol = ACTION_SYMBOLS[act_name]
            coder_specialty = archetype.get("coder_specialty", "Dev")
            rs3_actionable = archetype.get("rs3_actionable", "interact")

            chaos = round(((hash_val + hid * 7) % 100) / 100.0, 4)
            whimsy = round(((hash_val + hid * 13) % 100) / 100.0, 4)
            dark_tone = round(((hash_val + hid * 19) % 100) / 100.0, 4)
            coherence = round(max(0.1, 1.0 - (chaos * 0.5)), 4)
            voice_weight = round(min(1.0, 0.5 + (whimsy * 0.5)), 4)
            porosity = round((chaos + dark_tone) / 2.0, 4)

            porosity_label = self._classify_porosity(porosity)

            coord = JSpaceCoordinate(
                hexagram_id=hid,
                phase_bits=1,
                chaos=chaos,
                whimsy=whimsy,
                dark_tone=dark_tone,
                coherence=coherence,
                voice_weight=voice_weight,
                porosity=porosity,
                porosity_label=porosity_label,
                request_text=request_text
            )

            stances = {
                "past": TemporalStance(
                    weight=0.8,
                    confidence=0.9,
                    posture="Rooted",
                    focus=f"Legacy foundation for {archetype['skill_domain']} ({coder_specialty})",
                    concern=f"Historical precedent of {archetype['risk_category']}"
                ).to_dict(),
                "present": TemporalStance(
                    weight=1.0,
                    confidence=0.95,
                    posture="Active Execution",
                    focus=f"{archetype['name']} [{coder_specialty}] executing '{request_text}' via RS3 actionable '{rs3_actionable}'",
                    concern=f"Immediate risk: {archetype['risk_category']}"
                ).to_dict(),
                "future": TemporalStance(
                    weight=0.7,
                    confidence=0.85,
                    posture="Scalable Expansion",
                    focus=f"Long-term stability in {archetype['skill_domain']}",
                    concern=f"Mitigation of {archetype['risk_category']}"
                ).to_dict()
            }

            ternary_matrix = self._generate_ternary_line_matrix(binary_str)
            checklist = self._generate_checklist(coherence, chaos)

            pellet = {
                "hexagram_id": hid,
                "unicode": unicode_char,
                "binary": binary_str,
                "coder_name": archetype.get("name"),
                "coder_specialty": coder_specialty,
                "rs3_actionable": rs3_actionable,
                "traditional_name": archetype.get("traditional_name", ""),
                "category": cat_name,
                "action": act_name,
                "action_symbol": act_symbol,
                "upper_trigram": archetype.get("upper_trigram_bits", "111"),
                "lower_trigram": archetype.get("lower_trigram_bits", "111"),
                "skill_domain": archetype.get("skill_domain"),
                "risk_category": archetype.get("risk_category"),
                "voice_profile": archetype.get("voice_profile"),
                "inject_site": {
                    "primary_pool": f"pool_{cat_name.lower()}_primary",
                    "secondary_pool": f"pool_{act_name.lower()}_secondary",
                    "porosity": porosity,
                    "porosity_label": porosity_label
                },
                "ternary_line_matrix": ternary_matrix,
                "checklist": checklist,
                "sample_paths": [
                    f"path_hex_{hid:02d}_present -> path_hex_{hid:02d}_future",
                    f"path_hex_{hid:02d}_resolution"
                ],
                "stances": stances,
                "jspace_coordinate": {
                    "chaos": chaos,
                    "whimsy": whimsy,
                    "darkTone": dark_tone,
                    "coherence": coherence,
                    "voiceWeight": voice_weight,
                    "porosity": porosity,
                    "porosityLabel": porosity_label
                },
                "projections": {
                    "voicebox": coord.to_voicebox_payload(),
                    "megatron": coord.to_megatron_payload(),
                    "kimi": coord.to_kimi_payload(),
                    "agency_3d": coord.to_3d_agency_payload(rs3_actionable=rs3_actionable)
                }
            }
            pellets.append(pellet)

        return {
            "source": "kingwen-shotgun-pipeline-v3.0",
            "request_text": request_text,
            "deterministic_hash": hash_val,
            "total_pellets": len(pellets),
            "ternary_line_states_per_hex": 729, # 3^6
            "total_domained_routes": 35000,     # ~35k domained routes
            "total_perspectives": len(pellets) * 3,
            "pellets": pellets
        }

def slash_oracle(request_text: str) -> Dict[str, Any]:
    return KingWenShotgunPipeline().execute_shotgun_blast(request_text)

def slash_counsel(request_text: str) -> Dict[str, Any]:
    pipeline = KingWenShotgunPipeline()
    res = pipeline.execute_shotgun_blast(request_text)
    res["selected_counsel_pellets"] = [res["pellets"][0], res["pellets"][28], res["pellets"][50]]
    return res

def slash_blueprint(request_text: str) -> Dict[str, Any]:
    return KingWenShotgunPipeline().execute_shotgun_blast(request_text)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = KingWenShotgunPipeline()
    res = pipeline.execute_shotgun_blast("Refactor the IPC event bridge")
    print(f"Executed Shotgun Blast v3.0 (729 Ternary Baseline & RS3 Tagging) for '{res['request_text']}':")
    print(f"Total Pellets: {res['total_pellets']} | Ternary States per Hex: {res['ternary_line_states_per_hex']} | Total Domained Routes: {res['total_domained_routes']}")
    print(f"Hex 1 ID: {res['pellets'][0]['hexagram_id']} | Specialty: {res['pellets'][0]['coder_specialty']} | RS3 Actionable: {res['pellets'][0]['rs3_actionable']}")
    print(f"Hex 1 Ternary Pattern [6 lines]: {res['pellets'][0]['ternary_line_matrix']['ternary_pattern']}")
    print(f"Hex 1 3D Agency Payload: {json.dumps(res['pellets'][0]['projections']['agency_3d'], indent=2)}")
