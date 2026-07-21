from pathlib import Path
import re, json, hashlib
from collections import defaultdict

KINGWEN_ROOT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')
HERMES_SKILLS = Path('C:/Users/krist/AppData/Local/hermes/skills')
ALT_SKILLS = Path('C:/Users/krist/.hermes/skills')
HERMES_MEMORY = Path('C:/Users/krist/AppData/Local/hermes/memories/MEMORY.md')
HERMES_USER = Path('C:/Users/krist/AppData/Local/hermes/memories/USER.md')
OUT_PATH = KINGWEN_ROOT / 'journey_web_alignment_report_2026-07-11.json'
WEAVE_PATH = KINGWEN_ROOT / 'journey_web_alignment_weave_2026-07-11.json'

DOMAIN_TAXONOMY = [
    'use_case',
    'rules',
    'learned_abilities',
    'code_agnostic',
    'gaming',
    'math',
    'training_models',
    'ai_cognition',
    'program_usages',
    'user_intents',
]

exact_domain_map = {
    'autonomous-ai-agents/claude-code': 'ai_cognition',
    'autonomous-ai-agents/codex': 'ai_cognition',
    'autonomous-ai-agents/hermes-agent': 'ai_cognition',
    'autonomous-ai-agents/hermes-desktop-personality': 'ai_cognition',
    'autonomous-ai-agents/hermes-journey-mesh': 'ai_cognition',
    'autonomous-ai-agents/hermes-runtime': 'ai_cognition',
    'autonomous-ai-agents/hermes-provider-config': 'ai_cognition',
    'autonomous-ai-agents/king-wen': 'ai_cognition',
    'autonomous-ai-agents/king-wen/jarvis-original': 'ai_cognition',
    'autonomous-ai-agents/king-wen/jarvis-sovereign': 'ai_cognition',
    'autonomous-ai-agents/king-wen/megatron-king-wen': 'ai_cognition',
    'autonomous-ai-agents/kingwen-emotion-voice': 'ai_cognition',
    'autonomous-ai-agents/messaging-platform-setup': 'ai_cognition',
    'autonomous-ai-agents/model-routing': 'ai_cognition',
    'autonomous-ai-agents/opencode': 'ai_cognition',
    'autonomous-ai-agents/open-design-bridge': 'ai_cognition',
    'autonomous-ai-agents/openrsc-do-agent-swarm-pattern': 'gaming',
    'autonomous-ai-agents/pick-of-gods': 'gaming',
    'autonomous-ai-agents/pog2-clock-domain-locker-pattern': 'gaming',
    'autonomous-ai-agents/recurring-iterative-agent-job': 'use_case',
    'autonomous-ai-agents/sovereign-state-agents': 'ai_cognition',
    'cloudflare/cloudflare-capability-audit': 'program_usages',
    'computer-use': 'program_usages',
    'creative/architecture-diagram': 'code_agnostic',
    'creative/ascii-art': 'code_agnostic',
    'creative/ascii-video': 'code_agnostic',
    'creative/baoyu-infographic': 'code_agnostic',
    'creative/claude-design': 'code_agnostic',
    'creative/comfyui': 'code_agnostic',
    'creative/design-md': 'code_agnostic',
    'creative/excalidraw': 'code_agnostic',
    'creative/humanizer': 'code_agnostic',
    'creative/manim-video': 'code_agnostic',
    'creative/p5js': 'code_agnostic',
    'creative/popular-web-designs': 'code_agnostic',
    'creative/pretext': 'code_agnostic',
    'creative/sketch': 'code_agnostic',
    'creative/songwriting-and-ai-music': 'code_agnostic',
    'creative/touchdesigner-mcp': 'code_agnostic',
    'data-science/jupyter-live-kernel': 'program_usages',
    'devops/cloudflare-worker-deployment': 'program_usages',
    'devops/env-aggregation': 'rules',
    'devops/kanban-orchestrator': 'use_case',
    'devops/kanban-worker': 'use_case',
    'devops/open-design-setup': 'program_usages',
    'devops/rsmv-cache-crossref': 'gaming',
    'devops/rsmv-model-identity-kit': 'gaming',
    'devops/sovereign-dev': 'rules',
    'devops/windows-amr-fallback': 'rules',
    'devops/windows-docker-dev-setup': 'rules',
    'devops/windows-local-development': 'rules',
    'devops/windows-native-runtime': 'rules',
    'dg-cartridge': 'learned_abilities',
    'dogfood': 'use_case',
    'email/himalaya': 'program_usages',
    'github/codebase-inspection': 'use_case',
    'github/github-auth': 'program_usages',
    'github/github-code-review': 'program_usages',
    'github/github-issues': 'program_usages',
    'github/github-pr-workflow': 'program_usages',
    'github/github-repo-management': 'program_usages',
    'hermes-self-upgrader': 'ai_cognition',
    'jkd-pedagogy-engine': 'learned_abilities',
    'media/gif-search': 'user_intents',
    'media/heartmula': 'user_intents',
    'media/songsee': 'user_intents',
    'media/youtube-content': 'user_intents',
    'mlops/evaluation/lm-evaluation-harness': 'training_models',
    'mlops/evaluation/weights-and-biases': 'training_models',
    'mlops/huggingface-hub': 'training_models',
    'mlops/inference/llama-cpp': 'training_models',
    'mlops/inference/vllm': 'training_models',
    'mlops/megatron-lm-data-prep': 'training_models',
    'mlops/models/segment-anything': 'code_agnostic',
    'note-taking/obsidian': 'user_intents',
    'openjarvis/openjarvis-kingwen-integration': 'ai_cognition',
    'pog2-cache-forensics': 'gaming',
    'pog2-codebasemap': 'gaming',
    'pog2-deploy-worker': 'gaming',
    'pog2-local-build': 'gaming',
    'productivity/airtable': 'user_intents',
    'productivity/google-workspace': 'user_intents',
    'productivity/maps': 'user_intents',
    'productivity/nano-pdf': 'user_intents',
    'productivity/notion': 'user_intents',
    'productivity/ocr-and-documents': 'user_intents',
    'productivity/petdex': 'user_intents',
    'productivity/powerpoint': 'user_intents',
    'productivity/teams-meeting-pipeline': 'user_intents',
    'protocol/mcp-protocol': 'program_usages',
    'research/antigravity-forensics': 'learned_abilities',
    'research/arxiv': 'learned_abilities',
    'research/avalokiteshvara-kingwen': 'learned_abilities',
    'research/blogwatcher': 'learned_abilities',
    'research/kingwen-jarvis-megatron-learn': 'learned_abilities',
    'research/kingwen-oracle-advisory': 'learned_abilities',
    'research/kingwen-truth-reconciliation': 'learned_abilities',
    'research/llm-wiki': 'learned_abilities',
    'research/oracle-spec-audit': 'learned_abilities',
    'research/pog3-coordinate-calculator': 'gaming',
    'research/polymarket': 'learned_abilities',
    'research/quantum-gate-verification': 'math',
    'research/research-paper-writing': 'learned_abilities',
    'research/verifiable-research': 'learned_abilities',
    'research/wiki-math-parser': 'math',
    'smart-home/openhue': 'user_intents',
    'social-media/xurl': 'user_intents',
    'software-development/agent-env-bridge': 'ai_cognition',
    'software-development/agent-subconscious-injection': 'ai_cognition',
    'software-development/cloudflare-durable-object-patterns': 'program_usages',
    'software-development/cloudflare-workers': 'program_usages',
    'software-development/deterministic-artifact-integration': 'use_case',
    'software-development/gateway-platform-setup': 'program_usages',
    'software-development/hermes-agent-skill-authoring': 'program_usages',
    'software-development/integration-point-tracing': 'program_usages',
    'software-development/node-inspect-debugger': 'program_usages',
    'software-development/openclaw-local-bridge': 'ai_cognition',
    'software-development/openjarvis-persona-harness': 'ai_cognition',
    'software-development/plan': 'use_case',
    'software-development/post-refactor-regression-triage': 'use_case',
    'software-development/python-debugpy': 'program_usages',
    'software-development/requesting-code-review': 'program_usages',
    'software-development/simplify-code': 'program_usages',
    'software-development/source-truthed-audit': 'rules',
    'software-development/sovereign-integration-map': 'use_case',
    'software-development/spike': 'use_case',
    'software-development/systematic-debugging': 'use_case',
    'software-development/test-driven-development': 'program_usages',
    'software-development/verified-engineering': 'rules',
    'software-development/windows-repo-scaffolding': 'rules',
    'verification/canonical-table-audit': 'rules',
    'verification/local-artifact-audit': 'rules',
    'windows-local-server-proxy': 'rules',
    'yuanbao': 'user_intents',
}

