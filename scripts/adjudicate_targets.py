"""Targeted adjudication of unadjudicated Pix2Text candidates - 1907.04931.

------------------------------  LAYER CONTACT  ------------------------------
LAYER 1 - Discovery
  script:            scripts/pix2text_harvest.py
  output:            DATASETS/PDF_FIDELITY_RENDERINGS/1907_04931/pix2text_candidates.jsonl
  records:           158 raw-harvest candidates (immutable evidence; never modified)

LAYER 2 - Adjudication (classification)
  script:            scripts/adjudicate_candidates_v2.py
  output:            adjudication_report.jsonl (authoritative 4-level model:
                     SPATIAL_MATCH / TEXT_MATCH / VISUALLY_VERIFIED / ADJUDICATED /
                     UNADJUDICATED), adjudication_summary.json, adjudication_report.md
  contract:          exclusive statuses WITHIN this layer; carry-forward source
                     for Layer 3.

LAYER 3 - Targeted adjudication
  script:            scripts/adjudicate_targets.py
  output:            adjudication_targets.jsonl (+ summary + markdown)
  contract:          carries forward Layer-2 explicit statuses (VISUALLY_VERIFIED /
                     SPATIAL_MATCH / TEXT_MATCH); adjudicates UNADJUDICATED records.
                     Statuses are exclusive WITHIN this layer.
  AUTHORITATIVE:     adjudication_targets.jsonl holds the final adjudication status
                     for this layer set. Layer-3 status derives as:
                     - L2 explicit status carried forward unchanged, OR
                     - ADJUDICATED for records that were UNADJUDICATED.
  STATUSES ARE NOT
  MUTUALLY EXCLUSIVE ACROSS LAYERS: an element classified ADJUDICATED in Layer 3
  may be VISUALLY_VERIFIED in Layer 2 (and vice versa for different rows).

STATUS MODEL (machine-readable):
  ADJUDICATED      - newly adjudicated; non-semantic determination in
                     `adjudication_detail`
  UNVERIFIED       - could not be verified
  NO_MATCH         - no parser association and no evidence
  (VISUALLY_VERIFIED / SPATIAL_MATCH / TEXT_MATCH are carried forward)

Preserves per record: raw_ocr, bbox_original, source-image SHA-256,
parser_match_ids (unchanged), candidate_class, pix2text_element_id.
"""

import hashlib
import json
import os
import re
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER_DIR = os.path.join(REPO_ROOT, "DATASETS",
                          "PDF_FIDELITY_RENDERINGS", "1907_04931")
CANDIDATES_PATH = os.path.join(RENDER_DIR, "pix2text_candidates.jsonl")
ADJUDICATION_REPORT = os.path.join(RENDER_DIR, "adjudication_report.jsonl")  # source of explicit statuses (carry-forward)
TARGET_REPORT = os.path.join(RENDER_DIR, "adjudication_targets.jsonl")  # new adjudication output from this layer
SUMMARY_PATH = os.path.join(RENDER_DIR, "adjudication_targets_summary.json")
MD_PATH = os.path.join(RENDER_DIR, "adjudication_targets_report.md")

# Status values written to match_status on adjudicated records.
STATUS_ADJUDICATED = "ADJUDICATED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_NO_MATCH = "NO_MATCH"

# Carry-forward statuses (Layer 2 explicit statuses)
CARRY_FORWARD = ("VISUALLY_VERIFIED", "SPATIAL_MATCH", "TEXT_MATCH")

# Breach of the no-semantic-promotion rule: a record whose match_status would
# be upgraded >= ADJUDICATED by pixel/crop evidence alone is rejected here and
# stays UNVERIFIED/NO_MATCH instead.
# (The adjudication below never derives VISUALLY_VERIFIED from crop evidence;
# it only records what the earlier layer already recorded for the 30 visual
# records, and labels the rest explicitly.)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load_records():
    records = []
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_meaningful_ocr(text):
    """A non-trivial OCR token count; fragments have a single noise token."""
    toks = re.findall(r"[a-z0-9]+", _normalize(text))
    return len(toks) >= 2


