# Occurrence Lifecycle Ledger — Contract and Governance

**Date:** 2026-11-03
**Status:** Read-only governance artifact. No source modifications, no pipeline changes, no gate closures.
**Scope:** Common measurement contract for math extraction, recovery, solving, validation, and downstream integration.

---

## 1. Purpose

The King Wen math pipeline has accumulated substantial infrastructure across multiple independent processing paths: MathML tree parsing, flat-regex PDF extraction, vision/OCR recovery, occurrence-keyed accounting, typed Integral IR, delimiter identity, semantic-fidelity evaluation, and solver backends. These components produce results that look comparable but are not yet measured under a common contract.

The occurrence lifecycle ledger connects the evidence these components already produce into one persistent identity per equation occurrence, while preserving the distinct meanings of each processing stage. A failed stage must not erase the evidence from earlier stages. A rejected equation is still a valid source occurrence. An unsupported integral is still an extracted mathematical object.

This is a governance contract, not a code change. It defines what must be recorded, not how to implement the recording.

---

## 2. Foundational Principle

**An equation occurrence is the identity. Its rendered or normalized expression is content associated with that identity, not a substitute for it.**

- Occurrence identity is separate from: mathematical expression identity, parsed AST identity, reconstructed expression identity, and solver-result identity.
- SHA-256 over `(paper_id, version, locator, occurrence_index)` is the canonical identity key. No LaTeX, no AST, no solver output enters the key.
- Two identical LaTeX expressions in different papers are separate occurrences.
- An equation reconstructed into a different textual representation remains the same source occurrence.
- A failed stage retains all earlier-stage evidence.

---

## 3. Occurrence Lifecycle Stages

Every equation occurrence passes through a sequence of stages. Each stage produces evidence that is retained regardless of downstream outcomes.

| Stage | Evidence Retained | Failure Behavior |
|---|---|---|
| **Source** | Paper ID, version hash, page, HTML anchor, occurrence index, occurrence SHA-256 | Not applicable — source is the ground truth |
| **Extraction** | Original MathML, original LaTeX (x-tex annotation), extraction method, extraction path (MathML / flat-regex / vision) | If extraction fails, record the failure reason. Do not discard the occurrence. |
| **Parsing** | Parser version, AST (ExprNode tree), structural status, delimiter identity tokens | If parsing fails, record the failure reason and the raw input. Retain the AST if partial. |
| **Reconstruction** | Reconstructed expression, source-vs-reconstructed diff, delimiter pairing status | If reconstruction fails, record the failure reason. Retain the parsed structure. |
| **Recovery** | Recovery method, recovery status (RECOVERED / UNSUPPORTED / FAILED), failure reason | If recovery fails, record the failure reason. The occurrence remains in the corpus. |
| **Solving** | Solver implementation, version, input representation, equation role, solving policy, timeout, result, failure category | If solving fails or is inapplicable, record the failure reason and whether the equation was eligible for solving. |
| **Validation** | Independent checks, semantic fidelity, adjudication status, structural conservation | If validation fails, record which checks failed and why. |
| **Preservation** | Output reference, artifact hash, lineage chain, downstream consumers | Always recorded. Preservation is the terminal stage. |

### 3.1 Stage Independence Rule

Each stage is measured independently. A failure at stage N does not retroactively invalidate evidence from stages 1 through N-1. The ledger records the full chain, including the point of failure.

### 3.2 Null-Representation Rule

Occurrences with `latex: None` (22 reported in the 3,409-occurrence benchmark) must receive an explicit `missing-representation` status. They must not be silently discarded or converted to empty strings. Their source MathML may still contain usable information.

---

## 4. Extraction Path Separation

Three extraction paths exist. They are separate processing routes, not interchangeable implementations.

| Path | ID | Input | Implementation | Status |
|---|---|---|---|---|
| **MathML tree walk** | `path:mathml` | arXiv HTML MathML + x-tex annotations | `mathml_parser.py`, `arxiv_html_parser.py` | Verified: 991/991 on 2605.00155 |
| **Flat-regex / PyMuPDF** | `path:flat_regex` | PDF text blocks | `semantic_math_extractor.py` | Verified: 4,218 expressions from 245 papers; 8 solvable |
| **Vision / OCR** | `path:vision_ocr` | PDF image crops | `vision_comparison_pipeline.py`, Pix2Text | Verified: 4/4 recognized as `image_region`; reconstruction and fidelity not established |

