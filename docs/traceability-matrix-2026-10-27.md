# Documentation-to-Implementation Traceability Matrix

**Date:** 2026-10-27
**Repository:** KING-WEN-I-CHING-IMMUTABLE-TABLES
**Commit under audit:** `71fbf28f8e`
**Governing invariant:** No cross-hexagram normalization. Each of the 64 identities retains its own structure, mappings, meaning, and traceable outputs throughout the pipeline.

---

## Authority Tiers

| Tier | Definition | Examples |
|------|-----------|----------|
| **Canonical authority** | Immutable source of truth; downstream conforms to it | `kingwen_ternary_tables_complete.py` |
| **Mathematical specification** | Formulas, encodings, state spaces, computational rules | `immutable-table-math-decoded.md`, `KING_WEN_CONSENSUS_MATH.md`, ternary differential correction |
| **Executable pipeline** | Scripts, source, tests, datasets that implement specifications | `scripts/`, `src/`, `tests/`, `DATASETS/` |
| **Migration contract** | Describes intended mapping to another runtime | `lua-math-tool.md` |
| **Evidence and verification** | Requirements, execution status, known limitations, reproducible evidence | `AGENTS.md`, checklists, pipeline reports |

---

## Verification Status Key

| Status | Meaning |
|--------|---------|
| `PROVEN` | Reproducible check passed for the stated claim and scope. Includes exact command, environment/revision, observed result, and evidence location. |
| `SPECIFIED` | Requirement is documented; implementation has not been verified. |
| `UNVERIFIED` | Evidence is insufficient, incomplete, or not yet collected. |
| `KNOWN_CONCERN` | Documented defect, limitation, or unresolved discrepancy. |

---

## Section 1: Canonical Authority Tier

| # | Symbol | Type | Expected | Observed | Implementing File | Verification Command | Status | Evidence |
|---|--------|------|----------|----------|-------------------|---------------------|--------|----------|
| 1.1 | `HEXAGRAM_BASE` | `Dict[int, Dict]` | 64 entries, keys: name, unicode, binary_bottom_to_top, binary_top_to_bottom, upper_trigram, lower_trigram, upper_idx, lower_idx, category, action | 64 entries; 10 keys per entry; hex 1 = "The Creative", unicode ䷀, binary 111111, category sovereign, action ASSERT | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.HEXAGRAM_BASE))"` | `PROVEN` | Observed 64; all IDs 1-64 present |
| 1.2 | `TOTAL_HEXAGRAMS` | `int` | 64 | 64 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(m.TOTAL_HEXAGRAMS)"` | `PROVEN` | 64 |
| 1.3 | `TOTAL_PHASES` | `int` | 8 | 8 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(m.TOTAL_PHASES)"` | `PROVEN` | 8 |
| 1.4 | `TOTAL_ENCODINGS` | `int` | 512 | 512 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(m.TOTAL_ENCODINGS)"` | `PROVEN` | 512 |
| 1.5 | `MAX_9BIT_VALUE` | `int` | 511 | 511 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(m.MAX_9BIT_VALUE)"` | `PROVEN` | 511 |
| 1.6 | `BIT6_TO_HEXAGRAM` | `Dict` | 64 entries | 64 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.BIT6_TO_HEXAGRAM))"` | `PROVEN` | 64 |
| 1.7 | `HEX_PHASE_TO_9BIT` | `Dict` | 512 entries | 512 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.HEX_PHASE_TO_9BIT))"` | `PROVEN` | 512 |
| 1.8 | `ENCODING_TABLE` | `Dict` | 512 entries | 512 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.ENCODING_TABLE))"` | `PROVEN` | 512 |
| 1.9 | `PHASE_LINE_MAP` | `Dict` | 8 entries (phase 0-7 → changing line positions) | 8 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.PHASE_LINE_MAP))"` | `PROVEN` | 8 |
| 1.10 | `PHASE_INFO` | `Dict` | 8 entries | 8 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.PHASE_INFO))"` | `PROVEN` | 8 |
| 1.11 | `TRIGRAM_INFO` | `Dict` | 8 entries | 8 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.TRIGRAM_INFO))"` | `PROVEN` | 8 |
| 1.12 | `VOICEBOX_VOICE_POOL` | `Dict` | 66 entries (voice pools) | 66 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.VOICEBOX_VOICE_POOL))"` | `PROVEN` | 66 |
| 1.13 | `POROSITY_LEVELS` | `Dict` | 5 levels (0-4) | 5 levels: sealed, porous_min, balanced, porous_open, porous_max | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.POROSITY_LEVELS))"` | `PROVEN` | 5 |
| 1.14 | `HEXAGRAM_INJECTION_SITE` | `Dict` | 64 entries, keys: primary_pool, secondary_pool, porosity, reason | 64 entries; 4 keys per entry | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.HEXAGRAM_INJECTION_SITE))"` | `PROVEN` | 64 |
| 1.15 | `YAO_VOCABULARY` | `Dict` | 9-item yao vocabulary | 1 key (0) with 9 sub-keys: young_yin, old_yin, stable_yin, new_yao, old_yao, stable_yao, old_yang, new_yang, stable_yang | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.YAO_VOCABULARY[0]))"` | `PROVEN` | 9 (nested under key 0) |
| 1.16 | `EMOTIONAL_WEIGHTS` | `Dict` | 64 entries | 64 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.EMOTIONAL_WEIGHTS))"` | `PROVEN` | 64 |
| 1.17 | `SLIDER_CHECKLIST` | `List` | 8 items | 8 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.SLIDER_CHECKLIST))"` | `PROVEN` | 8 |
| 1.18 | `EMOTIONAL_POOL` | `Dict` | 66 entries (alias of VOICEBOX_VOICE_POOL) | 66 | `kingwen_ternary_tables_complete.py` | `python -c "import kingwen_ternary_tables_complete as m; print(len(m.EMOTIONAL_POOL))"` | `PROVEN` | 66 |
| 1.19 | `EMOTIONAL_WEIGHTS.get_emotional_weights()` | `Function` | Returns emotional weights for a hexagram | Present at line 14482 | `kingwen_ternary_tables_complete.py` | `grep -n "def get_emotional_weights" kingwen_ternary_tables_complete.py` | `PROVEN` | Function exists |
| 1.20 | `HEXAGRAM_BASE_TYPED` | `Final[Dict[int, Dict[str, Any]]]` | Typed alias of `HEXAGRAM_BASE` (identity-preserving, no copy) | `HEXAGRAM_BASE_TYPED is HEXAGRAM_BASE` = True | `full_hexagram_shotgun.py` | `python -c "from scripts.full_hexagram_shotgun import HEXAGRAM_BASE_TYPED, HEXAGRAM_BASE; print(HEXAGRAM_BASE_TYPED is HEXAGRAM_BASE)"` | `PROVEN` | True — cast is identity-preserving |

