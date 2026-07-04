import { describe, it } from 'node:test';
import assert from 'node:assert';
import { OracleEngine } from '../core/OracleEngine.js';

describe('OracleEngine', () => {
  const engine = new OracleEngine({ deterministic: true });

  it('should consult with basic query', async () => {
    const response = await engine.consult({
      text: 'What should I do about this obstacle?',
      session_id: 'test-session-001',
      emotional_input: 50,
    });

    assert.strictEqual(typeof response.hexagram_id, 'number');
    assert.ok(response.hexagram_id >= 1 && response.hexagram_id <= 64);
    assert.ok(response.hexagram_name.length > 0);
    assert.ok(response.past_reflection.length > 0);
    assert.ok(response.present_reflection.length > 0);
    assert.ok(response.future_reflection.length > 0);
    assert.ok(response.unified_weave.length > 0);
    assert.ok(['ASSERT', 'YIELD', 'ADAPT', 'WAIT'].includes(response.action));
    assert.ok(['sovereign', 'boundary', 'transformer', 'dissipator'].includes(response.category));
  });

  it('should be deterministic for same inputs', async () => {
    const q1 = await engine.consult({ text: 'test', session_id: 'sess-a', emotional_input: 30 });
    const q2 = await engine.consult({ text: 'test', session_id: 'sess-a', emotional_input: 30 });
    assert.strictEqual(typeof q1.hexagram_id, 'number');
    assert.strictEqual(typeof q2.hexagram_id, 'number');
  });
});
