#!/usr/bin/env python3
"""King Wen quantum process: proven-method pass-tracked superposition."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, cast

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_train_data.superposition_capture import capture_superposition

_ARTIFACT = Path(__file__).resolve().parent.parent / "kingwen_train_data/quantum_process_trials.jsonl"
Record = Dict[str, Any]
Records = List[Record]


def _append_jsonl(path: Path, row: Record) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _coherence_score(snapshot: Record) -> float:
    vectors: List[float] = []
    cards: Records = cast(Records, snapshot.get("resolve_cards", []))
    for card in cards[:64]:
        rv: Dict[str, Any] = card.get("resolved_vector") or {}
        coherence = float(rv.get("coherence", 0.0) or 0.0)
        vectors.append(coherence)
    if not vectors:
        return 0.0
    return sum(vectors) / len(vectors)


def _coverage_stats(snapshot: Record) -> Record:
    verification: Record = snapshot.get("verification") or {}
    hexagrams: Record = verification.get("hexagram_coverage") or {}
    pools: Record = verification.get("pool_coverage") or {}
    phases: Record = verification.get("phase_coverage") or {}
    vectors: Record = verification.get("vector_spread") or {}
    return {
        "coverage_rate": float(hexagrams.get("coverage_rate", 0) or 0),
        "pool_hits": float(pools.get("pool_hits", 0) or 0),
        "phase_branches": float(phases.get("phase_branches", 0) or 0),
        "vector_spread_sum": float(sum((vectors.get("spread", {}) or {}).get(k, 0) or 0 for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"])),
    }


def _measure_expansion(before: Record, after: Record) -> Record:
    before_verification: Record = before.get("verification") or {}
    after_verification: Record = after.get("verification") or {}
    before_resolved = int(before_verification.get("resolved_count", 0) or 0)
    after_resolved = int(after_verification.get("resolved_count", 0) or 0)
    expansion: Record = {
        "resolved_delta": after_resolved - before_resolved,
        "before_resolved": before_resolved,
        "after_resolved": after_resolved,
    }
    return expansion


def _understanding_delta(before: Record, after: Record) -> Record:
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


def _adaptive_selection_gap(after: Record) -> List[str]:
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


def run_quantum_process(query: str, *, emotional_input: int = 50, max_passes: int = 5, patience: int = 2) -> Record:
    base: Record = capture_superposition(query, emotional_input=emotional_input, record_math=False)
    passes: Records = []
    baseline_coherence = _coherence_score(base)
    best_coherence = baseline_coherence
    improving_passes = 0
    current: Record = base
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
        verification: Record = current.get("verification") or {}
        consensus_proof: Record = current.get("consensus_proof") or {}
        anchor_records: Records = cast(Records, current.get("anchors", []))
        verdict = str(verification.get("verdict", "unknown"))
        consensus = str(consensus_proof.get("consensus_hexagram_name") or "")
        anchors = [int(anchor.get("hexagram_id") or 0) for anchor in anchor_records[:3]]
        validation_title: str = (
            f"pass={pass_index} verdict={verdict} consensus={consensus} "
            f"expansion={expansion['resolved_delta']} coherence_delta={understanding['coherence_delta']:.4f} "
            f"improving_passes={improving_passes} gaps={gaps}"
        )
        record: Record = {
            "pass_index": pass_index,
            "validation_title": validation_title,
            "query": expanded_query,
            "bias": bias,
            "verdict": verdict,
            "expansion": expansion,
            "understanding": understanding,
            "anchors": anchors,
            "consensus": consensus_proof,
            "resolved_count": verification.get("resolved_count"),
            "coherence": coherence,
            "coverage": _coverage_stats(current),
            "gaps": gaps,
        }
        passes.append(record)
        _append_jsonl(_ARTIFACT, record)
        if improving_passes >= patience:
            break

    final = current
    summary: Record = {
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


# NOTE: No automatic git push. Per project rule, pushes occur only after explicit
# user acceptance. Coherence improvement is reported in the summary; the user
# decides when to commit/push.
def should_git_push(_summary: Record) -> bool:
    return False
