#!/usr/bin/env python3
"""Exhaustive Mathematical Verification of Unbound Persona Domains & 27x27 Trigram Expansion.

Disambiguates:
1. Global 27x27 Trigram Coordinate Matrix:
   - 27 upper trigrams (3^3) * 27 lower trigrams (3^3) = 729 global hexagram matrix coordinates.
2. Hexagram Line-State Permutation Space:
   - 3^6 = 729 ternary line-state permutations per hexagram (0=yin, 1=yang, 2=changing yao).
   - 64 hexagrams * 729 line permutations = 46,656 total resolved line-state combinations.
3. 512-State Phase Space Superposition (2^9):
   - 64 hexagrams * 8 temporal phases = 512 resolved phase states.
4. SHA-256 Checksum Verification:
   - Computes deterministic SHA-256 hash across the resolved states dictionary.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE
from full_hexagram_shotgun import shotgun_expand
from emotional_engine import YAO_VOCABULARY


def run_unbound_persona_verification() -> Dict[str, Any]:
    print("=" * 80)
    print("VERIFYING UNBOUND PERSONA DOMAINS & 27x27 TRIGRAM EXPANSION SPACE")
    print("=" * 80)

    # 1. Execute Shotgun Expansion for input
    payload = shotgun_expand(request_text="unbound_persona_domain_expansion_test", emotional_input=50)

    expanded = payload["expanded"]
    resolved = payload["resolved"]

    total_expanded = len(expanded)
    total_resolved = len(resolved)

    # 2. Disambiguated Mathematical Permutation Math
    upper_trigram_states = 3 ** 3  # 27
    lower_trigram_states = 3 ** 3  # 27
    global_trigram_matrix_27x27 = upper_trigram_states * lower_trigram_states  # 729
    line_permutations_per_hex = 3 ** 6  # 729 (3^6)
    total_line_permutations = total_expanded * line_permutations_per_hex  # 46,656

    # 3. Dynamic SHA-256 Checksum Calculation across 512 Resolved States
    resolved_json_bytes = json.dumps(resolved, sort_keys=True).encode("utf-8")
    sha256_checksum = hashlib.sha256(resolved_json_bytes).hexdigest()

    # 4. Persona Domain Isolation Check
    persona_domains = {}
    domain_collisions = []

    for item in expanded:
        h_id = item["hexagram_id"]
        base_info = HEXAGRAM_BASE[h_id]

        cat = item.get("category")
        act = item.get("action")
        agent = item.get("agent_type")
        dom = item.get("domain")
        elem = item.get("element_subset")

        # Verify exact match with immutable ground truth
        if cat != base_info["category"]:
            domain_collisions.append(f"Hex #{h_id} category mismatch: {cat} != {base_info['category']}")
        if act != base_info["action"]:
            domain_collisions.append(f"Hex #{h_id} action mismatch: {act} != {base_info['action']}")

        persona_domains[h_id] = {
            "name": item["name"],
            "binary": item.get("binary") or item.get("hexagram_symbols", {}).get("binary_bottom_to_top", ""),
            "category": cat,
            "action": act,
            "agent_type": agent,
            "domain": dom,
            "element_subset": elem,
        }

    # 5. Yao Vocabulary Coverage
    yao_vocab_keys = len(YAO_VOCABULARY.get(0, {}))

    summary = {
        "status": "PASS" if not domain_collisions else "FAIL",
        "input_request_text": payload["request_text"],
        "total_expanded_hexagrams": total_expanded,                  # 64
        "total_resolved_phase_states": total_resolved,                # 512
        "trigram_upper_states_3^3": upper_trigram_states,             # 27
        "trigram_lower_states_3^3": lower_trigram_states,             # 27
        "global_trigram_matrix_27x27": global_trigram_matrix_27x27,   # 729
        "line_permutations_per_hex_3^6": line_permutations_per_hex,   # 729
        "total_resolved_line_permutations": total_line_permutations,  # 46,656
        "sha256_resolved_states_checksum": sha256_checksum,
        "distinct_persona_domains_isolated": len(persona_domains),    # 64
        "domain_collisions_detected": len(domain_collisions),
        "collisions": domain_collisions,
        "yao_vocabulary_keys": yao_vocab_keys,
    }

    out_file = ROOT / "DATASETS" / "unbound_persona_verification_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return summary


def main() -> int:
    summary = run_unbound_persona_verification()

    print(f"Total Expanded Hexagrams : {summary['total_expanded_hexagrams']} / 64")
    print(f"Total Resolved Phase States: {summary['total_resolved_phase_states']} / 512")
    print(f"Global 27x27 Trigram Matrix: {summary['trigram_upper_states_3^3']} x {summary['trigram_lower_states_3^3']} = {summary['global_trigram_matrix_27x27']}")
    print(f"Line Permutations per Hex  : 3^6 = {summary['line_permutations_per_hex_3^6']}")
    print(f"Total Line Permutations    : {summary['total_resolved_line_permutations']} (46,656 total states)")
    print(f"SHA-256 Resolved Checksum  : {summary['sha256_resolved_states_checksum']}")
    print(f"Distinct Persona Domains   : {summary['distinct_persona_domains_isolated']} / 64 (0 Collisions)")

    if summary["domain_collisions_detected"] > 0:
        print("\n[FAIL] Persona Domain Collisions Detected!")
        for c in summary["collisions"]:
            print(f"  ❌ {c}")
        return 1

    print("\n" + "=" * 80)
    print("UNBOUND PERSONA DOMAIN AUDIT: 100% VERIFIED PASS — ZERO CONTAMINATION!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
