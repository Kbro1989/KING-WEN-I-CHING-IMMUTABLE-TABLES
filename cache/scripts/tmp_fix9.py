#!/usr/bin/env python3
"""Fix carry-forward logic in adjudicate_targets.py."""
path = 'scripts/adjudicate_targets.py'
with open(path, 'rb') as f:
    raw = f.read()

old = b'''    # Carry forward the earlier adjudication layer's explicit statuses.
    existing_map = {}
    adj_path = os.path.join(RENDER_DIR, "adjudication_report.jsonl")
    if os.path.exists(adj_path):
        with open(adj_path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("match_status") and r["match_status"] != STATUS_UNVERIFIED:
                    existing_map[r["pix2text_element_id"]] = r["match_status"]
    print(f"Carry-forward map: {len(existing_map)} records with explicit status")'''

new = b'''    # Carry forward the earlier adjudication layer's explicit statuses.
    # Only carry forward VISUALLY_VERIFIED, SPATIAL_MATCH, TEXT_MATCH — not UNADJUDICATED.
    existing_map = {}
    adj_path = os.path.join(RENDER_DIR, "adjudication_report.jsonl")
    if os.path.exists(adj_path):
        with open(adj_path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                st = r.get("match_status")
                if st in (b"VISUALLY_VERIFIED", b"SPATIAL_MATCH", b"TEXT_MATCH"):
                    existing_map[r["pix2text_element_id"]] = st
    print(f"Carry-forward map: {len(existing_map)} records with explicit status")'''

if old in raw:
    raw = raw.replace(old, new)
    with open(path, 'wb') as f:
        f.write(raw)
    print('Fixed carry-forward logic')
else:
    print('old block not found')
