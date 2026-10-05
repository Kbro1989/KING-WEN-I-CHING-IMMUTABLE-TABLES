#!/usr/bin/env python3
"""Runnable entry point: generate tests and index exports."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "src/tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

test_file = '''import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { OracleEngine } from '../core/OracleEngine.js';

// OracleEngine is a TRANSPARENT RELAY to the local Python expand server.
// It owns no selection logic, so the only correct way to test it is to stub
// fetch and assert the relay preserves the full 64-expanded / 512-resolved
// payload without collapsing to a single hexagram.
// The consensus block must carry the engine's real field names, otherwise the
// relay's own validation (consensus_hexagram_id in [1,64]) rejects it.
const resolvedStates = Array.from({ length: 512 }, (_, i) => ({
  hexagram_id: (i % 64) + 1,
  phase_bits: i % 8,
  phase_temporal: ['past', 'present', 'future'][i % 3],
  hexagram_symbols: { unicode: '\\u4dc0', action: 'ASSERT', category: 'sovereign' },
}));

const relayPayload = {
  source: 'local-python',
  expanded_count: 64,
  resolved_count: 512,
  expanded: Array.from({ length: 64 }, (_, i) => ({ hexagram_id: i + 1 })),
  resolved: resolvedStates,
  consensus: {
    consensus_hexagram_id: 1,
    consensus_hexagram_name: 'The Creative',
    consensus_temporal: 'present',
    consensus_yao: 'stable_yao',
    consensus_vector: {},
    consensus_intent: '',
  },
};

describe('OracleEngine', () => {
  const realFetch = globalThis.fetch;
  let engine: OracleEngine;

  beforeEach(() => {
    globalThis.fetch = (async () => ({ ok: true, json: async () => relayPayload })) as unknown as typeof fetch;
    engine = new OracleEngine({ localUrl: 'http://127.0.0.1:8765' });
  });

  afterEach(() => {
    globalThis.fetch = realFetch;
  });

  it('should relay a consult and keep the full expansion intact', async () => {
    const response = await engine.consult({
      text: 'What should I do about this obstacle?',
      session_id: 'test-session-001',
      emotional_input: 50,
    });

    assert.ok(response);
    assert.strictEqual(response.runtime_source, 'local-python');
    assert.strictEqual(response.expanded_state?.length, 64);
    assert.strictEqual(response.resolved_state?.length, 512);
  });

  it('should never collapse the 512-state superposition to one hexagram', async () => {
    const response = await engine.consult({ text: 'test', session_id: 'sess-a', emotional_input: 30 });

    assert.notStrictEqual(response.expanded_state?.length, 1);
    assert.notStrictEqual(response.resolved_state?.length, 1);
    assert.strictEqual(response.resolved_state?.length, 512);
  });
});
'''

index_ts = '''export { OracleEngine } from './core/OracleEngine.js';
export { EmotionalParser } from './parser/EmotionalParser.js';
export { NarrativeEngine } from './parser/NarrativeEngine.js';
export { computeTemporalPhase, phaseToString } from './utils/TemporalMath.js';
export {
  deterministicHash,
  deterministicHashHex,
  computeTokenSum,
  extractCoprimePrimeVector,
  generateDeterministicInjectHash,
} from './utils/DeterministicHash.js';
export { HexagramRuntimeBridge } from './core/HexagramRuntimeBridge.js';
export * from './types/IntentVector.js';
export * from './types/StateCapture.js';
export * from './types/oracle.js';
'''

with open(os.path.join(output_dir, "src/tests/oracle.test.ts"), "w", encoding="utf-8") as f:
    f.write(test_file)
with open(os.path.join(output_dir, "src/index.ts"), "w", encoding="utf-8") as f:
    f.write(index_ts)

print("✅ tests/oracle.test.ts")
print("✅ src/index.ts")
