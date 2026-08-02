"""
kingwen_mobius_sphere.py

Sovereign Avatar Coordinate Backend — Riemann Sphere / Smith Chart Machinery.

Translated from external agent prototype into sovereign stack:
- Source of truth: hexagram-registry.json, emotional-weights.json, inject sites
- No hardcoded RS3 tables; no duplicated canonical data
- Integrates opcode-dispatch + hidden-reference-stack from opcode_reader.ts
- Integrates compositional state-key pattern from kingwen_state_transition.py
- Produces AvatarPayload-compatible output for frontend/lib/avatarProtocol.ts

Analogy:
  head model id# + headwear model id# = composite appearance
  base state (hexagram/phase) + overlay (mask/coherence/vector) = composite identity
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Canonical data loaders (immutable tables, read-only)
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, Any] = {}
_EMOTIONAL_WEIGHTS: Dict[str, Any] = {}
_INJECT_SITES: Dict[str, Any] = {}
_KING_WEN_SEQUENCE: List[int] = []


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _ensure_loaded() -> None:
    global _REGISTRY, _EMOTIONAL_WEIGHTS, _INJECT_SITES, _KING_WEN_SEQUENCE
    if _REGISTRY:
        return
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _REGISTRY = _load_json(os.path.join(repo_root, "data", "hexagram-registry.json"))
    _EMOTIONAL_WEIGHTS = _load_json(os.path.join(repo_root, "data", "emotional-weights.json"))
    inject_path = os.path.join(repo_root, "collapse_full_128_output.json")
    if os.path.exists(inject_path):
        raw = _load_json(inject_path)
        for entry in raw.get("expanded", []):
            hid = str(entry.get("hexagram_id", ""))
            if hid:
                _INJECT_SITES[hid] = entry.get("inject_site", {})
    if not _INJECT_SITES:
        for hid, entry in _REGISTRY.items():
            _INJECT_SITES[hid] = {
                "category": entry.get("category", ""),
                "action": entry.get("action", ""),
            }
    # Canonical sequence from registry order (sorted by id)
    _KING_WEN_SEQUENCE = sorted(int(k) for k in _REGISTRY.keys())


# ---------------------------------------------------------------------------
# Hidden reference stack (mirrors opcode_reader.ts hiddenstack)
# ---------------------------------------------------------------------------

class HiddenStateStack:
    """Prior states for cross-state lookups without polluting public payload."""

    def __init__(self) -> None:
        self._stack: List[Dict[str, Any]] = []

    def push(self, state: Dict[str, Any]) -> None:
        self._stack.append(state)

    def pop(self) -> Optional[Dict[str, Any]]:
        return self._stack.pop() if self._stack else None

    def peek(self, depth: int = 0) -> Optional[Dict[str, Any]]:
        if 0 <= depth < len(self._stack):
            return self._stack[-(depth + 1)]
        return None

    def resolve(self, path: str, default: Any = None) -> Any:
        if not path.startswith("$"):
            return default
        rel = path[1:]
        for frame in reversed(self._stack):
            val = _dotted_lookup(frame, rel)
            if val is not None:
                return val
        return default

    def __len__(self) -> int:
        return len(self._stack)


def _dotted_lookup(d: Dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    cur: Any = d
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


# ---------------------------------------------------------------------------
# Riemann sphere math
# ---------------------------------------------------------------------------

@dataclass
class MobiusState:
    real: float = 0.0
    imag: float = 0.0
    magnitude: float = 0.0
    angle_deg: float = 0.0

    @property
    def gamma(self) -> complex:
        return complex(self.real, self.imag)

    def to_dict(self) -> dict:
        return {
            "real": self.real,
            "imag": self.imag,
            "magnitude": self.magnitude,
            "angle_deg": self.angle_deg,
        }


@dataclass
class RiemannCoords:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    @property
    def latitude(self) -> float:
        return math.degrees(math.asin(max(-1.0, min(1.0, self.z))))

    @property
    def longitude(self) -> float:
        return math.degrees(math.atan2(self.y, self.x))


class RiemannSphere:
    """Stereographic projection between complex plane and unit sphere."""

    @staticmethod
    def plane_to_sphere(z: complex) -> RiemannCoords:
        x, y = z.real, z.imag
        r2 = x * x + y * y
        denom = 1.0 + r2
        if denom == 0:
            return RiemannCoords(0.0, 0.0, -1.0)
        return RiemannCoords(
            x=2.0 * x / denom,
            y=2.0 * y / denom,
            z=(1.0 - r2) / denom,
        )

    @staticmethod
    def sphere_to_plane(coords: RiemannCoords) -> complex:
        X, Y, Z = coords.x, coords.y, coords.z
        if abs(Z + 1.0) < 1e-12:
            return complex(float("inf"), float("inf"))
        denom = 1.0 + Z
        return complex(X / denom, Y / denom)

    @staticmethod
    def mobius_map(z: complex) -> complex:
        if z == -1:
            return complex(float("inf"), 0)
        return (z - 1) / (z + 1)

    @staticmethod
    def inverse_mobius(gamma: complex) -> complex:
        if gamma == 1:
            return complex(float("inf"), 0)
        return (1 + gamma) / (1 - gamma)


# ---------------------------------------------------------------------------
# Enums / helpers
# ---------------------------------------------------------------------------

class Hemisphere(Enum):
    NORTH = "north"
    SOUTH = "south"
    EQUATOR = "equator"
    VOID = "void"


class Phase(Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    TRANSITION = "transition"
    RESOLUTION = "resolution"
    DISSOLUTION = "dissolution"
    CRYSTALLIZATION = "crystallization"
    VOID = "void"


_VOID_HEXES = {15, 20, 30, 40}

_PHASE_ROTATION = {
    "past": 0.0,
    "present": 45.0,
    "future": 90.0,
    "transition": 135.0,
    "resolution": 180.0,
    "dissolution": 225.0,
    "crystallization": 270.0,
    "void": 315.0,
}

_WU_XING_COLORS = {
    "wood": "#4ade80",
    "fire": "#f87171",
    "earth": "#fbbf24",
    "metal": "#94a3b8",
    "water": "#60a5fa",
    "void": "#1e293b",
}


# ---------------------------------------------------------------------------
# Node model (frontend-compatible)
# ---------------------------------------------------------------------------

@dataclass
class HexagramNode:
    id: int
    name: str
    unicode: str
    binary: str
    x: float
    y: float
    z: float
    radius: float
    color: str
    opacity: float
    phase: str
    voiceWeight: float
    coherence: float
    chaos: float
    whimsy: float
    darkTone: float
    porosity: float
    void_mask: bool = False
    hemisphere: str = "north"
    mobius_gamma: dict = field(default_factory=dict)
    riemann_coords: dict = field(default_factory=dict)
    latitude: float = 0.0
    longitude: float = 0.0
    live_bits: int = 0
    scale_factor: float = 1.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Hexagram registry lookups (no hardcoded tables)
# ---------------------------------------------------------------------------

def _hex_registry(hex_id: int) -> Dict[str, Any]:
    return _REGISTRY.get(str(hex_id), {})


def _hex_binary(hex_id: int) -> str:
    reg = _hex_registry(hex_id)
    bin_str = str(reg.get("binary", "000000"))
    if len(bin_str) != 6:
        bin_str = format(hex_id - 1, "06b")
    return bin_str


def _hex_trigram_ternary(hex_id: int) -> Tuple[str, str]:
    reg = _hex_registry(hex_id)
    upper = str(reg.get("upper_trigram_ternary", "000"))
    lower = str(reg.get("lower_trigram_ternary", "000"))
    if len(upper) != 3 or len(lower) != 3:
        # Fallback: derive from binary
        bin6 = _hex_binary(hex_id)
        upper = bin6[0:3]
        lower = bin6[3:6]
    return upper, lower


def _hex_name(hex_id: int) -> str:
    reg = _hex_registry(hex_id)
    return str(reg.get("name", f"Hexagram {hex_id}"))


def _hex_unicode(hex_id: int) -> str:
    reg = _hex_registry(hex_id)
    return str(reg.get("unicode", ""))


def _live_bits_from_binary(binary: str) -> int:
    return binary.count("1")


# ---------------------------------------------------------------------------
# Core sphere mapper
# ---------------------------------------------------------------------------

class HexagramRiemannSphere:
    """
    Maps 64 hexagrams onto Riemann sphere via ternary→complex→Möbius→stereographic.
    """

    def __init__(self, reference_impedance: float = 50.0):
        _ensure_loaded()
        self.sphere = RiemannSphere()
        self.Z0 = reference_impedance
        self.hex_to_index = {h: i for i, h in enumerate(_KING_WEN_SEQUENCE)}
        self.index_to_hex = {i: h for i, h in enumerate(_KING_WEN_SEQUENCE)}

    def _ternary_to_complex(self, upper: str, lower: str, live_bits: int = 6) -> complex:
        def trigram_value(t: str) -> float:
            return sum(int(t[i]) * (3 ** i) for i in range(3)) / 13.0

        real = trigram_value(upper)
        imag = trigram_value(lower)
        scale = live_bits / 6.0 if live_bits > 0 else 0.05
        real = 0.5 + real * scale
        imag = (imag - 0.5) * scale
        return complex(real, imag)

    def _get_hemisphere(self, gamma_mag: float, is_void: bool) -> Hemisphere:
        if is_void:
            return Hemisphere.VOID
        if gamma_mag < 0.95:
            return Hemisphere.NORTH
        elif gamma_mag > 1.05:
            return Hemisphere.SOUTH
        return Hemisphere.EQUATOR

    def _get_color(self, hex_num: int, hemisphere: Hemisphere, live_bits: int) -> str:
        if hemisphere == Hemisphere.VOID:
            return _WU_XING_COLORS["void"]
        reg = _hex_registry(hex_num)
        category = str(reg.get("category", "")).lower()
        if category in (" generative", "wood", "creation"):
            return _WU_XING_COLORS["wood"]
        if category in ("transformative", "fire", "action"):
            return _WU_XING_COLORS["fire"]
        if category in ("analytic", "metal", "structure"):
            return _WU_XING_COLORS["metal"]
        if category in ("grounding", "earth", "receptive"):
            return _WU_XING_COLORS["earth"]
        return _WU_XING_COLORS["water"] if hemisphere == Hemisphere.SOUTH else _WU_XING_COLORS["metal"]

    def hexagram_to_node(
        self,
        hex_number: int,
        phase: str = "present",
        live_bits: Optional[int] = None,
        coherence: float = 0.5,
        chaos: float = 0.5,
        whimsy: float = 0.5,
        dark_tone: float = 0.3,
        porosity: float = 0.5,
        voice_weight: float = 1.0,
    ) -> HexagramNode:
        """
        Convert hexagram to Riemann-sphere avatar node.
        Replaces ggwaveBridge.ts::binaryToSphereCoords().
        """
        is_void = hex_number in _VOID_HEXES
        binary = _hex_binary(hex_number)
        if live_bits is None:
            live_bits = _live_bits_from_binary(binary)
        upper, lower = _hex_trigram_ternary(hex_number)

        if is_void:
            coords = RiemannCoords(0.0, 0.0, -1.0)
            mobius = MobiusState(real=0.0, imag=0.0, magnitude=float("inf"), angle_deg=0.0)
            hemisphere = Hemisphere.VOID
            radius = 0.3
            opacity = 0.4
        else:
            z = self._ternary_to_complex(upper, lower, live_bits)
            rot_deg = _PHASE_ROTATION.get(phase, 0.0)
            rot_rad = math.radians(rot_deg)
            gamma_rot = z * complex(math.cos(rot_rad), math.sin(rot_rad))
            gamma = self.sphere.mobius_map(gamma_rot)
            coords = self.sphere.plane_to_sphere(gamma)
            mag = abs(gamma)
            ang = math.degrees(math.atan2(gamma.imag, gamma.real))
            mobius = MobiusState(
                real=gamma.real,
                imag=gamma.imag,
                magnitude=mag if mag < 1e6 else float("inf"),
                angle_deg=ang,
            )
            hemisphere = self._get_hemisphere(mag, is_void)
            base_radius = 0.5 + (live_bits / 6.0) * 0.8
            radius = base_radius * (0.8 + coherence * 0.4)
            opacity = 0.6 + porosity * 0.3

        return HexagramNode(
            id=hex_number,
            name=_hex_name(hex_number),
            unicode=_hex_unicode(hex_number),
            binary=binary,
            x=round(coords.x, 6),
            y=round(coords.y, 6),
            z=round(coords.z, 6),
            radius=round(radius, 4),
            color=self._get_color(hex_number, hemisphere, live_bits),
            opacity=round(opacity, 4),
            phase=phase,
            voiceWeight=round(voice_weight, 4),
            coherence=round(coherence, 4),
            chaos=round(chaos, 4),
            whimsy=round(whimsy, 4),
            darkTone=round(dark_tone, 4),
            porosity=round(porosity, 4),
            void_mask=is_void,
            hemisphere=hemisphere.value,
            mobius_gamma=mobius.to_dict(),
            riemann_coords=coords.to_dict(),
            latitude=round(coords.latitude, 4),
            longitude=round(coords.longitude, 4),
            live_bits=live_bits,
            scale_factor=round(1.2 + live_bits / 6 * 1.4, 4),
        )

    def sphere_to_hexagram(self, x: float, y: float, z: float) -> int:
        coords = RiemannCoords(x, y, z)
        if z < -0.99:
            return 48
        gamma = self.sphere.sphere_to_plane(coords)
        z_impedance = self.sphere.inverse_mobius(gamma)
        best_hex = 1
        best_dist = float("inf")
        for hex_num in _KING_WEN_SEQUENCE:
            if hex_num in _VOID_HEXES:
                continue
            upper, lower = _hex_trigram_ternary(hex_num)
            z_candidate = self._ternary_to_complex(upper, lower, live_bits=6)
            dist = abs(z_impedance - z_candidate)
            if dist < best_dist:
                best_dist = dist
                best_hex = hex_num
        return best_hex

    def get_all_nodes(self, phase: str = "present", live_bits_map: Optional[Dict[int, int]] = None) -> List[HexagramNode]:
        nodes = []
        for hex_num in _KING_WEN_SEQUENCE:
            lb = live_bits_map.get(hex_num, 6) if live_bits_map else 6
            nodes.append(self.hexagram_to_node(hex_num, phase=phase, live_bits=lb))
        return nodes

    def export_avatar_payload(
        self,
        session_id: str,
        phase: str = "present",
        live_bits_map: Optional[Dict[int, int]] = None,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        nodes = self.get_all_nodes(phase, live_bits_map)
        sorted_nodes = sorted(nodes, key=lambda n: n.coherence, reverse=True)
        connection_ring = [n.id for n in sorted_nodes[:12]]
        dominant = sorted_nodes[0] if sorted_nodes else nodes[0]

        return {
            "session_id": session_id,
            "mode": "human",
            "state_signature": "",  # caller should inject
            "nodes": [n.to_dict() for n in nodes],
            "dominant": dominant.to_dict(),
            "transition_tone": None,
            "timestamp": timestamp,
            "sphere": {
                "type": "riemann",
                "projection": "stereographic_south_pole",
                "mobiusTransform": "(z-1)/(z+1)",
                "voidHexes": sorted(_VOID_HEXES),
                "northHemisphereCount": sum(1 for n in nodes if n.hemisphere == "north"),
                "southHemisphereCount": sum(1 for n in nodes if n.hemisphere == "south"),
                "equatorCount": sum(1 for n in nodes if n.hemisphere == "equator"),
                "voidCount": sum(1 for n in nodes if n.hemisphere == "void"),
            },
            "meta": {
                "totalNodes": len(nodes),
                "activeNodes": len(nodes) - len(_VOID_HEXES),
                "voidNodes": len(_VOID_HEXES),
                "coordinateBackend": "kingwen_mobius_sphere.py",
                "version": "1.0.0",
            },
        }


# ---------------------------------------------------------------------------
# Conformal pathing — great-circle transitions
# ---------------------------------------------------------------------------

class ConformalPathing:
    @staticmethod
    def spherical_distance(a: RiemannCoords, b: RiemannCoords) -> float:
        dot = max(-1.0, min(1.0, a.x * b.x + a.y * b.y + a.z * b.z))
        return math.acos(dot)

    @staticmethod
    def slerp(a: RiemannCoords, b: RiemannCoords, t: float) -> RiemannCoords:
        omega = ConformalPathing.spherical_distance(a, b)
        if omega < 1e-10:
            return a
        sin_omega = math.sin(omega)
        wa = math.sin((1 - t) * omega) / sin_omega
        wb = math.sin(t * omega) / sin_omega
        return RiemannCoords(
            x=wa * a.x + wb * b.x,
            y=wa * a.y + wb * b.y,
            z=wa * a.z + wb * b.z,
        )

    @staticmethod
    def hexagram_transition_path(
        sphere: HexagramRiemannSphere,
        from_hex: int,
        to_hex: int,
        steps: int = 30,
        phase: str = "transition",
    ) -> List[HexagramNode]:
        node_a = sphere.hexagram_to_node(from_hex, phase=phase)
        node_b = sphere.hexagram_to_node(to_hex, phase=phase)
        coords_a = RiemannCoords(node_a.x, node_a.y, node_a.z)
        coords_b = RiemannCoords(node_b.x, node_b.y, node_b.z)
        path = []
        for i in range(steps + 1):
            t = i / steps
            interp = ConformalPathing.slerp(coords_a, coords_b, t)
            nearest = sphere.sphere_to_hexagram(interp.x, interp.y, interp.z)
            if nearest is None:
                nearest = from_hex if t < 0.5 else to_hex
            node = sphere.hexagram_to_node(nearest, phase=phase)
            node.x = round(interp.x, 6)
            node.y = round(interp.y, 6)
            node.z = round(interp.z, 6)
            path.append(node)
        return path


# ---------------------------------------------------------------------------
# Opcode dispatch + compositional state (from kingwen_state_transition.py)
# ---------------------------------------------------------------------------

class TransitionOpcode(Enum):
    MOBIUS = "mobius"
    STEREOGRAPHIC = "stereographic"
    NULL_VOID = "null_void"
    GAUSSIAN_FUTURE = "gaussian_future"
    IDENTITY = "identity"


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def compose_state_key(
    hexagram_id: int,
    phase_bits: int,
    mask: str,
    coherence: float,
    porosity: float,
) -> str:
    return f"{hexagram_id}:{phase_bits}:{mask}:{coherence:.4f}:{porosity:.4f}"


def parse_state_key(key: str) -> Dict[str, Any]:
    parts = key.split(":")
    if len(parts) != 5:
        raise ValueError(f"Invalid state key: {key}")
    return {
        "hexagram_id": int(parts[0]),
        "phase_bits": int(parts[1]),
        "mask": parts[2],
        "coherence": float(parts[3]),
        "porosity": float(parts[4]),
    }


def state_digest(state: Dict[str, Any]) -> str:
    canonical = compose_state_key(
        int(state.get("hexagram_id", 0)),
        int(state.get("phase_bits", 0)),
        str(state.get("mask", "PASS")),
        float(state.get("coherence", 0.5)),
        float(state.get("porosity", 0.5)),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class KingwenMobiusSphere:
    """
    Unified entry point for avatar coordinate generation + state transitions.

    Replaces:
      - frontend/src/lib/ggwaveBridge.ts::binaryToSphereCoords()
      - kingwen_state_transition.py opcode dispatch (subset)
    """

    def __init__(self) -> None:
        _ensure_loaded()
        self.sphere = HexagramRiemannSphere()
        self._hidden = HiddenStateStack()

    def node(
        self,
        hexagram_id: int,
        phase: str = "present",
        mask: str = "PASS",
        coherence: float = 0.5,
        porosity: float = 0.5,
        voice_weight: float = 1.0,
        live_bits: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Single hexagram node, ready for AvatarPayload."""
        node = self.sphere.hexagram_to_node(
            hex_number=hexagram_id,
            phase=phase,
            live_bits=live_bits,
            coherence=coherence,
            porosity=porosity,
            voice_weight=voice_weight,
        )
        state = node.to_dict()
        state["mask"] = mask
        state["state_key"] = compose_state_key(hexagram_id, 0, mask, coherence, porosity)
        state["digest"] = state_digest(state)
        return state

    def transition(
        self,
        hexagram_id: int,
        phase_bits: int,
        mask: str = "PASS",
        coherence: float = 0.5,
        porosity: float = 0.5,
        opcode: TransitionOpcode = TransitionOpcode.IDENTITY,
    ) -> Dict[str, Any]:
        """State transition with hidden-stack history."""
        base = {
            "hexagram_id": hexagram_id,
            "phase_bits": phase_bits,
            "mask": mask,
            "coherence": coherence,
            "porosity": porosity,
        }
        self._hidden.push(base)
        try:
            if opcode == TransitionOpcode.MOBIUS:
                result = self._mobius_transition(base)
            elif opcode == TransitionOpcode.STEREOGRAPHIC:
                result = self._stereographic_transition(base)
            elif opcode == TransitionOpcode.NULL_VOID:
                result = self._null_void_transition(base)
            elif opcode == TransitionOpcode.GAUSSIAN_FUTURE:
                result = self._gaussian_future_transition(base)
            else:
                result = dict(base)
            result["state_key"] = compose_state_key(
                int(result.get("hexagram_id", hexagram_id)),
                int(result.get("phase_bits", phase_bits)),
                str(result.get("mask", mask)),
                float(result.get("coherence", coherence)),
                float(result.get("porosity", porosity)),
            )
            result["digest"] = state_digest(result)
            return result
        finally:
            pass  # keep history

    def stack(self, current: Dict[str, Any], mask: Optional[str] = None, coherence: Optional[float] = None, porosity: Optional[float] = None) -> Dict[str, Any]:
        """Compose overlay on current state (headwear stacking)."""
        composite = dict(current)
        if mask is not None:
            composite["mask"] = mask
        if coherence is not None:
            composite["coherence"] = coherence
        if porosity is not None:
            composite["porosity"] = porosity
        composite["state_key"] = compose_state_key(
            int(composite.get("hexagram_id", 0)),
            int(composite.get("phase_bits", 0)),
            str(composite.get("mask", "PASS")),
            float(composite.get("coherence", 0.5)),
            float(composite.get("porosity", 0.5)),
        )
        composite["digest"] = state_digest(composite)
        return composite

    def batch_compose(self, specs: List[Tuple[int, str, str, float]]) -> List[Dict[str, Any]]:
        results = []
        for hex_id, phase, mask, coherence in specs:
            porosity = self._resolve_porosity(hex_id, mask)
            result = self.node(hex_id, phase=phase, mask=mask, coherence=coherence, porosity=porosity)
            results.append(result)
        return results

    def resolve_from_key(self, state_key: str) -> Dict[str, Any]:
        parsed = parse_state_key(state_key)
        return self.node(
            parsed["hexagram_id"],
            phase="present",
            mask=parsed["mask"],
            coherence=parsed["coherence"],
            porosity=parsed["porosity"],
        )

    def _resolve_porosity(self, hex_id: int, mask: str) -> float:
        hid = str(hex_id)
        site = _INJECT_SITES.get(hid, {})
        if "porosity" in site and isinstance(site["porosity"], (int, float)):
            return float(site["porosity"])
        ew = _EMOTIONAL_WEIGHTS.get(hid, {})
        if "porosity" in ew:
            return float(ew["porosity"])
        reg = _hex_registry(hex_id)
        return float(reg.get("porosity", 0.5))

    def _mobius_transition(self, base: Dict[str, Any]) -> Dict[str, Any]:
        hex_id = int(base.get("hexagram_id", 1))
        phase = int(base.get("phase_bits", 0))
        z_real = (hex_id - 32) / 32.0
        z_imag = (phase - 3.5) / 3.5
        gamma_real, gamma_imag = _mobius(z_real, z_imag)
        mag = math.sqrt(gamma_real ** 2 + gamma_imag ** 2)
        theta = math.atan2(gamma_imag, gamma_real)
        return {
            **base,
            "mobius_gamma": {"real": gamma_real, "imag": gamma_imag, "mag": mag, "theta": theta},
            "transition": "mobius",
        }

    def _stereographic_transition(self, base: Dict[str, Any]) -> Dict[str, Any]:
        hex_id = int(base.get("hexagram_id", 1))
        node = self.sphere.hexagram_to_node(hex_id)
        coords = RiemannCoords(node.x, node.y, node.z)
        u, v = RiemannSphere.sphere_to_plane(coords)
        x2, y2, z2 = RiemannSphere.plane_to_sphere(complex(u, v)).to_dict().values()
        inv_err = math.sqrt((node.x - x2) ** 2 + (node.y - y2) ** 2 + (node.z - z2) ** 2)
        return {
            **base,
            "sphere": coords.to_dict(),
            "stereographic": {"u": u, "v": v, "inverse_error": inv_err},
            "transition": "stereographic",
        }

    def _null_void_transition(self, base: Dict[str, Any]) -> Dict[str, Any]:
        hex_id = int(base.get("hexagram_id", 1))
        is_void = hex_id in _VOID_HEXES
        return {
            **base,
            "void": is_void,
            "projection": "south_pole" if is_void else "none",
            "transition": "null_void",
        }

    def _gaussian_future_transition(self, base: Dict[str, Any]) -> Dict[str, Any]:
        fwhm = float(base.get("future_fwhm", 2.5))
        phases = list(range(8))
        bias = [_gaussian_bias_weight(p, fwhm) for p in phases]
        total = sum(bias)
        if total > 0:
            bias = [b / total for b in bias]
        return {
            **base,
            "future_fwhm": fwhm,
            "phase_bias": bias,
            "future_weight": bias[2] if len(bias) > 2 else 0.0,
            "transition": "gaussian_future",
        }


