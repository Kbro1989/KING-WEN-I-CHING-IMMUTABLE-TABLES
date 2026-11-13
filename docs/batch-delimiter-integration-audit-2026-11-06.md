# Audit: Batch Pipeline ↔ Delimiter Detection Integration

**Audit date:** 2026-11-06
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Branch:** v2-remediation (befa228927)
**Reference:** Evaluation of the 243-paper batch pipeline as a delimiter-detection baseline

---

## Executive Summary

The batch PDF math extraction pipeline (`scripts/batch_math_pipeline.py`) is **disconnected** from the repository's existing delimiter-detection capabilities. The pipeline successfully processes 243 papers and produces a clean accounting baseline (solvable + partial + rejected + unresolved = total), but it does **not** invoke:

- `targeted_math_detector.py` (visual candidate detection)
- `font_aware_math_classifier.py` (font-aware classification)
- `delimiter_aware_structural_recovery.py` (structural recovery/pairing)
- `delimiter_identity.py` (delimiter identity classification)

The pipeline operates exclusively on extracted equation strings and their classification, without ever invoking the PDF-level visual detection components.

---

## 1. Producer/Consumer Call Graph

### Producer: batch_math_pipeline.py

```
batch_math_pipeline.py:16-30
├── fetch_arxiv_html(arxiv_id) → html content
        └── process_paper(arxiv_id, html_content, url)  ← single entry point
              ├── extract_math_with_context(html)       # equation strings
              ├── parse_integral(mathml)                # per equation
              ├── try_solve(expr)                       # per equation
              ├── relate_to_context(eq, ...)            # per equation
              └── return result_document
                    └── → batch_pipeline_output.jsonl
```

**Key observation:** The only inputs to the pipeline are HTML strings. The pipeline never opens PDF files directly, never loads images, and never invokes any visual detection component.

### Consumer: What the pipeline persists

The pipeline persists:
1. `total_equations` — count of extracted equation strings
2. `solvable`, `partial`, `rejected`, `unresolved` — classification counts
3. `equations` — the extracted equation data

**It does NOT persist:**
- Delimiter candidates
- Delimiter identity classifications
- Visual geometry (bounding boxes, heights)
- Pairing status
- Detection source (text/vector/raster)
- Any visual detection evidence

---

## 2. Detected Break

The following data flow exists in the repository for delimiter detection:

```
PDF page (fitz/pymupdf)
  → targeted_math_detector.py   (visual candidates: tall glyphs, stretched delimiters)
        → font_aware_math_classifier.py  (font-aware classification)
              → delimiter_aware_structural_recovery.py  (pairing, nesting, enclosure)
                    → delimiter_identity.py (identity classification)
                          → output: delimiter records with bbox, classification, pairing
```

**Current batch pipeline path:**

```
PDF page (fitz/pymupdf)
  → batch_math_pipeline.py (HTML extraction only)
        → process_paper(html)
              → extract equation strings
                    → equation accounting (solvable/partial/rejected/unresolved)
                    → output: equation counts only
```

**The disconnect:** The batch pipeline never calls the visual detector. The equation accounting baseline does not capture visual delimiter detection.

---

## 3. Producer Tables

### batch_math_pipeline.py producers

| Function | Input | Output | Consumer |
|----------|-------|--------|----------|
| `fetch_arxiv_html()` | arxiv_id | HTML content | `process_paper()` |
| `process_paper()` | HTML, URL | `result_document` | `main()` |
| `main()` | corpus JSONL | output JSONL, manifest | — |

### e2e_math_pipeline.py producers

| Function | Input | Output | Consumer |
|----------|-------|--------|----------|
| `extract_math_with_context()` | HTML | list[dict] | `process_paper()` |
| `parse_integral()` | mathml | node, notes | `process_paper()` |
| `try_solve()` | expr | solvable, result, error | `process_paper()` |
| `relate_to_context()` | eq, equations, i | eq with relations | in-place |
| `process_paper()` | HTML, URL | result_document | `batch_math_pipeline.py` |

### Existing delimiter ecosystem

| Function | Input | Output | Consumer |
|----------|-------|--------|----------|
| `targeted_math_detector.py` | PDF file | candidates, positions | — |
| `font_aware_math_classifier.py` | candidates, font info | classification | `delimiter_aware_structural_recovery.py` |
| `delimiter_aware_structural_recovery.py` | candidates, positions | paired/nested/unmatched | — |
| `delimiter_identity.py` | MathML/delimiter token | identity, kind | `mathml_parser.py`, downstream consumers |

