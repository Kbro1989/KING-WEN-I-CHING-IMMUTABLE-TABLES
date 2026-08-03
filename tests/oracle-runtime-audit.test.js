import test from 'node:test';
import assert from 'node:assert/strict';
import { OracleEngine } from '../src/core/OracleEngine.js';

test('consult surfaces expanded runtime state for enhanced control without gating', async () => {
  const originalFetch = global.fetch;
  const runtimePayload = {
    source: 'local-python',
    expanded_count: 2,
    resolved_count: 2,
    expanded: [{ hexagram_id: 1, expanded_vector: { chaos: 0.1 } }],
    resolved: [{ hexagram_id: 1, phase_bits: 0, resolved_vector: { chaos: 0.2 } }],
    consensus: { score: 0.75 },
  };

  global.fetch = async () => ({
    ok: true,
    json: async () => runtimePayload,
  });

  try {
    const engine = new OracleEngine({ deterministic: true });
    const response = await engine.consult({
      text: 'audit expanded runtime',
      session_id: 'runtime-audit',
      emotional_input: 60,
    });

    assert.deepStrictEqual(response.expanded_state, runtimePayload.expanded);
    assert.deepStrictEqual(response.resolved_state, runtimePayload.resolved);
    assert.deepStrictEqual(response.runtime_consensus, runtimePayload.consensus);
    assert.equal(response.runtime_source, 'local-python');
  } finally {
    global.fetch = originalFetch;
  }
});
