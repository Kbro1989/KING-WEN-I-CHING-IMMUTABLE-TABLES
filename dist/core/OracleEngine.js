const DEFAULT_LOCAL_URL = 'http://127.0.0.1:8765/expand';
const REQUEST_TIMEOUT_MS = 60_000;
export class LocalOracleClient {
    url;
    constructor(options = {}) {
        this.url = options.url || DEFAULT_LOCAL_URL;
    }
    async consult(query) {
        const body = {
            emotional_input: query.emotional_input ?? 50,
            session_id: query.session_id || 'anon',
            text: query.text || '',
        };
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
        let response;
        try {
            response = await fetch(this.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
                signal: controller.signal,
            });
        }
        catch (error) {
            throw new Error(`Local oracle engine unreachable at ${this.url}: ${error}`);
        }
        finally {
            clearTimeout(timeout);
        }
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Local oracle engine error ${response.status}: ${text}`);
        }
        const payload = await response.json();
        return mapExpandResponse(payload, query);
    }
    loadRegistry() {
        // No-op compatibility shim. Registry is owned by the local Python engine.
    }
    loadReflections() {
        // No-op compatibility shim. Reflections are owned by the local Python engine.
    }
    async evaluateForConsult(_env, _tick, sessionId, queryText) {
        const response = await this.consult({
            text: queryText,
            session_id: sessionId,
            emotional_input: 50,
        });
        return {
            oracleState: {
                sessionId,
                tick: _tick,
                evaluatedPaths: [response.hexagram_id],
                emotionalPool: { source: 'local-expand-server' },
            },
            consoleResolve: {
                resolvedEmotion: response.emotional_deltas,
                temporalContexts: [response.temporal_phase],
                unifiedAnswer: response.unified_weave,
                categorySubset: [response.category],
            },
        };
    }
}
export class OracleEngine {
    client;
    constructor(config = {}) {
        this.client = new LocalOracleClient({
            url: config.localUrl || DEFAULT_LOCAL_URL,
        });
    }
    loadRegistry() {
        this.client.loadRegistry();
    }
    loadReflections() {
        this.client.loadReflections();
    }
    async consult(query = { text: '', session_id: 'anon' }) {
        return this.client.consult(query);
    }
}
function mapExpandResponse(payload, query) {
    if (!payload || !Array.isArray(payload.resolved)) {
        throw new Error(`Invalid local oracle response: missing resolved[]`);
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
    const past_reflection = String(reflections.past || `Past echo from ${symbols.name || `hexagram #${hexagram_id}`}`);
    const present_reflection = String(reflections.present || `Present voice of ${symbols.name || `hexagram #${hexagram_id}`}`);
    const future_reflection = String(reflections.future || `Future signal from ${symbols.name || `hexagram #${hexagram_id}`}`);
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
    ]
        .filter(Boolean)
        .join('\n');
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
        sovereign_assertion: `[${resolvedAction}] ${symbols.name || `Hexagram #${hexagram_id}`} — ${dominantPhaseLabel} phase`,
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
    };
}
function phaseLabel(phase) {
    return ['past', 'present', 'future'][phase] || 'present';
}
function lineSummary(lineStates, dominantLine) {
    if (!lineStates.length)
        return '';
    return ('Lines:\n' +
        lineStates
            .map((line) => {
            const pos = Number(line.position);
            const yao = line.yao_label || line.yao_key || `ternary=${line.ternary_state}`;
            const mark = dominantLine && line.position === dominantLine.position ? ' ◀' : '';
            return `L${pos}: ${yao}${mark}`;
        })
            .join('\n'));
}
function deterministicIndex(input, maxExclusive) {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
        const code = input.charCodeAt(i);
        hash = ((hash << 5) - hash + code) | 0;
    }
    return ((hash % maxExclusive) + maxExclusive) % maxExclusive;
}
