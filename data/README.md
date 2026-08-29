# data/

Immutable lookup tables.

Edit policy: append-only. Do not delete or rewrite historical files.

Files:
- `hexagram-registry.json`: 64 canonical hexagrams with binary, Unicode, name, trigrams, category, action.
- `emotional-weights.json`: 5-axis emotional vector per hexagram: voiceWeight, coherence, chaos, whimsy, darkTone.
- `temporal-reflections.json`: Reflection strings across the 8 temporal phases (past, present, future, transition, resolution, dissolution, crystallization, void) covering 512 binary phase states (64×8). [Updated 2026-08-29]

Read by:
- `src/openjarvis/emotion/kingwen.py` (legacy consumer path) [Updated 2026-08-29]
- `scripts/build_hexagram_skill_cards.py`
- `scripts/multi_layer_expand.py`
- `scripts/open_pool_consensus.py`
