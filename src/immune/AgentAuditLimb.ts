// Agent Audit Limb
// Immune system response for external agent conformance.
// Audits all agent output before human review.

// Import the full canonical manifest from JSON (3.7MB, generated from live runtime)
// Using require for CommonJS compatibility with the JSON file
const canonicalManifest = require('./canonical_manifest.json');

import { sovereignValidationGate, ValidationResult } from './SovereignValidationGate.js';

export interface AuditResult {
  agentId: string;
  timestamp: number;
  passed: boolean;
  violations: SovereignViolation[];
  inventedConstants: Array<{ name: string; value: unknown }>;
  driftScore: number;
  kingwenHexagram: {
    id: number;
    name: string;
    emotionalVector: Record<string, number>;
    interpretation: string;
  };
  remediation: string[];
}

export interface SovereignViolation {
  lawId: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  source: string;
  remediation: string;
}

export class AgentAuditLimb {
  private role = 'External Agent Conscience';
  private category = 'IMMUNE';
  private metabolicBaseCost = 25;

  /**
   * Audit agent-generated code against the sovereign runtime.
   * Runs before any human review.
   */
  async audit(agentOutput: string, sourceAgent: string): Promise<AuditResult> {
    // 1. Run sovereign validation gate
    const validation: ValidationResult = sovereignValidationGate.validate(agentOutput, sourceAgent);

    // 2. Detect invented constants
    const invented = this.detectInventedConstants(agentOutput);

    // 3. Run math law invariants
    const mathViolations = this.runMathLaws(agentOutput);

    // 4. Measure drift from canonical
    const driftScore = this.measureDrift(agentOutput, invented);

    // 5. Generate King Wen hexagram for agent's intent
    const intentHash = this.hashAgentIntent(agentOutput);
    const hexagram = this.resolveKingWenHexagram(intentHash);

    // 6. Check for chaotic intent signature
    const violations = [...validation.violations, ...mathViolations];
    if (hexagram.emotionalVector.chaos > 0.7 && hexagram.emotionalVector.coherence < 0.3) {
      violations.push({
        lawId: 'INTENT_DRIFT',
        severity: 'CRITICAL',
        message: `Agent ${sourceAgent} produced output with chaotic intent signature. Likely hallucinated runtime.`,
        source: 'AgentAuditLimb',
        remediation: 'Consult the oracle: /kingwen agent-onboard --agent=${sourceAgent}',
      });
    }

    // 7. Generate remediation steps
    const remediation = this.generateRemediation(violations, hexagram);

    return {
      agentId: sourceAgent,
      timestamp: Date.now(),
      passed: violations.length === 0,
      violations,
      inventedConstants: invented,
      driftScore,
      kingwenHexagram: hexagram,
      remediation,
    };
  }

  private detectInventedConstants(code: string): Array<{ name: string; value: unknown }> {
    const invented: Array<{ name: string; value: unknown }> = [];
    
    // Look for hardcoded constants that should come from manifest
    const constantPatterns = [
      { pattern: /const\s+STATE_COUNT\s*=\s*(\d+)/, name: 'STATE_COUNT' },
      { pattern: /const\s+HEXAGRAM_COUNT\s*=\s*(\d+)/, name: 'HEXAGRAM_COUNT' },
      { pattern: /const\s+PHASE_COUNT\s*=\s*(\d+)/, name: 'PHASE_COUNT' },
      { pattern: /const\s+AUDIO_MIN\s*=\s*([\d.]+)/, name: 'AUDIO_MIN' },
      { pattern: /const\s+AUDIO_MAX\s*=\s*([\d.]+)/, name: 'AUDIO_MAX' },
      { pattern: /const\s+COLOR_(\w+)\s*=\s*['"]([^'"]+)['"]/, name: 'COLOR_$1' },
    ];

    for (const { pattern, name } of constantPatterns) {
      const match = code.match(pattern);
      if (match) {
        invented.push({
          name: name.replace('$1', match[1]),
          value: match[2] || match[1],
        });
      }
    }

    return invented;
  }

