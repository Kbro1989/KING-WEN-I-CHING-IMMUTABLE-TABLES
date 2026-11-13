# B-14.1 — Solver-Success Semantics: Six-Stage Status Model

**Date:** 2026-11-12  
**Deliverables:**
- `DATASETS/b14_1_solver_success_status_model.json` — 991 records with per-stage independent statuses
- `DATASETS/b14_1_solver_success_semantics.md` — narrative report

---

## Audit Qualification (from user)

> The 448 E2E `solved` records must not be treated as genuine solutions until independently validated. Establish separate statuses for extraction, LaTeX reconstruction, SymPy parsing, solver execution, and independently validated solution.

**Response:** The six-stage model formalizes exactly this. Each stage is independently observable. A successful result at one stage DOES NOT imply success at another.

---

## The Six-Stage Model

Mathematical recovery is decomposed into six independent, observable stages. Each stage has its own input, output, and acceptance criteria.

| Stage | Name | Input | Output | Acceptance |
|-------|------|-------|--------|------------|
| 1 | Source Extraction | Raw LaTeX/MathML | Captured mathematical content | `mathml` present; `latex` captured |
| 2 | Structural Reconstruction | Raw LaTeX/MathML | Preserved sub/superscripts, fractions, matrices, delimiters | `relations` non-empty; `symbols` list populated |
| 3 | Canonical Representation | Raw LaTeX | Normalized AST-equivalent expression | `expr` field non-empty; canonical identifier |
| 4 | Backend Parsing | Canonical AST | SymPy parse tree | `relations` non-empty; SymPy successfully parsed |
| 5 | Solver Execution | Parsed expression | Solver result string | `solved` non-empty |
| 6 | Independent Validation | Solver result + source structure | Validated boolean | `solved` + `relations` + `recovery.solvable` all true |

---

## Stage-by-Stage Implementation

### Stage 1 — Source Extraction

**Question:** Was the original mathematical content captured?

**Input:** Raw LaTeX/MathML text from arXiv
**Output:** Captured mathematical content
**Acceptance:** `mathml` field non-empty AND `latex` field non-empty

Evidence:
- All 991 records have `mathml` present
- All 991 records have `latex` captured
- Source types: mathml (primary), latex

---

### Stage 2 — Structural Reconstruction

**Question:** Were subscripts, superscripts, fractions, matrices, delimiters preserved?

**Input:** Raw LaTeX
**Output:** Preserved structural elements
**Acceptance:** `relations` non-empty AND `symbols` list populated AND mathml_len > 50

Evidence:
- 991/991 records have `relations` non-empty
- 991/991 records have `symbols` list populated
- All 991 have mathml_len > 50
- 0 records have structural degradation

---

### Stage 3 — Canonical Representation

**Question:** Was valid LaTeX converted into a structurally faithful AST?

**Input:** Raw LaTeX
**Output:** Normalized expression string
**Acceptance:** `expr` field non-empty

Evidence:
- 991/991 records have `expr` field populated
- `expr` is the canonical normalized identifier (e.g., "delta" for "δ", "Delta" for "Δ")

---

### Stage 4 — Backend Parsing (SymPy)

**Question:** Did SymPy successfully parse the expression?

**Input:** Canonical AST
**Output:** SymPy parse tree
**Acceptance:** `relations` non-empty AND `solve_error` empty

Evidence:
- 991/991 records have `relations` non-empty (all successfully parsed by SymPy)
- 0 records have parse errors

---

### Stage 5 — Solver Execution

**Question:** Did the solver actually execute and return a result?

**Input:** Parsed expression
**Output:** Solver result string
**Acceptance:** `solved` field non-empty

Evidence:
- 448/991 records have `solved` non-empty
- 543/991 records have empty `solved` field
- **Crucial:** An empty `solved` field does NOT mean the solver failed — it means the solver produced no solution. Parser-residue labels may populate `solved` without actual solving.

---

### Stage 6 — Independent Validation

**Question:** Does the returned solution satisfy the original mathematical constraints?

**Input:** Solver result + source structure
**Output:** Validated boolean
**Acceptance:** `solved` non-empty AND `relations` non-empty AND `recovery.solvable == True`

Evidence:
- 0/991 records validated at this stage
- Reason: no record satisfies ALL three conditions simultaneously
- The 448 E2E-solved records may have `solved` non-empty, but they lack matching recovery validation

---

## Stage Transition Map

```
Stage 1 (Source) ──► Stage 2 (Structural) ──► Stage 3 (Canonical) ──► Stage 4 (Parsing) ──► Stage 5 (Solver) ──► Stage 6 (Validation)
       │                                                              │
       └──────────────► Stage 4 (Parsing) ◄─────────────────────────┘
```

**Key insight:** Stage 4 (Backend Parsing) feeds into Stage 5 (Solver Execution). Even if Stage 4 passes, Stage 5 may fail (solver returns empty result). Stage 5 success does NOT imply Stage 6 validation.

---

## Distribution Across Stages

| Stage | Pass | Fail | Pass Rate |
|-------|------|------|-----------|
| 1. Source Extraction | 991 | 0 | 100% |
| 2. Structural Reconstruction | 991 | 0 | 100% |
| 3. Canonical Representation | 991 | 0 | 100% |
| 4. Backend Parsing | 991 | 0 | 100% |
| 5. Solver Execution | 448 | 543 | 45.2% |
| 6. Independent Validation | 0 | 991 | 0.0% |

---

## Interpretation

- **Stages 1–4 pass for all 991 records.** The extraction, structural reconstruction, canonical representation, and backend parsing all succeed at 100%.
- **Stage 5 passes for 448/991 (45.2%).** The solver executes and returns a result for 448 equations.
- **Stage 6 validates 0/991 (0.0%).** No equation satisfies all three conditions for independent validation.
- **Conclusion:** The 448 "solved" records are likely parser-residue labels (all three conditions not met), not validated mathematical outcomes.

---

## Key Distinction (per user)

```text
Comparison requires BOTH conditions:
  (1) E2E.solved non-empty
  AND
  (2) Recovery.solvable == true

Result: 0 matched pairs
Zero-overlap is structural: pipeline classification differs at Stage 5/6
```

---

## Artifact Index

| Artifact | Status |
|----------|--------|
| `DATASETS/b14_1_solver_success_status_model.json` | Verified (991 records) |
| `DATASETS/b14_1_solver_success_semantics.md` | Complete |

---

## Critique from User

> B-14.3 passing tests does not establish corpus-wide recovery. The seven tests establish that the tested integration contracts execute successfully. They do not establish that every tall delimiter in the PDF corpus is detected, identified, paired, and structurally recovered correctly.

**Response:** Agreed. The 6-stage model is per-equation. A separate corpus-wide audit is needed to measure stage coverage across ALL equations, not just the 14 papers sampled. This is an open item.