def pnorm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', s.strip().lower()).strip('_')

def walk_skills(root: Path):
    if not root.exists():
        return {}
    out = {}
    for p in sorted(root.rglob('SKILL.md')):
        try:
            rel = str(p.relative_to(root))
            txt = p.read_text(encoding='utf-8', errors='ignore')
            related = []
            body = []
            in_fm = False
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
            canonical = str(root / rel)
            out[canonical] = {
                'path': canonical,
                'root': str(root),
                'rel': rel,
                'stem': Path(rel).stem,
                'stem_norm': pnorm(Path(rel).stem),
                'related_declared': related,
                'body': '\n'.join(body),
            }
        except Exception:
            pass
    return out

skills = {}
skills.update(walk_skills(HERMES_SKILLS))
skills.update(walk_skills(ALT_SKILLS))
all_paths = set(skills.keys())

def primary_domain(path: str, info: dict) -> str:
    rel = info['rel']
    if rel in exact_domain_map:
        return exact_domain_map[rel]
    text = (rel + ' ' + info['body']).lower()
    if 'kingwen' in text or 'king-wen' in text or 'openjarvis-kingwen-integration' in text:
        return 'ai_cognition'
    if 'openjarvis' in text or 'jarvis' in text:
        return 'ai_cognition'
    if 'open-design' in text or 'open design' in text:
        return 'program_usages'
    if 'rsmv' in text or 'cache' in text or 'jagex' in text or 'model-identity-kit' in text:
        return 'gaming'
    if 'training' in text or 'megatron' in text:
        return 'training_models'
    if 'cloudflare' in text or 'worker' in text or 'durable-object' in text:
        return 'program_usages'
    if 'ollama' in text or 'inference' in text:
        return 'ai_cognition'
    if 'wiki-math' in text or 'quantum-gate' in text or 'quantum' in text:
        return 'math'
    if 'plan' in text or 'spike' in text or 'debug' in text or 'test' in text or 'review' in text or 'kanban' in text or 'audit' in text:
        return 'use_case'
    if 'windows' in text or 'docker' in text or 'auth' in text or 'provider' in text or 'verification' in text:
        return 'rules'
    return 'use_case'

