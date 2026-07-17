#!/usr/bin/env python3
"""King Wen quantum process: proven-method pass-tracked superposition."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from emotional_engine import (
    collapse_full_128,
    _hamiltonian_energy,
    _gaussian_kernel,
    _trigram_frequency_weight,
    _compute_consensus_from_resolved,
)
from kingwen_train_data.superposition_capture import capture_superposition

_ARTIFACT = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_train_data/quantum_process_trials.jsonl")


def _append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _coherence_score(snapshot: Dict[str, Any]) -> float:
    vectors = []
    for card in snapshot.get("resolve_cards", [])[:64]:
        rv = card.get("resolved_vector") or {}
        coherence = float(rv.get("coherence", 0.0) or 0.0)
        vectors.append(coherence)
    if not vectors:
        return 0.0
    return sum(vectors) / len(vectors)


def _coverage_stats(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    verification = snapshot.get("verification") or {}
    hexagrams = (verification.get("hexagram_coverage") or {})
    pools = (verification.get("pool_coverage") or {})
    phases = (verification.get("phase_coverage") or {})
    vectors = (verification.get("vector_spread") or {})
    return {
        "coverage_rate": float(hexagrams.get("coverage_rate", 0) or 0),
        "pool_hits": float(pools.get("pool_hits", 0) or 0),
        "phase_branches": float(phases.get("phase_branches", 0) or 0),
        "vector_spread_sum": float(sum((vectors.get("spread", {}) or {}).get(k, 0) or 0 for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"])),
    }


def _measure_expansion(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    before_verification = before.get("verification") or {}
    after_verification = after.get("verification") or {}
    before_resolved = before_verification.get("resolved_count", 0)
    after_resolved = after_verification.get("resolved_count", 0)
    expansion = {
        "resolved_delta": after_resolved - before_resolved,
        "before_resolved": before_resolved,
        "after_resolved": after_resolved,
    }
    return expansion


def _understanding_delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    before_coherence = _coherence_score(before)
    after_coherence = _coherence_score(after)
    before_coverage = _coverage_stats(before)
    after_coverage = _coverage_stats(after)
    direction = "increased" if (after_coherence - before_coherence) > 1e-6 else "decreased" if (after_coherence - before_coherence) < -1e-6 else "unchanged"
    return {
        "before_coherence": before_coherence,
        "after_coherence": after_coherence,
        "coherence_delta": after_coherence - before_coherence,
        "before_coverage": before_coverage,
        "after_coverage": after_coverage,
        "coverage_delta": {
            "coverage_rate": after_coverage["coverage_rate"] - before_coverage["coverage_rate"],
            "pool_hits": after_coverage["pool_hits"] - before_coverage["pool_hits"],
            "phase_branches": after_coverage["phase_branches"] - before_coverage["phase_branches"],
            "vector_spread_sum": after_coverage["vector_spread_sum"] - before_coverage["vector_spread_sum"],
        },
        "understanding_direction": direction,
    }


def _adaptive_selection_gap(after: Dict[str, Any]) -> List[str]:
    coverage = _coverage_stats(after)
    gaps = []
    if coverage["coverage_rate"] < 0.99:
        gaps.append("hexagram_coverage")
    if coverage["pool_hits"] < 12:
        gaps.append("pool_coverage")
    if coverage["phase_branches"] < 8:
        gaps.append("phase_coverage")
    if coverage["vector_spread_sum"] < 1.5:
        gaps.append("vector_spread")
    return gaps


def run_quantum_process(query: str, *, emotional_input: int = 50, max_passes: int = 5, patience: int = 2) -> Dict[str, Any]:
    base = capture_superposition(query, emotional_input=emotional_input, record_math=False)
    passes: List[Dict[str, Any]] = []
    baseline_coherence = _coherence_score(base)
    best_coherence = baseline_coherence
    improving_passes = 0
    current = base
    seed = query

    for pass_index in range(1, max_passes + 1):
        before = current
        gaps = _adaptive_selection_gap(before)
        bias = " | ".join(gaps) if gaps else "consolidate"
        expanded_query = f"{seed} | pass={pass_index} | expand superposition | bias={bias}"
        current = capture_superposition(expanded_query, emotional_input=emotional_input, record_math=False)
        expansion = _measure_expansion(before, current)
        understanding = _understanding_delta(before, current)
        coherence = _coherence_score(current)
        if understanding.get("understanding_direction") == "increased":
            improving_passes += 1
        else:
            improving_passes = 0
        if coherence > best_coherence:
            best_coherence = coherence
        verdict = current.get("verification", {}).get("verdict", "unknown")
        consensus = current.get("consensus_proof", {}).get("consensus_hexagram_name")
        anchors = [a.get("hexagram_id") for a in current.get("anchors", [])[:3]]
        validation_title = (
            f"pass={pass_index} verdict={verdict} consensus={consensus} "
            f"expansion={expansion['resolved_delta']} coherence_delta={understanding['coherence_delta']:.4f} "
            f"improving_passes={improving_passes} gaps={gaps}"
        )
        record = {
            "pass_index": pass_index,
            "validation_title": validation_title,
            "query": expanded_query,
            "bias": bias,
            "verdict": verdict,
            "expansion": expansion,
            "understanding": understanding,
            "anchors": anchors,
            "consensus": current.get("consensus_proof"),
            "resolved_count": current.get("verification", {}).get("resolved_count"),
            "coherence": coherence,
            "coverage": _coverage_stats(current),
            "gaps": gaps,
        }
        passes.append(record)
        _append_jsonl(_ARTIFACT, record)
        if improving_passes >= patience:
            break

    final = current
    summary = {
        "query": query,
        "emotional_input": emotional_input,
        "max_passes": max_passes,
        "passes": passes,
        "baseline_coherence": baseline_coherence,
        "best_coherence": best_coherence,
        "final_verdict": final.get("verification", {}).get("verdict"),
        "final_coherence": _coherence_score(final),
        "total_expansion_delta": sum((p.get("expansion", {}).get("resolved_delta", 0) or 0) for p in passes),
        "improving_passes": improving_passes,
        "understanding_trajectory": [p.get("understanding", {}).get("understanding_direction") for p in passes],
        "coverage_trajectory": [p.get("coverage", {}) for p in passes],
        "validation_titles": [p.get("validation_title") for p in passes],
        "artifact": str(_ARTIFACT),
    }
    return summary


def should_git_push(summary: Dict[str, Any]) -> bool:
    if summary.get("final_verdict") != "optimal_expansion_reached":
        return False
    if summary.get("improving_passes", 0) < 2:
        return False
    if summary.get("best_coherence", 0) <= summary.get("baseline_coherence", 0):
        return False
    if summary.get("total_expansion_delta", 0) <= 0:
        return False
    return True


def git_push_if_coherent(summary: Dict[str, Any]) -> Dict[str, Any]:
    import subprocess
    repo = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
    if not should_git_push(summary):
        return {"pushed": False, "reason": "coherent expansion not increased"}
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "quantum-process: coherent expansion increased"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)
        return {"pushed": True, "repo": str(repo)}
    except subprocess.CalledProcessError as exc:
        return {"pushed": False, "error": str(exc), "stdout": exc.stdout, "stderr": exc.stderr}
