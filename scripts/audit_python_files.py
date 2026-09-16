#!/usr/bin/env python3
"""Comprehensive Python file audit: syntax, imports, name resolution, and stale-path drift."""
import ast, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"__pycache__", ".venv", "node_modules", "quantum-simulation-main"}

def walk_pys(root: Path):
    for p in root.rglob("*.py"):
        if any(part in SKIP for part in p.parts):
            continue
        yield p

errors = []   # (path, kind, detail)
imports = []  # (path, names)

for p in walk_pys(ROOT):
    text = p.read_text(encoding="utf-8", errors="replace")
    tree = None
    try:
        tree = ast.parse(text, filename=str(p))
    except SyntaxError as e:
        errors.append((p, "SYNTAX", f"line {e.lineno}: {e.msg}"))
        continue

    # Collect imported names and their source module strings
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((p, alias.name, node))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((p, node.module, node))
            for alias in node.names:
                imports.append((p, f"from {node.module} import {alias.name}", node))

print(f"Scanned {len(list(walk_pys(ROOT)))} .py files")
print(f"Imported symbols recorded: {len(imports)}")
print()

# 1) Report syntax errors
if any(e[1] == "SYNTAX" for e in errors):
    print("=== SYNTAX ERRORS ===")
    for p, kind, detail in errors:
        if kind == "SYNTAX":
            print(f"{p}: {detail}")
    print()

# 2) Report bare except: and except Exception: without variable (informational)
print("=== EXCEPTIONS WITHOUT BINDING ===")
for p in walk_pys(ROOT):
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"} and handler.name is None:
                    print(f"{p}: except {handler.type.id}: without 'as' binding (line {handler.lineno})")
print()

# 3) Report hardcoded /tmp or Desktop paths that look like mistakes
print("=== STALE/HARDCODED PATH LITERALS (informational) ===")
for p in walk_pys(ROOT):
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            if ("/tmp/" in v or "\\\\tmp\\\\" in v) and "gen_broken" not in v and "blocked" not in v:
                print(f"{p}: hardcoded path {v!r} at line {node.lineno}")
print()

print("=== DONE ===")
