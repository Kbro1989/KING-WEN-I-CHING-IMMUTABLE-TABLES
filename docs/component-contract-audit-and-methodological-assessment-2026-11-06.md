# Component-Contract Audit + Methodological Assessment
## Subtitle: Mathematical PDF Vision — Raw Evidence, Information Retention, and Downstream Interpretation

**Audit date:** 2026-11-06
**Working tree:** `KING-WEN-I-CHING-IMMUTABLE-TABLES` (v2-remediation, branch `main`, committed and pushed as `befa228927`)
**Scope:** Read-only audit of visual-layer and recovery components; no implementation or corpus execution performed
**Concerns this revision addresses:**
- Do current visual tools lose information before classification, or preserve it but lack downstream interpretation?
- Is the claimed "lossy conversion" established by evidence, or speculative?
- Does the corrected disposition distinguish raw evidence collection from raw evidence retention in downstream outputs?

**Key correction:** The audit now distinguishes (1) raw evidence collection at the observation stage, (2) retention through the visual-layer output boundary, and (3) downstream interpretation/stages. These are three separate questions with different evidence.

---

## Part 1: Component-Contract & Data-Lineage Audit (Sections 1–7)

### §1 Audit Boundary & Retrospective

**Target:** Mathematical PDF vision pipeline — raw PDF observation → candidate generation → visual-layer output → (missing) classification ↔ pairing ↔ structural recovery.

**Retrospective correction from first revision (2026-11-06):**
- Original first-draft hypothesis: "Information is lost because `extract_raw_observations()` discards glyphs before candidate generation."
- This revision corrects that hypothesis: `extract_raw_observations()` (from `targeted_math_detector.py`) is the first-stage observation function and returns per-glyph records with font, coordinates, and character data. The defect is not in that function. It is in the **visual-layer output boundary**, where the summary record discards fields present in the raw dict.

**Audit scope (evidence layers):**
- Frozen equation-accounting baseline (243-paper batch, 235 successful, 8 HTTP 404) — provided as context, not examined in this audit.
- Component file inventory — read-only inspection.
- Actual import graph — verified via static analysis.
- Actual call graph — verified via static analysis of `pdf_visual_analysis_layer.py`.
- Interface contracts (input/output shapes) — read from source.

**Not part of scope:** Corpus execution (no PDF rendered), G0 certification, implementation work, corpus routing.

**Boundary rules:**
- Rule 1: Do not edit frozen components, gold data, evaluator contracts, manifests, or historical reports.
- Rule 2: Do not propose wiring, corpus execution, or G0 advancement.
- Rule 3: Distinguish raw evidence collection from raw evidence retention in downstream outputs.
- Rule 4: Use precise, evidence-matched language. Avoid claims of irreversible data destruction unless source-level evidence exists.

---

### §2 Artifact Inventory & Authority Map

| Artifact | Exact path | Lines | Size | Status |
|----------|-----------|-------|------|--------|
| Audit checklist | `docs/audit-checklist-2026-11-06.md` | 219 | 17.3 KB | ✅ Present |
| Completeness vocabulary | `docs/completeness-vocabulary-2026-11-06.md` | 414 | 19.1 KB | ✅ Present |
| Batch/delimiter integration audit | `docs/batch-delimiter-integration-audit-2026-11-06.md` | 355 | 13.6 KB | ✅ Present |
| Visual analysis layer | `scripts/pdf_visual_analysis_layer.py` | 219 | 7.2 KB | ✅ Present, imports clean |
| Corpus orchestrator | `scripts/pdf_visual_corpus_integrator.py` | 164 | 5.9 KB | ✅ Present, imports clean |
| Targeted math detector | `scripts/targeted_math_detector.py` | 343 | 13.6 KB | ✅ Present, on disk |
| Delimiter-aware structural recovery | `scripts/delimiter_aware_structural_recovery.py` | 531 | 22.0 KB | ✅ Present, on disk |
| Font-aware math classifier | `scripts/font_aware_math_classifier.py` | 226 | 8.7 KB | ✅ Present, on disk |
| MathML parser | `scripts/mathml_parser.py` | 849 | 37.8 KB | ✅ Present, on disk |
| G0 prediction adapter | `scripts/evaluation/prediction_adapter.py` | — | — | Frozen (per G0 contract) |
| G0 contracts | `scripts/evaluation/contracts.py` | — | — | Frozen (per G0 contract) |

