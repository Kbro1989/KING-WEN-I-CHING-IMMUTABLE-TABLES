import hashlib, json, os, subprocess, sys
man = json.load(open(os.environ["MANIFEST"], encoding="utf-8"))
entries = {e["relative_path"]: e["sha256"] for e in man["manifest"]}
paths = [l.split("\t", 1)[1] for l in open(os.environ["SNAPFILE"], encoding="utf-8").read().splitlines() if l.startswith("A\t")]
assert len(paths) == 702 and len(set(paths)) == 702, f"path count {len(paths)}"
bad = []
for p in paths:
    h = hashlib.sha256(subprocess.check_output(["git", "show", f":{p}"])).hexdigest()
    if entries.get(p) != h:
        bad.append((p, entries.get(p), h))
if bad:
    for b in bad[:20]: print("MISMATCH", *b, file=sys.stderr)
    sys.exit(f"{len(bad)} mismatches")
print(f"ok:   {len(paths)} staged blobs match manifest")
