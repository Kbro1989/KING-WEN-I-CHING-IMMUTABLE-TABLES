# King Wen I Ching — Immutable Tables

> Python · TypeScript · Symbolic Data

Immutable lookup tables for the King Wen hexagram sequence — foundational data layer
for `HexagramManager` and `TernaryRouter` across the POG2 system.

## Key Files

| File | Purpose |
|---|---|
| `KING_WEN_TABLES.py` | Primary 64-hexagram × 6-yao sequence definitions |
| `kingwen_ternary_tables_complete.py` | 729-path ternary routing tables (3^6) |
| `emotionalweights.json` | Emotional valence weights per hexagram state |

## Structure

```
KING-WEN-TABLES/   structured table directory
data/              raw data
dist/              built output
src/               TypeScript table consumers
scripts/           generation utilities
tests/             verification tests
```

## Integration

Consumed by `I-Ching_Oracle` (Cloudflare Worker) for `HexagramManager` 64-state machine
and `TernaryRouter` 729→64 path resolution. See `king-wen-workflow-paths.md`.
