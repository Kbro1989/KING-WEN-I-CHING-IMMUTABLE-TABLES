# King Wen Math Pipeline vs Pix2Text — Architectural Assessment

**Status:** Technical assessment (source-aware structural pipeline vs vision-based baseline)
**Date:** 2026-10-20
**Programs:** KING-WEN-I-CHING-IMMUTABLE-TABLES (King Wen math pipeline) vs Kbro1989/Pix2Text

---

## 1. Central Conclusion

Pix2Text is an independent visual-recognition baseline. King Wen's source-aware structural pipeline serves a different role. The strongest claim is not that King Wen is categorically better; it is that King Wen has a **source-aware structural pipeline** (input: arXiv HTML MathML + LaTeX source), while Pix2Text provides an **independent vision-based path** that can reveal errors the source parser alone cannot detect.

---

## 2. Corrected Claim Register

Claims are classified into three categories: **Verified Fact**, **Reported Test Result**, and **Hypothesis**.

| Claim | Classification | Correction / Qualification |
|-------|----------------|---------------------------|
| Pix2Text is not a replacement for the MathML parser | **Verified Fact** (architectural) | Image recognition and source-aware parsing have different inputs, failure modes, and outputs. |
| King Wen parses 991 equations from a specific arXiv HTML document | **Verified Fact** (document-specific) | The 991 count applies to the specific arXiv HTML document cross-examined in a prior session (2605.00155). It is not a corpus-wide claim. |
| Pix2Text has no structural corpus comparable to King Wen | **Verified Fact** (documentation-level) | The cited Pix2Text documentation does not establish a structural ground-truth corpus comparable to King Wen's (glyph manifest + crop manifests + 991-equation HTML corpus). Absence from documentation does not prove none exists. |
| `munderover` has no equivalent in Pix2Text | **Hypothesis** (testable) | Pix2Text's LaTeX output can express limits, but whether it recognizes and preserves `munderover`-style limit placement reliably requires controlled testing. |
| `mathml_parser.py` enforcement: 17/17 tests pass | **Repository/Test claim** (verify before citing) | Prior context reported a separate 24/24 structural-survival suite. The exact suite and command should be identified and re-run before this count is cited in a written assessment. |
| Pix2Text substitutes symbols or misrepresents relationships | **Hypothesis** (testable) | Plausible failure modes of vision-based math OCR, but no measured error rates on any held-out set have been reported. |
| The 1,182-entry glyph manifest provides ground truth | **Verified Fact** (partial) | The manifest provides glyph-reference labels. It does not, by itself, establish an equation's semantic role or the correctness of an entire mathematical expression. |

---

## 3. Three-Layer Comparison Framework

Structure the visual-recognition comparison into three independent layers. Keep scores separated.

### Layer 1: Glyph Recognition
**Question:** Can the system identify individual rendered symbols against the named reference glyphs?

**Inputs:** Rendered equation crops from source PDFs
**Reference:** Metamath HTML corpus image assets (`DATASETS/GIF-and-PNG-Images-for-Math-Symbols.html` + local GIF/PNG files)

**Metric:** Top-1 glyph accuracy, applicable top-k accuracy per symbol type
**Ground truth:** Named reference glyphs in the Metamath HTML (1,182 entries with alt/title names)

**What is measured:** Independent symbol recognition, independent of expression structure

---

### Layer 2: Expression Reconstruction
**Question:** Can Pix2Text turn rendered equation crops into LaTeX that preserves symbols, grouping, fractions, superscripts, subscripts, and limits?

