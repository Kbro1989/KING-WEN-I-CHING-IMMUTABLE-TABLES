# King Wen 64 Sovereign Model Engine — Cloudflare Pages & Workers Guide

**Engine Version**: `v3.2.0`  
**Deployment Target**: Cloudflare Pages + Pages Functions (Edge Workers)  
**Configuration File**: [`wrangler.toml`](../wrangler.toml)  
**Output Directory**: [`public/`](../public/)  

---

## 1. Cloudflare Architecture Overview

The King Wen 64 Sovereign Model Engine is packaged for zero-cold-start deployment on **Cloudflare Pages & Edge Workers**.

```
                           +----------------------------------------+
                           |     Cloudflare Edge Global CDN        |
                           +----------------------------------------+
                                        |                |
                     +------------------+                +------------------+
                     |                                                      |
         [Static Asset Routes]                                   [Edge Worker Routes]
       public/index.html (3D Viewfinder)                       functions/api/world.js
       public/DATASETS/topology.json                           functions/api/hexagram/[id].js
       public/DATASETS/manifest.json                          functions/api/jkd/[id].js
                                                               functions/api/kingwen-link.js
                                                               functions/widget/[id].js
```

---

## 2. API Endpoints Reference

| Endpoint | Method | Description | Cache Policy |
|---|---|---|---|
| `GET /` | GET | Serves the interactive 3D Sovereign World Viewfinder | CDN Cache |
| `GET /api/world` | GET | Serves full 64-sector topology, 60 pre-warmed 3D egg keyframes, pre-rendered audio PCM WAV buffer | `s-maxage=86400` |
| `GET /api/hexagram/:id` | GET | Serves hexagram `$1 \dots 64$` metadata, 9-bit VHDL resolver address, and 6-yao sound pellet frequencies | `s-maxage=86400` |
| `GET /api/jkd/:id` | GET | Serves JKD Megatron wavepacket text passages, 5-axis emotion vectors, and Hamiltonian energy | `s-maxage=86400` |
| `GET /api/kingwen-link` | GET/POST | King Wen Link peer-to-peer acoustic wavepacket protocol exchange | Edge Dynamic |
| `GET /widget/:id` | GET | Serves standalone hexagram HTML widgets (`:id` = `$1 \dots 64$`, `all`, or `512`) | `max-age=3600` |

---

## 3. How to Build & Deploy

### A. Pre-Bake Pipeline & Package Bundle
```bash
python scripts/build_cloudflare_dist.py
```

### B. Local Development & Testing (Wrangler CLI)
```bash
npx wrangler pages dev public
```
*Navigates to `http://localhost:8788` to test 3D world viewer and Edge API routes locally.*

### C. Production Deployment
```bash
npx wrangler pages deploy public --project-name=kingwen-sovereign-engine
```

---

## 4. King Wen Link Acoustic Peer Handshake Example

To initiate a machine-to-machine King Wen Link acoustic wavepacket handshake via Cloudflare Edge Workers:

```bash
curl -X POST https://kingwen-sovereign-engine.pages.dev/api/kingwen-link \
  -H "Content-Type: application/json" \
  -d '{"hexagram_id": 1, "phase_id": 1}'  # example: hexagram 1 of 64
```

**Response**:
```json
{
  "protocol": "King Wen Link Acoustic Peer-to-Peer Protocol v1.0",
  "hexagram_id": 1,
  "phase_id": 1,
  "vhdl_resolved_address_9bit": 1,
  "hexagram_name": "Creative",
  "binary_pattern": "111111",
  "acoustic_carriers": {
    "yao_line_frequencies_hz": [108.0, 118.9, 130.9, 144.1, 158.6, 174.6],
    "wavepacket_signature": "1:1:108.0|2:1:118.9|3:1:130.9|4:1:144.1|5:1:158.6|6:1:174.6",
    "fundamental_freq_hz": 108.0,
    "vortex_tension": 0.0
  },
  "peer_handshake": {
    "status": "SYNCHRONIZED",
    "consensus_mode": "UNBOUND_SUPERPOSITION"
  }
}
```
