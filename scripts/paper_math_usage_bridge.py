#!/usr/bin/env python3
"""Bridge Zotero math-usage artifacts into King Wen pipeline input.

Reads:
  zotero/learning-corpus/paper_frequency_profiles.jsonl
  zotero/learning-corpus/page_precision_math_summary.json
  zotero/learning-corpus/paper-variables-index.json

Writes:
  DATASETS/paper_math_usage.jsonl

One record per paper. Non-mutating; source files are never modified.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZOTERO = ROOT / ".." / "zotero" / "learning-corpus"
FREQ_PATH = ZOTERO / "paper_frequency_profiles.jsonl"
MATH_SUMMARY_PATH = ZOTERO / "page_precision_math_summary.json"
VARIABLES_INDEX_PATH = ZOTERO / "paper-variables-index.json"
OUTPUT_PATH = ROOT / "DATASETS" / "paper_math_usage.jsonl"


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _arxiv_from_file(file_path: str) -> str | None:
    m = re.search(r"(\d{4}\.\d{4,5})", file_path)
    return m.group(1) if m else None


def main() -> int:
    freq = {_arxiv_from_file(r.get("file", "")): r for r in _load_jsonl(FREQ_PATH)}
    variables = {r.get("arxiv"): r for r in json.loads(VARIABLES_INDEX_PATH.read_text(encoding="utf-8"))}
    math_summary = json.loads(MATH_SUMMARY_PATH.read_text(encoding="utf-8"))
    math_key = "page_precision_math_extraction_2026-08-03"
    math_entries = math_summary.get(math_key, {}).get("usable_math_expressions", [])

    # Build per-paper math summary from curated extraction
    math_by_paper: dict[str, list[dict]] = {}
    for entry in math_entries:
        file_path = entry.get("file", "")
        aid = _arxiv_from_file(file_path)
        if aid:
            math_by_paper.setdefault(aid, []).append(entry)

    out = []
    for aid, var in variables.items():
        if not aid:
            continue
        freq_row = freq.get(aid, {})
        math_rows = math_by_paper.get(aid, [])

        record = {
            "arxiv_id": aid,
            "title": var.get("title"),
            "category": var.get("category"),
            "abstract": var.get("abstract", "")[:500],
            "file": var.get("file"),
            "pdf": var.get("pdf"),
            "chars": freq_row.get("chars"),
            "words_total": freq_row.get("words_total"),
            "unique_words": freq_row.get("unique_words"),
            "lexical_density": freq_row.get("lexical_density"),
            "top_words": freq_row.get("top_words", [])[:20],
            "category_signals": freq_row.get("category_signals"),
            "dominant_signal": freq_row.get("dominant_signal"),
            "latex_density": freq_row.get("latex_density"),
            "number_density": freq_row.get("number_density"),
            "symbol_density": freq_row.get("symbol_density"),
            "usable_math_count": len(math_rows),
            "usable_math": math_rows,
        }
        out.append(record)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"wrote {len(out)} records -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
