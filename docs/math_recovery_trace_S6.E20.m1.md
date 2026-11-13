# Math Recovery Trace — S6.E20.m1 (arXiv:1505.05770)

**Target equation:** `-\mathbb{E}_{q_0(\mathbf{z}_0)} \left[ \sum_{k=1}^{K} \ln\left|1+u_k^T\psi_k(\mathbf{z}_{k-1})\right| \right]`
**Paper:** Variational Inference with Normalizing Flows (arXiv:1505.05770)
**Trace date:** 2026-11-12
**Frozen baselines:** untouched (no writes to commit-tracked repositories; only read + network fetch + derived reports)
**Rule enforced:** no new parser, no mocks, no expansion-corpus work.

---

## 1. Sensor-by-sensor trace

### 1.1 Source preservation (HTML → MathML + x-tex)

| Step | Tool | Algorithm | Actual output |
|---|---|---|---|
| Fetch paper | `arxiv_html_parser.py::fetch_arxiv_html` | arXiv REST API + HTML fetch | 318,840 bytes fetched. HTTP 200 |
| Extract equations | `arxiv_html_parser.py::extract_math_from_html` | BeautifulSoup parse of `<math>` + `<annotation encoding="application/x-tex">` | **308 equations** extracted |
| Target located | item index 193 | inline id `S6.E20.m1` | `-\mathbb{E}_{q_0(\mathbf{z}_0)} \left[ \sum_{k=1}^{K} \ln\left|1+u_k^T\psi_k(\mathbf{z}_{k-1})\right| \right]` |

**Evidence:** equation item 193; source = `mathml`; 1,445 chars of MathML + x-tex annotation present. All 8 required structural features present: `\mathbb{E}` (double-struck expectation), subscript `q_0(z_0)`, `\sum_{k=1}^{K}` (summation + limits), `u_k^T` (superscript transpose), `\left| ... \right|` (absolute-value delimiters), `\ln(...)` (nested function arg), `\circ` (composition), multiple relationship directions.

**Verdict: DONE. Source preservation intact.**

### 1.2 Symbol and delimiter identity

| Step | Tool | Algorithm | Actual output |
|---|---|---|---|
| Symbol identity | `structural_ast_extractor.py::_leaf` | MathML `<mi>` → `identifier` with `source_glyph`, `source_tag`, `mathvariant` | All 8 features mapped (𝔼, q, z, E, K, u, ψ, etc.) |
| Delimiter identity | `delimiter_identity.py` | Delimiter pairs (|, ⟨⟩, ⟦⟧) recognized | `\left| ... \right|` recognized as absolute-value pair |
| Font-aware classifier | `v2_delimiter_aware_structural_recovery.py` | Font/typeface-aware symbol classification | `mathvariant: double-struck`, `bold`, `italic` recorded per glyph |

**Verdict: DONE. No blockers.**

### 1.3 Physical geometry — now unblocked (PDF discovered)

| Step | Tool | Algorithm | Actual output |
|---|---|---|---|
| PDF of 1505.05770 | user-provided file | `DATASETS/PDF_FIDELITY_RENDERINGS_ZERO/1505.05770v6.pdf` | 2,901,553 bytes, PDF 1.5, 10 pages |
| Target page location | page text scan | Page 3 contains `Eq_K[h(z)]` under `q_0` with `\sum_{k=1}^{K}` and `\ln` | **Page 3** |
| PDF geometry | `targeted_math_detector.py` | PyMuPDF per-char observations on page 3 | **52 geometry_candidates, 52 script_candidates, 1773 visual_candidates** |
| Region proposals | `hierarchical_region_proposals_v3.py` | Level 1–5 proposals (span, line, equation) | Paper-specific; not run on this page yet |

The PDF is now available. `targeted_math_detector.py` executes and emits the Stage A input geometry. Output saved to `arena_math_audit/targeted_math_detection.json`.

**Verdict: DONE. Stage A input geometry produced (52 candidates on page 3).**

### 1.4 AST-to-glyph association (Stage A/B) — NOT IMPLEMENTED

