#!/usr/bin/env python3
"""
rl_shotgun_measurables.py — RL measurables extraction from shotgun rollout output.

Turns a single hexagram's 8-phase rollout (from shotgun_rollout_runtime.rollout_hexagram)
into RL-relevant quantities: per-phase state, trajectory-based rewards, chain-continuity
penalties, and a final terminal signal suitable for policy/value training.

Design anchors (from rl_intro2.rst):
  - model-free: these are rollouts sampled from the real environment (expand_hexagram),
    not a learned dynamics model. We extract what the rollout produced.
  - what to learn from a rollout: discounted return, state distribution, per-step
    rewards, advantage proxies (trajectory variance as intrinsic signal), terminal state.
  - policies/Q-functions/value functions: this module produces the tuples a learner
    would consume; it does not train a policy.
  - planning loops: the rollout IS the planned sequence (8 phases chained). The measurables
    describe what happened across that plan.
  - extrapolation: trajectory_std and chain_breaks flag where the rollout diverges from
    smooth continuation — those are the edges a learner should care about.

Does NOT import from or depend on the switchboard or visualization scripts.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# This module is meant to be importable from scripts/ or from repo root.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from emotional_engine import VEC_KEYS, _hamiltonian_energy, derive_dynamic_emotional_input
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_INFO


# ---------------------------------------------------------------------------
# Per-vec helpers
# ---------------------------------------------------------------------------

def vec_norm(v: Dict[str, float]) -> float:
    """L2-ish norm over the 5 canonical vector keys."""
    return math.sqrt(sum(float(v.get(k, 0.0)) ** 2 for k in VEC_KEYS))


def vec_entropy(v: Dict[str, float]) -> float:
    """Shannon entropy over normalized vector components (as a diversity proxy).

    A vector concentrated in one axis has low entropy; a spread-out vector has high
    entropy. This is an intrinsic-motivation-style signal: states with higher vector
    spread are "more informative" in the Shannon sense.
    """
    vals = [max(1e-9, float(v.get(k, 0.0))) for k in VEC_KEYS]
    total = sum(vals)
    if total <= 0.0:
        return 0.0
    p = [x / total for x in vals]
    return -sum(pp * math.log(pp) for pp in p)


def vec_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Cosine similarity between two 5-axis vectors."""
    num = sum(float(a.get(k, 0.0)) * float(b.get(k, 0.0)) for k in VEC_KEYS)
    da = math.sqrt(sum(float(a.get(k, 0.0)) ** 2 for k in VEC_KEYS))
    db = math.sqrt(sum(float(b.get(k, 0.0)) ** 2 for k in VEC_KEYS))
    if da <= 1e-9 or db <= 1e-9:
        return 0.0
    return num / (da * db)


# ---------------------------------------------------------------------------
# Single-step reward decomposition
# ---------------------------------------------------------------------------

def step_reward(
    phase_rec: Dict[str, Any],
    prev_rec: Optional[Dict[str, Any]] = None,
    *,
    hamiltonian_weight: float = 0.1,
    change_weight: float = 1.0,
    entropy_weight: float = 0.5,
    coherence_weight: float = 0.4,
    chain_bonus: float = 0.2,
) -> Dict[str, Any]:
    """Decompose one phase step into an RL reward tuple.

    Returns a dict with:
      - total: scalar reward for this step
      - components: breakdown (hamiltonian, change, entropy, coherence, chain_bonus)
      - state: the phase record serialized for the learner
      - step_index: position in the rollout
    """
    resolved = phase_rec.get("resolved_vector", {})
    expanded = phase_rec.get("expanded_vector", {})
    porosity = phase_rec.get("porosity", 0.0)
    hamiltonian = phase_rec.get("hamiltonian_energy", 0.0)
    prev_resolved = prev_rec.get("resolved_vector", {}) if prev_rec else None

    # Hamiltonian signal: how much structural energy this phase carries
    h_signal = float(hamiltonian) * hamiltonian_weight

    # Change signal: how much the resolved vector moved vs the prior step
    if prev_resolved:
        change = vec_norm({k: float(resolved.get(k, 0.0)) - float(prev_resolved.get(k, 0.0))
                           for k in VEC_KEYS})
    else:
        change = 0.0
    change_signal = change * change_weight

    # Entropy signal: spread of the resolved vector across the 5 axes
    entropy_signal = vec_entropy(resolved) * entropy_weight

    # Coherence signal: the coherence axis value of the resolved vector
    coherence_signal = float(resolved.get("coherence", 0.0)) * coherence_weight

    # Chain bonus: reward continuity — if this step carries forward prior values cleanly
    chain_bonus_signal = chain_bonus if phase_rec.get("rollout_context", {}).get("carry_break") is not True else 0.0

    total = h_signal + change_signal + entropy_signal + coherence_signal + chain_bonus_signal

    return {
        "total": round(total, 6),
        "components": {
            "hamiltonian": round(h_signal, 6),
            "change": round(change_signal, 6),
            "entropy": round(entropy_signal, 6),
            "coherence": round(coherence_signal, 6),
            "chain_bonus": round(chain_bonus_signal, 6),
        },
        "state": {
            "hexagram_id": phase_rec.get("hexagram_id"),
            "phase_bits": phase_rec.get("phase_bits"),
            "phase_temporal": phase_rec.get("phase_temporal"),
            "resolved_vector": {k: round(float(resolved.get(k, 0.0)), 6) for k in VEC_KEYS},
            "expanded_vector": {k: round(float(expanded.get(k, 0.0)), 6) for k in VEC_KEYS},
            "porosity": porosity,
            "hamiltonian_energy": round(float(hamiltonian), 6),
            "carry_break": phase_rec.get("rollout_context", {}).get("carry_break", False),
        },
        "step_index": phase_rec.get("phase_bits", 0),
    }


