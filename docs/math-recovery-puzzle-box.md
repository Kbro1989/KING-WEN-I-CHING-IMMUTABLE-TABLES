# Math Recovery Puzzle Box — Reconstruction Map

**Purpose:** A compiled provenance map of the math recovery tooling, showing
exactly what produced what, when, and why. Built for auditing the outputs of the
recovery pipeline: which script generated which formula, which crop set, which
delimiters, and what downstream consumption succeeded or failed.

**Scope:** Covers the full equation recovery pipeline from arXiv HTML source
through PDF targeted OCR to King Wen bridge output, with delimiter-aware
structural recovery as the core.

---

## 1. Pipeline Architecture

```
                    ┌──────────────────────────────┐
                    │  SOURCE DOCUMENTS            │
                    │  arXiv HTML (canonical)      │
                    │  PDF (benchmark_pdfs/)       │
                    └──────────────┬───────────────┘
                                   │
        ┌──────────────────────────┴───────────────┐
        │                                        │
┌────────▼────────┐                      ┌────────▼────────┐
│ Line path       │                      │ Targeted OCR    │
│ (arxiv_html_     │                      │ (targeted_    │
│  parser)        │                      │  depth_ocr)    │
│  parses MathML   │                      │  detects tall/ │
│  + x-tex annot.  │                      │  wide regions │
└────────┬────────┘                      └───────┬────────┘
         │                                        │
         │ full equations with                  │ crops at z4/z8
         │ short & tall delimiters              │ short & tall
         ▼                                        ▼
┌────────▼────────┐                      ┌────────▼────────┐
│ Line math IR    │                      │ Crop JSON     │
│ (ExprNode)      │                      │ (region bbox) │
└────────┬────────┘                      └───────┬────────┘
         │                                        │
         └────────────┬───────────────┬───────────┘
                      │               │
                      ▼               ▼
        ┌───────────────────────────────┐
        │  DELIMITER-AWARE              │
        │  STRUCTURAL RECOVERY (core)   │
        │  - delimiter identity         │
        │  - nesting depth              │
        │  - glyph preservation         │
        │  - extension bracket mapping  │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  CANONICAL IR (ExprNode)      │
        │  — typed, well-formed         │
        │  — delimiter-aware            │
        │  — math_contract.py           │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  BACKEND EMITTERS             │
        │  SymPy / Wolfram / Lean       │
        │  / PARI / Sage                │
        │  (solve_dual_path)            │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  SCOREBOARD                 │
        │  − parse success              │
        │  − structural survival        │
        │  − backend compatibility      │
        │  − solution acceptance        │
        │  − FALSE_RECOVERY = 0         │
        └───────────────────────────────┘
```

---

## 2. Layer Inventory

### Layer A — Discovery & Crop (targeted_ocr/)

Source: `scripts/targeted_depth_ocr.py`
Method: K-Means + flood fill + connected components on rendered PDF pages.
Detection zoom: 4x (`z4`); crop zoom: 8x (`z8`).

**Crop types produced:**
- `tall_narrow_*_z8.png` — stretched symbols: braces, delimiters, tall math,
  superscript lines (aspect ratio >2.5, height >3× median line height)
- `wide_*_z8.png` — multi-line expressions, fraction bars, aligned matrices
  (width >10× median line height)

**Key files per paper:**
- `0806.2366_p3_detection_z4.png`
- `1212.0957_p8_detection_z4.png` + `1212.0957_p8_tall_narrow_00/01_z8.png`
- `2009.00031_p5_detection_z4.png` + 11 tall_narrow + 4 wide crops
- `2102.03334_p6_detection_z4.png`
- `2605.00155_p27_detection_z4.png`
- `2605.00224_p1_detection_z4.png`
- `2605.06070_p12_detection_z4.png`
- `2605.18130_p4_detection_z4.png` + 4 wide
- `2605.22715_p19_detection_z4.png`
- `2605.23244_p4_detection_z4.png`
- `2605.24807_p9_detection_z4.png`
- `2605.24856_p17_detection_z4.png`
- `2605.25036_p3_detection_z4.png` + 4 wide
- `2605.25334_p6_detection_z4.png`
- `2605.28615_p15_detection_z4.png`
- `2605.28896_p16_detection_z4.png` + 4 tall_narrow + 5 wide

### Layer B — OCR & Harvest (pix2text)

Source: `scripts/pix2text_harvest.py`
Model: pix2text 1.1.7, `recognize_formula()` method
Parameters: detection_zoom=4, crop_zoom=8, min_height_px=40

