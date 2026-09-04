// Math Law Registry
// Every equation in the math papers must have a corresponding entry here.
// Agents cannot bypass these invariants. Violations block commits.

import { CANONICAL_MANIFEST } from './canonical_manifest.js';

export interface MathLaw {
  id: string;
  name: string;
  source: string;
  invariant: (state: unknown) => boolean;
  violationMessage: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  remediation: string;
}

export interface MathLawViolation {
  lawId: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  source: string;
  remediation: string;
}

export const MATH_LAWS: Record<string, MathLaw> = {
  'MWP-001': {
    id: 'MWP-001',
    name: 'Wave Packet Collapse',
    source: 'docs/math/wave_packet_collapse.md',
    invariant: (state: unknown) => {
      const s = state as { representation?: string; intent?: number };
      // Intent must NEVER collapse to scalar 1 on quantum representation
      if (s.representation === 'quantum' && (s.intent === 1 || s.intent === 0)) {
        return false;
      }
      return true;
    },
    violationMessage: 'Quantum state intent collapsed to scalar. Intent must remain as probability distribution over 512 states.',
    severity: 'CRITICAL',
    remediation: 'Query oracle for correct collapse behavior: /kingwen consult --domain=quantum --intent-collapse',
  },
  
  'MAP-002': {
    id: 'MAP-002',
    name: 'Audio Pellet Range',
    source: 'docs/math/audio_pellet_synthesis.md',
    invariant: (state: unknown) => {
      const s = state as { frequency?: number };
      if (s.frequency !== undefined) {
        const min = CANONICAL_MANIFEST.audio_ranges.min_frequency_hz;
        const max = CANONICAL_MANIFEST.audio_ranges.max_frequency_hz;
        if (s.frequency < min || s.frequency > max) {
          return false;
        }
      }
      return true;
    },
    violationMessage: 'Audio frequency outside canonical range [80.0, 8000.0] Hz.',
    severity: 'CRITICAL',
    remediation: 'Query AudioPelletSynthesizer.getCanonicalRanges() for correct range.',
  },
  
  'MCS-003': {
    id: 'MCS-003',
    name: 'Chromanumber Space',
    source: 'docs/math/chromanumber_color_space.md',
    invariant: (state: unknown) => {
      const s = state as { color?: string; emotionalVector?: Record<string, number> };
      if (s.color) {
        // Check if color is in canonical emotional subspace
        const mapping = CANONICAL_MANIFEST.color_space.mapping;
        const components = Object.keys(mapping);
        
        // Color must be derivable from emotional vector components
        if (!s.emotionalVector) {
          return false;
        }
        
        // Check all 5 emotional components present
        for (const comp of components) {
          if (s.emotionalVector[comp] === undefined) {
            return false;
          }
        }
      }
      return true;
    },
    violationMessage: 'Color variation outside canonical emotional subspace.',
    severity: 'HIGH',
    remediation: 'Query ChromanumberSpace.getSubspace() for correct color mapping.',
  },
  
  'MHS-004': {
    id: 'MHS-004',
    name: 'Hexagram State Count',
    source: 'docs/math/hexagram_state_space.md',
    invariant: (state: unknown) => {
      const s = state as { stateCount?: number; totalStates?: number };
      const expected = CANONICAL_MANIFEST.state_space.total_resolved_states;
      if (s.stateCount !== undefined && s.stateCount !== expected) {
        return false;
      }
      if (s.totalStates !== undefined && s.totalStates !== expected) {
        return false;
      }
      return true;
    },
    violationMessage: `State count must be exactly ${CANONICAL_MANIFEST.state_space.total_resolved_states} resolved states.`,
    severity: 'CRITICAL',
    remediation: 'Use CANONICAL_MANIFEST.state_space.total_resolved_states.',
  },
  
  'MTS-005': {
    id: 'MTS-005',
    name: 'Ternary Slot Count',
    source: 'docs/math/ternary_slot_system.md',
    invariant: (state: unknown) => {
      const s = state as { ternarySlots?: number; slotCount?: number };
      if (s.ternarySlots !== undefined && s.ternarySlots !== 6) {
        return false;
      }
      if (s.slotCount !== undefined && s.slotCount !== 6) {
        return false;
      }
      return true;
    },
    violationMessage: 'Ternary slot count must be exactly 6 (3^6 = 729 permutations).',
    severity: 'CRITICAL',
    remediation: 'Use CANONICAL_MANIFEST.state_space.ternary_permutations_per_hexagram.',
  },
};

export function runMathLaws(state: unknown): MathLawViolation[] {
  const violations: MathLawViolation[] = [];
  
  for (const [id, law] of Object.entries(MATH_LAWS)) {
    try {
      if (!law.invariant(state)) {
        violations.push({
          lawId: id,
          severity: law.severity,
          message: law.violationMessage,
          source: 'MathLawRegistry',
          remediation: law.remediation,
        });
      }
    } catch (err) {
      // Law check itself failed - this is a violation
      violations.push({
        lawId: id,
        severity: 'HIGH',
        message: `Math law ${id} check failed: ${err}`,
        source: 'MathLawRegistry',
        remediation: 'Fix state shape to match law requirements.',
      });
    }
  }
  
  return violations;
}
