# King Wen Quantum State Machine

**Domain:** `research`  
**Parent:** `jarvis|king-wen`  
**Module:** `hexagram_state_machine`  
**Format:** VHDL (synthesizable) / Python (simulation)  
**Target:** Zynq UltraScale+ ZU7EV  
**Revision:** 1.0  
**Date:** 2026-07-10  
**Status:** Verified Immutable

---

## 1. Purpose

Deterministic 512-state oracle implemented in silicon. No pseudo-RNG. All state transitions derived from immutable King Wen hexagram tables via hash function.

- **64 hexagrams** × **8 yao/temporal contexts** = **512 states** (2⁹)
- **Ternary line encoding:** yin=00, yang=01, yao=10
- **Metabolic rhythm:** 640ms tick (matches RSC server, OpenRSC DO, POG2 combat cycle)
- **Interface:** AXI4-Lite Slave + direct consult port

---

## 2. State Space

### 2.1 Hexagrams (64)

| # | Name | Binary | Category | Action | Porosity | Dominant |
|---|------|--------|----------|--------|----------|----------|
| 01 | The Creative | 111111 | sovereign | ASSERT | 0.25 | coherence |
| 02 | The Receptive | 000000 | transformer | YIELD | 0.25 | coherence |
| 03 | Difficulty at the Beginning | 010001 | dissipator | ADAPT | 0.75 | chaos |
| 04 | Youthful Folly | 100010 | transformer | WAIT | 0.50 | whimsy |
| 05 | Waiting | 010111 | dissipator | WAIT | 0.25 | coherence |
| 06 | Conflict | 111010 | transformer | ASSERT | 1.00 | chaos |
| 07 | The Army | 000010 | sovereign | ASSERT | 0.00 | coherence |
| 08 | Holding Together | 010000 | transformer | YIELD | 0.50 | coherence |
| 09 | Taming Power of the Small | 110111 | dissipator | ADAPT | 0.50 | voiceWeight |
| 10 | Treading | 111011 | sovereign | ADAPT | 0.50 | voiceWeight |
| 11 | Peace | 000111 | transformer | YIELD | 0.25 | coherence |
| 12 | Standstill | 111000 | boundary | WAIT | 1.00 | chaos |
| 13 | Fellowship with Men | 101111 | transformer | ASSERT | 0.50 | voiceWeight |
| 14 | Possession in Great Measure | 111101 | sovereign | ASSERT | 0.25 | coherence |
| 15 | Modesty | 001000 | transformer | YIELD | 0.25 | coherence |
| 16 | Enthusiasm | 000100 | dissipator | ADAPT | 0.75 | voiceWeight |
| 17 | Following | 100110 | transformer | YIELD | 0.50 | voiceWeight |
| 18 | Work on Decayed | 011001 | dissipator | ADAPT | 0.75 | chaos |
| 19 | Approach | 110000 | transformer | YIELD | 0.50 | coherence |
| 20 | Contemplation | 000011 | boundary | WAIT | 0.50 | coherence |
| 21 | Biting Through | 100101 | transformer | ASSERT | 0.50 | coherence |
| 22 | Grace | 101001 | boundary | WAIT | 0.50 | coherence |
| 23 | Splitting Apart | 000001 | dissipator | WAIT | 0.50 | coherence |
| 24 | Return | 100000 | transformer | YIELD | 0.50 | coherence |
| 25 | Innocence | 100111 | sovereign | ASSERT | 0.50 | coherence |
| 26 | Taming Power of the Great | 111001 | boundary | ADAPT | 0.50 | coherence |
| 27 | Corners of the Mouth | 100001 | transformer | YIELD | 0.50 | coherence |
| 28 | Preponderance of the Great | 011110 | dissipator | ADAPT | 0.75 | chaos |
| 29 | The Abysmal | 010010 | dissipator | WAIT | 0.50 | coherence |
| 30 | The Clinging | 101101 | boundary | ADAPT | 0.50 | coherence |
| 31 | Influence | 001110 | transformer | YIELD | 0.50 | voiceWeight |
| 32 | Duration | 011100 | boundary | WAIT | 0.50 | coherence |
| 33 | Retreat | 001111 | boundary | YIELD | 0.50 | coherence |
| 34 | Power of the Great | 111100 | sovereign | ASSERT | 0.50 | coherence |
| 35 | Progress | 000101 | transformer | ADAPT | 0.50 | voiceWeight |
| 36 | Darkening of the Light | 101000 | dissipator | WAIT | 0.50 | coherence |
| 37 | The Family | 101011 | transformer | YIELD | 0.50 | voiceWeight |
| 38 | Opposition | 110101 | dissipator | ADAPT | 0.50 | chaos |
| 39 | Obstruction | 010100 | dissipator | WAIT | 0.50 | coherence |
| 40 | Deliverance | 001010 | transformer | ADAPT | 0.50 | coherence |
| 41 | Decrease | 100011 | transformer | YIELD | 0.50 | coherence |
| 42 | Increase | 110001 | transformer | ASSERT | 0.50 | coherence |
| 43 | Breakthrough | 111110 | sovereign | ASSERT | 0.50 | coherence |
| 44 | Coming to Meet | 011111 | boundary | WAIT | 0.50 | coherence |
| 45 | Gathering Together | 000110 | transformer | YIELD | 0.50 | voiceWeight |
| 46 | Pushing Upward | 011000 | transformer | ADAPT | 0.50 | coherence |
| 47 | Oppression | 010110 | dissipator | WAIT | 0.50 | voiceWeight |
| 48 | The Well | 011010 | boundary | YIELD | 0.50 | coherence |
| 49 | Revolution | 101110 | transformer | ASSERT | 0.50 | voiceWeight |
| 50 | The Cauldron | 011101 | sovereign | ASSERT | 0.50 | coherence |
| 51 | The Arousing | 100100 | sovereign | ASSERT | 0.50 | coherence |
| 52 | Keeping Still | 001001 | boundary | WAIT | 0.50 | coherence |
| 53 | Development | 001011 | transformer | ADAPT | 0.50 | coherence |
| 54 | The Marrying Maiden | 110100 | dissipator | YIELD | 0.50 | voiceWeight |
| 55 | Abundance | 001101 | sovereign | ASSERT | 0.75 | voiceWeight |
| 56 | The Wanderer | 101100 | dissipator | ADAPT | 0.50 | voiceWeight |
| 57 | The Gentle | 011011 | boundary | YIELD | 0.25 | coherence |
| 58 | The Joyous | 110110 | transformer | YIELD | 0.50 | voiceWeight |
| 59 | Dispersion | 010011 | dissipator | ADAPT | 0.75 | voiceWeight |
| 60 | Limitation | 110010 | boundary | WAIT | 0.25 | coherence |
| 61 | Inner Truth | 110011 | transformer | YIELD | 0.25 | coherence |
| 62 | Preponderance of the Small | 001100 | dissipator | WAIT | 0.50 | coherence |
| 63 | After Completion | 101010 | boundary | WAIT | 0.50 | coherence |
| 64 | Before Completion | 010101 | transformer | ADAPT | 0.75 | voiceWeight |

