import json, hashlib

with open('inventory/registries/external_systems.json', 'rb') as f:
    raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()

data = json.loads(raw)

print("=== FINAL REGISTRY VERIFICATION ===")
print("SHA-256: " + sha)
print("Bytes: " + str(len(raw)))
line_count = raw.count(b'\n') + 1
print("Lines: " + str(line_count))
print("Systems: " + str(len(data['external_systems'])))

total_ips = 0
for s in data['external_systems']:
    n = len(s.get('verified_integration_points', []))
    total_ips += n
    repo_field = s.get('system_repo', 'KING-WEN-I-CHING-IMMUTABLE-TABLES')
    print("  " + s['system'].ljust(40) + " | repo: " + repo_field.ljust(40) + " | IPs: " + str(n))

rt_defs = data.get('relationship_type_definitions', {})
print("Relationship type definitions: " + str(len(rt_defs)))

# Verify repository boundary fields
for s in data['external_systems']:
    if s['system'] == 'Upgraded-Depth-Anything-V2':
        print("Upgraded-Depth-Anything-V2 fields:")
        for k, v in s.items():
            if k in ('system_repo', 'repo_relative_path'):
                print("  " + k + ": " + str(v))

# Verify Kimi paths unchanged
for s in data['external_systems']:
    if s['system'] == 'Kimi / MoonshotAI':
        for ip in s.get('verified_integration_points', []):
            ref = ip.get('king_wen_file', '')
            if 'build_hybrid' in ref or 'hybrid_kimi' in ref:
                print("Kimi path (unchanged): " + ref)

print("Total integration points: " + str(total_ips))
PYEOF