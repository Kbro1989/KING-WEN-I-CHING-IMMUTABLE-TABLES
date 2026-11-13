import json

with open("DATASETS/structural_preservation/2102.03334_hierarchical_proposals_p004.json", encoding="utf-8") as f:
    d = json.load(f)

lgs = {lg["line_group_id"]: lg for lg in d["level3_line_groups"]}

for lg_id in [67, 68, 71, 72, 75, 76, 77, 80, 82, 83, 84, 85, 87, 89, 90, 91, 92, 93, 95, 96]:
    lg = lgs[lg_id]
    print(f"LG {lg_id:>2}: bbox={lg['merged_bbox']} spans={lg['span_count']} text={repr(lg['text'])}")

