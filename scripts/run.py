import os
import sys
import runpy
from pathlib import Path

REPO = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES").resolve()
sys.path.insert(0, str(REPO))

# Provide the primary data source that the in-repo scripts expect.
import KING_WEN_TABLES  # noqa: F401

shared = {
    "output_dir": str(REPO),
    "HEXAGRAMS": KING_WEN_TABLES.HEXAGRAMS,
}

scripts = [
    "save registry",
    "test file",
    "generate deterministichash+temporalmath",
    "generate emotionalparser+narrativeengine",
    "generate oracle",
    "generate oracleengine.ts",
    "verifycation.py",
]

for name in scripts:
    path = REPO / name
    if not path.exists():
        print(f"MISSING {name}")
        continue
    print(f">>> RUN {name}")
    try:
        g = dict(shared)
        g["__file__"] = str(path)
        runpy.run_path(str(path), run_name="__main__", init_globals=g)
    except Exception as exc:
        print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    print()

print("=== done ===")