**Governing invariant for this tier:** `HEXAGRAM_BASE` is the canonical source. No downstream generator may mutate or replace it. `HEXAGRAM_BASE_TYPED` is a `cast()` alias — identity-preserving, no copy.

---

## Section 2: Mathematical Specification Tier

| # | Formula/Invariant | Source Document | Expected | Observed | Verification Command | Status | Evidence |
|---|-------------------|----------------|----------|----------|---------------------|--------|----------|
| 2.1 | 9-bit encoding: `value = (upper_idx * 8 + lower_idx) * 8 + phase_bits` | `immutable-table-math-decoded.md` | Exact 0-511 coverage, 512 entries | Verified 0 mismatches across 512 entries | `python scripts/sandbox_verify_final.py` | `PROVEN` | 0 mismatches |
| 2.2 | Phase line map: 8 phase bit patterns → changing line positions | `immutable-table-math-decoded.md` | `phase_changing_lines` matches `PHASE_LINE_MAP[phase_bits]` for all 512 | 0 mismatches | `python scripts/sandbox_verify_final.py` | `PROVEN` | 0 mismatches |
| 2.3 | Ternary lines derived from binary + phase yao substitutions | `immutable-table-math-decoded.md` | 0 mismatches | 0 mismatches | `python scripts/sandbox_verify_final.py` | `PROVEN` | 0 mismatches |
| 2.4 | 9-bit space exact 0-511 coverage, no gaps | `immutable-table-math-decoded.md` | 512 entries, no gaps | 512 entries | `python scripts/sandbox_verify_final.py` | `PROVEN` | 512 entries, 0 gaps |
| 2.5 | BIT6_TO_HEXAGRAM roundtrip consistent with upper_idx/lower_idx | `immutable-table-math-decoded.md` | 0 mismatches | 0 mismatches | `python scripts/sandbox_verify_final.py` | `PROVEN` | 0 mismatches |
| 2.6 | phase_temporal consistent per phase_bits across all entries | `immutable-table-math-decoded.md` | 0 mismatches | 0 mismatches | `python scripts/sandbox_verify_final.py` | `PROVEN` | 0 mismatches |
| 2.7 | Gaussian consensus: `σ = max(10⁻⁹, η̄/2.0)` | `KING_WEN_CONSENSUS_MATH.md` §2.1 | σ computed from mean porosity | Not independently verified | `python -c "from emotional_engine import _compute_consensus_from_resolved; ..."` | `UNVERIFIED` | Needs test with controlled inputs |
| 2.8 | Un-decayed vector accumulation: `v_raw = Σ w_i v_i` (single pass) | `KING_WEN_CONSENSUS_MATH.md` §3.1 | Single-pass accumulation, not nested | Not independently verified | `python -c "from emotional_engine import _compute_consensus_from_resolved; ..."` | `UNVERIFIED` | Needs intermediate-value comparison |
| 2.9 | Open-pool blend: `v_consensus = 0.7*v_raw + 0.3*(0.6*p_avg + 0.4*s_avg)` | `KING_WEN_CONSENSUS_MATH.md` §3.2 | Fixed 30% pool weight, single execution | Not independently verified | `python -c "from emotional_engine import _compute_consensus_from_resolved; ..."` | `UNVERIFIED` | Needs intermediate-value comparison |
| 2.10 | Hamiltonian: `ℋ = Σ p_i · q̇^i - ℒ` with paired differentials | `ternary-paired-differential-math-correction-2026-08-02.md` | Signed differentials, not absolute ratios | `_hamiltonian_energy()` returns 0.0 for all 512 states (clamped) | `python -c "from emotional_engine import _hamiltonian_energy; ..."` | `KNOWN_CONCERN` | Zero output conceals intermediate differences; needs paired-differential comparison test |
| 2.11 | q̇^i = resolved_vector[i] - expanded_vector[i] (per-axis) | `ternary-paired-differential-math-correction-2026-08-02.md` | Per-axis phase derivative | Not independently verified against code | `grep -n "q_dot" emotional_engine.py` | `UNVERIFIED` | Code uses `resolved - expanded` per VEC_KEYS; needs test |
| 2.12 | Lagrangian: `ℒ = |dy|*0.5 + |yao_dy|*0.3 + |changing_dy|*0.2` | `ternary-paired-differential-math-correction-2026-08-02.md` | Paired differentials, not absolute counts | Not independently verified | `grep -n "dy.*yao_dy.*changing_dy" emotional_engine.py` | `UNVERIFIED` | Needs test with controlled line states |
| 2.13 | 5-axis vector uses signed ternary differentials | `ternary-paired-differential-math-correction-2026-08-02.md` | dy, yao_dy, old_dy, stable_dy in all 5 axes | Code shows `dy`, `yao_dy`, `old_dy` in chaos/whimsy/darkTone; coherence/voiceWeight still use absolute terms | `grep -n "dy.*old_dy" emotional_engine.py` | `KNOWN_CONCERN` | coherence and voiceWeight formulas need separate review (still use absolute terms) |
| 2.14 | Boolean gating only at final decision gates | `ternary-paired-differential-math-correction-2026-08-02.md` | No boolean in math/scoring/phase-rate layers | Not audited | `grep -rn "is True\|== 0\|== 1" emotional_engine.py decision_matrix.py` | `UNVERIFIED` | Needs grep + manual review |

