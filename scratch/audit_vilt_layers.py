import fitz, json
from pathlib import Path

doc = fitz.open("DATASETS/benchmark_pdfs/2102.03334.pdf")
p = doc[3] # Page 4
raw = p.get_text("rawdict")

with open("DATASETS/structural_preservation/2102.03334_hierarchical_proposals_p004.json", encoding="utf-8") as f:
    prop_data = json.load(f)

proposals = prop_data["level4_level5_proposals"]
line_groups = prop_data["level3_line_groups"]

print(f"Total Level 3 line groups on Page 4: {len(line_groups)}")
print(f"Total proposals: {len(proposals)}")

# Focus on y in [495, 605], x > 300
print("\n=== ALL LEVEL 3 LINE GROUPS IN MATH REGION (y in [495, 605], x > 300) ===")
for lg in line_groups:
    bb = lg["merged_bbox"]
    if bb[0] > 300.0 and 495.0 <= bb[1] <= 605.0:
        print(f"LineGroup {lg['line_group_id']:>3}: bbox={[round(v,1) for v in bb]} spans={lg['span_count']} is_eq={lg['is_equation_line_candidate']} eq_num={lg['has_equation_number']}")
        print(f"   text: {repr(lg['text'])}")

print("\n=== ALL LEVEL 4 & 5 PROPOSALS IN MATH REGION ===")
for pr in proposals:
    bb = pr["merged_bbox"]
    if bb[0] > 300.0 and 495.0 <= bb[1] <= 605.0:
        print(f"Proposal {pr['proposal_id']} (L{pr['hierarchy_level']}): bbox={[round(v,1) for v in bb]} spans={pr['span_count']}")
        print(f"   text: {repr(pr['text'])}")

doc.close()

