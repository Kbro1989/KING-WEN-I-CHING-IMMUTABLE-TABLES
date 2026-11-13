#!/usr/bin/env python3
"""Staged blob SHA-256 verifier — reads name-status file and compares against manifest."""
import hashlib, json, os, subprocess, sys

def main():
    if len(sys.argv) < 2:
        print("Usage: staged_sha_check.py <name-status-file>", file=sys.stderr)
        sys.exit(1)
    
    name_status_file = sys.argv[1]
    man_path = os.environ.get("MANIFEST", "PUBLICATION_MANIFEST.json")
    
    with open(man_path, encoding="utf-8") as f:
        man = json.load(f)
    entries = {e["relative_path"]: e["sha256"] for e in man["manifest"]}
    
    paths = []
    with open(name_status_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("A	") or line.startswith("M	"):
                paths.append(line.split("\t", 1)[1].strip())
    
    assert len(paths) == 704 and len(set(paths)) == 704, f"path count {len(paths)}"
    
    bad = []
    for p in paths:
        h = hashlib.sha256(subprocess.check_output(["git", "show", f":{p}"])).hexdigest()
        if entries.get(p) != h:
            bad.append((p, entries.get(p), h))
    
    if bad:
        for b in bad[:20]:
            print("MISMATCH", *b, file=sys.stderr)
        sys.exit(f"{len(bad)} mismatches")
    
    print(f"ok:   {len(paths)} staged blobs match manifest")

if __name__ == "__main__":
    main()
