import { ReflectionSet, TemporalState, HexagramState, EmotionalVector, EmotionalWeightEntry } from '../types/oracle.js';

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
    return `[${dominant.toUpperCase()} VOICE LEADS]\n\n${present}\n\n[Echoes:]\nFrom what was: ${past.slice(0, 120)}...\nFrom what could be: ${future.slice(0, 120)}...`;
  }
}
