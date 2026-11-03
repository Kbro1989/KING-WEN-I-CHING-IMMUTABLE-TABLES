# Audit Drift Report: Old Findings vs Pipeline Output Measurement

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Audit sources:** `docs/cross-verification-checklist-2026-09-01.md`, `docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md`, `docs/AUDIT_PIPELINE_CHECKLIST_2026-08-22.md`, `docs/vortex-hamiltonian-jacobian-gaussian-diagnostic-2026-10-27.md`, `docs/traceability-matrix-audit-2026-10-27.md`, `docs/formula-design-review-2026-10-27.md`, `docs/math-term-usage-analysis-2026-10-27.md`, `docs/hamiltonian-equation-comparison-2026-10-27.md`

---

## Category 1: Pipeline Output Drift (Reported vs. Measured)

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp) are now VALIDATED. The scale mismatch (pq_dot 0-1 vs L 0-6) is the root cause (F-10); the clamp is the sole information-loss mechanism (F-12). F-11 (M6 imaginary amplitude) is also VALIDATED — imag=0 is a type 2 dependency on M3's zero H. The "FIXED (partially)" status for §1.1 is now superseded by F-10/F-12 which establish the root cause and mechanism. The proposed fix (normalize L to /4.0) remains unimplemented. See `docs/qsmc1-m3-mathematical-validation-f10.md`, `docs/qsmc1-m3-m6-imaginary-amplitude-f11.md`, `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

### 1.1 Hamiltonian Energy = 0.0 (All States)

**Old audit report (AUDIT_QUANTUM_3D_SHAPE_E, B2/B4):**
- B2: `consensus_hexagram_id = max(hex_scores, …)` — single-hex winner reduction
- B4: `kingwen_quantum_expand.py` uses RANDOM params (`np.random.seed(0x47524541)`)
- Audit said: "Hamiltonian returns 0.0 (all clamped) — downstream effects zeroed"

**Pipeline measurement confirmed:**
- `avg_hamiltonian_energy = 0.0`, `min = 0.0`, `max = 0.0` — all 64 expanded states
- `pq_dot` ∈ [0, 0.04], `L` ∈ [0, 6] → `raw = pq_dot - L` always negative → `_clamp` → 0.0
- Downstream: rotation_modulation=0.0, scale_factor=0.75 (constant), wavefunction imag=0.0, animation_phase=phase/8 only

**Status: FIXED (partially)**
- ✅ `or 0.35` fallback bug fixed (9 locations across 5 files) — explicit zero now preserved
- ✅ `_line_state_balance` confirmed using signed differentials (not boolean)
- ✅ `_hamiltonian_energy` signature updated to accept resolved_vector, expanded_vector, line_balance
- ❌ Hamiltonian still returns 0.0 for all states — scale mismatch not resolved
- ❌ Downstream effects still zeroed (rotation, scale, wavefunction imag)
- ❌ Candidate C (signed average) not yet implemented in production

**What's still broken:** The Hamiltonian energy is 0.0 for all 512 states. The scale mismatch (pq_dot 0-1 vs L 0-6) is documented but not fixed. Candidate C is recommended but not implemented.

---

### 1.2 Ternary 729/5832 Not in Pipeline Output

**Old audit report (cross-verification-checklist, §3.4):**
- "No ternary verification gate: no script asserts expanded=729, resolved=5832, signed paired differentials"
- "GAP: `shotgun_expand()` is single capture point; adapters do not reconstruct state"
- "GAP: `hexagram_full_expansion.json` is NOT used as inject-site/porosity source (stale)"

**Pipeline measurement confirmed:**
- `shotgun_expand()` produces 64 expanded + 512 resolved (binary layer only)
- `ternary_729_permutations` computed but only count stored (729), data discarded
- `ternary_slots`, `schauberger_parsing`, `personality_subsets` are None for 448/512 resolved states
- `projections` is None for all states
- 729 ternary hexagrams and 5,832 resolved ternary states live in separate file (`ternary_full_expansion.json`), not loaded by shotgun

