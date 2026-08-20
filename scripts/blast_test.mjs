/**
 * blast_test.mjs — fire a real consult through OracleEngine and print hydrated JSON.
 * Verifies: no template strings, real consensus_vector from 512-state accumulator,
 * corpus-anchored reflections, full resolved[] and expanded[] present.
 */

import { OracleEngine } from '../dist/core/OracleEngine.js';

const engine = new OracleEngine({ localUrl: 'http://127.0.0.1:8765/expand' });

const query = {
  text: 'resolve the intent of this system and surface the dominant trajectory',
  session_id: 'blast-test-001',
  emotional_input: 62,
};

console.log('Firing shotgun blast...');
console.log(`  text: "${query.text}"`);
console.log(`  emotional_input: ${query.emotional_input}`);
console.log(`  session_id: ${query.session_id}`);
console.log('');

let response;
try {
  response = await engine.consult(query);
} catch (err) {
  console.error('CONSULT FAILED:', err.message);
  process.exit(1);
}

// ── Top-level identity ──────────────────────────────────────────────────────
console.log('════════════════════════════════════════════════════');
console.log('ORACLE RESPONSE — HYDRATED');
console.log('════════════════════════════════════════════════════');
console.log(`hexagram_id      : ${response.hexagram_id}`);
console.log(`hexagram_name    : ${response.hexagram_name}`);
console.log(`hexagram_unicode : ${response.hexagram_unicode}`);
console.log(`temporal_phase   : ${response.temporal_phase}  (0=past 1=present 2=future)`);
console.log(`temporal_substate: ${response.temporal_substate}`);
console.log(`action           : ${response.action}`);
console.log(`category         : ${response.category}`);

// ── Corpus reflections ──────────────────────────────────────────────────────
console.log('');
console.log('── Corpus Reflections (from temporal-reflections.json) ──');
console.log(`past     : ${response.past_reflection}`);
console.log(`present  : ${response.present_reflection}`);
console.log(`future   : ${response.future_reflection}`);

// ── unified_weave — must be corpus text, not a template ───────────────────
console.log('');
console.log('── unified_weave (consensus temporal phase corpus text) ──');
console.log(response.unified_weave);

// ── sovereign / boundary / dissipator ─────────────────────────────────────
console.log('');
console.log('── Intent Fields ──');
console.log(`sovereign_assertion : ${response.sovereign_assertion}`);
console.log(`boundary_condition  : ${response.boundary_condition}`);
console.log(`dissipator_warning  : ${response.dissipator_warning}`);

// ── Emotional deltas — must be consensus_vector, not single-entry ─────────
console.log('');
console.log('── Emotional Deltas (Gaussian accumulator across 512 states) ──');
console.log(JSON.stringify(response.emotional_deltas, null, 2));

// ── Runtime consensus block ────────────────────────────────────────────────
console.log('');
console.log('── Runtime Consensus (Python _compute_consensus_from_resolved) ──');
const c = response.runtime_consensus;
console.log(`  consensus_hexagram_id   : ${c.consensus_hexagram_id}`);
console.log(`  consensus_hexagram_name : ${c.consensus_hexagram_name}`);
console.log(`  consensus_temporal      : ${c.consensus_temporal}`);
console.log(`  consensus_yao           : ${c.consensus_yao}`);
console.log(`  total_resolved          : ${c.total_resolved}`);
console.log(`  consensus_intent        : ${c.consensus_intent}`);
console.log(`  consensus_vector        : ${JSON.stringify(c.consensus_vector)}`);
console.log(`  consensus_porosity_mean : ${c.consensus_porosity_mean}`);

// ── State counts — verify full expansion came through ─────────────────────
console.log('');
console.log('── Expansion Counts ──');
console.log(`  resolved_state length  : ${response.resolved_state?.length ?? 'MISSING'}`);
console.log(`  expanded_state length  : ${response.expanded_state?.length ?? 'MISSING'}`);
console.log(`  runtime_source         : ${response.runtime_source}`);

// ── Spot-check: first and last resolved entries ───────────────────────────
if (Array.isArray(response.resolved_state) && response.resolved_state.length > 0) {
  const first = response.resolved_state[0];
  const last  = response.resolved_state[response.resolved_state.length - 1];
  console.log('');
  console.log('── First Resolved Entry ──');
  console.log(`  hexagram_id   : ${first.hexagram_id}`);
  console.log(`  phase_temporal: ${first.phase_temporal}`);
  console.log(`  resolved_vector: ${JSON.stringify(first.resolved_vector)}`);
  console.log('── Last Resolved Entry ──');
  console.log(`  hexagram_id   : ${last.hexagram_id}`);
  console.log(`  phase_temporal: ${last.phase_temporal}`);
  console.log(`  resolved_vector: ${JSON.stringify(last.resolved_vector)}`);
}

// ── Template-string contamination check ───────────────────────────────────
console.log('');
console.log('── Contamination Checks ──');
const templatePatterns = [
  /Past echo from/,
  /Present voice of/,
  /Future signal from hexagram #/,
  /\[PAST VOICE LEADS\]/,
  /\[PRESENT VOICE LEADS\]/,
  /\[FUTURE VOICE LEADS\]/,
  /\[Echoes:\]/,
  /From what was:/,
  /From what could be:/,
  /Energy drain risk in .* phase/,
  /Stable energy profile/,
];
const textFields = [
  ['unified_weave',       response.unified_weave],
  ['sovereign_assertion', response.sovereign_assertion],
  ['boundary_condition',  response.boundary_condition],
  ['dissipator_warning',  response.dissipator_warning],
  ['past_reflection',     response.past_reflection],
  ['present_reflection',  response.present_reflection],
  ['future_reflection',   response.future_reflection],
];
let clean = true;
for (const [field, value] of textFields) {
  for (const pat of templatePatterns) {
    if (pat.test(value)) {
      console.log(`  ❌ CONTAMINATION in ${field}: matched /${pat.source}/`);
      clean = false;
    }
  }
}
if (clean) {
  console.log('  ✅ No template-string contamination detected in text fields.');
}

// ── 1-hex collapse check ───────────────────────────────────────────────────
const resolvedCount = response.resolved_state?.length ?? 0;
if (resolvedCount >= 512) {
  console.log(`  ✅ Full 512-state expansion relayed (got ${resolvedCount}).`);
} else if (resolvedCount > 1) {
  console.log(`  ⚠  Partial expansion: ${resolvedCount} resolved states (expected 512).`);
} else {
  console.log(`  ❌ 1-hex collapse detected: only ${resolvedCount} resolved state(s).`);
}

console.log('');
console.log('════════════════════════════════════════════════════');
