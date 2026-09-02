#!/usr/bin/env python3
"""Fix all .md files: collapse_full_128 -> shotgun_expand, fix single-hex examples."""
import re

FIXES = [
    # (file_path, old_string, new_string)
    ('DATASETS/SKILL-kingwen-jspace-widget.md',
     'Regenerate `kingwen-512-full.json` via `collapse_full_128()`',
     'Regenerate `kingwen-512-full.json` via `shotgun_expand()`'),
    ('DATASETS/SKILL-kingwen-jspace-widget.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    
    ('docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md',
     '  -d \'{"hexagram_id": 1, "phase_id": 1}\'',
     '  -d \'{"hexagram_id": 1, "phase_id": 1}\'  # example: hexagram 1 of 64'),
    
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     'collapse_full_128_output.json', 'shotgun_expand_output.json'),
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     '`collapse_full_128_output.json`', '`shotgun_expand_output.json`'),
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     '3.1MB canonical snapshot', 'live shotgun expansion output'),
    ('docs/KING-WEN-RESEARCH-GUIDE.md',
     '3.1MB canonical', 'live shotgun expansion'),
    
    ('docs/KING-WEN-RESEARCH-CHECKLIST.md',
     '`collapse_full_128(50)`', '`shotgun_expand(emotional_input=50)`'),
    ('docs/KING-WEN-RESEARCH-CHECKLIST.md',
     'collapse_full_128(50)', 'shotgun_expand(emotional_input=50)'),
    ('docs/KING-WEN-RESEARCH-CHECKLIST.md',
     'from emotional_engine import collapse_full_128', 'from scripts.full_hexagram_shotgun import shotgun_expand'),
    
    ('KINGWEN_AGENT_ONBOARDING.md',
     '`collapse_full_128()`, the core expansion function',
     '`shotgun_expand()`, the core expansion function (64 hexagrams × 8 phases = 512 states)'),
    
    ('docs/kingwen-jspace-domain-layer-2026-07-11.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('docs/kingwen-jspace-domain-layer-2026-07-11.md',
     'collapse_full_128()', 'shotgun_expand()'),
    
    ('docs/kingwen-quantum-methods-2026-07-11.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('docs/kingwen-quantum-methods-2026-07-11.md',
     'collapse_full_128()', 'shotgun_expand()'),
    
    ('docs/kingwen-superposition-expansion-plan-2026-07-11.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('docs/kingwen-superposition-expansion-plan-2026-07-11.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('docs/kingwen-superposition-expansion-plan-2026-07-11.md',
     'collapse_full_128', 'shotgun_expand'),
    ('docs/kingwen-superposition-expansion-plan-2026-07-11.md',
     'test_collapse_full_128.py', 'test_collapse_full_512.py'),
    
    ('docs/README.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('docs/README.md',
     'collapse_full_128', 'shotgun_expand'),
    
    ('learn/exports/integration_map_2026-07-11.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('learn/exports/integration_map_2026-07-11.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('learn/exports/integration_map_2026-07-11.md',
     'collapse_full_128', 'shotgun_expand'),
    ('learn/exports/integration_map_2026-07-11.md',
     'collapse_full_128_output.json', 'shotgun_expand_output.json'),
    ('learn/exports/integration_map_2026-07-11.md',
     'Because hexagram 1 has voiceWeight≈0.95 and coherence≈0.98, it dominates the weighted score across ALL `emotional_input` values 0..100, causing `consensus_hexagram_id` to always resolve to hexagram 1.',
     'The consensus is the full 512-state quantum wave packet — all 64 hexagrams × 8 phases weighted together. The `consensus_hexagram_id` is the statistical mode of the full wave, not a single-hex collapse.'),
    
    ('learn/specs/blueprint-mined-data-integration.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('learn/specs/blueprint-mined-data-integration.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('learn/specs/blueprint-mined-data-integration.md',
     'collapse_full_128', 'shotgun_expand'),
    
    ('learn/specs/kingwen-jarvis-megatron-interconnections.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('learn/specs/kingwen-jarvis-megatron-interconnections.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('learn/specs/kingwen-jarvis-megatron-interconnections.md',
     'collapse_full_128', 'shotgun_expand'),
    ('learn/specs/kingwen-jarvis-megatron-interconnections.md',
     'test_collapse_full_128.py', 'test_collapse_full_512.py'),
    
    ('README.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('README.md',
     'collapse_full_128', 'shotgun_expand'),
    
    ('docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md',
     'collapse_full_128_output.json', 'shotgun_expand_output.json'),
    ('docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('docs/AUDIT_QUANTUM_3D_SHAPE_E_2026-08-21.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    
    ('docs/cross-verification-checklist-2026-09-01.md',
     'collapse_full_128_output.json', 'shotgun_expand_output.json'),
    ('docs/cross-verification-checklist-2026-09-01.md',
     'collapse_full_128()', 'shotgun_expand()'),
    ('docs/cross-verification-checklist-2026-09-01.md',
     '`collapse_full_128()`', '`shotgun_expand()`'),
    ('docs/cross-verification-checklist-2026-09-01.md',
     'test_collapse_full_128.py', 'test_collapse_full_512.py'),
]

# Group by file
from collections import defaultdict
file_fixes = defaultdict(list)
for path, old, new in FIXES:
    file_fixes[path].append((old, new))

for path, fixes in file_fixes.items():
    with open(path, encoding='utf-8') as f:
        content = f.read()
    for old, new in fixes:
        content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {path}")

print("\n=== ALL MD FILES FIXED ===")
