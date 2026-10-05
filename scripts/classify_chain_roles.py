#!/usr/bin/env python3
"""
classify_chain_roles.py — Build the A-E role lookup table from ALL-FILES.csv.

The operator's taxonomy:
  A = Input            values/variables/ranges/pools fed in
  B = Output           generated artifact
  C = Translator       converts representation for an ability
  D = Description      description of needs (spec/contract)
  E = Deployment       deployment + generated-reusable vs measured-over-time

This script does NOT walk the tree. It joins the existing inventory
(ALL-FILES.csv) so the classification is reproducible and diffable.

Rules are evidence-derived, not invented. Each carries a `rule` string so any
classification can be audited back to why it was made.

Output:
  DATASETS/chain_role_index.csv       — relative_path, role, subrole, rule
  DATASETS/chain_role_summary.json    — counts + role-by-directory matrix
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "ALL-FILES.csv"
OUT_CSV = ROOT / "DATASETS" / "chain_role_index.csv"
OUT_JSON = ROOT / "DATASETS" / "chain_role_summary.json"

NOISE = (
    "node_modules/", ".git/", "__pycache__/", ".venv/",
    ".mypy_cache/", ".pytest_cache/", ".pytest_cache",
    ".wrangler/", ".gemini/", ".hermes/",
)

# ---------------------------------------------------------------------------
# G — GHOST. The onboarding (SECTION 0.3) names these "GHOSTS. They will
# mislead you." They are neither input, output, translator, spec nor deployment.
# Also catches artifacts naming a retired state count (collapse_full_128).
#
# NOTE ON THE LETTER: this role is deliberately NOT called "Q". Q is a reserved
# math symbol here — the response kernel, as in arXiv:2609.36497 ("Evanescent-wave
# Johnson Noise from Superconductors"), where the electromagnetic response is
# described by a single microscopic transverse current-response kernel Q(q,omega),
# with Q = -i*omega*sigma_t and normalisation Q0 = n*e^2/m. That paper's central
# result is a FLOOR: a zero-temperature noise floor induced by magnetic impurities,
# bounded by T1_N(T)/T1(T) <= [nu(0)/nu_F]^2. Q is the kernel; the floor is its
# zero-temperature residue. Do not reuse Q as a taxonomy letter.
# G = ghost.
# ---------------------------------------------------------------------------
G_SUFFIXES = (".deprecated", ".bak", ".orig", ".old", ".rej")
G_NAME_HINTS = ("collapse_full_128",)

# ---------------------------------------------------------------------------
# E subroles: the operator's "generated reusable vs over time measured" split.
#   reusable -> deterministic, regenerable at any time
#   measured -> ACCUMULATED; re-running destroys history
# ---------------------------------------------------------------------------
E_MEASURED_SUFFIXES = (".sqlite", ".sqlite-shm", ".sqlite-wal", ".db", ".jsonl", ".log")
E_MEASURED_HINTS = ("timeseries", "ledger", "capture", "history", "trace", "event", "telemetry", "audit")
E_REUSABLE_HINTS = ("verify", "validate", "check", "test", "deploy", "run_all")

# ---------------------------------------------------------------------------
# D — DESCRIPTION OF NEEDS (spec / contract / declaration)
# ---------------------------------------------------------------------------
D_SUFFIXES = (".md", ".d.ts", ".schema.json", ".jsonc")
D_NAMES = {
    "readme.md", "codebasemap.md", "all-files.md", "all-files.csv",
    "kingwen_agent_onboarding.md", "skill_hexagram_state_machine.md",
    "package.json", "tsconfig.json", "pyproject.toml", "setup.py",
    "requirements.txt", "wrangler.jsonc", "wrangler.toml", "vitest.config.ts",
    "webpack.config.js", "manifest.json",
}
D_DIR_HINTS = ("docs/", "doc/")

# ---------------------------------------------------------------------------
# E — DEPLOYMENT + MEASUREMENT
# ---------------------------------------------------------------------------
E_PREFIXES = ("verify_", "validate_", "audit_", "test_", "check_", "measure_", "score_")
E_SUFFIXES = (".test.ts", ".test.js", ".spec.ts", ".spec.js", ".import")
E_NAMES = {
    "run_all.py", "dockerfile", "docker-compose.yml", "makefile",
    "deploy.sh", "deploy.py", "package-lock.json", ".gitignore",
}
E_DIR_HINTS = ("tests/", "test/", "e2e/", ".github/workflows/")

# ---------------------------------------------------------------------------
# C — TRANSLATORS (read one representation, write another)
# ---------------------------------------------------------------------------
C_PREFIXES = ("generate_", "bridge_", "transform_", "convert_", "enrich_", "update_", "ingest_", "extract_", "build_", "sync_", "expand_")
C_DIR_HINTS = ("scripts/", "src/")

# ---------------------------------------------------------------------------
# A — INPUTS (fed in; no upstream in the chain)
# NOTE: "manifest" is deliberately NOT a hint here. Manifests are *generated*
# (see B_DIR_HINTS / generated-manifest rule) — treating them as inputs would
# mislabel every produced index as a source.
# ---------------------------------------------------------------------------
A_DIR_HINTS = ("data/",)
A_NAME_HINTS = ("registry", "weights", "reflections", "kit_", "archetype",
                "vocabulary", "reference", "pairs", "trigram", "yao_lines",
                "flat", "matrix", "personality_map", "save_strings",
                "transition_graph")
# A manifest is only an input if it is NOT produced by a script in this repo.
GENERATED_MANIFEST_HINTS = ("avatar_mesh_manifest", "depth_anything_v2_manifest",
                            "desktop_3d_engines_manifest", "collisionvis_upgrade_manifest",
                            "desktop_viewers_sync_manifest", "differential_npc_manifest",
                            "jkd_megatron_manifest", "jkd_chapter_chorus_manifest",
                            "godot_mesh_conversion_manifest", "godot_shap_e_conversion_manifest")

# ---------------------------------------------------------------------------
# B — OUTPUTS (generated artifacts)
# ---------------------------------------------------------------------------
B_SUFFIXES = (".ply", ".obj", ".glb", ".gltf", ".usda", ".usdc", ".png",
              ".jpg", ".webp", ".jsonl", ".npz", ".bin", ".mesh", ".wav", ".mp3")
B_DIR_HINTS = ("DATASETS/", "godot/", "dist/", "output/", "generated/", "runtime/")


def _norm(p: str) -> str:
    return p.replace("\\", "/")


CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".sh", ".gd"}
MESH_EXT = {".ply", ".obj", ".glb", ".gltf", ".usda", ".usdc", ".mesh"}
IMAGE_EXT = {".png", ".jpg", ".webp"}
B_SUBROLE_BY_EXT = {
    **{e: "mesh" for e in MESH_EXT},
    **{e: "image" for e in IMAGE_EXT},
    ".tres": "material",
    ".tscn": "scene",
}


def classify(rel: str, ext: str) -> tuple[str, str, str]:
    """Return (role, subrole, rule). First match wins; order encodes precedence."""
    low = _norm(rel).lower()
    base = low.rsplit("/", 1)[-1]

    def has_any(hints) -> bool:
        return any(h in low for h in hints)

    # --- G: ghost (retired / misleading artifacts) ---
    if any(low.endswith(s) for s in G_SUFFIXES):
        return "G", "ghost", f"ext:{ext}"
    if has_any(G_NAME_HINTS):
        return "G", "retired-count", "name:collapse_full_128"

    # --- D: description of needs (early; .md/.d.ts are unambiguous) ---
    if base in D_NAMES:
        return "D", "spec", f"name:{base}"
    if low.endswith(D_SUFFIXES):
        if low.endswith(".jsonc"):
            return "D", "opcode-schema", "ext:.jsonc"
        if low.endswith(".d.ts"):
            return "D", "type-contract", "ext:.d.ts"
        return "D", "doc", f"ext:{ext}"
    if has_any(D_DIR_HINTS):
        return "D", "doc", "dir:docs"

    # --- E: deployment + measurement ---
    if base in E_NAMES:
        return "E", "deploy-config", f"name:{base}"
    # Source-code verifiers stay reusable even when named "audit_*"; only
    # non-code accumulated state counts as `measured`.
    measured = low.endswith(E_MEASURED_SUFFIXES) or has_any(E_MEASURED_HINTS)
    if measured and ext not in CODE_EXT:
        return "E", "measured", f"measured:{base}"
    if low.endswith(E_SUFFIXES) or base.startswith(E_PREFIXES):
        return "E", "reusable", f"name:{base.split('_')[0]}_"
    if has_any(E_DIR_HINTS):
        return "E", "reusable", "dir:tests"

    # --- C: translators ---
    if base.startswith(C_PREFIXES):
        return "C", "translator", f"prefix:{base.split('_')[0]}_"

    # --- A/B: manifests are generated, never sources ---
    if has_any(GENERATED_MANIFEST_HINTS) or base.endswith("manifest.json"):
        return "B", "manifest", "generated-manifest"

    # --- A: inputs ---
    if has_any(A_DIR_HINTS):
        return "A", "data", "dir:data"
    if ext in (".json", ".csv") and any(h in base for h in A_NAME_HINTS):
        return "A", "dataset", f"name-hint:{base}"

    # --- B: outputs ---
    if ext in B_SUBROLE_BY_EXT:
        return "B", B_SUBROLE_BY_EXT[ext], f"ext:{ext}"
    if ext in B_SUFFIXES or has_any(B_DIR_HINTS):
        return "B", "artifact", f"ext:{ext}" if ext in B_SUFFIXES else "dir:generated"

    # --- fallbacks ---
    if ext in CODE_EXT | {".vhd", ".vhdl", ".rs", ".lua", ".c", ".h"}:
        return "C", "code", f"ext:{ext}"
    if ext in (".html", ".htm"):
        return "B", "interface", f"ext:{ext}"
    if ext == ".json":
        # Unclaimed JSON is a data payload, not code and not a spec.
        return "B", "data", "ext:.json"
    if ext in (".txt", ".map", ".log"):
        return "D", "note", f"ext:{ext}"
    if ext == ".csv":
        return "A", "dataset", "ext:.csv"
    if ext == ".zip":
        return "B", "archive", "ext:.zip"
    if ext in (".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"):
        return "D", "config", f"ext:{ext}"
    if ext == ".cf":
        return "B", "toolchain", "ext:.cf"
    if ext in (".lock", ".tmp"):
        return "G", "transient", f"ext:{ext}"
    if not ext:
        return "D", "extensionless", "no-ext"
    return "?", "unclassified", "no-rule"


def main() -> int:
    if not INVENTORY.exists():
        print(f"ERROR: inventory not found: {INVENTORY}")
        return 2

    with INVENTORY.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    records = []
    skipped_noise = 0
    for r in rows:
        if r.get("type") == "directory":
            continue
        rel = _norm(r["relative_path"])
        if any(n in rel for n in NOISE):
            skipped_noise += 1
            continue
        role, subrole, rule = classify(rel, (r.get("extension") or "").lower())
        records.append({
            "relative_path": rel,
            "role": role,
            "subrole": subrole,
            "rule": rule,
            "extension": r.get("extension") or "",
            "size_bytes": r.get("size_bytes") or "",
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["relative_path", "role", "subrole", "rule", "extension", "size_bytes"])
        w.writeheader()
        w.writerows(records)

    role_counts = Counter(r["role"] for r in records)
    sub_counts = Counter(f"{r['role']}:{r['subrole']}" for r in records)
    rule_counts = Counter(r["rule"] for r in records)

    # role by top-level directory
    by_dir: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        top = r["relative_path"].split("/")[0]
        by_dir[top][r["role"]] += 1

    summary = {
        "inventory_source": str(INVENTORY.name),
        "inventory_rows": len(rows),
        "classified": len(records),
        "skipped_noise": skipped_noise,
        "role_counts": dict(role_counts),
        "subrole_counts": dict(sub_counts.most_common(30)),
        "rule_counts": dict(rule_counts.most_common(25)),
        "role_by_top_dir": {k: dict(v) for k, v in sorted(by_dir.items(), key=lambda kv: -sum(kv[1].values()))[:30]},
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=" * 74)
    print("CHAIN ROLE CLASSIFICATION (from ALL-FILES.csv)")
    print("=" * 74)
    print(f"inventory rows : {len(rows)}")
    print(f"classified     : {len(records)}")
    print(f"skipped noise  : {skipped_noise}")
    print()
    labels = {"A": "INPUT", "B": "OUTPUT", "C": "TRANSLATOR", "D": "DESCRIPTION", "E": "DEPLOY+MEASURE", "G": "GHOST", "?": "UNCLASSIFIED"}
    order = tuple(labels)

    def report(counts: Counter, total: int, heading: str) -> None:
        print(heading)
        for role in order:
            n = counts.get(role, 0)
            print(f"  {role} {labels[role]:<15} {n:>8}  {n / total * 100:5.1f}%")
        print()

    report(role_counts, len(records), "")
    # The .tres material wall dominates totals; report the ratio without it.
    no_mat = [r for r in records if r["extension"] != ".tres"]
    n_mat = len(records) - len(no_mat)
    report(Counter(r["role"] for r in no_mat), len(no_mat),
           f"EXCLUDING {n_mat} .tres materials ({len(no_mat)} files):")
    print("E breakdown (reusable vs measured):")
    for k, v in sorted(((k, v) for k, v in sub_counts.items() if k.startswith("E:")), key=lambda kv: -kv[1]):
        print(f"    {k}: {v}")
    print("top unclassified rules:")
    for k, v in rule_counts.most_common(25):
        if k == "no-rule":
            print(f"    {k}: {v}")
    print()
    print(f"index   -> {OUT_CSV}")
    print(f"summary -> {OUT_JSON}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
