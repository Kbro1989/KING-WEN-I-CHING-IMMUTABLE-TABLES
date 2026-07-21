# King Wen J-Space Domain Layer
## Mapping Anthropic's J-Space onto the King Wen Superposition State Machine
Date: 2026-07-11

## Source Material
- Paper: Verbalizable Representations Form a Global Workspace in Language Models
- J-lens math: `docs/j-space-jacobian-lens-math-2026-07-11.md`
- Engine: `emotional_engine.py`, `kingwen_quantum_process.py`, `superposition_capture.py`

## Exact Property-to-Layer Mapping

| J-Space Property | Paper Evidence | King Wen Superposition Analog | Implementation Target |
|---|---|---|---|
| Verbal report | "When the model is asked what it is thinking about, it names concepts represented in the workspace." | Consensus hexagram + yao vocabulary reportability | `consensus_proof.consensus_hexagram_name` + `yao_vocabulary` |
| Directed modulation | "When instructed to hold a concept in mind... the model is capable of activating and computing with workspace vectors" | Query bias / emotional_input seed modulation | `expand_hexagram(request_text, emotional_input=...)` |
| Internal reasoning | "Workspace vectors can be used to represent the value of intermediate computations... intervening on them is sufficient to redirect the conclusion." | Phase-shifted `sample_paths` + Hamiltonian energy reranking | `sample_resolve()` + `_hamiltonian_energy()` |
| Flexible generalization | "The same representation serves as a valid argument to many different downstream computations." | Inject-site pool reuse across domain slots | `HEXAGRAM_INJECTION_SITE[hexagram_id]` primary/secondary pools |
| Selectivity | "The workspace comprises a small subset of the total representational content... not involved in pervasive, routine processing." | Anchor selection from full 512 resolved set | `_anchors(resolved, limit=5)` |
| Broadcast hub | "J-lens vectors compose with the model's weights, both upstream and downstream, more broadly than other representational vectors." | Headmodel anchor + domain slot routing | `headmodel` field + slot-eligibility binding |
| Jacobian linearized effect | `J(a; v) ≈ E_{contexts}[ ∂y_v / ∂a ] · Δa` | Hamiltonian energy slope × Gaussian-smoothed state delta | `_hamiltonian_energy()` + `_gaussian_kernel()` |
| Layer correction | J-lens corrects for representational changes across layers | Phase-temporal shift as layer-proxy | `phase_temporal` + `PHASE_INFO` modulation |
| Sparse subframe | J-space is a sparse subframe of activation space | 64-hex shotgun subset of full 512 resolved space | `expand_hexagram()` 64-expanded / `collapse_full_128()` 512-resolved |
| Causal swap | Swapping J-lens vector changes output | Pass-query bias replacing previous selection | `run_quantum_process()` pass-indexed query mutation |

## Binding Method: Injection-Site → J-Space Domain Layer

### Step 1: Injection-site binding
- Each hexagram carries immutable `primary_pool`, `secondary_pool`, and derived `bodypart` domain-slot eligibility.
- This is the `a` in `J(a; v)` — the activation being measured.

### Step 2: Linearized effect measurement
- Compute Hamiltonian energy slope for each resolved state:
  - `ℋ(p,q,t) = Σ p_i q̇^i - ℒ`
- This is the discrete analog of `∂y_v / ∂a` — how much this state pushes toward a domain outcome.

### Step 3: Corpus averaging
- Baseline is the full 512 resolved-state distribution from `collapse_full_128()`.
- Average the Hamiltonian energy slope across all 512 states to get the baseline `E[∂y_v/∂a]`.

### Step 4: Gaussian smoothing
- Apply Gaussian kernel to smooth state transitions:
  - `f(x) = a * exp(-(x - b)^2 / (2c^2))`
- `b` = phase temporal center
- `c` = FWHM-derived width from phase spread

### Step 5: Broadcast selection
- Select top-K states by smoothed Hamiltonian energy.
- Enforce:
  - minimum domain-slot coverage
  - minimum temporal phase coverage
  - minimum vector spread
- These selected states form the J-space broadcast layer for this pass.

### Step 6: Causal swap / pass mutation
- Next pass replaces the current broadcast subset with a new selection.
- If coherence improves across baseline, the swap is validated.
- This mirrors the paper's causal swap experiment.

## Domain Layer Contract

Input:
- `snapshot`: one `capture_superposition()` result
- `baseline`: first-pass snapshot for delta measurement
- `emotional_input`: slider value

Output:
- `jspace_broadcast`: top-K selected resolved states
- `jspace_energy_delta`: change in average Hamiltonian energy from baseline
- `jspace_coherence_delta`: change in mean coherence from baseline
- `jspace_coverage`: domain-slot / phase / vector coverage of broadcast set
- `jspace_verbalizable`: consensus reportability score
- `jspace_modulatable`: query-bias responsiveness score
- `jspace_flexible`: cross-pool reuse score
- `jspace_selective`: broadcast-set sparsity score

## Validation Title Format

Each pass produces a title of the form:

```
pass=<N> verdict=<verdict> consensus=<hexagram> expansion=<delta> coherence_delta=<delta> jspace_energy=<value> jspace_coverage=<dict>
```

## Proven Variations Included

- Iterative self-guided quantum process tomography
- Active-learning adaptive reconstruction
- Direct superposition verification without recombination
- Coherence trajectory measurement
- Quantum Darwinism redundancy/amplification model