Output: `DATASETS/PDF_FIDELITY_RENDERINGS/<paper>/pix2text_candidates.jsonl`
Records: raw-harvest candidates (per crop region)

### Layer C — Adjudication (classification)

Source: `scripts/adjudicate_candidates_v2.py`, `scripts/adjudicate_targets.py`
Models the four-level adjudication:
- SPATIAL_MATCH — parser candidate boxes overlap/are contained
- TEXT_MATCH — normalized math content agrees
- VISUALLY_VERIFIED — source crop is non-blank, real content
- ADJUDICATED — human review, explicit row flag

Output: `adjudication_report.jsonl`, `adjudication_summary.json`

### Layer D — Structural Recovery (the puzzle box core)

Source: `scripts/delimiter_aware_structural_recovery.py`
Deliverable: `DATASETS/structural_preservation/cross_paper_case_registry_v1.json`
Engine baseline SHA-256: `8211592af549c29233b4c19f49b95694ecfcd9df1ab43c276ebdb1d3e2c142a1`

The recovery engine preserves:
1. delimiter identity (kind match: `(`→`)`, `[`→`]`, `{`→`}`)
2. nesting depth (correct pairing order)
3. glyph preservation (ascenders, descenders, symbols)
4. extension bracket typography (7-piece extensible brackets U+F8EE–U+F8FB)

### Layer E — Bridge to King Wen

Source: `scripts/bridge_math_diagram_extractor.py`
Output: `DATASETS/math_diagram_extractor_bridge.json`
Consumer: `emotional_engine.py`, `full_hexagram_shotgun.py`,
`src.core.pog3_hexagram_runtime_substrate`

Bridge pulls: extracted math regions, K-color palettes, bounding box
centroids, 729-vertex point cloud spatial anchors, KW64_SAVE_STRING_V2.1.

---

## 3. Evidence Role Taxonomy

| Role | Meaning | Applied to |
|------|---------|------------|
| CAPTURE | real source, non-fabricable values | benchmark PDFs, crop PNGs |
| MIRROR | wraps external behavior in local interface | html parser, OCR extractor |
| SIMULATION | models external transitions to test local logic | delimiter recovery engine, adjudication |
| SYNTHETIC | deliberate abstraction/test values | counting sequences, failure cases |

---

## 4. Version Provenance Map

| Version | State | Defects Fixed | Regressions Caused | Status |
|---------|-------|---------------|-------------------|--------|
| v1 baseline | 532 recovered, 223 solvable | — | — | BASE |
| v2 | 678 / 364 | nested `\frac` args (regex `[^{}]+` can't match braces) | — | FIXED |
| v3 | 678 / 364 | no change | — | OBSOLETE |
| v4 | 743 / 364 | escaped literals `\_ \& \% \# \$ \{ \}` | solvable 364→360 | FIX_WITH_REGRESSION |
| v5 | 747 / 377 | accent spacing (no space → `\log` fused to `pi_bar`) | — | FIXED |
| v6 | 754 / 385 | function-argument joining (detached `)\` `(`) | none | FIXED |
| v9–v12 | 756 / 386 | input join, tree control layer | none | FIXED |
| v13 (tree path) | 756 / 386, FALSE_RECOVERY=0 | delimiter identity, MathML structural conservation | — | GLASS_WALL |

---

## 5. Audit Checkpoints

For each paper in the targeted_ocr set:

1. **Crop integrity**: PNG decode succeeds, non-blank, ink ratio ≥0.01
2. **Target localization**: bbox genuinely contains intended formula
3. **Formula isolation**: crop free from adjacent prose
4. **OCR fidelity**: pix2text returns real content (no hallucination)
5. **Structural survival**: delimiter identity preserved through recovery
6. **Semantic fidelity**: backend solver accepts or rejects coherently

---

## 6. Extending the Puzzle Box

When adding a new paper or paper page to the pipeline:

1. Add the PDF to `DATASETS/benchmark_pdfs/`
2. Add the page selection to `SELECTED_PAGES` in `targeted_depth_ocr.py`
3. Run `targeted_depth_ocr.py --help` for crop generation
4. Run `pix2text_harvest.py` to produce candidates
5. Run `adjudicate_targets.py` for explicit adjudication
6. Run `delimiter_aware_structural_recovery.py` for structural recovery
7. Write `evidence_manifest.json` per paper documenting all provenance
8. Update `cross_paper_case_registry_v1.json` with the new case
9. Update `recovery_registry.py` with any new versions or defects fixed