**Status: NOT FIXED**
- ❌ 729 ternary permutations computed but discarded (only count stored)
- ❌ 729 ternary hexagrams not in pipeline output
- ❌ 5,832 resolved ternary states not in pipeline output
- ❌ ternary_slots/schauberger/personality_subsets None for 448/512 resolved
- ❌ projections None for all states
- ❌ Binary and ternary layers remain unintegrated

**What's still broken:** The pipeline claims to produce ternary data but only stores counts. The actual ternary expansion data is in a separate file and never loaded by the main pipeline.

---

### 1.3 Porosity: 3 Independent Computations

**Old audit report (vortex-hamiltonian-jacobian-gaussian-diagnostic, §5):**
- "Three different computations can legitimately represent three different properties"
- "No reconciliation exists. The three sources measure different things"
- "Vortex porosity contract: units and valid range not explicit"

**Pipeline measurement confirmed:**
- Injection site porosity: 0-4 integer scale (all 64 hexagrams)
- Kit QWP porosity: 0.15-0.71 float (from trigram indices)
- Emotional engine porosity: from line balance
- Vortex formula uses 0-4 int as float → porosity=4 always maxes out
- `or 0.35` bug: Hex 7 and Hex 52 (porosity=0) got 0.35 instead of 0.0

**Status: PARTIALLY FIXED**
- ✅ `or 0.35` bug fixed — explicit zero now preserved (Hex 7, 52)
- ✅ Porosity distribution documented: {0: 2, 1: 18, 2: 22, 3: 12, 4: 10} (expanded)
- ❌ 3 independent porosity computations still not reconciled
- ❌ No field name distinction (structural_porosity, injection_site_porosity, line_balance_porosity)
- ❌ Vortex formula still treats 0-4 int as 0-1 float
- ❌ Porosity scale mismatch unresolved

**What's still broken:** Porosity has 3 independent computations with no reconciliation. The vortex formula still assumes 0-1 scale but receives 0-4.

---

### 1.4 Temporal Distribution Gap

**Old audit report (cross-verification-checklist, §3.7):**
- "test_deterministic_replay.py shows porosity modulation, not constant"
- "No ternary verification gate: no script asserts expanded=729, resolved=5832"

**Pipeline measurement found (NEW — not in old audit):**
- Only 192 of 512 resolved states have phase_temporal = past/present/future
- 320 states (62.5%) have an unclassified temporal label
- This was NOT documented in any prior audit

**Status: NEW FINDING — NOT ADDRESSED**
- ❌ 62.5% of resolved states have unclassified temporal labels
- ❌ No investigation into why 320 states lack temporal classification

---

### 1.5 `or 0.35` Fallback Bug

**Old audit report (vortex-hamiltonian-jacobian-gaussian-diagnostic, §2):**
- "Python's `or` operator treats 0 as falsy. When porosity=0 (2 of 64 hexagrams), `float(0) or 0.35` evaluates to `0.35` instead of `0.0`"
- "Hex 15" and "Hex 20" had porosity=0 but got 0.35

**Pipeline measurement confirmed:**
- Hex 7 and Hex 52 have porosity=0 (not Hex 15 and 20 as the audit said — the audit had wrong hex numbers)
- The `or 0.35` pattern was in 9 locations across 5 files

**Status: FIXED**
- ✅ All 9 locations fixed (truthiness check → explicit None check)
- ✅ Hex 7 and Hex 52 now correctly preserve 0.0
- ✅ All 6 modified files compile clean
- ✅ Verified no remaining `or 0.35` patterns anywhere in codebase

**What's still broken:** Nothing — this fix is complete. (Note: audit had wrong hex numbers — said Hex 15/20, actual is Hex 7/52.)

---

### 1.6 LFS Pointer Reversion

**Old audit report (vortex-hamiltonian-jacobian-gaussian-diagnostic, §6):**
- "LFS reversion needs separate verification"

