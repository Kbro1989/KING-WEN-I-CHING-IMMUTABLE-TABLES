export function computeTemporalPhase(tick, emotionalInput) {
  const phase = tick % 3;
  const substate = emotionalInput < 33 ? 'old' : emotionalInput > 66 ? 'young' : 'transition';
  const baseWeight = 0.6;
  const sideWeight = 0.2;
  return {
    dominantPhase: phase,
    substate,
    pastWeight: phase === 0 ? baseWeight : sideWeight,
    presentWeight: phase === 1 ? baseWeight : sideWeight,
    futureWeight: phase === 2 ? baseWeight : sideWeight,
  };
}

export function phaseToString(phase) {
  return ['past', 'present', 'future'][phase];
}
