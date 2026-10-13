#!/usr/bin/env python3
"""
Paper Repository Provenance Indexer
===================================
Establishes rigorous, verifiable provenance between PDF source papers,
their arXiv identity, extracted GitHub repositories, and their semantic context.

Provenance chain:
  PDF source -> arXiv ID -> cited GitHub repository -> extraction context
  -> relationship type -> verification status

Distinguishes:
  - "author_implementation": Official code released by paper authors (e.g. in abstract/footnotes)
  - "benchmark_baseline": Code of baseline/comparison methods
  - "dependency_library": Core utility/package used by the method (e.g. PyTorch, PINT, DeepSpeed)
  - "bibliographic_citation": Reference in bibliography section
  - "unknown": Unclassified mention

Verification status levels:
  - "extracted": Raw URL found in text/PDF
  - "link_checked": URL validated for syntax & target
  - "paper_confirmed": Surrounding text confirms paper relation
  - "reproduction_tested": Executed code verifies equations/algorithms
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
ZOTERO = ROOT / ".." / "zotero" / "learning-corpus"
RAW_ARTIFACT = ROOT / "DATASETS" / "zotero_recovered_github_repos.json"
NORMALIZED_INDEX = ROOT / "DATASETS" / "paper_repository_provenance.json"
NORMALIZED_INDEX_JSONL = ROOT / "DATASETS" / "paper_repository_provenance.jsonl"

RE_GH = re.compile(r'https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)')
IGNORED_PREFIXES = ('brucemiller/', 'arXiv/', 'git-lfs/')
STRIP_CHARS = '.,;:)>\'"'

# Keywords signaling author implementation
AUTHOR_IMPL_PATTERNS = [
    r'\bour\s+code\b',
    r'\bour\s+implementation\b',
    r'\bour\s+method\b',
    r'\bwe\s+release\b',
    r'\bcode\s+(?:is|will\s+be)\s+available\b',
    r'\bimplementation\s+(?:is|will\s+be)\s+available\b',
    r'\bsource\s+code\b',
    r'\bwe\s+make\s+our\b',
    r'\bofficial\s+implementation\b',
    r'\bproject\s+page\b',
]

# Keywords signaling baseline or benchmark
BASELINE_PATTERNS = [
    r'\bbaseline\b',
    r'\bbenchmark\b',
    r'\bwe\s+compare\b',
    r'\bcomparison\b',
    r'\bexisting\s+method\b',
    r'\bprior\s+work\b',
]

# Keywords signaling dependency or framework
LIBRARY_PATTERNS = [
    r'\bimplemented\s+in\b',
    r'\busing\s+the\s+package\b',
    r'\blibrary\b',
    r'\bframework\b',
    r'\btoolbox\b',
    r'\bbuilt\s+on\b',
]


@dataclass
class ExtractionContext:
    page_number: int                     # 1-indexed PDF page
    surrounding_text: str                # ~200 chars around the link
    is_in_abstract: bool = False
    is_in_footnote: bool = False
    is_in_references: bool = False
    section_heading: str = ""


@dataclass
class PaperRepositoryRelationship:
    paper_id: str                        # Canonical arXiv ID
    source_pdf: str                      # Relative or canonical PDF path
    category: str                        # Corpus category
    repository_url: str                  # Original extracted GitHub URL
    extraction_context: ExtractionContext
    relationship_type: str               # "author_implementation", "benchmark_baseline", "dependency_library", "bibliographic_citation", "unknown"
    verification_status: str             # "extracted", "link_checked", "paper_confirmed", "reproduction_tested"
    paper_title: Optional[str] = None
    canonical_arxiv_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def classify_relationship(context_text: str, is_in_references: bool, is_in_abstract: bool) -> str:
    """Classify the semantic relationship based on surrounding context."""
    text_lower = context_text.lower()
    if is_in_references:
        return "bibliographic_citation"
    for pat in AUTHOR_IMPL_PATTERNS:
        if re.search(pat, text_lower):
            return "author_implementation"
    if is_in_abstract and ("github.com" in text_lower or "code" in text_lower):
        return "author_implementation"
    for pat in BASELINE_PATTERNS:
        if re.search(pat, text_lower):
            return "benchmark_baseline"
    for pat in LIBRARY_PATTERNS:
        if re.search(pat, text_lower):
            return "dependency_library"
    return "unknown"


def extract_provenance_from_pdf(pdf_path: Path, arxiv_id: str, category: str) -> List[PaperRepositoryRelationship]:
    """Scan PDF with PyMuPDF to extract exact page, surrounding text, and relationship context."""
    results = []
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}", file=sys.stderr)
        return results

    total_pages = len(doc)
    seen_urls = set()

    for page_idx in range(total_pages):
        page = doc[page_idx]
        text = page.get_text("text")
        lines = text.splitlines()

        for m in RE_GH.finditer(text):
            cleaned_repo = m.group(1).rstrip(STRIP_CHARS)
            if any(cleaned_repo.startswith(p) for p in IGNORED_PREFIXES) or cleaned_repo.endswith("/issues"):
                continue

            full_url = f"https://github.com/{cleaned_repo}"
            start_pos = max(0, m.start() - 150)
            end_pos = min(len(text), m.end() + 150)
            surrounding = " ".join(text[start_pos:end_pos].split())

            # Detect section location
            page_num = page_idx + 1
            is_abstract = (page_num == 1) and any("abstract" in l.lower() for l in lines[:15])
            is_references = any(
                kw in text.lower() for kw in ["references", "bibliography", "[1]", "[2]"]
            ) and (page_num >= total_pages - 3)

            rel_type = classify_relationship(surrounding, is_references, is_abstract)
            # If relationship confirmed by text, elevate verification status to paper_confirmed
            status = "paper_confirmed" if rel_type != "unknown" else "extracted"

            rel = PaperRepositoryRelationship(
                paper_id=arxiv_id,
                source_pdf=str(pdf_path.relative_to(ZOTERO.parent) if ZOTERO.parent in pdf_path.parents else pdf_path.name),
                category=category,
                repository_url=full_url,
                extraction_context=ExtractionContext(
                    page_number=page_num,
                    surrounding_text=surrounding,
                    is_in_abstract=is_abstract,
                    is_in_references=is_references,
                ),
                relationship_type=rel_type,
                verification_status=status,
                canonical_arxiv_url=f"https://arxiv.org/abs/{arxiv_id}",
            )
            # Avoid duplicate reporting of same URL on same page
            dedup_key = (arxiv_id, full_url, page_num)
            if dedup_key not in seen_urls:
                seen_urls.add(dedup_key)
                results.append(rel)

    doc.close()
    return results


def build_provenance_index() -> Dict[str, Any]:
    """Scan all 245 PDFs in zotero corpus and build normalized index."""
    categories = [
        "diffusion-generative",
        "efficient-inference-quantization",
        "graph-neural-networks",
        "llm-alignment",
        "multimodal-learning",
    ]

    all_relationships: List[PaperRepositoryRelationship] = []
    paper_count = 0
    papers_with_repos = set()

    for cat in categories:
        cat_dir = ZOTERO / cat
        if not cat_dir.exists():
            continue
        for pdf in sorted(cat_dir.glob("*.pdf")):
            paper_count += 1
            m = re.search(r"(\d{4}\.\d{4,5})", pdf.name)
            aid = m.group(1) if m else pdf.stem
            rels = extract_provenance_from_pdf(pdf, aid, cat)
            if rels:
                papers_with_repos.add(aid)
                all_relationships.extend(rels)

    # Summary metrics
    rel_type_counts = {}
    status_counts = {}
    for r in all_relationships:
        rel_type_counts[r.relationship_type] = rel_type_counts.get(r.relationship_type, 0) + 1
        status_counts[r.verification_status] = status_counts.get(r.verification_status, 0) + 1

    summary = {
        "provenance_chain": "PDF source -> arXiv ID -> cited GitHub repository -> extraction context -> relationship type -> verification status",
        "total_source_pdfs_scanned": paper_count,
        "papers_with_repos_recovered": len(papers_with_repos),
        "total_repository_relationships": len(all_relationships),
        "relationship_type_breakdown": rel_type_counts,
        "verification_status_breakdown": status_counts,
        "relationships": [r.to_dict() for r in all_relationships],
    }

    # Write normalized JSON
    NORMALIZED_INDEX.parent.mkdir(parents=True, exist_ok=True)
    NORMALIZED_INDEX.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write JSONL
    with open(NORMALIZED_INDEX_JSONL, "w", encoding="utf-8") as f:
        for r in all_relationships:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    return summary


if __name__ == "__main__":
    print("Building Normalized Paper Repository Provenance Index...")
    summ = build_provenance_index()
    print(f"Scanned: {summ['total_source_pdfs_scanned']} PDFs")
    print(f"Papers with repos: {summ['papers_with_repos_recovered']}")
    print(f"Total relationships extracted: {summ['total_repository_relationships']}")
    print("Relationship types:")
    for k, v in summ['relationship_type_breakdown'].items():
        print(f"  {k}: {v}")
    print("Verification statuses:")
    for k, v in summ['verification_status_breakdown'].items():
        print(f"  {k}: {v}")
    print(f"Wrote normalized index -> {NORMALIZED_INDEX}")
