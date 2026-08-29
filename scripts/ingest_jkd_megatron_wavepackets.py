#!/usr/bin/env python3
"""
King Wen x JKD Megatron Wavepacket Ingestion Engine
===================================================
Performs gap-aware sliding-window parsing of the entire 'Tao of Jeet Kune Do'
(DATASETS/jkd_full_text.txt) to compute continuous emotion vectors, Hamiltonian
potentials, 6-line ternary pellet states, and acoustic frequency telemetry
across the whole book.

Outputs:
  - DATASETS/jkd_megatron_wavepacket_emotions.jsonl (streaming training dataset)
  - DATASETS/jkd_megatron_manifest.json (summary telemetry & token metrics)

No pseudo-RNG. 100% deterministic mathematical projection.
"""

import json
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kingwen_ternary_tables_complete import HEXAGRAM_BASE, PHASE_INFO

TEXT_PATH = ROOT / "DATASETS" / "jkd_full_text.txt"
OUTPUT_JSONL = ROOT / "DATASETS" / "jkd_megatron_wavepacket_emotions.jsonl"
OUTPUT_MANIFEST = ROOT / "DATASETS" / "jkd_megatron_manifest.json"

# 15-Intent Keyword Vocabulary
INTENT_KEYWORDS = {
    "create":     ["create", "build", "make", "generate", "new", "start", "begin", "initiate", "action"],
    "destroy":    ["destroy", "end", "kill", "stop", "break", "collapse", "remove", "delete", "strike"],
    "transform":  ["transform", "change", "evolve", "morph", "shift", "transition", "become", "fluid"],
    "explore":    ["explore", "discover", "find", "search", "wander", "journey", "seek", "way"],
    "understand": ["understand", "learn", "see", "clarity", "know", "comprehend", "insight", "truth"],
    "feel":       ["feel", "emotion", "love", "fear", "joy", "pain", "heart", "soul", "mind"],
    "speak":      ["speak", "voice", "say", "tell", "express", "communicate", "utter", "form"],
    "listen":     ["listen", "hear", "silence", "quiet", "still", "pause", "receive", "empty"],
    "connect":    ["connect", "join", "unite", "bond", "link", "bridge", "weave", "contact"],
    "protect":    ["protect", "defend", "guard", "secure", "shelter", "preserve", "safe", "stance"],
    "conflict":   ["conflict", "fight", "oppose", "clash", "battle", "resist", "challenge", "opponent"],
    "heal":       ["heal", "repair", "restore", "renew", "mend", "fix", "revive", "recover"],
    "grow":       ["grow", "expand", "increase", "amplify", "scale", "rise", "flourish", "power"],
    "release":    ["release", "free", "surrender", "yield", "open", "flow", "water", "natural"],
    "focus":      ["focus", "concentrate", "center", "aim", "direct", "target", "precision", "speed"],
}

COPRIMES = [97, 89, 83, 79, 73]
COPRIME_BASE_FREQS = [146.0, 158.0, 166.0, 178.0, 194.0, 206.0]

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def clean_and_normalize_text(raw: str) -> str:
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        l = line.strip()
        if not l or l.startswith("--- PAGE") or re.match(r"^PAGE \d+", l) or l.startswith("OF "):
            continue
        cleaned.append(l)
    text = " ".join(cleaned)
    text = re.sub(r"\s+", " ", text)
    return text

def gap_aware_chunking(text: str, window_words: int = 40, stride_words: int = 25) -> list[dict]:
    """
    Sliding window with punctuation-boundary awareness so semantic clauses
    stay intact without breaking mid-sentence.
    """
    words = text.split(" ")
    chunks = []
    n = len(words)
    idx = 0
    chunk_id = 0

    while idx < n:
        end_idx = min(idx + window_words, n)
        # Scan backward for nearest punctuation if not at end
        if end_idx < n:
            for probe in range(end_idx, max(idx + 10, end_idx - 10), -1):
                if words[probe - 1].endswith((".", "!", "?", ";", ":", "—")):
                    end_idx = probe
                    break

        chunk_words = words[idx:end_idx]
        chunk_text = " ".join(chunk_words).strip()

        if len(chunk_text) >= 15:
            chunks.append({
                "chunk_id": chunk_id,
                "start_word_idx": idx,
                "end_word_idx": end_idx,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })
            chunk_id += 1

        idx += stride_words

    return chunks

