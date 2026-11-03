# Cross-Field Dependency and Information-Preservation Matrix

## Scope

Read-only investigation. No source changes, no commits, no remediation acceptance.
Synthesizes L1 (emotional vectors), L2 (porosity), and L3 (Hamiltonian) lineage audits into a single cross-field dependency matrix. Answers: which findings share upstream causes, which are independent, which affect the same downstream consumers, which losses are reversible from existing stored data, which require original inputs, and which are intentional representation boundaries.

## 1. Status Legend

| Status | Meaning |
|---|---|
| OPEN | Finding identified, not yet addressed or accepted |
| VALIDATED | Finding confirmed with evidence; root cause documented |
| PRESERVED | Field retains full information through all layers |
| PARTIALLY PRESERVED | Field retains information with documented loss points |
| NOT PRESERVED | Field loses information at one or more layers |
| INTENTIONAL | Representation boundary is by design, not defect |

## 2. Field-Level Integrity Summary

| Field | Integrity | Principal issue | Reversible from stored data? |
|---|---|---|---|
| Emotional vectors (5-axis) | PARTIALLY PRESERVED | 4-source blending provenance lost; phase shifts hardcoded; `or 0.0` masks zeros | Partially — raw H recoverable, but source contributions not |
| Porosity | NOT PRESERVED | 3 unreconciled computations; canonical base not preserved; `or` fallbacks conflate types | Partially — base_porosity recoverable from HEXAGRAM_INJECTION_SITE, but phase-modulated result not invertible |
| Hamiltonian | NOT PRESERVED | 727 raw values → 1 observed (0.0); empty line_balance; scale mismatch | Yes — raw H computable from stored pq_dot and lagrangian components (F-12) |

## 3. Cross-Field Dependency Matrix

### 3.1 Shared upstream causes

| Finding | F-01 | F-02 | F-05 | F-06 | F-07 | F-08 | F-10 | F-11 | F-12 |
|---|---|---|---|---|---|---|---|---|---|
| **F-01** (`or 0.0875`) | — | Same class (`or` fallback) | — | — | — | — | — | — | — |
| **F-02** (`float(None)`) | Same class | — | — | — | — | — | — | — | — |
| **F-05** (broken consumers) | — | — | — | Import path | Missing `__init__.py` | — | — | — | — |
| **F-06** (import path) | — | — | Broken consumers | — | Missing `__init__.py` | — | — | — | — |
| **F-07** (missing `__init__.py`) | — | — | Broken consumers | Import path | — | — | — | — | — |
| **F-08** (empty line_balance) | — | — | — | — | — | — | Enables F-10/F-12 | Enables F-11 | Enables F-12 |
| **F-10** (scale mismatch) | — | — | — | — | — | — | — | Causes F-11 | Causes F-12 |
| **F-11** (M6 imaginary) | — | — | — | — | — | — | Caused by F-10 | — | Caused by F-12 |
| **F-12** (clamp) | — | — | — | — | — | — | Caused by F-10 | Causes F-11 | — |

### 3.2 Independence classification

| Finding | Independent? | Shared cause with | Unique cause |
|---|---|---|---|
| F-01 | No | F-02 (same `or` fallback class) | `or 0.0875` specific to porosity_norm |
| F-02 | No | F-01 (same `or` fallback class) | `float(None)` TypeError in 3 locations |
| F-05 | No | F-06, F-07 (import resolution chain) | References nonexistent JSON file |
| F-05b | No | F-05 (same class of broken consumer) | Different file, same pattern |
| F-06 | No | F-05, F-07 | `from scripts.full_hexagram_shotgun` fails without `__init__.py` |
| F-07 | No | F-05, F-06 | PEP 420 implicit namespace package |
| F-08 | Yes | F-10 (enables scale mismatch by emptying line_balance) | Consumer integration defect — line_balance computed but not passed |
| F-10 | Yes | F-12 (enables clamp) | Scale/semantic incompatibility between pq_dot and lagrangian |
| F-11 | No | F-10, F-12 (dependency chain) | Type 2 dependency: M6 derived from M3 Hamiltonian |
| F-12 | No | F-10 (enables clamp) | One-sided `_clamp()` destroys 727 distinct values |

