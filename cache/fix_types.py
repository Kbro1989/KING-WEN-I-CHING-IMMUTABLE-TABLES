#!/usr/bin/env python3
"""Fix type annotations and None-handling in vision_comparison_pipeline.py."""

from pathlib import Path

path = Path('scripts/vision_comparison_pipeline.py')
content = path.read_text(encoding='utf-8')

# Fix 1: compare_candidate type annotations
old1 = """    def compare_candidate(self, candidate):
        \"\"\"Compare a single candidate against the symbols.zip catalog.
        Returns: comparison dict
        \"\"\"
        paper = candidate.get('paper_id', 'unknown')
        page = candidate.get('page', 0)
        bbox = candidate.get('bbox', {})
        source_text = candidate.get('line_text', '')
        classification = candidate.get('classification', 'unknown')
"""

new1 = """    def compare_candidate(self, candidate: dict) -> dict:
        \"\"\"Compare a single candidate against the symbols.zip catalog.
        Returns: comparison dict
        \"\"\"
        paper: str = candidate.get('paper_id', 'unknown')
        page: int = candidate.get('page', 0)
        bbox: dict = candidate.get('bbox', {})
        source_text: str = candidate.get('line_text', '')
        classification: str = candidate.get('classification', 'unknown')
"""

count1 = content.count(old1)
print(f"compare_candidate occurrences: {count1}")

# Fix 2: run_batch type annotations
old2 = """    def run_batch(self, paper_ids=None, max_per_paper=None):
        \"\"\"Run comparison batch on all positional entries."""
        candidates = self.load_candidates(paper_id=paper_ids)
        if max_per_paper:
            candidates = candidates[:max_per_paper]
"""

new2 = """    def run_batch(self, paper_ids: str | None = None, max_per_paper: int | None = None) -> list[dict]:
        \"\"\"Run comparison batch on all positional entries."""
        candidates: list[dict] = self.load_candidates(paper_id=paper_ids)
        if max_per_paper:
            candidates = candidates[:max_per_paper]
"""

count2 = content.count(old2)
print(f"run_batch occurrences: {count2}")

content = content.replace(old1, new1)
content = content.replace(old2, new2)

path.write_text(content, encoding='utf-8')
print('Done writing file')
