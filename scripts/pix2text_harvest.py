"""Pix2Text candidate harvest for arXiv 1907.04931 page-12 math comparison.

Purpose: non-destructively harvest every FORMULA element and every nested
mathematical embedding from the committed raw Pix2Text outputs
(DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_output/*.md),
attach spatial provenance from the source rendered page images, match
against the existing parser candidates, and write one JSONL record per
candidate.

This script does NOT modify any existing artifacts.  It adds a new artifact:
DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl

Run:  cd /c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
      python3.11 scripts/pix2text_harvest.py
"""

import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, ".")

from pix2text.page_elements import Page  # noqa: E402  (only used for eval globals)

# ---------------------------------------------------------------------------
# Safe reconstruction of the Pix2Text `Page` object from its repr dump.
# ---------------------------------------------------------------------------


class FakeElement:
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
    return {
        "array": np.array,
        "Page": Page,
        "np": np,
        "TOTAL_IMG_PLACEHOLDER": {},
        "TITLE": "TITLE",
        "Element": FakeElement,
    }


def _scan_element_blocks(raw):
    blocks = []
    pos = 0
    while True:
        start = raw.find("Element({", pos)
        if start == -1:
            break
        open_idx = start + len("Element({")
        end = _balanced_end(raw, open_idx)
        if end is None:
            break
        block = raw[open_idx:end]
        mini = _parse_element_dict(block)
        if mini is not None:
            blocks.append(mini)
        pos = end + 1
    return blocks