# ---------------------------------------------------------------------------
# Module-level math helpers
# ---------------------------------------------------------------------------

def _mobius(z_real: float, z_imag: float, z0_real: float = 1.0, z0_imag: float = 0.0) -> Tuple[float, float]:
    denom_real = z_real + z0_real
    denom_imag = z_imag + z0_imag
    if abs(denom_real) < 1e-12 and abs(denom_imag) < 1e-12:
        return float("inf"), float("inf")
    num_real = z_real - z0_real
    num_imag = z_imag - z0_imag
    denom_mag2 = denom_real ** 2 + denom_imag ** 2
    out_real = (num_real * denom_real + num_imag * denom_imag) / denom_mag2
    out_imag = (num_imag * denom_real - num_real * denom_imag) / denom_mag2
    return out_real, out_imag


def _gaussian_bias_weight(phase: int, fwhm: float) -> float:
    centers = {0: 0.1, 1: 0.3, 2: 2.0, 3: 0.4, 4: 0.6, 5: 0.5, 6: 0.7, 7: 0.2}
    center = centers.get(phase, 0.5)
    sigma = fwhm / 2.354820045
    diff = phase - center
    return math.exp(-(diff * diff) / (2.0 * sigma * sigma))


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    backend = KingwenMobiusSphere()

    print("=== Sovereign Riemann Sphere Backend ===")
    print()

    # Node generation
    n1 = backend.node(hexagram_id=1, phase="present", coherence=0.9, porosity=0.7)
    print(f"Hex 1 node: ({n1['x']:+.3f}, {n1['y']:+.3f}, {n1['z']:+.3f}) "
          f"|Γ|={n1['mobius_gamma'].get('magnitude', 0):.3f} "
          f"hem={n1['hemisphere']} void={n1['void_mask']}")

    n52 = backend.node(hexagram_id=52, phase="future", live_bits=4, coherence=0.8)
    print(f"Hex 52 node: ({n52['x']:+.3f}, {n52['y']:+.3f}, {n52['z']:+.3f}) "
          f"lat={n52['latitude']:+.1f}° lon={n52['longitude']:+.1f}°")

    n15 = backend.node(hexagram_id=15, phase="present", mask="MEASURE", coherence=0.0, porosity=0.0)
    print(f"Hex 15 void: ({n15['x']:+.3f}, {n15['y']:+.3f}, {n15['z']:+.3f}) "
          f"hem={n15['hemisphere']} void={n15['void_mask']}")

    # Transition
    t1 = backend.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8, opcode=TransitionOpcode.MOBIUS)
    print(f"t1 mobius: mag={t1['mobius_gamma']['mag']:.3f} theta={t1['mobius_gamma']['theta']:.3f}")

    t2 = backend.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8, opcode=TransitionOpcode.GAUSSIAN_FUTURE)
    print(f"t2 future bias: future_weight={t2['future_weight']:.4f} sum={sum(t2['phase_bias']):.4f}")

    # Stack
    stacked = backend.stack(t1, mask="SEVER", coherence=0.3)
    print(f"stacked: mask={stacked['mask']} coherence={stacked['coherence']} key={stacked['state_key']}")

    # Batch
    batch = backend.batch_compose([(i, "present", "PASS", 0.5) for i in range(1, 9)])
    print(f"batch: {len(batch)} nodes, {len(set(n['state_key'] for n in batch))} unique keys")

    # Payload
    payload = backend.sphere.export_avatar_payload("demo-session", phase="present")
    print(f"payload: {payload['meta']['totalNodes']} nodes, "
          f"north={payload['sphere']['northHemisphereCount']} "
          f"south={payload['sphere']['southHemisphereCount']} "
          f"void={payload['sphere']['voidCount']}")

    # Path
    path = ConformalPathing.hexagram_transition_path(backend.sphere, 1, 48, steps=5)
    print(f"path 1->48: {len(path)} steps")
    for i, node in enumerate(path):
        print(f"  step {i}: hex {node.id} @ ({node.x:+.3f}, {node.y:+.3f}, {node.z:+.3f})")

    print("\nPY_VERIFY_OK")
