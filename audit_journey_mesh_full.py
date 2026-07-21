from pathlib import Path
import re, json, hashlib
from collections import defaultdict

HERMES_SKILLS = Path('C:/Users/krist/AppData/Local/hermes/skills')
ALT_SKILLS = Path('C:/Users/krist/.hermes/skills')
SKILL_ROOTS = [HERMES_SKILLS, ALT_SKILLS]
KINGWEN_ROOT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')
HERMES_MEMORY = Path('C:/Users/krist/AppData/Local/hermes/memories/MEMORY.md')
HERMES_USER = Path('C:/Users/krist/AppData/Local/hermes/memories/USER.md')
OUT_PATH = KINGWEN_ROOT / 'journey_web_alignment_report_2026-07-11.json'

# Load skills ----------------------------------------------------------------
skills = {}
for p in sorted(HERMES_SKILLS.rglob('SKILL.md')):
    try:
        rel = str(p.relative_to(HERMES_SKILLS))
        txt = p.read_text(encoding='utf-8', errors='ignore')
        related = []
        in_fm = False
        body = []
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith('---'):
                in_fm = not in_fm
                continue
            if in_fm and s.startswith('related_skills:'):
                raw = s.split(':', 1)[1].strip()
                if raw.startswith('[') and raw.endswith(']'):
                    raw = raw[1:-1]
                related = [x.strip().strip('"').strip("'") for x in raw.split(',') if x.strip()]
            else:
                body.append(s)
        skills[rel] = {
            'path': rel,
            'related_declared': related,
            'body': '\n'.join(body),
            'sha1': hashlib.sha1(txt.encode('utf-8', errors='ignore')).hexdigest()[:12],
        }
    except Exception:
        pass

skill_names = set(skills.keys())
edges = []
missing_targets = []
for rel, info in skills.items():
    for r in info['related_declared']:
        exists = False
        candidates = [
            r, r + '.md', r.replace('/', '\\'), r.replace('/', '_'),
            r.replace('-', '_'), r + '\\SKILL.md'
        ]
        for c in candidates:
            if c in skill_names or (HERMES_SKILLS / c).exists():
                exists = True
                break
        if exists:
            edges.append((rel, r))
        else:
            missing_targets.append({'src': rel, 'target': r})

edges_by_node = defaultdict(set)
for a, b in edges:
    edges_by_node[a].add(b)
    edges_by_node[b].add(a)
edge_count = {k: len(v) for k, v in edges_by_node.items()}

sha_groups = defaultdict(list)
for rel, info in skills.items():
    sha_groups[info['sha1']].append(rel)
duplicate_sets = {sha: rels for sha, rels in sha_groups.items() if len(rels) > 1}

dominion_keywords = {
    'king-wen / kingwen': ['kingwen', 'king-wen', 'king_wen', 'openjarvis-kingwen-integration', 'kingwen-oracle-advisory', 'kingwen-truth-reconciliation'],
    'openjarvis / jarvis': ['openjarvis', 'jarvis', 'openjarvis'],
    'open design / moa': ['open-design', 'open_design', 'od-', 'design-bridge', 'open-design-setup'],
    'megatron / training': ['megatron', 'training', 'pretrain', 'dataset'],
    'rsmv / gaming / cache': ['rsmv', 'pog2', 'cache', 'rune', 'jagex', 'model-identity-kit'],
    'cloudflare / workers': ['cloudflare', 'worker', 'durable-object', 'party', 'pages'],
    'ollama / inference': ['ollama', 'llama-cpp', 'vllm', 'model-routing', 'mistral'],
    'hermes runtime / agent': ['hermes-agent', 'hermes-runtime', 'hermes-self-upgrader', 'provider-config', 'desktop-personality'],
    'creative / media': ['creative', 'ascii', 'excalidraw', 'manim', 'comfyui', 'p5js', 'songwriting', 'touchdesigner'],
    'productivity / docs': ['google-workspace', 'notion', 'airtable', 'nano-pdf', 'powerpoint', 'obsidian', 'ocr-and-documents'],
    'research / math': ['wiki-math', 'arxiv', 'polymarket', 'antigravity-forensics', 'verifiable-research', 'quantum-gate'],
    'protocol / integration': ['mcp', 'a2a', 'integration', 'touchdesigner-mcp', 'native-mcp'],
}
skill_domains = defaultdict(set)
for rel, info in skills.items():
    text = (rel + ' ' + info['body']).lower()
    hits = []
    for dom, words in dominion_keywords.items():
        if any(w in text for w in words):
            hits.append(dom)
    if not hits:
        hits = ['uncategorized']
    for dom in hits:
        skill_domains[dom].add(rel)

