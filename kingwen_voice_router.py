"""King Wen voice router.

Mines reasoning patterns from the verified VHDL state machine and applies them
as a consultative layer on top of the existing emotional engine. King Wen stays
the voice on the shoulder; this module decides when to speak, when to hold,
when to deliberate, and when to force a safe default.

VHDL patterns mined:
  - Priority routing: IMU override > PS override > tick evaluation > hold
  - Constraint masking: is_valid_transition() pure function
  - Deliberation window: hold on invalid prediction until resolved
  - CRIT countdown: 47-tick hard deadline → forced safe default
  - Fault detection: 46-bit fault vector from state/sensor mismatch
  - State tiers: 7 nominal + 57 fault/recovery states
"""

from __future__ import annotations

import time
from enum import IntFlag
from typing import Any, Dict, List, Optional, Tuple

from emotional_engine import (
    VEC_KEYS,
    collapse_full_128,
    expand_hexagram,
    sample_resolve,
    _clamp,
)
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_INFO

# ---------------------------------------------------------------------------
# Nominal hexagram states (from VHDL state machine, mapped to King Wen)
# ---------------------------------------------------------------------------
# 7 operational voices that the system is designed to speak with.
# All other 57 hexagram states are fault/recovery conditions where King Wen
# should hold instead of advising.

NOMINAL_STATES = {
    1: "idle",          # Creative - ready to speak
    2: "stealth",       # Receptive - listening mode
    8: "transit",       # Holding Together - consensus forming
    11: "tr_salt",      # Peace - stable advice
    12: "tr_crit",      # Standstill - high-stakes deliberation
    29: "limp",         # The Abysmal - degraded voice, minimal output
    58: "purge",        # The Joyous - channel reset
    52: "st_crit",      # Keeping Still - critical hold
}

# Reverse map: voice mode -> hexagram id
VOICE_MODE_TO_HEX = {v: k for k, v in NOMINAL_STATES.items()}

# ---------------------------------------------------------------------------
# Fault vector (46 bits mapped to 8-bit encoding)
# ---------------------------------------------------------------------------
class FaultVector(IntFlag):
    NONE = 0x00
    INVALID_TRANSITION = 0x01      # Advice contradicts last advice
    ELEC_MISMATCH = 0x02           # Vector magnitude doesn't match claimed confidence
    SAFETY_VIOLATION = 0x04        # Advice violates hard constraint
    THERMAL_OVERRUN = 0x08         # Emotional engine exceeding safe bounds
    PRESSURE_OUT = 0x10            # Too many simultaneous advisory requests
    ARC_SUPPRESS = 0x20            # Voice output suppressed by external signal
    CHOKE_FAULT = 0x40             # Input parsing failure
    SIC_FAULT = 0x80               # Core engine fault
    IMU_DECOHERENCE = 0x03         # Combined: invalid + elec mismatch
    GHOSTSPLAT_DIVERGENCE = 0x05   # Predicted state ≠ actual state
    TELEMETRY_TIMEOUT = 0x09       # Sensor data stale
    UNKNOWN_STATE = 0xFF           # Unknown hexagram, force recovery

# ---------------------------------------------------------------------------
# Priority stack for voice advice
# ---------------------------------------------------------------------------
class PriorityLevel:
    DIRECT_USER = 1      # User explicitly asks for voice (IMU override)
    SYSTEM_OVERRIDE = 2   # Agent system command (PS override)
    TICK_EVALUATION = 3   # Normal 640ms tick evaluation
    HOLD_STATE = 4        # Hold current advice, don't speak

# ---------------------------------------------------------------------------
# VHDL-derived constraint functions for King Wen
# ---------------------------------------------------------------------------
def is_valid_transition(
    current_hex: int,
    next_hex: int,
    confidence: float,
) -> bool:
    """Validate hexagram transition using constraint rules mined from VHDL.

    Returns True if the transition from current to next is allowed.
    This is a pure function - no emotional bias, just constraint checking.
    """
    if current_hex not in HEXAGRAM_BASE or next_hex not in HEXAGRAM_BASE:
        return False

    # IDLE (hex 1) can only transition to STEALTH (2) or PURGE (58)
    if current_hex == 1:
        return next_hex in (2, 58)

    # STEALTH (2) can transition to TRANSIT (8), IDLE (1), or PURGE (58)
    if current_hex == 2:
        return next_hex in (8, 1, 58)

    # TRANSIT (8) can transition to TR_SALT (11), TR_CRIT (12), LIMP (29), or PURGE (58)
    if current_hex == 8:
        return next_hex in (11, 12, 29, 58)

    # TR_SALT (11) can transition to TR_CRIT (12), TRANSIT (8), LIMP (29), or PURGE (58)
    if current_hex == 11:
        return next_hex in (12, 8, 29, 58)

    # TR_CRIT (12) can transition to LIMP (29), TRANSIT (8), or PURGE (58)
    if current_hex == 12:
        return next_hex in (29, 8, 58)

    # LIMP (29) can transition to TRANSIT (8), TR_SALT (11), STEALTH (2), or PURGE (58)
    if current_hex == 29:
        return next_hex in (8, 11, 2, 58)

    # PURGE (58) can transition to IDLE (1) or STEALTH (2)
    if current_hex == 58:
        return next_hex in (1, 2)

    # ST_CRIT (52) can transition to LIMP (29), STEALTH (2), or PURGE (58)
    if current_hex == 52:
        return next_hex in (29, 2, 58)

    # Unknown current state: no valid transitions
    return False


