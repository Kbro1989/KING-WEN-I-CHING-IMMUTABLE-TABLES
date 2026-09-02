# SKILL: King Wen 512-State J-Space Widget (POG3)

## Overview

Self-contained HTML widget for navigating the King Wen 512-state deterministic oracle within the POG3 cognitive ecosystem. Renders all 64 hexagrams × 8 phase bits with Hamiltonian energy computation, J-space broadcast selection, Gaussian kernel smoothing, and phase-accurate state export.

**No build step. No dependencies. Single file.**

Part of the POG3 unified substrate: Jarvis OS + King Wen 512-state oracle + Megatron-LM.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  KingWen DATA (embedded JSON: 64 expanded + 512 resolved)   │
├─────────────────────────────────────────────────────────────┤
│  Hamiltonian Engine  │  Broadcast Selector  │  Gaussian     │
│  ℋ(p,q,t) per state  │  Top-K by energy     │  Kernel       │
├─────────────────────────────────────────────────────────────┤
│  Grid View (512 cells)        │  Detail Panel (telemetry)   │
│  · Unicode glyph              │  · Hamiltonian energy       │
│  · Phase label                │  · Resolved vector bars     │
│  · Energy score               │  · Yao line visualization   │
│  · Broadcast star             │  · Phase timeline navigator │
│  · Selection highlight        │  · Diagnostic checklist     │
│                               │  · Phase-accurate export    │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  POG3 Integration Points                                    │
│  · Jarvis OS hands-free agentic substrate                   │
│  · King Wen 512-state oracle (deterministic hash)           │
│  · Megatron-LM distributed model serving                    │
│  · GhostSplat prediction layer                              │
│  · HexagramNetworkBridge BETA protocol                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Hamiltonian Energy Formula

```
ℋ(p,q,t) = coherence - chaos - 0.5×darkTone + 0.3×voiceWeight - 0.2×whimsy
```

> **display_approximation** — This is a visualization heuristic, not the engine's exact computation.
> The engine (`emotional_engine.py:_hamiltonian_energy`) computes:
>   `momentum = max(0, resolved_vector)`; `lagrangian = |yin_ratio-yang_ratio|×0.5 + yao_ratio×0.3 + changing_ratio×0.2`;
>   `ℋ = Σ(momentum_i × |phase_shift_i|) - lagrangian`, clamped to [0,1].
> The widget formula omits phase_shift and line_balance for offline rendering.
> Values will differ from engine output; use for relative ranking only.

**Baseline** = average ℋ across all 512 resolved states (computed at init, not hardcoded).

**Broadcast selection** = Top-K states by ℋ energy (default K=16).

---

## Data Structure

The widget embeds the full `kingwen-512-full.json` corpus with two arrays:

| Array | Count | Content |
|-------|-------|---------|
| `expanded` | 64 | Base hexagram definitions (phase_bits=0) |
| `resolved` | 512 | All 64 hexagrams × 8 phase bits (0-7) |

Each resolved entry contains:
- `hexagram_id` (1-64)
- `phase_bits` (0-7): past, present, future, transition, resolution, dissolution, crystallization, void
- `phase_temporal`, `phase_polarity`, `phase_description`
- `resolved_vector`: {chaos, whimsy, darkTone, coherence, voiceWeight}
- `line_states`: 6 yao lines with position + yao_key
- `checklist`: 8 diagnostic axes with status
- `primary_pool`, `secondary_pool`, `porosity`

---

## Controls

