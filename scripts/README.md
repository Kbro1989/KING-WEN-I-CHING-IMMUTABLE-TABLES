# scripts/

Active generation and ingestion surface.

Read/write rule:
- `data/` and `docs/` are read-only sources of truth.
- `scripts/` owns generated/ingested artifacts.
- No secrets, API keys, or tokens in scripts.

Key files:
- `build_ternary_expansion.py`: builds `ternary_full_expansion.json` from immutable tables.
- `build_hexagram_skill_cards.py`: builds `hexagram_full_expansion.json` with skill cards and inversion pairs.
- `full_hexagram_shotgun.py`: first-parse 64-hex expansion with ternary slot matrix.
- `multi_layer_expand.py`: 64 expanded + 512 resolved + pool descriptives.
- `open_pool_consensus.py`: open-pool consensus across 512 states with tau scoring.
- `ingest_jkd_gutenberg.py`: batch ingestion from `DATASETS/jkd_full_text.txt` to JSONL outputs.
- `schauberger_parsing_layers.py`: mechanism → inversion → drift classification parser.
- `query_layer_probe.py`: query-layer diagnostics.
- `run.py`, `run_all.py`, `run_generators.py`: convenience runners.

Generated artifacts:
- `ternary_full_expansion.json`: 27 trigrams, 729 hexagrams, 5,832 resolved states.
- `hexagram_full_expansion.json`: 64 hexagrams, 512 resolved states, personalities.
