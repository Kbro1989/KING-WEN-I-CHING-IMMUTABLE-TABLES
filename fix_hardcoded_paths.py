#!/usr/bin/env python3
"""
Surgical find-and-replace for hardcoded desktop paths across the King Wen repo.
Replaces `Path(r"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")`
with `Path(__file__).resolve().parent` (or .parent.parent for nested files).

Also handles variants: forward-slash, backslash, quoted, raw strings.
Does NOT touch external paths (voicebox, shap-e, rsmv, collisionvis, etc.) — those
are cross-repo references that genuinely need configuration, not __file__ tricks.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# The exact string we're replacing (KING-WEN repo self-references only)
KINGWEN_PATH_PATTERNS = [
    r'Path\(r?"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES"\)',
    r'Path\(r?"C:\\\\Users\\\\krist\\\\Desktop\\\\KING-WEN-I-CHING-IMMUTABLE-TABLES"\)',
    r"Path\(r?'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'\)",
    r"Path\(r?'C:\\\\Users\\\\krist\\\\Desktop\\\\KING-WEN-I-CHING-IMMUTABLE-TABLES'\)",
]

# Also catch sys.path.insert with the raw string (not wrapped in Path)
SYSPATH_PATTERNS = [
    r'"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES"',
    r"'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES'",
]

# Specific subpath references (e.g. pointing to a specific file inside the repo)
SUBPATH_PATTERNS = [
    (r'Path\(r?"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/([^"]+)"\)', r'kingwen_ternary_tables_complete.py'),
    (r"Path\(r?'C:\\\\Users\\\\krist\\\\Desktop\\\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\\\([^']+)'\)", None),
]


def depth_from_root(filepath: Path) -> int:
    """How many .parent calls needed to reach repo root from file's directory."""
    rel = filepath.resolve().parent.relative_to(ROOT)
    return len(rel.parts) + 1  # +1 because parent gets us to the directory, we need repo root


def get_replacement(filepath: Path) -> str:
    """Get the correct Path(__file__).resolve().parent[.parent...] for this file."""
    depth = depth_from_root(filepath)
    if depth == 1:
        return 'Path(__file__).resolve().parent'
    else:
        return 'Path(__file__).resolve()' + '.parent' * depth


def fix_file(filepath: Path, dry_run: bool = False) -> list:
    """Fix hardcoded KING-WEN paths in a single file. Returns list of changes made."""
    try:
        text = filepath.read_text(encoding='utf-8')
    except Exception:
        return []

    original = text
    changes = []
    replacement = get_replacement(filepath)

    # 1. Replace Path("C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES")
    for pattern in KINGWEN_PATH_PATTERNS:
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text)
            changes.append(f'  Path(...KING-WEN...) -> {replacement}')

    # 2. Replace bare string references to the repo path used in sys.path.insert etc.
    #    But only when it's the FULL repo path, not a subpath
    for pattern in SYSPATH_PATTERNS:
        if re.search(pattern, text):
            # Check it's not already inside a Path() call (already handled above)
            # Only replace bare string references
            bare_check = text
            text = re.sub(
                r'sys\.path\.insert\(0,\s*' + pattern + r'\)',
                f'sys.path.insert(0, str({replacement}))',
                text
            )
            if text != bare_check:
                changes.append(f'  sys.path.insert bare string -> str({replacement})')

    # 3. Replace subpath references like Path("C:/.../kingwen_ternary_tables_complete.py")
    for variant in [
        r'Path\(r?"C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/([^"]+)"\)',
        r"Path\(r?'C:\\\\Users\\\\krist\\\\Desktop\\\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\\\([^']+)'\)",
    ]:
        matches = re.finditer(variant, text)
        for m in matches:
            subpath = m.group(1).replace('\\\\', '/')
            old = m.group(0)
            new = f'{replacement} / "{subpath}"'
            text = text.replace(old, new)
            changes.append(f'  Subpath {subpath} -> {replacement} / "{subpath}"')

    if text != original:
        if not dry_run:
            filepath.write_text(text, encoding='utf-8')
        return changes
    return []


def main():
    dry_run = '--dry-run' in sys.argv

    py_files = sorted(
        f for f in ROOT.rglob('*.py')
        if '__pycache__' not in str(f)
        and 'node_modules' not in str(f)
        and f.name != 'fix_hardcoded_paths.py'  # don't fix ourselves
    )

    total_fixed = 0
    for f in py_files:
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue

        if 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES' not in text and \
           'C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES' not in text:
            continue

        changes = fix_file(f, dry_run=dry_run)
        if changes:
            rel = f.relative_to(ROOT)
            mode = '[DRY RUN]' if dry_run else '[FIXED]'
            print(f'{mode} {rel}')
            for c in changes:
                print(c)
            total_fixed += 1

    print(f'\n{"Would fix" if dry_run else "Fixed"} {total_fixed} files.')


if __name__ == '__main__':
    main()