---

### §3 Component Contract & Call Graph

**Import graph (verified via AST):**

| Component | Imports | Reference |
|-----------|---------|-----------|
| `pdf_visual_analysis_layer.py` | `targeted_math_detector` only | `scripts/pdf_visual_analysis_layer.py:40-46` |
| `pdf_visual_corpus_integrator.py` | stdlib | `scripts/pdf_visual_corpus_integrator.py` |
| `targeted_math_detector.py` | stdlib, pymupdf, numpy, cv2 | `scripts/targeted_math_detector.py` |
| `delimiter_aware_structural_recovery.py` | stdlib, pymupdf, cv2, numpy | `scripts/delimiter_aware_structural_recovery.py` |
| `font_aware_math_classifier.py` | stdlib, re | `scripts/font_aware_math_classifier.py` |
| `mathml_parser.py` | `delimiter_identity.py` | `scripts/mathml_parser.py` |

**Call graph (verified from `pdf_visual_analysis_layer.py` source):**

```
extract_raw_observations(page, page_index)  ← from targeted_math_detector
geometry_candidates(chars)                    ← from targeted_math_detector
script_position_candidates(chars)             ← from targeted_math_detector
render_visual_candidates(page, page_index, zoom, out_dir) ← from targeted_math_detector

detect_delimiters_on_page(page, page_index, zoom=3.0) 
    → returns per-page dict (10 fields)
```

**Confirmed call relationships (from source):**
- `pdf_visual_analysis_layer.py` calls 3 functions from `targeted_math_detector` only: `extract_raw_observations`, `geometry_candidates`, `script_position_candidates`, `render_visual_candidates`.
- `pdf_visual_analysis_layer.py` does **not** call `classify_glyph` from `font_aware_math_classifier`.
- `pdf_visual_analysis_layer.py` does **not** call `associate_delimiter_pairs` from `delimiter_aware_structural_recovery`.
- `pdf_visual_corpus_integrator.py` does **not** call `pdf_visual_analysis_layer.py`.
- `pdf_visual_corpus_integrator.py` does **not** call the recovery engine or classifier.

---

### §4 Information Retention and Downstream Interpretation

**Question:** Do the current visual tools lose information before classification, or preserve it but lack downstream interpretation and recovery?

**Answer:** Raw evidence is collected at the observation stage, but its retention through the visual-layer output boundary is incomplete. Downstream classification, pairing, and recovery are also absent from the verified call path.

**Stage-by-stage evidence:**

| Stage | Evidence (source: `scripts/pdf_visual_analysis_layer.py`) | Disposition |
|-------|----------------------------------------------------------|-------------|
| Raw observation | `extract_raw_observations()` returns per-glyph records with font, bbox, character, font_size_pt, is_math_char, etc. | Collected |
| Candidate generation | `geometry_candidates(chars)` and `script_position_candidates(chars)` derive candidate lists from those records | Derived from observations |
| Visual-layer output | `detect_delimiters_on_page()` returns a summary dict (10 fields): `page_index`, `total_chars`, `math_chars`, `visual_candidates_detected`, `geometric_candidates`, `script_position_candidates`, `visual_components_detected`, `render_path`, `threshold_path`, `connected_component_count` | Does not expose all raw observation fields |
| Classification | No classifier call found in the visual-layer source | Not connected |
| Pairing | No pairing call found in the visual-layer source | Not connected |
| Structural recovery | No recovery call found in the visual-layer source | Not connected |