**Pipeline measurement verified:**
- `git checkout -- DATASETS/semantic_math_zotero_full.json` restored intended file contents
- `git diff --stat` confirmed clean

**Status: FIXED**
- ✅ LFS pointer reverted
- ✅ No unintended changes in working tree

---

## Category 2: Audit-Reported Drifts (from AUDIT_QUANTUM_3D_SHAPE_E)

### 2.1 B1 — Auto-git-push (RESOLVED)
- `git_push_if_coherent()` removed from `kingwen_quantum_process.py`
- **Status: FIXED** ✅

### 2.2 B2 — Single-hex winner (OPEN)
- `consensus_hexagram_id = max(hex_scores, …)` still computed
- `ConsensusAccumulator.vhd` still enforces single output
- Full 512 still returned (not a hard discard)
- **Status: OPEN** — terminology + VHDL winner-accumulator needs review

### 2.3 B3 — Stale source feeding 3D backends (OPEN)
- `kingwen_mobius_sphere.py:50` and `kingwen_state_transition.py:59` still load from root `shotgun_expand_output.json` (Jul 5, stale)
- **Status: OPEN** — 3D backends still read stale data

### 2.4 B4 — Random params in quantum expand (OPEN)
- `kingwen_quantum_expand.py` seeds `np.random.seed(0x47524541)` and uses `np.random.uniform(-π, π, …)`
- `import pennylane as qml` at top — module fails to import if pennylane absent
- **Status: OPEN** — quantum expansion uses arbitrary circuit noise, not hexagram-derived params

### 2.5 B5 — Fabricated "100% Verified Parity" (RESOLVED)
- `bridge_rsmv_shap_e_manifesto.py` removed verification claim
- **Status: FIXED** ✅

### 2.6 B6 — Shap-E mutates canonical kit files (OPEN)
- `kit_1.json` `extra[]` = 205 entries (should be 14)
- Contains `shap_e_prompt` and `rsmv_model_id` injected by integration scripts
- **Status: OPEN** — canonical identity kits still mutated

### 2.7 B7 — Two divergent 3D coordinate systems (OPEN)
- `kingwen_mobius_sphere.py`: trigram→complex via `trigram_value/13.0 + 0.5`
- `kingwen_state_transition.py`: linear index `(hex_id-32)/32, (phase-3.5)/3.5`
- **Status: OPEN** — no canonical projection chosen

### 2.8 B8 — Doc/code drift (RESOLVED)
- Doc header corrected to "applied"
- **Status: FIXED** ✅

### 2.9 B9 — Vortex formula split (OPEN)
- `bridge_quantumlab_visualization.py:56` uses float `(u*l)/49.0`
- VHDL uses exact integer `(u*l*256+24)/49`
- **Status: OPEN** — not unified

### 2.10 B10 — Fake placeholder meshes (OPEN)
- `bridge_desktop_3d_engines.py` emits 3-vertex triangle stub
- `compute_collisionvis_bvh()` returns hardcoded constants (-1.2..1.2)
- **Status: OPEN** — violates no-mock policy

### 2.11 B11 — Synthetic ψ mislabeled (OPEN)
- `bridge_quantum_64_grid.py` computes synthetic `cos(kx)^2+sin(kz)^2` standing wave
- Labeled "REAL-TIME QUANTUMLAB" but framework never imported
- **Status: OPEN** — mislabeled output

### 2.12 B12 — Flat-50 band-aid (NOTE ONLY)
- `DynamicEmotionalInputDerivator.vhd` adds +1 to eliminate flat-50
- **Status: NOTE ONLY** — not blocking

---

## Category 3: External Reverence Gaps (from AUDIT_QUANTUM_3D_SHAPE_E §6)

### 3.1 Shap-E extension mismatch (OPEN)
- Manifest declares `.obj`, generator writes `.ply`
- **Status: OPEN**