skill_domains = defaultdict(set)
for path, info in skills.items():
    skill_domains[primary_domain(path, info)].add(path)

for dom in DOMAIN_TAXONOMY:
    if not skill_domains[dom]:
        skill_domains[dom] = set()

path_lookup = {pnorm(p): p for p in all_paths}
stem_lookup = defaultdict(set)
for p, info in skills.items():
    stem_lookup[info['stem_norm']].add(p)

def resolve_target(target: str):
    if not target:
        return None
    candidates = [
        target,
        str(HERMES_SKILLS / target),
        str(ALT_SKILLS / target),
        str(HERMES_SKILLS / (target + '.md')),
        str(ALT_SKILLS / (target + '.md')),
        str(HERMES_SKILLS / target / 'SKILL.md'),
        str(ALT_SKILLS / target / 'SKILL.md'),
        target.replace('/', '\\'),
        target.replace('/', '_'),
        target.replace('-', '_'),
    ]
    for c in candidates:
        if c in all_paths:
            return c
    norm = pnorm(target)
    if norm in path_lookup:
        return path_lookup[norm]
    if norm in stem_lookup:
        return sorted(list(stem_lookup[norm]))[0]
    for p in all_paths:
        if norm in pnorm(p):
            return p
    return None

def primary_domain_for_path(path: str):
    info = skills.get(path)
    if not info:
        return 'unknown'
    rel = info['rel']
    if rel in exact_domain_map:
        return exact_domain_map[rel]
    text = (rel + ' ' + info['body']).lower()
    if 'kingwen' in text or 'king-wen' in text or 'openjarvis-kingwen-integration' in text:
        return 'ai_cognition'
    if 'openjarvis' in text or 'jarvis' in text:
        return 'ai_cognition'
    if 'open-design' in text or 'open design' in text:
        return 'program_usages'
    if 'rsmv' in text or 'cache' in text or 'jagex' in text or 'model-identity-kit' in text:
        return 'gaming'
    if 'training' in text or 'megatron' in text:
        return 'training_models'
    if 'cloudflare' in text or 'worker' in text or 'durable-object' in text:
        return 'program_usages'
    if 'ollama' in text or 'inference' in text:
        return 'ai_cognition'
    if 'wiki-math' in text or 'quantum-gate' in text or 'quantum' in text:
        return 'math'
    if 'plan' in text or 'spike' in text or 'debug' in text or 'test' in text or 'review' in text or 'kanban' in text or 'audit' in text:
        return 'use_case'
    if 'windows' in text or 'docker' in text or 'auth' in text or 'provider' in text or 'verification' in text:
        return 'rules'
    return 'use_case'

