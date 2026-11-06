# Glyph Catalog Template Matching — P1 Implementation & Evaluation Specification

**Status:** Read-only specification. No source changes, baseline changes, or acceptance claims authorized by this document.

**Date:** 2026-11-03
**Author:** Hermes (with external assessment input)
**Predecessor:** `docs/cross-document-finding-authority-map-2026-11-03.md` (CF-023), `docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md`, `DATASETS/vision_comparison/catalog_audit_p0.json`

---

## 1. Purpose and Scope

This specification defines a read-only implementation and evaluation contract for activating the 3,304-entry glyph catalog as a visual reference corpus for template matching. It does not authorize source changes, baseline modifications, or acceptance claims. Implementation requires separate authorization.

**What this specification does:**
- Defines identity layers, normalization, matching procedure, and evaluation gates.
- Establishes provenance and ambiguity-preservation rules.
- Specifies evaluation populations and tracked outcomes.

**What this specification does not do:**
- Does not replace Pix2Text or Tesseract.
- Does not authorize modification of `vision_comparison_pipeline.py`, `math_symbol_vision_hooks.py`, or any other source file.
- Does not modify the frozen baseline (`baseline_frozen_padding15.jsonl`).
- Does not overwrite original or corrected image clips.
- Does not claim recognition accuracy, semantic fidelity, or acceptance.

---

## 2. Catalog Identity Layers

Three identity layers must be maintained separately. Collapsing them would lose Metamath's naming information or multiply matching work.

### 2.1 Catalog Identity (3,304 records)

Every original catalog entry retains:
- `index`: catalog record index
- `name`: glyph name (e.g., `partial`, `alpha`, `_.0`)
- `zip_file`: original filename
- `format`: `.gif` or `.png`
- `variant_relationship`: regular vs. `_.` small variant

### 2.2 Image Identity (1,595 unique hashes)

Deduplicated pixel content:
- `image_hash`: perceptual hash (16×16 binary resize)
- `original_dimensions`: (width, height) of source image
- `original_format`: `.gif` or `.png`
- `valid`: whether image decodes successfully (3 non-image entries excluded)

### 2.3 Recognition Identity

When a template match succeeds, return **all** applicable catalog names for the matched image identity, not just whichever filename was indexed first. Multiple catalog identities may reference one image identity. Multiple normalized variants may reference one image identity.

### 2.4 Identity Mapping

```
catalog_record (3,304)
    → image_identity (1,595 unique hashes)
    → catalog_identity (all names referencing that hash)
    → normalized_variants (per-image-identity, per-variant-type)
```

---

## 3. Image Decoding and Caching

### 3.1 Exclusions

The three non-image entries (`favicon.ico`, `searchindex.html`, `symbols.html`) must be excluded from all matching operations. They are catalog metadata, not glyph images.

### 3.2 Decoding

- Decode all 3,301 valid images using OpenCV (`cv2.imread`).
- Preserve original dimensions and aspect ratios.
- Do not resize, crop, or transform during initial decode.
- Store decoded images in a read-only cache keyed by `image_hash`.

### 3.3 Caching Contract

- Original decoded images must never be overwritten.
- Cache must be addressable by `image_hash` for efficient retrieval.
- Cache must include original dimensions, format, and catalog identity references.

---

## 4. Normalized Variants

### 4.1 Variant Generation

For each unique image identity, generate controlled normalized variants. Every variant must retain provenance:

| Field | Description |
|---|---|
| `original_image_hash` | Hash of the source image |
| `original_dimensions` | (width, height) of source |
| `transformation_type` | `grayscale`, `binary`, `size_normalized`, `padding_normalized` |
| `transformation_params` | Parameters used (threshold value, target height, padding amount) |
| `resulting_dimensions` | (width, height) after transformation |
| `variant_id` | Unique identifier for this variant |

### 4.2 Variant Types

| Variant | Description | When to use |
|---|---|---|
| Grayscale | Original image converted to single channel | Document crops with antialiasing |
| Binary | Thresholded to two colors | Clean binary comparison |
| Size-normalized | Fixed target height, preserve aspect ratio | Cross-scale matching |
| Padding-normalized | Center on square canvas with fixed dimensions | Template alignment |

### 4.3 Grayscale vs. Threshold Distinction

Because source images are binary (2 colors), grayscale conversion may produce no meaningful additional information. Thresholding is useful for document crops that contain antialiasing or compression artifacts. These are distinct operations and must not be conflated.

### 4.4 Reversibility

No variant may overwrite the original decoded image. All transformations must be reproducible from the original plus the recorded parameters. The original image remains the source of truth.

