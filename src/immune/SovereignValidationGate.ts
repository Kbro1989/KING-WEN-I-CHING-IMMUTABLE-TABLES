// Sovereign Validation Gate
// All agent-generated code must pass through this gate before reaching any branch.
// The gate maintains the Canonical Manifest as single source of truth.

import { CANONICAL_MANIFEST } from './canonical_manifest.js';
import { runMathLaws, MathLawViolation } from './MathLawRegistry.js';

export interface ValidationResult {
  passed: boolean;
  violations: SovereignViolation[];
  lineageHash: string;
  timestamp: number;
}

export interface SovereignViolation {
  lawId: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  source: string;
  remediation: string;
}

export class SovereignValidationGate {
  private manifest: typeof CANONICAL_MANIFEST;

  constructor() {
    this.manifest = CANONICAL_MANIFEST;
  }

  /**
   * Validate agent-generated code against the Canonical Manifest.
   * Any code that references a constant not present in the manifest is rejected.
   */
  validate(code: string, agentId: string): ValidationResult {
    const violations: SovereignViolation[] = [];

    // 1. Check for invented constants
    const inventedConstants = this.detectInventedConstants(code);
    for (const constant of inventedConstants) {
      violations.push({
        lawId: 'MHS-004',
        severity: 'CRITICAL',
        message: `Invented constant "${constant.name}" not found in Canonical Manifest`,
        source: agentId,
        remediation: `Query Canonical Manifest for correct value: ${constant.name}`,
      });
    }

    // 2. Check for quantum intent collapse
    if (this.detectQuantumCollapse(code)) {
      violations.push({
        lawId: 'MWP-001',
        severity: 'CRITICAL',
        message: 'Quantum state intent collapsed to scalar. Intent must remain as probability distribution over 512 states.',
        source: agentId,
        remediation: 'Refer to: docs/math/wave_packet_collapse.md. Query oracle: /kingwen consult --domain=quantum --intent-collapse',
      });
    }

    // 3. Check for audio range violations
    const audioViolations = this.detectAudioRangeViolations(code);
    for (const violation of audioViolations) {
      violations.push({
        lawId: 'MAP-002',
        severity: 'CRITICAL',
        message: `Audio frequency ${violation.frequency} outside canonical range [${this.manifest.audio_ranges.min_frequency_hz}, ${this.manifest.audio_ranges.max_frequency_hz}]`,
        source: agentId,
        remediation: `Query AudioPelletSynthesizer.getCanonicalRanges() for correct range`,
      });
    }

    // 4. Check for color subspace violations
    const colorViolations = this.detectColorSubspaceViolations(code);
    for (const violation of colorViolations) {
      violations.push({
        lawId: 'MCS-003',
        severity: 'HIGH',
        message: `Color "${violation.color}" outside canonical emotional subspace`,
        source: agentId,
        remediation: `Query ChromanumberSpace.getSubspace() for correct color mapping`,
      });
    }

    // 5. Check for state count violations
    if (this.detectStateCountViolation(code)) {
      violations.push({
        lawId: 'MHS-004',
        severity: 'CRITICAL',
        message: `State count violation. Must be exactly ${this.manifest.invariants.resolved_state_count} resolved states`,
        source: agentId,
        remediation: `Use CANONICAL_MANIFEST.state_space.total_resolved_states`,
      });
    }

    // 6. Check for ternary slot violations
    if (this.detectTernarySlotViolation(code)) {
      violations.push({
        lawId: 'MTS-005',
        severity: 'CRITICAL',
        message: `Ternary slot violation. Must be exactly ${this.manifest.invariants.ternary_permutation_count} permutations per hexagram`,
        source: agentId,
        remediation: `Use CANONICAL_MANIFEST.state_space.ternary_permutations_per_hexagram`,
      });
    }

    // 7. Check for forbidden actions
    const forbiddenActions = this.detectForbiddenActions(code);
    for (const action of forbiddenActions) {
      violations.push({
        lawId: 'FORBIDDEN',
        severity: 'CRITICAL',
        message: `Forbidden action detected: ${action}`,
        source: agentId,
        remediation: `Remove forbidden action. Query oracle for correct approach.`,
      });
    }

    // Generate lineage hash
    const lineageHash = this.generateLineageHash(code, agentId);

    return {
      passed: violations.length === 0,
      violations,
      lineageHash,
      timestamp: Date.now(),
    };
  }