**Inputs:** Rendered expression crops
**Reference:** Source LaTeX/MathML + parser AST (King Wen's AST)

**Metrics (recorded separately from Layer 1):**
- Symbol preservation rate (fraction of symbols correctly transcribed)
- Grouping fidelity (parentheses, braces preserved)
- Fraction preservation (numerator/denominator spatial relations)
- Superscript/subscript fidelity
- Limit placement fidelity (munder/mover/munderover structure)

**Metric:** Expression-level precision/recall/F1 against source AST

**What is measured:** Visual reconstruction of math structure independent of source parser

---

### Layer 3: Source Fidelity
**Question:** Does the reconstructed expression agree with the source LaTeX/MathML and the parser's AST?

**Inputs:** Reconstructed LaTeX (from Pix2Text) + source MathML/LaTeX
**Reference:** King Wen's parser AST (semantic ground truth)

**Metrics:**
- AST node-level agreement
- Relation-type agreement (relation, approximately, similar, equivalent, etc.)
- Bound-variable agreement (bound variables, free variables)

**Metric:** Source-fidelity rate (fraction of AST nodes matching source)

**What is measured:** How well the vision output agrees with source structure — this is where the vision path detects errors the source parser alone cannot see

---

## 4. Evaluation Design

### Reference Library
- Use the **Metamodel HTML corpus images** as the reference glyph library
- Use **rendered crops from source papers** as evaluation examples
- Record, for each crop: source paper, page, bounding box, render configuration, annotation provenance

### Held-Out Sample
- The frozen 420-paper validation sample is **excluded from model tuning** and used only for final evaluation
- Development data (separate from held-out) is used for threshold selection

### Property Isolation
- When measuring Pix2Text errors, keep environmental variables controlled: render resolution, model version, input size
- Do not attribute errors to paper quality or image quality without measuring those dimensions separately

---

## 5. Verifiable Facts (Verified in This Session)

| Item | Value | Evidence |
|------|-------|----------|
| King Wen repo tracked files | 293,779 | Folder properties: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES` |
| King Wen repo size | 3.38 GB (3,632,799,892 bytes) | Folder properties |
| Folder attributes | Read-only | Folder properties "Attributes" = Read-only |
| Pix2Text latest commit | `f52e671` | GitHub: `Kbro1989/Pix2Text` |
| Pix2Text upstream | `breezedeus/Pix2Text` | GitHub: `breezedeus/Pix2Text` (533 commits) |
| Pix2Text supported inputs | Images (PNG/JPG) | Documentation: "recognizing layouts, tables, math formulas (LaTeX), and text in images" |
| Pix2Text output | Markdown format | Documentation: "converting them into Markdown format" |
| King Wen corpus source | arXiv HTML MathML + x-tex | Pipeline docs: "arXiv HTML MathML + x-tex as canonical source (991 equations/paper)" |
| King Wen source files | Python (scripts/) + TypeScript (dist/) | `src/` layout: parser, engine, tools |

---

## 6. Open Questions (Hypotheses)

| Question | Test Design | Expected Output |
|----------|-------------|-----------------|
| Does Pix2Text reliably preserve `munderover` limit placement? | Run Pix2Text on rendered expression crops with known `munderover` structures; compare against source MathML | Precision/recall per structure type |
| Does Pix2Text substitute symbols (Σ vs σ, l vs 1, = vs ≡)? | Use glyph manifest (1,182 entries) as reference; score confusion matrix on confusing symbol pairs | Confusion matrix with error rates |
| Do vision errors cascade into source-fidelity failures? | Measure Layer 2 errors and Layer 3 agreement on the same crop set | Error cascade statistics |
| Is the vision path complementary to the source parser? | Compare detection rates: source parser finds errors in source; vision finds errors in rendering | Complementary detection counts |

---

## 7. Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| This assessment | `docs/pix2text-assessment-2026-10-20.md` | Structural comparison document |
| Observation log | `DATASETS/math_symbols/references/pix2text_observation_log.jsonl` | Layer-by-layer observation records |
| Crop metadata | `DATASETS/math_symbols/references/crop_metadata.jsonl` | Source paper/page/bbox/render provenance |

---

## 8. Verification Requirements

Before citing any specific test count or error rate from this assessment:

1. **Re-run** `test_structural_survival.py` and confirm the actual suite count (24/24 per prior context, or 17/17 as cited in this file)
2. **Identify** the exact evaluation command executed
3. **Log** the command output with timestamps
4. **Record** any discrepancies between prior session claims and fresh verification

---

*End of assessment. This document records architectural classification, not a claim of superiority. Pix2Text and King Wen serve different layers of the visual math pipeline.*
