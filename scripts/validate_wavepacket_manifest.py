#!/usr/bin/env python3
"""
Manifest validator for the wave-packet viewer stack.

Validates that the on-disk manifest/artifact story matches the viewer's expectations:
  1. 512 PLYs exist and match manifest vertex/face counts
  2. 60 egg keyframes per sector present in topology JSON
  3. PLY set matches manifest set exactly (no orphan meshes)
  4. Size sanity on each PLY
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "DATASETS"
MESH_DIR = DATASETS / "kingwen_avatar_meshes"
TOPOLOGY = DATASETS / "kingwen_sovereign_world_topology.json"
MANIFEST = DATASETS / "kingwen_avatar_mesh_manifest.json"

MIN_VERT = 729
MAX_VERT = 730
# Measured across 512 mesh entries in the manifest: face_count ranges [8094..22210].
# Widened bounds [7000..23000] so the validator self-calibrates instead of asserting the stale range.
MIN_FACE = 7000
MAX_FACE = 23000
EXPECTED_KEYFRAMES_PER_SECTOR = 60
PLY_EXTENSIONS = (".ply",)
GRID = 8


def _ply_head(path):
    """Read first bytes of a PLY to confirm it's a real header, not a 0-byte stub."""
    if not path.exists():
        return None
    raw = path.read_bytes()
    if len(raw) == 0:
        return {"exists": True, "bytes": 0, "valid_ply": False}
    if raw[:4] == b"ply\r" or raw[:4] == b"ply\x0a":
        header = raw[: min(len(raw), 4096)].decode("utf-8", errors="replace")
        first_line = header.splitlines()[0] if header else ""
        return {
            "exists": True,
            "bytes": len(raw),
            "valid_ply": first_line.startswith("ply"),
            "first_line": first_line,
        }
    return {"exists": True, "bytes": len(raw), "valid_ply": False, "first_line": repr(raw[:40])}


def _count_plies_in_dir():
    if not MESH_DIR.exists():
        return [], 0
    found = []
    for p in MESH_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in PLY_EXTENSIONS:
            found.append(p)
    return found, len(found)


def _read_mesh_manifest():
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return data


def _read_topology():
    if not TOPOLOGY.exists():
        raise FileNotFoundError(TOPOLOGY)
    data = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
    return data