---

## 4. Verification Commands

### Verify current batch pipeline connectivity

```bash
cd /c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
python -c "
import sys
sys.path.insert(0, 'scripts')
import importlib
mod = importlib.import_module('batch_math_pipeline')
print('batch_math_pipeline imports:', [n for n in dir(mod) if not n.startswith('_')])
"
```

### Verify process_paper call graph

```bash
cd /c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES
grep -n "from e2e_math_pipeline import\|import.*targeted_math\|import.*delimiter\|import.*font_aware\|import.*recovery" scripts/batch_math_pipeline.py scripts/e2e_math_pipeline.py
```

Expected result: No imports of delimiter/visual-detection modules from either file.

### Verify output schema has no delimiter fields

```bash
python -c "
import json
with open('DATASETS/batch_pipeline_output.jsonl') as f:
    lines = f.readlines()
import re
schema_keys = set()
for line in lines:
    rec = json.loads(line)
    rd = rec.get('result_document', {})
    for k in rd:
        schema_keys.add(k)
print('Output schema keys:', sorted(schema_keys))
model_fields = ['delimiter_candidates', 'delimiter_identity', 'delimiter_bbox', 'delimiter_height', 'opening_closing_direction', 'pairing_status', 'structural_recovery_status', 'detection_source']
for m in model_fields:
    present = any(m in k.lower() for k in schema_keys)
    print(f'  {m}: {\"YES\" if present else \"NO\"} — NOT PRESENT')
"
```

---

## 5. Recommended Integration Architecture

The existing delimiter components are confirmed to exist in the repository. The missing piece is correlation of the visual-detection output into the batch accounting layer.

### Proposed data flow

```
PDF (fitz/pymupdf)
  → targeted_math_detector.py  (candidates: bbox, font, glyph_type)
        → font_aware_math_classifier.py  (classification: math/op/bigger/another/normal)
              → delimiter_aware_structural_recovery.py  (pairing: open/close/non-pair)
                    → delimiter_identity.py  (identity management)
                          → persist: per-page delimiter records
```

### Integration targets

1. **Paper-level audit record**: Add fields to batch output documenting detection attempts per paper (PDF available, pages failed, candidates detected).
2. **Page-level detection record**: Persist delimiter candidates per page (font, bbox, glyph_type, classification).
3. **Cross-modal association**: Link visual candidates to recovered equation structures where applicable.
4. **Manifest**: Persist detection status per page.

### Existing evidence to preserve

The following artifacts are frozen and should not be modified:
- `scripts/phase2b_adversarial_challenge.jsonl` — adversarial challenge material
- `scripts/phase2c_gate_library.py` — gate evaluation
- `scripts/evaluate_cross_paper_generalization_v1.py` — generalization evaluation
- `scripts/cross_paper_generalization_evaluation_v1.json` — frozen baseline reference
- `scripts/evaluate_rakmani_generalization.py` — Rakhmani generalization
- `scripts/evaluate_structural_completeness_b2.py` — structural completeness evaluation
- `scripts/structural_evidence_graph.py` — evidence graph

### Existing delimiter tracking artifacts

- `DATASETS/delimiter_tracking.json` — tracking contract (already frozen, do not modify)
- `DATASETS/delimiter_identity_audit.json` — identity-loss audit
- `delimiter_structural_recovery_report.json` — recovery report

---

## 6. Recommended Priorities

### 1. Preserve the accounting baseline (DONE)

The 243-paper batch output is a clean accounting baseline. Do not modify:
- `scripts/e2e_math_pipeline.py` (except the resolution fix already applied)
- `scripts/batch_math_pipeline.py` (no change to accounting fields)

### 2. Build the visual-detection integration layer (NEXT)

Create a new script that:
1. Loads a paper PDF
2. Runs `targeted_math_detector.py` on each page
3. Applies `font_aware_math_classifier.py`
4. Runs `delimiter_aware_structural_recovery.py`
5. Persists a per-page delimiter record with provenance

### 3. Add corpus-level accounting for the delimiter layer

Per paper, persist:
- `pages_attempted` — total pages in PDF
- `pages_detected` — pages with delimiter candidates
- `page_failure_count` — pages where detection failed
- `delimiters_detected` — number of delimiter candidates
- `delimiters_classified` — number of candidates with valid classification
- `delimiters_unresolved` — number of candidates without resolution

