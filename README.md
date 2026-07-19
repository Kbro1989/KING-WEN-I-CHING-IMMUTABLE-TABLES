# King Wen I Ching — Immutable Tables

> Python · TypeScript · Symbolic Data · 27-Ternary Expansion · 5,832 States

This repository is the **read-only source of truth** for the King Wen state machine:
- **64 canonical binary hexagrams** with upper/lower trigrams, Unicode, category, action
- **8 binary trigrams** mapped to names and symbols
- **27 ternary trigrams** as math-first vectors (`3^3`)
- **729 ternary hexagrams** (`27 × 27`) with 64 canonical subset preserved
- **5,832 resolved states** (`729 × 8`)
- **512 binary resolved states** (`64 × 8`) for backward-compatible consumers

## Folder Map

### `data/`
Canonical immutable tables. Do **not** edit history; append-only only.

| File | Purpose |
|---|---|
| `hexagram-registry.json` | 64 canonical hexagrams with `binary`, `unicode`, `upper_trigram`, `lower_trigram`, `category`, `action` |
| `emotional-weights.json` | 5-axis voice vectors per hexagram: `voiceWeight`, `coherence`, `chaos`, `whimsy`, `darkTone` |
| `temporal-reflections.json` | `past`, `present`, `future` reflection strings per hexagram |

### `scripts/`
The active formalization surface. **5,832-state runtime path** is built here.

| File | Purpose |
|---|---|
| `build_ternary_expansion.py` | Generates `ternary_full_expansion.json` from immutable tables: 27 trigrams, 729 hexagrams, 5,832 resolved states |
| `ternary_full_expansion.json` | **2.9 MB** canonical artifact: full ternary expansion with `trigrams`, `hexagrams`, `resolved` |
| `build_hexagram_skill_cards.py` | Builds per-binary-position `/skill` cards: `{}`/`[]`/`()`/`!` mappings |
| `hexagram_full_expansion.json` | Binary expansion artifact: 64 hexagrams, 512 states, personalities, inversion pairs |
| `ingest_jkd_gutenberg.py` | Batch ingestion runner: `jkd_full_text.txt` → `jkd_ingestion_binary.jsonl` + `jkd_ingestion_ternary.jsonl` |
| `full_hexagram_shotgun.py` | First-parse shotgun blast: 64 expanded + 512 resolved, no early collapse |
| `multi_layer_expand.py` | Layer 1–5 expansion with ternary line options and pool descriptives |
| `open_pool_consensus.py` | Open-pool consensus across all 512 states with tau scoring, no hardcoded booleans |
| `run.py`, `run_all.py`, `run_generators.py` | Convenience runners for generators |
| `generate_engine.py`, `generate_parser.py`, `generate_types.py`, `generate_utils.py` | TypeScript table generators |
| `schauberger_parsing_layers.py` | Viktor Schauberger parsing layer: original mechanism → inversions → drift classification |
| `export_voicebox_training.py` | Voicebox training export |
| `query_layer_probe.py` | Query-layer diagnostics |
| `sandbox_verify_final.py` | Sandbox verification |
| `demo.js` | JS demo |
| `verify_registry.py` | Registry verification |

### `docs/`
Research and math first, not hand-wavy definitions.

| File | Purpose |
|---|---|
| `immutable-table-math-decoded.md` | 9-bit formula, 512 → 729 expansion, `encode_hex_phase`, `decode_9bit` |
| `j-space-jacobian-lens-math-2026-07-11.md` | J-lens math: `J(a; v) ≈ E[∂y_v/∂a] · Δa`, Hamiltonian energy |
| `kingwen-jspace-domain-layer-2026-07-11.md` | Maps Anthropic’s J-space onto King Wen: 512/5,832 broadcast layer |
| `kingwen-quantum-methods-2026-07-11.md` | Quantum methods: collapse_full_128, superposition capture, tomography |
| `kingwen-superposition-expansion-plan-2026-07-11.md` | 27³ math, first-parse shotgun, layer expansion, consensus |
| `avalokiteshvara-kingwen-mapping.md` | 64-arm mapping for compassionate voice reconfiguration |
| `query_probe/` | Query probe artifacts |

