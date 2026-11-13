# Delimiter-Visual-Evidence Audit Package — Source-Level Audit Package
## Four-Artifact Consolidation and G0 Execution Audit Recommendation

**Date:** 2026-11-11
**Branch:** `v2-remediation` (befa228927)
**Purpose:** Freeze four-source-level audit documents as the complete evidence chain, and recommend a narrowly scoped G0 execution audit.
**Status:** Source-level audit; no files modified.

---

## Four-Artifact Evidence Chain

The audit series now consists of four source-level documents, each with a distinct evidence responsibility.

| Artifact | File | Evidence responsibility |
|----------|------|-------------|
| 1. Cross-reference audit | `docs/cross-reference-audit-2026-11-11.md` | Architectural domains, relationships, population boundaries |
| 2. Interface-conformance matrix | `docs/interface-conformance-matrix-2026-11-11.md` | Callable signatures, input/output contracts, coordinate assumptions, execution characteristics |
| 3. Usage-evidence audit | `docs/delimiter-usage-evidence-audit-2026-11-11.md` | Actual imports, invocation sites, data flow, runtime reachability |
| 4. Blind-coordinate semantics audit | `docs/delimiter-blind-coordinate-semantics-audit-2026-11-11.md` | Execution semantics, vocabulary, coordinate interpretation, blind execution definition |

### How the Four Documents Combine

```
cross-reference-audit-2026-11-11.md
  /      |        \  
 /        |         \
ic       interface   |\       
-conformance  |        |      delimiter-        
-matrix       |        |       blind-coordinate- 
              |        |       semantics-audit
              |        |                          |
        Usage-evidence audit
```

Each layer adds precision:
- **Cross-reference** = where the concepts and artifacts live (architecture)
- **Interface conformance** = what each component accepts and produces (contracts)
- **Usage evidence** = what actually connects and executes (data flow)
- **Blind-coordinate semantics** = execution semantics, vocabulary, coordinate interpretation (methodology)

---

## Most Important Finding

**Reported y_band implementation removes one specific G0 concern:**

```python
y_band = (0.0, float(page.rect.height))
```

This is the full page height, not a gold-derived delimiter region. Combined with the reported GS-001 through GS-005 checks (zero imports, references, or knowledge of gold manifests in `blind_detection_run_1505.py` and `targeted_math_detector.py`), this is meaningful evidence for prediction independence.

### G0 Investigation Status — Current Disposition

| Claim | Current disposition |
|-------|---------------------|
| Full-page search interval `y_band = (0.0, float(page.rect.height))` | Reported verified (prediction_adapter.py:88) |
| Blind execution has no gold-manifest imports/references | Reported verified (GS-001 through GS-005) |
| Prediction path is independent of all gold-derived information | Requires complete data-flow proof — see below |
| Full-corpus G0 certification | Not established |
| G1–G5 certification | Not established by these findings |

### Certification Boundary

The distinction matters because:
- Source-level import independence (GS-001–GS-005) is necessary evidence, but not sufficient
- Region-level independence (`y_band` is full-page) is also necessary, but not sufficient
- Complete independence also requires examining:
  - **Indirect data dependencies** — e.g., JSON/CSV config files that encode gold coordinates, cache files that carry gold-derived state, test fixtures that embed reference targets
  - **Downstream filtering** — any filtering, pairing, or adjudication step that could consume gold-derived information
  - **Evaluation gates** — the G0–G5 gates are applied in the evaluation layer, which is where gold is consumed

### Certification Levels

| Level | Definition | Current status |
|---------|------------|----------------|
| **Source-level verified** | Import and call sites verified against disk | G0–G5 gates, `y_band` origin, GS-001–GS-005 all reported verified |
| **Execution verified** | Real pipeline run shown; expected outputs recorded | Blind run executed (1505.05770); g0-g5 gates asserted but not executed in corpus |
| **Corpus certified** | All 243 papers processed through the complete gated path; results recorded | Not established |

