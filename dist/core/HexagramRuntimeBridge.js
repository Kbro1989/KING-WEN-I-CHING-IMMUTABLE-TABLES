// ============================================================
// HEXAGRAM RUNTIME BRIDGE — TypeScript ↔ Python substrate
//
// Bridges the existing King Wen TS modules (EmotionalParser,
// TemporalMath, OracleEngine) into the POG3 hexagram runtime
// substrate. Can call the Python substrate via subprocess or
// operate in pure-TS mode using the same deterministic collapse.
// ============================================================
import { emotionalToIntent, intentToBits } from '../types/IntentVector.js';
import { captureToTelemetry } from '../types/StateCapture.js';
/** Phase map matching Python HexagramState.from_bits() */
const PHASE_MAP = {
    0: 'past', 1: 'present', 2: 'future',
    3: 'past', 4: 'present', 5: 'future',
    6: 'past', 7: 'present',
};
/**
 * Pure-TypeScript hexagram collapse engine.
 *
 * Mirrors the Python HexagramRuntimeEngine.consult() deterministic
 * collapse logic so the TS layer can produce identical results without
 * crossing the Python boundary. This is the "embedded mode" — for the
 * full engine with temporal reflection and adapter callbacks, use the
 * Python substrate via subprocess.
 */
export class HexagramRuntimeBridge {
    sessionId;
    tickCounter;
    stateHistory;
    hexagramRegistry;
    emotionalWeights;
    constructor(sessionId, hexagramRegistry, emotionalWeights) {
        this.sessionId = sessionId;
        this.tickCounter = 0;
        this.stateHistory = [];
        this.hexagramRegistry = hexagramRegistry ?? {};
        this.emotionalWeights = emotionalWeights ?? {};
    }
    /**
     * Consult the oracle — collapse an IntentVector to a hexagram state.
     *
     * This is the deterministic pure-TS equivalent of the Python
     * HexagramRuntimeEngine.consult(). Temporal reflection is simplified
     * (no momentum); for full behavior, call the Python substrate.
     */
    consult(intent, context) {
        this.tickCounter += 1;
        const tickId = this.tickCounter;
        const bits = intentToBits(intent);
        // Lower 6 bits → yao lines (matching Python exactly)
        const yaoLines = [];
        for (let i = 0; i < 6; i++) {
            yaoLines.push((bits & (1 << i)) ? 1 : -1);
        }
        // Upper 3 bits → temporal phase
        const temporalBits = (bits >> 6) & 0b111;
        const temporalPhase = PHASE_MAP[temporalBits] ?? 'present';
        // King Wen ID: lower 6 bits + 1 (1-64)
        const kingWenId = (bits & 0b111111) + 1;
        const registryEntry = this.hexagramRegistry[String(kingWenId)] ?? {};
        const kwWeights = this.emotionalWeights[String(kingWenId)] ?? {};
        const collapsedState = {
            state_id: bits,
            yao_lines: yaoLines,
            temporal_phase: temporalPhase,
            emotional_signature: {
                chaos: intent.emotional[0],
                whimsy: intent.emotional[1],
                darkTone: intent.emotional[2],
                kw_chaos: kwWeights.chaos,
                kw_whimsy: kwWeights.whimsy,
                kw_darkTone: kwWeights.darkTone,
                kw_coherence: kwWeights.coherence,
                kw_voiceWeight: kwWeights.voiceWeight,
            },
            provenance: {
                session_id: this.sessionId,
                tick_id: tickId,
                timestamp: Date.now() / 1000,
                context: context ?? {},
                king_wen_id: kingWenId,
                king_wen_name: registryEntry.name ?? '',
                king_wen_action: (registryEntry.action ?? 'WAIT'),
                king_wen_category: (registryEntry.category ?? 'transformer'),
            },
        };
        const capture = {
            intent,
            collapsed_state: collapsedState,
            timestamp: Date.now() / 1000,
            session_id: this.sessionId,
            tick_id: tickId,
        };
        this.stateHistory.push(capture);
        return [collapsedState, capture];
    }
    /**
     * High-level bridge: take existing EmotionalVector + TemporalState
     * and consult the oracle. This is what OracleEngine and downstream
     * consumers call.
     */
    consultFromEmotion(emotional, temporal, actionBits, context) {
        const intent = emotionalToIntent(emotional, temporal, actionBits);
        return this.consult(intent, context);
    }
    /** Get recent state history for analysis. */
    getStateHistory(n = 64) {
        return this.stateHistory.slice(-n);
    }
    /** Export emotional time-series for Megatron-LM training. */
    getEmotionalTimeseries() {
        return this.stateHistory.map(captureToTelemetry);
    }
}
