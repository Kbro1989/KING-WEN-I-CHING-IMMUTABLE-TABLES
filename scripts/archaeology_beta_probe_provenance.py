#!/usr/bin/env python3
"""
PASS 1/2 — Beta probe provenance: first git appearance per file in POG2.

Establishes the chronology half of the provenance graph. The rsmv copy lives
under a gitignored path (.gitignore:233 scripts/.pog2/), so it is untracked and
cannot be dated there. POG2's git history is the datable side.
"""
import subprocess
from pathlib import Path

POG2 = Path(r"C:\Users\krist\.gemini\antigravity\scratch\POG2")

FILES = [
    "scratch/search_import_save.ts",
    "scratch/search_import_save_binary.ts",
    "scratch/search_import_save_utf16.ts",
    "scratch/search_beta_binary.ts",
    "scratch/search_beta_scripts.ts",
    "scratch/search_beta_strings.ts",
    "scratch/pull_beta_enums.ts",
    "scratch/scan_beta_majors.ts",
    "scratch/extract_beta_enums.ts",
    "scratch/extract_beta_enums_raw.ts",
    "scratch/analyze_beta_enums.ts",
]


def git(*args):
    r = subprocess.run(
        ["git", "-C", str(POG2)] + list(args),
        capture_output=True, text=True, errors="replace",
    )
    return r.stdout.strip()


print("=== POG2 git identity ===")
print("HEAD:", git("log", "-1", "--format=%H %ci %s"))
print("branches:", git("branch", "-a").replace("\n", " ")[:200])
print()

print("=== FIRST APPEARANCE (git --diff-filter=A) ===")
rows = []
for f in FILES:
    out = git("log", "--diff-filter=A", "--follow",
              "--format=%H|%ci|%s", "--", f)
    if not out:
        rows.append((f, "NOT TRACKED", "", ""))
        continue
    # oldest is last line
    lines = [l for l in out.splitlines() if "|" in l]
    if not lines:
        rows.append((f, "NO COMMIT", "", ""))
        continue
    sha, date, subj = lines[-1].split("|", 2)
    rows.append((f, date, sha[:10], subj[:60]))

rows.sort(key=lambda r: (r[1] == "NOT TRACKED", r[1]))
for f, date, sha, subj in rows:
    name = f.replace("scratch/", "")
    print(f"  {date[:19]:19s}  {sha:11s}  {name}")
    if subj:
        print(f"       {subj}")

print()
print("=== ALL COMMITS TOUCHING ANY BETA PROBE (chronological) ===")
out = git("log", "--reverse", "--format=%H|%ci|%s", "--", "scratch/search_import_save.ts",
          "scratch/search_beta_binary.ts", "scratch/pull_beta_enums.ts",
          "scratch/scan_beta_majors.ts", "scratch/analyze_beta_enums.ts",
          "scratch/extract_beta_enums.ts", "scratch/search_beta_scripts.ts",
          "scratch/search_beta_strings.ts", "scratch/search_import_save_utf16.ts",
          "scratch/search_import_save_binary.ts")
seen = set()
for line in out.splitlines():
    if "|" not in line:
        continue
    sha, date, subj = line.split("|", 2)
    if sha in seen:
        continue
    seen.add(sha)
    print(f"  {date[:19]:19s}  {sha[:10]}  {subj[:70]}")

print()
print("=== does rsmv-upstream track scripts/.pog2/ ? ===")
rs = Path(r"C:\Users\krist\Desktop\rsmv-upstream")
r = subprocess.run(["git", "-C", str(rs), "check-ignore", "-v",
                    "scripts/.pog2/sovereign/sovereign/search_import_save.ts"],
                   capture_output=True, text=True, errors="replace")
print("  check-ignore:", r.stdout.strip() or "(not ignored)")
r2 = subprocess.run(["git", "-C", str(rs), "ls-files", "scripts/.pog2/"],
                    capture_output=True, text=True, errors="replace")
print(f"  tracked files under scripts/.pog2/: {len([l for l in r2.stdout.splitlines() if l])}")