### 3.3 Downstream consumer impact

| Consumer | Emotional vectors | Porosity | Hamiltonian | Shared downstream impact |
|---|---|---|---|---|
| `emotional_engine.py` | Produces + consumes | Produces + consumes | Produces + consumes | All three fields co-located; empty line_balance (F-08) affects Hamiltonian only |
| `decision_matrix.py` | Consumes (resolved) | Consumes (porosity_norm) | Consumes (consensus_hamiltonian) | F-02 affects both porosity and Hamiltonian paths |
| `multi_layer_expand.py` | Consumes (resolved) | Consumes (porosity, porosity_norm) | Consumes (consensus) | F-01 affects porosity_norm specifically |
| `expand_server.py` | Serializes both | Serializes porosity | Serializes hamiltonian | HTTP response carries all three fields |
| `kingwen_training.py` | Consumes (expanded) | Consumes (porosity_norm) | — | Training data serialization |
| `kingwen_voice_router.py` | Consumes (resolved) | — | — | Voice routing from emotional vectors only |
| `scripts/generate_godot_729*.py` (×4) | Consumes (resolved) | — | Consumes (resolved includes H) | 3D generation from resolved state |
| `scripts/generate_sovereign_world.py` | Consumes (resolved) | — | Consumes (resolved includes H) | Sovereign world from resolved state |
| `scripts/enrich_kit_models.py` | Consumes (expanded) | Consumes (kit QWP porosity) | — | Kit enrichment from expanded + QWP |
| 5 broken consumers (F-05/F-05b) | Cannot verify | Cannot verify | Cannot verify | All three fields inaccessible |

### 3.4 Reversibility analysis

| Finding | Reversible from stored data? | Required input for reconstruction | Reversibility type |
|---|---|---|---|
| F-01 (`or 0.0875`) | Yes | None — fix is code change only | Code fix (no data needed) |
| F-02 (`float(None)`) | Yes | None — fix is code change only | Code fix (no data needed) |
| F-05/F-05b (broken consumers) | Yes | None — fix is code change (point to live producer) | Code fix (no data needed) |
| F-06 (import path) | Yes | None — fix is `__init__.py` or path change | Code fix (no data needed) |
| F-07 (missing `__init__.py`) | Yes | None — create file | Code fix (no data needed) |
| F-08 (empty line_balance) | Yes | Actual line_balance from `_pool_weights_for_hex()` | Code fix (data already computed, just not passed) |
| F-10 (scale mismatch) | Partially | Original inputs (line counts, vector values) | Requires semantic redefinition of coefficients |
| F-11 (M6 imaginary) | Yes (after F-10/F-12 resolved) | Nonzero Hamiltonian | Derived — depends on F-10/F-12 resolution |
| F-12 (clamp) | Yes | Raw H values (computable from stored pq_dot and lagrangian) | Data recovery possible without code change |

### 3.5 Intentional representation boundaries

| Boundary | Type | Preserved? | Notes |
|---|---|---|---|
| Expanded vs resolved vector | INTENTIONAL | Yes | Phase shift creates temporal displacement; both stored |
| Binary (512) vs ternary (5,832) | INTENTIONAL | Yes | Different state spaces; ternary is expansion artifact |
| Injection site porosity (0-4 int) vs phase-modulated (0.0-1.0) | INTENTIONAL | Partially | Base not preserved separately (medium loss) |
| Injection site porosity vs kit QWP porosity | INTENTIONAL | No | Different scales, sources, semantics; no conversion |
| Emotional vector (5-axis) vs Hamiltonian (scalar) | INTENTIONAL | No | Information reduction by design (different mathematical spaces) |
| pq_dot (continuous) vs lagrangian (discrete) | INTENTIONAL | No | Different physical quantities; scale mismatch is the defect (F-10) |
| Raw H vs clamped H | NOT INTENTIONAL | No | One-sided clamp is information-loss mechanism (F-12) |
| domain_vector == resolved_vector | NOT INTENTIONAL | Yes (no loss) | Redundant field; potential semantic collision |
| sample_paths (primary == neighbor_blend) | NOT INTENTIONAL | Yes (no loss) | Redundant data; both use expanded_vec |

