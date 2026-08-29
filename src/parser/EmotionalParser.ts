import { EmotionalVector, OracleQuery, UserContext } from '../types/oracle.js';
import { computeTokenSum, extractCoprimePrimeVector } from '../utils/DeterministicHash.js';

// =============================================================================
// Intent keyword vocabulary — exact match of _INTENT_KEYWORDS in emotional_engine.py
// =============================================================================

const INTENT_KEYWORDS: Record<string, string[]> = {
  create:     ['create', 'build', 'make', 'generate', 'new', 'start', 'begin', 'initiate'],
  destroy:    ['destroy', 'end', 'kill', 'stop', 'break', 'collapse', 'remove', 'delete'],
  transform:  ['transform', 'change', 'evolve', 'morph', 'shift', 'transition', 'become'],
  explore:    ['explore', 'discover', 'find', 'search', 'wander', 'journey', 'seek'],
  understand: ['understand', 'learn', 'see', 'clarity', 'know', 'comprehend', 'insight'],
  feel:       ['feel', 'emotion', 'love', 'fear', 'joy', 'pain', 'heart', 'soul'],
  speak:      ['speak', 'voice', 'say', 'tell', 'express', 'communicate', 'utter'],
  listen:     ['listen', 'hear', 'silence', 'quiet', 'still', 'pause', 'receive'],
  connect:    ['connect', 'join', 'unite', 'bond', 'link', 'bridge', 'weave'],
  protect:    ['protect', 'defend', 'guard', 'secure', 'shelter', 'preserve', 'safe'],
  conflict:   ['conflict', 'fight', 'oppose', 'clash', 'battle', 'resist', 'challenge'],
  heal:       ['heal', 'repair', 'restore', 'renew', 'mend', 'fix', 'revive'],
  grow:       ['grow', 'expand', 'increase', 'amplify', 'scale', 'rise', 'flourish'],
  release:    ['release', 'free', 'surrender', 'yield', 'open', 'flow'],
  focus:      ['focus', 'concentrate', 'center', 'aim', 'direct', 'target', 'precision'],
};

function clamp(value: number, lo = 0.0, hi = 1.0): number {
  return Math.max(lo, Math.min(hi, value));
}

export interface IntentExtraction {
  queryTokens: Set<string>;
  matchedIntents: Record<string, number>;
  dominantIntent: string;
  intensity: number;
  wordCount: number;
  intentVector: EmotionalVector;
}

export class EmotionalParser {
  /**
   * Full deterministic parse pipeline:
   *   1. Extract intent keywords → score distribution
   *   2. Compute 5-axis base vector from intent boosts
   *   3. Apply coprime prime hash perturbation from token ASCII sum
   *   4. Apply user context weighting (fatigue, etc.)
   *
   * Matches Python extract_intent() + _intent_to_vector() exactly.
   * No randomness. No fallback to flat 0.5 defaults.
   */
  parse(query: OracleQuery): EmotionalVector {
    const extraction = this.extractIntent(query.text ?? '');
    const vec = { ...extraction.intentVector };

    if (query.user_context) {
      this.applyContext(vec, query.user_context);
    }

    // emotional_input slider override — same as before but additive, not replacing
    if (query.emotional_input !== undefined) {
      const normalized = query.emotional_input / 100;
      vec.whimsy = clamp(vec.whimsy * 0.7 + normalized * 0.3);
      vec.darkTone = clamp(vec.darkTone * 0.7 + (1 - normalized) * 0.3);
    }

    return vec;
  }

  /**
   * Extract intent signals from query text.
   * Exact port of Python extract_intent() in emotional_engine.py.
   */
  extractIntent(text: string): IntentExtraction {
    const lower = (text ?? '').toLowerCase();
    const words = lower.match(/[a-z0-9]+/g) ?? [];
    const wordSet = new Set(words);

    // Score each intent by keyword match with positional weight 1/(i+1)
    const matched: Record<string, number> = {};
    for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
      let score = 0;
      for (let i = 0; i < keywords.length; i++) {
        if (wordSet.has(keywords[i])) {
          score += 1.0 / (i + 1);
        }
      }
      if (score > 0) matched[intent] = score;
    }

    const dominantIntent = Object.keys(matched).length > 0
      ? Object.entries(matched).reduce((a, b) => a[1] >= b[1] ? a : b)[0]
      : 'understand';