---

## Narrow-Scoped G0 Execution Audit Recommendation

### Why G0 First, Not G1

G1 concerns localization equivalence. But localization equality cannot be assessed if the prediction path is not independently generated. The correct order is:

1. Establish G0 (g0-level gate) — prediction independence and candidate detection
2. Establish G1 (localization matching) — once G0 is verified
3. Establish G2–G5 — once the earlier gates are certified

### Proposed Next Steps

| Step | Deliverable | Scope |
|------|-------------|-------|
| **A. Reproduce blind G0** | Run `blind_detection_run_1505.py`; record full-page `y_band` origin on every paper in the corpus | 143 papers selected (or all 243 available) |
| **B. Record G0 gate results** | Produce per-paper G0 dispositions (G0 defined in `golden-standard-audit-matrix.md`) | Not a pass/fail; a per-paper evidence table |
| **C. Report** | `docs/g0-execution-audit-report-2026-11-11.md` | Result of Step A and B, with per-paper evidence tables |

### G0 Gate Definition (from `golden-standard-audit-matrix.md`)

| Gate | Requirement |
|------|-------------|
| G0 | Independent engine prediction — prediction generated without gold |
| G1 | Comparable localization — predicted bbox matches gold bbox |
| G2 | Four-edge clearance and contamination — no gold-adjacent content in candidate regions |
| G3 | Direct semantic comparison — predicted expression matches gold expression |
| G4 | Real adversarial perturbations through production paths |
| G5 | Three-state gate verdicts and correct denominator accounting |

The G0 audit focuses on G0 only. G1, G2, G3, G4, and G5 are deferred until G0 is corpus-certified.

---

## Term Definitions (Frozen)

The terms used in this package are frozen and defined in `delimiter-blind-coordinate-semantics-audit-2026-11-11.md`:

| Term | Definition |
|------|------------|
| `blind_execution` | The resolver runs without reference data |
| `gold_comparison` | A separate process compares blind output with gold |
| `independent_validation` | A validation run uses a separate reference or execution path |
| `blind_render_manifest` | Frozen rendered outputs produced under a blind execution protocol |
| `observation` | Raw PDF character geometry and font properties |
| `detection` | Visual candidate hypotheses |
| `recovery` | Structural relationships and delimiter pairing |
| `verification` | Independent validation and gold comparison |
| `pdf_points` | Native page geometry (top-left origin, y-down) |
| `rendered_pixels` | Raster observations from rendered page image |
| `normalized_page_coordinates` | Derived coordinates — not confirmed in source |
| `full_page_search_region` | Complete prediction-path independent search interval |
| `gold_conditioned_search_region` | Search region derived from gold data |

---

## Files in This Package

| File | Role |
|------|--------|
| `docs/cross-reference-audit-2026-11-11.md` | Cross-reference audit (architectural domains) |
| `docs/interface-conformance-matrix-2026-11-11.md` | Interface-conformance matrix (callable contracts) |
| `docs/delimiter-usage-evidence-audit-2026-11-11.md` | Usage-evidence audit (imports, invocations, reachability) |
| `docs/delimiter-blind-coordinate-semantics-audit-2026-11-11.md` | Blind-coordinate semantics audit (execution semantics) |
| `docs/g0-execution-audit-report-2026-11-11.md` | (Pending) G0 execution audit — narrowly scoped, corpus-level |

---

## Preservation Notes

1. **Do not widen** from G0 to G1 or alter the frozen 243-paper baseline until G0 has a reproducible, corpus-level disposition.
2. **Preserve the source-level / execution-verified / corpus-certified** distinction in every report.
3. **Do not replace** the four-artifact chain with a single integration diagram or a large passing test count.
4. **Verify each artifact** with `py_compile`, `npm run build`, or equivalent before claiming a certificate.

