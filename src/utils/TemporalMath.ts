import { TemporalPhase, TemporalSubstate, TemporalState } from '../types/oracle.js';

export function computeTemporalPhase(
  tick: number,
  emotionalInput: number
): TemporalState {
  const phase = (tick % 3) as TemporalPhase;
  const substate: TemporalSubstate =
    emotionalInput < 33 ? 'old' :
    emotionalInput > 66 ? 'young' :
    'transition';

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

export function phaseToString(phase: TemporalPhase): string {
  return ['past', 'present', 'future'][phase];
}
