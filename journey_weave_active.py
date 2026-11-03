"""
Active-only journey weave — filters archived (.archive/) skills from graph calculations.

This is a Step 1 (Archive filtering) artifact. It does NOT modify journey_weave.py.
It produces an active-only graph for comparison against the frozen baseline.

Filtering rule: A skill is "archived" if any path component of its SKILL.md
relative path contains ".archive". Archived skills are excluded from:
  - skill inventory (walk_skills)
  - edge computation
  - orphan detection
  - cluster formation
  - domain classification
  - straggler/missing-target attachment

Archived skills remain recoverable: their SKILL.md files are untouched and
their original paths are preserved in the frozen baseline artifacts.

Original baseline: journey_web_alignment_report_2026-07-11.json (241 skills, 155 edges)
"""

from pathlib import Path
import re, json, hashlib
from collections import defaultdict

KINGWEN_ROOT = Path(__file__).resolve().parent
HERMES_SKILLS = Path('C:/Users/krist/AppData/Local/hermes/skills')
ALT_SKILLS = Path('C:/Users/krist/.hermes/skills')
HERMES_MEMORY = Path('C:/Users/krist/AppData/Local/hermes/memories/MEMORY.md')
HERMES_USER = Path('C:/Users/krist/AppData/Local/hermes/memories/USER.md')
OUT_PATH = KINGWEN_ROOT / 'journey_web_alignment_report_active_2026-11-03.json'
WEAVE_PATH = KINGWEN_ROOT / 'journey_web_alignment_weave_active_2026-11-03.json'

# Import constants from original weave
import importlib.util
spec = importlib.util.spec_from_file_location("journey_weave", KINGWEN_ROOT / "journey_weave.py")
# We won't exec the original (it writes files); instead replicate needed constants
DOMAIN_TAXONOMY = [
    'use_case', 'rules', 'learned_abilities', 'code_agnostic', 'gaming',
    'math', 'training_models', 'ai_cognition', 'program_usages', 'user_intents',
]

exact_domain_map = {}  # Will be populated from original module if available

# Load original module's constants by reading the file
exec(open(KINGWEN_ROOT / "journey_weave.py").read().split("skills = {}")[0])

# Override output paths AFTER exec (exec may have set original paths)
OUT_PATH = KINGWEN_ROOT / 'journey_web_alignment_report_active_2026-11-03.json'
WEAVE_PATH = KINGWEN_ROOT / 'journey_web_alignment_weave_active_2026-11-03.json'

# Now redefine walk_skills with archive filtering
def walk_skills_active(root: Path):
    if not root.exists():
        return {}
    out = {}
    for p in sorted(root.rglob('SKILL.md')):
        # FILTER: skip archived skills
        rel_parts = p.relative_to(root).parts
        if '.archive' in rel_parts:
            continue
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

# Walk skills with archive filtering
skills = {}
skills.update(walk_skills_active(HERMES_SKILLS))
skills.update(walk_skills_active(ALT_SKILLS))
all_paths = set(skills.keys())

# Replicate the rest of the weave logic from the original
path_lookup = {pnorm(p): p for p in all_paths}
stem_lookup = defaultdict(set)
for p, info in skills.items():
    stem_lookup[info['stem_norm']].add(p)