def compute_emotion_vector(text: str) -> tuple[dict, dict, float, int, int]:
    lower = text.lower()
    tokens = re.findall(r"[a-z0-9]+", lower)
    token_set = set(tokens)

    # 1. Match intent keywords with rank discount
    matched = {}
    for intent, kw_list in INTENT_KEYWORDS.items():
        score = 0.0
        for rank, kw in enumerate(kw_list):
            if kw in token_set:
                score += 1.0 / (rank + 1.0)
        if score > 0:
            matched[intent] = score

    total_score = sum(matched.values())
    intent_simplex = {k: v / total_score for k, v in matched.items()} if total_score > 0 else {}

    # 2. Linear projection W onto 5 emotion axes
    chaos = (intent_simplex.get("conflict", 0.0) * 0.40 +
             intent_simplex.get("destroy", 0.0) * 0.30 +
             intent_simplex.get("transform", 0.0) * 0.20 +
             intent_simplex.get("create", 0.0) * 0.15)

    whimsy = (intent_simplex.get("explore", 0.0) * 0.30 +
              intent_simplex.get("feel", 0.0) * 0.30 +
              intent_simplex.get("heal", 0.0) * 0.20 +
              intent_simplex.get("release", 0.0) * 0.20)

    dark_tone = (intent_simplex.get("destroy", 0.0) * 0.30 +
                 intent_simplex.get("conflict", 0.0) * 0.25 +
                 intent_simplex.get("transform", 0.0) * 0.15)

    coherence = (intent_simplex.get("understand", 0.0) * 0.15 +
                 intent_simplex.get("focus", 0.0) * 0.15 +
                 intent_simplex.get("speak", 0.0) * 0.10 +
                 intent_simplex.get("protect", 0.0) * 0.10)

    voice_weight = (intent_simplex.get("speak", 0.0) * 0.15 +
                    intent_simplex.get("grow", 0.0) * 0.15 +
                    intent_simplex.get("protect", 0.0) * 0.10 +
                    intent_simplex.get("connect", 0.0) * 0.10)

    # 3. Coprime prime hash perturbation (97, 89, 83, 79, 73)
    token_sum = sum(ord(c) for w in token_set for c in w)
    p_chaos = ((token_sum % 97) / 97.0) * 0.12
    p_whimsy = (((token_sum // 7) % 89) / 89.0) * 0.12
    p_dark = (((token_sum // 13) % 83) / 83.0) * 0.12
    p_coh = (((token_sum // 19) % 79) / 79.0) * 0.12
    p_vw = (((token_sum // 23) % 73) / 73.0) * 0.12

    vec = {
        "chaos": round(clamp(0.10 + chaos + p_chaos), 5),
        "whimsy": round(clamp(0.10 + whimsy + p_whimsy), 5),
        "darkTone": round(clamp(0.10 + dark_tone + p_dark), 5),
        "coherence": round(clamp(0.80 + coherence + p_coh), 5),
        "voiceWeight": round(clamp(0.85 + voice_weight + p_vw), 5),
    }

    # 4. Hamiltonian Energy Scalar Functional
    hamiltonian = round(
        vec["coherence"] - vec["chaos"] - 0.5 * vec["darkTone"] + 0.3 * vec["voiceWeight"] - 0.2 * vec["whimsy"], 5
    )

    # 5. Resolve to 9-bit discrete address
    # Best matching hexagram by Euclidean distance to baseline emotional weight
    # Phase determined by coherence & chaos balance
    phase_id = int(clamp(math.floor((1.0 - vec["coherence"]) * 8.0), 0, 7))
    # Hexagram index 1..64 derived deterministically
    hex_id = ((token_sum % 64) + 1)
    addr_9bit = (hex_id - 1) * 8 + phase_id

    return vec, intent_simplex, hamiltonian, hex_id, phase_id

def process_jkd_corpus():
    print("=" * 80)
    print("INGESTING JKD CORPUS INTO MEGAPACKET EMOTIONAL LEARNING DATASET")
    print("=" * 80)

    if not TEXT_PATH.exists():
        raise FileNotFoundError(f"Missing {TEXT_PATH}")

    raw_text = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    clean_text = clean_and_normalize_text(raw_text)
    chunks = gap_aware_chunking(clean_text, window_words=45, stride_words=25)

    print(f"Loaded source text: {len(raw_text)} chars -> Clean: {len(clean_text)} chars")
    print(f"Generated {len(chunks)} gap-aware semantic chunks.\n")

    records = []
    hamiltonian_series = []
    hex_distribution = {}

    t0 = time.perf_counter()

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f_out:
        for chunk in chunks:
            text = chunk["text"]
            vec, intent_simplex, H, hex_id, phase_id = compute_emotion_vector(text)
            base_hex = HEXAGRAM_BASE[hex_id]
            binary_str = base_hex.get("binary_bottom_to_top", "111111")

            u_idx = base_hex.get("upper_idx", 1)
            l_idx = base_hex.get("lower_idx", 1)
            vortex_tension = round((u_idx * l_idx) / 49.0, 4)

            # 6-line ternary pellet states & frequencies
            pellets = []
            for line_idx in range(6):
                bit = int(binary_str[line_idx]) if line_idx < len(binary_str) else 1
                is_changing = (phase_id in [3, 4]) and ((line_idx % 3) == (phase_id % 3))
                ternary_state = 2 if is_changing else (1 if bit == 1 else 0)
                freq = round(COPRIME_BASE_FREQS[line_idx] * (1.18 if ternary_state == 2 else (1.0 if ternary_state == 1 else 0.82)) * (1.0 + vortex_tension * 0.25), 2)
                pellets.append({
                    "line": line_idx + 1,
                    "state": ternary_state,
                    "type": "yang" if ternary_state == 1 else ("yin" if ternary_state == 0 else "yao"),
                    "frequency_hz": freq
                })

            rec = {
                "chunk_id": chunk["chunk_id"],
                "start_word": chunk["start_word_idx"],
                "end_word": chunk["end_word_idx"],
                "prompt": text,
                "emotion_vector": vec,
                "hamiltonian_energy": H,
                "intent_distribution": intent_simplex,
                "resolved_hexagram": {
                    "hexagram_id": hex_id,
                    "name": base_hex["name"],
                    "hanzi": base_hex.get("unicode", "䷀"),
                    "phase_id": phase_id,
                    "phase_name": PHASE_INFO[phase_id]["temporal"],
                    "address_9bit": (hex_id - 1) * 8 + phase_id,
                    "ternary_pellets": pellets,
                    "vortex_tension": vortex_tension
                },
                "megatron_target": {
                    "input_text": text,
                    "target_emotion_vector": [vec["chaos"], vec["whimsy"], vec["darkTone"], vec["coherence"], vec["voiceWeight"]],
                    "target_hamiltonian": H,
                    "target_hex_id": hex_id,
                    "target_phase_id": phase_id,
                    "target_frequencies": [p["frequency_hz"] for p in pellets]
                }
            }

            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
            hamiltonian_series.append(H)
            hex_distribution[hex_id] = hex_distribution.get(hex_id, 0) + 1

    elapsed = time.perf_counter() - t0

    manifest = {
        "corpus_name": "Tao of Jeet Kune Do (Bruce Lee)",
        "source_file": str(TEXT_PATH),
        "total_chunks": len(records),
        "total_words_processed": len(clean_text.split(" ")),
        "generation_time_seconds": round(elapsed, 4),
        "dataset_output_jsonl": str(OUTPUT_JSONL),
        "file_size_bytes": OUTPUT_JSONL.stat().st_size,
        "hamiltonian_stats": {
            "min_energy": min(hamiltonian_series),
            "max_energy": max(hamiltonian_series),
            "mean_energy": round(sum(hamiltonian_series) / len(hamiltonian_series), 5)
        },
        "distinct_hexagrams_covered": len(hex_distribution),
        "all_64_covered": len(hex_distribution) == 64
    }

    OUTPUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Ingested {len(records)} chunks in {elapsed:.3f}s")
    print(f"     Output JSONL: {OUTPUT_JSONL} ({OUTPUT_JSONL.stat().st_size // 1024} KB)")
    print(f"     Manifest:     {OUTPUT_MANIFEST}")
    print(f"     Hamiltonian Range: [{min(hamiltonian_series)} .. {max(hamiltonian_series)}], Mean: {manifest['hamiltonian_stats']['mean_energy']}")
    print(f"     Distinct Hexagrams Addressed: {len(hex_distribution)} / 64")

if __name__ == "__main__":
    process_jkd_corpus()
