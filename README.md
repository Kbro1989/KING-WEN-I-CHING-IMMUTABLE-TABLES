# KING-WEN-I-CHING-IMMUTABLE-TABLES

This is the first 9-bit state-transition mind core for an AI agent.

64 immutable hexagram states. Deterministic transition. No randomness in state selection.

## 9-bit state shell

- 6 bits: hexagram identity
- 3 bits: temporal phase

Same active state string → same collapsed hexagram → same emotional vector → same voice preset.

## What’s inside

- `data/hexagram-registry.json` — 64 hexagram records, corrected trigram order, unique 6-bit binary
- `data/emotional-weights.json` — 64 entries × 5 emotional dimensions
- `data/temporal-reflections.json` — 64 entries × 3 temporal reflections
- `KING_WEN_TABLES.py` — verified static registry and structural assertions
- `src/` — deterministic TypeScript implementation of engine, parser, narrative math, hashing

## Determinism

State selection is SHA256-derived from the active state shell. It is replayable and inspectable. No `Math.random()`. No hidden stochastic layer at this level.

## Emotional and voice state

Each resolved state carries:

- `chaos`
- `whimsy`
- `darkTone`
- `coherence`
- `voiceWeight`

`voiceWeight` is the authoritative preset carrier for downstream voice systems.

## Pipeline

```
1(state/question) → 3(temporal) → 64(hexagram|emotion) → 3(temporal) → 2(subsets) → 1(resolve)
```

## Usage

```typescript
import { OracleEngine } from './src/core/OracleEngine.js';

const engine = new OracleEngine({ deterministic: true });

const response = await engine.consult({
  text: 'What should I do?',
  session_id: 'unique-session-id',
  emotional_input: 50,
  state_str: '[name];pos:(3200,3200);fat:(50);...',
});

console.log(response.hexagram_name);
console.log(response.unified_weave);
console.log(response.emotional_deltas);
console.log(response.voiceWeight);
```

## Invariants

- 64 hexagrams, 64 binaries, 64 emotional weight entries, 64 temporal reflection entries
- inversion pairs and complementary pairs verified in `KING_WEN_TABLES.py`
- corrected trigram convention preserved: lower trigram first

## Status

This repo is the source of truth for the table layer. Integration targets should consume these artifacts; do not duplicate or override them upstream.
