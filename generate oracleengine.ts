
# OracleEngine.ts
oracle_engine = '''import { 
  OracleConfig, OracleQuery, OracleResponse, HexagramState, 
  TemporalState, EmotionalVector, UserContext 
} from '../types/oracle.js';
import { EmotionalParser } from '../parser/EmotionalParser.js';
import { NarrativeEngine } from '../parser/NarrativeEngine.js';
import { computeTemporalPhase, phaseToString } from '../utils/TemporalMath.js';
import { deterministicHexagramSelect } from '../utils/DeterministicHash.js';

import registryJson from '../../data/hexagram-registry.json' assert { type: 'json' };
import weightsJson from '../../data/emotional-weights.json' assert { type: 'json' };
import reflectionsJson from '../../data/temporal-reflections.json' assert { type: 'json' };

export class OracleEngine {
  private config: OracleConfig;
  private emotionalParser: EmotionalParser;
  private narrativeEngine: NarrativeEngine;
  private hexagramRegistry: Map<number, HexagramState>;
  private tick: number = 0;

  constructor(config: Partial<OracleConfig> = {}) {
    this.config = {
      tick_interval_ms: 640,
      deterministic: true,
      emotional_smoothing: 0.1,
      ...config,
    };

    this.emotionalParser = new EmotionalParser();
    this.narrativeEngine = new NarrativeEngine(reflectionsJson, weightsJson);
    
    this.hexagramRegistry = new Map();
    for (const [id, data] of Object.entries(registryJson)) {
      this.hexagramRegistry.set(parseInt(id), { id: parseInt(id), ...data } as HexagramState);
    }
  }

  async consult(query: OracleQuery): Promise<OracleResponse> {
    const emotionalState = this.emotionalParser.parse(query);
    const temporal = computeTemporalPhase(this.tick++, query.emotional_input ?? 50);
    const hexagram = await this.selectHexagram(query, emotionalState, temporal);
    const reflections = this.narrativeEngine.generateReflections(hexagram, temporal, emotionalState);
    const emotionalDeltas = this.computeEmotionalDeltas(hexagram, emotionalState);
    
    return {
      hexagram_id: hexagram.id,
      hexagram_name: hexagram.name,
      hexagram_unicode: hexagram.unicode,
      temporal_phase: temporal.dominantPhase,
      temporal_substate: temporal.substate,
      past_reflection: reflections.past,
      present_reflection: reflections.present,
      future_reflection: reflections.future,
      unified_weave: reflections.unified_weave,
      sovereign_assertion: this.generateSovereignAssertion(hexagram, temporal),
      boundary_condition: this.generateBoundaryCondition(hexagram, temporal),
      dissipator_warning: this.generateDissipatorWarning(hexagram, temporal),
      action: hexagram.action,
      category: hexagram.category,
      emotional_deltas: emotionalDeltas,
      state_str: query.state_str,
    };
  }

  private async selectHexagram(
    query: OracleQuery,
    emotional: EmotionalVector,
    temporal: TemporalState
  ): Promise<HexagramState> {
    if (this.config.deterministic) {
      const previousHex = 1;
      const id = await deterministicHexagramSelect(this.tick, query.session_id, previousHex, 'sovereign');
      const hex = this.hexagramRegistry.get(id);
      if (!hex) throw new Error(`Invalid hexagram ID: ${id}`);
      return hex;
    }
    throw new Error('Weighted selection not yet implemented');
  }

  private computeEmotionalDeltas(hexagram: HexagramState, current: EmotionalVector): EmotionalVector {
    const weights = (weightsJson as Record<string, any>)[hexagram.id.toString()];
    if (!weights) return { chaos: 0, whimsy: 0, darkTone: 0, coherence: 0, voiceWeight: 0 };
    return {
      chaos: weights.chaos - current.chaos,
      whimsy: weights.whimsy - current.whimsy,
      darkTone: weights.darkTone - current.darkTone,
      coherence: weights.coherence - current.coherence,
      voiceWeight: weights.voiceWeight - current.voiceWeight,
    };
  }

  private generateSovereignAssertion(hexagram: HexagramState, temporal: TemporalState): string {
    return `[${hexagram.action}] ${hexagram.name} — ${phaseToString(temporal.dominantPhase)} phase`;
  }

  private generateBoundaryCondition(hexagram: HexagramState, temporal: TemporalState): string {
    return `Boundary: ${hexagram.category} | Action: ${hexagram.action} | Phase: ${temporal.substate}`;
  }

  private generateDissipatorWarning(hexagram: HexagramState, temporal: TemporalState): string {
    return hexagram.category === 'dissipator' 
      ? `⚠️ Energy drain risk in ${phaseToString(temporal.dominantPhase)} phase`
      : `Stable energy profile`;
  }
}
'''

with open(f"{output_dir}/src/core/OracleEngine.ts", "w") as f:
    f.write(oracle_engine)

# package.json
pkg = '''{
  "name": "oracle-emotional-state-machine",
  "version": "1.0.0",
  "description": "Standalone King Wen I Ching emotional parser with 64 hexagrams, 3 temporal phases, 5 emotional dimensions",
  "type": "module",
  "main": "dist/core/OracleEngine.js",
  "types": "dist/types/oracle.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "node --test dist/tests/*.js"
  },
  "dependencies": {},
  "devDependencies": {
    "typescript": "^5.3.0"
  }
}
'''

with open(f"{output_dir}/package.json", "w") as f:
    f.write(pkg)

# tsconfig.json
tsconfig = '''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*", "data/**/*"]
}
'''

with open(f"{output_dir}/tsconfig.json", "w") as f:
    f.write(tsconfig)

print("✅ src/core/OracleEngine.ts")
print("✅ package.json")
print("✅ tsconfig.json")
