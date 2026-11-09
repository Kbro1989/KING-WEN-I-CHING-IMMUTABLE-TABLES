#!/usr/bin/env python3
"""Read-only contract audit: trace imports and call relationships."""
import ast, sys, os

REPO_ROOT = '/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'
os.chdir(REPO_ROOT)

files = [
    os.path.join(REPO_ROOT, 'scripts', 'pdf_visual_analysis_layer.py'),
    os.path.join(REPO_ROOT, 'scripts', 'pdf_visual_corpus_integrator.py'),
    os.path.join(REPO_ROOT, 'scripts', 'targeted_math_detector.py'),
    os.path.join(REPO_ROOT, 'scripts', 'delimiter_aware_structural_recovery.py'),
    os.path.join(REPO_ROOT, 'scripts', 'font_aware_math_classifier.py'),
    os.path.join(REPO_ROOT, 'scripts', 'mathml_parser.py'),
]

print("=== IMPORT TRACE ===")
for f in files:
    path = 'scripts/' + f
    try:
        with open(path) as fh:
            tree = ast.parse(fh.read())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.imports:
                    imports.add(a.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        print(f'{f}: imports {sorted(imports)}')
    except Exception as e:
        print(f'{f}: ERROR {e}')

print()
print("=== CALL GRAPH (from visual layer) ===")
with open('scripts/pdf_visual_analysis_layer.py') as fh:
    visual_source = fh.read()

import re
func_defs = re.findall(r'def\s+(\w+)\s*\(', visual_source)
print(f"Functions in visual layer: {func_defs}")

imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', visual_source)
all_imports = set()
for imp in imports:
    for x in imp:
        if x:
            all_imports.add(x.split('.')[0])
print(f"Imports: {sorted(all_imports)}")

calls = set(re.findall(r'(\w+)\s*\(', visual_source))
for c in list(calls):
    if c in ('import', 'from', 'def', 'print', 'return', 'len', 'round', 'sum', 'min', 'max', 'open', 'json', 'Path', 'datetime', 'timezone', 'argparse', 'fitz', 'sys'):
        calls.discard(c)
print(f"Call sites (excluding stdlib): {sorted(calls)}")

print()
print("=== DO VISUAL LAYER IMPORTS CALL DELIMITER RECOVERY? ===")
with open(os.path.join(REPO_ROOT, 'scripts', 'pdf_visual_analysis_layer.py')) as fh:
    vl = fh.read()
print(f"  from delimiter_aware_structural_recovery import: {'delimiter_aware_structural_recovery' in vl}")
print(f"  from font_aware_math_classifier import: {'font_aware_math_classifier' in vl}")
print(f"  from mathml_parser import: {'mathml_parser' in vl}")
print(f"  from targeted_math_detector import: {'targeted_math_detector' in vl}")
