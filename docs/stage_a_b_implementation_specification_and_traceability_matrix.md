# Stage A / Stage B Implementation Specification and Traceability Matrix
**Project:** King Wen — Math-to-PDF Association Contract v1 (read-only spec)
**Deliverable:** Implementation specification + traceability matrix only
**Date:** 2026-11-12

---

## 0. Frozen baseline (no changes made this session)

| Artifact | Role | Git status | SHA-256 |
|---|---|---|---|
| `scripts/math_pdf_association.py` | Sidecar writer + version enforcement | **untracked** (not modified) | `6bc40a56...fd6ecd` |
| `scripts/test_math_pdf_association_contract_v1.py` | 16-test contract suite | **untracked** | `d940b5ce...ce9443` |
| `scripts/run_contract_v1_standalone.py` | Standalone runner (no pytest) | untracked | `342454af...02762` |
| `docs/math_pdf_association_contract_v1.md` | Contract spec (v1) | untracked | `27878e75...c0d27a3` |

**Verified:** `PYTHONPATH=scripts python -m pytest scripts/test_math_pdf_association_contract_v1.py -q` → `16 passed in 0.08s`.
**Verified:** `git status --porcelain` shows none of the four files tracked (produced this session).

**Status of frozen baseline (accurate, not aspirational):**
- **Implemented:** sidecar assembly (`build_association_sidecar`), canonical JSON serialization (`sidecar_to_canonical_json`), version compatibility enforcement (`is_version_compatible`, `validate_sidecar_compatibility`, `quarantine_incompatible_sidecar`, `VersionMismatchError`), deterministic node identity (`_make_node_id`).
- **Not implemented:** any association matching. The production module's own header states it "does NOT parse LaTeX, does NOT derive PDF coordinates, and does NOT perform any matching."

---

## 1. Contract discrepancy resolved

The contract spec (`docs/math_pdf_association_contract_v1.md`) describes **two layers**:

- **Layer 1 (delivered):** Section 2 schema + Section 3 versioning + Section 3.4 enforcement + Section 3.3 canonical serialization. This is the sidecar writer live in `scripts/math_pdf_association.py`.
- **Layer 2 (documented, not delivered):** Section 4 Stage A alignment, Section 5 Stage B association, Section 6 relationship geometry. The spec's own acceptance criteria (Section 7.2) explicitly split these: *contract tests* verify schema/role/bbox/provenance; *association tests* verify independent discovery against adjudicated gold.

**Discrepancy:** the production module implements Layer 1 only. Section 4/5 Stage A/B matchers are documented as "new scope this contract governs" but do not exist in `scripts/math_pdf_association.py` — nor in any file in the repo. This is not a patchable drift; it is a scope that was never delivered. The module's documented scope is "pure data-assembly function" — no matching.

**Do not treat documented functions as implemented APIs.** The Stage A/B signatures described in Section 4.1 and 5.1 are *contract requirements*, not *existing functions*.

---

## 2. Stage A — Source occurrence ↔ PDF expression-region alignment

### 2.1 Position in pipeline

Stage A precedes Stage B. It maps a `SourceOccurrence` to its PDF spatial container before any AST-node work.

### 2.2 Inputs (per spec)

- `SourceOccurrence` — paper_id, paper_version, source_locator, occurrence_index, source_hash
- `targeted_math_detector.py` per-char observations — font, size, bbox_pdf_pt, page_index, block_index, line_index, span_index, char_index

### 2.3 Required matcher functions (documented, not implemented)

| Matcher | Spec description | Inputs | Outputs | Acceptance criteria |
|---|---|---|---|---|
| `expression_region_overlap` | bounding-box intersection with tolerance | occurrence + glyph observations (bboxes) | one `source_alignment` record (or `unverified_region`) | overlap > 0; confidence ≥ 0.80 → `established`; else `ambiguous` |
| `page_region_fallback` | no bbox available | occurrence with no geometry | `source_alignment` with `expression_region.rect_pdf_pt` = null, `alignment_method` = `page_region_fallback`, `annotation` = `unverified_region` | must not raise; must mark `unresolved`-like |

### 2.4 Ambiguity / failure representation (spec-mandated, no forced decisions)

From spec Sections 4.1 and 5.1:

| Condition | Status | Representation |
|---|---|---|
| single occurrence → multiple PDF regions | `ambiguous` | `competing_ids` lists both |
| multiple occurrences → same region | `ambiguous` | competing IDs listed |
| no geometry evidence | `unresolved` | `pdf_sha256`, `page_index`, `expression_region` all `null` — `unresolved` is a valid status, not an error |
| bbox available but no overlap | `unresolved` | same `null` treatment |
| latent/detached region (fallback) | `unverified_region` | `expression_region` null, `alignment_method` = `page_region_fallback` |

