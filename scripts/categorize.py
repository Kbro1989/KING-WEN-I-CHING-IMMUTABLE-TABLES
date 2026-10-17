import os

scripts_dir = '/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts'

# Categories based on filename analysis
i_ching_related = []
math_related = []
three_d_related = []
other = []

# Explicitly 3D/3D engine related
three_d_keywords = [
    '3d', '3D', 'mesh', 'mesh', 'ply', 'godot', 'vhdl', 'camera_view',
    'quantumlab_visualization', 'shap_e', 'avatar', '3d_kits',
    'quantum_64_grid', 'quantumlab', 'desktop_3d', 'snake',
    '3D_anim', 'keyframe', 'pose', 'animate', 'blend'
]

# I-Ching related
i_ching_keywords = [
    'hexagram', 'kingwen-', 'kingwen_', 'shotgun', 'yao',
    'ternary', 'vault', 'oracle', 'collapse', 'phase', 'trigram',
    'emotional_engine', '_compute', 'consensus', 'full_hexagram',
    'skill_cards', 'hexagram_skill', 'domain_map', 'domain_registry',
    'archetypes', 'inject_site', 'voice_box', 'kingwen_consult',
    'kingwen_benchmark', 'kingwen_ai', 'kingwen_avatar',
    'biological_pulse', 'sovereign_manifest', 'binary_table',
    'model_sets', 'voice_profiles', 'save_strings', 'save_string',
    'consult_tool', 'junction_solver', 'agentloop', 'quantum_population',
    'ternary_rules', 'lerp_palette', 'render_color_spectrum',
    'color_spectrum', 'palette', 'spectral', 'noun_site', 'hook_type',
    'big_array', 'decode', 'fee', 'blanket', 'lens', 'inout', 'hall',
    'horizon', 'pairing', 'match', 'puzzle', 'reverse', 'round',
    'route', 'pairwise', 'puzzle', 'rain', 'bridge', 'quote', 'schauberger',
    'compute', 'quantum', 'godot', 'vortex', 'wave_packet', 'wavefunction',
    'accurate', 'deriv', 'run', 'verify', 'probe', 'inspect', 'mult',
    'expansion', 'states', 'resolve', 'resolved', 'binary',
]

# Math related
math_keywords = [
    'math', 'equation', 'pdf', 'latex', 'mathml', 'arxiv',
    'symbol', 'solve_', 'solve', 'parser', 'contract',
    'extractor', 'extraction', 'notation', 'benchmark', 'occurrence',
    'structural_survival', 'semantic', 'scoreboard', 'regression',
    'nesting', 'corruption', 'integrity', 'classification',
    'math_diagram', 'visual_math', 'alttext', 'prose', 'proof',
    'context', 'notations', 'notation', 'resolution', 'numbered',
    'representation', 'validation', 'check', 'diagn', 'audit',
    'impl', 'interp', 'match', 'include'
]

for root, dirs, files in os.walk(scripts_dir):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        fname = f[:-3]
        content = ''
        with open(path, 'r', errors='ignore') as fh:
            content = fh.read(2000)
        
        lower = fname.lower()
        lower_content = content.lower()
        
        is_math = any(kw in lower or kw in lower_content for kw in math_keywords)
        is_iching = any(kw in lower for kw in i_ching_keywords)
        is_3d = any(kw in lower for kw in three_d_keywords)
        
        if is_3d:
            three_d_related.append((fname, path))
        elif is_iching:
            i_ching_related.append((fname, path))
        elif is_math:
            math_related.append((fname, path))
        else:
            other.append((fname, path))

# Dedup and sort
def uniq(lst):
    seen = set()
    result = []
    for n, p in lst:
        if n not in seen:
            seen.add(n)
            result.append((n, p))
    return sorted(result, key=lambda x: x[0])

three_d_related = uniq(three_d_related)
i_ching_related = uniq(i_ching_related)
math_related = uniq(math_related)
other = uniq(other)

print(f"3D/3D-engine related: {len(three_d_related)}")
for n, p in three_d_related:
    print(f"  {n}")

print(f"\nI-Ching related: {len(i_ching_related)}")
for n, p in i_ching_related:
    print(f"  {n}")

print(f"\nMath/PDF/HTML parsing related: {len(math_related)}")
for n, p in math_related:
    print(f"  {n}")

print(f"\nOther (unclassified): {len(other)}")
for n, p in other:
    print(f"  {n}")