### 3.2 rsmv topology key mismatch (OPEN)
- `kit_1.json` uses `point_cloud_vertices_count:729`, real rsmv uses `vertexCount` + `positionBuffer`
- **Status: OPEN**

### 3.3 Quantum-sim framework unused (OPEN)
- Bridge never imports quantumlab, computes synthetic values
- **Status: OPEN**

### 3.4 POG2 Kan limb misnamed (OPEN)
- `AdrenalineLimb.ts` should be `AggressionLimb.ts`
- **Status: OPEN**

### 3.5 alt1-ai format disjoint (OPEN)
- `k_color_map` is King-Wen-native decoration, not alt1-ai-compatible
- **Status: OPEN**

---

## Category 4: Traceability Matrix Corrections (from traceability-matrix-audit)

### 4.1 PROVEN count discrepancy (CORRECTED)
- User said "16 PROVEN" but actual is 40
- 19 of 40 are presence-only (count verified, not identity)
- **Status: CORRECTED in audit report** ✅

### 4.2 coherence uses abs(old_dy) (OPEN — design decision)
- Hexagram 1 and 2 both get coherence = 0.0 with abs
- Hexagram 2 would get +0.6 with signed old_dy
- **Status: OPEN** — needs design review, not code change

### 4.3 voiceWeight uses absolute terms (OPEN — design decision)
- Uses `yang_r` (absolute ratio) and `old_yang` (absolute count)
- Spec says "signed ternary differentials"
- **Status: OPEN** — needs design review

### 4.4 chaos uses abs(dy) (OPEN — design decision)
- Not flagged in original matrix; added as KNOWN_CONCERN
- **Status: OPEN** — needs design review

### 4.5 T10 not explicitly listed (OPEN)
- No cross-hexagram normalization test in Section 10 build order
- **Status: OPEN** — needs addition to matrix

### 4.6 Test-to-invariant mapping (OPEN)
- Section 10 doesn't map tests to invariants
- **Status: OPEN** — needs addition

### 4.7 YAO_VOCABULARY expected column (OPEN)
- Says "9-item yao vocabulary" but actual is `{0: {9 items}}` — 1 key with 9 sub-keys
- **Status: OPEN** — needs correction

---

## Category 5: Formula Design Review (from formula-design-review-2026-10-27.md)

### 5.1 Chaos (abs(dy))
- Uses `abs(dy)` — discards sign
- Design question: is chaos magnitude or signed?
- **Status: OPEN** — design decision needed

### 5.2 Coherence (abs(old_dy))
- Uses `abs(old_dy)` — discards sign
- Design question: does sign matter for coherence?
- **Status: OPEN** — design decision needed

### 5.3 VoiceWeight (absolute terms)
- Uses `yang_r` and `old_yang` (absolute)
- Design question: should use signed differentials?
- **Status: OPEN** — design decision needed

### 5.4 Whimsy (yin_r absolute)
- Uses `yin_r` (absolute ratio)
- **Status: OPEN** — design decision needed

### 5.5 DarkTone (old_yang, old_yao absolute)
- Uses `old_yang` and `old_yao` (absolute counts)
- **Status: OPEN** — design decision needed

---

**Cross-reference to current run (2026-11-02):** F-10 (semantic/scale incompatibility) and F-12 (one-sided clamp) are now VALIDATED. The scale mismatch (pq_dot 0-1 vs L 0-6) is the root cause (F-10); the clamp is the sole information-loss mechanism (F-12). Candidate C remains unimplemented and unvalidated. The abs() sign-discarding question (coherence/voiceWeight/chaos) is a SEPARATE design question from F-10/F-12. See `docs/qsmc1-m3-mathematical-validation-f10.md` and `docs/qsmc1-m3-one-sided-clamp-information-loss-f12.md`.

## Category 6: Math Term Usage Analysis (from math-term-usage-analysis-2026-10-27.md)

