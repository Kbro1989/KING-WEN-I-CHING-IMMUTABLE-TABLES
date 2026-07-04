#!/usr/bin/env python3
"""Runnable entry point: run all generators in dependency order."""
from __future__ import annotations

import runpy
from pathlib import Path

REPO = Path(__file__).resolve().parent
scripts = [
    REPO / "verify_registry.py",
    REPO / "generate_types.py",
    REPO / "generate_utils.py",
    REPO / "generate_parser.py",
    REPO / "generate_engine.py",
    REPO / "generate_tests.py",
]

for path in scripts:
    print(f">>> RUN {path.name}")
    g = {"__file__": str(path)}
    runpy.run_path(str(path), run_name="__main__", init_globals=g)
    print()

print("=== generation complete ===")
