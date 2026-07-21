# /learn — King Wen Test Pass Suite

These are the progressive-intent and consensus-verification scripts for the
porosity-driven state machine. They are real executable passes, not stubs.

## Scripts

- `learn/scripts/test_collapse_full_128.py`
- `learn/scripts/test_progressive_intents.py`
- `learn/scripts/test_porosity_sweep.py`
- `learn/scripts/test_deterministic_replay.py`

## Run from tables root

```bash
cd C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES
PYTHONPATH=. python3 learn\scripts\test_collapse_full_128.py --emotional-input 50
PYTHONPATH=. python3 learn\scripts\test_progressive_intents.py
PYTHONPATH=. python3 learn\scripts\test_porosity_sweep.py
PYTHONPATH=. python3 learn\scripts\test_deterministic_replay.py
```

## Status

These pass on live immutable-table state. If any fails, it indicates a drift
between `emotional_engine.py` and the canonical tables.