---

## 5. Size/Role Classification

Dimensions alone cannot reliably distinguish a large operator from an ordinary tall symbol. Classification must use multiple evidence sources.

### 5.1 Candidate Classes

| Class | Initial classification evidence |
|---|---|
| Isolated glyph | Small bounding box and ordinary symbol proportions |
| Large operator | Known catalog identity and/or large operator geometry |
| Fraction bar | Wide, shallow geometry |
| Delimiter | Tall, narrow geometry |
| Composite/ambiguous | Multiple components or uncertain role |

### 5.2 Classification Rules

- These are **candidate classes**, not established ground truth.
- Every glyph must have a classification, but the class may be `composite/ambiguous`.
- Classification must preserve an unclassified route for glyphs that do not fit any candidate class.
- Large operators, fraction bars, and delimiters must not be normalized as ordinary isolated glyphs. Their dimensions and spatial roles carry information.
- Template matching must support separate size/role classes with distinct matching strategies.

### 5.3 Known Large Operators (from catalog audit)

The following catalog names are known large operators and must be classified accordingly:
- `bigcap`, `bigcup`, `bigodot`, `bigoplus`, `bigotimes`, `bigsqcup`, `biguplus`, `bigvee`, `bigwedge`, `coprod`, `prod`, `sum`, `int`, `oint`, `smallint`

### 5.4 Size Thresholds (candidate, not ground truth)

| Width | Height | Candidate class |
|---|---|---|
| ≤ 20px | ≤ 25px | Isolated glyph |
| Any | ≥ 30px, width < height/2 | Delimiter (candidate) |
| ≥ 30px | ≤ 15px | Fraction bar (candidate) |
| ≥ 25px | ≥ 25px | Large operator (candidate) |
| Other | Other | Composite/ambiguous |

These thresholds are starting points for classification. They must be validated against catalog identities and adjudicated ground truth before being treated as reliable.

---

## 6. Template Matching (P1 Core)

### 6.1 Matching Procedure

Normalized cross-correlation (NCC) is the starting mechanism. The comparison procedure must specify:

1. **Sliding-window vs. whole-crop matching**: Template matching is performed as whole-crop comparison (template vs. entire crop) for isolated glyphs. For multi-component regions, sliding-window matching is used to detect individual glyphs within the region.

2. **Unequal dimensions**: When template and crop dimensions differ, the smaller dimension is padded with zero (for binary) or 128 (for grayscale) to match the larger. Alternatively, the template is resized to match the crop using the same interpolation as the variant generation.

3. **Matching scope**: Matching is performed on the entire crop for isolated glyph classification. For complex formulas, matching is performed on segmented regions identified by `detect_math_regions_on_page()`.

4. **Multiple scales**: Search at 0.5×, 1.0×, and 2.0× of the crop's native resolution. Each scale produces a separate similarity score.

5. **Overlapping detections**: When multiple templates match the same region, retain all matches above a threshold. Apply non-maximum suppression only when two matches have IoU > 0.5 and the lower-scoring match is not a different catalog identity.

6. **Score calibration**: NCC scores are similarity measures, not probabilities. Do not label them as "confidence" without calibration against adjudicated ground truth. Report as `similarity_score` (range [−1, 1]).

### 6.2 Matching Output

Each match result must include:

| Field | Description |
|---|---|
| `crop_path` | Path to the source crop image |
| `matched_image_hash` | Hash of the matched catalog image |
| `catalog_names` | All catalog names associated with the matched image hash |
| `similarity_score` | NCC score (range [−1, 1]) |
| `match_scale` | Scale at which best match occurred |
| `variant_type` | Which normalized variant produced the best match |
| `match_method` | `template_ncc` (for P1) |
| `ambiguity_flag` | True if multiple catalog identities share the matched image hash |

### 6.3 Ambiguity Preservation

When multiple catalog identities share the same image hash (21 groups identified in P0), all applicable names must be returned. The system must not select one arbitrarily. Ambiguous matches must be flagged in the output.

---

## 7. Evaluation Protocol

### 7.1 Four-Outcome Test

| Source condition | Correct behavior |
|---|---|
| Genuine stretched glyph | Recognize |
| Genuine stretched glyph | Reject **only if** evidence does not support identity |
| Hallucinated glyph | Reject |
| Hallucinated glyph | Accept **only if** independently supported by source evidence |

### 7.2 Evaluation Populations

| Population | Definition | Candidates |
|---|---|---|
| P1 | Clean glyph recognition | 5 |
| P2 | Border contamination and clipping | 8 |
| P3 | Stretched delimiters and operators | 4 |
| P4 | Inline mathematics and surrounding prose | 2 |
| P5 | Multi-component mathematical structures | 6 |
| P6 | Similar-looking glyph discrimination | 0 (coverage gap) |

