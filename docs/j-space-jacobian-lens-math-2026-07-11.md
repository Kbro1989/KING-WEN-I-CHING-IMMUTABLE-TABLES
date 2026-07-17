# J-lens Exact Math Formulation
## Source
- Paper: Verbalizable Representations Form a Global Workspace in Language Models
- Authors: Wes Gurnee, Nicholas Sofroniew, Adam Pearce, et al.
- Published: July 6, 2026
- URL: http://transformer-circuits.pub/2026/workspace/index.html
- Code: https://github.com/anthropics/jacobian-lens

## Core Definition

For each token in the model's vocabulary, the Jacobian lens identifies a vector
representation that encodes the **potential** for the model to verbalize that token
in the future.

Concretely, it computes, for each layer, the **average linearized effect** of an
activation on the model's likelihood of producing a particular token, averaging over
a large corpus of contexts.

## Interpreted Mathematical Form

Let:
- `a` be the model activation at a given layer and position
- `y` be the future token likelihood/output logits
- `v` be the vocabulary token of interest

Then the J-lens vector for token `v` is:

```
J(a; v) ≈ E_{contexts}[ ∂y_v / ∂a ] · Δa
```

Where:
- `∂y_v / ∂a` is the Jacobian of token `v` likelihood with respect to activation `a`
- `E_{contexts}[ ... ]` is the average linearized effect over many contexts
- `Δa` is the activation perturbation/change being measured

In words: **how much this activation linearly pushes the model toward saying token `v`.**

## Key Constraints from the Paper

1. **Averaging is essential**
   - "The averaging step is key, as it distinguishes representations that are
     verbalizable—poised to be spoken about, should the occasion arise—from those
     that merely happen to be verbalized in one particular context."

2. **Layer correction**
   - J-lens corrects for representational changes across layers, unlike logit lens.
   - This is why earlier layers yield meaningful readouts.

3. **Sparse subframe**
   - If activations decompose into sparse linear features, J-space is a sparse
     subframe of that representation space.

4. **Single-token limitation**
   - Current J-lens identifies only single-token concepts.
   - Multi-token concepts are not fully captured.

5. **Causal swap intervention**
   - Swapping one active J-lens vector for another changes model output accordingly.
   - This confirms the vector is not just correlated, but causally mediating.

## Operational Mapping for King Wen

| J-lens term | King Wen analog |
|---|---|
| activation `a` | hexagram resolved state / inject-site record |
| token likelihood `y_v` | domain relevance score |
| Jacobian `∂y_v / ∂a` | Hamiltonian energy slope |
| corpus averaging `E[ ... ]` | 512 resolved-state baseline distribution |
| linearized effect | Gaussian kernel–smoothed state transition |
| J-lens vector `J(a; v)` | inject-site vector + headmodel anchor |
| swap intervention | superposition pass replacement |
| layer correction | phase-temporal shift |
| sparse subframe | 64-hex subset vs full 512 resolved set |

## Proven Study Methods Adopted

- Baseline-stabilized iterative passes
- Self-guided adaptive selection from coverage gaps
- Coherence trajectory tracking
- XOR-gate direct verification without forced collapse
- Convergence by non-improvement patience
