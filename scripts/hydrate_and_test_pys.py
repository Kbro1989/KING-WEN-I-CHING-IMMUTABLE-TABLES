#!/usr/bin/env python3
"""
Hydrate ALL_FILES.csv, enumerate every Python file, and run a pass:
- syntax check
- top-level import resolution (best-effort)
- runtime import smoke where safe (no side-effect files)
- failure-mode notes for anything that fails
"""
import ast, csv, sys, importlib.util, traceback
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "ALL-FILES.csv"
SKIP_DIRS = {"__pycache__", ".venv", "node_modules", "quantum-simulation-main",
             "tmp_broken_compare", "openjarvis_blueprints_extracted"}

def load_py_rows():
    rows = []
    with CSV.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("extension", "").lower() == ".py":
                rows.append(r)
    return rows

def syntax_ok(path: Path):
    try:
        ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return True, None
    except SyntaxError as e:
        return False, f"line {e.lineno}: {e.msg}  text={e.text!r}"

def top_level_modules(text: str):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    mods = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                mods.append(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
    return mods

def runnable_as_module(text: str):
    """True if the file appears to be a library module (no top-level print/sys.exit/etc.)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Expr,)):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id in {"print", "sys_exit", "exit", "quit"}:
                    return False
        if isinstance(node, ast.Import):
            continue
        if isinstance(node, ast.ImportFrom):
            continue
        # Any top-level statement beyond imports/expr-print is a side-effect candidate
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Expr)):
            return False
        # Expression that is NOT a print call
        if isinstance(node, ast.Expr) and not (isinstance(node.value, ast.Call) and
                                                 isinstance(node.value.func, ast.Name) and
                                                 node.value.func.id == "print"):
            # a bare expression at top level (e.g. a docstring-only file = OK; anything else suspicious)
            if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
                return False
    return True

def import_smoke(text: str, path: Path):
    """Best-effort importability check without executing file code.

    Returns (status, note, missing_names, runnable_as_module).
    status: 'ok' | 'import-missing' | 'not-runnable-as-module'
    """
    names = set()
    for node in ast.iter_child_nodes(ast.parse(text)):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    if not names:
        return "ok", None, [], True
    missing = []
    for n in names:
        spec = importlib.util.find_spec(n)
        if spec is None:
            missing.append(n)
    if missing:
        return "import-missing", None, missing, runnable_as_module(text)
    r = runnable_as_module(text)
    if not r:
        return "not-runnable-as-module", "top-level side-effect statements present; skip exec smoke", names, False
    return "ok", None, [], True

def main():
    rows = load_py_rows()
    print(f"ALL_FILES.csv python rows: {len(rows)}")
    total = len(rows)

    missing_disk = []
    syntax_fail = []
    import_smoke_fail = []
    not_runnable = []
    ok_names_present = []
    ok_no_imports = []

    for r in rows:
        rel = r["relative_path"]
        p = ROOT / rel
        size = int(r.get("size_bytes") or 0)
        if not p.exists():
            missing_disk.append((rel, size))
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        ok_syn, syn_note = syntax_ok(p)
        if not ok_syn:
            syntax_fail.append((rel, syn_note, size))
            continue
        mods = top_level_modules(text)
        status, note, missing, runnable = import_smoke(text, p)
        if status == "import-missing":
            import_smoke_fail.append((rel, missing, size, mods))
            continue
        if status == "not-runnable-as-module":
            not_runnable.append((rel, note, size, mods))
            continue
        if mods:
            ok_names_present.append((rel, size, mods))
        else:
            ok_no_imports.append((rel, size))

    print(f"total python rows in CSV: {total}")
    print(f"on disk: {len(rows) - len(missing_disk)}")
    print(f"missing on disk: {len(missing_disk)}")
    print()
    print(f"syntax ok (all): {len(rows) - len(missing_disk) - len(syntax_fail)}")
    print(f"syntax FAIL: {len(syntax_fail)}")
    print(f"import smoke FAIL (name not importable): {len(import_smoke_fail)}")
    print(f"not runnable as module (side-effect files): {len(not_runnable)}")
    print(f"ok names present: {len(ok_names_present)}")
    print(f"ok no imports: {len(ok_no_imports)}")
    print()

    if missing_disk:
        print("=== MISSING ON DISK (CSV says present, file not found) ===")
        for rel, size in missing_disk:
            print(f"  {rel}  csv_size={size}")
        print()

    if syntax_fail:
        print("=== SYNTAX FAIL ===")
        for rel, note, size in syntax_fail:
            print(f"  {rel}  {size}B  {note}")
        print()

    if import_smoke_fail:
        print("=== IMPORT-SMOKE FAIL (top-level imported names not found) ===")
        for rel, missing, size, mods in import_smoke_fail:
            print(f"  {rel}  {size}B  missing={missing}  all_imports={mods[:6]}{'...' if len(mods) > 6 else ''}")
        print()

    if not_runnable:
        print("=== NOT RUNNABLE AS MODULE (top-level side-effect files; skipped exec smoke) ===")
        for rel, note, size, mods in not_runnable[:80]:
            print(f"  {rel}  {size}B  imports={mods[:6]}{'...' if len(mods) > 6 else ''}  note={note}")
        if len(not_runnable) > 80:
            print(f"  ...and {len(not_runnable)-80} more")
        print()

    if ok_names_present:
        print("=== OK NAMES PRESENT (importable, module-shaped) ===")
        for rel, size, mods in ok_names_present[:40]:
            print(f"  {rel}  {size}B  {mods[:6]}{'...' if len(mods) > 6 else ''}")
        if len(ok_names_present) > 40:
            print(f"  ...and {len(ok_names_present)-40} more")
        print()

    if ok_no_imports:
        print("=== OK NO TOP-LEVEL IMPORTS ===")
        for rel, size in ok_no_imports[:40]:
            print(f"  {rel}  {size}B")
        if len(ok_no_imports) > 40:
            print(f"  ...and {len(ok_no_imports)-40} more")
        print()

if __name__ == "__main__":
    main()
