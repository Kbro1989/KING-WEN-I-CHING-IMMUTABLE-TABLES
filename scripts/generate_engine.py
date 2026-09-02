#!/usr/bin/env python3
"""Runnable entry point: generate TS engine sources and package metadata."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    (output_dir / sub).mkdir(parents=True, exist_ok=True)

oracle_engine = '''import {
  OracleConfig, OracleQuery, OracleResponse, HexagramState,
  TemporalState, EmotionalVector, UserContext
} from '../types/oracle.js';
import { EmotionalParser } from '../parser/EmotionalParser.js';
import { NarrativeEngine } from '../parser/NarrativeEngine.js';
import { computeTemporalPhase, phaseToString } from '../utils/TemporalMath.js';
import { deterministicHexagramSelect } from '../utils/DeterministicHash.js';

import registryJson from '../../data/hexagram-registry.json' assert { type: 'json' };
import weightsJson from '../../data/emotional-weights.json' assert { type: 'json' };
import reflectionsJson from '../../data/temporal-reflections.json' assert { type: 'json' };

// =============================================================================
// OracleEngine — TRANSPARENT RELAY to Python expand server.
//
// Laws enforced:
//   - NO 1-hex collapse. Consensus comes from Python _compute_consensus_from_resolved()
//     across ALL 512 resolved states (64 hexagrams × 8 phases). Never collapse early.
//   - NO pseudo-RNG, no Math.random(), no deterministicHexagramSelect roll.
//     The Python Hamiltonian + Gaussian accumulator selects the consensus hexagram.
//   - NO template-generated text for sovereign_assertion / boundary_condition /
//     dissipator_warning / unified_weave. These are Python-computed corpus lookups.
//   - expanded_state and resolved_state are relayed intact. Never strip.
// =============================================================================

export class LocalOracleClient {
  url: string;

  constructor(options: { url?: string } = {}) {
    this.url = options.url || 'http://127.0.0.1:8765/expand';
  }

  async consult(query: OracleQuery): Promise<OracleResponse> {
    const body = {
      emotional_input: query.emotional_input ?? 50,
      session_id: query.session_id || 'anon',
      text: query.text || '',
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60_000);

    let response: Response;
    try {
      response = await fetch(this.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (error) {
      throw new Error(`Oracle engine unreachable at ${this.url}: ${error}`);
    } finally {
      clearTimeout(timeout);
    }

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Oracle engine error ${response.status}: ${text}`);
    }

    const payload: unknown = await response.json();
    return mapExpandResponse(payload, query);
  }

  loadRegistry(): void { /* no-op: owned by Python engine */ }
  loadReflections(): void { /* no-op: owned by Python engine */ }
}

export class OracleEngine {
  client: LocalOracleClient;

  constructor(config: { localUrl?: string } = {}) {
    this.client = new LocalOracleClient({ url: config.localUrl });
  }

  loadRegistry(): void { this.client.loadRegistry(); }
  loadReflections(): void { this.client.loadReflections(); }

  async consult(query: OracleQuery = { text: '', session_id: 'anon' }): Promise<OracleResponse> {
    return this.client.consult(query);
  }
}

// =============================================================================
// mapExpandResponse — transparent relay.
// Python runs shotgun_expand(): 64 hexagrams × 8 phases = 512 resolved states
// with Hamiltonian energy, Gaussian accumulator, and open-pool vector blending.
// This function RELAYS. It does not fabricate, template-concatenate, or collapse.
// =============================================================================

function mapExpandResponse(rawPayload: unknown, query: OracleQuery): OracleResponse {
  if (typeof rawPayload !== 'object' || rawPayload === null) {
    throw new Error('Oracle: invalid expand response — payload must be an object');
  }
  const payload = rawPayload as Record<string, unknown>;

  if (!Array.isArray(payload.resolved)) {
    throw new Error('Oracle: missing resolved[] — engine must return full 512-state expansion');
  }
  if (payload.resolved.length === 0) {
    throw new Error('Oracle: expand server returned 0 resolved states — engine fault');
  }
  if (!payload.consensus || typeof payload.consensus !== 'object') {
    throw new Error('Oracle: missing consensus block — cannot relay without computed field');
  }

  const consensus = payload.consensus as Record<string, unknown>;

  const hexagram_id = Number(consensus.consensus_hexagram_id);
  if (!Number.isFinite(hexagram_id) || hexagram_id < 1 || hexagram_id > 64) {
    throw new Error(`Oracle: consensus_hexagram_id=${hexagram_id} out of range [1,64]`);
  }

  const hexagram_name   = String(consensus.consensus_hexagram_name ?? '');
  const temporal_phase  = String(consensus.consensus_temporal ?? 'present');
  const consensus_yao   = String(consensus.consensus_yao ?? 'stable_yao');
  const consensus_vec   = (consensus.consensus_vector ?? {}) as Record<string, number>;
  const consensus_intent = String(consensus.consensus_intent ?? '');

  const resolved = payload.resolved as Record<string, unknown>[];
  const representative = resolved.find(
    (e) => Number(e.hexagram_id) === hexagram_id && e.phase_temporal === temporal_phase,
  ) ?? resolved.find((e) => Number(e.hexagram_id) === hexagram_id) ?? resolved[0];

  const symbols    = (representative.hexagram_symbols ?? {}) as Record<string, unknown>;
  const hexUnicode = String(symbols.unicode ?? '');

  const rawAction = String(symbols.action ?? 'WAIT').toUpperCase();
  const action = (['ASSERT', 'YIELD', 'ADAPT', 'WAIT'] as const).includes(rawAction as 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT')
    ? rawAction as 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT'
    : 'WAIT';

  const rawCat   = String(symbols.category ?? 'transformer').toLowerCase();
  const category = (['sovereign', 'boundary', 'transformer', 'dissipator'] as const).includes(rawCat as 'sovereign' | 'boundary' | 'transformer' | 'dissipator')
    ? rawCat as 'sovereign' | 'boundary' | 'transformer' | 'dissipator'
    : 'transformer';

  // Reflections: corpus lookup by hexagram_id — no fortune-cookie fallbacks.
  let corpusEntry: { past: string; present: string; future: string } | undefined;
  try {
    const { readFileSync } = require('fs');
    const { resolve, dirname } = require('path');
    const corpusPath = resolve(dirname(require.resolve('../types/oracle.js')), '../../data/temporal-reflections.json');
    const corpus = JSON.parse(readFileSync(corpusPath, 'utf-8')) as Record<string, { past: string; present: string; future: string }>;
    corpusEntry = corpus[String(hexagram_id)];
  } catch { /* corpus unavailable — surface error below */ }

  if (!corpusEntry || !corpusEntry.past || !corpusEntry.present || !corpusEntry.future) {
    throw new Error(`Oracle: no corpus entry for hexagram_id=${hexagram_id} in data/temporal-reflections.json`);
  }

  const phaseToCorpus: Record<string, string> = {
    past: corpusEntry.past, present: corpusEntry.present, future: corpusEntry.future,
    transition: corpusEntry.present, resolution: corpusEntry.past,
    dissolution: corpusEntry.future, crystallization: corpusEntry.present, void: corpusEntry.present,
  };

  const emotional_deltas = {
    chaos:       Number(consensus_vec.chaos       ?? 0),
    whimsy:      Number(consensus_vec.whimsy      ?? 0),
    darkTone:    Number(consensus_vec.darkTone     ?? 0),
    coherence:   Number(consensus_vec.coherence   ?? 0),
    voiceWeight: Number(consensus_vec.voiceWeight ?? 0),
  };

  return {
    hexagram_id,
    hexagram_name,
    hexagram_unicode: hexUnicode,
    temporal_phase: ({ past: 0, present: 1, future: 2 } as Record<string, number>)[temporal_phase] as 0 | 1 | 2 ?? 1,
    temporal_substate: (consensus_yao.includes('old') ? 'old' : consensus_yao.includes('young') ? 'young' : 'transition') as 'old' | 'young' | 'transition',
    past_reflection:    corpusEntry.past,
    present_reflection: corpusEntry.present,
    future_reflection:  corpusEntry.future,
    unified_weave: phaseToCorpus[temporal_phase] ?? corpusEntry.present,
    sovereign_assertion: String(representative.sovereign_assertion ?? consensus_intent),
    boundary_condition:  String(representative.boundary_condition  ?? ''),
    dissipator_warning:  String(representative.dissipator_warning  ?? ''),
    action,
    category,
    emotional_deltas,
    state_str: query.state_str,
    // Full expansion relay — intact, never stripped.
    expanded_state:    Array.isArray(payload.expanded) ? payload.expanded : [],
    resolved_state:    payload.resolved,
    runtime_consensus: consensus,
    runtime_source:    String(payload.source ?? 'local-python'),
  };
}
'''

pkg = {
    "name": "oracle-emotional-state-machine",
    "version": "1.0.0",
    "description": "Standalone King Wen I Ching emotional parser with 64 hexagrams, 3 temporal phases, 5 emotional dimensions",
    "type": "module",
    "main": "dist/core/OracleEngine.js",
    "types": "dist/types/oracle.d.ts",
    "scripts": {
        "build": "tsc",
        "test": "node --test dist/tests/*.js",
        "demo": "node scripts/demo.js",
        "verify": "python scripts/verify_registry.py && python scripts/run_all.py && npm test"
    },
    "dependencies": {},
    "devDependencies": {
        "typescript": "^5.3.0"
    }
}

tsconfig = {
    "compilerOptions": {
        "target": "ES2022",
        "module": "NodeNext",
        "moduleResolution": "NodeNext",
        "outDir": "./dist",
        "rootDir": "./src",
        "strict": True,
        "esModuleInterop": True,
        "skipLibCheck": True,
        "forceConsistentCasingInFileNames": True,
        "resolveJsonModule": True
    },
    "include": ["src/**/*", "data/**/*"]
}

(output_dir / "src/core/OracleEngine.ts").write_text(oracle_engine, encoding="utf-8")
(output_dir / "package.json").write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")
(output_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2) + "\n", encoding="utf-8")

print("✅ src/core/OracleEngine.ts")
print("✅ package.json")
print("✅ tsconfig.json")
