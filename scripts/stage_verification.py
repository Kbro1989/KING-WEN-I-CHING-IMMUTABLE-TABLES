import json, hashlib, os

path = 'inventory/registries/external_systems.json'
with open(path, 'rb') as f:
    raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()

data = json.loads(raw)
print("=== Staged Registry Verification ===")
print(f"SHA-256: {sha}")
print(f"Bytes: {len(raw)}")
line_count = raw.count(b'\n') + 1
print(f"Lines: {line_count}")

systems = data['external_systems']
print(f"Systems: {len(systems)}")

total_ips = 0
for s in systems:
    n = len(s.get('verified_integration_points', []))
    total_ips += n
print(f"Integration points: {total_ips}")

rt_defs = data.get('relationship_type_definitions', {})
print(f"Relationship type definitions: {len(rt_defs)}")

print()
print("=== Path Verification ===")
checks = ['emotional_engine.py', 'kingwen_ternary_tables_complete.py', 'run_image-depth_8bit.py']
for fpath in checks:
    exists = os.path.exists(os.path.join('/c/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES', fpath))
    print(f"  {fpath:45s} | {'EXISTS' if exists else 'MISSING'}")

print()
print("=== Staged Files ===")
print("  inventory/registries/external_systems.json")
print("  docs/external-systems-reconciliation-2026-11-11.md")
print("  scripts/write_external_registry.py")
print()
print("=== Modified Files (outside scope) ===")
print("  KINGWEN_AGENT_ONBOARDING.md")
print("  king-wen-workflow-paths.md")
print("  lua-math-tool.md")
print()
print("=== Final Disposition ===")
print("Review scope: staging-boundary (file-level inspection)")
print("Source-level approval: NOT yet granted")
print("Commit: NOT authorized")
print("Push: NOT authorized")