---

## Section 3: Executable Pipeline Tier

### 3.1 State Expansion (I Ching Engine)

| # | Symbol | Input | Output | Verification Command | Status | Evidence |
|---|--------|-------|--------|---------------------|--------|----------|
| 3.1.1 | `shotgun_expand()` | `request_text: str`, `emotional_input: int` | `{expanded: [64], resolved: [512], source: 'kingwen-shotgun-expand', total_expanded: 64, total_resolved: 512, ternary_line_permutations_per_hex: 729, total_ternary_line_permutations: 46656, total_domained_routes: 35000, ...}` | `PYTHONPATH=scripts python3 -c "from full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); print(len(r['expanded']), len(r['resolved']))"` | `PROVEN` | 64, 512 |
| 3.1.2 | `shotgun_expand()` deterministic across hash seeds | Same input + 5 PYTHONHASHSEED values | Identical SHA-256 hash | `for seed in 0 1 42 12345 99999; do PYTHONHASHSEED=$seed ...; done` | `PROVEN` | Identical hash across all 5 seeds |
| 3.1.3 | `shotgun_expand()` all 64 hex IDs present | `expanded[]` | All hex IDs in range 1-64 | `python3 -c "from scripts.full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); ids=[e['hexagram_id'] for e in r['expanded']]; print(sorted(ids)==list(range(1,65)))"` | `PROVEN` | True |
| 3.1.4 | `shotgun_expand()` no winner/dominant collapse | `expanded[]`, `resolved[]` | `winner=None`, `dominantEntry=None` | `python3 -c "from scripts.full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); print(r.get('winner'), r.get('dominantEntry'))"` | `UNVERIFIED` | Needs test — not yet run |
| 3.1.5 | `expand_hexagram()` | `hexagram_id`, `emotional_input` | Expanded dict with inject_site, resolved_vector, line_balance, etc. | `python3 -c "from emotional_engine import expand_hexagram; e=expand_hexagram(1, 50); print(list(e.keys()))"` | `UNVERIFIED` | Needs test |
| 3.1.6 | `sample_resolve()` | `expanded`, `emotional_input` | 512 resolved states | `python3 -c "from emotional_engine import sample_resolve; ..."` | `UNVERIFIED` | Needs test |
| 3.1.7 | `capture_pre_slider()` | `request_text: str` | `{expanded: [...], resolved: [...]}` | `PYTHONPATH=scripts python3 -c "from emotional_engine import capture_pre_slider; r=capture_pre_slider('test'); print(len(r['expanded']), len(r['resolved']))"` | `PROVEN` | 64, 512 |
| 3.1.8 | `_compute_consensus_from_resolved()` | `resolved: list`, `emotional_input: int` | Consensus dict with consensus_hexagram_id, consensus_vector, etc. | `python3 -c "from emotional_engine import _compute_consensus_from_resolved; ..."` | `UNVERIFIED` | Needs test with controlled inputs |
| 3.1.9 | `_hamiltonian_energy()` | `resolved_vector`, `expanded_vector`, `line_balance` | Float (clamped 0-1) | `python3 -c "from emotional_engine import _hamiltonian_energy; print(_hamiltonian_energy({'chaos':0.5,'whimsy':0.3,'darkTone':0.2,'coherence':0.7,'voiceWeight':0.6}, {'chaos':0.4,'whimsy':0.2,'darkTone':0.1,'coherence':0.5,'voiceWeight':0.4}, {'yang_count':6,'yin_count':0,'yao_count':0}))"` | `KNOWN_CONCERN` | Returns 0.0 (clamped) for all inputs |
| 3.1.10 | `_quantum_avatar_modulation()` | `hexagram_id`, `resolved`, `expanded` | Wavefunction, rotation, scale, color | `python3 -c "from emotional_engine import _quantum_avatar_modulation; ..."` | `UNVERIFIED` | Needs test |
| 3.1.11 | `_pool_weights_for_hex()` | `hexagram_id`, `emotional_input` | Porosity from HEXAGRAM_INJECTION_SITE + emotional_input | `python3 -c "from emotional_engine import _pool_weights_for_hex; ..."` | `UNVERIFIED` | Needs test |

