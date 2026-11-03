# In-Context Reward Adaptation: Comparative Analysis for King Wen

**Date:** 2026-10-29
**Source:** Sun, Xu, Wei. "In-Context Reward Adaptation for Robust Preference Modeling." arXiv:2605.30323v1, 2026.
**Purpose:** Comparative mathematical analysis. This document does NOT validate the Hamiltonian formula, authorize any code change, or close Gate 2.

---

## 1. Paper Summary

The paper studies preference modeling in RLHF (Reinforcement Learning from Human Feedback). Its central technical result: **binary preference labels alone can be insufficient to identify an underlying reward function for an unseen preference type**, but **response time** (how long a human takes to express a preference) provides additional information that restores identifiability under the paper's assumptions.

Key concepts:
- **Binary preference** z ∈ {0,1}: directional signal (which option is preferred)
- **Feature difference** φ̃: paired-state differential between options
- **Response time** t: auxiliary evidence channel (magnitude-sensitive)
- **Latent reward parameter** θ: inferred preference profile, distinct from identity
- **Identifiability**: whether distinct underlying reward functions can be distinguished from observed data

The paper's key distinction: **directional signal** (binary z) vs **magnitude-sensitive signal** (response time t). Direction alone encodes which way; magnitude encodes how strongly. Without magnitude, multiple reward functions can produce identical preference distributions.

---

## 2. Potential Connections to King Wen

### 2.1 Binary preference → yin/yang directional signal

In King Wen, each hexagram line is either yin (0) or yang (1). This is a binary directional signal: IS (yin) vs IS NOT (yang). The paper's concern applies directly — a binary label encodes direction but not strength. In King Wen, the "strength" of a line is encoded separately: young (weak) vs old (strong) vs stable (fixed). The yao vocabulary (young_yin, old_yin, stable_yin, etc.) adds a magnitude dimension that the binary alone lacks.

**Parallel**: The paper's binary z ↔ King Wen's binary line (0/1). The paper's response time t ↔ King Wen's yao strength (young/old/stable). Both add magnitude to a directional signal.

### 2.2 Feature difference → paired-state differential

The paper's φ̃ (feature difference between options) corresponds to King Wen's paired differentials: `dy = yang - yin`, `yao_dy = yao - 3.0`, `old_dy = old_yang - old_yin`, `stable_dy = stable_yao - stable_yin`. These are signed differentials between paired states — exactly the paper's feature-difference concept.

**Parallel**: The paper's φ̃ ↔ King Wen's dy, yao_dy, old_dy, stable_dy. Both are signed (not absolute) differences between paired observations.

### 2.3 Latent reward parameter → inferred emotional vector

The paper's θ (latent reward parameter) is inferred from preferences, not directly observed. In King Wen, the 5-axis emotional vector (chaos, whimsy, darkTone, coherence, voiceWeight) is derived from line balance and phase, not directly observed from hexagram identity. Both are inferred quantities that must remain distinct from canonical identity.

**Parallel**: The paper's θ ↔ King Wen's emotional vector. Both are derived, not canonical. Both must not be conflated with identity (hexagram_id).

### 2.4 Identifiability → state uniqueness

The paper asks: can distinct reward functions produce identical preference distributions? In King Wen terms: can distinct hexagrams produce identical emotional vectors? The audit found 29 duplicate expanded_vector groups — but all within the same hexagram (different phases). No cross-hexagram duplicates. This suggests hexagram identity is preserved, but phase-level duplicates mean some phases are informationally redundant for certain hexagrams.

**Parallel**: The paper's identifiability ↔ King Wen's identity preservation. The audit's 512 unique (hexagram_id, phase_bits) identities confirm no identity collapse. But the paper would ask: are 512 identities *semantically* distinguishable, or merely structurally unique?

---

## 3. Analogous Information Loss in King Wen Pipeline

The paper's framework raises three questions for the King Wen pipeline:

### 3.1 Binary → Phase expansion: Does direction alone suffice?

Binary hexagram (6 lines, each 0/1) → 64 configurations. Phase expansion adds 8 temporal variants → 512. The binary encodes direction (yin/yang) but not strength (young/old/stable). The phase expansion adds temporal context but does not add strength information — strength comes from the yao vocabulary, which is a separate layer.

**Question**: Is the binary→phase transition information-preserving? The binary has 64 states; phase expansion has 512. The 8× expansion adds temporal context, not strength. Strength is added later (ternary layer). So the binary→phase step is information-preserving for direction but does not yet encode magnitude.