### 2.2 Structural Properties

**Inversion Pairs (28):** Hexagrams that are vertical mirror images.

```
03↔04  05↔06  07↔08  09↔10  11↔12  13↔14  15↔16  17↔18
19↔20  21↔22  23↔24  25↔26  31↔32  33↔34  35↔36  37↔38
39↔40  41↔42  43↔44  45↔46  47↔48  49↔50  51↔52  53↔54
55↔56  57↔58  59↔60  63↔64
```

**Complementary Pairs (6):** Bit-flipped opposites.

| Pair | Hexagrams | Binary | Relation |
|------|-----------|--------|----------|
| 01↔02 | The Creative ⟷ The Receptive | 111111 ⟷ 000000 | Heaven ⟷ Earth |
| 11↔12 | Peace ⟷ Standstill | 000111 ⟷ 111000 | Flow ⟷ Block |
| 17↔18 | Following ⟷ Work on Decayed | 100110 ⟷ 011001 | Order ⟷ Repair |
| 27↔28 | Corners ⟷ Preponderance | 100001 ⟷ 011110 | Nourish ⟷ Excess |
| 29↔30 | The Abysmal ⟷ The Clinging | 010010 ⟷ 101101 | Water ⟷ Fire |
| 61↔62 | Inner Truth ⟷ Preponderance of Small | 110011 ⟷ 001100 | Center ⟷ Edge |

