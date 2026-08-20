/**
 * SovereignNPC — Interface & Parser for King Wen 64 Sovereign Model NPCs.
 * Maps kit_*.json metadata to 3D runtime SovereignNPC instance properties.
 */

export interface SovereignNPC {
  kitId: number;
  hexagramId: number;
  codename: string;
  name: string;
  category: 'sovereign' | 'boundary' | 'transformer' | 'dissipator';
  action: 'ASSERT' | 'YIELD' | 'ADAPT' | 'WAIT';
  agentType: string;
  domain: string;
  elementSubset: string;
  kColorMap: {
    blendedHex: string;
    primaryHex?: string;
    secondaryHex?: string;
  };
  schauberger: {
    vortexTension: number;
    motionMode: 'centripetal' | 'centrifugal';
    implosionScore: number;
  };
  oracleState: {
    stateFidelity: number;
    action: string;
    porosity: number;
    porosityLabel: string;
  };
  hermesLayer: {
    voiceMode: string;
  };
}

export function parseKitToNPC(json: any): SovereignNPC {
  const grounded = json.grounded_npc || json;
  const kcol = json.k_color_map || grounded.k_color_map || {};
  const schau = json.schauberger_metrics || grounded.schauberger_metrics || {};
  const oracle = json.oracle_state || grounded.oracle_state || {};
  const hermes = json.hermes_layer || grounded.hermes_layer || {};

  return {
    kitId: json.kit_id || json.hexagram_id || 1,
    hexagramId: json.hexagram_id || json.kit_id || 1,
    codename: json.codename || json.name || `Hex_${json.hexagram_id || 1}`,
    name: json.name || json.codename || `Hexagram ${json.hexagram_id || 1}`,
    category: grounded.category || json.category || 'sovereign',
    action: grounded.action || json.action || 'ASSERT',
    agentType: grounded.agent_type || json.agent_type || 'Sovereign',
    domain: grounded.domain || json.domain || 'Core',
    elementSubset: grounded.element_subset || json.element_subset || 'Prime',
    kColorMap: {
      blendedHex: kcol.blended_hex || '#FFD700',
      primaryHex: kcol.primary_hex || '#FFD700',
      secondaryHex: kcol.secondary_hex || '#4ECDC4',
    },
    schauberger: {
      vortexTension: floatVal(schau.vortex_tension, 0.4),
      motionMode: schau.motion_mode || 'centripetal',
      implosionScore: floatVal(schau.implosion_score, 0.3),
    },
    oracleState: {
      stateFidelity: floatVal(oracle.state_fidelity, 0.85),
      action: oracle.action || grounded.action || 'ASSERT',
      porosity: floatVal(oracle.porosity, 0.5),
      porosityLabel: oracle.porosity_label || 'Structured',
    },
    hermesLayer: {
      voiceMode: hermes.voice_mode || 'qwen',
    },
  };
}

function floatVal(val: any, fallback: number): number {
  const n = parseFloat(val);
  return isNaN(n) ? fallback : n;
}
