
"""
dsp_clock.py — 2-clock model for King Wen testbed.

Two clocks:

  WALL_CLOCK  — real-world date/time.
    Measures wall-clock elapsed seconds, timestamps, cron cadence.
    Source of truth for "when did this happen in the world."

  TICK_CLOCK  — internal run time over ticks.
    Carries the -640Hz DSP phasor concept.
      healing  -> +640 Hz -> counter-clockwise phase advance
      opposition-> -640 Hz -> clockwise phase advance (negative-frequency phasor)
    Advances once per tick; each tick is 1/tick_rate_hz seconds of internal time.
    Provides phase, phase_mod (mod 2pi), sin/cos of current phase.

Pattern: baseline -> continue (n steps, measuring each) -> final report.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Canonical constants
# ---------------------------------------------------------------------------

HEALING_CLOCK_HZ: float = 640.0          # positive reference carrier frequency
OPPOSITION_CLOCK_HZ: float = -640.0      # opposition: negative-frequency phasor

_TWOPI: float = 2.0 * math.pi
DEFAULT_TICK_RATE_HZ: float = 60.0       # internal tick rate (like 60 fps)


# ---------------------------------------------------------------------------
# Wall clock — real-world date/time
# ---------------------------------------------------------------------------

@dataclass
class WallClock:
    """Real-world wall-clock reference.  Measures elapsed real seconds."""
    start_epoch: float = field(default_factory=time.time)

    def elapsed_s(self) -> float:
        return time.time() - self.start_epoch

    def snapshot(self) -> Dict[str, Any]:
        return {
            "epoch": time.time(),
            "elapsed_s": self.elapsed_s(),
        }


def wall_now_epoch() -> float:
    """Current wall-clock epoch time in seconds."""
    return time.time()


# ---------------------------------------------------------------------------
# Tick clock — internal run time over ticks, carries -640Hz / opposition
# ---------------------------------------------------------------------------

@dataclass
class TickClock:
    """Internal run-time clock over ticks.

    Carries the -640Hz / opposition concept:
      healing   -> effective_hz = +640  -> counter-clockwise phase advance
      opposition-> effective_hz = -640  -> clockwise phase advance (neg-freq phasor)

    Advances once per tick.  dt_per_tick = 1 / tick_rate_hz.
    """

    base_hz: float = HEALING_CLOCK_HZ
    tick_rate_hz: float = DEFAULT_TICK_RATE_HZ
    opposition: bool = False

    tick: int = 0
    phase: float = 0.0                      # accumulated phase (radians, can exceed 2pi)
    history: List[Dict[str, Any]] = field(default_factory=list)

    _dt: float = field(init=False)

    def __post_init__(self) -> None:
        self._dt = 1.0 / self.tick_rate_hz if self.tick_rate_hz else 0.0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def effective_hz(self) -> float:
        """+640 for healing, -640 for opposition."""
        return -abs(self.base_hz) if self.opposition else abs(self.base_hz)

    @property
    def d_phase_per_tick(self) -> float:
        """Phase advance per tick: 2pi * effective_hz * dt."""
        return _TWOPI * self.effective_hz * self._dt

    # ------------------------------------------------------------------
    # Advancing / measuring
    # ------------------------------------------------------------------

    def step(self, measurement: Any = None) -> Dict[str, Any]:
        """Advance one tick.  Optionally attach a per-tick measurement."""
        self.phase += self.d_phase_per_tick
        self.tick += 1
        record: Dict[str, Any] = {
            "tick": self.tick,
            "phase": self.phase,
            "phase_mod": self.phase % _TWOPI,
            "sin": math.sin(self.phase % _TWOPI),
            "cos": math.cos(self.phase % _TWOPI),
            "effective_hz": self.effective_hz,
            "opposition": self.opposition,
            "d_phase_per_tick": self.d_phase_per_tick,
            "measurement": measurement,
        }
        self.history.append(record)
        return record

    def run_steps(self, n: int,
                   per_step: Optional[Callable[["TickClock", int], Any]] = None
                   ) -> List[Dict[str, Any]]:
        """Advance n ticks, calling per_step(tick_clock, step_index) for a measurement."""
        recs: List[Dict[str, Any]] = []
        for i in range(n):
            m = per_step(self, i) if per_step else None
            recs.append(self.step(m))
        return recs

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def set_healing(self) -> None:
        self.opposition = False

    def set_opposition(self) -> None:
        self.opposition = True

    def toggle_opposition(self) -> None:
        self.opposition = not self.opposition


# ---------------------------------------------------------------------------
# Baseline + continue + measure
# ---------------------------------------------------------------------------

@dataclass
class ContinueRun:
    """Result of: load baseline -> run n ticks (continue) -> measure over time."""
    baseline: Dict[str, Any]
    wall: WallClock
    tick: TickClock
    steps: List[Dict[str, Any]]
    final: Dict[str, Any]

    @classmethod
    def run(cls,
             baseline: Dict[str, Any],
             n_steps: int,
             per_step: Optional[Callable[[int, TickClock, Dict[str, Any]], Any]] = None,
             *,
             tick_rate_hz: float = DEFAULT_TICK_RATE_HZ,
             base_hz: float = HEALING_CLOCK_HZ,
             opposition: bool = False,
             ) -> "ContinueRun":
        """Load baseline, then run n steps of the tick clock, measuring each step.

        baseline: the loaded state (payload).
        n_steps: number of internal ticks to run.
        per_step: optional callback(step_index, tick_clock, baseline) -> measurement.
        """
        wall = WallClock()
        tick = TickClock(tick_rate_hz=tick_rate_hz, base_hz=base_hz, opposition=opposition)
        steps: List[Dict[str, Any]] = []
        for i in range(n_steps):
            measurement = per_step(i, tick, baseline) if per_step else None
            tick.step(measurement)
            steps.append({
                "step_index": i,
                "wall_elapsed_s": wall.elapsed_s(),
                "tick_record": tick.history[-1],
            })
        final_rec = tick.history[-1] if tick.history else {}
        final: Dict[str, Any] = {
            "wall_elapsed_s": wall.elapsed_s(),
            "tick_tick": tick.tick,
            "tick_phase": tick.phase,
            "tick_phase_mod": final_rec.get("phase_mod", 0.0),
            "tick_phase_sin": final_rec.get("sin", 0.0),
            "tick_phase_cos": final_rec.get("cos", 0.0),
            "effective_hz": tick.effective_hz,
            "opposition": tick.opposition,
            "d_phase_per_tick": tick.d_phase_per_tick,
            "history_len": len(tick.history),
        }
        return cls(baseline=baseline, wall=wall, tick=tick, steps=steps, final=final)

# ---------------------------------------------------------------------------
# Pre-computed phase tables for consumers (egg keyframes, audio samples, etc.)
# ---------------------------------------------------------------------------

def precompute_tick_phase_table_from_frames(
    num_frames: int,
    frame_rate: float,
    mode: str = "healing",
    hz: Optional[float] = None,
) -> Dict[str, Any]:
    """Precompute per-frame tick phase table for animation consumers."""
    if hz is None:
        hz = HEALING_CLOCK_HZ
    omega = _TWOPI * abs(hz)
    sign = -1.0 if mode == "healing" else +1.0
    per_tick: List[float] = []
    per_tick_sin: List[float] = []
    per_tick_cos: List[float] = []
    tick_duration = 1.0 / frame_rate if frame_rate > 0 else 1.0/60.0
    for k in range(num_frames):
        t = k * tick_duration
        ph = sign * omega * t
        per_tick.append(ph)
        per_tick_sin.append(math.sin(ph))
        per_tick_cos.append(math.cos(ph))
    return {
        "mode": mode,
        "hz": hz,
        "sign": sign,
        "omega": omega,
        "frame_rate": frame_rate,
        "num_frames": num_frames,
        "per_tick": per_tick,
        "per_tick_sin": per_tick_sin,
        "per_tick_cos": per_tick_cos,
    }

def precompute_tick_phase_table_from_samples(
    sample_rate: int,
    num_samples: int,
    mode: str = "healing",
    hz: Optional[float] = None,
) -> Dict[str, Any]:
    """Precompute per-sample tick phase table for audio consumers."""
    if hz is None:
        hz = HEALING_CLOCK_HZ
    omega = _TWOPI * abs(hz)
    sign = -1.0 if mode == "healing" else +1.0
    per_tick: List[float] = []
    per_tick_sin: List[float] = []
    per_tick_cos: List[float] = []
    tick_duration = 1.0 / sample_rate if sample_rate > 0 else 1.0/22050.0
    for k in range(num_samples):
        t = k * tick_duration
        ph = sign * omega * t
        per_tick.append(ph)
        per_tick_sin.append(math.sin(ph))
        per_tick_cos.append(math.cos(ph))
    return {
        "mode": mode,
        "hz": hz,
        "sign": sign,
        "omega": omega,
        "sample_rate": sample_rate,
        "num_samples": num_samples,
        "per_tick": per_tick,
        "per_tick_sin": per_tick_sin,
        "per_tick_cos": per_tick_cos,
    }