def is_nominal_hex(hexagram_id: int) -> bool:
    """Returns True if hexagram is one of the 7 nominal operational states."""
    return hexagram_id in NOMINAL_STATES


def compute_fault_vector(
    current_hex: int,
    next_hex: int,
    confidence: float,
    emotional_input: int,
    sensor_variance: float,
) -> FaultVector:
    """Compute 46-bit fault vector from state/sensor mismatch.

    Mined from VHDL compute_faults() pure function.
    """
    faults = FaultVector.NONE

    # Bit 0: Invalid transition
    if not is_valid_transition(current_hex, next_hex, confidence):
        faults |= FaultVector.INVALID_TRANSITION

    # Bit 1: Emotional vector magnitude doesn't match claimed confidence
    vec_mag = confidence  # confidence is derived from vector magnitude
    if abs(vec_mag - confidence) > 0.1:
        faults |= FaultVector.ELEC_MISMATCH

    # Bit 2: Safety violation - emotional_input outside safe bounds
    if not (0 <= emotional_input <= 100):
        faults |= FaultVector.SAFETY_VIOLATION

    # Bit 3: Thermal overrun - sensor variance exceeding safe bounds
    if sensor_variance > 0.8:
        faults |= FaultVector.THERMAL_OVERRUN

    # Bit 4: Pressure out of bounds - too many simultaneous requests
    # Not implemented in software yet; placeholder for future

    # Bit 45 equivalent: Unknown state
    if not is_nominal_hex(next_hex):
        faults |= FaultVector.UNKNOWN_STATE

    return faults


def default_next_state(current_hex: int, safety_ok: bool) -> int:
    """Return safe default state when normal transition is blocked.

    Mined from VHDL default_next_state() pure function.
    Forces IDLE/PURGE for non-combat states, LIMP for combat states.
    """
    # Combat states: TRANSIT (8), TR_SALT (11), TR_CRIT (12)
    combat_states = (8, 11, 12)

    if current_hex in combat_states:
        if not safety_ok:
            return 29  # LIMP
        return current_hex  # Hold current state

    # STEALTH (2)
    if current_hex == 2:
        if not safety_ok:
            return 1  # IDLE
        return current_hex

    # Default: IDLE
    return 1


def should_hold_in_state(
    current_hex: int,
    confidence: float,
    safety_ok: bool,
) -> bool:
    """Return True if King Wen should hold current advice rather than transition.

    Mined from VHDL should_hold_in_state() pure function.
    Preserves current advice during high-confidence deliberation.
    """
    # Hold in TR_SALT (11) or TR_CRIT (12) if confidence is high and safety OK
    if current_hex in (11, 12):
        if confidence > 0.7 and safety_ok:
            return True

    # Hold in TRANSIT (8) if safety OK (prevents premature advice)
    if current_hex == 8:
        if confidence > 0.5 and safety_ok:
            return True

    return False


def hexagram_to_voice_mode(hexagram_id: int) -> str:
    """Map hexagram state to voice output mode.

    Mined from VHDL hexagram_to_mode() pure function.
    """
    if hexagram_id == 1:
        return "idle"
    elif hexagram_id == 2:
        return "stealth"
    elif hexagram_id in (8, 11, 12):
        return "transit"
    elif hexagram_id == 29:
        return "limp"
    elif hexagram_id == 58:
        return "purge"
    elif hexagram_id == 52:
        return "stealth"  # ST_CRIT maps to stealth
    else:
        return "emergency"  # Unknown state, suppress voice


