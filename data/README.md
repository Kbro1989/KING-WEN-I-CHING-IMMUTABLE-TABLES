# data/

Immutable lookup tables.

Edit policy: append-only. Do not delete or rewrite historical files.

Files:
- `hexagram-registry.json`: 64 canonical hexagrams with binary, Unicode, name, trigrams, category, action.
- `emotional-weights.json`: 5-axis emotional vector per hexagram: voiceWeight, coherence, chaos, whimsy, darkTone.
- `temporal-reflections.json`: past/present/future reflection strings per hexagram.

Read by:
- `src/openjarvis/emotion/kingwen.py`
- `scripts/build_hexagram_skill_cards.py`
- `scripts/multi_layer_expand.py`
- `scripts/open_pool_consensus.py`