### 2.5 Outputs

One `source_alignment` record per matched occurrence:
```json
{
  "id": "src_align:{paper_id}:{version}:{locator}:{region_n}",
  "source_occurrence_id": "paper:{paper_id}:{version}:{locator}",
  "pdf_sha256": "sha256:...",
  "page_index": 3,
  "expression_region": {"rect_pdf_pt": [100,200,350,240], "block_index":0, "line_index":4, "span_index":0},
  "alignment_method": "page_region_overlap",
  "confidence": 0.88,
  "annotation": "unverified_region"  // only when fallback
}
```

---

## 3. Stage B — AST node ↔ glyph observation association

### 3.1 Pipeline position

Stage B runs **after** Stage A. It uses the Stage A `source_alignment` to anchor each AST node to its glyph observations. It consumes `ast_nodes`, `glyph_observations`, and `source_alignments`.

### 3.2 Required matcher functions (documented, not implemented)

| Matcher | Spec description | Inputs | Outputs | Acceptance criteria |
|---|---|---|---|---|
| `expression_region_overlap` | bounding-box intersection with tolerance (default 1.0 pt) | AST node xmml bbox / associated glyph bbox | node ↔ glyph binding | overlap ≥ 0 → binding; `established` if confidence ≥ 0.80 |
| `expression_region_exact` | exact containment, no tolerance — reserved for equality checks | same as above | binding (only valid if containment is exact) | must never relax to `overlap` semantics |
| `node_id_replay` | source-ordered glyph IDs replayed from AST in document order | AST tree walk | node → glyph list | used only when coordinates absent; weaker association |
| `glyph_geometry_match` | glyph character matches node value AND bbox matches expression region exactly | node value + glyph char + bbox | binding | glyph `char` must equal node `value`; bbox must match |
| `expression_region_leak` | no explicit correspondence; recorded as `unverified_regression` | degenerate case | node binding with `confidence` = 0.0, `annotation` = `unverified_regression`, method listed for manual adjudication | least reliable; must not be presented as established |

### 3.3 Association statuses (spec-mandated)

| Status | Meaning | Confidence |
|---|---|---|
| `established` | high-reliability method (overlap/exact/glyph_geometry) | ≥ 0.80 |
| `ambiguous` | reliable method but ambiguous region OR confidence < 0.80 | < 0.80 or competing IDs |
| `unresolved` | no geometry evidence, or mapping impossible | null |
| `unverified_regression` | fallback method used | 0.0 |

### 3.4 Ambiguity / failure representation

Per spec Section 5.1 and 5.2: unambiguous incident = `ambiguous` with competing IDs listed; missing evidence = `unresolved` (null fields); low-confidence fallback = `unverified_regression` (confidence 0.0). No forced match, no silent fallback to `established`.

### 3.5 Outputs

One `node_association` record per node:
```json
{
  "node_id": "paper:{paper_id}:{version}:{locator}:root/0",
  "matched_glyph_ids": ["glyph:{paper_id}:{version}:{locator}:1"],
  "association_method": "expression_region_overlap",
  "confidence": 0.87,
  "status": "established"
}
```

---

## 4. Relationship geometry contract (contract-only, Tier 3)

Section 6 defines relationship records that must retain component geometry, not merged bbox:

- Per-child role records: `child_role` (base/exponent/numerator/denominator), `child_node_id`, `child_glyph_ids`, `child_bbox_pdf_pt`
- `combined_bbox_pdf_pt` = union of child bboxes (final output, not proof)
- `relationship_id` computed per relationship, recursive child roles
- Preserve `child_bbox_pdf_pt` per child (not collapsed to combined)

---

## 5. test division (spec-mandated, must not be conflated)

Spec Section 7 splits validation into two independent categories. **Do not conflate:**

| Category | What it verifies | Grade |
|---|---|---|
| Contract tests | schema, role mapping, bbox calculation, provenance; manually constructed inputs (`msup`, `mfrac`, `munderover`, tall delimiter, malformed MathML) | verifies implementation structure only |
| Association tests | independent discovery from per-item inputs vs separately adjudicated gold | establishes accuracy |

**Metrics for association tests:** node association precision/recall, glyph coverage, role assignment accuracy, ambiguous-association rate, unmatched-AST-node rate, unmatched-glyph rate, relationship bbox IoU and edge residual. Gold must be *separately adjudicated*, not manually supplied AST-to-glyph IDs.

**Key limitation:** the existing 16 tests verify contract-level schema and serialization only. They are **not** association-accuracy tests and must not be cited as evidence of association validation.

---

## 6. math_recovery/ provenance audit

Files in `scripts/math_recovery/` (all untracked, not in any git commit):