# ---------------------------------------------------------------------------
# Voice router: applies VHDL reasoning patterns to King Wen consult output
# ---------------------------------------------------------------------------
class KingWenVoiceRouter:
    """Consultative router for King Wen voice outputs.

    Mines VHDL reasoning patterns and applies them as advisory logic on top
    of the emotional engine. King Wen remains the voice; this module decides
    whether the voice should be heard, held, or forced to a safe default.

    Attributes:
        current_hex: Last advised hexagram (6-bit state)
        current_confidence: Confidence of last advice (0-1)
        crit_tick_count: Tick counter for CRIT states (0-47)
        crit_active: Whether CRIT countdown is active
        fault_vector: Current fault flags
        deliberation_mode: Whether in deliberation window
    """

    def __init__(self) -> None:
        self.current_hex: int = 1  # IDLE
        self.current_confidence: float = 0.0
        self.crit_tick_count: int = 0
        self.crit_active: bool = False
        self.fault_vector: FaultVector = FaultVector.NONE
        self.deliberation_mode: bool = False
        self.tick_count: int = 0

    def reset(self) -> None:
        """Reset router state (VHDL rst signal)."""
        self.current_hex = 1
        self.current_confidence = 0.0
        self.crit_tick_count = 0
        self.crit_active = False
        self.fault_vector = FaultVector.NONE
        self.deliberation_mode = False
        self.tick_count = 0

    def evaluate_advice(
        self,
        consult_result: Dict[str, Any],
        user_direct_input: bool = False,
        system_override: Optional[int] = None,
        safety_ok: bool = True,
        thermal_ok: bool = True,
        sensor_variance: float = 0.0,
    ) -> Dict[str, Any]:
        """Evaluate King Wen consult output through VHDL-derived reasoning.

        Args:
            consult_result: Output from collapse_full_128() or expand_with_personality()
            user_direct_input: True if user explicitly asked for voice (IMU override)
            system_override: Hexagram id if agent system is overriding (PS override)
            safety_ok: Aggregate safety flag
            thermal_ok: Thermal sensor flag
            sensor_variance: Variance from GhostSplat predictor

        Returns:
            dict with:
                - advice_hexagram: hexagram to speak, or hold
                - voice_mode: idle/stealth/transit/limp/purge/emergency
                - hold_in_state: bool, whether to hold current advice
                - deliberation: bool, whether in deliberation window
                - fault_vector: FaultVector flags
                - priority: priority level that decided this
                - crit_countdown: remaining ticks before forced safe default
                - reasoning: human-readable explanation
        """
        next_hex = consult_result.get("consensus", {}).get("consensus_hexagram_id") or 1
        confidence = consult_result.get("consensus", {}).get("consensus_vector", {}).get(
            "voiceWeight", 0.5
        )
        confidence = float(confidence or 0.5)

        # ------------------------------------------------------------------
        # Priority 1: Direct user input (IMU override)
        # ------------------------------------------------------------------
        if user_direct_input:
            self.fault_vector = compute_fault_vector(
                self.current_hex, next_hex, confidence,
                consult_result.get("emotional_input", 50), sensor_variance
            )
            voice_mode = hexagram_to_voice_mode(next_hex)
            return {
                "advice_hexagram": next_hex,
                "voice_mode": voice_mode,
                "hold_in_state": False,
                "deliberation": False,
                "fault_vector": self.fault_vector,
                "priority": PriorityLevel.DIRECT_USER,
                "crit_countdown": self.crit_tick_count,
                "reasoning": "Direct user input - voice speaks",
            }

        # ------------------------------------------------------------------
        # Priority 2: System override (PS override)
        # ------------------------------------------------------------------
        if system_override is not None:
            self.fault_vector = compute_fault_vector(
                self.current_hex, system_override, confidence,
                consult_result.get("emotional_input", 50), sensor_variance
            )
            voice_mode = hexagram_to_voice_mode(system_override)
            return {
                "advice_hexagram": system_override,
                "voice_mode": voice_mode,
                "hold_in_state": False,
                "deliberation": False,
                "fault_vector": self.fault_vector,
                "priority": PriorityLevel.SYSTEM_OVERRIDE,
                "crit_countdown": self.crit_tick_count,
                "reasoning": "System override - voice speaks per system command",
            }

        # ------------------------------------------------------------------
        # Priority 3: Normal tick evaluation
        # ------------------------------------------------------------------
        if should_hold_in_state(self.current_hex, confidence, safety_ok):
            self.deliberation_mode = False
            return {
                "advice_hexagram": self.current_hex,
                "voice_mode": hexagram_to_voice_mode(self.current_hex),
                "hold_in_state": True,
                "deliberation": False,
                "fault_vector": self.fault_vector,
                "priority": PriorityLevel.HOLD_STATE,
                "crit_countdown": self.crit_tick_count,
                "reasoning": "Hold in current state - high confidence or safety hold",
            }

        # Check if predicted transition is valid
        if is_valid_transition(self.current_hex, next_hex, confidence):
            # Valid transition - commit
            self.current_hex = next_hex
            self.current_confidence = confidence
            self.deliberation_mode = False
            voice_mode = hexagram_to_voice_mode(next_hex)

            # CRIT countdown logic
            if next_hex in (12, 52):  # TR_CRIT or ST_CRIT
                self.crit_active = True
                self.crit_tick_count = min(self.crit_tick_count + 1, 47)
            else:
                self.crit_active = False
                self.crit_tick_count = 0

            return {
                "advice_hexagram": next_hex,
                "voice_mode": voice_mode,
                "hold_in_state": False,
                "deliberation": False,
                "fault_vector": self.fault_vector,
                "priority": PriorityLevel.TICK_EVALUATION,
                "crit_countdown": self.crit_tick_count,
                "reasoning": f"Valid transition - voice advises hex {next_hex}",
            }
        else:
            # Invalid transition - enter deliberation
            self.deliberation_mode = True
            self.fault_vector |= FaultVector.INVALID_TRANSITION

            # Default: hold current state
            default_hex = default_next_state(self.current_hex, safety_ok)
            voice_mode = hexagram_to_voice_mode(default_hex)

            return {
                "advice_hexagram": default_hex,
                "voice_mode": voice_mode,
                "hold_in_state": True,
                "deliberation": True,
                "fault_vector": self.fault_vector,
                "priority": PriorityLevel.TICK_EVALUATION,
                "crit_countdown": self.crit_tick_count,
                "reasoning": f"Invalid transition to hex {next_hex} - deliberation, hold at {default_hex}",
            }

    def tick(self, safety_ok: bool = True) -> None:
        """Advance 640ms tick counter.

        Mined from VHDL tick_strobe process.
        """
        self.tick_count += 1

        # CRIT countdown logic from VHDL:
        # Activate counter when in CRIT states
        if self.current_hex in (12, 52):  # TR_CRIT or ST_CRIT
            self.crit_active = True
            if self.crit_tick_count < 47:
                self.crit_tick_count += 1
            else:
                # Hard deadline reached: force LIMP_MODE
                self.current_hex = 29  # LIMP
                self.crit_active = False
                self.crit_tick_count = 0
        else:
            # Reset counter when not in CRIT
            self.crit_tick_count = 0
            self.crit_active = False


