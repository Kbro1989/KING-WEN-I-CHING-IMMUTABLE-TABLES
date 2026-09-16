#!/usr/bin/env python3
"""
shotgun_rollout_runtime.py — chained phase rollout over the shotgun sequence.

Takes shotgun_expand() output and sequences the 8 phases per hexagram so that
each phase's resolved+expanded state becomes input context for the next phase.

This is the "one rolled-on equation that changes over time" runtime: the
sequence of phase outputs IS the equation. No separate math stack between layers
— each phase produces a state record, and the next phase receives the prior
phase's state as context.

If a value from a prior phase is missing when a later phase needs it, the
runtime flags the break rather than silently dropping it. Downstream usages
(voice, 3D, training, quantum viz) read from the chained record, so a break
anywhere in the chain corrupts everything downstream — which is the point: the
runtime makes the break visible instead of silent.

Windows-native paths only. Imports from existing King Wen modules as the prime
import; quantum lab simulation constants are imported as a functional layer.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# Prime import: existing King Wen modules
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_INFO
from emotional_engine import (
    VEC_KEYS,
    _hamiltonian_energy,
    _line_state_balance,
    expand_hexagram,
    derive_dynamic_emotional_input,
)
from scripts.full_hexagram_shotgun import (
    shotgun_expand,
    _ternary_slot_matrix,
)

# Quantum lab simulation program usages — imported as a functional layer constant.
# These are the measured/derived values that the quantum lab simulation produces
# and that downstream renderings (2D/3D wave packets, audio pellets) consume.
# They are NOT recomputed here; they are imported and carried forward in the
# chained record so nothing is lost between phases.
QUANTUM_LAB_CONSTANTS: Dict[str, Any] = {
    "coprimes": [97, 89, 83, 79, 73],
    "hbar": 1.0,
    "mass": 1.0,
    "dt": 0.02,
    "warmup_steps": 3,
    "t_max": 4.0 * math.pi,
    "x_range": (-6.0, 6.0),
    "t_samples": 60,
    "x_samples": 80,
    "phase_names": [
        "past", "present", "future", "transition",
        "resolution", "dissolution", "crystallization", "void",
    ],
}


def _carry_forward(
    prior: Optional[Dict[str, Any]],
    current: Dict[str, Any],
    phase_bits: int,
    hex_id: int,
) -> Dict[str, Any]:
    """Merge prior-phase state into current-phase record.

    The current record is the primary; prior values are carried forward only
    where the current record does not already supply them. If a value the
    chain needs is missing from both, the break is flagged.
    """
    if prior is None:
        return dict(current)

    carried: Dict[str, Any] = {}
    needed_keys = [
        "resolved_vector", "expanded_vector", "inject_site",
        "line_balance", "yao_vocabulary", "quantum_avatar_state",
        "hamiltonian_energy", "porosity",
    ]
    for k in needed_keys:
        cur_val = current.get(k)
        pri_val = prior.get(k) if prior else None
        if cur_val not in (None, {}, "", 0.0) and cur_val is not None:
            carried[k] = cur_val
        elif pri_val not in (None, {}, "", 0.0) and pri_val is not None:
            carried[k] = pri_val
        else:
            carried[k] = None  # flagged break

    # Build the rolled-on context: prior phase's feeling about the input
    # becomes part of the next phase's input context.
    context: Dict[str, Any] = {
        "hexagram_id": hex_id,
        "phase_bits": phase_bits,
        "phase_temporal": PHASE_INFO[phase_bits]["temporal"],
        "prior_resolved_vector": prior.get("resolved_vector") if prior else None,
        "prior_expanded_vector": prior.get("expanded_vector") if prior else None,
        "prior_porosity": prior.get("inject_site", {}).get("porosity") if prior else None,
        "prior_line_balance": prior.get("line_balance") if prior else None,
        "prior_yao_vocabulary": prior.get("yao_vocabulary") if prior else None,
        "prior_hamiltonian": prior.get("hamiltonian_energy") if prior else None,
        "current_resolved_vector": carried.get("resolved_vector"),
        "current_expanded_vector": carried.get("expanded_vector"),
        "current_porosity": carried.get("porosity"),
        "current_line_balance": carried.get("line_balance"),
        "current_yao_vocabulary": carried.get("yao_vocabulary"),
        "current_hamiltonian": carried.get("hamiltonian_energy"),
        "carry_break": any(
            carried.get(k) is None for k in needed_keys
        ),
        "quantum_lab_constants": QUANTUM_LAB_CONSTANTS,
    }
    # Merge the current record's own fields on top
    for k in current:
        if k not in context:
            context[k] = current[k]
    return context


def rollout_hexagram(
    hex_id: int,
    request_text: str = "",
    emotional_input: Optional[int] = None,
    *,
    carry_chain: bool = True,
) -> Dict[str, Any]:
    """Run the 8-phase rollout for a single hexagram as a chained sequence.

    Returns a dict with:
      - hexagram_id, name, category, action
      - phases: list of 8 phase records, each carrying its own state AND
        the prior-phase carry-forward context
      - chain_breaks: list of (phase_index, missing_keys) for any break in
        the handoff chain
      - final_rollout_state: the last phase's carried-forward state
      - hamiltonian_trajectory: [H_t for t in phases]
      - porosity_trajectory: [porosity_t for t in phases]
      - resolved_vector_trajectory: [resolved_t for t in phases]
    """
    base = HEXAGRAM_BASE[hex_id]
    emotional_input = derive_dynamic_emotional_input(request_text, emotional_input)

    phases: List[Dict[str, Any]] = []
    chain_breaks: List[Tuple[int, List[str]]] = []
    prior: Optional[Dict[str, Any]] = None
    hamiltonian_trajectory: List[float] = []
    porosity_trajectory: List[float] = []
    resolved_trajectory: List[Dict[str, float]] = []

    for phase_bits in range(8):
        phase_rec = expand_hexagram(
            hex_id,
            request_text=request_text,
            phase_bits=phase_bits,
            emotional_input=emotional_input,
        )
        # Current record is what this phase produces on its own
        current: Dict[str, Any] = {
            "hexagram_id": hex_id,
            "phase_bits": phase_bits,
            "phase_temporal": PHASE_INFO[phase_bits]["temporal"],
            "expanded_vector": phase_rec.get("expanded_vector", {}),
            "resolved_vector": phase_rec.get("resolved_vector", {}),
            "inject_site": phase_rec.get("inject_site", {}),
            "line_balance": phase_rec.get("line_balance", {}),
            "yao_vocabulary": phase_rec.get("yao_vocabulary", {}),
            "quantum_avatar_state": phase_rec.get("quantum_avatar_state", {}),
            "hamiltonian_energy": _hamiltonian_energy(
                [float(phase_rec.get("resolved_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS],
                [float(phase_rec.get("expanded_vector", {}).get(k, 0.0) or 0.0) for k in VEC_KEYS],
                phase_rec.get("line_balance", {}),
            ),
            "porosity": phase_rec.get("inject_site", {}).get("porosity"),
        }

        if carry_chain and prior is not None:
            ctx = _carry_forward(prior, current, phase_bits, hex_id)
            # Flag breaks
            break_keys = [
                k for k in ["resolved_vector", "expanded_vector", "inject_site",
                             "line_balance", "yao_vocabulary", "hamiltonian_energy",
                             "porosity"]
                if ctx.get(k) is None
            ]
            if break_keys:
                chain_breaks.append((phase_bits, break_keys))
            current["rollout_context"] = ctx

        prior = current
        phases.append(current)
        hamiltonian_trajectory.append(current["hamiltonian_energy"])
        porosity_trajectory.append(current["porosity"])
        resolved_trajectory.append(current["resolved_vector"])

    return {
        "hexagram_id": hex_id,
        "name": base.get("name"),
        "category": base.get("category", ""),
        "action": base.get("action", ""),
        "request_text": request_text,
        "emotional_input": emotional_input,
        "phases": phases,
        "chain_breaks": chain_breaks,
        "final_rollout_state": phases[-1] if phases else None,
        "hamiltonian_trajectory": hamiltonian_trajectory,
        "porosity_trajectory": porosity_trajectory,
        "resolved_vector_trajectory": resolved_trajectory,
        "quantum_lab_constants": QUANTUM_LAB_CONSTANTS,
    }


def rollout_all(
    request_text: str = "",
    emotional_input: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Run the chained rollout for all 64 hexagrams.

    This is the shotgun sequence with phase handoff: 64 hexagrams × 8 phases,
    each phase carrying forward the prior phase's state.
    """
    return [rollout_hexagram(hex_id, request_text, emotional_input)
            for hex_id in range(1, 65)]


