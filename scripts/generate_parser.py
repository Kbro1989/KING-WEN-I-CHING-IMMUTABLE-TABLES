#!/usr/bin/env python3
"""Runnable entry point: generate TS parser/narrative modules."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

emotional_parser = '''import { EmotionalVector, OracleQuery, UserContext } from '../types/oracle.js';

export class EmotionalParser {
  parse(query: OracleQuery): EmotionalVector {
    const base: EmotionalVector = {
      chaos: 0.5,
      whimsy: 0.5,
      darkTone: 0.5,
      coherence: 0.5,
      voiceWeight: 0.5,
    };

    if (query.user_context) {
      this.applyContext(base, query.user_context);
    }

    if (query.emotional_input !== undefined) {
      const normalized = query.emotional_input / 100;
      base.whimsy = normalized;
      base.darkTone = 1 - normalized;
    }

    return base;
  }

  private applyContext(vec: EmotionalVector, ctx: UserContext): void {
    if (ctx.fatigue !== undefined) {
      vec.chaos = Math.min(1, vec.chaos + (ctx.fatigue / 100) * 0.3);
      vec.coherence = Math.max(0, vec.coherence - (ctx.fatigue / 100) * 0.2);
    }
  }
}
'''

narrative_engine = '''import { ReflectionSet, TemporalState, HexagramState, EmotionalVector, EmotionalWeightEntry } from '../types/oracle.js';

export class NarrativeEngine {
  private temporalReflections: Map<number, { past: string; present: string; future: string }>;
  private emotionalWeights: Map<number, EmotionalWeightEntry>;

  constructor(
    reflectionsJson: Record<string, { past: string; present: string; future: string }>,
    weightsJson: Record<string, EmotionalWeightEntry>
  ) {
    this.temporalReflections = new Map();
    this.emotionalWeights = new Map();

    for (const [id, data] of Object.entries(reflectionsJson)) {
      this.temporalReflections.set(parseInt(id), data);
    }
    for (const [id, data] of Object.entries(weightsJson)) {
      this.emotionalWeights.set(parseInt(id), data);
    }
  }

  generateReflections(
    hexagram: HexagramState,
    temporal: TemporalState,
    emotional: EmotionalVector
  ): ReflectionSet {
    const reflections = this.temporalReflections.get(hexagram.id);
    if (!reflections) throw new Error(`No reflections for hexagram ${hexagram.id}`);

    const weights = this.emotionalWeights.get(hexagram.id);

    const past = this.modulateVoice(reflections.past, 'past', temporal, emotional, weights);
    const present = this.modulateVoice(reflections.present, 'present', temporal, emotional, weights);
    const future = this.modulateVoice(reflections.future, 'future', temporal, emotional, weights);

    const weave = this.weaveUnified(past, present, future, temporal);

    return { past, present, future, unified_weave: weave };
  }

  private modulateVoice(
    baseText: string,
    phaseName: string,
    temporal: TemporalState,
    emotional: EmotionalVector,
    weights?: EmotionalWeightEntry
  ): string {
    return baseText;
  }

  private weaveUnified(past: string, present: string, future: string, temporal: TemporalState): string {
    const dominant = ['past', 'present', 'future'][temporal.dominantPhase];
    return `[${dominant.toUpperCase()} VOICE LEADS]\\n\\n${present}\\n\\n[Echoes:]\\nFrom what was: ${past.slice(0, 120)}...\\nFrom what could be: ${future.slice(0, 120)}...`;
  }
}
'''

with open(os.path.join(output_dir, "src/parser/EmotionalParser.ts"), "w", encoding="utf-8") as f:
    f.write(emotional_parser)
with open(os.path.join(output_dir, "src/parser/NarrativeEngine.ts"), "w", encoding="utf-8") as f:
    f.write(narrative_engine)

print("✅ src/parser/EmotionalParser.ts")
print("✅ src/parser/NarrativeEngine.ts")
