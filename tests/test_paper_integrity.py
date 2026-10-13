"""
Test Integrity of Zotero PDF Hash Index, Corpus, and Paper Registry.
Ensures titles in the persistent index match the corpus JSON and registry
so that PDF renames or file mix-ups (like 2009.00031 or 2605.06070) are impossible.
"""
import json
import re
from pathlib import Path
import pytest
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / "DATASETS" / "zotero_pdf_index.json"
CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
REGISTRY_FILE = ROOT / "DATASETS" / "paper_registry.json"
ZOTERO_DIR = (ROOT / ".." / "zotero" / "learning-corpus").resolve()


def normalize_title(s: str) -> str:
    """Normalize title for fuzzy comparison across HTML, PDF, and filesystem."""
    return re.sub(r"[^a-zA-Z0-9]", "", s.lower())


def test_zotero_pdf_index_paths_are_relative() -> None:
    """Invariant: index must NEVER store hardcoded user absolute paths."""
    assert INDEX_FILE.exists(), "zotero_pdf_index.json must exist"
    data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    for pid, info in data.items():
        assert "pdf_rel_path" in info, f"Paper {pid} missing pdf_rel_path"
        assert not Path(info["pdf_rel_path"]).is_absolute(), f"Path for {pid} must be relative, got {info['pdf_rel_path']}"
        assert "\\" not in info["pdf_rel_path"], f"Path for {pid} must use forward slashes"


def test_zotero_index_title_matches_corpus_and_pdf_text() -> None:
    """
    Integrity test:
    For every paper in the index:
    1. Corpus title matches registry title
    2. Actual PDF first-page text contains the title from the corpus
    This completely prevents misnamed PDF files from being indexed under wrong IDs.
    """
    assert INDEX_FILE.exists()
    assert REGISTRY_FILE.exists()
    
    idx_data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    reg_data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    for pid, info in idx_data.items():
        corpus_file = CORPUS_DIR / f"{pid}.json"
        assert corpus_file.exists(), f"Corpus file missing for indexed paper {pid}"

        c_data = json.loads(corpus_file.read_text(encoding="utf-8"))
        corpus_title = c_data.get("structure", {}).get("title", "")
        registry_title = reg_data.get(pid, {}).get("title", "")

        norm_corpus = normalize_title(corpus_title)
        norm_registry = normalize_title(registry_title)

        # Invariant 1: Corpus title matches registry title
        assert norm_corpus[:30] == norm_registry[:30], (
            f"Paper {pid} title mismatch: corpus '{corpus_title}' vs registry '{registry_title}'"
        )

        # Invariant 2: PDF actually exists and its first page contains the title
        pdf_path = ZOTERO_DIR / info["pdf_rel_path"]
        assert pdf_path.exists(), f"PDF file not found on disk: {pdf_path}"

        doc = pymupdf.open(pdf_path)
        first_page_text = doc[0].get_text("text")
        doc.close()

        norm_pdf = normalize_title(first_page_text)
        # Check first 25 alphanumeric chars of title exist in the PDF page 0
        assert norm_corpus[:25] in norm_pdf, (
            f"Paper {pid} PDF content mismatch! PDF at {pdf_path} does not contain '{corpus_title}' on page 0."
        )


def test_rejected_diagrams_retained_in_discrepancies_artifact() -> None:
    """
    Invariant: Discrepancy audit must retain filtered diagram candidates with status
    'rejected_diagram' and an explicit rejection reason for human spot-checking.
    """
    disc_file = ROOT / "DATASETS" / "chroma_visual_discrepancies.json"
    assert disc_file.exists()
    data = json.loads(disc_file.read_text(encoding="utf-8"))

    assert "rejected_diagram_candidates" in data, "Rejected diagram candidates must be preserved"
    assert len(data["rejected_diagram_candidates"]) > 0, "Must have retained diagram candidates"
    for item in data["rejected_diagram_candidates"]:
        assert item["status"] == "rejected_diagram"
        assert len(item["rejection_reason"]) > 0
        assert "pdf_sha256" in item