### 3.2 Identity Preservation (First-Class Gate)

| # | Invariant | Expected | Observed | Verification Command | Status | Evidence |
|---|-----------|----------|----------|---------------------|--------|----------|
| 3.2.1 | 64 canonical identities retain own mappings | Each hexagram's inject_site, emotional weights, category, action unchanged through expansion | Not verified end-to-end | `python3 -c "from scripts.full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); [print(e['hexagram_id'], e.get('inject_site',{}).get('primary_pool')) for e in r['expanded']]"` | `UNVERIFIED` | Needs per-hexagram comparison |
| 3.2.2 | 512 binary states retain canonical identity/phase association | Each resolved state's hexagram_id matches its expanded parent | Not verified | `python3 -c "from scripts.full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); [print(x['hexagram_id'], x['phase_bits']) for x in r['resolved'][:5]]"` | `UNVERIFIED` | Needs association test |
| 3.2.3 | 729 ternary states do not replace 64 canonical identities | Ternary expansion is separate from canonical table | Not verified | `python3 -c "import json; d=json.load(open('scripts/ternary_full_expansion.json')); print(len(d['hexagrams']))"` | `UNVERIFIED` | Needs cross-reference test |
| 3.2.4 | 5,832 resolved ternary states preserve provenance | Each resolved state traces to its hexagram + phase | Not verified | `python3 -c "import json; d=json.load(open('scripts/ternary_full_expansion.json')); print(len(d['resolved']))"` | `UNVERIFIED` | Needs provenance test |
| 3.2.5 | Selection (argmax) does not erase other candidates | Other 63 hexagrams remain in expanded[] after selection | `winner=None`, `dominantEntry=None` in shotgun output | `python3 -c "from scripts.full_hexagram_shotgun import shotgun_expand; r=shotgun_expand(emotional_input=50); print('winner:', r.get('winner'), 'dominant:', r.get('dominantEntry'), 'count:', len(r['expanded']))"` | `UNVERIFIED` | Needs test — not yet run |
| 3.2.6 | No cross-hexagram normalization | No hexagram's representation transformed to conform to another's | Not verified | `grep -rn "normalize.*hexagram\|hexagram.*normalize" emotional_engine.py scripts/*.py` | `UNVERIFIED` | Needs grep + manual review |
| 3.2.7 | No universal fallback to Hexagram 1 | Missing mappings remain explicitly missing | Not verified | `grep -rn "or 1\b\|default.*hexagram.*1\|Hexagram 1" emotional_engine.py scripts/*.py` | `UNVERIFIED` | Needs grep + manual review |

