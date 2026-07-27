/**
 * kingwen_shotgun_types.ts
 * TypeScript interfaces and type definitions for the King Wen 64-pellet shotgun pipeline
 * and the J-Space latent vector manifold.
 */

export type TrigramBitString = '000' | '001' | '010' | '011' | '100' | '101' | '110' | '111';
export type HexagramBinary = string; // 6-bit binary representation '000000' to '111111'
export type PorosityLabel = 'Crystallized' | 'Structured' | 'Porous' | 'Fluid' | 'Dissolved';
export type TemporalPhase = 'past' | 'present' | 'future';

export interface JSpaceVector {
  chaos: number;
  whimsy: number;
  darkTone: number;
  coherence: number;
  voiceWeight: number;
  porosity: number;
  porosityLabel: PorosityLabel;
}

export interface VoiceboxPayload {
  profile_id: string;
  preset_engine: 'qwen_custom_voice' | 'kokoro' | 'chatterbox_turbo' | 'qwen';
  instruct: string;
  design_prompt: string;
  personality: string;
  prosody: {
    speed: number;
    weight: number;
    pitch_delta: number;
  };
}

export interface MegatronPayload {
  hexagram_id: number;
  phase_bits: number;
  porosity_head_label: PorosityLabel;
  porosity_score: number;
  target_vectors: {
    chaos: number;
    whimsy: number;
    darkTone: number;
    coherence: number;
  };
  training_prompt: string;
}

export interface KimiPayload {
  hexagram_id: number;
  context_window_bias: 'expand' | 'strict';
  max_tokens_budget: number;
  multi_doc_anchor: string;
}

export interface Agency3DPayload {
  hexagram_id: number;
  category: 'Sovereign' | 'Transformer' | 'Dissipator' | 'Boundary';
  mesh_stability: number;
  porosity_label: PorosityLabel;
  camera_track_mode: 'locked' | 'dynamic_pan';
  particle_dispersion: number;
  visual_prompt: string;
}

export interface ModelProjections {
  voicebox: VoiceboxPayload;
  megatron: MegatronPayload;
  kimi: KimiPayload;
  agency_3d: Agency3DPayload;
}

export interface TemporalStances {
  past: string;
  present: string;
  future: string;
}

export interface ShotgunPellet {
  hexagram_id: number;
  binary: HexagramBinary;
  coder_name: string;
  skill_domain: string;
  risk_category: string;
  voice_profile: string;
  stances: TemporalStances;
  jspace_coordinate: JSpaceVector;
  projections: ModelProjections;
}

export interface ShotgunMatrixResponse {
  source: string;
  request_text: string;
  deterministic_hash: number;
  total_pellets: number;
  total_perspectives: number; // 64 x 3 = 192 perspectives
  pellets: ShotgunPellet[];
  selected_counsel_pellets?: ShotgunPellet[];
}
