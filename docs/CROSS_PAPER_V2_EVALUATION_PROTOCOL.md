# King Wen Math: Cross-Paper Delimiter Generalization v2 Evaluation Protocol

## 1. Executive Protocol Summary

This document establishes the governing evaluation protocol for the **v2 Cross-Paper Delimiter Generalization Program**. It codifies the transition from the frozen v1 baseline into v2 development while strictly preserving the five-axis conjunctive acceptance contract and immutable reference separation.

```
Evaluation Protocol Lifecycle:
┌────────────────────────────────────────────────────────┐
│ Frozen v1 Reference Baseline (Main Branch)             │
│ - Spec: 188ac350... (FROZEN)                           │
│ - Engine: 8211592a... (FROZEN)                         │
│ - Registry: da4c166b... (FROZEN)                       │
│ - Evaluation Report: 85320ae7... (FROZEN)              │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ v2 Remediation Program (Dedicated v2 Branch)           │
│ Phase 1: Re-evaluate CP-001, CP-002, CP-003           │
│   - Apply engine fixes EL-001, EL-002, EL-003, EL-004  │
│   - Require 5/5 dimensions PASS under conjunctive gate │
│   - Verify all 4 negative controls per case            │
│ Phase 2: Unseen Corpus Expansion                       │
│   - Ingest previously unseen academic PDFs             │
│   - Test diverse font programs & math engines          │
│   - Independent ground-truth registration              │
└────────────────────────────────────────────────────────┘
```

---

## 2. Five-Axis Conjunctive Acceptance Policy

Every candidate mathematical expression evaluated under v2 MUST satisfy all five dimensions simultaneously to achieve the verdict `PASSED_CERTIFIED`. Failure in any single dimension results in `FAILED`.

$$\text{Verdict} = \bigwedge_{i=1}^{5} \text{dim}_i \land \bigwedge_{j=1}^{4} \text{NC}_j$$

| Axis | Acceptance Criterion | Strict Verification Standard |
| :--- | :--- | :--- |
| **`dim_1_geometric_localization`** | Spatial bounds coverage | Display bounding box encompasses complete expression, including multi-line vertical spans, fractional bars, and trailing exponents/subscripts. |
| **`dim_2_glyph_completeness`** | 100% Glyph constituent inventory | Every constituent glyph in extensible assemblies (e.g. 7-piece brackets) and specialized math fonts is recognized and localized. |
| **`dim_3_structural_recovery`** | Structural AST fidelity | Reconstructed AST preserves operator kinds, bounds, nesting, and directional enclosure pairing without operator flattening. |
| **`dim_4_semantic_fidelity`** | Computational & semantic validity | Zero mathematical residual ($|\text{target} - \text{other}| = 0$) and correct variable-matrix indexing. |
| **`dim_5_boundary_isolation`** | Crop perimeter boundary clearance | Zero intrusion of adjacent page headers, body text, or neighboring equations across vertical gutters (Authoritative standard: $g_{\min} \ge 2.0\text{ pt}$). |

### 2.1 Gate D4 Safety Margin Decomposition & Calibration
The certified perimeter safety margin accounts for three distinct physical and computational uncertainties:

$$g_{\text{required}} = g_{\text{geometry uncertainty}} + g_{\text{rendering uncertainty}} + g_{\text{downstream processing}}$$

- **Authoritative Preservation Invariant:** The historical $2.0\text{ pt}$ clearance threshold remains the governing acceptance standard. It must never be silently weakened.
- **Experimental Calibration Candidate:** A $1.5\text{ pt}$ threshold is tracked as a versioned comparative metric evaluated side-by-side against the $2.0\text{ pt}$ baseline across all benchmark targets. This evaluation explicitly measures whether reduced margins impact delicate structural features (such as thin macron bars, trailing superscripts, or tight inter-equation gutters like ViLT's $2.45\text{ pt}$ gutter to Eq 4). Both thresholds are reported in evaluation runs.

---

## 3. Negative-Control Invariants

Each registered case must be subjected to four negative controls to prevent false positives:

1. `NEG_INCOMPLETE_DELIMITER_ASSEMBLY`: Rejects assemblies missing constituent pieces (e.g. 6 of 7 pieces).
2. `NEG_UNMATCHED_DELIMITERS`: Rejects isolated open or close delimiters without valid structural partners.
3. `NEG_MISMATCHED_DELIMITER_TYPES`: Rejects pairs combining mismatched delimiter kinds (e.g. open bracket with close parenthesis) regardless of geometric overlap score.
4. `NEG_INTRUDING_BOUNDARY_NOISE`: Rejects candidates whose bounding box encompasses external text tokens or neighbor equation marks.

---

## 4. Multi-Channel Separation of Concerns

Evaluation results must be reported across three decoupled channels to prevent perceptual approximations from diluting mathematical ground truth:

```
Candidate Expression Pipeline
├── Channel A: Strict Raw LaTeX Channel
│   └── Exact verbatim string/macro match.
├── Channel B: Perceptual Layout Matching (Local-CDM-v1.0)
│   └── Hungarian bipartite alignment with 44-rule visual token normalization.
│   └── Metric identity: "KING-WEN-LOCAL-CDM-V1.0" (Approximation; not official OmniDocBench).
└── Channel C: Semantic Structural Validation (King Wen Stage 1 & 2)
    └── Stage 1: AST isomorphism & non-flattened operator preservation.
    └── Stage 2: Computational residual verification.
    └── Strictly forbids operator collapsing (\cdot -> ., \lVert -> ||).
```

---

## 5. Phased Execution Roadmap

### Phase 1: Targeted Engine Remediation (Known Baselines)
Executed on dedicated branch `v2-remediation`:
- `EL-001`: Implement `txexs` PUA font-lineage table branch (`U+F8EE`–`U+F8FB` as brackets).
- `EL-002`: Implement Type 1 `/Differences` encoding resolver for Latin Modern `/vextenddouble`.
- `EL-003`: Expand `build_enclosure_completeness` to scan the full vertical extent in multi-line display expressions.
- `EL-004`: Convert delimiter kind compatibility from a soft score to a hard rejection gate in `associate_delimiter_pairs`.

### Phase 2: Unseen Corpus Expansion
- Register 3–5 previously unseen academic PDFs across distinct math typesetting systems (e.g., Computer Modern TeX, MathTime Professional, Lucida Bright, Cambria Math).
- Adhere to the two-level registration standard: independent human/source inspection prior to detector execution.
- Maintain versioned registry overlays via `scripts/case_registry_patch_manager.py` without mutating frozen parent files.

