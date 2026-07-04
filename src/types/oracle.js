export const TemporalPhase = { 0: 'past', 1: 'present', 2: 'future' };
export const HexagramAction = ['ASSERT','YIELD','ADAPT','WAIT'];
export const HexagramCategory = ['sovereign','boundary','transformer','dissipator'];

export function phaseToString(phase) {
  return TemporalPhase[phase] ?? 'present';
}

export function createTemporalState(phase, emotionalInput) {
  const dominantPhase = typeof phase === 'number' ? phase % 3 : 0;
  const substate = emotionalInput < 33 ? 'old' : emotionalInput > 66 ? 'young' : 'transition';
  const baseWeight = 0.6;
  const sideWeight = 0.2;
  return {
    dominantPhase,
    substate,
    pastWeight: dominantPhase === 0 ? baseWeight : sideWeight,
    presentWeight: dominantPhase === 1 ? baseWeight : sideWeight,
    futureWeight: dominantPhase === 2 ? baseWeight : sideWeight,
  };
}

export function ensureHexagramState(id, record) {
  return {
    id: Number(id),
    name: record.name,
    chinese: record.chinese,
    pinyin: record.pinyin,
    binary: record.binary,
    unicode: record.unicode,
    upper_trigram: record.upper_trigram,
    lower_trigram: record.lower_trigram,
    category: record.category,
    action: record.action,
  };
}

export function emotionalDelta(current, target) {
  return {
    chaos: target.chaos - current.chaos,
    whimsy: target.whimsy - current.whimsy,
    darkTone: target.darkTone - current.darkTone,
    coherence: target.coherence - current.coherence,
    voiceWeight: target.voiceWeight - current.voiceWeight,
  };
}
