import { OracleEngine } from './core/OracleEngine.js';

export async function bootstrap() {
  const engine = new OracleEngine({ deterministic: true });
  const registry = await import('node:fs').then((fs) => JSON.parse(fs.readFileSync(new URL('../data/hexagram-registry.json', import.meta.url), 'utf8')));
  const weights = await import('node:fs').then((fs) => JSON.parse(fs.readFileSync(new URL('../data/emotional-weights.json', import.meta.url), 'utf8')));
  const reflections = await import('node:fs').then((fs) => JSON.parse(fs.readFileSync(new URL('../data/temporal-reflections.json', import.meta.url), 'utf8')));
  engine.loadRegistry(registry);
  engine.loadReflections(reflections, weights);
  const response = await engine.consult({ text: 'What should I do?', session_id: 'demo', emotional_input: 50 });
  console.log(JSON.stringify(response, null, 2));
}

bootstrap().catch((err) => {
  console.error(err);
  process.exit(1);
});
