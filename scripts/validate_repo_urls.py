#!/usr/bin/env python3
"""
Validate repository URLs in the provenance file and mark incomplete ones.

PROBLEM
=======
The external audit found truncated URLs like:
  gusye1234/pytorch-
  mubertai/mubert-text-to-
  alembics/disco-
  automatic1111/stable-
  EkkoXiao/Bio-

These are incomplete paths that end with a hyphen (truncated name).
They must be flagged as INVALID_OR_INCOMPLETE — not silently guessed at.

VALIDATION RULES
================
  1. Must be a valid URL (has scheme + netloc)
  2. GitHub URLs must have at least 2 path segments (owner/repo)
  3. Must not end with a hyphen or other truncation indicator
  4. Must not contain whitespace or obvious corruption

OUTPUT
======
DATASETS/paper_repository_provenance_validated.jsonl
  - same records as input, plus:
    - url_valid: bool
    - url_issue: str | null (description of the problem)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "DATASETS" / "paper_repository_provenance.jsonl"
OUT = ROOT / "DATASETS" / "paper_repository_provenance_validated.jsonl"

TRUNCATION_INDICATORS = re.compile(r"[-_]$")


def validate_url(url: str) -> tuple[bool, str | None]:
    """Validate a repository URL. Returns (is_valid, issue_description)."""
    if not url or not url.strip():
        return False, "empty URL"

    url = url.strip()

    # Check for whitespace inside the URL (corruption indicator)
    if re.search(r"\s", url):
        return False, f"contains whitespace: {url!r}"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"parse error: {e}"

    if not parsed.scheme:
        return False, f"no scheme: {url!r}"

    if not parsed.netloc:
        return False, f"no netloc: {url!r}"

    # GitHub-specific: need at least owner/repo
    if "github.com" in parsed.netloc:
        path_parts = [p for p in parsed.path.split("/") if p]
        if len(path_parts) < 2:
            return False, f"GitHub URL missing repo name: {url!r}"

        # Check for truncation indicators on the repo name
        repo_name = path_parts[1]
        if TRUNCATION_INDICATORS.search(repo_name):
            return False, f"repo name appears truncated (ends with hyphen/underscore): {url!r}"

    # Check for truncation indicators on any path segment
    path_parts = [p for p in parsed.path.split("/") if p]
    for part in path_parts:
        if TRUNCATION_INDICATORS.search(part):
            return False, f"path segment appears truncated: {url!r}"

    return True, None


def main() -> int:
    records = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]

    valid_count = 0
    invalid_count = 0
    issues = []

    for r in records:
        url = r.get("repository_url", "")
        is_valid, issue = validate_url(url)

        r["url_valid"] = is_valid
        r["url_issue"] = issue

        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            issues.append({"paper_id": r.get("paper_id"), "url": url, "issue": issue})

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )

    print(f"total records: {len(records)}")
    print(f"  valid:   {valid_count}")
    print(f"  invalid: {invalid_count}")
    if issues:
        print("\ninvalid URLs:")
        for x in issues:
            print(f"  {x['paper_id']}: {x['issue']}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