def summarize_rollout(rollout: Dict[str, Any]) -> Dict[str, Any]:
    """Extract training-relevant measurables from a single hexagram rollout."""
    phases = rollout["phases"]
    if not phases:
        return {}

    # Chain continuity check
    breaks = rollout["chain_breaks"]
    chain_continuous = len(breaks) == 0

    # Final phase's carried-forward state (the "rolled-on equation" result)
    final = phases[-1]
    final_resolved = final.get("resolved_vector", {})
    final_expanded = final.get("expanded_vector", {})
    final_porosity = final.get("porosity")
    final_hamiltonian = final.get("hamiltonian_energy")

    # Trajectory variance: how much does each measure move across the 8 phases
    def trajectory_norm(traj: List[Any], key: str) -> float:
        vals = []
        for rec in traj:
            v = rec.get(key, {})
            if isinstance(v, dict):
                vals.append(sum(float(v.get(kk, 0.0)) for kk in VEC_KEYS) / max(1, len(VEC_KEYS)))
            elif isinstance(v, (int, float)):
                vals.append(float(v))
            else:
                vals.append(0.0)
        if len(vals) < 2:
            return 0.0
        mean = sum(vals) / len(vals)
        return math.sqrt(sum((x - mean) ** 2 for x in vals) / len(vals))

    hamiltonian_trajectory = rollout["hamiltonian_trajectory"]
    porosity_trajectory = rollout["porosity_trajectory"]

    return {
        "hexagram_id": rollout["hexagram_id"],
        "chain_continuous": chain_continuous,
        "chain_breaks": breaks,
        "hamiltonian_trajectory": hamiltonian_trajectory,
        "hamiltonian_trajectory_std": trajectory_norm(phases, "hamiltonian_energy"),
        "resolved_vector_trajectory_std": trajectory_norm(phases, "resolved_vector"),
        "porosity_trajectory": porosity_trajectory,
        "porosity_trajectory_std": trajectory_norm(phases, "porosity"),
        "final_resolved_vector": final_resolved,
        "final_hamiltonian": final_hamiltonian,
        "final_porosity": final_porosity,
    }