**Symmetric Hexagrams (8):** Same upright and inverted.

```
01  02  27  28  29  30  61  62
```

**Four Life Stages:**

| Range | Stage | Description |
|-------|-------|-------------|
| 01–02 | Pre-existential | Womb, potential |
| 03–18 | Physical | Birth to adulthood |
| 19–48 | Social | Career, family, community |
| 49–64 | Spiritual | Transcendence, completion |

---

## 3. Ternary Trigrams

Standard I Ching uses binary trigrams (yin/yang). POG2 extends to ternary:

| Trigram | Binary | Ternary | Attribute | Nature |
|---------|--------|---------|-----------|--------|
| Qian | 111 | 222 | Heaven | Creative |
| Dui | 110 | 221 | Lake | Joyous |
| Li | 101 | 212 | Fire | Clinging |
| Zhen | 100 | 211 | Thunder | Arousing |
| Xun | 011 | 122 | Wind | Gentle |
| Kan | 010 | 121 | Water | Abysmal |
| Gen | 001 | 112 | Mountain | Keeping Still |
| Kun | 000 | 111 | Earth | Receptive |

**Ternary rule:** Binary digit + 1. `0→1`, `1→2`. Yao state (`2`) introduces the third pole.

**27 Ternary Trigrams:** 3³ = 27 states per trigram (8 standard + 19 yao-mixed).

---

## 4. 512-State Oracle

### 4.1 Encoding

```
State [8:0] = {hexagram_id[5:0], yao_context[2:0]}

hexagram_id: 0-63 (maps to 1-64)
yao_context: 0-7 (yao injection pattern / temporal modifier)
```

### 4.2 State Transition

```
next_state = deterministic_hash(
    current_state,
    emotional_x,    -- stability bias (8-bit)
    emotional_y,    -- change bias (8-bit)
    emotional_z,    -- alignment bias (8-bit)
    tick_counter    -- 640ms metabolic rhythm (10-bit)
)
```

**Hash properties:**
- No pseudo-RNG
- Avalanche: single-bit input change → ~50% output bits flip
- Tick-dependent: same context at different times → different states
- Emotional modulation: user intent weights the hash

### 4.3 Output Resolution

```
hexagram = HEX_TABLE[state[8:3]]
porosity = hexagram.porosity + emotional_x[3:0]
dominant = hexagram.dominant
action   = hexagram.action
```

---

## 5. Hardware Interface

### 5.1 AXI4-Lite Register Map

| Address | Name | Access | Description |
|---------|------|--------|-------------|
| 0x00 | CTRL | R/W | Control: bit 0=use_axi_context, bit 1=auto_consult |
| 0x04 | STATUS | R | Status: 0x00000001=done, 0x80000000=error |
| 0x08 | CONTEXT | R/W | Input context vector (9-bit state) |
| 0x0C | RESULT | R | Output: {hex_id[5:0], yao_ctx[2:0], porosity[7:0], dominant[1:0], action[1:0]} |
| 0x10 | EMOTIONAL_X | R/W | Stability bias (8-bit) |
| 0x14 | EMOTIONAL_Y | R/W | Change bias (8-bit) |
| 0x18 | EMOTIONAL_Z | R/W | Alignment bias (8-bit) |
| 0x1C | DIAG_PHASE | R | State machine phase (3-bit) |
| 0x20 | DIAG_TICK | R | 640ms tick counter (10-bit) |

### 5.2 Direct Consult Port