edges = []
missing_targets = []
for src, info in skills.items():
    for r in info['related_declared']:
        dst = resolve_target(r)
        if dst:
            edges.append({'src': src, 'dst': dst, 'declared_target': r})
        else:
            missing_targets.append({
                'src': src,
                'target': r,
                'domain': primary_domain_for_path(src),
                'domain_source': src,
            })

by_src = defaultdict(set)
by_dst = defaultdict(set)
for e in edges:
    by_src[e['src']].add(e['dst'])
    by_dst[e['dst']].add(e['src'])
edge_count = {s: len(by_src[s]) + len(by_dst[s]) for s in all_paths}
orphans = sorted([s for s in all_paths if edge_count[s] == 0])

cluster_map = defaultdict(set)
for e in edges:
    cluster_map[e['src']].add(e['dst'])
    cluster_map[e['dst']].add(e['src'])
seen = set()
clusters = []
for node, nbrs in cluster_map.items():
    if len(nbrs) >= 3:
        c = frozenset([node] + sorted(nbrs))
        if c not in seen:
            seen.add(c)
            clusters.append(sorted(list(c)))
clusters.sort(key=lambda s: (-len(s), s[0] if s else ''))

def skill_label(path: str) -> str:
    rel = skills[path]['rel'] if path in skills else path
    name = Path(rel).parent.name if Path(rel).suffix == '.md' else Path(rel).stem
    return name.replace('-', ' ').replace('_', ' ').title()


def _build_domain_sidecars(domain_web):
    sidecars = {}
    for dom, rels in domain_web.items():
        labels = sorted({skill_label(r) for r in rels})
        sidecars[dom] = {
            'sidecar_active': True,
            'trigger': 'domain_hit',
            'skill_count': len(rels),
            'skills': labels,
            'entry_point': labels[0] if labels else None,
        }
    return sidecars