def rollout_summaries(request_text: str = "", emotional_input: Optional[int] = None) -> List[Dict[str, Any]]:
    """Roll out all 64 hexagrams and return per-hex summaries for training."""
    rollouts = rollout_all(request_text, emotional_input)
    return [summarize_rollout(r) for r in rollouts]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Shotgun phase rollout runtime")
    parser.add_argument("--text", type=str, default="", help="input text for the shotgun")
    parser.add_argument("--emotional-input", type=int, default=None, help="emotional input (0-100)")
    parser.add_argument("--hex", type=int, default=None, help="run only this hexagram")
    parser.add_argument("--out", type=str, default=None, help="write rollout JSON to this path")
    args = parser.parse_args()

    if args.hex:
        rollouts = [rollout_hexagram(args.hex, args.text, args.emotional_input)]
    else:
        rollouts = rollout_all(args.text, args.emotional_input)

    summaries = [summarize_rollout(r) for r in rollouts]

    out_obj = {
        "request_text": args.text,
        "emotional_input": args.emotional_input,
        "hexagon_count": len(rollouts),
        "chain_break_total": sum(len(r["chain_breaks"]) for r in rollouts),
        "rollouts": rollouts,
        "summaries": summaries,
        "quantum_lab_constants": QUANTUM_LAB_CONSTANTS,
    }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(out_obj, indent=2, default=str), encoding="utf-8")
        print(f"[OK] Wrote rollout to {out_path}  ({out_path.stat().st_size} bytes)")
    else:
        print(f"[OK] Rollout for {len(rollouts)} hexagrams")
        print(f"     chain breaks total: {out_obj['chain_break_total']}")
        print(f"     quantum lab constants: {list(QUANTUM_LAB_CONSTANTS.keys())}")
        for s in summaries[:3]:
            print(f"  hex {s['hexagram_id']}: chain_continuous={s['chain_continuous']} "
                  f"ham_std={s['hamiltonian_trajectory_std']:.4f} "
                  f"res_std={s['resolved_vector_trajectory_std']:.4f}")
