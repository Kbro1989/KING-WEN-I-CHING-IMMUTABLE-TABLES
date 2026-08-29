// =============================================================================
// King Wen 8-Phase Temporal Mathematics
//
// Matches PHASE_INFO in emotional_engine.py exactly:
//   0=past, 1=present, 2=future, 3=transition, 4=resolution,
//   5=dissolution, 6=crystallization, 7=void
//
// No randomness. Phase index is deterministic from tick modulo 8.
// Substate derived from emotional_input slider thresholds.
// =============================================================================
export const PHASE_NAMES = [
    'past', 'present', 'future', 'transition',
    'resolution', 'dissolution', 'crystallization', 'void',
];
export const PHASE_YAO_MAP = {
    0: 'old_yang', // past
    1: 'stable_yang', // present
    2: 'new_yao', // future
    3: 'old_yao', // transition
    4: 'old_yao', // resolution
    5: 'old_yao', // dissolution
    6: 'stable_yao', // crystallization
    7: 'stable_yin', // void
};
/**
 * Compute full 8-phase temporal state from tick and emotional_input.
 *
 * tick % 8 → phase index (deterministic, no randomness)
 * emotional_input thresholds → substate (old/young/transition)
 */
export function computeTemporalPhase(tick, emotionalInput) {
    const phase8 = (tick % 8);
    const phaseName = PHASE_NAMES[phase8];
    // Map 8-phase to legacy 3-phase: 0→0(past), 1→1(present), 2→2(future),
    // 3→1, 4→0, 5→2, 6→1, 7→1
    const PHASE8_TO_LEGACY = [0, 1, 2, 1, 0, 2, 1, 1];
    const dominantPhase = PHASE8_TO_LEGACY[phase8];
    const substate = emotionalInput < 33 ? 'old' :
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
export function phaseToString(phase) {
    if (phase >= 0 && phase < PHASE_NAMES.length)
        return PHASE_NAMES[phase];
    return ['past', 'present', 'future'][phase] ?? 'present';
}
