export type MaskState = 'PASS' | 'MEASURE' | 'SEVER' | 'ZERO_ROT' | 'ATTENTION';

export interface MaskingEntry {
  hexagram_id: number;
  paper_count: number;
  masking_default: MaskState;
  assignment_rule: string;
  live_corpus_driven: boolean;
}

export interface MaskingPayload {
  schema_version: string;
  description: string;
  corpus: {
    total_papers: number;
    populated_hexes: number;
    void_hexes: number[];
  };
  rules: Record<string, string>;
  full_64_masking_map: MaskingEntry[];
}

export interface MaskResolution {
  hexagramId: number;
  mask: MaskState;
  rule: string;
  source: 'json' | 'default_override' | 'runtime_override';
}

const MASK_COLORS: Record<MaskState, string> = {
  PASS: '#16a34a',
  MEASURE: '#2563eb',
  SEVER: '#dc2626',
  ZERO_ROT: '#475569',
  ATTENTION: '#d97706'
};

const MASK_LABELS: Record<MaskState, string> = {
  PASS: 'Pass / Full Expressibility',
  MEASURE: 'Measure / Observe Only',
  SEVER: 'Sever / Suppress Boundary',
  ZERO_ROT: 'Zero Rotation / Hold State',
  ATTENTION: 'Attention / Weighted Amplify'
};

const OVERRIDE_3D_HEXES = new Set([52, 53]);
const SINGULARITY_THRESHOLD = 100;
const MID_TIER_MIN = 30;
const ADVERSARIAL_SEVER_MAX = 50;

export class QuantumMaskSelector {
  private map: Map<number, MaskingEntry>;
  private payload: MaskingPayload;
  private runtimeOverrides: Map<number, MaskState>;

  constructor(payload: MaskingPayload) {
    this.payload = payload;
    this.map = new Map(payload.full_64_masking_map.map(e => [e.hexagram_id, e]));
    this.runtimeOverrides = new Map();
  }

  static fromJson(json: unknown): QuantumMaskSelector {
    const payload = json as MaskingPayload;
    if (!payload.full_64_masking_map || payload.full_64_masking_map.length !== 64) {
      throw new Error(`QuantumMaskSelector requires 64-entry full_64_masking_map; got ${payload.full_64_masking_map?.length ?? 0}`);
    }
    return new QuantumMaskSelector(payload);
  }

  static defaultTier(paperCount: number, hexagramId: number, isAdversarialMember: boolean): MaskState {
    if (paperCount === 0) return 'MEASURE';
    if (OVERRIDE_3D_HEXES.has(hexagramId)) return 'PASS';
    if (paperCount >= SINGULARITY_THRESHOLD) return 'PASS';
    if (isAdversarialMember && paperCount > 0 && paperCount < ADVERSARIAL_SEVER_MAX) return 'SEVER';
    if (paperCount >= MID_TIER_MIN) return 'ATTENTION';
    if (paperCount >= 20 && !isAdversarialMember) return 'ATTENTION';
    return 'ZERO_ROT';
  }

  setRuntimeOverride(hexagramId: number, mask: MaskState): void {
    this.runtimeOverrides.set(hexagramId, mask);
  }

  clearRuntimeOverride(hexagramId: number): void {
    this.runtimeOverrides.delete(hexagramId);
  }

  resolve(hexagramId: number, paperCount?: number, adversarialPairId?: string): MaskResolution {
    const entry = this.map.get(hexagramId);
    if (!entry) {
      return {
        hexagramId,
        mask: QuantumMaskSelector.defaultTier(paperCount ?? 0, hexagramId, false),
        rule: 'fallback_default_tier',
        source: 'default_override'
      };
    }

    const runtime = this.runtimeOverrides.get(hexagramId);
    if (runtime) {
      return {
        hexagramId,
        mask: runtime,
        rule: 'runtime_override',
        source: 'runtime_override'
      };
    }

    return {
      hexagramId,
      mask: entry.masking_default,
      rule: entry.assignment_rule,
      source: 'json'
    };
  }

  getColor(mask: MaskState): string {
    return MASK_COLORS[mask];
  }

  getLabel(mask: MaskState): string {
    return MASK_LABELS[mask];
  }

  getPayload(): MaskingPayload {
    return this.payload;
  }

  getMap(): Map<number, MaskingEntry> {
    return this.map;
  }
}
