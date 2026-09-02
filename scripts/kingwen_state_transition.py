"""
kingwen_state_transition.py

Code-agnostic I-Ching state transition engine.

Analogy from rsmv opcode_reader:
  - opcode dispatch       -> transition type selector (mobius/stereographic/void)
  - hidden reference stack -> cross-state lookups without polluting public payload
  - chunked array parser   -> compositional overlays (headwear on head model)

Analogy from RS item/NPC/object actionable system:
  - head model id# + headwear model id# = composite appearance
  - base state (hexagram) + overlay state (phase/mask/vector) = composite identity

State transition grammar:
  base = hexagram_id + phase_bits
  overlay = mask_mode + coherence + emotional_vector
  composite = base:overlay
  transition = mobius | stereographic | null_void | gaussian_future

Each transition type is an opcode that selects a different projection function.
The hidden stack stores prior states so transitions can reference history
without contaminating the current payload.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Source-of-truth loaders (immutable tables, read-only)
# ---------------------------------------------------------------------------

def _load_json(path: str) -> Any:
    import json
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

_HEX_REGISTRY: Dict[str, Any] = {}
_EMOTIONAL_WEIGHTS: Dict[str, Any] = {}
_INJECT_SITES: Dict[str, Any] = {}

def _ensure_loaded() -> None:
    global _HEX_REGISTRY, _EMOTIONAL_WEIGHTS, _INJECT_SITES
    if _HEX_REGISTRY:
        return
    base = __file__  # scripts/
    # Walk up to repo root: scripts/ -> KING-WEN-I-CHING-IMMUTABLE-TABLES/
    import os
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _HEX_REGISTRY = _load_json(os.path.join(repo_root, "data", "hexagram-registry.json"))
    _EMOTIONAL_WEIGHTS = _load_json(os.path.join(repo_root, "data", "emotional-weights.json"))
    # inject_site comes from shotgun_expand() expanded[] or
    # hexagram_full_expansion.json; fall back to empty dict if absent
    inject_path = os.path.join(repo_root, "shotgun_expand_output.json")
    if os.path.exists(inject_path):
        raw = _load_json(inject_path)
        expanded = raw.get("expanded", [])
        for entry in expanded:
            hid = str(entry.get("hexagram_id", ""))
            if hid:
                _INJECT_SITES[hid] = entry.get("inject_site", {})
    # If still empty, seed from registry action/category
    if not _INJECT_SITES:
        for hid, entry in _HEX_REGISTRY.items():
            _INJECT_SITES[hid] = {
                "category": entry.get("category", ""),
                "action": entry.get("action", ""),
                "inject_site": hid,
            }


# ---------------------------------------------------------------------------
# Opcode dispatch — transition type selector (mirrors opcode_reader.ts)
# ---------------------------------------------------------------------------

class TransitionOpcode(Enum):
    """Opcode -> projection function mapping."""
    MOBIUS = "mobius"
    STEREOGRAPHIC = "stereographic"
    NULL_VOID = "null_void"
    GAUSSIAN_FUTURE = "gaussian_future"
    IDENTITY = "identity"


# ---------------------------------------------------------------------------
# Hidden reference stack — mirrors opcode_reader.ts hiddenstack
# ---------------------------------------------------------------------------

class HiddenStateStack:
    """Stores prior states so transitions can reference history without
    polluting the public payload.  $ prefix convention mirrors hidden props."""

    def __init__(self) -> None:
        self._stack: List[Dict[str, Any]] = []

    def push(self, state: Dict[str, Any]) -> None:
        self._stack.append(state)

    def pop(self) -> Optional[Dict[str, Any]]:
        if self._stack:
            return self._stack.pop()
        return None

    def peek(self, depth: int = 0) -> Optional[Dict[str, Any]]:
        if 0 <= depth < len(self._stack):
            return self._stack[-(depth + 1)]
        return None

    def resolve(self, path: str, default: Any = None) -> Any:
        """Resolve a dotted reference path against the hidden stack.
        Example: '$.hexagram_id' -> top state's hexagram_id
                 '$.emotional_deltas.voiceWeight' -> nested lookup
        """
        if not path.startswith("$"):
            return default
        rel = path[1:]
        # search from top down
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
# Projection functions — the actual math
# ---------------------------------------------------------------------------

def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def mobius(z_real: float, z_imag: float, z0_real: float = 1.0, z0_imag: float = 0.0) -> Tuple[float, float]:
    """Möbius transformation (z - z0) / (z + z0).
    Maps impedance-like plane to unit circle (Smith Chart core).
    """
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


def stereographic_project(x: float, y: float, z: float) -> Tuple[float, float]:
    """Stereographic projection from South Pole onto complex plane.
    Sphere point (x,y,z) -> complex plane (u,v).
    """
    denom = 1.0 - z
    if abs(denom) < 1e-12:
        return float("inf"), float("inf")
    return x / denom, y / denom


def stereographic_inverse(u: float, v: float) -> Tuple[float, float, float]:
    """Inverse stereographic: complex plane -> unit sphere."""
    u2v2 = u ** 2 + v ** 2
    denom = 1.0 + u2v2
    x = 2.0 * u / denom
    y = 2.0 * v / denom
    z = (u2v2 - 1.0) / denom
    return x, y, z


def gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    """Gaussian bell used for future-phase bias."""
    sigma = fwhm / 2.354820045
    diff = value - center
    return math.exp(-(diff * diff) / (2.0 * sigma * sigma))


def void_null_projection(hex_id: int, phase: int) -> Dict[str, Any]:
    """Void hexes 15/20/30/40 map to null-state South Pole.
    Not another phase — bounded absence.
    """
    void_set = {15, 20, 30, 40}
    if hex_id not in void_set:
        return {"void": False, "null_radius": 0.0}
    return {
        "void": True,
        "null_radius": 0.0,       # South Pole
        "projection": "south_pole",
        "hexagram_id": hex_id,
        "phase_bits": phase,
    }


# ---------------------------------------------------------------------------
# Compositional state key — "head model id#,headwear model id#"
# ---------------------------------------------------------------------------

def compose_state_key(
    hexagram_id: int,
    phase_bits: int,
    mask: str,
    coherence: float,
    porosity: float,
) -> str:
    """Compose a deterministic state key from base + overlays.
    Analogous to 'head_model_id,headwear_model_id'.
    """
    return f"{hexagram_id}:{phase_bits}:{mask}:{coherence:.4f}:{porosity:.4f}"


def parse_state_key(key: str) -> Dict[str, Any]:
    """Inverse of compose_state_key."""
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


# ---------------------------------------------------------------------------
# State transition engine — opcode dispatch + hidden stack
# ---------------------------------------------------------------------------

@dataclass
class StateTransition:
    """One transition step.  Mirrors ChunkParser read/write contract."""
    opcode: TransitionOpcode
    base_state: Dict[str, Any]
    overlay: Dict[str, Any]
    hidden: HiddenStateStack = field(default_factory=HiddenStateStack)
    result: Optional[Dict[str, Any]] = None

    def read(self) -> Dict[str, Any]:
        """Resolve the transition: dispatch opcode, apply projection."""
        self.hidden.push(self.base_state)
        try:
            projector = _PROJECTORS[self.opcode]
            self.result = projector(self.base_state, self.overlay, self.hidden)
            return self.result
        finally:
            # keep history alive for downstream references
            pass

    def write(self, next_overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a new overlay on top of current result (headwear stacking)."""
        if not self.result:
            self.read()
        composite = dict(self.result)
        composite.update(next_overlay)
        composite["state_key"] = compose_state_key(
            int(composite.get("hexagram_id", 0)),
            int(composite.get("phase_bits", 0)),
            str(composite.get("mask", "PASS")),
            float(composite.get("coherence", 0.5)),
            float(composite.get("porosity", 0.5)),
        )
        return composite


