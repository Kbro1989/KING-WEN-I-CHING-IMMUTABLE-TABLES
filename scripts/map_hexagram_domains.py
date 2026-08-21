"""
Map corpus keywords/phrases to hexagram archetypes by domain position.

For each hexagram's category/action/phase, attach the actual keywords and phrases
from the paper frequency profiles that belong to that domain.
"""
from pathlib import Path
import json
from collections import defaultdict, Counter

# Paths
CORPUS_PROFILES = (Path.home() / "Desktop" / "zotero/learning-corpus/paper_frequency_profiles.jsonl")
ROOT = Path(__file__).resolve().parent.parent
ARCHETYPES = ROOT / "output" / "hexagram_coder_archetypes.csv"
PHASE_INDIVIDUALS = ROOT / "output" / "hexagram_phase_individuals.csv"
TRANSLATIONS = ROOT / "output" / "hexagram_translations.json"
OUT = ROOT / "output" / "hexagram_domain_keywords.json"

# Load corpus profiles
corpus = []
with CORPUS_PROFILES.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            corpus.append(json.loads(line))

print(f'corpus profiles: {len(corpus)}')

# Build domain keyword index from corpus
domain_keywords = defaultdict(lambda: {
    'top_words': Counter(),
    'top_bigrams': Counter(),
    'top_symbols': Counter(),
    'top_numbers': Counter(),
    'paper_count': 0,
    'avg_lexical_density': 0.0,
    'avg_number_density': 0.0,
})

for cp in corpus:
    signal = cp.get('dominant_signal', 'general')
    dk = domain_keywords[signal]
    dk['paper_count'] += 1
    dk['avg_lexical_density'] += cp.get('lexical_density', 0)
    dk['avg_number_density'] += cp.get('number_density', 0)
    for w in cp.get('top_words', []):
        dk['top_words'][w['w']] += w['c']
    for s in cp.get('top_symbols', []):
        dk['top_symbols'][s['s']] += s['c']
    for n in cp.get('top_numbers', []):
        dk['top_numbers'][n['n']] += n['c']

# Normalize domain stats
for signal, dk in domain_keywords.items():
    count = max(dk['paper_count'], 1)
    dk['avg_lexical_density'] = round(dk['avg_lexical_density'] / count, 6)
    dk['avg_number_density'] = round(dk['avg_number_density'] / count, 6)
    dk['top_words'] = [w for w, _ in dk['top_words'].most_common(50)]
    dk['top_symbols'] = [s for s, _ in dk['top_symbols'].most_common(20)]
    dk['top_numbers'] = [n for n, _ in dk['top_numbers'].most_common(20)]

print('domains indexed:', list(domain_keywords.keys()))

# Load archetypes
import csv
archetypes = []
with ARCHETYPES.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        archetypes.append(row)

print(f'archetypes: {len(archetypes)}')

# Load phase individuals
phase_individuals = []
with PHASE_INDIVIDUALS.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        phase_individuals.append(row)

print(f'phase individuals: {len(phase_individuals)}')

# Load translations
translations = json.loads(TRANSLATIONS.read_text(encoding='utf-8'))
print(f'translations: {len(translations)} entries')

# Map hexagram category/action to domain signals
CATEGORY_ACTION_TO_DOMAIN = {
    ('sovereign', 'ASSERT'): 'rlhf_alignment',
    ('sovereign', 'YIELD'): 'reasoning',
    ('sovereign', 'ADAPT'): 'safety',
    ('sovereign', 'WAIT'): 'multimodal',
    ('transformer', 'ASSERT'): 'transformer',
    ('transformer', 'YIELD'): 'transformer',
    ('transformer', 'ADAPT'): 'video',
    ('transformer', 'WAIT'): 'audio',
    ('dissipator', 'ASSERT'): 'diffusion',
    ('dissipator', 'YIELD'): 'diffusion',
    ('dissipator', 'ADAPT'): 'diffusion',
    ('dissipator', 'WAIT'): 'gan',
    ('boundary', 'ASSERT'): 'quant_efficiency',
    ('boundary', 'YIELD'): 'quant_efficiency',
    ('boundary', 'ADAPT'): 'graph',
    ('boundary', 'WAIT'): 'quant_efficiency',
}