- **12-crop frozen regression set**: The 12 crops from `DATASETS/vision_comparison/border_evaluation_results.jsonl`.
- **4 before/after image pairs**: The original/corrected pairs in `DATASETS/vision_comparison/crop_verification_renders/`.

The 4 before/after pairs must not be automatically counted as 4 additional independent samples if they overlap with the 12 crops. Overlap must be documented.

### 7.3 Three Tracked Outcomes

1. **Recognition**: Was the glyph or symbol identified?
2. **Structural reconstruction**: Was its mathematical relationship to neighboring symbols preserved?
3. **Source fidelity**: Does the reconstructed expression agree with the original source?

These are independent measurements. Improvement in one does not imply improvement in another.

### 7.4 Evaluation Gates (Provisional P1 Pilot Thresholds)

The following thresholds are engineering targets for the 12-crop pilot. They are **not** established research standards. The 12-crop regression population is too small to establish general recognition performance. All thresholds must be re-evaluated when the population expands.

| Gate | Definition | Criteria | Status |
|---|---|---|---|
| Functional | Engine produces candidates, scores, and provenance | Runs without error; output schema matches §6.2 | Pilot target |
| Retrieval quality | Known reference glyphs appear in candidate set at measurable rate | ≥ 50% of adjudicated glyphs appear in top-5 candidates | Provisional |
| Accuracy | Candidates correctly identified against adjudicated evidence | ≥ 70% of top-1 candidates match adjudicated verdict | Provisional |
| Acceptance | Catalog contributes genuine recoveries without unacceptable false positives | Net recovery > 0; false positive rate < 25% | Provisional |

### 7.4.1 Net Recovery Definition

Net recovery must be computed as:

$$\text{Net Recovery} = \text{New Correct Recoveries} - \text{New False Positives}$$

Both counts must be reported independently. A positive net result alone can hide important regressions. The full report must include:

| Metric | Definition |
|---|---|
| New Correct Recoveries | Symbols missed by existing OCR that are correctly identified by catalog matching |
| New False Positives | Symbols incorrectly identified by catalog matching that existing OCR did not report |
| Regressions | Previously recognized symbols that become incorrect after adding catalog evidence |
| Unresolved | Existing OCR errors that catalog matching does not address |

### 7.4.2 False-Positive Denominator Definitions

Two distinct false-positive measures must be reported. They measure different things and must not be treated as interchangeable.

**FPR (false positive rate):**

$$FPR = \frac{FP}{FP + TN}$$

Where FP = catalog false positives and TN = true negatives (symbols correctly not reported).

**Candidate Error Rate:**

$$\text{Candidate Error Rate} = \frac{\text{Incorrect Accepted Candidates}}{\text{All Accepted Candidates}}$$

Report both. A candidate retrieval system may have a low FPR (few false positives relative to the full population) but a high candidate error rate (many false positives among the candidates it actually returns).

### 7.4.3 OCR Baseline Comparison (Paired Evaluation)

The acceptance gate must measure **incremental contribution**, not merely whether template matching works. Paired evaluation on the same crops is required.

| Recognition path | Evaluation |
|---|---|
| Pix2Text alone | Baseline |
| Tesseract alone | Baseline |
| Catalog matching alone | Independent contribution |
| OCR + catalog evidence | Combined contribution |

This reveals whether the catalog:
- Recovers symbols that existing OCR misses (genuine contribution).
- Duplicates existing OCR results (no incremental value).
- Introduces new errors (negative contribution).

Original OCR outputs must be preserved. Do not modify or overwrite them during evaluation.

The retrieval-quality gate is placed between functional operation and accuracy acceptance. A technically functioning matcher that returns poor candidates must not be mistaken for a successful recognition system.

### 7.5 Prohibited Evaluation Practices

- Do not use OCR-generated labels as ground truth for P6 (similar-looking glyph discrimination).
- Do not count `INTENDED_PARTIAL_FRAGMENT` as OCR failure.
- Do not reconcile historical numeric results (448 solved, 457 solvable, 448 recovery PASS) by assumption.
- Do not overwrite original clips, corrected clips, or frozen baseline during evaluation.
- Do not modify `baseline_frozen_padding15.jsonl`.

### 7.5.1 Cross-Name Hash Group Visibility

The 21 visually identical cross-name hash groups identified in P0 (§Appendix A) must remain visible in all evaluation reports. These are not merely duplicate storage entries; they demonstrate that image identity does not necessarily establish semantic identity. Evaluation must track whether recognition decisions treat these groups as ambiguous (correct) or collapse them to a single name (incorrect).

