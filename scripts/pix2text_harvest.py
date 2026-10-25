"""Pix2Text candidate harvest for arXiv 1907.04931 page-12 math comparison.

Purpose: non-destructively harvest every FORMULA element and every nested
mathematical embedding from the committed raw Pix2Text outputs
(datatsets/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_output/*.md),
attach spatial provenance from the source rendered page images, match
against the existing parser candidates, and write one JSONL record per
candidate.

This script does NOT modify any existing artifacts.  It adds a new artifact:
datatsets/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl

Run:  cd /c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
      python3.11 scripts/pix2text_harvest.py
"""

import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, ".")

from pix2text.page_elements import Page  # noqa: E402  (only used for eval globals)

# ---------------------------------------------------------------------------
# Safe reconstruction of the Pix2Text `Page` object from its repr dump.
# The committed .md files store repr(Page(...)) which contains:
#   - dict() literals (valid Python)
#   - array(...) calls  (numpy array literals)
#   - PIL.Image reprs (not eval-able)  -- stripped and replaced by {}
#   - unquoted type names (TEXT, TITLE, FORMULA)                     -- quoted
#   - "Element(...)" / "Page(...)" constructors
# ---------------------------------------------------------------------------

class FakeElement:
    """Minimal stand-in for pix2text.page_elements.Element.

    The repr calls Element({...}) with a single positional dict, which the
    real Element.__init__ (keyword-only) rejects.  This stand-in records the
    fields the harvest needs and nothing more.
    """

    def __init__(self, d):
        self.id = d["id"]
        self.box = list(d["box"])
        self.text = d.get("text")
        self.meta = d.get("meta")
        self.type = d["type"]
        self.total_img = d.get("total_img")
        self.isolated = d.get("isolated", False)
        self.col_number = d.get("col_number", -1)
        self.score = d.get("score", 1.0)
        self.spellchecker = None
        self.kwargs = d.get("kwargs", {})

    @property
    def type_str(self):
        return str(self.type)


def _eval_globals():
    """Closed set of names the Page repr may reference."""
    return {
        "array": np.array,
        "Page": Page,
        "np": np,
        "TOTAL_IMG_PLACEHOLDER": {},   # replaces PIL.Image reprs
        "TITLE": "TITLE",
        "Element": FakeElement,
    }


def load_page_object(md_path):
    """Parse a Pix2Text `page_<n>_formulas_<m>_pix2text.md` into a Page.

    Returns the Page on success; on a malformed file (e.g. a page whose OCR
    output could not be serialised back into Python) returns an empty Page
    so that the harvest can continue over the remaining pages.
    """
    raw = open(md_path, encoding="utf-8").read()
    # 1) strip PIL image reprs (they span newlines; use DOTALL)
    raw2 = re.sub(r"<PIL\.Image\.Image.*?>", "TOTAL_IMG_PLACEHOLDER", raw, flags=re.DOTALL)
    # 2) quote unquoted type names
    raw3 = re.sub(r"(?<!\w)TEXT(?!\w)", "'TEXT'", raw2)
    raw3 = re.sub(r"(?<!\w)TITLE(?!\w)", "'TITLE'", raw3)
    raw3 = re.sub(r"(?<!\w)FORMULA(?!\\w)", "'FORMULA'", raw3)
    # eval is safe here: the file is our own artefact, and we only exercise
    # a closed set of builtins plus numpy + the pix2text data classes.
    try:
        obj = eval(raw3, {"__builtins__": {}}, _eval_globals())
    except (SyntaxError, ValueError, NameError, AttributeError) as e:
        # Malformed repr: skip this page rather than abort the whole harvest.
        print(f"WARN: skipped unparseable page {md_path}: {type(e).__name__}: {e}", flush=True)
        obj = Page(id=-1, number=-1, elements=[])
    return obj


# ---------------------------------------------------------------------------
# File / naming helpers
# ---------------------------------------------------------------------------

RENDER_DIR = os.path.join(
    "DATASETS", "PDF_FIDELITY_RENDERINGS", "1907_04931"
)
RENDER_DIR = os.path.abspath(RENDER_DIR)
OUT_PATH = os.path.join(RENDER_DIR, "pix2text_candidates.jsonl")


def image_path_for(pix2text_file):
    """Map 'page_12_formulas_18_pix2text.md' -> 'page_12_formulas_18.png'."""
    base = pix2text_file
    if base.endswith("_pix2text.md"):
        base = base[: -len("_pix2text.md")]
    return base + ".png"


def sha256_file(path):
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Candidate schema (per attachment f7cf5d.txt)
# ---------------------------------------------------------------------------

def make_candidate(pix2text_file, page_obj):
    """Build a candidate dict from one parsed Page object."""
    pdf_page = None
    m = re.match(r"^page_(\d+)_formulas_(\d+)_pix2text\.md$", os.path.basename(pix2text_file))
    if m:
        pdf_page = int(m.group(1))

    records = []
    for idx, el in enumerate(page_obj.elements):
        # element-level transcription
        records.append(_element_record(pix2text_file, idx, el, pdf_page))
        # nested math embeddings (TEXT elements whose meta dicts carry math)
        if el.type == "TEXT" and isinstance(el.meta, list):
            for mi, meta in enumerate(el.meta):
                if isinstance(meta, dict) and meta.get("type") == "embedding":
                    records.append(_embedding_record(pix2text_file, idx, mi, meta, pdf_page))
    return records