memory_cards = []
for path in [HERMES_MEMORY, HERMES_USER]:
    if path and path.exists():
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for block in re.split(r'\n§\n', txt):
            block = block.strip()
            if block:
                memory_cards.append({
                    'source': path.name,
                    'body': block,
                    'sha1': hashlib.sha1(block.encode('utf-8', errors='ignore')).hexdigest()[:12],
                })

learned_path = KINGWEN_ROOT / 'learn/exports/learned_constructs.json'
learned_data = json.loads(learned_path.read_text(encoding='utf-8')) if learned_path.exists() else {}
learned_meta = {}
if isinstance(learned_data, dict):
    learned_meta['top_keys'] = sorted(learned_data.keys())[:40]
    learned_meta['rsmv_verified_count'] = len(learned_data.get('rsmv_verified_constructs', []))
    learned_meta['hexagrams_count'] = len(learned_data.get('hexagrams', {}))
elif isinstance(learned_data, list):
    learned_meta['list_len'] = len(learned_data)
    first = learned_data[0] if learned_data else {}
    learned_meta['first_keys'] = sorted(first.keys())[:40] if isinstance(first, dict) else []
    learned_meta['rsmv_verified_count'] = sum(1 for x in learned_data if isinstance(x, dict) and 'rsmv_verified_constructs' in x)
    learned_meta['jagex_count'] = sum(1 for x in learned_data if isinstance(x, dict) and x.get('type') in ['cache_wiki_correlation','jagex_cache_update_taxonomy','jagex_live_cache_surface'])
    learned_meta['hexagrams_count'] = sum(1 for x in learned_data if isinstance(x, dict) and 'hexagrams' in x)
    learned_meta['meta_entries'] = sum(1 for x in learned_data if isinstance(x, dict) and 'meta' in x and isinstance(x['meta'], dict))

registry_path = KINGWEN_ROOT / 'learn/exports/domain_registry.json'
registry = json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
registry_domains = list(registry.get('domains', {}).keys()) if isinstance(registry, dict) else []
registry_bridges = list(registry.get('bridges', {}).keys()) if isinstance(registry, dict) else []

secluded = []
for rel, info in skills.items():
    for r in info['related_declared']:
        if not any(c in skill_names for c in [r, r+'.md', r.replace('/','\\'), r.replace('/', '_')]):
            if r not in info['body']:
                secluded.append({'skill': rel, 'edge': r, 'why': 'missing target + no shared path/repo mention'})

cluster_map = defaultdict(set)
for a, b in edges:
    cluster_map[a].add(b)
    cluster_map[b].add(a)
large_clusters = [sorted(list(v)) for v in cluster_map.values() if len(v) >= 3]
seen = set()
deduped_clusters = []
for c in sorted([frozenset(v) for v in large_clusters], key=lambda s: (-len(s), sorted(s)[0])):
    if c not in seen:
        seen.add(c)
        deduped_clusters.append(sorted(list(c)))

report = {
    'skill_nodes_count': len(skills),
    'edge_count': len(edges),
    'edge_targets_missing': len(missing_targets),
    'orphan_candidates_count': sum(1 for v in edge_count.values() if v == 0),
    'memory_cards_count': len(memory_cards),
    'domains': {dom: sorted(list(rels)) for dom, rels in skill_domains.items()},
    'domain_counts': {dom: len(rels) for dom, rels in skill_domains.items()},
    'learned_meta': learned_meta,
    'registry_domains': registry_domains,
    'registry_bridges': registry_bridges,
    'orphan_candidates': [k for k, v in edge_count.items() if v == 0][:120],
    'learn_drift': {
        'file': str(learned_path),
        'meta': learned_meta,
        'detected': f"{learned_meta.get('list_len', 'dict')} top-level records; rsmv entries={learned_meta.get('rsmv_verified_count',0)}; jagex entries={learned_meta.get('jagex_count',0)}; hexagram entries={learned_meta.get('hexagrams_count',0)}"
    },
    'duplicate_sets': {sha: rels for sha, rels in duplicate_sets.items()},
    'secluded_connections': secluded[:80],
    'large_clusters_ge3': deduped_clusters,
    'missing_edge_targets': missing_targets[:80],
}

OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('wrote', OUT_PATH, flush=True)
print('skill_nodes_count', report['skill_nodes_count'], flush=True)
print('edge_count', report['edge_count'], flush=True)
print('orphan_candidates_count', report['orphan_candidates_count'], flush=True)
print('memory_cards_count', report['memory_cards_count'], flush=True)
print('rsmv_verified', learned_meta.get('rsmv_verified_count', 0), flush=True)
print('hexagrams_count', learned_meta.get('hexagrams_count', 0), flush=True)
print('jagex_count', learned_meta.get('jagex_count', 0), flush=True)
print('duplicate_sets', sum(len(v)-1 for v in report['duplicate_sets'].values()), flush=True)
print('secluded', len(report['secluded_connections']), flush=True)
print('large_clusters', len(report['large_clusters_ge3']), flush=True)
