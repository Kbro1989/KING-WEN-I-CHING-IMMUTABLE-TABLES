# King Wen Immutable Table Math — Decoded 2026-07-14

Source: `C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py`
Verified by: `scripts/sandbox_verify_final.py` (ALL PASS)

## Core formulas

- **9-bit encoding:** `value = (upper_idx * 8 + lower_idx) * 8 + phase_bits`
- **6-bit trigram:** `value = (upper_idx << 3) | lower_idx`
- **9-bit space:** exact 0–511 coverage, 512 entries = 64 hexagrams × 8 phases
- **MAX_9BIT_VALUE:** 511 = 2^9 − 1

## Table structure

19 top-level immutable symbols:
- **Core math (6):** `HEXAGRAM_BASE` (64), `PHASE_LINE_MAP` (8), `PHASE_INFO` (8), `ENCODING_TABLE` (512), `HEX_PHASE_TO_9BIT` (512), `BIT6_TO_HEXAGRAM` (64)
- **Additive payload (5):** `VOICEBOX_VOICE_POOL`, `POROSITY_LEVELS`, `HEXAGRAM_INJECTION_SITE`, `YAO_VOCABULARY`, `EMOTIONAL_WEIGHTS`, `SLIDER_CHECKLIST`
- **Constants (4):** `TOTAL_HEXAGRAMS=64`, `TOTAL_PHASES=8`, `TOTAL_ENCODINGS=512`, `MAX_9BIT_VALUE=511`

## Verified properties

- 9-bit formula matches all 512 `HEX_PHASE_TO_9BIT` entries (0 mismatches)
- `phase_changing_lines` matches `PHASE_LINE_MAP[phase_bits]` for all 512 entries (0 mismatches)
- `ternary_lines_top_to_bottom` derived from `binary_top_to_bottom` + phase yao substitutions (0 mismatches)
  - Convention: stored array uses same left-to-right read order as `binary_top_to_bottom`
  - Changing lines are numbered 1–6 bottom-to-top; array index = `line_num - 1`
- 9-bit space has exact 0–511 coverage, no gaps
- `BIT6_TO_HEXAGRAM` roundtrip consistent with `upper_idx`/`lower_idx` (0 mismatches)
- `phase_temporal` consistent per `phase_bits` across all entries (0 mismatches)

## Phase line map

```
0b000 -> []
0b001 -> [1, 4]
0b010 -> [2, 5]
0b011 -> [1, 2, 4, 5]
0b100 -> [3, 6]
0b101 -> [1, 3, 4, 6]
0b110 -> [2, 3, 5, 6]
0b111 -> [1, 2, 3, 4, 5, 6]
```

## Decoded math summary

The file is a complete, self-contained 9-bit finite state machine:
- **tensor product:** trigram_space ⊗ trigram_space ⊗ phase_space
- **lossless round-trip:** any 9-bit value decomposes uniquely to (hexagram, phase)
- **phase gating:** phase bits control which line positions become yao (changing)
- **structural capacity:** 3^6 = 729 possible ternary states, only 512 reachable via phase-gated expansion; 217 states are structurally unreachable without violating `PHASE_LINE_MAP`
