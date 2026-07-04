#!/usr/bin/env python3
"""Runnable entry point: generate tests and index exports."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

test_file = '''import { describe, it } from 'node:test';
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
'''

index_ts = '''export { OracleEngine } from './core/OracleEngine.js';
export { EmotionalParser } from './parser/EmotionalParser.js';
export { NarrativeEngine } from './parser/NarrativeEngine.js';
export { computeTemporalPhase, phaseToString } from './utils/TemporalMath.js';
export { deterministicHash, deterministicIndex, deterministicHexagramSelect } from './utils/DeterministicHash.js';
export * from './types/oracle.js';
'''

with open(os.path.join(output_dir, "tests/oracle.test.ts"), "w", encoding="utf-8") as f:
    f.write(test_file)
with open(os.path.join(output_dir, "src/index.ts"), "w", encoding="utf-8") as f:
    f.write(index_ts)

print("✅ tests/oracle.test.ts")
print("✅ src/index.ts")