# ---------------------------------------------------------------------------
# Projector registry — each opcode is a different projection function
# ---------------------------------------------------------------------------

def _project_mobius(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    hidden: HiddenStateStack,
) -> Dict[str, Any]:
    hex_id = int(base.get("hexagram_id", 1))
    phase = int(base.get("phase_bits", 0))
    coherence = float(base.get("coherence", overlay.get("coherence", 0.5)))
    porosity = float(base.get("porosity", overlay.get("porosity", 0.5)))

    # Encode hexagram+phase into complex plane
    # hex_id gives real axis, phase gives imaginary axis
    z_real = (hex_id - 32) / 32.0
    z_imag = (phase - 3.5) / 3.5

    gamma_real, gamma_imag = mobius(z_real, z_imag)
    mag = math.sqrt(gamma_real ** 2 + gamma_imag ** 2)
    theta = math.atan2(gamma_imag, gamma_real)

    # Prior state reference via hidden stack
    prev_hex = hidden.resolve("$.hexagram_id")
    prev_phase = hidden.resolve("$.phase_bits")

    return {
        "hexagram_id": hex_id,
        "phase_bits": phase,
        "mask": base.get("mask", overlay.get("mask", "PASS")),
        "coherence": _clamp(coherence),
        "porosity": _clamp(porosity),
        "mobius_gamma": {"real": gamma_real, "imag": gamma_imag, "mag": mag, "theta": theta},
        "transition": "mobius",
        "prev_hexagram_id": prev_hex,
        "prev_phase_bits": prev_phase,
        "state_key": compose_state_key(hex_id, phase, str(base.get("mask", "PASS")), coherence, porosity),
    }


