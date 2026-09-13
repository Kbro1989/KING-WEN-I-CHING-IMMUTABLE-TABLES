"""
analyze_inversion_opposition.py - inspect polar opposition across inversion pairs.
"""

import json
from pathlib import Path

profiles_path = Path('C:/Users/krist/Desktop/voicebox/backend/exports/kingwen_64_npc_voice_profiles.json')
with open(profiles_path, 'r', encoding='utf-8') as f:
    profiles = json.load(f)

profile_by_hex = {p['hexagram_id']: p for p in profiles}

inversion_pairs = [
    (1, 2), (3, 49), (4, 50), (5, 36), (6, 35), (7, 14), (8, 13),
    (9, 15), (10, 16), (11, 12), (17, 18), (19, 33), (20, 34),
    (21, 48), (22, 47), (23, 43), (24, 44), (25, 46), (26, 45),
    (27, 28), (29, 30), (31, 42), (32, 41), (37, 39), (38, 40),
    (51, 57), (52, 58), (53, 54), (55, 60), (56, 59), (61, 62), (63, 64)
]

voice_vars = ['pitch_f0_hz', 'duration_scale', 'energy_db', 'pitch_shift_hz', 'gain_db']
axis_vars = ['chaos', 'whimsy', 'darkTone', 'coherence', 'voiceWeight']

print('Inversion pairs - voice variable opposition')
print('=' * 90)

for h1, h2 in inversion_pairs:
    p1 = profile_by_hex[h1]
    p2 = profile_by_hex[h2]
    pros1 = p1['fastspeech_prosody']
    pros2 = p2['fastspeech_prosody']
    ax1 = p1['5_axis_vector']
    ax2 = p2['5_axis_vector']

    name1 = p1['name']
    name2 = p2['name']

    f0_1 = pros1['pitch_f0_hz']
    dur_1 = pros1['duration_scale']
    energy_1 = pros1['energy_db']
    ps_1 = p1.get('pitch_shift_hz', 0.0)
    g_1 = p1.get('gain_db', 0.0)

    f0_2 = pros2['pitch_f0_hz']
    dur_2 = pros2['duration_scale']
    energy_2 = pros2['energy_db']
    ps_2 = p2.get('pitch_shift_hz', 0.0)
    g_2 = p2.get('gain_db', 0.0)

    deltas = {
        'pitch_f0_hz': f0_1 - f0_2,
        'duration_scale': dur_1 - dur_2,
        'energy_db': energy_1 - energy_2,
        'pitch_shift_hz': ps_1 - ps_2,
        'gain_db': g_1 - g_2,
    }

    ax1 = p1['5_axis_vector']
    ax2 = p2['5_axis_vector']

    deltas['chaos'] = ax1['chaos'] - ax2['chaos']
    deltas['whimsy'] = ax1['whimsy'] - ax2['whimsy']
    deltas['darkTone'] = ax1['darkTone'] - ax2['darkTone']
    deltas['coherence'] = ax1['coherence'] - ax2['coherence']
    deltas['voiceWeight'] = ax1['voiceWeight'] - ax2['voiceWeight']

    voice_opp = sum(1 for v in voice_vars if abs(deltas[v]) > 0.1)
    axis_opp = sum(1 for v in axis_vars if abs(deltas[v]) > 0.02)

    total_voice_delta = sum(abs(deltas[v]) for v in voice_vars)
    total_axis_delta = sum(abs(deltas[v]) for v in axis_vars)

    voice_signs = [1 if deltas[v] > 0 else -1 for v in voice_vars]
    axis_signs = [1 if deltas[v] > 0 else -1 for v in axis_vars]
    voice_polarity = 1 - (sum(abs(s) for s in voice_signs) / len(voice_signs))
    axis_polarity = 1 - (sum(abs(s) for s in axis_signs) / len(axis_signs))

    print(f'Hex {h1:2d} {name1[:28]:28s} <-> Hex {h2:2d} {name2[:28]:28s}')
    print(f'  F0:        {f0_1:6.2f} <-> {f0_2:6.2f}  diff={deltas["pitch_f0_hz"]:+6.2f}')
    print(f'  Dur:       {dur_1:6.4f} <-> {dur_2:6.4f}  diff={deltas["duration_scale"]:+6.4f}')
    print(f'  Energy:    {energy_1:+6.2f} <-> {energy_2:+6.2f}  diff={deltas["energy_db"]:+6.2f}')
    print(f'  Pitch sh:  {ps_1:+6.2f} <-> {ps_2:+6.2f}  diff={deltas["pitch_shift_hz"]:+6.2f}')
    print(f'  Gain:      {g_1:+6.2f} <-> {g_2:+6.2f}  diff={deltas["gain_db"]:+6.2f}')
    print(f'  Chaos:     {ax1["chaos"]:.4f} <-> {ax2["chaos"]:.4f}  diff={deltas["chaos"]:+6.4f}')
    print(f'  Whimsy:    {ax1["whimsy"]:.4f} <-> {ax2["whimsy"]:.4f}  diff={deltas["whimsy"]:+6.4f}')
    print(f'  DarkTone:  {ax1["darkTone"]:.4f} <-> {ax2["darkTone"]:.4f}  diff={deltas["darkTone"]:+6.4f}')
    print(f'  Coherence: {ax1["coherence"]:.4f} <-> {ax2["coherence"]:.4f}  diff={deltas["coherence"]:+6.4f}')
    print(f'  VoiceW:    {ax1["voiceWeight"]:.4f} <-> {ax2["voiceWeight"]:.4f}  diff={deltas["voiceWeight"]:+6.4f}')
    print(f'  Mode:      {p1["hermes_mode"]:20s} <-> {p2["hermes_mode"]:20s}')
    print(f'  Element:   {p1["element_subset"]:8s} <-> {p2["element_subset"]:8s}  Agent: {p1["agent_type"]:10s} <-> {p2["agent_type"]:10s}  Domain: {p1["domain"]:10s} <-> {p2["domain"]:10s}')
    print(f'  Opposition: voice_opp={voice_opp}/{len(voice_vars)} axis_opp={axis_opp}/{len(axis_vars)} | polar voice={voice_polarity:.2f} axis={axis_polarity:.2f}')
    print(f'  Total voice diff={total_voice_delta:.3f} | Total axis diff={total_axis_delta:.4f}')
    print()

