#!/usr/bin/env python3
"""Self-resolving King Wen quantum superposition capture.

Appends one batched math record per new source, using live engine output as
ground truth. No hard-coded answer paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from emotional_engine import collapse_full_128, _compute_consensus_from_resolved
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise RuntimeError(f"emotional_engine is required: {exc}")


_SUPERPOSITION_ROOT = Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
_SUPERPOSITION_PATH = _SUPERPOSITION_ROOT / "kingwen_train_data/superposition_capture.jsonl"
_PARSER_BATCH_PATH = _SUPERPOSITION_ROOT / "kingwen_train_data/wiki_math_research_batch_2026-07-11.json"


def _append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _domain_signature(query: str) -> Dict[str, Any]:
    text = (query or "").lower()
    tokens = [t for t in text.replace("/", " ").split() if t]
    return {
        "query": query,
        "query_length": len(query or ""),
        "token_count": len(tokens),
        "tokens": tokens[:80],
        "operators": [t for t in tokens if t in {"if", "not", "maybe", "and", "or", "then", "else", "when"}],
    }


def _pool_coverage(resolved: List[Dict[str, Any]]) -> Dict[str, Any]:
    pools: List[str] = []
    for item in resolved:
        inject = item.get("inject_site") or {}
        if inject.get("primary_pool"):
            pools.append(inject["primary_pool"])
        if inject.get("secondary_pool"):
            pools.append(inject["secondary_pool"])
    hit = sorted(set(pools))
    return {
        "pool_hits": len(hit),
        "unique_pools": hit,
        "pool_touch_rate": round(len(hit) / max(1, len(set(pools))), 4),
    }


def _phase_coverage(resolved: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for item in resolved:
        counts[str(item.get("phase_temporal") or "")] = counts.get(str(item.get("phase_temporal") or ""), 0) + 1
    return {"phase_counts": counts, "phase_branches": len(counts)}


def _vector_spread(resolved: List[Dict[str, Any]]) -> Dict[str, Any]:
    axes = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
    mins = {k: 1e18 for k in axes}
    maxs = {k: -1e18 for k in axes}
    sums = {k: 0.0 for k in axes}
    count = 0
    for item in resolved:
        rv = item.get("resolved_vector") or {}
        for k in axes:
            v = float(rv.get(k, 0.0) or 0.0)
            mins[k] = min(mins[k], v)
            maxs[k] = max(maxs[k], v)
            sums[k] += v
        count += 1
    spread = {k: round((maxs[k] - mins[k]), 6) for k in axes}
    means = {k: round((sums[k] / count), 6) if count else 0.0 for k in axes}
    return {"spread": spread, "means": means, "resolved_count": count}


def _hexagram_coverage(resolved: List[Dict[str, Any]]) -> Dict[str, Any]:
    ids = sorted({int(item.get("hexagram_id") or 0) for item in resolved if item.get("hexagram_id")})
    return {"hexagram_count": len(ids), "hexagram_ids": ids, "coverage_rate": round(len(ids) / 64, 4)}


def _line_state_profile(resolved: List[Dict[str, Any]]) -> Dict[str, Any]:
    yin = yang = yao = 0
    for item in resolved:
        for ls in item.get("line_states", []):
            key = str(ls.get("yao_key") or "")
            if key.endswith("_yin"):
                yin += 1
            elif key.endswith("_yang"):
                yang += 1
            elif key.endswith("_yao"):
                yao += 1
    total = max(1, yin + yang + yao)
    return {"yin": yin, "yang": yang, "yao": yao, "ratios": {"yin": round(yin/total, 4), "yang": round(yang/total, 4), "yao": round(yao/total, 4)}}


def _consensus_proof(result: Dict[str, Any], emotional_input: int) -> Dict[str, Any]:
    consensus = _compute_consensus_from_resolved(result.get("resolved", []), emotional_input=emotional_input)
    return {
        "consensus_hexagram_id": consensus.get("consensus_hexagram_id"),
        "consensus_hexagram_name": consensus.get("consensus_hexagram_name"),
        "consensus_temporal": consensus.get("consensus_temporal"),
        "consensus_yao": consensus.get("consensus_yao"),
        "consensus_vector": consensus.get("consensus_vector"),
        "consensus_explanation": consensus.get("consensus_explanation"),
    }


def _anchors(resolved: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    scored = []
    for item in resolved:
        rv = item.get("resolved_vector") or {}
        score = float(sum(float(rv.get(k, 0.0) or 0.0) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]))
        scored.append((score, int(item.get("hexagram_id") or 0), str(item.get("phase_temporal") or ""), item))
    scored.sort(key=lambda row: (row[0], row[1], row[2]), reverse=True)
    top = []
    for score, hexagram_id, phase_temporal, item in scored[:limit]:
        top.append({
            "hexagram_id": item.get("hexagram_id"),
            "phase_temporal": item.get("phase_temporal"),
            "score": round(score, 6),
            "resolved_vector": item.get("resolved_vector"),
            "inject_site": item.get("inject_site"),
        })
    return top


def capture_superposition(query: str, *, emotional_input: int = 50, record_math: bool = True) -> Dict[str, Any]:
    result = collapse_full_128(emotional_input=emotional_input, request_text=query)
    resolved = result.get("resolved", [])
    expanded = result.get("expanded", [])
    domain_signature = _domain_signature(query)
    pool_coverage = _pool_coverage(resolved)
    phase_coverage = _phase_coverage(resolved)
    vector_spread = _vector_spread(resolved)
    hexagram_coverage = _hexagram_coverage(resolved)
    line_state_profile = _line_state_profile(resolved)
    consensus_proof = _consensus_proof(result, emotional_input)
    anchors = _anchors(resolved)
    verification = {
        "expanded_count": len(expanded),
        "resolved_count": len(resolved),
        "pool_coverage": pool_coverage,
        "phase_coverage": phase_coverage,
        "vector_spread": vector_spread,
        "hexagram_coverage": hexagram_coverage,
        "line_state_profile": line_state_profile,
        "anchors": anchors,
        "consensus_proof": consensus_proof,
        "verdict": _verdict(hexagram_coverage, pool_coverage, phase_coverage, vector_spread),
    }
    resolve_cards = []
    for item in resolved:
        resolve_cards.append({
            "hexagram_id": item.get("hexagram_id"),
            "hexagram_symbols": item.get("hexagram_symbols"),
            "phase_bits": item.get("phase_bits"),
            "phase_temporal": item.get("phase_temporal"),
            "phase_polarity": item.get("phase_polarity"),
            "inject_site": item.get("inject_site"),
            "line_states": item.get("line_states", [])[:6],
            "resolved_vector": item.get("resolved_vector"),
            "sample_paths": item.get("sample_paths", [])[:3],
            "yao_vocabulary": item.get("yao_vocabulary"),
            "checklist": item.get("checklist", [])[:8],
        })
    output = {
        "query": query,
        "domain_signature": domain_signature,
        "emotional_input": emotional_input,
        "superposition_state": {
            "total_expanded": len(expanded),
            "total_resolved": len(resolved),
            "expanded": expanded,
            "resolved": resolved[:64],
        },
        "resolve_cards": resolve_cards,
        "domain_coverage": {
            "pools": pool_coverage,
            "phases": phase_coverage,
            "hexagrams": hexagram_coverage,
            "line_states": line_state_profile,
            "vectors": vector_spread,
        },
        "anchors": anchors,
        "consensus_proof": consensus_proof,
        "verification": verification,
        "recorded_math": bool(record_math),
    }
    if record_math:
        _append_jsonl(_SUPERPOSITION_PATH, output)
    return output


def _verdict(hexagram_coverage: Dict[str, Any], pool_coverage: Dict[str, Any], phase_coverage: Dict[str, Any], vector_spread: Dict[str, Any]) -> str:
    if hexagram_coverage.get("coverage_rate", 0) < 0.95:
        return "incomplete_hexagram_coverage"
    if pool_coverage.get("pool_hits", 0) < 10:
        return "incomplete_pool_coverage"
    if phase_coverage.get("phase_branches", 0) < 8:
        return "incomplete_phase_coverage"
    spread = vector_spread.get("spread", {})
    if any(abs(spread.get(k, 0)) < 1e-6 for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]):
        return "insufficient_vector_spread"
    return "optimal_expansion_reached"


def append_math_batch_record(batch_path: Optional[str] = None) -> Dict[str, Any]:
    path = Path(batch_path) if batch_path else _PARSER_BATCH_PATH
    if not path.exists():
        return {"status": "missing_batch", "path": str(path)}
    try:
        batch = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "bad_batch", "error": str(exc), "path": str(path)}
    math_pages = sum(len(entry.get("pages", [])) for entry in batch.get("wiki_math", []))
    terms = [entry.get("term") for entry in batch.get("wikipedia", [])]
    record = {
        "status": "recorded",
        "math_pages": math_pages,
        "terms": terms,
        "parser_notes_count": len(batch.get("parser_notes", [])),
        "superposition_recorded": _SUPERPOSITION_PATH.exists(),
        "path": str(_SUPERPOSITION_PATH),
    }
    _append_jsonl(_SUPERPOSITION_PATH, record)
    return record