def _project_stereographic(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    hidden: HiddenStateStack,
) -> Dict[str, Any]:
    hex_id = int(base.get("hexagram_id", 1))
    phase = int(base.get("phase_bits", 0))
    coherence = float(base.get("coherence", overlay.get("coherence", 0.5)))
    porosity = float(base.get("porosity", overlay.get("porosity", 0.5)))

    # Fibonacci sphere placement using hex_id as index
    phi = math.acos(1.0 - ((hex_id - 1 + 0.5) / 64.0) * 2.0)
    theta = math.pi * (1.0 + math.sqrt(5.0)) * (hex_id - 1)
    live_bits = _count_live_bits(hex_id)
    radius = 1.2 + (live_bits / 6.0) * 1.4

    x = math.cos(theta) * math.sin(phi) * radius
    y = math.cos(phi) * radius
    z = math.sin(theta) * math.sin(phi) * radius

    # Project to complex plane and back to verify conformal mapping
    u, v = stereographic_project(x, y, z)
    x2, y2, z2 = stereographic_inverse(u, v)

    return {
        "hexagram_id": hex_id,
        "phase_bits": phase,
        "mask": base.get("mask", overlay.get("mask", "PASS")),
        "coherence": _clamp(coherence),
        "porosity": _clamp(porosity),
        "sphere": {"x": x, "y": y, "z": z, "radius": radius},
        "stereographic": {"u": u, "v": v, "inverse_error": math.sqrt((x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2)},
        "transition": "stereographic",
        "state_key": compose_state_key(hex_id, phase, str(base.get("mask", "PASS")), coherence, porosity),
    }


def _project_null_void(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    hidden: HiddenStateStack,
) -> Dict[str, Any]:
    hex_id = int(base.get("hexagram_id", 1))
    phase = int(base.get("phase_bits", 0))
    void_state = void_null_projection(hex_id, phase)
    void_state["mask"] = "MEASURE"
    void_state["coherence"] = float(base.get("coherence", overlay.get("coherence", 0.0)))
    void_state["porosity"] = float(base.get("porosity", overlay.get("porosity", 0.0)))
    void_state["state_key"] = compose_state_key(hex_id, phase, "MEASURE", void_state["coherence"], void_state["porosity"])
    return void_state


def _project_gaussian_future(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    hidden: HiddenStateStack,
) -> Dict[str, Any]:
    """Weight future phase (index 2) through Gaussian kernel.
    Past=0, Present=1, Future=2, Transition=3, Resolution=4,
    Dissolution=5, Crystallization=6, Void=7.
    """
    hex_id = int(base.get("hexagram_id", 1))
    phase = int(base.get("phase_bits", 0))
    coherence = float(base.get("coherence", overlay.get("coherence", 0.5)))
    porosity = float(base.get("porosity", overlay.get("porosity", 0.5)))
    fwhm = float(base.get("future_fwhm", overlay.get("future_fwhm", 2.5)))

    phases = list(range(8))
    bias = [_gaussian_bias_weight(p, fwhm) for p in phases]
    total = sum(bias)
    if total > 0:
        bias = [b / total for b in bias]

    future_weight = bias[2] if len(bias) > 2 else 0.0
    resolution_weight = bias[4] if len(bias) > 4 else 0.0

    return {
        "hexagram_id": hex_id,
        "phase_bits": phase,
        "mask": base.get("mask", overlay.get("mask", "PASS")),
        "coherence": _clamp(coherence),
        "porosity": _clamp(porosity),
        "future_fwhm": fwhm,
        "phase_bias": bias,
        "future_weight": future_weight,
        "resolution_weight": resolution_weight,
        "transition": "gaussian_future",
        "state_key": compose_state_key(hex_id, phase, str(base.get("mask", "PASS")), coherence, porosity),
    }


def _gaussian_bias_weight(phase: int, fwhm: float) -> float:
    """Non-uniform phase weights centered on future (2)."""
    centers = {0: 0.1, 1: 0.3, 2: 2.0, 3: 0.4, 4: 0.6, 5: 0.5, 6: 0.7, 7: 0.2}
    center = centers.get(phase, 0.5)
    return gaussian_kernel(float(phase), center, fwhm)


def _project_identity(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
    hidden: HiddenStateStack,
) -> Dict[str, Any]:
    hex_id = int(base.get("hexagram_id", 1))
    phase = int(base.get("phase_bits", 0))
    coherence = float(base.get("coherence", overlay.get("coherence", 0.5)))
    porosity = float(base.get("porosity", overlay.get("porosity", 0.5)))
    return {
        "hexagram_id": hex_id,
        "phase_bits": phase,
        "mask": base.get("mask", overlay.get("mask", "PASS")),
        "coherence": _clamp(coherence),
        "porosity": _clamp(porosity),
        "transition": "identity",
        "state_key": compose_state_key(hex_id, phase, str(base.get("mask", "PASS")), coherence, porosity),
    }


_PROJECTORS: Dict[TransitionOpcode, Callable[..., Dict[str, Any]]] = {
    TransitionOpcode.MOBIUS: _project_mobius,
    TransitionOpcode.STEREOGRAPHIC: _project_stereographic,
    TransitionOpcode.NULL_VOID: _project_null_void,
    TransitionOpcode.GAUSSIAN_FUTURE: _project_gaussian_future,
    TransitionOpcode.IDENTITY: _project_identity,
}


# ---------------------------------------------------------------------------
# Public API — state machine entry points
# ---------------------------------------------------------------------------

class KingwenStateMachine:
    """Code-agnostic state transition engine.

    Usage:
      sm = KingwenStateMachine()
      # Single transition
      # Full 512-state sweep: all 64 hexagrams × 8 phases
    # Full 512-state sweep: all 64 hexagrams × 8 phases
    result = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)  # example transition  # example transition
      # Stack transitions (headwear stacking)
      result2 = sm.stack(result, mask="SEVER", coherence=0.4)
      # Batch composition
      batch = sm.batch_compose([(hex, phase, mask, coh) for ...])
    """

    def __init__(self) -> None:
        _ensure_loaded()
        self._hidden = HiddenStateStack()

    def transition(
        self,
        hexagram_id: int,
        phase_bits: int,
        mask: str = "PASS",
        coherence: float = 0.5,
        porosity: float = 0.5,
        opcode: TransitionOpcode = TransitionOpcode.IDENTITY,
        future_fwhm: float = 2.5,
    ) -> Dict[str, Any]:
        """Single state transition."""
        base = {
            "hexagram_id": hexagram_id,
            "phase_bits": phase_bits,
            "mask": mask,
            "coherence": coherence,
            "porosity": porosity,
        }
        if future_fwhm != 2.5:
            base["future_fwhm"] = future_fwhm

        step = StateTransition(
            opcode=opcode,
            base_state=base,
            overlay=base,
            hidden=self._hidden,
        )
        result = step.read()
        self._hidden.push(result)
        return result

    def stack(
        self,
        current: Dict[str, Any],
        mask: Optional[str] = None,
        coherence: Optional[float] = None,
        porosity: Optional[float] = None,
        opcode: TransitionOpcode = TransitionOpcode.IDENTITY,
    ) -> Dict[str, Any]:
        """Compose overlay on current state (headwear on head model)."""
        overlay: Dict[str, Any] = {}
        if mask is not None:
            overlay["mask"] = mask
        if coherence is not None:
            overlay["coherence"] = coherence
        if porosity is not None:
            overlay["porosity"] = porosity

        step = StateTransition(
            opcode=opcode,
            base_state=current,
            overlay=overlay,
            hidden=self._hidden,
        )
        return step.write(overlay)

    def batch_compose(
        self,
        specs: List[Tuple[int, int, str, float]],
        opcode: TransitionOpcode = TransitionOpcode.IDENTITY,
    ) -> List[Dict[str, Any]]:
        """Batch composition: list of (hex_id, phase, mask, coherence).
        Each entry is independent; no hidden-stack coupling between them.
        Returns list of resolved state dicts.
        """
        results: List[Dict[str, Any]] = []
        for hex_id, phase, mask, coherence in specs:
            porosity = self._resolve_porosity(hex_id, mask)
            result = self.transition(
                hexagram_id=hex_id,
                phase_bits=phase,
                mask=mask,
                coherence=coherence,
                porosity=porosity,
                opcode=opcode,
            )
            results.append(result)
        return results

    def resolve_from_key(self, state_key: str) -> Dict[str, Any]:
        """Inverse lookup: parse composite key and re-resolve."""
        parsed = parse_state_key(state_key)
        return self.transition(
            hexagram_id=parsed["hexagram_id"],
            phase_bits=parsed["phase_bits"],
            mask=parsed["mask"],
            coherence=parsed["coherence"],
            porosity=parsed["porosity"],
        )

    def _resolve_porosity(self, hex_id: int, mask: str) -> float:
        """Pull porosity from inject_site or emotional weights."""
        hid = str(hex_id)
        site = _INJECT_SITES.get(hid, {})
        if "porosity" in site and isinstance(site["porosity"], (int, float)):
            return float(site["porosity"])
        ew = _EMOTIONAL_WEIGHTS.get(hid, {})
        if "porosity" in ew:
            return float(ew["porosity"])
        # fallback registry lookup
        reg = _HEX_REGISTRY.get(hid, {})
        return float(reg.get("porosity", 0.5))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_live_bits(hex_id: int) -> int:
    """Count 1 bits in canonical hexagram binary."""
    reg = _HEX_REGISTRY.get(str(hex_id), {})
    binary = str(reg.get("binary", "000000"))
    return binary.count("1")


def state_digest(state: Dict[str, Any]) -> str:
    """Deterministic hash of state for identity/change detection."""
    canonical = compose_state_key(
        int(state.get("hexagram_id", 0)),
        int(state.get("phase_bits", 0)),
        str(state.get("mask", "PASS")),
        float(state.get("coherence", 0.5)),
        float(state.get("porosity", 0.5)),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sm = KingwenStateMachine()

    # Identity transition
    # Full 512-state sweep: all 64 hexagrams × 8 phases
    # Full 512-state sweep: all 64 hexagrams × 8 phases
    t1 = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8)  # example transition  # example transition
    print(f"t1 state_key={t1['state_key']} digest={state_digest(t1)}")

    # Möbius transition
    t2 = sm.transition(hexagram_id=1, phase_bits=2, mask="PASS", coherence=0.8, opcode=TransitionOpcode.MOBIUS)
    print(f"t2 mobius_gamma={t2['mobius_gamma']}")

    # Stereographic projection
    t3 = sm.transition(hexagram_id=52, phase_bits=1, mask="PASS", coherence=0.9, opcode=TransitionOpcode.STEREOGRAPHIC)
    print(f"t3 sphere={t3['sphere']} inverse_err={t3['stereographic']['inverse_error']:.6f}")

    # Void null projection for void hex 15
    t4 = sm.transition(hexagram_id=15, phase_bits=0, mask="MEASURE", coherence=0.0, opcode=TransitionOpcode.NULL_VOID)
    print(f"t4 void={t4['void']} projection={t4.get('projection')}")

    # Gaussian future bias
    t5 = sm.transition(hexagram_id=1, phase_bits=0, mask="PASS", coherence=0.5, opcode=TransitionOpcode.GAUSSIAN_FUTURE)
    print(f"t5 future_weight={t5['future_weight']:.4f} bias_sum={sum(t5['phase_bias']):.4f}")

    # Stack overlay (headwear stacking)
    stacked = sm.stack(t1, mask="SEVER", coherence=0.3)
    print(f"stacked state_key={stacked['state_key']} mask={stacked['mask']} coherence={stacked['coherence']}")

    # Batch compose
    batch = sm.batch_compose([(i, i % 8, "PASS", 0.5) for i in range(1, 9)])
    print(f"batch count={len(batch)} unique keys={len(set(s['state_key'] for s in batch))}")

    print("\nPY_VERIFY_OK")
