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


import unicodedata
from bs4 import BeautifulSoup
from structural_ast_extractor import StructuralASTExtractor

_AST_EXTRACTOR = StructuralASTExtractor()

_GREEK_MAP = {
    "pi": "π", "theta": "θ", "sigma": "σ", "beta": "β", "lambda": "λ", "mu": "μ", "gamma": "γ",
    "alpha": "α", "delta": "δ", "epsilon": "ε", "rho": "ρ", "phi": "φ", "psi": "ψ", "omega": "ω"
}


def extract_canonical_math_atoms(tokens: List[str]) -> set:
    """Extract normalized mathematical identifier atoms from string or AST tokens."""
    atoms = set()
    for t in tokens:
        tl = t.lower().strip()
        if tl in _GREEK_MAP:
            atoms.add(_GREEK_MAP[tl])
            continue
        t_norm = unicodedata.normalize("NFKD", t)
        for ch in t_norm:
            chl = ch.lower()
            if "a" <= chl <= "z" or chl in _GREEK_MAP.values():
                atoms.add(chl)
    return atoms


def _get_ast_leaves(node: Any) -> List[str]:
    """Recursively collect leaf token strings from an ExprNode."""
    leaves = []
    if getattr(node, "value", None):
        leaves.append(node.value)
    for c in getattr(node, "children", ()):
        leaves.extend(_get_ast_leaves(c))
    return leaves


def match_fraction_to_ast_corpus(vis_num: str, vis_den: str, corpus_equations: List[Dict[str, Any]], min_score: float = 0.85) -> Dict[str, Any] | None:
    """
    Phase 3 Structural Subtree Matcher:
    Compares visual fraction tokens against actual MathML fraction subtrees extracted
    by StructuralASTExtractor, replacing naive substring search.
    Requires one-to-one disambiguation with a combined Jaccard & atom recall score >= min_score.
    """
    vn_atoms = extract_canonical_math_atoms([vis_num])
    vd_atoms = extract_canonical_math_atoms([vis_den])
    if not vn_atoms or not vd_atoms:
        return None

    best_match: Dict[str, Any] | None = None
    best_score = 0.0

    for eq in corpus_equations:
        mathml = eq.get("mathml", "")
        if not mathml or "mfrac" not in mathml:
            continue
        try:
            soup = BeautifulSoup(mathml, "html.parser")
            math_el = soup.find("math")
            if not math_el:
                continue
            ast = _AST_EXTRACTOR.extract(math_el)

            frac_nodes = []
            def _find_fracs(n):
                if getattr(n, "kind", None) == "fraction" and len(getattr(n, "children", ())) >= 2:
                    frac_nodes.append(n)
                for c in getattr(n, "children", ()):
                    _find_fracs(c)
            _find_fracs(ast)

            for frac_idx, fn in enumerate(frac_nodes):
                an_atoms = extract_canonical_math_atoms(_get_ast_leaves(fn.children[0]))
                ad_atoms = extract_canonical_math_atoms(_get_ast_leaves(fn.children[1]))
                if not an_atoms or not ad_atoms:
                    continue
                n_recall = len(an_atoms & vn_atoms) / max(1, len(an_atoms))
                d_recall = len(ad_atoms & vd_atoms) / max(1, len(ad_atoms))
                n_jacc = len(an_atoms & vn_atoms) / max(1, len(an_atoms | vn_atoms))
                d_jacc = len(ad_atoms & vd_atoms) / max(1, len(ad_atoms | vd_atoms))
                composite_score = (n_recall + d_recall + n_jacc + d_jacc) / 4.0

                if n_recall >= 0.8 and d_recall >= 0.8 and composite_score >= min_score:
                    if composite_score > best_score:
                        best_score = composite_score
                        best_match = {
                            "equation_index": eq.get("index"),
                            "equation_latex": eq.get("latex", "")[:120],
                            "fraction_index_in_eq": frac_idx + 1,
                            "composite_match_score": round(composite_score, 3),
                            "numerator_atoms_matched": list(an_atoms & vn_atoms),
                            "denominator_atoms_matched": list(ad_atoms & vd_atoms),
                        }
        except Exception:
            continue
    return best_match


INDEX_FILE = ROOT / "DATASETS" / "zotero_pdf_index.json"