**Placement of the information gap:**

```
extract_raw_observations()  →  [verified: retains font, coordinates, char data]
                              ↓
geometry_candidates()       →  [verified: derived candidate list, height/aspect ratios]
                              ↓
script_position_candidates()→  [verified: derived script-position hypotheses]
                              ↓
detect_delimiters_on_page() →  [verified: returns summary dict, does NOT surface rawdict fields]
                              ↓
┌───────────────────────────────┐
│ OUT: candidate summaries + metadata  ← MISSING: font, coordinates, char fields per candidate
└───────────────────────────────┘
```

**Placement of missing downstream analysis:**

```
OUT(cropped candidate summaries) →  [NOT connected]
    → classify_glyph()              →  [missing — no call]
    → associate_delimiter_pairs()   →  [missing — no call]
    → recovery engine               →  [missing — no call]
```

**Key clarification:**
- The evidence supports an **observation-to-output retention gap** and **missing downstream interpretation**.
- The evidence does **not** establish that the original detector irreversibly destroys the raw data internally. That would require inspecting the actual returned objects and their lifetimes, which is outside this audit's scope (read-only).

**Placement of missing downstream interpretation:**

```
OUT(cropped candidate summaries) →  [NOT connected]
    → classify_glyph()              →  [missing — no call]
    → associate_delimiter_pairs()   →  [missing — no call]
    → recovery engine               →  [missing — no call]
```

**Disposition:** `PARTIALLY PRESERVED / DOWNSTREAM INTERPRETATION NOT CONNECTED`

---

### §5 Summary of Component Contracts

**What `pdf_visual_analysis_layer.py` expects and returns:**

| Stage | Function | Input | Output |
|-------|----------|-------|--------|
| Raw observation | `extract_raw_observations(page, page_index)` | `fitz.Page`, int | `(spans, chars)` |
| Geometric candidates | `geometry_candidates(chars)` | list of char dicts | list of geometry candidates |
| Script-position candidates | `script_position_candidates(chars)` | list of char dicts | list of script candidates |
| Render/visual candidates | `render_visual_candidates(page, page_index, zoom, out_dir)` | page, int, float, Path | dict with visual candidates |
| Page summary | `detect_delimiters_on_page(page, page_index, zoom=3.0)` | `fitz.Page`, int, float | dict with 10 fields |

**What `delimiter_aware_structural_recovery.py` expects and returns:**

| Stage | Function | Input | Output |
|-------|----------|-------|--------|
| D1 glyph extent | `verify_d1_glyph_extent(glyph_rect, crop_rect, tolerance_pt)` | 2× pymupdf.Rect, float | dict |
| D2 delimiter identity | `classify_delimiter_glyph_font_aware(page, rect)` | `fitz.Page`, `pymupdf.Rect` | dict with kind, is_opening, family, confidence |
| D3 pairing | `associate_delimiter_pairs(candidates, page_width, page_height)` | list[dict w/ rect+delimiter_id], floats | (paired, unpaired) |
| D4 enclosure | `build_enclosure_completeness(page, pair)` | page, pair dict w/ `_opening_rect_raw`, `_closing_rect_raw` | (Rect, meta dict) |
| D5 translation | `verify_d5_translation_fidelity(grid_data, delimiter_info, expected_rows)` | dict, dict, int | dict |
| D6 provenance | `build_d6_provenance(pdf_path, page_num, pair, enclosure_rect)` | Path, int, pair dict, Rect | dict |

**What `font_aware_math_classifier.py` expects and returns:**

| Stage | Function | Input | Output |
|-------|----------|-------|--------|
| Font check | `is_math_font(font_name)` | str | bool |
| Glyph classification | `classify_glyph(char, font_name, font_size_pt)` | char, str, float | dict with is_math, category, latex_interpretation |
| Citation discrimination | `discriminate_citation(text)` | str | dict with is_citation_candidate, confidence |

---

### §6 Preservation Rule Verification

