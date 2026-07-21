#!/usr/bin/env python3
"""Ingest Tao of JKD full text as paragraph-agnostic scene chunks.

Reads DATASETS/jkd_full_text.txt, cleans obvious OCR artifacts, splits into
paragraph-level scene chunks, and runs ONE King Wen consult pass that emits
scene-level payloads suitable for full POG2 receptive-map pipeline assembly.

Outputs:
  DATASETS/jkd_ingestion_binary.jsonl      # one record per scene chunk
  DATASETS/jkd_ingestion_ternary.jsonl     # sampled record per N chunks
  DATASETS/jkd_ingestion_summary.json      # aggregate movie-level stats
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEXT_PATH = ROOT / "DATASETS" / "jkd_full_text.txt"
BINARY_OUT = ROOT / "DATASETS" / "jkd_ingestion_binary.jsonl"
TERNARY_OUT = ROOT / "DATASETS" / "jkd_ingestion_ternary.jsonl"
SUMMARY_OUT = ROOT / "DATASETS" / "jkd_ingestion_summary.json"

OPENJARVIS_SRC = Path(r"C:/Users/krist/Desktop/OpenJarvis/src")
if OPENJARVIS_SRC.exists():
    sys.path.insert(0, str(OPENJARVIS_SRC))

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from openjarvis.emotion.kingwen import KingWenEmotionProvider  # noqa: E402


def _clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if line.startswith("--- PAGE") or line.startswith("OF ") or re.match(r"^PAGE \d+", line):
        return ""
    line = re.sub(r"[A-Z]{2,}", "", line)
    line = re.sub(r"[0-9]+", "", line)
    line = re.sub(r"[^\w\s.,;:'\"!?\-\—]", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def _load_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    cleaned = [_clean_line(line) for line in lines]
    cleaned = [line for line in cleaned if line]
    return "\n".join(cleaned)


def _chunk_paragraphs(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]
    return [chunk for chunk in chunks if len(chunk) > 40]


def _chunk_sentences(text: str, max_chars: int = 800, overlap: int = 100) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current += sentence + " "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = (current[-overlap:] if overlap > 0 else "") + sentence + " "
    if current.strip():
        chunks.append(current.strip())
    return [chunk for chunk in chunks if len(chunk) > 40]


def _provider() -> KingWenEmotionProvider:
    return KingWenEmotionProvider(
        registry_path=str(ROOT / "data" / "hexagram-registry.json"),
        weights_path=str(ROOT / "data" / "emotional-weights.json"),
        reflections_path=str(ROOT / "data" / "temporal-reflections.json"),
        ternary_module_path=str(ROOT / "kingwen_ternary_tables_complete.py"),
    )


def run_binary(provider: KingWenEmotionProvider, chunks: list[str]) -> None:
    with BINARY_OUT.open("w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks, 1):
            try:
                result = provider.consult(chunk, session_id=f"jkd-scene-{idx}", emotional_input=50, ternary=False)
                record = {
                    "scene_index": idx,
                    "scene_text": chunk,
                    "source": result.get("source"),
                    "all_hexagrams_count": result.get("all_hexagrams_count"),
                    "all_resolved_count": result.get("all_resolved_count"),
                    "expanded_count": len(result.get("expanded", [])),
                    "resolved_count_sample": len(result.get("resolved", [])),
                    "consensus": result.get("consensus", {}),
                    "expanded": result.get("expanded", []),
                    "resolved": result.get("resolved", []),
                    "pipeline_stage_map": {
                        1: {"function": "GutenbergLimb.enable()", "command": "digest_collect", "domain": "listen", "timeout_ms": 5000},
                        2: {"function": "GutenbergLimb.ingestBook(...)", "command": "file_write", "domain": "integrate", "timeout_ms": 30000},
                        3: {"function": "GutenbergLimb.analyzeStyle(bookId)", "command": "think", "domain": "debug", "timeout_ms": 10000},
                        4: {"function": "getSequencedSegments(...)", "command": "shell_exec", "domain": "scaffold", "timeout_ms": 15000},
                        5: {"function": "StoryboardLimbV2.generateScenes(...)", "command": "think", "domain": "design", "timeout_ms": 30000},
                        6: {"function": "ChromanumberEngine.generateVisualSubstrate(...)", "command": "think", "domain": "creative", "timeout_ms": 60000},
                        7: {"function": "VoiceLimb.narrate(...)", "command": "web_search", "domain": "api", "timeout_ms": 45000},
                        8: {"function": "VideoAssemblerLimb.assemble(...)", "command": "shell_exec", "domain": "deploy", "timeout_ms": 120000},
                        9: {"function": "YouTubeLimb.upload(...)", "command": "code_interpreter", "domain": "codegen", "timeout_ms": 60000},
                    },
                    "image_substrate": {
                        "generated": False,
                        "path": None,
                        "status": "pending",
                        "eval_score": None,
                        "eval_passed": False,
                        "redos": 0,
                        "eval_breakdown": {},
                    }
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception as exc:
                f.write(json.dumps({"scene_index": idx, "scene_text": chunk, "error": str(exc)}, ensure_ascii=False) + "\n")


def run_ternary(provider: KingWenEmotionProvider, chunks: list[str], sample_every: int = 25) -> None:
    with TERNARY_OUT.open("w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks, 1):
            if idx % sample_every != 0:
                continue
            try:
                result = provider.consult(chunk, session_id=f"jkd-scene-ternary-{idx}", emotional_input=50, ternary=True)
                record = {
                    "scene_index": idx,
                    "scene_text": chunk,
                    "mode": result.get("mode"),
                    "expanded_count": result.get("expanded_count"),
                    "resolved_count": result.get("resolved_count"),
                    "canonical_count": result.get("canonical_count"),
                    "ternary_count": result.get("ternary_count"),
                    "source": result.get("source"),
                    "canonical_map_entries": len(result.get("canonical_map", {})),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception as exc:
                f.write(json.dumps({"scene_index": idx, "scene_text": chunk, "error": str(exc)}, ensure_ascii=False) + "\n")


def summarize(chunks: list[str], scene_records: list[dict]) -> None:
    summary = {
        "source": str(TEXT_PATH),
        "total_chunks": len(chunks),
        "scene_records": len(scene_records),
        "binary_output": str(BINARY_OUT),
        "ternary_output": str(TERNARY_OUT),
        "summary_output": str(SUMMARY_OUT),
        "pipeline_assembly": "stitch_full_movie_at_end",
        "stage_count": 9,
        "total_stage_timeout_ms": 375000,
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if not TEXT_PATH.exists():
        raise FileNotFoundError(f"Missing source text: {TEXT_PATH}")
    text = _load_text(TEXT_PATH)
    chunks = _chunk_sentences(text)
    if not chunks:
        chunks = _chunk_paragraphs(text)
    provider = _provider()
    run_binary(provider, chunks)
    run_ternary(provider, chunks)
    records = [json.loads(line) for line in BINARY_OUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    summarize(chunks, records)
    print(f"Scenes: {len(chunks)}")
    print(f"Binary records: {BINARY_OUT}")
    print(f"Ternary records: {TERNARY_OUT}")
    print(f"Summary: {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
