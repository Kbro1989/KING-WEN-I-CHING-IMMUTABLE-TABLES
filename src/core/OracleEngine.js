import { createTemporalState, ensureHexagramState, emotionalDelta } from '../types/oracle.js';

const DEFAULT_LOCAL_URL = 'http://127.0.0.1:8765/expand';
const REQUEST_TIMEOUT_MS = 60_000;

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
    this.localUrl = config.localUrl || DEFAULT_LOCAL_URL;
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
    if (typeof fetch === 'function') {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
        const response = await fetch(this.localUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            emotional_input: query.emotional_input ?? 50,
            session_id: query.session_id || 'anon',
            text: query.text || '',
          }),
          signal: controller.signal,
        });
        clearTimeout(timeout);
        if (response?.ok) {
          const payload = await response.json();
          if (payload && Array.isArray(payload.resolved)) {
            return mapExpandResponse(payload, query);
          }
        }
      } catch {
        // Fall back to the local registry-based path when the runtime server is unavailable.
      }
    }

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

function mapExpandResponse(payload, query = {}) {
  if (!payload || !Array.isArray(payload.resolved)) {
    throw new Error('Invalid local oracle response: missing resolved[]');
  }

  const resolved = payload.resolved;
  if (resolved.length === 0) {
    throw new Error('Local oracle response resolved[] is empty');
  }

  const index = deterministicIndex(query.session_id || 'anon', resolved.length);
  const entry = resolved[index];
  const symbols = entry.hexagram_symbols || {};
  const resolvedVector = entry.resolved_vector || {};
  const lineStates = Array.isArray(entry.line_states) ? entry.line_states : [];

  const hexagram_id = Number(symbols.hexagram_id || entry.hexagram_id || index + 1);
  if (hexagram_id < 1 || hexagram_id > 64) {
    throw new Error(`Local oracle returned invalid hexagram_id=${hexagram_id}`);
  }

  const action = String(symbols.action || 'WAIT').toUpperCase();
  const resolvedAction = ['ASSERT', 'YIELD', 'ADAPT', 'WAIT'].includes(action) ? action : 'WAIT';
  const category = String(symbols.category || 'transformer').toLowerCase();
  const resolvedCategory = ['sovereign', 'boundary', 'transformer', 'dissipator'].includes(category) ? category : 'transformer';
  const temporal_phase = Number(entry.phase_bits ?? 0);
  const temporal_substate = String(entry.phase_polarity || 'transition');
  const reflections = entry.reflections || {};
  const past_reflection = String(reflections.past || `Past echo from ${symbols.name || 'hexagram #' + hexagram_id}`);
  const present_reflection = String(reflections.present || `Present voice of ${symbols.name || 'hexagram #' + hexagram_id}`);
  const future_reflection = String(reflections.future || `Future signal from ${symbols.name || 'hexagram #' + hexagram_id}`);
  const dominantPhaseLabel = phaseLabel(temporal_phase);
  const dominantLine = lineStates.find((line) => Number(line.ternary_state) === 2) || lineStates[lineStates.length - 1];
  const unified_weave = [
    `[${dominantPhaseLabel.toUpperCase()} VOICE LEADS]`,
    '',
    present_reflection,
    '',
    '[Echoes:]',
    `From what was: ${past_reflection.slice(0, 120)}`,
    `From what could be: ${future_reflection.slice(0, 120)}`,
    '',
    `Phase: ${entry.phase_temporal || dominantPhaseLabel}`,
    `Emotional bleed: ${Number(entry.bleed ?? 0).toFixed(3)}`,
    'Resolved vector: ' + `chaos=${resolvedVector.chaos ?? 0}, ` + `whimsy=${resolvedVector.whimsy ?? 0}, ` + `darkTone=${resolvedVector.darkTone ?? 0}, ` + `coherence=${resolvedVector.coherence ?? 0}, ` + `voiceWeight=${resolvedVector.voiceWeight ?? 0}`,
    lineSummary(lineStates, dominantLine),
  ].filter(Boolean).join('\n');

  return {
    hexagram_id,
    hexagram_name: String(symbols.name || ''),
    hexagram_unicode: String(symbols.unicode || ''),
    temporal_phase,
    temporal_substate,
    past_reflection,
    present_reflection,
    future_reflection,
    unified_weave,
    sovereign_assertion: `[${resolvedAction}] ${symbols.name || 'Hexagram #' + hexagram_id} — ${dominantPhaseLabel} phase`,
    boundary_condition: `Boundary: ${resolvedCategory} | Action: ${resolvedAction} | Phase: ${entry.phase_description || dominantPhaseLabel}`,
    dissipator_warning: resolvedCategory === 'dissipator' ? `Energy drain risk in ${dominantPhaseLabel} phase` : 'Stable energy profile',
    action: resolvedAction,
    category: resolvedCategory,
    emotional_deltas: {
      chaos: Number(resolvedVector.chaos ?? 0),
      whimsy: Number(resolvedVector.whimsy ?? 0),
      darkTone: Number(resolvedVector.darkTone ?? 0),
      coherence: Number(resolvedVector.coherence ?? 0),
      voiceWeight: Number(resolvedVector.voiceWeight ?? 0),
    },
    state_str: query.state_str,
    expanded_state: Array.isArray(payload.expanded) ? payload.expanded : [],
    resolved_state: Array.isArray(payload.resolved) ? payload.resolved : [],
    runtime_consensus: payload.consensus ?? {},
    runtime_source: payload.source ?? 'local-python',
  };
}

function phaseLabel(phase) {
  return ['past', 'present', 'future'][phase] || 'present';
}

function lineSummary(lineStates, dominantLine) {
  if (!lineStates.length) return '';
  return 'Lines:\n' + lineStates.map((line) => {
    const pos = Number(line.position);
    const yao = line.yao_label || line.yao_key || `ternary=${line.ternary_state}`;
    const mark = dominantLine && line.position === dominantLine.position ? ' ◀' : '';
    return `L${pos}: ${yao}${mark}`;
  }).join('\n');
}

function deterministicIndex(input, maxExclusive) {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const code = input.charCodeAt(i);
    hash = ((hash << 5) - hash + code) | 0;
  }
  return ((hash % maxExclusive) + maxExclusive) % maxExclusive;
}