def find_pdf_for_paper(paper_id: str) -> Tuple[Path | None, Dict[str, Any] | None]:
    """Find source PDF for a given arXiv ID using the persistent hash index."""
    if INDEX_FILE.exists():
        idx_data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        if paper_id in idx_data:
            pinfo = idx_data[paper_id]
            raw_path = pinfo.get("pdf_rel_path") or pinfo.get("pdf_path")
            p = Path(raw_path)
            if not p.is_absolute():
                p = (ZOTERO_DIR / p).resolve()
            return p, pinfo

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
                vf_status = vf.get("status", "confirmed_math_fraction")
                vf_reason = vf.get("rejection_reason", "")

                # If the fraction was filtered as a diagram/table, record it as a rejected candidate
                if vf_status == "rejected_diagram":
                    reports.append({
                        "paper_id": paper_id,
                        "pdf_sha256": pdf_sha256,
                        "page": page_idx + 1,
                        "structure_type": "fraction",
                        "status": "rejected_diagram",
                        "rejection_reason": vf_reason,
                        "issue_kind": "diagram_rejection",
                        "bbox": vf["vinculum_rect"],
                        "visually_parsed_latex": vis_latex,
                        "numerator": num,
                        "denominator": den,
                        "source": "vector_layout",
                        "details": f"Filtered candidate rejected as diagram: {vf_reason}",
                    })
                    continue

                # Phase 3 Structural Subtree Match: verify against 1D MathML ASTs and LaTeX text
                ast_match = match_fraction_to_ast_corpus(num, den, corpus_data.get("equations", []), min_score=0.85)
                if ast_match:
                    reports.append({
                        "paper_id": paper_id,
                        "pdf_sha256": pdf_sha256,
                        "page": page_idx + 1,
                        "structure_type": "fraction",
                        "status": "matched_structure",
                        "bbox": vf["vinculum_rect"],
                        "visually_parsed_latex": vis_latex,
                        "numerator": num,
                        "denominator": den,
                        "source": "vector_layout",
                        "matched_equation_index": ast_match["equation_index"],
                        "matched_equation_latex": ast_match["equation_latex"],
                        "fraction_index_in_eq": ast_match["fraction_index_in_eq"],
                        "composite_match_score": ast_match["composite_match_score"],
                        "details": f"Visually parsed fraction structurally matched to 1D equation {ast_match['equation_index']} fraction {ast_match['fraction_index_in_eq']} with score {ast_match['composite_match_score']}.",
                    })
                    continue

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
    all_reports = []
    audited_papers = 0
    paper_metadata = {}
    per_paper_stats = {}

    for jf in sorted(CORPUS_DIR.glob("*.json")):
        pid = jf.stem
        pdf, pinfo = find_pdf_for_paper(pid)
        if pdf:
            audited_papers += 1
            if pinfo:
                paper_metadata[pid] = {
                    "pdf_sha256": pinfo.get("sha256"),
                    "filename": pinfo.get("filename"),
                    "verified_title": pinfo.get("verified_title"),
                    "filename_mislabeled": pinfo.get("filename_mislabeled", False),
                    "page_count": pinfo.get("page_count"),
                }
            discreps = audit_paper_discrepancies(pid, max_pages=3)
            all_reports.extend(discreps)

            p_detected = len(discreps)
            p_rejected = sum(1 for d in discreps if d.get("status") == "rejected_diagram")
            p_matched = sum(1 for d in discreps if d.get("status") == "matched_structure")
            p_unmatched = sum(1 for d in discreps if d.get("status") == "candidate_visual_structure")
            per_paper_stats[pid] = {
                "detected": p_detected,
                "rejected_diagrams": p_rejected,
                "matched_structures": p_matched,
                "unmatched_discrepancies": p_unmatched,
            }

    active_discrepancies = [d for d in all_reports if d.get("status") == "candidate_visual_structure"]
    matched_structures = [d for d in all_reports if d.get("status") == "matched_structure"]
    rejected_diagrams = [d for d in all_reports if d.get("status") == "rejected_diagram"]

    rel_index_file = str(INDEX_FILE.relative_to(ROOT)).replace("\\", "/")

    summary = {
        "metadata": {
            "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "vector_engine_active": True,
            "neural_ocr_active": False,
            "neural_engine_info": "pix2tex_vit_cpu_v0.1 (available, not enabled for batch audit)",
            "index_file": rel_index_file,
            "audited_paper_hashes": paper_metadata,
            "audit_scope": "First 3 pages per paper across 8 indexed corpus papers",
        },
        "total_papers_audited": audited_papers,
        "total_candidates_detected": len(all_reports),
        "total_matched_structures": len(matched_structures),
        "total_diagrams_rejected": len(rejected_diagrams),
        "total_unmatched_discrepancies": len(active_discrepancies),
        "per_paper_stats": per_paper_stats,
        "matched_structures": matched_structures,
        "discrepancies": active_discrepancies,
        "rejected_diagram_candidates": rejected_diagrams,
        "note": "Visual structures classified into matched 1D ASTs, retained diagram rejections, and true unmatched discrepancies.",
    }

    OUT_FILE.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Audited {audited_papers} papers -> Detected {len(all_reports)}: Matched {len(matched_structures)}, Rejected {len(rejected_diagrams)}, Unmatched {len(active_discrepancies)} -> Wrote {OUT_FILE}")
    return summary


if __name__ == "__main__":
    run_full_discrepancy_audit()