# Build hexagram domain keyword map
hexagram_domains = {}
for arch in archetypes:
    hid = arch['hexagram_id']
    cat = arch['category']
    action = arch['action']
    
    # Primary domain from category/action
    primary_domain = CATEGORY_ACTION_TO_DOMAIN.get((cat, action), 'general')
    
    # Secondary domains based on trigrams
    upper = arch.get('upper_trigram', '')
    lower = arch.get('lower_trigram', '')
    
    # Trigram-to-domain mapping
    trigram_domains = {
        'Qian': ['transformer', 'video'],
        'Kun': ['diffusion', 'audio'],
        'Zhen': ['rlhf_alignment', 'safety'],
        'Xun': ['graph', 'multimodal'],
        'Kan': ['quant_efficiency', 'diffusion'],
        'Li': ['transformer', 'video'],
        'Gen': ['quant_efficiency', 'graph'],
        'Dui': ['rlhf_alignment', 'multimodal'],
    }
    
    secondary_domains = []
    if upper in trigram_domains:
        secondary_domains.extend(trigram_domains[upper])
    if lower in trigram_domains:
        secondary_domains.extend(trigram_domains[lower])
    secondary_domains = list(dict.fromkeys(secondary_domains))  # deduplicate
    
    # Collect keywords from primary + secondary domains
    domain_keyword_sets = {}
    for domain in [primary_domain] + secondary_domains:
        dk = domain_keywords.get(domain, {})
        domain_keyword_sets[domain] = {
            'top_words': dk.get('top_words', [])[:30],
            'top_symbols': dk.get('top_symbols', [])[:10],
            'top_numbers': dk.get('top_numbers', [])[:10],
            'paper_count': dk.get('paper_count', 0),
            'avg_lexical_density': dk.get('avg_lexical_density', 0),
            'avg_number_density': dk.get('avg_number_density', 0),
        }
    
    hexagram_domains[hid] = {
        'hexagram_id': int(hid),
        'name': arch['name'],
        'category': cat,
        'action': action,
        'upper_trigram': upper,
        'lower_trigram': lower,
        'primary_domain': primary_domain,
        'secondary_domains': secondary_domains,
        'domain_keywords': domain_keyword_sets,
        'position_summary': f"{cat} {action} — {primary_domain}",
    }

# Attach phase-specific domain keywords
phase_domain_map = defaultdict(list)
for pi in phase_individuals:
    hid = pi['hexagram_id']
    phase = pi['phase_temporal']
    phase_key = f"{hid}_{phase}"
    
    if hid in hexagram_domains:
        primary = hexagram_domains[hid]['primary_domain']
        dk = domain_keywords.get(primary, {})
        phase_domain_map[phase_key] = {
            'hexagram_id': int(hid),
            'phase_temporal': phase,
            'domain': primary,
            'phase_keywords': dk.get('top_words', [])[:20],
            'phase_symbols': dk.get('top_symbols', [])[:8],
        }

# Merge phase data into hexagram domains
for hid, hd in hexagram_domains.items():
    phase_keywords = []
    for phase in ['past', 'present', 'future', 'transition', 'resolution', 'dissolution', 'crystallization', 'void']:
        pk = phase_domain_map.get(f"{hid}_{phase}")
        if pk:
            phase_keywords.append(pk)
    hd['phase_domain_keywords'] = phase_keywords

# Write output
with OUT.open('w', encoding='utf-8') as f:
    json.dump(hexagram_domains, f, ensure_ascii=False, indent=2)

print(f'wrote {OUT}')
print(f'size MB: {OUT.stat().st_size / 1024 / 1024:.2f}')

# Sample output
print('\n=== Sample Domain Mappings ===')
for hid in ['1', '6', '7', '29', '64']:
    hd = hexagram_domains.get(hid, {})
    if hd:
        print(f"\n{hid}: {hd['name']} ({hd['category']} {hd['action']})")
        print(f"  primary: {hd['primary_domain']}")
        print(f"  secondary: {hd['secondary_domains']}")
        dk = hd['domain_keywords'].get(hd['primary_domain'], {})
        print(f"  top words: {dk.get('top_words', [])[:8]}")
        print(f"  papers: {dk.get('paper_count', 0)}")
