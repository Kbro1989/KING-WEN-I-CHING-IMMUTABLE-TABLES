#!/usr/bin/env python3
"""Fix remaining hardcoded KING-WEN subpath references (backslash variants, .resolve() calls, etc.)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FIXES = {
    # file -> list of (old_string, new_string)
    Path("output/build_hexagram_archetypes.py"): [
        (r"shotgun_path = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_train_data\full_shotgun_expansion_all.jsonl')",
         'ROOT = Path(__file__).resolve().parent.parent\nshotgun_path = ROOT / "kingwen_train_data" / "full_shotgun_expansion_all.jsonl"'),
        (r"registry_path = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\data\hexagram-registry.json')",
         'registry_path = ROOT / "data" / "hexagram-registry.json"'),
        (r"out_dir = Path(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\output')",
         'out_dir = ROOT / "output"'),
    ],
    Path("scripts/run.py"): [
        (r'REPO = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES").resolve()',
         'REPO = Path(__file__).resolve().parent.parent'),
    ],
    Path("scripts/run_generators.py"): [
        (r'repo = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES").resolve()',
         'repo = Path(__file__).resolve().parent.parent'),
    ],
    Path("scripts/sandbox_verify_final.py"): [
        (r'p = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")',
         'ROOT = Path(__file__).resolve().parent.parent\np = ROOT / "kingwen_ternary_tables_complete.py"'),
    ],
    Path("scripts/query_layer_probe.py"): [
        (r'IMMUTABLE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")',
         'ROOT = Path(__file__).resolve().parent.parent\nIMMUTABLE_PATH = ROOT / "kingwen_ternary_tables_complete.py"'),
        (r'ENGINE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\emotional_engine.py")',
         'ENGINE_PATH = ROOT / "emotional_engine.py"'),
        (r'OUTPUT_DIR = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\docs\query_probe")',
         'OUTPUT_DIR = ROOT / "docs" / "query_probe"'),
    ],
    Path("scripts/full_pool_voice_pick.py"): [
        (r'IMMUTABLE_PATH = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\kingwen_ternary_tables_complete.py")',
         'ROOT = Path(__file__).resolve().parent.parent\nIMMUTABLE_PATH = ROOT / "kingwen_ternary_tables_complete.py"'),
    ],
    Path("scripts/build_full_hexagram_vocabulary.py"): [
        ("ARCHETYPES = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_coder_archetypes.csv')",
         'ROOT = Path(__file__).resolve().parent.parent\nARCHETYPES = ROOT / "output" / "hexagram_coder_archetypes.csv"'),
        ("OUT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_full_vocabulary.json')",
         'OUT = ROOT / "output" / "hexagram_full_vocabulary.json"'),
    ],
    Path("scripts/kingwen_lexical_gate.py"): [
        ("EXPANSION = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_train_data/full_shotgun_expansion_all.jsonl')",
         'ROOT = Path(__file__).resolve().parent.parent\nEXPANSION = ROOT / "kingwen_train_data" / "full_shotgun_expansion_all.jsonl"'),
        ("OUT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/kingwen_train_data/full_shotgun_expansion_lexical_gate.jsonl')",
         'OUT = ROOT / "kingwen_train_data" / "full_shotgun_expansion_lexical_gate.jsonl"'),
    ],
    Path("scripts/map_hexagram_domains.py"): [
        ("ARCHETYPES = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_coder_archetypes.csv')",
         'ROOT = Path(__file__).resolve().parent.parent\nARCHETYPES = ROOT / "output" / "hexagram_coder_archetypes.csv"'),
        ("PHASE_INDIVIDUALS = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_phase_individuals.csv')",
         'PHASE_INDIVIDUALS = ROOT / "output" / "hexagram_phase_individuals.csv"'),
        ("TRANSLATIONS = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_translations.json')",
         'TRANSLATIONS = ROOT / "output" / "hexagram_translations.json"'),
        ("OUT = Path('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/output/hexagram_domain_keywords.json')",
         'OUT = ROOT / "output" / "hexagram_domain_keywords.json"'),
    ],
    Path("learn/scripts/wiki_math_parser.py"): [
        (r'wikitext = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES\learn\exports\wiki_math_sample.wikitext.txt").read_text(encoding="utf-8")',
         'ROOT = Path(__file__).resolve().parent.parent.parent\nwikitext = (ROOT / "learn" / "exports" / "wiki_math_sample.wikitext.txt").read_text(encoding="utf-8")'),
    ],
}

fixed = 0
for relpath, replacements in FIXES.items():
    filepath = ROOT / relpath
    if not filepath.exists():
        print(f"[SKIP] {relpath} — file not found")
        continue
    text = filepath.read_text(encoding='utf-8')
    original = text
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
    if text != original:
        filepath.write_text(text, encoding='utf-8')
        print(f"[FIXED] {relpath}")
        fixed += 1
    else:
        print(f"[NO-OP] {relpath} — pattern not found in file")

print(f"\nFixed {fixed} additional files.")
