# Research Lead: Enhanced EWC with Cross-Modal Knowledge Retention

**Paper:** Lifelong Learning in Vision-Language Models: Enhanced EWC with Cross-Modal Knowledge Retention — Hamza Ahmed Durrani and Rafay Suleman Durrani, submitted May 12, 2026.
**ArXiv:** https://arxiv.org/abs/2605.30323 (verify exact ID from source)

## 1. What the paper proposes

Three mechanisms for continual learning in vision-language models:

**A. Enhanced Elastic Weight Consolidation (EWC):** Estimate parameter importance separately for visual encoder, text encoder, and cross-modal projection. Penalize changes to parameters important to previously learned tasks, using separate regularization weights.

**B. Cross-modal consistency preservation:** Compare current image-text relationships with relationships established by earlier encoders. Prevent new learning from damaging alignment even when individual modalities still perform well.

**C. Parameter-efficient adaptation:** LoRA-inspired low-rank updates; keep much of the underlying model fixed.

Central distinction: preserving parameters (EWC) vs preserving relationships (consistency mechanism).

## 2. Connection to King Wen

The useful transfer is as a **test-design principle**, not as a new mathematical model.

| Paper concept | King Wen analogue | What it could motivate |
|---|---|---|
| Preserve important parameters | Preserve canonical identity and source records | Test whether consumer repairs leave canonical producer outputs unchanged |
| Preserve cross-modal relationships | Preserve relationships between identity, phase, vectors, voice, avatar artifacts | Test linked records and lineage, not just individual files |
| Sequential task learning | Successive pipeline and consumer changes | Compare behavior before and after each isolated repair |
| Parameter-importance estimates | No direct equivalent established | Do not equate Fisher importance with King Wen's Hamiltonian or other weights |
| Cross-modal consistency loss | Potential analogy to consumer-boundary invariants | Define expected relationships first; measure deviations rather than assuming all representations should be numerically equal |

The paper reinforces a useful question: can each representation change in its permitted way while the relationships that must remain invariant are preserved?

For example, a phase-specific avatar may legitimately differ geometrically from another phase. The invariant is not that their meshes match; it is that each mesh retains the correct identity, phase, and provenance. Similarly, a consumer may transform a producer's output without being allowed to silently change what its identity fields mean.

This suggests adding relationship-preservation tests to the existing consumer contract suite—but only as a research proposal. It does not require changing the current repair specification or closing Gate 2.

## 3. Important limitations in the paper itself

**Issue 1 — Consistency equation needs clarification.** Equation (3) compares current encoder's cosine similarity for pair (x_i, y_i) with previous encoder's similarity for (x_j, y_j). Indices differ. Unless there is an omitted pairing rule, this does not clearly compare the same image-text pair or the same pairwise relationship. The claimed preservation of cross-modal structure depends on what is actually being compared.

**Issue 2 — Reported performance figures inconsistent.** Abstract claims 78% reduction in forgetting; results report 0.31 → 0.08 (74.2% reduction); conclusion reports 74%. Also reports 15% computational overhead, 20% longer training time, 300% reduction in computational overhead from parameter-efficient adaptation. Measures need clearer definitions and consistent accounting basis.

**Issue 3 — Reproducibility details insufficient.** Paper describes four dataset stages but parts of results discuss two tasks and two-task convergence. Does not establish complete, independently reproducible experimental protocol with sufficient detail about model configuration, Fisher estimation, adaptive-weight selection, seeds, uncertainty across runs.

Acknowledged limitations: evaluation focuses on image-text matching rather than complex reasoning; assumes clearly defined task boundaries.

This does not prove reported results are false. It means claims are not sufficiently established by reported tables and descriptions alone.

## 4. Proposed research note for King Wen

Classify as **cross-representation consistency research lead**. Five questions:

1. **Identity invariant:** Does every derived artifact preserve the correct canonical identity, even when its vector or geometry changes?
2. **Relationship invariant:** Which relationships must remain stable across producer, voice, avatar, and OpenJarvis consumers?
3. **Permitted variation:** Which differences are expected across phases or input conditions, and which indicate corruption?
4. **Change isolation:** Can each consumer repair be shown to preserve unaffected outputs and relationships?
5. **Measurement validity:** Are consistency scores measuring the intended relationship, or merely numerical similarity between representations?

Suitable first experiment (read-only): capture canonical producer outputs and their identity/phase relationships, then compare against each consumer's outputs. Record exact matches, permitted transformations, mismatches, and unresolved cases separately. Do not use cosine similarity or any aggregate score as substitute for exact identity and provenance checks.

## 5. Boundary statement

- This is a research lead for test design, not a method to adopt.
- EWC formula addresses neural-network parameter updates and does not establish a valid replacement for King Wen's Hamiltonian, five-valued differential model, or identity resolver.
- Cross-modal consistency concept is relevant to consumer-boundary invariants but must be defined in King Wen terms (identity, phase, provenance) first.
- Does not solve Hamiltonian scale mismatch, justify energy formula change, or authorize normalization between hexagrams.
- Does not change current repair specification or close Gate 2.
- Key question: is cross-modal consistency an independently evaluated observable structure, or a learned signal?

## 6. Relationship to existing research leads

This is the **fourth** research lead in the 2026-10-29 series, alongside:
- `research-lead-incontext-reward-adaptation-2026-10-29.md` (arXiv:2605.30323v1) — identifiability via auxiliary evidence
- `research-lead-polymorphism-rotation-2026-10-29.md` (McCann) — structural similarity ≠ functional equivalence
- `research-lead-tur-dpo-2026-10-29.md` (arXiv:2605.00224) — topology- and uncertainty-aware evaluation

All four are comparative analysis only. None validate the Hamiltonian formula, authorize code changes, or close Gate 2.

## 7. Recommended test additions (proposal only, not implementation)

Add to `representation-equivalence-audit-checklist-2026-10-29.md` as Category 6 (cross-representation consistency):

- Item 23: Identity invariant — every derived artifact preserves correct canonical identity
- Item 24: Relationship invariant — relationships stable across producer, voice, avatar, consumers
- Item 25: Permitted variation — expected differences across phases/input conditions vs corruption
- Item 26: Change isolation — each consumer repair preserves unaffected outputs and relationships
- Item 27: Measurement validity — consistency scores measure intended relationship, not numerical similarity

## Verdict

Research value: moderate to high for test design; unproven as a method to adopt.

The paper's most useful idea for King Wen's current stage: local correctness does not guarantee relational correctness. This directly motivates stronger consumer-boundary tests. Its EWC formula, however, addresses neural-network parameter updates and does not establish a valid replacement for King Wen's Hamiltonian, five-valued differential model, or identity resolver.

Record the paper as a research lead and leave the existing implementation and Gate 2 decisions untouched.
"""