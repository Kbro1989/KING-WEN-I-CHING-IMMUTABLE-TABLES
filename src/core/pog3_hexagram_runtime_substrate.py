"""pog3_hexagram_runtime_substrate.py
The central nervous system of POG3.

King Wen 512-state oracle (2^9) serves as the quantum expansion/capture
mechanic for agent intents. Every limb consults this substrate before
committing action. The hexagram runtime is not a sidecar — it IS the
volition layer.

Architecture:
    Intent (superposition) → Emotional Weighting → Temporal Reflection
    → Hexagram Collapse → State Capture → Provenance Trail → Action Commit

Integration points:
    - GhostSplat: receives hexagram state as prediction context
    - ModelRolodex: uses hexagram reputation for model selection
    - HexagramNetworkBridge: broadcasts collapsed states to mesh
    - POG2 save-string: serializes intent transcriptome with hexagram telemetry
    - Megatron-LM: trains on captured state trajectories
"""
from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Resolve data directory relative to this file's location in the repo
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]  # src/core/ -> repo root
_DATA_DIR = _REPO_ROOT / "data"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Core Data Structures
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IntentVector:
    """Agent intent as a 9-dimensional superposition vector.

    9 bits = 512 states. Each dimension represents:
    0-2: Temporal (past/present/future)
    3-5: Emotional (chaos/whimsy/darkTone from your pipeline prosody)
    6-8: Action (move/attack/interact — mapped from POG2 actionables)
    """
    temporal: Tuple[int, int, int]      # 3-bit past/present/future signature
    emotional: Tuple[float, float, float]  # chaos, whimsy, darkTone weights
    action: Tuple[int, int, int]        # 3-bit action signature

    def to_bits(self) -> int:
        """Collapse 9-dimensional vector to deterministic 9-bit integer."""
        # Temporal: quantize to 1 bit each (yin=0, yang=1)
        t_bits = sum(1 << i for i, v in enumerate(self.temporal) if v > 0)
        # Emotional: threshold at 0.5
        e_bits = sum(1 << (i + 3) for i, v in enumerate(self.emotional) if v > 0.5)
        # Action: quantize to 1 bit each
        a_bits = sum(1 << (i + 6) for i, v in enumerate(self.action) if v > 0)
        return t_bits | e_bits | a_bits

    def to_hexagram_state(self) -> HexagramState:
        """Deterministic hash → 512-state oracle coordinate."""
        bits = self.to_bits()
        return HexagramState.from_bits(bits)


@dataclass
class HexagramState:
    """A resolved state in the 512-state King Wen oracle.

    512 = 2^9: 6 yao lines (classic hexagram) + 3 temporal dimensions.
    The upper 3 bits encode temporal phase; lower 6 encode yao lines.
    """
    state_id: int           # 0-511
    yao_lines: Tuple[int, ...]  # 6 lines, each -1 (yin), 0 (changing), 1 (yang)
    temporal_phase: str     # "past", "present", "future"
    emotional_signature: Dict[str, float] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_bits(cls, bits: int) -> "HexagramState":
        """Deterministic construction from 9-bit intent vector."""
        # Lower 6 bits → yao lines
        yao = tuple(
            -1 if not (bits & (1 << i)) else 1
            for i in range(6)
        )
        # Upper 3 bits → temporal phase
        temporal_bits = (bits >> 6) & 0b111
        phase_map = {
            0: "past", 1: "present", 2: "future",
            3: "past", 4: "present", 5: "future",
            6: "past", 7: "present",
        }
        phase = phase_map.get(temporal_bits, "present")

        return cls(
            state_id=bits,
            yao_lines=yao,
            temporal_phase=phase,
        )

    def to_king_wen_id(self) -> int:
        """Map the lower 6 yao bits to a King Wen hexagram ID (1-64).

        Uses the lower 6 bits of state_id to select from the 64 hexagrams.
        """
        return (self.state_id & 0b111111) + 1

    def to_save_string(self) -> str:
        """Serialize to POG2 save-string format."""
        return (
            f"[hex];id:{self.state_id};"
            f"yao:{','.join(map(str, self.yao_lines))};"
            f"tmp:{self.temporal_phase};"
            f"em:{json.dumps(self.emotional_signature)};"
            f"prv:{json.dumps(self.provenance)}"
        )