### Capability Discovery: Candidate Tooling Inventory (2026-11-11)

This appendix consolidates the capability map from all four artifacts in the audit package into a single reference table. It is the capability layer of the audit package, not a fifth independent artifact.

| # | Capability | Primary source path(s) | Input authority | Output contract | Evidence status |
|----|-----------|-----------------|-----------------|-----------------|-----------------|
| C1 | MathML extraction | `scripts/mathml_parser.py`, `scripts/arxiv_html_parser.py` | MathML tree + x-tex annotations | Equation structured output (ExprNode tree) | CONFIRMED — imported by consumers |
| C2 | LaTeX reconstruction | `scripts/math_recovery_tool.py`, `scripts/delimiter_identity.py` | MathML, gold, LaTeX | Reconstructed LaTeX string | CONFIRMED — leaf modules, imported by multiple consumers |
| C3 | Structural recovery (V1) | `scripts/delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | CONFIRMED caller — evaluation scripts |
| C4 | Structural recovery (V2) | `scripts/v2_delimiter_aware_structural_recovery.py` | Visual candidates (bbox) | Paired/unpaired structure | DECLARATION ONLY — no confirmed caller |
| C5 | AST extraction | `scripts/structural_ast_extractor.py` | MathML tree | Structural AST (ExprNode) | NOT_TESTED — import not confirmed |
| C6 | Visual detection | `scripts/targeted_math_detector.py`, `scripts/vision_math_extractor.py` | PDF page (rawdict) | Bbox, char observations, visual candidates | CONFIRMED — executable CLI |
| C7 | OCR | Pix2Text, Tesseract integrations | PDF image / crop | Character/text output | NOT_TESTED — no integration scripts found |
| C8 | Semantic validation | `scripts/math_contract.py`, `scripts/semantic_honesty_scoreboard.py` | Recovered math tree | Validation status + scoreboard | NOT_TESTED — import not traced |
| C9 | Equation solving | `scripts/solve_all.py`, `scripts/solve_dual_path.py` | Recovered math IR | Solution (SymPy) | NOT_TESTED — coverage not audited |
| C10 | Geometric validation | Localization, crop-isolation tests | Geometry ops | Adversary output (pass/fail) | NOT_TESTED — assertions not read |
| C11 | Provenance tracing | `scripts/verify_provenance_trace.py`, manifests, audit runners | Artifact + trace | Verification result | NOT_TESTED — execution needed |

### Audit Package Contribution Summary

| Package artifact | Contribution | Capability coverage |
|------------------|-------------|---------------------|
| `docs/cross-reference-audit-2026-11-11.md` | Architectural domains, relationships, populations | C1, C2, C3, C4, C6 (broad architecture) |
| `docs/interface-conformance-matrix-2026-11-11.md` | Callable interfaces, contracts, coordinate assumptions | C1, C3, C4, C6, C9 (interface layer) |
| `docs/delimiter-usage-evidence-audit-2026-11-11.md` | Import graph, invocation sites, data flow | C1, C2, C3, C4, C6, C7 (usage layer) |
| `docs/delimiter-blind-coordinate-semantics-audit-2026-11-11.md` | Blind execution definition, coordinate semantics | C1, C6, C8, C9, C11 (semantics layer) |

### G0 Execution Status Within Package

| G0 claim | Current status |
|----------|----------------|
| Full-page `y_band` = `(0.0, float(page.rect.height))` | Reported verified (prediction_adapter.py:88) |
| Blind execution has no gold-manifest imports | Reported verified (GS-001 through GS-005) |
| Full-corpus G0 certification | **NOT ESTABLISHED** |
| G1–G5 certification | **NOT AUTHORIZED** |

The G0 execution audit recommendation is documented as a future artifact: `docs/g0-execution-audit-report-2026-11-11.md`.

---

*This package is a source-level audit. It is not a deployment recommendation. No files were modified during the audit process.*