| File | Content type | Role per self-description | Executable? |
|---|---|---|---|
| `evidence_role_classifier.py` | classification ontology / metadata | Documents CAPTURE/MIRROR/SIMULATION/SYNTHETIC taxonomy for the broader pipeline | No (scope: other programs) |
| `pipeline_contract.py` | docstring-only API spec + `RECOVERY_VERSIONS` comment | Defines `detect_status`, `classify_recovery`, `verify_occurrence_conservation` — **no implementation present** | No |
| `recovery_registry.py` | docstring + in-code `RECOVERY_VERSIONS` registry | Comments track math-recover history, not executable association logic | No |
| `__init__.py` | **missing** | Reference import model uses `from math_recovery.pipeline_contract import ...` | — |

### 6.1 Missing `__init__.py` — required or not?

The three files contain docstring `Usage:` blocks that reference `from math_recovery.pipeline_contract import ...` and `from math_recovery.recovery_registry import RECOVERY_VERSIONS`. These import statements are **documentation-only** — they appear inside `__doc__` strings, not in executable code. No file in `scripts/math_recovery/` executes an import against the sibling `math_pdf_association.py` or the rest of the extraction pipeline.

**Conclusion:** the missing `__init__.py` is **not required by any current executable import model**. It is required only if these three files become executable Python packages (i.e., if the documented `from math_recovery.pipeline_contract import ...` forms are promoted into real code). Creating `__init__.py` now would be premature — it would make the directory look complete without there being any executable package. If we later implement the math_recovery pipeline and use standard package imports, add `__init__.py` then.

The math_recovery/ files are a **secondary recording layer** (classification ontology, versioning registry, docstring-only API spec) — they are not the association capacity itself and must not be treated as evidence of Stage A/B implementation.

---

## 7. Traceability matrix (stage-by-stage)

| Requirement | Source | Implemented? | Evidence |
|---|---|---|---|
| Sidecar assembly + serialization | spec §§2–3.3 | **Yes** | `build_association_sidecar`, `sidecar_to_canonical_json` in `scripts/math_pdf_association.py` |
| Version enforcement | spec §3.4 | **Yes** | `is_version_compatible`, `validate_sidecar_compatibility`, `quarantine_incompatible_sidecar`, `VersionMismatchError` |
| Stage A matcher `expression_region_overlap` | spec §4.1 | **No** | spec §4.1 describes it; no file implements it |
| Stage A matcher `page_region_fallback` | spec §4.1 | **No** | spec §4.1 describes it; no file implements it |
| Stage B matcher `expression_region_overlap` (B) | spec §5.1 | **No** | spec §5.1 describes it; no file implements it |
| Stage B matcher `expression_region_exact` | spec §5.1 | **No** | spec §5.1 describes it; no file implements it |
| Stage B matcher `node_id_replay` | spec §5.1 | **No** | spec §5.1 describes it; no file implements it |
| Stage B matcher `glyph_geometry_match` | spec §5.1 | **No** | spec §5.1 describes it; no file implements it |
| Stage B matcher `expression_region_leak` | spec §5.1 | **No** | spec §5.1 describes it; no file implements it |
| Ambiguity representation | spec §§4.1, 5.1–5.2 | **No** | spec mandates `ambiguous`, `unresolved`, `unverified_regression`; not implemented |
| Relationship geometry | spec §6 | **No** | contract-described only |
| Association-accuracy metrics | spec §7.2 | **No** | metrics defined, no test implementation |
| Existing 16 tests | test file | **Yes** (contract tests only) | `16 passed in 0.08s`; verify they do not call Stage A/B matchers |

---

## 8. Implementation and testing recommendations (for later sessions)

1. **Implement Stage A/B matchers as a separate production surface** (e.g., `scripts/association_matchers.py`), not in `scripts/math_pdf_association.py`. Keep the sidecar writer pristine: sidecar serialization + version enforcement are the delivery layer; matching is the computation layer.
2. **Test division:** contract tests (schema, role mapping, bbox, provenance, idempotence) are separate from association tests (independent discovery vs adjudicated gold). The existing 16 tests stay contract tests.
3. **Inputs:** association matchers must accept per-item inputs (SourceOccurrence, glyph observations, AST node) and produce one record each — not read frozen sidecars.
4. **Gold:** association tests require separately adjudicated gold; the existing test file's hard-coded records do not qualify as gold.
5. **Do not implement now.** The spec above is the freeze and the boundary. Implementation follows the traceable development sequence: capture gold → write Stage A matcher → write Stage B matcher → run contract tests → run association tests → certify accuracy.

---

*Spec status: unchanged since 2026-11-12. No implementation code was produced in this session. No files were created, deleted, or modified. No git commit performed.*