@dataclass
class StateCapture:
    """A captured state transition with full provenance.

    This is the quantum measurement record — what collapsed, when,
    and what the emotional context was at collapse time.
    """
    intent: IntentVector
    collapsed_state: HexagramState
    timestamp: float
    session_id: str
    tick_id: int
    action_taken: Optional[str] = None
    outcome: Optional[str] = None

    def to_telemetry(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "tick_id": self.tick_id,
            "timestamp": self.timestamp,
            "intent_bits": self.intent.to_bits(),
            "state_id": self.collapsed_state.state_id,
            "king_wen_id": self.collapsed_state.to_king_wen_id(),
            "temporal_phase": self.collapsed_state.temporal_phase,
            "emotional": {
                "chaos": self.intent.emotional[0],
                "whimsy": self.intent.emotional[1],
                "darkTone": self.intent.emotional[2],
            },
            "action": self.action_taken,
            "outcome": self.outcome,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: The Runtime Engine
# ═══════════════════════════════════════════════════════════════════════════════

class HexagramRuntimeEngine:
    """Central nervous system for POG3.

    Every agent intent passes through here. The engine:
    1. Receives intent superposition
    2. Weights by emotional context
    3. Applies temporal reflection
    4. Collapses to hexagram state
    5. Captures provenance
    6. Returns actionable state + telemetry
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.tick_counter = 0
        self._lock = threading.Lock()
        self._state_history: List[StateCapture] = []
        self._emotional_weights: Dict[str, Any] = {}
        self._hexagram_registry: Dict[str, Any] = {}
        self._callbacks: List[Callable[[StateCapture], None]] = []

        # Load data from King Wen immutable tables
        self._load_emotional_weights()
        self._load_hexagram_registry()

    def _load_emotional_weights(self) -> None:
        """Load emotional weight mappings from data/emotional-weights.json."""
        weights_path = _DATA_DIR / "emotional-weights.json"
        try:
            with open(weights_path, "r", encoding="utf-8") as f:
                self._emotional_weights = json.load(f)
            logger.info("Loaded %d emotional weight entries from %s",
                        len(self._emotional_weights), weights_path)
        except Exception as exc:
            logger.warning("Could not load emotional weights from %s: %s",
                           weights_path, exc)
            self._emotional_weights = {}

    def _load_hexagram_registry(self) -> None:
        """Load hexagram registry from data/hexagram-registry.json."""
        registry_path = _DATA_DIR / "hexagram-registry.json"
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                self._hexagram_registry = json.load(f)
            logger.info("Loaded %d hexagram entries from %s",
                        len(self._hexagram_registry), registry_path)
        except Exception as exc:
            logger.warning("Could not load hexagram registry from %s: %s",
                           registry_path, exc)
            self._hexagram_registry = {}

    def consult(
        self,
        intent: IntentVector,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[HexagramState, StateCapture]:
        """Consult the oracle — the core runtime operation.

        This is where agent intent collapses from superposition
        into observable state. Every limb calls this before acting.
        """
        with self._lock:
            self.tick_counter += 1
            tick_id = self.tick_counter

        # Apply emotional weighting from context
        weighted_intent = self._apply_emotional_weights(intent, context)

        # Apply temporal reflection (past states influence present collapse)
        reflected_intent = self._apply_temporal_reflection(weighted_intent)

        # Collapse to hexagram state
        state = reflected_intent.to_hexagram_state()

        # Enrich with King Wen registry data
        king_wen_id = state.to_king_wen_id()
        registry_entry = self._hexagram_registry.get(str(king_wen_id), {})

        # Enrich with emotional signature
        state.emotional_signature = {
            "chaos": intent.emotional[0],
            "whimsy": intent.emotional[1],
            "darkTone": intent.emotional[2],
        }

        # Merge King Wen emotional weights if available
        kw_weights = self._emotional_weights.get(str(king_wen_id), {})
        if kw_weights:
            state.emotional_signature["kw_chaos"] = kw_weights.get("chaos", 0.5)
            state.emotional_signature["kw_whimsy"] = kw_weights.get("whimsy", 0.5)
            state.emotional_signature["kw_darkTone"] = kw_weights.get("darkTone", 0.5)
            state.emotional_signature["kw_coherence"] = kw_weights.get("coherence", 0.5)
            state.emotional_signature["kw_voiceWeight"] = kw_weights.get("voiceWeight", 0.5)

        # Build provenance
        state.provenance = {
            "session_id": self.session_id,
            "tick_id": tick_id,
            "timestamp": time.time(),
            "context": context or {},
            "king_wen_id": king_wen_id,
            "king_wen_name": registry_entry.get("name", ""),
            "king_wen_action": registry_entry.get("action", "WAIT"),
            "king_wen_category": registry_entry.get("category", "transformer"),
        }

        # Capture the collapse
        capture = StateCapture(
            intent=intent,
            collapsed_state=state,
            timestamp=time.time(),
            session_id=self.session_id,
            tick_id=tick_id,
        )

        self._state_history.append(capture)

        # Notify subscribers (GhostSplat, ModelRolodex, etc.)
        for cb in self._callbacks:
            try:
                cb(capture)
            except Exception as exc:
                logger.debug("Callback error: %s", exc)

        return state, capture

    def _apply_emotional_weights(
        self,
        intent: IntentVector,
        context: Optional[Dict[str, Any]],
    ) -> IntentVector:
        """Apply emotional weighting from King Wen corpus."""
        if not context or "emotional_override" not in context:
            return intent

        override = context["emotional_override"]
        new_emotional = (
            override.get("chaos", intent.emotional[0]),
            override.get("whimsy", intent.emotional[1]),
            override.get("darkTone", intent.emotional[2]),
        )
        return IntentVector(
            temporal=intent.temporal,
            emotional=new_emotional,
            action=intent.action,
        )

    def _apply_temporal_reflection(
        self,
        intent: IntentVector,
    ) -> IntentVector:
        """Past states influence present collapse via temporal reflection."""
        if len(self._state_history) < 3:
            return intent

        # Look at last 3 captures for temporal momentum
        recent = self._state_history[-3:]
        avg_chaos = sum(c.intent.emotional[0] for c in recent) / 3
        avg_whimsy = sum(c.intent.emotional[1] for c in recent) / 3

        # Temporal momentum: if recent states were chaotic, increase chaos weight
        momentum = (avg_chaos + avg_whimsy) / 2
        new_chaos = min(1.0, intent.emotional[0] + momentum * 0.1)

        return IntentVector(
            temporal=intent.temporal,
            emotional=(new_chaos, intent.emotional[1], intent.emotional[2]),
            action=intent.action,
        )

    def subscribe(self, callback: Callable[[StateCapture], None]) -> None:
        """Subscribe to state collapse events.

        Used by:
        - GhostSplat: receives state for prediction context
        - ModelRolodex: updates reputation based on state outcomes
        - HexagramNetworkBridge: broadcasts to mesh
        """
        self._callbacks.append(callback)

    def get_state_history(self, n: int = 64) -> List[StateCapture]:
        """Get recent state history for temporal analysis."""
        return self._state_history[-n:]

    def get_emotional_timeseries(self) -> List[Dict[str, Any]]:
        """Export emotional time-series for Megatron-LM training."""
        return [
            {
                "tick_id": c.tick_id,
                "timestamp": c.timestamp,
                "chaos": c.intent.emotional[0],
                "whimsy": c.intent.emotional[1],
                "darkTone": c.intent.emotional[2],
                "state_id": c.collapsed_state.state_id,
                "king_wen_id": c.collapsed_state.to_king_wen_id(),
            }
            for c in self._state_history
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Integration Adapters
# ═══════════════════════════════════════════════════════════════════════════════

class GhostSplatAdapter:
    """Adapter: HexagramRuntimeEngine → GhostSplat prediction layer.

    GhostSplat receives hexagram state as additional prediction context,
    enabling it to factor oracle guidance into position/action predictions.
    """

    def __init__(self, runtime: HexagramRuntimeEngine):
        self.runtime = runtime
        runtime.subscribe(self._on_state_collapse)

    def _on_state_collapse(self, capture: StateCapture) -> None:
        """Feed collapsed state into GhostSplat context."""
        ghost_context = {
            "hexagram_state_id": capture.collapsed_state.state_id,
            "king_wen_id": capture.collapsed_state.to_king_wen_id(),
            "temporal_phase": capture.collapsed_state.temporal_phase,
            "emotional_signature": capture.collapsed_state.emotional_signature,
            "tick_id": capture.tick_id,
        }
        logger.debug("GhostSplat context updated: %s", ghost_context)


class ModelRolodexAdapter:
    """Adapter: HexagramRuntimeEngine → ModelRolodex reputation learning.

    Hexagram states influence model selection. High chaos states may
    prefer creative models; high coherence states prefer precise models.
    """

    def __init__(self, runtime: HexagramRuntimeEngine):
        self.runtime = runtime
        runtime.subscribe(self._on_state_collapse)
        self._model_bias: Dict[str, float] = {}

    def _on_state_collapse(self, capture: StateCapture) -> None:
        """Update model bias based on hexagram emotional signature."""
        chaos = capture.collapsed_state.emotional_signature.get("chaos", 0.5)
        whimsy = capture.collapsed_state.emotional_signature.get("whimsy", 0.5)

        # High chaos + whimsy → boost creative models
        if chaos > 0.7 and whimsy > 0.7:
            self._model_bias["creative"] = self._model_bias.get("creative", 1.0) + 0.1
        # Low chaos, high coherence → boost precise models
        elif chaos < 0.3:
            self._model_bias["precise"] = self._model_bias.get("precise", 1.0) + 0.1

    def get_model_bias(self) -> Dict[str, float]:
        return dict(self._model_bias)


class SaveStringAdapter:
    """Adapter: HexagramRuntimeEngine → POG2 save-string serialization.

    Captures intent transcriptome with hexagram telemetry for
    durable state reconstruction.
    """

    def __init__(self, runtime: HexagramRuntimeEngine):
        self.runtime = runtime

    def serialize_session(self) -> str:
        """Serialize full session to POG2 save-string format."""
        captures = self.runtime.get_state_history()
        segments = []
        for c in captures:
            segments.append(c.collapsed_state.to_save_string())
        return ";".join(segments)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Initialization & Factory
# ═══════════════════════════════════════════════════════════════════════════════

class POG3Runtime:
    """Singleton factory for POG3 hexagram runtime substrate.

    Usage:
        runtime = POG3Runtime.for_session("session_abc")
        intent = IntentVector(
            temporal=(1,0,0),
            emotional=(0.5, 0.8, 0.2),
            action=(1,0,0),
        )
        state, capture = runtime.engine.consult(intent, context={...})

        # state: HexagramState — the collapsed oracle guidance
        # capture: StateCapture — full provenance for telemetry/training
    """

    _instances: Dict[str, "POG3Runtime"] = {}
    _lock = threading.Lock()

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.engine = HexagramRuntimeEngine(session_id)
        self.ghost_adapter = GhostSplatAdapter(self.engine)
        self.rolodex_adapter = ModelRolodexAdapter(self.engine)
        self.save_adapter = SaveStringAdapter(self.engine)

    @classmethod
    def for_session(cls, session_id: str) -> "POG3Runtime":
        with cls._lock:
            if session_id not in cls._instances:
                cls._instances[session_id] = cls(session_id)
            return cls._instances[session_id]

    def get_telemetry(self) -> Dict[str, Any]:
        """Export full telemetry for HexagramNetworkBridge broadcast."""
        return {
            "session_id": self.session_id,
            "tick_count": self.engine.tick_counter,
            "emotional_timeseries": self.engine.get_emotional_timeseries(),
            "model_bias": self.rolodex_adapter.get_model_bias(),
            "latest_state": (
                self.engine._state_history[-1].collapsed_state.to_save_string()
                if self.engine._state_history else None
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Quick Test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    runtime = POG3Runtime.for_session("test_session")

    # Simulate an agent intent: high whimsy, low chaos, moving forward
    intent = IntentVector(
        temporal=(1, 0, 0),      # present-focused
        emotional=(0.2, 0.9, 0.1),  # low chaos, high whimsy, low dark
        action=(1, 0, 0),        # move action
    )

    state, capture = runtime.engine.consult(intent)
    print(f"Collapsed to state {state.state_id}: {state.temporal_phase}")
    print(f"King Wen hexagram: #{state.to_king_wen_id()}")
    print(f"Yao lines: {state.yao_lines}")
    print(f"Emotional signature: {state.emotional_signature}")
    print(f"Provenance: {json.dumps(state.provenance, indent=2)}")
    print(f"Save string: {state.to_save_string()}")
    print(f"Telemetry: {json.dumps(capture.to_telemetry(), indent=2)}")
    print(f"\nSession telemetry: {json.dumps(runtime.get_telemetry(), indent=2)}")
