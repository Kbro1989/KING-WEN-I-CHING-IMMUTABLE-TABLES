import { ReflectionSet, TemporalState, HexagramState, EmotionalVector, EmotionalWeightEntry } from '../types/oracle.js';
import type { StateCapture } from '../types/StateCapture.js';

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

  generateFromCapture(capture: StateCapture): ReflectionSet {
    const kingWenId = capture.collapsed_state.provenance.king_wen_id;
    const reflections = this.temporalReflections.get(kingWenId);
    if (!reflections) throw new Error(`No reflections for hexagram ${kingWenId}`);

    const weights = this.emotionalWeights.get(kingWenId);

    const phaseStr = capture.collapsed_state.temporal_phase;
    const dominantPhase = phaseStr === 'past' ? 0 : phaseStr === 'future' ? 2 : 1;
    const temporal: TemporalState = {
      dominantPhase,
      substate: 'transition',
      pastWeight: dominantPhase === 0 ? 0.6 : 0.2,
      presentWeight: dominantPhase === 1 ? 0.6 : 0.2,
      futureWeight: dominantPhase === 2 ? 0.6 : 0.2,
    };

    const emotional: EmotionalVector = {
      chaos: capture.intent.emotional[0],
      whimsy: capture.intent.emotional[1],
      darkTone: capture.intent.emotional[2],
      coherence: 0.5,
      voiceWeight: 0.5,
    };

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
    const action = weights?.trainingNotes?.includes("ASSERT") ? "ASSERT" :
                   weights?.trainingNotes?.includes("YIELD") ? "YIELD" :
                   weights?.trainingNotes?.includes("ADAPT") ? "ADAPT" : "WAIT";

    // 1. CODE COMPLETION MODE
    // High coherence suggests structured code completion
    if (emotional.coherence > 0.6 && emotional.chaos < 0.4) {
      return this.generateCodeCompletion(phaseName, action, emotional);
    }

    // 2. BLUEPRINT / VISION MODE
    // High chaos + whimsy suggests visual or topological structures
    if (emotional.chaos > 0.5 && emotional.whimsy > 0.5) {
      return this.generateBlueprint(phaseName, action, emotional);
    }

    // 3. AGENT DEFINITION MODE
    // High voiceWeight + darkTone suggests background agent specs
    if (emotional.voiceWeight > 0.6 && emotional.darkTone > 0.6) {
      return this.generateAgentSpec(phaseName, action, emotional);
    }

    // 4. GENERATIONS / LITERARY TEXT MODE (Default fallback)
    let text = baseText;
    if (emotional.chaos > 0.7) {
      text = `[CHAOS LEVEL ${Math.floor(emotional.chaos * 100)}% DETECTED] ${text} [SYSTEM ITERATION RECURSED]`;
    }
    if (emotional.whimsy > 0.7) {
      text = `✨ (whimsy sub-vector) ${text} 🌀 [quantum whimsy enabled]`;
    }
    if (emotional.darkTone > 0.7) {
      text = `⚠️ [DARK PATH ACTIVE] ${text} [entropy threshold crossed]`;
    }
    return text;
  }

  private generateCodeCompletion(phase: string, action: string, emotional: EmotionalVector): string {
    return `/**
 * CODE COMPLETION: Volition Substrate [Phase: ${phase}]
 * Coherence: ${emotional.coherence.toFixed(2)}, Chaos: ${emotional.chaos.toFixed(2)}
 * Volition Target: ${action}
 */
export async function executeVolitionStep<T>(intent: T): Promise<{ success: boolean; outcome: string }> {
  const metabolicHeartbeat = 640; // ms
  const threshold = ${Math.max(0.1, 1 - emotional.coherence).toFixed(2)};
  
  if (Math.random() > threshold) {
    return {
      success: true,
      outcome: "Volition commit executed successfully matching ${action} state."
    };
  }
  
  throw new Error("Volition step failed: coherence threshold mismatch.");
}`;
  }

  private generateBlueprint(phase: string, action: string, emotional: EmotionalVector): string {
    return `====================================================================
BLUEPRINT: POG3 Volition Grid Topology [Phase: ${phase}]
Action: ${action} | Chaos: ${emotional.chaos.toFixed(2)} | Whimsy: ${emotional.whimsy.toFixed(2)}
====================================================================
      [Superposition Intent]
                |
                v (Emotional Weighting: whimsy=${emotional.whimsy.toFixed(2)})
      [Hexagram Collapse]  ---(broadcast)---> [HexagramNetworkBridge]
                |
                v (Temporal Phase: ${phase})
       +-----------------+
       |  State Capture  |
       |  (ID: deterministic)
       +-----------------+
                |
                v
      [ModelRolodex Select] ===> Precise/Creative bias adjusted by ${Math.floor((1 - emotional.chaos) * 100)}%
====================================================================`;
  }

  private generateAgentSpec(phase: string, action: string, emotional: EmotionalVector): string {
    return `agent_definition:
  id: pog3_volition_agent_${phase}
  volition_rhythm: 640ms
  reputation_bias: ${emotional.darkTone > 0.8 ? 'entropy_resilient' : 'standard'}
  parameters:
    chaos_tolerance: ${emotional.chaos.toFixed(3)}
    coherence_target: ${emotional.coherence.toFixed(3)}
    voice_weight: ${emotional.voiceWeight.toFixed(3)}
  strategy:
    mode: ${action}
    fallback: WAIT
    dispatch_limbs:
      - GhostSplat
      - ModelRolodex
      - HexagramNetworkBridge`;
  }

  private weaveUnified(past: string, present: string, future: string, temporal: TemporalState): string {
    const dominant = ['past', 'present', 'future'][temporal.dominantPhase];
    return `[${dominant.toUpperCase()} VOICE LEADS]\n\n${present}\n\n[Echoes:]\nFrom what was: ${past.slice(0, 120)}...\nFrom what could be: ${future.slice(0, 120)}...`;
  }
}
