import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const paths = {
  registry: path.join(ROOT, 'data', 'hexagram-registry.json'),
  weights: path.join(ROOT, 'data', 'emotional-weights.json'),
  reflections: path.join(ROOT, 'data', 'temporal-reflections.json'),
};

export async function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export async function ensureDataFiles({ registry, weights, reflections }) {
  if (!fs.existsSync(paths.registry) || fs.readFileSync(paths.registry, 'utf8').trim().length === 0) {
    fs.mkdirSync(path.dirname(paths.registry), { recursive: true });
    fs.writeFileSync(paths.registry, JSON.stringify(registry, null, 2));
  }
  if (!fs.existsSync(paths.weights) || fs.readFileSync(paths.weights, 'utf8').trim().length === 0) {
    fs.mkdirSync(path.dirname(paths.weights), { recursive: true });
    fs.writeFileSync(paths.weights, JSON.stringify(weights, null, 2));
  }
  if (!fs.existsSync(paths.reflections) || fs.readFileSync(paths.reflections, 'utf8').trim().length === 0) {
    fs.mkdirSync(path.dirname(paths.reflections), { recursive: true });
    fs.writeFileSync(paths.reflections, JSON.stringify(reflections, null, 2));
  }
}
