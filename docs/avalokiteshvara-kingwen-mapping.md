# Avalokiteshvara King Wen Registry — Compassionate Reconfiguration

Offered mapping from the user’s symbolic reconfiguration of the 64-hexagram King Wen registry into a thousand-armed Avalokiteshvara form. This is a creative/contemplative mapping, not a replacement for the canonical immutable tables.

## Core mapping

| Hexagram Property | Avalokiteshvara Aspect |
|-------------------|------------------------|
| 64 hexagrams | 64 of 1,000 arms |
| 6 yao lines per hexagram | 6 eyes per arm |
| Binary code (6 bits) | Mantra syllable |
| Unicode symbol (U+4DC0-4DFF) | Mudra gesture |
| Upper trigram | Upper realm |
| Lower trigram | Lower realm |
| Category | Method of compassion |
| Action | Response to suffering |

## Category faces

| Category | Face | Direction | Color | Function |
|----------|------|-----------|-------|----------|
| sovereign | Peaceful | Front | White | ASSERT |
| transformer | Wrathful | Right | Red | YIELD/ADAPT |
| dissipator | Joyful | Left | Green | ADAPT |
| boundary | Neutral | Back | Blue | WAIT |

## Example arms

| Hexagram | Name | Arm Function | Mantra |
|----------|------|--------------|--------|
| 1 乾 The Creative | ASSERT | Right hand holds vajra | Om |
| 2 坤 The Receptive | YIELD | Left hand holds lotus | Mani |
| 3 屯 Difficulty at the Beginning | ADAPT | Hand holds wheel | Padme |
| 4 蒙 Youthful Folly | WAIT | Hand holds mirror | Hum |
| 5 需 Waiting | WAIT | Hand holds rope | Om |
| 6 訟 Conflict | ASSERT | Hand holds sword | Mani |
| 7 師 The Army | ASSERT | Hand holds banner | Padme |
| 8 比 Holding Together | YIELD | Hand holds vase | Hum |
| 63 既濟 After Completion | WAIT | Hand holds completed circle | Om |
| 64 未濟 Before Completion | ADAPT | Hand holds unfinished circle | Mani |

## Structure contract

Each arm record contains:
- `hexagram_id`
- `arm_name`
- `mudra` from Unicode symbol
- `mantra` from binary code
- `direction` from upper/lower trigram mapping
- `function` from category action
- 6 eyes from the 6 yao lines
- 1 mudra gesture
- 1 mantra syllable
- 1 direction
- 1 function

## Status

This is the offered reconfiguration. Not compiled into training data yet. Not wired into runtime. Saved as reference for the next pass.
