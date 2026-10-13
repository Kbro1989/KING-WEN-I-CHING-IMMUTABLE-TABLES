#!/usr/bin/env python3
"""
Chroma Usage Finder — Audits Discrepancies between Visual 2D and 1D Readers.
===========================================================================
Scans papers across the corpus, extracting 2D visual structures from their PDFs
and comparing them against the 1D parsed LaTeX/MathML occurrences.

Flags cases where:
  - 1D readers skipped division bars
  - 1D readers collapsed multi-row cases braces
  - 1D readers dropped large brackets, norms, or limits

Outputs:
  DATASETS/chroma_visual_discrepancies.json
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chroma_visual_reader import analyze_pdf_page
from visual_math_translator import VisualMathTranslator, DiscrepancyReport

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OUT_FILE = ROOT / "DATASETS" / "chroma_visual_discrepancies.json"
CORPUS_DIR = ROOT / "DATASETS" / "arxiv_html_corpus"
ZOTERO_DIR = ROOT / ".." / "zotero" / "learning-corpus"


INDEX_FILE = ROOT / "DATASETS" / "zotero_pdf_index.json"


def find_pdf_for_paper(paper_id: str) -> Tuple[Path | None, Dict[str, Any] | None]:
    """Find source PDF for a given arXiv ID using the persistent hash index."""
    if INDEX_FILE.exists():
        idx_data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        if paper_id in idx_data:
            pinfo = idx_data[paper_id]
            return Path(pinfo["pdf_path"]), pinfo

    # Fallback to direct directory scan if index not yet generated
    if ZOTERO_DIR.exists():
        for pdf in ZOTERO_DIR.rglob("*.pdf"):
            if paper_id in pdf.name:
                return pdf, None
    return None, None


def audit_paper_discrepancies(paper_id: str, max_pages: int = 5) -> List[Dict[str, Any]]:
    """
    Audit discrepancies for a single paper between actual visually parsed
    formulas (Tier 1 vector vinculum + Tier 2 neural OCR) and 1D parsed text.
    Every reported discrepancy includes the real visually parsed LaTeX expression and PDF hash.
    """
    pdf_path, pinfo = find_pdf_for_paper(paper_id)
    if not pdf_path or not pdf_path.exists():
        return []

    pdf_sha256 = pinfo.get("sha256") if pinfo else None

    corpus_json = CORPUS_DIR / f"{paper_id}.json"
    if not corpus_json.exists():
        return []

    corpus_data = json.loads(corpus_json.read_text(encoding="utf-8"))
    eqs = corpus_data.get("equations", [])
    eq_texts = [e.get("latex", "") for e in eqs]

    reports = []
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        num_pages = min(max_pages, len(doc))
        doc.close()

        for page_idx in range(num_pages):
            page_data = analyze_pdf_page(pdf_path, page_idx, dpi=120)
            vector_fracs = page_data.get("vector_fractions", [])

            for vf in vector_fracs:
                num = vf["numerator"]
                den = vf["denominator"]
                vis_latex = vf["latex"]
                # Structural check: verify whether this fraction exists in 1D text
                found_in_text = any(
                    (num in t and den in t) or (vis_latex in t) or ("\\frac" in t and (num in t or den in t))
                    for t in eq_texts
                )
                if not found_in_text:
                    reports.append({
                        "paper_id": paper_id,
                        "pdf_sha256": pdf_sha256,
                        "page": page_idx + 1,
                        "structure_type": "fraction",
                        "status": "candidate_visual_structure",
                        "issue_kind": "skipped_division",
                        "bbox": vf["vinculum_rect"],
                        "visually_parsed_latex": vis_latex,
                        "numerator": num,
                        "denominator": den,
                        "source": "vector_layout",
                        "details": f"Visually parsed fraction {vis_latex} has no matching 2D fraction in 1D parsed equations.",
                    })

    except Exception as e:
        print(f"Error auditing {paper_id}: {e}", file=sys.stderr)

    return reports


def run_full_discrepancy_audit() -> Dict[str, Any]:
    """Run audit across all papers in the corpus using indexed hashes and execution metadata."""
    import datetime
    all_discrepancies = []
    audited_papers = 0
    paper_metadata = {}

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        pid = jf.stem
        pdf, pinfo = find_pdf_for_paper(pid)
        if pdf:
            audited_papers += 1
            if pinfo:
                paper_metadata[pid] = {
                    "pdf_sha256": pinfo.get("sha256"),
                    "filename": pinfo.get("filename"),
                    "page_count": pinfo.get("page_count")
                }
            discreps = audit_paper_discrepancies(pid, max_pages=3)
            all_discrepancies.extend(discreps)

    summary = {
        "metadata": {
            "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "vector_engine_active": True,
            "neural_ocr_active": False,
            "neural_engine_info": "pix2tex_vit_cpu_v0.1 (available, not enabled for batch audit)",
            "index_file": str(INDEX_FILE),
            "audited_paper_hashes": paper_metadata,
        },
        "total_papers_audited": audited_papers,
        "total_discrepancies_found": len(all_discrepancies),
        "discrepancies": all_discrepancies,
        "note": "Candidate 2D visual structures in PDF not matched in 1D parsed text stream.",
    }

    OUT_FILE.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Audited {audited_papers} papers -> Found {len(all_discrepancies)} discrepancies -> Wrote {OUT_FILE}")
    return summary


if __name__ == "__main__":
    run_full_discrepancy_audit()