def _element_record(pix2text_file, idx, el, pdf_page):
    return {
        "paper_id": "1907.04931",
        "pdf_sha256": None,                     # PDF not present in this repo
        "page_index": pdf_page - 1 if pdf_page else None,  # 0-based
        "pdf_page": pdf_page,
        "render_sha256": None,                  # filled by caller after image path resolved
        "image_path": image_path_for(os.path.basename(pix2text_file)),
        "pix2text_element_id": el.id,
        "element_index": idx,
        "element_type": el.type,
        "bbox_original": list(el.box),
        "raw_ocr": el.text,
        "element_score": el.score,
        "metadata_score": None,
        "parser_match_ids": [],
        "match_status": "UNADJUDICATED",
        "adjudication": None,
        "source_image_sha256": None,  # filled later
    }


def _embedding_record(pix2text_file, el_idx, meta_idx, meta, pdf_page):
    return {
        "paper_id": "1907.04931",
        "pdf_sha256": None,
        "page_index": pdf_page - 1 if pdf_page else None,
        "pdf_page": pdf_page,
        "render_sha256": None,
        "image_path": image_path_for(os.path.basename(pix2text_file)),
        "pix2text_element_id": f"{el_idx}-{meta_idx}",
        "element_index": el_idx,
        "element_type": "TEXT_embedding",
        "bbox_original": None,          # embedded positions differ from parent box
        "raw_ocr": meta.get("text"),
        "element_score": meta.get("score"),
        "metadata_score": None,
        "parser_match_ids": [],
        "match_status": "UNADJUDICATED",
        "adjudication": None,
    }


# ---------------------------------------------------------------------------
# Parser-candidate matching
# ---------------------------------------------------------------------------

CANDIDATE_JSON = os.path.join(
    "DATASETS", "candidates_1907.04931.json"
)
CANDIDATE_JSON = os.path.abspath(CANDIDATE_JSON)


def load_parser_candidates(pdf_page):
    """Return list of (bbox, line_text, record_keys) for one PDF page."""
    candidates = []
    with open(CANDIDATE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        if c.get("page") == pdf_page:
            candidates.append({
                "bbox": [c["bbox"]["x0"], c["bbox"]["y0"],
                         c["bbox"]["x1"], c["bbox"]["y1"]],
                "line_text": c.get("line_text", ""),
                "classification": c.get("classification"),
                "char_count": c.get("char_count"),
            })
    return candidates


def iou(a, b):
    """Intersection-over-union of two [x0,y0,x1,y1] boxes."""
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    return inter / max(1e-9, area_a + area_b - inter)


def containment(a, b):
    """Fraction of parser box covered by candidate box.

    b may be a {'x0','y0','x1','y1'} dict or a [x0,y0,x1,y1] list (as returned
    by load_parser_candidates).
    """
    if isinstance(b, dict):
        x0 = max(a[0], b["x0"]); y0 = max(a[1], b["y0"])
        x1 = min(a[2], b["x1"]); y1 = min(a[3], b["y1"])
        area_b = max(0, b["x1"] - b["x0"]) * max(0, b["y1"] - b["y0"])
    else:
        x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
        x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
        area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    return inter / max(1e-9, area_b)


def match_parser_candidates(candidates, parser_list):
    """Attach parser_match_ids to each candidate (0..n matches allowed)."""
    for cand in candidates:
        if not cand.get("bbox_original"):
            # No spatial bounding box; cannot be matched to parser candidates.
            cand["parser_match_ids"] = []
            continue
        matched = []
        for pc in parser_list:
            # Parser boxes are small regions inside (or overlapping) the
            # element's larger bbox.  Require either:
            #   - containment: parser box is mostly inside the element bbox, or
            #   - IoU: meaningful overlap between the two.
            if containment(cand["bbox_original"], pc["bbox"]) >= 0.3 or iou(
                cand["bbox_original"], pc["bbox"]
            ) >= 0.05:
                matched.append(pc)
        cand["parser_match_ids"] = matched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(RENDER_DIR, exist_ok=True)

    pix2text_files = []
    for root, _dirs, names in os.walk(RENDER_DIR):
        for name in names:
            if name.endswith("_pix2text.md"):
                pix2text_files.append(os.path.join(root, name))
    pix2text_files.sort()

    written = 0
    for pf in pix2text_files:
        page_obj = load_page_object(os.path.join(RENDER_DIR, pf))
        pdf_page = int(re.search(r"^page_(\d+)_", os.path.basename(pf)).group(1))
        render_img = os.path.join(RENDER_DIR, image_path_for(pf))
        render_sha = sha256_file(render_img) if os.path.exists(render_img) else None

        candidates = make_candidate(pf, page_obj)
        parser_candidates = load_parser_candidates(pdf_page)
        match_parser_candidates(candidates, parser_candidates)

        for rec in candidates:
            rec["render_sha256"] = render_sha
            rec["source_image_sha256"] = render_sha
            with open(OUT_PATH, "a", encoding="utf-8") as out:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1

        print(f"{pf}: {len(page_obj.elements)} elements, "
              f"{len(candidates)} candidates, page {pdf_page}, "
              f"parser candidates {len(parser_candidates)}")

    print(f"WROTE {written} records to {OUT_PATH}")


if __name__ == "__main__":
    main()
