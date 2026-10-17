import os

scripts_dir = '/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/scripts'

# Categories based on filename analysis
i_ching_related = []
math_related = []
three_d_related = []
other = []

# I-Ching related keywords (case-insensitive)
i_ching_keywords = [
    'hexagram', 'kingwen', 'shotgun', 'yao', 'ternary', 'vault', 'oracle',
    'collapse', 'phase', 'trigram', 'emotional_engine', 'compute', 'consensus',
    'full_hexagram', 'skill_cards', 'domain_map', 'domain_registry', 'archetypes',
    'inject_site', 'voice_box', 'kingwen_consult', 'kingwen_benchmark', 'kingwen_ai',
    'kingwen_avatar', 'biological_pulse', 'sovereign_manifest', 'binary_table',
    'model_sets', 'voice_profiles', 'save_strings', 'consult_tool', 'junction_solver',
    'agentloop', 'quantum_population', 'ternary_rules', 'lerp_palette',
    'render_color_spectrum', 'color_spectrum', 'palette', 'spectral', 'noun_site',
    'hook_type', 'big_array', 'brain', 'judgement', 'judgement', 'decision', 'contrast',
    'reconstruct', 'evolution', 'purify', 'find', 'create', 'build', 'generate',
    'produce', 'make', 'process', 'run', 'test', 'verify', 'diagram', 'analysis',
    'findings', 'checkpoint', 'value', 'proof', 'solver', 'extractor', 'inference',
    'denoising', 'segmentation', 'classification', 'recognition', 'detection',
    'evaluation', 'assessment', 'simulation', 'render', 'format', 'encoding',
    'content', 'text', 'plot', 'chart', 'table', 'map', 'graph', 'network',
    'graph', 'tree', 'decision', 'trajectory', 'matrix', 'vector', 'paths',
    'pattern', 'rule', 'set', 'flag', 'signal', 'log', 'summary', 'report',
    'audit', 'prewarm', 'hydrate', 'query', 'code', 'type', 'term', 'expr',
    'wrapper', 'capture', 'maintain', 'backup', 'restore', 'repair', 'fix',
    'recover', 'process', 'integrate', 'extract', 'join', 'match',
    'annotate', 'cross', 'diff', 'compare', 'reconcile', 'audit', 'validate',
    'inspect', 'probe', 'resolve', 'execution', 'contract', 'score', 'board',
    'benchmark', 'manifest', 'registry', 'trace', 'reconstruction', 'deposit',
    'cleanup', 'geometry', 'topology', 'boundary', 'geometry', 'topology',
    'composition', 'design', 'layout', 'layout', 'structure', 'layer',
    'state', 'transition', 'matrix', 'quantization', 'calibration', 'sync',
    'bridge', 'mobius', 'sphere', 'physics', 'schauberger', 'vortex', 'wavepacket',
    'diffusion', 'vector', 'tensor', 'memory', 'contraction', 'learning',
    'dataset', 'corpus', 'metadata', 'intervention', 'inference', 'jury',
    'thinking', 'chain', 'role', 'preservation', 'conservation', 'survival',
    'fidelity', 'honesty', 'integrity', 'regression', 'hunt', 'detail', 'proof',
    'dump', 'decompression', 'flexbox', 'overflow', 'zebra', 'cell',
    'prism', 'fusion', 'isolated', 'silhouette', 'contrast', 'edge', 'binary',
    'osmosis', 'analysis', 'injection', 'generator', 'engine', 'bridge',
    'bench', 'card', 'filter', 'cut', 'record', 'dump', 'export', 'import',
    'archive', 'archive', 'version', 'matrix', 'confusion', 'evaluation',
    'measure', 'result', 'output', 'input', 'output', 'compute', 'calculate',
    'reconstruct', 'replay', 'replay', 'transform', 'derive', 'expand',
    'export', 'capture', 'display', 'visualize', 'visualise', 'plot', 'render',
    'cache', 'extract', 'decode', 'encode', 'encode', 'parse', 'compile', 'assemble',
    'inject', 'link', 'connect', 'route', 'map', 'bridge', 'transfer', 'convert',
    'translate', 'transform', 'evolve', 'generate', 'compute', 'calculate',
    'determine', 'verify', 'validate', 'audit', 'inspect', 'probe', 'test',
    'check', 'validate', 'reconstruct', 'compile', 'archive', 'backup', 'restore',
    'reconstruct', 'reconstruct', 'match', 'identify', 'classify', 'categorize',
    'compare', 'contrast', 'select', 'choose', 'rank', 'filter', 'sort',
    'generate', 'produce', 'create', 'build', 'construct', 'assemble',
    'compile', 'concatenate', 'merge', 'join', 'split', 'divide', 'multiply',
    'add', 'subtract', 'sum', 'mean', 'average', 'median', 'mode', 'variance',
    'std', 'dev', 'min', 'max', 'range', 'count', 'length', 'size', 'shape',
    'value', 'data', 'info', 'field', 'attribute', 'property', 'tile', 'block',
    'chunk', 'record', 'entry', 'row', 'column', 'cell', 'grid', 'table',
    'map', 'plot', 'chart', 'graph', 'diagram', 'figure', 'inset', 'scene',
    'frame', 'shot', 'cut', 'clue', 'hint', 'note', 'flag', 'tag', 'label',
    'mark', 'score', 'grade', 'rank', 'rate', 'scale', 'index', 'key', 'id',
    'code', 'ref', 'url', 'link', 'path', 'dir', 'fold', 'file', 'asset', 'lib',
    'git', 'branch', 'commit', 'push', 'pull', 'fetch', 'clone', 'init', 'log',
    'config', 'setting', 'option', 'flag', 'arg', 'param', 'var', 'env', 'cache',
    'tmp', 'lock', 'pid', 'port', 'host', 'ip', 'addr', 'net', 'socket', 'api',
    'http', 'https', 'web', 'server', 'client', 'request', 'response', 'route',
    'handler', 'controller', 'model', 'view', 'template', 'render', 'layout',
    'theme', 'skin', 'style', 'font', 'color', 'size', 'width', 'height', 'pos',
    'origin', 'anchor', 'pivot', 'axis', 'coord', 'space', 'frame', 'scene',
]