### 3.3 Decision Matrix

| # | Symbol | Input | Output | Verification Command | Status | Evidence |
|---|--------|-------|--------|---------------------|--------|----------|
| 3.3.1 | `_hamiltonian_alignment_score()` | `resolved_item`, `expanded_item` | Float (alignment score) | `grep -n "q_dot\|pq_dot" decision_matrix.py` | `UNVERIFIED` | Needs test |
| 3.3.2 | `_neighbor_continuity_score()` | `current_vec`, `prev_vec`, `next_vec` | Float (continuity score) | `grep -n "prev_dy\|next_dy" decision_matrix.py` | `UNVERIFIED` | Needs test |

### 3.4 Determinism

| # | Invariant | Expected | Observed | Verification Command | Status | Evidence |
|---|-----------|----------|----------|---------------------|--------|----------|
| 3.4.1 | Deterministic serialization (sorted query_tokens) | Identical output across PYTHONHASHSEED values | Identical SHA-256 hash across 5 seeds | `for seed in 0 1 42 12345 99999; do PYTHONHASHSEED=$seed ...; done` | `PROVEN` | Identical hash |
| 3.4.2 | No pseudo-RNG in engine math | No `random.random()`, `np.random.rand()` without explicit seed | Not audited | `grep -rn "random\." emotional_engine.py decision_matrix.py scripts/full_hexagram_shotgun.py` | `UNVERIFIED` | Needs grep |

---

## Section 4: Migration Contract Tier (lua-math-tool.md)

| # | Documented Interface | Actual Python Symbol | Classification | Verification Command | Status | Evidence |
|---|---------------------|---------------------|----------------|---------------------|--------|----------|
| 4.1 | `semantic_math.extract()` | `extract_pdf_math()` | **Renamed** | `grep -n "def extract_pdf_math" scripts/semantic_math_extractor.py` | `KNOWN_CONCERN` | Mismatch documented |
| 4.2 | `mathml_parser.parse()` | `MathMLParser.parse()` (returns str, not tree) | **Renamed + type mismatch** | `grep -n "def parse\|class MathMLParser" scripts/mathml_parser.py` | `KNOWN_CONCERN` | Mismatch documented |
| 4.3 | `math_context.extract_with_context()` | `extract_text_blocks()` | **Renamed** | `grep -n "def extract_text_blocks" scripts/math_context_extractor.py` | `KNOWN_CONCERN` | Mismatch documented |
| 4.4 | `display_eq.extract()` | `extract_display_equations()` | **Renamed** | `grep -n "def extract_display_equations" scripts/display_equation_extractor.py` | `KNOWN_CONCERN` | Mismatch documented |
| 4.5 | `symbol_classifier.LOOKUP` | `MATH_SYMBOL_LOOKUP` | **Renamed** | `grep -n "MATH_SYMBOL_LOOKUP" scripts/math_symbol_classifier.py` | `KNOWN_CONCERN` | Mismatch documented |
| 4.6 | `extract_clean.extract()` | CLI script, no module function | **Unsupported as documented** | `grep -n "def extract" scripts/extract_math_clean.py` | `KNOWN_CONCERN` | No module function exists |
| 4.7 | `tex_macros.extract_macros()` | Script, not module | **Unsupported as documented** | `grep -n "def extract_macros" scripts/extract_tex_macros.py` | `KNOWN_CONCERN` | No module function exists |
| 4.8 | `jspace_math.extract_function()` | Different input/output contract | **Adapter required** | `grep -n "def " scripts/extract_jspace_math.py` | `KNOWN_CONCERN` | Contract mismatch documented |

**Governing rule for this tier:** `lua-math-tool.md` is a design document, not proof of Python behavior or Lua parity. It must be corrected against actual Python implementations before the Lua port begins.

---

## Section 5: Math Pipeline Tier (Separate from I Ching)

### 5.1 Math Extraction