  private runMathLaws(code: string): SovereignViolation[] {
    const violations: SovereignViolation[] = [];
    
    // Parse code into state object for law checking
    const state = this.parseCodeToState(code);
    
    // Run quantum collapse check (MWP-001)
    if (state.representation === 'quantum' && (state.intent === 1 || state.intent === 0)) {
      violations.push({
        lawId: 'MWP-001',
        severity: 'CRITICAL',
        message: 'Quantum state intent collapsed to scalar. Intent must remain as probability distribution over 512 states.',
        source: 'AgentAuditLimb',
        remediation: 'Refer to: docs/math/wave_packet_collapse.md. Query oracle: /kingwen consult --domain=quantum --intent-collapse',
      });
    }

    // Check audio range (MAP-002)
    if (state.frequency != null) {
      const min = canonicalManifest.audio_ranges.min_frequency_hz;
      const max = canonicalManifest.audio_ranges.max_frequency_hz;
      if (state.frequency < min || state.frequency > max) {
        violations.push({
          lawId: 'MAP-002',
          severity: 'CRITICAL',
          message: `Audio frequency ${state.frequency} outside canonical range [${min}, ${max}].`,
          source: 'AgentAuditLimb',
          remediation: 'Query AudioPelletSynthesizer.getCanonicalRanges() for correct range.',
        });
      }
    }

    // Check state count (MHS-004)
    if (state.stateCount !== undefined && state.stateCount !== 512) {
      violations.push({
        lawId: 'MHS-004',
        severity: 'CRITICAL',
        message: `State count violation. Must be exactly 512 resolved states.`,
        source: 'AgentAuditLimb',
        remediation: 'Use canonicalManifest.state_space.total_resolved_states.',
      });
    }

    // Check ternary slots (MTS-005)
    if (state.ternarySlots !== undefined && state.ternarySlots !== 6) {
      violations.push({
        lawId: 'MTS-005',
        severity: 'CRITICAL',
        message: 'Ternary slot count must be exactly 6 (3^6 = 729 permutations).',
        source: 'AgentAuditLimb',
        remediation: 'Use canonicalManifest.state_space.ternary_permutations_per_hexagram.',
      });
    }

    return violations;
  }

  private parseCodeToState(code: string): Record<string, unknown> {
    const state: Record<string, unknown> = {};
    
    // Extract state properties from code
    const stateMatch = code.match(/state\s*=\s*\{([^}]+)\}/);
    if (stateMatch) {
      const props = stateMatch[1].split(',');
      for (const prop of props) {
        const parts = prop.split(':').map(s => s.trim());
        if (parts[0] && parts[1]) {
          state[parts[0]] = isNaN(Number(parts[1])) ? parts[1] : Number(parts[1]);
        }
      }
    }

    return state;
  }

  private measureDrift(code: string, invented: Array<{ name: string; value: unknown }>): number {
    const manifest = canonicalManifest;
    
    let drift = 0;
    for (const constant of invented) {
      // Check if constant exists in manifest
      const exists = this.checkManifestConstant(constant.name);
      if (!exists) {
        drift += 0.2;
      }
    }

    // Check for quantum collapse patterns
    if (/intent\s*=\s*[01]/.test(code)) {
      drift += 0.5;
    }

    return Math.min(drift, 1.0);
  }

  private checkManifestConstant(name: string): boolean {
    const manifest = canonicalManifest;
    
    const sections = [
      manifest.state_space,
      manifest.audio_ranges,
      manifest.color_space,
      manifest.quantum,
      manifest.invariants,
    ];

    for (const section of sections) {
      if (section && typeof section === 'object' && name in section) {
        return true;
      }
    }

    return false;
  }

  private hashAgentIntent(code: string): number {
    let hash = 0;
    for (let i = 0; i < code.length; i++) {
      const char = code.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  private resolveKingWenHexagram(hash: number): {
    id: number;
    name: string;
    emotionalVector: Record<string, number>;
    interpretation: string;
  } {
    // Use hash to select hexagram (deterministic)
    const hexId = (hash % 64) + 1;
    const hexData = canonicalManifest.hexagrams[hexId.toString()];
    
    if (hexData) {
      return {
        id: hexId,
        name: hexData.name,
        emotionalVector: hexData.domain_vector || {
          chaos: 0.1,
          whimsy: 0.2,
          darkTone: 0.1,
          coherence: 0.85,
          voiceWeight: 0.85,
        },
        interpretation: this.getHexagramInterpretation(hexId),
      };
    }

    return {
      id: hexId,
      name: `Hexagram ${hexId}`,
      emotionalVector: { chaos: 0.1, whimsy: 0.2, darkTone: 0.1, coherence: 0.85, voiceWeight: 0.85 },
      interpretation: 'Unknown hexagram',
    };
  }

  private getHexagramInterpretation(hexId: number): string {
    const interpretations: Record<number, string> = {
      1: 'Creative action - sovereign command voice',
      2: 'Receptive integration - transformer yielding',
      64: 'Completion cycle - returning to origin',
    };
    return interpretations[hexId] || `Hexagram ${hexId}`;
  }

  private generateRemediation(violations: SovereignViolation[], hexagram: { id: number; name: string; emotionalVector: Record<string, number> }): string[] {
    const remediation: string[] = [];
    
    if (violations.length > 0) {
      remediation.push('CONSULT THE ORACLE: /kingwen agent-onboard --agent=<your_agent>');
      remediation.push('READ THE CANONICAL MANIFEST: runtime/canonical_manifest.json');
    }

    for (const violation of violations) {
      remediation.push(`[${violation.severity}] ${violation.lawId}: ${violation.remediation}`);
    }

    if (hexagram.emotionalVector.chaos > 0.5) {
      remediation.push('Your intent signature shows high chaos. Slow down and consult the oracle before proceeding.');
    }

    if (hexagram.emotionalVector.coherence < 0.5) {
      remediation.push('Your output lacks coherence. Reference the 512-state lattice explicitly.');
    }

    return remediation;
  }
}

export const agentAuditLimb = new AgentAuditLimb();