print('=' * 90)
print('AGGREGATE: inversion pair opposition statistics')
print('=' * 90)

voice_deltas = {v: [] for v in voice_vars}
axis_deltas = {v: [] for v in axis_vars}
opp_counts_voice = []
opp_counts_axis = []
polarity_voice = []
polarity_axis = []

for h1, h2 in inversion_pairs:
    p1 = profile_by_hex[h1]
    p2 = profile_by_hex[h2]
    pros1 = p1['fastspeech_prosody']
    pros2 = p2['fastspeech_prosody']
    ax1 = p1['5_axis_vector']
    ax2 = p2['5_axis_vector']

    f0_1 = pros1['pitch_f0_hz']
    dur_1 = pros1['duration_scale']
    energy_1 = pros1['energy_db']
    ps_1 = p1.get('pitch_shift_hz', 0.0)
    g_1 = p1.get('gain_db', 0.0)
    f0_2 = pros2['pitch_f0_hz']
    dur_2 = pros2['duration_scale']
    energy_2 = pros2['energy_db']
    ps_2 = p2.get('pitch_shift_hz', 0.0)
    g_2 = p2.get('gain_db', 0.0)

    voice_deltas['pitch_f0_hz'].append(f0_1 - f0_2)
    voice_deltas['duration_scale'].append(dur_1 - dur_2)
    voice_deltas['energy_db'].append(energy_1 - energy_2)
    voice_deltas['pitch_shift_hz'].append(ps_1 - ps_2)
    voice_deltas['gain_db'].append(g_1 - g_2)

    axis_deltas['chaos'].append(ax1['chaos'] - ax2['chaos'])
    axis_deltas['whimsy'].append(ax1['whimsy'] - ax2['whimsy'])
    axis_deltas['darkTone'].append(ax1['darkTone'] - ax2['darkTone'])
    axis_deltas['coherence'].append(ax1['coherence'] - ax2['coherence'])
    axis_deltas['voiceWeight'].append(ax1['voiceWeight'] - ax2['voiceWeight'])

    v1_list = [f0_1, dur_1, energy_1, ps_1, g_1]
    v2_list = [f0_2, dur_2, energy_2, ps_2, g_2]
    a1_list = [ax1['chaos'], ax1['whimsy'], ax1['darkTone'], ax1['coherence'], ax1['voiceWeight']]
    a2_list = [ax2['chaos'], ax2['whimsy'], ax2['darkTone'], ax2['coherence'], ax2['voiceWeight']]

    voice_opp = sum(1 for i in range(len(voice_vars)) if abs(v1_list[i] - v2_list[i]) > 0.1)
    axis_opp = sum(1 for i in range(len(axis_vars)) if abs(a1_list[i] - a2_list[i]) > 0.02)
    opp_counts_voice.append(voice_opp)
    opp_counts_axis.append(axis_opp)

    vs = [1 if v1_list[i] - v2_list[i] > 0 else -1 for i in range(len(voice_vars))]
    as_ = [1 if a1_list[i] - a2_list[i] > 0 else -1 for i in range(len(axis_vars))]
    voice_sign_flip_frac = sum(1 for s in vs if s < 0) / len(vs)
    axis_sign_flip_frac = sum(1 for s in as_ if s < 0) / len(as_)
    voice_polarity = 1 - voice_sign_flip_frac
    axis_polarity = 1 - axis_sign_flip_frac

print()
print('Voice variable deltas across 32 inversion pairs:')
for var in voice_vars:
    deltas = voice_deltas[var]
    print(f'  {var:14s}: mean diff={sum(deltas)/len(deltas):+.3f}  min diff={min(deltas):+.3f}  max diff={max(deltas):+.3f}  mean_abs={sum(abs(d) for d in deltas)/len(deltas):.3f}')

