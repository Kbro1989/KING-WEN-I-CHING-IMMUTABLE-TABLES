# Cross-Reference Audit: golden · delimiter · coordinate

**Date:** 2026-11-11
**Branch:** `v2-remediation` (befa228927)
**Purpose:** Cross-referential audit of three terms across `.md`, `.json`, and `.py` files — where each is mentioned, what it is located in, and what imports/exports reference it.
**Status:** Source-level audit; no files modified.

---

## Table of Contents

1. [Scope and Method](#scope-and-method)
2. [Three-Term Architectural Distinction](#three-term-architectural-distinction)
3. [Golden — Cross-Reference Map](#golden--cross-reference-map)
4. [Delimiter — Cross-Reference Map](#delimiter--cross-reference-map)
5. [Coordinate — Cross-Reference Map](#coordinate--cross-reference-map)
6. [Delimiter Ecosystem Import/Export Graph](#delimiter-ecosystem-importexport-graph)
7. [Population Separation Diagram](#population-separation-diagram)
8. [G0–G5 Acceptance Gates](#g0-g5-acceptance-gates)
9. [Completion States and Contract](#completion-states-and-contract)
10. [Open Questions](#open-questions)

---

## Scope and Method

This audit performs a **cross-reference audit** over the KING-WEN-I-CHING-IMMUTABLE-TABLES repository. For each term (`golden`, `delimiter`, `coordinate`), the audit records:

- Which files mention the term.
- What role the term plays in that file.
- Which `.py` files import or export components related to the term.
- Which `.json` files store data derived from or about the term.

**Verification method:** read_file/grep on disk, not inference from proposal diagrams. All import edges are confirmed against actual Python imports on disk.

---

## Three-Term Architectural Distinction

| Term | Meaning in Repository | What It Does NOT Establish |
|------|----------------------|---------------------------|
| `golden` | Frozen reference authority, adjudicated truth, evaluator acceptance criteria | That a candidate or implementation is correct |
| `delimiter` | Structural recognition, pairing, nesting, enclosure, identity recovery | That a visual candidate was independently detected |
| `coordinate` | Spatial observations, localization, transformations, geometry | That a coordinate is authoritative or correctly interpreted |

### Important Distinction

`golden` in this repository refers to **frozen reference authority**, not `golden-ratio` mathematics. The `golden-ratio` harmonic appears in `KING_WEN_LINK_ACOUSTIC_PROTOCOL.md` and `interop-algebra-empirical-graph.md`; it shares the keyword but not the authority relationship.

### Coordinate Domains

Two distinct coordinate systems exist and should not be grouped merely because both use coordinates:

1. **PDF page coordinates** — used by `targeted_math_detector.py` (`bbox_pdf_pt`), `mathml_parser.py`, and the visual extraction pipeline. Coordinate space convention: `pdf_points` vs `rendered_pixels`.
2. **Möbius/Riemann sphere coordinates** — used by `kingwen_mobius_sphere.py`, `generate_avatar_meshes.py`, and the 3D avatar pipeline. These are mathematical/spatial coordinates for the quantum avatar field, not spatial observations of PDF content.

---

## Golden — Cross-Reference Map

### Summary

| File type | Count | Notes |
|-----------|-------|-------|
| `.md` | 9 | Mostly documentation/audit files |
| `.json` | 4 | Staged classification caches, execution topology |
| `.py` | 0 | No Python files use `golden` as a code symbol |

### `.md` References

| File | Role |
|------|------|
| `docs/golden-standard-audit-matrix.md` | **Central authority matrix** — 8 HIGH-authority frozen files, 55 total across 5 categories |
| `docs/audit-checklist-2026-11-06.md` | References golden matrix; confirms 8 HIGH-authority files; frozen/identity correct |
| `docs/method-ocr-evaluation-corrected-2026-11-07.md` | Classifies RapidOCR as `GOLDEN_CANDIDATE` (then corrects: RapidOCR is NOT a golden candidate) |
| `docs/method-original-pipeline-recovery-2026-11-07.md` | "Near-golden" disposition; "Golden Blocker Summary" |
| `docs/KING_WEN_LINK_ACOUSTIC_PROTOCOL.md` | "Golden-ratio harmonics" — ratio $r_\ell = 1.0 + \left(\frac{\ell-1}{6.0}\right) \times 0.618$; CRC tone $f_{crc} = f_0 \times 1.618$ |
| `docs/interop-algebra-empirical-graph.md` | "Golden-ratio line harmonics" |
| `docs/method-dav2-producer-contract-audit-2026-11-07.md` | 4-line report stamp: "Golden certification | Not established" |
| `docs/hex43_producer_consumer_trace.md` | `k_color_map.blendedHex → "#C58E09"` from "golden/earth palette" |

### `.json` References

| File | Role |
|------|------|
| `cache/staged_classification.json` — 2 entries (line 6793: `docs/golden-standard-audit-matrix.md` as relative_path) |
| `inventory/execution_topology.json` — references golden-standard matrix |
| `cache/staged_classification_v2.json` — duplicate classification from staged source |

### `.py` References

No `.py` file contains `golden` as a code symbol. The word appears only in documentation and data-cache files.

---

## Delimiter — Cross-Reference Map

### Summary

| File type | Count | Notes |
|-----------|-------|-------|
| `.md` | 30 | Mostly documentation/audit files |
| `.json` | 8 | Tracking artifacts, cache files, test outputs |
| `.py` | 66 | The largest population — the delimiter ecosystem |

### `.md` References

| File | Role |
|------|------|
| `docs/batch-delimiter-integration-audit-2026-11-06.md` | **The integration audit** — producer/consumer map of the entire delimiter ecosystem |
| `docs/audit-checklist-2026-11-06.md` | Audit checklist — calls out the integration gap in the visual pipeline |
| `docs/CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md` | **The frozen acceptance spec** — 7 test families, 5 conjunctive gates |
| `docs/golden-standard-audit-matrix.md` | Category 2 (structural gold) and Category 3 (evaluator integrity), including delimiter test families |
| `docs/component-contract-audit-and-methodological-assessment-2026-11-06.md` | Visual-layer output boundary audit — coordinates, font, char data |
| `docs/numerical-extraction-vision-pipeline.md` | Extraction pipeline documentation |
| `docs/CROSS_PAPER_SOURCE_SELECTION_RECONNAISSANCE_V1.md` | Gold annotation generation, coordinate lineage |

### `.json` References

| File | Role |
|------|------|
| `DATASETS/delimiter_tracking.json` | **Tracking contract** (frozen — do not modify); 3,329 total, 219 tracked, 191 paired, 28 big delimiters |
| `DATASETS/delimiter_identity_audit.json` | Identity-loss audit |
| `delimiter_structural_recovery_report.json` | Recovery report |
| `DATASETS/structural_preservation/cross_paper_delimiter_generalization_spec_v1.json` | JSON spec for delimiter generalization (referenced by `CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md`) |
| `geometry_generalization_results.json` | Geometry generalization test results |

### `.py` References

| Module | Exports | Imported by |
|--------|---------|-------------|
| `scripts/delimiter_identity.py` | `normalize_latex_norms()`, `DelimiterInferer`, `infer_delimiters()` | `mathml_parser.py`, `math_recovery_tool.py` |
| `scripts/delimiter_aware_structural_recovery.py` | V1 engine (pairing, nesting, enclosure) | `evaluate_cross_paper_v2_strict.py`, `evaluate_rahmani_generalization.py`, `evaluate_v1_v2_cross_paper_comparison.py`, `e2e_math_pipeline.py` |
| `scripts/v2_delimiter_aware_structural_recovery.py` | V2 engine (alias `engine_v2`) | `evaluate_cross_paper_v2_strict.py`, `evaluate_v1_v2_cross_paper_comparison.py` |
| `scripts/delimiter_inference.py` | `DelimiterInferer`, `infer_delimiters()` | `delimiter_inference.py` (self-import) |

### The Delimiter Import Graph

```
targeted_math_detector.py  →  font_aware_math_classifier.py  →  
delimiter_aware_structural_recovery.py  →  delimiter_identity.py
```

### The Disconnect

- `batch_math_pipeline.py` never calls `targeted_math_detector.py`
- `pdf_visual_analysis_layer.py` never calls `delimiter_aware_structural_recovery.py`
- The visual-detection components exist but are not wired into the batch accounting

---

## Coordinate — Cross-Reference Map

### Summary

| File type | Count | Notes |
|-----------|-------|-------|
| `.md` | 60+ | The most common of the three terms |
| `.json` | 3 | Cache files, fix scripts |
| `.py` | 45+ | The largest population — coordinate handling pervades the 3D and visual pipelines |

### `.md` References

| File | Role |
|------|------|
| `docs/full-page-text-math-extraction-cross-reference-plan-2026-11-04.md` | All bboxes must record which coordinate space they occupy (`coord_space: pdf_points` or `rendered_pixels`) |
| `docs/component-contract-audit-and-methodological-assessment-2026-11-06.md` | Coordinate contract: candidates must retain original page coordinates; interpretation cannot overwrite observation |
| `docs/CROSS_PAPER_DELIMITER_GENERALIZATION_PROTOCOL_V1.md` | Continuation symbols mapped to grid coordinates |
| `docs/cross-reference-audit-2026-11-02.md` | Two divergent 3D coordinate systems (B7 — OPEN) |
| `docs/diagnose-system-models-14-research-continuity-record-2026-11-09.md` | Gold delimiter coordinates — oracle-conditioned evaluator |
| `docs/context-preservation-implementation-evaluation-spec-2026-11-04.md` | Candidate coordinates must be preserved (original_bbox, region_bbox) |
| `docs/glyph-catalog-template-matching-p1-spec-2026-11-03.md` | Spatial localization |
| `docs/cross-reference-authorization-boundary-2026-11-04.md` | Coordinates retain their coordinate system, origin, units, and rendering scale |
| `docs/kings-wen-function-coverage-audit-report-2026-11-06.md` | Coverage report using coordinates |
| `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md` | Riemann/Möbius avatar coordinate backend |
| `docs/B4-PARAM-SPEC-KW-B4-PARAM-001.md` | Tensor coordinates and their input index tuple |
| `docs/hamiltonian-equation-comparison-2026-10-27.md` | Canonical coordinates/momenta in Hamiltonian construction |

### `.json` References

| File | Role |
|------|------|
| `cache/audit/pre_repair_snapshot_2026-10-22/unified_manifest.json.bak` | Backup with coordinate references |
| `cache/scripts/fix2.py`, `cache/scripts/fix_final.py`, `cache/scripts/fix_pipeline.py` | Fix scripts with coordinate handling |

### `.py` References

| Module | Coordinate Handling |
|--------|------|
| `scripts/targeted_math_detector.py` | `extract_raw_observations()` returns `bbox_pdf_pt` per candidate |
| `scripts/kingwen_mobius_sphere.py` | Möbius sphere / Riemann sphere coordinates |
| `scripts/generate_avatar_meshes.py` | Avatar mesh geometry coordinates |
| `scripts/generate_sovereign_world.py` | Sovereign world grid coordinates (from OEIS formula) |
| `scripts/kingwen_state_transition.py` | State-transition coordinates |
| `scripts/update_3d_kits_with_quantum_wavepackets.py` | 3D kit wavepacket coordinates |

**Key coordinate-contract requirement** (from `docs/component-contract-audit-and-methodological-assessment-2026-11-06.md`):

```text
The visual layer's summary record does not contain font or original
coordinates for each candidate; the recovery engine expects those fields.
Every candidate must retain its original page coordinates.
No downstream step may modify the original candidate coordinates,
pixel evidence, or font data.
```

---

## Delimiter Ecosystem Import/Export Graph

```
targeted_math_detector.py
  └── extract_raw_observations()  →  per-glyph records with font, coordinates, char data
        │
        ▼
font_aware_math_classifier.py
  │  (classification: math/op/bigger/another/normal)
        │
        ▼
delimiter_aware_structural_recovery.py  (V1 engine)
  │  (pairing: open/close/non-pair, nesting, enclosure)
  │  imports: normalize_latex_norms from delimiter_identity
        │
        ▼
delimiter_identity.py  (identity classification)
  │  exports: normalize_latex_norms(), DelimiterInferer, infer_delimiters()
        │
        ▼
mathml_parser.py  ←  (imports delimiter_identity)
math_recovery_tool.py  ←  (imports normalize_latex_norms from delimiter_identity)
```

### Consumer Modules

`evaluate_cross_paper_v2_strict.py`, `evaluate_rahmani_generalization.py`, `evaluate_v1_v2_cross_paper_comparison.py`, `e2e_math_pipeline.py`

### The Disconnect (from `batch-delimiter-integration-audit-2026-11-06.md`)

- `batch_math_pipeline.py` never calls `targeted_math_detector.py`
- `pdf_visual_analysis_layer.py` never calls `delimiter_aware_structural_recovery.py`

---

## Population Separation Diagram

```
paper_id
  ├── equation_population
  │     └── equation_record_id
  │
  └── visual_population
        └── visual_observation_id
              └── delimiter_candidate_id
                    └── adjudication_id
```

This permits cross-population analysis without treating:
- an equation string as visual detection evidence, or
- a visual candidate as a validated equation.

---

## G0–G5 Acceptance Gates

| Gate | Requirement | Conjunction |
|------|-------------|-------------|
| G0 | Independent engine prediction — predictions generated without gold leakage | Mandatory |
| G1 | Comparable localization | Mandatory |
| G2 | Four-edge clearance and contamination | Mandatory |
| G3 | Direct semantic comparison | Mandatory |
| G4 | Real adversarial perturbations through production paths | Mandatory |
| G5 | Three-state gate verdicts and correct denominator accounting | Mandatory |

**All six gates must pass for `CERTIFIED`.** A passing unit test cannot certify a corpus-level gate.

---

## Completion States and Contract

| State | Meaning |
|-------|---------|
| `SPECIFIED` | Contract and schemas defined |
| `IMPLEMENTED` | Components and interfaces exist |
| `INTEGRATED` | End-to-end execution and persistence demonstrated |
| `REPRODUCIBLE` | Independent rerun reproduces the recorded evidence |
| `CERTIFIED` | Applicable G0–G5 requirements passed |

A successful end-to-end run does not automatically imply certification. A passing unit test cannot certify a corpus-level gate.

### Required Completion Criteria for Integration

1. The resource schema is documented from actual serialized contents.
2. The reported population is reconciled against observed resource identities.
3. The six-variant and phase-resource classifications have evidence.
4. The selected sample is reproducible and registry-comparable.
5. The scene/resource dependency graph is constructed from actual references.
6. Generator lineage is established where evidence exists and explicitly marked unknown elsewhere.
7. Resource, mathematical, presentation, and provenance validation results remain independently reportable.

---

## Open Questions

1. **Delimiter inference self-import:** `scripts/delimiter_inference.py` line 17 contains `from delimiter_inference import DelimiterInferer, infer_delimiters`. This appears to be a documentation/listing artifact (the actual module imports from `dataclasses` and `typing` on lines 22–23). Verify whether this is a genuine self-import or a stale listing.

2. **Alias naming consistency:** `evaluate_cross_paper_v2_strict.py` imports `delimiter_aware_structural_recovery as engine_v1` and `v2_delimiter_aware_structural_recovery as engine_v2`. The module file is `delimiter_aware_structural_recovery.py` but the alias is `engine_v1`. Verify this naming is intentional and consistent across all consumers.

3. **Batch pipeline disconnection:** `batch_math_pipeline.py` never calls `targeted_math_detector.py`. The visual-detection components exist but are not wired into the batch accounting. This is the primary gap identified by `batch-delimiter-integration-audit-2026-11-06.md`.

4. **Coordinate-space conversion:** No recorded transformation exists between `pdf_points` and `rendered_pixels`. Any conversion requires an explicit transformation including scale, rotation, and page-origin conventions. Confirm whether `rendered_pixels` has ever been converted to `pdf_points` in any existing pipeline step.

5. **Golden vs. derivation independence:** The G0 concern remains: gold coordinates cannot be used to construct the predictions that are subsequently evaluated against those same coordinates. Confirm whether `baseline_gold_coordinates.json` has ever been used as a prediction input.

---

## Files Alive at Completion

| File | Status |
|------|--------|
| `docs/delimiter-corpus-integration-contract-2026-11-11.md` | To be written before integration code |
| `scripts/delimiter_corpus_integration.py` | To be written after contract approval |
| `docs/golden-standard-audit-matrix.md` | Existing; updated with integration audit (per `batch-delimiter-integration-audit-2026-11-06.md`) |

---

*This document is a read-only audit report. No repository files were modified during the audit.*
