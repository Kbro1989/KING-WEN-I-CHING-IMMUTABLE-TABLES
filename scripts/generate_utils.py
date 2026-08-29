#!/usr/bin/env python3
"""Runnable entry point: generate TS utility modules."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

det_hash = '''import { EmotionalVector } from '../types/oracle.js';

// SHA256-based deterministic hashing & 5 coprime prime extractor — zero randomness

export async function deterministicHash(input: string): Promise<Uint8Array> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  return new Uint8Array(await crypto.subtle.digest('SHA-256', data));
}

export async function deterministicHashHex(input: string): Promise<string> {
  const bytes = await deterministicHash(input);
  return Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Deterministic ASCII token sum matching Python _intent_to_vector in emotional_engine.py.
 */
export function computeTokenSum(tokens: Iterable<string>): number {
  let sum = 0;
  for (const token of tokens) {
    for (let i = 0; i < token.length; i++) {
      sum += token.charCodeAt(i);
    }
  }
  return sum;
}

/**
 * 5 Coprime Prime Vector Perturbation: (97, 89, 83, 79, 73)
 * Exact match for Python _intent_to_vector coprime moduli extractor.
 */
export function extractCoprimePrimeVector(hashVal: number): EmotionalVector {
  return {
    chaos: ((hashVal % 97) / 97.0) * 0.12,
    whimsy: ((Math.floor(hashVal / 7) % 89) / 89.0) * 0.12,
    darkTone: ((Math.floor(hashVal / 13) % 83) / 83.0) * 0.12,
    coherence: ((Math.floor(hashVal / 19) % 79) / 79.0) * 0.12,
    voiceWeight: ((Math.floor(hashVal / 23) % 73) / 73.0) * 0.12,
  };
}

export async function generateDeterministicInjectHash(
  sessionId: string,
  tick: number,
  queryText: string
): Promise<string> {
  const input = `${tick}:${sessionId}:${queryText}`;
  return deterministicHashHex(input);
}
'''

temporal_math = '''// =============================================================================
// King Wen 8-Phase Temporal Mathematics
//
// Matches PHASE_INFO in emotional_engine.py exactly:
//   0=past, 1=present, 2=future, 3=transition, 4=resolution,
//   5=dissolution, 6=crystallization, 7=void
//
// No randomness. Phase index is deterministic from tick modulo 8.
// Substate derived from emotional_input slider thresholds.
// =============================================================================

/** Full 8-phase temporal index (0..7) */
export type TemporalPhase8 = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7;

/** Legacy 3-phase for OracleResponse backward compat */
export type TemporalPhase = 0 | 1 | 2;

export type TemporalSubstate = 'old' | 'young' | 'transition';

export const PHASE_NAMES: readonly string[] = [
  'past', 'present', 'future', 'transition',
  'resolution', 'dissolution', 'crystallization', 'void',
] as const;

export const PHASE_YAO_MAP: Record<number, string> = {
  0: 'old_yang',    // past
  1: 'stable_yang', // present
  2: 'new_yao',     // future
  3: 'old_yao',     // transition
  4: 'old_yao',     // resolution
  5: 'old_yao',     // dissolution
  6: 'stable_yao',  // crystallization
  7: 'stable_yin',  // void
};

export interface TemporalState {
  /** Full 8-phase index (0..7) */
  phase8: TemporalPhase8;
  /** Phase name string */
  phaseName: string;
  /** Legacy 3-phase mapping for backward compat: past=0, present=1, future=2 */
  dominantPhase: TemporalPhase;
  /** Substate from emotional_input */
  substate: TemporalSubstate;
  /** Yao state for this phase */
  yaoState: string;
  /** Temporal weight distribution across past/present/future */
  pastWeight: number;
  presentWeight: number;
  futureWeight: number;
}

/**
 * Compute full 8-phase temporal state from tick and emotional_input.
 *
 * tick % 8 → phase index (deterministic, no randomness)
 * emotional_input thresholds → substate (old/young/transition)
 */
export function computeTemporalPhase(
  tick: number,
  emotionalInput: number
): TemporalState {
  const phase8 = (tick % 8) as TemporalPhase8;
  const phaseName = PHASE_NAMES[phase8];

  // Map 8-phase to legacy 3-phase: 0→0(past), 1→1(present), 2→2(future),
  // 3→1, 4→0, 5→2, 6→1, 7→1
  const PHASE8_TO_LEGACY: TemporalPhase[] = [0, 1, 2, 1, 0, 2, 1, 1];
  const dominantPhase = PHASE8_TO_LEGACY[phase8];

  const substate: TemporalSubstate =
    emotionalInput < 33 ? 'old' :
    emotionalInput > 66 ? 'young' :
    'transition';

  const yaoState = PHASE_YAO_MAP[phase8];

  // Weight distribution: dominant phase gets 0.6, others split 0.2 each
  const baseWeight = 0.6;
  const sideWeight = 0.2;

  return {
    phase8,
    phaseName,
    dominantPhase,
    substate,
    yaoState,
    pastWeight: dominantPhase === 0 ? baseWeight : sideWeight,
    presentWeight: dominantPhase === 1 ? baseWeight : sideWeight,
    futureWeight: dominantPhase === 2 ? baseWeight : sideWeight,
  };
}

export function phaseToString(phase: TemporalPhase | TemporalPhase8): string {
  if (phase >= 0 && phase < PHASE_NAMES.length) return PHASE_NAMES[phase];
  return ['past', 'present', 'future'][phase] ?? 'present';
}
'''

with open(os.path.join(output_dir, "src/utils/DeterministicHash.ts"), "w", encoding="utf-8") as f:
    f.write(det_hash)
with open(os.path.join(output_dir, "src/utils/TemporalMath.ts"), "w", encoding="utf-8") as f:
    f.write(temporal_math)

print("✅ src/utils/DeterministicHash.ts")
print("✅ src/utils/TemporalMath.ts")
