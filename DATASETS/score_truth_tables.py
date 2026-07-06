#!/usr/bin/env python3
import json, csv
from pathlib import Path
from collections import defaultdict, Counter
from kingwen_ternary_tables_complete import HEXAGRAM_BASE, EMOTIONAL_WEIGHTS, HEXAGRAM_INJECTION_SITE, YAO_VOCABULARY, PHASE_LINE_MAP, POROSITY_LEVELS

datasets = Path("DATASETS")

# Load flat CSV
flat = []
with open(datasets / "kingwen_oracle_flat (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        flat.append(row)

# Load master json
master = json.loads(Path("DATASETS/kingwen_oracle_master (1).json").read_text(encoding='utf-8'))
master_hex = master.get('hexagrams', {})
master_by_id = {}
if isinstance(master_hex, dict):
    master_by_id = {int(k): v for k, v in master_hex.items()}
elif isinstance(master_hex, list):
    for h in master_hex:
        master_by_id[h['hexagram_id']] = h

# Load other datasets
yao_lines = []
with open(datasets / "kingwen_oracle_yao_lines (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        yao_lines.append(row)

transitions = []
with open(datasets / "kingwen_transition_graph.csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        transitions.append(row)

em_ts = []
with open(datasets / "kingwen_emotional_timeseries (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        em_ts.append(row)

saves = []
with open(datasets / "kingwen_save_strings (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        saves.append(row)

pairs = []
with open(datasets / "kingwen_hexagram_pairs (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        pairs.append(row)

cat = []
with open(datasets / "kingwen_category_matrix (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        cat.append(row)

trigrams = []
with open(datasets / "kingwen_trigram_reference (1).csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        trigrams.append(row)

flat_by_id = {int(r['hexagram_id']): r for r in flat}
results = []

for hex_id in range(1, 65):
    row = {'hexagram_id': hex_id}
    base = HEXAGRAM_BASE.get(hex_id, {})
    inject = HEXAGRAM_INJECTION_SITE.get(hex_id, {})
    weights = EMOTIONAL_WEIGHTS.get(str(hex_id), {}) or EMOTIONAL_WEIGHTS.get(hex_id, {})
    vocab = YAO_VOCABULARY[0] if isinstance(YAO_VOCABULARY, (list, tuple)) and len(YAO_VOCABULARY) > 0 else {}

    f = flat_by_id.get(hex_id, {})
    m = master_by_id.get(hex_id, {})

    # Flat symbol fields
    row['name_match_flat'] = f.get('name') == base.get('name')
    row['binary_match_flat'] = f.get('binary') == base.get('binary_bottom_to_top')
    row['unicode_match_flat'] = f.get('unicode') == base.get('unicode')
    row['upper_match_flat'] = f.get('upper_trigram') == base.get('upper_trigram')
    row['lower_match_flat'] = f.get('lower_trigram') == base.get('lower_trigram')
    row['category_match_flat'] = f.get('category') == base.get('category')

    # Flat inject
    try:
        row['porosity_match_flat'] = int(f.get('porosity', -1)) == inject.get('porosity')
    except Exception:
        row['porosity_match_flat'] = False
    row['inject_primary_match_flat'] = f.get('inject_primary') == inject.get('primary_pool')
    row['inject_secondary_match_flat'] = f.get('inject_secondary') == inject.get('secondary_pool')

    # Master inject/emotions/reflections
    m_inject = m.get('inject_site', {}) if isinstance(m, dict) else {}
    row['inject_primary_match_master'] = m_inject.get('primary_pool') == inject.get('primary_pool')
    row['inject_secondary_match_master'] = m_inject.get('secondary_pool') == inject.get('secondary_pool')
    row['porosity_match_master'] = m_inject.get('porosity') == inject.get('porosity')
    row['reason_match_master'] = m_inject.get('reason') == inject.get('reason')

    mw = m.get('emotional_deltas', {}) if isinstance(m, dict) else {}
    row['voiceWeight_match_master'] = abs(float(mw.get('voiceWeight', 0)) - weights.get('voiceWeight', 0)) < 0.001
    row['coherence_match_master'] = abs(float(mw.get('coherence', 0)) - weights.get('coherence', 0)) < 0.001
    row['chaos_match_master'] = abs(float(mw.get('chaos', 0)) - weights.get('chaos', 0)) < 0.001
    row['whimsy_match_master'] = abs(float(mw.get('whimsy', 0)) - weights.get('whimsy', 0)) < 0.001
    row['darkTone_match_master'] = abs(float(mw.get('darkTone', 0)) - weights.get('darkTone', 0)) < 0.001

    mr = m.get('reflections', {}) if isinstance(m, dict) else {}
    row['past_match_master'] = bool(mr.get('past', '').strip())
    row['present_match_master'] = bool(mr.get('present', '').strip())
    row['future_match_master'] = bool(mr.get('future', '').strip())

    # Yao lines presence
    hex_yao = [y for y in yao_lines if int(y.get('hexagram_id', 0)) == hex_id]
    row['has_yao_lines'] = len(hex_yao) > 0
    row['yao_line_count'] = len(hex_yao)

    flat_score = sum([
        row.get('name_match_flat', False),
        row.get('binary_match_flat', False),
        row.get('unicode_match_flat', False),
        row.get('inject_primary_match_flat', False),
        row.get('inject_secondary_match_flat', False),
        row.get('porosity_match_flat', False),
    ])
    master_score = sum([
        row.get('inject_primary_match_master', False),
        row.get('inject_secondary_match_master', False),
        row.get('porosity_match_master', False),
        row.get('reason_match_master', False),
        row.get('voiceWeight_match_master', False),
        row.get('coherence_match_master', False),
        row.get('chaos_match_master', False),
        row.get('whimsy_match_master', False),
        row.get('darkTone_match_master', False),
        row.get('past_match_master', False),
        row.get('present_match_master', False),
        row.get('future_match_master', False),
    ])
    row['flat_score'] = flat_score
    row['master_score'] = master_score
    if master_score > flat_score:
        row['winner'] = 'master'
    elif flat_score > master_score:
        row['winner'] = 'flat'
    else:
        row['winner'] = 'tie'
    results.append(row)

# Print summary
total_flat = sum(r['flat_score'] for r in results)
total_master = sum(r['master_score'] for r in results)
flat_max = len(results) * 6
master_max = len(results) * 12
flat_wins = sum(1 for r in results if r['winner'] == 'flat')
master_wins = sum(1 for r in results if r['winner'] == 'master')
ties = sum(1 for r in results if r['winner'] == 'tie')

print("=== OVERALL ===")
print(f"Flat CSV score:  {total_flat}/{flat_max}  ({total_flat*100//flat_max if flat_max else 0}%)")
print(f"Master JSON score: {total_master}/{master_max}  ({total_master*100//master_max if master_max else 0}%)")
print(f"Per-hex wins: flat={flat_wins}, master={master_wins}, tie={ties}")

field_scores = {
    'name_match_flat': sum(r['name_match_flat'] for r in results),
    'binary_match_flat': sum(r['binary_match_flat'] for r in results),
    'unicode_match_flat': sum(r['unicode_match_flat'] for r in results),
    'inject_primary_match_flat': sum(r['inject_primary_match_flat'] for r in results),
    'inject_secondary_match_flat': sum(r['inject_secondary_match_flat'] for r in results),
    'porosity_match_flat': sum(r['porosity_match_flat'] for r in results),
    'inject_primary_match_master': sum(r['inject_primary_match_master'] for r in results),
    'inject_secondary_match_master': sum(r['inject_secondary_match_master'] for r in results),
    'porosity_match_master': sum(r['porosity_match_master'] for r in results),
    'reason_match_master': sum(r['reason_match_master'] for r in results),
    'voiceWeight_match_master': sum(r['voiceWeight_match_master'] for r in results),
    'coherence_match_master': sum(r['coherence_match_master'] for r in results),
    'chaos_match_master': sum(r['chaos_match_master'] for r in results),
    'whimsy_match_master': sum(r['whimsy_match_master'] for r in results),
    'darkTone_match_master': sum(r['darkTone_match_master'] for r in results),
    'past_match_master': sum(r['past_match_master'] for r in results),
    'present_match_master': sum(r['present_match_master'] for r in results),
    'future_match_master': sum(r['future_match_master'] for r in results),
}

print("\n=== FIELD SCORES ===")
for k, v in field_scores.items():
    pct = v * 100 // len(results)
    print(f"  {k}: {v}/{len(results)} ({pct}%)")

print("\n=== HEX-WIN BREAKDOWN ===")
for r in results:
    print(f"hex {r['hexagram_id']:>2}: flat={r['flat_score']}, master={r['master_score']} -> {r['winner']}")

# Additional dataset stats
print("\n=== DATASET STATS ===")
print(f"Flat CSV rows: {len(flat)}")
print(f"Master hexagrams: {len(master_by_id)}")
print(f"Yao lines rows: {len(yao_lines)}")
print(f"Transitions rows: {len(transitions)}")
print(f"Emotional timeseries rows: {len(em_ts)}")
print(f"Save strings rows: {len(saves)}")
print(f"Pairs rows: {len(pairs)}")
print(f"Category rows: {len(cat)}")
print(f"Trigram refs rows: {len(trigrams)}")