| # | Symbol | Input | Output | Verification Command | Status | Evidence |
|---|--------|-------|--------|---------------------|--------|----------|
| 5.1.1 | `semantic_math_extractor.extract_pdf_math()` | PDF file path | `{total_math_expressions, proof_chain_elements, math_images, ...}` | `python scripts/semantic_math_extractor.py --help` | `PROVEN` | Help runs, exits 0 |
| 5.1.2 | `semantic_math_extractor` arXiv path | `--arxiv 2605.00155` | Runs extraction | `python scripts/semantic_math_extractor.py --arxiv 2605.00155` | `PROVEN` | Runs, exits 0 |
| 5.1.3 | `semantic_math_extractor` PDF path | `--pdf <file>` | Runs extraction | `python scripts/semantic_math_extractor.py --pdf` | `PROVEN` | Runs (no PDF dir configured, graceful) |
| 5.1.4 | `mathml_parser.MathMLParser` | HTML string | Parsed MathML tree | `python -c "from scripts.mathml_parser import MathMLParser; ..."` | `UNVERIFIED` | Import guard fails (`parse_mathml_tree` doesn't exist) |
| 5.1.5 | `math_recovery_tool` | Raw LaTeX string | Recovered LaTeX | `python -c "from scripts.math_recovery_tool import ..."` | `UNVERIFIED` | Needs import test |
| 5.1.6 | `math_context_extractor.extract_text_blocks()` | HTML/text | Text blocks with context | `grep -n "def extract_text_blocks" scripts/math_context_extractor.py` | `SPECIFIED` | Function exists, not tested |
| 5.1.7 | `display_equation_extractor.extract_display_equations()` | HTML | Display equations | `grep -n "def extract_display_equations" scripts/display_equation_extractor.py` | `SPECIFIED` | Function exists, not tested |
| 5.1.8 | `math_symbol_classifier.MATH_SYMBOL_LOOKUP` | Symbol string | Symbol classification | `grep -n "MATH_SYMBOL_LOOKUP" scripts/math_symbol_classifier.py` | `SPECIFIED` | Constant exists, not tested |
| 5.1.9 | `extract_math_clean` (CLI) | PDF/HTML input | Clean math extraction | `python scripts/extract_math_clean.py --help` | `UNVERIFIED` | Needs help test |
| 5.1.10 | `extract_tex_macros` (CLI) | LaTeX source | Macro definitions | `python scripts/extract_tex_macros.py --help` | `UNVERIFIED` | Needs help test |

### 5.2 Math Occurrence Accounting

| # | Invariant | Expected | Observed | Verification Command | Status | Evidence |
|---|-----------|----------|----------|---------------------|--------|----------|
| 5.2.1 | Occurrence identity uses SHA-256 over paper_id/version/locator/index | No LaTeX in identity key | Not verified | `python -c "from scripts.math_occurrence_accounting import OccurrenceLedger; ..."` | `UNVERIFIED` | Needs test |
| 5.2.2 | Content change separate from identity change | Same identity, different content → update, not new entry | Not verified | `python -c "from scripts.math_occurrence_accounting import OccurrenceLedger; ..."` | `UNVERIFIED` | Needs test |
| 5.2.3 | Attempts ≠ equations | Count of attempts ≠ count of equations | Not verified | `grep -n "attempts\|equations" scripts/math_occurrence_accounting.py` | `UNVERIFIED` | Needs test |
| 5.2.4 | Legacy ambiguity stays visible | Ambiguous entries flagged, not silently resolved | Not verified | `grep -n "ambig\|legacy" scripts/math_occurrence_accounting.py` | `UNVERIFIED` | Needs test |

### 5.3 Math Recovery

| # | Symbol | Input | Output | Verification Command | Status | Evidence |
|---|--------|-------|--------|---------------------|--------|----------|
| 5.3.1 | `math_recovery_tool` | Raw LaTeX string | Recovered LaTeX | `python -c "import scripts.math_recovery_tool; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.2 | `math_contract.py` | Various | Canonical IR (ExprNode, Integral) | `python -c "import scripts.math_contract; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.3 | `structural_ast_extractor` | LaTeX/MathML | Structural AST | `python -c "import scripts.structural_ast_extractor; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.4 | `math_structure_extractor` | LaTeX/MathML | Structure extraction | `python -c "import scripts.math_structure_extractor; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.5 | `prose_math_extractor` | Text | Prose math extraction | `python -c "import scripts.prose_math_extractor; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.6 | `visual_math_translator` | Visual math | Translated math | `python -c "import scripts.visual_math_translator; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.7 | `chroma_visual_reader` | Visual math | Chroma visual reading | `python -c "import scripts.chroma_visual_reader; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.8 | `alttext_cross_checker` | Alt text + math | Cross-check results | `python -c "import scripts.alttext_cross_checker; ..."` | `UNVERIFIED` | Needs import test |
| 5.3.9 | `math_context_extractor` | Math + context | Context extraction | `python -c "import scripts.math_context_extractor; ..."` | `UNVERIFIED` | Needs import test |

### 5.4 Math Pipeline Verification

| # | Invariant | Expected | Verification Command | Status | Evidence |
|---|-----------|----------|---------------------|--------|----------|
| 5.4.1 | Two-stage separation (Stage 1 = source fidelity, Stage 2 = computational validity) | Both stages must pass or be explicitly flagged | `grep -n "stage1_skipped\|both stages passed" scripts/*.py` | `UNVERIFIED` | Needs audit |
| 5.4.2 | Operator preservation (no stripping of non-alphanumeric operators) | Inner products, norms, non-equality relations preserved | `grep -rn "re.sub.*\\\\w" scripts/math_recovery_tool.py` | `UNVERIFIED` | Needs audit |
| 5.4.3 | UTF-8 invariant (all file reads/writes specify encoding) | `encoding="utf-8"` in all file operations | `grep -rn "read_text()\|write_text()" scripts/*.py` | `UNVERIFIED` | Needs audit |
| 5.4.4 | No mass replace files (surgical edits only) | No bulk file rewrites in scripts | `git log --oneline -- scripts/` | `UNVERIFIED` | Needs audit |

---

## Section 6: Evidence and Verification Tier

### 6.1 Commit `71fbf28f8e` Audit

| # | Finding | Expected | Observed | Status | Evidence |
|---|---------|----------|----------|--------|----------|
| 6.1.1 | Canonical table untouched | `kingwen_ternary_tables_complete.py` absent from diff | Absent from changed-file list | `PROVEN` | `git show --name-only 71fbf28f8e` |
| 6.1.2 | CSV changes limited to token ordering | Only `query_tokens` field differs | 64/64 expanded + 512/512 resolved rows differ only in `query_tokens` | `PROVEN` | Python CSV comparison script |
| 6.1.3 | Three regressions corrected | `verify_restored_state.py`, `capture_pre_slider` import, `sorted(word_set)` | All three fixed and verified | `PROVEN` | `py_compile` + probe run + hash seed test |
| 6.1.4 | Four pre-existing concerns documented | Hamiltonian 0.0, mathml import guard, scripts shadowed, mutable global | Documented, not classified as regressions | `PROVEN` | Audit report §Pre-Existing Issues |
| 6.1.5 | Eight interface mismatches identified | 4 renamed, 2 unsupported, 1 adapter-required, 1 renamed+type-mismatch | Documented in audit report | `PROVEN` | Audit report §Interface Mismatch Reconciliation |
| 6.1.6 | Six acceptance criteria established | Determinism, canonical integrity, identity preservation, occurrence conservation, interface fidelity, parity | All six defined as independent gates | `PROVEN` | Audit report §Six Acceptance Criteria |

### 6.2 Test Suite Status

| # | Test File | Expected | Observed | Status | Evidence |
|---|-----------|----------|----------|--------|----------|
| 6.2.1 | `learn/scripts/test_deterministic_replay.py` | Passes with stable hash | Not run (import path issues) | `UNVERIFIED` | Blocked by `scripts` shadowing |
| 6.2.2 | `learn/scripts/test_porosity_sweep.py` | Shows porosity modulation | Not run (import path issues) | `UNVERIFIED` | Blocked by `scripts` shadowing |
| 6.2.3 | `learn/scripts/test_collapse_full_128.py` (renamed to `test_collapse_full_512.py`) | Passes | Not run | `UNVERIFIED` | Blocked by `scripts` shadowing |
| 6.2.4 | `learn/scripts/test_progressive_intents.py` | Diagnostic only | Not run | `UNVERIFIED` | Blocked by `scripts` shadowing |
| 6.2.5 | `scripts/verify_math_jacobian_hamiltonian.py` | Exits 0 | Not run | `UNVERIFIED` | Needs run |
| 6.2.6 | `scripts/verify_output_mismatches.py` | Exits 0 | Not run | `UNVERIFIED` | Needs run |
| 6.2.7 | `scripts/verify_registry.py` | Exits 0 | Not run | `UNVERIFIED` | Needs run |

---

## Section 7: Six Acceptance Gates (Independent)

| Gate | Criterion | Current Status | Blocking |
|------|-----------|----------------|----------|
| 1 | **Determinism**: identical inputs produce identical serialized outputs | `PROVEN` | No |
| 2 | **Canonical integrity**: generators do not mutate or replace canonical table | `PROVEN` | No |
| 3 | **Identity preservation**: all 64 hexagrams retain distinct identity and associated mappings across every applicable pipeline stage | `UNVERIFIED` | Yes — needs per-hexagram tests |
| 4 | **Occurrence conservation**: extraction preserves provenance-bearing occurrences, including multiplicity | `UNVERIFIED` | Yes — needs multiset conservation tests |
| 5 | **Interface fidelity**: migration specification accurately describes actual Python contracts | `KNOWN_CONCERN` | Yes — 8 mismatches remain |
| 6 | **Parity**: Lua results match validated Python baseline without cross-hexagram normalization, substitution, or convergence | `SPECIFIED` | Yes — 10 tests not yet written; Lua port blocked |

---

## Section 8: Governing Invariants (Referenced by All Sections)

### Invariant A: No Cross-Hexagram Normalization

Each of the 64 hexagrams retains its own identity, structure, mappings, meaning, and traceable outputs throughout expansion, resolution, extraction, and serialization.

- **Scope:** All pipeline stages (expansion, resolution, extraction, serialization, migration)
- **Prohibition:** No semantic convergence, no identity-erasing deduplication, no universal fallback, no normalization disguised as serialization
- **Exception:** Within-hexagram processing may normalize if explicitly permitted by project rules
- **Referenced by:** Sections 1, 2, 3, 4, 5, 7

### Invariant B: Expansion-First, Normalization-Last

Always capture all 64 canonical + 665 ternary hexagrams before any selection layer.

- **Scope:** All expansion and resolution operations
- **Prohibition:** No 1-hex early collapse, no premature selection
- **Referenced by:** Sections 1, 2, 3, 7

### Invariant C: Canonical Table is Immutable Contract

`kingwen_ternary_tables_complete.py` is the source of truth. Generators conform to it; they do not redefine it.

- **Scope:** All code that reads or transforms hexagram data
- **Prohibition:** No mutation, no replacement, no fallback to Hexagram 1
- **Referenced by:** Sections 1, 3, 7

### Invariant D: Math Pipeline Separate from I Ching Pipeline

Math extraction, parsing, recovery, occurrence tracking, and serialization have their own contracts. Integration points are documented but not assumed ready.

- **Scope:** Math pipeline (`scripts/semantic_math_extractor.py`, `scripts/mathml_parser.py`, etc.) vs I Ching pipeline (`emotional_engine.py`, `full_hexagram_shotgun.py`, etc.)
- **Prohibition:** No merging of math extractor into I Ching state-expansion path until contracts and validation are established
- **Referenced by:** Sections 4, 5, 7

---

## Section 9: Expected vs Observed Result Distinction

The following examples illustrate the distinction between expected, observed, and proven results:

| Claim | Expected (from spec) | Observed (from probe) | Proven? | Notes |
|-------|---------------------|----------------------|---------|-------|
| 64 canonical hexagrams | 64 | 64 | Yes | `len(HEXAGRAM_BASE)` = 64 |
| 512 binary states | 512 | 512 | Yes | `len(HEX_PHASE_TO_9BIT)` = 512 |
| 729 ternary hexagrams | 729 | Not independently verified | No | Needs cross-reference test |
| 5,832 resolved ternary states | 5,832 | Not independently verified | No | Needs provenance test |
| 64 expanded per shotgun_expand | 64 | 64 | Yes | `len(r['expanded'])` = 64 |
| 512 resolved per shotgun_expand | 512 | 512 | Yes | `len(r['resolved'])` = 512 |
| All 64 hex IDs in range 1-64 | 64 distinct IDs | 64 distinct IDs | Yes | `sorted(ids) == list(range(1,65))` |
| No winner/dominant collapse | `winner=None`, `dominantEntry=None` | Not yet tested | No | Needs test |
| Hamiltonian energy | Non-zero for balanced hexagrams | 0.0 for all (clamped) | Known concern | Pre-existing structural issue |
| query_tokens deterministic | Same order across hash seeds | Identical hash across 5 seeds | Yes | `sorted(word_set)` fix verified |

---

## Section 10: Recommended Build Order for Parity Tests

Before writing the 10 Python parity tests, the following must be completed:

1. **Correct 8 interface mismatches** in `lua-math-tool.md` (4 renamed, 2 unsupported, 1 adapter-required, 1 renamed+type-mismatch)
2. **Define test scope** for each of the 6 acceptance gates
3. **Write test for Gate 1 (Determinism):** identical inputs → identical serialized outputs (already partially verified)
4. **Write test for Gate 2 (Canonical integrity):** `HEXAGRAM_BASE` unchanged after pipeline run (already partially verified)
5. **Write test for Gate 3 (Identity preservation):** each hexagram's inject_site, emotional weights, category, action unchanged through expansion and resolution
6. **Write test for Gate 4 (Occurrence conservation):** multiset of provenance-bearing occurrence keys preserved through extraction
7. **Write test for Gate 5 (Interface fidelity):** each documented interface matches actual Python symbol
8. **Write test for Gate 6 (Parity):** Lua results match Python baseline (blocked until gates 1-5 pass)

**Do not begin the Lua port until gates 1-5 are green.**

---

*This matrix is a living document. Entries marked `UNVERIFIED` must be checked against the actual repository before being marked `PROVEN`. No canonical code or data was modified in the creation of this matrix.*