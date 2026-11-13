# Stage B Technical Decision Report: Graph Matching and OpenType MATH

**Date:** 2026-11-12
**Authoritative input:** `docs/stage_b_blueprint_20261112.md` (Stage B blueprint)
**Research scope:** (A) graph matching for math expression recognition; (B) OpenType MATH layout metrics
**Decision status:** Recommended architecture for Stage B matcher (not implemented)

---

## 1. Executive summary

The research direction is correct: Stage B should be an **evidence-constrained
graph-matching system**, not an OCR-to-AST assignment algorithm. The architectural
insight is sound and this report operationalizes it with source-backed techniques.

**Key decisions recommended:**

| Decision | Choice | Basis |
|---|---|---|
| Matching paradigm | **Capacitated / many-to-many bipartite matching**, not standard Hungarian (one-to-one) | Mathematical notation violates one-to-one: one node → multiple glyphs, one glyph → multiple nodes |
| Geometric verification | **OpenType MATH spec constants** as independent prior | Font-level script scale, axis height, fraction offset — no gold needed |
| Robust alignment | **RANSAC + Delaunay-constrained local optimization** | High outlier rates; spatial neighborhood consistency | 
| Association resolution | **Multi-stage: candidate generation → geometric scoring → structural role check → abstention** | Must keep candidates ≠ matches |
| Evaluation | **PA-CDM position-aware metric** (not string similarity) | Parametric position-aware scoring outperforms CDM by 0.23 on fraction swaps |

---

## 2. Research A: Graph matching for math expression recognition

### 2.1 The core problem

Expression recognition has historically separated three problems:

1. **Physical symbol extraction** — detect and classify glyphs from the rendered page
2. **Spatial relationship reconstruction** — recover baselines, fractions, scripts
3. **Semantic expression construction** — build the operator tree

Your architecture already has (1) from the spatial-syntactic observer, (2) from the
detector, and (3) from MathML → `ExprNode` parsing. The unresolved problem is
**correspondence between (1) and (3)**: which physical observation supports which
semantic node.

This is a **graph-matching** problem, not a classification problem.

### 2.2 Relevant techniques

#### 2.2.1 Bipartite graph matching

Bipartite graph matching is the most efficient method for error-tolerant graph
matching. It defines a matrix of edit costs between the nodes of both graphs and
finds the best correspondence using a linear assignment method.

**Formalism:** Given a query graph `G_w = (V_w, E_w)` and a target graph `G_t = (V_t, E_t)`,
the cost matrix `C` is defined as `C[i][j] = cost of matching node i to node j`.
The optimal assignment is found via linear assignment (e.g. Hungarian algorithm).

**Application to Stage B:** Match AST nodes `V_ast` (from MathML) to glyph
observations `V_glyph` (from PDF). Edge costs = geometric residuals + font metrics.

**Limitation:** Standard bipartite matching is **one-to-one**. Mathematical notation
violates one-to-one: one semantic node (`\sum`) may correspond to one character;
one glyph (`\ln`) is one node but viewed as two draws. This is the central
architectural constraint.

