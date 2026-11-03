import json

skills = [
    "autonomous-ai-agents/rs3-cache-decoder/SKILL.md",
    "autonomous-ai-agents/rsmv-upstream-viewer-extension/SKILL.md",
    "research/vision-math-symbol-detection/SKILL.md",
    "rsmv-pog2-tools/SKILL.md",
    "software-development/fork-recovery/SKILL.md",
]

orig_report = json.load(open("journey_web_alignment_report_2026-07-11.json"))
active_report = json.load(open("journey_web_alignment_report_active_2026-11-03.json"))

for skill_rel in skills:
    # Find full paths
    orig_srcs = [m for m in orig_report["missing_edge_targets"] if skill_rel in m["src"]]
    active_srcs = [m for m in active_report["missing_edge_targets"] if skill_rel in m["src"]]
    print(f"{skill_rel}:")
    print(f"  original missing: {len(orig_srcs)} -> {[m['target'] for m in orig_srcs]}")
    print(f"  active missing: {len(active_srcs)} -> {[m['target'] for m in active_srcs]}")
    # Check if they were orphans (no edges at all)
    orig_orphans = orig_report["orphan_candidates"]
    active_orphans = active_report["orphan_candidates"]
    was_orphan = any(skill_rel in p for p in orig_orphans)
    is_orphan = any(skill_rel in p for p in active_orphans)
    print(f"  was orphan: {was_orphan}, is orphan: {is_orphan}")
    print()
"