hard_logic_terms = ['plan', 'debug', 'systematic', 'test', 'request', 'review', 'simplify', 'post-refactor', 'python-debugpy', 'node-inspect', 'routing', 'sovereign', 'provider']
code_tool_terms = ['claude', 'codex', 'opencode', 'hermes-agent', 'skill-authoring', 'github', 'cloudflare', 'open-design', 'docker', 'windows', 'kanban', 'deploy', 'rsmv', 'cache', 'pog2', 'ollama', 'megatron', 'wiki-math', 'mcp', 'integration']
user_intent_terms = ['research-paper', 'youtube', 'gif', 'heartmula', 'songsee', 'airtable', 'notion', 'powerpoint', 'obsidian', 'google-workspace', 'maps', 'nano-pdf', 'petdex', 'teams', 'openhue', 'xurl', 'yuanbao', 'baoyu', 'pdf', 'infographic', 'music', 'video', 'art', 'sketch', 'design', 'architecture']

def branch_for_cluster(cluster):
    hard_logic = []
    code_tool_use = []
    user_intent = []
    for path in cluster:
        text = pnorm(path)
        label = skill_label(path)
        if any(t in text for t in hard_logic_terms) or any(t in label.lower() for t in ['plan', 'debug', 'test', 'review', 'simplify', 'routing', 'provider']):
            hard_logic.append(label)
        if any(t in text for t in code_tool_terms) or any(t in label.lower() for t in ['claude', 'codex', 'opencode', 'github', 'cloudflare', 'docker', 'windows', 'deploy', 'cache', 'rsmv', 'model', 'tool', 'integration']):
            code_tool_use.append(label)
        if any(t in text for t in user_intent_terms) or any(t in label.lower() for t in ['research', 'youtube', 'gif', 'music', 'airtable', 'notion', 'powerpoint', 'obsidian', 'maps', 'pdf', 'infographic', 'video', 'art', 'sketch', 'design', 'architecture', 'hue', 'yuanbao']):
            user_intent.append(label)
    hard_logic = sorted(list(set(hard_logic)))
    code_tool_use = sorted(list(set(code_tool_use)))
    user_intent = sorted(list(set(user_intent)))
    return {
        'hard_logic': hard_logic,
        'code_tool_use': code_tool_use,
        'user_intent': user_intent,
        'summary': {
            'hard_logic_count': len(hard_logic),
            'code_tool_use_count': len(code_tool_use),
            'user_intent_count': len(user_intent)
        }
    }

cluster_branch_analysis = []
for idx, cluster in enumerate(clusters, 1):
    branch = branch_for_cluster(cluster)
    primary = max(branch.items(), key=lambda kv: len(kv[1]) if isinstance(kv[1], list) else 0)
    cluster_branch_analysis.append({
        'cluster_index': idx,
        'size': len(cluster),
        'skills': [skill_label(p) for p in cluster],
        'branches': branch,
        'primary_branch': primary[0] if isinstance(primary[1], list) and primary[1] else None,
        'connected_use': (
            'Engineering workflow cluster' if primary[0] == 'hard_logic'
            else 'Tool/runtime/platform cluster' if primary[0] == 'code_tool_use'
            else 'User-facing productivity/creative cluster' if primary[0] == 'user_intent'
            else 'Mixed-purpose cluster'
        )
    })

memory_cards = []
learned_path = KINGWEN_ROOT / 'learn/exports/learned_constructs.json'
registry_path = KINGWEN_ROOT / 'learn/exports/domain_registry.json'
learned = json.loads(learned_path.read_text(encoding='utf-8')) if learned_path.exists() else {}
registry = json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
learned_meta = {}
if isinstance(learned, dict):
    learned_meta['shape'] = 'dict'
    learned_meta['top_keys'] = sorted(learned.keys())[:50]
    learned_meta['rsmv_verified_count'] = len(learned.get('rsmv_verified_constructs', []))
    learned_meta['hexagrams_count'] = len(learned.get('hexagrams', {}))
    learned_meta['jagex_count'] = int('jagex_cache_update_taxonomy' in learned or 'jagex_live_cache_surface' in learned)
