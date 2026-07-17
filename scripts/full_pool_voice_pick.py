"""Full-pool voice pick mapper: every voice weight returns full ranked pool.

Reads VOICEBOX_VOICE_POOL and EMOTIONAL_WEIGHTS from immutable tables.
Returns a deterministic full ranking from all 66 presets per (hexagram, phase).
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

IMMUTABLE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")
spec = importlib.util.spec_from_file_location("kwt_pool3", str(IMMUTABLE_PATH))
mod = importlib.util.module_from_spec(spec)
sys.modules["kwt_pool3"] = mod
spec.loader.exec_module(mod)

VOICEBOX_VOICE_POOL = getattr(mod, "VOICEBOX_VOICE_POOL", {})
EMOTIONAL_WEIGHTS = getattr(mod, "EMOTIONAL_WEIGHTS", {})
HEXAGRAM_INJECTION_SITE = getattr(mod, "HEXAGRAM_INJECTION_SITE", {})
HEXAGRAM_BASE = getattr(mod, "HEXAGRAM_BASE", {})


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _resolve_target(hexagram_id: int) -> tuple[float, float, float, float, float]:
    ew = EMOTIONAL_WEIGHTS.get(str(hexagram_id), {})
    return (
        ew.get("chaos", 0.5),
        ew.get("whimsy", 0.5),
        ew.get("darkTone", 0.5),
        ew.get("coherence", 0.5),
        ew.get("voiceWeight", 0.5),
    )


def pick_voice_from_pool(
    hexagram_id: int,
    phase_bits: int = 0,
    axis_weights: tuple[float, float, float, float, float] | None = None,
    top_k: int | None = None,
) -> list[dict]:
    """Return full ranked pool of 66 presets, or top_k if specified."""
    target = axis_weights if axis_weights is not None else _resolve_target(hexagram_id)
    salt = hash((hexagram_id, phase_bits))

    candidates = []
    for name, vec in VOICEBOX_VOICE_POOL.items():
        sim = _cosine_similarity(target, vec)
        tiebreak = (salt + hash(name)) % 1000 / 1000.0
        candidates.append({
            "name": name,
            "vector": vec,
            "similarity": round(sim, 6),
            "tiebreak": round(tiebreak, 4),
        })

    candidates.sort(key=lambda c: (-c["similarity"], c["tiebreak"]))
    for i, c in enumerate(candidates):
        c["rank"] = i + 1

    if top_k is not None:
        return candidates[:top_k]
    return candidates


def get_full_pool_size() -> int:
    return len(VOICEBOX_VOICE_POOL)


def get_pool_names() -> list[str]:
    return list(VOICEBOX_VOICE_POOL.keys())


def verify_full_pool_coverage() -> dict:
    results = {
        "total_combinations": 512,
        "pool_size": get_full_pool_size(),
        "mismatches": [],
    }
    for hid in range(1, 65):
        for phase in range(8):
            ranked = pick_voice_from_pool(hid, phase)
            if not ranked:
                results["mismatches"].append((hid, phase))
    results["coverage"] = (512 - len(results["mismatches"])) / 512.0
    return results


if __name__ == "__main__":
    print("=== Full Pool Voice Pick (full ranked output) ===")
    print(f"Pool size: {get_full_pool_size()}")
    print()

    for hid in [1, 2, 63]:
        name = HEXAGRAM_BASE[hid]["name"]
        print(f"Hexagram {hid} ({name}), phase 0 full ranking:")
        ranked = pick_voice_from_pool(hid, 0)
        for c in ranked:
            marker = " <- TOP" if c["rank"] == 1 else ""
            print(f"  {c['rank']:2d}. {c['name']:30s} sim={c['similarity']:.6f}{marker}")
        print()

    cov = verify_full_pool_coverage()
    print(f"Coverage: {cov['coverage']:.1%} ({512 - len(cov['mismatches'])}/512)")
    print(f"Pool size: {cov['pool_size']}")
    if cov["mismatches"]:
        print(f"Mismatches: {len(cov['mismatches'])}")
    else:
        print("Mismatches: 0")