def resolve_target(target: str):
    if not target:
        return None
    candidates = [
        target, str(HERMES_SKILLS / target), str(ALT_SKILLS / target),
        str(HERMES_SKILLS / (target + '.md')), str(ALT_SKILLS / (target + '.md')),
        str(HERMES_SKILLS / target / 'SKILL.md'), str(ALT_SKILLS / target / 'SKILL.md'),
        target.replace('/', '\\'), target.replace('/', '_'), target.replace('-', '_'),
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

edges = []
missing_targets = []
for src, info in skills.items():
    for r in info['related_declared']:
        dst = resolve_target(r)
        if dst:
            edges.append({'src': src, 'dst': dst, 'declared_target': r})
        else:
            missing_targets.append({
                'src': src, 'target': r,
                'domain': primary_domain(src, info), 'domain_source': src,
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

# Memory cards
memory_cards = []
for path in [HERMES_MEMORY, HERMES_USER]:
    if path.exists():
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for block in re.split(r'\n§\n', txt):
            block = block.strip()
            if block:
                memory_cards.append({'source': path.name, 'body': block, 'sha1': hashlib.sha1(block.encode('utf-8', errors='ignore')).hexdigest()[:12]})

# Learned constructs
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

def skill_label(path: str) -> str:
    rel = skills[path]['rel'] if path in skills else path
    name = Path(rel).parent.name if Path(rel).suffix == '.md' else Path(rel).stem
    return name.replace('-', ' ').replace('_', ' ').title()

def _build_domain_sidecars(domain_web):
    sidecars = {}
    for dom, rels in domain_web.items():
        labels = sorted({skill_label(r) for r in rels})
        sidecars[dom] = {
            'sidecar_active': True, 'trigger': 'domain_hit',
            'skill_count': len(rels), 'skills': labels,
            'entry_point': labels[0] if labels else None,
        }
    return sidecars

def attach_stragglers_to_clusters(orphans, clusters, skills, all_paths):
    attached = []
    unattachable = []
    for orphan in orphans:
        info = skills.get(orphan, {})
        rel = info.get('rel', '')
        body = info.get('body', '')
        text = (rel + ' ' + body).lower()
        best_cluster = None
        best_score = 0
        for ci, cluster in enumerate(clusters):
            score = 0
            for member in cluster:
                m_info = skills.get(member, {})
                m_text = (m_info.get('rel', '') + ' ' + m_info.get('body', '')).lower()
                for term in ['kingwen', 'openjarvis', 'rsmv', 'megatron', 'cloudflare', 'sovereign', 'verification', 'research', 'creative', 'devops', 'github', 'software', 'ai_cognition', 'gaming', 'training', 'math', 'voice', 'hermes', 'pog2', 'cinder', 'open-design', 'kimi', 'voicebox']:
                    if term in text and term in m_text:
                        score += 1
            if score > best_score:
                best_score = score
                best_cluster = ci
        if best_cluster is not None and best_score > 0:
            attached.append({'orphan': orphan, 'attached_to_cluster': best_cluster, 'score': best_score})
        else:
            unattachable.append(orphan)
    return attached, unattachable

def attach_missing_targets_to_clusters(missing_targets, clusters, skills, all_paths):
    attached = []
    for item in missing_targets:
        target = item.get('target', '')
        src = item.get('src', '')
        domain = item.get('domain', 'unknown')
        best_cluster = None
        best_score = 0
        for ci, cluster in enumerate(clusters):
            score = 0
            for member in cluster:
                m_info = skills.get(member, {})
                m_text = (m_info.get('rel', '') + ' ' + m_info.get('body', '')).lower()
                for term in DOMAIN_TERMS.get(domain, []):
                    if term in m_text:
                        score += 1
            if score > best_score:
                best_score = score
                best_cluster = ci
        if best_cluster is not None and best_score > 0:
            attached.append({'missing_target': target, 'src': src, 'attached_to_cluster': best_cluster, 'score': best_score})
        else:
            attached.append({'missing_target': target, 'src': src, 'attached_to_cluster': None, 'score': 0})
    return attached

# Domain terms (from original)
DOMAIN_TERMS = {
    'ai_cognition': ['kingwen', 'openjarvis', 'hermes', 'ai', 'cognition', 'megatron', 'training'],
    'gaming': ['rsmv', 'cache', 'jagex', 'model', 'pog2', 'game'],
    'use_case': ['plan', 'debug', 'test', 'review', 'kanban', 'audit', 'workflow'],
    'rules': ['windows', 'docker', 'auth', 'provider', 'verification', 'rules', 'compliance'],
    'program_usages': ['cloudflare', 'worker', 'open-design', 'github', 'cli', 'tool'],
    'training_models': ['training', 'megatron', 'model', 'pretrain', 'dataset'],
    'math': ['math', 'quantum', 'wave', 'Hamiltonian', 'equation'],
    'learned_abilities': ['learn', 'study', 'paper', 'corpus', 'pdf', 'extract'],
    'code_agnostic': ['design', 'architecture', 'diagram', 'semantic', 'graph'],
    'user_intents': ['research', 'paper', 'writing', 'citation', 'review'],
}

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
        'hard_logic': hard_logic, 'code_tool_use': code_tool_use, 'user_intent': user_intent,
        'summary': {'hard_logic_count': len(hard_logic), 'code_tool_use_count': len(code_tool_use), 'user_intent_count': len(user_intent)},
    }

cluster_branch_analysis = []
for idx, cluster in enumerate(clusters, 1):
    branch = branch_for_cluster(cluster)
    primary = max(branch.items(), key=lambda kv: len(kv[1]) if isinstance(kv[1], list) else 0)
    cluster_branch_analysis.append({
        'cluster_index': idx, 'size': len(cluster),
        'skills': [skill_label(p) for p in cluster],
        'branches': branch,
        'primary_branch': primary[0] if isinstance(primary[1], list) and primary[1] else None,
        'connected_use': (
            'Engineering workflow cluster' if primary[0] == 'hard_logic'
            else 'Tool/runtime/platform cluster' if primary[0] == 'code_tool_use'
            else 'User-facing productivity/creative cluster' if primary[0] == 'user_intent'
            else 'Mixed-purpose cluster'
        ),
    })

# Straggler/missing attachments
straggler_attached, straggler_unattached = attach_stragglers_to_clusters(orphans, clusters, skills, all_paths)
missing_attached = attach_missing_targets_to_clusters(missing_targets, clusters, skills, all_paths)

# Build report
report = {
    'baselined_at': '2026-11-03T00:00:00Z',
    'filter': 'active-only (excludes .archive/ directory)',
    'skill_nodes_total': len(skills),
    'edge_count': len(edges),
    'missing_edge_targets_count': len(missing_targets),
    'missing_edge_targets': missing_targets,
    'orphan_candidates_count': len(orphans),
    'orphan_candidates': orphans,
    'memory_cards_count': len(memory_cards),
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
    'straggler_attachments': {
        'attached': straggler_attached,
        'unattachable': straggler_unattached,
        'total_orphans': len(orphans),
        'attached_count': len(straggler_attached),
        'unattachable_count': len(straggler_unattached),
    },
    'missing_target_attachments': {
        'attached': missing_attached,
        'total_missing': len(missing_targets),
        'attached_count': len([a for a in missing_attached if a.get('attached_to_cluster') is not None]),
    },
    'no_deletions': {
        'stragglers': 'preserved under orphans list with domain taxonomy assignment; attached to clusters via domain affinity',
        'secluded_edges': 'preserved in missing_edge_targets inventory; attached to clusters via domain affinity',
        'archived_skills': 'NOT deleted or modified; excluded from active graph only',
    },
    'baseline_comparison': {
        'original_total_skills': 241,
        'original_edges': 155,
        'original_orphans': 141,
        'original_missing': 49,
        'original_clusters': 42,
        'active_total_skills': len(skills),
        'active_edges': len(edges),
        'active_orphans': len(orphans),
        'active_missing': len(missing_targets),
        'active_clusters': len(clusters),
    },
}

OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

weave = {
    'baselined_at': '2026-11-03T00:00:00Z',
    'filter': 'active-only (excludes .archive/ directory)',
    'taxonomy': DOMAIN_TAXONOMY,
    'counts': {
        'skills': len(skills), 'edges': len(edges),
        'missing': len(missing_targets), 'memory_cards': len(memory_cards),
        'orphans': len(orphans),
    },
    'stragglers_preserved': orphans,
    'cluster_branch_analysis': cluster_branch_analysis,
    'largest_clusters_by_size': sorted(cluster_branch_analysis, key=lambda x: x['size'], reverse=True)[:10],
    'missing_edge_targets': missing_targets,
    'domain_web': {dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels},
    'domain_sidecars': _build_domain_sidecars({dom: sorted(list(rels)) for dom, rels in skill_domains.items() if rels}),
    'straggler_attachments': report['straggler_attachments'],
    'missing_target_attachments': report['missing_target_attachments'],
    'baseline_comparison': report['baseline_comparison'],
    'active_narrative_applied': True,
    'no_deletions': report['no_deletions'],
}

WEAVE_PATH.write_text(json.dumps(weave, ensure_ascii=False, indent=2), encoding='utf-8')

print('wrote', OUT_PATH, flush=True)
print('wrote', WEAVE_PATH, flush=True)
print('active skills:', len(skills), flush=True)
print('active edges:', len(edges), flush=True)
print('active missing:', len(missing_targets), flush=True)
print('active orphans:', len(orphans), flush=True)
print('active clusters:', len(clusters), flush=True)
print('active domains:', {k: len(v) for k, v in skill_domains.items()}, flush=True)
print('stragglers attached:', len(straggler_attached), 'unattachable:', len(straggler_unattached), flush=True)
print('missing targets attached:', len([a for a in missing_attached if a.get('attached_to_cluster') is not None]), flush=True)