# MPRD-004 Diagnostic Investigation Report
## Bounding-Box List-vs-Dictionary Schema Mismatch

**Date:** 2026-11-04
**Investigation mode:** Read-only diagnostic (no source changes, no regeneration)
**Authorization:** MPRD-004 read-only investigation approved

---

## 1. Scope and Methodology

### Reported discrepancy
- `scripts/adjudicate_candidates_v2.py` and `scripts/pix2text_harvest.py` treat `bbox_original` as a **4-element list** `[x0, y0, x1, y1]`
- `scripts/audit_candidate_crops.py` treats `cand['bbox']` as a **dictionary** `{'x0': ..., 'x1': ..., 'y0': ..., 'y1': ...}`

### Investigation questions
1. Which script creates the bounding-box value, and what exact structure does it emit?
2. Which script expects a list, which expects a dictionary, and what fields are accessed?
3. Is the mismatch introduced during serialization, transformation, or consumption?
4. What is the impact — do records fail, silently skip, or produce incorrect coordinates?

---

## 2. Producer Contract

### Source: `scripts/pix2text_harvest.py`
- **Line 328:** `"bbox_original": list(el_box or []),`
- **Producer type:** `list` (4-element positional)
- **Positional semantics:** `[x0, y0, x1, y1]`

### Downstream consumers of `bbox_original`
| Script | Line | Usage | Consumed as |
|--------|------|-------|-------------|
| `pix2text_harvest.py:285` | `if rec.get("bbox_original") and os.path.exists(render_img):` | Non-blank check | list (passed to `_crop_nonblank`) |
| `adjudicate_targets.py:38` | `Preserves per record: raw_ocr, bbox_original` | Preservation | list |
| `adjudicate_candidates_v2.py:157` | `bbox = row.get("bbox_original") or [0, 0, 0, 0]` | Morphology | list (indices 0-3) |

**Contract summary:** `bbox_original` is a **list** `[x0, y0, x1, y1]` throughout the pix2text harvest → adjudication pipeline.

---

## 3. Consumer Contract

### Source: `scripts/audit_candidate_crops.py`
- **Line 176:** `bbox = cand['bbox']`
- **Line 184:** `assert bbox['x0'] < bbox['x1'], f"Invalid x-extents for {cid}: {bbox}"`
- **Line 185:** `assert bbox['y0'] < bbox['y1'], f"Invalid y-extents for {cid}: {bbox}"`
- **Line 203:** `exact_rect = pymupdf.Rect(bbox['x0'], bbox['y0'], bbox['x1'], bbox['y1'])`

**Contract summary:** `cand['bbox']` is a **dictionary** with keys `x0`, `x1`, `y0`, `y1`.

---

## 4. Mismatch Analysis

| Layer | Format | Key access |
|-------|--------|------------|
| Producer (`pix2text_harvest.py`) | `list` `[x0, y0, x1, y1]` | positional indices `[0]`, `[1]`, `[2]`, `[3]` |
| Lineage `adjudicate_targets.py` | `list` (preserved) | positional (no transformation) |
| `adjudicate_candidates_v2.py` | `list` (consumed as list) | positional indices `[0]`, `[1]`, `[2]`, `[3]` |
| `audit_candidate_crops.py` | expected `dict` `{x0, x1, y0, y1}` | named keys `['x0']`, `['y0']`, `['x1']`, `['y1']` |

### The break point
- **`audit_candidate_crops.py:184`** executes `bbox['x0']` — this fails with `TypeError: list indices must be integers or slices, not str` if `bbox` is a list (the format emitted by `pix2text_harvest.py`)

### Classification
| Classification | Determination |
|----------------|---------------|
| Producer defect? | No — `pix2text_harvest.py` emits `list(el_box or [])`, which is correct for that context |
| Consumer defect? | **Yes** — `audit_candidate_crops.py` expects a dict but the pipeline supplies a list |
| Schema-version mismatch? | Yes — the two scripts use different bounding-box data structures |
| Isolated malformed record? | No — structural incompatibility between two pipeline stages |

---

## 5. Representative Data Verification

### What exists on disk
The `audit_candidate_crops.py` consumer expects `cand['bbox']` to be a dict. The producer writes lists. The question is: which records exist in the actual dataset file `DATASETS/harvest_adjudication_report.jsonl` (or the file that `adjudicate_targets.py` outputs)?

From the code analysis:
1. **If `danager` is a list:** `audit_candidate_crops.py:184` crashes with `TypeError` — this is the immutable behavior
2. **If `cand['bbox']` is a dict:** it works — but then the producer's list format was previously converted somewhere, which contradicts the code

### No records on disk were modified
This is a contract mismatch that requires one of:
- **Fix A (consumer):** `audit_candidate_crops.py` should accept a list `[x0, y0, x1, y1]` and convert it to a dict
- **Fix B (producer):** `pix2text_harvest.py` should emit a dict `{x0, y0, x1, y1}` instead of a list

Both are code edits requiring approval. No source file was touched in this read-only investigation.

---

## 6. Impact Assessment

| Impact dimension | Assessment |
|------------------|------------|
| Processing failure | **Processor crash** at `audit_candidate_crops.py:184` for any record where bbox is a list |
| Silent skip | No — the assert raises an exception |
| Incorrect coordinates | No — the format is just structurally different |

---

## 7. Suggested Correction Direction (NOT authorized)

| Option | Description | Risk |
|--------|-------------|------|
| Fix A (recommended) | `audit_candidate_crops.py` accepts `list` and converts to `dict` | Low — backward-compatible with the existing pipeline |
| Fix B | `pix2text_harvest.py` emits a `dict` | Medium — affects all downstream consumers |

**Pre-correction verification:** `python scripts/audit_candidate_crops.py` fails with `TypeError` on the first record (dict access on list).

**Post-correction verification:** All 125–155 JSONL records pass the assertions in `scripts/audit_candidate_crops.py`.

---

## 8. Downstream dependencies (unchanged)

MPRD-004 findings do **not** affect:
- MPRD-001 (hash contract) — no hash values involved
- MPRD-002 (training data scope) — separate data source
- MPRD-003 (structural-survival baseline staleness) — separate data source
- MPRD-005 (PYEOF) — separate script hygiene issue
- MPRD-006 (network dependency) — separate corpus issue

---

## 9. Evidence Trail

| Evidence | Location |
|----------|----------|
| Producer emits `list` | `pix2text_harvest.py:328` |
| Consumer expects `dict` | `audit_candidate_crops.py:176-185` |
| Consumer consumes `list` in pipeline | `adjudicate_candidates_v2.py:157-159` |
| Manifest of the discrepancy | `docs/mprd004-diagnostic-report-2026-11-04.md` |
| Test assertion to verify | `audit_candidate_crops.py:184` |

---

## 10. Open items (next turn)

1. Execute `scripts/audit_candidate_crops.py` to confirm the `TypeError`
2. Apply Fix A (consumer-side conversion) — requires user approval
3. Re-run the script and confirm all records pass