### 6.1 Hamiltonian
- Standard form ℋ(z,ω) = -ℒ(z) - ½ωᵀMω (paper 1505.05770)
- King Wen `pq_dot - L` is canonical Hamiltonian construction (Legendre transform), NOT Lagrangian
- Issue: variable meanings, units, scale — not the form itself
- `abs()` discards sign required by ternary paired differential spec
- **Status: ANALYZED** — Candidate C (signed average) recommended, not implemented

### 6.2 Porosity
- Not in any of 245 Zotero papers or arxiv corpus — domain-specific
- 3 independent computations measuring different things
- **Status: ANALYZED** — field contracts needed, not reconciled

### 6.3 Jacobian
- King Wen J-lens produces E[dY/dA]×dA — perturbation-response estimate, not standard Jacobian
- Closer to sensitivity analysis
- **Status: ANALYZED** — interface specification needed before integration

### 6.4 Gaussian
- Valid use case for phase bias weighting
- Needs regression tests (normalization, FWHM, boundaries, identity preservation)
- **Status: FUNCTIONAL** — validation tests needed

---

## Category 7: Hamiltonian Equation Comparison (from hamiltonian-equation-comparison-2026-10-27.md)

### 7.1 Candidate Analysis
| Candidate | Behavior | Status |
|-----------|----------|--------|
| A (current) | All 4 cases clamp to 0.0 | ❌ Fails |
| B (signed sum) | Saturates at 1.0 for all-yin and balanced | ❌ Loses differentiation |
| C (signed average) | Differentiates all 4 cases without saturation | ✅ Leading candidate |
| D (signed weighted) | Intermediate | ⚠️ Not tested |
| E (signed Lagrangian) | L = T - V | ⚠️ Not tested |
| F (T+V, abs) | Positive values | ⚠️ Sign discarded |

### 7.2 Candidate C Validation Gates (0 of 7 complete)
1. Full-state evaluation (64 × 8) — ❌ Not run
2. Signed-differential fidelity — ❌ Not run
3. Inversion behavior — ❌ Not run
4. Saturation analysis — ❌ Not run
5. Identity preservation — ❌ Not run
6. Downstream integration — ❌ Not run
7. Determinism — ❌ Not run

**Status: NOT VALIDATED** — Candidate C not yet tested across all 64×8 states

---

## Summary: Fixed vs. Still Broken

### FIXED (verified)
| Item | What was fixed | Evidence |
|------|---------------|----------|
| `or 0.35` fallback bug | 9 locations across 5 files; explicit zero preserved | grep: "NO REMAINING 'or 0.35' PATTERNS" |
| LFS pointer reversion | `DATASETS/semantic_math_zotero_full.json` restored | `git diff --stat` clean |
| Auto-git-push (B1) | `git_push_if_coherent()` removed | Audit §2.1 |
| Fabricated parity claim (B5) | "100% Verified Parity" removed | Audit §2.5 |
| Doc/code drift (B8) | Ternary correction doc header corrected | Audit §2.8 |
| Deterministic token ordering | `list(word_set)` → `sorted(word_set)` | Verified across PYTHONHASHSEED 0/12345 |
| `verify_restored_state.py` probe | `ee.HEXAGRAM_BASE_TYPED` → `m.HEXAGRAM_BASE_TYPED` | Script runs successfully |
| `emotional_engine.py` import path | `from scripts.full_hexagram_shotgun` → `from full_hexagram_shotgun` | Script runs successfully |
| PROVEN count discrepancy | User said 16, actual 40 | Corrected in audit report |
| Hex 2 coherence value | Prior claim +0.6, actual +0.25 | Recalculated from formula |
| Vortex porosity for Hex 7/52 | Was 0.35 (wrong), now 0.0 (correct) | Fixed by `or 0.35` removal |

