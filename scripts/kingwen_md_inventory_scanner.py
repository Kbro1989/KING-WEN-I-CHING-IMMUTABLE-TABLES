#!/usr/bin/env python3
"""
King Wen .md inventory scanner.

Finds every .md file under
    C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
reads each file to end (no max-size cap), and prints:
  - absolute path + filename
  - short human summary (first 2-4 lines, cleaned)
  - word count
  - last-modified timestamp
  - embedded YAML/JSON frontmatter hints if any

At the end, appends a single consolidated semantic summary to a log file
    <repo>/docs/kingwen_md_inventory_semantic_summary.txt

Usage:
    python scripts/kingwen_md_inventory_scanner.py
    python scripts/kingwen_md_inventory_scanner.py --log docs/inventory_semantic_summary.txt
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_ROOT = Path(
    r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES"
)
DEFAULT_LOG = Path("docs/kingwen_md_inventory_semantic_summary.txt")

# Patterns used for a quick, zero-token semantic hint
MD_START_HINT = re.compile(r"^#{1,6}\s+", re.MULTILINE)
MD_TITLE = re.compile(r"^#+\s+(.+)$", re.MULTILINE)
MD_LIST = re.compile(r"^\s*[-*+]\s+([^|]+)", re.MULTILINE)
MD_TABLE_ROW = re.compile(r"^\s*[-|]\s*([^|]+)", re.MULTILINE)
MD_CODE_BLOCK = re.compile(r"```", re.MULTILINE)

# ---------------------------------------------------------------------------
# Core scanning
# ---------------------------------------------------------------------------
def find_md_files(root: Path) -> list[Path]:
    """Return every *.md under root, sorted by path."""
    if not root.exists():
        print(f"[ERROR] Root directory not found: {root}", file=sys.stderr)
        sys.exit(1)
    if not root.is_dir():
        print(f"[ERROR] Not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(p for p in root.rglob("*.md") if p.is_file())
    return md_files


def read_md(path: Path) -> str:
    """
    Read a .md file in full.  On Windows a bare `path.read_text()`
    sometimes falls back to the locale encoding (cp1252) and raises a
    UnicodeDecodeError for files that contain non-ASCII bytes (e.g. a
    0x9d byte in a JSON dump).  Use explicit UTF-8 with a fallback to
    errors='replace' so we never fail on a single file.
    """
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # never raise: keep the file in the inventory, show a marker
        return raw.decode("utf-8", errors="replace")


def make_short_summary(text: str, max_lines: int = 4) -> str:
    """
    Build a human-readable, one-line-ish summary from the raw markdown.

    Strategy:
      1. If a top-level heading (H1/H2) exists, use it as the title.
      2. Otherwise pull the first 2-4 non-empty, non-code lines.
      3. Strip markdown emphasis/bullets so the output reads like prose.
    """
    lines = text.splitlines()

    # 1) Look for an H1/H2 heading as the title
    title = ""
    for ln in lines:
        if re.match(r"^#{1,2}\s+", ln):
            title = re.sub(r"^#{1,2}\s+", "", ln).strip()
            break

    # 2) Take the first few "content" lines (skip headings, code fences, blank)
    content_lines = []
    in_code = False
    for ln in lines:
        if MD_CODE_BLOCK.search(ln):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = ln.strip()
        if not stripped:
            continue
        if re.match(r"^#{1,6}\s", stripped):
            continue
        # stop once we have enough lines
        if len(content_lines) >= max_lines:
            break
        # strip list markers / leading pipes
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\|", "", stripped)
        content_lines.append(stripped)

    if title:
        part = f"TITLE: {title}\n"
    else:
        part = "TITLE: (no H1/H2 found)\n"

    if content_lines:
        body = "  ".join(content_lines[:max_lines])
        part += f"SUMMARY: {body}\n"
    else:
        part += "SUMMARY: (no visible content)\n"

    return part


def scan_file(path: Path) -> dict:
    """Read one .md file and return a structured record."""
    text = read_md(path)
    size = path.stat().st_size
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    # Try to detect embedded YAML/JSON frontmatter
    frontmatter = ""
    if text.startswith("---"):
        m = re.match(r"^---(\n.*?\n)---", text, re.DOTALL)
        if m:
            frontmatter = m.group(1).strip()
            # strip it so summaries are not polluted by YAML keys
            text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)

    return {
        "path": str(path),
        "name": path.name,
        "size": size,
        "mtime": mtime.isoformat(),
        "full_text": text,
        "word_count": len(text.split()),
        "line_count": text.count("\n") + 1,
        "frontmatter": frontmatter,
        "summary": make_short_summary(text),
    }


def print_file_report(rec: dict, idx: int, total: int) -> None:
    """Print a single-file report line to the terminal."""
    print("=" * 78)
    print(f"[{idx}/{total}]  {rec['path']}")
    print(f"       size={rec['size']:,} bytes  |  lines={rec['line_count']}  |  words={rec['word_count']}")
    print(f"       modified={rec['mtime']}")
    if rec["frontmatter"]:
        print(f"       frontmatter present ({len(rec['frontmatter'])} chars)")
    print("       " + rec["summary"].replace("\n", "\n       "))
    print()


def build_semantic_summary(records: list[dict], root: Path) -> str:
    """
    Build a consolidated semantic summary suitable for appending to the
    inventory log.  This is deliberately terse and structured so the
    file-side rather than session-time state can be audited.
    """
    now = datetime.now(timezone.utc).isoformat()
    total = len(records)

    # Word-count distribution
    word_counts = [r["word_count"] for r in records]
    size_bytes = [r["size"] for r in records]
    total_words = sum(word_counts)
    total_bytes = sum(size_bytes)

    # Average file size and word count
    avg_words = total_words / total if total else 0
    avg_bytes = total_bytes / total if total else 0

    # File count by depth (relative to root)
    depth_counts = {}
    for r in records:
        try:
            rel = str(Path(r["path"]).relative_to(str(root)))
            depth = len(rel.split(os.sep)) - 1
        except ValueError:
            depth = 0
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    lines = []
    lines.append("=" * 78)
    lines.append("KING WEN .md INVENTORY — TERMFlINE SUMMARY (2>&1)")
    lines.append(f"Generated at (UTC): {now}")
    lines.append(f"Root:  {root}")
    lines.append(f"Total .md files: {total}")
    lines.append(f"Total words: {total_words:,}")
    lines.append(f"Average words/file: {avg_words:.0f}")
    lines.append(f"Total bytes: {total_bytes:,}")
    lines.append(f"Average bytes/file: {avg_bytes:.0f}")

    lines.append("")
    lines.append("--- DISTRIBUTION BY DIRECTORY DEPTH ---")
    lines.append("  Depth definition: depth 0 = files in repo root; depth N = N parent-directory levels below root.")
    lines.append(f"  Observed depth tiers ({len(depth_counts)}): " + ", ".join(f"depth {d}" for d in sorted(depth_counts)))
    for depth in sorted(depth_counts):
        lines.append(f"  depth {depth}: {depth_counts[depth]} files")
    lines.append("")

    lines.append("--- TOP HEADINGS (first H1/H2 per file) ---")
    for r in records:
        title = r["summary"].split("TITLE: ", 1)[-1] if "TITLE: " in r["summary"] else "(none)"
        lines.append(f"  {r['path']}")
        lines.append(f"    {title}")
    lines.append("")

    lines.append("--- SUPPORTED ANATOMY (last-modified oldest first) ---")
    sorted_by_mtime = sorted(records, key=lambda x: x["mtime"])
    for r in sorted_by_mtime:
        lines.append(f"  {r['mtime']}  {r['path']}")
    lines.append("")

    lines.append("=" * 78)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan KING-WEN-I-CHING-IMMUTABLE-TABLES for .md files and print a terminal summary."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Root directory to scan (default: %(default)s)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Append semantic summary to this file (default: %(default)s)",
    )
    args = parser.parse_args()

    global root_depth
    root_depth = len(args.root.parts)

    md_files = find_md_files(args.root)
    print(f"Found {len(md_files)} .md files under {args.root}\n")

    records = []
    for idx, p in enumerate(md_files, 1):
        rec = scan_file(p)
        records.append(rec)
        print_file_report(rec, idx, len(md_files))

    # Build and print the semantic summary
    semantic = build_semantic_summary(records, args.root)
    print(semantic)

    # Append semantic summary to the log file (if requested)
    log_path = args.log
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Scan run at {datetime.now(timezone.utc).isoformat()} ---\n")
            f.write(semantic)
        print(f"\nSemantic summary appended to: {log_path}")


if __name__ == "__main__":
    main()