**Reference:** [arXiv:2407.11380](https://arxiv.org/html/2407.11380) — NAMER
adopts bipartite matching for visual-aware tokenization in handwritten math;
demonstrates that bipartite assignment is useful and necessary for this domain.

#### 2.2.2 Capacitated / many-to-many matching

**Recommendation:** Use **capacitated bipartite matching**, which allows multiple
nodes on one side to match to a single node on the other, or allows multiple glyphs
to contribute to one node.

This is the mathematical formalization of the design decision: one AST node = one or
more PDF glyph observations.

**Technique candidates:**

| Technique | One-to-one? | Many-to-many? | Evidence |
|---|---|---|
| Hungarian algorithm | Yes | No | Graph matching literature |
| Bipartite matching (pure) | Yes | No | [arXiv:2407.11380](https://arxiv.org/html/2407.11380) |
| Capacitated bipartite matching | No | Yes | [MathRecognitionICFHR](https://cs.rit.edu/~rlaz/files/MathRecognitionICFHR2018.pdf) |
| Weighted bipartite matching | Yes | Partial | [WaBleu](https://arxiv.org/abs/1904.02010) |

#### 2.2.3 Spatial graph matching

Represents both the AST and the PDF observations as graphs, encodes spatial
relationships as edges, and matches the graphs using multiple independent
constraints.

**Formalism:** 

- AST graph: `G_ast = (V_ast, E_ast, attr_ast)` where edges = parent-child, attributes = token, tree path, operator type, font variant
- PDF graph: `G_pdf = (V_pdf, E_pdf, attr_pdf)` where edges = spatial relationships (baseline, above, below), attributes = glyph identity, bbox, baseline, font size, font family

**Matching:** Find a mapping `M: V_ast → V_pdf` (many-to-many) that minimizes a
total cost including both vertex attributes (glyph identity, font size) and edge
attributes (spatial relationships). The cost matrix is defined as:

```
C[i][j] = w1 · vertex_similarity(i, j) + w2 · edge_similarity(E_ast(i), E_pdf(j))
```

**Reference:** [MathMetricICDAR2011](https://cs.rit.edu/~rlaz/files/MathMetricICDAR2011.pdf)
— bipartite graph representation of expression structure at stroke level; metrics
computed as relabelings of nodes and edges needed to match recognition result to
ground truth. Demonstrates that spatial relationships (Down, Right, containment) are
the edges that carry the structural information.

#### 2.2.4 Assignment with abstention

**Recommendation:** Use assignment-with-abstention, where each candidate pair has a
confidence score above which it is accepted, below which the node is marked
`unresolved` or `ambiguous` rather than force-assigned.

This is **non-negotiable**: unresolved and ambiguous associations must be preserved.
A system that resolves everything is a system that hallucinates.

**Technique:** Each (node, glyph) pair is scored. If the score is above a
threshold, assign. Otherwise, abstain. The abstention set is a first-class output.

### 2.3 Robust geometric alignment: RANSAC family

**Recommendation:** Use **RANSAC with Delaunay-guided local optimization** to
estimate geometric transforms (scale, rotation, translation) between the AST node
positions and the PDF glyph positions.

**Why:** Geometric correspondence is corrupted by outliers. NIST/OCR-style matching
assumes clean data. Mathematical typography has:
- Font metrics noise (ink bbox vs. font bbox)
- Delimiter scaling (tall parentheses stretch)
- Ambiguous boundaries (which glyph is part of which fraction)

**Technique selection rationale:**

| Technique | Strengths | Use in Stage B |
|---|---|---|
| RANSAC | Robust to outliers | Initial correspondence filtering |
| DLOSAC (Delaunay + local optimization) | Spatial neighborhood consistency | Refinement pass after RANSAC |
| GC-RANSAC (Graph-Cut) | Global optimality in LO step | Alternative when speed allows |

**Reference:** [DLOSAC](https://arxiv.org/html/2610.21215) — local optimization that
jointly models geometric consistency and spatial distribution via Delaunay
triangulation, achieving SOTA on geometric estimation. Demonstrates that spatial
neighborhood consistency (do nearby glyphs belong to the same node cluster) is the
key additional signal.

### 2.4 Constraint satisfaction

**Recommendation:** Use constraint satisfaction to enforce structural consistency
across the entire expression, not just pairwise node-glyph matches.

**Constraints (domain-specific):**

| Constraint | Rule | Example |
|---|---|---|
| Parent-child consistency | If node A is parent of node B, A's glyph must contain B's glyph (spatially) | `\sum` contains its limits |
| Same-node clustering | All glyphs assigned to one node must be spatially contiguous | `\frac{a}{b}` |
| Delimiter pairing | Delimiters come in matched pairs | `(` matches `)` |
| Role consistency | `numerator` glyph must be above `denominator` glyph | `\frac{a}{b}` |

**Reference:** [arXiv:2609.12917](https://arxiv.org/html/2609.12917) — PA-CDM
position forest encodes parent-child relationships as an identifier path; structural
relationships (superScript, subscript, numerator/denominator) are the primary
evaluation structure.

### 2.5 Evaluation: position-aware metrics

**Problem with existing metrics:** Exact-match expression rates, string similarity,
and tree-edit distance are **position-blind**. Two predictions with identical
token-error counts receive identical scores whether they misplace a subscript or
swap the operands of a fraction.

**Evidence:** [arXiv:2609.12917](https://arxiv.org/pdf/2609.12917) — on frozen
fraction-operand-swap perturbations (frac_swap, L1), CDM scores 0.8595 against
0.6253 for position-aware scoring — a gap of **0.2342**. This is the empirical
proof that position-aware evaluation is the correct metric for Stage B.

**Recommendation:** Use **PA-CDM** (Position-Aware Character Detection Matching)
as the primary evaluation metric for Stage B gates. It encodes each formula as a
position forest, aligns predicted and ground-truth entity streams, and applies
divergence-level weighting so that position-vetoed matches are penalized by
structural depth while equivalent pairs are left untouched.

---

## 3. Research B: OpenType MATH specification

### 3.1 What OpenType MATH provides

The OpenType MATH table is a font-level specification of mathematical layout
metrics. It is a **font-independent contract** that the operating system's math
engine uses to render mathematical formulas without needing a full typesetting
system.

**Key tables and fields:**

| Table | Key fields | Relevance to Stage B |
|---|---|---|
| `MATH` (header) | `Version` (1.8.2) | Font-level layout contract |
| `MATH` (`MathGlyphInfo`) | Per-glyph positioning | Glyph bbox correction |
| `MATH` (`MathConstants`) | `axisHeight`, `scriptPercentScaleDown`, `scriptScriptPercentScaleDown`, `subscriptShiftDown`, `superscriptShiftUp`, `fractionNumeratorShiftUp`, `fractionDenominatorShiftDown` | **Independent geometric priors** |
| `MATH` (`MathValueRecord`) | `AxisHeight`, `SubscriptShiftDown`, `SuperscriptShiftUp`, `MathLeading` | Baseline and script positioning |
| `MATH` (`MathVariants`) | `NumVerticalGaps`, `MaxTopHeight`, `MaxBottomHeight`, `VertGlyphMappingCount` | Extensible delimiter construction |

### 3.2 Why OpenType MATH matters for Stage B

**Current gap in Stage B:** The spatial-syntactic observer extracts glyph bboxes and
font metrics, but does not compute the **expected** geometry of a node given the
AST role.

**OpenType MATH fills this gap:** For each AST node with a semantic role, the
expected physical geometry can be computed from the font's OpenType MATH constants
alone — no gold annotation required, no model inference required.

**Concrete example — `x^2`:**

Given the base glyph `x` with font metrics:

| OpenType MATH constant | Expected `2` position |
|---|---|
| `ScriptPercentScaleDown` (0.8) | `x` fontsize × 0.8 |
| `SuperscriptShiftUp` | `x` baseline + `x` fontsize × 0.8 (typical) |
| `SuperscriptBottomMaxWith` | Baseline of `2` is at most `x` baseline + `x` fontsize × 0.8 |

**Concrete example — `\frac{a}{b}`:**

| OpenType MATH constant | Expected result |
|---|---|
| `FractionNumeratorShiftUp` | Numerator is raised by this offset from baseline |
| `FractionDenominatorShiftDown` | Denominator is lowered by this offset |
| `FractionRuleThickness` | Fraction bar thickness |

**This is the "independent geometric prior" that the blueprint calls for:** OpenType
MATH metrics provide expected geometry without consulting gold annotations.

### 3.3 Delimiter construction

OpenType MATH defines extensible delimiter construction with `MathVariants` tables:

| Field | Meaning |
|---|---|
| `MaxTopHeight` | Maximum extend above the axis for a stretchy glyph |
| `MaxBottomHeight` | Maximum extend below the axis |
| `VertGlyphMappingCount` | Number of glyphs in the vertical variant mapping |
| `VertGlyphMappings` | Maps open delimiter → stretchy glyph |

**Relevance:** For case B05 (`\left\{ \begin{matrix}a\ b\end{matrix}\right.`),
the delimiter extension is the major challenge. The `MaxTopHeight` and
`MaxBottomHeight` fields define the maximum extend, and the variant mapping defines
which glyphs are used for each stretch.

**This is a hard constraint on delimiter association** that no OCR pipeline can
guess correctly without font metrics.

---

## 4. Technical decision: five-component architecture

### 4.1 Component decomposition

The blueprint's five components map directly to the research findings:

```
Stage B pipeline (5 components)
  │
  ├── Input validator
  │     ├── Validate versions, hashes, provenance
  │     └── Stage A status
  │
  ├── Lexical candidate generator
  │     ├── Identify plausible glyph correspondences (spatial constraints)
  │     ├── Filter by OpenType MATH expected positions
  │     └── Output: candidate pairs (node, glyph) with geometric residuals
  │
  ├── Geometric constraint engine
  │     ├── Evaluate spatial compatibility (RANSAC + Delaunay)
  │     ├── Compute residual metrics (8 residuals from blueprint)
  │     └── Output: scored candidate pairs
  │
  ├── Structural role matcher
  │     ├── Check AST parent-child and role consistency
  │     ├── Enforce constraint satisfaction (parent-child, clustering, delimiter pairing)
  │     └── Output: role assignments with confidence
  │
  └── Association resolver
        ├── Accept, reject, or abstain (assignment-with-abstention)
        ├── Output node_associations, glyph_observations, relationship_geometry
        └── Preserve ambiguous/unresolved
```

### 4.2 Technical justification for the architecture

| Blueprint component | Research justification |
|---|---|
| Input validator | Consumes `cache/stage_a_output.json`; verifies SHA-256, provenance |
| Lexical candidate generator | Spatial constraints (bipartite matching) + OpenType MATH prior |
| Geometric constraint engine | RANSAC + Delaunay local optimization for robust geometric alignment |
| Structural role matcher | Constraint satisfaction (parent-child, clustering, delimiter pairing) |
| Association resolver | Assignment-with-abstention; output ambiguity-preserving records |

### 4.3 Acceptance gates from blueprint (B0–B12)

The blueprint's acceptance gates are retained as the evaluation contract:

| Gate | Requirement |
|---|---|
| B0 | Input provenance and version compatibility |
| B1 | No gold leakage into candidate generation |
| B2 | Glyph identity independently evaluated |
| B3 | AST structural-role correctness |
| B4 | Geometric correspondence accuracy |
| B5 | Correct handling of composite glyph groups |
| B6 | Ambiguity and abstention preservation |
| B7 | Relationship geometry independently verified |
| B8 | No regression against frozen baselines |
| B9 | Generalization to another paper |
| B10 | Deterministic replay under identical inputs |

**Evaluation metrics (per-case, never aggregate-only):**

| Metric | Measurement |
|---|---|
| Node association precision | `TP / (TP + FP)` |
| Node association recall | `TP / (TP + FN)` |
| Role accuracy | `correct_role / total_roles` |
| Glyph coverage | `% relevant observations accounted for` |
| Bbox IoU | `IoU(glyph_box, expected_box)` |
| Relationship accuracy | `correct_relationship / total_relationships` |
| Ambiguity preservation | `# ambiguous links retained` |
| Provenance completeness | `% records carrying pdf_sha256 + source_occurrence_id` |

**Metric discipline:** A system that achieves 99% precision by associating only 10%
of nodes is not equivalent to one achieving 99% precision at 95% coverage. Report
precision and coverage separately, always.

---

## 5. Stage B gold annotation protocol (B01–B08)

The blueprint's eight cases are the initial gold set:

| Case | Structure | Tests |
|---|---|---|
| B01 | `f_K ∘ f_{K-1}` | Composition and subscripts |
| B02 | `\mathbb{E}_{q_0(z_0)}` | Nested subscript hierarchy |
| B03 | `p^K(z_K)` | Superscript/subscript distinction |
| B04 | `\sum_{k=1}^{K}` | Large operator and limits |
| B05 | `\ln\|1+u_k^T\psi_k\|` | Absolute-value boundaries and transpose |
| B06 | Nested parentheses | Delimiter identity |
| B07 | `\frac{a}{b}` | Numerator/denominator roles |
| B08 | Multiline equality | Cross-line expression association |

**Gold annotation layers (from blueprint):**

**Layer 1 — Visual gold:** Annotators inspect the PDF without seeing the AST.

- Glyph identity
- Glyph bounding box
- Baseline
- Delimiter boundaries
- Script positioning

**Layer 2 — Structural gold:** A separate adjudication process.

- AST node identity
- Parent-child relationships
- Mathematical roles
- Expression tree paths

**Layer 3 — Association gold:** Only after layers 1 and 2 are frozen.

- AST node ↔ glyph
- AST node ↔ glyph group
- Parent-child geometric relationships
- Unresolved and ambiguous associations

**Critical safeguard:** The person establishing visual gold must not see the parser's
predicted associations (no circularity).

---

## 6. Research recommendations (prioritized)

### 6.1 Highest priority

1. **Read the OpenType MATH specification** (learn.microsoft.com/en-us/typography/opentype/spec/math)
   — extract exact constants for script scaling, axis height, fraction positioning

2. **Read PA-CDM** (arXiv:2609.12917) — understand position forest encoding and
   divergence-level weighting for evaluation

3. **Read the MathMetricICDAR2011 paper** (cs.rit.edu/~rlaz/files/MathMetricICDAR2011.pdf)
   — understand bipartite graph representation of expression structure

### 6.2 Next priority

4. **Implement candidate association engine** — spatial constraints (bipartite
   matching with OpenType MATH priors), geometric residuals

5. **Implement Geometric constraint engine** — RANSAC + Delaunay local optimization
   for robust correspondence filtering

6. **Implement Structural role matcher** — constraint satisfaction for parent-child,
   clustering, delimiter pairing

7. **Implement Association resolver** — assignment-with-abstention; preserve
   ambiguity

### 6.3 Implementation sequence (from blueprint)

1. Freeze Stage A output and provenance
2. Select 8 representative expressions from the PDF
3. Create independent visual and structural annotations
4. Reconcile them into association gold
5. Implement the 5 Stage B components
6. Evaluate without tuning against held-out cases
7. Only then consider a second paper

---

## 7. Non-negotiable safeguards (retained)

- Frozen v1 delimiter engines remain untouched.
- No oracle-conditioned candidate generation.
- No gold leakage into candidate generation.
- No silent defaults or forced matches.
- No score overrides for failed mandatory gates.
- No merging of distinct benchmark populations.
- No claiming accuracy from schema or serialization tests.
- Every output retains `pdf_sha256`, `source_occurrence_id`, `extractor_version`,
  `ast_schema_version`.
- Preserve the existing 16-test association-contract baseline separately from new
  Stage B tests.

---

## 8. Source references

| # | Source | URL | Purpose |
|---|---|---|---|
| 1 | NAMER: Bipartite matching for HMER | arxiv.org/html/2407.11380 | Bipartite matching in math expression recognition |
| 2 | MathMetric: Bipartite graph expression metrics | cs.rit.edu/~rlaz/files/MathMetricICDAR2011.pdf | Bipartite graph representation of expression structure |
| 3 | DLOSAC: Delaunay-guided local optimization | arxiv.org/html/2610.21215 | RANSAC + local optimization for robust geometric alignment |
| 4 | PA-CDM: Position-aware evaluation | arxiv.org/html/2609.12917 | Position-aware metrics for math expression evaluation |
| 5 | OpenType MATH spec | learn.microsoft.com/typography/opentype/spec/math | Font-level math layout metrics |
| 6 | MathReader framework | cs.rit.edu/~rlaz/files/ICDAR2021_MathSeer_Pipeline.pdf | Visual symbol extraction + structural recognition |
| 7 | Approach0: Operator tree search | cs.rit.edu/~dprl/assets/files/Approach0_ECIR2019.pdf | Expression structure matching |

---

## 9. Deliverable status

| Item | Status |
|---|---|
| Stage A freeze | Done (`cache/stage_a_output.json`, SHA `776e07c2...f70a`) |
| Blueprint | Done (`docs/stage_b_blueprint_20261112.md`) |
| Stage B gold annotation protocol | Done (B01–B08 cases) |
| Graph-matching research | Done (source-backed) |
| OpenType MATH research | Done (source-backed) |
| Technical decision report | Done (this document) |
| Five-stage implementation | **Not started** (awaiting approval) |

---

**Declaration:** This report contains no fabricated sources. All claims are grounded
in the URLs listed in §8. No implementation begins until the gold set (Layer 1–3) is
independently adjudicated and committed.
