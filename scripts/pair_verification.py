#!/usr/bin/env python3
"""
Pair-Dynamics Verification Script
================================

Regenerates inversion/complement pairs from canonical binary encodings
(king_wen_64_verified.json), asserts expected counts, compares against
pair_dynamics_verification.json, and fails if the artifact disagrees.

Usage:
    python pair_verification.py

Canonical source: king_wen_64_verified.json (64 hexagrams, binary field)
Artifact: docs/pair_dynamics_verification.json
"""

import json
import os
import sys

BASE = r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES'
CANONICAL_PATH = os.path.join(BASE, 'king_wen_64_verified.json')
ARTIFACT_PATH = os.path.join(BASE, 'docs', 'pair_dynamics_verification.json')


def load_canonical(path):
    """Load canonical hexagram table and return hex_id -> binary mapping."""
    with open(path, 'r') as f:
        data = json.load(f)
    hex_binary = {}
    for h in data.get('hexagrams', []):
        hid = h['id']
        binary = h.get('binary', '')
        hex_binary[hid] = binary.zfill(6)
    return hex_binary


def generate_pairs(hex_binary):
    """
    Generate inversion (reversed bits) and complement (flipped bits)
    pairs from canonical 6-bit encodings.
    
    Bit order convention (per canonical table):
    - Six-bit encoding read bottom-to-top.
    - Line 0 = bottom (young yin), Line 5 = top (old yang).
    - Inversion = reverse the six bits (line_0<->line_5, line_1<->line_4, line_2<->line_3).
    - Complement = flip each bit (0->1, 1->0) at every position.
    
    Returns:
        (inversion_pairs, complement_pairs) as sorted lists of [hex_a, hex_b]
        and same_partner_dual_pairs list of [hex_a, hex_b]
    """
    inversion_pairs = set()
    complement_pairs = set()
    
    for hex_id in sorted(hex_binary.keys()):
        binary = hex_binary[hex_id]
        
        # Inversion: reverse the six bits
        reversed_bits = binary[::-1]
        for other_id in sorted(hex_binary.keys()):
            if other_id <= hex_id:
                continue
            if hex_binary[other_id] == reversed_bits:
                inversion_pairs.add(tuple(sorted([hex_id, other_id])))
                break
        
        # Complement: flip all six bits
        complemented = ''.join('1' if b == '0' else '0' for b in binary)
        for other_id in sorted(hex_binary.keys()):
            if other_id <= hex_id:
                continue
            if hex_binary[other_id] == complemented:
                complement_pairs.add(tuple(sorted([hex_id, other_id])))
                break
    
    return sorted(inversion_pairs), sorted(complement_pairs)


def main():
    print("Pair-Dynamics Verification")
    print("=" * 50)
    print(f"Canonical source: {CANONICAL_PATH}")
    print(f"Artifact: {ARTIFACT_PATH}")
    print()
    
    # Load canonical
    print("Loading canonical tables...")
    hex_binary = load_canonical(CANONICAL_PATH)
    print(f"  Loaded {len(hex_binary)} canonical hexagrams")
    
    # Generate pairs from canonical
    print("Generating pairs from canonical encodings...")
    gen_inv, gen_comp = generate_pairs(hex_binary)
    gen_same = sorted([p for p in gen_inv if tuple(p) in [tuple(p) for p in gen_comp]])
    
    print(f"  Generated {len(gen_inv)} inversion pairs")
    print(f"  Generated {len(gen_comp)} complement pairs")
    print(f"  Generated {len(gen_same)} same-partner dual pairs")
    
    # Load artifact
    print("Loading artifact...")
    with open(ARTIFACT_PATH, 'r') as f:
        artifact = json.load(f)
    
    # Assert expected counts
    print("=== ASSERTING EXPECTED COUNTS ===")
    assert len(gen_inv) == 28, f"Expected 28 inversion pairs, got {len(gen_inv)}"
    print(f"  [PASS] Inversion pairs = 28")
    
    assert len(gen_comp) == 32, f"Expected 32 complement pairs, got {len(gen_comp)}"
    print(f"  [PASS] Complement pairs = 32")
    
    assert len(gen_same) == 4, f"Expected 4 same-partner pairs, got {len(gen_same)}"
    print(f"  [PASS] Same-partner pairs = 4")
    
    # Compare against artifact
    print("=== COMPARING AGAINST ARTIFACT ===")
    art_inv = set(tuple(p) for p in artifact['inversion_pairs'])
    art_comp = set(tuple(p) for p in artifact['complement_pairs'])
    art_same = set(tuple(p) for p in artifact['same_partner_dual_pairs'])
    
    gen_inv_set = set(tuple(p) for p in gen_inv)
    gen_comp_set = set(tuple(p) for p in gen_comp)
    gen_same_set = set(tuple(p) for p in gen_same)
    
    assert gen_inv_set == art_inv, f"Inversion pairs differ"
    print(f"  [PASS] Inversion pairs match artifact ({len(gen_inv_set)})")
    
    assert gen_comp_set == art_comp, f"Complement pairs differ"
    print(f"  [PASS] Complement pairs match artifact ({len(gen_comp_set)})")
    
    assert gen_same_set == art_same, f"Same-partner pairs differ"
    print(f"  [PASS] Same-partner dual pairs match artifact ({len(gen_same_set)})")
    
    # Final summary
    print("")
    print("VERIFICATION COMPLETE: ALL CHECKS PASSED")
    print(f"  - Inversion pairs: {len(gen_inv_set)}")
    print(f"  - Complement pairs: {len(gen_comp_set)}")
    print(f"  - Same-partner dual pairs: {len(gen_same_set)}")
    print(f"  - Canonical hexagrams: {len(hex_binary)}")
    print("=" * 50)


if __name__ == '__main__':
    main()
