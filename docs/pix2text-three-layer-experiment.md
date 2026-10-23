# Pix2Text Three-Layer Glyph Recognition Experiment

**Status:** Experimental design with reference library documented
**Date:** 2026-10-20
**Programs:** King Wen math pipeline (KING-WEN-I-CHING-IMMUTABLE-TABLES) vs P2T/Pix2Text

---

## 1. Purpose

Compare Pix2Text (vision-based) against the King Wen parser (source-aware structural) on rendered equation crops. The goal is NOT to claim one is better than the other. The goal is to measure three independent capabilities:

1. Glyph recognition (identifying symbols against named references)
2. Expression reconstruction (converting rendered crops to LaTeX)
3. Source fidelity (agreement between reconstructed and source)

## 2. Reference Library

### Metamath HTML Corpus

**File:** `DATASETS/GIF-and-PNG-Images-for-Math-Symbols.html`

| Property | Value |
|----------|-------|
| HTML source size | 289,604 bytes |
| Symbol entries (`<area>` chart tags) | 1,182 |
| Symbol name extraction | alt/title fields, 1,182/1,182 consistent |
| Dimensions (coords attribute) | Present in all 1,182 |
| Local image files | 29 GIF files on disk |
| PNG references | 0 |
| Remote (metamath.org) hrefs | 1,158 (98%) |
| Local hrefs | 24 (2%) |

**Reference glyph library:** The 29 local GIF files serve as the reference glyph library for Layer 1 (glyph recognition). Each has a symbolic name from its filename.

**Stencil images:** The 29 GIFs are at:
- `DATASETS/GIF-and-PNG-Images-for-Math-Symbols_files/2.gif`
- `DATASETS/GIF-and-PNG-Images-for-Math-Symbols_files/ch.gif`
- `DATASETS/GIF-and-PNG-Images-for-Math-Symbols_files/d.gif`
- ... and 25 more

---

## 3. Evaluation Examples

Rendered expression crops from source papers. Excluded from model tuning: the frozen 420-paper validation sample.

**Required recording per crop:**
- Source paper (arXiv ID)
- Page number
- Bounding box (x1, y1, x2, y2)
- Render configuration (model version, input size, resolution)
- Annotation provenance (source LaTeX/TeX, kernel, extraction method)
- Pix2Text reconstructed LaTeX
- King Wen AST node match

---

## 4. Three-Layer Scoring

Keep scores separate. A correct glyph label does not prove correct expression structure, and correct LaTeX text does not prove the parser's AST preserves the intended mathematics.

### Layer 1: Glyph Recognition
**Question:** Can the system identify individual rendered symbols against the named reference glyphs?

**Metric:** Top-1 accuracy, applicable top-k accuracy

### Layer 2: Expression Reconstruction
**Question:** Can Pix2Text turn rendered equation crops into LaTeX that preserves symbols, grouping, fractions, superscripts, subscripts, and limits?

**Metrics:**
- Symbol preservation rate
- Grouping fidelity
- Fraction preservation
- Superscript/subscript fidelity
- Limit placement fidelity

**Metric:** Expression-level precision/recall/F1

### Layer 3: Source Fidelity
**Question:** Does the reconstructed expression agree with the source LaTeX/MathML and the parser's AST?

**Metrics:**
- AST node-level agreement
- Relation-type agreement (relation, approximately, similar, equivalent, etc.)
- Bound-variable agreement

**Metric:** Source-fidelity rate (fraction of AST nodes matching source)

---

## 5. Blocked: Pix2Text Import Compatibility

**Status:** BLOCKED — not actionable at this stage

Pix2Text 1.1.7 requires `rapidocr 3.10.0` (already installed). But the installed `rapidocr` 3.10.0 doesn't export `resolve_model_key` from `rapidocr.utils.model_resolver`. Pix2Text's `layout_parser.py` imports this function but it doesn't exist in the installed version.

