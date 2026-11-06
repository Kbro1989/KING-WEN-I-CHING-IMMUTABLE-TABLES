 function _nullishCoalesce(lhs, rhsFn) { if (lhs != null) { return lhs; } else { return rhsFn(); } }







/**
 * A collapsed hexagram state from the 512-state oracle.
 * This is the resolved observable state after intent superposition collapses.
 */




















































































/**
 * Convert a StateCapture to its telemetry representation.
 * Mirrors Python StateCapture.to_telemetry() exactly.
 */
export function captureToTelemetry(capture) {
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
    action: _nullishCoalesce(capture.action_taken, () => ( null)),
    outcome: _nullishCoalesce(capture.outcome, () => ( null)),
  };
}

/** Internal: compute bits from intent (avoiding circular import) */
function intentToBitsFromCapture(intent) {
  let bits = 0;
  for (let i = 0; i < 3; i++) {
    if (intent.temporal[i] > 0) bits |= (1 << i);
    if (intent.emotional[i] > 0.5) bits |= (1 << (i + 3));
    if (intent.action[i] > 0) bits |= (1 << (i + 6));
  }
  return bits;
}