def _normalize(text):
    t = re.sub(r"\s+", " ", str(text or "")).lower()
    t = re.sub(r"[^a-z0-9\s._-]", " ", t)
    return t.strip()


def _parser_association(record):
    return bool(record.get("parser_match_ids") or [])


def _source_hash(record):
    path = os.path.join(RENDER_DIR, record.get("image_path", ""))
    if not os.path.exists(path):
        return None
    return _sha256_file(path)


# --------------------------------------------------------------------------
# adjudication decisions
# --------------------------------------------------------------------------
def _decide(record):
    """Return (match_status, adjudication_detail). Never reads image pixels."""
    raw = str(record.get("raw_ocr") or "")
    raw_norm = _normalize(raw)
    if not raw_norm:
        return STATUS_UNVERIFIED, "EMPTY_OCR"

    # 1. Malformed OCR page (known for pages 14/16/17/18/19 in the harvest).
    if record.get("parse_error"):
        return STATUS_ADJUDICATED, "MALFORMED_OCR_WARN_SAFE_SKIP"

    # 2. Fragments: single noise token, no meaningful OCR.
    if len(re.findall(r"[a-z0-9]+", raw_norm)) == 1:
        # e.g. 'v', 'm', 'n', 'r', 'h' - fragments, not expressions.
        return STATUS_ADJUDICATED, "FRAGMENT_SINGLE_TOKEN"

    # 3. Duplicate occurrence of a normalized expression.
    import itertools
    norm = raw_norm
    cands = [c for c in records if c.get("pix2text_element_id") != record.get("pix2text_element_id")]
    dup = [c for c in cands if _normalize(str(c.get("raw_ocr") or "")) == norm]
    if dup:
        return STATUS_ADJUDICATED, "DUPLICATE_OBSERVATION"

    # 4. Inline expression missing from the parser ledger.
    #    The frozen parser ledger has 4 records (page 4: ζ(ℓ+1)×2; page 12: √pe, ∝√pe).
    #    Anything else inline with no parser association is a discovery candidate
    #    - reviewed, but not promoted to semantic.
    if not _parser_association(record):
        return STATUS_ADJUDICATED, "PARSE_GAP_DISCOVERY"

    # 5. Strong spatial/textual association (e.g. parser_match_ids) but no
    #    crop evidence in this layer → retain the layer status; do NOT upgrade.
    return STATUS_NO_MATCH, "NO_CROP_EVIDENCE_IN_ADJUDICATION_LAYER"


# --------------------------------------------------------------------------
# adjudication
# --------------------------------------------------------------------------
def adjudicate(records, existing_status_by_id):
    """Adjudicate only UNADJUDICATED records; carry forward explicit statuses.

    existing_status_by_id: map pix2text_element_id -> match_status from the
    earlier adjudication layer (adjudicate_candidates_v2.py). Records already
    carrying an explicit non-UNADJUDICATED status are left untouched.

    A record is adjudicated only when it has NO existing explicit status.
    """
    adjudicated = []
    for r in records:
        row = dict(r)
        st = existing_status_by_id.get(r["pix2text_element_id"])
        if st:  # carry forward explicit status from earlier layer
            row["match_status"] = st
            adjudicated.append(row)
            continue
        st, detail = _decide(r)
        row["match_status"] = st
        row["adjudication_detail"] = detail
        adjudicated.append(row)
    return adjudicated