    const total = Object.values(matched).reduce((a, b) => a + b, 0);
    const normalized: Record<string, number> = {};
    if (total > 0) {
      for (const [k, v] of Object.entries(matched)) {
        normalized[k] = v / total;
      }
    }

    const intensity = lower.trim().length > 0
      ? clamp(lower.split(/\s+/).length / 50.0)
      : 0.0;

    const intentVector = this.intentToVector(normalized, wordSet);

    return {
      queryTokens: wordSet,
      matchedIntents: matched,
      dominantIntent,
      intensity,
      wordCount: words.length,
      intentVector,
    };
  }

  /**
   * Map intent distribution + semantic tokens to 5-axis vector.
   * Exact port of Python _intent_to_vector() in emotional_engine.py.
   *
   * Base vector: [0.1, 0.1, 0.1, 0.8, 0.85]
   * Intent boosts applied per-axis.
   * Coprime prime hash perturbation (97, 89, 83, 79, 73) from token ASCII sum.
   */
  private intentToVector(
    intentScores: Record<string, number>,
    wordSet: Set<string>
  ): EmotionalVector {
    const base = [0.1, 0.1, 0.1, 0.8, 0.85];

    // Chaos boost
    const chaosBoost =
      (intentScores.conflict ?? 0) * 0.4 +
      (intentScores.destroy ?? 0) * 0.3 +
      (intentScores.transform ?? 0) * 0.2 +
      (intentScores.create ?? 0) * 0.15;
    base[0] = clamp(base[0] + chaosBoost);

    // Whimsy boost
    const whimsyBoost =
      (intentScores.explore ?? 0) * 0.3 +
      (intentScores.feel ?? 0) * 0.3 +
      (intentScores.heal ?? 0) * 0.2 +
      (intentScores.release ?? 0) * 0.2;
    base[1] = clamp(base[1] + whimsyBoost);

    // DarkTone boost
    const darkBoost =
      (intentScores.destroy ?? 0) * 0.3 +
      (intentScores.conflict ?? 0) * 0.25 +
      (intentScores.transform ?? 0) * 0.15;
    base[2] = clamp(base[2] + darkBoost);

    // Coherence boost
    const cohBoost =
      (intentScores.understand ?? 0) * 0.15 +
      (intentScores.focus ?? 0) * 0.15 +
      (intentScores.speak ?? 0) * 0.1 +
      (intentScores.protect ?? 0) * 0.1;
    base[3] = clamp(base[3] + cohBoost);

    // VoiceWeight boost
    const vwBoost =
      (intentScores.speak ?? 0) * 0.15 +
      (intentScores.protect ?? 0) * 0.1 +
      (intentScores.connect ?? 0) * 0.1 +
      (intentScores.grow ?? 0) * 0.15;
    base[4] = clamp(base[4] + vwBoost);

    // Coprime prime hash perturbation from ASCII token sum
    if (wordSet.size > 0) {
      const hashVal = computeTokenSum(wordSet);
      const primeVec = extractCoprimePrimeVector(hashVal);
      base[0] = clamp(base[0] + primeVec.chaos);
      base[1] = clamp(base[1] + primeVec.whimsy);
      base[2] = clamp(base[2] + primeVec.darkTone);
      base[3] = clamp(base[3] + primeVec.coherence);
      base[4] = clamp(base[4] + primeVec.voiceWeight);
    }

    return {
      chaos: base[0],
      whimsy: base[1],
      darkTone: base[2],
      coherence: base[3],
      voiceWeight: base[4],
    };
  }

  /**
   * Extract the 3-dimensional emotional tuple for the POG3 substrate.
   * Maps 5-dim EmotionalVector → [chaos, whimsy, darkTone] for IntentVector.
   */
  toIntentEmotional(vec: EmotionalVector): [number, number, number] {
    return [vec.chaos, vec.whimsy, vec.darkTone];
  }

  private applyContext(vec: EmotionalVector, ctx: UserContext): void {
    if (ctx.fatigue !== undefined) {
      vec.chaos = clamp(vec.chaos + (ctx.fatigue / 100) * 0.3);
      vec.coherence = clamp(vec.coherence - (ctx.fatigue / 100) * 0.2);
    }
  }
}