### 3.2 Phase → Ternary: Does the magnitude addition restore identifiability?

Ternary expansion (729 = 3^6) adds yao (changing lines) as a third state. This is the magnitude dimension: young (weak), old (strong), stable (fixed). The paper's logic suggests that adding magnitude (response time) to direction (binary preference) restores identifiability. In King Wen, adding yao to yin/yang adds magnitude to direction.

**Question**: Does the ternary layer restore identifiability that the binary lacked? The ternary has 729 configurations vs binary's 64. The 11.4× expansion adds magnitude information. But the paper's identifiability result depends on specific statistical assumptions — not all magnitude additions restore identifiability.

### 3.3 Ternary → Five-valued: Is the emotional vector identifiable?

The five-valued differential model (15,625 = 5^6) adds emotional intensity (0-4 scale). The paper's θ (latent reward parameter) is inferred from preferences. In King Wen, the emotional vector (5 axes, 0-1 per axis) is inferred from line balance and phase.

**Question**: Given an emotional vector, can you uniquely recover the hexagram + phase + ternary state that produced it? The audit found 29 duplicate expanded_vector groups (within same hexagram, different phases). This means some phases produce identical emotional vectors — the emotional vector alone does not identify the phase. This is the paper's identifiability concern in King Wen terms.

---

## 4. Important Limitations

1. **The paper's model is not King Wen's model.** The paper uses binary preferences + response time → reward function. King Wen uses binary lines + phase + yao + emotional vectors. The mathematical structures are different. The paper provides a conceptual framework, not a proof.

2. **The paper's assumptions may not hold.** Response time identifiability requires specific decision models (e.g., drift-diffusion) and statistical assumptions. King Wen's emotional vectors are not "response times" — the analogy is structural, not literal.

3. **The five emotional axes are not the paper's learned features.** The paper learns features from data; King Wen's axes (chaos, whimsy, darkTone, coherence, voiceWeight) are derived from line balance and phase. The paper's identifiability result applies to learned features, not derived ones.

4. **This analysis does not validate the Hamiltonian formula.** The paper's framework is a research lead for comparative analysis, not a code patch or a Gate 2 decision.

5. **This analysis does not authorize any source change.** It is a comparative document for future mathematical contract development.

---

## 5. Open Questions for Future Investigation

1. **Information loss in binary→phase**: Does the 8× phase expansion add information that the binary lacked, or does it redistribute existing information? The paper's framework would test this by checking whether phase-expanded states are identifiable from binary observations alone.

2. **Magnitude restoration in ternary**: Does adding yao (young/old/stable) to yin/yang restore identifiability? The paper suggests magnitude can restore identifiability, but only under specific assumptions. What are King Wen's assumptions?

3. **Emotional vector identifiability**: Given an emotional vector, can you recover (hexagram, phase, ternary state)? The audit found 29 within-hexagram phase duplicates. Are these a problem (information loss) or a feature (phase redundancy)?

4. **Hamiltonian as identifiability test**: The Hamiltonian energy is supposed to distinguish states. Currently it's 0.0 for all states (uninformative). The paper's framework suggests that a magnitude-sensitive output (like response time) could restore identifiability. Is the Hamiltonian intended to be that magnitude-sensitive output?

5. **Response time analog**: Does King Wen have an analog to response time? The porosity field (0-4 integer) modulates exchange rate. Is porosity the "response time" of the hexagram — how quickly it exchanges with its neighbors?

---

## 6. Recommended Disposition

- **Use this paper as a source for comparative mathematical analysis.** Examine its identifiability argument and ask whether analogous information loss occurs in the binary → phase → ternary → yao pipeline.
- **Do not treat this paper as validation.** It does not establish that King Wen's pipeline is identifiable, nor that the Hamiltonian formula is correct.
- **Do not change source code.** This is a research lead, not an implementation authorization.
- **Gate 2 remains open.** This analysis does not choose between binary-first, ternary-first, or dual-track representation.

### Relevant existing artifacts
- `docs/B4_SEMANTIC_CONTRACT_AND_TEST_SPEC.md` — semantic contract (Gate 2 evidence)
- `docs/hamiltonian-equation-comparison-2026-10-27.md` — Hamiltonian candidate analysis
- `docs/ternary-semantics-reconciliation.md` — ternary semantics reconciliation
- `docs/audit-drift-report-2026-10-27.md` — audit drift report
- `DATASETS/math_kingwen_regression_2605.00155.json` — 991-equation regression report