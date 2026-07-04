import { EmotionalParser } from '../parser/EmotionalParser.js';
import { NarrativeEngine } from '../parser/NarrativeEngine.js';
import { computeTemporalPhase, phaseToString } from '../utils/TemporalMath.js';
import { deterministicHexagramSelect } from '../utils/DeterministicHash.js';
import registryJson from '../../data/hexagram-registry.json' with { type: 'json' };
import weightsJson from '../../data/emotional-weights.json' with { type: 'json' };
import reflectionsJson from '../../data/temporal-reflections.json' with { type: 'json' };
export class OracleEngine {
    config;
    emotionalParser;
    narrativeEngine;
    hexagramRegistry;
    tick = 0;
    constructor(config = {}) {
        this.config = {
            tick_interval_ms: 640,
            deterministic: true,
            emotional_smoothing: 0.1,
            ...config,
        };
        this.emotionalParser = new EmotionalParser();
        this.narrativeEngine = new NarrativeEngine(reflectionsJson, weightsJson);
        this.hexagramRegistry = new Map();
        for (const [id, data] of Object.entries(registryJson)) {
            this.hexagramRegistry.set(parseInt(id), { id: parseInt(id), ...data });
        }
    }
    async consult(query) {
        const emotionalState = this.emotionalParser.parse(query);
        const temporal = computeTemporalPhase(this.tick++, query.emotional_input ?? 50);
        const hexagram = await this.selectHexagram(query, emotionalState, temporal);
        const reflections = this.narrativeEngine.generateReflections(hexagram, temporal, emotionalState);
        const emotionalDeltas = this.computeEmotionalDeltas(hexagram, emotionalState);
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
            sovereign_assertion: this.generateSovereignAssertion(hexagram, temporal),
            boundary_condition: this.generateBoundaryCondition(hexagram, temporal),
            dissipator_warning: this.generateDissipatorWarning(hexagram, temporal),
            action: hexagram.action,
            category: hexagram.category,
            emotional_deltas: emotionalDeltas,
            state_str: query.state_str,
        };
    }
    async selectHexagram(query, emotional, temporal) {
        if (this.config.deterministic) {
            const previousHex = 1;
            const id = await deterministicHexagramSelect(this.tick, query.session_id, previousHex, 'sovereign');
            const hex = this.hexagramRegistry.get(id);
            if (!hex)
                throw new Error(`Invalid hexagram ID: ${id}`);
            return hex;
        }
        throw new Error('Weighted selection not yet implemented');
    }
    computeEmotionalDeltas(hexagram, current) {
        const weights = weightsJson[hexagram.id.toString()];
        if (!weights)
            return { chaos: 0, whimsy: 0, darkTone: 0, coherence: 0, voiceWeight: 0 };
        return {
            chaos: weights.chaos - current.chaos,
            whimsy: weights.whimsy - current.whimsy,
            darkTone: weights.darkTone - current.darkTone,
            coherence: weights.coherence - current.coherence,
            voiceWeight: weights.voiceWeight - current.voiceWeight,
        };
    }
    generateSovereignAssertion(hexagram, temporal) {
        return `[${hexagram.action}] ${hexagram.name} — ${phaseToString(temporal.dominantPhase)} phase`;
    }
    generateBoundaryCondition(hexagram, temporal) {
        return `Boundary: ${hexagram.category} | Action: ${hexagram.action} | Phase: ${temporal.substate}`;
    }
    generateDissipatorWarning(hexagram, temporal) {
        return hexagram.category === 'dissipator'
            ? `Energy drain risk in ${phaseToString(temporal.dominantPhase)} phase`
            : `Stable energy profile`;
    }
}