| Control | Function |
|---------|----------|
| **J-Space Broadcast** toggle | Highlight Top-K Hamiltonian states (★) |
| **Gaussian Smooth** toggle | Apply kernel smoothing to resolved vectors (`display_approximation`: index-distance sliding window, not engine's scalar measurement-space kernel) |
| **Grid/List** buttons | Switch cell layout density |
| **Hexagram cell click** | Select state, render detail panel |
| **Phase timeline dot** | Navigate between phases of same hexagram |
| **Export State** button | Download phase-accurate JSON |

---

## Phase Bits Mapping

| Bits | Temporal | Polarity | Description |
|------|----------|----------|-------------|
| 0 | past | yin | completed, resolved, memory |
| 1 | present | yang | active, manifest, now |
| 2 | future | yao | potential, emerging, becoming |
| 3 | transition | yin-yang | changing, flux, threshold |
| 4 | resolution | yang-yin | settling, clarity, convergence |
| 5 | dissolution | yin-yao | breaking, releasing, dispersal |
| 6 | crystallization | yang-yao | forming, condensing, structure |
| 7 | void | yao-yao | null, reset, origin |

---

## Color Scheme

| Element | Color | Meaning |
|---------|-------|---------|
| Sovereign | `#c9a84c` gold | ASSERT action, genesis spark |
| Transformer | `#4ec9a8` teal | YIELD/ADAPT action |
| Dissipator | `#c94e6e` rose | WAIT/ADAPT, high chaos |
| Boundary | `#6e9ec9` blue | WAIT action, meditative |
| Broadcast | `#4ec9a8` star | Top-K Hamiltonian selection |
| Selected | `#c9a84c` border | Active detail view |
| Hamiltonian + | `#4ec9a8` | Above baseline |
| Hamiltonian − | `#c94e6e` | Below baseline |

---

## POG3 Integration

### As Standalone HTML
```bash
# Open directly in browser
open kingwen-jspace-widget.html

# Or serve via any static server
python -m http.server 8080
# Navigate to http://localhost:8080/kingwen-jspace-widget.html
```

### Embedded in POG3 Dashboard (Jarvis OS)
```typescript
// Load widget into Jarvis OS viewport
const container = document.getElementById('jarvis-oracle-viewport');
fetch('/widgets/kingwen-jspace-widget.html')
  .then(r => r.text())
  .then(html => container.innerHTML = html);

// Bridge to Megatron-LM for model selection
// Bridge to GhostSplat for prediction overlay
// Bridge to HexagramNetworkBridge for BETA protocol telemetry
```

### Hermes CLI Deployment
```bash
# Hermes fans out widget to all 61 repos
hermes deploy --widget kingwen-jspace-widget.html --target pog3-dashboard

# Updates jarvisupgradepoints.md with widget version
hermes log --skill kingwen-jspace --version 1.0.0 --status deployed
```

### Data Refresh
The widget embeds data statically. To refresh with new resolved states:
1. Regenerate `kingwen-512-full.json` via `shotgun_expand()`
2. Re-run the widget generator (Python script replaces `KINGWEN_DATA` constant)
3. No runtime API calls — deterministic, offline-capable, Ghost Limb ready

---

## Export Format

Phase-accurate JSON export includes:
```json
{
  "hexagram_id": 1,
  "phase_bits": 3,
  "phase_temporal": "transition",
  "phase_polarity": "yin-yang",
  "name": "The Creative",
  "unicode": "\u4dc0",
  "binary": "111111",
  "hamiltonian_energy": 0.8234,
  "hamiltonian_delta": 0.1456,
  "resolved_vector": { "chaos": 0.0937, "whimsy": 0.1812, ... },
  "line_states": [...],
  "primary_pool": "genesis_spark",
  "secondary_pool": "void_origin",
  "porosity": 1,
  "timestamp": "2026-07-23T20:52:00.000Z"
}
```

---

## Performance

| Metric | Value |
|--------|-------|
| File size | ~1.7 MB (embedded data) |
| Render time | <100ms for 512 cells |
| Memory | ~8 MB heap |
| Dependencies | None |
| Browser | Any modern browser (ES6+) |

---

## Determinism Guarantee

No `Math.random()`. No pseudo-RNG. All state:
- Hamiltonian energies computed from resolved vectors
- Broadcast set selected by sort (deterministic)
- Gaussian smoothing uses fixed bandwidth (σ=1.5)
- Phase transitions are index lookups

The only non-deterministic element is the export timestamp.

---

## POG3 System Context

| Component | Role |
|-----------|------|
| Jarvis OS | Hands-free agentic substrate — widget runs as viewport module |
| King Wen 512 | Deterministic hash oracle — 2^9 states, no pseudo-RNG |
| Megatron-LM | Distributed model serving — widget feeds state vectors to model selection |
| GhostSplat | Prediction layer — Hamiltonian energy informs volition commit |
| HexagramNetworkBridge | BETA protocol — broadcast states emit telemetry |
| ModelRolodex | 7-provider selection — widget state drives capability resolution |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-23 | POG3 release. Hamiltonian energy, broadcast overlay, Gaussian smooth, phase export. Hermes-deployed. |

---

## Source of Truth

- Canonical data: `kingwen-512-full.json` (64 expanded + 512 resolved)
- Hamiltonian baseline: computed at runtime from all 512 states
- Broadcast K: configurable (default 16)
- Gaussian bandwidth: 1.5 (configurable)
- POG3 ecosystem: Jarvis OS + King Wen + Megatron-LM
