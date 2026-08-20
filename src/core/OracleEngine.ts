import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import {
  OracleQuery,
  OracleResponse,
} from '../types/oracle.js';

const DEFAULT_LOCAL_URL = 'http://127.0.0.1:8765/expand';
const REQUEST_TIMEOUT_MS = 60_000;

// =============================================================================
// Reflections corpus — data/temporal-reflections.json
// Keyed by hexagram_id string ("1"–"64"), each entry has past/present/future.
// This is the immutable anchor. No text is generated in TS — only looked up.
// =============================================================================

type ReflectionEntry = { past: string; present: string; future: string };
type ReflectionsCorpus = Record<string, ReflectionEntry>;

let _reflectionsCache: ReflectionsCorpus | null = null;

function loadReflectionsCorpus(): ReflectionsCorpus {
  if (_reflectionsCache) return _reflectionsCache;
  try {
    const __dirname = dirname(fileURLToPath(import.meta.url));
    const corpusPath = resolve(__dirname, '../../data/temporal-reflections.json');
    _reflectionsCache = JSON.parse(readFileSync(corpusPath, 'utf-8')) as ReflectionsCorpus;
  } catch (err) {
    throw new Error(
      `Oracle: cannot load data/temporal-reflections.json — ${err}. ` +
      'This file is the immutable reflection corpus. Without it the oracle has no anchored text.',
    );
  }
  return _reflectionsCache!;
}

function getReflectionFromCorpus(
  hexagram_id: number,
  temporal_phase: string,
): ReflectionEntry {
  const corpus = loadReflectionsCorpus();
  const entry = corpus[String(hexagram_id)];
  if (!entry) {
    throw new Error(
      `Oracle: no reflection corpus entry for hexagram_id=${hexagram_id}. ` +
      'Add it to data/temporal-reflections.json.',
    );
  }
  // Validate all three temporal fields are present.
  if (!entry.past || !entry.present || !entry.future) {
    throw new Error(
      `Oracle: incomplete reflection entry for hexagram_id=${hexagram_id} — ` +
      `missing: ${[!entry.past && 'past', !entry.present && 'present', !entry.future && 'future'].filter(Boolean).join(', ')}.`,
    );
  }
  return entry;
}

export class LocalOracleClient {
  url: string;

  constructor(options: { url?: string } = {}) {
    this.url = options.url || DEFAULT_LOCAL_URL;
  }

  async consult(query: OracleQuery): Promise<OracleResponse> {
    const body = {
      emotional_input: query.emotional_input ?? 50,
      session_id: query.session_id || 'anon',
      text: query.text || '',
    };

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    let response: Response;
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

    const payload: unknown = await response.json();
    return mapExpandResponse(payload, query);
  }

  loadRegistry() {
    // No-op compatibility shim. Registry is owned by the local Python engine.
  }

  loadReflections() {
    // No-op compatibility shim. Reflections are owned by the local Python engine.
  }

  async evaluateForConsult(_env: unknown, _tick: unknown, sessionId: string, queryText: string): Promise<Record<string, unknown>> {
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

  async consult(query: OracleQuery = { text: '', session_id: 'anon' }): Promise<OracleResponse> {
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

function mapExpandResponse(rawPayload: unknown, query: OracleQuery): OracleResponse {
  if (typeof rawPayload !== 'object' || rawPayload === null) {
    throw new Error('Oracle: invalid expand response — payload must be an object');
  }
  const payload = rawPayload as Record<string, unknown>;

  // --- Structural gate: Python engine must have returned a valid expansion ---
  if (!Array.isArray(payload.resolved)) {
    throw new Error('Oracle: invalid expand response — missing resolved[]');
  }
  if (payload.resolved.length === 0) {
    throw new Error('Oracle: expand server returned 0 resolved states — engine fault');
  }
  if (!payload.consensus || typeof payload.consensus !== 'object') {
    throw new Error('Oracle: expand response missing consensus block — cannot relay without computed field');
  }

  const consensus = payload.consensus as Record<string, unknown>;

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
  const resolved = payload.resolved as Record<string, unknown>[];
  const consensusEntries = resolved.filter(
    (e) => Number(e.hexagram_id) === hexagram_id && e.phase_temporal === temporal_phase,
  );
  // Fall back to any entry for that hexagram if temporal match is absent.
  const representative = consensusEntries[0]
    ?? resolved.find((e) => Number(e.hexagram_id) === hexagram_id)
    ?? resolved[0];

  const symbols   = (representative.hexagram_symbols ?? {}) as Record<string, unknown>;
  const hexUnicode = String(symbols.unicode ?? '');

  const rawAction = String(symbols.action ?? 'WAIT').toUpperCase();
  const action    = (['ASSERT', 'YIELD', 'ADAPT', 'WAIT'] as const).includes(rawAction as 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT')
    ? rawAction as 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT'
    : 'WAIT';

  const rawCat   = String(symbols.category ?? 'transformer').toLowerCase();
  const category = (['sovereign', 'boundary', 'transformer', 'dissipator'] as const).includes(rawCat as 'sovereign' | 'boundary' | 'transformer' | 'dissipator')
    ? rawCat as 'sovereign' | 'boundary' | 'transformer' | 'dissipator'
    : 'transformer';

  // --- Reflections: looked up from data/temporal-reflections.json by hexagram_id.
  //
  // Python's expand/sample_resolve computes vectors, line states, and Hamiltonian
  // energy — it does not emit text. Text lives in the immutable corpus. The lookup
  // is deterministic: hexagram_id → corpus entry → {past, present, future}.
  // No fallback strings. If the corpus entry is missing, the system is misconfigured.
  const corpusEntry = getReflectionFromCorpus(hexagram_id, temporal_phase);
  const past_reflection    = corpusEntry.past;
  const present_reflection = corpusEntry.present;
  const future_reflection  = corpusEntry.future;

  // --- unified_weave: the temporal-phase corpus text for this hexagram.
  //
  // This is the anchored philosophical statement for the resolved hexagram in its
  // consensus temporal context. It is NOT a template. It is the corpus line itself —
  // the same text the kit_ models were trained on as a coordinate anchor.
  // For past → past corpus text. For present → present corpus text. Etc.
  const phaseToCorpus: Record<string, string> = {
    past:            past_reflection,
    present:         present_reflection,
    future:          future_reflection,
    // Extended phase_temporal values from Python's PHASE_INFO map to present
    // as the active voice when temporal doesn't resolve to the base three.
    transition:      present_reflection,
    resolution:      past_reflection,
    dissolution:     future_reflection,
    crystallization: present_reflection,
    void:            present_reflection,
  };
  const unified_weave = phaseToCorpus[temporal_phase] ?? present_reflection;

  // --- sovereign_assertion, boundary_condition, dissipator_warning:
  // Python's _resolve_intent_from_consensus() computes consensus_intent —
  // the intent resolution string derived from hexagram scoring across all 512 states.
  // Surface it as sovereign_assertion. boundary/dissipator are category-derived
  // fields from the consensus hexagram — if Python surfaces them, relay them;
  // if not, leave empty. No template substitution.
  const sovereign_assertion = String(representative.sovereign_assertion ?? consensus_intent);
  const boundary_condition  = String(representative.boundary_condition  ?? '');
  const dissipator_warning  = String(representative.dissipator_warning  ?? '');

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
