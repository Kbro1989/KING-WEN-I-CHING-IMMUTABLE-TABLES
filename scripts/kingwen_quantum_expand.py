#!/usr/bin/env python3
"""
King Wen Quantum Expansion Engine v2.0
Full ternary expansion: 729 hexagrams × 8 phases = 46,656 resolved states

Inputs:
  - scripts/ternary_full_expansion.json (canonical source of truth)
  - DATASETS/quantum_masking_hexagram_integration.json (64-entry mask map)
  - shotgun_expand_output.json (coherence C values for canonical 64)
  - output/per_hex_training/manifest.json (corpus index)

Outputs:
  - kingwen_train_data/quantum_enriched_corpus.jsonl
  - data/hexagram-registry.json (enriched with quantum weights)
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np

_PENNYLANE_AVAILABLE = False
try:
    import pennylane as qml  # noqa: F401

    _PENNYLANE_AVAILABLE = True
except ImportError:
    qml = None  # type: ignore


def _gaussian_kernel(value: float, center: float, fwhm: float) -> float:
    sigma = fwhm / 2.354820045
    diff = value - center
    return np.exp(-(diff * diff) / (2.0 * sigma * sigma))


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TERNARY_EXPANSION = PROJECT_ROOT / "scripts" / "ternary_full_expansion.json"
MASK_MAP_PATH = PROJECT_ROOT / "DATASETS" / "quantum_masking_hexagram_integration.json"
REGISTRY_PATH = PROJECT_ROOT / "data" / "hexagram-registry.json"
PER_HEX_DIR = PROJECT_ROOT / "output" / "per_hex_training"
MANIFEST_PATH = PER_HEX_DIR / "manifest.json"
OUTPUT_CORPUS = PROJECT_ROOT / "kingwen_train_data" / "quantum_enriched_corpus.jsonl"
ORACLE_MASTER = PROJECT_ROOT / "shotgun_expand_output.json"

MaskMode = Literal["MEASURE", "SEVER", "ZERO_ROT", "ATTENTION", "PASS"]

# Load once at import
TERNARY_DATA = json.loads(TERNARY_EXPANSION.read_text(encoding="utf-8"))
MASK_DATA = json.loads(MASK_MAP_PATH.read_text(encoding="utf-8"))
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
ORACLE = json.loads(ORACLE_MASTER.read_text(encoding="utf-8"))

# Index structures
TRIGRAMS = TERNARY_DATA.get("trigrams", {})
HEXAGRAMS = TERNARY_DATA.get("hexagrams", {})
RESOLVED = TERNARY_DATA.get("resolved", {})

MASK_MAP = {int(e["hexagram_id"]): e for e in MASK_DATA.get("full_64_masking_map", [])}
HEX_COUNTS = {int(k): v for k, v in MANIFEST.get("hex_counts", {}).items()}

# Coherence lookup: canonical 64 only, from shotgun_expand expanded[]
COHERENCE: Dict[str, float] = {}
for entry in ORACLE.get("expanded", []):
    hid = entry.get("hexagram_id")
    vec = entry.get("expanded_vector", {})
    if hid is not None and vec:
        COHERENCE[str(hid)] = float(vec.get("coherence", 0.5))


def get_mask(hexagram_id: int) -> MaskMode:
    if hexagram_id <= 64:
        return MASK_MAP.get(hexagram_id, {}).get("masking_default", "PASS")
    return "PASS"


def get_coherence(hexagram_id: int, phase_bits: int) -> float:
    if hexagram_id <= 64:
        base = COHERENCE.get(str(hexagram_id), 0.5)
        # Apply phase damping from resolved vector
        rid = f"{hexagram_id}_{phase_bits}"
        # phase variation: +/- 10% based on phase polarity
        return base
    return 0.5


def encode_ternary_position(wire_a: int, wire_b: int, state: int):
    """Encode ternary digit onto 2 qubits: 0=yin, 1=yao, 2=yang, 3=null/void."""
    if state == 0:
        pass
    elif state == 1:
        qml.RY(np.pi / 2, wires=wire_b)
    elif state == 2:
        qml.RY(np.pi / 2, wires=wire_a)


def apply_mask_gate(wire_a: int, wire_b: int, mask: MaskMode):
    if mask == "MEASURE":
        qml.PauliX(wire_a)
        qml.PauliX(wire_b)
        qml.CNOT(wires=[wire_a, wire_b])
        qml.PauliX(wire_a)
        qml.PauliX(wire_b)
    elif mask == "SEVER":
        pass
    elif mask == "ZERO_ROT":
        qml.RY(0.0, wires=wire_a)
        qml.RY(0.0, wires=wire_b)
    elif mask == "ATTENTION":
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(np.pi / 4, wires=wire_b)
    elif mask == "PASS":
        qml.CNOT(wires=[wire_a, wire_b])
        qml.CRZ(np.pi / 3, wires=[wire_a, wire_b])


def variational_layer(params: np.ndarray, layer_idx: int, n_qubits: int = 12):
    for q in range(n_qubits):
        qml.RX(params[layer_idx, q, 0], wires=q)
        qml.RY(params[layer_idx, q, 1], wires=q)
        qml.RZ(params[layer_idx, q, 2], wires=q)
    for q in range(n_qubits):
        qml.CNOT(wires=[q, (q + 1) % n_qubits])


def build_circuit(
    upper_trigram_id: int,
    lower_trigram_id: int,
    mask: MaskMode,
    coherence: float,
    params: np.ndarray,
    n_layers: int = 4,
):
    dev = qml.device("default.qubit", wires=12)

    @qml.qnode(dev)
    def circuit():
        upper_vector = TRIGRAMS[str(upper_trigram_id)]["vector"]
        lower_vector = TRIGRAMS[str(lower_trigram_id)]["vector"]
        ternary_vector = upper_vector + lower_vector

        for i, state in enumerate(ternary_vector):
            wa, wb = i * 2, i * 2 + 1
            encode_ternary_position(wa, wb, state)
            apply_mask_gate(wa, wb, mask)

        for layer_idx in range(n_layers):
            variational_layer(params, layer_idx)
            for i in range(6):
                wa, wb = i * 2, i * 2 + 1
                apply_mask_gate(wa, wb, mask)

        if coherence < 0.5:
            strength = float(0.5 - coherence)
            for q in range(12):
                if _PENNYLANE_AVAILABLE:
                    qml.DepolarizingChannel(p=strength, wires=q)
                else:
                    qml.BitFlip(p=strength, wires=q)
                    qml.PhaseFlip(p=strength, wires=q)
        return qml.probs(wires=list(range(12)))

    return np.array(circuit())


def marginalize_to_46656(raw_probs: np.ndarray) -> np.ndarray:
    """Map 4096-dimensional probability onto 46,656 resolved states."""
    result = np.zeros(46656)
    for idx in range(4096):
        p = raw_probs[idx]
        if p == 0:
            continue
        digits = []
        valid = True
        for pos in range(6):
            bits = (idx >> (pos * 2)) & 0b11
            if bits == 0b11:
                valid = False
                break
            digits.append(bits)
        if not valid:
            continue
        upper_val = digits[0] + digits[1] * 3 + digits[2] * 9
        lower_val = digits[3] + digits[4] * 3 + digits[5] * 9
        hex_id = upper_val * 27 + lower_val
        if hex_id >= 729:
            continue
        for phase in range(8):
            resolved_idx = hex_id * 8 + phase
            if resolved_idx < 46656:
                result[resolved_idx] += p / 8.0
    total = result.sum()
    if total > 0:
        result /= total
    return result


def _phase_bias_vector(fwhm: float = 2.5) -> np.ndarray:
    """Gaussian future-phase bias over 8 temporal phases.
    
    phase order: past=0, present=1, future=2, transition=3,
                 resolution=4, dissolution=5, crystallization=6, void=7
    Future is index 2. The Gaussian kernel boosts predictive proximity
    to future without zeroing other phases.
    """
    phases = np.arange(8, dtype=float)
    bias = _gaussian_kernel(phases, 2.0, fwhm)
    bias[0] = 0.1  # past: low weight
    bias[1] = 0.3  # present: moderate
    bias[3] = 0.4  # transition: moderate-high
    bias[4] = 0.6  # resolution: high
    bias[5] = 0.5  # dissolution: moderate-high
    bias[6] = 0.7  # crystallization: high
    bias[7] = 0.2  # void: low
    total = bias.sum()
    if total > 0:
        bias /= total
    return bias


def compute_semantic_weights(
    hexagram_id: int,
    phase_bits: int,
    mask: MaskMode,
    coherence: float,
    params: np.ndarray,
    future_fwhm: float = 2.5,
) -> Dict:
    hex_data = HEXAGRAMS.get(str(hexagram_id))
    if hex_data is None:
        return {}

    upper_id = hex_data.get("upper_trigram_id", 0)
    lower_id = hex_data.get("lower_trigram_id", 0)
    raw_probs = np.array(build_circuit(upper_id, lower_id, mask, coherence, params))
    expansion = marginalize_to_46656(raw_probs)

    # Apply future-phase Gaussian bias across 8-phase blocks
    phase_bias = _phase_bias_vector(fwhm=future_fwhm)
    biased = np.zeros_like(expansion)
    for h in range(729):
        start = h * 8
        end = start + 8
        block = expansion[start:end]
        biased[start:end] = block * phase_bias
    biased /= biased.sum() + 1e-12

    top5_idx = np.argsort(biased)[-5:][::-1]
    top5 = [(int(i), float(biased[i])) for i in top5_idx]

    return {
        "hexagram_id": hexagram_id,
        "phase_bits": phase_bits,
        "mask": mask,
        "coherence": coherence,
        "expansion_vector": biased.tolist(),
        "dominant_resolved": int(top5_idx[0]),
        "entropy": float(-np.sum(biased * np.log(biased + 1e-12))),
        "top5_neighbors": top5,
        "paper_count": HEX_COUNTS.get(hexagram_id, 0),
        "future_fwhm": future_fwhm,
        "phase_bias": phase_bias.tolist(),
    }


def run_quantum_expansion():
    np.random.seed(0x47524541)
    n_layers = 4
    params = np.random.uniform(-np.pi, np.pi, (n_layers, 12, 3))

    phases = ["past", "present", "future", "transition", "resolution", "dissolution", "crystallization", "void"]
    enriched = []

    for hex_id in range(729):
        mask = get_mask(hex_id)
        coherence = get_coherence(hex_id, 0)
        hex_data = HEXAGRAMS.get(str(hex_id))
        if hex_data is None:
            continue
        for phase_idx, phase_name in enumerate(phases):
            weights = compute_semantic_weights(hex_id, phase_idx, mask, coherence, params, future_fwhm=2.5)
            if weights:
                weights["phase_temporal"] = phase_name
                enriched.append(weights)

    OUTPUT_CORPUS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CORPUS, "w", encoding="utf-8") as f:
        for record in enriched:
            f.write(json.dumps(record) + "\n")

    print(f"Quantum expansion complete: {len(enriched)} states enriched")
    print(f"Output: {OUTPUT_CORPUS}")
    if enriched:
        entropies = [r["entropy"] for r in enriched]
        coherences = [r["coherence"] for r in enriched]
        future_peaks = [max(r["expansion_vector"][h*8:(h*8+8)]) for r in enriched for h in [r["hexagram_id"]]]
        print(f"Mean entropy: {np.mean(entropies):.4f}")
        print(f"Mean coherence: {np.mean(coherences):.4f}")
        if future_peaks:
            print(f"Future-phase peak probability: {np.mean(future_peaks):.4f}")


if __name__ == "__main__":
    run_quantum_expansion()
