// Canonical Manifest - Live Runtime Source of Truth
// Generated from shotgun_expand() - agents cannot argue with this.

export const CANONICAL_MANIFEST = {
  version: "1.0.0",
  generated_from: "live_runtime",
  source: "shotgun_expand(emotional_input=50)",
  timestamp: "2026-09-02T00:00:00Z",
  
  state_space: {
    total_hexagrams: 64,
    phases_per_hexagram: 8,
    total_resolved_states: 512,
    ternary_permutations_per_hexagram: 729,
    total_ternary_permutations: 46656,
    description: "64 hexagrams x 8 phases = 512 resolved states. 64 x 729 = 46,656 ternary permutations."
  },
  
  audio_ranges: {
    min_frequency_hz: 80.0,
    max_frequency_hz: 8000.0,
    canonical_fundamental_range: [108.0, 174.6],
    harmonics: [108.0, 118.9, 130.9, 144.1, 158.6, 174.6],
    description: "Audio pellet frequency range derived from live synthesizer. 6-yao harmonic series."
  },
  
  color_space: {
    subspace: "emotional_5axis",
    components: ["chaos", "whimsy", "darkTone", "coherence", "voiceWeight"],
    mapping: {
      chaos: { h_range: [0, 60], s_range: [0.7, 1.0], v_range: [0.5, 0.8] },
      whimsy: { h_range: [180, 240], s_range: [0.5, 0.8], v_range: [0.7, 1.0] },
      darkTone: { h_range: [270, 330], s_range: [0.3, 0.6], v_range: [0.2, 0.5] },
      coherence: { h_range: [90, 150], s_range: [0.4, 0.7], v_range: [0.6, 0.9] },
      voiceWeight: { h_range: [30, 90], s_range: [0.6, 0.9], v_range: [0.7, 1.0] }
    },
    description: "All 5 emotional vector components must map to canonical color subspace. No invented colors."
  },
  
  quantum: {
    representation: "distribution",
    intent_type: "probability_distribution_over_512_states",
    collapse_forbidden: true,
    min_states: 512,
    max_states: 512,
    ternary_permutations: 729,
    description: "Intent must NEVER collapse to scalar 1 on quantum representation. Intent is always a distribution over 512 states."
  },
  
  invariants: {
    hexagram_count: 64,
    phase_count: 8,
    resolved_state_count: 512,
    ternary_permutation_count: 729,
    total_ternary_permutations: 46656,
    emotional_vector_components: 5,
    audio_frequency_range: [80.0, 8000.0],
    canonical_fundamental_range: [108.0, 174.6]
  },
  
  forbidden_actions: [
    "collapse_quantum_intent_to_scalar",
    "invent_audio_frequency_outside_range",
    "invent_color_outside_subspace",
    "reduce_state_count_below_512",
    "reduce_ternary_slots_below_6",
    "ignore_canonical_manifest",
    "bypass_validation_gate"
  ],
  
  agent_requirements: {
    must_query_canonical_manifest: true,
    must_verify_constants_against_manifest: true,
    must_include_lineage_hash: true,
    must_pass_validation_gate: true,
    must_obey_math_laws: true
  }
} as const;