def _balanced_end(s, open_idx):
    depth = 0
    i = open_idx
    while i < len(s):
        ch = s[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


def _parse_element_dict(block):
    import json as _json

    try:
        raw = block.strip()
        raw = re.sub(r",\s*([\]}])", r"\1", raw)
        raw = raw.replace("'", '"')
        data = _json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return {
        "id": data.get("id", ""),
        "box": data.get("box"),
        "text": data.get("text"),
        "type": data.get("type", "TEXT"),
        "score": data.get("score", 1.0),
    }


def load_page_object(md_path):
    raw = open(md_path, encoding="utf-8").read()
    raw2 = re.sub(r"<PIL\.Image\.Image.*?>", "TOTAL_IMG_PLACEHOLDER", raw, flags=re.DOTALL)
    raw3 = re.sub(r"(?<!\w)TEXT(?!\w)", "'TEXT'", raw2)
    raw3 = re.sub(r"(?<!\w)TITLE(?!\w)", "'TITLE'", raw3)
    raw3 = re.sub(r"(?<!\w)FORMULA(?!\\w)", "'FORMULA'", raw3)
    try:
        obj = eval(raw3, {"__builtins__": {}}, _eval_globals())
        if obj is None:
            raise ValueError("eval returned None")
        return obj
    except (SyntaxError, ValueError, NameError, AttributeError):
        blocks = _scan_element_blocks(raw)
        if blocks:
            return Page(id=-1, number=-1, elements=blocks)
        return Page(id=-1, number=-1, elements=[])


RENDER_DIR = os.path.abspath(os.path.join(
    "DATASETS", "PDF_FIDELITY_RENDERINGS", "1907_04931"
))
OUT_PATH = os.path.join(RENDER_DIR, "pix2text_candidates.jsonl")


def image_path_for(pix2text_file):
    base = pix2text_file
    if base.endswith("_pix2text.md"):
        base = base[: -len("_pix2text.md")]
    return base + ".png"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_rev_parse(path="."):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def _extract_math_keywords(text):
    if not text:
        return False
    low = text.lower()
    markers = [
        "\\", "frac", "sum", "prod", "int", "sqrt", "alpha", "beta", "gamma",
        "delta", "theta", "lambda", "mu", "pi", "sigma", "phi", "psi", "omega",
        "mathbb", "mathbf", "mathit", "operatorname", "begin", "end",
        "\\left", "\\right", "\\sum", "\\prod", "\\int", "\\sqrt",
    ]
    return any(m in low for m in markers)


def classify_candidate(el, text):
    """Return a `candidate_class` string for one Element or a raw text block.

    Classes: DISPLAY_EQUATION, INLINE_MATH, TEXT, PROSE, TITLE, UNPARSEABLE
    """
    # FakeElement objects expose attributes; real pix2text elements are dicts.
    if el is None:
        return "PROSE"
    if isinstance(el, dict):
        el_type = el.get("type", "TEXT")
        el_text = el.get("text")
    else:
        el_type = el.type
        el_text = el.text
    t = (el_text or "") if isinstance(el, dict) else str(el_text)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return "PROSE"
    if el_type == "FORMULA":
        return "DISPLAY_EQUATION"
    if el_type == "TITLE":
        return "TITLE"
    if _extract_math_keywords(t):
        return "INLINE_MATH"
    return "PROSE"


def _math_tokens(text):
    """Extract math-relevant tokens (commands, symbols, numbers) from text."""
    t = re.sub(r"\s+", " ", str(text or "")).lower()
    tokens = set()
    for tok in re.findall(r"[a-z]+|[0-9]+\.?[0-9]*|\.{3}", t):
        tok = tok.strip()
        if tok and tok not in {"a", "an", "the", "and", "or", "of", "to", "in", "on", "is", "it", "with"}:
            tokens.add(tok)
    return tokens


def _token_jaccard(a, b):
    """Jaccard similarity between two token sets."""
    sa, sb = _math_tokens(a), _math_tokens(b)
    if not sa and not sb:
        return 1.0
    union = sa | sb
    if not union:
        return 0.0
    return len(sa & sb) / len(union)


def _text_match(ocr_text, parser_line_text, threshold=0.5):
    """Return True if normalized math content agrees (TEXT_MATCH)."""
    jac = _token_jaccard(ocr_text, parser_line_text)
    return jac >= threshold and (_math_tokens(ocr_text) & _math_tokens(parser_line_text))


def _crop_nonblank(image_path, bbox, margin=0.05):
    """Crop the source image at bbox and verify non-blank content.

    Returns True if the crop contains meaningful pixel variance (not blank
    or fully saturated).  This is a lightweight visual-integrity gate used
    to promote records toward VISUALLY_VERIFIED.
    """
    try:
        from PIL import Image
        img = Image.open(image_path).convert("L")
        w, h = img.size
        x0 = max(0, int(bbox[0] * w))
        y0 = max(0, int(bbox[1] * h))
        x1 = min(w, int(bbox[2] * w))
        y1 = min(h, int(bbox[3] * h))
        crop = img.crop((x0, y0, x1, y1))
        hist = crop.histogram()
        total = sum(hist)
        if total == 0:
            return False
        dark = sum(hist[:128])
        bright = sum(hist[128:])
        return (dark > total * 0.01 and bright > total * 0.01)
    except Exception:
        return False


def _match_status(rec, parser_candidates, pdf_page):
    """Compute the base match status from spatial + text evidence.

    Returns one of: UNADJUDICATED, SPATIAL_MATCH, TEXT_MATCH, VISUALLY_VERIFIED
    The adjudication layer (ADJUDICATED) is applied separately by
    adjudicate_candidates.py; it never runs during harvesting.
    """
    if rec.get("parser_match_ids"):
        return "SPATIAL_MATCH"
    for pc in parser_candidates:
        if pc.get("bbox") and _text_match(rec.get("raw_ocr") or "", pc.get("line_text") or ""):
            return "TEXT_MATCH"
    render_img = os.path.join(
        RENDER_DIR, image_path_for(rec.get("_pix2text_file", ""))
    )
    if rec.get("bbox_original") and os.path.exists(render_img):
        if _crop_nonblank(render_img, rec["bbox_original"]):
            return "VISUALLY_VERIFIED"
    return "UNADJUDICATED"


def _jsonable(obj):
    """Convert numpy-ish objects to native Python JSON-serializable types."""
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def _element_record(pix2text_file, idx, el, pdf_page):
    # FakeElement objects expose attributes; real pix2text elements are dicts.
    if isinstance(el, dict):
        el_id = el.get("id", f"el-{idx}")
        el_box = el.get("box")
        el_text = el.get("text")
        el_type = el.get("type", "TEXT")
        el_score = el.get("score", 1.0)
    else:
        el_id = el.id
        el_box = el.box
        el_text = el.text
        el_type = el.type
        el_score = el.score
    return {
        "_pix2text_file": pix2text_file,
        "paper_id": "1907.04931",
        "pdf_sha256": None,
        "page_index": pdf_page - 1 if pdf_page else None,
        "pdf_page": pdf_page,
        "render_sha256": None,
        "image_path": image_path_for(os.path.basename(pix2text_file)),
        "pix2text_element_id": el_id,
        "element_index": idx,
        "element_type": el_type,
        "bbox_original": list(el_box or []),
        "raw_ocr": el_text,
        "element_score": el_score,
        "metadata_score": None,
        "parser_match_ids": [],
        "match_status": "UNADJUDICATED",
        "adjudication": None,
        "candidate_class": classify_candidate(el, el_text),
        "parse_error": None,
    }


def _embedding_record(pix2text_file, el_idx, meta_idx, meta, pdf_page):
    return {
        "_pix2text_file": pix2text_file,
        "paper_id": "1907.04931",
        "pdf_sha256": None,
        "page_index": pdf_page - 1 if pdf_page else None,
        "pdf_page": pdf_page,
        "render_sha256": None,
        "image_path": image_path_for(os.path.basename(pix2text_file)),
        "pix2text_element_id": f"{el_idx}-{meta_idx}",
        "element_index": el_idx,
        "element_type": "TEXT_embedding",
        "bbox_original": None,
        "raw_ocr": meta.get("text"),
        "element_score": meta.get("score"),
        "metadata_score": None,
        "parser_match_ids": [],
        "match_status": "UNADJUDICATED",
        "adjudication": None,
        "candidate_class": "INLINE_MATH",
        "parse_error": None,
    }


def make_candidate(pix2text_file, page_obj, pdf_page):
    records = []
    for idx, el in enumerate(page_obj.elements):
        records.append(_jsonable(_element_record(pix2text_file, idx, el, pdf_page)))
        if el.type == "TEXT" and isinstance(el.meta, list):
            for mi, meta in enumerate(el.meta):
                if isinstance(meta, dict) and meta.get("type") == "embedding":
                    records.append(_jsonable(_embedding_record(pix2text_file, idx, mi, meta, pdf_page)))
    return records


def make_candidate_from_text(pix2text_file, pdf_page, raw):
    records = []
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        records.append(_jsonable({
            "paper_id": "1907.04931",
            "pdf_sha256": None,
            "page_index": pdf_page - 1 if pdf_page else None,
            "pdf_page": pdf_page,
            "render_sha256": None,
            "image_path": image_path_for(os.path.basename(pix2text_file)),
            "pix2text_element_id": f"raw-line-{i}",
            "element_index": None,
            "element_type": "TEXT",
            "bbox_original": None,
            "raw_ocr": line,
            "element_score": None,
            "metadata_score": None,
            "parser_match_ids": [],
            "match_status": "UNADJUDICATED",
            "adjudication": None,
            "candidate_class": classify_candidate(None, line),
            "parse_error": "raw_ocr_only: no Element blocks found",
        }))
    return records


def load_parser_candidates(pdf_page):
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


CANDIDATE_JSON = os.path.abspath(os.path.join(
    "DATASETS", "candidates_1907.04931.json"
))


def iou(a, b):
    x0 = max(a[0], b[0]); y0 = max(a[1], b[1])
    x1 = min(a[2], b[2]); y1 = min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    return inter / max(1e-9, area_a + area_b - inter)


def containment(a, b):
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
    for cand in candidates:
        if not cand.get("bbox_original"):
            cand["parser_match_ids"] = []
            continue
        matched = []
        for pc in parser_list:
            if containment(cand["bbox_original"], pc["bbox"]) >= 0.3 or iou(
                cand["bbox_original"], pc["bbox"]
            ) >= 0.05:
                matched.append(pc)
        cand["parser_match_ids"] = matched


def main():
    os.makedirs(RENDER_DIR, exist_ok=True)

    git_sha = git_rev_parse()
    pix2text_version = "unknown"
    try:
        from pix2text import __version__ as _pv
        # __version__ may be the module itself on some pix2text installs.
        if isinstance(_pv, str):
            pix2text_version = _pv
        elif hasattr(_pv, "__version__"):
            pix2text_version = _pv.__version__
        else:
            pix2text_version = str(_pv)
    except Exception:
        pass

    pix2text_files = []
    for root, _dirs, names in os.walk(RENDER_DIR):
        for name in names:
            if name.endswith("_pix2text.md"):
                pix2text_files.append(os.path.join(root, name))
    pix2text_files.sort()

    written = 0
    for pf in pix2text_files:
        _m = re.search(r"^page_(\d+)_", os.path.basename(pf))
        if _m is None:
            raise ValueError(f"cannot parse page number from {pf!r}")
        pdf_page = int(_m.group(1))
        input_sha = sha256_file(pf)
        render_img = os.path.join(RENDER_DIR, image_path_for(pf))
        render_sha = sha256_file(render_img) if os.path.exists(render_img) else None

        page_obj = load_page_object(pf)

        candidates = []
        if page_obj.elements:
            candidates = make_candidate(pf, page_obj, pdf_page)
        else:
            raw = open(pf, encoding="utf-8", errors="replace").read()
            candidates = make_candidate_from_text(pf, pdf_page, raw)

        parser_candidates = load_parser_candidates(pdf_page)
        match_parser_candidates(candidates, parser_candidates)

        for rec in candidates:
            rec["render_sha256"] = render_sha
            rec["source_image_sha256"] = render_sha
            rec["pix2text_version"] = pix2text_version
            rec["input_sha256"] = input_sha
            rec["harvest_script_sha256"] = git_sha
            rec["harvest_script_version"] = "pix2text-harvest 0.2.0"
            # Base match status from spatial + text evidence (adjudication
            # layer adds ADJUDICATED; that layer runs separately).
            rec["match_status"] = _match_status(rec, parser_candidates, pdf_page)
            out_rec = _jsonable(rec)
            with open(OUT_PATH, "a", encoding="utf-8") as out:
                out.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
                written += 1

        print(f"{os.path.basename(pf)}: "
              f"{len(page_obj.elements)} elements, "
              f"{len(candidates)} candidates, page {pdf_page}, "
              f"parser candidates {len(parser_candidates)}")

    print(f"WROTE {written} records to {OUT_PATH}")


if __name__ == "__main__":
    main()