# ---------------------------------------------------------------------------
# Discounted return over a rollout
# ---------------------------------------------------------------------------

def discounted_returns(
    steps: List[Dict[str, Any]],
    gamma: float = 0.95,
) -> List[float]:
    """Compute discounted returns G_t = sum_{k>=t} gamma^(k-t) * r_k.

    steps: list of step_reward dicts (in temporal order).
    Returns list of same length with G_t per step.
    """
    n = len(steps)
    returns = [0.0] * n
    running = 0.0
    for t in range(n - 1, -1, -1):
        running = steps[t]["total"] + gamma * running
        returns[t] = round(running, 6)
    return returns


# ---------------------------------------------------------------------------
# Trajectory-level measurables
# ---------------------------------------------------------------------------

def trajectory_stats(rollout: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate statistics across the 8-phase rollout for a single hexagram.

    Produces the quantities a value/policy learner would condition on:
      - per-step rewards and discounted returns
      - trajectory variance (intrinsic signal)
      - initial -> final state delta
      - chain continuity summary
      - terminal state
    """
    phases = rollout.get("phases", [])
    if not phases:
        return {"hexagram_id": rollout.get("hexagram_id"), "empty": True}

    hex_id = rollout.get("hexagram_id")
    step_recs = []
    prev: Optional[Dict[str, Any]] = None

    for ph in phases:
        # Attach the rollout context (carry-forward info) to the phase for step_reward
        ph_with_ctx = dict(ph)
        if "rollout_context" in ph:
            ph_with_ctx["rollout_context"] = ph["rollout_context"]
        sr = step_reward(ph_with_ctx, prev)
        step_recs.append(sr)
        prev = ph_with_ctx

    returns = discounted_returns(step_recs)
    totals = [s["total"] for s in step_recs]

    init_state = step_recs[0]["state"]
    final_state = step_recs[-1]["state"]

    # Initial -> final delta per vector axis
    delta_vector = {
        k: round(float(final_state["resolved_vector"].get(k, 0.0))
                 - float(init_state["resolved_vector"].get(k, 0.0)), 6)
        for k in VEC_KEYS
    }
    delta_norm = round(vec_norm(delta_vector), 6)

    # Chain continuity
    breaks = rollout.get("chain_breaks", [])
    chain_continuous = len(breaks) == 0
    chain_break_total = sum(len(bk) for _, bk in breaks)

    # Trajectory variance (std of step totals) — intrinsic signal
    if len(totals) >= 2:
        mean_t = sum(totals) / len(totals)
        traj_var = math.sqrt(sum((x - mean_t) ** 2 for x in totals) / len(totals))
    else:
        traj_var = 0.0

    # Discounted return summary
    total_return = returns[0] if returns else 0.0
    last_return = returns[-1] if returns else 0.0

    # Terminal signal: is this a "good terminal state"?
    # Heuristic: high coherence + non-zero entropy + no chain breaks
    terminal_goodness = (
        float(final_state["resolved_vector"].get("coherence", 0.0)) * 0.5
        + vec_entropy(final_state["resolved_vector"]) * 0.3
        + (0.2 if chain_continuous else 0.0)
    )

    return {
        "hexagram_id": hex_id,
        "name": HEXAGRAM_BASE[hex_id].get("name", ""),
        "category": HEXAGRAM_BASE[hex_id].get("category", ""),
        "action": HEXAGRAM_BASE[hex_id].get("action", ""),
        "step_count": len(step_recs),
        "steps": step_recs,
        "discounted_returns": returns,
        "total_return": round(total_return, 6),
        "last_return": round(last_return, 6),
        "trajectory_variance": round(traj_var, 6),
        "chain_continuous": chain_continuous,
        "chain_breaks": breaks,
        "chain_break_total": chain_break_total,
        "initial_resolved_vector": init_state["resolved_vector"],
        "final_resolved_vector": final_state["resolved_vector"],
        "delta_vector": delta_vector,
        "delta_norm": delta_norm,
        "terminal_goodness": round(terminal_goodness, 6),
        "initial_entropy": round(vec_entropy(init_state["resolved_vector"]), 6),
        "final_entropy": round(vec_entropy(final_state["resolved_vector"]), 6),
        "initial_coherence": round(float(init_state["resolved_vector"].get("coherence", 0.0)), 6),
        "final_coherence": round(float(final_state["resolved_vector"].get("coherence", 0.0)), 6),
        "per_step_cosine_similarity": [
            round(vec_similarity(step_recs[i]["state"]["resolved_vector"],
                                step_recs[i+1]["state"]["resolved_vector"]), 6)
            for i in range(len(step_recs) - 1)
        ],
    }


def rollout_measurables(
    rollout: Dict[str, Any],
    gamma: float = 0.95,
) -> Dict[str, Any]:
    """Convenience: trajectory_stats + discounted returns on a rollout dict."""
    ts = trajectory_stats(rollout)
    ts["discounted_returns"] = discounted_returns(ts["steps"], gamma)
    return ts


# ---------------------------------------------------------------------------
# Batch: all 64 hexagrams
# ---------------------------------------------------------------------------

def measurables_all(
    request_text: str = "",
    emotional_input: Optional[int] = None,
    gamma: float = 0.95,
) -> List[Dict[str, Any]]:
    """Run rollout + measurables for all 64 hexagrams.

    Import shotgun_rollout_runtime here (not at module top) so this module can
    be imported without triggering the rollout runtime's heavy imports in contexts
    that don't need them.
    """
    from shotgun_rollout_runtime import rollout_all

    emotional_input = derive_dynamic_emotional_input(request_text, emotional_input)
    rollouts = rollout_all(request_text, emotional_input)
    out: List[Dict[str, Any]] = []
    for r in rollouts:
        m = rollout_measurables(r, gamma=gamma)
        out.append(m)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract RL measurables from shotgun rollout output"
    )
    parser.add_argument("--text", type=str, default="",
                        help="input text for the shotgun")
    parser.add_argument("--emotional-input", type=int, default=None,
                        help="emotional input (0-100)")
    parser.add_argument("--hex", type=int, default=None,
                        help="run only this hexagram (1-64)")
    parser.add_argument("--gamma", type=float, default=0.95,
                        help="discount factor for returns")
    parser.add_argument("--out", type=str, default=None,
                        help="write measurables JSON to this path")
    args = parser.parse_args()

    if args.hex:
        from shotgun_rollout_runtime import rollout_hexagram
        r = rollout_hexagram(args.hex, args.text, args.emotional_input)
        m = rollout_measurables(r, gamma=args.gamma)
        out_obj = {"hexagram_id": args.hex, "measurables": m}
    else:
        out_obj = {
            "request_text": args.text,
            "emotional_input": args.emotional_input,
            "gamma": args.gamma,
            "measurables": measurables_all(args.text, args.emotional_input, gamma=args.gamma),
        }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(out_obj, indent=2, default=str), encoding="utf-8")
        print(f"[OK] Wrote RL measurables to {out_path}  ({out_path.stat().st_size} bytes)")
    else:
        m = out_obj["measurables"]
        if isinstance(m, list):
            print(f"[OK] {len(m)} hexagram measurables")
            for mm in m[:3]:
                print(f"  hex {mm['hexagram_id']}: total_return={mm['total_return']:.4f} "
                      f"traj_var={mm['trajectory_variance']:.4f} "
                      f"chain_continuous={mm['chain_continuous']} "
                      f"terminal_goodness={mm['terminal_goodness']:.4f}")
        else:
            print(f"[OK] hex {m['hexagram_id']}: total_return={m['total_return']:.4f} "
                  f"traj_var={m['trajectory_variance']:.4f} "
                  f"chain_continuous={m['chain_continuous']} "
                  f"terminal_goodness={m['terminal_goodness']:.4f}")