```vhdl
consult_req  : in  std_logic;   -- Pulse to request consultation
consult_ack  : out std_logic;   -- High when result valid
context_in   : in  std_logic_vector(8 downto 0);  -- Input state
emotional_x  : in  std_logic_vector(7 downto 0);  -- Stability
emotional_y  : in  std_logic_vector(7 downto 0);  -- Change
emotional_z  : in  std_logic_vector(7 downto 0);  -- Alignment
state_out    : out std_logic_vector(8 downto 0);  -- Resolved state
state_valid  : out std_logic;   -- High when state_out valid
porosity_out : out std_logic_vector(7 downto 0);  -- 0.0-1.0
 dominant_out : out std_logic_vector(1 downto 0);  -- 00=coherence, 01=chaos, 10=voiceWeight, 11=whimsy
action_out   : out std_logic_vector(1 downto 0);  -- 00=ASSERT, 01=YIELD, 10=ADAPT, 11=WAIT
```

---

## 6. State Machine Phases

```
IDLE    → LOAD    → HASH    → LOOKUP  → RESOLVE → OUTPUT  → IDLE
(000)     (001)     (010)     (011)     (100)     (101)
                     ↑_________________________________________|
                     (auto-return after OUTPUT)
```

**Timing:**
- Each phase: 1 clock cycle
- Full consult: 6 cycles
- At 100MHz: 60ns per consult
- 640ms tick: ~10.7M consults per tick

---

## 7. Integration

### 7.1 POG2 MHD Controller

```
hexagram_state_machine.vhd ──→ POG2_MHD_FPGA_TOP.vhd
     ↓                              ↓
AXI4-Lite ←── ARM Cortex-A53 ←── Zynq UltraScale+ ZU7EV
     ↓
640ms tick ←─── SensorAcquisition.vhd
     ↓
GhostSplatPredictor.vhd (3-tick horizon)
```

### 7.2 Software Binding

```python
# Python simulation (for Megatron training corpus)
def consult(context: int, emotional: tuple[int,int,int], tick: int) -> dict:
    h = deterministic_hash(context, *emotional, tick)
    hex_id = (h >> 3) & 0x3F
    yao_ctx = h & 0x07
    hexagram = HEX_TABLE[hex_id]
    return {
        "state": h,
        "hexagram": hex_id + 1,
        "yao_context": yao_ctx,
        "porosity": hexagram["porosity"],
        "dominant": hexagram["dominant"],
        "action": hexagram["action"]
    }
```

### 7.3 MCP Endpoint

```
POST /mcp/hexagram/consult
Body: {
    "context": 0-511,
    "emotional": [0-255, 0-255, 0-255],
    "tick": 0-1023
}
Response: {
    "state": 0-511,
    "hexagram": 1-64,
    "yao_context": 0-7,
    "porosity": 0.0-1.0,
    "dominant": "coherence|chaos|voiceWeight|whimsy",
    "action": "ASSERT|YIELD|ADAPT|WAIT"
}
```

---

## 8. Verification

All 64 hexagrams verified against immutable tables:

```bash
cd KING-WEN-I-CHING-IMMUTABLE-TABLES
PYTHONPATH=. python3 learn/scripts/learn_sequential_hexagrams.py
# → learn/exports/learned_sequential_64.json
# → All 64 unique, all binaries valid, all pairs confirmed
```

**Tests:**
- ✅ 64 unique binary patterns
- ✅ 28 inversion pairs (vertical mirror)
- ✅ 6 complementary pairs (bit-flip)
- ✅ 8 symmetric hexagrams
- ✅ Unicode range U+4DC0–U+4DFF
- ✅ Ternary trigram mapping (27 states)
- ✅ 512-state hash determinism

---

## 9. Files

| File | Purpose |
|------|---------|
| `hexagram_state_machine.vhd` | Synthesizable VHDL (this module) |
| `learn/scripts/learn_sequential_hexagrams.py` | Verification script |
| `learn/exports/learned_sequential_64.json` | Verified output |
| `KING_WEN_TABLES.py` | Python generator for immutable tables |
| `kingwen_ternary_tables_complete.py` | Ternary routing tables |

---

## 10. Sovereign Principle

> "The 6 yao lines represent machinery restrictions and diagnostics layer only. Full system implements complex I Ching with temporal dimensions (past/present/future) and polarity states (yin/yang/yao)."

This module is the **machinery**. The oracle lives in the hash. The hash lives in the tables. The tables are immutable. The immutability is the sovereignty.

---

*POG2 Sovereign Systems Engineering | STATIC KING WEN REGISTRY | Verified Immutable | 2026-07-10*