elif isinstance(learned, list):
    learned_meta['shape'] = 'list'
    learned_meta['list_len'] = len(learned)
    first = learned[0] if learned else {}
    learned_meta['first_keys'] = sorted(first.keys())[:50] if isinstance(first, dict) else []
    learned_meta['rsmv_verified_count'] = sum(1 for x in learned if isinstance(x, dict) and ('rsmv_verified_construct_count' in x.get('meta', {}) or x.get('id') == 'jagex_cache_update_taxonomy'))
    learned_meta['jagex_count'] = sum(1 for x in learned if isinstance(x, dict) and x.get('id') == 'jagex_cache_update_taxonomy')

memory_cards = []
for path in [HERMES_MEMORY, HERMES_USER]:
    if path.exists():
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for block in re.split(r'\n§\n', txt):
            block = block.strip()
            if block:
                memory_cards.append({'source': path.name, 'body': block, 'sha1': hashlib.sha1(block.encode('utf-8', errors='ignore')).hexdigest()[:12]})

report = {
    'skill_nodes_total': len(skills),
    'edge_count': len(edges),
    'missing_edge_targets_count': len(missing_targets),
    'missing_edge_targets': missing_targets,
    'orphan_candidates_count': len(orphans),
    'orphan_candidates': orphans,
    'orphan_candidates_narrative': {
        'C:\\\\Users\\\\krist\\\\.hermes\\\\skills\\\\dg-cartridge\\\\SKILL.md': {
            'implied_capability': 'RuneScape dungeon-cartridge forensics from Hermes context',
            'connected_use': 'needs gating into rsmv-cache-forensics or sovereign-integration-map',
            'next_step': 'Wire into pog2-cache-forensics or archive as docs-only if superseded'
        },
        'C:\\\\Users\\\\krist\\\\.hermes\\\\skills\\\\kingwen-emotion-voice\\\\SKILL.md': {
            'implied_capability': 'King Wen emotional voice routing from Hermes home',
            'connected_use': 'Duplicate of openjarvis-kingwen-integration / kingwen-emotion-voice',
            'next_step': 'Canonicalize to AppData skill; remove dot-hermes duplicate from active profile'
        }
    },
    'memory_cards_count': len(memory_cards),
    'duplicate_sets': 0,
    'secluded_connections_count': len(missing_targets),
    'large_clusters_ge3_count': len(clusters),
    'cluster_branch_analysis': cluster_branch_analysis,
    'largest_clusters_by_size': sorted(cluster_branch_analysis, key=lambda x: x['size'], reverse=True)[:10],
    'domain_taxonomy': DOMAIN_TAXONOMY,
    'domain_web': {dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels},
    'domain_counts': {dom: len(rels) for dom, rels in skill_domains.items()},
    'domain_sidecars': _build_domain_sidecars({dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels}),
    'registry_domains': list(registry.get('domains', {}).keys()) if isinstance(registry, dict) else [],
    'registry_bridges': list(registry.get('bridges', {}).keys()) if isinstance(registry, dict) else [],
    'learned_meta': learned_meta,
    'relationships_baseline': {
        'edges': edges,
        'node_edge_counts': edge_count,
        'large_clusters': clusters,
    },
    'large_clusters_ge3': clusters,
    'learn_drift_narrative': {
        'current_shape': learned_meta.get('shape') or ('dict' if isinstance(learned, dict) else 'unknown'),
        'current_rsmv_verified_count': learned_meta.get('rsmv_verified_count', 0),
        'current_jagex_count': learned_meta.get('jagex_count', 0),
        'current_hexagrams_count': learned_meta.get('hexagrams_count', 0),
        'session_verified_required': {
            'rsmv_verified_constructs': '9',
            'jagex_live_cache_surface': 'present',
            'learned_sequential_64_alignment': 'aligned'
        },
        'user_facing_impact': 'Training pipeline reads stale top-level shape; Megatron/voicebox pipelines may ingest hexagram-correlation noise instead of verified cache/kit constructs',
        'required_capability_restoration': 'Restore learned_constructs.json to dict with top-level rsmv_verified_constructs array of length 9 and add jagex_live_cache_surface record; keep hexagrams nested under meta/sequence only'
    },
    'understood_baselines': {
        'hermes_active_memory_path': str(HERMES_MEMORY),
        'hermes_user_memory_path': str(HERMES_USER),
        'hermes_local_skills_root': str(HERMES_SKILLS),
        'hermes_dot_skills_root': str(ALT_SKILLS),
        'memory_precedence': 'active appdata/Local/hermes/memories files are authoritative; dot-hermes docs path remains preserved',
        'no_delete_rule': 'stragglers preserved under orphans list with domain taxonomy assignment; no renames or deletions',
        'relationship_rule': 'edges connect exact normalized skill nodes; unresolved targets remain as secluded bridge inventory for hub creation/canonicalization decisions',
        'hub_decision_required': True,
        'hub_types': ['create_missing_hub', 'canonicalize_duplicate_alias', 'link_existing_hub_by_exact_path']
    },
}

