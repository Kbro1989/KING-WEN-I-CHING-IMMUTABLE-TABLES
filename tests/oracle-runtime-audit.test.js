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

test('computeTokenSum matches deterministic ASCII character summation', async () => {
  const { computeTokenSum } = await import('../dist/utils/DeterministicHash.js');
  const tokens = ['create', 'transform'];
  const sum = computeTokenSum(tokens);
  // 'create' = 99+114+101+97+116+101 = 628
  // 'transform' = 116+114+97+110+115+102+111+114+109 = 988
  // Total = 1616
  assert.equal(sum, 1616);
});

test('extractCoprimePrimeVector applies (97, 89, 83, 79, 73) coprime moduli', async () => {
  const { extractCoprimePrimeVector } = await import('../dist/utils/DeterministicHash.js');
  const hashVal = 1608;
  const primeVec = extractCoprimePrimeVector(hashVal);

  const expectedChaos = ((1608 % 97) / 97.0) * 0.12;
  const expectedWhimsy = ((Math.floor(1608 / 7) % 89) / 89.0) * 0.12;
  const expectedDark = ((Math.floor(1608 / 13) % 83) / 83.0) * 0.12;
  const expectedCoh = ((Math.floor(1608 / 19) % 79) / 79.0) * 0.12;
  const expectedVw = ((Math.floor(1608 / 23) % 73) / 73.0) * 0.12;

  assert.ok(Math.abs(primeVec.chaos - expectedChaos) < 1e-9);
  assert.ok(Math.abs(primeVec.whimsy - expectedWhimsy) < 1e-9);
  assert.ok(Math.abs(primeVec.darkTone - expectedDark) < 1e-9);
  assert.ok(Math.abs(primeVec.coherence - expectedCoh) < 1e-9);
  assert.ok(Math.abs(primeVec.voiceWeight - expectedVw) < 1e-9);
});

test('EmotionalParser extracts intent and applies prime hash without flat default fallback', async () => {
  const { EmotionalParser } = await import('../dist/parser/EmotionalParser.js');
  const parser = new EmotionalParser();
  const vector = parser.parse({
    text: 'create and transform the sovereign architecture',
    session_id: 'test-session',
  });

  assert.notEqual(vector.chaos, 0.5);
  assert.notEqual(vector.coherence, 0.5);
  assert.ok(vector.chaos >= 0 && vector.chaos <= 1);
  assert.ok(vector.coherence >= 0 && vector.coherence <= 1);
});

test('computeTemporalPhase supports all 8 King Wen temporal phases without RNG', async () => {
  const { computeTemporalPhase, PHASE_NAMES } = await import('../dist/utils/TemporalMath.js');
  assert.equal(PHASE_NAMES.length, 8);
  for (let tick = 0; tick < 16; tick++) {
    const state = computeTemporalPhase(tick, 50);
    assert.equal(state.phase8, tick % 8);
    assert.equal(state.phaseName, PHASE_NAMES[tick % 8]);
    assert.equal(typeof state.dominantPhase, 'number');
    assert.equal(typeof state.substate, 'string');
  }
});