| Rule | Status | Evidence |
|------|--------|----------|
| R1 (preserve frozen engines/gold data/manifests/historical reports) | ✅ | Components read-only; no modification of frozen outputs |
| R2 (read before acting) | ✅ | Source inspection via read_file/read-based verification |
| R3 (verify claims via source inspection) | ✅ | Import graph and call relationships verified via AST |
| R4 (no automatic implementation) | ✅ | Integration boundary confirmed as a documented gap, not a defect |
| R5 (no new architecture) | ✅ | Audit describes existing implementation without proposing new components |
| R6 (preserve every benchmark's original denominator/scope) | ✅ | 243-paper accounting and 988-page visual analysis remain separate populations |
| R7 (preserve history) | ✅ | Static report; no historical measurements overwritten |
| R8 (explicit NOT VERIFIED when evidence missing) | ✅ | Delimiter detection and identity marked NOT VERIFIED |
| R9 (separate evidence collection from retention assessment) | ✅ | Section 4 distinguishes raw observation collection from output-boundary retention |

**Not established by this audit:** That `extract_raw_observations()` irreversibly destroys raw data internally. The audit covers the observed call chain and the output record structure, not the internal lifetime of the returned dict. That would require a runtime inspection, which is outside this audit's scope.

---

### §7 Per-Page Evidence & Corpus-Level Status

**Per-page evidence (visual layer output, `scripts/pdf_visual_analysis_layer.py:80-92`):**
- `page_index`, `page_label`
- `total_chars`, `math_chars`
- `visual_candidates_detected` (count)
- `geometric_candidates` (list of candidates with height_ratio, candidate_reasons, status)
- `script_position_candidates` (list with vertical_offset, attachment_status, status)
- `visual_components_detected` (count)
- `render_path`, `threshold_path` (file paths to rendered images)
- `connected_component_count`

**Corpus-level status (from `pdf_visual_corpus_integrator.py`):**
- `equation_accounting`: PASS (verified, 235/235 reconciled, 8 HTTP 404 failures explicit)
- `delimiter_detection_and_identity`: NOT VERIFIED (pending PDF integration)
- `structural_preservation`: NOT VERIFIED (pending PDF integration)

No corpus execution has been performed. The corpus orchestrator builds a report template; it does not execute the visual layer against any PDF.

---

## Part 2: InstructPix2Pix Methodological Assessment (Sections 8–10)

*Separate section — does not alter Section 1 findings. Methodological analysis only.*

### §8 InstructPix2Pix Relevance to the Existing Vision Architecture

| Paper concept | Existing pipeline relationship | Audit implication |
|---------------|-------------------------------|-------------------|
| Input-image conditioning | `extract_raw_observations()` and page rendering | Preserve the original page as authoritative evidence |
| Instruction conditioning | Candidate interpretation and classification | Interpretation must remain separate from observed glyph data |
| Image-consistency guidance | Candidate coordinates and source-page provenance | Do not allow interpretation or enhancement to overwrite source evidence |
| Instruction-following guidance | Classification and structural hypotheses | A model's interpretation is a hypothesis, not a verified delimiter identity |
| Paired image/edit data | Existing visual comparison and selected structural cases | Controlled visual variations could test robustness |
| Generated-image filtering | Existing evaluation and adjudication | Perceptual similarity cannot certify mathematical correctness |

**Disposition:** Adopt as design principles. Do not add as new implementation dependencies.

---

### §9 The Missing Distinction: Observation Versus Intervention

The paper is about editing images. Your pipeline is about extracting evidence from images. Those are fundamentally different operating modes.

**Evidence-preserving vision:**

```
Original PDF page → observation (glyphs, fonts, geometry, pixels, coordinates)
                              ↓
                    interpretation (identity hypotheses, classification, confidence)
                              ↓
                    structural verification (pairing, extent, enclosure, preservation)
```

The critical property: **interpretation can inform verification, but cannot rewrite the observation.** No downstream step may modify the original candidate coordinates, pixel evidence, or font data.

**InstructPix2Pix** could be useful in an auxiliary experimentation path for visual enhancement or targeted transformations. Any transformed image must remain a derivative, with explicit lineage to the original. Its output cannot become the authoritative source for glyph coordinates or delimiter identity.

---

### §10 Controlled Visual-Degradation Experiment

The strongest practical contribution is the paired-data methodology. Use existing known mathematical cases and generate controlled visual variants:

| Original                       | Controlled variation                     |
| ------------------------------ | ---------------------------------------- |
| Clean equation rendering       | Reduced contrast                         |
| Known delimiter identity       | Slight geometric distortion              |
| Known delimiter coordinates    | Scan skew                                |
| Full mathematical context      | Controlled neighboring text interference |
| Known structural relationships | Controlled crop truncation               |

**Not acceptable as ground truth:** Diffusion-generated mathematical expressions (models can silently change minus signs, brackets, exponents, or operators while producing an image that looks convincing).

**Measurements needed for each variant:**
1. Candidate detection (recall vs. clean baseline)
2. Glyph identity (correctness of classification)
3. Geometric extent (extent preservation)
4. Pairing (opening/closing association)
5. Structural preservation (D1–D6 gate results)
6. Context retention (neighborhood preservation)

**Key caveat:** Mathematical delimiters are often thin, discontinuous, nested, or font-dependent. Generic object segmentation merges adjacent symbols or breaks a delimiter into multiple components. Mathematical-specific evaluation is required.

---

## Part 3: Research Evidence Review (Sections 8.1–8.x)

*Additional methodological findings from the latest user attachments. No implementation recommended.*

### §8.1 Object-Centric Image Editing (CPAM / EMNLP 2023 Findings)

**Paper:** *Learning to Follow Object-Centric Image Editing Instructions Faithfully* (Chakrabarty et al., Findings of EMNLP 2023)

**Relevance to mathematical PDF vision: HIGHEST**

The paper's three central challenges map to the needed capabilities:
- **Underspecification:** the instruction does not fully describe the intended object
- **Grounding:** the system must locate the intended region
- **Faithfulness:** unrelated image content must remain unchanged

**Translation to the visual PDF domain:**
- A tall glyph is not necessarily a delimiter
- A delimiter candidate is not necessarily part of the nearest equation
- A detected delimiter must not cause surrounding mathematical content to be discarded or altered

**Use in audit:** Structural evidence for the context-preservation requirements (R22/R23/R42 family). The paper provides a research basis for the three-level distinction below, not a new implementation.

---

### §8.2 InstructEdit (Wang et al. 2023)

**Relevance to mathematical PDF vision: HIGH**

The decomposition (language processor → segmenter → editor) is useful for the **segmentation component**, not the editing component. The useful idea is:
- A language processor produces segmentation prompts
- A segmenter generates masks
- (Editing is not needed for evidence extraction)

**Transfer to the pipeline (segmentation as auxiliary evidence):**

```
Original PDF rendering → existing geometric candidate detection
                          → segmentation / region proposal
                          → candidate mask, connected region, contextual boundary
                          → existing classification and structural recovery
```

The segmentation result is an additional observation, not a replacement for the original glyph or its coordinates. A mathematical-specific evaluation is required because generic object segmentation may merge adjacent symbols, break a delimiter into multiple components, or mistake a fraction bar for part of a larger object.

**Use in audit:** Constructive research direction for region-proposal improvement. Does not change the component-audit findings.

---

### §8.3 InstructRL4Pix (Li et al. 2024)

**Relevance to mathematical PDF vision: MODERATE**

Attention-map localization and reward optimization could inform candidate-region localization evaluation. Note: its editing reward is not a mathematical correctness metric and cannot be used as ground truth for mathematical identity.

---

### §8.4 Instruct-NeRF2NeRF (Haque et al. 2023)

**Relevance to mathematical PDF vision: LOWER DIRECT**

Iterative multi-view optimization toward consistent edits is interesting for 3D reconstruction, but PDF pages are fundamentally different from reconstructed 3D scenes.

---

### §8.5 Three-Level Distinction for Mathematical Vision

The object-centric grounding research suggests the following three-level mapping for a mathematical expression like `⟮a b; c d⟧`:

| Level | Operation | Relevant research idea |
|-------|-----------|------------------------|
| Glyph localization | Find candidate visual features | Attention and segmentation (CPAM, InstructEdit) |
| Region grounding | Determine which mathematical region contains the candidate | Object-centric grounding (CPAM) |
| Structural interpretation | Determine identity, pairing, enclosure | Your existing recovery system |

The papers offer useful ideas for levels 1 and 2. They do not solve level 3 (structural interpretation). Level 3 is your existing recovery system's role.

---

### §8.6 Key Research Questions

The audit confirms these remain open research questions (hypotheses for investigation, not established defects or demonstrated improvements):

1. Can segmentation improve the localization of complete mathematical regions?
2. Can candidate-to-region relationships be preserved more reliably than with isolated glyph crops?
3. Can controlled image degradation reveal where geometric detection loses context?
4. Can attention or segmentation evidence improve candidate ranking without being treated as proof of mathematical identity?

---

### §8.7 Integration: Placement of Research Evidence

The papers contribute to the evidence base as **methodological hypothesis generators**, not as missing executable components. No new implementation dependency is added. The research evidence should:
- Inform the design of future context-preservation tests
- Provide the theoretical basis for the segmentation-as-auxiliary-evidence path
- Offer a research agenda for the three-level distinction
- Not be treated as an established improvement to the current pipeline

---

## Part 4: Corrections and Clarifications

### Correction 1: Section 4 — Do Not Claim the Conversion Is Necessarily Lossy

The earlier draft said a "lossy conversion is required" to reconcile the visual layer's summary output with the recovery engine's input contract. The contract mismatch is established by the described field differences, but lossiness depends on whether the missing information can be recovered from retained source observations or other records.

**Revised language:** "An adapter is required to reconcile the candidate schemas. Whether that adapter can be lossless depends on the availability and retention of the original geometry, font, identity, and provenance fields."

**Rationale:** The visual layer's summary record does not contain font or original coordinates for each candidate; the recovery engine expects those fields. The protocol below describes the gap and the need for an adapter, but does not assert that the adapter must be lossy.

---

### Correction 2: Section 4 — Raw Evidence vs. Downstream Retention

The earlier Part 3 claimed "The visual tools preserve raw evidence but lack downstream interpretation." This combines two separate questions:

1. Does the first-stage observation function extract raw evidence? **(Answer: Yes — `extract_raw_observations()` is the observation stage.)**
2. Does the visual layer preserve that evidence in its returned records? **(Answer: Partially — the summary record does not surface all rawdict fields. The disposition is `PARTIALLY PRESERVED`.)**

**Revised Part 3:**

| Stage | Evidence (source: `scripts/pdf_visual_analysis_layer.py`) | Disposition |
|-------|----------------------------------------------------------|-------------|
| Raw observation | `extract_raw_observations()` returns per-glyph records with font, bbox, character | **Collected** |
| Candidate generation | `geometry_candidates()` and `script_position_candidates()` derive candidate summaries | **Derived from observations** |
| Visual-layer output | `detect_delimiters_on_page()` returns 10-field summary | **Does not expose all raw observation fields** |
| Classification | No classifier call found | **Not connected** |
| Pairing | No pairing call found | **Not connected** |
| Structural recovery | No recovery call found | **Not connected** |

**Disposition:** `PARTIALLY PRESERVED / DOWNSTREAM INTERPRETATION NOT CONNECTED`

---

### Correction 3: Section 4 — Read-Only Boundaries

The earlier Part 4 proposed wiring, corpus execution, and G0 advancement. These are future implementation considerations, not read-only findings.

**Read-only verification questions (this audit):**
- Does the visual layer's output preserve the original observation fields? (Answer: No — the summary record discards them)
- Does the visual layer invoke classification? (Answer: No — no classifier call established)
- Does the visual layer invoke pairing or recovery? (Answer: No — no calls established)

**Future implementation consideration (not audit scope):**
- Evaluate an adapter between the visual-layer candidate output and the recovery engine's input contract, to determine whether the adapter can be lossless.
- The adapter evaluation is a separate task; wiring is not authorized by this audit.

---

### Correction 4: Section 4 — Unified New Direction

The latest attachment adds a fourth question for the read-only audit: **inside the coordinate-system/candidate-record relationship**. Specifically:

- The visual layer returns candidate summaries with `bbox_pdf_pt_approx` from a rendered image.
- The recovery engine expects `pymupdf.Rect` objects for exact geometry.
- The coordination relationship between the two is a compatibility question, not a defect.

**Not part of this audit:** whether the adapter can be synthesized. Only whether the coordinate system and data flow are documented accurately in this audit.

---

## Part 5: Final Disposition

### Question: Does InstructPix2Pix fix the missing recovery interface?

**Answer:** No. InstructPix2Pix is a research direction, not a missing executable component.

### Question: Does it supply a replacement delimiter detector?

**Answer:** No.

### Question: Does it offer useful visual-processing principles?

**Answer:** Yes. The source-consistency, paired-data, and segmentation-as-auxiliary-evidence concepts are documented as methodological guidance.

### Question: Does it suggest a robustness-testing methodology?

**Answer:** Yes. Controlled visual-degradation experiments are recommended (see §10).

### Question: Should its generated edits enter the authoritative evidence path?

**Answer:** No. Any transformed image must remain a derivative, with explicit lineage to the original.

### Question: Should it be evaluated as an auxiliary vision experiment?

**Answer:** Potentially yes — as an auxiliary path for visual enhancement or targeted transformations, not in the authoritative evidence chain.

---

## Part 6: Overall Audit Findings

### Findings that remain unchanged from the earlier audit:

- The batch equation-accounting result does not establish delimiter detection.
- The visual layer invokes candidate-generation functions but does not establish classification, pairing, or structural recovery.
- The corpus integrator does not establish visual-layer execution.
- The InstructPix2Pix paper contributes methodological principles, not a missing executable component.
- No corpus-level delimiter certification follows from the available evidence.

### Substantive correction (latest revision):

- Part 3 is revised to `PARTIALLY PRESERVED / DOWNSTREAM INTERPRETATION NOT CONNECTED`, distinguishing raw evidence collection from raw evidence retention.
- Section 4 no longer claims a necessarily lossy conversion; it describes an adapter requirement.
- Implementation recommendations (adapter evaluation, wiring, corpus execution) have been moved from read-only disposition to future-implementation consideration.
- New research-review section added: three-level distinction (glyph localization, region grounding, structural interpretation) and four candidate research questions.

---

## Part 7: Verification Notes

This audit was produced by read-only inspection of the actual source files:

- `scripts/pdf_visual_analysis_layer.py` — 219 lines; import graph verified (imports only `targeted_math_detector`; visual-layer call chain verified)
- `scripts/pdf_visual_corpus_integrator.py` — 164 lines; corpus orchestrator verified (static report template, no live component calls)
- `scripts/targeted_math_detector.py` — 343 lines; `extract_raw_observations()` returns rawdict fields (font, coordinates, char); geometry/script functions produce derived candidates
- `scripts/delimiter_aware_structural_recovery.py` — 531 lines; D1–D6 gates documented; not called by visual layer
- `scripts/font_aware_math_classifier.py` — 226 lines; `classify_glyph` exists but is not called by visual layer
- `scripts/mathml_parser.py` — 849 lines; source-level parser for MathML; not called by visual layer

All verification based on source inspection. No corpus-level execution performed.
