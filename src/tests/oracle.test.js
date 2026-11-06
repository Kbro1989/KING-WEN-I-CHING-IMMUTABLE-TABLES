 function _optionalChain(ops) { let lastAccessLHS = undefined; let value = ops[0]; let i = 1; while (i < ops.length) { const op = ops[i]; const fn = ops[i + 1]; i += 2; if ((op === 'optionalAccess' || op === 'optionalCall') && value == null) { return undefined; } if (op === 'access' || op === 'optionalAccess') { lastAccessLHS = value; value = fn(value); } else if (op === 'call' || op === 'optionalCall') { value = fn((...args) => value.call(lastAccessLHS, ...args)); lastAccessLHS = undefined; } } return value; }import { describe, it, beforeEach, afterEach } from 'node:test';
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
  hexagram_symbols: { unicode: '\u4dc0', action: 'ASSERT', category: 'sovereign' },
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
  let engine;

  beforeEach(() => {
    globalThis.fetch = (async () => ({ ok: true, json: async () => relayPayload })) ;
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
    assert.strictEqual(_optionalChain([response, 'access', _2 => _2.expanded_state, 'optionalAccess', _3 => _3.length]), 64);
    assert.strictEqual(_optionalChain([response, 'access', _4 => _4.resolved_state, 'optionalAccess', _5 => _5.length]), 512);
  });

  it('should never collapse the 512-state superposition to one hexagram', async () => {
    const response = await engine.consult({ text: 'test', session_id: 'sess-a', emotional_input: 30 });

    assert.notStrictEqual(_optionalChain([response, 'access', _6 => _6.expanded_state, 'optionalAccess', _7 => _7.length]), 1);
    assert.notStrictEqual(_optionalChain([response, 'access', _8 => _8.resolved_state, 'optionalAccess', _9 => _9.length]), 1);
    assert.strictEqual(_optionalChain([response, 'access', _10 => _10.resolved_state, 'optionalAccess', _11 => _11.length]), 512);
  });
});
