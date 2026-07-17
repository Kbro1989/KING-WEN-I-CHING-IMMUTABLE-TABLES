// ============================================================
// INTENT VECTOR — 9-dimensional superposition for POG3 substrate
// Maps to Python IntentVector in pog3_hexagram_runtime_substrate.py
// ============================================================
/**
 * Convert an EmotionalVector (5-dim) + TemporalState → IntentVector (9-dim).
 *
 * This is the bridge from the existing King Wen type system into the
 * POG3 substrate's 512-state oracle. The 5-dim emotional vector is
 * projected down to 3 dims (chaos/whimsy/darkTone), and the temporal
 * state's dominant phase determines the temporal signature.
 */
export function emotionalToIntent(emotional, temporal, actionBits) {
    // Temporal: one-hot encode the dominant phase
    const temporalBits = [
        temporal.dominantPhase === 0 ? 1 : 0, // past
        temporal.dominantPhase === 1 ? 1 : 0, // present
        temporal.dominantPhase === 2 ? 1 : 0, // future
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
export function intentToBits(intent) {
    let bits = 0;
    // Temporal: bits 0-2
    for (let i = 0; i < 3; i++) {
        if (intent.temporal[i] > 0)
            bits |= (1 << i);
    }
    // Emotional: bits 3-5, threshold at 0.5
    for (let i = 0; i < 3; i++) {
        if (intent.emotional[i] > 0.5)
            bits |= (1 << (i + 3));
    }
    // Action: bits 6-8
    for (let i = 0; i < 3; i++) {
        if (intent.action[i] > 0)
            bits |= (1 << (i + 6));
    }
    return bits;
}
