import subprocess
import sys
from pathlib import Path

repo = Path(r"C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES").resolve()
scripts = [
    repo / "save registry",
    repo / "test file",
    repo / "generate deterministichash+temporalmath",
    repo / "generate emotionalparser+narrativeengine",
    repo / "generate oracle",
    repo / "generate oracleengine.ts",
    repo / "verifycation.py",
]

for path in scripts:
    text = path.read_text(encoding="utf-8")
    updated = 'output_dir = r"' + str(repo).replace("\\", "/") + '"\n' + text
    path.write_text(updated, encoding="utf-8")
    print(f"Patched output_dir -> {path.name}")

results = {}
for path in scripts:
    res = subprocess.run([sys.executable, str(path)], cwd=str(repo), capture_output=True, text=True)
    results[path.name] = {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
    print(f"--- {path.name} (rc={res.returncode}) ---")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr)

print("\n=== Manifest ===")
for p in sorted(repo.rglob("*")):
    if p.is_file() and p.name != ".gitignore":
        print(p.relative_to(repo))
