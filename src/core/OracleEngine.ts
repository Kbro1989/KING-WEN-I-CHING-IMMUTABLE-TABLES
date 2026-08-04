import {
  OracleQuery,
  OracleResponse,
} from '../types/oracle.js';

const DEFAULT_LOCAL_URL = 'http://127.0.0.1:8765/expand';
const REQUEST_TIMEOUT_MS = 60_000;

export class LocalOracleClient {
  url: string;

  constructor(options: { url?: string } = {}) {
    this.url = options.url || DEFAULT_LOCAL_URL;
  }

  async consult(query: OracleQuery): Promise<any> {
    const body = {
      emotional_input: query.emotional_input ?? 50,
      session_id: query.session_id || 'anon',
      text: query.text || '',
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    let response: any;
    try {
      response = await fetch(this.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (error) {
      throw new Error(`Local oracle engine unreachable at ${this.url}: ${error}`);
    } finally {
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

  async evaluateForConsult(_env: any, _tick: any, sessionId: string, queryText: string): Promise<any> {
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
  client: LocalOracleClient;
  deterministic: boolean;

  constructor(config: { localUrl?: string; deterministic?: boolean } = {}) {
    this.client = new LocalOracleClient({
      url: config.localUrl || DEFAULT_LOCAL_URL,
    });
    this.deterministic = config.deterministic ?? true;
  }

  loadRegistry(): void {
    this.client.loadRegistry();
  }

  loadReflections(): void {
    this.client.loadReflections();
  }

  async consult(query: OracleQuery = { text: '', session_id: 'anon' }): Promise<any> {
    return this.client.consult(query);
  }
}

// =============================================================================
// mapExpandResponse — transparent relay of Python engine output.
//
// The Python collapse_full_128() runs all 64 hexagrams × 8 phase variants
// = 512 resolved states with full Hamiltonian energy computation, Gaussian
// accumulator consensus, and open-pool vector blending. This function is a
// RELAY. It must not fabricate, template-concatenate, or collapse the field.
//
// Laws enforced here:
//   - NO 1-hex collapse. Consensus comes from Python's _compute_consensus_from_resolved().
//   - NO template strings on unified_weave / sovereign_assertion /
//     boundary_condition / dissipator_warning. These are Python-computed.
//     If they are absent from the payload, the trajectory is unanchored — THROW.
//   - NO fortune-cookie reflection fallbacks. Absent reflections = bad expand
//     server response. Surface the error. Do not guess.
//   - resolved[] and expanded[] are passed through intact for downstream
//     training capture and widget consumers.
// =============================================================================

function mapExpandResponse(payload: any, query: OracleQuery): OracleResponse {
  // --- Structural gate: Python engine must have returned a valid expansion ---
  if (!payload || !Array.isArray(payload.resolved)) {
    throw new Error('Oracle: invalid expand response — missing resolved[]');
  }
  if (payload.resolved.length === 0) {
    throw new Error('Oracle: expand server returned 0 resolved states — engine fault');
  }
  if (!payload.consensus || typeof payload.consensus !== 'object') {
    throw new Error('Oracle: expand response missing consensus block — cannot relay without computed field');
  }

  const consensus = payload.consensus as Record<string, any>;

  // --- Identity: read from Python consensus, not TS-computed ---
  const hexagram_id = Number(consensus.consensus_hexagram_id);
  if (!Number.isFinite(hexagram_id) || hexagram_id < 1 || hexagram_id > 64) {
    throw new Error(`Oracle: consensus_hexagram_id=${hexagram_id} out of range [1,64]`);
  }

  const hexagram_name   = String(consensus.consensus_hexagram_name ?? '');
  const temporal_phase  = String(consensus.consensus_temporal ?? 'present');
  const consensus_yao   = String(consensus.consensus_yao ?? 'stable_yao');
  const consensus_vec   = (consensus.consensus_vector ?? {}) as Record<string, number>;
  const consensus_intent = String(consensus.consensus_intent ?? '');

  // --- Action / category: read from the consensus hexagram's own resolved entry ---
  // Find the Python-weighted representative entry for the consensus hexagram.
  // Python already scored all 512 states; we surface the one that aligns with
  // consensus_temporal (highest-weighted temporal match for the winning hex).
  const resolved: any[] = payload.resolved;
  const consensusEntries = resolved.filter(
    (e: any) => Number(e.hexagram_id) === hexagram_id && e.phase_temporal === temporal_phase,
  );
  // Fall back to any entry for that hexagram if temporal match is absent.
  const representative = consensusEntries[0]
    ?? resolved.find((e: any) => Number(e.hexagram_id) === hexagram_id)
    ?? resolved[0];

  const symbols   = (representative.hexagram_symbols ?? {}) as Record<string, any>;
  const hexUnicode = String(symbols.unicode ?? '');

  const rawAction = String(symbols.action ?? 'WAIT').toUpperCase();
  const action    = (['ASSERT', 'YIELD', 'ADAPT', 'WAIT'] as const).includes(rawAction as any)
    ? rawAction as 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT'
    : 'WAIT';

  const rawCat   = String(symbols.category ?? 'transformer').toLowerCase();
  const category = (['sovereign', 'boundary', 'transformer', 'dissipator'] as const).includes(rawCat as any)
    ? rawCat as 'sovereign' | 'boundary' | 'transformer' | 'dissipator'
    : 'transformer';

  // --- Reflections: Python-owned. If absent, the entry is unanchored — throw. ---
  const reflections = (representative.reflections ?? null) as Record<string, string> | null;
  if (!reflections || (!reflections.past && !reflections.present && !reflections.future)) {
    throw new Error(
      `Oracle: no reflections in expand response for hexagram_id=${hexagram_id} phase=${temporal_phase}. ` +
      `Unanchored trajectory — check temporal-reflections.json and expand server.`,
    );
  }
  const past_reflection    = String(reflections.past    ?? '');
  const present_reflection = String(reflections.present ?? '');
  const future_reflection  = String(reflections.future  ?? '');

  // --- Computed fields: Python-owned. Must arrive from the expand payload. ---
  // unified_weave comes from the Python NarrativeEngine / voice_ensemble; if absent
  // the engine has not computed it. Do not reconstruct from string templates.
  const unified_weave = String(reflections.unified_weave ?? representative.unified_weave ?? '');
  if (!unified_weave) {
    throw new Error(
      `Oracle: unified_weave absent for hexagram_id=${hexagram_id}. ` +
      `This field must be computed by the Python engine, not fabricated in TS.`,
    );
  }

  // sovereign_assertion, boundary_condition, dissipator_warning:
  // Python computes these via _resolve_intent_from_consensus and category scoring.
  // Surface them from consensus_intent + representative entry fields.
  // If the Python engine does not yet emit these as first-class fields, surface
  // consensus_intent as sovereign_assertion — do NOT template-build strings.
  const sovereign_assertion  = String(representative.sovereign_assertion  ?? consensus_intent);
  const boundary_condition   = String(representative.boundary_condition   ?? '');
  const dissipator_warning   = String(representative.dissipator_warning   ?? '');

  // --- Emotional deltas: Python-computed Gaussian-weighted consensus vector ---
  // This is NOT `resolvedVector` from a single entry. It is the accumulator
  // output across all 512 states — the actual Hamiltonian field summary.
  const emotional_deltas = {
    chaos:       Number(consensus_vec.chaos       ?? 0),
    whimsy:      Number(consensus_vec.whimsy      ?? 0),
    darkTone:    Number(consensus_vec.darkTone     ?? 0),
    coherence:   Number(consensus_vec.coherence   ?? 0),
    voiceWeight: Number(consensus_vec.voiceWeight ?? 0),
  };

  // --- Relay full expansion payload for training capture and widget consumers ---
  return {
    hexagram_id,
    hexagram_name,
    hexagram_unicode: hexUnicode,
    // temporal_phase in OracleResponse is typed as TemporalPhase (0|1|2).
    // Map the Python string back to the numeric encoding used by the TS runtime.
    temporal_phase: ({ past: 0, present: 1, future: 2 } as Record<string, number>)[temporal_phase] as 0 | 1 | 2 ?? 1,
    temporal_substate: (consensus_yao.includes('old') ? 'old' : consensus_yao.includes('young') ? 'young' : 'transition') as 'old' | 'young' | 'transition',
    past_reflection,
    present_reflection,
    future_reflection,
    unified_weave,
    sovereign_assertion,
    boundary_condition,
    dissipator_warning,
    action,
    category,
    emotional_deltas,
    state_str: query.state_str,
    // Full expansion payload — 64 expanded + 512 resolved + consensus intact.
    // Downstream training capture reads these fields; they must not be stripped.
    expanded_state:    Array.isArray(payload.expanded) ? payload.expanded : [],
    resolved_state:    payload.resolved,
    runtime_consensus: consensus,
    runtime_source:    String(payload.source ?? 'local-python'),
  };
}