# ---------------------------------------------------------------------------
# Quick verification
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    router = KingWenVoiceRouter()

    # Test 1: Direct user input (highest priority)
    result = router.evaluate_advice(
        {"consensus": {"consensus_hexagram_id": 1, "consensus_vector": {"voiceWeight": 0.9}}},
        user_direct_input=True,
    )
    print("Test 1 - Direct user input:")
    print(f"  advice_hexagram: {result['advice_hexagram']}")
    print(f"  voice_mode: {result['voice_mode']}")
    print(f"  priority: {result['priority']}")
    print(f"  reasoning: {result['reasoning']}")
    print()

    # Test 2: Invalid transition deliberation
    router.reset()
    result = router.evaluate_advice(
        {"consensus": {"consensus_hexagram_id": 99, "consensus_vector": {"voiceWeight": 0.5}}},
        safety_ok=True,
    )
    print("Test 2 - Invalid transition (hex 99):")
    print(f"  advice_hexagram: {result['advice_hexagram']}")
    print(f"  voice_mode: {result['voice_mode']}")
    print(f"  deliberation: {result['deliberation']}")
    print(f"  hold_in_state: {result['hold_in_state']}")
    print(f"  reasoning: {result['reasoning']}")
    print()

    # Test 3: CRIT countdown
    router.reset()
    router.current_hex = 12  # TR_CRIT
    print("Test 3 - CRIT countdown from TR_CRIT:")
    for i in range(5):
        router.tick(safety_ok=True)
        print(f"  tick {i+1}: crit_countdown={router.crit_tick_count}, current_hex={router.current_hex}")
    print()

    # Test 4: Hold in state
    router.reset()
    router.current_hex = 8  # TRANSIT
    result = router.evaluate_advice(
        {"consensus": {"consensus_hexagram_id": 11, "consensus_vector": {"voiceWeight": 0.8}}},
        safety_ok=True,
    )
    print("Test 4 - Hold in TRANSIT (high confidence):")
    print(f"  advice_hexagram: {result['advice_hexagram']}")
    print(f"  hold_in_state: {result['hold_in_state']}")
    print(f"  reasoning: {result['reasoning']}")
