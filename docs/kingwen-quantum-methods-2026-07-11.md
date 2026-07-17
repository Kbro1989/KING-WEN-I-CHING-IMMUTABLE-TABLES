# King Wen Quantum Methods
## Proven Variations for Experimental Pass Tracking
Date: 2026-07-11

## Sources
- PhysRevA.111.L050402 — Direct and efficient detection of quantum superposition via XOR game without spatial recombination.
- PhysRevA.101.022317 — Self-guided quantum process tomography: iterative experimental reconstruction of an unknown process.
- arXiv:2412.20925 — Active learning with variational quantum circuits for adaptive state/process reconstruction.
- Nat Commun 2023 / arXiv-like ML-QPT — Quantum process tomography with unsupervised learning and tensor-network representation.
- Quantum Darwinism experiments — Environment-assisted amplification/redundancy as objective-reality emergence from quantum possibilities.

## Methods Adopted

### 1. Baseline-Stabilized Iterative Passes
- Record baseline snapshot before first experimental pass.
- Compare every subsequent pass to baseline, not only previous pass.
- Proven in: self-guided QPT iterative refinement.

### 2. Self-Guided Adaptive Selection
- From current candidate set, select next experimental targets by:
  - highest Hamiltonian path energy, AND
  - highest coverage deficit / information gain.
- Proven in: self-guided QPT + active learning VQC reconstruction.

### 3. Coherence as Primary Validation Metric
- Use mean coherence across resolved states as the success signal.
- Track coherence trajectory: baseline, best, improving passes count.
- Proven in: PhysRevResearch.1.033020, quantum coherence measurement experiments.

### 4. XOR-Gate Direct Superposition Verification
- Validate diversity/coverage without forcing collapse.
- In our process: require minimum domain-slot coverage + temporal branch coverage + vector spread before declaring success.
- Proven in: PhysRevA.111.L050402 direct-detection protocol.

### 5. Convergence Criteria
- Stop experimental passes when:
  - coherence does not improve for N consecutive passes, OR
  - coverage thresholds are met, OR
  - max passes reached.
- Prevent indefinite looping while preserving exploration.

### 6. Validation Title Per Attempt
- Each attempt/record gets a title summarizing:
  - pass index
  - verdict
  - consensus anchor
  - expansion delta
  - coherence delta
- Enables provenance review without reading full payload.

## Domain Mapping

| Quantum Method | King Wen Usage Domain | Implementation |
|---|---|---|
| Baseline-stabilized iterative passes | `collapse_full_128()` / `superposition_capture.py` | `baseline_coherence`, `best_coherence`, `improving_passes` |
| Self-guided adaptive selection | `kingwen_quantum_process.py` | next-pass query bias from top energy + coverage deficit |
| Coherence trajectory | `kingwen_quantum_process.py` | coherence delta, trajectory array |
| XOR-gate direct verification | `superposition_capture.py` / `kingwen_quantum_process.py` | coverage + spread gates before push |
| Convergence criteria | `kingwen_quantum_process.py` | stop when no improvement for N passes |
| Validation title per attempt | `kingwen_quantum_process.py` | `validation_title` field in JSONL |

## Proven Variations Included
- Iterative self-guided quantum process tomography
- Active-learning adaptive quantum circuit reconstruction
- Direct superposition verification without recombination
- Quantum coherence measurement across repeated trials
- Quantum Darwinism redundancy/amplification model for objective reality emergence
