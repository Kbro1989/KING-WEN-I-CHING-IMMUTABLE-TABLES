#!/usr/bin/env python3
"""Runnable entry point: generate TS type definitions."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
output_dir = REPO
for sub in ["data", "src/core", "src/parser", "src/types", "src/utils", "tests"]:
    os.makedirs(os.path.join(output_dir, sub), exist_ok=True)

oracle_types = '''// ============================================================
// ORACLE EMOTIONAL STATE MACHINE — TYPE DEFINITIONS
// Pipeline: 1(question) -> 3(temporal) -> 64(hexagram|emotion) -> 3(temporal) -> 2(subsets) -> 1(resolve)
// ============================================================

export type TemporalPhase = 0 | 1 | 2; // 0=past(yin), 1=present(yang), 2=future(yao)
export type TemporalSubstate = 'old' | 'young' | 'transition';
export type HexagramAction = 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT';
export type HexagramCategory = 'sovereign' | 'boundary' | 'transformer' | 'dissipator';

export interface EmotionalVector {
  chaos: number;
  whimsy: number;
  darkTone: number;
  coherence: number;
  voiceWeight: number;
}

export interface HexagramState {
  id: number;
  name: string;
  chinese: string;
  pinyin: string;
  binary: string;
  unicode: string;
  upper_trigram: string;
  lower_trigram: string;
  category: HexagramCategory;
  action: HexagramAction;
}

export interface EmotionalWeightEntry extends EmotionalVector {
  trainingNotes: string;
}

export interface TemporalReflection {
  past: string;
  present: string;
  future: string;
}

export interface OracleQuery {
  text: string;
  session_id: string;
  state_str?: string;
  emotional_input?: number;
  user_context?: UserContext;
}

export interface UserContext {
  position?: { x: number; y: number };
  skills?: Record<string, { current: number; experience: number }>;
  inventory?: Array<{ id: number; equipped?: boolean; amount?: number }>;
  fatigue?: number;
}

export interface TemporalState {
  dominantPhase: TemporalPhase;
  substate: TemporalSubstate;
  pastWeight: number;
  presentWeight: number;
  futureWeight: number;
}

export interface ReflectionSet {
  past: string;
  present: string;
  future: string;
  unified_weave: string;
}

export interface OracleResponse {
  hexagram_id: number;
  hexagram_name: string;
  hexagram_unicode: string;
  temporal_phase: TemporalPhase;
  temporal_substate: TemporalSubstate;
  past_reflection: string;
  present_reflection: string;
  future_reflection: string;
  unified_weave: string;
  sovereign_assertion: string;
  boundary_condition: string;
  dissipator_warning: string;
  action: HexagramAction;
  category: HexagramCategory;
  emotional_deltas: EmotionalVector;
  state_str?: string;
}

export interface OracleConfig {
  tick_interval_ms: number;
  deterministic: boolean;
  emotional_smoothing: number;
}
'''

with open(os.path.join(output_dir, "src/types/oracle.ts"), "w", encoding="utf-8") as f:
    f.write(oracle_types)

print("✅ src/types/oracle.ts")