---

## 8. Catalog as Evidence Source, Not Authority

### 8.1 Architectural Principle

The catalog must become an **independent source of visual evidence**, not an authority that silently overrides OCR or mathematical structure. It is a third evidence source alongside Pix2Text and Tesseract.

### 8.2 Evidence Flow

```
Crop region
    ├── Pix2Text OCR → candidate symbols + confidence
    ├── Tesseract OCR → candidate symbols + confidence
    └── Catalog template matching → candidate symbols + similarity scores
            ↓
    Contextual ranking (LaTeX grammar + spatial relationships + neighboring symbols)
            ↓
    Evidence-preserving output (candidate identities, scores, source crop, recognition method, ambiguity, confidence)
```

### 8.3 Conflict Resolution

When catalog matching disagrees with OCR:
- Preserve both results in the output.
- Flag the disagreement as `recognition_conflict`.
- Do not silently select one over the other.
- Let contextual ranking (§8.2) determine the final candidate order, not a hardcoded priority.

---

## 9. What P1 Does NOT Do

- Does not replace Pix2Text or Tesseract.
- Does not train a neural classifier.
- Does not modify the frozen baseline.
- Does not overwrite original or corrected clips.
- Does not claim recognition accuracy, semantic fidelity, or acceptance.
- Does not modify source code (implementation requires separate authorization).

---

## 10. Authorization Boundary

This document is a **read-only specification**. It does not authorize:
- Source code modifications (any file in `scripts/`, `tests/`, `DATASETS/`).
- Baseline modifications (`baseline_frozen_padding15.jsonl`).
- Acceptance claims for any gate in §7.4.
- Deployment or integration into the live pipeline.

**Implementation requires a separate, explicit authorization** after this specification is reviewed.

---

## Appendix A: P0 Audit Summary (reference)

| Metric | Value |
|---|---|
| Total catalog entries | 3,304 |
| Valid image records | 3,301 |
| Non-image entries (excluded) | 3 (favicon.ico, searchindex.html, symbols.html) |
| Unique names | 2,120 |
| Names with duplicates | 1,184 |
| Unique image hashes | 1,595 |
| Duplicate image instances | 1,706 |
| Unique image sizes | 75 |
| Hash collisions (different names) | 21 |
| Formats | 2,118 GIF + 1,183 PNG |
| Size range | 3–470px wide, 15–1,027px tall |

Audit report: `DATASETS/vision_comparison/catalog_audit_p0.json`
Audit script: `scripts/audit_glyph_catalog.py`

## Appendix B: Research References

1. **Symbol Spotting for Architectural Drawings** (2019, University of Victoria) — template matching, clutter-tolerant cross-correlation, precision/recall in dense drawings.
2. **Graph-to-Graph: Accurate and Interpretable Mathematical Expression Recognition** (AAAI 2021) — spatial and symbolic correspondence.
3. **SSAN: Symbol Spatial-Aware Network** (AAAI 2025) — spatial distribution and symbol alignment.
4. **Seeing Symbols, Missing Structure** (PMLR 2026) — symbol-level recognition vs. expression-level structural errors.
5. **Normalized cross-correlation** — standard template matching baseline; multiple scales and variants required for robustness.
6. **HOG + geometric descriptors** — aspect ratio, Hu moments, connected components, skeleton features, distance transforms for rendering-tolerant matching.

## Appendix C: Related Documents

| Document | Relationship |
|---|---|
| `docs/cross-document-finding-authority-map-2026-11-03.md` | CF-023 (vision pipeline stretched symbols/borders) |
| `docs/vision-stretched-symbols-border-recognition-audit-2026-11-03.md` | 4 gaps identified, all closed |
| `docs/frozen-regression-evaluation-mapping-2026-11-03.md` | 6 populations, 21 candidates, baseline protection rules |
| `docs/frozen-regression-execution-results-2026-11-03.md` | Border detection 9/12 (75%), 12 ballooned PNGs |
| `scripts/vision_comparison_pipeline.py` | Current vision pipeline (10 functions + bracket tracking) |
| `scripts/run_border_evaluation.py` | Border detection + ballooning execution |
| `scripts/audit_glyph_catalog.py` | P0 catalog audit script |
| `DATASETS/vision_comparison/catalog_audit_p0.json` | P0 audit results |
| `symbols/symbols/symbols.zip` | Source archive for 3,304-glyph catalog |
| `DATASETS/unified_manifest.json` | Catalog manifest with metadata and aliases |