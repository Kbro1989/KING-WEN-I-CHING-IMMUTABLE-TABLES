"""
King Wen lexical gate: attach corpus-derived frequency profiles as initial parsing
expectations for expansion records. Uses actual paper frequency profiles from
paper_frequency_profiles.jsonl to set variable expectations per category/action.
"""
from pathlib import Path
import json
from collections import Counter, defaultdict

# Paths
CORPUS_PROFILES = (Path.home() / "Desktop" / "zotero/learning-corpus/paper_frequency_profiles.jsonl")
ROOT = Path(__file__).resolve().parent.parent
EXPANSION = ROOT / "kingwen_train_data" / "full_shotgun_expansion_all.jsonl"
OUT = ROOT / "kingwen_train_data" / "full_shotgun_expansion_lexical_gate.jsonl"

# Load corpus profiles
corpus = []
with CORPUS_PROFILES.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            corpus.append(json.loads(line))

print(f'corpus profiles: {len(corpus)}')

# Aggregate corpus statistics by dominant signal
signal_stats = defaultdict(lambda: {
    'count': 0,
    'avg_lexical_density': 0.0,
    'avg_number_density': 0.0,
    'avg_latex_density': 0.0,
    'top_words': Counter(),
    'top_symbols': Counter(),
    'top_signals': Counter(),
})

for cp in corpus:
    sig = cp.get('dominant_signal', 'general')
    stats = signal_stats[sig]
    stats['count'] += 1
    stats['avg_lexical_density'] += cp.get('lexical_density', 0)
    stats['avg_number_density'] += cp.get('number_density', 0)
    stats['avg_latex_density'] += cp.get('latex_density', 0)
    for w in cp.get('top_words', [])[:20]:
        stats['top_words'][w['w']] += w['c']
    for s in cp.get('top_symbols', [])[:10]:
        stats['top_symbols'][s['s']] += s['c']
    for sig_name, weight in cp.get('category_signals', {}).items():
        stats['top_signals'][sig_name] += weight

# Normalize
for sig, stats in signal_stats.items():
    count = max(stats['count'], 1)
    stats['avg_lexical_density'] = round(stats['avg_lexical_density'] / count, 6)
    stats['avg_number_density'] = round(stats['avg_number_density'] / count, 6)
    stats['avg_latex_density'] = round(stats['avg_latex_density'] / count, 6)
    stats['top_words'] = dict(stats['top_words'].most_common(30))
    stats['top_symbols'] = dict(stats['top_symbols'].most_common(15))
    stats['top_signals'] = dict(stats['top_signals'].most_common(5))

print('signal stats computed for:', list(signal_stats.keys()))

# Load expansion records
expansion = []
with EXPANSION.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            expansion.append(json.loads(line))

print(f'expansion records: {len(expansion)}')

# Map expansion categories to corpus signals
CATEGORY_TO_SIGNAL = {
    'sovereign': 'rlhf_alignment',
    'transformer': 'transformer',
    'dissipator': 'diffusion',
    'boundary': 'quant_efficiency',
}

ACTION_TO_SIGNAL = {
    'ASSERT': 'rlhf_alignment',
    'YIELD': 'transformer',
    'ADAPT': 'diffusion',
    'WAIT': 'quant_efficiency',
}

# Enrich each expansion record with corpus-derived expectations
enriched = 0
for rec in expansion:
    lp = rec.setdefault('label_payload', {})
    cat = lp.get('category', 'sovereign')
    action = lp.get('action', 'ASSERT')
    phase = lp.get('phase_temporal', 'present')
    
    # Derive signal from category/action
    signal = CATEGORY_TO_SIGNAL.get(cat) or ACTION_TO_SIGNAL.get(action) or 'general'
    stats = signal_stats.get(signal, signal_stats['general'])
    
    # Build expectations
    expectations = {
        'dominant_signal': signal,
        'category_bias': cat,
        'action_bias': action,
        'phase_bias': phase,
        'confidence': 0.85 if signal != 'general' else 0.5,
        'source': 'corpus_frequency_profile',
        'corpus_signal_stats': {
            'signal_count': stats['count'],
            'avg_lexical_density': stats['avg_lexical_density'],
            'avg_number_density': stats['avg_number_density'],
            'avg_latex_density': stats['avg_latex_density'],
            'top_words': stats['top_words'],
            'top_symbols': stats['top_symbols'],
            'top_signals': stats['top_signals'],
        },
        'variable_expectations': {
            'word_repetition_threshold': max(1, int(stats['avg_lexical_density'] * 1000)),
            'number_density_expected': stats['avg_number_density'],
            'symbol_density_expected': stats['avg_latex_density'],
            'high_frequency_words': list(stats['top_words'].keys())[:10],
            'high_frequency_symbols': list(stats['top_symbols'].keys())[:5],
        },
    }
    
    lp['initial_parsing_expectations'] = expectations
    enriched += 1

# Write enriched output
with OUT.open('w', encoding='utf-8') as f:
    for rec in expansion:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f'enriched records: {enriched}/{len(expansion)}')
print('wrote', OUT)
print('size MB:', round(OUT.stat().st_size / 1024 / 1024, 2))

# Sample expectations
for rec in expansion[:3]:
    lp = rec.get('label_payload', {})
    exp = lp.get('initial_parsing_expectations', {})
    print(f"\ncat={lp.get('category')} action={lp.get('action')} phase={lp.get('phase_temporal')}")
    print(f"  signal={exp.get('dominant_signal')} bias={exp.get('category_bias')}/{exp.get('action_bias')} conf={exp.get('confidence')}")
    print(f"  var_expectations={exp.get('variable_expectations')}")