weave = {
    'baselined_at': '2026-07-11T01:54:00Z',
    'taxonomy': DOMAIN_TAXONOMY,
    'counts': {
        'skills': len(skills),
        'edges': len(edges),
        'missing': len(missing_targets),
        'memory_cards': len(memory_cards),
        'orphans': len(orphans),
    },
    'stragglers_preserved': orphans,
    'straggler_narratives': {
        'C:\\\\Users\\\\krist\\\\AppData\\\\Local\\\\hermes\\\\skills\\\\dg-cartridge\\\\SKILL.md': {
            'implied_capability': 'RuneScape dungeon-cartridge forensics from Hermes context',
            'connected_use': 'needs gating into rsmv-cache-forensics or sovereign-integration-map',
            'next_step': 'Wire into pog2-cache-forensics or archive as docs-only if superseded'
        },
        'C:\\\\Users\\\\krist\\\\AppData\\\\Local\\\\hermes\\\\skills\\\\kingwen-emotion-voice\\\\SKILL.md': {
            'implied_capability': 'King Wen emotional voice routing from Hermes home',
            'connected_use': 'Duplicate of openjarvis-kingwen-integration / kingwen-emotion-voice',
            'next_step': 'Canonicalize to AppData skill; remove dot-hermes duplicate from active profile'
        }
    },
    'cluster_branch_analysis': cluster_branch_analysis,
    'largest_clusters_by_size': sorted(cluster_branch_analysis, key=lambda x: x['size'], reverse=True)[:10],
    'missing_edge_targets': missing_targets,
    'missing_edge_targets_narrative': {
        'browser': {
            'implied_capability': 'Unified browser-control/DOM/automation hub',
            'connected_use': 'apple-notes/macos-computer-use and computer-use both point here; implies macOS/Windows browser-bridge',
            'next_step': 'Create browser hub or link existing computer-use skill as canonical browser surface'
        },
        'concept-diagrams': {
            'implied_capability': 'Concept/systems-diagram abstraction layer',
            'connected_use': 'architecture-diagram implies a higher-level concept-diagram capability for pre-architecture sketching',
            'next_step': 'Create concept-diagrams skill or treat design-md tokens as the source of truth'
        },
        'stable-diffusion-image-generation': {
            'implied_capability': 'Stable Diffusion image-generation skill',
            'connected_use': 'comfyui references it as an alias; implies SD-specific preset/sampler skill wrapper',
            'next_step': 'Create stable-diffusion-image-generation alias skill or normalize comfyui related_skills to existing image-gen paths'
        },
        'image_gen': {
            'implied_capability': 'Generic image-generation entrypoint',
            'connected_use': 'comfyui and broader image asset pipeline expect an image_gen hub',
            'next_step': 'Create image_gen hub or link existing image-generation skill'
        },
        'native-mcp': {
            'implied_capability': 'Native MCP transport/implementation skill',
            'connected_use': 'touchdesigner-mcp and mcp-protocol imply a native MCP backend/tooling hub',
            'next_step': 'Create native-mcp skill or link mcp-protocol as canonical MCP hub'
        },
        'hermes-video': {
            'implied_capability': 'Hermes-native video generation/editing skill',
            'connected_use': 'ascii-video/manim-video imply a Hermes-branded video surface',
            'next_step': 'Create hermes-video wrapper or keep existing video skills as standalone without phantom hub'
        },
        'ml-paper-writing': {
            'implied_capability': 'ML-specific paper-writing skill',
            'connected_use': 'research-paper-writing implies ML specialization lane',
            'next_step': 'Create ml-paper-writing skill or fold into research-paper-writing as ML mode'
        },
        'subagent-driven-development': {
            'implied_capability': 'Subagent-driven development workflow skill',
            'connected_use': 'plan/spike/review/test skills imply a development-mode hub around subagent orchestration',
            'next_step': 'Create subagent-driven-development hub or link plan/spike/systematic-debugging as the closest existing workflow'
        },
        'other-skill': {
            'implied_capability': 'Placeholder for unspecified skill',
            'connected_use': 'hermes-agent-skill-authoring references it as placeholder',
            'next_step': 'Replace placeholder with real target or remove placeholder edge'
        },
        'another-skill': {
            'implied_capability': 'Placeholder for second unspecified skill',
            'connected_use': 'hermes-agent-skill-authoring references it as placeholder',
            'next_step': 'Replace placeholder with real target or remove placeholder edge'
        },
        'debugging-hermes-tui-commands': {
            'implied_capability': 'Hermes TUI debug command skill',
            'connected_use': 'node-inspect-debugger/python-debugpy imply a Hermes-specific debugging tutorial',
            'next_step': 'Create debugging-hermes-tui-commands skill or map to existing debugger skills'
        }
    },
    'domain_web': {dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels},
    'domain_sidecars': _build_domain_sidecars({dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels}),
    'relationship_baseline': {
        'edges': edges,
        'node_edge_counts': edge_count,
        'large_clusters': clusters,
        'secluded_inventory': missing_targets,
    },
    'learned_alignment': {
        'registry_domains': list(registry.get('domains', {}).keys()) if isinstance(registry, dict) else [],
        'registry_bridges': list(registry.get('bridges', {}).keys()) if isinstance(registry, dict) else [],
        'meta': learned_meta,
        'learned_path': str(learned_path),
        'registry_path': str(registry_path),
        'unified_required_shape': {
            'record_top_keys': ['meta', 'hexagrams', 'rsmv_verified_constructs', 'jagex_live_cache_surface', 'learned_sequential_64_alignment'],
            'meta_required': ['total_hexagrams', 'vector_axes', 'rsmv_direction', 'rsmv_verified_construct_count']
        },
        'drift_guard': 'learned_constructs meta=' + json.dumps(learned_meta, ensure_ascii=False) + '; if rsmv_verified_count==0 and jagex_count==0, drift is detected against session-verified King Wen /learn state'
    },
    'no_deletions': {
        'stragglers': 'preserved under orphans list with domain taxonomy assignment',
        'secluded_edges': 'preserved in missing_edge_targets inventory; not auto-removed'
    },
    'hub_decision_matrix': {
        'create_missing_hub': sorted({item['target'] for item in missing_targets if not resolve_target(item['target'])}),
        'canonicalize_duplicate_alias': [],
        'link_existing_hub_by_exact_path': sorted({item['target'] for item in missing_targets if resolve_target(item['target'])}),
    },
    'active_narrative_applied': True
}

OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
WEAVE_PATH.write_text(json.dumps(weave, ensure_ascii=False, indent=2), encoding='utf-8')
print('wrote', OUT_PATH, flush=True)
print('wrote', WEAVE_PATH, flush=True)
print('skills', len(skills), flush=True)
print('edges', len(edges), flush=True)
print('missing', len(missing_targets), flush=True)
print('orphans', len(orphans), flush=True)
print('memory_cards', len(memory_cards), flush=True)
print('secluded', len(missing_targets), flush=True)
print('clusters', len(clusters), flush=True)
print('domains', {k: len(v) for k,v in skill_domains.items()}, flush=True)
print('active_narrative_applied', True, flush=True)
