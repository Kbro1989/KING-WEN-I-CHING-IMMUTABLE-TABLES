"""Build hexagram archetype/individual CSV+JSON outputs from full_shotgun_expansion_all.jsonl"""
import json, csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
shotgun_path = ROOT / "kingwen_train_data" / "full_shotgun_expansion_all.jsonl"
registry_path = ROOT / "data" / "hexagram-registry.json"
out_dir = ROOT / "output"
out_dir.mkdir(exist_ok=True)

# Load registry
with registry_path.open(encoding='utf-8') as f:
    registry = json.load(f)

# Load shotgun index by hexagram
hex_data = defaultdict(list)
with shotgun_path.open(encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        lp = rec.get('label_payload', {})
        hid = lp.get('hexagram_id')
        if hid:
            hex_data[int(hid)].append(lp)

print(f'Loaded {len(hex_data)} hexagrams from shotgun')

# 1. hexagram_coder_archetypes.csv — one row per hexagram
archetype_rows = []
for hid in range(1, 65):
    entries = hex_data.get(hid, [])
    if not entries:
        continue
    sample = entries[0]
    sym = sample.get('hexagram_symbols', {})
    reg_entry = registry.get(str(hid), {})
    tnm = sample.get('tool_native_map', {})
    cat = sample.get('category', '')
    primary_tool = tnm.get(cat.lower(), tnm.get('generation', 'codegen'))
    archetype_rows.append({
        'hexagram_id': hid,
        'name': reg_entry.get('name', sym.get('name', '')),
        'chinese': reg_entry.get('chinese', sym.get('chinese', '')),
        'pinyin': reg_entry.get('pinyin', ''),
        'binary': reg_entry.get('binary', sym.get('binary', '')),
        'category': cat,
        'action': sample.get('action', ''),
        'coder_specialty': sample.get('coder_specialty', ''),
        'rs3_actionable': sample.get('rs3_actionable', ''),
        'primary_tool': primary_tool,
        'archetype': f"{cat} {sample.get('action', '')} — {sample.get('coder_specialty', '')} coder; RS3:{sample.get('rs3_actionable', '')}",
        'upper_trigram': sym.get('upper_trigram', ''),
        'lower_trigram': sym.get('lower_trigram', ''),
    })

with open(out_dir / 'hexagram_coder_archetypes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['hexagram_id','name','chinese','pinyin','binary','category','action','coder_specialty','rs3_actionable','primary_tool','archetype','upper_trigram','lower_trigram'])
    writer.writeheader()
    writer.writerows(archetype_rows)
print(f'Wrote {len(archetype_rows)} archetype rows')

# 2. hexagram_phase_individuals.csv — one row per (hexagram, phase)
individual_rows = []
for hid in range(1, 65):
    entries = hex_data.get(hid, [])
    if not entries:
        continue
    reg_entry = registry.get(str(hid), {})
    name = reg_entry.get('name', entries[0].get('hexagram_symbols', {}).get('name', ''))
    for lp in entries:
        subsets = lp.get('personality_subsets', [])
        primary_subset = subsets[0] if subsets else {}
        pool_names = primary_subset.get('pool_names', [])
        expression = primary_subset.get('expression', '')
        tnm = lp.get('tool_native_map', {})
        cat = lp.get('category', '')
        tool_role = tnm.get(cat.lower(), tnm.get('generation', 'codegen'))
        individual_rows.append({
            'hexagram_id': hid,
            'hexagram_name': name,
            'phase_temporal': lp.get('phase_temporal', ''),
            'phase_bits': lp.get('phase_bits', 0),
            'yao_key': lp.get('yao_vocabulary', {}).get('old_yang', lp.get('yao_vocabulary', {}).get('stable_yang', '')),
            'pool_names': '|'.join(pool_names[:3]),
            'expression': expression[:200] if expression else '',
            'tool_role': tool_role,
            'category': cat,
            'action': lp.get('action', ''),
            'state_fidelity': lp.get('quantum_superposition', {}).get('state_fidelity', ''),
            'megatron_head': lp.get('quantum_superposition', {}).get('megatron_target_head', ''),
            'voice_mode': lp.get('hermes_layer', {}).get('voice_mode', ''),
        })

with open(out_dir / 'hexagram_phase_individuals.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['hexagram_id','hexagram_name','phase_temporal','phase_bits','yao_key','pool_names','expression','tool_role','category','action','state_fidelity','megatron_head','voice_mode'])
    writer.writeheader()
    writer.writerows(individual_rows)
print(f'Wrote {len(individual_rows)} individual rows')

# 3. hexagram_translations.json — full mapping
translations = {}
for hid in range(1, 65):
    entries = hex_data.get(hid, [])
    if not entries:
        continue
    reg_entry = registry.get(str(hid), {})
    sample = entries[0]
    sym = sample.get('hexagram_symbols', {})
    phases = []
    for lp in entries:
        phases.append({
            'phase': lp.get('phase_temporal', ''),
            'phase_bits': lp.get('phase_bits', 0),
            'yao_vocabulary': lp.get('yao_vocabulary', {}),
            'inject_site': lp.get('inject_site', {}),
            'tool_native_map': lp.get('tool_native_map', {}),
            'skill_cards': lp.get('skill_cards', [])[:3],
            'personality_subsets': lp.get('personality_subsets', [])[:2],
            'quantum_superposition': lp.get('quantum_superposition', {}),
            'hermes_layer': lp.get('hermes_layer', {}),
            'avalokiteshvara_arm': lp.get('avalokiteshvara_arm', {}),
            'jkd_pedagogy_anchor': lp.get('jkd_pedagogy_anchor', {}),
            'coder_specialty': lp.get('coder_specialty', ''),
            'rs3_actionable': lp.get('rs3_actionable', ''),
        })
    translations[str(hid)] = {
        'hexagram_id': hid,
        'name': reg_entry.get('name', sym.get('name', '')),
        'chinese': reg_entry.get('chinese', sym.get('chinese', '')),
        'pinyin': reg_entry.get('pinyin', ''),
        'binary': reg_entry.get('binary', sym.get('binary', '')),
        'unicode': sym.get('unicode', ''),
        'upper_trigram': sym.get('upper_trigram', ''),
        'lower_trigram': sym.get('lower_trigram', ''),
        'category': sample.get('category', ''),
        'action': sample.get('action', ''),
        'coder_specialty': sample.get('coder_specialty', ''),
        'rs3_actionable': sample.get('rs3_actionable', ''),
        'tool_native_map': sample.get('tool_native_map', {}),
        'phases': phases,
    }

with open(out_dir / 'hexagram_translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
print(f'Wrote translations for {len(translations)} hexagrams')

print('\n=== OUTPUT FILES ===')
for fname in ['hexagram_coder_archetypes.csv', 'hexagram_phase_individuals.csv', 'hexagram_translations.json']:
    fp = out_dir / fname
    print(f'{fname}: {fp.stat().st_size:,} bytes')