### 4.1 Path Separation Rules

1. Paths must not be treated as interchangeable. A successful result on one path does not imply the same result on another.
2. A shared downstream occurrence contract may eventually make paths comparable, but only if the contract explicitly records which path produced each result.
3. CF-019 (seam mismatch) is an integration-seam finding: the verified MathML parser is not consumed by the flat-regex extraction path. It does not establish comparative accuracy.

---

## 5. Solver Result Reproducibility

Solver results must be recorded with enough context to reproduce and interpret them.

| Field | Purpose |
|---|---|
| Solver implementation | Which solver (SymPy, latex2sympy2, pylatexenc, etc.) |
| Solver version | Exact version string |
| Input representation | LaTeX, AST (ExprNode), Typed Integral IR, or other |
| Equation role | Equation, inequality, definition, theorem statement, integral, recurrence, etc. |
| Equation classification | How the occurrence was classified before solving |
| Solving policy | Which solving policy was applied (e.g., `solve_all.py`, `solve_provenance.py`) |
| Timeout | Whether a timeout was applied and its value |
| Result | Solved, simplified, partial, failed, or inapplicable |
| Failure category | Why solving failed (syntax error, timeout, not-an-equation, NotImplemented, etc.) |
| Eligibility | Whether the equation was eligible for symbolic solving under the policy |
| Independent verification | Whether the result was independently checked (semantic fidelity, structural conservation) |

### 5.1 Solvability Is Conditional

Many mathematical expressions are not equations that should produce a conventional solution. An integral, a definition, a theorem statement, a recurrence, and an inequality may all be valid mathematical occurrences without being solvable by the same SymPy workflow.

Solvability must be conditional on equation role and solving policy, not a universal metric. The 457 vs 120 solvability discrepancy reflects different runs, processing paths, or status definitions — not necessarily a mathematical contradiction.

---

## 6. Measurement-Layer Defect Dependency Map

The five measurement defects identified in the typed Integral IR report must be impact-mapped individually.

| Defect | Affects | Does NOT Affect |
|---|---|---|
| Dropped corpus field (preferred code path never ran) | Source extraction counts, corpus completeness | Delimiter identity tests, AST persistence tests |
| Glyph-vs-transliteration checker (phantom failures) | Structural classification counts, semantic fidelity scores | Occurrence conservation, solver outcomes |
| `\in`/`\infty` prefix match (18 phantom findings) | Structural classification counts (specifically relation-type classification) | Occurrence identity, extraction counts, solver outcomes |
| Subscript relation count (relations inside subscripts counted as top-level) | Structural classification counts, relation-type classification | Occurrence identity, extraction counts, solver outcomes |
| Missing argparse (`--output` silently ignored) | Output artifact production, reproducibility | In-memory processing results, metric computation |

### 6.1 Rule

A measurement bug invalidates only the metrics that depend on it, unless evidence establishes a broader impact. Defects must be classified as affecting extraction counts, occurrence identity, structural classification, recovery counts, or solver outcomes — not blanket "all invalid."

---

## 7. Pipeline Execution and Usage Registry

Available components are not necessarily active dependencies. The following registry tracks actual usage, not just availability.

| Field | Purpose |
|---|---|
| Pipeline ID | Stable processing-path identity |
| Entry point | Actual callable script/function |
| Input population | Exact papers and occurrences processed |
| Commit/version | Implementation provenance |
| Run ID | Unique execution identifier |
| Output artifact | Exact result location |
| Measurement contract | Definitions used for reported numbers |
| Downstream consumers | Actual consumers, not merely potential callers |

### 7.1 Components requiring usage verification

| Component | Available? | Tested? | Actually Used in Production Workflow? |
|---|---|---|---|
| `mathml_parser.py` | Yes | Yes (991/991) | **Unknown** — not consumed by `semantic_math_extractor.py` (CF-019) |
| `semantic_math_extractor.py` | Yes | Yes | **Unknown** — produces 4,218 expressions from 245 papers |
| `math_recovery_tool.py` | Yes | Yes | **Unknown** — produces recovery results |
| `e2e_math_pipeline.py` | Yes | Yes (991 equations, 448 solved) | **Unknown** — CLI entry point |
| `vision_comparison_pipeline.py` | Yes | Yes (4/4 recognized) | **Unknown** — 4 candidates on 1 paper |
| `math_occurrence_accounting.py` | Yes | Yes (12 tests) | **Unknown** — occurrence ledger implementation |