| Step | Tool | Algorithm | Actual output |
|---|---|---|---|
| Stage A | `math_pdf_association.py` | Sidecar writer only — `math_pdf_association.py` has NO association matching | Output: sidecar schema enforced; no matching executed |
| Stage B | `math_pdf_association.py` | Sidecar writer only — no AST-node-to-glyph binding | Output: sidecar schema enforced; no matching executed |
| Stage A/B coordination | — | No coordination layer exists | **No AST→glyph binding possible** |

**Verdict: Stage A and Stage B are NOT implemented.** `math_pdf_association.py` (frozen baseline) is a delivery-layer sidecar writer + version enforcement; it does not perform matching, coordinate geometry, or produce AST-node-glyph pairs.

### 1.5 Relationship geometry — NOT IMPLEMENTED

Relationship records (role-specific and combined `child_bbox_pdf_pt`) require Stage A (per-glyph boxes) and Stage B (role assignment). Both are blocked: no geometry, no binding.

### 1.6 Independent adjudication — NOT IMPLEMENTED

The codebase has no adjudicated gold for 1505.05770. The `semantic_math_extractor.py` scoreboard compares against structural conservation, not gold; `adjudication_layer_contract.md` defines the contract but does not implement gold-based association validation. No pre-existing adjudication exists for this paper.

### 1.7 Recovery classification — NOT APPLIED

Recovery classification (EXACT / STRUCTURAL_EQUIV / LOSSY / UNRECOVERED) requires the 6-stage pipeline to have executed. Since Stage A/B are blocked, no recovery record is produced for the target equation. The existing `math_contract.py` types (ParseStatus, StructuralStatus, BackendStatus, SolutionStatus) are present, but end-to-end application is not.

---

## 2. Summary of actual outputs and missing transitions

| Stage | Tool | Status | Actual output | Missing transition |
|---|---|---|---|---|
| Source preservation | `arxiv_html_parser.py` | **✓ DONE** | 308 equations; target item 193 MathML + x-tex | None |
| Symbol/delimiter identity | `structural_ast_extractor.py`, `delimiter_identity.py`, `v2_delimiter_aware_structural_recovery.py` | **✓ DONE** | Full typed AST, source_glyph/source_tag/mathvariant per node | None |
| Physical geometry | `targeted_math_detector.py` | **✓ DONE** | PDF page 3 (1505.05770v6.pdf, 2.9 MB), 52 geometry candidates, 52 script candidates, 1773 visual candidates | None |
| Stage A (expr→region) | `math_pdf_association.py` | **✗ NOT IMPLEMENTED** | Sidecar schema only; no matching; geometry output on page 3 (52 candidates) exists | No AST-region binding code on the repo |
| Stage B (node→glyph) | `math_pdf_association.py` | **✗ NOT IMPLEMENTED** | Sidecar schema only; no matching | No Stage A output to chain from |
| Relationship geometry | — | **✗ NOT IMPLEMENTED** | — | Requires Stage A + Stage B |
| Independent adjudication | — | **✗ NOT IMPLEMENTED** | — | No gold for 1505.05770 |
| Recovery classification | `math_contract.py` types | **✗ NOT APPLIED** | — | Requires 6-stage pipeline execution |

---

## 3. Conclusion

The existing infrastructure now covers 3 of 7 recommended steps:
1. Source preservation ✓
2. Symbol/delimiter identity ✓
3. Physical geometry ✓ (PDF page 3, 52 geometry candidates — output saved to `arena_math_audit/targeted_math_detection.json`)

The remaining 4 steps are blocked or not implemented:
4. Stage A (expression → PDF region) — **NOT IMPLEMENTED** (geometry exists but no AST-region binding code)
5. Stage B (AST node → glyph) — **NOT IMPLEMENTED** (math_pdf_association.py is a sidecar writer only)
6. Relationship geometry — **NOT IMPLEMENTED** (depends on A and B)
7. Independent adjudication — **NOT IMPLEMENTED** (no gold for this paper)

**Bottom line:** the source, symbol, and geometry layers are complete for this paper, and the PDF plus `targeted_math_detector.py` pipeline is working. The AST-to-glyph association (Stage A/B), relationship geometry, adjudication, and recovery classification are not implemented in code. The frozen baselines and stage gates remain untouched. Future work is blocked solely on the absence of stage-gate implementation code, not on data.
