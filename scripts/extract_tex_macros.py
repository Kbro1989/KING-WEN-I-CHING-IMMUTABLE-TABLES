#!/usr/bin/env python3
"""Extract macro definitions from arxiv TeX source to resolve shorthand."""
import io
import json
import re
import sys
import tarfile
import urllib.request

ARXIV_ID = sys.argv[1] if len(sys.argv) > 1 else "2006.11239"
VERSION = sys.argv[2] if len(sys.argv) > 2 else "v2"

req = urllib.request.Request(
    f"https://arxiv.org/e-print/{ARXIV_ID}{VERSION}",
    headers={"User-Agent": "Mozilla/5.0"},
)
raw = urllib.request.urlopen(req, timeout=60).read()

with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
    tex = None
    for m in tar.getmembers():
        if m.name.endswith(".tex"):
            tex = tar.extractfile(m).read().decode("utf-8", "replace")
            print(f"FILE: {m.name} ({m.size} bytes)")
            break

if not tex:
    print("no .tex found")
    sys.exit(1)

print()
print("=== Custom macro definitions ===")
# \newcommand{\name}[n]{body}  OR  \def\name{body}
macros = {}

pat_newcommand = re.compile(r"\\newcommand\s*\{?\\([a-zA-Z@]+)\}?\s*(?:\[(\d+)\])?\s*\{")
for m in pat_newcommand.finditer(tex):
    name = m.group(1)
    nargs = m.group(2)
    # brace-match the body
    i = m.end() - 1
    depth = 0
    body_start = i + 1
    j = i
    while j < len(tex):
        if tex[j] == "{":
            depth += 1
        elif tex[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = tex[body_start:j]
    macros[name] = {"nargs": int(nargs) if nargs else 0, "body": body}

pat_def = re.compile(r"\\def\s*\\([a-zA-Z@]+)\s*\{")
for m in pat_def.finditer(tex):
    name = m.group(1)
    i = m.end() - 1
    depth = 0
    body_start = i + 1
    j = i
    while j < len(tex):
        if tex[j] == "{":
            depth += 1
        elif tex[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    macros[name] = {"nargs": 0, "body": tex[body_start:j]}

for name, info in sorted(macros.items()):
    print(f"  \\{name} [{info['nargs']} args] -> {info['body'][:70]}")

print()
print(f"Total custom macros: {len(macros)}")

# The key ones for equation reading
print()
print("=== Key shorthand resolution ===")
for k in ["bx", "bI", "bmu", "bepsilon", "Eb", "kl", "defeq", "ba", "bt", "bSigma"]:
    if k in macros:
        print(f"  \\{k} -> {macros[k]['body']}")
