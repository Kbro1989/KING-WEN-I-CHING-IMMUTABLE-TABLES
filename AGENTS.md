# King Wen Math: Pipeline Invariants and Engineering Rules

## 1. Evidence Artifact Synchronization
- Whenever changes are made to parsers, solvers, AST extractors, or validation logic (`scripts/math_reconstruction_evidence.py`, `scripts/math_recovery_tool.py`, `scripts/structural_ast_extractor.py`, `scripts/mathml_parser.py`), the downstream evidence artifacts (`DATASETS/math_reconstruction_evidence.jsonl`, `DATASETS/math_reconstruction_evidence.json`, and `DATASETS/reconstruction_work_log.md`) MUST be re-executed and regenerated from the exact same run.
- Metric figures reported to the user or in commit messages MUST match the regenerated JSON summary, never unverified partial runs or intermediate staging checkpoints.

## 2. Structural & Semantic Verification Invariants
- **Persistence $\ne$ Fidelity:** Persisting an AST dictionary (`canonical_tree`) proves serializability, not structural isomorphism with the source. Structural fidelity requires verifying operator kinds, relation types, bounds, and operand roles.
- **Operator Preservation:** Structural checks must never strip non-alphanumeric operators or rely purely on regex word tokens (`\w+`). Flattening $\langle a, b \rangle \to a \cdot b$ or $a \sim b \to a = b$ is a structural violation and must explicitly fail Stage 1.
- **Two-Stage Separation:**
  - Stage 1 (Source Fidelity): Verifies that critical structural constructs (named operators, inner products, norms, non-equality relations) are preserved.
  - Stage 2 (Computational Validity): Verifies mathematical residual ($|\text{target} - \text{other}| = 0$).
  - If Stage 1 is skipped (e.g., no AST available), the record MUST be flagged as `stage1_skipped: True`, never claimed as "both stages passed".

## 3. Cross-Platform UTF-8 Invariant
- All file reads, writes, and test scripts handling mathematical formulas or recovery datasets MUST explicitly specify `encoding="utf-8"`.
- Direct console-printing test scripts executing on Windows (`sys.platform == 'win32'`) must reconfigure stdout/stderr with `encoding="utf-8", errors="replace"` to prevent unhandled `charmap` codec exceptions with mathematical glyphs.

## 4. Surgical Code Edits
- Follow the global rule: no mass replace files. Surgical edits only.