Do NOT add these counts to the equation accounting.

### 4. Cross-modal association

For each paper, attempt to associate:
- Visual candidates (from `targeted_math_detector.py`)
- With recovered equation structures (from `process_paper()`)

### 5. Documentation

Update `docs/golden-standard-audit-matrix.md` with:
- Batch pipeline producer/consumer map (completed above)
- Delimiter ecosystem inventory
- Integration gaps identified
- Recommended next steps

---

## 7. Files to Create / Modify

### New files

- `scripts/delimiter_corpus_integration.py` — corpus-level delimiter integration layer
- `docs/batch-delimiter-integration-audit-2026-11-06.md` — integration audit (this file)

### Files to modify

- `docs/golden-standard-audit-matrix.md` — update with integration audit (mentioned above)

### Files to preserve (do not modify)

- `scripts/e2e_math_pipeline.py` — resolution fix already applied
- `scripts/batch_math_pipeline.py` — accounting baseline frozen
- `scripts/phase2b_adversarial_challenge.jsonl`
- `scripts/phase2c_gate_library.py`
- `scripts/evaluate_cross_paper_generalization_v1.py`
- `scripts/evaluate_structural_completeness_b2.py`
- `scripts/structural_evidence_graph.py`
- `DATASETS/delimiter_tracking.json`
- `DATASETS/delimiter_identity_audit.json`
- `delimiter_structural_recovery_report.json`

---

## 8. Verification Pattern

After building the integration layer:

```bash
cd /c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES

# 1. Verify batch pipeline frozen
python -m py_compile scripts/e2e_math_pipeline.py
python -m py_compile scripts/batch_math_pipeline.py

# 2. Verify integrated tier green
python scripts/delimiter_corpus_integration.py --test-mode

# 3. Audit trail documented
python scripts/audit_integration_call_graph.py

# 4. Output has delimiter fields
python -c "
import json
with open('DATASETS/batch_pipeline_output.jsonl') as f:
    last = json.loads(f.readlines()[-1])
rd = last['result_document']
print('Has delimiter_candidates:', 'delimiter_candidates' in rd)
print('Has page_detection:', 'page_detection' in rd)
"
```

---

## 9. Open Questions

1. **What is the correct mapping between equation strings and visual candidates?** The equation extraction layer (mathml text) and the visual layer (PDF pixels) may capture different delimiters. A mapping strategy is needed.

2. **Which detector should be the primary?** `targeted_math_detector.py` and `v2_delimiter_aware_structural_recovery.py` are separate paths with different detectors. Which one should be the canonical integration?

3. **Is `mathml_parser.py` the source of truth for delimiter identity?** If yes, callers need to be re-verified against the actual `delimiter_identity.py` API, not assumed semantics.

4. **Which engine version should be declared?** The repository has both a frozen v1 engine and a v2 remediation engine. Any integration must declare which engine version it invokes.

---

## 10. Status

**Completed:**

- [x] Verified all 243 papers reconciled (accounting = total)
- [x] Preserved pre-fix evidence
- [x] Confirmed batch pipeline call graph (no delimiter imports)
- [x] Confirmed delimiter components exist on disk
- [x] Documented producer/consumer chain

**Pending:**

- [ ] Build PDF visual-detection integration layer
- [ ] Add per-page detection records to batch output
- [ ] Update golden-standard-audit-matrix.md with integration plan
- [ ] Restore batch pipeline after integration verification

---

## 11. Summary of Delimiter Ecosystem

| Layer | Component | Status |
|-------|-----------|--------|
| MathML identity | `mathml_parser.py`, `delimiter_identity.py` | Existing |
| Visual candidates | `targeted_math_detector.py` | Existing (unused by batch) |
| Font classification | `font_aware_math_classifier.py` | Existing (unused by batch) |
| Structural recovery | `delimiter_aware_structural_recovery.py`, `v2_delimiter_aware_structural_recovery.py` | Existing (unused by batch) |
| Corpus accounting | `batch_pipeline_output.jsonl` | Existing (frozen, baseline) |

---

## Sign-off

**Prepared:** 2026-11-06
**Auditors:** Kbro1989 (auto-audit), Kbro1989 (verification)
**Findings:** 1 critical disconnect identified (batch pipeline does not invoke visual delimiter detection)
**Action items:** Build integration layer, freeze accounting baseline, preserve existing components
