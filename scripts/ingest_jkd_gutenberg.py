#!/usr/bin/env python3
"""Ingest Tao of JKD full text through King Wen consult in batches.

Reads DATASETS/jkd_full_text.txt, cleans obvious OCR artifacts, splits into
sentence-level chunks, and runs each chunk through KingWenEmotionProvider.consult().

Outputs:
  DATASETS/jkd_ingestion_binary.jsonl      # 64-hex expansion per chunk
  DATASETS/jkd_ingestion_ternary.jsonl     # 729-hex expansion per chunk
  DATASETS/jkd_ingestion_summary.json      # aggregate stats
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
    line = re.sub(r"[^\w\s.,;:'\"!?\-—]", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def _load_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    cleaned = [_clean_line(line) for line in lines]
    cleaned = [line for line in cleaned if line]
    return "\n".join(cleaned)


def _chunk_text(text: str, max_chars: int = 800) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    buf = ""
    for sentence in sentences:
        if len(buf) + len(sentence) + 1 > max_chars:
            if buf.strip():
                chunks.append(buf.strip())
            buf = sentence + " "
        else:
            buf += sentence + " "
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


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
                result = provider.consult(chunk, session_id=f"jkd-binary-{idx}", emotional_input=50, ternary=False)
                record = {
                    "batch": idx,
                    "text": chunk,
                    "source": result.get("source"),
                    "winner": result.get("winner"),
                    "all_hexagrams_count": result.get("all_hexagrams_count"),
                    "all_resolved_count": result.get("all_resolved_count"),
                    "expanded_count": len(result.get("expanded", [])),
                    "resolved_count_sample": len(result.get("resolved", [])),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception as exc:
                f.write(json.dumps({"batch": idx, "text": chunk, "error": str(exc)}, ensure_ascii=False) + "\n")


def run_ternary(provider: KingWenEmotionProvider, chunks: list[str], sample_every: int = 25) -> None:
    with TERNARY_OUT.open("w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks, 1):
            if idx % sample_every != 0:
                continue
            try:
                result = provider.consult(chunk, session_id=f"jkd-ternary-{idx}", emotional_input=50, ternary=True)
                record = {
                    "batch": idx,
                    "text": chunk,
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
                f.write(json.dumps({"batch": idx, "text": chunk, "error": str(exc)}, ensure_ascii=False) + "\n")


def summarize(chunks: list[str]) -> None:
    summary = {
        "source": str(TEXT_PATH),
        "total_chunks": len(chunks),
        "binary_output": str(BINARY_OUT),
        "ternary_output": str(TERNARY_OUT),
        "summary_output": str(SUMMARY_OUT),
    }
    if BINARY_OUT.exists():
        lines = BINARY_OUT.read_text(encoding="utf-8").splitlines()
        summary["binary_records"] = len(lines)
    if TERNARY_OUT.exists():
        lines = TERNARY_OUT.read_text(encoding="utf-8").splitlines()
        summary["ternary_records"] = len(lines)
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if not TEXT_PATH.exists():
        raise FileNotFoundError(f"Missing source text: {TEXT_PATH}")
    text = _load_text(TEXT_PATH)
    chunks = _chunk_text(text, max_chars=800)
    provider = _provider()
    run_binary(provider, chunks)
    run_ternary(provider, chunks, sample_every=25)
    summarize(chunks)
    print(f"Chunks: {len(chunks)}")
    print(f"Binary records: {BINARY_OUT}")
    print(f"Ternary records: {TERNARY_OUT}")
    print(f"Summary: {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
