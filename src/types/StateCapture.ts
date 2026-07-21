// ============================================================
// STATE CAPTURE — Collapse record with full provenance
// Maps to Python StateCapture in pog3_hexagram_runtime_substrate.py
// ============================================================

import { EmotionalVector, HexagramAction, HexagramCategory, TemporalPhase } from './oracle.js';
import { IntentVector } from './IntentVector.js';

/**
 * A collapsed hexagram state from the 512-state oracle.
 * This is the resolved observable state after intent superposition collapses.
 */
export interface CollapsedHexagramState {
  /** 0-511: the 9-bit collapsed state ID */
  state_id: number;

  /** 6 yao lines, each -1 (yin) or 1 (yang) */
  yao_lines: number[];

  /** Temporal phase at collapse: "past", "present", or "future" */
  temporal_phase: string;

  /** Emotional signature at collapse time */
  emotional_signature: {
    chaos: number;
    whimsy: number;
    darkTone: number;
    /** King Wen corpus emotional weights (when available) */
    kw_chaos?: number;
    kw_whimsy?: number;
    kw_darkTone?: number;
    kw_coherence?: number;
    kw_voiceWeight?: number;
  };

  /** Provenance trail — who, when, why this state collapsed */
  provenance: {
    session_id: string;
    tick_id: number;
    timestamp: number;
    context: Record<string, unknown>;
    king_wen_id: number;
    king_wen_name: string;
    king_wen_action: HexagramAction;
    king_wen_category: HexagramCategory;
  };
}

/**
 * A captured state transition — the quantum measurement record.
 * Records what collapsed, when, and the emotional context at collapse time.
 */
export interface StateCapture {
  /** The intent that was collapsed */
  intent: IntentVector;

  /** The resulting hexagram state */
  collapsed_state: CollapsedHexagramState;

  /** Unix timestamp of the capture */
  timestamp: number;

  /** Session identifier */
  session_id: string;

  /** Monotonic tick counter within the session */
  tick_id: number;

  /** What action was taken based on this collapse (filled post-hoc) */
  action_taken?: string;

  /** Outcome of the action (filled post-hoc) */
  outcome?: string;
}

/**
 * Telemetry record exported from a StateCapture.
 * Suitable for Megatron-LM training or HexagramNetworkBridge broadcast.
 */
export interface StateTelemetry {
  session_id: string;
  tick_id: number;
  timestamp: number;
  intent_bits: number;
  state_id: number;
  king_wen_id: number;
  temporal_phase: string;
  emotional: {
    chaos: number;
    whimsy: number;
    darkTone: number;
  };
  action: string | null;
  outcome: string | null;
}

/**
 * Convert a StateCapture to its telemetry representation.
 * Mirrors Python StateCapture.to_telemetry() exactly.
 */
export function captureToTelemetry(capture: StateCapture): StateTelemetry {
  return {
    session_id: capture.session_id,
    tick_id: capture.tick_id,
    timestamp: capture.timestamp,
    intent_bits: intentToBitsFromCapture(capture.intent),
    state_id: capture.collapsed_state.state_id,
    king_wen_id: capture.collapsed_state.provenance.king_wen_id,
    temporal_phase: capture.collapsed_state.temporal_phase,
    emotional: {
      chaos: capture.intent.emotional[0],
      whimsy: capture.intent.emotional[1],
      darkTone: capture.intent.emotional[2],
    },
    action: capture.action_taken ?? null,
    outcome: capture.outcome ?? null,
  };
}

/** Internal: compute bits from intent (avoiding circular import) */
function intentToBitsFromCapture(intent: IntentVector): number {
  let bits = 0;
  for (let i = 0; i < 3; i++) {
    if (intent.temporal[i] > 0) bits |= (1 << i);
    if (intent.emotional[i] > 0.5) bits |= (1 << (i + 3));
    if (intent.action[i] > 0) bits |= (1 << (i + 6));
  }
  return bits;
}
