// ============================================================
// INTENT VECTOR — 9-dimensional superposition for POG3 substrate
// Maps to Python IntentVector in pog3_hexagram_runtime_substrate.py
// ============================================================

import { EmotionalVector, TemporalState } from './oracle.js';

/**
 * 9-bit intent vector representing agent superposition before collapse.
 *
 * Dimensions:
 *   0-2: Temporal (past/present/future signature)
 *   3-5: Emotional (chaos/whimsy/darkTone from pipeline prosody)
 *   6-8: Action (move/attack/interact from POG2 actionables)
 */
export interface IntentVector {
  /** 3-bit past/present/future signature. Each element is 0 (yin) or 1 (yang). */
  temporal: [number, number, number];

  /** Emotional weights from pipeline prosody. Each in [0.0, 1.0]. */
  emotional: [chaos: number, whimsy: number, darkTone: number];

  /** 3-bit action signature. Each element is 0 (inactive) or 1 (active). */
  action: [number, number, number];
}

/**
 * Convert an EmotionalVector (5-dim) + TemporalState → IntentVector (9-dim).
 *
 * This is the bridge from the existing King Wen type system into the
 * POG3 substrate's 512-state oracle. The 5-dim emotional vector is
 * projected down to 3 dims (chaos/whimsy/darkTone), and the temporal
 * state's dominant phase determines the temporal signature.
 */
export function emotionalToIntent(
  emotional: EmotionalVector,
  temporal: TemporalState,
  actionBits?: [number, number, number],
): IntentVector {
  // Temporal: one-hot encode the dominant phase
  const temporalBits: [number, number, number] = [
    temporal.dominantPhase === 0 ? 1 : 0,  // past
    temporal.dominantPhase === 1 ? 1 : 0,  // present
    temporal.dominantPhase === 2 ? 1 : 0,  // future
  ];

  return {
    temporal: temporalBits,
    emotional: [emotional.chaos, emotional.whimsy, emotional.darkTone],
    action: actionBits ?? [0, 0, 0],
  };
}

/**
 * Collapse an IntentVector to a deterministic 9-bit integer (0-511).
 * Mirrors Python IntentVector.to_bits() exactly.
 */
export function intentToBits(intent: IntentVector): number {
  let bits = 0;

  // Temporal: bits 0-2
  for (let i = 0; i < 3; i++) {
    if (intent.temporal[i] > 0) bits |= (1 << i);
  }

  // Emotional: bits 3-5, threshold at 0.5
  for (let i = 0; i < 3; i++) {
    if (intent.emotional[i] > 0.5) bits |= (1 << (i + 3));
  }

  // Action: bits 6-8
  for (let i = 0; i < 3; i++) {
    if (intent.action[i] > 0) bits |= (1 << (i + 6));
  }

  return bits;
}