### STILL BROKEN (not fixed)
| Item | Severity | Why not fixed | Next action |
|------|----------|--------------|-------------|
| Hamiltonian = 0.0 (all states) | HIGH | Scale mismatch not resolved; Candidate C not implemented | Implement Candidate C, test across 64×8 |
| 729 ternary permutations discarded | HIGH | Only count stored, data thrown away | Store full permutation list in output |
| 729 ternary hexagrams not in pipeline | HIGH | Separate file, not loaded by shotgun | Integrate ternary_full_expansion.json |
| 5,832 resolved ternary not in pipeline | HIGH | Same as above | Same as above |
| ternary_slots None (448/512) | MED | Only computed for phase 0 | Compute for all phases |
| schauberger_parsing None (448/512) | MED | Only computed for phase 0 | Compute for all phases |
| personality_subsets None (448/512) | MED | Only computed for phase 0 | Compute for all phases |
| projections None (all) | MED | Never computed | Implement projection computation |
| Porosity 3 independent computations | MED | No reconciliation | Define field contracts |
| Vortex treats 0-4 as 0-1 | MED | Formula assumes 0-1 scale | Normalize or change formula |
| Temporal distribution gap (320/512) | MED | Not investigated | Investigate why 320 lack temporal label |
| coherence uses abs(old_dy) | MED | Design decision needed | Design review |
| voiceWeight uses absolute terms | MED | Design decision needed | Design review |
| chaos uses abs(dy) | MED | Design decision needed | Design review |
| Single-hex winner (B2) | MED | Terminology + VHDL | Reframe as "primary anchor" |
| Stale 3D source (B3) | MED | Still reads root JSON | Point at live engine |
| Random params (B4) | MED | Still uses np.random | Derive from hexagram state |
| Shap-E mutates kits (B6) | MED | Still mutates canonical files | Move to sidecar |
| Two 3D coordinate systems (B7) | LOW | No canonical chosen | Pick one |
| Vortex formula split (B9) | LOW | Float vs integer | Unify |
| Fake placeholder meshes (B10) | LOW | Still emits 3-vertex stub | Source real geometry |
| Synthetic ψ mislabeled (B11) | LOW | Still labeled "REAL-TIME" | Relabel |
| Shap-E extension mismatch (6.1) | LOW | Manifest .obj vs .ply | Reconcile |
| rsmv topology mismatch (6.2) | LOW | Wrong key names | Align or relabel |
| Quantum-sim unused (6.3) | LOW | Framework never imported | Relabel |
| POG2 Kan limb misnamed (6.4) | LOW | AdrenalineLimb vs AggressionLimb | Correct name |
| alt1-ai format disjoint (6.5) | LOW | Disjoint concepts | Relabel |
| T10 not in build order | LOW | Missing from matrix | Add to Section 10 |
| Test-to-invariant mapping | LOW | Not in matrix | Add mapping |
| YAO_VOCABULARY expected column | LOW | Says "9-item" not "1 key, 9 sub-keys" | Fix column |

### Summary Counts

| Category | Fixed | Still Broken | Total |
|----------|-------|--------------|-------|
| Pipeline output drift | 2 | 6 | 8 |
| Audit-reported drifts (B1-B12) | 3 | 9 | 12 |
| External reverence gaps (6.1-6.5) | 0 | 5 | 5 |
| Traceability matrix corrections | 1 | 6 | 7 |
| Formula design review | 0 | 5 | 5 |
| Math term usage analysis | 4 | 0 | 4 (all analyzed) |
| Hamiltonian equation comparison | 0 | 7 (gates) | 7 |
| **Total** | **10** | **38** | **48** |

### Priority Order for Remaining Work

1. **Hamiltonian = 0.0** — most impactful defect; downstream effects all zeroed
2. **Ternary 729/5832 not in pipeline** — core data gap
3. **Temporal distribution gap** — 62.5% of states unclassified
4. **Porosity reconciliation** — 3 independent computations
5. **Stale 3D source (B3)** — 3D backends read stale data
6. **coherence/voiceWeight/chaos design review** — sign information may be discarded
7. **Candidate C validation** — 0 of 7 gates complete
8. **B4 random params, B6 kit mutation, B7 coordinate systems, B9-B11** — lower priority fixes