## 4. Upstream Cause Analysis

### 4.1 Single upstream root causes

| Root cause | Findings caused | Impact |
|---|---|---|
| `or` fallback pattern | F-01, F-02 | 0.0 masked, float(None) crashes |
| Missing `__init__.py` | F-05, F-06, F-07 | 5 consumers broken, import path fails |
| Empty line_balance argument | F-08, F-10, F-12 | Hamiltonian uses zero inputs, amplifying scale mismatch |
| Scale mismatch (pq_dot vs lagrangian) | F-10, F-12, F-11 | H always negative → clamp → 0.0 → M6 inherits zero |
| One-sided clamp | F-12, F-11 | 727 distinct → 1 observed; imaginary amplitude zero |

### 4.2 Independent findings (no shared upstream cause)

| Finding | Unique cause |
|---|---|
| F-05b (build_unified_bin.py:23) | Same pattern as F-05 but different file; discovered during producer-to-consumer audit |
| Phase 6-7 porosity (no porosity=0) | Phase overdrive pushes base porosity up; not a defect, but an observed behavior |

## 5. Consumer Impact Analysis

### 5.1 Consumers affected by multiple findings

| Consumer | Findings affecting it | Severity |
|---|---|---|
| `emotional_engine.py` | F-08 (empty line_balance), F-10, F-11, F-12 | High — produces H=0, M6 imaginary=0 |
| `decision_matrix.py` | F-02 (float(None)) | Medium — crashes on None |
| `multi_layer_expand.py` | F-01 (or 0.0875) | High — masks 0.0 |
| `expand_server.py` | F-05 (broken consumers), F-06 (import) | Medium — HTTP serialization affected |
| 5 broken consumers | F-05, F-06, F-07 | High — cannot run at all |

### 5.2 Consumers unaffected by any finding

| Consumer | Reason |
|---|---|
| `kingwen_voice_router.py` | Uses resolved_vector only; no Hamiltonian or porosity computation |
| `kingwen_training.py` | Uses porosity_norm as string; no numeric computation |
| `scripts/test_*.py` (12 scripts) | Testing only; no production impact |

## 6. Reversibility Summary

| Reversibility class | Findings | Count | Description |
|---|---|---|---|
| Code fix only (no data needed) | F-01, F-02, F-05, F-05b, F-06, F-07 | 6 | Fix is code change; no data reconstruction needed |
| Code fix + data already computed | F-08 | 1 | Line balance exists but not passed; fix is one-line change |
| Derived fix (depends on other fixes) | F-11 | 1 | Requires F-10 and F-12 resolution first |
| Semantic redefinition needed | F-10 | 1 | Requires design decision on coefficient scaling |
| Data recovery possible | F-12 | 1 | Raw H computable from stored pq_dot and lagrangian |

**Total**: 10 findings tracked (7 OPEN, 3 VALIDATED).

## 7. Recommended Next Steps

1. **No remediation authorized.** Gate 2 remains OPEN.
2. **Cross-field dependency matrix complete.** All three lineage audits (L1, L2, L3) synthesized.
3. **Next investigation options** (user's choice):
   - Data-flow reconciliation (producer → export → importer → schema → representation)
   - Orphaned exports audit
   - Remediation planning for F-01/F-02 (code-fix-only findings, lowest risk)
   - F-10 semantic redefinition design investigation (requires user authorization)