**Workaround options:**
1. Downgrade rapidocr to a version that has `resolve_model_key`
2. Patch `pix2text/layout_parser.py` to not import `resolve_model_key` (or provide a shim)
3. Upgrade Pix2Text to a version that works with rapidocr 3.10.0

This is a version-compatible issue, not a "not installed" issue. Pix2Text is installed; the import needs a fix before the experiment can run.

---

## 6. Verifiable Facts

| Item | Value | Evidence |
|------|-------|----------|
| King Wen repo files | 293,779 | Folder properties |
| King Wen repo size | 3.38 GB | Folder properties |
| Folder attributes | Read-only | Folder properties |
| Pix2Text repo latest commit | `f52e671` | GitHub |
| Pix2Text upstream | `breezedeus/Pix2Text` | GitHub |
| Pix2Text version installed | 1.1.7 | setuptools metadata |
| rapidocr version (after fix) | 3.9.2 | downgraded from 3.10.0 per Option 1 (recommended) |
| Resolved import error | rapidocr>=3.10.0 requires `resolve_model_key` in `rapidocr.utils.model_resolver`; Pix2Text 1.1.7 expects older API. Downgrade to rapidocr<3.10.0 resolves the ImportError. | Confirmed via `from rapidocr.utils.model_resolver import resolve_model_key` |
| End-to-end processing | Working | `Pix2Text()` initializes with default config; `recognize_text()` accepts image paths (not LaTeX strings) |
| Metamath corpus symbol count | 1,182 | HTML `<area>` chart tags |
| Metamath local image count | 29 | GIF files on disk |
| Metamath remote hrefs | 1,158 | HTML href analysis |
| Metamath PNG hrefs | 0 | HTML href analysis |
| Symbols.zip catalog | 3,304 glyphs | Pipeline reference library (`symbols_zip_catalog` in manifest) |
| Vision pipeline run | 4 processed → 4 recognized (image_region, 0 failed) | `python scripts/vision_comparison_pipeline.py --paper 1907.04931 --max-per-paper 4` |
| Crop method | PyMuPDF pixmap → OpenCV decode | Adaptive zoom pixmap decoded to NumPy array |
| Recognize formula | `recognize_formula(crop)` | Accepts NumPy array; internal tempfile encapsulation with str/dict return handling |
| HTML/PDF separation | Distinct inputs | HTML = source-aware parse; PDF = vision crop; symbols.zip = reference catalog |
| OpenJarvis path fix | Line 271 of `docs/cross-verification-checklist-2026-09-01.md` | "OpenJarvas" → "OpenJarvis" fixed |

---

---

## 7. Open Questions

| Question | Test Design | Expected Output |
|----------|-------------|-----------------|
| Does Pix2Text reliably preserve `munderover` limit placement? | Run Pix2Text on rendered expression crops with known `munderover` structures | Precision/recall per structure type |
| Does Pix2Text substitute symbols (Σ vs σ, l vs 1, = vs ≡)? | Use glyph manifest (1,182 entries) as reference | Confusion matrix with error rates |
| Does the vision path complement the source parser? | Compare detection rates: source parser finds errors in source; vision finds errors in rendering | Complementary detection counts |
| What is the `munderover` handling in Pix2Text output? | Parse Pix2Text output for limit expressions | Whether limits are preserved as text |

---

## 8. Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| This assessment | `docs/pix2text-assessment-2026-10-20.md` | Structural comparison document |
| Observation log | `DATASETS/math_symbols/references/pix2text_observation_log.jsonl` | Layer-by-layer observation records |
| Crop metadata | `DATASETS/math_symbols/references/crop_metadata.jsonl` | Source paper/page/bbox/render provenance |
| Pix2Text output | `DATASETS/math_symbols/references/p2t_output.jsonl` | Layer 2 reconstruction results |

---

## 9. Verification Requirements

Before citing any specific test count or error rate:

1. Re-run `test_structural_survival.py` and confirm the actual suite count
2. Identify the exact evaluation command executed
3. Log the command output with timestamps
4. Record any discrepancies between prior session claims and fresh verification