  private detectInventedConstants(code: string): Array<{ name: string; value: unknown }> {
    const invented: Array<{ name: string; value: unknown }> = [];
    
    // Look for hardcoded constants that should come from manifest
    const constantPatterns = [
      /const\s+STATE_COUNT\s*=\s*(\d+)/,
      /const\s+HEXAGRAM_COUNT\s*=\s*(\d+)/,
      /const\s+PHASE_COUNT\s*=\s*(\d+)/,
      /const\s+AUDIO_MIN\s*=\s*([\d.]+)/,
      /const\s+AUDIO_MAX\s*=\s*([\d.]+)/,
      /const\s+COLOR_(\w+)\s*=\s*['"]([^'"]+)['"]/,
    ];

    for (const pattern of constantPatterns) {
      const match = code.match(pattern);
      if (match) {
        invented.push({
          name: match[1],
          value: match[2],
        });
      }
    }

    return invented;
  }

  private detectQuantumCollapse(code: string): boolean {
    // Check for patterns that collapse quantum state to scalar
    const collapsePatterns = [
      /intent\s*=\s*1/,
      /intent\s*=\s*0/,
      /state\s*=\s*1/,
      /collapse.*to.*scalar/,
      /quantum.*intent\s*=\s*\d/,
    ];

    return collapsePatterns.some(pattern => pattern.test(code));
  }

  private detectAudioRangeViolations(code: string): Array<{ frequency: number }> {
    const violations: Array<{ frequency: number }> = [];
    
    // Look for audio frequency assignments
    const freqPattern = /frequency\s*:\s*([\d.]+)/g;
    let match;
    while ((match = freqPattern.exec(code)) !== null) {
      const freq = parseFloat(match[1]);
      if (freq < this.manifest.audio_ranges.min_frequency_hz || 
          freq > this.manifest.audio_ranges.max_frequency_hz) {
        violations.push({ frequency: freq });
      }
    }

    return violations;
  }

  private detectColorSubspaceViolations(code: string): Array<{ color: string }> {
    const violations: Array<{ color: string }> = [];
    
    // Look for color assignments outside emotional subspace
    const colorPattern = /color\s*:\s*['"]#?([0-9a-fA-F]{6})['"]/g;
    let match;
    while ((match = colorPattern.exec(code)) !== null) {
      const color = match[1];
      // Check if color is in canonical subspace
      if (!this.isInColorSubspace(color)) {
        violations.push({ color });
      }
    }

    return violations;
  }

  private isInColorSubspace(color: string): boolean {
    // Simplified check - in production, convert to HSV and check against mapping
    const r = parseInt(color.substring(0, 2), 16) / 255;
    const g = parseInt(color.substring(2, 4), 16) / 255;
    const b = parseInt(color.substring(4, 6), 16) / 255;
    
    // Check if within emotional vector bounds
    const chaos = Math.max(r, g, b) - Math.min(r, g, b);
    const coherence = (r + g + b) / 3;
    
    return chaos <= 0.5 && coherence >= 0.3;
  }

  private detectStateCountViolation(code: string): boolean {
    const stateCountPattern = /stateCount\s*[=:]\s*(\d+)/;
    const match = code.match(stateCountPattern);
    if (match) {
      const count = parseInt(match[1]);
      return count !== this.manifest.invariants.resolved_state_count;
    }
    return false;
  }

  private detectTernarySlotViolation(code: string): boolean {
    const slotPattern = /ternarySlots\s*[=:]\s*(\d+)/;
    const match = code.match(slotPattern);
    if (match) {
      const count = parseInt(match[1]);
      return count !== 6;
    }
    return false;
  }

  private detectForbiddenActions(code: string): string[] {
    const found: string[] = [];
    for (const action of this.manifest.forbidden_actions) {
      if (code.includes(action)) {
        found.push(action);
      }
    }
    return found;
  }

  private generateLineageHash(code: string, agentId: string): string {
    // Generate hash from code + agent + manifest version
    const data = `${code}:${agentId}:${this.manifest.version}`;
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

export const sovereignValidationGate = new SovereignValidationGate();
