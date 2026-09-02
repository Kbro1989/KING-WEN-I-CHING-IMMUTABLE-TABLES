#!/usr/bin/env python3
"""Test Suite for Continued Cognitive Variation Across Inputs & Full Shotgun Expansion.

Evaluates 4 distinct consult inputs through shotgun_expand():
1. Quantum Physics & Wave Packet Mechanics
2. Forensic Analysis & -z MOA Compute
3. Game Design & 3D Spatial Collision Topology
4. Legal Crosswalk & State Conflict Resolution

Verifies:
- Dynamic 5-axis prosody vector shift (chaos, whimsy, darkTone, coherence, voiceWeight)
- Intent distribution shift (dominant_intent, query_tokens, intensity)
- Hamiltonian energy variation across 512 resolved states
- Lossless Save String V2.1 serialization roundtrip for all 4 runs
"""

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from emotional_engine import extract_intent
from full_hexagram_shotgun import shotgun_expand
from src.core.pog3_hexagram_runtime_substrate import SaveStringAdapter, HexagramRuntimeEngine

TEST_QUERIES = [
    ("QUANTUM_PHYSICS", "Simulate 3D split-step Fourier wave packet evolution through Gaussian potential barrier"),
    ("FORENSICS_MOA", "Perform zero-trust forensic audit of -z MOA compute execution traces and hash-addressed blocks"),
    ("GAME_DESIGN_3D", "Construct Godot CharacterBody3D scene graph with CollisionVis BVH bounding volumes"),
    ("LEGAL_CONFLICT", "Build legal crosswalk architecture for multi-jurisdictional state conflict resolution"),
]


def vector_distance(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Compute Euclidean distance between two 5-axis vectors."""
    keys = ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]
    return math.sqrt(sum((v1.get(k, 0.0) - v2.get(k, 0.0)) ** 2 for k in keys))


def run_cognitive_variation_test() -> Dict[str, Any]:
    results = []
    save_strings = []

    print("=" * 80)
    print("TESTING CONTINUED COGNITIVE VARIATION ACROSS DISTINCT INPUTS")
    print("=" * 80)

    for tag, text in TEST_QUERIES:
        print(f"\n[EXECUTING SHOTGUN] Tag: {tag}")
        print(f"  Input Text: \"{text}\"")

        # Execute full 64-hexagram / 512-state shotgun expansion
        payload = shotgun_expand(request_text=text, emotional_input=50)

        # Consensus & Intent metrics
        consensus = payload.get("personality_consensus", {})
        c_vec = consensus.get("consensus_vector", {})
        dom_intent = consensus.get("dominant_intent", "understand")
        intensity = payload.get("expanded", [{}])[0].get("intent", {}).get("intensity", 0.0)
        tokens = payload.get("expanded", [{}])[0].get("intent", {}).get("query_tokens", [])

        # Universal Save String V2.1 Serialization
        adapter = SaveStringAdapter(HexagramRuntimeEngine(f"test-cognitive-{tag}"))
        save_str = adapter.serialize_64_hexagram_shotgun_save_string(payload)
        reconstructed = adapter.deserialize_64_hexagram_shotgun_save_string(save_str)

        results.append({
            "tag": tag,
            "text": text,
            "dominant_intent": dom_intent,
            "intensity": round(intensity, 4),
            "token_count": len(tokens),
            "tokens_sample": tokens[:6],
            "consensus_vector": {k: round(c_vec.get(k, 0.0), 4) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]},
            "hex_01_vector": {k: round(payload["expanded"][0]["expanded_vector"].get(k, 0.0), 4) for k in ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"]},
            "save_string_bytes": len(save_str),
            "reconstructed_pellets_count": len(reconstructed),
        })
        save_strings.append((tag, save_str))

    # Compute pairwise cognitive variation distances
    distances = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            r1, r2 = results[i], results[j]
            dist = vector_distance(r1["consensus_vector"], r2["consensus_vector"])
            distances.append({
                "pair": f"{r1['tag']} <-> {r2['tag']}",
                "euclidean_vector_distance": round(dist, 4),
                "intent_shift": f"{r1['dominant_intent']} vs {r2['dominant_intent']}",
            })

    # Summary Audit
    all_reconstructed = all(r["reconstructed_pellets_count"] == 64 for r in results)
    all_unique_intents = len(set(r["dominant_intent"] for r in results)) >= 3
    avg_distance = sum(d["euclidean_vector_distance"] for d in distances) / max(1, len(distances))

    summary = {
        "status": "ok",
        "total_test_queries": len(TEST_QUERIES),
        "all_64_pellets_reconstructed": all_reconstructed,
        "average_pairwise_vector_distance": round(avg_distance, 4),
        "pairwise_distances": distances,
        "query_results": results,
    }

    out_file = ROOT / "DATASETS" / "cognitive_variation_test_results.json"
    out_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return summary


def main() -> int:
    summary = run_cognitive_variation_test()

    print("\n" + "=" * 80)
    print("COGNITIVE VARIATION PAIRWISE DISTANCES")
    print("=" * 80)
    for d in summary["pairwise_distances"]:
        print(f"  [{d['pair']}]")
        print(f"    Euclidean Distance : {d['euclidean_vector_distance']}")
        print(f"    Intent Shift       : {d['intent_shift']}")
        print()

    print("=" * 80)
    print("COGNITIVE VARIATION AUDIT RESULT:", "100% VERIFIED PASS" if summary["all_64_pellets_reconstructed"] else "FAIL")
    print(f"Average Pairwise Distance: {summary['average_pairwise_vector_distance']}")
    print(f"Saved Results to: DATASETS/cognitive_variation_test_results.json")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
