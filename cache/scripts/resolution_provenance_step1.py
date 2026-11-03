import json, re
from pathlib import Path

def pnorm(s):
    return re.sub(r'[^a-z0-9]+', '_', s.strip().lower()).strip('_')

HERMES = Path('C:/Users/krist/AppData/Local/hermes/skills')
skills = {str(p): p for p in HERMES.rglob('SKILL.md')}
all_paths = set(skills.keys())

path_lookup = {}
stem_lookup = {}
for p in all_paths:
    pn = pnorm(p)
    path_lookup[pn] = p
    stem = pnorm(Path(p).parent.name)
    stem_lookup.setdefault(stem, []).append(p)

def resolve_target(target, all_paths, path_lookup, stem_lookup):
    if not target:
        return (None, None)
    candidates = [
        target,
        str(HERMES / target),
        str(HERMES / target / 'SKILL.md'),
        target.replace('/', '_'),
        target.replace('-', '_'),
    ]
    for c in candidates:
        if c in all_paths:
            return ('exact', c)
    norm = pnorm(target)
    if norm in path_lookup:
        return ('path_lookup', path_lookup[norm])
    if norm in stem_lookup:
        return ('stem_lookup', sorted(stem_lookup[norm])[0])
    for p in all_paths:
        if norm in pnorm(p):
            return ('fuzzy', p)
    return (None, None)

provenance = []
for p in sorted(skills.keys()):
    if '.archive' in p:
        continue
    txt = Path(p).read_text(encoding='utf-8', errors='ignore')
    in_fm = False
    related = []
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
    for r in related:
        method, resolved = resolve_target(r, all_paths, path_lookup, stem_lookup)
        if resolved and '.archive' in resolved:
            provenance.append({
                'source_skill': str(Path(p).relative_to(HERMES)),
                'declared_target': r,
                'resolved_path': str(Path(resolved).relative_to(HERMES)),
                'resolution_method': method,
                'archived': True,
            })

out = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/resolution_provenance_step1.json'
Path(out).write_text(json.dumps(provenance, indent=2), encoding='utf-8')
print('Total archived-target resolutions: ' + str(len(provenance)))
print('Written to ' + out)
