# /learn — King Wen Test Pass Suite

These are the progressive-intent and consensus-verification scripts for the
porosity-driven state machine. They are real executable passes, not stubs.

## Primary Master Pipeline Runner `[Updated 2026-08-29]`

To run the complete 18-stage pipeline covering state expansion, 3D meshes, voice profiles, JKD audio pellets, quantum space-time plots, and parity audits:

```bash
python scripts/run_all_unified_pipeline.py
```

## Legacy / Individual Scripts

- `learn/scripts/test_collapse_full_128.py` (legacy 512-state runner)
- `learn/scripts/test_progressive_intents.py`
- `learn/scripts/test_porosity_sweep.py`
- `learn/scripts/test_deterministic_replay.py`

## Run from tables root

```bash
python learn/scripts/test_progressive_intents.py
python learn/scripts/test_porosity_sweep.py
python learn/scripts/test_deterministic_replay.py
```

## Status

All passes verify deterministic consistency against `kingwen_ternary_tables_complete.py` and `HEXAGRAM_BASE`.

