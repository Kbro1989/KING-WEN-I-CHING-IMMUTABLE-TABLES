import { createTemporalState, ensureHexagramState, emotionalDelta } from '../types/oracle.js';

export class EmotionalParser {
  parse(query = {}) {
    const base = {
      chaos: 0.5,
      whimsy: 0.5,
      darkTone: 0.5,
      coherence: 0.5,
      voiceWeight: 0.5,
    };

    const normalized = (query.emotional_input ?? 50) / 100;
    return {
      ...base,
      whimsy: normalized,
      darkTone: 1 - normalized,
    };
  }
}

export class NarrativeEngine {
  constructor(reflections = {}, weights = {}) {
    this.reflections = reflections;
    this.weights = weights;
  }

  generateReflections(hexagram, temporal, emotional) {
    const data = this.reflections[String(hexagram.id)] || {};
    const past = data.past || `Past echo from ${hexagram.name}`;
    const present = data.present || `Present voice of ${hexagram.name}`;
    const future = data.future || `Future signal from ${hexagram.name}`;
    const dominant = ['past','present','future'][temporal.dominantPhase];
    const unified_weave = `[${dominant.toUpperCase()} VOICE LEADS]\n\n${present}\n\n[Echoes:]\nFrom what was: ${past.slice(0,120)}...\nFrom what could be: ${future.slice(0,120)}...`;
    return { past, present, future, unified_weave };
  }

  weightFor(hexagram) {
    return this.weights[String(hexagram.id)] || { chaos:0, whimsy:0, darkTone:0, coherence:0, voiceWeight:0 };
  }
}

export class OracleEngine {
  constructor(config = {}) {
    this.config = {
      tick_interval_ms: 640,
      deterministic: true,
      emotional_smoothing: 0.1,
      ...config,
    };
    this.tick = 0;
    this.parser = new EmotionalParser();
    this.narrative = new NarrativeEngine();
    this.registry = new Map();
  }

  loadRegistry(registryJson) {
    for (const [id, record] of Object.entries(registryJson)) {
      this.registry.set(Number(id), ensureHexagramState(id, record));
    }
  }

  loadReflections(reflectionsJson, weightsJson) {
    this.narrative = new NarrativeEngine(reflectionsJson || {}, weightsJson || {});
  }

  async consult(query = {}) {
    const emotional = this.parser.parse(query);
    const temporal = createTemporalState(this.tick++, query.emotional_input ?? 50);
    const selector = 'sovereign';
    const id = await this.selectHexagramId(query, selector);
    const hexagram = this.registry.get(id);
    if (!hexagram) throw new Error(`Invalid hexagram ID: ${id}`);
    const reflections = this.narrative.generateReflections(hexagram, temporal, emotional);
    const target = this.narrative.weightFor(hexagram);
    const emotionalDeltas = emotionalDelta(emotional, target);
    const action = hexagram.action || 'WAIT';
    const category = hexagram.category || 'transformer';
    return {
      hexagram_id: hexagram.id,
      hexagram_name: hexagram.name,
      hexagram_unicode: hexagram.unicode,
      temporal_phase: temporal.dominantPhase,
      temporal_substate: temporal.substate,
      past_reflection: reflections.past,
      present_reflection: reflections.present,
      future_reflection: reflections.future,
      unified_weave: reflections.unified_weave,
      sovereign_assertion: `[${action}] ${hexagram.name} — temporal phase ${temporal.dominantPhase}`,
      boundary_condition: `Boundary: ${category} | Action: ${action} | Phase: ${temporal.substate}`,
      dissipator_warning: category === 'dissipator' ? `Energy drain risk in phase ${temporal.dominantPhase}` : 'Stable energy profile',
      action,
      category,
      emotional_deltas: emotionalDeltas,
      state_str: query.state_str,
    };
  }

  async selectHexagramId(query, selector) {
    if (this.config.deterministic) {
      const previousHex = 1;
      const hash = await import('../utils/DeterministicHash.js');
      return await hash.deterministicHexagramSelect(this.tick, query.session_id || 'default', previousHex, selector);
    }
    throw new Error('Weighted selection not yet implemented');
  }
}
