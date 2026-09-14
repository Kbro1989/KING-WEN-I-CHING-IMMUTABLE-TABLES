#!/usr/bin/env python3
"""Examine King Wen DATASETS folders for patterns.

Here I am, a simple Python script, examining the DATASETS folder in the King Wen
repository. My job: find patterns in how hexagrams are represented across different
output formats - empty folders, hex 1 patterns, pellet data, model generation.

The user wants to know:
- What's empty?
- What numbers repeat across all outputs?
- Does hex 1 have pellets while others don't?
- What's NOT being generated?
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from collections import Counter, defaultdict


ROOT = Path(__file__).resolve().parent
DATASETS = ROOT / "DATASETS"


def extract_hex_id_from_filename(filename: str) -> int | None:
    """Extract hex number (1-64) from filename patterns."""
    fname_lower = filename.lower()
    
    # Patterns to detect hex numbers in filenames
    patterns = [
        (r"hex[_\-]?0*(\d{1,2})", "hex_NN"),           # hex_01, hex-1, hex01
        (r"scene[_\-]?0*(\d{3})", "scene_NNN"),          # scene_001
        (r"npc_hex[_\-]?0*(\d{1,2})", "npc_hex_NN"),    # npc_hex_01
        (r"kit[_\-]?0*(\d{1,2})", "kit_NN"),            # kit_01, kit-1
        (r"quantum.*hex[_\-]?0*(\d{1,2})", "quantum_hex_NN"),  # quantum_2d_hex_01
        (r"^0*(\d{1,2})\.(?:ply|tscn|usda|png|json|jsonl)", "NN.ext"),  # 01.ply
    ]
    
    for pattern, _ in patterns:
        m = re.search(pattern, fname_lower)
        if m:
            num_str = m.group(1)
            try:
                num = int(num_str)
                if 1 <= num <= 64:
                    return num
            except ValueError:
                continue
    return None


def load_json_content(path: Path):
    """Load JSON/JSONL content safely, return dict/list or None."""
    try:
        if path.suffix == ".jsonl":
            with open(path, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
        else:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        return {"_load_error": str(e)}


def examine_folder(folder_path: Path) -> dict:
    """Examine a single folder and return analysis."""
    result = {
        "name": folder_path.name,
        "exists": folder_path.exists(),
        "is_dir": folder_path.is_dir() if folder_path.exists() else False,
        "file_count": 0,
        "empty_files": [],
        "hex_files": defaultdict(list),  # hex_num -> list of filenames
        "non_hex_files": [],
        "model_files": [],       # hex -> list of model files
        "scene_files": [],       # hex -> list of scene files
        "data_files": [],        # hex -> list of data files (json/jsonl)
        "pkg_files": [],         # package/archive files
        "image_files": [],       # hex -> list of image files
    }
    
    if not folder_path.exists():
        result["error"] = "Does not exist"
        return result
    
    if not folder_path.is_dir():
        result["error"] = "Not a directory"
        return result
    
    files = sorted(f for f in folder_path.iterdir() if f.is_file())
    result["file_count"] = len(files)
    result["all_filenames"] = [f.name for f in files]
    
    for f in files:
        if f.stat().st_size == 0:
            result["empty_files"].append(f.name)
            continue
        
        hex_id = extract_hex_id_from_filename(f.name)
        
        if hex_id is not None:
            result["hex_files"][hex_id].append(f.name)
            
            # Categorize by type
            ext = f.suffix.lower()
            if ext in (".ply", ".tscn", ".usda", ".fbx", ".glb", ".gltf", ".obj"):
                result["model_files"].setdefault(hex_id, []).append(f.name)
            elif ext in (".json", ".jsonl"):
                result["data_files"].setdefault(hex_id, []).append(f.name)
                # Try to load for pellet analysis
                content = load_json_content(f)
                if content and check_for_pellet_data(content):
                    result.setdefault("hex_with_pellet_data", set()).add(hex_id)
            elif ext == ".png":
                result["image_files"].setdefault(hex_id, []).append(f.name)
        else:
            result["non_hex_files"].append(f.name)
    
    return result


def check_for_pellet_data(content) -> bool:
    """Check if content contains pellet/wavepacket data."""
    if content is None:
        return False
    
    if isinstance(content, dict):
        for key in content.keys():
            key_lower = key.lower()
            if any(term in key_lower for term in [
                "pellet", "wavepacket", "wave_packet", "ternary_pellet",
                "acoustic_pellet", "sound_pellet", "audio_pellet", "pellet_dispersion"
            ]):
                return True
        # Recursively check nested dicts and lists
        for value in content.values():
            if isinstance(value, (dict, list)):
                if check_for_pellet_data(value):
                    return True
    elif isinstance(content, list):
        for item in content:
            if check_for_pellet_data(item):
                return True
    return False


def has_pellet_key(data, path="") -> list[str]:
    """Find all keys containing 'pellet' in nested data."""
    found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if "pellet" in key.lower():
                found.append(f"{path}.{key}" if path else key)
            if isinstance(value, (dict, list)):
                found.extend(has_pellet_key(value, f"{path}.{key}" if path else key))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            found.extend(has_pellet_key(item, f"{path}[{i}]"))
    return found


def analyze_all_folders():
    """Examine all DATASETS subfolders and analyze patterns."""
    
    # Get all subfolders
    all_subfolders = sorted([
        d for d in DATASETS.iterdir() 
        if d.is_dir() and not d.name.startswith("_")
    ])
    
    # Also include those from the user's list if they exist
    for folder_name in FOLDERS:
        folder_path = DATASETS / folder_name
        if folder_path.exists() and folder_path.is_dir():
            if folder_name not in [d.name for d in all_subfolders]:
                all_subfolders.append(folder_path)
    
    # Examine each folder
    folder_results = {}
    for folder_path in all_subfolders:
        folder_results[folder_path.name] = examine_folder(folder_path)
    
    # Analysis
    analysis = {
        "total_folders": len(folder_results),
        "empty_folders": [],
        "folders_with_files": [],
        "folders_with_hex_files": [],
        "hex_coverage": defaultdict(set),      # hex -> set of folders
        "hex_model_coverage": defaultdict(set),  # hex -> set of model folders
        "hex_scene_coverage": defaultdict(set),   # hex -> set of scene folders
        "hex_pellet_coverage": defaultdict(set),  # hex -> set of data folders with pellet data
        "hex_file_counts": Counter(),             # hex -> total file count across folders
        "hex_model_counts": Counter(),           # hex -> model file count
        "hex_data_counts": Counter(),            # hex -> data file count
        "hex_image_counts": Counter(),           # hex -> image file count
        "hex_1_present_folders": set(),
        "hex_1_has_pellet_data": False,
        "hex_1_pellet_sources": [],
        "hexes_without_models": set(),
        "hexes_without_data": set(),
        "hexes_without_scenes": set(),
        "all_hexes_have_models": True,
        "all_hexes_have_data": True,
        "all_hexes_have_scenes": True,
        "hexes_with_pellet_data": set(),
        "hex_1_pellet_is_unique": False,
    }
    
    # Collect all hex IDs
    all_hex_ids = set(range(1, 65))
    
    for folder_name, result in folder_results.items():
        if not result["exists"]:
            continue
        if not result["is_dir"]:
            continue
        
        if result["file_count"] == 0:
            analysis["empty_folders"].append(folder_name)
            continue
        
        analysis["folders_with_files"].append(folder_name)
        
        for hex_id, files in result["hex_files"].items():
            hex_str = str(hex_id).zfill(2)
            analysis["hex_coverage"][hex_str].add(folder_name)
            analysis["hex_file_counts"][hex_str] += len(files)
            
            # Check for models
            model_files = [f for f in files if Path(f).suffix.lower() in (".ply", ".tscn", ".usda", ".fbx", ".glb", ".gltf", ".obj")]
            if model_files:
                analysis["hex_model_coverage"][hex_str].add(folder_name)
            
            # Check for data files (json/jsonl)
            data_files = [f for f in files if Path(f).suffix.lower() in (".json", ".jsonl")]
            if data_files:
                analysis["hex_data_coverage"][hex_str].add(folder_name)
                
                # Check for pellet data in hex 1
                if hex_str == "01":
                    for fname in data_files:
                        full_path = folder_path / fname
                        content = load_json_content(full_path)
                        if content and check_for_pellet_data(content):
                                    analysis["hex_1_has_pellet_data"] = True
                                    analysis["hex_1_pellet_sources"].append({
                                        "folder": folder_name,
                                        "file": fname,
                                        "keys": has_pellet_key(content)
                            })
    
    # Determine which hexes have models across all relevant folders
    for hex_id in all_hex_ids:
        hex_str = str(hex_id).zfill(2)
        if hex_str in analysis["hex_model_coverage"]:
            analysis["hexes_without_models"].discard(hex_str)
        else:
            analysis["hexes_without_models"].add(hex_str)
    
    # Determine which hexes have data files
    for hex_id in all_hex_ids:
        hex_str = str(hex_id).zfill(2)
        if hex_str not in analysis["hex_data_coverage"]:
            analysis["hexes_without_data"].add(hex_str)
    
    # Check if hex 1 is the only one with pellet data
    all_hexes_with_pellet_data = set(analysis["hex_pellet_coverage"].keys())
    if "01" in all_hexes_with_pellet_data and len(all_hexes_with_pellet_data) == 1:
        analysis["hex_1_is_only_with_pellets"] = True
    
    # Count hexes that have data in all folders that have hex files
    folders_with_hex_data = [f for f in analysis["folders_with_files"] 
                            if any(f in folder_results[f].get("files_by_hex", {}) for f in ["01"])]
    
    return {
        "folder_results": folder_results,
        "analysis": analysis,
    }


def generate_report(results: dict, analysis: dict) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 80)
    lines.append("KINGWEN DATASETS EXAMINATION REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Folder summary
    lines.append("## FOLDER SUMMARY")
    lines.append("-" * 60)
    for folder_name in sorted(results.keys()):
        result = results[folder_name]
        if not result["exists"]:
            lines.append(f"  {folder_name}/: [MISSING]")
            continue
        if not result["is_dir"]:
            lines.append(f"  {folder_name}: [NOT A DIRECTORY]")
            continue
        if result["file_count"] == 0:
            lines.append(f"  {folder_name}/: [EMPTY FOLDER]")
            continue
        
        lines.append(f"  {folder_name}/: {result['file_count']} files")
        if result.get("empty_files"):
            lines.append(f"    Empty files: {result['empty_files']}")
        
        # Hex breakdown
        hex_files = result.get("hex_files", {})
        if hex_files:
            hex_summary = ", ".join(
                f"{h}:{len(fl)}" for h, fl in sorted(hex_files.items(), key=lambda x: int(x[0]))
            )
            lines.append(f"    Hex breakdown: {hex_summary}")
        
        # Model files
        model_files = result.get("model_files", {})
        if model_files:
            model_summary = ", ".join(
                f"{h}:{len(fl)}" for h, fl in sorted(model_files.items(), key=lambda x: int(x[0]))
            )
            lines.append(f"    Model files: {model_summary}")
        
        # Data files with pellet info
        data_files = result.get("data_files", {})
        if data_files:
            for hex_id, files in sorted(data_files.items(), key=lambda x: int(x[0])):
                for fname in files:
                    full_path = DATASETS / folder_name / fname
                    content = load_json_content(full_path)
                    if content and check_for_pellet_data(content):
                        pellet_keys = has_pellet_key(content)
                        if pellet_keys:
                            lines.append(f"    HEX {hex_id} PELLET DATA in {folder_name}/{fname}:")
                            for key in pellet_keys:
                                val = content
                                for k in key.split("."):
                                    if isinstance(val, dict):
                                        val = val.get(k, "...")
                                    lines.append(f"      {key}: {val}")
        lines.append("")
    
    # Empty folders
    lines.append("EMPTY FOLDERS:")
    lines.append("-" * 60)
    if analysis["empty_folders"]:
        for f in analysis["empty_folders"]:
            lines.append(f"  - {f}/")
    else:
        lines.append("  None")
    lines.append("")
    
    # Hex coverage
    lines.append("HEX COVERAGE:")
    lines.append("-" * 60)
    lines.append(f"  Hexes found in at least one folder: {len(analysis['hex_coverage'])}")
    lines.append(f"  Hexes in ALL folders with hex data: {sorted(analysis['hexes_with_pellet_data'], key=int) if analysis['hexes_with_pellets'] else 'None'}")
    
    hexes_not_found = all_hex - analysis["hex_coverage"]
    if hexes_not_found:
        lines.append(f"  Hexes NOT in any folder: {sorted(hexes_not_found, key=int)}")
    
    # Hex 1 specific
    lines.append("")
    lines.append("HEX 01 (The Creative) ANALYSIS:")
    lines.append("-" * 60)
    hex1_folders = analysis["hex_coverage"].get("01", set())
    lines.append(f"  Found in {len(hex1_folders)} folder(s): {sorted(hex1_folders)}")
    lines.append(f"  Has models: {'YES' if '01' in analysis['hex_model_coverage'] else 'NO'}")
    lines.append(f"  Has data files: {'YES' if '01' in analysis['hex_data_coverage'] else 'NO'}")
    lines.append(f"  Has pellet data: {'YES' if analysis['hex_1_has_pellet_data'] else 'NO'}")
    
    if analysis["hex_1_pellet_sources"]:
        for source in analysis["hex_1_pellet_sources"]:
            lines.append(f"    - {source['folder']}/{source['file']}")
            lines.append(f"      Keys: {source['keys']}")
    
    # Hexes with pellet data
    lines.append("")
    lines.append("ALL HEXES WITH PELLET/WAVEPACKET DATA:")
    lines.append("-" * 60)
    if analysis["hexes_with_pellet_data"]:
        for hex_id in sorted(analysis["hexes_with_pellet_data"], key=int):
            folders = analysis["hex_pellet_coverage"].get(hex_id, set())
        lines.append(f"  Hex {hex_id}: {sorted(folders)}")
    else:
        lines.append("  None found")
    
    # Hexes without models
    lines.append("")
    lines.append("HEXES WITHOUT 3D MODELS:")
    lines.append("-" * 60)
    if analysis["hexes_without_models"]:
        for hex_id in sorted(analysis["hexes_without_models"], key=int):
            print(f"  Hex {hex_id}: NOT in any model folder")
    else:
        lines.append("  All hexes have at least one 3D model file")
    
    # Hex 1 comparison
    lines.append("")
    lines.append("HEX 01 VS OTHERS:")
    lines.append("-" * 60)
    
    hex1_folders = analysis["hex_coverage"].get("01", set())
    hex1_model_folders = analysis["hex_model_coverage"].get("01", set())
    hex1_data_folders = analysis["hex_data_coverage"].get("01", set())
    
    print(f"  Hex 01 folders: {sorted(hex1_folders)}")
    print(f"  Hex 01 model folders: {sorted(hex1_model_folders)}")
    print(f"  Hex 01 data folders: {sorted(hex1_data_folders)}")
    
    # Find hexes that DON'T have hex 1 in some folders
    hexes_missing_in_some_folders = {}
    for folder_name in analysis["folders_with_files"]:
        for hex_id in all_hexes:
            if folder_name not in analysis["hex_coverage"].get(hex_id, set()):
                analysis["hexes_not_in_all_folders"].setdefault(hex_id, set()).add(folder_name)
    
    if analysis["hexes_not_in_all_folders"]:
        for hex_id in sorted(analysis["hexes_not_in_all_folders"].keys(), key=int):
            missing = analysis["hexes_not_in_all_folders"][hex_id]
            lines.append(f"  Hex {hex_id}: missing from {len(missing)} folder(s): {sorted(missing)}")
    
    print()
    print("=" * 80)
    print("PATTERN SUMMARY")
    lines.append("")
    
    # Check if hex 1 is unique in having pellet data
    hexes_with_pellet = analysis.get("hexes_with_pellet_data", [])
    if hexes_with_pellet:
        if len(hexes_with_pellet) == 1 and "01" in hexes_with_pellet:
            lines.append("* HEX 01 IS THE ONLY HEX WITH PELLET DATA - all other hexes have NO pellet data!")
        else:
            lines.append(f"* Hexes with pellet data: {sorted(hexes_with_pellet, key=int)}")
    
    # Check if hex 1 is overrepresented
    hex1_count = analysis["hex_file_counts"].get("01", 0)
    avg_count = sum(analysis["hex_file_counts"].values()) / len(analysis["hex_file_counts"]) if analysis["hex_file_counts"] else 0
    if hex1_count > avg_count * 1.5:
        lines.append(f"* Hex 01 has {hex1_count} files ({hex1_count/avg_count:.1f}x average)")
    
    # Check for repeated numbers
    hex_counts = Counter()
    for result in results.values():
        if result.get("hex_files"):
            for hex_id, files in result["hex_files"].items():
                hex_counts[hex_id] += len(files)
    if hex_counts:
        most_common = hex_counts.most_common(5)
        lines.append(f"  Most files per hex: {most_common}")
    
    print("\n".join(lines))


def main():
    print("Examining DATASETS folders...")
    
    # Get all subfolders
    all_subfolders = sorted([
        d for d in DATASETS.iterdir() 
        if d.is_dir() and not d.name.startswith("_")
    ])
    
    # Add specific folders from user's list
    for folder_name in FOLDERS:
        folder_path = DATASETS / folder_name
        if folder_path.exists() and folder_path.is_dir():
            if folder_path not in all_subfolders:
                all_subfolders.append(folder_path)
    
    # Examine each folder
    results = {}
    for folder_path in all_subfolders:
        result = examine_folder(folder_path)
        results[folder_path.name] = result
        
        # Print brief status
        if not result["exists"]:
            print(f"  {folder_path.name}: MISSING")
        elif not result["is_dir"]:
            print(f"  {folder_path.name}: not a directory")
        elif result["file_count"] == 0:
            print(f"  {folder_path.name}: EMPTY")
        else:
            hex_ids = sorted(result.get("files_by_hex", {}).keys(), key=int)
            print(f"  {folder_path.name}: {result['file_count']} files")
            if hex_ids:
                print(f"    Hexes: {hex_ids}")
            if result.get("empty_files"):
                print(f"    Empty files: {result['empty_files']}")
    
    print(f"\nExamined {len(results)} folders")
    
    # Analyze patterns
    print("\nAnalyzing patterns...")
    analysis = analyze_patterns(results)
    
    # Print report
    report = generate_report(results, analysis)
    print(report)
    
    # Write JSON summary
    summary = {
        "analysis": analysis,
        "folder_results": {
            name: {
                "exists": r["exists"],
                "file_count": r["file_count"],
                "empty_files": r.get("empty_files", []),
                "hex_breakdown": {h: [f["name"] for f in fl] for h, fl in r.get("files_by_hex", {}).items()},
                "hex_model_files": {h: [f["name"] for f in fl] for h, fl in r.get("model_files", {}).items()},
                "hex_data_files": {h: [f["name"] for f in fl] for h, fl in r.get("data_files", {}).items()},
            }
            for name, r in results.items()
        }
    }
    
    summary_path = ROOT / "datasets_examination_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nJSON summary written to: {summary_path}")


if __name__ == "__main__":
    main()