---

## 8. King Wen Integration Levels

Three distinct integration levels exist between math evidence and King Wen expansion. They must not be conflated.

| Level | Route | Status |
|---|---|---|
| **Level 1** | Paper text → King Wen intent | Established. `recover_training_data.py` processes paper text through `extract_intent()` → `shotgun_expand()` → consensus. 6.8 GB artifact, 54 papers, 82,224 records, 1,536 records per paper. |
| **Level 2** | Equation text/context → King Wen lexical intent | Working experiment. `math_to_kingwen_adapter.py` routes equation-level text through King Wen. 989/991 classified as "understand", 2/991 as "destroy", 989/991 zero matched intents. Working but not meaningful mathematical-semantic discrimination. |
| **Level 3** | Structured mathematical evidence → King Wen expansion | **Unestablished.** ExprNode IR, SymPy solutions, structural conservation scores, recovery adjudication, and occurrence identities are not shown to be consumed by any King Wen generator. |

### 8.1 Preservation Rule

The original 6.8 GB artifact (`recover_training_data.py` output) must not be discarded or treated as replaceable by a future normalized representation. The historical text, tokenization, expansion associations, and provenance are valuable evidence in their own right.

---

## 9. Mathematical Evidence Graph

The existing work approaches a more useful architecture than a conventional extraction pipeline. The conceptual model:

1. **Papers** contain **equation occurrences**.
2. **Occurrences** have **source representations** (MathML, LaTeX, PDF text, image crop).
3. **Representations** produce **parsed structures** (AST, ExprNode tree, Typed Integral IR).
4. **Structures** may undergo **reconstruction and recovery** (delimiter identity, semantic fidelity, adjudication).
5. **Solver attempts** operate on particular representations (SymPy on LaTeX, on AST, on IR).
6. **Validation results** attach to specific attempts (structural conservation, semantic fidelity, adjudication status).
7. **Outputs** retain links to the original occurrence (occurrence SHA-256, source hash, extraction hash).
8. **Downstream systems** consume outputs without erasing mathematical provenance (King Wen expansion, adjudication, training data).

This is not simply a pipeline status tracker. It is a record of how a mathematical claim or expression moved through different representations and operations. Failed and partial results remain useful instead of disappearing from the successful-output population.

---

## 10. Recommended Research Priorities

| Priority | Investigation | Expected Value |
|---|---|---|
| 1 | Occurrence lifecycle and provenance continuity | Prevents silent loss across stages |
| 2 | CF-019 downstream impact trace | Establishes which outputs depend on each extraction path |
| 3 | Solver discrepancy analysis | Makes solvability measurements interpretable |
| 4 | Measurement-defect dependency map | Establishes which benchmark results remain trustworthy |
| 5 | Null-LaTeX failure characterization | Prevents a small number of records terminating processing |
| 6 | Pipeline execution registry | Separates available components from actual usage |
| 7 | Full-corpus recovery coverage accounting | Establishes what has actually been processed |

### 10.1 Null-Representation Rule

The 22 `latex: None` occurrences in the 3,409-occurrence benchmark must remain represented in the corpus with an explicit `missing-representation` status. They must not be silently discarded or converted to empty strings. Their source MathML may still contain usable information.

---

## 11. Relationship to Existing Governance

This contract does not replace or modify any existing governance artifact:

- The **cross-document finding authority map** (`docs/cross-document-finding-authority-map-2026-11-03.md`) remains the canonical finding registry (21 findings, CF-001 through CF-021).
- The **math-pipeline evidence matrix** (`docs/math-pipeline-evidence-matrix-2026-11-03.md`) remains the operational baseline.
- The **QSMC-1 Gate 2** remains OPEN.
- The **B4 Gate 2** remains BLOCKED by U-07.
- The **Lua migration prerequisite** remains not yet passed.

This contract adds a governance layer that defines how existing evidence should be connected, not how it should be changed.

---

*End of occurrence lifecycle ledger contract. This is a read-only governance artifact. No source modifications, pipeline changes, gate closures, or remediation acceptance are implied by its creation.*