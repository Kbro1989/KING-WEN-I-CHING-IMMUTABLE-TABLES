#!/usr/bin/env python3
"""
interpretation_space.py — Count how many distinct interpretations can be derived
from the hexagram classes WITHOUT breaking their individual roles.

A "role" is an invariant of the class: hexagram identity, trigram membership,
category, action, line-state ordering, phase, pool membership. An interpretation
is a *projection* of those invariants into a representation. The constraint is
that a projection must not destroy the invariant it reads — i.e. no two distinct
role-values may collapse to the same interpretation token.

This enumerates the projections that are injective over their source invariant,
and reports the total combinatorial space.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import kingwen_ternary_tables_complete as t

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Source invariants (each is a function hexagram_id -> role value)
# --------------------------------------------------------------------------
def line_states(hid: int):
    return tuple(t.HEXAGRAM_BASE[hid]["binary_bottom_to_top"])


ROLES = {
    # name: (extractor, cardinality_observed)
    "hexagram_identity": (lambda h: h, 64),
    "upper_trigram": (lambda h: t.HEXAGRAM_BASE[h]["upper_idx"], 8),
    "lower_trigram": (lambda h: t.HEXAGRAM_BASE[h]["lower_idx"], 8),
    "category": (lambda h: t.HEXAGRAM_BASE[h]["category"], None),
    "action": (lambda h: t.HEXAGRAM_BASE[h]["action"], None),
    "line_states": (line_states, None),
    "primary_pool": (lambda h: t.HEXAGRAM_INJECTION_SITE[h]["primary_pool"], None),
    "secondary_pool": (lambda h: t.HEXAGRAM_INJECTION_SITE[h]["secondary_pool"], None),
    "porosity": (lambda h: t.HEXAGRAM_INJECTION_SITE[h]["porosity"], None),
}


def main() -> int:
    print("=" * 78)
    print("KING WEN — INTERPRETATION SPACE (role-preserving projections)")
    print("=" * 78)

    # ---- 1. Observed cardinality of each invariant -------------------------
    print("\n1. ROLE INVARIANTS (observed over 64 hexagrams)")
    print(f"{'invariant':<20} {'distinct':>9}  {'injective?':>10}  sample")
    print("-" * 78)
    obs = {}
    for name, (fn, _) in ROLES.items():
        vals = [fn(h) for h in range(1, 65)]
        distinct = len(set(vals))
        obs[name] = distinct
        inj = "yes" if distinct == 64 else f"NO ({distinct}/64)"
        print(f"{name:<20} {distinct:>9}  {inj:>10}  {vals[0]}")

    # ---- 2. Independent invariants ----------------------------------------
    # Two invariants are independent if neither determines the other.
    print("\n2. INDEPENDENT INVARIANT PAIRS")
    print("-" * 78)
    indep = []
    names = list(ROLES)
    for a, b in itertools.combinations(names, 2):
        fa, fb = ROLES[a][0], ROLES[b][0]
        pairs = {(fa(h), fb(h)) for h in range(1, 65)}
        # independent if the joint space is larger than either alone
        if len(pairs) > max(obs[a], obs[b]):
            indep.append((a, b, len(pairs)))
    indep.sort(key=lambda x: -x[2])
    for a, b, n in indep[:12]:
        print(f"  {a:<20} x {b:<20} -> {n:>4} joint classes")
    print(f"  ... {len(indep)} independent pairs total")

    # ---- 3. Interpretation surfaces (representations) ---------------------
    # Each surface reads a subset of invariants and emits a distinct token.
    print("\n3. REPRESENTATION SURFACES (each must stay injective)")
    print("-" * 78)
    surfaces = {
        "9-bit VHDL ROM address":       (64 * 8, "hex x phase -> 0..511"),
        "binary phase state":           (512,    "HEX_PHASE_TO_9BIT"),
        "ternary line configuration":   (729,    "3^6 unconstrained"),
        "ternary phase-resolved":       (729 * 8, "5832"),
        "emotional pool vector":        (66,     "EMOTIONAL_POOL entries"),
        "voice pool":                   (66,     "VOICEBOX_VOICE_POOL"),
        "porosity tier":                (5,      "POROSITY_LEVELS"),
        "yao vocabulary token":         (9,      "9 yao terms"),
        "trigram pair":                 (64,     "8 x 8"),
        "category":                     (obs["category"], "observed"),
        "action":                       (obs["action"], "observed"),
        "line-state tuple":             (obs["line_states"], "observed"),
        "kit model (embodiment)":       (64,     "kit_*.json"),
        "avatar mesh (64 x 8)":         (512,    "PLY"),
        "save-string pellet":           (64,     "V2.1 batch slots"),
    }
    for name, (card, note) in surfaces.items():
        print(f"  {name:<30} {card:>7}   {note}")

    # ---- 4. Total role-preserving combinatorial space ---------------------
    print("\n4. COMBINATORIAL SPACE")
    print("-" * 78)
    combos = {
        "hex x phase (binary resolved)":        64 * 8,
        "hex x phase x porosity_tier":          64 * 8 * 5,
        "hex x phase x yao_vocab(6 lines)":     64 * 8 * (9 ** 6),
        "ternary manifold":                     729,
        "ternary x phase":                      729 * 8,
        "ternary x phase x porosity_tier":      729 * 8 * 5,
        "hex x ternary x phase":                64 * 729 * 8,
        "hex x ternary x phase x porosity":     64 * 729 * 8 * 5,
        "full ternary line permutations":       64 * 729 * 6,
        "pool pairings (66 choose 2, ordered)": 66 * 65,
    }
    for k, v in combos.items():
        print(f"  {k:<42} {v:>18,}")

    out = {
        "invariants_observed": obs,
        "independent_pairs": [{"a": a, "b": b, "joint_classes": n} for a, b, n in indep],
        "representation_surfaces": {k: v[0] for k, v in surfaces.items()},
        "combinatorial_space": combos,
    }
    dest = ROOT / "DATASETS" / "interpretation_space.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