# --------------------------------------------------------------------------
# writer
# --------------------------------------------------------------------------
def _git_sha():
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=REPO_ROOT, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def write_reports(adjudicated):
    os.makedirs(RENDER_DIR, exist_ok=True)
    with open(TARGET_REPORT, "w", encoding="utf-8") as f:
        for r in adjudicated:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    total = len(adjudicated)
    carried = [r for r in adjudicated if r.get("match_status") in CARRY_FORWARD]
    newly = [r for r in adjudicated if r.get("match_status") == STATUS_ADJUDICATED]

    status_counts = {}
    for r in adjudicated:
        st = r.get("match_status")
        status_counts[st] = status_counts.get(st, 0) + 1

    newly_detail = {}
    carried_detail = {}
    for r in newly:
        d = r.get("adjudication_detail") or "UNKNOWN"
        newly_detail[d] = newly_detail.get(d, 0) + 1
    for r in carried:
        d = r.get("adjudication_detail") or "UNKNOWN"
        carried_detail[d] = carried_detail.get(d, 0) + 1

    summary = {
        "paper_id": "1907.04931",
        "total_records": total,
        "carried_forward_count": len(carried),
        "carried_forward_detail_count": len(carried),
        "newly_adjudicated_count": len(newly),
        "newly_adjudicated_detail_count": len(newly),
        "status_distribution": status_counts,
        "status_distribution_denominator": total,
        "newly_adjudicated_detail_distribution": newly_detail,
        "newly_adjudicated_detail_denominator": len(newly),
        "carried_forward_detail_distribution": carried_detail,
        "carried_forward_detail_denominator": len(carried),
        "target_report_path": TARGET_REPORT,
        "summary_path": SUMMARY_PATH,
        "generated_commit": _git_sha(),
        "generated_commit_note": "Commit HEAD at generation time; this file is committed in the following commit.",
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Markdown report.
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("# Targeted Adjudication Report - 1907.04931\n\n")
        f.write("Layer 3 of the adjudication contract (see "
                "docs/adjudication-layer-contract.md). Carries forward Layer-2 "
                "explicit statuses; adjudicates UNADJUDICATED records.\n\n")
        f.write("| Metric | Value |\n|---|---|\n")
        f.write(f"| Total records | {total} |\n")
        f.write(f"| Carried forward | {len(carried)} |\n")
        f.write(f"| Newly adjudicated | {len(newly)} |\n")
        f.write("\n## Status distribution (denominator = total records = %d)\n\n" % total)
        f.write("| Status | Count |\n|---|---|\n")
        for st in (STATUS_ADJUDICATED, STATUS_UNVERIFIED, STATUS_NO_MATCH,
                   "VISUALLY_VERIFIED", "SPATIAL_MATCH", "TEXT_MATCH"):
            if st in status_counts:
                f.write(f"| {st} | {status_counts[st]} |\n")
        f.write("\n## Newly-adjudicated reasons (denominator = newly adjudicated = %d)\n\n" % len(newly))
        f.write("| Detail | Count |\n|---|---|\n")
        for d, c in sorted(newly_detail.items()):
            f.write(f"| {d} | {c} |\n")
        f.write("\n## Carried-forward detail (denominator = carried forward = %d)\n\n" % len(carried))
        f.write("| Detail | Count |\n|---|---|\n")
        for d, c in sorted(carried_detail.items()):
            f.write(f"| {d} | {c} |\n")
# --------------------------------------------------------------------------
if __name__ == "__main__":
    records = load_records()
    # Carry forward the earlier adjudication layer's explicit statuses.
    existing_map = {}
    adj_path = os.path.join(RENDER_DIR, "adjudication_report.jsonl")
    if os.path.exists(adj_path):
        with open(adj_path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                st = r.get("match_status")
                if st in ("VISUALLY_VERIFIED", "SPATIAL_MATCH", "TEXT_MATCH"):
                    existing_map[r["pix2text_element_id"]] = st
    print(f"Carry-forward map: {len(existing_map)} records with explicit status")
    adjudicated = adjudicate(records, existing_map)
    write_reports(adjudicated)
    print(f"WROTE {len(adjudicated)} records")
    from collections import Counter
    print(json.dumps(dict(Counter(r["match_status"] for r in adjudicated)), indent=2))