### `src/`
TypeScript/JavaScript consumers of the immutable tables.

| File/Dir | Purpose |
|---|---|
| `index.ts`, `index.js` | Entry points |
| `core/` | Core runtime |
| `parser/` | Binary/ternary parsing |
| `types/` | TypeScript types |
| `utils/` | Utilities |

### `tests/`
Verification tests.

| File | Purpose |
|---|---|
| `oracle.test.ts` | Oracle contract tests |

### `learn/`
Training specs and integration maps. Not code edits.

| File/Dir | Purpose |
|---|---|
| `README.md` | Learning suite overview |
| `specs/` | Blueprint-mined integration specs |
| `exports/` | Integration maps and audits |
| `scripts/` | Learning pipeline scripts |
| `cache_version_correlation_2025_2026.json` | Cache version correlation |
| `runescape_updates_2025_2026.json` | RS cache updates 2025–2026 |

### `kingwen_train_data/`
Training data source layer for Megatron/jarvis/multi-domain learning.

| File | Purpose |
|---|---|
| `kingwen_quantum_process.py` | Hamiltonian energy, Gaussian kernel, trigram frequency weight |
| `superposition_capture.py` | Superposition capture |
| `kingwen_expansion_wrapper.py` | Expansion wrapper |
| `*.jsonl` | Pre-captured train/eval corpora |
| `rsmv_*` | RuneScape model viewer cache format samples |

### `kingwen_train_data_demo2/`
Demo/validation corpora.

| File | Purpose |
|---|---|
| `consensus_gaussian.json` | Per-hexagram/phase 6D stats |
| `expanded_source.jsonl` | Expanded source samples |
| `resolved_source.jsonl` | Resolved source samples |
| `learned_sequential_64.json` | Sequential 64 learned |
| `megatron_weights.csv` | Weight dump |

### `DATASETS/`
Ingestion outputs and raw source text.

| File | Purpose |
|---|---|
| `jkd_full_text.txt` | Tao of Jeet Kune Do — OCR raw source for batch ingestion |
| `jkd_ingestion_binary.jsonl` | 470 binary-mode consult records |
| `jkd_ingestion_ternary.jsonl` | 18 sampled ternary-mode consult records |
| `jkd_ingestion_summary.json` | Aggregate counts |
| `kingwen_consultation_record.json` | Consultation record |
| `*.csv` | Category, emotional timeseries, save strings, transition graph, trigram reference |

## Key Rules

1. **Immutable tables only.** `data/` is append-only. Do not delete or rewrite historical files.
2. **Expansion-first, normalization-last.** Always capture all 64 canonical + 665 ternary hexagrams before any selection layer.
3. **No mock/stub/placeholder** in `src/`, `scripts/`, `tests/`.
4. **Math-first trigrams.** 27 ternary trigrams from `[0,1,2] × [0,1,2] × [0,1,2]`; 8 binary trigrams are the canonical subset.
5. **No secrets in repos.** API keys, tokens, passwords stay out of `data/`, `docs/`, `scripts/`.

## Quick Start

```bash
# Build full ternary expansion artifact
python scripts/build_ternary_expansion.py

# Run shotgun first-parse expansion
python scripts/full_hexagram_shotgun.py

# Run multi-layer expansion with open-pool consensus
python scripts/multi_layer_expand.py

# Verify registry + inversion pairs
python KING_WEN_TABLES.py

# Ingest JKD text through King Wen consult
python scripts/ingest_jkd_gutenberg.py
```

## Outputs

- `scripts/ternary_full_expansion.json` — 27 trigrams, 729 hexagrams, 5,832 resolved states
- `scripts/hexagram_full_expansion.json` — 64 hexagrams, 512 resolved states, personalities, inversion pairs
- `scripts/build_hexagram_skill_cards.py` — per-binary-position skill cards