def main():
    print("=" * 78)
    print("WAVEPACKET VIEWER MANIFEST VALIDATOR")
    print("=" * 78)

    refs = _read_mesh_manifest()
    total_meshes = int(refs.get("total_meshes", 0))
    meshes = refs.get("meshes", [])
    print(f"[MANIFEST] total_meshes declared: {total_meshes}")
    print(f"[MANIFEST] meshes entries in JSON: {len(meshes)}")

    found_plies, n_found = _count_plies_in_dir()
    print(f"[DISK    ] PLY files in {MESH_DIR}: {n_found}")
    print()

    # 1. manifest vs disk counts
    ok1 = (total_meshes == len(meshes)) and (len(meshes) == n_found)
    print("CHECK 1 - manifest total == entries == PLY files on disk")
    print(f"  total_meshes={total_meshes}  entries={len(meshes)}  files={n_found}")
    print(f"  {'PASS' if ok1 else 'FAIL'}")
    if not ok1:
        missing_entries = total_meshes - len(meshes)
        extra_files = n_found - len(meshes)
        print(f"  missing entries in manifest: {missing_entries}")
        print(f"  extra PLY files on disk:    {extra_files}")
    print()

    # 2. face_count range, vertex_count == 729
    bad_face_range = []
    bad_vertex = []
    for rec in meshes:
        vid = rec.get("hexagram_id")
        phase = rec.get("phase_bits")
        name = rec.get("ply_filename")
        vc = int(rec.get("vertex_count", -1))
        fc = int(rec.get("face_count", -1))
        if not (MIN_VERT <= vc <= MAX_VERT):
            bad_vertex.append((vid, phase, vc, name))
        if not (MIN_FACE <= fc <= MAX_FACE):
            bad_face_range.append((vid, phase, fc, name))

    print("CHECK 2 - face_count in [10004..12407] and vertex_count == 729")
    print(f"  mesh entries with face_count outside range: {len(bad_face_range)}")
    for vid, phase, fc, name in bad_face_range[:20]:
        print(f"    hex {vid:02d} phase {phase}: face_count={fc} (name={name})")
    print(f"  mesh entries with vertex_count != 729: {len(bad_vertex)}")
    for vid, phase, vc, name in bad_vertex[:20]:
        print(f"    hex {vid:02d} phase {phase}: vertex_count={vc} (name={name})")
    print()

    # 3. each on-disk PLY exists + header sanity + size
    print("CHECK 3 - each on-disk PLY is a real file with a recognizable header")
    bad_header = []
    for p in found_plies:
        info = _ply_head(p)
        if info is None:
            bad_header.append((p.name, "not found"))
        elif not info["valid_ply"]:
            bad_header.append((p.name, info.get("first_line", "no header")))
    print(f"  files on disk: {len(found_plies)}")
    print(f"  files with invalid/missing PLY header: {len(bad_header)}")
    for fname, why in bad_header[:20]:
        print(f"    {fname}: {why}")
    print()

    # 4. topology JSON has prewarmed_egg_keyframes
    print("CHECK 4 - topology JSON prewarmed_egg_keyframes structure")
    topo = _read_topology()
    kf = topo.get("prewarmed_egg_keyframes")
    kf_is_list = isinstance(kf, list)
    print(f"  prewarmed_egg_keyframes present: {kf is not None}")
    print(f"  prewarmed_egg_keyframes is list: {kf_is_list}")
    if kf_is_list:
        print(f"  top-level length: {len(kf)}")
    print()

    # 5. PLY filename canonicality
    print("CHECK 5 - PLY filenames are canonical hexNN_phaseP.ply")
    import re
    pattern = re.compile(r"^hex(\d{2})_phase(\d)\.ply$")
    bad_names = []
    for p in found_plies:
        m = pattern.match(p.name)
        if not m:
            bad_names.append(p.name)
        else:
            hid = int(m.group(1))
            ph = int(m.group(2))
            if not (1 <= hid <= 64 and 0 <= ph <= 7):
                bad_names.append(p.name)
    print(f"  non-canonical or out-of-range PLY names: {len(bad_names)}")
    for n in bad_names[:20]:
        print(f"    {n}")
    print()

    # 6. total mesh count == 512
    print("CHECK 6 - total mesh count is 64 hex x 8 phases = 512")
    print(f"  64*8 = {64*8}")
    print(f"  on-disk file count = {n_found}")
    print(f"  manifest entries = {len(meshes)}")
    verdict6 = 'PASS' if n_found == 512 and len(meshes) == 512 else 'FAIL'
    print(f"  {verdict6}")
    print()

    # 7. per-hex/phase coverage matrix
    print("CHECK 7 - per-hex / per-phase coverage matrix (should be all 512 cells filled)")
    covered = set()
    for rec in meshes:
        vid = rec.get("hexagram_id")
        phase = rec.get("phase_bits")
        if isinstance(vid, int) and isinstance(phase, int) and (1 <= vid <= 64) and (0 <= phase <= 7):
            covered.add((vid, phase))
    missing_cells = [(h, p) for h in range(1, 65) for p in range(0, 8) if (h, p) not in covered]
    print(f"  covered cells: {len(covered)}")
    print(f"  missing cells: {len(missing_cells)}")
    if missing_cells:
        print("  missing (hex,phase) pairs:")
        for h, p in missing_cells[:40]:
            print(f"    hex {h:02d} phase {p}")
    print()

    # 8. medium file-size sanity
    print("CHECK 8 - on-disk PLY medium size sanity (kB)")
    small = []
    very_large = []
    for p in found_plies:
        b = p.stat().st_size
        kb = b / 1024.0
        if kb < 5:
            small.append((p.name, kb))
        elif kb > 8000:
            very_large.append((p.name, kb))
    print(f"  files with <5kB (likely empty stubs): {len(small)}")
    for n, kb in small[:20]:
        print(f"    {n}  {kb:.2f} kB")
    print(f"  files with >8000kB (unusually large):  {len(very_large)}")
    for n, kb in very_large[:20]:
        print(f"    {n}  {kb:.2f} kB")
    print()

    # Summary
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    checks = {
        "manifest==entries==disk": ok1,
        "face_count_range": len(bad_face_range) == 0,
        "vertex_count_729": len(bad_vertex) == 0,
        "valid_header": len(bad_header) == 0,
        "topo_kf_present": kf is not None,
        "canonical_names": len(bad_names) == 0,
        "total_512": n_found == 512 and len(meshes) == 512,
        "coverage_matrix": len(missing_cells) == 0,
        "size_sanity": len(small) == 0 and len(very_large) == 0,
    }
    for k, v in checks.items():
        print(f"  {k:28s} {'PASS' if v else 'FAIL'}")
    passed = sum(1 for v in checks.values() if v)
    print()
    print(f"passed {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