print()
print('Axis variable deltas across 32 inversion pairs:')
for var in axis_vars:
    deltas = axis_deltas[var]
    print(f'  {var:14s}: mean diff={sum(deltas)/len(deltas):+.4f}  min diff={min(deltas):+.4f}  max diff={max(deltas):+.4f}  mean_abs={sum(abs(d) for d in deltas)/len(deltas):.4f}')

print()
print(f'Voice opposition: mean pairs with clear direction = {sum(opp_counts_voice)/len(opp_counts_voice):.2f}/{len(voice_vars)}')
print(f'Axis opposition: mean pairs with clear direction = {sum(opp_counts_axis)/len(opp_counts_axis):.2f}/{len(axis_vars)}')
print(f'Voice polarity (1=all same sign): mean={sum(polarity_voice)/len(polarity_voice):.2f}')
print(f'Axis polarity: mean={sum(polarity_axis)/len(polarity_axis):.2f}')

print()
print('Polarity index vs Voicebox pitch_shift correlation:')
from kingwen_ternary_tables_complete import HEXAGRAM_BASE

def polarity_index(hex_id):
    binary = HEXAGRAM_BASE[hex_id]['binary_bottom_to_top']
    yang = binary.count('1')
    yin = binary.count('0')
    return (yang - yin) / 6.0

pitch_shift_pairs = []
f0_pairs = []
for h1, h2 in inversion_pairs:
    pi1 = polarity_index(h1)
    pi2 = polarity_index(h2)
    ps1 = profile_by_hex[h1].get('pitch_shift_hz', 0.0)
    ps2 = profile_by_hex[h2].get('pitch_shift_hz', 0.0)
    f1 = profile_by_hex[h1]['fastspeech_prosody']['pitch_f0_hz']
    f2 = profile_by_hex[h2]['fastspeech_prosody']['pitch_f0_hz']
    pitch_shift_pairs.append((pi1 - pi2, ps1 - ps2))
    f0_pairs.append((pi1 - pi2, f1 - f2))

def corr(pairs):
    n = len(pairs)
    sx = sum(a for a, b in pairs)
    sy = sum(b for a, b in pairs)
    sxy = sum(a*b for a, b in pairs)
    sx2 = sum(a*a for a, b in pairs)
    sy2 = sum(b*b for a, b in pairs)
    denom = ((n*sx2 - sx*sx) * (n*sy2 - sy*sy)) ** 0.5
    if denom == 0:
        return 0
    return (n*sxy - sx*sy) / denom

print(f'  pitch_shift vs polarity diff: r={corr(pitch_shift_pairs):.4f}')
print(f'  pitch_f0 vs polarity diff: r={corr(f0_pairs):.4f}')

print()
print('Polarity index (yang-yin ratio, +/-1 = pure yang/pure yin):')
for h in range(1, 65):
    pi = polarity_index(h)
    if abs(pi) > 0.5:
        name = HEXAGRAM_BASE[h]["name"][:30]
        print(f'  Hex {h:2d}: polarity={pi:+.3f}  {name}')

print()
print('Inversion pairs where polarity INDEX matches Voicebox opposition direction:')
for h1, h2 in inversion_pairs:
    pi1 = polarity_index(h1)
    pi2 = polarity_index(h2)
    ps1 = profile_by_hex[h1].get('pitch_shift_hz', 0.0)
    ps2 = profile_by_hex[h2].get('pitch_shift_hz', 0.0)
    f1 = profile_by_hex[h1]['fastspeech_prosody']['pitch_f0_hz']
    f2 = profile_by_hex[h2]['fastspeech_prosody']['pitch_f0_hz']
    ax1 = profile_by_hex[h1]['5_axis_vector']
    ax2 = profile_by_hex[h2]['5_axis_vector']

    polarity_diff = pi1 - pi2
    ps_diff = ps1 - ps2
    f0_diff = f1 - f2

    ps_aligned = (polarity_diff > 0 and ps_diff > 0) or (polarity_diff < 0 and ps_diff < 0)
    f0_aligned = (polarity_diff > 0 and f0_diff > 0) or (polarity_diff < 0 and f0_diff < 0)
    chaos_aligned = (polarity_diff > 0 and ax1['chaos'] - ax2['chaos'] > 0) or (polarity_diff < 0 and ax1['chaos'] - ax2['chaos'] < 0)
    coherence_aligned = (polarity_diff > 0 and ax1['coherence'] - ax2['coherence'] > 0) or (polarity_diff < 0 and ax1['coherence'] - ax2['coherence'] < 0)

    if ps_aligned and f0_aligned:
        direc = 'yang-high' if polarity_diff > 0 else 'yin-high'
        print(f'    {h1:2d}<->{h2:2d}: polarity {pi1:+.2f}<->{pi2:+.2f} ({direc}) | ps {ps1:+.2f}<->{ps2:+.2f} | f0 {f1:.1f}<->{f2:.1f} | chaos {ax1["chaos"]:.3f}<->{ax2["chaos"]:.3f} | coh {ax1["coherence"]:.3f}<->{ax2["coherence"]:.3f}')