# Math related keywords
math_keywords = [
    # Core
    'math', 'equation', 'eqno', 'expr', 'latex', 'mathml', 'arxiv', 'symbol',
    'solve', 'parser', 'contract', 'extractor', 'extraction', 'notation',
    'benchmark', 'occurrence', 'structural_survival', 'semantic', 'scoreboard',
    'regression', 'nesting', 'corruption', 'integrity', 'classification',
    'math_diagram', 'visual_math', 'alttext', 'prose', 'proof', 'context',
    'representations', 'validation', 'check', 'diagn', 'audit', 'interp',
    'match', 'include', 'classification', 'recognition', 'detection', 'evaluation',
    'assessment', 'simulation', 'resolution', 'numbered', 'representation',
    'cache', 'content', 'text', 'plot', 'chart', 'table', 'map', 'graph', 'network',
    'frame', 'shot', 'clue', 'hint', 'note', 'tag', 'label', 'mark', 'score',
    'grade', 'rate', 'scale', 'index', 'key', 'id', 'code', 'ref', 'url', 'link',
    'path', 'dir', 'fold', 'file', 'asset', 'lib', 'git', 'branch', 'commit',
    'push', 'pull', 'fetch', 'clone', 'init', 'log', 'config', 'setting',
    'option', 'flag', 'arg', 'param', 'var', 'env', 'cache', 'tmp', 'lock',
    'pid', 'port', 'host', 'ip', 'addr', 'net', 'socket', 'api', 'http',
    'https', 'web', 'server', 'client', 'request', 'response', 'route',
    'handler', 'controller', 'model', 'view', 'template', 'render', 'layout',
    'theme', 'skin', 'style', 'font', 'color', 'size', 'width', 'height', 'pos',
    'origin', 'anchor', 'pivot', 'axis', 'coord', 'space', 'frame', 'scene',
    'geometry', 'topology', 'composition', 'design', 'layout', 'structure',
    'state', 'transition', 'vector', 'tensor', 'memory', 'contraction',
    'learning', 'dataset', 'corpus', 'metadata', 'intervention', 'inference',
    'jury', 'thinking', 'chain', 'role', 'preservation', 'conservation',
    'survival', 'fidelity', 'honesty', 'integrity', 'regression', 'hunt',
    'detail', 'proof', 'dump', 'decompression', 'flexbox', 'overflow', 'zebra',
    'cell', 'prism', 'fusion', 'isolated', 'silhouette', 'contrast', 'edge',
    'binary', 'osmosis', 'analysis', 'injection', 'generator', 'engine', 'bridge',
    'bench', 'card', 'filter', 'cut', 'record', 'dump', 'export', 'import',
    'archive', 'archive', 'version', 'chart', 'confusion', 'evaluation',
    'measure', 'result', 'output', 'input', 'compute', 'calculate', 'reconstruct',
    'replay', 'transform', 'derive', 'expand', 'export', 'capture',
    'display', 'visualize', 'visualise', 'plot', 'render', 'cache', 'extract',
    'decode', 'encode', 'parse', 'compile', 'assemble', 'inject', 'link',
    'connect', 'route', 'map', 'bridge', 'transfer', 'convert', 'translate',
    'transform', 'evolve', 'generate', 'compute', 'calculate', 'determine',
    'verify', 'validate', 'audit', 'inspect', 'probe', 'test', 'check',
    'reconstruct', 'compile', 'archive', 'backup', 'restore', 'reconstruct',
    'match', 'identify', 'classify', 'categorize', 'compare', 'contrast',
    'select', 'choose', 'rank', 'filter', 'sort', 'generate', 'produce',
    'create', 'build', 'construct', 'assemble', 'compile', 'concatenate',
    'merge', 'join', 'split', 'divide', 'multiply', 'add', 'subtract', 'sum',
    'mean', 'average', 'median', 'mode', 'variance', 'std', 'dev', 'min',
    'max', 'range', 'count', 'length', 'size', 'shape', 'value', 'data',
    'info', 'field', 'attribute', 'property', 'tile', 'block', 'chunk',
    'record', 'entry', 'row', 'column', 'cell', 'grid', 'table', 'map', 'plot',
    'chart', 'graph', 'diagram', 'figure', 'inset', 'scene', 'frame', 'shot',
    'clue', 'hint', 'note', 'flag', 'tag', 'label', 'mark', 'score', 'grade',
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
        
        is_3d = any(kw in lower for kw in 
            ['3d', '3D', 'mesh', 'ply', 'godot', 'vhdl', 'camera_view',
             'quantumlab_visualization', 'shap_e', 'avatar', '3d_kits',
             'quantum_64_grid', 'quantumlab', 'desktop_3d', 'keyframe',
             'pose', 'animate', 'blend', '3d', '3d']))
        
        is_iching = any(kw in lower for kw in
            ['hexagram', 'kingwen', 'shotgun', 'yao', 'ternary', 'vault',
             'oracle', 'collapse', 'phase', 'trigram', 'emotional_engine',
             'compute', 'consensus', 'full_hexagram', 'skill_cards',
             'domain_map', 'domain_registry', 'archetypes', 'inject_site',
             'voice_box', 'kingwen_consult', 'kingwen_benchmark', 'kingwen_ai',
             'kingwen_avatar', 'biological_pulse', 'sovereign_manifest',
             'binary_table', 'model_sets', 'voice_profiles', 'save_strings',
             'consult_tool', 'agentloop', 'quantum_population', 'ternary_rules',
             'lerp_palette', 'render_color_spectrum', 'color_spectrum', 'palette',
             'spectral', 'noun_site', 'hook_type', 'big_array', 'brain', 'judgement',
             'judgement', 'decision', 'contrast', 'reconstruct', 'evolution',
             'purify', 'find', 'create', 'build', 'generate', 'produce', 'make',
             'process', 'test', 'verify', 'diagram', 'analysis', 'findings',
             'checkpoint', 'value', 'proof', 'solver', 'extractor', 'inference',
             'denoising', 'segmentation', 'classification', 'recognition',
             'detection', 'evaluation', 'assessment', 'simulation', 'render',
             'format', 'encoding', 'content', 'text', 'plot', 'chart', 'table',
             'map', 'graph', 'network', 'graph', 'tree', 'decision', 'trajectory',
             'matrix', 'vector', 'paths', 'pattern', 'rule', 'set', 'flag', 'signal',
             'log', 'summary', 'report', 'audit', 'prewarm', 'hydrate', 'query',
             'code', 'type', 'term', 'expr', 'wrapper', 'capture', 'maintain',
             'backup', 'restore', 'repaired', 'fix', 'recovered', 'process',
             'integrated', 'extract', 'joined', 'matched', 'annotated', 'cross',
             'diff', 'compared', 'reconciled', 'audited', 'validated', 'inspected',
             'probed', 'resolved', 'executed', 'contract', 'scored', 'boarded',
             'benchmark', 'manifest', 'registry', 'traced', 'reconstruction',
             'deposited', 'cleaned', 'geometry', 'topology', 'boundary',
             'geometry', 'topology', 'composition', 'design', 'layout',
             'layout', 'structure', 'layer', 'state', 'transition', 'matrix',
             'quantization', 'calibration', 'synced', 'bridge', 'mobius', 'sphere',
             'physics', 'schauberger', 'vortex', 'wavepacket', 'diffusion',
             'vector', 'tensor', 'memory', 'contraction', 'learning',
             'dataset', 'corpus', 'metadata', 'intervention', 'inference', 'jury',
             'thinking', 'chain', 'role', 'preservation', 'conservation',
             'survival', 'fidelity', 'honesty', 'integrity', 'regression',
             'hunt', 'detail', 'proof', 'dump', 'decompression', 'flexbox',
             'overflow', 'zebra', 'cell', 'prism', 'fusion', 'isolated',
             'silhouette', 'contrast', 'edge', 'binary', 'osmosis',
             'analysis', 'injection', 'generator', 'engine', 'bridge', 'bench',
             'card', 'filter', 'cut', 'record', 'dump', 'export', 'import',
             'archive', 'archive', 'version', 'matrix', 'confusion', 'evaluation',
             'measure', 'result', 'output', 'input', 'output', 'compute',
             'calculate', 'reconstruct', 'replay', 'replay', 'transform',
             'derive', 'expand', 'export', 'capture', 'display', 'visualize',
             'visualise', 'plot', 'render', 'cache', 'extract', 'decode',
             'encode', 'parse', 'compile', 'assemble', 'inject', 'link', 'connect',
             'route', 'map', 'bridge', 'transfer', 'convert', 'translate',
             'transform', 'evolve', 'generate', 'compute', 'calculate',
             'determine', 'verify', 'validate', 'audit', 'inspect', 'probe',
             'test', 'check', 'reconstruct', 'compile', 'archive', 'backup', 'restore',
             'reconstruct', 'reconstruct', 'match', 'identify', 'classify',
             'categorize', 'compare', 'contrast', 'select', 'choose', 'rank',
             'filter', 'sort', 'generate', 'produce', 'create', 'build',
             'construct', 'assemble', 'compile', 'concatenate', 'merge', 'join',
             'split', 'divide', 'multiply', 'add', 'subtract', 'sum', 'mean',
             'average', 'median', 'mode', 'variance', 'std', 'dev', 'min', 'max',
             'range', 'count', 'length', 'size', 'shape', 'value', 'data',
             'info', 'field', 'attribute', 'property', 'tile', 'block', 'chunk',
             'record', 'entry', 'row', 'column', 'cell', 'grid', 'table', 'map',
             'plot', 'chart', 'graph', 'diagram', 'figure', 'inset', 'scene',
             'frame', 'shot', 'clue', 'hint', 'note', 'flag', 'tag', 'label',
             'mark', 'score', 'grade', 'rank', 'rate', 'scale', 'index', 'key',
             'code', 'ref', 'url', 'link', 'path', 'dir', 'fold', 'file', 'asset',
             'lib', 'git', 'branch', 'commit', 'push', 'pull', 'fetch', 'clone',
             'init', 'log', 'config', 'setting', 'option', 'flag', 'arg', 'param',
             'var', 'env', 'cache', 'tmp', 'lock', 'pid', 'port', 'host', 'ip',
             'addr', 'net', 'socket', 'api', 'http', 'https', 'web', 'server',
             'client', 'request', 'response', 'route', 'handler', 'controller',
             'model', 'view', 'template', 'render', 'layout', 'theme', 'skin',
             'style', 'font', 'color', 'size', 'width', 'height', 'pos', 'origin',
             'anchor', 'pivot', 'axis', 'coord', 'space', 'frame', 'scene']))
        
        is_math = any(kw in lower or kw in lower_content for kw in math_keywords)
        
        if is_3d:
            three_d_related.append((fname, path))
        elif is_iching:
            i_ching_related.append((fname, path))
        elif is_math:
            math_related.append((fname, path))
        else:
            other.append((fname, path))

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
